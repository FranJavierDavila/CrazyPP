#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 65 · GENERADOR DEL DIRECTORIO DE RELEASE v3657
======================================================================
Crea scripts/release-v3657/ a partir de scripts/release-v3656/ con:
  · reemplazos de versión (3.6.56-SDK6 → 3.6.57-SDK6 · v3656-sdk6 → v3657-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 59 — EL ONBOARDING
    GAMIFICADO: voz nativa es/en con 25 átomos por idioma, el mando GLB
    REAL del dueño con halos por pieza y 4 acciones reales, dos pasos
    NUEVOS de reglas visuales sobre la mesa, el panel PIZARRA del dueño
    con textos tiza en la zona negra, el saque demo dormido (adiós al
    bote continuo) y 11 pasos con confirmación real),
    sustituido por MARCADORES, método ronda 26/59/60/61/62/63/64.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3657 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3656"
DEST = RAIZ / "scripts" / "release-v3657"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r64 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 58 — LA ACADEMIA, A PUNTO: los tres"
              + BS_N + "'")
BLOQUE_FIN = "    '    5 campeonatos)." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 59 — EL ONBOARDING GAMIFICADO: la@NL@'
    'academia se convierte en un tutorial hablado, interactivo y visual,@NL@'
    'con los assets exactos que entregó el dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.56-SDK6):@NL@@NL@'
    '  · ADIÓS AL BOTE CONTINUO (informe del dueño: «es muy molesto que@NL@'
    '    nada más empezar esté como sonando la bola botar continuamente»):@NL@'
    '    el saque DEMO del espectador DUERME dentro de la academia y el@NL@'
    '    árbitro queda siempre en saque del jugador — silencio total hasta@NL@'
    '    que TOCA oír botes (el profesor de la práctica sirve a propósito).@NL@@NL@'
    '  · VOZ NATIVA castellano/inglés: el banco de voz Piper se amplía con@NL@'
    '    25 átomos por idioma; cada paso NARRA al entrar (bienvenida, mando,@NL@'
    '    pala, reglas, saque, intercambio, botones, modos y despedida), el@NL@'
    '    STICK repite la última narración y el saque fallido avisa «otra@NL@'
    '    vez» hablado. Respeta el interruptor del megáfono de AJUSTES.@NL@@NL@'
    '  · EL MANDO GLB REAL DEL DUEÑO: tu Mando.glb (Touch Plus exacto,@NL@'
    '    482 KB) flota giratorio junto a la pizarra con HALOS pulsantes@NL@'
    '    sobre la pieza pedida (anclas calculadas por raycast fino: gatillo,@NL@'
    '    stick, botones X/Y y grip). Y el paso 1 es INTERACTIVO de verdad:@NL@'
    '    aprieta el GATILLO, el GRIP, mueve el STICK y pulsa A en tu mando@NL@'
    '    real — cada acierto suena, ilumina la pieza siguiente y avanza.@NL@@NL@'
    '  · LAS REGLAS, VISUALES SOBRE LA MESA (no sólo texto): 2 pasos nuevos@NL@'
    '    con holo-demo sobre la mesa real — el marcador sube punto a punto@NL@'
    '    a 11 ganando por 2 con pips por lado y la bola fantasma cruzando@NL@'
    '    la red; y la rotación del saque (2 por jugador, a 10-10 cada punto,@NL@'
    '    cartel ¡10-10!) con el doble bote reglamentario propio→rival.@NL@@NL@'
    '  · LA PIZARRA DEL DUEÑO: el panel del tutorial es ahora tu Pizarra@NL@'
    '    (graduación + palita) — todo el texto va estilo tiza SOBRE LA ZONA@NL@'
    '    NEGRA (nada fuera de la zona segura) y en los pasos que pasan en@NL@'
    '    la mesa (reglas y práctica) la pizarra se APARTA: nunca tapa la@NL@'
    '    visión. La práctica r64 intacta: 3 saques válidos + 6 devoluciones.@NL@@NL@'
    '  · ONBOARDING GAMIFICADO DE 11 PASOS: cada paso exige SU acción (el@NL@'
    '    gatillo, las 4 del mando, el vaivén, ENTENDIDO tras la demo, los@NL@'
    '    3 saques, las 6 devoluciones, A/X de verdad, los modos, JUGAR YA).@NL@'
    '    VERIFICACIÓN: capa AZ nueva (113 checks: agujas + 25 átomos ×2@NL@'
    '    idiomas + mecánica real sobre el grafo — GLB con 4 halos, subfases@NL@'
    '    con voz, holo con puerta de tiempo, pose lado, stick-repetir y@NL@'
    '    11 pasos completos) · AY actualizada a 65 · QA r59 ampliada a 149.@NL@@NL@'
    '  · Conserva TODO lo anterior (la academia, a punto r64; la academia@NL@'
    '    cierra bien r63; el toque profesional r62: sonido real por síntesis@NL@'
    '    modal, háptica escalada y cámara lenta; los tres arreglos r60; la@NL@'
    '    estela de poderes, el rival adaptativo y la repetición r61, 5@NL@'
    '    poderes, norma de 20 toques, voz del selector, expresiones, bomba@NL@'
    '    y eléctrico, passthrough en caliente, SALÓN, PRO CIRCUITO, CCD,@NL@'
    '    CRAZY TV y los 5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.56-SDK6", "V3.6.57-SDK6"),
    ("3.6.56-SDK6", "3.6.57-SDK6"),
    ("v3656-sdk6", "v3657-sdk6"),
    ("3.6.56", "3.6.57"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.57-SDK6", "frente a V3.6.56-SDK6"),
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
            print(f"  ✓ {f.name}: notas FASE 59 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
                    print(f"  ✓ {f.name}: restaurado {viejo} → {nuevo} (×{n})")
        f.write_text(txt, encoding="utf-8")

    print(f"OK → {DEST}")


if __name__ == "__main__":
    main()
