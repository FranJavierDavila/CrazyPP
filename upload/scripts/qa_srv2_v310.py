#!/usr/bin/env python3
"""QA V3.1.0-SRV2 — saque VR realista con asistencia limitada + hall como hub.

Ejecuta los 9 casos mínimos del requisito del dueño contra la FÍSICA REAL del
juego (window.__PP_SERVE_LAB usa la misma collidePaddle + asistencia acotada),
verifica el flujo del hall (cerrar menú permanece; Home devuelve al hall; los
arranques de modo sacan del hall) y la regresión básica (versión, DIMS, 0
pageerrors, hub de descargas con los 4 paquetes v310).

v2 de la QA (misma sesión que el fix del lab): el laboratorio reproduce el
frame REAL (base previa sincronizada + pala barrida + bola delante del centro
de la hoja) y la rejilla del caso 1 usa gestos REALISTAS de saque (cara
ligeramente cerrada, contacto tras la línea de fondo) — los gestos de cara
abierta sobre la mesa no pueden ser saques legates NI en el juego NI en la
vida real. La ley de asistencia (D) se prueba con el probe determinista
(__ppDebug.serveAssistProbe) + 2 pruebas vivas (legal intocable, 45° jamás).
"""
import asyncio, sys, urllib.request
from playwright.async_api import async_playwright

BASE = "http://localhost:3000"
OUT_PNG = "/home/z/my-project/download/qa_srv2_portada.png"

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
check("VERSION 3.1.0-SRV2", "const VERSION = '3.1.0-SRV2'" in html)
check("badge estático V3.1.0-SRV2", "V3.1.0-SRV2" in html)
check("sin guardián antiguo (cerrar menú sacaba del hall)",
      "if (presenting && this.inHall && !this.menuOpen" not in html)
for anchor in ["this.exitHall();          // v3.1.0-SRV2: arrancar un modo saca del hall",
               "g.exitHall();             // v3.1.0-SRV2: un campeonato se juea en la cancha",
               "game.exitHall();                          // v3.1.0-SRV2: un modo se juea en la cancha",
               "game.exitHall();                        // v3.1.0-SRV2: el ajuste vive en la cancha",
               "this.exitHall();          // v3.1.0-SRV2: la sesión online se juea en la cancha"]:
    check("exitHall en arranque: " + anchor.split("//")[1].strip()[:34], anchor in html)
