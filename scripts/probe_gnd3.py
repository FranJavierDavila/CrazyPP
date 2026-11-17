#!/usr/bin/env python3
"""v2.113 · Sonda 3: render aislado de la arena + borde inferior del P1."""
import asyncio, os, threading, base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8935
OUT = "/tmp/trenshot"
os.makedirs(OUT, exist_ok=True)

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

JS = """async () => {
  const g = window.__PP_GAME;
  const mod = g.champs.mod;
  let act = null;
  const walk = (o, d) => {
    if (!o || d > 4 || act) return;
    if (o.cubos && o.group) { act = o; return; }
    for (const k of Object.keys(o)) { try { walk(o[k], d + 1); } catch (e) {} }
  };
  walk(mod, 0);
  const out = {};
  // --- render AISLADO: sólo los planos de arena (64 m) ---
  const saved = [];
  act.group.traverse((n) => {
    if (n && n.isMesh) { saved.push([n, n.visible]); n.visible = false; }
  });
  const arenas = [];
  for (const [n] of saved) {
    const pr = n.geometry && n.geometry.parameters;
    if (pr && pr.width === 64) { n.visible = true; arenas.push(n); }
  }
  const ren = g.renderer;
  const cam = g.camera.clone();
  cam.position.set(0.15, 1.62, 0.35);
  cam.lookAt(-40, -0.35, -1.8);
  const orig = ren.render.bind(ren);
  orig(g.scene, cam);
  window.__shotA = ren.domElement.toDataURL('image/png');
  // --- render aislado P1 (panorámica) ---
  for (const [n] of saved) n.visible = false;
  const p1s = [];
  for (const [n] of saved) {
    const pr = n.geometry && n.geometry.parameters;
    if (pr && pr.width === 530) { n.visible = true; p1s.push(n); }
  }
  cam.lookAt(-140, 0, -1.8);
  orig(g.scene, cam);
  window.__shotP1 = ren.domElement.toDataURL('image/png');
  for (const [n, v] of saved) n.visible = v;
  // --- píxel del centro de la textura arena ---
  const gt = act._gndTex;
  const c2 = document.createElement('canvas');
  c2.width = c2.height = 8;
  const cx2 = c2.getContext('2d');
  try {
    cx2.drawImage(gt.image, 0, 0, 8, 8);
    out.texPixel = Array.from(cx2.getImageData(4, 4, 1, 1).data);
  } catch (e) { out.texPixel = 'err:' + e.message; }
  // --- lienzo P1: muestrea columnas del BORDE INFERIOR (¿negro?) ---
  const p1m = p1s[0] && p1s[0].material.map;
  if (p1m && p1m.image) {
    const img = p1m.image;
    const c3 = document.createElement('canvas');
    c3.width = 16; c3.height = 16;
    const cx3 = c3.getContext('2d');
    try {
      cx3.drawImage(img, 0, img.height - 8, img.width, 8, 0, 0, 16, 16);
      const d3 = cx3.getImageData(0, 8, 16, 1).data;
      out.p1Bottom = Array.from(d3.slice(0, 16)).join(',');
      // y una franja a mitad (desierto estirado)
      cx3.clearRect(0, 0, 16, 16);
      cx3.drawImage(img, 0, img.height * 0.82, img.width, 8, 0, 0, 16, 16);
      const d4 = cx3.getImageData(0, 8, 16, 1).data;
      out.p182 = Array.from(d4.slice(0, 16)).join(',');
      out.p1H = img.height; out.p1W = img.width;
    } catch (e) { out.p1Bottom = 'err:' + e.message; }
  }
  // --- intersección analítica con los planos de arena ---
  const ro = new (Object.getPrototypeOf(arenas[0]).constructor)();
  out.analitica = arenas.map((a) => {
    const nrm = { x: 0, y: 1, z: 0 };
    const ey = 1.62, py = a.position.y;
    const dir = { x: -0.85, y: -0.30, z: -0.45 };
    const t = (py - ey) / dir.y;
    const px = 0.15 + dir.x * t, pz = 0.35 + dir.z * t;
    const halfW = 32, halfD = 120;
    const lx = px - a.position.x, lz = pz - a.position.z;
    const dentro = Math.abs(lx) <= halfW && Math.abs(lz) <= halfD;
    return { t: +t.toFixed(1), p: [+px.toFixed(1), py, +pz.toFixed(1)],
             dentro, centro: a.position.toArray().map((v) => +v.toFixed(1)) };
  });
  return out;
}"""

async def main():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), _H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 900, "height": 520})
        await page.goto(f"http://127.0.0.1:{PORT}/index.html")
        await page.wait_for_timeout(2500)
        await page.evaluate("""() => {
            localStorage.setItem('pp_player_name', 'foro3d');
            localStorage.setItem('pp_champ_oeste_stage', '4');
        }""")
        await page.reload()
        await page.wait_for_timeout(3500)
        await page.evaluate("""() => {
            window.__pp2DPlay = true;
            const ov = document.getElementById('overlay');
            if (ov) ov.style.display = 'none';
        }""")
        await page.evaluate("() => window.__PP_GAME.champs.launch('oeste')")
        await page.wait_for_timeout(5000)
        for i in range(80):
            await page.evaluate("() => window.__PP_GAME.champs.mod.replayLaunch(3)")
            await page.wait_for_timeout(400)
            if await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()"): break
        await page.wait_for_timeout(4000)
        res = await page.evaluate(JS)
        print("texPixel arena:", res.get("texPixel"))
        print("P1 bottom rgba:", res.get("p1Bottom"), " (h=", res.get("p1H"), "w=", res.get("p1W"), ")")
        print("P1 82% rgba:", res.get("p1_82") or res.get("p182") or res.get("p1%82") or res.get("p1_82%") or res.get("p1_82pc") or res.get("p1_82_prc") or res.get("p1'82") or res.get("p1_82v") or res.get("p1_82x") or res.get("p1_82y") or res.get("p1_82z") or "")
        print("analítica rayo hacia la banda:", res.get("analitica"))
        for key, name in [("__shotA", "arena_aislada.png"), ("__shotP1", "p1_aislada.png")]:
            shot = await page.evaluate(f"() => window.{key} || ''")
            if shot:
                with open(f"{OUT}/{name}", "wb") as f:
                    f.write(base64.b64decode(shot.split(",")[1]))
                print("captura ->", name)
        await browser.close()

asyncio.run(main())
