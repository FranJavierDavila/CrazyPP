#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r66_mide_agujas.py — conteos MEDIDOS de las agujas FASE 160 sobre el
ensamblado EN MEMORIA (método r63/r64/r65): nada se escribe, sólo medir."""
import importlib.util
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'

spec = importlib.util.spec_from_file_location(
    'bg', RAIZ / 'scripts' / 'build_game.py')
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)

datos = b''.join(
    bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/')
    else (SRC / n).read_bytes()
    for n, _ in bg.ORDER
)
txt = datos.decode('utf-8', 'replace')
print(f'ensamblado en memoria: {len(datos):,} B')

AGUJAS = [
    # FASE 160 · registro y datos
    ('const PNG_PODER_BOLALOCA', 1),
    ('const VOZ_PODER_BOLALOCA =', 1),
    ('const VOZ_PODER_BOLALOCA_EN =', 1),
    ("{ id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),", 1),
    ('voz: VOZ_PODER_BOLALOCA, vozEn: VOZ_PODER_BOLALOCA_EN, png: PNG_PODER_BOLALOCA', 1),
    ("bolaloca: ['arcono_tipo_distraccion', '#c39bff']", 1),
    ('const BOLALOCA_DUR = ARCANO_CFG.ventanas.bolaloca;', 1),
    ('const BOLALOCA_SCALE = 1.65;', 1),
    ('const BOLALOCA_HUE_V = 0.30;', 1),
    ('const BOLALOCA_SWAY = 4.0;', 1),
    ('const BOLALOCA_FREQ = 8.5;', 1),
    ('const BOLALOCA_JIT = 2.5;', 1),
    ('const BOLALOCA_JT = 0.22;', 1),
    ('bolaloca: 10,', 1),
    ('bolaloca: ARCANO_CFG.ventanas.bolaloca,', 1),
    # FASE 160 · regla SOLO 1 PODER
    ('_poderVivoAlguno()', 4),   # definición + 2 gates + ¿doc? — medir
    ('poder_uno_activo', 3),     # i18n ES + EN + uso en gate — medir
    # FASE 160 · trigger/frame/fin
    ('_bolalocaTrigger(ent) {', 1),
    ('_bolalocaFrame(dt) {', 1),
    ('_bolalocaFin() {', 1),
    ('_bolalocaAplicaFx() {', 1),
    ('this._bolalocaT = BOLALOCA_DUR;', 2),
    ('this._megaGasta(ent);', None),
    ('_bolalocaAplicaFx();', 1),
    ('pwViva(this._bolalocaT)', 1),
    ("[' _bolalocaT'".replace(' ', ''), 0),
    ("['_bolalocaT', '_bolalocaFin']", 1),
    # FASE 160 · icono activo
    ("if (ent.id === 'bolaloca') return this._bolalocaT > 0;", 1),
    ("if (this._megaActivaId === 'bolaloca') return this._bolalocaT;", 1),
    # FASE 160 · desbloqueo de serie
    ('BOLA LOCA SIEMPRE DESBLOQUEADA', 1),
    ("lista.unshift('bolaloca');", 1),
    ("return ['bolaloca'];", 1),
    ('DL_SURTIDO', 3),
    ("filter((id) => id !== 'loca')", 1),
    # FASE 160 · i18n (ES + EN)
    ("dl_bolaloca: 'BOLA LOCA',", 1),
    ("dl_bolaloca: 'CRAZY BALL',", 1),
    ("arc_bolaloca_go: '¡BOLA LOCA!", 1),
    ("arc_bolaloca_fin: 'BOLA LOCA agotada',", 1),
    ("poder_bolaloca: '¡BOLA LOCA!',", 1),
    ("arc_bolaloca_go: 'CRAZY BALL!", 1),
    ("arc_bolaloca_fin: 'CRAZY BALL worn off',", 1),
    ("poder_bolaloca: 'CRAZY BALL!',", 1),
    # FASE 160 · wiring
    ("if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent);", 1),
    ("bolaloca: '_bolalocaTrigger',", 1),
    ("else if (id === 'bolaloca') par = [VOZ_PODER_BOLALOCA, VOZ_PODER_BOLALOCA_EN];", 1),
    ("this._megaVozPrecalentar('bolaloca');", 1),
    # FASE 160 · parámetros del mago usados en frame
    ('m.material.color.setHSL(hue, 0.9, 0.58);', 1),
    ('m.material.emissive.setHSL(hue, 0.9, 0.22);', 1),
    ('Math.sin(this._bolalocaPh * BOLALOCA_FREQ)', 1),
    ('(Math.random() - 0.5) * 2 * BOLALOCA_JIT', 1),
    ('DIMS.ballRadius = this._bolalocaFx.r * BOLALOCA_SCALE;', 1),
    ('m.scale.setScalar(BOLALOCA_SCALE);', 1),
    ('this._bolalocaReloj += dt;', 1),
    # CONSERVACIÓN r65 (las 4 capas del saque siguen en el núcleo)
    ('LA BOLA SIEMPRE VUELVE A TU MANO', 1),
    ('_srvManoValida(bh) {', 1),
]

AGUJAS_RE = [
    (r'_bolalocaT', None),
    (r'_poderVivoAlguno', None),
    (r'BOLALOCA_\w+', None),
    (r'bolaloca', None),
]

for aguja, esperado in AGUJAS:
    n = txt.count(aguja)
    marca = '  ' if esperado is None else ('OK' if n == esperado else '!!')
    print(f'[{marca}] ×{n:3d} (esp {esperado if esperado is not None else "≥1"}) {aguja[:72]}')

for pat, _ in AGUJAS_RE:
    print(f'RE {pat}: ×{len(re.findall(pat, txt))}')
