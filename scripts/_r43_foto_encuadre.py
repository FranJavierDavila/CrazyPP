#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r43 · TOMA ENCUADRADA: entra al arcano, apunta la cámara de escritorio
al conjunto (búho + letrero + suelo con destellos) y fotografía."""
import asyncio
import base64
import os

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'
G = '(window.__PP_GAME||window.__game)'

ENCUADRA = """() => {
  const G = """ + G + """;
  // cámara de escritorio mirando al búho (el grupo arcano está plantado
  // en los pies del rig: origen del grupo ≈ posición del rig)
  const gx = G.arcaneGroup.position.x, gz = G.arcaneGroup.position.z;
  G.camera.position.set(gx + 0.2, 1.6, gz + 2.2);
  G.camera.lookAt(gx, 1.7, gz - 2.4);
  G.camera.updateMatrixWorld();
  return true;
}"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.add_init_script("try { localStorage.clear(); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                     timeout=45000)
        await page.evaluate("""async () => { const G=""" + G + """; if (!G.inHall) G.enterHall(); }""")
        await page.wait_for_function(G + '.inHall === true', timeout=30000)
        await page.evaluate("() => { (" + G + ")._arconoEntrar(); }")
        await page.wait_for_function(G + '._arconoOn === true', timeout=60000)
        # letrero: hover encendido
        await page.evaluate("() => { (" + G + ").arcaneGroup.userData.arcono.buho.hover = true; }")
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.salir.op > 0.5', timeout=45000)
        # destellos: espera a que haya trazos y avancen (estela visible)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.suelo.userData.trazos.length >= 2',
            timeout=120000)
        await page.wait_for_timeout(2500)
        await page.evaluate(ENCUADRA)
        b64 = await page.evaluate("""() => {
          const G = """ + G + """;
          G.renderer.render(G.scene, G.camera);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/_r43_encuadre_salir.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        # segunda toma: el suelo de destellos (cámara baja hacia el suelo)
        await page.evaluate("""() => {
          const G = """ + G + """;
          const gx = G.arcaneGroup.position.x, gz = G.arcaneGroup.position.z;
          G.camera.position.set(gx + 0.1, 2.2, gz + 1.4);
          G.camera.lookAt(gx, 0.05, gz - 2.2);
          G.camera.updateMatrixWorld();
        }""")
        b64 = await page.evaluate("""() => {
          const G = """ + G + """;
          G.renderer.render(G.scene, G.camera);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open(OUT + '/_r43_encuadre_suelo.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('fotos: _r43_encuadre_salir.png · _r43_encuadre_suelo.png')
        await browser.close()


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    raise SystemExit(asyncio.run(main()))
