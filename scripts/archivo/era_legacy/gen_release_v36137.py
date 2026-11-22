#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.137-SDK6 (r41).
Crea scripts/release-v36137/ a partir de scripts/release-v36136/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 139
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36137 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36137.py
    python3 scripts/release-v36137/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36136"
DEST = RAIZ / "scripts" / "release-v36137"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 139 — EL ARCANO HOLOGRÁFICO: el pulido",
    "del dueño sobre el espacio arcano de la r40 — motas de polvo",
    "CIRCULARES y menores, SUELO NEGRO con matriz fina de losetas y",
    "rellenos azules que NACEN y MUEREN al azar, flechas ‹ › con los",
    "glifos DESCruzados (icono = lado = acción), iconos a SANGRE COMPLETA",
    "en el medallón, panel con APARICIÓN HOLOGRÁFICA (bandas, disolución,",
    "barrido y parpadeo), LA VOZ que presenta cada poder, los ojos del",
    "búho con HALO azul↔rojo y el CANDADO FLOTANTE con halo rojo",
    "pulsante delante del icono).",
    "  · 1 · MOTAS DE POLVO (c08): textura radial — punto REDONDO y",
    "    suave, jamás el cuadrado del PointsMaterial pelado — y la MITAD",
    "    de tamaño (0,055 → 0,026).",
    "  · 2 · EL SUELO NEGRO DE LOSETAS (c08): TRES planos — BASE negra",
    "    (radial al color del horizonte #0a1a36: la costura con la bóveda",
    "    sigue siendo imposible), MATRIZ ESTÁTICA de 48×48 losetas de",
    "    1,5 m (la r40 eran 9×9 de 8 m — ahora más pequeñas y mejor",
    "    definidas) con líneas SIEMPRE visibles y nodos cada 8 losetas,",
    "    y RELLENOS VIVOS: cada loseta NACE (subida rápida), AGUANTA y",
    "    MUERE en posiciones TOTALMENTE aleatorias con la banda azul del",
    "    dueño (#10284e → #1a3868) — «unas aparecen, otras se apagan, de",
    "    forma completamente aleatoria».",
    "  · 3 · FLECHAS INTERCAMBIADAS (c08): los GLIFOS estaban cruzados —",
    "    el glifo L dibujaba el chevron › y el R dibujaba ‹. Ahora ‹ vive",
    "    a la IZQUIERDA (retrocede, oculto en el 0) y › a la DERECHA",
    "    (avanza, oculto en el último): el icono coincide SIEMPRE con el",
    "    lado y con la acción.",
    "  · 4 · ICONOS A SANGRE COMPLETA (c08): escala 1,28R → 1,96R",
    "    recortada al propio círculo (sin letterbox) — «deben ocupar",
    "    TODO el espacio del círculo azul que los perimetra»; bloqueado,",
    "    el icono se ATENÚA (0,42) para que el candado destaque.",
    "  · 5 · APARICIÓN HOLOGRÁFICA (c08): DOS lienzos (cv = ficha",
    "    completa, holo = lienzo vivo) y arconoHoloFrame compone la",
    "    formación ~1,1 s — bandas horizontales que viajan y se asientan,",
    "    DISOLUCIÓN de motas (destination-out), BARRIDO de condensación",
    "    (lighter), líneas de escaneo con parpadeo de encendido y",
    "    aberración fantasma que se cierra; a k=1 copia exacta y la",
    "    textura duerme (coste cero en reposo).",
    "  · 6 · LA VOZ PRESENTA CADA PODER (c12): _arconoRepinta llama a",
    "    _vozSel (nombre corto embebido ES/EN, la misma vía del selector)",
    "    al navegar con ‹ ›; en la ENTRADA el hint habla primero y el",
    "    poder entra 2,3 s después (UNA voz viva, jamás dos a la vez).",
    "  · 7 · HALO EN LOS OJOS DEL BÚHO (c08): el color de los dos glints",
    "    del espacio OSCILA 0x49b6ff ↔ 0xff3524 con un seno lento y el",
    "    halo respira con la misma fase (escala del sprite).",
    "  · 8 · CANDADO FLOTANTE (c08/c12): GRUPO propio DELANTE del",
    "    medallón (z −2,28 vs panel −2,35, borde inf-derecho del círculo,",
    "    SIN tapar jamás el icono) — glifo azul en SU lienzo",
    "    (drawArcanoCandado) + sprite de HALO ROJO pulsante (escala",
    "    0,24→0,37 y opacidad 0,34→0,84 por seno); c12 sincroniza la",
    "    visibilidad con el estado REAL de desbloqueo.",
    "  · 9 · QA: test_r41_arcano_holo_v36137 NUEVO 92/0 (sellos, motas,",
    "    suelo negro, flechas, iconos, holograma, voz, ojos, candado,",
    "    física byte-exacto) · PROBE EN VIVO 9/9 (entrada, suelo negro",
    "    medido por píxel, losetas vivas, flechas descruzadas, holograma",
    "    formándose y condensado, candado delante, ojos oscilando, voz",
    "    con espía, motas circulares, 0 pageerrors) · regresión",
    "    re-anclada (sella_r41_viva): r40 62/0 · r39 165/0 · r38 51/0 ·",
    "    r37 46/0 · r36 30/0 · r35 36/0 · r34 61/0 · r33 77/0 · r32 49/0 ·",
    "    r31 47/0 · r30 54/0 · r24 89/0 · test_red_nucleo (PPNET) 60/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: el Arcano a la vista r40 (búho 25 %, pulsables",
    "    sin menú, escenario delante, cielo liso, arcano.mp3), apartado",
    "    arcano r39 (galería de los 14, desbloqueo por coronación, Duelos",
    "    Locos), salón de la partida r38, multijugador r37/r36, Prisma",
    "    visible r35, fixes r34, lote r33, salones r32, higiene r31,",
    "    Fénix r30, Oscuridad/Crono, voces Piper, iconos del dueño, bola",
    "    atractora r26b, barrera eléctrica, FORO3D r27, skins r21,",
    "    cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2, ELO,",
    "    matchmaking, halloween.",
    "  · sellada a",
    "  3.6.137",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36136", "release-v36137"),
    ("staging-v36136", "staging-v36137"),
    ("V3.6.136-SDK6", "V3.6.137-SDK6"),
    ("3.6.136-SDK6", "3.6.137-SDK6"),
    ("v36136-sdk6", "v36137-sdk6"),
    ("v36136", "v36137"),
    ("3.6.136", "3.6.137"),
    ("fase 138", "fase 139"),
    ("FASE 138", "FASE 139"),
    ("Fase 138", "Fase 139"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36136 son las de la r40, ya re-selladas a FASE 139 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 139 — EL ARCANO A LA VISTA: revisión del"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.137" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.137-SDK6 lista: el Arcano a la vista — "
                     "el búho un 25 % más pequeño, los botones del hall pulsables SIN "
                     "menú, el escenario arcano DELANTE del anfitrión (nunca más a la "
                     "espalda), cielo azul oscuro liso sin imagen, suelo infinito de "
                     "losetas que mutan su azul y la melodía propia arcano.mp3; "
                     "test r40 62/0 y regresión re-anclada verde." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.137-SDK6 lista: el Arcano holográfico — "
                     "motas de polvo circulares, suelo negro con matriz fina y "
                     "rellenos que nacen y mueren al azar, flechas descruzadas "
                     "(‹ izquierda · › derecha), iconos a sangre completa, panel "
                     "con aparición holográfica, la voz que presenta cada poder, "
                     "ojos del búho azul↔rojo y candado flotante con halo rojo "
                     "pulsante; test r41 92/0, probe en vivo 9/9 y regresión "
                     "re-anclada verde." + "')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
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
        # bloque de notas → FASE 139 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        else:
            notas_ok = 0
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA, 1)
            linea_ok = 1
        elif LINEA_FINAL_NUEVA in txt:
            linea_ok = 1
        else:
            linea_ok = 0
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36137 · {tocados} ficheros re-sellados · '
          f'notas FASE 139 {notas_ok}/1 · línea final {linea_ok}/1')


if __name__ == '__main__':
    main()
