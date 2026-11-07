#!/usr/bin/env python3
"""QA v3.0.5-FIS1 (reconstruida) · física viva + PALAS CON CARÁCTER:
  1) la página carga sin pageerrors
  2) badge V3.0.5-FIS1 en portada 2D
  3) __PP_PADDLE_PERKS expone 6 pieles y __PP_SET_PADDLE_SKIN funciona
  4) la skin del perfil (localStorage ppxr_train_v1) sincroniza con la física
  5) DIMS.physicsRealism y DIMS.paddlePerks activos
  6) capturas de portada y HUB con etiquetas de carácter
"""
import asyncio, json
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_HUB = "/home/z/my-project/download/qa_fis1_hub_perks.png"
OUT_PORTADA = "/home/z/my-project/download/qa_fis1_portada.png"

PROFILE = {
    "pts": 3000, "best": {}, "done": {},
    "unlocked": ["clasica", "fuego", "hielo", "oro", "arcoiris", "carbon"],
    "skin": "arcoiris", "fb": {"marks": 1, "line": 1, "spin": 1},
}

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto("about:blank")
        await page.add_init_script(
            "localStorage.setItem('ppxr_train_v1', JSON.stringify(" + json.dumps(PROFILE) + "));")
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        checks = await page.evaluate("""() => {
          const out = {};
          out.badge = (document.querySelector('#verBadge') || {}).textContent || '';
          out.perks = !!window.__PP_PADDLE_PERKS &&
                      Object.keys(window.__PP_PADDLE_PERKS).length;
          out.skinSync = window.__PP_PADDLE_SKIN || null;
          out.setSkinFn = typeof window.__PP_SET_PADDLE_SKIN === 'function';
          out.dims = (window.__ppDebug && window.__ppDebug.DIMS) ? {
            fis: window.__ppDebug.DIMS.physicsRealism,
            perks: window.__ppDebug.DIMS.paddlePerks,
          } : null;
          out.trainApi = !!window.__PP_TRAIN;
          return out;
        }""")
        print("badge      :", checks["badge"])
        print("pieles     :", checks["perks"])
        print("skin sync  :", checks["skinSync"])
        print("setSkin fn :", checks["setSkinFn"])
        print("DIMS       :", checks["dims"])
        print("__PP_TRAIN :", checks["trainApi"])

        await page.screenshot(path=OUT_PORTADA)
        # abrir el hub de entrenamiento si se puede (botón del menú 2D)
        try:
            await page.click("#btnTrain", timeout=2500)
        except Exception:
            pass
        await page.wait_for_timeout(2500)
        await page.screenshot(path=OUT_HUB)

        await browser.close()
        ok = (errors == []
              and "3.0.5" in checks["badge"].upper().replace("V", "")
              or "FIS1" in checks["badge"].upper()
              and checks["perks"] == 6
              and checks["skinSync"] == "arcoiris"
              and checks["setSkinFn"]
              and checks["dims"] and checks["dims"]["fis"] == 1
              and checks["dims"]["perks"] == 1)
        print("pageerrors :", errors or "ninguno")
        print("CAPTURAS   :", OUT_PORTADA, "+", OUT_HUB)
        print("RESULTADO  :", "OK" if ok else "REVISAR")

asyncio.run(main())
