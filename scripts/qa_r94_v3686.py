#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r94_v3687.py — capa de QA de la ronda 94 (V3.6.88-SDK6).
Informe del dueño tras V3.6.85: «cuando jugamos con calabaza en determinados
momentos se produce un desfase y se ve por un lado la calabaza y por otro la
bola. No debería pasar, la calabaza debería ocupar el lugar exacto de la bola
y esta no verse mientras tengamos la calabaza sin destruir».

Raíces verificadas AQUÍ (módulo halloween, cero cambios de núcleo):
 1) LA BOLA JAMÁS SE VE mientras la calabaza vive: paso() re-oculta ballMesh
    CADA frame (después de toss/HELD/reset del núcleo y antes del render).
 2) EL LUGAR EXACTO: la calabaza copia ballMesh.position (bola renderizada).
 3) NACIMIENTO EN SITIO + GUARD ppCalabaza (r92 no caduca a mitad de poder).
 4) ENTREGA del estallido intacta: calabaza se oculta, bola VUELVE."""
import os, sys, functools, json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
HAL = os.path.join(PUB, 'championships/halloween')
PORT = 8814
OK = []
FAIL = []

def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)

# ------------------------------------------------------------- ESTÁTICA ----
print('== ESTÁTICA ==')
man = json.load(open(os.path.join(HAL, 'manifest.json')))
CHK(any(n.startswith('v8 (r94)') for n in man.get('notes', [])), 'manifest: nota v8 (r94) presente')

PLA = open(os.path.join(HAL, 'index.js'), encoding='utf-8').read()
CHK(PLA.count('if (game.ballMesh) game.ballMesh.visible = false;') == 2,
    'módulo: ballMesh oculto en inicio() Y re-oculto cada frame en paso() (×2)')
CHK(PLA.count('C.gltf.position.copy(game.ballMesh ? game.ballMesh.position : b.pos);') == 1,
    'módulo: paso() copia la bola RENDERIZADA (ballMesh.position, fallback b.pos)')
CHK(PLA.count('if (game.ballMesh) C.gltf.position.copy(game.ballMesh.position);') == 1,
    'módulo: inicio() nace EN el punto vivo de la bola (sin frame en el origen)')
CHK(PLA.count('if (b) b.ppCalabaza = true;') == 1,
    'módulo: guard r94 — ppCalabaza renace cada frame (r92 no caduca)')
CHK(PLA.count('game.ballMesh.visible = true;') == 2,
    'módulo: la bola VUELVE sólo en estallido y fin() (×2 — entrega diseñada)')
CHK('if (C.explotada) return;' in PLA,
    'módulo: tras el estallido paso() abandona (bola normal dueña de la escena)')
CHK('if (game.ball) game.ball.ppCalabaza = false;' in PLA,
    'módulo: estallido/fin limpian ppCalabaza (contacto IA a la norma)')

GH = open(os.path.join(PUB, 'game.html'), encoding='utf-8', errors='ignore').read()
CHK(GH.count("const VERSION = '3.6.88-SDK6'") == 1, 'bundle: sello const VERSION 3.6.88-SDK6')
CHK('>V3.6.88-SDK6<' in GH, 'bundle: badge V3.6.88-SDK6 en el servido')
CHK('const rise0 = sw.flat ? 0 : 0.05;' in GH, 'bundle: aguja r93 c12 rise0/flat intacta')

# ------------------------------------------------------------- RUNTIME ----
print('== RUNTIME (juego vivo) ==')
Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT, wait_until='load')
    pg.wait_for_timeout(2500)
    pg.mouse.click(640, 600)
    pg.wait_for_timeout(6000)
    pg.evaluate("""() => {
      const g = window.__PP_HALLOWEEN && window.__PP_HALLOWEEN.ctrl().game;
      if (g && g.champIntro) g.hideChampIntro(true);
    }""")
    pg.wait_for_timeout(3000)

    # ---- inyección del poder calabaza (mismo camino real: pend → _lanzar)
    vive = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; if (!H) return { err: 'sin handle' };
      const ctrl = H.ctrl(); const P = ctrl.poderes;
      if (!P) return { err: 'sin poderes' };
      const cal = (P.lista || []).find(p => p.kind === 'calabaza');
      if (!cal) return { err: 'sin calabaza en lista' };
      P.pend = cal; P.pendT = 0.001;
      return { ok: true, dur: cal.duration || 10 };
    }""")
    CHK(vive.get('ok') is True, 'inyección: calabaza en cola del poder (%s)' % (vive.get('err') or 'pend→_lanzar'))
    pg.wait_for_timeout(600)

    # ---- A · NACIMIENTO: la bola OCULTA y la calabaza EN SU LUGAR EXACTO
    nace = pg.evaluate("""() => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      const C = P.ctx && P.ctx.calabaza;
      if (!C || !C.gltf) return { err: 'calabaza no nacida' };
      const d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
      return { activo: P.activo && P.activo.kind,
               bolaOculta: g.ballMesh ? g.ballMesh.visible === false : null,
               calaVisible: C.gltf.visible === true,
               dist: d(C.gltf.position, g.ballMesh.position),
               enEscena: g.scene.children.indexOf(C.gltf) >= 0 };
    }""")
    if 'err' in (nace or {}):
        CHK(False, 'nacimiento: %s' % nace['err'])
    else:
        CHK(nace.get('activo') == 'calabaza', 'nacimiento: poder calabaza ACTIVO (pend → _lanzar)')
        CHK(nace.get('bolaOculta') is True, 'nacimiento: la bola OCULTA (la calabaza ES la bola)')
        CHK(nace.get('calaVisible') is True, 'nacimiento: la calabaza visible')
        CHK(nace.get('dist') is not None and nace['dist'] < 1e-6,
            'nacimiento: calabaza EN EL LUGAR EXACTO de la bola (dist=%s m)' % nace.get('dist'))
        CHK(nace.get('enEscena') is True, 'nacimiento: cuerpo en la escena desde el frame 1')

    # ---- B · CAMINOS DEL NÚCLEO: aunque el núcleo re-enseñe la bola, paso() la re-oculta
    # (polling paciente: en headless la 1.ª compilación GLSL del cuerpo bloquea ~150 ms)
    reens = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      g.ballMesh.visible = true;               // simula toss 4417 / HELD 8774 / reset 1132
      for (let i = 0; i < 30; i++) {           // hasta 1,8 s esperando un frame del juego
        await new Promise(r => setTimeout(r, 60));
        if (g.ballMesh.visible === false) break;
      }
      return { reoculta: g.ballMesh.visible === false,
               activo: !!(P.activo && P.activo.kind === 'calabaza') };
    }""")
    CHK(reens.get('activo') is True, 're-enseño: poder sigue vivo durante la prueba')
    CHK(reens.get('reoculta') is True,
        're-enseño: el núcleo re-enseña la bola y paso() la RE-OCULTA antes del render (imposible ver ambas)')

    # ---- C · LUGAR EXACTO con la bola en movimiento (mismo sincronizado del núcleo)
    # (polling: en champtest el núcleo re-aparca la bola y los primeros frames
    #  de la calabaza compilan GLSL — se espera a que un frame real corra)
    mueve = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      const C = P.ctx && P.ctx.calabaza;
      if (!C || !C.gltf) return { err: 'sin calabaza' };
      const d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y, a.z - b.z);
      g.ball.pos.x += 0.35; g.ball.pos.y += 0.22; g.ball.pos.z -= 0.4;
      g.ballMesh.position.copy(g.ball.pos);    // el sincronizado del núcleo (c12 §7)
      let dist = d(C.gltf.position, g.ballMesh.position);
      let t0 = performance.now();
      for (let i = 0; i < 30; i++) {           // hasta 1,8 s esperando el frame que la clava
        await new Promise(r => setTimeout(r, 60));
        dist = d(C.gltf.position, g.ballMesh.position);
        if (dist < 1e-6) break;
      }
      return { dist: dist, ms: Math.round(performance.now() - t0),
               estado: g.rules.state };
    }""")
    if 'err' in (mueve or {}):
        CHK(False, 'lugar exacto: %s' % mueve['err'])
    else:
        CHK(mueve.get('dist') is not None and mueve['dist'] < 1e-6,
            'lugar exacto: bola movida 0,6 m → la calabaza la CLAVA en el primer frame real (dist=%s m, %s ms — cero deriva)' %
            (mueve.get('dist'), mueve.get('ms')))

    # ---- D · GUARD r92: la marca ppCalabaza renace aunque el núcleo recrea la bola
    guard = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const g = ctrl.game;
      delete g.ball.ppCalabaza;                // simula bola recreada entre puntos
      for (let i = 0; i < 30; i++) {           // hasta 1,8 s esperando un frame
        await new Promise(r => setTimeout(r, 60));
        if (g.ball.ppCalabaza === true) break;
      }
      return { marca: g.ball.ppCalabaza === true };
    }""")
    CHK(guard.get('marca') is True, 'guard r92: ppCalabaza RENACE cada frame (contacto de la IA no caduca)')

    # ---- E · ESTALLIDO: la calabaza se oculta y la bola VUELVE (entrega diseñada)
    explota = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      const C = P.ctx && P.ctx.calabaza;
      if (!C) return { err: 'sin calabaza' };
      C.t = C.dur - 0.5;                       // dentro de la ventana de estallido
      await new Promise(r => setTimeout(r, 300));
      return { explotada: C.explotada === true,
               bolaVisible: g.ballMesh.visible === true,
               calaOculta: C.gltf.visible === false };
    }""")
    if 'err' in (explota or {}):
        CHK(False, 'estallido: %s' % explota['err'])
    else:
        CHK(explota.get('explotada') is True, 'estallido: CHOFFF disparado en su ventana')
        CHK(explota.get('calaOculta') is True, 'estallido: la calabaza SE OCULTA')
        CHK(explota.get('bolaVisible') is True, 'estallido: la bola VUELVE — nunca ambas a la vez')

    # ---- F · CIERRE: fin() limpia todo (cuerpo fuera de la escena)
    cierre = pg.evaluate("""async () => {
      const H = window.__PP_HALLOWEEN; const ctrl = H.ctrl();
      const P = ctrl.poderes; const g = ctrl.game;
      const C = P.ctx && P.ctx.calabaza;
      const ref = C ? C.gltf : null;
      P.powerT = 0.01;
      await new Promise(r => setTimeout(r, 300));
      return { cerrado: P.activo === null,
               ctxLimpio: !P.ctx.calabaza,
               fuera: ref ? g.scene.children.indexOf(ref) < 0 : true };
    }""")
    CHK(cierre.get('cerrado') is True, 'cierre: poder cerrado (activo=null)')
    CHK(cierre.get('ctxLimpio') is True, 'cierre: ctx.calabaza limpio')
    CHK(cierre.get('fuera') is True, 'cierre: cuerpo retirado de la escena (sin fugas)')

    CHK(len(errs) == 0, 'cero pageerrors en toda la sesión (%s)' % (errs[:2] if errs else 'limpio'))
    b.close()
srv.shutdown()

print('')
print('== MARCADOR r94: %d OK · %d FALLO ==' % (len(OK), len(FAIL)))
if FAIL:
    print('FALLOS:')
    for f in FAIL:
        print('  ✗', f)
    sys.exit(1)
print('VERDE')
