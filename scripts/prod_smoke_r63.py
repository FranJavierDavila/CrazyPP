#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r63.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 157
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.154-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_RALLY (metas 30/50/100 t5a ·
    20/40/80 t5b y bonos 15/25/50 por modo) con sus lectores reales
    (c13: RALLY_MILL = CONFIG_RALLY.metas · RALLY_BONUS = CONFIG_RALLY.bonos
    · DEDUP de MODES: las filas t5a/t5b leen meta1/bonus1 de la tabla), los
    4 lectores rally pre-existentes conservados y la conservación completa
    r55/r58/r59/r60/r61/r62, sw.js/portada a 3.6.154.
  · FUNCIONAL: el juego VIVO con las tablas vivas de la cadena completa —
    pieles r62 (applySkin desde CONFIG_PIELES · tienda · perk carbon), logros
    r61 (6 medallones con umbrales de tabla · ELO +12 · árbitro CONFIG_TORNEOS
    · portadaId), menú r58. Restauración honesta del localStorage.
Uso: python3 scripts/prod_smoke_r63.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.154-SDK6'

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
  // — r61 · LOS LOGROS SIGUEN DATA-DRIVEN: GameStats desbloquea DESDE LA TABLA —
  const GS = window.__PP_GameStats;
  out.gsHook = typeof GS === 'function';
  if (GS) {
    const raw = localStorage.getItem('ppxr_stats_v1');
    const gs = new GS();          // instancia limpia para la prueba
    gs.data.ach = {};             // catálogo a cero SÓLO en la instancia de prueba
    gs.data.won = 0; gs.data.lost = 0; gs.data.streak = 0;
    gs.data.elo = 1000;           // ancla de la prueba (inicial del contrato r60)
    gs.data.hoyDia = { dia: '', v: 0 };
    let got = [];
    for (let i = 0; i < 10; i++) got = got.concat(gs.recordPoint('player', 1));
    out.aces10 = got.includes('aces10');
    out.maraton = gs.recordRally(20).includes('maraton');
    out.superviv = gs.recordSurvivalRally(1, 25).includes('superviv');
    const g1 = gs.recordMatch(true, 'hard');
    out.primera = g1.includes('primera');
    out.gigante = g1.includes('gigante');
    out.eloTrasWin = gs.data.elo;          // 1012 = dato DIFICULTAD.elo vivo
    const g2 = gs.recordMatch(true, 'easy');
    const g3 = gs.recordMatch(true, 'easy');
    out.racha3 = (g2.concat(g3)).includes('racha3');
    try { if (raw === null) localStorage.removeItem('ppxr_stats_v1');
          else localStorage.setItem('ppxr_stats_v1', raw); } catch (e) {}
  }
  // — r61 · EL ÁRBITRO LEE EL FORMATO DE LA TABLA (CONFIG_TORNEOS) —
  try {
    const R = G.rules;
    const st0 = { p: R.scorePlayer, a: R.scoreAi, t: R.totalPoints,
      s: R.server, op: R.gameOpener, fs: R.firstServer };
    R.scorePlayer = 3; R.scoreAi = 1; R.totalPoints = 4;
    R.gameOpener = null; R.firstServer = 'player';
    out.saqNormal = R.computeNextServer();
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
  // — r62 · LAS PIELES SIGUEN DATA-DRIVEN EN VIVO (conservación r63) —
  try {
    const rawTr = localStorage.getItem('ppxr_train_v1');
    const TR = window.__PP_TRAIN;
    out.trnHook = !!TR;
    if (TR) {
      const st0 = TR.state;
      out.skin0 = st0.skin;
      out.unlocked0 = Array.isArray(st0.unlocked) &&
        st0.unlocked.indexOf('clasica') >= 0;
      // equipar DESDE la tabla: applySkin busca en SKINS = CONFIG_PIELES.pieles
      TR.menuAction(G, 'skin:arcoiris');
      out.skinEquip = TR.state.skin;   // 'arcoiris' = la tabla está VIVA
      // la TIENDA dibuja las pieles POR PUNTOS de la tabla (la fila de
      // asistencia comparte prefijo y puede sumarse según trainGamify)
      G.menuPage = 'train'; G._instr = null; G.champIntro = null;
      G.tutV1 = false; G.calib = false; G.calibPala = false;
      G.inHall = false; G._arconoOn = false;
      G.drawMenu();
      await dorme(200);
      const ids = (G.menuRects || []).map((r) => r && r.id).filter(Boolean)
        .filter((i) => String(i).indexOf('trv3:skin:') === 0);
      const PORPUNTOS = ['clasica', 'fuego', 'hielo', 'oro', 'arcoiris', 'carbon'];
      out.tiendaSeis = PORPUNTOS.filter((p) =>
        ids.indexOf('trv3:skin:' + p) >= 0).length;   // 6 = tabla viva pintada
      // CADENA completa c02→c13→c04→c12 con un id de la tabla
      const PP = window.__PP_PADDLE_PERKS;
      window.__PP_SET_PADDLE_SKIN('carbon');
      out.perkSkin = (PP && PP.carbon) ? window.__PP_PADDLE_SKIN : null;
      // restauración honesta: skin y save del jugador
      TR.menuAction(G, 'skin:clasica');
      try { if (rawTr === null) localStorage.removeItem('ppxr_train_v1');
            else localStorage.setItem('ppxr_train_v1', rawTr); } catch (e) {}
    }
  } catch (e) { out.pielesErr = String(e); }
  out.fin = true;
  return out;
}"""


async def main():
    # — FASE ESTÁTICA: lo que GitHub Pages SIRVE —
    gh = get(URL)
    # r63 · CONFIG_RALLY: la tabla del rally servida
    chk('const CONFIG_RALLY = {' in gh, 'CONFIG_RALLY servida (c02, única fuente)')
    chk('metas: { t5a: [30, 50, 100], t5b: [20, 40, 80] },' in gh,
        'metas del rally servidas (t5a 30/50/100 · t5b 20/40/80)')
    chk('bonos: { t5a: [15, 25, 50], t5b: [15, 25, 50] },' in gh,
        'bonos del rally servidos (15/25/50 los dos modos)')
    chk('const RALLY_MILL = CONFIG_RALLY.metas;' in gh and
        'const RALLY_BONUS = CONFIG_RALLY.bonos;' in gh,
        'c13: los dos alias leen de CONFIG_RALLY (lector único)')
    chk("t5a: { area: 'rit', nk: 'm_t5a', dk: 'm_t5a_d', n: RALLY_MILL.t5a[0], ok: 'ok_beat', pts: 1, bonus: RALLY_BONUS.t5a[0] }," in gh
        and "t5b: { area: 'rit', nk: 'm_t5b', dk: 'm_t5b_d', n: RALLY_MILL.t5b[0], ok: 'ok_beat', pts: 1, bonus: RALLY_BONUS.t5b[0] }," in gh,
        'c13: DEDUP de MODES servido (t5a/t5b leen meta1/bonus1 de la tabla)')
    chk('RALLY_MILL.t5a.includes(st.rally)' in gh and
        'const MI = RALLY_MILL[id];' in gh and
        'const MI = RALLY_MILL[active], MO = RALLY_BONUS[active];' in gh and
        'RALLY_BONUS.t5a[hi]' in gh,
        'c13: los 4 lectores rally pre-existentes intactos (okHit/medallaDe/juez/dedup)')
    chk(len(re.findall(r'RALLY_MILL\.\w+', gh)) == 5 and
        len(re.findall(r'RALLY_BONUS\.\w+', gh)) == 3 and
        len(re.findall(r'CONFIG_RALLY\.\w+', gh)) == 4,
        'c02/c13: lectores del rally vivos (5+3+4 — medido r63)')
    # CONSERVACIÓN r62 · pieles siguen servidas y enchufadas
    chk('const CONFIG_PIELES = {' in gh and
        "{ id: 'clasica', name: { es: 'Clásica', en: 'Classic' }, min: 0, grip: 0x6b4a2f }," in gh
        and "{ id: 'carbon', name: { es: 'Pro Carbon', en: 'Pro Carbon' }, min: 2500, tex: 'carbon', edge: 0xff2d2d, grip: 0x17181c, modelUrl: 'assets/pala/pala_pro.glb' }," in gh,
        'conservación r62: CONFIG_PIELES servida (clasica 0 · carbon 2500 + GLB)')
    chk('const SKINS = CONFIG_PIELES.pieles;' in gh and
        gh.count('min: Infinity') == 3 and
        "SKINS.filter((s) => s.via === 'racha')" in gh,
        'conservación r62: lector SKINS + asistencia racha ×3 (dato)')
    # CONSERVACIÓN r61 · torneos + logros siguen servidos y enchufados
    chk('const CONFIG_TORNEOS = {' in gh and
        'puntosGanar: 11,' in gh and 'ventajaMinima: 2,' in gh and
        'igualaEn: 10,' in gh, 'conservación r61: CONFIG_TORNEOS íntegra (a 11/ventaja/iguala)')
    chk('caminos: { locura: 5, magia: 5, oeste: 5, estacion_orbital: 5, halloween: 5 },' in gh
        and "portada: 'locura'," in gh and "candados: ['estacion_orbital']," in gh,
        'conservación r61: caminos/portada/candados como datos')
    chk('const CONFIG_LOGROS = {' in gh and
        'const ACHIEVEMENTS = CONFIG_LOGROS.core.map' in gh and
        len(re.findall(r"COND_LOGRO\('\w+'\)", gh)) == 5,
        'conservación r61: CONFIG_LOGROS + ACHIEVEMENTS derivado + 5 condiciones')
    chk(gh.count('CONFIG_TORNEOS.partido.bestOfLibre;') == 7 and
        'const CHAMP_STAGE_TOTAL = CONFIG_TORNEOS.caminos;' in gh and
        'static LOCKED = CONFIG_TORNEOS.candados;' in gh,
        'conservación r61: lectores c12/c11 intactos (bestOf ×7 · caminos · LOCKED)')
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
    chk("const VERSION = '3.6.154-SDK6'" in gh, 'VERSION 3.6.154-SDK6 servida')
    sw = get(BASE + '/sw.js')
    chk("const CACHE = 'crazypp-v3.6.154-SDK6'" in sw, 'sw.js con CACHE 3.6.154')
    idx = get(BASE + '/')
    chk('v=3.6.154-SDK6' in idx, 'portada con cache-buster 3.6.154')

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
        print(f'RESULTADO r63: {ok} OK · {fails} FALLOS')
        sys.exit(1 if fails else 0)

    chk(res.get('trnHook') is True, 'gancho __PP_TRAIN vivo (c13)')
    chk(res.get('skin0') == 'clasica' and res.get('unlocked0') is True,
        'conservación r62: estado de pieles intacto (skin clasica · base)')
    chk(res.get('skinEquip') == 'arcoiris',
        'conservación r62: applySkin equipa DESDE CONFIG_PIELES (arcoiris)')
    chk(res.get('tiendaSeis') == 6,
        'conservación r62: la tienda dibuja las 6 pieles por puntos de la tabla')
    chk(res.get('perkSkin') == 'carbon',
        'conservación r62: cadena c02→c13→c04→c12 equipa carbon (perk vivo)')
    # conservación r61 viva
    chk(res.get('gsHook'), 'conservación r61: gancho __PP_GameStats vivo')
    chk(res.get('aces10') is True, 'conservación r61: aces10 con el umbral de la tabla (10)')
    chk(res.get('maraton') is True, 'conservación r61: maraton con rallye 20 de la tabla')
    chk(res.get('superviv') is True, 'conservación r61: superviv con mejor histórica 25')
    chk(res.get('primera') is True, 'conservación r61: primera victoria desbloquea')
    chk(res.get('gigante') is True, "conservación r61: gigante con 'hard' de la tabla")
    chk(res.get('racha3') is True, 'conservación r61: racha3 con umbral 3 de la tabla')
    chk(res.get('eloTrasWin') == 1012,
        'conservación r60: ELO +12 tras ganar (K 24 · rival 1000 — dato DIFICULTAD.elo)')
    chk(res.get('saqNormal') == 'player', 'conservación r61: saque normal alterna cada 2 (dato)')
    chk(res.get('saqIguala') == 'ai', 'conservación r61: en iguala alterna CADA punto (dato)')
    chk(res.get('portada') == 'locura', "conservación r61: portadaId resuelve 'locura' (índice eager)")
    chk(res.get('eloHook') is True and res.get('cpuMedium') == 1050 and
        res.get('hardVelo') == 3.8, 'conservación r60: ELO_CPU/AI_PRESETS vivos')
    chk(res.get('tarjeta') is True, 'conservación r58: tarjeta salirweb dibujada')

    print(f'RESULTADO r63: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
