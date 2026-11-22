#!/usr/bin/env python3
"""Smoke SDK1 (V3.6.1-SDK1): versión nueva + import del orbital en cadena +
SDK registrado en window + congela/descongela operativos + 0 pageerrors."""
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
        await pg.goto('http://localhost:3000/game.html', wait_until='networkidle')
        ver = await pg.evaluate("window.__PP_VERSION || ''")
        badge = await pg.inner_text('#verBadge') if await pg.locator('#verBadge').count() else ''
        print('version:', ver, '· badge:', badge)

        # import directo del módulo orbital (carga el SDK en cadena) + engine SFX
        r = await pg.evaluate("""async () => {
          const m = await import('/championships/estacion_orbital/index.js');
          const sdk = await import('/championships/sdk/champ_sdk.js');
          const dummy = { freezeT: 0 };
          sdk.congela(dummy, 2.15);
          const tras1 = dummy.freezeT;
          sdk.congela(dummy, 1.0);          // no acorta una en curso
          const tras2 = dummy.freezeT;
          sdk.descongela(dummy);
          const eng = sdk.createSfx(new URL('/x/', 'http://z/').href, () => null);
          return {
            def: !!m.default,
            sdkVer: window.__PP_SDK || null,
            sdkExports: ['createSfx','congela','descongela','getCore','assetURL']
              .filter(k => !(k in sdk)),
            congela: [tras1, tras2, dummy.freezeT],
            engine: typeof eng.play === 'function' && typeof eng.tiene === 'function',
          };
        }""")
        print('orbital default:', r['def'], '· __PP_SDK:', r['sdkVer'])
        print('exports ausentes (debe ser []):', r['sdkExports'])
        print('congela [2.15, 2.15, 0]:', r['congela'])
        print('engine play/tiene:', r['engine'])
        print('pageerrors:', len(errs), errs[:2])
        await b.close()
        ok = (ver == '3.6.1-SDK1' and r['def'] and r['sdkVer'] == '1.0.0'
              and not r['sdkExports'] and r['congela'] == [2.15, 2.15, 0]
              and r['engine'] and not errs)
        print('SMOKE SDK1:', 'OK' if ok else 'FALLO')
        return 0 if ok else 1

exit(asyncio.run(main()))
