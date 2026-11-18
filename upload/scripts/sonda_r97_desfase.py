#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonda r97 — desfase calabaza↔bote/golpe del rival en el BUCLE REAL.
Mide (posiciones MUNDO, getWorldPosition) durante un duelo vivo con la
calabaza forzada por el camino real (pend → _lanzar):
  A) rig/world transforms (¿padre distinto?)
  B) calabaza↔ballMesh (mismo frame), calabaza↔ball.pos (¿lag?)
  C) en cada GOLPE real del rival (aiStrikeT crece): hoja↔calabaza
  D) calabazas residuales en escena (Lathe 0xe8720c)
  E) altura de mesa CUSTOM (deslizador r96) repite B/C
  F) fuga del zombi: SFX one-shot vivo tras leaveAll + Hall (arcMute on)
"""
import os, functools, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8817

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

SAMPLER = """() => {
  const g = window.__PP_HALLOWEEN.ctrl().game;
  if (g.__r97Hook) return true;
  g.__r97Hook = true;
  window.__S = [];
  const P = window.__PP_HALLOWEEN.ctrl().poderes;
  const wp = new (g.ballMesh.position.constructor)();
  const sample = () => {
    const C = P && P.ctx && P.ctx.calabaza;
    const rec = {
      t: performance.now(), st: g.rules.state,
      hold: !!g.holdLock,
      strike: g.aiStrikeT,
      rig: [g.rig.position.x, g.rig.position.y, g.rig.position.z],
      ball: [g.ball.pos.x, g.ball.pos.y, g.ball.pos.z],
      mesh: [g.ballMesh.position.x, g.ballMesh.position.y, g.ballMesh.position.z],
      meshVis: g.ballMesh.visible,
    };
    if (C && C.gltf) {
      C.gltf.getWorldPosition(wp);
      rec.calaW = [wp.x, wp.y, wp.z];
      g.ballMesh.getWorldPosition(wp);
      rec.meshW = [wp.x, wp.y, wp.z];
      rec.calaVis = C.gltf.visible;
      rec.expl = !!C.explotada;
    }
    if (g.aiPaddleMesh) {
      g.aiPaddleMesh.getWorldPosition(wp);
      rec.blade = [wp.x, wp.y, wp.z];
    }
    window.__S.push(rec);
    if (window.__S.length > 4000) window.__S.shift();
  };
  const ch = g.champs;
  const orig = ch.update.bind(ch);
  ch.update = (dt) => { orig(dt); try { sample(); } catch (e) { } };
  return true;
}"""

FUERZA = """() => {
  const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
  const P = ctrl.poderes;
  const cal = (P.lista || []).find(p => p.kind === 'calabaza');
  if (!cal) return { err: 'sin calabaza' };
  P.pend = cal; P.pendT = 0.001;
  return { ok: true, dur: cal.duration || 10 };
}"""

RESUMEN = """() => {
  const S = window.__S || [];
  const d3 = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1], a[2]-b[2]);
  const out = { n: S.length, estados: {}, strikes: [], maxCalaMesh: 0, maxCalaBall: 0,
                maxMeshBall: 0, minBladeCalaAlGolpe: null, ballVisConCala: 0,
                calaFrames: 0, rigNoCero: 0, residuales: null };
  let prevStrike = 0;
  const g = window.__PP_HALLOWEEN.ctrl().game;
  // residuales: cuerpos de calabaza (lathe naranja 0xe8720c) en escena
  let n = 0;
  g.scene.traverse((o) => {
    if (o.isMesh && o.geometry && o.geometry.type === 'LatheGeometry' &&
        o.material && o.material.color && o.material.color.getHex() === 0xe8720c) n++;
  });
  out.residuales = n;
  for (const r of S) {
    out.estados[r.st] = (out.estados[r.st] || 0) + 1;
    if (r.rig && (r.rig[0] || r.rig[1] || r.rig[2])) out.rigNoCero++;
    if (r.calaW && r.meshW) {
      out.calaFrames++;
      const d1 = d3(r.calaW, r.meshW), d2 = d3(r.calaW, r.ball);
      if (d1 > out.maxCalaMesh) { out.maxCalaMesh = d1; out.maxCalaMeshAt = r; }
      if (d2 > out.maxCalaBall) out.maxCalaBall = d2;
      if (r.meshVis) out.ballVisConCala++;
    }
    if (r.calaW && r.blade && r.strike > 0) {
      const db = d3(r.blade, r.calaW);
      if (out.minBladeCalaAlGolpe == null || db < out.minBladeCalaAlGolpe)
        out.minBladeCalaAlGolpe = db;
    }
    if (r.strike > prevStrike + 0.2) {
      out.strikes.push({ t: r.t, st: r.st, blade: r.blade, calaW: r.calaW,
                         ball: r.ball, hold: r.hold,
                         dBladeCala: (r.blade && r.calaW) ? +d3(r.blade, r.calaW).toFixed(3) : null,
                         dBladeBall: (r.blade) ? +d3(r.blade, r.ball).toFixed(3) : null });
    }
    prevStrike = r.strike;
  }
  if (out.maxCalaMeshAt) delete out.maxCalaMeshAt.t;
  return out;
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => { const g = window.__PP_HALLOWEEN && window.__PP_HALLOWEEN.ctrl().game;
                           if (g && g.champIntro) g.hideChampIntro(true); }""")
    pg.wait_for_timeout(2500)

    # ---- duelo REAL (etapa 1) por el camino del módulo
    duelo = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      try { ctrl._startDuel(0); return { ok: true, st: ctrl.game.rules.state }; }
      catch (e) { return { err: String(e) }; }
    }""")
    print('DUELO:', json.dumps(duelo))
    pg.wait_for_timeout(1200)

    # ---- sampler + calabaza forzada (camino real)
    print('SAMPLER:', pg.evaluate(SAMPLER))
    print('FUERZA:', json.dumps(pg.evaluate(FUERZA)))

    # ---- medir 16 s (dur 10 + estallido 0.55 + margen; el saque IA corre solo)
    pg.wait_for_timeout(16000)
    R1 = pg.evaluate(RESUMEN)
    print('== BASE (altura por defecto) ==')
    print(json.dumps(R1, ensure_ascii=False, indent=1)[:3600])

    # ---- reset poderes (cerrar si siguiera algo) + altura CUSTOM 0.83
    pg.evaluate("""() => {
      const ctrl = window.__PP_HALLOWEEN.ctrl(); const g = ctrl.game;
      try { ctrl.poderes.parar(); } catch (e) {}
      window.__S.length = 0;
      try { g._mesaAplicarY(0.83, { persist: false }); } catch (e) {}
      return { y: g.DIMS ? g.DIMS.tableTopY : null };
    }""")
    pg.wait_for_timeout(400)
    pg.evaluate(FUERZA)
    pg.wait_for_timeout(13000)
    R2 = pg.evaluate(RESUMEN)
    print('== ALTURA CUSTOM 0.83 ==')
    print(json.dumps(R2, ensure_ascii=False, indent=1)[:3600])

    # ---- FUGA DEL ZOMBI: one-shot del zombi sonando + salir al Hall (música mute)
    fuga = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl(); const g = ctrl.game;
      const Z = H.sfxZ && H.sfxZ();
      if (!Z || !Z.crazy) return { err: 'sin ZONB' };
      try { g.audio.setArcMute(true); } catch (e) {}       // música del Hall muteada (caso del dueño)
      Z.crazy.b.on(); Z.crazy.reloj = 0;                    // suena el zombi (como disparar un poder)
      await new Promise(r => setTimeout(r, 300));
      const suenaEnCancha = Z.crazy.b.suena();
      g.champs.leaveAll();                                  // salir del campeonato (camino real)
      try { g.enterHall(); } catch (e) {}
      await new Promise(r => setTimeout(r, 1800));
      return { suenaEnCancha, suenaEnHall: Z.crazy.b.suena(),
               estado: Z.crazy.b.estado ? Z.crazy.b.estado() : null,
               inHall: g.inHall };
    }""")
    print('== FUGA ZOMBI ==', json.dumps(fuga))

    # ---- residuales tras la fuga (¿calabazas viejas?)
    print('pageerrors:', errs[:4])
    b.close()
srv.shutdown()
