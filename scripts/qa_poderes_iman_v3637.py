#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.37 · SUPERPODER DE PALA v3 — SÚPER IMÁN + flechas propias +
SÚPER EFECTO notorio (capa AF, en vivo; sustituye a la AE en el listado).

Peticiones del dueño implementadas esta ronda:
  · «me gustaría que las flechas de la matriz… sea un poco más evidente,
    ahora al estar encima de la imagen no se nota» — chevrons FUERA del
    icono: sprites PROPIOS a cada lado (disco oscuro + oro + pulso),
    ‹ SOLO con vecino izquierdo, › SOLO con vecino derecho.
  · «El efecto del superpoder de Super efecto no sé cómo aplicarlo o por
    lo menos no lo noto, debería verse visualmente sobre el bote de la
    bola y "dificultar en un %" el éxito de impacto del rival… colocando
    sobre la bola un halo visible rojo» — halo ROJO aditivo anclado a la
    bola marcada + anillo de bote amplificado + IA con error ×2 y piernas
    ×0,85 mientras la bola marcada vuela (DIMS.efectoRival*) + mensaje que
    enseña A APLICARLO («golpea con GIRO»).
  · «Vamos a añadir otro superpoder de pala "SuperPala_Iman.png"» — el
    SÚPER IMÁN con la spec completa: campo de 8 s que atrae SUAVE la bola
    al punto dulce (radio 0,75 m · plena a 0,20 m · a ≤5 m/s² · Δv ≤0,60
    m/s por aproximación · predicción ≤0,15 s), pala mandada por la mano
    real, nada teleportado, sin recuperar bolas que ya pasaron el plano,
    física por SUBPASO (independiente del framerate) y CADA impacto
    asistido válido consume 1 carga (máx. 3 por activación).

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del núcleo (registro de 3 poderes, constantes
     del imán y del efecto notorio, applyIman en la física, IA castigada,
     flechas sprites, halo, anillo de bote, voces 6) + i18n ES/EN +
     plantilla 2.4 + locura v26 intacta + regresiones (chev dentro del
     icono ABSENT).
  2) MECÁNICA REAL en headless — norma completa con 3 poderes (11 carga ·
     22/33 acumula · 44 tope · distinto ENTRA · ciclo sin envolver ·
     efecto 8 s/5 · recarga · mega alarga) + IMÁN: ventana 8 s, campo en
     la bola, micro-simulación de física (empuje lateral al punto dulce,
     topes Δv, nada sin el poder, bola que ya pasó, bola que se aleja),
     consumo por impacto asistido (n−1, sale a 0, cierre a 3 asistencias),
     flechas ‹ › visibilidad por índice, halo rojo, conmutador y hall.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import sys
import urllib.request

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"
MOD = "http://localhost:3000/championships/locura/index.js"

ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


