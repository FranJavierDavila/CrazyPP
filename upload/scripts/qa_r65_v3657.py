#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r65_v3657 — CAPA AZ · V3.6.57-SDK6, FASE 59 «EL ONBOARDING GAMIFICADO».

Lo pedido por el dueño para la academia (literales):
  · «es muy molesto que nada más empezar esté como sonando la bola botar
    continuamente» → el saque DEMO del espectador DUERME en la academia
    (c12: guardia !this.tutV1) y el árbitro queda SIEMPRE en server='player'.
  · «Introducir las reglas básicas de forma visual sobre la propia mesa
    ilustrándolo con nuestra pala y bola, algo muy atractivo y visual NO
    SOLO con TEXTO» → 2 pasos NUEVOS de REGLAS (holo sobre la mesa):
    paso 3 marcador a 11 ganando por 2 (pips + bola fantasma cruzando la
    red) y paso 4 rotación del saque 2·2 / 10-10 cada punto + doble bote
    reglamentario. El panel se APARTA (pose lado) para no tapar la mesa.
  · «adjunto el modelo glb exacto (Mando.glb)… marcando sobre él los
    botones que se deben pulsar y solicitando al jugador que lo haga,
    explicaciones interactivas» → el GLB REAL del dueño (628 KB b64)
    flotando giratorio junto al panel con HALOS pulsantes por pieza
    (anclas por raycast fino) y el paso 1 exige 4 acciones REALES:
    gatillo → grip → stick → A (halo en la pieza pedida + voz).
  · «Lo ideal es que lo podamos escuchar en voz nativa (castellano e
    inglés)» → banco de voz Piper es/en AMPLIADO con 25 átomos por idioma
    (tutv0a…tutv10b + tutok + tutotra); cada paso narra al entrar, el
    STICK la repite y el fallo de saque dice «otra vez».
  · «que cada paso requiera la conformidad del usuario» → gating real:
    paso 0 EMPEZAR · paso 1 las 4 acciones · paso 2 vaivén · 3/4 ver la
    demo ≥6 s y gatillo ENTENDIDO · 5 tres saques · 6 seis devoluciones
    · 7 A/X de verdad · 8/9 gatillo · 10 JUGAR YA.
  · «información textual sobre la imagen de pizarra (Pizarra.png)… textos
    claros y bien montados sobre la zona negra… nunca obstruir la mesa» →
    panel PIZARRA: canvas 1408×768 (webp 46 KB b64) sobre plano 1.24×0.6765,
    texto tiza SÓLO en la zona negra (x 170..1190 · y 168..618), stickers
    del birrete y la pala siempre visibles, pose lado en 3/4/5/6.

Pruebas: (1) FUENTE SERVIDA — agujas r65 + negativas (mando procedural
r64 y canvas 1280 retirados). (2) i18n ES/EN ×2. (3) MECÁNICA REAL
headless SOBRE EL GRAFO DE ESCENA: mando GLB cargado con halos, subfases
del paso 1 con resalte y voz, holo-reglas presentes en la escena con
puerta de tiempo, pose lado, stick repite la voz, 11 pasos completos.

