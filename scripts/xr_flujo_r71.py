#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xr_flujo_r71.py — FLUJO COMPLETO DEL DUEÑO con rays posados por MATRIX.

Los espacios targetRay tienen matrixAutoUpdate=false (por eso xr_clic
fallaba): se posan escribiendo .matrix directly. Prueba el informe r71:
  A · arranque real (onSessionStart) → menú nace ANCLADO Y FIJO (pin True).
  B · apuntar PLAY con el rayo real → hover → select → el menú CIERRA y
      el partido arranca (fin del «bloquea el juego»).
  C · girar la mirada 90° con la chincheta puesta → el menú NO sigue
      (queda fijo donde nació — «queda fijo salvo que le quitemos la
      chincheta»).
"""
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3683', '--bind', '127.0.0.1',
     '--directory', '/home/z/my-project/upload/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
ok, fails = 0, 0


def chk(cond, label, extra=''):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label + (f' → {extra}' if (extra and not cond) else ''))
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


AIM = """(idRect) => {
  const THREEM = window.__PP_THREE;
  const G = window.__PP_GAME;
  const r = G.menuRects.find((x) => x.id === idRect);
  if (!r) return 'sinRect:' + idRect;
  const pa = (G._menuPanelas || []).find((m) => {
    const p = m.userData.panela;
    return r.x >= p.x - 1 && r.x <= p.x + p.w + 1;
  }) || G.menuMesh;
  const p = pa.userData.panela;
  const u = ((r.x + r.w / 2) - p.x) / p.w;
  const v = 1 - (r.y + r.h / 2) / 1400;
  const V3 = THREEM.Vector3, Q4 = THREEM.Quaternion, M4 = THREEM.Matrix4;
  const mundo = G.menuGroup.localToWorld(new V3(
    (u - 0.5) * p.anchoM, (v - 0.5) * p.altoM, 0.004));
  const ray = G.rays[0];
  // el ray es HIJO DEL RIG (traslación al hall): origen en LOCAL del rig,
  // rotación en MUNDO (rig sin rotación → cuaternión local idéntico)
  const ojos = G.camera.getWorldPosition(new V3());
  const origenW = ojos.clone().add(new V3(-0.2, -0.25, 0.3));
  const origenL = G.rig.worldToLocal(origenW.clone());
  const q = new Q4().setFromRotationMatrix(
    new M4().lookAt(origenW, mundo, new V3(0, 1, 0)));
  ray.matrixAutoUpdate = false;
  ray.matrix.compose(origenL, q, new V3(1, 1, 1));
  ray.matrixWorldNeedsUpdate = true;
  ray.updateMatrixWorld(true);
  return { id: idRect, ok: true };
}"""

try:
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader',
                                     '--enable-unsafe-swiftshader'])
        page = b.new_page(viewport={'width': 960, 'height': 600})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:300]))
        page.goto('http://127.0.0.1:3683/game.html', wait_until='domcontentloaded')
        page.wait_for_function('!!window.__PP_GAME', timeout=60000)
        page.wait_for_timeout(1000)
        page.evaluate("""() => {
          const G = window.__PP_GAME;
          window.__PP_THREE = G.rig.constructor;
          while (window.__PP_THREE.name !== 'Group') { /* Group */ }
          Object.defineProperty(G.renderer.xr, 'isPresenting',
            { value: true, configurable: true });
          G.connected = [true, true];
        }""")
        # THREE real via import dinámico para clases exactas
        page.evaluate("""async () => {
          const THREE = await import('three');
          window.__PP_THREE = THREE;
        }""")

        # — A · arranque real —
        page.evaluate("""() => { const G = window.__PP_GAME;
          G.pendingMode = 'match'; G.onSessionStart(); }""")
        page.wait_for_timeout(700)
        s = page.evaluate("""() => { const G = window.__PP_GAME;
          const V3 = window.__PP_THREE.Vector3;
          const ojos = G.camera.getWorldPosition(new V3());
          return { pin: G.menuPin, open: G.menuOpen, page: G.menuPage,
                   pos: G.menuGroup.position.toArray().map((x) => +x.toFixed(2)) }; }""")
        print('   A:', s)
        chk(s['open'] and s['pin'], 'A: arranque con menú ANCLADO (chincheta puesta)')
        chk(s['page'] == 'main', 'A: nace en el HUB (main)')

        # — B · PLAY con el rayo real (todo en UN tick: posar → 2 frames
        #      RAF (asienta matrices) → hover → select → verificar) —
        rb = page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const THREEM = window.__PP_THREE;
          const V3 = THREEM.Vector3, Q4 = THREEM.Quaternion, M4 = THREEM.Matrix4;
          const r = G.menuRects.find((x) => x.id === 'start');
          const pa = (G._menuPanelas || []).find((m) => {
            const p = m.userData.panela;
            return r.x >= p.x - 1 && r.x <= p.x + p.w + 1;
          }) || G.menuMesh;
          const p = pa.userData.panela;
          const u = ((r.x + r.w / 2) - p.x) / p.w;
          const v = 1 - (r.y + r.h / 2) / 1400;
          const mundo = G.menuGroup.localToWorld(new V3(
            (u - 0.5) * p.anchoM, (v - 0.5) * p.altoM, 0.004));
          const ray = G.rays[0];
          const ojos = G.camera.getWorldPosition(new V3());
          const origenW = ojos.clone().add(new V3(-0.2, -0.25, 0.3));
          const origenL = G.rig.worldToLocal(origenW.clone());
          const q = new Q4().setFromRotationMatrix(
            new M4().lookAt(origenW, mundo, new V3(0, 1, 0)));
          ray.matrixAutoUpdate = false;
          ray.matrix.compose(origenL, q, new V3(1, 1, 1));
          ray.matrixWorldNeedsUpdate = true;
          ray.updateMatrixWorld(true);
          const dorme = (ms) => new Promise((r2) => setTimeout(r2, ms));
          await new Promise((r2) => requestAnimationFrame(
            () => requestAnimationFrame(r2)));   // 2 frames reales de render
          await dorme(80);
          const hover = G.menuHover[0];
          const rectId = hover >= 0 ? G.menuRects[hover].id : null;
          if (hover >= 0) G.onSelectStart(0);
          await dorme(400);
          return { hover, rectId, open: G.menuOpen, vis: G.menuGroup.visible,
                   estado: G.rules.state };
        }""")
        print('   B:', rb)
        chk(rb.get('hover', -1) >= 0, 'B: el rayo REAL halla PLAY (hover ≥ 0)', rb.get('hover'))
        chk(rb.get('rectId') == 'start', 'B: el hover cae en el botón PLAY', rb.get('rectId'))
        chk(not rb.get('open') and not rb.get('vis'),
            'B: PLAY cierra el menú (se puede jugar)')
        chk(rb.get('estado') not in ('', 'over'), 'B: partido en marcha', rb.get('estado'))

        # — C · girar la mirada 90° con chincheta: el menú NO sigue —
        p0 = page.evaluate("""() => { const G = window.__PP_GAME;
          return G.menuGroup.position.toArray().map((x) => +x.toFixed(3)).join(','); }""")
        page.evaluate("""() => { const G = window.__PP_GAME;
          const V3 = window.__PP_THREE.Vector3;
          const ojos = G.camera.getWorldPosition(new V3());
          G.camera.lookAt(ojos.clone().add(new V3(1, 0, 0)));   // mirada 90°
          G.camera.updateMatrixWorld(true); }""")
        page.wait_for_timeout(700)
        p1 = page.evaluate("""() => { const G = window.__PP_GAME;
          return { pos: G.menuGroup.position.toArray().map((x) => +x.toFixed(3)).join(','),
                   pin: G.menuPin }; }""")
        print(f'   C: pos antes={p0} · después={p1["pos"]} · pin={p1["pin"]}')
        chk(p0 == p1['pos'], 'C: chincheta puesta → el menú NO sigue la mirada (FIJO)')
        chk(p1['pin'], 'C: la chincheta sigue puesta')

        chk(not errs, 'sin pageerrors en todo el flujo', errs[:2])
        if errs:
            for e in errs[:3]:
                print('   pageerror:', e)
        b.close()
finally:
    server.terminate()
print(f'RESULTADO: {ok} OK · {fails} fallos')
sys.exit(1 if fails else 0)
