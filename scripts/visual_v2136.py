#!/usr/bin/env python3
"""QA V2.136 · VISUAL FINAL II — la cámara orbital 2D se re-aplica en CADA
frame justo antes del render, así que la pose se inyecta con un PATCH de
renderer.render (funciona para RAF y ticks):
  1. PRIMER PLANO del mapa nuevo en la sala.
  2. PORTAL de ENTRADA (1,2 m, normal) en la ventana izquierda del tren.
  3. PORTAL de SALIDA (espejado) asomando al acabar la banda."""
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

POSE_JS = """(() => {
  if (!window.__renderPatch) {
    const r = window.__PP_GAME.renderer;
    const real = r.render.bind(r);
    r.render = (scene, cam) => {
      const p = window.__camPose;
      if (p) { cam.position.set(p[0], p[1], p[2]); cam.lookAt(p[3], p[4], p[5]); }
      return real(scene, cam);
    };
    window.__renderPatch = true;
  }
  window.__camPose = window.__posePendiente || null;
  window.__posePendiente = null;
  return 1; })()"""

def pose(page, px, py, pz, tx, ty, tz):
    page.evaluate(f"window.__posePendiente = [{px},{py},{pz},{tx},{ty},{tz}]")
    page.evaluate(POSE_JS)

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto("http://localhost:3000/game.html?champ=oeste", wait_until="domcontentloaded",
              timeout=60000)
    for _ in range(30):
        s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")

    # ===== 1 · PRIMER PLANO DEL MAPA NUEVO (sala) =====
    js(page, """(() => { const G = window.__PP_GAME, s = window.__PP_OESTE.ctrl();
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      s.mapa.visible = true; return 1; })()""")
    page.evaluate("window.__n = 6")
    page.evaluate(TICK)
    pose(page, -1.30, 1.50, -0.90, -2.98, 1.48, -0.90)
    page.evaluate(TICK)
    time.sleep(0.5)
    page.screenshot(path="/home/z/my-project/scripts/_v2136_mapa_cerca.png")
    print("1 · mapa cerca OK")
    page.evaluate("window.__camPose = null")

    # ===== 2 · PORTAL DE ENTRADA en la ventana (etapa 4) =====
    js(page, """(() => { const G = window.__PP_GAME, c = G.champs.mod.controller;
      c.stage = 4; c._armT = 0; c._duelOn = false; c.serveTrigger(0);
      return 1; })()""")
    page.evaluate(TICK)
    js(page, """(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      return 1; })()""")
    for _ in range(20):
        t = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
          return (c._tren && c._stageMode === 'tren') ? c._tren.phase : null; })()""")
        if t:
            break
        page.evaluate(TICK)
        time.sleep(0.3)
    print("tren fase:", t)
    js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller,
      t = c._tren;
      if (t.phase !== 'run') t._depart();
      return { fase: t.phase }; })()""")
    page.evaluate("window.__n = 10")
    page.evaluate(TICK)
    # boca de ENTRADA centrada en la ventana izquierda (_tunelZ = -1.82)
    js(page, """(() => { const G = window.__PP_GAME, t =
      G.champs.mod.controller._tren;
      t._tunnelPhase = 'pre'; t._tunnelT2 = 0; t._tunelZ = -1.82;
      t.tunelGrp.position.z = t._tunelZ; t.tunelGrp.visible = true;
      return 1; })()""")
    page.evaluate("window.__n = 2")
    page.evaluate(TICK)
    pose(page, 0.30, 1.60, 0.10, -3.55, 1.70, -1.82)
    page.evaluate(TICK)
    time.sleep(0.5)
    page.screenshot(path="/home/z/my-project/scripts/_v2136_portal_ventana.png")
    print("2 · portal entrada OK")

    # ===== 3 · PORTAL DE SALIDA (espejado) =====
    js(page, """(() => { const G = window.__PP_GAME, t =
      G.champs.mod.controller._tren;
      t._tunnelPhase = 'dur'; t._tunnelT2 = 0; t._tunelZ = 25.78;
      t.tunelGrp.position.z = t._tunelZ;
      return 1; })()""")
    page.evaluate(TICK)
    pose(page, 0.30, 1.60, 0.10, -3.55, 1.70, -1.82)
    page.evaluate(TICK)
    time.sleep(0.5)
    page.screenshot(path="/home/z/my-project/scripts/_v2136_portal_salida.png")
    print("3 · portal salida OK · pageerrors:", len(errs), errs[:2])
    page.evaluate("window.__camPose = null")
    browser.close()
