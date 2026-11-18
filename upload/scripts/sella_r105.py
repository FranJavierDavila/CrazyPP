#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 105 · SELLADO EN CASCADA de las capas QA a 3.6.97-SDK6.

Barrido genérico e idempotente r105: en TODA capa qa_*.py que aún lleve el
sello de la ronda anterior se sustituyen los dos tokens de versión
(3.6.96-SDK6 → 3.6.97-SDK6 y v3696-sdk6 → v3697-sdk6). Si una capa ya lleva
el sello nuevo (o nunca lo llevó), no se toca (lección de la ronda 13:
«ya sellado» cuenta como OK). El SDK NO cambia esta ronda (1.6.0 continúa);
el cambio r105 vive en el NÚCLEO (c12: cursor del menú al plano real
0,90×1,35 + mips OFF en menuTex + repintado por hover throttled a 90 ms) y
en el HUB (descargas al día con la versión).

Los tamaños byte-exactos de los ZIPs v3697 se re-anclaron tras
gen_release_v3697 (qa_descargas_v366: COMPLETO 146.642.414 · ligera
18.436.329 · CLOUDFLARE 146.628.623 · SOLO 6.221)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.96-SDK6', '3.6.97-SDK6'), ('v3696-sdk6', 'v3697-sdk6')]

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
    print('== SELLADO r105 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.97-SDK6 / v3697-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')

if __name__ == '__main__':
    main()
