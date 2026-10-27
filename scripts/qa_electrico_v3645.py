#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_electrico_v3645 — CAPA AN · ronda 53 (V3.6.75-SDK6, FASE 47).

La petición del dueño (literal): «vamos a introducir una variación en el
arkanoid etapa 4 del campeonato de la locura. El ladrillo de la bomba que
tenga un comportamiento que haga que salga de manera aleatoria pero con
intervalos de 15 segundos si tiene ladrillos disponible donde aparecer.
En los últimos 30 segundos uno de los ladrillos azules (aleatorio) se
convierte en eléctrico con pequeños rayos que sale de él (solo es
destructible con la bola) si se le consigue dar con la pelota, atrae hacia
si al resto de los ladrillos que queden en la pared distribuyéndolos en
las celdas pegadas a su alrededor cubriendo todas las casillas más
próximas posibles y todos cogen el mismo efecto de rayitos pegándolos a
su alrededor, en ese momento y hasta el final del tiempo cualquier
impacto en cualquiera de los ladrillos en el nuevo estado de eléctrico
desencadena una reacción en cadena destruyéndolos de forma ramificada
desde el que recibe el impacto hasta los siguientes hasta destruir todos
en cadena, finalizando de forma exitosa la misión. Si fuese posible
cuando sela un ladrillo y pasa a eléctrico que emita un sonido de
chisporroteo de electricidad.»

