#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 98 · SELLADO EN CASCADA de las capas QA a 3.6.90-SDK6.

Barrido genérico e idempotente: en TODA capa qa_*.py que aún lleve el sello
de la ronda anterior se sustituyen los dos tokens de versión (3.6.89-SDK6 →
3.6.90-SDK6 y v3689-sdk6 → v3690-sdk6). Si una capa ya lleva el sello nuevo
(o nunca lo llevó), no se toca (lección de la ronda 13: «ya sellado» cuenta
como OK). El SDK NO cambia esta ronda (1.6.0 se estrenó en la r97); el
cambio r98 vive en el NÚCLEO (c12 bocadillo blanco + arrastre de
deslizadores + mesa agarrable + selectend; c00 i18n r98) y en el HUB
(descargas al día con la versión).

Los tamaños byte-exactos de los ZIPs v3690 se rellenan tras gen_release_v3690
(como manda el ritual): hasta entonces las capas de descargas siguen con los
tamaños r97 — qa_descargas se re-ancla en ese momento."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.89-SDK6', '3.6.90-SDK6'), ('v3689-sdk6', 'v3690-sdk6')]

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
    # idempotencia: ¿ya sellado?
    ya = all(t.count(nuevo) > 0 for _, nuevo in VERSIONES if nuevo in orig or True)
    return 'ya' if ya else 0

def main():
    capas = sorted(SCR.glob('qa_*.py')) + sorted(SCR.glob('sella_r9*.py'))
    tocados = []
    for p in capas:
        if p.name in ('sella_r97.py', 'sella_r98.py'):
            continue   # los selladores no se sellan a sí mismos
        r = sella_fichero(p)
        if isinstance(r, int) and r > 0:
            tocados.append((p.name, r))
    print('== SELLADO r98 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.90-SDK6 / v3690-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')

if __name__ == '__main__':
    main()
