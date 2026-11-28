#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r162 · dos frentes del informe del dueño:
A · «No podríamos entrar directamente en VR sin pulsar VR otra vez en
  game.html?» — la portada YA pedía la sesión en el gesto, pero podía
  MORIR A MEDIAS: (1) enterVR pedía SIEMPRE immersive-ar (v3.6.43) y si
  requestSession('immersive-ar') fallaba (permiso de passthrough denegado/
  caducado) toda la entrada se caía SIN reintento a VR → segundo pulso
  desde dentro del juego; (2) la portada bloqueaba el intento si
  isSessionSupported('immersive-vr') había dicho «no» (permiso XR denegado
  en otra época) — botón muerto que ni siquiera re-pregunta el permiso.
  FIX: fallback AR→VR en el MISMO gesto + la portada intenta SIEMPRE
  (requestSession es la única verdad; el catch da el mensaje honesto).
B · «No veo la V3.6.241 en producción» — el servidor SÍ la sirve (curl sin
  caché: PAGES-VERSION 3.6.241 · fuente_commit 1cb15d8 · CONFIG_UI_TEMAS en
  el game.html servido). Es caché del dispositivo: el SW servía game.html
  red-primero pero con límite 4 s (wifi del casco lenta → caía al cache
  viejo) y la PORTADA index.html iba cache-first (se servía vieja para
  siempre). FIX: límite 8 s para game.html + index.html también
  red-primero + ?v del salto fresco."""
import sys

F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
F_C13 = '/home/z/my-project/src/game/core/c13_ui_arranque.js'
F_SW = '/home/z/my-project/public/sw.js'
F_IDX = '/home/z/my-project/public/index.html'

B = {}
for f in (F_C12, F_C13, F_SW, F_IDX):
    with open(f, 'r', encoding='utf-8') as fh:
        B[f] = fh.read()

P = []


def p(f, old, new, n=1):
    P.append((f, old, new, n))


# A1 · enterVR: fallback AR→VR dentro del mismo gesto
p(F_C12, """    let arOK = false;
    try { arOK = !!(await xr.isSessionSupported('immersive-ar')); } catch (eXR) { /* */ }
    const session = await xr.requestSession(
      arOK ? 'immersive-ar' : 'immersive-vr',
      { optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking', 'dom-overlay'] },
    );
    await this.renderer.xr.setSession(session);""",
"""    let arOK = false;
    try { arOK = !!(await xr.isSessionSupported('immersive-ar')); } catch (eXR) { /* */ }
    // v3.6.242 · ENTRADA A PRUEBA DE CAPRICHOS: si la AR cantó DESPUÉS del
    // isSessionSupported (permiso de passthrough denegado/caducado, visor
    // reacio), el MISMO gesto reintenta con VR inmersivo — la entrada
    // directa de la portada nunca se queda a medias (el dueño no vuelve a
    // pulsar VR dentro del juego porque el primer pulso ya no puede morir).
    const rasgosXR = { optionalFeatures: ['local-floor', 'bounded-floor',
      'hand-tracking', 'dom-overlay'] };
    let session = null;
    if (arOK) {
      try {
        session = await xr.requestSession('immersive-ar', rasgosXR);
      } catch (eAR) {
        session = await xr.requestSession('immersive-vr', rasgosXR);
        this.pendingAR = false;   // la sesión real es VR: sin passthrough
      }
    } else {
      session = await xr.requestSession('immersive-vr', rasgosXR);
    }
    await this.renderer.xr.setSession(session);""")

# A2 · portada: el gesto manda — se intenta SIEMPRE
p(F_C13, """  vrbtn.addEventListener('click', () => {
    game.audio.ensure();
    if (!navigator.xr || !navigator.xr.isSessionSupported) {
      setStatusKey('status_no_vr');
      return;
    }
    if (!xrOK) { setStatusKey('status_no_vr'); return; }
    setStatusKey('status_starting_vr');""",
"""  vrbtn.addEventListener('click', () => {
    game.audio.ensure();
    if (!navigator.xr || !navigator.xr.isSessionSupported) {
      setStatusKey('status_no_vr');
      return;
    }
    // v3.6.242 · EL GESTO MANDA: se intenta SIEMPRE (aunque
    // isSessionSupported haya dicho «no» — permiso XR denegado en otra
    // época, visor caprichoso). requestSession es la única verdad: si el
    // casco puede, entra (y re-pregunta el permiso si hacía falta); si
    // no, el mensaje honesto del catch. Bloquear aquí dejaba el botón
    // MUERTO y obligaba a pulsar VR desde dentro del juego.
    setStatusKey('status_starting_vr');""")

# B1 · sw.js: game.html con más margen de red
p(F_SW, """    event.respondWith(redPrimero(req, 4000));
    return;
  }""",
"""    event.respondWith(redPrimero(req, 8000));
    return;
  }
  // v3.6.242 · la PORTADA también red-primero: cache-first la servía vieja
  // PARA SIEMPRE (el salto ?v apuntaba a builds anteriores — informe del
  // dueño: «no veo la nueva versión»). Es un fichero minúsculo: la red
  // siempre llega, y con redPrimero el ?v que trae manda fresco.
  if (url.pathname.endsWith('/index.html') || url.pathname.endsWith('/')) {
    event.respondWith(redPrimero(req, 3000));
    return;
  }""")

# B2 · el ?v del salto apunta a la build nueva
p(F_IDX, 'game.html?v=36152', 'game.html?v=36242')

mal = [(i, f.split('/')[-1], cc, nn) for i, (f, old, new, nn) in enumerate(P)
       if (cc := B[f].count(old)) != nn]
if mal:
    for i, nom, cc, nn in mal:
        print(f'✗ parche {i} [{nom}]: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for f, old, new, _ in P:
    B[f] = B[f].replace(old, new)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")
print('✓ entrada VR a prueba de caprichos + portada/SW siempre frescos')
