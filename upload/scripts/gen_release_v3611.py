#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 14 · GENERADOR DEL DIRECTORIO DE RELEASE v3611
======================================================================
Crea scripts/release-v3611/ a partir de scripts/release-v3610/ con:
  · reemplazos de versión (3.6.10-SDK6 → 3.6.11-SDK6 · v3610-sdk6 → v3611-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 13 — FLUIDEZ: reversión
    de nitidez 1.5→1.4 por datos + sesiones VR en el panel)
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3611 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3610"
DEST = RAIZ / "scripts" / "release-v3611"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo).
# La aguja EMPIEZA en 'Rama (sin indentar): el reemplazo respeta la
# sangría de 4 espacios que ya tiene la línea en el fichero.
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 12 — NITIDEZ: framebufferScaleFactor 1.5 por datos)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.9-SDK6):\\n'\n"
    "    '  · FASE 12 — NITIDEZ (ronda 13): framebufferScaleFactor 1.4 →\\n'\n"
    "    '    1.5 (+15% píxeles/ojo sobre el 1.4 «Extra Sharpness» de\\n'\n"
    "    '    Meta). Lo aprueba la telemetría: la primera sesión VR en\\n'\n"
    "    '    3.6.9 midió 78 fps de media (63-88) — margen claro sobre\\n'\n"
    "    '    los 72 de confort.\\n'\n"
    "    '  · Foveation 0.5 sin cambios: la periferia sigue comprimida\\n'\n"
    "    '    por el compositor (imperceptible en juego).\\n'\n"
    "    '  · Si el vr_end de esta versión diera media < 72 fps, volver\\n'\n"
    "    '    a 1.4 es un ajuste de una línea.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 13 — FLUIDEZ: reversión nitidez 1.5→1.4 por datos)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.10-SDK6):\\n'\n"
    "    '  · FASE 13 — FLUIDEZ (ronda 14): la regla pre-comprometida\\n'\n"
    "    '    («media < 72 fps → volver a 1.4») se cumplió en la primera\\n'\n"
    "    '    sesión real en 3.6.10: 63 fps de media (41-82) con el 1.5×,\\n'\n"
    "    '    frente a 78 (63-88) con el 1.4×. Se vuelve a 1.4× «Extra\\n'\n"
    "    '    Sharpness»: la fluidez manda sobre la nitidez extra.\\n'\n"
    "    '  · SESIONES VR en el panel /telemetria: permanencia real en el\\n'\n"
    "    '    casco — duración del vr_end o estimada por el latido vr_ping\\n'\n"
    "    '    (primer ping real: 68 fps al minuto 5), estado por sesión y\\n'\n"
    "    '    curva de fps con la línea de los 72 de confort.\\n'\n"
    "    '  · Los bots de verificación dejan de emitir boot a producción\\n'\n"
    "    '    (opt-out pp_tele=0 en el verificador en vivo).\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.10-SDK6", "V3.6.11-SDK6"),
    ("3.6.10-SDK6", "3.6.11-SDK6"),
    ("v3610-sdk6", "v3611-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 13 insertadas")
            # guard del COMPLETO (lección ronda 10/11/12/13): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.10"' in txt:
                txt = txt.replace('grep -c "3.6.10"', 'grep -c "3.6.11"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.11")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.11-SDK6") == 1:
            txt = txt.replace("frente a V3.6.11-SDK6", "frente a V3.6.10-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.10)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3611 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.10-SDK6", "v3610-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.11-SDK6" not in bz or "FASE 13" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    print("· release-v3611 listo → python3 scripts/release-v3611/build_zip.py")


if __name__ == "__main__":
    main()
