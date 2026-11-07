#!/usr/bin/env python3
"""QA del HUB /descargas · V3.4.1-RIV1. Verde = todas las comprobaciones OK.
Uso: python3 scripts/qa_descargas_v341.py"""
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
    'crazypp-v341-riv1-COMPLETO.zip': 123740436,
    'crazypp-v341-riv1-ligera.zip': 11447371,
    'crazypp-v341-riv1-CLOUDFLARE.zip': 123728360,
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
        chk(html.count('v341-riv1') >= 4, f'enlaces v341-riv1 ({html.count("v341-riv1")})')
        chk(html.count('3.4.1-RIV1') >= 6, f'menciones 3.4.1-RIV1 ({html.count("3.4.1-RIV1")})')
        for kw in ('ASTRO', 'pared', 'CLOWN y WIZARD', 'convención de duelos',
                   'REACTOR DE IMPULSO', 'ESTACIÓN ORBITAL', 'cubos cuánticos',
                   'PRECISIÓN CCD', 'Reactor de energía inestable'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', '3.1.0-SRV2', '3.2.0-ORB1',
                      '3.2.1-ORB2', '3.3.0-NUC1', '3.4.0-IMP1'):
            chk(viejo not in html, f'sin residuos de {viejo}')
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
        chk("const VERSION = '3.4.1-RIV1'" in cuerpo, 'gateway: game.html = 3.4.1-RIV1')
        chk('V3.4.1-RIV1' in cuerpo, 'gateway: badge V3.4.1-RIV1')
        mod = await RC.get(GW + '/championships/estacion_orbital/index.js')
        mod_src = await mod.text()
        chk('position.set(1.26, RIV_H / 2' in mod_src,
            'gateway: módulo coloca al ASTRO en la convención de duelos (x 1,26)')
        chk('(D.tableCenterZ || -1.6) - 2.22' in mod_src,
            'gateway: profundidad del ASTRO = −3,82 (misma que CLOWN/WIZARD)')
        chk('position.set(1.62, RIV_H / 2' not in mod_src,
            'gateway: sin la posición antigua del ASTRO (x 1,62 · z −4,5)')
        chk('class ReactorImpulso' in mod_src and "id: 'impulso'" in mod_src,
            'gateway: módulo orbital sirve el Reactor de impulso (etapa 4)')
        chk('class ReactorInestable' in mod_src,
            'gateway: la etapa 2 (reactor NUC1) sigue íntegra')
        man = await (await RC.get(GW + '/championships/estacion_orbital/manifest.json')).json()
        chk(man.get('version') == 10, 'gateway: manifest del orbital = v10')
        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')
        diana = await RC.head(GW + '/championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png')
        chk(int(diana.headers.get('content-length') or -1) == 409356,
            'diana_quantica.png byte-exacta por gateway')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_riv1_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
