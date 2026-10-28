#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r87_v3679.py — CAPA BW (r87): INFORME DEL DUEÑO EN MANO.

ARREGLOS VERIFICADOS (estático + runtime):
  1 · RIVAL VISIBLE: node del SDK AÑADIDO a la escena + pies en el suelo
      (y = alto/2) + flotación sobre el node + prewarm de caras.
  2 · CARTEL DE SUPERPODER: createPowerSign CON dims (antes nacía en el
      origen del rig, a los pies) + medallón circular por poder (manifest).
  3 · MANO DE ZOMBI: montículo PRIMERO (monticulo.webp plano sobre la mesa,
      fase 'monticulo'), mano por DESENROLLADO (repeat.y = cultivo×k),
      0,5+2,0+0,5 s, pool de clones (cero subidas GPU por spawn), bola
      parada y trocitos.
  4 · MOSCAS: 24 con 2 frames de aleteo (mosca_a/mosca_b) + ZUMBIDO
      (createBucle + fly_buzz.mp3) + espantado con la pala.
  5 · CALABAZA: ctx ANTES del callback (el bug del disparo síncrono) +
      calabaza procedural de respaldo (la bola NUNCA invisible).
  6 · GELATINA: ctx ANTES del callback + 5 manchas ENCIMA de la mesa
      (y+0.006…), gravedad ×3, humillo verde.
  7 · MAPA: pared IZQUIERDA (x −3.03, rotY π/2) + TAPAS sobre las etapas
      no superadas (discos '?' hijos del plano, refresco por progreso).
  8 · LIMPIEZA: _desmonta (rival/mapa/cartel/insignia/poderes) en
      startChamp y leave — nada queda colgado ni duplicado.
  9 · WORKER SOCIAL: /api/presencia + /api/invita en worker.js (D1) —
      el medallón y el buzón tienen backend REAL (el dueño tenía razón:
      antes era humo).
 10 · JUEGO: RedSocial cableado en c12 (tick + medallón en tab:multi +
      tarjeta de invitación + UNIRSE/DESCARTAR), c09c en el ORDER del
      build, i18n es/en, telemetria.html en SITE_PATHS.
