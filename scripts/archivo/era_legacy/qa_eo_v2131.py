#!/usr/bin/env python3
"""QA V2.131 · Estación Orbital: ¿por qué no hay superpoderes (etapas 1/3/5)
ni pruebas de habilidad (etapas 2/4)?

Carga game.html?champ=estacion_orbital en Chromium headless (modo 2D QA con
window.__pp2DPlay=true) y ejercita la máquina de estados del módulo:
  1. estado del CTRL tras el arranque (¿'sala'? ¿mapa? ¿cartel?)
  2. serveTrigger() en sala → ¿arranca el duelo 1? ¿rules.state?
  3. onPoint() xN → ¿_quizasPoder dispara (warn/act)? ¿poderes visibles?
  4. victoria del duelo → ¿stage avanza a 2?
  5. serveTrigger() en etapa 2 (prueba) → ¿ cartel instrucciones? ¿ callback
     _arrancarPrueba? ¿prueba.start? ¿rules.state='champtest'? ¿testActive?
"""
import json, sys, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"
OUT = {"steps": []}

def log(step, data):
    OUT["steps"].append({"step": step, **data})
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:400], flush=True)

def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {"__err": str(e)[:300]}

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errors = []
    page.on("console", lambda m: errors.append(m.text[:300]) if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)[:300]))

    # __pp2DPlay ANTES de que cargue el juego
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    # espera al núcleo + champ activo
    deadline = time.time() + 45
    state = None
    while time.time() < deadline:
        state = js(page, """(() => {
          const G = window.__PP_GAME; const C = G && (G.champs||G.loader);
          const m = C && C.mod; const ctrl = m && (m.controller||m._ctrl);
          return { hasGame: !!G, activeId: C && C.activeId,
                   ctrlState: ctrl && ctrl.state, stage: ctrl && ctrl.stage,
                   rulesState: G && G.rules && G.rules.state };
        })()""")
        if isinstance(state, dict) and state.get("ctrlState"):
            break
        time.sleep(1)
    log("boot", state)

    # ---- paso 1: detallar el CTRL en sala
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      return { state: ctrl.state, stage: ctrl.stage, etapas: ctrl.stage!==undefined && (ctrl.constructor+'').slice(0,40),
               cartelVisible: ctrl.cartel && ctrl.cartel.visible,
               mapa: !!ctrl.mapa, rival: !!ctrl.rivalMesh,
               etCfg: (typeof CTRL_ETAPAS !== 'undefined') ? null : undefined,
               powerCd: ctrl._powerCd, bolsa: ctrl._bolsa && ctrl._bolsa.length,
               rules: G.rules.state, msg: G.rules.message };
    })()""")
    log("sala", d)

    # ---- paso 2: serveTrigger en sala → debe arrancar DUELO 1
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      ctrl.serveTrigger(0);
      return new Promise(r => setTimeout(() => r({
        ctrlState: ctrl.state, rules: G.rules.state,
        rivalEstado: ctrl.rivalMesh && ctrl.rivalMesh.material.map.image ? 'tex' : 'none',
        cartelVisible: ctrl.cartel && ctrl.cartel.visible,
        instrOn: !!G._instr, msg: G.rules.message,
        powerCd: ctrl._powerCd, bolsa: ctrl._bolsa && ctrl._bolsa.length,
      }), 1200));
    })()""")
    log("duelo1-start", d)

    # ---- paso 3: simular puntos jugados → onPoint → ¿poderes?
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      // forzar: sin cooldown, bolsa llena, probabilidad 1
      ctrl._powerCd = 0; ctrl._bolsa.length = 0;
      const origRandom = Math.random;
      Math.random = () => 0.0;   // siempre < chance → warn garantizado
      let fired = null;
      try { ctrl.onPoint({ winner: 'rival' }); fired = !!ctrl._warn || !!ctrl._act; }
      finally { Math.random = origRandom; }
      return { fired, warn: ctrl._warn && ctrl._warn.def && ctrl._warn.def.name,
               act: ctrl._act && ctrl._act.def && ctrl._act.def.name,
               msg: G.rules.message, rules: G.rules.state };
    })()""")
    log("poder-warn", d)

    # avanzar el aviso 3 s y ver si el efecto arranca
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      if (ctrl._warn) { ctrl._warn.t = 0.01; ctrl.update(0.05); }
      return { act: ctrl._act && ctrl._act.def && ctrl._act.def.name,
               beam: ctrl.beam && ctrl.beam.visible,
               rocasOn: ctrl.rocas ? ctrl.rocas.filter(r=>r.on).length : -1,
               msg: G.rules.message };
    })()""")
    log("poder-act", d)

    # limpiar poder para el siguiente test
    js(page, """(() => { const G=window.__PP_GAME; const ctrl=G.champs.mod.controller; ctrl._poderClear(); })()""")

    # ---- paso 4: ganar el duelo 1 → ¿stage 1→ prueba?
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      const before = { state: ctrl.state, stage: ctrl.stage };
      ctrl.onMatchOver(true);
      return { before, after: { state: ctrl.state, stage: ctrl.stage,
                cartelVisible: ctrl.cartel && ctrl.cartel.visible,
                msg: G.rules.message, mapaRefresh: !!ctrl.mapa } };
    })()""")
    log("duelo1-win", d)

    # ---- paso 5: serveTrigger en etapa 2 (PRUEBA cinturon)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      ctrl.serveTrigger(0);
      return new Promise(r => setTimeout(() => r({
        ctrlState: ctrl.state, instrK: ctrl._instrK || null,
        instrOn: !!G._instr, instrWaitBtn: !!(G._instr && G._instr.waitBtn),
        rules: G.rules.state, testActive: m.testActive ? m.testActive() : null,
        pruebaRunning: ctrl.prueba && ctrl.prueba.running,
        pruebaBuilt: ctrl.prueba && ctrl.prueba.built,
        msg: G.rules.message,
      }), 1500));
    })()""")
    log("prueba2-instr", d)

    # en 2D no hay botón EMPEZAR (WAIT=false) → debe auto-cerrar en 7.5s.
    # aceleramos: cerramos a mano y comprobamos que _arrancarPrueba corre
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, m = C.mod, ctrl = m.controller;
      if (G._instr) G.hideInstrucciones(false);   // dispara callback
      return new Promise(r => setTimeout(() => r({
        ctrlState: ctrl.state, rules: G.rules.state,
        testActive: m.testActive ? m.testActive() : null,
        pruebaRunning: ctrl.prueba && ctrl.prueba.running,
        stepActive: ctrl.prueba && ctrl.prueba.stepActive && ctrl.prueba.stepActive(),
        dianas: ctrl.prueba && ctrl.prueba.dianas ? ctrl.prueba.dianas.filter(d=>d.on).length : null,
        err: ctrl.prueba && ctrl.prueba._lastErr || null,
        msg: G.rules.message,
      }), 1500));
    })()""")
    log("prueba2-run", d)

    # ---- paso 6: STEP disponible? (stepPhysics del núcleo)
    d = js(page, """(() => {
      const C = window.__PP_CORE;
      return { stepPhysics: typeof (C && C.stepPhysics),
               coreKeys: C ? Object.keys(C).slice(0,25) : null };
    })()""")
    log("core-hooks", d)

    browser.close()

with open("/home/z/my-project/scripts/qa_eo_v2131_out.json", "w") as f:
    json.dump({"errors": errors[-30:], **OUT}, f, indent=1, ensure_ascii=False)
print("CONSOLAS(err/warn) últimas:", *errors[-12:], sep="\n  ")
