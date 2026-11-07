#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r85 · Ajusta el manifest del Campeonato de Halloween al arte real del dueño:
   rival ZOMBI con las 12 poses, mapa modo arte con los 5 nodos medidos,
   poderes temáticos (Niebla de tumba + Orbe espectral), salas provisionales,
   coronación temática, i18n (normas provisionales de las etapas 2 y 4),
   estado 'publicado' + registro en championships.json (retira valle_neon)."""
import json, os, sys

RAIZ = '/home/z/my-project'
CH = os.path.join(RAIZ, 'public', 'championships', 'halloween')
MAN = os.path.join(CH, 'manifest.json')
REG = os.path.join(RAIZ, 'public', 'championships', 'championships.json')

m = json.load(open(MAN, encoding='utf-8'))

# ---------------------------------------------------------------- identidad
m['version'] = 1
m['estado'] = 'publicado'          # el arte del dueño ya define el campeonato
m['title'] = {'es': 'Campeonato de Halloween', 'en': 'Halloween Championship'}
m['description'] = {
    'es': 'Un cementerio bajo la luna donde el ZOMBI defiende su cripta: cinco etapas '
          'entre niebla, dianas que brotan de la tierra y un duelo final aullante.',
    'en': 'A moonlit graveyard where the ZOMBIE defends his crypt: five stages of fog, '
          'targets rising from the soil and a howling final duel.',
}

# -------------------------------------------------------------------- rival
m['rival']['states'] = ['present', 'idle', 'focused', 'surprised', 'panic',
                        'laughing', 'crazy', 'angry', 'picando', 'loosing',
                        'defeated', 'victory']
m['rival']['personalidad'] = {
    'agresividad': 4, 'precision': 3, 'constancia': 4,
    'caracter': 'siniestro',
    'celebracion': 'Alienta a los muertos y estremece la noche con su risa.',
    'cerebro': 'equilibrado',
}
m['rivalVisual'] = {
    'modo': 'precarga',
    'base': 'present.webp',
    'ext': 'webp',
    'alto': 2.15,
    'anchoFijo': 0,
    'material': 'basic',
    'alphaTest': 0.25,
    'flotacion': {'activo': True, 'amplitud': 0.012, 'periodo': 1.4},
    'aspecto': True,
}

# ------------------------------------------------------------------- camino
m['stages'] = [
    {'id': 'duelo1', 'name': 'Duelo en la Niebla', 'kind': 'duelo'},
    {'id': 'prueba1', 'name': 'La Cripta Sellada', 'kind': 'dianas',
     'rules': {'modo': 'objetivos', 'objetivo': 6, 'puntos': 2,
               'premio': 'Calavera de Oro'}},
    {'id': 'duelo2', 'name': 'Duelo de la Luna', 'kind': 'duelo'},
    {'id': 'prueba2', 'name': 'El Pozo del Cometa', 'kind': 'dianas',
     'rules': {'modo': 'movimiento', 'objetivo': 4, 'puntos': 3,
               'premio': 'Sello del Cometa'}},
    {'id': 'final', 'name': 'DUELO FINAL', 'kind': 'duelo', 'rules': {'jefe': True}},
]

# -------------------------------------------------------------------- mapa
# Nodos medidos sobre el arte del dueño (1380x752): los 5 medallones del camino.
m['mapa'] = {
    'modo': 'arte',
    'arte': 'assets/mapa.webp',
    'planoW': 1.66,
    'rotY': 0.42,
    'nodos': [
        {'x': 148, 'y': 392, 'r': 118, 'ts': 1},    # 1 · zombi listo (duelo 1)
        {'x': 355, 'y': 592, 'r': 110, 'ts': 1},    # 2 · cripta esquelética (prueba 1)
        {'x': 875, 'y': 202, 'r': 112, 'ts': 1},    # 3 · zombi risueño (duelo 2)
        {'x': 890, 'y': 556, 'r': 104, 'ts': 1},    # 4 · pozo del cometa (prueba 2)
        {'x': 1265, 'y': 332, 'r': 120, 'ts': 1},   # 5 · zombi aullante (DUELO FINAL)
    ],
}

# ----------------------------------------------------------------- poderes
m['powers'] = [
    {'kind': 'mareo', 'name': 'Niebla de tumba', 'icon': 'assets/power_0.png',
     'cooldown': 16, 'duration': 6, 'warn': 2, 'activacion': 'rally', 'chance': 0.32},
    {'kind': 'orbe', 'name': 'Orbe espectral', 'icon': 'assets/power_1.png',
     'cooldown': 20, 'duration': 8, 'warn': 2, 'activacion': 'puntos', 'cadaCuantos': 3},
]

# ------------------------------------------------------------------- audio
m['audio'] = {
    'music': 'assets/bso.wav',
    'musicVolume': 0.18,
    'musicOpts': {'fadeIn': 0.8, 'ancla': True, 'syncMode': 'ramp',
                  'gateStart': True, 'gateOn': False, 'renace': True, 'stopFade': 0},
    'sounds': {'laugh': 'assets/risas.mp3'},
}

# -------------------------------------------------------------------- room
m['room'] = {
    'floor': 'assets/sala_floor.jpg', 'ceil': 'assets/sala_ceil.jpg',
    'back': 'assets/sala_back.jpg', 'front': 'assets/sala_front.jpg',
    'left': 'assets/sala_left.jpg', 'right': 'assets/sala_right.jpg',
    'variants': {'final': {'tint': 2770474}},   # 0x2a4d2a · noche verde tóxica en el JEFE
}

# ------------------------------------------------------------------- decor
# Los 4 troqueles llegan en la siguiente tanda (dicho por el dueño).
m['decor'] = {'pieces': []}

# ------------------------------------------------------------------ trophy
m['trophy'] = {
    'name': {'es': 'Trofeo de la Calavera', 'en': 'Skull Trophy'},
    'arte': 'assets/insignia.png',
    'rotY': 0.62,
}

# -------------------------------------------------------------- coronación
m['coronacion'] = {
    'titulo': {'es': '¡ZOMBI DERROTADO!', 'en': 'ZOMBIE DEFEATED!'},
    'mensaje': {'es': 'La cripta es tuya: el cementerio descansa en paz… por hoy.',
                'en': 'The crypt is yours: the graveyard rests in peace… for today.'},
    'dur': 14, 'insignia': 'assets/insignia.png',
    'stats': ['puntos', 'duelos', 'fecha'],
}

# --------------------------------------------------------------------- i18n
# Normas PROVISIONALES de las etapas 2 y 4 (mecánicas por definir en futuras
# tandas — lo dice el dueño). Salen sobre el cartel del artista (NORMAS_SKIN).
m['i18n'] = {
    'es': {
        'bienvenida': 'Bienvenido al Campeonato de Halloween',
        'instr_titulo': 'Las normas del cementerio',
        'instr_lineas': [
            'Las dianas brotan de la tierra entre la niebla: reviéntalas antes de que se agote el tiempo',
            'En El Pozo del Cometa las dianas se mueven: apunta al vuelo',
            'Si fallas, el ZOMBI se ríe; si aciertas, la cripta tiembla',
            'Mecánica secreta de esta prueba: por anunciar',
        ],
        'duelo_vs': '¡DUELO! VS ZOMBI · Ronda {n}',
        'prueba_vs': '¡PRUEBA! {nombre} · Intento {n}',
        'sello_leyenda': 'Sello de leyenda {n} conseguido',
        'leyenda_medalla': 'LEYENDA COMPLETA: los 5 sellos son tuyos.',
        'coronacion_titulo': '¡CAMPEÓN DE HALLOWEEN!',
        'coronacion_msg': 'El trono de la cripta es tuyo. Bienvenido a la leyenda.',
        'reset_ok': 'Registros eliminados.',
    },
    'en': {
        'bienvenida': 'Welcome to the Halloween Championship',
        'instr_titulo': 'The graveyard rules',
        'instr_lineas': [
            'Targets rise from the foggy soil: smash them before time runs out',
            'In The Comet Pit targets move: aim on the fly',
            'Miss and the ZOMBIE laughs; score and the crypt trembles',
            'Secret mechanic of this trial: to be announced',
        ],
        'duelo_vs': 'DUEL! VS ZOMBIE · Round {n}',
        'prueba_vs': 'TRIAL! {nombre} · Attempt {n}',
        'sello_leyenda': 'Legend seal {n} earned',
        'leyenda_medalla': 'FULL LEGEND: all 5 seals are yours.',
        'coronacion_titulo': 'HALLOWEEN CHAMPION!',
        'coronacion_msg': 'The crypt throne is yours. Welcome to legend.',
        'reset_ok': 'Records wiped.',
    },
}

m['assets'] = ('assets/ (12 poses del zombi del dueño en webp, mapa.webp del dueño, '
               'normas_halloween.png del dueño, sala_*.jpg procedimentales PROVISIONAL, '
               'bso.wav PROVISIONAL, risas.mp3 PROVISIONAL, power_0/1.png, insignia.png)')
m['notes'] = [
    'v1 (r85) · Campeonato de Halloween — el campeonato del Valle Neón se RETIRA a '
    'petición del dueño y su hueco lo ocupa Halloween: rival ZOMBI con las 12 poses '
    'del artista (upload/zombi.zip), mapa del artista con 5 nodos medidos '
    '(upload/Mapa.png) y cartel de normas del artista (upload/zombi_normas.png) para '
    'las etapas 2 y 4.',
    'PROVISIONAL: sala (cementerio procedimental), bso (del valle) y risa — el dueño '
    'pasará el escenario real (6 planos) y los 4 troqueles en la siguiente tanda; las '
    'mecánicas de las etapas 2 y 4 se definen en futuras tandas (hoy dianas).',
]

json.dump(m, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
open(MAN, 'a', encoding='utf-8').write('\n')
print('manifest ajustado:', MAN)

# ----------------------------------------------------------- championships
reg = json.load(open(REG, encoding='utf-8'))
ids = [e['id'] if isinstance(e, dict) else e for e in reg.get('championships', [])]
if 'valle_neon' in ids:
    reg['championships'] = [e for e in reg['championships']
                            if (e['id'] if isinstance(e, dict) else e) != 'valle_neon']
    print('valle_neon retirado del índice')
if 'halloween' not in [e['id'] if isinstance(e, dict) else e for e in reg['championships']]:
    reg['championships'].append('halloween')
    reg['version'] = int(reg.get('version', 0)) + 1
reg['generado'] = ('2026-10-28 r85 · Campeonato de Halloween (rival ZOMBI del dueño) '
                   'sustituye a valle_neon — retirado a petición del dueño')
json.dump(reg, open(REG, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(REG, 'a', encoding='utf-8').write('\n')
print('championships.json:', reg['version'], [e['id'] if isinstance(e, dict) else e for e in reg['championships']])
print('OK')
