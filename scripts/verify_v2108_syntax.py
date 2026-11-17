#!/usr/bin/env python3
"""v2.108 · Verificación sintáctica: módulos ESM + bloques <script> del index.html."""
import re, subprocess, os, tempfile, sys

BASE = '/home/z/my-project/crazypp'
fails = 0

# 1) Módulos de campeonato (ESM) — copiar a .mjs y node --check
for cid in ('oeste', 'locura', 'magia'):
    src = f'{BASE}/championships/{cid}/index.js'
    dst = f'/tmp/chk_{cid}.mjs'
    with open(src, encoding='utf-8') as f:
        code = f.read()
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(code)
    r = subprocess.run(['node', '--check', dst], capture_output=True, text=True)
    ok = r.returncode == 0
    print(f'[{"OK" if ok else "FAIL"}] módulo {cid} ({len(code)//1024} KB)')
    if not ok:
        fails += 1
        print(r.stderr[:1500])

# 2) Bloques <script> inline del index.html (sin src=) — envueltos como .mjs
#    (el juego usa <script type="module"> para el núcleo)
with open(f'{BASE}/index.html', encoding='utf-8') as f:
    html = f.read()
blocks = re.findall(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', html, re.S | re.I)
print(f'bloques <script> inline: {len(blocks)}')
for i, (attrs, code) in enumerate(blocks):
    if not code.strip():
        continue
    is_mod = 'module' in attrs.lower()
    ext = 'mjs' if is_mod else 'js'
    dst = f'/tmp/chk_html_{i}.{ext}'
    with open(dst, 'w', encoding='utf-8') as f:
        f.write(code)
    r = subprocess.run(['node', '--check', dst], capture_output=True, text=True)
    if r.returncode != 0:
        fails += 1
        print(f'[FAIL] bloque #{i} ({attrs.strip()[:40]})')
        print(r.stderr[:1200])
    else:
        print(f'[OK] bloque #{i} ({len(code)//1024} KB, {"module" if is_mod else "classic"})')

print('\nRESULTADO:', 'TODO OK' if fails == 0 else f'{fails} FALLOS')
sys.exit(1 if fails else 0)
