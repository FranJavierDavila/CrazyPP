#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r64_v3656 — CAPA r64 · V3.6.56-SDK6, FASE 58 «LA ACADEMIA, A PUNTO».

Las tres correcciones del dueño al tutorial (literales):
  1. «Los textos están mal maquetados y quedan fuera de sus contenedores
     cortándose» → auto-ajuste: fitFont reduce la fuente hasta caber,
     pill auto-dimensiona la píldora al texto, wrap2 parte en 2 líneas los
     textos largos (tut_s7_p) y el canvas sube a 1280×800 (texto nítido).
  2. «El mando no está en 3d y es muy cutre — Lo modelo yo en 3D real
     procedural (Touch Plus: cuerpo, anillo, stick, gatillo, grip)
     flotando junto al panel, giratorio y con cada pieza iluminándose
     cuando el paso la menciona» → buildMando: 6 piezas nombradas en el
     grafo, giro continuo + vaivén, resalte emissive por paso
     (paso 0 cuerpo · paso 1 ciclo gatillo/grip/stick/botones ·
     paso 3 gatillo · paso 5 botones).
  3. «Al final del tutorial tenemos que practicar a sacar y devolver la
     bola… al menos 3 saques y varias devoluciones… pero ojo el panel del
     tutorial en la práctica tiene que moverse de sitio ya que no nos deja
     ver la mesa» → SAQ_META=3 (con cerrojo anti-doble-recuento y aviso
     verde «saque válido») · DEVOL_META=6 (con rally real: cada golpe
     habilita UNA devolución del profesor) · poseDestino(): el panel se
     APARTA al lado contrario de la pala en los pasos 3 y 4 (lerp suave).

Pruebas: (1) FUENTE SERVIDA — agujas r64 del módulo + negativas (el
diagrama 2D y la meta 2 ya no existen). (2) i18n ES/EN de las claves
nuevas/cambiadas. (3) MECÁNICA REAL headless SOBRE EL GRAFO DE ESCENA
(rig real de three): panel + mando 3D con sus 6 partes, giro, resalte por
paso, pose frente→lado con desplazamiento medible, 3 saques con cerrojo,
saque fallido sin contar, 6 devoluciones con el profesor devolviendo cada
vez, salida limpia sin residuos.

