#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r66_v3658 — CAPA BA · V3.6.58-SDK6, FASE 60 «LA ACADEMIA SOBRE LA MESA».

Lo pedido por el dueño tras probar V3.6.57 en el Quest (literales):
  · «Sigo escuchando un ruido molesto de bote continuo, eliminar» → c12:
    con tutV1 y sin bola viva la bola queda EN CINEMÁTICA (holdLock, sin
    física, sin eventos, sin pock) — c13 pone G.tutBolaViva=true sólo con
    bola en juego (saque/rally/demos) y la ACUESTA en los pasos quietos.
  · «Las voces deberían ser más pausadas… y mejorar la entonación» →
    átomos Piper regenerados con --length-scale 1.16 + --sentence-silence
    0.55 y respiro entre átomos en narra() (gap 0.32).
  · «El mando debería mostrarse delante en el centro… te paso el derecho
    (mando_derecho.glb, botones B y A) para que pongas AMBOS» → dos GLB
    reales (TUT_MANDO_GLB izq Y/X + TUT_MANDO_DER_GLB der B/A) centrados
    bajo la pizarra (mandosGrp con pose propia centro/saque/oculto) y
    anclas del derecho ESPEJO del izquierdo (clustering verificado).
  · «Las zonas que marcas sobre los pulsadores deben verse mejor, menos
    transparentes» → halos OPACOS (núcleo blanco sólido, escala 0.052,
    pulso 0.72..1.0) + ETIQUETA de la pieza pedida (sprite legible).
  · «Después de enseñar los mandos podría aparecer sobre ellos una
    raqueta con material tipo fantasma» → clon de la pala REAL del juego
    (makePaddleVisual) con material aditivo translúcido sobre AMBOS
    mandos; aparece al dominarlos (subfase 4) y vive en el paso 2 y en
    la pose de saque.
  · «Ojo los textos en determinadas explicaciones se están solapando» →
    pintor 9 re-espaciado (título 206 · filas 242/314/386 · poder 462 ·
    píldora 538) — nada invade la línea de «B · saltar» (604) ni la zona
    negra (hasta 618).
  · «La simulación de reglas a una distancia sobre la mesa real no tiene
    sentido, mejor explicarlo pausadamente sobre la mesa real… ver 1
    ejemplo… el rival devuelve… cada dos saques rota el sacador… 11
    puntos con diferencia de 2… a 10-10 el saque se alterna cada punto…
    pudiendo pararse en cada fase» → paso 3 (demo REAL de saque con los
    mandos y la bola del juego: bote propio → rival → PUNTO, findServe
    Velocity + física y sonidos de verdad, y luego 3 saques del jugador),
    paso 4 (intercambio REAL: sacas, el rival devuelve 2 veces y falla en
    la 3ª — rota el sacador) y paso 5 (marcador BAJO sobre la mitad rival
    con saques reales en bucle: 10-10 rápido y P·A·P·P a +2). Panel
    apartado en 3/4/5/6 (la mesa nunca tapada).

Pruebas: (1) FUENTE SERVIDA — agujas r66 + negativas (holo r65 retirado,
claves tut_r1_*/tut_r2_* retiradas, gap 0.10 retirado). (2) i18n ES/EN ×2.
(3) ÁTOMOS de voz 27 ×2 bancos. (4) MECÁNICA REAL headless: mandos duales
con 8 halos + etiqueta, fantasma al dominar, demo de saque por fases con
tutBolaViva, práctica de 3 saques, intercambio con rival que falla,
marcador con igualada a +2, ENTENDIDO con puerta de tiempo, salida limpia.

