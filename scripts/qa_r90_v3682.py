#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r90_v3682.py — capa de QA en vivo de la ronda 90 (V3.6.82-SDK6).
Informe del dueño tras V3.6.81: «añadir la música Midnight_Volley.mp3 ·
el mapa está lavado de color (adjunto arte nuevo) · no se escuchan crazy/
defeated/victory · la calabaza sigue sin verse (o la arreglamos o buscamos
otra forma) · retirar monticulo.png de la mesa porque corta las manos ·
¿qué pasa que la bola no hace nada al atravesar o chocar con las manos?
(con Clown-Burla era muy similar y funcionaba) · desfase entre la textura
de las vísceras y su zona de colisión + humillo verde CONTINUO mientras
dura el poder».
Estática (manifest/index/sdk) + RUNTIME determinista (colisión CCD real,
calabaza en escena, humillo continuo, decodificación del arte sonoro)."""
import os, sys, functools, json, math, subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
PORT = 8797
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(HAL, 'manifest.json')))
au = man.get('audio', {})
# r90 · BSO REAL del dueño
CHK(au.get('music') == 'assets/midnight_volley.mp3', 'manifest: BSO → assets/midnight_volley.mp3 (fin del bso.wav provisional)')
CHK(os.path.getsize(os.path.join(HAL, 'assets/midnight_volley.mp3')) > 1000000, 'assets: midnight_volley.mp3 presente (%d B)' % os.path.getsize(os.path.join(HAL, 'assets/midnight_volley.mp3')))
# r90 · perfil de audio del casco (lección Tunel: 24 kHz NO decodifica)
for f, dur in [('zombi_crazy.mp3', 2.25), ('zombi_victory.mp3', 1.85), ('zombi_defeated.mp3', 8.10), ('risas.mp3', 2.90), ('midnight_volley.mp3', 153.65)]:
    try:
        out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0',
                              '-show_entries', 'stream=sample_rate', '-of', 'csv=p=0',
                              os.path.join(HAL, 'assets', f)], capture_output=True, text=True).stdout.strip()
        CHK(out == '44100', 'assets: %s a 44100 Hz (perfil del casco; venía a %s)' % (f, out or '?'))
    except Exception as e:
        CHK(False, 'assets: ffprobe %s (%s)' % (f, e))
gel = [p for p in man.get('powers', []) if p.get('kind') == 'gelatina']
CHK(bool(gel) and gel[0].get('duration') == 12, 'manifest: gelatina duration=12 s (efecto verde prolongado)')

PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
# r90 · SONIDOS DEL ZOMBI AL MOTOR PROBADO (createBucle — lección del tren)
CHK('ZONB' in PLA and 'createBucle(() => GAME' in PLA and 'DUR_Z' in PLA,
    'index: sonidos del zombi en createBucle PROPIO por sonido (motor probado en el casco)')
CHK('_zombiSfxTick' in PLA and 'z.b.off()' in PLA and 'z.b.suena()' in PLA,
    'index: reloj de corte honesto (suena() + off ANTES del wrap, desistir a 9 s)')
CHK('ignoraMute: true' in PLA and 'fadeIn: 0.06' in PLA, 'index: one-shots del zombi con ignoraMute + fadeIn 0,06 (perfil Tunel/Tren_Llegada)')
CHK('base.play(' not in PLA.split('r90 · LOS ONE-SHOTS')[1][:2000] if 'r90 · LOS ONE-SHOTS' in PLA else False,
    'index: el play del zombi ya NO pasa por createSfx')
# r90 · MANOS SIN MONTÍCULO
CHK('M.texMonticulo' not in PLA and 'monticulo.webp' not in PLA and 'v.mont' not in PLA,
    'index: monticulo.png RETIRADO de la mesa (nada corta ya a las manos)')
CHK("fase: 'subir'" in PLA and "fase: 'monticulo'" not in PLA, 'index: la mano nace DIRECTA en fase subir (sin pop de tierra)')
CHK('MON = 0.17 + 0.03' in PLA, 'index: guardia de canto por RADIO DE LA MANO (sin montículo)')
# r90 · COLISIÓN BOLA↔MANO = MOTOR DE BURLA
CHK('M.prev.copy(bola)' in PLA and 'M.prevOk' in PLA and 'pasos = Math.max(1, Math.ceil(len / 0.03))' in PLA,
    'index: CCD por SEGMENTO subdividido a ≤3 cm (la bola NO atraviesa la mano)')
CHK('MANO_GROSOR' in PLA and 'Math.abs(lz) < semiesp' in PLA, 'index: caja LOCAL con grosor — vale por DELANTE y por DETRÁS')
CHK('game.ball.vel.set(0, -0.4, 0)' in PLA, 'index: la bola SE PARA Y CAE al chocar (0,-0.4,0 como Burla)')
CHK("game.rules.state === 'rally'" in PLA, 'index: colisión de mano en RALLYE (patrón Burla)')
CHK('game.audio.playNoise(0.20, 900' in PLA, 'index: crujido seco al reventar la mano')
CHK('SLOTS = [[-0.30, -0.9], [0.30, 0.0], [-0.30, 0.9]]' in PLA and '0.62 * 0.62' in PLA,
    'index: ranuras de mano SIN solape (regresión r89 intacta)')
# r90 · GELATINA SIN DESFASE + HUMILLO CONTINUO
CHK('_q86.copy(m.quaternion).invert()' in PLA and 'Math.abs(_v86.x) <= lim' in PLA,
    'index: zona de impacto = CUADRADO visual exacto (marco local por quaternion)')
CHK('(m.userData.tam || 0.3) * 0.5 + r * 0.75' in PLA, 'index: límite = mitad de la mancha + 3/4 de bola (holgura de borde)')
CHK('G.humoT2' in PLA and 'HUMILLO CONTINUO' in PLA and 'G.humo.length < 70' in PLA,
    'index: HUMILLO VERDE CONTINUO desde las manchas durante todo el poder')
# r90 · CALABAZA PROCEDURAL GARANTIZADA
CHK('_calabazaProcedural' in PLA and 'LatheGeometry' in PLA and 'TorusGeometry' in PLA,
    'index: calabaza PROCEDURAL (lathe costillas + rabo + zarcillo — pipeline del trofeo)')
CHK('_pumpkinGet' not in PLA and 'C.fallbackT' not in PLA and 'pumpkin' not in PLA,
    'index: GLB de la calabaza RETIRADO del runtime (sin esperas, sin swaps)')
CHK('esProc: true, explotada: false' in PLA, 'index: cuerpo nace EN EL DISPARO (la bola JAMÁS sin cuerpo)')
CHK('6.0 : 0' not in PLA and '_esperaCuerpo' not in PLA, 'index: aviso de superpoder sin congelación extra (warn normal)')
# r90 · MAPA CON SU COLOR
CHK('textura.colorSpace = THREE.SRGBColorSpace' in PLA and 'getMaxAnisotropy' in PLA,
    'index: mapa con SRGBColorSpace + anisotropía (adiós al lavado)')
CHK('this.marco' in PLA and 'marco.geometry.dispose()' in PLA, 'index: MARCO de anclaje intacto (regresión r89)')
CHK('for (let i = 0; i < 48; i++)' in PLA, 'index: moscas AL DOBLE (regresión r89)')
CHK(os.path.exists(os.path.join(HAL, 'assets/mapa.webp')) and os.path.getsize(os.path.join(HAL, 'assets/mapa.webp')) > 100000,
    'assets: mapa.webp del dueño presente (%d B)' % os.path.getsize(os.path.join(HAL, 'assets/mapa.webp')))

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
    pg.wait_for_timeout(15000)
    try:
        pg.evaluate("() => { const o = document.getElementById('overlay'); if (o) o.style.display = 'none'; }")
    except Exception:
        pass

    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), g = ctrl.game;
      const out = { vive: true, state: g.rules ? g.rules.state : null };
      try {
        const mp = ctrl.mapa.plane;
        out.mapa = { x: +mp.position.x.toFixed(3), y: +mp.position.y.toFixed(2), rotY: +mp.rotation.y.toFixed(4) };
        out.mapaCS = (mp.material && mp.material.map) ? mp.material.map.colorSpace : null;
        out.mapaAniso = (mp.material && mp.material.map) ? mp.material.map.anisotropy : null;
      } catch (e) { out.mapaErr = '' + e; }
      return out;
    }""")
    CHK(st.get('vive') is True, 'halloween vivo')
    if not st.get('vive'):
        print(json.dumps(st, indent=1)); srv.shutdown(); b.close(); sys.exit(1)
    # r90 · EL MAPA YA NO ESTÁ LAVADO: colorSpace SRGB EN LA TEXTURA VIVA
    CHK(st.get('mapaCS') == 'srgb', 'mapa: textura VIVA en SRGB (colorSpace=%s — antes lineal=desaturado)' % st.get('mapaCS'))
    m = st.get('mapa') or {}
    CHK(abs(m.get('x', 0) + 3.043) < 0.002 and abs(m.get('y', 0) - 1.66) < 0.01,
        'mapa: posición intacta (x=%s y=%s)' % (m.get('x'), m.get('y')))
    CHK(abs((m.get('rotY') or 0) - 1.5708) < 1e-3, 'mapa: PARALELO a la pared (rotY=%s)' % m.get('rotY'))

    # ARTE SONORO DECODIFICABLE en este navegador (perfil del casco)
    dec = pg.evaluate("""async () => {
      const files = ['zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3', 'risas.mp3', 'midnight_volley.mp3'];
      const actx = new (window.AudioContext || window.webkitAudioContext)();
      const out = {};
      for (const f of files) {
        try {
          const r = await fetch('/championships/halloween/assets/' + f);
          const ab = await r.arrayBuffer();
          const buf = await actx.decodeAudioData(ab.slice(0));
          out[f] = { ok: true, dur: +buf.duration.toFixed(2), rate: buf.sampleRate };
        } catch (e) { out[f] = { ok: false, err: '' + e }; }
      }
      return out;
    }""")
    for f in ['zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3', 'risas.mp3', 'midnight_volley.mp3']:
        d = (dec or {}).get(f) or {}
        CHK(d.get('ok') is True and d.get('rate') == 44100,
            'audio: %s decodifica a 44100 Hz (dur %s s)' % (f, d.get('dur')))

    # ---------------- MANOS: sin montículo + colisión CCD REAL ------------
    manos = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
      const D = window.__PP_CORE.DIMS;
      try { motor._cerrar(); } catch (e) {}
      const p = motor.lista.find(q => q.kind === 'mano');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const M = motor.ctx.mano; if (!M) return { err: 'sin ctx.mano' };
      // DETERMINISMO: esperamos a las 3 texturas (pedir → cache) antes de
      // ceder el paso — el spawn exige M.tex.length
      for (let i = 0; i < 100 && M.tex.length < 3; i++) await new Promise(r => setTimeout(r, 100));
      for (let s = 0; s < 2; s++) motor.update(0.5, motor.game.rules);   // spawn + subir + arriba (t=1,0 s: EN 'arriba')
      const impl2 = H.pods.mano;
      if (!M.vivos.length) { impl2._spawn(g, M); motor.update(0.5, motor.game.rules); }
      const MON = 0.17 + 0.03, BORDE = 0.07;
      const MX = Math.max(0.05, D.tableHalfWidth - MON - BORDE);
      const MZ = Math.max(0.05, D.tableHalfLength - MON - BORDE);
      const vivos = M.vivos.map(v => ({ x: +v.mano.position.x.toFixed(3),
        z: +(v.mano.position.z - D.tableCenterZ).toFixed(3),
        y: +v.mano.position.y.toFixed(3), fase: v.fase, sy: +v.mano.scale.y.toFixed(2),
        sinMont: (v.mont === undefined) }));
      // ---- COLISIÓN CCD REAL (rallye simulado: la bola ATRAVIESA la mano) --
      const stPrev = g.rules.state;
      g.rules.state = 'rally';
      let golpe = null, porDetras = null;
      const v0 = M.vivos[0];
      if (v0) {
        const vel = { x: 0, y: 0, z: -4.0 };
        g.ball.pos.set(v0.mano.position.x, D.tableTopY + 0.10, v0.mano.position.z + 0.45);
        g.ball.vel.set(vel.x, vel.y, vel.z);
        for (let s = 0; s < 14 && !v0.golpeada; s++) {
          g.ball.pos.x += vel.x * 0.02; g.ball.pos.y += vel.y * 0.02; g.ball.pos.z += vel.z * 0.02;
          motor.update(0.02, motor.game.rules);
        }
        golpe = { ok: v0.golpeada, velZ: +g.ball.vel.z.toFixed(2), velY: +g.ball.vel.y.toFixed(2),
                  trocitos: M.trocitos.length, fase: v0.fase };
      }
      // POR DETRÁS: nueva mano, aproximación opuesta
      M.t = 99; M.prox = 99;                    // no más spawns automáticos
      const impl = H.pods.mano; impl._spawn(g, M);
      for (let s = 0; s < 4; s++) motor.update(0.5, motor.game.rules);
      const v1 = M.vivos.find(q => !q.golpeada && (q.fase === 'subir' || q.fase === 'arriba'));
      if (v1) {
        const vel = { x: 0, y: 0, z: 4.0 };
        g.ball.pos.set(v1.mano.position.x, D.tableTopY + 0.10, v1.mano.position.z - 0.45);
        g.ball.vel.set(vel.x, vel.y, vel.z);
        for (let s = 0; s < 14 && !v1.golpeada; s++) {
          g.ball.pos.x += vel.x * 0.02; g.ball.pos.y += vel.y * 0.02; g.ball.pos.z += vel.z * 0.02;
          motor.update(0.02, motor.game.rules);
        }
        porDetras = { ok: v1.golpeada, velY: +g.ball.vel.y.toFixed(2) };
      }
      g.rules.state = stPrev;
      try { motor._cerrar(); } catch (e) {}
      return { MX: +MX.toFixed(3), MZ: +MZ.toFixed(3), vivos, golpe, porDetras };
    }""")
    if 'err' in (manos or {}):
        CHK(False, 'mano: ctx vivo (%s)' % manos['err'])
    else:
        viv = manos.get('vivos') or []
        CHK(len(viv) >= 1 and all(v['sinMont'] for v in viv), 'mano: manos SIN montículo (v.mont inexistente)')
        if viv:
            dentro = all(abs(v['x']) <= manos['MX'] + 1e-6 and abs(v['z']) <= manos['MZ'] + 1e-6 for v in viv)
            CHK(dentro, 'mano: TODAS dentro del tablero (|x|≤%s, |z|≤%s)' % (manos['MX'], manos['MZ']))
            pares = [((viv[i]['x'], viv[i]['z']), (viv[j]['x'], viv[j]['z']))
                     for i in range(len(viv)) for j in range(i + 1, len(viv))
                     if ((viv[i]['x'] - viv[j]['x']) ** 2 + (viv[i]['z'] - viv[j]['z']) ** 2) < 0.62 * 0.62 - 1e-6]
            CHK(not pares, 'mano: SIN solape (separación ≥ 0,62 m)')
        gk = manos.get('golpe') or {}
        CHK(gk.get('ok') is True, 'mano: la bola QUE ATRAVIESA choca (CCD por segmento)')
        CHK(gk.get('velZ') == 0 and abs((gk.get('velY') or 0) + 0.4) < 1e-6,
            'mano: la bola SE PARA Y CAE (vel 0,-0.4) tras el choque')
        CHK((gk.get('trocitos') or 0) >= 6 and gk.get('fase') == 'golpeada',
            'mano: la mano SE DESTROZA en trocitos (fase=%s, trocitos=%s)' % (gk.get('fase'), gk.get('trocitos')))
        pd = manos.get('porDetras') or {}
        CHK(pd.get('ok') is True, 'mano: el choque POR DETRÁS también registra (caja local con grosor)')

    # ---------------- GELATINA: desfase cero + humillo continuo -----------
    pg.evaluate("""() => { const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; try { motor._cerrar(); } catch (e) {} }""")
    gel = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
      const D = window.__PP_CORE.DIMS;
      const p = motor.lista.find(q => q.kind === 'gelatina');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const powerT0 = +motor.powerT.toFixed(1);                          // r90: 12 s AL LANZAR
      for (let s = 0; s < 6; s++) motor.update(0.1, motor.game.rules);
      const G = motor.ctx.gelatina; if (!G) return { err: 'sin ctx.gelatina' };
      const BORDE = 0.07;
      const manchas = G.manchas.map(m => ({ x: +m.position.x.toFixed(3), z: +(m.position.z - D.tableCenterZ).toFixed(3), tam: +m.userData.tam.toFixed(3) }));
      let dentro = true;
      for (const mm of manchas) {
        const circ = (mm.tam / 2) * 1.4142 + 0.012 + BORDE;
        if (Math.abs(mm.x) + circ > D.tableHalfWidth + 1e-6 || Math.abs(mm.z) + circ > D.tableHalfLength + 1e-6) dentro = false;
      }
      let sep = true;
      for (let i = 0; i < manchas.length; i++) for (let j = i + 1; j < manchas.length; j++) {
        const a = manchas[i], bb = manchas[j];
        if (Math.hypot(a.x - bb.x, a.z - bb.z) < (a.tam + bb.tam) * 0.42 + 0.02) sep = false;
      }
      // HUMILLO CONTINUO: sólo con el paso del tiempo (bola lejos, sin tocar)
      const n0 = G.humo.length;
      for (let s = 0; s < 30; s++) motor.update(0.1, motor.game.rules);   // 3 s de poder
      const continuo = { n0, n1: G.humo.length };
      // BORDE de la mancha: la bola toca el CANTO del cuadrado (antes el
      // círculo salado lo perdía = el «desfase» que veía el dueño).
      // La bola se RE-ESTACIONA en su reposo (la prueba de MANOS pudo
      // dejarla cayendo con velocidad)
      const b = g.ball;
      b.pos.set(0, D.tableTopY + D.ballRadius, D.tableCenterZ + 0.45);
      if (b.vel) b.vel.set(0, 0, 0);
      const m0 = G.manchas[0];
      const borde = (m0.userData.tam / 2) - 0.015;
      m0.position.set(b.pos.x + borde, m0.position.y, b.pos.z);
      for (let s = 0; s < 4; s++) motor.update(0.1, motor.game.rules);
      const contaminadaBorde = G.contaminada;
      const col = g.ballMesh && g.ballMesh.material ? g.ballMesh.material.color.getHexString() : '';
      // HUMO al botar (regresión r89)
      G.prevVy = -1.5; b.vel.y = 1.2;
      for (let s = 0; s < 4; s++) motor.update(0.1, motor.game.rules);
      let sprites = 0;
      g.scene.traverse((o) => { if (o.isSprite) sprites++; });
      return { n: manchas.length, dentro, sep, powerT0, continuo, contaminadaBorde, col, sprites };
    }""")
    if 'err' in (gel or {}):
        CHK(False, 'gelatina: %s' % gel['err'])
    else:
        CHK(gel.get('n') == 5, 'gelatina: 5 manchas (%s)' % gel.get('n'))
        CHK(gel.get('dentro') is True, 'gelatina: TODAS dentro del tablero')
        CHK(gel.get('sep') is True, 'gelatina: SIN solape entre manchas')
        co = gel.get('continuo') or {}
        CHK((co.get('n1') or 0) > (co.get('n0') or 0), 'gelatina: HUMILLO CONTINUO sin tocar nada (%d→%d efluvios en 3 s)' % (co.get('n0') or 0, co.get('n1') or 0))
        CHK(gel.get('contaminadaBorde') is True, 'gelatina: el BORDE de la mancha SÍ contamina (cuadrado exacto — sin desfase)')
        CHK(gel.get('col') == '39ff14', 'gelatina: bola VERDE FOSFORITO (%s)' % gel.get('col'))
        CHK((gel.get('sprites') or 0) > 0, 'gelatina: humo en botes (ráfaga r89 intacta, %s sprites)' % gel.get('sprites'))
        CHK(abs((gel.get('powerT0') or 0) - 12.0) < 0.1, 'gelatina: efecto de 12 s al lanzar (powerT0=%s)' % gel.get('powerT0'))

    # ---------------- CALABAZA: cuerpo procedural EN ESCENA ---------------
    pg.evaluate("""() => { const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; try { motor._cerrar(); } catch (e) {} }""")
    cal = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
      const D = window.__PP_CORE.DIMS;
      const g0 = D.gravity;
      const p = motor.lista.find(q => q.kind === 'calabaza');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const C = motor.ctx.calabaza; if (!C) return { err: 'sin ctx.calabaza' };
      const cuerpoAlInstante = !!C.gltf && C.gltf.parent === g.scene;   // r90: DESDE EL DISPARO
      let geos = [];
      if (C.gltf) C.gltf.traverse((o) => { if (o.isMesh && geos.indexOf(o.geometry.type) < 0) geos.push(o.geometry.type); });
      for (let s = 0; s < 10; s++) motor.update(0.1, motor.game.rules);
      const out = { grav: +D.gravity.toFixed(3), g0: +g0.toFixed(3) };
      out.cuerpoAlInstante = cuerpoAlInstante;
      out.geos = geos;
      out.esProc = !!C.esProc;
      out.visible = C.gltf ? C.gltf.visible : null;
      out.bolaOculta = g.ballMesh ? !g.ballMesh.visible : null;
      out.alinea = C.gltf ? +C.gltf.position.distanceTo(g.ball.pos).toFixed(4) : null;
      out.tam = C.gltf ? null : null;
      C.t = C.dur - 0.56;
      for (let s = 0; s < 4; s++) motor.update(0.1, motor.game.rules);
      out.explotada = C.explotada;
      out.bolaVuelve = g.ballMesh ? g.ballMesh.visible : null;
      return out;
    }""")
    if 'err' in (cal or {}):
        CHK(False, 'calabaza: %s' % cal['err'])
    else:
        CHK(abs(cal['grav'] - cal['g0']) < 1e-6, 'calabaza: gravedad INTACTA (peso estándar %s)' % cal['grav'])
        CHK(cal.get('cuerpoAlInstante') is True, 'calabaza: CUERPO EN ESCENA DESDE EL DISPARO (sin esperas de GLB)')
        CHK((cal.get('geos') or []).count('LatheGeometry') > 0, 'calabaza: cuerpo de LATHE con costillas (%s)' % '+'.join(cal.get('geos') or []))
        CHK(cal.get('visible') is True, 'calabaza: VISIBLE (nunca más invisible en el casco)')
        CHK(cal.get('bolaOculta') is True, 'calabaza: la bola se OCULTA (nunca dos cuerpos)')
        CHK(cal.get('alinea') is not None and cal.get('alinea') < 0.01, 'calabaza: centrada en el CENTRO de la bola (Δ=%s)' % cal.get('alinea'))
        CHK(cal.get('explotada') is True, 'calabaza: ESTALLA al final de la vida')
        CHK(cal.get('bolaVuelve') is True, 'calabaza: la bola VUELVE en el estallido')

    # Capturas: sala del jugador + mapa con el arte nuevo saturado
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      try { H.ctrl().poderes._cerrar(); } catch (e) {}
      g.camera.position.set(1.35, 1.55, 0.35);
      g.camera.lookAt(-0.2, 1.45, -2.2);
    }""")
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r90_sala.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.9, 1.62, -0.4);
      g.camera.lookAt(-3.043, 1.66, -1.9);
    }""")
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r90_mapa.png'))
    print('· capturas r90 escritas')

    if errs:
        print('ERRORES DE PÁGINA:', errs[:6])
        CHK(False, 'sin pageerrors (%d)' % len(errs))
    else:
        CHK(True, 'sin pageerrors')
    b.close()
srv.shutdown()

print('== RESUMEN ==')
print('OK %d / FALLO %d' % (len(OK), len(FAIL)))
for f in FAIL:
    print('  ✗', f)
sys.exit(0 if not FAIL else 1)
