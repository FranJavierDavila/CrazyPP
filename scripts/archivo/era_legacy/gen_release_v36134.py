#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.134-SDK6 (r38).
Crea scripts/release-v36134/ a partir de scripts/release-v36133/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 136
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36134 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36134.py
    python3 scripts/release-v36134/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36133"
DEST = RAIZ / "scripts" / "release-v36134"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 136 — EL SALÓN DE LA PARTIDA: RASCACIELOS,",
    "el 4.º salón del dueño con el material «rascacielos.zip +",
    "rascacielos.mp3», y las PARTIDAS EN EL HALL DEL ANFITRIÓN — contra la",
    "IA y en multijugador; petición del dueño: «te doy material para un",
    "nuevo hall, «Rascacielos» rascacielos.zip y su melodía",
    "rascacielos.mp3. Mismo comportamiento que el resto de halls. Vamos a",
    "permitir que las partidas se realicen en el hall que tenga configurado",
    "el anfitrión, tanto para las modalidades contra la IA como en el modo",
    "multijugador»).",
    "  · 1 · RASCACIELOS, 4.º SALÓN DEL DUEÑO (c02/c08/c00): los 6 JPG del",
    "    ZIP byte-exactos en las medidas EXACTAS de la spec (frente/fondo",
    "    1849×864 · laterales 2395×864 · suelo/techo 1296×1678) y SU pista",
    "    rascacielos.mp3 junto a su arte; variante en HALL_VARIANTES con",
    "    candado hito_won25 (25 victorias — un rascacielos se construye",
    "    victoria a victoria), i18n ES/EN completo (nombre + hint +",
    "    candado) y mobiliario 3D propio: dos torres con ventanas",
    "    encendidas (emisivo cálido) y baliza roja que PARPADEA en la",
    "    antena (flicker de updateHallFx — el mobiliario vive como el",
    "    resto de salones). Música ambiental al abrir (prioridad de la",
    "    r32) e icono de mute en la pared, igual que Dojo/Neón/Observatorio.",
    "  · 2 · EL SALÓN DE LA PARTIDA (c12/c08/c09): cada partida nueva",
    "    (menú, revancha, cambio de modo, online, reinicio del over,",
    "    vuelta del hall) se disputa EN EL HALL CONFIGURADO POR EL",
    "    ANFITRIÓN — local: TU variante validada; online: la del",
    "    ANFITRIÓN, viajada en hp.hv (HELLO) y en el evento FIABLE hallv",
    "    (cambios de salón EN VIVO, sin recargar). createChampRoom estrena",
    "    la TERCERA fuente de arte por cara (campeonato → salón del",
    "    anfitrión → arte por defecto) con carga perezosa a prueba de",
    "    fallos (una ficha que no llega cae a la fuente siguiente y el",
    "    juego SIGUE); la pista nace por el PUNTO ÚNICO del árbitro",
    "    (onMatchStart), idempotente; en campeonato calla (SU BSO) y en la",
    "    estancia manda enterHall. Id desconocido NO viste (saneo estricto",
    "    contra el catálogo); build viejo del anfitrión: cancha clásica",
    "    (JSON tolerante). El mute sigue siendo el de siempre (icono de la",
    "    pared, persistente).",
    "  · 3 · QA: test_r38_rascacielos_v36134 NUEVO 51/0 (6 JPG byte-exacto",
    "    contra el ZIP, pista byte-exacto, catálogo/candado/i18n, cadena",
    "    efectiva por cara, resolución local/anfitrión, punto único",
    "    onMatchStart, evento fiable hallv, saneo estricto) · regresión",
    "    re-anclada (sella_r38_viva): r37 46/0 · r36 30/0 · r35 36/0 ·",
    "    r34 61/0 · r32 49/0 · r31 47/0 · r30 54/0 · r24 89/0 ·",
    "    test_red_nucleo (PPNET) 60/0 · estilos 66 parejas distinguibles.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: multijugador r37 (reinicio ICE real, ack",
    "    monotono u16, hangup i18n) y r36 (ventana viva, pausa legal,",
    "    eventos sin fantasmas), Prisma visible r35 (bola arcoíris),",
    "    fixes r34 (Red en rig, voz de los 14, Electricidad con",
    "    retención, Prisma por campos), lote aprobado r33, salones del",
    "    dueño r32 con su música, higiene Fénix r31, Fénix jugable r30,",
    "    Súper Oscuridad, Crono, voces Piper, iconos del dueño, bola",
    "    atractora r26b, barrera eléctrica, FORO3D r27, skins r21,",
    "    cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2, ELO,",
    "    matchmaking, halloween.",
    "  · sellada a",
    "  3.6.134",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36133", "release-v36134"),
    ("staging-v36133", "staging-v36134"),
    ("V3.6.133-SDK6", "V3.6.134-SDK6"),
    ("3.6.133-SDK6", "3.6.134-SDK6"),
    ("v36133-sdk6", "v36134-sdk6"),
    ("v36133", "v36134"),
    ("3.6.133", "3.6.134"),
    ("fase 135", "fase 136"),
    ("FASE 135", "FASE 136"),
    ("Fase 135", "Fase 136"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36133 son las de la r37, ya re-selladas a FASE 136 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 136 — REVISIÓN DEL MULTIJUGADOR II: la"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.134" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.134-SDK6 lista: revisión II del multijugador — "
                     "el reinicio de ICE ahora renegocia de verdad (además del silencio "
                     "tolerante mientras vuela), el ack sólo avanza y la envoltura u16 de "
                     "los seqs ya no ciega acks ni pérdida; batería multi en vivo 3/3." + "')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.134-SDK6 lista: el salón de la partida — "
                     "RASCACIELOS como 4.º salón del dueño (arte byte-exacto con SU pista "
                     "y su baliza) y las partidas EN EL HALL DEL ANFITRIÓN, contra la IA "
                     "y en multijugador (hallv fiable en vivo); test r38 51/0 y regresión "
                     "re-anclada verde." + "')")


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
        # bloque de notas → FASE 136 (sustitución ASERTADA — lección r33).
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
    print(f"\nrelease-v36134 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36134/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
