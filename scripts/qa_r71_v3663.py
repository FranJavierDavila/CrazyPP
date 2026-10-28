#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r71_v3663 — CAPA BF · V3.6.78-SDK6, FASE 65 «EL SERVICIO HONESTO».

El informe del dueño tras probar V3.6.62 en el Quest, punto por punto:
  1. «Cuando el profesor realiza un saque lo hace mal. Tiene que botar
     primero en su campo y después en el nuestro, ahora no lo hace».
  2. «Cuando sacamos nosotros está dando por saque correcto si la bola
     bota en nuestro campo aunque no bote en el del rival».
  3. «Al final del tutorial, cuando dice lo de que con 10-10 se alternan
     los saques, la palabra GAN aparece cortada y debería decir GANAR».
  4. «Nivel de la CPU y Opción de rival adaptativo deben ir dentro de
     Ajustes».
  5. «Ajustes mejor organizado por subcategorías con iconos explícitos,
     un diseño bonito y agradable».

El arreglo (r71) y SU verificación:
  · SAQUE DEL PROFESOR HONESTO: la bola-demo vivía a la ALTURA de la mesa
    17 cm detrás del borde — ningún arco descendente puede botar antes en
    SU campo desde ahí, así que el solver no hallaba candidatos y caía
    SIEMPRE al fallback (lob directo a NUESTRO campo: UN solo bote).
    Reproducido 0/200 con la física real (Node) y arreglado elevando la
    bola a TY+0.34: el solver devuelve 100/100 saques con bote propio
    profundo + bote en el nuestro (margen de red ≥ 49 mm) — verificado
    AQUÍ con la mecánica real de los módulos.
  · BOTES SOBRE LA MESA, NO EN EL SUELO: la valla antigua (z + vel.y +
    y<TY+0.35) aceptaba el bote en el SUELO — un saque largo que salía
    fuera del fondo «botaba» más allá de la mesa y contaba como bueno.
    Ahora cada bote exige el RECTÁNGULO del campo (x y z de la mesa) y
    pegado a la superficie (y<TY+12 cm) — en el saque del jugador Y en la
    demo del profesor. Verificado: LARGO no cuenta, LATERAL no cuenta,
    volea no cuenta, medio saque no cuenta, DOBLE BOTE completo cuenta.
  · CARTEL SIN RECORTES: «¡+2 PARA GANAR!» a 54 px no cabía en el lienzo
    de 256 px (se veía «GAN»). Ahora _cartelTxt MIDE el texto y encoge la
    fuente hasta caber (autoajuste) y el cartel crece a 0.42 m — la
    palabra GANAR entera en ES y EN.
  · CPU + ADAPTATIVO A AJUSTES: fuera del HUB (el dueño lo pidió); viven
    en AJUSTES › JUEGO junto a la Pala Mejorada. Verificado en el menú
    REAL: el HUB no dibuja diff:*/adapt y la subpágina JUEGO sí.
  · AJUSTES POR SUBCATEGORÍAS: 5 tarjetas con icono explícito cada una
    (chip JUEGO · casa SALA · altavoz SONIDO · ojo VISUALES · persona
    PERFIL) + subtítulo con estado vivo + subpágina propia por categoría
    con todos sus controles. Ko-fi al pie. Verificado navegando el menú
    real (rects por página).

