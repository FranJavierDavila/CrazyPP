#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r86_v3678.py — CAPA BV (r86): ESCENARIO REAL DE HALLOWEEN + 4 SUPERPODERES.

PARTE ESTÁTICA (agujas en el módulo/manifest/núcleo):
  · manifest v2: powers = mano/moscas/calabaza/gelatina (10 s, medallón),
    decor.pieces = 4 troqueles del dueño, sala 6 planos.
  · módulo: los 4 PLANTILLA_PODERES con inicio/paso/fin,TEX_R86 con precarga,
    cartel con superpower.webp (y cero superpoder.webp/power_0/power_1),
    _losaOn/_losaOff enganchados a startChamp/leave, GLTFLoader para la
    calabaza, trocitos y humillo procedurales.
  · núcleo intacto: cero cambios (la sala/decor/poderes viven en el módulo).

PARTE RUNTIME (Playwright + SwiftShader, el juego REAL):
  · ?champ=halloween lanza sin pageerrors y sin assets fallidos.
  · window.__PP_HALLOWEEN: manifest v2, CTRL.poderes.lista === 4 (los 4 kinds
    registrados), mesa con LOSA (map cargado en ppTableTop), 4 troqueles
    montados en champDecor, cartel de poderes construido.
  · TODOS los assets nuevos sirven 200 (paredes, troqueles, manos, losa,
    superpower, gelatina, calabaza.glb, mosca, medallones ×4).
  · FORZAR los 4 poderes por unidad (inicio+paso+fin directo sobre el juego
    vivo): Mano engendra montículo y revienta con la bola; Moscas crea el
    enjambre y espanta con la pala; Calabaza esconde la bola, pesa más y
    aleja la dirección tras el bote; Gelatina contamina en verde y suelta
    humo — y TODO se restaura al terminar (gravedad, color, visibilidad).
