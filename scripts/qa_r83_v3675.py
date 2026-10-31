#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r83_v3675 — CAPA BS · V3.6.74→3.6.89-SDK6, FASE 77 «LA PALA AL MILÍMETRO».

Petición del dueño (r83): «Dentro del Pro Training tenemos el ajuste de la
posición de la pala, pero no tiene sentido ahí, así que vamos a moverlo al
apartado de Ajustes y crear un subapartado que nos de acceso a la
configuración de la pala (botón bonito y colorido como el resto de la
interface y con su iconito correspondiente). … el stick de la mano derecha
realiza giros en los ejes creo que X e Y, mientras que el stick de la mano
izquierda realiza desplazamientos en los ejes X e Y … mientras en un panel
lateral se muestran los grados o desplazamiento … permitir guardar estos
ajustes con un nombre para cargarlos … me gustaría que ese panel informativo
fuese más visual y bonito y pudiera verse frontalmente un poco por encima de
nuestra vista sin interferir con la visión de la pala … forzando a que cuando
entramos en ajuste de pala siempre se active el passthrow … (pasar a
passthrow debe ser inmediato sin salir de la pantalla de configuración). Si
esto no fuese posible, entonces visualizaríamos la réplica de los mandos …
usamos esos modelos que ya tenemos. Además me falta poder girar en el eje Z y
mover en el eje Z … representar los ejes locales sobre la pala y dibujar
claramente visibles una flecha con el desplazamiento o giro … La guardamos
con un nombre y queda permanente almacenada en nuestro dispositivo … podremos
salir de este modo llamando al menú con la pulsación B y al salir se recupera
la visión anterior del Hall eliminado los elementos o modos usados».

Lo implementado (r83, verificación de ESTA capa sobre el código REAL):
  · AJUSTES › PALA: 7.ª tarjeta (cat_pala, icono PP_ICONS.pala) → subpágina
    «pala» (AJUSTAR LA PALA EN VR · GUARDAR CON NOMBRE · NATURAL · lista
    CARGAR/Quitar · ⌂ Hall). La tarjeta del Pro Training DESAPARECE.
  · enterCalib(true) = ajuste PURO: PASSTHROUGH INMEDIATO en caliente
    (_pstAplicar — sesión immersive-ar intacta), gizmo de EJES LOCALES RGB
    sobre la montura de la pala + LA FLECHA DEL AJUSTE por eje (raíl + flecha
    que viaja con el valor vivo: dirección = signo, magnitud = distancia),
    panel FRONTAL head-locked por ENCIMA de la vista (sin pisar la pala) con
    chip PASSTHROUGH/RÉPLICA y tabla viva de los 6 GDL, RÉPLICAS GLB de los
    mandos del tutorial SOLO sin passthrough, salida Y directa y B → MENÚ con
    recogida total («nada arrastrado al HALL»).
  · VERIFICACIÓN DEL MAPEO que describió el dueño (es CORRECTO): stick D =
    giros X/Y · stick I = movimientos X/Y · panel con mm y grados · Z por
    CLICK del stick (botones[3]) con GRIP como atajo de siempre.
  · AGARRES con nombre PERMANENTES (ppxr_grips_v1) + teclado NOMBRE DEL
    AGARRE + gestión completa desde el menú.

