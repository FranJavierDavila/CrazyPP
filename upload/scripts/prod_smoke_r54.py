#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r54.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 148
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.145-SDK6):
  · arranque: __PP_VERSION 3.6.145-SDK6 + badge + __PP_GAME · 0 pageerrors
  · FUNCIONAL (el bug «nacen agotados» del dueño): en un campeonato
    simulado, lanzar el SÚPER IMÁN → la ventana NACE (~10 s) y SIGUE viva
    1 s después (antes moría al frame siguiente con «worn off»).
Uso: python3 scripts/prod_smoke_r54.py"""
import asyncio
import sys
from playwright.async_api import async_playwright

URL = ('https://franjavierdavila.github.io/CrazyPP/game.html'
       '?v=3.6.145-SDK6')

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


JS = """async () => {
  const G = window.__PP_GAME || window.__pingpong;
  const out = { presente: !!G };
  if (!G) return out;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) {}
  G.palaMejorada = true;
  await dorme(300);
  G.renderer.xr.isPresenting = true;
  G.menuOpen = false; G._instr = null; G.champIntro = null;
  G.tutV1 = false; G.calib = false; G.calibPala = false;
  G.inHall = false; G._arconoOn = false;
  try { G.rules.onMatchStart = null; } catch (e) {}
  G.champs = { active: true, gunArmed: false, paddleGunArmed: false };
  G.rules.state = 'rally';
  G.rules.rallyHits = 0;
  // — el bug del dueño: ¿la ventana del imán NACE y SOBREVIVE? —
  G._megaMatriz = [{ id: 'iman', n: 1 }]; G._megaIdx = 0;
  G._imanT = 0; G._efectoT = 0;
  const iLibre = (G.paddleHand === 0) ? 1 : 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.nace = +G._imanT.toFixed(2);
  out.msg = String(G.rules.message || '');
  await dorme(1000);
  out.sigue = +G._imanT.toFixed(2);
  // y un segundo poder CONVIVE (puerta única r54)
  G._megaMatriz = [{ id: 'efecto', n: 1 }, { id: 'iman', n: 0 }];
  G._megaIdx = 0;
  G._efectoT = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.efectoNace = +G._efectoT.toFixed(2);
  out.imanAun = +G._imanT.toFixed(2);
  out.fin = true;
  return out;
}"""


async def main():
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
        chk(ver == '3.6.145-SDK6', f'__PP_VERSION = {ver!r}')
        chk('V3.6.145-SDK6' in badge, f'badge 2D = {badge!r}')
        out = await pg.evaluate(JS)
        await b.close()
    chk(out.get('presente'), 'juego vivo (window.__PP_GAME)')
    chk(not errs, f'0 pageerrors ({len(errs)}: {errs[:2]})')
    if out.get('presente'):
        chk(out.get('nace', 0) > 9.5,
            f'IMÁN: la ventana NACE ({out.get("nace")} s)')
        chk('agotado' not in (out.get('msg') or '').lower() and
            'worn off' not in (out.get('msg') or '').lower(),
            f'IMÁN: sin «agotado» al lanzar ({out.get("msg", "")[:48]}…)')
        chk(out.get('sigue', 0) > 8.5,
            f'IMÁN: la ventana SIGUE viva 1 s después ({out.get("sigue")} s)')
        chk(out.get('efectoNace', 0) > 9.5,
            f'EFECTO convive: nace ({out.get("efectoNace")} s)')
        chk(out.get('imanAun', 0) > 8.0,
            f'EFECTO convive: el imán SIGUE ({out.get("imanAun")} s)')
    print(f'RESULTADO PROD SMOKE r54: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)

asyncio.run(main())
