#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_tut_v3651 — CAPA r59 · V3.6.51-SDK6, FASE 53 «LA ACADEMIA».

La petición del dueño (literal): «hay algo muy importante que no hemos
realizado y se trata de un tutorial o demo para los usuarios que entran en
el juego por primera vez, una explicación detallada y práctica de las
diferentes modalidades de juego. El juego lo ha probado varias personas y
con tanto menú y opciones no saben ni siquiera como hacer para sacar, así
que en el Menú principal debemos incluir un tutorial interactivo para que
sepan como jugar y sacarle partido al juego, hasta creo que podría estar
bien que pudieran ver el mando para familiarizarse con los controles y que
pudiesen probar acciones guiados por este tutorial».

Pruebas: (1) FUENTE SERVIDA — agujas r59 del núcleo (12 guardias/ganchos
tutV1, banner del HUB, oferta de primera vez, caso 'tut', icono birrete,
botón de AJUSTES) y del MÓDULO __PP_TUT (9 pasos, profesor con el solver
de la casa, panel en el RIG, B/Y de salida, estado() de QA). i18n ES/EN
con las MISMAS claves. Negativas: sin placeholders, sin 'export ' ilegal.
(2) MECÁNICA REAL headless — el módulo REAL __PP_TUT dentro del navegador
con un juego simulado: arranque (estanqueidad), avance 0→1→2 (vaivén),
3 EL SAQUE (gatillo-toss + cruce de red + rearme con bola muerta; r64:
   3 VÁLIDOS con cerrojo anti-doble-recuento),
4 EL INTERCAMBIO (profesor devuelve con solver + 6 devoluciones, r64,
   con rally real: cada golpe habilita UNA devolución del profesor),
5 A/X (cambio de mano real), 6/7 modos por gatillo, 8 JUGAR YA (done +
localStorage + exitCalib) y salida por B (goHomeHall + sin 'done').
r64: mando 3D PROCEDURAL Touch Plus (6 partes giratorias con resalte),
pose del panel (frente ⇄ lado: se aparta en la práctica), auto-ajuste
de textos (fitFont/pill/wrap2) y canvas 1280×800.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import io
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


