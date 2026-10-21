#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 39 · GENERADOR DEL DIRECTORIO DE RELEASE v3631
======================================================================
Crea scripts/release-v3631/ a partir de scripts/release-v3630/ con:
  · reemplazos de versión (3.6.30-SDK6 → 3.6.31-SDK6 · v3630-sdk6 → v3631-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 33 — MENÚ DE CAMPEONATOS:
    texto fantasma fuera · intro opcional · menú prioritario · haz-puntero),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3631 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3630"
DEST = RAIZ / "scripts" / "release-v3631"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 32"
BLOQUE_FIN = "    '    en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 33 — MENÚ DE CAMPEONATOS:@NL@'
    'TEXTO FANTASMA FUERA · INTRO OPCIONAL · MENÚ PRIORITARIO · HAZ-PUNTERO)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.30-SDK6):@NL@'
    '  · FASE 33 (ronda 39, informe del dueño: «aparece un texto que no@NL@'
    '    tiene sentido… 11-point match vs the Clown… MEGA PADDLE»): el hint@NL@'
    '    heredado del ARCADE (v2.34) ya NO se pinta al pie del listado de@NL@'
    '    campeonatos. La MEGA PALA sigue viva donde toca: es el poder de La@NL@'
    '    Locura (Crazy Combo con rally de 6 tras vencer al Clown).@NL@'
    '  · INTRO SÓLO LA PRIMERA VEZ: el vídeo de la historia del rival se@NL@'
    '    muestra al entrar por PRIMERA vez a cada campeonato (conocer al@NL@'
    '    rival y dar contexto); las siguientes entradas van DIRECTAS a@NL@'
    '    jugar (registro pp_intro_<id> por campeonato).@NL@'
    '  · VER PRESENTACIÓN: nueva botonera en cada tarjeta del menú para@NL@'
    '    re-ver el vídeo a demanda (opcional, nunca obligatorio) + ?intro=1@NL@'
    '    en la URL para pruebas del dueño.@NL@'
    '  · MENÚ PRIORITARIO: si sacas el menú (o el prompt del Hall) durante@NL@'
    '    la intro, el menú MANDA — sus clics funcionan aunque el vídeo siga@NL@'
    '    en pantalla (antes la intro se comía los clics: menú decorado).@NL@'
    '  · HAZ-PUNTERO en la intro: al apuntar con la pala al panel sale el@NL@'
    '    MISMO haz de luz del mapa del camino (azul; DORADO sobre el botón@NL@'
    '    JUGAR): siempre se ve a qué se apunta y se apaga al dejar de@NL@'
    '    apuntar (igual de discreto que en los mapas).@NL@'
    '  · Capa Z nueva (qa_menu_intro_v3631, en vivo): 36 checks — texto@NL@'
    '    fantasma fuera, persistencia 1ª vez / re-ver, menú ANTES que@NL@'
    '    intro en onSelectStart, botón en los rects del menú, haz vivo y@NL@'
    '    apagado, y catálogo íntegro.@NL@'
    '  · Conserva TODO: el HALL SIN PALA NI BOLA (FASE 32), la SALA DEL@NL@'
    '    PARTIDO con su arte por defecto y el MEJOR DE 3 (FASE 31), el@NL@'
    '    SALÓN DEL ARTISTA (FASE 30), la coronación épica y la RUTA LEYENDA@NL@'
    '    del Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE@NL@'
    '    IMPULSO, la CCD SDF de contacto, el saque VR realista, PRO@NL@'
    '    CIRCUITO, intro oficial, física viva, palas con carácter, CRAZY TV@NL@'
    '    en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.30-SDK6", "V3.6.31-SDK6"),
    ("3.6.30-SDK6", "3.6.31-SDK6"),
    ("v3630-sdk6", "v3631-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 33 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.30"' in txt:
                txt = txt.replace('grep -c "3.6.30"', 'grep -c "3.6.31"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.31")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.30" in txt:
                txt = txt.replace("menciones 3.6.30", "menciones 3.6.31")
                txt = txt.replace("n3630 = int", "n3631 = int").replace("{n3630}", "{n3631}").replace("if n3630 < 4", "if n3631 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.31")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.31-SDK6") == 1:
            txt = txt.replace("frente a V3.6.31-SDK6", "frente a V3.6.30-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.30)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3631 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.30-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n30 = bz.count("3.6.30-SDK6")
    if n30 != 1 or "frente a V3.6.30-SDK6" not in bz:
        print(f"aviso: 3.6.30-SDK6 queda ×{n30} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3630-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.31-SDK6" not in bz or "FASE 33" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    for guard, esperado in [("SDK_VERSION", "1.5.4"), ("version\": 56", "56")]:
        if guard == "SDK_VERSION" and "1.5.4" not in bz:
            print("aviso: guard del SDK 1.5.4 no aparece (revisar)")
        if guard == "version\": 56" and 'version": 56' not in bz:
            print("aviso: guard del manifest oeste v56 no aparece (revisar)")
    print("OK · release-v3631 generado")


if __name__ == "__main__":
    main()
