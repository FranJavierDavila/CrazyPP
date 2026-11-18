#!/usr/bin/env python3
"""QA del HUB /descargas · V3.5.1-IMP2. Uso: python3 scripts/qa_descargas_v351.py"""
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
    'crazypp-v351-imp2-COMPLETO.zip': 125088171,
    'crazypp-v351-imp2-ligera.zip': 11451188,
    'crazypp-v351-imp2-CLOUDFLARE.zip': 125075797,
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
        chk(html.count('v351-imp2') >= 3, f'enlaces v351-imp2 ({html.count("v351-imp2")})')
        chk(html.count('3.5.1-IMP2') >= 6, f'menciones 3.5.1-IMP2 ({html.count("3.5.1-IMP2")})')
        for kw in ('REACTOR DE IMPULSO', 'golpeo de la pala', 'pistola láser',
                   'desintegran', 'mitad de pequeños', 'velocidad lumínica',
                   'atractor', 'núcleo', 'ASTRO', 'ESCUDO DE PALA',
                   'etapa 4', 'PRECISIÓN CCD', 'barrido CCD'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', 'v350-esc1',
                      '3.1.0-SRV2', '3.2.0-ORB1', '3.2.1-ORB2', '3.3.0-NUC1',
                      '3.4.0-IMP1', '3.4.1-RIV1', '3.5.0-ESC1'):
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
        chk("const VERSION = '3.5.1-IMP2'" in cuerpo, 'gateway: game.html = 3.5.1-IMP2')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del núcleo')
        mod = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        chk('class EscudoCasco' in mod and "id: 'escudo'" in mod,
            'gateway: módulo sirve el ESCUDO DE PALA (etapa 4)')
        chk("{ kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' }" in mod,
            'gateway: impulso en la etapa 2')
        chk('cubeS: 0.16, cubeHitR: 0.14' in mod, 'gateway: cubos a la mitad (0,16 m)')
        chk('dianaMat' in mod and 'uDissolve' in mod, 'gateway: desintegración de dianas')
        chk('_atractorSepara' in mod, 'gateway: atractor sin penetraciones')
        chk('alphaTest: ventanal ? 0.35 : 0' in mod, 'gateway: ventanales con cristal recortado')
        chk("(D.tableCenterZ || -1.6) - 1.70" in mod, 'gateway: ASTRO a distancia fija (z −3,30)')
        chk('(D.tableCenterZ || -1.6) - 2.22' not in mod, 'gateway: sin el spot antiguo (z −3,82)')
        man = await (await RC.get(GW + '/championships/estacion_orbital/manifest.json')).json()
        chk(man.get('version') == 12, 'gateway: manifest v12')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = v3.5.1')
        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')
        # cristal recortado servido por el gateway
        for f in ('izquierda.png', 'derecha.png'):
            art = await RC.get(GW + '/championships/estacion_orbital/assets/reactor_impulso/' + f)
            cuerpo_art = await art.body()
            chk(len(cuerpo_art) > 2000000, f'gateway: {f} servido ({len(cuerpo_art):,} B)')
        diana = await RC.head(GW + '/championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png')
        chk(int(diana.headers.get('content-length') or -1) == 409356,
            'gateway: diana_quantica.png byte-exacta')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_imp2_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
