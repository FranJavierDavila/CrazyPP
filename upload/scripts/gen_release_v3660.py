#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 68 · GENERADOR DEL DIRECTORIO DE RELEASE v3660
======================================================================
Crea scripts/release-v3660/ a partir de scripts/release-v3659/ con:
  · reemplazos de versión (3.6.59-SDK6 → 3.6.60-SDK6 · v3659-sdk6 → v3660-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 62 — LA RAQUETA DEL
    RIVAL), sustituido por MARCADORES, método ronda 26/59/…/67.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3660 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3659"
DEST = RAIZ / "scripts" / "release-v3660"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r67 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 61 — LA ACADEMIA EN TUS MANOS: el\\n'"
BLOQUE_FIN = "    '    CRAZY TV y los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 62 — LA RAQUETA DEL RIVAL: el@NL@'\n    'informe del dueño tras probar V3.6.59 en el Quest, punto por punto)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.59-SDK6):@NL@@NL@'\n    '  · LA RAQUETA DEL RIVAL (el dueño: «en el tutorial de la academia@NL@'\n    '    la pelota en el saque y en el juego debe ser golpeada por la@NL@'\n    '    raqueta del rival; en estos momentos permanece quieta y la@NL@'\n    '    pelota la golpea un fantasma»): el PROFESOR de la academia tiene@NL@'\n    '    por fin SU pala — la misma pala del juego, viva en la escena al@NL@'\n    '    lado lejano de la mesa. ARMA el golpe (retroceso siguiendo la@NL@'\n    '    bola), BARRE hasta ella y el golpe sale EXACTAMENTE cuando la@NL@'\n    '    hoja pasa por la bola: el saque demo, el saque del marcador y@NL@'\n    '    cada devolución del intercambio y de la práctica se VEN@NL@'\n    '    golpear. Adiós al golpe fantasma.@NL@@NL@'\n    '  · SAQUES CON ESPERA HONESTA: la bola quieta del profesor ya no@NL@'\n    '    despega por arte de magia — espera quieta mientras la hoja@NL@'\n    '    viaja (0,13 s) y despega al paso del blade. Y en LAS@NL@'\n    '    DEVOLUCIONES la bola vuelve a estar VIVA tras cada saque del@NL@'\n    '    profesor: la renumeración del guion la dejaba congelada en el@NL@'\n    '    aire (sin física, sin eventos) y el rally de ese paso no@NL@'\n    '    existía — ahora el intercambio de práctica fluye de verdad.@NL@@NL@'\n    '  · Conserva TODO lo anterior (la academia en tus manos r67: voz@NL@'\n    '    única, mandos anclados a los grips reales al 75% y una sola@NL@'\n    '    raqueta — la tuya; la academia sobre la mesa r66; el onboarding@NL@'\n    '    hablado r65; la academia a punto r64; el toque profesional r62;@NL@'\n    '    la estela de poderes, el rival adaptativo y la repetición r61;@NL@'\n    '    5 poderes, voz del selector, expresiones, bomba y eléctrico,@NL@'\n    '    passthrough en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y@NL@'\n    '    los 5 campeonatos).@NL@@NL@'\n"

GLOBALES = [
    ("V3.6.59-SDK6", "V3.6.60-SDK6"),
    ("3.6.59-SDK6", "3.6.60-SDK6"),
    ("v3659-sdk6", "v3660-sdk6"),
    ("3.6.59", "3.6.60"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.60-SDK6", "frente a V3.6.59-SDK6"),
    ("tras probar V3.6.60", "tras probar V3.6.59"),
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
            print(f"  ✓ {f.name}: notas FASE 62 insertadas")
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