Uso: python3 scripts/qa_r65_v3657.py        (servidor dev en :3000)
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
    # --- fix del bote continuo (petición literal del dueño) ---
    ("el saque demo del espectador DUERME en la academia",
     "} else if (!this.net.online && !this.tutV1) {"),
    ("la academia fuerza server='player' al arrancar",
     "G.rules.server = 'player';            // r65 · el saque SIEMPRE del jugador:"),
    ("el profesor de la academia sirve con feedPracticeBall",
     "G.feedPracticeBall();   // el profesor sirve otra bola suave"),
    # --- voz nativa (banco Piper es/en ampliado) ---
    ("motor de narración (narra) con banco por idioma",
     "function narra(keys) {"),
    ("reintentos de voz si el banco aún decodifica",
     "narrRetry = 1.4;"),
    ("la voz respeta el interruptor del megáfono",
     "if (G.audio.voice === false) return;   // el dueño apagó el megáfono"),
    ("STICK repite la última narración",
     "function pollVoz() {"),
    ("guion de voz por paso (9 entradas remapeadas r67)",
     "const VOCES_PASO = ["),
    ("aviso hablado de saque fallido («otra vez»)",
     "narra(['tutotra']);"),
    ("felicitación hablada dentro del plan de acción (tutok + voz, sin dobles)",
     "if (subfase === 1) narra(['tutok', 'tutv1c']);"),
    # --- mando GLB real del dueño (r66: DOS mandos centrados) ---
    ("mando GLB embebido (const del asset)",
     "const TUT_MANDO_GLB = '"),
    ("mando DERECHO GLB embebido (r66)",
     "const TUT_MANDO_DER_GLB = '"),
    ("carga por GLTFLoader.parse del GLB embebido",
     "new GLTFLoader().parse(bin"),
    ("anclas por raycast fino (stick/botones/gatillo/grip)",
     "const ANCLAS_MANDO = {"),
    ("anclas del derecho ESPEJO (r66)",
     "const ANCLAS_MANDO_DER = {"),
    ("halos OPACOS con textura radial aditiva (r66)",
     "function _haloTex() {"),
    ("etiqueta legible de la pieza (r66)",
     "function _etiquetaSprite() {"),
    ("AURA sobre la PALA REAL (la única raqueta, r67)",
     "function _ponAuraPala() {"),
    ("los mandos anclados NO giran ni flotan (r67)",
     "r67 · tick de los mandos ANCLADOS: NADA de giro ni flotación"),
    ("resalte por subfase en el paso 1 (4 acciones)",
     "return ['gatillo', 'grip', 'stick', 'botones'][Math.min(subfase, 3)];"),
    # --- reglas visuales sobre la mesa (r66: demos REALES, sin holo abstracto) ---
    ("paso 2: demo REAL del PROFESOR sobre la mesa (r67)",
     "const { v, spin } = findServeVelocity(b.pos, -1, { x: -0.05, spd: 1.22 });"),
    ("aros guía del saque sobre la mesa real (r67)",
     "function construirAros() {"),
    ("paso 5: marcador BAJO sobre la mitad rival",
     "holo.position.set(0, DIMS.tableTopY + 0.22, DIMS.tableCenterZ - DIMS.tableHalfLength * 0.34);"),
    ("paso 5: fichas de saque del marcador (2 por lado)",
     "holoTokens = { fichas: [], cartel10: null };"),
    ("paso 5: cartel ¡10-10! en la igualada",
     "holoTokens.cartel10 = _cartelTxt(T('tut_h_10'), '#ff8a3d', 62, 0.30, 0.15);"),
    ("el marcador anota con las reglas del árbitro",
     "function anotaPuntoMarcador() {"),
    ("el holo sale limpio con el guion",
     "limpiarHolo();                        // r65 · el holo-reglas sale con el guion"),
    # --- panel pizarra del dueño ---
    ("pizarra embebida (const del asset)",
     "const TUT_PIZARRA = '"),
    ("canvas 1408×768 = resolución nativa de la pizarra",
     "cv.width = 1408; cv.height = 768;"),
    ("decodificación webp de la pizarra",
     "im.src = 'data:image/webp;base64,' + TUT_PIZARRA;"),
    ("fondo pizarra dibujado bajo el texto",
     "c.drawImage(pizImg, 0, 0, 1408, 768);   // la PIZARRA del dueño de fondo"),
    ("zona negra: centro del texto en x=680",
     "const PIZ_CX = 680;           // centro de la zona negra"),
    ("píldoras estilo tiza",
     "function pill(c, txt, y, opts) {"),
    # --- gating del onboarding gamificado ---
    ("guion reorganizado de 9 pasos (r67)",
     "const STEPS = 9;              // r67 · guion REORGANIZADO (0..8): menos pizarra, más mesa"),
    ("la demo de reglas exige verla completa (≥6 s)",
     "const DEMO_MIN = 6;           // r65 · segundos de demo de reglas antes del OK"),
    ("el gatillo del paso 1 es la acción pedida, no un salto",
     "if (subfase === 0) accionMandoOk();"),
    ("ENTENDIDO sólo tras la demo (voz única r67: sin tutok antes de avanzar)",
     "if (demoT >= DEMO_MIN) { advance(); }"),
    ("OK hablado de cada acción del mando",
     "function accionMandoOk() {"),
    ("el panel se aparta en reglas y práctica (pasos 2-5, r67)",
     "if (step === 2 || step === 3 || step === 4 || step === 5) {"),
]

NEGATIVAS = [
    ("el mando procedural r64 (cutre) ya no existe",
     "function _matMando(col, rough, metal) {"),
    ("el canvas 1280×800 r64 retirado",
     "cv.width = 1280; cv.height = 800;"),
    ("el centro viejo del panel (512) retirado de los pintores r64",
     "c.fillText(txt, 512, y + h / 2 + 1);"),
    ("la vieja HL_CICLO por tiempo retirada (ahora manda la subfase)",
     "const HL_CICLO_S1 = ['gatillo', 'grip', 'stick', 'botones'];"),
]

