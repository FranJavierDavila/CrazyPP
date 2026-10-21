#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 41 · GENERADOR DEL DIRECTORIO DE RELEASE v3633
======================================================================
Crea scripts/release-v3633/ a partir de scripts/release-v3632/ con:
  · reemplazos de versión (3.6.32-SDK6 → 3.6.33-SDK6 · v3632-sdk6 → v3633-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 35 — MEGA PALA 2.0
    «NÚCLEO DE ENERGÍA»: canto de energía ajustado a la silueta · núcleo
    en la garganta · uso voluntario por gatillo · recarga + crazy combo
    instantáneo), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste
    v56 se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos del
    oeste; la LOCURA sube a v25 — sus guards del build_zip se ajustan).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3633 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3632"
DEST = RAIZ / "scripts" / "release-v3633"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 34"
BLOQUE_FIN = ("    '    carácter, CRAZY TV en directo y los 5 campeonatos."
              + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 35 — MEGA PALA 2.0 «NÚCLEO DE ENERGÍA»:@NL@'
    'CANTO DE ENERGÍA AJUSTADO A LA SILUETA · NÚCLEO EN LA GARGANTA ·@NL@'
    'USO VOLUNTARIO POR GATILLO · RECARGA + CRAZY COMBO INSTANTÁNEO)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.32-SDK6):@NL@'
    '  · FASE 35 (ronda 41, informe del dueño: «el efecto de energía@NL@'
    '    está muy desajustado al tamaño de la pala, el aura dorada se@NL@'
    '    mete dentro de la propia pala quedando muy cutre, el jugador no@NL@'
    '    se entera de que tiene la Mega Pala y su uso debería ser@NL@'
    '    voluntario, por ejemplo apretando el gatillo»): REDISEÑO@NL@'
    '    COMPLETO de la MEGA PALA de La Locura.@NL@'
    '  · FUERA el billboard de 34 cm que atravesaba la hoja. CANTO DE@NL@'
    '    ENERGÍA: clon EXACTO de la pala montada con materiales@NL@'
    '    invertidos (BackSide) aditivos a escala 1,055 — borde dorado@NL@'
    '    que abraza la SILUETA desde fuera (depth test: donde la pala lo@NL@'
    '    tapa no se pinta — imposible entrar en la hoja).@NL@'
    '  · NÚCLEO dorado en la GARGANTA visible TODO el partido: dormido@NL@'
    '    (tenue) sin carga / vivo (halo + 26 chispas orbitando la hoja@NL@'
    '    por fuera) cuando está CARGADA + aro de carga que se llena — el@NL@'
    '    jugador SIEMPRE sabe que tiene el poder.@NL@'
    '  · USO VOLUNTARIO: el GATILLO con la bola en juego LIBERA la carga@NL@'
    '    (c12 → ChampLoader.megaTrigger → módulo); en saque el gatillo@NL@'
    '    sigue sacando. Cada partido arranca CARGADO; tras los 8 s la@NL@'
    '    recarga corre sola (14 s) y el CRAZY COMBO (rally 6) la llena@NL@'
    '    AL INSTANTE (si está activa, le repone los 8 s).@NL@'
    '  · ONDA DE CHOQUE al liberar + arpegio arcade + háptica; aviso@NL@'
    '    honesto «recargando» con blip grave si se aprieta sin carga;@NL@'
    '    chime + destello «lista de nuevo»; pista única al empezar el@NL@'
    '    primer partido; parpadeo de agotamiento intacto.@NL@'
    '  · LA LOCURA módulo v25 (manifest + historial). Capa AB nueva@NL@'
    '    (qa_mega_pala_v3633, en vivo): 85 checks — agujas del módulo y@NL@'
    '    del núcleo servidos + mecánica real headless (armado por@NL@'
    '    partido, liberación por gatillo, saque respetado, recarga,@NL@'
    '    combo instantáneo, sin-poder, leave con dispose).@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.32-SDK6", "V3.6.33-SDK6"),
    ("3.6.32-SDK6", "3.6.33-SDK6"),
    ("v3632-sdk6", "v3633-sdk6"),
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
        antes = len(txt)
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
            print(f"  ✓ {f.name}: notas FASE 35 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.32"' in txt:
                txt = txt.replace('grep -c "3.6.32"', 'grep -c "3.6.33"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.33")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.32" in txt:
                txt = txt.replace("menciones 3.6.32", "menciones 3.6.33")
                txt = txt.replace("n3632 = int", "n3633 = int").replace("{n3632}", "{n3633}").replace("if n3632 < 4", "if n3633 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.33")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
            # v3.6.33 (ronda 41): LA LOCURA sube a v25 (MEGA PALA 2.0) —
            # sus guards del build_zip se actualizan (lección ronda 40).
            if "'locura': (24," in txt:
                txt = txt.replace("'locura': (24,", "'locura': (25,")
                txt = txt.replace('locura v24', 'locura v25')
                print("  \u2713 build_zip.py: guards del manifest de locura v24 \u2192 v25")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.33-SDK6") == 1:
            txt = txt.replace("frente a V3.6.33-SDK6", "frente a V3.6.32-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.32)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3633 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.32-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n32 = bz.count("3.6.32-SDK6")
    if n32 != 1 or "frente a V3.6.32-SDK6" not in bz:
        print(f"aviso: 3.6.32-SDK6 queda ×{n32} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3632-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.33-SDK6" not in bz or "FASE 35" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    for guard, esperado in [("SDK_VERSION", "1.5.4"), ("version\": 56", "56"), ("locura v25", "25")]:
        if guard == "SDK_VERSION" and "1.5.4" not in bz:
            print("aviso: guard del SDK 1.5.4 no aparece (revisar)")
        if guard == "version\": 56" and 'version": 56' not in bz:
            print("aviso: guard del manifest oeste v56 no aparece (revisar)")
    print("OK · release-v3633 generado")


if __name__ == "__main__":
    main()
