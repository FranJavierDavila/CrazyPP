#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonda de depuración: secuencia OFF del conmutador, paso a paso."""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        rt = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          const dump = (tag) => ({
            tag, st: G.rules.state, rh: G.rules.rallyHits,
            ready: G._megaReady, icoOn: G._megaIconOn,
            icoVis: G._megaIcon ? G._megaIcon[0].visible : null,
            ico: !!G._megaIcon, mejorada: G.palaMejorada, t: G._megaT,
          });
          const log = [];
          try { G.rules.startMatch('match'); } catch (e) { log.push('errMatch ' + e); }
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { log.push('errUpd ' + e); } };
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          log.push(dump('cargada'));
          G.palaMejorada = false; paso(); paso();
          log.push(dump('off'));
          G.rules.state = 'point'; paso();
          log.push(dump('point'));
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          log.push(dump('rally11-off'));
          await dorme(300);
          log.push(dump('tras300ms'));
          return log;
        }""")
        for d in rt:
            print(d)
        await browser.close()


asyncio.run(main())
