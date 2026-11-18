#!/usr/bin/env python3
"""Sonda puntual: estado del telón tras lanzar locura (debug del fallo BG)."""
import asyncio
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_GAME.champs", timeout=30000)
        out = await page.evaluate("""async () => {
            const g = window.__PP_GAME;
            const espera = () => {
                const room = g.champRoom;
                if (!room || room.builtFor !== 'locura') return 'builtFor!=locura (' + (room && room.builtFor) + ')';
                const mod = g.champs.moduleIfLoaded('locura');
                const cfg = (mod && mod.room) || null;
                const KEYS = ['floor','ceil','left','right','back','front'];
                const want = cfg ? KEYS.filter(k => cfg[k]) : [];
                if (!want.length) return 'sin room propio → listo';
                const have = room.loadedKeys || [];
                return 'want=' + want.length + ' have=' + have.length;
            };
            localStorage.removeItem('pp_intro_locura');
            g.champs.introPendiente = () => false;
            await g.champs.launch('locura');
            const snap = () => ({
                activo: g.champs.activeId,
                telon: !!g.champCurtain,
                t: g.champCurtain ? +g.champCurtain.t.toFixed(2) : null,
                esperaSet: !!(g.champCurtain && g.champCurtain.espera),
                fade: g.champCurtain ? g.champCurtain.fade : null,
                estado: espera(),
            });
            const s0 = snap();
            await new Promise((r) => setTimeout(r, 3000));
            const s3 = snap();
            return { s0, s3 };
        }""")
        import json
        print(json.dumps(out, indent=2, ensure_ascii=False))
        await browser.close()


asyncio.run(main())
