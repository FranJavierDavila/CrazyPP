#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r98_produccion.py — tres vías byte-exacto + agujas r98 en el servido.
Hereda el patrón r95. VIEJO = sha del servido 3.6.89 (r97) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '2776e083'          # sha256 del servido 3.6.89 (r97) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r97 heredada)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3690')
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
open(RAIZ + '/scripts/_r98_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3690')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.90' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.90')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r98_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
# r98 · agujas de los seis frentes
CHK("const VERSION = '3.6.90-SDK6'" in gh, 'aguja servido: sello 3.6.90-SDK6')
CHK('>V3.6.90-SDK6<' in gh, 'aguja servido: badge V3.6.90-SDK6')
CHK('_salaPreviewUpdate() {' in gh, 'aguja servido: vista de sala EN VIVO (r97 heredada)')
CHK("'page:optsSalaRoom'" in gh and "'page:optsSalaMesa'" in gh, 'aguja servido: submenús SALA/MESA (r97 heredada)')
CHK('_mesaAplicarY(yNum, opts) {' in gh, 'aguja servido: deslizador de altura (r97 heredada)')
CHK("_menuTipDraw(c, rects) {" in gh, 'aguja servido: tooltips del menú (r97 heredada)')
CHK("case 'mvolset':" in gh and "case 'fvolset':" in gh, 'aguja servido: barras de volumen CLICABLES (r97 heredada)')
CHK('try { if (g._mesaNativo) g._mesaNativo(); } catch (eMN) { /* */ }' in gh, 'aguja servido: campeonato ARRANCA nativo (r97 heredada)')
CHK('try { if (this.game._mesaSkinReapply) this.game._mesaSkinReapply(); } catch (eMR) { /* */ }' in gh, 'aguja servido: leaveAll reaplica la piel (r97 heredada)')
CHK('const PERF_FFR_MODOS = {' in gh and 'foveaMax() {' in gh, 'aguja servido: NITIDEZ (FFR) con techo (r97 heredada)')
CHK("quest3: { label: 'Quest 3', scale: 1.40, fovea: 0.35, rate: 90 }" in gh, 'aguja servido: Quest 3 nítido 0,35 (r97 heredada)')
# r95/r93 intactas
CHK('setMusicVol(v) {' in gh and 'setFxVol(v) {' in gh, 'aguja servido: canales música/efectos (r95 intacta)')
CHK('_rivStyleCalc() {' in gh, 'aguja servido: estilo del rival (r95 intacta)')
CHK("T('fanf_stats'" in gh, 'aguja servido: chip de estadísticas (r95 intacta)')
CHK('contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)' in gh, 'aguja servido: c06 swing tangente (r93 intacta)')
CHK('const rise0 = sw.flat ? 0 : 0.05;' in gh, 'aguja servido: c12 rise0/flat (r93 intacta)')
# r98 · agujas de la ronda
# la calabaza vive en el MÓDULO (no en game.html): la aguja va al servido del módulo
try:
    stM, modJS = get(BASE + 'championships/halloween/index.js?v=v3690')
    ghM = modJS.decode('utf-8', 'replace')
    CHK(stM == 200 and 'if (game.ballMesh && game.ballMesh.parent) game.ballMesh.parent.add(C.gltf);' in ghM,
        'aguja módulo servido: calabaza HIJA del padre de la bola (r97 heredada)')
    CHK('ZONB[k].b.off(true);' in ghM, 'aguja módulo servido: leave() corta el tren del zombi (r97 heredada)')
except Exception as e:
    CHK(False, 'aguja módulo servido: ilegible (%s)' % e)
