#!/usr/bin/env python3
"""Arnés de diagnóstico v2: superpoderes nuevos del CLOWN (globos + mareo/giro).

Usa el acceso público al controlador: champs.mod.controller (get controller())
o window.__PP_LOCURA.ctrl(). Ejercita la cadena REAL:
maybeTriggerPower → firePower → cartel → _launchPending → _startGlobos/_startGiro.
"""
import asyncio, json
from playwright.async_api import async_playwright

URL = "http://localhost:3000/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        cons: list[str] = []
        page.on("console", lambda m: cons.append(f"[{m.type}] {m.text}"))
        page.on("pageerror", lambda e: cons.append(f"[PAGEERROR] {e}"))
        await page.goto(URL)
        await page.wait_for_timeout(5000)

        # ---------- 0) gancho + campeonato + controlador ----------
        boot = await page.evaluate("""async () => {
            const g = window.__PP_GAME || window.__game;
            if (!g) return { err: 'sin gancho' };
            window.__pp2DPlay = true;
            try { await g.champs.launch('locura'); } catch (e) { return { err: 'launch: ' + e }; }
            const wrap = g.champs.mod;
            if (!wrap) return { err: 'módulo no activo' };
            const C = wrap.controller || (window.__PP_LOCURA && window.__PP_LOCURA.ctrl());
            if (!C) return { err: 'sin controller' };
            return { ok: true, activo: g.champs.activeId,
                     metodos: { firePower: typeof C.firePower, _powerList: typeof C._powerList,
                                _startGlobos: typeof C._startGlobos, _startGiro: typeof C._startGiro,
                                _updateGlobos: typeof C._updateGlobos, _updateGiro: typeof C._updateGiro },
                     dataPowers: (C.data && (C.data.powers || []).map(p => p.kind)) || null };
        }""")
        print("BOOT:", json.dumps(boot, ensure_ascii=False))
        if boot.get("err"):
            print("CONSOLE:", "\n".join(cons[-12:])); await browser.close(); return

        # ---------- 1) lista de poderes del runtime ----------
        plist = await page.evaluate("""() => {
            const C = window.__PP_GAME.champs.mod.controller;
            return (C._powerList() || []).map(p => ({ kind: p.kind, dur: p.duration, icon: p.icon || null }));
        }""")
        print("POWERS RUNTIME:", json.dumps(plist, ensure_ascii=False))

        # ---------- 2) duelo + partida viva ----------
        duel = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            try { C.startArcade(); } catch (e) {}
            await new Promise(r => setTimeout(r, 1200));
            try { C.startArcade(); } catch (e) {}
            await new Promise(r => setTimeout(r, 1500));
            g.renderer.xr.isPresenting = true;
            g.rules.startMatch('match');
            await new Promise(r => setTimeout(r, 800));
            return { activo: C.active, stage: C.stage, estado: g.rules.state,
                     bola: !!(g.ball && g.ball.pos), rig: !!g.rig,
                     freezeT: g.freezeT || 0 };
        }""")
        print("DUELO:", json.dumps(duel, ensure_ascii=False))

        # ---------- 3) GLOBOS: cadena forzada ----------
        globos = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            C.firePower('globos');
            const anuncio = { pend: C._pendingPower && C._pendingPower.kind,
                              pendT: +C._pendT.toFixed(2), freezeT: +g.freezeT.toFixed(2) };
            C._pendT = 0.02;
            await new Promise(r => setTimeout(r, 700));
            const G = C._globos;
            return { anuncio, powerKind: C._powerKind, powerT: +(C._powerT||0).toFixed(2),
                     pool: !!G, grpVisible: G ? G.grp.visible : null,
                     padreEsRig: G ? (G.grp.parent === g.rig) : null,
                     vivos: G ? G.items.filter(i => i.alive).length : null,
                     pos: G ? G.items.filter(i => i.alive).slice(0,3).map(i =>
                        [+i.s.position.x.toFixed(2), +i.s.position.y.toFixed(2), +i.s.position.z.toFixed(2)]) : null };
        }""")
        print("GLOBOS:", json.dumps(globos, ensure_ascii=False))
        await page.screenshot(path="/home/z/my-project/scripts/diag_globos.png")

        # ---------- 4) GIRO (mareo): cadena forzada + muestras del rig ----------
        giro = await page.evaluate("""async () => {
            const g = window.__PP_GAME, C = g.champs.mod.controller;
            if (C._powerKind) { C._powerT = 0; try { C._endPower(); } catch (e) {} }
            await new Promise(r => setTimeout(r, 400));
            const base = { ry: +g.rig.rotation.y.toFixed(5), rx: +g.rig.rotation.x.toFixed(5) };
            C.firePower('giro');
            C._pendT = 0.02;
            const mues = [];
            for (let i = 0; i < 10; i++) {
                await new Promise(r => setTimeout(r, 300));
                mues.push({ t: +(C._giroT||0).toFixed(2), ry: +g.rig.rotation.y.toFixed(5),
                            rx: +g.rig.rotation.x.toFixed(5), kind: C._powerKind,
                            pT: +(C._powerT||0).toFixed(2) });
            }
            return { base, mues };
        }""")
        print("GIRO:", json.dumps(giro, ensure_ascii=False, indent=1))
        await page.screenshot(path="/home/z/my-project/scripts/diag_giro.png")

        # ---------- 5) consola sospechosa ----------
        sos = [c for c in cons if ('champs.update' in c or 'PAGEERROR' in c
               or 'locura' in c.lower() or 'error' in c.lower() or 'warn' in c.lower())]
        print("\nCONSOLE SOSPECHOSA (últimas 15):")
        for c in sos[-15:]:
            print("  ", c[:250])
        await browser.close()

asyncio.run(main())
