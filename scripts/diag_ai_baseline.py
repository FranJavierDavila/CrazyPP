#!/usr/bin/env python3
"""Línea base de la IA en modo demo: 60 s de IA vs IA, tally de causas de punto."""
import asyncio, json, collections, sys
from playwright.async_api import async_playwright

DUR_S = 60

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
        last_msg = ""
        last_score = (0, 0)
        rally_hits = 0
        samples = []
        for i in range(DUR_S * 5):
            out = await page.evaluate("""() => {
                const g = window.__game;
                return { msg: g.rules.message, p: g.rules.scorePlayer,
                         a: g.rules.scoreAi, r: g.rules.rallyHits,
                         state: g.rules.state };
            }""")
            msg = out["msg"] or ""
            score = (out["p"], out["a"])
            rally_hits = max(rally_hits, out["r"])
            if score != last_score and out["state"] != "over":
                rallies.append(rally_hits)
                tally[msg] += 1
                last_score = score
                rally_hits = 0
            if msg != last_msg:
                last_msg = msg
            samples.append(out)
            await asyncio.sleep(0.2)

        # resumen
        print("MARCADOR FINAL:", last_score)
        print("RALLYES:", len(rallies),
              "· media:", round(sum(rallies) / max(1, len(rallies)), 2),
              "· max:", max(rallies) if rallies else 0)
        print("CAUSAS DE PUNTO:")
        for k, v in tally.most_common(12):
            print(f"  {v:3d}  {k}")
        await browser.close()

asyncio.run(main())
