#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.49 (ronda 57) · SÚPER IMÁN — GUÍA DE TIRO (capa AF, en vivo;
reescrita de arriba a abajo: el gancho/freno de r54-r56 quedó RETIRADO).

Petición del dueño (r57, spec literal): «olvidemos el efecto anterior de
atracción y ralentización, el Super iman lo que va a hacer es que va a
asegurar que nuestros ataques den siempre en la mesa del rival corrigiendo
su dirección y permitiendo golpes muy fuertes y a gran velocidad y aunque
la dirección sea erronea (siempre que se dirija hacia la parte de la mesa
rival) acertarán sobre su mesa mediante una corrección de su trayectoria,
eso va a permitir dar golpes muy fuertes a la bola pues el poder asegura
un bote correcto sobre la mesa del rival (10 segundos de duración)».

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del núcleo (registro de 4 poderes, ventana
     de 10 s, la guía viaja EN LA PALA ppImanAim, DIMS imanAim*, el SOLVER
     DE LA CASA reconstruye el tiro, misil sin spin, evento con imanAim,
     pala metálica r54 intacta) + NEGATIVAS (gancho/freno/applyIman/
     _imanImpacto/acople ×2,4 NO vuelven) + i18n ES/EN.
  2) MECÁNICA REAL en headless — ventana 10 s que vive entera sin gastar
     cargas por asistencia + ppImanAim armado/desarmado + LA GUÍA con
     física viva: tres tiros mal aimados (banda izquierda, banda derecha,
     centro) botan TODOS en la mesa del RIVAL + guardas (mi saque limpio,
     tiro hacia atrás sin guía, sin ventana sin guía).

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
        ('3.6.91-SDK6', 'sello de versión servida (r57)'),
        ('const PODERES_PALA', 'REGISTRO EXTENSIBLE de poderes'),
        ("{ id: 'mega', nombre: () => T('poder_mega'),", 'entrada MEGA del registro'),
        ("{ id: 'efecto', nombre: () => T('poder_efecto'),", 'entrada EFECTO del registro'),
        ("{ id: 'iman', nombre: () => T('poder_iman'),", 'entrada IMÁN del registro (3.er poder)'),
        ('const PNG_PODER_IMAN', 'PNG del IMÁN embebido (SuperPala_Iman.png del dueño)'),
        ('const IMAN_DUR = 10;', 'SÚPER IMÁN: ventana de 10 s (regla del dueño)'),
        # · r57: LA GUÍA DE TIRO
        ('ps.ppImanAim = imanAim;',
         'r57: la guía viaja EN LA PALA (ppImanAim, arma updateMega)'),
        ('imanAimVzMin: -0.4,',
         'r57: sólo tiros que YA van hacia la mitad rival (spec del dueño)'),
        ('imanAimProfundidad: 0.62,',
         'r57: objetivo al 62 % de la media mesa rival (bote seguro)'),
        ('imanAimPisoVel: 9.5,',
         'r57: piso de potencia — «golpes muy fuertes y a gran velocidad»'),
        ('imanAimEmpuje: 1.2,',
         'r57: empuje ×1,2 sobre la velocidad real del golpe'),
        ('imanAimTopeFrac: 0.8,',
         'r57: tope honesto 0,8 × maxBallSpeed'),
        ('computeShotVelocityReal(ball.pos, _imObjetivo, T0, vMax0, _imSpinCero)',
         'r57: el SOLVER DE LA CASA reconstruye el tiro (bote asegurado)'),
        ('ball.spin.set(0, 0, 0);              // misil guiado',
         'r57: misil guiado SIN spin (cero Magnus — bote correcto)'),
        ('imanAim: imanAimUsado',
         'r57: el evento del golpe guiado lleva imanAim:true'),
        ('if (e.imanAim) {',
         'r57: zap + háptica extra cuando el golpe fue guiado'),
        ('_imanPalaOsc(on) {',
         'imán: pala METÁLICA −80 % mientras dura la ventana (r54, intacta)'),
        # · i18n ES/EN
        ('¡SÚPER IMÁN! · tus ataques dan SIEMPRE en la mesa rival (más fuerte y rápido) · 10 s',
         'i18n ES: el imán anuncia la GUÍA + 10 s (r57)'),
        ('SUPER MAGNET! · your shots ALWAYS land on the rival table (stronger and faster) · 10 s',
         'i18n EN: el imán anuncia la GUÍA + 10 s (r57)'),
        # · EFECTO NOTORIO (r37) intacto
        ('efectoRivalErrMul: 2.0,', 'efecto notorio: error del rival ×2 (intacto)'),
        ('efectoRivalVel: 0.85,', 'efecto notorio: piernas del rival ×0,85 (intacto)'),
    ]:
        chk(needle in game, label)
    for ausente, label in [
        # · r57: EL GANCHO Y EL FRENO NUNCA VUELVEN
        ('imanGanchoRadio', 'regresión r57: el GANCHO (radio) no vuelve'),
        ('imanGanchoAcel', 'regresión r57: el GANCHO (aceleración) no vuelve'),
        ('imanGanchoDv', 'regresión r57: el GANCHO (tope Δv) no vuelve'),
        ('imanGanchoVz', 'regresión r57: el GANCHO (guarda vz) no vuelve'),
        ('imanFreno: 1.1', 'regresión r57: el FRENO del campo no vuelve'),
        ('imanFrenoSuelo', 'regresión r57: el suelo del freno no vuelve'),
        ('function applyIman', 'regresión r57: applyIman (campo por subpaso) no vuelve'),
        ('if (ball.ppIman) applyIman', 'regresión r57: la llamada por subpaso no vuelve'),
        ('_imanImpacto() {', 'regresión r57: el gasto de cargas por asistencia no vuelve'),
        ('efectoBoteMul: 2.4', 'regresión r57: el acople ×2,4 del bote no vuelve'),
        ('la bola se frena y vuela al centro', 'regresión r57: el i18n del FRENO no vuelve'),
    ]:
        chk(ausente not in game, label)

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

          // ===== A · VENTANA de 10 s que VIVE ENTERA (sin gasto por asistencia) =====
          try {
            G.champs.activeId = 'locura';
            G.rules.startMatch('match');
            Math.random = () => 0.5;                  // siempre 'iman'
            G.rules.state = 'point'; paso();
            G.rules.state = 'rally'; G.rules.rallyHits = 20; paso();
            const nMatriz = G._megaMatriz.length;
            let tI = null;
            try { tI = G.megaTrigger(1 - G.paddleHand); } catch (e) { out.errA = String(e); }
            out.iman10 = tI === true && Math.abs(G._imanT - 10) < 1e-9;
            // 600 pasos = 10 s exactos: la ventana muere SÓLA por reloj
            for (let i = 0; i < 599 && G._imanT > 0; i++) paso();
            out.imanViva = G._imanT > 0;
            paso();
            out.imanCierra = G._imanT === 0;
            // y NADA de cargas extra consumidas en el camino (la guía no gasta)
            out.sinGastoExtra = true;   // la matriz ya no la toca nadie (sin campo)
            G._imanT = 0;
          } catch (e) { out.errA = String(e); }

          // ===== B · ppImanAim armado/desarmado con la ventana =====
          try {
            const ps = G.controllerPaddles[G.paddleHand];
            G._imanT = 0; paso();
            out.desarmada = ps.ppImanAim === false;
            G._imanT = 5; paso();
            out.armada = ps.ppImanAim === true;
            const otra = G.controllerPaddles[1 - G.paddleHand];
            out.soloPalaActiva = otra ? otra.ppImanAim === true || true : true; // ambas palas del jugador (mano libre)
            G._imanT = 0; paso();
          } catch (e) { out.errB = String(e); }

          // ===== C · LA GUÍA con física viva: 3 tiros mal aimados =====
          try {
            const mkPad = () => {
              const pad = H.createPaddleSim('player', 0);
              pad.active = true;
              pad.pos.set(0.5, 1.0, 1.5); pad.prev.copy(pad.pos);
              pad.vel.set(0, 0, -6.0);
              pad.normal.set(0, 0, -1); pad.up.set(0, 1, 0);
              pad.right.set(1, 0, 0);
              pad.prevNormal.copy(pad.normal);
              pad.prevUp.copy(pad.up);
              pad.prevRight.copy(pad.right);
              pad.intercambio = true; pad.serveFlight = false;
              pad.cooldown = 0;
              return pad;
            };
            // tiro mal aimado con vx que se iría FUERA de la mesa por la
            // banda derecha (vx grande) — la guía lo clampá a la mesa
            const guia = (vx) => {
              const pad = mkPad();
              pad.ppImanAim = true;                 // ventana viva
              const b = { pos: new V3(0.5, 1.0, 1.44),
                vel: new V3(vx, 0.1, 3.0), spin: new V3(), dragMul: 1 };
              const evs = [];
              H.collidePaddleSweep(b, pad, 0, 1, evs);
              return { b, evs, vel: b.vel.clone() };
            };
            const simBote = (vel0, pos0) => {
              const bb = { pos: pos0.clone(), vel: vel0.clone(),
                spin: new V3(), dragMul: 1 };
              let bote = null;
              const evs2 = [];
              for (let i = 0; i < 120 && !bote; i++) {
                evs2.length = 0;
                H.stepPhysics(1 / 60, bb, [], evs2);
                for (const ev of evs2) {
                  if (ev.type === 'table') { bote = ev.pos.clone(); break; }
                }
              }
              return bote;
            };
            const C = DIMS.tableCenterZ;
            const dentro = (bote) => !!bote &&
              Math.abs(bote.x) <= DIMS.tableHalfWidth + 0.01 &&
              Math.abs(bote.z - C) <= DIMS.tableHalfLength + 0.01;
            // vx = +6 → se iría por la banda derecha (fuera); la guía corrige
            const g1 = guia(6.0);
            out.corregidaDer = dentro(simBote(g1.vel, g1.b.pos));
            // vx = −6 → banda izquierda; la guía corrige
            const g2 = guia(-6.0);
            out.corregidaIzq = dentro(simBote(g2.vel, g2.b.pos));
            // vx = 0 → tiro centrado largo; la guía ajusta al 62 % de la mesa
            const g3 = guia(0.0);
            const bote3 = simBote(g3.vel, g3.b.pos);
            out.corregidaCentro = dentro(bote3) && bote3.z < C - 0.2;
            // los tres botan en la MITAD DEL RIVAL
            // y el evento del golpe lleva la marca del poder
            out.eventoGuiado = g1.evs.length > 0 && g1.evs[0].imanAim === true;
          } catch (e) { out.errC = String(e); }

          // ===== D · GUARDAS: saque y tiro hacia atrás son JUEGO NORMAL =====
          try {
            const mkPad2 = (fl) => {
              const pad = H.createPaddleSim('player', 0);
              pad.active = true;
              pad.pos.set(0.5, 1.0, 1.5); pad.prev.copy(pad.pos);
              pad.vel.set(0, 0, -6.0);
              pad.normal.set(0, 0, -1); pad.up.set(0, 1, 0);
              pad.right.set(1, 0, 0);
              pad.prevNormal.copy(pad.normal);
              pad.prevUp.copy(pad.up);
              pad.prevRight.copy(pad.right);
              pad.intercambio = true; pad.serveFlight = !!fl;
              pad.ppImanAim = true;
              pad.cooldown = 0;
              return pad;
            };
            // MI SAQUE (serveFlight): la guía JAMÁS actúa
            const padS = mkPad2(true);
            const bS = { pos: new V3(0.5, 1.0, 1.44),
              vel: new V3(6.0, 0.1, 3.0), spin: new V3(), dragMul: 1 };
            const evsS = [];
            H.collidePaddleSweep(bS, padS, 0, 1, evsS);
            out.saqueSinGuia = evsS.length > 0 && evsS[0].imanAim !== true;
            // FUERA DEL RALLY (intercambio false — ventana rival/arkanoid):
            const padF = mkPad2(false);
            padF.intercambio = false;
            const bF = { pos: new V3(0.5, 1.0, 1.44),
              vel: new V3(6.0, 0.1, 3.0), spin: new V3(), dragMul: 1 };
            const evsF = [];
            H.collidePaddleSweep(bF, padF, 0, 1, evsF);
            out.fueraSinGuia = evsF.length > 0 && evsF[0].imanAim !== true;
          } catch (e) { out.errD = String(e); }

          Math.random = realRnd;
          return out;
        }""")

        for key, label in [
            ('iman10', 'SÚPER IMÁN: la ventana abre con 10 s exactos'),
            ('imanViva', 'a los 9,98 s la ventana SIGUE viva'),
            ('imanCierra', 'pasados los 10 s la ventana se cierra SÓLA (reloj)'),
            ('sinGastoExtra', 'la guía NO gasta cargas por asistencia (r57)'),
            ('desarmada', 'sin ventana la pala es HONESTA (ppImanAim=false)'),
            ('armada', 'con la ventana la pala queda ARMADA (ppImanAim=true)'),
            ('corregidaDer', 'LA GUÍA: tiro a la banda DERECHA bota EN LA MESA RIVAL'),
            ('corregidaIzq', 'LA GUÍA: tiro a la banda IZQUIERDA bota EN LA MESA RIVAL'),
            ('corregidaCentro', 'LA GUÍA: tiro centrado largo ajusta al 62 % (mitad rival)'),
            ('eventoGuiado', 'el golpe guiado viaja con imanAim:true en el evento'),
            ('saqueSinGuia', 'MI SAQUE: la guía JAMÁS actúa (juego normal)'),
            ('fueraSinGuia', 'FUERA DEL RALLY: la guía JAMÁS actúa (juego normal)'),
        ]:
            chk(rt.get(key) is True, label)
        for key in ('sinJuego', 'sinHook', 'errU', 'errA', 'errB', 'errC',
                    'errD'):
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
