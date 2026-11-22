#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 46 · GENERADOR DEL DIRECTORIO DE RELEASE v3638
======================================================================
Crea scripts/release-v3638/ a partir de scripts/release-v3637/ con:
  · reemplazos de versión (3.6.37-SDK6 → 3.6.38-SDK6 · v3637-sdk6 → v3638-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 40 — GATILLO INMEDIATO +
    HALO/BOTE EXACTOS + FLECHAS EN EL PLANO + LOD 50 %/MIRADA, sustituido
    por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3638 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3637"
DEST = RAIZ / "scripts" / "release-v3638"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 39"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 40 — PODERES v4: GATILLO INMEDIATO +@NL@'
    'HALO/BOTE EXACTOS + FLECHAS EN EL PLANO DEL ICONO + LOD 50 % CON@NL@'
    'MIRADA AL MANGO — 4 peticiones del dueño tras probar V3.6.37)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.37-SDK6):@NL@'
    '  · GATILLO INMEDIATO («detecto un pequeño lag… debe sentirse que la@NL@'
    '    aplicación es inmediata» — a todas costa): (a) el redibujo del@NL@'
    '    icono SALE del frame del gatillo (marca _megaTexDirty y lo ejecuta@NL@'
    '    updateMega — al lanzar, el icono se oculta y el trabajo se ahorra@NL@'
    '    entero); (b) textura del icono PERSISTENTE (canvas + CanvasTexture@NL@'
    '    UNA vez, recalentada con needsUpdate — adiós al crear/disponer por@NL@'
    '    pulsación, y el doble refresh del mismo frame, fuera); (c)@NL@'
    '    PRECALIENTE: desde la primera carga, TODO el arsenal (cantos@NL@'
    '    mega/efecto/imán, halo, anillo de bote, flechas) se construye POR@NL@'
    '    ADELANTADO y REPARTIDO — una pieza por frame. El gatillo ya no crea@NL@'
    '    nada: solo enciende.@NL@'
    '  · HALO ROJO Y BOTE ROJO EXACTOS («desfasados en relación a la bola»):@NL@'
    '    el halo ES HIJO del ballMesh — viaja con su transform, cero desfase@NL@'
    '    posible incluso entre subpasos de física o con extrapolación de red.@NL@'
    '    El anillo de bote está PRECALENTADO: el primer bote marcado ya no@NL@'
    '    construye nada.@NL@'
    '  · FLECHAS EN EL PLANO DEL ICONO («mismo plano… prácticamente tocándose@NL@'
    '    tangencialmente… mirando hacia la cámara»): anclaje en MUNDO cada@NL@'
    '    frame — centro del icono + componente del right de cámara@NL@'
    '    PERPENDICULAR a la línea ojo→icono × separación tangencial (6 % del@NL@'
    '    icono). Nada rota con la muñeca: siempre a los lados, sin solaparse,@NL@'
    '    coplanares y mirando al ojo.@NL@'
    '  · LOD DE TAMAÑO («los iconos y flechas más pequeños mientras jugamos,@NL@'
    '    recuperan su tamaño si miramos el palo de nuestra pala»): en rally@NL@'
    '    miden el 50 %; MIRANDO EL MANGO (≈12°) o fuera del rally vuelven al@NL@'
    '    100 % — transición exponencial suave (rápida al crecer, reposada al@NL@'
    '    encoger). PRUEBA DE SENSACIÓN: calibrable con el feedback del dueño.@NL@'
    '  · Capa AG nueva (qa_poderes_v3638, en vivo): 66 checks — agujas de@NL@'
    '    los 4 cambios + mecánica real headless (precaliente que drena solo,@NL@'
    '    textura persistente con identidad estable, gatillo que NO dibuja,@NL@'
    '    halo hijo de la bola que viaja con ella, flechas coplanares y@NL@'
    '    tangenciales medidas, LOD 50 % en rally → 100 % en saque y con la@NL@'
    '    mirada forzada) + regresiones de las reglas de la ronda 45.@NL@'
    '  · Conserva TODO: la matriz de 3 poderes (mega · efecto · imán) con@NL@'
    '    ciclo ⟷ sin envolver, SÚPER EFECTO notorio (halo + anillo de bote +@NL@'
    '    rival castigado ×2/×0,85), SÚPER IMÁN con la spec completa del@NL@'
    '    dueño, 6 voces nativas y 3 iconos, el menú de campeonatos v3.6.31,@NL@'
    '    el HALL OF FAME (FASE 29), el SALÓN DEL ARTISTA (FASE 30), la SALA@NL@'
    '    DEL PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN PALA NI BOLA@NL@'
    '    (FASE 32), la coronación épica y la RUTA LEYENDA del Oeste, el tren@NL@'
    '    100 % sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD SDF@NL@'
    '    de contacto, el saque VR realista, PRO CIRCUITO, intro oficial,@NL@'
    '    física viva, palas con carácter, CRAZY TV en directo y los 5@NL@'
    '    campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.37-SDK6", "V3.6.38-SDK6"),
    ("3.6.37-SDK6", "3.6.38-SDK6"),
    ("v3637-sdk6", "v3638-sdk6"),
    ("3.6.37", "3.6.38"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.38-SDK6", "frente a V3.6.37-SDK6"),
    ("tras probar V3.6.38", "tras probar V3.6.37"),
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
            print(f"  ✓ {f.name}: notas FASE 40 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3638 LISTA")


if __name__ == "__main__":
    main()
