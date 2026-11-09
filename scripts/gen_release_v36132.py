#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.132-SDK6 (r36).
Crea scripts/release-v36132/ a partir de scripts/release-v36131/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 134
    (con ABORTE DURO si los marcadores no casan — lección r33)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36132 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36132.py
    python3 scripts/release-v36132/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36131"
DEST = RAIZ / "scripts" / "release-v36132"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 134 — REVISIÓN DEL MULTIJUGADOR: 3 BUGS",
    "DE RED cazados en la auditoría completa pedida por el dueño",
    "«revisa el funcionamiento de las partidas multijugador por si cazas",
    "algún bug»).",
    "  · 1 · BUG A · LA PÉRDIDA ERA VITALICIA (c09 _trackLoss): el contador",
    "    de huecos acumulaba DE POR VIDA y el denominador se limitaba al",
    "    anillo — tras ~15 paquetes perdidos en TODA la sesión (o UN atasco",
    "    de ICE ≥5 s, que sumaba cientos de huecos de golpe) la pose caía a",
    "    30 Hz PARA SIEMPRE: la recuperación exigía <4 % de pérdida VITAL,",
    "    imposible tras el atasco. «Partida a trompicones» permanente tras",
    "    cualquier susto de Wi-Fi. FIX: ventana VIVA — los huecos que",
    "    cuentan son los DENTRO del anillo (span − recibidos, clamp ≥0 y al",
    "    total contado) y los saltos >64 paquetes son PARADAS (reinicio de",
    "    ICE, pestaña congelada), no pérdida. Verificado con aritmética",
    "    real: atasco de 300 paquetes NO degrada · ráfaga del 20 % degrada",
    "    en su momento y RECUPERA 60 Hz al salir de la ventana · pérdida",
    "    crónica del 12,5 % mantiene la degradación honesta (spec §11).",
    "    netInfo() (HUD/telemetría) enseña la MISMA ventana.",
    "  · 2 · BUG B · LA PAUSA LEGAL MORÍA A LOS 12 s (c09 frame): el rival",
    "    que se quitó el visor AVISA («pause») y al reponerse envía",
    "    «resume» — pero el watchdog de silencio mataba la partida a los",
    "    12 s aunque su pausa fuera de 30 s. FIX: con pausa ANUNCIADA el",
    "    silencio tolerado sube a 60 s (sin pausa anunciada, 12 s de",
    "    siempre — el abandono real se corta igual).",
    "  · 3 · BUG C · EVENTOS FANTASMA DADOS POR ENTREGADOS (c09",
    "    _sendFast/_flushEvents): el paquete fast lleva los 8 PRIMEROS",
    "    eventos pendientes (spec §5) pero el seq se asignaba a TODOS los",
    "    pendientes (hasta 24) — un ack posterior marcaba como entregados",
    "    eventos que JAMÁS viajaron (pérdida silenciosa de HIT/HANDOFF",
    "    bajo acumulación). FIX: seq sólo a los que viajan.",
    "  · 4 · QA: test_r36_red_v36132 30/0 (agujas + aritmética real de la",
    "    ventana) · BATERÍA MULTI EN VIVO (3 parejas completas, PeerJS",
    "    real + NETSIM): P1 LAN 67/0 · P2 WIFI 2 % con relojes desiguales",
    "    68/0 · P3 TÚNEL con ICE ROTO 69/0 — marcador espejado, rotación",
    "    de saque, HANDOFF→AUTH, 0 rechazos del validador, 0 pageerrors ·",
    "    test_red_nucleo (PPNET) 60/0 · regresión re-anclada r35 36/0 ·",
    "    r34 61/0 · r33 77/0 · r32 49/0 · r31 47/0 · r30 54/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: Prisma visible r35 (bola arcoíris), fixes r34",
    "    (Red en rig, voz de los 14, Electricidad con retención y fin por",
    "    baja, Prisma por campos), lote aprobado r33, salones del dueño",
    "    r32 con su música, higiene Fénix r31, Fénix jugable r30, Súper",
    "    Oscuridad, Crono, voces Piper, iconos del dueño, bola atractora",
    "    r26b, barrera eléctrica, FORO3D r27, skins r21, cortina etapas",
    "    2/4, _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.132",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36131", "release-v36132"),
    ("staging-v36131", "staging-v36132"),
    ("V3.6.131-SDK6", "V3.6.132-SDK6"),
    ("3.6.131-SDK6", "3.6.132-SDK6"),
    ("v36131-sdk6", "v36132-sdk6"),
    ("v36131", "v36132"),
    ("3.6.131", "3.6.132"),
    ("fase 133", "fase 134"),
    ("FASE 133", "FASE 134"),
    ("Fase 133", "Fase 134"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36131 son las de la r35, ya re-selladas a FASE 134 por los tokens):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 134 — PRISMA VISIBLE: LA BOLA ARCOÍRIS,"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.132" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.132-SDK6 lista: el Prisma SE VE — la bola "
                     "pinta arcoíris aleatorio mientras la ventana vive y la devuelve "
                     "intacta al morir (cesión Oscuridad y auto-soltado incluidos).')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.132-SDK6 lista: multijugador revisado — "
                     "pérdida por ventana viva (adiós al 30 Hz vitalicio), pausa legal "
                     "que no muere a los 12 s y eventos sin fantasmas; batería multi "
                     "en vivo 3/3 parejas (LAN · WIFI · TÚNEL).')")


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
        # bloque de notas → FASE 134 (sustitución ASERTADA — lección r33).
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
    print(f"\nrelease-v36132 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36132/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
