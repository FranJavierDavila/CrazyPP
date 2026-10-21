#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 47 · GENERADOR DEL DIRECTORIO DE RELEASE v3639
======================================================================
Crea scripts/release-v3639/ a partir de scripts/release-v3638/ con:
  · reemplazos de versión (3.6.38-SDK6 → 3.6.39-SDK6 · v3638-sdk6 → v3639-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 41 — PARTIDA NUEVA = PALA
    LIMPIA: hook rules.onMatchStart, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3639 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3638"
DEST = RAIZ / "scripts" / "release-v3639"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 40"
BLOQUE_FIN = ("    '    campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 41 — PODERES v5: PARTIDA NUEVA = PALA@NL@'
    'LIMPIA — el reporte del dueño tras probar V3.6.38)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.38-SDK6):@NL@'
    '  · PARTIDA NUEVA = PALA LIMPIA («los poderes de la pala al iniciar@NL@'
    '    una partida deben desaparecer — permanecen los de una partida@NL@'
    '    previa que no se han gastado»): la recogida completa@NL@'
    '    (_megaNormReset) SOLO corría al ENTRAR EN EL HALL y al APAGAR@NL@'
    '    «Pala Mejorada». TODOS los demás caminos de nueva partida@NL@'
    '    (revancha por gatillo al terminar, revancha de menú, cambio de@NL@'
    '    modo, online, vuelta de calibración y el REINICIO AUTOMÁTICO del@NL@'
    '    árbitro en el estado over) arrancaban con las cargas, el icono ×N@NL@'
    '    y los FX de la partida anterior todavía colgados de la pala.@NL@'
    '  · SOLUCIÓN con UN solo punto: HOOK rules.onMatchStart — el árbitro@NL@'
    '    (c06) avisa al FINAL de CADA startMatch (con blindaje try/catch:@NL@'
    '    el árbitro NUNCA rompe) y el núcleo (c12) lo registra UNA vez,@NL@'
    '    en su constructor, apuntando a _megaNormReset. Cualquier camino@NL@'
    '    presente o FUTURO hereda la recogida gratis: imposible olvidar@NL@'
    '    uno. Idempotente (el hall recogía antes de startMatch; repetir@NL@'
    '    no rompe nada) y sin dispose doble.@NL@'
    '  · REGLA aprobada: empezar una partida SIEMPRE con la pala exacta@NL@'
    '    de siempre — cero cargas, cero icono, cero FX. Las cargas se@NL@'
    '    ganan JUGANDO (norma de los 11 golpes del rally, tope ×3) y se@NL@'
    '    gastan en ESA partida. El marcador y el bestOf no se tocan.@NL@'
    '  · Capa AH nueva (qa_poderes_reset_v3639, en vivo): agujas del hook@NL@'
    '    en árbitro y núcleo + mecánica real headless — cargas sembradas@NL@'
    '    → startMatch: matriz VACÍA, icono OCULTO, temporizadores de los@NL@'
    '    tres poderes a CERO, FX null, bola SIN marcas, escalas LOD y@NL@'
    '    multiplicador del rival a 1; el REINICIO AUTOMÁTICO del estado@NL@'
    '    over también recoge; DOBLE recogida sin errores; y tras el@NL@'
    '    corte el juego vuelve a conceder y precalentar (sigue vivo).@NL@'
    '  · Conserva TODO: la INMEDIATEZ del gatillo (redibujo diferido +@NL@'
    '    textura persistente + precaliente repartido), el halo rojo HIJO@NL@'
    '    de la bola, las flechas EN EL PLANO del icono, el LOD 50 % con@NL@'
    '    mirada al mango, la matriz de 3 poderes (mega · efecto · imán)@NL@'
    '    con ciclo ⟷ sin envolver, SÚPER EFECTO notorio (rival castigado@NL@'
    '    ×2/×0,85), SÚPER IMÁN con la spec completa del dueño, 6 voces@NL@'
    '    nativas y 3 iconos, el menú de campeonatos v3.6.31, el HALL OF@NL@'
    '    FAME (FASE 29), el SALÓN DEL ARTISTA (FASE 30), la SALA DEL@NL@'
    '    PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN PALA NI BOLA@NL@'
    '    (FASE 32), la coronación épica y la RUTA LEYENDA del Oeste, el@NL@'
    '    tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la@NL@'
    '    CCD SDF de contacto, el saque VR realista, PRO CIRCUITO, intro@NL@'
    '    oficial, física viva, palas con carácter, CRAZY TV en directo y@NL@'
    '    los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.38-SDK6", "V3.6.39-SDK6"),
    ("3.6.38-SDK6", "3.6.39-SDK6"),
    ("v3638-sdk6", "v3639-sdk6"),
    ("3.6.38", "3.6.39"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.39-SDK6", "frente a V3.6.38-SDK6"),
    ("tras probar V3.6.39", "tras probar V3.6.38"),
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
            print(f"  ✓ {f.name}: notas FASE 41 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    if "1.5.4" not in bz or "v56" not in bz or "v26" not in bz:
        print("FALLO: guards SDK/oeste/locura alterados")
        sys.exit(1)
    print("· guards SDK 1.5.4 / oeste v56 / locura v26 intactos")
    print("RELEASE v3639 LISTA")


if __name__ == "__main__":
    main()
