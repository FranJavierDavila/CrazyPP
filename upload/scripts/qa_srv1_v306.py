#!/usr/bin/env python3
"""QA v3.0.6-SRV1 · INTRO OFICIAL:
  1) la página carga sin pageerrors
  2) badge V3.0.6-SRV1 en portada 2D
  3) el intro servido en /assets/intro.mp4 es el MONTAJE OFICIAL
     (5.779.719 B, sha256 3f58e634…, faststart verificado en disco)
  4) el visor 🎬 INTRO abre el overlay con el vídeo y lee metadatos (~10 s)
  5) DIMS de la FIS1 intactos (física viva + perks) — sin regresión
Capturas: download/qa_srv1_portada.png + qa_srv1_intro.png
"""
import asyncio, json, hashlib, urllib.request
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_PORTADA = "/home/z/my-project/download/qa_srv1_portada.png"
OUT_INTRO = "/home/z/my-project/download/qa_srv1_intro.png"
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
        await page.wait_for_timeout(6000)

        checks = await page.evaluate("""async () => {
          const out = {};
          out.badge = (document.querySelector('#verBadge') || {}).textContent || '';
          out.introbtn = !!document.querySelector('#introbtn');
          out.vid = (() => { const v = document.querySelector('#introvid');
                             return v ? {src: v.getAttribute('src'), muted: v.muted,
                                         playsinline: v.hasAttribute('playsinline')} : null; })();
          // el intro servido debe ser el oficial (tamaño + sha256 del primer byte al final)
          const r = await fetch('/assets/intro.mp4');
          const buf = await r.arrayBuffer();
          out.introStatus = r.status;
          out.introSize = buf.byteLength;
          const dig = new Uint8Array(buf);
          // sha256 vía crypto.subtle
          const h = await crypto.subtle.digest('SHA-256', buf);
          out.introSha = [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('').slice(0, 16);
          out.dims = (window.__ppDebug && window.__ppDebug.DIMS) ? {
            fis: window.__ppDebug.DIMS.physicsRealism,
            perks: window.__ppDebug.DIMS.paddlePerks,
          } : null;
          out.version = window.__PP_VERSION || null;
          return out;
        }""")
        print("badge        :", checks["badge"])
        print("__PP_VERSION :", checks["version"])
        print("boton intro  :", checks["introbtn"], "· video:", checks["vid"])
        print("intro served :", checks["introStatus"], "·", checks["introSize"], "B · sha", checks["introSha"])
        print("DIMS FIS1    :", checks["dims"])

        # abrir el visor de intro y esperar metadatos
        await page.screenshot(path=OUT_PORTADA)
        # click JS directo: la portada puede interceptar el click sintético
        await page.evaluate("document.querySelector('#introbtn').click()")
        await page.wait_for_timeout(3000)
        meta = await page.evaluate("""async () => {
          const ov = document.querySelector('#introov');
          const v = document.querySelector('#introvid');
          let dur = null;
          try { if (v.readyState < 1) await new Promise(r => { v.onloadedmetadata = r; setTimeout(r, 5000); });
                dur = v.duration; } catch (e) {}
          return { overlayOpen: ov && ov.classList.contains('open'),
                   readyState: v ? v.readyState : -1, duration: dur };
        }""")
        print("visor intro  :", meta)
        await page.screenshot(path=OUT_INTRO)

        await browser.close()

        ok = ("3.0.6" in checks["badge"] and checks["version"] == "3.0.6-SRV1"
              and checks["introbtn"]
              and checks["vid"] and checks["vid"]["src"] == "assets/intro.mp4"
              and checks["introStatus"] == 200
              and checks["introSize"] == INTRO_SIZE
              and checks["introSha"].startswith("3f58e634")
              and checks["dims"] and checks["dims"]["fis"] == 1
              and checks["dims"]["perks"] == 1
              and meta["overlayOpen"] and meta["duration"] and 9.5 <= meta["duration"] <= 10.5
              and errors == [])
        print("pageerrors   :", errors or "ninguno")
        print("CAPTURAS     :", OUT_PORTADA, "+", OUT_INTRO)
        print("RESULTADO    :", "OK" if ok else "REVISAR")

asyncio.run(main())
