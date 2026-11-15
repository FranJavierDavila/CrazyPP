#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r70.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 164 · r70
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.161-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva EL APARTADO COMPLETO (aspecto
    exacto por panela, silueta redondeada, arco recalculado por página,
    lados condicionales, banda ATRÁS sobre la C, landings formato Ajustes,
    «Volver al Hall» fuera de Entrenar) + ancla r69 íntegra + sw a 3.6.161
    + PAGES-VERSION.txt con fuente_commit=d2a9c36.
  · FUNCIONAL: el juego VIVO — aspecto texel==rodaja, central ~1 m, yaw por
    fórmula, colocación en mundo, congela/sigue, lados condicionales en 26
    páginas, barrido en bounds, banda ATRÁS flotante, 5 landings nuevas,
    rejilla de AJUSTES, ids del Vestíbulo, prompt de salida y r160.
Uso: python3 scripts/prod_smoke_r70.py"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.161-SDK6'

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
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }
  const V3 = G.menuGroup.position.constructor;

  // — 1 · ASPECTO EXACTO + YAW POR FÓRMULA (fin de las elipses) —
  const pas = G.menuGroup.children
    .filter((m) => m.userData && m.userData.panela)
    .map((m) => m.userData.panela);
  out.texelOk = pas.every((pa) =>
    Math.abs((pa.anchoM / pa.w) - (pa.altoM / 1400)) < 0.001);
  out.centralGrande = pas[1].anchoM > 0.95;
  const gam = (pa) => Math.atan(pa.anchoM / 2 / pa.dist) * 180 / Math.PI;
  const ranura = Math.atan(0.017 / 1.15) * 180 / Math.PI;
  out.formulaOk = Math.abs(pas[0].yaw - (gam(pas[1]) + gam(pas[0]) + ranura)) < 0.01
    && Math.abs(pas[2].yaw + (gam(pas[1]) + gam(pas[2]) + ranura)) < 0.01;
  out.distOk = pas.every((pa) => Math.abs(pa.dist - 1.15) < 0.001);

  // — 2 · COLOCACIÓN EN MUNDO (delante de la mirada a ~1,15 m) —
  if (!G.menuOpen) G.toggleMenu();
  await dorme(400);
  G.menuPin = true;
  G.anchorMenu(true);
  await dorme(120);
  const c2c = G.menuMesh.getWorldPosition(new V3())
    .sub(G.camera.getWorldPosition(new V3()));
  const camF = G.camera.getWorldDirection(new V3());
  const dist = c2c.length();
  const frente = c2c.dot(camF) / Math.max(0.001, dist);
  out.colocacionC = dist > 1.05 && dist < 1.30 && frente > 0.75;

  // — 3 · SEMÁNTICA DEL ANCLA (r69 intacto) —
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

  // — 4 · BLOQUES CONDICIONALES: panelas montadas == lados del dato —
  const ESPERAN = {
    main: 3, multi: 1, join: 1, name: 1, gripname: 1,
    rankini: 1, rank: 1, rankme: 1, champs: 2, champuno: 1, champhist: 1,
    train: 2, trainext: 2, trainarea: 1, carrera: 1, carreradiv: 1,
    opts: 2, optsJuego: 1, optsSala: 1, optsSonido: 1, optsVisual: 1,
    optsPerfil: 1, optsRendi: 1, optsPala: 1,
    salirask: 1, hallask: 1,
  };
  out.ladosMalos = [];
  for (const [pg, esperado] of Object.entries(ESPERAN)) {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    await dorme(30);
    if (G._menuPanelas.length !== esperado)
      out.ladosMalos.push(pg + ':' + G._menuPanelas.length + '/' + esperado);
  }
  out.ladosOk = out.ladosMalos.length === 0;

  // — 5 · BARRIDO: rects dentro del lienzo virtual en TODAS las páginas —
  out.paginasMalas = [];
  for (const pg of Object.keys(ESPERAN)) {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    await dorme(30);
    const rs = G.menuRects || [];
    const malas = rs.filter((r) => r.x < -2 || r.y < -2 ||
        r.x + r.w > 3698 || r.y + r.h > 1402).map((r) => r.id);
    if (!rs.length || malas.length)
      out.paginasMalas.push(pg + (malas.length ? ':' + malas.join(',') : ''));
  }
  out.todasLimpias = out.paginasMalas.length === 0;

  // — 6 · BANDA DE NAVEGACIÓN COMÚN sobre el bloque central —
  G.menuPage = 'opts';
  G.drawMenu();
  await dorme(60);
  const atras = (G.menuRects || []).find((r) => r.id === 'page:main');
  out.bandaOk = !!atras && atras.y < 140 &&
    atras.x > 1112 && atras.x + atras.w < 2584;

  // — 7 · LANDINGS NUEVAS con sus tarjetas —
  const cardsDe = (pg) => {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    return (G.menuRects || []).map((r) => String(r.id));
  };
  out.multiOk = ['mjnorm', 'mjduel', 'net:join'].every((id) =>
    cardsDe('multi').includes(id));
  out.rankOk = ['wrl:tab', 'page:rankme'].every((id) =>
    cardsDe('rankini').includes(id));
  const idsTrain = cardsDe('train');
  out.trainOk = ['trv3:area:dir', 'trv3:semana', 'page:trainext']
    .every((id) => idsTrain.includes(id)) && !idsTrain.includes('homehall');
  out.champsOk = cardsDe('champs').includes('page:champhist');
  out.carreraOk = cardsDe('carrera')
    .filter((i) => i.indexOf('carrera:sel:') === 0).length === 5;

  // — 8 · VESTÍBULO principal —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(150);
  const ids = (G.menuRects || []).map((r) => r.id);
  const requeridos = ['start', 'carrera:abre', 'traingo', 'survgo',
    'tab:multi', 'page:champs', 'wrl:open', 'homehall', 'tut:go',
    'page:opts', 'salirweb', 'close', 'lang:es', 'lang:en'];
  out.idsOk = requeridos.every((id) => ids.includes(id));
  out.sinDock = ['docktv', 'dockintro', 'dockpwa', 'dockkofi']
    .every((id) => !ids.includes(id));
  out.iconosListos = Object.values(G._menuIconos || {})
    .filter((im) => im.complete && im.naturalWidth > 0).length >= 20;

  // — 9 · rejilla de AJUSTES (r68 conservado) —
  G.menuPage = 'opts';
  G.drawMenu();
  await dorme(200);
  const ids2 = (G.menuRects || []).map((r) => r.id);
  out.paginaOpts = G.menuPage === 'opts' &&
    ['page:optsJuego', 'page:optsSala', 'page:optsSonido', 'page:optsVisual',
     'page:optsPerfil', 'page:optsRendi', 'page:optsPala', 'kofi']
      .every((id) => ids2.includes(id));

  // — 10 · prompt de salida (caramelo en la C) —
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(120);
  const iSw = (G.menuRects || []).findIndex((r) => r.id === 'salirweb');
  G.menuClick(iSw, 0);
  await dorme(250);
  const ids4 = (G.menuRects || []).map((r) => r.id);
  out.promptSalida = G.menuPage === 'salirask' &&
    ids4.includes('salirweb_si') && ids4.includes('salirweb_no');
  G.menuClick(ids4.indexOf('salirweb_no'), 0);
  await dorme(200);

  // — 11 · conservación r160: BOLA LOCA + regla solo-1 —
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
    out.bloquea = G.megaTrigger(libre) === true && G._efectoT === 0;
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    out.siembra = G.poderesDesbloqueados().indexOf('bolaloca') === 0;
    try { localStorage.removeItem('pp_poderes_v1'); } catch (e) { /* */ }
    G._megaMatriz.length = 0; G._megaIdx = 0; G._megaIcon = null;
    G._megaActivaId = null; G.champs.activeId = '';
  } catch (e) { out.err160 = String(e); }
  G.menuPage = 'main';
  G.drawMenu();
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
        # — r70 · aspecto exacto + silueta redondeada + arco calculado —
        ('pa.anchoM = (pa.w / CONFIG_MENUS.lienzo.alto) * pa.altoM;',
         'ASPECTO EXACTO por panela (fin de las elipses)'),
        ('_menuShapePanela(pa)', 'silueta ShapeGeometry redondeada'),
        ('radioEsquinaM: 0.036', 'esquinas en curva (4/4)'),
        ('_menuArco(ids)', 'arco recalculado por página (bloques condicion.)'),
        ('gam(pC) + gam(pL) + ranura', 'yaw POR FÓRMULA desde anchuras reales'),
        ('ranuraM: 0.017', 'ranura uniforme conservada (r69)'),
        # — r70 · lados condicionales —
        ("main: ['L', 'C', 'R']", 'lados del Vestíbulo (3 panelas)'),
        ("multi: ['C']", 'MULTIJUGADOR en una panela'),
        ("champs: ['C', 'R']", 'CAMPEONATOS en dos panelas'),
        ("train: ['C', 'R']", 'ENTRENAR en dos panelas'),
        # — r70 · banda de navegación común —
        ('BANDA DE NAVEGACIÓN COMÚN sobre el bloque central',
         'ATRÁS flotante documentado en la concha'),
        ("c.fillText(T('btn_back'), bx + 94", 'ATRÁS en la panela C'),
        # — r70 · landings en formato Ajustes —
        ("multi: { columnas: ['C'], y: 300", 'rejilla MULTIJUGADOR'),
        ("rank: { columnas: ['C'], y: 300", 'rejilla RANKING'),
        ("train: { columnas: ['C', 'R'], y: 300", 'rejilla ENTRENAR'),
        ("champs: { columnas: ['C', 'R'], y: 300", 'rejilla CAMPEONATOS'),
        ("carrera: { columnas: ['C'], y: 300", 'rejilla CARRERA'),
        ('drawMenuChampUno', 'detalle de campeonato'),
        ('drawMenuCarreraDiv', 'división con rivales'),
        ('drawMenuRankIni', 'landing de Ranking'),
        ('_multiSala(rects, st)', 'estados de sala en la panela C'),
        # — r70 · «Volver al Hall» fuera de Entrenar —
        ('FUERA «Volver al Hall» (petición del dueño', 'hall fuera del train'),
        # — r69 · conservado íntegro —
        ('anchorMenu(forzar) {', 'anchorMenu con forzar'),
        ('CONVENCIÓN r67 RESTAURADA', 'grupo delante mirando a la cara'),
        ('D_REF - Math.cos(yaw) * pa.dist', 'arco centrado en la cabeza'),
        ('if (!this.menuPin) this.anchorMenu();', 'sin ancla: sigue siempre'),
        ('this.anchorMenu(true);', 'aperturas con forzar'),
        ('const ESP = this._menuMap', 'tooltip espacio-consciente'),
        # — legado duplicado FUERA (dedup r69 + backs r70) —
        ("    label(T('tab_multi'), 244, 26)", 'título multi duplicado FUERA', True),
        ("    btn('page:champs', 40, 216, 240, 60", 'back legado del historial FUERA', True),
        ('drawHub(this, c, rects', 'hub legado de train desconectado', True),
        # — sello —
        ("const VERSION = '3.6.161-SDK6'", 'sello a 3.6.161'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'r160: regla'),
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'r65: blindaje del saque'),
    ]
    for item in agujas:
        needle, label = item[0], item[1]
        invertir = len(item) > 2
        presente = needle in game
        chk((not presente) if invertir else presente, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')
    i0 = game.find('function drawExtras')
    i1 = game.find('menuAction(game, arg)', i0)
    chk('homehall' not in game[i0:i1],
        'sin «Volver al Hall» en drawExtras (train)')
    try:
        sw = get(BASE + '/sw.js')
        chk("const CACHE = 'crazypp-v3.6.161-SDK6'" in sw, 'sw.js a 3.6.161')
    except Exception as e:
        chk(False, f'sw.js servido ({e})')
    try:
        pv = get(BASE + '/PAGES-VERSION.txt')
        chk('version=3.6.161-SDK6' in pv and 'fuente_commit=d2a9c36' in pv,
            'PAGES-VERSION.txt: 3.6.161 desde d2a9c36')
    except Exception as e:
        chk(False, f'PAGES-VERSION.txt ({e})')

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
            await page.wait_for_function('!!window.__PP_GAME', timeout=60000)
            await page.wait_for_timeout(1500)
            rt = await page.evaluate(JS)
        except Exception as e:
            print('✗ El juego de producción no arrancó:', e)
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            await browser.close()
            sys.exit(1)
        await browser.close()

    for k, label in [
        ('texelOk', 'en vivo: aspecto texel==rodaja en las 3 panelas'),
        ('centralGrande', 'en vivo: central recupera ~1,00 m (>0,95)'),
        ('formulaOk', 'en vivo: yaw por fórmula con ranura 1,7 cm'),
        ('distOk', 'en vivo: arco a 1,15 m'),
        ('colocacionC', 'en vivo: panela C DELANTE de la mirada'),
        ('congela', 'en vivo: chincheta congela donde esté'),
        ('sigue', 'en vivo: sin chincheta sigue'),
        ('ladosOk', 'en vivo: panelas montadas == lados del dato (26 págs)'
         + ('' if rt.get('ladosOk') else f' → {rt.get("ladosMalos", [])[:4]}')),
        ('todasLimpias', 'en vivo: rects en bounds en TODAS las páginas'
         + ('' if rt.get('todasLimpias') else f' → {rt.get("paginasMalas", [])[:4]}')),
        ('bandaOk', 'en vivo: ATRÁS flotante sobre el bloque central (y<140)'),
        ('multiOk', 'en vivo: rejilla MULTIJUGADOR (crear/unirse/código)'),
        ('rankOk', 'en vivo: rejilla RANKING (tabla + mi posición)'),
        ('trainOk', 'en vivo: rejilla ENTRENAR sin «Volver al Hall»'),
        ('champsOk', 'en vivo: rejilla CAMPEONATOS con historial'),
        ('carreraOk', 'en vivo: CARRERA con las 5 divisiones'),
        ('idsOk', 'en vivo: los 14 ids del Vestíbulo'),
        ('sinDock', 'en vivo: dock desaparecido'),
        ('iconosListos', 'en vivo: iconos decodificados'),
        ('paginaOpts', 'en vivo: rejilla de AJUSTES (8 tarjetas)'),
        ('promptSalida', 'en vivo: prompt caramelo de salida'),
        ('bolalocaActiva', 'en vivo (r160): BOLA LOCA se activa'),
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
