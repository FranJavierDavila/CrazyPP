#!/usr/bin/env python3
"""Sonda: ¿importa limpio el módulo orbital tras NUC1? Captura consola + error."""
import asyncio
import sys

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg = await b.new_page()
        errs, cons = [], []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: cons.append(f'{m.type}: {m.text[:220]}') if m.type in ('error', 'warning') else None)
        await pg.goto('http://localhost:3000/game.html', wait_until='domcontentloaded')
        await pg.wait_for_timeout(1500)
        r = await pg.evaluate("""async () => {
          try {
            const m = await import('/championships/estacion_orbital/index.js?v=' + Date.now());
            return { ok: true, claves: Object.keys(m).slice(0, 6) };
          } catch (e) {
            return { ok: false, err: String(e && e.message || e).slice(0, 400),
                     pila: String(e && e.stack || '').slice(0, 600) };
          }
        }""")
        print('import:', r)
        g = await pg.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { sin: '__PP_GAME' };
          try { G.champs.launch('estacion_orbital'); } catch (e) { return { launch: String(e).slice(0, 300) }; }
          await new Promise(r => setTimeout(r, 5000));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          return { mod: !!mod, ctrl: !!(mod && mod.controller),
                   reactor: !!(mod && mod.controller && mod.controller.reactor) };
        }""")
        print('launch:', g)
        print('pageerrors:', errs[:3])
        print('consola (err/warn):')
        for c in cons[:8]:
            print('  ', c)
        await b.close()

asyncio.run(main())
