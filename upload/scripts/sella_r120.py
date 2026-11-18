#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 120 · SELLADO EN CASCADA de las capas QA a 3.6.109-SDK6.

Barrido genérico e idempotente r120 (heredado de r115/r119): en TODA capa
qa_*.py que aún lleve el sello de la ronda anterior se sustituyen los
tokens de versión (3.6.108-SDK6 → 3.6.109-SDK6 y v36108-sdk6 →
v36109-sdk6). Después se re-anclan los TAMAÑOS BYTE-EXACTOS de los 3
ZIPs en la capa H (qa_descargas_v366.py) con los construidos esta ronda.

El SDK (1.6.0) NO cambia esta ronda. El cambio r120 vive en c13
(M7d · PRO TRAINING extendido: t1c ESQUINA EXACTA + t5b METRÓNOMO LOCO,
medallas por ejercicio retroactivas, MEDALLERO DE ORO, PLAN_POOL
congelado y m50/m100 re-anclados al juez vivo)."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.108-SDK6', '3.6.109-SDK6'), ('v36108-sdk6', 'v36109-sdk6')]

# tamaños byte-exactos de los ZIPs v36109 (construidos esta ronda)
TAMANOS = [
    (146776773, 146781526),   # COMPLETO
    (18569505, 18574258),     # ligera
    (146762608, 146767361),   # CLOUDFLARE
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
    print(f'\nSELLA r120: {tocados} capas re-selladas · {total} tokens')


if __name__ == '__main__':
    main()
