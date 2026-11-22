#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 51 · GENERADOR DEL DIRECTORIO DE RELEASE v3643
======================================================================
Crea scripts/release-v3643/ a partir de scripts/release-v3642/ con:
  · reemplazos de versión (3.6.42-SDK6 → 3.6.43-SDK6 · v3642-sdk6 → v3643-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 45 — los superpoderes SE
    VEN y SE OYEN, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3643 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3642"
DEST = RAIZ / "scripts" / "release-v3643"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 44"
BLOQUE_FIN = ("CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 45 — LOS SUPERPODERES SE VEN Y SE@NL@'
    'OYEN — informe del dueño tras probar V3.6.42 en el Quest 3, corregido@NL@'
    'pieza a pieza)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.42-SDK6):@NL@'
    '  · SÚPER EFECTO EXAGERADO («no noto los efectos… es preciso@NL@'
    '    exagerarlo para que visualmente veamos el resultado»): el brush@NL@'
    '    generado sube a ×3, la curva Magnus en vuelo a ×2,2, el acople del@NL@'
    '    bote a ×2,4 y el tope de giro a ×3 — la bola marcada CURVA a la@NL@'
    '    vista; su halo rojo crece un 35 % con pulso más vivo.@NL@'
    '  · SÚPER IMÁN ENTENDIBLE (petición literal: «ampliar un poco el radio@NL@'
    '    de influencia y si la bola entra dentro del mismo que aparezcan@NL@'
    '    unas pequeñas flechas desde la bola en dirección al centro de@NL@'
    '    nuestra pala indicando que está siendo atraída y que sea así»):@NL@'
    '    radio 0,45→0,75 m, empuje ×5 m/s², Δv 0,60; TRES FLECHAS cian en@NL@'
    '    línea bola→pala aparecen cuando la bola entra en el campo y laten@NL@'
    '    si el campo la empuja; y el RESCATE NUEVO: una bola que se nos@NL@'
    '    escapa (cruzada o larga, viniendo a nuestra mitad) es atraída de@NL@'
    '    VERDAD hacia el punto dulce (6 m/s², tope 0,85 m/s).@NL@'
    '  · SÚPER PORTAL CONSISTENTE («a veces puedo golpear varios portales y@NL@'
    '    otras parece que con uno solo me desaparece»): el gasto iba POR@NL@'
    '    GOLPE — con el sorteo ×1 la ventana moría al primer portal. Ahora@NL@'
    '    la ACTIVACIÓN gasta 1 carga y la ventana trae SIEMPRE SUS 3 GOLPES@NL@'
    '    PORTALIZADOS (u 8 s); re-activar refresca. Nunca más «con uno me@NL@'
    '    desaparece».@NL@'
    '  · FEEDBACK SONORO DE FIN (petición del dueño: «en todos los super@NL@'
    '    efectos de pala debemos dar feedback sonoro cuando está a punto de@NL@'
    '    acabarse para que el jugador lo sepa sin mirar el indicador del@NL@'
    '    icono»): CUENTA SONORA 3·2·1 uniforme en los CUATRO poderes —@NL@'
    '    blips agudos al quedar 3, 2 y 1 segundo; el último sube de tono.@NL@'
    '  · PASSTHROUGH EN CALIENTE («que no nos lleve a la ventana principal@NL@'
    '    web desde VR, que sea algo directo desde VR a MR sin pasar por la@NL@'
    '    página web»): la sesión se pide SIEMPRE immersive-ar (el Quest 3@NL@'
    '    la soporta) y el conmutador de AJUSTES alterna tu habitación ⇄@NL@'
    '    sala virtual AL VUELO, sin cerrar la sesión y sin salir a la web.@NL@'
    '  · Capa AL nueva (qa_superpoderes_v3643): agujas de las 5 piezas +@NL@'
    '    agujas NEGATIVAS (el gasto por golpe y el vigilante del portal ya@NL@'
    '    no existen) + mecánica real headless (precaliente de 14 piezas,@NL@'
    '    flechas vivas según el campo, portal ×1 con 3 golpes, cuenta sonora@NL@'
    '    3·2·1 espiada, passthrough que canjea y restaura la escena).@NL@'
    '  · Conserva TODO: la matriz de poderes (mega · efecto · imán ·@NL@'
    '    portal) con ciclo ⟷ sin envolver, el PODER ACTIVO SE VE EN LA@NL@'
    '    PALA (anillo de tiempo, FASE 42), la PARTIDA NUEVA = PALA LIMPIA@NL@'
    '    (hook del árbitro, FASE 41), la INMEDIATEZ del gatillo, el halo@NL@'
    '    rojo HIJO de la bola, las flechas EN EL PLANO del icono, SÚPER@NL@'
    '    EFECTO notorio (rival castigado ×2/×0,85), el portal EXPLÍCITO de@NL@'
    '    3 fases con la IA penalizada en % (flanco único, r50), las voces@NL@'
    '    nativas y los iconos recortados, el menú de campeonatos v3.6.31,@NL@'
    '    el HALL OF FAME (FASE 29), el SALÓN DEL ARTISTA (FASE 30), la SALA@NL@'
    '    DEL PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN PALA NI BOLA@NL@'
    '    (FASE 32), la coronación épica y la RUTA LEYENDA del Oeste, el@NL@'
    '    tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la@NL@'
    '    CCD SDF de contacto, el saque VR realista, PRO CIRCUITO, intro@NL@'
    '    oficial, física viva, palas con carácter, CRAZY TV en directo y@NL@'
    '    los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.42-SDK6", "V3.6.43-SDK6"),
    ("3.6.42-SDK6", "3.6.43-SDK6"),
    ("v3642-sdk6", "v3643-sdk6"),
    ("3.6.42", "3.6.43"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.43-SDK6", "frente a V3.6.42-SDK6"),
    ("tras probar V3.6.43", "tras probar V3.6.42"),
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
            print(f"  ✓ {f.name}: notas FASE 45 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3643 LISTA")


if __name__ == "__main__":
    main()
