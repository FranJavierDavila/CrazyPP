#!/usr/bin/env python3
"""Descarga las fuentes de Google (Baloo 2 + Nunito Sans) y reescribe el CSS a rutas locales."""
import re, os, urllib.request, hashlib

CSS_IN = '/tmp/fonts.css'
OUT_DIR = '/home/z/my-project/download/fonts'
CSS_OUT = os.path.join(OUT_DIR, 'fonts.css')
os.makedirs(OUT_DIR, exist_ok=True)

css = open(CSS_IN, encoding='utf-8').read()
urls = sorted(set(re.findall(r'https://[^)]+\.woff2', css)))
mapping = {}
for u in urls:
    h = hashlib.md5(u.encode()).hexdigest()[:10]
    name = f"{h}.woff2"
    dest = os.path.join(OUT_DIR, name)
    if not os.path.exists(dest):
        req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0 Chrome/120.0'})
        data = urllib.request.urlopen(req, timeout=30).read()
        open(dest, 'wb').write(data)
    mapping[u] = name
    print(f"OK {name} {os.path.getsize(dest)//1024} KB <- {u[-40:]}")

for u, name in mapping.items():
    css = css.replace(u, name)  # fonts.css vive junto a los .woff2

open(CSS_OUT, 'w', encoding='utf-8').write(css)
print(f"\nCSS reescrito: {CSS_OUT} ({len(mapping)} fuentes locales)")
