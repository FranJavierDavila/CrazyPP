#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 26 · GENERADOR DEL DIRECTORIO DE RELEASE v3619
======================================================================
Crea scripts/release-v3619/ a partir de scripts/release-v3618/ con:
  · reemplazos de versión (3.6.18-SDK6 → 3.6.19-SDK6 · v3618-sdk6 → v3619-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 21 — FIX ZONAS DE
    ENTRENAMIENTO), sustituido por MARCADORES (lección de esta ronda:
    las agujas copiadas a mano se descarrilan por quirks de formato del
    bloque original — literales adyacentes en la misma línea).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3619 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3618"
DEST = RAIZ / "scripts" / "release-v3619"

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 20"
BLOQUE_FIN = "el hub «Tu camino te espera».\\n\\n'"

# bloque NUEVO en texto fuente de build_zip.py (los \\n literales son los
# saltos del VERSION.txt generado; los saltos reales separan literales).
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 21 — FIX ZONAS DE ENTRENAMIENTO)\\n\\n'
    'Novedades de esta versión (frente a V3.6.18-SDK6):\\n'
    '  · FASE 21 — FIX ZONAS (ronda 26, informe del dueño): en el\\n'
    '    PRO TRAINING por zonas (MESA MARCADA) la zona OBJETIVO\\n'
    '    pintada NO era la que el juez aceptaba y al rotar objetivos\\n'
    '    las zonas nuevas nunca se veían marcadas.\\n'
    '  · Causa 1 (espejado): el overlay de la mesa usaba la textura\\n'
    '    con flipY por defecto; con la rotación del plano, la fila\\n'
    '    0 del canvas aterrizaba en el FONDO en vez de la red y TODO\\n'
    '    lo pintado se mostraba volteado en profundidad (la zona\\n'
    '    amarilla caía donde el juez dice «corta»). Fix: flipY=false\\n'
    '    sólo en esa textura — t1a, t1b, t4a y t4b quedan EXACTOS.\\n'
    '  · Causa 2 (congelado): al acertar, el objetivo rotaba pero el\\n'
    '    quad no se repintaba — el jugador seguía viendo la zona\\n'
    '    inicial. Fix: la rotación repinta el overlay al momento.\\n'
    '  · Verificación AIRTIGHT: qa_train_zonas_v3619.py (capa T del\\n'
    '    QA TOTAL) renderiza la mesa top-down y lee píxeles de la\\n'
    '    GPU: lo visible == lo juzgado en deep/mid × izq/der, rojo\\n'
    '    EVITA intacto, rotación con repintado en vivo y franjas de\\n'
    '    t1b/t4a/t4b en su sitio (12/12).\\n'
    '  · Sólo positivo: nada del gameplay cambia — física, duelos,\\n'
    '    campeonatos y progreso del dueño intactos.\\n'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del\\n'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD\\n'
    '    SDF de contacto, el saque VR realista, el hall del\\n'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"""

GLOBALES = [
    ("V3.6.18-SDK6", "V3.6.19-SDK6"),
    ("3.6.18-SDK6", "3.6.19-SDK6"),
    ("v3618-sdk6", "v3619-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 21 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO (lección ronda 10/…/21): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.18"' in txt:
                txt = txt.replace('grep -c "3.6.18"', 'grep -c "3.6.19"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.19")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.19-SDK6") == 1:
            txt = txt.replace("frente a V3.6.19-SDK6", "frente a V3.6.18-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.18)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3619 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.18-SDK6", "v3618-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.19-SDK6" not in bz or "FASE 21" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3619 listo → python3 scripts/release-v3619/build_zip.py")


if __name__ == "__main__":
    main()
