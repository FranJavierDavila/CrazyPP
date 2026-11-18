"""Sonda 2 SRV3: bote tras el guard de recesión + diagnóstico serveFlight."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto('http://localhost:3000/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__PP_BOUNCE_LAB', timeout=30000)

        r = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 5 })''')
        print('quieta   :', r['impactSpeeds'], 'resting', r['resting'], 'faceDist', r['faceDist'])

        r2 = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 1.2, padVelY: 1.5 })''')
        print('subiendo :', r2['impactSpeeds'])

        # diagnóstico serveFlight: eventos COMPLETOS de stepPhysics + traza de la bola
        d = await pg.evaluate('''() => {
          const dbg = window.__ppDebug;
          const DIMS = dbg.DIMS;
          const THREEv = window.__game ? null : null;
          // reconstruir el lab a mano para ver todos los eventos
          const q = new (window.__game.constructor ? Object : Object)();
          return null;
        }''')
        # más directo: instrumentamos con un runner propio que usa stepPhysics expuesto
        d = await pg.evaluate('''() => {
          const stepPhysics = window.__ppDebug.stepPhysics;
          const DIMS = window.__ppDebug.DIMS;
          // no tenemos createPaddleSim expuesto: usamos el bounce lab y leemos
          // su resultado con eventos capturados vía un truco — repetimos con
          // seconds corto y miramos ballY final para ver si atraviesa
          const r = window.__PP_BOUNCE_LAB({ seconds: 1.0, serveFlight: true });
          return r;
        }''')
        print('saque    :', d['impactSpeeds'], 'finalSpeed', d['finalSpeed'], 'ballY', d['ballY'])
        await b.close()

asyncio.run(main())