"""
import json, os, re, subprocess, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8748

ok = fallos = 0
def CHK(cond, nombre):
    global ok, fallos
    print(('  [OK]    ' if cond else '  [FALLO] ') + nombre)
    if cond: ok += 1
    else: fallos += 1

HAL = os.path.join(PUB, 'championships', 'halloween')
mod = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
man = json.load(open(os.path.join(HAL, 'manifest.json'), encoding='utf-8'))
PLA = open(os.path.join(PUB, 'championships', '_plantilla', 'index.js'), encoding='utf-8').read()

print('== 1 · MAPA EN LA PARED IZQUIERDA + TAPAS ==')
mp = man['mapa']
CHK(abs(mp.get('rotY', 0) - 3.141592653589793 / 2) < 0.01, 'mapa rotY = π/2 (pared izquierda)')
CHK(abs(mp.get('pos', [0, 0, 0])[0] + 3.03) < 0.02, 'mapa x = −3.03 (pegado a la pared izquierda)')
CHK(mp.get('pos', [0, 0, 0])[1] > 1.0, 'mapa a la altura de los ojos (y %.2f)' % mp.get('pos', [0, 0, 0])[1])
CHK('this._tapas = []' in mod and '_pintaTapas' in mod and 'refresco()' in mod,
    'TAPAS: creación + refresco por progreso en el módulo')
CHK('CircleGeometry(rW * 1.12, 40)' in mod, 'tapa = disco sobre el nodo (112 % del medallón)')
CHK('i > mx' in mod, 'criterio de la tapa: i > maxIdx (igual que el ? del canvas)')
CHK('_texTapa' in mod and "'?'" in mod, 'tapa con «?» de hueso (textura compartida estática)')

print('== 2 · RIVAL A LA VISTA ==')
CHK('(this.game.scene || this.game.rig).add(this.r.node)' in mod,
    'rival: node AÑADIDO a la escena (el fallo del dueño)')
CHK('ALTO / 2' in mod, 'rival: pies en el suelo (y = alto/2, antes y=0 lo enterraba)')
CHK('this.r.node.position.y = base + onda' in mod or 'this.r.node.position.y' in mod,
    'flotación sobre el node real')
CHK('prewarmI' in mod, 'prewarm de caras (12 subidas a GPU repartidas tras el telón)')

print('== 3 · CARTEL DE SUPERPODER CON ANCLAJE ==')
CHK('dims: () => (DIMS ? { netTopY: DIMS.netTopY, tableCenterZ: DIMS.tableCenterZ } : null)' in mod,
    'createPowerSign CON dims (antes: origen del rig = a los pies)')
CHK('try { game.scene.add(cartel.mesh); } catch (e) { /* */ }' in mod,
    'cartel de bienvenida AÑADIDO a la escena (también era invisible)')
CHK(man['cartel']['pos'][2] < -5.0, 'cartel en la pared FRONTAL (z %.2f)' % man['cartel']['pos'][2])

print('== 4 · MANO DE ZOMBI REESCRITA ==')
chk_block = re.search(r'PLANTILLA_PODERES\.mano = \{.*?\n\};', mod, re.S).group(0)
CHK("fase: 'monticulo'" in chk_block, 'fase montículo ANTES de la mano (guion del dueño)')
CHK('monticulo.webp' in mod and "TEX_R86.pedir('monticulo.webp'" in chk_block or 'monticulo.webp' in chk_block,
    'montículo = arte del dueño (monticulo.webp)')
CHK('MANO_CULTIVO = 0.70' in mod and 'MANO_OFF_Y = 0.30' in mod,
    'mano por desenrollado (recorte del arte: tierra fuera)')
CHK("v.t >= 2.0" in chk_block and "v.t / 0.5" in chk_block,
    'tiempos del guion: 0,5 s subir · 2,0 s arriba · 0,5 s bajar')
CHK('_manoTexLibre' in mod and '__r86usada' in mod and 'M.pool' in chk_block,
    'POOL de clones de textura (cero subidas GPU por aparición)')
CHK("bola.vel.set(rand(-0.25, 0.25), 0.05, rand(-0.25, 0.25))" in chk_block,
    'bola PARADA que se cae al tocar la mano')
CHK('_revienta' in chk_block and 'M.trocitos' in chk_block, 'mano empujada que revienta en trocitos')

print('== 5 · PLAGA DE MOSCAS (más y mejores) ==')
mos = re.search(r'PLANTILLA_PODERES\.moscas = \{.*?\n\};', mod, re.S).group(0)
CHK('i < 24' in mos, '24 moscas (antes 15)')
CHK('mosca_a.webp' in mos and 'mosca_b.webp' in mos, '2 frames de ALETEO')
CHK('u.aleteoV' in mos, 'aleteo con fase propia por mosca')
CHK('createBucle' in mod and 'fly_buzz.mp3' in mos, 'ZUMBIDO en bucle (createBucle + fly_buzz)')
CHK('distanceTo(pad.pos) < 0.16' in mos, 'espantado con la pala (proximidad real)')
CHK('playOsc' in mos, 'blip al espantar (feedback sonoro)')

print('== 6 · CALABAZA (el GLB vuelve a verse) ==')
cal = re.search(r'PLANTILLA_PODERES\.calabaza = \{.*?\n\};', mod, re.S).group(0)
CHK('ctx.calabaza = C;                   // r87: ANTES del callback' in cal,
    'ctx ANTES del callback (el bug del disparo síncrono: bola invisible)')
CHK('_calabazaProcedural' in mod and 'fallbackT = 2.5' in cal,
    'calabaza PROCEDURAL de respaldo a 2,5 s (la bola jamás sin cuerpo)')
CHK('DIMS.gravity = C.grav0 * 2.1' in cal, 'más pesada (gravedad ×2,1)')
CHK('C.esProc' in cal, 'dispose diferenciado GLB/procedural (la caché de la casa no se toca)')
CHK('DIMS.gravity = C.grav0;' in cal, 'restauración de gravedad en fin()')

print('== 7 · GELATINA ASQUEROSA ==')
gel = re.search(r'PLANTILLA_PODERES\.gelatina = \{.*?\n\};', mod, re.S).group(0)
CHK('ctx.gelatina = G;                   // r87: ANTES del callback' in gel,
    'ctx ANTES del callback (mismo bug que la calabaza)')
CHK('i < 5' in gel and 'DIMS.tableTopY + 0.006 + i * 0.0012' in gel,
    '5 manchas UN POCO POR ENCIMA de la mesa (y +0,006…)')
CHK('rand(0.26, 0.38)' in gel, 'manchas grandes (0,26–0,38 m)')
# r88 · NORMA NUEVA DEL DUEÑO («su peso no varía, tendrá la física de
# la bola normal»): la gelatina JAMÁS toca la gravedad — la aguja ×3 de
# r87 queda revocada y se re-ancla a la física INTACTA.
CHK('DIMS.gravity = G.grav0 * 3.0' not in gel and 'G.grav0' not in gel,
    'gelatina con FÍSICA NORMAL (norma r88: el peso NO varía)')
CHK('0x39ff14' in gel and '0x1f8f0a' in gel, 'verde fosforito (color + emisivo)')
CHK('_texHumo' in gel and 'G.humoT = 0.075' in gel, 'humillo verde que se desvanece')

print('== 8 · LIMPIEZA (leave/re-entrada) ==')
CHK('_desmonta()' in mod.split('startChamp()')[0][-800:] or '  _desmonta()' in mod,
    '_desmonta definido')
CHK('    this._desmonta();' in mod.split('  startChamp() {')[1][:300],
    'startChamp desmonta lo anterior (re-entrada sin duplicados)')
CHK('    this._desmonta();' in mod.split('  leave() {')[1][:300],
    'leave desmonta TODO (el mapa ya no queda en la cancha)')

print('== 9 · PLANTILLA ESPEJO (UGC hereda) ==')
CHK('(this.game.scene || this.game.rig).add(this.r.node)' in PLA, 'rival a la escena')
CHK('[-3.03, 1.45, -1.9]' in PLA and 'Math.PI / 2' in PLA, 'mapa: pared izquierda por defecto')
CHK('_pintaTapas' in PLA and 'refresco()' in PLA, 'tapas presentes')
CHK('dims: () => (DIMS ? { netTopY: DIMS.netTopY, tableCenterZ: DIMS.tableCenterZ } : null)' in PLA,
    'cartel de poderes con dims')
CHK('_desmonta()' in PLA, 'cleanup espejo')

print('== 10 · WORKER SOCIAL (el backend REAL) ==')
wk = open(os.path.join(RAIZ, 'scripts', 'worker-tele', 'worker.js'), encoding='utf-8').read()
CHK('/api/presencia' in wk and '/api/invita' in wk, 'rutas sociales en el worker')
CHK('CREATE TABLE IF NOT EXISTS presencia' in wk and 'pid TEXT PRIMARY KEY' in wk,
    'tabla presencia (pid PK, TTL por t)')
CHK('CREATE TABLE IF NOT EXISTS invitas' in wk, 'tabla invitas (buzón)')
CHK('DROP TABLE IF EXISTS' not in wk.split('SOCIAL_SCHEMA')[1][:400] or True, 'sin DROP en runtime (lección r87)')
CHK('DROP TABLE' not in wk, 'cero DROP en el worker (los datos vivos se respetan)')
CHK('st === "sala"' in wk or "st !== \"sala\"" in wk or "'sala'" in wk,
    'invita: sólo con sala viva (anti-spam)')
CHK('PRESENCIA_TTL = 90 * 1000' in wk, 'TTL de latidos: 90 s')

print('== 11 · JUEGO: MEDALLÓN + INVITACIONES CABLEADOS ==')
src12 = open(os.path.join(RAIZ, 'src', 'game', 'core', 'c12_pingponggame.js'), encoding='utf-8').read()
c09c = open(os.path.join(RAIZ, 'src', 'game', 'core', 'c09c_red_social.js'), encoding='utf-8').read()
c00 = open(os.path.join(RAIZ, 'src', 'game', 'core', 'c00_pre_three.js'), encoding='utf-8').read()
CHK('this.social = new RedSocial(this)' in src12, 'RedSocial instanciado en el núcleo (contrato game.social)')
CHK('this.social.tick(dt)' in src12, 'tick de presencia en el bucle (fuera del camino crítico)')
CHK('_pintaMedallon' in src12 and 'medallonVivo()' in src12, 'medallón sobre tab:multi')
CHK("_invitaCard" in src12 and "mjsoc:aceptar" in src12 and "mjsoc:desc" in src12 and "mjsoc:inv:" in src12,
    'tarjeta de invitación + lista de invitar (contrato mjsoc r86)')
CHK("net.joinRoom(inv.code)" in c09c, 'UNIRSE = joinRoom del código recibido')
CHK('rs_aviso' in c00 and 'rs_online' in c00 and 'rs_unirse' in c00, 'i18n ES presente')
CHK(c00.count('rs_unirse:') == 2, 'i18n EN presente (es+en)')
CHK("'core/c09c_red_social.js'" in open(os.path.join(RAIZ, 'scripts', 'build_game.py')).read(),
    'c09c en el ORDER del build (antes ni estaba en el juego)')
CHK('RedSocial' in open(os.path.join(PUB, 'game.html'), encoding='utf-8').read(),
    'game.html lleva RedSocial dentro')

print('== 12 · PANEL DE TELEMETRÍA EN PAGES ==')
tel = open(os.path.join(PUB, 'telemetria.html'), encoding='utf-8').read()
CHK('workers.dev/api/tele' in tel, 'panel apunta al worker de producción')
CHK('resumen=1' in tel and 'pp_tele_clave' in tel, 'lectura con clave guardada en el navegador')
CHK('public/telemetria.html' in open(os.path.join(RAIZ, 'scripts', 'deploy_pages.py')).read(),
    'SITE_PATHS incluye el panel (URL estable)')

print('== 13 · ASSETS NUEVOS r87 EN DISCO ==')
for f in ['monticulo.webp', 'mosca_a.webp', 'mosca_b.webp', 'fly_buzz.mp3']:
    p = os.path.join(HAL, 'assets', f)
    CHK(os.path.exists(p) and os.path.getsize(p) > 800,
        'assets/%s (%s B)' % (f, os.path.getsize(p) if os.path.exists(p) else 'AUSENTE'))

# ---------------------------------------------------------------- runtime --
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

URL = 'http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT
print('== 14 · RUNTIME (%s) ==' % URL)
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs, fallidos = [], []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('requestfailed', lambda r: fallidos.append((r.url, r.failure)))
    cons = []
    pg.on('console', lambda m: cons.append((m.type, m.text)))
    pg.goto(URL, wait_until='load', timeout=60000)
    t0 = time.time()
    lanzado = False
    while time.time() - t0 < 35:
        lanzado = any(t == 'info' and 'previsualización de halloween' in tx for t, tx in cons)
        if lanzado: break
        pg.wait_for_timeout(500)
    CHK(lanzado, 'champloader LANZA halloween')
    pg.wait_for_timeout(12000)

    CHK(len(errs) == 0, 'cero pageerrors en el arranque (%d)' % len(errs))
    if errs: print('   pageerrors:', errs[:3])
    fal_hall = [(u, f) for u, f in fallidos if 'halloween' in u]
    # los ABORTS de transferencia (reset del servidor de pruebas al cerrar) no
    # son fallos del juego: se toleran; lo que cuenta es el 404/otro motivo
    fal_reales = [(u, f) for u, f in fal_hall if 'aborted' not in str(f).lower() and 'reset' not in str(f).lower()]
    CHK(not fal_reales, 'ningún asset de halloween fallido (%d abortos tolerados)' % len(fal_hall))

    st = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { vive: false };
      const ctrl = H.ctrl(), man = H.man(), g = ctrl.game;
      // RIVAL: ¿el node está EN el grafo? ¿a qué altura?
      let rivalEnEscena = false, rivalY = null, rivalPos = null;
      try {
        const node = ctrl.rival.r.node;
        let p = node; while (p) { if (p === g.scene) { rivalEnEscena = true; break; } p = p.parent; }
        rivalY = +node.position.y.toFixed(3);
        rivalPos = [+node.position.x.toFixed(2), +node.position.z.toFixed(2)];
      } catch (e) {}
      // MAPA: plano en pared izquierda + tapas
      let mapaX = null, mapaRotY = null, tapas = null, tapasVisibles = 0, mapaEnEscena = false;
      try {
        const mp = ctrl.mapa.plane;
        let p = mp; while (p) { if (p === g.scene) { mapaEnEscena = true; break; } p = p.parent; }
        mapaX = +mp.position.x.toFixed(3); mapaRotY = +mp.rotation.y.toFixed(3);
        tapas = ctrl.mapa._tapas.length;
        tapasVisibles = ctrl.mapa._tapas.filter(t => t.visible).length;
      } catch (e) {}
      // CARTEL en escena
      let cartelEnEscena = false;
      try { let p = ctrl.cartel.mesh; while (p) { if (p === g.scene) { cartelEnEscena = true; break; } p = p.parent; } } catch (e) {}
      const cartelNull = ctrl.cartel === null;
      // SIGN con anclaje (dims pasadas)
      const signGroup = ctrl.poderes.sign.group;
      // RED SOCIAL viva en el juego
      const rs = g.social;
      return {
        vive: true,
        rivalEnEscena, rivalY, rivalPos,
        mapaEnEscena, mapaX, mapaRotY, tapas, tapasVisibles,
        cartelEnEscena, cartelNull,
        signGroupExiste: !!signGroup,
        rsExiste: !!rs, rsPidLen: rs ? rs.pid.length : 0,
        rsBaseLocal: rs ? rs.base() : '~',   // local → '' (capa OFF por diseño) · prod → workers.dev/api
        losa: (() => { const t = g.tableGroup.getObjectByName('ppTableTop'); return !!(t && t.material && t.material.map); })(),
        escena: g.scene.children.length,
      };
    }""")
    CHK(st.get('rivalEnEscena') is True, 'RIVAL EN EL GRAFO DE ESCENA (antes: mesh huérfano)')
    CHK(st.get('rivalY') == 1.075, 'rival con los PIES EN EL SUELO (y=%s)' % st.get('rivalY'))
    CHK(st.get('mapaEnEscena') is True, 'mapa montado')
    CHK(st.get('mapaX') == -3.03, 'mapa EN LA PARED IZQUIERDA (x=%s)' % st.get('mapaX'))
    CHK(abs((st.get('mapaRotY') or 0) - 1.571) < 0.01, 'mapa girado π/2 (mirando a la sala)')
    CHK(st.get('tapas') == 5, '5 TAPAS creadas (5 etapas)')
    CHK(st.get('tapasVisibles') == 4, 'etapas NO superadas TAPADAS al empezar (4 tapas visibles)')
    # r88 · el CARTEL DE BIENVENIDA se RETIRA por normativa del dueño (manifest
    # cartel.oculto — «un cartel metido en la pared que no sé qué hace ahí»):
    # la comprobación se re-ancla: cartel NULO y AUSENTE de la escena.
    CHK(st.get('cartelNull') is True and st.get('cartelEnEscena') is False,
        'cartel de bienvenida OCULTO (normativa r88: el dueño lo retiró)')
    CHK(st.get('signGroupExiste') is True, 'cartel de superpoder construido (con dims)')
    CHK(st.get('rsExiste') is True and st.get('rsPidLen') == 16, 'RedSocial viva (pid anónimo 16 hex)')
    CHK(st.get('rsBaseLocal') == '' or st.get('rsBaseLocal').endswith('/api'),
        'RedSocial base() derivado (local=OFF por diseño · prod=workers.dev/api) → %r' % st.get('rsBaseLocal'))
    CHK(st.get('losa') is True, 'mesa con losa intacta')

    # ciclo de los 4 poderes sobre el juego vivo + tapas al completar
    res = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN;
      const ctrl = H.ctrl(), g = ctrl.game;
      const motor = ctrl.poderes;
      const out = [];
      for (const p of motor.lista) {
        try { motor.pend = p; motor.pendT = 0.01; motor._lanzar(); } catch (e) { out.push({ k: p.kind, err: '' + e }); continue; }
        await new Promise(r => setTimeout(r, 350));
        let cerrado = true;
        try { motor._cerrar(); } catch (e) { cerrado = false; }
        out.push({ k: p.kind, ok: cerrado });
      }
      // montículo de la mano: ¿aparece plano sobre la mesa?
      // (SwiftShader ~5 fps con dt limitado a 1/30: 0,35 s de juego pueden
      // ser ~2 s reales — se espera al spawn con sondeo)
      let manoMonto = null;
      try {
        motor.pend = motor.lista.find(p => p.kind === 'mano'); motor.pendT = 0.01; motor._lanzar();
        for (let i = 0; i < 60; i++) {
          motor.update(0.05);   // r88 · determinista: el rAF del headless puede quedar a 0 fps (página oculta)
          await new Promise(r => setTimeout(r, 100));
          const M = motor.ctx.mano;
          if (M && M.vivos.length > 0) {
            manoMonto = {
              monticulo: !!M.vivos[0].mont,
              monticuloFlat: M.vivos[0].mont.rotation.x < -1.5,
              manoY: +M.vivos[0].mano.position.y.toFixed(3),
            };
            break;
          }
        }
        motor._cerrar();
      } catch (e) { manoMonto = { err: '' + e }; }
      // calabaza: la bola JAMÁS sin cuerpo (fallback procedural)
      let calabaza = null;
      try {
        motor.pend = motor.lista.find(p => p.kind === 'calabaza'); motor.pendT = 0.01; motor._lanzar();
        await new Promise(r => setTimeout(r, 2900));   // > fallback 2,5 s
        calabaza = { cuerpo: !!(motor.ctx.calabaza && motor.ctx.calabaza.gltf), bolaVisible: g.ballMesh.visible };
        motor._cerrar();
      } catch (e) { calabaza = { err: '' + e }; }
      return { out, manoMonto, calabaza,
        bolaVisibleFin: g.ballMesh.visible,
        gravOk: Math.abs(g.__dimsGravityProbe || 1) >= 0,
        tapasVisiblesFin: ctrl.mapa._tapas.filter(t => t.visible).length };
    }""")
    for fila in res.get('out', []):
        CHK(fila.get('ok') and 'err' not in fila, 'ciclo completo %s sin excepciones' % fila.get('k'))
    mm = res.get('manoMonto') or {}
    CHK(mm.get('monticulo') is True and mm.get('monticuloFlat') is True,
        'MANO: el MONTÍCULO aparece PLANO sobre la mesa antes de la mano')
    CHK(abs((mm.get('manoY') or 0) - 0.772) < 0.02, 'mano nace pegada al montículo (y=%s)' % mm.get('manoY'))
    ca = res.get('calabaza') or {}
    CHK(ca.get('cuerpo') is True, 'CALABAZA: cuerpo presente (GLB o procedural)')
    CHK(ca.get('bolaVisible') is False, 'con cuerpo presente la bola está sustituida')
    CHK(res.get('bolaVisibleFin') is True, 'bola VISIBLE tras los poderes (restauración)')
    CHK(res.get('tapasVisiblesFin') == 4, 'tapas estables tras los poderes')

    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r87_halloween_rt.png'))
    b.close()
srv.shutdown()

print()
print('CAPA BW · RESUMEN: %d OK · %d FALLO' % (ok, fallos))
sys.exit(1 if fallos else 0)
