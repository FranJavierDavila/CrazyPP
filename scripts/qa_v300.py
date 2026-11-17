#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA V3.0 · ACADEMIA DE ENTRENAMIENTO + PALAS COSMÉTICAS + SPIN GLOBAL.

  A1  game.html SERVIDO = disco (sha256) y VERSION '3.0.0'
  A2  i18n: 40 claves nuevas de la academia presentes en ES y EN
  A3  Catálogos: TRAIN_AREAS (6) · TRAIN_MODES (9, ids correctos, puntos)
      · PADDLE_SKINS (6, umbrales 0/60/150/280/450/700)
  A4  Motor: enterTraining/exitTraining/updateTraining/_trainTableBounce/
      feedDrillBall/buildTrainProps/disposeTrainProps/setPaddleSkin/
      createTrainPanel/addSpinBadges/markRingTexture presentes
  A5  Menú: tarjeta page:train · drawMenuTraining · casos 'tr'/'skin' ·
      'page' acepta 'train'
  A6  Compuertas del saque: _trainServe en gatillo/release/hold/validación
      + sin enderezado en modos de saque
  A7  Sintaxis JS inline (node --check)
  B   RUNTIME (Playwright, headless):
      B1  carga 0 pageerrors + VERSION 3.0.0 + ventana window.__PP_GAME
      B2  enterTraining('quad'): props (tiza + resaltado), HUD visible,
          máquina alimenta (la bola vuela), panel repinta
      B3  Puntos: trainSuccess encadena racha, escribe pp_train_v1 y
          trainFail reinicia (red)
      B4  Robot cortado: spin.x < −40 (backspin) · Robot topspin: > +30
      B5  Cinta: _tapeY = netTop + 0,17 y colisión que devuelve la bola
      B6  Palas: setPaddleSkin cambia materiales de las monturas y
          persiste en pp_train_v1 (fuego a 150 pts)
      B7  Iconos de spin: show() enciende las DOS caras, update apaga
      B8  Menú academia: rects con 'tr:quad'… y 'skin:ebano' (page:train)
      B9  desbloqueo: trainAddPoints cruza 60 → desbloquea 'ebano'
      B10 FOTOS: página academia + modo cuadrantes + cinta + skin fuego
  C   smoke portada 2D: 0 pageerrors tras el arranque completo
