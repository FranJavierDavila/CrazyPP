#!/usr/bin/env python3
"""QA V2.131 · humo rápido de los 4 campeonatos tras el fix (sin regresiones)."""
import time
from playwright.sync_api import sync_playwright

CHAMPS = ["locura", "magia", "oeste", "estacion_orbital"]

def probe(page, cid):
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(f"http://localhost:3000/game.html?champ={cid}", wait_until="domcontentloaded", timeout=60000)
    deadline = time.time() + 40
    out = {}
    while time.time() < deadline:
        try:
            out = page.evaluate("""(() => {
              const G = window.__PP_GAME, C = G && (G.champs||G.loader);
              const m = C && C.mod; const ctrl = m && (m.controller || m.ctrl || m.CTRL);
              return { active: C && C.activeId,
                       rules: G && G.rules && G.rules.state,
                       modState: ctrl && (ctrl.state || ctrl.stage !== undefined ? (ctrl.state||'?') : '?'),
                       intro: !!G.champIntro, err: null }; })()""")
        except Exception as e:
            out = {"err": str(e)[:120]}
        if out.get("active"):
            time.sleep(2.5)   # deja arrancar start()/intro
            try:
                out = page.evaluate("""(() => {
                  const G = window.__PP_GAME, C = G.champs, m = C.mod;
                  const ctrl = m.controller || m.ctrl || m.CTRL;
                  return { active: C.activeId, rules: G.rules.state,
                           modState: (ctrl && ctrl.state) || '?',
                           intro: !!G.champIntro }; })()""")
            except Exception as e:
                out = {"err": str(e)[:120]}
            return out
        time.sleep(1)
    return {"timeout": True}

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
                                      "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    for cid in CHAMPS:
        r = probe(page, cid)
        print(f"[{cid}] " + str(r), flush=True)
        try: page.evaluate("localStorage.clear()")
        except Exception: pass
    browser.close()
