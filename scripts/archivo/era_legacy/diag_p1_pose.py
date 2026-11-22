#!/usr/bin/env python3
"""diag_p1: ¿dónde se pierde la pose? envío vs recepción vs push JB, P1 LAN."""
import asyncio
import importlib.util
import os

_spec = importlib.util.spec_from_file_location(
    "b3674", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bateria_multi_v3674.py"))
b3674 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b3674)

JS_TAP_ENVIO = """() => {
  const G = window.__PP_GAME;
  if (G.__tapEnv) return true;
  G.__tapEnv = { snd: 0, bytes: 0, t0: performance.now() };
  const o = G.net._fastSend.bind(G.net);
  G.net._fastSend = (buf, now) => { G.__tapEnv.snd++; G.__tapEnv.bytes += buf.byteLength; return o(buf, now); };
  return true;
}"""

JS_TAP_RECEP = """() => {
  const G = window.__PP_GAME;
  if (G.__tapRec) return true;
  G.__tapRec = { fast: 0, conPose: 0, push: 0, t0: performance.now() };
  const of = G.net._onFast.bind(G.net);
  G.net._onFast = (b) => {
    G.__tapRec.fast++;
    try {
      const p = window.__PPNET.decodePacket(b, { yAnchor: 0.76, evs: [] });
      if (p && p.pose) G.__tapRec.conPose++;
    } catch (e) { /* */ }
    return of(b);
  };
  const op = G.net._jb.push.bind(G.net._jb);
  G.net._jb.push = (t, s) => { G.__tapRec.push++; return op(t, s); };
  return true;
}"""

JS_LEE_TAP = """() => { const G = window.__PP_GAME;
  const e = G.__tapEnv, r = G.__tapRec;
  const s = e ? Math.round(e.snd / ((performance.now() - e.t0) / 1000) * 10) / 10 : -1;
  const f = r ? Math.round(r.fast / ((performance.now() - r.t0) / 1000) * 10) / 10 : -1;
  const cp = r ? Math.round(r.conPose / ((performance.now() - r.t0) / 1000) * 10) / 10 : -1;
  const pu = r ? Math.round(r.push / ((performance.now() - r.t0) / 1000) * 10) / 10 : -1;
  return { envio_s: s, recep_s: f, conPose_s: cp, push_s: pu,
           poseHz: G.net._poseHz, poseAcc: Math.round((G.net._poseAcc || 0) * 1000) / 1000,
           raf: G.__rafN || -1, tun: !!G.net._tunnel, v2: G.net.v2 }; }"""

JS_RAF_CONTA = """() => { const G = window.__PP_GAME;
  if (G.__rafOn) return true;
  G.__rafN = 0;
  const f = () => { G.__rafN++; requestAnimationFrame(f); };
  requestAnimationFrame(f);
  G.__rafOn = true;
  return true; }"""


async def main():
    url, srv = b3674.arranca_servidor_si_hace_falta(b3674.URL_DEFECTO)
    async with b3674.async_playwright() as pw:
        b = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        h = await b.new_page(viewport={"width": 480, "height": 320})
        g = await b.new_page(viewport={"width": 480, "height": 320})
        for pg in (h, g):
            await pg.add_init_script(b3674.JS_HILO_QA)
            await pg.goto(url, wait_until="domcontentloaded", timeout=45000)
        for pg in (h, g):
            await b3674.wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
        geo = {"host": (0.15, 1.72, 0.35, 0.22, 0.95, -0.75, 0.1, -0.28, 1.0, 0.1, 0),
               "guest": (-0.2, 1.65, 0.5, 0.3, 0.92, -0.7, 0.0, -0.32, 0.98, 0.18, 977)}
        for pg, quien in ((h, "host"), (g, "guest")):
            gx = geo[quien]
            js = (b3674.JS_ARM
                  .replace("__HX__", repr(gx[0])).replace("__HY__", repr(gx[1])).replace("__HZ__", repr(gx[2]))
                  .replace("__PX__", repr(gx[3])).replace("__PY__", repr(gx[4]))
                  .replace("__PZ__", repr(gx[5])).replace("__PZC__", repr(gx[6]))
                  .replace("__LX__", repr(gx[7])).replace("__LY__", repr(gx[8])).replace("__LZ__", repr(gx[9]))
                  .replace("__SIMT0__", str(gx[10]))
                  .replace("__LAT__", "18").replace("__JIT__", "4")
                  .replace("__LOSS__", "0.005").replace("__SEED__", "36780001"))
            await pg.evaluate(js)
            await pg.evaluate(JS_RAF_CONTA)
        await h.evaluate(b3674.JS_HOST_ROOM)
        code = None
        for _ in range(80):
            st = await h.evaluate("() => window.__PP_GAME.net.status")
            if st == "waiting":
                code = await h.evaluate("() => window.__PP_GAME.net.code")
                break
            await h.wait_for_timeout(250)
        print(f"sala {code}", flush=True)
        await g.evaluate(b3674.JS_GUEST_JOIN, code)
        for pg in (h, g):
            ok = await b3674.wait_cond(pg, b3674.JS_ONLINE, 40)
            print(f"v2 ok: {ok}", flush=True)
        await h.wait_for_timeout(1000)
        await h.evaluate(JS_TAP_ENVIO)
        await g.evaluate(JS_TAP_RECEP)
        await h.wait_for_timeout(6000)
        print("HOST (emisor):", await h.evaluate(JS_LEE_TAP), flush=True)
        print("GUEST (receptor):", await g.evaluate(JS_LEE_TAP), flush=True)
        await b.close()
    if srv:
        srv.terminate()

asyncio.run(main())
