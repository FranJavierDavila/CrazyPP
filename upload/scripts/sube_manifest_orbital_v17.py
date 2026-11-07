#!/usr/bin/env python3
"""r72 · bump del manifest de estacion_orbital: version 16→17 + nota
(ASTRO EN EL RIG — el grupo del campeonato vivía en g.scene y el
recentrado del rig lo descolocaba: era la causa real de «no se ve a
Astro»; guard idempotente del standee en build + stop del muro que
restaura al rival). Actualiza TAMBIÉN VERSION.json (qa_version cruza
ambos)."""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/estacion_orbital/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
assert m['version'] == 16, f"versión inesperada: {m['version']}"
m['version'] = 17
nota = ('2026-10-26 v3.6.64-SDK6 · r72: ASTRO EN EL ESPACIO CORRECTO — '
        'StockController.build colgaba el grupo del campeonato en g.scene '
        '(mundo crudo) mientras mesa/sala/mapa viven en g.rig: el '
        'RECENTRADO del Quest (updateRecenter, 25 frames tras cada sesión '
        'XR) giraba el rig y dejaba al standee girado/desplazado respecto '
        'a la mesa — causa real de «no se visualiza a Astro» y de las tres '
        'correcciones de coordenadas anteriores. Ahora game.rig.add '
        '(convención CLOWN/WIZARD) + guard idempotente del rival en build() '
        '(re-entradas no duplican el standee) + EOArkanoid.stop restaura '
        'rivalMesh.visible.')
hist = m.get('historial')
m['historial'] = ([nota] if not isinstance(hist, list) else [nota] + hist)
P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
             encoding='utf-8')

V = Path('/home/z/my-project/src/game/VERSION.json')
vd = json.loads(V.read_text(encoding='utf-8'))
assert vd['manifests']['estacion_orbital'] == 16, 'VERSION.json desalineado'
vd['manifests']['estacion_orbital'] = 17
V.write_text(json.dumps(vd, ensure_ascii=False, indent=2) + '\n',
             encoding='utf-8')
print('estacion_orbital manifest → v17 · VERSION.json manifests alineados')
