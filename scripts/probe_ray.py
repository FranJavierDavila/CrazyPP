#!/usr/bin/env python3
"""Sonda rayo: ¿qué objeto pinta la banda blanca de la ventana?"""
import asyncio, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8936

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS_RAY = """
() => import('three').then((THREE) => {
  const g = window.__PP_GAME;
  const out = [];
  const mk = (ox,oy,oz, dx,dy,dz, tag) => {
    try {
      const ro = new THREE.Vector3(ox,oy,oz);
      const rd = new THREE.Vector3(dx,dy,dz).normalize();
      const rc = new THREE.Raycaster(ro, rd, 0.1, 400);
      const cands = [];
      g.scene.traverse((o) => { if (o.isMesh && o.material && o.visible) cands.push(o); });
      let hits = [];
      for (const o of cands) {
        try { const h = rc.intersectObject(o, false);
          if (h && h.length) hits.push(h[0]);
        } catch (e) { /* objeto raro: se ignora */ }
      }
      hits.sort((a, b) => a.distance - b.distance);
      const top = [];
      for (const h of hits.slice(0, 5)) {
        const m = h.object.material || {};
        top.push({
          dist: +h.distance.toFixed(1),
          geo: h.object.geometry && h.object.geometry.parameters
               ? [h.object.geometry.parameters.width, h.object.geometry.parameters.height] : null,
          type: m.map && m.map.image ? (m.map.image.constructor.name + ':' + m.map.image.width + 'x' + m.map.image.height)
               : (m.color ? 'color:' + m.color.getHexString() : m.type),
          alphaTest: (m.alphaTest === undefined) ? null : m.alphaTest,
          transparent: !!m.transparent,
          uvpx: m.map && m.map.image ? (() => {
              try {
                const im = m.map.image; const cv = document.createElement('canvas');
                cv.width = im.width; cv.height = im.height;
                const c = cv.getContext('2d'); c.drawImage(im, 0, 0);
                const u = h.uv ? h.uv.x : 0.5, v = h.uv ? h.uv.y : 0.5;
                const d = c.getImageData(
                  Math.min(im.width-1, (u*im.width)|0),
                  Math.min(im.height-1, ((1-v)*im.height)|0), 1, 1).data;
                return [d[0], d[1], d[2], d[3]];
              } catch (e) { return 'err'; }
            })() : null,
        });
      }
      out.push({ tag, hits: top });
    } catch (e) { out.push({ tag, err: String(e) }); }
  };
  mk(0.15,1.62,0.35, -3.2, 0.55, -1.5, 'ventana-centro');
  mk(0.15,1.62,0.35, -3.2, 0.85, -1.2, 'ventana-blanco');
  mk(0.15,1.62,0.35, -3.2, 0.55, -2.6, 'ventana-azul');
  mk(0.15,1.62,0.35, -3.2, 0.10, -2.4, 'ventana-arena');
  return out;
})
"""

async def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 760, "height": 460})
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2000)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3000)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(4000)
        for i in range(60):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         instr: g._instr ? 'si' : 'none' };
            }""")
            if st["ta"] or st["instr"] == "si":
                break
        for i in range(240):
            await page.wait_for_timeout(500)
            st = await page.evaluate("""() => {
                const g = window.__PP_GAME;
                return { ta: g.champs.mod.testActive(),
                         by: +(g.ball ? g.ball.pos.y : -9).toFixed(2) };
            }""")
            if st["ta"] and st["by"] > 0.95:
                print(f"bola viva tras {i*0.5:.0f}s")
                break
        await page.wait_for_timeout(4000)
        rays = await page.evaluate(JS_RAY)
        print(json.dumps(rays, indent=1, ensure_ascii=False))
        await browser.close()

asyncio.run(main())
