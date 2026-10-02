#!/usr/bin/env python3
"""Diagnóstico EN VIVO de la pala en index.html (v2.21 · caras invertidas).
1) Recorre aiPaddleMesh y vuelca el estado real de cada material
   (side, transparent, opacity, depthWrite, alphaTest, castShadow).
2) Primeros planos de la hoja por delante/detrás/rasantes para ver el
   artefacto que reporta el usuario.
Uso: python3 scripts/diag_pala_faces.py [ruta.html] [prefijo_capturas]"""
import asyncio, json, sys
from playwright.async_api import async_playwright

HTML = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/z/my-project/download/pingpong-quest3-v2/index.html"
PREFIX = sys.argv[2] if len(sys.argv) > 2 else "pala"

VIEWS = [  # (nombre, desplazamiento local respecto a la hoja, en m)
    ("front", (0.0, 0.0, 0.42)),
    ("back", (0.0, 0.0, -0.42)),
    ("rasante-der", (0.40, 0.05, 0.10)),
    ("rasante-izq", (-0.40, 0.05, 0.10)),
    ("canto", (0.44, 0.02, 0.0)),
]

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(3800)
        try:
            await page.click("#spectate", timeout=3000)   # saltar overlay de ayuda
            await page.wait_for_timeout(1200)
        except Exception:
            pass

        mats = await page.evaluate("""() => {
            const g = window.__game;
            if (!g || !g.aiPaddleMesh) return { error: 'sin juego/pala' };
            const out = [];
            g.aiPaddleMesh.traverse((o) => {
                if (!o.isMesh) return;
                const ms = Array.isArray(o.material) ? o.material : [o.material];
                for (const m of ms) {
                    out.push({
                        mesh: o.geometry?.type,
                        name: m.name || '(sin nombre)',
                        side: m.side,                 // 0=Front 1=Back 2=Double
                        transparent: m.transparent,
                        opacity: m.opacity,
                        depthWrite: m.depthWrite,
                        alphaTest: m.alphaTest,
                        castShadow: o.castShadow,
                        hasMap: !!m.map,
                    });
                }
            });
            return { mats: out };
        }""")
        print(json.dumps(mats, indent=2, ensure_ascii=False))

        # capturas: orbitar la hoja de la pala de la IA
        info = await page.evaluate("""() => {
            const g = window.__game;
            const v = Object.getPrototypeOf(g.camera.position).constructor;
            const blade = new v();
            g.aiPaddleMesh.getWorldPosition(blade);
            return { blade: blade.toArray() };
        }""")
        bx, by, bz = info["blade"]
        print("centro hoja:", info["blade"])

        for name, (dx, dy, dz) in VIEWS:
            b64 = await page.evaluate("""([bx, by, bz, dx, dy, dz]) => {
                const g = window.__game;
                const cam = g.camera;
                cam.position.set(bx + dx, by + dy, bz + dz);
                cam.lookAt(bx, by, bz);
                cam.updateMatrixWorld(true);
                g.renderer.render(g.scene, cam);
                return g.renderer.domElement.toDataURL('image/png');
            }""", [bx, by, bz, dx, dy, dz])
            import base64
            png = base64.b64decode(b64.split(',', 1)[1])
            open(f"/home/z/my-project/scripts/{PREFIX}_{name}.png", "wb").write(png)
            print("captura", name, len(png), "bytes")

        await browser.close()
    print("errores de página:", errors if errors else "ninguno")

asyncio.run(main())
