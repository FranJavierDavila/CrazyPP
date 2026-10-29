#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r92 · manifest del Halloween: nota v6 (r92) + descripción de assets.

Informa el informe del dueño tras V3.6.83:
  «Las manos de los zombis deben salir justa de la mesa de tal forma que su
   parte inferior toque la mesa y no quede suspendida en el aire. Cambiamos
   la textura de la mesa por la nueva que adjunto. Ojo que cuando tenemos el
   superpoder calabaza, el rival no la golpea correctamente con su pala
   parece que tiene un desplazamiento y el efecto no queda bien. La calabaza
   debería girar sobre si misma al golpearla tal como haría la bola.»
El campo version se MANTIENE en 3 (contrato sin cambios, patrón r90/r91):
las notas llevan el historial."""
import json

P = '/home/z/my-project/public/championships/halloween/manifest.json'
with open(P, encoding='utf-8') as f:
    d = json.load(f)

assert d['notes'][-1].startswith('v5 (r91)'), d['notes'][-1][:20]

d['notes'].append(
    "v6 (r92) · LAS CUATRO DEL INFORME — informe del dueño tras V3.6.83: «las manos deben salir "
    "justa de la mesa, su parte inferior toca la mesa y no queda suspendida en el aire · cambiamos "
    "la textura de la mesa por la nueva que adjunto · el rival no golpea bien la calabaza con su "
    "pala, parece un desplazamiento · la calabaza debería girar sobre sí misma al golpearla tal "
    "como haría la bola». (1) MANOS ANCLADAS: base del plano a MANO_Y (tableTopY + 0,005) en TODAS "
    "las fases — fuera el ascenso +0,12 y el bob de la r89 que dejaban la mano flotando; el «nacer "
    "de abajo» lo sigue leyendo el DESENROLLADO (repeat.y 0→1 con la base fija) y el vaivén queda "
    "en rotación (pivote en la base) y respiración de escala. (2) MESA NUEVA: mesa.webp del dueño "
    "(2048×1024, cuatro losas de piedra con grietas, musgo y salpicaduras de sangre) viste el "
    "ppTableTop por el mismo camino _losaOn (SRGB + anisotropía + marco piedra oscura); losa.jpg "
    "se conserva para rollback. (3) GOLPE DEL RIVAL A LA CALABAZA: marca ppCalabaza en la bola "
    "(puesta en inicio, limpia en estallido/fin) que lee el núcleo — alcance del rival 0,21→0,12 m "
    "y punto de contacto ARRASTRADO hasta la tangente con la hoja (centro de calabaza a 7,5 cm del "
    "centro de pala, corrección ≤4,5 cm): la pala ya NO se para junto a la calabaza ni hay salto "
    "visible; la salida parte del punto tocado con computeShotVelocityReal al mismo blanco. "
    "(4) GIRO SOBRE SÍ MISMA: la calabaza lleva SU rotación arrastrada por el spin de la bola "
    "(spin·dt·0,15 = ×3 la tasa visual de la bola — en un cuerpo de 13 cm el quaternion r88 no se "
    "apreciaba): cada golpe cambia el spin y la vuelta REARRANCA — se la ve girar al golpearla.")

# assets: la textura de mesa ahora es mesa.webp (losa.jpg conservada)
d['assets'] = d['assets'].replace(
    'losa.jpg del dueño (mesa.jpg)',
    'mesa.webp del dueño (textura de mesa r92, 4 losas de piedra con sangre; losa.jpg conservada)')

with open(P, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
    f.write('\n')
print('manifest v6 nota añadida · version field =', d['version'])
