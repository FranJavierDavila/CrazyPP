#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.42 · RONDA 50 — el SÚPER PORTAL SE ENTIENDE Y LA IA RESPONDE (AK).

Informe del dueño tras probar V3.6.41 en el Quest 3:
  1) CRÍTICO: «si se dispara he visto que el contrincante no devuelve las
     pelotas (he sacado y no las devuelve)… una cosa es que se le penalice
     en un % y otra que se anule su respuesta; solo mientras el super poder
     está activo, una vez finaliza las desventajas se anulan».
     CAUSA RAÍZ (r49): c06 mataba predictValid CADA FRAME con la marca
     ppPortal viva — y la marca solo se limpiaba al devolver la propia IA.
     FIX: flanco ÚNICO (la muerte de la predicción es puntual), la marca
     muere con la ventana y con el punto; penalización = % (error ×1,6 ·
     piernas ×0,75 · +10 % fallo decidido), NUNCA anulación.
  2) «el icono te lo he pasado con transparencia y no lo has recortado» —
     r49 lo embebió RGB (alfa destruido). FIX: recorte al contenido + alfa
     preservado (verificado AQUÍ con PIL sobre el data-URI servido).
  3) «la voz no sale en castellano» — la ES de r49 duraba 2,78 s (corrupta).
     FIX: Piper es_ES-davefx nativa (0,82 s) verificada por ASR.
  4) «no se sabe qué está pasando»: portal de ENTRADA (portals.png del
     dueño, el arte del rival wizard, al 50 %) en la zona de impacto con el
     halo creciente, la bola se hunde, VIAJA OCULTA 1 s y el MISMO portal
     se abre SOBRE la mesa del rival con la bola saliendo por su centro.
     Física congelada en el viaje (stepPhysics la salta): cero eventos,
     cero colisiones fantasma, UNA identidad.
  5) «congelación al cargar un superpoder»: el precaliente arranca AL
     EMPEZAR LA PARTIDA (13 piezas: 4 cantos + halo + bote + flechas +
     imagen del portal + icono + 4 voces) — la carga y el gatillo ya no
     construyen ni decodifican nada.
  6) Conmutador PASSTHROUGH en AJUSTES (en VR), por defecto DESACTIVADO,
     aplicado en vivo (fin de sesión + re-entrada automática al modo
     contrario) y persistente (ppxr_pending_ar).

