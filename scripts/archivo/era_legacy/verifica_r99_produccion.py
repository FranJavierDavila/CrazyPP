#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r99_produccion.py — tres vías byte-exacto + agujas r99 en el servido.
Hereda el patrón r98. VIEJO = sha del servido 3.6.90 (r98) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '682e36d8'          # sha256 del servido 3.6.90 (r98) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r98 heredada)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3691')
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
open(RAIZ + '/scripts/_r99_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3691')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.91' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.91')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r99_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
# sellos
CHK("const VERSION = '3.6.91-SDK6'" in gh, 'aguja servido: sello 3.6.91-SDK6')
CHK('>V3.6.91-SDK6<' in gh, 'aguja servido: badge V3.6.91-SDK6')
# r99 · agujas de la ronda
CHK("c.fillText(Math.round(vol * 100) + '%', 512, vy + 2);" in gh,
    'aguja servido: % ENCIMA de la barra (vy+2 — r99)')
CHK("c.fillText(Math.round(vol * 100) + '%', 512, vy + 27);" not in gh,
    'aguja servido: el % DENTRO de la barra está RETIRADO (r99)')
CHK('this._mesaLabel.rotation.x = -Math.PI / 2;   // decal plano sobre la mesa' in gh,
    'aguja servido: rótulo TUMBADO paralelo a la superficie (r99)')
CHK('new THREE.PlaneGeometry(1.04, 0.26)' in gh,
    'aguja servido: decal 1,04×0,26 — algo más pequeño (r99)')
CHK("c2.font = '800 96px system-ui, sans-serif';" in gh,
    'aguja servido: texto 96 px (r99)')
CHK('DIMS.tableCenterZ + DIMS.tableHalfLength - 0.34' in gh,
    'aguja servido: decal sobre el lado del dueño, 34 cm hacia la red (r99)')
CHK('DIMS.tableTopY + 0.006' in gh,
    'aguja servido: decal a 6 mm de la superficie (r99)')
CHK('r99 · el decal vive PEGADO a la superficie' in gh,
    'aguja servido: seguimiento POR FRAME durante el agarre (r99)')
CHK('DIMS.tableTopY + 0.52, 0.92' not in gh,
    'aguja servido: la posición flotante antigua está RETIRADA (r99)')
CHK('PlaneGeometry(1.12, 0.28)' not in gh,
    'aguja servido: el plano antiguo 1,12×0,28 está RETIRADO (r99)')
# r98 heredada e intacta
CHK('r98 · BOCADILLO DEL DUEÑO' in gh, 'aguja servido: bocadillo blanco del dueño (r98 heredada)')
CHK("c.fillStyle = '#0e1219';" in gh, 'aguja servido: texto NEGRO del bocadillo (r98 heredada)')
CHK('COLA del bocadillo' in gh, 'aguja servido: cola precisa del bocadillo (r98 heredada)')
CHK('this._menuDrag = { hand, id: ns };' in gh, 'aguja servido: arrastre de deslizadores (r98 heredada)')
CHK('_menuDragUpdate() {' in gh, 'aguja servido: arrastre actualizado por frame (r98 heredada)')
CHK("targetRay.addEventListener('selectend', () => this.onSelectEnd(i));" in gh,
    'aguja servido: selectend por mando (r98 heredada)')
CHK('_mesaGrabActivo()' in gh and '_mesaRay(origin, dir) {' in gh,
    'aguja servido: rayo de selección sobre la mesa (r98 heredada)')
CHK('_mesaGrabUpdate() {' in gh and '_mesaLabelShow() {' in gh,
    'aguja servido: agarre 1:1 + rótulo vivo (r98 heredada)')
