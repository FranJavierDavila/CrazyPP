#!/usr/bin/env python3
"""Lector de rangos seguro para ficheros con líneas gigantes (base64).
Uso: python3 scripts/_rl.py <fichero> <ini> <fin> [maxlen]"""
import sys
path, ini, fin = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
maxlen = int(sys.argv[4]) if len(sys.argv) > 4 else 240
with open(path, encoding='utf-8', errors='replace') as f:
    for i, line in enumerate(f, 1):
        if i < ini:
            continue
        if i > fin:
            break
        t = line.rstrip('\n')
        if len(t) > maxlen:
            t = t[:maxlen] + f'  …[{len(t)} chars]'
        print(f'{i}: {t}')
