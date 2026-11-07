#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r64 · debug fino del paso 4 (profesor + devoluciones)."""
import asyncio

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

DBG = """async () => {
  const THREE = await import('three');
  const T = window.__PP_TUT;
  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  const G = {
    net: { online: false }, champs: null,
    trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
    rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
      startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
    ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
    renderer: { xr: { isPresenting: true } },
    controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
    paddleHand: 1, ballHand: 0, tossed: false, mode: 'match',
    sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
    audio: { playOsc: () => {}, announce: () => {}, serve: () => {} },
    haptic: () => {},
    resetToss() { this.tossed = false; },
    tossFromHand(i, a) { this.tossed = true; },
    feedPracticeBall() { this.__feeds = (this.__feeds || 0) + 1; },
    exitHall() {}, enterCalib() { this.calib = true; },
    exitCalib() { this.calib = false; }, closeMenu() {}, goHomeHall() { return true; },
    toggleMenu() {}, anchorMenu() {}, drawMenu() {},
    hideInstrucciones() {}, _instr: null,
    menuOpen: false, menuPage: 'main',
    calibPanel: { group: { visible: true } },
    confettiBurst: 0,
    rig: new THREE.Group(),
  };
  T.start(G);
  // avanza hasta paso 4 rápido: 0→1→2 (vaivén) → 3 (3 saques) → 4
  T.onTrigger(0); T.onTrigger(0);
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);
  for (let i = 0; i < 8; i++) T.tick(0.1);
  const log = [];
  const saca = () => {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016); T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  };
  saca(); saca(); saca();
  let e = T.estado();
  log.push('pre-loop: paso=' + e.paso + ' saq=' + e.saq + ' hits=' + e.hitCount + ' fase=' + e.fase + ' feeds=' + (G.__feeds || 0));
  for (let i = 0; i < 3; i++) {
    G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
    T.tick(0.016);
    e = T.estado();
    log.push('iter' + i + ' post-golpe: hits=' + e.hitCount + ' fase=' + e.fase + ' ball.z=' + G.ball.pos.z.toFixed(2) + ' vz=' + G.ball.vel.z.toFixed(2));
    G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);
    T.tick(0.016);
    e = T.estado();
    log.push('iter' + i + ' post-bote: hits=' + e.hitCount + ' fase=' + e.fase + ' ball.vz=' + G.ball.vel.z.toFixed(2) + ' vy=' + G.ball.vel.y.toFixed(2));
    G.ball.vel.y = 0.4;
    T.tick(0.016);
    e = T.estado();
    log.push('iter' + i + ' post-profe: hits=' + e.hitCount + ' fase=' + e.fase + ' ball.vz=' + G.ball.vel.z.toFixed(2) + ' vzsign=' + Math.sign(G.ball.vel.z));
  }
  return log;
}"""


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(900)
        for line in await page.evaluate(DBG):
            print(' ', line)
        if errs:
            print('PAGEERRORS:', errs[:3])
        await browser.close()

asyncio.run(main())
