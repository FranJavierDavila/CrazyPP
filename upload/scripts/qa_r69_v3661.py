#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r69_v3661 — CAPA BD · V3.6.61-SDK6, FASE 63 «UNA RAQUETA, CERO FANTASMAS».

El informe del dueño tras probar V3.6.60 en el Quest, punto por punto:
  1. «Cuando practicamos a golpear aparecen en el lado del rival DOS
     raquetas, una que es la que se utiliza para las partidas (visible en
     todo momento) y otra para el profesor… si usas la que has metido para
     el profesor OJO porque está desfasada y no golpea la pelota».
  2. «La pala es una prolongación de nuestra mano… es preciso que se le
     diga EN ESE MOMENTO que tiene que moverla hacia los lados».
  3. «Todos los parámetros exclusivos del tutorial deben morir al cerrarlo
     — después de la academia jugamos con un halo sobre nuestra propia
     pala que no debe estar ahí».
  4. «En ajustes tenemos un Tutorial que ya no tiene sentido: eliminarlo».
  5. «Los troqueles de adorno de los campeonatos han desaparecido».

El arreglo (r69):
  · UNA SOLA RAQUETA POR LADO: la pala flotante de la IA (aiPaddleMesh,
    la de los partidos) se OCULTA durante la academia y stop() la
    devuelve; el jugador ve UNA raqueta al otro lado — la del profesor.
  · GOLPES HONESTOS: las devoluciones ya no aplican la velocidad en el
    frame en que arranca el barrido (la hoja llegaba 0.13 s tarde —
    «desfasada»). armaDevolucion arma el golpe (devPend) y tickDevolucion
    despega la bola EXACTAMENTE cuando el tramo A se cierra; el contacto
    es VIVO (raqContacto persigue a la bola en vuelo) y si la bola muere
    el golpe se cancela: jamás un lanzamiento fantasma.
  · LA AURA SE DESMONTA: limpiarAura() saca ppTutAuraPala del paddleMount
    (antes quedaba con el pulso congelado — el «halo fantasma») y libera
    sus materiales; _ponAuraPala autocura huérfanos por nombre.
  · INSTRUCCIÓN DEL VAIVÉN: la pizarra muestra «MUÉVELA HACIA LOS LADOS ·
    vaivén firme» (i18n ES/EN tut_m1_lado) latiendo mientras la barra
    está vacía.
  · AJUSTES SIN TUTORIAL: la entrada repetida del menú de ajustes se
    retira (quedan el banner del HUB y la oferta de primera vez).
  · TROQUELES VERIFICADOS: los 5 campeonatos montan sus piezas (listas y
    visibles) en el juego real — capa de regresión para que nada vuelva a
    taparlos silenciosamente.

