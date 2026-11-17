"""Verificación de música en el SALVAJE OESTE (V2.125).

Escenarios:
  O1) menú → lanzar OESTE → cerrar menú · la BSO del saloon sola
  O2) abrir/cerrar menú en la sala · nunca dos melodías audibles
  O3) CAMINO LOCURA→OESTE (arcWanted residual): jugar locura, salir, lanzar
      oeste, cerrar menú · el núcleo NO debe arrancar su BSO encima
  O4) abrir/cerrar menú tras el cambio · ídem
  O5) TREN: vagon.mp3 manda solo (BSO del saloon retirada)
  O6) ASEDIO: sin melodía solapada (jingle de oleada aparte)
  O7) re-bind del contexto en el Oeste · la BSO resucita sola y única
"""
import json

from playwright.sync_api import sync_playwright

INIT = """
(() => {
  window.__PP_SRC = [];
  const proto = AudioContext.prototype;
  const orig = proto.createBufferSource;
  proto.createBufferSource = function (...a) {
    const src = orig.apply(this, a);
    const rec = { ctx: this, loop: false, started: 0, stopped: 0,
      bufDur: 0, gain: null };
    const dLoop = Object.getOwnPropertyDescriptor(AudioBufferSourceNode.prototype, 'loop');
    Object.defineProperty(src, 'loop', {
      get() { return dLoop.get.call(src); },
      set(v) { rec.loop = !!v; dLoop.set.call(src, v); },
    });
    const dBuf = Object.getOwnPropertyDescriptor(AudioBufferSourceNode.prototype, 'buffer');
    Object.defineProperty(src, 'buffer', {
      get() { return dBuf.get.call(src); }, set(b) { rec.bufDur = b ? b.duration : 0; },
    });
    const _connect = src.connect.bind(src);
    src.connect = (dst, ...r) => {
      if (dst && dst.gain && dst.gain.value !== undefined) rec.gain = dst;
      return _connect(dst, ...r);
    };
    const _start = src.start.bind(src);
    src.start = (...sa) => { rec.started++; window.__PP_SRC.push(rec); return _start(...sa); };
    const _stop = src.stop.bind(src);
    src.stop = (...sa) => { rec.stopped++; return _stop(...sa); };
    return src;
  };
})();
"""

