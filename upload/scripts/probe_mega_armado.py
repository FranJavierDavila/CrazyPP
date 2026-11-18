#!/usr/bin/env python3
"""Sonda puntual: por qué el armado de _megaMatch falla en headless."""
import asyncio
import json

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)[:200]))
        await page.goto("http://localhost:3000/game.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        for ronda in range(3):
            rt = await page.evaluate("""async () => {
              const G = window.__PP_GAME;
              const C = G.champs;
              const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
              try { window.__pp2DPlay = true; } catch (e) { /* */ }
              let catalogo = false;
              for (let i = 0; i < 120 && !catalogo; i++) {
                await dorme(500);
                catalogo = C.list().length >= 5;
              }
              if (!catalogo) return { sinCatalogo: true };
              try { await C.launch('locura'); } catch (e) { return { errLaunch: String(e) }; }
              const w = C.mod;
              const bk = window.__PP_LOCURA;
              let impl = null;
              for (let i = 0; i < 48 && !impl; i++) {
                impl = (bk && typeof bk.ctrl === 'function' && bk.ctrl()) ||
                       (w && w.impl) || null;
                if (!impl) await dorme(250);
              }
              if (!impl) return { sinImpl: true };
              if (!impl.active && w && typeof w.start === 'function') {
                try { w.start(); } catch (e) { /* */ }
                await dorme(400);
              }
              if (!impl.powers.includes('mega_pala')) impl.powers.push('mega_pala');
              const pre = {
                activo: impl.active, inited: impl.inited,
                powers: impl.powers.length, megaT: impl._megaT,
                match: impl._megaMatch, ready: impl._megaReady,
                estadoReglas: G.rules.state,
              };
              let errMatch = null;
              try { G.rules.startMatch('match'); } catch (e) { errMatch = String(e); }
              G.rules.state = 'serve';
              let errUpd = null;
              try { impl.update(1 / 60); } catch (e) { errUpd = String(e); }
              const post = {
                estadoReglas: G.rules.state,
                match: impl._megaMatch, ready: impl._megaReady,
                cd: impl._megaCd, fx: !!impl._megaFx, fxOn: impl._megaFxOn,
              };
              return { pre, errMatch, errUpd, post };
            }""")
            print(f"RONDA {ronda}:", json.dumps(rt, ensure_ascii=False))
            try:
                await page.evaluate("async () => { try { window.__PP_GAME.champs.leaveAll(); } catch (e) { /* */ } }")
            except Exception:
                pass
            await page.wait_for_timeout(800)
        if errs:
            print("PAGEERRORS:", errs[:3])
        await browser.close()

asyncio.run(main())
