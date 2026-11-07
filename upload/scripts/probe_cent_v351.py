#!/usr/bin/env python3
"""Sonda 2: flujo EXACTO del QA del escudo hasta el rebote del Centinela."""
import asyncio
import json

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto('http://localhost:3000/game.html', wait_until='networkidle')
        await page.wait_for_timeout(1200)
        out = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const V3 = G.camera.position.constructor;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const E = ctrl.escudo;
          ctrl.stage = 3;
          ctrl._arrancarEscudo(ctrl._etapa());
          for (let i = 0; i < 40; i++) E.step(0.1);
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true; pad.cooldown = 0; pad.serveFlight = false; pad.extraReach = 0;
          pad.who = 'player'; pad.index = G.paddleHand;
          pad.normal = new V3(0, 0, 1); pad.up = new V3(0, 1, 0); pad.right = new V3(1, 0, 0);
          pad.prevNormal = pad.normal.clone(); pad.prevRight = pad.right.clone();
          pad.prevUp = pad.up.clone();
          pad.omega = pad.omega || new V3(); pad.omega.set(0, 0, 0);
          pad.vel = pad.vel || new V3();
          const BCU = (window.__ppDebug.DIMS.bladeCenterUp) || 0.14;
          const BC = new V3(0.28, 1.2, 0);
          pad.pos.copy(BC).addScaledVector(pad.up, -BCU);
          pad.prev.copy(pad.pos);
          const d0 = E.drones.find(d => d.alive);
          d0.shootT = 0; E.step(0.05); d0.chargeT = 0.01; E.step(0.05);
          const orbe = E.orbes.find(o => o.alive && o.owner === 'enemigo');
          G.camera.getWorldPosition(E._tmpC);
          // golpeo vía barrido CCD
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, 5.5); orbe.spin.set(0, 0, 0);
          pad.vel.set(0, 0, -3);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          const golpeo = orbe.alive && orbe.owner === 'jugador' && orbe.vel.z < 0;
          const limpio = orbe.clean === true && E.sobrecarga > 0;
          E.sobrecarga = 1;
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, 5.5);
          orbe.owner = 'enemigo'; orbe.perf = false; orbe.clean = false;
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          const perforante = orbe.perf === true && E.sobrecarga === 0;
          // destrucción de dron
          orbe.mesh.position.copy(d0.pos).add(new V3(0, 0, 0.15));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, -6);
          orbe.owner = 'jugador'; orbe.perf = false;
          E._orbesStep(0.03);
          const dronCae = !d0.alive;
          for (const dd of E.drones) if (dd.alive) E._dronMuere(dd);
          const inter = E.phase === 'inter';
          for (let i = 0; i < 60; i++) E.step(0.1);
          const fase2 = E.fase === 1 && E.drones.filter(d => d.alive).length === 4 && E.centOn;
          // EXACTAMENTE el bloque del QA
          const o2 = E.orbes.find(o => !o.alive);
          const pre2 = o2 ? { tipo: o2.tipo, r: o2.r, fuse: o2.fuse,
                              perf: o2.perf, alive: o2.alive } : null;
          o2.alive = true; o2.owner = 'jugador'; o2.tipo = 'std'; o2.r = 0.05;
          o2.mesh.visible = true; o2.glow.visible = true; o2.pos = o2.mesh.position;
          o2.mesh.position.set(0, E.cent.position.y, E.cent.position.z + 0.55);
          o2.prev.copy(o2.mesh.position); o2.vel.set(0, 0, -6);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          const reboteCent = o2.alive && o2.owner === 'enemigo' && o2.rebote;
          const dep = { o2alive: o2.alive, owner: o2.owner, rebote: o2.rebote,
                        z: +o2.mesh.position.z.toFixed(2),
                        velLen: +o2.vel.length().toFixed(2),
                        centOn: E.centOn, centSobreT: E.centSobreT,
                        centro: E.cent.position.toArray() };
          return { golpeo, limpio, perforante, dronCae, inter, fase2, pre2,
                   reboteCent, dep };
        }""")
        print(json.dumps(out, indent=2, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
