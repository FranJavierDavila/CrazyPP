#!/usr/bin/env python3
"""Probe del check 'rebota ENTRE ELLAS' (gravedad cero): geometría y evolución real."""
import asyncio
from playwright.async_api import async_playwright

URL = 'http://localhost:3000/game.html'

JS = r"""() => {
  const G = window.__PP_GAME;
  const mod = G.champs.moduleIfLoaded('estacion_orbital');
  const ctrl = mod.controller;
  ctrl._poderClear();
  const def = { kind: 'custom', name: 'Gravedad cero', duration: 8 };
  const rally0 = G.rules.state;
  const ball = G.ball;
  ball.pos.set(0, 0.95, -0.7);
  ball.vel.set(0.5, 0, 0.5);
  ctrl._poderArrancar(def);
  G.rules.state = 'rally';
  const motas = ctrl.motas.map(m => ({x: +m.x.toFixed(2), y: +m.y.toFixed(2), z: +m.z.toFixed(2), op: +m.s.material.opacity.toFixed(2)}));
  const out = { _t: ctrl._t, nMotas: ctrl.motas.length, motas, tray: [] };
  out.tgt0 = ctrl._act.tgt;
  for (let i = 0; i < 300; i++) {
    ctrl._ceroStep(1 / 60, ctrl._act, ball, true);
    ball.pos.addScaledVector(ball.vel, 1 / 60);
    if (i % 50 === 49) {
      const tm = ctrl.motas[ctrl._act.tgt];
      const dl = Math.hypot(tm.x - ball.pos.x, tm.y - ball.pos.y, tm.z - ball.pos.z);
      out.tray.push({ i: i + 1, tgt: ctrl._act.tgt, dl: +dl.toFixed(3),
                      pos: [+ball.pos.x.toFixed(2), +ball.pos.y.toFixed(2), +ball.pos.z.toFixed(2)],
                      v: +ball.vel.length().toFixed(2) });
    }
  }
  out.cambios = 0; let lastT = out.tgt0;
  out.vFin = +ball.vel.length().toFixed(2);   // discriminador: 4.4 = atracción viva; 0.707 = ceroStep retorna pronto
  G.rules.state = rally0;
  return out;
}"""

JS2 = r"""() => {
  // segunda pasada idéntica a la del QA real (conteo exacto de cambios)
  const G = window.__PP_GAME;
  const mod = G.champs.moduleIfLoaded('estacion_orbital');
  const ctrl = mod.controller;
  ctrl._poderClear();
  const def = { kind: 'custom', name: 'Gravedad cero', duration: 8 };
  const rally0 = G.rules.state;
  const ball = G.ball;
  ball.pos.set(0, 0.95, -0.7);
  ball.vel.set(0.5, 0, 0.5);
  ctrl._poderArrancar(def);
  G.rules.state = 'rally';
  for (let i = 0; i < 10; i++) ctrl._ceroStep(1 / 60, ctrl._act, ball, true);
  const motas = ctrl.motas.map(m => ({x: +m.x.toFixed(2), y: +m.y.toFixed(2), z: +m.z.toFixed(2)}));
  let cambios = 0, lastT = ctrl._act.tgt; const dls = [];
  for (let i = 0; i < 300; i++) {
    ctrl._ceroStep(1 / 60, ctrl._act, ball, true);
    ball.pos.addScaledVector(ball.vel, 1 / 60);
    if (i % 30 === 29) {
      const tm = ctrl.motas[ctrl._act.tgt];
      dls.push(+Math.hypot(tm.x - ball.pos.x, tm.y - ball.pos.y, tm.z - ball.pos.z).toFixed(3));
    }
    if (ctrl._act.tgt !== lastT) { cambios++; lastT = ctrl._act.tgt; }
  }
  G.rules.state = rally0;
  return { cambios, motas, dls, _t: +ctrl._t.toFixed(1) };
}"""

async def main():
    async with async_playwright() as pw:
        b = await pw.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 800})
        await pg.goto(URL, wait_until='networkidle')
        await pg.wait_for_timeout(1500)
        await pg.evaluate("""async () => {
          const G = window.__PP_GAME;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 4000));
        }""")
        r1 = await pg.evaluate(JS)
        print('— pasada 1 (geometría):')
        print(f"  _t={r1['_t']} nMotas={r1['nMotas']} tgt0={r1['tgt0']}")
        for m in r1['motas'][:14]:
            print(f"    mota {m}")
        for t in r1['tray']:
            print(f"    i={t['i']:3d} tgt={t['tgt']} dl={t['dl']} pos={t['pos']} v={t['v']}")
        r2 = await pg.evaluate(JS2)
        print('— pasada 2 (réplica del QA):')
        print(f"  cambios={r2['cambios']} _t={r2['_t']}")
        print(f"  dls cada 30 pasos: {r2['dls']}")
        await b.close()

asyncio.run(main())
