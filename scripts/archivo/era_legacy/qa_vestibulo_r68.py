#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r68.py — QA FASE 162 · EL ARCO (r68).

Peticiones del dueño verificadas:
  1) «el menú debe ocupar prácticamente toda la pantalla» — TRES panelas
     físicas en arco (centro 0,98 m a 1,15 m · lados 0,74 m a 1,25 m ·
     yaw ±36°) alimentadas por el lienzo virtual 3696×1400.
  2) «los 3 bloques equidistantes como si de una pantalla curva se
     tratase» — cada panela girada hacia el jugador, centros a su dist.
  3) «por defecto aparecerá anclado en el centro (chincheta pulsada)» —
     menuPin=true por defecto, anchorMenu en la cabeza, sin flotación.
  4) «el bloque central más protagonismo para el verde JUGAR y la
     escalera al nivel del resto» — héroe 380 px con halo; carrera 215.
  5) «el dock desaparece completo; reubicar Salir a la WEB» — sin
     docktv/dockintro/dockpwa/dockkofi; 'salirweb' como tarjeta fina en
     TU CASA con prompt caramelo (SI/NO).
  6) «rediseño de todos los apartados y submenús» — concha data-driven
     (CONFIG_SECCIONES) en TODAS las páginas + rejilla de AJUSTES en
     tarjetas-icono (8) + prompts caramelo; legado con mecánica intacta
     y rects mapeados al lienzo virtual.

