#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 121 · SELLADO EN CASCADA de las capas QA a 3.6.110-SDK6.

Barrido genérico e idempotente r121 (patrón sella_r99): en TODA capa qa_*.py
que aún lleve el sello de la ronda anterior se sustituyen los dos tokens de
versión (3.6.109-SDK6 → 3.6.110-SDK6 y v36109-sdk6 → v36110-sdk6). Si una capa
ya lleva el sello nuevo (o nunca lo llevó), no se toca. El SDK NO cambia esta
ronda (1.6.0); el cambio r121 vive en el NÚCLEO de red (c09 pose fresca para
juzgar + cadencia sin toss; c09b VP.POSE_FRESH_MS) y en el banco/batería
multijugador (S3 saque del invitado + puntos 3-4 con rotación ITTF).

Los tamaños byte-exactos de los ZIPs v36110 se rellenan tras gen_release_v36110
(como manda el ritual): hasta entonces las capas de descargas siguen con los
tamaños r120 — qa_descargas se re-ancla en ese momento."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.109-SDK6', '3.6.110-SDK6'), ('v36109-sdk6', 'v36110-sdk6')]

def sella_fichero(p: Path):
    try:
        t = p.read_text(encoding='utf-8')
    except Exception:
        return None
    orig = t
    cambios = 0
    for viejo, nuevo in VERSIONES:
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            cambios += n
    if cambios:
        p.write_text(t, encoding='utf-8')
        return cambios
    ya = all(t.count(nuevo) > 0 for _, nuevo in VERSIONES)
    return 'ya' if ya else 0

def main():
    capas = sorted(SCR.glob('qa_*.py')) + sorted(SCR.glob('sella_r12*.py'))
    tocados = []
    for p in capas:
        if p.name.startswith('sella_'):
            continue   # los selladores no se sellan a sí mismos
        r = sella_fichero(p)
        if isinstance(r, int) and r > 0:
            tocados.append((p.name, r))
    print('== SELLADO r121 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.110-SDK6 / v36110-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')
    return 0

if __name__ == '__main__':
    sys.exit(main())
