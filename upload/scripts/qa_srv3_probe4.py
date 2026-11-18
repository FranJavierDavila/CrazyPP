"""Sonda 4: secuencia real de contactos del caso pala quieta."""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto('http://localhost:3000/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__PP_BOUNCE_LAB', timeout=30000)
        r = await pg.evaluate('''() => {
          window.__PP_HITLOG = [];
          const out = window.__PP_BOUNCE_LAB({ seconds: 3.5 });
          return { log: window.__PP_HITLOG, impacts: out.impactSpeeds,
                   resting: out.resting, faceDist: out.faceDist };
        }''')
        for e in r['log'][:40]:
            print(json.dumps(e))
        print('impacts:', r['impacts'])
        await b.close()

asyncio.run(main())
