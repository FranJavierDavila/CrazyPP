#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_spin_pala_v3646 — CAPA AO · ronda 54 (V3.6.46-SDK6, FASE 48).

La petición del dueño (literal): «El super poder de pala de efecto la
estela está desfasada y como no consigo ver el efecto vamos a
establecerlo, en función del efecto que se le de con nuestra pala al
llegar a la mes del rival y botar hará un giro exagerado… Topspin: al
botar la pelota sale muy acelerada hacia delante del bote. Backspin: la
pelota prácticamente se queda parada con muy poca velocidad. Sidespin:
dependiendo del lado exagera el bote en la dirección del efecto… en
cualquiera de ellos penalizamos en un % al rival. Para el efecto de
Super Iman, cuando lo activamos la bola se redirige automáticamente al
centro de nuestra pala en su movimiento como atraída por la pala para
que podamos dar un buen golpe (ojo siempre que venga en nuestra
dirección de golpeo). Visualmente quitamos las flechas anteriores y
dejamos un diseño limpio de pala solo que la pala se oscurece como un
80% de su valor mientras dura el efecto (simula que es metálica) como
un imán.» + «revisar que el rival nunca meta la raqueta o alguna de sus
partes palo o mango en contacto con la mesa».

Pruebas: (1) FUENTE SERVIDA — agujas de la clasificación del spin
(c05), del BOTE TIPIFICADO (c05/c02), del GANCHO al centro (c05/c02),
de la PALA METÁLICA (c12), del tinte por tipo (halo + anillo), de la
limpieza de marca (c06) y del CLAMP del mango (c12) + NEGATIVAS
(estela/flechas/campo NO pueden volver). (2) MECÁNICA REAL headless —
física viva: clasificación por barrido (top/back/side/ninguno), los
tres botes con su firma exacta, convergencia del gancho (con negativas:
bola que se va, bola fuera de radio), oscurecido −80 % con aislamiento
de materiales (la pala del rival NO se oscurece) y restauración exacta,
clamp del mango sobre la mesa (y negativa: pala alta sin clamp).

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
        # · CLASIFICACIÓN del spin por el movimiento REAL de la pala (c05)
        ("ball.ppEfectoTipo = pvy > 0 ? 'top' : 'back';",
         'spin: barrido arriba→TOPSPIN · abajo→BACKSPIN (c05, r54)'),
        ("ball.ppEfectoTipo = 'side';",
         'spin: barrido lateral→SIDESPIN con lado del barrido (c05, r54)'),
        ('const pvx = pad.vel.x, pvy = pad.vel.y;',
         'spin: clasifica con la VELOCIDAD REAL de la pala (c05)'),
        ('efectoTipoUmbral: 0.55,',
         'spin: umbral de barrido 0,55 m/s para clasificar (c02)'),
        # · BOTE TIPIFICADO (c05 + c02 — la firma exacta del dueño)
        ('if (ball.ppEfectoTipo === \'top\') {',
         'bote: regla TOPSPIN presente (c05)'),
        ('} else if (ball.ppEfectoTipo === \'back\') {',
         'bote: regla BACKSPIN presente (c05)'),
        ('} else if (ball.ppEfectoTipo === \'side\') {',
         'bote: regla SIDESPIN presente (c05)'),
        ('const eM = (ball.ppEfecto && !ball.ppEfectoTipo)',
         'bote: con tipo claro el bote es FÍSICO PURO (sin acople ×2,4)'),
        ('efectoBoteTopAvance: 1.55,', 'bote TOPSPIN: acelera ×1,55 (+piso 0,4)'),
        ('efectoBoteTopVy: 0.62,', 'bote TOPSPIN: sale BAJO (vy ×0,62)'),
        ('efectoBoteBackH: 0.16,', 'bote BACKSPIN: horizontal ×0,16 (casi para)'),
        ('efectoBoteBackVy: 0.32,', 'bote BACKSPIN: saltito mínimo (vy ×0,32)'),
        ('efectoBoteSideKick: 0.42,', 'bote SIDESPIN: patada lateral 0,42 × |vz|'),
        ('efectoBoteSideMax: 1.5,', 'bote SIDESPIN: tope de patada 1,5 m/s'),
        # · GANCHO del imán al CENTRO de la pala (c05 + c02)
        ('function applyIman(ball, paddles, h) {', 'imán: applyIman presente'),
        ('if (ball.vel.z <= (DIMS.imanGanchoVz || 0.2)) continue;',
         'imán: SOLO bolas que vienen en nuestra dirección de golpeo'),
        ('if (d > DIMS.imanGanchoRadio || d < 1e-4) continue;',
         'imán: captura dentro del radio del GANCHO (1,8 m)'),
        ('if (!pad.active || pad.serveFlight || pad.who !== \'player\') continue;',
         'imán: SOLO la pala del jugador (el rival nunca gana asistencia)'),
        ('imanGanchoAcel: 26,', 'imán: aceleración del gancho 26 m/s²'),
        ('imanGanchoDv: 3.2,', 'imán: tope de Δv del gancho 3,2 m/s'),
        # · PALA METÁLICA −80 % (c12) — sin flechas, sin campo, sin canto
        ('_imanPalaOsc(on) {', 'imán: _imanPalaOsc (pala metálica) presente'),
        ('m.color.setHex(m.userData._imanOscuroC);   // −80 % (hex sRGB exacto)',
         'imán: oscurecido EXACTO −80 % del color base (hex sRGB)'),
        ('m.userData._imanPropio = true;',
         'imán: materiales AISLADOS (rival/demo no comparten el oscurecido)'),
        ('try { this._imanPalaOsc(!!(on && this._imanT > 0)); } catch (eOsc) { /* */ }',
         'imán: updateMega gobierna el oscurecido con la ventana'),
        # · TINTE POR TIPO (halo de la bola + anillo del bote)
        ("tpH === 'top' ? 0xff8c2a :", 'halo: TOPSPIN se tiñe NARANJA'),
        ("tpH === 'back' ? 0x3fd0ff :", 'halo: BACKSPIN se tiñe CIAN'),
        ("tpH === 'side' ? 0x8dff5a : 0xff5240);",
         'halo: SIDESPIN VERDE · sin tipo ROJO de siempre'),
        ("tipo === 'top' ? 0xff8c2a :",
         'anillo de bote: tinte por tipo (misma familia del halo)'),
        # · CLAMP del mango (el rival NUNCA atraviesa la mesa)
        ('const hHalf = 0.05;',
         'clamp: media LONGITUD del mango bajo el ancla (fix del palo en mesa)'),
        ('Math.min(low, gripY - hHalf * Math.max(0, pcA.y) - handleDown);',
         'clamp: el punto bajo incluye la punta del mango (pala IA)'),
        ('const overTable = inSlabXZ(pcC.x, pcC.z) || inSlabXZ(gripX, gripZ);',
         'clamp: la puerta de la mesa incluye TAMBIÉN al agarre'),
        # · LIMPIEZA de la marca (c06: la IA al devolver borra el tipo)
        ("ball.ppEfectoTipo = '';  // v3.6.46: fuera también el tipo de spin",
         'marca: la IA limpia tipo y lado al devolver (c06 ×2)'),
    ]:
        chk(needle in game, label)

    # · AGUJAS NEGATIVAS (lo retirado NO puede volver)
    chk('_imanFlechasUpdate() {' not in game,
        'NEGATIVA: _imanFlechasUpdate RETIRADO (sin flechas)')
    chk('_buildImanCampo() {' not in game,
        'NEGATIVA: _buildImanCampo RETIRADO (sin disco de campo)')
    chk('_buildEfectoTrail() {' not in game,
        'NEGATIVA: _buildEfectoTrail RETIRADO (sin estela desfasada)')
    chk('new THREE.ConeGeometry(0.024, 0.08, 10)' not in game,
        'NEGATIVA: los conos de las flechas ya no se construyen')
    chk('UT.puntos.push(this.ball.pos.clone());' not in game,
        'NEGATIVA: la estela ya no se alimenta de la bola')

    # ---------- 2 · MECÁNICA REAL headless (física viva + visuales) ----------
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

          // ============ A · CLASIFICACIÓN del SPIN (c05 REAL) ============
          const mkPad = () => {
            const pad = H.createPaddleSim('player', 0);
            pad.active = true;
            pad.pos.set(0, 1.0, 1.5); pad.prev.copy(pad.pos);
            pad.ppEfectoMul = 3;                       // Súper Efecto ACTIVO
            return pad;
          };
          const C = new V3(0, 1.0 + DIMS.bladeCenterUp, 1.5);
          const hit = (pv) => {
            const pad = mkPad();
            pad.vel.copy(pv);
            // la bola va DELANTE de la cara (lado +normal) entrando HACIA
            // ella (vel −normal): createPaddleSim nace con normal (0,0,1)
            const b = { pos: C.clone().addScaledVector(pad.normal, 0.05),
              vel: pad.normal.clone().multiplyScalar(-2.2),
              spin: new V3(), dragMul: 1 };
            const evs = [];
            for (let i = 0; i < 6 && !evs.length; i++) {
              H.stepPhysics(1 / 60, b, [pad], evs);
              if (pad.cooldown > 0) break;             // golpeó
            }
            return { tipo: b.ppEfectoTipo || '', lado: b.ppEfectoLado || 0,
                     marco: b.ppEfecto === true, golpe: evs.some((e) => e.type === 'paddle') };
          };
          const rTop = hit(new V3(0, 2.5, 0));
          out.clsTop = rTop.golpe && rTop.tipo === 'top' && rTop.marco;
          const rBack = hit(new V3(0, -2.5, 0));
          out.clsBack = rBack.golpe && rBack.tipo === 'back' && rBack.marco;
          const rSide = hit(new V3(2.0, 0, 0));
          out.clsSide = rSide.golpe && rSide.tipo === 'side' && rSide.lado === 1 && rSide.marco;
          const rNeu = hit(new V3(0, 0, 0));
          out.clsNeutro = rNeu.golpe && rNeu.tipo === '' && rNeu.marco;   // sin barrido: marca sin tipo

          // ============ B · BOTE TIPIFICADO (c05 REAL) ============
          const bote = (tipo, lado, vx) => {
            const b = { pos: new V3(0.1, DIMS.tableTopY + 0.04, -0.9),
              vel: new V3(vx, -2.5, -3.0), spin: new V3(), dragMul: 1,
              ppEfecto: true, ppEfectoTipo: tipo,
              ppEfectoLado: lado || 0 };
            const evs = [];
            let vzPre = null;
            for (let i = 0; i < 60; i++) {
              vzPre = b.vel.z;
              H.stepPhysics(1 / 60, b, [], evs);
              if (evs.some((e) => e.type === 'table')) break;
            }
            return { hubo: evs.some((e) => e.type === 'table'), vzPre,
                     vz: b.vel.z, vx: b.vel.x, vy: b.vel.y };
            };
          const tTop = bote('top', 0, 0);
          out.boteTop = tTop.hubo && tTop.vz < -4.2 &&
            tTop.vz < tTop.vzPre * 1.3;                // sale MUY acelerada
          const tBack = bote('back', 0, 0.4);
          out.boteBack = tBack.hubo && Math.abs(tBack.vz) <= 0.6 &&
            Math.abs(tBack.vx) <= 0.25;                // prácticamente PARADA
          const tSide = bote('side', 1, 0);
          out.boteSide = tSide.hubo && tSide.vx >= 0.45; // exagera AL LADO
          const tSin = bote('', 0, 0.4);
          out.boteSinTipo = tSin.hubo && Math.abs(tSin.vx) < 0.45;  // sin tipo: sin patada

          // ============ C · GANCHO al CENTRO (c05 REAL) ============
          const pad2 = H.createPaddleSim('player', 0);
          pad2.active = true;
          pad2.pos.set(0, 1.0, 1.5); pad2.prev.copy(pad2.pos);
          // base de pala REAL del jugador: la cara mira a la RED (−z) —
          // el sim por defecto nace mirando +z y el plano de la cara
          // mandaría a la bola al lado equivocado
          pad2.normal.set(0, 0, -1); pad2.prevNormal.set(0, 0, -1);
          pad2.up.set(0, 1, 0); pad2.prevUp.set(0, 1, 0);
          pad2.right.set(-1, 0, 0); pad2.prevRight.set(-1, 0, 0);
          const C2 = new V3(0, 1.0 + DIMS.bladeCenterUp, 1.5);
          const bG = { pos: new V3(0.7, 1.05, 0.9), vel: new V3(0, 0, 2.0),
            spin: new V3(), dragMul: 1, ppIman: { dv: 0 } };
          const d0 = bG.pos.distanceTo(C2);
          // 8 subllamadas (0,133 s): la bola SIGUE en el lado de la red —
          // el gancho ya debe estar tirando de ella hacia el centro
          for (let i = 0; i < 8; i++) H.stepPhysics(1 / 60, bG, [pad2], []);
          const d1 = bG.pos.distanceTo(C2);
          out.ganchoCerca = d1 < d0 * 0.8 && bG.vel.x < -0.3 &&
            bG.ppImanTocada === true;
          out.ganchoTope = bG.ppIman.dv <= DIMS.imanGanchoDv + 0.001;
          // negativa 1: bola que se ALEJA (no viene en nuestra dirección)
          const bF = { pos: C2.clone().add(new V3(0.3, 0, -0.4)),
            vel: new V3(0, 0, -2.5), spin: new V3(), dragMul: 1,
            ppIman: { dv: 0 } };
          for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, bF, [pad2], []);
          out.ganchoFueraDir = bF.vel.x === 0 && !bF.ppImanTocada;
          // negativa 2: bola FUERA del radio del gancho
          const bL = { pos: new V3(2.6, 1.05, 0.9), vel: new V3(0, 0, 2.0),
            spin: new V3(), dragMul: 1, ppIman: { dv: 0 } };
          for (let i = 0; i < 10; i++) H.stepPhysics(1 / 60, bL, [pad2], []);
          out.ganchoFueraRadio = !bL.ppImanTocada;

          // ============ D · PALA METÁLICA −80 % (c12 REAL) ============
          const mount = G.paddleMounts && G.paddleMounts[G.paddleHand];
          if (!mount) { out.sinMontura = true; return out; }
          // recolector FRESCO en cada estado: al oscurecer, los meshes
          // llevan MATERIALES CLONADOS (el aislamiento real)
          const collect = () => {
            const list = [];
            mount.traverse((o) => {
              if (o.isMesh && o.material) {
                const arr = Array.isArray(o.material) ? o.material : [o.material];
                for (const m of arr) if (m && m.color) list.push(m);
              }
            });
            return list;
          };
          const hex20 = (h) => (((Math.round(((h >> 16) & 255) * 0.2) & 255) << 16) |
            ((Math.round(((h >> 8) & 255) * 0.2) & 255) << 8) |
            (Math.round((h & 255) * 0.2) & 255)) >>> 0;
          const base = collect().map((m) => m.color.getHex());
          G._imanPalaOsc(true);
          const oscuros = collect();
          out.oscAplicado = G._imanOscApplied === true && oscuros.length > 0;
          out.oscOchenta = base.length > 0 && oscuros.length === base.length &&
            oscuros.every((m, i) => m.color.getHex() === hex20(base[i]));
          const antes2 = oscuros.map((m) => m.color.getHex());
          G._imanPalaOsc(true);                        // idempotente
          const oscuros2 = collect();
          out.oscIdempotente = oscuros2.length === oscuros.length &&
            oscuros2.every((m, i) => m.color.getHex() === antes2[i]);
          // AISLAMIENTO: la pala del RIVAL (mismo GLB) conserva SUS propios
          // materiales originales — ni _imanPropio ni color tocado
          let rivalOk = true;
          if (G.aiPaddleMesh) {
            G.aiPaddleMesh.traverse((o) => {
              if (o.isMesh && o.material && !Array.isArray(o.material)) {
                if (o.material.userData._imanPropio) rivalOk = false;
              }
            });
          }
          out.oscAislado = rivalOk;
          G._imanPalaOsc(false);
          const restaurados = collect();
          out.oscRestaura = G._imanOscApplied === false &&
            restaurados.length === base.length &&
            restaurados.every((m, i) => m.color.getHex() === base[i]);

          // ============ E · CLAMP del MANGO (c12 REAL) ============
          const qI = new T3.Quaternion();
          // caso 1: hoja sobre la mesa con el eje VERTICAL (el mango cuelga
          // hacia abajo — el caso del informe del dueño)
          const p1 = new V3(0.3, DIMS.tableTopY + 0.10, -0.9);
          const p1a = p1.y;
          G.clampPaddlePose(p1, qI, false);
          out.clampMango = p1.y > p1a + 0.07 &&
            (p1.y - DIMS.bladeRadius * 0 - 0.1303 - 0.05) >= DIMS.tableTopY + 0.002;
          // caso 2: pala ALTA sobre la mesa → sin clamp (libre)
          const p2 = new V3(0.3, 1.35, -0.9);
          G.clampPaddlePose(p2, qI, false);
          out.clampLibre = Math.abs(p2.y - 1.35) < 1e-6;
          // caso 3: mano BAJO la mesa (solo la hoja asoma) → resuelve sin saltos
          const p3 = new V3(0.3, DIMS.tableTopY - 0.16, -0.9);
          G.clampPaddlePose(p3, qI, false);
          out.clampBajo = Number.isFinite(p3.y) && Math.abs(p3.y - (DIMS.tableTopY - 0.16)) < 0.2;
          return out;
        }""")

        exp = {
            'clsTop': 'spin: barrido HACIA ARRIBA clasifica TOPSPIN',
            'clsBack': 'spin: barrido HACIA ABAJO clasifica BACKSPIN',
            'clsSide': 'spin: barrido LATERAL clasifica SIDESPIN (lado +1)',
            'clsNeutro': 'spin: golpe RECTO sin barrido → marca SIN tipo',
            'boteTop': 'bote TOPSPIN: sale MUY acelerada hacia delante (física viva)',
            'boteBack': 'bote BACKSPIN: prácticamente se QUEDA PARADA (física viva)',
            'boteSide': 'bote SIDESPIN: exagera el bote HACIA EL LADO (física viva)',
            'boteSinTipo': 'bote SIN tipo: sin patada lateral (comportamiento de siempre)',
            'ganchoCerca': 'gancho: tira de la bola HACIA el centro (se acerca y curva, física viva)',
            'ganchoTope': 'gancho: el Δv acumulado respeta el tope 3,2 m/s',
            'ganchoFueraDir': 'gancho NEGATIVO: bola que NO viene hacia nosotros — sin empuje',
            'ganchoFueraRadio': 'gancho NEGATIVO: bola fuera del radio — sin empuje',
            'oscAplicado': 'pala metálica: el oscurecido se aplica (marca de estado)',
            'oscOchenta': 'pala metálica: color EXACTO base × 0,2 (−80 %) en todos los materiales',
            'oscIdempotente': 'pala metálica: doble llamada NO vuelve a oscurecer',
            'oscAislado': 'pala metálica: la pala del RIVAL conserva sus materiales propios',
            'oscRestaura': 'pala metálica: al apagar restaura el color EXACTO',
            'clampMango': 'clamp: el MANGO ya no entra en la mesa (la pala se levanta entera)',
            'clampLibre': 'clamp NEGATIVO: pala ALTA sobre la mesa — sin clamp',
            'clampBajo': 'clamp: mano bajo la mesa se mueve LIBRE (sin saltos)',
        }
        for k, label in exp.items():
            chk(rt.get(k) is True, label)
        for k in ('sinJuego', 'sinHook', 'sinCore', 'sinCtrl', 'sinMontura'):
            if rt.get(k):
                chk(False, f'arnés: {k} — el juego no llegó a montarse')

    for e in errors[:4]:
        print('  · pageerror:', e[:140])
    chk(len(errors) == 0, f'sin pageerrors ({len(errors)})')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    asyncio.run(main())
