#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r94 · añade la nota v8 (r94) al manifest de halloween y la sube a
maniquesta 8 (nota de historial del módulo, patrón v7/r93)."""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/halloween/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))

NOTA = (
    "v8 (r94) · LA CALABAZA ES LA BOLA, SIN TESTIGOS — informe del dueño tras "
    "V3.6.85: «cuando jugamos con calabaza en determinados momentos se produce "
    "un desfase y se ve por un lado la calabaza y por otro la bola. No debería "
    "pasar, la calabaza debería ocupar el lugar exacto de la bola y esta no ver- "
    "se mientras tengamos la calabaza sin destruir». Tres garantías duras cada "
    "frame en paso(): (1) LA BOLA JAMÁS SE VE mientras la calabaza vive — el "
    "núcleo re-enseñaba ballMesh en varios caminos (toss del saque c12:4417, "
    "HELD del sacador c12:8774, reset de punto c12:1132, tránsitos/restauracio- "
    "nes c12:6316/10195) y el módulo sólo la ocultaba UNA VEZ en inicio(); ahora "
    "paso() la vuelve a ocultar DESPUÉS de esos caminos y ANTES del render — ver "
    "bola y calabaza a la vez es imposible. (2) EL LUGAR EXACTO: la calabaza "
    "copia la posición RENDERIZADA de la bola (ballMesh.position, sincronizada "
    "de ball.pos por el núcleo en el mismo frame) — bit a bit con donde la bola "
    "estaría pintada. (3) NACIMIENTO EN SITIO: inicio() la coloca en el punto "
    "vivo de la bola (antes pasaba un frame en el origen) y la marca ppCalabaza "
    "renace cada frame (si el núcleo recrea la bola entre puntos, el contacto de "
    "la IA r92 no caduca). El estallido mantiene su entrega: calabaza se oculta "
    "y la bola VUELVE en el mismo punto."
)

if not any(n.startswith('v8 (r94)') for n in m.get('notes', [])):
    m['notes'].append(NOTA)

P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('manifest halloween: nota v8 (r94) añadida —', len(m['notes']), 'notas')
