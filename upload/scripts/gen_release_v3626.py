#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 33 · GENERADOR DEL DIRECTORIO DE RELEASE v3626
======================================================================
Crea scripts/release-v3626/ a partir de scripts/release-v3625/ con:
  · reemplazos de versión (3.6.25-SDK6 → 3.6.26-SDK6 · v3625-sdk6 → v3626-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 28 — LOS ONE-SHOTS VIAJAN
    EN EL MOTOR DEL GALOPE), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 (createBucle.precarga)
    y manifest del oeste v56.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3626 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3625"
DEST = RAIZ / "scripts" / "release-v3626"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 27"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 28 — LOS ONE-SHOTS VIAJAN EN EL MOTOR@NL@'
    'DEL GALOPE)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.25-SDK6):@NL@'
    '  · FASE 28 (ronda 33, informe del dueño tras V3.6.25 en el@NL@'
    '    dispositivo real: «la entrada en el túnel no suena… las@NL@'
    '    llegadas tampoco, igual concatenando el sonido con la voz que@NL@'
    '    sí suena»): los ONE-SHOTS SORDOS EN EL CASCO, cerrados con un@NL@'
    '    CAMBIO DE MOTOR.@NL@'
    '  · Cuatro versiones del camino createSfx (v3.6.22→25) no llegaron@NL@'
    '    al hardware de la Quest, mientras el MISMO SDK con createBucle@NL@'
    '    llevaba galopes y rodadura al casco desde el primer día: los@NL@'
    '    one-shots (Tunel + Tren_Llegada) VIAJAN ahora en el motor@NL@'
    '    PROBADO — cada pista es un createBucle (ignoraMute, fades@NL@'
    '    cortos) y el disparo es on(), con revival por statechange y@NL@'
    '    espera de buffer dentro del motor; _pistaTrenStep conduce con@NL@'
    '    reloj de play sólo con suena() honesto y corte con off() antes@NL@'
    '    del wrap de src.loop (margen 0,45 s).@NL@'
    '  · MOMENTOS DEL DUEÑO: Tunel.mp3 CUANDO SE BAJA LA LUZ (paso@NL@'
    '    pre→in del túnel, ya no al asomar la boca a lo lejos) y@NL@'
    '    Tren_Llegada.mp3 CONCATENADO CON LA VOZ (entra justo al terminar@NL@'
    '    la locución real, _voiceDur + 0,35 s). Las dos pistas@NL@'
    '    re-codificadas al perfil probado de caballos.mp3 (44100 Hz ·@NL@'
    '    256 kbps) — cero rarezas de encoder para el decoder del casco.@NL@'
    '  · SDK v1.5.4, una vez para los 5 campeonatos: createBucle.precarga@NL@'
    '    () — pedir + decodificar SIN sonar (patrón load* de la casa)@NL@'
    '    para calentar el buffer de un one-shot minutos antes del disparo.@NL@'
    '  · Capa V re-anclada a 74 checks (qa_tren_audio_v3626) + arnés@NL@'
    '    runtime 36 checks (qa_tren_audio_rt_v3626: Tunel 1 vez AL BAJAR@NL@'
    '    LA LUZ · Llegada 1 vez CONCATENADA con la voz · galopes@NL@'
    '    intactos · precarga sin sonido · contrato del SDK 1.5.4).@NL@'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD@NL@'
    '    SDF de contacto, el saque VR realista, el hall del@NL@'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas@NL@'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.25-SDK6", "V3.6.26-SDK6"),
    ("3.6.25-SDK6", "3.6.26-SDK6"),
    ("v3625-sdk6", "v3626-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 28 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.25"' in txt:
                txt = txt.replace('grep -c "3.6.25"', 'grep -c "3.6.26"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.26")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.25" in txt:
                txt = txt.replace("menciones 3.6.25", "menciones 3.6.26")
                txt = txt.replace("n3625 = int", "n3626 = int").replace("{n3625}", "{n3626}").replace("if n3625 < 4", "if n3626 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.26")
            # guard del SDK: la versión viva ahora es 1.5.4 (FASE 12)
            if "const SDK_VERSION = '1.5.3'" in txt:
                txt = txt.replace("const SDK_VERSION = '1.5.3'",
                                  "const SDK_VERSION = '1.5.4'")
                print("  ✓ build_zip.py: guard del SDK actualizado a 1.5.4")
            # guard de adopción: el manifest de oeste sube a v56 (note_v2146)
            if "'oeste': (55," in txt:
                txt = txt.replace("'oeste': (55,", "'oeste': (56,")
                txt = txt.replace("verificada: oeste v55", "verificada: oeste v56")
                txt = txt.replace("oeste v55 (BSO+vagón)", "oeste v56 (BSO+vagón)")
                txt = txt.replace("PowerSign SDK5 verificada: oeste v55", "PowerSign SDK5 verificada: oeste v56")
                print("  ✓ build_zip.py: guard de adopción del manifest de oeste → v56")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.26-SDK6") == 1:
            txt = txt.replace("frente a V3.6.26-SDK6", "frente a V3.6.25-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.25)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3626 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.25-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n25 = bz.count("3.6.25-SDK6")
    if n25 != 1 or "frente a V3.6.25-SDK6" not in bz:
        print(f"aviso: 3.6.25-SDK6 queda ×{n25} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3625-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.26-SDK6" not in bz or "FASE 28" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    if "const SDK_VERSION = '1.5.4'" not in bz:
        print("FALLO: build_zip.py sin el guard del SDK 1.5.4")
        sys.exit(1)
    if "'oeste': (56," not in bz:
        print("FALLO: build_zip.py sin el guard del manifest v56")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_tren_audio_v3626" not in bz:
        print("FALLO: el bloque nuevo no cita qa_tren_audio_v3626")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3626 listo → python3 scripts/release-v3626/build_zip.py")


if __name__ == "__main__":
    main()
