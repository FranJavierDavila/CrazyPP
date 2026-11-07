#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 59 · GENERADOR DEL DIRECTORIO DE RELEASE v3651
======================================================================
Crea scripts/release-v3651/ a partir de scripts/release-v3650/ con:
  · reemplazos de versión (3.6.50-SDK6 → 3.6.51-SDK6 · v3650-sdk6 → v3651-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 53 — LA ACADEMIA: el
    TUTORIAL INTERACTIVO que enseña a jugar — petición del dueño: «la
    gente entra, hay tanto menú y opciones que no saben ni cómo hacer
    para sacar»). 9 pasos guiados con práctica REAL sobre la mesa de
    verdad (árbitro dormido): bienvenida, TU MANDO con diagrama del
    control Quest 3 y gatillo, LA PALA con vaivén, EL SAQUE con la bola
    descansando en la mano libre y cruce de red, EL INTERCAMBIO con un
    «profesor» que devuelve suave con el solver de la casa (2
    devoluciones), LOS BOTONES con A/X cambiando la pala de mano de
    verdad, LOS MODOS (los 6 + los 5 poderes) y ¡YA SABES JUGAR! con
    GATILLO = jugar ya. Tres puertas: banner dorado en el HUB, oferta
    «¿PRIMERA VEZ?» la primera vez que se entra en VR (una sola vez) y
    botón en AJUSTES. B/Y salta siempre; se recuerda quién lo completó.
    ES/EN completos (60 claves × 2).
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v27.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3651 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3650"
DEST = RAIZ / "scripts" / "release-v3651"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 52"
BLOQUE_FIN = "    '    campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 53 — LA ACADEMIA: EL TUTORIAL QUE@NL@'
    'ENSEÑA A JUGAR — petición del dueño tras V3.6.50)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.50-SDK6):@NL@'
    '  · LA ACADEMIA (petición literal del dueño: «la gente entra, hay@NL@'
    '    tanto menú y opciones que no saben ni cómo hacer para sacar»):@NL@'
    '    TUTORIAL INTERACTIVO de 9 pasos con práctica REAL sobre la mesa@NL@'
    '    de verdad (física viva, árbitro dormido, IA dormida): 0 bienvenida@NL@'
    '    · 1 TU MANDO (diagrama del control Quest 3 con GATILLO/GRIP/A-X/@NL@'
    '    B-Y/STICK etiquetados + práctica de gatillo) · 2 LA PALA (vaivén@NL@'
    '    firme con barra de progreso) · 3 EL SAQUE (la bola descansa en la@NL@'
    '    mano libre como en partido: GATILLO la lanza y hay que cruzar la@NL@'
    '    red; bola muerta vuelve a la mano y se avisa) · 4 EL INTERCAMBIO@NL@'
    '    (un «profesor» devuelve suave con el SOLVER DE LA CASA tras el@NL@'
    '    bote lejano; 2 devoluciones y pasas; bola muerta se realimenta) ·@NL@'
    '    5 LOS BOTONES (A/X cambia la pala de mano DE VERDAD) · 6/7 LOS@NL@'
    '    MODOS (Partido, Supervivencia, Multijugador, Campeonatos, Ranking@NL@'
    '    y Entrenar + los 5 poderes y la norma de los 20 toques) · 8 ¡YA@NL@'
    '    SABES JUGAR! (GATILLO = jugar ya contra la CPU).@NL@@NL@'
    '  · TRES PUERTAS DE ENTRADA: banner dorado ENCIMA de la parrilla del@NL@'
    '    HUB (siempre visible), OFERTA «¿PRIMERA VEZ?» la primera vez que@NL@'
    '    se entra en VR (el menú nace en ella, una sola vez, marcas@NL@'
    '    pp_tut_asked/pp_tut_done) y botón en AJUSTES para repetir.@NL@'
    '    B o Y saltan siempre (vuelta al HALL con el menú); al completar@NL@'
    '    hay confeti, voz de bienvenida y sello permanente. ES/EN completos.@NL@@NL@'
    '  · NÚCLEO CON GUARDIAS (tutV1): gatillo, A/X, bola-en-mano (saque@NL@'
    '    natural por grip incluido), tick, página del menú y limpieza en@NL@'
    '    sessionstart — la academia jamás sobrevive a una sesión VR y no@NL@'
    '    toca árbitro, IA, marcador, campeonatos ni multijugador (se niega@NL@'
    '    con aviso si hay partida online o prueba activa).@NL@@NL@'
    '  · VERIFICACIÓN: capa r59 nueva (qa_tut_v3651, 128 checks: agujas de@NL@'
    '    los 12 ganchos del núcleo, 60 claves ES/EN balanceadas, negativas@NL@'
    '    y MECÁNICA REAL headless del módulo — arranque estanco, vaivén,@NL@'
    '    saque con rearme, profesor con solver, 2 devoluciones, A/X real,@NL@'
    '    JUGAR YA con sello done, salida por B sin sello, tutela online).@NL@@NL@'
    '  · Conserva TODO: los 5 poderes con sus ventanas, la norma de 20@NL@'
    '    toques, la voz del selector, las expresiones de los 6 rivales, la@NL@'
    '    bomba por intervalos y el ladrillo eléctrico con su cadena, el@NL@'
    '    passthrough EN CALIENTE, el SALÓN DEL ARTISTA, la SALA DEL@NL@'
    '    PARTIDO, PRO CIRCUITO, el ESCUDO DE PALA, el REACTOR DE IMPULSO,@NL@'
    '    la CCD SDF, el saque VR realista, CRAZY TV en directo y los 5@NL@'
    '    campeonatos.@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.50-SDK6", "V3.6.51-SDK6"),
    ("3.6.50-SDK6", "3.6.51-SDK6"),
    ("v3650-sdk6", "v3651-sdk6"),
    ("3.6.50", "3.6.51"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.51-SDK6", "frente a V3.6.50-SDK6"),
    ("tras probar V3.6.51", "tras probar V3.6.50"),
    ("tras V3.6.51", "tras V3.6.50"),
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
            print(f"  ✓ {f.name}: notas FASE 53 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3651 LISTA")


if __name__ == "__main__":
    main()
