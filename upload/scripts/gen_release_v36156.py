#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.156-SDK6 (r65).
Crea scripts/release-v36156/ a partir de scripts/release-v36154/ (patrón de
la casa — el release de la ronda anterior es la base; los tokens re-sellan
de una pasada y las notas se sustituyen por las de FASE 159, con ABORTE
DURO si los marcadores no casan — lección r33).
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 159
    (EL SAQUE VUELVE A LA MANO — blindaje del saque en 4 capas)
  · el candado del hub añade v36154-sdk6 a la lista de versiones viejas
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36156 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36156.py
    python3 scripts/release-v36156/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
ORIGEN = RAIZ / "scripts" / "release-v36154"
DEST = RAIZ / "scripts" / "release-v36156"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 159 — EL SAQUE VUELVE A LA MANO: blindaje",
    "del saque en 4 capas — petición del dueño, MÁXIMA PRIORIDAD: «no se",
    "puede sacar, la pelota aparece detrás del jugador y no en su mano y no",
    "responde a los controles correctamente; por lo visto es solo en el",
    "saque»).",
    "  · 1 · CAPA 1 · GATILLO SAQUE-PRIMERO: en el estado SAQUE del jugador",
    "    el gatillo lanza SIEMPRE y ANTES de gunArmed/replayConsume/",
    "    arkanoid/over — la reordenación que el cartel del superpoder",
    "    (v3.6.35) ya prometía («En el saque el gatillo sigue SIENDO DEL",
    "    SAQUE»). Misma condición que la rama del final: reordenación pura.",
    "  · 2 · CAPA 2 · RESPALDO RELATIVO A LA CABEZA: el punto fijo viejo",
    "    (0,3 · 1,05 · fondo+0,4) podía quedar DETRÁS del jugador (el museo",
    "    mueve el rig y el casco no re-centra al arrancar partida). Ahora",
    "    nace 0,35 m por delante de la mirada y a la altura del pecho.",
    "  · 3 · CAPA 3 · POSE FRESCA + GRIP VIVO: _srvManoValida (pose sellada",
    "    hace <400 ms Y plausible: a <2,2 m de la cabeza) y el saque natural",
    "    por grip ya NO exige hand.active (el evento squeeze es prueba",
    "    vivísima de que el mando responde). Velocidad REAL de la mano",
    "    intacta (requisito A v3.1.0-SRV2).",
    "  · 4 · CAPA 4 · WATCHDOG «LA BOLA SIEMPRE VUELVE A TU MANO»: corre",
    "    FUERA de las guardias del pegado; si el saque se atasca, la bola",
    "    vuelve a la mano libre (pose fresca) o delante de la mirada en ~1 s.",
    "    En el camino feliz es un no-op (<0,45 m cada frame).",
    "  · 5 · LA MISMA ARMADURA en el guardián ONLINE (_bolaGuard r25) — en",
    "    ESCRITORIO (sin visor) el punto reglamentario se queda (r25).",
    "  · 6 · TELEMETRÍA («receptor no responde»): el receptor de producción",
    "    está VIVO (latido 200 OK · CORS * · 419 eventos); el panel",
    "    telemetria.html ahora DICE QUÉ receptor probó («receptor no",
    "    responde · probó <origen><ruta>») para destapar una pp_tele_url",
    "    vieja guardada en localStorage al instante.",
    "  · 7 · QA: batería node con LOS NÚMEROS EXACTOS del estado r64",
    "    (verdes 12/0 · 16/0 · 63/0 · 171/0 · 54/0 · 47/0 · 49/0 · 77/0 ·",
    "    62/0 · 36/0 · 30/0 · 46/0 · 51/0 · 167/0 · 62/0 · 92/0 · TODO OK",
    "    · 55/0 · 60/0; rojos heredados idénticos: r23 81/1 · r25 141/9 ·",
    "    r26 105/4 con GIT_CONFIG por entorno · r27 36/4 · r28 28/9 ·",
    "    r29 68/7 — causas históricas pre-r55, ni una línea de r65 en el",
    "    camino) · python verde (qa_version 31/0 espejos byte-exacto a",
    "    3.6.156 · qa_rendimiento 14/0 · qa_r46_humo OK · qa_sup1 151/0).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256 BYTE-EXACTO",
    "    (d792b5e7 / b195a0db); cero cambios de códec (PROTO 3).",
    "  SE CONSERVA TODO: la ola data-driven completa (ARCANO_CFG r55,",
    "    CONFIG_MENU r58, CONFIG_AUDIO r59, CONFIG_DIFICULTAD r60,",
    "    CONFIG_TORNEOS+CONFIG_LOGROS r61, CONFIG_PIELES r62, CONFIG_RALLY",
    "    r63, CONFIG_MEDALLAS r64), la vitrina del cielo r45, el suelo de",
    "    destellos r43, el duelo honesto y la física en tiempo real,",
    "    multijugador r37/r36, CRAZY LINK v2, ELO, matchmaking, el taller",
    "    UGC, la PWA, el PRO TRAINING y halloween.",
    "  · sellada a",
    "  3.6.156",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36154", "release-v36156"),
    ("staging-v36154", "staging-v36156"),
    ("V3.6.154-SDK6", "V3.6.156-SDK6"),
    ("3.6.154-SDK6", "3.6.156-SDK6"),
    ("v36154-sdk6", "v36156-sdk6"),
    ("v36154", "v36156"),
    ("3.6.154", "3.6.156"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas del
# v36154 son las de CONFIG_RALLY; los tokens ya convirtieron el «3.6.154»
# final del bloque en «3.6.156» — el FIN busca el estado POST-tokens).
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 157 — CONFIG_RALLY: LOS HITOS Y BONOS DEL"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.156" + NL + "'")

HUB_VIEJO = ("if 'v36156-sdk6' not in hub or 'v36139-sdk6' in hub "
             "or 'v3667-sdk6' in hub")
HUB_NUEVO = ("if 'v36156-sdk6' not in hub or 'v36139-sdk6' in hub "
             "or 'v3667-sdk6' in hub or 'v36154-sdk6' in hub")

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
        # bloque de notas → FASE 159 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        # línea final del build → resumen FASE 159.
        i2 = txt.find("print('" + NL + "V3.6.156-SDK6 lista: CONFIG_RALLY")
        if i2 >= 0:
            f2 = txt.find(FIN_PRINT, i2)
            nueva = ("print('" + NL +
                     "V3.6.156-SDK6 lista: EL SAQUE VUELVE A LA MANO — blindaje "
                     "del saque en 4 capas (gatillo saque-primero · respaldo "
                     "relativo a la cabeza · pose fresca y plausible + grip "
                     "vivo · watchdog bola→mano) y la misma armadura en el "
                     "guardián online; telemetría con receptor vivo verificado "
                     "y panel que dice qué receptor probó; conservación "
                     "r55-r64 íntegra." + FIN_PRINT)
            txt = txt[:i2] + nueva + txt[f2 + len(FIN_PRINT):]
            linea_ok = 1
        # candado del hub: v36154 pasa a la lista de versiones viejas.
        if HUB_VIEJO in txt:
            txt = txt.replace(HUB_VIEJO, HUB_NUEVO, 1)
            hub_ok = 1
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36156 · {tocados} ficheros re-sellados · '
          f'notas FASE 159 {notas_ok}/1 · línea final {linea_ok}/1 · '
          f'candado hub {hub_ok}/1')


if __name__ == '__main__':
    main()
