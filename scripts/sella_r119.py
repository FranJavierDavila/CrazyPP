#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 119 · SELLADO EN CASCADA de las capas QA a 3.6.108-SDK6.

Barrido genérico e idempotente r119 (heredado de r115): en TODA capa
qa_*.py que aún lleve el sello de la ronda anterior se sustituyen los
tokens de versión (3.6.107-SDK6 → 3.6.108-SDK6 y v36107-sdk6 →
v36108-sdk6). Después se re-anclan los TAMAÑOS BYTE-EXACTOS de los 3
ZIPs en la capa H (qa_descargas_v366.py) con los construidos esta ronda.

El SDK (1.6.0) NO cambia esta ronda. El cambio r119 vive en c12+c00
(M7c · DOBLES 2v2 prototipo: dos IA extra con arbitraje de alcance,
botón en AJUSTES › JUEGO, limpieza al terminar y i18n ES/EN)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.107-SDK6', '3.6.108-SDK6'), ('v36107-sdk6', 'v36108-sdk6')]

# tamaños byte-exactos de los ZIPs v36108 (construidos esta ronda)
TAMANOS = [
    (146775500, 146776773),   # COMPLETO
    (18568232, 18569505),     # ligera
    (146761335, 146762608),   # CLOUDFLARE
]


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
    for viejo, nuevo in TAMANOS:
        s_v, s_n = str(viejo), str(nuevo)
        n = t.count(s_v)
        if n:
            t = t.replace(s_v, s_n)
            cambios += n
    if cambios:
        p.write_text(t, encoding='utf-8')
        return cambios
    return 'ya'


def main():
    total = 0
    tocados = 0
    for p in sorted(SCR.glob('qa_*.py')) + sorted(SCR.glob('smoke_*.py')):
        r = sella_fichero(p)
        if r and r != 'ya':
            tocados += 1
            total += r
            print(f'  · {p.name}: {r} sello(s)')
        elif r == 'ya':
            print(f'  · {p.name}: ya sellado')
    print(f'\nSELLA r119: {tocados} capas re-selladas · {total} tokens')


if __name__ == '__main__':
    main()
