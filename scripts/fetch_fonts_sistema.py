#!/usr/bin/env python3
"""Instala Baloo 2 + Nunito Sans como fuentes del sistema (para imprimir
PDFs con Playwright/Chromium, que no incrusta webfonts @font-face).
Lección de la V2.125: imprimir desde una variante SIN @font-face usando
estas fuentes del sistema."""
import re, os, urllib.request, subprocess, sys

OUT_DIR = os.path.expanduser('~/.local/share/fonts/crazypp_manual')
os.makedirs(OUT_DIR, exist_ok=True)

FAMILIES = [
    ('Baloo 2', 'family=Baloo+2:wght@400;500;600;700;800'),
    ('Nunito Sans', 'family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700;6..12,800;6..12,900'),
]

n = 0
for nombre, q in FAMILIES:
    url = f'https://fonts.googleapis.com/css2?{q}'
    req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.88'})  # UA simple -> TTF
    css = urllib.request.urlopen(req, timeout=30).read().decode('utf-8')
    ttfs = re.findall(r'src:\s*url\((https://[^)]+\.ttf)\)', css)
    if not ttfs:
        print(f'AVISO: sin .ttf para {nombre}'); continue
    for u in sorted(set(ttfs)):
        h = u.split('/')[-2] + '-' + u.split('/')[-1]
        dest = os.path.join(OUT_DIR, h)
        if not os.path.exists(dest):
            data = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'curl/7.88'}), timeout=60).read()
            open(dest, 'wb').write(data)
        n += 1
        print(f'OK {nombre}: {h} ({os.path.getsize(dest)//1024} KB)')
        # solo el primer ttf por familia (regular); Google con UA curl devuelve 1 archivo por peso
subprocess.run(['fc-cache', '-f', OUT_DIR], check=False)
r = subprocess.run(['fc-list'], capture_output=True, text=True)
print('--- instaladas en crazypp_manual:', r.stdout.count('crazypp_manual'))
sys.exit(0 if n else 1)
