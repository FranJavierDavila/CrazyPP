#!/usr/bin/env python3
"""QA V2.136 · OESTE — «el túnel como antes + mapa nuevo».

Ruta NATURAL: boot ?champ=oeste (sala) · stage=4 · serveTrigger (gatillo
real) → cartel → TrenAction con FRAME NATURAL (G.animate, lección v2.134).

  A. MAPA NUEVO: el mapa.webp SERVIDO es byte a byte el mapa.png del dueño
     (1699×926); la textura de la sala carga 1699 px; tapas en los NODOS
     re-medidos (1/3/5 más abajo), tapa 284×292 y anillo r 110.
  B. TÚNEL COMO ANTES: SIN subgrupos (6 mallas hijas directas), piezas
     COPLANARES a x=±3.55, bocas de 1.2 m con el ESPEJADO de siempre
     (izq: in+1/out-1 · der: in-1/out+1), cosida sin hueco y —el FIX
     raíz— la textura tunelboca.png APLICADA a las 4 bocas (traverse).
  C. FOTO DEL PORTAL: el túnel en 'pre' con la boca en la ventana →
     screenshot mirando a la ventana izquierda (portal visible).
  D. SMOKE: 0 pageerrors.
"""
import hashlib, json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=oeste"
MAPA_LOCAL = "/home/z/my-project/public/championships/oeste/assets/mapa.webp"
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
window.__t = performance.now();
window.__tick = (n) => {
  const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
  for (let i = 0; i < n; i++) {
    window.__t += 50;
    G.lastTime = window.__t / 1000 - 0.05;
    G.freezeT = 0;
    G.animate(window.__t);
  }
  return { rules: G.rules.state, stage: c.stage, mode: c._stageMode || null };
};
"""

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    page.on("pageerror", lambda e: pageerrors.append(str(e)[:200]))

    okb = boot(page)
    log("boot", {"ok": okb, "version": js(page, "window.__PP_GAME.version || (window.__PP_TELE&&window.__PP_TELE.version)||'?'")},
        ok=okb)
    js(page, TICK_JS)

    # ============ A · MAPA NUEVO ============
    # A1: el fichero SERVIDO es byte a byte el mapa nuevo del dueño
    servido = page.request.get("http://localhost:3000/championships/oeste/assets/mapa.webp")
    body = servido.body()
    h_serv = hashlib.sha256(body).hexdigest()
    h_loc = hashlib.sha256(open(MAPA_LOCAL, "rb").read()).hexdigest()
    log("A1-mapa-servido", {"status": servido.status, "bytes": len(body),
                            "igualAlLocal": h_serv == h_loc},
        ok=(servido.status == 200 and h_serv == h_loc))

    # A2: textura del mapa de la sala cargada a 1699 px + TAPAS en los
    # NODOS re-medidos + anillo a escala 110/120
    time.sleep(2.5)
    page.evaluate("window.__tick(4)")
    da = js(page, """(() => { const s = window.__PP_OESTE.ctrl();
      if (!s || !s.mapa) return { __err: 'sin sala/mapa' };
      const mapa = s.mapa;
      const w = mapa.material.map && mapa.material.map.image ?
                mapa.material.map.image.width : 0;
      // tapas en coords locales del mapa: x = (n.x/1699-0.5)*PW
      const PW = 1.68, PH = PW * 926 / 1699;
      const NODOS = [[198,367],[516,458],[863,349],[1173,461],[1536,293]];
      const tapas = (s.tapas || []).map(m => [
        +(m.position.x.toFixed(3)), +(m.position.y.toFixed(3))]);
      const esperadas = NODOS.slice(1).map(([nx, ny]) => [
        +((nx / 1699 - 0.5) * PW).toFixed(3),
        +((0.5 - ny / 926) * PH).toFixed(3)]);
      const TW = +(284 / 1699 * PW).toFixed(3), TH = +(292 / 926 * PH).toFixed(3);
      const tapaSize = s.tapas && s.tapas[0] ?
        [+s.tapas[0].geometry.parameters.width.toFixed(3),
         +s.tapas[0].geometry.parameters.height.toFixed(3)] : [0, 0];
      const anillo = s.mapaMarker;
      return { mapaW: w, mapaVisible: mapa.visible,
               nTapas: (s.tapas || []).length, tapas, esperadas,
               tapaSize, TW, TH,
               anilloEscala: anillo ? +anillo.scale.x.toFixed(4) : 0,
               anilloEsperado: +(110 / 120).toFixed(4) }; })()""")
    ok_a2 = (da.get("mapaW") == 1699 and
             da.get("nTapas") == 4 and
             all(
                 abs(p[0] - e[0]) < 2e-3 and abs(p[1] - e[1]) < 2e-3
                 for p, e in zip(da.get("tapas", []), da.get("esperadas", []))) and
             abs(da.get("tapaSize", [0, 0])[0] - da.get("TW", -1)) < 2e-3 and
             abs(da.get("tapaSize", [0, 0])[1] - da.get("TH", -1)) < 2e-3 and
             abs(da.get("anilloEscala", 0) - da.get("anilloEsperado", -1)) < 1e-3)
    log("A2-nodos-tapas-anillo", da, ok=ok_a2)

    # A3: FOTO de la sala mirando al mapa (pared izquierda)
    page.evaluate("window.__tick(2)")
    js(page, """(() => { const G = window.__PP_GAME, s = window.__PP_OESTE.ctrl();
      // mira a la pared del mapa (x=-2.98, z=-0.9 desde el ojo z≈0.4)
      const dir = Math.atan2(-(-2.98), -(-0.9 - 0.4));
      if (G.rig) G.rig.rotation.y = dir;
      s.mapa.visible = true;
      return { yaw: +dir.toFixed(3) }; })()""")
    time.sleep(0.6)
    page.evaluate("window.__tick(2)")
    page.screenshot(path="/home/z/my-project/scripts/_qa_v2136_mapa.png")
    js(page, "(() => { const G = window.__PP_GAME; if (G.rig) G.rig.rotation.y = 0; return 1; })()")

    # ============ ruta natural a la etapa 4 (TREN) ============
    d = js(page, """(() => {
      const c = window.__PP_GAME.champs.mod.controller;
      c.stage = 4;
      c._armT = 0; c._duelOn = false;
      c.serveTrigger(0);
      return { instrK: c._instrK || null, mode: c._stageMode || null };
    })()""")
    log("gatillo-etapa4", d, ok=(d.get("instrK") == "tren"))
    page.evaluate("window.__tick(6)")
    js(page, """(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      return { cerrado: !G._instr }; })()""")
    t0 = time.time()
    tren = None
    while time.time() - t0 < 15:
        tren = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
          return (c._tren && c._stageMode === 'tren') ?
            { phase: c._tren.phase } : null; })()""")
        if tren:
            break
        page.evaluate("window.__tick(6)")
        time.sleep(0.5)
    log("tren-arranca", tren, ok=bool(tren))
    page.evaluate("window.__tick(6)")

    # ============ B · TÚNEL COMO ANTES ============
    time.sleep(2.5)   # margen para que tunelboca.png cargue
    db = js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      if (!t.tunelGrp) return { __err: 'sin tunelGrp' };
      const g = t.tunelGrp;
      const grupos = g.children.filter(m => m.isGroup === true);
      const bocas = [], bandas = [];
      g.traverse(m => {
        if (!m.isMesh) return;
        const info = { x: +m.position.x.toFixed(3), y: +m.position.y.toFixed(3),
                       z: +m.position.z.toFixed(3),
                       w: +m.geometry.parameters.width.toFixed(3),
                       h: +m.geometry.parameters.height.toFixed(3),
                       sx: m.scale.x, boca: !!(m.userData && m.userData.boca),
                       map: !!(m.material.map && m.material.map.image),
                       mapW: m.material.map && m.material.map.image ?
                             m.material.map.image.width : 0 };
        if (info.boca) bocas.push(info); else bandas.push(info);
      });
      return { grupos: grupos.length, total: g.children.length,
               bocas: bocas.sort((a, b) => a.x - b.x),
               bandas: bandas.map(b => ({ x: b.x, z: b.z, w: b.w, h: b.h,
                                          map: b.map })) }; })()""")
    bocas = db.get("bocas", [])
    bandas = db.get("bandas", [])
    ok_b = (
        db.get("grupos") == 0 and db.get("total") == 6 and
        len(bocas) == 4 and len(bandas) == 2 and
        all(abs(b["x"]) - 3.55 < 1e-3 and abs(b["x"]) for b in bocas + bandas) and
        all(abs(b["w"] - 1.2) < 1e-3 and abs(b["h"] - 1.2) < 1e-3 for b in bocas) and
        all(abs(b["y"] - 1.8) < 1e-3 for b in bocas) and
        # espejado como siempre: izq (x<0) in sx=1/out sx=-1 · der in sx=-1/out sx=1
        # (in: z=0 · out: z=-(len+bh)=-27.6)
        all(b["map"] and b["mapW"] == 512 for b in bocas) and
        all(abs(b["z"] + (1.2 / 2 + 26.4 / 2)) < 1e-3 for b in bandas))
    # espejado explícito
    esp = None
    if len(bocas) == 4:
        izq_in = next((b for b in bocas if b["x"] < 0 and b["z"] == 0), None)
        izq_out = next((b for b in bocas if b["x"] < 0 and b["z"] < -20), None)
        der_in = next((b for b in bocas if b["x"] > 0 and b["z"] == 0), None)
        der_out = next((b for b in bocas if b["x"] > 0 and b["z"] < -20), None)
        esp = (izq_in and izq_out and der_in and der_out and
               izq_in["sx"] == 1 and izq_out["sx"] == -1 and
               der_in["sx"] == -1 and der_out["sx"] == 1)
        ok_b = ok_b and esp
    log("B-tunel-coplanar", {"grupos": db.get("grupos"), "total": db.get("total"),
                             "bocas": len(bocas), "bandas": len(bandas),
                             "texturas512": all(b["map"] for b in bocas),
                             "espejadoOK": bool(esp), "detalle": db}, ok=ok_b)

    # ============ C · FOTO DEL PORTAL EN LA VENTANA ============
    js(page, """(() => { const t = window.__PP_GAME.champs.mod.controller._tren;
      const G = window.__PP_GAME;
      t._tunnelPhase = 'pre'; t._tunnelT2 = 0;
      t._tunelZ = -1.82;                       // boca centrada en la ventana
      t.tunelGrp.position.z = t._tunelZ;
      t.tunelGrp.visible = true;
      // mira a la ventana izquierda: boca en (-3.55, 1.8, -1.82), ojo z≈0.4
      if (G.rig) G.rig.rotation.y = Math.atan2(3.55, 1.82 - 0.4) * -1 + Math.PI;
      return { yaw: +G.rig.rotation.y.toFixed(3) }; })()""")
    time.sleep(0.6)
    page.evaluate("window.__tick(1)")
    page.screenshot(path="/home/z/my-project/scripts/_qa_v2136_portal.png")
    js(page, "(() => { const G = window.__PP_GAME; if (G.rig) G.rig.rotation.y = 0; return 1; })()")

    # ============ D · SMOKE ============
    log("D-pageerrors", {"n": len(pageerrors), "errs": pageerrors[:3]},
        ok=(len(pageerrors) == 0))

    browser.close()

print("\n==== RESULTADO QA V2.136 ====")
if fallos:
    print("FALLOS:", fallos)
    raise SystemExit(1)
print("TODO VERDE ✔")
