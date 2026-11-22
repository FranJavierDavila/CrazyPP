#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r60.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 154
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.151-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_DIFICULTAD (presets/saque/
    escala/elo/adaptativo/supervivencia/esfuerzo) con sus 12 lectores
    (c02 scalePreset+rivalPorElo · c06 ELO+esfuerzo · c12 adaptativo+
    supervivencia+rango k) y los ALIAS del contrato, más la conservación
    completa r55/r56/r57/r58/r59 y sw.js/portada a 3.6.151.
  · FUNCIONAL: el juego VIVO calcula la dificultad DESDE LA TABLA —
    __PP_ELO (alias) · bandas del matchmaking · k adaptativo 4-0 = 1,22 ·
    rampa de supervivencia (1,8 y techo 2,1) · el grafo de audio r59 ·
    el HUB dibuja 'salirweb' (r58) y la puerta resuelve AUTO_ORIGIN; en
    un campeonato simulado el IMÁN nace/sobrevive, un poder CONVIVE y la
    MEGA nace a los 15,00 s de ARCANO_CFG (el dato manda).
Uso: python3 scripts/prod_smoke_r60.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.151-SDK6'

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
  // — r60 · LA DIFICULTAD ES DATA-DRIVEN: el dato manda VIVO —
  const ELO = window.__PP_ELO;
  out.eloHook = !!ELO;
  if (ELO) {
    out.cpuMedium = ELO.ELO_CPU.medium;
    out.hardVelo = ELO.AI_PRESETS.hard.maxSpeed;
    out.easyMiss = ELO.AI_PRESETS.easy.missBase;
    const r1 = ELO.rivalPorElo(1000, 0);
    out.mm1 = [r1.preset, +r1.k.toFixed(4), r1.elo];
    const r2 = ELO.rivalPorElo(950, 0);
    out.mm2 = [r2.preset, r2.elo];
    const r3 = ELO.rivalPorElo(1200, 0);
    out.mm3 = [r3.preset, r3.elo];
    const r4 = ELO.rivalPorElo(2000, 120);
    out.mm4 = [+r4.k.toFixed(4), r4.elo];
  }
  try {
    G._estiloActivo = function () { return null; };   // QA: aísla el canal de estilos
    const adapt0 = !!G.adaptive;
    const mode0 = G.mode;
    G.adaptive = true;
    G.rules.scorePlayer = 4; G.rules.scoreAi = 0;
    G.applyAISkill();
    out.adaptK = +G._aiKTarget.toFixed(4);
    G.adaptive = false;
    G.mode = 'survival';
    G.survivalRallies = 10;
    G.applyAISkill();
    out.svK10 = +G._aiKTarget.toFixed(4);
    G.survivalRallies = 50;
    G.applyAISkill();
    out.svK50 = +G._aiKTarget.toFixed(4);
    // restauración honesta del estado del jugador
    G.survivalRallies = 0;
    G.mode = mode0;
    G.adaptive = adapt0;
    G.rules.scorePlayer = 0; G.rules.scoreAi = 0;
    G.applyAISkill();
  } catch (e) { out.adaptErr = String(e); }
  // — r59 · el grafo de audio construido DESDE LA TABLA (conservación) —
  try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) {}
  G.palaMejorada = true;
  const A = G.audio;
  out.audioVivo = !!A;
  if (A) {
    try { A.hadGesture = true; A.kick(); } catch (e) { out.kickErr = String(e); }
    await dorme(300);
    out.master = (A.master && A.master.gain) ? +A.master.gain.value : null;
    out.musicaFab = A.musicVol;
    out.fxFab = A.fxVol;
    out.locutorFab = A.arcVol;
  }
  // — r58 · el menú vivo dibuja la tarjeta de salida (conservación) —
  G.menuOpen = true; G._instr = null; G.champIntro = null;
  G.tutV1 = false; G.calib = false; G.calibPala = false;
  G.inHall = false; G._arconoOn = false;
  G.menuPage = 'main';
  try { G.drawMenu(); } catch (e) {}
  await dorme(200);
  out.tarjeta = (G.menuRects || []).some((r) => r && r.id === 'salirweb');
  out.fnPuerta = typeof G.salirALaWeb === 'function';
  // — herencia r54/r57: el campeonato simulado y el dato que manda —
  G.renderer.xr.isPresenting = true;
  G.menuOpen = false;
  try { G.rules.onMatchStart = null; } catch (e) {}
  G.champs = { active: true, gunArmed: false, paddleGunArmed: false };
  G.rules.state = 'rally';
  G.rules.rallyHits = 0;
  G._megaMatriz = [{ id: 'iman', n: 1 }]; G._megaIdx = 0;
  G._imanT = 0; G._efectoT = 0;
  const iLibre = (G.paddleHand === 0) ? 1 : 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.nace = +G._imanT.toFixed(2);
  out.msg = String(G.rules.message || '');
  await dorme(1000);
  out.sigue = +G._imanT.toFixed(2);
  G._megaMatriz = [{ id: 'efecto', n: 1 }, { id: 'iman', n: 0 }];
  G._megaIdx = 0;
  G._efectoT = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.efectoNace = +G._efectoT.toFixed(2);
  out.imanAun = +G._imanT.toFixed(2);
  G._megaMatriz = [{ id: 'mega', n: 1 }, { id: 'efecto', n: 0 },
                   { id: 'iman', n: 0 }];
  G._megaIdx = 0;
  G._megaT = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.megaNace = +G._megaT.toFixed(2);
  out.fin = true;
  return out;
}"""


async def main():
    # — FASE ESTÁTICA: lo que GitHub Pages SIRVE —
    gh = get(URL)
    # r60 · CONFIG_DIFICULTAD: la tabla de la dificultad servida
    chk('const CONFIG_DIFICULTAD = {' in gh, 'CONFIG_DIFICULTAD servida (c02, única fuente)')
    chk('easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.15, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },' in gh and
        'medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.05,  missBase: 0.08, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },' in gh and
        'hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.024, missBase: 0.03, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },' in gh,
        'presets: las 3 curvas de la CPU como DATOS')
    chk('easy:   { reach: 0.060, vy: 3.5,  angleMul: 1.4,  assistMul: 1.35 },' in gh and
        'hard:   { reach: 0.028, vy: 2.70, angleMul: 0.7,  assistMul: 0.6  },' in gh,
        'saque: asistencia por dificultad como DATOS')
    chk('kMin: 0.7, kMax: 2.2,        // rango legal del factor k (invariante del arnés)' in gh,
        'escala: topes/exponentes de scalePreset como DATOS')
    chk('cpu: { easy: 900, medium: 1050, hard: 1200 },' in gh and
        'kModo: { ia: 24, carrera: 20, p2p: 32 },' in gh and
        'bandaEasyHasta: 975, bandaMediumHasta: 1125,' in gh,
        'elo: anclas CPU · K por modo · bandas del matchmaking')
    chk('adaptativo: { pasoSube: 0.055, pasoBaja: 0.05, topeDif: 6 },' in gh and
        'supervivencia: { porRallye: 0.08, techo: 2.1 },' in gh,
        'adaptativo + supervivencia como DATOS')
    chk('baseFrac: 0.25,' in gh and 'tope: 0.85,' in gh and 'cooldownS: 0.55,' in gh,
        'esfuerzo: la fórmula r113 como DATOS')
    chk('const AI_PRESETS = CONFIG_DIFICULTAD.presets;' in gh and
        'const SERVE_ASSIST_TIERS = CONFIG_DIFICULTAD.saque;   // r60: dato' in gh and
        'const ELO_CPU = CONFIG_DIFICULTAD.elo.cpu;   // r60: dato' in gh,
        'ALIAS del contrato (AI_PRESETS/SERVE_ASSIST_TIERS/ELO_CPU)')
    chk('const E = CONFIG_DIFICULTAD.escala;   // r60: topes y exponentes como datos' in gh and
        'const M = CONFIG_DIFICULTAD.elo;   // r60: bandas, jitter y paso como datos' in gh,
        'c02 lee la tabla (scalePreset + rivalPorElo)')
    chk('const EF = CONFIG_DIFICULTAD.esfuerzo;   // r60: la fórmula del fallo vive en datos' in gh and
        'this.cfg.missBase * EF.baseFrac +' in gh and
        'elo: CONFIG_DIFICULTAD.elo.inicial,   // r60: dato (fábrica del número)' in gh,
        'c06 lee la tabla (esfuerzo + ELO)')
    chk('const AD = CONFIG_DIFICULTAD.adaptativo;   // r60: el paso vive en datos' in gh and
        'const SV = CONFIG_DIFICULTAD.supervivencia;   // r60: la rampa vive en datos' in gh and
        'const ES = CONFIG_DIFICULTAD.escala;   // r60: rango legal de la tabla' in gh,
        'c12 lee la tabla (adaptativo + supervivencia + rango k)')
    n_cd = len(re.findall(r'CONFIG_DIFICULTAD\.\w+', gh))
    chk(n_cd == 12, f'12 lectores enchufados (servidos: {n_cd})')
    # CONSERVACIÓN r59 · CONFIG_AUDIO (la mezcla data-driven intacta)
    chk('const CONFIG_AUDIO = {' in gh and
        'canales: { musica: 1, efectos: 1, locutor: 0.18 },' in gh and
        'pala:  { nivel: 0.72, piso: 0.15, tonoMin: 0.84, tonoMax: 1.34 },' in gh,
        'CONFIG_AUDIO servida (conservación r59)')
    chk('this.master.gain.value = CONFIG_AUDIO.buses.master;' in gh and
        '_applyArcGain(ms = CONFIG_AUDIO.bso.reajusteMs)' in gh,
        'c03 lee la tabla de audio (conservación r59)')
    # CONSERVACIÓN r58 · CONFIG_MENU (el menú data-driven intacto)
    chk('const CONFIG_MENU = {' in gh and "id: 'salirweb'," in gh and
        "urlDestino: 'AUTO_ORIGIN'," in gh and 'async salirALaWeb() {' in gh,
        'CONFIG_MENU + la puerta de salida (conservación r58)')
    chk("hub_salirweb: 'SALIR A LA WEB'," in gh and
        "hub_salirweb: 'EXIT TO WEB'," in gh,
        'i18n del menú (conservación r58)')
    # CONSERVACIÓN r57/r56/r55
    chk('const PASO_TUNE = { uiMax: 1 / 30, fisMax: 1 / 12 };' in gh and
        'updatePaddleSim(ps, grip.position, tmpMountQ, now, dtFis);' in gh,
        'PASO_TUNE + pala con dtFis (conservación r57)')
    chk(gh.count('DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 &&') == 3,
        'R2 margen de bote alineado (conservación r57)')
    chk('const ARCANO_CFG = {' in gh and
        'const pwViva = (t) => (on || dlV) && t > 0;' in gh and
        gh.count('dur: ARCANO_CFG.ventanas.') == 14,
        'ARCANO_CFG + pwViva + dur ×14 (conservación r55)')
    n_pw = len(re.findall(r'if \(pwViva\(this\._\w+T\)\)', gh))
    chk(n_pw == 13, f'13 compuertas LEEN pwViva (servidas: {n_pw})')
    chk('const BOTE_TUNE = {' in gh and 'const BOLA_TUNE = { spinGanancia: 0.45 };' in gh,
        'BOTE_TUNE + BOLA_TUNE (conservación r56)')
    sw = get(BASE + '/sw.js')
    chk('crazypp-v3.6.151-SDK6' in sw, 'sw.js CACHE crazypp-v3.6.151-SDK6')
    portada = get(BASE + '/')
    chk('v=3.6.151-SDK6' in portada, 'portada con cache-buster v=3.6.151-SDK6')

    # — FASE FUNCIONAL: el juego VIVO en producción —
    errs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL, wait_until='domcontentloaded', timeout=60000)
        await pg.wait_for_function(
            '() => window.__PP_GAME && window.__PP_VERSION', timeout=60000)
        ver = await pg.evaluate('window.__PP_VERSION || ""')
        badge = (await pg.locator('#verBadge').count() and
                 await pg.inner_text('#verBadge')) or ''
        chk(ver == '3.6.151-SDK6', f'__PP_VERSION = {ver!r}')
        chk('V3.6.151-SDK6' in badge, f'badge 2D = {badge!r}')
        out = await pg.evaluate(JS)
        # — r58 · LA PUERTA en una página DESECHABLE (navega de verdad) —
        pg2 = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg2.goto(URL, wait_until='domcontentloaded', timeout=60000)
        await pg2.wait_for_function(
            '() => window.__PP_GAME && window.__PP_VERSION', timeout=60000)
        try:
            await pg2.evaluate("() => { window.__PP_GAME.salirALaWeb(); }")
        except Exception:
            pass   # la navegación destruye el contexto del evaluate: ESPERADO
        try:
            await pg2.wait_for_url(BASE + '/', timeout=15000)
            salida_ok = True
        except Exception:
            salida_ok = False
        url_final = pg2.url
        await pg2.close()
        await b.close()
    chk(out.get('presente'), 'juego vivo (window.__PP_GAME)')
    chk(not errs, f'0 pageerrors ({len(errs)}: {errs[:2]})')
    if out.get('presente'):
        # r60 · EL DATO MANDA VIVO: la dificultad se calcula DESDE LA TABLA
        chk(out.get('eloHook'), 'gancho __PP_ELO vivo (alias de la tabla)')
        chk(out.get('cpuMedium') == 1050 and out.get('hardVelo') == 3.8 and
            out.get('easyMiss') == 0.15,
            f"alias vivos: ELO_CPU.medium={out.get('cpuMedium')} · "
            f"hard.maxSpeed={out.get('hardVelo')} · easy.missBase={out.get('easyMiss')}")
        chk(out.get('mm1') == ['medium', 0.7499, 1000] and
            out.get('mm2') == ['easy', 950] and out.get('mm3') == ['hard', 1200],
            f"bandas del matchmaking VIVAS: {out.get('mm1')} · "
            f"{out.get('mm2')} · {out.get('mm3')}")
        chk(out.get('mm4') == [1.6, 1282],
            f"k del matchmaking acotado por la tabla (k tope + elo): {out.get('mm4')}")
        chk(out.get('adaptK') == 1.22,
            f"ADAPTATIVO VIVO: 4 puntos arriba → k = {out.get('adaptK')} "
            '(1 + 4×0.055 de la tabla)')
        chk(out.get('svK10') == 1.8,
            f"SUPERVIVENCIA VIVA: 10 rallyes → k = {out.get('svK10')} "
            '(1 + 10×0.08 de la tabla)')
        chk(out.get('svK50') == 2.1,
            f"techo de supervivencia de la tabla: k = {out.get('svK50')} (2,1)")
        chk(not out.get('adaptErr'), f"sin errores en el ciclo adaptativo ({out.get('adaptErr')})")
        # r59 · conservación funcional del audio
        chk(out.get('audioVivo'), 'audio vivo (G.audio)')
        chk(out.get('master') is not None and
            abs(out.get('master') - 0.9) < 1e-3,
            f'EL DATO MANDA: master.gain = {out.get("master")} '
            '(0,9 leído de CONFIG_AUDIO.buses · AudioParam float32)')
        chk(out.get('musicaFab') == 1 and out.get('fxFab') == 1 and
            out.get('locutorFab') == 0.18,
            f'fábrica de canales desde la tabla '
            f'(música {out.get("musicaFab")} · efectos {out.get("fxFab")} · '
            f'locutor {out.get("locutorFab")})')
        chk(out.get('tarjeta'), 'HUB vivo: la tarjeta \'salirweb\' se dibuja '
            'DESDE CONFIG_MENU (conservación r58)')
        chk(out.get('fnPuerta'), 'puerta viva: salirALaWeb existe (r58)')
        chk(salida_ok and url_final == BASE + '/',
            f'AUTO_ORIGIN resuelto VIVO: {url_final!r} (conservación r58)')
        chk(out.get('nace', 0) > 9.5,
            f'IMÁN: la ventana NACE ({out.get("nace")} s) — herencia r54')
        chk('agotado' not in (out.get('msg') or '').lower() and
            'worn off' not in (out.get('msg') or '').lower(),
            f'IMÁN: sin «agotado» al lanzar ({out.get("msg", "")[:48]}…)')
        chk(out.get('sigue', 0) > 8.5,
            f'IMÁN: la ventana SIGUE viva 1 s después ({out.get("sigue")} s)')
        chk(out.get('efectoNace', 0) > 9.5,
            f'EFECTO convive: nace ({out.get("efectoNace")} s)')
        chk(out.get('imanAun', 0) > 8.0,
            f'EFECTO convive: el imán SIGUE ({out.get("imanAun")} s)')
        chk(out.get('megaNace', 0) > 14.5,
            f'DATO MANDA: la MEGA nace a los 15,00 s de ARCANO_CFG '
            f'({out.get("megaNace")} s) — herencia r55')
    print(f'RESULTADO PROD SMOKE r60: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)


asyncio.run(main())
