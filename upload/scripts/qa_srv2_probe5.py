#!/usr/bin/env python3
"""Sonda de depuración del caso 5 (pala mirando fuera) y del sweep del lab."""
import asyncio, json
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"

PROBE = """
() => {
  const L = window.__PP_SERVE_LAB;
  const out = {};
  // caso 5 exacto de la QA
  out.c5 = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, assist: true, tier: 'medium' });
  // variaciones para localizar el fantasma
  out.c5_noswing = L({ yawDeg: 270, pitchDeg: 0, padVelZ: 0, assist: false });
  out.c5_nodrop  = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, ballVelY: 0, assist: false });
  out.c5_far     = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, dist: 0.10, assist: false });
  // caso 2a y 3 con el lab actual (para confirmar el sweep)
  out.c2a = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.06 });
  out.c3  = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, ballVelZ: 1.4 });
  return out;
}
"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await b.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(BASE + "/game.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(4500)
        r = await page.evaluate(PROBE)
        for k, v in r.items():
            print(k, json.dumps(v))
        await b.close()

asyncio.run(main())
