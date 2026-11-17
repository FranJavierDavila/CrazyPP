#!/usr/bin/env python3
"""prueba RAF: ¿a cuántos Hz corre requestAnimationFrame en 2 pestañas headless?"""
import asyncio
from playwright.async_api import async_playwright

JS_RAF = """async () => {
  let n = 0;
  const t0 = performance.now();
  await new Promise((res) => {
    const f = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(f); else res(); };
    requestAnimationFrame(f);
  });
  return { rafHz: Math.round(n / 2), hidden: document.hidden, timers: await new Promise((r) => {
    let m = 0; const i = setInterval(() => { if (++m >= 10) { clearInterval(i); r(10); } }, 16);
  }) };
}"""


async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader",
                                           "--use-fake-device-for-media-stream"])
        for n_pages in (1, 2):
            pages = [await b.new_page(viewport={"width": 480, "height": 320}) for _ in range(n_pages)]
            for p in pages:
                await p.goto("about:blank")
            res = []
            for p in pages:
                res.append(await p.evaluate(JS_RAF))
            print(f"{n_pages} página(s): {res}", flush=True)
            for p in pages:
                await p.close()
        await b.close()

asyncio.run(main())
