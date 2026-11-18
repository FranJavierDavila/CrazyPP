#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 40 · GENERADOR DEL DIRECTORIO DE RELEASE v3632
======================================================================
Crea scripts/release-v3632/ a partir de scripts/release-v3631/ con:
  · reemplazos de versión (3.6.31-SDK6 → 3.6.32-SDK6 · v3631-sdk6 → v3632-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 34 — MEGA PALA CON
    FEEDBACK VISUAL: pala ×1,30 · aura y anillos de energía · power-up
    sonoro/háptica · aviso de agotamiento · carrera eager↔launch fuera),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos del oeste;
    la LOCURA sube a v24 — su guard del build_zip, si existe, se ajusta).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3632 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3631"
DEST = RAIZ / "scripts" / "release-v3632"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 33"
BLOQUE_FIN = "    '    en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 34 — MEGA PALA CON FEEDBACK VISUAL:@NL@'
    'PALA ×1,30 · AURA Y ANILLOS DE ENERGÍA · POWER-UP SONORO/HÁPTICA ·@NL@'
    'AVISO DE AGOTAMIENTO · CARRERA EAGER↔LAUNCH FUERA)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.31-SDK6):@NL@'
    '  · FASE 34 (ronda 40, petición del dueño: «si la MEGA PALA sí existe@NL@'
    '    debería dar feedback visual… aumentando el tamaño de la raqueta y@NL@'
    '    poniendo una alerta visual como de energía»): la MEGA PALA de La@NL@'
    '    Locura (Crazy Combo rally 6 tras vencer al Clown · radio ×1,38 ·@NL@'
    '    8 s) era INVISIBLE — ahora la pala CRECE a ×1,30 (montura visual,@NL@'
    '    la física no cambia) y se envuelve en ENERGÍA: aura dorada@NL@'
    '    (billboard) + doble anillo girando en el plano de la hoja.@NL@'
    '  · POWER-UP SONORO (arpegio arcade) + HÁPTICA al activarse y AVISO@NL@'
    '    ÚNICO en los <2 s finales: parpadeo rápido + sfx descendente (el@NL@'
    '    poder se agota). La energía cuelga de las DOS monturas de pala:@NL@'
    '    viaja sola si el jugador cambia de mano; leave() la recoge con@NL@'
    '    dispose completo (regla Quest: nada queda colgado).@NL@'
    '  · REGRESIÓN del radio corregida: si un startMatch ponía _megaT=0@NL@'
    '    directo (auto-revancha dentro de la ventana), el radio de@NL@'
    '    detección quedaba inflado hasta el fin de sesión — el update lo@NL@'
    '    restaura SIEMPRE.@NL@'
    '  · CARRERA eager↔launch CORREGIDA (núcleo c11): el arranque eager@NL@'
    '    marca _ppInited antes de que la init del módulo resuelva; un@NL@'
    '    launch() en esa ventana recibía el módulo sin cablear y start()@NL@'
    '    era un NO-OP silencioso (el campeonato no arrancaba). Ahora el@NL@'
    '    launch espera la init en vuelo: el campeonato SIEMPRE arranca.@NL@'
    '  · LA LOCURA módulo v24 (manifest + historial). Capa AA nueva@NL@'
    '    (qa_mega_pala_v3632, en vivo): 41 checks — agujas del módulo@NL@'
    '    servido + mecánica real en headless (launch, activación forzada,@NL@'
    '    escala de la montura, energía viva/apagada, bucle vivo,@NL@'
    '    restauración en leaveAll y monturas a escala 1).@NL@'
    '  · Conserva TODO: el menú de campeonatos v3.6.31 (texto fantasma@NL@'
    '    fuera · intro opcional · menú prioritario · haz-puntero), el HALL@NL@'
    '    SIN PALA NI BOLA (FASE 32), la SALA DEL PARTIDO y el MEJOR DE 3@NL@'
    '    (FASE 31), el SALÓN DEL ARTISTA (FASE 30), la coronación épica y@NL@'
    '    la RUTA LEYENDA del Oeste, el tren 100 % sonoro, el ESCUDO DE@NL@'
    '    PALA, el REACTOR DE IMPULSO, la CCD SDF de contacto, el saque VR@NL@'
    '    realista, PRO CIRCUITO, intro oficial, física viva, palas con@NL@'
    '    carácter, CRAZY TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.31-SDK6", "V3.6.32-SDK6"),
    ("3.6.31-SDK6", "3.6.32-SDK6"),
    ("v3631-sdk6", "v3632-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 34 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.31"' in txt:
                txt = txt.replace('grep -c "3.6.31"', 'grep -c "3.6.32"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.32")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.31" in txt:
                txt = txt.replace("menciones 3.6.31", "menciones 3.6.32")
                txt = txt.replace("n3631 = int", "n3632 = int").replace("{n3631}", "{n3632}").replace("if n3631 < 4", "if n3632 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.32")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
            # v3.6.32 (ronda 40): LA LOCURA sube a v24 (MEGA PALA visual) —
            # sus guards del build_zip se actualizan (lección ronda 40).
            if "'locura': (23," in txt:
                txt = txt.replace("'locura': (23,", "'locura': (24,")
                txt = txt.replace('locura v23', 'locura v24')
                print("  \u2713 build_zip.py: guards del manifest de locura v23 \u2192 v24")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.32-SDK6") == 1:
            txt = txt.replace("frente a V3.6.32-SDK6", "frente a V3.6.31-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.31)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3632 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.31-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n31 = bz.count("3.6.31-SDK6")
    if n31 != 1 or "frente a V3.6.31-SDK6" not in bz:
        print(f"aviso: 3.6.31-SDK6 queda ×{n31} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3631-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.32-SDK6" not in bz or "FASE 34" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    for guard, esperado in [("SDK_VERSION", "1.5.4"), ("version\": 56", "56"), ("locura v24", "24")]:
        if guard == "SDK_VERSION" and "1.5.4" not in bz:
            print("aviso: guard del SDK 1.5.4 no aparece (revisar)")
        if guard == "version\": 56" and 'version": 56' not in bz:
            print("aviso: guard del manifest oeste v56 no aparece (revisar)")
    print("OK · release-v3632 generado")


if __name__ == "__main__":
    main()
