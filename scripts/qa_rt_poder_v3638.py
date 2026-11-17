#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA v3.6.38 · SUPERPODER DE PALA v4 — TIEMPO REAL (capa AG, en vivo;
sustituye a la AF en el listado). Las cuatro peticiones del dueño tras
probar V3.6.37 en el dispositivo:

  1) «detecto un pequeño lag cuando desde el gatillo se lanza un
     superpoder… debe sentirse que la aplicación es inmediata» — PREWARM:
     todo lo pesado de la activación (clon de la pala, materiales, texturas,
     cartelera, compilación de shaders) se fabrica UN paso por frame en los
     ratos del saque (_megaPrewarmArma/_megaPrewarmTick) y el gatillo solo
     ENCIENDE lo ya construido; repintado del icono DIFERIDO (_megaIconDirty
     + canvas persistente): cero canvas y cero texturas nuevas en el disparo.

  2) «el halo rojo y el bote rojo están desfasados en relación a la bola» —
     por ARQUITECTURA, no por sincronización: el halo nace HIJO de ballMesh
     (viaja con ella frame a frame, cero copias) y el anillo de bote vive en
     el RIG (el mismo espacio que la bola y sus marcadores de siempre).

  3) «las flechitas deben estar en el mismo plano del icono, sin solaparse,
     prácticamente tocándose tangencialmente y mirando hacia la cámara» —
     CARTELERA ÚNICA: icono + ‹ › comparten UN grupo billboard (quaternion
     de cámara), z = 0 exacto y hueco tangencial de 1 mm (MEGA_FLECHA_GAP).

  4) «¿podrían los iconos y flechas ser más pequeños mientras jugamos y
     recuperar su tamaño si miramos la pala directamente?» — GAZE: −50 %
     mientras no estén enfocados (MEGA_GAZE_MIN) y tamaño completo dentro
     de un cono de ~15° alrededor del centro de la vista (MEGA_GAZE_COS),
     con lerp exponencial suave.

Pruebas (dos niveles):
  1) FUENTE SERVIDA — agujas del prewarm, del repintado diferido, de la
     cartelera (gap 1 mm · billboard), del halo hijo de bola, del anillo en
     el rig, del gaze (0,5 / cos 0,966) + regresiones (copia de posición del
     halo FUERA, hueco viejo 6 mm FUERA, plano adelantado FUERA, sprites
     sueltos de flechas FUERA) + sello V3.6.38-SDK6.
  2) MECÁNICA REAL headless — prewarm completo en saque (hecho, FX ×3 y
     cartelera fabricados ANTES del disparo), DISPAROS MEDIDOS < 8 ms,
     geometría tangencial exacta (±0,035 m · z = 0), cartelera mirando a
     cámara (ángulo de quaterniones ~0), gaze sube a ~1 mirando la pala y
     baja a ~0,5 al desviarla, halo pegado a la bola al moverla (distancia
     mundo < 1 mm), anillo en el rig, repintado diferido (dirty → paso →
     limpio) y textura del icono SIEMPRE la misma instancia (caché).

