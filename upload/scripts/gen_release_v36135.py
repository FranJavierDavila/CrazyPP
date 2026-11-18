#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.135-SDK6 (r39).
Crea scripts/release-v36135/ a partir de scripts/release-v36134/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 137
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36135 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36135.py
    python3 scripts/release-v36135/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36134"
DEST = RAIZ / "scripts" / "release-v36135"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 137 — EL APARTADO ARCANO: el búho del hall",
    "con el arte del dueño «Arcano.png» que destella por los dos ojos, el",
    "ESPACIO INFINITO azul con motas, cometas y Vía Láctea, la GALERÍA de",
    "superpoderes de pala con desbloqueo por campeonato ganado y los",
    "desbloqueados JUGABLES en Duelos Locos; petición del dueño: «El hall",
    "debería contener un apartado que explique los poderes de super pala…",
    "una especie de icono (Arcano.png) en la pared del fondo del hall o en",
    "una esquina superior derecha con la forma de un buho que emite un",
    "ligero destello a través de sus dos ojos…»).",
    "  · 1 · EL BÚHO DEL ARCANO EN EL HALL (c08/c12): placa con el arte",
    "    del dueño (1024×683, byte-exacto en assets/hall/arcano.png) en la",
    "    esquina superior derecha de la pared que el anfitrión mira al",
    "    entrar; DOS sprites aditivos sobre los centros de los ojos",
    "    MEDIDOS del arte (0.452/0.392 · 0.557/0.376) emiten el LIGERO",
    "    DESTELLO con dos fases vivas en updateHallFx; hover y gatillo",
    "    VR con el mismo raycast del icono de la música; fallback",
    "    vectorial si la textura no llega. Fundido a NEGRO con cortina",
    "    que sigue a la cabeza (0,42 m del ojo en VR) para el canje de",
    "    estancias — y la vía de vuelta idéntica.",
    "  · 2 · EL ESPACIO INFINITO (c08 montarArcano / c12): bóveda celeste",
    "    oscura esférica con la VÍA LÁCTEA pintada (banda diagonal de",
    "    nubes estelares + 610 estrellas), 240 MOTAS azules que",
    "    SERPENTEAN (base + fase propia por punto, Points aditivas) y",
    "    COMETAS ocasionales (3 en pool) que cruzan a lo lejos dejando su",
    "    HALO azul tras la cabeza. El búho SIGUE PRESENTE flotando con sus",
    "    ojos encendidos: pulsarlo devuelve al salón. Todo PROCEDURAL",
    "    (cero assets nuevos); el museo no juega: física c04/c05 INTACTA.",
    "  · 3 · LA GALERÍA DE SUPERPODERES (c12/c08/c00): los 14 poderes se",
    "    materializan UNO A UNO delante del anfitrión (pop elástico) con",
    "    icono embebido, nombre, TIPO (ataque/defensa/distracción con su",
    "    color), DESCRIPCIÓN y MÉTRICAS del juego que altera; el ÍNDICE es",
    "    AUTOMÁTICO contra PODERES_PALA (un poder nuevo hereda la galería",
    "    con añadir su ficha), flechas ‹ › con la estética azul y glow del",
    "    búho SIN flecha en los extremos (0 y último detectados del",
    "    registro), y CANDADO azul translúcido en los bloqueados con las",
    "    descripciones LEGIBLES igualmente. i18n ES/EN completo (16 claves",
    "    de UI + 14 descripciones + 14 métricas + 14 nombres de duelos).",
    "  · 4 · DESBLOQUEO POR CAMPEONATO GANADO (c12 + 6 módulos): cada",
    "    CORONACIÓN (duelo final ganado — la medalla LEYENDA y los",
    "    rejuegos NO repiten) libera UN superpoder AL AZAR que aún esté",
    "    con candado — el azar COMPRUEBA que no esté desbloqueado para no",
    "    dar el mismo (spec literal del dueño); persistencia saneada en",
    "    pp_poderes_v1; la REVELACIÓN se anuncia en el panel ¡CONSEGUIDO!",
    "    (línea azul bajo el título) y en la megafonía. Coronaciones",
    "    marcadas: locura · magia · oeste · estacion_orbital · halloween ·",
    "    plantilla (los campeonatos nuevos heredan).",
    "  · 5 · DUELOS LOCOS CON LOS DESBLOQUEADOS (c12/c09): el surto",
    "    aleatorio crece — gigante/fuego/loca (los NETCODE-SAFE de r84) +",
    "    TUS desbloqueados, cada uno con SU forma online segura: MEGA",
    "    (pala ×1,30/radio ×1,38, 15 s, bit 16 compartido), EFECTO (spin",
    "    ×3 en el canal de la LOCA), IMÁN (guía al punto dulce), CLON y",
    "    SALVA (palas fantasma/warp en TU mitad, devoluciones legales por",
    "    HIT), CRONO y RED (ritmo lento y red alta COMPARTIDOS por cable",
    "    fiable), OSCURIDAD (la niebla vive en MI golpeo), ONDA (el smash",
    "    avisa y la próxima devolución rival sale ×0,75), PORTAL (el",
    "    invitado portaliza SU golpe — owner = quien golpea), FENIX/PRISMA",
    "    (fuego y arcoíris viajan con la bola), ELEC (tormenta real sobre",
    "    el campo rival) y ANCLA (ESTRELLA los poderes entrantes). Ventanas",
    "    tickadas en duelos (13 compuertas) y recogida con FIN NATURAL",
    "    (red exacta, rapidez restaurada, marcas limpias) al morir el",
    "    modo; el cable pow ignora ids desconocidos (builds viejos",
    "    intactos, POSE 31 B intacto, PROTO 3).",
    "  · 6 · QA: test_r39_arcano_v36135 NUEVO 165/0 (sellos, arte",
    "    byte-exacto, búho/espacio/galería/desbloqueo/duelos, i18n 84",
    "    claves, 13 compuertas, física byte-exacto) · regresión",
    "    re-anclada (sella_r39_viva): r38 51/0 · r37 46/0 · r36 30/0 ·",
    "    r35 36/0 · r34 61/0 · r32 49/0 · r31 47/0 · r30 54/0 · r24 89/0 ·",
    "    test_red_nucleo (PPNET) 60/0 · estilos 66 parejas distinguibles ·",
    "    presupuesto refrescado.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: salón de la partida r38 (Rascacielos + partidas",
    "    en el hall del anfitrión), multijugador r37 (reinicio ICE real,",
    "    ack monotono u16, hangup i18n) y r36 (ventana viva, pausa legal,",
    "    eventos sin fantasmas), Prisma visible r35 (bola arcoíris),",
    "    fixes r34 (Red en rig, voz de los 14, Electricidad con",
    "    retención, Prisma por campos), lote aprobado r33, salones del",
    "    dueño r32 con su música, higiene Fénix r31, Fénix jugable r30,",
    "    Súper Oscuridad, Crono, voces Piper, iconos del dueño, bola",
    "    atractora r26b, barrera eléctrica, FORO3D r27, skins r21,",
    "    cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2, ELO,",
    "    matchmaking, halloween.",
    "  · sellada a",
    "  3.6.135",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36134", "release-v36135"),
    ("staging-v36134", "staging-v36135"),
    ("V3.6.134-SDK6", "V3.6.135-SDK6"),
    ("3.6.134-SDK6", "3.6.135-SDK6"),
    ("v36134-sdk6", "v36135-sdk6"),
    ("v36134", "v36135"),
    ("3.6.134", "3.6.135"),
    ("fase 136", "fase 137"),
    ("FASE 136", "FASE 137"),
    ("Fase 136", "Fase 137"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36134 son las de la r38, ya re-selladas a FASE 137 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 137 — EL SALÓN DE LA PARTIDA: RASCACIELOS,"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.135" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.135-SDK6 lista: el salón de la partida — "
                     "RASCACIELOS como 4.º salón del dueño (arte byte-exacto con SU pista "
                     "y su baliza) y las partidas EN EL HALL DEL ANFITRIÓN, contra la IA "
                     "y en multijugador (hallv fiable en vivo); test r38 51/0 y regresión "
                     "re-anclada verde." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.135-SDK6 lista: el apartado arcano — "
                     "el búho del hall (Arcano.png con destello en los ojos), el espacio "
                     "infinito azul (motas, cometas y Vía Láctea), la galería automática "
                     "de los 14 superpoderes con candados y desbloqueo por campeonato "
                     "ganado, y los desbloqueados JUGABLES en Duelos Locos; test r39 165/0 "
                     "y regresión re-anclada verde." + "')")


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
        # bloque de notas → FASE 137 (sustitución ASERTADA — lección r33).
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
            f'notas={notas_ok} · linea_final={linea_ok}.')
    print(f"\nrelease-v36135 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36135/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
