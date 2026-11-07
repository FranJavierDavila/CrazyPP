#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 45 · GENERADOR DEL DIRECTORIO DE RELEASE v3637
======================================================================
Crea scripts/release-v3637/ a partir de scripts/release-v3636/ con:
  · reemplazos de versión (3.6.36-SDK6 → 3.6.37-SDK6 · v3636-sdk6 → v3637-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 39 — SÚPER IMÁN + flechas
    propias + SÚPER EFECTO notorio, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip actualizados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 se CONSERVAN sin cambios (la mecánica vive en
    el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3637 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3636"
DEST = RAIZ / "scripts" / "release-v3637"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 38"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 39 — SUPERPODER DE PALA v3: SÚPER IMÁN +@NL@'
    'FLECHAS PROPIAS + SÚPER EFECTO NOTORIO, sobre la MATRIZ de 3 poderes@NL@'
    'con ciclo por joystick)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.36-SDK6):@NL@'
    '  · FASE 39 (ronda 45, peticiones del dueño tras probar V3.6.36):@NL@'
    '    «las flechas de la matriz… sea un poco más evidente, ahora al@NL@'
    '    estar encima de la imagen no se nota» — chevrons FUERA del icono:@NL@'
    '    sprites PROPIOS a cada lado (disco oscuro + chevron oro + pulso),@NL@'
    '    ‹ SOLO con vecino a la izquierda y › SOLO a la derecha.@NL@'
    '  · SÚPER EFECTO NOTORIO: la bola marcada lleva un HALO ROJO aditivo@NL@'
    '    anclado a la bola; su bote dispara un ANILLO rojo + barrido@NL@'
    '    sonoro; el RIVAL sufre la bola marcada (error de puntería ×2 y@NL@'
    '    piernas ×0,85 mientras vuela — «dificultar en un %»); y el@NL@'
    '    megáfono ahora ENSEÑA a aplicarlo («golpea con GIRO: arrastra la@NL@'
    '    pala al golpear»). Golden de física determinista INTACTO.@NL@'
    '  · NUEVO PODER «SÚPER IMÁN» (SuperPala_Iman.png del dueño + voz@NL@'
    '    nativa davefx/lessac): campo de 8 s que atrae SUAVE la bola al@NL@'
    '    PUNTO DULCE de la pala — la pala sigue mandada por la mano real,@NL@'
    '    no se teleporta nada, no se recuperan bolas que ya pasaron el@NL@'
    '    plano y la salida la calcula el modelo de contacto de siempre.@NL@'
    '    Parámetros prototipo del dueño: radio 0,45 m · plena asistencia@NL@'
    '    a 0,12 m · aceleración ≤3 m/s² · Δv lateral ≤0,35 m/s POR@NL@'
    '    APROXIMACIÓN · predicción ≤0,15 s · integración POR SUBPASO@NL@'
    '    (estable ante fluctuaciones de FPS). CADA IMPACTO ASISTIDO VÁLIDO@NL@'
    '    consume 1 carga (máx. 3 asistencias por activación) — el gatillo@NL@'
    '    solo abre el campo; las cargas solo se gastan cuando el imán@NL@'
    '    ayuda de verdad. Activo + gatillo = refresca la ventana.@NL@'
    '  · La MATRIZ ahora con 3 PODERES (mega · efecto · imán): misma carga@NL@'
    '    cada 11 golpes, mismo ciclo ⟷ sin envolver, mismo tope ×3, SOLO@NL@'
    '    campeonatos y llave «Pala Mejorada». 6 VOCES nativas embebidas@NL@'
    '    (3 poderes × ES davefx / EN lessac) + 3 iconos del dueño (Crece ·@NL@'
    '    Efecto · Imán) anclados al mango con etiqueta ×N.@NL@'
    '  · Capa AF nueva (qa_poderes_iman_v3637, en vivo): agujas + mecánica@NL@'
    '    real headless con micro-simulación de física del imán (empuje al@NL@'
    '    punto dulce · tope Δv · golden intacto sin el poder · bola pasada@NL@'
    '    no se recupera · bola que se aleja) + consumo por asistido + tope@NL@'
    '    de 3 + flechas por índice + halo + conmutador + hall. Capas AD y@NL@'
    '    AE retiradas del listado (historial conservado).@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.36-SDK6", "V3.6.37-SDK6"),
    ("3.6.36-SDK6", "3.6.37-SDK6"),
    ("v3636-sdk6", "v3637-sdk6"),
    ("3.6.36", "3.6.37"),   # guard del hub empaquetado (versión desnuda)
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
            print(f"  ✓ {f.name}: notas FASE 39 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
        for viejo, nuevo in GLOBALES:
            n = txt.count(viejo)
            if n:
                txt = txt.replace(viejo, nuevo)
                print(f"  ✓ {f.name}: {viejo} → {nuevo} (×{n})")
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
    print("RELEASE v3637 LISTA")


if __name__ == "__main__":
    main()