CHK("id: 'mesa_altoy'" not in gh, 'aguja servido: el raíl del deslizador sigue RETIRADO (r98 heredada)')
CHK("label(T('mesa_alto_grab')" in gh, 'aguja servido: la página MESA explica el gesto (r98 heredada)')
CHK("hint_mesa_altoy: 'Apunta a la mesa, mantén el gatillo" in gh, 'aguja servido: i18n ES del gesto (r98 heredada)')
CHK("hint_mesa_altoy: 'Point at the table, hold the trigger" in gh, 'aguja servido: i18n EN del gesto (r98 heredada)')
# r97 heredada
CHK('_salaPreviewUpdate() {' in gh, 'aguja servido: vista de sala EN VIVO (r97 heredada)')
CHK("'page:optsSalaRoom'" in gh and "'page:optsSalaMesa'" in gh, 'aguja servido: submenús SALA/MESA (r97 heredada)')
CHK('_mesaAplicarY(yNum, opts) {' in gh, 'aguja servido: altura continua (r97 heredada)')
CHK("_menuTipDraw(c, rects) {" in gh, 'aguja servido: tooltips del menú (r97 heredada)')
CHK('const PERF_FFR_MODOS = {' in gh and 'foveaMax() {' in gh, 'aguja servido: NITIDEZ (FFR) con techo (r97 heredada)')
CHK('setMusicVol(v) {' in gh and 'setFxVol(v) {' in gh, 'aguja servido: canales música/efectos (r95 heredada)')
CHK('_rivStyleCalc() {' in gh, 'aguja servido: estilo del rival (r95 heredada)')
CHK('contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)' in gh, 'aguja servido: c06 swing tangente (r93 heredada)')
CHK('!ball.ppCalabaza &&' in gh, 'aguja servido: c06 bola calabaza JAMÁS recolocada (r97 heredada)')
CHK('typeof m.musicOff === \'function\') m.musicOff()' in gh, 'aguja servido: candado universal musicOff (r97 heredada)')
CHK('__ppCoreVoz' in gh, 'aguja servido: voz del manifest al motor del núcleo (r97 heredada)')
CHK('window.__PP_CHAMP_PERS' in gh and 'f0 * PM' in gh, 'aguja servido: síntesis teñida por personalidad (r97 heredada)')
CHK('_heatClasifica(p) {' in gh and 'pp_heat_v1' in gh, 'aguja servido: mapa de calor (r97 heredada)')
CHK('const RETOS_POOL' in gh and 'pp_retos_v1' in gh, 'aguja servido: retos semanales (r97 heredada)')
CHK("key: 'nocturna'" in gh and "lock: 'stars4'" in gh, 'aguja servido: tema Nocturna desbloqueable (r97 heredada)')
CHK('game.heatGlobal' in gh, 'aguja servido: tarjeta MAPA DE CALOR en el hub (r97 heredada)')

# la calabaza vive en el MÓDULO (no en game.html): la aguja va al servido del módulo
try:
    stM, modJS = get(BASE + 'championships/halloween/index.js?v=v3691')
    ghM = modJS.decode('utf-8', 'replace')
    CHK(stM == 200 and 'if (game.ballMesh && game.ballMesh.parent) game.ballMesh.parent.add(C.gltf);' in ghM,
        'aguja módulo servido: calabaza HIJA del padre de la bola (r97 heredada)')
    CHK('ZONB[k].b.off(true);' in ghM, 'aguja módulo servido: leave() corta el tren del zombi (r97 heredada)')
except Exception as e:
    CHK(False, 'aguja módulo servido: ilegible (%s)' % e)

MOD = [('index.js', RAIZ + '/public/championships/halloween/index.js', ''),
       ('manifest.json', RAIZ + '/public/championships/halloween/manifest.json', ''),
       ('melodia.mp3', RAIZ + '/public/championships/halloween/assets/melodia.mp3', 'assets/'),
       ('power_mano.webp', RAIZ + '/public/championships/halloween/assets/power_mano.webp', 'assets/'),
       ('power_calabaza.webp', RAIZ + '/public/championships/halloween/assets/power_calabaza.webp', 'assets/')]
for nombre, fich, sub in MOD:
    try:
        st, data = get(BASE + 'championships/halloween/' + sub + nombre + '?v=v3691')
        loc = open(fich, 'rb').read()
        CHK(st == 200 and sha(data) == sha(loc), 'módulo byte-idéntico: %s' % nombre)
    except Exception as e:
        CHK(False, 'módulo %s: ilegible (%s)' % (nombre, e))

print('\n== PRODUCCIÓN r99: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys.exit(1)
print('VERDE — 3.6.91-SDK6 viva en producción (tres vías byte-exacto)')
