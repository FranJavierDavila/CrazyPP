#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 36 · GENERADOR DEL DIRECTORIO DE RELEASE v3628
======================================================================
Crea scripts/release-v3628/ a partir de scripts/release-v3627/ con:
  · reemplazos de versión (3.6.27-SDK6 → 3.6.28-SDK6 · v3627-sdk6 → v3628-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 30 — SALÓN DEL ARTISTA),
    sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.4 y manifest del oeste v56
    se CONSERVAN sin cambios (esta ronda no toca SDK ni módulos).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3628 ya existe, lo regenera desde cero.

NOTA DE ESCAPES: el bloque de notas se escribe con el placeholder @NL@
que se sustituye por backslash+n (los saltos del VERSION.txt generado
dentro de los literales de build_zip.py) — sin ambigüedad de escapes.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3627"
DEST = RAIZ / "scripts" / "release-v3628"
BS_N = chr(92) + "n"          # backslash + n, sin ambigüedad

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 29"
BLOQUE_FIN = "    '    TV en directo y los 5 campeonatos." + BS_N + BS_N + "'"

# bloque NUEVO en texto fuente de build_zip.py (@NL@ → backslash+n)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 30 — EL SALÓN DEL ARTISTA: EL HALL SE@NL@'
    'RECONSTRUYE CON ARTE PROPIO MAPEADO CARA A CARA)@NL@@NL@'
    'Novedades de esta versión (frente a V3.6.27-SDK6):@NL@'
    '  · FASE 30 (ronda 36, petición del dueño: «rediseñar el Hall con las@NL@'
    '    mismas dimensiones que los escenarios de los campeonatos, con las@NL@'
    '    imágenes del artista en las paredes, como solemos montar estas@NL@'
    '    estancias mapeando cada cara»): el Hall del Anfitrión se reconstruye.@NL@'
    '  · DIMENSIONES DE SALA: 6,10 × 7,90 × 2,85 m — EXACTAMENTE las de los@NL@'
    '    escenarios de campeonato (createRoom). Mismo ancho, mismo fondo,@NL@'
    '    misma altura, mismas proporciones de plano por cara.@NL@'
    '  · ARTE MAPEADO CARA A CARA (patrón de las salas, createChampRoom):@NL@'
    '    frente.jpg en la pared del mirada (vitrina de insignias + cartel),@NL@'
    '    fondo.jpg con la puerta luminosa, izquierda.jpg con el ventanal@NL@'
    '    panorámico, derecha.jpg con las insignias hexagonales, suelo.jpg@NL@'
    '    con el emblema elíptico de la casa y techo.jpg con el círculo de@NL@'
    '    luz — seis JPG en assets/hall/ (2,6 MB) con SRGBColorSpace y@NL@'
    '    anisotropía; carga a prueba de fallos: si una imagen no llega, el@NL@'
    '    plano conserva su color y el juego sigue.@NL@'
    '  · EL TROFEO SIGUE VIVO: la copa torneada nace ahora EN EL CENTRO de@NL@'
    '    la estancia, DE PIE SOBRE EL EMBLEMA del suelo, con su haz de luz@NL@'
    '    que respira, su anillo dorado y su placa — PLATEADO mientras@NL@'
    '    espera al primer campeón, ORO (SALÓN DE CAMPEONES) al coronar.@NL@'
    '  · 7 bolas doradas flotan en vaivén por el salón (updateHallFx sólo@NL@'
    '    con la estancia visible: coste cero en la cancha) y 3 luces@NL@'
    '    propias (2 lavados cálidos + foco del trofeo).@NL@'
    '  · RETIRADO el mobiliario procedural del museo (pintores de pared,@NL@'
    '    zócalos, artesonado, vitrinas 3D): el arte lo pinta ya en las@NL@'
    '    texturas — nada duplicado, nada que tape el cuadro del artista.@NL@'
    '  · Capa W nueva (qa_hall_salon_v3628, en vivo): 41 checks — las 6@NL@'
    '    texturas cargadas con SRGB, dimensiones de sala exactas, las 6@NL@'
    '    caras con su map, trofeo plateado girando, bolas navegando, los 6@NL@'
    '    JPG servidos con peso real y pintores antiguos retirados.@NL@'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del@NL@'
    '    Oeste, el tren 100 % sonoro, el ESCUDO DE PALA, el REACTOR DE@NL@'
    '    IMPULSO, la CCD SDF de contacto, el saque VR realista, PRO@NL@'
    '    CIRCUITO, intro oficial, física viva, palas con carácter, CRAZY@NL@'
    '    TV en directo y los 5 campeonatos.@NL@@NL@'"""

GLOBALES = [
    ("V3.6.27-SDK6", "V3.6.28-SDK6"),
    ("3.6.27-SDK6", "3.6.28-SDK6"),
    ("v3627-sdk6", "v3628-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 30 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.27"' in txt:
                txt = txt.replace('grep -c "3.6.27"', 'grep -c "3.6.28"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.28")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.27" in txt:
                txt = txt.replace("menciones 3.6.27", "menciones 3.6.28")
                txt = txt.replace("n3627 = int", "n3628 = int").replace("{n3627}", "{n3628}").replace("if n3627 < 4", "if n3628 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.28")
            # el SDK (1.5.4) y el manifest del oeste (v56) NO cambian esta
            # ronda: sus guards se conservan tal cual (verificación abajo).
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.28-SDK6") == 1:
            txt = txt.replace("frente a V3.6.28-SDK6", "frente a V3.6.27-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.27)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3628 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.27-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n27 = bz.count("3.6.27-SDK6")
    if n27 != 1 or "frente a V3.6.27-SDK6" not in bz:
        print(f"aviso: 3.6.27-SDK6 queda ×{n27} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3627-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.28-SDK6" not in bz or "FASE 30" not in bz:
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
    if "qa_hall_salon_v3628" not in bz:
        print("FALLO: el bloque nuevo no cita qa_hall_salon_v3628")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3628 listo → python3 scripts/release-v3628/build_zip.py")


if __name__ == "__main__":
    main()
