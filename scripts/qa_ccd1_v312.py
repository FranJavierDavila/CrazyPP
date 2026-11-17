#!/usr/bin/env python3
"""QA V3.1.2-CCD1 — precisión de contacto por CCD SDF (requisito del dueño).

0) CCD POR SDF: barrido del segmento de bola en el espacio LOCAL de la pala
   (poses P0→P1 del frame XR) contra el SDF exacto del disco con grosor.
   Criterios de aceptación del dueño (spec J) vía __PP_CCD_LAB:
   - lluvia 10 000 offsets a 40 m/s contra pala quieta: 100 % golpes, 0 túneles
   - entradas oblicuas 25°: 100 % · referencia de fuerza bruta: TOI < 0,05 ms
     y contacto < 0,1 mm · pala a 20 m/s · cruce en un frame de 33 ms ·
     rotación 35 rad/s (y lenta: normal coherente) · canto sin túneles ni
     dobles golpes · coherencia energética · coste por barrido/frame.
1) REGRESIÓN FEEL1: gracia del saque (12,5 ms), botes en decaimiento, suelo
   de golpes — __PP_FEEL_LAB.
2) REGRESIÓN SRV2: los 9 casos del saque realista, ley de asistencia D,
   flujo del prompt B, flujo del hall, DIMS/tiers y 0 pageerrors.
"""
import asyncio, sys, urllib.request
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT_PNG = "/home/z/my-project/download/qa_ccd1_portada.png"

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
check("VERSION 3.1.2-CCD1", "const VERSION = '3.1.2-CCD1'" in html)
check("badge estático V3.1.2-CCD1", "V3.1.2-CCD1" in html)
# --- CCD por SDF (núcleo del ajuste) ---
for anchor in ["const CCD_TUNE = {", "bladeHalfT: 0.004,", "function sdfBlade(",
               "function sweepBallVsBlade(", "function sweepBallVsCapsuleY(",
               "function bladeNormalLocal(", "function collidePaddleSweep("]:
    check("módulo CCD: " + anchor.split("(")[0].replace("const ", "").replace("function ", ""),
          anchor in html)
check("stepPhysics barre por subpaso (P0→P1 alineado)",
      "collidePaddleSweep(ball, pad, i / n, (i + 1) / n, events)" in html)
check("testPaddleContact (online) barre el frame completo",
      "collidePaddleSweep(ball, pad, 0, 1, events)" in html)
check("envoltorio compatible collidePaddle(k)", "return collidePaddleSweep(ball, pad, k, k, events);" in html)
check("dtFrame limitado a 1/30 s (spec A)", "Math.min(now - this.lastTime, 1 / 30)" in html)
check("updateTargetFrameRate(120) en sessionstart", "updateTargetFrameRate" in html)
check("normal de cara firmada por POSICIÓN (spec F)", "if (lhz < 0) tmpN.negate();" in html)
check("rim lateral usa el gradiente del SDF", "bladeNormalLocal(lx, dyy, lhz, Rb, hT, ccdNL);" in html)
check("separación tras el golpe: ya se separan no golpean (vRelN ≥ 0)",
      "if (vRelN >= 0) return false;   // ya se separan: no es un golpe (spec F)" in html)
check("gracia FEEL1 preservada (armado con radio de bola)",
      "rB + reach0 + SERVE_TUNE.lateInPlane" in html)
check("gracia inflada durante el barrido", "(grace ? SERVE_TUNE.lateInPlane : 0)" in html)
check("lab CCD expuesto", "window.__PP_CCD_LAB" in html)
check("ccdTune vivo en __ppDebug", "ccdTune: CCD_TUNE" in html)
# --- regresión FEEL1 ---
for anchor in ["lateMs: 14,", "lateInPlane: 0.02,", "lateSkin: 0.012,"]:
    check("SERVE_TUNE gracia: " + anchor.split(":")[0], anchor in html)