FUENTE = [
    # --- guardias y ganchos del núcleo (r59) ---
    ("gancho onTrigger del tutorial (antes de la máquina de calib)",
     "if (this.tutV1 && window.__PP_TUT && window.__PP_TUT.onTrigger) {"),
    ("updateCalibration dormido en la academia",
     "if (this.tutV1) return;"),
    ("A/X cambia la pala de mano también en la academia",
     "if (presenting && (!this.calib || this.trainV3 || this.tutV1)) {"),
    ("Y ya no saca del ajuste durante el tutorial",
     "if (presenting && this.calib && !this.tutV1 &&\n        this.readButton(this.handIndex('left'), 5)) {"),
    ("holdLock r59: bola en la mano libre durante el saque de la academia",
     "this.rules.state === 'serve' && (!this.calib || this.tutV1)) {"),
    ("releaseBallHand: saque natural (grip) también en la academia",
     "if (this.tutV1) {\n      if (!window.__PP_TUT) return;"),
    ("tick del tutorial en el ciclo del núcleo",
     "if (window.__PP_TUT) window.__PP_TUT.tick(dt);"),
    ("caso 'tut' en el dispatcher del menú",
     "if (window.__PP_TUT) window.__PP_TUT.menuAction(this, arg);"),
    ("página 'tutask' delegada al módulo",
     "if (this.menuPage === 'tutask' && window.__PP_TUT) {"),
    ("oferta de primera vez (pp_tut_asked) en onSessionStart",
     "localStorage.getItem('pp_tut_asked')"),
    ("sello de tutorial completado (pp_tut_done)",
     "localStorage.getItem('pp_tut_done')"),
    ("la academia nunca sobrevive a una sesión VR (stop en sessionstart)",
     "window.__PP_TUT.stop({})"),
    ("banner dorado del HUB con acceso al tutorial",
     "this._modeCard(rects, 'tut:go', 40, 240, 944, 96, T('tut_hub'),"),
    ("botón de repetir el tutorial en AJUSTES",
     "btn('tut:go', 56, y, 912, 56, T('tut_hub') + ' · ' + T('tutask_yes'),"),
    ("icono birrete de LA ACADEMIA (PP_ICONS.tut)",
     "tut(c, x, y) {            // v3.6.51 (r59) · birrete (LA ACADEMIA)"),
    # --- módulo LA ACADEMIA (r59) ---
    ("módulo registrado como window.__PP_TUT",
     "window.__PP_TUT = {"),
    ("guion de 9 pasos",
     "const STEPS = 9;"),
    ("paso 3 usa el estado REAL de saque del núcleo",
     "G.rules.state = 'serve';"),
    ("profesor devuelve con el SOLVER de la casa",
     "computeShotVelocityReal(b.pos, targetProfesor(), 1.05, 5.4, _cero)"),
    ("respaldo balístico si el solver faltara",
     "b.vel.set((Math.random() * 2 - 1) * 0.4, 2.4, 3.1);"),
    ("profesor alimenta con la máquina de práctica del núcleo",
     "G.feedPracticeBall();"),
    ("panel colgado del RIG delante del jugador",
     "grp.position.set(0, 1.52, -0.86);"),
    ("salto con B/Y (botón 5, borde por mando)",
     "if (b5 && !btn5Prev[h]) { stop({ done: false }); return; }"),
    ("meta del paso 2 (vaivén de la pala)",
     "const SWAY_META = 0.55;"),
    ("meta del paso 3 (3 saques válidos, r64)",
     "const SAQ_META = 3;"),
    ("meta del paso 4 (6 devoluciones, r64)",
     "const DEVOL_META = 6;"),
    ("rally real: cada golpe habilita UNA devolución del profesor (r64)",
     "aiReturned = false;   // r64 · cada golpe habilita UNA devolución del"),
    ("mando 3D procedural Touch Plus (r64)",
     "function buildMando() {"),
    ("el mando 3D flota junto al panel (r64)",
     "mando.position.set(0.68, -0.05, 0.03);"),
    ("resalte de piezas por paso (r64)",
     "function hlDePaso(t) {"),
    ("el panel se aparta en la práctica (pose lado, r64)",
     "function poseDestino() {"),
    ("transición suave de pose (lerp, r64)",
     "const k = 1 - Math.exp(-dt * 4.5);"),
    ("auto-ajuste de textos (sin cortes, r64)",
     "function fitFont(c, txt, size, weight, maxW, minSize) {"),
    ("píldoras auto-dimensionadas (r64)",
     "const w = Math.max(opts.w || 640, Math.min(need, 960));"),
    ("canvas nítido 1280×800 (r64)",
     "cv.width = 1280; cv.height = 800;"),
    ("estanqueidad: deja los campeonatos al entrar",
     "if (G.champs) { try { G.champs.leaveAll(); } catch (e) { /* */ } }"),
    ("estanqueidad: cierra el PRO TRAINING al entrar",
     "if (G.trainV3 || G.trainV3Hub) G.closeTrainingV3();"),
    ("estado() de introspección para QA",
     "estado() {"),
    ("pantalla «¿PRIMERA VEZ?» con EMPEZAR TUTORIAL",
     "btn('tut:go', 132, 446, 760, 168, T('tutask_yes'), true, 'green', undefined, 44);"),
    ("anuncio hablado al completar",
     "gm.audio.announce(T('tut_done_msg'), true);"),
]

