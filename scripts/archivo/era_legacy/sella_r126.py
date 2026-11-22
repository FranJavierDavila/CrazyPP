#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 126 · SELLADO EN CASCADA de las capas QA a 3.6.115-SDK6.

Barrido genérico e idempotente (patrón sella_r112/r121/r122/r123/r124/r125):
en TODA capa qa_*.py que aún lleve el sello de la ronda anterior se
sustituyen los dos tokens de versión (3.6.114-SDK6 → 3.6.115-SDK6 ·
v36114-sdk6 → v36115-sdk6). Si una capa ya lleva el sello nuevo (o nunca lo
llevó), no se toca. El SDK NO cambia; la ronda r126 vive en P4.1 (lección de
la primera partida real): verCompara + aviso de build EN LA SALA (c09/c12) +
telemetría ver_mismatch + cache-busting del landing (deploy_pages.py).
RAIZ apunta al mount vivo (/home/z/my-project/upload)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.114-SDK6', '3.6.115-SDK6'), ('v36114-sdk6', 'v36115-sdk6')]

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
    if t != orig:
        p.write_text(t, encoding='utf-8')
        return cambios
    return None

def main():
    tocados = 0
    for p in sorted(SCR.glob('qa_*.py')):
        n = sella_fichero(p)
        if n is not None:
            print(f'  ✓ qa/{p.name} · {n} sello(s)')
            tocados += 1
    # también las capas bateria_* y los test_*.mjs de casa (si llevan sello)
    for p in sorted(list(SCR.glob('bateria_*.py')) + list(SCR.glob('test_*.mjs'))):
        n = sella_fichero(p)
        if n is not None:
            print(f'  ✓ {p.name} · {n} sello(s)')
            tocados += 1
    print(f'\nsellado r126 completo: {tocados} fichero(s) tocados.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
