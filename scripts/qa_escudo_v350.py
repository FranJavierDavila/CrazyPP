#!/usr/bin/env python3
"""QA del JUEGO · V3.5.1-IMP2 (Escudo de pala · Defensa del casco, etapa 4
nueva con arte propio + impulso en etapa 2 + fixes Hall/entrenamiento).
Uso: python3 scripts/qa_escudo_v350.py"""
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
ESC = [
    f'{ORBITAL}/assets/escudo_pala/frente.jpg', f'{ORBITAL}/assets/escudo_pala/trasera.jpg',
    f'{ORBITAL}/assets/escudo_pala/izquierda.png', f'{ORBITAL}/assets/escudo_pala/derecha.png',
    f'{ORBITAL}/assets/escudo_pala/techo.jpg', f'{ORBITAL}/assets/escudo_pala/suelo.jpg',
    f'{ORBITAL}/assets/escudo_pala/pantallainfo.png',
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))

        print('== PORTADA (dev :3000) ==')
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded')
        await page.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=45000)
        ver = await page.evaluate("window.__PP_VERSION || ''")
        chk(ver == '3.6.8-SDK6', f'__PP_VERSION = {ver!r}')
        badge = await page.inner_text('#verBadge') if await page.locator('#verBadge').count() else ''
        chk('V3.6.8-SDK6' in badge, f'badge 2D = {badge!r}')
        chk(await page.evaluate("!!window.__PP_CCD_LAB"), 'CCD lab intacto (CCD1)')
        chk(await page.evaluate("!!window.__PP_SERVE_LAB"), 'SERVE lab intacto (SRV2)')
        chk(await page.evaluate("typeof window.__PP_PADDLE_SWEEP === 'function'"),
            'puente CCD del escudo expuesto (__PP_PADDLE_SWEEP)')

        print('== Ficheros ==')
        src = await page.evaluate(f"fetch('{ORBITAL}/index.js').then(r=>r.text())")
        for tk in ('class EscudoCasco', 'const ESC_CFG', "id: 'escudo'", '_empezarEscudo',
                   '_arrancarEscudo', '_dronMuere', '_centRebota', '_canonSiguiente',
                   'escudo_pala/', 'BARRERA DE CASCO', 'ORBE PERFORANTE', 'champDecorHidden',
                   "if (et.id === 'escudo') { this._empezarEscudo(et); return; }",
                   "if (this.escudo) this.escudo.stop();"):
            chk(tk in src, f'módulo: {tk}')
        # camino nuevo: impulso etapa 2 · escudo etapa 4 · sin reactor en etapas
        chk(src.count("{ kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' }") == 1,
            'camino: impulso en la etapa 2')
        chk(src.count("{ kind: 'prueba', id: 'escudo', name: 'Escudo de pala' }") == 1,
            'camino: escudo en la etapa 4')
        chk("{ kind: 'prueba', id: 'reactor'" not in src, 'camino: el reactor v3.3.0 sale del camino')
        chk('class ReactorInestable' in src, 'clase ReactorInestable conservada (re-insertable)')
        chk('(D.tableCenterZ || -1.6) - 1.70' in src, 'ASTRO v3.5.1 intacto (x 1,26 · z −3,30)')
        man = await page.evaluate(f"fetch('{ORBITAL}/manifest.json').then(r=>r.json())")
        chk(man.get('version') == 16, f'manifest version = {man.get("version")}')
        chk([st['id'] for st in man['stages']] == ['duelo1', 'impulso', 'duelo2', 'escudo', 'final'],
            'manifest stages = duelo1·impulso·duelo2·escudo·final')
        codes = await page.evaluate("""async (urls) => {
          const out = [];
          for (const u of urls) { try { const r = await fetch(u); out.push(r.status); } catch { out.push(0); } }
          return out;
        }""", [BASE + '/' + a for a in ESC])
        chk(all(c == 200 for c in codes), f'{len(ESC)} arte del escudo = 200 ({codes})')

        print('== ESCENA EN VIVO: mecánica completa del ESCUDO ==')
        esc = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const V3 = G.camera.position.constructor;
          G.champs.launch('estacion_orbital');
          await new Promise(r => setTimeout(r, 5500));
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller;
          const E = ctrl.escudo;
          const out = {};
          ctrl.stage = 3;
          ctrl._arrancarEscudo(ctrl._etapa());
          out.arranque = E.active && E.phase === 'prep';
          out.sala = E.grp.visible && !G.roomGroup.visible && !G.tableGroup.visible &&
                     !G.scoreboardGroup.visible && !ctrl.rivalMesh.visible &&
                     !G.ballMesh.visible && G.champDecorHidden === true;
          for (let i = 0; i < 40; i++) E.step(0.1);
          out.fase1 = E.phase === 'combate' && E.fase === 0 &&
                      E.drones.filter(d => d.alive).length === 3;
          // pala fantasma con basis completa
          const pad = G.controllerPaddles[G.paddleHand];
          pad.active = true; pad.cooldown = 0; pad.serveFlight = false; pad.extraReach = 0;
          pad.who = 'player'; pad.index = G.paddleHand;
          pad.normal = new V3(0, 0, 1); pad.up = new V3(0, 1, 0); pad.right = new V3(1, 0, 0);
          pad.prevNormal = pad.normal.clone(); pad.prevRight = pad.right.clone();
          pad.prevUp = pad.up.clone();
          pad.omega = pad.omega || new V3(); pad.omega.set(0, 0, 0);
          pad.vel = pad.vel || new V3();
          const BCU = (window.__ppDebug.DIMS.bladeCenterUp) || 0.14;
          const BC = new V3(0.28, 1.2, 0);
          pad.pos.copy(BC).addScaledVector(pad.up, -BCU);
          pad.prev.copy(pad.pos);
          // disparo enemigo con telegrafía y zona segura de cabeza
          const d0 = E.drones.find(d => d.alive);
          d0.shootT = 0; E.step(0.05); d0.chargeT = 0.01; E.step(0.05);
          const orbe = E.orbes.find(o => o.alive && o.owner === 'enemigo');
          out.disparo = !!orbe && Math.abs(orbe.vel.length() - 9) < 0.1;
          G.camera.getWorldPosition(E._tmpC);
          const dir = orbe.vel.clone().normalize();
          const t2 = Math.max(0, E._tmpC.clone().sub(orbe.mesh.position).dot(dir));
          out.zonaSegura = orbe.mesh.position.clone().addScaledVector(dir, t2).distanceTo(E._tmpC) > 0.35;
          // golpeo vía barrido CCD del núcleo
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, 5.5); orbe.spin.set(0, 0, 0);
          pad.vel.set(0, 0, -3);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.golpeo = orbe.alive && orbe.owner === 'jugador' && orbe.vel.z < 0;
          out.limpio = orbe.clean === true && E.sobrecarga > 0;
          // perforante
          E.sobrecarga = 1;
          orbe.mesh.position.copy(BC).add(new V3(0, 0, -0.2));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, 5.5);
          orbe.owner = 'enemigo'; orbe.perf = false; orbe.clean = false;
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.perforante = orbe.perf === true && E.sobrecarga === 0;
          // destrucción de dron
          orbe.mesh.position.copy(d0.pos).add(new V3(0, 0, 0.15));
          orbe.prev.copy(orbe.mesh.position); orbe.vel.set(0, 0, -6);
          orbe.owner = 'jugador'; orbe.perf = false;
          E._orbesStep(0.03);
          out.dronCae = !d0.alive;
          // fase completa → interludio (+30) → fase 2 con Centinela
          for (const dd of E.drones) if (dd.alive) E._dronMuere(dd);
          out.inter = E.phase === 'inter';
          for (let i = 0; i < 60; i++) E.step(0.1);
          out.fase2 = E.fase === 1 && E.drones.filter(d => d.alive).length === 4 && E.centOn;
          // v3.5.1 · DETERMINISMO: fuera del reloj de combate no puede haber
          // orbes ajenos en vuelo (disparos aleatorios de drones/Centinela
          // durante los 60 steps contaminaban el pool del test)
          for (const oo of E.orbes) {
            if (oo.alive) { oo.alive = false; oo.mesh.visible = false;
              if (oo.glow) oo.glow.visible = false; }
          }
          E.centSobreT = 0;
          // rally: rebote del escudo → 5 devoluciones → núcleo expuesto → muere
          const o2 = E.orbes.find(o => !o.alive);
          o2.alive = true; o2.owner = 'jugador'; o2.tipo = 'std'; o2.r = 0.05;
          o2.fuse = -1; o2.perf = false; o2.clean = false; o2.rebote = false;
          o2.mesh.visible = true; o2.glow.visible = true; o2.pos = o2.mesh.position;
          o2.mesh.position.set(0, E.cent.position.y, E.cent.position.z + 0.55);
          o2.prev.copy(o2.mesh.position); o2.vel.set(0, 0, -6);
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.05);
          out.reboteCent = o2.alive && o2.owner === 'enemigo' && o2.rebote;
          const v0 = 6;
          out.velGanada = o2.alive ? o2.vel.length() > v0 : false;
          for (let k = 0; k < 5; k++) E._rallySube();
          out.expuesto = E.centSobreT > 0;
          o2.mesh.position.copy(E.cent.position); o2.prev.copy(o2.mesh.position);
          o2.vel.set(0, 0, -4); o2.owner = 'jugador'; o2.rebote = false;
          E._cdT = 0; E._cdO = null;
          E._orbesStep(0.03);
          out.centCae = E.centDead;
          for (const dd of E.drones) if (dd.alive) E._dronMuere(dd);
          for (let i = 0; i < 60; i++) E.step(0.1);
          out.fase3 = E.fase === 2 && E.jefeOn;
          for (let i = 0; i < 50; i++) E.step(0.1);
          out.canon = E.jefeCanon >= 0;
          if (E.jefeCanon >= 0) {
            const cA = E.canones[E.jefeCanon];
            E._jefeCanonDano(cA, 2, true);
            out.canon2HP = cA.hp === 1;   // 3 HP − 2 (golpe limpio) = 1
          }
          // barrera: daño por tipo + onda
          const o3 = E.orbes.find(o => !o.alive);
          o3.alive = true; o3.owner = 'enemigo'; o3.tipo = 'pesado'; o3.r = 0.09;
          o3.mesh.visible = true; o3.glow.visible = true; o3.pos = o3.mesh.position;
          o3.mesh.position.set(0.4, 1.4, 1.5); o3.prev.copy(o3.mesh.position);
          o3.vel.set(0, 0, 3);
          const h0 = E.hull;
          E._orbesStep(0.2);
          out.barrera25 = E.hull === h0 - 25 && E.ondas.some(w => w.m.visible);
          // VICTORIA final: los 3 cañones
          for (const c of E.canones) if (!c.dead) E._jefeCanonDano(c, 3, false);
          out.victoria = E.phase === 'result' && E._win === true && !E.jefe.visible;
          for (let i = 0; i < 70; i++) E.step(0.1);
          out.regresa = ctrl.state === 'sala' && !E.active && G.roomGroup.visible &&
                        G.tableGroup.visible && G.ballMesh.visible &&
                        G.champDecorHidden === false &&
                        Math.abs(ctrl.rivalMesh.position.x - 1.26) < 1e-3;
          return out;
        }""")
        for k, d in (
            ('arranque', 'arranque: fase PREPARACIÓN'),
            ('sala', 'sala propia SIN mesa/rival/bola/marcador/recortes'),
            ('fase1', 'fase 1: 3 drones artilleros'),
            ('disparo', 'disparo enemigo a 9 m/s (fase 1) con telegrafía'),
            ('zonaSegura', 'ningún disparo apunta a la zona segura de cabeza'),
            ('golpeo', 'la pala devuelve por el BARRIDO CCD del núcleo'),
            ('limpio', 'golpe limpio → +Sobrecarga'),
            ('perforante', 'Sobrecarga 100 % + golpe firme → orbe perforante'),
            ('dronCae', 'orbe devuelto destruye el dron (una vez)'),
            ('inter', 'fin de fase → interludio'),
            ('fase2', 'fase 2: 4 drones + Centinela'),
            ('reboteCent', 'el escudo del Centinela REBOTA el orbe'),
            ('velGanada', 'rebote con +10 % de velocidad'),
            ('expuesto', 'rally 5 → núcleo expuesto 3 s'),
            ('centCae', 'núcleo expuesto + orbe → Centinela destruido'),
            ('fase3', 'fase 3: nave abordadora'),
            ('canon', 'jefe: cañón activo tras la entrada'),
            ('canon2HP', 'golpe limpio = 2 HP (cañón cae)'),
            ('barrera25', 'barrera: pesado = −25 con onda en el punto'),
            ('victoria', 'victoria final: 3 cañones → jefe explota'),
            ('regresa', 'regreso a la sala con todo restaurado'),
        ):
            chk(bool(esc.get(k)), f'{d} ({k})')
        if esc.get('estado'):
            print('   estado:', esc['estado'])

        print('== Capturas de evidencia ==')
        shot = await page.evaluate("""async () => {
          const G = window.__PP_GAME;
          const ctrl = G.champs.moduleIfLoaded('estacion_orbital').controller;
          ctrl.stage = 3;
          ctrl._arrancarEscudo(ctrl._etapa());
          const E = ctrl.escudo;
          for (let i = 0; i < 40; i++) E.step(0.1);
          try { G.hideChampIntro(false); } catch (e) { /* */ }
          for (let k = 0; k < 100; k++) {
            const ok2 = E.grp.children.every(m => !m.material || !m.material.map ||
              (m.material.map.image && m.material.map.image.width));
            if (ok2) break;
            await new Promise(r => setTimeout(r, 100));
          }
          await new Promise(r => setTimeout(r, 500));
          const c = G.camera;
          c.parent && c.parent.remove(c);
          G.scene.add(c);
          c.position.set(0, 1.62, 0.4);
          c.lookAt(0, 1.6, -9);
          c.fov = 75; c.aspect = 1280 / 800; c.updateProjectionMatrix();
          G.renderer.render(G.scene, c);
          return G.renderer.domElement.toDataURL('image/png');
        }""")
        with open('/home/z/my-project/download/qa_esc1_sala.png', 'wb') as f:
            f.write(base64.b64decode(shot.split(',', 1)[1]))
        chk(True, 'captura qa_esc1_sala.png')

        print('== Limpieza ==')
        chk(not errors, f'0 pageerrors dev ({len(errors)}): {errors[:2]}')
        await page.screenshot(path='/home/z/my-project/download/qa_esc1_portada.png')
        await browser.close()

    print('\n== GATEWAY (:81) ==')
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        pg2 = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errors2 = []
        pg2.on('pageerror', lambda e: errors2.append(str(e)))
        await pg2.goto(GW + '/game.html', wait_until='domcontentloaded')
        await pg2.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=45000)
        chk(await pg2.evaluate("window.__PP_VERSION") == '3.6.8-SDK6', 'gateway: __PP_VERSION 3.6.8-SDK6')
        chk(await pg2.evaluate("typeof window.__PP_PADDLE_SWEEP === 'function'"), 'gateway: puente CCD')
        chk(await pg2.evaluate("!!window.__PP_GAME"), 'gateway: juego arranca')
        chk(not errors2, f'0 pageerrors gateway ({len(errors2)}): {errors2[:2]}')
        await browser.close()

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    sys.exit(1 if fails else 0)

asyncio.run(main())
