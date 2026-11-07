#!/usr/bin/env python3
"""QA del JUEGO · V3.2.1-ORB2 (ajuste fino de la Estación Orbital).
Verde = todas las comprobaciones en OK. Uso: python3 scripts/qa_orbital_v321.py"""
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
        chk(ver == '3.2.1-ORB2', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.2.1-ORB2' in badge, f'badge 2D = {badge!r}')
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

        print('== Módulo orbital ORB2: rival forajido + SuperPower de la casa + expresiones ==')
        src = await page.evaluate(
            f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in ('class EOArkanoid', "id: 'muro1'", "id: 'muro2'",
                   "superpower.png", "GUN_ART_URL", "_arrancarMuro",
                   'class PwSignEO', 'this.pwSign = new PwSignEO',
                   'const RIV_H = 2.15', 'position.set(1.62, RIV_H / 2',
                   'this.cartel.position.set(-2.2, 1.5, -5.28)',
                   'x: 1197, y: 335, r: 115', 'TAPA_W = 240 / 1376',
                   '_exprOnPoint', "_exprSet('angry', 2.6)",
                   "_exprSet('laughing', 2.4)", "_exprSet('crazy', 3.4)",
                   "_exprSet('picando', 2.2)", "'loosing'", "'panic'",
                   'this.pwSign.update(dt)', 'pwSign.dispose()',
                   'a._despuesDePrueba()'):
            chk(tk in src, f'index.js contiene {tk!r}')
        # fuera el panel provisional y la posición antigua
        for viejo in ('this.powerSign', '_psCv', 'zRival', 'PlaneGeometry(0.9, 1.75)',
                      'this.cartel.position.set(-2.2, 1.46, -5.44)',
                      'TAPA_W = 165 / 1380'):
            chk(viejo not in src, f'sin restos de {viejo!r}')
        chk(src.count('rivalEstado(') >= 14, f'rivalEstado llamado en muchos puntos ({src.count("rivalEstado(")})')

        print('== Manifest v7 (ASTRO + ajuste fino) ==')
        man = await page.evaluate(
            f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man['version'] == 7, f"manifest version = {man['version']}")
        chk(man['rival']['name'] == 'ASTRO', f"rival = {man['rival']['name']}")
        kinds = {s['id']: s['kind'] for s in man['stages']}
        chk(kinds.get('muro1') == 'arkanoid' and kinds.get('muro2') == 'arkanoid',
            f"etapas 2/4 = arkanoid {kinds}")
        chk(len(man['rival']['states']) >= 12, f"estados del rival = {len(man['rival']['states'])}")
        decor = [p['file'] for p in man['decor']['pieces']]
        chk(len(decor) == 4 and all('escena_' in f for f in decor),
            f'decor = 4 recortables {decor}')
        chk(any('ORB2' in n for n in man.get('notes', [])), 'nota ORB2 en el manifest')

        print(f'== Assets del dueño ({len(ASSETS)} ficheros HTTP 200) ==')
        codes = await page.evaluate(
            "() => Promise.all(" + json.dumps(ASSETS) + ".map(u => fetch(u).then(r => r.status)))")
        malos = [a for a, c in zip(ASSETS, codes) if c != 200]
        chk(not malos, f'{len(ASSETS) - len(malos)}/{len(ASSETS)} OK' + (f' · fallos: {malos}' if malos else ''))
        intro = await page.evaluate(
            "() => fetch('assets/intro.mp4', {method:'HEAD'}).then(r=>+r.headers.get('content-length'))")
        chk(intro == 5779719, f'intro oficial = {intro} B')

        print('== Escena en vivo: rival + cartel + mapa en su sitio ==')
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          if (!ctrl || !ctrl.rivalMesh) return { error: 'sin ctrl/build' };
          const r = ctrl.rivalMesh.position;
          const okRival = Math.abs(r.x - 1.62) < 1e-3 && Math.abs(r.y - 1.075) < 1e-3 &&
                          Math.abs(r.z - (-4.5)) < 1e-3;
          const geo = ctrl.rivalMesh.geometry.parameters;
          const okAlto = Math.abs(geo.height - 2.15) < 1e-6 && Math.abs(geo.width - 1.075) < 1e-6;
          const okCartel = Math.abs(ctrl.cartel.position.z - (-5.28)) < 1e-3;
          const pwOk = !!ctrl.pwSign && !!ctrl.pwSign.group && ctrl.pwSign.group.parent === G.rig;
          ctrl.pwSign.show(ctrl._A('powertractor.png'));
          ctrl.pwSign.update(0.016); ctrl.pwSign.update(0.8);
          const p = ctrl.pwSign.group.position;
          const okRed = Math.abs(p.y - 1.0525) < 1e-3 && Math.abs(p.z - (-1.3)) < 1e-3 &&
                        ctrl.pwSign.group.visible;
          ctrl.pwSign.hide();
          const mapa = ctrl.mapa;
          const nodos = mapa && mapa.nodesPx;
          const okNodo5 = nodos && nodos[4].y === 335 && nodos[4].x === 1197;
          const okTapas = !!(mapa && mapa.tapas && mapa.tapas.length === 4);
          // expresiones: mismo estado no recarga; cambio sí
          ctrl._rivalEstado = '';
          ctrl.rivalEstado('laughing');
          const e1 = ctrl._rivalEstado;
          ctrl.rivalEstado('laughing');
          const e2 = ctrl._rivalEstado;
          const sinRecarga = (e1 === 'laughing' && e2 === 'laughing');
          ctrl.rivalEstado('idle');
          return { okRival, okAlto, okCartel, pwOk, okRed, okNodo5, okTapas,
                   sinRecarga, alto: geo.height, ancho: geo.width };
        }""")
        if esc.get('error'):
            chk(False, f"escena: {esc['error']}")
        else:
            chk(esc['okRival'], 'ASTRO en el spot del forajido (1,62 / 1,075 / −4,5)')
            chk(esc['okAlto'], f"plano cuerpo entero 2,15 m ({esc.get('alto')}×{esc.get('ancho')})")
            chk(esc['okCartel'], 'cartel de bienvenida despegado de la pared (z −5,28)')
            chk(esc['pwOk'], 'PwSignEO montado bajo el rig')
            chk(esc['okRed'], 'cartel SuperPower anclado a la red (y 1,0525 · z −1,3)')
            chk(esc['okNodo5'], 'mapa: nodo 5 re-medido (1197, 335)')
            chk(esc['okTapas'], 'mapa: 4 tapas para las etapas futuras')
            chk(esc['sinRecarga'], 'rivalEstado anti-recarga operativo')

        print('== Limpieza de carga ==')
        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_v321_portada.png')
        await browser.close()

        print('\n== GATEWAY (:81) ==')
        async with async_playwright() as p:
            b2 = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
            pg2 = await b2.new_page()
            err2 = []
            pg2.on('pageerror', lambda e: err2.append(str(e)))
            await pg2.goto(GW + '/game.html', wait_until='networkidle')
            chk(await pg2.evaluate("window.__PP_VERSION") == '3.2.1-ORB2',
                'gateway sirve 3.2.1-ORB2')
            chk(not err2, f'gateway 0 pageerrors ({len(err2)})')
            await b2.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
