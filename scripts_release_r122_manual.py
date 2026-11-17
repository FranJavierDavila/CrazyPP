#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r122 · release manual v3.6.111-SDK6 (pasos EXACTOS de do_release en
scripts/deploy_pages.py, ejecutados fuera del deploy porque assemble()
limpia public/descargas antes del paso release). Idempotente."""
import glob
import json
import os
import subprocess
import sys
import time

import requests

REPO = '/home/z/my-project'
OWNER_REPO = 'FranJavierDavila/CrazyPP'
VERSION = '3.6.111-SDK6'
TAG = f'v{VERSION}'
PAGES_URL = 'https://franjavierdavila.github.io/CrazyPP/'

tok = open('/home/z/my-project/upload/scripts/worker-tele/.github-pat').read().strip()
H = {'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'}
api = f'https://api.github.com/repos/{OWNER_REPO}'

zips = sorted(glob.glob(os.path.join(REPO, 'public', 'descargas', f'crazypp-v36111-*.zip')))
solo = os.path.join(REPO, 'public', 'descargas', 'crazypp-live-service-SOLO.zip')
if os.path.exists(solo):
    zips.append(solo)
print('ZIPs:', [os.path.basename(z) for z in zips])
if len(zips) != 4:
    sys.exit(f'✗ esperaba 4 ZIPs, hay {len(zips)}')

# 1 · tag en HEAD de main (558eca7) + push del tag
subprocess.run(['git', '-C', REPO, 'tag', '-f', TAG, 'HEAD'], check=True)
subprocess.run(['git', '-C', REPO, 'push', '-f', 'origin', f'refs/tags/{TAG}'], check=True,
               env={**os.environ, 'GIT_TOKEN': tok,
                    'GIT_ASKPASS': 'echo', 'GIT_TERMINAL_PROMPT': '0'},
               capture_output=True)
print(f'✓ tag {TAG} pushed')

# 2 · release (idempotente: reutilizar si existe, sin recrear si ya está)
r = requests.get(f'{api}/releases/tags/{TAG}', headers=H, timeout=(15, 60))
if r.status_code == 200:
    rel = r.json()
    print(f"· release existente reutilizada: {rel['id']}")
else:
    body = (f'CRAZY PING PONG **{VERSION}** · FASE 113 — M-RED2 · REVISIÓN COMPLETA DEL NETCODE (r122)\n\n'
            '- **Jugar sin descargar**: ' + PAGES_URL + ' (ábrela en el navegador del visor)\n'
            '- **ZIPs**: COMPLETO (todo, ~147 MB) · ligera (~18 MB) · CLOUDFLARE · SOLO (servicio live, 6 KB)\n'
            '- REVISIÓN COMPLETA pedida por el dueño: FIX CRÍTICO resync sin perspectiva (marcador '
            'invertido / victoria-ELO falsos en el invitado) · guardia de estado ante HIT atrasados · '
            'resync-req (un rechazo legal ya no atasca el lado) · claim sin autoridad (divergencia '
            'detectable) · toss caído re-arma el HELD · higiene RTC (timers, AudioContext, SNAP, '
            'carrera de invitados) · fuga del 2v2 a la academia cerrada · PULSO/reto semanal en el '
            'camino vivo (deuda v3.0.2)\n'
            '- QA del release: cadena completa 75 capas verde · batería multi P1 67/0 · P2 68/0 · '
            'P3 69/0 (0 rechazos del validador, 0 pageerrors) · test_red_nucleo 60/0 · smoke 30/0\n')
    r = requests.post(f'{api}/releases', headers=H, timeout=(15, 120), json={
        'tag_name': TAG, 'name': f'CRAZY PING PONG {VERSION}', 'body': body, 'draft': False,
        'prerelease': False})
    r.raise_for_status()
    rel = r.json()
    print(f"✓ release creada: {rel['id']} · {rel['html_url']}")


# 3 · assets (los 4 ZIPs) —/uploads.github.com + octet-stream, omisión por tamaño
have = {a['name']: a['size'] for a in requests.get(
    f"{api}/releases/{rel['id']}/assets?per_page=100", headers=H, timeout=(15, 60)).json()}
for z in zips:
    name = os.path.basename(z)
    size = os.path.getsize(z)
    if have.get(name) == size:
        print(f'  · asset {name} ya está (mismo tamaño) — omitido')
        continue
    print(f'  · subiendo {name} ({size/1e6:.1f} MB)…')
    with open(z, 'rb') as fh:
        up = requests.post(f'https://uploads.github.com/repos/{OWNER_REPO}/releases/{rel["id"]}/assets?name={name}',
                           headers={**H, 'Content-Type': 'application/zip'},
                           data=fh.read(), timeout=(30, 1800))
    up.raise_for_status()
    print(f'  ✓ asset {name}')
print('· RELEASE COMPLETA')