Uso: python3 scripts/qa_r64_v3656.py        (servidor dev en :3000)
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
    # --- FIX 1 · maquetación (r64, vivo en el r65 con pizarra) ---
    ("auto-ajuste de textos (fitFont)",
     "function fitFont(c, txt, size, weight, maxW, minSize) {"),
    ("line() ajusta TODAS las líneas al panel",
     "function line(c, txt, y, size, col, align, x, maxW) {\n    fitFont(c, txt, size, '600', maxW || LINE_MAXW);"),
    ("píldoras auto-dimensionadas al texto",
     "const w = Math.max(opts.w || 640, Math.min(need, 1000));"),
    ("wrap2 para textos largos (2 líneas)",
     "function wrap2(c, txt, y, size, col, maxW, lh) {"),
    ("tut_s7_p en 2 líneas dentro de su fila (r66: sin solapes)",
     "wrap2(c, T('tut_s7_p'), 487, 16, '#ffe08a', 900, 12);"),
    ("canvas nítido (r65: pizarra nativa 1408×768)",
     "cv.width = 1408; cv.height = 768;"),
    ("título de cabecera ajustado al hueco",
     "fitFont(c, T('tut_title'), 40, '900', 600, 26);"),
    ("filas de modos ajustadas (título)",
     "fitFont(c, title, 25, '800', 740, 17);"),
    ("filas de modos ajustadas (sub)",
     "fitFont(c, sub, 17, '500', 740, 12);"),
    # --- FIX 2 · mandos 3D (r66: DOS GLB reales del dueño, centrados) ---
    ("mandos 3D (builder de los DOS GLB del dueño)",
     "function buildMandos() {"),
    ("materiales del GLB con resalte emissive",
     "m.emissive = new THREE.Color('#ffd257');"),
    ("anclas de pieza (izquierdo)",
     "const ANCLAS_MANDO = {"),
    ("anclas del derecho = ESPEJO del izquierdo (r66)",
     "const ANCLAS_MANDO_DER = {"),
    ("los mandos nacen CENTRADOS delante del jugador (r66)",
     "mandosGrp.position.set(0, 1.07, -0.56);"),
    ("los mandos son GIRATORIOS (tick de giro r66)",
     "mm.spin.rotation.y += mm.__g * dt;"),
    ("vaivén suave de los mandos",
     "mm.grupo.position.y = Math.sin(mandoT * 1.4 + (mm === mandosI ? 0 : 1.1)) * 0.008;"),
    ("resalte por paso/subfase (¿qué pieza menciona el guion?)",
     "function hlDePaso() {"),
    ("halos pulsantes por pieza (r66 opacos)",
     "mm.halos[kk].material.opacity = (kk === hlParte) ? pulso : 0;"),
    ("el panel construye los mandos",
     "buildMandos();                      // r66 · DOS mandos GLB (izq+der) centrados"),
    ("teardown limpia los mandos",
     "mandosGrp = null; mandosI = null; mandosD = null;"),
    # --- FIX 3 · práctica real + panel apartado ---
    ("meta del paso 3 (práctica): 3 saques válidos",
     "const SAQ_META = 3;           // r64 · saques válidos para superar el paso 5"),
    ("meta del paso 6: 6 devoluciones",
     "const DEVOL_META = 6;         // r64 · devoluciones para superar el paso 6"),
    ("cerrojo anti-doble-recuento del saque",
     "saqLatch = true;"),
    ("aviso verde «saque válido»",
     "flashOk = 2.2; flashAgain = 0;"),
    ("contador grande de saques en el panel",
     "c.fillText(Math.min(saqCount, SAQ_META) + ' / ' + SAQ_META, PIZ_CX, 436);"),
    ("pose del panel (frente ⇄ lado)",
     "function poseDestino() {"),
    ("pose lado: al lado CONTRARIO de la pala",
     "const sgn = (G && G.paddleHand === 1) ? -1 : 1;"),
    ("transición suave de pose (lerp)",
     "const k = 1 - Math.exp(-dt * 4.5);"),
    ("el panel se aparta en reglas y práctica (pasos 3 a 6)",
     "if (step === 3 || step === 4 || step === 5 || step === 6) {"),
    ("tick invoca la pose y los mandos (r66)",
     "tickPose(dt);                       // el panel se aparta en la práctica\n    tickMandos(dt);                     // r66 · giro + halos + fantasma + pose"),
    ("rally real: cada golpe habilita UNA devolución del profesor",
     "aiReturned = false;   // r64 · cada golpe habilita UNA devolución"),
    ("estado() de QA ampliada (saques/pose/mando)",
     "saq: saqCount, metaSaq: SAQ_META, metaDevol: DEVOL_META,"),
]

NEGATIVAS = [
    ("el diagrama 2D del mando ha desaparecido (era «cutre»)",
     "function drawController("),
    ("la meta vieja de 2 devoluciones retirada",
     "const DEVOL_META = 2;"),
    ("el panel ya NO está clavado delante de la cara en la práctica",
     "if (cruzada) { advance(); break; }"),
    ("el scale(1.25) del canvas r64 retirado (ahora 1:1 nativo)",
     "cc.scale(1.25, 1.25);"),
    ("el centro viejo 512 de los pintores retirado",
     "c.fillText(txt, 512, y + h / 2 + 1);"),
]

