#!/usr/bin/env python3
"""gen_release_v3680 — hereda scripts/release-v3679 → scripts/release-v3680
e inserta las NOTAS de la FASE 82 «A JUSTO DEL INFORME (HALLOWEEN)» en
build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3680 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3679"
DEST = RAIZ / "scripts" / "release-v3680"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 81 — EL INFORME DEL DUEÑO EN MANO: el" + NL + "'"
BLOQUE_VIEJO_FIN = ("    'campeonatos, CCD, CRAZY TV y el Hall Of Fame)." + NL + "'"
                    + chr(10) + "    '" + NL + "'")

# líneas de texto PLANO de las notas FASE 82 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 82 — A JUSTO DEL INFORME: el mapa SE VE",
    "    'en su pared, el zombi se ancla a la MESA con pose nueva, el cartel",
    "    'intruso desaparece, la mano y las manchas viven DENTRO del tablero,",
    "    'la calabaza pudre y ESTALLA y la sala arranca EN CALMA.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.79-SDK6):",
    "    '",
    "    '  · EL MAPA SE VE Y EL CARTEL INTRUSO, FUERA (informe del dueño: «no",
    "    '    se ve el mapa en la pared izquierda» + «un cartel metido en la",
    "    '    pared izquierda hacia el fondo y no sé qué hace ahí»): el dueño",
    "    '    venía de V3.6.78, donde el mapa flotaba en [-1.05, 1.45, -3.58] —",
    "    '    ESE cartel flotante ERA el mapa sin anclar (r87 ya lo puso en su",
    "    '    pared). Y el CARTEL DE BIENVENIDA se RETIRA de Halloween",
    "    '    (manifest cartel.oculto): la etapa la pinta el HUD y el único",
    "    '    cartel de la sala es el de superpoder.",
    "    '",
    "    '  · ZOMBI A LA MESA Y MÁS A LA DERECHA (informe: «debe aparecer en",
    "    '    relación a la mesa algo más a la derecha… se referenciaban a la",
    "    '    mesa»): anclaje a la MESA — z = mesa − 1,70 (la convención que",
    "    '    ya daba menos problemas) y x = CANTO derecho de la mesa + 0,69.",
    "    '    Nada de x absolutos: si la mesa se mueve, el zombi la sigue.",
    "    '",
    "    '  · POSE IDLE NUEVA (informe: «sustituye la posición idle, la que",
    "    '    tienes tiene un error»): el arte nuevo del dueño",
    "    '    (zombi_idle.png) entra como idle.webp con el mismo pipeline de",
    "    '    las 12 poses (limpiado perimetral + webp).",
    "    '",
    "    '  · MANO DE ZOMBI EN SU TIERRA (informe: «deben aparecer siempre",
    "    '    dentro del tablero… la mano POR DELANTE de la tierra; ahora es",
    "    '    al revés y no se ve la parte inferior»): el montículo nace",
    "    '    SIEMPRE dentro del canto (canto − radio 0,23) y el ORDEN DE",
    "    '    PINTADO queda montículo 3 → mano 4 → trocitos 5: la mano pisa",
    "    '    SU tierra y se ve entera.",
    "    '",
    "    '  · CALABAZA REESCRITA (informe: «no funciona, es imposible",
    "    '    jugarlo»): la calabaza ES la bola — centrada en su CENTRO",
    "    '    EXACTO (adiós el foleo +0,035 y el pivote del artista) y girando",
    "    '    COMO LA BOLA (mismo quaternion del mesh). Durante los 10 s se",
    "    '    OSCURECE (pudre, tinte por instancia) y 0,55 s antes del cierre",
    "    '    ESTALLA en 12 trozos con un «CHOFFF» — la bola normal vuelve en",
    "    '    ese instante: NUNCA calabaza y bola a la vez. Sin rebotes",
    "    '    aleatorios: física de bola pesada y nada más (se siente más",
    "    '    pesada: hay que golpearla más fuerte).",
    "    '",
    "    '  · GELATINA CON FÍSICA NORMAL (informe: «las manchas dentro de la",
    "    '    mesa… sonido CHOFFF… bola verde fosforito y al botar explosión",
    "    '    de humo verde… su peso no varía»): las 5 manchas nacen SIEMPRE",
    "    '    dentro del tablero (radio CIRCUNSCRITO del cuadrado girado), el",
    "    '    pisado suena CHOFFF y tiñe la bola de verde fosforito SIN tocar",
    "    '    la gravedad (la r87 la pesaba ×3: retirado), y cada BOTE en",
    "    '    mesa o pala lanza una RÁFAGA de 18 sprites de humo verde que",
    "    '    dificulta mucho la visión (sobrevive al cierre del poder y se",
    "    '    disipa sola).",
    "    '",
    "    '  · LA SALA ARMANA EN CALMA (informe: «al arrancar la escena, lo de",
    "    '    siempre: la bola sobre la mesa con botes y ruido infinito»): en",
    "    '    el estado de sala de campeonato (champtest) la bola queda",
    "    '    APARCADA e INERTA — sin gravedad, sin micro-botes, sin «pock» —",
    "    '    el mismo remedio del holdLock del tutorial r62. El paso de sala",
    "    '    de CUALQUIER campeonato nunca vuelve a sonar solo.",
    "    '",
    "    'Hereda de V3.6.79 (FASE 81: zombi visible, mapa con tapas, cartel",
    "    'de superpoder, 4 superpoderes y la red social real del Pulso; 5",
    "    'campeonatos, CCD, CRAZY TV y el Hall Of Fame).",
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

    # 1 · identidad de la release: v3679 → v3680 / V3.6.79 → V3.6.80
    txt = txt.replace("V3.6.79-SDK6", "V3.6.80-SDK6")
    txt = txt.replace("3.6.79-SDK6", "3.6.80-SDK6")   # guards contra game_src
    txt = txt.replace("v3679-sdk6", "v3680-sdk6")
    txt = txt.replace("release-v3679", "release-v3680")
    txt = txt.replace("staging-v3679", "staging-v3680")
    txt = txt.replace('grep -c "3.6.79"', 'grep -c "3.6.80"')
    txt = txt.replace("menciones 3.6.79", "menciones 3.6.80")
    txt = txt.replace("no es el v3679", "no es el v3680")
    txt = txt.replace("n3679 = int", "n3680 = int")
    txt = txt.replace("{n3679}", "{n3680}")
    txt = txt.replace("if n3679 < 4:", "if n3680 < 4:")

    # 2 · notas: bloque FASE 81 → bloque FASE 82
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 81 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + _construir_bloque() + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.80-SDK6'" in txt, "guard VERSION"
    assert "V3.6.80-SDK6" in txt, "badge"
    assert "FASE 82" in txt, "notas FASE 82"
    assert "FASE 81 —" not in txt, "quedan notas FASE 81"
    print("✓ release-v3680 creada (notas FASE 82, guards V3.6.80-SDK6)")


if __name__ == "__main__":
    main()
