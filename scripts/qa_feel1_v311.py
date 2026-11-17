#!/usr/bin/env python3
"""QA V3.1.1-FEEL1 — game-feel (3 ajustes del dueño) sobre la SRV2.

1) GRACE del saque: la detección sigue viva unos ms tras un cruce muy justo
   al borde de la hoja (SOLO en el vuelo del saque) — __PP_FEEL_LAB grace.
2) REBOTE REAL sobre pala quieta: los botes decaen hasta pararse, la bola no
   atraviesa la hoja, el reposo es mudo y el suelo de salida de los golpes
   activos (2,3 m/s) queda INTACTO — __PP_FEEL_LAB decay/stroke.
3) BOTÓN B = PROMPT «Menú Principal ¿SI/No?» en estancias ≠ Hall: NO cierra
   y sigues; SI va al HALL con el menú principal delante.

Más REGRESIÓN completa de la SRV2: los 9 casos del saque realista, ley de
asistencia D, flujo del hall, DIMS/tiers y 0 pageerrors.
"""
import asyncio, sys, urllib.request
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT_PNG = "/home/z/my-project/download/qa_feel1_portada.png"

FAILS = []
def check(name, ok, detail=""):
    tag = "OK " if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)

def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return r.read()

def head(url):
    req = urllib.request.Request(url, method="HEAD")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, int(r.headers.get("Content-Length", "0"))

# ---------------------------------------------------------------- estáticos
print("== ESTÁTICOS ==")
html = fetch("/game.html").decode("utf-8", "replace")
check("VERSION 3.1.1-FEEL1", "const VERSION = '3.1.1-FEEL1'" in html)
check("badge estático V3.1.1-FEEL1", "V3.1.1-FEEL1" in html)
# --- Ajuste 1: gracia del saque ---
for anchor in ["lateMs: 14,", "lateInPlane: 0.02,", "lateSkin: 0.012,"]:
    check("SERVE_TUNE gracia: " + anchor.split(":")[0], anchor in html)
check("grace sólo en serveFlight (armado)",
      "if (pad.serveFlight) {\n      const rl = reach + SERVE_TUNE.lateInPlane;" in html)
check("grace en el gate de detección (nearPlaneGrace)", "nearPlaneGrace" in html)
check("grace decae con la física (stepPhysics)", "if (ball.__serveGrace > 0) ball.__serveGrace -= h;" in html)
# --- Ajuste 2: rebote real ---
check("suelo escalado por velocidad de pala", "exitFloor = DIMS.minExitSpeed * floorK;" in html)
check("palancas del suelo (exitFloorFrom/To)", "exitFloorFrom: 0.15," in html and "exitFloorTo: 1.0," in html)
check("contacto de reposo ignora cooldown (pala quieta)",
      "pad.vel.lengthSq() <= SERVE_TUNE.restPadSpeed * SERVE_TUNE.restPadSpeed;" in html)
check("micro-contactos mudos (restEventMin)", "Math.abs(vRelN) >= SERVE_TUNE.restEventMin" in html)
check("evento gated por impacto (restEventMin) + saque siempre emite",
      "if (pad.serveFlight || Math.abs(vRelN) >= SERVE_TUNE.restEventMin) {" in html)
check("cara de contacto por POSICIÓN sin cruce (anti-túnel en reposo)",
      "if (crossing) {\n    if (relVel.dot(tmpN) > 0) tmpN.negate();\n  } else {\n    if (dNow < 0) tmpN.negate();\n  }" in html)
# --- Ajuste 3: prompt B ---
check("B: prompt fuera del hall", "this.openHallAsk();" in html)
check("B: toggle normal en hall/online/AR",
      "if (this.menuOpen || this.inHall || this.net.online || this.inAR) {" in html)
check("página hallask en drawMenu", "this.menuPage === 'hallask'" in html)
check("drawMenuHallAsk definido", "drawMenuHallAsk(rects) {" in html)
check("casos hallask_si/hallask_no", "case 'hallask_si':" in html and "case 'hallask_no':" in html)
check("goHomeHall compartido (homehall + SI)",
      "goHomeHall() {" in html and "if (this.goHomeHall()) {" in html)