CLAVES_ES = [
    "tut_hub", "tut_hub_sub", "tutask_title", "tutask_sub", "tutask_yes",
    "tutask_no", "tut_title", "tut_step", "tut_hint_next", "tut_hint_skip",
    "tut_s0_t", "tut_s0_l1", "tut_s0_l2", "tut_s0_go",
    "tut_s1_t", "tut_s1_l1", "tut_s1_l2", "tut_s1_l3", "tut_s1_task",
    "tut_s2_t", "tut_s2_l1", "tut_s2_l2", "tut_s2_task",
    "tut_s3_t", "tut_s3_l1", "tut_s3_l2", "tut_s3_l3", "tut_s3_task",
    "tut_s3_again", "tut_s3_cnt", "tut_s3_ok", "tut_s4_t", "tut_s4_l1",
    "tut_s4_l2", "tut_s4_task",
    "tut_s4_n", "tut_s5_t", "tut_s5_l1", "tut_s5_l2", "tut_s5_l3",
    "tut_s5_task", "tut_s6_t", "tut_s6_m1", "tut_s6_m2", "tut_s6_m3",
    "tut_s7_t", "tut_s7_m1", "tut_s7_m2", "tut_s7_m3", "tut_s7_p",
    "tut_s8_t", "tut_s8_l1", "tut_s8_l2", "tut_s8_go",
    "tut_done_msg", "tut_bad_online", "tut_bad_busy",
    "tut_lab_trigger", "tut_lab_stick", "tut_lab_grip", "tut_lab_btns",
]

