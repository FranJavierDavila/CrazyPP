#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r109-c · LIMPIEZA DE GITHUB — petición del dueño («solo vamos a dejar las
ramas principal y la que sirve el juego: main y pages · todo el material NO
IMPRESCINDIBLE con antigüedad superior a 1 semana se elimine definitivamente»).

Plan (asertado, con SIMULACIÓN por defecto):
  1. RELEASES: fuera todas las anteriores a 2026-11-14 (cada una arrastra sus
     4 ZIPs, ~264 MB). Se conservan las de la última semana.
  2. TAGS: fuera todos los de fecha anterior al corte (138 de 178). Los
     commits siguen alcanzables desde main — los tags eran sólo etiquetas.
  3. RAMAS: fuera proyecto, exp/live-tv y las tres archive/* — antes, los dos
     archivos con commits únicos (main-web-1510 · overlay-r23) se amarran a
     tags rescate/* para que NADA sea irrecuperable. proyecto y exp/live-tv
     están íntegramente contenidos en main (0 commits únicos, verificado
     ronda r109).
  4. INFORME: ramas, tags y releases restantes.

USO (necesita el token del dueño en el entorno — nunca se escribe en fichero):
  GIT_TOKEN=... python3 scripts/limpieza_github_r109.py            # simulación
  GIT_TOKEN=... python3 scripts/limpieza_github_r109.py --ejecutar # real
"""
import os
import subprocess
import sys

try:
    import requests
except ImportError:
    sys.exit('FALLO: falta requests (python3 -m pip install requests)')

CUTOFF = '2026-11-14'
OR = 'FranJavierDavila/CrazyPP'
API = f'https://api.github.com/repos/{OR}'
EJECUTAR = '--ejecutar' in sys.argv

tok = os.environ.get('GIT_TOKEN', '').strip()
if not tok:
    sys.exit('✗ GIT_TOKEN no está en el entorno. Uso:\n'
             '  GIT_TOKEN=... python3 scripts/limpieza_github_r109.py [--ejecutar]')
H = {'Authorization': f'Bearer {tok}', 'Accept': 'application/vnd.github+json'}


def api(met, url, **kw):
    r = requests.request(met, url, headers=H, timeout=(15, 300), **kw)
    if r.status_code >= 300 and r.status_code != 404:
        sys.exit(f'✗ {met} {url} → {r.status_code}: {r.text[:300]}')
    return r


def git_push(*refs):
    """push con el PAT del dueño (patrón deploy_pages.py — el token jamás
    se escribe en fichero ni en disco)."""
    helper = "!f() { echo username=FranJavierDavila; echo password=$GIT_TOKEN; }; f"
    cmd = ['git', '-c', f'credential.helper={helper}', 'push', 'origin', *refs]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f'✗ git push {refs} → {r.stderr[-400:]}')


# ── 1. releases ─────────────────────────────────────────────────────
viejas, nuevas = [], []
page = 1
while True:
    lista = api('GET', f'{API}/releases?per_page=100&page={page}').json()
    if not isinstance(lista, list) or not lista:
        break
    for rel in lista:
        (nuevas if rel['created_at'][:10] >= CUTOFF else viejas).append(rel)
    if len(lista) < 100:
        break
    page += 1

mb = sum(sum(a['size'] for a in r.get('assets', [])) for r in viejas) / 1e6
print(f'== RELEASES ==\n  se quedan (≥ {CUTOFF}): {len(nuevas)}')
print(f'  FUERA: {len(viejas)} releases · {mb:.0f} MB de ZIPs en assets')
if EJECUTAR:
    for rel in viejas:
        api('DELETE', f"{API}/releases/{rel['id']}")
        print(f"  · borrada {rel['tag_name']} ({rel['created_at'][:10]})")

# ── 2. tags ─────────────────────────────────────────────────────────
fuera = subprocess.run(
    ['git', 'for-each-ref', 'refs/tags', '--format=%(creatordate:short) %(refname:short)'],
    capture_output=True, text=True).stdout
tags_fuera = [n for f, _, n in (l.partition(' ') for l in fuera.splitlines()) if f < CUTOFF]
print(f'== TAGS ==\n  FUERA (fecha < {CUTOFF}): {len(tags_fuera)} de '
      f'{len(fuera.splitlines())}')
if EJECUTAR:
    # r112 · borrado TOLERANTE: el listado sale del LOCAL (git for-each-ref),
    # pero limpiezas anteriores ya quitaron del remoto tags que aquí siguen
    # listados — un solo ref inexistente mataba el lote entero (push atómico).
    # Lote de 25 y, si casca, tag a tag tolerando «remote ref does not exist».
    borrados = ausentes = 0
    for i in range(0, len(tags_fuera), 25):
        lote = tags_fuera[i:i + 25]
        p = subprocess.run(['git', '-c', 'credential.helper=!f() { echo '
                           'username=FranJavierDavila; echo password=$GIT_TOKEN; }; f',
                           'push', 'origin', '--delete'] + lote,
                          capture_output=True, text=True)
        if p.returncode == 0:
            borrados += len(lote)
            print(f'  · lote {i // 25 + 1}: {len(lote)} tags borrados')
            continue
        for tag in lote:
            q = subprocess.run(['git', '-c', 'credential.helper=!f() { echo '
                               'username=FranJavierDavila; echo password=$GIT_TOKEN; }; f',
                               'push', 'origin', '--delete', tag],
                              capture_output=True, text=True)
            if q.returncode == 0:
                borrados += 1
            elif 'remote ref does not exist' in q.stderr:
                ausentes += 1   # ya no estaba: nada que borrar
            else:
                print(f'  ✗ {tag}: {q.stderr.strip()[:150]}')
    print(f'  · {borrados} tags borrados · {ausentes} ya ausentes en el remoto')

# ── 3. ramas ────────────────────────────────────────────────────────
print('== RAMAS ==')
RESCATES = {
    'rescate/main-web-1510-20261015': 'ca53ffea6d2f239586e0ed03f66ce64ab0801b0b',
    'rescate/overlay-r23-20261107': '300157c7081613c87342374c477fbc6c0319ce5e',
}
if EJECUTAR:
    for tag, sha in RESCATES.items():
        subprocess.run(['git', 'tag', '-f', tag, sha], check=True)
        git_push(f'refs/tags/{tag}')
        print(f'  · tag de rescate {tag} → {sha[:9]} (la rama archive/* puede morir)')
FUERA_RAMAS = ['proyecto', 'exp/live-tv', 'archive/main-web-1510',
               'archive/linea-b-v3627', 'archive/overlay-r23-20261107']
print(f'  FUERA: {", ".join(FUERA_RAMAS)} (quedan main + pages)')
if EJECUTAR:
    for rama in FUERA_RAMAS:   # r112: una a una — misma tolerancia que los tags
        q = subprocess.run(['git', '-c', 'credential.helper=!f() { echo '
                           'username=FranJavierDavila; echo password=$GIT_TOKEN; }; f',
                           'push', 'origin', '--delete', rama],
                          capture_output=True, text=True)
        if q.returncode == 0:
            print(f'  · rama {rama} borrada en el remoto')
        elif 'remote ref does not exist' in q.stderr:
            print(f'  · rama {rama} ya no existía')
        else:
            print(f'  ✗ rama {rama}: {q.stderr.strip()[:150]}')

# ── 4. informe ──────────────────────────────────────────────────────
print('== RESTANTE ==')
ramas = api('GET', f'{API}/branches?per_page=100').json()
print('  ramas: ' + ', '.join(sorted(b['name'] for b in ramas)))
n_tags = int(subprocess.run(['git', 'ls-remote', '--tags', 'origin'],
                            capture_output=True, text=True).stdout.count('refs/tags/'))
print(f'  tags en el remoto: ~{n_tags} (cada push de borrado los recuenta)')
print('  releases: las de la última semana (el informe de arriba)')
if not EJECUTAR:
    print('\nSIMULACIÓN — añade --ejecutar para borrar de verdad.')
