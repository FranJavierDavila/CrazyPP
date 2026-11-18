#!/usr/bin/env python3
"""Mapa estructural de public/game.html (v3.6.0): bloques top-level y límites de corte."""
import re

SRC = '/home/z/my-project/public/game.html'
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

print(f'total líneas: {len(lines)}')
pat = re.compile(r'^(class |const [A-Z_]{3,}\s*=|function [A-Za-z_]|import |export |let [A-Z_]{3,}\s*=|\/\/ ═|/\* ═)')
marks = []
for i, ln in enumerate(lines, 1):
    if 381 <= i <= 17032 and pat.match(ln):
        marks.append((i, ln.rstrip()[:95]))

print(f'marcas top-level en el módulo: {len(marks)}')
for i, ln in marks:
    print(f'{i:6d}  {ln}')
