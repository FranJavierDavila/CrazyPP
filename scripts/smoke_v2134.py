#!/usr/bin/env python3
"""Smoke V2.134 · los 4 campeonatos cargan sin errores de página."""
import time
from playwright.sync_api import sync_playwright

CHAMPS = ["locura", "magia", "oeste", "estacion_orbital"]

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    mal = {}
    for ch in CHAMPS:
        ctx = browser.new_context(viewport={"width": 800, "height": 450})
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)[:160]))
        page.add_init_script("window.__pp2DPlay = true;")
        page.goto(f"http://localhost:3000/game.html?champ={ch}",
                  wait_until="domcontentloaded", timeout=60000)
        t0 = time.time()
        ok = False
        while time.time() - t0 < 40:
            try:
                ok = page.evaluate(
                    "!!(window.__PP_GAME&&window.__PP_GAME.champs&&"
                    "window.__PP_GAME.champs.mod&&window.__PP_GAME.champs.mod.controller)")
            except Exception:
                ok = False
            if ok:
                break
            time.sleep(1)
        time.sleep(3)
        estado = page.evaluate("""(() => { const c = window.__PP_GAME.champs.mod.controller;
          return { active: !!c.active, ver: c.manifest ? c.manifest.version : null }; })()""" )
        print(f"[{ch}] boot={ok} estado={estado} pageerrors={len(errs)}", flush=True)
        if errs or not ok:
            mal[ch] = errs[:3]
        ctx.close()
    browser.close()

print("\n==== SMOKE V2.134 ====")
if mal:
    print("FALLOS:", mal)
    raise SystemExit(1)
print("4/4 CAMPEONATOS SIN ERRORES ✔")
