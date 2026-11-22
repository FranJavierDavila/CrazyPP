#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 64 · GENERADOR DEL DIRECTORIO DE RELEASE v3656
======================================================================
Crea scripts/release-v3656/ a partir de scripts/release-v3655/ con:
  · reemplazos de versión (3.6.55-SDK6 → 3.6.56-SDK6 · v3655-sdk6 → v3656-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 58 — LA ACADEMIA, A PUNTO:
    los tres arreglos del tutorial pedidos por el dueño — textos que se
    salían de sus contenedores, el mando 3D procedural prometido y la
    práctica real de 3 saques + 6 devoluciones con el panel apartado),
    sustituido por MARCADORES, método ronda 26/59/60/61/62/63.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3656 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3655"
DEST = RAIZ / "scripts" / "release-v3656"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r63 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 57 — LA ACADEMIA CIERRA BIEN: el panel"
              + BS_N + "'")
BLOQUE_FIN = "    '    SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos)." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 58 — LA ACADEMIA, A PUNTO: los tres@NL@'
    'arreglos del tutorial pedidos por el dueño tras probar V3.6.55)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.55-SDK6):@NL@@NL@'
    '  · TEXTOS BIEN MAQUETADOS: los textos del tutorial que se salían de@NL@'
    '    sus contenedores y se cortaban (las líneas del paso TU MANDO@NL@'
    '    acababan fuera del canvas y la ficha de PODERES sobresalía por@NL@'
    '    ambos lados) ya encajan SIEMPRE: cada línea reduce su fuente hasta@NL@'
    '    caber (fitFont), las píldoras se auto-dimensionan al texto y los@NL@'
    '    textos largos se parten en 2 líneas. Además el panel sube a@NL@'
    '    1280×800 píxeles: el texto se ve NÍTIDO dentro del casco.@NL@@NL@'
    '  · EL MANDO EN 3D DE VERDAD: fuera el dibujo plano — ahora flota@NL@'
    '    junto al panel un mando Touch Plus modelado en 3D procedural@NL@'
    '    (cuerpo, anillo, stick, gatillo, grip y botones A/X/B/Y), girando@NL@'
    '    sobre sí mismo con un vaivén suave, y cada pieza se ILUMINA en oro@NL@'
    '    cuando el paso la menciona (paso 0 el cuerpo · paso 1 cicla@NL@'
    '    gatillo→grip→stick→botones · paso 3 el gatillo · paso 5 botones).@NL@@NL@'
    '  · PRÁCTICA DE VERDAD: para terminar la academia hay que demostrar@NL@'
    '    que se sabe jugar: 3 SAQUES VÁLIDOS (contador grande en el panel,@NL@'
    '    cerrojo que no re-cuenta un saque en vuelo, aviso verde «saque@NL@'
    '    válido» y «otra vez» si el lanzamiento se pierde) y 6 DEVOLUCIONES@NL@'
    '    del profesor (con rally real: cada golpe habilita una devolución@NL@'
    '    del profesor — la meta 6 destapó y arregló un cerrojo latente).@NL@@NL@'
    '  · EL PANEL NO ESTORBA: durante la práctica (pasos 3 y 4) el panel se@NL@'
    '    APARTA al lado contrario de la pala, más abajo, más cerca y más@NL@'
    '    pequeño, girado hacia el jugador: la mesa queda COMPLETA a la@NL@'
    '    vista. Transición suave por interpolación y vuelta a su sitio al@NL@'
    '    acabar (jugador zurdo incluido: se aparta al otro lado).@NL@@NL@'
    '  · VERIFICACIÓN: capa AY nueva (qa_r64_v3656, 64 checks: agujas de@NL@'
    '    fuente + mecánica real SOBRE EL GRAFO con rig de three — mando con@NL@'
    '    sus 6 partes, giro, resalte, pose frente⇄lado con desplazamiento@NL@'
    '    medible, cerrojo del saque, saque fallido, rally del profesor y@NL@'
    '    salida sin residuos) + QA r59 ampliada a 142 checks. Regresión@NL@'
    '    r63 intacta (16) y presupuesto refrescado (7.373.974 B).@NL@@NL@'
    '  · Conserva TODO lo anterior (la academia cierra bien r63, el toque@NL@'
    '    profesional r62: sonido real por síntesis modal, háptica escalada y@NL@'
    '    cámara lenta; LA ACADEMIA, los tres arreglos r60, la estela de@NL@'
    '    poderes, el rival adaptativo y la repetición r61, 5 poderes, norma@NL@'
    '    de 20 toques, voz del selector, expresiones, bomba y eléctrico,@NL@'
    '    passthrough en caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los@NL@'
    '    5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.55-SDK6", "V3.6.56-SDK6"),
    ("3.6.55-SDK6", "3.6.56-SDK6"),
    ("v3655-sdk6", "v3656-sdk6"),
    ("3.6.55", "3.6.56"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.56-SDK6", "frente a V3.6.55-SDK6"),
    ("tras probar V3.6.56", "tras probar V3.6.55"),
    ("tras V3.6.56", "tras V3.6.55"),
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
            print(f"  ✓ {f.name}: notas FASE 58 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    if "v369-sdk5" not in bz or "V3.6.56-SDK6" not in bz:
        print("FALLO: guard de identidad roto en build_zip.py")
        sys.exit(1)
    print("· guard v369-sdk5 intacto · V3.6.56-SDK6 presente")
    print("GEN_RELEASE_V3656 COMPLETO")


if __name__ == "__main__":
    main()
