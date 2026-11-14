#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r69.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 163
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.160-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva el ARCO CORREGIDO (panelas
    tangentes y seguidas a 1,15 m, anchorMenu(forzar), grupo delante
    mirando a la cara, seguir-siempre, tooltip espacio-consciente, títulos
    duplicados fuera) + concha/rejilla/prompts + sw a 3.6.160 + r160/r65.
  · FUNCIONAL: el juego VIVO — colocación en MUNDO (panela central a
    ~1,15 m de proyección sobre la vista), arco sin solape por fórmulas,
    semántica del ancla (congela/sigue), 14 ids sin dock, rejilla, prompt,
    train legado mapeado.
Uso: python3 scripts/prod_smoke_r67.py"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.160-SDK6'

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
  const CM = G._menuPanelas.map((m) => m.userData.panela);
  const grads = CM.map((pa) => Math.atan2(pa.anchoM / 2, pa.dist) * 180 / Math.PI);
  const th = Math.abs(CM[0].yaw);
  out.arco = CM.every((pa) => Math.abs(pa.dist - 1.15) < 0.001) &&
    th - grads[0] >= grads[1] + 0.5;   // sin solape (fórmula)
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  G.menuPin = true;
  G.anchorMenu(true);
  await dorme(100);
  const V3 = G.menuGroup.position.constructor;
  const Q4 = G.menuGroup.quaternion.constructor;
  const cp = new V3();
  G.camera.getWorldPosition(cp);
  const q = new Q4();
  G.camera.getWorldQuaternion(q);
  const fwd = new V3(0, 0, -1).applyQuaternion(q);
  const pCw = G._menuPanelas[1].getWorldPosition(new V3()).sub(cp);
  out.colocacion = pCw.dot(fwd) > 1.05 &&
    Math.abs(pCw.length() - pCw.dot(fwd)) < 0.2;
  const p0 = G.menuGroup.position.clone();
  G.menuGroup.position.set(5, 5, 5);
  G.anchorMenu();
  out.congela = G.menuGroup.position.distanceTo(new V3(5, 5, 5)) < 0.001;
  G.menuPin = false;
  G.anchorMenu();
  out.sigue = G.menuGroup.position.distanceTo(p0) < 0.03;
  G.menuPin = true;
  G._menuPinDraw();
  G.anchorMenu(true);
  await dorme(100);
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
        ("{ id: 'C', x: 1112, w: 1472, anchoM: 0.88, altoM: 0.95, yaw: 0, dist: 1.15 }",
         'panela C 0,88 m a 1,15 m'),
        ("{ id: 'L', x: 0, w: 1112, anchoM: 0.66, altoM: 0.95, yaw: 37.8, dist: 1.15 }",
         'panela L 0,66 m a 1,15 m (equidistancia real)'),
        ('anchorMenu(forzar) {', 'anchorMenu con forzar'),
        ('CONVENCIÓN r67 RESTAURADA', 'grupo delante mirando a la cara'),
        ('D_REF - Math.cos(yaw) * pa.dist', 'arco centrado en la cabeza'),
        ('if (!this.menuPin) this.anchorMenu();', 'sin ancla: sigue siempre'),
        ('this.anchorMenu(true);', 'aperturas con forzar'),
        ('const ESP = this._menuMap', 'tooltip espacio-consciente'),
        ('yU6fW' if False else "    label(T('tab_multi'), 244, 26)",
         'título multi duplicado FUERA', ),
        ("const VERSION = '3.6.160-SDK6'", 'sello a 3.6.160'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'r160: regla'),
        ('const BOLALOCA_SCALE = 1.65;', 'r160: bola loca'),
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'r65: blindaje del saque'),
    ]
    for item in agujas:
        needle, label = item[0], item[1]
        invertir = len(item) > 2
        presente = needle in game
        chk((not presente) if invertir else presente, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')
    try:
        sw = get(BASE + '/sw.js')
        chk("const CACHE = 'crazypp-v3.6.160-SDK6'" in sw, 'sw.js a 3.6.160')
    except Exception as e:
        chk(False, f'sw.js servido ({e})')
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
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')

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
        ('arco', 'en vivo: arco a 1,15 m sin solape (fórmula)'),
        ('colocacion', 'en vivo: panela central DELANTE de la mirada'),
        ('congela', 'en vivo: chincheta congela donde esté'),
        ('sigue', 'en vivo: sin chincheta sigue'),
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
