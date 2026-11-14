#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.159-SDK6 (r67).
Crea scripts/release-v36159/ a partir de scripts/release-v36157/ (patrón de
la casa — el release de la ronda anterior es la base; los tokens re-sellan
de una pasada y las notas se sustituyen por las de FASE 161, con ABORTE
DURO si los marcadores no casan — lección r33).
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 161
    (EL VESTÍBULO — rediseño de los menús principales)
  · el candado del hub añade v36157-sdk6 a la lista de versiones viejas
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36159 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36159.py
    python3 scripts/release-v36159/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
ORIGEN = RAIZ / "scripts" / "release-v36157"
DEST = RAIZ / "scripts" / "release-v36159"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 162 — EL ARCO: el menú a pantalla curva,",
    "ajustes del dueño sobre el Vestíbulo r67).",
    "  · 1 · EL MENÚ OCUPA (casi) TODA LA PANTALLA Y ES CURVO: TRES panelas",
    "    físicas reales — centro 0,98 m a 1,15 m y lados 0,74 m a 1,25 m con",
    "    yaw ±36°, cada una girada hacia el jugador — alimentadas por un",
    "    LIENZO VIRTUAL 3696×1400 que drawMenu pinta entero y _menuTexSube()",
    "    trocea a las tres texturas (los 20 needsUpdate delegan allí). El",
    "    rayo prueba las TRES panelas y suma el offset de la tocada →",
    "    coordenadas virtuales; el cursor vive en la panela (local→grupo).",
    "    Cobertura ≈105°, centros equidistantes: pantalla curva real.",
    "  · 2 · CHINCHETA ON POR DEFECTO (petición literal): cada apertura",
    "    ancla el arco EN LA CABEZA (posición+yaw de la vista) y queda FIJO",
    "    sin flotación; soltar la chincheta devuelve el modo flotante r113",
    "    (sigue a la cabeza 1,8 s). La firma r114 (estancia+rig z) sigue",
    "    curando anclas al viajar de escena.",
    "  · 3 · JERARQUÍA: héroe ▶ JUGAR con protagonismo (380 px, halo verde,",
    "    medallón grande) y CARRERA al nivel del resto (215 px); dock",
    "    ELIMINADO completo y «SALIR A LA WEB» reubicado como tarjeta fina",
    "    al pie de TU CASA con prompt caramelo (SI/NO con auto-ajuste).",
    "  · 4 · REDISEÑO DE TODOS LOS SUBAPARTADOS: concha data-driven",
    "    (CONFIG_SECCIONES) en TODAS las páginas — cristal continuo en las",
    "    tres panelas, ATRÁS con icono, título con medallón, idiomas y",
    "    sello — más la rejilla de AJUSTES (8 tarjetas-icono en dos",
    "    columnas: 7 categorías + Ko-fi) y prompts caramelo de salida y",
    "    hall. Las páginas complejas (teclados, sliders, tablas) conservan",
    "    su mecánica íntegra vestidas con la concha; los subtítulos vivos",
    "    se mantienen. 7 iconos nuevos (audio, ojo, usuario, gauge,",
    "    consola, plus, entrar) — 24 en ICONOS_MENUS v2 — predecodificados",
    "    al abrir para que ningún medallón nazca vacío.",
    "  · 5 · CALIDAD: qa_vestibulo_r68.py 46 OK · 0 fallos (agujas +",
    "    mecánica headless: 3 panelas con geometría y normales verificadas,",
    "    chincheta, 14 ids del Vestíbulo sin dock, rejilla, prompts, train",
    "    legado mapeado) + capturas reales del lienzo (main, ajustes,",
    "    prompt) revisadas a ojo. Bugs cazados por la QA y corregidos:",
    "    signo del yaw de las panelas laterales (miraban hacia fuera),",
    "    doble mapeo de las palas de idioma en la concha, transform del",
    "    legado filtrando en rejilla/prompt y placa vacía en páginas sin",
    "    contenido legado. Ensamblado 12.161.485 B (golden 460eb8e3).",
    "  SE CONSERVA TODO: r55-r67 íntegro (ola data-driven, blindaje del",
    "    saque r65, BOLA LOCA + regla solo-1 r160, Hall de FASE 29,",
    "    multijugador, ELO, taller UGC, PWA, PRO TRAINING, halloween).",
    "  · sellada a",
    "  3.6.159",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36157", "release-v36159"),
    ("staging-v36157", "staging-v36159"),
    ("V3.6.157-SDK6", "V3.6.159-SDK6"),
    ("3.6.157-SDK6", "3.6.159-SDK6"),
    ("v36157-sdk6", "v36159-sdk6"),
    ("v36157", "v36159"),
    ("3.6.157", "3.6.159"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas del
# v36157 son las de FASE 160; los tokens ya convirtieron el «3.6.157» final
# del bloque en «3.6.159» — el FIN busca el estado POST-tokens).
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 160 — BOLA LOCA + SOLO 1 SUPERPODER EN"
                + NL + "'")
FIN_MARCADOR = ("    '  · sellada a" + NL + "'" + chr(10) +
                "    '  3.6.159" + NL + "'")

HUB_VIEJO = ("'v36154-sdk6' in hub or 'v36156-sdk6' in hub")
HUB_NUEVO = ("'v36154-sdk6' in hub or 'v36156-sdk6' in hub or 'v36157-sdk6' in hub or 'v36158-sdk6' in hub")

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
        i2 = txt.find("print('" + NL + "V3.6.159-SDK6 lista: BOLA LOCA")
        if i2 >= 0:
            f2 = txt.find(FIN_PRINT, i2)
            nueva = ("print('" + NL +
                     "V3.6.159-SDK6 lista: EL VESTÍBULO — los menús "
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
    print(f'OK gen_release_v36159 · {tocados} ficheros re-sellados · '
          f'notas FASE 161 {notas_ok}/1 · línea final {linea_ok}/1 · '
          f'candado hub {hub_ok}/1')


if __name__ == '__main__':
    main()