SNAP = """
() => {
  const G = window.__PP_GAME;
  const A = G.audio;
  const vivos = (window.__PP_SRC || [])
    .filter((s) => s.started > 0 && s.stopped === 0 && s.loop && s.bufDur > 3)
    .map((s) => ({
      pista: +s.bufDur.toFixed(1),
      vol: s.gain ? +(s.gain.gain.value || 0).toFixed(4) : null,
      ctxOk: s.ctx.state === 'running',
    }));
  const audibles = vivos.filter((s) => s.vol > 0.002 && s.ctxOk);
  let oesteMus = null;
  try {
    const mod = G.champs.modules['oeste'];
    const c = mod && mod.controller;
    if (c && c._mus) oesteMus = {
      viva: c._mus.src.context.state === 'running',
      mismaCtx: !!(A.ctx && c._mus.src.context === A.ctx),
      vol: +c._mus.gain.gain.value.toFixed(4),
      etapa: c._stageMode || 'sala',
    };
  } catch (e) { /* */ }
  return {
    esc: window.__ESC || '',
    musicPlaying: A.musicPlaying, arcPlaying: A.arcPlaying,
    arcWanted: !!A.arcWanted, ducked: !!A._arcDucked, menuOpen: G.menuOpen,
    activo: G.champs.activeId, ctx: A.ctx && A.ctx.state,
    bucles: vivos, audibles: audibles.length,
    solapan: audibles.length > 1, oesteMus,
  };
}
"""

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.add_init_script(INIT)
    pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(6000)

    def snap(esc):
        pg.evaluate(f"window.__ESC = '{esc}'")
        return pg.evaluate(SNAP)

    def show(tag, s):
        ok = "✓" if not s["solapan"] else "✗ SOLAPAN"
        print(f"--- {tag} [{ok}] audible={s['audibles']} menu={s['musicPlaying']} "
              f"arc={s['arcPlaying']}(want={s['arcWanted']}) duck={s['ducked']}")
        for bucle in s["bucles"]:
            print(f"      bucle: pista={bucle['pista']}s vol={bucle['vol']} ctxOk={bucle['ctxOk']}")
        if s["oesteMus"]:
            print(f"      _mus OESTE: {s['oesteMus']}")

    def menu_abrir():
        pg.evaluate("""() => { const g = window.__PP_GAME;
          g.menuOpen = true; g.audio.setArcDuck(true); g.audio.setMusicWanted(true); }""")

    def menu_cerrar():
        pg.evaluate("""() => { const g = window.__PP_GAME;
          g.closeMenu(); g.audio.setArcDuck(false); }""")

    # audio vivo + menú
    pg.evaluate("""() => { const g = window.__PP_GAME;
      g.audio.ensure();
      if (g.audio.ctx && g.audio.ctx.state !== 'running') g.audio.ctx.resume(); }""")
    menu_abrir()
    pg.wait_for_timeout(1500)

    # O1 · lanzar OESTE y cerrar menú
    pg.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
    pg.wait_for_timeout(2500)
    menu_cerrar()
    pg.wait_for_timeout(2500)
    show("O1 · sala del OESTE (BSO sola)", snap("O1"))

    # O2 · menú dentro de la sala
    menu_abrir()
    pg.wait_for_timeout(1800)
    show("O2a · sala + menú", snap("O2a"))
    menu_cerrar()
    pg.wait_for_timeout(2200)
    show("O2b · sala tras cerrar menú", snap("O2b"))

    # O3 · camino LOCURA→OESTE (arcWanted residual)
    menu_abrir()
    pg.wait_for_timeout(800)
    pg.evaluate("() => window.__PP_GAME.champs.launch('locura')")
    pg.wait_for_timeout(2500)
    menu_cerrar()
    pg.wait_for_timeout(2000)
    s = snap("O3-pre")
    print(f"--- O3-pre · dentro de LOCURA arc={s['arcPlaying']}(want={s['arcWanted']})")
    menu_abrir()
    pg.wait_for_timeout(800)
    pg.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
    pg.wait_for_timeout(2500)
    menu_cerrar()
    pg.wait_for_timeout(2500)
    show("O3 · sala OESTE tras LOCURA", snap("O3"))

    # O4 · menú tras el cambio de campeonato
    menu_abrir()
    pg.wait_for_timeout(1500)
    show("O4a · sala OESTE + menú", snap("O4a"))
    menu_cerrar()
    pg.wait_for_timeout(2200)
    show("O4b · sala OESTE tras cerrar", snap("O4b"))

    # O5 · TREN (vagon.mp3 manda solo)
    pg.evaluate("""() => {
      const c = window.__PP_GAME.champs.modules['oeste'].controller;
      c._endPower && c._endPower();
      c._instrGo = (n, cb) => cb();     // sin cartel en la prueba
      c._startTren();
    }""")
    pg.wait_for_timeout(3000)
    show("O5 · TREN en marcha", snap("O5"))

    # O6 · ASEDIO
    pg.evaluate("""() => {
      const c = window.__PP_GAME.champs.modules['oeste'].controller;
      if (c._tren) { try { c._endTren(false); } catch (e) { } }
      c._instrGo = (n, cb) => cb();
      c._startAsedio();
    }""")
    pg.wait_for_timeout(3000)
    show("O6 · ASEDIO en marcha", snap("O6"))

    # O7 · re-bind en el Oeste (vuelta a la sala primero)
    pg.evaluate("""() => {
      const c = window.__PP_GAME.champs.modules['oeste'].controller;
      if (c._stageMode === 'asedio' && c._asedio) { try { c._endAsedio(false); } catch (e) { } }
    }""")
    pg.wait_for_timeout(1500)
    pg.evaluate("() => window.__PP_GAME.audio.rebind('verif oeste v2.125')")
    pg.wait_for_timeout(3000)
    show("O7 · tras re-bind (BSO resucitada)", snap("O7"))

    b.close()

print("Errores JS:", len(errs))
for e in errs[:6]:
    print("  -", e[:180])
