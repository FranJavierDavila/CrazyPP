#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r77_v3669 — CAPA BL · V3.6.72-SDK6, FASE 71 «LA RAQUETA MODO FANTASMA».

Nota del dueño (r77): «En el apartado de academia el tutorial: en las fases
iniciales, antes de que diga "Pulsa el botón A… Tu mando se convierte en tu
raqueta", [la raqueta ya está visible pegada al mando] — justo antes de que
aparezca. En lugar de colocar la raqueta visible con el mando, puede aparecer
en modo fantasma sin verse aún, hasta que aparece cuando lo dice».

El arreglo (r77) y SU verificación:
  · Núcleo (c12): llave setPalaOculta(v) + flag tutPalaOculta. UNA sola
    regla de visibilidad (hall + fantasma + mano activa) que respetan
    setPaddleHand (cambiar de mano no la destapa) y exitHall (volver del
    Hall tampoco). Fuera de la academia el flag vale false: CERO cambios.
  · Academia (c13): start() la nace INVISIBLE (sólo los mandos GLB
    acompañan) · accionMandoOk subfase 4 la MATERIALIZA en el instante
    exacto en que la voz dice «tu mando se convierte en tu raqueta», con
    la aura dorada (r67/r74) como destello de nacimiento · stop() la
    devuelve a la mano en CUALQUIER salida (jugar ya, B/Y, fin).
  · Introspección QA: estado() expone palaOculta + palaVisible.

