#!/usr/bin/env python3
"""r60 · bump del manifest de magia: version 32→33 + nota de historial
(orbe COMPLEJO a la mitad por petición del dueño)."""
import json
from datetime import date
from pathlib import Path

P = Path('/home/z/my-project/public/championships/magia/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
assert m['version'] == 32, f"versión inesperada: {m['version']}"
m['version'] = 33
nota = ('2026-10-24 v3.6.52-SDK6 · r60: ORBE COMPLEJO (etapa 4) a la mitad '
        'de ladrillos por petición del dueño — 1.419 → 515 (−63,7%) con la '
        'misma envergadura (radio 0,625 m), dianas +42% gordas (ladrillo '
        '0,125), núcleo/medio 2/3,5, sin prórrogas ni cambios de reglas — '
        'alivio de FPS (−64% de instancias).')
if isinstance(m.get('historial'), list):
    m['historial'].insert(0, nota)
else:
    m['historial'] = [nota]
P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
             encoding='utf-8')
print('magia manifest → version', m['version'], '· historial +1 nota')
