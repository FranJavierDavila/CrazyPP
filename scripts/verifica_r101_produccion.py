#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r101_produccion.py — tres vías byte-exacto + agujas r101 en el servido.
Hereda el patrón r100. VIEJO = sha del servido 3.6.92 (r100) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = '7e7f74f0'          # sha256 del servido 3.6.92 (r100) — debe desaparecer

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
CHK(golden == sha_local, f'local == golden {sha_local[:8]}… (r99 heredada)')

print('— esperando la build de Pages (el servido debe dejar de ser %s…) —' % VIEJO)
servido = None
deadline = time.time() + 480
while time.time() < deadline:
    try:
        st, servido = get(BASE + 'game.html?v=v3693')
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
open(RAIZ + '/scripts/_r101_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3693')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.93' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.93')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r101_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
# sellos
CHK("const VERSION = '3.6.93-SDK6'" in gh, 'aguja servido: sello 3.6.93-SDK6')
CHK('>V3.6.93-SDK6<' in gh, 'aguja servido: badge V3.6.93-SDK6')
# r101 · barra por PROXIMIDAD (sin gatillo, sin rayo)
CHK('r101 · BARRA INTERACTIVA DEL PASE BAJO — AJUSTE POR PROXIMIDAD.' in gh,
    'aguja servido: cabecera del ajuste por proximidad (r101)')
CHK('const RIBBON_Y = () => DIMS.netTopY + barraH;         // cinta AJUSTABLE' in gh,
    'aguja servido: cinta con altura VIVA (r101)')
CHK('const RIBBON_Y = () => DIMS.netTopY + 0.17;' not in gh,
    'aguja servido: la cinta fija a 17 cm sigue RETIRADA')
CHK("localStorage.setItem('pp_train_barra_v1', JSON.stringify({ h: Math.round(barraH * 1000) / 1000 }))" in gh,
    'aguja servido: persistencia de la barra (r101)')
CHK('const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);' in gh,
    'aguja servido: lectura en cm sobre la SUPERFICIE (r101)')
CHK('function barraUpdate(px, py, pz, dt) {' in gh and 'function barraSoltar() {' in gh,
    'aguja servido: máquina de ajuste por proximidad (r101)')
CHK('const BARRA_DWELL = 0.30;' in gh and 'const BARRA_PASO = 0.01;' in gh,
    'aguja servido: dwell 0,30 s + pasos de 1 cm (r101)')
CHK('function pistaBarra() {' in gh and 'function barraFijar(hRaw, salto) {' in gh,
    'aguja servido: rótulo con pista por estado (r101)')
CHK('if (barraAjustarHover()) return;' not in gh,
    'aguja servido: el gatillo CONSUMIDO por las flechas RETIRADO (r101)')
CHK('function barraHazEnsure() {' not in gh,
    'aguja servido: haz de selección por rayo RETIRADO (r101)')
# r101 · aro al centro (heredado r100-B) + gatillo libre + saque V3.6.91
CHK('g.position.set(0, APEX_Y, C());' in gh and 'C() + 0.5' not in gh,
    'aguja servido: aro del globo al CENTRO de la mesa (r100-B intacto)')
CHK("serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } }," in gh,
    'aguja servido: serveTrigger EXACTO de V3.6.91 — gatillo SIEMPRE lanza (r101)')
CHK('if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);' not in gh,
    'aguja servido: velInst del saque RETIRADO (r101)')
CHK('if (bh.velInst && bh.velInst.lengthSq() > v.lengthSq()) v.copy(bh.velInst);' not in gh,
    'aguja servido: velInst del tee RETIRADO (r101)')
# r101 · contacto de reposo con umbral único + transporte
CHK('r100/r101 · CONTACTO DE REPOSO pala-bola (el estándar Eleven).' in gh,
    'aguja servido: contacto de reposo r101 (umbral único)')
CHK('paddleRestSpeed: 0.25,' in gh and 'paddleRestSpeedPad' not in gh,
    'aguja servido: umbral ÚNICO 0,25 (dual 0,95/0,65 RETIRADO) (r101)')
CHK('paddleRestFric: 0.38,' in gh and 'paddleRestMuS: 0.35,' in gh and 'paddleRestCarry: 0.5,' in gh,
    'aguja servido: fricción + fricción estática + arrastre (r101)')
CHK('-vRelN <= DIMS.paddleRestSpeed) {' in gh,
    'aguja servido: condición de reposo con umbral único (r101)')
CHK('r100 · TRANSPORTE DEL APOYO' in gh,
    'aguja servido: transporte de la bola apoyada (r100 intacto)')
CHK("case 'restTouch':" in gh,
    'aguja servido: «toc» suave del apoyo (r100)')
CHK('r100 · un GOLPE rompe cualquier apoyo previo' in gh,
    'aguja servido: el golpe limpia el apoyo (r100)')
# r99 heredada e intacta
CHK("c.fillText(Math.round(vol * 100) + '%', 512, vy + 2);" in gh,
    'aguja servido: % ENCIMA de la barra (r99 heredada)')
CHK('this._mesaLabel.rotation.x = -Math.PI / 2;   // decal plano sobre la mesa' in gh,
    'aguja servido: rótulo TUMBADO sobre la superficie (r99 heredada)')
CHK('new THREE.PlaneGeometry(1.04, 0.26)' in gh,
    'aguja servido: decal 1,04×0,26 (r99 heredada)')
CHK('r99 · el decal vive PEGADO a la superficie' in gh,
    'aguja servido: pegado por frame (r99 heredada)')
# r98 heredada e intacta
CHK('r98 · BOCADILLO DEL DUEÑO' in gh, 'aguja servido: bocadillo blanco (r98 heredada)')
CHK('this._menuDrag = { hand, id: ns };' in gh,
    'aguja servido: arrastre de deslizadores (r98 heredada)')
CHK('_mesaGrabUpdate() {' in gh and '_mesaLabelShow() {' in gh,
    'aguja servido: agarre 1:1 + rótulo vivo (r98 heredada)')
# r97/r95 heredadas
CHK('_salaPreviewUpdate() {' in gh, 'aguja servido: sala EN VIVO (r97 heredada)')
CHK('setMusicVol(v) {' in gh and 'setFxVol(v) {' in gh,
    'aguja servido: canales de volumen (r95 heredada)')
CHK('!ball.ppCalabaza &&' in gh,
    'aguja servido: calabaza JAMÁS recolocada (r97 heredada)')
CHK('const RETOS_POOL' in gh and 'pp_retos_v1' in gh,
    'aguja servido: retos semanales (r97 heredada)')

# la calabaza vive en el MÓDULO (no en game.html): la aguja va al servido del módulo
try:
    stM, modJS = get(BASE + 'championships/halloween/index.js?v=v3692')
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
        st, data = get(BASE + 'championships/halloween/' + sub + nombre + '?v=v3692')
        loc = open(fich, 'rb').read()
        CHK(st == 200 and sha(data) == sha(loc), 'módulo byte-idéntico: %s' % nombre)
    except Exception as e:
        CHK(False, 'módulo %s: ilegible (%s)' % (nombre, e))

print('\n== PRODUCCIÓN r101: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys.exit(1)
print('VERDE — 3.6.93-SDK6 viva en producción (tres vías byte-exacto)')