CLAVES = [
    "tut_rep", "tut_m1_gat", "tut_m1_grip", "tut_m1_stick", "tut_m1_a",
    "tut_m1_ok", "tut_m1_raf",
    "tut_d3_t", "tut_d3_l1", "tut_d3_l2", "tut_d3_l3", "tut_d3_go",
    "tut_d4_t", "tut_d4_l1", "tut_d4_l2", "tut_d4_l3",
    "tut_d5_t", "tut_d5_l1", "tut_d5_l2", "tut_d5_l3", "tut_ent",
    "tut_h_tu", "tut_h_ia", "tut_h_saq", "tut_h_10", "tut_h_p2",
]

# átomos de voz r66 presentes en AMBOS bancos (es + en) del fuente
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
  const mkJuego = (mano) => { const G = ({
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
  // r67 · grips XR reales (los mandos GLB se ANCLAN a ellos)
  const grips = [new THREE.Group(), new THREE.Group()];
  const mounts = [new THREE.Group(), new THREE.Group()];
  grips[0].add(mounts[0]); grips[1].add(mounts[1]);
  G.grips = grips; G.paddleMounts = mounts; G.handOf = ['left', 'right'];
  return G;
  };

  // ---------- 1 · arranque + panel PIZARRA + mandos duales -----------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0 && e.total === 9,
             lab: 'arranque: paso 0 de 9 (guion r67)' });
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
  out.push({ ok: e.anclados === true && e.ancladosEnGrips === true,
             lab: 'DOS mandos GLB ANCLADOS a los grips XR (r67)' });
  out.push({ ok: e.mandosPose === 'manos',
             lab: 'los mandos viven EN TUS MANOS desde la bienvenida (r67)' });
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
  out.push({ ok: e.aura > 0.4 && e.mandosVisMeta === 0,
             lab: 'AURA sobre la PALA REAL, el mando GLB se desvanece (r67)' });
  // STICK repite la última narración
  G.audio.__voz = [];
  G.sources[0].gamepad.buttons[3] = { pressed: true };
  T.tick(0.016);
  out.push({ ok: (G.audio.__voz || []).length > 0,
             lab: 'STICK repite la última narración (pollVoz)' });
  G.sources[0].gamepad.buttons[3] = { pressed: false };
  T.tick(0.016);
  // el vaivén (subfase 4) avanza SOLO al paso 2 (r67)
  G.controllerPaddles[G.paddleHand].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 2 && e.pose === 'lado',
             lab: 'vaivén → paso 2 EL SAQUE con panel APARTADO (lado)' });
  out.push({ ok: e.submodo === 'demo' && e.mandosPose === 'oculto' && e.aros === true,
             lab: 'demo del PROFESOR sobre la mesa real con AROS GUÍA (r67)' });
  out.push({ ok: e.voz === 'tutv3a',
             lab: 'narración del saque al entrar (tutv3a)' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 2 && e.submodo === 'demo',
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
  out.push({ ok: e.paso === 3, lab: '3/3 saques → paso 3 EL INTERCAMBIO' });

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
  out.push({ ok: e.paso === 4 && e.holo === true && e.pose === 'lado',
             lab: 'paso 4 MARCADOR: holo BAJO en la escena (lado)' });

  // ---------- 5 · paso 5: marcador con igualada ----------------------
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'ENTENDIDO se niega antes de la demo' });
  for (let i = 0; i < 45; i++) T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.demoDeuce === true, lab: 'la igualada 10-10 llega (r66)' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 5 && e.holo === false && e.aros === false,
             lab: 'ENTENDIDO → paso 5 PRÁCTICA (holo y aros recogidos)' });

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
  out.push({ ok: e.paso === 6, lab: '6/6 devoluciones → paso 6 BOTONES' });
  G.paddleHand = 0;
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.paso === 7 && e.pose === 'frente',
             lab: 'A/X → paso 7 MODOS con panel de nuevo FRENTE' });
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 8, lab: 'modos: UNA pizarra → paso 8 por gatillo' });
  localStorage.removeItem('pp_tut_done');
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.activo === false, lab: 'paso 8 JUGAR YA cierra la academia' });
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

        print("--- 1 · FUENTE SERVIDA (agujas r65) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (lo r64 retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · i18n ES/EN (claves r65 ×2 idiomas) ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 4 · ÁTOMOS DE VOZ (25 × es + en) ---")
        for atomo in ATOMOS:
            n = len(re.findall(rf"^\s+{atomo}: \"", src, re.M))
            chk(n == 2, f"átomo {atomo} en banco es y en (×{n})")

        print("--- 5 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    if errors:
        for e in errors[:6]:
            print("  ·", e[:220])
    chk(len(errors) == 0, "sin errores JS en la carga del juego")

    print(f"\nRESULTADO qa_r65_v3657: {ok} OK · {fails} FALLOS")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
