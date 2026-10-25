"""RONDA 71 · SELLADO EN CASCADA de las capas QA a 3.6.63-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-70).
El SDK (1.5.4) y los manifests del oeste (v56), locura (v27), magia (v33)
y valle_neon (v5) NO cambian esta ronda.

LECCIÓN DE LA RONDA 68 APLICADA: smoke_sdk5.py ENTRA en el plan (su pin
de versión se quedó viejo en el bump anterior y el smoke cayó).

Tamaños byte-exactos de los ZIPs v3663 (ronda 71):
  COMPLETO   133.109.480 · ligera 18.055.124 · CLOUDFLARE 133.096.094

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.62-SDK6', '3.6.63-SDK6'), ('v3662-sdk6', 'v3663-sdk6')]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3663 (ronda 71)
    ('133106952', '133109480'),   # COMPLETO
    ('18052596', '18055124'),     # ligera
    ('133093565', '133096094'),   # CLOUDFLARE
]

PLAN = [
    ('qa_sup1_v365.py', VERSIONES[:1]),
    ('qa_imp2_v351.py', VERSIONES[:1]),
    ('qa_escudo_v350.py', VERSIONES[:1]),
    ('qa_poderes_iman_v3637.py', VERSIONES[:1]),
    ('qa_poderes_v3638.py', VERSIONES[:1]),
    ('qa_poderes_reset_v3639.py', VERSIONES[:1]),
    ('qa_poderes_activo_v3640.py', VERSIONES[:1]),
    ('qa_bomba_v3644.py', VERSIONES[:1]),
    ('qa_electrico_v3645.py', VERSIONES[:1]),
    ('qa_superpoderes_v3643.py', VERSIONES[:1]),
    ('qa_portal_v3642.py', VERSIONES[:1]),
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

fallos = 0
for nombre, reemplazos in PLAN:
    f = SCR / nombre
    txt = f.read_text(encoding='utf-8')
    for viejo, nuevo in reemplazos:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: {viejo} → {nuevo} (×{n})')
        elif nuevo in txt:
            print(f'  · {nombre}: {nuevo} ya sellado')
        else:
            print(f'  ? {nombre}: ni {viejo} ni {nuevo} (¿capa sin sello?)')
    # tamaños de ZIPs (solo donde existan)
    for viejo, nuevo in TAMANOS:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: tamaño {viejo} → {nuevo} (×{n})')
    f.write_text(txt, encoding='utf-8')

print('SELLADO r71:', 'OK' if fallos == 0 else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)