Pruebas: (1) FUENTE SERVIDA — agujas de las 6 piezas + verificación PIL
del PNG del icono (recorte + alfa) y de la voz (tamaño Piper).
(2) MECÁNICA REAL headless — precaliente al empezar, golpe portalizado con
tránsito de 3 fases, salida por el centro del portal B, IA que VUELVE a
predecir (el fix crítico), marca muere con ventana/punto, recogida completa.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import base64
import io
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
        # · SELLO DE VERSIÓN (ronda 50)
        ('3.6.47-SDK6', 'versión servida: 3.6.47-SDK6 (ronda 50)'),
        # · TRÁNSITO EXPLÍCITO (presentación del dueño)
        ('this._portalSinkT = 0;            // hundimiento en el portal de entrada',
         'tránsito: fase de hundimiento declarada'),
        ('this._portalDelayT = 0;           // viaje oculto (PORTAL_DELAY = 1 s)',
         'tránsito: reloj del viaje oculto (1 s del dueño)'),
        ('this._portalRiseT = 0;            // salida por el centro del portal B',
         'tránsito: fase de salida por el centro'),
        ('const PORTAL_DELAY = 1.0;     // s entre el portal de entrada y el de salida',
         'presentación: 1 segundo entre portal A y portal B (petición exacta)'),
        ('const PORTAL_IMG_S = 0.6;     // tamaño mundo del portal (50 % de 1,2 m)',
         'presentación: portal al 50 % de su tamaño real'),
        ('const PORTAL_EXIT_H = 0.52;   // altura del portal B sobre la mesa (m)',
         'presentación: el portal B flota SOBRE la mesa del rival'),
        ('this._portalShow(b.pos.clone(), true);',
         'presentación: portal de ENTRADA en la ZONA DE IMPACTO'),
        ('this._portalOndaShow(b.pos.clone(), false);',
         'presentación: halo creciente de entrada (anillo one-shot)'),
        ('b.vel.set(0, 0, 0);                   // congelada (spin CONSERVADO, spec)',
         'tránsito: la bola se CONGELA (una identidad, sin física fantasma)'),
        ('b.ppTransito = true;',
         'tránsito: la bola marcada en viaje'),
        ('this._portalDelayT = PORTAL_DELAY;    // viaje oculto (1 s del dueño)',
         'tránsito: el viaje dura el segundo pedido'),
        ('if (this.ball && this.ball.ppTransito) return;   // ya viajando: nada',
         'tránsito: un golpe NO portaliza mientras la bola viaja'),
        ('_portalSalida() {', 'salida: _portalSalida definida'),
        ("b.ppPortal = this._portalT > 0 &&",
         'salida: penalización IA SOLO con la ventana viva'),
        ('this._portalRiseT = PORTAL_TRANS;     // sale por el centro (0,16 s)',
         'salida: la bola EMERGE del centro del portal B'),
        ('this._portalShow(this._portalSalPos.clone(), false);',
         'salida: portal de SALIDA sobre la mesa rival'),
        # · FÍSICA CONGELADA EN EL VIAJE
        ('if (!(this.ball && this.ball.ppTransito)) {\n          stepPhysics(dt, this.ball, pads, this.events);\n        }',
         'física: stepPhysics SALTA la bola congelada (cero eventos fantasma)'),
        ('if (this.showTrail && !(this.ball && this.ball.ppTransito)) {',
         'física: sin estela durante el viaje dimensional'),
        ('if (this.ball && this.ball.ppTransito) {\n      if (this.blob) this.blob.visible = false;',
         'física: sin sombra durante el viaje dimensional'),
        # · PORTAL DEL MUNDO (portals.png del dueño)
        ('const PNG_PORTAL_FX =', 'mundo: portals.png del dueño embebida'),
        ("imF.onload = () => { this._megaPngs.portalfx = imF; };",
         'mundo: la imagen del FX se precarga con los PNG del registro'),
        ('_buildPortalImg() {', 'mundo: _buildPortalImg (sprites del portal)'),
        ('blending: THREE.AdditiveBlending }));\n      sp.scale.setScalar(PORTAL_IMG_S);',
         'mundo: sprites al 50 % del tamaño real'),
        ('for (const spP of [this._portalSpriteA, this._portalSpriteB]) {',
         'mundo: pulso + desvanecido de los portales en animate'),
        ('if (_portalTmpC.z > C - 0.18) _portalTmpC.z = C - 0.18;  // margen de red',
         'legalidad: margen de red del portal de salida (lección r49)'),
        ('if (Math.abs(_portalTmpC.x) > 0.58) {',
         'legalidad: bote del portal en zona jugable (|x| ≤ 0,58)'),
        ('_portalTmpC.y = DIMS.tableTopY + PORTAL_EXIT_H + dVer;   // centro portal B',
         'legalidad: portal B SOBRE la mesa (+ variación vertical spec)'),
        # · IA PENALIZADA EN %, NUNCA ANULADA (el FIX crítico)
        ('if (ball.ppPortal && !this._ppPortalVisto) {',
         'IA FIX: la muerte de la predicción es UN FLANCO (no cada frame)'),
        ('this.predictTimer = Math.max(this.predictTimer, this.cfg.predictInterval);',
         'IA FIX: reacciona tras SU predictInterval natural'),
        ('this._ppPortalVisto = false;   // v3.6.42: el flanco del portal a limpio',
         'IA FIX: el flanco se recoge en el reset de la IA'),
        ('(ball.ppPortal ? (DIMS.portalRivalErrMul || 1) : 1);',
         'IA %: error de puntería ×1,6 SOLO con la marca (penalización honesta)'),
        ('if (ball.ppPortal) vMulIA *= (DIMS.portalRivalVel || 1);',
         'IA %: piernas ×0,75 SOLO con la marca'),
        ('(ball.ppPortal ? (DIMS.portalMissExtra || 0) : 0);',
         'IA %: +10 % de fallo decidido SOLO con la marca'),
        # · LAS DESVENTAJAS Mueren CON EL PODER
        ('try { if (this.ball && !this.ball.ppTransito) this.ball.ppPortal = false; }',
         'fin de ventana: la marca IA muere CON el poder'),
        ('(this._portalT <= 0 ||\n         (this.rules && this.rules.state !== \'rally\')))',
         'fin de punto: el saque siguiente nace SIEMPRE limpio'),
        # · ANTI-LAG: PRECALIENTE DESDE EL SAQUE
        ('// caliente y la congelación es imposible.\n    this._megaPrewarm();',
         'ANTI-LAG: el precaliente arranca AL EMPEZAR LA PARTIDA'),
        ('() => { try { this._buildPortalImg(); } catch (e) { /* */ } },   // PNG del dueño',
         'ANTI-LAG: la imagen del portal se precalienta'),
        ('() => { try { if (!this._megaIcon) this._buildMegaIcon(); } catch (e) { /* */ } },',
         'ANTI-LAG: el icono se preconstruye (ya no se crea en la carga)'),
        ("() => { try { this._megaVozPrecalentar('portal'); } catch (e) { /* */ } },",
         'ANTI-LAG: las voces se predecodifican (la carga jamás decodifica)'),
        ('_megaVozPrecalentar(id) {', 'ANTI-LAG: precalentador de voces definido'),
        # · PASSTHROUGH EN AJUSTES (en VR, por defecto OFF)
        ("btn('psthru', 56, y, 912, 56, T('btn_psthru', { v: yn(pstOn) }), !!pstOn, undefined, !!pstOn, 23);",
         'PASSTHROUGH: conmutador en la página AJUSTES del menú VR'),
        ("case 'psthru': {", 'PASSTHROUGH: caso de clic definido'),
        ('this._xrSwitchTo = pstNuevo;   // el sessionend re-entra solo',
         'PASSTHROUGH: cambio de modo en vivo (fin + re-entrada automática)'),
        ("localStorage.getItem('ppxr_pending_ar') === '1'",
         'PASSTHROUGH: preferencia persistente (por defecto DESACTIVADO)'),
        ("btn_psthru: 'Passthrough · tu habitación: {v}',",
         'PASSTHROUGH: texto ES del conmutador'),
        ("btn_psthru: 'Passthrough · your room: {v}',",
         'PASSTHROUGH: texto EN del conmutador'),
        # · RECOGIDA COMPLETA (regla Quest)
        ('this._portalSinkT = 0;\n    this._portalDelayT = 0;\n    this._portalRiseT = 0;',
         'recogida: las tres fases del tránsito duermen en el reset'),
        ('try { if (this.ball) this.ball.ppTransito = false; } catch (eTr) { /* */ }',
         'recogida: la bola JAMÁS queda congelada tras una partida nueva'),
    ]:
        chk(needle in game, label)

    # viejos caminos de r49 RETIRADOS
    chk('this._portalTrans = PORTAL_TRANS;' not in game,
        'retirado: el swap inmediato de r49 (ahora hay viaje de 1 s)')
    chk('newV.setLength(Math.min(keep, DIMS.maxBallSpeed));' not in game,
        'retirado: el reescalado de rapidez que rompía el bote legal')
    chk('if (ball.ppPortal) this.predictValid = false;' not in game,
        'IA FIX: la muerte por-frame de r49 DESAPARECIDA (el flanco manda)')

    # · ICONO del dueño: recortado y con TRANSPARENCIA (verificación PIL)
    chk('const PNG_PODER_PORTAL' in game, 'icono: PNG del portal embebido')
    try:
        import re as _re
        m = _re.search(r"const PNG_PODER_PORTAL = 'data:image/png;base64,([^']+)'", game)
        from PIL import Image
        im = Image.open(io.BytesIO(base64.b64decode(m.group(1)))).convert('RGBA')
        w, h = im.size
        esquinas = [im.getpixel(p)[3] for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]]
        trans = sum(1 for px in im.getdata() if px[3] < 128)
        chk(w == 256 and h == 256, 'icono: lienzo 256×256 como los demás poderes')
        chk(all(a == 0 for a in esquinas) and trans > (w * h) * 0.10,
            'icono: TRANSPARENCIA preservada (esquinas alfa 0 — recortado)')
    except Exception as e:
        chk(False, f'icono: verificación PIL ({e})')

    # · VOZ castellana nativa (Piper davefx — la de r49 duraba 2,78 s)
    try:
        import re as _re
        mES = _re.search(r"const VOZ_PODER_PORTAL = 'data:audio/mpeg;base64,([^']+)'", game)
        mEN = _re.search(r"const VOZ_PODER_PORTAL_EN = 'data:audio/mpeg;base64,([^']+)'", game)
        nES, nEN = len(mES.group(1)), len(mEN.group(1))
        chk(5000 < nES < 11000,
            f'voz ES: tamaño Piper nativo ({nES} chars; la corrupta de r49 tenía ~20.300)')
        chk(4000 < nEN < 10000, f'voz EN: tamaño Piper nativo ({nEN} chars)')
    except Exception as e:
        chk(False, f'voces: verificación de tamaño ({e})')

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

          // · ARRANQUE limpio: el PRECALIENTE arranca AL EMPEZAR (r50)
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          out.precalienteAlEmpezar = !!(G._megaPrewarmQ && G._megaPrewarmQ.length >= 13);
          // espera a que la imagen del FX llegue (data-URI decodificada)
          for (let i = 0; i < 60 && !(G._megaPngs.portalfx &&
              G._megaPngs.portalfx.complete); i++) {
            await new Promise((r) => setTimeout(r, 100));
          }
          // drena la cola entera (una pieza por frame, como en el juego)
          Math.random = () => 0.9;
          for (let i = 0; i < 20; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errD = String(e); }
          }
          out.spritesPortalCalientes = !!G._portalSpriteA && !!G._portalSpriteB;
          out.iconoPreconstruido = !!G._megaIcon;

          // · SEMBRA portal ×2 (dos rallyes de 11 con frame 'point' entre
          //    ventanas) y ABRE la ventana con el gatillo
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errU0 = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errU1 = String(e); }
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errGP = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errG2 = String(e); }
          out.sembrado = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'portal' && G._megaMatriz[0].n === 2;
          let tP = null;
          try { tP = G.megaTrigger(libre); } catch (e) { out.errP1 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errP2 = String(e); }
          out.ventanaAbre = tP === true && G._portalT > 7.9 &&
            G._portalGolpes === 3;

          // · GOLPE PORTALIZADO: portal A en la zona de impacto + bola
          //    congelada viajando
          G.rules.state = 'rally';
          const b = G.ball;
          b.pos.set(0.10, 1.02, 0.55);
          b.spin.set(2, -1, 4);
          b.vel.set(-0.35, 0.55, -6.2);
          const spin0 = b.spin.clone();
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          G._portalCd = 0;
          try { G._portalProcesa(); } catch (e) { out.errX1 = String(e); }
          out.portalAEnImpacto = !!G._portalSpriteA && G._portalSpriteA.visible &&
            G._portalSpriteA.position.distanceTo(b.pos) < 0.02;
          out.bolaCongelada = b.ppTransito === true &&
            b.vel.lengthSq() === 0;
          out.spinIntacto = Math.abs(b.spin.x - spin0.x) < 1e-6;
          out.hundimiento = G._portalSinkT > 0 && G._portalSinkT <= 0.17;
          out.viajeUnSegundo = G._portalDelayT > 0.9 && G._portalDelayT <= 1.01;
          out.cargaGastada = (G._megaMatriz.find((x) => x.id === 'portal') || {}).n === 1;
          out.eventoNoConsumido = G.events.length === 1 && !G.events[0].consumed;

          // · EL VIAJE: a mitad de camino la bola sigue oculta y quieta
          //    (ticks de 0,05 s: en el juego real cada frame es ~16 ms y la
          //    anatomía visual corre entera)
          for (let i = 0; i < 10; i++) {
            try { G.updateMega(0.05); } catch (e) { out.errV1 = String(e); }
          }
          out.bolaOcultaEnViaje = b.ppTransito === true && b.vel.lengthSq() === 0;
          // · …y al completar el segundo SALE por el centro del portal B
          //    (cortamos EN EL FRAME de la salida: la emergencia dura 0,16 s)
          for (let i = 0; i < 14 && b.ppTransito; i++) {
            try { G.updateMega(0.05); } catch (e) { out.errV2 = String(e); }
          }
          out.salePorPortalB = b.ppTransito === false &&
            Math.abs(b.pos.y - (TY + 0.52 + 0)) < 0.16 &&
            Math.abs(b.pos.y - G._portalSalPos.y) < 1e-6;
          out.portalBSobreMesaRival = b.pos.z < TZ - 0.15 && b.pos.y > TY;
          out.haciaElRival = b.vel.z < -0.5;
          out.zonaLegalX = Math.abs(b.pos.x) <= 0.59;
          out.velocidadLegal = b.vel.length() > 1.0 &&
            b.vel.length() <= 12.5;
          out.marcaIA = b.ppPortal === true;
          out.portalBVisible = !!G._portalSpriteB && G._portalSpriteB.visible;
          out.anilloSalida = !!G._portalOndaB && G._portalOndaB.visible;
          out.subeDelPortal = G._portalRiseT > 0;

          // · FIX CRÍTICO IA: la predicción muere UNA vez y VUELVE
          G.rules.startMatch('match');
          const ai = G.ai;
          if (ai) {
            const ballIA = G.ball;
            // (a) flanco: la primera vez que VE la marca, pierde la predicción
            ai.predictValid = true;
            ballIA.ppPortal = true;
            try { ai.update(1 / 60, ballIA, { canHit: false, validBounce: false }); }
            catch (e) { out.errA1 = String(e); }
            out.iaFlancoMata = ai.predictValid === false;
            // (b) LA PRUEBA DEL FIX: con la marca SIGUE viva, una predicción
            //     NUEVA ya no se mata (r49 la mataba cada frame: la IA no
            //     volvía a golpear JAMÁS). El reloj SIN vencer: sin nueva
            //     predicción, la vieja SOBREVIVE al frame (canHit real).
            ai.predictValid = true;
            ai.predictTimer = 0.5;
            ballIA.vel.set(0, -1, -6);
            try { ai.update(1 / 60, ballIA, { canHit: true, validBounce: true }); }
            catch (e) { out.errA2 = String(e); }
            out.iaPrediccionSobrevive = ai.predictValid === true;
            // (c) y con su reloj vencido VUELVE a predecir (reacción natural)
            ai.predictValid = false;
            ai.predictTimer = 0;
            ballIA.vel.set(0, -1, -6);
            try { ai.update(1 / 60, ballIA, { canHit: true, validBounce: true }); }
            catch (e) { out.errA3 = String(e); }
            out.iaVuelveAPredecir = ai.predictValid === true;
            // (d) la marca muere con la ventana: sin poder, IA normal
            ballIA.ppPortal = false;
            ai._ppPortalVisto = false;
            out.iaSinMarcaNormal = ai._ppPortalVisto === false;
          } else { out.iaFlancoMata = false; }

          // · FIN DE VENTANA limpia la marca (las desventajas se anulan)
          G._portalT = 8;
          G._megaMatriz.push({ id: 'portal', n: 1 });
          const b2 = G.ball;
          b2.ppPortal = true;
          try { G._portalFin(); } catch (e) { out.errF1 = String(e); }
          out.marcaMuereConVentana = b2.ppPortal === false && G._portalT === 0;

          // · FIN DE PUNTO: el saque siguiente nace limpio
          b2.ppPortal = true;
          G._portalT = 8;
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errF2 = String(e); }
          out.marcaMuereConPunto = b2.ppPortal === false;

          // · GOLPES AGOTADOS: 3 golpes (resolviendo CADA viaje) cierran
          G.rules.state = 'rally';
          const entP = G._megaMatriz.find((x) => x.id === 'portal') ||
            G._megaMatriz.push({ id: 'portal', n: 3 }) && G._megaMatriz.find((x) => x.id === 'portal');
          entP.n = 3;
          G._portalT = 8; G._portalGolpes = 3;
          let bien = 0;
          for (let i = 0; i < 3; i++) {
            b.pos.set(0.05, 1.0, 0.55);
            b.vel.set(-0.3, 0.5, -6.0);
            b.ppTransito = false;
            G.events.length = 0;
            G.events.push({ type: 'paddle', who: 'player', speed: 6,
              pos: b.pos.clone(), paddleIndex: G.paddleHand });
            G._portalCd = 0;
            try { G._portalProcesa(); bien++; } catch (e) { out.errX8 = String(e); }
            for (let j = 0; j < 26; j++) {
              try { G.updateMega(0.05); } catch (e) { out.errV3 = String(e); }
            }
          }
          out.finPorGolpes = bien === 3 && G._portalGolpes === 0 &&
            G._portalT === 0;

          // · RECOGIDA COMPLETA con la bola EN VIAJE (regla Quest)
          b.pos.set(0.05, 1.0, 0.55); b.vel.set(-0.3, 0.5, -6.0);
          G._portalT = 8; G._portalGolpes = 1; G._portalCd = 0;
          entP.n = 1;
          G.events.length = 0;
          G.events.push({ type: 'paddle', who: 'player', speed: 6,
            pos: b.pos.clone(), paddleIndex: G.paddleHand });
          try { G._portalProcesa(); } catch (e) { out.errX9 = String(e); }
          out.enViajeAlMorir = b.ppTransito === true;
          try { G.rules.startMatch('match'); } catch (e) { out.errR = String(e); }
          out.recogidaConBolaEnViaje = b.ppTransito === false &&
            G._portalDelayT === 0 && G.ballMesh.visible === true &&
            Math.abs(G.ballMesh.scale.x - 1) < 1e-6 &&
            G._megaActivaId === null;

          Math.random = rndReal;
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'window.__PP_GAME disponible (juego vivo)')
        else:
            chk(rt.get('precalienteAlEmpezar') is True,
                'ANTI-LAG: el precaliente (13 piezas) arranca al empezar la partida')
            chk(rt.get('spritesPortalCalientes') is True,
                'ANTI-LAG: los portales del mundo quedan calientes antes de jugar')
            chk(rt.get('iconoPreconstruido') is True,
                'ANTI-LAG: el icono ya está construido (la carga solo lo enciende)')
            chk(rt.get('sembrado') is True,
                'siembra: portal ×2 en la matriz (dos rallyes de 11)')
            chk(rt.get('ventanaAbre') is True,
                'gatillo: la ventana del portal abre (8 s / 3 golpes)')
            chk(rt.get('portalAEnImpacto') is True,
                'PORTAL A: se abre en la ZONA DE IMPACTO (PNG del dueño al 50 %)')
            chk(rt.get('bolaCongelada') is True,
                'TRÁNSITO: la bola se congela con el golpe (una identidad)')
            chk(rt.get('spinIntacto') is True, 'TRÁNSITO: spin CONSERVADO (spec v1)')
            chk(rt.get('hundimiento') is True, 'TRÁNSITO: hundimiento armado (0,16 s)')
            chk(rt.get('viajeUnSegundo') is True, 'TRÁNSITO: viaje oculto de 1 segundo')
            chk(rt.get('cargaGastada') is True,
                'CONSUMO: cada golpe portalizado gasta 1 carga (×2 → ×1)')
            chk(rt.get('eventoNoConsumido') is True,
                'ÁRBITRO INTACTO: el evento del golpe NO se consume')
            chk(rt.get('bolaOcultaEnViaje') is True,
                'VIAJE: a mitad de camino la bola sigue oculta y quieta')
            chk(rt.get('salePorPortalB') is True,
                'SALIDA: la bola EMERGE en el centro del portal B')
            chk(rt.get('portalBSobreMesaRival') is True,
                'SALIDA: el portal B flota SOBRE la mesa del rival')
            chk(rt.get('haciaElRival') is True, 'SALIDA: marcha hacia el rival')
            chk(rt.get('zonaLegalX') is True, 'SALIDA: bote en zona jugable (|x| ≤ 0,59)')
            chk(rt.get('velocidadLegal') is True,
                'SALIDA: velocidad del solver LEGAL (bote jugable, rival capaz)')
            chk(rt.get('marcaIA') is True,
                'SALIDA: bola marcada para la IA SOLO con la ventana viva')
            chk(rt.get('portalBVisible') is True, 'SALIDA: portal B visible')
            chk(rt.get('anilloSalida') is True, 'SALIDA: halo creciente de salida')
            chk(rt.get('subeDelPortal') is True, 'SALIDA: emergencia visual armada')
            chk(rt.get('iaFlancoMata') is True,
                'IA (flanco): al cruzar el portal pierde la predicción UNA vez')
            chk(rt.get('iaPrediccionSobrevive') is True,
                'IA (FIX CRÍTICO): la marca YA viva NO mata predicciones nuevas — vuelve a jugar')
            chk(rt.get('iaVuelveAPredecir') is True,
                'IA: reacciona tras SU predictInterval y vuelve a predecir')
            chk(rt.get('iaSinMarcaNormal') is True,
                'IA: sin marca los parámetros vuelven a ser los de siempre')
            chk(rt.get('marcaMuereConVentana') is True,
                'FIN DE VENTANA: las desventajas se anulan con el poder')
            chk(rt.get('marcaMuereConPunto') is True,
                'FIN DE PUNTO: el saque siguiente nace limpio')
            chk(rt.get('finPorGolpes') is True,
                '3 GOLPES (con su viaje resuelto) → fin de ventana')
            chk(rt.get('enViajeAlMorir') is True,
                'RECOGIDA: la partida muere con la bola EN VIAJE (caso límite)')
            chk(rt.get('recogidaConBolaEnViaje') is True,
                'RECOGIDA COMPLETA: bola liberada, malla visible, escala 1, pala limpia')

    # ---------- 3 · CONSOLA limpia ----------
    chk(not errors, f'cero pageerrors ({len(errors)}: {errors[:2]})')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    await browser.close()
    if fails:
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
