#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r101_edits — Ronda 101 (V3.6.93): arregla la r100.

 1) c12: REVERTIR el velInst del lanzamiento del saque (tossFromHand) —
    comportamiento EXACTO de V3.6.91 (el dueño: «volver al estado anterior
    donde sí funcionaban bien los saques»).
 2) c13: REVERTIR el hook del gatillo (serveTrigger V3.6.91) y el velInst
    del tee; SUSTITUIR el ajuste por rayo+gatillo (que «se pisaba» el
    gatillo y no coincidía lo apuntado con los botones) por AJUSTE POR
    PROXIMIDAD sin ningún botón: la mano libre entra en el pasillo de la
    cinta (≥0,30 s) y la barra sigue su altura en pasos de 1 cm; apartar
    la mano fija y guarda (persistencia pp_train_barra_v1).
 3) c02: umbral de reposo ÚNICO 0,25 m/s (el dual 0,95/0,65 de r100
    secuestraba botes suaves — «botar la bola sobre la pala» imposible).
 4) c05: el contacto de reposo usa el umbral único; el comentario lo
    documenta; transporte y despegue r100 intactos.

Cada empalme verifica ancla inicial y final únicos ANTES de escribir.
"""
import sys

RAIZ = '/home/z/my-project/'


def lee(f):
    return open(RAIZ + f, 'rb').read()


def guarda(f, b):
    open(RAIZ + f, 'wb').write(b)


def span(b, ini, fin, nombre, incluir_fin=True):
    """Localiza [ini, fin] (fin incluido si incluir_fin) con anclajes únicos."""
    i = b.find(ini)
    assert i >= 0, 'ANCLA INI no encontrada: ' + nombre
    assert b.find(ini, i + 1) < 0, 'ANCLA INI duplicada: ' + nombre
    j = b.find(fin, i)
    assert j >= 0, 'ANCLA FIN no encontrada: ' + nombre
    assert b.find(fin, j + 1) < 0, 'ANCLA FIN duplicada: ' + nombre
    return (i, j + len(fin)) if incluir_fin else (i, j)


def sustituye(b, ini, fin, nuevo, nombre):
    i, j = span(b, ini, fin, nombre)
    return b[:i] + nuevo + b[j:]


def linea_que_contiene(b, aguja, nuevo, nombre):
    """Sustituye la ÚNICA línea que contiene `aguja` por `nuevo` (sin \\n)."""
    i = b.find(aguja)
    assert i >= 0, 'AGUJA no encontrada: ' + nombre
    assert b.find(aguja, i + 1) < 0, 'AGUJA duplicada: ' + nombre
    a = b.rfind(b'\n', 0, i) + 1
    z = b.find(b'\n', i)
    return b[:a] + nuevo.encode('utf-8') + b[z:]


OK = []

# ════════════════════════════════════════════════ c12 · SAQUE A V3.6.91 ══
f = 'src/game/core/c12_pingponggame.js'
b = lee(f)
b = sustituye(
    b,
    b'    // r100 \xc2\xb7 LANZAMIENTO FIEL AL GESTO (informe del due\xc3\xb1o: \xc2\xabel primer saque',
    b'    if (hand.velInst && hand.velInst.lengthSq() > v.lengthSq()) v.copy(hand.velInst);\n',
    b'',   # ELIMINAR el bloque completo (comentario + if)
    'c12: bloque velInst de tossFromHand')
guarda(f, b)
OK.append('c12: tossFromHand vuelve a V3.6.91 (velInst fuera)')

# ══════════════════════════════════════════ c02 · UMBRAL DE REPOSO ÚNICO ══
f = 'src/game/core/c02_cfg_escena.js'
b = lee(f)
NUEVO_C02 = (
    b'  // --- r100/r101 \xc2\xb7 CONTACTO DE REPOSO pala-bola (el est\xc3\xa1ndar Eleven) ---\n'
    b'  // Petici\xc3\xb3n del due\xc3\xb1o: \xc2\xabsi paramos la bola sobre la pala va a trompicones\xe2\x80\xa6\n'
    b'  // y si levanto la pala la bola la atraviesa\xc2\xbb. r100 lo implement\xc3\xb3 con\n'
    b'  // umbral dual 0,95/0,65 y el due\xc3\xb1o lo devolvi\xc3\xb3: con 0,95 la pala\n'
    b'  // SECUESTRABA los botes leg\xc3\xadtimos (botar la bola sobre la pala mor\xc3\xada\n'
    b'  // al tercer toque y las llegadas suaves quedaban pegadas). r101:\n'
    b'  // umbral \xc3\x9aNICO 0,25 m/s \xe2\x80\x94 s\xc3\xb3lo se posa una bola REALMENTE quieta (el\n'
    b'  // redil de gravedad por frame a 72 Hz es ~0,14 m/s: la bola apoyada\n'
    b'  // re-captura en silencio cada frame, sin trompicones) y CUALQUIER\n'
    b'  // bote con vida (>0,25) BOTA con la f\xc3\xadsica de golpe de siempre.\n'
    b'  paddleRestSpeed: 0.25,    // vRelN <= esto al llegar = APOYO (no golpe, sin rebote)\n'
    b'  paddleRestFric: 0.38,     // fricci\xc3\xb3n tangencial por re-contacto (deslizar/rodar)\n'
    b'  paddleRestMuS: 0.35,      // fricci\xc3\xb3n est\xc3\xa1tica: gravedad tangencial menor no desliza\n'
    b'  paddleRestDrop: 0.09,     // s de edad del apoyo sin re-confirmar antes de soltar\n'
    b'  paddleRestCarry: 0.5,     // pala m\xc3\xa1s lenta que esto ARRASTRA la bola apoyada\n'
)
b = sustituye(
    b,
    b'  // --- r100 \xc2\xb7 CONTACTO DE REPOSO pala-bola (el est\xc3\xa1ndar Eleven) ---',
    b'  paddleRestBounce: 0.35,   // fricci\xc3\xb3n (Coulomb suavizado) del apoyo en un bote suave\n',
    NUEVO_C02,
    'c02: bloque de constantes de reposo')
guarda(f, b)
OK.append('c02: umbral \xc3\xbanico paddleRestSpeed 0.25 (0.95/0.65 y bounce retirados)')

# ════════════════════════════════════ c05 · CONDICIÓN DE REPOSO (r101) ══
f = 'src/game/core/c05_colisiones_ia_golpeo.js'
b = lee(f)
NUEVO_C05 = (
    b'  /* ================================================================\n'
    b'   * r100/r101 \xc2\xb7 CONTACTO DE REPOSO pala-bola (el est\xc3\xa1ndar Eleven).\n'
    b'   * r100 lo estren\xc3\xb3 con umbral dual 0,95 (pala lenta) / 0,65 (pala\n'
    b'   * viva) y el due\xc3\xb1o lo devolvi\xc3\xb3: \xc2\xabno has sabido resolver lo del\n'
    b'   * contacto de la bola parada y has estropeado los saques\xc2\xbb \xe2\x80\x94 con\n'
    b'   * 0,95 la pala SECUESTRABA botes leg\xc3\xadtimos (botar la bola sobre la\n'
    b'   * pala mor\xc3\xada al tercer toque; llegadas suaves quedaban pegadas en\n'
    b'   * pleno intercambio). r101: umbral \xc3\x9aNICO 0,25 m/s \xe2\x80\x94 se posa S\xc3\x93LO\n'
    b'   * una bola realmente quieta (el redil de gravedad por frame ~0,14\n'
    b'   * m/s a 72 Hz queda dentro: el apoyo re-captura en silencio cada\n'
    b'   * frame, sin trompicones) y todo lo que llegue con vida BOTA por la\n'
    b'   * v\xc3\xada de golpe normal (restituci\xc3\xb3n, spin y suelo FEEL1 de siempre,\n'
    b'   * byte a byte). El transporte en stepPhysics (bloque r100) sigue\n'
    b'   * arrastrando la bola apoyada 1:1 y el swing la suelta limpio:\n'
    b'   * levantar la pala la lanza al aire \xe2\x80\x94 Eleven. */\n'
    b'  if (pad.who === \'player\' && !pad.serveFlight && !onHandle &&\n'
    b'      Math.abs(lhz) >= hT &&\n'
    b'      -vRelN <= DIMS.paddleRestSpeed) {\n'
)
b = sustituye(
    b,
    b'  /* ================================================================\n'
    b'   * r100 \xc2\xb7 CONTACTO DE REPOSO pala-bola (el est\xc3\xa1ndar Eleven).',
    b'        : DIMS.paddleRestSpeed)) {     // pala viva: umbral estricto (0,65)\n',
    NUEVO_C05,
    'c05: condici\xc3\xb3n del contacto de reposo')
guarda(f, b)
OK.append('c05: reposo con umbral \xc3\xbanico DIMS.paddleRestSpeed (0,25)')

print('\n'.join('  \xe2\x9c\x93 ' + s for s in OK))
print('c05/c12/c02 escritos.')
