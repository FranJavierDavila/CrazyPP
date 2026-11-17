#!/usr/bin/env python3
"""QA v3.0.5-FIS1 · PALAS CON CARÁCTER:
  1) La página carga sin pageerrors
  2) El núcleo expone __PP_PADDLE_PERKS (6 skins) y __PP_SET_PADDLE_SKIN
  3) La skin del perfil (localStorage ppxr_train_v1) sincroniza con la física
  4) window.__PP_TRAIN.applySkin() actualiza el carácter en vivo
  5) Badge V3.0.5-FIS1 en la portada 2D
  6) Captura del HUB de entrenamiento con las etiquetas de carácter
"""
import asyncio, base64, json
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT_HUB = "/home/z/my-project/download/qa_fis1_hub_perks.png"
OUT_PORTADA = "/home/z/my-project/download/qa_fis1_portada.png"

PROFILE = {
    "pts": 3000, "best": {}, "done": {},
    "unlocked": ["clasica", "fuego", "hielo", "oro", "arcoiris", "carbon"],
    "skin": "arcoiris", "fb": {"marks": 1, "line": 1, "spin": 1},
}

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))

        # 1) carga limpia con perfil arcoiris preconfigurado
        await page.goto("about:blank")
        await page.add_init_script(
            "localStorage.setItem('ppxr_train_v1', JSON.stringify(" + json.dumps(PROFILE) + "));")
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        checks = await page.evaluate("""() => {
            const r = {};
            r.perks = typeof window.__PP_PADDLE_PERKS === 'object' && !!window.__PP_PADDLE_PERKS;
            r.skins = r.perks ? Object.keys(window.__PP_PADDLE_PERKS) : [];
            r.setter = typeof window.__PP_SET_PADDLE_SKIN === 'function';
            r.equipped = window.__PP_PADDLE_SKIN || null;
            r.badge = (document.querySelector('#verBadge') || {}).textContent || '';
            r.carbonDual = r.perks && !!(window.__PP_PADDLE_PERKS.carbon && window.__PP_PADDLE_PERKS.carbon.dual);
            return r;
        }""")
        print("perfil arcoiris →", json.dumps(checks, ensure_ascii=False))
        ok = True
        if not checks["perks"]: ok = False; print("✗ FALTA __PP_PADDLE_PERKS")
        if sorted(checks["skins"]) != sorted(["clasica", "fuego", "hielo", "oro", "arcoiris", "carbon"]):
            ok = False; print("✗ skins incorrectas:", checks["skins"])
        if not checks["setter"]: ok = False; print("✗ FALTA __PP_SET_PADDLE_SKIN")
        if checks["equipped"] != "arcoiris": ok = False; print("✗ la skin del perfil NO sincronizó:", checks["equipped"])
        if not checks["carbonDual"]: ok = False; print("✗ carbon sin dual")
        if "3.0.5-FIS1" not in checks["badge"]: ok = False; print("✗ badge:", checks["badge"])
        if checks["equipped"] == "arcoiris": print("✓ skin del perfil sincronizada con el núcleo (arcoiris)")

        # 2) cambio de skin EN VIVO vía el módulo de entrenamiento
        live = await page.evaluate("""() => {
            const T = window.__PP_TRAIN;
            if (!T || !T.applySkin) return { has: false };
            T.applySkin('carbon');
            return { has: true, equipped: window.__PP_PADDLE_SKIN };
        }""")
        print("applySkin('carbon') →", json.dumps(live, ensure_ascii=False))
        if not live.get("has") or live.get("equipped") != "carbon":
            ok = False; print("✗ el cambio en vivo no llegó al núcleo")
        else:
            print("✓ applySkin del módulo sincroniza el carácter en vivo (carbon)")

        # 3) portada 2D con badge
        b64 = await page.evaluate("""() => {
            const cv = document.querySelector('canvas');
            return cv ? cv.toDataURL('image/png') : '';
        }""")
        if b64:
            open(OUT_PORTADA, "wb").write(base64.b64decode(b64.split(',', 1)[1]))
            print("portada:", OUT_PORTADA)

        # 4) HUB de entrenamiento con etiquetas de carácter
        hub = await page.evaluate("""() => {
            const g = window.__PP_GAME || window.__game;
            if (!g || !g.menuCanvas) return { ok: false };
            if (!g.menuOpen && g.toggleMenu) g.toggleMenu();
            g.menuPage = 'train';
            g.menuHover = [-1, -1];
            g.drawMenu();
            return { ok: true, png: g.menuCanvas.toDataURL('image/png') };
        }""")
        if hub.get("ok"):
            open(OUT_HUB, "wb").write(base64.b64decode(hub["png"].split(',', 1)[1]))
            print("hub:", OUT_HUB)
        else:
            print("(menú canvas no disponible en esta build — salto captura del hub)")

        await browser.close()

    print("pageerrors:", errors if errors else "ninguno")
    if errors: ok = False
    print("QA PERKS:", "OK ✅" if ok else "FALLOS ❌")
    if not ok:
        raise SystemExit(1)

asyncio.run(main())
