#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 67 · GENERADOR DEL DIRECTORIO DE RELEASE v3659
======================================================================
Crea scripts/release-v3659/ a partir de scripts/release-v3658/ con:
  · reemplazos de versión (3.6.58-SDK6 → 3.6.59-SDK6 · v3658-sdk6 → v3659-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 61 — LA ACADEMIA EN TUS
    MANOS), sustituido por MARCADORES, método ronda 26/59/…/66.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3659 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3658"
DEST = RAIZ / "scripts" / "release-v3659"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r66 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 60 — LA ACADEMIA SOBRE LA MESA: el\\n'"
BLOQUE_FIN = "    '    PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 61 — LA ACADEMIA EN TUS MANOS: el@NL@'\n    'informe del dueño tras probar V3.6.58 en el Quest, punto por punto)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.58-SDK6):@NL@@NL@'\n    '  · ADIÓS AL AUDIO DOBLE (el dueño: «el audio se superpone dos veces@NL@'\n    '    en varios momentos de la explicación»): el motor de voz CANCELA la@NL@'\n    '    locución viva cuando llega una nueva — una sola voz, la última@NL@'\n    '    gana. Cubre el cierre de cada paso, el STICK repetido y los@NL@'\n    '    reintentos, en la academia y en el megáfono del marcador.@NL@@NL@'\n    '  · MANDOS ANCLADOS A TUS MANOS (el dueño: «los mandos 3D que he@NL@'\n    '    subido que estén anclados a las manos reales y a los mandos@NL@'\n    '    reales, NO un modelo 3D moviéndose en el aire… y más pequeños,@NL@'\n    '    como un 75% del tamaño actual»): cada GLB (izquierdo Y/X y@NL@'\n    '    derecho B/A) vive DENTRO del espacio grip de SU mando XR — sigue@NL@'\n    '    la mano 1:1 con la orientación REAL del mando (cabeza arriba, cara@NL@'\n    '    hacia delante), al 75% del tamaño anterior, sin giro ni flotación.@NL@'\n    '    Los halos y la etiqueta viajan con el mando real: las explicaciones@NL@'\n    '    se dan SOBRE lo que tienes en la mano.@NL@@NL@'\n    '  · UNA SOLA RAQUETA: LA REAL (el dueño: «la raqueta fantasma también@NL@'\n    '    sea la que está real ya en nuestra mano y solo 1 raqueta no 2»):@NL@'\n    '    adiós a los clones fantasma — una AURA dorada pulsa sobre la PALA@NL@'\n    '    del juego que ya está en tu mano cuando el mando se convierte en@NL@'\n    '    tu raqueta, y después la academia juega EXACTAMENTE con lo que@NL@'\n    '    vas a jugar.@NL@@NL@'\n    '  · EL GUION, MÁS SENCILLO Y DIVERTIDO (el dueño: «piensa tú la mejor@NL@'\n    '    forma de explicarlo de una manera muy sencilla y divertida»): 9@NL@'\n    '    pasos en vez de 11 — bienvenida · TU MANDO, TU RAQUETA (las 4@NL@'\n    '    acciones reales y el vaivén, fusionados) · EL SAQUE (demo del@NL@'\n    '    PROFESOR sobre la mesa real con AROS GUÍA que se iluminan con los@NL@'\n    '    botes, y después 3 saques tuyos) · el intercambio · el marcador ·@NL@'\n    '    la práctica · los botones · LOS MODOS en una sola pizarra (rejilla@NL@'\n    '    2×3) · ¡a jugar! Textos re-diseñados SIN SOLAPES (nada invade la@NL@'\n    '    línea «B · saltar» ni sale de la zona negra de la pizarra).@NL@@NL@'\n    '  · Conserva TODO lo anterior (voces pausadas r66; bola dormida r66;@NL@'\n    '    la academia a punto r64; el onboarding hablado r65; el toque@NL@'\n    '    profesional r62; la estela de poderes, el rival adaptativo y la@NL@'\n    '    repetición r61; 5 poderes, voz del selector, expresiones, bomba y@NL@'\n    '    eléctrico, passthrough en caliente, SALÓN, PRO CIRCUITO, CCD,@NL@'\n    '    CRAZY TV y los 5 campeonatos).@NL@@NL@'\n"

GLOBALES = [
    ("V3.6.58-SDK6", "V3.6.59-SDK6"),
    ("3.6.58-SDK6", "3.6.59-SDK6"),
    ("v3658-sdk6", "v3659-sdk6"),
    ("3.6.58", "3.6.59"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.59-SDK6", "frente a V3.6.58-SDK6"),
]


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    print(f"· copiado {ORIGEN.name} → {DEST.name}")

    for f in sorted(DEST.iterdir()):
        if f.suffix not in (".py", ".txt", ".json", ".mjs"):
            continue
        txt = f.read_text(encoding="utf-8")
        if f.name == "build_zip.py":
            i = txt.find(BLOQUE_INI)
            if i < 0:
                print("FALLO: marcador INI del bloque no encontrado")
                sys.exit(1)
            j = txt.find(BLOQUE_FIN, i)
            if j < 0:
                print("FALLO: marcador FIN del bloque no encontrado")
                sys.exit(1)
            j += len(BLOQUE_FIN)
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 61 insertadas")
        for viejo, nuevo in GLOBALES:
            n = txt.count(viejo)
            if n:
                txt = txt.replace(viejo, nuevo)
                print(f"  ✓ {f.name}: {viejo} → {nuevo} (×{n})")
        if f.name == "build_zip.py":
            for viejo, nuevo in RESTAURA:
                n = txt.count(viejo)
                if n:
                    txt = txt.replace(viejo, nuevo)
                    print(f"  ✓ {f.name}: restaurado {viejo} → {nuevo} (×{n})")
        f.write_text(txt, encoding="utf-8")

    print(f"OK → {DEST}")


if __name__ == "__main__":
    main()
