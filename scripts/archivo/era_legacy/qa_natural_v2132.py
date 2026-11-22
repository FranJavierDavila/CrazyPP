#!/usr/bin/env python3
"""QA V2.132 · Estación Orbital — RUTA NATURAL de superpoderes (sin forzar).

Diferencia con el QA de V2.131 (que forzaba prob=1, cooldown=0, onMatchOver
directo y dianas alive=false): aquí el duelo se juega por la MISMA tubería
del núcleo que en el casco:
    rules.applyPoint(...) → processIntents → case 'point' → champs.onPoint
    → mod.onPoint → CTRL.onPoint → (state==='duelo') → _quizasPoder()
con Math.random REAL (sin tocarlo) y cooldowns reales.
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"
OUT = {"steps": []}
errors = []

def log(step, data):
    OUT["steps"].append({"step": step, **data})
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:400], flush=True)

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

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)[:200]))

    log("boot", boot(page))

    # 1 · Gatillo vía gating REAL del núcleo → DUELO 1
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs;
      if (G.rules.state !== 'champtest') return {__err:'rules '+G.rules.state};
      C.serveTrigger(0);
      const ctrl = C.mod.controller;
      return { st: ctrl.state, rules: G.rules.state, powerCd: ctrl._powerCd }; })()""")
    log("1-trigger-duelo", d)

    # 2 · DUELO NATURAL: 40 puntos por la tubería REAL del núcleo (prob real).
    #     Cada punto: processIntents(rules.applyPoint) EXACTAMENTE como el
    #     árbitro lo hace (líneas 11673-11674 del núcleo), y ticks de
    #     rules.update para que el estado 'point' respire.
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, ctrl = C.mod.controller;
      const seen = { warns: [], acts: [], onPointCalls: 0, puntos: 0, matchOver: null, st: null };
      // instrumentación pasiva: envolvemos CTRL.onPoint sin cambiar su lógica
      const realOnPoint = ctrl.onPoint.bind(ctrl);
      ctrl.onPoint = (it) => { seen.onPointCalls++; return realOnPoint(it); };
      // envolvemos _quizasPoder para registrar Tiradas (sin cambiar probabilidad)
      const realQ = ctrl._quizasPoder.bind(ctrl);
      let tiradas = 0;
      ctrl._quizasPoder = () => { tiradas++; return realQ(); };
      if (ctrl._warn) seen.warns.push('pre-warn:'+ctrl._warn.def.name);
      // 40 puntos reales (gana quien gane), con ticks del árbitro entre ellos
      for (let i = 0; i < 40 && seen.matchOver === null; i++) {
        const winner = (i % 3 === 0) ? 'player' : 'rival';   // mezcla realista
        const its = G.rules.applyPoint(winner, 'out');
        G.processIntents(its);
        seen.puntos++;
        if (ctrl._warn) seen.warns.push(ctrl._warn.def.name);
        if (ctrl._act) seen.acts.push(ctrl._act.def.name);
        // ticks del árbitro: 2.5 s en pasos de 50 ms (transición point→serve)
        for (let k = 0; k < 50; k++) G.processIntents(G.rules.update(0.05));
        if (G.rules.state === 'over' || ctrl.state !== 'duelo') { seen.matchOver = { st: ctrl.state, rules: G.rules.state }; }
      }
      ctrl.onPoint = realOnPoint; ctrl._quizasPoder = realQ;
      return { ...seen, tiradas, powerCd: +ctrl._powerCd.toFixed(1),
               warnNow: ctrl._warn && ctrl._warn.def.name, actNow: ctrl._act && ctrl._act.def.name,
               marcador: [G.rules.scorePlayer, G.rules.scoreAi] }; })()""")
    log("2-duelo-natural", d)

    # 3 · Si el duelo terminó por 'over' natural, el camino debe avanzar
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      return { st: ctrl.state, stage: ctrl.stage, rules: G.rules.state, msg: G.rules.message }; })()""")
    log("3-post-duelo", d)

    # 4 · POSICIÓN de la bola-HOLD de la prueba vs alcance del jugador
    d = js(page, """(() => { const G=window.__PP_GAME,ctrl=G.champs.mod.controller;
      const D = window.__PP_CORE.DIMS;
      const nearZ = D.tableCenterZ + D.tableHalfLength;
      // módulo HOLD si existe, si no leemos del módulo compilado
      let hold = null;
      try { hold = ctrl.prueba.HOLD || null; } catch(e){}
      return { holdModulo: hold, nearZ: +nearZ.toFixed(3),
               distHold: hold ? +Math.hypot(hold.x, hold.z).toFixed(3) : null,
               distNearEdge: hold ? +(nearZ - hold.z).toFixed(3) : null,
               jugadorEn: 'z=0 (origen, convención del núcleo)' }; })()""")
    log("4-hold-posicion", d)

    browser.close()

with open("/home/z/my-project/scripts/qa_natural_v2132_out.json", "w") as f:
    json.dump({"errors": errors[-25:], **OUT}, f, indent=1, ensure_ascii=False)
print("\nERRORES consola:", *errors[-8:], sep="\n  ") if errors else print("\nSin errores de consola")
