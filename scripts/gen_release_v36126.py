#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.126-SDK6 (r30).
Crea scripts/release-v36126/ a partir de scripts/release-v36125/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 128
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36126 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36126.py
    python3 scripts/release-v36126/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36125"
DEST = RAIZ / "scripts" / "release-v36126"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 128 — FÉNIX JUGABLE (dinámica NORMAL",
    "por orden del dueño) + los 3 salones nuevos ILUSTRADOS con IA de",
    "imagen al nivel de Locura/Magia — informe del dueño).",
    "  · 1 · SÚPER FÉNIX — DINÁMICA NORMAL: «El efecto de Súper Fénix —",
    "    no es jugable mantener los efectos pero que la dinámica del",
    "    juego sea la de una partida normal con una pequeña penalización",
    "    para la IA… al activar el superpoder la bola salía disparada a",
    "    mucha velocidad de forma incontrolable… los saques deben",
    "    permitirse normales» — CAUSA RAÍZ: el bloque 5.55b de r26b/r29",
    "    multiplicaba la velocidad de la bola CADA FRAME del rally",
    "    (×1,18 compuesto — tope 26 m/s en un par de décimas) y de paso",
    "    disparaba el saque. CURA: boost ANULADO (constantes FENIX_MUL/",
    "    FENIX_CAP retiradas, cero multiplyScalar del poder). Los",
    "    efectos SE QUEDAN («mantener los efectos»): el fuego REAL del",
    "    Wizard, la estela naranja y las EXPLOSIONES de ascuas al",
    "    golpear pala o mesa siguen intactos. La ventaja de juego es la",
    "    PEQUEÑA penalización de la IA: FENIX_OUT_P = 0.15 — el 15 % de",
    "    las devoluciones de la IA salen LARGAS (el helper _oscuridadFalla",
    "    apunta 0,25-0,70 m más allá de la línea de fondo; el saque de",
    "    la IA — estado «serve» guiado — jamás se sabotea: SAQUES",
    "    NORMALES; en dobles también el rival 2). c04/c05 INTACTOS.",
    "  · 2 · LOS 3 SALONES NUEVOS, ILUSTRADOS CON IA (fin de lo «cutre»):",
    "    «Vuelvo a insistir en lo cutre de los halles que has creado",
    "    nuevos, fíjate en el arte y nivel de detalle del Campeonato de",
    "    la Locura y el Campeonato de la magia… Debe invocar a los",
    "    skills de arte y generación de imagen para decorar e ilustrar",
    "    todos los planos con gran riqueza de detalles gráficos busca",
    "    referencias reales de esos entornos y adáptalas a nuestro",
    "    espacio» — los 6 planos de NEÓN ARCADE, OBSERVATORIO ORBITAL y",
    "    DOJO ZEN regenerados con el modelo de generación de imagen",
    "    (18 ilustraciones ricas de 5 MB totales, el doble de riqueza",
    "    que el arte plano de r28) tras consultar REFERENCIAS REALES",
    "    (arcades ochenteros con neones, la cúpula de la ISS con la",
    "    Tierra, dojos japoneses con tatami/shoji/tokonoma). Cadena:",
    "    scripts/_r30_gen_halls.mjs (18 prompts con el estilo de",
    "    Locura/Magia) + scripts/_r30_postproceso_halls.py (recorte al",
    "    tamaño EXACTO de la spec: frente/fondo 1849×864 · laterales",
    "    2395×864 · suelo/techo 1296×1678 + enfoque y saturación).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO contra la r26b; cero cambios de códec en c09.",
    "  · TEST NUEVO: test_r30_fenix_salones_v36126 (54/0) — boost",
    "    anulado, efectos intactos, falta 15 % en las dos palas",
    "    rivales con guard de rally (saques normales), 18 planos con",
    "    medidas exactas y riqueza, generadores, c04/c05 byte-exacto.",
    "    Regresión r29 75/0, r28 37/0, r27 40/0 (re-ancladas r30 —",
    "    fase 128 + veto del boost), r26b 171/0 (re-anclada r30),",
    "    r26 109/0, r25 150/0, r24 89/0, r23 81/0 y r21 63/0.",
    "    bump BYTE-EXACTO (11.166.642 B · golden 345c9a8d…).",
    "  SE CONSERVA TODO: fuego real del Wizard en Fénix, anillos del",
    "    Crono centrados, Súper Oscuridad completa, voces Piper",
    "    animosas, iconos del dueño, bug de la bola oculta cerrado",
    "    (r28), FORO3D completo (r27), bola atractora y ráfagas",
    "    r26/r26b, barrera eléctrica, skins r21, hall cabaña, cortina",
    "    etapas 2/4, _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking,",
    "    halloween.",
    "  · sellada a",
    "  3.6.126",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36125", "release-v36126"),
    ("staging-v36125", "staging-v36126"),
    ("V3.6.125-SDK6", "V3.6.126-SDK6"),
    ("3.6.125-SDK6", "3.6.126-SDK6"),
    ("v36125-sdk6", "v36126-sdk6"),
    ("v36125", "v36126"),
    ("3.6.125", "3.6.126"),
    ("fase 127", "fase 128"),
    ("FASE 127", "FASE 128"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r29 a FASE 128/3.6.126 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 128 — SUPERPODERES"
FIN_MARCADOR = "'  3.6.126" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.126-SDK6 lista: Fénix arde con el fuego real del Wizard, los anillos del Crono van centrados en la bola y el Hielo deja paso al Superpoder de la Oscuridad (niebla + IA 35 % fuera).')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.126-SDK6 lista: Fénix ya es JUGABLE (dinámica normal, saques normales y solo la pequeña falta del 15 % para la IA) y los 3 salones lucen ilustraciones IA ricas al nivel de Locura y Magia.')"


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
        # bloque de notas → FASE 128 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36126 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36126/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
