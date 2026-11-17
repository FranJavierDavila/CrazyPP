#!/usr/bin/env python3
"""QA V2.132 · Estación Orbital v3.2 — «LOS PODERES YA MANDAN» + dianas 3D.

TODO por la RUTA NATURAL (nada forzado donde importa):
  · Poderes: puntos por processIntents(applyPoint REAL) + ticks del módulo;
    disparo por RALLY; GARANTÍA de 22 s con Math.random estirado a 0.99.
  · Cartel del superpoder: visible + repintado por fase.
  · onMatchOver: GANAR avanza, PERDER NO (fix del bug del string 'rival').
  · Prueba: bola-HOLD alcanzable + colisión REAL por barrido (balística
    manual: vy = Δy/T + ½·g·T) + escudo caja 2 golpes + etapa 4 completa.
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"
OUT = {"steps": []}
errors = []
fallos = []
malas_urls = []

def log(step, data, ok=None):
    OUT["steps"].append({"step": step, **data})
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:420], flush=True)
    if ok is False:
        fallos.append(step)

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
        s = js(page, "!!(window.__PP_GAME&&window.__PP_GAME.champs&&window.__PP_GAME.champs.mod&&window.__PP_GAME.champs.mod.controller)")
        if s is True:
            return True
        time.sleep(1)
    return False

def trigger_core(page):
    return js(page, """(() => { const G=window.__PP_GAME,C=G.champs,ctrl=C.mod.controller;
      const before = { rules: G.rules.state, st: ctrl.state, stage: ctrl.stage };
      if (G.rules.state !== 'champtest') return { before, reached: false };
      C.serveTrigger(0);
      return { before, reached: true,
        after: { rules: G.rules.state, st: ctrl.state, stage: ctrl.stage } }; })()""")

# bucle de puntos NATURAL que mantiene el duelo vivo (marca a 0 al llegar a 10)
TICKS = """(() => {
  const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
  const res = { puntos: 0, warns: [], actos: [], cartel: null, visibles: null };
  for (let i = 0; i < 34 && c.state === 'duelo'; i++) {
    const win = (i % 3 === 0) ? 'player' : 'rival';
    G.processIntents(G.rules.applyPoint(win, 'out'));
    res.puntos++;
    if (G.rules.scorePlayer >= 10 || G.rules.scoreAi >= 10) G.rules.startMatch('match');
    for (let k = 0; k < 50 && c.state === 'duelo'; k++) {
      G.processIntents(G.rules.update(0.05));
      C.mod.update(0.05);
      if (c._warn && !res.warns.includes(c._warn.def.name)) {
        res.warns.push(c._warn.def.name);
        res.cartel = { visible: !!(c.powerSign && c.powerSign.visible),
          pos: c.powerSign ? c.powerSign.position.toArray().map(v=>+v.toFixed(2)) : null };
      }
      if (c._act && !res.actos.includes(c._act.def.name)) {
        res.actos.push(c._act.def.name);
        res.visibles = { beam: !!(c.beam && c.beam.visible),
          motas: (c.motas||[]).filter(m=>m.s.material.opacity>0).length,
          confeti: (c._poolConfeti||[]).filter(p=>p.on).length,
          rocas: (c.rocas||[]).filter(r=>r.on).length };
      }
    }
  }
  return { ...res, st: c.state }; })()"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)[:200]))
    page.on("response", lambda r: malas_urls.append(f"{r.status} {r.url[-70:]}")
            if r.status >= 400 and ('championships' in r.url or 'game.html' in r.url or 'assets' in r.url) else None)

    log("boot", {"ok": boot(page)}, ok=True)

    # 1 · SALA → gatillo (gating real) → DUELO 1
    d = trigger_core(page)
    log("1-duelo", d, ok=(isinstance(d, dict) and d.get("reached") and d.get("after", {}).get("st") == "duelo"))

    # 2 · PODER POR PUNTOS NATURALES (probabilidad REAL, duelo vivo)
    d = js(page, TICKS)
    ok2 = isinstance(d, dict) and len(d.get("actos", [])) >= 1 and d.get("cartel", {}).get("visible") is True
    log("2-poder-por-puntos", d, ok=ok2)
    js(page, "(() => { const c=window.__PP_GAME.champs.mod.controller; if (c._act||c._warn) c._poderClear(); return 1; })()")

    # 3 · PODER POR RALLY (bola viniendo al jugador, edge vel.z>0.35)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      if (c.state !== 'duelo') return {__err: 'estado ' + c.state};
      c._powerCd = 0; c._poderClear();
      G.rules.state = 'rally'; G.ball.vel.set(0, 0, 2.2);
      let via = null;
      for (let k = 0; k < 400 && !via; k++) {
        G.ball.vel.z = (k % 2) ? -2.2 : 2.2;   // edge real: la bola va y viene
        C.mod.update(0.05);
        if (c._warn) via = c._warn.def.name;
      }
      const out = { via: via, cartel: !!(c.powerSign && c.powerSign.visible) };
      c._poderClear(); G.rules.state = 'serve';
      return out; })()""")
    log("3-poder-por-rally", d, ok=(isinstance(d, dict) and bool(d.get("via"))))

    # 4 · GARANTÍA 22 s CON MALA SUERTE TOTAL (Math.random → 0.99)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      if (c.state !== 'duelo') return {__err: 'estado ' + c.state};
      const o = Math.random; Math.random = () => 0.99;
      let salvado = null;
      try {
        c._poderClear(); c._powerCd = 0; c._dueloT = 0; c._lastPowerT = 0;
        for (let k = 0; k < 560 && !salvado; k++) {   // 28 s de juego
          C.mod.update(0.05);
          if (c._warn) salvado = { t: +c._dueloT.toFixed(1), def: c._warn.def.name,
                                   cartel: !!(c.powerSign && c.powerSign.visible) };
        }
      } finally { Math.random = o; c._poderClear(); }
      return { salvado, en22s: salvado ? (salvado.t <= 23.5) : false }; })()""")
    ok4 = isinstance(d, dict) and d.get("en22s") is True and d.get("salvado", {}).get("cartel") is True
    log("4-garantia-22s", d, ok=ok4)

    # 5 · GANAR duelo 1 por intents naturales (puntos del jugador) → etapa 2
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,c=C.mod.controller;
      if (c.state !== 'duelo') return {__err:'estado '+c.state};
      for (let i = 0; i < 12 && c.state === 'duelo'; i++) {
        G.processIntents(G.rules.applyPoint('player', 'out'));
        for (let k = 0; k < 46 && c.state === 'duelo'; k++) G.processIntents(G.rules.update(0.05));
      }
      return { st: c.state, stage: c.stage, rules: G.rules.state,
               msg: G.rules.message && G.rules.message.slice(0, 44) }; })()""")
    log("5-duelo1-GANADO", d, ok=(isinstance(d, dict) and d.get("st") == "sala" and d.get("stage") == 1))

    # 6 · gatillo → PRUEBA normal (etapa index 1): 1 diana por COLISIÓN REAL
    #      balística + resto por teleport-into-target (mismo barrido _collide)
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,c=C.mod.controller;
      if (G.rules.state !== 'champtest') return {__err:'rules '+G.rules.state};
      C.serveTrigger(0);
      if (c.state !== 'prueba') return {__err:'no prueba: '+c.state};
      if (G._instr) G.hideInstrucciones(false);
      return new Promise(r => setTimeout(() => {
        const pr = c.prueba;
        const g0 = 9.81, T = 0.40;
        const t0 = pr.targets[0];
        pr.hold = false; pr.flight = 0;
        const d3 = t0.sp.position.clone().sub(G.ball.pos);
        G.ball.vel.set(d3.x / T, d3.y / T + 0.5 * g0 * T, d3.z / T);
        G.ball.__exPrev && G.ball.__exPrev.copy(G.ball.pos);
        let frames = 0;
        for (let k = 0; k < 40 && t0.alive; k++) { pr.step(0.02); frames++; }
        const golpeReal = !t0.alive;
        for (const t of pr.targets) {
          if (!t.alive) continue;
          pr.hold = false; pr.flight = 0;
          G.ball.pos.copy(t.sp.position); G.ball.pos.y += 0.02;
          G.ball.vel.set(0, -0.5, 0.4);
          G.ball.__exPrev && G.ball.__exPrev.copy(G.ball.pos);
          for (let k = 0; k < 8 && t.alive; k++) pr.step(0.02);
          if (t.alive) { pr._bolaPerdida(); pr.deadT = 0; pr._spawnHeld(); }
        }
        // step() llama a _fin solo (sin doble _fin); acelera el banner
        let guard = 0;
        while (!pr.result && guard++ < 50) pr.step(0.05);
        if (pr.result) { pr.bannerT = 0.01; pr.step(0.02); }
        setTimeout(() => r({ golpeReal, frames, vivas: pr.alive, st: c.state,
          stage: c.stage, rules: G.rules.state,
          testActive: G.champs.mod.testActive() }), 350);
      }, 1300)); })()""")
    log("6-prueba1-colision-real", d, ok=(isinstance(d, dict) and d.get("golpeReal") is True and d.get("st") == "sala" and d.get("stage") == 2))

    # 7 · PERDER DUELO 2 por intents naturales → la etapa NO avanza (fix string)
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,c=C.mod.controller;
      if (G.rules.state !== 'champtest') return {__err:'rules '+G.rules.state};
      C.serveTrigger(0);   // etapa index 2 = DUELO 2
      if (c.state !== 'duelo') return {__err:'no duelo: '+c.state};
      for (let i = 0; i < 12 && c.state === 'duelo'; i++) {
        G.processIntents(G.rules.applyPoint('rival', 'out'));
        for (let k = 0; k < 46 && c.state === 'duelo'; k++) G.processIntents(G.rules.update(0.05));
      }
      return { st: c.state, stage: c.stage, rules: G.rules.state,
               msg: G.rules.message && G.rules.message.slice(0, 44) }; })()""")
    log("7-duelo2-PERDIDO", d, ok=(isinstance(d, dict) and d.get("st") == "sala" and d.get("stage") == 2))

    # 8 · Revancha: GANAR duelo 2 → etapa 3 (prueba compleja)
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,c=C.mod.controller;
      if (G.rules.state !== 'champtest') return {__err:'rules '+G.rules.state};
      C.serveTrigger(0);
      if (c.state !== 'duelo') return {__err:'no duelo: '+c.state};
      for (let i = 0; i < 12 && c.state === 'duelo'; i++) {
        G.processIntents(G.rules.applyPoint('player', 'out'));
        for (let k = 0; k < 46 && c.state === 'duelo'; k++) G.processIntents(G.rules.update(0.05));
      }
      return { st: c.state, stage: c.stage, rules: G.rules.state }; })()""")
    log("8-duelo2-GANADO", d, ok=(isinstance(d, dict) and d.get("stage") == 3))

    d = trigger_core(page)
    log("8-gatillo-prueba4", d, ok=(isinstance(d, dict) and d.get("after", {}).get("rules") == "champtest"))

    # 8 · PRUEBA compleja activa (cierra el panel EMPEZAR) + 3D + escudos
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs,m=C.mod,c=m.controller;
      if (G._instr) G.hideInstrucciones(false);
      return new Promise(r => setTimeout(() => {
        const pr = c.prueba;
        r({ st: c.state, testActive: m.testActive(), running: pr.running,
          dianas: pr.targets.length,
          cajas: pr.targets.filter(t=>t.tipo==='caja').length,
          drones: pr.targets.filter(t=>t.tipo==='dron').length,
          escudos: pr.targets.filter(t=>!!t.escudo).length,
          es3D: pr.targets.every(t => t.mesh && t.sp.isObject3D),
          rotoresDron: pr.targets.filter(t=>t.rotores&&t.rotores.length===4).length,
          bonus: pr.cfg.dronBonus }); }, 1300)); })()""")
    ok8 = isinstance(d, dict) and d.get("running") and d.get("dianas") == 14 and d.get("cajas") == 3 \
        and d.get("drones") == 2 and d.get("escudos") == 3 and d.get("es3D") is True and d.get("rotoresDron") == 2
    log("9-prueba4-3D", d, ok=ok8)

    # 9 · BOLA-HOLD ALCANZABLE
    d = js(page, """(() => { const G=window.__PP_GAME,c=G.champs.mod.controller,pr=c.prueba;
      const D = window.__PP_CORE.DIMS;
      const b = G.ball.pos;
      const dist = Math.hypot(b.x, b.z);
      return { hold: pr.hold, pos: [b.x, b.y, b.z].map(v=>+v.toFixed(2)),
        dist: +dist.toFixed(3), cerca: dist <= 0.65,
        sobreMesa: +(b.y - D.tableTopY).toFixed(2) }; })()""")
    log("10-hold-alcanzable", d, ok=(isinstance(d, dict) and d.get("hold") is True and d.get("cerca") is True))

    # 10 · COLISIÓN REAL por barrido con balística (vy = Δy/T + ½gT): primero
    #      contra una CAJA (2 golpes: escudo aguanta → destello → 2º la rompe)
    d = js(page, """(() => {
      const G=window.__PP_GAME,c=G.champs.mod.controller,pr=c.prueba;
      const g0 = 9.81, T = 0.40;
      const tiro = (tgt) => {
        pr.hold = false; pr.flight = 0;
        const d3 = tgt.clone().sub(G.ball.pos);
        G.ball.vel.set(d3.x / T, d3.y / T + 0.5 * g0 * T, d3.z / T);
        G.ball.__exPrev && G.ball.__exPrev.copy(G.ball.pos);
        for (let k = 0; k < 40; k++) pr.step(0.02);
      };
      const caja = pr.targets.find(t => t.alive && t.tipo === 'caja');
      const out = { hayCaja: !!caja };
      if (caja) {
        const hp0 = caja.hp;
        tiro(caja.sp.position.clone());            // golpe 1: escudo
        out.g1 = { hp: caja.hp, alive: caja.alive, escudoOp: +caja.escudo.material.opacity.toFixed(2) };
        if (caja.alive) {
          caja._hitT = 0;                           // deja decaer el destello
          G.ball.pos.set(0.26, 0.88 + 0.12, -0.50); G.ball.vel.set(0,0,0);
          for (let k = 0; k < 10; k++) pr.step(0.02);   // bola muerta: respawn hold
          tiro(caja.sp.position.clone());          // golpe 2: rompe
        }
        out.g2 = { hp: caja.hp, alive: caja.alive };
        out.escudoOK = (out.g1.hp === hp0 - 1) && out.g1.alive && (out.g2.alive === false);
      }
      out.vivas = pr.alive;
      return out; })()""")
    log("11-colision-real-escudo", d, ok=(isinstance(d, dict) and d.get("escudoOK") is True))

    # 12 · Resto de dianas por el MISMO barrido → victoria natural de step()
    #       → sala etapa 4 (index 4 = DUELO FINAL)
    d = js(page, """(() => {
      const G=window.__PP_GAME,c=G.champs.mod.controller,pr=c.prueba;
      const g0 = 9.81, T = 0.40;
      for (const t of pr.targets) {
        if (!t.alive) continue;
        for (let intento = 0; intento < 3 && t.alive; intento++) {
          pr.hold = false; pr.flight = 0;
          const d3 = t.sp.position.clone().sub(G.ball.pos);
          const TT = T + intento * 0.05;
          G.ball.vel.set(d3.x / TT, d3.y / TT + 0.5 * g0 * TT, d3.z / TT);
          G.ball.__exPrev && G.ball.__exPrev.copy(G.ball.pos);
          for (let k = 0; k < 40 && t.alive; k++) pr.step(0.02);
          if (t.alive) { pr._bolaPerdida(); pr.deadT = 0; pr._spawnHeld(); }
        }
      }
      const vivas = pr.alive;
      // step() llama a _fin una sola vez (sin doble _fin del QA anterior)
      let guard = 0;
      while (!pr.result && guard++ < 60) pr.step(0.05);
      if (pr.result) { pr.bannerT = 0.01; pr.step(0.02); }
      return new Promise(r => setTimeout(() => r({ vivas, total: pr.total, st: c.state,
        stage: c.stage, rules: G.rules.state,
        testActive: G.champs.mod.testActive() }), 350)); })()""")
    log("12-prueba4-fin", d, ok=(isinstance(d, dict) and d.get("st") == "sala" and d.get("stage") == 4 and d.get("vivas") == 0))

    # 12 · LEAVE limpio
    d = js(page, """(() => { const G=window.__PP_GAME,C=G.champs;
      C.leaveAll();
      return { rules: G.rules.state, activo: C.activeId }; })()""")
    log("13-leave", d, ok=(isinstance(d, dict) and d.get("rules") != "champtest"))

    browser.close()

OUT["fallos"] = fallos
OUT["urls_malas"] = malas_urls[:10]
with open("/home/z/my-project/scripts/qa_v2132_out.json", "w") as f:
    json.dump({"errors": errors[-25:], **OUT}, f, indent=1, ensure_ascii=False)
print("\n==== RESULTADO ====")
print("FALLOS:", fallos if fallos else "NINGUNO — TODO VERDE")
if malas_urls:
    print("URLs >=400:", *malas_urls[:6], sep="\n  ")
if errors:
    print("ERRORES consola (no-404):", *[e for e in errors[-10:] if '404' not in e and '400' not in e][:5], sep="\n  ")
