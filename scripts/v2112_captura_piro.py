#!/usr/bin/env python3
"""Captura de la PIROTECNIA v2 (determinista): aro + cohete + estela visibles."""
import subprocess, sys, time
from playwright.sync_api import sync_playwright

BASE = "/home/z/my-project/download/crazypp-v2112"
PORT = 8965
P = "/home/z/my-project/scripts"

srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT)],
                       cwd=BASE, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
time.sleep(1.2)
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox",
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        pg = browser.new_context(viewport={"width": 1100, "height": 700},
            user_agent="Mozilla/5.0 HeadlessTest").new_page()
        pg.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="load",
                timeout=90000)
        pg.wait_for_function("() => !!window.__game", timeout=60000)
        pg.wait_for_timeout(1200)
        pg.evaluate("""() => {
          for (const el of document.body.children) {
            if (el.tagName === 'CANVAS') continue;
            el.style.display = 'none';
          }
        }""")
        pg.evaluate("() => window.__game.champs.leaveAll()")
        pg.wait_for_timeout(1000)
        pg.evaluate("() => window.__game.champs.launch('locura')")
        pg.wait_for_timeout(2400)
        pg.evaluate("""() => {
          const c = window.__PP_LOCURA.ctrl();
          const g = window.__game;
          c.stage = 0;
          c.startArcade();
          g.rules.state = 'rally';
          g.freezeT = 0;
          c._rallyFired = false;
          c._pendingPower = null;
          c.firePower('pirotecnia');
          c._pendT = 0.001;
          c.update(0.01);
        }""")
        pg.wait_for_timeout(2300)   # el cartel Super Power!! se apaga solo
        pg.evaluate("""() => {
          const c = window.__PP_LOCURA.ctrl();
          const A = c._piroArt;
          for (const r of A.rockets) { r.life = -1; r.grp.visible = false; }
          for (const a of A.aros) { a.life = -1; a.mesh.visible = false; }
          c._piro.fired = 1; c._piro.next = 99;
          c._piroFire();
          // objetivo DETERMINISTA bien visible: centro-derecha de tu media mesa
          A.rockets[0].to = { x: 0.25, y: 1.61, z: -1.85 };
        }""")
        pg.wait_for_timeout(430)    # ~mitad del vuelo
        pg.screenshot(path=P + "/v2112_piro_vuelo.png")
        # y el ESTALLIDO a p👍
        pg.wait_for_timeout(420)
        pg.screenshot(path=P + "/v2112_piro_boom.png")
        print("capturas v2112_piro_vuelo.png y v2112_piro_boom.png listas")
        browser.close()
finally:
    srv.terminate()
