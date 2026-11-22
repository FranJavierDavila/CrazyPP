#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.158-SDK6 (r67).
Crea scripts/release-v36158/ a partir de scripts/release-v36157/ (patrón de
la casa — el release de la ronda anterior es la base; los tokens re-sellan
de una pasada y las notas se sustituyen por las de FASE 161, con ABORTE
DURO si los marcadores no casan — lección r33).
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 161
    (EL VESTÍBULO — rediseño de los menús principales)
  · el candado del hub añade v36157-sdk6 a la lista de versiones viejas
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36158 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36158.py
    python3 scripts/release-v36158/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
ORIGEN = RAIZ / "scripts" / "release-v36157"
DEST = RAIZ / "scripts" / "release-v36158"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 161 — EL VESTÍBULO: rediseño de los menús",
    "principales del juego y sus apartados, petición del dueño).",
    "  · 1 · LA PÁGINA PRINCIPAL (la página «main») SE CONVIERTE EN EL VESTÍBULO:",
    "    TRES paneles de cristal en arco (JUGAR al centro con el héroe",
    "    ▶ PARTIDO + Carrera + Entrenar/Superivencia en par · COMPITE a la",
    "    izquierda con Multijugador/Campeonatos/Ranking Mundial · TU CASA a",
    "    la derecha con Volver al Hall/Academia/Ajustes) + dock inferior de",
    "    utilidades (TV en vivo · Intro · Instalar · Apoyar · Salir a la",
    "    web) + cabecera con el logo, las palas de idioma ES/EN (reutilizan",
    "    _langPaddle y su id «lang:xx») y el sello de versión. Estilo",
    "    «caramelo» calcado de la referencia del dueño (Menú de ping-pong",
    "    futurista sin texto.png): gradiente glossy + aro oscuro + brillo",
    "    superior + medallón circular por icono; los subtítulos vivos son",
    "    los del «main» de r111-r115.",
    "  · 2 · TODO DATA-DRIVEN (petición del dueño: «haz que los menús sean",
    "    también data-driven por si más adelante personalizamos los iconos",
    "    de los botones»): ICONOS_MENUS (registro de los 17 iconos del set",
    "    «CRAZY ICONOS v1» diseñados a mano — SVG 96×96 → PNG 256 px con",
    "    cairosvg, cuantizados a 64 colores, 344 KB base64; sistema común:",
    "    glifo blanco + sub-trazo oscuro + acento con degradado del color",
    "    de su tarjeta + brillo especular) y CONFIG_MENUS (lienzo,",
    "    cabecera, paneles, tarjetas con id/icono/etiquetaKey/gradiente,",
    "    dock) — AMBAS en c02 junto a CONFIG_MENU r58. Cambiar un icono =",
    "    editar una data-URI; reordenar/recolorar = editar la tabla; cero",
    "    lógica. Los subtítulos vivos (división, racha, online, coronas,",
    "    ajustes) los resuelve _vestSubPorId con las MISMAS expresiones del",
    "    HUB de r111-r115.",
    "  · 3 · GEOMETRÍA: lienzo PANORÁMICO 2560×1440 (16:9) sobre plano",
    "    1,60×0,90 m (antes 1024×1536 sobre 0,90×1,35) — los tres paneles",
    "    caben en el FOV a 1,08 m y la densidad sube a ~1600 texel/m (más",
    "    nitidez, sin mips como r105). El rayo lee VIVO this.menuCanvas y",
    "    geometry.parameters (el FIX DERIVA r105 se vuelve estructural: no",
    "    hay literales que desincronizar). Chincheta re-anclada a 0,482.",
    "  · 4 · CONSERVACIÓN DEL LEGADO: las 15 páginas 1024×1536 se pintan",
    "    ESCALADAS (0,9375) y CENTRADAS (dx 800) sobre el lienzo nuevo con",
    "    transform por repintado (reset identidad al inicio de drawMenu —",
    "    cero fugas) y TODOS sus rects mapeados al lienzo (btn + _mapRect en",
    "    _langPaddle, retoDiario, _modeCard, carrera sel/des, ppchamp y",
    "    sliders). El despacho de acciones es INTACTO (ids idénticos); el",
    "    medallón del pulso r87 vive en el Vestíbulo (save/reset/restore);",
    "    el dock reutiliza los botones DOM de SIEMPRE (introbtn/pwabtn/",
    "    kofibtn/tvlink — cero duplicación de flujos); QA",
    "    qa_vestibulo_r67.py: 49 OK · 0 fallos (35 agujas + 14 mecánicas",
    "    headless: lienzo/plano vivos, 18 ids del Vestíbulo, rects en",
    "   _bounds, navegación main→opts→main→train, dock que cierra, iconos",
    "    decodificados 15/15) + capturas reales del lienzo (main y opts).",
    "  · 5 · SIN TOCAR: física (c04/c05), saque r65, campeonatos, Arcano,",
    "    Duelos Locos, voces, telemetría, PWA. El Hub de r111-r115 queda en",
    "    la fuente como referencia histórica y generador de subtítulos.",
    "  SE CONSERVA TODO: la ola data-driven completa (ARCANO_CFG r55,",
    "    CONFIG_MENU r58, CONFIG_AUDIO r59, CONFIG_DIFICULTAD r60,",
    "    CONFIG_TORNEOS+CONFIG_LOGROS r61, CONFIG_PIELES r62, CONFIG_RALLY",
    "    r63, CONFIG_MEDALLAS r64), el blindaje del saque r65, BOLA LOCA +",
    "    regla solo-1 r160, el Hall de FASE 29, la vitrina del cielo r45,",
    "    el suelo de destellos r43, el duelo honesto y la física en tiempo",
    "    real, multijugador r37/r36, CRAZY LINK v2, ELO, matchmaking, el",
    "    taller UGC, la PWA, el PRO TRAINING y halloween.",
    "  · sellada a",
    "  3.6.158",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36157", "release-v36158"),
    ("staging-v36157", "staging-v36158"),
    ("V3.6.157-SDK6", "V3.6.158-SDK6"),
    ("3.6.157-SDK6", "3.6.158-SDK6"),
    ("v36157-sdk6", "v36158-sdk6"),
    ("v36157", "v36158"),
    ("3.6.157", "3.6.158"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas del
# v36157 son las de FASE 160; los tokens ya convirtieron el «3.6.157» final
# del bloque en «3.6.158» — el FIN busca el estado POST-tokens).
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 160 — BOLA LOCA + SOLO 1 SUPERPODER EN"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.158" + NL + "'")

