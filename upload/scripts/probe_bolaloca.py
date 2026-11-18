#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe_bolaloca.py — sondeo del estado real de la regla solo-1 en vivo."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("http://localhost:3000/game.html",
                        wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        rt = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const o = {};
          window.__pp2DPlay = true;
          G.palaMejorada = true;
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          const libre = (G.paddleHand === 0) ? 1 : 0;
          o.lang = (typeof __ppLang !== 'undefined') ? __ppLang : '?';
          o.mensajeInicial = G.rules.message || '';
          try { G.rules.startMatch('match'); } catch (e) { o.errM = String(e); }
          G.champs.activeId = 'locura';
          G.rules.state = 'rally';
          const entB = { id: 'bolaloca', n: 1 };
          const entE = { id: 'efecto', n: 1 };
          G._megaMatriz.length = 0;
          G._megaMatriz.push(entB, entE);
          G._megaIdx = 0;
          o.sel0 = (G._megaSel() || {}).id;
          o.vivo0 = G._poderVivoAlguno();
          o.bolaHay = !!(G.ball && G.ball.vel);
          o.r1 = G.megaTrigger(libre);
          o.T = G._bolalocaT;
          o.vivo1 = G._poderVivoAlguno();
          o.msg1 = G.rules.message || '';
          G._megaIdx = 1;
          o.sel1 = (G._megaSel() || {}).id;
          o.r2 = G.megaTrigger(libre);
          o.efectoT = G._efectoT;
          o.nE = entE.n;
          o.msg2 = G.rules.message || '';
          G._megaIdx = 0;
          o.tAntes = G._bolalocaT;
          o.r3 = G.megaTrigger(libre);
          o.T3 = G._bolalocaT;
          o.msg3 = G.rules.message || '';
          o.matriz = G._megaMatriz.map((x) => x.id + ':' + x.n);
          return o;
        }""")
        await browser.close()
        for k, v in rt.items():
            print(f'{k}: {v}')

asyncio.run(main())
