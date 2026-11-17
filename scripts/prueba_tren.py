"""Mini-verificación TREN del Oeste: vagon.mp3 suena SOLO y muere al bajar
del tren (la BSO del saloon vuelve sola y única). Espera larga por el
decode del mp3 (3,7 MB)."""
from playwright.sync_api import sync_playwright

INIT = open('/home/z/my-project/scripts/repro_musica_oeste.py').read().split('INIT = """')[1].split('"""')[0]
SNAP = open('/home/z/my-project/scripts/repro_musica_oeste.py').read().split('SNAP = """')[1].split('"""')[0]

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
        print(f"--- {tag} [{ok}] audible={s['audibles']} menu={s['musicPlaying']} arc={s['arcPlaying']}")
        for bucle in s["bucles"]:
            print(f"      bucle: pista={bucle['pista']}s vol={bucle['vol']} ctxOk={bucle['ctxOk']}")

    pg.evaluate("""() => { const g = window.__PP_GAME;
      g.audio.ensure();
      if (g.audio.ctx && g.audio.ctx.state !== 'running') g.audio.ctx.resume();
      g.menuOpen = true; g.audio.setArcDuck(true); g.audio.setMusicWanted(true); }""")
    pg.wait_for_timeout(1200)
    pg.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
    pg.wait_for_timeout(2500)
    pg.evaluate("""() => { const g = window.__PP_GAME;
      g.closeMenu(); g.audio.setArcDuck(false); }""")
    pg.wait_for_timeout(2000)
    show("T1 · sala (BSO sola)", snap("T1"))

    pg.evaluate("""() => {
      const c = window.__PP_GAME.champs.modules['oeste'].controller;
      c._instrGo = (n, cb) => cb();
      c._startTren();
    }""")
    pg.wait_for_timeout(9000)
    show("T2 · TREN en marcha (vagon solo)", snap("T2"))

    pg.evaluate("""() => {
      const c = window.__PP_GAME.champs.modules['oeste'].controller;
      if (c._tren) c._endTren(false);
    }""")
    pg.wait_for_timeout(3500)
    show("T3 · de vuelta en la sala (BSO sola)", snap("T3"))

    b.close()

print("Errores JS:", len(errs))
for e in errs[:6]:
    print("  -", e[:180])
