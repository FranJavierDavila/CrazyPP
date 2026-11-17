#!/usr/bin/env python3
"""QA V2.133 · CLOWN «BOLA DOBLE» — el split SE VE (ruta natural).

Marcas del fix (módulo locura v19 / manifest v19 / núcleo 2.133.0):
  A. cloneMesh existe SIN build del arkanoid (constructor)  → era el bug
  B. firePower('split') en Nv.3 → cartel (group.visible/t) + aviso
  C. lanzamiento → clon vivo, MALLA VISIBLE siguiendo la física, bola blanca
  D. salvación splitFilterEvents (floor con lastHitter='ai' → swap)
  E. punto muerto durante el aviso → RE-ARMA (no lanza) y entra en el
     próximo rallye (antes: clon nacía y moría en el 1.er frame)
  F. bolsa por nivel: split SOLO en Nv.3 (diseño)
Marco de ticks FIEL al núcleo (11311/11586/11672/11763).
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=locura"
fallos = []
pageerrors = []

def log(step, data, ok=None):
    print(f"[{step}] " + json.dumps(data, ensure_ascii=False)[:520], flush=True)
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

TICK_JS = """
window.__tick = (n) => {
  const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
  for (let i = 0; i < n; i++) {
    const frozen = G.freezeT > 0;
    if (frozen) G.freezeT = Math.max(0, G.freezeT - 0.05);
    if (!frozen) {
      if (C._split) { C.splitFilterEvents(G.events); C.updateSplit(0.05); }
      if (G.rules.state !== 'over') {
        G.processIntents(G.rules.handleEvents(G.events));
        G.processIntents(G.rules.update(0.05));
      }
    }
    C.mod.update(0.05);
  }
  return { rules: G.rules.state, split: !!C._split, kind: c._powerKind };
};
window.__cartel = () => { const c = window.__PP_GAME.champs.mod.controller;
  const ps = c.powerSign;
  return ps ? { grupo: !!(ps.group && ps.group.visible), t: ps.t } : null; };
