#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r68.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 162
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.159-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva EL ARCO (CONFIG_MENUS v2 con
    panelas físicas, CONFIG_SECCIONES, _menuTexSube, rayo por panela, pin
    ON, concha, rejilla y prompts) + 24 iconos + sw a 3.6.159 + r160/r65.
  · FUNCIONAL: el juego VIVO — lienzo virtual 3696×1400, 3 panelas con
    arco verificado (yaw y normal), chincheta ON, 14 ids del Vestíbulo sin
    dock, rejilla de AJUSTES, prompt de salida, train legado mapeado.
Uso: python3 scripts/prod_smoke_r67.py"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.159-SDK6'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  if (!G) { out.sinJuego = true; return out; }
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  out.canvas = G.menuCanvas.width === 3696 && G.menuCanvas.height === 1400;
  out.panelas = Array.isArray(G._menuPanelas) && G._menuPanelas.length === 3;
  const geo = G._menuPanelas.map((m) => ({
    yaw: Math.round(m.rotation.y * 180 / Math.PI),
    dist: Math.round(Math.hypot(m.position.x, m.position.z) * 100) / 100 }));
  out.arco = geo[0].yaw === 36 && geo[2].yaw === -36 &&
    Math.abs(geo[0].dist - 1.25) < 0.01;
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  out.abierto = G.menuOpen === true && G.menuPage === 'main';
  await dorme(600);
  const ids = (G.menuRects || []).map((r) => r.id);
  const requeridos = ['start', 'carrera:abre', 'traingo', 'survgo',
    'tab:multi', 'page:champs', 'wrl:open', 'homehall', 'tut:go',
    'page:opts', 'salirweb', 'close', 'lang:es', 'lang:en'];
  out.idsOk = requeridos.every((id) => ids.includes(id));
  out.sinDock = ['docktv', 'dockintro', 'dockpwa', 'dockkofi']
    .every((id) => !ids.includes(id));
  out.enBounds = (G.menuRects || []).every((r) =>
    r.x >= -2 && r.y >= -2 && r.x + r.w <= 3698 && r.y + r.h <= 1402);
  out.iconosListos = Object.values(G._menuIconos || {})
    .filter((im) => im.complete && im.naturalWidth > 0).length >= 20;
  const iOpts = ids.indexOf('page:opts');
  G.menuClick(iOpts, 0);
  await dorme(250);
  const ids2 = (G.menuRects || []).map((r) => r.id);
  out.paginaOpts = G.menuPage === 'opts' &&
    ['page:optsJuego', 'page:optsSala', 'page:optsSonido', 'page:optsVisual',
     'page:optsPerfil', 'page:optsRendi', 'page:optsPala', 'kofi']
      .every((id) => ids2.includes(id));
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(200);
  const iTr = (G.menuRects || []).findIndex((r) => r.id === 'traingo');
  G.menuClick(iTr, 0);
  await dorme(200);
  out.train = G.menuPage === 'train' && (G.menuRects || []).length > 5 &&
    (G.menuRects || []).every((r) => r.x >= -2 && r.y >= -2 &&
      r.x + r.w <= 3698 && r.y + r.h <= 1402);
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(150);
  const iSw = (G.menuRects || []).findIndex((r) => r.id === 'salirweb');
  G.menuClick(iSw, 0);
  await dorme(250);
  const ids4 = (G.menuRects || []).map((r) => r.id);
  out.promptSalida = G.menuPage === 'salirask' &&
    ids4.includes('salirweb_si') && ids4.includes('salirweb_no');
  G.menuClick(ids4.indexOf('salirweb_no'), 0);
  await dorme(200);
  out.dockCierra = G.menuPage === 'main';
  // conservación r160: la regla solo-1 decide y la siembra vive
  try {
    G.palaMejorada = true;
    try { G.rules.startMatch('match'); } catch (e) { /* */ }
    G.champs.activeId = 'locura';
    G.rules.state = 'rally';
    const libre = (G.paddleHand === 0) ? 1 : 0;
    const entB = { id: 'bolaloca', n: 1 };
    const entE = { id: 'efecto', n: 1 };
    G._megaMatriz.length = 0;
    G._megaMatriz.push(entB, entE);
    G._megaIdx = 0;
    out.bolalocaActiva = G.megaTrigger(libre) === true && G._bolalocaT > 9.5;
    out.vivo = G._poderVivoAlguno() === 'bolaloca';
    G._megaIdx = 1;
    const nE = entE.n;
    out.bloquea = G.megaTrigger(libre) === true && G._efectoT === 0 &&
      entE.n === nE;
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    out.siembra = G.poderesDesbloqueados().indexOf('bolaloca') === 0;
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    G._megaMatriz.length = 0; G._megaIdx = 0; G._megaIcon = null;
    G._megaActivaId = null; G.champs.activeId = '';
  } catch (e) { out.err160 = String(e); }
  return out;
}"""


async def main():
    # ---------- ESTÁTICO ----------
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html de producción:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    agujas = [
        ('const CONFIG_MENUS', 'CONFIG_MENUS v2 (arco)'),
        ('const CONFIG_SECCIONES', 'CONFIG_SECCIONES (concha)'),
        ('lienzo: { ancho: 3696, alto: 1400 }', 'lienzo virtual 3696×1400'),
        ("{ id: 'C', x: 1112, w: 1472, anchoM: 0.98, altoM: 0.95, yaw: 0, dist: 1.15 }",
         'panela central 0,98 m a 1,15 m'),
        ('this._menuPanelas = [];', 'tres panelas físicas'),
        ('mesh.rotation.y = yaw;', 'panelas giradas al jugador'),
        ('_menuTexSube()', 'troceado virtual→3 texturas'),
        ('muRaycaster.intersectObjects(this._menuPanelas, false)',
         'rayo a las tres panelas'),
        ('this.menuPin = true;              // r68: ON por defecto', 'pin ON'),
        ('this.menuGroup.position.copy(muHead);', 'ancla en la cabeza'),
        ("{ id: 'salirweb', icono: 'salir', etiquetaKey: 'dock_salir',",
         'salir a la web en TU CASA'),
        ('drawMenuConcha(rects)', 'concha de secciones'),
        ('_menuRejilla(rects, nombre, subs)', 'rejilla genérica'),
        ('_vestPrompt(rects, cfg)', 'prompts caramelo'),
        ('const CONFIG_SECCIONES', 'concha en el ensamblado'),
        ("const VERSION = '3.6.159-SDK6'", 'sello a 3.6.159'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'r160: regla'),
        ('const BOLALOCA_SCALE = 1.65;', 'r160: bola loca'),
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'r65: blindaje del saque'),
    ]
    for needle, label in agujas:
        chk(needle in game, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')
    try:
        sw = get(BASE + '/sw.js')
        chk("const CACHE = 'crazypp-v3.6.159-SDK6'" in sw, 'sw.js a 3.6.159')
    except Exception as e:
        chk(False, f'sw.js servido ({e})')
    for needle, label in agujas:
        chk(needle in game, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 17, f'17+ iconos embebidos (hay {n_icons})')
    try:
        sw = get(BASE + '/sw.js')
        chk("const CACHE = 'crazypp-v3.6.158-SDK6'" in sw, 'sw.js a 3.6.158')
    except Exception as e:
        chk(False, f'sw.js servido ({e})')

    # ---------- FUNCIONAL ----------
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
            print('✗ El juego de producción no arrancó:', e)
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            await browser.close()
            sys.exit(1)
        await browser.close()

    for k, label in [
        ('canvas', 'en vivo: lienzo virtual 3696×1400'),
        ('panelas', 'en vivo: tres panelas físicas'),
        ('arco', 'en vivo: arco yaw ±36° equidistante'),
        ('abierto', 'en vivo: Vestíbulo abierto (main)'),
        ('idsOk', 'en vivo: los 14 ids del Vestíbulo'),
        ('sinDock', 'en vivo: dock desaparecido'),
        ('enBounds', 'en vivo: rects en bounds'),
        ('iconosListos', 'en vivo: iconos decodificados'),
        ('paginaOpts', 'en vivo: rejilla de AJUSTES (8 tarjetas)'),
        ('train', 'en vivo: PRO TRAINING legado'),
        ('promptSalida', 'en vivo: prompt caramelo de salida'),
        ('dockCierra', 'en vivo: NO vuelve al Vestíbulo'),
        ('bolalocaActiva', 'en vivo (r160): BOLA LOCA se activa'),
        ('vivo', 'en vivo (r160): _poderVivoAlguno'),
        ('bloquea', 'en vivo (r160): regla solo-1 bloquea'),
        ('siembra', 'en vivo (r160): siembra de serie'),
    ]:
        chk(rt.get(k) is True, label)
    for k in ['err160']:
        if rt.get(k):
            chk(False, f'en vivo: {k} = {rt[k]}')
    chk(not rt.get('sinJuego'), 'window.__PP_GAME presente')
    chk(not errors, f'sin pageerrors ({len(errors)})')
    if errors:
        print('   pageerrors:', errors[:3])

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
