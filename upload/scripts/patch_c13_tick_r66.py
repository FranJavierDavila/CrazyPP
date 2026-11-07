#!/usr/bin/env python3
"""r66 · Máquinas de estado nuevas del _tick (paso 1 fantasma · paso 3 demo+
práctica · paso 4 intercambio real · paso 5 marcador), helpers del ciclo de
demo, accionMandoOk con momento RAQUETA y onTrigger r66. Reemplazos EXACTOS
por marcadores; idempotente por presencia del marcador nuevo."""
import sys

C13 = "/home/z/my-project/src/game/core/c13_ui_arranque.js"
txt = open(C13, encoding="utf-8").read()

def sustituye(viejo, nuevo, etiqueta):
    global txt
    if nuevo[:60] in txt and etiqueta != "header":
        print(f"  · {etiqueta}: YA aplicado")
        return
    if viejo not in txt:
        sys.exit(f"FALLO: marcador no encontrado para {etiqueta}")
    txt = txt.replace(viejo, nuevo, 1)
    print(f"  · {etiqueta}: OK")

# ---------------------------------------------------------------- header
sustituye(
    "    tickMando(dt);                      // giro + halos del mando GLB",
    "    tickMandos(dt);                     // r66 · giro + halos + fantasma + pose",
    "header tickMandos")

# ---------------------------------------------------------------- helpers + cases
VIEJO_CASES = """    switch (step) {
      case 1: {
        // LAS 4 ACCIONES REALES del mando (r65): gatillo → grip → stick → A
        // el gatillo llega por onTrigger; grip/stick/A se sondean aquí
        if (subfase === 1 || subfase === 3) {"""

NUEVO_CASES_INI = """    switch (step) {
      case 1: {
        // LAS 4 ACCIONES REALES de los mandos (r65/r66): gatillo → grip →
        // stick → A. El gatillo llega por onTrigger; grip/stick/A se
        // sondean aquí. Al completarlas, la RAQUETA FANTASMA aparece.
        if (subfase === 1 || subfase === 3) {"""

sustituye(VIEJO_CASES, NUEVO_CASES_INI, "case 1 comentario")

# ------------------------------------------------- casos 3/4/5 → nuevos
VIEJO_345 = """      case 3:
      case 4: {
        // REGLAS (r65): la demo corre; el OK del gatillo exige DEMO_MIN s
        demoT += dt;
        if (repaintT <= 0 && demoT < DEMO_MIN + 0.4) { paintStep(); repaintT = 0.5; }
        break;
      }
      case 5: {
        // EL SAQUE (r64): 3 VÁLIDOS para superar el paso. Cada lanzamiento
        // cuenta UNA sola vez (saqLatch). Si la bola muere vuelve a la
        // mano libre: en silencio si era válido, «otra vez» si se perdió.
        if (flashAgain > 0) {
          flashAgain -= dt;
          if (repaintT <= 0) { paintStep(); repaintT = 0.25; }
        }
        if (G.tossed) {
          const b = G.ball;
          if (!saqLatch) {
            const cruzada = b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9;
            if (cruzada) {
              saqLatch = true;
              saqCount++;
              flashOk = 2.2; flashAgain = 0;
              paintStep();
              chime(true);
              if (saqCount >= SAQ_META) { narra(['tutok']); advance(); break; }
            }
          }
          const muerta = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
            (Math.abs(b.vel.x) < 0.5 && Math.abs(b.vel.y) < 0.5 && Math.abs(b.vel.z) < 0.5 &&
              b.pos.y < DIMS.tableTopY + 0.12) ||
            b.pos.y < -0.4;
          if (muerta) {
            // la bola vuelve a la mano libre (holdLock del núcleo)
            const valida = saqLatch;
            G.resetToss();
            saqLatch = false;
            if (!valida && flashOk <= 0) {
              flashAgain = 2.6;
              paintStep();
              narra(['tutotra']);
              try { G.audio.playOsc(330, 220, 0.12, 'sine', 0.12, 0); } catch (e) { /* */ }
            }
          }
        }
        break;
      }"""

