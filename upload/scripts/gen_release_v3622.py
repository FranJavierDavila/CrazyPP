#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 28 · GENERADOR DEL DIRECTORIO DE RELEASE v3622
======================================================================
Crea scripts/release-v3622/ a partir de scripts/release-v3621/ con:
  · reemplazos de versión (3.6.21-SDK6 → 3.6.22-SDK6 · v3621-sdk6 → v3622-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 24 — EL TREN SUENA Y EL
    ORO SE VE), sustituido por MARCADORES (método de la ronda 26).
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3622 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3621"
DEST = RAIZ / "scripts" / "release-v3622"

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 23"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"

# bloque NUEVO en texto fuente de build_zip.py (los \\n literales son los
# saltos del VERSION.txt generado; los saltos reales separan literales).
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 24 — EL TREN SUENA Y EL ORO SE VE)\\n\\n'
    'Novedades de esta versión (frente a V3.6.21-SDK6):\\n'
    '  · FASE 24 (ronda 28, informe del dueño en el casco, etapa 4 del\\n'
    '    vagón del Oeste): CUATRO PISTAS DE SONIDO del artista.\\n'
    '    Tren_Llegada.mp3 al llegar a la estación · vias.mp3 en bucle\\n'
    '    mientras el tren marcha · Tunel.mp3 al entrar en el túnel ·\\n'
    '    caballos.mp3 GALOPE POR INSTANCIA (cada jinete desfasado y\\n'
    '    con paneo de su lado, se desvanece con la distancia y calla\\n'
    '    brusco al abatirlo).\\n'
    '  · Nuevo createBucle() en champ_sdk v1.5.0: bucles con control\\n'
    '    por instancia (desfase, volumen vivo y parada seca) — decode\\n'
    '    en forma promesa, mute del arcade respetado, cero setTimeout.\\n'
    '  · CAJONES DEL ORO A LAS VENTANAS: x 1,35→2,55 — los lingotes\\n'
    '    caen debajo mismo de las ventanas y se ven de sobra (antes\\n'
    '    quedaban muy cerca de la mesa).\\n'
    '  · FIX DE LA INTERPENETRACIÓN DE LINGOTES: la barra del GLB nace\\n'
    '    con el eje largo EN Z y la rejilla la solapaba 7,5 cm fila\\n'
    '    contra fila; el prototipo gira 90° y la rejilla cuadra entera\\n'
    '    (holguras +3,7/+6,1 mm verificadas numéricamente).\\n'
    '  · Verificación estática permanente: capa V nueva\\n'
    '    (qa_tren_audio_v3622) con 25 checks de assets, cableado,\\n'
    '    regla SDK y rejilla sin solape.\\n'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del\\n'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD\\n'
    '    SDF de contacto, el saque VR realista, el hall del\\n'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"""

GLOBALES = [
    ("V3.6.21-SDK6", "V3.6.22-SDK6"),
    ("3.6.21-SDK6", "3.6.22-SDK6"),
    ("v3621-sdk6", "v3622-sdk6"),
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
            txt = txt[:i] + BLOQUE_NUEVO + txt[j:]
            print(f"  ✓ {f.name}: notas FASE 24 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.21"' in txt:
                txt = txt.replace('grep -c "3.6.21"', 'grep -c "3.6.22"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.22")
            # continuidad del print de menciones (patrón heredado de la ronda 27)
            if "menciones 3.6.21" in txt:
                txt = txt.replace("menciones 3.6.21", "menciones 3.6.22")
                txt = txt.replace("n3621 = int", "n3622 = int").replace("{n3621}", "{n3622}").replace("if n3621 < 4", "if n3622 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.22")
            # guard del SDK: la versión viva ahora es 1.5.0 (FASE 8 · createBucle)
            # y el SDK debe llevar el motor nuevo (dura desde el build, no sólo en QA)
            if "const SDK_VERSION = '1.4.0'" in txt:
                txt = txt.replace("const SDK_VERSION = '1.4.0'", "const SDK_VERSION = '1.5.0'")
                txt = txt.replace(
                    "for tk in (\"const SDK_VERSION = '1.5.0'\", 'export function createSfx',",
                    "for tk in (\"const SDK_VERSION = '1.5.0'\", 'export function createBucle', 'export function createSfx',")
                print("  ✓ build_zip.py: guard del SDK actualizado a 1.5.0 + createBucle")
            # guard de adopción: el manifest de oeste sube a v52 (nota_v2142)
            if "'oeste': (51," in txt:
                txt = txt.replace("'oeste': (51,", "'oeste': (52,")
                txt = txt.replace("verificada: oeste v51", "verificada: oeste v52")
                txt = txt.replace("oeste v51 (BSO+vagón)", "oeste v52 (BSO+vagón)")
                txt = txt.replace("PowerSign SDK5 verificada: oeste v51", "PowerSign SDK5 verificada: oeste v52")
                print("  ✓ build_zip.py: guard de adopción del manifest de oeste → v52")
            # el import de oeste estrena createBucle + assetURL (FASE 8) —
            # SÓLO la línea de oeste: el import de magia NO cambia esta ronda
            txt = txt.replace(
                "'oeste': (52, (\"import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'\"",
                "'oeste': (52, (\"import { createSfx, createMusic, createBucle, createPowerSign, congela, getCore, assetURL } from '../sdk/champ_sdk.js'\"")
            if "createBucle, createPowerSign, congela, getCore, assetURL } from '../sdk/champ_sdk.js'\"" in txt:
                print("  ✓ build_zip.py: guard del import de oeste actualizado (createBucle + assetURL)")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.22-SDK6") == 1:
            txt = txt.replace("frente a V3.6.22-SDK6", "frente a V3.6.21-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.21)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3622 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.21-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n21 = bz.count("3.6.21-SDK6")
    if n21 != 1 or "frente a V3.6.21-SDK6" not in bz:
        print(f"aviso: 3.6.21-SDK6 queda ×{n21} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3621-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.22-SDK6" not in bz or "FASE 24" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_tren_audio_v3622" not in bz:
        print("FALLO: el bloque nuevo no cita qa_tren_audio_v3622")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3622 listo → python3 scripts/release-v3622/build_zip.py")


if __name__ == "__main__":
    main()
