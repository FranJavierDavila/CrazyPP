#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r35 · PRUEBA EN VIVO del Prisma visible (petición del dueño):
  A · la BOLA pinta arcoíris ALEATORIO (~6 saltos/s) mientras Prisma vive.
  B · fin honesto: al morir la ventana la bola vuelve a SU tinta.
  C · cooperativo: Oscuridad toma la bola (Prisma cede) y la devuelve intacta.
  D · auto-soltado: si otro poder (Onda) toma el testigo, el tinte cae solo.
  E · refresco honesto: re-disparar Prisma re-conquista la bola sin duplicar tinte.
Servidor: http://127.0.0.1:8123 (servir upload/public)."""
import asyncio
import base64
import json

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'

CONCEDER = """(id) => {
  const G = window.__PP_GAME || window.__game;
  const ent = { id, n: 1 };
  G._megaMatriz.push(ent);
  G._megaIdx = G._megaMatriz.length - 1;
  return G._megaMatriz.map((e) => e.id);
}"""

TRIGGER = """(id) => {
  const G = window.__PP_GAME || window.__game;
  G.rules.state = 'rally';
  G._megaIdx = G._megaMatriz.findIndex((e) => e.id === id);
  const r = G.megaTrigger(1);
  return { r, activa: G._megaActivaId };
}"""

ORIGEN = """() => {
  const G = window.__PP_GAME || window.__game;
  const m = G.ballMesh.material;
  return { col: m.color.getHex(), em: m.emissive ? m.emissive.getHex() : null };
}"""

ESTADO = """() => {
  const G = window.__PP_GAME || window.__game;
  const m = G.ballMesh.material;
  return {
    col: m.color.getHex(),
    em: m.emissive ? m.emissive.getHex() : null,
    tint: G._prismaBolaTint ? G._prismaBolaTint.col : null,
    tintEm: G._prismaBolaTint ? G._prismaBolaTint.em : null,
    oscTint: G._oscuridadTint ? G._oscuridadTint.col : null,
    activa: G._megaActivaId,
    prismaT: +G._prismaT.toFixed(2),
  };
}"""

FOTO = """() => {
  const G = window.__PP_GAME || window.__game;
  G.renderer.render(G.scene, G.camera);
  return G.renderer.domElement.toDataURL('image/png');
}"""


