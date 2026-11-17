#!/usr/bin/env python3
"""v2.113 · Sonda 2 del suelo exterior: raycast con THREE + render aislado."""
import asyncio, os, threading, base64
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8934
OUT = "/tmp/trenshot"
os.makedirs(OUT, exist_ok=True)

class _H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=GAME, **kw)
    def log_message(self, *a):
        pass

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

        res = await page.evaluate("""async () => {
            const T = await import('https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js');
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
            // 1) raycast hacia la banda negra (ventana izquierda)
            const rc = new T.Raycaster();
            const pos = new T.Vector3(0.15, 1.62, 0.35);
            const dirs = {
                'sill~13m': new T.Vector3(-0.148, -0.0510, -0.30).normalize(),
                'medio':    new T.Vector3(-0.85, -0.30, -0.45).normalize(),
                'bajo':     new T.Vector3(-0.85, -0.55, -0.45).normalize(),
            };
            out.rays = {};
            for (const [k, d] of Object.entries(dirs)) {
                rc.set(pos, d); rc.far = 200;
                const hits = rc.intersectObject(act.group, true).slice(0, 4).map((h) => {
                    const pr = h.object.geometry.parameters || {};
                    return {
                    d: +h.distance.toFixed(1),
                    p: h.point.toArray().map((v) => +v.toFixed(1)),
                    tipo: (pr.width === 64)
                        ? 'ARENA' : ('geo:' + (h.object.geometry.type || '?') +
                          (pr ? ' ' + Math.round(pr.width || 0) + 'x' +
                              Math.round(pr.height || 0) : '')),
                    ro: h.object.renderOrder,
                    color: h.object.material && h.object.material.color
                        ? '#' + h.object.material.color.getHexString() : null,
                    mapW: h.object.material && h.object.material.map &&
                          h.object.material.map.image ? h.object.material.map.image.width : 0,
                    transparent: h.object.material ? h.object.material.transparent : null,
                    opacity: h.object.material ? h.object.material.opacity : null,
                    };
                });
                out.rays[k] = hits;
            }
            // 2) render AISLADO: sólo los planos de arena
            const saved = [];
            act.group.traverse((n) => {
                if (n.isMesh) {
                    const arena = n.geometry.parameters && n.geometry.parameters.width === 64;
                    saved.push([n, n.visible]);
                    n.visible = arena;
                }
            });
            const ren = g.renderer;
            const cam = g.camera.clone();
            cam.position.set(0.15, 1.62, 0.35);
            cam.lookAt(-30, -0.3, -1.8);
            const origRender = ren.render.bind(ren);
            origRender(g.scene, cam);
            const cv = ren.domElement;
            out.aislado = cv.toDataURL('image/png').slice(0, 30) + '...';
            window.__shotAislado = cv.toDataURL('image/png');
            // restaurar
            for (const [n, v] of saved) n.visible = v;
            // 3) mapa de la arena: color del píxel central
            const gt = act._gndTex;
            const c2 = document.createElement('canvas');
            c2.width = c2.height = 8;
            const cx2 = c2.getContext('2d');
            try {
                cx2.drawImage(gt.image, 0, 0, 8, 8);
                const px = cx2.getImageData(4, 4, 1, 1).data;
                out.texPixel = Array.from(px);
            } catch (e) { out.texPixel = 'err:' + e.message; }
            return out;
        }""")
        print("rays:")
        for k, hits in res["rays"].items():
            print(" ", k)
            for h in hits:
                print("    ", h)
        print("texPixel (arena):", res.get("texPixel"))
        shot = await page.evaluate("() => window.__shotAislado || ''")
        if shot:
            with open(f"{OUT}/arena_aislada.png", "wb") as f:
                f.write(base64.b64decode(shot.split(",")[1]))
            print("captura aislada -> arena_aislada.png")
        await browser.close()

asyncio.run(main())
