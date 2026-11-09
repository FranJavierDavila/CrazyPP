#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 124 · SELLADO EN CASCADA de las capas QA a 3.6.113-SDK6.

Barrido genérico e idempotente (patrón sella_r112/r121/r122/r123): en TODA
capa qa_*.py que aún lleve el sello de la ronda anterior se sustituyen los
dos tokens de versión (3.6.112-SDK6 → 3.6.113-SDK6 · v36112-sdk6 →
v36113-sdk6). Si una capa ya lleva el sello nuevo (o nunca lo llevó), no se
toca. El SDK NO cambia; la ronda r124 vive en PERSISTENCIA (c11/c12/c00):
historial de torneos (pp_torneos_historial_v1) + perfil recordado +
test_m7e_persistencia_v36113 (19/0)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.112-SDK6', '3.6.113-SDK6'), ('v36112-sdk6', 'v36113-sdk6')]

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
    print('== SELLADO r124 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.113-SDK6 / v36113-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')

if __name__ == '__main__':
    sys.exit(main())
