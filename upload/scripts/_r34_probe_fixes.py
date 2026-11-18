#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r34 · PRUEBA EN VIVO de las correcciones a los superpoderes de pala:
  A · FX de mesa colgando del this.rig (Red/Elec/Efecto/Portal).
  B · voz del selector disponible para los 14 poderes en ES y EN.
  C · SÚPER ELECTRICIDAD: fin por baja (máx. 1 bola perdida).
  D · retención del rayo: 1 s con halo + mini-rayos y luego estallido.
  E · Prisma: firma arcoíris sólo en la mitad rival.
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

VOZES = """() => {
  const G = window.__PP_GAME || window.__game;
  const ids = ['mega','efecto','iman','portal','clon','red','elec','fenix',
    'crono','oscuridad','prisma','onda','salva','ancla','nada'];
  const out = {};
  for (const id of ids) {
    out[id] = { es: !!G._vozSelFuente(id + '_es'), en: !!G._vozSelFuente(id + '_en') };
  }
  return out;
}"""

AGARRAR = """() => {
  const G = window.__PP_GAME || window.__game;
  const red = G.tableGroup.getObjectByName('ppTableNet');
  const zC = red.position.z;             // DIMS.tableCenterZ (fuente viva)
  G.rules.state = 'rally';
  G.ball.pos.set(0.2, 1.05, zC - 0.6);
  G.ball.vel.set(0.3, -0.5, -1.2);
  if (G.ballMesh) G.ballMesh.visible = true;
  const antes = { scoreP: G.rules.scorePlayer };
  G._elecAgarra();
  const fx = G._elecAgarraFx;
  return {
    ppTransito: G.ball.ppTransito, t: +G._elecAgarraT.toFixed(2),
    pos: G.ball.pos.z.toFixed(2), haloVisible: !!(fx && fx.halo && fx.halo.visible),
    nRayos: fx ? fx.rayos.length : -1, haloParent: fx && fx.halo ? fx.halo.parent === G.rig : null,
    bolaVista: G.ballMesh.visible, msg: G.rules.message, antes,
  };
}"""

FRAME = """(dt) => {
  const G = window.__PP_GAME || window.__game;
  G._elecFrame(dt);
  return { t: +G._elecAgarraT.toFixed(2), elecT: +G._elecT.toFixed(2) };
}"""

ESTADO_FIN = """(antes) => {
  const G = window.__PP_GAME || window.__game;
  const fx = G._elecAgarraFx;
  return {
    scoreP: G.rules.scorePlayer, antes,
    estado: G.rules.state, msg: G.rules.message,
    elecT: G._elecT, elecFxOn: G._elecFxOn,
    agarraT: G._elecAgarraT, ppTransito: G.ball.ppTransito,
    haloVisible: !!(fx && fx.halo && fx.halo.visible),
    bolaVista: G.ballMesh.visible, velY: +G.ball.vel.y.toFixed(2),
  };
}"""

LIBERAR = """() => {
  const G = window.__PP_GAME || window.__game;
  G._elecFin();
  const fx = G._elecAgarraFx;
  return { t: G._elecAgarraT, ppTransito: G.ball.ppTransito,
           haloVisible: !!(fx && fx.halo && fx.halo.visible),
           bolaVista: G.ballMesh.visible };
}"""

PRISMA = """() => {
  const G = window.__PP_GAME || window.__game;
  const zC = G.tableGroup.getObjectByName('ppTableNet').position.z;
  G.ball.pos.set(0.1, 1.0, zC - 0.5);
  const rival = G._trailFirmaPoder();
  G.ball.pos.set(0.1, 1.0, zC + 0.5);
  const propio = G._trailFirmaPoder();
  return { rival: rival === G._trailFirmaPoder.r ? 'arr' : !!rival,
           propioArr: propio === null };
}"""

