#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91_probe_escena.py — sonda r91 (informe del dueño tras V3.6.82).
Verifica EN ESCENA VIVA las 7 quejas:
 1) MAPA en pared izquierda: ¿está el plano? ¿textura viva? ¿lo ve el jugador?
 2) RIVAL: nº de planos de estado (solape), cambio a defeated/victory real.
 3) CALABAZA procedural: ¿el cuerpo se renderiza? (spawn manual + captura).
 4) MÚSICA: reproducir el bug del vol numérico (TypeError silencioso).
 5) MANOS: repet.y/offset.y reales tras el cultivo (qué franja se ve).
 6) SONIDOS: quién dispara qué (mapa de disparos real).
 7) capturas desde la vista del jugador.
"""
import os, sys, time, functools, json, threading, base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8793
OUT = os.path.join(RAIZ, 'scripts')
SALIDA = {}

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

ENUM = """() => {
  const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
  const g = H.ctrl().game;
  const out = { vive: true, planos: [], V3: null };
  const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
  g.scene.traverse((o) => {
    let src = null;
    try {
      const m = o.material;
      const map = Array.isArray(m) ? m[0] && m[0].map : m && m.map;
      if (map && map.image && map.image.src) src = map.image.src;
    } catch (e) {}
    if (!src) return;
    const i = src.indexOf('/championships/halloween/');
    if (i < 0) return;
    const nom = src.slice(i + '/championships/halloween/'.length);
    const p = o.getWorldPosition(new V3());
    const s = o.getWorldScale(new V3());
    out.planos.push({
      tex: nom, pos: [+p.x.toFixed(3), +p.y.toFixed(3), +p.z.toFixed(3)],
      esc: [+s.x.toFixed(2), +s.y.toFixed(2)],
      rotY: +(o.getWorldRotation && o.getWorldRotation(new (Object.getPrototypeOf(new V3().x ? new V3() : new V3())).constructor ? V3 : V3) ? 0 : 0) || +(o.rotation.y ? o.rotation.y.toFixed(2) : 0),
      visible: o.visible && (!o.parent || o.parent.visible !== false),
      order: o.renderOrder || 0,
      padre: o.parent && o.parent.type,
    });
  });
  const r = H.ctrl().rival;
  out.estadoRival = r ? r.estado : null;
  out.mapa = H.ctrl().mapa ? {
    pos: H.ctrl().mapa.plane ? [+H.ctrl().mapa.plane.position.x.toFixed(3), +H.ctrl().mapa.plane.position.y.toFixed(3), +H.ctrl().mapa.plane.position.z.toFixed(3)] : null,
    enEscena: H.ctrl().mapa.plane ? !!H.ctrl().mapa.plane.parent : false,
    texViva: H.ctrl().mapa.plane && H.ctrl().mapa.plane.material.map && !!H.ctrl().mapa.plane.material.map.image,
    texTam: H.ctrl().mapa.plane && H.ctrl().mapa.plane.material.map && H.ctrl().mapa.plane.material.map.image ? [H.ctrl().mapa.plane.material.map.image.width, H.ctrl().mapa.plane.material.map.image.height] : null,
    colorSpace: H.ctrl().mapa.plane && H.ctrl().mapa.plane.material.map ? H.ctrl().mapa.plane.material.map.colorSpace : null,
    visible: H.ctrl().mapa.plane ? H.ctrl().mapa.plane.visible : null,
  } : null;
  return out;
}"""

MUSICA = """() => {
  // reproducir el bug: createMusic con vol NÚMERO (lo que hace el módulo r90)
  return new Promise((res) => {
    import('/championships/sdk/champ_sdk.js').then((sdk) => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      let errorNum = null, errorFn = null;
      const mNum = sdk.createMusic(() => g, { url: () => 'championships/halloween/assets/midnight_volley.mp3', vol: 0.18 });
      try { mNum.on(); } catch (e) { errorNum = String(e); }
      const mFn = sdk.createMusic(() => g, { url: () => 'championships/halloween/assets/midnight_volley.mp3', vol: () => 0.18 });
      try { mFn.on(); } catch (e) { errorFn = String(e); }
      setTimeout(() => {
        res({ num: mNum.estado(), fn: mFn.estado(), errorNum, errorFn,
              ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null });
      }, 2500);
    }).catch((e) => res({ importError: String(e) }));
  });
}"""

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
    pg.wait_for_timeout(6000)

    # 1) ENUM
    e0 = pg.evaluate(ENUM)
    SALIDA['enum_t0'] = e0
    print('== ENUM t=0 ==')
    print(json.dumps({k: e0[k] for k in ('vive', 'estadoRival', 'mapa')}, indent=1, ensure_ascii=False))
    print('planos con textura del módulo:')
    for p in e0.get('planos', []):
        print('  ', p['tex'], p['pos'], 'vis', p['visible'], 'esc', p['esc'])

    # 2) MÚSICA (bug del vol numérico)
    m = pg.evaluate(MUSICA)
    SALIDA['musica'] = m
    print('== MÚSICA =='); print(json.dumps(m, indent=1))

    # 3) RIVAL: pedir defeated y victory — ¿cambia la cara de verdad?
    caras = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const r = H.ctrl().rival; if (!r || !r.r) return { err: 'sin rival' };
      const cara = () => { try { const mm = r.r.mat; return mm && mm.map && mm.map.image ? mm.map.image.src.split('/').pop() : null; } catch (e) { return 'ERR'; } };
      const antes = cara();
      r._set('defeated', 4.0);
      return new Promise((res) => setTimeout(() => {
        const d1 = cara();
        r._set('victory', 2.0);
        setTimeout(() => res({ antes, defeated: d1, victory: cara(), sdkEstado: r.r.estado() }), 400);
      }, 400));
    }""")
    SALIDA['caras_rival'] = caras
    print('== CARAS DEL RIVAL =='); print(json.dumps(caras, indent=1))

    # captura del rival en defeated (vista del jugador hacia el rival)
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(0.1, 1.55, 0.9);
      g.camera.lookAt(1.45, 1.05, -3.3);
    }""")
    pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(OUT, '_r91_rival_defeated.png'))

    # 4) capturas del MAPA desde la vista del jugador
    for nom, cx, cy, cz, tx, ty, tz in (
        ('jugador_centro', 0.0, 1.60, 0.90, -3.04, 1.55, -1.9),
        ('jugador_cerca', -0.9, 1.60, -0.5, -3.04, 1.60, -1.9),
        ('recto_pared', 0.4, 1.55, -1.9, -3.05, 1.66, -1.9),
    ):
        pg.evaluate(f"""() => {{
          const g = window.__PP_HALLOWEEN.ctrl().game;
          g.camera.position.set({cx}, {cy}, {cz});
          g.camera.lookAt({tx}, {ty}, {tz});
        }}""")
        pg.wait_for_timeout(700)
        pg.screenshot(path=os.path.join(OUT, f'_r91_mapa_{nom}.png'))

    # 5) CALABAZA: spawn manual del poder y captura
    cala = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods(); const ctrl = H.ctrl();
      const ctxP = {};
      try { pods.calabaza.inicio(g, { duration: 10 }, ctrl, ctxP); } catch (e) { return { err: String(e) }; }
      // bola ficticia en medio de la mesa, vista del jugador
      const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
      if (!g.ball) g.ball = { pos: new V3(), vel: new V3(), spin: new V3() };
      g.ball.pos.set(0.15, 0.85, -0.6);
      if (g.ballMesh) { g.ballMesh.position.copy(g.ball.pos); g.ballMesh.visible = false; }
      // 3 pasos del poder
      for (let i = 0; i < 3; i++) { try { pods.calabaza.paso(0.033, g, { duration: 10 }, ctrl, ctxP); } catch (e) { return { errPaso: String(e) }; } }
      const C = ctxP.calabaza;
      const info = { spawn: !!C, enEscena: C && C.gltf ? !!C.gltf.parent : false,
        hijos: C && C.gltf ? C.gltf.children.map((c) => ({ tipo: c.type, vis: c.visible, geom: c.geometry && c.geometry.type })) : null,
        posCuerpo: C && C.gltf ? [+C.gltf.position.x.toFixed(2), +C.gltf.position.y.toFixed(2), +C.gltf.position.z.toFixed(2)] : null };
      // drenar el cache __calProc para crear UNO fresco y mirar su material
      try {
        const cuerpo = C.gltf.children[0];
        info.matCuerpo = { tipo: cuerpo.material.type, map: !!cuerpo.material.map, side: cuerpo.material.side,
                           color: '#'+cuerpo.material.color.getHexString(), transparent: cuerpo.material.transparent };
      } catch (e) { info.matCuerpo = String(e); }
      return info;
    }""")
    SALIDA['calabaza'] = cala
    print('== CALABAZA =='); print(json.dumps(cala, indent=1))
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(0.35, 1.50, 0.15);
      g.camera.lookAt(0.15, 0.85, -0.6);
    }""")
    pg.wait_for_timeout(600)
    pg.screenshot(path=os.path.join(OUT, '_r91_calabaza.png'))
    # cerrar la calabaza de prueba
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      try { H.pods().calabaza.fin(g, { duration: 10 }, H.ctrl(), window.__ctxR91 || {}); } catch (e) {}
    }""")

    # 6) MANOS: textura repeat/offset reales tras un spawn real
    manos = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods(); const ctrl = H.ctrl();
      const ctxP = {};
      pods.mano.inicio(g, { duration: 10 }, ctrl, ctxP);
      const M = ctxP.mano;
      // forzar las 3 texturas y un spawn
      return new Promise((res) => {
        const t0 = Date.now();
        const espera = () => {
          if (M.tex.length < 1 && Date.now() - t0 < 8000) return setTimeout(espera, 200);
          try { pods.mano._spawn(g, M); } catch (e) { res({ err: String(e) }); return; }
          setTimeout(() => {
            const v = M.vivos[0];
            res({ texCargadas: M.tex.length, vivos: M.vivos.length,
                  spawn: v ? { repeatY: +v.tex.repeat.y.toFixed(3), offY: +v.tex.offset.y.toFixed(3),
                               alto: +v.HF.toFixed(3), fase: v.fase,
                               imgTam: v.tex.image ? [v.tex.image.width, v.tex.image.height] : null } : null });
          }, 700);
        };
        espera();
      });
    }""")
    SALIDA['manos'] = manos
    print('== MANOS =='); print(json.dumps(manos, indent=1))
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(0.2, 1.45, -0.05);
      g.camera.lookAt(0.3, 0.95, -0.9);
    }""")
    pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(OUT, '_r91_mano.png'))

    if errs:
        SALIDA['pageerrors'] = errs[:8]
        print('ERRORES DE PÁGINA:', errs[:8])
    b.close()

srv.shutdown()
with open(os.path.join(OUT, '_r91_probe_salida.json'), 'w') as f:
    json.dump(SALIDA, f, indent=1, ensure_ascii=False)
print('SONDA R91 OK → scripts/_r91_probe_salida.json')
