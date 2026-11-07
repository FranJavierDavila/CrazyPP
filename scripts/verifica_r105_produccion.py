#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r105_produccion.py — tres vías byte-exacto + agujas r105 en el servido.
Hereda el patrón r104. VIEJO = sha del servido 3.6.96 (r104) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = 'f35e1d35'          # sha256 del servido 3.6.96 (r104) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r105)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3697')
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
open(RAIZ + '/scripts/_r105_servido_game.html', 'wb').write(servido)
# el deploy aplica 2 reescrituras ruta absoluta→relativa sobre game.html:
# el servido NO es byte-idéntico al local (2 B), pero las TRES VÍAS deben
# cerrar entre sí: PAGES-VERSION == servido == blob de origin/pages.
CHK(sha_local == golden, 'local == golden (%s…) — el servido lleva 2 reescrituras' % sha_local[:8])
s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3697')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.97' in txt, 'PAGES-VERSION anuncia 3.6.97')
except Exception as e:
    CHK(False, 'PAGES-VERSION.txt ilegible (%s)' % e)
CHK(s2 == sha_srv, 'VÍA 1 · servido == PAGES-VERSION.txt (%s…)' % sha_srv[:8])
subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r105_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
CHK(blob is not None and ho == blob, 'VÍA 2 · hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])
print('· TRES VÍAS: servido sha256 %s… = PAGES-VERSION %s… · blob git %s… · local==golden %s…'
      % (sha_srv[:8], (s2 or '?')[:8], (blob or '?')[:8], sha_local[:8]))

TXT = servido.decode('utf-8', 'replace')

# ── agujas r105 en el SERVIDO ──
AGUJAS = [
    ('dot.position.set((hit.uv.x - 0.5) * 0.90, (hit.uv.y - 0.5) * 1.35, 0.004);',
     'cursor del menú en el plano REAL 0,90×1,35 (FIX deriva)'),
    ('this.menuTex.generateMipmaps = false;', 'menuTex: mips OFF'),
    ('this.menuTex.minFilter = THREE.LinearFilter;', 'menuTex: minFilter Linear'),
    ('this.menuTex.anisotropy = 1;   // sin mips el anisotrópico no aplica (era 8)',
     'menuTex: anisotropía 1'),
    ('if ((nowH - (this._menuHoverDrawAt || 0)) >= 90) {',
     'repintado por HOVER throttled a 90 ms'),
    ('this._menuDrawPend = false;   // r105 · cualquier repintado real atiende el hover pendiente',
     'drawMenu atiende el hover pendiente'),
    ('this._menuHoverDrawAt = 0;      // r105 · última hora de repintado por hover',
     'estado del throttle en el constructor'),
]
for a, n in AGUJAS:
    CHK(a in TXT, 'servido: ' + n)

RETIRADAS = [
    ('(hit.uv.x - 0.5) * 0.72, (hit.uv.y - 0.5) * 1.08', 'cursor en plano antiguo 0,72×1,08 ausente'),
]
for a, n in RETIRADAS:
    CHK(a not in TXT, 'servido: ' + n)
CHK('3.6.97-SDK6' in TXT, 'servido: sello de versión 3.6.97-SDK6')

# heredadas (r104/r103/r102)
CHK('new THREE.PlaneGeometry(0.90, 1.35),' in TXT, 'servido: panel 0,90×1,35 intacto (r104)')
CHK('const MENU_FS = 1.16;' in TXT, 'servido: fuentes ×1,16 intactas (r104)')
CHK('this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);', 'anclaje compensado intacto (r104)') if False else None
CHK('this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);' in TXT,
    'servido: anclaje compensado intacto (r104)')
CHK('function barraStick(dt) {' in TXT, 'servido: joystick de la barra intacto (r102)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in TXT, 'servido: rótulo a la DERECHA intacto (r103)')
CHK('PROTO: 2,' in TXT, 'servido: pala rival FIEL intacta (r102)')

# módulo halloween byte-idéntico entre local y servido
for f in ('championships/halloween/index.js', 'championships/halloween/manifest.json'):
    st, srv = get(BASE + f)
    loc = open(RAIZ + '/public/' + f, 'rb').read()
    CHK(sha(srv) == sha(loc), 'módulo %s byte-idéntico local/servido' % f.split('/')[1])

print()
print('VERIFICA r105 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('TRES VÍAS BYTE-EXACTO — V3.6.97-SDK6 EN PRODUCCIÓN (recarga con game.html?v=v3697)')