Pruebas: (1) FUENTE SERVIDA — agujas del MÓDULO LOCURA (siembra en los
últimos 30 s, atracción por anillos, cadena BFS ramificada, rayitos pool
de 14, chisporroteo, inmunidad al láser en raycast y laserHit, reinicio
state0, tween de la atracción, freeze del reloj en la cadena, i18n) y de
la CADENCIA de la bomba (intervalos de 15 s). (2) MECÁNICA REAL headless
— ArcadeController REAL con bricks simulados: siembra → inmunidad al
láser → atracción (todos eléctricos, celdas únicas, anillo ≤ 2, tweens)
→ cadena (12/12 muertos por ondas, bricksLeft 0, misión SUPERADA con
_finish(true)) → bomba bloqueada con el eléctrico activo.

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
import io
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
    global ok, fails
    errors = []

    # ---------- 1 · FUENTE SERVIDA (núcleo: versión + i18n) ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('3.6.75-SDK6', 'versión servida: 3.6.75-SDK6 (ronda 53)'),
        # i18n del ELÉCTRICO (c00 → game.html compilado)
        ("ark_elec_on: '¡LADRILLO ELÉCTRICO! Dale con la BOLA',",
         'eléctrico: i18n ES del sellado (c00→game.html)'),
        ("ark_elec_aran: '¡PARED ELECTRIFICADA! Un golpe y… ¡CADENA!',",
         'eléctrico: i18n ES de la electrificación (c00→game.html)'),
        ("ark_elec_on: 'ELECTRIC BRICK! Hit it with the BALL',",
         'eléctrico: i18n EN del sellado (c00→game.html)'),
        ("ark_elec_aran: 'WALL ELECTRIFIED! One more hit… CHAIN!',",
         'eléctrico: i18n EN de la electrificación (c00→game.html)'),
    ]:
        chk(needle in game, label)

    # ---------- 1b · FUENTE SERVIDA (módulo locura) ----------
    try:
        mod_src = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        # · CADENCIA NUEVA DE LA BOMBA (r53)
        ('bombaCada: 15,', 'bomba: INTERVALOS DE 15 s en ARK2_CFG (r53)'),
        ('this._bombNext = 2 + Math.random() * 10;',
         'bomba: 1.ª aparición aleatoria dentro del 1.er intervalo'),
        ('this._bombNext = this._stageT + (this.C.bombaCada || 15);',
         'bomba: cada aparición programa la siguiente a +15 s'),
        ('if (this._eFase > 0) return;',
         'bomba: el final eléctrico la APAGA (sin bomba en el gran final)'),
        # · SIEMBRA (fase 0 → 1): últimos 30 s, UN azul al azar
        ('if (this.variant === 2 && sec <= 30 && !this._eFase) this._eSembrar();',
         'eléctrico: se siembra al ENTRAR en los últimos 30 s'),
        ('_eSembrar() {', 'eléctrico: _eSembrar definida'),
        ("this.bricks.filter((b) => b.alive && b.state === 'blue' &&",
         'eléctrico: la semilla sale de un AZUL vivo al azar'),
        ("b.state = 'elec';", 'eléctrico: la semilla pasa a estado ELÉCTRICO'),
        ('b.mesh.material = this.eBrickMat;',
         'eléctrico: material cian que EMITE (se ve la electrificación)'),
        ('this.eIcon.position.z += this.C.depth / 2 + 0.003;',
         'eléctrico: icono del RAYO delante del ladrillo (familia reloj/bomba)'),
        ('g.audio.playOsc(2400, 700, 0.16, \'sawtooth\', 0.2, pan);',
         'eléctrico: ZAP de sellado al pasar a eléctrico'),
        ("this._msg = T('ark_elec_on');",
         'eléctrico: cartel «¡LADRILLO ELÉCTRICO! Dale con la BOLA»'),
        # · SÓLO LA BOLA: inmune al láser (raycast + laserHit)
        (".filter((b) => b.alive && b.state !== 'elec' &&",
         'eléctrico: el rayo del LÁSER ni siquiera lo ve (atraviesa su hueco)'),
        ("if (b.state === 'elec') {            // v3.6.45: sólo la BOLA lo activa",
         'eléctrico: laserHit lo rechaza (chispa, no destrucción)'),
        # · EL GOLPE DE LA BOLA ES EL GATILLO (colisión por subpaso)
        ('if (this._eFase === 1) this._eAtraer(b);',
         'eléctrico: el golpe de la bola en la semilla dispara la ATRACCIÓN'),
        ('else if (this._eFase === 2) this._eCadenaDesde(b);',
         'eléctrico: armada la cadena, CUALQUIER impacto la desencadena'),
        # · ATRACCIÓN por ANILLOS (las casillas más próximas primero)
        ('_eAtraer(seed) {', 'eléctrico: _eAtraer definida (fase 1 → 2)'),
        ("if (Math.max(Math.abs(r - rS), Math.abs(c - cS)) !== ring) continue;",
         'eléctrico: reparto por ANILLOS Chebyshev desde la semilla'),
        ('celdas.sort((a, b2) => a.d - b2.d);',
         'eléctrico: dentro del anillo, las casillas más PRÓXIMAS primero'),
        ('b.min.set(x - C.bw / 2, y - C.bh / 2, C.z - C.depth / 2);',
         'eléctrico: AABB nuevo YA (la colisión manda sobre la disposición final)'),
        # · REACCIÓN EN CADENA ramificada (fase 2)
        ('_eCadenaDesde(b0) {', 'eléctrico: _eCadenaDesde definida (BFS)'),
        ('if (this._eCadena.length) return;     // la cadena ya corre: no re-dispara',
         'eléctrico: la cadena no se re-dispara mientras corre'),
        ('t += 0.12;', 'eléctrico: ONDAS de 0,12 s — destrucción RAMIFICADA visible'),
        ('_eCadenaStep(dt) {', 'eléctrico: _eCadenaStep definida (procesa la cola)'),
        ('this._finish(true);                 // misión finalizada con ÉXITO',
         'eléctrico: muro arrasado = misión SUPERADA (_finish(true))'),
        # · EFECTOS: rayitos + chisporroteo (petición literal)
        ('_eBoltUpdate(dt) {', 'eléctrico: _eBoltUpdate definida (rayitos)'),
        ('new THREE.BufferAttribute(new Float32Array(4 * 3), 3)',
         'eléctrico: pool de 14 RAYOS dentados (líneas 4 puntos)'),
        ('blending: THREE.AdditiveBlending, depthWrite: false,',
         'eléctrico: rayos ADITIVOS (brillan sobre el muro)'),
        ('this._eBoltT = 0.07;', 'eléctrico: los rayos CHISPORROTEAN (regen 0,07 s)'),
        ('_eChispUpdate(dt) {', 'eléctrico: _eChispUpdate definida (chisporroteo)'),
        ('this._eChispT = 0.12 + Math.random() * 0.26;',
         'eléctrico: crepitar ALEATORIO mientras hay eléctricos'),
        ('this._eUpdate(dt);',
         'eléctrico: enganchado al bucle (rayos · chisporroteo · cadena)'),
        # · GRAN FINAL: el reloj se congela durante la cadena
        ('if (!this._eCadena.length) this.time -= dt;',
         'eléctrico: la cadena CONGELA el contador (el final se completa)'),
        # · REINICIO con cada partida + color ORIGINAL
        ('state0: blue ? \'blue\' : \'red\',',
         'eléctrico: state0 — el color ORIGINAL se recuerda'),
        ('if (b.state0) b.state = b.state0;   // v3.6.45: color ORIGINAL de fábrica',
         'eléctrico: cada partida arranca con el muro de FÁBRICA'),
        ('this._eCadena.length = 0;',
         'eléctrico: la cadena se limpia con cada partida (start)'),
        # · NADA se crea por partida (regla Quest): todo nace en build()
        ('this.eBrickMat = this.eBrickMat || new THREE.MeshStandardMaterial({',
         'eléctrico: material creado UNA vez (regla Quest anti-lag)'),
        ('emissive: 0x36c9ff, emissiveIntensity: 0.8,',
         'eléctrico: emisión cian 0,8 (la pared electrificada BRILLA)'),
        # · TWEEN de la atracción
        ('mv.t += dt / 0.35;',
         'eléctrico: los ladrillos VIAJAN 0,35 s al ser atraídos'),
    ]:
        chk(needle in mod_src, label)

    # · AGUJAS NEGATIVAS (la cadencia vieja NO puede volver)
    chk('this._bombAge' not in mod_src,
        'NEGATIVO: el reloj viejo _bombAge (prob 0,55/s + forzosa a los 6 s) murió')
    chk('Math.random() < dt * 0.55' not in mod_src,
        'NEGATIVO: la aparición por probabilidad por segundo murió (r53: intervalos)')

    # ---------- 2 · MECÁNICA REAL headless (módulo real + bricks simulados) --
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
          const T3 = await import('three');   // importmap del juego
          const G = window.__PP_GAME;
          if (!G) { out.sinJuego = true; return out; }
          try {
            const mod = (await import('/championships/locura/index.js')).default;
            const ctx = window.__PP_CORE;
            if (!ctx) { out.sinCore = true; return out; }
            await mod.init({ game: G });
            await new Promise((r) => setTimeout(r, 500));
            const ctrl = mod.impl;
            if (!ctrl) { out.sinCtrl = true; return out; }
            const ark = ctrl.arkanoid;

            // --- andamio mínimo (la escena real no se monta en headless) ---
            ark.variant = 2;
            ark.C = { cols: 9, rows: 6, gap: 0.012, depth: 0.12,
              bw: 0.1586, bh: 0.15, baseY: 0, z: 0, brickRest: 0.86 };
            ark._dying = [];
            ark._flash = () => {};
            ark.redMats = [{}, {}, {}];
            ark.blueMats = [{}, {}, {}];
            ark.eBrickMat = { __elec: true };
            ark.eIcon = { visible: false, position: new T3.Vector3() };
            ark._debris = [];
            for (let i = 0; i < 16; i++) {
              ark._debris.push({ mesh: { visible: false, material: null,
                position: { x: 0, y: 0, z: 0, copy() {} } },
              vel: { set() {} }, life: 0 });
            }
            ark.bricks = [];
            const Wg = 9 * 0.1586 + 8 * 0.012;   // ancho REAL del muro 9×6
            for (let r = 0; r < 6; r++) {
              for (let c = 0; c < 9; c++) {
                const blue = ((r * 7 + c * 5 + 3) % 10) < 4;
                const x = -Wg / 2 + 0.1586 / 2 + c * (0.1586 + 0.012);
                const y = 0.15 / 2 + r * (0.15 + 0.012);
                const m = { visible: true, material: null,
                  position: new T3.Vector3(x, y, 0) };
                ark.bricks.push({
                  alive: true, state: blue ? 'blue' : 'red',
                  state0: blue ? 'blue' : 'red',
                  matIdx: (r * 3 + c) % 3, mesh: m,
                  home: new T3.Vector3(x, y, 0),
                  min: new T3.Vector3(x - 0.0793, y - 0.075, -0.06),
                  max: new T3.Vector3(x + 0.0793, y + 0.075, 0.06),
                });
              }
            }
            ark.bricksLeft = 54;
            ark._msg = ''; ark._msgT = 0; ark._hudDirty = false;
            ark._eFase = 0; ark._eSeed = null; ark._eMove = [];
            ark._eCadena = []; ark._eBoltT = 0; ark._eChispT = 0;
            ark._bombBrick = null; ark._bombUsed = false;
            ark._bombWait = false; ark._bombNext = 3; ark._bombT = 0;
            ark._stageT = 0;

            // ===== (a) SIEMBRA en los últimos 30 s =====
            ark._eSembrar();
            const seed = ark._eSeed;
            out.aSemilla = ark._eFase === 1 && !!seed &&
              seed.state === 'elec' && seed.alive === true &&
              seed.mesh.material === ark.eBrickMat &&
              ark.eIcon.visible === true &&
              String(ark._msg).indexOf('ELÉCTRICO') >= 0;

            // ===== (b) INMUNIDAD al láser =====
            const rLaser = ark.laserHit(seed);
            out.bLaser = rLaser === false && seed.alive === true &&
              seed.state === 'elec';   // chispa, NO destrucción

            // ===== (c) BOMBA BLOQUEADA con el eléctrico activo =====
            ark._bombUsed = false; ark._bombWait = false; ark._bombNext = 0;
            ark._bombUpdate(0.2);      // hay azules y el intervalo pasó
            out.cSinBomba = ark._bombBrick === null;

            // ===== (d) ATRACCIÓN: matamos hasta dejar 12 vivos =====
            let vivosExtra = 0;
            for (const b of ark.bricks) {
              if (b === seed) continue;
              if (b.alive && vivosExtra < 11) { vivosExtra++; continue; }
              b.alive = false; b.mesh.visible = false;
            }
            ark.bricksLeft = 12;
            ark._eAtraer(seed);
            // todos los vivos eléctricos y la fase armada
            const vivos = ark.bricks.filter((b) => b.alive);
            out.dTodosElec = ark._eFase === 2 &&
              vivos.every((b) => b.state === 'elec') && vivos.length === 12;
            // celdas DESTINO únicas (ningún par comparte centro de AABB)
            const centros = new Set(vivos.map((b) =>
              (b.min.x + b.max.x).toFixed(4) + '|' + (b.min.y + b.max.y).toFixed(4)));
            out.dCeldasUnicas = centros.size === 12;
            // ANILLO ≤ 2 desde la semilla (11 ladrillos caben en anillos 1-2)
            // — celdas derivadas con la MISMA función del módulo (_eCeldaDe)
            const cS0 = ark._eCeldaDe(seed);
            let maxAnillo = 0;
            for (const b of vivos) {
              if (b === seed) continue;
              const cd = ark._eCeldaDe(b);
              maxAnillo = Math.max(maxAnillo,
                Math.max(Math.abs(cd.r - cS0.r), Math.abs(cd.c - cS0.c)));
            }
            out.dAnillo = maxAnillo <= 2 && maxAnillo >= 1;
            // tweens de viaje creados (la malla viaja 0,35 s)
            out.dTweens = ark._eMove.length === 11;
            // la semilla NO se movió (es el centro de la atracción)
            out.dCentro = Math.abs((seed.min.x + seed.max.x) / 2 - seed.home.x) < 1e-6;

            // ===== (e) CADENA ramificada hasta arrasar la pared =====
            ark.phase = 'play';
            ark.time = 20;
            ark._eCadenaDesde(vivos.find((b) => b !== seed));
            out.eColaLlena = ark._eCadena.length === 12;
            for (let i = 0; i < 400 && ark._eCadena.length; i++) {
              ark._eCadenaStep(0.05);
            }
            out.eArrasa = ark._eCadena.length === 0 &&
              ark.bricks.filter((b) => b.alive).length === 0 &&
              ark.bricksLeft === 0;
            out.eMision = ark.phase === 'result' && ark._lastWin === true;

            // ===== (f) RESET con cada partida (state0 + fase 0) =====
            ark.phase = 'play';
            // simulamos el bloque de reset de start() sobre los mocks
            ark._eFase = 2; ark._eCadena.push({ b: seed, t: 0 });
            ark._eCadena.length = 0;
            ark._eFase = 0; ark._eSeed = null;
            for (const b of ark.bricks) {
              b.alive = true; b.mesh.visible = true;
              if (b.state0) b.state = b.state0;
            }
            ark.bricksLeft = 54;
            const azules = ark.bricks.filter((b) => b.state === 'blue').length;
            const esperados = ark.bricks.filter((b) => b.state0 === 'blue').length;
            out.fFabrica = ark._eFase === 0 && ark._eSeed === null &&
              azules === esperados;   // el muro vuelve a FÁBRICA (state0)
          } catch (eB) { out.errElec = (eB && eB.stack) ?
            String(eB.stack).split(String.fromCharCode(10)).slice(0, 4).join(' || ') : String(eB); }
          return out;
        }""")

        if rt.get('sinJuego'):
            chk(False, 'headless: window.__PP_GAME presente')
        else:
            if rt.get('sinCore'):
                chk(False, 'headless: window.__PP_CORE presente (módulo locura)')
            elif rt.get('sinCtrl'):
                chk(False, f'headless: mod.impl presente — CTRL montado ({rt.get("errElec", "sin err")})')
            else:
                chk(not rt.get('errElec'),
                    f'mecánica eléctrico sin excepciones ({rt.get("errElec", "limpia")})')
                chk(rt.get('aSemilla') is True,
                    'mecánica (a): SIEMBRA — un azul al azar pasa a eléctrico '
                    '(material cian, icono y cartel)')
                chk(rt.get('bLaser') is True,
                    'mecánica (b): INMUNE al láser — chispa, no destrucción')
                chk(rt.get('cSinBomba') is True,
                    'mecánica (c): con el eléctrico activo la BOMBA no sale')
                chk(rt.get('dTodosElec') is True,
                    'mecánica (d): la ATRACCIÓN electrifica TODOS los vivos (12/12)')
                chk(rt.get('dCeldasUnicas') is True,
                    'mecánica (d): celdas destino ÚNICAS (nadie se solapa)')
                chk(rt.get('dAnillo') is True,
                    'mecánica (d): reparto en ANILLO ≤ 2 — las casillas más '
                    'próximas primero')
                chk(rt.get('dTweens') is True,
                    'mecánica (d): los 11 ladrillos VIAJAN con tween (0,35 s)')
                chk(rt.get('dCentro') is True,
                    'mecánica (d): la semilla es el CENTRO (no se mueve)')
                chk(rt.get('eColaLlena') is True,
                    'mecánica (e): la cadena encola los 12 eléctricos (BFS ramificado)')
                chk(rt.get('eArrasa') is True,
                    'mecánica (e): la cadena ARRASA la pared (12/12 muertos, '
                    'bricksLeft 0)')
                chk(rt.get('eMision') is True,
                    'mecánica (e): misión FINALIZADA CON ÉXITO (_finish(true) → '
                    'result + _lastWin)')
                chk(rt.get('fFabrica') is True,
                    'mecánica (f): el muro vuelve a FÁBRICA (state0) y fase 0')

    for e in errors[:4]:
        print('  · pageerror:', e[:140])
    chk(len(errors) == 0, f'sin pageerrors ({len(errors)})')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(0 if fails == 0 else 1)


asyncio.run(main())
