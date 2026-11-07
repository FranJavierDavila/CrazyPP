#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 11 · GENERADOR DEL DIRECTORIO DE RELEASE v368
======================================================================
Crea scripts/release-v368/ a partir de scripts/release-v367/ con:
  · reemplazos de versión (3.6.7-SDK6 → 3.6.8-SDK6 · v367-sdk6 → v368-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 10 — ANÁLISIS DE VENTA)
Idempotente: si release-v368 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v367"
DEST = RAIZ / "scripts" / "release-v368"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo)
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 9 — RENDIMIENTO: FPS en XR optimizados)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.7-SDK6):\\n'\n"
    "    '  · FASE 9 — RENDIMIENTO (ronda 10): la telemetría vr_end midió 38 fps\\n'\n"
    "    '    de media en sesión VR larga (GPU saturada por nitidez máxima).\\n'\n"
    "    '    FramebufferScaleFactor 1.7 → 1.4 (−32% píxeles/ojo), foveation\\n'\n"
    "    '    0 → 0.5 (periferia comprimida por el compositor) y sombras\\n'\n"
    "    '    PCFSoft 2048² → PCF 1024². Objetivo: 60+ fps en Quest 3.\\n'\n"
    "    '  · TELEMETRÍA vr_end: fpsMin/fpsMax de la sesión VR (antes solo la\\n'\n"
    "    '    media de las últimas 12 muestras = 60 s).\\n'\n"
    "    '  · CERO cambios de física: el golden de los 11 escenarios queda\\n'\n"
    "    '    intacto (solo presentación y telemetría).\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 10 — ANÁLISIS DE VENTA: embudo por campeonato)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.7-SDK6):\\n'\n"
    "    '  · FASE 10 — ANÁLISIS (ronda 11): los eventos stage y champion\\n'\n"
    "    '    llevan el ID del campeonato (Magia, La Locura) — el panel\\n'\n"
    "    '    /telemetria separa el embudo POR CAMPEONATO: etapas, títulos,\\n'\n"
    "    '    partidas, victorias, mejor puntuación y estrellas.\\n'\n"
    "    '  · champ_rank VIAJA POR la cola __PP_TELE: versión REAL del juego\\n'\n"
    "    '    (antes 2.81.0 clavada a mano), t y sid propios, y RESPETA el\\n'\n"
    "    '    opt-out (pp_tele=0) y el modo depuración.\\n'\n"
    "    '  · Manifests: Magia v32 y La Locura v23 (telemetría identificada).\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.7-SDK6", "V3.6.8-SDK6"),
    ("3.6.7-SDK6", "3.6.8-SDK6"),
    ("v367-sdk6", "v368-sdk6"),
    ("v367", "v368"),
    ("V3.6.7", "V3.6.8"),
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
            print(f"  ✓ {f.name}: notas FASE 10 insertadas")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        if len(txt) != antes or True:
            f.write_text(txt, encoding="utf-8")
            print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v368 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.7-SDK6", "v367-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.8-SDK6" not in bz or "FASE 10" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    print("· release-v368 listo → python3 scripts/release-v368/build_zip.py")


if __name__ == "__main__":
    main()
