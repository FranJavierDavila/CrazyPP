#!/usr/bin/env python3
"""Capturas v2.16: menú de muñeca con láser de la PALA apuntando (sin overlay)."""
import asyncio
from playwright.async_api import async_playwright

HTML = "/home/z/my-project/download/pingpong-quest3-v2/index.html"
OUT = "/home/z/my-project/scripts"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        await page.goto(f"file://{HTML}")
        await page.wait_for_timeout(4200)
        await page.click("#spectate")
        await page.wait_for_timeout(800)
        await page.evaluate("""() => {
            const g = window.__game;
            g.setTheme('pabellon', true);
            g.menuGroup.position.set(0.62, 1.02, -0.72);
            g.menuGroup.lookAt(2.2, 1.5, 1.4);
            g.toggleMenu();
            g.menuGroup.updateMatrixWorld(true);
        }""")
        await page.wait_for_timeout(500)
        await page.screenshot(path=f"{OUT}/shot_v216_menu.png")

        # láser de la PALA apuntando a 'Difícil' (v2.16: ambas manos apuntan)
        await page.evaluate("""() => {
            const g = window.__game;
            const V3 = g.menuGroup.position.constructor;
            const M4 = g.menuGroup.matrixWorld.constructor;
            const ph = g.paddleHand;
            const idx = g.menuRects.findIndex((r) => r.id === 'diff:hard');
            const r = g.menuRects[idx];
            const u = ((r.x + r.w / 2) / 512 - 0.5) * 0.28;
            const v = (0.5 - (r.y + r.h / 2) / 640) * 0.35;
            const wp = new V3(u, v, 0).applyMatrix4(g.menuGroup.matrixWorld);
            const n = new V3(0, 0, 1).transformDirection(g.menuGroup.matrixWorld);
            const rayPos = new V3().copy(wp).addScaledVector(n, 0.55);
            rayPos.x += 0.25;               // el rayo viene ligeramente en diagonal
            const ray = g.rays[ph];
            ray.position.copy(rayPos);
            ray.quaternion.setFromRotationMatrix(
                new M4().lookAt(rayPos, wp, new V3(0, 1, 0)));
            ray.updateMatrix();
            // láser visible desde el mando hasta el panel
            const line = g.menuLines[ph];
            line.visible = true;
            line.position.copy(rayPos);
            line.quaternion.copy(ray.quaternion);
            line.scale.z = new V3().copy(wp).sub(rayPos).length();
            // cursor en el punto de impacto
            const dot = g.menuDots[ph];
            dot.visible = true;
            dot.position.set(u, v, 0.004);
            // hover pintado en el botón
            g.menuHover[ph] = idx;
            g.menuHover[1 - ph] = -1;
            g.drawMenu();
        }""")
        await page.wait_for_timeout(300)
        await page.screenshot(path=f"{OUT}/shot_v216_menu_hover.png")
        await browser.close()
    print("capturas listas")

asyncio.run(main())
