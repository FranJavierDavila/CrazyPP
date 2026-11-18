#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.121-SDK6 (r26).
Crea scripts/release-v36121/ a partir de scripts/release-v36120/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 123
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36121 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36121.py
    python3 scripts/release-v36121/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36120"
DEST = RAIZ / "scripts" / "release-v36121"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 123 — NIEBLA DENSA + MÁS RAYOS +",
    "BARRERA ELÉCTRICA: informe del dueño tras la r25 — la tormenta",
    "se vuelve niebla real y la red crecida, un campo de energía).",
    "  · 1 · NIEBLA DENSA (informe del dueño: «las nubes están muy",
    "    cutres… debemos sustituirlas por una especie de niebla muy",
    "    densa que simula que son nubes»). Fuera los 2 borrones sprite:",
    "    banco de ELEC_NIEBLA_N=14 puffs con textura de GRADIENTE RADIAL",
    "    (bordes que se funden, cero cartón), paleta pizarra de tormenta,",
    "    SOLAPADOS (densidad real), cada puff HIERVE con fase/velocidad/",
    "    radio propios (LCG semillado — la misma niebla en cada build y",
    "    QA), respira y se ILUMINA con cada descarga (gris pizarra ↔",
    "    azul pálido con el destello del rayo — la niebla recibe la luz",
    "    como una nube real).",
    "  · 2 · BASTANTES MÁS RAYOS (dueño: «deben descargar bastantes más",
    "    rayos de tormenta»): pool 3→10 polilíneas recicladas de 9",
    "    puntos, cadencia 1,15→0,42 s y RÁFAGAS de hasta 3 rayos por",
    "    descarga (38 % + 16 %) ≈ 35 rayos por ventana de 10 s. Emisora =",
    "    puff de niebla MÁS CERCANO al objetivo (coherencia visual).",
    "    Trueno con volumen vivo (0,55-0,95) para 35 descargas sin",
    "    fatiga. Radio de interceptación 0,17 m y punto por el árbitro",
    "    INTACTOS.",
    "  · 3 · BARRERA ELÉCTRICA en la SÚPER RED (dueño: «el efecto también",
    "    más vistoso que la red al crecer parezca una barrera de",
    "    electricidad»): el plano crecido se VISTE de campo de energía —",
    "    cuerpo aditivo cian DOBLE CARA pegado a la red VIVA (lee DIMS",
    "    cada frame), 7 arcos dentados de 12 puntos que se REGENERAN cada",
    "    0,085 s con flicker (a todas las alturas y ambas caras), RIEL",
    "    superior nervioso en la coronación actual, chispas cian del pool",
    "    de la casa sobre el riel y ZUMBIDO eléctrico suave con jitter.",
    "    Destello de energizado (0,3 s) + zap al crecer. Sólo capa de",
    "    render: DIMS.netTopY sigue siendo la única verdad y la física",
    "    c04/c05 no sabe que existe. Apagado garantizado en fin natural,",
    "    salida del campeonato, cortina y startMatch (_redRestaurar).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05/c09/c02/c07 SIN",
    "    una línea nueva (diff vacío contra la r25); cero PointLights",
    "    nuevos (lección v2.92); cero asignaciones por frame (pools",
    "    reciclados).",
    "  · TEST NUEVO: test_r26_sup_v36121 (109/0) — niebla, ráfagas,",
    "    barrera, ciclo de vida, preservación r25 y garantías. Regresión",
    "    r25 150/0 (aguja de cadencia re-anclada 1.15→0.42), r24 89/0,",
    "    r23 81/0 y r21 63/0. QA A-D verde. bump BYTE-EXACTO (10.984.244",
    "    B · golden 0a3e5d65…).",
    "  SE CONSERVA TODO: skins r21, hall cabaña, cortina etapas 2/4,",
    "    _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.121",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36120", "release-v36121"),
    ("staging-v36120", "staging-v36121"),
    ("V3.6.120-SDK6", "V3.6.121-SDK6"),
    ("3.6.120-SDK6", "3.6.121-SDK6"),
    ("v36120-sdk6", "v36121-sdk6"),
    ("v36120", "v36121"),
    ("3.6.120", "3.6.121"),
    ("fase 122", "fase 123"),
    ("FASE 122", "FASE 123"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r25 a FASE 123/3.6.121 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 123 — SÚPER RED +"
FIN_MARCADOR = "'  3.6.121" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.121-SDK6 lista: SÚPER RED (red ×2 · 10 s) + SÚPER ELECTRICIDAD (tormenta sobre el rival) + CORTINA en etapas 2/4 + BOLA BLINDADA online (_bolaGuard).')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.121-SDK6 lista: NIEBLA DENSA (14 puffs que hierve y se ilumina) + RÁFAGAS ≈35 rayos + BARRERA ELÉCTRICA en la SÚPER RED.')"


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 123 (sustitución EXACTA, lección r24:
        # sin conservar la comilla de cierre del marcador FIN)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36121 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36121/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