MECANICA = r"""
() => {
  const out = [];
  const T = window.__PP_TUT;
  if (!T || typeof T.start !== 'function') return ['__PP_TUT ausente'];
  const V = (x, y, z) => ({
    x, y, z,
    copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; },
    set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; },
    length() { return Math.hypot(this.x, this.y, this.z); },
  });
  const mkJuego = () => {
    const G = {
      net: { online: false }, champs: null,
      trainV3: null, trainV3Hub: false, tutV1: null, calib: false,
      rules: { state: 'point', server: 'ai', message: '', bestOf: 3,
        startMatch(m) { this.state = 'serve'; this.server = 'player'; } },
      ball: { pos: V(0, 1.0, 0.4), vel: V(0, 0, 0), spin: V(0, 0, 0) },
      renderer: { xr: { isPresenting: true } },
      controllerPaddles: [
        { vel: V(0, 0, 0) }, { vel: V(0, 0, 0) },
      ],
      paddleHand: 0, ballHand: 1, tossed: false, mode: 'match',
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
      __feeds: 0, __exitHall: 0, __exitCalib: 0, __goHome: 0,
    };
    Object.defineProperty(G, 'ballHand', { get() { return 1 - this.paddleHand; } });
    return G;
  };
  // --- 1 · arranque estanco
  let G = mkJuego();
  T.start(G);
  let e = T.estado();
  out.push(['arranque: activo', e.activo === true]);
  out.push(['arranque: guardia tutV1 del núcleo', G.tutV1 === true]);
  out.push(['arranque: calib ON (árbitro dormido)', G.calib === true]);
  out.push(['arranque: panel de agarre oculto', G.calibPanel.group.visible === false]);
  out.push(['arranque: paso 0 (bienvenida)', e.paso === 0]);
  out.push(['arranque: exitHall llamado', G.__exitHall === 1]);
  // --- 2 · paso 0 y 1 por gatillo
  T.onTrigger(0);
  e = T.estado();
  out.push(['gatillo: paso 0 → 1 (tu mando)', e.paso === 1]);
  T.onTrigger(1);
  e = T.estado();
  out.push(['gatillo: paso 1 → 2 (la pala)', e.paso === 2]);
  // --- 3 · paso 2: vaivén de la pala (2,6 m/s sostenido)
  G.controllerPaddles[0].vel.set(1.5, 1.2, 1.5);
  T.tick(0.2); T.tick(0.2); T.tick(0.2);
  e = T.estado();
  out.push(['vaivén: 0,6 s ≥ meta 0,55 → paso 3 (EL SAQUE)', e.paso === 3]);
  out.push(['saque: estado REAL del núcleo', G.rules.state === 'serve' && G.rules.server === 'player']);
  out.push(['saque: resetToss del rearme', G.tossed === false]);
  // --- 4 · paso 3: 3 SAQUES VÁLIDOS (r64) con cerrojo anti-doble-recuento
  T.onTrigger(0);
  out.push(['saque: gatillo lanza (tossFromHand)', G.tossed === true]);
  G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);   // cruza la red
  T.tick(0.016); T.tick(0.016);   // el 2.º tick NO debe re-contar (cerrojo r64)
  e = T.estado();
  out.push(['saque 1/3 contado UNA vez (cerrojo r64)', e.saq === 1 && e.paso === 3]);
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);        // bola muerta
  T.tick(0.3); T.tick(0.3);       // rearme silencioso (el saque había sido válido)
  e = T.estado();
  out.push(['saque: bola muerta tras saque válido rearma sin aviso', G.tossed === false && e.saq === 1]);
  // saque FALLIDO: no cuenta y rearma (aviso «otra vez»)
  T.onTrigger(0);
  G.ball.pos.set(0.3, 0.05, 0.8); G.ball.vel.set(0, 0, 0);        // muerta sin cruzar
  T.tick(0.3); T.tick(0.3);
  e = T.estado();
  out.push(['saque fallido NO cuenta y rearma', e.saq === 1 && e.paso === 3 && G.tossed === false]);
  // saques 2/3 y 3/3 → paso 4
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
  T.tick(0.016);
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.3); T.tick(0.3);
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
  T.tick(0.016);
  e = T.estado();
  out.push(['saque 3/3 → paso 4 (EL INTERCAMBIO)', e.paso === 4]);
  out.push(['intercambio: rally sin árbitro', G.rules.state === 'rally']);
  // --- 5 · paso 4: el profesor devuelve tras el bote lejano
  const vzAntes = G.ball.vel.z;
  G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);   // bote lejano
  T.tick(0.016);                                                   // siembra farBounced
  G.ball.vel.y = 0.4;                                              // en la bajada
  T.tick(0.016);
  e = T.estado();
  out.push(['profesor: devuelve tras el bote (vel.z invierte)', e.fase === 'espera_golpe' && G.ball.vel.z > 0 && vzAntes < 0]);
  // --- 6 · el jugador devuelve: 1/6 (r64)
  G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
  T.tick(0.016);
  e = T.estado();
  out.push(['jugador: devolución 1/6 contada', e.hitCount === 1 && e.paso === 4]);
  // --- 7 · bola muerta → el profesor realimenta (máquina del núcleo)
  const feeds0 = G.__feeds;
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.3); T.tick(0.3);
  out.push(['profesor: realimenta con feedPracticeBall', G.__feeds > feeds0]);
  // --- 8 · el jugador devuelve hasta 6/6 → paso 5 (r64)
  for (let i = e.hitCount; i < 6; i++) {
    G.ball.pos.set(0.1, 1.1, -1.75); G.ball.vel.set(0, -0.5, -3.0);
    T.tick(0.016);                                   // golpe válido del jugador
    G.ball.pos.set(0.2, 0.9, -2.3); G.ball.vel.set(0, 0.5, -2.0);
    T.tick(0.016);                                   // siembra el bote lejano
    G.ball.vel.y = 0.4;
    T.tick(0.016);                                   // el profesor devuelve
  }
  e = T.estado();
  out.push(['jugador: devolución 6/6 → paso 5 (botones)', e.paso === 5]);
  // --- 9 · A/X cambia la mano de verdad
  G.paddleHand = 1;
  T.tick(0.016);
  e = T.estado();
  out.push(['botones: A/X cambia la mano → paso 6 (modos 1/2)', e.paso === 6]);
  // --- 10 · modos por gatillo hasta el 8
  T.onTrigger(0); T.onTrigger(1);
  e = T.estado();
  out.push(['modos: pasos 6→7→8 por gatillo', e.paso === 8]);
  // --- 11 · JUGAR YA: done + localStorage + exitCalib
  localStorage.removeItem('pp_tut_done');
  T.onTrigger(0);
  e = T.estado();
  out.push(['fin: JUGAR YA cierra la academia', e.activo === false]);
  out.push(['fin: exitCalib restaura el modo', G.__exitCalib === 1]);
  out.push(['fin: sello pp_tut_done escrito', localStorage.getItem('pp_tut_done') === '1']);
  out.push(['fin: guardia tutV1 limpiada', G.tutV1 === null]);
  out.push(['fin: gatillo ya no se consume', T.onTrigger(0) === false]);
  // --- 12 · salida por B (sin done, al HALL con el menú)
  localStorage.removeItem('pp_tut_done');
  G = mkJuego();
  T.start(G);
  // borde limpio: primero SOLTADO (btn5Prev baja a false), luego PULSADO
  G.sources[0].gamepad.buttons = [{ pressed: false }, { pressed: false },
    { pressed: false }, { pressed: false }, { pressed: false }, { pressed: false }];
  T.tick(0.016);
  G.sources[0].gamepad.buttons[5] = { pressed: true };
  T.tick(0.016);
  e = T.estado();
  out.push(['salida B: cierra la academia', e.activo === false]);
  out.push(['salida B: goHomeHall al HALL', G.__goHome === 1]);
  out.push(['salida B: menú principal delante', G.menuPage === 'main']);
  out.push(['salida B: SIN sello done (no lo completó)', localStorage.getItem('pp_tut_done') === null]);
  // --- 13 · drawAsk: dos botones con ids correctos
  const rects = [];
  const btn = (id, x, y, w, h, lb, act) => rects.push({ id });
  const label = () => {};
  const ctx = { strokeStyle: '', lineWidth: 0, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {} };
  const uiFalso = { menuRects: null, _menuState: null, menuTex: null, rules: { state: 'point' } };
  T.drawAsk(uiFalso, ctx, rects, btn, label);
  out.push(['oferta: botones tut:go y tut:no', !!rects.find(r => r.id === 'tut:go') && !!rects.find(r => r.id === 'tut:no')]);
  // --- 14 · menuAction 'no' vuelve al HUB
  const uiNo = { menuPage: 'tutask', drawMenu() {}, audio: { playOsc() {} } };
  T.menuAction(uiNo, 'no');
  out.push(['oferta: AHORA NO vuelve al HUB', uiNo.menuPage === 'main']);
  // --- 15 · tutela online
  const GOn = mkJuego(); GOn.net = { online: true };
  T.start(GOn);
  out.push(['online: la academia se niega y avisa', GOn.rules.message.length > 0 && GOn.tutV1 === null]);
  return out.map(([lab, cond]) => ({ lab, ok: !!cond }));
}
"""


