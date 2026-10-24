#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.39 · PODERES — CADA PARTIDA NUEVA NACE CON LA PALA LIMPIA
(capas AH, en vivo).

Reporte del dueño tras probar V3.6.38:
  «Debes revisar que los poderes de la pala al iniciar una partida
   desaparezcan — en estos momentos me da la sensación de que permanecen
   los de una partida previa que no se han gastado.»

Causa raíz: la recogida completa (_megaNormReset) SOLO se llamaba al
ENTRAR EN EL HALL y al APAGAR «Pala Mejorada». Los caminos de nueva
partida que no pasan por el hall (revancha por gatillo, revancha de
menú, cambio de modo, online, vuelta de calibración y el REINICIO
AUTOMÁTICO del árbitro cuando el estado es 'over') arrancaban el
partido con la matriz de cargas, el icono ×N y los FX de la partida
anterior colgados de la pala.

Solución (ronda 47): UN hook — rules.onMatchStart — que el árbitro
(c06) avisa al FINAL de CADA startMatch y el núcleo (c12) registra UNA
vez apuntando a _megaNormReset. Un solo punto de aviso cubre TODOS los
caminos presentes y futuros: imposible olvidar uno. Idempotente (el
hall recogía antes de startMatch y repetir la recogida no rompe nada).

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del hook (campo en el constructor del
     árbitro, aviso al final de startMatch con try/catch, registro en
     el núcleo apuntando a _megaNormReset) + regresiones (la recogida
     del hall y del interruptor «Pala Mejorada» intactas).
  2) MECÁNICA REAL en headless — cargas concedidas → partido nuevo por
     startMatch: matriz vacía, índice a cero, icono oculto, los tres
     temporizadores a cero, FX null (mega/efecto/imán/flechas/halo/
     anillo), marcas de la bola limpias, multiplicador del rival y
     escalas LOD a 1; el REINICIO AUTOMÁTICO del árbitro (estado
     'over') también recoge; la recogida es IDEMPOTENTE (doble llamada
     sin errores); tras el reset el arsenal se vuelve a conceder y
     precalentar (el juego sigue vivo).

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
        # HOOK en el ÁRBITRO (c06 dentro del game.html servido)
        ('this.onMatchStart = null;',
         'árbitro: campo onMatchStart declarado (hook de arranque)'),
        ('try { if (this.onMatchStart) this.onMatchStart(); } catch (e) { /* nunca rompe el árbitro */ }',
         'árbitro: CADA startMatch avisa al hook (con blindaje try/catch)'),
        # REGISTRO en el NÚCLEO (c12)
        ('this.rules.onMatchStart = () => {',
         'núcleo: registra el hook UNA vez (constructor)'),
        ('try { this._megaNormReset(); } catch (e) { /* nunca rompe el árbitro */ }',
         'núcleo: el hook recoge TODO el arsenal (_megaNormReset)'),
        # REGRESIONES: las recogidas que YA existían siguen intactas
        ('this._megaNormReset();   // v3.6.34: el hall es zona neutra — pala como siempre',
         'el HALL sigue recogiendo al entrar (zona neutra)'),
        ('if (!this.palaMejorada) this._megaNormReset();',
         'apagar «Pala Mejorada» sigue recogiendo al instante'),
        # Reglas intactas (regresión de las rondas 45-46)
        ('const IMAN_DUR = 10;', 'imán: ventana 10 s (r56: regla del dueño)'),
        ('const EFECTO_DUR = 10;', 'efecto: ventana 10 s (r56: regla del dueño)'),
        ('const MEGA_GOLPES = 20;', 'mega: carga cada 20 toques (r56: «no antes de 20»)'),
        ('const MEGA_LOD_JUEGO = 0.5;', 'LOD 50 % en juego intacto'),
        ('V3.6.56-SDK6', 'sello de versión servida'),
    ]:
        chk(needle in game, label)
    chk(game.count('_megaNormReset') >= 4,
        'recogida cableada en todos sus puntos (definición + hall + pmej + hook)')

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
          const rndReal = Math.random;

          // · EL HOOK ESTÁ REGISTRADO
          out.hookVivo = typeof G.rules.onMatchStart === 'function';

          // · SEMBRAR cargas y estados vivos (como una partida en marcha)
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');        // el propio arranque ya recoge
          Math.random = () => 0.1;            // siempre 'mega'
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG1 = String(e); }
          for (let i = 0; i < 10; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errGD = String(e); }
          }
          // 2.ª carga: frame en 'point' (el rally nuevo REINICIA la cuenta,
          // igual que en la capa AG) y otra ventana de 20 toques
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errGP = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG2 = String(e); }
          // estado VIVO: efecto + imán activos y marcas en la bola/pala
          G._efectoT = 5; G._efectoWarn = true;
          try { G._buildEfectoFx(); G._efectoFxVis(true); } catch (e) { /* */ }
          try { G._buildEfectoHalo(); } catch (e) { /* */ }
          G._imanT = 6; G._imanAsistidas = 1; G._imanWarn = true;
          try { G._buildImanFx(); G._imanFxVis(true); } catch (e) { /* */ }
          G.ball.ppEfecto = true;
          G.ball.ppIman = true; G.ball.ppImanTocada = true;
          if (G.controllerPaddles && G.controllerPaddles[0]) G.controllerPaddles[0].ppEfectoMul = 1.8;
          if (G.paddleMounts && G.paddleMounts[0]) G.paddleMounts[0].scale.setScalar(0.5);
          out.sembrado = G._megaMatriz.length > 0 && G._megaMatriz[0].n >= 2 &&
            G._megaIconOn === true && G._efectoT > 0 && G._imanT > 0;
          out.iconoVisibleAntes = G._megaIconOn === true;

          // · PARTIDA NUEVA por startMatch: la pala debe quedar EXACTA
          G.rules.startMatch('match');
          out.matrizVacia = Array.isArray(G._megaMatriz) && G._megaMatriz.length === 0;
          out.indiceCero = G._megaIdx === 0;
          out.iconoFuera = G._megaIconOn === false;
          out.megaTcero = G._megaT === 0 && G._megaS === 1 && G._megaWarn === false;
          out.efectoDuerme = G._efectoT === 0 && G._efectoWarn === false;
          out.imanDuerme = G._imanT === 0 && G._imanAsistidas === 0 && G._imanWarn === false;
          out.fxMegaNull = G._megaFx === null || G._megaFx === undefined;
          out.fxEfectoNull = G._efectoFx === null || G._efectoFx === undefined;
          out.fxImanNull = !G._imanFx || G._imanFx.every((fx) => !fx || fx.visible === false);
          out.flechasNull = G._megaArrows === null || G._megaArrows === undefined;
          out.haloNull = G._efectoHalo === null || G._efectoHalo === undefined;
          out.bolaLimpia = G.ball.ppEfecto === false &&
            G.ball.ppIman === undefined && G.ball.ppImanTocada === false;
          out.palaMulUno = !G.controllerPaddles || !G.controllerPaddles[0] ||
            G.controllerPaddles[0].ppEfectoMul === 1;
          out.escalaUno = !G.paddleMounts || !G.paddleMounts[0] ||
            Math.abs(G.paddleMounts[0].scale.x - 1) < 1e-6;
          out.lodUno = G._megaLOD === 1;
          // re-anclado r50: el precaliente se RE-ARMA al empezar (anti-lag,
          // 13 piezas calientes para la carga — la congelación es imposible)
          out.prewarmApagado = Array.isArray(G._megaPrewarmQ) &&
            G._megaPrewarmQ.length >= 13;
          out.baseHitNum = typeof G._BASE_HIT === 'number' && G._BASE_HIT > 0;

          // · IDEMPOTENCIA: recoger DOS veces seguidas no rompe nada
          let errDoble = null;
          try { G._megaNormReset(); G._megaNormReset(); G.rules.startMatch('match'); }
          catch (e) { errDoble = String(e); }
          out.dobleResetSinError = errDoble === null;

          // · REINICIO AUTOMÁTICO del árbitro (estado 'over') TAMBIÉN recoge
          Math.random = () => 0.5;            // otro poder distinto esta vez
          G.rules.state = 'rally'; G.rules.rallyHits = 20;
          try { G.updateMega(1 / 60); } catch (e) { out.errG3 = String(e); }
          out.resembrado = G._megaMatriz.length > 0;
          G.rules.state = 'over';
          G.rules.stateTimer = 0;             // el árbitro reinicia SOLO
          try { G.rules.update(1 / 60); } catch (e) { out.errOver = String(e); }
          out.autoReinicioLimpia = G._megaMatriz.length === 0 &&
            G._megaIconOn === false && G._efectoT === 0;

          // · tras el reinicio el árbitro queda en SAQUE (partido vivo)
          out.arbitroSirve = G.rules.state === 'serve';

          Math.random = rndReal;
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'window.__PP_GAME disponible (juego vivo)')
        else:
            chk(rt.get('hookVivo') is True, 'hook rules.onMatchStart REGISTRADO y vivo')
            chk(rt.get('sembrado') is True,
                'siembra: cargas ×2 + icono visible + efecto/imán activos')
            chk(rt.get('iconoVisibleAntes') is True, 'icono ×N visible antes del corte')
            chk(rt.get('matrizVacia') is True, 'partida nueva: matriz de cargas VACÍA')
            chk(rt.get('indiceCero') is True, 'partida nueva: índice de selección a CERO')
            chk(rt.get('iconoFuera') is True, 'partida nueva: icono del mango OCULTO')
            chk(rt.get('megaTcero') is True, 'partida nueva: SÚPER MEGA a cero')
            chk(rt.get('efectoDuerme') is True, 'partida nueva: SÚPER EFECTO dormido')
            chk(rt.get('imanDuerme') is True, 'partida nueva: SÚPER IMÁN dormido')
            chk(rt.get('fxMegaNull') is True, 'partida nueva: FX mega recogido (null)')
            chk(rt.get('fxEfectoNull') is True, 'partida nueva: FX efecto recogido (null)')
            chk(rt.get('fxImanNull') is True, 'partida nueva: FX imán OCULTO (se conserva precalentado)')
            chk(rt.get('flechasNull') is True, 'partida nueva: flechas recogidas (null)')
            chk(rt.get('haloNull') is True, 'partida nueva: halo rojo recogido (null)')
            chk(rt.get('bolaLimpia') is True,
                'partida nueva: bola SIN marcas (ppEfecto/ppIman/ppImanTocada)')
            chk(rt.get('palaMulUno') is True, 'partida nueva: multiplicador del rival a 1')
            chk(rt.get('escalaUno') is True, 'partida nueva: escala de la pala a 1')
            chk(rt.get('lodUno') is True, 'partida nueva: LOD al 100 %')
            chk(rt.get('prewarmApagado') is True, 'partida nueva: precaliente RE-ARMADO (anti-lag r50)')
            chk(rt.get('baseHitNum') is True, 'partida nueva: radio de asistencia base intacto')
            chk(rt.get('dobleResetSinError') is True,
                'IDEMPOTENCIA: doble recogida + startMatch sin errores')
            chk(rt.get('resembrado') is True, 'tras el corte el juego VUELVE a conceder')
            chk(rt.get('autoReinicioLimpia') is True,
                'REINICIO AUTOMÁTICO del árbitro (estado over) TAMBIÉN recoge')
            chk(rt.get('arbitroSirve') is True,
                'tras el reinicio automático el árbitro queda en SAQUE')

        for e in errors[:5]:
            print('  ✗ pageerror:', e)
        chk(len(errors) == 0, 'cero pageerrors durante la prueba')

        await browser.close()

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
