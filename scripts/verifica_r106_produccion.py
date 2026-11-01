#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r106_produccion.py — tres vías byte-exacto + agujas r106 en el servido.
Hereda el patrón r105. VIEJO = sha del servido 3.6.97 (r105) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '17d76589'          # sha256 del servido 3.6.97 (r105) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r106)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3698')
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
open(RAIZ + '/scripts/_r106_servido_game.html', 'wb').write(servido)
# el deploy aplica 2 reescrituras ruta absoluta→relativa sobre game.html:
# el servido NO es byte-idéntico al local (2 B), pero las TRES VÍAS deben
# cerrar entre sí: PAGES-VERSION == servido == blob de origin/pages.
CHK(sha_local == golden, 'local == golden (%s…) — el servido lleva 2 reescrituras' % sha_local[:8])
s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3698')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.98' in txt, 'PAGES-VERSION anuncia 3.6.98')
except Exception as e:
    CHK(False, 'PAGES-VERSION.txt ilegible (%s)' % e)
CHK(s2 == sha_srv, 'VÍA 1 · servido == PAGES-VERSION.txt (%s…)' % sha_srv[:8])
subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r106_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
CHK(blob is not None and ho == blob, 'VÍA 2 · hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])
print('· TRES VÍAS: servido sha256 %s… = PAGES-VERSION %s… · blob git %s… · local==golden %s…'
      % (sha_srv[:8], (s2 or '?')[:8], (blob or '?')[:8], sha_local[:8]))

TXT = servido.decode('utf-8', 'replace')

# ── agujas r106 (M1 · hápticas calibradas) en el SERVIDO ──
AGUJAS = [
    ('M1 · r106 · HÁPTICA DEL BOTE CALIBRADA',
     'comentario M1 presente (bote calibrado, guard, canto)'),
    ('const s6 = Math.min(1, e.speed / 6);', 's6: velocidad normalizada del bote'),
    ('this.haptic(this.paddleHand, 0.08 + 0.16 * s6, Math.round(50 + 30 * s6));',
     'bote llano: 0,08–0,24 · 50–80 ms por velocidad'),
    ('this.haptic(this.paddleHand, 0.14 + 0.16 * s6, 28);',
     'canto: pico alto (0,14–0,30) y seco (28 ms)'),
    ('this.haptic(this.paddleHand, 0.15, 45);', 'red: vibración sutil 0,15/45 ms'),
]
for a, n in AGUJAS:
    CHK(a in TXT, 'servido: ' + n)

RETIRADAS = [
    ('this.haptic(this.paddleHand, 0.18);', 'háptica fija 0,18 del bote AUSENTE (M1)'),
]
for a, n in RETIRADAS:
    CHK(a not in TXT, 'servido: ' + n)
CHK('3.6.98-SDK6' in TXT, 'servido: sello de versión 3.6.98-SDK6')

# heredadas (r105/r104/r103/r102)
CHK('this.menuTex.generateMipmaps = false;', 'mips OFF' in TXT or False)
CHK('this.menuTex.generateMipmaps = false;' in TXT, 'servido: mips OFF intacto (r105)')
CHK('if ((nowH - (this._menuHoverDrawAt || 0)) >= 90) {' in TXT,
    'servido: throttle de hover 90 ms intacto (r105)')
CHK('dot.position.set((hit.uv.x - 0.5) * 0.90, (hit.uv.y - 0.5) * 1.35, 0.004);' in TXT,
    'servido: cursor en el plano REAL intacto (r105)')
CHK('new THREE.PlaneGeometry(0.90, 1.35),' in TXT, 'servido: panel 0,90×1,35 intacto (r104)')
CHK('const MENU_FS = 1.16;' in TXT, 'servido: fuentes ×1,16 intactas (r104)')
CHK('this.menuGroup.position.y = Math.max(0.85, muHead.y - 0.12);' in TXT,
    'servido: anclaje compensado intacto (r104)')
CHK('function barraStick(dt) {' in TXT, 'servido: joystick de la barra intacto (r102)')
CHK('const BARRA_LBL_X = () => HW() + 0.42;' in TXT, 'servido: rótulo a la DERECHA intacto (r103)')
CHK('PROTO: 2,' in TXT, 'servido: pala rival FIEL intacta (r102)')
# r62 · SFX reales intactos (la otra mitad de M1)
CHK("const nombres = ['mesa', 'pala', 'canto', 'red', 'suelo'];" in TXT,
    'servido: 5 muestras físicas r62 intactas')

# módulo halloween byte-idéntico entre local y servido
for f in ('championships/halloween/index.js', 'championships/halloween/manifest.json'):
    st, srv = get(BASE + f)
    loc = open(RAIZ + '/public/' + f, 'rb').read()
    CHK(sha(srv) == sha(loc), 'módulo %s byte-idéntico local/servido' % f.split('/')[1])

print()
print('VERIFICA r106 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('TRES VÍAS BYTE-EXACTO — V3.6.98-SDK6 EN PRODUCCIÓN (recarga con game.html?v=v3698)')
