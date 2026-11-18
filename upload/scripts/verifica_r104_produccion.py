#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r104_produccion.py — tres vías byte-exacto + agujas r104 en el servido.
Hereda el patrón r103. VIEJO = sha del servido 3.6.95 (r103) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = 'a868a17d'          # sha256 del servido 3.6.95 (r103) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r104)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3696')
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

sha_srv = sha(servido)
open(RAIZ + '/scripts/_r104_servido_game.html', 'wb').write(servido)
# el deploy aplica 2 reescrituras ruta absoluta→relativa sobre game.html:
# el servido NO es byte-idéntico al local (2 B), pero las TRES VÍAS deben
# cerrar entre sí: PAGES-VERSION == servido == blob de origin/pages.
CHK(sha_local == golden, 'local == golden (%s…) — el servido lleva 2 reescrituras' % sha_local[:8])
s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3696')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.96' in txt, 'PAGES-VERSION anuncia 3.6.96')
except Exception as e:
    CHK(False, 'PAGES-VERSION.txt ilegible (%s)' % e)
CHK(s2 == sha_srv, 'VÍA 1 · servido == PAGES-VERSION.txt (%s…)' % sha_srv[:8])
subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r104_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
CHK(blob is not None and ho == blob, 'VÍA 2 · hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])
print('· TRES VÍAS: servido sha256 %s… = PAGES-VERSION %s… · blob git %s… · local==golden %s…'
      % (sha_srv[:8], (s2 or '?')[:8], (blob or '?')[:8], sha_local[:8]))

TXT = servido.decode('utf-8', 'replace')

# ── agujas r104 en el SERVIDO ──
AGUJAS = [
    ('new THREE.PlaneGeometry(0.90, 1.35),', 'panel del menú 0,90×1,35 m (pantalla completa)'),
    ('this.menuTex.anisotropy = 8;', 'anisotropía 8'),
    ('const MENU_FS = 1.16;', 'fuentes del menú ×1,16'),
    ("const label = (txt, y, size = 28, col = '#c9d3dd', align = 'left') => {",
     'label 28 px gris luminoso'),
    ('const bs = 14, bx = x + 26, by = y + h / 2;', 'casillas ☑ mayores'),
    ("this._langPaddle(rects, 'es', 728, 40);", 'palas de idioma reencajadas'),
    ("heat_t: 'MAPA DE CALOR',", 'mapa de calor traducido (adiós claves en crudo)'),
    ('while (hint104.length > 2 && c.measureText(hint104).width > 700) hint104 = hint104.slice(0, -1);',
     'hint de campeonatos con elipsis'),
    ('while (sub104.length > 2 && c.measureText(sub104).width > 500) sub104 = sub104.slice(0, -1);',
     'subtítulo PRO TRAINING recortado'),
    ('const nmT104 = nm104.length > 16 ? nm104.slice(0, 15) + \'…\' : nm104;',
     'lista del PULSO sin desbordes'),
    ('this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);', 'anclaje compensado'),
]
for a, n in AGUJAS:
    CHK(a in TXT, 'servido: ' + n)

RETIRADAS = [
    ('new THREE.PlaneGeometry(0.72, 1.08),', 'panel pequeño retirado'),
    ('const MENU_FS', None),   # se comprueba distinto abajo
]
CHK('new THREE.PlaneGeometry(0.72, 1.08),' not in TXT, 'servido: panel 0,72×1,08 ausente')
CHK('3.6.96-SDK6' in TXT, 'servido: sello de versión 3.6.96-SDK6')

# heredadas (r101/r102/r103)
CHK('function barraStick(dt) {' in TXT, 'servido: joystick de la barra intacto (r102)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in TXT, 'servido: rótulo a la DERECHA intacto (r103)')
CHK('PROTO: 2,' in TXT, 'servido: pala rival FIEL intacta (r102)')

# módulo halloween byte-idéntico entre local y servido
for f in ('championships/halloween/index.js', 'championships/halloween/manifest.json'):
    st, srv = get(BASE + f)
    loc = open(RAIZ + '/public/' + f, 'rb').read()
    CHK(sha(srv) == sha(loc), 'módulo %s byte-idéntico local/servido' % f.split('/')[1])

print()
print('VERIFICA r104 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('TRES VÍAS BYTE-EXACTO — V3.6.96-SDK6 EN PRODUCCIÓN (recarga con game.html?v=v3696)')
