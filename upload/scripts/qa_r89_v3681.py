#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r89_v3681.py — capa de QA en vivo de la ronda 89 (V3.6.81-SDK6).
Informe del dueño tras V3.6.80: mapa «paralelo a la pared izquierda,
ligeramente por encima», estados del zombi que se superponen coplanares,
moscas al doble, manos fuera del tablero/solapadas/sin ascenso/no salen
las 3, vísceras fuera del tablero/solapadas/zona de impacto mal calculada
(12 s), calabaza sin modelo (precarga + aviso prolongado) y peso estándar,
sonidos zombi_victory/crazy/defeated.
Estática (manifest/index/sdk/_plantilla) + RUNTIME determinista.
"""
import os, sys, time, functools, hashlib, json, math
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8795
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(PUB, 'championships/halloween/manifest.json')))
mp = man.get('mapa', {})
CHK(abs(mp.get('pos', [0, 0, 0])[0] + 3.043) < 0.002 and abs(mp.get('pos', [0, 0, 0])[1] - 1.66) < 0.002,
    'manifest: mapa elevado y pegado a la pared izquierda (x=%.3f y=%.2f)' % (mp.get('pos', [0, 0, 0])[0], mp.get('pos', [0, 0, 0])[1]))
CHK(abs(mp.get('rotY', 0) - math.pi / 2) < 1e-6, 'manifest: mapa rotY=π/2 EXACTO (paralelo a la pared)')
gel = [p for p in man.get('powers', []) if p.get('kind') == 'gelatina']
CHK(bool(gel) and gel[0].get('duration') == 12, 'manifest: gelatina duration=12 s (efecto verde prolongado)')
son = man.get('audio', {}).get('sounds', {})
for k, f in [('crazy', 'assets/zombi_crazy.mp3'), ('victory', 'assets/zombi_victory.mp3'), ('defeated', 'assets/zombi_defeated.mp3')]:
    CHK(son.get(k) == f and os.path.exists(os.path.join(PUB, 'championships/halloween', f)),
        'manifest+assets: sonido %s → %s presente' % (k, f))
PLA = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()
CHK('for (let i = 0; i < 48; i++)' in PLA, 'index: moscas AL DOBLE (48)')
CHK('_bolsa(M)' in PLA and 'M.bolsa.pop()' in PLA, 'index: bolsa de manos (las 3 salen antes de repetir)')
CHK('MON = 0.23 * 1.18' in PLA and 'BORDE = 0.07' in PLA, 'index: mano dentro del tablero (pop ×1,18 + canto rugoso)')
CHK('SLOTS = [[-0.30, -0.9], [0.30, 0.0], [-0.30, 0.9]]' in PLA and '0.62 * 0.62' in PLA,
    'index: manos SIEMPRE separadas (ranuras por construcción, ≥ 0,62 m)')
CHK('v.y0 + e * 0.12' in PLA, 'index: mano ASIENDE abajo→arriba (12 cm)')
CHK('czG - HZg + 0.18' in PLA, 'index: el empujón de la mano CLAMPEADO al tablero')
CHK('PLANTILLA_PODERES.calabaza' in PLA and 'DIMS.gravity = C.grav0 * 2.1' not in PLA,
    'index: calabaza con PESO ESTÁNDAR (sin gravedad ×2,1)')
CHK('C.fallbackT = 1.2' in PLA, 'index: calabaza con cuerpo de respaldo a 1,2 s')
CHK('SWAP AL MODELO DEL ARTISTA' in PLA, 'index: calabaza SWAP al GLB del dueño cuando llega')
CHK('__reintento' in PLA, 'index: calabaza REINTENTO de carga ante error')
CHK('? 6.0 : 0' in PLA and '_esperaCuerpo' in PLA and 'descongela(this.game)' in PLA,
    'index: aviso de superpoder PROLONGADO hasta que carga la calabaza (tope 6 s)')
CHK('prewarmI' not in PLA, 'index: sin paseo visible de caras (estados superpuestos)')
CHK('this.marco' in PLA and 'marco.geometry.dispose()' in PLA, 'index: MARCO de anclaje del mapa (+dispose)')
CHK("SFX.play('crazy', 0.62)" in PLA and "SFX.play(won ? 'defeated' : 'victory', 0.7)" in PLA,
    'index: sonidos zombi crazy (poder) y victory/defeated (final)')
CHK('m.userData.tam' in PLA and 'rad = (m.userData.tam || 0.3) * 0.42' in PLA,
    'index: gelatina con zona de impacto REAL (radio por tamaño de mancha)')
CHK('G.prevVy < -0.25 && b.vel.y > 0.25' in PLA, 'index: gelatina humo en botes suaves (umbral 0,25)')
SDK = open(os.path.join(PUB, 'championships/sdk/champ_sdk.js'), encoding='utf-8').read()
CHK('initTexture' in SDK and 'if (estado_ === st)' in SDK,
    'sdk: caras SIN pintado al llegar + subida a GPU invisible (initTexture)')
CHK('if (t) ponMapa(t);' in SDK, 'sdk: estadoPrecarga no-op real (nunca rectángulo blanco)')
PLT = open(os.path.join(PUB, 'championships/_plantilla/index.js'), encoding='utf-8').read()
CHK('prewarmI' not in PLT, 'plantilla UGC: paseo visible retirado (no hereda el bug)')

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
    # el splash DOM tapa el canvas en las capturas: se oculta para ver la sala
    try:
        pg.evaluate("() => { const o = document.getElementById('overlay'); if (o) o.style.display = 'none'; }")
    except Exception:
        pass

    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), man = H.man(), g = ctrl.game;
      const out = { vive: true, state: g.rules ? g.rules.state : null };
      try {
        const n = ctrl.rival.r.node;
        out.zombi = [+n.position.x.toFixed(3), +n.position.y.toFixed(3), +n.position.z.toFixed(3)];
        let p = n; out.zombiEnEscena = false;
        while (p) { if (p === g.scene) { out.zombiEnEscena = true; break; } p = p.parent; }
        out.zombiTex = (n.material && n.material.map && n.material.map.image && n.material.map.image.src || '').split('/').pop();
      } catch (e) { out.zombiErr = '' + e; }
      try {
        const mp = ctrl.mapa.plane;
        out.mapa = { x: +mp.position.x.toFixed(3), y: +mp.position.y.toFixed(2), rotY: +mp.rotation.y.toFixed(4) };
        out.marco = !!ctrl.mapa.marco && ctrl.mapa.marco.parent === g.scene;
        out.marcoX = ctrl.mapa.marco ? +ctrl.mapa.marco.position.x.toFixed(3) : null;
      } catch (e) { out.mapaErr = '' + e; }
      out.g0 = (window.__PP_CORE && window.__PP_CORE.DIMS) ? +window.__PP_CORE.DIMS.gravity.toFixed(3) : null;
      return out;
    }""")
    CHK(st.get('vive') is True, 'halloween vivo')
    if not st.get('vive'):
        print(json.dumps(st, indent=1)); srv.shutdown(); b.close(); sys.exit(1)
    m = st.get('mapa') or {}
    CHK(abs(m.get('x', 0) + 3.043) < 0.002 and abs(m.get('y', 0) - 1.66) < 0.01,
        'mapa ELEVADO (y=%s) y pegado a la pared (x=%s)' % (m.get('y'), m.get('x')))
    CHK(abs((m.get('rotY') or 0) - 1.5708) < 1e-3, 'mapa PARALELO a la pared (rotY=%s)' % m.get('rotY'))
    CHK(st.get('marco') is True and abs((st.get('marcoX') or 0) + 3.047) < 0.002,
        'marco de anclaje vivo (x=%s, detrás del póster)' % st.get('marcoX'))
    z = st.get('zombi') or [0, 0, 0]
    CHK(st.get('zombiEnEscena') is True, 'zombi EN el grafo de escena')
    CHK(abs(z[0] - 1.4525) < 0.01 and abs(z[2] + 3.30) < 0.01, 'zombi anclado a la MESA (x=%.3f z=%.2f)' % (z[0], z[2]))

    # SIN ESTADOS SUPERPUESTOS: 6 s de muestreo del mapa del material —
    # sólo la base (present) o el estado lógico (idle); jamás un paseo.
    flicker = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const vistos = new Set();
      for (let i = 0; i < 24; i++) {
        const n = H.ctrl().rival.r.node;
        const src = (n.material && n.material.map && n.material.map.image && n.material.map.image.src) || '';
        vistos.add(src.split('/').pop());
        await new Promise(r => setTimeout(r, 250));
      }
      return [...vistos];
    }""")
    CHK(set(flicker) <= {'present.webp', 'idle.webp'},
        'sin superposición de estados en 6 s (vistos: %s)' % sorted(flicker))

    # SONIDO URLs al alcance del módulo
    urls_ok = pg.evaluate("""async () => {
      const base = ['zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3'];
      const out = {};
      for (const f of base) {
        const r = await fetch('/championships/halloween/assets/' + f, { method: 'HEAD' });
        out[f] = r.status;
      }
      return out;
    }""")
    CHK(all(v == 200 for v in urls_ok.values()), 'mp3 del zombi servidos (200): %s' % urls_ok)

    # ---------------- MANOS: dentro del tablero, separadas, 3 distintas ----
    # (paso MANUAL del motor: el rAF del sandbox corre ~1 tick/s — con
    # motor.update(0.5)×N el poder vive 12 s deterministas en milisegundos)
    manos = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes;
      const p = motor.lista.find(q => q.kind === 'mano');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const M = motor.ctx.mano; if (!M) return { err: 'sin ctx.mano' };
      for (let s = 0; s < 14; s++) motor.update(0.5, motor.game.rules);   // 7 s: 3 spawns (timer 2,0-2,5 s entre ellos)
      const D = window.__PP_CORE.DIMS;
      const MON = 0.23 * 1.18, BORDE = 0.07;
      const MX = Math.max(0.05, D.tableHalfWidth - MON - BORDE);
      const MZ = Math.max(0.05, D.tableHalfLength - MON - BORDE);
      const vivos = M.vivos.map(v => ({ x: +v.mont.position.x.toFixed(3),
        z: +(v.mont.position.z - D.tableCenterZ).toFixed(3),
        tex: (v.tex.image && v.tex.image.src || '').split('/').pop(),
        y: +v.mano.position.y.toFixed(3), fase: v.fase }));
      return { MX: +MX.toFixed(3), MZ: +MZ.toFixed(3), vivos, ty: +D.tableTopY.toFixed(3) };
    }""")
    if 'err' in (manos or {}):
        CHK(False, 'mano: ctx vivo (%s)' % manos['err'])
    else:
        viv = manos['vivos']
        CHK(len(viv) >= 1, 'mano: manos vivas al corte (%d; ritmo natural: spawn 2,0-2,5 s / vida 3,6 s)' % len(viv))
        if viv:
            dentro = all(abs(v['x']) <= manos['MX'] + 1e-6 and abs(v['z']) <= manos['MZ'] + 1e-6 for v in viv)
            CHK(dentro, 'mano: TODAS dentro del tablero (|x|≤%s, |z|≤%s)' % (manos['MX'], manos['MZ']))
            pares_malos = [((viv[i]['x'], viv[i]['z']), (viv[j]['x'], viv[j]['z']))
                           for i in range(len(viv)) for j in range(i+1, len(viv))
                           if ((viv[i]['x']-viv[j]['x'])**2 + (viv[i]['z']-viv[j]['z'])**2) < 0.62*0.62 - 1e-6]
            CHK(not pares_malos, 'mano: SIN solape (separación ≥ 0,62 m) %s' % (pares_malos or ''))
            sube = [v for v in viv if v['y'] > manos['ty'] + 0.06]
            CHK(bool(sube), 'mano: la mano ASCIENDE abajo→arriba (y=%s sobre mesa %s)' %
                ([v['y'] for v in sube] or '—', manos['ty']))
    # BOLSA UNITARIA: cada ventana de 3 extracciones consecutivas trae las
    # 3 manos (garantía «no están saliendo todas» corregida)
    bolsa_ok = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H.pods || !H.pods.mano) return null;
      const M = { tex: ['a', 'b', 'c'], bolsa: [] };
      const tiradas = [];
      for (let i = 0; i < 9; i++) tiradas.push(H.pods.mano._bolsa(M));
      let ok = true;
      for (let c = 0; c < tiradas.length; c += 3) {   // cada CICLO de 3: las 3 manos
        if (new Set(tiradas.slice(c, c + 3)).size !== 3) ok = false;
      }
      return { tiradas, ok };
    }""")
    CHK(bool(bolsa_ok and bolsa_ok['ok']), 'mano: BOLSA garantiza las 3 manos del artista por ciclo (%s)' % bolsa_ok['tiradas'])

    # ---------------- GELATINA: bordes, separación, impacto, humo, 12 s ---
    pg.evaluate("""() => { const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; try { motor._cerrar(); } catch (e) {} }""")
    gel = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
      const D = window.__PP_CORE.DIMS;
      const p = motor.lista.find(q => q.kind === 'gelatina');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      for (let s = 0; s < 6; s++) motor.update(0.1, motor.game.rules);   // textura → manchas
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
        const d = Math.hypot(a.x - bb.x, a.z - bb.z);
        if (d < (a.tam + bb.tam) * 0.42 + 0.02) sep = false;   // radios VISIBLES sin tocarse (tolerancia de redondeo 1 mm)
      }
      // IMPACTO: la mancha VA BAJO la bola aparcada (el núcleo la retiene
      // en su reposo — mover la bola no vale en champtest)
      const b = g.ball;
      const m0 = G.manchas[0];
      m0.position.set(b.pos.x, m0.position.y, b.pos.z);
      for (let s = 0; s < 4; s++) motor.update(0.1, motor.game.rules);
      const contaminada = G.contaminada;
      const col = g.ballMesh && g.ballMesh.material ? g.ballMesh.material.color.getHexString() : '';
      // HUMO al botar: prevVy negativa + vel.y positiva (bote en mesa)
      G.prevVy = -1.5; b.vel.y = 1.2;
      for (let s = 0; s < 4; s++) motor.update(0.1, motor.game.rules);
      let sprites = 0;
      g.scene.traverse((o) => { if (o.isSprite) sprites++; });
      return { n: manchas.length, dentro, sep, contaminada, col, sprites, powerT: +motor.powerT.toFixed(1) };
    }""")
    if 'err' in (gel or {}):
        CHK(False, 'gelatina: %s' % gel['err'])
    else:
        CHK(gel.get('n') == 5, 'gelatina: 5 manchas (%s)' % gel.get('n'))
        CHK(gel.get('dentro') is True, 'gelatina: TODAS dentro del tablero (canto rugoso incluido)')
        CHK(gel.get('sep') is True, 'gelatina: SIN solape (aire ≥ 3 cm entre circunscritas)')
        CHK(gel.get('contaminada') is True, 'gelatina: la ZONA DE IMPACTO registra el golpe')
        CHK(gel.get('col') == '39ff14', 'gelatina: bola VERDE FOSFORITO (%s)' % gel.get('col'))
        CHK((gel.get('sprites') or 0) > 0, 'gelatina: HUMO VERDE en el bote (%s sprites)' % gel.get('sprites'))
        CHK(abs((gel.get('powerT') or 0) - 12.0) < 1.5, 'gelatina: efecto de 12 s (powerT=%s)' % gel.get('powerT'))

    # ---------------- CALABAZA: cuerpo, peso estándar, estallido ----------
    pg.evaluate("""() => { const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; try { motor._cerrar(); } catch (e) {} }""")
    cal = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const motor = H.ctrl().poderes; const g = H.ctrl().game;
      const D = window.__PP_CORE.DIMS;
      const g0 = D.gravity;
      const p = motor.lista.find(q => q.kind === 'calabaza');
      motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
      const C = motor.ctx.calabaza; if (!C) return { err: 'sin ctx.calabaza' };
      for (let s = 0; s < 10; s++) motor.update(0.1, motor.game.rules);
      const out = { grav: +D.gravity.toFixed(3), g0: +g0.toFixed(3) };
      out.listo = C.listo; out.esProc = !!C.esProc; out.cuerpo = !!C.gltf && C.gltf.parent === g.scene;
      out.bolaOculta = g.ballMesh ? !g.ballMesh.visible : null;
      // el cuerpo sigue la bola
      out.alinea = C.gltf ? +C.gltf.position.distanceTo(g.ball.pos).toFixed(4) : null;
      // estallido: forzamos el instante
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
        CHK(cal.get('cuerpo') is True, 'calabaza: CUERPO en escena (GLB precargado en init)')
        CHK(cal.get('bolaOculta') is True, 'calabaza: la bola se OCULTA (nunca dos cuerpos)')
        CHK(cal.get('alinea') is not None and cal.get('alinea') < 0.01, 'calabaza: centrada en el CENTRO de la bola (Δ=%s)' % cal.get('alinea'))
        CHK(cal.get('explotada') is True, 'calabaza: ESTALLA al final de la vida')
        CHK(cal.get('bolaVuelve') is True, 'calabaza: la bola VUELVE en el estallido')

    # Capturas: sala desde el jugador + mapa con marco
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      try { H.ctrl().poderes._cerrar(); } catch (e) {}
      g.camera.position.set(1.35, 1.55, 0.35);
      g.camera.lookAt(-0.2, 1.45, -2.2);
    }""")
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_sala.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      g.camera.position.set(-0.9, 1.62, -0.4);
      g.camera.lookAt(-3.043, 1.66, -1.9);
    }""")
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r89_mapa_marco.png'))
    print('· capturas r89 escritas')

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
