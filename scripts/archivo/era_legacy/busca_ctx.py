#!/usr/bin/env python3
"""Búsqueda con contexto en módulos enormes (c12/c13/c01/c00).

Uso: python3 scripts/busca_ctx.py <fichero> <regex> [ctx_antes] [ctx_despues] [max_matches]
Imprime nº de línea + contenido truncado a 400 chars (evita líneas base64).
"""
import re
import sys

MAXLEN = 400

def main():
    fic, pat = sys.argv[1], sys.argv[2]
    antes = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    desp = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    maxm = int(sys.argv[5]) if len(sys.argv) > 5 else 40
    rx = re.compile(pat)
    with open(fic, 'rb') as f:
        lineas = f.read().split(b'\n')
    hits = [i for i, l in enumerate(lineas) if rx.search(l.decode('utf-8', 'replace'))]
    mostrados = 0
    prev_hasta = -1
    for i in hits:
        if mostrados >= maxm:
            print(f'... ({len(hits) - mostrados} coincidencias más)')
            break
        ini, fin = max(0, i - antes), min(len(lineas), i + desp + 1)
        if ini <= prev_hasta:
            ini = prev_hasta + 1
        if ini > i:
            pass
        for j in range(ini, fin):
            t = lineas[j].decode('utf-8', 'replace')
            if len(t) > MAXLEN:
                t = t[:MAXLEN] + f' …[+{len(lineas[j]) - MAXLEN}B]'
            marca = '»' if j == i else ' '
            print(f'{marca}{j + 1:6d} {t}')
        prev_hasta = fin - 1
        mostrados += 1
        print('---')

if __name__ == '__main__':
    main()