1"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("pageerror", lambda e: pageerrors.append(str(e)[:200]))

    okb = boot(page)
    log("boot", {"ok": okb, "version": js(page, "window.__PP_GAME.version || 'n/a'")}, ok=okb)
    js(page, TICK_JS)

    # A · LA MARCA DEL BUG: cloneMesh existe SIN haber construido el arkanoid
    d = js(page, """(() => {
      const c = window.__PP_GAME.champs.mod.controller;
      const ark = c.arkanoid;
      return { arkanoidInited: ark.inited,                 // false = nunca build()
        cloneMeshExiste: !!ark.cloneMesh,                  // EL FIX
        visibleAhora: ark.cloneMesh ? ark.cloneMesh.visible : null,
        enRig: ark.cloneMesh ? !!ark.cloneMesh.parent : null,
        makeCloneDisponible: typeof ark._makeCloneMesh === 'function' }; })()""")
    log("A-clon-en-constructor", d,
        ok=(d.get("arkanoidInited") is False and d.get("cloneMeshExiste") is True
            and d.get("visibleAhora") is False and d.get("enRig") is True))

    # F · BOLSA POR NIVEL
    d = js(page, """(() => {
      const c = window.__PP_GAME.champs.mod.controller;
      const s0 = c.stage;
      c.stage = 0; const b1 = c._powerList().map(p => p.kind);
      c.stage = 4; const b3 = c._powerList().map(p => p.kind);
      c.stage = s0;
      return { bolsaNv1: b1, bolsaNv3: b3,
        splitSoloEnNv3: !b1.includes('split') && b3.includes('split') }; })()""")
    log("F-bolsa-nivel", d, ok=d.get("splitSoloEnNv3") is True)

    # B · Nv.3: firePower('split') → cartel + aviso + congelación
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      G.rules.startMatch('match');
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.2, -2.0); G.ball.vel.set(0, 0, 2.0);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.stage = 4;
      c.firePower('split');
      window.__tick(2);
      const ps = c.powerSign;
      return { pend: c._pendingPower ? c._pendingPower.kind : null,
        cartel: ps ? { grupo: !!(ps.group && ps.group.visible), t: ps.t } : null,
        freeze: +G.freezeT.toFixed(2), msg: G.rules.message }; })()""")
    log("B-cartel-aviso", d,
        ok=(d.get("pend") == "split" and
            isinstance(d.get("cartel"), dict) and d["cartel"].get("grupo") is True))

    # C · LANZAMIENTO: clon vivo + MALLA VISIBLE + física + bola blanca
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      let lanzado = -1;
      for (let k = 0; k < 70; k++) {
        window.__tick(1);
        if (lanzado < 0 && c._powerKind === 'split') lanzado = k;
        if (lanzado >= 0 && k >= lanzado + 6) break;
      }
      const cl = c._split;
      const mesh = c.arkanoid.cloneMesh;
      const nan = cl ? (!isFinite(cl.ball.pos.x) || !isFinite(cl.ball.vel.z)) : null;
      return { lanzadoEnTick: lanzado, powerT: +c._powerT.toFixed(2),
        splitVivo: !!cl, nan,
        clonPos: cl ? cl.ball.pos.toArray().map(v=>+v.toFixed(2)) : null,
        meshVisible: mesh.visible,
        meshPos: mesh.position.toArray().map(v=>+v.toFixed(2)),
        meshSigueClon: cl ? (mesh.position.distanceTo(cl.ball.pos) < 0.001) : null,
        bolaBlanca: '#'+G.ballMesh.material.color.getHexString() }; })()""")
    log("C-lanzamiento-visible", d,
        ok=(d.get("lanzadoEnTick", -1) >= 0 and d.get("splitVivo") is True and
            d.get("nan") is False and d.get("meshVisible") is True and
            d.get("meshSigueClon") is True and d.get("bolaBlanca") == "#ffffff"))

    # D · SALVACIÓN: la bola oficial muere con lastHitter='ai' → el clon la hereda
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      if (c._split) c._endSplit();
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.6, -2.0); G.ball.vel.set(0, 0, 1.4);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.firePower('split');
      window.__tick(50);
      if (!c._split) return { __err: 'clon no nació', rules: G.rules.state };
      const clon = c._split.ball;
      G.rules.lastHitter = 'ai';
      G.events.push({ type: 'floor', pos: G.ball.pos.clone(), speed: 2 });
      window.__tick(1);
      return { salvado: !c._split,
        floorRestantes: G.events.filter(e => e.type === 'floor').length,
        bolaTomóClon: G.ball.pos.distanceTo(clon.pos) < 0.05,
        msg: G.rules.message }; })()""")
    log("D-salvacion", d,
        ok=(d.get("salvado") is True and d.get("bolaTomóClon") is True and
            d.get("floorRestantes") == 0))

    # E · PUNTO MUERTO durante el aviso → RE-ARMA y entra en el próximo rallye
    d = js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      G.rules.startMatch('match');
      G.rules.state = 'rally'; G.rules.lastHitter = 'ai';
      G.ball.pos.set(0, 1.6, -2.0); G.ball.vel.set(0, 0, 1.4);
      G.freezeT = 0; c._powerCd = 0; c._powerT = 0; c._endPower();
      c.firePower('split');
      G.rules.state = 'serve';                 // el punto muere DURANTE el aviso
      window.__tick(60);                       // el aviso termina EN SAQUE
      const rearmado = c._pendingPower && c._pendingPower.kind === 'split' && !C._split;
      // vuelve el rallye (el jugador saca) → el split ENTRA
      G.rules.state = 'rally';
      window.__tick(40);                       // 1,2 s de re-arma + margen
      const cl = c._split;
      return { rearmadoEnSaque: rearmado,
        entraEnProximoRallye: !!cl,
        meshVisible: c.arkanoid.cloneMesh.visible,
        kind: c._powerKind }; })()""")
    log("E-rearma", d,
        ok=(d.get("rearmadoEnSaque") is True and d.get("entraEnProximoRallye") is True
            and d.get("meshVisible") is True and d.get("kind") == "split"))

    # limpieza
    js(page, """(() => { const G=window.__PP_GAME,c=G.champs.mod.controller;
      c._endPower(); c._powerCd=0; if (c.powerSign) c.powerSign.hide();
      G.rules.startMatch('match'); G.freezeT=0; return 1; })()""")

    # SMOKE: página sin errores
    time.sleep(2)
    log("smoke-pageerrors", {"n": len(pageerrors), "detalle": pageerrors[:3]},
        ok=len(pageerrors) == 0)

    browser.close()

print("\n== RESUMEN ==")
print(json.dumps({"fallos": fallos, "pageerrors": pageerrors}, ensure_ascii=False, indent=1))
