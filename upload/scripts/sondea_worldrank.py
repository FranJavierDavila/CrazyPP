#!/usr/bin/env python3
"""Sonda 2: evento a evento de la petición a api.restful-api.dev dentro de la
página + estado de WORLDRANK, para saber por qué cuelga >8 s sin abortar."""
import asyncio
import time
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        t0 = time.time()
        def tag(u):
            return 'restful' if 'restful-api' in u else ('tele' if 'telemetria' in u else 'otra')
        pg.on('request', lambda r: print(f'[{time.time()-t0:6.2f}] REQ  {tag(r.url)} {r.method} {r.url[:90]}'))
        pg.on('requestfinished', lambda r: print(f'[{time.time()-t0:6.2f}] FIN  {tag(r.url)} {r.method} {r.url[:90]}'))
        pg.on('requestfailed', lambda r: print(f'[{time.time()-t0:6.2f}] FAIL {tag(r.url)} {r.method} {r.url[:90]} · {r.failure}'))
        try:
            await pg.goto('http://localhost:3000/game.html', wait_until='commit', timeout=15000)
        except Exception as e:
            print('goto commit fallo:', str(e)[:100])
        for i in range(6):
            await asyncio.sleep(4)
            try:
                st = await pg.evaluate("() => (window.__PP_WORLD && window.__PP_WORLD.status) || 'sin-__PP_WORLD'")
            except Exception:
                st = 'eval-fallo'
            print(f'[{time.time()-t0:6.2f}] WORLDRANK.status = {st!r}')
        await b.close()

asyncio.run(main())