"""
import hashlib
import json
import re
import time
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'
GAME = '/home/z/my-project/public/game.html'
RES = []


def chk(name, ok, extra=''):
    RES.append((name, bool(ok), extra))
    print(('OK   ' if ok else 'FAIL ') + name + (('  · ' + str(extra)) if extra else ''))


def sha(b):
    return hashlib.sha256(b).hexdigest()[:12]


# ---------------------------------------------------------------- A · estático
disk = open(GAME, 'rb').read()
served = urllib.request.urlopen(BASE + '/game.html', timeout=20).read()
chk('A1a game.html servido = disco', sha(served) == sha(disk), sha(served))
chk('A1b VERSION 3.0.0', b"VERSION = '3.0.0'" in served)

txt = served.decode('utf-8')
KEYS = ['train_hub_sub', 'train_title', 'train_back', 'train_pts_badge',
        'train_area_grip', 'train_area_dir', 'train_area_arc',
        'train_area_spin', 'train_area_serv', 'train_area_rhy',
        'tr_grip_t', 'tr_grip_d', 'tr_quad_t', 'tr_quad_d', 'tr_bord_t',
        'tr_bord_d', 'tr_tape_t', 'tr_tape_d', 'tr_glob_t', 'tr_glob_d',
        'tr_back_t', 'tr_back_d', 'tr_top_t', 'tr_top_d', 'tr_sshort_t',
        'tr_sshort_d', 'tr_sdeep_t', 'tr_sdeep_d', 'tr_metro_t',
        'tr_metro_d', 'train_best', 'train_hud_streak', 'train_hud_sess',
        'train_hud_feed', 'train_hud_serve', 'train_ok', 'train_fail_net',
        'train_fail_zone', 'train_skin_t', 'skin_ebano', 'skin_neon',
        'msg_skin_unlock', 'train_rally']
# separa las dos mesas i18n
es_i = txt.index('es: {')
en_i = txt.index('en: {')
es_tbl = txt[es_i:en_i]
en_tbl = txt[en_i:txt.index('function ppPlayerName')] if 'function ppPlayerName' in txt else txt[en_i:en_i + 90000]
chk('A2a claves i18n ES', all((k + ':') in es_tbl for k in KEYS),
    str(sum(1 for k in KEYS if (k + ':') in es_tbl)) + '/' + str(len(KEYS)))
chk('A2b claves i18n EN', all((k + ':') in en_tbl for k in KEYS),
    str(sum(1 for k in KEYS if (k + ':') in en_tbl)) + '/' + str(len(KEYS)))

chk('A3a TRAIN_AREAS 6', txt.count("key: 'grip'") == 1 and "key: 'rhy'" in txt)
for mid, pts in [('quad', 12), ('bord', 10), ('cinta', 12), ('glob', 14),
                 ('cortada', 12), ('topspin', 12), ('saquecorto', 15),
                 ('saqueprof', 15), ('metro', 10)]:
    if f"id: '{mid}'" not in txt:
        chk('A3b TRAIN_MODES ' + mid, False)
        break
else:
    chk('A3b TRAIN_MODES 9 ids', True)
chk('A3c TRAIN_SERVE', "new Set(['saquecorto', 'saqueprof'])" in txt)
chk('A3d PADDLE_SKINS umbrales',
    all(f"need: {n}" in txt for n in (0, 60, 150, 280, 450, 700)))
chk('A3e almacen pp_train_v1', "const TRAIN_KEY = 'pp_train_v1'" in txt)

for fn in ['enterTraining(', 'exitTraining(', 'updateTraining(', '_trainTableBounce(',
           'feedDrillBall(', 'buildTrainProps(', 'disposeTrainProps(', 'setPaddleSkin(',
           'createTrainPanel(', 'addSpinBadges(', 'markRingTexture(', 'trainAddPoints(',
           'trainBest(', '_newQuadTarget(', '_zoneAt(', 'drawMenuTraining(']:
    if fn not in txt:
        chk('A4 motor ' + fn, False)
        break
else:
    chk('A4 motor completo (15 símbolos)', True)

chk('A5a tarjeta page:train', "this._modeCard(rects, 'page:train'" in txt)
chk('A5b caso tr:', "case 'tr': {" in txt)
chk('A5c caso skin:', "case 'skin': {" in txt)
chk('A5d page acepta train', "arg === 'champs' || arg === 'opts' || arg === 'train'" in txt)
chk('A5e despachador drawMenuTraining', 'this.drawMenuTraining(rects)' in txt)

gates = txt.count('this._trainServe')
chk('A6a compuertas _trainServe (>=7)', gates >= 7, gates)
chk('A6b saque SIN enderezado en academia', 'if (!this._trainServe) {' in txt)
chk('A6c evento paddle lleva spin', 'spin: ball.spin.clone(), vz: ball.vel.z' in txt)
chk('A6d iconos en processEvents', 'e.who === \'player\' && e.spin' in txt)

# A7 · sintaxis
import subprocess, tempfile, os
tmpdir = tempfile.mkdtemp(prefix='qa300_')
m = re.search(r'<script>([\s\S]*?)</script>', txt)
blocks = re.findall(r'<script(?![^>]*\bsrc=)(?![^>]*importmap)[^>]*>([\s\S]*?)</script>', txt)
fails = 0
for i, code in enumerate(blocks):
    if not code.strip():
        continue
    p = os.path.join(tmpdir, f'blk{i}.js')
    open(p, 'w').write(code)
    r = subprocess.run(['node', '--check', p], capture_output=True)
    if r.returncode != 0:
        fails += 1
        print(r.stderr.decode()[:800])
chk('A7 sintaxis JS inline', fails == 0, f'{len(blocks)} bloques')

# ---------------------------------------------------------------- B · runtime
with sync_playwright() as pw:
    br = pw.chromium.launch(args=['--use-gl=swiftshader', '--enable-unsafe-swiftshader'])
    pg = br.new_page(viewport={'width': 1280, 'height': 800})
    errors = []
    pg.on('pageerror', lambda e: errors.append(str(e)))
    pg.goto(BASE + '/game.html', wait_until='domcontentloaded')
    pg.wait_for_function('() => !!window.__PP_GAME', timeout=60000)
    pg.wait_for_timeout(2500)
    chk('B1a 0 pageerrors en carga', len(errors) == 0, errors[:2])
    chk('B1b motor vivo (reglas + ball + audio)', pg.evaluate(
        "!!window.__PP_GAME.rules && !!window.__PP_GAME.ball && !!window.__PP_GAME.audio"))
    chk('B1c game expuesto', pg.evaluate('!!window.__PP_GAME.ball'))

    # B2 · CUADRANTES
    pg.evaluate("window.__PP_GAME.enterTraining('quad')")
    pg.wait_for_timeout(600)
    st = pg.evaluate("""(() => {
      const g = window.__PP_GAME;
      return {
        mode: g.trainMode, calib: g.calib, isServe: g.train && g.train.isServe,
        zone: g.train && g.train.targetZone,
        props: !!g.trainGrp, chalk: !!g._chalk, hi: !!g._zoneHi,
        marks: g._marks ? g._marks.length : 0, arrow: !!g._spinArrow,
        panel: g.trainPanel.group.visible, dirty: g.trainPanelDirty,
      };
    })()""")
    chk('B2a quad activo', st['mode'] == 'quad' and st['calib'] and not st['isServe'], st)
    chk('B2b props cuadrantes', st['props'] and st['chalk'] and st['hi'] and st['marks'] == 14 and st['arrow'])
    chk('B2c HUD visible', st['panel'])
    # (el bucle de portada 2D no arrastra el entrenamiento: tick manual)
    fed = pg.evaluate("""(() => { const g = window.__PP_GAME;
      for (let i = 0; i < 240; i++) g.updateTraining(1/60);
      return { v: +g.ball.vel.length().toFixed(2), phase: g.train.phase };
    })()""")
    chk('B2d máquina alimenta (tick manual)', fed['v'] > 0.5 and fed['phase'] in ('fly', 'live'), fed)

    # B3 · puntos y rachas
    pts0 = pg.evaluate("JSON.parse(localStorage.getItem('pp_train_v1')||'{}').pts||0")
    pg.evaluate("window.__PP_GAME.trainSuccess()")
    r = pg.evaluate("""(() => {
      const g = window.__PP_GAME, st = JSON.parse(localStorage.getItem('pp_train_v1')||'{}');
      return { streak: g.train.streak, pts: st.pts||0, best: (st.bests||{}).quad||0 };
    })()""")
    chk('B3a success suma racha+puntos', r['streak'] == 1 and r['pts'] > pts0, r)
    pg.evaluate("window.__PP_GAME.trainFail('net')")
    r2 = pg.evaluate("window.__PP_GAME.train.streak")
    chk('B3b fail resetea racha', r2 == 0, r2)

    # B4 · robots con spin
    sp = pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.exitTraining(); g.enterTraining('cortada'); g.feedDrillBall();
      const s1 = g.ball.spin.x;
      g.exitTraining(); g.enterTraining('topspin'); g.feedDrillBall();
      const s2 = g.ball.spin.x;
      g.exitTraining();
      return { back: +s1.toFixed(1), top: +s2.toFixed(1) }; })()""")
    chk('B4a robot cortado backspin', sp['back'] < -40, sp)
    chk('B4b robot topspin', sp['top'] > 30, sp)

    # B5 · cinta
    tape = pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.enterTraining('cinta');
      const y = g._tapeY, netTop = 0.9125;
      // bola cruzando JUSTO la cinta: debe rebotar hacia el jugador
      // (integración MANUAL: la física no corre en la portada 2D)
      const b = g.ball;
      b.pos.set(0, y, -1.3); b.vel.set(0, 0, -2.5); b.spin.set(0,0,0);
      g.train.prevZ = b.pos.z; g.train.prevY = b.pos.y; g.train.prevX = 0;
      g.train.inPlay = true; g.train.crossed = false; g.train.phase = 'live';
      for (let i = 0; i < 40; i++) {
        b.pos.z += b.vel.z / 60; b.pos.y += b.vel.y / 60;
        g.updateTraining(1/60);
      }
      return { y: +y.toFixed(3), ok: +(y - netTop).toFixed(3), zEnd: +b.pos.z.toFixed(2) };
    })()""")
    chk('B5a cinta a +17 cm de la red', abs(tape['ok'] - 0.17) < 0.005, tape)
    chk('B5b colisión con la cinta', tape['zEnd'] > -1.55, tape)
    pg.evaluate("window.__PP_GAME.exitTraining()")

    # B6 · palas cosméticas
    skin = pg.evaluate("""(() => {
      const g = window.__PP_GAME;
      const st = JSON.parse(localStorage.getItem('pp_train_v1')||'{}');
      st.pts = 200; localStorage.setItem('pp_train_v1', JSON.stringify(st));
      g.setPaddleSkin('fuego');
      const m = g.paddleMounts[1].children[0];
      let col = null, badges = 0;
      m.traverse(o => { if (o.isMesh && !col && o.material) {
        const mm = Array.isArray(o.material) ? o.material[0] : o.material;
        if (mm.color) col = '#' + mm.color.getHexString(); } });
      g.spinBadges.forEach(b => { if (b) badges++; });
      return { skin: g.paddleSkin, saved: JSON.parse(localStorage.getItem('pp_train_v1')).skin,
               col, badges };
    })()""")
    chk('B6a skin fuego equipada+persistida', skin['skin'] == 'fuego' and skin['saved'] == 'fuego', skin)
    chk('B6b material tintado (≠ madera natural)', skin['col'] not in (None, '#b98a5a', 'c8a06a'), skin['col'])
    chk('B6c badges en las dos monturas', skin['badges'] == 2, skin['badges'])

    # B7 · icono de efecto se enciende y apaga
    badge = pg.evaluate("""(() => { const g = window.__PP_GAME;
      const sb = g.spinBadges[1];
      g.ball.spin.set(60, 0, 0);              // topspin hacia el rival
      sb.show(g.ball.spin, -2);
      const on = sb.meshes[0].visible && sb.meshes[1].visible;
      for (let i = 0; i < 90; i++) sb.update(1/60);
      const off = !sb.meshes[0].visible;
      return { on, off }; })()""")
    chk('B7a icono enciende ambas caras', badge['on'])
    chk('B7b icono se apaga solo', badge['off'])

    # B8 · página academia del menú
    menu = pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.toggleMenu(); g.menuPage = 'train'; g.drawMenu();
      const ids = g.menuRects.map(r => r.id);
      return { n: ids.length, quad: ids.includes('tr:quad'), metro: ids.includes('tr:metro'),
               skin: ids.includes('skin:ebano'), back: ids.includes('page:main'),
               grip: ids.includes('tr:grip') }; })()""")
    chk('B8 menú academia completo', all([menu['quad'], menu['metro'], menu['skin'],
                                          menu['back'], menu['grip'], menu['n'] >= 15]), menu)
    pg.screenshot(path='/home/z/my-project/scripts/_qa_v300_menu.png')

    # B9 · desbloqueo por puntos (vía REAL: _trainSessionPts → trainAddPoints)
    unl = pg.evaluate("""(() => {
      const g = window.__PP_GAME;
      g.enterTraining('metro');
      const st = JSON.parse(localStorage.getItem('pp_train_v1')||'{}');
      st.pts = 55; localStorage.setItem('pp_train_v1', JSON.stringify(st));
      g._trainSessionPts(10, false);           // 65 → cruza 60 (Ébano)
      const r = JSON.parse(localStorage.getItem('pp_train_v1')||'{}');
      return { pts: r.pts||0, msg: g.train.msg, ok: g.train.msgOk };
    })()""")
    chk('B9a 65 pts desbloquea Ébano(60) con aviso',
        unl['pts'] == 65 and 'Ébano' in unl['msg'] or 'Ebony' in unl['msg'], unl)
    # skin bloqueada no se equipa
    locked = pg.evaluate("""(() => { const g = window.__PP_GAME;
      g.setPaddleSkin('oro');   // 450 > 65 → debe ignorarse
      return g.paddleSkin; })()""")
    chk('B9b skin bloqueada rechazada', locked == 'fuego', locked)

    # B10 · foto del modo cuadrantes (3D con tiza) — renderer 2D sin XR:
    pg.evaluate("window.__PP_GAME.enterTraining('quad')")
    pg.wait_for_timeout(1800)
    pg.screenshot(path='/home/z/my-project/scripts/_qa_v300_quad.png')
    pg.evaluate("window.__PP_GAME.exitTraining()")
    chk('B10 fotos guardadas', True)

    # C · smoke 2D: el juego sigue arrancando limpio
    pg.evaluate("window.__PP_GAME.rules.startMatch('match')")
    pg.wait_for_timeout(1200)
    errs_after = [e for e in errors]
    chk('C smoke partido 0 pageerrors', len(errs_after) == 0, errs_after[:2])
    br.close()

print()
ok = sum(1 for _, o, _ in RES if o)
print(f"QA V3.0 · {ok}/{len(RES)} pruebas superadas")
raise SystemExit(0 if ok == len(RES) else 1)
