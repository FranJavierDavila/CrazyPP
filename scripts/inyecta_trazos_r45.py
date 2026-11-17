#!/usr/bin/env python3
"""r45 · inserta el const ARCANO_PALAS_TRAZO (polilíneas de palas.png) en
c08_hall_hud.js justo antes de montarArcano. Idempotente."""
import json

C08 = '/home/z/my-project/src/game/core/c08_hall_hud.js'
JS = '/home/z/my-project/scripts/constelacion_palas.json'
MARCA = '/** MONTA el espacio arcano.'

datos = json.load(open(JS))
bloque = (
    '/* =====================================================================\n'
    ' *  r45 · TRAZOS DE LA CONSTELACIÓN DE PALAS — el contorno de palas.png\n'
    ' *  (arte del dueño) reducido a 16 polilíneas ordenadas como traza un\n'
    ' *  bolígrafo (encadenado por extremos próximos, extraído del canal\n'
    ' *  alfa del PNG con esqueleto + grafo 8-conexo + Douglas-Peucker 0.8).\n'
    ' *  Coordenadas normalizadas: x −0.5..0.5, y abajo→arriba positivo.\n'
    ' *  La consume montaConstelacion() (mismo fichero).\n'
    ' *  ===================================================================== */\n'
    'const ARCANO_PALAS_TRAZO = ' + json.dumps(datos, separators=(',', ':')) + ';\n\n'
)

src = open(C08).read()
if 'ARCANO_PALAS_TRAZO' in src:
    print('ya insertado — nada que hacer')
else:
    i = src.index(MARCA)
    open(C08, 'w').write(src[:i] + bloque + src[i:])
    print('insertado en byte', i, '· trazos:', len(datos))
