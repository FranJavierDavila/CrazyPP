#!/usr/bin/env python3
"""Instrumentación fina del disparador: ¿qué cerrojo bloquea el poder?

Muestreo a 10 Hz durante 40 s de rally real (misma simulación de jugador):
estado, rallyHits, bola (z, vz), _toward del módulo, _rallyFired, _powerCd y
conteo de bordes ascendentes (bola pasa a venir hacia el jugador). Crucial
para saber si maybeTriggerPower ve los mismos eventos que mi simulación.
"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required"])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("http://localhost:3000/")
        await page.wait_for_timeout(5000)
        await page.evaluate("""async () => {
            const g = window.__PP_GAME;
            window.__pp2DPlay = true;
            await g.champs.launch('locura');
            const C = g.champs.mod.controller;
            try { C.startArcade(); } catch (e) {}
            await new Promise(r => setTimeout(r, 1100));
            try { C.startArcade(); } catch (e) {}
            await new Promise(r => setTimeout(r, 1400));
            g.renderer.xr.isPresenting = true;
            g.rules.startMatch('match');
            g.__sim = { returns: 0, faults: 0 };
            g.__simTick = setInterval(() => {
                try {
                    const r = g.rules, b = g.ball;
                    if (!b || !b.pos || !b.vel) return;
                    if (r.state === 'serve' && b.pos.z > 0) {
                        g.setupAIServe(); g.aiServeTimer = 0.15; return;
                    }
                    if (r.state === 'rally' && !g.__simRet &&
                        b.vel.z > 0.5 && b.pos.z > 0.35 && b.pos.y > 0.7) {
                        const antes = r.state;
                        r.registerPaddleHit('player');
                        if (r.state === 'rally') {
                            b.pos.y = Math.max(b.pos.y, 0.95);
                            b.vel.set((Math.random()*2-1)*0.5, 1.35, -(2.6 + Math.random()*0.8));
                            g.__simRet = true; g.__sim.returns++;
                        } else { g.__sim.faults++; }
                    }
                    if (r.state !== 'rally') g.__simRet = false;
                } catch (e) {}
            }, 16);
        }""")

        mues = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            const filas = [];
            let edges = 0, towardPrev = false;
            const t0 = performance.now();
            while (performance.now() - t0 < 40000) {
                await new Promise(r => setTimeout(r, 100));
                const b = g.ball;
                const toward = !!(b && b.vel && b.vel.z > 0.35);
                if (toward && !towardPrev) edges++;
                towardPrev = toward;
                filas.push({
                    t: +((performance.now()-t0)/1000).toFixed(1),
                    est: g.rules.state, hits: g.rules.rallyHits | 0,
                    vz: b && b.vel ? +b.vel.z.toFixed(2) : null,
                    z: b && b.pos ? +b.pos.z.toFixed(2) : null,
                    tw: C._toward ? 1 : 0, fired: C._rallyFired ? 1 : 0,
                    cd: +(C._powerCd || 0).toFixed(1),
                    ret: g.__sim.returns, fault: g.__sim.faults,
                    ed: edges,
                });
            }
            return filas;
        }""")

        # Resumen compacto: cambios de estado y conteos
        print("== MUESTRAS (cada 2 s) ==")
        for m in mues:
            if abs(m["t"] % 2) < 0.1:
                print("  ", json.dumps(m, ensure_ascii=False))
        ult = mues[-1]
        print("\n== TOTALES ==")
        print(f"  bordes vistos (vz>0.35): {ult['ed']} · returns legales: {ult['ret']} · faltas: {ult['fault']}")
        await browser.close()

asyncio.run(main())
