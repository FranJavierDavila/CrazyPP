#!/usr/bin/env python3
"""QA V3.1.1-SRV3 — sensaciones: ventana tardía del saque + bote honesto +
diálogo B (¿Menú principal? SÍ/NO) + regresión completa del saque realista.

Ejecuta los 9 casos del requisito original contra la FÍSICA REAL (misma
collidePaddle), las 3 novedades SRV3 pedidas por el dueño:
  1 · VENTANA TARDÍA (sólo saque): un contacto muy justo que el subpaso no
      cazaba se recupera re-examinando la estela real (~12 ms); sin ventana
      NO hay contacto; en rally (serveFlight=false) tampoco; muy fuera,
      jamás.
  2 · BOTE HONESTO: con la pala quieta los botes decaen estrictamente hasta
      reposarse en la cara (sin suelo de salida); con la pala en movimiento
      el suelo de 2,3 m/s se conserva; en vuelo de saque manda el suelo
      propio del saque (la bola no reposa).
  3 · DIÁLOGO B: fuera del hall, B abre «¿MENÚ PRINCIPAL? SÍ/NO»; NO cierra
      y sigues en la escena; SÍ sale al hall con el menú abierto. En el hall
      B sigue siendo el menú (no hay diálogo).
y la regresión (versión, DIMS, tiers, hall, hub, 0 pageerrors).
"""
import asyncio, sys, urllib.request
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT_PNG = "/home/z/my-project/download/qa_srv3_portada.png"

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
check("VERSION 3.1.1-SRV3", "const VERSION = '3.1.1-SRV3'" in html)
check("badge estático V3.1.1-SRV3", "V3.1.1-SRV3" in html)
# SRV3 · ventana tardía
check("SERVE_TUNE.lateWindow definido", "lateWindow: 0.012," in html)
check("SERVE_TUNE.lateMargin definido", "lateMargin: 0.012," in html)
check("estela del saque (SERVE_TRAIL)", "const SERVE_TRAIL = [];" in html)
check("re-examinación tardía", "function serveLateRecheck(" in html)
check("ventana sólo en saque (gate 1)",
      "return collidePaddle(ball, pad, k, events, true);" in html)
check("banda del recheck = banda del gate",
      "(pad.extraReach ? SERVE_TUNE.skinServe : 0);" in html)
# SRV3 · bote honesto
check("DIMS.paddleStillSpeed", "paddleStillSpeed: 0.4," in html)
check("DIMS.paddleRestMax", "paddleRestMax: 1.2," in html)
check("lado honesto (regla anti-cara-contraria)",
      "const honestSide = rawApproach * dNow < 0;" in html)
check("contacto restringido en pala quieta",
      "if (stillPad && honestSide && vRelN > -DIMS.paddleRestMax) {" in html)
check("reposo real en la cara",
      "if (stillPad && honestSide && vRelN < 0.01) {" in html)
check("suelo desvanecido con pala quieta",
      "if (padSpd < still) { const f = padSpd / still; exitFloor *= f * f; }" in html)
check("lab de bote expuesto", "window.__PP_BOUNCE_LAB" in html)
# SRV3 · diálogo B
check("B: menú en el hall / diálogo fuera",
      "if (this.inHall) this.toggleMenu();" in html and "else this.toggleBail();" in html)
check("buildBail + diálogo modal", "buildBail()" in html and "bailRects" in html)
check("goHomeHall compartido (⌂ y SÍ)", "case 'homehall':" in html and "this.goHomeHall();" in html)
check("gatillo modal del diálogo", "if (this.bailOpen) {" in html)
check("i18n bail es/en",
      "bail_title: '¿MENÚ PRINCIPAL?'" in html and "bail_title: 'MAIN MENU?'" in html)
# regresión SRV2 (intacta)
check("sin guardián antiguo (cerrar menú sacaba del hall)",
      "if (presenting && this.inHall && !this.menuOpen" not in html)
