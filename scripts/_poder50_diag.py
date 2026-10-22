#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnóstico puntual del tránsito del portal (r50)."""
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
          const out = {};
          G.palaMejorada = true;
          const libre = (G.paddleHand === 0) ? 1 : 0;
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          Math.random = () => 0.9;
          for (let i = 0; i < 20; i++) G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          G.updateMega(1 / 60);
          let tP = null;
          try { tP = G.megaTrigger(libre); } catch (e) { out.errT = String(e); }
          G.updateMega(1 / 60);
          out.ventana = G._portalT;
          G.rules.state = 'rally';
          const b = G.ball;
          b.pos.set(0.10, 1.02, 0.55);
          b.vel.set(-0.35, 0.55, -6.2);
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          G._portalCd = 0;
          try { G._portalProcesa(); } catch (e) { out.errX = String(e); }
          out.trasGolpe = {
            delayT: G._portalDelayT, sinkT: G._portalSinkT, riseT: G._portalRiseT,
            transit: b.ppTransito, ondaB: G._portalOndaB ? G._portalOndaB.visible : null };
          G.updateMega(0.5);
          out.mitad = {
            delayT: G._portalDelayT, riseT: G._portalRiseT, transit: b.ppTransito };
          try { G.updateMega(0.55); } catch (e) { out.errV = String(e); }
          out.trasSalida = {
            delayT: G._portalDelayT, riseT: G._portalRiseT,
            transit: b.ppTransito, posZ: b.pos.z, posY: b.pos.y,
            ondaB: G._portalOndaB ? G._portalOndaB.visible : null,
            ondaBT: G._portalOndaB ? G._portalOndaB.userData.ppT : null,
            spriteB: G._portalSpriteB ? G._portalSpriteB.visible : null,
            salPos: G._portalSalPos ? G._portalSalPos.toArray() : null };
          return out;
        }""")
        import json
        print(json.dumps(rt, indent=1, ensure_ascii=False))
        await browser.close()


asyncio.run(main())
