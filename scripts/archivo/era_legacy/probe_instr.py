#!/usr/bin/env python3
"""Probe: llama _instrArte y captura el warn del try/catch."""
import json
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_page(viewport={"width": 1280, "height": 720})
    logs = []
    page.on("console", lambda m: logs.append(m.type + ": " + m.text[:300]))
    page.on("pageerror", lambda e: logs.append("PAGEERROR: " + str(e)[:300]))
    page.add_init_script("window.__pp2DPlay = true;")
    page.goto("http://localhost:3000/game.html", wait_until="domcontentloaded",
              timeout=60000)
    t0 = time.time()
    while time.time() - t0 < 40:
        try:
            if page.evaluate("!!window.__PP_GAME"):
                break
        except Exception:
            pass
        time.sleep(0.5)
    time.sleep(1)
    r = page.evaluate("""(() => {
      const G = window.__PP_GAME;
      const rigOk = !!G.rig;
      let err = null;
      try {
        G.showInstrucciones('ASEDIO AL ESCONDITE',
          ['Uno dos tres cuatro cinco seis siete ocho nueve diez once doce.',
           'Otra linea de prueba para el cartel del oeste.'], 7.5, null,
          'oeste', { empezar: true });
      } catch (e) { err = String(e && e.stack || e); }
      return { rigOk, err, instr: !!G._instr,
        arte: G._instr ? !!G._instr.arte : null };
    })()""")
    print(json.dumps(r, indent=1))
    time.sleep(0.5)
    print("LOGS:")
    for l in logs[-12:]:
        print("  ", l)
    browser.close()
