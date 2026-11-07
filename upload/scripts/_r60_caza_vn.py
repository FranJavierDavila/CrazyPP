#!/usr/bin/env python3
"""r60 · pila COMPLETA del add(undefined) de valle_neon (n.º de línea exacto)."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        p = await b.new_page()
        await p.goto("http://localhost:3000/game.html", wait_until="load")
        await p.wait_for_timeout(900)
        await p.evaluate("""() => {
          window.__stk = [];
          const ce = console.error.bind(console);
          console.error = (...a) => {
            try {
              const m = a.map(x => (x && x.message) ? x.message : String(x)).join(' ');
              if (/Object3D/.test(m)) window.__stk.push(new Error().stack);
            } catch (e) {}
            ce(...a);
          };
        }""")
        r = await p.evaluate("""async () => {
          const g = window.__game;
          await g.champs.launch('valle_neon');
          await new Promise(r => setTimeout(r, 800));
          return 'lanzado';
        }""")
        stk = await p.evaluate("() => window.__stk")
        print("retorno:", r, "| capturas:", len(stk))
        for s in stk[:2]:
            print(s[:1600])
        await b.close()

asyncio.run(main())
