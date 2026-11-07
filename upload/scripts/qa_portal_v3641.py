#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.41 · PODERES — SÚPER PORTAL, EL 4.º PODER DE PALA (capa AJ).

Petición del dueño (ronda 49): «Vamos a crear un nuevo superpoder de pala
"Super Portal"… el rival es el ordenador deberá penalizarlo de alguna
forma para que le resulte más complicado acertar el golpe» + spec completa
(8 s / 3 golpes · transición 0,12–0,20 s · desplazamiento lateral
0,25–0,70 m · variación vertical 0–0,15 m · conserva 90–100 % de la
rapidez · antirrebote 0,25 s · salida legal con bote jugable · NUNCA
segundo objeto físico ni colisiones fantasma).

FASE 43: el icono del dueño (SuperPala_Portal.png) entra en el registro
PODERES_PALA (4.º poder); la ventana la abre el gatillo (refresco honesto
como el imán); CADA golpe VÁLIDO del jugador en rally portaliza la salida
(swap ATÓMICO tras el enderezado 5.5 y ANTES del árbitro — la bola nunca
cruza la red físicamente); el rival IA sufre la bola marcada (c06:
predicción muerta + error ×1,6 + piernas ×0,75 + +10 % de fallo).

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del portal (estado, constantes, trigger,
     procesa con sus 7 pasos, bloque 5.55, penalización IA en c06, DIMS,
     registro, icono violeta, reset) + reglas intactas (las 3 ventanas
     previas + hook FASE 41 + anillo FASE 42).
  2) MECÁNICA REAL en headless — siembra portal ×2 → gatillo abre ventana
     (modo ACTIVO + anillo) → refresco SIN gasto → golpe portalizado:
     la bola REAPARECE en el campo rival con rapidez conservada, desviación
     legal y spin intacto; marca ppPortal puesta; carga gastada; evento
     del golpe NO consumido (el árbitro lo necesita); antirrebote 0,25 s;
     guards (saque, bola lenta, dirección contraria); 3 golpes → fin;
     PARTIDA NUEVA recoge todo; IA invalida su predicción con ppPortal.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    global ok, fails
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # ESTADO del portal (constructor)
        ('this._portalT = 0;                // s restantes de ventana',
         'estado: _portalT declarado (ventana del portal)'),
        ('this._portalGolpes = 0;           // golpes con portal restantes',
         'estado: _portalGolpes declarado (máx. 3 por activación)'),
        ('this._portalCd = 0;               // antirrebote entre golpes (0,25 s)',
         'estado: antirrebote 0,25 s declarado (spec del dueño)'),
        ('this._portalTrans = 0;            // tránsito visual restante (0,16 s)',
         'estado: tránsito visual declarado (0,12–0,20 s spec)'),
        ('this._portalFx = null;            // [fx0, fx1] canto violeta + onda',
         'estado: canto violeta propio del portal'),
        ('this._portalOndaA = null;         // anillo de ENTRADA (one-shot world)',
         'estado: anillo de ENTRADA en el mundo'),
        ('this._portalOndaB = null;         // anillo de SALIDA (one-shot world)',
         'estado: anillo de SALIDA en el mundo'),
        # CONSTANTES (spec completa del dueño)
        ('const PORTAL_DUR = 8;', 'spec: ventana de 8 s'),
        ('const PORTAL_GOLPES = 3;', 'spec: 3 golpes con portal por activación'),
        ('const PORTAL_LAT_MIN = 0.25;', 'spec: desviación lateral mínima 0,25 m'),
        ('const PORTAL_LAT_MAX = 0.70;', 'spec: desviación lateral máxima 0,70 m'),
        ('const PORTAL_VER_MAX = 0.15;', 'spec: variación vertical máxima 0,15 m'),
        ('const PORTAL_VEL_MIN = 0.90;', 'spec: conserva el 90–100 % de la rapidez'),
        ('const PORTAL_TRANS = 0.16;', 'spec: transición visual 0,16 s (0,12–0,20)'),
        ('const PORTAL_CD = 0.25;', 'spec: 0,25 s entre golpes portalizados'),
        # GATILLO + selección/reloj del modo activo (FASE 42 heredada)
        ("if (ent.id === 'portal') return this._portalTrigger(ent);",
         'gatillo: el poder seleccionado portal se libera'),
        ("this._megaActivaId = 'portal';",
         'gatillo: apertura y refresco marcan el modo ACTIVO'),
        ("if (ent.id === 'portal') return this._portalT > 0;",
         'FASE 42: ¿está activo el portal? en _megaSelActiva'),
        ("if (this._megaActivaId === 'portal') return this._portalT;",
         'FASE 42: el anillo lee SU ventana en _megaActivaRest'),
        ('() => { try { this._buildPortalFx(); } catch (e) { /* */ } },',
         'precaliente: el canto del portal se construye por adelantado'),
        # _portalProcesa: los 7 pasos de la spec
        ('if (!this.rules || this.rules.state !== \'rally\') return;',
         'procesa: DOBLE GUARD — solo rally (defensa en profundidad)'),
        ("e.type === 'paddle' && e.who === 'player' && !e.consumed)) return;",
         'procesa: SOLO tras impacto válido (evento sin consumir, spec)'),
        ('if (_portalTmpC.z > C - 0.12) _portalTmpC.z = C - 0.12;',
         'procesa: margen de red — la salida jamás se acerca al plano'),
        ('_portalProcesa() {', 'procesa: _portalProcesa definido'),
        ('if (sp < 2.0) return;                 // toque sin cuerpo: no hay portal',
         'procesa: un toque sin cuerpo NO portaliza (solo golpe válido)'),
        ('if (v.z > -0.5) return;               // debe marchar hacia el campo rival',
         'procesa: la bola debe marchar hacia el rival'),
        ('const zOut = C - 0.22;',
         'procesa: plano de salida pasado el plano de la red'),
        ('if (!(k > 0.04) || k > 1.1) return;   // salida imposible → golpe normal',
         'procesa: salida imposible → golpe NORMAL (spec: cancela)'),
        ('_portalTmpA.set(v.x * k, v.y * k + 0.5 * g * k * k, v.z * k).add(b.pos);',
         'procesa: proyección NATURAL con la gravedad (intención del golpe)'),
        ('const dLat = PORTAL_LAT_MIN +\n      Math.random() * (PORTAL_LAT_MAX - PORTAL_LAT_MIN);',
         'procesa: desviación lateral 0,25–0,70 m (no siempre la máxima)'),
        ('_portalTmpC.y = Math.max(DIMS.tableTopY + 0.07,',
         'procesa: la salida JAMÁS dentro de la mesa'),
        ('if (Math.abs(_portalTmpC.x) > 0.62) {',
         'procesa: zona legal — reduce la desviación al borde de mesa'),
        ('const newV = computeShotVelocity(_portalTmpC, _portalTmpD, T,',
         'procesa: el solver EXISTENTE garantiza el bote jugable'),
        ('const keep = sp * (PORTAL_VEL_MIN + Math.random() * (1 - PORTAL_VEL_MIN));',
         'procesa: conserva 90–100 % de la rapidez del golpe real'),
        ('b.vel.copy(newV);                     // spin: CONSERVADO (spec v1)',
         'procesa: swap ATÓMICO — posición + velocidad en el mismo frame'),
        ('b.ppPortal = true;                    // marca para la IA (c06)',
         'procesa: la bola queda MARCADA para penalizar a la IA'),
        ('if (ent) this._megaGasta(ent);',
         'procesa: CADA golpe portalizado gasta 1 carga'),
        ('this._portalCd = PORTAL_CD;           // antirrebote (spec: 0,25 s)',
         'procesa: antirrebote armado tras cada golpe'),
        ('this._portalFin();                  // golpes o cargas agotadas',
         'procesa: 3 golpes o cargas agotadas → fin'),
        # BLOQUE 5.55 (orden del frame: tras 5.5, antes del árbitro)
        ('if (presenting && this._portalT > 0 && this.rules.state === \'rally\' &&',
         '5.55: SOLO rally (el saque NO se portaliza) y ventana activa'),
        ('!(this.net.online && this.net.role === \'guest\')',
         '5.55: el invitado online no simula la bola (sin portal)'),
        ('try { this._portalProcesa(); } catch (eP0) { /* nunca rompe el frame */ }',
         '5.55: blindado — un error del portal JAMÁS tumba el frame'),
        # updateMega: reloj + seguridad
        ('if (this._portalCd > 0) this._portalCd -= dt;    // antirrebote SIEMPRE',
         'reloj: el antirrebote corre siempre (ventana o no)'),
        ('this._portalFin();               // fin natural (8 s agotados)',
         'reloj: fin natural de la ventana'),
        ('this._portalT = 0;                 // sin cargas: portal fuera YA',
         'reloj: sin cargas el portal se apaga YA (patrón imán)'),
        # TRÁNSITO visual + anillos del mundo
        ('this._portalTrans = PORTAL_TRANS;     // tránsito visual (0,16 s)',
         'tránsito: armado en cada golpe portalizado'),
        ('if (this._portalTrans > 0) {',
         'tránsito: la bola se hunde y reaparece (SOLO visual)'),
        ('if (this.ballMesh) this.ballMesh.scale.setScalar(1);   // tránsito a limpio',
         'reset: la escala de la bola se restaura (nada queda colgado)'),
        ('_portalOndaShow(pos, salida) {',
         'mundo: anillos violeta de entrada/salida (billboard)'),
        # REGISTRO + icono (4.º poder)
        ("{ id: 'portal', nombre: () => T('poder_portal'),",
         'registro: portal como 4.º poder de PODERES_PALA'),
        ("} else if (id === 'portal') {",
         'icono: dibujo de reserva del vórtice si el PNG no llega'),
        ("(activo === 'portal' ? '#a86bff' : '#5aa2ff'));",
         'FASE 42: el anillo de tiempo del portal es VIOLETA'),
        ('colHex === 0xa86bff ? 1.085 : 1.055);',
         'canto violeta: ×1,085 (no pelea con oro ni cian)'),
        # RESET FASE 41 heredado
        ('this._portalT = 0;\n    this._portalGolpes = 0;\n    this._portalWarn = false;',
         'reset: el portal duerme en CADA _megaNormReset'),
        ('if (this.ball.ppPortal) this.ball.ppPortal = false;',
         'reset: la marca de portal de la bola también se recoge'),
        # PENALIZACIÓN IA (c06) — petición del dueño
        ('if (ball.ppPortal) this.predictValid = false;',
         'IA: la predicción MUERE al cruzar el portal (reacción natural)'),
        ('(ball.ppPortal ? (DIMS.portalRivalErrMul || 1) : 1);',
         'IA: error de puntería amplificado ×portalRivalErrMul'),
        ('if (ball.ppPortal) vMulIA *= (DIMS.portalRivalVel || 1);',
         'IA: piernas lentas mientras sufre el portal'),
        ('(ball.ppPortal ? (DIMS.portalMissExtra || 0) : 0);',
         'IA: +portalMissExtra de fallo decidido'),
        # LIMPIEZA de la marca (la IA la limpia al devolver)
        ('ball.ppEfecto = false;   // v3.6.36: la devolución de la IA LIMPIA la marca\n    ball.ppPortal = false;   // v3.6.41: la devolución de la IA LIMPIA el portal',
         'IA: la devolución limpia la marca (golpe limpio)'),
        ('ball.ppEfecto = false;   // v3.6.36: el golpe torpe de la IA LIMPIA la marca\n    ball.ppPortal = false;   // v3.6.41: el golpe torpe LIMPIA el portal',
         'IA: el golpe torpe también la limpia'),
        # DIMS (c02)
        ('portalRivalErrMul: 1.6,', 'DIMS: error IA ×1,6'),
        ('portalRivalVel: 0.75,', 'DIMS: piernas IA ×0,75'),
        ('portalMissExtra: 0.10,', 'DIMS: +10 % de fallo decidido'),
        # i18n ES/EN
        ("arc_portal_go: '¡SÚPER PORTAL! · la bola cruza el vórtice · 8 s / 3 golpes',",
         'i18n: mensaje de apertura ES'),
        ("arc_portal_fin: 'SÚPER PORTAL agotado',", 'i18n: mensaje de fin ES'),
        ("poder_portal: '¡PORTAL DIMENSIONAL!',", 'i18n: nombre del poder ES'),
        ("arc_portal_go: 'SUPER PORTAL! · the ball crosses the vortex · 8 s / 3 hits',",
         'i18n: mensaje de apertura EN'),
        ("poder_portal: 'DIMENSIONAL PORTAL!',", 'i18n: nombre del poder EN'),
        # REGLAS INTACTAS (regresión rondas 45-48)
        ('const MEGA_DUR = 15;', 'mega: ventana 15 s intacta'),
        ('const EFECTO_DUR = 8;', 'efecto: ventana 8 s intacta'),
        ('const IMAN_DUR = 8;', 'imán: ventana 8 s intacta'),
        ('const MEGA_TOPE = 3;', 'tope ×3 de cargas intacto'),
        ('const MEGA_GOLPES = 11;', 'carga por rally 11+ intacta'),
        ('const MEGA_LOD_JUEGO = 0.5;', 'LOD 50 % en juego intacto'),
        ('const MEGA_LOD_MIRA = 0.978;', 'LOD 100 % con la mirada intacto'),
        ("this._megaActivaId = null;        // 'mega' | 'efecto' | 'iman' | null",
         'FASE 42: modo activo intacto (comentario histórico)'),
        ('try { if (this.onMatchStart) this.onMatchStart(); } catch (e) { /* nunca rompe el árbitro */ }',
         'FASE 41: el hook de partida nueva sigue avisando'),
        ('V3.6.41-SDK6', 'sello de versión servida'),
    ]:
        chk(needle in game, label)
    chk(game.count("this._megaActivaId = 'portal';") == 2,
        'portal: exactamente apertura + refresco marcan el modo')
    chk(game.count('ball.ppPortal = false;') == 3,
        'marca ppPortal: la limpian la IA (2) y el reset (1) — y solo ellas')
    chk('PNG_PODER_PORTAL' in game and 'SuperPala_Portal.png' in game,
        'assets: PNG del dueño embebido (data-URI) y citado')
    chk("data:audio/mpeg;base64," in game and game.count('VOZ_PODER_PORTAL') >= 3,
        'assets: voces ES/EN del portal embebidas')

    # ---------- 2 · MECÁNICA REAL (headless) ----------
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--autoplay-policy=no-user-gesture-required",
        ])
        page = await browser.new_page(viewport={"width": 1280, "height": 800})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(7000)

        rt = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const out = {};
          if (!G) { out.sinJuego = true; return out; }
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          try { localStorage.removeItem('pp_mega_norm_hint'); } catch (e) { /* */ }
          try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
          G.palaMejorada = true;
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const rndReal = Math.random;
          const TZ = -1.6, TY = 0.76;          // DIMS.tableCenterZ / tableTopY

          // · ARRANQUE limpio + precaliente drenado
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          Math.random = () => 0.9;               // 0.9×4 → SIEMPRE 'portal'
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errU0 = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errU1 = String(e); }
          for (let i = 0; i < 10; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errD = String(e); }
          }
          // 2.ª carga PORTAL (×2): frame en 'point' entre ventanas
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errGP = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errG2 = String(e); }
          out.sembrado = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'portal' && G._megaMatriz[0].n === 2;

          // · GATILLO: la ventana ABRE (modo ACTIVO + anillo, 3 golpes)
          let tP = null;
          try { tP = G.megaTrigger(libre); } catch (e) { out.errP1 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errP2 = String(e); }
          out.ventanaAbre = tP === true && G._portalT > 7.9 &&
            G._portalGolpes === 3;
          out.iconoModoActivo = G._megaIconOn === true &&
            G._megaIconModo === 'act' && G._megaActivaId === 'portal';
          out.durAnillo = G._megaActivaDur === 8;
          out.anilloAlDia = G._megaActivaFrac > 0.9 && G._megaActivaFrac <= 1;

          // · REFRESCO honesto SIN gasto (2.º gatillo, patrón imán)
          let tP2 = null;
          try { tP2 = G.megaTrigger(libre); } catch (e) { out.errP3 = String(e); }
          out.refrescaSinGasto = tP2 === true && G._portalT > 7.9 &&
            G._megaMatriz.find((x) => x.id === 'portal').n === 2;

          // · GOLPE PORTALIZADO (la vía REAL: bloque 5.55 → _portalProcesa)
          //    bola recién golpeada por el jugador, marchando hacia la IA
          G.rules.state = 'rally';
          const b = G.ball;
          b.pos.set(0.10, 1.02, 0.55);
          b.spin.set(2, -1, 4);                 // spin real del golpe
          b.vel.set(-0.35, 0.55, -6.2);         // hacia el campo rival
          const sp0 = b.vel.length();
          const spin0 = b.spin.clone();
          const pos0 = b.pos.clone();
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          G._portalCd = 0;
          try { G._portalProcesa(); } catch (e) { out.errX1 = String(e); }
          out.reapareceEnCampoRival = b.pos.z < (TZ - 0.1);
          out.zonaLegalX = Math.abs(b.pos.x) <= 0.63;
          out.sobreLaMesa = b.pos.y > TY;
          const sp1 = b.vel.length();
          out.rapidezConservada = sp1 >= sp0 * 0.88 && sp1 <= sp0 * 1.02;
          out.haciaElRival = b.vel.z < -0.5;
          out.spinIntacto = Math.abs(b.spin.x - spin0.x) < 1e-6 &&
            Math.abs(b.spin.z - spin0.z) < 1e-6;
          out.marcaIA = b.ppPortal === true;
          out.cargaGastada = G._megaMatriz.find((x) => x.id === 'portal')
            ? G._megaMatriz.find((x) => x.id === 'portal').n === 1
            : false;
          out.golpesQuedan2 = G._portalGolpes === 2;
          out.eventoNoConsumido = G.events.length === 1 &&
            !G.events[0].consumed;              // el árbitro lo necesita
          out.transitoArmado = G._portalTrans > 0 && G._portalTrans <= 0.17;
          out.anilloEntrada = !!G._portalOndaA && G._portalOndaA.visible;
          out.anilloSalida = !!G._portalOndaB && G._portalOndaB.visible;
          out.salidaDistinta = b.pos.distanceTo(pos0) > 0.5;

          // · DESVIACIÓN VIVA: dos golpes más, salidas DISTINTAS (no es un
          //    teletransporte fijo — cada portal calcula SU salida)
          const x1 = b.pos.x;
          b.pos.set(0.05, 1.0, 0.55); b.vel.set(-0.3, 0.5, -6.0);
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          G._portalCd = 0;
          Math.random = () => 0.45;
          try { G._portalProcesa(); } catch (e) { out.errX2 = String(e); }
          const x2 = b.pos.x;
          b.pos.set(0.05, 1.0, 0.55); b.vel.set(-0.3, 0.5, -6.0);
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          G._portalCd = 0;
          Math.random = () => 0.85;
          try { G._portalProcesa(); } catch (e) { out.errX3 = String(e); }
          const x3 = b.pos.x;
          out.desviacionViva = Math.abs(x2 - x1) > 0.02 ||
            Math.abs(x3 - x2) > 0.02;

          // · ANTIRREBOTE 0,25 s: el golpe inmediato NO portaliza
          G._portalCd = 0.25;
          b.pos.set(0.05, 1.0, 0.55); b.vel.set(-0.3, 0.5, -6.0);
          const zAntes = b.pos.z;
          try { G._portalProcesa(); } catch (e) { out.errX4 = String(e); }
          out.antirrebote = Math.abs(b.pos.z - zAntes) < 1e-6;

          // · GUARDS: saque / bola lenta / dirección contraria
          G._portalCd = 0;
          G.rules.state = 'serve';
          b.pos.set(0.05, 1.0, 0.55); b.vel.set(-0.3, 0.5, -6.0);
          const zServe = b.pos.z;
          try { G._portalProcesa(); } catch (e) { out.errX5 = String(e); }
          out.guardSaque = Math.abs(b.pos.z - zServe) < 1e-6;
          G.rules.state = 'rally';
          b.vel.set(0, 0.3, 0.8);              // lenta y hacia el jugador
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 1,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          const zLenta = b.pos.z;
          try { G._portalProcesa(); } catch (e) { out.errX6 = String(e); }
          out.guardBolaLenta = Math.abs(b.pos.z - zLenta) < 1e-6;
          b.vel.set(0, 0.5, 6.0);              // rápida pero al revés
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          const zRev = b.pos.z;
          try { G._portalProcesa(); } catch (e) { out.errX7 = String(e); }
          out.guardDireccion = Math.abs(b.pos.z - zRev) < 1e-6;

          // · EXPIRACIÓN por TIEMPO: ventana a cero e icono vuelve a
          //    inventario (repongo ×1: el portal ya gastó las suyas)
          Math.random = rndReal;
          if (!G._megaMatriz.find((x) => x.id === 'portal')) {
            G._megaMatriz.push({ id: 'portal', n: 1 });
          }
          G._portalT = 0.005;                  // un frame (1/60) la cruza
          try { G.updateMega(1 / 60); } catch (e) { out.errP4 = String(e); }
          out.expiraTiempo = G._portalT === 0 &&
            G._megaIconModo === 'inv' && G._megaIconOn === true;

          // · GOLPES AGOTADOS: 3 golpes portalizados cierran la ventana
          //    (repongo con 3 cargas: cada golpe se bebe la suya)
          G.rules.state = 'rally';
          if (!G._megaMatriz.find((x) => x.id === 'portal')) {
            G._megaMatriz.push({ id: 'portal', n: 3 });
          } else {
            G._megaMatriz.find((x) => x.id === 'portal').n = 3;
          }
          G._portalT = 8; G._portalGolpes = 3; G._portalCd = 0;
          for (let i = 0; i < 3; i++) {
            b.pos.set(0.05, 1.0, 0.55);
            b.vel.set(-0.3, 0.5, -6.0);
            G.events.length = 0;
            G.events.push({ type: 'paddle', who: 'player', speed: 6,
              pos: b.pos.clone(), paddleIndex: G.paddleHand });
            G._portalCd = 0;
            try { G._portalProcesa(); } catch (e) { out.errX8 = String(e); }
          }
          out.finPorGolpes = G._portalGolpes === 0 &&
            (G._megaMatriz.find((x) => x.id === 'portal') === undefined ||
             G._megaMatriz.find((x) => x.id === 'portal') === null);

          // · SIN CARGAS la ventana se apaga YA (updateMega la recoge)
          if (!G._megaMatriz.find((x) => x.id === 'portal')) {
            G._megaMatriz.push({ id: 'portal', n: 1 });
          }
          G._portalT = 8; G._portalGolpes = 3;
          const ix = G._megaMatriz.findIndex((x) => x.id === 'portal');
          G._megaMatriz.splice(ix, 1);        // cargas agotadas → fuera
          try { G.updateMega(1 / 60); } catch (e) { out.errP5 = String(e); }
          out.sinCargasFuera = G._portalT === 0 && G._portalGolpes === 0;

          // · IA PENALIZADA (c06): la marca ppPortal MATA la predicción
          G.rules.startMatch('match');        // pala limpia (FASE 41)
          const ai = G.ai;
          if (ai) {
            ai.predictValid = true;           // la IA «perseguía» la bola vieja
            const ballIA = G.ball;
            ballIA.ppPortal = true;           // …pero la bola cruzó un portal
            ballIA.vel.set(0, -1, -6 * Math.sign(ballIA.vel.z || 1) || -6);
            ballIA.vel.set(0, -1, -6);
            try {
              ai.update(1 / 60, ballIA, { canHit: false, validBounce: false });
            } catch (e) { out.errA1 = String(e); }
            out.iaPrediccionMuere = ai.predictValid === false;
          } else { out.iaPrediccionMuere = false; }
          out.partidaNuevaLimpia = G._portalT === 0 && G._portalGolpes === 0 &&
            G._portalCd === 0 && G._portalTrans === 0 &&
            G._megaActivaId === null && G._megaIconOn === false;

          Math.random = rndReal;
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'window.__PP_GAME disponible (juego vivo)')
        else:
            chk(rt.get('sembrado') is True,
                'siembra: portal ×2 en la matriz (dos rallyes de 11)')
            chk(rt.get('ventanaAbre') is True,
                'gatillo: la ventana del portal abre (8 s / 3 golpes)')
            chk(rt.get('iconoModoActivo') is True,
                'FASE 42 heredada: el icono pasa a modo ACTIVO con el portal')
            chk(rt.get('durAnillo') is True, 'anillo: ventana de 8 s de referencia')
            chk(rt.get('anilloAlDia') is True, 'anillo al día tras el primer frame')
            chk(rt.get('refrescaSinGasto') is True,
                'gatillo 2.º: REFRESCA sin gastar (honesto como el imán)')
            chk(rt.get('reapareceEnCampoRival') is True,
                'PORTAL: la bola REAPARECE en el campo rival (jamás cruza la red)')
            chk(rt.get('zonaLegalX') is True, 'PORTAL: salida en zona legal (|x| ≤ 0,63)')
            chk(rt.get('sobreLaMesa') is True, 'PORTAL: salida JAMÁS dentro de la mesa')
            chk(rt.get('rapidezConservada') is True,
                'PORTAL: conserva 90–100 % de la rapidez del golpe real')
            chk(rt.get('haciaElRival') is True, 'PORTAL: la salida marcha hacia el rival')
            chk(rt.get('spinIntacto') is True, 'PORTAL: spin CONSERVADO (spec v1)')
            chk(rt.get('marcaIA') is True, 'PORTAL: bola marcada para la IA (ppPortal)')
            chk(rt.get('cargaGastada') is True,
                'PORTAL: CADA golpe consume 1 carga (×2 → ×1)')
            chk(rt.get('golpesQuedan2') is True, 'PORTAL: contador de golpes 3 → 2')
            chk(rt.get('eventoNoConsumido') is True,
                'ÁRBITRO INTACTO: el evento del golpe NO se consume (lo registra él)')
            chk(rt.get('transitoArmado') is True,
                'TRÁNSITO visual armado (0,16 s — solo cosmético)')
            chk(rt.get('anilloEntrada') is True, 'anillo de ENTRADA visible')
            chk(rt.get('anilloSalida') is True, 'anillo de SALIDA visible')
            chk(rt.get('salidaDistinta') is True,
                'PORTAL: la salida se aleja >0,5 m de la trayectoria natural')
            chk(rt.get('desviacionViva') is True,
                'PORTAL: la desviación es VIVA (dos portales, salidas distintas)')
            chk(rt.get('antirrebote') is True,
                'ANTIRREBOTE 0,25 s: el golpe inmediato NO portaliza (spec)')
            chk(rt.get('guardSaque') is True,
                'guard SAQUE: en state serve no hay portal')
            chk(rt.get('guardBolaLenta') is True,
                'guard BOLA LENTA: un toque sin cuerpo no portaliza')
            chk(rt.get('guardDireccion') is True,
                'guard DIRECCIÓN: la bola debe marchar hacia el rival')
            chk(rt.get('expiraTiempo') is True,
                'EXPIRACIÓN por tiempo: icono vuelve a inventario (queda carga)')
            chk(rt.get('finPorGolpes') is True,
                '3 GOLPES portalizados: la ventana cierra y la carga se va')
            chk(rt.get('sinCargasFuera') is True,
                'sin cargas: el portal se apaga YA (patrón imán)')
            chk(rt.get('iaPrediccionMuere') is True,
                'IA PENALIZADA: la predicción muere con la bola del portal')
            chk(rt.get('partidaNuevaLimpia') is True,
                'PARTIDA NUEVA: el portal duerme entero (FASE 41 heredada)')

        for e in errors[:5]:
            print('  ✗ pageerror:', e)
        chk(len(errors) == 0, 'cero pageerrors durante la prueba')

        await browser.close()

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
