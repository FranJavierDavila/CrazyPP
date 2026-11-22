#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r68_v3660 — CAPA BC · V3.6.60-SDK6, FASE 62 «LA RAQUETA DEL RIVAL».

Lo pedido por el dueño tras probar V3.6.59 en el Quest (literal):
  · «En el tutorial de la academia la pelota en el saque y en el juego debe
    ser golpeada por la raqueta del rival; en estos momentos permanece
    quieta y la pelota la golpea un fantasma».

Qué pasaba de verdad (dos males del mismo fantasma):
  1. El PROFESOR no tenía pala: la bola del saque demo (pasos 2/4) salía
     con velocidad aplicada EN UN FRAME desde la postura quieta, las
     devoluciones del intercambio (paso 3) y de la práctica (paso 5)
     cambiaban la velocidad de la bola desde el aire vacío y los feeds de
     feedPracticeBall lanzaban la bola en el mismo frame en que aparecía.
  2. Desde la renumeración r67 (11→9 pasos), NADIE ponía tutBolaViva=true
     en el paso 5: tras cada feed la compuerta r66 CONGELABA la bola en el
     aire (sin física, sin eventos) — la bola «permanece quieta» literal.

El arreglo (r68):
  · LA RAQUETA DEL RIVAL: la MISMA pala del juego (makePaddleVisual
    'center' — hoja en el origen, pensado para la IA) viva en la escena
    mundo al lado lejano (ppTutRaquetaRival). Estados: reposo (guardia con
    vaivén) → prep (retroceso siguiendo la bola) → golpe (TRAMO A: barrido
    ease-in hasta el contacto en RAQ_T_GOLPE=0.13 s · TRAMO B:
    acompañamiento hacia la red) → reposo. Visible SÓLO en los pasos 2-5.
  · SAQUES CON ESPERA HONESTA: la demo (case 1) mantiene la bola quieta
    mientras la hoja viaja y el saque REAL sale a RAQ_T_GOLPE — exactamente
    cuando el blade la alcanza. El feed del paso 5 igual (feed5T) y al
    salir pone tutBolaViva=true: el rally del paso 5 vuelve a existir.
  · DEVOLUCIONES (pasos 3 y 5): farBounced arma la raqueta y el golpe
    (raquetaGolpe) parte SIEMPRE de la posición exacta de la bola.