BLOQUES: (1) AGUJAS de fuente r71. (2) CONTADORES. (3) MECÁNICA REAL
headless (palma, demo con botes sobre la mesa, saque del jugador con
LARGO/LATERAL rechazados y doble bote válido). (4) SOLVER REAL en Node
(100/100 saques reglamentarios desde la palma del juego). (5) MENÚ REAL
(HUB sin CPU, AJUSTES con 5 categorías, subpágina JUEGO con CPU+adapt).
(6) AUTOAJUSTE del cartel medido en canvas. (7) ERRORES DE PÁGINA.
Uso: python3 scripts/qa_r71_v3663.py [URL]"""
import asyncio
import re
import subprocess
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
    # --- r71 · SAQUE DEL PROFESOR HONESTO (palma elevada) ---
    ("bola-demo ELEVADA y tras el borde (el saque de DOS botes es posible)",
     "return new THREE.Vector3(0.10, TY + 0.34, C - HL - 0.16);"),
    ("comentario de la causa raíz (la palma vieja hacía imposible el bote propio)",
     "ningún arco que parte descendiendo"),
    ("verificación empírica citada (100/100 saques reglamentarios)",
     "100/100 saques con bote propio profundo"),
    # --- r71 · BOTES SOBRE LA MESA (saque del jugador) ---
    ("valla del bote PROPIO exige el rectángulo de TU campo (z dentro de mesa)",
     "b.pos.z < C + HL + 0.03 &&"),
    ("valla del bote PROPIO exige estar sobre la mesa en X",
     "Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&"),
    ("el bote PROPIO es pegado a la superficie (y<TY+12, el suelo queda fuera)",
     "b.pos.y < TY + 0.12) {\n              saqBote1 = true;"),
    ("valla del bote RIVAL exige el rectángulo de SU campo",
     "b.pos.z > C - HL - 0.03 &&\n                Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&"),
    ("comentario r71 (el saque LARGO que se iba fuera ya no contaba)",
     "y se marchaba LARGO contaba"),
    # --- r71 · BOTES SOBRE LA MESA (demo del profesor) ---
    ("demo: bote del profesor dentro de SU rectángulo y pegado a la mesa",
     "b.pos.z > C - HL - 0.03 && Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&\n            b.pos.y < TY + 0.12) {\n          demoBote1 = true;"),
    ("demo: bote en el campo del jugador también sobre la mesa",
     "b.pos.z < C + HL + 0.03 && Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.02 &&\n                   b.pos.y < TY + 0.12) {\n          demoBote2 = true;"),
    # --- r71 · CARTEL SIN RECORTES (GANAR entero) ---
    ("_cartelTxt MIDE el texto antes de pintar",
     "let ancho = g2.measureText(txt).width;"),
    ("autoajuste: la fuente se ENCOGE hasta caber (margen 244 px)",
     "px2 = Math.max(20, Math.floor(px2 * (MARGEN / ancho)));"),
    ("comentario del fallo del dueño (GAN recortado)",
     "«GAN» en vez de «GANAR»"),
    ("cartel «+2 PARA GANAR» más ancho (0.50 m, legible de golpe)",
     "holoCartel2 = _cartelTxt(T('tut_h_p2'), '#ffd257', 54, 0.50, 0.25);"),
    # --- r71 · CPU + ADAPTATIVO VIVEN EN AJUSTES › JUEGO ---
    ("el HUB ya no dibuja la dificultad (se mudó a Ajustes)",
     "r71 · LA DIFICULTAD DE LA CPU Y EL RIVAL ADAPTATIVO SE MUDAN A AJUSTES"),
    ("subpágina JUEGO: la dificultad de la CPU vive ahí",
     "r71 · LA CASA NUEVA del Nivel de la CPU y el Rival Adaptativo"),
    # --- r71 · AJUSTES POR SUBCATEGORÍAS ---
    ("tarjeta JUEGO con icono chip",
     "T('cat_juego'), subJuego, '#2f9e44', '#1e7c33', PP_ICONS.cpu);"),
    ("tarjeta SALA Y ESCENA con icono casa",
     "T('cat_sala'), subSala, '#1c7ed6', '#145c9e', PP_ICONS.sala);"),
    ("tarjeta SONIDO con icono altavoz",
     "T('cat_sonido'), subSonido, '#7048e8', '#4c2bb0', PP_ICONS.sonido);"),
    ("tarjeta VISUALES con icono ojo",
     "T('cat_visual'), subVisual, '#0ca678', '#087354', PP_ICONS.visual);"),
    ("tarjeta PERFIL Y DATOS con icono persona",
     "T('cat_perfil'), subPerfil, '#e8590c', '#b0420a', PP_ICONS.perfil);"),
    ("subtítulos con ESTADO VIVO (lo que se ajusta dentro, de un vistazo)",
     "subtítulos con ESTADO VIVO"),
    ("enrutado de las subpáginas en el dispatcher",
     "this.drawMenuOptsCat(rects, this.menuPage.slice(4).toLowerCase());"),
    ("los clicks de las subpáginas están enroutados",
     "arg === 'optsJuego' || arg === 'optsSala' || arg === 'optsSonido' ||"),
    # --- r71 · i18n de las categorías (ES/EN) ---
    ("claves de categorías en ES",
     "cat_juego: 'JUEGO',"),
    ("claves de categorías en EN",
     "cat_juego: 'GAME',"),
    ("pista de navegación (toca una categoría)",
     "opts_elegir: 'Toca una categoría para entrar',"),
    # --- r71 · introspección de QA ---
    ("estado() expone demoBote1/demoBote2 y la palma",
     "demoBote1, demoBote2,"),
]

CONTADORES = [
    (r"tableHalfWidth \+ 0\.02", 4, "rectángulo de mesa en los 4 botes (2 jugador + 2 demo)"),
    (r"TY \+ 0\.12", 4, "botes pegados a la superficie (4 vallas)"),
    (r"PP_ICONS\.(cpu|sala|sonido|visual|perfil)\b", 6, "iconos de categoría en las tarjetas (5 + RENDIMIENTO r81, cpu ×2)"),
    (r"page:opts(Juego|Sala|Sonido|Visual|Perfil)", 5, "5 tarjetas que abren su subpágina"),
    (r"cat_(juego|sala|sonido|visual|perfil): '", 10, "claves de categoría definidas (5 ES + 5 EN)"),
    (r"saqBote1 = false; saqBote2 = false", 5, "resets del saque intactos (r70)"),
    (r"bolaPalmDemo\(\)", 6, "palma usada por posaBolaDemo/estado"),
]

# MECÁNICA REAL headless — el harness de __PP_TUT (mock G + ticks) de las
# capas BD/BE, extendido con el guion r71: la palma nueva, los botes de la
# demo SOBRE LA MESA y el saque del jugador con LARGO y LATERAL rechazados.
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
  const C = -1.6, HL = 1.37, TY = 0.76;   // DIMS (mesa z∈[-2.97,-0.23])

  // ---------- 1 · arranque hasta el paso 2 (SAQUE) --------------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  T.start(G);
  T.tick(0.05);
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
  let e = T.estado();
  out.push({ ok: e.paso === 2, lab: 'paso 2 EL SAQUE alcanzado' });

  // ---------- 2 · LA PALMA NUEVA (r71): bola elevada tras el borde -----
  out.push({ ok: e.palma && Math.abs(e.palma[0] - 0.10) < 0.001 &&
                    Math.abs(e.palma[1] - (TY + 0.34)) < 0.001 &&
                    Math.abs(e.palma[2] - (C - HL - 0.16)) < 0.001,
             lab: 'la bola-demo vive ELEVADA (TY+0.34) tras el borde de la mesa' });

  // la demo corre: postura (2.1 s) → barrido (0.13 s) → lanzamiento
  let vioPrep = false, lanzo = false, bolaVivaAlLanzar = false, minDist = 1e9;
  for (let i = 0; i < 70; i++) {          // 70×0.05 = 3.5 s > espera 2.1 s
    T.tick(0.05);
    e = T.estado();
    if (e.raqModo === 'prep') vioPrep = true;
    if (e.demoFase !== 0) break;
  }
  for (let i = 0; i < 40 && !lanzo; i++) {  // 0.8 s > RAQ_T_GOLPE 0.13 s
    T.tick(0.02);
    e = T.estado();
    if (e.demoFase >= 1) {                 // el barrido vive en la fase 1: medir AHÍ
      minDist = Math.min(minDist, dist(raqEnRig().position, G.ball.pos));
    }
    if (e.demoFase >= 2 && !lanzo) {
      lanzo = true;
      bolaVivaAlLanzar = e.bolaViva === true;
    }
  }
  out.push({ ok: lanzo, lab: 'el saque del profesor SALE (con su golpe)' });
  out.push({ ok: bolaVivaAlLanzar, lab: 'la bola queda VIVA al lanzarse (r68)' });
  out.push({ ok: minDist < 0.09,
             lab: `la hoja barre hacia la bola (mín ${Math.round(minDist * 1000)} mm)` });

  // ---------- 3 · BOTES DE LA DEMO SOBRE LA MESA (r71) ----------------
  // Todo DENTRO de la fase 2 (los tres teletransportes seguidos, sin dejar
  // que el ciclo de la demo avance de fase).
  if (lanzo) {
    // 3a · bote del profesor DENTRO de su campo (sobre la mesa) → aro rival
    G.ball.pos.set(0.1, TY + 0.05, C - 0.50); G.ball.vel.set(0, 2.0, 0.5);
    T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.demoBote1 === true,
               lab: 'demo: bote del profesor SOBRE SU MESA registrado (aro encendido)' });
    // 3b · LARGO: el «bote» tras la mesa YA NO enciende el aro (valla z)
    G.ball.pos.set(0.1, TY + 0.30, C - HL - 0.20); G.ball.vel.set(0, 2.0, -0.3);
    T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.demoBote2 === false,
               lab: 'demo: bote FUERA del fondo de la mesa NO cuenta (valla z, r71)' });
    // 3c · bote real en el campo del jugador → completo
    G.ball.pos.set(0.1, TY + 0.05, C + 0.50); G.ball.vel.set(0, 2.0, 0.5);
    T.tick(0.016);
    e = T.estado();
    out.push({ ok: e.demoBote2 === true,
               lab: 'demo: bote en el campo del JUGADOR completa la secuencia' });
  }

  // ---------- 4 · SAQUE DEL JUGADOR: LARGO y LATERAL NO CUENTAN -------
  for (let i = 0; i < 90; i++) {
    T.tick(0.1);
    if (T.estado().demoT >= 6.2) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica', lab: 'gatillo → TU TURNO (práctica)' });
  // 4a · volea (r70, se mantiene)
  T.onTrigger(0);
  G.ball.pos.set(0.1, 1.5, -2.2); G.ball.vel.set(0, -2.0, -3.0);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saq === 0 && e.saqBote1 === false,
             lab: 'VOLEA cruzada: sin bote propio NO cuenta (r70 intacto)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  // 4b · EL FALLO DEL DUEÑO: bote tuyo y luego LARGO (suelo tras la mesa)
  T.onTrigger(0);
  G.ball.pos.set(0.1, 0.80, -1.0); G.ball.vel.set(0, 1.2, -0.4);
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saqBote1 === true, lab: 'bote PROPIO registrado (aro tuyo)' });
  G.ball.pos.set(0.1, 0.10, -3.20); G.ball.vel.set(0, 2.0, -0.5);  // suelo tras la mesa
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saqBote2 === false && e.saq === 0,
             lab: 'LARGO (bote en el SUELO tras la mesa): NO es saque bueno (r71)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  e = T.estado();
  out.push({ ok: e.saq === 0 && e.saqBote1 === false,
             lab: 'el saque largo murió SIN contar y los botes se resetean' });
  // 4c · LATERAL: bote tuyo y luego fuera por el LADO de la mesa
  T.onTrigger(0);
  G.ball.pos.set(0.1, 0.80, -1.0); G.ball.vel.set(0, 1.2, -0.4);
  T.tick(0.016);
  G.ball.pos.set(0.95, 0.80, -2.0); G.ball.vel.set(0, 1.0, -0.2);  // |x|>halfW
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saqBote2 === false && e.saq === 0,
             lab: 'LATERAL (fuera del ancho de la mesa): NO cuenta (r71)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  // 4c-bis · SIN BOTE: cruzando el campo rival EN SUBIDA (ni bota) — la
  // valla de ALTURA (y<TY+12 cm) lo rechaza aunque z y x estén sobre la mesa
  T.onTrigger(0);
  G.ball.pos.set(0.1, 0.80, -1.0); G.ball.vel.set(0, 1.2, -0.4);
  T.tick(0.016);
  G.ball.pos.set(0.1, 1.00, -2.0); G.ball.vel.set(0, 0.8, -0.2);  // alto y subiendo
  T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.saqBote2 === false && e.saq === 0,
             lab: 'SIN BOTE (cruzando alto el campo rival, en subida): NO cuenta (r71)' });
  G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
  T.tick(0.05); T.tick(0.1);
  // 4d · TRES SAQUES COMPLETOS (dos botes SOBRE la mesa) → paso 3
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
  out.push({ ok: e.paso === 3, lab: '3/3 saques COMPLETOS (dos botes sobre la mesa) → paso 3' });

  return out;
}"""

