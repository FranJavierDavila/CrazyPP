#!/usr/bin/env python3
"""QA del HUB /descargas · V3.6.0-SUP1. Uso: python3 scripts/qa_descargas_v360.py"""
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
    'crazypp-v360-sup1-COMPLETO.zip': 125206366,
    'crazypp-v360-sup1-ligera.zip': 11451838,
    'crazypp-v360-sup1-CLOUDFLARE.zip': 125194235,
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
        chk(html.count('v360-sup1') >= 3, f'enlaces v360-sup1 ({html.count("v360-sup1")})')
        chk(html.count('3.6.0-SUP1') >= 6, f'menciones 3.6.0-SUP1 ({html.count("3.6.0-SUP1")})')
        for kw in ('SUPERPODERES REDEFINIDOS', 'congela la partida', 'rocas en 3D',
                   'vetas de óxido', 'rayo tractor', 'dron', 'ATRAPADA',
                   'caída vertical', 'gravedad cero', 'partículas blancas',
                   'risa', 'enfado', 'ASTRO', 'diana se ve 2 segundos',
                   'siempre vuelve a botar', 'REACTOR DE IMPULSO',
                   'ESCUDO DE PALA', 'etapa 4', 'PRECISIÓN CCD'):
            chk(kw in html, f'el hub menciona {kw!r}')
        for viejo in ('v310-srv2', 'v312-ccd1', 'v320-orb1', 'v321-orb2',
                      'v330-nuc1', 'v340-imp1', 'v341-riv1', 'v350-esc1',
                      'v351-imp2', '3.1.0-SRV2', '3.2.0-ORB1', '3.2.1-ORB2',
                      '3.3.0-NUC1', '3.4.0-IMP1', '3.4.1-RIV1', '3.5.0-ESC1',
                      '3.5.1-IMP2'):
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
        chk("const VERSION = '3.6.0-SUP1'" in cuerpo, 'gateway: game.html = 3.6.0-SUP1')
        chk('__PP_PADDLE_SWEEP' in cuerpo, 'gateway: puente CCD del núcleo')
        mod = await (await RC.get(GW + '/championships/estacion_orbital/index.js')).text()
        chk('class EscudoCasco' in mod and "id: 'escudo'" in mod,
            'gateway: módulo sirve el ESCUDO DE PALA (etapa 4)')
        chk("{ kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' }" in mod,
            'gateway: impulso en la etapa 2')
        chk('function _geoMeteorito' in mod and 'dronTractor' in mod,
            'gateway: meteoritos 3D + dron del tractor')
        chk('_tractorTrap' in mod and 'caída vertical pura' in mod,
            'gateway: bola atrapada + caída vertical')
        chk('const ATT = 7.5' in mod, 'gateway: gravedad cero atrae la bola')
        chk("this._sfx('risa_astro.mp3')" in mod and "this._sfx('enfado_astro.mp3')" in mod,
            'gateway: audios del ASTRO cableados')
        chk('dianaVis: 2.0' in mod, 'gateway: diana visible 2 s')
        chk('this._restT > 0.6' in mod, 'gateway: reposo → la pelota vuelve a la base')
        chk('this.game.freezeT = Math.max' in mod, 'gateway: freeze real en el aviso')
        chk("(D.tableCenterZ || -1.6) - 1.70" in mod, 'gateway: ASTRO a distancia fija (z −3,30)')
        chk('(D.tableCenterZ || -1.6) - 2.22' not in mod, 'gateway: sin el spot antiguo (z −3,82)')
        man = await (await RC.get(GW + '/championships/estacion_orbital/manifest.json')).json()
        chk(man.get('version') == 13, 'gateway: manifest v13')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'gateway: camino del manifest = v3.6.0')
        intro = await RC.head(GW + '/assets/intro.mp4')
        chk(int(intro.headers.get('content-length') or -1) == 5779719,
            'intro oficial byte-perfecta por gateway')
        # los mp3 del dueño servidos por el gateway, byte-exactos
        for f, esperado in (('risa_astro.mp3', 81408), ('enfado_astro.mp3', 37616)):
            m = await RC.head(GW + '/championships/estacion_orbital/assets/' + f)
            chk(int(m.headers.get('content-length') or -1) == esperado,
                f'gateway: {f} byte-exacto ({esperado} B)')
        # cristal recortado servido por el gateway
        for f in ('izquierda.png', 'derecha.png'):
            art = await RC.get(GW + '/championships/estacion_orbital/assets/reactor_impulso/' + f)
            cuerpo_art = await art.body()
            chk(len(cuerpo_art) > 2000000, f'gateway: {f} servido ({len(cuerpo_art):,} B)')
        diana = await RC.head(GW + '/championships/estacion_orbital/assets/reactor_impulso/diana_quantica.png')
        chk(int(diana.headers.get('content-length') or -1) == 409356,
            'gateway: diana_quantica.png byte-exacta')

        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_sup1_descargas_hub.png')
        await A.close()
        await RC.dispose()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