async def main():
    import os
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.add_init_script(
            "try { localStorage.setItem('pp_player_name', 'foro3d'); } catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                     timeout=45000)
        print('versión:', await page.evaluate('window.__PP_VERSION || "?"'))

        await page.evaluate(
            """async () => { const G = window.__PP_GAME || window.__game;
             try { await G.champs.launch('estacion_orbital'); } catch (e) {} }""")
        await page.wait_for_timeout(3500)
        await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller || mod;
          ctrl.serveTrigger();
        }""")
        await page.wait_for_timeout(1500)

        origen = await page.evaluate(ORIGEN)
        print('tinta original de la bola:', json.dumps(origen))

        # ── A · activar Prisma → la bola pinta arcoíris ALEATORIO ──
        await page.evaluate(CONCEDER, 'prisma')
        trig = await page.evaluate(TRIGGER, 'prisma')
        print('gatillo prisma:', json.dumps(trig))
        muestras = []
        for _ in range(6):
            await page.wait_for_timeout(140)
            muestras.append((await page.evaluate(ESTADO))['col'])
        distintos = len(set(muestras))
        est = await page.evaluate(ESTADO)
        print('colores muestreados (0,84 s):', [hex(c) for c in muestras])
        print('   tint guardado:', hex(est['tint'] or 0),
              '· emisivo:', hex(est['em'] or 0), '· activa:', est['activa'])
        ok_a = (est['activa'] == 'prisma' and est['tint'] == origen['col']
                and est['tintEm'] == origen['em']
                and est['col'] != origen['col'] and distintos >= 2)
        print('A · bola arcoíris aleatoria:',
              'OK ✓' if ok_a else f'FALLO (distintos={distintos})')
        png = base64.b64decode((await page.evaluate(FOTO)).split(',', 1)[1])
        with open(f'{OUT}/_r35_prisma_bola.png', 'wb') as f:
            f.write(png)
        print('   foto de la bola arcoíris:', f'{len(png):,} B')

        # ── E · refresco honesto (re-disparo con la ventana viva) ──
        await page.evaluate(CONCEDER, 'prisma')
        await page.evaluate(TRIGGER, 'prisma')
        est = await page.evaluate(ESTADO)
        ok_e = (est['activa'] == 'prisma' and est['tint'] == origen['col']
                and est['col'] != origen['col'])
        print('E · refresco re-conquista la bola:',
              'OK ✓' if ok_e else f"FALLO ({json.dumps(est)})")

        # ── C · Oscuridad toma la bola (Prisma cede; Oscuridad guarda el ORIGINAL) ──
        await page.evaluate(CONCEDER, 'oscuridad')
        await page.evaluate(TRIGGER, 'oscuridad')
        await page.wait_for_timeout(300)
        est = await page.evaluate(ESTADO)
        ok_c = (est['activa'] == 'oscuridad' and est['tint'] is None
                and est['oscTint'] == origen['col'] and est['col'] != origen['col'])
        print('C · cesión a Oscuridad:',
              'OK ✓' if ok_c else f"FALLO ({json.dumps(est)})")
        await page.evaluate("""() => { const G = window.__PP_GAME || window.__game;
          G._oscuridadT = 0.01; }""")
        await page.wait_for_timeout(250)
        est = await page.evaluate(ESTADO)
        ok_c2 = (est['col'] == origen['col'] and est['oscTint'] is None
                 and (est['em'] == origen['em']))
        print('C · Oscuridad devuelve la bola intacta:',
              'OK ✓' if ok_c2 else f"FALLO ({json.dumps(est)})")

        # ── D · auto-soltado: Onda toma el testigo → el tinte cae SOLO ──
        await page.evaluate(CONCEDER, 'prisma')
        await page.evaluate(TRIGGER, 'prisma')
        await page.wait_for_timeout(200)
        await page.evaluate(CONCEDER, 'onda')
        await page.evaluate(TRIGGER, 'onda')
        await page.wait_for_timeout(300)
        est = await page.evaluate(ESTADO)
        ok_d = (est['activa'] == 'onda' and est['tint'] is None
                and est['col'] == origen['col'] and est['prismaT'] > 0)
        print('D · auto-soltado con Onda viva:',
              'OK ✓' if ok_d else f"FALLO ({json.dumps(est)})")

        # ── B · fin natural: la bola vuelve a SU tinta (Prisma dueño) ──
        await page.evaluate(CONCEDER, 'prisma')
        await page.evaluate(TRIGGER, 'prisma')   # refresh: re-conquista la bola
        await page.evaluate("""() => { const G = window.__PP_GAME || window.__game;
          G._prismaFrame(0.2); G._prismaT = 0.05; }""")   # 1er salto determinista
        pre = await page.evaluate(ESTADO)
        # reloj HONESTO de la casa (el render de SwiftShader es lento): 3
        # frames de 0,2 s por updateMega — el MISMO camino que animate.
        await page.evaluate("""() => { const G = window.__PP_GAME || window.__game;
          for (let i = 0; i < 3; i++) G.updateMega(0.2); }""")
        est = await page.evaluate(ESTADO)
        ok_b = (pre['col'] != origen['col'] and est['tint'] is None
                and est['col'] == origen['col'] and est['em'] == origen['em']
                and est['activa'] != 'prisma')
        print('B · fin natural restaura la bola:',
              'OK ✓' if ok_b else f"FALLO ({json.dumps(est)})")

        print('errores de página:', errs[:5] if errs else 'ninguno')
        await browser.close()

        verdicts = [('A', ok_a), ('B', ok_b), ('C', ok_c and ok_c2),
                    ('D', ok_d), ('E', ok_e)]
        malos = [k for k, v in verdicts if not v]
        print('VEREDICTO r35:', '5/5 OK' if not malos else f'FALLOS: {malos}')
        return 0 if not malos else 1


raise SystemExit(asyncio.run(main()))