CHK('!ball.ppCalabaza &&' in gh, 'aguja servido: c06 bola calabaza JAMÁS recolocada (r97 heredada)')
CHK('const dcx = ball.pos.x - this.pos.x,' in gh, 'aguja servido: c06 tangente a la bola RENDERIZADA (r97 heredada)')
CHK('typeof m.musicOff === \'function\') m.musicOff()' in gh, 'aguja servido: candado universal musicOff (r97 heredada)')
CHK('__ppCoreVoz' in gh, 'aguja servido: voz del manifest al motor del núcleo (r97 heredada)')
CHK('window.__PP_CHAMP_PERS' in gh and 'f0 * PM' in gh, 'aguja servido: síntesis teñida por personalidad (r97 heredada)')
CHK('_heatClasifica(p) {' in gh and 'pp_heat_v1' in gh, 'aguja servido: mapa de calor (r97 heredada)')
CHK('const RETOS_POOL' in gh and 'pp_retos_v1' in gh, 'aguja servido: retos semanales (r97 heredada)')
CHK("key: 'nocturna'" in gh and "lock: 'stars4'" in gh, 'aguja servido: tema Nocturna desbloqueable (r97 heredada)')
CHK('game.heatGlobal' in gh, 'aguja servido: tarjeta MAPA DE CALOR en el hub (r97 heredada)')


# r98 · agujas de la ronda (gestos continuos del menú)
CHK('r98 · BOCADILLO DEL DUEÑO' in gh, 'aguja servido: bocadillo blanco del dueño (r98)')
CHK("c.fillStyle = '#0e1219';" in gh, 'aguja servido: texto NEGRO del bocadillo (r98)')
CHK('COLA del bocadillo' in gh, 'aguja servido: cola precisa del bocadillo (r98)')
CHK('this._menuDrag = { hand, id: ns };' in gh, 'aguja servido: arrastre de deslizadores armado al pulsar (r98)')
CHK('_menuDragUpdate() {' in gh, 'aguja servido: arrastre actualizado por frame (r98)')
CHK("targetRay.addEventListener('selectend', () => this.onSelectEnd(i));" in gh, 'aguja servido: selectend por mando (r98)')
CHK('_mesaGrabActivo()' in gh and '_mesaRay(origin, dir) {' in gh, 'aguja servido: rayo de selección sobre la mesa (r98)')
CHK('_mesaGrabUpdate() {' in gh and '_mesaLabelShow() {' in gh, 'aguja servido: agarre 1:1 + rótulo grande (r98)')
CHK('this._mesaLabel.position.set(0, DIMS.tableTopY + 0.52, 0.92);' in gh, 'aguja servido: rótulo sobre el lado del dueño (r98)')
CHK("id: 'mesa_altoy'" not in gh, 'aguja servido: el raíl del deslizador está RETIRADO (r98)')
CHK("label(T('mesa_alto_grab')" in gh, 'aguja servido: la página MESA explica el gesto (r98)')
CHK("hint_mesa_altoy: 'Apunta a la mesa, mantén el gatillo" in gh, 'aguja servido: i18n ES del gesto (r98)')
CHK("hint_mesa_altoy: 'Point at the table, hold the trigger" in gh, 'aguja servido: i18n EN del gesto (r98)')

MOD = [('index.js', RAIZ + '/public/championships/halloween/index.js', ''),
       ('manifest.json', RAIZ + '/public/championships/halloween/manifest.json', ''),
       ('melodia.mp3', RAIZ + '/public/championships/halloween/assets/melodia.mp3', 'assets/'),
       ('power_mano.webp', RAIZ + '/public/championships/halloween/assets/power_mano.webp', 'assets/'),
       ('power_calabaza.webp', RAIZ + '/public/championships/halloween/assets/power_calabaza.webp', 'assets/')]
for nombre, fich, sub in MOD:
    try:
        st, data = get(BASE + 'championships/halloween/' + sub + nombre + '?v=v3690')
        loc = open(fich, 'rb').read()
        CHK(st == 200 and sha(data) == sha(loc), 'módulo byte-idéntico: %s' % nombre)
    except Exception as e:
        CHK(False, 'módulo byte-idéntico: %s (%s)' % (nombre, e))

print('')
print('== PRODUCCIÓN r98: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    for f in FAIL:
        print('  ✗', f)
    sys.exit(1)
print('VERDE — 3.6.90-SDK6 viva en producción (tres vías byte-exacto)')
