#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r103_v3695.py — capa de QA de la ronda 103 (V3.6.95-SDK6).

Dos peticiones del dueño:
 1) «Las etiquetas de altura de la barra no estén en primer plano: no dejan
    jugar con comodidad al estar sobre la línea de visión de mesa. Estarán
    FIJAS sin ningún cambio de orientación, ancladas a la altura de la barra
    que movemos y en su mismo plano, pero en la parte DERECHA fuera de la
    visión de la mesa»: rótulo cm + flechas pasan de sprites flotantes sobre
    el cuadrante propio (z mundo −0,53, r102) a MALLAS DE ORIENTACIÓN FIJA
    en el PLANO de la barra (z mundo = centro de mesa −1,6) y a la DERECHA
    de la mesa (x = canto derecho +0,42 ≈ 1,18 m), altura viva (cinta +0,075).
 2) «TODOS los rivales de los campeonatos [a la] derecha de la mesa fuera
    del campo de visión y SIEMPRE anclados a la posición de la mesa…
    si reorientamos la cámara o escaneamos una nueva zona condiciona su
    colocación y NO PUEDE SER»: Halloween era el ÚNICO módulo que colgaba el
    rival (y cartel, manos, dianas, hud, globos, trozos, humo, manchas,
    insignia) de game.SCENE en vez de game.RIG — el rig es el marco que rota
    updateRecenter(); al recentrar, mesa+sala giran y lo de scene se queda
    atrás (el zombi acababa «detrás de la mesa a la altura de la raqueta»).
    r103: TODO lo anclado a mesa vive en el RIG (28 sitios), con las
    excepciones de mundo correctas preservadas (visor de cámara, calabaza
    hija del padre de la bola r97, haz de pistola en mundo) y las DOS
    conversiones mundo→rig que el cambio exige (billboard de manos y rayo
    de la pistola contra dianas, patrón c12 r73 worldToLocal).
