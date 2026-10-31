#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r101_edits_c13 — Ronda 101 (V3.6.93): reescribe el ajuste de la barra.

 · REVERTIR serveTrigger a V3.6.91 (el gatillo vuelve a lanzar la bola del
   tee SIEMPRE — la r100 lo consumía para las flechas: «se traba»).
 · REVERTIR el velInst del tee (serveTossFromTee) a V3.6.91.
 · SUSTITUIR flechas+rayo+gatillo por AJUSTE POR PROXIMIDAD sin botones:
   la mano libre entra en el pasillo de la cinta (≥0,30 s) → la barra sigue
   su altura en pasos de 1 cm (blip + háptica); apartar la mano fija y
   guarda. Donde apuntas = lo que mueves: cero interferencias.
 · i18n ES/EN de la prueba t2a actualizado al nuevo gesto.
 · Accesores __test adaptados (qa_r101_v3693).

Anclajes verificados como ÚNICOS antes de escribir nada.
"""
B = '/home/z/my-project/src/game/core/c13_ui_arranque.js'


def lee():
    return open(B, 'rb').read()


def guarda(b):
    open(B, 'wb').write(b)


def span(b, ini, fin, nombre, incluir_fin=True):
    if isinstance(ini, str): ini = ini.encode('utf-8')
    if isinstance(fin, str): fin = fin.encode('utf-8')
    i = b.find(ini)
    assert i >= 0, 'ANCLA INI no encontrada: ' + nombre
    assert b.find(ini, i + 1) < 0, 'ANCLA INI duplicada: ' + nombre
    j = b.find(fin, i)
    assert j >= 0, 'ANCLA FIN no encontrada: ' + nombre
    assert b.find(fin, j + 1) < 0, 'ANCLA FIN duplicada: ' + nombre
    return (i, j + len(fin)) if incluir_fin else (i, j)


def sustituye(b, ini, fin, nuevo, nombre, incluir_fin=True):
    i, j = span(b, ini, fin, nombre, incluir_fin)
    return b[:i] + nuevo + b[j:]


def linea(b, aguja, nuevo, nombre):
    i = b.find(aguja.encode('utf-8'))
    assert i >= 0, 'AGUJA no encontrada: ' + nombre
    assert b.find(aguja.encode('utf-8'), i + 1) < 0, 'AGUJA duplicada: ' + nombre
    a = b.rfind(b'\n', 0, i) + 1
    z = b.find(b'\n', i)
    return b[:a] + nuevo.encode('utf-8') + b[z:]


b = lee()

# ── S1/S2 · i18n de la prueba (ES/EN): el gesto nuevo ──────────────────────
b = linea(b,
    "m_t2a: 'PASE BAJO', m_t2a_d: 'Golpea drives profundos pasando ENTRE la red",
    "        m_t2a: 'PASE BAJO', m_t2a_d: 'Golpea drives profundos pasando ENTRE la red y la cinta naranja. Ajusta la altura de la barra acercando la MANO LIBRE a la cinta y movi\u00e9ndola arriba o abajo (aparta la mano para fijar). Si pasas por encima, el rival te remata.',",
    'i18n ES m_t2a_d')
b = linea(b,
    "m_t2a: 'LOW PASS', m_t2a_d: 'Hit deep drives passing BETWEEN the net",
    "        m_t2a: 'LOW PASS', m_t2a_d: 'Hit deep drives passing BETWEEN the net and the orange ribbon. Adjust the bar height by bringing your FREE HAND to the ribbon and moving it up or down (pull away to set). Over it and they smash you.',",
    'i18n EN m_t2a_d')

# ── S3 · bloque de estado ──────────────────────────────────────────────────
NUEVO_S3 = (
    "    /* r101 \u00b7 BARRA INTERACTIVA DEL PASE BAJO \u2014 AJUSTE POR PROXIMIDAD.\n"
    "     * La r100 lo intent\u00f3 con flechas + rayo de la mano libre y el GATILLO\n"
    "     * consumido; el due\u00f1o lo retir\u00f3: \u00abes in\u00fatil, cuesta enfocar, donde\n"
    "     * apunto y donde est\u00e1n los botones nada tienen que ver y se pisa el\n"
    "     * gatillo que suelta las bolas del tee\u00bb. En el tee TODOS los botones\n"
    "     * est\u00e1n vivos (gatillo = lanzar, grip = lanzamiento natural al soltar),\n"
    "     * as\u00ed que el ajuste NO usa NING\u00daN bot\u00f3n: la MANO LIBRE entra en el\n"
    "     * pasillo de la cinta (\u22650,30 s) y la barra pasa a SEGUIR la altura de\n"
    "     * la mano en vivo (pasos de 1 cm, blip y h\u00e1ptica por paso, clamps\n"
    "     * 5..40 cm); al APARTAR la mano del pasillo la altura queda fijada y\n"
    "     * guardada (persistencia pp_train_barra_v1). Interacci\u00f3n directa,\n"
    "     * c\u00f3moda y cero interferencias con el juego. */\n"
    "    let barraH = 0.17;\n"
    "    let barraZona = false;       // mano libre dentro del pasillo de la cinta\n"
    "    let barraZonaT = 0;          // dwell dentro del pasillo (s)\n"
    "    let barraAgarrada = false;   // la barra sigue la mano AHORA\n"
    "    try {\n"
    "      const _bh = JSON.parse(localStorage.getItem('pp_train_barra_v1') || '{}');\n"
    "      if (typeof _bh.h === 'number' && _bh.h >= 0.05 && _bh.h <= 0.40) barraH = _bh.h;\n"
    "    } catch (e) { /* sin almacenamiento: 17 cm de siempre */ }\n"
    "    const BARRA_MIN = 0.05, BARRA_MAX = 0.40;\n"
    "    const BARRA_DWELL = 0.30;                // s en el pasillo para agarrar\n"
    "    const BARRA_PASO = 0.01;                 // resoluci\u00f3n: 1 cm\n"
    "    const RIBBON_Y = () => DIMS.netTopY + barraH;         // cinta AJUSTABLE\n"
    "    const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);\n"
).encode('utf-8')
b = sustituye(
    b,
    '    /* r100 \u00b7 BARRA INTERACTIVA DEL PASE BAJO (petici\u00f3n del due\u00f1o): \u00abque',
    '    const BARRA_CM = () => Math.round((DIMS.netTopY + barraH - DIMS.tableTopY) * 100);\n',
    NUEVO_S3, 'S3 bloque de estado')

# ── S4 · texturas, lets y barraLay (nueva disposici\u00f3n) ────────────────────
NUEVO_S4 = (
    "    // r101 \u00b7 la cinta trae SUS MANDOS: r\u00f3tulo con la lectura en cm sobre la\n"
    "    // SUPERFICIE de la mesa y las dos flechas flanque\u00e1ndolo \u2014 ya no son\n"
    "    // botones de rayo: indican el ajuste por proximidad (mano libre).\n"
    "    function barraChevronTex(dir) {\n"
    "      const cv = mkCanvas(96, 96), x = cv.getContext('2d');\n"
    "      x.fillStyle = '#16202c';\n"
    "      x.beginPath();\n"
    "      if (x.roundRect) x.roundRect(6, 6, 84, 84, 20); else x.rect(6, 6, 84, 84);\n"
    "      x.fill();\n"
    "      x.lineWidth = 4; x.strokeStyle = '#8f6a3a';\n"
    "      x.stroke();\n"
    "      x.lineWidth = 11; x.lineCap = 'round'; x.lineJoin = 'round';\n"
    "      x.strokeStyle = '#ffbf5a';\n"
    "      x.beginPath();\n"
    "      if (dir > 0) { x.moveTo(26, 58); x.lineTo(48, 34); x.lineTo(70, 58); }\n"
    "      else { x.moveTo(26, 38); x.lineTo(48, 62); x.lineTo(70, 38); }\n"
    "      x.stroke();\n"
    "      return texOf(cv);\n"
    "    }\n"
    "    function pistaBarra() {\n"
    "      if (barraAgarrada) return LANG === 'en' ? 'PULL AWAY TO SET' : 'APARTA LA MANO PARA FIJAR';\n"
    "      if (barraZona) return LANG === 'en' ? 'MOVE YOUR HAND \u2191\u2193' : 'MUEVE LA MANO \u2191\u2193';\n"
    "      return LANG === 'en' ? 'BAR HEIGHT' : 'ALTURA BARRA';\n"
    "    }\n"
    "    function barraLabelTex() {\n"
    "      const cv = mkCanvas(320, 110), x = cv.getContext('2d');\n"
    "      x.clearRect(0, 0, 320, 110);\n"
    "      x.fillStyle = 'rgba(20,26,36,0.88)';\n"
    "      x.beginPath();\n"
    "      if (x.roundRect) x.roundRect(4, 4, 312, 102, 22); else x.rect(4, 4, 312, 102);\n"
    "      x.fill();\n"
    "      x.lineWidth = 4; x.strokeStyle = barraAgarrada ? '#ffe08a' : '#ffb84d';\n"
    "      x.stroke();\n"
    "      x.textAlign = 'center'; x.textBaseline = 'middle';\n"
    "      x.fillStyle = '#ffd27a';\n"
    "      x.font = 'bold 56px \"Noto Sans SC\", sans-serif';\n"
    "      x.fillText(String(BARRA_CM()) + ' cm', 160, 42);\n"
    "      x.fillStyle = (barraZona || barraAgarrada) ? '#ffe8b0' : '#9fb3c8';\n"
    "      x.font = '20px \"Noto Sans SC\", sans-serif';\n"
    "      x.fillText(pistaBarra(), 160, 84);\n"
    "      return texOf(cv);\n"
    "    }\n"
    "    let barraUp = null, barraDn = null, barraLbl = null;\n"
    "    let barraRibbon = null;                 // cinta viva (band+glow) para barraLay\n"
    "    let barraUltCm = -1;                    // repintado del r\u00f3tulo s\u00f3lo al cambiar\n"
    "    const BARRA_SEP = 0.24;                 // flechas flanqueando el r\u00f3tulo\n"
    "    function barraLay() {\n"
    "      // recoloca cinta + mandos a la altura viva (cada ajuste)\n"
    "      const by = RIBBON_Y();\n"
    "      if (barraLbl) barraLbl.position.set(0, by + 0.13, 0);\n"
    "      if (barraUp) barraUp.position.set(-BARRA_SEP, by + 0.13, 0);\n"
    "      if (barraDn) barraDn.position.set(BARRA_SEP, by + 0.13, 0);\n"
    "      if (barraRibbon) { barraRibbon.band.position.y = by; barraRibbon.glow.position.y = by + 0.02; }\n"
    "    }\n"
).encode('utf-8')
b = sustituye(
    b,
    '    // r100 \u00b7 la cinta trae SUS MANDOS: flecha arriba / flecha abajo con la',
    '    function buildRibbon() {',
    NUEVO_S4, 'S4 texturas+barraLay', incluir_fin=False)

# ── S5 · comentario de mkBoton dentro de buildRibbon ──────────────────────
b = linea(b,
    "// jugador) \u2014 el rayo de la mano libre los enfoca y el gatillo ajusta.",
    "      // jugador) \u2014 el ajuste es por PROXIMIDAD de la mano libre (sin gatillo).",
    'S5 comentario mkBoton')

# ── S6 · m\u00e1quina de ajuste (sustituye haz+tick+ajustarHover) ──────────────
NUEVO_S6 = (
    "    /* r101 \u00b7 M\u00c1QUINA DE AJUSTE (pura, verificable en QA): (px, py, pz) =\n"
    "     * posici\u00f3n de la mano libre en mundo. Dentro del pasillo de la cinta\n"
    "     * (|x| \u2264 semiancho+0,30 \u00b7 |z\u2212cinta| \u2264 0,20 \u00b7 altura cerca de la red)\n"
    "     * durante \u2265 BARRA_DWELL la barra se AGARRA y sigue la mano en pasos de\n"
    "     * 1 cm; fuera del pasillo se suelta (fijar + guardar). Sin botones. */\n"
    "    const hMano = () => G.ballHand;          // mano libre (getter del n\u00facleo)\n"
    "    function barraFijar(hRaw, salto) {\n"
    "      const sube = hRaw >= barraH;\n"
    "      const h = THREE.MathUtils.clamp(\n"
    "        Math.round(hRaw / BARRA_PASO) * BARRA_PASO, BARRA_MIN, BARRA_MAX);\n"
    "      const cambio = Math.abs(h - barraH) > 1e-9;\n"
    "      barraH = h;\n"
    "      if (cambio || salto) {\n"
    "        barraUltCm = -1;\n"
    "        barraLay();\n"
    "        barraPinta();\n"
    "      }\n"
    "      if (cambio) {\n"
    "        try { G.audio.playOsc(sube ? 640 : 480, sube ? 760 : 400, 0.05, 'sine', 0.10, 0); } catch (eBF) { /* */ }\n"
    "        try { G.haptic(hMano(), 0.12, 18); } catch (eBF2) { /* */ }\n"
    "      }\n"
    "    }\n"
    "    function barraSoltar() {\n"
    "      barraAgarrada = false;\n"
    "      barraUltCm = -1;\n"
    "      barraPinta();\n"
    "      try { localStorage.setItem('pp_train_barra_v1', JSON.stringify({ h: Math.round(barraH * 1000) / 1000 })); } catch (eBS) { /* */ }\n"
    "      try { G.audio.playOsc(520, 340, 0.09, 'triangle', 0.12, 0); } catch (eBS2) { /* */ }\n"
    "      toast((LANG === 'en' ? 'Bar: ' : 'Barra: ') + BARRA_CM() + ' cm', true);\n"
    "    }\n"
    "    function barraPinta() {\n"
    "      const cm = BARRA_CM();\n"
    "      if (barraLbl && barraUltCm !== cm) {\n"
    "        barraLbl.material.map = barraLabelTex();\n"
    "        barraLbl.material.needsUpdate = true;\n"
    "        barraUltCm = cm;\n"
    "      }\n"
    "      const tinte = barraAgarrada ? 0xffffff : (barraZona ? 0xffe0a8 : 0xbfcfe0);\n"
    "      if (barraUp) barraUp.material.color.setHex(tinte);\n"
    "      if (barraDn) barraDn.material.color.setHex(tinte);\n"
    "    }\n"
    "    function barraUpdate(px, py, pz, dt) {\n"
    "      if (!ribbonG || !ribbonG.visible) {\n"
    "        barraZona = false; barraZonaT = 0;\n"
    "        if (barraAgarrada) barraSoltar();\n"
    "        return { zona: false, agarrada: false };\n"
    "      }\n"
    "      const dz = pz - ribbonG.position.z;\n"
    "      const enZona = Math.abs(px) <= DIMS.tableHalfWidth + 0.30 &&\n"
    "        Math.abs(dz) <= 0.20 &&\n"
    "        py >= DIMS.netTopY - 0.06 && py <= DIMS.netTopY + 0.60;\n"
    "      if (enZona) {\n"
    "        barraZonaT += dt;\n"
    "        if (!barraZona) { barraZona = true; barraPinta(); }\n"
    "        if (!barraAgarrada && barraZonaT >= BARRA_DWELL) {\n"
    "          barraAgarrada = true;\n"
    "          barraFijar(py - DIMS.netTopY, true);      // agarre: la barra salta a la mano\n"
    "          try { G.audio.playOsc(300, 520, 0.10, 'triangle', 0.16, 0); } catch (eGA) { /* */ }\n"
    "        } else if (barraAgarrada) {\n"
    "          barraFijar(py - DIMS.netTopY, false);     // sigue la mano en vivo\n"
    "        }\n"
    "      } else {\n"
    "        barraZonaT = 0;\n"
    "        if (barraZona) { barraZona = false; barraPinta(); }\n"
    "        if (barraAgarrada) barraSoltar();\n"
    "      }\n"
    "      return { zona: barraZona, agarrada: barraAgarrada };\n"
    "    }\n"
    "    /* r101 \u00b7 TICK: posici\u00f3n REAL de la mano libre \u2192 m\u00e1quina de ajuste. */\n"
    "    const _bW = new THREE.Vector3();\n"
    "    function barraTick(dt) {\n"
    "      if (!ribbonG || !ribbonG.visible) { barraUpdate(0, -1, 0, dt); return; }\n"
    "      const h = G.ballHand;\n"
    "      const ray = G.rays && G.rays[h];\n"
    "      if (!ray || !G.connected || !G.connected[h]) {\n"
    "        if (barraAgarrada || barraZona) barraUpdate(0, -1, 0, dt);\n"
    "        return;\n"
    "      }\n"
    "      ray.getWorldPosition(_bW);\n"
    "      barraUpdate(_bW.x, _bW.y, _bW.z, dt);\n"
    "    }\n"
    "    /* r101 \u00b7 AJUSTE DIRECTO \u00b11 cm (QA; el juego usa barraUpdate). */\n"
    "    function barraAjustar(dir) {\n"
    "      if (!ribbonG || !ribbonG.visible) return false;\n"
    "      barraH = THREE.MathUtils.clamp(\n"
    "        Math.round((barraH + (dir > 0 ? BARRA_PASO : -BARRA_PASO)) * 1000) / 1000,\n"
    "        BARRA_MIN, BARRA_MAX);\n"
    "      barraUltCm = -1;\n"
    "      barraLay();\n"
    "      barraPinta();\n"
    "      return true;\n"
    "    }\n"
    "\n"
).encode('utf-8')
b = sustituye(
    b,
    '    /* r100 \u00b7 HAZ DE SELECCI\u00d3N de la barra (el rayo de la mano libre): l\u00ednea',
    '    // --- aro de altura (globo defensivo) ---',
    NUEVO_S6, 'S6 m\u00e1quina de ajuste', incluir_fin=False)

# ── S7 · serveTrigger a V3.6.91 ────────────────────────────────────────────
NUEVO_S7 = (
    "      serveTrigger: () => { try { serveTossFromTee(true); } catch (e) { /* nunca rompe */ } },\n"
).encode('utf-8')
b = sustituye(
    b,
    '      serveTrigger: () => {',
    '      serveRelease: (i)',
    NUEVO_S7, 'S7 serveTrigger', incluir_fin=False)

# ── S8 · velInst del tee FUERA (V3.6.91) ───────────────────────────────────
b = sustituye(
    b,
    '        // r100 \u00b7 lanzamiento FIEL al gesto (mismo fix que el n\u00facleo): si la',
    'v.copy(bh.velInst);\n',
    b'', 'S8 velInst del tee')

# ── S9 · accesores __test ──────────────────────────────────────────────────
NUEVO_S9 = (
    "      // r101 \u00b7 internos de la BARRA del pase bajo (qa_r101_v3693): accesores\n"
    "      // \u2014nunca sustituciones\u2014 de la altura viva, la lectura en cm, el estado\n"
    "      // del agarre por proximidad y los mandos (flechas + r\u00f3tulo + recolocaci\u00f3n)\n"
    "      barraH: () => barraH,\n"
    "      barraCm: () => BARRA_CM(),\n"
    "      barraEstado: () => ({ zona: barraZona, agarrada: barraAgarrada }),\n"
    "      barraUpdate,\n"
    "      barraVisSet: (v) => { if (ribbonG) ribbonG.visible = !!v; },   // QA: estado t2a\n"
    "      barraAjustar,\n"
    "      barraLay,\n"
    "      barraSpr: () => ({\n"
    "        up: barraUp ? { x: barraUp.position.x, y: barraUp.position.y } : null,\n"
    "        lbl: barraLbl ? { x: barraLbl.position.x, y: barraLbl.position.y } : null,\n"
    "        dn: barraDn ? { x: barraDn.position.x, y: barraDn.position.y } : null,\n"
    "        cinta: barraRibbon ? { band: barraRibbon.band.position.y } : null,\n"
    "        grupo: ribbonG ? ribbonG.position.z : null,\n"
    "      }) },\n"
).encode('utf-8')
b = sustituye(
    b,
    '      // r100 \u00b7 internos de la BARRA del pase bajo (qa_r100_v3692): accesores',
    '      barraHaz: () => barraHaz },',
    NUEVO_S9, 'S9 accesores __test')

# ── S10 · comentario del tick ──────────────────────────────────────────────
NUEVO_S10 = (
    "        // r101 \u00b7 mandos de la BARRA del pase bajo (t2a): la mano libre cerca\n"
    "        // de la cinta la agarra (\u22650,3 s) y la barra sigue su altura \u2014 sin gatillo\n"
    "        barraTick(dt);\n"
).encode('utf-8')
b = sustituye(
    b,
    '        // r100 \u00b7 mandos de la BARRA del pase bajo (t2a): el rayo de la mano',
    '        barraTick(dt);\n',
    NUEVO_S10, 'S10 comentario del tick')

guarda(b)
print('  \u2713 c13 reescrito: proximidad sin botones + gatillo y tee a V3.6.91')