check("i18n hallask es/en", "hallask_yes_btn: 'SÍ, SALIR AL HALL'" in html
      and "hallask_yes_btn: 'YES, GO TO THE HALL'" in html)
check("lab game-feel expuesto", "window.__PP_FEEL_LAB" in html)
# --- regresión SRV2 ---
check("sin guardián antiguo (cerrar menú sacaba del hall)",
      "if (presenting && this.inHall && !this.menuOpen" not in html)
for anchor in ["this.exitHall();          // v3.1.0-SRV2: arrancar un modo saca del hall",
               "g.exitHall();             // v3.1.0-SRV2: un campeonato se juea en la cancha",
               "game.exitHall();                          // v3.1.0-SRV2: un modo se juea en la cancha",
               "game.exitHall();                        // v3.1.0-SRV2: el ajuste vive en la cancha",
               "this.exitHall();          // v3.1.0-SRV2: la sesión online se juea en la cancha"]:
    check("exitHall en arranque: " + anchor.split("//")[1].strip()[:34], anchor in html)
check("cascada antigua fuera (tier.lerp1)", "tier.lerp1" not in html)
check("SERVE_TUNE definido", "const SERVE_TUNE = {" in html)
check("asistencia acotada definida", "function applyServeProgressiveAssist(" in html)
check("lab de saque expuesto", "window.__PP_SERVE_LAB" in html)
check("botón homehall en hub", "btn('homehall'" in html)
check("lanzamiento natural puro (release)", "this.tossFromHand(i, false);" in html)
check("gatillo asistido separado", "serveTossFromTee(true)" in html and "serveTossFromTee(false)" in html)
check("i18n hall_home_btn es/en", "hall_home_btn: '⌂ VOLVER AL HALL'" in html and "hall_home_btn: '⌂ BACK TO HALL'" in html)
check("DIMS intactos fis=1 perks=1", "physicsRealism: 1," in html and "paddlePerks: 1," in html)

