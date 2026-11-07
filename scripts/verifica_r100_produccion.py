#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r100_produccion.py — tres vías byte-exacto + agujas r100 en el servido.
Hereda el patrón r99. VIEJO = sha del servido 3.6.91 (r99) — debe desaparecer."""
import subprocess, time, sys, hashlib, urllib.request

BASE = 'https://franjavierdavila.github.io/CrazyPP/'
RAIZ = '/home/z/my-project'
VIEJO = 'a80e2a8f'          # sha256 del servido 3.6.91 (r99) — debe desaparecer

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
        st, servido = get(BASE + 'game.html?v=v3692')
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
open(RAIZ + '/scripts/_r100_servido_game.html', 'wb').write(servido)

s2 = None
try:
    st, pv = get(BASE + 'PAGES-VERSION.txt?v=v3692')
    txt = pv.decode('utf-8', 'replace')
    line = [l for l in txt.splitlines() if 'game_sha256' in l]
    s2 = line[0].split('=')[-1].strip() if line else None
    CHK('3.6.92' in txt, 'vía 2: PAGES-VERSION anuncia 3.6.92')
except Exception as e:
    CHK(False, 'vía 2: PAGES-VERSION.txt ilegible (%s)' % e)

subprocess.run(['git', 'fetch', 'origin', 'pages'], cwd=RAIZ, capture_output=True)
ls = subprocess.run(['git', 'ls-tree', 'origin/pages', 'game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
blob = ls.split()[2] if ls else None
ho = subprocess.run(['git', 'hash-object', RAIZ + '/scripts/_r100_servido_game.html'],
                    cwd=RAIZ, capture_output=True, text=True).stdout.strip()
print('servido sha256 = %s… · PAGES-VERSION = %s… · blob = %s… · hash-object servido = %s…'
      % (s1[:12], (s2 or '?')[:12], (blob or '?')[:12], ho[:12]))

CHK(s2 == s1, 'vía 1 == vía 2: servido == PAGES-VERSION (%s…)' % s1[:8])
CHK(blob is not None and ho == blob, 'vía 3: hash-object del servido == blob origin/pages (%s…)' % (blob or '?')[:8])

gh = servido.decode('utf-8', 'replace')
# sellos
CHK("const VERSION = '3.6.92-SDK6'" in gh, 'aguja servido: sello 3.6.92-SDK6')
CHK('>V3.6.92-SDK6<' in gh, 'aguja servido: badge V3.6.92-SDK6')
# r100 · barra interactiva del pase bajo
CHK('r100 · BARRA INTERACTIVA DEL PASE BAJO' in gh,
    'aguja servido: cabecera del ajuste (r100)')
CHK('const RIBBON_Y = () => DIMS.netTopY + barraH;         // cinta AJUSTABLE (r100)' in gh,
    'aguja servido: cinta con altura VIVA (r100)')
CHK('const RIBBON_Y = () => DIMS.netTopY + 0.17;' not in gh,
    'aguja servido: la cinta fija a 17 cm está RETIRADA (r100)')
CHK("localStorage.setItem('pp_train_barra_v1', JSON.stringify({ h: Math.round(barraH * 1000) / 1000 }))" in gh,
    'aguja servido: persistencia de la barra (r100)')
CHK('const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);' in gh,
    'aguja servido: lectura en cm sobre la SUPERFICIE (r100)')
CHK('function barraChevronTex(dir) {' in gh and 'function barraLabelTex() {' in gh,
    'aguja servido: flechas ↑/↓ + rótulo de cm (r100)')
CHK('function barraTick(dt) {' in gh and 'function barraAjustarHover() {' in gh,
    'aguja servido: rayo de la mano libre + ajuste ±1 cm (r100)')
CHK('if (barraAjustarHover()) return;' in gh,
    'aguja servido: el gatillo sobre una flecha SE CONSUME (r100)')
CHK('const BARRA_MIN = 0.05, BARRA_MAX = 0.40;' in gh,
    'aguja servido: clamps 5..40 cm (r100)')
CHK('function barraHazEnsure() {' in gh,
    'aguja servido: haz de selección de la mano libre (r100)')
# r100 · aro al centro
CHK('g.position.set(0, APEX_Y, C());' in gh and 'C() + 0.5' not in gh,
    'aguja servido: aro del globo al CENTRO de la mesa (r100)')
# r100 · primer saque fiel
CHK('r100 · LANZAMIENTO FIEL AL GESTO' in gh,
    'aguja servido: cabecera del fix del flick (r100)')
CHK('if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);' in gh,
    'aguja servido: velInst manda al soltar (r100)')
CHK('if (bh.velInst && bh.velInst.lengthSq() > v.lengthSq()) v.copy(bh.velInst);' in gh,
    'aguja servido: el tee del Pro Training igual (r100)')
# r100 · contacto de reposo + transporte
CHK('r100 · CONTACTO DE REPOSO pala-bola (el estándar Eleven).' in gh,
    'aguja servido: contacto de reposo (r100)')
CHK('paddleRestSpeed: 0.65,' in gh and 'paddleRestSpeedPad: 0.95,' in gh,
    'aguja servido: umbrales dual del apoyo (r100)')
CHK('paddleRestFric: 0.38,' in gh and 'paddleRestMuS: 0.35,' in gh and 'paddleRestCarry: 0.5,' in gh,
    'aguja servido: fricción + fricción estática + arrastre (r100)')
CHK('r100 · TRANSPORTE DEL APOYO' in gh,
    'aguja servido: transporte de la bola apoyada (r100)')
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

print('\n== PRODUCCIÓN r100: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('   -', f)
    sys.exit(1)
print('VERDE — 3.6.92-SDK6 viva en producción (tres vías byte-exacto)')
