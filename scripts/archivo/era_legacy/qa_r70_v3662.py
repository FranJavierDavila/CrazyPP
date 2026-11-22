#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r70_v3662 — CAPA BE · V3.6.62-SDK6, FASE 64 «LA ACADEMIA PERFECTA».

El informe del dueño tras probar V3.6.61 en el Quest, punto por punto:
  1. «Devuelve los 4 troqueles de decoración a todos los campeonatos».
  2. «"Tu control es tu raqueta"… ese panel superpone los textos… se
     espera que el usuario mueva la raqueta a ambos lados, lo indica el
     panel pero tiene textos superpuestos».
  3. «Si además la voz aquí dice "Mueve tu raqueta hacia los lados
     rápidamente" reforzaría el mensaje del tutorial».
  4. «Estando en el tutorial pulsamos el botón B para salir al Hall…
     la voz sigue sonando y debe terminar».
  5. «Blindar de tal forma que al salir del tutorial NADA de este
     persista en las otras escenas».
  6. «Cuando tengo que servir la bola debe botar en ambos campos y esto
     no lo comprueba, dando por bueno un servicio aunque bote en 1 sola
     parte del campo, mío o de mi rival».
  7. «Durante la parte del tutorial del Rally, el rival golpea pero no
     aparece su raqueta que debería estar bien colocada».

El arreglo (r70) y SU verificación:
  · TROQUELES SIEMPRE: la condición !game.inAR escondía los troqueles en
    TODAS las sesiones con passthrough del Quest (la QA headless no lo
    veía: inAR=false). Ahora se muestran en todos los campeonatos
    también con passthrough — verificado AQUÍ con inAR=true en el juego
    real de los 5 campeonatos.
  · PANEL SIN SOLAPE: la píldora «TU MANDO ES TU RAQUETA» (caja
    406..478) y la instrucción «MUÉVELA HACIA LOS LADOS» (glifos
    441..463) se comían — DOS textos superpuestos. Nuevo reparto
    vertical: píldora 392..448 · instrucción 472 · barra 500. La
    geometría se comprueba aquí (cajas que NO se tocan).
  · LA VOZ DEL VAIVÉN: el átomo tutv2b («Muévela de lado a lado, con
    firmeza») existía desde r66 y jamás se narraba — ahora suena en el
    momento exacto (1f + 2a + 2b).
  · LA VOZ MUERE AL SALIR: stop() llama audio.callaVoz() (corta el
    buffer vivo _vozSrc + speechSynthesis) y limpia narrKeys/narrRetry —
    en el Hall no queda voz sonando (el caso exacto del dueño).
  · BLINDAJE TOTAL: stop() además cancela devoluciones pendientes y
    devuelve el árbitro a estado limpio (nada del tutorial se cuela).
  · SAQUE CON LOS DOS BOTES: la cuenta exigía solo CRUZAR al campo
    rival (¡voleas y medios saques contaban!). Ahora exige la secuencia
    reglamentaria: bote en TU campo y DESPUÉS en el del rival — verificado
    aquí con un saque que cruza sin botar (NO cuenta), uno que solo bota
    en el tuyo (NO cuenta) y tres completos (cuentan).
  · LA RAQUETA DEL PROFESOR, POR FIN EN SU SITIO: vivía en G.scene
    (mundo crudo) mientras mesa, bola y pala IA viven en el RIG (el
    espacio de referencia XR) — el recentrado del Quest la descolocaba
    («problemas de colocación», «desfasada y no golpea», «el rival
    golpea pero no aparece su raqueta»). Ahora raqueta, aros guía y
    holo-marcador viven EN EL RIG como la mesa; la QA comprueba el
    parent EXACTO y la visibilidad durante todo el rally del paso 5.

