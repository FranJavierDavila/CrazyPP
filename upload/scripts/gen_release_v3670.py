#!/usr/bin/env python3
"""gen_release_v3670 — hereda scripts/release-v3669 → scripts/release-v3670
e inserta las NOTAS de la FASE 72 «EL NARRADOR HONESTO» en build_zip.py.

Idempotente: si release-v3670 ya existe, se regenera desde cero.
"""
import re
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3669"
DEST = RAIZ / "scripts" / "release-v3670"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 71 (r77) que sale entero
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 71 — LA RAQUETA MODO FANTASMA: la nota\\n'")
BLOQUE_VIEJO_FIN = ("    '    sin raqueta jamás; fuera de la academia, CERO cambios.\\n\\n'")

# Bloque nuevo FASE 72 (r78)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 72 — EL NARRADOR HONESTO: la nota del\\n'
    'dueño sobre el tutorial — «En el audio del tutorial en el apartado\\n'
    'de modos se dice que cada 20 toques ganamos un superpoder, pero\\n'
    'esto no es para los partidos normales ya que los superpoderes solo\\n'
    'aparecen en los campeonatos. Cuando describe los modos llega un\\n'
    'momento que dice "…y más…" cuando lo que debería es decir\\n'
    'Campeonatos»)\\n\\n'
    'Novedades de esta versión (frente a V3.6.69-SDK6):\\n\\n'
    '  · LA VOZ DEL PASO 7 (LOS MODOS) CUENTA LA VERDAD: adiós al «…y\\n'
    '    más…» — ahora dice «partido, supervivencia, multijugador y\\n'
    '    CAMPEONATOS»; el partido normal ya NO promete superpoderes\\n'
    '    (esa carga de poder era falsa fuera de los campeonatos).\\n\\n'
    '  · CAMPEONATOS EXPLICADOS COMO MERECE (dictado del dueño): el modo\\n'
    '    tipo ARCADE con poderes en juego para el RIVAL y para el jugador\\n'
    '    al superar los 20 toques seguidos; cada superpoder se ve con su\\n'
    '    icono identificativo sobre el MANGO de la pala, se lanza\\n'
    '    apretando el GATILLO y dura 10 segundos. ¡Lucha con el rival y\\n'
    '    véncelo! (átomo nuevo tutv9c · mismo narrador Piper de siempre).\\n\\n'
    '  · PIZARRA SINCRONIZADA: la caja PODERES de los modos ahora dice\\n'
    '    «SOLO CAMPEONATOS · 20 toques seguidos cargan · gatillo lanza ·\\n'
    '    10 s» (ES+EN) — la voz y la pizarra cuentan la misma verdad.\\n'
    '    Regla del juego intacta (c12): los poderes SOLO viven en los\\n'
    '    campeonatos (megaEnabled = champs.active).\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3669 → v3670 / V3.6.69 → V3.6.70
    txt = txt.replace("V3.6.69-SDK6", "V3.6.70-SDK6")
    txt = txt.replace("3.6.69-SDK6", "3.6.70-SDK6")   # guards contra game_src
    txt = txt.replace("v3669-sdk6", "v3670-sdk6")
    txt = txt.replace("release-v3669", "release-v3670")
    txt = txt.replace("staging-v3669", "staging-v3670")
    txt = txt.replace('grep -c "3.6.69"', 'grep -c "3.6.70"')
    txt = txt.replace("menciones 3.6.69", "menciones 3.6.70")
    txt = txt.replace("no es el v3669", "no es el v3670")
    txt = txt.replace("n3669 = int", "n3670 = int")
    txt = txt.replace("if n3669 < 4:", "if n3670 < 4:")

    # 2 · notas: bloque FASE 71 → bloque FASE 72
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 71 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.70-SDK6'" in txt, "guard VERSION"
    assert "V3.6.70-SDK6" in txt, "badge"
    assert "FASE 72" in txt, "notas FASE 72"
    assert "FASE 71" not in txt, "quedan notas FASE 71"
    print("✓ release-v3670 creada (notas FASE 72, guards V3.6.70-SDK6)")


if __name__ == "__main__":
    main()
