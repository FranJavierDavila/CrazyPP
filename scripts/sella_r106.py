#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 106 · SELLADO EN CASCADA de las capas QA a 3.6.98-SDK6.

Barrido genérico e idempotente r106: en TODA capa qa_*.py que aún lleve el
sello de la ronda anterior se sustituyen los dos tokens de versión
(3.6.97-SDK6 → 3.6.98-SDK6 y v3697-sdk6 → v3698-sdk6). Si una capa ya lleva
el sello nuevo (o nunca lo llevó), no se toca. El SDK NO cambia (1.6.0
continúa); el cambio r106 vive en el NÚCLEO (c12: háptica del bote
calibrada dentro del guard + canto distinguible + red palpable — hito M1
de MEJORAS.md) y en el HUB (descargas al día con la versión)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.97-SDK6', '3.6.98-SDK6'), ('v3697-sdk6', 'v3698-sdk6')]

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
    ya = all(t.count(nuevo) > 0 for _, nuevo in VERSIONES if nuevo in orig or True)
    return 'ya' if ya else 0

def main():
    capas = sorted(SCR.glob('qa_*.py'))
    tocados = []
    for p in capas:
        if p.name.startswith('sella_'):
            continue   # los selladores no se sellan a sí mismos
        r = sella_fichero(p)
        if isinstance(r, int) and r > 0:
            tocados.append((p.name, r))
    print('== SELLADO r106 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.98-SDK6 / v3698-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')

if __name__ == '__main__':
    main()
