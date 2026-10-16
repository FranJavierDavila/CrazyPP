#!/usr/bin/env python3
"""QA v3.0.8-TRN1 (base de trabajo entregada por el dueño, «v3.8»):
  1) la página carga sin pageerrors
  2) badge V3.0.8-TRN1 en portada 2D
  3) herencia intacta: DIMS.physicsRealism=1, paddlePerks=1, trainGamify=1,
     __PP_TRAIN, __PP_LIVE (CRAZY TV), pieles __PP_SET_PADDLE_SKIN
  4) intro oficial servida (5.779.719 B, sha 3f58e634…) y el visor la lee
Capturas: download/qa_trn1_portada.png + qa_trn1_intro.png
"""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_PORTADA = "/home/z/my-project/download/qa_trn1_portada.png"
OUT_INTRO = "/home/z/my-project/download/qa_trn1_intro.png"
INTRO_SIZE = 5779719

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        checks = await page.evaluate("""async () => {
          const out = {};
          out.badge = (document.querySelector('#verBadge') || {}).textContent || '';
          out.version = window.__PP_VERSION || null;
          out.dims = (window.__ppDebug && window.__ppDebug.DIMS) ? {
            fis: window.__ppDebug.DIMS.physicsRealism,
            perks: window.__ppDebug.DIMS.paddlePerks,
            gamify: window.__ppDebug.DIMS.trainGamify,
          } : null;
          out.train = !!window.__PP_TRAIN;
          out.live = typeof window.__PP_LIVE !== 'undefined';
          out.setSkin = typeof window.__PP_SET_PADDLE_SKIN === 'function';
          out.perksN = window.__PP_PADDLE_PERKS ? Object.keys(window.__PP_PADDLE_PERKS).length : 0;
          out.introbtn = !!document.querySelector('#introbtn');
          const r = await fetch('/assets/intro.mp4');
          const buf = await r.arrayBuffer();
          out.introStatus = r.status; out.introSize = buf.byteLength;
          const h = await crypto.subtle.digest('SHA-256', buf);
          out.introSha = [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
          return out;
        }""")
        for k, v in checks.items():
            print(f"{k:12s}: {v}")

        await page.screenshot(path=OUT_PORTADA)
        await page.evaluate("document.querySelector('#introbtn').click()")
        await page.wait_for_timeout(3000)
        meta = await page.evaluate("""async () => {
          const ov = document.querySelector('#introov');
          const v = document.querySelector('#introvid');
          let dur = null;
          try { if (v.readyState < 1) await new Promise(r => { v.onloadedmetadata = r; setTimeout(r, 5000); });
                dur = v.duration; } catch (e) {}
          return { overlayOpen: !!(ov && ov.classList.contains('open')),
                   readyState: v ? v.readyState : -1, duration: dur };
        }""")
        print("visor intro :", meta)
        await page.screenshot(path=OUT_INTRO)

        await browser.close()

        ok = ("3.0.8-TRN1" in checks["badge"] and checks["version"] == "3.0.8-TRN1"
              and checks["dims"] and checks["dims"]["fis"] == 1
              and checks["dims"]["perks"] == 1 and checks["dims"]["gamify"] == 1
              and checks["train"] and checks["live"] and checks["setSkin"]
              and checks["perksN"] == 6
              and checks["introStatus"] == 200
              and checks["introSize"] == INTRO_SIZE
              and checks["introSha"].startswith("3f58e634")
              and meta["overlayOpen"] and meta["duration"]
              and 9.5 <= meta["duration"] <= 10.5
              and errors == [])
        print("pageerrors  :", errors or "ninguno")
        print("CAPTURAS    :", OUT_PORTADA, "+", OUT_INTRO)
        print("RESULTADO   :", "OK" if ok else "REVISAR")

asyncio.run(main())
