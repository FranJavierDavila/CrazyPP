#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r62.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 156
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.153-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_PIELES (las 9 pieles de
    pala fila a fila — clasica 0 · fuego 150 · hielo 400 · oro 800 ·
    arcoiris 1500 anim · carbon 2500 + GLB · neon/fantasma/campeon por
    racha de días 7/14/30 con min:Infinity ×3) con su lector real
    (c13: SKINS = CONFIG_PIELES.pieles · RACHA_SKINS por filtro · tienda
    que oculta las de asistencia · 4 bucles de pieles · 4 lecturas de
    nombre), más la conservación completa r55/r58/r59/r60/r61 y
    sw.js/portada a 3.6.153.
  · FUNCIONAL: el juego VIVO lee la tabla — applySkin equipa 'arcoiris'
    DESDE CONFIG_PIELES (state.skin), la tienda dibuja las 6 pieles por
    puntos de la tabla, la cadena c02→c13→c04→c12 equipa 'carbon' vía
    __PP_SET_PADDLE_SKIN (perk de la tabla PADDLE_PERKS), y la
    conservación r61 sigue viva (6 medallones con umbrales de
    CONFIG_LOGROS · ELO +12 · árbitro con cadencia de CONFIG_TORNEOS ·
    portadaId 'locura'). Restauración honesta del localStorage.