BLOQUES: (1) AGUJAS r77 en el game.html servido. (2) CONTADORES + ORDEN de
fuente. (3) JUEGO REAL headless contra el módulo SERVIDO: ciclo de vida
completo del fantasma (nace oculto → sobrevive a las 4 acciones →
materializa EXACTAMENTE en subfase 4 con aura y mandos fuera → cualquier
salida lo restaura → re-arma en la 2.ª sesión y B/Y antes del momento
también restaura), 0 pageerrors.
Uso: python3 scripts/qa_r77_v3669.py [URL]
"""
import asyncio
import base64
import os
import re
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
RAIZ = "/home/z/my-project"
DIR_CAPS = os.path.join(RAIZ, "download")
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- r77 · el núcleo (c12) ---
    ("flag del modo fantasma inicializado a false",
     "this.tutPalaOculta = false;  // r77 · ACADEMIA: pala REAL en modo FANTASMA"),
    ("llave del núcleo setPalaOculta(v)",
     "setPalaOculta(v) {"),
    ("regla ÚNICA de visibilidad (hall + fantasma + mano activa)",
     "!this.inHall && !this.tutPalaOculta && k === this.paddleHand;"),
    ("setPaddleHand respeta el fantasma (cambiar de mano no la destapa)",
     "r77 · ni la ACADEMIA en modo fantasma (paso 1, antes del momento\n      // raqueta): cambiar de mano no la destapa antes de tiempo."),
    ("exitHall respeta el fantasma (volver del Hall tampoco)",
     "r77 · y respeta el MODO FANTASMA de la academia si siguiera vivo."),
    ("fundamento del núcleo (petición del dueño citada)",
     "r77 · ACADEMIA MODO FANTASMA — petición del dueño: en las fases"),
    # --- r77 · la academia (c13) ---
    ("start: la pala nace fantasma (comentario)",
     "r77 · LA RAQUETA MODO FANTASMA (petición del dueño): en las fases"),
    ("start: nace INVISIBLE (sólo mandos GLB)",
     "try { G.setPalaOculta(true); } catch (ePO) { /* sin fantasma, sigue */ }"),
    ("momento raqueta: materializa cuando la voz lo dice (comentario)",
     "r77 · MATERIALIZACIÓN EN EL INSTANTE EXACTO: hasta aquí la pala"),
    ("momento raqueta: destape con guarda",
     "try { G.setPalaOculta(false); } catch (ePR) { /* sigue igual */ }"),
    ("stop: cualquier salida devuelve la pala (blindaje)",
     "try { gm.setPalaOculta(false); } catch (ePS) { /* */ }"),
    ("stop: nadie se queda sin raqueta (comentario)",
     "la pala REAL a la mano. Nadie se queda sin raqueta jamás."),
    # --- r77 · introspección QA ---
    ("estado(): palaOculta expuesta",
     "palaOculta: !!(G && G.tutPalaOculta),"),
    ("estado(): palaVisible expuesta",
     "palaVisible: !!(G && G.paddleMounts && G.paddleMounts[G.paddleHand] &&"),
]

CONTADORES = [
    ("setPalaOculta (1 def + 3 llamadas)",
     ["setPalaOculta("], 4),
    ("tutPalaOculta (init+llave×3+2 reglas+hall+estado)",
     ["tutPalaOculta"], 8),
    ("regla de visibilidad con fantasma (llave + setPaddleHand + exitHall)",
     ["!this.tutPalaOculta && k === this.paddleHand"], 3),
    ("nace fantasma ×1",
     ["G.setPalaOculta(true)"], 1),
    ("materializa ×1",
     ["G.setPalaOculta(false)"], 1),
    ("restaura en stop ×1",
     ["gm.setPalaOculta(false)"], 1),
    ("introspección palaOculta ×1",
     ["palaOculta: !!(G && G.tutPalaOculta)"], 1),
]

ORDEN_FUENTE = [
    ("try { G.setPalaOculta(true);", "G.haptic(G.paddleHand, 0.5, 110);",
     "la pala nace OCULTA antes de que arranque el guion (start completo)"),
    ("try { G.setPalaOculta(false); } catch (ePR)", "auraMeta = 1;",
     "la pala MATERIALIZA justo antes del destello de la aura"),
    ("try { gm.setPalaOculta(false);", "teardownPanel();",
     "stop restaura la pala ANTES de desmontar (G vivo, orden r63)"),
]

# --- JUEGO REAL: ciclo de vida completo del fantasma, contra el SERVIDO ---
JS_FANTASMA = """async () => {
  const THREE = await import('three');
  const T = window.__PP_TUT;
  if (!T || typeof T.start !== 'function') return { error: '__PP_TUT ausente' };
  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  // Mock del núcleo (contrato EXACTO de c12 para la visibilidad de la pala)
  const mkJuego = () => {
    const mounts = [new THREE.Group(), new THREE.Group()];
    mounts[0].visible = true;   // paddleHand 0: la pala de siempre, visible
    const G = {
      net: { online: false }, champs: null,
      trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
      inHall: false,
      rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
        startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
      ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
      renderer: { xr: { isPresenting: true } },
      controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
      paddleHand: 0, tossed: false, mode: 'match',
      paddleMounts: mounts, tutPalaOculta: false,
      setPalaOculta(v) {
        const antes = this.tutPalaOculta;
        this.tutPalaOculta = !!v;
        if (antes === this.tutPalaOculta) return;
        for (let k = 0; k < 2; k++) {
          if (this.paddleMounts[k]) this.paddleMounts[k].visible =
            !this.inHall && !this.tutPalaOculta && k === this.paddleHand;
        }
      },
      scene: new THREE.Scene(), rig: new THREE.Group(), paddleModelRef: null,
      sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
      audio: { playOsc: () => {}, announce: () => {}, serve: () => {} },
      haptic: () => {},
      resetToss() { this.tossed = false; },
      tossFromHand(i, a) { this.tossed = true; },
      feedPracticeBall() { this.__feeds++; },
      exitHall() { this.__exitHall++; },
      enterCalib() { this.calib = true; },
      exitCalib() { this.calib = false; this.__exitCalib++; },
      closeMenu() { this.menuOpen = false; },
      goHomeHall() { this.__goHome++; return true; },
      toggleMenu() {}, anchorMenu() {}, drawMenu() {},
      hideInstrucciones() {}, _instr: null,
      menuOpen: false, menuPage: 'main',
      calibPanel: { group: { visible: true } },
      confettiBurst: 0,
      audio_voice: true,
      __feeds: 0, __exitHall: 0, __exitCalib: 0, __goHome: 0,
    };
    Object.defineProperty(G, 'ballHand', { get() { return 1 - this.paddleHand; } });
    return G;
  };
  const out = { checks: [] };
  const ok = (id, cond, det) => out.checks.push({ id, ok: !!cond, det: det || '' });
  const pal = (G) => G.paddleMounts[G.paddleHand].visible;

  // ---- SESIÓN 1: nace fantasma → 4 acciones → materializa → fin ---------
  let G = mkJuego();
  T.start(G);
  let e = T.estado();
  ok('s1.arranque', e.activo === true && e.paso === 0);
  ok('s1.naceFantasma.flag', e.palaOculta === true);
  ok('s1.naceFantasma.estado', e.palaVisible === false);
  ok('s1.naceFantasma.montura', pal(G) === false);

  T.onTrigger(0); T.tick(0.05);                      // paso 0 → 1
  e = T.estado();
  ok('s1.paso1.fantasma', e.paso === 1 && e.palaOculta === true && e.palaVisible === false);
  T.onTrigger(0); T.tick(0.05);                      // subfase 0 → 1 (grip)
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016); G.sources[0].gamepad.buttons[1] = { pressed: false };
  T.tick(0.016); G.sources[0].gamepad.buttons[1] = { pressed: true };
  T.tick(0.016); T.tick(0.05);                       // subfase 1 → 2 (stick)
  e = T.estado();
  ok('s1.sub2.fantasma', e.subfase === 2 && e.palaOculta === true && e.palaVisible === false);
  G.stickAxis = () => ({ x: 0.7, y: 0 });
  T.tick(0.016); T.tick(0.05);                       // subfase 2 → 3 (botones)
  e = T.estado();
  ok('s1.sub3.fantasma', e.subfase === 3 && e.palaOculta === true && e.palaVisible === false);
  G.sources[0].gamepad.buttons[4] = { pressed: true };   // 4) botón A
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  ok('s1.sub4.momento', e.subfase === 4);
  ok('s1.sub4.materializa.flag', e.palaOculta === false);
  ok('s1.sub4.materializa.estado', e.palaVisible === true);
  ok('s1.sub4.materializa.montura', pal(G) === true);
  ok('s1.sub4.auraEncendida', e.auraMeta === 1);
  ok('s1.sub4.mandosSeVan', e.mandosVisMeta === 0);
  G.controllerPaddles[0].vel.set(1.5, 1.2, 1.5);     // el vaivén sigue vivo
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  ok('s1.vaivenIntacto', e.paso === 2 && e.palaOculta === false && e.palaVisible === true);

  T.stop({ done: false });                            // salir con B/Y al Hall
  ok('s1.stop.restaura.flag', G.tutPalaOculta === false);
  ok('s1.stop.restaura.montura', pal(G) === true);

  // ---- SESIÓN 2: B/Y ANTES del momento también devuelve la pala ---------
  G = mkJuego();
  T.start(G);
  e = T.estado();
  ok('s2.reArma', e.palaOculta === true && e.palaVisible === false);
  T.onTrigger(0); T.tick(0.05);                      // paso 0 → 1
  T.onTrigger(0); T.tick(0.05);                      // subfase 0 → 1
  e = T.estado();
  ok('s2.aMitad.oculta', e.subfase === 1 && e.palaOculta === true);
  T.stop({ done: false });
  ok('s2.stopTemprano.flag', G.tutPalaOculta === false);
  ok('s2.stopTemprano.montura', pal(G) === true);

  // ---- SESIÓN 3: idempotencia + fin del guion (done) --------------------
  G = mkJuego();
  G.setPalaOculta(true); G.setPalaOculta(true);       // doble llamada: inofensiva
  T.start(G);
  e = T.estado();
  ok('s3.idempotente', e.palaOculta === true && e.palaVisible === false);
  T.stop({ done: true });
  ok('s3.fin.doneFlag', G.tutPalaOculta === false && pal(G) === true);
  ok('s3.fin.pp_tut_done', localStorage.getItem('pp_tut_done') === '1');
  return out;
}"""


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r77 en el game.html servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES + ORDEN de fuente —")
    for label, pats, esperado in CONTADORES:
        n = sum(len(re.findall(re.escape(p), src)) for p in pats)
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")
    for a, b, label in ORDEN_FUENTE:
        chk(0 <= src.find(a) < src.find(b), label)

    print("— BLOQUE 3 · JUEGO REAL headless (ciclo de vida del fantasma) —")
    os.makedirs(DIR_CAPS, exist_ok=True)
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate(
                    "() => !!window.__PP_TUT")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_TUT")

            res = await page.evaluate(JS_FANTASMA, [])
            if res.get("error"):
                chk(False, "JS_FANTASMA: " + res["error"])
            else:
                for c in res["checks"]:
                    chk(c["ok"], c["id"] + (f" [{c['det']}]" if c["det"] else ""))

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r77_v3669 · CAPA BL)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
