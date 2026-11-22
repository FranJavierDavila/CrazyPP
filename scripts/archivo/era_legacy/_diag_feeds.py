#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        await page.goto("http://localhost:3000/game.html", wait_until="load")
        await page.wait_for_timeout(1200)
        out = await page.evaluate("""async () => {
          const res = [];
          const orig = Error.prepareStackTrace;
          // parche global: cualquier feedPracticeBall de CUALQUIER objeto
          // deja traza en window.__feedStacks
          window.__feedStacks = [];
          const patch = (obj) => {
            if (!obj || !obj.feedPracticeBall || obj.__ffPatched) return;
            obj.__ffPatched = true;
            const origFn = obj.feedPracticeBall.bind(obj);
            obj.feedPracticeBall = (...a) => {
              window.__feedStacks.push(new Error().stack.split('\\n').slice(1, 4).join(' | '));
              return origFn(...a);
            };
          };
          // el juego real de la página
          const g = window.__ppGame || window.game || null;
          res.push('juego real: ' + (g ? 'sí' : 'no'));
          if (g) patch(g);
          // busca instancias PingPongGame en window
          for (const k of Object.keys(window)) {
            try {
              const v = window[k];
              if (v && typeof v === 'object' && v.feedPracticeBall && v.ball) patch(v);
            } catch (e) { /* */ }
          }
          return res;
        }""")
        print(out)
        await page.wait_for_timeout(3500)
        stacks = await page.evaluate("window.__feedStacks || []")
        print("feeds en 3.5s:", len(stacks))
        for s in stacks[:4]:
            print("  ·", s)
        await browser.close()

asyncio.run(main())