# ---------------------------------------------------------------- funcionales
CASES_JS = """
async () => {
  const L = window.__PP_SERVE_LAB, D = window.__ppDebug;
  if (!L || !D) return { fatal: 'sin ganchos QA (__PP_SERVE_LAB/__ppDebug)' };
  const V3 = window.__PP_VEC3;
  const out = {};
  // CASO 1 · saque correcto: se BUSCA un gesto real (cara + swing) cuya
  // salida física sea ya un saque legal y se verifica que el sistema NO lo
  // toca (w=0) y que la salida es idéntica sin asistencia.
  out.c1 = null;
  outer:
  for (const pitch of [-20, -25, -30, -35, -40, -45, -50]) {
    for (const pvz of [-1.0, -1.4, -1.8, -2.2, -2.6]) {
      for (const pvy of [0, 0.3, 0.6]) {
        const r = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz, padVelY: pvy,
          assist: true, tier: 'medium' });
        if (r.hit && r.sim && r.sim.ok && r.exitZ < -1.2) {
          const raw = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz, padVelY: pvy,
            assist: false });
          out.c1 = { pitch, pvz, pvy, r, rawDelta: Math.abs(raw.exitSpeed - r.exitSpeed) };
          break outer;
        }
      }
    }
  }
  // CASO 2 · pequeñas imprecisiones de timing: contacto algo tarde (6 cm) y
  // casi en el plano (1 cm) — la tolerancia los cubre
  out.c2a = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.06 });
  out.c2b = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.012 });
  // CASO 3 · golpe antes/después del instante ideal: la bola CRUZA el plano
  // dentro del frame (TOI) — debe resolver el contacto
  out.c3 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, ballVelZ: 1.4 });
  // CASO 4 · pala PARALELA a la mesa (cara al cielo): salida débil y hacia
  // arriba, NUNCA convertida en saque válido (w=0)
  out.c4 = L({ yawDeg: 180, pitchDeg: -90, padVelZ: -2.6, assist: true, tier: 'medium' });
  // CASO 5 · bola DETRÁS de la goma (goma hacia fuera de la mesa): sin
  // contacto útil — la pala barre paralela y la bola está al otro lado de la
  // hoja (v3.1.1: dist negativa — la base interpolada ya no es fantasma)
  out.c5 = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, assist: true, tier: 'medium',
    dist: -0.06 });
  // CASO 6 · contacto con el CANTO: golpe sordo (menos velocidad que el centro)
  out.c6 = [0, 1, 2].map(() => L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6,
    offX: 0.168, assist: false }));
  out.c6c = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, assist: false });
  // CASO 7 · lanzamiento sin velocidad suficiente (swing flojo): roce flojo,
  // sin asistencia (w=0) → el árbitro lo juzga falta
  out.c7 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -0.30, assist: true, tier: 'medium' });
  // CASO 8 · golpe SIN contacto real: la bola pasa 30 cm fuera del plano de
  // la hoja — nada ocurre
  out.c8 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, offY: -0.30 });
  // CASO 9 · red / fuera / sin bote: el simulador (misma física) los caza.
  // v3.1.1: trayectorias con retornos RICOS del sim (los casos antiguos
  // caían en retornos tempranos {ok:false} sin telemetría).
  // Math.random DETERMINISTA durante el bloque: findServeVelocity sortea el
  // giro (±2) y la lateralidad — sin semilla, la referencia del QA y la
  // referencia INTERNA de la asistencia difieren y la ley D sería flaky.
  const S = D.simulateServePath;
  const __rnd = Math.random;
  Math.random = () => 0.5;
  try {
  // roza la banda de la red (y en el cruce ≈ 0,92 m: netTouch, no atrapada)
  // y luego bota en campo rival sin bote propio → ok:false con netTouch:true
  out.c9net = S(new V3(0, 1.02, -0.5), new V3(0, 1.16, -4.0), new V3(), 1);
  // pasa LIMPIA por encima de la red (y ≈ 0,96) pero SIN bote propio →
  // ok:false con ownBounce:false (falta de saque)
  out.c9out = S(new V3(0, 1.02, -0.5), new V3(0, 0.5, -7.0), new V3(), 1);
  // bola muerta bajo la mesa: cae al suelo sin botes → ok:false
  out.c9dead = S(new V3(0.25, 0.6, -0.55), new V3(0, -2.5, 0.05), new V3(), 1);
  // referencia legal del solver (misma física, misma semilla) — desde una
  // posición de saque REAL (tras la línea de fondo, pecho): allí el solver
  // encuentra candidato VALIDADO (desde (0,1.02,-0.5), sobre la mesa, no)
  out.c9ref = D.findServeVelocity(new V3(0.0, 1.15, 0.0), 1, null);
  out.c9ok = S(new V3(0.0, 1.15, 0.0), out.c9ref.v, out.c9ref.spin, 1);
  // LEY DE ASISTENCIA (D): decae linealmente y muere fuera del margen
  const pos = new V3(0, 1.15, 0.0);
  const ref = D.findServeVelocity(pos, 1, null);
  const axis = new V3(1, 0, 0);
  const deg = THREE_DEG;
  const mk = (rotDeg) => {
    const v = ref.v.clone().applyAxisAngle(axis, rotDeg * deg);
    const b = { pos: pos.clone(), vel: v, spin: new V3() };
    return D.applyServeProgressiveAssist(b, null, D.serveTiers.medium);
  };
  out.legal = mk(0);          // legal → w 0 (no se toca)
  out.near = mk(8);           // dentro del margen (17°) → 0 < w < máximo
  out.far = mk(45);           // fuera del margen → w 0 (jamás se corrige)
  } finally { Math.random = __rnd; }
  return out;
}
"""

