#!/usr/bin/env python3
"""Depuración de arranque: qué globals hay y qué consola emite game.html."""
import asyncio
from playwright.async_api import async_playwright

BASE = 'http://localhost:3000/game.html'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        page = await b.new_page()
        cons = []
        page.on('console', lambda m: cons.append(m.type + ': ' + m.text[:200]))
        page.on('pageerror', lambda e: cons.append('PAGEERROR: ' + str(e)[:300]))
        await page.goto(BASE, wait_until='domcontentloaded', timeout=60000)
        for _ in range(12):
            await page.wait_for_timeout(5000)
            g = await page.evaluate(
                "() => ({ pp: !!window.__PP_GAME, train: !!window.__PP_TRAIN,"
                " ver: window.__PP_VERSION || null,"
                " ready: document.readyState })")
            print(g)
            if g.get('pp'):
                break
        print('--- consola (últimas 25) ---')
        for c in cons[-25:]:
            print(' ', c)
        await b.close()

asyncio.run(main())
