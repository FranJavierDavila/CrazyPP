#!/usr/bin/env python3
"""Prueba rápida: ocultar el overlay DOM del menú para VER el canvas 3D."""
import time
from playwright.sync_api import sync_playwright

def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {"__err": str(e)[:200]}

TICK = """(() => { const G = window.__PP_GAME;
  if (!window.__t) window.__t = performance.now();
  for (let i = 0; i < (window.__n || 4); i++) {
    window.__t += 50; G.lastTime = window.__t / 1000 - 0.05; G.freezeT = 0;
    G.animate(window.__t);
  } return 1; })()"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto("http://localhost:3000/game.html?champ=oeste", wait_until="domcontentloaded",
              timeout=60000)
    for _ in range(30):
        s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    # oculta el menú (asistencia visual del QA; no toca lógica de juego)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")
    page.evaluate("window.__n = 8")
    page.evaluate(TICK)
    time.sleep(0.8)
    st = js(page, """(() => { const G = window.__PP_GAME, c = G.champs.mod.controller;
      return { mode: c._stageMode || 'sala', cam: G.renderer.xr.isPresenting,
               rigY: G.rig ? +G.rig.rotation.y.toFixed(2) : null,
               camPos: G.camera ? [G.camera.position.x.toFixed(2), G.camera.position.y.toFixed(2), G.camera.position.z.toFixed(2)] : null }; })()""")
    print("estado:", st)
    page.screenshot(path="/home/z/my-project/scripts/_probe_vista.png")
    browser.close()
