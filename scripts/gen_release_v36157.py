#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.157-SDK6 (r66).
Crea scripts/release-v36157/ a partir de scripts/release-v36156/ (patrón de
la casa — el release de la ronda anterior es la base; los tokens re-sellan
de una pasada y las notas se sustituyen por las de FASE 160, con ABORTE
DURO si los marcadores no casan — lección r33).
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 160
    (BOLA LOCA + SOLO 1 SUPERPODER EN MARCHA)
  · el candado del hub añade v36156-sdk6 a la lista de versiones viejas
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36157 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36157.py
    python3 scripts/release-v36157/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
ORIGEN = RAIZ / "scripts" / "release-v36156"
DEST = RAIZ / "scripts" / "release-v36157"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 160 — BOLA LOCA + SOLO 1 SUPERPODER EN",
    "MARCHA: dos peticiones del dueño).",
    "  · 1 · REGLA DEL DUEÑO: «el jugador solo pueda lanzar un superpoder",
    "    de pala de cada vez… si un superpoder de pala está activo SOLO",
    "    cuando este se termine podrá aplicar otro. Solo 1 superpoder puede",
    "    estar ejecutándose al mismo tiempo» — helper _poderVivoAlguno() (la",
    "    mesa de relojes que gobierna updateMega con la puerta única pwViva",
    "    y que recoge _dlVentanasApaga) y los DOS gatillos (megaTrigger y",
    "    _dlTrigger) bloquean un poder DISTINTO mientras una ventana corre:",
    "    aviso honesto «Ya hay un superpoder activo» y CERO consumo. El",
    "    MISMO poder se refresca (patrón imán r57) y la MEGA se alarga.",
    "  · 2 · BOLA LOCA (15.º poder): «Se trata del superpoder que usa",
    "    Wizard en el campeonato de la Magia, la bola grande que cambia de",
    "    colores y modifica su trayectoria ligeramente de forma aleatoria.",
    "    Lo llamaremos Bola Loca, durará 10 segundos» — los parámetros",
    "    EXACTOS del mago (LOCA_BALL de magia): bola ×1,65 con el radio",
    "    físico DIMS.ballRadius acompañando, ciclo arcoíris HSL 0,30",
    "    vueltas/s (0.9/0.58 + emissive 0.22), vaivén sinusoidal 4 m/s² a",
    "    8,5 rad/s y ráfagas aleatorias de 2,5 m/s² cada 0,22 s. Icono DEL",
    "    DUEÑO (SuperPala_BolaLoca.png cuantizado a 64 colores) y voces",
    "    Piper NATIVAS de la casa (es_ES-davefx ¡Bola loca! / en_US-lessac",
    "    Crazy ball!) — mismo contrato data-URI que el registro. Anuncio",
    "    con la MISMA voz del sistema: concesión + selector en campeonatos,",
    "    nombre corto dl_bolaloca en duelos.",
    "  · 3 · SIEMPRE DESBLOQUEADA (regla del dueño): primer puesto de la",
    "    sala Arcana SIN candado — la galería ABRE en ella",
    "    (_arconoEntrar → findIndex bolaloca) y poderesDesbloqueados la",
    "    SIEMBRA de serie (se auto-persiste). En DUELOS LOCOS disponible de",
    "    INICIO (surto = base + desbloqueados) y la vieja loca de spin ×2",
    "    (anunciada BOLA LOCA) SALE del surto para no duplicar el nombre —",
    "    sigue VIVA en recepción para rivales con build anterior. El sorteo",
    "    aleatorio de la coronación la EXCLUYE sola (ya no está con",
    "    candado). En campeonatos: un superpoder más (el sorteo de cargas",
    "    la puede conceder). La voz de la sala Arcana presenta la ficha",
    "    como siempre (galería data-driven del registro).",
    "  · 4 · PUERTA CONSERVADORA (la del crono, r26b): la deriva y el",
    "    radio físico SOLO en partida local (campeonato contra la IA — su",
    "    predicción lee DIMS en vivo, lección v2.72 de magia); en online la",
    "    bola crece y cicla de color (visual, tu mitad) y la física NUNCA",
    "    se toca — una deriva aleatoria no puede viajar en el HIT/HANDOFF",
    "    sin romper el fantasma (r54: cero códec nuevo).",
    "  · 5 · QA: agujas r66 sobre el ensamblado (199 verdes, cadena de",
    "    conservación r55-r65 íntegra incluida) · qa_bolaloca_v36157.py",
    "    NUEVO: 79 OK · 0 fallos (60 agujas de fuente + 19 mecánicas",
    "    headless: siembra, exclusión del sorteo, bloqueo del otro poder",
    "    sin consumo, refresco del mismo, bola ×1,65, deriva viva, ciclo",
    "    de color, fin natural y restauración exacta) · qa_version",
    "    re-anclada al sello vivo v36157 (lección: el deploy de r65 había",
    "    dejado el check del hub mirando a v36154) · física determinista",
    "    12/0 · manifiestos 29/0 · presupuesto 10/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sin una línea",
    "    cambiada; cero cambios de códec (PROTO 3); el guardián online y",
    "    el validador §12 ni se enteran.",
    "  SE CONSERVA TODO: la ola data-driven completa (ARCANO_CFG r55,",
    "    CONFIG_MENU r58, CONFIG_AUDIO r59, CONFIG_DIFICULTAD r60,",
    "    CONFIG_TORNEOS+CONFIG_LOGROS r61, CONFIG_PIELES r62, CONFIG_RALLY",
    "    r63, CONFIG_MEDALLAS r64), el blindaje del saque r65, la vitrina",
    "    del cielo r45, el suelo de destellos r43, el duelo honesto y la",
    "    física en tiempo real, multijugador r37/r36, CRAZY LINK v2, ELO,",
    "    matchmaking, el taller UGC, la PWA, el PRO TRAINING y halloween.",
    "  · sellada a",
    "  3.6.157",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36156", "release-v36157"),
    ("staging-v36156", "staging-v36157"),
    ("V3.6.156-SDK6", "V3.6.157-SDK6"),
    ("3.6.156-SDK6", "3.6.157-SDK6"),
    ("v36156-sdk6", "v36157-sdk6"),
    ("v36156", "v36157"),
    ("3.6.156", "3.6.157"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas del
# v36156 son las de FASE 159; los tokens ya convirtieron el «3.6.156» final
# del bloque en «3.6.157» — el FIN busca el estado POST-tokens).
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 159 — EL SAQUE VUELVE A LA MANO: blindaje"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.157" + NL + "'")

