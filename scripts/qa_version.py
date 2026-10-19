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

RAIZ = Path('/home/z/my-project')
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
chk(hub.count(ver) >= 3, f'hub: menciones de {ver} ({hub.count(ver)})')
chk(hub.count(V['hub']) >= 3, f'hub: menciones del sello {V["hub"]} ({hub.count(V["hub"])})')

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
