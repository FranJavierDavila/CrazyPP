#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.43 (re-anclada v3.6.44: imán 0,95/6,5/0,80 · halo 0,21 · blips 988/1319) · RONDA 51 — SUPERPODERES QUE SE VEN Y SE OYEN (AL).

Informe del dueño tras probar V3.6.42 en el Quest 3:
  1) «No noto los efectos del Poder Super Efectos, igual es preciso
     exagerarlo para que visualmente veamos el resultado» — FIX: el brush
     generado sube ×3 (EFECTO_SPIN_MUL), Magnus ×2,2 y bote ×2,4 (c02) y
     tope de giro ×3 (efectoSpinTope); el halo rojo de la bola marcada
     crece un 35 % (0,142 m) con pulso más vivo.
  2) «El Súper Imán tampoco se entiende visualmente: ampliar el radio de
     influencia y si la bola entra dentro del mismo que aparezcan unas
     pequeñas flechas desde la bola en dirección al centro de nuestra pala
     indicando que está siendo atraída y que sea así, eso permite que una
     bola que se nos escapa la atraigamos hacia la pala» — FIX: radio
     0,45→0,75 m y plena 0,12→0,20, acel ×5 y Δv ×0,60; RESCATE NUEVO en
     c05/applyIman (bolas que NO se acercan pero vienen a nuestra mitad son
     atraídas DIRECTO al punto dulce: imanRescateAcel 6, imanRescateDv
     0,85); 3 FLECHAS cian en línea bola→punto dulce (construidas por el
     precaliente, ancladas por _imanFlechasUpdate, laten si el campo
     empuja).
  3) «En el Super Poder Portal a veces puedo golpear varios portales y
     otras parece que con uno solo me desaparece» — CAUSA: el gasto iba
     POR GOLPE (el sorteo ×1 mataba la ventana al primer portal y encima
     el vigilante «sin cargas» la apagaba). FIX: la ACTIVACIÓN gasta 1
     carga y la ventana trae SIEMPRE SUS 3 GOLPES PORTALIZADOS (u 8 s);
     el vigilante de la matriz se RETIRA; re-activar refresca.
  4) «En todos los super efectos de pala debemos dar feedback sonoro
     cuando está a punto de acabarse para que el jugador lo sepa sin
     mirar el indicador del icono» — FIX: CUENTA SONORA 3·2·1 uniforme en
     los CUATRO poderes (_poderTickBlip: blips de 1319 Hz; el último, de
     1568 Hz) + el sonido de fin propio de cada poder.
  5) «El conmutador de passthrough que no nos lleve a la ventana principal
     web desde VR, que sea algo directo desde VR a MR sin pasar por la
     página web» — FIX: la sesión se pide SIEMPRE immersive-ar (el Quest 3
     la soporta) y el passthrough ya NO cambia el MODO: cambia el FONDO al
     vuelo (_pstAplicar canjea background/fog/sala/shadowCatcher y pone
     clearColor alfa 0) — sin session.end, sin salir a la web. La sala
     virtual opaca se ve idéntica a una sesión VR; los usos del hall y el
     menú ahora filtran con (inAR && pstOn); fallback r49 solo para
     dispositivos SIN immersive-ar.

