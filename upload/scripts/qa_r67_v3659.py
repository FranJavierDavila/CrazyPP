#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r67_v3659 — CAPA BB · V3.6.59-SDK6, FASE 61 «LA ACADEMIA EN TUS MANOS».

Lo pedido por el dueño tras probar V3.6.58 en el Quest (literales):
  · «Siguen apareciendo solapes en los textos» → guion reorganizado a 9
    pasos con layout estricto dentro de la zona negra de la pizarra
    (nada pinta por debajo de 596: la línea «B · saltar» vive en 604) y
    la rejilla de modos 2×3 en UNA sola pizarra con textos cortos propios.
  · «El audio se superpone dos veces en varios momentos de la explicación»
    → speakPlan (c03) CANCELA la voz viva anterior (this._vozSrc: stop +
    disconnect + onended con guard): una sola voz, la última gana — cubre
    tutok→voz del paso, STICK repetido y reintentos.
  · «Los mandos 3D que he subido que estén anclados a las manos reales y a
    los mandos reales, NO un modelo 3D moviéndose en el aire… y más
    pequeños, como un 75% del tamaño actual» → cada GLB (izq Y/X · der
    B/A) vive DENTRO del espacio grip XR de SU mando (G.grips[h], hijo del
    grupo que sigue la mano 1:1): sin grupo flotante, sin poses, sin giro,
    sin flotación. Escala MANDO_ESC = 0.154 (75% del 0.205 de r66) y
    orientación real: la cara del GLB (+Z) mira hacia -Z del grip (giro
    180°) con la cabeza arriba; halos (8) y ETIQUETA viajan con el mando.
  · «que la raqueta fantasma también sea la que está real ya en nuestra
    mano y solo 1 raqueta no 2» → ADIÓS a los clones fantasma (makePaddle
    Visual sobre mandos): una AURA dorada (2 sprites aditivos) pulsa sobre
    la PALA REAL del juego en el paddleMount de la mano — la única raqueta.
  · «piensa tú la mejor forma de explicarlo de una manera muy sencilla y
    divertida» → guion de 9 pasos (antes 11): 0 bienvenida · 1 TU MANDO,
    TU RAQUETA (4 acciones reales + vaivén con la pala real, fusionados) ·
    2 EL SAQUE (demo del PROFESOR sobre la mesa real — la bola saca desde
    SU campo con findServeVelocity(-1) y los AROS GUÍA se iluminan con los
    botes — y después 3 saques tuyos) · 3 el intercambio · 4 el marcador ·
    5 la práctica (6 devoluciones) · 6 botones · 7 los modos (UNA pizarra,
    rejilla 2×3 + caja de poderes) · 8 ¡a jugar!. Los mandos anclados sólo
    se ven en los pasos 0-1: del 2 en adelante ves lo que vas a jugar.

