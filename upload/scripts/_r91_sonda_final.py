#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91_sonda_final.py — verificación r91 EN ESCENA VIVA (técnica r88 + DOM-kill).
1) entrada REAL al campeonato (clic idioma + JUGAR EN VR)
2) ENUM + capturas de la sala viva: MAPA en pared izquierda (3 vistas),
   CALABAZA procedural (spawn manual), MANO (arte completo), RIVAL defeated
3) muestreo 24 s con tormenta de puntos (onPoint + rivalEmocion) — solape de
   planos de estado del zombi
4) MÚSICA en vivo: número vs función (tras el fix ambos deben sonar)
"""
import os, sys, time, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8795
OUT = os.path.join(RAIZ, 'scripts')
SALIDA = {}

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
Handler.log_message = lambda *a, **k: None
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

KILL_DOM = """() => {
  // oculta overlays DOM (menú/intro) que tapan el lienzo 3D en headless
  const vh = innerHeight;
  let n = 0;
  document.querySelectorAll('body *').forEach((el) => {
    if (el.tagName === 'CANVAS' || el.tagName === 'SCRIPT' || el.tagName === 'STYLE' || el.tagName === 'LINK') return;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    if (cs.position === 'fixed' || cs.position === 'absolute') {
      if (r.height > vh * 0.5 && r.width > innerWidth * 0.5) { el.style.display = 'none'; n++; }
    }
  });
  return n;
}"""

ENUM = """() => {
  const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
  const g = H.ctrl().game;
  const out = { vive: true, estados: [], mapa: null };
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
    if (['present','idle','focused','surprised','panic','laughing','crazy','angry','picando','loosing','defeated','victory','rival.webp'].some(s => nom === (s.endsWith('.webp') ? s : s + '.webp'))) {
      const p = o.getWorldPosition(new V3());
      out.estados.push({ tex: nom, pos: [+p.x.toFixed(2), +p.y.toFixed(2), +p.z.toFixed(2)] });
    }
    if (nom === 'mapa.webp') {
      const p = o.getWorldPosition(new V3());
      const vis = o.visible;
      const op = o.material.opacity;
      const pad = [];
      let q = o.parent; while (q) { pad.push(q.type + (q === g.rig ? ':RIG' : '')); q = q.parent; }
      out.mapa = { pos: [+p.x.toFixed(3), +p.y.toFixed(3), +p.z.toFixed(3)], visible: vis, opacity: op, padres: pad.join('>'),
                   texViva: !!o.material.map.image, cs: o.material.map.colorSpace };
    }
  });
  const r = H.ctrl().rival;
  out.caraRival = r && r.r && r.r.mat && r.r.mat.map && r.r.mat.map.image ? r.r.mat.map.image.src.split('/').pop() : null;
  return out;
}"""

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    # entrada REAL: idioma y JUGAR (patrón r88, con reintentos)
    for texto in ('ESPAÑOL', 'ENGLISH'):
        try:
            pg.get_by_text(texto, exact=True).click(timeout=1200); break
        except Exception: pass
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=6000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(12000)
    # clic JUGAR de la intro 3D si existe (panel del rig — es 3D, no DOM)
    try:
        pg.mouse.click(640, 360)   # el botón JUGAR de la intro 3D está al centro-bajo
    except Exception: pass
    pg.wait_for_timeout(4000)

    # 1) ENUM tras la entrada
    e0 = pg.evaluate(ENUM)
    SALIDA['enum'] = e0
    print('== ENUM =='); print(json.dumps(e0, indent=1, ensure_ascii=False))

    # capturas de la sala (con kill DOM si aún queda overlay)
    nk = pg.evaluate(KILL_DOM)
    pg.wait_for_timeout(400)
    print('DOM oculto:', nk)
    for nom, cx, cy, cz, tx, ty, tz in (
        ('sala_jugador', 0.0, 1.55, 0.75, -1.2, 1.35, -1.9),
        ('mapa_cerca', -0.4, 1.50, -0.9, -2.98, 1.45, -0.9),
        ('mapa_lejos', 0.6, 1.55, 0.4, -2.98, 1.50, -0.9),
    ):
        pg.evaluate(f"""() => {{
          const g = window.__PP_HALLOWEEN.ctrl().game;
          g.camera.position.set({cx}, {cy}, {cz});
          g.camera.lookAt({tx}, {ty}, {tz});
        }}""")
        pg.wait_for_timeout(800)
        pg.screenshot(path=os.path.join(OUT, f'_r91f_{nom}.png'))
    print('capturas de sala escritas')

    # 2) RIVAL: defeated vía onMatchOver COMPLETO (con el hold de sala)
    caras = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const C = H.ctrl(); if (!C.rival) return { err: 'sin rival' };
      const cara = () => { try { const mm = C.rival.r.mat; return mm && mm.map && mm.map.image ? mm.map.image.src.split('/').pop() : null; } catch (e) { return 'ERR'; } };
      // simular fin de duelo perdido por el zombi (el jugador gana)
      C.dueloVivo = true; C.dueloIdx = 0;
      C.onMatchOver(true);
      const inmediato = cara();               // r91: debe ser defeated YA
      // simular sala() implícita (la llama onMatchOver) — el hold debe aguantarla
      C.sala();
      const trasSala = cara();                // r91: defeated sigue (hold _finalT)
      // tick de update 4,5 s (dt 0,1 × 45) → vuelve a idle
      for (let i = 0; i < 45; i++) { C.update(0.1); H.ctrl().rival && C.rival.update(0.1); }
      const trasHold = cara();
      // tormenta de la norma: punto del zombi → laughing (+risa) → victory
      const mod = window.__PP_HALLOWEEN;
      let sonidoLaugh = null, sonidoVictory = null;
      try {
        // interceptar SFX.play vía ZONB no es posible (privado) — probamos cara + estado sdk
        C.rival.rivalEmocion('laughing'); const l1 = cara();
        C.rival.rivalEmocion('victory');  const v1 = cara();
        C.rival.rivalEmocion('defeated'); const d1 = cara();
        return { inmediato, trasSala, trasHold, laughing: l1, victory: v1, defeated: d1 };
      } catch (e) { return { err: String(e), inmediato, trasSala, trasHold }; }
    }""")
    SALIDA['caras'] = caras
    print('== CARAS/HOLD =='); print(json.dumps(caras, indent=1))

    # captura del zombi en defeated
    pg.evaluate("""() => {
      const C = window.__PP_HALLOWEEN.ctrl(); const g = C.game;
      C.rival.rivalEmocion('defeated');
      g.camera.position.set(-0.2, 1.5, 0.3);
      g.camera.lookAt(1.45, 1.1, -3.3);
    }""")
    pg.wait_for_timeout(800)
    pg.screenshot(path=os.path.join(OUT, '_r91f_rival_defeated.png'))

    # 3) CALABAZA: spawn manual + pasos + captura
    cala = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods; const ctrl = H.ctrl();
      const ctxP = {};
      try { pods.calabaza.inicio(g, { duration: 10 }, ctrl, ctxP); } catch (e) { return { err: String(e) }; }
      const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
      if (!g.ball) g.ball = { pos: new V3(), vel: new V3(), spin: new V3() };
      g.ball.pos.set(0.15, 0.85, -0.6);
      if (g.ballMesh) { g.ballMesh.position.copy(g.ball.pos); g.ballMesh.visible = false; }
      for (let i = 0; i < 5; i++) { try { pods.calabaza.paso(0.033, g, { duration: 10 }, ctrl, ctxP); } catch (e) { return { errPaso: String(e) }; } }
      const C = ctxP.calabaza;
      const cuerpo = C.gltf.children[0];
      return { spawn: !!C, enEscena: !!C.gltf.parent, pos: [+C.gltf.position.x.toFixed(2), +C.gltf.position.y.toFixed(2), +C.gltf.position.z.toFixed(2)],
               cuerpo: { side: cuerpo.material.side, color: '#' + cuerpo.material.color.getHexString(),
                         map: !!cuerpo.material.map, frustumCulled: cuerpo.frustumCulled,
                         vis: cuerpo.visible, rad0: +cuerpo.geometry.attributes.position.getY(0).toFixed(4) } };
    }""")
    SALIDA['calabaza'] = cala
    print('== CALABAZA =='); print(json.dumps(cala, indent=1))
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(0.32, 1.30, -0.18);
      g.camera.lookAt(0.15, 0.85, -0.6);
    }""")
    pg.wait_for_timeout(700)
    pg.screenshot(path=os.path.join(OUT, '_r91f_calabaza.png'))
    pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      try { H.pods.calabaza.fin(g, { duration: 10 }, H.ctrl(), { calabaza: H.ctrl() && null }); } catch (e) {}
    }""")

    # 4) MANO: spawn + captura (arte completo)
    manos = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      const pods = H.pods; const ctrl = H.ctrl();
      const ctxP = {};
      pods.mano.inicio(g, { duration: 10 }, ctrl, ctxP);
      const M = ctxP.mano;
      return new Promise((res) => {
        const t0 = Date.now();
        const espera = () => {
          if (M.tex.length < 1 && Date.now() - t0 < 8000) return setTimeout(espera, 200);
          try { pods.mano._spawn(g, M); } catch (e) { res({ err: String(e) }); return; }
          // completar el unroll manualmente
          const v = M.vivos[0];
          if (v) { for (let i = 0; i < 20; i++) pods.mano.paso(0.05, g, { duration: 10 }, ctrl, ctxP); }
          res({ texCargadas: M.tex.length, vivos: M.vivos.length,
                spawn: v ? { repeatY: +v.tex.repeat.y.toFixed(3), offY: +v.tex.offset.y.toFixed(3), fase: v.fase } : null });
        };
        espera();
      });
    }""")
    SALIDA['manos'] = manos
    print('== MANOS =='); print(json.dumps(manos, indent=1))
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN.ctrl().game;
      g.camera.position.set(0.55, 1.42, -0.25);
      g.camera.lookAt(0.3, 0.92, -0.95);
    }""")
    pg.wait_for_timeout(500)
    pg.screenshot(path=os.path.join(OUT, '_r91f_mano.png'))

    # 5) MÚSICA en vivo: número vs función (tras el fix del SDK, ambos)
    mus = pg.evaluate("""() => new Promise((res) => {
      import('/championships/sdk/champ_sdk.js').then((sdk) => {
        const g = window.__PP_HALLOWEEN.ctrl().game;
        const mNum = sdk.createMusic(() => g, { url: () => 'championships/halloween/assets/midnight_volley.mp3', vol: 0.18 });
        const mFn  = sdk.createMusic(() => g, { url: 'championships/halloween/assets/midnight_volley.mp3', vol: () => 0.18 });
        mNum.on(); mFn.on();
        setTimeout(() => res({ numero: mNum.estado(), funcion: mFn.estado(),
                               ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null }), 9000);
      }).catch((e) => res({ importError: String(e) }));
    })""")
    SALIDA['musica'] = mus
    print('== MÚSICA =='); print(json.dumps(mus, indent=1))

    # 6) muestreo 24 s con tormenta de puntos — ¿dos planos de estado?
    print('== MUESTREO 24 s (tormenta de puntos) ==')
    dup = 0
    for k in range(12):
        e = pg.evaluate("""() => {
          const H = window.__PP_HALLOWEEN; const C = H.ctrl();
          // tormenta de la norma: el patrón real del núcleo en un duelo
          C.rival.rivalEmocion('laughing');
          C.rival.rivalEmocion('victory');
          C.rival.rivalEmocion('angry');
          C.rival.rivalEmocion('idle');
          const g = C.game;
          const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
          let estados = [];
          g.scene.traverse((o) => {
            let src = null;
            try { const m = o.material; const map = Array.isArray(m) ? m[0] && m[0].map : m && m.map; if (map && map.image && map.image.src) src = map.image.src; } catch (e) {}
            if (!src) return;
            const i = src.indexOf('/championships/halloween/');
            if (i < 0) return;
            const nom = src.slice(i + '/championships/halloween/'.length);
            if (['present','idle','focused','surprised','panic','laughing','crazy','angry','picando','loosing','defeated','victory'].includes(nom.replace('.webp',''))) {
              estados.push(nom);
            }
          });
          return { estados, cara: C.rival && C.rival.estado };
        }""")
        if len(e['estados']) > 1: dup += 1
        SALIDA.setdefault('muestreo', []).append(e)
        pg.wait_for_timeout(2000)
    print('muestras con >1 plano de estado:', dup, '/ 12')
    SALIDA['duplicados'] = dup

    if errs:
        SALIDA['pageerrors'] = errs[:8]
        print('ERRORES DE PÁGINA:', errs[:8])
    b.close()

srv.shutdown()
with open(os.path.join(OUT, '_r91_sonda_salida.json'), 'w') as f:
    json.dump(SALIDA, f, indent=1, ensure_ascii=False)
print('SONDA FINAL OK → scripts/_r91_sonda_salida.json')