NUEVO_345 = """      case 3: {
        // EL SAQUE (r66): DEMO REAL sobre la mesa y después 3 SAQUES del
        // jugador (la práctica de r64 vive aquí como submodo 'practica').
        demoT += dt;
        if (submodo === 'demo') {
          tickDemoSaque(dt, false);
          if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        } else {
          if (flashAgain > 0) {
            flashAgain -= dt;
            if (repaintT <= 0) { paintStep(); repaintT = 0.25; }
          }
          if (G.tossed) {
            const b = G.ball;
            if (!saqLatch) {
              const cruzada = b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9;
              if (cruzada) {
                saqLatch = true;
                saqCount++;
                flashOk = 2.2; flashAgain = 0;
                paintStep();
                chime(true);
                if (saqCount >= SAQ_META) { narra(['tutok']); advance(); break; }
              }
            }
            const muerta = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              (Math.abs(b.vel.x) < 0.5 && Math.abs(b.vel.y) < 0.5 && Math.abs(b.vel.z) < 0.5 &&
                b.pos.y < DIMS.tableTopY + 0.12) ||
              b.pos.y < -0.4;
            if (muerta) {
              // la bola vuelve a la mano libre (holdLock del núcleo)
              const valida = saqLatch;
              G.resetToss();
              saqLatch = false;
              if (!valida && flashOk <= 0) {
                flashAgain = 2.6;
                paintStep();
                narra(['tutotra']);
                try { G.audio.playOsc(330, 220, 0.12, 'sine', 0.12, 0); } catch (e) { /* */ }
              }
            }
          }
        }
        break;
      }
      case 4: {
        // EL INTERCAMBIO REAL (r66): sacas, el RIVAL devuelve y el
        // intercambio corre hasta que él falla; entonces rota el sacador.
        const b = G.ball;
        if (rfFase !== 'saque' && G.rules.state !== 'rally') G.rules.state = 'rally';
        switch (rfFase) {
          case 'saque':
            G.tutBolaViva = false;
            break;
          case 'vuelo': {
            // la bola va hacia el rival: espera el bote lejano para devolver
            if (!rfVueltaVista && b.pos.z < (DIMS.tableCenterZ - 0.1)) {
              if (!farBounced && b.vel.y > 0.3 && b.pos.y < DIMS.tableTopY + 0.5) {
                farBounced = true;
              }
              if (farBounced && b.vel.y < 1.1 && _cero) {
                rfVueltaVista = true;
                rfVueltas++;
                if (rfVueltas >= 3) {
                  // el rival FALLA: la devolución se queda corta y muere en
                  // la red — punto limpio y visible
                  try {
                    const v = computeShotVelocityReal(b.pos, targetProfesor(), 1.15, 4.6, _cero);
                    b.vel.copy(v).multiplyScalar(0.62);
                  } catch (e) {
                    b.vel.set(0, 1.4, 2.2);
                  }
                  b.spin.set(0, 0, 0);
                  rfFase = 'fallo';
                } else {
                  try {
                    const t = new THREE.Vector3(
                      (Math.random() * 2 - 1) * 0.34, DIMS.tableTopY,
                      DIMS.tableCenterZ + DIMS.tableHalfLength * 0.52);
                    const v = computeShotVelocityReal(b.pos, t, 1.05, 4.8, _cero);
                    b.vel.copy(v);
                  } catch (e) {
                    b.vel.set((Math.random() * 2 - 1) * 0.4, 2.4, 3.1);
                  }
                  b.spin.set(0, 0, 0);
                  try { G.audio.paddle(0, 0.45); } catch (e) { /* */ }
                  try { G.haptic(G.paddleHand, 0.3, 70); } catch (e) { /* */ }
                  rfFase = 'ida';
                }
              }
            }
            break;
          }
          case 'ida': {
            // tu turno: la bola viene; cruza = golpe válido del jugador
            const muertaI = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              (Math.abs(b.vel.x) < 0.4 && Math.abs(b.vel.y) < 0.4 && Math.abs(b.vel.z) < 0.4 &&
                b.pos.y < DIMS.tableTopY + 0.12) ||
              b.pos.y < -0.4;
            if (muertaI) {
              // no llegaste: el intercambio se repite (sin castigo)
              rfFase = 'saque';
              rfVueltas = 0; farBounced = false; rfVueltaVista = false;
              G.rules.state = 'serve';
              G.resetToss();
              G.tutBolaViva = false;
              flashAgain = 2.4;
              paintStep();
              narra(['tutotra']);
              break;
            }
            if (b.pos.z < (DIMS.tableCenterZ - 0.06) && b.vel.z < -0.9) {
              farBounced = false; rfVueltaVista = false;
              rfFase = 'vuelo';
              try { G.haptic(G.paddleHand, 0.4, 80); } catch (e) { /* */ }
            }
            break;
          }
          case 'fallo': {
            const muertaF = (b.pos.y < DIMS.ballRadius + 0.05 && Math.abs(b.vel.y) < 0.6) ||
              b.pos.y < -0.4 || (b.pos.y < DIMS.tableTopY + 0.12 &&
                Math.abs(b.vel.z) < 0.5);
            if (muertaF || demoFaseT > 2.6) {
              rfHecho = true;
              rfFase = 'hecho';
              demoTxt = { txt: T('tut_d4_ok'), col: 'rgba(47,158,68,0.35)', t: 3.4 };
              chime(true);
              narra(['tutv4b']);
              paintStep();
            }
            break;
          }
          case 'hecho':
            G.tutBolaViva = false;
            break;
          default:
            break;
        }
        demoFaseT += dt;
        if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        break;
      }
      case 5: {
        // EL MARCADOR (r66): holo BAJO sobre la mesa; los puntos suben
        // rápido hasta 10-10 y desde ahí CADA punto la anota un saque
        // REAL del bucle — la igualada se ve con la bola de verdad.
        demoT += dt;
        tickDemoSaque(dt, true);
        if (demoPtos < 20) {
          holoT += dt;
          while (holoT > 0.45 && demoPtos < 20) {
            holoT -= 0.45;
            anotaPuntoMarcador();
          }
        }
        if (repaintT <= 0) { paintStep(); repaintT = 0.4; }
        break;
      }"""

