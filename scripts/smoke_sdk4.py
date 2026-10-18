#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Smoke SDK3 (V3.6.4-SDK4 · FASE 6): versión nueva + import EN CADENA de los
5 campeonatos + SDK v1.2.0 registrado (createMusic incluido) + motor de
música operativo (estado limpio, on/off sin contexto no rompen) +
precarga/pan en el engine + congela/descongela operativos + 0 pageerrors."""
import asyncio

from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:3000/game.html', wait_until='domcontentloaded')
        await pg.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=45000)
        ver = await pg.evaluate("window.__PP_VERSION || ''")
        badge = await pg.inner_text('#verBadge') if await pg.locator('#verBadge').count() else ''
        print('version:', ver, '· badge:', badge)

        # import en cadena de TODOS los campeonatos (el SDK carga con cada uno)
        r = await pg.evaluate("""async () => {
          const mods = {};
          for (const m of ['estacion_orbital', 'oeste', 'magia', 'locura', 'valle_neon']) {
            try {
              mods[m] = !!(await import('/championships/' + m + '/index.js')).default;
            } catch (e) { mods[m] = 'FALLO: ' + e.message; }
          }
          const sdk = await import('/championships/sdk/champ_sdk.js');
          // FASE 6: fábrica del tablón — forma de la API sin montarla
          const THREE = await import('three');
          const ps = sdk.createPowerSign(THREE, () => null, {
            coreo: 'v240', halo: true, arte: 'fit1833',
            url: () => undefined, dims: () => null,
          });
          const dummy = { freezeT: 0 };
          sdk.congela(dummy, 2.15);
          const tras1 = dummy.freezeT;
          sdk.congela(dummy, 1.0);          // no acorta una en curso
          const tras2 = dummy.freezeT;
          sdk.descongela(dummy);
          const eng = sdk.createSfx(new URL('/x/', 'http://z/').href, () => null);
          // FASE 5: motor de MÚSICA — sin game (null) no rompe y nace limpio
          const mus = sdk.createMusic(() => null, {
            url: () => undefined, vol: () => 0.18,
          });
          mus.on(); mus.sync(); mus.off();    // sin contexto: no-ops seguros
          const est = mus.estado();
          return {
            mods,
            sdkVer: window.__PP_SDK || null,
            sdkExports: ['createSfx', 'createMusic', 'createPowerSign',
                         'congela', 'descongela', 'getCore', 'assetURL']
              .filter(k => !(k in sdk)),
            congela: [tras1, tras2, dummy.freezeT],
            engine: typeof eng.play === 'function'
              && typeof eng.tiene === 'function'
              && typeof eng.precarga === 'function',
            music: typeof mus.on === 'function' && typeof mus.off === 'function'
              && typeof mus.sync === 'function' && typeof mus.sonando === 'function',
            musicEstado: est,
            musicSilente: mus.sonando() === false,
            powersign: typeof ps.build === 'function' && typeof ps.show === 'function'
              && typeof ps.hide === 'function' && typeof ps.update === 'function'
              && typeof ps.dispose === 'function' && ps.T_OUT === 1.9,
          };
        }""")
        print('defaults por módulo:', r['mods'])
        print('__PP_SDK:', r['sdkVer'])
        print('exports ausentes (debe ser []):', r['sdkExports'])
        print('congela [2.15, 2.15, 0]:', r['congela'])
        print('engine play/tiene/precarga:', r['engine'])
        print('música on/off/sync/sonando:', r['music'])
        print('estado del motor sin game:', r['musicEstado'])
        print('motor nace en silencio:', r['musicSilente'])
        print('pageerrors:', len(errs), errs[:2])
        await b.close()
        todos = all(v is True for v in r['mods'].values())
        ok = (ver == '3.6.4-SDK4' and todos and r['sdkVer'] == '1.3.0'
              and not r['sdkExports'] and r['congela'] == [2.15, 2.15, 0]
              and r['engine'] and r['music'] and r['musicSilente'] and r['powersign']
              and r['musicEstado'] == {'sonando': False, 'querido': False,
                                       'cargado': False, 'cargando': False}
              and not errs)
        print('tablón (createPowerSign) on/off/sync/dispose + T_OUT=1.9:', r['powersign'])
        print('SMOKE SDK4:', 'OK' if ok else 'FALLO')
        return 0 if ok else 1

exit(asyncio.run(main()))
