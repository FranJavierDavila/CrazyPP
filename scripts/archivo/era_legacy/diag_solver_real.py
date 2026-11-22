#!/usr/bin/env python3
"""Compara el aterrizaje PREDICHO por el solver vs el vuelo REAL (stepPhysics)."""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 480, "height": 300})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        await page.evaluate("() => { window.__wantSolverHook = true; }")
        await page.wait_for_timeout(600)
        await page.click("#spectate")
        await page.wait_for_timeout(400)

        CASES = [
            ("dejada desde fondo", [0.33, 0.93, -2.13], 0.95, -8, [-0.12, -1.30], 3.4),
            ("push medio",         [0.20, 0.90, -2.10], 0.75, -7, [0.18, -0.78], 5.0),
            ("drive profundo",     [0.00, 1.00, -1.95], 0.55, 16, [-0.35, -0.31], 6.2),
            ("drive corto",        [0.10, 1.05, -1.90], 0.62, 13, [0.30, -0.75], 6.2),
        ]
        for name, f, T, sx, tgt, maxV in CASES:
            out = await page.evaluate("""(c) => {
                const H = window.__solverHook;
                const g = window.__game;
                const V3 = g.ball.vel.constructor;
                const from = { x: c.f[0], y: c.f[1], z: c.f[2] };
                const spin = new V3(c.sx, 0, 0);
                const target = { x: c.t[0], y: H.DIMS.tableTopY + H.DIMS.ballRadius,
                                 z: c.t[1] };
                const v = H.computeShotVelocityReal(from, target, c.T, c.maxV, spin);
                g.demoAI._frozen = true; g.demoAI.update = () => null;
                g.rules.state = 'rally'; g.rules.stateTimer = 999;
                g.rules.mustBounceOpp = true; g.rules.validBounce = false;
                g.rules.lastHitter = null;
                g.ball.pos.set(from.x, from.y, from.z);
                g.ball.vel.set(v.x, v.y, v.z);
                g.ball.spin.set(spin.x, spin.y, 0);
                return { name: c.name, v: [v.x, v.y, v.z].map((x) => +x.toFixed(2)),
                         target: c.t };
            }""", {"f": f, "t": tgt, "T": T, "sx": sx, "maxV": maxV, "name": name})
            res = await page.evaluate("""() => new Promise((done) => {
                const g = window.__game;
                let prevVy = g.ball.vel.y, n = 0;
                const iv = setInterval(() => {
                    const b = g.ball;
                    if (prevVy < 0 && b.vel.y > 0 && Math.abs(b.pos.y - 0.78) < 0.06) {
                        clearInterval(iv);
                        done({ landed: [+b.pos.x.toFixed(3), +b.pos.z.toFixed(3)] });
                    }
                    if (b.pos.y < 0.03 || ++n > 600) {
                        clearInterval(iv);
                        done({ landed: null,
                               end: [+b.pos.x.toFixed(2), +b.pos.y.toFixed(2), +b.pos.z.toFixed(2)] });
                    }
                    prevVy = b.vel.y;
                }, 12);
            })""")
            print(f"{out['name']:20s} v0={out['v']} objetivo={out['target']} -> real={res}")
        await browser.close()

asyncio.run(main())
