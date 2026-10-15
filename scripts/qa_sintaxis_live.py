#!/usr/bin/env python3
"""QA de sintaxis: extrae los <script> inline de game.html y tv.html y los
valida con node --check (los módulos ES se comprueban como módulos)."""
import re, subprocess, sys, tempfile, os

for html in ['public/game.html', 'public/tv.html']:
    src = open(html, encoding='utf-8').read()
    blocks = re.findall(r'<script(?![^>]*\bsrc=)([^>]*)>(.*?)</script>', src, re.S)
    ok = True
    for i, (attrs, code) in enumerate(blocks):
        if not code.strip() or 'importmap' in attrs:
            continue
        es_mod = 'type="module"' in attrs
        suf = '.mjs' if es_mod else '.js'
        with tempfile.NamedTemporaryFile('w', suffix=suf, delete=False, encoding='utf-8') as f:
            f.write(code)
            path = f.name
        r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
        os.unlink(path)
        tag = f'{html} #{i} {"module" if es_mod else "classic"}'
        if r.returncode != 0:
            ok = False
            print(f'✗ {tag}\n{r.stderr[:1200]}')
        else:
            print(f'✓ {tag} ({len(code)} chars)')
    if not ok:
        sys.exit(1)
print('SINTAXIS OK')