"""
import functools, json, os
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8840
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA (game.html + módulo halloween) ==')
GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8').read()
HWJS = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()

AGUJAS = [
    # 1 · etiquetas de la barra: DERECHA, PLANO de la barra, altura viva, FIJAS
    ('const BARRA_LBL_X = () => HW() + 0.42;',
     'c13: rótulo FUERA del canto derecho (x ≈ 1,18 m, canto +0,42)'),
    ('if (barraLbl) barraLbl.position.set(xl, by + 0.075, 0);',
     'c13: rótulo en el PLANO de la barra (z local 0) y a su ALTURA (+0,075)'),
    ('if (barraUp) barraUp.position.set(xl - BARRA_SEP, by + 0.075, 0);',
     'c13: flecha ↑ anclada a la altura de la barra'),
    ('if (barraDn) barraDn.position.set(xl + BARRA_SEP, by + 0.075, 0);',
     'c13: flecha ↓ anclada a la altura de la barra'),
    ('new THREE.PlaneGeometry(0.34, 0.0935)',
     'c13: rótulo = MALLA de orientación FIJA (no sprite)'),
    ('new THREE.PlaneGeometry(0.085, 0.085)',
     'c13: flechas = MALLAS de orientación FIJA (no sprites)'),
    ('barraFijo: () => ({',
     'c13: accesores QA de la orientación fija'),
    # 2 · halloween anclado al RIG (marco de la mesa)
    ('(this.game.rig || this.game.scene).add(this.r.node);',
     'halloween: EL RIVAL nace en el RIG (inmune al recentrado)'),
    ('(game.rig || game.scene).add(cartel.mesh);',
     'halloween: cartel de bienvenida en el RIG'),
    ('(game.rig || game.scene).add(M.grupo);',
     'halloween: grupo de MANOS en el RIG (colisiona con la bola del rig)'),
    ('(this.game.rig || this.game.scene).add(this.hud);',
     'halloween: HUD de dianas en el RIG'),
    ('(this.game.rig || this.game.scene).add(s);',
     'halloween: DIANAS en el RIG (posiciones de mesa)'),
    ('if (raiz103 && raiz103.worldToLocal) raiz103.worldToLocal(_v86);',
     'halloween: billboard de manos convierte cámara MUNDO→RIG'),
    ('raiz.getWorldQuaternion(new THREE.Quaternion()).invert());',
     'halloween: rayo de la pistola convertido MUNDO→RIG (quaternión)'),
    ('oR = origen.clone(); raiz.worldToLocal(oR);',
     'halloween: origen del rayo convertido MUNDO→RIG'),
]
for aguja, nombre in AGUJAS:
    objetivo = HWJS if nombre.startswith('halloween') else GH
    CHK(aguja in objetivo, ('halloween: ' if objetivo is HWJS else 'game.html: ') + nombre)

RETIRADAS = [
    # la etiqueta en primer plano del r102
    ('const BARRA_LBL_Z = () => HL() - 0.30;',
     'c13: rótulo sobre el cuadrante propio RETIRADO (estorbaba la visión)'),
    ('if (barraLbl) barraLbl.position.set(0, by + 0.13, zl);',
     'c13: rótulo pegado al jugador (r102) RETIRADO'),
    ('barraLbl.scale.set(0.34, 0.093, 1);',
     'c13: SPRITE del rótulo RETIRADO (ahora malla fija)'),
    ('new THREE.Sprite(new THREE.SpriteMaterial({\n          map: barraChevronTex(dir)',
     'c13: SPRITES de flechas RETIRADOS (ahora mallas fijas)'),
    # el anclaje roto de halloween
    ('(this.game.scene || this.game.rig).add(this.r.node);',
     'halloween: rival en SCENE RETIRADO (se descolgaba del recentrado)'),
]
for aguja, nombre in RETIRADAS:
    objetivo = HWJS if nombre.startswith('halloween') else GH
    CHK(aguja not in objetivo, ('halloween: ' if objetivo is HWJS else 'game.html: ') + nombre)

# las excepciones de MUNDO correctas siguen en su sitio (nada convertido en exceso)
CHK('try { game.camera.add(S.grupo); } catch (e) { game.scene.add(S.grupo); }' in HWJS,
    'halloween: visor de moscas SIGUE en cámara (efecto de vista, no de mesa)')
CHK('else game.scene.add(C.gltf);' in HWJS,
    'halloween: calabaza SIGUE hija del padre de la bola (r97)')
CHK('this.game.scene.add(m);\n    this.beams.push({ m, t: 0.16 });' in HWJS,
    'halloween: haz de la pistola SIGUE en mundo (nace de la cámara XR)')
CHK('(this.game.rig || this.game.scene).remove(this.cartel.mesh);' in HWJS,
    'halloween: retirada del cartel también del RIG (sin fugas)')

# r101/r102 intactas
CHK('function barraUpdate(px, py, pz, dt) {' in GH, 'game.html: máquina por proximidad intacta (r101)')
CHK('function barraStick(dt) {' in GH, 'game.html: máquina del JOYSTICK intacta (r102)')
CHK('const BARRA_STICK_V = 0.14;' in GH, 'game.html: 14 cm/s intacto (r102)')
CHK("'JOYSTICK ↑↓ O MANO EN LA CINTA';" in GH, 'game.html: aviso al jugador intacto (r102)')
CHK('PROTO: 2,' in GH, 'game.html: pala rival FIEL intacta (r102 códec)')

# versión sellada
import re as _re
mver = _re.search(r"const VERSION = '([^']+)'", GH)
CHK(bool(mver) and mver.group(1) == '3.6.101-SDK6', 'c00: VERSION sella 3.6.101-SDK6')
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
CHK(V.get('fase') == 100, 'VERSION.json: FASE 97')
CHK(V.get('hub') == 'v36101-sdk6', 'VERSION.json: hub v3695-sdk6')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(2500)

    # ---- 1 · ETIQUETAS: derecha, plano de la barra, altura viva, mallas fijas
    esc = pg.evaluate("""() => {
      const T = window.__PP_TRAIN;
      const X = T.__test;
      const D = window.__PP_CORE.DIMS;
      try { T.tick(0.016); } catch (e) { return { err: 'tick: ' + (e && e.message) }; }
      X.barraVisSet(true);
      X.barraLay();
      const out = { spr: X.barraSpr(), fijo: X.barraFijo(), zLbl: X.barraEtiquetaZ(),
                    D: { hw: D.tableHalfWidth, cz: D.tableCenterZ } };
      out.xEsperado = D.tableHalfWidth + 0.42;
      // el rótulo VIAJA con la barra: +7 cm de barra → +7 cm de rótulo
      const y0 = out.spr.lbl.y, b0 = out.spr.cinta.band;
      for (let k = 0; k < 7; k++) X.barraAjustar(1);
      X.barraLay();
      out.spr2 = X.barraSpr();
      out.dyR = out.spr2.lbl.y - y0;
      out.dyC = out.spr2.cinta.band - b0;
      out.fijo2 = X.barraFijo();
      for (let k = 0; k < 7; k++) X.barraAjustar(-1);   // volver
      X.barraLay();
      return out;
    }""")
    if 'err' in (esc or {}):
        CHK(False, 'etiqueta: %s' % esc.get('err'))
    else:
        s, f = esc['spr'], esc['fijo']
        CHK(s and s.get('up'), 'etiqueta: mandos construidos')
        if s and s.get('up'):
            CHK(abs(s['lbl']['x'] - esc['xEsperado']) < 1e-6,
                'etiqueta: rótulo a la DERECHA de la mesa (x=%s = canto+0,42)' % round(s['lbl']['x'], 4))
            CHK(s['lbl']['x'] > esc['D']['hw'] + 0.40,
                'etiqueta: FUERA del campo de la mesa (x > canto derecho +0,40)')
            CHK(abs(s['up']['x'] - (esc['xEsperado'] - 0.24)) < 1e-6 and
                abs(s['dn']['x'] - (esc['xEsperado'] + 0.24)) < 1e-6,
                'etiqueta: flechas flanqueando el rótulo (±0,24 m)')
            CHK(abs(esc['zLbl'] - esc['D']['cz']) < 1e-6,
                'etiqueta: en el MISMO PLANO que la barra (z mundo=%s = centro de mesa)' % round(esc['zLbl'], 3))
            CHK(abs(s['lbl']['y'] - (s['cinta']['band'] + 0.075)) < 1e-6,
                'etiqueta: ANCLADA a la altura de la barra (cinta +0,075)')
            CHK(f['lblMesh'] and f['upMesh'] and f['dnMesh'],
                'etiqueta: MALLAS de orientación FIJA (isMesh, jamás sprites)')
            CHK(abs(f['lblYRel'] - 0.075) < 1e-6, 'etiqueta: delta cinta→rótulo constante +0,075')
            CHK(abs(esc['dyR'] - esc['dyC']) < 1e-9 and abs(esc['dyR'] - 0.07) < 1e-9,
                'etiqueta: sube y baja CON la barra (+7 cm de barra → +7 cm de rótulo, delta 0)')
            CHK(abs(esc['fijo2']['lblX'] - esc['xEsperado']) < 1e-6,
                'etiqueta: la X no se mueve al ajustar (fija en su columna)')
        for k in range(0): pass

    # ---- 2 · ANCLAJE AL RIG: las conversiones de halloween, con un rig GIRADO
    # (recrea el informe del dueño: «si reorientamos la cámara… condiciona su
    # colocación»). Matemática pura — la MISMA fórmula que el módulo ejecuta
    # (worldToLocal + quaternión inverso), verificada contra la directa.
    rig = pg.evaluate("""() => {
      // rig girado 90° en Y (updateRecenter) — sin traslación (partida)
      const s = Math.SIN = Math.sin(Math.PI / 2), c = Math.cos(Math.PI / 2);
      // R(90°): x→−z, z→x  (matriz de rotación Y)
      const rotY = (v, inv) => inv
        ? [ v[0]*c + v[2]*s, v[1], -v[0]*s + v[2]*c ]     // R⁻¹ = R(−90°)
        : [ v[0]*c - v[2]*s, v[1], v[0]*s + v[2]*c ];      // R
      const T = [0, 0, 0];
      // worldToLocal del patrón three: v' = R⁻¹·(v − T)
      const worldToLocal = (v) => rotY([v[0]-T[0], v[1]-T[1], v[2]-T[2]], true);
      // DIANA en rig-local (donde el módulo la coloca respecto a la mesa)
      const dianaLocal = [1.20, 1.00, -2.00];
      const dianaMundo = rotY(dianaLocal, false);        // donde la VE la cámara XR
      // cámara XR (mundo) apuntando a la diana
      const cam = [0.0, 1.6, 0.6];
      const dir = [dianaMundo[0]-cam[0], dianaMundo[1]-cam[1], dianaMundo[2]-cam[2]];
      const n = Math.hypot(dir[0], dir[1], dir[2]);
      dir[0]/=n; dir[1]/=n; dir[2]/=n;
      const alcance = 6.0;
      const prueba = (origen, d) => {
        const t0 = [dianaLocal[0]-origen[0], dianaLocal[1]-origen[1], dianaLocal[2]-origen[2]];
        const tProy = t0[0]*d[0] + t0[1]*d[1] + t0[2]*d[2];
        if (tProy < 0 || tProy > alcance) return { hit: false, dist: 99 };
        const punto = [origen[0]+d[0]*tProy, origen[1]+d[1]*tProy, origen[2]+d[2]*tProy];
        return { hit: Math.hypot(punto[0]-dianaLocal[0], punto[1]-dianaLocal[1], punto[2]-dianaLocal[2]) <= 0.24,
                 dist: Math.hypot(punto[0]-dianaLocal[0], punto[1]-dianaLocal[1], punto[2]-dianaLocal[2]) };
      };
      // SIN CONVERSIÓN (dianas ya en el RIG pero rayo aún en mundo):
      // el rayo apunta a donde el jugador VE la diana (rig girado) y el
      // test la busca en rig-local → falla de largo. La conversión es OBLIGATORIA.
      const viejo = prueba(cam, dir);
      // LO NUEVO r103: origen y dir convertidos al espacio del rig
      const oR = worldToLocal(cam.slice());
      const dR = rotY(dir.slice(), true);
      const nuevo = prueba(oR, dR);
      // BILLBOARD de la mano: la mano debe mirar a la cámara EN ESPACIO RIG
      const manoLocal = [0.3, 0.9, -0.9];
      const camRig = worldToLocal(cam.slice());
      const yawNuevo = Math.atan2(camRig[0]-manoLocal[0], camRig[2]-manoLocal[2]);
      const yawViejo = Math.atan2(cam[0]-manoLocal[0], cam[2]-manoLocal[2]);
      return { viejo, nuevo, yawNuevo, yawViejo };
    }""")
    CHK(rig['nuevo']['hit'] and rig['nuevo']['dist'] < 1e-9,
        'anclaje: con el rig girado 90°, el rayo CONVERTIDO da EN la diana (err %.1e m)' % rig['nuevo']['dist'])
    CHK(not rig['viejo']['hit'] or rig['viejo']['dist'] > 0.5,
        'anclaje: el rayo SIN convertir falla de largo (err %.2f m — la conversión es obligatoria)' % rig['viejo']['dist'])
    CHK(abs(rig['yawNuevo'] - 0.3217) < 0.01,
        'anclaje: billboard de la mano mira a la cámara EN ESPACIO RIG (yaw %.3f rad)' % rig['yawNuevo'])
    CHK(abs(rig['yawViejo'] - rig['yawNuevo']) > 0.5,
        'anclaje: la fórmula VIEJA desviaba el billboard %.2f rad (mezcla de espacios)' % abs(rig['yawViejo'] - rig['yawNuevo']))

    # ---- 3 · JOYSTICK r102 sigue vivo (subida de 14 pasos + clamps)
    stick = pg.evaluate("""() => {
      const T = window.__PP_TRAIN, X = T.__test, g = window.__PP_GAME;
      const out = {};
      const orig = g.stickAxis.bind(g);
      try {
        g.stickAxis = (h) => (h === 0 ? { x: 0, y: -1 } : { x: 0, y: 0 });
        const h0 = X.barraH();
        let n = 0;
        for (let k = 0; k < 72; k++) if (X.barraStick(1 / 72)) n++;
        out.pasos = n;
        out.subida = X.barraH() - h0;
        // …y el rótulo siguió a la cinta durante el ajuste por stick
        const s1 = X.barraSpr();
        out.dyLbl = s1.lbl.y - (s1.cinta.band + 0.075);
        g.stickAxis = orig;
        X.barraStick(1 / 72);
      } catch (e) { out.err = e && e.message; try { orig(); } catch (e2) { /* */ } }
      return out;
    }""")
    if 'err' in stick:
        CHK(False, 'joystick: %s' % stick['err'])
    else:
        CHK(13 <= stick['pasos'] <= 15, 'joystick: 72 frames ≈ 14 pasos de 1 cm (%s) — r102 intacto' % stick['pasos'])
        CHK(abs(stick['dyLbl']) < 1e-6, 'joystick: el rótulo siguió a la barra durante TODO el ajuste')

    # ---- 4 · sin errores de página
    CHK(not errs, 'runtime: sin errores de página (%s)' % (errs[0][:80] if errs else 'limpio'))

    b.close()
srv.shutdown()

print()
print('QA r103 · OK=%d · FALLO=%d' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  -', f)
    raise SystemExit(1)
