#!/usr/bin/env python3
"""Sonda 5: estado del plano P1 (posición, textura, contenido) + cielo."""
import asyncio, threading, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8938

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS_P1 = """
() => {
  const g = window.__PP_GAME;
  const out = [];
  g.scene.traverse((o) => {
    if (!o.isMesh || !o.geometry || !o.geometry.parameters) return;
    const gp = o.geometry.parameters;
    if (gp.width === 530 || gp.width === 400) {
      const m = o.material;
      const im = m.map && m.map.image;
      const info = {
        geo: [gp.width, gp.height],
        pos: [o.position.x, o.position.y, o.position.z].map((v) => +v.toFixed(1)),
        rotY: +o.rotation.y.toFixed(2),
        img: im ? (im.constructor.name + ':' + im.width + 'x' + im.height) : 'null',
        repeat: m.map ? [m.map.repeat.x, m.map.repeat.y] : null,
        offset: m.map ? [+m.map.offset.x.toFixed(3)] : null,
        alphaTest: m.alphaTest, transparent: m.transparent,
        visible: o.visible, parentVisible: o.parent ? o.parent.visible : null,
        renderOrder: o.renderOrder,
      };
      if (im && im.width > 100) {
        try {
          const cv = document.createElement('canvas');
          cv.width = im.width; cv.height = im.height;
          const c = cv.getContext('2d');
          c.drawImage(im, 0, 0);
          info.rows = [];
          for (const yy of [100, 300, 420, 500, 600, 700]) {
            const d = c.getImageData(2000, Math.min(yy, im.height-1), 1, 1).data;
            info.rows.push([yy, d[0], d[1], d[2], d[3]]);
          }
          // uv del hit horizontal: ¿qué fila del canvas cae a la altura del ojo?
          // plano y = pos.y + h/2 - v*h  =>  v = (pos.y + h/2 - 1.6)/h
          const v = ((o.position.y + gp.height/2) - 1.6) / gp.height;
          info.v_at_eye = +v.toFixed(3);
          info.row_at_eye = Math.round((1 - v) * im.height);
        } catch (e) { info.rows = 'err:' + e; }
      }
      out.push(info);
    }
  });
  return out;
}
"""

async def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 700, "height": 430})
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
            if st["ta"] and st["by"] > 1.2:
                print(f"bola viva tras {i*0.5:.0f}s")
                break
        await page.wait_for_timeout(6000)
        res = await page.evaluate(JS_P1)
        print(json.dumps(res, indent=1))
        await browser.close()

asyncio.run(main())
