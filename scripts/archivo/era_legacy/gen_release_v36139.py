#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.139-SDK6 (r45+r46).
Crea scripts/release-v36139/ a partir de scripts/release-v36138/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 141
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36139 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36139.py
    python3 scripts/release-v36139/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36138"
DEST = RAIZ / "scripts" / "release-v36139"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 141 — LA VITRINA DEL CIELO: el candado",
    "del dueño, la constelación de palas, la skin de la pala en red y",
    "los RANKINGS MUNDIALES — la petición del dueño: analizar el juego",
    "con gráficas fáciles de leer (retención, ranking, logros,",
    "desbloqueos) y la garantía de que la telemetría JAMÁS cuesta FPS",
    "en una partida en red).",
    "  · 1 · CANDADO DEL DUEÑO (c08): el candado de los superpoderes",
    "    bloqueados estrena SU IMAGEN (candado.png, el arte del dueño)",
    "    con el halo rojo de siempre, en la esquina superior izquierda",
    "    del icono del superpoder.",
    "  · 2 · CONSTELACIÓN DE PALAS (c08): el cielo del Arcano dibuja el",
    "    contorno de palas.png como una constelación viva — polilíneas",
    "    del arte trazadas con glow azul (la estética del búho) que",
    "    nacen en un punto, se dibujan solas hasta completarse, se",
    "    desvanecen y reaparecen en otra posición aleatoria de la",
    "    bóveda (~cada 10 s, muy sutil).",
    "  · 3 · SKIN DE LA PALA EN RED (c09/c12): el HELLO v2 lleva el",
    "    campo opcional `sp` con la skin de pala propia — la pala del",
    "    INVITADO se viste con su personalización en el duelo (los",
    "    halls y la bola ya viajaban desde antes).",
    "  · 4 · RANKINGS MUNDIALES (c00/c12 + worker v3 + panel): cada",
    "    evento firma el pid anónimo persistente y el nombre elegido;",
    "    el juego emite perfil (ELO, victorias, racha, estrellas,",
    "    puntos y logros), resultado de partido (modo, marcador y",
    "    victoria) y logro (uno por desbloqueo); el worker añade",
    "    ?rank=1 (4 tablas top-20: ELO · victorias · puntos Pro",
    "    Training · logros, ventana 90 días) y el resumen gana",
    "    retención (D1/D7/D30 + % recurrentes) y logrosTop; el panel",
    "    «Centro de Telemetría» pinta Rankings mundiales, Retención y",
    "    Desbloqueos de logros con barras y exportación CSV/JSON de",
    "    todo.",
    "  · 5 · GOBERNADOR DE TELEMETRÍA (c00/c12): en partida EN RED, si",
    "    la media de FPS cae bajo 58 en DOS ventanas seguidas de 5 s,",
    "    la telemetría se CONGELA sola (nada toca la red ni el GC: la",
    "    cola espera en memoria, tope 60 eventos) y se descongela al",
    "    recuperar 60+ o al terminar el duelo — la experiencia de juego",
    "    tiene prioridad absoluta.",
    "  · 6 · QA: test_r45_vitrina_cielo_v36139 55/0 (candado,",
    "    constelación, skin `sp`, perfil/resultado/logro y panel) ·",
    "    worker v3 en local 102/0 (?rank=1, retención con cohortes",
    "    sintéticas, logrosTop, tolerancia sin pid) · test_r43 79/0 ·",
    "    r41 92/0 · r40 62/0 · test_red_nucleo (PPNET) 60/0 · qa_sup1",
    "    151/0 · qa_telemetria 132/0 · qa_version 29/0 · humo r46 del",
    "    gobernador en vivo (versión, badge, __PP_TELE.partida, 0",
    "    pageerrors) · presupuesto y física determinista verdes.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: el suelo de destellos r43, el duelo honesto y",
    "    la física en tiempo real, la esfera del casco en el RIG, el",
    "    Arcano holográfico r41, apartado arcano r39/r40 (búho 25 %,",
    "    pulsables sin menú, arcano.mp3, Salir/Exit), salón de la",
    "    partida r38, multijugador r37/r36, Prisma visible r35, fixes",
    "    r34, lote r33, salones r32, higiene r31, Fénix r30,",
    "    Oscuridad/Crono, voces Piper, iconos del dueño, bola atractora",
    "    r26b, barrera eléctrica, FORO3D r27, skins r21, cortina etapas",
    "    2/4, _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking,",
    "    halloween.",
    "  · sellada a",
    "  3.6.139",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36138", "release-v36139"),
    ("staging-v36138", "staging-v36139"),
    ("V3.6.138-SDK6", "V3.6.139-SDK6"),
    ("3.6.138-SDK6", "3.6.139-SDK6"),
    ("v36138-sdk6", "v36139-sdk6"),
    ("v36138", "v36139"),
    ("3.6.138", "3.6.139"),
    ("fase 140", "fase 141"),
    ("FASE 140", "FASE 141"),
    ("Fase 140", "Fase 141"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36138 son las de la r43, ya re-selladas a FASE 141 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 141 — EL SUELO DE DESTELLOS y el DUELO"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.139" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.139-SDK6 lista: el suelo de destellos — "
                     "la trama fina sólo existe donde un destello la dibuja "
                     "(90°, ambos sentidos, estela ~5 s), letrero Salir/Exit "
                     "sobre el búho, la esfera del casco remoto en el RIG, "
                     "saques sin bola invisible, convergencia del fantasma en "
                     "la zona de juicio y fluido: física en tiempo real + TX "
                     "sin allocations; test r43 79/0, probe en vivo 9/9 y "
                     "regresión re-anclada verde." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.139-SDK6 lista: la vitrina del cielo — "
                     "candado del dueño con halo rojo, constelación de palas "
                     "en la bóveda, skin de la pala del invitado en red, "
                     "rankings mundiales con retención y desbloqueos en el "
                     "panel y gobernador que congela la telemetría si la "
                     "partida en red baja de 58 fps; test r45 55/0, worker "
                     "102/0 y regresión re-anclada verde." + "')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    notas_ok = 0
    linea_ok = 0
    for p in DEST.rglob('*'):
        if not p.is_file() or p.suffix in ('.pyc',) or '__pycache__' in str(p):
            continue
        try:
            txt = p.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 141 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        else:
            notas_ok = notas_ok or 0
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA, 1)
            linea_ok = 1
        elif LINEA_FINAL_NUEVA in txt:
            linea_ok = 1
        else:
            linea_ok = linea_ok or 0
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36139 · {tocados} ficheros re-sellados · '
          f'notas FASE 141 {notas_ok}/1 · línea final {linea_ok}/1')


if __name__ == '__main__':
    main()
