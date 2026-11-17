#!/usr/bin/env python3
"""QA v3.0.7-PLAY1 · PRO CIRCUITO (gamificación del entrenamiento):
  1) la página carga sin pageerrors y badge V3.0.7-PLAY1
  2) INTRO oficial del dueño (200 · 5,78 MB · parsea 1920x1080/10,05 s)
  3) FIS1 intacta (DIMS.physicsRealism=1, paddlePerks=1, trainGamify=1, 6 pieles)
  4) COMBO: 4 okHits seguidos → ×2 activo y puntos 1+1+1+2 = 5 (juez intacto)
  5) COMPLETADO t1a sin fallos → 3★, logro PERFECTO, sesion 22 pts
     (1+1+1+2+2 con combo + 15 de bonus), ronda reiniciada
  6) con 1 fallo en la ronda → precisión 83 % y la estrella se queda en 3★
  7) DIMS.trainGamify=0 (modo puro): 4 aciertos = 4 pts exactos, sin combo
  8) drawHub/drawArea ejecutan sin excepción (barra de nivel + logros + estrellas)
  9) prueba de saques t4a: ciclo soporte → lanzamiento → gatillo → juez (regresión)
"""
import asyncio, json, urllib.request
from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(6000)

        base = await page.evaluate("""() => {
          const out = {};
          out.badge = (document.querySelector('#verBadge') || {}).textContent || '';
          out.perks = window.__PP_PADDLE_PERKS ? Object.keys(window.__PP_PADDLE_PERKS).length : 0;
          out.dims = (window.__ppDebug && window.__ppDebug.DIMS) ? {
            fis: window.__ppDebug.DIMS.physicsRealism,
            perks: window.__ppDebug.DIMS.paddlePerks,
            gamify: window.__ppDebug.DIMS.trainGamify,
          } : null;
          out.introSrc = (document.getElementById('introvid') || {}).getAttribute?.('src') || '';
          const iv = document.getElementById('introvid');
          out.introMeta = iv ? { w: iv.videoWidth, h: iv.videoHeight, dur: iv.duration } : null;
          return out;
        }""")

        req = urllib.request.Request("http://localhost:3000/assets/intro.mp4", method="HEAD")
        with urllib.request.urlopen(req) as r:
            intro_status = r.status
            intro_len = int(r.headers.get("Content-Length", "0"))
        print("badge        :", base["badge"])
        print("intro.mp4    :", intro_status, f"{intro_len/1e6:.2f} MB", base["introMeta"])
        print("pieles/DIMS  :", base["perks"], base["dims"])

        # ── PRO CIRCUITO: combo, estrellas, logros, precisión, modo puro ──
        gam = await page.evaluate("""() => {
          const g = window.__PP_GAME, tr = window.__PP_TRAIN;
          if (!g || !tr) return { err: 'sin juego/módulo' };
          const T = tr.__test, dbg = tr.__debug;
          const out = {};
          // limpiar perfil para aritmética determinista
          dbg.S.pts = 0; dbg.S.stars = {}; dbg.S.acc = {}; dbg.S.ach = {};
          dbg.S.comboBest = 0; dbg.S.best = {};
          window.__ppDebug.DIMS.trainGamify = 1;

          tr.stopMode(g); tr.startMode(g, 't1a');
          // 3 aciertos: racha 1-3, sin combo
          T.okHit('ok_zona', 1); T.okHit('ok_zona', 1); T.okHit('ok_zona', 1);
          out.antes = { sess: dbg.st.sessPts, streak: dbg.st.streak };       // 3 / 3
          // 4.º acierto: racha 4 → COMBO ×2
          T.okHit('ok_zona', 1);
          out.combo = { sess: dbg.st.sessPts, comboBest: tr.state.comboBest }; // 5 / 2
          // 5.º acierto: meta alcanzada → bonus 15 + 3★ + logro PERFECTO
          T.okHit('ok_zona', 1);
          out.fin = {
            sess: dbg.st.sessPts,                                            // 22
            stars: tr.state.stars.t1a,                                       // 3
            p1: tr.state.ach.p1,                                             // 1
            streak: dbg.st.streak, hits: tr.state.round.hits,                // 0 / 0
          };
          // ronda con UN fallo: 5 aciertos → 2★ (se guarda la mejor: 3★).
          // acc se limpia antes para verificar el CÁLCULO de la ronda
          // (83 % = 5 aciertos / 6 intentos); récord queda como mejor.
          T.failHit('mal_fuera');
          out.fallo = { faults: tr.state.round.faults };                     // 1
          dbg.S.acc = {};
          for (let i = 0; i < 5; i++) T.okHit('ok_zona', 1);
          out.ronda2 = {
            sess: dbg.st.sessPts,                                            // 44
            acc: tr.state.acc.t1a,                                           // 83
            stars: tr.state.stars.t1a,                                       // 3 (máximo)
          };

          // modo puro profesional: sin combo ni estrellas
          window.__ppDebug.DIMS.trainGamify = 0;
          tr.stopMode(g); tr.startMode(g, 't1a');
          for (let i = 0; i < 4; i++) T.okHit('ok_zona', 1);
          out.puro = { sess: dbg.st.sessPts, streak: dbg.st.streak };        // 4 / 4
          window.__ppDebug.DIMS.trainGamify = 1;
          tr.stopMode(g);

          // humo de dibujo: drawHub + drawArea con canvas real (sin excepciones)
          const cv = document.createElement('canvas');
          cv.width = 1024; cv.height = 1500;
          const c = cv.getContext('2d');
          const rects = [];
          const btn = (id) => { rects.push(id); };
          const label = () => { /* */ };
          tr.drawHub(g, c, rects, btn, label);
          tr.drawArea(g, c, rects, btn, label);
          out.hubDraw = { rects: rects.length, err: null };
          return out;
        }""")
        print("gam antes    :", gam.get("antes"))
        print("gam combo    :", gam.get("combo"))
        print("gam fin      :", gam.get("fin"))
        print("gam fallo    :", gam.get("fallo"))
        print("gam ronda2   :", gam.get("ronda2"))
        print("gam puro     :", gam.get("puro"))
        print("gam hubDraw  :", gam.get("hubDraw"))

        # ── prueba de saques t4a (regresión SRV1) ──────────────────────────
        tee = await page.evaluate("""() => {
          const g = window.__PP_GAME, tr = window.__PP_TRAIN;
          if (!g || !tr) return { err: 'sin juego/módulo' };
          tr.stopMode(g);
          tr.startMode(g, 't4a');
          const C = window.__ppDebug.DIMS.tableCenterZ, HL = window.__ppDebug.DIMS.tableHalfLength;
          const b = g.ball;
          for (let i = 0; i < 90; i++) tr.tick(1/60);          // 1,5 s → serveTee
          const snap1 = { phase: tr.__debug.st.phase, x: b.pos.x, y: b.pos.y, z: b.pos.z,
                          teeEsperadoZ: C + HL + 0.35 };
          for (let i = 0; i < 80; i++) tr.tick(1/60);          // 1,33 s → lanzamiento
          const snap2 = { phase: tr.__debug.st.phase, vy: b.vel.y,
                          reach0: g.controllerPaddles[0] ? g.controllerPaddles[0].extraReach : -1 };
          tr.serveTrigger();                                    // gatillo (idempotente en vuelo)
          return { snap1, snap2, trainV3: g.trainV3, calib: !!g.calib };
        }""")
        print("t4a soporte  :", tee.get("snap1"))
        print("t4a lanzado  :", tee.get("snap2"), "calib:", tee.get("calib"), "trainV3:", tee.get("trainV3"))

        await page.screenshot(path="/home/z/my-project/download/qa_play1_portada.png")
        await browser.close()

        ok = (errors == []
              and "3.0.7" in base["badge"]
              and intro_status == 200 and 5.0e6 < intro_len < 6.5e6
              and base["introMeta"] and base["introMeta"]["w"] == 1920
              and base["introMeta"]["h"] == 1080
              and base["introMeta"]["dur"] and 9.5 < base["introMeta"]["dur"] < 10.6
              and base["perks"] == 6
              and base["dims"] and base["dims"]["fis"] == 1 and base["dims"]["perks"] == 1
              and base["dims"]["gamify"] == 1
              and gam.get("antes") == {"sess": 3, "streak": 3}
              and gam.get("combo") == {"sess": 5, "comboBest": 2}
              and gam.get("fin") == {"sess": 22, "stars": 3, "p1": 1, "streak": 0, "hits": 0}
              and gam.get("fallo") == {"faults": 1}
              and gam.get("ronda2") == {"sess": 44, "acc": 83, "stars": 3}
              and gam.get("puro") == {"sess": 4, "streak": 4}
              and gam.get("hubDraw", {}).get("rects", 0) > 10 and gam.get("hubDraw", {}).get("err") is None
              and tee.get("snap1", {}).get("phase") == "tee"
              and abs(tee.get("snap1", {}).get("z", 9) - tee.get("snap1", {}).get("teeEsperadoZ", 0)) < 0.05
              and tee.get("snap2", {}).get("phase") == "toss" and tee.get("snap2", {}).get("vy", 0) > 0.5)
        print("pageerrors   :", errors or "ninguno")
        print("RESULTADO    :", "OK" if ok else "REVISAR")

asyncio.run(main())