Uso: python3 scripts/prod_smoke_r62.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.153-SDK6'

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
  // — r62 · LAS PIELES SON DATA-DRIVEN EN VIVO —
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
    # r62 · CONFIG_PIELES: la tabla de las pieles servida
    chk('const CONFIG_PIELES = {' in gh, 'CONFIG_PIELES servida (c02, única fuente)')
    chk("{ id: 'clasica', name: { es: 'Clásica', en: 'Classic' }, min: 0, grip: 0x6b4a2f }," in gh
        and "{ id: 'fuego', name: { es: 'Fuego', en: 'Fire' }, min: 150, tex: 'fuego', edge: 0xff5a2a, grip: 0xc22a12 }," in gh
        and "{ id: 'hielo', name: { es: 'Hielo', en: 'Ice' }, min: 400, tex: 'hielo', edge: 0x35c4e8, grip: 0x1479a3 }," in gh,
        'pieles por puntos servidas (clasica 0 · fuego 150 · hielo 400)')
    chk("{ id: 'oro', name: { es: 'Oro', en: 'Gold' }, min: 800, tex: 'oro', edge: 0xf2c14e, grip: 0x3a2c10 }," in gh
        and "{ id: 'arcoiris', name: { es: 'Arcoíris', en: 'Rainbow' }, min: 1500, tex: 'holo', edge: 0xb07aff, grip: 0x8e44ad, anim: true }," in gh
        and "{ id: 'carbon', name: { es: 'Pro Carbon', en: 'Pro Carbon' }, min: 2500, tex: 'carbon', edge: 0xff2d2d, grip: 0x17181c, modelUrl: 'assets/pala/pala_pro.glb' }," in gh,
        'pieles premium servidas (oro 800 · arcoiris 1500 anim · carbon 2500 + GLB)')
    chk("{ id: 'neon', name: { es: 'Neón', en: 'Neon' }, min: Infinity, days: 7, via: 'racha', tex: 'neon', edge: 0x39ff88, grip: 0x0f3d2e }," in gh
        and "{ id: 'fantasma', name: { es: 'Fantasma', en: 'Ghost' }, min: Infinity, days: 14, via: 'racha', tex: 'fantasma', edge: 0xbfe9ff, grip: 0x43545e }," in gh
        and "{ id: 'campeon', name: { es: 'Campeón', en: 'Champion' }, min: Infinity, days: 30, via: 'racha', tex: 'oro', edge: 0xffd700, grip: 0x4a3808, anim: true }," in gh
        and gh.count('min: Infinity') == 3,
        'asistencia por racha servida (neon 7 · fantasma 14 · campeon 30 · Infinity ×3)')
    chk('const SKINS = CONFIG_PIELES.pieles;' in gh,
        'c13: SKINS = CONFIG_PIELES.pieles (lector único)')
    chk("SKINS.filter((s) => s.via === 'racha')" in gh,
        'c13: RACHA_SKINS deriva por filtro (dato)')
    chk("if (sk.via === 'racha') continue;" in gh,
        'c13: la tienda oculta las de asistencia (dato)')
    chk(gh.count('for (const sk of SKINS) {') == 2 and
        gh.count('for (const sk of RACHA_SKINS) {') == 2,
        'c13: los 4 bucles de pieles intactos (2+2)')
    chk(gh.count('sk.name[LANG] || sk.name.es') == 4,
        'c13: avisos y tarjetas leen el nombre de la tabla (×4)')
    # CONSERVACIÓN r61 · torneos + logros siguen servidos y enchufados
    chk('const CONFIG_TORNEOS = {' in gh and
        'puntosGanar: 11,' in gh and 'ventajaMinima: 2,' in gh and
        'igualaEn: 10,' in gh, 'conservación r61: CONFIG_TORNEOS íntegra (a 11/ventaja/iguala)')
    chk('saqueCada: 2,' in gh and 'saqueIguala: 1,' in gh and
        'bestOfLibre: 3,' in gh and 'serieFactor: 2,' in gh,
        'conservación r61: cadencia/best-of/serie como datos')
    chk('caminos: { locura: 5, magia: 5, oeste: 5, estacion_orbital: 5, halloween: 5 },' in gh
        and "portada: 'locura'," in gh and "candados: ['estacion_orbital']," in gh,
        'conservación r61: caminos/portada/candados/circuito como datos')
    chk('const CONFIG_LOGROS = {' in gh and
        'const ACHIEVEMENTS = CONFIG_LOGROS.core.map' in gh and
        len(re.findall(r"COND_LOGRO\('\w+'\)", gh)) == 5,
        'conservación r61: CONFIG_LOGROS + ACHIEVEMENTS derivado + 5 condiciones')
    chk("cond: { tipo: 'aces', valor: 10 }" in gh and
        "cond: { tipo: 'medallasOro', cuenta: 5 }" in gh,
        'conservación r61: umbrales de logros como datos (10 · or5)')
    chk(gh.count('CONFIG_TORNEOS.partido.bestOfLibre;') == 7 and
        'const CHAMP_STAGE_TOTAL = CONFIG_TORNEOS.caminos;' in gh and
        'static LOCKED = CONFIG_TORNEOS.candados;' in gh,
        'conservación r61: lectores c12/c11 intactos (bestOf ×7 · caminos · LOCKED)')
    chk('const ACHS = Object.keys(CONFIG_LOGROS.train)' in gh and
        'const LEVELS = CONFIG_TORNEOS.circuito.niveles;' in gh and
        'RALLY_BONUS.t5a[hi]' in gh,
        'conservación r61: ACHS/LEVELS/RALLY_BONUS de las tablas')
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
    chk("const VERSION = '3.6.153-SDK6'" in gh, 'VERSION 3.6.153-SDK6 servida')
    sw = get(BASE + '/sw.js')
    chk("const CACHE = 'crazypp-v3.6.153-SDK6'" in sw, 'sw.js con CACHE 3.6.153')
    idx = get(BASE + '/')
    chk('v=3.6.153-SDK6' in idx, 'portada con cache-buster 3.6.153')

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
        print(f'RESULTADO r62: {ok} OK · {fails} FALLOS')
        sys.exit(1 if fails else 0)

    chk(res.get('trnHook') is True, 'gancho __PP_TRAIN vivo (c13)')
    chk(res.get('skin0') == 'clasica' and res.get('unlocked0') is True,
        'VIVO: estado de pieles intacto (skin clasica · desbloqueo base)')
    chk(res.get('skinEquip') == 'arcoiris',
        'VIVO: applySkin equipa DESDE CONFIG_PIELES (skin:arcoiris)')
    chk(res.get('tiendaSeis') == 6,
        'VIVO: la tienda dibuja las 6 pieles por puntos de la tabla')
    chk(res.get('perkSkin') == 'carbon',
        'VIVO: cadena c02→c13→c04→c12 equipa carbon (perk vivo)')
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

    print(f'RESULTADO r62: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
