#!/usr/bin/env python3
"""gen_release_v3679 — hereda scripts/release-v3678 → scripts/release-v3679
e inserta las NOTAS de la FASE 81 «EL INFORME DEL DUEÑO EN MANO» en
build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3679 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3678"
DEST = RAIZ / "scripts" / "release-v3679"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 80 — ESCENARIO REAL DE HALLOWEEN + 4" + NL + "'"
BLOQUE_VIEJO_FIN = ("    'poderes, CCD, CRAZY TV y el Hall Of Fame)." + NL + "'"
                    + chr(10) + "    '" + NL + "'")

# líneas de texto PLANO de las notas FASE 81 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 81 — EL INFORME DEL DUEÑO EN MANO: el",
    "    'zombi VISIBLE, el mapa en su pared, el cartel de superpoder, los 4",
    "    'superpoderes según el guion y LA RED SOCIAL DEL PULSO real.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.78-SDK6):",
    "    '",
    "    '  · EL ZOMBI APARECE (informe del dueño: «no aparece el rival»): el",
    "    '    standee del SDK NUNCA se añadía a la escena y nacía medio",
    "    '    enterrado (y=0). Ahora vive en el grafo con los pies en el suelo,",
    "    '    flotación sobre el node real y las 12 caras pre-calentadas tras",
    "    '    el telón (cero tirones al cambiar de emoción en pleno duelo).",
    "    '",
    "    '  · EL CARTEL DE SUPERPODER SE VE (informe: «no aparece el cartel»):",
    "    '    sin dims el anclaje nacía en el ORIGEN del rig (a los pies).",
    "    '    Ahora se ancla a la red como en los otros campeonatos, con el",
    "    '    arte SuperPower del dueño + medallón circular por poder +",
    "    '    congelación momentánea. También el cartel de bienvenida vuelve a",
    "    '    la escena (y a la pared frontal).",
    "    '",
    "    '  · MAPA EN LA PARED IZQUIERDA (normativa del dueño): x −3,03 con",
    "    '    rotY π/2 y TAPAS sobre las etapas aún no superadas (discos «?»",
    "    '    de hueso que se retiran al superar cada etapa) — el mismo",
    "    '    criterio del mapa canvas de la casa. Y nada queda colgado al",
    "    '    salir: _desmonta retira rival/mapa/cartel/insignia/poderes.",
    "    '",
    "    '  · MANO DE ZOMBI SEGÚN EL GUION: montículo.png aparece PLANO sobre",
    "    '    la mesa (0,32 s) y de él DESENROLLA una de las 3 manos (0,5 s",
    "    '    rápida que se frena al final para dar el susto, 2 s de vaivén,",
    "    '    retracto 0,5 s y ambos se funden). La bola que la toca queda",
    "    '    PARADA y se cae; la mano sale empujada y revienta en trocitos.",
    "    '    Pool de clones de textura: cero subidas a GPU por aparición.",
    "    '",
    "    '  · PLAGA DE MOSCAS DE GALA: 24 moscas con 2 FRAMES de aleteo (fase",
    "    '    propia por mosca), dardos y deriva viva, ZUMBIDO de enjambre en",
    "    '    bucle (fly_buzz.mp3 del motor createBucle) y espantado con la",
    "    '    pala con blip sonoro.",
    "    '",
    "    '  · CALABAZA (informe: «no se ve por ningún lado y la bola",
    "    '    desaparece»): el callback del GLB llegaba ANTES de registrar el",
    "    '    estado del poder y el guard lo saltaba. Ahora el estado va",
    "    '    PRIMERO, y si el GLB tarda >2,5 s hay calabaza procedural de",
    "    '    respaldo: la bola JAMÁS se queda sin cuerpo. Gravedad ×2,1 y",
    "    '    salida en CUALQUIER dirección tras cada bote en la mesa.",
    "    '",
    "    '  · GELATINA ASQUEROSA (mismo arreglo + guion): 5 manchas UN POCO",
    "    '    POR ENCIMA de la mesa (0,26–0,38 m), bola VERDE FOSFORITO con",
    "    '    POR LO MENOS 3 VECES más de peso (gravedad ×3 + frenado) y",
    "    '    humillo verde que crece y se desvanece.",
    "    '",
    "    '  · LA RED SOCIAL DEL PULSO ES REAL (informe: «no tengo estadísticas,",
    "    '    ni indicación de jugadores conectados ni aviso alguno»): el",
    "    '    worker de producción sirve /api/presencia y /api/invita (D1,",
    "    '    TTL 90 s / buzón 6 h, anti-spam por sala viva); el juego lleva",
    "    '    latido cada 20 s, MEDALLÓN numerado sobre la tarjeta",
    "    '    Multijugador (verde con gente, ÁMBAR con invitación), tarjeta de",
    "    '    invitación con UNIRSE/Descartar, lista de jugadores para INVITAR",
    "    '    sin teclear código y aviso en el árbitro. Verificado E2E con 2",
    "    '    jugadores reales hasta la partida (capa BX 31/0).",
    "    '",
    "    '  · PANEL DE TELEMETRÍA con URL estable: /telemetria.html en el",
    "    '    propio sitio (Producción D1 por defecto, clave en el navegador).",
    "    '",
    "    '  · FLUIDEZ (informe: «iba a trompicones»): prewarm de shaders tras",
    "    '    el telón, prewarm de las 12 caras del rival, pool de texturas",
    "    '    de mano y precarga total de los assets de superpoderes — las",
    "    '    subidas a GPU y las compilaciones GLSL jamás caen en plena",
    "    '    partida.",
    "    '",
    "    'Hereda de V3.6.78 (FASE 80: la sala real de la estancia, los 4",
    "    'troqueles, la mesa de losa y los 4 superpoderes del zombi; 5",
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

    # 1 · identidad de la release: v3678 → v3679 / V3.6.78 → V3.6.79
    txt = txt.replace("V3.6.78-SDK6", "V3.6.79-SDK6")
    txt = txt.replace("3.6.78-SDK6", "3.6.79-SDK6")   # guards contra game_src
    txt = txt.replace("v3678-sdk6", "v3679-sdk6")
    txt = txt.replace("release-v3678", "release-v3679")
    txt = txt.replace("staging-v3678", "staging-v3679")
    txt = txt.replace('grep -c "3.6.78"', 'grep -c "3.6.79"')
    txt = txt.replace("menciones 3.6.78", "menciones 3.6.79")
    txt = txt.replace("no es el v3678", "no es el v3679")
    txt = txt.replace("n3678 = int", "n3679 = int")
    txt = txt.replace("{n3678}", "{n3679}")
    txt = txt.replace("if n3678 < 4:", "if n3679 < 4:")

    # 2 · notas: bloque FASE 80 → bloque FASE 81
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 80 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + _construir_bloque() + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.79-SDK6'" in txt, "guard VERSION"
    assert "V3.6.79-SDK6" in txt, "badge"
    assert "FASE 81" in txt, "notas FASE 81"
    assert "FASE 80 —" not in txt, "quedan notas FASE 80"
    print("✓ release-v3679 creada (notas FASE 81, guards V3.6.79-SDK6)")


if __name__ == "__main__":
    main()
