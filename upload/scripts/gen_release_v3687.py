#!/usr/bin/env python3
"""gen_release_v3687 — hereda scripts/release-v3686 → scripts/release-v3687
e inserta las NOTAS de la FASE 89 «AJUSTES DEL DUEÑO (r95)» en build_zip.py.

Ronda 95, cuatro frentes del dueño:
 1) SIN CARTEL EN LOS DUELOS (regla de casa: el cartel explicativo sólo
    existe en las etapas de HABILIDAD) — halloween (los 3 duelos), la
    PLANTILLA y la ESTACIÓN ORBITAL dejan de pintarlo.
 2) VOLÚMENES SEPARADOS música/efectos en AJUSTES › SONIDOS.
 3) SALA Y ESCENA en dos subapartados: SALA (los 4 temas) y MESA (altura
    baja/normal/alta + aspecto con 3 opciones y 2 liberables con recompensas).
 4) RIVALES CON ESTILO VISIBLE (colocación + celebraciones) y ESTADÍSTICAS
    AL FINAL DE CADA DUELO (vel. máx · rally más largo · % precisión).

Lección de la r93 aplicada: los guards en MINÚSCULA se heredan REEMPLAZADOS
aquí — nada de correcciones post-gen. Idempotente.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3686"
DEST = RAIZ / "scripts" / "release-v3687"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 88 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 88 — LA CALABAZA ES LA BOLA (r94). El dueño" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    y cierre limpios, cero pageerrors) + sellos 3.6.86." + NL + "'"

# líneas de texto PLANO de las notas FASE 89 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 89 — AJUSTES DEL DUEÑO (r95). Cuatro",
    "    'frentes en una ronda: el cartel explicativo SÓLO en las etapas de",
    "    'habilidad, volumen separado música/efectos, la MESA con altura y",
    "    'aspecto propios en Ajustes, y los rivales que MUESTRAN su",
    "    'personalidad con estadísticas al final de cada duelo.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.86-SDK6):",
    "    '",
    "    '  · SIN CARTEL EN LOS DUELOS (regla de casa: «en todos los",
    "    '    campeonatos, en las fases de duelo con el rival no hay cartel",
    "    '    explicativo; ese sólo existe en las etapas de habilidades»). Los",
    "    '    TRES duelos de Halloween (Niebla, Luna y FINAL), los duelos de la",
    "    '    ESTACIÓN ORBITAL y la PLANTILLA (futuros campeonatos) arrancan",
    "    '    sin cartel: el aviso vive en la línea del marcador y el duelo",
    "    '    empieza al saque. Las PRUEBAS de habilidad conservan SU cartel",
    "    '    (regla v2.106 intacta). Oeste, magia y locura ya cumplían.",
    "    '",
    "    '  · VOLÚMENES SEPARADOS (AJUSTES › SONIDOS): dos barras −/+ con",
    "    '    canales PERSISTENTES e independientes. MÚSICA escala el tema del",
    "    '    menú Y las BSO de los campeonatos (núcleo + motores privados de",
    "    '    oeste y magia). EFECTOS escala el bus completo (golpes, botes,",
    "    '    canto, red, suelo, rival, fanfarria). Voz y ambiente conservan",
    "    '    SUS canales de siempre. Aplicación EN VIVO y persistente.",
    "    '",
    "    '  · SALA Y ESCENA en DOS subapartados (AJUSTES): «SALA» con los",
    "    '    cuatro temas de siempre (futuro: pieles de sala) y «MESA» NUEVO:",
    "    '    ALTURA Baja/Normal/Alta (muta DIMS.tableTopY — física, IA y",
    "    '    saque la leen en vivo; la mesa viva se reacomoda sin",
    "    '    reconstruirse y la red mantiene sus 15,25 cm reglamentarios) y",
    "    '    ASPECTO con 3 opciones por defecto (Azul oficial, Verde clásica,",
    "    '    Neón locura) + 2 liberables con RECOMPENSAS (Oro campeón: gana",
    "    '    10 partidos · Carbono pro: racha de 5). Bloqueada durante un",
    "    '    campeonato activo.",
    "    '",
    "    '  · RIVALES CON ESTILO VISIBLE (AJUSTES › JUEGO): la personalidad del",
    "    '    manifest (agresivo/defensivo) SE NOTA — el agresivo espera más",
    "    '    cerca de la mesa y se adelanta al golpe; el defensivo espera",
    "    '    atrás — y al ganar el punto LO CELEBRA (saltitos y guiño de",
    "    '    hoja). Toggle sí/no: en NO, comportamiento clásico exacto.",
    "    '",
    "    '  · ESTADÍSTICAS AL FINAL DE CADA DUELO: el cartel de fanfarria",
    "    '    añade el chip ⚡ velocidad máx. de bola · rally más largo ·",
    "    '    % precisión, medidos EN VIVO durante el partido (vmax por frame,",
    "    '    rally en cada punto, precisión del marcador final).",
    "    '",
    "    '  · QA r95 NUEVA (69 checks: sin cartel en los 5 campeonatos vivos +",
    "    '    plantilla, canales de volumen en vivo y persistentes, mesa que",
    "    '    muta DIMS + reacomoda patas/red y bloqueos honestos, estilo con",
    "    '    sonda de colocación 0,32 m, chip de stats con tinta nueva, menú",
    "    '    que obedece al rayo, mStats a cero por partida, 0 pageerrors) +",
    "    '    cascada completa re-anclada a 3.6.87 (version 23/0 · r94 20/0 ·",
    "    '    r93 50/0 · r92 41/0 · r91 55/0 · r90 66/0 · sup1 151/0).",
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
    ("release-v3686", "release-v3687"),
    ("staging-v3686", "staging-v3687"),
    ("v3686-sdk6", "v3687-sdk6"),
    ("V3.6.86-SDK6", "V3.6.87-SDK6"),
    ("3.6.86-SDK6", "3.6.87-SDK6"),   # guard en minúscula (const VERSION) — lección r93
    ('grep -c "3.6.86"', 'grep -c "3.6.87"'),
    ("n3686", "n3687"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 88 completo por el FASE 89
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 88'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 88'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implicit-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 89 ({len(_NOTAS)} líneas), versiones → v3687-sdk6')
print('OK — ejecuta: python3 scripts/release-v3687/build_zip.py')
