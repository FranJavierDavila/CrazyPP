#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_efecto_rally_v3647 — CAPA AP · ronda 55 (V3.6.47-SDK6, FASE 49).

La petición del dueño (literal): «el potenciador de super efecto solo
debe estar activo en el tiempo que dura, SOLO debe aplicar el efecto
durante el intercambio de pelotas NUNCA sobre el saca ni mio ni del
rival, es decir es un efecto que solo se aplica a mis jugadas y siempre
en el bote sobre la mesa del rival, el resto de tiempo no aplica ningún
efecto y es todo juego normal.»

Pruebas: (1) FUENTE SERVIDA — agujas del GATE del eMul (pala honesta en
el vuelo del saque y fuera del rally, c05), de la VENTANA en la pala
(ps.intercambio = rules.state === 'rally', c12) y de la PUERTA DE MITAD
en el bote (boteRival = pos.z < C firma las tres reglas y el acople
×2,4, c05) + NEGATIVAS (la aplicación incondicional de la r54 NO puede
volver). (2) MECÁNICA REAL headless — física viva: MI SAQUE no marca
(serveFlight) aunque el poder esté armado, FUERA DEL RALLY no marca
(intercambio=false: ventana del rival, arkanoid, punto muerto), el
INTERCAMBIO marca y clasifica (control), los sims antiguos sin ventana
siguen marcando (compatibilidad AF/AO), y en el BOTE los tres tipos y
el acople ×2,4 SÓLO firman en la mitad del RIVAL — en la mitad PROPIA
el bote es física pura idéntica al gemelo sin firma (pares gemelos con
el mismo vuelo: el Magnus de la marca se cancela y sólo el bote
diferencia).

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
        # · LA PALA HONESTA (c05 — el gate del eMul, spec r55)
        ('const eMul = (pad.ppEfectoMul || 1) > 1 && !pad.serveFlight &&',
         'efecto: NUNCA en el vuelo del SAQUE propio (c05, r55)'),
        ('pad.intercambio !== false ? pad.ppEfectoMul : 1;',
         'efecto: SÓLO marca en el INTERCAMBIO — fuera, juego normal (c05, r55)'),
        # · LA VENTANA EN LA PALA (c12 — el estado del punto viaja a la pala)
        ("ps.intercambio = this.rules.state === 'rally';",
         'ventana: la pala del jugador conoce el estado del punto (c12, r55)'),
        # · LA PUERTA DE MITAD EN EL BOTE (c05 — «siempre en el bote sobre
        #   la mesa del rival»)
        ('const boteRival = pos.z < C;',
         'bote: puerta de mitad — SÓLO la mesa del RIVAL aplica (c05, r55)'),
        ("if (boteRival && ball.ppEfectoTipo === 'top') {",
         'bote: firma TOPSPIN sólo en la mitad del rival (c05, r55)'),
        ("} else if (boteRival && ball.ppEfectoTipo === 'back') {",
         'bote: firma BACKSPIN sólo en la mitad del rival (c05, r55)'),
        ("} else if (boteRival && ball.ppEfectoTipo === 'side') {",
         'bote: firma SIDESPIN sólo en la mitad del rival (c05, r55)'),
        # · v3.6.49 (r57): el acople ×2,4 RETIRADO — «la ventaja del efecto
        #   en los botes sólo es para el jugador, el perjudicado siempre es
        #   el rival»: la marca sin tipo bota FÍSICO PURO.
        ('bounceOnTable(vel, spin, impact);',
         'r57: bote físico puro (sin acople eM) — el call sin multiplicador'),
    ]:
        chk(needle in game, label)

    # · AGUJAS NEGATIVAS (la aplicación incondicional NO puede volver)
    chk("if (ball.ppEfectoTipo === 'top') {" not in game,
        'NEGATIVA: la firma TOPSPIN incondicional (sin puerta de mitad) no vuelve')
    chk('const eMul = pad.ppEfectoMul || 1;' not in game,
        'NEGATIVA: el eMul sin gate (marcaba en saques y fuera del rally) no vuelve')
    chk('const eM = (ball.ppEfecto && !ball.ppEfectoTipo)' not in game,
        'NEGATIVA: el acople ×2,4 incondicional (botaba en cualquier mitad) no vuelve')
    chk('const eM = (boteRival && ball.ppEfecto && !ball.ppEfectoTipo)' not in game,
        'NEGATIVA r57: el acople ×2,4 (aunque sea sólo en mitad rival) NO vuelve')
    chk('efectoBoteMul: 2.4' not in game,
        'NEGATIVA r57: la constante del acople no vuelve en los DIMS')

    # ---------- 2 · MECÁNICA REAL headless (física viva) ----------
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

          // ===== A · SAQUE y VENTANA (c05 REAL — la pala honesta) =====
          const CF = new V3(0, 1.0 + DIMS.bladeCenterUp, 1.5);
          const mkPad = (fl, ic) => {
            const pad = H.createPaddleSim('player', 0);
            pad.active = true;
            pad.pos.set(0, 1.0, 1.5); pad.prev.copy(pad.pos);
            pad.ppEfectoMul = 3;                   // Súper Efecto ARMADO
            if (fl !== undefined) pad.serveFlight = fl;
            if (ic !== undefined) pad.intercambio = ic;
            return pad;
          };
          const hit = (pv, fl, ic) => {
            const pad = mkPad(fl, ic);
            pad.vel.copy(pv);
            // la bola va DELANTE de la cara (lado +normal) entrando HACIA
            // ella — createPaddleSim nace con normal (0,0,1)
            const b = { pos: CF.clone().addScaledVector(pad.normal, 0.05),
              vel: pad.normal.clone().multiplyScalar(-2.2),
              spin: new V3(), dragMul: 1 };
            const evs = [];
            for (let i = 0; i < 6 && !evs.length; i++) {
              H.stepPhysics(1 / 60, b, [pad], evs);
              if (pad.cooldown > 0) break;             // golpeó
            }
            return { tipo: b.ppEfectoTipo || '', lado: b.ppEfectoLado || 0,
                     marco: b.ppEfecto === true,
                     golpe: evs.some((e) => e.type === 'paddle') };
          };
          // MI SAQUE (en vuelo de saque): el poder está armado y AUN ASÍ
          // el golpe es LIMPIO — sin marca, sin tipo (juego normal)
          const rSaca = hit(new V3(0, 2.5, 0), true, false);
          out.sacaLimpio = rSaca.golpe && !rSaca.marco && rSaca.tipo === '';
          // CONTROL (intercambio): mismo barrido → marcado y TOPSPIN
          const rCtrl = hit(new V3(0, 2.5, 0), false, true);
          out.ctrlMarca = rCtrl.golpe && rCtrl.marco && rCtrl.tipo === 'top';
          // FUERA DEL RALLY (ventana del rival / arkanoid / punto muerto):
          // sin marca aunque el poder esté armado
          const rFuera = hit(new V3(0, 2.5, 0), false, false);
          out.fueraLimpio = rFuera.golpe && !rFuera.marco && rFuera.tipo === '';
          // COMPATIBILIDAD: sims sin ventana (AF/AO) siguen marcando
          const rCompat = hit(new V3(0, 2.5, 0), undefined, undefined);
          out.compat = rCompat.golpe && rCompat.marco && rCompat.tipo === 'top';

          // ===== B · EL BOTE: mitad PROPIA vs mitad del RIVAL (c05 REAL) ==
          // Pares GEMELOS: mismo estado inicial (el Magnus de la marca se
          // cancela) — sólo la mitad del bote diferencia.
          const boteEn = (z, tipo, lado) => {
            const b = { pos: new V3(0.1, DIMS.tableTopY + 0.04, z),
              vel: new V3(0, -2.5, -3.0), spin: new V3(), dragMul: 1,
              ppEfecto: true, ppEfectoTipo: tipo, ppEfectoLado: lado || 0 };
            const evs = [];
            for (let i = 0; i < 60; i++) {
              H.stepPhysics(1 / 60, b, [], evs);
              if (evs.some((e) => e.type === 'table')) break;
            }
            return b;
          };
          const ZMIO = -1.0;    // mitad del JUGADOR (tableCenterZ −1,6)
          const ZRIV = -2.2;    // mitad del RIVAL
          // — TOPSPIN: en mi mitad bote FÍSICO PURO (≈ gemelo sin firma);
          //   en la del rival sale MUY acelerada (firma de la r54)
          const tMio = boteEn(ZMIO, 'top');
          const tBase = boteEn(ZMIO, '');
          out.topMioPuro = Math.abs(tMio.vel.z - tBase.vel.z) < 1e-6 &&
            Math.abs(tMio.vel.z) < 4.0;
          const tRiv = boteEn(ZRIV, 'top');
          out.topRivFirma = tRiv.vel.z < -4.2;
          // — BACKSPIN: en mi mitad sin aplastar; en la rival casi PARA
          const bMio = boteEn(ZMIO, 'back');
          out.backMioLibre = Math.abs(bMio.vel.z - tBase.vel.z) < 1e-6;
          const bRiv = boteEn(ZRIV, 'back');
          out.backRivParada = Math.abs(bRiv.vel.z) <= 0.6;
          // — SIDESPIN: en mi mitad sin patada; en la rival exagera AL LADO
          const sMio = boteEn(ZMIO, 'side', 1);
          out.sideMioSinPatada = Math.abs(sMio.vel.x) < 0.45;
          const sRiv = boteEn(ZRIV, 'side', 1);
          out.sideRivPatada = sRiv.vel.x >= 0.45;

          // ===== C · SIN ACOPLE (r57): la marcada SIN tipo bota FÍSICO
          // PURO — idéntica a la bola limpia en AMBAS mitades =====
          const botePuro = (z, marcada) => {
            // spin CERO: así el Magnus ×2,2 de la marca (vuelo) es nulo y la
            // única diferencia posible sería el acople del BOTE (retirado)
            const b = { pos: new V3(0.1, DIMS.tableTopY + 0.04, z),
              vel: new V3(0, -2.5, -3.0), spin: new V3(), dragMul: 1 };
            if (marcada) { b.ppEfecto = true; b.ppEfectoTipo = ''; b.ppEfectoLado = 0; }
            const evs = [];
            for (let i = 0; i < 60; i++) {
              H.stepPhysics(1 / 60, b, [], evs);
              if (evs.some((e) => e.type === 'table')) break;
            }
            return b;
          };
          const pMio = botePuro(ZMIO, false), pMioM = botePuro(ZMIO, true);
          const pRiv = botePuro(ZRIV, false), pRivM = botePuro(ZRIV, true);
          // la marca SIN tipo ya NO amplifica NADA (el ×2,4 antiguo metía
          // >1 m/s de diferencia; hoy el residuo del vuelo es < 2 cm/s)
          out.acopleMuertoRival =
            Math.abs(pRiv.vel.z - pRivM.vel.z) < 0.02 &&
            Math.abs(pRiv.vel.x - pRivM.vel.x) < 0.02;
          out.acopleMuertoMio =
            Math.abs(pMio.vel.z - pMioM.vel.z) < 0.02 &&
            Math.abs(pMio.vel.x - pMioM.vel.x) < 0.02;

          return out;
        }""")

        exp = {
            'sacaLimpio': 'MI SAQUE: poder armado y AUN ASÍ golpe limpio — sin marca ni tipo',
            'ctrlMarca': 'CONTROL (intercambio): el mismo barrido SÍ marca y clasifica TOPSPIN',
            'fueraLimpio': 'FUERA DEL RALLY (ventana rival/arkanoid/muerto): sin marca',
            'compat': 'COMPATIBILIDAD: sims sin ventana (AF/AO) siguen marcando',
            'topMioPuro': 'TOPSPIN en MI mitad: bote físico puro, idéntico al gemelo sin firma',
            'topRivFirma': 'TOPSPIN en la mesa del RIVAL: sale MUY acelerada (firma r54 viva)',
            'backMioLibre': 'BACKSPIN en MI mitad: bote normal, sin aplastar',
            'backRivParada': 'BACKSPIN en la mesa del RIVAL: prácticamente PARADA',
            'sideMioSinPatada': 'SIDESPIN en MI mitad: sin patada lateral',
            'sideRivPatada': 'SIDESPIN en la mesa del RIVAL: exagera AL LADO (patada viva)',
            'acopleMuertoRival': 'r57 SIN ACOPLE: marcada sin tipo = física pura en el RIVAL (Δ<2 cm/s)',
            'acopleMuertoMio': 'r57 SIN ACOPLE: ídem en MI mitad (Δ<2 cm/s)',
        }
        if rt.get('sinJuego'):
            chk(False, 'ventana __PP_GAME presente (¿arranque completo?)')
        elif rt.get('sinHook'):
            chk(False, 'hook __solverHook presente')
        else:
            for k, label in exp.items():
                chk(rt.get(k) is True, label)

        await browser.close()

    for e in errors[:5]:
        print('  ⚠ pageerror:', e)
    if errors:
        fails += len(errors)

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


asyncio.run(main())
