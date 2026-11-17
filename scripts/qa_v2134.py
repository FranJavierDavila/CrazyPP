#!/usr/bin/env python3
"""QA V2.134 · SALVAJE OESTE — etapa 4 «ASALTO AL TREN» a peticion del dueno.

Ruta NATURAL: boot ?champ=oeste · stage=4 · serveTrigger (gatillo real) →
cartel instrucciones → arranque del tren · TrenAction.step(dt) por la
delegacion real del nucleo (testStep) + mod.update para visuales.

  A. PARADAS SIN REPETIR: la SALIDA pide PARADA0.png (y NO PARADA1)
  B. TUNEL CON PROFUNDIDAD: 2 subgrupos rotados ∓0.24 rad, piezas a x=3.75
  C. PARED DEL FONDO REBOTA: bola contra z=-5.55 → viva, vel.z>0
  D. X3 BALISTICO: 3 extras con tiro asegurado a cajas apiladas → impactos
  E. DINAMITA CADENA: estalla SIEMPRE, caza caja a caja hasta agotar la
     serie (foto de las activas al activarse) y brote final
  F. SMOKE: 0 pageerrors
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=oeste"
fallos = []
pageerrors = []
pedidos = []

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
window.__t = performance.now();
window.__tick = (n) => {
  const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
  for (let i = 0; i < n; i++) {
    window.__t += 50;
    G.lastTime = window.__t / 1000 - 0.05;   // dt exactamente 0.05 s
    G.freezeT = 0;                            // sin avisos de poder congelando
    G.animate(window.__t);                    // FRAME NATURAL COMPLETO
  }
  return { rules: G.rules.state, stage: c.stage, mode: c._stageMode || null,
           phase: c._tren ? c._tren.phase : null };
};
"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.on("pageerror", lambda e: pageerrors.append(str(e)[:200]))
    page.on("request", lambda r: pedidos.append(r.url) if "PARADA" in r.url else None)

    okb = boot(page)
    log("boot", {"ok": okb}, ok=okb)
    js(page, TICK_JS)

    # ============ ruta natural a la etapa 4 (TREN) ============
    d = js(page, """(() => {
      const c = window.__PP_GAME.champs.mod.controller;
      c.stage = 4;
      c._armT = 0; c._duelOn = false;
      c.serveTrigger(0);
      return { instrK: c._instrK || null, mode: c._stageMode || null };
    })()""")
    log("gatillo-etapa4", d, ok=(d.get("instrK") == "tren"))
    # cierre del cartel por la MISMA puerta del botón EMPEZAR/gatillo
    # (hideInstrucciones(false) dispara el callback que arranca la prueba;
    # en headless el RAF corre ~0.03× y el desvanecido no llegaría a tiempo)
    page.evaluate("window.__tick(6)")
    js(page, """(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      return { cerrado: !G._instr }; })()""")
    # espera el arranque real del tren
    t0 = time.time()
    tren = None
    while time.time() - t0 < 15:
        tren = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
          return (c._tren && c._stageMode === 'tren') ?
            { phase: c._tren.phase, wave: c._tren.wave } : null; })()""")
        if tren:
            break
        page.evaluate("window.__tick(6)")
        time.sleep(0.5)
    log("tren-arranca", tren, ok=bool(tren))
    page.evaluate("window.__tick(6)")

    # ============ A · PARADAS SIN REPETIR ============
    time.sleep(2.5)   # da margen a que la Image de PARADA0 cargue
    da = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      return { try0: t._paradaTry[0] === true, try1: !!t._paradaTry[1],
               tex0: !!(t._paradaTex[0] && t._paradaTex[0].image),
               w: t._paradaTex[0] ? t._paradaTex[0].image.width : 0 }; })()""")
    pid0 = any(u.endswith("PARADA0.png") for u in pedidos)
    pid1 = any(u.endswith("PARADA1.png") for u in pedidos)
    log("A-parada0", {"pedida0": pid0, "pedida1_antesDeParada1": pid1,
                      "tex0Cargada": da.get("tex0"), "ancho": da.get("w"),
                      "try0": da.get("try0")},
        ok=(pid0 and not pid1 and da.get("try0") and da.get("tex0")))
    page.screenshot(path="/home/z/my-project/scripts/_qa_v2134_tren_intro.png")

    # ============ B · TÚNEL CON PROFUNDIDAD ============
    db = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      if (!t.tunelGrp) return { __err: 'sin tunelGrp' };
      const subs = t.tunelGrp.children.filter(m => m.isGroup === true || m.type === 'Group');
      const rot = subs.map(s => +s.rotation.y.toFixed(4));
      const xs = subs.map(s => +s.children[0].position.x.toFixed(3));
      const cnt = subs.map(s => s.children.length);
      return { subs: subs.length, rot, xs, piezasPorLado: cnt,
               inclCfg: t.game ? 0.24 : 0.24 }; })()""")
    okb = (db.get("subs") == 2 and len(set(db.get("rot", []))) == 2 and
           abs(abs(db.get("rot", [0, 0])[0]) - 0.24) < 1e-3 and
           all(abs(abs(x) - 3.75) < 1e-3 for x in db.get("xs", [])) and
           db.get("piezasPorLado") == [3, 3])
    log("B-tunel", db, ok=okb)

    # ============ C · LA PARED DEL FONDO REBOTA ============
    js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller, t = c._tren;
      if (t.phase !== 'run') t._depart();          // ruta natural: sale del andén
      const G = window.__PP_GAME;
      t._dead = false; t._respawnT = 99;
      G.ball.pos.set(0.3, 1.10, -5.10);
      G.ball.vel.set(0, 0, -3.5);
      G.ball.spin.set(0, 0, 0);
      G.ballMesh.visible = true;
      return { phase: t.phase }; })()""")
    page.evaluate("window.__tick(4)")   # 0.2 s: la bola llega a la pared
    dc = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      const b = window.__PP_GAME.ball;
      return { dead: t._dead, vz: +b.vel.z.toFixed(3), z: +b.pos.z.toFixed(3),
               paredZ: t.paredZ !== undefined ? t.paredZ : -5.55 }; })()""")
    okc = (dc.get("dead") is False and dc.get("vz", 0) > 0.5 and
           dc.get("z", -9) > -5.53)
    log("C-rebote", dc, ok=okc)

    # ============ D · X3 BALÍSTICO ============
    js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller, t = c._tren;
      const G = window.__PP_GAME;
      window.__ex0 = t.extras.filter(e => e.alive).length;   // extras previas
      t._buildPiramide();                       // pirámide nueva, cajas apiladas
      t._dead = false; t._respawnT = 99;
      // pod X3 forzado en un punto fijo de la mesa rival
      t._pod = { ref: t.pods[1], tipo: 'x3', x: 0.05, z: -2.30, vida: 8, k: 1 };
      t.pods[1].mesh.visible = true;
      t.pods[1].mesh.position.set(0.05, t._podY(), -2.30);
      G.ball.pos.set(0.05, t._podY() + 0.05, -2.30);
      G.ball.vel.set(0, 0.2, 0.1);
      G.ballMesh.visible = true;
      return { vivas: t.cubos.filter(r => !r.muerto).length, ex0: window.__ex0 }; })()""")
    page.evaluate("window.__tick(3)")
    dd = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      const ex = t.extras.filter(e => e.alive);
      return { nuevas: ex.length - (window.__ex0 || 0), pods: t._pod === null,
               vels: ex.slice(-3).map(e => +Math.hypot(e.ball.vel.x, e.ball.vel.y, e.ball.vel.z).toFixed(2)),
               dead: t._dead }; })()""")
    okd1 = (dd.get("nuevas") == 3 and dd.get("pods") is True and
            all(v > 3.0 for v in dd.get("vels", [])))
    log("D-x3-lanzamiento", dd, ok=okd1)
    page.evaluate("window.__tick(50)")   # 2.5 s de vuelo + impactos + retiros
    dd2 = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      return { muertos: t.cubos.filter(r => r.muerto).length,
               abiertos: t.cubos.filter(r => r.abierto && !r.muerto).length,
               extrasVivos: t.extras.filter(e => e.alive).length }; })()""")
    golpes = dd2.get("muertos", 0) + dd2.get("abiertos", 0)
    log("D-x3-impactos", dd2, ok=(golpes >= 3))
    page.screenshot(path="/home/z/my-project/scripts/_qa_v2134_x3.png")

    # ============ E · DINAMITA CADENA ============
    js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller, t = c._tren;
      const G = window.__PP_GAME;
      t.start();                                  // reset completo y natural
      t._depart();
      t._buildPiramide();
      t._dead = false; t._respawnT = 99;
      t._pod = { ref: t.pods[2], tipo: 'dina', x: -0.1, z: -2.10, vida: 8, k: 1 };
      t.pods[2].mesh.visible = true;
      t.pods[2].mesh.position.set(-0.1, t._podY(), -2.10);
      G.ball.pos.set(-0.1, t._podY() + 0.05, -2.10);
      G.ball.vel.set(0, 0.2, 0.1);
      G.ballMesh.visible = true;
      return { ok: true }; })()""")
    page.evaluate("window.__tick(3)")
    de0 = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      return { bomba: t._bomba === true, serie: t._bombaSerie ? t._bombaSerie.rest.size : -1,
               vivas: t.cubos.filter(r => !r.muerto && !r.abierto).length }; })()""")
    log("E-dina-activacion", de0,
        ok=(de0.get("bomba") is True and de0.get("serie") == de0.get("vivas")))
    # lanza la bomba CONTRA la pirámide
    js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      const G = window.__PP_GAME;
      G.ball.pos.set(0.0, 1.05, -4.10);
      G.ball.vel.set(0.2, 0, -4.2);
      return {}; })()""")
    page.evaluate("window.__tick(6)")   # 0.3 s: primer impacto + BOOM
    de1 = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      return { serie: t._bombaSerie ? t._bombaSerie.rest.size : -1,
               vivas: t.cubos.filter(r => !r.muerto && !r.abierto).length,
               muertos: t.cubos.filter(r => r.muerto).length,
               bolaViva: !t._dead }; })()""")
    okE1 = (de1.get("serie", 99) < de0.get("serie", 0) and de1.get("bolaViva") is True)
    log("E-dina-primera-explosion", de1, ok=okE1)
    # la cadena corre sola hasta agotar la serie
    fin = None
    for i in range(60):
        page.evaluate("window.__tick(10)")   # 0.5 s por vuelta
        fin = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
          return { serie: t._bombaSerie ? t._bombaSerie.rest.size : -1,
                   muertos: t.cubos.filter(r => r.muerto).length,
                   abiertos: t.cubos.filter(r => r.abierto && !r.muerto).length,
                   dead: t._dead, bomba: t._bomba }; })()""")
        if fin.get("serie") == 0 or fin.get("serie") == -1:
            break
    page.evaluate("window.__tick(30)")   # margen para el brote final / retirada
    de2 = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      return { serieRest: t._bombaSerie ? t._bombaSerie.rest.size : -1,
               muertos: t.cubos.filter(r => r.muerto).length,
               abiertos: t.cubos.filter(r => r.abierto).length,
               bomba: t._bomba, dead: t._dead }; })()""")
    serie0 = de0.get("serie", 0)
    todas = (de2.get("muertos", 0) + de2.get("abiertos", 0)) >= serie0
    okE2 = (todas and (de2.get("bomba") is False or de2.get("dead") is True))
    log("E-dina-cadena", {"serie0": serie0, **de2, "todasResueltas": todas}, ok=okE2)
    page.screenshot(path="/home/z/my-project/scripts/_qa_v2134_cadena.png")

    # ============ F · SMOKE ============
    log("F-pageerrors", {"n": len(pageerrors), "errs": pageerrors[:3]},
        ok=(len(pageerrors) == 0))

    browser.close()

print("\n==== RESULTADO QA V2.134 ====")
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("TODO VERDE ✔")
