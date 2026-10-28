#!/usr/bin/env python3
"""gen_release_v3678 — hereda scripts/release-v3677 → scripts/release-v3678
e inserta las NOTAS de la FASE 80 «ESCENARIO REAL DE HALLOWEEN + 4 SUPERPODERES»
en build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3678 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3677"
DEST = RAIZ / "scripts" / "release-v3678"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 79 — HALLOWEEN + TALLER UGC: «Perfecto." + NL + "'"
BLOQUE_VIEJO_FIN = ("    'poderes, CCD, CRAZY TV y el Hall Of Fame)." + NL + "'"
                    + chr(10) + "    '" + NL + "'")

# líneas de texto PLANO de las notas FASE 80 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 80 — ESCENARIO REAL DE HALLOWEEN + 4",
    "    'SUPERPODERES DEL ZOMBI: «Lo siguiente será completar el escenario del",
    "    'campeonato de Halloween» — las 6 paredes de la estancia del artista",
    "    'sustituyen al cementerio procedimental, entran los 4 troqueles, la",
    "    'mesa viste la LOSA de piedra y el zombi lanza sus 4 superpoderes.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.77-SDK6):",
    "    '",
    "    '  · SALA REAL DE LA ESTANCIA (paredes.zip del artista → sala_*.jpg):",
    "    '    cementerio nocturno con luna, niebla, iglesia y catedral gótica en",
    "    '    las 6 superficies (frontal, laterales, trasera, suelo de adoquines",
    "    '    y cielo en el techo). El contrato de siempre: cero código, el",
    "    '    núcleo viste los 6 planos y el telón espera las 6 texturas.",
    "    '",
    "    '  · LOS 4 TROQUELES DEL ARTISTA (troqueles.zip → decor_*.png): araña",
    "    '    calavera, escena de calabaza, lápida RIP y ojos rojos, montados en",
    "    '    sus caballetes por el sistema decor (pivote en la base, sombra con",
    "    '    forma real, tambaleo + knock cuando la bola o la pala los roza).",
    "    '",
    "    '  · MESA DE LOSA (mesa.jpg del artista → losa.jpg): la mesa viste la",
    "    '    piedra agrietada del cementerio como la mesa de madera del Oeste",
    "    '    (_losaOn/_losaOff en startChamp/leave; marco y patas a piedra",
    "    '    oscura; restauración byte-idéntica al salir del campeonato).",
    "    '",
    "    '  · LOS 4 SUPERPODERES REALES DEL ZOMBI (10 s, anuncio con el CARTEL",
    "    '    SuperPower del dueño + medallón circular abajo-derecha diseñado",
    "    '    por la casa + congelación momentánea v2.40 de la partida):",
    "    '    MANO DE ZOMBI — de montículos que brotan en la mesa sale una de",
    "    '    las 3 manos del artista (rápida y frenándose al final para dar",
    "    '    el susto, 2 s de vaivén siniestro y de vuelta a la tierra);",
    "    '    estorban y frenan la bola: si la tocan, la bola se para y se",
    "    '    cae y la mano revienta en TROCITOS. PLAGA DE MOSCAS — enjambre",
    "    '    revoloteando en la cara del jugador (15 moscas, como el confeti",
    "    '    del Clown) que se puede ESPANTAR CON LA PALA. CALABAZA — la bola",
    "    '    se vuelve la calabaza.glb del dueño (×3 del tamaño, gravedad",
    "    '    ×2,1) y tras CADA BOTE en la mesa sale en CUALQUIER dirección.",
    "    '    GELATINA ASQUEROSA — 4 manchas del dueño sobre la mesa: la bola",
    "    '    que las pisa se vuelve VERDE FOSFORITO, pesa ×2,6 con frenada",
    "    '    constante (necesita más fuerza para avanzar) y suelta un",
    "    '    humillo verde que se desvanece.",
    "    '",
    "    '  · MOTOR: precarga única de manos/mosca/gelatina/calabaza.glb (caché",
    "    '    r86 — las rejugadas no re-descargan), guard anti-disparos",
    "    '    fantasma en _lanzar, retirados los 2 poderes provisionales (Niebla",
    "    '    de tumba y Orbe espectral) y sus iconos power_0/1.",
    "    '",
    "    'Hereda de V3.6.77 (FASE 79: el zombi del artista con su mapa y sus",
    "    'normas, el Reto Diario escalonado y EL TALLER UGC; 5 campeonatos, 5",
    "    'poderes, CCD, CRAZY TV y el Hall Of Fame).",
    "    '",
]


def _construir_bloque():
    partes = []
    for ln in _NOTAS:
        partes.append(ln + NL + "'")
    return chr(10).join(partes) + chr(10)


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3677 → v3678 / V3.6.77 → V3.6.78
    txt = txt.replace("V3.6.77-SDK6", "V3.6.78-SDK6")
    txt = txt.replace("3.6.77-SDK6", "3.6.78-SDK6")   # guards contra game_src
    txt = txt.replace("v3677-sdk6", "v3678-sdk6")
    txt = txt.replace("release-v3677", "release-v3678")
    txt = txt.replace("staging-v3677", "staging-v3678")
    txt = txt.replace('grep -c "3.6.77"', 'grep -c "3.6.78"')
    txt = txt.replace("menciones 3.6.77", "menciones 3.6.78")
    txt = txt.replace("no es el v3677", "no es el v3678")
    txt = txt.replace("n3677 = int", "n3678 = int")
    txt = txt.replace("{n3677}", "{n3678}")
    txt = txt.replace("if n3677 < 4:", "if n3678 < 4:")

    # 2 · notas: bloque FASE 79 → bloque FASE 80
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 79 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + _construir_bloque() + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.78-SDK6'" in txt, "guard VERSION"
    assert "V3.6.78-SDK6" in txt, "badge"
    assert "FASE 80" in txt, "notas FASE 80"
    assert "FASE 79 —" not in txt, "quedan notas FASE 79"
    print("✓ release-v3678 creada (notas FASE 80, guards V3.6.78-SDK6)")


if __name__ == "__main__":
    main()
