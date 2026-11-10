#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r41 · PRUEBA EN VIVO del ARCANO HOLOGRÁFICO (petición del dueño):
  A · entrar al espacio arcano (fundido a negro, polling headless).
  B · SUELO NEGRO con matriz fina + rellenos azules aleatorios vivos.
  C · FLECHAS INTERCAMBIADAS: glifos descruzados — ‹ a la izquierda
      (oculto en el 0) y › a la derecha (oculto en el último).
  D · HOLOGRAMA: pop 0→1 (formación) y condensado exacto.
  E · CANDADO flotante: delante del medallón, visible con poder bloqueado.
  F · OJOS del búho: color oscilando azul↔rojo (muestras distintas).
  G · VOZ: _vozSel invocada al navegar (espía, sin audio en headless).
  H · MOTAS circulares: PointsMaterial con map (textura radial).
  I · 0 errores de página.
Fotos: download/_r41_arcano_formando.png · _r41_arcano_condensado.png
Servidor: http://127.0.0.1:8123 (servir upload/public).
NOTA headless: con SwiftShader el render cae a ~1-10 fps y el dt del
juego está clampeado a 1/30 — los fundidos REALES (0,38 s) tardan más
en el probe; todo se espera con POLLING, jamás con tiempos fijos."""
import asyncio
import base64
import json
import os

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'

G = '(window.__PP_GAME||window.__game)'

AL_HALL = """async () => {
  const G = """ + G + """;
  if (G.inHall) return 'ya';
  try { G.enterHall(); } catch (e) { return 'err:' + e; }
  return 'ok';
}"""

ENTRAR = """() => { (""" + G + """)._arconoEntrar(); return true; }"""

ESTADO = """() => {
  const G = """ + G + """;
  const A = G.arcaneGroup.userData.arcono;
  return {
    on: G._arconoOn,
    idx: G._arconoIdx,
    pop: +A.pop.toFixed(2),
    flechaLx: A.flechas.L.mesh.position.x,
    flechaRx: A.flechas.R.mesh.position.x,
    flechaLvis: A.flechas.L.mesh.visible,
    flechaRvis: A.flechas.R.mesh.visible,
    candadoVisible: A.candado.grupo.visible,
    candadoZ: +A.candado.grupo.position.z.toFixed(3),
    panelZ: +A.panel.mesh.position.z.toFixed(3),
    ojos: A.buho.glints[0].material.color.getHex(),
    motasMap: !!A.motas.material.map,
    motasSize: A.motas.material.size,
    losetasVivas: A.suelo.userData.lit.length,
    sueloN: A.suelo.userData.N,
  };
}"""

FOTO = """() => {
  const G = """ + G + """;
  G.renderer.render(G.scene, G.camera);
  return G.renderer.domElement.toDataURL('image/png');
}"""

PIXELES = """() => {
  const G = """ + G + """;
  G.renderer.render(G.scene, G.camera);
  const cv = G.renderer.domElement;
  const t = document.createElement('canvas');
  t.width = cv.width; t.height = cv.height;
  const x = t.getContext('2d');
  x.drawImage(cv, 0, 0);
  const W = cv.width, H = cv.height;
  const muestra = (px, py) => Array.from(x.getImageData(px, py, 1, 1).data);
  return {
    suelo: muestra((W / 2) | 0, (H * 0.92) | 0),
    cielo: muestra((W / 2) | 0, (H * 0.18) | 0),
  };
}"""

VOZ_ESPIA = """() => {
  const G = """ + G + """;
  if (!G.__r41VozSpy) {
    G.__r41VozSpy = 0;
    const orig = G._vozSel.bind(G);
    G._vozSel = (id) => { G.__r41VozSpy++; try { return orig(id); } catch (e) {} };
  }
  return true;
}"""

NAVEGA = """() => {
  const G = """ + G + """;
  G._arconoIdx = 1;
  G._arconoRepinta();
  return { idx: G._arconoIdx, pop: G.arcaneGroup.userData.arcono.pop };
}"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    fallos = 0
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script("try { localStorage.clear(); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                     timeout=45000)
        print('versión:', await page.evaluate('window.__PP_VERSION || "?"'))

        await page.evaluate(AL_HALL)
        await page.wait_for_function(G + '.inHall === true', timeout=30000)
        print('hall: ok')

        # ── A · ENTRAR (fundido — polling headless) ──
        await page.evaluate(ENTRAR)
        await page.wait_for_function(G + '._arconoOn === true', timeout=60000)
        print('A · entrar al arcano: OK ✓')

        # ── D · el holograma SE ESTÁ FORMANDO (pop < 1) ──
        await page.evaluate("(() => { const G=" + G + "; G._arconoRepinta(); })()")
        await page.wait_for_timeout(500)
        est = await page.evaluate(ESTADO)
        ok_d1 = 0.0 <= est['pop'] < 1.0
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r41_arcano_formando.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('D · holograma formándose (pop =', est['pop'], '):',
              'OK ✓' if ok_d1 else 'FALLO', '· foto formando')

        # ── condensado ──
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.pop >= 1', timeout=90000)
        est2 = await page.evaluate(ESTADO)
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r41_arcano_condensado.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('D · condensado (pop = 1): OK ✓ · foto condensado')

        # ── B · suelo negro + losetas vivas ──
        px = await page.evaluate(PIXELES)
        print('píxeles · suelo:', px['suelo'], '· cielo:', px['cielo'])
        suelo_oscuro = sum(px['suelo'][:3]) < 150
        cielo_azul = px['cielo'][2] > px['cielo'][0] and px['cielo'][2] > 12
        vivas = est2['losetasVivas']
        ok_b = suelo_oscuro and cielo_azul and 5 <= vivas <= 140
        print('B · suelo negro:', 'OK ✓' if suelo_oscuro else 'FALLO',
              '· cielo azul oscuro:', 'OK ✓' if cielo_azul else 'FALLO',
              '· losetas vivas:', vivas, '· matriz:', est2['sueloN'])

        # ── C · flechas: ‹ a la IZQUIERDA (oculto en el 0), › a la DERECHA ──
        ok_c = (est2['flechaLx'] == -0.93 and est2['flechaRx'] == 0.93
                and est2['flechaLvis'] is False and est2['flechaRvis'] is True)
        print('C · flechas ‹ en −0,93 (oculto en el 0) · › en +0,93 (visible):',
              'OK ✓' if ok_c else 'FALLO',
              json.dumps({k: est2[k] for k in
                          ['flechaLx', 'flechaRx', 'flechaLvis', 'flechaRvis']}))

        # ── E · candado flotante ──
        ok_e = (est2['candadoVisible'] is True and est2['candadoZ'] > est2['panelZ'])
        print('E · candado DELANTE del panel (z', est2['candadoZ'], '>',
              est2['panelZ'], ') y visible con poder bloqueado:',
              'OK ✓' if ok_e else 'FALLO')

        # ── F · ojos oscilando azul↔rojo ──
        m1 = await page.evaluate(G + '.arcaneGroup.userData.arcono.buho.glints[0].material.color.getHex()')
        await page.wait_for_timeout(900)
        m2 = await page.evaluate(G + '.arcaneGroup.userData.arcono.buho.glints[0].material.color.getHex()')
        ok_f = m1 != m2
        print('F · ojos oscilando (', hex(m1), '→', hex(m2), '):',
              'OK ✓' if ok_f else 'FALLO')

        # ── G · voz con espía + navegación ──
        await page.evaluate(VOZ_ESPIA)
        nav = await page.evaluate(NAVEGA)
        await page.wait_for_timeout(400)
        espia = await page.evaluate('(window.__PP_GAME||window.__game).__r41VozSpy || 0')
        ok_g = espia >= 1 and nav['pop'] == 0
        print('G · voz al presentar (espía =', espia, '· pop reiniciado =',
              nav['pop'], '):', 'OK ✓' if ok_g else 'FALLO')
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.pop >= 1', timeout=90000)

        # ── H · motas circulares ──
        ok_h = est2['motasMap'] is True and est2['motasSize'] < 0.04
        print('H · motas circulares pequeñas (map =', est2['motasMap'],
              '· size =', est2['motasSize'], '):', 'OK ✓' if ok_h else 'FALLO')

        # ── I · cero errores de página ──
        ok_i = not errs
        print('I · errores de página:', len(errs),
              'OK ✓' if ok_i else 'FALLO ' + json.dumps(errs[:3]))

        checks = [True, ok_d1, ok_b, ok_c, ok_e, ok_f, ok_g, ok_h, ok_i]
        fallos = sum(1 for c in checks if not c)
        print(f'\nPROBE r41: {len(checks) - fallos}/{len(checks)} OK · fallos={fallos}')
        await browser.close()
        return 1 if fallos else 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
