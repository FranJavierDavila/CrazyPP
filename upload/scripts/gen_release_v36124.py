#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.124-SDK6 (r28).
Crea scripts/release-v36124/ a partir de scripts/release-v36123/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 126
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36124 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36124.py
    python3 scripts/release-v36124/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36123"
DEST = RAIZ / "scripts" / "release-v36124"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 126 — BOLA JAMÁS OCULTA + SALONES DE",
    "LUJO: informe del dueño — la Súper Electricidad dejaba la bola",
    "invisible al cazarla durante el saque rival, y los 3 salones",
    "r26b «son muy cutres… la diferencia es abismal» con Locura/Wizard).",
    "  · 1 · BUG DE LA BOLA OCULTA (causa raíz TRIPLE confirmada):",
    "    (1) _elecRompe ocultaba la bola SIEMPRE, incluso quieta",
    "    preparando el saque; (2) la caducidad de los 0,9 s sólo",
    "    re-encendía con estado DISTINTO de rally — el saque de Wizard",
    "    vive como rally y saltaba la reaparición (bola invisible TODO",
    "    el rally); (3) _elecFin sólo re-encendía con _elecRotoT <= 0 y",
    "    estado rally, pero _elecFrame (el tick que cuenta los 0,9 s)",
    "    SÓLO corre con _elecT > 0: si la tormenta moría dentro de la",
    "    ventana (fin de los 10 s, cortina de etapas 2/4, salida), la",
    "    bola quedaba OCULTA PARA SIEMPRE (offline no corre _bolaGuard",
    "    y los saques de la CPU no re-encienden).",
    "  · 2 · CURA EN TRES CAPAS: ① el estallido SÓLO oculta si la bola",
    "    VUELA (|vel| > 0,5: bola quieta = estallido visual + punto del",
    "    árbitro sin ocultar nada), ② la caducidad re-enciende SIEMPRE",
    "    (respetando sólo el tránsito de portal), ③ _elecFin re-enciende",
    "    SIEMPRE con bola rota + la ESTELA restaurada con el showTrail",
    "    del dueño (bug hermano: la estela tampoco volvía nunca).",
    "  · 3 · SALONES DE LUJO (rediseño a nivel Locura/Wizard): arte PIL",
    "    NUEVO en las 18 imágenes (gradientes multi-parada, oclusión",
    "    ambiental, glow de 3 pasadas y en anillo, grano + viñeta):",
    "    NEÓN ARCADE — recreativas con partida viva en pantalla (CRT con",
    "    scanlines), letrero CRAZY ARCADE, portal INSERT COIN, sol",
    "    synthwave con cortes, rejilla geométrica, suelo espejo;",
    "    OBSERVATORIO ESTELAR — bahía octogonal con la TIERRA real",
    "    (continentes, nubes, terminador, atmósfera), consolas con",
    "    órbitas, esclusa con rayas de peligro y volante, paneles con",
    "    remaches y tuberías, placas de cubierta con guías; DOJO ZEN —",
    "    tokonoma con ensō e ikebana, shoji con Fuji al atardecer,",
    "    ranma calado, andón, cerezos, bonsái, tatami con trama y",
    "    ensō gigante, vigas con washi. Proporciones EXACTAS (SOF).",
    "  · 4 · MOBILIARIO 3D POR SALÓN (c08 — el lujo vive en la",
    "    geometría): recreativas EMISIVAS con flicker CRT (neón),",
    "    GLOBO TERRÁQUEO con anillo orbital que GIRA y FLOTA",
    "    (updateHallFx), tōrō de piedra + bambúes (dojo); montados por",
    "    montarProps() dentro de vestir() (re-vestido en vivo con",
    "    dispose), CERO PointLights nuevos (lección v2.92), pegados a",
    "    las paredes (jamás estorban la mesa).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO contra la r26b; cero cambios de códec en c09.",
    "  · TEST NUEVO: test_r28_bola_salones_v36124 (37/0) — guard de",
    "    velocidad, caducidad sin estado, _elecFin sin estado, estela",
    "    ×2, 18 SOF exactos, props 3D, sellos. Regresión r27 40/0",
    "    (sellos re-anclados r28), r26b 158/0, r26 109/0, r25 150/0,",
    "    r24 89/0, r23 81/0 y r21 63/0. bump BYTE-EXACTO",
    "    (11.183.014 B · golden bbe61385…).",
    "  SE CONSERVA TODO: modo depuración FORO3D completo (r27), bola",
    "    atractora y ráfagas r26/r26b, Súper Fénix/Crono/Hielo, los 3",
    "    salones por hitos, barrera eléctrica, skins r21, hall cabaña,",
    "    cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2, ELO,",
    "    matchmaking, halloween.",
    "  · sellada a",
    "  3.6.124",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36123", "release-v36124"),
    ("staging-v36123", "staging-v36124"),
    ("V3.6.123-SDK6", "V3.6.124-SDK6"),
    ("3.6.123-SDK6", "3.6.124-SDK6"),
    ("v36123-sdk6", "v36124-sdk6"),
    ("v36123", "v36124"),
    ("3.6.123", "3.6.124"),
    ("fase 125", "fase 126"),
    ("FASE 125", "FASE 126"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r27 a FASE 126/3.6.124 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 126 — MODO DEPURACIÓN (FORO3D)"
FIN_MARCADOR = "'  3.6.124" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.124-SDK6 lista: MODO DEPURACIÓN COMPLETO (foro3d): salones por hitos + mapas de halloween y estación orbital abiertos.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.124-SDK6 lista: la bola JAMÁS queda oculta (cura triple en la tormenta) + 3 salones rediseñados con arte de lujo y mobiliario 3D vivo.')"


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
        # bloque de notas → FASE 126 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36124 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36124/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
