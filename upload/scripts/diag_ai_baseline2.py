#!/usr/bin/env python3
"""Línea base IA (v2): 90 s demo IA-vs-IA, tally de causas con bolas del rallye."""
import asyncio, json, collections
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

        tally = collections.Counter()
        rallies = []
        cur_rally = 0
        state_prev = ""
        history = []
        for i in range(DUR_S * 6):
            out = await page.evaluate("""() => {
                const g = window.__game;
                return { msg: g.rules.message, p: g.rules.scorePlayer,
                         a: g.rules.scoreAi, r: g.rules.rallyHits,
                         state: g.rules.state, last: g.rules.lastHitter };
            }""")
            if out["state"] == "rally":
                cur_rally = max(cur_rally, out["r"])
            if out["state"] != "rally" and state_prev == "rally":
                rallies.append(cur_rally)
                cur_rally = 0
            if out["msg"] and out["msg"] != history[-1] if history else True:
                pass
            if out["msg"] and (not history or out["msg"] != history[-1][1]):
                history.append((i / 6.0, out["msg"], cur_rally, out["p"], out["a"]))
            state_prev = out["state"]
            await asyncio.sleep(1 / 6)

        print("MARCADOR FINAL:", history[-1][3:], "· eventos:", len(history))
        print("RALLYES:", len(rallies),
              "· media:", round(sum(rallies) / max(1, len(rallies)), 2),
              "· max:", max(rallies) if rallies else 0)
        print("EVENTOS (t, msg, rally):")
        for t, m, r, pp, aa in history:
            print(f"  {t:6.1f}s  rally={r:2d}  {m[:70]}")
        await browser.close()

asyncio.run(main())
