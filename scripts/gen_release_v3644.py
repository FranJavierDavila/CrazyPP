#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 52 · GENERADOR DEL DIRECTORIO DE RELEASE v3644
======================================================================
Crea scripts/release-v3644/ a partir de scripts/release-v3643/ con:
  · reemplazos de versión (3.6.42-SDK6 → 3.6.43-SDK6 · v3642-sdk6 → v3643-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 45 — los superpoderes SE
    VEN y SE OYEN, sustituido por MARCADORES, método ronda 26)
  · guards del build_zip conservados: SDK v1.5.4, manifest del oeste v56 y
    manifest de la locura v26 (la mecánica vive en el núcleo).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3644 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3643"
DEST = RAIZ / "scripts" / "release-v3644"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 45"
BLOQUE_FIN = ("los 5 campeonatos." + BS_N + BS_N + "'")

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 46 — SEÑAL CONTINUA Y LA BOMBA —@NL@'
    'informe del dueño tras probar V3.6.43 en el Quest 3, corregido pieza a@NL@'
    'pieza)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.43-SDK6):@NL@'
    '  · SÚPER IMÁN SE VIVE («no hace nada, no se ve efecto ni se nota nada@NL@'
    '    sobre la pala»): CAMPO CONTINUO en el punto dulce — disco cian con@NL@'
    '    12 partículas orbitando mientras dura el poder (no solo cuando la@NL@'
    '    bola entra) — y FIX CRÍTICO: las flechas de la ronda 51 estaban@NL@'
    '    construidas pero NADIE LAS LLAMABA (los conos nacían ocultos a@NL@'
    '    y=-100 para siempre); ahora updateMega las ancla SIEMPRE. Flechas@NL@'
    '    ×1,8 y sin exigir cruce; radio 0,95 m, acel 6,5 m/s², Δv 0,80 y@NL@'
    '    RESCATE de bolas escapadas 7,5 m/s² / 1,05 m/s — la bola cruzada@NL@'
    '    CURVA hacia la pala a la vista.@NL@'
    '  · SÚPER EFECTO SE VE («en el Super efecto tampoco noto nada»): halo@NL@'
    '    rojo de la bola marcada 0,142→0,21 m con pulso amplio + ESTELA ROJA@NL@'
    '    NUEVA (línea de 14 puntos que dibuja la trayectoria curvada del@NL@'
    '    Magnus) + anillo de bote más grande (0,09-0,115 m) y más lento@NL@'
    '    (0,55 s) + barrido sonoro del bote al doble de volumen.@NL@'
    '  · MARCA DEL BOTE EXACTA («la marca del bote va desfasada»): la marca@NL@'
    '    se clavaba al contacto del SUBPASO físico y la bola RENDERIZADA va@NL@'
    '    un poco más adelante (los subpasos restantes del frame) — a rally@NL@'
    '    la diferencia se VE; ahora la marca (flashMarker y anillo) se clava@NL@'
    '    a la bola visual, posición EXACTA bajo la bola del frame.@NL@'
    '  · AVISO DE FIN OÍDO Y SENTIDO («el sonido de alerta de que se está@NL@'
    '    agotando no suena o no se percibe»): los blips de 0,07-0,09 s a@NL@'
    '    gain 0,18 se perdían en el casco — ahora gain 0,42, duración@NL@'
    '    0,15/0,2 s, DOBLE BLIP en los dos primeros ticks y HÁPTICA@NL@'
    '    creciente (el aviso también se SIENTE en el mango). Y el canto de@NL@'
    '    la pala de los cuatro poderes sube de opacidad 0,55 a 0,82 con@NL@'
    '    pulso vivo — SE VE de verdad sobre la hoja.@NL@'
    '  · EL LADRILLO BOMBA del ARKANOID 2 (etapa 4 del campeonato de La@NL@'
    '    Locura — la spec literal del dueño): un ladrillo NEGRO con el@NL@'
    '    dibujo de una bomba (bomba.webp del estilo del reloj) aparece@NL@'
    '    ALEATORIAMENTE y AL MENOS 1 VEZ POR PARTIDA sustituyendo a un azul;@NL@'
    '    permanece 4 segundos y SALTA a otro azul si está presente — si no,@NL@'
    '    desaparece hasta que aparezca otro azul; una vez CONSUMIDO (bola o@NL@'
    '    láser) no vuelve en toda la partida y SE REINICIA CON CADA PARTIDA.@NL@'
    '    Al destruirlo DETONA ESTREPITOSAMENTE: arrasa todos los ladrillos@NL@'
    '    en radio de 2 filas × 2 columnas (rojos Y azules), escombros@NL@'
    '    negros, flash doble, BOOM grave con sub-tono, háptica fuerte y@NL@'
    '    cartel «¡BOOM! ¡DETONACIÓN!». La etapa Arkanoid tiene así DOS@NL@'
    '    ayudas aseguradas: el reloj (+1 min) y la bomba (el destrozo).@NL@'
    '  · Capa AM nueva (qa_bomba_v3644): agujas del núcleo y del módulo +@NL@'
    '    PIL del bomba.webp + mecánica headless REAL del ArcadeController@NL@'
    '    (aparición garantizada, salto a 4 s con restauración del azul,@NL@'
    '    espera sin azules, detonación radio 2×2 exacta — 25 muertos/29@NL@'
    '    intactos, no-vuelta, núcleo: campo/estela/flechas precalentados y@NL@'
    '    blips 988/1319 a gain 0,42 espiados). AF y AL re-ancladas a la@NL@'
    '    spec v3.6.44 (imán 0,95/0,26/6,5/0,80 + rescate 7,5/1,05 · halo@NL@'
    '    0,21 · blips 988/1319 · versión servida).@NL@'
    '  · Conserva TODO: la matriz de poderes (mega · efecto · imán ·@NL@'
    '    portal) con ciclo ⟷ sin envolver, el PODER ACTIVO SE VE EN LA@NL@'
    '    PALA (anillo de tiempo, FASE 42), la PARTIDA NUEVA = PALA LIMPIA@NL@'
    '    (hook del árbitro, FASE 41), la INMEDIATEZ del gatillo, el portal@NL@'
    '    EXPLÍCITO de 3 fases con la IA penalizada en % (r50) y sus 3@NL@'
    '    golpes garantizados (r51), el passthrough EN CALIENTE (r51), el@NL@'
    '    PRECALIENTE anti-lag al empezar la partida (r50), las voces@NL@'
    '    nativas y los iconos recortados, el menú de campeonatos v3.6.31,@NL@'
    '    el HALL OF FAME (FASE 29), el SALÓN DEL ARTISTA (FASE 30), la SALA@NL@'
    '    DEL PARTIDO y el MEJOR DE 3 (FASE 31), el HALL SIN PALA NI BOLA@NL@'
    '    (FASE 32), la coronación épica y la RUTA LEYENDA del Oeste, el@NL@'
    '    tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la@NL@'
    '    CCD SDF de contacto, el saque VR realista, PRO CIRCUITO, intro@NL@'
    '    oficial, física viva, palas con carácter, CRAZY TV en directo y@NL@'
    '    los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.43-SDK6", "V3.6.44-SDK6"),
    ("3.6.43-SDK6", "3.6.44-SDK6"),
    ("v3643-sdk6", "v3644-sdk6"),
    ("3.6.43", "3.6.44"),   # guard del hub empaquetado (versión desnuda)
]

# El bloque NUEVO menciona la versión ANTERIOR (frente a / tras probar) y
# los reemplazos globales la manglarían a la nueva — se restaura aquí.
RESTAURA = [
    ("frente a V3.6.44-SDK6", "frente a V3.6.43-SDK6"),
    ("tras probar V3.6.44", "tras probar V3.6.43"),
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
            print(f"  ✓ {f.name}: notas FASE 46 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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
    print("RELEASE v3644 LISTA")


if __name__ == "__main__":
    main()
