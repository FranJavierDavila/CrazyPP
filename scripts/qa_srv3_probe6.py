"""Sonda 6: HITLOG filtrado SOLO por la bola del lab (tag='lab')."""
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
          const out = window.__PP_BOUNCE_LAB({ seconds: 4 });
          return { log: window.__PP_HITLOG.filter((e) => e.tag === 'lab'),
                   impacts: out.impactSpeeds, resting: out.resting,
                   faceDist: out.faceDist };
        }''')
        lab = [e for e in r['log'] if e['kind'] != 'REST']
        print('--- contactos del LAB (sin REST) ---')
        for e in lab[:24]:
            print(json.dumps({k: e[k] for k in ('seq', 'kind', 'dNow', 'vRelN') if k in e}))
        rests = [e for e in r['log'] if e['kind'] == 'REST']
        print('REST total:', len(rests),
              '· primer REST:', json.dumps(rests[0]) if rests else '-')
        print('impacts lab:', r['impacts'])
        print('resting:', r['resting'], '· faceDist:', r['faceDist'])
        await b.close()

asyncio.run(main())
