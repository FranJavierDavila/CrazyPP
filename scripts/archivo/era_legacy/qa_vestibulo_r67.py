#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r67.py — QA FASE 161 · EL VESTÍBULO (r67).

Peticiones del dueño verificadas:
  1) Rediseño de los menús principales al estilo caramelo de SU referencia:
     cabecera con logo + palas de idioma ES/EN + sello de versión, TRES
     paneles de cristal (JUGAR centro · COMPITE izquierda · TU CASA derecha),
     dock de utilidades (TV · Intro · Instalar · Apoyar · Salir) y cierre.
  2) TODO data-driven: ICONOS_MENUS (17 iconos del set «CRAZY ICONOS v1»,
     intercambiables sin tocar código) + CONFIG_MENUS (paneles, tarjetas,
     gradientes, orden) en c02 — el render los LEE.
  3) Iconos con detalle: 17 PNG 256 px diseñados a mano (SVG→cairosvg,
     cuantización 64 colores), medallón + escala desde el registro.
  4) Conservación: los 15 submenús legados (1024×1536) se pintan escalados
     (0,9375) y centrados (dx 800) con TODOS sus rects mapeados al lienzo
     2560×1440; despacho de acciones con ids idénticos; dock reutiliza los
     botones DOM (intro/PWA/Ko-fi/TV); medallón del pulso r87 vivo; rayo
     leído VIVO del canvas/geometry (fin de literales).

Pruebas: 1) FUENTE SERVIDA (agujas) · 2) MECÁNICA REAL headless (lienzo,
plano, rects del Vestíbulo, mapeo del legado, navegación main→opts→main→
train, iconos decodificados) + capturas del lienzo del menú.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo) + 2 PNG en download/."""
import asyncio
import base64
import io
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3667/game.html'   # r67: puerto propio (el 3000 es
# del next-server residente de la app web, que sirve una copia arcaica)
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

  // · LIENZO + PLANO (FASE 161) —
  out.canvas = G.menuCanvas.width === 2560 && G.menuCanvas.height === 1440;
  const gp = G.menuMesh.geometry.parameters;
  out.plano = gp.width === 1.60 && gp.height === 0.90;

  // · VESTÍBULO EN VIVO —
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  out.abierto = G.menuOpen === true && G.menuPage === 'main';
  await dorme(600);   // tiempo para decodificar los data-URI de los iconos
  const ids = (G.menuRects || []).map((r) => r.id);
  const requeridos = ['start', 'carrera:abre', 'traingo', 'survgo',
    'tab:multi', 'page:champs', 'wrl:open', 'homehall', 'tut:go',
    'page:opts', 'docktv', 'dockintro', 'dockpwa', 'dockkofi', 'salirweb',
    'close', 'lang:es', 'lang:en'];
  out.idsFaltan = requeridos.filter((id) => !ids.includes(id));
  out.idsOk = out.idsFaltan.length === 0;
  out.enBounds = (G.menuRects || []).every((r) =>
    r.x >= -2 && r.y >= -2 && r.x + r.w <= 2562 && r.y + r.h <= 1442);
  out.nRects = (G.menuRects || []).length;
  out.iconosCache = Object.keys(G._menuIconos || {}).length;
  out.iconosListos = Object.values(G._menuIconos || {})
    .filter((im) => im.complete && im.naturalWidth > 0).length;
  out.pngVestibulo = G.menuCanvas.toDataURL('image/png');

  // · LEGADO: AJUSTES (mapeo de rects + pintado escalado/centrado) —
  const iOpts = ids.indexOf('page:opts');
  G.menuClick(iOpts, 0);
  await dorme(250);
  out.paginaOpts = G.menuPage === 'opts';
  out.legacyBounds = (G.menuRects || []).length > 5 && (G.menuRects || [])
    .every((r) => r.x >= -2 && r.y >= -2 && r.x + r.w <= 2562 &&
      r.y + r.h <= 1442);
  out.pngOpts = G.menuCanvas.toDataURL('image/png');

  // · VUELTA AL VESTÍBULO —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(200);
  out.vuelta = G.menuPage === 'main' &&
    (G.menuRects || []).some((r) => r.id === 'start');

  // · LEGADO: TRAIN (otro submenú, por la pestaña ENTRENAR) —
  const iTr = (G.menuRects || []).findIndex((r) => r.id === 'traingo');
  G.menuClick(iTr, 0);
  await dorme(200);
  out.train = G.menuPage === 'train' && (G.menuRects || []).length > 5;

  // · DOCK: docktv despacha y cierra el menú (reutiliza el DOM) —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(150);
  const iTv = (G.menuRects || []).findIndex((r) => r.id === 'docktv');
  G.menuClick(iTv, 0);
  await dorme(250);
  out.dockCierra = G.menuOpen === false;
  return out;
}"""


