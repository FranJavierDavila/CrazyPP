#!/usr/bin/env python3
"""gen_release_v3677 — hereda scripts/release-v3676 → scripts/release-v3677
e inserta las NOTAS de la FASE 79 «HALLOWEEN + TALLER UGC» en build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3677 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3676"
DEST = RAIZ / "scripts" / "release-v3677"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 78 — DUELOS LOCOS: «Vamos con 2 y 3» — el" + NL + "'"
BLOQUE_VIEJO_FIN = ("    '    campeonatos, 5 poderes, CCD, CRAZY TV y el Hall Of Fame)." + NL + "'"
                    + chr(10) + "    '" + NL + "'")

# líneas de texto PLANO de las notas FASE 79 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 79 — HALLOWEEN + TALLER UGC: «Perfecto.",
    "    'Vamos con varias tareas» — el campeonato del Valle Neón se RETIRA a",
    "    'petición del dueño y su hueco lo ocupa el Campeonato de HALLOWEEN con",
    "    'el ZOMBI del artista, se sube la dificultad del Reto Diario poco a",
    "    'poco y nace EL TALLER UGC, el editor de etapas y campeonatos.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.76-SDK6):",
    "    '",
    "    '  · CAMPEONATO DE HALLOWEEN: el rival ZOMBI con las DOCE POSES del",
    "    '    artista (upload/zombi.zip, 512×1024 con alfa real, conversión a",
    "    '    webp ~100 KB cada una; el borde opaco del idle limpiado por la",
    "    '    regla de oro). Camino de 5 etapas: Duelo en la Niebla → La",
    "    '    Cripta Sellada → Duelo de la Luna → El Pozo del Cometa → DUELO",
    "    '    FINAL (patrón canónico, jefe en el final).",
    "    '",
    "    '  · MAPA DEL ARTISTA (upload/Mapa.png 1380×752 → mapa.webp): los",
    "    '    CINCO MEDALLONES del camino medidos sobre el arte (148,392 ·",
    "    '    355,592 · 875,202 · 890,556 · 1265,332) con anillo de rejugada",
    "    '    por nodo; las tumbas 1-4 y el zombi aullante cuentan el camino.",
    "    '",
    "    '  · CARTEL DE NORMAS DEL ARTISTA (upload/zombi_normas.png →",
    "    '    normas_halloween.png): nueva skin en NORMAS_SKIN.defs con el",
    "    '    hueco interior medido (166..906 × 122..454) — las NORMAS de las",
    "    '    etapas 2 y 4 se pintan SOBRE el arte real del dueño, y el filtro",
    "    '    de showInstrucciones ahora acepta CUALQUIER campeonato con cartel",
    "    '    del artista (los UGC futuros heredan la vía).",
    "    '",
    "    '  · MECÁNICAS DE LAS ETAPAS 2 Y 4 POR DEFINIR (lo dicho por el",
    "    '    dueño): hoy son dianas provisionales y las normas llevan la nota",
    "    '    «Mecánica secreta de esta prueba: por anunciar». La sala es",
    "    '    PROVISIONAL (cementerio procedimental — el escenario real y los",
    "    '    4 troqueles llegan en la siguiente tanda, igual que la música).",
    "    '",
    "    '  · DIFICULTAD DEL RETO DIARIO ESCALONADA (petición del dueño:",
    "    '    «subir la dificultad del Reto Diario poco a poco», ya anticipada",
    "    '    en r80). UN solo mando central (DAILY_DIF): el reto del día sigue",
    "    '    siendo IGUAL para toda la academia, pero su objetivo crece +1",
    "    '    seguida cada 14 días desde el 1-NOV con tope +3. Entrenamiento",
    "    '    libre intacto: manda el objetivo base del modo.",
    "    '",
    "    '  · EL TALLER UGC (editor de etapas y campeonatos, herramienta",
    "    '    APARTE en /ugc): carga un manifest.json o nace de plantilla,",
    "    '    edita identidad, rival y poses, CAMINO de etapas (añadir/quitar/",
    "    '    reordenar duelos y pruebas con sus rules), MAPA con PICADO DE",
    "    '    NODOS por clic sobre el póster, poderes, sala, decorado,",
    "    '    coronación y textos i18n; VALIDA (ids únicos, kinds, nodos ==",
    "    '    etapas, assets) y exporta el manifest.json listo para instalar.",
    "    '    Sin dependencias, todo local, con guía de los 4 pasos incluida.",
    "    '",
    "    '  · NÚCLEO: CHAMP_STAGE_TOTAL halloween:5 (valle_neon fuera),",
    "    '    CHAMPS_DIA con HALLOWEEN y el cartel del campeonato con el total",
    "    '    REAL de etapas (plantilla: adiós al «/5» fijo).",
    "    '",
    "    'Hereda de V3.6.76 (FASE 78: duelos locos con tres poderes y el Reto",
    "    'Diario en la puerta; r79-r71: CRAZY LINK v2, academia en tus manos,",
    "    'AJUSTES por subcategorías, passthrough en caliente; 5 campeonatos, 5",
    "    'poderes, CCD, CRAZY TV y el Hall Of Fame).",
    "    '",
]

def _construir_bloque():
    partes = []
    for ln in _NOTAS:
        partes.append(ln + NL + "'")
    return chr(10).join(partes) + chr(10)


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3676 → v3677 / V3.6.76 → V3.6.76
    txt = txt.replace("V3.6.76-SDK6", "V3.6.77-SDK6")
    txt = txt.replace("3.6.76-SDK6", "3.6.77-SDK6")   # guards contra game_src
    txt = txt.replace("v3676-sdk6", "v3677-sdk6")
    txt = txt.replace("release-v3676", "release-v3677")
    txt = txt.replace("staging-v3676", "staging-v3677")
    txt = txt.replace('grep -c "3.6.76"', 'grep -c "3.6.77"')
    txt = txt.replace("menciones 3.6.76", "menciones 3.6.77")
    txt = txt.replace("no es el v3676", "no es el v3677")
    txt = txt.replace("n3676 = int", "n3677 = int")
    txt = txt.replace("{n3676}", "{n3677}")
    txt = txt.replace("if n3676 < 4:", "if n3677 < 4:")

    # 2 · notas: bloque FASE 78 → bloque FASE 79
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 78 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + _construir_bloque() + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.77-SDK6'" in txt, "guard VERSION"
    assert "V3.6.77-SDK6" in txt, "badge"
    assert "FASE 79" in txt, "notas FASE 79"
    assert "FASE 78 —" not in txt, "quedan notas FASE 78"
    print("✓ release-v3677 creada (notas FASE 79, guards V3.6.77-SDK6)")


if __name__ == "__main__":
    main()
