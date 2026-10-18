#!/usr/bin/env python3
"""QA del JUEGO · V3.4.0-IMP1 (Reactor de impulso, nueva etapa 4).
Verde = todas las comprobaciones en OK. Uso: python3 scripts/qa_impulso_v340.py"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

BASE = 'http://localhost:3000'
GW = 'http://localhost:81'
ok = fails = 0

def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1

ORBITAL = 'championships/estacion_orbital'
RI = ORBITAL + '/assets/reactor_impulso'
ASSETS = [
    f'{RI}/frente.jpg', f'{RI}/fondo.jpg', f'{RI}/techo.jpg', f'{RI}/suelo.jpg',
    f'{RI}/izquierda.png', f'{RI}/derecha.png', f'{RI}/diana_quantica.png',
    f'{RI}/base.png', f'{RI}/pantallainfo.png',
    f'{ORBITAL}/assets/pistol.glb', f'{ORBITAL}/assets/nucleo_gravedad_lp.glb',
    f'{ORBITAL}/assets/mapa.png',
]
TOKENS = [
    'class ReactorImpulso', 'const IMP_CFG', "id: 'impulso'",
    '_empezarImpulso', '_arrancarImpulso', '_oleadaArranca', '_oleadaCompleta',
    '_pertAplica', '_pertAleatoria', '_cubosCollide', '_cadenaDestruye',
    '_fragmenta', '_dianasStep', '_dianaHit', 'laserTargets',
    'reactor_impulso/', 'base.png', 'pantallainfo.png',
    'diana_quantica.png', 'GRAVEDAD 0', 'ATRACTOR', 'SUPERGRAVEDAD',
    'CTRL.impulso.reenter', 'get gunArmed() { return !!(CTRL && CTRL.gunArmed); }',
    "fireGun(i) { if (CTRL) { try { CTRL.fireGun(i);",
    "if (et.id === 'impulso') { this._empezarImpulso(et); return; }",
    'PERTURBACIÓN ACTIVA', 'REACTOR DE IMPULSO',
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== PORTADA (dev :3000) ==')
        await page.goto(BASE + '/game.html', wait_until='networkidle')
        ver = await page.evaluate("window.__PP_VERSION || ''")
        chk(ver == '3.4.0-IMP1', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.4.0-IMP1' in badge, f'badge 2D = {badge!r}')
        chk(await page.evaluate("!!(window.__ppDebug && window.__ppDebug.DIMS)"), 'DIMS presente (FIS1)')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), 'CCD lab intacto (CCD1)')
        chk(await page.evaluate("!!window.__PP_SERVE_LAB"), 'SERVE lab intacto (SRV2)')

        print('== Módulo IMP1: ReactorImpulso + hereda reactor/muro ==')
        src = await page.evaluate(f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in TOKENS:
            chk(tk in src, f'index.js contiene {tk!r}')
        chk("id: 'reactor'" in src and 'class ReactorInestable' in src,
            'la etapa 2 (reactor NUC1) sigue íntegra')
        chk('class EOArkanoid' in src, 'EOArkanoid sigue compilando (fuera del camino)')

        print('== Manifest v9 (impulso en la etapa 4) ==')
        man = await page.evaluate(f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man['version'] == 9, f"manifest version = {man['version']}")
        st3 = man['stages'][3]
        chk(st3['id'] == 'impulso' and st3['kind'] == 'impulso',
            f"stages[3] = {st3['id']}/{st3['kind']}")
        chk(man['stages'][1]['id'] == 'reactor', 'stages[1] sigue siendo reactor')
        chk(len(man['stages']) == 5, 'el camino sigue en 5 etapas')
        chk(any('IMP1' in n for n in man.get('notes', [])), 'nota IMP1 en el manifest')

        print(f'== Assets ({len(ASSETS)} ficheros HTTP 200) ==')
        codes = await page.evaluate(
            "() => Promise.all(" + json.dumps(ASSETS) + ".map(u => fetch(u).then(r => r.status)))")
        malos = [a for a, c in zip(ASSETS, codes) if c != 200]
        chk(not malos, f'{len(ASSETS) - len(malos)}/{len(ASSETS)} OK' + (f' · fallos: {malos}' if malos else ''))
        glb = await page.evaluate(
            f"() => fetch('{ORBITAL}/assets/nucleo_gravedad_lp.glb')"
            ".then(r => r.arrayBuffer()).then(b => b.byteLength)")
        chk(glb == 183560, 'núcleo GLB de la etapa 2 byte-exacto = 183560 B')

        print('== Escena en vivo: la mecánica del REACTOR DE IMPULSO de principio a fin ==')
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          if (!ctrl || !ctrl.impulso) return { error: 'sin ctrl.impulso' };
          const I = ctrl.impulso;
          const out = {};
          out.activo0 = !I.active;   // en sala el reactor de impulso está apagado
          // ENTRAR: etapa 4 (índice 3) sin cartel (la cartelería la cubre el patrón QA-ificado)
          ctrl.stage = 3;
          ctrl._arrancarImpulso(ctrl._etapa());
          out.arrancado = I.active && I.phase === 'intro';
          out.salaSwap = !!(G.roomGroup && G.roomGroup.visible === false && I.grp.visible === true);
          out.sinMesa = G.tableGroup.visible === false;
          out.sinRival = ctrl.rivalMesh.visible === false;
          out.sinMapa = !(ctrl.mapa && ctrl.mapa.group && ctrl.mapa.group.visible);
          out.coreVisible = I.core.visible;
          const cp = I.core.position;
          out.corePos = Math.abs(cp.x) < 1e-6 && Math.abs(cp.y - 1.55) < 1e-6 &&
                        Math.abs(cp.z - (-2.75)) < 1e-6;
          out.baseVisible = I.baseGrp.visible &&
                            Math.abs(I.baseGrp.position.z - (-0.55)) < 1e-6;
          out.reactorEstable = I.reactorState === 'estable';
          out.testActive = mod.testActive() === true && ctrl._testActivo() === I;
          // bote-en-espera sobre la BASE FLOTANTE + OLEADA 1 (3 cubos)
          for (let i = 0; i < 40; i++) I.step(0.1);
          out.bolaBase = Math.abs(G.ball.pos.x) < 1e-3 &&
                         Math.abs(G.ball.pos.z - (-0.55)) < 1e-3 &&
                         G.ball.pos.y > 0.85 && G.ball.pos.y < 1.35;
          out.oleada1 = I.wave === 1 && I.waveActive && I.reactorState === 'inestable';
          out.cubos1 = I.aliveCubes === 3 && I.cubes.filter(c => c.alive).length === 3;
          out.waveT120 = Math.abs(I.waveT - 119.3) < 1.5;
          out.cubosLejosNucleo = I.cubes.filter(c => c.alive)
            .every(c => Math.sqrt((c.pos.x - cp.x) ** 2 + (c.pos.y - cp.y) ** 2 +
                                  (c.pos.z - cp.z) ** 2) > 1.0);
          // DIANAS: ciclo 1 s visible / 1 s de espera con cambio de posición
          for (let i = 0; i < 120 && !I.diana.sp.visible; i++) I.step(0.05);
          out.dianaVisible = I.diana.sp.visible;
          const ax = I.diana.sp.position.x, ay = I.diana.sp.position.y, az = I.diana.sp.position.z;
          for (let i = 0; i < 40 && I.diana.sp.visible; i++) I.step(0.05);
          out.dianaExpira = !I.diana.sp.visible && I.diana.fase === 'wait';
          for (let i = 0; i < 40 && !I.diana.sp.visible; i++) I.step(0.05);
          const dx2 = I.diana.sp.position.x - ax, dy2 = I.diana.sp.position.y - ay,
                dz2 = I.diana.sp.position.z - az;
          out.dianaNuevaPos = I.diana.sp.visible &&
                              Math.sqrt(dx2 * dx2 + dy2 * dy2 + dz2 * dz2) > 0.4;
          // LÁSER → DIANA → PERTURBACIÓN (montura fantasma + raycast real)
          G.scene.updateMatrixWorld(true);
          const gmOrig = G.gunMounts;
          const mount = { getWorldPosition: (v) => v.set(0, 1.4, 0.4),
            getWorldQuaternion: (q) => q.identity(), visible: true, children: [] };
          G.gunMounts = [mount, mount];
          I.diana.sp.position.set(0, 1.49, -2.2);
          I.diana.sp.visible = true; I.diana.fase = 'vis'; I.diana.t = 1;
          I.diana.sp.updateMatrixWorld(true);
          const pert0 = I.pert;
          ctrl.fireGun(0);
          G.gunMounts = gmOrig;
          ctrl._purgeBeams();
          out.laserDiana = I.diana.fase === 'wait' && !I.diana.sp.visible &&
                           !!I.pert && I.pert !== pert0;
          out.pertNombre = I.pert;
          out.exportGun = typeof mod.fireGun === 'function' && mod.gunArmed !== undefined;
          out.laserTargetsVacia = Array.isArray(I.laserTargets()) && I.laserTargets().length === 0;
          // GOLPEO DE PALA: la pala libera la bola del bote-en-espera
          I.ballState = 'hold'; I.holdT = 0; I.graceT = 0; I._cdT = 0;
          G.ball.vel.set(0, 0, 0);
          G.ball.pos.set(0, 1.0, -0.55);
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true;
          pad.pos.copy(G.ball.pos); pad.pos.y -= 0.06;
          pad.vel.set(0, 1.0, -3.0);
          I._paddleHit(false);
          out.golpeo = I.ballState === 'play' && G.ball.vel.z < 0 &&
                       G.ball.vel.length() > 2.0;
          pad.active = false;
          // re-aparca la bola (hold) para el resto de pruebas
          I.ballState = 'hold'; I.holdT = 0; I.graceT = 0.5; I._cdT = 0;
          G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
          // PERTURBACIONES: sustitución total + supergravedad + gravedad 0
          I._pertAplica('super', false);
          for (let i = 0; i < 40; i++) I.step(0.05);
          out.superBaja = I.pert === 'super' && I.cubes.filter(c => c.alive)
            .every(c => c.pos.y < 0.5 && c.mesh.scale.y < 0.95);
          I._pertAplica('g0', false);
          const p0 = I.cubes.filter(c => c.alive).map(c => ({ x: c.pos.x, y: c.pos.y, z: c.pos.z }));
          for (let i = 0; i < 20; i++) I.step(0.05);
          out.g0Mueve = I.pert === 'g0' && I.cubes.filter(c => c.alive)
            .some((c, j) => Math.sqrt((c.pos.x - p0[j].x) ** 2 + (c.pos.y - p0[j].y) ** 2 +
                                      (c.pos.z - p0[j].z) ** 2) > 0.02);
          // ATRACTOR: agrupa en el centro y UN golpe los destruye TODOS (cadena)
          I._pertAplica('atractor', false);
          for (let i = 0; i < 60; i++) I.step(0.05);
          out.atractorAgrupa = I.pert === 'atractor' && I.cubes.filter(c => c.alive)
            .every(c => Math.sqrt(c.pos.x * c.pos.x + (c.pos.y - 1.35) ** 2 +
                                  (c.pos.z + 1.95) ** 2) < 1.2);
          const c0 = I.cubes.find(c => c.alive);
          I.ballState = 'play';   // la cadena exige bola LANZADA (colisión válida)
          G.ball.vel.set(0, 0, -3);
          G.ball.pos.copy(c0.pos); G.ball.pos.z += 0.10;
          I._tmpA.copy(c0.pos); I._tmpA.z += 0.42;
          I._cubosCollide(I._tmpA, G.ball.pos, G.ball.vel, 0.02);
          out.cadena = I.aliveCubes === 0 && !I.waveActive &&
                       I.reactorState === 'estable' && I.pert === null;
          // re-aparca la bola para no interferir con la oleada 2
          I.ballState = 'hold'; I.holdT = 0; I.graceT = 0.5; I._cdT = 0;
          G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
          // pausa estable → OLEADA 2 (5 cubos)
          for (let i = 0; i < 40; i++) I.step(0.1);
          out.oleada2 = I.wave === 2 && I.waveActive && I.aliveCubes === 5;
          for (const c of I.cubes.filter(c => c.alive)) I._destruye(c, true);
          for (let i = 0; i < 40; i++) I.step(0.1);
          out.oleada3 = I.wave === 3 && I.waveActive && I.aliveCubes === 7;
          // VICTORIA FINAL: exclusivamente tras completar las TRES oleadas
          for (const c of I.cubes.filter(c => c.alive)) I._destruye(c, true);
          out.victoria = I.phase === 'result' && ctrl.stage === 4 && !I.waveActive;
          I.step(5.0);
          out.cierre = ctrl.state === 'sala' && !I.active &&
                       G.rules.state === 'champtest' &&
                       G.roomGroup.visible === true && G.tableGroup.visible === true;
          // DERROTA: tiempo a cero con cubos → ASTRO laughing FRENTE al jugador
          ctrl.stage = 3;
          ctrl._arrancarImpulso(ctrl._etapa());
          for (let i = 0; i < 40; i++) I.step(0.1);
          I.waveT = 0.05;
          I.step(0.1);
          out.derrota = I.phase === 'result' && ctrl.rivalMesh.visible === true &&
                        ctrl._rivalEstado === 'laughing' &&
                        Math.abs(ctrl.rivalMesh.position.x) < 0.01 &&
                        Math.abs(ctrl.rivalMesh.position.z - (-2.1)) < 0.01;
          I.step(4.5);
          out.regreso = ctrl.state === 'sala' && ctrl.stage === 3 &&
                        G.tableGroup.visible === true && G.roomGroup.visible === true;
          return out;
        }""")
        if esc.get('error'):
            chk(False, f"escena: {esc['error']}")
        else:
            for k, d in (
                ('activo0', 'reactor de impulso inactivo en sala'),
                ('arrancado', 'arranque: fase intro activa'),
                ('salaSwap', 'sala propia visible · sala de la estación oculta'),
                ('sinMesa', 'SIN mesa tradicional (spec)'),
                ('sinRival', 'sin rival durante la partida (spec)'),
                ('sinMapa', 'sin mapa heredado de la escena anterior'),
                ('coreVisible', 'núcleo del reactor visible'),
                ('corePos', 'núcleo en la zona central (0 · 1,55 · −2,75)'),
                ('baseVisible', 'base flotante en su spot (z −0,55)'),
                ('reactorEstable', 'reactor arranca ESTABLE (azul)'),
                ('testActive', 'testActive del núcleo enruta al impulso'),
                ('bolaBase', 'bola botando sobre la base flotante'),
                ('oleada1', 'oleada 1 activa: reactor INESTABLE (rojo)'),
                ('cubos1', 'oleada 1 = 3 cubos expulsados'),
                ('waveT120', 'temporizador de oleada = 120 s independientes'),
                ('cubosLejosNucleo', 'cubos fuera del reactor y delante del jugador'),
                ('dianaVisible', 'diana cuántica visible (ciclo activo)'),
                ('dianaExpira', 'diana desaparece tras su segundo de visibilidad'),
                ('dianaNuevaPos', 'nueva diana en OTRA posición tras 1 s de espera'),
                ('laserDiana', f"láser acierta la diana → perturbación ({esc.get('pertNombre')})"),
                ('exportGun', 'export expone gunArmed/fireGun (FIX del gatillo)'),
                ('laserTargetsVacia', 'laserTargets: diana desactivada no recibe impactos'),
                ('golpeo', 'golpeo de pala libera la bola (velocidad real de la pala)'),
                ('superBaja', 'SUPERGRAVEDAD: cubos caen y quedan comprimidos'),
                ('g0Mueve', 'GRAVEDAD 0: deriva flotante caótica'),
                ('atractorAgrupa', 'ATRACTOR: cubos agrupados en la zona central'),
                ('cadena', 'CADENA: un golpe válido destruye TODOS los cubos → oleada completa'),
                ('oleada2', 'oleada 2 = 5 cubos tras la pausa estable'),
                ('oleada3', 'oleada 3 = 7 cubos'),
                ('victoria', 'victoria final SOLO tras completar las 3 oleadas'),
                ('cierre', 'victoria: stage → 4, vuelta a sala con la mesa restaurada'),
                ('derrota', 'derrota: ASTRO laughing FRENTE al jugador (0 · z −2,1)'),
                ('regreso', 'derrota: regreso al escenario de la etapa 1 sin avanzar'),
            ):
                chk(bool(esc.get(k)), f'{d} ({k})')

        print('== Limpieza de carga ==')
        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_imp1_portada.png')
        await browser.close()

        print('\n== GATEWAY (:81) ==')
        async with async_playwright() as p:
            b2 = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
            pg2 = await b2.new_page()
            err2 = []
            pg2.on('pageerror', lambda e: err2.append(str(e)))
            await pg2.goto(GW + '/game.html', wait_until='networkidle')
            chk(await pg2.evaluate("window.__PP_VERSION") == '3.4.0-IMP1',
                'gateway sirve 3.4.0-IMP1')
            chk(not err2, f'gateway 0 pageerrors ({len(err2)})')
            await b2.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
