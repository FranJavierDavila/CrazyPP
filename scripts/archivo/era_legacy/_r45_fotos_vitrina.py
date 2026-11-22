#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r45 · FOTOS de verificación: (1) el LIENZO de la constelación (lo que
el bolígrafo ha dibujado, a resolución nativa) compuesto sobre el azul del
cielo; (2) PRIMER PLANO del candado sobre el medallón (recorte del render)."""
import asyncio
import base64
import os

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'
G = '(window.__PP_GAME||window.__game)'

AL_HALL = """async () => { const G = """ + G + """; if (!G.inHall) { try { G.enterHall(); } catch (e) {} } return G.inHall; }"""
ENTRAR = """() => { (""" + G + """)._arconoEntrar(); return true; }"""

# coloca la constelación DELANTE de la cámara (el panel mira a -Z del grupo:
# el búho/panel viven en z −2.3…−2.5) y la deja en pleno trazado
ENCUADRA = """() => {
  const A = (""" + G + """).arcaneGroup.userData.arcono;
  const M = A.conste, CN = M.userData.conste;
  // frente-alto: el jugador mira a −Z; la constelación a 20 m, 25° arriba
  M.position.set(0, 20, -38);
  M.lookAt(0, 1.55, 0);
  M.scale.setScalar(1.05);
  M.rotateZ(0.05);
  // reinicia el trazado a un punto temprano para pillar el bolígrafo en marcha
  CN.cv.getContext('2d').clearRect(0, 0, CN.cv.width, CN.cv.height);
  CN.estado = 'trazo'; CN.prog = CN.total * 0.30;
  M.visible = true; M.material.opacity = CN.opMax;
  return { p: M.position.toArray().map((v) => +v.toFixed(1)), prog: +CN.prog.toFixed(0) };
}"""

LIENZO = """() => {
  const A = (""" + G + """).arcaneGroup.userData.arcono;
  const CN = A.conste.userData.conste;
  const fin = document.createElement('canvas');
  fin.width = CN.cv.width; fin.height = CN.cv.height;
  const x = fin.getContext('2d');
  // el azul profundo del cielo de la bóveda como fondo
  x.fillStyle = '#040a1c';
  x.fillRect(0, 0, fin.width, fin.height);
  x.drawImage(CN.cv, 0, 0);
  return fin.toDataURL('image/png');
}"""

FOTO = """(clip) => {
  const G = """ + G + """;
  G.renderer.render(G.scene, G.camera);
  return G.renderer.domElement.toDataURL('image/png');
}"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("try { localStorage.clear(); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded', timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)', timeout=45000)
        await page.evaluate(AL_HALL)
        await page.wait_for_function(G + '.inHall === true', timeout=30000)
        await page.evaluate(ENTRAR)
        await page.wait_for_function(G + '._arconoOn === true', timeout=60000)
        # espera al pop del panel para una foto limpia
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.pop >= 1', timeout=120000)
        await page.evaluate(ENCUADRA)
        # deja al bolígrafo trabajar (polling: tinta creciendo)
        await page.wait_for_function(
            "(() => { const CN = (" + G + ").arcaneGroup.userData.arcono.conste.userData.conste;" +
            " const x = CN.cv.getContext('2d'); const d = x.getImageData(0,0,CN.cv.width,CN.cv.height).data;" +
            " let t=0; for (let i=3;i<d.length;i+=4) if (d[i]>30) t++; return t > 4000; })()",
            timeout=180000)
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r45_cielo_encuadre.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        b64 = await page.evaluate(LIENZO)
        with open(OUT + '/_r45_constelacion_lienzo.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('fotos: _r45_cielo_encuadre.png · _r45_constelacion_lienzo.png · errores:', len(errs))
        await browser.close()
        return 1 if errs else 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
