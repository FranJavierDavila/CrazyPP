"""Sonda 5: traza por subpaso alrededor del bote anómalo (pala quieta)."""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto('http://localhost:3000/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__PP_BOUNCE_LAB', timeout=30000)
        r = await pg.evaluate('''() => {
          window.__PP_TRACE = []; window.__PP_HITLOG = [];
          const out = window.__PP_BOUNCE_LAB({ seconds: 1.05 });
          return { trace: window.__PP_TRACE, log: window.__PP_HITLOG,
                   impacts: out.impactSpeeds };
        }''')
        print('impactos:', r['impacts'])
        print('--- HITLOG ---')
        for e in r['log']:
            print(json.dumps(e))
        print('--- TRACE (últimas 60 llamadas a collidePaddle con |d|<9cm) ---')
        for t in r['trace']:
            print(json.dumps(t))
        await b.close()

asyncio.run(main())
