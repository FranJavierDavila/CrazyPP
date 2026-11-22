#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sonda_r54_asesino.py — ¿QUIÉN mata la ventana del imán recién nacida?
Envuelve _dlVentanasApaga/_poderesCortina/*Fin con contadores, lanza el
imán en un campeonato simulado y vuelca quién disparó el fin."""
import asyncio
import json
from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3000/game.html'

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

  // — envuelve los posibles asesinos —
  const conta = {};
  const env = (obj, name, label) => {
    const orig = obj[name];
    if (typeof orig !== 'function') return;
    obj[name] = function (...a) {
      conta[label] = (conta[label] || 0) + 1;
      return orig.apply(this, a);
    };
  };
  env(G, '_dlVentanasApaga', 'dlVentanasApaga');
  env(G, '_poderesCortina', 'cortina');
  env(G, '_imanFin', 'imanFin');
  env(G, '_efectoFin', 'efectoFin');
  const um = G.updateMega;
  env(G, 'updateMega', 'updateMega');
  const du = G._dlUpdate;
  env(G, '_dlUpdate', 'dlUpdate');

  out.estado0 = {
    mode: G.rules.mode, online: !!(G.net && G.net.online),
    dlEnabled: G._dlEnabled(), megaEnabled: G.megaEnabled(),
    enPrueba: G._poderesEnPrueba(),
  };
  // lanza el IMÁN
  G._megaMatriz = [{ id: 'iman', n: 1 }]; G._megaIdx = 0;
  G._imanT = 0;
  const iLibre = (G.paddleHand === 0) ? 1 : 0;
  let exc = null;
  try { G.onSelectStart(iLibre); } catch (e) { exc = String(e); }
  out.exc = exc;
  out.t0 = G._imanT;
  out.activa0 = G._megaActivaId;
  out.msg0 = String(G.rules.message || '');
  await dorme(250);
  out.t250 = G._imanT;
  out.activa250 = G._megaActivaId;
  out.msg250 = String(G.rules.message || '');
  out.conta = conta;
  out.estado1 = {
    dlEnabled: G._dlEnabled(), on: (G.megaEnabled() && !G.inHall && !G.calib),
    inHall: G.inHall, calib: G.calib,
    enPrueba: G._poderesEnPrueba(), state: G.rules.state,
  };
  return out;
}"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(URL, wait_until='domcontentloaded')
        await pg.wait_for_timeout(7000)
        out = await pg.evaluate(JS)
        await b.close()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print('pageerrors:', errs[:3])

asyncio.run(main())
