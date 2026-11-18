#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 16 · GENERADOR DEL DIRECTORIO DE RELEASE v3613
======================================================================
Crea scripts/release-v3613/ a partir de scripts/release-v3612/ con:
  · reemplazos de versión (3.6.12-SDK6 → 3.6.13-SDK6 · v3612-sdk6 → v3613-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 15 — SEGUNDA OPORTUNIDAD
    en MAGIA: perder el ORBE repite la prueba, ronda 16)
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3613 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3612"
DEST = RAIZ / "scripts" / "release-v3613"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo).
# La aguja EMPIEZA en 'Rama (sin indentar): el reemplazo respeta la
# sangría de 4 espacios que ya tiene la línea en el fichero.
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 14 — SEGUNDA OPORTUNIDAD: perder el ARKANOID repite la prueba)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.11-SDK6):\\n'\n"
    "    '  · FASE 14 — SEGUNDA OPORTUNIDAD (ronda 15): en LA LOCURA,\\n'\n"
    "    '    perder la prueba ARKANOID ya NO retrocede el camino — la\\n'\n"
    "    '    prueba se REPITE directamente (misma política que los\\n'\n"
    "    '    duelos desde v2.44). El dato mandó: en la 3.6.10 se ganó\\n'\n"
    "    '    el CLOWN Nv. 1 (etapa 0→1), se perdió el ARKANOID y el\\n'\n"
    "    '    retroceso a la etapa 0 provocó el abandono 16 s después;\\n'\n"
    "    '    3 sesiones VR (20 min) y 0 campeonatos completos.\\n'\n"
    "    '  · Con la etapa sin cambiar, re-entrar en el campeonato te\\n'\n"
    "    '    devuelve DIRECTO a la prueba (etapa impar = ARKANOID).\\n'\n"
    "    '  · La rejugada de etapas superadas (v2.96) conserva su\\n'\n"
    "    '    comportamiento: al perder restaura tu paso de origen.\\n'\n"
    "    '  · Fluidez confirmada: la primera sesión VR en 3.6.11 (1.4×)\\n'\n"
    "    '    midió 79 fps de media (48-97) en 7,7 min — la reversión\\n'\n"
    "    '    de la ronda 14 validada en producción.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 15 — SEGUNDA OPORTUNIDAD en MAGIA: perder el ORBE repite la prueba)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.12-SDK6):\\n'\n"
    "    '  · FASE 15 — SEGUNDA OPORTUNIDAD (ronda 16): en el campeonato\\n'\n"
    "    '    NEW MAGIC TRICK (MAGIA), perder la prueba del ORBE MÁGICO\\n'\n"
    "    '    ya NO retrocede el camino — la prueba se REPITE (misma\\n'\n"
    "    '    política que los duelos desde v2.44 y que La Locura desde\\n'\n"
    "    '    la ronda 15).\\n'\n"
    "    '  · El cartel de derrota lo anuncia («La prueba se repite:\\n'\n"
    "    '    ¡otra oportunidad, vuelve a intentarlo!») y el reintento\\n'\n"
    "    '    entra con su pergamino explicativo y botón EMPEZAR, con\\n'\n"
    "    '    reset idéntico a un arranque fresco (v2.63: árbitro,\\n'\n"
    "    '    saque, escena y pistola).\\n'\n"
    "    '  · Los 5 campeonatos quedan ALINEADOS en la misma política:\\n'\n"
    "    '    Locura (ronda 15) y Magia (ronda 16); Oeste, Estación\\n'\n"
    "    '    Orbital y Valle Neón ya repetían la etapa sin retroceder.\\n'\n"
    "    '  · La rejugada de etapas superadas (v2.96) conserva su\\n'\n"
    "    '    comportamiento: al perder restaura tu paso de origen.\\n'\n"
    "    '  · Fluidez estable: la primera sesión VR en la 3.6.12 (21\\n'\n"
    "    '    min) midió 73-78 fps en los pings de 5 min y alcanzó la\\n'\n"
    "    '    etapa 2 de La Locura (récord de profundidad).\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.12-SDK6", "V3.6.13-SDK6"),
    ("3.6.12-SDK6", "3.6.13-SDK6"),
    ("v3612-sdk6", "v3613-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 15 insertadas")
            # guard del COMPLETO (lección ronda 10/11/12/13/14/15): el grep del
            # hub empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.12"' in txt:
                txt = txt.replace('grep -c "3.6.12"', 'grep -c "3.6.13"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.13")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.13-SDK6") == 1:
            txt = txt.replace("frente a V3.6.13-SDK6", "frente a V3.6.12-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.12)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3613 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.12-SDK6", "v3612-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.13-SDK6" not in bz or "FASE 15" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    print("· release-v3613 listo → python3 scripts/release-v3613/build_zip.py")


if __name__ == "__main__":
    main()
