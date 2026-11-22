#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 114 · SELLADO EN CASCADA de las capas QA a 3.6.104-SDK6.

Barrido genérico e idempotente r114 (heredado de r113): en TODA capa
qa_*.py que aún lleve el sello de la ronda anterior se sustituyen los
tokens de versión (3.6.103-SDK6 → 3.6.104-SDK6 y v36103-sdk6 →
v36104-sdk6). Después se re-anclan los TAMAÑOS BYTE-EXACTOS de los 3
ZIPs en la capa H (qa_descargas_v366.py) con los construidos esta ronda.

El SDK (1.6.0) NO cambia esta ronda. El cambio r114 vive en c12:
ancla por estancia + heal del menú + retiro del diorama del hall."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.103-SDK6', '3.6.104-SDK6'), ('v36103-sdk6', 'v36104-sdk6')]

# tamaños byte-exactos de los ZIPs v36104 (construidos esta ronda)
TAMANOS = [
    (146764129, 146764214),   # COMPLETO
    (18557518, 18557603),     # ligera
    (146749964, 146750049),   # CLOUDFLARE
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
    capas = sorted(SCR.glob('qa_*.py'))
    tocados = []
    for p in capas:
        if p.name.startswith('sella_'):
            continue   # los selladores no se sellan a sí mismos
        r = sella_fichero(p)
        if isinstance(r, int) and r > 0:
            tocados.append((p.name, r))
    print('== SELLADO r114 ==')
    for nombre, n in tocados:
        print(f'  ✓ {nombre}: {n} sello(s) → 3.6.104-SDK6 / v36104-sdk6')
    if not tocados:
        print('  (nada que sellar: todas las capas ya estaban al día)')
    print(f'\nTotal capas selladas: {len(tocados)}')
    # verificación: la capa H debe llevar los tamaños NUEVOS
    h = (SCR / 'qa_descargas_v366.py').read_text(encoding='utf-8')
    ok = all(str(n) in h for _, n in TAMANOS)
    print('capa H con tamaños v36104:', 'OK' if ok else 'FALLO')
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
