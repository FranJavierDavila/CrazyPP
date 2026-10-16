"""Smoke SRV3: carga la página, comprueba versión, labs nuevos y errores JS."""
import asyncio
from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--use-gl=swiftshader'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(f'{BASE}/game.html', wait_until='load', timeout=60000)
        await pg.wait_for_function('window.__ppDebug && window.__PP_SERVE_LAB', timeout=30000)
        res = await pg.evaluate('''() => {
          const out = {};
          out.version = window.__PP_VERSION;
          out.badge = document.getElementById('verBadge')?.textContent;
          out.dims = { fis: window.__ppDebug.DIMS.physicsRealism,
                       perks: window.__ppDebug.DIMS.paddlePerks,
                       still: window.__ppDebug.DIMS.paddleStillSpeed };
          out.tune = { lateWindow: window.__ppDebug.serveTune.lateWindow,
                       lateMargin: window.__ppDebug.serveTune.lateMargin };
          out.hasBounceLab = typeof window.__PP_BOUNCE_LAB === 'function';
          // lab de saque sigue vivo (caso 1 de referencia)
          const lab = window.__PP_SERVE_LAB({ pitch: 12, padVelZ: -1.8, ballVelY: 0,
            padY: 1.1, padZ: 0.05, assist: true });
          out.lab1 = { hit: lab.hit, exitSpeed: lab.exitSpeed,
                       ok: lab.sim && lab.sim.ok };
          // i18n del diálogo
          out.bail_es = [window.__T('bail_title'), window.__T('bail_yes'), window.__T('bail_no')];
          window.__setLang('en');
          out.bail_en = [window.__T('bail_title'), window.__T('bail_yes'), window.__T('bail_no')];
          window.__setLang('es');
          return out;
        }''')
        print('version      :', res['version'])
        print('badge        :', res['badge'])
        print('dims         :', res['dims'])
        print('tune         :', res['tune'])
        print('bounceLab    :', res['hasBounceLab'])
        print('lab caso1    :', res['lab1'])
        print('bail es      :', res['bail_es'])
        print('bail en      :', res['bail_en'])
        print('pageerrors   :', errs if errs else 'ninguno')
        ok = (res['version'] == '3.1.1-SRV3' and res['badge'] == 'V3.1.1-SRV3'
              and res['dims']['still'] == 0.4 and res['tune']['lateWindow'] == 0.012
              and res['hasBounceLab'] and res['lab1']['hit'] and not errs)
        print('RESULTADO    :', 'OK' if ok else 'FALLO')
        await b.close()
        raise SystemExit(0 if ok else 1)

asyncio.run(main())
