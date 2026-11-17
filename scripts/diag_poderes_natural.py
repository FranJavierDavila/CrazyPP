#!/usr/bin/env python3
"""Test NATURAL del disparador de poderes del Clown (sin forzar nada).

Arranca el campeonato + duelo, deja jugar a la IA (saques → bola hacia el
jugador) y sondea cada 200 ms durante 45 s: estado del punto, poderes
anunciados/lanzados, globos vivos, vaivén del rig. El objetivo es ver si la
cadena NATURAL (maybeTriggerPower → firePower → _launchPending → efecto)
funciona sin ningún forcing.
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
        page.on("console", lambda m: cons.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: cons.append(f"[PAGEERROR] {e}"))
        await page.goto("http://localhost:3000/")
        await page.wait_for_timeout(5000)

        setup = await page.evaluate("""async () => {
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
            return { estado: g.rules.state };
        }""")
        print("SETUP:", json.dumps(setup, ensure_ascii=False))

        # Sondeo natural 45 s
        hist = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            const log = [];
            let lastPhase = '';
            const t0 = performance.now();
            while (performance.now() - t0 < 45000) {
                await new Promise(r => setTimeout(r, 200));
                const snap = {
                    t: +((performance.now() - t0) / 1000).toFixed(1),
                    estado: g.rules.state, hits: g.rules.rallyHits | 0,
                    pend: C._pendingPower ? C._pendingPower.kind : null,
                    kind: C._powerKind || null, pT: +(C._powerT || 0).toFixed(1),
                    globos: C._globos ? C._globos.items.filter(i => i.alive).length : 0,
                    giroT: +(C._giroT || 0).toFixed(1),
                    ry: +g.rig.rotation.y.toFixed(3),
                };
                const fase = (snap.pend ? 'ANUNCIO:' + snap.pend : '') +
                             (snap.kind ? ' ACTIVO:' + snap.kind : '');
                if (fase !== lastPhase) { log.push(snap); lastPhase = fase; }
            }
            return log;
        }""")
        print("CAMBIOS DE FASE (natural):")
        for h in hist:
            print("  ", json.dumps(h, ensure_ascii=False))

        sos = [c for c in cons if ('champs.update' in c or 'PAGEERROR' in c)]
        print("ERRORES MÓDULO:", len(sos))
        for c in sos[-5:]:
            print("  ", c[:200])
        await browser.close()

asyncio.run(main())
