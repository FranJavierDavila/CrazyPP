#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r91e_ciclo.py — sonda r91e: CICLO DE VIDA completo del zombi + música +
sonidos + manos. Busca el segundo plano (solape) en cada transición:
entrada → tormenta de emociones → duelo → final → re-entrada."""
import os, functools, json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8798

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

CUENTA = """() => {
  const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
  const V3 = (Object.getPrototypeOf(g.camera.position).constructor);
  const ESTADOS = ['present','idle','focused','surprised','panic','laughing','crazy','angry','picando','loosing','defeated','victory'];
  const planos = [];
  g.scene.traverse((o) => {
    let src = null;
    try { const m = o.material; const map = m && m.map; if (map && map.image && map.image.src) src = map.image.src; } catch (e) {}
    if (!src) return;
    const i = src.indexOf('/championships/halloween/');
    if (i < 0) return;
    const nom = src.slice(i + '/championships/halloween/'.length);
    const base = nom.replace('.webp', '').replace('.png', '');
    if (ESTADOS.includes(base) || nom.indexOf('mano') === 0 || nom.indexOf('monticulo') === 0) {
      const p = o.getWorldPosition(new V3());
      planos.push({ tex: nom, pos: [+p.x.toFixed(2), +p.y.toFixed(2), +p.z.toFixed(2)], vis: o.visible });
    }
  });
  // nodos con padre escena (top-level) para detectar huérfanos del rival
  const rivalEnEscena = [];
  g.scene.children.forEach((c) => {
    let src = null;
    try { const m = c.material; const map = m && m.map; if (map && map.image && map.image.src) src = map.image.src; } catch (e) {}
    if (src && src.indexOf('/championships/halloween/') >= 0) rivalEnEscena.push(src.split('/').pop());
  });
  const C = H.ctrl();
  return { planos, rivalEnEscena, cara: C.rival && C.rival.estado,
           nEscenaHijos: g.scene.children.length };
}"""

SALIDA = {}
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(3000)
    for texto in ('ESPAÑOL', 'ENGLISH'):
        try:
            pg.get_by_text(texto, exact=True).click(timeout=1200); break
        except Exception: pass
    try:
        pg.get_by_text('JUGAR EN VR').click(timeout=6000)
    except Exception:
        pg.mouse.click(640, 600)
    pg.wait_for_timeout(10000)
    try:
        pg.mouse.click(640, 360)
    except Exception: pass
    pg.wait_for_timeout(4000)

    # 1) estado de entrada
    e = pg.evaluate(CUENTA)
    SALIDA['entrada'] = e
    print('== ENTRADA =='); print('planos estado:', [(p['tex'], p['pos'][1]) for p in e['planos']])
    print('cara:', e['cara'], '· top-level halloween en escena:', e['rivalEnEscena'])

    # 2) tormenta de emociones (la norma r57 real) — 30 cambios rápidos
    pg.evaluate("""() => {
      const C = window.__PP_HALLOWEEN.ctrl();
      const seq = ['laughing','victory','angry','idle','focused','picando','surprised','panic',
                   'loosing','laughing','victory','defeated','victory','angry','idle','crazy',
                   'laughing','victory','defeated','idle','focused','panic','surprised','loosing',
                   'laughing','victory','angry','crazy','idle','defeated'];
      seq.forEach((s) => C.rival.rivalEmocion(s));
    }""")
    pg.wait_for_timeout(2500)
    e = pg.evaluate(CUENTA)
    SALIDA['tormenta'] = e
    print('== TORMENTA =='); print('planos estado:', [(p['tex'], p['pos'][1]) for p in e['planos']], '· cara:', e['cara'])

    # 3) ciclo de duelo: lanzar etapa (duelo 1) — serveTrigger real
    pg.evaluate("""() => { const C = window.__PP_HALLOWEEN.ctrl(); C.serveTrigger(0); }""")
    pg.wait_for_timeout(5000)
    e = pg.evaluate(CUENTA)
    SALIDA['duelo'] = e
    print('== DUELO =='); print('planos estado:', [(p['tex'], p['pos'][1]) for p in e['planos']], '· cara:', e['cara'])

    # 4) final del duelo (jugador gana) → defeated + hold + vuelta a sala
    pg.evaluate("""() => { const C = window.__PP_HALLOWEEN.ctrl(); C.onMatchOver(true); }""")
    pg.wait_for_timeout(1200)
    e = pg.evaluate(CUENTA)
    SALIDA['final'] = e
    print('== FINAL =='); print('planos estado:', [(p['tex'], p['pos'][1]) for p in e['planos']], '· cara:', e['cara'])

    # 5) RE-ENTRADA (startChamp de nuevo — el _desmonta debe limpiar TODO)
    pg.evaluate("""() => { window.__PP_HALLOWEEN.ctrl().startChamp(); }""")
    pg.wait_for_timeout(3000)
    e = pg.evaluate(CUENTA)
    SALIDA['reentrada'] = e
    print('== RE-ENTRADA =='); print('planos estado:', [(p['tex'], p['pos'][1]) for p in e['planos']])
    print('top-level halloween en escena:', e['rivalEnEscena'])

    # 6) MÚSICA: estado del motor tras on() (fix SDK forma número/función)
    mus = pg.evaluate("""() => new Promise((res) => {
      const H = window.__PP_HALLOWEEN; const g = H.ctrl().game;
      // el MUSIC del módulo ya está on() desde startChamp: esperamos 8 s y miramos
      setTimeout(() => {
        let modulo = null;
        try { modulo = (typeof MUSIC !== 'undefined' && MUSIC) ? MUSIC.estado() : 'no-accesible'; } catch (e) { modulo = 'err:' + e; }
        res({ modulo, ctx: g.audio && g.audio.ctx ? g.audio.ctx.state : null });
      }, 8000);
    })""")
    SALIDA['musica'] = mus
    print('== MÚSICA =='); print(json.dumps(mus))

    # 7) SONIDOS: disparo real de los 4 + estado ZONB (vía __PP_HALLOWEEN)
    snd = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const C = H.ctrl();
      const out = {};
      // SFX es privado del módulo; pero rivalEmocion dispara los sonidos:
      // comprobamos vía fetch que los 4 ficheros existen y decodifican
      return ['risas.mp3', 'zombi_crazy.mp3', 'zombi_victory.mp3', 'zombi_defeated.mp3', 'midnight_volley.mp3']
        .map((f) => fetch('championships/halloween/assets/' + f).then((r) => r.arrayBuffer()).then((b) => ({ f, kb: Math.round(b.byteLength / 1024) })));
    }""")
    snd = pg.evaluate("""() => Promise.all(
      ['risas.mp3','zombi_crazy.mp3','zombi_victory.mp3','zombi_defeated.mp3','midnight_volley.mp3']
        .map((f) => fetch('championships/halloween/assets/' + f)
          .then((r) => r.arrayBuffer())
          .then((b) => window.__PP_HALLOWEEN.ctrl().game.audio.ctx.decodeAudioData(b))
          .then((ab) => ({ f: f, dur: +ab.duration.toFixed(2), ch: ab.numberOfChannels, rate: ab.sampleRate }))
          .catch((e) => ({ f: f, err: String(e).slice(0, 60) }))))""")
    SALIDA['sonidos'] = snd
    print('== SONIDOS =='); print(json.dumps(snd, indent=1))

    SALIDA['pageerrors'] = errs[:6]
    print('pageerrors:', errs[:6])
    b.close()

srv.shutdown()
with open(os.path.join(RAIZ, 'scripts', '_r91e_salida.json'), 'w') as f:
    json.dump(SALIDA, f, indent=1, ensure_ascii=False)
print('SONDA r91e OK')
