#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r88_v3680.py — capa de QA en vivo de la ronda 88 (V3.6.80-SDK6).
Informe del dueño tras V3.6.79: mapa invisible en la pared izquierda,
zombi a reanclar a la mesa + pose idle nueva, mano/gelatina fuera del
tablero, mano bajo la tierra, calabaza injugable (reescrita: centrada,
gira como la bola, pudre y ESTALLA con CHOFFF), gelatina con física
normal + humo al botar, cartel perdido en la pared, bola con botes y
ruido infinito al arrancar la escena.
Estática (manifest/index.js/core) + RUNTIME determinista (pasos manuales
de motor.update: el rAF del headless corre a ~1 tick/s con SwiftShader).
"""
import os, sys, time, functools, hashlib, json, math
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8765
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(PUB, 'championships/halloween/manifest.json')))
CHK(man.get('cartel', {}).get('oculto') is True, 'manifest: cartel.oculto=true (cartel de bienvenida RETIRADO)')
mp = man.get('mapa', {})
CHK(abs(mp.get('rotY', 0) - math.pi / 2) < 0.01, 'manifest: mapa rotY=π/2 (pared izquierda, normativa)')
CHK(abs(mp.get('pos', [9])[0] + 3.03) < 0.02, 'manifest: mapa x=-3.03 (pared izquierda)')
PLA = open(os.path.join(PUB, 'championships/halloween/index.js'), encoding='utf-8').read()
CHK('DIMS.tableHalfWidth) || 0.7625) + 0.69' in PLA, 'index: zombi anclado a la MESA (canto derecho +0,69)')
CHK('if (c.oculto) return null;' in PLA, 'index: construirCartel respeta cartel.oculto')
CHK('mano.renderOrder = 4' in PLA and 'm.renderOrder = 5' in PLA, 'index: mano (4) POR DELANTE del montículo (3), trocitos (5)')
CHK('MX = Math.max(0.05, ((DIMS.tableHalfWidth != null)' in PLA, 'index: mano spawn DENTRO del tablero (canto − radio)')
CHK('const circ = (tam / 2) * 1.4142' in PLA, 'index: gelatina manchas con radio CIRCUNSCRITO')
CHK('_chofff(game, b.pos.x)' in PLA, 'index: CHOFFF en la mancha pisada')
CHK('_humoVerdeR88(game, b.pos, 18)' in PLA, 'index: EXPLOSIÓN de humo verde al botar (18 sprites)')
CHK('DIMS.gravity = G.grav0 * 3.0' not in PLA, 'index: gelatina SIN peso ×3 (física de la bola normal)')
CHK('b.vel.x *= (1 - 0.35 * dt)' not in PLA, 'index: gelatina SIN frenado (física normal)')
CHK('C.gltf.quaternion.copy(game.ballMesh.quaternion)' in PLA, 'index: calabaza GIRA COMO LA BOLA (mismo quaternion)')
CHK('C.gltf.position.copy(b.pos)' in PLA, 'index: calabaza centrada en el CENTRO de la bola')
CHK('C.t >= C.dur - 0.55' in PLA and '_trozoAl(game, b.pos' in PLA, 'index: calabaza ESTALLA en trozos 0,55 s antes del cierre')
CHK('_preparaCuerpoR88' in PLA and '_PODRE_R88' in PLA, 'index: pudrición por instancia (materiales clonados)')
CHK('_pasoTrozosR88(dt, this.game)' in PLA, 'index: trozos/humo con vida FUERA del poder (tick global)')
CORE = open(os.path.join(RAIZ, 'src/game/core/c12_pingponggame.js'), encoding='utf-8').read()
CHK("state === 'champtest' && !holdLock" in CORE, 'core: bola APARCADA e INERTA en la sala de campeonato (champtest)')
idle_sha = hashlib.sha256(open(os.path.join(PUB, 'championships/halloween/assets/idle.webp'), 'rb').read()).hexdigest()[:12]
upl_sha = hashlib.sha256(open(os.path.join(RAIZ, 'scripts/_r88_idle_anterior.webp'), 'rb').read()).hexdigest()[:12]
CHK(idle_sha != upl_sha, 'assets: idle.webp SUSTITUIDA (arte nuevo del dueño, sha %s)' % idle_sha)

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
        print('· clic JUGAR EN VR')
    except Exception:
        pg.mouse.click(640, 600)
        print('· clic centro')
    pg.wait_for_timeout(13000)

    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), man = H.man(), g = ctrl.game;
      const out = { vive: true, state: g.rules ? g.rules.state : null };
      out.cartelNull = ctrl.cartel === null;
      try {
        const n = ctrl.rival.r.node;
        out.zombi = [+n.position.x.toFixed(3), +n.position.y.toFixed(3), +n.position.z.toFixed(3)];
        let p = n; out.zombiEnEscena = false;
        while (p) { if (p === g.scene) { out.zombiEnEscena = true; break; } p = p.parent; }
      } catch (e) { out.zombiErr = '' + e; }
      try {
        const mp = ctrl.mapa.plane;
        out.mapa = { x: +mp.position.x.toFixed(3), rotY: +mp.rotation.y.toFixed(3),
                     y: +mp.position.y.toFixed(2), w: +mp.geometry.parameters.width.toFixed(2),
                     texCargada: !!(mp.material.map && mp.material.map.image &&
                                    mp.material.map.image.width > 0) };
      } catch (e) { out.mapaErr = '' + e; }
      out.bola = { pos: g.ball ? [+g.ball.pos.x.toFixed(3), +g.ball.pos.y.toFixed(3), +g.ball.pos.z.toFixed(3)] : null,
                   vel: g.ball ? +Math.hypot(g.ball.vel.x, g.ball.vel.y, g.ball.vel.z).toFixed(4) : null };
      g.events.length = 0;
      return out;
    }""")
    CHK(st.get('vive') is True, 'halloween vivo')
    if not st.get('vive'):
        print(json.dumps(st, indent=1)); srv.shutdown(); b.close(); sys.exit(1)
    CHK(st.get('cartelNull') is True, 'CARTEL de bienvenida AUSENTE (null — nada en la pared)')
    z = st.get('zombi') or [0, 0, 0]
    CHK(st.get('zombiEnEscena') is True, 'zombi EN el grafo de escena')
    CHK(abs(z[0] - 1.4525) < 0.01, 'zombi anclado a la MESA, algo más a la derecha (x=%.3f, antes 1.26)' % z[0])
    CHK(abs(z[2] + 3.30) < 0.01, 'zombi referido a la mesa (z=%.2f = mesa − 1,70)' % z[2])
    CHK(abs(z[1] - 1.075) < 0.01, 'zombi con los pies en el suelo (y=%.3f)' % z[1])
    m = st.get('mapa') or {}
    CHK(m.get('x') == -3.03 and abs((m.get('rotY') or 0) - 1.571) < 0.01,
        'mapa EN la pared izquierda (x=%s rotY=%s)' % (m.get('x'), m.get('rotY')))
    CHK(m.get('texCargada') is True, 'mapa con SU TEXTURA cargada (no un cartel en blanco)')

    # bola aparcada: 2 s de escucha sin un solo evento de mesa (cero botes/ruido)
    evs = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      await new Promise(r => setTimeout(r, 2000));
      return { n: g.events.filter(e => e.type === 'table').length,
               pos: [+g.ball.pos.x.toFixed(3), +g.ball.pos.y.toFixed(3), +g.ball.pos.z.toFixed(3)],
               vel: +Math.hypot(g.ball.vel.x, g.ball.vel.y, g.ball.vel.z).toFixed(4),
               state: g.rules.state,
               xr: !!(g.renderer && g.renderer.xr && g.renderer.xr.isPresenting) };
    }""")
    CHK(evs.get('n') == 0, 'cero BOTES en 2 s de sala (antes: goteo de «pock» infinito)')
    # En 2D (xr=false) el parque de portada (cz+0,25) pisa al de champtest
    # (cz+0,45) cada frame — en el casco XR manda el de champtest (estática ✓).
    # Lo que importa al dueño: bola QUIETA, SIN ruido, en champtest.
    v = evs.get('vel')
    CHK(v is not None and v == 0 and evs.get('state') == 'champtest',
        'bola INERTA (vel=0) en champtest (xr=%s, pos=%s)' % (evs.get('xr'), evs.get('pos')))

    # ------------- CICLO DE LOS 4 PODERES (pasos MANUALES, rAF a 1 tick/s) ----
    res = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const motor = ctrl.poderes;
      const D = window.__PP_CORE.DIMS;
      const HW = D.tableHalfWidth, HL = D.tableHalfLength, cz = D.tableCenterZ, ty = D.tableTopY;
      const pasoN = async (n, dt) => { for (let i = 0; i < n; i++) motor.update(dt || 0.05); await new Promise(r => setTimeout(r, 4)); };
      const cuenta = (f) => { let n = 0; g.scene.traverse(o => { try { if (f(o)) n++; } catch (e) {} }); return n; };
      const out = {};
      // 1) MANO: spawns reales — montículo SIEMPRE dentro del tablero + orden
      try {
        const p = motor.lista.find(p => p.kind === 'mano');
        motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
        // el primer spawn llega a prox ≈ 0,35+rand(2,0,2,5) — pasamos HASTA ver vivo
        let guard = 0;
        while (guard++ < 160) { motor.update(0.05); if (motor.ctx.mano && motor.ctx.mano.vivos.length >= 1) { motor.update(0.05); break; } }
        await new Promise(r => setTimeout(r, 4));
        const M = motor.ctx.mano;
        let fuera = 0, conOrden = 0;
        for (const v of M.vivos) {
          const half = 0.23;
          if (Math.abs(v.mont.position.x) > HW - half - 0.005 ||
              Math.abs(v.mont.position.z - cz) > HL - half - 0.005) fuera++;
          if (v.mano && v.mano.renderOrder === 4 && v.mont.renderOrder === 3) conOrden++;
        }
        out.mano = { vivos: M.vivos.length, fuera, conOrden };
      } catch (e) { out.manoErr = '' + e; }
      try { motor._cerrar(); motor.cd = 0; motor.pendT = 0; motor.pend = null; } catch (e) {}
      // 2) CALABAZA: centrado EXACTO, giro = bola, pudrición y ESTALLIDO
      try {
        const p = motor.lista.find(p => p.kind === 'calabaza');
        motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
        await pasoN(10);
        const C = motor.ctx.calabaza;
        if (C && C.gltf) {
          const b = g.ball;
          const off = Math.hypot(C.gltf.position.x - b.pos.x, C.gltf.position.y - b.pos.y, C.gltf.position.z - b.pos.z);
          const bolaOculta = !g.ballMesh.visible;      // ANTES del estallido
          g.ballMesh.rotation.set(0.4, 0.7, 0.1);      // gira la bola: la calabaza debe seguirle
          await pasoN(2);
          const qd = Math.abs(C.gltf.quaternion.x - g.ballMesh.quaternion.x) +
                     Math.abs(C.gltf.quaternion.y - g.ballMesh.quaternion.y) +
                     Math.abs(C.gltf.quaternion.z - g.ballMesh.quaternion.z);
          const col0 = C.mats.length ? '#' + C.mats[0].m.color.getHexString() : null;
          C.t = C.dur * 0.5;                    // mitad de vida → tinte intermedio
          await pasoN(2);
          const colMid = C.mats.length ? '#' + C.mats[0].m.color.getHexString() : null;
          const tetra0 = cuenta(o => o.isMesh && o.geometry && o.geometry.type === 'TetrahedronGeometry');
          C.t = C.dur - 0.20;                   // tramo final → estallido
          await pasoN(8);                       // 0,4 s
          out.calabaza = {
            cuerpo: true, offsetCentro: off, giroSigue: qd,
            bolaOcultaConCalabaza: bolaOculta,
            col0, colMid,
            explotada: C.explotada === true,
            trozosNuevos: cuenta(o => o.isMesh && o.geometry && o.geometry.type === 'TetrahedronGeometry') - tetra0,
            bolaVuelta: g.ballMesh.visible === true,
          };
        } else out.calabaza = { cuerpo: false };
      } catch (e) { out.calabazaErr = '' + e; }
      try { motor._cerrar(); motor.cd = 0; motor.pendT = 0; motor.pend = null; } catch (e) {}
      // 3) GELATINA: manchas dentro, física INTACTA, contamina (CHOFFF), humo al botar
      try {
        const grav0 = D.gravity;
        const p = motor.lista.find(p => p.kind === 'gelatina');
        motor.cd = 0; motor.powerT = 0; motor.pend = p; motor.pendT = 0.01; motor._lanzar();
        await pasoN(6);
        const G = motor.ctx.gelatina;
        if (G && G.manchas.length) {
          let fuera = 0;
          for (const m of G.manchas) {
            const half = m.geometry.parameters.width / 2 * 1.4142;
            if (Math.abs(m.position.x) > HW - half + 0.005 ||
                Math.abs(m.position.z - cz) > HL - half + 0.005) fuera++;
          }
          const m0 = G.manchas[0];            // la bola cae SOBRE una mancha real
          g.ball.pos.set(m0.position.x, ty + D.ballRadius + 0.02, m0.position.z);
          g.ball.vel.set(0, -1.0, 0);
          await pasoN(6);
          const verde = '#' + g.ballMesh.material.color.getHexString();
          const sprites0 = cuenta(o => o.isSprite);
          g.ball.pos.set(0.1, ty + 0.06, cz + 0.2);   // BOTE sobre la mesa
          g.ball.vel.set(0.2, -3.2, 0.1);
          await pasoN(2);
          g.ball.vel.y = 2.4;                 // inversión de vy = bote
          await pasoN(4);
          out.gelatina = {
            manchas: G.manchas.length, fuera,
            gravAntes: +grav0.toFixed(3), gravDespues: +D.gravity.toFixed(3),
            fisicaIntacta: Math.abs(D.gravity - grav0) < 1e-9,
            verde, chofffContamina: G.contaminada === true,
            humoRafaga: cuenta(o => o.isSprite) - sprites0,
          };
        } else out.gelatina = { manchas: 0 };
      } catch (e) { out.gelatinaErr = '' + e; }
      try { motor._cerrar(); } catch (e) {}
      motor.parar();
      return out;
    }""")
    print(json.dumps(res, indent=1, ensure_ascii=False))
    mn = res.get('mano') or {}
    CHK(mn.get('fuera') == 0 and (mn.get('vivos') or 0) >= 1,
        'MANO: %s montículos vivos, TODOS dentro del tablero (fuera=%s)' % (mn.get('vivos'), mn.get('fuera')))
    CHK(mn.get('conOrden', 0) > 0, 'MANO: mano renderOrder 4 POR DELANTE de la tierra (3)')
    cal = res.get('calabaza') or {}
    CHK(cal.get('cuerpo') is True, 'CALABAZA: cuerpo vivo (GLB o respaldo)')
    oc = cal.get('offsetCentro')
    CHK(oc is not None and oc < 0.02, 'CALABAZA: centrada en el CENTRO EXACTO de la bola (off=%s)' % oc)
    gs = cal.get('giroSigue')
    CHK(gs is not None and gs < 0.02, 'CALABAZA: gira COMO LA BOLA (dif tras giro nuevo=%s)' % gs)
    CHK(cal.get('bolaOcultaConCalabaza') is True, 'CALABAZA: bola normal OCULTA mientras la calabaza vive (nunca las dos)')
    CHK(cal.get('explotada') is True and (cal.get('trozosNuevos') or 0) >= 8 and cal.get('bolaVuelta') is True,
        'CALABAZA: ESTALLA en trozos (%s) y la bola normal VUELVE' % cal.get('trozosNuevos'))
    CHK(cal.get('col0') != cal.get('colMid'), 'CALABAZA: PUDRICIÓN (color %s → %s)' % (cal.get('col0'), cal.get('colMid')))
    ge = res.get('gelatina') or {}
    CHK(ge.get('fuera') == 0 and (ge.get('manchas') or 0) == 5,
        'GELATINA: 5 manchas TODAS dentro del tablero (fuera=%s)' % ge.get('fuera'))
    CHK(ge.get('fisicaIntacta') is True, 'GELATINA: física INTACTA (gravedad %s == %s, sin peso ×3)' % (ge.get('gravDespues'), ge.get('gravAntes')))
    CHK(ge.get('verde') == '#39ff14', 'GELATINA: bola VERDE FOSFORITO (%s)' % ge.get('verde'))
    CHK(ge.get('chofffContamina') is True, 'GELATINA: la mancha se PISA y contamina (con CHOFFF)')
    CHK((ge.get('humoRafaga') or 0) >= 12, 'GELATINA: EXPLOSIÓN de humo verde al botar (%s sprites nuevos)' % ge.get('humoRafaga'))

    # capturas: sala normal + cámara a la PARED IZQUIERDA (el mapa) + zombi
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_halloween_sala.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const cam = g.camera;
      cam.position.set(0, 1.5, 0.6);
      cam.lookAt(-3.03, 1.45, -1.9);
    }""")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_halloween_mapa.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const cam = g.camera;
      cam.position.set(0, 1.5, 0.6);
      cam.lookAt(1.45, 1.1, -3.3);
    }""")
    pg.wait_for_timeout(1200)
    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r88_halloween_zombi.png'))
    CHK(len(errs) == 0, 'cero pageerrors (%s)' % (errs[:2] if errs else 'limpio'))
    b.close()
srv.shutdown()
print('== RESUMEN r88 == OK %d · FALLOS %d' % (len(OK), len(FAIL)))
for f in FAIL: print('  ✗', f)
sys.exit(1 if FAIL else 0)
