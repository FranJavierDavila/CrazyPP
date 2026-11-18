#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r61.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 155
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.152-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_TORNEOS (partido/caminos/
    portada/candados/circuito) y CONFIG_LOGROS (core 6 + train 10) con sus
    lectores reales (c06 ACHIEVEMENTS derivado + COND_LOGRO + formato del
    árbitro · c11 LOCKED/portada/caminos+alias · c12 bestOfLibre ×7 ·
    c13 ACHS/LEVELS/combo/estrellas/hitos con RALLY_BONUS deduplicado),
    más la conservación completa r55/r56/r57/r58/r59/r60 y sw.js/portada
    a 3.6.152.
  · FUNCIONAL: el juego VIVO lee las dos tablas — GameStats desbloquea los
    SEIS medallones con los umbrales de CONFIG_LOGROS (aces 10 · maratón 20
    · supervivencia 25 · racha 3 · gigante en 'hard' · primera) y el ELO
    sigue moviéndose con CONFIG_DIFICULTAD (K 24, rival 1000 → +12); el
    ÁRBITRO alterna el saque con la cadencia de la tabla (cada 2 · cada
    punto en iguala) y el portadaId del ChampLoader resuelve desde el
    índice ('locura' eager). Restauración honesta del localStorage.
Uso: python3 scripts/prod_smoke_r61.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.152-SDK6'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME || window.__pingpong;
  const out = { presente: !!G };
  if (!G) return out;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  // — r61 · LOS LOGROS SON DATA-DRIVEN: GameStats desbloquea DESDE LA TABLA —
  const GS = window.__PP_GameStats;
  out.gsHook = typeof GS === 'function';
  if (GS) {
    const raw = localStorage.getItem('ppxr_stats_v1');
    const gs = new GS();          // instancia limpia para la prueba
    gs.data.ach = {};             // catálogo a cero SÓLO en la instancia de prueba
    gs.data.won = 0; gs.data.lost = 0; gs.data.streak = 0;
    gs.data.elo = 1000;           // ancla de la prueba (inicial del contrato r60)
    gs.data.hoyDia = { dia: '', v: 0 };
    // aces10 · cond.valor = 10 (CONFIG_LOGROS)
    let got = [];
    for (let i = 0; i < 10; i++) got = got.concat(gs.recordPoint('player', 1));
    out.aces10 = got.includes('aces10');
    // maraton · cond.valor = 20
    out.maraton = gs.recordRally(20).includes('maraton');
    // superviv · cond.valor = 25 (mejor histórica)
    out.superviv = gs.recordSurvivalRally(1, 25).includes('superviv');
    // primera + gigante ('hard' de la tabla) + ELO (K 24 · rival 1000 → +12)
    const g1 = gs.recordMatch(true, 'hard');
    out.primera = g1.includes('primera');
    out.gigante = g1.includes('gigante');
    out.eloTrasWin = gs.data.elo;          // 1012 = dato DIFICULTAD.elo vivo
    // racha3 · cond.valor = 3
    const g2 = gs.recordMatch(true, 'easy');
    const g3 = gs.recordMatch(true, 'easy');
    out.racha3 = (g2.concat(g3)).includes('racha3');
    // restauración honesta del localStorage del jugador
    try { if (raw === null) localStorage.removeItem('ppxr_stats_v1');
          else localStorage.setItem('ppxr_stats_v1', raw); } catch (e) {}
  }
  // — r61 · EL ÁRBITRO LEE EL FORMATO DE LA TABLA (CONFIG_TORNEOS) —
  try {
    const R = G.rules;
    const st0 = { p: R.scorePlayer, a: R.scoreAi, t: R.totalPoints,
      s: R.server, op: R.gameOpener, fs: R.firstServer };
    // normal 3-1 · total 4 → alterna cada saqueCada=2: floor(4/2)%2=0 → base
    R.scorePlayer = 3; R.scoreAi = 1; R.totalPoints = 4;
    R.gameOpener = null; R.firstServer = 'player';
    out.saqNormal = R.computeNextServer();
    // iguala 10-10 · total 21 → alterna CADA punto (saqueIguala=1):
    // floor(21/1)%2=1 → otro
    R.scorePlayer = 10; R.scoreAi = 10; R.totalPoints = 21;
    out.saqIguala = R.computeNextServer();
    R.scorePlayer = st0.p; R.scoreAi = st0.a; R.totalPoints = st0.t;
    R.server = st0.s; R.gameOpener = st0.op; R.firstServer = st0.fs;
  } catch (e) { out.arbErr = String(e); }
  // — r61 · el campeonato de PORTADA resuelve (índice eager → 'locura') —
  try { await dorme(400); out.portada = G.champs ? G.champs.portadaId : null; }
  catch (e) { out.portadaErr = String(e); }
  // — conservación r60 · la dificultad sigue viva desde su tabla —
  const ELO = window.__PP_ELO;
  out.eloHook = !!ELO;
  if (ELO) {
    out.cpuMedium = ELO.ELO_CPU.medium;
    out.hardVelo = ELO.AI_PRESETS.hard.maxSpeed;
  }
  // — conservación r58 · la puerta de la web sigue dibujada —
  try {
    G.menuOpen = true; G._instr = null; G.champIntro = null;
    G.tutV1 = false; G.calib = false; G.calibPala = false;
    G.inHall = false; G._arconoOn = false;
    G.menuPage = 'main';
    G.drawMenu();
    await dorme(200);
    out.tarjeta = (G.menuRects || []).some((r) => r && r.id === 'salirweb');
  } catch (e) { out.menuErr = String(e); }
  out.fin = true;
  return out;
}"""


async def main():
    # — FASE ESTÁTICA: lo que GitHub Pages SIRVE —
    gh = get(URL)
    # r61 · CONFIG_TORNEOS: la tabla de los torneos servida
    chk('const CONFIG_TORNEOS = {' in gh, 'CONFIG_TORNEOS servida (c02, única fuente)')
    chk('puntosGanar: 11,' in gh and 'ventajaMinima: 2,' in gh and
        'igualaEn: 10,' in gh, 'partido: a 11 con ventaja de 2 e iguala en 10 (dato)')
    chk('saqueCada: 2,' in gh and 'saqueIguala: 1,' in gh,
        'partido: cadencia del saque (cada 2 · cada punto en iguala)')
    chk('pausaPuntoS: 2.2,' in gh and 'pausaSupervivenciaS: 1.7,' in gh,
        'partido: pausas de punto como datos')
    chk('bestOfLibre: 3,' in gh and 'bestOfFabrica: 1,' in gh and
        'serieFactor: 2,' in gh, 'partido: best-of libre/fábrica + factor de serie')
    chk('caminos: { locura: 5, magia: 5, oeste: 5, estacion_orbital: 5, halloween: 5 },' in gh,
        'caminos: etapas de TU CAMINO como datos (antes CHAMP_STAGE_TOTAL)')
    chk("portada: 'locura'," in gh and "candados: ['estacion_orbital']," in gh,
        'portada + candados de campeonatos como datos')
    chk('niveles: [' in gh and 'x2Desde: 4' in gh and 'tresSinFallo: 3' in gh,
        'circuito: niveles/combo/estrellas del PRO TRAINING')
    # r61 · CONFIG_LOGROS: el catálogo servido
    chk('const CONFIG_LOGROS = {' in gh, 'CONFIG_LOGROS servida (c02, única fuente)')
    chk('const ACHIEVEMENTS = CONFIG_LOGROS.core.map' in gh,
        'ACHIEVEMENTS se DERIVA de la tabla (c06)')
    chk('COND_LOGRO(' in gh and len(re.findall(r"COND_LOGRO\('\w+'\)", gh)) == 5,
        '5 condiciones de GameStats leen la tabla (aces/maratón/superviv/racha/gigante)')
    chk("cond: { tipo: 'aces', valor: 10 }" in gh and
        "cond: { tipo: 'rallye', valor: 20 }" in gh and
        "cond: { tipo: 'mejorSupervivencia', valor: 25 }" in gh,
        'umbrales de los medallones como datos (10 · 20 · 25)')
    chk("cond: { tipo: 'rachaSesion', valor: 10 }" in gh and
        "cond: { tipo: 'puntosCircuito', valor: 1500 }" in gh and
        "cond: { tipo: 'medallasOro', cuenta: 5 }" in gh,
        'honores del PRO TRAINING como datos (r10 · leg 1500 · or5)')
    # r61 · lectores repartidos
    chk(gh.count('CONFIG_TORNEOS.partido.bestOfLibre;') == 7,
        'c12: el PARTIDO libre fija bestOf desde la tabla (×7)')
    chk('const CHAMP_STAGE_TOTAL = CONFIG_TORNEOS.caminos;' in gh,
        'c11: alias CHAMP_STAGE_TOTAL = dato')
    chk('static LOCKED = CONFIG_TORNEOS.candados;' in gh and
        'e ? e.id : CONFIG_TORNEOS.portada;' in gh,
        'c11: LOCKED y portadaId leen la tabla')
    chk('RALLY_BONUS.t5a[hi]' in gh and 'st.rally === 30 ? 15' not in gh,
        'c13: bonus del metrónomo DEDUPLICADO a la tabla RALLY_BONUS')
    chk('const ACHS = Object.keys(CONFIG_LOGROS.train)' in gh and
        'const LEVELS = CONFIG_TORNEOS.circuito.niveles;' in gh,
        'c13: ACHS y LEVELS derivan de las tablas')
    # CONSERVACIÓN r60/r59/r58/r55
    chk('const CONFIG_DIFICULTAD = {' in gh and
        len(re.findall(r'CONFIG_DIFICULTAD\.\w+', gh)) == 12,
        'conservación r60: CONFIG_DIFICULTAD íntegra (12 lectores)')
    chk('const CONFIG_AUDIO = {' in gh and
        len(re.findall(r'CONFIG_AUDIO\.\w+', gh)) == 44,
        'conservación r59: CONFIG_AUDIO íntegra (44 lectores)')
    chk('const CONFIG_MENU = {' in gh and len(re.findall(r'CONFIG_MENU\.salir', gh)) == 8,
        'conservación r58: CONFIG_MENU íntegra (8 lectores)')
    chk('const ARCANO_CFG = {' in gh and
        len(re.findall(r'if \(pwViva\(this\._\w+T\)\)', gh)) == 13,
        'conservación r55: ARCANO_CFG + pwViva íntegros')
    # sellos de versión en lo SERVIDO
    chk("const VERSION = '3.6.152-SDK6'" in gh, 'VERSION 3.6.152-SDK6 servida')
    sw = get(BASE + '/sw.js')
    chk("const CACHE = 'crazypp-v3.6.152-SDK6'" in sw, 'sw.js con CACHE 3.6.152')
    idx = get(BASE + '/')
    chk('v=3.6.152-SDK6' in idx, 'portada con cache-buster 3.6.152')

    # — FASE FUNCIONAL: el juego VIVO leyendo las tablas —
    async with async_playwright() as pw:
        try:
            browser = await pw.chromium.launch(args=[
                '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
                '--disable-dev-shm-usage'])
        except TypeError:
            browser = await pw.chromium.launch(args=['--use-gl=swiftshader',
                                                     '--disable-dev-shm-usage'])
        page = await browser.new_page()
        await page.goto(URL, wait_until='domcontentloaded', timeout=90000)
        try:
            await page.wait_for_function('window.__PP_GAME || window.__pingpong',
                                         timeout=60000)
        except Exception:
            pass
        await page.evaluate("""() => { try { localStorage.setItem('pp_player_name_v1', 'foro3d'); } catch (e) {} }""")
        res = await page.evaluate(JS)
        await browser.close()

    chk(res.get('presente'), 'el juego arranca en producción (__PP_GAME vivo)')
    if not res.get('presente'):
        print('  · sin juego vivo: los checks funcionales no corren')
        print(f'RESULTADO r61: {ok} OK · {fails} FALLOS')
        sys.exit(1 if fails else 0)

    chk(res.get('gsHook'), 'gancho __PP_GameStats vivo')
    chk(res.get('aces10') is True, 'VIVO: aces10 se desbloquea con el umbral de la tabla (10)')
    chk(res.get('maraton') is True, 'VIVO: maraton con rallye 20 de la tabla')
    chk(res.get('superviv') is True, 'VIVO: superviv con mejor histórica 25 de la tabla')
    chk(res.get('primera') is True, 'VIVO: primera victoria desbloquea')
    chk(res.get('gigante') is True, "VIVO: gigante con 'hard' de la tabla")
    chk(res.get('racha3') is True, 'VIVO: racha3 con umbral 3 de la tabla')
    chk(res.get('eloTrasWin') == 1012,
        'VIVO: ELO +12 tras ganar (K 24 · rival 1000 — dato DIFICULTAD.elo)')
    chk(res.get('saqNormal') == 'player', 'VIVO: saque normal alterna cada 2 (dato)')
    chk(res.get('saqIguala') == 'ai', 'VIVO: en iguala alterna CADA punto (dato)')
    chk(res.get('portada') == 'locura', "VIVO: portadaId resuelve 'locura' (índice eager)")
    chk(res.get('eloHook') is True and res.get('cpuMedium') == 1050 and
        res.get('hardVelo') == 3.8, 'conservación r60: ELO_CPU/AI_PRESETS vivos')
    chk(res.get('tarjeta') is True, 'conservación r58: tarjeta salirweb dibujada')

    print(f'RESULTADO r61: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