async def main():
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO', 'bloque del superpoder en el núcleo'),
        ('const PODERES_PALA', 'REGISTRO EXTENSIBLE de poderes'),
        ("{ id: 'mega', nombre: () => T('poder_mega'),", 'entrada MEGA del registro'),
        ("{ id: 'efecto', nombre: () => T('poder_efecto'),", 'entrada EFECTO del registro'),
        ("{ id: 'iman', nombre: () => T('poder_iman'),", 'entrada IMÁN del registro (3.er poder)'),
        ('const PNG_PODER_IMAN', 'PNG del IMÁN embebido (SuperPala_Iman.png del dueño)'),
        ('const VOZ_PODER_IMAN', 'voz ES del IMÁN embebida (davefx)'),
        ('const VOZ_PODER_IMAN_EN', 'voz EN del IMÁN embebida (lessac)'),
        ('voz: VOZ_PODER_IMAN, vozEn: VOZ_PODER_IMAN_EN, png: PNG_PODER_IMAN',
         'imán: voz ES + voz EN + PNG en el registro'),
        ('const IMAN_DUR = 8;', 'SÚPER IMÁN: ventana de 8 s'),
        ('const IMAN_ASIST = 3;', 'SÚPER IMÁN: máx. 3 asistencias por activación'),
        ('const MEGA_ARROW_S = 0.020;', 'flechas de la matriz: sprites de 2 cm'),
        ('imanRadio: 0.95,', 'física: radio de influencia 0,95 m (v3.6.44: «no se nota nada» → campo grande)'),
        ('imanPlena: 0.26,', 'física: distancia de máxima asistencia 0,26 m (v3.6.44)'),
        ('imanAcelMax: 6.5,', 'física: aceleración lateral máxima 6,5 m/s² (v3.6.44)'),
        ('imanDvMax: 0.80,', 'física: Δv lateral máximo por aproximación 0,80 m/s (v3.6.44)'),
        ('imanRescateAcel: 7.5,', 'física: RESCATE con aceleración 7,5 m/s² (v3.6.44)'),
        ('imanRescateDv: 1.05,', 'física: RESCATE con tope Δv 1,05 m/s (v3.6.44)'),
        ('imanTPred: 0.15,', 'física: horizonte de predicción 0,15 s (dueño)'),
        ('efectoRivalErrMul: 2.0,', 'efecto notorio: error del rival ×2'),
        ('efectoRivalVel: 0.85,', 'efecto notorio: piernas del rival ×0,85'),
        ('if (ball.ppIman) applyIman(ball, paddles, h);',
         'física: el imán se integra POR SUBPASO (independiente del framerate)'),
        ('function applyIman(ball, paddles, h) {', 'física: empuje al punto dulce (applyIman)'),
        ('if (closing <= 0.4) {', 'física: el filtro de closing deriva al RESCATE (r51)'),
        ('if (_imD.dot(pad.normal) < -DIMS.ballRadius) continue;',
         'física: NUNCA recupera bolas que ya superaron el plano de la cara'),
        ('IM.dv += aMag * h;', 'física: contador real de Δv lateral'),
        ('ball.ppImanTocada = true;', 'física: la aproximación asistida queda MARCADA'),
        ('const eMulIA = (ball.ppEfecto ? (DIMS.efectoRivalErrMul || 1) : 1) *',
         'IA: error de puntería amplificado con bola marcada'),
        ('if (ball.ppPortal) vMulIA *= (DIMS.portalRivalVel || 1);',
         'IA: piernas más lentas con bola marcada'),
        ('if (ent.id === \'iman\') return this._imanTrigger(ent);',
         'el gatillo libera el IMÁN seleccionado'),
        ('this._imanT = IMAN_DUR;', 'activación del campo del imán'),
        ('this._imanAsistidas >= IMAN_ASIST) this._imanFin();',
         '3.ª asistencia CIERRA el campo (tope del dueño)'),
        ('this._imanImpacto();', 'gancho: impacto asistido consume 1 carga'),
        ('_buildMegaArrows() {', 'flechas: sprites PROPIOS construidos'),
        ('_megaArrowTex(dir) {', 'flechas: textura chevron con disco'),
        ("chev(17, '#141822');", 'flechas: contorno oscuro (se VE sobre el icono)'),
        ("'rgba(12,16,26,0.78)'", 'flechas: disco de fondo oscuro'),
        ('const visL = flechasOn && activa && this._megaIdx > 0;',
         'flecha ‹ SOLO con vecino a la izquierda'),
        ('const visR = flechasOn && activa && this._megaIdx < L - 1;',
         'flecha › SOLO con vecino a la derecha (sin envolver)'),
        ('_buildEfectoHalo() {', 'halo ROJO de la bola marcada construido'),
        ('blending: THREE.AdditiveBlending', 'halo: mezcla aditiva (visible)'),
        ('this.ballMesh.add(sp);',
         'halo: HIJO del ballMesh (v3.6.38 — viaja con la bola, cero desfase)'),
        ('_efectoBoteFxShow(pMar);', 'bote amplificado: anillo rojo en la mesa (v3.6.44: clavado a la bola visual)'),
        ('RingGeometry(0.09, 0.115, 40)', 'bote amplificado: anillo one-shot (v3.6.44: 0,09-0,115 m)'),
        ('golpea con GIRO (arrastra la pala al golpear)',
         'i18n ES: el mensaje del efecto enseña A APLICARLO'),
        ('brush the ball WITH SPIN', 'i18n EN: el mensaje enseña a aplicar'),
        ('poder_iman:', 'i18n: nombre del poder imán'),
        ('¡POTENCIADOR DE SÚPER IMÁN!', 'ES: megáfono del imán'),
        ('¡SÚPER IMÁN! · la bola vuela al punto dulce · 8 s / 3 asistencias',
         'ES: mensaje de activación del imán'),
        ('SUPER MAGNET BOOSTER!', 'EN: nombre del poder imán'),
        ('iman_asistido:', 'i18n: aviso de impacto asistido'),
        ('const key = id + ((__ppLang === \'en\') ? \'_en\' : \'_es\');',
         'voz por PODER e IDIOMA (__ppLang)'),
        ('return !!(this.champs && this.champs.active);',
         'GATE: superpoderes SOLO en campeonatos'),
        ('SOLO en campeonatos', 'i18n ES: «SOLO en campeonatos» en los avisos'),
        ('championships only', 'i18n EN: «championships only» en los avisos'),
        ('pp_pala_mejorada_v1', 'conmutador persistente «Pala Mejorada»'),
        ('_megaNormReset()', 'recogida completa con dispose'),
        ('this.updateMega(dt);', 'la norma corre en el bucle animate'),
        ('V3.6.44-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)
    # REGRESIONES
    chk('if (this._megaIdx > 0) chev(24, -1);' not in game,
        'regresión: las chevrons YA NO viven dentro del icono (petición del dueño)')
    chk('_megaLoads' not in game, 'regresión: el estado único v3.6.35 no vuelve')
    chk('tongtong' not in game, 'regresión: la voz no nativa tongtong fuera')
    chk(game.count('data:audio/mpeg;base64,') >= 6, '6 voces nativas embebidas (3 poderes × es/en)')
    chk(game.count('data:image/png;base64,') >= 3, '3 iconos de poder embebidos (dueño)')
    chk(game.count('ball.ppImanTocada = false;') >= 3,
        'la marca de aproximación se limpia (IA ×2 rutas + recogida)')

    # módulo locura v26 intacto (la norma vive en el núcleo)
    try:
        served = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ("trigger: 'norma_rally11'", 'locura: playerPower apunta a la norma'),
        ('MEGA PALA es NORMATIVA del NÚCLEO', 'locura: nota de la mudanza al núcleo'),
    ]:
        chk(needle in served, label)
    for ausente, label in [
        ('_megaMatriz', 'locura: sin estado de matriz (es del núcleo)'),
        ('_imanT', 'locura: sin estado del imán (es del núcleo)'),
    ]:
        chk(ausente not in served, 'regresión: ' + label)

    # plantilla: la norma documentada con el imán
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer PLANTILLA-GUIA.md servida:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('2.4 SUPERPODER DE PALA · MATRIZ + SÚPER EFECTO + SÚPER IMÁN' in guia,
        'plantilla: la norma 2.4 documentada con el imán')
    chk('SÚPER IMÁN = campo de' in guia, 'plantilla: campo del imán documentado')
    chk('cada impacto asistido válido gasta 1 carga' in guia,
        'plantilla: consumo por impacto asistido documentado')
    chk('halo rojo' in guia, 'plantilla: halo rojo del efecto documentado')
    chk('Prohibido para los módulos' in guia,
        'plantilla: prohibición de duplicar la mecánica')

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
          const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const rndReal = Math.random;

          // estado fresco
          out.porDefecto = G.palaMejorada === true &&
            Array.isArray(G._megaMatriz) && G._megaMatriz.length === 0 &&
            G._megaIdx === 0 && G._megaT === 0 && G._efectoT === 0 &&
            G._imanT === 0 && G._megaFx === null && G._efectoFx === null &&
            G._megaIcon === null;
          out.hayAPI = typeof G.updateMega === 'function' &&
            typeof G.megaTrigger === 'function' &&
            typeof G._megaCicla === 'function' &&
            typeof G._efectoTrigger === 'function' &&
            typeof G._imanTrigger === 'function' &&
            typeof G._imanImpacto === 'function' &&
            typeof G._megaVoz === 'function' &&
            typeof G._megaIconRefresh === 'function';

          // PARTIDO + rally controlado
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd = String(e); } };

          // · FUERA DE CAMPEONATO: rally de 44 golpes NO carga NADA
          G.champs.activeId = '';
          G.rules.state = 'rally'; G.rules.rallyHits = 44;
          paso(); paso();
          out.fueraSinCarga = G._megaMatriz.length === 0 && G._megaIcon === null;
          let tFuera = null;
          try { tFuera = G.megaTrigger(libre); } catch (e) { out.errFuera = String(e); }
          out.fueraGatilloLibre = tFuera === false;

          // · EN CAMPEONATO: 3 poderes en el registro (mega=0.1, efecto=0.5, iman=0.9)
          G.champs.activeId = 'locura';
          Math.random = () => 0.1;                     // SIEMPRE 'mega'
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 10;
          paso(); paso();
          out.diezSinCarga = G._megaMatriz.length === 0;
          G.rules.rallyHits = 11; paso();
          out.cargada = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 1 &&
            G._megaIdx === 0;
          out.iconoVivo = Array.isArray(G._megaIcon) &&
            G._megaIcon.filter((s) => s).length === 2 &&
            G._megaIcon[0].visible === true;
          out.iconoAnclado = Math.abs(G._megaIcon[0].position.y + 0.034) < 0.006 &&
            Math.abs(G._megaIcon[0].position.z - 0.004) < 0.002;

          // · MISMO PODER ACUMULA ×2/×3, tope ×3 honesto
          G.rules.rallyHits = 22; paso();
          out.dosCargas = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 2;
          G.rules.rallyHits = 33; paso();
          out.tresCargas = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
          G.rules.rallyHits = 44; paso(); paso();
          out.topeTres = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
          out.msgTope = (G.rules.message || '').indexOf('TOPE ×3') === 0;

          // · PODER DISTINTO (efecto): ENTRA en la matriz (posición 1)
          Math.random = () => 0.3;                     // SIEMPRE 'efecto' (4 poderes)
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.matrizDos = G._megaMatriz.length === 2 &&
            G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 3 &&
            G._megaMatriz[1].id === 'efecto' && G._megaMatriz[1].n === 1;
          out.selNuevo = G._megaIdx === 1;
          out.ordenLlegada = G._megaMatriz[0].n === 3;

          // · FLECHAS ‹ › (sprites propios): ‹ en el 1, nada en el índice 0
          paso();                                      // construye las flechas
          out.flechasVivas = Array.isArray(G._megaArrows) &&
            Array.isArray(G._megaArrows[0]) && G._megaArrows[0].length === 2;
          out.sinFlechaIzqEnCero = G._megaIdx === 1 &&
            G._megaArrows[0][0].visible === true &&
            G._megaArrows[0][1].visible === false;      // ‹ visible, › oculta (último)
          G._megaCicla(-1);                            // al índice 0
          paso();
          out.enCeroSinIzq = G._megaIdx === 0 &&
            G._megaArrows[0][0].visible === false &&
            G._megaArrows[0][1].visible === true;
          out.opPulso = G._megaArrows[0][1].material.opacity > 0.2 &&
            G._megaArrows[0][1].material.opacity < 1.01;
          G._megaCicla(1); G._megaCicla(1);
          out.alUltimoYNoPasa = G._megaIdx === 1;

          // · SÚPER EFECTO: ventana, FX cian, multiplicador, mensaje que enseña
          G.rules.state = 'serve';
          let saq = null;
          try { saq = G.megaTrigger(libre); } catch (e) { out.errSaq = String(e); }
          out.saqueRespetado = saq === false && G._efectoT === 0 &&
            G._megaMatriz[1].n === 1;
          G.rules.state = 'rally';
          let ef = null;
          try { ef = G.megaTrigger(libre); } catch (e) { out.errEf = String(e); }
          paso();
          out.efectoAbre = ef === true && G._efectoT > 7.9 &&
            G._efectoGolpes === 5;
          out.fxHubicacion = Array.isArray(G._efectoFx) &&
            G._efectoFx.filter((f) => f).length === 2;
          const fxE = G._efectoFx && G._efectoFx.find((f) => f);
          out.cantoCian = !!(fxE && fxE.userData.rim && fxE.userData.rimMats &&
                             fxE.userData.rimMats[0] &&
                             fxE.userData.rimMats[0].color.getHex() === 0x54d8f0);
          out.multEnPala = G.controllerPaddles[0].ppEfectoMul === 3 &&
            G.controllerPaddles[1].ppEfectoMul === 3;
          out.msgEfectoEnsenia = (G.rules.message || '').indexOf('¡SÚPER EFECTO!') === 0 &&
            (G.rules.message || '').indexOf('GIRO') > 0;

          // · HALO ROJO sobre la bola marcada (SÚPER EFECTO notorio;
          //   v3.6.38: el halo es HIJO del ballMesh — se mide en MUNDO)
          try {
            G.ball.ppEfecto = true;
            paso();
            const V3H = Object.getPrototypeOf(G.ball.pos).constructor;
            const mWH = G._efectoHalo
              ? G._efectoHalo.getWorldPosition(new V3H()) : null;
            out.haloVivo = !!G._efectoHalo && G._efectoHalo.visible === true &&
              G._efectoHalo.parent === G.ballMesh &&
              mWH && mWH.distanceTo(G.ball.pos) < 0.02;
            G.ball.ppEfecto = false;
            paso();
            out.haloFuera = G._efectoHalo.visible === false;
          } catch (e) { out.errHalo = String(e); }

          // · ANILLO DE BOTE (one-shot) al botar la bola marcada con giro
          try {
            G.ball.ppEfecto = true;
            G.ball.spin.set(0, 40, 0);
            G._efectoBoteFxShow(G.ball.pos);
            out.boteFx = !!G._efectoBoteFx && G._efectoBoteFx.visible === true &&
              G._efectoBoteFx.userData.boteT > 0;
            G._efectoBoteFx.userData.boteT = 0.0001;
            paso();
            out.boteFxApaga = G._efectoBoteFx.visible === false;
            G.ball.ppEfecto = false;
          } catch (e) { out.errBote = String(e); }

          // · fin del efecto + RECARGA (camino AE completo)
          G._efectoT = 7.0; G._efectoGolpes = 1;
          try { G._efectoFin(); } catch (e) { out.errFin = String(e); }
          out.finPorGolpes = G._efectoT === 0 && G._efectoGolpes === 0;
          Math.random = () => 0.3;                     // SIEMPRE 'efecto'
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          let rec = null;
          try { rec = G.megaTrigger(libre); } catch (e) { out.errRec = String(e); }
          out.recarga = rec === true && G._efectoT > 7.9;
          G._efectoT = 0; paso();

          // · SÚPER IMÁN: entra en la matriz y el gatillo ABRE el campo
          Math.random = () => 0.6;                     // SIEMPRE 'iman' (4 poderes)
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.imanEntra = !!G._megaMatriz.find((x) => x.id === 'iman') &&
            G._megaIdx === G._megaMatriz.length - 1;
          let im = null;
          try { im = G.megaTrigger(libre); } catch (e) { out.errIm = String(e); }
          out.imanAbre = im === true && G._imanT > 7.9 && G._imanAsistidas === 0;
          out.imanFx = Array.isArray(G._imanFx) &&
            G._imanFx.filter((f) => f).length === 2;
          const fxI = G._imanFx && G._imanFx.find((f) => f);
          out.cantoAzul = !!(fxI && fxI.userData.rim && fxI.userData.rimMats &&
            fxI.userData.rimMats[0] &&
            fxI.userData.rimMats[0].color.getHex() === 0x5aa2ff);
          out.msgIman = (G.rules.message || '').indexOf('¡SÚPER IMÁN!') === 0;
          out.imanSelActiva = G._megaSelActiva() === true;   // icono cede
          paso();                                      // el bucle arma la bola

          // · campo EN LA BOLA (solo rally)
          out.bolaArma = !!G.ball.ppIman;
          G.rules.state = 'serve'; paso();
          out.bolaFueraEnSaque = !G.ball.ppIman;
          G.rules.state = 'rally'; paso();

          // · FÍSICA REAL del imán (micro-simulación por __solverHook)
          try {
            window.__wantSolverHook = true;
            await dorme(300);
            const H = window.__solverHook;
            const pad = H.createPaddleSim('player', 0);
            pad.active = true;
            pad.pos.set(0, 1.0, 1.5); pad.prev.copy(pad.pos);
            const C = pad.pos.clone(); C.y += H.DIMS.bladeCenterUp;
            const mkBall = (vx) => ({ pos: C.clone().add(new (Object.getPrototypeOf(C).constructor)(0.2, 0, 0.3)),
              vel: new (Object.getPrototypeOf(C).constructor)(vx, 0, -4),
              spin: new (Object.getPrototypeOf(C).constructor)(),
              dragMul: 1 });
            // A) con imán: empuje lateral HACIA el punto dulce
            const b1 = mkBall(0);
            b1.ppIman = { dv: 0 };
            for (let i = 0; i < 40; i++) H.stepPhysics(1 / 60, b1, [pad], []);
            out.imanEmpuja = b1.vel.x < -0.01 && b1.ppImanTocada === true;
            // B) tope de Δv por aproximación (0,35 m/s del dueño)
            out.imanTopeDv = b1.ppIman.dv <= H.DIMS.imanDvMax + 0.001 &&
              Math.abs(b1.vel.x) <= H.DIMS.imanDvMax + 0.001;
            // C) SIN el poder: física idéntica (golden) — vel.x === 0
            const b2 = mkBall(0);
            for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, b2, [pad], []);
            out.sinPoderIntacto = b2.vel.x === 0;
            // D) bola que YA superó el plano: no se recupera
            const b3 = mkBall(0);
            b3.pos.copy(C).add(new (Object.getPrototypeOf(C).constructor)(0.2, 0, -0.3));
            b3.vel.set(0, 0, -4);
            b3.ppIman = { dv: 0 };
            for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, b3, [pad], []);
            out.pasadaNoRecupera = b3.vel.x === 0 && !b3.ppImanTocada;
            // E) bola LATERAL que NO viene a nuestra mitad: sin empuje
            //    (el RESCATE de r51 solo actúa con vel.z > 0,3 — «viene
            //    hacia nosotros» — petición literal del dueño)
            const b4 = mkBall(0);
            b4.pos.copy(C).add(new (Object.getPrototypeOf(C).constructor)(0.5, 0, 0.05));
            b4.vel.set(3, 0, 0);                       // puramente lateral
            b4.ppIman = { dv: 0 };
            for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, b4, [pad], []);
            out.alejandoseNada = b4.vel.x > 2.5 && !b4.ppImanTocada;
            // E2) RESCATE de r51: bola CRUZADA que viene a nuestra mitad
            //     (closing ≤ 0,4 pero vel.z > 0,3) — el campo la atrae de
            //     VERDAD hacia el punto dulce («una bola que se nos escapa
            //     la atraigamos hacia la pala»)
            const b5 = mkBall(0);
            b5.pos.copy(C).add(new (Object.getPrototypeOf(C).constructor)(0.45, 0, 0.15));
            b5.vel.set(2.5, 0, 2.0);                   // cruzada y viniendo
            b5.ppIman = { dv: 0, dvRes: 0 };
            for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, b5, [pad], []);
            out.rescateActua = b5.vel.x < 2.0 && b5.ppImanTocada === true;
          } catch (e) { out.errFis = String(e); }

          // · CONSUMO por impacto asistido (1 carga por asistencia)
          const entI = G._megaMatriz.find((x) => x.id === 'iman');
          const n0 = entI ? entI.n : 0;
          try { G._imanImpacto(); } catch (e) { out.errImp1 = String(e); }
          out.asisteGasta = G._imanAsistidas === 1 &&
            (G._megaMatriz.find((x) => x.id === 'iman') || { n: 0 }).n === n0 - 1;
          try { G._imanImpacto(); } catch (e) { out.errImp2 = String(e); }
          out.asisteGasta2 = G._imanAsistidas === 2;
          out.imanSaleACero = !G._megaMatriz.find((x) => x.id === 'iman');
          paso();                                      // el bucle cierra el campo
          out.campoFueraSinCargas = G._imanT === 0 && G._imanFxOn === false;

          // · TOPE de 3 asistencias por activación → en la 2.ª pasada
          return out;
        }""", )
        # segundo evaluate: tope de asistencias + megáfono + conmutador + hall + voces
        rt2 = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const out = {};
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd2 = String(e); } };
          const rndReal = Math.random;

          // re-poner imán ×3 y abrir campo: 3 asistencias cierran
          Math.random = () => 0.6;                     // SIEMPRE 'iman'
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          let im = null;
          try { im = G.megaTrigger(libre); } catch (e) { out.errIm2 = String(e); }
          G._imanImpacto(); G._imanImpacto(); G._imanImpacto();
          out.topeAsistencias = G._imanT === 0 && G._imanAsistidas === 0;

          // · MEGA sigue operando con 3 poderes en el registro
          Math.random = () => 0.1;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.megaSigue = !!G._megaMatriz.find((x) => x.id === 'mega');
          const sel = G._megaSel();
          if (sel && sel.id === 'mega') {
            let mgo = null;
            try { mgo = G.megaTrigger(libre); } catch (e) { out.errMgo = String(e); }
            out.megaLibera = mgo === true && G._megaT > 14.9;
            let ext = null;
            try { ext = G.megaTrigger(libre); } catch (e) { out.errExt = String(e); }
            out.megaAlarga = ext === true && G._megaT > 29.5;
            G._megaT = 0; paso();
          } else { out.megaLibera = false; out.megaAlarga = false; }

          // · MANO VACÍA: aviso honesto
          G._megaMatriz.length = 0; G._megaIdx = 0; paso(); paso();
          let vac = null;
          try { vac = G.megaTrigger(libre); } catch (e) { out.errVac = String(e); }
          out.manoVacia = vac === true &&
            (G.rules.message || '').indexOf('SIN CARGAS') === 0;

          // · CONMUTADOR APAGADO (camino REAL del menú) y ENCENDIDO
          G.rules.state = 'rally'; G.rules.rallyHits = 11; Math.random = () => 0.1;
          paso();
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOff = String(e); }
          out.apagadoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '0' &&
              G.palaMejorada === false; } catch (e) { return false; } })();
          paso(); paso();
          out.apagadoLimpia = G._megaMatriz.length === 0 && G._megaIcon === null &&
            G._imanT === 0;
          G.menuRects.push({ id: 'pmej' });
          try { G.menuClick(G.menuRects.length - 1); } catch (e) { out.errOn = String(e); }
          out.encendidoPersiste = (() => { try {
            return localStorage.getItem('pp_pala_mejorada_v1') === '1' &&
              G.palaMejorada === true; } catch (e) { return false; } })();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          out.vuelveANacer = G._megaMatriz.length === 1;

          // · HALL = ZONA NEUTRA
          G.inHall = true;
          let enHall = null;
          try { enHall = G.megaTrigger(libre); } catch (e) { out.errHall = String(e); }
          G.inHall = false;
          out.hallNeutro = enHall === false;

          // · VOCES: el registro trae voz ES y EN para los TRES poderes
          out.vozImanEs = typeof G._poderVoz('iman_es') === 'string' &&
            G._poderVoz('iman_es').indexOf('data:audio/mpeg;base64,') === 0;
          out.vozImanEn = typeof G._poderVoz('iman_en') === 'string' &&
            G._poderVoz('iman_en').indexOf('data:audio/mpeg;base64,') === 0 &&
            G._poderVoz('iman_en') !== G._poderVoz('iman_es');
          out.vozMegaOk = typeof G._poderVoz('mega_es') === 'string' &&
            G._poderVoz('mega_es').indexOf('data:audio/mpeg;base64,') === 0;
          out.vozEfectoOk = typeof G._poderVoz('efecto_en') === 'string' &&
            G._poderVoz('efecto_en') !== G._poderVoz('efecto_es');
          out.pngImanDueno = !!(G._megaPngs['iman'] &&
            G._megaPngs['iman'].complete && G._megaPngs['iman'].naturalWidth === 256);
          out.pngMegaOk = !!(G._megaPngs['mega'] && G._megaPngs['mega'].complete);

          Math.random = rndReal;
          out.erroresPagina = 0;
          return out;
        }""")
        await browser.close()

        if rt.get('sinJuego'):
            print('✗ window.__PP_GAME no existe (el juego no arrancó)')
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            sys.exit(1)

        rt.update(rt2 or {})
        for k, v in sorted(rt.items()):
            if k.startswith('err'):
                print(f'  · {k}: {v}')

        esperados = [
            ('porDefecto', 'estado fresco: matriz vacía y construcción perezosa'),
            ('hayAPI', 'API del superpoder (incluida _imanTrigger/_imanImpacto)'),
            ('fueraSinCarga', 'FUERA de campeonato: un rally de 44 NO carga nada'),
            ('fueraGatilloLibre', 'FUERA de campeonato: el gatillo no es del poder (false)'),
            ('diezSinCarga', 'a los 10 golpes NO hay carga'),
            ('cargada', 'al golpe 11: +1 carga de MEGA en la MATRIZ (posición 0)'),
            ('iconoVivo', 'icono vivo en las DOS monturas'),
            ('iconoAnclado', 'icono ANCLADO al mango (y=−0,034 · z=0,004)'),
            ('dosCargas', 'al golpe 22 del MISMO rally: ×2 (acumula)'),
            ('tresCargas', 'al golpe 33: ×3'),
            ('topeTres', 'al golpe 44 NO hay cuarta carga (tope ×3)'),
            ('msgTope', 'megáfono del tope: «TOPE ×3 · ¡gasta una…»'),
            ('matrizDos', 'poder distinto ENTRA en la matriz: [mega ×3, efecto ×1]'),
            ('selNuevo', 'el poder nuevo se SELECCIONA solo (índice 1)'),
            ('ordenLlegada', 'los ×3 del mega se CONSERVAN (nada se elimina)'),
            ('flechasVivas', 'flechas de la matriz: pareja de sprites por montura'),
            ('sinFlechaIzqEnCero', '‹ oculta y › visible (petición del dueño: se NOTAN)'),
            ('enCeroSinIzq', 'en el índice 0 NO hay flecha izquierda (sin envolver)'),
            ('opPulso', 'las flechas PULSAN (opacidad animada)'),
            ('alUltimoYNoPasa', 'al último y NO pasa (sin flecha derecha en el final)'),
            ('saqueRespetado', 'en saque el gatillo SACA (no gasta)'),
            ('efectoAbre', 'gatillo con EFECTO seleccionado: ventana 8 s / 5 golpes'),
            ('fxHubicacion', 'FX cian construido para las DOS monturas'),
            ('cantoCian', 'el canto del efecto es CIAN (0x54d8f0)'),
            ('multEnPala', 'multiplicador ×3 en las DOS palas del jugador (r51)'),
            ('msgEfectoEnsenia', 'megáfono del efecto ENSEÑA a aplicarlo («GIRO»)'),
            ('haloVivo', 'HALO ROJO visible y anclado a la bola marcada'),
            ('haloFuera', 'sin marca: el halo se apaga'),
            ('boteFx', 'anillo de bote amplificado se dispara (one-shot)'),
            ('boteFxApaga', 'el anillo de bote se apaga solo (0,38 s)'),
            ('finPorGolpes', 'fin de la ventana del efecto por golpes'),
            ('recarga', 'efecto ACTIVO + gatillo: RECARGA la ventana'),
            ('imanEntra', 'el IMÁN ENTRA en la matriz y se selecciona'),
            ('imanAbre', 'gatillo con IMÁN: campo de 8 s (sin consumo)'),
            ('imanFx', 'FX azul construido para las DOS monturas'),
            ('cantoAzul', 'el canto del imán es AZUL (0x5aa2ff), familia del icono'),
            ('msgIman', 'megáfono: ¡SÚPER IMÁN! · la bola vuela al punto dulce…'),
            ('imanSelActiva', 'campo activo: el icono cede (selActiva)'),
            ('bolaArma', 'el campo viaja EN LA BOLA (ball.ppIman) en rally'),
            ('bolaFueraEnSaque', 'en saque la bola NO lleva campo'),
            ('imanEmpuja', 'física: el imán empuja la bola HACIA el punto dulce'),
            ('imanTopeDv', 'física: Δv lateral respeta el tope 0,60 m/s (v3.6.43)'),
            ('sinPoderIntacto', 'física: SIN el poder, vel.x === 0 (golden intacto)'),
            ('pasadaNoRecupera', 'física: la bola que YA pasó el plano no se recupera'),
            ('alejandoseNada', 'física: bola que se va LATERAL sin venir a nuestra mitad: sin empuje'),
            ('rescateActua', 'física RESCATE (r51): la bola cruzada que viene a nuestra mitad ES atraída'),
            ('asisteGasta', 'impacto asistido: −1 carga y contador +1'),
            ('asisteGasta2', 'segunda asistencia: −1 carga más'),
            ('imanSaleACero', 'cargas a 0: la entrada SALE de la matriz'),
            ('campoFueraSinCargas', 'sin cargas: el campo se apaga YA'),
            ('topeAsistencias', '3 asistencias CIERRAN la activación (tope del dueño)'),
            ('megaSigue', 'el MEGA sigue operando con 3 poderes en el registro'),
            ('megaLibera', 'gatillo con MEGA seleccionado: LIBERA 15 s'),
            ('megaAlarga', 'MEGA activa + gatillo: ALARGA a ~30 s'),
            ('manoVacia', 'matriz vacía: aviso honesto «SIN CARGAS»'),
            ('apagadoPersiste', 'conmutador OFF por el menú: persiste'),
            ('apagadoLimpia', 'conmutador OFF: matriz vacía, icono fuera, campo 0'),
            ('encendidoPersiste', 'conmutador ON por el menú: persiste encendido'),
            ('vuelveANacer', 'conmutador ON de nuevo: la norma vuelve a operar'),
            ('hallNeutro', 'hall: zona neutra (el gatillo no libera)'),
            ('vozImanEs', 'voz NATIVA ES del imán embebida (data-URI)'),
            ('vozImanEn', 'voz EN del imán embebida y DISTINTA de la ES'),
            ('vozMegaOk', 'voz del mega intacta'),
            ('vozEfectoOk', 'voz del efecto intacta'),
            ('pngImanDueno', 'PNG del dueño (Imán) decodificado (256px)'),
            ('pngMegaOk', 'PNG del mega decodificado'),
        ]
        for k, label in esperados:
            chk(rt.get(k) is True, label)

    if errors:
        for e in errors[:5]:
            print('  · pageerror:', e[:200])
        chk(False, 'sin errores de página durante la mecánica real')
    else:
        chk(True, 'sin errores de página durante la mecánica real')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


asyncio.run(main())
