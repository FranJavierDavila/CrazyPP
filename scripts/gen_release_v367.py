#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 10 · GENERADOR DEL DIRECTORIO DE RELEASE v367
======================================================================
Crea scripts/release-v367/ a partir de scripts/release-v365/ con:
  · reemplazos de versión (3.6.5-SDK6 → 3.6.7-SDK6 · v365-sdk6 → v367-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 9 — RENDIMIENTO)
Idempotente: si release-v367 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v365"
DEST = RAIZ / "scripts" / "release-v367"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo)
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 8 — TELEMETRÍA: flujo de producción reparado)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.5-SDK5):\\n'\n"
    "    '  · FASE 8 — TELEMETRÍA (roadmap P1): el lote de __PP_TELE ahora es un\\n'\n"
    "    '    ARRAY DIRECTO (el receptor de producción rechazaba con 400 el\\n'\n"
    "    '    wrapper {app,events} desde v2.50: los lotes se perdían en silencio;\\n'\n"
    "    '    sendBeacon daba true por éxito de transporte). Mismo contrato que\\n'\n"
    "    '    el champ_rank de Magia.\\n'\n"
    "    '  · ROUTING POR HOST del endpoint: en desarrollo (localhost) los lotes\\n'\n"
    "    '    van al receptor local /api/telemetria (panel /telemetria con\\n'\n"
    "    '    lectura); en producción van al Worker.\\n'\n"
    "    '  · FASE 7 (frente a SDK4): CIERRE DEL SDK v1.x — createRival\\n'\n"
    "    '    (standee), createCartel (tablero) y createMusic (orbital) en el\\n'\n"
    "    '    SDK v1.4.0; CERO decodeAudioData en los 5 campeonatos.\\n'"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 9 — RENDIMIENTO: FPS en XR optimizados)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.5-SDK6):\\n'\n"
    "    '  · FASE 9 — RENDIMIENTO (ronda 10): la telemetría vr_end midió 38 fps\\n'\n"
    "    '    de media en sesión VR larga (GPU saturada por nitidez máxima).\\n'\n"
    "    '    FramebufferScaleFactor 1.7 → 1.4 (−32% píxeles/ojo), foveation\\n'\n"
    "    '    0 → 0.5 (periferia comprimida por el compositor) y sombras\\n'\n"
    "    '    PCFSoft 2048² → PCF 1024². Objetivo: 60+ fps en Quest 3.\\n'\n"
    "    '  · TELEMETRÍA vr_end: fpsMin/fpsMax de la sesión VR (antes solo la\\n'\n"
    "    '    media de las últimas 12 muestras = 60 s).\\n'\n"
    "    '  · CERO cambios de física: el golden de los 11 escenarios queda\\n'\n"
    "    '    intacto (solo presentación y telemetría).\\n'"
)

GLOBALES = [
    ("V3.6.5-SDK6", "V3.6.7-SDK6"),
    ("3.6.5-SDK6", "3.6.7-SDK6"),
    ("v365-sdk6", "v367-sdk6"),
    ("v365", "v367"),
    ("V3.6.5", "V3.6.7"),
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
        antes = len(txt)
        if f.name == "build_zip.py":
            if txt.count(BLOQUE_VIEJO) != 1:
                print(f"FALLO: bloque de notas ×{txt.count(BLOQUE_VIEJO)} en build_zip.py")
                sys.exit(1)
            txt = txt.replace(BLOQUE_VIEJO, BLOQUE_NUEVO)
            print(f"  ✓ {f.name}: notas FASE 9 insertadas")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        if len(txt) != antes or True:
            f.write_text(txt, encoding="utf-8")
            print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v367 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.5-SDK6", "v365-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.7-SDK6" not in bz or "FASE 9" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    print("· release-v367 listo → python3 scripts/release-v367/build_zip.py")


if __name__ == "__main__":
    main()
