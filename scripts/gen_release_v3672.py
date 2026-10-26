#!/usr/bin/env python3
"""gen_release_v3672 — hereda scripts/release-v3671 → scripts/release-v3672
e inserta las NOTAS de la FASE 74 «EL RETO DIARIO EN LA PUERTA» en
build_zip.py.

Idempotente: si release-v3672 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3671"
DEST = RAIZ / "scripts" / "release-v3672"

BZ = DEST / "build_zip.py"

# Bloque de notas FASE 73 (r79) que sale entero
BLOQUE_VIEJO_INI = ("    'Rama    : main · SDK6 (FASE 73 — CRAZY LINK v2: el multijugador deja\\n'")
BLOQUE_VIEJO_FIN = ("    '    y telemetría de red (net_match) para medirlo todo.\\n\\n'")

# Bloque nuevo FASE 74 (r80)
BLOQUE_NUEVO = """    'Rama    : main · SDK6 (FASE 74 — EL RETO DIARIO EN LA PUERTA: informe\\n'
    'del dueño («en el submenu del multijugador has colocado mal los\\n'
    'botones que se están pisando con el marco superior del menú y los\\n'
    'idiomas. Ponerlo bien. Al pulsar sobre estos modos de juego\\n'
    'multijugador es cuando aparecen las opciones de sala y código. Otra\\n'
    'cosa, La opción del reto del dia debe estar especialmente destacada\\n'
    'en la parte de abajo del menú principal (y la retiramos del apartado\\n'
    'de entrenamiento) Un botón con la pala troquelada con el texto\\n'
    '"Reto Diario!" y un pequeño resplandor en su perímetro para llamar\\n'
    'la atención… las zonas de bote… más permisivas y grandes… digamos\\n'
    'que el doble de anchas. Esto es para no desanimar al jugador»))\\n\\n'
    'Novedades de esta versión (frente a V3.6.71-SDK6):\\n\\n'
    '  · EL SUBMENÚ QUE RESPIRA: las dos tarjetas de modo del multijugador\\n'
    '    BAJAN bajo la cabecera (ya no pisan el marco superior ni las palas\\n'
    '    de idioma) y las opciones de sala y código aparecen AL PULSAR un\\n'
    '    modo — sin elegir, el submenú sólo ofrece NORMAL · PARTIDA y\\n'
    '    DUELOS LOCOS (candado + PRÓXIMAMENTE intactos). Cancelar o colgar\\n'
    '    devuelve a la selección de modos.\\n\\n'
    '  · EL RETO DIARIO EN LA PUERTA: botón estrella al pie del menú\\n'
    '    principal con la PALA TROQUELADA (silueta recortada con borde\\n'
    '    punteado de troquel, agujeros de perforación y oreja de colgante),\\n'
    '    el texto literal «Reto Diario!» y un RESPLANDOR en su perímetro\\n'
    '    (verde cuando ya está hecho hoy). Muestra el duelo del día y la\\n'
    '    racha viva: es el reclamo para volver cada día y liberar poco a\\n'
    '    poco las apariencias (palas, pistas y bolas).\\n\\n'
    '  · FUERA DEL ENTRENAMIENTO: el panel del reto se retira del hub de\\n'
    '    PRO TRAINING; quedan las PIELES DE ASISTENCIA como escaparate de\\n'
    '    lo que la racha de días desbloquea.\\n\\n'
    '  · EL RETO PERMISIVO: las zonas de bote del reto diario son el DOBLE\\n'
    '    de anchas — bandas laterales 10→20 cm, franja de fondo 12→24 cm,\\n'
    '    doble bote junto a la red 0,51→1,02 m, franja del saque profundo\\n'
    '    15→30 cm, filas del objetivo más generosas y centro prohibido a la\\n'
    '    mitad. Lo pintado ES lo juzgado (pintor y árbitro comparten las\\n'
    '    mismas dimensiones); en entrenamiento normal TODO queda igual. La\\n'
    '    dificultad irá subiendo con el tiempo.\\n\\n'
"""


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3671 → v3672 / V3.6.71 → V3.6.72
    txt = txt.replace("V3.6.71-SDK6", "V3.6.72-SDK6")
    txt = txt.replace("3.6.71-SDK6", "3.6.72-SDK6")   # guards contra game_src
    txt = txt.replace("v3671-sdk6", "v3672-sdk6")
    txt = txt.replace("release-v3671", "release-v3672")
    txt = txt.replace("staging-v3671", "staging-v3672")
    txt = txt.replace('grep -c "3.6.71"', 'grep -c "3.6.72"')
    txt = txt.replace("menciones 3.6.71", "menciones 3.6.72")
    txt = txt.replace("no es el v3671", "no es el v3672")
    txt = txt.replace("n3671 = int", "n3672 = int")
    txt = txt.replace("{n3671}", "{n3672}")
    txt = txt.replace("if n3671 < 4:", "if n3672 < 4:")

    # 2 · notas: bloque FASE 73 → bloque FASE 74
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 73 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + BLOQUE_NUEVO + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.72-SDK6'" in txt, "guard VERSION"
    assert "V3.6.72-SDK6" in txt, "badge"
    assert "FASE 74" in txt, "notas FASE 74"
    assert "FASE 73" not in txt, "quedan notas FASE 73"
    print("✓ release-v3672 creada (notas FASE 74, guards V3.6.72-SDK6)")


if __name__ == "__main__":
    main()
