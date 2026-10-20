#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 27 · GENERADOR DEL DIRECTORIO DE RELEASE v3621
======================================================================
Crea scripts/release-v3621/ a partir de scripts/release-v3620/ con:
  · reemplazos de versión (3.6.20-SDK6 → 3.6.21-SDK6 · v3620-sdk6 → v3621-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 23 — AYUDAS TÉCNICAS
    OBEDIENTES), sustituido por MARCADORES (método de la ronda 26).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3621 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3620"
DEST = RAIZ / "scripts" / "release-v3621"

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 22"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"

# bloque NUEVO en texto fuente de build_zip.py (los \\n literales son los
# saltos del VERSION.txt generado; los saltos reales separan literales).
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 23 — AYUDAS TÉCNICAS OBEDIENTES)\\n\\n'
    'Novedades de esta versión (frente a V3.6.20-SDK6):\\n'
    '  · FASE 23 (ronda 27, informe del dueño): en el PRO TRAINING,\\n'
    '    al desmarcar las AYUDAS TÉCNICAS (Marcas de bote, Línea de\\n'
    '    tiro, Flecha de efecto) sólo obedecía «Línea de tiro».\\n'
    '  · Causa probada por QA GPU sobre el juego real: los iconos de\\n'
    '    efecto de las DOS CARAS de la pala no consultaban su\\n'
    '    interruptor (pulsaban siempre) y, al desmarcar, lo ya\\n'
    '    dibujado seguía en pantalla hasta ~1,7 s desvaneciéndose —\\n'
    '    «no hace caso». Marcas y línea SÍ obedecían al flag.\\n'
    '  · Fix 1: los iconos de efecto de la pala pasan a obedecer a\\n'
    '    «Flecha de efecto» (igual que el sprite de la bola).\\n'
    '  · Fix 2 · OBEDIENCIA INMEDIATA: al desmarcar cada ayuda, lo\\n'
    '    ya dibujado se retira AL INSTANTE (marcas, línea, sprite e\\n'
    '    iconos) — sin esperas de fundido. Las pistas de goma de la\\n'
    '    piel DOBLE GOMA se conservan (no son feedback de efecto).\\n'
    '  · Verificación AIRTIGHT: nuevo QA permanente\\n'
    '    (qa_train_ayudas_v3621) que conduce el JUEGO REAL por la\\n'
    '    cadena completa (clic → estado → stepPhysics → evento de\\n'
    '    bote → dibujado): 17/17. Regresión de zonas intacta (17/17).\\n'
    '  · Sólo positivo: nada del gameplay cambia — física, duelos,\\n'
    '    campeonatos y progreso del dueño intactos.\\n'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del\\n'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD\\n'
    '    SDF de contacto, el saque VR realista, el hall del\\n'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"""

GLOBALES = [
    ("V3.6.20-SDK6", "V3.6.21-SDK6"),
    ("3.6.20-SDK6", "3.6.21-SDK6"),
    ("v3620-sdk6", "v3621-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 23 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.20"' in txt:
                txt = txt.replace('grep -c "3.6.20"', 'grep -c "3.6.21"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.21")
            # deuda cosmética de la ronda 26: el print de la FASE 8 decía
            # «menciones 3.6.8» (variable n368) con el grep ya actualizado
            if "menciones 3.6.8" in txt:
                txt = txt.replace("menciones 3.6.8", "menciones 3.6.21")
                txt = txt.replace("n368 = int", "n3621 = int").replace("{n368}", "{n3621}").replace("if n368 < 4", "if n3621 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.21 (deuda ronda 26)")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.21-SDK6") == 1:
            txt = txt.replace("frente a V3.6.21-SDK6", "frente a V3.6.20-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.20)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3621 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.20-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n20 = bz.count("3.6.20-SDK6")
    if n20 != 1 or "frente a V3.6.20-SDK6" not in bz:
        print(f"aviso: 3.6.20-SDK6 queda ×{n20} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3620-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.21-SDK6" not in bz or "FASE 23" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # los nombres de QA en las NOTAS nuevas: la capa T vive en qa_todo, no
    # aquí; lo que debe sobrevivir es la cita del QA nuevo del bloque.
    if "qa_train_ayudas_v3621" not in bz:
        print("FALLO: el bloque nuevo no cita qa_train_ayudas_v3621")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3621 listo → python3 scripts/release-v3621/build_zip.py")


if __name__ == "__main__":
    main()
