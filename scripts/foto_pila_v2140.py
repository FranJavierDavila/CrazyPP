#!/usr/bin/env python3
"""V2.140 · FOTO de verificación de la pila de lingotes en el suelo.
Cámara centrada en las DOS pilas (izquierda x<0 / derecha x>0, z -1,0…-0,82)."""
import time
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'

TICK = """(() => { const G = window.__PP_GAME;
  if (!window.__t) window.__t = performance.now();
  for (let i = 0; i < (window.__n || 4); i++) {
    window.__t += 50; G.lastTime = window.__t / 1000 - 0.05; G.freezeT = 0;
    G.animate(window.__t);
  } return 1; })()"""

POSE_JS = """(() => {
  const r = window.__PP_GAME.renderer;
  const real = r.render.bind(r);
  r.render = (scene, cam) => {
    const p = window.__camPose;
    if (p) { cam.position.set(p[0], p[1], p[2]); cam.lookAt(p[3], p[4], p[5]); }
    return real(scene, cam);
  };
  window.__camPose = null; return 1; })()"""

def pose(page, px, py, pz, tx, ty, tz):
    page.evaluate(f"window.__camPose = [{px},{py},{pz},{tx},{ty},{tz}]")
    page.evaluate(TICK)   # SIN reset: la pose queda fija para el screenshot

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.goto(BASE + '/game.html?champ=oeste', wait_until='domcontentloaded', timeout=60000)
    for _ in range(30):
        if page.evaluate("!!(window.__PP_GAME && window.__PP_GAME.champs && "
                         "window.__PP_GAME.champs.mod && window.__PP_GAME.champs.mod.controller)"):
            break
        time.sleep(1)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")
    page.evaluate(POSE_JS)
    page.evaluate("""(() => { const G = window.__PP_GAME, c = G.champs.mod.controller;
      c.stage = 4; c._armT = 0; c._duelOn = false; c.serveTrigger(0);
      return 1; })()""")
    page.evaluate(TICK)
    page.evaluate("""(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      const t = G.champs.mod.controller._tren;
      if (t.phase !== 'run') t._depart();
      t.time = 95;                      // sin anuncios durante la foto
      const from = { x: 0, y: 0.9, z: -4.5 };
      for (let i = 0; i < 18; i++) t._lanzaLingote(from);
      return 1; })()""")
    page.evaluate("window.__n = 40")
    page.evaluate(TICK)
    page.evaluate("window.__n = 4")
    # foto 1: las DOS pilas desde el centro del vagón
    pose(page, 0.0, 1.55, 1.45, 0.0, 0.15, -1.15)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2140_pilas_dos.png')
    # foto 2: primer plano de la pila IZQUIERDA (2 capas)
    pose(page, 0.15, 0.75, -0.15, -1.19, 0.08, -0.91)
    time.sleep(0.4)
    page.screenshot(path='/home/z/my-project/scripts/_v2140_pila_cerca.png')
    print('fotos OK')
    browser.close()
