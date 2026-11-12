#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r59.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 153
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.150-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_AUDIO (la mezcla como
    datos: buses+compresor+murmullo · canales de fábrica · fundidos
    musica/bso/salon con timeouts derivados · SFX nivel/piso/tono ·
    clamps+jitter) con sus 44 lectores en c03, más la conservación
    completa r55/r56/r57/r58 y sw.js/portada a 3.6.150.
  · FUNCIONAL: el juego VIVO construye el grafo de audio DESDE LA TABLA
    (master 0,9 · fábrica música/efectos/locutor), el HUB dibuja la
    tarjeta 'salirweb' (r58) y la puerta resuelve AUTO_ORIGIN; en un
    campeonato simulado el IMÁN nace/sobrevive, un poder CONVIVE y la
    MEGA nace a los 15,00 s de ARCANO_CFG (el dato manda).
Uso: python3 scripts/prod_smoke_r59.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.150-SDK6'

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
  // — r59 · el grafo de audio construido DESDE LA TABLA —
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
    # r58 · CONFIG_AUDIO: la tabla de la mezcla servida
    chk('const CONFIG_AUDIO = {' in gh, 'CONFIG_AUDIO servida (c02, única fuente)')
    chk('murmullo: { base: 0.05, entradaS: 1.5, salidaS: 0.8 },' in gh and
        'compresor: { umbral: -16, rodilla: 22, ratio: 5, ataqueS: 0.002, liberacionS: 0.12 },' in gh,
        'buses: compresor y murmullo como DATOS')
    chk('canales: { musica: 1, efectos: 1, locutor: 0.18 },' in gh,
        'canales de FÁBRICA (música/efectos/locutor bajita) como datos')
    chk('musica: { base: 0.26, entradaS: 0.9, salidaS: 0.7, reajusteS: 0.15 },' in gh and
        'bso: { entradaS: 0.8, salidaS: 0.6, reajusteMs: 150, duckMs: 250, restauraMs: 500 },' in gh and
        'salon: { base: 0.30, entradaS: 1.2, salidaS: 1.0 },' in gh,
        'fundidos de los 3 canales de melodía (UNA MELODÍA) como datos')
    chk('pala:  { nivel: 0.72, piso: 0.15, tonoMin: 0.84, tonoMax: 1.34 },' in gh and
        'suelo: { nivel: 0.42, piso: 0.05, tonoMin: 0.86, tonoMax: 1.18 },' in gh,
        'SFX r62: nivel/piso/tono por impacto como DATOS')
    # r58 · los 44 lectores en c03 (RE de familias)
    n_bus = len(re.findall(r'CONFIG_AUDIO\.buses\.\w+', gh))
    n_can = len(re.findall(r'CONFIG_AUDIO\.canales\.\w+', gh))
    n_mus = len(re.findall(r'CONFIG_AUDIO\.musica\.\w+', gh))
    n_bso = len(re.findall(r'CONFIG_AUDIO\.bso\.\w+', gh))
    n_sal = len(re.findall(r'CONFIG_AUDIO\.salon\.\w+', gh))
    n_sfx = len(re.findall(r'CONFIG_AUDIO\.sfx\.\w+', gh))
    chk((n_bus, n_can, n_mus, n_bso, n_sal, n_sfx) == (12, 3, 7, 7, 5, 10),
        f'44 lectores enchufados (buses {n_bus} · canales {n_can} · '
        f'musica {n_mus} · bso {n_bso} · salon {n_sal} · sfx {n_sfx})')
    chk('this.master.gain.value = CONFIG_AUDIO.buses.master;' in gh and
        'this.arcVol = CONFIG_AUDIO.canales.locutor;' in gh,
        'c03 lee la tabla (grafo de salida + fábrica del locutor)')
    chk('_applyArcGain(ms = CONFIG_AUDIO.bso.reajusteMs)' in gh and
        'CONFIG_AUDIO.sfx.jitterBase +' in gh,
        'rampas y jitter leen la tabla (cero literales)')
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
    chk('crazypp-v3.6.150-SDK6' in sw, 'sw.js CACHE crazypp-v3.6.150-SDK6')
    portada = get(BASE + '/')
    chk('v=3.6.150-SDK6' in portada, 'portada con cache-buster v=3.6.150-SDK6')

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
        chk(ver == '3.6.150-SDK6', f'__PP_VERSION = {ver!r}')
        chk('V3.6.150-SDK6' in badge, f'badge 2D = {badge!r}')
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
    print(f'RESULTADO PROD SMOKE r59: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)


asyncio.run(main())
