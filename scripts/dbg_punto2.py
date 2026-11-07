#!/usr/bin/env python3
import asyncio, importlib.util
from playwright.async_api import async_playwright

spec = importlib.util.spec_from_file_location("bat", "/home/z/my-project/scripts/bateria_multi_v3674.py")
bat = importlib.util.module_from_spec(spec); bat.__name__ = "bat"
spec.loader.exec_module(bat)

JS_POLL = """() => {
  const G = window.__PP_GAME;
  return {
    st: G.rules.state, sv: G.rules.server, timer: +G.rules.stateTimer.toFixed(2),
    msg: (G.rules.message || '').slice(0, 40),
    ball: G.net._ball ? G.net._ball.state : '?',
    pSelf: !!G.net._pausedSelf, pRem: !!G.net._pausedRemote,
    freeze: +G.freezeT.toFixed(2), v2: G.net.v2,
    online: G.net.online, active: !!(G.renderer.xr.isPresenting || G.net.online || window.__pp2DPlay),
    intents: (window.__INTENTS_LOG || []).slice(-4),
  };
}"""

async def wait_cond(page, js, timeout_s, step_ms=250):
    t = 0.0
    while t < timeout_s:
        try:
            if await page.evaluate(js):
                return True
        except Exception:
            pass
        await page.wait_for_timeout(step_ms)
        t += step_ms / 1000.0
    return False

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        host = await browser.new_page(viewport={"width": 1100, "height": 650})
        guest = await browser.new_page(viewport={"width": 1100, "height": 650})
        per = dict(bat.PERFILES[0])
        for pg, clave in ((host, "skew_h"), (guest, "skew_g")):
            await pg.add_init_script(bat.JS_HILO_QA)
        for pg in (host, guest):
            await pg.goto("http://localhost:3000/game.html", wait_until="domcontentloaded", timeout=45000)
        for pg in (host, guest):
            await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
        geo_h = {"hx": 0.15, "hy": 1.72, "hz": 0.35, "px": 0.22, "py": 0.95, "pz": -0.75, "pzc": 0.1, "lx": -0.28, "ly": 1.0, "lz": 0.1, "t0": 0}
        geo_g = {"hx": -0.2, "hy": 1.65, "hz": 0.5, "px": 0.3, "py": 0.92, "pz": -0.7, "pzc": 0.0, "lx": -0.32, "ly": 0.98, "lz": 0.18, "t0": 977}
        for pg, quien, g0 in ((host, "host", geo_h), (guest, "guest", geo_g)):
            seed = 36740001 + (1 if quien == "host" else 2)
            js = (bat.JS_ARM
                  .replace("__HX__", repr(g0["hx"])).replace("__HY__", repr(g0["hy"])).replace("__HZ__", repr(g0["hz"]))
                  .replace("__PX__", repr(g0["px"])).replace("__PY__", repr(g0["py"]))
                  .replace("__PZ__", repr(g0["pz"])).replace("__PZC__", repr(g0["pzc"]))
                  .replace("__LX__", repr(g0["lx"])).replace("__LY__", repr(g0["ly"])).replace("__LZ__", repr(g0["lz"]))
                  .replace("__SIMT0__", str(g0["t0"]))
                  .replace("__LAT__", "18").replace("__JIT__", "4")
                  .replace("__LOSS__", "0.005").replace("__SEED__", str(seed)))
            await pg.evaluate(js)
        await host.evaluate(bat.JS_HOST_ROOM)
        code = None
        for _ in range(80):
            if await host.evaluate("() => window.__PP_GAME.net.status") == "waiting":
                code = await host.evaluate("() => window.__PP_GAME.net.code")
                break
            await host.wait_for_timeout(250)
        print("sala:", code, flush=True)
        await guest.evaluate(bat.JS_GUEST_JOIN, code)
        for pg, n in ((host, "H"), (guest, "G")):
            ok = await wait_cond(pg, bat.JS_ONLINE, 40)
            print(f"v2 {n}: {ok}", flush=True)
        for pg, n in ((host, "H"), (guest, "G")):
            ok = await wait_cond(pg, bat.JS_STARTED, 20)
            print(f"start {n}: {ok}", flush=True)
        # punto 1
        await host.evaluate(bat.JS_SERVE_A)
        await host.wait_for_timeout(220)
        await host.evaluate(bat.JS_SERVE_B)
        gR = await wait_cond(guest, "() => window.__PP_GAME.rules.state === 'rally'", 8)
        print("rally invitado:", gR, flush=True)
        gA = await wait_cond(guest, bat.JS_WAIT_AUTH, 10)
        print("auth invitado:", gA, flush=True)
        await guest.evaluate(bat.JS_BRAZO_DEVUELVE)
        await guest.wait_for_timeout(60)
        ret = await guest.evaluate(bat.JS_DEVUELVE)
        print("devuelve:", ret, flush=True)
        hP = await wait_cond(host, bat.JS_WAIT_PUNTO, 12)
        print("punto anfitrión:", hP, flush=True)
        gP = await wait_cond(guest, bat.JS_WAIT_PUNTO, 12)
        print("punto invitado:", gP, flush=True)
        # VIGILAR 15 s: ¿el árbitro transiciona a serve?
        for i in range(15):
            h = await host.evaluate(JS_POLL)
            print(f"t+{i}s H: {h}", flush=True)
            await host.wait_for_timeout(1000)
        await browser.close()

asyncio.run(main())
