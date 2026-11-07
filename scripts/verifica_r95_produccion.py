#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r95_produccion.py — tres vías byte-exacto + agujas r95 en el servido.
Hereda el patrón r94. VIEJO = sha del servido 3.6.86 (r94) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '7af857fd'          # sha256 del servido 3.6.86 (r94) — debe desaparecer
LOCAL8 = 'bdb8a5e6'

def sha(b):
    return hashlib.sha256(b).hexdigest()

def get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.status, r.read()

OK = []
FAIL = []
def CHK(c, m):
    (OK if c else FAIL).append(m)
    print(('  ✓ ' if c else '  ✗ FALLO: ') + m)

local = open(RAIZ + '/public/game.html', 'rb').read()
sha_local = sha(local)
golden = None
for line in open(RAIZ + '/src/game/GOLDEN_SHA256.txt', encoding='utf-8'):
    if len(line.strip()) == 64 and all(c in '0123456789abcdef' for c in line.strip()):
        golden = line.strip()
        break
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (bdb8a5e6 r95)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3687')
        s1 = sha(servido)
        if st == 200 and not s1.startswith(VIEJO):
            print('  · servido NUEVO detectado: %s… (%d B)' % (s1[:16], len(servido)))
            break
        print('  · aún viejo (%s…) — reintento en 30 s' % s1[:12])
    except Exception as e:
        print('  · (%s) — reintento en 30 s' % e)
    time.sleep(30)

if servido is None or sha(servido).startswith(VIEJO):
    print('✗ Pages no publicó la build nueva en 8 min')
    sys.exit(1)

s1 = sha(servido)
open(RAIZ + '/scripts/_r95_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3687')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.87' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.87')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r95_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
CHK("const VERSION = '3.6.87-SDK6'" in gh, 'aguja servido: sello 3.6.87-SDK6')
CHK('>V3.6.87-SDK6<' in gh, 'aguja servido: badge V3.6.87-SDK6')
CHK('setMusicVol(v) {' in gh, 'aguja servido: canal MÚSICA (r95)')
CHK('setFxVol(v) {' in gh, 'aguja servido: canal EFECTOS (r95)')
CHK('const MESA_ALTOS' in gh, 'aguja servido: MESA_ALTOS (r95)')
CHK('function relayoutMesa(group)' in gh, 'aguja servido: relayoutMesa (r95)')
CHK('_rivStyleCalc() {' in gh, 'aguja servido: estilo del rival (r95)')
CHK("T('fanf_stats'" in gh, 'aguja servido: chip de estadísticas (r95)')
CHK('contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)' in gh, 'aguja servido: c06 swing tangente (r93 intacta)')
CHK('const rise0 = sw.flat ? 0 : 0.05;' in gh, 'aguja servido: c12 rise0/flat (r93 intacta)')

MOD = [('index.js (sin cartel en duelos)', RAIZ + '/public/championships/halloween/index.js', ''),
       ('manifest.json (v9)', RAIZ + '/public/championships/halloween/manifest.json', ''),
       ('melodia.mp3', RAIZ + '/public/championships/halloween/assets/melodia.mp3', 'assets/'),
       ('power_mano.webp', RAIZ + '/public/championships/halloween/assets/power_mano.webp', 'assets/'),
       ('power_calabaza.webp', RAIZ + '/public/championships/halloween/assets/power_calabaza.webp', 'assets/')]
for nombre, fich, sub in MOD:
    try:
        st, data = get(BASE + 'championships/halloween/' + sub + nombre.split(' ')[0] + '?v=v3687')
        loc = open(fich, 'rb').read()
        CHK(st == 200 and sha(data) == sha(loc), 'módulo byte-idéntico: %s' % nombre)
    except Exception as e:
        CHK(False, 'módulo byte-idéntico: %s (%s)' % (nombre, e))

print('')
print('== PRODUCCIÓN r95: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  ✗', f)
    sys.exit(1)
print('VERDE — 3.6.87-SDK6 viva en producción (tres vías byte-exacto)')
