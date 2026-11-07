#!/usr/bin/env python3
"""Baseline IA v3: recorder dentro de la página, 90 s de demo IA-vs-IA."""
import asyncio, json
from playwright.async_api import async_playwright

DUR_S = 90

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(600)
        await page.evaluate("""() => {
            window.__rec = { rally: 0, rallies: [], hist: [], last: '' };
            const g = window.__game;
            window.__recTimer = setInterval(() => {
                const r = window.__rec;
                if (g.rules.state === 'rally') r.rally = Math.max(r.rally, g.rules.rallyHits);
                if (g.rules.state !== 'rally' && r._prev === 'rally') {
                    r.rallies.push(r.rally); r.rally = 0;
                }
                r._prev = g.rules.state;
                const m = g.rules.message || '';
                if (m && m !== r.last) {
                    r.hist.push({ t: performance.now() / 1000, rally: r.rally,
                                  p: g.rules.scorePlayer, a: g.rules.scoreAi, msg: m });
                    r.last = m;
                }
            }, 60);
        }""")
        await asyncio.sleep(DUR_S)
        out = await page.evaluate("""() => {
            clearInterval(window.__recTimer);
            return window.__rec;
        }""")
        rallies = out["rallies"]
        print("MARCADOR FINAL:", (out["hist"][-1]["p"], out["hist"][-1]["a"]))
        print("RALLYES:", len(rallies),
              "· media:", round(sum(rallies) / max(1, len(rallies)), 2),
              "· max:", max(rallies) if rallies else 0)
        print("EVENTOS:")
        for h in out["hist"]:
            print(f"  {h['t']:7.1f}s rally={h['rally']:2d} {h['p']}-{h['a']}  {h['msg'][:72]}")
        await browser.close()

asyncio.run(main())
