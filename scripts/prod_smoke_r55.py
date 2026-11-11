#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r55.py — VERIFICACIÓN EN PRODUCCIÓN de la FASE 149
(https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.146-SDK6):
  · ESTÁTICO: el game.html SERVIDO lleva la capa data-driven —
    ARCANO_CFG (ventanas/reglas/búho), puerta única pwViva (1 definición,
    13 compuertas leyéndola), búho leyendo ARCANO_CFG.ui.buho — y sw.js
    CACHE 3.6.146 + portada con cache-buster ?v=3.6.146-SDK6.
  · FUNCIONAL (herencia r54): en un campeonato simulado, lanzar el SÚPER
    IMÁN → la ventana NACE (~10 s) y SIGUE viva 1 s después; un segundo
    poder CONVIVE (la puerta única sigue viva tras el refactor).
Uso: python3 scripts/prod_smoke_r55.py"""
import asyncio
import re
import sys
import urllib.request
from playwright.async_api import async_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP'
URL = BASE + '/game.html?v=3.6.146-SDK6'

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
  // y un segundo poder CONVIVE (puerta única pwViva, r55)
  G._megaMatriz = [{ id: 'efecto', n: 1 }, { id: 'iman', n: 0 }];
  G._megaIdx = 0;
  G._efectoT = 0;
  G.onSelectStart(iLibre);
  await dorme(150);
  out.efectoNace = +G._efectoT.toFixed(2);
  out.imanAun = +G._imanT.toFixed(2);
  // LA CAPA DE DATOS se observa POR CONDUCTO (r55): la MEGA nace a los
  // 15,00 s EXACTOS de ARCANO_CFG.ventanas.mega (si el alias estuviera
  // roto, _megaT nacería NaN/0 — el dato manda sobre el código).
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
    chk('const ARCANO_CFG = {' in gh, 'ARCANO_CFG en el game.html SERVIDO')
    chk("golpesPorCarga: 20," in gh and
        "campeonato: { origen: 'registro_completo', candados: false }," in gh,
        'reglas por modalidad en la tabla servida')
    chk('ui: { buho: { x: 2.70, y: 2.60, zOff: 0.016 } },' in gh,
        'posición del búho como DATO en la tabla servida')
    chk('const pwViva = (t) => (on || dlV) && t > 0;' in gh,
        'puerta ÚNICA pwViva servida (1 definición)')
    n_pw = len(re.findall(r'if \(pwViva\(this\._\w+T\)\)', gh))
    chk(n_pw == 13, f'13 compuertas LEEN pwViva (servidas: {n_pw})')
    chk(len(re.findall(r'\(on \|\| dlV\)', gh)) == 1,
        'cero patrones copiados (sólo la definición)')
    chk('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,' in gh,
        'búho del Hall leyendo ARCANO_CFG (c08 servido)')
    chk('dur: ARCANO_CFG.ventanas.' in gh and
        gh.count('dur: ARCANO_CFG.ventanas.') == 14,
        'catálogo PODERES_PALA con su dur (14 filas)')
    sw = get(BASE + '/sw.js')
    chk('crazypp-v3.6.146-SDK6' in sw, 'sw.js CACHE crazypp-v3.6.146-SDK6')
    portada = get(BASE + '/')
    chk('v=3.6.146-SDK6' in portada, 'portada con cache-buster v=3.6.146-SDK6')

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
        chk(ver == '3.6.146-SDK6', f'__PP_VERSION = {ver!r}')
        chk('V3.6.146-SDK6' in badge, f'badge 2D = {badge!r}')
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
        chk(out.get('megaNace', 0) > 14.5,
            f'DATO MANDA: la MEGA nace a los 15,00 s de ARCANO_CFG '
            f'({out.get("megaNace")} s)')
    print(f'RESULTADO PROD SMOKE r55: {ok} OK · {fails} FALLOS')
    sys.exit(0 if not fails else 1)

asyncio.run(main())