async def main():
    # servidor propio del QA (puerto 3667 — el 3000 es del next-server)
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3667', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)

    # ---------- 1 · FUENTE SERVIDA (agujas) ----------
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        server.terminate()
        sys.exit(1)

    agujas = [
        # datos nuevos en c02 (embebidos en el ensamblado — sin `export`)
        ('const CONFIG_MENUS', 'CONFIG_MENUS data-driven (c02)'),
        ('const ICONOS_MENUS', 'ICONOS_MENUS registro de iconos (c02)'),
        ("tituloKey: 'vest_compite'", 'panel COMPITE como dato'),
        ("tituloKey: 'vest_jugar'", 'panel JUGAR como dato'),
        ("tituloKey: 'vest_casa'", 'panel TU CASA como dato'),
        ("{ id: 'docktv', icono: 'tv', etiquetaKey: 'dock_tv' }",
         'dock: TV como dato'),
        ("{ id: 'salirweb', icono: 'salir', etiquetaKey: 'dock_salir' }",
         'dock: salir como dato'),
        # render nuevo en c12
        ('drawMenuVestibulo(rects)', 'render del Vestíbulo'),
        ('_vestSubPorId(id, def)', 'subtítulos vivos resueltos'),
        ('this._menuMap = { s: 0.9375, dx: 800, dy: 0 }',
         'legado: transform 0,9375 + dx 800'),
        ('_mapRect(o)', 'mapeo de rects del legado'),
        ('new THREE.PlaneGeometry(1.60, 0.90)', 'plano panorámico 1,60×0,90'),
        ('this.menuCanvas.width = 2560;', 'lienzo 2560'),
        ('this.menuCanvas.height = 1440;', 'lienzo 1440'),
        ('hit.uv.x * this.menuCanvas.width', 'rayo: px vivos del canvas'),
        ('const gp = this.menuMesh.geometry.parameters;',
         'rayo: cursor desde geometry.parameters'),
        ("{ docktv: 'tvlink', dockintro: 'introbtn',",
         'dock reutiliza los botones DOM'),
        ("case 'docktv':", 'despachador: caso docktv'),
        ("case 'dockkofi':", 'despachador: caso dockkofi'),
        ('this._langPaddle(rects, \'es\', HC.x + HC.w - 310, HC.y + 9)',
         'cabecera: pala de idioma ES'),
        ('c.save();\n    c.setTransform(1, 0, 0, 1, 0, 0);',
         'medallón: save/reset (r87 intacto)'),
        ('this._menuPinMesh.position.set(0, 0.482, 0.006);',
         'chincheta re-anclada al plano panorámico'),
        ('(0, 0.482, 0.006)', 'pin a 0,482'),
        # conservación del hub legado (sigue vivo para… nada lo borra: es
        # la referencia de subtítulos y el despacho)
        ('drawMenuHub(rects)', 'hub legado conservado (referencia)'),
        ('_modeCard(rects,', '_modeCard intacto'),
        ("rects.push(this._mapRect({ x: x - 6, y: y - 6, w: S + 12, h: S + 12, id: 'lang:' + lang }));",
         '_langPaddle con rects mapeados'),
        ("rects.push(this._mapRect({ x: rx - 8, y: vy - 4, w: rw + 16, h: 62, id: idSet, slider: true }));",
         'sliders de AJUSTES mapeados'),
        ('id: \'retoDiario\'', 'reto diario mapeado'),
        ("id: 'ppchamp:' + ch.id", 'tarjetas ppchamp mapeadas'),
        # i18n
        ("vest_jugar: 'JUGAR',", 'i18n ES paneles'),
        ("vest_jugar: 'PLAY',", 'i18n EN paneles'),
        ("dock_salir: 'Salir a la web',", 'i18n ES dock'),
        ("dock_salir: 'Exit to web',", 'i18n EN dock'),
        # sello
        ("const VERSION = '3.6.158-SDK6'", 'sello c00 a 3.6.158'),
        ('V3.6.158-SDK6', 'badge DOM a 3.6.158'),
    ]
    for needle, label in agujas:
        chk(needle in game, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 17, f'17+ iconos embebidos (hay {n_icons})')

    # ---------- 2 · MECÁNICA REAL (headless) ----------
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

    for k, label, extra in [
        ('canvas', 'lienzo 2560×1440 en vivo', None),
        ('plano', 'plano 1,60×0,90 en vivo', None),
        ('abierto', 'menú abierto en el Vestíbulo (main)', None),
        ('idsOk', 'los 18 ids del Vestíbulo presentes'
         + (f' · faltan {rt.get("idsFaltan")}' if rt.get('idsFaltan') else ''), None),
        ('enBounds', 'todos los rects dentro del lienzo', None),
        ('iconosListos', f'iconos decodificados '
         f'({rt.get("iconosListos")}/{rt.get("iconosCache")})', 'num12'),
        ('paginaOpts', 'page:opts despacha a AJUSTES (legado)', None),
        ('legacyBounds', 'rects del legado mapeados dentro del lienzo', None),
        ('vuelta', 'vuelta al Vestíbulo con start presente', None),
        ('train', 'traingo despacha a PRO TRAINING (legado)', None),
        ('dockCierra', 'docktv despacha y cierra el menú', None),
    ]:
        chk(rt.get(extra or k) is True if extra != 'num12'
            else (rt.get(k) or 0) >= 12, label)
    chk(not rt.get('sinJuego'), 'window.__PP_GAME presente')
    chk(not errors, f'sin pageerrors ({len(errors)})')
    if errors:
        print('   pageerrors:', errors[:3])

    # capturas del lienzo del menú
    for key, name in [('pngVestibulo', 'qa_vestibulo_main.png'),
                      ('pngOpts', 'qa_vestibulo_opts.png')]:
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
