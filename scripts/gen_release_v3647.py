#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 55 · GENERADOR DEL DIRECTORIO DE RELEASE v3647
======================================================================
Crea scripts/release-v3647/ a partir de scripts/release-v3646/ con:
  · reemplazos de versión (3.6.46-SDK6 → 3.6.47-SDK6 · v3646-sdk6 → v3647-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 49 — el SÚPER EFECTO SÓLO
    vive en el INTERCAMBIO: nunca sobre el saque propio ni el del rival,
    sólo en las jugadas del jugador, y su firma SÓLO en el bote sobre la
    mesa del rival; el resto del tiempo, juego normal),
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3647 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3646"
DEST = RAIZ / "scripts" / "release-v3647"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 48"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 49 — EL EFECTO SÓLO VIVE EN EL@NL@'
    'INTERCAMBIO — el Súper Efecto deja de tocar saques y botes ajenos,@NL@'
    'a petición del dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.46-SDK6):@NL@'
    '  · EL EFECTO SÓLO EN EL INTERCAMBIO: «SOLO debe aplicar el efecto@NL@'
    '    durante el intercambio de pelotas NUNCA sobre el saca ni mío ni@NL@'
    '    del rival». Tu SAQUE vuelve a ser un saque de siempre aunque el@NL@'
    '    poder esté armado (sin brush ×2, sin marca, sin halo) — y la@NL@'
    '    ventana del rival, el arkanoid y los puntos muertos también son@NL@'
    '    juego normal: la pala del jugador conoce el estado del punto y@NL@'
    '    sólo en RALLY clasifica el barrido.@NL@'
    '  · LA FIRMA SÓLO EN LA MESA DEL RIVAL: «siempre en el bote sobre@NL@'
    '    la mesa del rival» — topspin acelerado, backspin casi parado y@NL@'
    '    sidespin con patada SÓLO ocurren cuando TU bola con efecto bota@NL@'
    '    en la MITAD DEL RIVAL; un mishit que bote en tu mitad es bote@NL@'
    '    físico normal (sin firma ni acople ×2,4).@NL@'
    '  · VERIFICACIÓN: capa AP nueva (qa_efecto_rally_v3647, 22 checks)@NL@'
    '    con mecánica headless real — saque limpio con poder armado,@NL@'
    '    control del intercambio, fuera del rally, compatibilidad de@NL@'
    '    sims, y los tres botes + acople comparados por pares gemelos en@NL@'
    '    ambas mitades · AO y matriz re-ancladas a la puerta de mitad.@NL@'
    '    Golden de física INTACTO (11/11).@NL@'
    '  · Conserva TODO: el spin real con su clasificación por barrido y@NL@'
    '    su señal por tipo (halo + anillo tintados y barrido sonoro), la@NL@'
    '    penalización al rival en % (error ×2 · piernas ×0,85), el GANCHO@NL@'
    '    del imán al centro de la pala con PALA METÁLICA −80 %, el clamp@NL@'
    '    del mango del rival fuera de la mesa, la bomba por intervalos de@NL@'
    '    15 s y el ladrillo eléctrico con su cadena (FASE 47), la matriz@NL@'
    '    de poderes con ciclo ⟷, el portal EXPLÍCITO con la IA penalizada@NL@'
    '    en %, el passthrough EN CALIENTE, las voces nativas, el HALL OF@NL@'
    '    FAME, el SALÓN DEL ARTISTA, la SALA DEL PARTIDO y el MEJOR DE 3,@NL@'
    '    la coronación épica y la RUTA LEYENDA del Oeste, PRO CIRCUITO,@NL@'
    '    el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto,@NL@'
    '    el saque VR realista, física viva, palas con carácter, CRAZY TV@NL@'
    '    en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.46-SDK6", "V3.6.47-SDK6"),
    ("3.6.46-SDK6", "3.6.47-SDK6"),
    ("v3646-sdk6", "v3647-sdk6"),
    ("3.6.46", "3.6.47"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.47-SDK6", "frente a V3.6.46-SDK6"),
    ("tras probar V3.6.47", "tras probar V3.6.46"),
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
            print(f"  ✓ {f.name}: notas FASE 49 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3647 LISTA")


if __name__ == "__main__":
    main()
