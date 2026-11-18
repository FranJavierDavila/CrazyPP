#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.136-SDK6 (r40).
Crea scripts/release-v36136/ a partir de scripts/release-v36135/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 138
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36136 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36136.py
    python3 scripts/release-v36136/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36135"
DEST = RAIZ / "scripts" / "release-v36136"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 138 — EL ARCANO A LA VISTA: revisión del",
    "dueño sobre la r39 — el búho del hall un 25 % más pequeño, los",
    "botones del hall PULSABLES SIN MENÚ (el rayo y el hover viven siempre",
    "en las estancias), el escenario arcano nace DELANTE del anfitrión (el",
    "bug raíz de la r39 lo dejaba a 14 m a la espalda: «no aparecía",
    "nada»), cielo azul oscuro LISO sin imagen, SUELO INFINITO de losetas",
    "grandes que MUTAN su azul al azar y la MELODÍA PROPIA arcano.mp3).",
    "  · 1 · EL BÚHO, UN 25 % MÁS PEQUEÑO (c08): la placa del hall pasa de",
    "    0,78×0,52 a 0,585×0,39 (×0,75 exacto, misma proporción 1024×683;",
    "    los destellos de los ojos escalan con ARC_W/ARC_H, misma pared).",
    "  · 2 · PULSABLES SIN MENÚ (c12, petición literal: «si existen botones",
    "    repartidos por el hall estos se deben poder pulsar sin necesidad",
    "    de sacar el menú»): updateMenu corre TAMBIÉN sin menú en el salón",
    "    y en el Arcano — el rayo, el HAZ (mirilla honesta de 3 m) y el",
    "    hover del búho y de la placa de la música viven desde el primer",
    "    segundo; el panel del menú SÓLO es objetivo con el menú abierto",
    "    (ni botón fantasma ni cursor en el aire); DENTRO del Arcano B no",
    "    abre nada: EL BÚHO es la única puerta de vuelta.",
    "  · 3 · EL ESCENARIO NACE DELANTE (c12, bug raíz de la r39): el grupo",
    "    arcano se PLANTA sobre los pies del anfitrión (XZ del rig) y gira",
    "    al yaw de la cabeza en cada entrada — búho, galería y flechas",
    "    SIEMPRE delante, esté donde esté y mirando a donde mire. Además",
    "    fog:false en TODAS las piezas: la niebla de la cancha (Fog 9/18)",
    "    ahogaba los cometas de la r39 a 22-38 m.",
    "  · 4 · CIELO LISO + SUELO INFINITO (c08): bóveda SIN Vía Láctea ni",
    "    estrellas — «el fondo completamente azul oscuro sin imagen» (sólo",
    "    el degradado azul noche #03061a→#0a1a36); el SUELO es un plano",
    "    72×72 m con losetas GRANDES de 8 m (9×9), retícula fina sutil,",
    "    banda azulada apenas más clara que el cielo (#10284e→#1a3868) y",
    "    viñeta radial que funde al color del horizonte (el suelo «se",
    "    pierde» sin costura); las losetas MUTAN su tono al azar (7 eligen",
    "    tono cada 0,35 s, mordisco suave, re-pintado por loseta). 240",
    "    motas que serpentean, destellos flotantes y cometas con halo",
    "    azul (conservados de la r39, ahora visibles).",
    "  · 5 · LA MELODÍA PROPIA (c12/c03): dentro del Arcano NO suena la",
    "    pista del salón sino arcano.mp3 (el arte del dueño, byte-exacto en",
    "    assets/hall/arcano.mp3) por el ÚNICO canal de música ambiental",
    "    (canal hall: caché, fundidos, prioridad sobre el menú); al salir,",
    "    _arconoSalir restaura el aire del salón (SU variante — o la del",
    "    anfitrión en visita online) por el mismo camino que enterHall.",
    "  · 6 · SE CONSERVA DE LA R39: la galería automática de los 14",
    "    superpoderes (nombre + tipo + descripción + MÉTRICAS reales),",
    "    flechas ‹ › con glow azul SIN flecha en los extremos, candado",
    "    azul translúcido con descripciones legibles, desbloqueo por",
    "    coronación (azar sin repetición) y Duelos Locos con los",
    "    desbloqueados.",
    "  · 7 · QA: test_r40_arcano_v36136 NUEVO 62/0 (sellos, búho 25 %,",
    "    cielo liso, suelo que muta, escenario delante, pulsables sin",
    "    menú, melodía propia, física byte-exacto) · regresión re-anclada",
    "    (sella_r40_viva): r39 165/0 · r38 51/0 · r37 46/0 · r36 30/0 ·",
    "    r35 36/0 · r34 61/0 · r33 77/0 · r32 49/0 · r31 47/0 · r30 54/0 ·",
    "    r24 89/0 · test_red_nucleo (PPNET) 60/0 · estilos 12/0 ·",
    "    presupuesto refrescado (boot 3.184 ms, 0 pageerrors).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: apartado arcano r39 (búho con destello, galería",
    "    de los 14, desbloqueo por coronación, Duelos Locos), salón de la",
    "    partida r38 (Rascacielos + partidas en el hall del anfitrión),",
    "    multijugador r37 (reinicio ICE real, ack monotono u16, hangup",
    "    i18n) y r36 (ventana viva, pausa legal, eventos sin fantasmas),",
    "    Prisma visible r35 (bola arcoíris), fixes r34 (Red en rig, voz de",
    "    los 14, Electricidad con retención, Prisma por campos), lote",
    "    aprobado r33, salones del dueño r32 con su música, higiene Fénix",
    "    r31, Fénix jugable r30, Súper Oscuridad, Crono, voces Piper,",
    "    iconos del dueño, bola atractora r26b, barrera eléctrica, FORO3D",
    "    r27, skins r21, cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK",
    "    v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.136",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36135", "release-v36136"),
    ("staging-v36135", "staging-v36136"),
    ("V3.6.135-SDK6", "V3.6.136-SDK6"),
    ("3.6.135-SDK6", "3.6.136-SDK6"),
    ("v36135-sdk6", "v36136-sdk6"),
    ("v36135", "v36136"),
    ("3.6.135", "3.6.136"),
    ("fase 137", "fase 138"),
    ("FASE 137", "FASE 138"),
    ("Fase 137", "Fase 138"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36135 son las de la r39, ya re-selladas a FASE 138 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 138 — EL APARTADO ARCANO: el búho del hall"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.136" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.136-SDK6 lista: el apartado arcano — "
                     "el búho del hall (Arcano.png con destello en los ojos), el espacio "
                     "infinito azul (motas, cometas y Vía Láctea), la galería automática "
                     "de los 14 superpoderes con candados y desbloqueo por campeonato "
                     "ganado, y los desbloqueados JUGABLES en Duelos Locos; test r39 165/0 "
                     "y regresión re-anclada verde." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.136-SDK6 lista: el Arcano a la vista — "
                     "el búho un 25 % más pequeño, los botones del hall pulsables SIN "
                     "menú, el escenario arcano DELANTE del anfitrión (nunca más a la "
                     "espalda), cielo azul oscuro liso sin imagen, suelo infinito de "
                     "losetas que mutan su azul y la melodía propia arcano.mp3; "
                     "test r40 62/0 y regresión re-anclada verde." + "')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    notas_ok = 0
    linea_ok = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 138 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            j = txt.find(FIN_MARCADOR, i)
            if j < 0:
                raise SystemExit(
                    f'ABORTA: INI sin FIN en {f.name} — nada escrito.')
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
            notas_ok += 1
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
            linea_ok += 1
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    if notas_ok != 1 or linea_ok != 1:
        raise SystemExit(
            f'ABORTA: sustituciones esperadas 1/1, obtenidas '
            f'notas {notas_ok} y línea final {linea_ok} — nada escrito.')
    print(f'OK gen_release_v36136 · {tocados} ficheros re-sellados · '
          f'notas FASE 138 {notas_ok}/1 · línea final {linea_ok}/1')


if __name__ == '__main__':
    main()