FEEL_JS = """
() => {
  const L = window.__PP_FEEL_LAB, tune = window.__ppDebug.serveTune;
  if (!L) return { fatal: 'sin __PP_FEEL_LAB' };
  const out = {};
  out.graceOn = L({ mode: 'grace' });
  const saved = tune.lateMs;
  tune.lateMs = 0;
  out.graceOff = L({ mode: 'grace' });
  tune.lateMs = saved;
  out.decay = L({ mode: 'decay' });
  out.stroke = L({ mode: 'stroke' });
  // bola SUAVE + pala que SUBE: la salida natural (≈0,7) queda por DEBAJO
  // del suelo — si el suelo está vivo, la salida sale disparada a ≥ 2,25
  out.strokeFloor = L({ mode: 'stroke', padVy: 1.5, dropH: 0.02 });
  // empuje LENTO (0,4 m/s): suelo parcial ≈ 0,68 — ni pleno ni natural puro
  out.strokeSlow = L({ mode: 'stroke', padVy: 0.4, dropH: 0.02 });
  out.graceKnobs = { lateMs: tune.lateMs, lateInPlane: tune.lateInPlane,
    lateSkin: tune.lateSkin, exitFloorFrom: tune.exitFloorFrom,
    exitFloorTo: tune.exitFloorTo, restPadSpeed: tune.restPadSpeed,
    restEventMin: tune.restEventMin };
  return out;
}
"""

VEC3_SETUP = """
() => { window.__PP_VEC3 = (window.__PP_GAME && window.__PP_GAME.ball &&
  window.__PP_GAME.ball.pos) ? window.__PP_GAME.ball.pos.constructor
  : (window.THREE ? window.THREE.Vector3 : null);
  window.THREE_DEG = Math.PI / 180; }
"""