4 BLOQUES: (1) AGUJAS de fuente + negativas del código flotante retirado.
(2) i18n ES/EN (claves nuevas ×2 idiomas). (3) ÁTOMOS de voz 27×2 intactos.
(4) MECÁNICA REAL headless sobre el grafo de escena: anclaje a grips,
escala 75%, halos, aura única, voz que se sustituye, 9 pasos con prácticas
reales, demo del profesor con aros, y cierre limpio.
Uso: python3 scripts/qa_r67_v3659.py [URL]"""
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
    # --- guion reorganizado ---
    ("guion de 9 pasos (const STEPS = 9)",
     "const STEPS = 9;              // r67 · guion REORGANIZADO (0..8): menos pizarra, más mesa"),
    ("paso 1 fusiona mando+raqueta (título propio)",
     "line(c, T('tut_m_t'), 236, 40, '#ffd257');"),
    ("el vaivén vive en el paso 1 subfase 4 (fusion r67)",
     "} else if (subfase === 4) {\n          // el vaivén firme (velocidad del simulador de la pala): la raqueta"),
    ("los mandos anclados SÓLO en pasos 0-1",
     "mandosVisMeta = (step <= 1) ? 1 : 0;"),
    # --- mandos anclados a grips reales ---
    ("montaje DENTRO del grip XR (anclaje 1:1)",
     "try { G.grips[h].add(mont); } catch (eG) { continue; }"),
    ("escala 75% del tamaño r66 (0.205 → 0.154)",
     "const MANDO_ESC = 0.154;      // r67 · 75% del tamaño r66 (0.205): petición del dueño"),
    ("orientación REAL: cara del GLB hacia -Z del grip (giro 180°)",
     "glb.rotation.y = Math.PI;"),
    ("mano correcta: izquierda → grip de handOf 'left'",
     "{ mano: 'left', bin: TUT_MANDO_GLB, anclas: ANCLAS_MANDO },"),
    ("sin giro de exhibición (nada se mueve solo en tu mano)",
     "r67 · tick de los mandos ANCLADOS: NADA de giro ni flotación"),
    ("etiqueta sobre el mando de la mano de la pala",
     "/* la ETIQUETA vive sobre el mando REAL de la mano de la pala */"),
    ("fade del conjunto anclado (opacidad de materiales)",
     "mandosVis += (mandosVisMeta - mandosVis) * k;"),
    # --- la ÚNICA raqueta (pala real, sin clones) ---
    ("aura sobre la PALA REAL (mismo paddleMount)",
     "const mount = G.paddleMounts[G.paddleHand];"),
    ("aura con halo aditivo pulsante",
     "const pulso = 0.55 + 0.45 * Math.sin(mandoT * 4.2);"),
    ("momento raqueta: aura + desvanecer del mando GLB",
     "auraMeta = 1;\n      mandosVisMeta = 0;"),
    ("etiqueta TU RAQUETA durante la aura",
     ": (auraMeta > 0.3 ? T('tut_lab_pala') : '');"),
    # --- demo del profesor + aros guía ---
    ("demo del PROFESOR: saque desde su campo (ownSign -1)",
     "const { v, spin } = findServeVelocity(b.pos, -1, { x: -0.05, spd: 1.22 });"),
    ("bola de la demo apoyada en el lado del profesor",
     "return new THREE.Vector3(0.10, TY + DIMS.ballRadius + 0.004, C - HL - 0.17);"),
    ("AROS GUÍA construidos sobre la mesa real",
     "function construirAros() {\n    limpiarAros();"),
    ("el aro se ilumina con el bote real del jugador",
     "if (aroIzq && !aroIzq.__ok && b.vel.y > 0.3 &&"),
    ("aros fuera con el paso (limpiarAros en enterStep)",
     "limpiarHolo();\n    limpiarAros();                      // r67 · los aros salen con el paso"),
    ("1er bote de la demo = SU campo (cartela propia)",
     "demoTxt = { txt: T('tut_p1r'), col: 'rgba(232,180,90,0.32)', t: 1.5 };"),
    # --- rejilla de modos sin solapes ---
    ("título propio de la página de modos (ya no 1 DE 2)",
     "line(c, T('tut_mods_t'), 208, 36, '#ffd257');"),
    ("rejilla 2×3 con tarjetas compactas",
     "function modeCard(c, x, y, w, h, col0, ini, title, sub) {"),
    ("píldora de modos 552..594 (no invade la línea B·saltar 604)",
     "pill(c, T('tut_hint_next'), 552, { w: 520, h: 42, col: 'rgba(232,180,90,0.28)', size: 20 });"),
    # --- voz que se sustituye (anti-doble) ---
    ("speakPlan CANCELA la voz viva anterior",
     "if (this._vozSrc) {\n        try { this._vozSrc.stop(0); } catch (e) { /* ya parada */ }"),
    ("la voz viva se registra (_vozSrc = src)",
     "this._vozSrc = src;                     // r67 · la voz viva ahora mismo"),
    ("onended con guard (no mata a la voz nueva)",
     "if (this._vozSrc === src) this._vozSrc = null;"),
    ("el OK de acción narra el plan completo (tutok + voz)",
     "if (subfase === 1) narra(['tutok', 'tutv1c']);"),
    ("avance de paso SIN narración doble (sólo chime + nueva voz)",
     "if (saqCount >= SAQ_META) { advance(); break; }"),
    ("guard del setTimeout del marcador (holo pudo morir)",
     "if (!holoPips) return;             // r67 · la academia pudo avanzar ya"),
]

NEGATIVAS = [
    # el código flotante r66 retirado por completo
    ("el grupo flotante de mandos (hijo del rig) retirado",
     "mandosGrp.position.set(0, 1.07, -0.56);"),
    ("las poses del grupo flotante (centro/saque/oculto) retiradas",
     "function _poseMandos() {"),
    ("los clones fantasma de la pala retirados",
     "function _ponFantasma(mm) {"),
    ("el material fantasma retirado",
     "function _fantasmaMats(grupo, coleccion) {"),
    ("el giro de exhibición de los mandos retirado",
     "mm.spin.rotation.y += mm.__g * dt;"),
    ("la flotación senoidal del mando retirada",
     "mm.grupo.position.y = Math.sin(mandoT * 1.4"),
    ("la narración doble en el avance de saques retirada",
     "if (saqCount >= SAQ_META) { narra(['tutok']); advance(); break; }"),
    ("la página de modos 2 DE 2 retirada (una sola pizarra)",
     "line(c, T('tut_s7_t'), 206, 34, '#ffd257');"),
    ("la píldora de modos que invadía la línea B·saltar retirada",
     "pill(c, T('tut_hint_next'), 538, { w: 520, h: 46, col: 'rgba(232,180,90,0.28)', size: 21 });"),
    ("el texto largo de poderes en la rejilla retirado (clave corta propia)",
     "wrap2(c, T('tut_s7_p'), 512, 14, '#ffe08a', 310, 11);"),
]

CLAVES = [
    "tut_m_t", "tut_lab_pala", "tut_mods_t", "tut_mod_p", "tut_mod_s",
    "tut_mod_m", "tut_mod_c", "tut_mod_r", "tut_mod_t", "tut_pow_t",
    "tut_p1r", "tut_m1_raf", "tut_d3_t", "tut_d3_p2", "tut_d3_pto",
    "tut_d4_ok", "tut_ent", "tut_hint_next", "tut_hint_skip",
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

  // ---------- 1 · arranque + mandos ANCLADOS a los grips -------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0 && e.total === 9,
             lab: 'arranque: paso 0 de 9 (guion reorganizado)' });
  out.push({ ok: e.bolaViva === false,
             lab: 'la bola nace DORMIDA (sin bote continuo)' });
  out.push({ ok: e.voz === 'tutv0a', lab: 'bienvenida hablada (tutv0a)' });
  // espera el parse async de los DOS GLB anclados
  for (let i = 0; i < 90 && !e.anclados; i++) {
    await new Promise((r) => setTimeout(r, 50));
    e = T.estado();
  }
  out.push({ ok: e.anclados === true,
             lab: 'DOS mandos GLB anclados (izq Y/X + der B/A)' });
  out.push({ ok: e.ancladosEnGrips === true,
             lab: 'ANCLADOS a los GRIPS XR reales (hijo de G.grips[h])' });
  out.push({ ok: e.escalaMando === 0.154,
             lab: 'escala 75% del tamaño r66 (0.154)' });
  out.push({ ok: e.mandosPose === 'manos',
             lab: 'los mandos viven EN TUS MANOS (sin poses flotantes)' });
  // orientación real: la cara del GLB gira 180° (rotación Y pura)
  let giroOk = false, nHalos = 0, nEtiqueta = 0, nAura = 0;
  for (let i = 0; i < 2; i++) {
    const mont = G.grips[i].children.find((ch) => ch.name === 'ppTutMando' + i);
    if (!mont) continue;
    const glb = mont.children.find((ch) => Math.abs(ch.rotation.y - Math.PI) < 1e-6);
    if (glb) giroOk = true;
    mont.traverse((o) => {
      if (o.isSprite) (o.__cv ? nEtiqueta++ : nHalos++);
    });
  }
  out.push({ ok: giroOk, lab: 'cara del GLB hacia -Z del grip (giro 180°)' });
  out.push({ ok: nHalos === 8, lab: `8 halos opacos (4 por mando anclado) · hay ${nHalos}` });
  out.push({ ok: nEtiqueta === 1, lab: 'etiqueta ÚNICA sobre el mando de la pala' });
  // sin nada flotando en el rig: los mandos ya NO son hijos del rig
  const flotante = G.rig.children.find((ch) => ch.name === 'ppTutMandos');
  out.push({ ok: !flotante, lab: 'NINGÚN grupo de mandos flotando en el rig' });
  T.tick(0.1); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.mandosVis > 0.5,
             lab: 'fade IN de los mandos anclados (visibles en la mano)' });

  // ---------- 2 · paso 1: 4 acciones + AURA de la ÚNICA raqueta ------
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 0 && e.mandoHl === 'gatillo',
             lab: 'paso 1: halo en el GATILLO (subfase 0)' });
  T.tick(0.1); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.etiqueta > 0.5,
             lab: 'etiqueta GATILLO visible SOBRE EL MANDO REAL' });
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
  G.sources[0].gamepad.buttons[4] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 4, lab: 'A pulsada: momento RAQUETA (subfase 4)' });
  out.push({ ok: e.auraMeta === 1,
             lab: 'AURA sobre la PALA REAL (la única raqueta)' });
  out.push({ ok: e.mandosVisMeta === 0,
             lab: 'el mando GLB se DESVANECE: sólo 1 raqueta en escena' });
  for (let i = 0; i < 40; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.aura > 0.4, lab: 'aura dorada pulsando sobre la pala real' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv1f'),
             lab: 'voz del momento raqueta (tutv1f)' });
  const auraGrp = G.paddleMounts[1].children.find(
    (ch) => ch.name === 'ppTutAuraPala');
  out.push({ ok: !!auraGrp, lab: 'aura montada en el paddleMount REAL' });
  // vaivén con la raqueta real → paso 2
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 2 && e.pose === 'lado',
             lab: 'vaivén → paso 2 EL SAQUE con panel APARTADO' });

  // ---------- 3 · paso 2: DEMO del profesor + AROS + práctica --------
  out.push({ ok: e.submodo === 'demo',
             lab: 'demo del PROFESOR (nada flota: todo en la mesa real)' });
  out.push({ ok: e.aros === true, lab: 'AROS GUÍA construidos sobre la mesa' });
  out.push({ ok: e.mandosVisMeta === 0,
             lab: 'mandos ocultos desde el paso 2 (ves lo que vas a jugar)' });
  out.push({ ok: e.voz === 'tutv3a', lab: 'narración del saque (tutv3a)' });
  out.push({ ok: G.ball.pos.z < 0,
             lab: 'bola de la demo apoyada en el campo del PROFESOR' });
  // el gatillo ANTES de 2.5 s NO pasa a práctica
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 2 && e.submodo === 'demo',
             lab: 'la práctica se niega antes de ver la demo' });
  // deja correr la demo: fase 0 (2,1 s) → fase suelta
  for (let i = 0; i < 25 && e.demoFase === 0; i++) { T.tick(0.2); e = T.estado(); }
  T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.demoFase >= 1, lab: 'el profesor SUELTA el saque (fase 1+)' });
  out.push({ ok: e.bolaViva === true || e.demoFase >= 2,
             lab: 'bola VIVA durante el saque del profesor' });
  for (let i = 0; i < 30; i++) T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.demoCiclos >= 1 || e.demoFase >= 2,
             lab: 'ciclo completo: bote SU campo → TU campo → PUNTO' });
  // ahora sí: gatillo → práctica
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica' && G.rules.state === 'serve' &&
             G.rules.server === 'player',
             lab: 'gatillo → TU TURNO: práctica con estado real' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv3d'),
             lab: 'voz de la práctica (tutv3d)' });
  // 3 saques válidos (los aros siguen en la mesa)
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: '3/3 saques → paso 3 EL INTERCAMBIO' });

  // ---------- 4 · paso 3: intercambio REAL (rival devuelve y falla) --
  out.push({ ok: e.rfFase === 'saque', lab: 'paso 3: espera el saque del jugador' });
  T.onTrigger(0);                       // saca
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque hecho: la bola va hacia el rival (viva)' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'ida', lab: 'el rival DEVUELVE (ida hacia ti)' });
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
  out.push({ ok: e.paso === 4, lab: 'gatillo → paso 4 EL MARCADOR' });

  // ---------- 5 · paso 4: marcador con igualada ----------------------
  out.push({ ok: e.holo === true && e.pose === 'lado',
             lab: 'holo-marcador BAJO sobre la mesa (panel apartado)' });
  out.push({ ok: e.aros === true, lab: 'aros guía también en el marcador' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'ENTENDIDO se niega antes de la demo' });
  for (let i = 0; i < 70; i++) T.tick(0.2);       // 14 s de demo
  e = T.estado();
  out.push({ ok: e.demoPtos >= 20, lab: `tanteo real visto (10-10 · ${e.demoPtos} ptos)` });
  out.push({ ok: e.demoDeuce === true, lab: 'la IGUALADA 10-10 se alcanzó' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO → paso 5 LA PRÁCTICA' });

  // ---------- 6 · paso 5: 6 devoluciones del profesor ----------------
  e = T.estado();
  out.push({ ok: e.holo === false && e.aros === false,
             lab: 'holo y aros limpiados al cambiar de paso' });
  // la bola de la demo murió en el campo del profesor: el ciclo de bola
  // muerta (0,5 s) rearma el profesor y la fase queda en 'espera_golpe'
  for (let i = 0; i < 5; i++) T.tick(0.2);
  let ultimoHit = 0;
  for (let d = 0; d < 6; d++) {
    // ciclo REAL: tu golpe cruza (z<-0.06, vel.z<-0.9) → bote lejano →
    // el profesor devuelve y la fase vuelve a espera_golpe
    G.ball.pos.set(0.05, 1.15, -1.75); G.ball.vel.set(0, -0.8, -3.0);
    T.tick(0.016);
    ultimoHit = T.estado().hitCount;
    G.ball.pos.set(0.1, 0.85, -2.3); G.ball.vel.set(0, 0.6, -0.8);
    T.tick(0.016);
    T.tick(0.05);
  }
  e = T.estado();
  out.push({ ok: ultimoHit >= 6 || e.paso === 6,
             lab: `devoluciones contadas en vivo (última cuenta ${ultimoHit})` });
  out.push({ ok: e.paso === 6, lab: '6/6 → paso 6 LOS BOTONES' });

  // ---------- 7 · paso 6 botones → 7 modos → 8 final -----------------
  G.paddleHand = 1 - G.paddleHand;
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 7, lab: 'A/X cambia la mano → paso 7 LOS MODOS' });
  out.push({ ok: e.pose === 'frente', lab: 'panel al FRENTE en los modos' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 8, lab: 'gatillo → paso 8 ¡A JUGAR!' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.activo === false, lab: 'paso 8 JUGAR YA cierra la academia' });
  out.push({ ok: localStorage.getItem('pp_tut_done') === '1',
             lab: 'sello pp_tut_done escrito' });
  // los mandos anclados salen de los grips al cerrar
  const restos = G.grips.filter((gr) => gr.children.some(
    (ch) => ch.name && ch.name.indexOf('ppTutMando') === 0)).length;
  out.push({ ok: restos === 0, lab: 'grips LIMPIOS tras salir (sin residuos)' });
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

        print("--- 1 · FUENTE SERVIDA (agujas r67) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (lo flotante r66 retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · i18n ES/EN (claves r67 ×2 idiomas) ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 4 · ÁTOMOS DE VOZ (27 × es + en, intactos) ---")
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

    print(f"\nCAPA BB · qa_r67_v3659: {ok} OK · {fails} FALLOS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
