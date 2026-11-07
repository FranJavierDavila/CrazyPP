#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sonda v4 MEGA PALA: mecánica manual (update llamados a mano) vs bucle."""
import asyncio
import json
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: print('PAGEERROR:', str(e)[:200]))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        out = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const C = G && G.champs;
          if (!C) return { sin: 'champs' };
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          window.__pp2DPlay = true;
          let catalogo = false;
          for (let i = 0; i < 120 && !catalogo; i++) { await dorme(500); catalogo = C.list().length >= 5; }
          if (!catalogo) return { sin: 'catalogo' };
          await C.launch('locura');
          const w = C.mod;
          let impl = w && w.impl;
          for (let i = 0; i < 40 && !(impl && impl.active); i++) {
            await dorme(250);
            impl = w && w.impl;
          }
          const r = {};
          r.activo = !!(impl && impl.active);
          r.init = !!(impl && impl.inited);
          r.wUpdateSrc = w ? String(w.update).slice(0, 300) : null;
          if (!impl || !impl.active) return r;
          // ---- MECÁNICA MANUAL: 60 updates a mano ----
          impl._megaT = 8;
          impl._megaFxStart();
          for (let i = 0; i < 60; i++) { try { impl.update(1 / 60); } catch (e) { r.errUpd = String(e); break; } }
          const hand = G.paddleHand | 0;
          r.escalaManual = (G.paddleMounts[hand].scale.x || 0).toFixed(3);
          r.megaSManual = +impl._megaS.toFixed(3);
          r.fxOn = impl._megaFxOn;
          // ---- BUCLE VIVO: 1.2 s esperando que el bucle decremente ----
          impl._megaT = 8;
          await dorme(1200);
          r.megaTBucle = +impl._megaT.toFixed(2);
          r.escalaBucle = (G.paddleMounts[hand].scale.x || 0).toFixed(3);
          return r;
        }""")
        print(json.dumps(out, indent=1, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