HUB_VIEJO = ("'v36154-sdk6' in hub or 'v36156-sdk6' in hub")
HUB_NUEVO = ("'v36154-sdk6' in hub or 'v36156-sdk6' in hub or 'v36157-sdk6' in hub")

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
        # bloque de notas → FASE 161 (sustitución ASERTADA — lección r33).
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            f = txt.find(FIN_MARCADOR, i)
            if f < 0:
                raise SystemExit('ABORTE: FIN_MARCADOR no hallado tras INI')
            txt = txt[:i] + _NOTAS + txt[f + len(FIN_MARCADOR):]
            notas_ok = 1
        # línea final del build → resumen FASE 161.
        i2 = txt.find("print('" + NL + "V3.6.158-SDK6 lista: BOLA LOCA")
        if i2 >= 0:
            f2 = txt.find(FIN_PRINT, i2)
            nueva = ("print('" + NL +
                     "V3.6.158-SDK6 lista: EL VESTÍBULO — los menús "
                     "principales redisenados al estilo caramelo de la "
                     "referencia del dueño (3 paneles de cristal "
                     "JUGAR/COMPITE/TU CASA + dock de utilidades + cabecera "
                     "con logo y palas de idioma + 17 iconos del set CRAZY "
                     "ICONOS v1 diseñados a mano), TODO data-driven "
                     "(ICONOS_MENUS + CONFIG_MENUS en c02), lienzo "
                     "panorámico 2560×1440 con rayo vivo y las 15 páginas "
                     "legadas escaladas y mapeadas; conservación r55-r66 "
                     "íntegra." +
                     FIN_PRINT)
            txt = txt[:i2] + nueva + txt[f2 + len(FIN_PRINT):]
            linea_ok = 1
        # candado del hub: v36157 pasa a la lista de versiones viejas.
        if HUB_VIEJO in txt:
            txt = txt.replace(HUB_VIEJO, HUB_NUEVO, 1)
            hub_ok = 1
        if txt != orig:
            p.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f'OK gen_release_v36158 · {tocados} ficheros re-sellados · '
          f'notas FASE 161 {notas_ok}/1 · línea final {linea_ok}/1 · '
          f'candado hub {hub_ok}/1')


if __name__ == '__main__':
    main()
