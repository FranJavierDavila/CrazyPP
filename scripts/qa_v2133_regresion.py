#!/usr/bin/env python3
"""QA V2.133 · REGRESIÓN: los otros poderes del Clown intactos + smoke 4 campeonatos."""
import json, time
from playwright.sync_api import sync_playwright

pageerrors = []
fallos = []

def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {"__err": str(e)[:300]}

def boot(page, champ):
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(f"http://localhost:3000/game.html?champ={champ}",
              wait_until="domcontentloaded", timeout=60000)
    deadline = time.time() + 45
    while time.time() < deadline:
        if js(page, "!!(window.__PP_GAME&&window.__PP_GAME.champs&&window.__PP_GAME.champs.mod&&window.__PP_GAME.champs.mod.controller)") is True:
            time.sleep(2)
            return True
        time.sleep(1)
    return False

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("pageerror", lambda e: pageerrors.append(str(e)[:200]))

    # 1 · LOCURA: otros poderes intactos (globos/burla/confetti/redball)
    okb = boot(page, "locura")
    print("[boot-locura]", {"ok": okb}, flush=True)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      const out = {};
      const prep = () => { G.rules.startMatch('match');
        G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
        G.ball.pos.set(0, 1.2, -2.0); G.ball.vel.set(0, 0, 2.0);
        G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
        c.stage = 0; };
      // GLOBOS
      prep(); c.firePower('globos');
      for (let k = 0; k < 60; k++) { C.mod.update(0.05); if (c._powerKind) break; }
      const GL = c._globos ? (c._globos.items || []) : [];
      out.globos = { kind: c._powerKind,
        vivos: GL.filter(it => it && it.alive).length,
        grupoVisible: !!(c._globos && c._globos.grp && c._globos.grp.visible),
        powerT: +c._powerT.toFixed(1) };
      // BURLA
      prep(); c.firePower('burla');
      for (let k = 0; k < 60; k++) { C.mod.update(0.05); if (c._powerKind) break; }
      const BU = c._burla ? (c._burla.cartones || []) : [];
      out.burla = { kind: c._powerKind, powerT: +c._powerT.toFixed(1),
        cartones: BU.filter(x => x && (x.on || x.alive || (x.mesh && x.mesh.visible))).length,
        grupo: !!(c._burla && c._burla.grp && c._burla.grp.visible) };
      // REDBALL
      prep(); c.firePower('redball');
      for (let k = 0; k < 60; k++) { C.mod.update(0.05); if (c._powerKind) break; }
      out.redball = { kind: c._powerKind,
        roja: '#'+G.ballMesh.material.color.getHexString(),
        escala: +G.ballMesh.scale.x.toFixed(1) };
      // CONFETI
      prep(); c.firePower('confetti');
      for (let k = 0; k < 60; k++) { C.mod.update(0.05); if (c._powerKind) break; }
      out.confetti = { kind: c._powerKind, burst: +G.confettiBurst.toFixed(1) };
      c._endPower(); G.rules.startMatch('match'); G.freezeT = 0;
      return out; })()""")
    print("[poderes-otros]", json.dumps(d, ensure_ascii=False), flush=True)
    ok1 = (isinstance(d, dict) and d.get("globos", {}).get("kind") == "globos" and
           d.get("burla", {}).get("kind") == "burla" and
           d.get("redball", {}).get("kind") == "redball" and
           d.get("redball", {}).get("roja") == "#e02430" and
           d.get("redball", {}).get("escala", 0) >= 1.9 and
           d.get("confetti", {}).get("kind") == "confetti" and
           d.get("confetti", {}).get("burst", 0) >= 7)
    print("OK-otros-poderes:", ok1, flush=True)
    if not ok1: fallos.append("otros-poderes")
    # NATURAL: gatillo real del rally con azar forzado (bolsa gira y avisa)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      const oR = Math.random; Math.random = () => 0.0;
      let avisos = [];
      try {
        G.rules.startMatch('match');
        c._powerCd = 0; c._powerT = 0; c._endPower(); c.stage = 0;
        for (let k = 0; k < 400 && avisos.length < 4; k++) {
          G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
          G.rules.rallyHits = 3;
          G.ball.pos.set(0, 1.2, -2.0); G.ball.vel.set(0, 0, 2.6);
          C.mod.update(0.05);
          if (c._pendingPower) { avisos.push(c._pendingPower.kind);
            c._pendingPower = null; c._pendT = 0; c._rallyFired = false;
            G.rules.state = 'serve';    // cierra el rallye para el siguiente
            C.mod.update(0.05); }       // el módulo VE el saque (resetea _toward)
        }
      } finally { Math.random = oR; }
      G.rules.startMatch('match'); G.freezeT = 0;
      return { avisos }; })()""")
    print("[gatillo-natural]", json.dumps(d, ensure_ascii=False), flush=True)
    ok2 = isinstance(d, dict) and len(d.get("avisos", [])) >= 4
    if not ok2: fallos.append("gatillo-natural")

    # 2 · SMOKE de los otros campeonatos (boot + 0 errores)
    for champ in ["magia", "oeste", "estacion_orbital"]:
        pe0 = len(pageerrors)
        ok3 = boot(page, champ)
        time.sleep(2)
        print(f"[boot-{champ}]", {"ok": ok3, "pageerrors_nuevos": len(pageerrors) - pe0}, flush=True)
        if not ok3 or len(pageerrors) > pe0: fallos.append("smoke-" + champ)

    browser.close()

print("\n== RESUMEN ==")
print(json.dumps({"fallos": fallos, "pageerrors": pageerrors[:5]}, ensure_ascii=False, indent=1))