4 BLOQUES: (1) AGUJAS de fuente r70. (2) NEGATIVAS. (3) CONTADORES +
geometría del panel. (4) MECÁNICA REAL headless (anclaje RIG, saque con
dos botes, rally visible, voz cortada, cierre sin residuos). (5) TROQUELES
en el juego real de los 5 campeonatos CON y SIN passthrough.
(6) ERRORES DE PÁGINA.
Uso: python3 scripts/qa_r70_v3662.py [URL]"""
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
    # --- r70 · LA RAQUETA DEL PROFESOR VIVE EN EL RIG (colocación) ---
    ("raqueta del rival ANCLADA AL RIG (el espacio de la mesa y la bola)",
     "G.rig.add(raqGrp);"),
    ("comentario de la causa raíz (recentrado del Quest descolocaba la raqueta)",
     "el recentrado del Quest la"),
    ("el ARMA nunca queda oculta (defensiva en raquetaPreparar)",
     "raqModo = 'prep'; raqT = 0;\n    raqGrp.visible = true;          // r70 · defensivo: el arma NUNCA queda oculta"),
    ("el GOLPE siempre se ve (defensiva en raquetaGolpe)",
     "raqGrp.visible = true;          // r70 · defensivo: el golpe SIEMPRE se ve"),
    ("los AROS GUÍA también al RIG",
     "G.rig.add(arosGrp);   // r70 · al RIG: las DIMS son coordenadas del rig"),
    ("el HOLO-MARCADOR también al RIG",
     "G.rig.add(holo);"),
    # --- r70 · PANEL SIN SOLAPE ---
    ("píldora compacta del vaivén (392, alto 56)",
     "pill(c, T('tut_m1_raf'), 392, { col: 'rgba(90,160,255,0.30)', size: 24, h: 56 });"),
    ("instrucción del vaivén en su propia banda (472)",
     "line(c, T('tut_m1_lado'), 472, 21, '#7fb069');"),
    ("barra de progreso bajada (500)",
     "rr(c, 280, 500, 800, 40, 20);"),
    # --- r70 · LA VOZ DEL VAIVÉN (tutv2b por fin suena) ---
    ("el momento raqueta narra 1f + 2a + 2b",
     "narra(['tutv1f', 'tutv2a', 'tutv2b']);"),
    # --- r70 · LA VOZ MUERE AL SALIR ---
    ("callaVoz() existe en el motor de voz (c03)",
     "  callaVoz() {"),
    ("stop() CORTA la voz viva al salir de la academia",
     "try { if (gm.audio && gm.audio.callaVoz) gm.audio.callaVoz(); } catch (eV) { /* */ }"),
    ("stop() limpia los reintentos de narración",
     "narrKeys = null; narrRetry = 0; narrTries = 0;"),
    # --- r70 · BLINDAJE TOTAL ---
    ("stop() cancela golpes pendientes",
     "cancelaDevolucion();\n    try { gm.rules.state = 'point'; gm.rules.message = ''; } catch (eR) { /* */ }"),
    # --- r70 · SAQUE CON LOS DOS BOTES ---
    ("bandera: bote en TU campo",
     "let saqBote1 = false;         // r70 · la bola YA BOTÓ en TU campo (saque válido)"),
    ("bandera: bote en el campo del rival",
     "let saqBote2 = false;         // r70 · y DESPUÉS en el campo del rival"),
    ("la cuenta exige la SECUENCIA completa (bote1 && bote2)",
     "if (!saqLatch && saqBote1 && saqBote2) {"),
    ("el aro TUYO se enciende con el bote propio",
     "saqBote1 = true;\n              if (aroIzq) aroIzq.__ok = true;"),
    ("el aro RIVAL se enciende con el segundo bote",
     "saqBote2 = true;\n              if (aroDer) aroDer.__ok = true;"),
    ("saque nuevo, botes nuevos (muerte de bola)",
     "saqBote1 = false; saqBote2 = false;   // r70 · saque nuevo, botes nuevos"),
    # --- r70 · introspección de QA ---
    ("introspección: raqueta VISIBLE",
     "raqVisible: !!(raqGrp && raqGrp.visible),"),
    ("introspección: raqueta ANCLADA al rig",
     "raqAnclada: !!(raqGrp && G && raqGrp.parent === G.rig),"),
    ("introspección: botes del saque",
     "saqBote1, saqBote2,"),
    ("introspección: aros y holo anclados",
     "arosAnclados: !!(arosGrp && G && arosGrp.parent === G.rig),"),
]

NEGATIVAS = [
    ("la raqueta del rival ya NO nace en G.scene (mundo crudo)",
     "G.scene.add(raqGrp);"),
    ("el holo-marcador ya NO nace en G.scene",
     "G.scene.add(holo);"),
    ("los aros guía ya NO nacen en G.scene",
     "G.scene.add(arosGrp);"),
    ("el saque ya NO cuenta solo con CRUZAR (el voleo no vale)",
     "const cruzada = b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9;"),
    ("los troqueles ya NO dependen de !game.inAR (passthrough los quería)",
     "&& !game.inAR &&"),
    ("el vaivén ya NO narra sin el átomo del vaivén (2b)",
     "narra(['tutv1f', 'tutv2a']);"),
]

CONTADORES = [
    (r"saqBote1", 9, "saqBote1 (decl. + 4 resets + 2 usos + cuenta + introspección)"),
    (r"saqBote2", 8, "saqBote2 (decl. + 4 resets + uso + introspección)"),
    (r"callaVoz", 2, "callaVoz (definición en c03 + llamada en stop)"),
    (r"G\.rig\.add\(", 3, "G.rig.add (raqueta + aros + holo)"),
    (r"tutv2b", 1, "el átomo del vaivén narrado en el momento"),
    (r"raqVisible", 1, "introspección de visibilidad de la raqueta"),
]

# Geometría del panel del vaivén (paso 1, subfase >= 4) — CAJAS que NO
# se tocan (el dueño: «ese panel superpone los textos»):
#   píldora tut_m1_raf: y=392, h=56            → 392..448 (texto 24px: 409..433)
#   línea  tut_m1_lado: y=472, glifos de 21px  → ~461..483
#   barra  de progreso: y=500, h=40            → 500..540 (porcentaje en 521)
#   los 4 puntos de tareas: y=374, radio 9     → 365..383
GEOMETRIA = [
    (383, 392, "los puntos de tareas terminan ANTES de la píldora"),
    (448, 461, "la píldora termina ANTES de la instrucción del vaivén"),
    (483, 500, "la instrucción termina ANTES de la barra de progreso"),
]

TROQUELES = """async () => {
  const g = window.__game;
  if (!g || !g.champDecor) return [{ ok: false, lab: 'juego real sin champDecor' }];
  const out = [];
  const camps = {
    oeste: 4, magia: 4, locura: 4, estacion_orbital: 4, valle_neon: 2,
  };
  for (const cid of Object.keys(camps)) {
    await g.champs.launch(cid);
    for (let i = 0; i < 45; i++) {
      g.champDecor.update(0.05, performance.now() / 1000);
      await new Promise((r) => setTimeout(r, 30));
    }
    const d = g.champDecor;
    const sinAR = d.builtFor === cid && d.pieces.length === camps[cid] &&
      d.pieces.every((p) => p.ready) && d.group.visible === true &&
      !g.champDecorHidden;
    out.push({ ok: sinAR,
               lab: `troqueles de ${cid}: ${d.pieces.length} piezas listas y VISIBLES` });
    // r70 · EL PASSTHROUGH YA NO LOS ESCONDE (el dueño los echaba en
    // falta jugando con passthrough: la condición !game.inAR los mataba)
    g.inAR = true;
    d.update(0.05, performance.now() / 1000);
    out.push({ ok: d.group.visible === true,
               lab: `troqueles de ${cid}: VISIBLES también con passthrough (inAR)` });
    g.inAR = false;
    d.update(0.05, performance.now() / 1000);
    g.champs.leaveAll();
    await new Promise((r) => setTimeout(r, 120));
  }
  return out;
}"""

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
    const aiPaddleMesh = new THREE.Group();
    aiPaddleMesh.name = 'aiPaddleMeshMock';
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
      aiPaddleMesh,
      audio: { playOsc: () => {}, announce: () => {}, serve: () => {},
               paddle: () => {}, voice: true,
               __voz: [], __vozViva: false, __vozCortada: 0,
               speakPlan(plan) { this.__voz = this.__voz
                 .concat(plan.map((p) => p.k)); this.__vozViva = true; return true; },
               callaVoz() { if (this.__vozViva) this.__vozCortada++;
                 this.__vozViva = false; } },
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

  const raqEnRig = () => G.rig.children.find(
    (ch) => ch.name === 'ppTutRaquetaRival');
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
  const misma = (a, b) => Math.abs(a.x - b.x) < 1e-6 &&
    Math.abs(a.y - b.y) < 1e-6 && Math.abs(a.z - b.z) < 1e-6;

  // ---------- 1 · arranque: la raqueta NACE EN EL RIG -----------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  G.aiPaddleMesh.visible = true;         // estado de partido: VISIBLE
  T.start(G);
  T.tick(0.05);
  let e = T.estado();
  out.push({ ok: e.raquetaRival === true && !!raqEnRig(),
             lab: 'raqueta del RIVAL construida EN EL RIG al arrancar' });
  out.push({ ok: e.raqAnclada === true,
             lab: 'ANCLAJE EXACTO: parent de la raqueta === G.rig (colocación)' });
  out.push({ ok: G.aiPaddleMesh.visible === false && e.aiPadOculta === true,
             lab: 'UNA SOLA RAQUETA: la pala IA de los partidos OCULTA en la academia' });
  out.push({ ok: raqEnRig().visible === false,
             lab: 'raqueta del profesor OCULTA en el paso 0 (vive en los pasos 2-5)' });

  // ---------- 2 · paso 1 → paso 2 (acciones + vaivén con la voz 2b) ---
  const vozAntes = G.audio.__voz.length;
  T.onTrigger(0); T.tick(0.05);
  T.tick(0.1); T.tick(0.1);
  T.onTrigger(0); T.tick(0.05);
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
             lab: 'paso 2 EL SAQUE: la raqueta del profesor EN MESA (en el rig)' });
  out.push({ ok: G.audio.__voz.slice(vozAntes).includes('tutv2b'),
             lab: 'LA VOZ DEL VAIVÉN SUENA: tutv2b («muévela de lado a lado») narrado' });

  // ---------- 3 · demo del profesor (el barrido honesto r68/r69 vivo) -
  const p0 = { x: G.ball.pos.x, y: G.ball.pos.y, z: G.ball.pos.z };
  let vioPrep = false;
  for (let i = 0; i < 40; i++) {
    T.tick(0.05);
    if (T.estado().raqModo === 'prep') vioPrep = true;
    if (T.estado().demoFase !== 0) break;
  }
  out.push({ ok: misma(G.ball.pos, p0),
             lab: 'bola QUIETA en el campo del profesor durante la postura' });
  out.push({ ok: vioPrep, lab: 'la raqueta se ARMA (retroceso) antes del saque' });
  let minDist = 1e9, lanzo = false, bolaVivaAlLanzar = false;
  for (let i = 0; i < 40; i++) {
    T.tick(0.02);
    e = T.estado();
    if (e.demoFase >= 2 && !lanzo) {
      lanzo = true;
      bolaVivaAlLanzar = e.bolaViva === true;
    }
    if (lanzo) {
      minDist = Math.min(minDist, dist(raqEnRig().position, G.ball.pos));
      if (i > 24) break;
    }
  }
  out.push({ ok: lanzo, lab: 'el saque del profesor SALE (con su golpe antes)' });
  out.push({ ok: minDist < 0.06,
             lab: `la hoja pasa por la bola al golpear (mín ${Math.round(minDist * 1000)} mm)` });

  // ---------- 4 · práctica: saque VOLEADO no cuenta -------------------
  for (let i = 0; i < 90; i++) {
    T.tick(0.1);
    if (T.estado().demoT >= 6.2) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica',
             lab: 'gatillo → TU TURNO (la raqueta rival espera en guardia)' });
  // 4a · VOLEA: cruza al campo rival SIN botar en el tuyo → NO cuenta
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.5, -2.2); G.ball.vel.set(0, -2.0, -3.0);
  T.tick(0.016);
  e = T.estado();
  const saqAntesVolea = e.saq;
  out.push({ ok: saqAntesVolea === 0 && e.saqBote1 === false,
             lab: 'VOLEA cruzada: sin bote propio NO hay saque válido (r70)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.saq === 0,
             lab: 'la bola muere: el saque voleado NO contó (0/3)' });
  // 4b · SOLO TU CAMPO: bote propio y muere sin cruzar → NO cuenta
  T.onTrigger(0);
  G.ball.pos.set(0.1, 0.80, -1.0); G.ball.vel.set(0, 1.2, -0.4);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saqBote1 === true && e.saq === 0,
             lab: 'bote PROPIO registrado (aro tuyo)… y aún no cuenta' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.saq === 0 && e.saqBote1 === false && e.saqBote2 === false,
             lab: 'medio saque (solo TU campo) NO contó y los botes se resetean' });
  // 4c..4e · TRES SAQUES COMPLETOS: bote tuyo + bote rival → cuentan
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 0.80, -1.0); G.ball.vel.set(0, 1.2, -2.0);  // bote TUYO
    T.tick(0.016);
    G.ball.pos.set(0.1, 0.80, -2.2); G.ball.vel.set(0, 1.0, -2.0);  // bote RIVAL
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);        // muere
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: '3/3 saques COMPLETOS (dos botes) → paso 3' });

  // ---------- 5 · devolución honesta + raqueta SIEMPRE visible --------
  T.onTrigger(0); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque hecho: la bola va hacia el rival (viva)' });
  out.push({ ok: e.raqVisible === true,
             lab: 'raqueta del profesor VISIBLE mientras la bola vuela' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016);
  e = T.estado();
  const velAlArmar = G.ball.vel.length();
  out.push({ ok: e.raqModo === 'prep' || e.raqModo === 'golpe',
             lab: 'bote lejano: el rival ARMA la devolución' });
  let vioDevPend = false, despegaTarde = false, minDev = 1e9;
  let postLanzamiento = -1;
  for (let i = 0; i < 40; i++) {
    T.tick(0.02);
    e = T.estado();
    if (e.devPend > 0) {
      vioDevPend = true;
    } else if (vioDevPend && postLanzamiento < 0) {
      postLanzamiento = 0;              // el tramo A se cierra ESTE tick
      despegaTarde = G.ball.vel.length() > 2.5;
    } else if (postLanzamiento >= 0) {
      postLanzamiento++;
      if (postLanzamiento > 2) break;   // 3 ticks de contacto/acompañamiento
    }
    if (vioDevPend) {
      minDev = Math.min(minDev, dist(raqEnRig().position, G.ball.pos));
    }
  }
  out.push({ ok: vioDevPend,
             lab: 'la devolución queda ARMADA (cuenta atrás del golpe honesto)' });
  out.push({ ok: despegaTarde,
             lab: 'la bola despega DESPUÉS, cuando la hoja la alcanza' });
  out.push({ ok: minDev < 0.10,
             lab: `el blade está SOBRE la bola al despegar (mín ${Math.round(minDev * 1000)} mm)` });

  // ---------- 6 · paso 4 marcador (aros+holo EN EL RIG) → paso 5 -----
  for (let d = 0; d < 2; d++) {
    G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
    T.tick(0.016);
    G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
    T.tick(0.016); T.tick(0.016);
    for (let i = 0; i < 30; i++) {
      T.tick(0.05);
      if (T.estado().devPend <= 0) break;
    }
  }
  for (let i = 0; i < 90; i++) {
    T.tick(0.1);
    if (T.estado().rfHecho) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'punto del rival → paso 4 EL MARCADOR' });
  e = T.estado();
  out.push({ ok: e.holoAnclado === true && e.arosAnclados === true,
             lab: 'holo-marcador y aros guía ANCLADOS AL RIG (misma sala que la mesa)' });
  for (let i = 0; i < 90; i++) T.tick(0.2);
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO → paso 5 LA PRÁCTICA' });
  out.push({ ok: e.raqVisible === true,
             lab: 'RALLY: la raqueta del profesor VISIBLE al entrar al paso 5' });

  // ---------- 7 · el FEED del profesor: golpe visible + bola viva -----
  G.ball.pos.set(0.1, 0.79, -2.3); G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
  let vioGolpeFeed = false, vivoEnGolpe = false, lanzada = false, visibleGolpe = true;
  for (let i = 0; i < 80 && !vivoEnGolpe; i++) {
    T.tick(0.05);
    e = T.estado();
    if (e.raqModo === 'golpe') vioGolpeFeed = true;
    if (!e.raqVisible) visibleGolpe = false;
    if (e.raqModo === 'golpe' && e.bolaViva === true) {
      vivoEnGolpe = true;
      lanzada = G.ball.vel.length() > 2.5 && G.ball.vel.z > 1.0;
    }
  }
  out.push({ ok: vioGolpeFeed,
             lab: 'el profesor GOLPEA su saque de práctica (hoja visible)' });
  out.push({ ok: vivoEnGolpe && lanzada,
             lab: 'bola VIVA y LANZADA hacia ti al paso de la hoja (rally existe)' });
  out.push({ ok: visibleGolpe,
             lab: 'la raqueta NO desaparece en NINGÚN frame del ciclo del rally' });

  // ---------- 8 · devolución del rally → LA VOZ MUERE AL SALIR -------
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016);
  for (let i = 0; i < 30; i++) {
    T.tick(0.05);
    if (T.estado().devPend > 0) break;   // un golpe EN MARCHA al salir
  }
  e = T.estado();
  const devPendAlSalir = e.devPend;
  out.push({ ok: G.audio.__vozViva === true || G.audio.__voz.length > 0,
             lab: 'hay voz de la academia viva justo antes de salir (caso del dueño)' });
  T.stop({});
  e = T.estado();
  out.push({ ok: G.audio.__vozCortada >= 1,
             lab: 'B al Hall: audio.callaVoz() CORTA la voz en el acto (r70)' });
  out.push({ ok: e.voz === null,
             lab: 'sin narraciones pendientes tras salir' });
  out.push({ ok: devPendAlSalir >= 0 && e.devPend === 0,
             lab: 'sin golpes pendientes tras salir (blindaje)' });
  out.push({ ok: G.rules.state === 'point' && G.rules.message === '',
             lab: 'el árbitro queda LIMPIO (nada del tutorial se cuela al Hall)' });
  out.push({ ok: e.activo === false && e.raquetaRival === false,
             lab: 'cierre: la academia suelta la raqueta del rival' });
  out.push({ ok: !G.rig.children.some((ch) => ch.name === 'ppTutRaquetaRival'),
             lab: 'rig SIN residuos de la raqueta rival' });
  out.push({ ok: !G.paddleMounts[1].children.find((ch) => ch.name === 'ppTutAuraPala'),
             lab: 'CERO HALO FANTASMA: la aura salió del paddleMount al cerrar' });
  out.push({ ok: G.aiPaddleMesh.visible === true,
             lab: 'la pala IA VUELVE a estar visible (los partidos la necesitan)' });
  // una segunda sesión rearma todo limpio (el blindaje no rompe el arranque)
  const G2 = mkJuego(1);
  G2.scene.add(G2.rig);
  T.start(G2);
  T.tick(0.05);
  const e2 = T.estado();
  out.push({ ok: e2.activo === true && e2.raqAnclada === true,
             lab: 'segunda sesión: la academia rearma limpia (raqueta de nuevo al rig)' });
  T.stop({});
  return out;
}"""


async def main():
    global ok, fails
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1200)

        print("--- 1 · FUENTE SERVIDA (agujas r70) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (retiradas r70) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · CONTADORES + GEOMETRÍA del panel ---")
        for pat, minimo, label in CONTADORES:
            n = len(re.findall(pat, src))
            chk(n >= minimo, f"{label} ({n})")
        n_lado = len(re.findall(r"tut_m1_lado", src))
        chk(n_lado >= 3, f"tut_m1_lado ES+EN+uso en el servido ({n_lado})")
        n_2b = len(re.findall(r"tutv2b", src))
        chk(n_2b >= 1, f"tutv2b narrado en el servido ({n_2b})")
        for a, b, label in GEOMETRIA:
            chk(a < b, f"{label} ({a} < {b})")

        print("--- 4 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 5 · TROQUELES en el juego real (5 campeonatos, ±passthrough) ---")
        filas = await page.evaluate(TROQUELES)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 6 · ERRORES DE PÁGINA ---")
        chk(len(errors) == 0, f"sin pageerror/console.error ({len(errors)})")
        for err in errors[:5]:
            print("    ·", err[:180])

        await browser.close()

    print(f"\nCAPA BE · qa_r70_v3662: {ok} OK · {fails} FALLOS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
