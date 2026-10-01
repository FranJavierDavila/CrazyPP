#!/usr/bin/env python3
import asyncio, json
from playwright.async_api import async_playwright

JS = """() => {
    const g = window.__game;
    g._camWP = g.camera.getWorldPosition.bind(g.camera);
    g.camera.getWorldPosition = (v) => v.set(0, 1.6, 2.2);
    g.connected[0] = true; g.connected[1] = true;
    g.toggleMenu();
    g.updateMenu();
    const V3 = g.menuGroup.position.constructor;
    const Q = g.menuGroup.quaternion.constructor;
    const r = g.menuRects.find((x) => x.id === 'diff:hard');
    const u = ((r.x + r.w/2)/512 - 0.5) * 0.28;
    const v = (0.5 - (r.y + r.h/2)/640) * 0.35;
    g.menuGroup.updateMatrixWorld(true);
    const wp = new V3(u, v, 0).applyMatrix4(g.menuGroup.matrixWorld);
    const n = new V3(0,0,1).transformDirection(g.menuGroup.matrixWorld);
    const ph = g.paddleHand;
    const ray = g.rays[ph];
    ray.position.copy(wp).addScaledVector(n, 0.45);
    ray.lookAt(wp); ray.rotateY(Math.PI); ray.updateMatrix();
    ray.updateWorldMatrix(true, false);
    const rp = new V3().setFromMatrixPosition(ray.matrixWorld);
    const rq = new Q();
    ray.getWorldQuaternion(rq);
    const dir = new V3(0,0,-1).applyQuaternion(rq);
    // réplica EXACTA del raycast del juego
    const RC = ray.layers.constructor;   // por si acaso, no se usa
    const res = { ph, localPos: ray.position.toArray().map(x=>+x.toFixed(3)),
        worldPos: rp.toArray().map(x=>+x.toFixed(3)),
        dir: dir.toArray().map(x=>+x.toFixed(3)),
        panelPos: g.menuGroup.position.toArray().map(x=>+x.toFixed(3)),
        wp: wp.toArray().map(x=>+x.toFixed(3)),
        n: n.toArray().map(x=>+x.toFixed(3)),
        matrixAutoUpdate: ray.matrixAutoUpdate,
        matrixEl: ray.matrixWorld.elements.slice(12,15).map(x=>+x.toFixed(3)),
    };
    g.updateMenu();
    res.hover = g.menuHover.slice();
    res.dotVis = g.menuDots[ph].visible;
    res.lineLen = +g.menuLines[ph].scale.z.toFixed(3);
    // segundo: mismo evaluate, segundo intento tras otro updateMenu
    g.updateMenu();
    res.hover2 = g.menuHover.slice();
    return res;
}"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        out = await page.evaluate(JS)
        print(json.dumps(out, indent=1))
        await browser.close()

asyncio.run(main())
