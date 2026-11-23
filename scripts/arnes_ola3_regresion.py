#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Arnés de regresión en vivo para la OLA 3 (r129).

C2: comprueba que el juego arranca SIN los recursos embebidos y que los
assets externos (pala, voz, música, iconos, portada) se cargan con red
limpia. No sustituye a qa_rendimiento: lo complementa mirando la RED."""
import asyncio
import time

from playwright.async_api import async_playwright

OK, FALLO = [], []


def puerta(nombre, cond, detalle=''):
    (OK if cond else FALLO).append(f'{nombre}{(" · " + detalle) if detalle else ""}')


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--enable-unsafe-swiftshader',
                                          '--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        errores, fallos_red, pedidos = [], [], {}

        def en_respuesta(r):
            try:
                url = r.url
                if '/assets/' in url or url.endswith('.json') or '/vendor/' in url:
                    pedidos[url] = r.status
                    if r.status >= 400:
                        fallos_red.append(f'{r.status} {url}')
            except Exception:  # noqa
                pass

        pg.on('pageerror', lambda e: errores.append(str(e)))
        pg.on('response', en_respuesta)
        t0 = time.monotonic()
        await pg.goto('http://localhost:3000/game.html', wait_until='domcontentloaded')
        await pg.wait_for_function('() => window.__PP_GAME && window.__PP_VERSION', timeout=60000)
        boot_ms = (time.monotonic() - t0) * 1000
        version = await pg.evaluate('window.__PP_VERSION')

        # el menú VR se pinta con los iconos externos: entrar como en el juego real
        await pg.click('#vrbtn')
        await pg.wait_for_timeout(4000)
        # gesto para la música (el tail arranca el audio con el primer gesto)
        await pg.mouse.click(640, 400)
        await pg.wait_for_timeout(3500)

        def pedidos_de(fragmento):
            return [u for u in pedidos if fragmento in u]

        puerta('boot hasta __PP_GAME', boot_ms > 0 and version == '3.6.210-SDK6',
               f'{boot_ms:.0f} ms · v{version}')
        puerta('0 pageerrors', len(errores) == 0, '; '.join(errores[:3]))
        puerta('0 fallos de red en /assets/ + /vendor/', len(fallos_red) == 0,
               '; '.join(fallos_red[:4]))
        puerta('pala GLB externa servida', any('/assets/pala/pala.glb' in u and s == 200
                                               for u, s in pedidos.items()))
        puerta('portada servida (head CSS + body hero)',
               any('/assets/externos/portada.jpg' in u and s == 200 for u, s in pedidos.items()))
        puerta('iconos de menú servidos (>= 8)', len(pedidos_de('/assets/externos/icono_')) >= 8,
               f'{len(pedidos_de("/assets/externos/icono_"))} iconos')
        puerta('banco de voz ES descargado', any('/assets/audio/voz_es.json' in u and s == 200
                                                 for u, s in pedidos.items()))
        puerta('música OGG pedida tras el gesto',
               any('/assets/externos/musica.ogg' in u for u in pedidos),
               f'{len(pedidos_de("/assets/externos/musica.ogg"))} pedido(s)')
        logos = pedidos_de('/assets/externos/logo_menu.jpg')
        puerta('logo del menú servido', bool(logos) and all(pedidos[u] == 200 for u in logos))

        heap = await pg.evaluate('performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1048576) : 0')
        if heap:
            puerta('heap estable (< 300 MB)', 0 < heap < 300, f'{heap} MB')
        await b.close()

    print(f'== REGRESIÓN VIVA OLA 3 · {len(OK)} OK · {len(FALLO)} FALLOS ==')
    for l in OK:
        print('  ✓', l)
    for l in FALLO:
        print('  ✗', l)
    raise SystemExit(1 if FALLO else 0)


asyncio.run(main())
