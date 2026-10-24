#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 66 · GENERADOR DEL DIRECTORIO DE RELEASE v3658
======================================================================
Crea scripts/release-v3658/ a partir de scripts/release-v3657/ con:
  · reemplazos de versión (3.6.57-SDK6 → 3.6.58-SDK6 · v3657-sdk6 → v3658-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 60 — LA ACADEMIA SOBRE LA
    MESA: adiós DEFINITIVO al bote continuo (bola dormida), voces más
    pausadas, DOS mandos GLB reales centrados (izquierdo Y/X + derecho
    B/A), halos opacos con etiqueta, raqueta fantasma, textos sin solapes
    y las reglas REALES sobre la mesa: demo de saque con los mandos,
    intercambio contra el rival que falla y marcador a 11 por 2 con la
    igualada a 10-10),
    sustituido por MARCADORES, método ronda 26/59/60/61/62/63/64/65.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3658 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3657"
DEST = RAIZ / "scripts" / "release-v3658"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r65 (texto FUENTE real) ──
# El FIN llega hasta el final de las notas heredadas (la r65 dejó cola de
# la r60 tras «los 5 campeonatos)») — r66 deja el VERSION.txt limpio.
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 59 — EL ONBOARDING GAMIFICADO: la"
              + BS_N + "'")
BLOQUE_FIN = ("    '    el saque VR realista, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 60 — LA ACADEMIA SOBRE LA MESA: el@NL@'
    'informe del dueño tras probar V3.6.57 en el Quest, atendido punto por@NL@'
    'punto)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.57-SDK6):@NL@@NL@'
    '  · ADIÓS DEFINITIVO AL BOTE CONTINUO (el dueño: «sigo escuchando un@NL@'
    '    ruido molesto de bote continuo»): la bola de la academia queda@NL@'
    '    DORMIDA en los pasos quietos — sin física, sin micro-rebotes y sin@NL@'
    '    el «pock» de la mesa — y SOLO despierta cuando hay bola en juego@NL@'
    '    (saque, intercambio y demos). Silencio real hasta que TOCA oír botes.@NL@@NL@'
    '  · VOCES MÁS PAUSADAS Y MEJOR ENTONADAS (el dueño: «las voces deberían@NL@'
    '    ser más pausadas… y mejorar la entonación»): los 27 átomos por@NL@'
    '    idioma se regeneran con ritmo más lento (length-scale 1,16),@NL@'
    '    respiros entre frases y nuevo guion; además la narración respira@NL@'
    '    entre átomos y el STICK la repite cuando quieras.@NL@@NL@'
    '  · LOS DOS MANDOS, CENTRADOS Y A COMODIDAD (el dueño: «el mando@NL@'
    '    debería mostrarse delante en el centro… el mando que te he pasado@NL@'
    '    es el izquierdo (Y y X), te paso el derecho (B y A) para que pongas@NL@'
    '    ambos»): DOS Touch Plus reales flotan centrados bajo la pizarra, el@NL@'
    '    derecho ESPEJO geométrico del izquierdo, con HALOS OPACOS (núcleo@NL@'
    '    blanco sólido, más grandes) y ETIQUETA de la pieza pedida.@NL@@NL@'
    '  · EL MANDO ES TU RAQUETA (el dueño: «aparecería una raqueta con@NL@'
    '    material tipo fantasma»): al dominar las 4 acciones reales, la pala@NL@'
    '    REAL del juego aparece en fantasma sobre ambos mandos — y acompaña@NL@'
    '    al mando de la demo en el saque.@NL@@NL@'
    '  · LAS REGLAS, EN LA MESA REAL Y PAUSADAS (el dueño: «la simulación a@NL@'
    '    una distancia sobre la mesa no tiene sentido»): paso 3 — los mandos@NL@'
    '    sirven un saque REGLAMENTARIO con la bola del juego (bote propio →@NL@'
    '    rival → sin devolución: PUNTO) y luego toca a ti: 3 saques válidos;@NL@'
    '    paso 4 — intercambio REAL: sacas, el rival devuelve dos veces y@NL@'
    '    falla en la tercera: PUNTO y «cada dos saques rota el sacador»;@NL@'
    '    paso 5 — el MARCADOR sube sobre la propia mesa con saques reales@NL@'
    '    hasta 11 ganando por 2, y en el 10-10 el saque cambia CADA punto@NL@'
    '    (cartel ¡10-10! y +2 PARA GANAR). Todo repetible y con confirmación.@NL@@NL@'
    '  · TEXTOS SIN SOLAPES (el dueño: «los textos se están solapando»): la@NL@'
    '    pizarra re-espaciada — nada invade la línea «B · saltar» ni sale de@NL@'
    '    la zona negra; el panel se aparta en los pasos de mesa (3-6).@NL@@NL@'
    '  · Conserva TODO lo anterior (el onboarding hablado r65; la academia@NL@'
    '    a punto r64; la academia cierra bien r63; el toque profesional r62;@NL@'
    '    los tres arreglos r60; la estela de poderes, el rival adaptativo y@NL@'
    '    la repetición r61, 5 poderes, norma de 20 toques, voz del selector,@NL@'
    '    expresiones, bomba y eléctrico, passthrough en caliente, SALÓN,@NL@'
    '    PRO CIRCUITO, CCD, CRAZY TV y los 5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.57-SDK6", "V3.6.58-SDK6"),
    ("3.6.57-SDK6", "3.6.58-SDK6"),
    ("v3657-sdk6", "v3658-sdk6"),
    ("3.6.57", "3.6.58"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.58-SDK6", "frente a V3.6.57-SDK6"),
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
            print(f"  ✓ {f.name}: notas FASE 60 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