check("SERVE_TUNE definido", "const SERVE_TUNE = {" in html)
check("asistencia acotada definida", "function applyServeProgressiveAssist(" in html)
check("ley pura compartida", "function serveAssistWeight(" in html)
check("lab QA de saque expuesto", "window.__PP_SERVE_LAB" in html)
check("botón homehall en hub", "btn('homehall'" in html)
check("i18n hall_home_btn es/en", "hall_home_btn: '⌂ VOLVER AL HALL'" in html and "hall_home_btn: '⌂ BACK TO HALL'" in html)
check("DIMS intactos fis=1 perks=1", "physicsRealism: 1," in html and "paddlePerks: 1," in html)

# ---------------------------------------------------------------- funcionales
CASES_JS = """
async () => {
  const L = window.__PP_SERVE_LAB, D = window.__ppDebug;
  if (!L || !D) return { fatal: 'sin ganchos QA (__PP_SERVE_LAB/__ppDebug)' };
  const V3 = window.__PP_VEC3;
  const out = {};
  // CASO 1 · saque correcto (gestos realistas, salida legal, w=0)
  out.c1 = null;
  outer:
  for (const pitch of [12, 16, 20, 24]) {
    for (const pvz of [-1.8, -2.2]) {
      for (const pvy of [0, 0.2]) {
        for (const padY of [1.1, 1.2]) {
          for (const padZ of [0.05, 0.2]) {
            const r = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz, padVelY: pvy,
              padY, padZ, assist: true, tier: 'medium' });
            if (r.hit && r.sim && r.sim.ok && r.exitZ < -1.2) {
              const raw = L({ yawDeg: 180, pitchDeg: pitch, padVelZ: pvz,
                padVelY: pvy, padY, padZ, assist: false });
              out.c1 = { pitch, pvz, pvy, padY, padZ, r,
                rawDelta: Math.abs(raw.exitSpeed - r.exitSpeed) };
              break outer;
            }
          }
        }
      }
    }
  }
  // CASOS 2-8 (idénticos a la QA SRV2)
  out.c2a = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.058 });
  out.c2b = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.012 });
  out.c3 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, ballVelZ: 1.4 });
  out.c4 = L({ yawDeg: 180, pitchDeg: -90, padVelZ: -2.6, assist: true, tier: 'medium' });
  out.c5 = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, assist: true, tier: 'medium' });
  out.c6 = [0, 1, 2].map(() => L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6,
    offX: 0.074, assist: false }));
  out.c6c = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, assist: false });
  out.c7 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -0.30, assist: true, tier: 'medium' });
  out.c8 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, offY: -0.30 });
  // CASO 9 · red / fuera / sin bote
  const S = D.simulateServePath;
  out.c9net = S(new V3(0, 0.86, -0.45), new V3(0, 0.6, -4.6), new V3(), 1);
  out.c9out = S(new V3(0, 0.95, -0.55), new V3(0, -0.05, -6.5), new V3(), 1);
  out.c9dead = S(new V3(0.25, 0.6, -0.55), new V3(0, -2.5, 0.05), new V3(), 1);
  const servePos = new V3(0.05, 1.05, 0.10);
  out.c9ref = D.findServeVelocity(servePos, 1, null);
  out.c9ok = S(servePos, out.c9ref.v, out.c9ref.spin, 1);
  // LEY DE ASISTENCIA (D) viva
  const ref = D.findServeVelocity(servePos, 1, null);
  const bLegal = { pos: servePos.clone(), vel: ref.v.clone(), spin: new V3() };
  out.liveLegal = D.applyServeProgressiveAssist(bLegal, null, D.serveTiers.medium);
  const axis = new V3(1, 0, 0);
  const deg = Math.PI / 180;
  const bFar = { pos: servePos.clone(), vel: ref.v.clone().applyAxisAngle(axis, 45 * deg),
    spin: new V3() };
  out.liveFar = D.applyServeProgressiveAssist(bFar, null, D.serveTiers.medium);

  // ===== SRV3 · 1) VENTANA TARDÍA =====
  const T = D.serveTune;
  const geo = { offX: 0.178, ballVelZ: -1.2, padVelZ: -1.8, dist: 0.05,
    ballVelY: -0.4, padY: 1.05, padZ: -0.55, pitchDeg: 10 };
  out.lateOn = L(geo);                       // con ventana: contacto honesto
  const w0 = T.lateWindow, m0 = T.lateMargin;
  T.lateWindow = 0; T.lateMargin = 0;
  out.lateOff = L(geo);                      // sin ventana: la bola pasa
  T.lateWindow = w0; T.lateMargin = m0;
  out.lateRally = L({ ...geo, serveFlight: false });  // rally: sin ventana
  out.lateFar = L({ ...geo, offX: 0.26 });   // claramente fuera: jamás

  // ===== SRV3 · 2) BOTE HONESTO =====
  out.quieta = window.__PP_BOUNCE_LAB({ seconds: 4 });
  out.rally = window.__PP_BOUNCE_LAB({ seconds: 1.2, padVelY: 1.5 });
  out.serve = window.__PP_BOUNCE_LAB({ seconds: 1.0, serveFlight: true });
  return out;
}
"""

