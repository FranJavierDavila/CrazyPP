#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_poderes_10s20_v3648 — CAPA AQ · ronda 56 (V3.6.48-SDK6, FASE 50).

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
campo, FRENO del gancho en c02/c05) + NEGATIVAS (los topes de golpes de
la r36-37 NO vuelven: EFECTO_GOLPES, IMAN_ASIST, el cierre por golpes) +
i18n ES/EN honesto + plantilla 2.4 con la norma de 20 toques. (2)
MECÁNICA REAL headless — cadencia EXACTA (19 toques NADA · 20 → +1 · 40
→ ×2 · 60 → ×3 · 80 → tope), ventanas de 10 s PURAMENTE TEMPORALES (el
efecto y el imán viven sus 10 s completos y cierran solos), el campo del
imán NUNCA arma sobre la bola del SAQUE del rival (isServeBall) y el
FRENO de la física viva: la bola asistida llega MÁS DESPACIO al dulce
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
        # · «MENOS EN LOS SAQUES»: el campo no arma sobre la bola del
        #   saque del rival (isServeBall vive hasta el primer toque)
        ("r.state === 'rally' && !r.isServeBall",
         'r56: el imán NUNCA arma sobre la bola del SAQUE del rival'),
        # · «QUE RALENTICE LA BOLA»: el FRENO del gancho (c02 + c05)
        ('imanFreno: 1.1,',
         'r56: FRENO exponencial del campo (1/s) en los DIMS'),
        ('imanFrenoSuelo: 0.15,',
         'r56: suelo de velocidad del freno (0,15 m/s) — el vuelo no muere'),
        ('Math.max(DIMS.imanFrenoSuelo / sp0,',
         'r56: el gancho FRENE dentro de sus guardas y sin gastar el tope Δv'),
        # · i18n ES/EN honesto
        ('cada 20 toques de rally te da una', 'i18n ES: la norma de 20 toques'),
        ('cada 20 toques del rally = +1 carga', 'i18n ES: la pista de la norma'),
        ('every 20 rally shots grants one', 'i18n EN: la norma de 20 shots'),
        ('every 20 rally shots = +1 charge', 'i18n EN: la pista de la norma'),
        ('¡SÚPER IMÁN! · la bola se frena y vuela al centro de la pala · 10 s',
         'i18n ES: el imán anuncia FRENO + 10 s'),
        ('SUPER MAGNET! · the ball slows down and flies to the paddle centre · 10 s',
         'i18n EN: el imán anuncia FRENO + 10 s'),
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

          // ===== C · SAQUE DEL RIVAL: el campo NO arma (r56) =====
          try {
            G._imanT = 5;                             // ventana abierta (sintética)
            G.rules.state = 'rally';
            G.rules.isServeBall = true;               // bola del SAQUE rival
            if (G.ball && G.ball.ppIman) delete G.ball.ppIman;
            paso();
            out.saqueRivalLimpio = !G.ball || !G.ball.ppIman;
            G.rules.isServeBall = false;              // primer toque: rally vivo
            paso();
            out.rallyArma = !!(G.ball && G.ball.ppIman);
            G._imanT = 0;
            if (G.ball && G.ball.ppIman) delete G.ball.ppIman;
          } catch (e) { out.errSaq = String(e); }

          // ===== D · EL FRENO (física viva — «que ralentice la bola») ====
          try {
            const mkPad = (x) => {
              const pad = H.createPaddleSim('player', 0);
              pad.active = true;
              pad.pos.set(x, 1.0, 1.5); pad.prev.copy(pad.pos);
              return pad;
            };
            // El FRENO en ISOLACIÓN: presupuesto del tirón AGOTADO
            // (ppIman.dv = tope) — así sólo actúa el freno exponencial.
            // Bola ALTA (y=2.0) y vuelo CORTO (10 frames): ni mesa ni
            // suelo ni CONTACTO con la pala estropean la medida. EN radio
            // (d≈1,5 m), viniendo (vz=2,6), delante del plano (normal
            // (0,0,-1) mira a la bola que llega).
            const vuela = (xPad, conIman, dv) => {
              const pad = mkPad(xPad);
              pad.normal.set(0, 0, -1);
              const b = { pos: new V3(0, 2.0, 0.35),
                vel: new V3(0, -0.4, 2.6), spin: new V3(), dragMul: 1 };
              if (conIman) b.ppIman = { dv: (dv === undefined) ? DIMS.imanGanchoDv : dv };
              const v0 = b.vel.length();
              for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, b, [pad], []);
              return { v0, v1: b.vel.length(), vz1: b.vel.z, p1: b.pos.clone(),
                       empuje: b.ppImanEmpuje === true,
                       tocada: b.ppImanTocada === true };
            };
            const ref = vuela(0, false);          // vuelo libre (sin poder)
            const fuera = vuela(3, true);         // con poder, FUERA del radio
            const con = vuela(0, true);           // con poder EN el radio (sólo freno)
            // el freno ataca la VELOCIDAD DE APROXIMACIÓN (z): la gravedad
            // contamina el módulo (la bola cae) — se compara la componente
            out.frena = con.vz1 < ref.vz1 * 0.9 && con.empuje && con.tocada;
            out.goldenIntacto = fuera.v1 === ref.v1 && !fuera.empuje;
            // y el TIRÓN vive: con presupuesto (dv=0), la bola acaba MÁS
            // CERCA del centro de la pala que el vuelo libre
            const tir = vuela(0, true, 0);
            const padC = mkPad(0);
            const C = padC.pos.clone().addScaledVector(padC.up, DIMS.bladeCenterUp);
            out.centra = tir.p1.distanceTo(C) < ref.p1.distanceTo(C);
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
            ('saqueRivalLimpio', 'la bola del SAQUE del rival NO recibe campo (r56)'),
            ('rallyArma', 'en el intercambio el campo vuelve a armar'),
            ('frena', 'EL FRENO: el campo frena la bola asistida (dv agotado, sólo freno) (r56)'),
            ('goldenIntacto', 'fuera del radio la física es BIT-EXACTA al vuelo libre (golden intacto)'),
            ('centra', 'EL TIRÓN: con presupuesto, la bola acaba más CERCA del centro de la pala (r54+r56)'),
        ]:
            chk(rt.get(key) is True, label)
        for key in ('sinJuego', 'sinHook', 'errCad', 'errVen', 'errSaq',
                    'errFren', 'errU', 'errE', 'errI'):
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
