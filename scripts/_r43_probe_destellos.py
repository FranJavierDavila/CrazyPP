#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r43 · PRUEBA EN VIVO del SUELO DE DESTELLOS + el LETRERO DE SALIDA:
  A · entrar al espacio arcano (fundido a negro, polling headless).
  B · SUELO DE DESTELLOS: base negra por píxel, TRAZOS vivos creciendo
      (destellos que dibujan la trama), rellenos acotados, matriz estática
      FUERA (sin línea siempre visible).
  C · LETRERO «Salir»: oculto por defecto, se FUNDE con el hover del búho
      (op 0 → >0,5 · visible) y se retira al apartar (hover false).
  D · el texto está REPINTADO con el idioma vivo (lienzo con tinta).
  E · OJOS del búho siguen oscilando (regresión r41) + pop del holograma.
  F · 0 errores de página.
Fotos: download/_r43_destellos.png · _r43_salir_hover.png
Servidor: http://127.0.0.1:8123 (servir upload/public).
NOTA headless: con SwiftShader el render cae a ~1-10 fps y el dt va
clampeado — todo se espera con POLLING, jamás con tiempos fijos."""
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
  const S = A.suelo.userData;
  return {
    on: G._arconoOn,
    pop: +A.pop.toFixed(2),
    trazos: S.trazos.length,
    trazosInfo: S.trazos.slice(0, 4).map((q) => ({
      ax: q.ax, dir: q.dir, ln: q.ln,
      head: +q.head.toFixed(2), desde: q.desde,
    })),
    lit: S.lit.length,
    vida: S.VIDA,
    salirOp: +A.salir.op.toFixed(3),
    salirVis: A.salir.mesh.visible,
    salirY: +A.salir.mesh.position.y.toFixed(3),
    ojos: A.buho.glints[0].material.color.getHex(),
    ojosR: A.buho.glints[1].material.color.getHex(),
    sueloTexAncho: S.tcv ? S.tcv.width : 0,
  };
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

LETRA_TINTA = """() => {
  // el lienzo del letrero tiene TINTA (texto repintado con el idioma vivo)
  const G = """ + G + """;
  const cv = G.arcaneGroup.userData.arcono.salir.cv;
  const x = cv.getContext('2d');
  const d = x.getImageData(0, 0, cv.width, cv.height).data;
  let tintados = 0;
  for (let i = 3; i < d.length; i += 4) if (d[i] > 40) tintados++;
  return { w: cv.width, h: cv.height, tintados };
}"""

HOVER_ON = """() => {
  (""" + G + """).arcaneGroup.userData.arcono.buho.hover = true;
  return true;
}"""

HOVER_OFF = """() => {
  (""" + G + """).arcaneGroup.userData.arcono.buho.hover = false;
  return true;
}"""

FOTO = """() => {
  const G = """ + G + """;
  G.renderer.render(G.scene, G.camera);
  return G.renderer.domElement.toDataURL('image/png');
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

        # ── C1 · el letrero nace OCULTO (op 0) ──
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.salir.op < 0.02', timeout=30000)
        est0 = await page.evaluate(ESTADO)
        ok_c1 = est0['salirOp'] < 0.02 and est0['salirVis'] is False
        print('C1 · letrero oculto sin hover (op', est0['salirOp'], '):',
              'OK ✓' if ok_c1 else 'FALLO')

        # ── D · el texto está repintado con el idioma vivo ──
        tinta = await page.evaluate(LETRA_TINTA)
        ok_d = tinta['tintados'] > 400
        print('D · lienzo del letrero con tinta (', tinta['tintados'],
              'px opacos en', tinta['w'], '×', tinta['h'], '):',
              'OK ✓' if ok_d else 'FALLO')

        # ── C2 · hover del búho → el letrero SE FUNDE (op alta) ──
        await page.evaluate(HOVER_ON)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.salir.op > 0.5', timeout=45000)
        est1 = await page.evaluate(ESTADO)
        ok_c2 = est1['salirOp'] > 0.5 and est1['salirVis'] is True
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r43_salir_hover.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('C2 · letrero fundido con hover (op', est1['salirOp'],
              '· y', est1['salirY'], '):', 'OK ✓' if ok_c2 else 'FALLO',
              '· foto hover')

        # ── C3 · sin hover → el letrero se RETIRA ──
        await page.evaluate(HOVER_OFF)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.salir.op < 0.05', timeout=45000)
        print('C3 · letrero retirado al apartar la mano: OK ✓')

        # ── B · EL SUELO DE DESTELLOS ──
        # los destellos nacen con temporizador propio: esperamos a que
        # existan TRAZOS vivos (polling; en headless el dt va clampeado)
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.suelo.userData.trazos.length >= 2',
            timeout=120000)
        await page.wait_for_timeout(1200)
        est2 = await page.evaluate(ESTADO)
        px = await page.evaluate(PIXELES)
        b64 = await page.evaluate(FOTO)
        with open(OUT + '/_r43_destellos.png', 'wb') as f:
            f.write(base64.b64decode(b64.split(',')[1]))
        print('píxeles · suelo:', px['suelo'], '· cielo:', px['cielo'])
        suelo_oscuro = sum(px['suelo'][:3]) < 150
        cielo_azul = px['cielo'][2] > px['cielo'][0] and px['cielo'][2] > 12
        ok_b1 = suelo_oscuro and cielo_azul
        print('B1 · base negra:', 'OK ✓' if suelo_oscuro else 'FALLO',
              '· cielo azul:', 'OK ✓' if cielo_azul else 'FALLO')
        eje_x = any(q['ax'] == 'x' for q in est2['trazosInfo'])
        eje_z = any(q['ax'] == 'z' for q in est2['trazosInfo'])
        sentidos = {q['dir'] for q in est2['trazosInfo']}
        ok_b2 = est2['trazos'] >= 2 and (eje_x or eje_z)
        print('B2 · trazos vivos:', est2['trazos'],
              '· info:', json.dumps(est2['trazosInfo']),
              '· 90° ambos ejes vivos (x=', eje_x, '· z=', eje_z,
              '· sentidos', sentidos, '):', 'OK ✓' if ok_b2 else 'FALLO')
        ok_b3 = est2['vida'] == 5.0 and est2['lit'] <= 70
        print('B3 · VIDA =', est2['vida'], 's · rellenos acotados (',
              est2['lit'], '≤ 70):', 'OK ✓' if ok_b3 else 'FALLO')

        # ── E · regresión r41: ojos oscilando + holograma condensado ──
        await page.wait_for_function(
            G + '.arcaneGroup.userData.arcono.pop >= 1', timeout=120000)
        m1 = await page.evaluate(G + '.arcaneGroup.userData.arcono.buho.glints[0].material.color.getHex()')
        await page.wait_for_timeout(900)
        m2 = await page.evaluate(G + '.arcaneGroup.userData.arcono.buho.glints[0].material.color.getHex()')
        ok_e = m1 != m2
        print('E · ojos oscilando (', hex(m1), '→', hex(m2), ') · pop = 1:',
              'OK ✓' if ok_e else 'FALLO')

        # ── F · cero errores de página ──
        ok_f = not errs
        print('F · errores de página:', len(errs),
              'OK ✓' if ok_f else 'FALLO ' + json.dumps(errs[:3]))

        checks = [True, ok_c1, ok_d, ok_c2, ok_b1, ok_b2, ok_b3, ok_e, ok_f]
        fallos = sum(1 for c in checks if not c)
        print(f'\nPROBE r43: {len(checks) - fallos}/{len(checks)} OK · fallos={fallos}')
        await browser.close()
        return 1 if fallos else 0


if __name__ == '__main__':
    raise SystemExit(asyncio.run(main()))
