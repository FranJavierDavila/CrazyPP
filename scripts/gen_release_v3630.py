#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 38 · GENERADOR DEL DIRECTORIO DE RELEASE v3630
======================================================================
Crea scripts/release-v3630/ a partir de scripts/release-v3629/ con:
  · reemplazos de versión (3.6.29-SDK6 → 3.6.30-SDK6 · v3629-sdk6 → v3630-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 32 — EL HALL ES UN MUSEO:
    SIN PALA NI BOLA), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3630 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3629"
DEST = RAIZ / "scripts" / "release-v3630"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 31"
BLOQUE_FIN = "    '    carácter, CRAZY TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 32 — EL HALL ES UN MUSEO:@NL@'
    'SIN PALA NI BOLA)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.29-SDK6):@NL@'
    '  · FASE 32 (ronda 38, informe del dueño: «en el hall no tiene sentido@NL@'
    '    que tengamos la pala y la pelota, ahí nunca se va a jugar»): la@NL@'
    '    estancia de entrada es un MUSEO, no una cancha — ni pala ni bola.@NL@'
    '  · SIN PALA: al entrar al Hall se apagan los mounts de pala de AMBOS@NL@'
    '    mandos; el cambio de mano (A/X) o la reconexión de un mando NO la@NL@'
    '    resucitan dentro de la estancia. Al salir (exitHall) la pala vuelve@NL@'
    '    a la mano activa, y solo ella.@NL@'
    '  · SIN BOLA: la bola nace OCULTA en el Hall (mesh + estela + sombra) —@NL@'
    '    _hallResetBall(true) es el único sitio que toca ballMesh.visible,@NL@'
    '    así que ningún repintado la resucita. Al volver a la cancha, la@NL@'
    '    bola reaparece limpia (posición/color/escala de fábrica).@NL@'
    '  · SIN JUEGO FANTASMA: en la estancia no hay preparación de saque (ni@NL@'
    '    bola en la mano del jugador, ni paseo/saque de la CPU), la IA duerme@NL@'
    '    y la bola NO se simula (sin gravedad, sin eventos, sin puntos@NL@'
    '    fantasma del árbitro). El gatillo sólo vive en el menú; el grip de@NL@'
    '    la mano libre no saca; el toggle de estela respeta el museo.@NL@'
    '  · EL GESTO DE SIEMPRE INTACTO: al arrancar un modo desde el Hall, el@NL@'
    '    saque por gatillo (asistido) y por grip (natural, velocidad real de@NL@'
    '    la mano) siguen exactamente igual en la cancha.@NL@'
    '  · EL MUSEO RESPIRA: trofeo plateado (Lathe + asas + haz + anillo), 7@NL@'
    '    bolas doradas flotantes, 3 luces propias y drawHall al día — el@NL@'
    '    SALÓN DEL ARTISTA (FASE 30) no sufre ni un pincelazo.@NL@'
    '  · Capa Y nueva (qa_hall_sin_pala_v3630, en vivo): 32 checks — mounts@NL@'
    '    apagados en el hall y vivos al salir, bola/sombra/estela ocultas,@NL@'
    '    setPaddleHand no resucita nada dentro, re-entrada idempotente, IA@NL@'
    '    dormida, gates del bucle servidos y el saque clásico intacto.@NL@'
    '  · Conserva TODO: la SALA DEL PARTIDO con su arte por defecto y el@NL@'
    '    MEJOR DE 3 (FASE 31), la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE@NL@'
    '    IMPULSO, la CCD SDF de contacto, el saque VR realista, PRO@NL@'
    '    CIRCUITO, intro oficial, física viva, palas con carácter, CRAZY TV@NL@'
    '    en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.29-SDK6", "V3.6.30-SDK6"),
    ("3.6.29-SDK6", "3.6.30-SDK6"),
    ("v3629-sdk6", "v3630-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 32 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.29"' in txt:
                txt = txt.replace('grep -c "3.6.29"', 'grep -c "3.6.30"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.30")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.29" in txt:
                txt = txt.replace("menciones 3.6.29", "menciones 3.6.30")
                txt = txt.replace("n3629 = int", "n3630 = int").replace("{n3629}", "{n3630}").replace("if n3629 < 4", "if n3630 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.30")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.30-SDK6") == 1:
            txt = txt.replace("frente a V3.6.30-SDK6", "frente a V3.6.29-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.29)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3630 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.29-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n29 = bz.count("3.6.29-SDK6")
    if n29 != 1 or "frente a V3.6.29-SDK6" not in bz:
        print(f"aviso: 3.6.29-SDK6 queda ×{n29} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3629-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.30-SDK6" not in bz or "FASE 32" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # guards CONSERVADOS: SDK 1.5.4 y oeste v56 siguen pinchados
    if "const SDK_VERSION = '1.5.4'" not in bz:
        print("FALLO: el guard del SDK 1.5.4 se perdió")
        sys.exit(1)
    if "'oeste': (56," not in bz:
        print("FALLO: el guard del manifest v56 se perdió")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_hall_sin_pala_v3630" not in bz:
        print("FALLO: las notas no citan la capa Y nueva")
        sys.exit(1)
    print(f"\n✓ release-v3630 generada y verificada ({DEST})")


if __name__ == "__main__":
    main()
