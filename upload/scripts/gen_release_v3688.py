#!/usr/bin/env python3
"""gen_release_v3688 — hereda scripts/release-v3687 → scripts/release-v3688
e inserta las NOTAS de la FASE 90 «SALA Y ESCENA EN VIVO (r96)» en build_zip.py.

Ronda 96, seis frentes del dueño:
 1) SALA Y ESCENA EN VIVO: entrar en la categoría cambia el entorno del
    HALL a la SALA DE PARTIDOS (mesa a la vista) con feedback inmediato.
 2) SALA y MESA como SUBMENÚS-BOTÓN (tarjetas con color e icono).
 3) ALTURA POR DESLIZADOR continuo 70-84 cm (adiós a los 3 presets).
 4) TOOLTIPS del menú (norma general, i18n ES/EN).
 5) SONIDOS sin solapes (etiqueta en su fila) y barras CLICABLES.
 6) PIELES DE MESA SÓLO partidas/entrenamiento (fuera de campeonatos).
 7) AUDITORÍA DE FLUIDEZ: NITIDEZ (FFR) 4 niveles + techo del gobernador
    0,65 (antes 0,8) + Quest 3 nace a fovea 0,35.

Lección de la r93 aplicada: los guards en MINÚSCULA se heredan REEMPLAZADOS
aquí — nada de correcciones post-gen. Idempotente.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3687"
DEST = RAIZ / "scripts" / "release-v3688"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 89 completo en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 89 — AJUSTES DEL DUEÑO (r95). Cuatro" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    r93 50/0 · r92 41/0 · r91 55/0 · r90 66/0 · sup1 151/0)." + NL + "'"

# líneas de texto PLANO de las notas FASE 90 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 90 — SALA Y ESCENA EN VIVO (r96). Seis",
    "    'frentes del dueño en una ronda: la sala de partidos se ve al",
    "    'ajustarla, SALA y MESA con sus botones propios, la altura de mesa",
    "    'pasa a DESLIZADOR continuo, TODO el menú gana tooltips, los",
    "    'sonidos dejan de solaparse, las pieles de mesa quedan FUERA de los",
    "    'campeonatos y una auditoría de fluidez tunde el foveado agresivo.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.87-SDK6):",
    "    '",
    "    '  · SALA Y ESCENA EN VIVO: al entrar en Ajustes › Sala y Escena el",
    "    '    entorno deja el HALL y salta a la SALA DE PARTIDOS (sala + mesa",
    "    '    + marcador; el rig retrocede 1,15 m para que el panel no tape",
    "    '    la mesa). Todo cambio se ve AL MOMENTO en la mesa real. Al",
    "    '    salir de la categoría o cerrar el menú, vuelta EXACTA al Hall.",
    "    '",
    "    '  · SALA y MESA como SUBMENÚS-BOTÓN: dos tarjetas con la estética",
    "    '    del menú (color + icono propio de mesa) que abren SU página —",
    "    '    SALA (los cuatro temas + passthrough) y MESA (altura + aspecto).",
    "    '",
    "    '  · ALTURA POR DESLIZADOR: adiós a los tres presets — un raíl",
    "    '    continuo ajusta el tablero entre Baja (70 cm) y Alta (84 cm),",
    "    '    fijando la altura AL PUNTO apuntado, con botones − / + de paso",
    "    '    fino (1 cm) y lectura viva en cm y zona. DIMS.tableTopY muta y",
    "    '    física, IA, saque y escena la leen en vivo; la red conserva sus",
    "    '    15,25 cm reglamentarios y las patas se re-escalan honestas.",
    "    '",
    "    '  · TOOLTIPS (norma general del dueño): al APUNTAR cualquier opción",
    "    '    de los menús aparece una caja con una breve indicación de qué",
    "    '    hace ese ajuste, en el idioma escogido (ES/EN, ~55 claves",
    "    '    nuevas). Sin apuntar no pinta nada: cero ruido, cero coste.",
    "    '",
    "    '  · SONIDOS SIN SOLAPES: cada volumen (música / efectos) tiene SU",
    "    '    fila de etiqueta y SU fila de controles — nada pisa nada — y las",
    "    '    barras son CLICABLES: tocar un punto fija el volumen al punto.",
    "    '",
    "    '  · PIELES DE MESA SÓLO PARTIDAS Y ENTRENAMIENTO (petición literal:",
    "    '    «los ajustes de pieles de las mesas no deben afectar a los",
    "    '    campeonatos, sólo a las partidas y entrenamiento»). En",
    "    '    campeonato activo la mesa está en su AZUL NATIVO: el tinte del",
    "    '    dueño ya no tiñe la mesa de La Locura ni la de nadie. Al salir",
    "    '    del campeonato, la piel elegida vuelve sola.",
    "    '",
    "    '  · AUDITORÍA DE FLUIDEZ (el dueño: «deformación en medio de la",
    "    '    pantalla» en una partida de resistencia): sospechoso confirmado",
    "    '    — el FOVEADO FIJO (FFR) agresivo del autocalibrador llegaba a",
    "    '    0,8 y dibuja los anillos de compresión dentro de la vista. ",
    "    '    AHORA: NITIDEZ (FFR) en AJUSTES › RENDIMIENTO con 4 niveles",
    "    '    (Máxima 0 · Alta 0,25 · Normal 0,5 · Rinde 0,75) que CAPAN el",
    "    '    gobernador, techo honesto 0,65 sin tope manual y Quest 3 naciendo",
    "    '    a 0,35. El gobernador sigue garantizando 60 FPS, pero ya nunca",
    "    '    deforma la imagen en plena vista.",
    "    '",
    "    '  · QA r96 NUEVA (90 checks: deslizador con DIMS/red/patas/paso",
    "    '    fino/clamps, pieles con regla de campeonato simulada, vista de",
    "    '    sala Hall↔cancha con vuelta exacta, raíl y barras que obedecen",
    "    '    al punto apuntado por mano, tooltips con tinta nueva, FFR con",
    "    '    topes y persistencia, 14 páginas del menú repintadas sin",
    "    '    pageerrors) + cascada re-anclada a 3.6.88.",
    "    '",
]

# ── 1. heredar el directorio ─────────────────────────────────────────────
if DEST.exists():
    shutil.rmtree(DEST)
shutil.copytree(ORIGEN, DEST)
print(f'· heredado {ORIGEN.name} → {DEST.name}')

# ── 2. reescribir build_zip.py ───────────────────────────────────────────
src = BZ.read_text(encoding='utf-8')
for a, b in [
    ("release-v3687", "release-v3688"),
    ("staging-v3687", "staging-v3688"),
    ("v3687-sdk6", "v3688-sdk6"),
    ("V3.6.87-SDK6", "V3.6.88-SDK6"),
    ("3.6.87-SDK6", "3.6.88-SDK6"),   # guard en minúscula (const VERSION) — lección r93
    ('grep -c "3.6.87"', 'grep -c "3.6.88"'),
    ("n3687", "n3688"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 89 completo por el FASE 90
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 89'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 89'
i1 += len(BLOQUE_VIEJO_FIN)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 90 ({len(_NOTAS)} líneas), versiones → v3688-sdk6')
print('OK — ejecuta: python3 scripts/release-v3688/build_zip.py')
