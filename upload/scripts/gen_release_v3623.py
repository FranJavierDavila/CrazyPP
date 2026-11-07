#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 29 · GENERADOR DEL DIRECTORIO DE RELEASE v3623
======================================================================
Crea scripts/release-v3623/ a partir de scripts/release-v3622/ con:
  · reemplazos de versión (3.6.22-SDK6 → 3.6.23-SDK6 · v3622-sdk6 → v3623-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 25 — EL TREN SE OYE
    SIEMPRE), sustituido por MARCADORES (método de la ronda 26).
  · guards del build_zip actualizados: SDK v1.5.1 (ignoraMute) y manifest
    del oeste v53.
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3623 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3622"
DEST = RAIZ / "scripts" / "release-v3623"

# ── marcadores del bloque de notas del VERSION.txt (texto FUENTE real) ──
BLOQUE_INI = "    'Rama    : main · SDK6 (FASE 24"
BLOQUE_FIN = "    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"

# bloque NUEVO en texto fuente de build_zip.py (los \\n literales son los
# saltos del VERSION.txt generado; los saltos reales separan literales).
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 25 — EL TREN SE OYE SIEMPRE)\\n\\n'
    'Novedades de esta versión (frente a V3.6.22-SDK6):\\n'
    '  · FASE 25 (ronda 29, informe del dueño: «no se escuchan los\\n'
    '    sonidos del tren, ni las llegadas, ni los túneles»): CAUSA\\n'
    '    PROBADA con QA runtime de 24 checks sobre el juego real — la\\n'
    '    cadena fetch→decode→contexto estaba SANA; el silencio era el\\n'
    '    GATE arcMute/_arcDucked del SDK (el silencio de la MÚSICA del\\n'
    '    arcade aplicado a pistas que NO son música; los sintéticos de\\n'
    '    la casa nunca consultaron ese interruptor y por eso sí se\\n'
    '    oían).\\n'
    '  · champ_sdk v1.5.1 «ignoraMute»: rodadura, galopes y SFX del\\n'
    '    vagón suenan SIEMPRE; el mute del arcade sigue gobernando la\\n'
    '    MÚSICA (BSO del saloon y del vagón). El primer play() de una\\n'
    '    pista ya no muere en silencio (play pendiente que se dispara\\n'
    '    al decodificar).\\n'
    '  · AUTOREPARACIÓN por frame de los 3 bucles del vagón (rodadura\\n'
    '    y galopes): un contexto renacido en un re-bind de VR ya no\\n'
    '    deja el trayecto mudo — el sonido vuelve al instante.\\n'
    '  · FUERA el «¡YIHAAA!» sintético de las entradas del forajido y\\n'
    '    de los indios (petición del dueño): los jinetes entran\\n'
    '    galopando con su caballos.mp3 desfasado y paneado.\\n'
    '  · Capa V ampliada a 33 checks (qa_tren_audio_v3623) + nuevo QA\\n'
    '    RUNTIME del audio (qa_tren_audio_rt_v3623: ctx, fetch, decode\\n'
    '    y AUDIBILIDAD medida con analizador, en dev y producción).\\n'
    '  · Conserva TODO: la coronación épica y la RUTA LEYENDA del\\n'
    '    Oeste, el ESCUDO DE PALA, el REACTOR DE IMPULSO, la CCD\\n'
    '    SDF de contacto, el saque VR realista, el hall del\\n'
    '    anfitrión, PRO CIRCUITO, intro oficial, física viva, palas\\n'
    '    con carácter, CRAZY TV en directo y los 5 campeonatos.\\n\\n'"""

GLOBALES = [
    ("V3.6.22-SDK6", "V3.6.23-SDK6"),
    ("3.6.22-SDK6", "3.6.23-SDK6"),
    ("v3622-sdk6", "v3623-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 25 insertadas (marcadores, {j - i} → {len(BLOQUE_NUEVO)} B)")
            # guard del COMPLETO: el grep del hub empaquetado debe apuntar
            # a la versión NUEVA
            if 'grep -c "3.6.22"' in txt:
                txt = txt.replace('grep -c "3.6.22"', 'grep -c "3.6.23"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.23")
            # continuidad del print de menciones (patrón heredado)
            if "menciones 3.6.22" in txt:
                txt = txt.replace("menciones 3.6.22", "menciones 3.6.23")
                txt = txt.replace("n3622 = int", "n3623 = int").replace("{n3622}", "{n3623}").replace("if n3622 < 4", "if n3623 < 4")
                print("  ✓ build_zip.py: print de menciones actualizado a 3.6.23")
            # guard del SDK: la versión viva ahora es 1.5.1 (FASE 9 · ignoraMute)
            if "const SDK_VERSION = '1.5.0'" in txt:
                txt = txt.replace("const SDK_VERSION = '1.5.0'",
                                  "const SDK_VERSION = '1.5.1'")
                print("  ✓ build_zip.py: guard del SDK actualizado a 1.5.1")
            # guard de adopción: el manifest de oeste sube a v53 (note_v2143)
            if "'oeste': (52," in txt:
                txt = txt.replace("'oeste': (52,", "'oeste': (53,")
                txt = txt.replace("verificada: oeste v52", "verificada: oeste v53")
                txt = txt.replace("oeste v52 (BSO+vagón)", "oeste v53 (BSO+vagón)")
                txt = txt.replace("PowerSign SDK5 verificada: oeste v52", "PowerSign SDK5 verificada: oeste v53")
                print("  ✓ build_zip.py: guard de adopción del manifest de oeste → v53")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.23-SDK6") == 1:
            txt = txt.replace("frente a V3.6.23-SDK6", "frente a V3.6.22-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.22)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3623 no debe quedar con sellos viejos
    # (se admite EXACTAMENTE 1 «3.6.22-SDK6»: la cita «frente a» de las notas)
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    n22 = bz.count("3.6.22-SDK6")
    if n22 != 1 or "frente a V3.6.22-SDK6" not in bz:
        print(f"aviso: 3.6.22-SDK6 queda ×{n22} en build_zip.py (debe ser sólo «frente a»)")
    for sello_viejo in ("v3622-sdk6",):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.23-SDK6" not in bz or "FASE 25" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    if "const SDK_VERSION = '1.5.1'" not in bz:
        print("FALLO: build_zip.py sin el guard del SDK 1.5.1")
        sys.exit(1)
    if "'oeste': (53," not in bz:
        print("FALLO: build_zip.py sin el guard del manifest v53")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    # el bloque nuevo debe citar el QA nuevo de esta ronda
    if "qa_tren_audio_v3623" not in bz:
        print("FALLO: el bloque nuevo no cita qa_tren_audio_v3623")
        sys.exit(1)
    # el bloque nuevo debe ser sintaxis Python válida
    compile(bz, "build_zip.py", "exec")
    print("  ✓ build_zip.py sintaxis OK tras el bloque nuevo")
    print("· release-v3623 listo → python3 scripts/release-v3623/build_zip.py")


if __name__ == "__main__":
    main()
