"""Sonda 3 SRV3: bote con hoja en z limpio + traza del caso serveFlight."""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto('http://localhost:3000/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__PP_BOUNCE_LAB', timeout=30000)

        r = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 5 })''')
        print('quieta   :', r['impactSpeeds'])
        print('           resting', r['resting'], '· faceDist', r['faceDist'],
              '· eventos', r['eventTypes'])

        r2 = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 1.2, padVelY: 1.5 })''')
        print('subiendo :', r2['impactSpeeds'], r2['eventTypes'])

        r3 = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 1.0, serveFlight: true, trace: true })''')
        print('saque    :', r3['impactSpeeds'], r3['eventTypes'])
        print('  traza  :', json.dumps(r3['trace'][:12]))
        await b.close()

asyncio.run(main())
