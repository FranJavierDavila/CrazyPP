#!/usr/bin/env python3
"""Sonda en vivo de la etapa ESCUDO DE PALA (V3.5.0-ESC1).
Uso: python3 scripts/probe_escudo.py"""
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
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          const V3 = G.camera.position.constructor;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          if (!ctrl || !ctrl.escudo) return { error: 'sin ctrl.escudo' };
          const E = ctrl.escudo;
          const out = {};
          // puente CCD presente
          out.puenteCCD = typeof window.__PP_PADDLE_SWEEP === 'function';
          // arranque forzado de la etapa 4 (escudo)
          ctrl.stage = 3;
          ctrl._arrancarEscudo(ctrl._etapa());
          out.arrancado = E.active && E.phase === 'prep';
          out.salaPropia = E.grp.visible && !G.roomGroup.visible && !G.tableGroup.visible;
          out.sinBola = !G.ballMesh.visible;
          out.sinRival = !ctrl.rivalMesh.visible;
          out.pantalla = E.panMesh.visible;
          // prep 3 s → fase 1
          for (let i = 0; i < 40; i++) E.step(0.1);
          out.fase1 = E.phase === 'combate' && E.fase === 0;
          out.drones3 = E.drones.filter(d => d.alive).length === 3;
          // PALA FANTASMA con basis completa (el barrido CCD la exige)
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true; pad.cooldown = 0;
          pad.serveFlight = false; pad.extraReach = 0;
          pad.who = 'player'; pad.index = G.paddleHand;
          pad.normal = new V3(0, 0, 1); pad.up = new V3(0, 1, 0); pad.right = new V3(1, 0, 0);
          pad.prevNormal = pad.normal.clone(); pad.prevRight = pad.right.clone();
          pad.prevUp = pad.up.clone();
          pad.omega = pad.omega || new V3(); pad.omega.set(0, 0, 0);
          pad.vel = pad.vel || new V3();
          const BCU = (window.__ppDebug && window.__ppDebug.DIMS.bladeCenterUp) || 0.14;
          const BC = new V3(0.28, 1.2, 0);            // centro de la hoja deseado
          pad.pos.copy(BC).addScaledVector(pad.up, -BCU);   // grip = hoja − up·BCU
          pad.prev.copy(pad.pos);
          // DISPARO de un dron: telegrafía (en _dronStep) + orbe enemigo
          const d0 = E.drones.find(d => d.alive);
          d0.shootT = 0; E.step(0.05);
          d0.chargeT = 0.01; E.step(0.05);
          const orbe = E.orbes.find(o => o.alive && o.owner === 'enemigo');
          out.orbeEnemigo = !!orbe;
          if (!orbe) return out;
          out.orbeVel = +orbe.vel.length().toFixed(1);
          // objetivo fuera de la zona segura de cabeza
          G.camera.getWorldPosition(E._tmpC);
          const dir = orbe.vel.clone().normalize();
          const t = Math.max(0, E._tmpC.clone().sub(orbe.mesh.position).dot(dir));
          const cerca = orbe.mesh.position.clone().addScaledVector(dir, t).distanceTo(E._tmpC);
          out.zonaSegura = cerca > 0.35;
          // GOLPEO con el barrido CCD del núcleo: orbe hacia la cara de la hoja
          // (telemetría del barrido para diagnóstico)
          const dbg = (() => {
            const evs = [];
            const probe = { pos: BC.clone().add(new V3(0, 0, -0.03)), prev: BC.clone().add(new V3(0, 0, -0.2)),
              vel: new V3(-0.3, 0, 4.5), spin: new V3() };
            const hit = window.__PP_PADDLE_SWEEP(probe, probe.prev, pad, evs);
            return { hit, nEv: evs.length, ev0: evs[0] ? { speed: +evs[0].speed.toFixed(2), pz: +evs[0].pos.z.toFixed(3) } : null,
              D: { br: (window.__ppDebug.DIMS.bladeRadius), ha: (window.__ppDebug.DIMS.hitAssistRadius),
                   hT: window.__ppDebug.ccdTune.bladeHalfT } };
          })();
          out.dbg = dbg;
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position);
          orbe.vel.set(-0.3, 0, 4.5);
          orbe.spin.set(0, 0, 0);
          pad.vel.set(0, 0, -2.0);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.golpeo = orbe.alive && orbe.owner === 'jugador';
          out.velDevuelta = orbe.alive ? +orbe.vel.length().toFixed(1) : 0;
          out.haciaEnemigos = orbe.alive ? orbe.vel.z < 0 : null;
          if (!orbe.alive) return out;
          // GOLPE LIMPIO: centro de la hoja + cierre ≥4 m/s
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position);
          orbe.vel.set(0, 0, 5.5);
          orbe.spin.set(0, 0, 0);
          orbe.owner = 'enemigo'; orbe.clean = false; orbe.perf = false;
          pad.vel.set(0, 0, -3.0);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.limpio = orbe.clean === true;
          out.sobrecarga = +E.sobrecarga.toFixed(2);
          // SOBRECARGA al 100 % + golpe firme → ORBE PERFORANTE
          E.sobrecarga = 1;
          orbe.mat.color.setHex(0x4db8ff); orbe.mat.emissive.setHex(0x4db8ff);
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position);
          orbe.vel.set(0, 0, 5.5);
          orbe.owner = 'enemigo'; orbe.perf = false; orbe.clean = false;
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.perforante = orbe.perf === true;
          out.sobrecargaReseteada = E.sobrecarga === 0;
          // DESTRUCCIÓN de un dron con el orbe devuelto
          orbe.mesh.position.copy(d0.pos).add(new V3(0, 0, 0.15));
          orbe.prev.copy(orbe.mesh.position);
          orbe.vel.set(0, 0, -6);
          orbe.owner = 'jugador'; orbe.perf = false;
          E._orbesStep(0.03);
          out.dronDestruido = !d0.alive;
          out.enemigosRestantes = E.drones.filter(dd => dd.alive).length;
          // COMPLETAR fase 1 → interludio
          for (const dd of E.drones) if (dd.alive) E._dronMuere(dd);
          out.interludio = E.phase === 'inter' && E.phaseT > 0;
          for (let i = 0; i < 60; i++) E.step(0.1);
          out.fase2 = E.phase === 'combate' && E.fase === 1;
          out.fase2Enemigos = E.drones.filter(d => d.alive).length === 4 && E.centOn;
          // CENTINELA: el escudo REBOTA el orbe devuelto (+10 %, sesgo jugador)
          const c0 = E.cent;
          const orbe2 = E.orbes.find(o => !o.alive);
          if (!orbe2) return out;
          orbe2.alive = true; orbe2.owner = 'jugador'; orbe2.tipo = 'std'; orbe2.r = 0.05;
          orbe2.mesh.visible = true; orbe2.glow.visible = true;
          orbe2.mesh.position.set(0, c0.position.y, c0.position.z + 0.55);
          orbe2.prev.copy(orbe2.mesh.position);
          orbe2.vel.set(0, 0, -6);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.escudoRebota = orbe2.alive && orbe2.owner === 'enemigo' && orbe2.rebote;
          out.velGanada = orbe2.alive ? +orbe2.vel.length().toFixed(1) : 0;
          // rally: 5 devoluciones → escudo abierto; núcleo expuesto → muere
          for (let k = 0; k < 5; k++) E._rallySube();
          out.sobreCalienta = E.centSobreT > 0;
          orbe2.mesh.position.copy(c0.position);
          orbe2.prev.copy(orbe2.mesh.position);
          orbe2.vel.set(0, 0, -4);
          orbe2.owner = 'jugador'; orbe2.rebote = false;
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.03);
          out.centinelaMuerto = E.centDead && !E.centOn;
          for (const dd of E.drones) if (dd.alive) E._dronMuere(dd);
          out.inter2 = E.phase === 'inter';
          for (let i = 0; i < 60; i++) E.step(0.1);
          out.fase3 = E.phase === 'combate' && E.fase === 2 && E.jefeOn;
          for (let i = 0; i < 50; i++) E.step(0.1);
          out.estadoPreCanon = E.phase + '/' + E.fase + '/entrada=' + E.jefeEntrT.toFixed(2) + '/canon=' + E.jefeCanon;
          out.canonActivo = E.jefeCanon >= 0 && E.canones[E.jefeCanon].tip.material.emissiveIntensity > 1;
          if (E.jefeCanon >= 0) {
            const cAct = E.canones[E.jefeCanon];
            E._jefeCanonDano(cAct, 1, false);
            out.hpTrasGolpe = cAct.hp === 2;
            E._jefeCanonDano(cAct, 2, true);
            out.hpTrasLimpio = cAct.hp === 0 && cAct.dead;
            out.canonSiguiente = E.canones.filter(c => !c.dead).length === 2;
          }
          // barrera: orbe enemigo llega → daño 10 + onda en el punto
          const orbe3 = E.orbes.find(o => !o.alive);
          if (!orbe3) return out;
          orbe3.alive = true; orbe3.owner = 'enemigo'; orbe3.tipo = 'std'; orbe3.r = 0.05;
          orbe3.mesh.visible = true; orbe3.glow.visible = true;
          orbe3.mesh.position.set(0.4, 1.4, 1.5);
          orbe3.prev.copy(orbe3.mesh.position);
          orbe3.vel.set(0, 0, 3);
          const hull0 = E.hull;
          E._orbesStep(0.2);
          out.barreraDano = E.hull === hull0 - 10;
          out.ondaVisible = E.ondas.some(w => w.m.visible);
          // DERROTA: hull a 0 → astro ríe → regreso a la etapa 1
          E._cascoDano(200);
          out.derrota = E.phase === 'result' && E._win === false;
          out.astroRie = ctrl.rivalMesh.visible && ctrl._rivalEstado === 'laughing';
          for (let i = 0; i < 60; i++) E.step(0.1);
          out.regresa = ctrl.stage === 3 && ctrl.state === 'sala' && !E.active &&
                        G.roomGroup.visible && G.tableGroup.visible && G.ballMesh.visible;
          out.rivalHome = Math.abs(ctrl.rivalMesh.position.x - 1.26) < 1e-3 &&
                          Math.abs(ctrl.rivalMesh.position.z - (-3.82)) < 1e-3;
          return out;
        }""")
        print(json.dumps(esc, ensure_ascii=False, indent=1))
        print('pageerrors:', errors[:4])
        await browser.close()

asyncio.run(main())