4 BLOQUES: (1) AGUJAS de fuente. (2) NEGATIVAS del golpe fantasma retirado.
(3) MECÁNICA REAL headless sobre el grafo de escena (raqueta construida y
oculta en pasos 0/1 · postura quieta · armado · barrido que pasa por la
bola · saque vivo · devoluciones · feed del paso 5 con bola viva · cierre
sin residuos). (4) ERRORES DE PÁGINA.
Uso: python3 scripts/qa_r68_v3660.py [URL]"""
import asyncio
import re
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- la raqueta del rival ---
    ("nace en el build del panel (junto a los mandos anclados)",
     "buildRaqueta();                     // r68 · LA RAQUETA DEL RIVAL (escena)"),
    ("grupo propio en la ESCENA MUNDO (no en el rig, no en los grips)",
     "raqGrp.name = 'ppTutRaquetaRival';"),
    ("usa la PALA DEL JUEGO con la hoja en el origen (modo IA)",
     "raqVis = makePaddleVisual(G.paddleModelRef, 'center');"),
    ("guardia al lado lejano con vaivén vivo",
     "// REPOSO: guardia del rival al lado lejano, vaivén vivo"),
    ("barrido de dos tramos: impacto + acompañamiento",
     "raqGrp.position.lerpVectors(raqDe, raqContacto, u);"),
    ("constante del barrido hasta la bola (0.13 s)",
     "const RAQ_T_GOLPE = 0.13;     // s de la barra hasta la bola (contacto)"),
    ("el tick de la raqueta vive en el ciclo del tutorial",
     "try { tickRaqueta(dt); } catch (e) { /* decorativo */ } // r68 · raqueta rival"),
    ("sólo en los pasos de mesa (2-5)",
     "const conRival = (step >= 2 && step <= 5);"),
    # --- saque demo con golpe visible ---
    ("la demo ARMA la raqueta durante la postura",
     "if (demoFaseT >= espera - 0.55) raquetaPreparar();"),
    ("el golpe arranca con la transición a la suelta (contacto = bola)",
     "raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 1);   // r68 · la hoja barre"),
    ("el saque se RETIENE hasta que la hoja llega (adiós al fantasma)",
     "if (demoFaseT < RAQ_T_GOLPE) break;"),
    # --- devoluciones (paso 3 y paso 5) ---
    ("el bote lejano ARMA la devolución (paso 3)",
     "raquetaPreparar();        // r68 · el rival ARMA la devolución"),
    ("el fallo a la red también tiene SU golpe (corto)",
     "raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 0.45); // r68 · golpe corto a la red"),
    ("la práctica arma al rival (paso 5)",
     "raquetaPreparar();              // r68 · el rival se arma"),
    # --- el paso 5 vuelve a tener rally ---
    ("el saque del profesor espera a la hoja (cuenta atrás feed5T)",
     "feed5T = RAQ_T_GOLPE;"),
    ("la bola queda VIVA al salir el saque del profesor",
     "G.tutBolaViva = true;    // bola en juego: el rally existe"),
    # --- higiene ---
    ("limpieza en el cierre (doble cinturón con teardownPanel)",
     "limpiarRaqueta();                   // r68 · la pala del rival sale con el guion"),
    ("introspección de QA para la raqueta",
     "raquetaRival: !!raqGrp,"),
]

NEGATIVAS = [
    ("el saque instantáneo del profesor (golpe fantasma) retirado",
     "// SUELTA: el profesor saca (saque REAL desde su campo)"),
    ("sin import huérfano: makePaddleVisual ahora SÍ se usa en c13",
     "import { fixInvertedMeshes, loadGunModel, loadPaddleModel, makeGunVisual } from './c01_modelos_3d.js';"),
]

MECANICA = """async () => {
  const out = [];
  const THREE = await import('three');
  const T = window.__PP_TUT;
  if (!T) return [{ ok: false, lab: '__PP_TUT ausente' }];

  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  const mkJuego = (mano) => {
    const grips = [new THREE.Group(), new THREE.Group()];
    const paddleMounts = [new THREE.Group(), new THREE.Group()];
    grips[0].add(paddleMounts[0]);
    grips[1].add(paddleMounts[1]);
    return {
      net: { online: false }, champs: null,
      trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
      rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
        startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
      ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
      renderer: { xr: { isPresenting: true } },
      controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
      paddleHand: mano, tossed: false, mode: 'match',
      sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
      grips, paddleMounts, handOf: ['left', 'right'],
      audio: { playOsc: () => {}, announce: () => {}, serve: () => {},
               paddle: () => {}, voice: true,
               speakPlan(plan) { this.__voz = (this.__voz || [])
                 .concat(plan.map((p) => p.k)); return true; } },
      stickAxis(h) { return this.__stick || { x: 0, y: 0 }; },
      haptic: () => {},
      resetToss() { this.tossed = false; },
      tossFromHand(i, a) { this.tossed = true; },
      feedPracticeBall() { this.__feeds = (this.__feeds || 0) + 1; },
      exitHall() {}, enterCalib() { this.calib = true; },
      exitCalib() { this.calib = false; this.__exitCalib = (this.__exitCalib || 0) + 1; },
      closeMenu() {}, goHomeHall() { return true; },
      toggleMenu() {}, anchorMenu() {}, drawMenu() {},
      hideInstrucciones() {}, _instr: null,
      menuOpen: false, menuPage: 'main',
      calibPanel: { group: { visible: true } },
      confettiBurst: 0,
      scene: new THREE.Scene(),
      rig: new THREE.Group(),
      paddleModelRef: null,
    };
  };

  const raqEnEscena = () => G.scene.children.find(
    (ch) => ch.name === 'ppTutRaquetaRival');
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
  const misma = (a, b) => Math.abs(a.x - b.x) < 1e-6 &&
    Math.abs(a.y - b.y) < 1e-6 && Math.abs(a.z - b.z) < 1e-6;

  // ---------- 1 · arranque: la raqueta NACE oculta --------------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.raquetaRival === true && !!raqEnEscena(),
             lab: 'raqueta del RIVAL construida en la escena al arrancar' });
  out.push({ ok: raqEnEscena().visible === false,
             lab: 'raqueta OCULTA en el paso 0 (sólo vive en los pasos 2-5)' });

  // ---------- 2 · paso 1 → paso 2 (baile de acciones r67) -------------
  T.onTrigger(0); T.tick(0.05);                  // paso 0 → paso 1 (gatillo pide)
  T.tick(0.1); T.tick(0.1);                      // respira (halo del gatillo)
  T.onTrigger(0); T.tick(0.05);                  // gatillo hecho → halo del GRIP
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: false };
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  G.__stick = { x: 0.7, y: 0 };
  T.tick(0.016); T.tick(0.05);
  G.sources[0].gamepad.buttons[4] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 2 && e.raquetaRival,
             lab: 'paso 2 EL SAQUE: la raqueta del rival EN MESA' });
  T.tick(0.05);                                  // un tick con paso 2 activo
  e = T.estado();
  out.push({ ok: raqEnEscena().visible === true,
             lab: 'raqueta VISIBLE en los pasos de mesa' });
  out.push({ ok: e.raqModo === 'reposo',
             lab: 'en GUARDIA mientras la bola espera' });

  // ---------- 3 · la demo: postura quieta + armado + barrido ----------
  const p0 = { x: G.ball.pos.x, y: G.ball.pos.y, z: G.ball.pos.z };
  let vioPrep = false, demoFase = 0;
  for (let i = 0; i < 40; i++) {                 // 2.0 s en pasos de 0.05
    T.tick(0.05);
    demoFase = T.estado().demoFase;
    if (T.estado().raqModo === 'prep') vioPrep = true;
    if (demoFase !== 0) break;
  }
  out.push({ ok: misma(G.ball.pos, p0),
             lab: 'bola QUIETA en el campo del profesor durante la postura' });
  out.push({ ok: vioPrep,
             lab: 'la raqueta se ARMA (retroceso) antes del saque' });
  // barrido fino: la hoja pasa por la bola EXACTAMENTE al lanzar
  let minDist = 1e9, lanzo = false, bolaVivaAlLanzar = false;
  for (let i = 0; i < 40; i++) {
    T.tick(0.02);
    e = T.estado();
    if (e.demoFase >= 2 && !lanzo) {
      lanzo = true;
      bolaVivaAlLanzar = e.bolaViva === true;
    }
    if (lanzo) {
      const rq = raqEnEscena();
      minDist = Math.min(minDist, dist(rq.position, G.ball.pos));
      if (i > 24) break;
    }
  }
  out.push({ ok: lanzo, lab: 'el saque del profesor SALE (con su golpe antes)' });
  out.push({ ok: bolaVivaAlLanzar, lab: 'bola VIVA al salir el saque' });
  out.push({ ok: G.ball.vel.length() > 3,
             lab: `velocidad REAL de saque (${Math.round(G.ball.vel.length() * 100) / 100} m/s)` });
  out.push({ ok: minDist < 0.06,
             lab: `la hoja pasa por la bola al golpear (mín ${Math.round(minDist * 1000)} mm)` });
  const rc2 = T.estado().raqContacto;
  out.push({ ok: rc2 && Math.hypot(rc2[0] - p0.x, rc2[1] - p0.y, rc2[2] - p0.z) < 0.01,
             lab: 'contacto registrado EXACTAMENTE donde estaba la bola' });
  for (let i = 0; i < 30; i++) T.tick(0.05);     // 1.5 s: sigue + guardia
  out.push({ ok: T.estado().raqModo === 'reposo',
             lab: 'tras el golpe VUELVE a la guardia (sin poses raras)' });

  // ---------- 4 · demo completa → práctica → 3 saques → paso 3 --------
  for (let i = 0; i < 90; i++) {                 // corre la demo (demoT ≥ 6)
    T.tick(0.1);
    if (T.estado().demoT >= 6.2) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica',
             lab: 'gatillo → TU TURNO (la raqueta rival espera en guardia)' });
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: '3/3 saques → paso 3 EL INTERCAMBIO' });

  // ---------- 5 · paso 3: el rival ARMA y GOLPEA ----------------------
  T.onTrigger(0); T.tick(0.016);                 // sacas
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque hecho: la bola va hacia el rival (viva)' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016);
  e = T.estado();
  // headless el bote y el hit colapsan en el MISMO tick (vel.y 0.6 ya
  // cumple ambas condiciones): se acepta prep o golpe directo
  out.push({ ok: e.raqModo === 'prep' || e.raqModo === 'golpe',
             lab: 'bote lejano: el rival ARMA la devolución (o golpea en el mismo tick)' });
  const posBote = { x: G.ball.pos.x, y: G.ball.pos.y, z: G.ball.pos.z };
  T.tick(0.016);
  e = T.estado();
  const rc3 = e.raqContacto;
  out.push({ ok: (e.rfFase === 'ida' || e.rfFase === 'fallo') && rc3 &&
             Math.hypot(rc3[0] - posBote.x, rc3[1] - posBote.y, rc3[2] - posBote.z) < 0.01,
             lab: 'SU hoja golpea justo donde estaba la bola (devolución 1)' });
  out.push({ ok: e.raqModo === 'golpe',
             lab: 'la raqueta está en pleno GOLPE tras devolver' });

  // ---------- 6 · paso 4 marcador → paso 5 LA PRÁCTICA ----------------
  for (let d = 0; d < 2; d++) {                  // devoluciones 2 y 3 (el 3.º falla)
    G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
    T.tick(0.016);
    G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
    T.tick(0.016); T.tick(0.016);
  }
  for (let i = 0; i < 90; i++) {                 // el fallo muere → rfHecho
    T.tick(0.1);
    if (T.estado().rfHecho) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'punto del rival → paso 4 EL MARCADOR' });
  for (let i = 0; i < 90; i++) T.tick(0.2);      // la demo del marcador (14 s)
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO → paso 5 LA PRÁCTICA' });

  // ---------- 7 · el FEED del profesor: golpe visible + bola viva -----
  // la bola queda MUERTA (apoyada en el campo rival, como al morir un
  // intercambio real) para que el ciclo de 0,5 s rearme al profesor
  G.ball.pos.set(0.1, 0.79, -2.3); G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
  let vioGolpeFeed = false, quietaFeed = false, vivoEnGolpe = false;
  let lanzada = false, posFeed = null;
  for (let i = 0; i < 80 && !vivoEnGolpe; i++) { // ciclo de bola muerta 0.5 s
    T.tick(0.05);
    e = T.estado();
    if (e.raqModo === 'golpe' && !posFeed) {
      posFeed = { x: G.ball.pos.x, y: G.ball.pos.y, z: G.ball.pos.z };
      vioGolpeFeed = true;
    }
    if (posFeed && e.raqModo === 'golpe' && e.bolaViva === false)
      quietaFeed = misma(G.ball.pos, posFeed);
    if (posFeed && e.raqModo === 'golpe' && e.bolaViva === true) {
      vivoEnGolpe = true;
      lanzada = G.ball.vel.length() > 2.5 && G.ball.vel.z > 1.0;
    }
  }
  out.push({ ok: vioGolpeFeed,
             lab: 'el profesor GOLPEA su saque de práctica (hoja visible)' });
  out.push({ ok: quietaFeed,
             lab: 'la bola ESPERA quieta mientras la hoja viaja' });
  out.push({ ok: vivoEnGolpe && lanzada,
             lab: 'bola VIVA y LANZADA hacia ti al paso de la hoja (rally existe)' });

  // ---------- 8 · una devolución completa y cierre limpio -------------
  for (let i = 0; i < 20; i++) T.tick(0.05);     // la bola vuela hacia ti
  G.ball.pos.set(0.05, 1.15, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  e = T.estado();
  const crossOk = e.fase === 'vuelo_lejos' || e.hitCount >= 1;
  out.push({ ok: crossOk, lab: 'tu devolución cruza hacia el campo lejano' });
  G.ball.pos.set(0.1, 0.85, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.raqModo === 'golpe' || e.hitCount >= 1,
             lab: 'el profesor devuelve EN PRÁCTICA con golpe visible' });
  T.stop({});
  e = T.estado();
  out.push({ ok: e.activo === false && e.raquetaRival === false,
             lab: 'cierre: la academia suelta la raqueta del rival' });
  out.push({ ok: !G.scene.children.some((ch) => ch.name === 'ppTutRaquetaRival'),
             lab: 'escena SIN residuos de la raqueta rival' });
  return out;
}"""


async def main():
    global ok, fails
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1200)

        print("--- 1 · FUENTE SERVIDA (agujas r68) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (el golpe fantasma retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · CONTADORES ---")
        n_golpes = len(re.findall(r"raquetaGolpe\(", src))
        chk(n_golpes >= 5, f"raquetaGolpe( presente en los 5 momentos ({n_golpes})")
        n_preps = len(re.findall(r"raquetaPreparar\(\)", src))
        chk(n_preps >= 3, f"raquetaPreparar() en demo + paso 3 + paso 5 ({n_preps})")
        n_limp = len(re.findall(r"limpiarRaqueta\(\);", src))
        chk(n_limp >= 2, f"limpiarRaqueta() en teardownPanel y stop ({n_limp})")

        print("--- 4 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 5 · ERRORES DE PÁGINA ---")
        chk(len(errors) == 0, f"sin pageerror/console.error ({len(errors)})")
        for err in errors[:5]:
            print("    ·", err[:180])

        await browser.close()

    print(f"\nCAPA BC · qa_r68_v3660: {ok} OK · {fails} FALLOS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
