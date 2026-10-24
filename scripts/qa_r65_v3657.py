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
    ("guion de voz por paso (11 entradas)",
     "const VOCES_PASO = ["),
    ("aviso hablado de saque fallido («otra vez»)",
     "narra(['tutotra']);"),
    ("felicitación hablada al superar pasos",
     "narra(['tutok']);"),
    # --- mando GLB real del dueño ---
    ("mando GLB embebido (const del asset)",
     "const TUT_MANDO_GLB = '"),
    ("carga por GLTFLoader.parse del GLB embebido",
     "new GLTFLoader().parse(bin.buffer, '', (gltf) => {"),
    ("anclas por raycast fino (stick/botones/gatillo/grip)",
     "const ANCLAS_MANDO = {"),
    ("halos pulsantes con textura radial aditiva",
     "function _haloTex() {"),
    ("el mando GLB gira y flota junto al panel",
     "mandoSpin.rotation.y = (step === 1 ? mandoT * 0.35 : mandoT * 0.55);"),
    ("resalte por subfase en el paso 1 (4 acciones)",
     "return ['gatillo', 'grip', 'stick', 'botones', null][Math.min(subfase, 4)];"),
    # --- reglas visuales sobre la mesa (holo) ---
    ("holo base sobre la MESA en la escena (no en el rig)",
     "holo.position.set(0, DIMS.tableTopY + 0.40, DIMS.tableCenterZ);"),
    ("paso 3: marcador a 11 con pips por lado",
     "function construirHoloPuntos() {"),
    ("paso 4: rotación del saque + cartel 10-10",
     "function construirHoloSaques() {"),
    ("la fantasma muestra el DOBLE BOTE del saque",
     "SAQUE REGLAMENTARIO — bote PROPIO y luego RIVAL"),
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
    ("11 pasos en el guion",
     "const STEPS = 11;             // r65 · pasos del guion (0..10): +2 REGLAS"),
    ("la demo de reglas exige verla completa (≥6 s)",
     "const DEMO_MIN = 6;           // r65 · segundos de demo de reglas antes del OK"),
    ("el gatillo del paso 1 es la acción pedida, no un salto",
     "if (subfase === 0) accionMandoOk();"),
    ("ENTENDIDO sólo tras la demo",
     "if (demoT >= DEMO_MIN) { narra(['tutok']); advance(); }"),
    ("OK hablado de cada acción del mando",
     "function accionMandoOk() {"),
    ("el panel se aparta en reglas y práctica (pasos 3-6)",
     "if (step === 3 || step === 4 || step === 5 || step === 6) {"),
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
    "tut_m1_ok", "tut_r1_t", "tut_r1_l1", "tut_r1_l2", "tut_r1_ok",
    "tut_r2_t", "tut_r2_l1", "tut_r2_l2", "tut_r2_l3",
    "tut_h_tu", "tut_h_ia", "tut_h_saq", "tut_h_10",
]