check("grace decae con la física (stepPhysics)", "if (ball.__serveGrace > 0) ball.__serveGrace -= h;" in html)
check("suelo escalado por velocidad de pala", "exitFloor = DIMS.minExitSpeed * floorK;" in html)
check("palancas del suelo (exitFloorFrom/To)", "exitFloorFrom: 0.15," in html and "exitFloorTo: 1.0," in html)
check("contacto de reposo ignora cooldown (pala quieta)",
      "pad.vel.lengthSq() <= SERVE_TUNE.restPadSpeed * SERVE_TUNE.restPadSpeed;" in html)
check("evento gated por impacto (restEventMin) + saque siempre emite",
      "if (pad.serveFlight || Math.abs(vRelN) >= SERVE_TUNE.restEventMin) {" in html)
# --- regresión FEEL1 ajuste 3: prompt B ---
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
  // v3.1.2: Math.random DETERMINISTA también en la búsqueda del gesto (el
  // bamboleo del canto sortea dispersión: sin semilla, la pasada con
  // asistencia y la cruda difieren y el "gesto preservado" sería flaky).
  const __rnd = Math.random;
  Math.random = () => 0.5;
  try {
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
  } finally { Math.random = __rnd; }
  out.c2a = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.06 });
  out.c2b = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.012 });
  out.c3 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, ballVelZ: 1.4 });
  out.c4 = L({ yawDeg: 180, pitchDeg: -90, padVelZ: -2.6, assist: true, tier: 'medium' });
  out.c5 = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, assist: true, tier: 'medium',
    dist: -0.06 });
  out.c6 = [0, 1, 2].map(() => L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6,
    offX: 0.168, assist: false }));
  out.c6c = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, assist: false });
  out.c7 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -0.30, assist: true, tier: 'medium' });
  out.c8 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, offY: -0.30 });
  const S = D.simulateServePath;
  Math.random = () => 0.5;
  try {
  out.c9net = S(new V3(0, 1.02, -0.5), new V3(0, 1.16, -4.0), new V3(), 1);
  out.c9out = S(new V3(0, 1.02, -0.5), new V3(0, 0.5, -7.0), new V3(), 1);
  out.c9dead = S(new V3(0.25, 0.6, -0.55), new V3(0, -2.5, 0.05), new V3(), 1);
  out.c9ref = D.findServeVelocity(new V3(0.0, 1.15, 0.0), 1, null);
  out.c9ok = S(new V3(0.0, 1.15, 0.0), out.c9ref.v, out.c9ref.spin, 1);
  const pos = new V3(0, 1.15, 0.0);
  const ref = D.findServeVelocity(pos, 1, null);
  const axis = new V3(1, 0, 0);
  const deg = THREE_DEG;
  const mk = (rotDeg) => {
    const v = ref.v.clone().applyAxisAngle(axis, rotDeg * deg);
    const b = { pos: pos.clone(), vel: v, spin: new V3() };
    return D.applyServeProgressiveAssist(b, null, D.serveTiers.medium);
  };
  out.legal = mk(0);
  out.near = mk(8);
  out.far = mk(45);
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
  out.strokeFloor = L({ mode: 'stroke', padVy: 1.5, dropH: 0.02 });
  out.strokeSlow = L({ mode: 'stroke', padVy: 0.4, dropH: 0.02 });
  out.graceKnobs = { lateMs: tune.lateMs, lateInPlane: tune.lateInPlane,
    lateSkin: tune.lateSkin, exitFloorFrom: tune.exitFloorFrom,
    exitFloorTo: tune.exitFloorTo, restPadSpeed: tune.restPadSpeed,
    restEventMin: tune.restEventMin };
  return out;
}
"""

CCD_JS = """
() => {
  const L = window.__PP_CCD_LAB, D = window.__ppDebug;
  if (!L || !D) return { fatal: 'sin __PP_CCD_LAB' };
  const out = {};
  out.rain = L({ mode: 'rain' });
  out.rainAng = L({ mode: 'rainAngled', n: 4000 });
  out.ref = L({ mode: 'ref', n: 300 });
  out.fastPad = L({ mode: 'fastPad' });
  out.frameDrop = L({ mode: 'frameDrop' });
  out.spinBlade = L({ mode: 'spinBlade' });
  out.spinSlow = L({ mode: 'spinBlade', omega: 6 });
  out.edge = L({ mode: 'edge' });
  out.energy = L({ mode: 'energy' });
  out.perf = L({ mode: 'perf' });
  out.knobs = { bladeHalfT: D.ccdTune.bladeHalfT, eps: D.ccdTune.eps,
    maxIter: D.ccdTune.maxIter };
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
            "!!window.__PP_SERVE_LAB && !!window.__PP_FEEL_LAB && !!window.__PP_CCD_LAB"
            " && !!window.__ppDebug && !!window.__PP_GAME")
        check("__PP_SERVE_LAB + __PP_FEEL_LAB + __PP_CCD_LAB + __ppDebug + __PP_GAME", bool(hooks))
        await page.evaluate(VEC3_SETUP)

        print("== CCD POR SDF · CRITERIOS DE ACEPTACIÓN ==")
        c = await page.evaluate(CCD_JS)
        if c.get("fatal"):
            check("lab CCD", False, c["fatal"]); await browser.close(); return
        check("lluvia 10 000 offsets a 40 m/s: 100 % golpes",
              c["rain"]["hits"] == c["rain"]["n"] and c["rain"]["hitRate"] == 1,
              f"hits={c['rain']['hits']}/{c['rain']['n']}")
        check("lluvia: 0 túneles (bola nunca cruza sin contar)",
              c["rain"]["tunnels"] == 0, f"tunnels={c['rain']['tunnels']}")
        check("lluvia oblicua 25°: 100 % golpes, 0 túneles",
              c["rainAng"]["hitRate"] == 1 and c["rainAng"]["tunnels"] == 0,
              f"hits={c['rainAng']['hits']}/{c['rainAng']['n']}")
        check("referencia bruta: error TOI < 0,05 ms",
              c["ref"]["maxDtMs"] < 0.05, f"maxDtMs={c['ref']['maxDtMs']}")
        check("referencia bruta: error de contacto < 0,1 mm",
              c["ref"]["maxPosMm"] < 0.1, f"maxPosMm={c['ref']['maxPosMm']}")
        check("pala a 20 m/s contra bola quieta: golpe correcto",
              c["fastPad"]["hit"] is True and c["fastPad"]["exitSpeed"] > 1,
              f"exit={c['fastPad']['exitSpeed']}")
        check("cruce de pala y bola en UN frame de 33 ms: golpe",
              c["frameDrop"]["hit"] is True, f"dtMs={c['frameDrop']['dtMs']}")
        check("pala rotando a 35 rad/s: golpe con salida sana",
              c["spinBlade"]["hit"] is True and c["spinBlade"]["ndot"] > 0.3,
              f"ndot={c['spinBlade']['ndot']} exit={c['spinBlade']['exitSpeed']}")
        check("rotación lenta (6 rad/s): normal coherente con la cara",
              c["spinSlow"]["hit"] is True and c["spinSlow"]["ndot"] > 0.8,
              f"ndot={c['spinSlow']['ndot']}")
        check("canto/esquina 98-104 %: 100 % golpes",
              c["edge"]["hits"] == c["edge"]["n"], f"hits={c['edge']['hits']}/{c['edge']['n']}")
        check("canto: 0 túneles y 0 dobles golpes",
              c["edge"]["tunnels"] == 0 and c["edge"]["doubles"] == 0,
              f"tunnels={c['edge']['tunnels']} doubles={c['edge']['doubles']}")
        check("coherencia energética (salida ≤ (1+e)·entrada + cuerpo)",
              c["energy"]["ok"] is True, f"out={c['energy']['out']} cap={c['energy']['cap']}")
        check("coste: barrido < 5 µs y frame de física < 100 µs",
              c["perf"]["sweepUs"] < 5 and c["perf"]["frameUs"] < 100,
              f"sweep={c['perf']['sweepUs']} µs · frame={c['perf']['frameUs']} µs")
        check("knobs CCD vivos (halfT 4 mm = el visor, eps 0,01 mm, 32 iter)",
              c["knobs"]["bladeHalfT"] == 0.004 and c["knobs"]["eps"] == 1e-5
              and c["knobs"]["maxIter"] == 32, str(c["knobs"]))

        print("== REGRESIÓN FEEL1 · GRACIA Y REBOTE REAL ==")
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
        d = f["decay"]
        b = d["bounces"]
        check("los botes DECAEN (≥5 botes reales)", len(b) >= 5, str(b))
        check("decaimiento monótono (sin suelo de rebote)",
              all(v < b[i - 1] for i, v in enumerate(b) if i > 0), str(b))
        check("la bola NO atraviesa la hoja", d["fellThrough"] is False, f"gap={d['gap']}")
        check("reposo sobre la hoja (gap ≈ contacto)", 0.015 < d["gap"] < 0.035, f"gap={d['gap']}")
        check("reposo en calma (vel < 0,05 m/s)", d["restSpeed"] < 0.05, f"v={d['restSpeed']}")
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
            check("1 · salida hacia la red", c1["r"]["exitZ"] < -1.2, f"exitZ={c1['r']['exitZ']}")
            check("1 · el sistema NO toca el saque legal (w=0)",
                  c1["r"]["assist"]["w"] == 0, f"w={c1['r']['assist']['w']} err={c1['r']['assist']['err']}")
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

        print("== TELEMETRÍA Y TUNE (SRV2 + FEEL1 + CCD1) ==")
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
            g.enterHall(); g.exitHall();
            st.inHallAlInicio = g.inHall;
            g.openHallAsk();
            st.paginaPrompt = g.menuPage;
            st.menuAbierto = g.menuOpen;
            g.drawMenu();
            const ids = (g._menuRects || []).map(x => x.id);
            st.tieneSI = ids.includes('hallask_si');
            st.tieneNO = ids.includes('hallask_no');
            st.sinHomehall = !ids.includes('homehall');
            const noFn = g.menuAction ? (id) => g.menuAction(id)
              : (id) => { g.menuClick((g._menuRects || []).findIndex(x => x.id === id)); };
            noFn('hallask_no');
            st.trasNO_menuCerrado = !g.menuOpen;
            st.trasNO_fueraDelHall = !g.inHall;
            st.trasNO_paginaLimpia = g.menuPage === 'main';
            g.openHallAsk();
            noFn('hallask_si');
            st.trasSI_enHall = g.inHall;
            st.trasSI_menuAbierto = g.menuOpen;
            st.trasSI_paginaMain = g.menuPage === 'main';
            g.drawMenu();
            st.trasSI_sinPrompt = !(g._menuRects || []).some(x => x.id === 'hallask_si');
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
            g.exitHall();
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
        check("badge DOM V3.1.2-CCD1", badge == "V3.1.2-CCD1", badge)
        check("0 pageerrors en la sesión", len(errors) == 0, "; ".join(errors[:3]))

        await page.screenshot(path=OUT_PNG)
        await browser.close()

    print("== HUB /descargas (servido por dev) ==")
    hub = fetch("/descargas").decode("utf-8", "replace")
    check("hub sirve la v312 (o aún la v311 mientras no se reempaquete)",
          ("v312-ccd1" in hub) or ("v311-feel1" in hub))
    zips = [("crazypp-v312-ccd1-COMPLETO.zip", 100_000_000, 112_000_000),
            ("crazypp-v312-ccd1-ligera.zip", 10_000_000, 13_000_000),
            ("crazypp-v312-ccd1-CLOUDFLARE.zip", 100_000_000, 112_000_000),
            ("crazypp-live-service-SOLO.zip", 4_000, 12_000)]
    if "v312-ccd1" in hub:
        for z, lo, hi in zips:
            st, n = head(BASE + "/descargas/" + z)
            check(f"ZIP {z}", st == 200 and lo < n < hi, f"{n:,} B")
    else:
        print("  [..] ZIPs v312 aún no empaquetados (se verifican tras el build)")

    print()
    if FAILS:
        print("RESULTADO: FALLOS ->", FAILS); sys.exit(1)
    print("RESULTADO OK")

asyncio.run(main())
