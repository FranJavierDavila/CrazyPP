#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.40 · PODERES — EL PODER ACTIVO SE VE EN LA PALA (capa AI, en vivo).

Petición del dueño (ronda 48):
  «¿Se te ocurre alguna manera de que el usuario sepa el tipo de poder
   de pala que tiene activo, sin que moleste durante el juego?»

Recomendación ejecutada (FASE 42): el icono del mango NO desaparece al
activar — pasa a MODO ACTIVO: muestra el poder EN MARCHA con un ANILLO
DE TIEMPO que se vacía (oro mega / cian efecto / azul imán — la misma
firma que abraza la silueta de la pala), PARPADEA en los últimos 2 s y
al terminar vuelve al modo INVENTARIO (seleccionado ×N) o se esconde si
no quedan cargas. UN SOLO icono en la pala en todo momento (regla FASE
38 intacta), cero HUD, cero texto, cero voces nuevas. Lecciones aplicadas:
redibujo DIFERIDO fuera del frame del gatillo (r46) + AHORRADO por
muescas de 1/24 de vuelta + canvas persistente + el indicador duerme en
cada _megaNormReset (FASE 41: partida nueva = pala limpia).

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del modo activo (estado, reconciliación,
     anillo en el canvas, parpadeo, flechas que descansan, pulso) +
     reglas intactas (15/8/8 s, tope ×3, 11 golpes, LOD) + hook FASE 41.
  2) MECÁNICA REAL en headless — ciclo completo: MEGA abre → icono en
     modo ACTIVO con textura persistente y anillo al día; el anillo
     PROGRESA y decrece con el tiempo; ALARGA mantiene el modo y llena
     el anillo con TODO el restante; PARPADEO en los últimos 2 s sin
     romper nada; expiración → vuelve al INVENTARIO; EFECTO activo con
     FLECHAS que descansan y vuelven; IMÁN abre y REFRESCA sin gasto;
     LOD del icono en AMBOS modos; PARTIDA NUEVA recoge el indicador.

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
        # ESTADO del indicador (constructor)
        ("this._megaActivaId = null;        // 'mega' | 'efecto' | 'iman' | null",
         'estado: _megaActivaId declarado (último poder lanzado)'),
        ('this._megaIconModo = \'\';',
         'estado: modo del icono (inv/act) declarado'),
        # RELOJ + reconciliación de expiración
        ('_megaActivaRest() {', 'reloj: _megaActivaRest() definido'),
        ('if (this._megaActivaId && this._megaActivaRest() <= 0) {',
         'expiración: el indicador cae con SU poder (reconciliación)'),
        # VISIBILIDAD con dos modos (un solo icono, regla FASE 38)
        ('const icoOn = on && (this._megaMatriz.length > 0 || !!activaId);',
         'visibilidad: el icono vive con inventario O poder activo'),
        ("const modo = activaId ? 'act' : 'inv';",
         'modos: act/inv con cambio de DIBUJO diferido y pulso suave'),
        ('this._megaIconPop = 0.4;   // pulso suave',
         'cambio de modo: pulso suave de entrada'),
        # ANILLO DE TIEMPO en el canvas persistente
        ('c2.arc(128, 128, 117, a0, a0 + Math.PI * 2 * frac);',
         'anillo: arco dibujado según el tiempo restante'),
        ("'rgba(8,12,20,0.62)'", 'anillo: pista tenue completa'),
        ("activo === 'efecto' ? '#54d8f0'",
         'anillo: color por poder (oro/cian/azul = firma del canto)'),
        ('this._megaTex.needsUpdate = true;   // recalentada in-place',
         'textura PERSISTENTE intacta (lección ronda 46)'),
        ('Math.abs(frac - this._megaActivaFrac) >= 1 / 24',
         'anillo vivo: redibujo AHORRADO por muescas (1/24 de vuelta)'),
        # PARPADEO de los últimos 2 s
        ('const late = (modo === \'act\' && this._megaActivaRest() < 2);',
         'parpadeo: últimos 2 s del poder activo'),
        # CADA gatillo declara SU modo activo (abierto + refresco/alargue)
        ("this._megaActivaId = 'mega';", 'mega: gatillo abre y ALARGA marcan modo'),
        ("this._megaActivaId = 'efecto';", 'efecto: apertura y recarga marcan modo'),
        ("this._megaActivaId = 'iman';", 'imán: apertura y refresco marcan modo'),
        # FLECHAS: descansan en modo ACTIVO
        ("const flechasOn = on && icoOn && modo === 'inv' &&",
         'flechas: descansan mientras un poder corre (solo inventario)'),
        # DIBUJO por modos (activo sin ×N; inventario con ×N)
        ("const id = activo || (ent ? ent.id : 'mega');",
         'dibujo: en modo ACTIVO el icono muestra el poder en marcha'),
        ('const n = activo ? 0 : (ent ? ent.n : 0);',
         'dibujo: el ×N de cargas solo en modo inventario'),
        # REGLAS INTACTAS (regresión rondas 45-47)
        ('const MEGA_DUR = 15;', 'mega: ventana 15 s por carga intacta'),
        ('const EFECTO_DUR = 8;', 'efecto: ventana 8 s intacta'),
        ('const IMAN_DUR = 8;', 'imán: ventana 8 s intacta'),
        ('const MEGA_TOPE = 3;', 'tope ×3 de cargas intacto'),
        ('const MEGA_GOLPES = 11;', 'carga por rally 11+ intacta'),
        ('const MEGA_LOD_JUEGO = 0.5;', 'LOD 50 % en juego intacto'),
        ('const MEGA_LOD_MIRA = 0.978;', 'LOD 100 % con la mirada intacto'),
        # FASE 41 intacta: partida nueva = pala limpia
        ('try { if (this.onMatchStart) this.onMatchStart(); } catch (e) { /* nunca rompe el árbitro */ }',
         'FASE 41: el hook de partida nueva sigue avisando'),
        ('V3.6.43-SDK6', 'sello de versión servida'),
    ]:
        chk(needle in game, label)
    chk(game.count("this._megaActivaId = null;") >= 2,
        'reset: el indicador duerme en constructor + _megaNormReset')
    chk(game.count("_megaActivaId = 'mega';") == 2,
        'mega: exactamente apertura + alargue marcan el modo')

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

          // · ARRANQUE limpio (FASE 41) + precaliente drenado
          G.champs.activeId = 'locura';
          G.rules.startMatch('match');
          Math.random = () => 0.1;                 // siempre 'mega'
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errU0 = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errU1 = String(e); }
          for (let i = 0; i < 10; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errD = String(e); }
          }
          // 2.ª carga MEGA (×2): frame en 'point' entre ventanas
          G.rules.state = 'point';
          try { G.updateMega(1 / 60); } catch (e) { out.errGP = String(e); }
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          try { G.updateMega(1 / 60); } catch (e) { out.errG2 = String(e); }
          out.sembrado = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 2;

          // · MEGA ACTIVA: el icono NO desaparece — modo ACTIVO
          const texAntes = G._megaTex;
          let tM = null;
          try { tM = G.megaTrigger(libre); } catch (e) { out.errM = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errM1 = String(e); }
          out.megaAbre = tM === true && G._megaT > 14.9;
          out.iconoModoActivo = G._megaIconOn === true &&
            G._megaIconModo === 'act' && G._megaActivaId === 'mega';
          out.durAnillo = G._megaActivaDur === 15;
          out.texturaMismaActiva = G._megaTex === texAntes && texAntes !== null;
          out.anilloAlDia = G._megaActivaFrac > 0.9 && G._megaActivaFrac <= 1;

          // · el ANILLO PROGRESA (decrece con el tiempo, en rango)
          for (let i = 0; i < 132; i++) {          // 2,2 s de rally
            try { G.updateMega(1 / 60); } catch (e) { out.errP = String(e); }
          }
          out.anilloProgresado = G._megaActivaFrac > 0.75 &&
            G._megaActivaFrac < 0.91;
          out.anilloEnRango = G._megaActivaFrac >= 0 &&
            G._megaActivaFrac <= 1;

          // · ALARGA: anillo lleno con TODO el restante, mismo modo
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 11; G.updateMega(1 / 60);
          let tM2 = null;
          const tAntesE = G._megaT;
          try { tM2 = G.megaTrigger(libre); } catch (e) { out.errM2 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errM3 = String(e); }
          out.megaAlargaDur = tM2 === true && G._megaActivaId === 'mega' &&
            G._megaT > tAntesE + 14.9 &&
            Math.abs(G._megaActivaDur - G._megaT) < 0.1;

          // · PARPADEO en los últimos 2 s (opacity < 0.96, sin romper)
          G._megaT = 1.5;
          try { G.updateMega(1 / 60); G.updateMega(1 / 60); }
          catch (e) { out.errL = String(e); }
          const icoL = G._megaIcon[G.paddleHand];
          out.iconoLateParpadea = !!icoL && icoL.material.opacity <= 0.9501 &&
            icoL.material.opacity >= 0.49;

          // · EXPIRACIÓN: vuelve al INVENTARIO (queda mega ×1)
          G._megaT = 0.005;                   // un frame (1/60) la cruza
          try { G.updateMega(1 / 60); } catch (e) { out.errE = String(e); }
          out.vuelveInventario = G._megaActivaId === null &&
            G._megaIconModo === 'inv' && G._megaIconOn === true &&
            G._megaActivaFrac === -1;
          out.megaQuedaUna = G._megaMatriz.length === 1 &&
            G._megaMatriz[0].n === 1;

          // · EFECTO ACTIVO: modo, dur y anillo de SU ventana (8 s)
          Math.random = () => 0.3;
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 11; G.updateMega(1 / 60);
          Math.random = () => 0.3;                 // efecto ×2 (tras gastar queda ×1)
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 11; G.updateMega(1 / 60);
          let tE = null;
          try { tE = G.megaTrigger(libre); } catch (e) { out.errE1 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errE2 = String(e); }
          out.efectoActivo = tE === true && G._megaActivaId === 'efecto' &&
            G._megaIconModo === 'act' && G._megaActivaDur === 8 &&
            G._efectoT > 7.9;
          out.anilloEfecto = G._megaActivaFrac > 0 && G._megaActivaFrac <= 1;
          out.efectoQuedaUna = G._megaMatriz.length === 2 &&
            G._megaMatriz.find((x) => x.id === 'efecto').n === 1;

          // · FLECHAS descansan en modo ACTIVO y vuelven al inventario
          const parF = G._megaArrows ? G._megaArrows[G.paddleHand] : null;
          out.flechasDescansan = !!parF && parF.every((s) => !s.visible);
          G._efectoT = 0;
          try { G.updateMega(1 / 60); } catch (e) { out.errF = String(e); }
          out.flechasVuelven = !!parF && parF.some((s) => s.visible);

          // · IMÁN: abre, REFRESCA sin gasto y expira a inventario
          Math.random = () => 0.6;
          G.rules.state = 'point'; G.updateMega(1 / 60);
          G.rules.state = 'rally'; G.rules.rallyHits = 11; G.updateMega(1 / 60);
          let tI = null;
          try { tI = G.megaTrigger(libre); } catch (e) { out.errI1 = String(e); }
          try { G.updateMega(1 / 60); } catch (e) { out.errI2 = String(e); }
          out.imanActivo = tI === true && G._megaActivaId === 'iman' &&
            G._megaIconModo === 'act' && G._megaActivaDur === 8;
          let tI2 = null;
          try { tI2 = G.megaTrigger(libre); } catch (e) { out.errI3 = String(e); }
          out.imanRefrescaSinGasto = tI2 === true && G._imanT > 7.9 &&
            G._megaMatriz.find((x) => x.id === 'iman').n === 1;
          G._imanT = 0.005;                   // un frame (1/60) la cruza
          try { G.updateMega(1 / 60); } catch (e) { out.errI4 = String(e); }
          out.imanExpiraVuelve = G._megaActivaId === null &&
            G._megaIconModo === 'inv' && G._megaIconOn === true;

          // · LOD del icono en AMBOS modos (50 % en rally)
          G.rules.state = 'rally'; G._megaLOD = 1;
          G._megaT = 10; G._megaActivaId = 'mega'; G._megaActivaDur = 15;
          for (let i = 0; i < 90; i++) {
            try { G.updateMega(1 / 60); } catch (e) { out.errLd = String(e); }
          }
          out.lodModoActivo = G._megaLOD < 0.55 &&
            G._megaIcon[G.paddleHand].scale.x < 0.031;

          // · PARTIDA NUEVA (FASE 41 + 42): el indicador TAMBIÉN duerme
          G.rules.startMatch('match');
          out.partidaNuevaLimpia = G._megaActivaId === null &&
            G._megaIconModo === '' && G._megaActivaFrac === -1 &&
            G._megaIconOn === false && G._megaT === 0;

          Math.random = rndReal;
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'window.__PP_GAME disponible (juego vivo)')
        else:
            chk(rt.get('sembrado') is True,
                'siembra: mega ×2 en la matriz (dos rallyes de 11)')
            chk(rt.get('megaAbre') is True, 'gatillo: MEGA abre (regresión)')
            chk(rt.get('iconoModoActivo') is True,
                'EL ICONO NO DESAPARECE: modo ACTIVO con la MEGA en marcha')
            chk(rt.get('durAnillo') is True, 'anillo: ventana de 15 s de referencia')
            chk(rt.get('texturaMismaActiva') is True,
                'textura PERSISTENTE en modo ACTIVO (misma referencia)')
            chk(rt.get('anilloAlDia') is True,
                'anillo al día tras el primer frame activo')
            chk(rt.get('anilloProgresado') is True,
                'el anillo PROGRESA: decrece con el tiempo gastado')
            chk(rt.get('anilloEnRango') is True, 'anillo siempre en rango [0,1]')
            chk(rt.get('megaAlargaDur') is True,
                'ALARGA: anillo lleno con TODO el tiempo restante')
            chk(rt.get('iconoLateParpadea') is True,
                'PARPADEO en los últimos 2 s (opacity < 0.96)')
            chk(rt.get('vuelveInventario') is True,
                'EXPIRACIÓN: el icono vuelve al modo inventario')
            chk(rt.get('megaQuedaUna') is True,
                'cargas honestas: queda mega ×1 tras abrir con ×2')
            chk(rt.get('efectoActivo') is True,
                'EFECTO activo: modo, dur 8 s y ventana propia')
            chk(rt.get('anilloEfecto') is True, 'anillo del efecto en rango')
            chk(rt.get('efectoQuedaUna') is True, 'efecto: queda ×1 en matriz')
            chk(rt.get('flechasDescansan') is True,
                'FLECHAS descansan mientras el efecto corre')
            chk(rt.get('flechasVuelven') is True,
                'FLECHAS vuelven al terminar (inventario)')
            chk(rt.get('imanActivo') is True,
                'IMÁN activo: modo, dur 8 s')
            chk(rt.get('imanRefrescaSinGasto') is True,
                'imán REFRESCA sin gastar carga (spec del dueño)')
            chk(rt.get('imanExpiraVuelve') is True,
                'imán expirado: el icono vuelve al inventario')
            chk(rt.get('lodModoActivo') is True,
                'LOD del icono en modo ACTIVO: 50 % en rally')
            chk(rt.get('partidaNuevaLimpia') is True,
                'PARTIDA NUEVA: el indicador activo TAMBIÉN duerme (FASE 41+42)')

        for e in errors[:5]:
            print('  ✗ pageerror:', e)
        chk(len(errors) == 0, 'cero pageerrors durante la prueba')

        await browser.close()

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