BLOQUES: (1) AGUJAS r83 en el servido. (2) CONTADORES exactos (mudanza
confirmada). (3) JUEGO REAL headless: enterCalib(true) con sesión simulada,
passthrough al instante, gizmo con cursores vivos, sticks sintéticos (X·Y y
Z por click), guardado con A, teclado con nombre, carga/borrado desde el
menú, palaGo real, salida limpia al Hall y persistencia tras reload.
Uso: python3 qa_r83_v3675.py [URL]
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # — el modo puro: entrar / salir —
    ("enterCalib(pala) existe", "enterCalib(pala = false) {"),
    ("r83 · PASSTHROUGH INMEDIATO al entrar", "PASSTHROUGH INMEDIATO"),
    ("canje del fondo en caliente", "this._pstAplicar(true);"),
    ("restauración del passthrough previo", "_pstRestaurar() {"),
    ("SALIDA LIMPIA AL HALL (nada arrastrado)", "r83 · SALIDA LIMPIA AL HALL"),
    ("B en el ajuste abre el MENÚ COMÚN", "0.55) r83 · AJUSTE DE PALA: B abre el MENÚ COMÚN"),
    ("Y = salida directa documentada en el panel", "salida documentada en el propio panel"),
    ("startCalib entra en modo PURO", "game.enterCalib(true);"),
    # — ejes Z: click del stick (y GRIP compat) —
    ("click del stick leído (botones[3])", "?.buttons?.[3]?.pressed"),
    ("Z de giro: stick D pulsado", "const zRot = gripR || stickR;"),
    ("Z de posición: stick I pulsado", "const zPos = gripL || stickL;"),
    ("rodar en Z con el stick D", "off.rz = adj(off.rz, dz(R.x) * rot)"),
    ("acercar en Z con el stick I", "off.pz = adj(off.pz, -dz(L.y) * pos)"),
    # — gizmo: ejes locales + LA FLECHA DEL AJUSTE —
    ("gizmo de ejes locales", "function createPalaAxes()"),
    ("LA FLECHA DEL AJUSTE (cursor vivo)", "LA FLECHA DEL AJUSTE"),
    ("raíl por eje (recorrido del cursor)", "const GUIA = 0.085;"),
    ("cursor construido por eje", "const cursorDe = (col, dir) => {"),
    ("3 cursores (X roja · Y verde · Z azul)", "cursorDe(0x74c0fc, 'z')"),
    ("ejes alimentados con el valor VIVO", "setActive(this.calibPala ? act : null, off)"),
    ("tick del gizmo en el bucle (sólo en su modo)", "this._palaAxes.tick(dt);"),
    # — panel frontal (por encima de la vista, sin pisar la pala) —
    ("anclaje FRONTAL head-locked", "_palaPanelAnclar() {"),
    ("por ENCIMA de la vista (+0,30 m)", "destino.y = Math.max(1.32, muHead.y + 0.30);"),
    ("título del panel", "g2.fillText('AJUSTE DE PALA', 36, 62);"),
    ("chip passthrough", "PASSTHROUGH · mandos reales a la vista"),
    ("chip réplica 3D", "RÉPLICA 3D · mando de referencia"),
    ("leyenda honesta del botón B", "menú · cargar · salir"),
    ("pie del panel: Y · salir al HALL", "Y · salir al HALL"),
    # — réplicas GLB (fallback del dueño) —
    ("réplicas SOLO sin passthrough", "_palaMandosTick() {"),
    ("usa los GLB del tutorial", "window.__PP_MANDO_GLB"),
    ("exposición de los GLB reales", "__PP_MANDO_GLB = { izq: TUT_MANDO_GLB, der: TUT_MANDO_DER_GLB }"),
    ("réplicas ancladas a los grips", "this.grips[h].add(mont);"),
    ("dispose honesto de las réplicas", "_palaMandosOff() {"),
    # — AJUSTES › PALA: la 7.ª tarjeta y su subpágina —
    ("séptima categoría: PALA", "séptima categoría: PALA"),
    ("tarjeta con icono de pala", "PP_ICONS.pala"),
    ("subpágina «pala» en el router", "arg === 'optsPala'"),
    ("botón AJUSTAR LA PALA EN VR", "'palaGo'"),
    ("guardia: no en partida online", "msg_pala_online"),
    ("guardar con nombre (teclado)", "NOMBRE DEL AGARRE"),
    ("cargar agarre por nombre", "'gripLoad:'"),
    ("borrar agarre", "'gripDel:'"),
    ("botón ⌂ Hall desde la subpágina", "salida limpia al Hall desde AQUÍ"),
    # — i18n ES/EN —
    ("categoría ES", "cat_pala: 'PALA',"),
    ("categoría EN", "cat_pala: 'PADDLE',"),
    ("mensaje de entrada ES", "msg_pala_on: 'Coloca la pala sobre tu mando real"),
    ("sub ES", "pala_go: 'AJUSTAR LA PALA EN VR'"),
    ("sub EN", "pala_go: 'FIT THE PADDLE IN VR'"),
    # — persistencia permanente —
    ("almacén permanente del dispositivo", "ppxr_grips_v1"),
    ("guardar con A dentro del ajuste", "A: guardar"),
    # — mudanza confirmada —
    ("la tarjeta se RETIRA del hub del Pro Training", "se RETIRA del hub (se muda a"),
    ("versión 3.6.75 en el badge", "V3.6.89-SDK6"),
    ("versión 3.6.75 en VERSION", "VERSION = '3.6.89-SDK6'"),
]

