#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 49 · GENERADOR DEL DIRECTORIO DE RELEASE v3641
======================================================================
Crea scripts/release-v3641/ a partir de scripts/release-v3640/ con:
  · reemplazos de versión (3.6.40-SDK6 → 3.6.41-SDK6 · v3640-sdk6 → v3641-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 43 — SÚPER PORTAL, el
    4.º poder de pala, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3641 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3640"
DEST = RAIZ / "scripts" / "release-v3641"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 42"
BLOQUE_FIN = ("    '    TV en directo y los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 43 — PODERES v7: SÚPER PORTAL, EL@NL@'
    '4.º PODER DE PALA — petición del dueño: «vamos a crear un nuevo@NL@'
    'superpoder de pala Super Portal… el rival es el ordenador deberá@NL@'
    'penalizarlo de alguna forma para que le resulte más complicado@NL@'
    'acertar el golpe», con spec completa de 9 parámetros)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.40-SDK6):@NL@'
    '  · SÚPER PORTAL: la bola atraviesa un PORTAL ENERGÉTICO tras un@NL@'
    '    golpe VÁLIDO — desaparece en un vórtice violeta y reaparece más@NL@'
    '    adelante con una salida legítima. Sorprendente pero CON control:@NL@'
    '    jamás una teletransportación arbitraria que ignore la física.@NL@'
    '  · LA SPEC DEL DUEÑO, PARÁMETRO A PARÁMETRO: ventana de 8 s / 3@NL@'
    '    golpes portalizados · desviación lateral 0,25–0,70 m (NUNCA@NL@'
    '    siempre la máxima) · variación vertical 0–0,15 m · conserva el@NL@'
    '    90–100 % de la rapidez del golpe real · antirrebote 0,25 s ·@NL@'
    '    recarga por la norma de siempre (11 golpes, tope ×3).@NL@'
    '  · LAS 7 REGLAS FÍSICAS, UNA A UNA: (1) solo tras impacto válido@NL@'
    '    — doble guard: evento paddle del jugador SIN consumir en ESTE@NL@'
    '    frame, nunca por rozar ni por colisión duplicada, y el evento NO@NL@'
    '    se consume (el árbitro registra el golpe y el bote); (2) UNA sola@NL@'
    '    bola, UNA sola identidad — swap ATÓMICO posición+velocidad, la@NL@'
    '    bola NUNCA cruza la red físicamente (reaparece ya al otro lado,@NL@'
    '    margen 0,12 m), cero colisiones fantasma; (3) intención del@NL@'
    '    golpe — la salida parte de la PROYECCIÓN NATURAL con la gravedad@NL@'
    '    del juego; (4) desviación VIVA con signo hacia el centro de la@NL@'
    '    mesa y REDUCCIÓN/cancelación si la salida es ilegal; (5) bote@NL@'
    '    jugable garantizado por el solver EXISTENTE (computeShot-@NL@'
    '    Velocity, el del enderezado 5.5); (6) spin CONSERVADO; (7) gasto@NL@'
    '    honesto: 1 carga por golpe portalizado, refresco sin gastar.@NL@'
    '  · EL RIVAL IA PENALIZADO (petición expresa): su predicción MUERE@NL@'
    '    al cruzar el portal (la bola que perseguía desapareció — reacciona@NL@'
    '    tras SU intervalo natural), error de puntería ×1,6, piernas ×0,75@NL@'
    '    y +10 % de fallo decidido — SOLO con la bola marcada viniendo;@NL@'
    '    sin poder, la IA es idéntica (física y árbitro intactos).@NL@'
    '  · PRESENTACIÓN DIEGÉTICA: icono del dueño (SuperPala_Portal.png)@NL@'
    '    en el registro (4.º poder de la matriz), modo ACTIVO con anillo@NL@'
    '    VIOLETA que se vacía (FASE 42), canto violeta en la silueta,@NL@'
    '    anillos de ENTRADA/SALIDA en el mundo, tránsito visual de 0,16 s@NL@'
    '    (SOLO cosmético: la bola se hunde y reaparece) y voz propia ES/EN@NL@'
    '    («¡Súper portal!» / «Super portal!») embebida data-URI.@NL@'
    '  · Capa AJ nueva (qa_portal_v3641, 114 checks en vivo): agujas de la@NL@'
    '    spec completa + mecánica real headless — siembra ×2 → gatillo →@NL@'
    '    ventana con anillo; refresco SIN gasto; golpe portalizado con@NL@'
    '    reaparición legal, rapidez conservada y spin intacto; marca para@NL@'
    '    la IA; antirrebote 0,25 s; guards (saque/bola lenta/dirección);@NL@'
    '    3 golpes → fin; sin cargas → fuera; IA invalida su predicción;@NL@'
    '    y la PARTIDA NUEVA recoge todo (FASE 41 heredada). Capas AG/AH/AI@NL@'
    '    re-ancladas al 4.º poder (cola de precaliente 7 piezas).@NL@'
    '  · Conserva TODO: el PODER ACTIVO SE VE EN LA PALA (anillo de@NL@'
    '    tiempo, FASE 42), la PARTIDA NUEVA = PALA LIMPIA (hook del@NL@'
    '    árbitro, FASE 41), la INMEDIATEZ del gatillo, el halo rojo HIJO@NL@'
    '    de la bola, las flechas EN EL PLANO del icono, la matriz de@NL@'
    '    poderes (mega · efecto · imán · portal) con ciclo ⟷ sin envolver,@NL@'
    '    SÚPER EFECTO notorio (rival castigado ×2/×0,85), SÚPER IMÁN con@NL@'
    '    la spec completa del dueño, voces nativas e iconos embebidos, el@NL@'
    '    menú de campeonatos v3.6.31, el HALL OF FAME (FASE 29), el SALÓN@NL@'
    '    DEL ARTISTA (FASE 30), la SALA DEL PARTIDO y el MEJOR DE 3 (FASE@NL@'
    '    31), el HALL SIN PALA NI BOLA (FASE 32), la coronación épica y la@NL@'
    '    RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE PALA,@NL@'
    '    el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.40-SDK6", "V3.6.41-SDK6"),
    ("3.6.40-SDK6", "3.6.41-SDK6"),
    ("v3640-sdk6", "v3641-sdk6"),
    ("3.6.40", "3.6.41"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.41-SDK6", "frente a V3.6.40-SDK6"),
    ("tras probar V3.6.41", "tras probar V3.6.40"),
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
            print(f"  ✓ {f.name}: notas FASE 43 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3641 LISTA")


if __name__ == "__main__":
    main()
