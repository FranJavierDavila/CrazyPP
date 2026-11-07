#!/usr/bin/env python3
"""QA del HUB /descargas · V3.5.0-ESC1. Uso: python3 scripts/qa_descargas_v350.py"""
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
    'crazypp-v350-esc1-COMPLETO.zip': 124599669,
    'crazypp-v350-esc1-ligera.zip': 11451102,
    'crazypp-v350-esc1-CLOUDFLARE.zip': 124587189,
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
        chk(html.count('v350-esc1') >= 3, f'enlaces v350-esc1 ({html.count("v350-esc1")})')
        chk(html.count('3.5.0-ESC1') >= 6, f'menciones 3.5.0-ESC1 ({html.count("3.5.0-ESC1")})')
        for kw in ('ESCUDO DE PALA', 'DEFENSA DEL CASCO', 'orbes de plasma', 'Sobrecarga',
                   'CENTINELA', 'nave abordadora', 'INTEGRIDAD DEL CASCO',
                   'REACTOR DE IMPULSO', 'etapa 2', 'PRECISIÓN CCD', 'zurdos'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', '3.1.0-SRV2',
                      '3.2.0-ORB1', '3.2.1-ORB2', '3.3.0-NUC1', '3.4.0-IMP1', '3.4.1-RIV1'):
            chk(viejo not in html, f'sin residuos de {viejo}')
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
        chk("const VERSION = '3.5.0-ESC1'" in cuerpo, 'gateway: game.html = 3.5.0-ESC1')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del escudo')
        mod = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        chk('class EscudoCasco' in mod and "id: 'escudo'" in mod,
            'gateway: módulo sirve el ESCUDO DE PALA (etapa 4)')
        chk("{ kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' }" in mod,
            'gateway: impulso en la etapa 2')
        chk('position.set(1.26, RIV_H / 2' in mod, 'gateway: ASTRO v3.4.1 intacto')
        man = await (await RC.get(GW + '/championships/estacion_orbital/manifest.json')).json()
        chk(man.get('version') == 11, 'gateway: manifest v11')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = v3.5.0')
        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')
        frente = await RC.head(GW + '/championships/estacion_orbital/assets/escudo_pala/frente.jpg')
        chk(int(frente.headers.get('content-length') or -1) > 50000,
            'gateway: arte del escudo servido (frente.jpg)')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_esc1_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
