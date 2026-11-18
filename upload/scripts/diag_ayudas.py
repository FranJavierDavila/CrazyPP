#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""diag_ayudas.py · diagnóstico puntual de la física/bote/sprite en dev :3000."""
import asyncio

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'

DIAG = r"""
async () => {
  const G = window.__PP_GAME, T = window.__PP_TRAIN;
  const st = T.__debug.st;
  st.wait = 99; st.feedT = 0;
  const b = G.ball;
  const grp = G.rig.getObjectByName('ppTrainGrp');
  const quad = grp.children.find(m => m.isMesh && m.geometry &&
    m.geometry.type === 'PlaneGeometry');
  const C = quad.position.z + quad.geometry.parameters.height / 2;
  const TOP = quad.position.y;
  const out = { C, TOP, phase: st.phase, live: st.live, active: !!T.__debug };

  // 1) spawnMark DIRECTO (consumidor sin física)
  T.__test.spawnMark({ x: 0.15, y: TOP, z: C - 0.40 }, 0xffe08a);
  await new Promise(r => setTimeout(r, 250));
  out.marksDirect = [...grp.children].filter(o => o.userData &&
    typeof o.userData.ttl === 'number' && o.visible).length;

  // 2) física real: soltar la bola y ver si cae
  const p0 = b.pos.clone(), v0 = b.vel.clone();
  b.pos.set(0.15, TOP + 0.30, C - 0.40);
  b.vel.set(0.25, -2.4, 0.10);
  b.spin.set(0, 0, 0);
  await new Promise(r => setTimeout(r, 120));
  const p1 = { x: +b.pos.x.toFixed(3), y: +b.pos.y.toFixed(3), z: +b.pos.z.toFixed(3) };
  const v1 = { x: +b.vel.x.toFixed(3), y: +b.vel.y.toFixed(3), z: +b.vel.z.toFixed(3) };
  await new Promise(r => setTimeout(r, 500));
  const p2 = { x: +b.pos.x.toFixed(3), y: +b.pos.y.toFixed(3), z: +b.pos.z.toFixed(3) };
  const v2 = { x: +b.vel.x.toFixed(3), y: +b.vel.y.toFixed(3), z: +b.vel.z.toFixed(3) };
  out.fisica = { p0: { x: +p0.x.toFixed(3), y: +p0.y.toFixed(3), z: +p0.z.toFixed(3) },
                 v0: { x: +v0.x.toFixed(2), y: +v0.y.toFixed(2), z: +v0.z.toFixed(2) },
                 p1, v1, p2, v2 };

  // 3) sprite ON directo: ¿cosmeticsTick lo enciende?
  T.__debug.S.fb.spin = 1;
  b.spin.set(0, 0, 20); b.vel.set(1.5, 2.0, -1.5);
  await new Promise(r => setTimeout(r, 350));
  const sp = grp.children.find(o => o.isSprite);
  out.sprite = { vis: sp.visible, op: +sp.material.opacity.toFixed(3),
                 spinNow: +b.spin.lengthSq().toFixed(0),
                 velNow: +b.vel.lengthSq().toFixed(1) };

  // 4) BOTE REAL vía la máquina: modeFeed lanza una bola volando de verdad
  //    (feedToPlayer fija vel real) → bote en campo del jugador (live=1)
  st.live = true; st.shotRec = true;
  T.__test.modeFeed();
  b.spin.set(0, 0, 20);            // efecto real durante el vuelo (sprite)
  await new Promise(r => setTimeout(r, 200));
  const fly = { v: +b.vel.lengthSq().toFixed(1), s: +b.spin.lengthSq().toFixed(0) };
  const sp2 = grp.children.find(o => o.isSprite);
  out.vuelo = { ...fly, sprite: { vis: sp2.visible, op: +sp2.material.opacity.toFixed(3) } };
  await new Promise(r => setTimeout(r, 1100));
  out.marksTrasBote = [...grp.children].filter(o => o.userData &&
    typeof o.userData.ttl === 'number' && o.visible).length;
  out.fisicaTras = { p: { x: +b.pos.x.toFixed(2), y: +b.pos.y.toFixed(2), z: +b.pos.z.toFixed(2) },
                     v: +b.vel.lengthSq().toFixed(1) };
  return out;
};
"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_TRAIN", timeout=45000)
        await page.evaluate("() => window.__PP_TRAIN.startMode(window.__PP_GAME, 't1a')")
        await page.wait_for_timeout(150)
        r = await page.evaluate(DIAG)
        for k, v in r.items():
            print(f'{k}: {v}')
        print('pageerrors:', len(errs), errs[:2])
        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
