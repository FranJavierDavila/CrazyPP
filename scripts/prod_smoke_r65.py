#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r65.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 159
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.156-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva el BLINDAJE DEL SAQUE r65
    (gatillo saque-primero · respaldo relativo a la cabeza · _srvManoValida
    fresca+plausible · watchdog bola→mano · ps.seenT en el bucle de mandos ·
    la misma armadura en _bolaGuard con el punto reglamentario de escritorio
    r25 intacto) y la conservación completa r55/r58/r59/r60/r61/r62/r63/r64,
    sw.js/portada a 3.6.156.
  · FUNCIONAL: el juego VIVO — _srvManoValida decide en vivo (mano activa y
    cerca de la cámara → true · mano lejana → false · pose vieja → false) y
    las tablas vivas de la cadena completa (pieles r62, logros r61, menú r58,
    dificultad r60, árbitro r61). Restauración honesta del localStorage.
Uso: python3 scripts/prod_smoke_r65.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.156-SDK6'

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
  // — r65 · EL BLINDAJE DEL SAQUE DECIDE EN VIVO (_srvManoValida) —
  try {
    const bhOk = { active: true, pos: G.camera.position.clone().add(
      new (G.camera.position.constructor)(0.12, -0.25, -0.30)) };
    out.manoCerca = G._srvManoValida(bhOk) === true;
    const bhLejos = { active: true,
      pos: G.camera.position.clone().add(
        new (G.camera.position.constructor)(0, 0, -3.5)) };
    out.manoLejos = G._srvManoValida(bhLejos) === false;
    const bhVieja = { active: true,
      pos: G.camera.position.clone().add(
        new (G.camera.position.constructor)(0.12, -0.25, -0.30)),
      seenT: performance.now() - 5000 };
    out.manoVieja = G._srvManoValida(bhVieja) === false;
    out.manoMuerta = G._srvManoValida({ active: false }) === false;
    out.sinMano = G._srvManoValida(null) === false;
  } catch (e) { out.srvErr = String(e); }
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
  // — r62 · LAS PIELES SIGUEN DATA-DRIVEN EN VIVO (conservación r63/r64) —
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
      // la TIENDA dibuja las pieles POR PUNTOS de la tabla
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
    # r65 · EL BLINDAJE DEL SAQUE servido (las 4 capas + frescura del bucle)
    chk('EL SAQUE ES EL DUEÑO DEL GATILLO' in gh,
        'r65 capa 1: gatillo SAQUE-PRIMERO servido')
    chk(gh.count('this.tossFromHand(this.ballHand, true);') == 2,
        'r65 capa 1: el saque lanza en la rama temprana Y en la del final (×2)')
    chk('r65 · RESPALDO EN LA MANO VIRTUAL DEL JUGADOR' in gh and
        'this.ball.pos.copy(this.camera.position).addScaledVector(fSrv, 0.35);' in gh,
        'r65 capa 2: respaldo relativo a la cabeza servido (pegado local)')
    chk('r65 · WATCHDOG DEL SAQUE' in gh and
        'LA BOLA SIEMPRE VUELVE A TU MANO' in gh and
        'this._srvWdT > 1.0' in gh,
        'r65 capa 4: watchdog bola→mano servido')
    chk('_srvManoValida(bh) {' in gh and
        'return bh.pos.distanceTo(this.camera.position) < 2.2;' in gh and
        'ps.seenT = performance.now();' in gh,
        'r65 capa 3: _srvManoValida (fresca+plausible) + ps.seenT servidos')
    chk('r65 · misma armadura que el pegado local' in gh and
        'this.ball.pos.copy(this.camera.position).addScaledVector(fBg, 0.35);' in gh,
        'r65: la misma armadura en el guardián online (_bolaGuard)')
    chk('this.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.4);' in gh,
        'conservación r25: el punto reglamentario de ESCRITORIO se queda')
    chk('this.ball.pos.set(0.3, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4)' not in gh,
        'r65 negativa: el punto fijo viejo desapareció del pegado local')
    # r64 · CONFIG_MEDALLAS sigue servida y enchufada
    chk('const CONFIG_MEDALLAS = {' in gh and
        'estrellas: { bronce: 1, plata: 2, oro: 3 },' in gh and
        'precision: { plata: 70, oro: 85 },' in gh,
        'conservación r64: CONFIG_MEDALLAS servida (escalera 1/2/3 · 70/85)')
    chk('const MDE = CONFIG_MEDALLAS.estrellas, MDP = CONFIG_MEDALLAS.precision;' in gh,
        'conservación r64: lector MDE/MDP de c13 servido')
    # r63 · CONFIG_RALLY: la tabla del rally servida
    chk('const CONFIG_RALLY = {' in gh,
        'conservación r63: CONFIG_RALLY servida (c02, única fuente)')
    chk('metas: { t5a: [30, 50, 100], t5b: [20, 40, 80] },' in gh,
        'conservación r63: metas del rally servidas (t5a 30/50/100 · t5b 20/40/80)')
    chk('const RALLY_MILL = CONFIG_RALLY.metas;' in gh and
        'const RALLY_BONUS = CONFIG_RALLY.bonos;' in gh,
        'conservación r63: los dos alias leen de CONFIG_RALLY')
    # CONSERVACIÓN r62 · pieles siguen servidas y enchufadas
    chk('const CONFIG_PIELES = {' in gh and
        'const SKINS = CONFIG_PIELES.pieles;' in gh,
        'conservación r62: CONFIG_PIELES + lector SKINS servidos')
    # CONSERVACIÓN r61 · torneos + logros siguen servidos y enchufados
    chk('const CONFIG_TORNEOS = {' in gh and
        'puntosGanar: 11,' in gh and 'ventajaMinima: 2,' in gh,
        'conservación r61: CONFIG_TORNEOS íntegra (a 11/ventaja)')
    chk('const CONFIG_LOGROS = {' in gh and
        'const ACHIEVEMENTS = CONFIG_LOGROS.core.map' in gh,
        'conservación r61: CONFIG_LOGROS + ACHIEVEMENTS derivado')
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
    chk("const VERSION = '3.6.156-SDK6'" in gh, 'VERSION 3.6.156-SDK6 servida')
    sw = get(BASE + '/sw.js')
    chk("const CACHE = 'crazypp-v3.6.156-SDK6'" in sw, 'sw.js con CACHE 3.6.156')
    idx = get(BASE + '/')
    chk('v=3.6.156-SDK6' in idx, 'portada con cache-buster 3.6.156')

    # — FASE FUNCIONAL: el juego VIVO leyendo las tablas + la armadura —
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
        print(f'RESULTADO r65: {ok} OK · {fails} FALLOS')
        sys.exit(1 if fails else 0)

    # r65 · la armadura DECIDE en vivo
    chk(res.get('manoCerca') is True,
        'r65: mano activa y cerca de la cabeza → VÁLIDA (bola en la mano)')
    chk(res.get('manoLejos') is True,
        'r65: mano a 3,5 m de la cabeza → INVÁLIDA (respaldo de cabeza)')
    chk(res.get('manoVieja') is True,
        'r65: pose sellada hace 5 s → INVÁLIDA (frescura 400 ms)')
    chk(res.get('manoMuerta') is True and res.get('sinMano') is True,
        'r65: mando inactivo o ausente → INVÁLIDO (sin falsos positivos)')
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

    print(f'RESULTADO r65: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
