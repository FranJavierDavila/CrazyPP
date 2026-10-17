#!/usr/bin/env python3
"""Captura visual de la sala de ESTACIÓN ORBITAL (V3.2.1-ORB2): renderiza la
escena con una cámara manual desde 4 puntos de vista (general, mapa con tapas,
cartel SuperPower a la altura de la red, rival con expresión) y vuelca el
canvas 3D a PNG. No toca el estado del juego (sólo render 1 frame por toma)."""
import asyncio
import base64
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
OUT = "/home/z/my-project/download/qa_orb2_{tag}.png"

SHOTS = """
async () => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  G.champs.launch('estacion_orbital');
  await new Promise(r => setTimeout(r, 6000));          // import + build + texturas
  const mod = G.champs.moduleIfLoaded('estacion_orbital');
  const ctrl = mod && mod.controller;
  if (!ctrl || !ctrl.rivalMesh) return { error: 'sin ctrl/build' };
  const V3 = G.camera.position.constructor;
  const mkCam = (px, py, pz, tx, ty, tz, fov) => {
    const cam = G.camera.clone();
    cam.aspect = 16 / 9;
    cam.fov = fov;
    cam.updateProjectionMatrix();
    cam.position.set(px, py, pz);
    cam.lookAt(new V3(tx, ty, tz));
    return cam;
  };
  const snap = (cam) => {
    G.renderer.render(G.scene, cam);
    return G.renderer.domElement.toDataURL('image/png');
  };
  const out = {};

  // 1 · GENERAL: mesa + ASTRO a la derecha + cartel de bienvenida al fondo
  out.general = snap(mkCam(0, 1.62, 0.75, 0.55, 1.02, -3.2, 78));

  // 2 · MAPA (pared izquierda) con las tapas de las etapas por disputar
  out.mapa = snap(mkCam(-0.35, 1.55, 0.55, -2.98, 1.5, -1.1, 68));

  // 3 · CARTEL SUPERPOWER a la altura de la red (anuncio de la casa)
  try {
    ctrl.pwSign.show(ctrl._A('powermeteoritos.png'));
    ctrl.pwSign.update(0.016); ctrl.pwSign.update(0.80);   // a mitad de parada
    out.power = snap(mkCam(0, 1.62, 0.55, 0, 1.02, -1.6, 74));
    ctrl.pwSign.hide();
  } catch (e) { out.powerErr = String(e); }

  // 4 · RIVAL con expresión (laughing) en su spot del forajido
  ctrl.rivalEstado('laughing');
  await new Promise(r => setTimeout(r, 700));            // decode del webp
  out.rival = snap(mkCam(0.9, 1.6, -1.15, 1.62, 1.15, -4.5, 70));

  // datos de posición para el informe
  out.meta = {
    rival: ctrl.rivalMesh.position.toArray().map(n => +n.toFixed(3)),
    pwAnchor: (ctrl.pwSign && ctrl.pwSign.group) ? ctrl.pwSign.group.position.toArray().map(n => +n.toFixed(3)) : null,
    cartel: ctrl.cartel.position.toArray().map(n => +n.toFixed(3)),
    version: window.__PP_VERSION || '',
  };
  return out;
}
"""


async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)
        data = await page.evaluate(SHOTS)
        if data.get("error"):
            print("ERROR:", data["error"])
            await browser.close()
            sys.exit(1)
        for tag in ("general", "mapa", "power", "rival"):
            b64 = data.get(tag)
            if not b64:
                print(f"{tag:8s}: SIN CAPTURA" + (f" ({data.get('powerErr')})" if data.get("powerErr") else ""))
                continue
            png = base64.b64decode(b64.split(",", 1)[1])
            path = OUT.format(tag=tag)
            with open(path, "wb") as f:
                f.write(png)
            print(f"{tag:8s}: {path} ({len(png):,} B)")
        print("meta     :", data.get("meta"))
        await browser.close()
    print("pageerrors:", errors or "ninguno")
    print("RESULTADO :", "OK" if not errors and data.get("meta") else "REVISAR")

asyncio.run(main())
