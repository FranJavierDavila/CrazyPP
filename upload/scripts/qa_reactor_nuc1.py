#!/usr/bin/env python3
"""QA del JUEGO · V3.3.0-NUC1 (Reactor de energía inestable, etapa 2).
Verde = todas las comprobaciones en OK. Uso: python3 scripts/qa_reactor_nuc1.py"""
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
ASSETS = [
    f'{ORBITAL}/index.js', f'{ORBITAL}/manifest.json',
    f'{ORBITAL}/assets/nucleo_gravedad_lp.glb',
    f'{ORBITAL}/assets/rival.webp', f'{ORBITAL}/assets/focused.webp',
    f'{ORBITAL}/assets/laughing.webp', f'{ORBITAL}/assets/surprised.webp',
    f'{ORBITAL}/assets/mapa.png', f'{ORBITAL}/assets/normas_astro.png',
    f'{ORBITAL}/assets/pistol.glb',
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
        chk(ver == '3.3.0-NUC1', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.3.0-NUC1' in badge, f'badge 2D = {badge!r}')
        chk(await page.evaluate("!!(window.__ppDebug && window.__ppDebug.DIMS)"), 'DIMS presente (FIS1)')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), 'CCD lab intacto (CCD1)')
        chk(await page.evaluate("!!window.__PP_SERVE_LAB"), 'SERVE lab intacto (SRV2)')

        print('== Módulo NUC1: ReactorInestable + muro2 intacto ==')
        src = await page.evaluate(f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in ('class ReactorInestable', 'REACTOR_CFG', "id: 'reactor'",
                   'this.reactor = new ReactorInestable(this)',
                   '_empezarReactor', '_arrancarReactor', '_launch', '_paddleCollide',
                   '_gatesCheck', '_estabiliza', '_falla', '_gateSetup',
                   'nucleo_gravedad_lp.glb', '_ensureCoreArt', 'GLTFLoader',
                   "_exprSet('laughing', 2.4)", "_exprSet('surprised', 2.2)",
                   'GRAVEDAD PESADA', 'GRAVEDAD LIGERA', 'spotsA',
                   "id: 'muro2'", '_empezarMuro', 'this.arkanoid.variant',
                   'if (this.reactor && this.reactor.active) return this.reactor'):
            chk(tk in src, f'index.js contiene {tk!r}')
        chk("id: 'muro1'" not in src, "etapa 2 sin id 'muro1'")

        print('== Manifest v8 (reactor en la etapa 2) ==')
        man = await page.evaluate(f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man['version'] == 8, f"manifest version = {man['version']}")
        st1 = man['stages'][1]
        chk(st1['id'] == 'reactor' and st1['kind'] == 'reactor', f"stages[1] = {st1['id']}/{st1['kind']}")
        chk(man['stages'][3]['id'] == 'muro2' and man['stages'][3]['kind'] == 'arkanoid',
            'stages[3] sigue siendo muro2/arkanoid')
        chk(len(man['stages']) == 5, 'el camino sigue en 5 etapas')
        chk(any('NUC1' in n for n in man.get('notes', [])), 'nota NUC1 en el manifest')

        print(f'== Assets ({len(ASSETS)} ficheros HTTP 200) ==')
        codes = await page.evaluate(
            "() => Promise.all(" + json.dumps(ASSETS) + ".map(u => fetch(u).then(r => r.status)))")
        malos = [a for a, c in zip(ASSETS, codes) if c != 200]
        chk(not malos, f'{len(ASSETS) - len(malos)}/{len(ASSETS)} OK' + (f' · fallos: {malos}' if malos else ''))
        glb = await page.evaluate(
            f"() => fetch('{ORBITAL}/assets/nucleo_gravedad_lp.glb')"
            ".then(r => r.arrayBuffer()).then(b => b.byteLength)")
        chk(glb == 183560, f'núcleo GLB byte-exacto = {glb} B')

        print('== Escena en vivo: la mecánica del REACTOR de principio a fin ==')
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          if (!ctrl || !ctrl.reactor) return { error: 'sin ctrl.reactor' };
          const R = ctrl.reactor;
          const out = {};
          out.activo0 = !R.active;   // en sala el reactor DEBE estar apagado
          // ENTRAR: fuerza etapa 2 y arranca sin cartel (la cartelería la
          // cubre el patrón muro, ya QA-ificado)
          ctrl.stage = 1;
          ctrl._arrancarReactor(ctrl._etapa());
          out.arrancado = R.active && R.phase === 'intro';
          out.coreVisible = R.core.visible;
          const cp = R.core.position;
          out.corePos = Math.abs(cp.x) < 1e-3 && Math.abs(cp.y - 1.62) < 1e-3 &&
                        Math.abs(cp.z - (-3.35)) < 1e-3;
          out.hud = R.hudGroup.visible;
          out.rivalVisible = ctrl.rivalMesh.visible;   // el ASTRO REACCIONA
          // testActive del contrato del núcleo → reactor
          out.testActive = mod.testActive() === true && ctrl._testActivo() === R;
          // avance: intro (3 s) → play
          for (let i = 0; i < 40; i++) R.step(0.1);
          out.fasePlay = R.phase === 'play';
          out.bolaAparcada = Math.abs(G.ball.pos.x - 0.26) < 1e-3 &&
                             Math.abs(G.ball.pos.y - 0.95) < 1e-3 &&
                             Math.abs(G.ball.pos.z - (-0.50)) < 1e-3 &&
                             G.ball.vel.lengthSq() === 0;
          // LANZAMIENTO real del núcleo
          R._launchCd = 0; R.step(0.016);
          out.esfera = R.sphereOn && R.sphereMesh.visible && R.sphereGlow.visible;
          out.vy = +R.sphereVel.y.toFixed(2);
          out.vz = +R.sphereVel.z.toFixed(2);
          out.grav = +R.sphereG.toFixed(2);
          out.arco = R.sphereVel.z > 0.5 && R.sphereVel.y > 0.5;   // hacia el jugador y arriba
          // GOLPEO DE PALA: pala fantasma en la trayectoria
          R.sphereVel.set(0.3, 0.5, 2.6);
          R._sPrev.copy(R.spherePos);
          R.spherePos.addScaledVector(R.sphereVel, 0.05);
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true;
          pad.pos.copy(R.spherePos).addScaledVector(R.sphereVel, 0.02);
          pad.vel.set(0, 1.2, -2.4);
          R._cdT = 0; R._paddleCollide();
          out.golpeo = R.sphereHits === 1 && R.sphereVel.z < 0;   // devuelta hacia compuertas
          // ESTABILIZACIÓN: cruce real del plano de la compuerta 0
          const gate = R.gates[0];
          const sy = Math.sin(gate.yaw), cy = Math.cos(gate.yaw);
          R._sPrev.set(gate.pos.x + sy * 0.05, gate.pos.y, gate.pos.z + cy * 0.05);
          R.spherePos.set(gate.pos.x - sy * 0.01, gate.pos.y, gate.pos.z - cy * 0.01);
          R._gatesCheck(R._sPrev, R.spherePos);
          out.estabiliza = R.estabA === 1 && !R.sphereOn &&
                           R._msg.indexOf('ESTABILIZADA') >= 0;
          // FALLO: alarma + burla del ASTRO + modifier de gravedad
          R._falla('mesa');
          out.fallo = R.lives === 4 && ctrl._rivalEstado === 'laughing' &&
                      R._alarmT > 0 &&
                      ['normal', 'pesada', 'ligera'].indexOf(R.gravMod) >= 0;
          out.gatesFaseA = R.gates[0].on && !R.gates[1].on &&
                           Math.abs(R.gates[0].rIn - 0.40) < 1e-6;
          // CIERRE: victoria → _pruebaFin → sala
          R._finish(true);
          R.step(5.0);
          out.cierre = ctrl.stage === 2 && ctrl.state === 'sala' && !R.active &&
                       G.rules.state === 'champtest';
          // MURO 2 (etapa 4) INTACTO: arranca, variante 2 y el testActive lo elige
          ctrl.stage = 3;
          ctrl._arrancarMuro(ctrl._etapa());
          const ark = ctrl.arkanoid;
          out.muro2 = ark.active && ark.variant === 2 && ctrl._testActivo() === ark;
          ark.stop();
          ctrl.stage = 1;
          return out;
        }""")
        if esc.get('error'):
            chk(False, f"escena: {esc['error']}")
        else:
            for k, d in (
                ('activo0', 'reactor inactivo en sala'),
                ('arrancado', 'arranque: fase intro activa'),
                ('coreVisible', 'núcleo visible'),
                ('corePos', 'núcleo en (0 · 1,62 · −3,35)'),
                ('hud', 'HUD propio visible'),
                ('rivalVisible', 'ASTRO visible (reacciona en la prueba)'),
                ('testActive', 'testActive del núcleo enruta al reactor'),
                ('fasePlay', 'intro → play al agotarse el banner'),
                ('bolaAparcada', 'bola real aparcada en HOLD (0,26 · 0,95 · −0,50)'),
                ('esfera', 'esfera de plasma lanzada (malla + glow)'),
                ('arco', f"lanzamiento en arco (vy={esc.get('vy')} · vz={esc.get('vz')} · g={esc.get('grav')})"),
                ('golpeo', 'golpeo de pala: devuelta hacia las compuertas'),
                ('estabiliza', 'estabilización por cruce del plano (fase A)'),
                ('fallo', 'fallo: −1 estabilidad + burla + alarma + gravedad'),
                ('gatesFaseA', 'fase A: 1 compuerta GRANDE (r 0,40)'),
                ('cierre', 'victoria: _pruebaFin → etapa 2, vuelta a sala'),
                ('muro2', 'muro2 (etapa 4) intacto: variante 2 y testActive'),
            ):
                chk(bool(esc.get(k)), f'{d} ({k})')

        print('== Limpieza de carga ==')
        chk(not errors, f'0 pageerrors ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_nuc1_portada.png')
        await browser.close()

        print('\n== GATEWAY (:81) ==')
        async with async_playwright() as p:
            b2 = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
            pg2 = await b2.new_page()
            err2 = []
            pg2.on('pageerror', lambda e: err2.append(str(e)))
            await pg2.goto(GW + '/game.html', wait_until='networkidle')
            chk(await pg2.evaluate("window.__PP_VERSION") == '3.3.0-NUC1',
                'gateway sirve 3.3.0-NUC1')
            chk(not err2, f'gateway 0 pageerrors ({len(err2)})')
            await b2.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
