#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r102_produccion.py — tres vías byte-exacto + agujas r102 en el servido.
Hereda el patrón r101. VIEJO = sha del servido 3.6.93 (r101) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '2f9e4095'          # sha256 del servido 3.6.93 (r101) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r102)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3694')
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
open(RAIZ + '/scripts/_r102_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3694')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.94' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.94')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r102_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
# sellos
CHK("const VERSION = '3.6.94-SDK6'" in gh, 'aguja servido: sello 3.6.94-SDK6')
CHK('>V3.6.94-SDK6<' in gh, 'aguja servido: badge V3.6.94-SDK6')
# r102 · la pala del rival FIEL (cuaternión visual + receptor sin montura + PROTO 2)
CHK('qv.copy(grip.quaternion).multiply(mq);' in gh,
    'aguja servido: la mano con pala viaja como VISUAL grip⊗montura (r102)')
CHK('const mq = (g.paddleMounts && g.paddleMounts[i] && g.paddleMounts[i].quaternion)' in gh,
    'aguja servido: montura viva del emisor (mountQuatFor⊗gripOffsetQ) (r102)')
CHK('// aquí NO se multiplica ninguna montura' in gh,
    'aguja servido: el receptor conjuga el visual SIN multiplicar monturas (r102)')
CHK('.applyQuaternion(netTmpQ).add(netTmpP);' in gh,
    'aguja servido: hoja girada por la visual YA conjugada (r102)')
CHK('PROTO: 2,' in gh and 'PROTO: 1,' not in gh,
    'aguja servido: PROTO 2 — parejas mixtas caen a v1 (r102)')
CHK('const qVis = netTmpQ2.copy(netTmpQ)' not in gh,
    'aguja servido: montura multiplicada SIN conjugar RETIRADA (r102)')
CHK('const fisicaIzq = (smp.fl & 8) !== 0;' not in gh,
    'aguja servido: elección de montura por mano RETIRADA (r102)')
# r102 · etiqueta PEGADA AL JUGADOR
CHK('const BARRA_LBL_Z = () => HL() - 0.30;' in gh,
    'aguja servido: rótulo a 30 cm del borde cercano (r102)')
CHK('if (barraLbl) barraLbl.position.set(0, by + 0.13, zl);' in gh,
    'aguja servido: rótulo+flechas viajan con la cinta (r102)')
CHK('if (barraLbl) barraLbl.position.set(0, by + 0.13, 0);' not in gh,
    'aguja servido: rótulo en el CENTRO bajo la red RETIRADO (r102)')
CHK('const cv = mkCanvas(400, 110), x = cv.getContext(\'2d\');' in gh,
    'aguja servido: lienzo 400 px (r102)')
# r102 · barra por JOYSTICK + aviso al jugador
CHK('function barraStick(dt) {' in gh and 'const BARRA_STICK_V = 0.14;' in gh,
    'aguja servido: máquina del JOYSTICK (r102)')
CHK('if (ax && Math.abs(ax.y) > 0.30) y += -ax.y;' in gh,
    'aguja servido: eje Y de CUALQUIER stick, muerta 0,30 (r102)')
CHK('barraStick(dt);                        // r102: joystick, cualquier mando' in gh,
    'aguja servido: barraTick alimenta el stick ANTES del rayo (r102)')
CHK("'JOYSTICK ↑↓ O MANO EN LA CINTA'" in gh,
    'aguja servido: pista del rótulo con los DOS caminos (r102)')
CHK('ajústala con CUALQUIER JOYSTICK ↑↓' in gh,
    'aguja servido: toast informativo al entrar al PASE BAJO (r102)')
# r101 heredada e intacta (proximidad + gatillo libre + saque V3.6.91 + reposo)
CHK('function barraUpdate(px, py, pz, dt) {' in gh and 'function barraSoltar() {' in gh,
    'aguja servido: máquina por proximidad INTACTA (r101)')
CHK('const BARRA_DWELL = 0.30;' in gh and 'const BARRA_PASO = 0.01;' in gh,
    'aguja servido: dwell 0,30 + pasos 1 cm (r101 intacto)')
CHK('if (barraAgarrada) barraSoltar();\n      barraZona = false; barraZonaT = 0;' in gh,
    'aguja servido: el stick MANDA sobre la proximidad (r102 sobre r101)')
CHK("serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } }," in gh,
    'aguja servido: serveTrigger EXACTO de V3.6.91 (r101 intacto)')
CHK('if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);' not in gh,
    'aguja servido: velInst del saque RETIRADO (r101 intacto)')
CHK('paddleRestSpeed: 0.25,' in gh and 'paddleRestSpeedPad' not in gh,
    'aguja servido: reposo umbral ÚNICO 0,25 (r101 intacto)')
CHK('g.position.set(0, APEX_Y, C());' in gh and 'C() + 0.5' not in gh,
    'aguja servido: aro del globo al CENTRO (r100-B intacto)')
# r99/r98/r97/r95 heredadas
CHK("c.fillText(Math.round(vol * 100) + '%', 512, vy + 2);" in gh,
    'aguja servido: % ENCIMA de la barra (r99 heredada)')
CHK('_mesaGrabUpdate() {' in gh and '_mesaLabelShow() {' in gh,
    'aguja servido: agarre 1:1 + rótulo vivo (r98 heredada)')
CHK('this._mesaLabel.position.set(\n      0, DIMS.tableTopY + 0.006,\n      DIMS.tableCenterZ + DIMS.tableHalfLength - 0.34);' in gh,
    'aguja servido: rótulo de MESA pegado al dueño (r99 heredada)')
CHK('_salaPreviewUpdate() {' in gh, 'aguja servido: sala EN VIVO (r97 heredada)')
CHK('setMusicVol(v) {' in gh and 'setFxVol(v) {' in gh,
    'aguja servido: canales de volumen (r95 heredada)')

# la calabaza vive en el MÓDULO (no en game.html): la aguja va al servido del módulo
try:
    stM, modJS = get(BASE + 'championships/halloween/index.js?v=v3694')
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
        st, data = get(BASE + 'championships/halloween/' + sub + nombre + '?v=v3694')
        loc = open(fich, 'rb').read()
        CHK(st == 200 and sha(data) == sha(loc), 'módulo byte-idéntico: %s' % nombre)
    except Exception as e:
        CHK(False, 'módulo %s: ilegible (%s)' % (nombre, e))

print('\n== PRODUCCIÓN r102: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys.exit(1)
print('VERDE — 3.6.94-SDK6 viva en producción (tres vías byte-exacto)')
