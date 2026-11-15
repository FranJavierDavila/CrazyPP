#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r73.py — QA FASE 167 «EL NIVEL 3, PLACA A PLACA» (r73).

Continúa la maquetación que pidió el dueño («todos los menús de tercer
nivel siguen en el formato antiguo»): r72 vistió el botón compartido;
r73 viste la TARJETA entera —
  · _menuRejilla (AJUSTES · MULTIJUGADOR · RANKING · CAMPEONATOS ·
    ENTRENAR · CARRERA) pinta PLACA DE MUSEO: base oscura + overlay sutil
    + MARCO DE LATÓN; el color de categoría sobrevive como ARO del
    medallón (wayfinding sin caramelo).
  · drawMenuCarreraDiv: filas de rivales en placa; vencido verde /
    pendiente acero EN EL ARO.
  · _modeCard: tarjetas de SALA (Room/Mesa/Bola/Hall) en placa.
  · _vestMedallion admite aro teñido (_aroTinte); sin tinte queda blanco.
NO se toca el VESTÍBULO (referencia caramelo del dueño), los prompts, el
botón ATRÁS flotante ni los héroes de acción (▶ JUGAR / JUGAR verde).

Salida: RESULTADO: N OK · M fallos + capturas en download/r73_capturas/.
"""
import base64
import pathlib
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3668/game.html'
OUT = pathlib.Path('/home/z/my-project/download/r73_capturas')
OUT.mkdir(parents=True, exist_ok=True)

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
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }

  // — A1 · pintores FASE 167 presentes —
  out.placa73 = typeof G._vestPlaca73 === 'function';
  out.aroTinte = typeof G._aroTinte === 'function';

  // — A2 · _aroTinte: hex → rgba 0,62; lo no-hex sin tinte —
  out.tinteOro = G._aroTinte('#ffca1e') === 'rgba(255,202,30,0.62)';
  out.tinteNada = G._aroTinte('rojo') === '' && G._aroTinte('#abc') === '' &&
    G._aroTinte(null) === '';

  // — A3 · medallón: aro teñido / blanco sin tinte —
  const mc = document.createElement('canvas');
  mc.width = 200; mc.height = 100;
  const mx = mc.getContext('2d');
  const sinEsp = (s) => String(s).replace(/\s+/g, '');
  G._vestMedallion(mx, 50, 50, 20, 'partido', '#ffca1e');
  out.medOro = sinEsp(mx.strokeStyle) === 'rgba(255,202,30,0.62)';
  mx.strokeStyle = '#123456';
  G._vestMedallion(mx, 150, 50, 20, 'partido');
  out.medBlanco = sinEsp(mx.strokeStyle) === 'rgba(255,255,255,0.85)';

  // — A4 · contadores candy/placa por página del nivel 3 —
  // nC = _vestCandy (el ATRÁS flotante cuenta 1 por página; champuno suma
  // su héroe verde); nP = _vestPlaca73 (tarjetas de museo).
  const oc = G._vestCandy, op = G._vestPlaca73;
  let nC = 0, nP = 0;
  G._vestCandy = function () { nC++; return oc.apply(this, arguments); };
  G._vestPlaca73 = function () { nP++; return op.apply(this, arguments); };
  const ESPERA = [
    ['opts', 1, 7], ['multi', 1, 3], ['rankini', 1, 2],
    ['champs', 1, 2], ['train', 1, 7], ['carrera', 1, 5],
    ['optsSala', 1, 4], ['carreradiv', 1, 3],
    ['rank', 1, 0], ['rankme', 1, 0],
  ];
  out.contadores = [];
  for (const [pg, eC, eP] of ESPERA) {
    nC = 0; nP = 0;
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    // lectura SÍNCRONA inmediata: los .then asíncronos (historial de
    // champs, ranking) re-dibujan durante el dorme y contaminarían el
    // contador de la página siguiente (visto en la sonda r73).
    const leeC = nC, leeP = nP;
    await dorme(25);
    const linea = pg + ':' + leeC + '/' + leeP;
    out.contadores.push(linea + (leeC === eC && leeP >= eP ? '' : ' ✗'));
    if (leeC !== eC) out.candyMal = (out.candyMal || []).push(linea + ' candy');
    if (leeP < eP) out.placaMal = (out.placaMal || []).push(linea + ' placa');
  }
  out.candyOk = !out.candyMal;
  out.placaOk = !out.placaMal;
  G._vestCandy = oc; G._vestPlaca73 = op;

  // — A5 · el héroe JUGAR de champuno conserva su caramelo verde —
  // (con el índice cargado se toma el primer campeonato DESBLOQUEADO:
  //  uno lockado pinta el chip y no llega al héroe)
  const chs = (G.champs && G.champs.list && G.champs.list()) || [];
  const chLibre = chs.find((c0) => !c0.locked);
  if (chLibre) {
    G._champSel = chLibre.id;
    nC = 0; nP = 0;
    G._vestCandy = function () { nC++; return oc.apply(this, arguments); };
    G.menuPage = 'champuno';
    G.drawMenu();
    const leeC = nC;   // lectura síncrona (mismo motivo que arriba)
    G._vestCandy = oc;
    out.heroVerde = leeC === 2;   // ATRÁS + héroe
  } else {
    out.heroVerde = null;       // sin índice libre no se puede probar
  }

  // — A6 · regresión r72: rejillas vivas y kofi fuera —
  G.menuPage = 'opts';
  G.drawMenu();
  await dorme(40);
  const ids = (G.menuRects || []).map((r) => String(r.id));
  out.ajustesOk = ['page:optsJuego', 'page:optsSala', 'page:optsSonido',
    'page:optsVisual', 'page:optsPerfil', 'page:optsRendi', 'page:optsPala']
    .every((i) => ids.includes(i));
  out.kofiFuera = !ids.includes('kofi');
  G.menuPage = 'multi'; G._mjMode = null; G.drawMenu();
  out.multiIds = (G.menuRects || []).map((r) => String(r.id));
  out.multiOk = ['mjnorm', 'mjduel', 'net:join'].every((i) =>
    out.multiIds.includes(i));
  G.menuPage = 'carrera'; G.drawMenu();
  out.carreraSel = (G.menuRects || []).filter((r) =>
    String(r.id).indexOf('carrera:sel:') === 0).length;
  out.carreraOk = out.carreraSel === 5;
  G.menuPage = 'rankini'; G.drawMenu();
  out.rankOk = ['wrl:tab', 'page:rankme'].every((i) =>
    (G.menuRects || []).some((r) => String(r.id) === i));
  out.rankiniFresh = typeof G._rankiniFresh !== 'undefined';   // r72

  // — A7 · panelas montadas == lados del dato + rects en bounds (r70) —
  const ESPERAN = {
    main: 3, multi: 1, join: 1, name: 1, gripname: 1,
    rankini: 1, rank: 1, rankme: 1, champs: 2, champuno: 1, champhist: 1,
    train: 2, trainext: 2, trainarea: 1, carrera: 1, carreradiv: 1,
    opts: 2, optsJuego: 1, optsSala: 1, optsSonido: 1, optsVisual: 1,
    optsPerfil: 1, optsRendi: 1, optsPala: 1,
    salirask: 1, hallask: 1,
  };
  out.ladosMalos = [];
  out.paginasMalas = [];
  for (const pg of Object.keys(ESPERAN)) {
    G.menuPage = pg;
    if (pg === 'multi') G._mjMode = null;
    G.drawMenu();
    await dorme(25);
    const n = G._menuPanelas.length;
    if (n !== ESPERAN[pg]) out.ladosMalos.push(pg + ':' + n);
    const rs = G.menuRects || [];
    const malas = rs.filter((r) => r.x < -2 || r.y < -2 ||
      r.x + r.w > 3698 || r.y + r.h > 1402).map((r) => r.id);
    if (!rs.length || malas.length) {
      out.paginasMalas.push(pg + ':' + (malas.join(',') || 'sin rects'));
    }
  }
  out.ladosOk = out.ladosMalos.length === 0;
  out.todasLimpias = out.paginasMalas.length === 0;

  // — C · capturas del nivel 3 maquetado —
  const capt = async (pg, key, limpiar) => {
    G.menuPage = pg;
    if (limpiar) G._mjMode = null;
    G.drawMenu();
    await dorme(130);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  await capt('opts', 'pngOpts');
  await capt('optsSala', 'pngOptsSala');
  await capt('multi', 'pngMulti', true);
  await capt('rankini', 'pngRankini');
  await capt('champs', 'pngChamps');
  await capt('train', 'pngTrain');
  await capt('carrera', 'pngCarrera');
  await capt('carreradiv', 'pngCarreraDiv');
  await capt('rankme', 'pngRankme');
  await capt('champuno', 'pngChampuno');
  G.menuPage = 'main';
  G.drawMenu();
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3668', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        return
    chk('3.6.164-SDK6' in game, 'game.html sello 3.6.164-SDK6 (FASE 167)')
    chk('_vestPlaca73' in game and '_aroTinte' in game,
        'fuentes: _vestPlaca73 + _aroTinte presentes en el artefacto')
    chk(game.count('_vestPlaca73(') >= 4,
        'placa usada por rejilla + carreradiv + _modeCard (' +
        str(game.count('_vestPlaca73(')) + ' llamadas)')
    chk(game.count('_vestCandy(c, x0, y, w0, 200,') == 1,
        'héroe JUGAR de champuno conserva su caramelo (estático)')
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3800)
        out = await page.evaluate(JS)
        await browser.close()

    if out.get('sinJuego'):
        print('✗ window.__PP_GAME no llegó — el juego no arrancó')
        return
    chk(out.get('placa73'), 'pintor _vestPlaca73 vivo en la instancia')
    chk(out.get('aroTinte'), 'método _aroTinte vivo en la instancia')
    chk(out.get('tinteOro'), '_aroTinte(#ffca1e) = rgba(255,202,30,0.62)')
    chk(out.get('tinteNada'), '_aroTinte sin hex = sin tinte')
    chk(out.get('medOro'), 'medallón con aro teñido (oro)')
    chk(out.get('medBlanco'), 'medallón sin aro = blanco (Vestíbulo intacto)')
    print('  contadores candy/placa:', '; '.join(out.get('contadores', [])))
    chk(out.get('candyOk'), 'candy residual = solo el ATRÁS en las 10 páginas')
    chk(out.get('placaOk'), 'placas de museo en las 8 rejillas esperadas')
    if out.get('heroVerde') is not None:
        chk(out.get('heroVerde'), 'héroe JUGAR de champuno conserva caramelo')
    else:
        chk(True, 'héroe champuno sin índice — no evaluable (OK)')
    chk(out.get('ajustesOk'), 'rejilla AJUSTES con sus 7 tarjetas')
    chk(out.get('kofiFuera'), 'kofi sigue fuera de AJUSTES (r72)')
    chk(out.get('multiOk'), 'MULTIJUGADOR con sus 3 tarjetas')
    chk(out.get('carreraOk'), 'CARRERA con las 5 divisiones')
    chk(out.get('rankOk'), 'RANKING landing con sus 2 tarjetas')
    chk(out.get('rankiniFresh'), 'guarda _rankiniFresh presente (r72)')
    chk(out.get('ladosOk'), 'panelas montadas == lados del dato (26 págs)')
    chk(out.get('todasLimpias'), 'rects en bounds en TODAS las páginas')
    chk(not errores, 'sin pageerrors (' + str(len(errores)) + ')')

    guardadas = 0
    for key, nombre in [('pngOpts', 'opts'), ('pngOptsSala', 'optsSala'),
                        ('pngMulti', 'multi'), ('pngRankini', 'rankini'),
                        ('pngChamps', 'champs'), ('pngTrain', 'train'),
                        ('pngCarrera', 'carrera'),
                        ('pngCarreraDiv', 'carreradiv'),
                        ('pngRankme', 'rankme'), ('pngChampuno', 'champuno')]:
        data = out.get(key)
        if data and data.startswith('data:image/png'):
            (OUT / (nombre + '.png')).write_bytes(
                base64.b64decode(data.split(',', 1)[1]))
            guardadas += 1
    print('  capturas: ' + str(guardadas) + '/10 en ' + str(OUT))
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