async def main():
    global ok, fails
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        # los 4xx de recursos (telemetría en dev) NO son errores JS: se filtran
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(900)

        print("--- 1 · FUENTE SERVIDA (agujas r59 del núcleo y del módulo) ---")
        src = await page.content()
        for label, aguja in FUENTE:
            chk(aguja in src, label)

        print("--- 2 · i18n ES/EN: claves presentes y balanceadas ---")
        import re
        for clave in CLAVES_ES:
            n = len(re.findall(rf"^\s+{clave}: '", src, re.M))
            chk(n == 2, f"clave {clave} en ES y EN (×{n})")

        print("--- 3 · NEGATIVAS ---")
        chk("PLACEHOLDER_TUT" not in src, "sin placeholders de tutorial")
        chk(src.count("TODO TUT") == 0, "sin TODO pendiente del tutorial")
        chk("__PP_TUT" in src and "window.__PP_TUT = {" in src,
            "registro único del módulo")
        # el módulo no debe pisar al PRO TRAINING ni al champloader
        chk(src.count("window.__PP_TRAIN = PP_TRAIN;") == 1, "PRO TRAINING intacto (1 registro)")
        chk(src.count("window.__PP_CORE") >= 1, "puente __PP_CORE intacto")

        print("--- 4 · MECÁNICA REAL headless (módulo real, juego simulado) ---")
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
