#!/usr/bin/env python3
"""SONDEO del golpeo real del reactor (capa F · qa_imp2_v351) — ronda 5.

Reproduce el bloque del golpeo de qa_imp2_v351 N veces en UNA sesión y mide
la DISTRIBUCIÓN del resultado (vel total, vel.y, liberada, subio) con la fase
del bote-en-espera variando entre muestras (como el RAF entre evaluaciones).
Si el margen sobre los umbrales (vel ≥ 2.9 · vel.y ≥ 0.39) es fino, ahí vive
el flake observado en la certificación del deploy (65/66).

Uso: python3 scripts/sondea_golpeo_imp2.py [N]
"""
import asyncio
import statistics
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
PIN = '--pin' in sys.argv
BASE = 'http://localhost:3000'

from playwright.async_api import async_playwright  # noqa: E402


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        await page.goto(BASE + '/game.html', wait_until='networkidle')

        # montaje idéntico al bloque del QA: launch (import dinámico) + espera
        await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          G.champs.launch('estacion_orbital');
          for (let i = 0; i < 100; i++) {
            if (G.champs.moduleIfLoaded('estacion_orbital')) break;
            await new Promise(r => setTimeout(r, 100));
          }
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl.stage = 1;
          ctrl._arrancarImpulso(ctrl._etapa());
          await new Promise(r => setTimeout(r, 500));
          const I = ctrl.impulso;
          for (let i = 0; i < 45; i++) I.step(0.1);
        }""")

        muestras = await page.evaluate("""async (arg) => {
          const [N, pin] = arg;
          window.__SONDEO_PIN = pin;
          const G = window.__PP_GAME;
          const V3 = G.camera.position.constructor;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const I = ctrl.impulso;
          const pad = G.controllerPaddles[G.paddleHand];
          const BCU = window.__ppDebug.DIMS.bladeCenterUp || 0.14;
          const out = [];
          for (let k = 0; k < N; k++) {
            // entre muestras: el RAFbotea la bola en hold (fase distinta cada vez)
            await new Promise(r => setTimeout(r, 40 + Math.floor(Math.random() * 160)));
            I.ballState = 'hold'; I.graceT = 0; I._cdT = 0;
            I._ballDisponible(0);
            if (window.__SONDEO_PIN) {
              // candado determinista: bola en el punto de REPOSO del hold
              // (pp=0 de la fórmula de _ballStep: baseTopY + r + 0.015)
              G.ball.pos.set(0, I._baseTopY() + 0.035, -0.55);
              if (G.ball.__exPrev) G.ball.__exPrev.copy(G.ball.pos);
            }
            const yEntrada = G.ball.pos.y;
            pad.active = true; pad.cooldown = 0; pad.serveFlight = false; pad.extraReach = 0;
            pad.who = 'player'; pad.index = G.paddleHand;
            pad.normal = new V3(0, 0, 1); pad.up = new V3(0, 1, 0); pad.right = new V3(1, 0, 0);
            pad.prevNormal = pad.normal.clone(); pad.prevRight = pad.right.clone();
            pad.prevUp = pad.up.clone();
            pad.omega = pad.omega || new V3(); pad.omega.set(0, 0, 0);
            pad.vel = pad.vel || new V3();
            pad.vel.set(0, 0, -2);
            pad.pos.copy(G.ball.pos).addScaledVector(pad.up, -BCU);
            pad.prev.copy(pad.pos);
            G.ball.vel.set(0, -0.5, -1.5);
            I._fisica(0.0125, true);
            out.push({
              k,
              yEntrada: +yEntrada.toFixed(4),
              x: +G.ball.pos.x.toFixed(3), z: +G.ball.pos.z.toFixed(3),
              liberada: I.ballState === 'play',
              vel: +G.ball.vel.length().toFixed(3),
              velY: +G.ball.vel.y.toFixed(4),
              subio: G.ball.vel.y >= 0.39,
            });
            // devolver la bola al hold para la siguiente muestra
            I.ballState = 'hold';
          }
          return out;
        }""", [N, PIN])

        await browser.close()

    print(f"modo: {'PIN (candado determinista)' if PIN else 'libre (como el QA)'}")
    vel = [m['vel'] for m in muestras]
    velY = [m['velY'] for m in muestras]
    ys = [m['yEntrada'] for m in muestras]
    noLib = sum(1 for m in muestras if not m['liberada'])
    noSub = sum(1 for m in muestras if not m['subio'])
    print(f"muestras: {len(muestras)}")
    print(f"yEntrada (fase del bote): min {min(ys):.3f} · media {statistics.mean(ys):.3f} · max {max(ys):.3f}")
    print(f"vel total : min {min(vel):.2f} · media {statistics.mean(vel):.2f} · max {max(vel):.2f}  (umbral 2.9)")
    print(f"vel.y     : min {min(velY):.3f} · media {statistics.mean(velY):.3f} · max {max(velY):.3f}  (umbral 0.39)")
    print(f"FALLOS simulados: liberada {noLib} · subio {noSub}")
    if noSub:
        print("muestras con subio=False:")
        for m in muestras:
            if not m['subio']:
                print(f"   k={m['k']} yEntrada={m['yEntrada']} velY={m['velY']} vel={m['vel']}")
    # correlación grosera yEntrada vs velY (terciles)
    ter = sorted(range(len(ys)), key=lambda i: ys[i])
    terc = [ter[:len(ter)//3], ter[len(ter)//3:2*len(ter)//3], ter[2*len(ter)//3:]]
    print("velY por tercil de yEntrada (bajo/medio/alto):",
          [round(statistics.mean([velY[i] for i in t]), 3) for t in terc])


asyncio.run(main())
