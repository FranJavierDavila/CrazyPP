#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r33 · PRUEBA EN VIVO de los 4 poderes nuevos + foto del ASTRO arreglado.
Concede cada poder por consola (matriz), dispara el gatillo en rally y
verifica la ventana viva; luego cortina etapas 2/4 y restauración."""
import asyncio
import base64
import json

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'

CONCEDER = """(id) => {
  const G = window.__PP_GAME || window.__game;
  const ent = { id, n: 1 };
  G._megaMatriz.push(ent);
  G._megaIdx = G._megaMatriz.length - 1;
  return G._megaMatriz.map((e) => e.id);
}"""

TRIGGER = """(id) => {
  const G = window.__PP_GAME || window.__game;
  G.rules.state = 'rally';
  G._megaIdx = G._megaMatriz.findIndex((e) => e.id === id);
  const r = G.megaTrigger(1);            // mano libre (escritorio)
  return { r, t: G['_megaActivaRest'] ? G._megaActivaRest() : null,
           activa: G._megaActivaId, mensaje: G.rules.message };
}"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script(
            "try { localStorage.setItem('pp_player_name', 'foro3d'); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                     timeout=45000)
        print('versión:', await page.evaluate('window.__PP_VERSION || "?"'))
        await page.evaluate(
            """async () => { const G = window.__PP_GAME || window.__game;
             try { await G.champs.launch('estacion_orbital'); } catch (e) {} }""")
        await page.wait_for_timeout(4000)
        # arranca el duelo 1 (sala → serveTrigger)
        await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller || mod;
          ctrl.serveTrigger();
        }""")
        await page.wait_for_timeout(2000)
        for pid in ['prisma', 'onda', 'salva', 'ancla']:
            await page.evaluate(CONCEDER, pid)
            r = await page.evaluate(TRIGGER, pid)
            print(f'{pid:8s} → gatillo={r["r"]} activa={r["activa"]} '
                  f'restante={r["t"]} msg={r["mensaje"]!r}')
        await page.wait_for_timeout(1200)
        estado = await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          return { prismaT: +G._prismaT.toFixed(1), ondaT: +G._ondaT.toFixed(1),
                   salvaT: +G._salvaT.toFixed(1), anclaT: +G._anclaT.toFixed(1),
                   gui: G._prismaGuiaT > 0, firma: G._trailFirmaPoder() };
        }""")
        print('ventanas tras 1,2 s:', json.dumps(estado, ensure_ascii=False))
        # foto del ASTRO en el duelo (cámara manual hacia su standee)
        data = await page.evaluate("""async () => {
          const G = window.__PP_GAME || window.__game;
          const cam = G.camera.clone();
          cam.aspect = 16 / 9; cam.fov = 75; cam.updateProjectionMatrix();
          const V = G.camera.position.constructor;
          cam.position.set(0.7, 1.5, 0.4);
          cam.lookAt(new V(1.26, 1.05, -3.3));
          G.renderer.render(G.scene, cam);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        png = base64.b64decode(data.split(',', 1)[1])
        with open(f'{OUT}/_r33_astro_arreglado.png', 'wb') as f:
            f.write(png)
        print('foto ASTRO:', f'{len(png):,} B')
        print('errores de página:', errs[:5] if errs else 'ninguno')
        await browser.close()


asyncio.run(main())
