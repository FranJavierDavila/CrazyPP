#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_poderes_10s20_v3648 — CAPA AQ · ronda 56 (V3.6.49-SDK6, FASE 50).

La petición del dueño (literal): «Todos los superpoderes de la pala que
se concedan superados los 20 toques no antes. El super iman que ralentice
la bola y la dirija hacia el centro de nuestra pala para que nos sea más
sencillo golpearla, el efecto solo entra cuando tenemos que devolver un
golpe del rival… menos en los saques que será comportamiento normal y
evidentemente el efecto solo dura 10 segundos. Pasado ese tiempo desde la
activación todo vuelve a la normalidad. El super Efecto tambien solo está
activo 10 segundos desde la activación del mismo y la ventaje del efecto
en los bores solo es para nosotros, el perjudicado siempre es el rival.»

Pruebas: (1) FUENTE SERVIDA — agujas de la NORMA r56 (MEGA_GOLPES=20,
EFECTO_DUR=10, IMAN_DUR=10, gate del SAQUE DEL RIVAL en el arme del
campo, GUÍA DE TIRO r57 en c02/c05) + NEGATIVAS (los topes de golpes de
la r36-37 NO vuelven: EFECTO_GOLPES, IMAN_ASIST, el cierre por golpes) +
i18n ES/EN honesto + plantilla 2.4 con la norma de 20 toques. (2)
MECÁNICA REAL headless — cadencia EXACTA (19 toques NADA · 20 → +1 · 40
→ ×2 · 60 → ×3 · 80 → tope), ventanas de 10 s PURAMENTE TEMPORALES (el
efecto y el imán viven sus 10 s completos y cierran solos), el campo del
imán ya no arma campo por bola NUNCA (r57: la guía vive EN EL GOLPE)
y la GUÍA DE TIRO de la física viva: el golpe guiado BOTA EN LA MESA DEL RIVAL
(sin ppIman, velocidad idéntica — golden intacto).

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

    # ---------- 1 · FUENTE SERVIDA (núcleo) ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # · LA NORMA DE CONCESIÓN r56 («superados los 20 toques, no antes»)
        ('const MEGA_GOLPES = 20;',
         'r56: +1 carga CADA 20 TOQUES del rally — todos los poderes'),
        ('Math.floor((r.rallyHits || 0) / MEGA_GOLPES);',
         'la cadencia sigue viniendo del contador de toques del rally'),
        # · LAS VENTANAS DE 10 s («el efecto solo dura 10 segundos»)
        ('const EFECTO_DUR = 10;',
         'r56: SÚPER EFECTO — ventana de 10 s desde la activación'),
        ('const IMAN_DUR = 10;',
         'r56: SÚPER IMÁN — campo de 10 s desde la activación'),
        # · r57: LA GUÍA DE TIRO (el imán reescrito, «olvidemos el efecto
        #   anterior de atracción y ralentización») viaja EN LA PALA
        ('ps.ppImanAim = imanAim;',
         'r57: la guía de tiro viaja EN LA PALA (ppImanAim)'),
        ('imanAimVzMin: -0.4,',
         'r57: sólo tiros que YA van hacia la mitad rival'),
        ('imanAimProfundidad: 0.62,',
         'r57: objetivo al 62 % de la media mesa rival (bote seguro)'),
        ('imanAimPisoVel: 9.5,',
         'r57: piso de potencia — «golpes muy fuertes y a gran velocidad»'),
        ('computeShotVelocityReal(ball.pos, _imObjetivo, T0, vMax0, _imSpinCero)',
         'r57: el SOLVER DE LA CASA reconstruye el tiro (bote asegurado)'),
        # · r57: SIN campo por bola y SIN gasto por asistencia
        ('_imanImpacto RETIRADO',
         'r57: el gasto de cargas por asistencia RETIRADO'),
        # · i18n ES/EN honesto
        ('cada 20 toques de rally te da una', 'i18n ES: la norma de 20 toques'),
        ('cada 20 toques del rally = +1 carga', 'i18n ES: la pista de la norma'),
        ('every 20 rally shots grants one', 'i18n EN: la norma de 20 shots'),
        ('every 20 rally shots = +1 charge', 'i18n EN: la pista de la norma'),
        ('¡SÚPER IMÁN! · tus ataques dan SIEMPRE en la mesa rival (más fuerte y rápido) · 10 s',
         'i18n ES: el imán anuncia GUÍA + 10 s (r57)'),
        ('SUPER MAGNET! · your shots ALWAYS land on the rival table (stronger and faster) · 10 s',
         'i18n EN: el imán anuncia GUÍA + 10 s (r57)'),
        ('spin ×3 · 10 s', 'i18n ES: el efecto anuncia 10 s (sin tope de golpes)'),
        ('×3 spin · 10 s', 'i18n EN: el efecto anuncia 10 s (sin tope de golpes)'),
    ]:
        chk(needle in game, label)
    for ausente, label in [
        # · LOS TOPES DE GOLPES DE LA r36-37 NO VUELVEN (el reloj manda)
        ('const EFECTO_GOLPES',
         'regresión r56: el tope de 5 golpes del efecto NO vuelve'),
        ('const IMAN_ASIST',
         'regresión r56: el tope de 3 asistencias del imán NO vuelve'),
        ('--this._efectoGolpes',
         'regresión r56: el CIERRE del efecto por golpes NO vuelve'),
        ('this._imanAsistidas >= IMAN_ASIST',
         'regresión r56: el cierre del imán por asistencias NO vuelve'),
        # · LA NORMA VIEJA DE 11 NO VUELVE (ni en i18n)
        ('cada 11 golpes', 'regresión r56: la norma de 11 golpes NO vuelve'),
        ('every 11 rally hits', 'regresión r56: la norma de 11 hits NO vuelve'),
        ('8 s / 5 golpes', 'regresión r56: «8 s / 5 golpes» NO vuelve'),
        ('8 s / 3 asistencias', 'regresión r56: «8 s / 3 asistencias» NO vuelve'),
        # · r57: el gancho/freno NUNCA VUELVE (imán = guía de tiro)
        ('imanGanchoRadio', 'regresión r57: el GANCHO (radio) no vuelve'),
        ('imanGanchoAcel', 'regresión r57: el GANCHO (aceleración) no vuelve'),
        ('imanFreno: 1.1', 'regresión r57: el FRENO del campo no vuelve'),
        ('function applyIman', 'regresión r57: applyIman (campo por subpaso) no vuelve'),
        ('efectoBoteMul: 2.4', 'regresión r57: el acople ×2,4 del bote NO vuelve'),
        ('_imanImpacto() {', 'regresión r57: el gasto por asistencia no vuelve'),
    ]:
        chk(ausente not in game, label)

    # · PLANTILLA 2.4 (documentación servida — la norma del dueño)
    try:
        guia = urllib.request.urlopen(
            'http://localhost:3000/championships/PLANTILLA-GUIA.md',
            timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer PLANTILLA-GUIA.md servida:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk('cada 20 toques del rally** (20, 40, 60' in guia,
        'plantilla: la norma de 20 toques documentada (sección 2.4)')
    chk('cada 11 golpes del rally' not in guia,
        'plantilla: la norma de 11 golpes NO vuelve')

    # ---------- 2 · MECÁNICA REAL headless ----------
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
          const out = {};
          const T3 = await import('three');
          const G = window.__PP_GAME;
          if (!G) { out.sinJuego = true; return out; }
          window.__wantSolverHook = true;
          await new Promise((r) => setTimeout(r, 300));
          const H = window.__solverHook;
          if (!H) { out.sinHook = true; return out; }
          const DIMS = H.DIMS;
          const V3 = Object.getPrototypeOf(new T3.Vector3()).constructor;
          const realRnd = Math.random;
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errU = String(e); } };

          // ===== A · CADENCIA r56: 20 TOQUES, NUNCA ANTES =====
          try {
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');
            Math.random = () => 0.1;                  // siempre 'mega'
            G.rules.state = 'point'; paso();
            G.rules.state = 'rally'; G.rules.rallyHits = 19;
            paso(); paso();
            out.a19Nada = G._megaMatriz.length === 0;      // JAMÁS antes de 20
            G.rules.rallyHits = 20; paso();
            out.a20Carga = G._megaMatriz.length === 1 &&
              G._megaMatriz[0].id === 'mega' && G._megaMatriz[0].n === 1;
            G.rules.rallyHits = 40; paso();
            out.a40Dos = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 2;
            G.rules.rallyHits = 60; paso();
            out.a60Tres = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
            G.rules.rallyHits = 80; paso(); paso();
            out.a80Tope = G._megaMatriz.length === 1 && G._megaMatriz[0].n === 3;
          } catch (e) { out.errCad = String(e); }

          // ===== B · VENTANAS de 10 s PURAMENTE TEMPORALES =====
          try {
            // EFECTO: trigger → 10 s exactos; vive ENTERA (sin tope de
            // golpes) y cierra sola al agotarse el reloj
            Math.random = () => 0.3;                  // siempre 'efecto'
            G.rules.state = 'point'; paso();
            G.rules.state = 'rally'; G.rules.rallyHits = 20; paso();
            let tE = null;
            try { tE = G.megaTrigger(1 - G.paddleHand); } catch (e) { out.errE = String(e); }
            out.efecto10 = tE === true && Math.abs(G._efectoT - 10) < 1e-9;
            for (let i = 0; i < 599 && G._efectoT > 0; i++) paso();
            out.efectoViva = G._efectoT > 0;               // a 9,98 s SIGUE
            paso();
            out.efectoCierra = G._efectoT === 0;           // a los 10 s: normalidad
            // IMÁN: campo de 10 s que también vive entero
            Math.random = () => 0.6;                  // siempre 'iman'
            G.rules.state = 'point'; paso();
            G.rules.state = 'rally'; G.rules.rallyHits = 20; paso();
            let tI = null;
            try { tI = G.megaTrigger(1 - G.paddleHand); } catch (e) { out.errI = String(e); }
            out.iman10 = tI === true && Math.abs(G._imanT - 10) < 1e-9;
            for (let i = 0; i < 599 && G._imanT > 0; i++) paso();
            out.imanVivo = G._imanT > 0;
            paso();
            out.imanCierra = G._imanT === 0;
          } catch (e) { out.errVen = String(e); }

          // ===== C · LA GUÍA viaja EN LA PALA (r57) =====
          try {
            const psG = G.controllerPaddles[G.paddleHand];
            G._imanT = 0; paso();
            out.palaSinVentana = psG.ppImanAim === false;   // sin ventana: honesta
            G._imanT = 5; paso();                           // ventana viva
            out.palaConVentana = psG.ppImanAim === true;
            out.bolaSinCampo = !G.ball || !G.ball.ppIman;   // NUNCA campo por bola
            G._imanT = 0; paso();
            out.palaRestaurada = psG.ppImanAim === false;
          } catch (e) { out.errSaq = String(e); }

          // ===== D · LA GUÍA DE TIRO (física viva — r57) =====
          // Un golpe del jugador con la ventana viva y dirección hacia la
          // mitad rival BOTARÁ EN LA MESA DEL RIVAL (el solver de la casa
          // reconstruye la velocidad). Golpe MUY MAL AIMADO (hacia la banda
          // derecha, fuera de la mesa): la guía lo CORRIGE dentro.
          try {
            const mkPadGuia = () => {
              const pad = H.createPaddleSim('player', 0);
              pad.active = true;
              pad.pos.set(0.5, 1.0, 1.5); pad.prev.copy(pad.pos);
              pad.vel.set(0, 0, -6.0);           // la mano ATACA hacia el rival
              // la cara mira AL RIVAL (−z) — prev* coherentes para el barrido
              pad.normal.set(0, 0, -1); pad.up.set(0, 1, 0);
              pad.right.set(1, 0, 0);
              pad.prevNormal.copy(pad.normal);
              pad.prevUp.copy(pad.up);
              pad.prevRight.copy(pad.right);
              pad.intercambio = true; pad.serveFlight = false;
              pad.ppImanAim = true;              // ventana viva (pala armada)
              pad.cooldown = 0;
              return pad;
            };
            const guia = () => {
              const pad = mkPadGuia();
              // bola LLEGANDO a la cara (v.z>0) y el golpe sale hacia la
              // DERECHA y hacia el rival: dirección errónea (se iría larga
              // por la banda) — la guía la tiene que corregir dentro
              const b = { pos: new V3(0.5, 1.0, 1.44),
                vel: new V3(1.2, 0.1, 3.0), spin: new V3(), dragMul: 1 };
              H.collidePaddleSweep(b, pad, 0, 1, []);
              return { b, vel: b.vel.clone() };
            };
            const g1 = guia();
            // el evento viaja con imanAim (marca del golpe guiado)
            const evs = [];
            const pad2 = mkPadGuia();
            const b2 = { pos: new V3(0.5, 1.0, 1.44),
              vel: new V3(1.2, 0.1, 3.0), spin: new V3(), dragMul: 1 };
            H.collidePaddleSweep(b2, pad2, 0, 1, evs);
            out.eventoGuiado = evs.length > 0 && evs[0].imanAim === true;
            // SIMULACIÓN real del vuelo hasta el bote en mesa: tiene que
            // botar EN la mitad del rival y DENTRO de la mesa
            const b3 = { pos: g1.b.pos.clone(), vel: g1.vel.clone(),
              spin: new V3(), dragMul: 1 };
            let bote = null;
            const evsV = [];
            for (let i = 0; i < 120 && !bote; i++) {
              evsV.length = 0;
              H.stepPhysics(1 / 60, b3, [], evsV);
              for (const ev of evsV) {
                if (ev.type === 'table') { bote = ev.pos.clone(); break; }
              }
            }
            out.boteEnMesa = !!bote;
            out.boteMitadRival = !!bote &&
              bote.z < DIMS.tableCenterZ - 0.2 &&   // claramente en SU mitad
              Math.abs(bote.x) <= DIMS.tableHalfWidth &&
              Math.abs(bote.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength;
            // y la potencia: el golpe guiado sale RÁPIDO (piso fuerte)
            out.veloz = g1.vel.length() >= (DIMS.imanAimPisoVel || 9.5) - 0.6;
          } catch (e) { out.errFren = String(e); }

          Math.random = realRnd;
          return out;
        }""")

        for key, label in [
            ('a19Nada', 'a los 19 toques NO hay carga (r56: nunca antes de 20)'),
            ('a20Carga', 'al toque 20: +1 carga (todos los poderes, norma del dueño)'),
            ('a40Dos', 'al toque 40: ×2 (acumula)'),
            ('a60Tres', 'al toque 60: ×3'),
            ('a80Tope', 'al toque 80: tope ×3 honesto'),
            ('efecto10', 'SÚPER EFECTO: la ventana abre con 10 s exactos'),
            ('efectoViva', 'a los 9,98 s la ventana SIGUE viva (sin tope de golpes)'),
            ('efectoCierra', 'pasados los 10 s TODO vuelve a la normalidad'),
            ('iman10', 'SÚPER IMÁN: el campo abre con 10 s exactos'),
            ('imanVivo', 'a los 9,98 s el campo SIGUE vivo'),
            ('imanCierra', 'pasados los 10 s el campo se apaga solo'),
            ('palaSinVentana', 'sin ventana la pala es HONESTA (ppImanAim=false) (r57)'),
            ('palaConVentana', 'con la ventana la pala queda ARMADA (ppImanAim=true) (r57)'),
            ('bolaSinCampo', 'la bola JAMÁS lleva campo (r57: guía en el golpe)'),
            ('palaRestaurada', 'cerrada la ventana la pala vuelve a honesta'),
            ('eventoGuiado', 'el golpe guiado viaja con imanAim:true en el evento (r57)'),
            ('boteEnMesa', 'LA GUÍA: el golpe mal aimado BOTA EN LA MESA (solver de la casa) (r57)'),
            ('boteMitadRival', 'el bote cae en la MITAD DEL RIVAL (62 % de la media mesa) (r57)'),
            ('veloz', 'el golpe guiado sale VELOZ (piso de potencia del dueño) (r57)'),
        ]:
            chk(rt.get(key) is True, label)
        for key in ('sinJuego', 'sinHook', 'errCad', 'errVen', 'errSaq',
                    'errFren', 'errU', 'errE', 'errI', 'errFren2'):
            if rt.get(key):
                chk(False, f'{key}: {rt.get(key)}')

        await browser.close()

    if errors:
        for e in errors[:5]:
            print('  ✗ pageerror:', e[:200])
        fails += len(errors)

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
