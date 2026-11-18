#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r109_produccion.py — tres vías byte-exacto + agujas r109 (M3 PWA)
en el servido. Hereda el patrón r106. VIEJO = sha del servido 3.6.98 (r106)
— debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request, json

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '414f27dc'          # sha256 del servido 3.6.98 (r106) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r109)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3699')
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
open(RAIZ + '/scripts/_r109_servido_game.html', 'wb').write(servido)
# el deploy aplica 2 reescrituras ruta absoluta→relativa sobre game.html:
# las TRES VÍAS deben cerrar entre sí: PAGES-VERSION == servido == blob origin/pages.
CHK(sha_local == golden, 'local == golden (%s…) — el servido lleva 2 reescrituras' % sha_local[:8])
s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3699')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.99' in txt, 'PAGES-VERSION anuncia 3.6.99')
except Exception as e:
    CHK(False, 'PAGES-VERSION.txt ilegible (%s)' % e)
CHK(s2 == sha_srv, 'VÍA 1 · servido == PAGES-VERSION.txt (%s…)' % sha_srv[:8])
subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r109_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
CHK(blob is not None and ho == blob, 'VÍA 2 · hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])
print('· TRES VÍAS: servido sha256 %s… = PAGES-VERSION %s… · blob git %s… · local==golden %s…'
      % (sha_srv[:8], (s2 or '?')[:8], (blob or '?')[:8], sha_local[:8]))

TXT = servido.decode('utf-8', 'replace')

# ── agujas r109 (M3 · PWA INSTALABLE) en el SERVIDO ──
AGUJAS = [
    ('r109 · M3 PWA INSTALABLE', 'comentario del hito presente (c13)'),
    ("navigator.serviceWorker.register('sw.js', { scope: './' })",
     'registro del service worker en contexto seguro'),
    ("window.matchMedia('(display-mode: fullscreen)').matches",
     'detección de standalone'),
    ("window.addEventListener('beforeinstallprompt'", 'beforeinstallprompt capturado'),
    ('pwa_standalone', 'telemetría pwa_standalone'),
    ('pwa_manual_hint', 'telemetría pwa_manual_hint'),
    ('ov_pwa', 'i18n: clave ov_pwa presente'),
    ('id="pwabtn"', 'portada: botón instalar presente'),
    ('<link rel="manifest" href="manifest.webmanifest" />', 'head: link rel=manifest'),
    ('#ppToast {', 'CSS del toast presente'),
]
for a, n in AGUJAS:
    CHK(a in TXT, 'servido: ' + n)
CHK('3.6.99-SDK6' in TXT, 'servido: sello de versión 3.6.99-SDK6')

# ── los FICHEROS PWA en producción ──
st, man = get(BASE + 'manifest.webmanifest')
CHK(st == 200, 'producción: manifest.webmanifest HTTP 200')
try:
    mjson = json.loads(man.decode('utf-8'))
    CHK(mjson.get('start_url') == './game.html' and mjson.get('display') == 'fullscreen',
        'producción: manifest válido (start_url ./game.html · fullscreen)')
except Exception as e:
    CHK(False, 'producción: manifest ilegible (%s)' % e)

st, sw = get(BASE + 'sw.js')
CHK(st == 200, 'producción: sw.js HTTP 200')
CHK(b"const CACHE = 'crazypp-v3.6.99-SDK6';" in sw,
    'producción: sw.js lleva const CACHE = crazypp-v3.6.99-SDK6 (bump gobierna la caché)')

loc_icons = {'logo-192.png': RAIZ + '/public/logo-192.png',
             'logo-512.png': RAIZ + '/public/logo-512.png',
             'logo-maskable-512.png': RAIZ + '/public/logo-maskable-512.png'}
for nombre, ruta in loc_icons.items():
    st, srv = get(BASE + nombre)
    CHK(st == 200 and sha(srv) == sha(open(ruta, 'rb').read()),
        f'producción: {nombre} byte-idéntico ({st})')

# heredadas (r106/r105/r104/r102/r62)
CHK('const s6 = Math.min(1, e.speed / 6);' in TXT, 'servido: háptica del bote calibrada intacta (r106)')
CHK('this.haptic(this.paddleHand, 0.14 + 0.16 * s6, 28);' in TXT, 'servido: canto distinguible intacto (r106)')
CHK('this.menuTex.generateMipmaps = false;' in TXT, 'servido: mips OFF intacto (r105)')
CHK('const MENU_FS = 1.16;' in TXT, 'servido: fuentes ×1,16 intactas (r104)')
CHK('PROTO: 2,' in TXT, 'servido: pala rival FIEL intacta (r102)')
CHK("const nombres = ['mesa', 'pala', 'canto', 'red', 'suelo'];" in TXT,
    'servido: 5 muestras físicas r62 intactas')

# módulo halloween byte-idéntico entre local y servido (regresión de deploy)
for f in ('championships/halloween/index.js', 'championships/halloween/manifest.json'):
    st, srv = get(BASE + f)
    loc = open(RAIZ + '/public/' + f, 'rb').read()
    CHK(sha(srv) == sha(loc), 'módulo %s byte-idéntico local/servido' % f.split('/')[1])

print()
print('VERIFICA r109 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  -', f)
    sys.exit(1)
print('TRES VÍAS BYTE-EXACTO — V3.6.99-SDK6 EN PRODUCCIÓN · PWA INSTALABLE (recarga con game.html?v=v3699)')
