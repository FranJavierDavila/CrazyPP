#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xr_clic_r71.py — PRUEBA DEL CAMINO DE CLIC COMPLETO (r71).

El arnés xr_sim_r71 disparó menuClick a mano; el camino REAL del Quest es:
rayo del mando → intersectObject(panela ShapeGeometry) → hit.uv →
px virtual (pa.x + uv.x·pa.w · py = (1-uv.y)·1400) → menuRects.findIndex →
menuHover → onSelectStart → menuClick. Si CUALQUIER eslabón falla, el menú
se VE perfecto pero NADA responde — «imposible jugar».

Para cada rect importante: calcula el punto mundo sobre la panela desde
uv, apunta el rayo, espera 2 frames y comprueba hover + clic.
"""
import base64
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:3674/game.html'

ok, fails = 0, 0


def chk(cond, label, extra=''):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label + (f' → {extra}' if (extra and not cond) else ''))
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


SETUP = """() => {
  const G = window.__PP_GAME;
  Object.defineProperty(G.renderer.xr, 'isPresenting',
    { value: true, configurable: true });
  G.connected = [true, true];
  return true;
}"""

# apunta el mando 0 al PUNTO MUNDO que corresponde al uv del rect dado
# en su panela, y devuelve el diagnóstico del camino
APUNTA = """(idRect) => {
  const G = window.__PP_GAME;
  const V3 = G.menuGroup.position.constructor;
  const r = G.menuRects.find((x) => x.id === idRect);
  if (!r) return { sinRect: idRect };
  // panela dueña del rect por su x virtual
  const pa = (G._menuPanelas.length > 1
    ? G._menuPanelas : [G.menuMesh]).find((m) => {
      const p = m.userData.panela;
      return r.x >= p.x - 1 && r.x <= p.x + p.w + 1;
    }) || G._menuPanelas[0];
  const p = pa.userData.panela;
  // centro del rect en uv de la panela
  const u = ((r.x + r.w / 2) - p.x) / p.w;
  const v = 1 - (r.y + r.h / 2) / 1400;
  // punto mundo: centro de la panela + offset local (misma cuenta que el cursor)
  const centro = new V3();
  pa.getWorldPosition(centro);
  const local = new V3((u - 0.5) * p.anchoM, (v - 0.5) * p.altoM, 0.004)
    .applyQuaternion(pa.quaternion).add(pa.position);
  const mundo = G.menuGroup.localToWorld(local.clone());
  // rayo desde los OJOS con cuaternión de CÁMARA (las cámaras miran -Z
  // con lookAt — sin ambigüedad de giro): clona el rig de la cámara
  const ray = G.rays[0];
  const origen = new V3(-0.25, 1.30, 0.55);
  const camAux = G.camera.clone();
  camAux.position.copy(origen);
  camAux.lookAt(mundo);
  ray.position.copy(origen);
  ray.quaternion.copy(camAux.quaternion);
  ray.updateMatrixWorld(true);
  // camino REAL: el hover lo calcula updateMenu (HOVER_NOW, abajo)
  const dir = mundo.clone().sub(origen).normalize();
  return { u: +u.toFixed(3), v: +v.toFixed(3), rect: idRect,
           panela: p.id, hayRay: !!ray, world: [ +mundo.x.toFixed(2), +mundo.y.toFixed(2), +mundo.z.toFixed(2) ] };
}"""

HOVER_NOW = """() => {
  const G = window.__PP_GAME;
  // fuerza una pasada del bloque de rayo como updateMenu (sin esperar RAF):
  // llamamos updateMenu(0.016) con el menú abierto — es el camino real
  try { G.updateMenu(0.016); } catch (e) { return { error: String(e) }; }
  return { hover: (G.menuHover || []).join(','),
           hitPx: G._menuHitPx ? JSON.stringify(G._menuHitPx[0]) : null };
}"""


def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3674', '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    errores = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(args=[
                '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
                '--autoplay-policy=no-user-gesture-required'])
            page = browser.new_page(viewport={'width': 1280, 'height': 800})
            page.on('pageerror', lambda e: errores.append(str(e)[:400]))
            page.goto(URL, wait_until='domcontentloaded')
            page.wait_for_function('!!window.__PP_GAME', timeout=60000)
            page.wait_for_timeout(1200)
            page.evaluate(SETUP)
            page.evaluate("""() => { const G = window.__PP_GAME;
              if (!G.menuOpen) G.toggleMenu(); }""")
            page.wait_for_timeout(500)

            # — rects clave del MAIN en la C y en las laterales —
            for idr in ['start', 'page:opts', 'tab:multi', 'lang:es', 'homehall']:
                d = page.evaluate(APUNTA, idr)
                if d.get('sinRect'):
                    print(f'   [{idr}] sin rect en main')
                    continue
                h = page.evaluate(HOVER_NOW)
                print(f'   [{idr}] panela={d.get("panela")} u={d.get("u")} v={d.get("v")} → hover={h.get("hover")} px={h.get("hitPx")}')
                chk(str(h.get('hover', '')).split(',')[0] != '-1',
                    f'clic-path: el rayo HALLA el rect {idr}', str(h))
                # clic real
                page.evaluate("""() => { const G = window.__PP_GAME;
                  if (G.menuHover[0] >= 0) G.onSelectStart(0); }""")
                page.wait_for_timeout(120)
                # volver a main si el clic cambió de página
                page.evaluate("""() => { const G = window.__PP_GAME;
                  if (G.menuPage !== 'main') { G.menuPage = 'main'; G.drawMenu(); } }""")
                page.wait_for_timeout(80)

            # — y la ATRÁS de la concha en una página nueva —
            page.evaluate("""() => { const G = window.__PP_GAME;
              G.menuPage = 'multi'; G._mjMode = null; G.drawMenu(); }""")
            page.wait_for_timeout(150)
            d = page.evaluate(APUNTA, 'page:main')
            h = page.evaluate(HOVER_NOW)
            print(f"   [page:main en multi] → hover={h.get('hover')}")
            chk(str(h.get('hover', '')).split(',')[0] != '-1',
                'clic-path: ATRÁS de la concha hallado en página 1-panela', str(h))

            chk(not errores, 'sin pageerrors', errores[:2])
            if errores:
                for e in errores[:3]:
                    print('   pageerror:', e)
            browser.close()
    finally:
        server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
