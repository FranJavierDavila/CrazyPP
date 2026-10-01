#!/usr/bin/env python3
import asyncio, json
from playwright.async_api import async_playwright

JS = """() => {
    const g = window.__game;
    const ray = g.rays[0];
    const V3 = ray.position.constructor;
    // ¿qué clase es y qué tiene sobrescrito?
    const protoKeys = [];
    let p = Object.getPrototypeOf(ray);
    const chain = [];
    while (p && chain.length < 5) { chain.push(p.constructor.name); p = Object.getPrototypeOf(p); }
    for (const k of ['lookAt','updateMatrix','getWorldQuaternion']) {
        protoKeys.push(k + ':' + (ray[k] === Object.getPrototypeOf(ray)[k] ? 'proto' : 'OWN'));
    }
    // lookAt en un objeto limpio vs el ray
    const grp = new (g.scene.constructor)();
    const a = new (ray.constructor === grp.constructor ? grp.constructor : Object.getPrototypeOf(ray).constructor)();
    // prueba directa: lookAt hacia -Z desde (0,0,1)
    const t = new V3(0, 0, 0);
    ray.position.set(0, 0, 1);
    ray.lookAt(t);
    const q1 = ray.quaternion.toArray();
    ray.rotateY(Math.PI);
    const q2 = ray.quaternion.toArray();
    const dir = new V3(0,0,-1).applyQuaternion(ray.getWorldQuaternion(new (ray.quaternion.constructor)()));
    return { chain, protoKeys, q1: q1.map(x=>+x.toFixed(3)), q2: q2.map(x=>+x.toFixed(3)),
             dirAfter: dir.toArray().map(x=>+x.toFixed(3)) };
}"""

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto("file:///home/z/my-project/download/pingpong-quest3-v2/index.html")
        await page.wait_for_timeout(4200)
        print(json.dumps(await page.evaluate(JS), indent=1))
        await browser.close()

asyncio.run(main())