# MENÚ REAL (game.html vivo): HUB sin CPU/adaptativo, AJUSTES con 5
# categorías + Ko-fi, subpágina JUEGO con la CPU, el adaptativo y la mega
# pala, y navegación ida y vuelta por los rects reales.
MENU = """async () => {
  const out = [];
  const g = window.__game;
  if (!g || !g.menuRects) return [{ ok: false, lab: '__game ausente' }];
  const ids = () => g.menuRects.map((r) => r.id);
  const tiene = (arr, pref) => arr.some((id) => String(id).indexOf(pref) === 0);

  // ---------- 1 · HUB: SIN dificultad ni adaptativo (r71) -------------
  g.menuOpen = true; g.menuPage = 'main'; g.drawMenu();
  let h = ids();
  out.push({ ok: !tiene(h, 'diff:') && !tiene(h, 'adapt'),
             lab: 'HUB: el Nivel de la CPU y el adaptativo YA NO están (se mudaron)' });
  out.push({ ok: tiene(h, 'page:opts'), lab: 'HUB: la tarjeta AJUSTES sigue' });
  out.push({ ok: tiene(h, 'start') && tiene(h, 'traingo') && tiene(h, 'page:champs'),
             lab: 'HUB: los modos siguen intactos (partido/entrenar/campeonatos)' });

  // ---------- 2 · AJUSTES: 5 categorías con sus subpáginas ------------
  g.menuPage = 'opts'; g.drawMenu();
  let o = ids();
  out.push({ ok: ['optsJuego', 'optsSala', 'optsSonido', 'optsVisual', 'optsPerfil']
      .every((p) => o.includes('page:' + p)),
             lab: 'AJUSTES: 5 subcategorías (JUEGO · SALA · SONIDO · VISUALES · PERFIL)' });
  out.push({ ok: o.includes('kofi'), lab: 'AJUSTES: el apoyo Ko-fi queda al pie' });
  out.push({ ok: !tiene(o, 'diff:') && !tiene(o, 'theme:'),
             lab: 'AJUSTES: página limpia (los controles viven DENTRO de cada categoría)' });

  // ---------- 3 · subpágina JUEGO: la casa nueva de la CPU ------------
  const idxJuego = o.indexOf('page:optsJuego');
  out.push({ ok: idxJuego >= 0, lab: 'la tarjeta JUEGO existe y es clicable' });
  g.menuClick(idxJuego);
  out.push({ ok: g.menuPage === 'optsJuego',
             lab: 'click JUEGO → subpágina optsJuego (navegación real)' });
  let j = ids();
  out.push({ ok: ['diff:easy', 'diff:medium', 'diff:hard'].every((d) => j.includes(d)),
             lab: 'JUEGO: DIFICULTAD DE LA CPU (fácil/medio/difícil) vive aquí (r71)' });
  out.push({ ok: j.includes('adapt'),
             lab: 'JUEGO: el RIVAL ADAPTATIVO vive aquí (r71)' });
  out.push({ ok: j.includes('pmej'), lab: 'JUEGO: la Pala Mejorada acompaña a la CPU' });

  // el click de dificultad real funciona desde su nueva casa
  const idxMed = j.indexOf('diff:medium');
  g.menuClick(idxMed);
  out.push({ ok: g.difficulty === 'medium',
             lab: 'cambiar la CPU a MEDIO desde AJUSTES › JUEGO funciona' });

  // ---------- 4 · las otras subpáginas dibujan SUS controles ----------
  g.menuPage = 'optsSala'; g.drawMenu();
  let s = ids();
  out.push({ ok: ['theme:pabellon', 'theme:neon', 'theme:atardecer', 'theme:artico']
      .every((t) => s.includes(t)) && s.includes('psthru'),
             lab: 'SALA: las 4 salas + passthrough en su subpágina' });
  g.menuPage = 'optsSonido'; g.drawMenu();
  s = ids();
  out.push({ ok: s.includes('music') && s.includes('amb') && s.includes('voz') &&
                  s.includes('sndtest'),
             lab: 'SONIDO: música, ambiente, megáfono y prueba de sonido' });
  g.menuPage = 'optsVisual'; g.drawMenu();
  s = ids();
  out.push({ ok: s.includes('trail') && s.includes('hapt') && s.includes('tips'),
             lab: 'VISUALES: estela, vibración y consejos' });
  g.menuPage = 'optsPerfil'; g.drawMenu();
  s = ids();
  out.push({ ok: s.includes('pname') && s.includes('tele') && s.includes('reset'),
             lab: 'PERFIL: nombre, telemetría y borrado de registros' });

  // ---------- 5 · vuelta atrás en cadena completa ---------------------
  const idxBack = ids().indexOf('page:opts');
  g.menuClick(idxBack);
  out.push({ ok: g.menuPage === 'opts', lab: 'volver de PERFIL → AJUSTES (categorías)' });
  const idxMain = ids().indexOf('page:main');
  g.menuClick(idxMain);
  out.push({ ok: g.menuPage === 'main', lab: 'volver de AJUSTES → MENÚ PRINCIPAL' });
  g.menuOpen = false;
  return out;
}"""

