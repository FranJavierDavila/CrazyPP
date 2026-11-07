#!/usr/bin/env python3
"""QA del JUEGO · V3.2.0-ORB1 (decorado real de Estación Orbital + muros).
Verde = todas las comprobaciones en OK. Uso: python3 scripts/qa_orbital_v320.py"""
import asyncio
import json
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

ORBITAL = 'championships/estacion_orbital'
ASSETS = [
    f'{ORBITAL}/index.js', f'{ORBITAL}/manifest.json',
    f'{ORBITAL}/assets/rival.webp', f'{ORBITAL}/assets/idle.webp',
    f'{ORBITAL}/assets/duelo.webp', f'{ORBITAL}/assets/focused.webp',
    f'{ORBITAL}/assets/surprised.webp', f'{ORBITAL}/assets/panic.webp',
    f'{ORBITAL}/assets/laughing.webp', f'{ORBITAL}/assets/loosing.webp',
    f'{ORBITAL}/assets/picando.webp', f'{ORBITAL}/assets/crazy.webp',
    f'{ORBITAL}/assets/angry.webp', f'{ORBITAL}/assets/victory.webp',
    f'{ORBITAL}/assets/defeated.webp', f'{ORBITAL}/assets/triunfante.webp',
    f'{ORBITAL}/assets/derrotado.webp',
    f'{ORBITAL}/assets/sala_left.jpg', f'{ORBITAL}/assets/sala_right.jpg',
    f'{ORBITAL}/assets/sala_back.jpg', f'{ORBITAL}/assets/sala_front.jpg',
    f'{ORBITAL}/assets/sala_floor.jpg', f'{ORBITAL}/assets/sala_ceil.jpg',
    f'{ORBITAL}/assets/mapa.png', f'{ORBITAL}/assets/tapa.png',
    f'{ORBITAL}/assets/normas_astro.png', f'{ORBITAL}/assets/superpower.png',
    f'{ORBITAL}/assets/pistol.glb', f'{ORBITAL}/assets/insignia.png',
    f'{ORBITAL}/assets/bso.wav',
    f'{ORBITAL}/assets/powerestrellas.png', f'{ORBITAL}/assets/powermeteoritos.png',
    f'{ORBITAL}/assets/powertractor.png', f'{ORBITAL}/assets/powercero.png',
    f'{ORBITAL}/assets/asteroide.png', f'{ORBITAL}/assets/asteroide2.png',
    f'{ORBITAL}/assets/caja.png', f'{ORBITAL}/assets/dron.png',
    f'{ORBITAL}/assets/decor/escena_cohete.png',
    f'{ORBITAL}/assets/decor/escena_astro.png',
    f'{ORBITAL}/assets/decor/escena_lander.png',
    f'{ORBITAL}/assets/decor/escena_telescopio.png',
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== PORTADA (dev :3000) ==')
        await page.goto(BASE + '/game.html', wait_until='networkidle')
        ver = await page.evaluate("window.__PP_VERSION || ''")
        chk(ver == '3.2.0-ORB1', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.2.0-ORB1' in badge, f'badge 2D = {badge!r}')
        dims = await page.evaluate("!!(window.__ppDebug && window.__ppDebug.DIMS)")
        chk(dims, '__ppDebug.DIMS presente (FIS1)')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), '__PP_CCD_LAB presente (CCD1)')
        chk(await page.evaluate("!!window.__PP_SERVE_LAB"), '__PP_SERVE_LAB presente (SRV2)')
        chk(await page.evaluate("!!window.__PP_NORMAS"), '__PP_NORMAS presente (v2.135)')

        print('== NORMAS_SKIN · piel del artista para la estación ==')
        st = await page.evaluate(
            "() => { const d = window.__PP_NORMAS && window.__PP_NORMAS.defs.estacion;"
            " const i = window.__PP_NORMAS && window.__PP_NORMAS.imgs.estacion;"
            " return { def: !!d, url: d && d.url, rect: d && JSON.stringify(d.rect),"
            " cargada: !!(i && i.complete && i.naturalWidth === 1024) }; }")
        chk(st['def'], 'defs.estacion registrada')
        chk(st['url'] == f'{ORBITAL}/assets/normas_astro.png', f"url = {st['url']}")
        chk(st['rect'] == '[152,152,872,432]', f'rect del hueco = {st["rect"]}')
        chk(st['cargada'], 'normas_astro.png precargada (1024 px)')

        print('== Registro de campeonatos ==')
        reg = await page.evaluate(
            "fetch('championships/championships.json').then(r=>r.json())")
        ids = [e['id'] if isinstance(e, dict) else e for e in reg['championships']]
        chk('estacion_orbital' in ids, f'5 campeonatos registrados: {ids}')
        chk(len(ids) == 5, 'el registro sigue en 5 campeonatos')

        print('== Módulo orbital: muros + etiqueta de la casa ==')
        src = await page.evaluate(
            f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in ('class EOArkanoid', "id: 'muro1'", "id: 'muro2'",
                   "superpower.png", "GUN_ART_URL", "_arrancarMuro",
                   "this.arkanoid = new EOArkanoid", 'ARK2_CFG',
                   "rivalEstado('crazy')", "a._despuesDePrueba()"):
            chk(tk in src, f'index.js contiene {tk!r}')
        chk('troquel1' not in src, 'sin restos de troquel1 en el módulo')

        print('== Manifest v6 (ASTRO + muros) ==')
        man = await page.evaluate(
            f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man['version'] == 6, f"manifest version = {man['version']}")
        chk(man['rival']['name'] == 'ASTRO', f"rival = {man['rival']['name']}")
        kinds = {s['id']: s['kind'] for s in man['stages']}
        chk(kinds.get('muro1') == 'arkanoid' and kinds.get('muro2') == 'arkanoid',
            f"etapas 2/4 = arkanoid {kinds}")
        chk(len(man['rival']['states']) >= 12, f"estados del rival = {len(man['rival']['states'])}")
        decor = [p['file'] for p in man['decor']['pieces']]
        chk(len(decor) == 4 and all('escena_' in f for f in decor),
            f'decor = 4 recortables {decor}')

        print(f'== Assets del dueño ({len(ASSETS)} ficheros HTTP 200) ==')
        codes = await page.evaluate(
            "() => Promise.all(" + json.dumps(ASSETS) + ".map(u => fetch(u).then(r => r.status)))")
        malos = [a for a, c in zip(ASSETS, codes) if c != 200]
        chk(not malos, f'{len(ASSETS) - len(malos)}/{len(ASSETS)} OK' + (f' · fallos: {malos}' if malos else ''))
        gone = await page.evaluate(
            "() => fetch('championships/estacion_orbital/assets/decor/troquel1.png').then(r=>r.status)")
        chk(gone == 404, f'troquel1.png retirado ({gone})')
        intro = await page.evaluate(
            "() => fetch('assets/intro.mp4', {method:'HEAD'}).then(r=>+r.headers.get('content-length'))")
        chk(intro == 5779719, f'intro oficial = {intro} B')

        print('== Limpieza de carga ==')
        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_v320_portada.png')
        await browser.close()

        print('\n== GATEWAY (:81) ==')
        async with async_playwright() as p:
            b2 = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
            pg2 = await b2.new_page()
            err2 = []
            pg2.on('pageerror', lambda e: err2.append(str(e)))
            await pg2.goto(GW + '/game.html', wait_until='networkidle')
            chk(await pg2.evaluate("window.__PP_VERSION") == '3.2.0-ORB1',
                'gateway sirve 3.2.0-ORB1')
            chk(not err2, f'gateway 0 pageerrors ({len(err2)})')
            await b2.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
