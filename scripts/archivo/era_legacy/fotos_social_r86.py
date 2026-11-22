#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fotos_social_r86 — capturas del MEDALLÓN y de la TARJETA DE INVITACIÓN.

Levanta el mock del worker (qa_social_v3678), deja 2 jugadores online,
fuerza una invitación y captura:
  1. el HUB con el medallón VERDE (número de jugadores) sobre Multijugador;
  2. el HUB con el medallón DORADO pulsante (invitaciones);
  3. el submenú multi con la TARJETA «INVITACIÓN RECIBIDA» + código + UNIRSE.
Las fotos van a download/fotos_r86/ para el dueño.
"""
import asyncio
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "qs", os.path.join(os.path.dirname(os.path.abspath(__file__)), "qa_social_v3678.py"))
qs = importlib.util.module_from_spec(_spec)
import sys
sys.argv = ["qa_social_v3678.py", "http://localhost:3000/game.html?nocache=1"]
# cargar SIN ejecutar main (el guard __main__ protege)
_spec.loader.exec_module(qs)

DEST = "/home/z/my-project/download/fotos_r86"


async def main():
    os.makedirs(DEST, exist_ok=True)
    mw, ep, srv = qs.mock_arranca()
    async with qs.async_playwright() as pw:
        b = await pw.chromium.launch(args=qs.ARGS_VOZ if hasattr(qs, "ARGS_VOZ") else
                                     ["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 1280, "height": 800})
        await pg.add_init_script(qs.JS_HILO_QA)
        await pg.add_init_script(qs.JS_ENDPOINT.replace("__EP__", ep))
        await pg.add_init_script(qs.JS_NOMBRE.replace("__NOM__", "Fran"))
        await pg.goto("http://localhost:3000/game.html?v=foto", wait_until="domcontentloaded",
                      timeout=45000)
        for _ in range(180):
            if await pg.evaluate("() => !!window.__PP_GAME && !!window.__PP_GAME.social"):
                break
            await pg.wait_for_timeout(250)
        # un segundo jugador simulado en el mock (el amigo de Ana)
        import urllib.request
        req = urllib.request.Request(
            ep + "/presencia",
            data=b'{"pid":"amigo0000000abc","n":"Ana","v":"3.6.78-SDK6","st":"libre"}',
            headers={"Content-Type": "text/plain"})
        urllib.request.urlopen(req)

        # 1. medallón VERDE en el HUB
        await pg.evaluate("() => { window.__PP_GAME.social.pollNumero(); }")
        await pg.wait_for_timeout(1200)
        await pg.evaluate("() => { window.__PP_GAME.toggleMenu(); }")
        await pg.wait_for_timeout(600)
        canvas = await pg.evaluate("""() => {
          const G = window.__PP_GAME;
          return G.menuCanvas.toDataURL('image/png');
        }""")
        import base64
        with open(os.path.join(DEST, "1_medallon_hub_verde.png"), "wb") as f:
            f.write(base64.b64decode(canvas.split(",", 1)[1]))
        print("foto 1 · medallón verde en el HUB", flush=True)

        # 2. medallón DORADO + 3. tarjeta de invitación
        code = await pg.evaluate("""() => {
          const G = window.__PP_GAME;
          G.social.invitas = [{ id: 7, de: 'amigo0000000abc', deN: 'Ana', code: 'KQ3WP', hace: 4200 }];
          G.drawMenu();
          return 'ok';
        }""")
        await pg.wait_for_timeout(400)
        canvas = await pg.evaluate("() => window.__PP_GAME.menuCanvas.toDataURL('image/png')")
        with open(os.path.join(DEST, "2_medallon_hub_dorado.png"), "wb") as f:
            f.write(base64.b64decode(canvas.split(",", 1)[1]))
        print("foto 2 · medallón dorado (invitación)", flush=True)
        # submenú multi con la tarjeta
        await pg.evaluate("""() => {
          const G = window.__PP_GAME;
          const i = G.menuRects.findIndex(r => r.id === 'tab:multi');
          if (i >= 0) G.menuClick(i);
        }""")
        await pg.wait_for_timeout(500)
        canvas = await pg.evaluate("() => window.__PP_GAME.menuCanvas.toDataURL('image/png')")
        with open(os.path.join(DEST, "3_tarjeta_invitacion.png"), "wb") as f:
            f.write(base64.b64decode(canvas.split(",", 1)[1]))
        print("foto 3 · tarjeta de invitación en el submenú", flush=True)
        await b.close()
    srv.shutdown()
    print(f"LISTO · fotos en {DEST}", flush=True)


asyncio.run(main())
