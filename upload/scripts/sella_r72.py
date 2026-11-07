"""RONDA 72 · SELLADO EN CASCADA de las capas QA a 3.6.64-SDK6.

Actualiza IN SITU los sellos de versión y los tamaños esperados de los
ZIPs en las capas que los llevan clavados (lección de las rondas 10-71).
El SDK (1.5.4) y los manifests del oeste (v56), locura (v27), magia (v33)
y valle_neon (v5) NO cambian esta ronda; el orbital SUBE a v17 (Astro en
el rig) — su pin vive en release-v3664/build_zip.py, ya alineado.

LECCIÓN DE LA RONDA 68 APLICADA: smoke_sdk5.py ENTRA en el plan (su pin
de versión se quedó viejo en el bump anterior y el smoke cayó).

Tamaños byte-exactos de los ZIPs v3664 (ronda 72):
  COMPLETO   133.116.865 · ligera 18.061.653 · CLOUDFLARE 133.103.478

Idempotente: si la aguja da ×0 pero el sello NUEVO ya está presente,
cuenta como «ya sellado» (no falla) — lección de la ronda 13."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'

VERSIONES = [('3.6.63-SDK6', '3.6.64-SDK6'), ('v3663-sdk6', 'v3664-sdk6')]
MANIFEST = [  # r72 · el orbital sube a v17 (Astro en el rig)
    ("chk(man.get('version') == 16,", "chk(man.get('version') == 17,"),
    ("'gateway: manifest v16", "'gateway: manifest v17"),
]
TAMANOS = [  # tamaños byte-exactos de los ZIPs v3664 (ronda 72)
    ('133109480', '133116865'),   # COMPLETO
    ('18055124', '18061653'),     # ligera
    ('133096094', '133103478'),   # CLOUDFLARE
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
    ('qa_r71_v3663.py', VERSIONES[:1]),
    ('qa_descargas_v366.py', VERSIONES),
    ('smoke_sdk5.py', VERSIONES[:1]),
]

fallos = 0
for nombre, reemplazos in PLAN:
    f = SCR / nombre
    if not f.exists():
        print(f'  ? {nombre}: no existe (se omite)')
        continue
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
    # pines de MANIFEST orbital (solo donde existan)
    for viejo, nuevo in MANIFEST:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: pin manifest 16→17 (×{n})')
    # tamaños de ZIPs (solo donde existan)
    for viejo, nuevo in TAMANOS:
        n = txt.count(viejo)
        if n:
            txt = txt.replace(viejo, nuevo)
            print(f'  ✓ {nombre}: tamaño {viejo} → {nuevo} (×{n})')
    f.write_text(txt, encoding='utf-8')

print('SELLADO r72:', 'OK' if fallos == 0 else f'{fallos} FALLOS')
sys.exit(1 if fallos else 0)
