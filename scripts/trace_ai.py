#!/usr/bin/env python3
"""Traza fina de una prueba de devolución: por qué la CPU no llega."""
import asyncio, json, random
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 480, "height": 300})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(500)

        await page.evaluate("""() => {
            const g = window.__game;
            g.demoAI._frozen = true;
            g.demoAI.update = () => null;
            g.demoAI.pos.set(0, 1.0, 99);
            if (g.demoPaddleMesh) g.demoPaddleMesh.visible = false;
            window.__trace = [];
            window.__trTimer = setInterval(() => {
                const g = window.__game, b = g.ball, ai = g.ai;
                window.__trace.push({
                    t: +((performance.now() - window.__t0) / 1000).toFixed(3),
                    st: g.rules.state[0] + (g.rules.lastHitter || '?')[0],
                    bz: +b.pos.z.toFixed(2), by: +b.pos.y.toFixed(2),
                    bvz: +b.vel.z.toFixed(2),
                    az: +ai.pos.z.toFixed(2), ax: +ai.pos.x.toFixed(2),
                    pv: ai.predictValid,
                    pz: +ai.predict.z.toFixed(2), px: +ai.predict.x.toFixed(2),
                });
            }, 100);
        }""")

        for trial in range(6):
            x0 = random.uniform(-0.3, 0.3)
            vx = random.uniform(-0.8, 0.8)
            vz = -random.uniform(5.5, 6.5)
            vy = random.uniform(2.8, 3.2)
            sx = random.uniform(5, 9)
            await page.evaluate("""(p) => {
                const g = window.__game;
                g.rules.state = 'rally';
                g.rules.stateTimer = 999;
                g.rules.serveOwnPending = false;
                g.rules.mustBounceOpp = true;
                g.rules.validBounce = false;
                g.rules.isServeBall = false;
                g.rules.netTouched = false;
                g.rules.lastHitter = 'player';
                g.rules.message = '';
                g.tossed = false;
                g.ball.pos.set(p.x, 1.05, 0.9);
                g.ball.vel.set(p.vx, p.vy, p.vz);
                g.ball.spin.set(p.sx, 0, 0);
                window.__t0 = performance.now();
                window.__trialP = p;
                window.__trace.length = 0;
            }""", {"x": round(x0, 2), "vx": round(vx, 2), "vy": round(vy, 2),
                    "vz": round(vz, 2), "sx": round(sx, 1)})
            await asyncio.sleep(6.0)
            trace = await page.evaluate("() => window.__trace")
            msg = await page.evaluate("() => [window.__game.rules.state, window.__game.rules.message]")
            hit = any(h["st"] == "ra" and h["st"].startswith("ra") for h in trace)  # noop
            ret = await page.evaluate("() => window.__game.rules.lastHitter")
            print(f"--- prueba {trial}: x0={x0:.2f} vx={vx:.2f} vz={vz:.2f} vy={vy:.2f} sx={sx:.1f} -> last={ret} {msg[1][:40]}")
            # imprime cada 5 muestras (~0.17s)
            for h in trace[::3]:
                print(f"   t={h['t']:5.2f} {h['st']} bola z={h['bz']:+.2f} y={h['by']:.2f} vz={h['bvz']:+.2f} | ai x={h['ax']:+.2f} z={h['az']:+.2f} pv={h['pv']!s:5s} pred=({h['px']:+.2f},{h['pz']:+.2f})")
        await page.evaluate("() => clearInterval(window.__trTimer)")
        await browser.close()

asyncio.run(main())
