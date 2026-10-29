#!/usr/bin/env python3
"""QA del JUEGO · V3.6.85-SDK6 (superpoderes redefinidos + voz del ASTRO +
ajustes del reactor). Verifica en vivo: congelado REAL durante el aviso
(g.freezeT), meteoritos 3D procedurales con calor de entrada, rayo tractor
con dron + bola atrapada que cae vertical al morir el haz, gravedad cero
que atrae la bola y la hace rebotar entre partículas, audios
risa_astro.mp3 / enfado_astro.mp3 cacheados, diana cuántica visible 2 s y
la pelota que SIEMPRE vuelve a botar sobre la base flotante.
Uso: python3 scripts/qa_sup1_v361.py"""
import asyncio
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

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== PORTADA (dev :3000) ==')
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        # QA más dura que networkidle: el juego debe ARRANCAR (el sello
        # de versión solo existe si el módulo entero ejecutó) y no le
        # afecta una petición colgada del arranque.
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=45000)
        ver = await page.evaluate("window.__PP_VERSION || ''")
        chk(ver == '3.6.85-SDK6', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.6.85-SDK6' in badge, f'badge 2D = {badge!r}')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), 'CCD lab intacto (CCD1)')
        chk(await page.evaluate("typeof window.__PP_PADDLE_SWEEP === 'function'"),
            'puente CCD del núcleo expuesto (__PP_PADDLE_SWEEP)')

        print('== Ficheros ==')
        src = await page.evaluate(f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in (
            # meteoritos 3D
            'function _geoMeteorito', '_rocasGeo = [_geoMeteorito(0), _geoMeteorito(1)]',
            'vertexColors: true, flatShading: true', 'emissive: 0xff6a22',
            'calor de la entrada', 'r.m.rotation.y += dt * r.sp',
            'r.m.position.y, ez = cur.z - r.z',
            # rayo tractor
            'this.dronTractor', '_tractorTrap', 'el rayo sale de su emisor',
            'caída vertical pura', 'dentro(prev.x + dx * f',
            'this._tractorPrev.copy(ball.pos)',
            # gravedad cero
            'const ATT = 7.5', '+ 0.5 * Math.sin', 'OTRA distinta con dispersión',
            'if (g.ball.vel.y > 0) g.ball.vel.y = 0',
            # freeze del aviso — v3.6.1: vive en el SDK (una sola fuente)
            'congela(this.game, (def.warn || 2.0) + 0.15)',
            "from '../sdk/champ_sdk.js'", 'createSfx(import.meta.url', '__sdkSfx',
            # audios del ASTRO
            "_sfx(name)", "this._sfx('enfado_astro.mp3')", "this._sfx('risa_astro.mp3')",
            "a._sfx('risa_astro.mp3')",
            # reactor
            'dianaVis: 2.0, dianaWait: 1.0', 'this._restT > 0.6',
            'this._restT = 0;                   // v3.6.0: bote limpio',
        ):
            chk(tk in src, f'módulo: {tk}')
        chk('r.s.visible' not in src.split('class StockController')[1].split('class MapaEO')[0],
            'sin referencias huérfanas a los sprites antiguos de rocas')
        man = await page.evaluate(f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man.get('version') == 17, f'manifest version = {man.get("version")}')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'manifest stages = duelo1·impulso·duelo2·escudo·final')
        chk(any('v3.6.1-SDK1' in c for c in man.get('cambios', [])), 'cambios: entrada v3.6.1-SDK1')
        chk(len(man.get('powers', [])) == 4, 'los 4 superpoderes siguen en el manifest')
        mp3s = await page.evaluate("""async () => {
          const out = {};
          for (const f of ['risa_astro.mp3', 'enfado_astro.mp3']) {
            const r = await fetch(`championships/estacion_orbital/assets/${f}`);
            out[f] = { st: r.status, n: (await r.arrayBuffer()).byteLength };
          }
          return out;
        }""")
        chk(mp3s['risa_astro.mp3']['st'] == 200 and mp3s['risa_astro.mp3']['n'] == 81408,
            f"risa_astro.mp3 servido ({mp3s['risa_astro.mp3']['n']} B)")
        chk(mp3s['enfado_astro.mp3']['st'] == 200 and mp3s['enfado_astro.mp3']['n'] == 37616,
            f"enfado_astro.mp3 servido ({mp3s['enfado_astro.mp3']['n']} B)")

        print('== SDK DE CAMPEONATOS (champ_sdk.js) ==')
        sdksrc = await page.evaluate("fetch('championships/sdk/champ_sdk.js').then(r=>r.text())")
        for tk in ("const SDK_VERSION = '1.5.4'", 'export function createSfx',
                   'export function congela', 'export function descongela',
                   'export function getCore', 'export function assetURL',
                   'forma promesa (v2.125)', 'decodeAudioData(ab.slice(0))',
                   'function precarga', 'opts && opts.pan',
                   'export function createMusic',
                   'o.gateStart !== false && arcPlaying()',
                   'export function createPowerSign',
                   'V240 = o.coreo',
                   'export function createRival', "o.modo === 'precarga'",
                   'export function createCartel', 'pintorSuperPower'):
            chk(tk in sdksrc, f'SDK: {tk}')

        print('== FASE 5: la música en el SDK (createMusic) ==')
        for mod, vman, nota in (('oeste', 56, 'v3.6.4-SDK4'),
                                ('magia', 33, 'v3.6.4-SDK4'),
                                ('halloween', 3, 'r86')):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk("from '../sdk/champ_sdk.js'" in srcm, f'{mod}: importa el SDK')
            if mod == 'halloween':
                # r85 · la PLANTILLA (halloween) delega la música con su propia firma
                chk('createMusic(() => GAME' in srcm, f'{mod}: la música delega en createMusic (plantilla r85)')
            else:
                chk('get _musSDK()' in srcm, f'{mod}: la música delega en createMusic')
            chk('decodeAudioData(' not in srcm, f'{mod}: sin decodeAudioData propio')
            chk('freezeT = Math.max' not in srcm, f'{mod}: sin freeze duplicado')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            chk(any(nota in n for n in manm.get('notes', [])),
                f'{mod}: nota {nota} en el historial')
        print('== FASE 6: el tablón de SUPERPODER en el SDK (createPowerSign) ==')
        for mod, vman, coreo in (('oeste', 56, 'clasica'), ('magia', 33, 'clasica'),
                                 ('locura', 27, 'v240'),
                                 ('estacion_orbital', 17, 'v240')):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk('createPowerSign(THREE' in srcm, f'{mod}: el tablón delega en el SDK')
            chk("coreo: '" + coreo + "'" in srcm, f'{mod}: coreografía {coreo} conservada')
            ndec = srcm.count('decodeAudioData(')
            chk(ndec == 0,
                f'{mod}: decodeAudioData propio = {ndec} (FASE 7: cero en los 5)')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            chk(any('v3.6.4-SDK4' in n for n in manm.get('notes', [])),
                f'{mod}: nota SDK4 en el historial')

        print('== FASE 7: standee + tablero en el SDK (createRival/createCartel) ==')
        for mod, vman, modo, base in (('estacion_orbital', 17, 'perezoso', 'rival.webp'),
                                      ('halloween', 3, 'precarga', 'present.webp')):
            srcm = await page.evaluate(
                f"fetch('championships/{mod}/index.js').then(r=>r.text())")
            chk('createRival(THREE' in srcm, f'{mod}: el standee delega en el SDK')
            if mod == 'halloween':
                # r85 · tokens de la PLANTILLA (rv del manifest en vez de literales)
                chk("modo: this.rv.modo || 'precarga'" in srcm, f'{mod}: motor precarga conservado')
                chk("base: this.rv.base || 'rival.webp'" in srcm, f'{mod}: arte del rival cableado por manifest')
                chk('cartel.pinta(' in srcm, f'{mod}: el ARTE pinta en el lienzo del SDK')
                chk('so.musicOpts || {}' in srcm, f'{mod}: la música delega en createMusic')
            else:
                chk("modo: '" + modo + "'" in srcm, f'{mod}: motor {modo} conservado')
                chk("base: '" + base + "'" in srcm, f'{mod}: arte {base} cableado')
                chk('this._cartelSDK.pinta(' in srcm, f'{mod}: el ARTE pinta en el lienzo del SDK')
                chk('get _musSDK()' in srcm, f'{mod}: la música delega en createMusic')
            chk('createCartel(THREE' in srcm, f'{mod}: el tablero delega en el SDK')
            manm = await page.evaluate(
                f"fetch('championships/{mod}/manifest.json').then(r=>r.json())")
            chk(manm.get('version') == vman, f'{mod}: manifest v{vman}')
            if mod == 'halloween':
                chk(any('r85' in n for n in manm.get('notes', [])), f'{mod}: nota r85 en el historial')
            else:
                chk(any('v3.6.5-SDK5' in n for n in manm.get('notes', [])),
                    f'{mod}: nota SDK5 en el historial')
        ndec = await page.evaluate("""async () => {
          let n = 0;
          for (const m of ['oeste', 'magia', 'locura', 'estacion_orbital', 'halloween']) {
            const s = await fetch('championships/' + m + '/index.js').then(r => r.text());
            n += (s.match(/decodeAudioData[(]/g) || []).length;
          }
          return n;
        }""")
        chk(ndec == 0, f'decodeAudioData en los 5 módulos = {ndec} (FASE 7: cero; solo el SDK)')

        print('== ESCENA EN VIVO: campeonato cargado ==')
        ctx = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          try { localStorage.setItem('pp_player_name', 'FORO3D'); if (window.ppDebugRefresh) window.ppDebugRefresh(); } catch (e) { /**/ }
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 4000));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          try { if (G.audio && G.audio.ctx) await G.audio.ctx.resume(); } catch (e) { /**/ }
          return { state: ctrl.state, ctxState: (G.audio && G.audio.ctx) ? G.audio.ctx.state : 'none' };
        }""")
        chk(ctx['state'] in ('sala', 'duelo'), f"controlador vivo (state {ctx['state']})")
        chk(await page.evaluate("window.__PP_SDK || ''") == '1.5.4',
            'window.__PP_SDK = 1.5.4 (SDK importado en cadena por el orbital)')

        print('== FREEZE REAL durante el aviso de superpoder ==')
        frz = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          G.freezeT = 0;
          ctrl._bolsa = [];
          ctrl._quizasPoder(true);            // fuerza el aviso
          const out = { warn: !!ctrl._warn, name: ctrl._warn ? ctrl._warn.def.name : '',
                        freeze: G.freezeT, cartel: !!(ctrl.pwSign && ctrl.pwSign.group.visible) };
          ctrl._warn = null;                  // limpiar: el resto de pruebas manda
          ctrl._psOculta();
          G.freezeT = 0;
          return out;
        }""")
        chk(frz['warn'], f"aviso de dos fases disparado ({frz['name']})")
        chk(frz['freeze'] >= 1.9, f"PARTIDA CONGELADA: freezeT = {frz['freeze']:.2f} s (warn + 0,15)")
        chk(frz['cartel'], 'cartel Super Power!! en escena durante el aviso')

        print('== METEORITOS 3D (rocas procedurales) ==')
        met = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const def = { kind: 'custom', name: 'Meteoritos', rocas: 3, duration: 11 };
          ctrl._poderArrancar(def);
          const r0 = ctrl.rocas[0];
          const out = { esMesh: !!r0.m && r0.m.isMesh, vc: r0.mat.vertexColors,
                        flat: r0.mat.flatShading };
          // caída + aterrizaje (4 s a 1/60)
          const ball = G.ball;
          ball.vel.set(0, 0, 0);
          ball.pos.set(99, 3, 99);            // lejos: no interfiere
          for (let i = 0; i < 240; i++) ctrl._meteorStep(1 / 60, ctrl._act, ball, false);
          const r1 = ctrl.rocas.find(r => r.on);
          out.calor = { cayendo: r1 ? null : 'aterrizada', emi: r1 ? r1.mat.emissiveIntensity : 0.12 };
          out.posada = r1 && !r1.cayendo && Math.abs(r1.y - (0.76 + 0.17)) < 0.02;
          out.tumble = r1.m.rotation.y !== 0;
          // BLOQUEO de la bola (patrón Burla intacto)
          ctrl._bolaPrev = new ball.pos.constructor().copy(ball.pos);
          ball.pos.set(r1.x, r1.m.position.y, r1.z);
          ball.vel.set(0, -1, 0);
          ctrl._meteorStep(1 / 60, ctrl._act, ball, true);
          out.rockMuere = !r1.on;
          out.bolaRebota = ball.vel.y >= 2.3;
          ctrl._poderFin();
          out.finLimpio = ctrl.rocas.every(r => !r.on && !r.m.visible);
          return out;
        }""")
        chk(met['esMesh'], 'las rocas son MESHES 3D (adiós sprites)')
        chk(met['vc'] and met['flat'], 'material con color por vértice + flat shading')
        chk(met['posada'], 'la roca aterriza sobre tu campo (y = tableTop + 0,17)')
        chk(met['calor']['emi'] is not None and met['tumble'], 'tumbling de la roca viva')
        chk(met['rockMuere'] and met['bolaRebota'],
            f"la roca ESTALLA al bloquear la bola (rebote y {met['bolaRebota']})")
        chk(met['finLimpio'], 'fin del poder deja el pool limpio')

        print('== RAYO TRACTOR: dron encima del haz + bola atrapada ==')
        tra = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl._poderClear();   // anti-flake (Task 89): mismo patrón que en gravedad cero
          const def = { kind: 'custom', name: 'Rayo tractor', duration: 7 };
          const D = ctrl.D;
          const bz = (D.tableCenterZ || -1.6) + 0.55;
          ctrl._poderArrancar(def);
          const out = { beam: ctrl.beam.visible, dron: ctrl.dronTractor.visible,
                        dronY: ctrl.dronTractor.position.y, bz: bz };
          out.dronEncima = ctrl.dronTractor.position.y > 1.95;
          // la bola ENTRA en el cono (rally simulado)
          const rally0 = G.rules.state;
          G.rules.state = 'rally';
          const ball = G.ball;
          ball.pos.set(0.0, 1.45, bz + 0.02);
          ball.vel.set(0, -2.2, -3.0);
          ctrl._tractorStep(1 / 60, ctrl._act, ball, true);
          out.trap1 = !!ctrl._tractorTrap && ball.vel.lengthSq() === 0;
          // sigue atrapada: flota con vaivén y velocidad cero
          const y1 = ball.pos.y;
          ctrl._tractorStep(1 / 60, ctrl._act, ball, true);
          out.flota = ball.vel.lengthSq() === 0 && Math.abs(ball.pos.y - y1) < 0.05;
          out.dentroHaz = Math.abs(ball.pos.z - bz) < 0.20 && ball.pos.y > 0.8 && ball.pos.y < 1.9;
          // captura por CRUCE (segmento prev→actual)
          ctrl._tractorTrap = null;
          ball.pos.set(0.0, 1.30, bz - 0.60);     // fuera, en la línea del haz
          ball.vel.set(0, 0, 9.0);
          ctrl._tractorStep(1 / 60, ctrl._act, ball, true);   // registra prev
          ball.pos.set(0.0, 1.30, bz + 0.60);     // cruza el cono en un frame
          ctrl._tractorStep(1 / 60, ctrl._act, ball, true);
          out.cruce = !!ctrl._tractorTrap;
          // el haz muere → CAÍDA VERTICAL
          ctrl._poderFin();
          out.fin = !ctrl.beam.visible && !ctrl.dronTractor.visible && !ctrl._tractorTrap;
          out.suelta = ball.vel.x === 0 && ball.vel.z === 0 && ball.vel.y === 0;
          G.rules.state = rally0;
          return out;
        }""")
        chk(tra['beam'] and tra['dron'], 'haz visible + dron visible encima')
        chk(tra['dronEncima'], f"dron a y {tra['dronY']:.2f} (encima de la boca del haz)")
        chk(tra['trap1'], 'bola que entra en el haz queda ATRAPADA (vel = 0)')
        chk(tra['flota'] and tra['dentroHaz'], 'atrapada FLOTANDO dentro del rayo')
        chk(tra['cruce'], 'captura también por CRUCE del segmento (anti-túnel)')
        chk(tra['fin'] and tra['suelta'],
            'al morir el haz: dron fuera y bola SUELTA vertical (vel 0)')
        await page.screenshot(path='download/qa_sup1_tractor.png')

        print('== GRAVEDAD CERO: partículas que atraen y rebotan la bola ==')
        cer = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl._poderClear();   // anti-flake (Task 89): fuera poderes/avisos envejecidos del bucle vivo
          const rally0 = G.rules.state;
          const def = { kind: 'custom', name: 'Gravedad cero', duration: 8 };
          ctrl._poderArrancar(def);
          G.rules.state = 'rally';
          const ball = G.ball;
          ball.pos.set(0, 0.95, -0.7);
          ball.vel.set(0.5, 0, 0.5);
          // unas frames para que las motas se enciendan (la opacidad vive en el step)
          for (let i = 0; i < 10; i++) ctrl._ceroStep(1 / 60, ctrl._act, ball, true);
          const out = { motas: ctrl.motas.filter(m => m.s.material.opacity > 0.1).length };
          let minY = 9, spd = 0, cambios = 0, sobreCero = 0, lastT = ctrl._act.tgt;
          const GRAV = (ctrl.D && ctrl.D.gravity != null) ? ctrl.D.gravity : -9.81;
          for (let i = 0; i < 300; i++) {          // 5 s a 1/60
            ctrl._ceroStep(1 / 60, ctrl._act, ball, true);
            ball.vel.y += GRAV * (1 / 60);   // Task 89: gravedad del núcleo — el poder compensa +9,6 y el flotado es real (antes la bola salía lanzada y el check fallaba por suerte geométrica)
            ball.pos.addScaledVector(ball.vel, 1 / 60);   // integra como el núcleo
            minY = Math.min(minY, ball.pos.y);
            if (ball.pos.y > 0) sobreCero++;
            spd = ball.vel.length();
            if (ctrl._act.tgt !== lastT) { cambios++; lastT = ctrl._act.tgt; }
          }
          out.minY = minY; out.spd = spd; out.cambios = cambios;
          out.sobreCero = sobreCero / 300;
          // fin del poder: las partículas DESAPARECEN y DEJAN CAER la bola
          ball.vel.set(0.8, 1.4, 0.8);
          ctrl._poderFin();
          out.fin = ctrl.motas.every(m => m.s.material.opacity === 0);
          out.cae = ball.vel.y <= 0 && Math.abs(ball.vel.x) < 0.2 && Math.abs(ball.vel.z) < 0.2;
          G.rules.state = rally0;
          return out;
        }""")
        chk(cer['motas'] >= 12, f"{cer['motas']} partículas blancas visibles")
        chk(cer['sobreCero'] > 0.5, f"la bola FLOTA: {round(cer['sobreCero'] * 100)}% de frames sobre el suelo (y mín {cer['minY']:.2f}; gravedad compensada)")
        chk(cer['spd'] > 0.2, 'la bola es atraída (velocidad viva)')
        chk(cer['cambios'] >= 2, f"rebota ENTRE ELLAS: {cer['cambios']} cambios de objetivo")
        chk(cer['fin'] and cer['cae'], 'al desaparecer las partículas: bola DEJADA CAER')

        print('== AUDIOS DEL ASTRO (mp3 del dueño) ==')
        aud = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const out = {};
          // el motor de expresiones sólo actúa EN DUELO: estado temporal
          const st0 = ctrl.state;
          ctrl.state = 'duelo';
          // contexto de audio ejecutándose para el test (el juego real usa el suyo)
          if (!G.audio.ctx || G.audio.ctx.state !== 'running') {
            try { const tc = new AudioContext(); await tc.resume();
                  if (!out._old) out._old = G.audio.ctx; G.audio.ctx = tc; } catch (e) { /**/ }
          }
          // v3.6.49 (r57): la NORMA DE EMOCIONES del núcleo reparte las
          // reacciones (el viejo _exprOnPoint ya no decide) — el test
          // llama al hook estándar rivalEmocion como hace el núcleo.
          ctrl.rivalEmocion('angry');   // ASTRO pierde punto → enfado
          // poll: el fetch+decode del mp3 puede tardar >0,9 s en headless
          const espera = async (k) => {
            for (let i = 0; i < 40; i++) {
              await new Promise(r => setTimeout(r, 100));
              if (ctrl.__sdkSfx && ctrl.__sdkSfx.tiene(k)) return true;
            }
            return false;
          };
          out.enfado = await espera('enfado_astro.mp3');
          ctrl.rivalEmocion('laughing');   // ASTRO se ríe (jugador falla)
          out.risa = await espera('risa_astro.mp3');
          out.poseRisa = ctrl._rivalEstado === 'laughing' || ctrl._exprT > 0;
          if (out._old) G.audio.ctx = out._old;
          ctrl.state = st0;
          return out;
        }""")
        chk(aud['enfado'], 'enfado_astro.mp3 decodificado al perder el ASTRO un punto')
        chk(aud['risa'], 'risa_astro.mp3 decodificado con la pose de risas')
        chk(aud['poseRisa'], 'pose de risas aplicada (laughing)')

        print('== ESCENA EN VIVO: reactor de impulso · diana 2 s + pelota ==')
        imp = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          ctrl.stage = 1;
          ctrl._arrancarImpulso(ctrl._etapa());
          await new Promise(r => setTimeout(r, 400));
          const I = ctrl.impulso;
          for (let i = 0; i < 45; i++) I.step(0.1);          // intro → oleada 1
          const out = { wave: I.wave === 1 && I.waveActive };
          // DIANA visible 2 s: wait → in → vis (pasos finos para leer d.t recién)
          const d = I.diana;
          d.fase = 'wait'; d.t = 0.01;
          I._dianasStep(0.05);                                // → in
          out.vis = false; out.tVis = 0;
          for (let i = 0; i < 60 && !out.vis; i++) {          // pasos de 10 ms
            I._dianasStep(0.01);
            if (d.fase === 'vis') { out.vis = true; out.tVis = d.t; }
          }
          out.targets = I.laserTargets().length === 1;
          // PELOTA: reposo sobre la base → SIEMPRE vuelve a botar
          const ball = G.ball;
          I.ballState = 'play'; I.flight = 0; I._restT = 0;
          ball.pos.set(0, I._baseTopY() + 0.03, -0.55);       // encima de la base
          ball.vel.set(0, 0, 0);
          if (ball.__exPrev) ball.__exPrev.copy(ball.pos);
          let vioRespawn = false;
          for (let i = 0; i < 120; i++) {                     // 6 s
            I.step(0.05);
            if (I.ballState === 'respawn') vioRespawn = true;
            if (I.ballState === 'hold' && vioRespawn) break;
          }
          out.reposoPerdida = vioRespawn;
          for (let i = 0; i < 6 && I.ballState === 'hold'; i++) I.step(0.05);  // deja nacer el bote
          out.vuelve = I.ballState === 'hold' && ball.pos.x === 0 &&
                       Math.abs(ball.pos.z - (-0.55)) < 0.01 && ball.pos.y > 0.8;
          out.bote = Math.abs(ball.vel.y) > 0.2;              // BOTANDO, no quieta
          return out;
        }""")
        chk(imp['wave'], 'oleada 1 activa (3 cubos)')
        chk(imp['vis'], 'diana materializada (fase vis)')
        chk(imp['tVis'] > 1.9, f"DIANA VISIBLE {imp['tVis']:.2f} s (antes 1 s)")
        chk(imp['targets'], 'el láser la tiene como objetivo mientras es visible')
        chk(imp['reposoPerdida'], 'pelota en reposo → considerada perdida (se recupera)')
        chk(imp['vuelve'], 'la pelota VUELVE a la base flotante')
        chk(imp['bote'], '…y BOTANDO sobre la mesita circular (no quieta)')

        print('== Derrota del reactor: ASTRO se ríe (risa cableada) ==')
        der = await page.evaluate("""() => {
          const G = window.__PP_GAME;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const I = ctrl.impulso;
          I._finish(false, 'time');
          const out = { visible: ctrl.rivalMesh.visible, pose: ctrl._rivalEstado };
          try { I.stop(); } catch (e) { /**/ }
          return out;
        }""")
        chk(der['visible'] and der['pose'] == 'laughing',
            f"ASTRO en pose de risas ante la derrota ({der['pose']})")

        print('== Gateway :81 ==')
        pg2 = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors2 = []
        pg2.on('pageerror', lambda e: errors2.append(str(e)))
        await pg2.goto(GW + '/game.html', wait_until='domcontentloaded')
        await pg2.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=45000)
        chk(await pg2.evaluate("window.__PP_VERSION") == '3.6.85-SDK6', 'gateway: __PP_VERSION 3.6.85-SDK6')
        chk(await pg2.evaluate("typeof window.__PP_PADDLE_SWEEP === 'function'"), 'gateway: puente CCD')
        chk(await pg2.evaluate("!!window.__PP_GAME"), 'gateway: juego arranca')
        mp3gw = await pg2.evaluate("""async () => {
          const r = await fetch('championships/estacion_orbital/assets/risa_astro.mp3');
          return { st: r.status, n: (await r.arrayBuffer()).byteLength };
        }""")
        chk(mp3gw['st'] == 200 and mp3gw['n'] == 81408, 'gateway: risa_astro.mp3 servido byte-exacto')
        chk(not errors2, f'0 pageerrors gateway ({len(errors2)}): {errors2[:2]}')
        await pg2.close()

        chk(not errors, f'0 pageerrors dev ({len(errors)}): {errors[:2]}')
        await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    sys.exit(1 if fails else 0)

asyncio.run(main())
