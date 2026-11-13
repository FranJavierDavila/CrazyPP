#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.154-SDK6 (r63).
Crea scripts/release-v36154/ a partir de scripts/release-v36139/ (SALTO
DIRECTO: los releases dormían desde la v3.6.139 — el dueño lo pidió
explícitamente al ver GitHub parado en v3.6.139 — así que NO se recorre la
cadena 140→154; los tokens re-sellan de una pasada y las notas se
sustituyen por las de FASE 157, con ABORTE DURO si los marcadores no casan
— lección r33).
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 157
    (CONFIG_RALLY — hitos y bonos del rally data-driven)
  · el candado del hub añade v36139-sdk6 a la lista de versiones viejas
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36154 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36154.py
    python3 scripts/release-v36154/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
ORIGEN = RAIZ / "scripts" / "release-v36139"
DEST = RAIZ / "scripts" / "release-v36154"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 157 — CONFIG_RALLY: LOS HITOS Y BONOS DEL",
    "RALLY SON DATA-DRIVEN — octava parada de la ola tras ARCANO_CFG/",
    "física/menú/audio/dificultad/torneos+logros/pieles).",
    "  · 1 · CONFIG_RALLY (c02, al pie tras CONFIG_PIELES): ÚNICA FUENTE",
    "    DE VERDAD DEL RALLY POR MODO — metas [30/50/100 t5a RALLY ·",
    "    20/40/80 t5b LOCO — la máquina del LOCO traiciona cada bola] y",
    "    bonos paralelos de puntos [15/25/50 los dos modos], antes las",
    "    tablas locales RALLY_MILL/RALLY_BONUS de c13 desde M7d (r120).",
    "  · 2 · LECTORES (c13, DOS alias): RALLY_MILL = CONFIG_RALLY.metas ·",
    "    RALLY_BONUS = CONFIG_RALLY.bonos (declarados ANTES de MODES por",
    "    TDZ). Juez del rally, okHit de t5a, estrellas, medallas",
    "    medallaDe y HUD intactos.",
    "  · 3 · DEDUP de la casa: las filas t5a/t5b de MODES leen su",
    "    meta1/bonus1 DE LA TABLA — el objetivo jugable objN y la fila",
    "    de MODES son LA MISMA fila; cero cambios de comportamiento",
    "    (30→30 · 20→20 · 15→15).",
    "  · 4 · La ola data-driven de c13 queda COMPLETA: pieles r62 +",
    "    rally r63 son dato; el comentario FUERA DE ÁMBITO de",
    "    CONFIG_TORNEOS lo sella.",
    "  · 5 · QA: node verde con los seis rojos heredados demostrados",
    "    idénticos al estado r62 (aserciones congeladas de la era",
    "    pre-r55, ni una línea de r63 en el camino) · python 9/9 ·",
    "    qa_version 31/0 (espejos :3000/:81 byte-exacto a 3.6.154) ·",
    "    qa_sup1 151/0 · qa_r46_humo OK · presupuesto: boot a",
    "    __PP_GAME 2,609 ms · 0 pageerrors.",
    "  · 6 · VERIFICACIÓN EN PRODUCCIÓN (prod_smoke_r63.py): 39 OK ·",
    "    0 FALLOS — CONFIG_RALLY servida y leída VIVA (alias de c13 +",
    "    dedup de MODES) y conservación r55-r62 íntegra.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (d792b5e7 / b195a0db); cero cambios de códec",
    "    (PROTO 3).",
    "  SE CONSERVA TODO: la ola data-driven completa (ARCANO_CFG r55,",
    "    CONFIG_MENU r58, CONFIG_AUDIO r59, CONFIG_DIFICULTAD r60,",
    "    CONFIG_TORNEOS+CONFIG_LOGROS r61, CONFIG_PIELES r62), la",
    "    vitrina del cielo r45, el suelo de destellos r43, el duelo",
    "    honesto y la física en tiempo real, multijugador r37/r36,",
    "    CRAZY LINK v2, ELO, matchmaking, el taller UGC, la PWA, el",
    "    PRO TRAINING y halloween.",
    "  · sellada a",
    "  3.6.154",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36139", "release-v36154"),
    ("staging-v36139", "staging-v36154"),
    ("V3.6.139-SDK6", "V3.6.154-SDK6"),
    ("3.6.139-SDK6", "3.6.154-SDK6"),
    ("v36139-sdk6", "v36154-sdk6"),
    ("v36139", "v36154"),
    ("3.6.139", "3.6.154"),
    ("fase 141", "fase 157"),
    ("FASE 141", "FASE 157"),
    ("Fase 141", "Fase 157"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas del
# v36139 son las de la vitrina del cielo, ya re-selladas a FASE 157 por los
# tokens).
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 157 — LA VITRINA DEL CIELO: el candado"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.154" + NL + "'")

HUB_VIEJO = ("if 'v36154-sdk6' not in hub or 'v3667-sdk6' in hub")
HUB_NUEVO = ("if 'v36154-sdk6' not in hub or 'v36139-sdk6' in hub "
             "or 'v3667-sdk6' in hub")

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
        # bloque de notas → FASE 157 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        # línea final del build → resumen FASE 157.
        i2 = txt.find("print('" + NL + "V3.6.154-SDK6 lista: la vitrina")
        if i2 >= 0:
            f2 = txt.find(FIN_PRINT, i2)
            nueva = ("print('" + NL +
                     "V3.6.154-SDK6 lista: CONFIG_RALLY — las metas de los "
                     "hitos (30/50/100 en RALLY · 20/40/80 en LOCO) y sus "
                     "bonos (15/25/50) viven en la tabla c02; juez del rally, "
                     "okHit, estrellas, medallas, HUD y dedup intactos; humo "
                     "de producción 39 OK · 0 FALLOS y conservación r55-r62 "
                     "íntegra." + FIN_PRINT)
            txt = txt[:i2] + nueva + txt[f2 + len(FIN_PRINT):]
            linea_ok = 1
        # candado del hub: v36139 pasa a la lista de versiones viejas.
        if HUB_VIEJO in txt:
            txt = txt.replace(HUB_VIEJO, HUB_NUEVO, 1)
            hub_ok = 1
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36154 · {tocados} ficheros re-sellados · '
          f'notas FASE 157 {notas_ok}/1 · línea final {linea_ok}/1 · '
          f'candado hub {hub_ok}/1')


if __name__ == '__main__':
    main()
