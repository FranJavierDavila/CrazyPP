#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 58 · GENERADOR DEL DIRECTORIO DE RELEASE v3650
======================================================================
Crea scripts/release-v3650/ a partir de scripts/release-v3649/ con:
  · reemplazos de versión (3.6.49-SDK6 → 3.6.50-SDK6 · v3649-sdk6 → v3650-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 52 — EL CLON DOBLE Y LA
    VOZ QUE GUÍA: el 5.º poder de pala SÚPER CLONACIÓN (2 palas fantasma
    a ±50 cm que cazan la bola escapada al 90 % y barren globos y
    confeti), la VOZ DEL SELECTOR (mover el joystick y la voz dice el
    poder seleccionado — «Sin poder» con la mano vacía — ES/EN), el
    TROFEO DEL HALL RETIRADO (copa + haz fuera, espacio central libre)
    y el SUELO del Hall con la nueva imagen del dueño),
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v27.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3650 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3649"
DEST = RAIZ / "scripts" / "release-v3650"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 51"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 52 — EL CLON DOBLE Y LA VOZ QUE@NL@'
    'GUÍA — petición del dueño tras V3.6.49)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.49-SDK6):@NL@'
    '  · SÚPER CLONACIÓN (5.º poder de pala; spec literal del dueño):@NL@'
    '    «dura 10 segundos y crea 2 palas virtuales a una distancia de@NL@'
    '    50 centímetros». Material GHOST («medio transparente azulado»,@NL@'
    '    opacidad 0,42 con brillo propio). La pala clon de la DERECHA@NL@'
    '    atiende a bolas por la derecha y la IZQUIERDA por la izquierda,@NL@'
    '    SIEMPRE que el jugador no las devuelva (prioridad absoluta: el@NL@'
    '    clon calla donde la pala llega). Tasa de éxito del 90 % real —@NL@'
    '    UNA sola tirada por vuelo, sin re-tiradas encubiertas. La@NL@'
    '    devolución es un golpe de JUGADOR legal (árbitro, contador y@NL@'
    '    emociones del rival intactos) con el SOLVER DE LA CASA hacia la@NL@'
    '    mesa rival y cero spin (bote seguro). La ventana vive SUS 10 s@NL@'
    '    (reloj único; la caza NO gasta cargas; refresh honesto).@NL@@NL@'
    '  · LOS CLONES LIMPIAN LA VISIÓN: «estas palas Clon tratarán de@NL@'
    '    eliminar cualquier poder de molestia de visión como confeti o@NL@'
    '    el superpoder de Globos del Clown» — los globos del Clown son@NL@'
    '    CAZABLES por hook (clonBlancos, contrato PLANTILLA-GUIA §4.2;@NL@'
    '    locura módulo v27: el kill usa el pop propio del módulo) y el@NL@'
    '    confeti lo BARRE el núcleo (createConfetti.kill: las partículas@NL@'
    '    cazadas no renacen hasta que la ráfaga termina). Con blancos los@NL@'
    '    clones VUELAN a ellos; sin blancos patrullan la banda del@NL@'
    '    confeti; y si el aire está limpio vuelven a la guardia de ±50 cm.@NL@@NL@'
    '  · VOZ DEL SELECTOR (petición del dueño): «cuando tenemos cargado@NL@'
    '    algún poder y movemos el joystick para seleccionarlo que la voz@NL@'
    '    diga el que nos aparece seleccionado… si no tenemos nada voz@NL@'
    '    dirá Sin poder… dice de forma rápida solo el nombre». Voces@NL@'
    '    NATIVAS Piper embebidas (davefx/lessac), NOMBRES CORTOS:@NL@'
    '    Super Pala · Super Efecto · Imán · Portal · Clonación · Sin@NL@'
    '    poder — y en inglés Super Paddle · Super Effect · Magnet ·@NL@'
    '    Portal · Cloning · No power. Funciona con la mano vacía, con un@NL@'
    '    solo poder (nombra sin ciclar) y al ciclar la matriz ⟷.@NL@@NL@'
    '  · HALL: TROFEO RETIRADO (petición del dueño: «eliminar del@NL@'
    '    escenario Hall la copa central y el haz de luz que cae sobre@NL@'
    '    ella para dejar ese espacio libre») — fuera la copa torneada,@NL@'
    '    sus asas y bola, la peana, el haz volumétrico, el anillo del@NL@'
    '    techo, la placa plateado/oro y su foco: el CENTRO queda LIBRE@NL@'
    '    sobre el emblema del suelo. Sigue vivo el vaivén de las 7 bolas@NL@'
    '    doradas. Y SUELO NUEVO del Hall con la imagen del dueño@NL@'
    '    (suelo.jpg versión r58, byte-exacto).@NL@@NL@'
    '  · CONCESIÓN del clon por la MISMA puerta de siempre (cada 20@NL@'
    '    toques = +1 carga, tope ×3), icono del DUEÑO (etiqueta@NL@'
    '    SuperPala_Clon) con anillo de tiempo azul fantasma, voz nativa@NL@'
    '    «¡Súper clonación de pala!» / «Super clone booster!», sonido y@NL@'
    '    háptica propios. VERIFICACIÓN: capa AS nueva (qa_clon_voz_v3650,@NL@'
    '    69 checks: agujas + mecánica real headless — ventana de 10 s,@NL@'
    '    guardia ±50 cm, devolución legal del 90 %, el 10 % que falla,@NL@'
    '    prioridad del jugador, voz del selector con 0 y 1 poderes) ·@NL@'
    '    capa W re-anclada al hall sin trofeo (43 checks) · AF/AQ/AR@NL@'
    '    re-ancladas (5 poderes + suelo nuevo) · golden de física@NL@'
    '    INTACTO (el clon vive fuera del paso físico).@NL@@NL@'
    '  · Conserva TODO: la norma de 20 toques, las ventanas de 10 s del@NL@'
    '    efecto y del imán, la guía de tiro con el solver de la casa, el@NL@'
    '    spin real por barrido con su firma SÓLO en la mesa del rival, la@NL@'
    '    PALA METÁLICA −80 %, el portal EXPLÍCITO, la norma de emociones@NL@'
    '    del rival en los 6 campeonatos, la bomba por intervalos y el@NL@'
    '    ladrillo eléctrico con su cadena, la matriz con ciclo ⟷, el@NL@'
    '    passthrough EN CALIENTE, el SALÓN DEL ARTISTA, la SALA DEL@NL@'
    '    PARTIDO, PRO CIRCUITO, el ESCUDO DE PALA, el REACTOR DE IMPULSO,@NL@'
    '    la CCD SDF, el saque VR realista, CRAZY TV en directo y los 5@NL@'
    '    campeonatos.@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.49-SDK6", "V3.6.50-SDK6"),
    ("3.6.49-SDK6", "3.6.50-SDK6"),
    ("v3649-sdk6", "v3650-sdk6"),
    ("3.6.49", "3.6.50"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.50-SDK6", "frente a V3.6.49-SDK6"),
    ("tras probar V3.6.50", "tras probar V3.6.49"),
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
            txt = txt[:i] + BLOQUE_NUEVO.replace("@NL@", BS_N) + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 52 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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

    # guard anti-rollback de la estirpe v369-sdk5 (FASE 7)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    if "v369-sdk5" not in bz:
        print("FALLO: la estirpe v369-sdk5 desapareció del build_zip")
        sys.exit(1)
    print("· guard v369-sdk5 intacto")

    # el VERSION.txt del paquete lleva guard del SDK y de manifests: sin cambios
    if "1.5.4" not in bz or "v56" not in bz or "v27" not in bz:
        print("FALLO: guards SDK/oeste/locura alterados")
        sys.exit(1)
    print("· guards SDK 1.5.4 / oeste v56 / locura v27 intactos")
    print("RELEASE v3650 LISTA")


if __name__ == "__main__":
    main()
