#!/usr/bin/env python3
"""Extrae el <script type="module"> de public/game.html y lo valida con node --check."""
import re, subprocess, sys

html = open('/home/z/my-project/public/game.html', encoding='utf-8').read()
m = re.search(r'<script type="module"[^>]*>(.*?)</script>', html, re.S)
if not m:
    print('NO SCRIPT MODULE FOUND'); sys.exit(1)
js = m.group(1)
open('/home/z/my-project/scripts/_game_module.mjs', 'w', encoding='utf-8').write(js)
r = subprocess.run(['node', '--check', '/home/z/my-project/scripts/_game_module.mjs'],
                   capture_output=True, text=True)
print('node --check exit:', r.returncode)
if r.stdout: print(r.stdout[:3000])
if r.stderr: print(r.stderr[:3000])
sys.exit(r.returncode)