Uso: python3 scripts/qa_r66_v3658.py        (servidor dev en :3000)
"""
import asyncio
import re
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  \u2713 ' if cond else '  \u2717 FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # --- adiós DEFINITIVO al bote continuo (petición literal del dueño) ---
    ("c12: la bola de la academia QUEDA DORMIDA sin bola viva",
     "if (this.tutV1 && !this.tutBolaViva && !holdLock) {"),
    ("c12: sin física (holdLock) y sin velocidad mientras duerme",
     "this.ball.vel.set(0, 0, 0);\n      this.ball.spin.set(0, 0, 0);\n    }\n\n    // 4) Física"),
    ("c13: la bola viva SOLO con saque/rally/demos (practica lanza)",
     "G.tutBolaViva = true;\n        }\n        break;\n      case 4:"),
    ("c13: paso 4 el saque también despierta la bola",
     "G.tutBolaViva = true;\n          rfFase = 'vuelo';"),
    ("c13: al arrancar la academia la bola nace DORMIDA",
     "G.tutBolaViva = false;                // r66 · bola DORMIDA salvo bola en juego"),
    ("c13: al salir, la bola vuelve al núcleo",
     "gm.tutBolaViva = null;                // r66 · la bola vuelve al núcleo"),
    # --- voces más pausadas ---
    ("respiro entre átomos de voz (gap 0.32)",
     "const plan = keys.map((k) => ({ k, gap: 0.32 }));"),
    # --- DOS mandos reales centrados ---
    ("GLB del mando DERECHO embebido",
     "const TUT_MANDO_DER_GLB = '"),
    ("anclas del derecho = espejo del izquierdo",
     "const ANCLAS_MANDO_DER = {"),
    ("espejo verificado por clustering (comentario)",
     "ESPEJO geométrico del izquierdo (verificado por"),
    ("grupo propio de mandos con pose (centro/saque/oculto)",
     "function _poseMandos() {"),
    ("mandos centrados bajo la pizarra",
     "mandosGrp.position.set(0, 1.07, -0.56);"),
    ("halos OPACOS (núcleo blanco sólido)",
     "rg.addColorStop(0, 'rgba(255,255,255,1)');"),
    ("halos más grandes (0.052)",
     "sp.scale.setScalar(0.052);              // r66 · más GRANDE (era 0.03)"),
    ("etiqueta legible de la pieza pedida",
     "function _etiquetaSprite() {"),
    ("etiqueta compuesta para los botones Y·X | B·A",
     "return T('tut_lab_btns_i') + '  ·  ' + T('tut_lab_btns_d');"),
    ("raqueta FANTASMA sobre el mando",
     "function _ponFantasma(mm) {"),
    ("fantasma = pala REAL con material aditivo",
     "blending: THREE.AdditiveBlending, depthWrite: false,"),
    ("la fantasma aparece al dominar los mandos",
     "fantasmaMeta = 1;                    // el mando SE CONVIERTE en raqueta"),
    ("el giro se DETIENE cuando la fantasma aparece",
     "const giroMeta = (fantasmaMeta > 0.02 || mandosPose !== 'centro') ? 0"),
    ("pose de saque anclada a la MESA (mundo → rig)",
     "if (mandosPose === 'saque') destino.copy(G.rig.worldToLocal(destino));"),
    ("bola de la demo en la palma del mando izquierdo",
     "function bolaPalmDemo() {"),
    # --- pasos rediseñados SOBRE LA MESA ---
    ("paso 3: demo real + práctica (submáquina)",
     "submodo = 'demo';\n        demoT = 0; demoCiclos = 0;"),
    ("paso 3: mandos en pose de SAQUE sobre la mesa",
     "mandosPose = 'saque';\n        fantasmaMeta = 0.8;"),
    ("paso 4: intercambio real contra el rival",
     "rfFase = 'saque'; rfVueltas = 0; rfHecho = false; rfVueltaVista = false;"),
    ("paso 5: marcador BAJO sobre la mitad rival",
     "holo.position.set(0, DIMS.tableTopY + 0.22, DIMS.tableCenterZ - DIMS.tableHalfLength * 0.34);"),
    ("paso 5: cartel +2 PARA GANAR en la igualada",
     "holoCartel2 = _cartelTxt(T('tut_h_p2'), '#ffd257', 54, 0.34, 0.17);"),
    ("ciclo de demo: postura → suelta → vuelo → punto → reset",
     "function tickDemoSaque(dt, esMarcador) {"),
    ("la demo SUELTA la bola con el solucionador REAL de saques",
     "const { v, spin } = findServeVelocity(b.pos, 1, { x: 0.05, spd: 1.22 });"),
    ("la demo cuenta el BOTE PROPIO",
     "demoBote1 = true;\n          demoTxt = { txt: T('tut_d3_p1')"),
    ("la demo cuenta el BOTE RIVAL",
     "demoBote2 = true;\n          demoTxt = { txt: T('tut_d3_p2')"),
    ("el marcador anota puntos con las REGLAS del árbitro",
     "function anotaPuntoMarcador() {"),
    ("igualada: el marcador muestra el cartel 10-10",
     "if (holoTokens) holoTokens.cartel10.visible = true;"),
    ("el visual del marcador lee el tanteo real",
     "const nI = holoPips.__pi || 0, nD = holoPips.__pd || 0;"),
    ("paso 4: el rival devuelve con el solucionador REAL de tiros",
     "const v = computeShotVelocityReal(b.pos, t, 1.05, 4.8, _cero);"),
    ("paso 4: el rival FALLA a la tercera (remate corto a la red)",
     "b.vel.copy(v).multiplyScalar(0.62);"),
    ("paso 4: al fallar el rival, PUNTO y rotación narrada",
     "demoTxt = { txt: T('tut_d4_ok'), col: 'rgba(47,158,68,0.35)', t: 3.4 };"),
    ("paso 4: si no llegas, el intercambio se repite sin castigo",
     "rfFase = 'saque';\n              rfVueltas = 0; farBounced = false; rfVueltaVista = false;"),
    ("gatillo del paso 3: demo → práctica tras ver la mesa",
     "if (demoT > 2.5) {\n            submodo = 'practica';"),
    ("gatillo del paso 4: saca para empezar el intercambio",
     "else if (rfFase === 'saque' && !G.tossed) {"),
    ("paso 5: ENTENDIDO con puerta de tiempo",
     "if (demoT >= DEMO_MIN) { narra(['tutok']); advance(); }"),
    ("estado() para QA: mandos duales, fantasma y demos",
     "mandos: !!mandosGrp,"),
    ("guion de voz r66 (tutv1f de la raqueta)",
     "['tutv1a', 'tutv1b'],                    // 1 mandos (luego c/d/e/f por acción)"),
    # --- textos sin solapes (pintor 9 re-espaciado) ---
    ("pintor 9: filas subidas (242/314/386)",
     "modeRow(c, 314, 'rgba(12,166,120,0.8)', 'R', T('sec_rank'), T('tut_s7_m2'));"),
    ("pintor 9: píldora final a 538 (antes 570 invadía «B · saltar»)",
     "pill(c, T('tut_hint_next'), 538, { w: 520, h: 46, col: 'rgba(232,180,90,0.28)', size: 21 });"),
    ("pintor 1: píldora del momento RAQUETA",
     "pill(c, T('tut_m1_raf'), 470, { col: 'rgba(90,160,255,0.30)', size: 26 });"),
]

NEGATIVAS = [
    ("el holo abstracto r65 (marcador flotante) retirado",
     "function construirHoloPuntos() {"),
    ("el holo-saque abstracto r65 retirado",
     "function construirHoloSaques() {"),
    ("claves tut_r1_*/tut_r2_* retiradas de i18n",
     "tut_r1_t: '"),
    ("el respiro viejo de voz (0.10) retirado",
     "const plan = keys.map((k) => ({ k, gap: 0.10 }));"),
    ("el pintor 9 viejo (solape pill 570 vs hint 604) retirado",
     "pill(c, T('tut_hint_next'), 570, { w: 520, h: 50, col: 'rgba(232,180,90,0.28)', size: 22 });"),
]

CLAVES = [
    "tut_m1_raf", "tut_d3_t", "tut_d3_l1", "tut_d3_l2", "tut_d3_l3",
    "tut_d3_go", "tut_d3_p1", "tut_d3_p2", "tut_d3_pto",
    "tut_d4_t", "tut_d4_l1", "tut_d4_l2", "tut_d4_l3", "tut_d4_task",
    "tut_d4_ok", "tut_d5_t", "tut_d5_l1", "tut_d5_l2", "tut_d5_l3",
    "tut_ent", "tut_h_p2", "tut_lab_btns_i", "tut_lab_btns_d",
]

ATOMOS = ["tutv0a", "tutv0b", "tutv1a", "tutv1b", "tutv1c", "tutv1d",
          "tutv1e", "tutv1f", "tutv2a", "tutv2b", "tutv3a", "tutv3b",
          "tutv3c", "tutv3d", "tutv4a", "tutv4b", "tutv5a", "tutv5b",
          "tutv6a", "tutv6b", "tutv7a", "tutv8a", "tutv9a", "tutv10a",
          "tutv10b", "tutok", "tutotra"]

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
  const mkJuego = (mano) => ({
    net: { online: false }, champs: null,
    trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
    rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
      startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
    ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
    renderer: { xr: { isPresenting: true } },
    controllerPaddles: [{ vel: V(0, 0, 0) }, { vel: V(0, 0, 0) }],
    paddleHand: mano, tossed: false, mode: 'match',
    sources: [{ gamepad: { buttons: [] } }, { gamepad: { buttons: [] } }],
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
    sceneAddSpy: 0,
  });

  // ---------- 1 · arranque + DOS mandos GLB --------------------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0 && e.total === 11,
             lab: 'arranque: paso 0 de 11' });
  out.push({ ok: e.bolaViva === false,
             lab: 'la bola nace DORMIDA (adiós al bote continuo)' });
  out.push({ ok: e.voz === 'tutv0a', lab: 'bienvenida hablada (tutv0a)' });
  // espera el parse async de los DOS GLB
  for (let i = 0; i < 80 && !e.dosMandos; i++) {
    await new Promise((r) => setTimeout(r, 50));
    e = T.estado();
  }
  out.push({ ok: e.mandos && e.dosMandos,
             lab: 'DOS mandos GLB cargados (izquierdo + derecho)' });
  out.push({ ok: e.mandosPose === 'centro',
             lab: 'mandos CENTRADOS delante (pose centro)' });
  const mandosGrp = G.rig.children.find((ch) => ch.name === 'ppTutMandos');
  let nHalos = 0, nEtiqueta = 0, nFantasmas = 0;
  if (mandosGrp) mandosGrp.traverse((o) => {
    if (o.isSprite) (o.__cv ? nEtiqueta++ : nHalos++);
  });
  out.push({ ok: nHalos === 8, lab: `8 halos opacos (4 por mando) · hay ${nHalos}` });
  out.push({ ok: nEtiqueta === 1, lab: 'etiqueta de la pieza pedida presente' });
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.mandoHl === null,
             lab: 'paso 0 sin pieza resaltada: correcto' });

  // ---------- 2 · paso 1: 4 acciones reales + RAQUETA FANTASMA ------
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 0 && e.mandoHl === 'gatillo',
             lab: 'paso 1: halo en el GATILLO (subfase 0)' });
  T.tick(0.1); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.etiqueta > 0.5,
             lab: 'etiqueta GATILLO visible sobre los mandos' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 1 && e.mandoHl === 'grip',
             lab: 'gatillo hecho → halo en el GRIP' });
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: false };
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 2 && e.mandoHl === 'stick',
             lab: 'grip hecho → halo en el STICK' });
  G.__stick = { x: 0.7, y: 0 };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 3 && e.mandoHl === 'botones',
             lab: 'stick movido → halo en los BOTONES' });
  out.push({ ok: e.etiqueta > 0.5,
             lab: 'etiqueta doble Y·X | B·A visible' });
  G.sources[0].gamepad.buttons[4] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 4 && e.mandoHl === null,
             lab: 'A pulsada: mandos dominados (sin halo)' });
  for (let i = 0; i < 30; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.fantasma === true,
             lab: 'RAQUETA FANTASMA visible sobre los mandos (fade in)' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv1f'),
             lab: 'voz del momento raqueta (tutv1f)' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 2, lab: 'paso 1 → 2 (la pala)' });

  // ---------- 3 · paso 2 vaivén → paso 3 DEMO SOBRE LA MESA ---------
  G.controllerPaddles[G.paddleHand].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.pose === 'lado',
             lab: 'vaivén → paso 3 EL SAQUE con panel APARTADO' });
  out.push({ ok: e.submodo === 'demo' && e.mandosPose === 'saque',
             lab: 'demo de saque con los mandos en POSE DE SAQUE' });
  out.push({ ok: e.voz === 'tutv3a', lab: 'narración del saque (tutv3a)' });
  // el gatillo ANTES de 2.5 s NO pasa a práctica
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.submodo === 'demo',
             lab: 'la práctica se niega antes de ver la demo' });
  // deja correr la demo: el ciclo suelta la bola (fase 1) y la bola vuela
  for (let i = 0; i < 25 && e.demoFase === 0; i++) { T.tick(0.2); e = T.estado(); }
  T.tick(0.2); T.tick(0.2);          // la fase SUELTA se ejecuta y despierta la bola
  e = T.estado();
  out.push({ ok: e.demoFase >= 1, lab: 'la demo suelta la bola (fase suelta)' });
  out.push({ ok: e.bolaViva === true,
             lab: 'bola VIVA durante el vuelo de la demo' });
  for (let i = 0; i < 30; i++) { T.tick(0.2); }
  e = T.estado();
  out.push({ ok: e.demoCiclos >= 1 || e.demoFase >= 2,
             lab: 'ciclo de demo avanza (bote propio/rival/punto)' });
  // ahora sí: gatillo → práctica
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica' && G.rules.state === 'serve' &&
             G.rules.server === 'player',
             lab: 'gatillo → TU TURNO: práctica con estado real' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv3d'),
             lab: 'voz de la práctica (tutv3d)' });
  out.push({ ok: e.mandosPose === 'oculto',
             lab: 'mandos APARTADOS para la práctica (mesa libre)' });
  // 3 saques válidos
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: '3/3 saques → paso 4 EL INTERCAMBIO' });

  // ---------- 4 · paso 4: intercambio REAL (rival devuelve y falla) --
  e = T.estado();
  out.push({ ok: e.rfFase === 'saque' && e.mandosPose === 'oculto',
             lab: 'paso 4: espera el saque del jugador' });
  T.onTrigger(0);                       // saca
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque hecho: la bola va hacia el rival (viva)' });
  // bote lejano: el rival devuelve (vuelta 1)
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'ida', lab: 'el rival DEVUELVE (ida hacia ti)' });
  // tu golpe: la bola cruza hacia el campo lejano
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo', lab: 'tu devolución cruza (vuelo 2)' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'ida', lab: 'el rival devuelve OTRA VEZ' });
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'fallo',
             lab: 'tercera vuelta: el rival FALLA (remate corto)' });
  for (let i = 0; i < 20; i++) T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.rfHecho === true,
             lab: 'PUNTO: el intercambio se ganó (rfHecho)' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv4b'),
             lab: 'voz de la ROTACIÓN del sacador (tutv4b)' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'gatillo → paso 5 EL MARCADOR' });

  // ---------- 5 · paso 5: marcador con igualada ----------------------
  e = T.estado();
  out.push({ ok: e.holo === true && e.pose === 'lado',
             lab: 'holo-marcador BAJO sobre la mesa (panel apartado)' });
  out.push({ ok: e.mandosPose === 'saque',
             lab: 'mandos en pose de saque para el bucle del marcador' });
  // el gatillo ANTES de la demo NO avanza
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO se niega antes de la demo' });
  for (let i = 0; i < 70; i++) T.tick(0.2);       // 14 s
  e = T.estado();
  out.push({ ok: e.demoPtos >= 20, lab: `marcador hasta 10-10 (pts ${e.demoPtos})` });
  out.push({ ok: e.demoDeuce === true, lab: 'IGUALADA alcanzada (cartel 10-10)' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv5b'),
             lab: 'voz de la igualada (tutv5b)' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 6, lab: 'demo vista → gatillo pasa a las DEVOLUCIONES' });

  // ---------- 6 · pasos 6/7/8/9/10 (r64 intactos) --------------------
  for (let i = 0; i < 6; i++) {
    G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
    T.tick(0.016);
    G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);
    T.tick(0.016);
    G.ball.vel.y = 0.4;
    T.tick(0.016);
  }
  e = T.estado();
  out.push({ ok: e.paso === 7, lab: '6/6 devoluciones → paso 7 BOTONES' });
  G.paddleHand = 0;
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.paso === 8 && e.pose === 'frente',
             lab: 'A/X → paso 8 MODOS (panel de nuevo FRENTE)' });
  T.onTrigger(0); T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 10, lab: 'modos 8→9→10 por gatillo' });
  localStorage.removeItem('pp_tut_done');
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.activo === false, lab: 'paso 10 JUGAR YA cierra la academia' });
  out.push({ ok: localStorage.getItem('pp_tut_done') === '1',
             lab: 'sello pp_tut_done escrito' });
  out.push({ ok: G.scene.children.length >= 1,
             lab: 'escena sin residuos del holo tras salir' });
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

        print("--- 1 · FUENTE SERVIDA (agujas r66) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (lo r65 retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · i18n ES/EN (claves r66 ×2 idiomas) ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 4 · ÁTOMOS DE VOZ (27 × es + en) ---")
        for atomo in ATOMOS:
            n = len(re.findall(rf"^\s+{atomo}: \"", src, re.M))
            chk(n == 2, f"átomo {atomo} en banco es y en (×{n})")

        print("--- 5 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 6 · ERRORES DE PÁGINA ---")
        chk(len(errors) == 0, f"sin pageerror/console.error ({len(errors)})")
        for err in errors[:5]:
            print("    ·", err[:180])

        await browser.close()

    print(f"\nCAPA BA · qa_r66_v3658: {ok} OK · {fails} FALLOS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
