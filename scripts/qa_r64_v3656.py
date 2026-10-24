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
    # --- FIX 1 · maquetación ---
    ("auto-ajuste de textos (fitFont)",
     "function fitFont(c, txt, size, weight, maxW, minSize) {"),
    ("line() ajusta TODAS las líneas al panel",
     "function line(c, txt, y, size, col, align, x, maxW) {\n    fitFont(c, txt, size, '600', maxW || LINE_MAXW);"),
    ("píldoras auto-dimensionadas al texto",
     "const w = Math.max(opts.w || 640, Math.min(need, 960));"),
    ("wrap2 para textos largos (2 líneas)",
     "function wrap2(c, txt, y, size, col, maxW, lh) {"),
    ("tut_s7_p en 2 líneas dentro de su fila",
     "wrap2(c, T('tut_s7_p'), 499, 19, '#ffe08a', 860, 14);"),
    ("canvas nítido 1280×800",
     "cv.width = 1280; cv.height = 800;"),
    ("coordenadas lógicas intactas (scale 1.25)",
     "cc.scale(1.25, 1.25);"),
    ("título de cabecera ajustado al hueco",
     "fitFont(c, T('tut_title'), 36, '900', 700, 24);"),
    ("filas de modos ajustadas (título)",
     "fitFont(c, title, 27, '800', 760, 18);"),
    ("filas de modos ajustadas (sub)",
     "fitFont(c, sub, 19, '500', 760, 13);"),
    # --- FIX 2 · mando 3D procedural ---
    ("mando 3D procedural Touch Plus (builder)",
     "function buildMando() {"),
    ("materiales del mando con resalte emissive",
     "emissive: new THREE.Color('#ffd257'), emissiveIntensity: 0,"),
    ("6 piezas nombradas en el grafo",
     "g.name = 'tut_' + nombre;"),
    ("el mando nace junto al panel (hijo del panel)",
     "mando.position.set(0.68, -0.05, 0.03);"),
    ("el mando es GIRATORIO (tick de giro)",
     "mandoSpin.rotation.y = mandoT * 0.55;"),
    ("vaivén suave del mando",
     "mando.position.y = -0.05 + Math.sin(mandoT * 1.4) * 0.006;"),
    ("resalte por paso (¿qué pieza menciona el guion?)",
     "function hlDePaso(t) {"),
    ("ciclo de piezas del paso 1 (gatillo/grip/stick/botones)",
     "const HL_CICLO_S1 = ['gatillo', 'grip', 'stick', 'botones'];"),
    ("el panel construye el mando",
     "buildMando();                       // r64 · mando 3D flotando junto al panel"),
    ("teardown limpia el mando",
     "mando = null; mandoSpin = null; mandoPartes = null; mandoMats = null;"),
    # --- FIX 3 · práctica real + panel apartado ---
    ("meta del paso 3: 3 saques válidos",
     "const SAQ_META = 3;"),
    ("meta del paso 4: 6 devoluciones",
     "const DEVOL_META = 6;"),
    ("cerrojo anti-doble-recuento del saque",
     "saqLatch = true;"),
    ("aviso verde «saque válido»",
     "flashOk = 2.2; flashAgain = 0;"),
    ("contador grande de saques en el panel",
     "c.fillText(Math.min(saqCount, SAQ_META) + ' / ' + SAQ_META, 512, 412);"),
    ("pose del panel (frente ⇄ lado)",
     "function poseDestino() {"),
    ("pose lado: al lado CONTRARIO de la pala",
     "const sgn = (G && G.paddleHand === 1) ? -1 : 1;"),
    ("transición suave de pose (lerp)",
     "const k = 1 - Math.exp(-dt * 4.5);"),
    ("el panel se aparta en los pasos de práctica (3 y 4)",
     "if (step === 3 || step === 4) {"),
    ("tick invoca la pose y el mando",
     "tickPose(dt);                       // r64 · el panel se aparta en la práctica\n    tickMando(dt);                      // r64 · giro + resalte del mando 3D"),
    ("rally real: cada golpe habilita UNA devolución del profesor",
     "aiReturned = false;   // r64 · cada golpe habilita UNA devolución del"),
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

  // juego simulado CON RIG REAL (grafo de escena verificable)
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
    audio: { playOsc: () => {}, announce: () => {}, serve: () => {} },
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
    rig: new THREE.Group(),
  });
  const buscaPanelInicial = (rig) => rig.children.filter(ch =>
    ch.type === 'Group' && Math.abs(ch.position.y - 1.52) < 0.01 &&
    Math.abs(ch.position.z + 0.86) < 0.01 && ch.children.length > 0);
  const partesMando = (panel) => {
    const nombres = [];
    panel.traverse(o => { if (o.name && o.name.startsWith('tut_')) nombres.push(o.name); });
    return nombres;
  };

  // ---------- 1 · FIX 2: el mando 3D existe, tiene 6 partes y GIRA ----
  let G = mkJuego(1);                       // pala en mano 1 (derecha)
  T.start(G);
  let e = T.estado();
  let panel = buscaPanelInicial(G.rig)[0];
  out.push({ ok: e.activo && e.pose === 'frente' && !!panel,
             lab: 'arranque: pose frente y panel en el rig (huella r63 intacta)' });
  const mando = panel ? panel.children.find(ch => ch.name === 'ppTutMando') : null;
  out.push({ ok: !!mando, lab: 'mando 3D presente junto al panel' });
  const partes = mando ? partesMando(mando) : [];
  const esperadas = ['tut_cuerpo', 'tut_anillo', 'tut_stick', 'tut_gatillo', 'tut_grip', 'tut_botones'];
  out.push({ ok: esperadas.every(p => partes.includes(p)) && partes.length === 6,
             lab: 'Touch Plus: 6 partes (' + partes.join(',') + ')' });
  const spin = mando ? mando.children[0].children[0] : null;
  const y0 = spin ? spin.rotation.y : 0;
  for (let i = 0; i < 20; i++) T.tick(0.05);
  out.push({ ok: spin && spin.rotation.y > y0 + 0.3,
             lab: 'mando giratorio (dY=' + (spin ? (spin.rotation.y - y0).toFixed(3) : 'x') + ')' });
  out.push({ ok: T.estado().mandoHl === 'cuerpo', lab: 'paso 0 resalta el CUERPO' });
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: ['gatillo', 'grip', 'stick', 'botones'].includes(e.mandoHl),
             lab: 'paso 1 cicla piezas (' + e.mandoHl + ')' });
  out.push({ ok: T.estado().mandoHl !== null && T.estado().tieneMando === true,
             lab: 'estado() expone mando/resalte' });

  // ---------- 2 · FIX 3a: pose LADO en la práctica --------------------
  T.onTrigger(0);                                  // → paso 2
  G.controllerPaddles[1].vel.set(1.5, 1.2, 1.5);   // vaivén con la pala (mano 1)
  for (let i = 0; i < 8; i++) T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.paso === 3 && e.pose === 'lado',
             lab: 'paso 3 (EL SAQUE) → pose LADO' });
  for (let i = 0; i < 60; i++) T.tick(0.05);       // el lerp lleva el panel al lado
  const px = panel.position.x, py = panel.position.y, esc = panel.scale.x;
  out.push({ ok: px < -0.45, lab: 'panel APARTADO a la izquierda con pala dcha (x=' + px.toFixed(3) + ')' });
  out.push({ ok: py < 1.4 && esc < 0.95, lab: 'panel más bajo y compacto (y=' + py.toFixed(2) + ' · s=' + esc.toFixed(2) + ')' });
  out.push({ ok: Math.abs(panel.position.z + 0.62) < 0.05, lab: 'panel más cercano al jugador (z=' + panel.position.z.toFixed(2) + ')' });

  // ---------- 3 · FIX 3b: 3 SAQUES con cerrojo ------------------------
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
  out.push({ ok: e.paso === 4 && e.pose === 'lado', lab: 'saque 3/3 → paso 4 (sigue en LADO)' });

  // ---------- 4 · FIX 3c: 6 devoluciones con rally real ---------------
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
  out.push({ ok: e.paso === 5, lab: '6 devoluciones → paso 5 (LOS BOTONES)' });

  // ---------- 5 · vuelta a FRENTE y salida limpia ---------------------
  G.paddleHand = 0; T.tick(0.016);                   // A/X cambia la mano
  e = T.estado();
  out.push({ ok: e.paso === 6 && e.pose === 'frente', lab: 'paso 6 → pose FRENTE de nuevo' });
  const rig0 = G.rig.children.length;
  T.stop({ aJugar: true, done: true });
  out.push({ ok: G.rig.children.length === 0 && rig0 > 0,
             lab: 'salida: panel+mando desmontados (0 residuos de ' + rig0 + ')' });
  out.push({ ok: (T.estado().tieneMando === false && T.estado().tienePanel === false),
             lab: 'estado() limpio tras la salida' });

  // ---------- 6 · jugador ZURDO: el panel se aparta al OTRO lado ------
  G = mkJuego(0);                         // pala en mano 0 (izquierda)
  T.start(G);
  panel = buscaPanelInicial(G.rig)[0];
  T.onTrigger(0); T.onTrigger(0);                  // → paso 2
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
