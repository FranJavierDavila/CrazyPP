#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 30 · GENERADOR DEL DIRECTORIO DE RELEASE v3624
======================================================================
Crea scripts/release-v3624/ a partir de scripts/release-v3623/ con:
  · reemplazos de versión (3.6.23-SDK6 → 3.6.24-SDK6 · v3623-sdk6 → v3624-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 26 — EL TREN EN EL
    DISPOSITIVO REAL), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.2 (statechange/ignoraMute
    en setVol/suena consciente) y manifest del oeste v54.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3624 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3623"
DEST = RAIZ / "scripts" / "release-v3624"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 25"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 26 — EL TREN EN EL DISPOSITIVO REAL)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.23-SDK6):@NL@'
    '  · FASE 26 (ronda 30, informe del dueño tras V3.6.23: «solo@NL@'
    '    caballos» — la única pista que llegaba al hardware de la Quest@NL@'
    '    era la que escribe su ganancia DIRECTO por frame): tres agujeros@NL@'
    '    del dispositivo cerrados EN EL SDK v1.5.2, una vez para los 5@NL@'
    '    campeonatos.@NL@'
    '  · (a) createSfx.play() con el AudioContext aún no «running»@NL@'
    '    DESCARTABA el disparo — y un one-shot (llegada, túnel) no tiene@NL@'
    '    segunda oportunidad: queda PENDIENTE y el «statechange» del@NL@'
    '    propio contexto lo dispara al despertar. (b) createBucle.on()@NL@'
    '    con el contexto dormido ya no olvida el arranque (wanted +@NL@'
    '    desfase/pan guardados y despiertan igual). (c) suena() ya no@NL@'
    '    miente con instancias de contextos muertos (re-bind de VR): la@NL@'
    '    auto-reparación vuelve a actuar. (d) setVol respeta ignoraMute:@NL@'
    '    la escritura viva ya no re-aplica el mute de MÚSICA.@NL@'
    '  · El vagón SUENA en los momentos EXACTOS que pidió el dueño:@NL@'
    '    Tren_Llegada «poco después de que se anuncien los segundos para@NL@'
    '    llegar a la estación» (+1,2 s del anuncio de megafonía), Tunel@NL@'
    '    «cuando en el parallax del plano exterior se cargan las imágenes@NL@'
    '    tunelboca.png, que es el comienzo de la entrada al túnel» y vias@NL@'
    '    desde la salida hasta el freno, con setVol directo por frame (el@NL@'
    '    mecanismo probado del galope) + reintentos de los one-shots.@NL@'
    '  · Capa V ampliada a 52 checks (qa_tren_audio_v3624) + arnés@NL@'
    '    runtime que CONDUCE el juego real por los eventos reales@NL@'
    '    (qa_tren_audio_rt_v3624, 23 checks).@NL@'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD@NL@'
    '    SDF de contacto, el saque VR realista, el hall del@NL@'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas@NL@'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.23-SDK6", "V3.6.24-SDK6"),
    ("3.6.23-SDK6", "3.6.24-SDK6"),
    ("v3623-sdk6", "v3624-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 26 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.23"' in txt:
                txt = txt.replace('grep -c "3.6.23"', 'grep -c "3.6.24"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.24")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.23" in txt:
                txt = txt.replace("menciones 3.6.23", "menciones 3.6.24")
                txt = txt.replace("n3623 = int", "n3624 = int").replace("{n3623}", "{n3624}").replace("if n3623 < 4", "if n3624 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.24")
            # guard del SDK: la versión viva ahora es 1.5.2 (FASE 10)
            if "const SDK_VERSION = '1.5.1'" in txt:
                txt = txt.replace("const SDK_VERSION = '1.5.1'",
                                  "const SDK_VERSION = '1.5.2'")
                print("  ✓ build_zip.py: guard del SDK actualizado a 1.5.2")
            # guard de adopción: el manifest de oeste sube a v54 (note_v2144)
            if "'oeste': (53," in txt:
                txt = txt.replace("'oeste': (53,", "'oeste': (54,")
                txt = txt.replace("verificada: oeste v53", "verificada: oeste v54")
                txt = txt.replace("oeste v53 (BSO+vagón)", "oeste v54 (BSO+vagón)")
                txt = txt.replace("PowerSign SDK5 verificada: oeste v53", "PowerSign SDK5 verificada: oeste v54")
                print("  ✓ build_zip.py: guard de adopción del manifest de oeste → v54")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.24-SDK6") == 1:
            txt = txt.replace("frente a V3.6.24-SDK6", "frente a V3.6.23-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.23)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3624 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.23-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n23 = bz.count("3.6.23-SDK6")
    if n23 != 1 or "frente a V3.6.23-SDK6" not in bz:
        print(f"aviso: 3.6.23-SDK6 queda ×{n23} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3623-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.24-SDK6" not in bz or "FASE 26" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    if "const SDK_VERSION = '1.5.2'" not in bz:
        print("FALLO: build_zip.py sin el guard del SDK 1.5.2")
        sys.exit(1)
    if "'oeste': (54," not in bz:
        print("FALLO: build_zip.py sin el guard del manifest v54")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_tren_audio_v3624" not in bz:
        print("FALLO: el bloque nuevo no cita qa_tren_audio_v3624")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3624 listo → python3 scripts/release-v3624/build_zip.py")


if __name__ == "__main__":
    main()