Salida: RESULTADO: N OK · M fallos (contrato qa_todo)"""
import asyncio
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
    errors = []

    # ---------- 1 · FUENTE SERVIDA ----------
    try:
        game = urllib.request.urlopen(URL, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer game.html servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    for needle, label in [
        ('const MEGA_FLECHA_GAP = 0.001;', 'flechas TANGENCIALES: hueco de 1 mm'),
        ('MEGA_ICON_S / 2 + MEGA_ARROW_S / 2 + MEGA_FLECHA_GAP',
         'flechas: rozan el borde del icono (misma fórmula con gap)'),
        ('const MEGA_GAZE_MIN = 0.5;', 'GAZE: −50 % mientras no se mira la pala'),
        ('const MEGA_GAZE_COS = 0.966;', 'GAZE: cono de ~15° de «mirada directa»'),
        ('_megaPrewarmArma() {', 'anti-lag: cola de prewarm armada'),
        ('_megaPrewarmTick() {', 'anti-lag: UN paso por frame'),
        ('this.renderer.compile(this.scene, this.camera);',
         'anti-lag: shaders PRECOMPILADOS fuera del gatillo'),
        ("r.state === 'serve' || r.state === 'rally'",
         'anti-lag: el prewarm corre en los ratos del saque/rally'),
        ('_megaIconCv', 'icono: canvas PERSISTENTE (sin crear en jugada)'),
        ('this._megaTex.needsUpdate = true;',
         'icono: re-subida de textura sin crear/disponer'),
        ('this._megaIconDirty = true;', 'repintado DIFERIDO del icono (gatillo limpio)'),
        ('if (this._megaIconDirty) {', 'updateMega repinta solo con el icono a la vista'),
        ('g.quaternion.copy(this.camera.quaternion);',
         'CARTELERA: el grupo entero copia la cámara (mismo plano, de frente)'),
        ('this.ballMesh.add(sp);', 'halo HIJO de la bola (anti-desfase por arquitectura)'),
        ('sp.position.set(0, 0, 0);', 'halo: CENTRO EXACTO de la bola'),
        ('this.rig.add(this._efectoBoteFx);',
         'anillo de bote EN EL RIG (espacio de la bola y sus marcadores)'),
        ('_efectoBoteFxBuild() {', 'anillo: builder separado (lo fabrica el prewarm)'),
        ('_buildMegaIcon() {', 'cartelera del icono construida'),
        ('V3.6.38-SDK6', 'sello de versión servido'),
    ]:
        chk(needle in game, label)
    # agujas múltiples
    chk(game.count('this._buildEfectoHalo();') >= 2,
        'el halo lo construyen el prewarm Y el update (doble camino seguro)')
    # REGRESIONES (lo viejo que DEBE haber desaparecido)
    for ausente, label in [
        ('this._efectoHalo.position.copy(this.ball.pos);',
         'regresión: el halo YA NO copia posición (es hijo de la bola)'),
        ('this.scene.add(this._efectoBoteFx);',
         'regresión: el anillo YA NO vive en scene (vive en el rig)'),
        ('MEGA_ICON_S / 2 + MEGA_ARROW_S / 2 + 0.006',
         'regresión: fuera el hueco viejo de 6 mm (ahora tangencial 1 mm)'),
        ('MEGA_ICON_Z + 0.004',
         'regresión: fuera el plano adelantado de las flechas (mismo plano)'),
        ('_buildMegaArrows() {',
         'regresión: fuera los sprites sueltos de flechas (cartelera única)'),
        ('this._megaArrows = lista', 'regresión: fuera el estado _megaArrows'),
    ]:
        chk(ausente not in game, label)

    # módulo locura intacto (la norma vive en el núcleo)
    try:
        served = urllib.request.urlopen(MOD, timeout=10).read().decode('utf-8')
    except Exception as e:
        print('✗ No se pudo leer el módulo locura servido:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        sys.exit(1)
    chk("trigger: 'norma_rally11'" in served, 'locura: playerPower apunta a la norma')

    # ---------- 2 · MECÁNICA REAL (headless) ----------
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
          const G = window.__PP_GAME;
          const out = {};
          if (!G) { out.sinJuego = true; return out; }
          try { window.__pp2DPlay = true; } catch (e) { /* */ }
          try { localStorage.setItem('pp_pala_mejorada_v1', '1'); } catch (e) { /* */ }
          G.palaMejorada = true;
          G.champs.activeId = 'locura';
          const rndReal = Math.random;
          const libre = (G.paddleHand === 0) ? 1 : 0;
          const paso = () => { try { G.updateMega(1 / 60); } catch (e) { out.errUpd = String(e); } };

          // PARTIDO + saque: el PREWARM corre SOLO aquí (ratos muertos)
          try { G.rules.startMatch('match'); } catch (e) { out.errMatch = String(e); }
          G.rules.state = 'serve';
          for (let i = 0; i < 8; i++) paso();          // 6 pasos de cola + margen
          out.prewarmHecho = G._megaPrewarmHecho === true &&
            G._megaPrewarmQ === null;
          out.fxDeAntemano = !!G._megaFx && !!G._efectoFx && !!G._imanFx;
          out.carteleraDeAntemano = Array.isArray(G._megaIcon) &&
            G._megaIcon.filter((g) => g).length === 2;
          out.sinCargasAun = G._megaMatriz.length === 0;

          // · CARGA + cartelera viva: geometría tangencial EXACTA
          Math.random = () => 0.1;                     // SIEMPRE 'mega'
          G.rules.state = 'rally'; G.rules.rallyHits = 11;
          paso();
          const g0 = G._megaIcon && G._megaIcon[0];
          out.iconoVivo = !!g0 && g0.visible === true;
          const pieza = (g, n) => (g && g.children && g.children[n]) || null;
          const izq = g0 && g0.userData.izq, der = g0 && g0.userData.der,
                ico = g0 && g0.userData.ico;
          out.mismoPlano = !!izq && !!der && Math.abs(izq.position.z) < 1e-9 &&
            Math.abs(der.position.z) < 1e-9 && Math.abs(ico.position.z) < 1e-9;
          const X_TAN = 0.048 / 2 + 0.020 / 2 + 0.001;   // tangencial: 0,035 m
          out.tangencial = !!izq && !!der &&
            Math.abs(Math.abs(izq.position.x) - X_TAN) < 1e-9 &&
            Math.abs(Math.abs(der.position.x) - X_TAN) < 1e-9 &&
            izq.position.x < 0 && der.position.x > 0;
          out.flechaPorIndice = izq.visible === false && der.visible === false;

          // · CARTELERA mirando a CÁMARA (ángulo de quaterniones ~ 0)
          paso();
          let ang = -1;
          try { ang = g0.quaternion.angleTo(G.camera.quaternion); }
          catch (e) { out.errAng = String(e); }
          out.billboard = ang >= 0 && ang < 0.02;

          // · GAZE: mirar la pala la ENGRANDECE; desviar la vista la encoge
          try {
            const wp = g0.position.clone();
            g0.parent.localToWorld(wp);
            G.camera.position.set(wp.x, wp.y + 0.05, wp.z + 1.0);
            G.camera.lookAt(wp);                       // DIRECTO al icono
            for (let i = 0; i < 30; i++) paso();
            out.gazeCrece = G._megaGazeS > 0.9;
            out.escalaGrande = g0.scale.x > 0.85;
            G.camera.lookAt(wp.x + 2.0, wp.y, wp.z);   // vista DESVIADA
            for (let i = 0; i < 45; i++) paso();
            out.gazeBaja = G._megaGazeS < 0.62;
            out.escalaPequena = g0.scale.x < 0.68;
          } catch (e) { out.errGaze = String(e); }

          // · DISPAROS MEDIDOS (con todo precalentado: < 8 ms)
          G.rules.state = 'rally';
          let t0 = performance.now();
          let r1 = null;
          try { r1 = G.megaTrigger(libre); } catch (e) { out.errDisp1 = String(e); }
          out.megaRapido = r1 === true && (performance.now() - t0) < 8;
          G._megaT = 0; paso();
          // recarga de efecto e imán para medir sus disparos
          Math.random = () => 0.5;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          t0 = performance.now();
          let r2 = null;
          try { r2 = G.megaTrigger(libre); } catch (e) { out.errDisp2 = String(e); }
          out.efectoRapido = r2 === true && (performance.now() - t0) < 8;
          G._efectoT = 0; paso();
          Math.random = () => 0.9;
          G.rules.state = 'point'; paso();
          G.rules.state = 'rally'; G.rules.rallyHits = 11; paso();
          t0 = performance.now();
          let r3 = null;
          try { r3 = G.megaTrigger(libre); } catch (e) { out.errDisp3 = String(e); }
          out.imanRapido = r3 === true && (performance.now() - t0) < 8;
          G._imanT = 0; paso();

          // · HALO hijo de la bola: pegado a ella SEA CUAL SEA su posición
          try {
            G.ball.ppEfecto = true;
            paso();
            out.haloHijo = !!G._efectoHalo &&
              G._efectoHalo.parent === G.ballMesh &&
              G._efectoHalo.position.lengthSq() < 1e-12;
            G.ball.pos.set(0.42, 1.31, -0.65);         // bola movida a saco
            G.ballMesh.position.copy(G.ball.pos);
            const vh = G._efectoHalo.getWorldPosition(
              G._efectoHalo.position.clone());
            out.haloPegado = vh.distanceTo(G.ball.pos) < 0.001;
            G.ball.ppEfecto = false;
            paso();
            out.haloFuera = G._efectoHalo.visible === false;
          } catch (e) { out.errHalo = String(e); }

          // · ANILLO de bote EN EL RIG
          try {
            G.ball.ppEfecto = true; G.ball.spin.set(0, 40, 0);
            G._efectoBoteFxShow(G.ball.pos);
            out.anilloRig = !!G._efectoBoteFx &&
              G._efectoBoteFx.parent === G.rig &&
              G._efectoBoteFx.visible === true;
            G._efectoBoteFx.userData.boteT = 0.0001;
            paso();
            out.anilloApaga = G._efectoBoteFx.visible === false;
            G.ball.ppEfecto = false;
          } catch (e) { out.errAnillo = String(e); }

          // · REPINTADO DIFERIDO: gasta marca dirty; el paso lo limpia;
          //   la textura SIEMPRE es la misma instancia (caché de sesión)
          try {
            G.rules.state = 'point'; paso();
            Math.random = () => 0.1;
            G.rules.state = 'rally'; G.rules.rallyHits = 22; paso();
            const texAntes = G._megaTex;
            const ent = G._megaMatriz[0];
            G._megaGasta(ent);
            out.dirtyAlGastar = G._megaIconDirty === true;
            paso();
            out.dirtyLimpio = G._megaIconDirty === false;
            out.mismaTextura = G._megaTex === texAntes;
            out.canvasPersiste = !!G._megaIconCv;
          } catch (e) { out.errDirty = String(e); }

          Math.random = rndReal;
          out.erroresPagina = 0;
          return out;
        }""")
        await browser.close()

        if rt.get('sinJuego'):
            print('✗ window.__PP_GAME no existe (el juego no arrancó)')
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            sys.exit(1)

        for k, v in sorted(rt.items()):
            if k.startswith('err'):
                print(f'  · {k}: {v}')

        esperados = [
            ('prewarmHecho', 'anti-lag: prewarm COMPLETO en el saque (cola vacía)'),
            ('fxDeAntemano', 'anti-lag: los TRES cantos fabricados ANTES del disparo'),
            ('carteleraDeAntemano', 'anti-lag: cartelera del icono fabricada de antemano'),
            ('sinCargasAun', 'el prewarm NO concede cargas (solo fabrica)'),
            ('iconoVivo', 'cartelera viva al recoger la carga'),
            ('mismoPlano', 'flechas e icono en el MISMO plano (z = 0 exacto)'),
            ('tangencial', 'flechas TANGENCIALES: ±0,035 m (rozan el icono, 1 mm)'),
            ('flechaPorIndice', 'sin vecino NO hay flecha (índice 0 de 1 poder)'),
            ('billboard', 'CARTELERA mirando a cámara (ángulo de quaterniones ~0)'),
            ('gazeCrece', 'GAZE: mirar la pala directamente ENGRANDECE (→1)'),
            ('escalaGrande', 'GAZE: escala del conjunto grande al mirar'),
            ('gazeBaja', 'GAZE: desviar la vista ENCOGE el conjunto (→0,5)'),
            ('escalaPequena', 'GAZE: escala a la mitad mientras juegas'),
            ('megaRapido', 'DISPARO MEGA medido < 8 ms (inmediato)'),
            ('efectoRapido', 'DISPARO EFECTO medido < 8 ms (inmediato)'),
            ('imanRapido', 'DISPARO IMÁN medido < 8 ms (inmediato)'),
            ('haloHijo', 'halo HIJO de la bola en su centro exacto'),
            ('haloPegado', 'halo PEGADO a la bola movida (distancia mundo < 1 mm)'),
            ('haloFuera', 'sin marca: el halo se apaga'),
            ('anilloRig', 'anillo de bote EN EL RIG (espacio de la bola)'),
            ('anilloApaga', 'anillo one-shot se apaga solo'),
            ('dirtyAlGastar', 'gastar carga SOLO marca dirty (cero canvas en el gatillo)'),
            ('dirtyLimpio', 'el repintado diferido ocurre en updateMega'),
            ('mismaTextura', 'textura del icono SIEMPRE la misma (caché de sesión)'),
            ('canvasPersiste', 'canvas persistente del icono vivo'),
        ]
        for k, label in esperados:
            chk(rt.get(k) is True, label)

    if errors:
        for e in errors[:5]:
            print('  · pageerror:', e[:200])
        chk(False, 'sin errores de página durante la mecánica real')
    else:
        chk(True, 'sin errores de página durante la mecánica real')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


asyncio.run(main())