Salida: RESULTADO: N OK · M fallos + 3 capturas del lienzo (main·opts·prompt)."""
import asyncio
import base64
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3667/game.html'
OUT = '/home/z/my-project/download/'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  if (!G) { out.sinJuego = true; return out; }
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));

  out.canvas = G.menuCanvas.width === 3696 && G.menuCanvas.height === 1400;
  out.panelas = Array.isArray(G._menuPanelas) && G._menuPanelas.length === 3;
  const geo = G._menuPanelas.map((m) => ({
    w: m.geometry.parameters.width, h: m.geometry.parameters.height,
    yaw: Math.round(m.rotation.y * 180 / Math.PI),
    dist: Math.round(Math.hypot(m.position.x, m.position.z) * 100) / 100 }));
  out.arco = geo[0].yaw === 36 && geo[2].yaw === -36 && geo[1].yaw === 0 &&
    geo[1].w === 0.98 && geo[1].dist === 1.15 &&
    Math.abs(geo[0].dist - 1.25) < 0.01 &&
    // normal de la panela L apuntando a la cabeza (pantalla curva real)
    (() => { const m = G._menuPanelas[0];
      const n = new (m.position.constructor)(0, 0, 1)
        .applyQuaternion(m.quaternion);
      return n.x > 0.5 && n.z > 0.7; })();

  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  out.pinON = G.menuPin === true;
  await dorme(600);
  const ids = (G.menuRects || []).map((r) => r.id);
  const requeridos = ['start', 'carrera:abre', 'traingo', 'survgo',
    'tab:multi', 'page:champs', 'wrl:open', 'homehall', 'tut:go',
    'page:opts', 'salirweb', 'close', 'lang:es', 'lang:en'];
  out.idsFaltan = requeridos.filter((id) => !ids.includes(id));
  out.idsOk = out.idsFaltan.length === 0;
  out.sinDock = ['docktv', 'dockintro', 'dockpwa', 'dockkofi']
    .every((id) => !ids.includes(id));
  out.enBounds = (G.menuRects || []).every((r) =>
    r.x >= -2 && r.y >= -2 && r.x + r.w <= 3698 && r.y + r.h <= 1402);
  out.pngMain = G.menuCanvas.toDataURL('image/png');

  // AJUSTES: rejilla de tarjetas-icono (8) sobre las panelas C y R
  G.menuClick(ids.indexOf('page:opts'), 0);
  await dorme(300);
  const ids2 = (G.menuRects || []).map((r) => r.id);
  const rej = ['page:optsJuego', 'page:optsSala', 'page:optsSonido',
    'page:optsVisual', 'page:optsPerfil', 'page:optsRendi', 'page:optsPala',
    'kofi'];
  out.rejilla = rej.every((id) => ids2.includes(id));
  out.rejillaBounds = (G.menuRects || []).every((r) =>
    r.x >= -2 && r.y >= -2 && r.x + r.w <= 3698 && r.y + r.h <= 1402);
  out.pngOpts = G.menuCanvas.toDataURL('image/png');

  // volver con el ATRÁS de la concha (id page:main desde el dato)
  const iV = ids2.indexOf('page:main');
  G.menuClick(iV, 0);
  await dorme(200);
  out.vuelta = G.menuPage === 'main' &&
    (G.menuRects || []).some((r) => r.id === 'start');

  // SALIR A LA WEB: tarjeta fina en TU CASA → prompt caramelo
  const ids3 = (G.menuRects || []).map((r) => r.id);
  G.menuClick(ids3.indexOf('salirweb'), 0);
  await dorme(250);
  const ids4 = (G.menuRects || []).map((r) => r.id);
  out.prompt = G.menuPage === 'salirask' &&
    ids4.includes('salirweb_si') && ids4.includes('salirweb_no');
  out.pngPrompt = G.menuCanvas.toDataURL('image/png');
  G.menuClick(ids4.indexOf('salirweb_no'), 0);
  await dorme(200);

  // TRAIN legado vestido con la concha (mecánica intacta, rects mapeados)
  const ids5 = (G.menuRects || []).map((r) => r.id);
  G.menuClick(ids5.indexOf('traingo'), 0);
  await dorme(200);
  out.train = G.menuPage === 'train' && (G.menuRects || []).length > 5 &&
    (G.menuRects || []).every((r) => r.x >= -2 && r.y >= -2 &&
      r.x + r.w <= 3698 && r.y + r.h <= 1402);
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(150);
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3667', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        server.terminate()
        sys.exit(1)

    agujas = [
        # arco + virtual
        ('const CONFIG_MENUS', 'CONFIG_MENUS v2 (c02)'),
        ('const CONFIG_SECCIONES', 'CONFIG_SECCIONES (c02)'),
        ('lienzo: { ancho: 3696, alto: 1400 }', 'lienzo virtual 3696×1400'),
        ("{ id: 'C', x: 1112, w: 1472, anchoM: 0.98, altoM: 0.95, yaw: 0, dist: 1.15 }",
         'panela central 0,98 m a 1,15 m'),
        ("{ id: 'L', x: 0, w: 1112, anchoM: 0.74, altoM: 0.95, yaw: 36, dist: 1.25 }",
         'panela izquierda 0,74 m a 1,25 m yaw 36°'),
        ('this._menuPanelas = [];', 'tres panelas físicas'),
        ('mesh.rotation.y = yaw;', 'cada panela mira al jugador'),
        ('_menuTexSube()', 'troceado virtual→3 texturas'),
        ('muRaycaster.intersectObjects(this._menuPanelas, false)',
         'rayo a las tres panelas'),
        ('const px = paHit.x + hit.uv.x * paHit.w;', 'px virtuales por panela'),
        ('.applyQuaternion(hit.object.quaternion)',
         'cursor en la panela tocada'),
        # pin + anclaje
        ('this.menuPin = true;              // r68: ON por defecto', 'pin ON'),
        ('this.menuGroup.position.copy(muHead);', 'ancla en la cabeza'),
        ('this.menuPin = true;\n      this._menuPinDraw();\n      this.anchorMenu();',
         'apertura: pin + ancla'),
        # vestíbulo v2
        ("{ id: 'salirweb', icono: 'salir', etiquetaKey: 'dock_salir',",
         'salir a la web en TU CASA'),
        ('fino: true', 'tarjeta fina (salir)'),
        ('halo de protagonismo del héroe', 'héroe JUGAR con halo'),
        ('la CARRERA al nivel', 'carrera al nivel del resto'),
        ('dock ELIMINADO', 'dock fuera'),
        # concha + secciones
        ('drawMenuConcha(rects)', 'concha de secciones'),
        ("shell: {\n    multi: { tituloKey: 'tab_multi', icono: 'multijugador'",
         'shell data-driven por página'),
        ('_menuRejilla(rects, nombre, subs)', 'rejilla genérica'),
        ("rejillas: {\n    ajustes: { columnas: ['C', 'R']", 'rejilla AJUSTES'),
        ("{ id: 'page:optsRendi', icono: 'gauge', etiquetaKey: 'cat_rendi',",
         'categoría RENDIMIENTO con icono gauge'),
        ('_vestPrompt(rects, cfg)', 'prompts caramelo'),
        ("this._vestPrompt(rects, {\n      icono: 'vestibulo'",
         'prompt del hall caramelo'),
        # conservación
        ('drawMenuHub(rects)', 'hub legado conservado'),
        ('_pintaMedallon(rMulti, this.social)', 'medallón r87 vivo'),
        ('const S68 = H / 1536, DX68 = (W - 1024 * S68) / 2;',
         'legado 0,911 centrado'),
        # sello
        ("const VERSION = '3.6.159-SDK6'", 'sello a 3.6.159'),
    ]
    for needle, label in agujas:
        chk(needle in game, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')
    chk('docktv' not in game.split('CONFIG_SECCIONES')[0].split('CONFIG_MENUS')[1]
        if 'CONFIG_SECCIONES' in game else False, 'CONFIG_MENUS sin dock')

    errors = []
    rt = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            await page.goto(URL, wait_until='domcontentloaded', timeout=90000)
            await page.wait_for_timeout(9000)
            rt = await page.evaluate(JS)
        except Exception as e:
            print('✗ El juego no arrancó en headless:', e)
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            await browser.close()
            server.terminate()
            sys.exit(1)
        await browser.close()
    server.terminate()

    for k, label, kind in [
        ('canvas', 'lienzo virtual 3696×1400 en vivo', 'b'),
        ('panelas', 'tres panelas físicas', 'b'),
        ('arco', 'arco: yaw ±36° · C 0,98@1,15 · L/R 0,74@1,25', 'b'),
        ('pinON', 'chincheta ON por defecto al abrir', 'b'),
        ('idsOk', 'los 14 ids del Vestíbulo (sin dock)'
         + (f' · faltan {rt.get("idsFaltan")}' if rt.get('idsFaltan') else ''), 'b'),
        ('sinDock', 'dock desaparecido completo', 'b'),
        ('enBounds', 'rects del Vestíbulo en el lienzo virtual', 'b'),
        ('rejilla', 'AJUSTES: las 8 tarjetas-icono (7 + Ko-fi)', 'b'),
        ('rejillaBounds', 'rects de la rejilla en bounds', 'b'),
        ('vuelta', 'atrás de la concha → Vestíbulo', 'b'),
        ('prompt', 'salirweb → prompt caramelo SI/NO', 'b'),
        ('train', 'PRO TRAINING legado con concha y rects mapeados', 'b'),
    ]:
        chk(rt.get(k) is True, label)
    chk(not rt.get('sinJuego'), 'window.__PP_GAME presente')
    chk(not errors, f'sin pageerrors ({len(errors)})')
    if errors:
        print('   pageerrors:', errors[:3])

    for key, name in [('pngMain', 'qa_arco_main.png'),
                      ('pngOpts', 'qa_arco_ajustes.png'),
                      ('pngPrompt', 'qa_arco_prompt.png')]:
        if rt.get(key) and rt[key].startswith('data:image/png;base64,'):
            raw = base64.b64decode(rt[key].split(',', 1)[1])
            open(OUT + name, 'wb').write(raw)
            print(f'  captura: {name} ({len(raw):,} B)')
        else:
            chk(False, f'captura {name}')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
