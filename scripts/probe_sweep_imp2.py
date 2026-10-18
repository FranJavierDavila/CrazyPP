#!/usr/bin/env python3
"""Sonda del golpeo CCD en el reactor (por qué no libera la bola)."""
import asyncio

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://localhost:3000/game.html', wait_until='networkidle')
        await page.wait_for_timeout(1200)
        out = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const V3 = G.ball.vel.constructor;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 4500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl.stage = 1;
          ctrl._arrancarImpulso(ctrl._etapa());
          const I = ctrl.impulso;
          for (let i = 0; i < 45; i++) I.step(0.1);
          // congelar el step del juego para no interferir
          I.active = false;
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true; pad.cooldown = 0; pad.serveFlight = false; pad.extraReach = 0;
          pad.who = 'player'; pad.index = G.paddleHand;
          pad.normal = new V3(0, 0, 1); pad.up = new V3(0, 1, 0); pad.right = new V3(1, 0, 0);
          pad.prevNormal = pad.normal.clone(); pad.prevRight = pad.right.clone();
          pad.prevUp = pad.up.clone();
          pad.omega = pad.omega || new V3(); pad.omega.set(0, 0, 0);
          pad.vel = new V3(0, 0, -2);
          const BCU = window.__ppDebug.DIMS.bladeCenterUp || 0.14;
          I.ballState = 'hold'; I._ballDisponible(0);
          I._ballStep(0.016);          // coloca la bola en el bote
          const bp = G.ball.pos.clone();
          pad.pos.copy(bp).addScaledVector(pad.up, -BCU);
          pad.prev.copy(pad.pos);
          G.ball.vel.set(0, -0.5, 0);
          const evts = [];
          const prevC = bp.clone();
          G.ball.vel.set(0, -0.5, 0);
          const hit = window.__PP_PADDLE_SWEEP(G.ball, prevC, pad, evts);
          return {
            ballPos: bp.toArray().map(v => +v.toFixed(3)),
            padPos: pad.pos.toArray().map(v => +v.toFixed(3)),
            hit, evts: evts.length,
            ev: evts.length ? { pos: evts[evts.length - 1].pos.toArray().map(v => +v.toFixed(2)),
                                speed: evts[evts.length - 1].speed } : null,
            velTras: G.ball.vel.toArray().map(v => +v.toFixed(2)),
            dims: { bladeR: window.__ppDebug.DIMS.bladeRadius,
                    assist: window.__ppDebug.DIMS.hitAssistRadius,
                    BCU },
          };
        }""")
        for k, v in out.items():
            print(k, '=', v)
        await browser.close()

asyncio.run(main())
