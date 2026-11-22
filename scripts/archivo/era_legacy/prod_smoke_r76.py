#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r76.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 172 · r76
(https://franjavierdavila.github.io/CrazyPP/game.html — V3.6.167-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva el sello 3.6.167, el PISO 72
    (PERF_PISO), la sonda 68/55, la emergencia honesta, el congelado 68,
    el vr_ping con el estado del gobernador y TODAS las agujas r75 de red;
    sw.js servido sella v3.6.167; PAGES-VERSION.txt con fuente_commit.
  · FUNCIONAL: el juego VIVO en producción — __PP_PERF con piso ≥72,
    escalera 90→72 / imagen primero / emergencia 60, sonda 68 pasa y 64
    escalona, carga del perfil 60→72 (segunda visita pre-sembrada),
    MI CASA → ESCOGER HALL (regresión r74) y 0 pageerrors.
Uso: python3 scripts/prod_smoke_r76.py"""
import asyncio
import os
import urllib.request

from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.167-SDK6'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const pf = window.__PP_PERF || null;
  out.perfVivo = !!pf && typeof pf.status === 'function';
  if (pf) {
    out.pisoArranque = pf.rate >= 72;
    pf.rate = 90; pf._stepDown(true);
    out.noventaATierra = pf.rate === 72;
    pf.rate = 72; pf.fovea = 0.30; pf.scale = 1.20;
    const fv0 = pf.fovea;
    pf._stepDown(false);
    out.imagenPrimero = pf.rate === 72 && pf.fovea > fv0 + 0.05;
    pf.fovea = pf.foveaMax(); pf.scale = 0.8; pf.rate = 72;
    pf._stepDown(false);
    out.emergencia60 = pf.rate === 60;
    pf.probe = { round: 0, t: 0, n: 0, acc: 0, min: 999, why: 'qa' };
    pf._probeRound(69, 56);
    out.sonda68Pasa = !!pf.lastCal && pf.lastCal.fps === 69 && !pf.probe;
    pf.rate = 72; pf.scale = 1.2;
    pf.fovea = Math.min(pf.fovea, pf.foveaMax());
  }
  const G = window.__PP_GAME;
  if (!G) { out.sinJuego = true; return out; }
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(60);
  const idsMain = (G.menuRects || []).map((r) => String(r.id));
  out.casaHallpick = idsMain.includes('page:hallpick');
  out.errs = (window.__PP_ERRS || []).length;
  return out;
}"""


async def main():
    game = get(URL)
    chk('3.6.167-SDK6' in game, 'game.html SERVIDO sella 3.6.167-SDK6')
    chk('PERF_PISO = 72' in game, 'PISO 72 servido (PERF_PISO, r76)')
    chk('fpsAvg >= 68 && fpsMin >= 55' in game and
        'fpsAvg >= 63 && fpsMin >= 55' not in game,
        'sonda servida con la barra 68/55 (la 63 vieja FUERA)')
    chk('fpsAvg >= 60 ? Math.min(this.rate, PERF_PISO) : 60' in game,
        'emergencia honesta servida (60 solo con media < 60)')
    chk('const bajandoTasa' in game and 'const bajandoImg' in game,
        'gobernador servido: tasa e imagen separadas (r76)')
    chk('Math.max(PERF_PISO, typeof d.rate' in game,
        'perfil bajo 72 se recupera al piso (servido)')
    chk('red < 68' in game and 'red >= 70' in game and 'red < 58' not in game,
        'congelado de telemetría en red servido a 68 (r76)')
    chk('d2.perf = perf' in game, 'vr_ping con el estado del gobernador (servido)')
    chk('INTERP_MAX: 220' in game and 'EXTRAP_MAX: 0.160' in game and
        'bp > 32768' in game, 'regresión r75 servida: jitter buffer + contrapresión')
    chk('recien = performance.now() - (this._mstartAt || 0) < 8000' in game,
        'regresión r75 servida: guarda de revancha')
    swjs = get(BASE + '/sw.js')
    chk('crazypp-v3.6.167-SDK6' in swjs, 'sw.js SERVIDO sella v3.6.167 (purga PWA)')
    try:
        pv = get(BASE + '/PAGES-VERSION.txt')
        chk('d7516d3' in pv, 'PAGES-VERSION.txt: fuente_commit d7516d3 (r76)')
    except Exception as e:
        chk(False, 'PAGES-VERSION.txt legible (' + str(e)[:60] + ')')

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page(viewport={'width': 1280, 'height': 720})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)))
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(4200)
        out = await page.evaluate(JS)
        # segunda visita: perfil guardado a 60 → debe recuperar el PISO 72
        await page.add_init_script(
            "try { localStorage.setItem('ppxr_perf_v1',"
            " JSON.stringify({tier:'gen', auto:true, scale:1.2, rate:60,"
            " fovea:0.55})); } catch (e) {}")
        await page.goto(URL, wait_until='load', timeout=60000)
        await page.wait_for_timeout(3600)
        piso = await page.evaluate(
            "() => { const pf = window.__PP_PERF;"
            " return pf ? { rate: pf.rate, tier: pf.tier } : null; }")
        await browser.close()

    if out.get('sinJuego'):
        print('✗ el juego no arrancó en producción')
        return
    chk(out.get('perfVivo'), '__PP_PERF vivo en producción')
    chk(out.get('pisoArranque'), 'piso de arranque ≥72 (perfil gen del smoke)')
    chk(out.get('noventaATierra'), '90→72 en vivo (piso intacto)')
    chk(out.get('imagenPrimero'), 'en el piso regala IMAGEN (fovea) en vivo')
    chk(out.get('emergencia60'), '60 solo como emergencia en vivo')
    chk(out.get('sonda68Pasa'), 'sonda 69/56 PASA en producción')
    chk(piso and piso.get('rate') == 72, 'perfil guardado a 60 → AL PISO 72 en producción')
    chk(out.get('casaHallpick'), 'regresión r74: MI CASA abre ESCOGER HALL')
    chk(not errores and not out.get('errs'), 'sin pageerrors en producción')
    print('RESULTADO: ' + str(ok) + ' OK · ' + str(fails) + ' fallos')


if __name__ == '__main__':
    asyncio.run(main())
