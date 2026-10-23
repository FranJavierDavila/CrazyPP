#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 62 · GENERADOR DEL DIRECTORIO DE RELEASE v3654
======================================================================
Crea scripts/release-v3654/ a partir de scripts/release-v3653/ con:
  · reemplazos de versión (3.6.53-SDK6 → 3.6.54-SDK6 · v3653-sdk6 → v3654-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 56 — SONIDO REAL por
    síntesis modal, HÁPTICA ESCALADA por impacto y CÁMARA LENTA — las tres
    features aprobadas por el dueño para «un toque profesional»),
    sustituido por MARCADORES, método ronda 26/59/60/61.
  · guards del build_zip conservados: SDK v1.5.4, oeste v56, locura v27,
    magia v33 y valle_neon v5 (los r60 vienen heredados del origen).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7).
Idempotente: si release-v3654 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3653"
DEST = RAIZ / "scripts" / "release-v3654"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del build_zip r61 (texto FUENTE real) ──
BLOQUE_INI = ("    'Rama    : main · SDK6 (FASE 55 — ESTELA DE PODERES, RIVAL QUE SE"
              + BS_N + "'")
BLOQUE_FIN = "    '    CRAZY TV y los 5 campeonatos)." + BS_N + BS_N + "'"

BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 56 — SONIDO REAL, HÁPTICA QUE MIDE y@NL@'
    'EL MOMENTO CINE — las tres features del toque profesional aprobadas@NL@'
    'por el dueño)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.53-SDK6):@NL@@NL@'
    '  · SONIDO REAL: la bola ya NO suena a bleeps — cinco muestras por@NL@'
    '    SÍNTESIS MODAL FÍSICA (los modos de la cáscara hueca de 40 mm +@NL@'
    '    transitorio de contacto + cuerpo de cada superficie) van@NL@'
    '    INCRUSTADAS en el juego (WAV 44,1 kHz · 16-bit, el perfil probado@NL@'
    '    del casco) y suenan con el TONO MAPEADO A LA VELOCIDAD del@NL@'
    '    impacto (contacto más rígido = tono más alto — física real) con@NL@'
    '    jitter ±1,5% anti-ametralladora. Estreno del CANTO: el bote en el@NL@'
    '    borde de la mesa suena a su «ping» METÁLICO con cola. Si una@NL@'
    '    muestra no llega, la síntesis de siempre responde: el audio NUNCA@NL@'
    '    rompe el bucle del juego.@NL@@NL@'
    '  · HÁPTICA ESCALADA POR IMPACTO: la vibración del mando ya no es un@NL@'
    '    pulso fijo — intensidad Y duración crecen con la velocidad real@NL@'
    '    del golpe (una dejada es un tick corto y suave de 34 ms; un smash@NL@'
    '    es un zumbido seco a tope durante 96 ms), también en el SAQUE. El@NL@'
    '    refuerzo expresamente pedido para ARKANOID (v2.44) se conserva.@NL@@NL@'
    '  · CÁMARA LENTA — EL MOMENTO CINE: la repetición del mejor@NL@'
    '    intercambio corre a la MITAD del tiempo real con su pastilla@NL@'
    '    ámbar en el cartel, y la BOLA DE PARTIDO se dilata en vivo (la@NL@'
    '    física cae a 0,34× y regresa suave en ~1,15 s) justo al decidirse@NL@'
    '    el partido: el último vuelo se contempla antes de la fanfarria.@NL@'
    '    Sólo local — online la bola la conduce el stream del rival.@NL@@NL@'
    '  · VERIFICACIÓN: capa AW nueva (qa_r62_v3654, 48 checks con MECÁNICA@NL@'
    '    REAL headless: las 5 muestras decodificadas con duraciones de@NL@'
    '    diseño, tono por impacto en banda, jitter, fallback sintético,@NL@'
    '    despacho canto/llano/red, háptica dejada<smash con ARKANOID@NL@'
    '    intacto, dilatación en vivo con regreso suave, repetición a la@NL@'
    '    mitad y pastilla ámbar pintada).@NL@@NL@'
    '  · Conserva TODO lo anterior (LA ACADEMIA, los tres arreglos r60, la@NL@'
    '    estela de poderes, el rival adaptativo y la repetición r61, 5@NL@'
    '    poderes, norma de 20 toques, voz del selector, expresiones, bomba@NL@'
    '    y eléctrico, passthrough en caliente, SALÓN, PRO CIRCUITO, CCD,@NL@'
    '    CRAZY TV y los 5 campeonatos).@NL@@NL@'
"""

GLOBALES = [
    ("V3.6.53-SDK6", "V3.6.54-SDK6"),
    ("3.6.53-SDK6", "3.6.54-SDK6"),
    ("v3653-sdk6", "v3654-sdk6"),
    ("3.6.53", "3.6.54"),   # guard del hub empaquetado (versión desnuda)
]

RESTAURA = [
    ("frente a V3.6.54-SDK6", "frente a V3.6.53-SDK6"),
    ("tras probar V3.6.54", "tras probar V3.6.53"),
    ("tras V3.6.54", "tras V3.6.53"),
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
            print(f"  ✓ {f.name}: notas FASE 56 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
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

    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    if "v369-sdk5" not in bz or "V3.6.54-SDK6" not in bz:
        print("FALLO: guard de identidad roto en build_zip.py")
        sys.exit(1)
    print("· guard v369-sdk5 intacto · V3.6.54-SDK6 presente")
    print("GEN_RELEASE_V3654 COMPLETO")


if __name__ == "__main__":
    main()
