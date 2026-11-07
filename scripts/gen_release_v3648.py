#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 56 · GENERADOR DEL DIRECTORIO DE RELEASE v3648
======================================================================
Crea scripts/release-v3648/ a partir de scripts/release-v3647/ con:
  · reemplazos de versión (3.6.47-SDK6 → 3.6.48-SDK6 · v3647-sdk6 → v3648-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 50 — PODERES HONESTOS:
    20 TOQUES Y 10 SEGUNDOS, la norma íntegra del dueño: concesión sólo
    pasados los 20 toques, Súper Efecto y Súper Imán con ventanas de 10 s
    puramente temporales, el imán FRENA la bola y nunca arma sobre el
    saque del rival),
    sustituido por MARCADORES, método ronda 26.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3648 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3647"
DEST = RAIZ / "scripts" / "release-v3648"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 49"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 50 — PODERES HONESTOS: 20 TOQUES Y@NL@'
    '10 SEGUNDOS — la norma íntegra del dueño para los superpoderes@NL@'
    'de pala)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.47-SDK6):@NL@'
    '  · CONCESIÓN SÓLO PASADOS LOS 20 TOQUES: «Todos los superpoderes@NL@'
    '    de la pala que se concedan superados los 20 toques no antes» —@NL@'
    '    la cadencia sube de 11 a 20 TOQUES de rally (20 → +1 carga ·@NL@'
    '    40 → ×2 · 60 → ×3 · tope ×3 honesto): MEGA, EFECTO, IMÁN y@NL@'
    '    PORTAL pasan por la MISMA puerta.@NL@'
    '  · SÚPER EFECTO = 10 SEGUNDOS EXACTOS: «sólo está activo 10@NL@'
    '    segundos desde la activación» — el RELOJ es la única ley: se@NL@'
    '    RETIRA el tope de 5 golpes que cerraba la ventana antes de@NL@'
    '    tiempo. La ventaja del bote sigue siendo SÓLO NUESTRA (firma@NL@'
    '    en la mesa del rival) y el perjudicado siempre el rival.@NL@'
    '  · SÚPER IMÁN = 10 SEGUNDOS + FRENO: «que ralentice la bola y la@NL@'
    '    dirija hacia el centro de nuestra pala» — el GANCHO ahora@NL@'
    '    TAMBIÉN FRENA la bola (freno exponencial 1,1/s con suelo de@NL@'
    '    0,15 m/s: el vuelo nunca muere) mientras la arrastra al CENTRO@NL@'
    '    vivo de la hoja; se RETIRA el tope de 3 asistencias (el campo@NL@'
    '    vive sus 10 s o se apaga sin cargas) y NUNCA arma sobre la bola@NL@'
    '    del SAQUE del rival (isServeBall) — los saques son juego normal.@NL@'
    '  · PASADOS LOS 10 s TODO VUELVE A LA NORMALIDAD (relojes@NL@'
    '    independientes por poder, cuenta sonora 3·2·1 intacta).@NL@'
    '  · VERIFICACIÓN: capa AQ nueva (qa_poderes_10s20_v3648) con@NL@'
    '    mecánica headless real — cadencia 19 no concede / 20 concede /@NL@'
    '    40/60 acumula / 80 tope, ventanas de 10 s vivas enteras, saque@NL@'
    '    del rival limpio y FRENO medido en física viva (golden@NL@'
    '    intacto) · AF/AG/AH/AI re-ancladas a la norma r56.@NL@'
    '  · Conserva TODO: el spin real por barrido con su firma SÓLO en la@NL@'
    '    mesa del rival (r55), la pala honesta fuera del rally, el@NL@'
    '    GANCHO del imán con PALA METÁLICA −80 %, el clamp del mango del@NL@'
    '    rival, la bomba por intervalos y el ladrillo eléctrico con su@NL@'
    '    cadena, el portal EXPLÍCITO con la IA penalizada, la matriz con@NL@'
    '    ciclo ⟷, las voces nativas, el passthrough EN CALIENTE, el@NL@'
    '    HALL OF FAME, el SALÓN DEL ARTISTA, la SALA DEL PARTIDO, PRO@NL@'
    '    CIRCUITO, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD SDF,@NL@'
    '    el saque VR realista, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.47-SDK6", "V3.6.48-SDK6"),
    ("3.6.47-SDK6", "3.6.48-SDK6"),
    ("v3647-sdk6", "v3648-sdk6"),
    ("3.6.47", "3.6.48"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.48-SDK6", "frente a V3.6.47-SDK6"),
    ("tras probar V3.6.48", "tras probar V3.6.47"),
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
            print(f"  ✓ {f.name}: notas FASE 50 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3648 LISTA")


if __name__ == "__main__":
    main()
