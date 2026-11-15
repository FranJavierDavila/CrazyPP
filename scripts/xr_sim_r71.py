#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xr_sim_r71.py — ARNÉS DE SIMULACIÓN XR (r71 · caza del bloqueo).

Reproduce el flujo del dueño en la Quest SIN casco:
  · xr.isPresenting = true + 2 mandos falsos conectados y POSADOS (el humo
    headless nunca ejercitó el bloque del rayo por mando: connected=false).
  · A · abrir menú: ¿nace anclado delante de la mirada (dist ~1,15, frente)?
  · B · navegar las landings r70 (multi/rankini/champs/carrera/train) con
    el rayo real (hover + onSelectStart) — excepciones y lados montados.
  · C · JUGAR desde el menú: ¿cierra el menú? ¿arranca el partido?
  · D · 300 frames JUGANDO con mandos vivos: ¿menuGroup.visible sigue
    false? ¿hay pageerrors? ¿el gatillo SIRVE (no clica menú fantasma)?
  · E · abrir menú en pleno rally y cerrarlo: ¿el juego sigue?
  · F · heal r114: mover el rig 3 m con el menú anclado (re-ancla honesto).
"""
import base64
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:3673/game.html'

ok, fails = 0, 0


def chk(cond, label, extra=''):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label + (f' → {extra}' if (extra and not cond) else ''))
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


SETUP = """() => {
  const G = window.__PP_GAME;
  // isPresenting es un getter sin setter en three.js: lo sombreo en la instancia
  Object.defineProperty(G.renderer.xr, 'isPresenting',
    { value: true, configurable: true });
  G.connected = [true, true];
  return { rays: !!(G.rays && G.rays[0] && G.rays[1]),
           nRays: (G.rays || []).length,
           presentando: G.renderer.xr.isPresenting,
           cam: !!G.camera, rig: !!G.rig };
}"""

POSE = """(aimIdx) => {
  // apunta AMBOS mandos al centro de la panela C (forward del juego = -Z:
  // lookAt deja +Z hacia el objetivo → giro 180° en Y después)
  const G = window.__PP_GAME;
  const pa = (G._menuPanelas || []).find((m) => m.userData.panela.id === 'C')
    || G.menuMesh;
  const target = new G.menuGroup.position.constructor();
  pa.getWorldPosition(target);
  for (let i = 0; i < 2; i++) {
    if (!G.rays[i]) {
      const ray = new G.rig.constructor();          // Group (es un Object3D)
      G.rig.add(ray);
      G.rays[i] = ray;
    }
    const ray = G.rays[i];
    ray.position.set(i === 0 ? -0.25 : 0.25, 1.30, 0.55);
    ray.lookAt(target);
    ray.rotateY(Math.PI);
    ray.updateMatrixWorld(true);
  }
  return true;
}"""

SNAP = """() => {
  const G = window.__PP_GAME;
  const V3 = G.menuGroup.position.constructor;
  const cam = G.camera.getWorldPosition(new V3());
  const q = G.camera.getWorldQuaternion(new (G.menuGroup.quaternion.constructor)());
  const fwd = new V3(0, 0, -1).applyQuaternion(q);
  const gp = G.menuGroup.position.clone();
  const toG = gp.clone().sub(cam);
  const dist = toG.length();
  const frente = toG.normalize().dot(fwd);
  return {
    menuOpen: G.menuOpen,
    visible: G.menuGroup.visible,
    page: G.menuPage,
    dist: +dist.toFixed(3),
    frente: +frente.toFixed(3),
    pin: G.menuPin,
    estado: G.rules.state,
    lados: (G._menuLados || []).join(''),
    nPanelas: G._menuPanelas.length,
    hover: (G.menuHover || []).join(','),
  };
}"""


def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3673', '--bind', '127.0.0.1',
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
            page.wait_for_timeout(1500)

            # — arranque XR simulado —
            st = page.evaluate(SETUP)
            chk(st.get('cam'), 'XR simulado: cámara presente')
            chk(st.get('rig'), 'XR simulado: rig presente')

            # — A · apertura del menú (flujo toggleMenu real) —
            page.evaluate("""() => {
              const G = window.__PP_GAME;
              if (!G.menuOpen) G.toggleMenu();
            }""")
            page.wait_for_timeout(700)
            s = page.evaluate(SNAP)
            print('   A:', s)
            chk(s['menuOpen'] and s['visible'], 'A: menú abierto y visible')
            chk(1.05 <= s['dist'] <= 1.30, 'A: arco a ~1,15 m de la cámara', s['dist'])
            chk(s['frente'] > 0.85, 'A: menú DELANTE de la mirada (anclado)', s['frente'])
            chk(s['pin'], 'A: chincheta puesta al abrir')

            # — B · navegar landings r70 con el rayo posado —
            for pg, esperado in [('multi', 'C'), ('rankini', 'C'), ('champs', 'CR'),
                                 ('carrera', 'C'), ('train', 'CR')]:
                page.evaluate("""(pg) => {
                  const G = window.__PP_GAME;
                  G.menuPage = pg;
                  if (pg === 'multi') G._mjMode = null;
                  G.drawMenu();
                }""", pg)
                page.wait_for_timeout(120)
                idx = page.evaluate("""() => {
                  const G = window.__PP_GAME;
                  const i = G.menuRects.findIndex((r) => r.id === 'page:main');
                  return i >= 0 ? i : 0;
                }""")
                page.evaluate(POSE, idx)
                page.wait_for_timeout(250)
                s = page.evaluate(SNAP)
                print(f'   B[{pg}]:', s['lados'], s['nPanelas'], 'hover=' + s['hover'])
                chk(s['lados'] == esperado, f'B: {pg} lados {esperado}', s['lados'])
                chk(not errores, f'B: {pg} sin pageerrors', errores[:1])

            # — C · volver a main y JUGAR —
            page.evaluate("""() => {
              const G = window.__PP_GAME;
              G.menuPage = 'main';
              G.drawMenu();
              const i = G.menuRects.findIndex((r) => r.id === 'start');
              G.menuClick(i, 0);
            }""")
            page.wait_for_timeout(600)
            s = page.evaluate(SNAP)
            print('   C:', s)
            chk(not s['menuOpen'] and not s['visible'],
                'C: JUGAR cierra el menú (visible=false)')
            chk(s['estado'] not in ('over', ''), 'C: partido en marcha', s['estado'])

            # — D · 300 frames jugando con mandos vivos + gatillo —
            page.evaluate(POSE, 0)
            page.evaluate("""() => { const G = window.__PP_GAME;
              G.menuHover = [-1, -1]; }""")
            vis_bad = 0
            for _ in range(6):
                page.wait_for_timeout(500)
                s = page.evaluate(SNAP)
                if s['visible'] or s['menuOpen']:
                    vis_bad += 1
            chk(vis_bad == 0, 'D: 3 s jugando — el menú NO reaparece', vis_bad)
            s = page.evaluate(SNAP)
            print('   D:', s)
            chk(not errores, 'D: sin pageerrors jugando', errores[:2])

            # gatillo en pleno juego: debe SERVIR (no clicar menú)
            ev0 = page.evaluate("""() => {
              const G = window.__PP_GAME;
              const antes = G.rules.state + '|' + G.menuOpen;
              G.onSelectStart(0);
              return antes;
            }""")
            page.wait_for_timeout(400)
            s = page.evaluate(SNAP)
            chk(not s['menuOpen'], 'D: gatillo con menú cerrado NO abre nada',
                ev0 + '→' + s['estado'])

            # — E · abrir el menú EN PLENO RALLY y cerrarlo —
            page.evaluate("""() => { const G = window.__PP_GAME;
              if (!G.menuOpen) G.toggleMenu(); }""")
            page.wait_for_timeout(400)
            s = page.evaluate(SNAP)
            chk(s['menuOpen'] and s['visible'], 'E: menú abre en pleno rally')
            chk(1.05 <= s['dist'] <= 1.30 and s['frente'] > 0.85,
                'E: y nace ANCLADO delante', f"dist={s['dist']} frente={s['frente']}")
            page.evaluate("""() => { const G = window.__PP_GAME;
              if (G.menuOpen) G.toggleMenu(); }""")
            page.wait_for_timeout(400)
            s = page.evaluate(SNAP)
            chk(not s['visible'], 'E: menú cierra y desaparece')

            # — F · heal r114: el rig viaja 3 m con el menú anclado —
            page.evaluate("""() => { const G = window.__PP_GAME;
              if (!G.menuOpen) G.toggleMenu();
              G.menuGroup.position.set(50, 50, 50);   // ancla "vieja" en otra escena
              G.rig.position.z += 3;                   // viaje del rig
            }""")
            page.wait_for_timeout(500)
            s = page.evaluate(SNAP)
            print('   F:', s)
            chk(s['visible'], 'F: tras el viaje el menú REAPARECE (heal)')
            chk(s['frente'] > 0.85 and s['dist'] < 1.6,
                'F: re-anclado delante del jugador', f"dist={s['dist']} frente={s['frente']}")

            chk(not errores, 'SIN pageerrors en TODO el flujo', errores[:3])
            if errores:
                for e in errores[:5]:
                    print('   pageerror:', e)
            browser.close()
    finally:
        server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
