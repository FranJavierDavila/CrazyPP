#!/usr/bin/env python3
"""QA sintaxis · extrae cada bloque <script> de public/game.html y lo valida
con node --check (bloques sin atributos src)."""
import re, subprocess, sys, tempfile, os

SRC = '/home/z/my-project/public/game.html'
html = open(SRC, encoding='utf-8').read()
# excluye importmap/JSON: sólo JS ejecutable (sin src y sin type no-JS)
blocks = re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*\btype="(?:importmap|application/[^"]+)")[^>]*>(.*?)</script>', html, re.S | re.I)
ok = 0
for i, code in enumerate(blocks):
    if not code.strip():
        continue
    with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as f:
        f.write(code)
        tmp = f.name
    r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
    os.unlink(tmp)
    if r.returncode == 0:
        ok += 1
        print(f'  bloque {i}: OK ({len(code)} chars)')
    else:
        print(f'  bloque {i}: FAIL\n{r.stderr[:2000]}')
        sys.exit(1)
print(f'RESULTADO: OK · {ok} bloques validados')
