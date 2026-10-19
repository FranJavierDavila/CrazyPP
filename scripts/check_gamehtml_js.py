#!/usr/bin/env python3
"""Extrae los bloques <script> inline de public/game.html y valida sintaxis con node --check."""
import re, subprocess, sys, tempfile, os

SRC = '/home/z/my-project/public/game.html'
html = open(SRC, encoding='utf-8').read()

# bloques <script> SIN atributo src (inline)
blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', html, re.S | re.I)
print(f'{len(blocks)} bloques inline encontrados')
fails = 0
for i, code in enumerate(blocks):
    if not code.strip():
        continue
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(code)
        path = f.name
    r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
    if r.returncode != 0:
        fails += 1
        print(f'  BLOQUE {i}: FALLO ({len(code)} chars)')
        print(r.stderr[:1200])
    else:
        print(f'  BLOQUE {i}: OK ({len(code)} chars)')
    os.unlink(path)
sys.exit(1 if fails else 0)
