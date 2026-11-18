#!/usr/bin/env python3
import asyncio, json, random
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 480, "height": 300})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(500)
        for trial in range(4):
            await page.evaluate("""() => {
                const g = window.__game;
                g.demoAI._frozen = true; g.demoAI.update = () => null;
                g.demoAI.pos.set(0, 1.0, 99);
                window.__aiDbg = { ok: 0, null: 0, towardOff: 0 };
                g.rules.state = 'point'; g.rules.stateTimer = 999;
                g.ball.pos.set(0, 0.03, 3.0); g.ball.vel.set(0,0,0);
            }""")
            await asyncio.sleep(0.4)
            params = {"x": round(random.uniform(-0.3,0.3),2), "vx": round(random.uniform(-0.8,0.8),2),
                      "vy": round(random.uniform(2.8,3.2),2), "vz": round(-random.uniform(5.5,6.5),2),
                      "sx": round(random.uniform(5,9),1)}
            await page.evaluate("""(p) => {
                const g = window.__game;
                g.rules.state = 'rally'; g.rules.stateTimer = 999;
                g.rules.mustBounceOpp = true; g.rules.validBounce = false;
                g.rules.lastHitter = 'player';
                g.ball.pos.set(p.x, 1.05, 0.9);
                g.ball.vel.set(p.vx, p.vy, p.vz);
                g.ball.spin.set(p.sx, 0, 0);
            }""", params)
            await asyncio.sleep(4)
            out = await page.evaluate("""() => {
                const g = window.__game;
                return { dbg: window.__aiDbg, msg: g.rules.message,
                         last: g.rules.lastHitter, pv: g.ai.predictValid,
                         ai: [g.ai.pos.x, g.ai.pos.z].map(v=>+v.toFixed(2)) };
            }""")
            print(json.dumps({**params, **out}))
        await browser.close()

asyncio.run(main())
