#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 58 · manifest de LA LOCURA v26 → v27 (v3.6.50).

El SÚPER CLONACIÓN (5.º poder de pala, núcleo r58) necesita CAZAR las
molestias de visión del campeonato activo (petición del dueño: «estas
palas Clon tratarán de eliminar cualquier poder de molestia de visión
como confeti o el superpoder de Globos del Clown… se moverán por
pantalla destruyendo los globos (o el confeti)»).

Cambio de MÓDULO (locura, módulo v27): el Clown implementa el hook
`clonBlancos(out)` del contrato PLANTILLA-GUIA §4.2 — expone sus globos
VIVOS como blancos {x,y,z,r,vivo,kill} en el espacio de juego; el kill
usa el _popGlobo propio (mini-confeti + pop + háptica del módulo). El
confeti lo barre el NÚCLEO (createConfetti.kill, c08 r58). El resto del
módulo NO cambia (poderes, arte, BSO intactos)."""
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project')
P = RAIZ / 'public/championships/locura/manifest.json'

m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 27:
    print('manifest locura ya en v27 — nada que hacer')
else:
    assert m['version'] == 26, f'versión inesperada: {m["version"]}'
    m['version'] = 27
    m.setdefault('notes', []).append(
        '2026-10-23 v3.6.50-SDK6 · FASE 52 · BLANCOS DEL SÚPER CLONACIÓN '
        '(hook clonBlancos del contrato PLANTILLA-GUIA §4.2): los globos '
        'del Clown son CAZABLES por las 2 palas fantasma del 5.º poder de '
        'pala (núcleo r58) — {x,y,z,r,vivo,kill} en el espacio de juego, '
        'kill usa el _popGlobo propio (mini-confeti + pop + háptica). El '
        'confeti lo barre el núcleo (createConfetti.kill). Resto del '
        'módulo intacto.')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + '\n',
                 encoding='utf-8')
    print('manifest locura v26 → v27 OK (hook clonBlancos)')