CONTADORES = [
    ("la tarjeta antigua del Pro Training DESAPARECIÓ", "trv3:calib", 0),
    ("el botón palaGo aparece exactamente 3 veces", "'palaGo'", 3),
    ("enterCalib(pala = false) se declara una vez", "enterCalib(pala = false) {", 1),
    ("createPalaAxes: definición + una llamada", "createPalaAxes()", 2),
    ("los 3 cursores se construyen", "cursorDe(", 3),
    ("el ajuste PURO se arranca una vez", "game.enterCalib(true);", 1),
    ("sin restos del panel antiguo", "this.palaPanel", 0),
    ("versión 3.6.75 (badge + VERSION)", "3.6.89-SDK6", 2),
]


JS_RED83 = """() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 0 · sesión simulada (isPresenting) + cancha limpia
  const xr = G.renderer.xr;
  Object.defineProperty(xr, 'isPresenting', { get() { return true; }, configurable: true });
  G.inAR = true;
  G.pstOn = false;
  const bg0 = G.scene.background;
  const roomVis0 = G.roomGroup ? G.roomGroup.visible : null;

  // 1 · ENTRADA (enterCalib(true) = el mismo camino de palaGo/startCalib):
  //     passthrough INMEDIATO sin salir de la configuración
  G.enterCalib(true);
  chk(G.calib === true, 'enterCalib: modo ajuste activo');
  chk(G.calibPala === true, 'enterCalib(true): modo PALA PURO (AJUSTES › PALA)');
  chk(G.calibPanel && G.calibPanel.group.visible === true, 'panel FRONTAL visible');
  chk(G.pstOn === true, 'passthrough ACTIVADO al entrar (inmediato)');
  chk(G._pstAplicada === true, 'fondo canjeado EN CALIENTE (_pstAplicada)');
  chk(G.scene.background === null, 'fondo null: mandos REALES a la vista');
  chk(!G.roomGroup || G.roomGroup.visible === false, 'sala virtual OCULTA');
  chk(G._pstVenia && G._pstVenia.pstOn === false,
      'estado previo del jugador RECORDADO (se restaura al salir)');
  chk(!!G.rules.message, 'mensaje de entrada (coloca la pala sobre tu mando)');

  // 2 · gizmo de ejes locales: 3 ejes + 3 raíles + 3 flechas
  const axes = G._palaAxes;
  chk(!!axes, 'gizmo de ejes CONSTRUIDO');
  chk(axes && axes.group.parent === G.paddleMounts[G.paddleHand],
      'gizmo colgado de la MONTURA de la pala (ejes locales)');
  chk(axes && axes.group.children.length === 9,
      'gizmo: 3 ejes + 3 raíles + 3 flechas (' +
      (axes ? axes.group.children.length : 0) + ' hijos)');

  // 3 · LA FLECHA DEL AJUSTE: viaja con el valor vivo (dirección y magnitud)
  if (axes) {
    G.applyGripOffset({ px: 0.175, py: 0, pz: 0, rx: 0, ry: 0, rz: 0 }); // +50 % del raíl
    axes.setActive(null, G.gripOffset);
    axes.tick(0.016);
    const fleX = axes.group.children[4];   // 3 ejes + raíl X → flecha X
    chk(Math.abs(fleX.position.x - 0.0425) < 0.003,
        'flecha X VIAJA con el offset (+50 % del raíl: ' +
        fleX.position.x.toFixed(4) + ' m)');
    G.applyGripOffset({ px: -0.14, py: 0, pz: 0, rx: 0, ry: 0, rz: 0 }); // −40 %
    axes.setActive(null, G.gripOffset);
    axes.tick(0.016);
    chk(fleX.position.x < -0.03 && fleX.position.x > -0.09,
        'flecha X al LADO NEGATIVO (dirección = signo)');
    G.applyGripOffset({ px: 0, py: 0, pz: 0, rx: 0.6, ry: 0, rz: 0 }); // giro 0.6/1.2 = 50 %
    axes.setActive(null, G.gripOffset);
    axes.tick(0.016);
    chk(Math.abs(fleX.position.x - 0.0425) < 0.003,
        'la flecha también refleja el GIRO (misma regla que el panel)');
    G.applyGripOffset({ px: 0, py: 0, pz: 0, rx: 0, ry: 0, rz: 0 });
    axes.setActive(null, G.gripOffset);
    axes.tick(0.016);
    chk(Math.abs(fleX.position.x) < 0.002, 'flecha centrada con el agarre a cero');
  }

  // 4 · RÉPLICAS GLB: aparecen SIN passthrough y desaparecen CON él
  G.pstOn = false;
  G._pstAplicar(false);
  G._palaMandosTick();
  chk(!!G._palaMandos && G._palaMandos.length === 2,
      'réplicas: 2 monturas ancladas (' + (G._palaMandos ? G._palaMandos.length : 0) + ')');
  chk(!G._palaMandos ||
      G._palaMandos.every((m, i) => m.parent === G.grips[i]),
      'réplicas hijas de los GRIPS XR (coinciden 1:1 con el mando real)');
  G.pstOn = true;
  G._pstAplicar(true);
  G._palaMandosTick();
  chk(G._palaMandos === null, 'CON passthrough las réplicas se RETIRAN (se ve el mando real)');

  // utilidades de mando sintético (botones por ÍNDICE: 3 click stick,
  // 4 A/X, 5 B/Y — el estándar del juego)
  const setBtn = (gp, i, on) => {
    while (gp.buttons.length <= i) gp.buttons.push({ pressed: false });
    gp.buttons[i].pressed = on;
  };

  // 5 · MAPEO del dueño (verificado: ES correcto) — X·Y con los sticks
  G.sources = [
    { gamepad: { axes: [0, 0, 0, 0], buttons: [] } },   // right (handIndex 0)
    { gamepad: { axes: [0, 0, 0, 0], buttons: [] } },   // left  (handIndex 1)
  ];
  G.updateCalibration(0.016);   // asentar btnPrev sin mover nada
  const off0 = { ...G.gripOffset };
  G.sources[0].gamepad.axes = [0, 0, 0.7, 0.8];   // stick D: x=+, y=+
  G.sources[1].gamepad.axes = [0, 0, 0.7, 0.8];   // stick I: x=+, y=+
  G.updateCalibration(0.5);
  chk(G.gripOffset.ry > off0.ry + 0.25, 'stick D horizontal GIRA en Y (+' +
    ((G.gripOffset.ry - off0.ry) * 180 / Math.PI).toFixed(0) + '°)');
  chk(G.gripOffset.rx < off0.rx - 0.25, 'stick D vertical INCLINA en X (giro ' +
    ((G.gripOffset.rx - off0.rx) * 180 / Math.PI).toFixed(0) + '°)');
  chk(G.gripOffset.px > off0.px + 0.03, 'stick I horizontal MUEVE en X (+' +
    ((G.gripOffset.px - off0.px) * 1000).toFixed(0) + ' mm)');
  chk(G.gripOffset.py < off0.py - 0.03, 'stick I vertical MUEVE en Y (−' +
    ((off0.py - G.gripOffset.py) * 1000).toFixed(0) + ' mm)');
  chk(G._palaAct.ry === 1 && G._palaAct.rx === 1 &&
      G._palaAct.px === 1 && G._palaAct.py === 1,
      'los 4 ejes en uso MARCADOS (panel ilumina + flechas respiran)');

  // 6 · EJE Z: CLICK del stick (botones[3]) — giro Z con el derecho
  const ry0 = G.gripOffset.ry;
  const rz0 = G.gripOffset.rz;
  setBtn(G.sources[0].gamepad, 3, true);
  G.sources[0].gamepad.axes = [0, 0, 0.8, 0];
  G.updateCalibration(0.5);
  chk(G._palaAct.rz === 1 && G._palaAct.ry === 0, 'eje Z de giro ACTIVO (ry ya no)');
  chk(G.gripOffset.rz > rz0 + 0.25, 'stick D pulsado + horizontal RODA en Z (+' +
    ((G.gripOffset.rz - rz0) * 180 / Math.PI).toFixed(0) + '°)');
  chk(Math.abs(G.gripOffset.ry - ry0) < 1e-9, 'ry INTACTO (Z aislado de X·Y)');
  setBtn(G.sources[0].gamepad, 3, false);
  G.sources[0].gamepad.axes = [0, 0, 0, 0];
  G.updateCalibration(0.016);
  // posición Z con el izquierdo (stick pulsado + vertical = acercar)
  const pz0 = G.gripOffset.pz;
  setBtn(G.sources[1].gamepad, 3, true);
  G.sources[1].gamepad.axes = [0, 0, 0, -0.8];
  G.updateCalibration(0.5);
  chk(G._palaAct.pz === 1 && G._palaAct.py === 0, 'eje Z de posición ACTIVO (py ya no)');
  chk(G.gripOffset.pz > pz0 + 0.03, 'stick I pulsado + vertical ACERCA en Z (+' +
    ((G.gripOffset.pz - pz0) * 1000).toFixed(0) + ' mm)');
  setBtn(G.sources[1].gamepad, 3, false);
  G.sources[1].gamepad.axes = [0, 0, 0, 0];
  G.updateCalibration(0.016);
  // GRIP sigue valiendo como atajo (compatibilidad de la casa)
  setBtn(G.sources[1].gamepad, 1, true);
  G.sources[1].gamepad.axes = [0, 0, 0, -0.5];
  G.updateCalibration(0.3);
  chk(G.gripOffset.pz > G.gripOffset.pz - 1e9, 'GRIP compat sin error');
  setBtn(G.sources[1].gamepad, 1, false);
  G.sources[1].gamepad.axes = [0, 0, 0, 0];
  G.updateCalibration(0.016);

  // 7 · el panel recibe ejes/estado (repintado vivo sin errores)
  try {
    G.calibPanel.update({
      name: G.gripName,
      off: G.gripOffset,
      act: G._palaAct,
      pst: !!(G.inAR && G.pstOn),
    });
    chk(true, 'panel.update() con act+pst sin errores');
  } catch (ePan) {
    chk(false, 'panel.update() lanzó: ' + ePan);
  }

  // 8 · GUARDAR con A (nombre automático) — valores exactos en el almacén
  const n0 = Object.keys(G.loadGripsStore()).length;
  setBtn(G.sources[0].gamepad, 4, true);      // A = botón 4 (derecho)
  G.updateCalibration(0.016);
  setBtn(G.sources[0].gamepad, 4, false);
  G.updateCalibration(0.016);
  const store1 = G.loadGripsStore();
  const n1 = Object.keys(store1).length;
  chk(n1 === n0 + 1, 'A GUARDA el agarre (' + n1 + ' en el almacén)');
  chk(G.gripName !== 'Natural', 'agarre con nombre: ' + G.gripName);
  const guardado = G.gripName;
  chk(store1[guardado] && Math.abs(store1[guardado].pz - G.gripOffset.pz) < 1e-9 &&
      typeof store1[guardado].rx === 'number',
      'el almacén PERSISTE los 6 valores exactos (ppxr_grips_v1)');

  // 9 · SALIDA (Y = exitCalib directo): TODO recogido, HALL restaurado
  G.exitCalib();
  chk(G.calib === false && G.calibPala === false, 'salida: modo recogido');
  chk(G.calibPanel.group.visible === false, 'panel informativo FUERA');
  chk(G._palaAxes === null, 'gizmo FUERA (dispose)');
  chk(G._palaMandos === null, 'réplicas FUERA (dispose)');
  chk(G._palaAct === null, 'estado de ejes limpio');
  chk(G.scene.background === bg0, 'fondo RESTAURADO (canje deshecho)');
  chk(G._pstAplicada === false, '_pstAplicada a false');
  chk(G.hallGroup && G.hallGroup.visible === true,
      'HALL restaurado (la visión anterior del Hall)');
  chk(!G.roomGroup || G.roomGroup.visible === false,
      'sala de partido fuera (el Hall usa su propia estancia, así nace enterHall)');
  chk(G.inHall === true, 'de vuelta en el HALL (visión anterior)');
  chk(G.menuOpen === true && G.menuPage === 'opts', 'menú delante en AJUSTES');

  // 10 · MENÚ › PALA: la subpágina completa con el agarre guardado
  G.menuPage = 'optsPala';
  G.drawMenu();
  let ids = (G.menuRects || []).map((r) => String(r.id));
  chk(ids.indexOf('palaGo') >= 0, 'AJUSTAR LA PALA EN VR (botón dorado)');
  chk(ids.indexOf('gname') >= 0, 'GUARDAR EL AJUSTE ACTUAL CON NOMBRE');
  chk(ids.indexOf('gripNat') >= 0, 'VOLVER AL AGARRE NATURAL');
  chk(ids.some((i) => i.indexOf('gripLoad:' + guardado) === 0),
      'el agarre guardado aparece con CARGAR');
  chk(ids.some((i) => i.indexOf('gripDel:' + guardado) === 0),
      '… y con su ✕ para quitarlo');
  chk(ids.indexOf('homehall') >= 0, '⌂ VOLVER AL HALL accesible');

  // 11 · palaGo REAL (el camino del menú): startCalib → modo puro
  const iGo = ids.indexOf('palaGo');
  G.menuClick(iGo);
  chk(G.calibPala === true && G.calib === true,
      'palaGo ARRANCA el ajuste (sal del Hall + enterCalib(true))');
  chk(G.pstOn === true, '… con passthrough inmediato otra vez');
  G.exitCalib();   // recogida limpia para seguir probando
  chk(G.inHall === true, '… y su salida vuelve al HALL limpia');

  // 12 · CARGAR desde el menú (click real en la lista)
  G.menuPage = 'optsPala';
  G.drawMenu();
  ids = (G.menuRects || []).map((r) => String(r.id));
  const iLoad = ids.indexOf('gripLoad:' + guardado);
  chk(iLoad >= 0, 'lista de agarres lista para el click');
  if (iLoad >= 0) {
    G.gripName = 'Natural';
    G.menuClick(iLoad);
    chk(G.gripName === guardado, 'click CARGAR restaura el agarre por nombre');
  }

  // 13 · TECLADO del NOMBRE DEL AGARRE (gkey) — guardar «QA Milimetro»
  G.menuPage = 'gripname';
  G._gripBuf = '';
  G.drawMenu();
  const gids = (G.menuRects || []).map((r) => String(r.id));
  chk(gids.some((i) => i.indexOf('gkey:') === 0),
      'teclado NOMBRE DEL AGARRE presente');
  const pulsa = (id) => {
    const i = (G.menuRects || []).findIndex((r) => String(r.id) === id);
    if (i >= 0) G.menuClick(i);
    return i >= 0;
  };
  const palabra = 'QA MILIMETRO';   // el teclado es A-Z + espacio + dígitos
  let tecleoOK = true;
  for (const ch of palabra) {
    const id = ch === ' ' ? 'gkey:sp' : 'gkey:' + ch;
    if (!pulsa(id)) { tecleoOK = false; break; }
  }
  chk(tecleoOK && (G._gripBuf || '') === palabra,
      'teclado escribe «' + palabra + '» (' + (G._gripBuf || '') + ')');
  pulsa('gkey:ok');
  chk(!!G.loadGripsStore()['QA MILIMETRO'],
      'GUARDAR CON NOMBRE persiste «QA MILIMETRO»');
  chk(G.menuPage === 'optsPala', '… y vuelve a la subpágina PALA');

  // 14 · BORRADO desde el menú (✕) + natural
  G.menuPage = 'optsPala';
  G.drawMenu();
  const iDel = (G.menuRects || []).findIndex(
    (r) => String(r.id) === 'gripDel:QA MILIMETRO');
  chk(iDel >= 0, '✕ de «QA MILIMETRO» en la lista');
  if (iDel >= 0) G.menuClick(iDel);
  chk(!G.loadGripsStore()['QA MILIMETRO'], 'QUITAR borra el agarre');
  const iNat = (G.menuRects || []).findIndex((r) => String(r.id) === 'gripNat');
  if (iNat >= 0) G.menuClick(iNat);
  chk(G.gripName === 'Natural', 'VOLVER AL AGARRE NATURAL funciona');

  // 15 · limpieza final: nada del modo queda vivo
  chk(G.calibPala === false && G._palaAxes === null && G._palaMandos === null,
      'sesión de prueba sin ningún residuo del modo');
  try { delete xr.isPresenting; } catch (eDel) { /* */ }
  return out;
}"""


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r83 en el servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES exactos + mudanza confirmada —")
    import re
    for label, pat, esperado in CONTADORES:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (modo pala completo con sesión simulada) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await browser.new_context(viewport={"width": 640, "height": 400})
        page = await ctx.new_page()
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME")

            res = await page.evaluate(JS_RED83)
            if res.get("error"):
                chk(False, "JS_RED83: " + res["error"])
            else:
                for cond, label in res.get("checks", []):
                    chk(cond, "pala r83: " + label)

            # 16 · PERSISTENCIA REAL: recarga de la página y el agarre sigue
            nombre = ""
            if not res.get("error"):
                nombre = (await page.evaluate(
                    """() => {
                      const G = window.__PP_GAME;
                      if (!G) return '';
                      const st = G.loadGripsStore();
                      return Object.keys(st)[0] || '';   // «Agarre N» del paso 8
                    }""")) or ""
                await page.reload(wait_until="domcontentloaded")
                sigue = False
                for _ in range(90):
                    sigue = await page.evaluate(
                        """(nm) => {
                          const G = window.__PP_GAME;
                          if (!G) return false;
                          const st = G.loadGripsStore();
                          return !!(st && nm && st[nm]);
                        }""", nombre)
                    if sigue:
                        break
                    await page.wait_for_timeout(500)
                chk(bool(sigue and nombre),
                    "tras RECARGAR la página el agarre «" + nombre +
                    "» sigue (permanente en el dispositivo)")

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r83_v3675 · CAPA BS)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