async def main():
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(BASE + "/game.html", wait_until="domcontentloaded")
        await page.wait_for_timeout(4500)

        print("== GANCHOS ==")
        hooks = await page.evaluate(
            "!!window.__PP_SERVE_LAB && !!window.__PP_FEEL_LAB && !!window.__ppDebug && !!window.__PP_GAME")
        check("__PP_SERVE_LAB + __PP_FEEL_LAB + __ppDebug + __PP_GAME", bool(hooks))
        await page.evaluate(VEC3_SETUP)

        print("== AJUSTE 1 · GRACE DEL SAQUE ==")
        f = await page.evaluate(FEEL_JS)
        if f.get("fatal"):
            check("lab game-feel", False, f["fatal"]); await browser.close(); return
        g_on, g_off = f["graceOn"], f["graceOff"]
        check("gracia ON: el golpe muy justo CONECTA", g_on["hit"] is True,
              f"hitMs={g_on['hitMs']} offX={g_on['offX']}")
        check("gracia ON: conecta dentro de la ventana (≤ 25 ms)",
              g_on["hit"] and 0 <= g_on["hitMs"] <= 25, f"hitMs={g_on['hitMs']}")
        check("gracia OFF (lateMs=0): el mismo gesto NO conecta", g_off["hit"] is False)
        k = f["graceKnobs"]
        check("palancas de gracia vivas en SERVE_TUNE",
              k["lateMs"] == 14 and k["lateInPlane"] == 0.02 and k["lateSkin"] == 0.012, str(k))

        print("== AJUSTE 2 · REBOTE REAL SOBRE PALA QUIETA ==")
        d = f["decay"]
        b = d["bounces"]
        check("los botes DECAEN (≥5 botes reales)", len(b) >= 5, str(b))
        check("decaimiento monótono (sin suelo de rebote)",
              all(v < b[i - 1] for i, v in enumerate(b) if i > 0), str(b))
        check("la bola NO atraviesa la hoja", d["fellThrough"] is False,
              f"gap={d['gap']}")
        check("reposo sobre la hoja (gap ≈ contacto)", 0.015 < d["gap"] < 0.035,
              f"gap={d['gap']}")
        check("reposo en calma (vel < 0,05 m/s)", d["restSpeed"] < 0.05,
              f"v={d['restSpeed']}")
        check("reposo MUDO (micro-contactos sin eventos)", d["eventCount"] == len(b),
              f"events={d['eventCount']} botes={len(b)}")
        s = f["stroke"]
        check("swing real: suelo de salida INTACTO (≥ 2,25 m/s)", s["maxExit"] >= 2.25,
              f"maxExit={s['maxExit']}")
        sf = f["strokeFloor"]
        check("suelo VIVO con pala en movimiento (bola suave → ≥ 2,25 m/s)",
              sf["maxExit"] >= 2.25, f"maxExit={sf['maxExit']}")
        ss = f["strokeSlow"]
        check("empuje lento: suelo PARCIAL (< 2,25 m/s, no muerto ≥ 0,3)",
              0.3 <= ss["maxExit"] < 2.25, f"maxExit={ss['maxExit']}")

        print("== 9 CASOS DEL REQUISITO (regresión SRV2, física real) ==")
        r = await page.evaluate(CASES_JS)
        if r.get("fatal"):
            check("ganchos QA", False, r["fatal"]); await browser.close(); return
        c1 = r["c1"]
        check("1 · existe gesto correcto con salida legal", bool(c1),
              (f"pitch={c1['pitch']} pvz={c1['pvz']} pvy={c1['pvy']}"
               if c1 else "ningún gesto de la rejilla produjo saque legal"))
        if c1:
            check("1 · salida hacia la red", c1["r"]["exitZ"] < -1.2,
                  f"exitZ={c1['r']['exitZ']}")
            check("1 · el sistema NO toca el saque legal (w=0)",
                  c1["r"]["assist"]["w"] == 0,
                  f"w={c1['r']['assist']['w']} err={c1['r']['assist']['err']}")
            check("1 · gesto preservado (idéntico sin asistencia)",
                  c1["rawDelta"] < 0.01, f"Δspd={c1['rawDelta']:.4f}")
        check("2 · timing tarde (6 cm): contacto tolerado", r["c2a"]["hit"],
              f"spd={r['c2a']['exitSpeed']}")
        check("2 · timing casi en plano (1,2 cm): contacto", r["c2b"]["hit"])
        check("3 · cruce dentro del frame (TOI): contacto", r["c3"]["hit"],
              f"exitZ={r['c3']['exitZ']}")
        check("3 · la salida del cruce va hacia la red", r["c3"]["hit"] and r["c3"]["exitZ"] < -1.0,
              f"exitZ={r['c3']['exitZ']}")
        c4 = r["c4"]
        check("4 · cara al cielo: salida débil (< 1,6 m/s)", c4["hit"] and c4["exitSpeed"] < 1.6,
              f"spd={c4['exitSpeed']}")
        check("4 · cara al cielo: sin saque válido (sim fallo)", c4.get("sim", {}).get("ok") is False)
        check("4 · cara al cielo: la asistencia NO corrige (w=0)",
              c4.get("assist", {}).get("w") == 0, f"w={c4.get('assist',{}).get('w')}")
        c5 = r["c5"]
        check("5 · goma hacia fuera (bola detrás de la hoja): sin golpe válido",
              c5["hit"] is False, f"events={c5['events']}")
        c6m = sum(x["exitSpeed"] for x in r["c6"]) / len(r["c6"])
        check("6 · canto pega sordo (≈35 % menos que el centro)",
              r["c6c"]["exitSpeed"] > 0 and c6m < r["c6c"]["exitSpeed"] * 0.82,
              f"canto={c6m:.2f} centro={r['c6c']['exitSpeed']:.2f}")
        c7 = r["c7"]
        check("7 · swing flojo: salida floja (≤ 1,0 m/s)", c7["hit"] and c7["exitSpeed"] <= 1.0,
              f"spd={c7['exitSpeed']}")
        check("7 · swing flojo: sin asistencia (w=0)", c7.get("assist", {}).get("w") == 0,
              f"w={c7.get('assist',{}).get('w')}")
        check("7 · swing flojo: no se convierte en saque (sim fallo)",
              c7.get("sim", {}).get("ok") is False)
        c8 = r["c8"]
        check("8 · bola lejos: SIN contacto y bola intacta",
              c8["hit"] is False and abs(c8["exitSpeed"] - 0.224) < 0.06,
              f"hit={c8['hit']} spd={c8['exitSpeed']}")
        check("9 · roza la red: netTouch y no ok", r["c9net"]["netTouch"] is True and r["c9net"]["ok"] is False,
              f"netTouch={r['c9net'].get('netTouch')} ok={r['c9net']['ok']}")
        check("9 · sin bote propio: no ok", r["c9out"]["ok"] is False and r["c9out"]["ownBounce"] is False)
        check("9 · bola muerta (sin botes): no ok", r["c9dead"]["ok"] is False)
        check("9 · referencia del solver: saque legal ok", r["c9ok"]["ok"] is True,
              f"ok={r['c9ok']['ok']} netY={r['c9ok'].get('netY')}")
        print("== LEY DE ASISTENCIA (D) ==")
        check("legal → w=0 (el gesto manda)", r["legal"]["w"] == 0, f"w={r['legal']['w']}")
        check("8° de error → 0 < w < máximo (decae)",
              0 < r["near"]["w"] < 0.35, f"w={r['near']['w']} err={r['near']['err']}")
        check("45° de error → w=0 (jamás se convierte)", r["far"]["w"] == 0,
              f"w={r['far']['w']} err={r['far']['err']}")

        print("== TELEMETRÍA Y TUNE (SRV2 + FEEL1) ==")
        tune = await page.evaluate(
            "(() => { const t = window.__ppDebug.serveTune; return t && t.assistAngle === 0.30"
            " && t.serveMaxSpeed === 8.8 && t.serveMinSpeed === 0 && t.velWindow === 0.045"
            " && t.serveMinExit === 0.65 && t.skin === 0.02; })()")
        check("SERVE_TUNE vivo y completo (SRV2 intacto)", bool(tune))

        print("== AJUSTE 3 · PROMPT B «MENÚ PRINCIPAL ¿SI/No?» ==")
        ask = await page.evaluate("""
          (() => {
            const g = window.__PP_GAME;
            const st = {};
            g.enterHall(); g.exitHall();          // empezar FUERA del hall (en cancha)
            st.inHallAlInicio = g.inHall;
            g.openHallAsk();                       // lo que hace el botón B fuera del hall
            st.paginaPrompt = g.menuPage;
            st.menuAbierto = g.menuOpen;
            g.drawMenu();
            const ids = (g._menuRects || []).map(x => x.id);
            st.tieneSI = ids.includes('hallask_si');
            st.tieneNO = ids.includes('hallask_no');
            st.sinHomehall = !ids.includes('homehall');   // el prompt no es el menú del hub
            const noFn = g.menuAction ? (id) => g.menuAction(id)
              : (id) => { g.menuClick((g._menuRects || []).findIndex(x => x.id === id)); };
            noFn('hallask_no');                    // NO → cerrar y SEGUIR en la escena
            st.trasNO_menuCerrado = !g.menuOpen;
            st.trasNO_fueraDelHall = !g.inHall;    // no te ha movido de la escena
            st.trasNO_paginaLimpia = g.menuPage === 'main';
            g.openHallAsk();                       // reabrir el prompt
            noFn('hallask_si');                    // SI → al HALL con el menú delante
            st.trasSI_enHall = g.inHall;
            st.trasSI_menuAbierto = g.menuOpen;
            st.trasSI_paginaMain = g.menuPage === 'main';
            g.drawMenu();
            st.trasSI_sinPrompt = !(g._menuRects || []).some(x => x.id === 'hallask_si');
            // en el HALL, B vuelve a ser el menú normal (sin prompt): el handler
            // enruta a toggleMenu — lo verificamos por el flag inHall + menuPage
            st.enHallParaB = g.inHall;
            try { localStorage.removeItem('ppxr_dif'); } catch (e) {}
            return st;
          })()
        """)
        check("el prompt abre FUERA del hall", ask.get("paginaPrompt") == "hallask"
              and ask.get("menuAbierto") is True, str({k2: ask.get(k2) for k2 in ('paginaPrompt', 'menuAbierto')}))
        check("el prompt muestra SI y NO (y no es el hub)",
              ask.get("tieneSI") and ask.get("tieneNO") and ask.get("sinHomehall"))
        check("NO → cierra el prompt y SIGUES en la escena",
              ask.get("trasNO_menuCerrado") and ask.get("trasNO_fueraDelHall")
              and ask.get("trasNO_paginaLimpia"))
        check("SI → sales al HALL con el menú principal delante",
              ask.get("trasSI_enHall") and ask.get("trasSI_menuAbierto")
              and ask.get("trasSI_paginaMain") and ask.get("trasSI_sinPrompt"))

        print("== FLUJO DEL HALL (regresión SRV2) ==")
        hall = await page.evaluate("""
          (() => {
            const g = window.__PP_GAME;
            const st = {};
            const click = (id) => {
              const i = (g._menuRects || []).findIndex(x => x.id === id);
              if (i >= 0) g.menuClick(i);
            };
            g.exitHall();                  // salir al cancha para el test
            g.menuOpen = false; g.closeMenu();
            g.menuOpen = true;  g.drawMenu();
            st.homehallEnCancha = (g._menuRects || []).some(x => x.id === 'homehall');
            click('homehall');             st.inHallTrasHome = g.inHall;
            st.menuAbiertoTrasHome = g.menuOpen;
            g.drawMenu();
            st.homehallEnHall = (g._menuRects || []).some(x => x.id === 'homehall');
            g.switchMode('survival');      st.inHallTrasModo = g.inHall;
            st.rigZ = +g.rig.position.z.toFixed(2);
            return st;
          })()
        """)
        check("en cancha el menú muestra ⌂ VOLVER AL HALL", hall.get("homehallEnCancha") is True)
        check("⌂ Home → vuelves al hall", hall.get("inHallTrasHome") is True)
        check("⌂ Home → menú abierto delante (el menú vive en el hall)",
              hall.get("menuAbiertoTrasHome") is True)
        check("en el hall el botón Home NO aparece", hall.get("homehallEnHall") is False)
        check("arrancar un modo → sale a la cancha", hall.get("inHallTrasModo") is False)
        check("rig de vuelta en la cancha (z=0)", hall.get("rigZ") == 0.0, f"z={hall.get('rigZ')}")

        print("== REGRESIÓN ==")
        dims = await page.evaluate(
            "(() => { const d = window.__ppDebug.DIMS;"
            " return { fis: d.physicsRealism, perks: d.paddlePerks, gam: d.trainGamify }; })()")
        check("DIMS FIS1 intactos", dims.get("fis") == 1 and dims.get("perks") == 1
              and dims.get("gam") == 1, str(dims))
        tiers = await page.evaluate(
            "(() => { const t = window.__ppDebug.serveTiers;"
            " return [t.easy.reach, t.medium.reach, t.hard.reach,"
            " t.medium.angleMul, t.easy.assistMul]; })()")
        check("tiers nuevos (reach 6/4.5/2.8 cm + mul)", tiers == [0.06, 0.045, 0.028, 1.0, 1.35],
              str(tiers))
        badge = await page.evaluate("document.querySelector('#verBadge')?.textContent || ''")
        check("badge DOM V3.1.1-FEEL1", badge == "V3.1.1-FEEL1", badge)
        check("0 pageerrors en la sesión", len(errors) == 0, "; ".join(errors[:3]))

        await page.screenshot(path=OUT_PNG)
        await browser.close()

    print("== HUB /descargas (servido por dev) ==")
    hub = fetch("/descargas").decode("utf-8", "replace")
    check("hub sirve la v311 (o aún la v310 mientras no se reempaquete)",
          ("v311-feel1" in hub) or ("v310-srv2" in hub))
    zips = [("crazypp-v311-feel1-COMPLETO.zip", 100_000_000, 112_000_000),
            ("crazypp-v311-feel1-ligera.zip", 10_000_000, 13_000_000),
            ("crazypp-v311-feel1-CLOUDFLARE.zip", 100_000_000, 112_000_000),
            ("crazypp-live-service-SOLO.zip", 4_000, 12_000)]
    have311 = all(z.startswith("crazypp-v311") for z, _, _ in zips[:3])
    if "v311-feel1" in hub:
        for z, lo, hi in zips:
            st, n = head(BASE + "/descargas/" + z)
            check(f"ZIP {z}", st == 200 and lo < n < hi, f"{n:,} B")
    else:
        print("  [..] ZIPs v311 aún no empaquetados (se verifican tras el build)")

    print()
    if FAILS:
        print("RESULTADO: FALLOS ->", FAILS); sys.exit(1)
    print("RESULTADO OK")

asyncio.run(main())
