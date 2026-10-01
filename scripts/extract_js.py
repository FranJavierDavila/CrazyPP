#!/usr/bin/env python3
"""Extrae el <script type="module"> de index.html y lo guarda como .mjs para node --check."""
import re, sys

src = open('/home/z/my-project/download/pingpong-quest3/index.html', encoding='utf-8').read()
m = re.search(r'<script type="module">(.*?)</script>', src, re.S)
if not m:
    sys.exit('No se encontró el script module')
open('/home/z/my-project/scripts/game_module.mjs', 'w', encoding='utf-8').write(m.group(1))
print('Extraído', len(m.group(1)), 'caracteres')
