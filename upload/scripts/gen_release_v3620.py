#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 26 · GENERADOR DEL DIRECTORIO DE RELEASE v3620
======================================================================
Crea scripts/release-v3620/ a partir de scripts/release-v3619/ con:
  · reemplazos de versión (3.6.19-SDK6 → 3.6.20-SDK6 · v3619-sdk6 → v3620-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 22 — TEXTOS DEL QUAD
    LEGIBLES + i18n), sustituido por MARCADORES (método de la ronda 26).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3620 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3619"
DEST = RAIZ / "scripts" / "release-v3620"

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 21"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"

# bloque NUEVO en texto fuente de build_zip.py (los \\n literales son los
# saltos del VERSION.txt generado; los saltos reales separan literales).
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 22 — TEXTOS DEL QUAD LEGIBLES + i18n)\\n\\n'
    'Novedades de esta versión (frente a V3.6.19-SDK6):\\n'
    '  · FASE 22 (ronda 26, informe del dueño): en el PRO TRAINING\\n'
    '    por zonas, los textos pintados sobre la mesa (OBJETIVO,\\n'
    '    EVITA, FONDO, DOBLE BOTE, FONDO 15 cm) se veían EN ESPEJO\\n'
    '    desde el jugador y sólo existían en español.\\n'
    '  · Causa: con el flipY=false de la FASE 21 el jugador ve el\\n'
    '    lienzo con la fila 0 en la red; el rotate(π) histórico\\n'
    '    invertía el ORDEN de lectura (espejo horizontal): letras\\n'
    '    de pie pero secuencia al revés — «no se lee desde la\\n'
    '    perspectiva del jugador».\\n'
    '  · Fix: los 5 textos se dibujan con scale(1,-1) + baseline\\n'
    '    middle: parte alta hacia el fondo y lectura izquierda→\\n'
    '    derecha reales para el jugador.\\n'
    '  · i18n: claves z_obj/z_evita/z_fondo/z_doble/z_f15 en es/en\\n'
    '    (OBJETIVO/TARGET · EVITA/AVOID · FONDO/DEEP · DOBLE BOTE/\\n'
    '    DOUBLE BOUNCE · FONDO 15 cm/DEEP 15 cm) vía el t() del módulo.\\n'
    '  · Verificación AIRTIGHT: la capa T (qa_train_zonas_v3619)\\n'
    '    añade el chequeo permanente de textos: réplica del pintado\\n'
    '    nuevo vs antiguo sobre el canvas real y IoU con búsqueda\\n'
    '    ±3 px — legible 0.77-0.998 vs espejo 0.20-0.81 (pre-fix\\n'
    '    salía al revés: el test detectó el bug del dueño). 17/17.\\n'
    '  · Sólo positivo: nada del gameplay cambia — física, duelos,\\n'
    '    campeonatos y progreso del dueño intactos.\\n'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del\\n'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD\\n'
    '    SDF de contacto, el saque VR realista, el hall del\\n'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"""

GLOBALES = [
    ("V3.6.19-SDK6", "V3.6.20-SDK6"),
    ("3.6.19-SDK6", "3.6.20-SDK6"),
    ("v3619-sdk6", "v3620-sdk6"),
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
            # ── bloque de notas por marcadores ──
            i = txt.find(BLOQUE_INI)
            if i < 0:
                print("FALLO: marcador INI del bloque no encontrado")
                sys.exit(1)
            j = txt.find(BLOQUE_FIN, i)
            if j < 0:
                print("FALLO: marcador FIN del bloque no encontrado")
                sys.exit(1)
            j += len(BLOQUE_FIN)
            txt = txt[:i] + BLOQUE_NUEVO + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 22 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.19"' in txt:
                txt = txt.replace('grep -c "3.6.19"', 'grep -c "3.6.20"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.20")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.20-SDK6") == 1:
            txt = txt.replace("frente a V3.6.20-SDK6", "frente a V3.6.19-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.19)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3620 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.19-SDK6", "v3619-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.20-SDK6" not in bz or "FASE 22" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el nombre del script de QA (v3619 sin -sdk6) NO debe ser reescrito
    if "qa_train_zonas_v3619" not in bz:
        print("FALLO: la referencia a qa_train_zonas_v3619 se perdió")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3620 listo → python3 scripts/release-v3620/build_zip.py")


if __name__ == "__main__":
    main()
