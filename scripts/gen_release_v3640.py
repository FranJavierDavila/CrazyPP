#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 48 · GENERADOR DEL DIRECTORIO DE RELEASE v3640
======================================================================
Crea scripts/release-v3640/ a partir de scripts/release-v3639/ con:
  · reemplazos de versión (3.6.39-SDK6 → 3.6.40-SDK6 · v3639-sdk6 → v3640-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 42 — EL PODER ACTIVO SE
    VE EN LA PALA: modo activo del icono con anillo de tiempo, sustituido
    por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3640 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3639"
DEST = RAIZ / "scripts" / "release-v3640"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 41"
BLOQUE_FIN = ("    '    los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 42 — PODERES v6: EL PODER ACTIVO SE@NL@'
    'VE EN LA PALA — la pregunta del dueño: «¿se te ocurre alguna manera@NL@'
    'de que el usuario sepa el tipo de poder de pala que tiene activo,@NL@'
    'sin que moleste durante el juego?»)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.39-SDK6):@NL@'
    '  · EL ICONO DEL MANGO NO DESAPARECE AL ACTIVAR: pasa a MODO ACTIVO.@NL@'
    '    Muestra el poder EN MARCHA con un ANILLO DE TIEMPO que se vacía:@NL@'
    '    pista tenue completa + arco en el color del canto de cada poder@NL@'
    '    (oro mega / cian efecto / azul imán) con cabeza blanca que marca@NL@'
    '    el sentido del vaciado. Al terminar, el icono vuelve al modo@NL@'
    '    inventario (seleccionado ×N) o se esconde si no quedan cargas.@NL@'
    '  · PARPADEO en los últimos 2 s (el mismo lenguaje del canto que se@NL@'
    '    apaga): «se está acabando» sin texto, sin voz, sin HUD — todo@NL@'
    '    vive en la pala, en visión periférica. Cero elementos nuevos:@NL@'
    '    UN solo icono en la pala en todo momento (FASE 38 intacta).@NL@'
    '  · ÚLTIMO GATILLO MANDA: si dos poderes corren a la vez, el icono@NL@'
    '    muestra el lanzado más reciente; el ALARGA de la mega llena el@NL@'
    '    anillo con TODO el tiempo restante; el imán refresca sin gastar.@NL@'
    '  · Las flechas ‹ › de la matriz DESCANSAN mientras un poder corre@NL@'
    '    (elijen el SIGUIENTE, no van a molestar).@NL@'
    '  · INGENIERÍA: anillo en el canvas PERSISTENTE del icono (cero@NL@'
    '    texturas nuevas, needsUpdate in-place), redibujo DIFERIDO (nunca@NL@'
    '    en el frame del gatillo, lección ronda 46) y AHORRADO por muescas@NL@'
    '    de 1/24 de vuelta (≈ cada 0,3 s en una ventana de 8 s). El modo@NL@'
    '    activo hereda el LOD del icono (50 % en rally, 100 % mirando el@NL@'
    '    mango) y el indicador duerme en CADA _megaNormReset (FASE 41:@NL@'
    '    partida nueva = pala limpia, intacta).@NL@'
    '  · Capa AI nueva (qa_poderes_activo_v3640, en vivo): agujas del modo@NL@'
    '    activo + mecánica real headless — MEGA abre → icono en modo@NL@'
    '    ACTIVO con textura persistente y anillo al día; el anillo@NL@'
    '    PROGRESA con el tiempo; ALARGA mantiene el modo y llena el@NL@'
    '    anillo; PARPADEO sin romper nada; expiración → vuelve al@NL@'
    '    INVENTARIO; EFECTO con FLECHAS que descansan y vuelven; IMÁN@NL@'
    '    refresca SIN gasto; LOD en AMBOS modos; y la PARTIDA NUEVA@NL@'
    '    recoge también el indicador (FASE 41+42).@NL@'
    '  · Conserva TODO: la PARTIDA NUEVA = PALA LIMPIA (hook del árbitro),@NL@'
    '    la INMEDIATEZ del gatillo, el halo rojo HIJO de la bola, las@NL@'
    '    flechas EN EL PLANO del icono, la matriz de 3 poderes (mega ·@NL@'
    '    efecto · imán) con ciclo ⟷ sin envolver, SÚPER EFECTO notorio@NL@'
    '    (rival castigado ×2/×0,85), SÚPER IMÁN con la spec completa del@NL@'
    '    dueño, 6 voces nativas y 3 iconos, el menú de campeonatos@NL@'
    '    v3.6.31, el HALL OF FAME (FASE 29), el SALÓN DEL ARTISTA (FASE@NL@'
    '    30), la SALA DEL PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN@NL@'
    '    PALA NI BOLA (FASE 32), la coronación épica y la RUTA LEYENDA@NL@'
    '    del Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR@NL@'
    '    DE IMPULSO, la CCD SDF de contacto, el saque VR realista, PRO@NL@'
    '    CIRCUITO, intro oficial, física viva, palas con carácter, CRAZY@NL@'
    '    TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.39-SDK6", "V3.6.40-SDK6"),
    ("3.6.39-SDK6", "3.6.40-SDK6"),
    ("v3639-sdk6", "v3640-sdk6"),
    ("3.6.39", "3.6.40"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.40-SDK6", "frente a V3.6.39-SDK6"),
    ("tras probar V3.6.40", "tras probar V3.6.39"),
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
            print(f"  ✓ {f.name}: notas FASE 42 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3640 LISTA")


if __name__ == "__main__":
    main()
