#!/usr/bin/env python3
"""Tasa de devolución de la CPU: 20 tiros sintéticos hacia su campo.
Mide % devueltos + profundidad del bote de su devolución (campo jugador).
Uso: python test_ai_returns.py [etiqueta]"""
import asyncio, json, random, statistics, sys
from playwright.async_api import async_playwright

LABEL = sys.argv[1] if len(sys.argv) > 1 else "run"
HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
TRIALS = 14
random.seed(42 + hash(LABEL) % 1000)

INJECT = """(p) => {
    const g = window.__game;
    // congelar la demo del lado jugador: el test solo mide a la CPU
    if (!g.demoAI._frozen) {
        g.demoAI._frozen = true;
        g.demoAI.update = () => null;
        g.demoAI.pos.set(0, 1.0, 99);
        if (g.demoPaddleMesh) g.demoPaddleMesh.visible = false;
    }
    // rallye sintético: reglas blindadas (sin serviciones pendientes ni
    // cuenta atrás del estado 'point')
    g.rules.state = 'rally';
    g.rules.stateTimer = 999;
    g.rules.serveOwnPending = false;
    g.rules.mustBounceOpp = true;
    g.rules.validBounce = false;
    g.rules.isServeBall = false;
    g.rules.netTouched = false;
    g.rules.lastHitter = 'player';
    g.rules.message = '';
    g.tossed = false;
    g.aiToss = null; g.demoToss = null;
    g.ball.pos.set(p.x, p.y, p.z);
    g.ball.vel.set(p.vx, p.vy, p.vz);
    g.ball.spin.set(p.sx, 0, 0);
    return true;
}"""

WATCH = """() => {
    // observa la evolución: devuelve {returned, bounce:{x,z}, state, msg}
    const g = window.__game;
    const b = g.ball;
    if (g.rules.lastHitter === 'ai' && !this._hit) {
        this._hit = true;
        this._prevVy = b.vel.y; this._prevY = b.pos.y;
        return { done: false };
    }
    if (this._hit && !this._bounce) {
        // bote = vel.y pasa de negativo a positivo cerca de la mesa
        if (this._prevVy < 0 && b.vel.y > 0 && Math.abs(b.pos.y - 0.78) < 0.05) {
            this._bounce = { x: +b.pos.x.toFixed(3), z: +b.pos.z.toFixed(3) };
            return { done: true, returned: true, bounce: this._bounce };
        }
        this._prevVy = b.vel.y;
    }
    return { done: g.rules.state === 'point' || g.rules.state === 'serve',
             returned: !!this._hit, msg: g.rules.message,
             bounce: this._bounce || null };
}"""

async def main():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 480, "height": 300})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(500)

        for i in range(TRIALS):
            # aparcar la bola anterior para aislar la prueba
            await page.evaluate("""() => {
                const g = window.__game;
                g.rules.state = 'point';
                g.rules.stateTimer = 999;
                g.ball.pos.set(0, 0.03, 3.0);
                g.ball.vel.set(0, 0, 0);
                g.ball.spin.set(0, 0, 0);
                g.rules.lastHitter = null;
            }""")
            await asyncio.sleep(0.5)
            params = {
                "x": round(random.uniform(-0.30, 0.30), 2),
                "y": 1.05,
                "z": 0.9,
                "vx": round(random.uniform(-0.8, 0.8), 2),
                "vy": round(random.uniform(2.8, 3.2), 2),      # calibrado con
                "vz": round(-random.uniform(5.5, 6.5), 2),     # física real
                "sx": round(random.uniform(5, 9), 1),
            }
            await page.evaluate(INJECT, params)
            # watcher por prueba
            await page.evaluate("""() => {
                window.__w = { _hit: false, _bounce: null, _prevVy: 0 };
            }""")
            trial = None
            for step in range(120):         # máx 12 s por prueba (headless va lento)
                r = await page.evaluate(
                    """() => { const g = window.__game;
                        const w = window.__w; const b = g.ball;
                        if (!w._hit && g.rules.lastHitter === 'ai') {
                            w._hit = true; w._prevVy = b.vel.y;
                        } else if (w._hit && !w._bounce) {
                            if (w._prevVy < 0 && b.vel.y > 0 &&
                                Math.abs(b.pos.y - 0.78) < 0.06) {
                                w._bounce = { x: +b.pos.x.toFixed(3),
                                              z: +b.pos.z.toFixed(3) };
                            }
                            w._prevVy = b.vel.y;
                        }
                        if (g.rules.state !== 'rally' && !w._snap) {
                            w._snap = {
                                last: g.rules.lastHitter,
                                vb: g.rules.validBounce,
                                mbo: g.rules.mustBounceOpp,
                                pos: [+b.pos.x.toFixed(2), +b.pos.y.toFixed(2), +b.pos.z.toFixed(2)],
                                vel: [+b.vel.x.toFixed(2), +b.vel.y.toFixed(2), +b.vel.z.toFixed(2)],
                                ai: [+g.ai.pos.x.toFixed(2), +g.ai.pos.y.toFixed(2), +g.ai.pos.z.toFixed(2)],
                                pv: g.ai.predictValid,
                                pred: [+g.ai.predict.x.toFixed(2), +g.ai.predict.y.toFixed(2), +g.ai.predict.z.toFixed(2)],
                                cd: +g.ai.hitCooldown.toFixed(2),
                            };
                        }
                        return { done: g.rules.state !== 'rally',
                                 hit: w._hit, bounce: w._bounce,
                                 snap: w._snap || null,
                                 msg: g.rules.message };
                    }""")
                if r["done"] or (r["hit"] and r["bounce"]):
                    trial = r
                    break
                await asyncio.sleep(0.07)
            if trial:
                results.append({
                    "returned": bool(trial["hit"]),
                    "bounce": trial["bounce"],
                    "snap": trial["snap"],
                    "msg": (trial["msg"] or "")[:60],
                })
            else:
                results.append({"returned": False, "bounce": None, "msg": "timeout"})
            await asyncio.sleep(0.25)
        await browser.close()

    n_ok = sum(1 for r in results if r["returned"])
    depths = [r["bounce"]["z"] + 1.6 for r in results if r["bounce"]]
    depths_in = [d for d in depths if d > 0.05]
    print(f"[{LABEL}] devueltos: {n_ok}/{TRIALS} ({100*n_ok/TRIALS:.0f}%)")
    if depths:
        print(f"[{LABEL}] profundidad del bote CPU (desde la red): " +
              f"media {statistics.mean(depths):.2f} m · " +
              ", ".join(f"{d:+.2f}" for d in depths))
    if errors:
        print("ERRORES página:", errors[:3])
    json.dump(results, open(f"/home/z/my-project/scripts/returns_{LABEL}.json", "w"),
              indent=1)

asyncio.run(main())
