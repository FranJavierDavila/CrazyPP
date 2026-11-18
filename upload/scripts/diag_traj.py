#!/usr/bin/env python3
"""Trajetoria punto a punto: solver-sim vs fisica real para el mismo v0."""
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

        out = await page.evaluate("""() => {
            const H = window.__solverHook;
            const g = window.__game;
            const V3 = g.ball.vel.constructor;
            // ---- 1) traza del SOLVER (misma integración que su sim interna) ----
            const from = new V3(0.10, 1.05, -1.90);
            const spin = new V3(13, 0, 0);
            const target = { x: 0.30, y: H.DIMS.tableTopY + H.DIMS.ballRadius, z: -0.75 };
            const v0 = H.computeShotVelocityReal(from, target, 0.62, 6.2, spin);
            const simTrace = [];
            {
                const pos = from.clone(), vel = v0.clone(), sp = spin.clone();
                const h = 1 / 240;
                for (let i = 0; i < 240 * 1.2; i++) {
                    vel.y += H.DIMS.gravity * h;
                    H.applyAerodynamics(vel, sp, h);
                    pos.addScaledVector(vel, h);
                    if (i % 24 === 0) simTrace.push([+pos.z.toFixed(3), +pos.y.toFixed(3),
                                                     +vel.z.toFixed(2)]);
                }
            }
            // ---- 2) traza de la FÍSICA REAL: mismo estado, stepPhysics por
            //         substeps con dt=1/60 (como un juego a 60 fps) ----
            const ball = { pos: from.clone(), vel: v0.clone(), spin: spin.clone() };
            const realTrace = [];
            {
                const dt = 1 / 60;
                for (let f = 0; f < 72; f++) {
                    H.stepPhysics(dt, ball, [], []);
                    if (f % 4 === 0) realTrace.push([+ball.pos.z.toFixed(3),
                                                     +ball.pos.y.toFixed(3),
                                                     +ball.vel.z.toFixed(2)]);
                }
            }
            return { v0: [v0.x, v0.y, v0.z].map((x) => +x.toFixed(3)),
                     simTrace, realTrace };
        }""")
        print("v0 =", out["v0"])
        print(f"{'t_sim':>6s} {'solver z':>9s} {'y':>6s} {'vz':>6s} | {'t_real':>6s} {'real z':>9s} {'y':>6s} {'vz':>6s}")
        for i in range(max(len(out["simTrace"]), len(out["realTrace"]))):
            s = out["simTrace"][i] if i < len(out["simTrace"]) else None
            r = out["realTrace"][i] if i < len(out["realTrace"]) else None
            ts = i * 0.1
            tr = i * (1 / 60) * 4
            ss = f"{s[0]:+9.3f} {s[1]:6.3f} {s[2]:+6.2f}" if s else " " * 24
            rr = f"{r[0]:+9.3f} {r[1]:6.3f} {r[2]:+6.2f}" if r else ""
            print(f"{ts:6.2f} {ss} | {tr:6.2f} {rr}")
        await browser.close()

asyncio.run(main())
