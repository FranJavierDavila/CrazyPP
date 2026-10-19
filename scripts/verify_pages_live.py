#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_pages_live.py — Verificación EN VIVO de GitHub Pages.
Carga https://franjavierdavila.github.io/CrazyPP/game.html en Chromium headless
y afirma: __PP_VERSION correcto, 0 respuestas 4xx/5xx del sitio, 0 peticiones
rotas, 0 pageerrors. Uso: python3 scripts/verify_pages_live.py [versión]
"""
import asyncio
import sys

ORIGIN = 'https://franjavierdavila.github.io'
URL = ORIGIN + '/CrazyPP/game.html'
EXPECTED = sys.argv[1] if len(sys.argv) > 1 else '3.6.2-SDK2'


async def run_once():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        # ronda 14: opt-out de telemetría (pp_tele=0) ANTES de que corra el
        # juego — los bots de verificación NO contaminan la producción D1
        # con boots '2d' (el 15:48-16:09 del 10-19 eran verify/smoke bots)
        await page.add_init_script(
            "try { localStorage.setItem('pp_tele','0'); } catch (e) {}"
        )
        bad, perr, nreq = [], [], 0

        def on_resp(r):
            nonlocal nreq
            if r.url.startswith(ORIGIN):
                nreq += 1
                if r.status >= 400:
                    path = r.url.split(ORIGIN)[1]
                    if not path.startswith('/CrazyPP/socket.io') and path != '/favicon.ico':
                        bad.append((r.status, path))

        def on_fail(r):
            if r.url.startswith(ORIGIN) and r.failure and 'ERR_ABORTED' not in str(r.failure):
                bad.append(('FAIL', r.url.split(ORIGIN)[1]))

        page.on('response', on_resp)
        page.on('requestfailed', on_fail)
        page.on('pageerror', lambda e: perr.append(str(e)))
        await page.goto(URL, wait_until='domcontentloaded', timeout=60_000)
        await page.wait_for_timeout(22_000)
        ver = await page.evaluate('() => window.__PP_VERSION || null')
        await browser.close()
        return ver, bad, perr, nreq


for intento in (1, 2):
    ver, bad, perr, nreq = asyncio.run(run_once())
    print(f'intento {intento}: __PP_VERSION={ver} · peticiones al sitio={nreq}')
    if ver == EXPECTED and not bad and not perr:
        print(f'✓ PAGES EN VIVO: CRAZY PING PONG V{EXPECTED} arranca desde GitHub Pages '
              f'({nreq} peticiones OK · 0 fallos de red · 0 pageerrors)')
        sys.exit(0)
    print('  detalle:', bad[:5], perr[:2])
print('✗ verificación en vivo fallida')
sys.exit(1)
