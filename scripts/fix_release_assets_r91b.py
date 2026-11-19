#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_release_assets_r91b.py — reemplaza los ZIPs del release v3.6.182-SDK6
que cambiaron de tamaño con el hotfix (el build_zip regeneró los 4 en
public/descargas). Borra los assets desactualizados y sube los nuevos."""
import os
import requests

OWNER_REPO = 'FranJavierDavila/CrazyPP'
TAG = 'v3.6.182-SDK6'
H = {'Authorization': f"Bearer {os.environ['GIT_TOKEN']}",
     'Accept': 'application/vnd.github+json'}
api = f'https://api.github.com/repos/{OWNER_REPO}'

rel = requests.get(f'{api}/releases/tags/{TAG}', headers=H, timeout=(15, 60))
rel.raise_for_status()
rid = rel.json()['id']

zips = sorted(os.listdir('public/descargas'))
locales = {z: os.path.getsize(f'public/descargas/{z}') for z in zips}
print('ZIPs locales:', {k: f'{v:,}' for k, v in locales.items()})

assets = requests.get(f'{api}/releases/{rid}/assets?per_page=100',
                      headers=H, timeout=(15, 60)).json()
for a in assets:
    if a['name'] in locales and a['size'] != locales[a['name']]:
        d = requests.delete(f'{api}/releases/{rid}/assets/{a["id"]}',
                            headers=H, timeout=(15, 60))
        print(f'  · borrado {a["name"]} ({a["size"]:,} B obsoleto): {d.status_code}')
    elif a['name'] in locales:
        print(f'  · {a["name"]} ya está ({a["size"]:,} B) — omitido')

for z, size in locales.items():
    existe = {a['name'] for a in assets}
    if z in existe and size == next(a['size'] for a in assets if a['name'] == z):
        continue
    print(f'  · subiendo {z} ({size/1e6:.1f} MB)…')
    with open(f'public/descargas/{z}', 'rb') as fh:
        up = requests.post(
            f'https://uploads.github.com/repos/{OWNER_REPO}/releases/{rid}/assets?name={z}',
            headers={**H, 'Content-Type': 'application/zip'}, data=fh.read(),
            timeout=(30, 1800))
    print(f'    → {up.status_code}')
    up.raise_for_status()

final = requests.get(f'{api}/releases/{rid}/assets?per_page=100',
                     headers=H, timeout=(15, 60)).json()
print('ASSETS FINALES:', {a['name']: a['size'] for a in final})
