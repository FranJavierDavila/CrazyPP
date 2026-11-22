#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 31 · GENERADOR DEL DIRECTORIO DE RELEASE v3625
======================================================================
Crea scripts/release-v3625/ a partir de scripts/release-v3624/ con:
  · reemplazos de versión (3.6.24-SDK6 → 3.6.25-SDK6 · v3624-sdk6 → v3625-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 27 — EL GALOPE FANTASMA),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.3 (play booleano/sinPend/
    huérfana muerta/busyAt) y manifest del oeste v55.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3625 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3624"
DEST = RAIZ / "scripts" / "release-v3625"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 26"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 27 — EL GALOPE FANTASMA)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.24-SDK6):@NL@'
    '  · FASE 27 (ronda 31, informe del dueño tras V3.6.24: «los caballos@NL@'
    '    no se amortiguan ni desaparecen… · vias casi imperceptible ·@NL@'
    '    tunel y llegada no suenan nunca»): EL GALOPE FANTASMA, cerrado@NL@'
    '    en el SDK v1.5.3 y en el vagón.@NL@'
    '  · SDK v1.5.3, una vez para los 5 campeonatos: (a) createSfx.play()@NL@'
    '    devuelve BOOLEANO — true sólo cuando el disparo fue REAL; los@NL@'
    '    one-shots del vagón se retiraban de la agenda por LLAMAR a play@NL@'
    '    y un disparo tragado (contexto dormido / buffer tarde) era@NL@'
    '    silencio eterno. (b) opción sinPend: el que reintentA cada frame@NL@'
    '    gobierna y el arranque real CONSUME el pend del nombre (cero@NL@'
    '    dobles). (c) createBucle.on() MATA la instancia huérfana de un@NL@'
    '    contexto viejo (stop+disconnect) — sin galope fantasma eterno.@NL@'
    '    (d) vigilante anti-decode-colgado (20 s) en createSfx/createBucle.@NL@'
    '  · En el vagón: la auto-reparación del galope SÓLO con jinete VIVO@NL@'
    '    (paso/ida/ventana/fuga) — sin el filtro revivía el bucle cada@NL@'
    '    frame tras el off seco de la muerte (seguía galopando herido, en@NL@'
    '    el fade y tras gone); rodadura vias 0,13 → 0,30 (enterrada bajo@NL@'
    '    la música del vagón); reintentos honestos con margen 9 s.@NL@'
    '  · Capa V ampliada a 63 checks (qa_tren_audio_v3625) + arnés runtime@NL@'
    '    del CICLO DE VIDA del galope (qa_tren_audio_rt_v3625, 32 checks:@NL@'
    '    nace 0,45 · se amortigua en fuga 0,45→0,16 · calla SECO al balazo@NL@'
    '    · cero resurrecciones · indios simétricos · contrato del SDK).@NL@'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD@NL@'
    '    SDF de contacto, el saque VR realista, el hall del@NL@'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas@NL@'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.24-SDK6", "V3.6.25-SDK6"),
    ("3.6.24-SDK6", "3.6.25-SDK6"),
    ("v3624-sdk6", "v3625-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 27 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.24"' in txt:
                txt = txt.replace('grep -c "3.6.24"', 'grep -c "3.6.25"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.25")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.24" in txt:
                txt = txt.replace("menciones 3.6.24", "menciones 3.6.25")
                txt = txt.replace("n3624 = int", "n3625 = int").replace("{n3624}", "{n3625}").replace("if n3624 < 4", "if n3625 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.25")
            # guard del SDK: la versión viva ahora es 1.5.3 (FASE 11)
            if "const SDK_VERSION = '1.5.2'" in txt:
                txt = txt.replace("const SDK_VERSION = '1.5.2'",
                                  "const SDK_VERSION = '1.5.3'")
                print("  ✓ build_zip.py: guard del SDK actualizado a 1.5.3")
            # guard de adopción: el manifest de oeste sube a v55 (note_v2145)
            if "'oeste': (54," in txt:
                txt = txt.replace("'oeste': (54,", "'oeste': (55,")
                txt = txt.replace("verificada: oeste v54", "verificada: oeste v55")
                txt = txt.replace("oeste v54 (BSO+vagón)", "oeste v55 (BSO+vagón)")
                txt = txt.replace("PowerSign SDK5 verificada: oeste v54", "PowerSign SDK5 verificada: oeste v55")
                print("  ✓ build_zip.py: guard de adopción del manifest de oeste → v55")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.25-SDK6") == 1:
            txt = txt.replace("frente a V3.6.25-SDK6", "frente a V3.6.24-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.24)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3625 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.24-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n24 = bz.count("3.6.24-SDK6")
    if n24 != 1 or "frente a V3.6.24-SDK6" not in bz:
        print(f"aviso: 3.6.24-SDK6 queda ×{n24} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3624-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.25-SDK6" not in bz or "FASE 27" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    if "const SDK_VERSION = '1.5.3'" not in bz:
        print("FALLO: build_zip.py sin el guard del SDK 1.5.3")
        sys.exit(1)
    if "'oeste': (55," not in bz:
        print("FALLO: build_zip.py sin el guard del manifest v55")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_tren_audio_v3625" not in bz:
        print("FALLO: el bloque nuevo no cita qa_tren_audio_v3625")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3625 listo → python3 scripts/release-v3625/build_zip.py")


if __name__ == "__main__":
    main()
