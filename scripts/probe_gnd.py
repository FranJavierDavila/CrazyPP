#!/usr/bin/env python3
"""v2.113 · Sonda del SUELO EXTERIOR: ¿por qué se ve negro bajo el arte?

Localiza los planos de arena, los raycastea desde la cámara de la ventana
y vuelca qué objeto gana cada rayo. También guarda el lienzo P1 real.
"""
import asyncio, os, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.async_api import async_playwright

GAME = "/home/z/my-project/game"
PORT = 8933
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
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
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
            st = await page.evaluate("() => window.__PP_GAME.champs.mod.testActive()")
            if st: break
        await page.wait_for_timeout(4000)

        info = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            const mod = g.champs.mod;
            // localiza la acción del tren (tiene .cubos)
            let act = null;
            const walk = (o, d) => {
                if (!o || d > 4 || act) return;
                if (o.cubos && o.group) { act = o; return; }
                for (const k of Object.keys(o)) {
                    try { walk(o[k], d + 1); } catch (e) {}
                }
            };
            walk(mod, 0);
            if (!act) return 'sin-accion';
            const out = { groupChildren: act.group.children.length, grounds: [], ray: [] };
            const gndTex = act._gndTex;
            out.gndTex = gndTex ? {
                ok: true, rep: [gndTex.repeat.x, gndTex.repeat.y],
                w: gndTex.image && gndTex.image.width,
                wrapT: gndTex.wrapT,
            } : null;
            act.group.traverse((n) => {
                if (n.isMesh && n.geometry && n.geometry.parameters &&
                    n.geometry.parameters.width === 64) {
                    out.grounds.push({
                        pos: n.position.toArray().map((v) => +v.toFixed(1)),
                        visible: n.visible,
                        ro: n.renderOrder,
                        parentVisible: n.parent ? n.parent.visible : null,
                        matType: n.material && n.material.type,
                        transparent: n.material ? n.material.transparent : null,
                        hasMap: !!(n.material && n.material.map),
                    });
                }
            });
            // raycast desde la cámara proxy hacia la banda negra de la ventana izq
            const rc = new (g.scene.constructor.__three_rc || Object)() || null;
            return out;
        }""")
        print("info:", info)

        # raycast real con THREE del navegador
        rays = await page.evaluate("""() => {
            const g = window.__PP_GAME;
            const mod = g.champs.mod;
            let act = null;
            const walk = (o, d) => {
                if (!o || d > 4 || act) return;
                if (o.cubos && o.group) { act = o; return; }
                for (const k of Object.keys(o)) {
                    try { walk(o[k], d + 1); } catch (e) {}
                }
            };
            walk(mod, 0);
            const T = g.THREE || (g.scene.children[0] && null);
            // usa el THREE global del módulo vía import — más fácil: raycast manual
            const out = [];
            const origins = [[0.15, 1.62, 0.35]];
            const dirs = [[-0.85, -0.22, -0.45], [-0.85, -0.35, -0.45],
                          [-0.85, -0.05, -0.45], [-0.85, 0.10, -0.45]];
            // recorre TODA la escena buscando intersecciones portriangulo barato:
            // en su lugar, lista los objetos candidatos con su bounding sphere
            const objs = [];
            act.group.traverse((n) => {
                if (!n.isMesh || !n.visible) return;
                n.updateWorldMatrix(true, false);
                const bs = n.geometry.boundingSphere || n.geometry.computeBoundingSphere();
                const c = bs.clone().applyMatrix4(n.matrixWorld);
                objs.push({
                    tipo: (n.geometry.parameters && n.geometry.parameters.width === 64)
                        ? 'ARENA' : (n.material && n.material.map && n.material.alphaTest
                        ? 'alphaTest' : 'otro'),
                    centro: [c.center.x, c.center.y, c.center.z].map((v) => +v.toFixed(1)),
                    radio: +c.radius.toFixed(1),
                    ro: n.renderOrder,
                    dw: n.material ? n.material.depthWrite : null,
                    op: n.material ? n.material.opacity : null,
                    name: n.material && n.material.map && n.material.map.image &&
                          n.material.map.image.width ? n.material.map.image.width : 0,
                });
            });
            return objs.slice(0, 40);
        }""")
        for r in rays:
            print("  obj:", r)
        print("errores:", len(errs))
        await browser.close()

asyncio.run(main())