check("cascada antigua fuera (tier.lerp1)", "tier.lerp1" not in html)
check("suelo de saque 3.2 fuera", "if (this.ball.vel.length() < 3.2) this.ball.vel.setLength(3.2)" not in html)
check("SERVE_TUNE definido", "const SERVE_TUNE = {" in html)
check("asistencia acotada definida", "function applyServeProgressiveAssist(" in html)
check("ley pura compartida", "function serveAssistWeight(" in html)
check("lab QA expuesto", "window.__PP_SERVE_LAB" in html)
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
  // CASO 1 · saque correcto: gestos REALISTAS (cara ligeramente cerrada,
  // contacto tras la línea de fondo, swing hacia la red) cuya salida física
  // pura es ya un saque legal; se verifica que el sistema NO lo toca (w=0)
  // y que la salida es idéntica sin asistencia.
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
  // CASO 2 · pequeñas imprecisiones de timing: contacto algo tarde (5,8 cm ≈
  // 22 ms con el swing de referencia, dentro de la tolerancia 6,2 cm evaluada
  // en subpasos como el juego real) y casi en el plano (1,2 cm)
  out.c2a = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.058 });
  out.c2b = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, dist: 0.012 });
  // CASO 3 · golpe antes/después del instante ideal: la bola viene HACIA la
  // pala (cruza el plano dentro del frame) — el CCD debe resolver el contacto
  // y la salida debe marchar hacia la red
  out.c3 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, ballVelZ: 1.4 });
  // CASO 4 · pala PARALELA a la mesa (cara al cielo): la bola cae sobre la
  // cara — salida débil (suelo de roce 0,65 + arrastre), NUNCA un saque
  out.c4 = L({ yawDeg: 180, pitchDeg: -90, padVelZ: -2.6, assist: true, tier: 'medium' });
  // CASO 5 · pala orientada HACIA FUERA de la mesa (goma a la izquierda):
  // la bola pasa paralela al plano — sin contacto útil
  out.c5 = L({ yawDeg: 270, pitchDeg: 0, padVelZ: -2.6, assist: true, tier: 'medium' });
  // CASO 6 · contacto con el CANTO (bola a 7,4 cm del centro, hoja 8 cm):
  // golpe sordo y disperso frente al centro
  out.c6 = [0, 1, 2].map(() => L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6,
    offX: 0.074, assist: false }));
  out.c6c = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, assist: false });
  // CASO 7 · lanzamiento sin velocidad suficiente (swing flojo): roce flojo,
  // sin asistencia (w=0) → el árbitro lo juzga falta
  out.c7 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -0.30, assist: true, tier: 'medium' });
  // CASO 8 · golpe SIN contacto real: la bola pasa 30 cm fuera del plano de
  // la hoja — nada ocurre
  out.c8 = L({ yawDeg: 180, pitchDeg: -20, padVelZ: -2.6, offY: -0.30 });
  // CASO 9 · red / fuera / sin bote: el simulador (misma física) los caza
  const S = D.simulateServePath;
  out.c9net = S(new V3(0, 0.86, -0.45), new V3(0, 0.6, -4.6), new V3(), 1);
  out.c9out = S(new V3(0, 0.95, -0.55), new V3(0, -0.05, -6.5), new V3(), 1);
  out.c9dead = S(new V3(0.25, 0.6, -0.55), new V3(0, -2.5, 0.05), new V3(), 1);
  // referencia legal del solver (misma física) desde un punto de contacto
  // REALISTA (tras la línea de fondo) + saque legal ok
  const servePos = new V3(0.05, 1.05, 0.10);
  out.c9ref = D.findServeVelocity(servePos, 1, null);
  out.c9ok = S(servePos, out.c9ref.v, out.c9ref.spin, 1);
  // LEY DE ASISTENCIA (D) — viva: un saque YA legal no se toca; a 45° jamás
  const pos = servePos;
  const ref = D.findServeVelocity(pos, 1, null);
  const bLegal = { pos: pos.clone(), vel: ref.v.clone(), spin: new V3() };
  out.liveLegal = D.applyServeProgressiveAssist(bLegal, null, D.serveTiers.medium);
  const axis = new V3(1, 0, 0);
  const deg = Math.PI / 180;
  const bFar = { pos: pos.clone(), vel: ref.v.clone().applyAxisAngle(axis, 45 * deg),
    spin: new V3() };
  out.liveFar = D.applyServeProgressiveAssist(bFar, null, D.serveTiers.medium);
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
            "!!window.__PP_SERVE_LAB && !!window.__ppDebug && !!window.__PP_GAME"
            " && !!window.__ppDebug.serveAssistProbe")
        check("__PP_SERVE_LAB + __ppDebug + __PP_GAME + serveAssistProbe", bool(hooks))

        await page.evaluate(VEC3_SETUP)

        print("== 9 CASOS DEL REQUISITO (física real) ==")
        r = await page.evaluate(CASES_JS)
        if r.get("fatal"):
            check("ganchos QA", False, r["fatal"]); await browser.close(); return
        c1 = r["c1"]
        check("1 · existe gesto correcto con salida legal", bool(c1),
              (f"pitch={c1['pitch']} pvz={c1['pvz']} pvy={c1['pvy']} "
               f"padY={c1['padY']} padZ={c1['padZ']}" if c1
               else "ningún gesto realista de la rejilla produjo saque legal"))
        if c1:
            check("1 · salida hacia la red", c1["r"]["exitZ"] < -1.2,
                  f"exitZ={c1['r']['exitZ']} spd={c1['r']['exitSpeed']}")
            check("1 · el sistema NO toca el saque legal (w=0)",
                  c1["r"]["assist"]["w"] == 0,
                  f"w={c1['r']['assist']['w']} err={c1['r']['assist']['err']}")
            check("1 · gesto preservado (idéntico sin asistencia)",
                  c1["rawDelta"] < 0.01,
                  f"Δspd={c1['rawDelta']:.4f}")
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
              c4.get("assist", {}).get("w") == 0, f"w={c4.get('assist',{}).get('w')} err={c4.get('assist',{}).get('err')}")
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
        check("7 · swing flojo: salida floja (≤ 1,0 m/s)", c7["hit"] and c7["exitSpeed"] <= 1.0,
              f"spd={c7['exitSpeed']}")
        check("7 · swing flojo: sin asistencia (w=0)", c7.get("assist", {}).get("w") == 0,
              f"w={c7.get('assist',{}).get('w')}")
        check("7 · swing flojo: no se convierte en saque (sim fallo)",
              c7.get("sim", {}).get("ok") is False)
        c8 = r["c8"]
        check("8 · bola lejos: SIN contacto (caída libre por gravedad, intacta)",
              c8["hit"] is False and 0.30 < c8["exitSpeed"] < 0.45,
              f"hit={c8['hit']} spd={c8['exitSpeed']} (0,351 = caída libre 1 frame)")
        check("9 · red: netTouch y no ok", r["c9net"]["netTouch"] is True and r["c9net"]["ok"] is False,
              f"netTouch={r['c9net'].get('netTouch')} ok={r['c9net']['ok']}")
        check("9 · sin bote propio: no ok", r["c9out"]["ok"] is False and r["c9out"]["ownBounce"] is False)
        check("9 · bola muerta (sin botes): no ok", r["c9dead"]["ok"] is False)
        check("9 · referencia del solver: saque legal ok", r["c9ok"]["ok"] is True,
              f"ok={r['c9ok']['ok']} netY={r['c9ok'].get('netY')}")
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

        print("== FLUJO DEL HALL (2D, estado real del juego) ==")
        hall = await page.evaluate("""
          (() => {
            const g = window.__PP_GAME;
            const st = {};
            g.enterHall();                 st.inHallOnEnter = g.inHall;
            g.menuOpen = false; g.closeMenu();  st.inHallTrasCerrarMenu = g.inHall;
            // a la cancha: arrancar un modo (el guardián ya no saca del hall,
            // son los ARRANQUES quienes llevan a ella)
            g.switchMode('survival');      st.inHallTrasModo = g.inHall;
            st.rigZ = +g.rig.position.z.toFixed(2);
            // en cancha: abrir el menú → el botón ⌂ VOLVER AL HALL aparece
            g.menuOpen = true; g.drawMenu();
            const rects = g._menuRects || [];
            st.homehallEnCancha = rects.some(x => x.id === 'homehall');
            const idx = rects.findIndex(x => x.id === 'homehall');
            if (idx >= 0) g.menuClick(idx);
            st.inHallTrasHome = g.inHall;
            st.menuAbiertoTrasHome = g.menuOpen;
            g.drawMenu();
            st.homehallEnHall = (g._menuRects || []).some(x => x.id === 'homehall');
            try { localStorage.removeItem('ppxr_dif'); } catch (e) {}
            return st;
          })()
        """)
        check("entrar en VR → nace en el hall", hall.get("inHallOnEnter") is True)
        check("cerrar el menú → SIGUES en el hall", hall.get("inHallTrasCerrarMenu") is True)
        check("arrancar un modo → sale al cancha", hall.get("inHallTrasModo") is False)
        check("rig de vuelta en la cancha (z=0)", hall.get("rigZ") == 0.0,
              f"z={hall.get('rigZ')}")
        check("en cancha el menú muestra ⌂ VOLVER AL HALL", hall.get("homehallEnCancha") is True)
        check("⌂ Home → vuelves al hall", hall.get("inHallTrasHome") is True)
        check("⌂ Home → menú abierto delante (el menú vive en el hall)",
              hall.get("menuAbiertoTrasHome") is True)
        check("en el hall el botón Home NO aparece", hall.get("homehallEnHall") is False)

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
        check("badge DOM V3.1.0-SRV2", badge == "V3.1.0-SRV2", badge)
        check("0 pageerrors en la sesión", len(errors) == 0, "; ".join(errors[:3]))

        await page.screenshot(path=OUT_PNG)
        await browser.close()

    print("== HUB /descargas (servido por dev) ==")
    hub = fetch("/descargas").decode("utf-8", "replace")
    check("hub sirve la V3.1.0-SRV2 (v310-srv2)", "v310-srv2" in hub)
    check("hub sin residuos v309", "v309-hall1" not in hub)
    for z, lo, hi in [("crazypp-v310-srv2-COMPLETO.zip", 100_000_000, 112_000_000),
                      ("crazypp-v310-srv2-ligera.zip", 10_000_000, 13_000_000),
                      ("crazypp-v310-srv2-CLOUDFLARE.zip", 100_000_000, 112_000_000),
                      ("crazypp-live-service-SOLO.zip", 4_000, 12_000)]:
        st, n = head(BASE + "/descargas/" + z)
        check(f"ZIP {z}", st == 200 and lo < n < hi, f"{n:,} B")

    print()
    if FAILS:
        print("RESULTADO: FALLOS ->", FAILS); sys.exit(1)
    print("RESULTADO OK")

asyncio.run(main())
