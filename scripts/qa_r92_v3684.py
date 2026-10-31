#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r92_v3684.py — capa de QA en vivo de la ronda 92 (V3.6.89-SDK6).
Informe del dueño tras V3.6.83:
 «Las manos de los zombis deben salir justa de la mesa de tal forma que su
  parte inferior toque la mesa y no quede suspendida en el aire. Cambiamos
  la textura de la mesa por la nueva que adjunto. Ojo que cuando tenemos el
  superpoder calabaza, el rival no la golpea correctamente con su pala
  parece que tiene un desplazamiento y el efecto no queda bien. La calabaza
  debería girar sobre si misma al golpearla tal como haría la bola.»
Las cuatro, verificadas AQUÍ:
 1) MANOS ANCLADAS: la base del plano vive a tableTopY+0,005 (MANO_Y) en
    TODAS las fases (subir/arriba/bajar) — fuera el ascenso +0,12 y el bob
    de la r89 que dejaban la mano suspendida; el desenrollado (repeat.y)
    sigue naciendo DESDE la mesa.
 2) MESA NUEVA: mesa.webp (2048×1024, 4 losas con sangre) viste el
    ppTableTop por _losaOn (SRGB + anisotropía), losa.jpg conservada.
 3) GOLPE DEL RIVAL: con ppCalabaza el alcance baja a 0,12 m y el punto de
    contacto se arrastra a la TANGENTE con la hoja (≤0,075 del centro de
    la pala) — probado con la IA REAL (OpponentAI.update) en los dos
    sentidos (con y sin marca).
 4) GIRO PROPIO: la calabaza acumula SU rotación arrastrada por el spin
    (spin·dt·0,15) — se la ve girar al golpearla; la marca se limpia en
    estallido y fin()."""
import os, sys, functools, json, struct
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
C06 = os.path.join(RAIZ, 'src/game/core/c06_logros_stats_ia_rival.js')
PORT = 8813
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(HAL, 'manifest.json')))
CHK(any(n.startswith('v6 (r92)') for n in man.get('notes', [])), 'manifest: nota v6 (r92) presente')
CHK('mesa.webp' in man.get('assets', ''), 'manifest: assets cita mesa.webp (textura de mesa r92)')

PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
C6 = open(C06, encoding='utf-8').read()

# 1 · MANOS — base pegada a la mesa en TODAS las fases
CHK('const MANO_Y = 0.005;' in PLA, 'index: MANO_Y (base del plano a 5 mm del tablero)')
CHK('mano.position.set(x, DIMS.tableTopY + MANO_Y, z)' in PLA,
    'index: la mano NACE con la base en la mesa (tableTopY + MANO_Y)')
CHK(PLA.count('v.mano.position.y = v.y0;') == 3,
    'index: subir/arriba/bajar FIJAN la base (3 asignaciones position.y = v.y0, cero ascensos)')
CHK('+ e * 0.12' not in PLA and '+ 0.12 +' not in PLA and '(1 - k * k) * 0.12' not in PLA,
    'index: ASCENSO/BOB de la r89 FUERA (nada suspende la mano)')
CHK('pivote en la base' in PLA, 'index: el vaivén vivo es de rotación con PIVOTE EN LA BASE (comentario de la decisión)')

# 2 · MESA — mesa.webp viste el ppTableTop
CHK("new THREE.TextureLoader().load(A('mesa.webp'))" in PLA, 'index: _losaOn carga mesa.webp (textura nueva del dueño)')
CHK("A('losa.jpg')" not in PLA, 'index: losa.jpg ya no se carga en runtime (conservada para rollback)')
w, h = 0, 0
try:
    with open(os.path.join(HAL, 'assets/mesa.webp'), 'rb') as f:
        b0 = f.read(40)
    # RIFF....WEBPVP8 ; dimensiones en el chunk VP8X o VP8
    assert b0[:4] == b'RIFF' and b0[8:12] == b'WEBP'
    if b0[12:16] == b'VP8X':
        w = 1 + int.from_bytes(b0[24:27], 'little')
        h = 1 + int.from_bytes(b0[27:30], 'little')
    else:
        w = struct.unpack('<H', b0[26:28])[0] & 0x3fff
        h = struct.unpack('<H', b0[28:30])[0] & 0x3fff
except Exception as e:
    print('  (aviso webp:', e, ')')
CHK(w == 2048 and h == 1024, 'assets: mesa.webp VÁLIDO 2048×1024 (%s×%s)' % (w, h))
CHK(os.path.exists(os.path.join(HAL, 'assets/losa.jpg')), 'assets: losa.jpg CONSERVADA (rollback)')

# 3 · GOLPE DEL RIVAL — alcance + tangente con la marca ppCalabaza
CHK('const reach = ball.ppCalabaza ? 0.12 : 0.21;' in C6,
    'c06: alcance del rival 0,12 m CON calabaza (0,21 sin marca — el probado)')
CHK('const TOCA = 0.075;' in C6 and 'if (ball.ppCalabaza) {' in C6,
    'c06: contacto ARRASTRADO a la tangente con la hoja (centro de calabaza a 7,5 cm)')
CHK('if (game.ball) game.ball.ppCalabaza = true;' in PLA, 'index: marca ppCalabaza PUESTA en inicio')
CHK(PLA.count('ppCalabaza = false') >= 2, 'index: marca LIMPIA en estallido y fin (nunca queda pegada)')

# 4 · GIRO PROPIO — rotación arrastrada por el spin
CHK('C.gltf.rotation.x += sp.x * dt * 0.15;' in PLA and 'C.gltf.rotation.y += sp.y * dt * 0.15;' in PLA,
    'index: calabaza gira SOBRE SÍ MISMA (spin ×3 la tasa visual de la bola)')
CHK('quaternion.copy(game.ballMesh.quaternion)' not in PLA,
    'index: fuera la copia de quaternion r88 (no se apreciaba en 13 cm)')

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
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=4000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(9000)

    # ---- MESA: textura nueva en el ppTableTop
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), g = ctrl.game;
      const top = g.tableGroup && g.tableGroup.getObjectByName('ppTableTop');
      if (!top) return { vive: true, top: false };
      const src = top.material.map && top.material.map.image && top.material.map.image.src || null;
      return { vive: true, top: true,
        src: src ? (src.endsWith('mesa.webp') ? 'mesa.webp' : src.slice(src.length - 10)) : null,
        cs: top.material.map ? String(top.material.map.colorSpace) : null,
        rough: +top.material.roughness.toFixed(2),
        marco: (() => { const n = g.tableGroup.children.find(c => c.name === 'ppTableApron' || c.name === 'ppTableLeg');
                        return n && n.material ? '#' + n.material.color.getHexString() : null; })(),
        saved: !!ctrl._losaSaved };
    }""")
    CHK(st.get('vive') is True, 'halloween vivo')
    if not st.get('vive'):
        print(json.dumps(st, indent=1)); srv.shutdown(); b.close(); sys.exit(1)
    CHK(st.get('top') is True, 'mesa: ppTableTop presente')
    CHK(st.get('src') == 'mesa.webp', 'mesa: TEXTURA NUEVA puesta (src=…%s)' % st.get('src'))
    CHK(st.get('cs') == 'srgb', 'mesa: SRGB (el arte del dueño con su color)')
    CHK(st.get('saved') is True, 'mesa: respaldo _losaSaved vivo (restauración garantizada)')
    CHK(st.get('marco') == '#3d4145', 'mesa: marco/patas en piedra oscura (#3d4145)')

    # ---- MANOS: base EN la mesa en subir y arriba (sondeo por fases)
    manos = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const D = window.__PP_CORE.DIMS;
      const ctxP = {};
      H.pods.mano.inicio(g, { duration: 20 }, ctrl, ctxP);
      const M = ctxP.mano; if (!M) return { err: 'sin ctx.mano' };
      for (let i = 0; i < 100 && M.tex.length < 3; i++) await new Promise(r => setTimeout(r, 100));
      const impl = H.pods.mano;
      // la bola aparcada puede robar la ranura (guardia anti-nacer-sobre-la-bola):
      // la APARTAMOS fuera de la mesa durante el sondeo (como qa_r90)
      const bola0 = g.ball.pos.clone();
      g.ball.pos.set(0, 1.0, D.tableCenterZ + 1.15);
      let v = null;
      for (let i = 0; i < 6 && !v; i++) { impl._spawn(g, M); v = M.vivos[M.vivos.length - 1] || null; }
      if (!v) { g.ball.pos.copy(bola0); return { err: 'sin mano' }; }
      const base = D.tableTopY + 0.005;
      // SUBIR: 5 muestras durante el desenrollado
      const muestras = [];
      for (let i = 0; i < 5; i++) { impl.paso(0.07, g, { duration: 20 }, ctrl, ctxP); muestras.push({ f: v.fase, y: +v.mano.position.y.toFixed(4), sy: +v.mano.scale.y.toFixed(3), rep: +v.tex.repeat.y.toFixed(3) }); }
      for (let i = 0; i < 12 && v.fase !== 'arriba'; i++) impl.paso(0.07, g, { duration: 20 }, ctrl, ctxP);
      const arriba = [];
      for (let i = 0; i < 6; i++) { impl.paso(0.09, g, { duration: 20 }, ctrl, ctxP); arriba.push({ f: v.fase, y: +v.mano.position.y.toFixed(4), rep: +v.tex.repeat.y.toFixed(3) }); }
      // BAJAR: a mitad del retracto la base SIGUE en la mesa
      for (let i = 0; i < 26 && v.fase !== 'bajar'; i++) impl.paso(0.09, g, { duration: 20 }, ctrl, ctxP);
      impl.paso(0.2, g, { duration: 20 }, ctrl, ctxP);
      const bajar = { f: v.fase, y: +v.mano.position.y.toFixed(4) };
      try { H.pods.mano.fin(g, { duration: 20 }, ctrl, ctxP); } catch (e) {}
      g.ball.pos.copy(bola0);
      return { base: +base.toFixed(4), muestras, arriba, bajar };
    }""")
    if 'err' in (manos or {}):
        CHK(False, 'mano: ctx vivo (%s)' % manos['err'])
    else:
        CHK(all(abs(m['y'] - manos['base']) < 1e-3 for m in manos['muestras']),
            'mano: en SUBIR la base SIEMPRE en la mesa (%s — y0=%s)' % ([m['y'] for m in manos['muestras']], manos['base']))
        CHK(all(abs(m['y'] - manos['base']) < 1e-3 for m in manos['arriba']),
            'mano: en ARRIBA la base SIGUE en la mesa (sin bob — %s)' % [m['y'] for m in manos['arriba']])
        CHK(all(m['rep'] > 0.99 for m in manos['arriba']), 'mano: arte COMPLETO en arriba (repeat=%s)' % manos['arriba'][0]['rep'])
        CHK(manos['bajar']['f'] == 'bajar' and abs(manos['bajar']['y'] - manos['base']) < 1e-3,
            'mano: en BAJAR la base NO se levanta (y=%s)' % manos['bajar']['y'])
        primera = manos['muestras'][1] or {}
        CHK(primera.get('sy', 0) > 0.05, 'mano: el DESENROLLADO vive (scale.y=%s — nace desde la mesa)' % primera.get('sy'))

    # ---- GOLPE DEL RIVAL con la IA REAL (OpponentAI.update)
    golpe = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const ai = g.ai; if (!ai) return { err: 'sin ai' };
      const D = window.__PP_CORE.DIMS;
      const C = D.tableCenterZ;
      const out = {};
      const prepara = (marca, offX, zAI) => {
        ai.hitCooldown = 0; ai.swing = null; ai.predictValid = false;
        ai.pos.set(offX, 1.0, zAI); ai.vel.set(0, 0, 0);
        g.ball.pos.set(0.10, 1.0, C - 0.60);
        g.ball.vel.set(0, 0, -6);                    // hacia la IA (sign −1)
        g.ball.spin.set(0, 0, 0);
        g.ball.ppCalabaza = marca;
        const prev = g.ball.pos.clone(); prev.z += 0.06;   // un paso atrás
        const posAI = ai.pos.clone();
        const ctx = { canHit: true, validBounce: true, prevBall: prev,
                      oppPadX: 0, oppPadZ: C + 1.2, rallyHits: 3 };
        const v = ai.update(0.008, g.ball, ctx);
        return { golpeo: !!v, dist: +(g.ball.pos.distanceTo(posAI)).toFixed(4),
                 velZ: v ? +v.z.toFixed(2) : null, contacto: ai.swing ? ai.swing.contact.toArray().map(x=>+x.toFixed(3)) : null,
                 distContact: ai.swing ? +(ai.swing.contact.distanceTo(posAI)).toFixed(4) : null,
                 flat: ai.swing ? ai.swing.flat === true : null };
      };
      // A) CON marca: pala a 10 cm del radio — alcance 0,12 la ve.
      //    r93 (re-anclaje honesto): la bola se queda en el PUNTO DEL
      //    BARRIDO (≈0,10 — el arrastre a tangente de la r92 SE RETIRA:
      //    era el desfase que veía el dueño) y la HOJA nace en la piel
      //    (contacto tangente ≈0,075 + flat).
      out.con = prepara(true, 0.20, C - 0.60);
      // B) CON marca y pala a 18 cm del radio: alcance 0,12 NO llega (fallo natural — la marca no imita al alcance viejo)
      out.lejos = prepara(true, 0.28, C - 0.60);
      // C) SIN marca: alcance probado 0,21 SÍ la ve y el contacto NO se arrastra (queda en el barrido, ~0,18)
      out.sin = prepara(false, 0.28, C - 0.60);
      return out;
    }""")
    if 'err' in (golpe or {}):
        CHK(False, 'golpe IA: ai viva (%s)' % golpe['err'])
    else:
        con = golpe.get('con') or {}
        CHK(con.get('golpeo') is True, 'calabaza: la IA GOLPEA con la marca (alcance 0,12)')
        CHK(con.get('dist') is not None and con['dist'] > 0.08,
            'calabaza: la bola SE QUEDA en el punto del barrido (dist=%s — r93: sin arrastre a tangente)' % con.get('dist'))
        CHK(con.get('distContact') is not None and 0.069 <= con['distContact'] <= 0.081,
            'calabaza: la HOJA nace en la piel (contacto tangente=%s ≈ 0,075 — r93)' % con.get('distContact'))
        CHK(con.get('flat') is True, 'calabaza: swing flat (sin ascenso inicial — r93)')
        CHK(con.get('velZ') is not None and con['velZ'] > 0, 'calabaza: la devolución SALE (velZ=%s)' % con.get('velZ'))
        lejos = golpe.get('lejos') or {}
        CHK(lejos.get('golpeo') is False, 'calabaza: a 18 cm el alcance 0,12 NO golpea (fallo natural, sin imitar al viejo)')
        sin = golpe.get('sin') or {}
        CHK(sin.get('golpeo') is True, 'bola normal: la IA golpea con el alcance probado 0,21')
        CHK(sin.get('dist') is not None and sin['dist'] > 0.12,
            'bola normal: contacto SIN arrastre (dist=%s — norma genérica intacta)' % sin.get('dist'))

    # ---- CALABAZA: giro propio + ciclo de la marca
    cala = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const ctxP = {};
      /* r94 · RE-ANCLAJE HONESTO: la calabaza sigue la bola RENDERIZADA
       * (ballMesh.position — garantía del informe del dueño en r94). El núcleo
       * sincroniza ballMesh ← ball.pos cada frame (c12 §7); las sondas IA de
       * arriba movieron ball.pos sin pasar por el núcleo → se replica el
       * sincronizado aquí antes de nacer el cuerpo. */
      if (g.ballMesh) g.ballMesh.position.copy(g.ball.pos);
      H.pods.calabaza.inicio(g, { duration: 10 }, ctrl, ctxP);
      const C = ctxP.calabaza; if (!C || !C.gltf) return { err: 'sin cuerpo' };
      const marcaOn = g.ball.ppCalabaza === true;
      g.ball.spin.set(20, 8, 0);
      const r0 = { x: C.gltf.rotation.x, y: C.gltf.rotation.y };
      H.pods.calabaza.paso(0.05, g, { duration: 10 }, ctrl, ctxP);
      H.pods.calabaza.paso(0.05, g, { duration: 10 }, ctrl, ctxP);
      const dr = { x: +(C.gltf.rotation.x - r0.x).toFixed(4), y: +(C.gltf.rotation.y - r0.y).toFixed(4) };
      const posOk = C.gltf.position.distanceTo(g.ball.pos) < 0.001;
      // estallido: la marca se LIMPIA
      C.t = 10 - 0.5; H.pods.calabaza.paso(0.55, g, { duration: 10 }, ctrl, ctxP);
      const marcaTrasEstallido = g.ball.ppCalabaza === false;
      const bolaVuelve = g.ballMesh.visible === true;
      try { H.pods.calabaza.fin(g, { duration: 10 }, ctrl, ctxP); } catch (e) {}
      return { marcaOn, dr, posOk, marcaTrasEstallido, bolaVuelve };
    }""")
    if 'err' in (cala or {}):
        CHK(False, 'calabaza: cuerpo vivo (%s)' % cala['err'])
    else:
        CHK(cala.get('marcaOn') is True, 'calabaza: marca ppCalabaza viva en la bola durante el poder')
        CHK((cala.get('dr') or {}).get('x', 0) > 0.1 and (cala.get('dr') or {}).get('y', 0) > 0.03,
            'calabaza: GIRA sobre sí misma arrastrada por el spin (Δx=%s rad, Δy=%s rad en 0,1 s)' % ((cala.get('dr') or {}).get('x'), (cala.get('dr') or {}).get('y')))
        CHK(cala.get('posOk') is True, 'calabaza: sigue CENTRADA en la bola')
        CHK(cala.get('marcaTrasEstallido') is True, 'calabaza: marca LIMPIA en el estallido (bola normal → IA normal)')
        CHK(cala.get('bolaVuelve') is True, 'calabaza: la bola normal VUELVE al estallar')

    # captura para la pasada de arte (mesa nueva en pantalla)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r92_mesa_rt.png'))

    b.close()
srv.shutdown()

print('')
print('== MARCADOR r92: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  ✗', f)
    sys.exit(1)
print('VERDE')
