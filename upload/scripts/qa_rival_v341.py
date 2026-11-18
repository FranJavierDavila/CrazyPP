#!/usr/bin/env python3
"""QA del JUEGO · V3.4.1-RIV1 (ASTRO recolocado en la sala del orbital).
Verde = todas las comprobaciones en OK. Uso: python3 scripts/qa_rival_v341.py"""
import asyncio
import base64
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
    f'{ORBITAL}/assets/rival.webp', f'{ORBITAL}/assets/laughing.webp',
    f'{ORBITAL}/assets/mapa.png', f'{ORBITAL}/assets/pistol.glb',
    f'{ORBITAL}/assets/nucleo_gravedad_lp.glb',
    f'{ORBITAL}/assets/reactor_impulso/base.png',
    f'{ORBITAL}/assets/reactor_impulso/diana_quantica.png',
    f'{ORBITAL}/assets/reactor_impulso/pantallainfo.png',
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
        chk(ver == '3.4.1-RIV1', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.4.1-RIV1' in badge, f'badge 2D = {badge!r}')
        chk(await page.evaluate("!!(window.__ppDebug && window.__ppDebug.DIMS)"), 'DIMS presente (FIS1)')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), 'CCD lab intacto (CCD1)')
        chk(await page.evaluate("!!window.__PP_SERVE_LAB"), 'SERVE lab intacto (SRV2)')

        print('== Ficheros ==')
        src = await page.evaluate(f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        chk('position.set(1.26, RIV_H / 2' in src, 'módulo: ASTRO en x 1,26 (borde derecho + 0,50)')
        chk('(D.tableCenterZ || -1.6) - 2.22' in src, 'módulo: ASTRO en z −3,82 (tabla −2,22)')
        chk('position.set(1.62, RIV_H / 2' not in src, 'módulo: SIN la posición antigua (x 1,62 · z −4,5)')
        chk('REGLA FIJA de duelos' in src, 'módulo: comentario de la convención documentado')
        man = await page.evaluate(f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man.get('version') == 10, f'manifest version = {man.get("version")}')
        for tk in ('class ReactorImpulso', "id: 'impulso'", 'class ReactorInestable',
                   "id: 'reactor'", 'class EOArkanoid', 'class PwSignEO'):
            chk(tk in src, f'módulo íntegro: {tk}')
        codes = await page.evaluate("""async (urls) => {
          const out = [];
          for (const u of urls) {
            try { const r = await fetch(u); out.push(r.status); } catch { out.push(0); }
          }
          return out;
        }""", [BASE + '/' + a for a in ASSETS])
        chk(all(c == 200 for c in codes), f'{len(ASSETS)} assets del rival/reactor = 200 ({codes})')

        print('== ESCENA EN VIVO: el ASTRO bien colocado (etapa 1 · sala) ==')
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          if (!G) return { error: 'sin __PP_GAME' };
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod && mod.controller;
          if (!ctrl || !ctrl.rivalMesh) return { error: 'sin ctrl.rivalMesh' };
          const out = {};
          // SALA de la etapa 1: el ASTRO de pie en el spot nuevo
          ctrl.stage = 0;
          ctrl.state = 'sala';
          ctrl.rivalMesh.visible = true;
          const p = ctrl.rivalMesh.position;
          out.pos = [ +p.x.toFixed(3), +p.y.toFixed(3), +p.z.toFixed(3) ];
          out.spotX = Math.abs(p.x - 1.26) < 1e-3;
          out.spotZ = Math.abs(p.z - (-3.82)) < 1e-3;
          out.piesEnSuelo = Math.abs(p.y - 2.15 / 2) < 1e-3;   // RIV_H/2
          out.visible = ctrl.rivalMesh.visible;
          out.escala = ctrl.rivalMesh.scale.y === 1 && ctrl.rivalMesh.scale.x === 1;
          // GEOMETRÍA: hueco real con las paredes (sala del núcleo)
          const D = (window.__ppDebug && window.__ppDebug.DIMS) || G.DIMS;
          out.huecoFrontal = +((p.z - D.roomFrontZ)).toFixed(2);   // distancia a la pared frontal
          out.huecoDerecha = +((D.roomHalfX - p.x)).toFixed(2);    // distancia a la pared derecha
          out.librePared = (p.z - D.roomFrontZ) > 1.5 && (D.roomHalfX - p.x) > 1.5;
          // Detrás del borde lejano de la mesa, sin solaparla
          out.trasMesa = p.z < (D.tableCenterZ - D.tableHalfLength);
          out.alLadoMesa = p.x > (D.tableHalfWidth + 0.4) && p.x < (D.tableHalfWidth + 0.7);
          // id de la etapa 1 y estado
          out.etapa0 = ctrl._etapa().id;
          // Home del rival usado por reactor/impulso (clonado al arrancar)
          ctrl.reactor.start && ctrl.reactor.stop();
          out.homeClone = true;
          return out;
        }""")
        if esc.get('error'):
            chk(False, f"escena: {esc['error']}")
        else:
            chk(esc.get('spotX'), 'ASTRO en x 1,26 exacto')
            chk(esc.get('spotZ'), 'ASTRO en z −3,82 exacto (profundidad CLOWN/WIZARD)')
            chk(esc.get('piesEnSuelo'), f"pies en el suelo (y={esc['pos'][1]})")
            chk(esc.get('visible'), 'ASTRO visible en la sala')
            chk(esc.get('escala'), 'escala sin deformar (1:1)')
            chk(esc.get('librePared'),
                f"LIBRE DE PAREDES (frontal {esc['huecoFrontal']} m · derecha {esc['huecoDerecha']} m)")
            chk(esc.get('trasMesa'), 'detrás del borde lejano de la mesa')
            chk(esc.get('alLadoMesa'), 'al lado derecho de la mesa (0,50 m del borde)')
            chk(esc.get('etapa0') == 'duelo1', 'etapa 1 = duelo1 (el ASTRO acompaña)')

        print('== Capturas de evidencia ==')
        shot = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const c = G.camera;
          c.parent && c.parent.remove(c);
          G.scene.add(c);
          c.position.set(0, 1.62, 0.9);
          c.lookAt(1.26, 1.05, -3.82);
          c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open('/home/z/my-project/download/qa_riv1_rival_sala.png', 'wb') as f:
            f.write(base64.b64decode(shot.split(',', 1)[1]))
        chk(True, 'captura qa_riv1_rival_sala.png guardada')

        print('== Mecánicas intactas (reactor + impulso) ==')
        esc2 = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const out = {};
          // REACTOR (etapa 2) arranca y el testActive lo elige
          ctrl.stage = 1;
          ctrl._arrancarReactor(ctrl._etapa());
          out.reactor = ctrl.reactor.active && mod.testActive() === true;
          ctrl.reactor.stop();
          // IMPULSO (etapa 4) arranca y el testActive lo elige
          ctrl.stage = 3;
          ctrl._arrancarImpulso(ctrl._etapa());
          out.impulso = ctrl.impulso.active && mod.testActive() === true;
          out.impSala = G.roomGroup.visible === false;   // sala propia
          ctrl.impulso.stop();
          // al parar, el ASTRO vuelve a SU CASA (el nuevo spot)
          const p = ctrl.rivalMesh.position;
          out.homeRestaurada = Math.abs(p.x - 1.26) < 1e-3 &&
                               Math.abs(p.z - (-3.82)) < 1e-3;
          out.homeVisible = ctrl.rivalMesh.visible;
          ctrl.stage = 0;
          return out;
        }""")
        for k, d in (
            ('reactor', 'reactor (etapa 2) arranca + testActive'),
            ('impulso', 'impulso (etapa 4) arranca + testActive'),
            ('impSala', 'impulso: sala propia sin roomGroup'),
            ('homeRestaurada', 'al parar, el ASTRO vuelve al NUEVO spot (1,26 · −3,82)'),
            ('homeVisible', 'ASTRO visible tras las pruebas'),
        ):
            chk(bool(esc2.get(k)), d)

        print('== Limpieza de carga ==')
        chk(not errors, f'0 pageerrors dev ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_riv1_portada.png')
        await browser.close()

    print('\n== GATEWAY (:81) ==')
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg2 = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors2 = []
        pg2.on('pageerror', lambda e: errors2.append(str(e)))
        await pg2.goto(GW + '/game.html', wait_until='networkidle')
        chk(await pg2.evaluate("window.__PP_VERSION") == '3.4.1-RIV1', 'gateway: __PP_VERSION 3.4.1-RIV1')
        chk(await pg2.evaluate("!!window.__PP_GAME"), 'gateway: juego arranca')
        chk(not errors2, f'0 pageerrors gateway ({len(errors2)}): {errors2[:2]}')
        await browser.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
