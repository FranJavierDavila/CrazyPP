#!/usr/bin/env python3
"""QA del HUB /descargas · V3.2.1-ORB2. Verde = todas las comprobaciones OK.
Uso: python3 scripts/qa_descargas_v321.py"""
import asyncio
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
GW = 'http://localhost:81'
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

ZIPS = {
    'crazypp-v321-orb2-COMPLETO.zip': 113684493,
    'crazypp-v321-orb2-ligera.zip': 11460299,
    'crazypp-v321-orb2-CLOUDFLARE.zip': 113672612,
    'crazypp-live-service-SOLO.zip': 6089,
}

async def tam(base, nombre):
    r = await RC.head(base + '/descargas/' + nombre)
    return int(r.headers.get('content-length') or -1)

async def main():
    global A, RC
    async with async_playwright() as p:
        RC = await p.request.new_context()
        A = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await A.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== HUB /descargas (dev :3000) ==')
        await page.goto(BASE + '/descargas', wait_until='networkidle')
        html = await page.content()
        chk(html.count('v321-orb2') >= 4, f'enlaces v321-orb2 ({html.count("v321-orb2")})')
        chk(html.count('3.2.1-ORB2') >= 6, f'menciones 3.2.1-ORB2 ({html.count("3.2.1-ORB2")})')
        for kw in ('ESTACIÓN ORBITAL', 'ASTRO', 'forajido', 'tapa de la casa',
                   'SUPERPOWER!!', 'altura de la red', 'PRECISIÓN CCD',
                   'expresiones'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', '3.1.0-SRV2', '3.2.0-ORB1'):
            chk(viejo not in html, f'sin residuos de {viejo}')
        # la herencia sí se nombra (la tarjeta COMPLETO cita la base; Next
        # la duplica en el payload RSC, por eso 2)
        chk(html.count('3.1.2-CCD1') <= 2,
            f'herencia v3.1.2-CCD1 citada con cuentagotas ({html.count("3.1.2-CCD1")})')
        botones = await page.locator('a[download]').count()
        chk(botones == 4, f'4 botones de descarga ({botones})')

        print('== ZIPs byte-exactos vía dev (:3000) ==')
        for n, esperado in ZIPS.items():
            t = await tam(BASE, n)
            chk(t == esperado, f'{n} = {t:,} B (esperado {esperado:,})')

        print('== ZIPs byte-exactos vía gateway (:81) ==')
        for n, esperado in ZIPS.items():
            t = await tam(GW, n)
            chk(t == esperado, f'{n} = {t:,} B vía gateway')

        print('== Juego servido por gateway ==')
        r = await RC.get(GW + '/game.html')
        cuerpo = await r.text()
        chk("const VERSION = '3.2.1-ORB2'" in cuerpo, 'gateway: game.html = 3.2.1-ORB2')
        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_v321_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