Pruebas: (1) FUENTE SERVida — agujas de las 5 piezas (incluye agujas
NEGATIVAS: el gasto por golpe y el vigilante del portal ya no existen).
(2) MECÁNICA REAL headless — precaliente de 14 piezas, flechas del imán
vivas según el estado del campo, PORTAL ×1 con 3 golpes garantizados (el
caso exacto del dueño), cuenta sonora 3·2·1 espiada en el audio,
passthrough en caliente que canjea y restaura la escena, halo del efecto
exagerado.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import re
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
        # · SELLO DE VERSIÓN (ronda 51)
        ('3.6.62-SDK6', 'versión servida: 3.6.62-SDK6 (ronda 52)'),
        # · 1) SÚPER EFECTO EXAGERADO
        ('const EFECTO_SPIN_MUL = 3;  // multiplicador del brush generado (antes ×2)',
         'efecto: el brush generado sube a ×3 (antes ×2)'),
        ('efectoSpinTope: 3,', 'efecto: tope de giro ×3 (c02)'),
        ('efectoMagnusMul: 2.2,', 'efecto: curva Magnus ×2,2 en vuelo (c02)'),
        # v3.6.49 (r57): el acople ×2,4 RETIRADO — «la ventaja del bote
        # sólo es para el jugador»: bote físico puro sin tipo (c05)
        ('0.21 + 0.05 * Math.sin(performance.now() * 0.009)',
         'efecto: halo de la bola marcada un 35 % más grande y vivo'),
        # · 2) SÚPER IMÁN: radio + flechas + RESCATE
        ('imanRadio: 0.95,', 'imán: radio de influencia 0,95 m (v3.6.44)'),
        ('imanPlena: 0.26,', 'imán: zona plena 0,26 m (v3.6.44)'),
        ('imanAcelMax: 6.5,', 'imán: aceleración ×6,5 m/s² (v3.6.44)'),
        ('imanDvMax: 0.80,', 'imán: tope de Δv 0,80 m/s por aproximación (v3.6.44)'),
        ('imanRescateAcel: 7.5,', 'imán: RESCATE con aceleración 7,5 m/s² (v3.6.44)'),
        ('imanRescateDv: 1.05,', 'imán: RESCATE con tope Δv 1,05 m/s (v3.6.44)'),
        # · v3.6.49 (r57): GUÍA DE TIRO (gancho y freno RETIRADOS)
        ('ps.ppImanAim = imanAim;',
         'r57: la guía viaja EN LA PALA (ppImanAim) — gancho retirado'),
        ('imanAimVzMin: -0.4,', 'r57: guía sólo con tiros hacia la mitad rival'),
        ('imanAimProfundidad: 0.62,', 'r57: objetivo 62 % de la media mesa rival'),
        ('imanAimPisoVel: 9.5,', 'r57: piso de potencia — golpes muy fuertes'),
        ('computeShotVelocityReal(ball.pos, _imObjetivo, T0, vMax0, _imSpinCero)',
         'r57: el solver de la casa reconstruye el tiro (bote asegurado)'),
        # · r54 · NEGATIVAS: flechas y campo RETIRADOS (pala limpia + metálica)
        ('_imanPalaOsc(on) {', 'imán (r54): PALA METÁLICA −80 % (sin flechas ni campo)'),
        # · 3) PORTAL: 3 GOLPES GARANTIZADOS
        ('const entAbrir = this._megaMatriz.find((x) => x.id === \'portal\');\n    if (entAbrir) this._megaGasta(entAbrir);   // −1 carga AL ABRIR (no por golpe)',
         'portal: la ACTIVACIÓN gasta 1 carga AL ABRIR'),
        ('this._portalGolpes--;\n    this._portalCd = PORTAL_CD;',
         'portal: el golpe consume golpes de VENTANA (no cargas)'),
        ('if (this._portalGolpes <= 0) {\n      this._portalFin();                  // los 3 portales agotados',
         'portal: la ventana muere SOLO al agotar los 3 golpes'),
        ('// v3.6.43: el vigilante «sin cargas → portal fuera» se RETIRA — la',
         'portal: el vigilante de la matriz se RETIRA (comentario)'),
        ('this.pstOn = this.inAR && this.pendingAR;',
         'passthrough: pstOn nace de la preferencia al entrar en sesión'),
        # · 4) CUENTA SONORA 3·2·1 (los cuatro poderes)
        ('_poderTickBlip(n) {', 'ticks: _poderTickBlip definida (cuenta uniforme)'),
        ('const f = n >= 3 ? 1319 : 988;',
         'ticks: el último segundo sube de tono (urgencia)'),
        ('/** v3.6.43 · CUENTA SONORA de fin de poder',
         'ticks: documentada (petición del dueño)'),
        # · 5) PASSTHROUGH EN CALIENTE
        ("arOK ? 'immersive-ar' : 'immersive-vr',",
         'passthrough: la sesión se pide SIEMPRE immersive-ar si se soporta'),
        ("try { arOK = !!(await xr.isSessionSupported('immersive-ar')); } catch (eXR) { /* */ }",
         'passthrough: detección de soporte immersive-ar'),
        ('_pstAplicar(on) {', 'passthrough: _pstAplicar (canje de fondo/sala)'),
        ('try { this.renderer.setClearColor(0x000000, 0); } catch (eC) { /* */ }',
         'passthrough: clearColor alfa 0 → se ve la habitación real'),
        ('if (this.renderer.xr.isPresenting && this.inAR) {\n          this.pstOn = pstNuevo;\n          this._pstAplicar(pstNuevo);   // ⬅ AL VUELO: ni un frame de web',
         'passthrough: el conmutador en AR alterna EN CALIENTE'),
        ('this._pstAplicar(false);\n    this.pstOn = false;\n    this.inAR = false;',
         'passthrough: fin de sesión restaura sala virtual'),
        ('this.pstOn = false;           // passthrough visible AHORA (solo inAR)',
         'passthrough: estado pstOn en el constructor'),
        ('Passthrough ACTIVADO · tu habitación (sin salir de la partida)',
         'passthrough: i18n ES en caliente'),
        ('Passthrough ON · your room (no leaving the match)',
         'passthrough: i18n EN en caliente'),
    ]:
        chk(needle in game, label)

    # · AGUJAS NEGATIVAS (el defecto NO puede volver)
    chk('if (ent) this._megaGasta(ent);\n    this._portalGolpes--;' not in game,
        'portal NEGATIVO: ya no hay gasto POR GOLPE de la matriz')
    chk('sin cargas: portal fuera YA' not in game,
        'portal NEGATIVO: el vigilante «sin cargas → fuera» desapareció')
    chk(game.count('(this.inAR && this.pstOn)') >= 5,
        f'passthrough: los usos de sala/hall filtran con (inAR && pstOn) '
        f'({game.count("(this.inAR && this.pstOn)")} usos)')
    chk(game.count('this._poderTickBlip(2)') == 5 and
        game.count('this._poderTickBlip(1)') == 5 and
        game.count('this._poderTickBlip(3)') == 5,
        'ticks: los CINCO poderes comparten la cuenta 3·2·1 (15 llamadas)')

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

          // · PRECALIENTE de 13 piezas (r54: fuera flechas/campo/estela)
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          out.precaliente13 = !!(G._megaPrewarmQ && G._megaPrewarmQ.length === 16);
          Math.random = () => 0.5;                 // siembra IMÁN (tercer tercio)
          for (let i = 0; i < 20; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errD = String(e); }
          }
          // v3.6.46 · PALA METÁLICA: el oscurecido sigue el estado de la
          // ventana (sin flechas que vigilar — la señal es la pala)
          out.palaMetalicaMontada = typeof G._imanPalaOsc === 'function';

          // · VENTANA del imán viva (el gancho la arma en rally)
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errU0 = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG1 = String(e); }
          out.sembradoIman = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'iman';
          let tI = null;
          try { tI = G.megaTrigger(libre); } catch (e) { out.errI1 = String(e); }
          out.campoAbre = tI === true && G._imanT > 7.9;
          const ps = G.controllerPaddles[G.paddleHand];
          ps.active = true;
          ps.pos.set(0, 1.0, 0.9);
          ps.up.set(0, 1, 0); ps.normal.set(0, 0, -1);
          const bI = G.ball;
          // A) con la ventana viva, el oscurecido SE APLICA a la montura
          bI.pos.set(0.45, 1.0, 0.55);
          bI.vel.set(1.5, 0, 2.0);
          try { G.updateMega(1 / 60); } catch (e) { out.errF1 = String(e); }
          out.oscurecidoConVentana = G._imanOscApplied === true;
          // B) fin de la ventana → el oscurecido SE RETIRA
          G._imanT = 0;
          try { G.updateMega(1 / 60); } catch (e) { out.errF2 = String(e); }
          out.oscurecidoSinVentana = G._imanOscApplied === false;

          // · v3.6.49 (r57): SIN campo por bola — la guía vive EN LA PALA
          G._imanT = 8;                            // ventana viva (IMAN_DUR)
          bI.pos.set(0.45, 1.0, 0.55);
          bI.vel.set(1.5, 0, 2.0);
          bI.ppEfecto = false; bI.ppPortal = false; bI.ppTransito = false;
          try { G.updateMega(1 / 60); } catch (e) { out.errR1 = String(e); }
          out.rescateMarcaArmada = !bI.ppIman;     // NUNCA campo por bola (r57)
          // y la PALA del jugador queda armada con la guía
          const psR = G.controllerPaddles[G.paddleHand];
          out.empujeMarcado = psR.ppImanAim === true;   // guía armada (r57)
          G._imanT = 0;
          try { G.updateMega(1 / 60); } catch (e) { out.errF4 = String(e); }

          // · PORTAL ×1: el caso EXACTO del dueño («con uno solo me
          //   desaparece») — ahora abre SIEMPRE 3 golpes aunque la matriz
          //   se quede sin el poder
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errP0 = String(e); }
          Math.random = () => 0.65;               // siembra PORTAL (4.º de 5)
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG2 = String(e); }
          out.sembradoPortal1 = !!(G._megaMatriz.find((x) => x.id === 'portal')) &&
            G._megaMatriz.find((x) => x.id === 'portal').n === 1;
          let tP = null;
          try { tP = G.megaTrigger(libre); } catch (e) { out.errP1 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errP2 = String(e); }
          out.ventanaCon3Golpes = tP === true && G._portalT > 7.9 &&
            G._portalGolpes === 3;
          out.matrizVaciaTrasAbrir = !G._megaMatriz.find((x) => x.id === 'portal');
          out.ventanaVivaSinMatriz = G._portalT > 7.9;   // el defecto r50 moría AQUÍ
          // 3 golpes portalizados (cada uno con su viaje resuelto)
          const b = G.ball;
          let golpes = 0;
          for (let k = 0; k < 3; k++) {
            G.rules.state = 'rally';
            b.pos.set(0.10, 1.02, 0.55);
            b.spin.set(2, -1, 4);
            b.vel.set(-0.35, 0.55, -6.2);
            G.events.length = 0;
            G.events.push({ type: 'paddle', who: 'player', speed: 6,
              pos: b.pos.clone(), paddleIndex: G.paddleHand });
            G._portalCd = 0;
            try { G._portalProcesa(); } catch (e) { out.errX1 = String(e); }
            if (b.ppTransito) golpes++;
            for (let i = 0; i < 30 && b.ppTransito; i++) {
              try { G.updateMega(0.05); } catch (e) { out.errV = String(e); }
            }
          }
          out.tresPortales = golpes === 3;
          out.finTrasTres = G._portalT <= 0 && G._portalGolpes <= 0;

          // · CUENTA SONORA 3·2·1 (espiamos playOsc) — apagamos los OTROS
          //   poderes para que la cuenta sea EXACTAMENTE la del efecto
          Math.random = rndReal;
          G._imanT = 0; G._megaT = 0; G._portalT = 0; G._portalGolpes = 0;
          if (G.ball) { try { delete G.ball.ppIman; } catch (e) { /* */ } }
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errT0 = String(e); }
          Math.random = () => 0.30;               // siembra EFECTO (1.º tercio)
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG3 = String(e); }
          let blips = 0;
          const playOsc0 = G.audio.playOsc.bind(G.audio);
          G.audio.playOsc = (f1, f2, dur, tipo, vol, delay) => {
            if (f1 === 988 || f1 === 1319) blips++;
            return playOsc0(f1, f2, dur, tipo, vol, delay);
          };
          try { G.megaTrigger(libre); } catch (e) { out.errE1 = String(e); }
          G._efectoT = 3.4;
          for (let i = 0; i < 40; i++) {
            try { G.updateMega(0.1); } catch (e) { out.errE2 = String(e); }
          }
          G.audio.playOsc = playOsc0;
          out.cuenta321 = blips === 3;   // cruzó 3, 2 y 1 s exactamente

          // · HALO del efecto exagerado (bola marcada)
          // v3.6.49: la LEY de los 10 s limpia marcas sin ventana — el
          // test abre la ventana ANTES de marcar (r57: la marca sólo
          // existe con el poder vivo)
          G._buildEfectoHalo();
          G._efectoT = 5;                    // ventana viva (sintética)
          G.ball.ppEfecto = true;
          try { G.updateMega(1 / 60); } catch (e) { out.errH1 = String(e); }
          out.haloGrande = !!G._efectoHalo && G._efectoHalo.visible &&
            G._efectoHalo.scale.x > 0.115;   // exagerado: 0,118–0,166 (viejo 0,091–0,119)
          G._efectoT = 0;

          // · PASSTHROUGH EN CALIENTE (canje y restore de la escena)
          const bg0 = G.scene.background, fog0 = G.scene.fog;
          const sala0 = G.roomGroup ? G.roomGroup.visible : true;
          try { G._pstAplicar(true); } catch (e) { out.errPST1 = String(e); }
          out.pstCanjea = G._pstAplicada === true &&
            G.scene.background === null && G.scene.fog === null &&
            (!G.roomGroup || G.roomGroup.visible === false);
          try { G._pstAplicar(false); } catch (e) { out.errPST2 = String(e); }
          out.pstRestaura = G._pstAplicada === false &&
            G.scene.background === bg0 && G.scene.fog === fog0 &&
            (G.roomGroup ? G.roomGroup.visible === sala0 : true);
          out.pstInocuoDoble = (G._pstAplicar(false), G._pstAplicada === false);

          Math.random = rndReal;
          return out;
        }""")

        for k in sorted(rt):
            if k.startswith('err'):
                chk(not rt[k], f'sin error en runtime ({k}): {rt[k]}')
        esperados = [
            ('precaliente13', 'precaliente: cola de 16 piezas (r54: sin flechas/campo/estela)'),
            ('palaMetalicaMontada', 'imán (r54): _imanPalaOsc montada (pala metálica)'),
            ('sembradoIman', 'mecánica: imán sembrado'),
            ('campoAbre', 'mecánica: el gatillo abre la ventana del imán (8 s)'),
            ('oscurecidoConVentana', 'imán (r54): con la ventana viva la pala SE OSCURECE'),
            ('oscurecidoSinVentana', 'imán (r54): al morir la ventana el oscurecido SE RETIRA'),
            ('rescateMarcaArmada', 'r57: la ventana JAMÁS arma campo por bola (la guía vive en la pala)'),
            ('empujeMarcado', 'r57: la pala del jugador queda armada con la guía (ppImanAim)'),
            ('sembradoPortal1', 'mecánica: portal sembrado con UNA carga (sorteo ×1)'),
            ('ventanaCon3Golpes', 'portal: abrir da SIEMPRE los 3 golpes de ventana'),
            ('matrizVaciaTrasAbrir', 'portal: la matriz puede quedar SIN el poder'),
            ('ventanaVivaSinMatriz', 'portal: la ventana SOBREVIVE sin cargas (el defecto r50 moría aquí)'),
            ('tresPortales', 'portal: los 3 golpes portalizan (cada uno con su viaje)'),
            ('finTrasTres', 'portal: la ventana muere SOLO tras el 3.er golpe'),
            ('cuenta321', 'ticks: cuenta sonora 3·2·1 exacta al agotarse el efecto'),
            ('haloGrande', 'efecto: el halo exagerado se ve (> 0,12 m)'),
            ('pstCanjea', 'passthrough: _pstAplicar(true) canjea fondo/niebla/sala'),
            ('pstRestaura', 'passthrough: _pstAplicar(false) restaura la escena'),
            ('pstInocuoDoble', 'passthrough: doble restore es inocuo'),
        ]
        for k, label in esperados:
            chk(rt.get(k) is True, label + ('' if rt.get(k) is True else
                f' [got={rt.get(k)!r}]'))

        await browser.close()

    chk(not errors, f'cero pageerrors ({len(errors)}: {errors[:3]})')
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
