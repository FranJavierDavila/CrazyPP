#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA de la CADENA DE VERSIÓN (roadmap P1 · «version.json único»).
Verifica que la única fuente de verdad (src/game/VERSION.json) y TODOS los
sellos derivados cuentan la misma historia:
  c00 (const VERSION) · badge 03_body (#verBadge) · hub /descargas ·
  manifests de los 5 campeonatos · champ_sdk.js (SDK_VERSION) ·
  public/game.html (sha256 == golden) · ensamblador BYTE-EXACTO ·
  servidores :3000 y :81 (si están vivos).
Uso: python3 scripts/qa_version.py"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

# 1 · VERSION.json
V = json.loads((SRC / 'VERSION.json').read_text(encoding='utf-8'))
ver = V.get('version')
for campo in ('version', 'fase', 'sdk', 'hub', 'manifests', 'golden'):
    chk(campo in V, f'VERSION.json: campo {campo!r} presente')
chk(ver and ver.count('.') == 2 and '-' in ver, f'versión con formato X.Y.Z-NAME: {ver}')

# 2 · sellos físicos
c00 = (SRC / 'core/c00_pre_three.js').read_text(encoding='utf-8')
chk(c00.count(f"const VERSION = '{ver}'") == 1, 'c00_pre_three.js: const VERSION casa')
body = (SRC / '03_body.html').read_text(encoding='utf-8')
chk(body.count(f'>V{ver}</span>') == 1, '03_body.html: badge #verBadge casa')
hub = (RAIZ / 'src/app/descargas/page.tsx').read_text(encoding='utf-8')
# FASE 144 · re-ancla del hub: desde la higiene r47/r48 la página de
# descargas apunta al ÚLTIMO RELEASE REAL (v36139 → V3.6.140-SDK6, assets
# verificados en GitHub API) y NO a la versión de desarrollo — apuntar a
# ZIPs inexistentes fue el fallo que la higiene corrigió. El check exige
# coherencia de la página consigo misma (sello de release presente), no
# que anuncie la versión en desarrollo.
_hub_ver = 'V3.6.140-SDK6'
chk(hub.count(_hub_ver) >= 3, f'hub: menciones del release vivo {_hub_ver} ({hub.count(_hub_ver)})')
chk(hub.count(V['hub']) >= 3, f'hub: menciones del sello {V["hub"]} ({hub.count(V["hub"])})')

# 2b · r109 · M3 PWA: sello del service worker + manifest + iconos
swjs = (RAIZ / 'public/sw.js').read_text(encoding='utf-8')
chk(swjs.count(f"const CACHE = 'crazypp-v{ver}'") == 1,
    'public/sw.js: const CACHE casa con la versión (el bump gobierna la caché)')
man = json.loads((RAIZ / 'public/manifest.webmanifest').read_text(encoding='utf-8'))
chk(man.get('start_url') == './game.html' and man.get('scope') == './',
    'manifest: start_url ./game.html + scope ./ (compatible /CrazyPP/)')
chk(man.get('display') == 'fullscreen', 'manifest: display fullscreen (Quest)')
chk(man.get('name', '').startswith('CRAZY PING PONG'), 'manifest: nombre de la casa')
for _ico in man.get('icons', []):
    _f = RAIZ / 'public' / str(_ico.get('src', ''))
    _ok = _f.exists() and _f.stat().st_size > 1000
    chk(_ok, f"manifest: icono {_ico.get('src')} existe ({_f.stat().st_size if _f.exists() else 0:,} B)")
chk(len(man.get('icons', [])) >= 3, 'manifest: 3 iconos (192 + 512 + maskable)')

# 3 · manifests de los 5 campeonatos
for mod, esperado in V['manifests'].items():
    m = json.loads((RAIZ / f'public/championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    chk(m.get('version') == esperado, f'manifest {mod} = v{esperado}')

# 4 · SDK
sdk = (RAIZ / 'public/championships/sdk/champ_sdk.js').read_text(encoding='utf-8')
chk(f"const SDK_VERSION = '{V['sdk']}'" in sdk, f'champ_sdk.js: SDK_VERSION = {V["sdk"]}')

# 5 · game.html == golden == VERSION.json.golden
game = RAIZ / 'public' / 'game.html'
sha_local = sha256(game)
chk(sha_local == V['golden'], 'sha256(game.html) == VERSION.json.golden')
dorado = next(l.strip() for l in (SRC / 'GOLDEN_SHA256.txt').read_text(encoding='utf-8').splitlines()
              if l.strip() and not l.startswith('#'))
chk(sha_local == dorado, 'sha256(game.html) == GOLDEN_SHA256.txt')
chk(f"const VERSION = '{ver}'" in game.read_text(encoding='utf-8'),
    'game.html ensamblado lleva el sello de versión')

# 6 · ensamblador (guard de versión única + BYTE-EXACTO)
r = subprocess.run([sys.executable, str(RAIZ / 'scripts' / 'build_game.py')],
                   capture_output=True, text=True)
chk('BYTE-EXACTO' in r.stdout and r.returncode == 0,
    'build_game.py: guard de versión OK + BYTE-EXACTO')

# 7 · servidores (si están vivos)
import urllib.request
def vivo(url):
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.read()
    except Exception:
        return None

for puerto in (3000, 81):
    datos = vivo(f'http://localhost:{puerto}/game.html')
    if datos is None:
        print(f'  · (:{puerto} no responde — check en vivo omitido)')
        continue
    chk(hashlib.sha256(datos).hexdigest() == sha_local,
        f':{puerto} sirve el game.html de esta versión (byte-exacto)')

print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
sys.exit(1 if fails else 0)
