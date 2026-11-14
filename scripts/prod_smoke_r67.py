#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r67.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 161
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.158-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva EL VESTÍBULO (CONFIG_MENUS +
    ICONOS_MENUS data-driven, drawMenuVestibulo, lienzo 2560×1440, plano
    1,60×0,90, rayo vivo, legado mapeado, dock DOM, i18n ES/EN) y la
    conservación r160 (BOLA LOCA + regla solo-1) + sw a 3.6.158.
  · FUNCIONAL: el juego VIVO — lienzo/plano, 18 ids del Vestíbulo, rects
    en bounds, navegación main→opts→main→train, docktv que cierra,
    iconos decodificados.
Uso: python3 scripts/prod_smoke_r67.py"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.158-SDK6'

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
  out.canvas = G.menuCanvas.width === 2560 && G.menuCanvas.height === 1440;
  const gp = G.menuMesh.geometry.parameters;
  out.plano = gp.width === 1.60 && gp.height === 0.90;
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  out.abierto = G.menuOpen === true && G.menuPage === 'main';
  await dorme(600);
  const ids = (G.menuRects || []).map((r) => r.id);
  const requeridos = ['start', 'carrera:abre', 'traingo', 'survgo',
    'tab:multi', 'page:champs', 'wrl:open', 'homehall', 'tut:go',
    'page:opts', 'docktv', 'dockintro', 'dockpwa', 'dockkofi', 'salirweb',
    'close', 'lang:es', 'lang:en'];
  out.idsOk = requeridos.every((id) => ids.includes(id));
  out.enBounds = (G.menuRects || []).every((r) =>
    r.x >= -2 && r.y >= -2 && r.x + r.w <= 2562 && r.y + r.h <= 1442);
  out.iconosListos = Object.values(G._menuIconos || {})
    .filter((im) => im.complete && im.naturalWidth > 0).length >= 12;
  const iOpts = ids.indexOf('page:opts');
  G.menuClick(iOpts, 0);
  await dorme(250);
  out.paginaOpts = G.menuPage === 'opts' && (G.menuRects || []).length > 5 &&
    (G.menuRects || []).every((r) => r.x >= -2 && r.y >= -2 &&
      r.x + r.w <= 2562 && r.y + r.h <= 1442);
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(200);
  const iTr = (G.menuRects || []).findIndex((r) => r.id === 'traingo');
  G.menuClick(iTr, 0);
  await dorme(200);
  out.train = G.menuPage === 'train' && (G.menuRects || []).length > 5;
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(150);
  const iTv = (G.menuRects || []).findIndex((r) => r.id === 'docktv');
  G.menuClick(iTv, 0);
  await dorme(250);
  out.dockCierra = G.menuOpen === false;
  // conservación r160: la regla solo-1 decide y la siembra vive
  try {
    G.palaMejorada = true;
    try { G.rules.startMatch('match'); } catch (e) { /* */ }
    G.champs.activeId = 'locura';
    G.rules.state = 'rally';
    G._megaMatriz.length = 0;
    G._megaMatriz.push({ id: 'bolaloca', n: 1 }, { id: 'efecto', n: 1 });
    G._megaIdx = 0;
    const libre = (G.paddleHand === 0) ? 1 : 0;
    out.bolalocaActiva = G.megaTrigger(libre) === true && G._bolalocaT > 9.5;
    out.vivo = G._poderVivoAlguno() === 'bolaloca';
    G._megaIdx = 1;
    const nE = G._megaMatriz[1].n;
    out.bloquea = G.megaTrigger(libre) === true && G._efectoT === 0 &&
      G._megaMatriz[1].n === nE;
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
        ('const CONFIG_MENUS', 'CONFIG_MENUS data-driven'),
        ('const ICONOS_MENUS', 'ICONOS_MENUS registro de iconos'),
        ("tituloKey: 'vest_compite'", 'panel COMPITE como dato'),
        ("tituloKey: 'vest_jugar'", 'panel JUGAR como dato'),
        ("tituloKey: 'vest_casa'", 'panel TU CASA como dato'),
        ('drawMenuVestibulo(rects)', 'render del Vestíbulo'),
        ('_vestSubPorId(id, def)', 'subtítulos vivos'),
        ('this._menuMap = { s: 0.9375, dx: 800, dy: 0 }',
         'legado: transform 0,9375 + dx 800'),
        ('_mapRect(o)', 'mapeo de rects del legado'),
        ('new THREE.PlaneGeometry(1.60, 0.90)', 'plano panorámico'),
        ('this.menuCanvas.width = 2560;', 'lienzo 2560'),
        ('hit.uv.x * this.menuCanvas.width', 'rayo: px vivos'),
        ("{ docktv: 'tvlink', dockintro: 'introbtn',", 'dock → botones DOM'),
        ("case 'docktv':", 'despachador: docktv'),
        ('this._menuPinMesh.position.set(0, 0.482, 0.006);', 'pin 0,482'),
        ("vest_jugar: 'JUGAR',", 'i18n ES'),
        ("vest_jugar: 'PLAY',", 'i18n EN'),
        ("const VERSION = '3.6.158-SDK6'", 'sello a 3.6.158'),
        # conservación r160
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'r160: regla'),
        ('const BOLALOCA_SCALE = 1.65;', 'r160: bola loca'),
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'r65: blindaje del saque'),
    ]
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
        ('canvas', 'en vivo: lienzo 2560×1440'),
        ('plano', 'en vivo: plano 1,60×0,90'),
        ('abierto', 'en vivo: Vestíbulo abierto (main)'),
        ('idsOk', 'en vivo: los 18 ids del Vestíbulo'),
        ('enBounds', 'en vivo: rects en bounds'),
        ('iconosListos', 'en vivo: iconos decodificados'),
        ('paginaOpts', 'en vivo: AJUSTES legado mapeado'),
        ('train', 'en vivo: PRO TRAINING legado'),
        ('dockCierra', 'en vivo: docktv cierra el menú'),
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
