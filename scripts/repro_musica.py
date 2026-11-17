"""Verificación de la auditoría de música V2.124.

Escenarios:
  A) menú abierto → lanzar MAGIA → cerrar menú (duelo) · una sola melodía
  B) en duelo → abrir/cerrar menú · nunca dos melodías audibles
  C) en duelo MAGIA → recrear contexto (re-bind como la Quest) → la BSO
     propia del módulo debe RESUCITAR sola en el contexto nuevo
  D) LOCURA: menú → arcade → una sola melodía (reproductor del núcleo)
  E) invariante inverso: setArcWanted(true) con la música del menú sonando
     → la BSO manda y la del menú se retira
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
      get() { return dBuf.get.call(src); },
      set(b) { rec.bufDur = b ? b.duration : 0; dBuf.set.call(src, b); },
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
  let modMus = null;
  try {
    const c = window.__PP_MAGIA && window.__PP_MAGIA.ctrl();
    if (c && c._mus) modMus = { viva: c._mus.src.context.state === 'running',
      mismaCtx: !!(A.ctx && c._mus.src.context === A.ctx),
      vol: +c._mus.gain.gain.value.toFixed(4) };
  } catch (e) { /* */ }
  return {
    escenario: window.__ESC || '',
    musicPlaying: A.musicPlaying, arcPlaying: A.arcPlaying,
    ducked: !!A._arcDucked, menuOpen: G.menuOpen,
    activo: G.champs.activeId, ctx: A.ctx && A.ctx.state,
    bucles: vivos, audibles: audibles.length,
    solapan: audibles.length > 1,
    moduloMus: modMus,
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
        print(f"--- {tag} [{ok}] audible={s['audibles']} "
              f"menu={s['musicPlaying']} arc={s['arcPlaying']} duck={s['ducked']}")
        for bucle in s["bucles"]:
            print(f"      bucle: pista={bucle['pista']}s vol={bucle['vol']} ctxOk={bucle['ctxOk']}")
        if s["moduloMus"]:
            print(f"      _mus MAGIA: {s['moduloMus']}")

    # audio vivo + menú como en onSessionStart
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.audio.ensure();
      if (g.audio.ctx && g.audio.ctx.state !== 'running') g.audio.ctx.resume();
      g.menuOpen = true;
      g.audio.setArcDuck(true);
      g.audio.setMusicWanted(true);
    }""")
    pg.wait_for_timeout(1500)
    show("A0 · menú abierto", snap("A0"))

    # A) MAGIA: lanzar + cerrar menú
    pg.evaluate("() => window.__PP_GAME.champs.launch('magia')")
    pg.wait_for_timeout(2500)
    show("A1 · MAGIA lanzada", snap("A1"))
    pg.evaluate("() => window.__PP_GAME.closeMenu()")
    pg.wait_for_timeout(2500)
    show("A2 · duelo MAGIA", snap("A2"))

    # B) abrir/cerrar menú en pleno duelo
    pg.evaluate("() => window.__PP_GAME.toggleMenu()")
    pg.wait_for_timeout(1800)
    show("B1 · duelo + menú", snap("B1"))
    pg.evaluate("() => window.__PP_GAME.toggleMenu()")
    pg.wait_for_timeout(2500)
    show("B2 · menú cerrado", snap("B2"))

    # C) re-bind: la BSO del módulo debe resucitar sola
    pg.evaluate("() => window.__PP_GAME.audio.rebind('verif v2.124')")
    pg.wait_for_timeout(3000)
    show("C1 · tras re-bind (BSO resucitada)", snap("C1"))

    # D) LOCURA: el reproductor del núcleo
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.menuOpen = true;
      g.audio.setArcDuck(true);
      g.audio.setMusicWanted(true);
    }""")
    pg.wait_for_timeout(1000)
    pg.evaluate("() => window.__PP_GAME.champs.launch('locura')")
    pg.wait_for_timeout(1500)
    show("D1 · LOCURA lanzada (menú cerrado por el módulo)", snap("D1"))

    # E) invariante inverso: BSO arranca con la música del menú sonando
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.menuOpen = true;
      g.audio.setArcDuck(false);        // forzamos un camino mal emparejado
      g.audio.setMusicWanted(true);     // música del menú sonando
      g.audio.setArcWanted(true);       // y la BSO entra SIN duck
    }""")
    pg.wait_for_timeout(2000)
    show("E1 · BSO + menú (camino sin emparejar)", snap("E1"))

    b.close()

print("Errores JS:", len(errs))
for e in errs[:6]:
    print("  -", e[:180])