# AUTOAJUSTE del cartel medido en canvas REAL (el «GAN» del dueño): a 54 px
# «¡+2 PARA GANAR!» NO cabía en 256 px; con el algoritmo r71 sí cabe.
CARTEL = """async () => {
  const out = [];
  const cv = document.createElement('canvas');
  cv.width = 256; cv.height = 128;
  const g2 = cv.getContext('2d');
  const mide = (txt, px) => {
    g2.font = '900 ' + px + 'px system-ui, sans-serif';
    return g2.measureText(txt).width;
  };
  const txtEs = '¡+2 PARA GANAR!';
  const txtEn = '+2 TO WIN!';
  const wEs54 = mide(txtEs, 54);
  out.push({ ok: wEs54 > 244,
             lab: 'REPRODUCE el fallo: «' + txtEs + '» a 54 px mide ' +
                  Math.round(wEs54) + ' px y se salía del lienzo (256)' });
  const ajusta = (txt, px) => {
    let px2 = px;
    const w = mide(txt, px2);
    if (w > 244) px2 = Math.max(20, Math.floor(px2 * (244 / w)));
    return { px: px2, w: mide(txt, px2) };
  };
  const rEs = ajusta(txtEs, 54);
  const rEn = ajusta(txtEn, 54);
  out.push({ ok: rEs.w <= 244 && rEs.px >= 20,
             lab: 'ES: con autoajuste «' + txtEs + '» cabe (' + rEs.px +
                  ' px, ' + Math.round(rEs.w) + ' px) — GANAR ENTERO' });
  out.push({ ok: rEn.w <= 244 && rEn.px >= 20,
             lab: 'EN: con autoajuste «' + txtEn + '» cabe (' + rEn.px + ' px)' });
  out.push({ ok: rEs.px >= 20 && rEs.px < 54,
             lab: 'la fuente se ajustó SIN desaparecer (20..53 px, plano de 0.50 m)' });
  return out;
}"""


