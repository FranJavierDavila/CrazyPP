#!/usr/bin/env python3
"""QA · CLOWN «BOLA DOBLE» (split) — repro por ruta natural + caminos límite.

Marco de ticks FIEL al núcleo (game.html 11311/11586/11672/11763):
  frozen → decrementa freezeT; splitFilterEvents+updateSplit ANTES del árbitro;
  módulo update SIEMPRE (incluso congelado).

Pasos:
  1. boot (?champ=locura) + inventario (bolsa por nivel)
  2. Nv.1 (stage 0): firePower('split') NO puede elegir split (no está)
  3. Nv.3 (stage 4): rally vivo -> firePower('split') -> cartel + aviso
  4. tick hasta el lanzamiento: clon vivo, malla visible, física corre
  5. salvación splitFilterEvents (bola oficial muere, lastHitter='ai')
  6. CAMINO LÍMITE: punto muerto durante el aviso (state='serve' al lanzar)
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=locura"
OUT = {"steps": []}
fallos = []
pageerrors = []

def log(step, data, ok=None):
    OUT["steps"].append({"step": step, **data})
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:500], flush=True)
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
            time.sleep(2)
            return True
        time.sleep(1)
    return False

# TICK GLOBAL: replica el orden del frame del núcleo para el split
TICK_JS = """
window.__tick = (n) => {
  const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
  for (let i = 0; i < n; i++) {
    const frozen = G.freezeT > 0;
    if (frozen) G.freezeT = Math.max(0, G.freezeT - 0.05);
    if (!frozen) {                                   // núcleo 11586-11591
      if (C._split) { C.splitFilterEvents(G.events); C.updateSplit(0.05); }
      if (G.rules.state !== 'over') {
        G.processIntents(G.rules.handleEvents(G.events));
        G.processIntents(G.rules.update(0.05));
      }
    }
    C.mod.update(0.05);                              // núcleo 11763 (siempre)
  }
  return { frozen: G.freezeT > 0, rules: G.rules.state,
    split: !!C._split, kind: c._powerKind, powerT: +c._powerT.toFixed(2),
    cartel: !!(c.powerSign && c.powerSign.visible) };
};
1"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("pageerror", lambda e: pageerrors.append(str(e)[:200]))

    log("boot", {"ok": boot(page)}, ok=True)
    js(page, TICK_JS)

    # 1 · INVENTARIO (bolsa por nivel)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      const s0 = c.stage;
      c.stage = 0; const bolsa0 = c._powerList().map(p => p.kind);
      c.stage = 2; const bolsa2 = c._powerList().map(p => p.kind);
      c.stage = 4; const bolsa4 = c._powerList().map(p => p.kind);
      c.stage = s0;
      return { active: c.active, stage: s0, nv: c.clownLevel(),
        rules: G.rules.state, opp: G.rules.oppLabel,
        bolsaNv1: bolsa0, bolsaNv2: bolsa2, bolsaNv3: bolsa4 }; })()""")
    log("1-inventario", d, ok=(isinstance(d, dict) and d.get("active") is True))

    # 2 · Nv.1: firePower('split') NO puede lanzar split (no está en la bolsa)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      G.rules.startMatch('match');
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.2, -2.0); G.ball.vel.set(0, 0, 2.0);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.stage = 0;
      c.firePower('split');
      return { elegido: c._pendingPower ? c._pendingPower.kind : null }; })()""")
    ok2 = (isinstance(d, dict) and d.get("elegido") != "split")
    log("2-nv1-sin-split", d, ok=ok2)
    js(page, "window.__PP_GAME.champs.mod.controller._endPower(); window.__PP_GAME.freezeT=0; 1")

    # 3 · Nv.3: rally vivo + firePower('split') -> cartel + aviso
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      G.rules.startMatch('match');
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.2, -2.0); G.ball.vel.set(0, 0, 2.0);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.stage = 4;
      c.firePower('split');
      window.__tick(2);
      return { pend: c._pendingPower ? c._pendingPower.kind : null,
        cartel: !!(c.powerSign && c.powerSign.visible),
        freeze: +G.freezeT.toFixed(2), pendT: +c._pendT.toFixed(2),
        msg: G.rules.message }; })()""")
    ok3 = (isinstance(d, dict) and d.get("pend") == "split" and d.get("cartel") is True)
    log("3-firePower-split", d, ok=ok3)

    # 4 · LANZAMIENTO: tick hasta _powerKind='split' + clon vivo con malla
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      let lanzado = -1;
      for (let k = 0; k < 70; k++) {
        window.__tick(1);
        if (lanzado < 0 && c._powerKind === 'split') lanzado = k;
        if (lanzado >= 0 && k >= lanzado + 6) break;   // 0.3 s de vuelo del clon
      }
      const cl = c._split;
      const mesh = c.arkanoid && c.arkanoid.cloneMesh;
      const nan = cl ? (!isFinite(cl.ball.pos.x) || !isFinite(cl.ball.vel.z)) : null;
      return { lanzadoEnTick: lanzado, powerKind: c._powerKind,
        powerT: +c._powerT.toFixed(2), splitVivo: !!cl,
        clonPos: cl ? cl.ball.pos.toArray().map(v=>+v.toFixed(2)) : null,
        clonVel: cl ? cl.ball.vel.toArray().map(v=>+v.toFixed(2)) : null,
        meshVisible: mesh ? mesh.visible : null,
        meshPos: mesh ? mesh.position.toArray().map(v=>+v.toFixed(2)) : null,
        nan, bolaBlanca: G.ballMesh && G.ballMesh.material ?
          '#'+G.ballMesh.material.color.getHexString() : null }; })()""")
    ok4 = (isinstance(d, dict) and d.get("lanzadoEnTick", -1) >= 0 and
           d.get("splitVivo") is True and d.get("meshVisible") is True and d.get("nan") is False)
    log("4-lanzamiento-clon", d, ok=ok4)

    # 5 · SALVACIÓN: la bola oficial muere (floor) con lastHitter='ai'
    #     (relanzamos el split con bola alta para que el clon siga vivo)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      if (c._split) c._endSplit();
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.6, -2.0); G.ball.vel.set(0, 0, 1.4);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.firePower('split');
      window.__tick(50);                       // aviso completo (2.1 s)
      if (!c._split) return { __err: 'clon no llegó a nacer (estado cambió)',
        rules: G.rules.state };
      const clon = c._split.ball;
      const antes = { bola: G.ball.pos.toArray().map(v=>+v.toFixed(2)),
        clon: clon.pos.toArray().map(v=>+v.toFixed(2)) };
      G.rules.lastHitter = 'ai';
      G.events.push({ type: 'floor', pos: G.ball.pos.clone(), speed: 2 });
      window.__tick(1);
      return { antes, salvado: !c._split,
        floorRestantes: G.events.filter(e => e.type === 'floor').length,
        msg: G.rules.message,
        bolaTomóClon: G.ball.pos.distanceTo(clon.pos) < 0.05 }; })()""")
    ok5 = (isinstance(d, dict) and d.get("salvado") is True and
           d.get("bolaTomóClon") is True)
    log("5-salvacion", d, ok=ok5)

    # 6 · CAMINO LÍMITE: punto muerto durante el aviso (state='serve' al lanzar)
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      G.rules.startMatch('match');
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.6, -2.0); G.ball.vel.set(0, 0, 1.4);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.firePower('split');
      G.rules.state = 'serve';                 // el punto muere DURANTE el aviso
      let lanzo = false;
      for (let k = 0; k < 60; k++) {
        window.__tick(1);
        if (c._powerKind === 'split') { lanzo = true; }
        if (lanzo && k > 0 && !c._split) break;  // el clon murió ya
      }
      const mesh = c.arkanoid && c.arkanoid.cloneMesh;
      return { lanzo, splitTrasLaunch: !!c._split,
        meshVisible: mesh ? mesh.visible : null,
        powerT: +c._powerT.toFixed(2),
        rules: G.rules.state }; })()""")
    log("6-punto-muerto", d)
    js(page, """(() => { const G=window.__PP_GAME,c=G.champs.mod.controller;
      c._endPower(); c._powerCd=0; if (c.powerSign) c.powerSign.hide();
      G.rules.startMatch('match'); G.freezeT=0; return 1; })()""")

    browser.close()

print("\n== RESUMEN ==")
print(json.dumps({"fallos": fallos, "pageerrors": pageerrors},
                 ensure_ascii=False, indent=1))
