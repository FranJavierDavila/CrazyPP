"""Sonda SRV3: valida el lab de bote (decaimiento/rally/saque) y busca
geometrías de contacto «muy justo» que SOLO entran con la ventana tardía."""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto('http://localhost:3000/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__PP_BOUNCE_LAB', timeout=30000)

        print('=== BOTE: pala quieta (debe decaer hasta reposarse) ===')
        r = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 5 })''')
        print('impactos :', r['impactSpeeds'][:14])
        print('n botes  :', len(r['impactSpeeds']), '· finalSpeed', r['finalSpeed'],
              '· resting', r['resting'], '· faceDist', r['faceDist'], '· ballY', r['ballY'])

        print('=== BOTE: pala subiendo 1,5 m/s (suelo rally intacto ~2,3) ===')
        r2 = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 1.2, padVelY: 1.5 })''')
        print('impactos :', r2['impactSpeeds'][:6])

        print('=== BOTE: pala quieta en VUELO DE SAQUE (suelo 0,65) ===')
        r3 = await pg.evaluate('''() => window.__PP_BOUNCE_LAB({ seconds: 1.0, serveFlight: true })''')
        print('impactos :', r3['impactSpeeds'][:6])

        print('=== VENTANA TARDÍA: barrido «muy justo» (fuera del alcance directo) ===')
        # reach directo (medium, serveFlight): 0.0795+0.02+0.032+0.045 = 0.1765
        # con lateMargin: 0.1885. Barrimos offX 0.18..0.26 con bola cruzando el plano
        found = await pg.evaluate('''() => {
          const res = [];
          for (let offX = 0.178; offX <= 0.26; offX += 0.004) {
            for (const bvz of [-1.2, -2.0, -2.8, -3.6]) {
              for (const pvz of [-1.2, -1.8, -2.4, -3.0]) {
                for (const dist of [0.03, 0.05, 0.08]) {
                  const on = window.__PP_SERVE_LAB({ offX, ballVelZ: bvz, padVelZ: pvz, dist,
                    ballVelY: -0.4, padY: 1.05, padZ: -0.55, pitch: 10, assist: false });
                  if (on.hit) {
                    // contra-control: misma geometría SIN ventana
                    const w = window.__ppDebug.serveTune.lateWindow;
                    window.__ppDebug.serveTune.lateWindow = 0;
                    const off = window.__PP_SERVE_LAB({ offX, ballVelZ: bvz, padVelZ: pvz, dist,
                      ballVelY: -0.4, padY: 1.05, padZ: -0.55, pitch: 10, assist: false });
                    window.__ppDebug.serveTune.lateWindow = w;
                    res.push({ offX: +offX.toFixed(3), bvz, pvz, dist,
                      spd: on.exitSpeed, onlyLate: !off.hit });
                    if (res.filter(r => r.onlyLate).length >= 6) return res;
                  }
                }
              }
            }
          }
          return res;
        }''')
        for f in found:
            print(f)
        only_late = [f for f in found if f['onlyLate']]
        print('sólo-con-ventana:', len(only_late), '· total hits:', len(found))
        await b.close()

asyncio.run(main())
