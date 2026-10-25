#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 69 · GENERADOR DEL DIRECTORIO DE RELEASE v3661
======================================================================
Crea scripts/release-v3661/ a partir de scripts/release-v3660/ con:
  · reemplazos de versión (3.6.60-SDK6 → 3.6.61-SDK6 · v3660-sdk6 → v3661-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 63 — UNA RAQUETA, CERO
    FANTASMAS), sustituido por MARCADORES, método ronda 26/59/…/68.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3661 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3660"
DEST = RAIZ / "scripts" / "release-v3661"
BS_N = chr(92) + "n"

# ── marcadores del bloque de notas del build_zip r68 (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 62 — LA RAQUETA DEL RIVAL: el\\n'"
BLOQUE_FIN = "    '    los 5 campeonatos).\\n\\n'"

BLOQUE_NUEVO = "    'Rama    : main · SDK6 (FASE 63 — UNA RAQUETA, CERO FANTASMAS: el@NL@'\n    'informe del dueño tras probar V3.6.60 en el Quest, punto por punto)@NL@@NL@'\n    'Novedades de esta versión (frente a V3.6.60-SDK6):@NL@@NL@'\n    '  · UNA SOLA RAQUETA POR LADO (el dueño: «aparecen en el lado del@NL@'\n    '    rival dos raquetas, una que es la que se utiliza para las@NL@'\n    '    partidas y que está visible en todo momento y otra que has@NL@'\n    '    colocado para el profesor»): la pala flotante de la IA — la de@NL@'\n    '    los partidos, parada y eterna — se OCULTA durante la academia y@NL@'\n    '    vuelve al cerrarla. En el lado lejano sólo queda UNA raqueta: la@NL@'\n    '    del profesor.@NL@@NL@'\n    '  · SU GOLPE YA NO ESTÁ DESFASADO (el dueño: «está desfasada y no@NL@'\n    '    golpea la pelota, problemas de colocación»): las devoluciones@NL@'\n    '    aplicaban la velocidad EN EL FRAME en que el barrido arrancaba@NL@'\n    '    — la hoja llegaba 0,13 s tarde SIEMPRE. Ahora el golpe se ARMA@NL@'\n    '    y la bola despega EXACTAMENTE cuando la hoja se cierra sobre@NL@'\n    '    ella, con contacto VIVO que persigue a la bola en vuelo. Si la@NL@'\n    '    bola muere, el golpe se cancela: jamás un lanzamiento fantasma.@NL@@NL@'\n    '  · LA INSTRUCCIÓN EN SU MOMENTO (el dueño: «es preciso que se le@NL@'\n    '    diga que mueva la pala hacia los lados sino no nos enteramos»):@NL@'\n    '    la pizarra del paso TU MANDO, TU RAQUETA muestra ahora@NL@'\n    '    «MUÉVELA HACIA LOS LADOS · vaivén firme» (ES/EN) latiendo@NL@'\n    '    mientras la barra está vacía.@NL@@NL@'\n    '  · ADIÓS AL HALO FANTASMA (el dueño: «tras la academia jugamos con@NL@'\n    '    un halo sobre nuestra propia pala que no debe estar ahí»): la@NL@'\n    '    aura dorada de la academia SE DESMONTA de verdad al cerrar el@NL@'\n    '    tutorial (antes quedaba colgada del mount con el pulso@NL@'\n    '    congelado) y libera sus materiales; autocura de huérfanos@NL@'\n    '    incluida. Cada modo de juego crea y destruye lo suyo.@NL@@NL@'\n    '  · AJUSTES SIN TUTORIAL (el dueño: «el Tutorial de ajustes ya no@NL@'\n    '    tiene sentido, eliminarlo»): la entrada repetida se retira —@NL@'\n    '    la academia del HUB y la oferta de primera vez siguen vivas.@NL@@NL@'\n    '  · TROQUELES VERIFICADOS (el dueño: «los troqueles de adorno de@NL@'\n    '    los campeonatos han desaparecido»): los 5 campeonatos montan@NL@'\n    '    sus piezas (listas y visibles, verificado también en@NL@'\n    '    producción) — capa de regresión nueva para que nada vuelva a@NL@'\n    '    taparlos en silencio.@NL@@NL@'\n    '  · Conserva TODO lo anterior (la raqueta del rival r68 con saques@NL@'\n    '    honestos y rally del paso 5; la academia en tus manos r67: voz@NL@'\n    '    única, mandos anclados a los grips reales al 75%; la academia@NL@'\n    '    sobre la mesa r66; el onboarding hablado r65; la academia a@NL@'\n    '    punto r64; el toque profesional r62; la estela de poderes, el@NL@'\n    '    rival adaptativo y la repetición r61; 5 poderes, voz del@NL@'\n    '    selector, expresiones, bomba y eléctrico, passthrough en@NL@'\n    '    caliente, SALÓN, PRO CIRCUITO, CCD, CRAZY TV y los 5@NL@'\n    '    campeonatos).@NL@@NL@'\n"

GLOBALES = [
    ("V3.6.60-SDK6", "V3.6.61-SDK6"),
    ("3.6.60-SDK6", "3.6.61-SDK6"),
    ("v3660-sdk6", "v3661-sdk6"),
    ("3.6.60", "3.6.61"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.61-SDK6", "frente a V3.6.60-SDK6"),
    ("tras probar V3.6.61", "tras probar V3.6.60"),
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
            print(f"  ✓ {f.name}: notas FASE 63 insertadas")
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