sustituye(VIEJO_345, NUEVO_345, "cases 3/4/5")

# ------------------------------------------------- accionMandoOk fantasma
VIEJO_OK = """  /* OK de una acción del paso 1: voz + halo siguiente + repintado */
  function accionMandoOk() {
    subfase++;
    chime(true);
    paintStep();
    try { G.haptic(G.paddleHand, 0.4, 70); } catch (e) { /* */ }
    if (subfase === 1) narra(['tutok', 'tutv1c']);
    else if (subfase === 2) narra(['tutok', 'tutv1d']);
    else if (subfase === 3) narra(['tutok', 'tutv1e']);
    else if (subfase === 4) narra(['tutok']);
  }"""

NUEVO_OK = """  /* OK de una acción del paso 1: voz + halo siguiente + repintado. Al
   * dominar los mandos (subfase 4) aparece la RAQUETA FANTASMA sobre
   * ellos (r66, petición del dueño) y la voz lo celebra. */
  function accionMandoOk() {
    subfase++;
    chime(true);
    paintStep();
    try { G.haptic(G.paddleHand, 0.4, 70); } catch (e) { /* */ }
    if (subfase === 1) narra(['tutok', 'tutv1c']);
    else if (subfase === 2) narra(['tutok', 'tutv1d']);
    else if (subfase === 3) narra(['tutok', 'tutv1e']);
    else if (subfase === 4) {
      fantasmaMeta = 1;                    // el mando SE CONVIERTE en raqueta
      narra(['tutv1f']);
    }
  }
  /* ---------------- ciclo de la DEMO DE SAQUE (r66) --------------------
   * Los DOS mandos GLB, en pose de saque sobre la MESA REAL: el izquierdo
   * sostiene la bola del juego, el derecho (con la raqueta fantasma) la
   * saca. Física y sonidos de verdad: bote PROPIO → cruce → bote RIVAL →
   * «sin devolución: PUNTO». El paso 3 lo enseña pausado; el paso 5 lo
   * corre en bucle para anotar el marcador.                              */
  function tickDemoSaque(dt, esMarcador) {
    const b = G.ball;
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    demoFaseT += dt;
    if (demoTxt && demoTxt.t > 0) {
      demoTxt.t -= dt;
      if (repaintT <= 0) { paintStep(); repaintT = 0.3; }
    }
    switch (demoFase) {
      case 0: {
        // POSTURA: la bola espera en la palma del mando izquierdo
        G.tutBolaViva = false;
        posaBolaDemo();
        const espera = esMarcador ? 0.9 : 2.1;
        if (demoFaseT >= espera) {
          demoFase = 1; demoFaseT = 0;
          demoBote1 = false; demoBote2 = false;
        }
        break;
      }
      case 1: {
        // SUELTA: el gatillo de la demo suelta la bola (saque real)
        try {
          const { v, spin } = findServeVelocity(b.pos, 1, { x: 0.05, spd: 1.22 });
          b.vel.copy(v);
          b.spin.copy(spin);
        } catch (e) {
          b.vel.set(0.02, 2.6, -2.6);
          b.spin.set(0, 0, 0);
        }
        G.tutBolaViva = true;
        chime(false);
        demoFase = 2; demoFaseT = 0;
        break;
      }
      case 2: {
        // VUELO REAL: bote propio → cartel; bote rival → cartel
        if (!demoBote1 && b.vel.y > 0.3 && b.pos.z > C + 0.06 &&
            b.pos.y < TY + 0.35) {
          demoBote1 = true;
          demoTxt = { txt: T('tut_d3_p1'), col: 'rgba(232,180,90,0.32)', t: 1.5 };
          chime(true);
          if (!esMarcador) narra(['tutv3b']);
        } else if (demoBote1 && !demoBote2 && b.vel.y > 0.25 && b.pos.z < C - 0.05) {
          demoBote2 = true;
          demoTxt = { txt: T('tut_d3_p2'), col: 'rgba(232,89,12,0.32)', t: 1.5 };
          chime(true);
        }
        const fuera = b.pos.z < C - HL - 0.3 || b.pos.y < TY - 0.6;
        if (fuera || demoFaseT > 4.5) {
          demoFase = 3; demoFaseT = 0;
          demoTxt = { txt: T('tut_d3_pto'), col: 'rgba(47,158,68,0.35)', t: 1.4 };
          chime(true);
          if (esMarcador) anotaPuntoMarcador();
          else if (demoCiclos === 0) narra(['tutv3c']);
        }
        break;
      }
      case 3: {
        // PUNTO: pausa didáctica y la bola vuelve a la palma
        const pausa = esMarcador ? 0.7 : 1.5;
        if (demoFaseT >= pausa) {
          demoFase = 4; demoFaseT = 0;
          G.tutBolaViva = false;
          posaBolaDemo();
        }
        break;
      }
      case 4: {
        // RESET del ciclo
        const pausa = esMarcador ? 0.45 : 1.0;
        if (demoFaseT >= pausa) {
          demoCiclos++;
          demoFase = 0; demoFaseT = 0;
        }
        break;
      }
      default:
        demoFase = 0; demoFaseT = 0;
        break;
    }
  }
  /* anota el siguiente punto del marcador (paso 5) siguiendo las REGLAS
   * del árbitro: ganador alternado hasta 10-10, luego P·A·P·P a +2; el
   * sacador lo marca la ficha activa (2·2 y cada punto en la igualada) */
  function anotaPuntoMarcador() {
    if (!holoPips || demoPtos >= 24) return;
    const i = demoPtos;
    let ganaPlayer;
    if (i < 20) ganaPlayer = i % 2 === 0;
    else ganaPlayer = [true, false, true, true][i - 20];
    if (ganaPlayer) holoPips.__pi = Math.min(11, (holoPips.__pi || 0) + 1);
    else holoPips.__pd = Math.min(11, (holoPips.__pd || 0) + 1);
    demoPtos++;
    const deuce = demoPtos >= 20;
    if (deuce && !demoDeuce) {
      demoDeuce = true;
      if (holoTokens) holoTokens.cartel10.visible = true;
      narra(['tutv5b']);
      chime(false);
    }
    if (demoPtos >= 22 && holoCartel2) holoCartel2.visible = true;
    if (demoPtos >= 24) {
      // ¡JUEGO! flash del marcador y reinicio didáctico
      demoTxt = { txt: '11 - 10', col: 'rgba(47,158,68,0.4)', t: 2.4 };
      chime(true);
      setTimeout(() => {
        demoPtos = 0; demoDeuce = false;
        holoPips.__pi = 0; holoPips.__pd = 0;
        if (holoTokens) holoTokens.cartel10.visible = false;
        if (holoCartel2) holoCartel2.visible = false;
      }, 2600);
    }
    paintStep();
  }"""

sustituye(VIEJO_OK, NUEVO_OK, "accionMandoOk + helpers")

open(C13, "w", encoding="utf-8").write(txt)
print("patch _tick/accionMandoOk aplicado")
