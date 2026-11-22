#!/usr/bin/env python3
"""QA V2.131 · Estación Orbital — verificación del FIX RAÍZ (champtest en sala).

Simula el CAMINO REAL del gatillo del casco:
  onSelectStart → (instr/champIntro/calib/menu NO) → replayConsume? NO →
  rules.state==='champtest' → champs.serveTrigger(i)
Cubre: sala→duelo1, powers, win→etapa2, prueba completa (instrucciones EMPEZAR
en 2D = auto-fade), fin de prueba→sala, duelo2, derrota (repite), rejugada por
mapa, leave (restauración del árbitro).
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"
OUT = {"steps": []}
errors = []

def log(step, data):
    OUT["steps"].append({"step": step, **data})
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:360], flush=True)

def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {"__err": str(e)[:300]}

def boot(page):
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    deadline = time.time() + 45
    while time.time() < deadline:
        s = js(page, """(() => { const G=window.__PP_GAME,C=G&&(G.champs||G.loader);
          const ctrl=C&&C.mod&&C.mod.controller;
          return { ok: !!ctrl, rules: G&&G.rules&&G.rules.state, st: ctrl&&ctrl.state }; })()""")
        if isinstance(s, dict) and s.get("ok"):
            return s
        time.sleep(1)
    return {"ok": False}

def trigger_via_core(page):
    """La MISMA ruta del casco: sólo si rules.state==='champtest' llega al módulo."""
    return js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      const before = { rules: G.rules.state, st: ctrl.state, stage: ctrl.stage };
      // — réplica literal del gating de onSelectStart (línea ~10402-10419) —
      const stR = G.rules.state;
      let reached = false;
      if (stR === 'champtest') { C.serveTrigger(0); reached = true; }
      return { before, reached,
        after: { rules: G.rules.state, st: ctrl.state, stage: ctrl.stage,
                 cartel: ctrl.cartel && ctrl.cartel.visible, msg: G.rules.message } };
    })()""")

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)[:200]))

    log("boot", boot(page))

    # 1 · SALA: el gatillo vía núcleo debe arrancar DUELO 1
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      return { rules: G.rules.state, st: ctrl.state, stage: ctrl.stage,
               ballPos: [G.ball.pos.x, G.ball.pos.y, G.ball.pos.z].map(v=>+v.toFixed(2)),
               cartel: ctrl.cartel.visible, mapa: !!ctrl.mapa }; })()""")
    log("1-sala", d)

    d = trigger_via_core(page)
    log("2-trigger→duelo1", d)

    # 2 · POWERS en duelo (forzamos prob 1 y cooldown 0: como un punto real)
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      ctrl._powerCd = 0; ctrl._bolsa.length = 0;
      const o = Math.random; Math.random = () => 0.0;
      let out = {};
      try { ctrl.onPoint({winner:'rival'}); out.warn = ctrl._warn && ctrl._warn.def.name;
            if (ctrl._warn) { ctrl._warn.t = 0.01; ctrl.update(0.05); }
            out.act = ctrl._act && ctrl._act.def.name; out.msg = G.rules.message; }
      finally { Math.random = o; }
      ctrl._poderClear();
      return out; })()""")
    log("3-powers-duelo", d)

    # 3 · GANAR duelo1 → etapa 2 (prueba) + sala con árbitro dormido
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      ctrl.onMatchOver(true);
      return { st: ctrl.state, stage: ctrl.stage, rules: G.rules.state,
               cartel: ctrl.cartel.visible, msg: G.rules.message }; })()""")
    log("4-duelo1-win", d)

    # 4 · Gatillo vía núcleo en etapa 2 → PRUEBA (panel instrucciones)
    d = trigger_via_core(page)
    log("5-trigger→prueba-instr", d)

    # 5 · En 2D el panel se auto-cierra (7.5 s): aceleramos cerrándolo —
    #     el callback debe arrancar la prueba (champtest + testActive)
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,m=C.mod,ctrl=m.controller;
      if (G._instr) G.hideInstrucciones(false);      // callback → _arrancarPrueba
      return new Promise(r => setTimeout(() => r({
        st: ctrl.state, rules: G.rules.state,
        testActive: m.testActive(), running: ctrl.prueba.running,
        ignoreNet: G.ball.ignoreNet, msg: G.rules.message }), 1200)); })()""")
    log("6-prueba-run", d)

    # 6 · Destruir todas las dianas → banner → sala con árbitro dormido, etapa 3
    d = js(page, """(() => { const G=window.__PP_GAME,m=G.champs.mod,ctrl=m.controller;
      const pr = ctrl.prueba;
      for (const it of pr.targets) if (it.alive) { it.alive = false; pr.alive--; }
      pr._fin(true);
      return new Promise(r => setTimeout(() => {
        if (pr.result) { pr.bannerT = 0.01; pr.step(0.02); }
        setTimeout(() => r({ st: ctrl.state, stage: ctrl.stage, rules: G.rules.state,
          testActive: m.testActive(), cartel: ctrl.cartel.visible,
          ignoreNet: G.ball.ignoreNet, msg: G.rules.message }), 300);
      }, 200)); })()""")
    log("7-prueba-fin", d)

    # 7 · DUELO 2 arranca por gatillo; DERROTA → etapa se repite (flujo amable)
    d = trigger_via_core(page)
    log("8-trigger→duelo2", d)
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      ctrl.onMatchOver(false);
      return { st: ctrl.state, stage: ctrl.stage, rules: G.rules.state, msg: G.rules.message }; })()""")
    log("9-duelo2-lose", d)

    # 8 · REJUGADA por mapa: lanzar etapa 1 (índice 0) con progreso en 2
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      ctrl.replayLaunch(0);
      const inReplay = !!ctrl._replay;
      ctrl.serveTrigger(0);   // arranque de la etapa rejugada (duelo 1)
      return { inReplay, st: ctrl.state, stage: ctrl.stage, rules: G.rules.state,
               msg: G.rules.message }; })()""")
    log("10-rejugada-duelo", d)
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      ctrl.onMatchOver(true);
      return { replayCleared: ctrl._replay === null, st: ctrl.state, stage: ctrl.stage,
               rules: G.rules.state, cartel: ctrl.cartel.visible }; })()""")
    log("11-rejugada-fin", d)

    # 9 · LEAVE: el árbitro debe quedar restaurado (no 'champtest')
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,m=C.mod;
      C.leaveAll();
      return { rulesAfterLeave: G.rules.state, activeId: C.activeId }; })()""")
    log("12-leave-árbitro", d)

    browser.close()

with open("/home/z/my-project/scripts/qa_eo_fix_out.json", "w") as f:
    json.dump({"errors": errors[-25:], **OUT}, f, indent=1, ensure_ascii=False)
print("\nERRORES consola:", *errors[-8:], sep="\n  ") if errors else print("\nSin errores de consola")
