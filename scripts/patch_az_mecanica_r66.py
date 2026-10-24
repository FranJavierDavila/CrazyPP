#!/usr/bin/env python3
"""r66 · Reescribe la MECÁNICA de la capa AZ (qa_r65_v3657) al flujo de la
academia r66: mandos duales, fantasma, paso 3 (demo real + práctica),
paso 4 (intercambio real), paso 5 (marcador) y salida limpia. Mantiene el
enfoque de AZ (voz, poses, holo, gating)."""
import re

F = "/home/z/my-project/scripts/qa_r65_v3657.py"
src = open(F, encoding="utf-8").read()

i = src.index('MECANICA = """')
j = src.index('"""', i + 20)

NUEVA = r'''MECANICA = """async () => {
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
  });

  // ---------- 1 · arranque + panel PIZARRA + mandos duales -----------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0 && e.total === 11,
             lab: 'arranque: paso 0 de 11' });
  out.push({ ok: G.rules.server === 'player',
             lab: 'el árbitro queda en server=player' });
  out.push({ ok: e.voz === 'tutv0a',
             lab: 'la bienvenida SUENA al entrar (voz tutv0a)' });
  const panel = G.rig.children.find((ch) => ch.type === 'Group' &&
    Math.abs(ch.position.y - 1.52) < 0.01 && ch.children.length > 0);
  out.push({ ok: !!panel, lab: 'panel en el rig (huella r63 intacta)' });
  for (let i = 0; i < 80 && !e.dosMandos; i++) {
    await new Promise((r) => setTimeout(r, 50));
    e = T.estado();
  }
  out.push({ ok: e.mandos && e.dosMandos,
             lab: 'DOS mandos GLB del dueño cargados (r66)' });
  out.push({ ok: e.mandosPose === 'centro',
             lab: 'mandos CENTRADOS desde la bienvenida (r66)' });
  T.tick(0.05);
  out.push({ ok: T.estado().mandoHl === null,
             lab: 'paso 0 (bienvenida) sin pieza resaltada' });

  // ---------- 2 · paso 1: 4 ACCIONES reales + FANTASMA ---------------
  T.onTrigger(0);                                  // paso 0 → 1
  T.tick(0.1); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 0 && e.mandoHl === 'gatillo',
             lab: 'paso 1: halo en el GATILLO (subfase 0)' });
  out.push({ ok: e.etiqueta > 0.5,
             lab: 'etiqueta de la pieza visible (r66)' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 1 && e.mandoHl === 'grip',
             lab: 'gatillo hecho → halo en el GRIP' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv1c'),
             lab: 'la voz guía la acción siguiente (tutv1c)' });
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
  out.push({ ok: e.subfase === 4 && e.mandoHl === null,
             lab: 'A pulsada: mandos dominados (subfase 4)' });
  for (let i = 0; i < 30; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.fantasma === true,
             lab: 'RAQUETA FANTASMA visible (r66)' });
  // STICK repite la última narración
  G.audio.__voz = [];
  G.sources[0].gamepad.buttons[3] = { pressed: true };
  T.tick(0.016);
  out.push({ ok: (G.audio.__voz || []).length > 0,
             lab: 'STICK repite la última narración (pollVoz)' });
  G.sources[0].gamepad.buttons[3] = { pressed: false };
  T.tick(0.016);
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 2, lab: 'paso 1 → 2 (la pala) tras las 4 acciones' });

  // ---------- 3 · paso 2 vaivén → paso 3 DEMO SOBRE LA MESA ----------
  G.controllerPaddles[G.paddleHand].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.pose === 'lado',
             lab: 'vaivén → paso 3 EL SAQUE con panel APARTADO (lado)' });
  out.push({ ok: e.submodo === 'demo' && e.mandosPose === 'saque',
             lab: 'demo de saque REAL con los mandos sobre la mesa (r66)' });
  out.push({ ok: e.voz === 'tutv3a',
             lab: 'narración del saque al entrar (tutv3a)' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.submodo === 'demo',
             lab: 'la práctica se niega antes de ver la demo' });
  for (let i = 0; i < 25 && e.demoFase === 0; i++) { T.tick(0.2); e = T.estado(); }
  T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.bolaViva === true,
             lab: 'bola VIVA en el vuelo de la demo (física real)' });
  for (let i = 0; i < 12; i++) T.tick(0.2);
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica' && G.rules.state === 'serve' &&
             G.rules.server === 'player' && e.pose === 'lado',
             lab: 'gatillo → TU TURNO: 3 saques con estado real (lado)' });
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saq === 1, lab: 'saque 1/3 contado (mecánica r64 intacta)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.3); T.tick(0.3);
  for (let s = 1; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: '3/3 saques → paso 4 EL INTERCAMBIO' });

  // ---------- 4 · paso 4: intercambio REAL (r66) ---------------------
  T.onTrigger(0);                       // saca
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque del paso 4 en vuelo (bola viva)' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'ida', lab: 'el rival devuelve' });
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);
  for (let i = 0; i < 20; i++) T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.rfHecho === true, lab: 'el rival FALLA: PUNTO (rfHecho)' });
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5 && e.holo === true && e.pose === 'lado',
             lab: 'paso 5 MARCADOR: holo BAJO en la escena (lado)' });

  // ---------- 5 · paso 5: marcador con igualada ----------------------
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO se niega antes de la demo' });
  for (let i = 0; i < 45; i++) T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.demoDeuce === true, lab: 'la igualada 10-10 llega (r66)' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 6 && e.holo === false,
             lab: 'ENTENDIDO → paso 6 DEVOLUCIONES (holo recogido)' });

  // ---------- 6 · pasos 6/7/8/9/10 y salida --------------------------
  G.ball.pos.set(0.3, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.7);
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
             lab: 'A/X → paso 8 MODOS con panel de nuevo FRENTE' });
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
}'''

src = src[:i] + NUEVA + src[j:]
open(F, "w", encoding="utf-8").write(src)
print("MECANICA de AZ reescrita al flujo r66")