4 BLOQUES: (1) AGUJAS de fuente r69 (+r68 que siguen vivas). (2) NEGATIVAS.
(3) CONTADORES. (4) MECÁNICA REAL headless (raqueta única, devoluciones
honestas, aura desmontada, cierre sin residuos) + TROQUELES en el juego
real de los 5 campeonatos. (5) ERRORES DE PÁGINA.
Uso: python3 scripts/qa_r69_v3661.py [URL]"""
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
    # --- r68 vivo (la raqueta del rival y sus saques honestos) ---
    ("raqueta del rival: grupo propio en la escena mundo",
     "raqGrp.name = 'ppTutRaquetaRival';"),
    ("barrido de dos tramos: impacto + acompañamiento",
     "raqGrp.position.lerpVectors(raqDe, raqContacto, u);"),
    ("el saque se RETIENE hasta que la hoja llega (adiós al fantasma)",
     "if (demoFaseT < RAQ_T_GOLPE) break;"),
    ("el feed del paso 5 espera a la hoja (cuenta atrás feed5T)",
     "feed5T = RAQ_T_GOLPE;"),
    ("la bola queda VIVA al salir el saque del profesor",
     "G.tutBolaViva = true;    // bola en juego: el rally existe"),
    # --- r69 · UNA SOLA RAQUETA ---
    ("la pala IA se OCULTA durante la academia (idempotente por frame)",
     "try { if (G.aiPaddleMesh) G.aiPaddleMesh.visible = false; } catch (eI) { /* */ }"),
    ("stop() devuelve la pala IA a su estado (los partidos la necesitan)",
     "try { if (gm.aiPaddleMesh) gm.aiPaddleMesh.visible = true; } catch (eI0) { /* */ }"),
    # --- r69 · GOLPES HONESTOS ---
    ("el golpe de devolución se ARMA (cuenta atrás hasta el despegue)",
     "devPend = RAQ_T_GOLPE;"),
    ("el lanzamiento pendiente se diseña desde la bola VIVA",
     "b.vel.copy(devVelFn(b.pos));"),
    ("la bola muerta CANCELA el golpe (jamás un lanzamiento fantasma)",
     "if (muertaD) { cancelaDevolucion(); return; }"),
    ("contacto VIVO: el punto de contacto persigue a la bola en vuelo",
     "try { raqContacto.copy(G.ball.pos); } catch (eC) { /* */ }"),
    ("tickDevolucion vive en el ciclo del tutorial",
     "try { tickDevolucion(dt); } catch (eD2) { /* decorativo */ } // r69 · lanzamientos honestos"),
    ("sin golpes pendientes al cambiar de paso",
     "cancelaDevolucion();              // r69 · sin golpes pendientes al cambiar de paso"),
    # --- r69 · LA AURA SE DESMONTA ---
    ("limpiarAura existe: la aura sale del mount al cerrar",
     "limpiarAura();                      // r69 · la AURA sale del mount (adiós al halo fantasma)"),
    ("libera los materiales de la aura (sin residuos de GPU)",
     "if (o.material) { try { o.material.dispose(); } catch (eD) { /* */ } }"),
    ("autocura: una aura huérfana sale por nombre",
     "const viejo = mount.getObjectByName('ppTutAuraPala');"),
    ("la aura guarda referencia para su desmontaje",
     "auraGrp = grpA;                    // r69 · referencia para DESMONTARLO"),
    # --- r69 · INSTRUCCIÓN DEL VAIVÉN ---
    ("instrucción explícita en la pizarra del vaivén",
     "line(c, T('tut_m1_lado'), 452, 21, '#7fb069');"),
    ("latiendo mientras la barra está vacía (llama la atención)",
     "c.globalAlpha = p > 0.02 ? 1 : (0.55 + 0.45 * Math.sin(mandoT * 5.2));"),
    # --- r69 · AJUSTES SIN TUTORIAL ---
    ("la entrada de AJUSTES retirada (comentario de la retirada)",
     "// r69 · el Tutorial de AJUSTES se RETIRA (petición del dueño): la"),
    # --- r69 · introspección ---
    ("introspección de QA del golpe honesto",
     "devPend: Math.round(devPend * 1000) / 1000,"),
    ("introspección de QA de la raqueta única",
     "aiPadOculta: !!(G && G.aiPaddleMesh && !G.aiPaddleMesh.visible),"),
]

NEGATIVAS = [
    ("el botón de Tutorial en AJUSTES retirado del menú",
     "btn('tut:go', 56, y, 912, 56, T('tut_hub') + ' · ' + T('tutask_yes'), false, undefined, undefined, 23);"),
    ("la devolución instantánea del paso 3 retirada (golpe fantasma)",
     "raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 0.45); // r68 · golpe corto a la red"),
    ("la devolución instantánea del paso 5 retirada (golpe fantasma)",
     "raquetaGolpe(b.pos.x, b.pos.y, b.pos.z, 1);   // r68 · SU hoja golpea"),
]

CONTADORES = [
    (r"raquetaGolpe\(", 3, "raquetaGolpe( en definición + saque + armaDevolucion + feed"),
    (r"raquetaPreparar\(\)", 3, "raquetaPreparar() en demo + paso 3 + paso 5"),
    (r"limpiarRaqueta\(\);", 2, "limpiarRaqueta() en teardownPanel y stop"),
    (r"limpiarAura\(\);", 1, "limpiarAura() en teardownPanel"),
    (r"tut_m1_lado", 3, "tut_m1_lado en c13 (uso) — ×1 aquí; las 2 claves viven en c00"),
    (r"cancelaDevolucion\(\);", 4, "cancelaDevolucion() en tick/advance/start/launch"),
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
    out.push({ ok: d.builtFor === cid && d.pieces.length === camps[cid] &&
                    d.pieces.every((p) => p.ready) && d.group.visible === true &&
                    !g.champDecorHidden,
               lab: `troqueles de ${cid}: ${d.pieces.length} piezas listas y VISIBLES` });
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

  const raqEnEscena = () => G.scene.children.find(
    (ch) => ch.name === 'ppTutRaquetaRival');
  const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
  const misma = (a, b) => Math.abs(a.x - b.x) < 1e-6 &&
    Math.abs(a.y - b.y) < 1e-6 && Math.abs(a.z - b.z) < 1e-6;

  // ---------- 1 · arranque: UNA SOLA RAQUETA --------------------------
  let G = mkJuego(1);
  G.scene.add(G.rig);
  G.aiPaddleMesh.visible = true;         // estado de partido: VISIBLE
  T.start(G);
  T.tick(0.05);
  let e = T.estado();
  out.push({ ok: e.raquetaRival === true && !!raqEnEscena(),
             lab: 'raqueta del RIVAL construida en la escena al arrancar' });
  out.push({ ok: G.aiPaddleMesh.visible === false && e.aiPadOculta === true,
             lab: 'UNA SOLA RAQUETA: la pala IA de los partidos OCULTA en la academia' });
  out.push({ ok: raqEnEscena().visible === false,
             lab: 'raqueta del profesor OCULTA en el paso 0 (vive en los pasos 2-5)' });

  // ---------- 2 · paso 1 → paso 2 (acciones + vaivén r67) -------------
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
             lab: 'paso 2 EL SAQUE: la raqueta del profesor EN MESA' });
  out.push({ ok: G.aiPaddleMesh.visible === false,
             lab: 'la pala IA sigue oculta en los pasos de mesa' });
  // la AURA de la pala real nació en el momento raqueta (subfase 4)
  const auraEnMount = !!G.paddleMounts[1].children.find(
    (ch) => ch.name === 'ppTutAuraPala');
  out.push({ ok: auraEnMount,
             lab: 'la aura de TU pala nace en su mount (momento raqueta)' });

  // ---------- 3 · la demo: postura + armado + barrido honesto ---------
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
      minDist = Math.min(minDist, dist(raqEnEscena().position, G.ball.pos));
      if (i > 24) break;
    }
  }
  out.push({ ok: lanzo, lab: 'el saque del profesor SALE (con su golpe antes)' });
  out.push({ ok: bolaVivaAlLanzar, lab: 'bola VIVA al salir el saque' });
  out.push({ ok: minDist < 0.06,
             lab: `la hoja pasa por la bola al golpear (mín ${Math.round(minDist * 1000)} mm)` });

  // ---------- 4 · demo completa → práctica → 3 saques → paso 3 --------
  for (let i = 0; i < 90; i++) {
    T.tick(0.1);
    if (T.estado().demoT >= 6.2) break;
  }
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.submodo === 'practica',
             lab: 'gatillo → TU TURNO (la raqueta rival espera en guardia)' });
  for (let s = 0; s < 3; s++) {
    T.onTrigger(0);
    G.ball.pos.set(0.1, 1.3, -1.75); G.ball.vel.set(0, -1, -3.2);
    T.tick(0.016);
    G.ball.pos.set(0.4, 0.05, 0.9); G.ball.vel.set(0, 0, 0);
    T.tick(0.3); T.tick(0.3);
  }
  e = T.estado();
  out.push({ ok: e.paso === 3, lab: '3/3 saques → paso 3 EL INTERCAMBIO' });

  // ---------- 5 · devolución HONESTA: despega al paso de la hoja ------
  T.onTrigger(0); T.tick(0.016);
  e = T.estado();
  out.push({ ok: e.rfFase === 'vuelo' && e.bolaViva === true,
             lab: 'saque hecho: la bola va hacia el rival (viva)' });
  G.ball.pos.set(0.1, 0.8, -2.3); G.ball.vel.set(0, 0.6, -0.8);
  T.tick(0.016);
  e = T.estado();
  const velAlArmar = G.ball.vel.length();
  out.push({ ok: e.raqModo === 'prep' || e.raqModo === 'golpe',
             lab: 'bote lejano: el rival ARMA la devolución' });
  // r69 · mientras devPend > 0 la bola NO ha despegado todavía: vuela
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
      // el blade persigue a la bola: la distancia mínima incluye el
      // CONTACTO (tramo A cerrado / arranque del tramo B sobre la bola)
      minDev = Math.min(minDev, dist(raqEnEscena().position, G.ball.pos));
    }
  }
  out.push({ ok: vioDevPend,
             lab: 'la devolución queda ARMADA (cuenta atrás del golpe honesto)' });
  out.push({ ok: despegaTarde,
             lab: 'la bola despega DESPUÉS, cuando la hoja la alcanza' });
  out.push({ ok: minDev < 0.10,
             lab: `el blade está SOBRE la bola al despegar (mín ${Math.round(minDev * 1000)} mm)` });
  e = T.estado();
  out.push({ ok: e.raqModo === 'golpe' || e.rfFase === 'ida' || e.rfFase === 'fallo',
             lab: 'la raqueta en pleno golpe / la devolución en marcha' });

  // ---------- 6 · paso 4 marcador → paso 5 LA PRÁCTICA ----------------
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
  for (let i = 0; i < 90; i++) T.tick(0.2);
  T.onTrigger(0); T.tick(0.05);
  e = T.estado();
  out.push({ ok: e.paso === 5, lab: 'ENTENDIDO → paso 5 LA PRÁCTICA' });

  // ---------- 7 · el FEED del profesor: golpe visible + bola viva -----
  G.ball.pos.set(0.1, 0.79, -2.3); G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
  let vioGolpeFeed = false, vivoEnGolpe = false, lanzada = false;
  for (let i = 0; i < 80 && !vivoEnGolpe; i++) {
    T.tick(0.05);
    e = T.estado();
    if (e.raqModo === 'golpe') vioGolpeFeed = true;
    if (e.raqModo === 'golpe' && e.bolaViva === true) {
      vivoEnGolpe = true;
      lanzada = G.ball.vel.length() > 2.5 && G.ball.vel.z > 1.0;
    }
  }
  out.push({ ok: vioGolpeFeed,
             lab: 'el profesor GOLPEA su saque de práctica (hoja visible)' });
  out.push({ ok: vivoEnGolpe && lanzada,
             lab: 'bola VIVA y LANZADA hacia ti al paso de la hoja (rally existe)' });

  // ---------- 8 · cierre: SIN residuos (aura + raqueta + pala IA) -----
  T.stop({});
  e = T.estado();
  out.push({ ok: e.activo === false && e.raquetaRival === false,
             lab: 'cierre: la academia suelta la raqueta del rival' });
  out.push({ ok: !G.scene.children.some((ch) => ch.name === 'ppTutRaquetaRival'),
             lab: 'escena SIN residuos de la raqueta rival' });
  out.push({ ok: !G.paddleMounts[1].children.find((ch) => ch.name === 'ppTutAuraPala'),
             lab: 'CERO HALO FANTASMA: la aura salió del paddleMount al cerrar' });
  out.push({ ok: G.aiPaddleMesh.visible === true,
             lab: 'la pala IA VUELVE a estar visible (los partidos la necesitan)' });
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

        print("--- 1 · FUENTE SERVIDA (agujas r69) ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (retiradas r69) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · CONTADORES ---")
        for pat, minimo, label in CONTADORES:
            n = len(re.findall(pat, src))
            chk(n >= minimo, f"{label} ({n})")
        # las claves i18n viven en c00 (embebido en el HTML): 2 apariciones
        n_lado = len(re.findall(r"tut_m1_lado", src))
        chk(n_lado >= 3, f"tut_m1_lado ES+EN+uso en el servido ({n_lado})")

        print("--- 4 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 5 · TROQUELES en el juego real (los 5 campeonatos) ---")
        filas = await page.evaluate(TROQUELES)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        print("--- 6 · ERRORES DE PÁGINA ---")
        chk(len(errors) == 0, f"sin pageerror/console.error ({len(errors)})")
        for err in errors[:5]:
            print("    ·", err[:180])

        await browser.close()

    print(f"\nCAPA BD · qa_r69_v3661: {ok} OK · {fails} FALLOS")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