PADRES = """() => {
  const G = window.__PP_GAME || window.__game;
  const r = {};
  r.redCuerpo = !!(G._redFx && G._redFx.cuerpo && G._redFx.cuerpo.parent === G.rig);
  r.redRiel = !!(G._redFx && G._redFx.riel && G._redFx.riel.parent === G.rig);
  r.elecNiebla = !!(G._elecFx && G._elecFx.niebla[0] && G._elecFx.niebla[0].parent === G.rig);
  r.elecRayo = !!(G._elecFx && G._elecFx.rayos[0] && G._elecFx.rayos[0].parent === G.rig);
  r.elecMetal = !!(G._elecFx && G._elecFx.metales[0] && G._elecFx.metales[0].parent === G.rig);
  r.efectoBote = !!(G._efectoBoteFx && G._efectoBoteFx.parent === G.rig);
  r.portalSprite = !!(G._portalSpriteA && G._portalSpriteA.parent === G.rig);
  r.redArcos = !!(G._redFx && G._redFx.arcos[0] && G._redFx.arcos[0].parent === G.rig);
  return r;
}"""

FOTO = """() => {
  const G = window.__PP_GAME || window.__game;
  const cam = G.camera.clone();
  cam.aspect = 16 / 9; cam.fov = 75; cam.updateProjectionMatrix();
  const V = G.camera.position.constructor;
  cam.position.set(0.4, 1.35, 0.6);
  cam.lookAt(new V(G._elecAgarraPos.x, G._elecAgarraPos.y, G._elecAgarraPos.z));
  G.renderer.render(G.scene, cam);
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

        # ── B · voces del selector (14 poderes + nada) ──
        vozes = await page.evaluate(VOZES)
        faltan = [f'{k}:{v["es"]}/{v["en"]}' for k, v in vozes.items()
                  if not (v['es'] and v['en'])]
        print('B · voces selector:', 'TODAS OK (15 × ES/EN)' if not faltan
              else f'FALTAN: {faltan}')

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

        # ── A · padres de los FX (red + elec + efecto + portal) ──
        for pid in ['red', 'elec', 'efecto', 'portal']:
            await page.evaluate(CONCEDER, pid)
            await page.evaluate(TRIGGER, pid)
        await page.wait_for_timeout(1200)   # precaliente del portal puede tardar
        await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          try { G._efectoBotePrewarm(); } catch (e1) {}
          try { G._buildPortalImg(); } catch (e2) {}
        }""")
        pad = await page.evaluate(PADRES)
        print('A · padres en rig:', json.dumps(pad))
        todo_rig = all(pad.values())
        print('   →', 'TODOS EN EL RIG ✓' if todo_rig else '¡HAY FX FUERA DEL RIG!')

        # ── D + C · agarre → 1 s → estallido → fin por baja ──
        est = await page.evaluate(AGARRAR)
        print('D · agarre:', json.dumps(est, ensure_ascii=False))
        png = base64.b64decode((await page.evaluate(FOTO)).split(',', 1)[1])
        with open(f'{OUT}/_r34_elec_agarre.png', 'wb') as f:
            f.write(png)
        print('   foto del agarre:', f'{len(png):,} B')
        await page.evaluate(FRAME, 0.6)
        await page.evaluate(FRAME, 0.6)
        fin = await page.evaluate(ESTADO_FIN, est['antes'])
        ok_c = fin['elecT'] == 0 and fin['estado'] == 'point' and fin['scoreP'] > fin['antes']['scoreP']
        print('C · fin por baja:', json.dumps(fin, ensure_ascii=False))
        print('   →', 'TORMENTA CERRADA TRAS LA BAJA ✓' if ok_c else '¡LA TORMENTA SIGUE VIVA!')

        # ── D-bis · salida de emergencia libera el agarre ──
        await page.evaluate(CONCEDER, 'elec')
        await page.evaluate(TRIGGER, 'elec')
        await page.evaluate(AGARRAR)
        lib = await page.evaluate(LIBERAR)
        print('D-bis · _elecFin libera el agarre:', json.dumps(lib))

        # ── E · prisma por campos ──
        await page.evaluate(CONCEDER, 'prisma')
        await page.evaluate(TRIGGER, 'prisma')
        pr = await page.evaluate(PRISMA)
        print('E · prisma:', json.dumps(pr))
        print('   →', 'SÓLO CAMPO RIVAL ✓' if pr['propioArr'] else '¡SE VE EN NUESTRO CAMPO!')

        print('errores de página:', errs[:5] if errs else 'ninguno')
        await browser.close()


asyncio.run(main())
