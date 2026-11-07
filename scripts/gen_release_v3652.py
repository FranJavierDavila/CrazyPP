#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 60 · GENERADOR DEL DIRECTORIO DE RELEASE v3652
======================================================================
Crea scripts/release-v3652/ a partir de scripts/release-v3651/ con:
  · reemplazos de versión (3.6.51-SDK6 → 3.6.52-SDK6 · v3651-sdk6 → v3652-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 54 — ACADEMIA DESPEJADA,
    TROQUELES INMUNES, ORBE A DIETA: los tres arreglos del informe del
    dueño tras probar V3.6.51 en el Quest + bonus del mapa del taller).
    sustituido por MARCADORES, método ronda 26/59.
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v27 (magia v33 y valle_neon v5 NO están en los
    guards del empaquetador — sólo en la capa A/C).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3652 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3651"
DEST = RAIZ / "scripts" / "release-v3652"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r59 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 53 — LA ACADEMIA: EL TUTORIAL QUE"
              + BS_N + "'")
BLOQUE_FIN = "    '    campeonatos." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 54 — ACADEMIA DESPEJADA, TROQUELES@NL@'
    'INMUNES, ORBE A DIETA — los tres arreglos del informe del dueño@NL@'
    'tras probar V3.6.51-SDK6 en el Quest)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.51-SDK6):@NL@'
    '  · ACADEMIA DESPEJADA (informe del dueño: «el tutorial se queda@NL@'
    '    bloqueado, se superpone con otras ventanas del menú y no es@NL@'
    '    pulsable»): al entrar —por el banner del HUB, la oferta «¿PRIMERA@NL@'
    '    VEZ?» o AJUSTES— el MENÚ SE CIERRA. Antes nacía del clic y seguía@NL@'
    '    abierto delante del panel de la academia (misma altura de ojos,@NL@'
    '    renderOrder 990 sobre 985) comiéndose los rayos del gatillo; y@NL@'
    '    toggleMenu() duerme con calib, así que se cierra DIRECTO. Salida@NL@'
    '    SIEMPRE disponible: B/Y saltan, JUGAR YA en el paso 8.@NL@@NL@'
    '  · TROQUELES INMUNES (informe: «me has quitado de todos los@NL@'
    '    escenarios los troqueles»): NUNCA se borraron — las pruebas@NL@'
    '    especiales (asedio/vagón de la Oeste, recortables heredados de@NL@'
    '    la Estación) izan un cerrojo para esconderlos y lo bajan al@NL@'
    '    terminar; si la salida se colaba por un camino no previsto, el@NL@'
    '    cerrojo quedaba izado y los troqueles no volvían en NINGÚN@NL@'
    '    escenario hasta recargar. AUTOCURACIÓN: leaveAll los libera@NL@'
    '    SIEMPRE (también en su salida temprana). Sistema verificado@NL@'
    '    vivo en los 5 campeonatos.@NL@@NL@'
    '  · ORBE A DIETA (informe: «la etapa 4 del orbe en el campeonato de@NL@'
    '    Wizard supera los 1000 y pico… como mucho la mitad, y penaliza@NL@'
    '    los FPS»): ORBE COMPLEJO de 1.419 → 515 LADRILLOS (−63,7%) con@NL@'
    '    la MISMA envergadura (radio 0,625 m), dianas un 42% más gordas@NL@'
    '    (ladrillo 0,125 = el del orbe normal), núcleo/medio conservados,@NL@'
    '    sin prórrogas ni cambios de reglas — cima 2,07 m (< HUD 2,28) y@NL@'
    '    base apoyada en la mesa. −64% de instancias: alivio real de FPS.@NL@@NL@'
    '  · BONUS DE LA AUDITORÍA (directiva: «cuidado con el solapamiento@NL@'
    '    de menús… verificar que son manejables»): el MAPA DEL TALLER de@NL@'
    '    Valle Neón llevaba SIN VERSE desde la migración SDK5 (se colgaba@NL@'
    '    antes de existir: THREE rechazaba el add). Re-enganchado.@NL@@NL@'
    '  · VERIFICACIÓN: capa AU nueva (qa_r60_v3652, 34 checks con@NL@'
    '    MECÁNICA REAL headless: menú cerrado en las 3 puertas, cerrojo@NL@'
    '    autocurativo con recorrida de los 5 decorados, recuento del@NL@'
    '    orbe sobre las constantes servidas y batería SIN errores JS).@NL@@NL@'
    '  · Conserva TODO: LA ACADEMIA de r59 (9 pasos con práctica real),@NL@'
    '    los 5 poderes con sus ventanas, la norma de los 20 toques, la@NL@'
    '    voz del selector, las expresiones de los 6 rivales, la bomba por@NL@'
    '    intervalos y el ladrillo eléctrico con su cadena, el passthrough@NL@'
    '    EN CALIENTE, el SALÓN DEL ARTISTA, la SALA DEL PARTIDO, PRO@NL@'
    '    CIRCUITO, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD SDF,@NL@'
    '    el saque VR realista, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.51-SDK6", "V3.6.52-SDK6"),
    ("3.6.51-SDK6", "3.6.52-SDK6"),
    ("v3651-sdk6", "v3652-sdk6"),
    ("3.6.51", "3.6.52"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.52-SDK6", "frente a V3.6.51-SDK6"),
    ("tras probar V3.6.52", "tras probar V3.6.51"),
    ("tras V3.6.52", "tras V3.6.51"),
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
            print(f"  ✓ {f.name}: notas FASE 54 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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

    # guard de identidad: la estirpe v369-sdk5 NUNCA se toca
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    if "v369-sdk5" not in bz or "V3.6.52-SDK6" not in bz:
        print("FALLO: guard de identidad roto en build_zip.py")
        sys.exit(1)
    print("· guard v369-sdk5 intacto · V3.6.52-SDK6 presente")
    print("GEN_RELEASE_V3652 COMPLETO")


if __name__ == "__main__":
    main()
