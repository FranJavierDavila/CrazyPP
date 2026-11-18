#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r58.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 152
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.149-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva CONFIG_MENU (menú data-driven) —
    tarjeta SALIR A LA WEB en el HUB dibujada desde datos, página de
    confirmación gemela del hallask, despachador con los 3 casos, la única
    puerta salirALaWeb() (telemetría con flush síncrono · session.end() con
    guardia 2 s · AUTO_ORIGIN sin dominios hardcodeados), i18n es/en — más
    la conservación completa r55/r56/r57 (ARCANO_CFG, pwViva, BOTE_TUNE,
    BOLA_TUNE, PASO_TUNE, R2, R3) y sw.js/portada a 3.6.149.
  · FUNCIONAL (herencia r54/r57 + nuevo r58): el juego VIVO en producción
    dibuja la tarjeta 'salirweb' en el HUB y la página 'salirask' con
    SI/NO; la puerta salirALaWeb() resuelve AUTO_ORIGIN a la carpeta que
    sirve el juego (capturada sin abandonar la página) y en un campeonato
    simulado el IMÁN nace/sobrevive, un poder CONVIVE y la MEGA nace a los
    15,00 s de ARCANO_CFG (el dato manda).
Uso: python3 scripts/prod_smoke_r58.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.149-SDK6'

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
  // — r58 · CONFIG_MENU: el menú VIVO dibuja la tarjeta y el prompt —
  try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) {}
  G.palaMejorada = true;
  G.menuOpen = true; G._instr = null; G.champIntro = null;
  G.tutV1 = false; G.calib = false; G.calibPala = false;
  G.inHall = false; G._arconoOn = false;
  G.menuPage = 'main';
  try { G.drawMenu(); } catch (e) {}
  await dorme(200);
  const rectIds = () => (G.menuRects || []).map((r) => r && r.id);
  out.tarjeta = rectIds().includes('salirweb');
  G.menuPage = 'salirask';
  try { G.drawMenu(); } catch (e) {}
  await dorme(200);
  const ids2 = rectIds();
  out.askSi = ids2.includes('salirweb_si');
  out.askNo = ids2.includes('salirweb_no');
  out.fnPuerta = typeof G.salirALaWeb === 'function' &&
                 typeof G.drawMenuSalidaAsk === 'function' &&
                 typeof G._iconoDeMenu === 'function';
  // (la PUERTA se prueba en una página desechable — navega de verdad;
  //  Location es inforgeable y no admite stub de assign — ver Python)
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
    # r58 · CONFIG_MENU: la tabla y la tarjeta como DATOS
    chk('const CONFIG_MENU = {' in gh, 'CONFIG_MENU servida (c02, única fuente)')
    chk("id: 'salirweb'," in gh and "urlDestino: 'AUTO_ORIGIN'," in gh and
        'tiempoMaxEsperaXRms: 2000,' in gh and
        "eventoTelemetria: 'salir_web'," in gh and 'cerrarSesionXR: true,' in gh,
        'tabla salir completa (id/destino/guardia/telemetría/XR como datos)')
    chk('confirmacion: {' in gh and "tituloKey: 'salirask_title'," in gh,
        'confirmación leída de claves i18n (datos, no literales)')
    chk('const SALIRCFG = CONFIG_MENU.salir;' in gh and
        'this._iconoDeMenu(SALIRCFG.icono), false);' in gh,
        'tarjeta del HUB dibujada DESDE los datos (_modeCard + icono por nombre)')
    chk('_iconoDeMenu(nombre) {' in gh and '_iconoSalir(c, cx, cy) {' in gh,
        'resolutor de iconos por nombre + icono «salir» dibujado (sin PNG)')
    chk('drawMenuSalidaAsk(rects) {' in gh and
        "btn('salirweb_si', 132, 470, 760, 170," in gh and
        "btn('salirweb_no', 132, 700, 760, 170," in gh,
        'página de confirmación «¿SALIR A LA WEB?» servida (SI/NO)')
    chk("case 'salirweb':" in gh and "case 'salirweb_si':" in gh and
        "case 'salirweb_no':" in gh, 'despachador con los 3 casos')
    chk('async salirALaWeb() {' in gh, 'la ÚNICA puerta salirALaWeb() servida')
    chk('window.__PP_TELE.flush(true);' in gh and
        "window.__PP_TELE.ev(S.eventoTelemetria, {});" in gh,
        'telemetría salir_web con flush SÍNCRONO (sendBeacon/keepalive)')
    chk('this.renderer.xr.getSession()' in gh and
        'new Promise((res) => setTimeout(res, S.tiempoMaxEsperaXRms))' in gh,
        'session.end() con guardia de 2 s (dato)')
    chk("window.location.pathname.replace(/game\\.html$/, '')" in gh,
        'AUTO_ORIGIN: la web principal = la carpeta que sirve el juego '
        '(cero dominios hardcodeados)')
    chk("hub_salirweb: 'SALIR A LA WEB'," in gh and
        "hub_salirweb: 'EXIT TO WEB'," in gh and
        "salirask_yes_btn: 'SÍ, SALIR'," in gh and
        "salirask_yes_btn: 'YES, EXIT'," in gh and
        "'salirweb': 'hint_salirweb'," in gh,
        'i18n es/en simétricos + tooltip hint_salirweb')
    # CONSERVACIÓN r57 · R1/R2/R3 (auditoría de físicas aplicada)
    chk('const PASO_TUNE = { uiMax: 1 / 30, fisMax: 1 / 12 };' in gh,
        'PASO_TUNE servida (conservación r57)')
    chk('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);' in gh and
        'const dtFis = Math.min(_rawDt, PASO_TUNE.fisMax);' in gh and
        'updatePaddleSim(ps, grip.position, tmpMountQ, now, dtFis);' in gh,
        'R1: pala midiendo con dtFis (conservación r57)')
    chk(gh.count('DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 &&') == 3,
        'R2: margen de bote alineado en los 3 simuladores (conservación)')
    chk('r57 · AUDITORÍA R3: el ×2,2 sólo vuela en la bola MARCADA' in gh and
        'DIMS.efectoMagnusMul || 1.5' in gh,
        'R3: Magnus ×1 predicho vs ×2,2 documentado (conservación)')
    # CONSERVACIÓN r55/r56 · ARCANO_CFG / BOTE_TUNE / BOLA_TUNE
    chk('const ARCANO_CFG = {' in gh and
        'const pwViva = (t) => (on || dlV) && t > 0;' in gh,
        'ARCANO_CFG + puerta única pwViva (conservación r55)')
    n_pw = len(re.findall(r'if \(pwViva\(this\._\w+T\)\)', gh))
    chk(n_pw == 13, f'13 compuertas LEEN pwViva (servidas: {n_pw})')
    chk('dur: ARCANO_CFG.ventanas.' in gh and
        gh.count('dur: ARCANO_CFG.ventanas.') == 14,
        'catálogo PODERES_PALA con su dur (14 filas, conservación r55)')
    chk('const BOTE_TUNE = {' in gh and 'spinDecayBote: 0.72,' in gh,
        'BOTE_TUNE servida (conservación r56)')
    chk('const BOLA_TUNE = { spinGanancia: 0.45 };' in gh,
        'BOLA_TUNE servida (conservación r56)')
    tel = get(BASE + '/telemetria.html?v=3.6.149-SDK6')
    chk('Rankings por jugador' in tel and 'id="tabsRank"' in tel,
        'panel telemetria.html: rankings por jugador servidos')
    sw = get(BASE + '/sw.js')
    chk('crazypp-v3.6.149-SDK6' in sw, 'sw.js CACHE crazypp-v3.6.149-SDK6')
    portada = get(BASE + '/')
    chk('v=3.6.149-SDK6' in portada, 'portada con cache-buster v=3.6.149-SDK6')

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
        chk(ver == '3.6.149-SDK6', f'__PP_VERSION = {ver!r}')
        chk('V3.6.149-SDK6' in badge, f'badge 2D = {badge!r}')
        out = await pg.evaluate(JS)
        # — r58 · LA PUERTA en una página DESECHABLE: llamar a la única
        # puerta y ESPERAR la navegación real — debe aterrizar en la
        # carpeta que sirve el juego (AUTO_ORIGIN), sin game.html.
        pg2 = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg2.goto(URL, wait_until='domcontentloaded', timeout=60000)
        await pg2.wait_for_function(
            '() => window.__PP_GAME && window.__PP_VERSION', timeout=60000)
        try:
            await pg2.evaluate("() => { const G = window.__PP_GAME; "
                               "G.salirALaWeb(); }")
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
        chk(out.get('tarjeta'), 'HUB vivo: la tarjeta \'salirweb\' se dibuja '
            'DESDE CONFIG_MENU (rect presente)')
        chk(out.get('askSi') and out.get('askNo'),
            'página \'salirask\' viva: SI y NO se dibujan desde los datos')
        chk(out.get('fnPuerta'), 'puerta viva: salirALaWeb · drawMenuSalidaAsk '
            '· _iconoDeMenu existen')
        chk(salida_ok and url_final == BASE + '/',
            f'AUTO_ORIGIN resuelto VIVO: {url_final!r} (la carpeta, sin '
            'game.html)')
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
    print(f'RESULTADO PROD SMOKE r58: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)


asyncio.run(main())