HUB_VIEJO = ("'v36154-sdk6' in hub")
HUB_NUEVO = ("'v36154-sdk6' in hub or 'v36156-sdk6' in hub")

FIN_PRINT = "')"          # el print heredado termina en verde.') — sin NL previo


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    notas_ok = 0
    linea_ok = 0
    hub_ok = 0
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
        # bloque de notas → FASE 160 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        # línea final del build → resumen FASE 160.
        i2 = txt.find("print('" + NL + "V3.6.157-SDK6 lista: EL SAQUE")
        if i2 >= 0:
            f2 = txt.find(FIN_PRINT, i2)
            nueva = ("print('" + NL +
                     "V3.6.157-SDK6 lista: BOLA LOCA + SOLO 1 SUPERPODER EN "
                     "MARCHA — la original del Wizard de magia como 15.º "
                     "poder (bola ×1,65 arcoíris con deriva aleatoria del "
                     "mago · 10 s · icono del dueño y voces Piper nativas · "
                     "siempre desbloqueada: primer puesto del Arcano sin "
                     "candado, Duelos Locos de inicio y excluida del sorteo "
                     "de coronación) y la regla del dueño de un solo "
                     "superpoder a la vez (los dos gatillos leen "
                     "_poderVivoAlguno); conservación r55-r65 íntegra." +
                     FIN_PRINT)
            txt = txt[:i2] + nueva + txt[f2 + len(FIN_PRINT):]
            linea_ok = 1
        # candado del hub: v36156 pasa a la lista de versiones viejas.
        if HUB_VIEJO in txt:
            txt = txt.replace(HUB_VIEJO, HUB_NUEVO, 1)
            hub_ok = 1
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36157 · {tocados} ficheros re-sellados · '
          f'notas FASE 160 {notas_ok}/1 · línea final {linea_ok}/1 · '
          f'candado hub {hub_ok}/1')


if __name__ == '__main__':
    main()
