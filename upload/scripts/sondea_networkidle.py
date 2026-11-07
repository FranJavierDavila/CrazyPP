#!/usr/bin/env python3
"""Sonda: qué mantiene la red ocupada tras cargar :3000/game.html (caza del
timeout networkidle de la capa F). Lista peticiones vivas por ventanas."""
import asyncio
import time
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        vivas = {}
        done = []
        def on_req(r):
            vivas[r.url] = time.time()
        def on_done(r):
            done.append((time.time(), r.url))
            vivas.pop(r.url, None)
        pg.on('request', on_req)
        pg.on('requestfinished', on_done)
        pg.on('requestfailed', on_done)
        t0 = time.time()
        try:
            await pg.goto('http://localhost:3000/game.html', wait_until='networkidle', timeout=30000)
            print(f'networkidle alcanzado en {time.time()-t0:.1f} s')
        except Exception as e:
            print(f'NETWORKIDLE TIMEOUT ({time.time()-t0:.1f} s): {str(e)[:80]}')
        print('\n-- peticiones VIVAS al final --')
        for u, t in sorted(vivas.items(), key=lambda kv: kv[1]):
            print(f'  [{time.time()-t:6.1f} s en vuelo] {u[:110]}')
        print('\n-- últimas 12 terminadas --')
        for t, u in done[-12:]:
            print(f'  [{t-t0:6.1f} s] {u[:110]}')
        # conteo de reintentos socket.io
        n_live = sum(1 for _, u in done if '/live/socket.io' in u or 'socket.io' in u)
        print(f'\npeticiones socket.io terminadas: {n_live}')
        await b.close()

asyncio.run(main())
