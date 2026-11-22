#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 112 · SELLADO EN CASCADA de las capas QA a 3.6.102-SDK6.

Barrido genérico e idempotente r111: en TODA capa qa_*.py que aún lleve el
sello de la ronda anterior se sustituyen los dos tokens de versión
(3.6.102-SDK6 → 3.6.102-SDK6 y v36102-sdk6 → v36102-sdk6). Si una capa ya
lleva el sello nuevo (o nunca lo llevó), no se toca. El SDK NO cambia; el
cambio r111 vive en ONBOARDING (c12 ▶ JUGAR + diorama del hall + guía del
primer saque + altura auto · c00 idioma detectado + catálogo v6 · c13
tut_end) — hito M4 del roadmap MEJORAS.md."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.101-SDK6', '3.6.102-SDK6'), ('v36101-sdk6', 'v36102-sdk6')]

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
    return 'ya'

def main():
    capas = sorted(SCR.glob('qa_*.py'))
    tocados = []
    for p in capas:
        if p.name.startswith('sella_'):
            continue   # los selladores no se sellan a sí mismos
        r = sella_fichero(p)
        if isinstance(r, int) and r > 0:
            tocados.append((p.name, r))
    print('== SELLADO r111 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.102-SDK6 / v36102-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')

if __name__ == '__main__':
    main()
