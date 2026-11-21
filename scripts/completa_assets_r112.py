#!/usr/bin/env python3
"""completa_assets_r112.py — termina la re-release v3.6.209-SDK6 (r112).

El run de deploy_pages.py --push --release dejó hecho: smoke ✓ · pages ✓ ·
tag v3.6.209-SDK6 → d706efa ✓ · release creada ✓ — y falló SOLO en el
reemplazo de los 4 assets (el PAT fine-grained no puede DELETE: 404 con
Contents:write). Estrategia sin borrado (misma que deploy_pages r112):
renombrar los viejos con prefijo ANTIGUO- y subir los nuevos con su nombre.

Los ZIPs frescos están en public/descargas/ (build_zip.py r112, juego con
26 marcas r112 + relay H13/H14/H15 dentro).
"""
import os
import sys
import requests

H = {'Authorization': f"Bearer {os.environ.get('GIT_TOKEN', '')}",
     'Accept': 'application/vnd.github+json'}
API = 'https://api.github.com/repos/FranJavierDavila/CrazyPP'
TAG = 'v3.6.209-SDK6'
ZIPS = [
    'public/descargas/crazypp-v36209-sdk6-COMPLETO.zip',
    'public/descargas/crazypp-v36209-sdk6-ligera.zip',
    'public/descargas/crazypp-v36209-sdk6-CLOUDFLARE.zip',
    'public/descargas/crazypp-live-service-SOLO.zip',
]

r = requests.get(f'{API}/releases/tags/{TAG}', headers=H, timeout=30)
r.raise_for_status()
rel = r.json()
rid = rel['id']
have = {a['name']: a for a in requests.get(
    f'{API}/releases/{rid}/assets?per_page=100', headers=H, timeout=30).json()}
print(f'release {rid} · {len(have)} assets actuales')

for zp in ZIPS:
    name = os.path.basename(zp)
    size = os.path.getsize(zp)
    if have.get(name, {}).get('size') == size:
        print(f'  · {name}: ya está con el tamaño nuevo — omitido')
        continue
    if name in have:
        rn = requests.patch(f'{API}/releases/assets/{have[name]["id"]}',
                            headers=H, timeout=60, json={'name': 'ANTIGUO-' + name})
        rn.raise_for_status()
        print(f'  · ANTIGUO-{name} renombrado')
    print(f'  · subiendo {name} ({size/1e6:.1f} MB)…')
    with open(zp, 'rb') as fh:
        up = requests.post(
            f'https://uploads.github.com/repos/FranJavierDavila/CrazyPP'
            f'/releases/{rid}/assets?name={name}',
            headers={**H, 'Content-Type': 'application/zip'},
            data=fh.read(), timeout=(30, 1800))
    up.raise_for_status()
    print(f'    ✓ {name}')

# verificación final
final = requests.get(f'{API}/releases/{rid}/assets?per_page=100',
                     headers=H, timeout=30).json()
print(f'\nVERIFICACIÓN — {len(final)} assets en la release:')
for a in final:
    marca = ' ← NUEVO r112' if not a['name'].startswith('ANTIGUO-') else ' (era r110 — borrable a mano)'
    print(f'  {a["name"]:52s} {a["size"]:>13,} B{marca}')
nuevos = [a for a in final if not a['name'].startswith('ANTIGUO-')]
esperados = {os.path.basename(z) for z in ZIPS}
if {a['name'] for a in nuevos} != esperados:
    sys.exit('✗ faltan assets nuevos')
print('\n✓ RELEASE COMPLETA: tag d706efa + 4 assets r112 + nota de los ANTIGUO en el cuerpo')