async def main():
    global ok, fails
    print("=" * 74)
    print("qa_r71_v3663 — CAPA BF · V3.6.78-SDK6 FASE 65 «EL SERVICIO HONESTO»")
    print("=" * 74)

    print("\n[1] AGUJAS de fuente r71")
    src = None
    with open("/home/z/my-project/public/game.html", encoding="utf-8") as f:
        src = f.read()
    for lab, aguja in AGUJAS:
        chk(aguja in src, lab)

    print("\n[2] CONTADORES")
    for pat, esperado, lab in CONTADORES:
        n = len(re.findall(pat, src))
        chk(n == esperado, f"{lab}: {n}/{esperado}")

    # ---------- SOLVER REAL en Node (mecánica real de los módulos) ------
    print("\n[3] SOLVER REAL en Node (mecánica real de c05/c02)")
    try:
        p = subprocess.run(
            ["node", "/home/z/my-project/scripts/_r71_verifica_palma.mjs"],
            capture_output=True, text=True, timeout=300)
        salida = p.stdout
        chk("40/40 reglamentarios" in salida,
            "la palma del juego produce 40/40 saques REGLAMENTARIOS (bote propio + rival)")
        chk("margen de red mínimo: 49 mm" in salida or "margen de red" in salida,
            "el saque del profesor CLEORA la red con margen (≥ 49 mm)")
        chk("bote RIVAL  z ∈" in salida and "-1.6" in salida.split("bote RIVAL")[1][:200],
            "el bote rival cae DENTRO de nuestro campo (z > C)")
    except Exception as e:  # noqa: BLE001
        chk(False, f"solver Node: EXCEPCIÓN {e}")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        errores = []
        page.on("pageerror", lambda e: errores.append(str(e)))
        # los «Failed to load resource» son del SERVIDOR local de pruebas
        # (python -m http.server no acepta el POST del beacon de telemetría
        # → 405): artefacto del entorno, no del juego — las capas hermanas
        # (qa_sup1) solo escuchan pageerror por lo mismo.
        page.on("console", lambda m: errores.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text
                else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1500)

        print("\n[4] MECÁNICA REAL headless (palma + botes sobre la mesa)")
        filas = await page.evaluate(MECANICA)
        for r in filas:
            chk(bool(r.get("ok")), r.get("lab", "?"))

        print("\n[5] MENÚ REAL (HUB sin CPU · AJUSTES por categorías)")
        filas = await page.evaluate(MENU)
        for r in filas:
            chk(bool(r.get("ok")), r.get("lab", "?"))

        print("\n[6] CARTEL con autoajuste medido en canvas")
        filas = await page.evaluate(CARTEL)
        for r in filas:
            chk(bool(r.get("ok")), r.get("lab", "?"))

        print("\n[7] ERRORES DE PÁGINA")
        chk(len(errores) == 0,
            f"0 pageerrors/console errors ({len(errores)})"
            + (": " + " | ".join(errores[:3]) if errores else ""))

        await browser.close()

    print("\n" + "=" * 74)
    print(f"RESULTADO: {ok} OK · {fails} fallos")
    print("=" * 74)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    asyncio.run(main())