VEC3_SETUP = """
() => { window.__PP_VEC3 = (window.__PP_GAME && window.__PP_GAME.ball &&
  window.__PP_GAME.ball.pos) ? window.__PP_GAME.ball.pos.constructor
  : (window.THREE ? window.THREE.Vector3 : null); }
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
            "!!window.__PP_SERVE_LAB && !!window.__PP_BOUNCE_LAB && !!window.__ppDebug"
            " && !!window.__PP_GAME && !!window.__ppDebug.serveAssistProbe")
        check("labs + __ppDebug + __PP_GAME + serveAssistProbe", bool(hooks))

        await page.evaluate(VEC3_SETUP)

        print("== 9 CASOS DEL REQUISITO (física real) ==")
        r = await page.evaluate(CASES_JS)
        if r.get("fatal"):
            check("ganchos QA", False, r["fatal"]); await browser.close(); return
        c1 = r["c1"]
        check("1 · existe gesto correcto con salida legal", bool(c1),
              (f"pitch={c1['pitch']} pvz={c1['pvz']} padY={c1['padY']} padZ={c1['padZ']}"
               if c1 else "ningún gesto realista de la rejilla produjo saque legal"))
        if c1:
            check("1 · salida hacia la red", c1["r"]["exitZ"] < -1.2,
                  f"exitZ={c1['r']['exitZ']} spd={c1['r']['exitSpeed']}")
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
        check("3 · la salida del cruce va hacia la red",
              r["c3"]["hit"] and r["c3"]["exitZ"] < -1.0, f"exitZ={r['c3']['exitZ']}")
        c4 = r["c4"]
        check("4 · cara al cielo: salida débil (< 1,6 m/s)",
              c4["hit"] and c4["exitSpeed"] < 1.6, f"spd={c4['exitSpeed']}")
        check("4 · cara al cielo: sin saque válido (sim fallo)",
              c4.get("sim", {}).get("ok") is False)
        check("4 · cara al cielo: la asistencia NO corrige (w=0)",
              c4.get("assist", {}).get("w") == 0,
              f"w={c4.get('assist',{}).get('w')} err={c4.get('assist',{}).get('err')}")
        c5 = r["c5"]
        check("5 · goma hacia fuera: sin golpe válido", c5["hit"] is False,
              f"events={c5['events']}")
        c6m = sum(x["exitSpeed"] for x in r["c6"]) / len(r["c6"])
        c6hits = sum(1 for x in r["c6"] if x["hit"])
        check("6 · el canto CONECTA (3/3 golpes)", c6hits == 3, f"hits={c6hits}")
        check("6 · canto pega sordo (≥7 % menos que el centro)",
              r["c6c"]["exitSpeed"] > 0 and c6m < r["c6c"]["exitSpeed"] * 0.93,
              f"canto={c6m:.2f} centro={r['c6c']['exitSpeed']:.2f}")
        c7 = r["c7"]
        check("7 · swing flojo: salida floja (≤ 1,0 m/s)",
              c7["hit"] and c7["exitSpeed"] <= 1.0, f"spd={c7['exitSpeed']}")
        check("7 · swing flojo: sin asistencia (w=0)",
              c7.get("assist", {}).get("w") == 0, f"w={c7.get('assist',{}).get('w')}")
        check("7 · swing flojo: no se convierte en saque (sim fallo)",
              c7.get("sim", {}).get("ok") is False)
        c8 = r["c8"]
        check("8 · bola lejos: SIN contacto (caída libre, intacta)",
              c8["hit"] is False and 0.30 < c8["exitSpeed"] < 0.45,
              f"hit={c8['hit']} spd={c8['exitSpeed']}")
        check("9 · red: netTouch y no ok",
              r["c9net"]["netTouch"] is True and r["c9net"]["ok"] is False,
              f"netTouch={r['c9net'].get('netTouch')} ok={r['c9net']['ok']}")
        check("9 · sin bote propio: no ok",
              r["c9out"]["ok"] is False and r["c9out"]["ownBounce"] is False)
        check("9 · bola muerta (sin botes): no ok", r["c9dead"]["ok"] is False)
        check("9 · referencia del solver: saque legal ok", r["c9ok"]["ok"] is True,
              f"ok={r['c9ok']['ok']} netY={r['c9ok'].get('netY')}")

        print("== SRV3 · 1) VENTANA TARDÍA (sólo saque) ==")
        lo, lff, lr, lfar = r["lateOn"], r["lateOff"], r["lateRally"], r["lateFar"]
        check("contacto MUY justo recuperado (con ventana)", lo["hit"] is True,
              f"spd={lo['exitSpeed']} ev={lo['events'][:3]}")
        check("sin ventana el mismo gesto NO contacta", lff["hit"] is False,
              f"ev={lff['events'][:3]}")
        check("en RALLY la ventana no existe (serveFlight=false)",
              lr["hit"] is False, f"ev={lr['events'][:3]}")
        check("claramente fuera del alcance: jamás contacto",
              lfar["hit"] is False, f"ev={lfar['events'][:3]}")
        tune_w = await page.evaluate(
            "(() => { const t = window.__ppDebug.serveTune;"
            " return { w: t.lateWindow, m: t.lateMargin }; })()")
        check("SERVE_TUNE restaurado tras la prueba",
              tune_w["w"] == 0.012 and tune_w["m"] == 0.012, str(tune_w))

        print("== SRV3 · 2) BOTE HONESTO ==")
        q = r["quieta"]
        imp = q["impactSpeeds"]
        decreciente = all(imp[i + 1] < imp[i] for i in range(len(imp) - 1))
        check("pala quieta: cadena de botes (≥3)", len(imp) >= 3, str(imp[:8]))
        check("pala quieta: estrictamente DECRECIENTE", decreciente, str(imp[:8]))
        check("pala quieta: sin suelo (todos < 2,3 m/s)",
              all(s < 2.3 for s in imp), f"max={max(imp) if imp else 0}")
        check("pala quieta: reposa en la cara", q["resting"] is True and q["faceDist"] < 0.03,
              f"final={q['finalSpeed']} faceDist={q['faceDist']} ballY={q['ballY']}")
        rl = r["rally"]
        check("pala en movimiento: suelo rally intacto (≥2,2)",
              len(rl["impactSpeeds"]) > 0 and rl["impactSpeeds"][0] >= 2.2,
              f"impacts={rl['impactSpeeds'][:3]}")
        sv = r["serve"]
        check("vuelo de saque: el suelo propio del saque lo mantiene vivo",
              len(sv["impactSpeeds"]) >= 2 and sv["resting"] is False,
              f"impacts={sv['impactSpeeds'][:3]} resting={sv['resting']}")

        print("== LEY DE ASISTENCIA (D) — probe determinista ==")
        probes = await page.evaluate(
            "(() => { const P = window.__ppDebug.serveAssistProbe;"
            " return { p0: P(0), p8: P(8), p45: P(45),"
            " easy20: P(20, 'easy'), hard20: P(20, 'hard') }; })()")
        check("error 0 → mezcla máxima (0,35)", abs(probes["p0"]["w"] - 0.35) < 1e-9,
              f"w={probes['p0']['w']}")
        check("8° → mezcla parcial que decae (0 < w < 0,35)",
              0 < probes["p8"]["w"] < 0.35, f"w={probes['p8']['w']:.4f}")
        check("45° → w=0 (jamás se convierte)", probes["p45"]["w"] == 0,
              f"w={probes['p45']['w']}")
        check("escala por dificultad: fácil perdona 20°, duro no",
              probes["easy20"]["w"] > 0 and probes["hard20"]["w"] == 0,
              f"easy={probes['easy20']['w']:.3f} hard={probes['hard20']['w']:.3f}")
        print("== LEY DE ASISTENCIA (D) — viva ==")
        check("saque YA legal → w=0 (el gesto manda)",
              r["liveLegal"]["w"] == 0 and r["liveLegal"]["sim"]["ok"] is True,
              f"w={r['liveLegal']['w']}")
        check("45° en vivo → w=0 (sin corrección oculta)",
              r["liveFar"]["w"] == 0, f"w={r['liveFar']['w']} err={r['liveFar']['err']}")

        print("== TELEMETRÍA Y TUNE ==")
        tune = await page.evaluate(
            "(() => { const t = window.__ppDebug.serveTune; return t && t.assistAngle === 0.30"
            " && t.serveMaxSpeed === 8.8 && t.serveMinSpeed === 0 && t.velWindow === 0.045; })()")
        check("SERVE_TUNE vivo y completo", bool(tune))

        print("== FLUJO DEL HALL + DIÁLOGO B (2D, estado real) ==")
        hall = await page.evaluate("""
          (() => {
            const g = window.__PP_GAME;
            const st = {};
            g.enterHall();                 st.inHallOnEnter = g.inHall;
            g.menuOpen = false; g.closeMenu();  st.inHallTrasCerrarMenu = g.inHall;
            // EN EL HALL: B no abre el diálogo (es el menú)
            g.toggleBail();                st.bailEnHall = g.bailOpen === true;
            // a la cancha: arrancar un modo
            g.switchMode('survival');      st.inHallTrasModo = g.inHall;
            st.rigZ = +g.rig.position.z.toFixed(2);
            // EN CANCHA: B abre el diálogo «¿MENÚ PRINCIPAL? SÍ/NO»
            g.toggleBail();                st.bailAbierto = g.bailOpen === true;
            st.menuCerradoConBail = g.menuOpen === false;
            st.rectsBail = (g.bailRects || []).map(r => r.id);
            // NO → cerrar el diálogo y SEGUIR en la escena
            const iNo = g.bailRects.findIndex(r => r.id === 'bailno');
            g.bailClick(iNo);
            st.bailCerradoConNO = g.bailOpen === false;
            st.siguesEnCanchaConNO = g.inHall === false;
            // SÍ → salir al hall con el menú principal abierto
            g.toggleBail();
            const iYes = g.bailRects.findIndex(r => r.id === 'bailyes');
            g.bailClick(iYes);
            st.vuelvesAlHallConSI = g.inHall === true;
            st.menuAbiertoConSI = g.menuOpen === true;
            st.bailCerradoConSI = g.bailOpen === false;
            // y en cancha el menú sigue ofreciendo ⌂ VOLVER AL HALL
            // (el modo activo es 'survival': cambiar a 'match' SÍ sale del hall)
            g.switchMode('match');
            g.menuOpen = true; g.drawMenu();
            st.homehallEnCancha = (g._menuRects || []).some(x => x.id === 'homehall')
              && g.inHall === false;
            try { localStorage.removeItem('ppxr_dif'); } catch (e) {}
            return st;
          })()
        """)
        check("entrar en VR → nace en el hall", hall.get("inHallOnEnter") is True)
        check("cerrar el menú → SIGUES en el hall", hall.get("inHallTrasCerrarMenu") is True)
        check("en el HALL: B NO abre el diálogo", hall.get("bailEnHall") is False)
        check("arrancar un modo → sales a la cancha", hall.get("inHallTrasModo") is False)
        check("rig de vuelta en la cancha (z=0)", hall.get("rigZ") == 0.0,
              f"z={hall.get('rigZ')}")
        check("en cancha: B abre «¿MENÚ PRINCIPAL?»", hall.get("bailAbierto") is True)
        check("el diálogo sustituye al menú fuera del hall",
              hall.get("menuCerradoConBail") is True)
        check("botones SÍ/NO presentes", hall.get("rectsBail") == ["bailyes", "bailno"],
              str(hall.get("rectsBail")))
        check("NO → diálogo cerrado", hall.get("bailCerradoConNO") is True)
        check("NO → SIGUES en la escena (cancha)", hall.get("siguesEnCanchaConNO") is True)
        check("SÍ → vuelves al HALL", hall.get("vuelvesAlHallConSI") is True)
        check("SÍ → menú principal abierto en pantalla", hall.get("menuAbiertoConSI") is True)
        check("SÍ → diálogo recogido", hall.get("bailCerradoConSI") is True)
        check("en cancha el menú mantiene ⌂ VOLVER AL HALL",
              hall.get("homehallEnCancha") is True)

        print("== REGRESIÓN ==")
        dims = await page.evaluate(
            "(() => { const d = window.__ppDebug.DIMS;"
            " return { fis: d.physicsRealism, perks: d.paddlePerks, gam: d.trainGamify,"
            " still: d.paddleStillSpeed, restMax: d.paddleRestMax }; })()")
        check("DIMS FIS1 intactos + nuevos SRV3",
              dims.get("fis") == 1 and dims.get("perks") == 1 and dims.get("gam") == 1
              and dims.get("still") == 0.4 and dims.get("restMax") == 1.2, str(dims))
        tiers = await page.evaluate(
            "(() => { const t = window.__ppDebug.serveTiers;"
            " return [t.easy.reach, t.medium.reach, t.hard.reach,"
            " t.medium.angleMul, t.easy.assistMul]; })()")
        check("tiers nuevos (reach 6/4.5/2.8 cm + mul)",
              tiers == [0.06, 0.045, 0.028, 1.0, 1.35], str(tiers))
        badge = await page.evaluate("document.querySelector('#verBadge')?.textContent || ''")
        check("badge DOM V3.1.1-SRV3", badge == "V3.1.1-SRV3", badge)
        check("0 pageerrors en la sesión", len(errors) == 0, "; ".join(errors[:3]))

        await page.screenshot(path=OUT_PNG)
        await browser.close()

    print("== HUB /descargas (servido por dev) ==")
    hub = fetch("/descargas").decode("utf-8", "replace")
    check("hub sirve la V3.1.1-SRV3 (v311-srv3)", "v311-srv3" in hub)
    check("hub sin residuos v310", "v310-srv2" not in hub)
    for z, lo, hi in [("crazypp-v311-srv3-COMPLETO.zip", 100_000_000, 112_000_000),
                      ("crazypp-v311-srv3-ligera.zip", 10_000_000, 13_000_000),
                      ("crazypp-v311-srv3-CLOUDFLARE.zip", 100_000_000, 112_000_000),
                      ("crazypp-live-service-SOLO.zip", 4_000, 12_000)]:
        st, n = head(BASE + "/descargas/" + z)
        check(f"ZIP {z}", st == 200 and lo < n < hi, f"{n:,} B")

    print()
    if FAILS:
        print("RESULTADO: FALLOS ->", FAILS); sys.exit(1)
    print("RESULTADO OK")

asyncio.run(main())
