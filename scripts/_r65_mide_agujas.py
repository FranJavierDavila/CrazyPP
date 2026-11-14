#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r65_mide_agujas.py — conteos EXACTOS de las agujas r65 sobre el
ensamblado EN MEMORIA (método r63/r64: los comentarios sobreviven al
ensamblado). Alimenta sella_r65_saque.py."""
import importlib.util
import re
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'


def ensambla() -> bytes:
    spec = importlib.util.spec_from_file_location(
        'bg', RAIZ / 'scripts' / 'build_game.py')
    bg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bg)
    return b''.join(
        bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/')
        else (SRC / n).read_bytes()
        for n, _ in bg.ORDER
    )


datos = ensambla()
txt = datos.decode('utf-8', 'replace')
print(f'ensamblado en memoria: {len(datos):,} B')

LITERALES = [
    # r65 · capa 1 · saque-primero
    'EL SAQUE ES EL DUEÑO DEL GATILLO',
    'this.tossFromHand(this.ballHand, true);',
    # r65 · capa 2 · respaldo relativo a la cabeza (glue)
    'r65 · la pose del mando libre debe ser FRESCA',
    '(performance.now() - (bh.seenT || 0)) < 400',
    'r65 · RESPALDO EN LA MANO VIRTUAL DEL JUGADOR',
    'const fSrv = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);',
    'this.ball.pos.copy(this.camera.position).addScaledVector(fSrv, 0.35);',
    # r65 · capa 3 · grip vivo
    'r65 · el EVENTO squeeze acaba de llegar de ESTE mando',
    # r65 · capa 4 · watchdog
    'r65 · WATCHDOG DEL SAQUE',
    'LA BOLA SIEMPRE VUELVE A TU MANO',
    'const bhW = this.controllerPaddles[this.ballHand];',
    '(performance.now() - (bhW.seenT || 0)) < 400',
    'const fWd = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);',
    'this.ball.pos.copy(this.camera.position).addScaledVector(fWd, 0.35);',
    'this._srvWdT = cerca ? 0 : (this._srvWdT || 0) + dt;',
    'this._srvWdT > 1.0',
    # r65 · frescura en el bucle de mandos
    'ps.seenT = performance.now();',
    # compartidos
    'this.ball.pos.y = Math.max(0.55, this.ball.pos.y - 0.55);',
    # NEGATIVA · el punto fijo viejo ha de haber desaparecido
    'this.ball.pos.set(0.3, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4)',
]
print('— literales —')
for s in LITERALES:
    print(f'  ×{datos.count(s.encode("utf-8"))}  {s[:76]}')

REGEX = [
    r'r65 ·',
    r'r65:',
    r'_srvWdT',
    r'seenT',
    r'addScaledVector\(f\w+, 0\.35\)',
    r'tossFromHand\(this\.ballHand, true\)',
]
print('— regex —')
for p in REGEX:
    print(f'  ×{len(re.findall(p, txt))}  /{p}/')
