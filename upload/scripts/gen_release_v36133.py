#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.133-SDK6 (r37).
Crea scripts/release-v36133/ a partir de scripts/release-v36132/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 135
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36133 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36133.py
    python3 scripts/release-v36133/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36132"
DEST = RAIZ / "scripts" / "release-v36133"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 135 — REVISIÓN DEL MULTIJUGADOR II: la",
    "segunda pasada pedida por el dueño «no me fío, pasa otra revisión a",
    "fondo del juego en red multijugador», leída de nuevo c09 entera (2.296",
    "líneas), c09b (926), el glue online de c12 y el árbitro de c06).",
    "  · 1 · BUG D · REINICIO DE ICE MUERTO (c09 frame): el watchdog de la",
    "    r125 llamaba pc.restartIce(), que SÓLO arma una bandera interna del",
    "    agente ICE — sin una oferta nueva (createOffer iceRestart →",
    "    setLocal → «sdp») el ICE NUNCA se renegociaba: un enlace que moría",
    "    a mitad de partida (Wi-Fi→LTE, router que cambia la ruta) se",
    "    quedaba helado hasta que el silencio de 12 s mataba la partida.",
    "    FIX: el INVITADO renegocia DE VERDAD por la señalización viva",
    "    (PeerJS) y el anfitrión responde por el camino que ya existía",
    "    (_v2RemoteDesc: setRemoteDescription + answer). Sólo el invitado",
    "    ofrece (sin glare SDP si el enlace muere para los dos a la vez) y",
    "    el reinicio refresca los candidatos de AMBOS extremos. Con el",
    "    reinicio EN VUELO (<15 s desde el intento) el silencio tolerado",
    "    sube a 25 s para que el apretón de manos real (2-6 s) llegue a",
    "    tiempo; sin reinicio ni pausa: 12 s de siempre.",
    "  · 2 · BUG E · ACK REGRESIVO Y CIEGO EN LA ENVOLTURA (c09",
    "    _onAckFrom/_ackCovers/_myAckBits/_trackLoss/_lossWin): el ack se",
    "    colocaba SIN CONDICIÓN — en el canal sin orden, un paquete viejo",
    "    que llegaba tarde movía _ackP hacia ATRÁS y la máscara dejaba de",
    "    cubrir los seqs recientes (el rival retransmitía eventos YA",
    "    entregados). Y la aritmética usaba el wrapDiff u32 del RELOJ sobre",
    "    seqs u16: en el giro 0xffff→0 los acks, la máscara y la medición",
    "    de pérdida quedaban CIEGOS media vuelta del contador (~18 min a",
    "    60 Hz — una partida larga lo cruza). FIX: el ack sólo avanza con",
    "    la helper NUEVA _seqDiff (envoltura u16 con signo), aplicada a los",
    "    cinco puntos que comparan seqs.",
    "  · 3 · BUG F · COLGADO EN ESPAÑOL (c09 hangup): el texto «Has cerrado",
    "    la conexión» viajaba hardcodeado — un jugador en inglés cerraba su",
    "    sala y leía español. FIX: T(«bye_self») con clave ES/EN.",
    "  · 4 · QA: test_r37_red_v36133 46/0 (agujas + aritmética real del",
    "    silencio dinámico y del ack monotono u16, con el wrap ciego de la",
    "    aritmética vieja reproducido) · BATERÍA MULTI EN VIVO (3 parejas",
    "    completas, PeerJS real + NETSIM, en solitario — lección r36):",
    "    P1 LAN 67/0 · P2 WIFI 2 % con relojes desiguales 68/0 · P3 TÚNEL",
    "    con ICE ROTO 69/0 — marcador espejado, rotación de saque,",
    "    HANDOFF→AUTH, 0 rechazos del validador, 0 pageerrors ·",
    "    test_red_nucleo (PPNET) 60/0 · regresión re-anclada (sella_r37",
    "_viva): r36 30/0 · r35 36/0 · r34 61/0 · r33 77/0 · r32 49/0 ·",
    "    r31 47/0 · r30 54/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: multijugador r36 (ventana viva, pausa legal,",
    "    eventos sin fantasmas), Prisma visible r35 (bola arcoíris), fixes",
    "    r34 (Red en rig, voz de los 14, Electricidad con retención y fin",
    "    por baja, Prisma por campos), lote aprobado r33, salones del dueño",
    "    r32 con su música, higiene Fénix r31, Fénix jugable r30, Súper",
    "    Oscuridad, Crono, voces Piper, iconos del dueño, bola atractora",
    "    r26b, barrera eléctrica, FORO3D r27, skins r21, cortina etapas",
    "    2/4, _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.133",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36132", "release-v36133"),
    ("staging-v36132", "staging-v36133"),
    ("V3.6.132-SDK6", "V3.6.133-SDK6"),
    ("3.6.132-SDK6", "3.6.133-SDK6"),
    ("v36132-sdk6", "v36133-sdk6"),
    ("v36132", "v36133"),
    ("3.6.132", "3.6.133"),
    ("fase 134", "fase 135"),
    ("FASE 134", "FASE 135"),
    ("Fase 134", "Fase 135"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36132 son las de la r36, ya re-selladas a FASE 135 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 135 — REVISIÓN DEL MULTIJUGADOR: 3 BUGS"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.133" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.133-SDK6 lista: multijugador revisado — "
                     "pérdida por ventana viva (adiós al 30 Hz vitalicio), pausa legal "
                     "que no muere a los 12 s y eventos sin fantasmas; batería multi "
                     "en vivo 3/3 parejas (LAN · WIFI · TÚNEL).')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.133-SDK6 lista: revisión II del multijugador — "
                     "el reinicio de ICE ahora renegocia de verdad (además del silencio "
                     "tolerante mientras vuela), el ack sólo avanza y la envoltura u16 de "
                     "los seqs ya no ciega acks ni pérdida; batería multi en vivo 3/3." + "')")


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
        # bloque de notas → FASE 135 (sustitución ASERTADA — lección r33).
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
    print(f"\nrelease-v36133 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36133/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
