#!/usr/bin/env python3
"""Sonda de los 2 fixes v3.5.0: Hall sin arrastres + pala ambidiestra en el
PRO TRAINING. Uso: python3 scripts/probe_fixes_v350.py"""
import asyncio
import json

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        await page.goto(BASE + '/game.html', wait_until='networkidle')
        res = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const V3 = G.camera.position.constructor;
          const out = {};
          /* ── FIX 2 · HALL SIN ARRASTRES ───────────────────────────── */
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          // entrar al REACTOR DE IMPULSO (ahora etapa 2) y salir al hall en plena prueba
          ctrl.stage = 1;
          ctrl._arrancarImpulso(ctrl._etapa());
          for (let i = 0; i < 45; i++) ctrl.impulso.step(0.1);   // intro → oleada 1
          out.impulsoVivo = ctrl.impulso.active && ctrl.impulso.phase === 'play';
          out.salaImpulso = !G.roomGroup.visible && !G.tableGroup.visible;
          // …y AHORA el dueño sale al Hall (goHomeHall = botón ⌂ / prompt B)
          G.goHomeHall();
          out.enHall = G.inHall;
          out.mesaOculta = !G.tableGroup.visible && !G.scoreboardGroup.visible;
          out.salaNuclearFuera = !G.roomGroup.visible;
          out.estadoSaque = G.rules.state === 'serve';
          out.bolaEnMano = G.ballMesh.visible;      // la bola se lleva en la mano libre
          out.bolaQuieta = G.ball.vel.lengthSq() === 0;
          out.bolaBase = Math.abs(G.ball.pos.y - 0.78) < 0.2;
          out.bolaEscala = G.ballMesh.scale.x === 1;
          out.sinGrupoImpulso = !ctrl.impulso.grp.visible && !ctrl.impulso.baseGrp.visible;
          out.sinHudReactor = !ctrl.reactor.hudGroup.visible;
          // en VR (presenting) el estado 'serve' pone la bola EN LA MANO LIBRE:
          // la cinemática de mano es la que evita la bola flotante (holdLock)
          out.holdLockSirve = !!G.rules && G.rules.state === 'serve';
          /* ── FIX 1 · PALA EN CUALQUIER MANO (PRO TRAINING) ────────── */
          // salida del hall a la cancha y arranque de un modo de entrenamiento
          G.exitHall();
          const TRN = window.__PP_TRAIN;
          TRN.startMode(G, 't1a');
          out.trainV3 = !!G.trainV3;
          out.enCalib = !!G.calib;                  // los modos viven en calib
          out.condicionSwap = !!(!G.calib || G.trainV3);   // rama nueva activa (truthy)
          // swap real (lo que hace A/X al pulsarse)
          G.manualHand = true;
          G.setPaddleHand(1);
          out.swapeaDerecha = G.paddleHand === 1;
          out.montaVisibles = G.paddleMounts[1].visible && !G.paddleMounts[0].visible;
          out.ballHandSigue = G.ballHand === 0;
          G.setPaddleHand(0);
          out.vuelveZurda = G.paddleHand === 0 && G.ballHand === 1;
          TRN.stopMode(G);
          return out;
        }""")
        print(json.dumps(res, ensure_ascii=False, indent=1))
        print('pageerrors:', errors[:4])
        await browser.close()

asyncio.run(main())
