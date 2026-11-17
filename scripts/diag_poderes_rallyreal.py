#!/usr/bin/env python3
"""Test de RALLY REAL: saques de IA + devoluciones legales del jugador.

El jugador se simula: cuando la bola viene (z > 0.1, vel.z > 0), registra
golpe legal (rules.registerPaddleHit('player')) y devuelve con tiro parabólico
hacia el campo de la IA. La IA sirve y devuelve con su lógica real. Con rally
legal (rallyHits ≥ 1) el disparador natural (32% por bola entrante) debe
anunciar poderes → congelar → lanzar globos/giro. Se registran TODOS los
eventos con marca de tiempo.
"""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required"])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        cons: list[str] = []
        page.on("console", lambda m: cons.append(f"[{m.type}] {m.text[:200]}"))
        page.on("pageerror", lambda e: cons.append(f"[PAGEERROR] {e}"))
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

            // ---- jugador simulado con golpeo LEGAL ----
            g.__simReturn = false;
            g.__simTick = setInterval(() => {
                try {
                    const r = g.rules, b = g.ball;
                    if (!b || !b.pos || !b.vel) return;
                    // saque: si es turno del jugador (bola a su lado), pasamos
                    // el saque a la IA con su propio setup
                    if (r.state === 'serve' && b.pos.z > 0) {
                        g.setupAIServe();
                        g.aiServeTimer = 0.15;
                        return;
                    }
                    // devolución del jugador: bola que viene y ya pasó la red
                    if (r.state === 'rally' && !g.__simReturn &&
                        b.vel.z > 0.5 && b.pos.z > 0.35 && b.pos.y > 0.7) {
                        const ok = r.registerPaddleHit('player');
                        if (r.state === 'rally') {   // el golpeo fue legal
                            b.pos.y = Math.max(b.pos.y, 0.95);
                            b.vel.set((Math.random()*2-1)*0.5, 1.35, -(2.6 + Math.random()*0.8));
                            g.__simReturn = true;
                        }
                    }
                    if (r.state !== 'rally') g.__simReturn = false;
                } catch (e) { /* silencio */ }
            }, 16);
        }""")
        print("Simulación activa. Observando 60 s...")

        # ----Observación ----
        eventos = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            const ev = [];
            let lastKind = '', lastPend = null, maxVivos = 0, maxRy = 0;
            const t0 = performance.now();
            while (performance.now() - t0 < 60000) {
                await new Promise(r => setTimeout(r, 150));
                const pend = C._pendingPower ? C._pendingPower.kind : null;
                const kind = C._powerKind || '';
                if (pend && pend !== lastPend) ev.push(`t=${((performance.now()-t0)/1000).toFixed(1)} ANUNCIO ${pend} (estado=${g.rules.state}, freezeT=${g.freezeT.toFixed(1)})`);
                lastPend = pend;
                if (kind && kind !== lastKind) ev.push(`t=${((performance.now()-t0)/1000).toFixed(1)} LANZADO ${kind} (estado=${g.rules.state})`);
                lastKind = kind;
                if (C._globos) maxVivos = Math.max(maxVivos, C._globos.items.filter(i => i.alive).length);
                if (C._giroT > 0) maxRy = Math.max(maxRy, Math.abs(g.rig.rotation.y));
            }
            ev.push(`RESUMEN: maxGlobosVivos=${maxVivos} maxRigY=${maxRy.toFixed(3)} rad`);
            return ev;
        }""")
        for e in eventos:
            print("  ", e)

        sos = [c for c in cons if 'champs.update' in c or 'PAGEERROR' in c]
        print("ERRORES MÓDULO:", len(sos))
        for c in sos[-5:]:
            print("  ", c[:200])
        await browser.close()

asyncio.run(main())