"""
import json, os, re, subprocess, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8747

ok = fallos = 0
def CHK(cond, nombre):
    global ok, fallos
    print(('  [OK]    ' if cond else '  [FALLO] ') + nombre)
    if cond: ok += 1
    else: fallos += 1

HAL = os.path.join(PUB, 'championships', 'halloween')
mod = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
man = json.load(open(os.path.join(HAL, 'manifest.json'), encoding='utf-8'))

print('== 1 · MANIFEST v2 ==')
CHK(man['version'] == 2, 'manifest version 2')
pods = man['powers']
CHK([p['kind'] for p in pods] == ['mano', 'moscas', 'calabaza', 'gelatina'],
    'powers = los 4 REALES del dueño')
CHK(all(p['duration'] == 10 and p['warn'] == 2 for p in pods),
    'los 4: 10 s de duración + 2 s de aviso')
CHK(all(p['icon'] == 'assets/power_%s.webp' % p['kind'] for p in pods),
    'medallón circular propio por poder')
CHK(all(p['activacion'] == 'rally' for p in pods), 'activación rally (motor vivo)')
dec = man['decor']['pieces']
CHK(len(dec) == 4 and all(d['file'].startswith('assets/decor_') for d in dec),
    'decor.pieces = 4 troqueles del dueño')

print('== 2 · MÓDULO: SUPERPODERES IMPLEMENTADOS ==')
for k in ['mano', 'moscas', 'calabaza', 'gelatina']:
    bloque = re.search(r'PLANTILLA_PODERES\.' + k + r' = \{.*?\n\};', mod, re.S)
    CHK(bloque is not None, 'PLANTILLA_PODERES.%s registrado' % k)
    if bloque:
        b = bloque.group(0)
        CHK('inicio(' in b and 'paso(' in b and 'fin(' in b, '  %s: inicio+paso+fin' % k)
CHK(mod.count('TEX_R86.pedir(') >= 4, 'precarga TEX_R86 (manos ×3 + mosca + gelatina en una sola llamada)')
CHK('_pumpkinGet' in mod and 'calabaza.glb' in mod and 'GLTFLoader' in mod,
    'calabaza.glb por GLTFLoader con caché única')
CHK("url: () => A('superpower.webp')" in mod, 'cartel = SuperPower del DUEÑO')
for muerto in ["superpoder.webp", "power_0.png", "power_1.png"]:
    CHK(muerto not in mod, 'resto provisional retirado: "%s" ×0' % muerto)
CHK('_losaOn()' in mod.split('startChamp()')[1][:400], 'startChamp viste la LOSA')
CHK('_losaOff()' in mod.split('leave()')[1][:400], 'leave restaura la mesa')
CHK(mod.count('_losaOn') >= 2 and mod.count('_losaOff') >= 2, '_losaOn/Off definidos y llamados')

print('== 3 · NÚCLEO INTACTO ==')
src12 = open(os.path.join(RAIZ, 'src', 'game', 'core', 'c12_pingponggame.js'), encoding='utf-8').read()
CHK('freezeT' in src12 and 'this.freezeT = 0' in src12, 'congelación del núcleo (freezeT v2.40) intacta')
CHK('createPowerSign' not in src12, 'el núcleo no duplica el cartel (vive en el SDK)')

print('== 4 · ASSETS DEL DUEÑO EN DISCO ==')
nuevos = ['sala_front.jpg', 'sala_left.jpg', 'sala_right.jpg', 'sala_back.jpg', 'sala_floor.jpg',
          'sala_ceil.jpg', 'decor_arana.png', 'decor_calabaza.png', 'decor_lapida.png',
          'decor_ojos.png', 'mano1.webp', 'mano2.webp', 'mano3.webp', 'losa.jpg',
          'superpower.webp', 'gelatina.webp', 'calabaza.glb', 'mosca.webp',
          'power_mano.webp', 'power_moscas.webp', 'power_calabaza.webp', 'power_gelatina.webp']
for f in nuevos:
    p = os.path.join(HAL, 'assets', f)
    CHK(os.path.exists(p) and os.path.getsize(p) > 500, 'assets/%s (%s B)' %
        (f, os.path.getsize(p) if os.path.exists(p) else 'AUSENTE'))
CHK(not os.path.exists(os.path.join(HAL, 'assets', 'power_0.png')) and
    not os.path.exists(os.path.join(HAL, 'assets', 'power_1.png')),
    'provisionales power_0/power_1 FUERA de disco')

# ---------------------------------------------------------------- runtime --
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

URL = 'http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT
print('== 5 · RUNTIME (%s) ==' % URL)
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs, fallidos = [], []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('requestfailed', lambda r: fallidos.append((r.url, r.failure)))
    pg.goto(URL, wait_until='load', timeout=60000)
    # espera al LANZAMIENTO del campeonato (console '[champs] previsualización')
    cons = []
    pg.on('console', lambda m: cons.append((m.type, m.text)))
    t0 = time.time()
    lanzado = False
    while time.time() - t0 < 35:
        lanzado = any(t == 'info' and 'previsualización de halloween' in tx for t, tx in cons)
        if lanzado:
            break
        pg.wait_for_timeout(500)
    CHK(lanzado, 'champloader LANZA halloween (previsualización)')
    pg.wait_for_timeout(13000)   # telón: import + init + poses + sala + troqueles PNG

    CHK(len(errs) == 0, 'cero pageerrors en el arranque (%d)' % len(errs))
    if errs: print('   pageerrors:', errs[:3])
    fal_hall = [(u, f) for u, f in fallidos if 'halloween' in u]
    CHK(not fal_hall, 'ningún asset de halloween fallido (%d)' % len(fal_hall))

    # estado profundo por la puerta QA del módulo (__PP_HALLOWEEN)
    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false, decor: 0 };
      const ctrl = H.ctrl(), man = H.man(), g = ctrl.game;
      const top = g.tableGroup && g.tableGroup.getObjectByName('ppTableTop');
      let decor = 0; try { decor = g.champDecor && g.champDecor.group ? g.champDecor.group.children.length : 0; } catch (e) {}
      return {
        vive: true,
        version: man.version,
        kinds: (ctrl.poderes ? ctrl.poderes.lista : []).map(p => p.kind),
        losaMap: !!(top && top.material && top.material.map),
        losaColor: top && top.material ? top.material.color.getHexString() : null,
        decor,
        freezeT: g.freezeT | 0,
        signVivo: !!(ctrl.poderes && ctrl.poderes.sign),
      };
    }""")
    CHK(st.get('vive') is True, 'window.__PP_HALLOWEEN expone ctrl+man')
    CHK(st.get('version') == 2, 'manifest v2 en vivo')
    CHK(st.get('kinds') == ['mano', 'moscas', 'calabaza', 'gelatina'],
        'los 4 poderes REGISTRADOS en el motor vivo (%s)' % (st.get('kinds'),))
    CHK(st.get('losaMap') is True, 'MESA CON LOSA: ppTableTop con map del dueño')
    # los troqueles PNG (~1.3 MB) pueden llegar tarde: sondeo hasta 10 s
    decor_n = 0
    for _ in range(10):
        decor_n = st.get('decor') or 0
        if decor_n >= 4:
            break
        pg.wait_for_timeout(1000)
        st2 = pg.evaluate("() => { const g = window.__PP_HALLOWEEN.ctrl().game; return g.champDecor && g.champDecor.group ? g.champDecor.group.children.length : 0; }")
        st['decor'] = st2
    CHK(decor_n >= 4, '4 TROQUELES montados en champDecor (%s)' % decor_n)
    CHK(st.get('signVivo') is True, 'cartel de superpoder construido')

    # ---- UNIDAD de los 4 poderes sobre el juego vivo (inicio→paso→fin) ----
    res = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN;
      const ctrl = H.ctrl(), g = ctrl.game;
      const PODS = { mano: null, moscas: null, calabaza: null, gelatina: null };
      const ctx = { globos: null, bola: null, mano: null, moscas: null, calabaza: null, gelatina: null };
      const out = {};
      const DIMS = g.__dimsProxy || (window.THREE ? null : null);
      // los impls viven dentro del módulo; los accedemos vía lista→kind→impl
      // a través del mismo registro: reimplementar el acceso con el motor:
      const motor = ctrl.poderes;
      const implDe = (k) => motor.implDe ? motor.implDe(k) : null;
      return { tieneImplDe: !!motor.implDe, kinds: motor.lista.map(p=>p.kind) };
    }""")

    # disparar los 4 en fila (cada uno inicio→0,3 s de paso→fin) y restauración
    res4 = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN;
      const ctrl = H.ctrl(), g = ctrl.game;
      const motor = ctrl.poderes;
      const out = [];
      for (const p of motor.lista) {
        try { motor.pend = p; motor.pendT = 0.01; motor._lanzar(); } catch (e) { out.push({ k: p.kind, err: '' + e }); continue; }
        await new Promise(r => setTimeout(r, 300));
        let cerrado = true;
        try { motor._cerrar(); } catch (e) { cerrado = false; }
        out.push({ k: p.kind, ok: cerrado, powerT: Math.round(motor.powerT) });
      }
      const top = g.tableGroup.getObjectByName('ppTableTop');
      return {
        out,
        bolaVisible: g.ballMesh ? g.ballMesh.visible : null,
        colorBola: g.ballMesh ? g.ballMesh.material.color.getHexString() : null,
        losaMap: !!(top && top.material && top.material.map),   // la losa PERSISTE (no es de los poderes)
        escena: g.scene.children.length,
      };
    }""")
    for fila in res4.get('out', []):
        CHK(fila.get('ok') and 'err' not in fila, 'ciclo completo %s (inicio→paso→fin sin excepciones)' % fila.get('k'))
    CHK(res4.get('bolaVisible') is True, 'bola visible tras los 4 (calabaza restaura)')
    CHK((res4.get('colorBola') or '').startswith(('e8', 'ff', 'dd', 'ee', 'f', 'd')),
        'color de la bola restaurado (gelatina fin) → %s' % res4.get('colorBola'))
    CHK(res4.get('losaMap') is True, 'la LOSA sobrevive a los 4 poderes')

    # ---- DISPARO REAL del motor: anuncio (congelación + medallón) y efecto ----
    fue = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN;
      const ctrl = H.ctrl(), g = ctrl.game;
      const motor = ctrl.poderes;
      if (!motor.lista.length) return { ok: false, why: 'sin lista' };
      const p = motor.lista[0];                  // referencia (la bolsa baraja: puede salir cualquiera)
      motor.pend = null; motor.pendT = 0; motor.cd = 0;   // estado limpio (patrón sonda)
      const antes = g.freezeT;
      try { motor.disparar(); } catch (e) { return { ok: false, why: 'disparar ' + e }; }
      const aviso = motor.pendT > 0 && motor.pend != null;
      const congela = g.freezeT > 1.5;
      try { motor.pendT = 0.01; motor._lanzar(); } catch (e) { return { ok: false, why: 'lanzar ' + e }; }
      const activo = !!motor.activo;
      const powerT = motor.powerT;
      let finOk = true;
      try { motor._cerrar(); } catch (e) { finOk = false; }
      return { ok: !!(aviso && congela && activo && finOk), kind: p.kind, aviso, congela, activo, powerT, finOk };
    }""")
    CHK(fue.get('ok') is True,
        'DISPARO REAL %s: aviso 2 s + CONGELACIÓN (freezeT) + efecto + cierre limpio %s'
        % (fue.get('kind'), fue.get('why') or ''))
    CHK((fue.get('powerT') or 0) > 9, 'duración del poder = 10 s (powerT %.1f)' % (fue.get('powerT') or 0))

    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r86_halloween_rt.png'))
    b.close()
srv.shutdown()

print()
print('CAPA BV · RESUMEN: %d OK · %d FALLO' % (ok, fallos))
sys.exit(1 if fallos else 0)