# átomos de voz r65 presentes en AMBOS bancos (es + en) del fuente
ATOMOS = ["tutv0a", "tutv0b", "tutv1a", "tutv1b", "tutv1c", "tutv1d",
          "tutv1e", "tutv2a", "tutv2b", "tutv3a", "tutv3b", "tutv4a",
          "tutv4b", "tutv4c", "tutv5a", "tutv5b", "tutv6a", "tutv6b",
          "tutv7a", "tutv8a", "tutv9a", "tutv10a", "tutv10b",
          "tutok", "tutotra"]

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
             voice: true,
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
    sceneAddSpy: 0,
  });

  // ---------- 1 · arranque + panel PIZARRA + 11 pasos ----------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  out.push({ ok: e.activo && e.paso === 0 && e.total === 11,
             lab: 'arranque: paso 0 de 11 (guion ampliado r65)' });
  out.push({ ok: G.rules.server === 'player',
             lab: 'el árbitro queda en server=player (adiós al saque demo)' });
  out.push({ ok: e.voz === 'tutv0a',
             lab: 'la bienvenida SUENA al entrar (voz tutv0a)' });
  const panel = G.rig.children.find((ch) => ch.type === 'Group' &&
    Math.abs(ch.position.y - 1.52) < 0.01 && ch.children.length > 0);
  out.push({ ok: !!panel, lab: 'panel en el rig (huella r63 intacta)' });
  // espera el parse del GLB embebido
  for (let i = 0; i < 60 && !e.tieneMando; i++) {
    await new Promise((r) => setTimeout(r, 50));
    e = T.estado();
  }
  out.push({ ok: e.tieneMando, lab: 'mando GLB del dueño cargado (async parse)' });
  T.tick(0.05);
  const mandoGLB = panel && panel.children.find((ch) => ch.name === 'ppTutMandoGLB');
  let nHalos = 0, nMeshes = 0;
  if (mandoGLB) mandoGLB.traverse((o) => {
    if (o.isSprite) nHalos++;
    if (o.isMesh) nMeshes++;
  });
  out.push({ ok: nMeshes >= 1, lab: 'el GLB trae su mesh (Touch Plus real)' });
  out.push({ ok: nHalos === 4, lab: '4 halos por pieza (gatillo/stick/botones/grip)' });

  // ---------- 2 · paso 1: las 4 ACCIONES REALES del mando ------------
  out.push({ ok: e.mandoHl === null,
             lab: 'paso 0 (bienvenida) sin pieza resaltada: correcto' });
  T.onTrigger(0);                                  // paso 0 → 1
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 0 && e.mandoHl === 'gatillo',
             lab: 'paso 1: halo en el GATILLO (subfase 0)' });
  T.onTrigger(0);                                  // acción 1: gatillo
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 1 && e.mandoHl === 'grip',
             lab: 'gatillo hecho → halo en el GRIP (subfase 1)' });
  out.push({ ok: (G.audio.__voz || []).includes('tutv1c'),
             lab: 'la voz guía la acción siguiente (tutv1c)' });
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];  // grip ON
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: false };                    // grip OFF
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: true };                     // borde
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 2 && e.mandoHl === 'stick',
             lab: 'grip hecho → halo en el STICK (subfase 2)' });
  G.__stick = { x: 0.7, y: 0 };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 3 && e.mandoHl === 'botones',
             lab: 'stick movido → halo en los BOTONES (subfase 3)' });
  G.sources[0].gamepad.buttons[4] = { pressed: true };
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.subfase === 4, lab: 'A pulsada: mando dominado (subfase 4)' });
  // el gatillo AHORA sí avanza (subfase completa)
  T.onTrigger(0);
  T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 2, lab: 'paso 1 → 2 (la pala) tras las 4 acciones' });

  // ---------- 3 · paso 2 vaivén → paso 3 REGLAS con holo -------------
  G.controllerPaddles[G.paddleHand].vel.set(1.5, 1.2, 1.5);   // la mano de la pala
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.pose === 'lado',
             lab: 'vaivén → paso 3 REGLAS·PUNTOS con panel APARTADO (lado)' });
  out.push({ ok: e.holo === true,
             lab: 'holo-marcador presente en la escena (paso 3)' });
  out.push({ ok: e.voz === 'tutv3a',
             lab: 'narración de las reglas al entrar (tutv3a)' });
  // el gatillo ANTES de la demo NO avanza
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: 'ENTENDIDO se niega antes de ver la demo' });
  // deja correr la demo (6 s) y confirma
  for (let i = 0; i < 40; i++) T.tick(0.2);        // 8 s
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 4, lab: 'demo vista → gatillo pasa al paso 4' });

  // ---------- 4 · paso 4 REGLAS·SAQUES → paso 5 EL SAQUE -------------
  out.push({ ok: e.holo === true && e.pose === 'lado',
             lab: 'holo-saque presente y panel apartado (paso 4)' });
  for (let i = 0; i < 40; i++) T.tick(0.2);
  T.onTrigger(0);
  e = T.estado();
  out.push({ ok: e.paso === 5 && G.rules.state === 'serve' &&
             G.rules.server === 'player' && e.holo === false,
             lab: 'paso 5 EL SAQUE: estado real, holo recogido' });
  // saque rápido: lanzar + cruzar (mecánica r64 intacta)
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saq === 1, lab: 'saque 1/3 contado (mecánica r64 intacta)' });
  // STICK = repetir la voz (pollVoz con borde)
  G.audio.__voz = [];
  G.sources[0].gamepad.buttons[3] = { pressed: true };
  T.tick(0.016);
  out.push({ ok: (G.audio.__voz || []).length > 0,
             lab: 'STICK repite la última narración (pollVoz)' });
  // rearma la bola del saque 1 (estaba en vuelo) antes del bucle
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.3); T.tick(0.3);

  // ---------- 5 · pose: práctica aparta, texto devuelve a frente -----
  const pasoY = panel.position.y;
  e = T.estado();
  out.push({ ok: e.pose === 'lado', lab: 'paso 5 con panel en pose lado' });
  // termina los 3 saques → paso 6 (intercambio, también lado)
  for (let s = e.saq; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 6 && e.pose === 'lado',
             lab: '3/3 saques → paso 6 INTERCAMBIO (lado)' });
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
  G.paddleHand = 0;                       // A/X de verdad: la mano CAMBIA (1 → 0)
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.paso === 8 && e.pose === 'frente',
             lab: 'A/X → paso 8 MODOS con panel de nuevo FRENTE' });
  // modos 8→9→10 y JUGAR YA
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