CLAVES = [
    "tut_s3_task", "tut_s3_cnt", "tut_s3_ok",
    "tut_s4_l2", "tut_s4_task", "tut_s4_n",
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
             speakPlan(plan) { return true; } },
    stickAxis() { return { x: 0, y: 0 }; },
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
  });

  // ---------- 1 · el mando GLB existe, tiene HALOS y GIRA ------------
  let G = mkJuego(1);                       // pala en mano 1 (derecha)
  G.scene.add(G.rig);
  T.start(G);
  let e = T.estado();
  let panel = G.rig.children.find((ch) => ch.type === 'Group' &&
    Math.abs(ch.position.y - 1.52) < 0.01 && ch.children.length > 0);
  out.push({ ok: e.activo && e.pose === 'frente' && !!panel,
             lab: 'arranque: pose frente y panel en el rig (huella r63 intacta)' });
  for (let i = 0; i < 60 && !e.tieneMando; i++) {
    await new Promise((r) => setTimeout(r, 50));
    e = T.estado();
  }
  const mandosG = G.rig.children.find((ch) => ch.name === 'ppTutMandos');
  const mando = mandosG ? mandosG.children.find((ch) => ch.name === 'ppTutMandoGLB') : null;
  out.push({ ok: !!mando && !!mandosG, lab: 'mandos GLB presentes (grupo centrado en el rig, r66)' });
  let spin = null;
  if (mando) { spin = mando.children[0].children[0]; }
  const y0 = spin ? spin.rotation.y : 0;
  for (let i = 0; i < 20; i++) T.tick(0.05);
  out.push({ ok: spin && spin.rotation.y > y0 + 0.2,
             lab: 'mando giratorio (dY=' + (spin ? (spin.rotation.y - y0).toFixed(3) : 'x') + ')' });
  T.tick(0.05);
  out.push({ ok: T.estado().mandoHl === null,
             lab: 'paso 0 sin pieza resaltada (bienvenida, r65)' });
  out.push({ ok: T.estado().tieneMando === true,
             lab: 'estado() expone mando/resalte' });

  // ---------- 2 · 4 acciones del paso 1 y vaivén → reglas ------------
  T.onTrigger(0);                                  // paso 0 → 1
  T.tick(0.05);
  out.push({ ok: T.estado().mandoHl === 'gatillo',
             lab: 'paso 1 subfase 0 resalta el GATILLO (subfase r65)' });
  T.onTrigger(0);                                  // 1) gatillo
  T.tick(0.05);
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: false };
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: true };   // 2) grip
  T.tick(0.016); T.tick(0.05);
  G.stickAxis = () => ({ x: 0.7, y: 0 });                // 3) stick
  T.tick(0.016); T.tick(0.05);
  G.sources[0].gamepad.buttons[4] = { pressed: true };   // 4) A
  T.tick(0.016); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 1 && e.subfase === 4, lab: 'paso 1: 4 acciones completadas' });
  T.onTrigger(0);                                  // → paso 2
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);   // vaivén con la pala (mano 1)
  for (let i = 0; i < 8; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.pose === 'lado',
             lab: 'paso 3 (REGLAS·PUNTOS) → pose LADO' });
  for (let i = 0; i < 60; i++) T.tick(0.05);       // el lerp lleva el panel al lado
  const px = panel.position.x, py = panel.position.y, esc = panel.scale.x;
  out.push({ ok: px < -0.45, lab: 'panel APARTADO a la izquierda con pala dcha (x=' + px.toFixed(3) + ')' });
  out.push({ ok: py < 1.4 && esc < 0.95, lab: 'panel más bajo y compacto (y=' + py.toFixed(2) + ' · s=' + esc.toFixed(2) + ')' });

  // ---------- 3 · paso 3 (demo+3 saques con cerrojo) — r66 ------------
  for (let i = 0; i < 30; i++) T.tick(0.2);        // la demo corre sobre la mesa
  T.onTrigger(0);                                  // → práctica (tras 2.5 s)
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.submodo === 'practica' && e.pose === 'lado',
             lab: 'paso 3 (práctica del SAQUE) en LADO tras la demo (r66)' });
  const saca = () => {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016); T.tick(0.016);   // el 2.º tick NO debe re-contar
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);       // bola muerta → rearme
  };
  saca();
  e = T.estado();
  out.push({ ok: e.saq === 1 && e.paso === 3, lab: 'saque 1/3 contado UNA vez (cerrojo)' });
  T.onTrigger(0);
  G.ball.pos.set(0.3, 0.05, 0.8); G.ball.vel.set(0, 0, 0);   // fallido
  T.tick(0.3); T.tick(0.3);
  e = T.estado();
  out.push({ ok: e.saq === 1 && e.paso === 3 && !G.tossed,
             lab: 'saque FALLIDO no cuenta y rearma' });
  saca();
  e = T.estado();
  out.push({ ok: e.saq === 2 && e.paso === 3, lab: 'saque 2/3' });
  saca();
  e = T.estado();
  out.push({ ok: e.paso === 4 && e.pose === 'lado', lab: 'saque 3/3 → paso 4 INTERCAMBIO (LADO, r66)' });

  // ---------- 4 · paso 4: intercambio real → 6 devoluciones (paso 6) -
  // r66: el paso 4 pide SACAR para empezar; lo salta el intercambio
  T.onTrigger(0);                                  // saque del intercambio real
  T.tick(0.016);
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);                    // el rival devuelve
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);                                   // tu golpe cruza
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);                    // el rival vuelve a devolver
  G.ball.pos.set(0.05, 1.1, -1.75); G.ball.vel.set(0, -0.8, -3.0);
  T.tick(0.016);                                   // cruzas otra vez
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016); T.tick(0.016);                    // tercera: el rival FALLA
  for (let i = 0; i < 20; i++) T.tick(0.2);        // el fallo muere → PUNTO
  e = T.estado();
  out.push({ ok: e.paso === 4 && e.rfHecho === true,
             lab: 'intercambio REAL ganado (el rival falla, r66)' });
  T.onTrigger(0);                                  // → paso 5 MARCADOR (r66)
  e = T.estado();
  out.push({ ok: e.paso === 5 && e.holo === true,
             lab: 'paso 5 MARCADOR con holo bajo sobre la mesa (r66)' });
  for (let i = 0; i < 40; i++) T.tick(0.2);        // demo del marcador (8 s)
  T.onTrigger(0);                                  // ENTENDIDO → paso 6
  e = T.estado();
  out.push({ ok: e.paso === 6, lab: 'ENTENDIDO del marcador → paso 6 (r66)' });
  G.ball.pos.set(0.3, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.7);                                     // bola muerta → el profesor alimenta
  for (let i = 0; i < 6; i++) {
    G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
    T.tick(0.016);                                   // golpe válido del jugador
    G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);
    T.tick(0.016);                                   // siembra el bote lejano
    G.ball.vel.y = 0.4;
    T.tick(0.016);                                   // el profesor devuelve
    if (i < 2) {
      const ei = T.estado();
      out.push({ ok: ei.hitCount === i + 1 && G.ball.vel.z > 0,
                 lab: 'rally: devolución ' + (i + 1) + ' contada y el profesor devuelve (vz=' + G.ball.vel.z.toFixed(2) + ')' });
    }
  }
  e = T.estado();
  out.push({ ok: e.paso === 7, lab: '6 devoluciones → paso 7 (LOS BOTONES)' });

  // ---------- 5 · vuelta a FRENTE y salida limpia ---------------------
  G.paddleHand = 0; T.tick(0.016);                   // A/X cambia la mano
  e = T.estado();
  out.push({ ok: e.paso === 8 && e.pose === 'frente', lab: 'paso 8 → pose FRENTE de nuevo' });
  const rig0 = G.rig.children.length;
  T.stop({ aJugar: true, done: true });
  out.push({ ok: G.rig.children.length === 0 && rig0 > 0,
             lab: 'salida: panel+mandos desmontados (0 residuos de ' + rig0 + ')' });
  out.push({ ok: (T.estado().tieneMando === false && T.estado().tienePanel === false),
             lab: 'estado() limpio tras la salida' });

  // ---------- 6 · jugador ZURDO: el panel se aparta al OTRO lado ------
  G = mkJuego(0);                         // pala en mano 0 (izquierda)
  G.scene.add(G.rig);
  T.start(G);
  panel = G.rig.children.find((ch) => ch.type === 'Group' &&
    Math.abs(ch.position.y - 1.52) < 0.01 && ch.children.length > 0);
  T.onTrigger(0); T.tick(0.05);                    // paso 0 → 1
  T.onTrigger(0); T.tick(0.05);                    // paso 1: gatillo (subfase 0→1)
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: true }];
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: false };
  T.tick(0.016);
  G.sources[0].gamepad.buttons[1] = { pressed: true };   // grip
  T.tick(0.016); T.tick(0.05);
  G.stickAxis = () => ({ x: 0.7, y: 0 });
  T.tick(0.016); T.tick(0.05);
  G.sources[0].gamepad.buttons[4] = { pressed: true };   // A
  T.tick(0.016); T.tick(0.05);
  T.onTrigger(0); T.tick(0.05);                    // paso 1 → 2
  G.controllerPaddles[0].vel.set(1.5, 1.2, 1.5);   // vaivén con la mano 0
  for (let i = 0; i < 8; i++) T.tick(0.1);
  for (let i = 0; i < 60; i++) T.tick(0.05);
  out.push({ ok: panel.position.x > 0.45,
             lab: 'zurdo: el panel se aparta a la DERECHA (x=' + panel.position.x.toFixed(3) + ')' });
  T.stop({ done: false });
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
        await page.wait_for_timeout(1000)

        print("--- 1 · FUENTE SERVIDA (agujas r64) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (lo viejo y «cutre» retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · i18n ES/EN (claves r64 ×2 idiomas) ---")
        for clave in CLAVES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 4 · MECÁNICA REAL headless (grafo de escena, rig real) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    if errors:
        for e in errors[:6]:
            print("  ·", e[:220])
    chk(len(errors) == 0, "sin errores JS en la carga del juego")

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
