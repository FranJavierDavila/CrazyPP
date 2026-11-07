#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 61 · GENERADOR DEL DIRECTORIO DE RELEASE v3653
======================================================================
Crea scripts/release-v3653/ a partir de scripts/release-v3652/ con:
  · reemplazos de versión (3.6.52-SDK6 → 3.6.53-SDK6 · v3652-sdk6 → v3653-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 55 — ESTELA DE PODERES,
    RIVAL QUE SE ADAPTA y REPETICIÓN DEL MEJOR INTERCAMBIO — las tres
    candidatas aprobadas por el dueño).
    sustituido por MARCADORES, método ronda 26/59/60.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (los r60 vienen heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3653 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3652"
DEST = RAIZ / "scripts" / "release-v3653"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r60 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 54 — ACADEMIA DESPEJADA, TROQUELES"
              + BS_N + "'")
BLOQUE_FIN = "    '    vivo en los 5 campeonatos." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 55 — ESTELA DE PODERES, RIVAL QUE SE@NL@'
    'ADAPTA y EL MEJOR INTERCAMBIO EN PANTALLA — las tres candidatas@NL@'
    'aprobadas por el dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.52-SDK6):@NL@@NL@'
    '  · ESTELA DE PODERES: la estela de la bola VISTE LA FIRMA del poder@NL@'
    '    de pala ACTIVO mientras su ventana corre — Súper Pala ÁMBAR ·@NL@'
    '    Súper Efecto ROJO · Imán CIAN · Súper Portal VIOLETA · Clonación@NL@'
    '    AZUL FANTASMA — con transición suave y, sin poder, el color por@NL@'
    '    EFECTO (spin) de siempre: un vistazo a la bola y sabes qué poder@NL@'
    '    está corriendo.@NL@@NL@'
    '  · RIVAL ADAPTATIVO, visible y decidible: el ajuste del nivel de la@NL@'
    '    CPU con el marcador EXISTÍA desde v2.x pero era invisible e@NL@'
    '    inevitable — ahora es CONMUTADOR persistente en el HUB (junto a@NL@'
    '    la dificultad) y en AJUSTES, con mensaje de estado y transición@NL@'
    '    SUAVE (el factor se lerp-ea en el tick: la adaptación se siente,@NL@'
    '    no se trompea). Ganas → aprieta · pierdes → afloja · OFF → la@NL@'
    '    dificultad escogida, honesta, sin toques.@NL@@NL@'
    '  · REPETICIÓN DEL MEJOR INTERCAMBIO: el juego GRABA cada intercambio@NL@'
    '    (bola + pala del rival, por frames) y al terminar el partido —tras@NL@'
    '    asentar la fanfarria— REPRODUCE EL MEJOR (el de más toques, ≥3)@NL@'
    '    con fantasmas azul fantasma y su cartel REPETICIÓN. El gatillo lo@NL@'
    '    salta; la siguiente pulsación sigue siendo revancha. Sin grabación@NL@'
    '    en calib, academia ni invitado online; partido nuevo, campeón nuevo.@NL@@NL@'
    '  · VERIFICACIÓN: capa AV nueva (qa_r61_v3653, 46 checks con MECÁNICA@NL@'
    '    REAL headless: tinte pintado en el buffer por los 5 poderes,@NL@'
    '    objetivos del adaptativo con bounds, conmutador persistente y@NL@'
    '    ciclo completo de la repetición — mejor elegido, fantasmas,@NL@'
    '    interpolación, restauración exacta y puertas de grabación).@NL@@NL@'
    '  · Conserva TODO lo anterior (LA ACADEMIA, los tres arreglos r60, 5@NL@'
    '    poderes, norma de 20 toques, voz del selector, expresiones, bomba@NL@'
    '    y eléctrico, passthrough en caliente, SALÓN, PRO CIRCUITO, CCD,@NL@'
    '    CRAZY TV y los 5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.52-SDK6", "V3.6.53-SDK6"),
    ("3.6.52-SDK6", "3.6.53-SDK6"),
    ("v3652-sdk6", "v3653-sdk6"),
    ("3.6.52", "3.6.53"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.53-SDK6", "frente a V3.6.52-SDK6"),
    ("tras probar V3.6.53", "tras probar V3.6.52"),
    ("tras V3.6.53", "tras V3.6.52"),
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
            print(f"  ✓ {f.name}: notas FASE 55 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
                    print(f"  ✓ {f.name}: restaurado {nuevo!r} (×{n})")
        f.write_text(txt, encoding="utf-8")

    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    if "v369-sdk5" not in bz or "V3.6.53-SDK6" not in bz:
        print("FALLO: guard de identidad roto en build_zip.py")
        sys.exit(1)
    print("· guard v369-sdk5 intacto · V3.6.53-SDK6 presente")
    print("GEN_RELEASE_V3653 COMPLETO")


if __name__ == "__main__":
    main()
