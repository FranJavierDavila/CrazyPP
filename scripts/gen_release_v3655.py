#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 63 · GENERADOR DEL DIRECTORIO DE RELEASE v3655
======================================================================
Crea scripts/release-v3655/ a partir de scripts/release-v3654/ con:
  · reemplazos de versión (3.6.54-SDK6 → 3.6.55-SDK6 · v3654-sdk6 → v3655-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 57 — LA ACADEMIA CIERRA
    BIEN: el arreglo del panel huérfano del tutorial que se quedaba fijo),
    sustituido por MARCADORES, método ronda 26/59/60/61/62.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (los r60 vienen heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3655 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3654"
DEST = RAIZ / "scripts" / "release-v3655"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r62 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 56 — SONIDO REAL, HÁPTICA QUE MIDE y"
              + BS_N + "'")
BLOQUE_FIN = "    '    CRAZY TV y los 5 campeonatos)." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 57 — LA ACADEMIA CIERRA BIEN: el panel@NL@'
    'del tutorial ya NO se queda fijo en pantalla — informe del dueño@NL@'
    'tras probar V3.6.54 en el Quest)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.54-SDK6):@NL@@NL@'
    '  · EL ARREGLO: la última pantalla del tutorial («¡Ya sabes@NL@'
    '    jugar!») se quedaba CLAVADA delante del jugador y no había forma@NL@'
    '    de quitarla: al salir (gatillo del paso 8 o B), el cierre anulaba@NL@'
    '    el juego ANTES de desmontar el panel — y el desmontado necesita@NL@'
    '    el juego vivo para quitar el panel de la escena. El if@NL@'
    '    cortocircuitaba, el panel quedaba HUÉRFANO y VISIBLE a la altura@NL@'
    '    de los ojos para siempre (el módulo ya no lo controlaba) y@NL@'
    '    bloqueaba el juego. Ahora el panel se DESMONTA PRIMERO (con el@NL@'
    '    juego vivo) y el desmontado lleva además un RESPALDO por padre@NL@'
    '    que lo quita de cualquier sitio. La academia cierra bien por@NL@'
    '    TODAS sus salidas: gatillo del paso 8 (jugar ya, con sello),@NL@'
    '    B/Y en cualquier paso (saltar, sin sello) y fin de sesión.@NL@@NL@'
    '  · VERIFICACIÓN: capa AX nueva (qa_r63_v3655, 16 checks sobre el@NL@'
    '    GRAFO DE ESCENA — lo que el jugador ve de verdad: el panel nace@NL@'
    '    en el rig, DESAPARECE con el gatillo del paso 8 y con B/Y, no se@NL@'
    '    duplica en doble arranque, cero residuos, sello sólo al jugar,@NL@'
    '    calib limpio y partido jugable tras la salida). La QA r59 miraba@NL@'
    '    el estado del módulo, no la escena: por eso el bug la pasó.@NL@@NL@'
    '  · Conserva TODO lo anterior (el toque profesional r62: sonido real@NL@'
    '    por síntesis modal, háptica escalada y cámara lenta; LA ACADEMIA,@NL@'
    '    los tres arreglos r60, la estela de poderes, el rival adaptativo@NL@'
    '    y la repetición r61, 5 poderes, norma de 20 toques, voz del@NL@'
    '    selector, expresiones, bomba y eléctrico, passthrough en caliente,@NL@'
    '    SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.54-SDK6", "V3.6.55-SDK6"),
    ("3.6.54-SDK6", "3.6.55-SDK6"),
    ("v3654-sdk6", "v3655-sdk6"),
    ("3.6.54", "3.6.55"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.55-SDK6", "frente a V3.6.54-SDK6"),
    ("tras probar V3.6.55", "tras probar V3.6.54"),
    ("tras V3.6.55", "tras V3.6.54"),
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
            print(f"  ✓ {f.name}: notas FASE 57 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    if "v369-sdk5" not in bz or "V3.6.55-SDK6" not in bz:
        print("FALLO: guard de identidad roto en build_zip.py")
        sys.exit(1)
    print("· guard v369-sdk5 intacto · V3.6.55-SDK6 presente")
    print("GEN_RELEASE_V3655 COMPLETO")


if __name__ == "__main__":
    main()
