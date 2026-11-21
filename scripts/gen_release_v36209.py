#!/usr/bin/env python3
"""gen_release_v36209 — hereda scripts/release-v36207 → scripts/release-v36209
(patrón de la casa: gen_release_vXXXX hereda el release anterior, reescribe
las cuerdas de versión y sustituye el bloque de notas del VERSION.txt).

Notas de esta entrega: FASES 185-186 (r110 LA CRIPTONITA SE DESTRUYE AL
EXPIRAR + r111 FLUIDEZ PRIMERO — LA CABEZA MANDA, el judder del dueño).

Las notas se construyen desde una LISTA de líneas de texto plano y se unen
con la secuencia LITERAL \\n (backslash+n) que espera el string multi-línea
de build_zip.py — cero ambigüedad de escapes (lección de gen_release_v3682).

Idempotente: si release-v36209 ya existe, se regenera desde cero.
"""
import py_compile
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36207'
DEST = RAIZ / 'scripts' / 'release-v36209'
BZ = DEST / 'build_zip.py'

NL = chr(92) + 'n'          # secuencia LITERAL \n (2 caracteres)

# ── 1. herencia limpia ────────────────────────────────────────────
if DEST.exists():
    shutil.rmtree(DEST)
shutil.copytree(ORIGEN, DEST,
                ignore=shutil.ignore_patterns('__pycache__'))
print(f'· heredado: {ORIGEN.name} → {DEST.name}')

txt = BZ.read_text(encoding='utf-8')

# ── 2. bloque de notas FASE 184 → FASES 185-186 ──────────────────
# La primera línea va SIN sangría: txt[:i] ya termina con la sangría de 4
# espacios del source. La última se concatena (implícita) con 'Hashes…'.
_LINEAS = [
    'Base    : main · SDK6 (FASES 185-186 — LA CRIPTONITA SE DESTRUYE',
    'AL EXPIRAR · FLUIDEZ PRIMERO — LA CABEZA MANDA. El dueño: «si',
    'movemos la cabeza de izquierda a derecha, la línea longitudinal',
    'central de la mesa se percibe duplicada, como a saltos, sin',
    'continuidad — quiero que vaya fluida para no perder la sensación',
    'de una mesa real: es un efecto desagradable y llega a marear»):',
    '· LA DESTRUCCIÓN (FASE 185): al expirar la criptonita los',
    '  cristales se ROMPEN TODOS (fin() → giro + encogido de 0,3 s)',
    '  en el juego y en la sala Arcano — la mesa queda limpia tras',
    '  cada poder, sin cristales fantasma.',
    '· EL JUDDER (FASE 186): lo que ve el dueño es judder — el frame',
    '  que llega tarde lo repinta el compositor con la pose vieja y',
    '  la línea central se dobla al girar la cabeza. CUATRO CAUSAS DE',
    '  RAÍZ en el PerfManager: (1) perfil Quest 3 a filo de navaja',
    '  (1.40× @ 90 Hz: la telemetría vr_end midió 55-78 fps, bajo el',
    '  piso 72 la mayor parte del tiempo); (2) barra de la sonda FIJA',
    '  68/55 sin escalar por tasa (a 90 Hz eso acepta un 24% de',
    '  frames perdidos); (3) gobernador DORMIDO en el rallye (solo',
    '  avg<50 — un intercambio a 55-70 fps no se corregía nunca);',
    '  (4) calibración sobre-affilada guardada en localStorage v1.',
    '· EL ARREGLO: perfil con margen (1.25× / fovea 0.45 — la',
    '  nitidez la recupera el gobernador solo cuando el casco aguanta',
    '  20 s con margen), barra de sonda 93%/83% de la tasa objetivo',
    '  (90 Hz → 84/75 · 72 Hz → 67/60), gobernador VIVO en el rallye',
    '  (media < 64 o peor segundo < 45 degrada imagen al momento; la',
    '  tasa nunca se cambia en caliente) y registro ppxr_perf_v2 (el',
    '  casco nace recalibrado con la barra honesta; la preferencia',
    '  FFR del dueño sobrevive).',
    '· Arnés r111 24/0 · batería núcleo 9/9 · smoke Chromium y Pages',
    '  verdes · golden a627bed1 ·',
    '  sellada a 3.6.209',
]
partes = []
for k, linea in enumerate(_LINEAS):
    sangria = '' if k == 0 else '    '
    partes.append(sangria + "'" + linea + NL + "'")
BLOQUE = '\n'.join(partes)

A = "'Base    : main · SDK6 (FASE 184"
B = "'Hashes SHA256 (verificación de integridad):"
i, j = txt.find(A), txt.find(B)
if i < 0 or j < 0 or j <= i:
    raise SystemExit('✗ no encuentro el bloque de notas FASE 184 en build_zip.py')
txt = txt[:i] + BLOQUE + txt[j:]

# ── 3. cuerdas de versión (todo lo que queda) ────────────────────
txt = (txt.replace('release-v36207', 'release-v36209')
          .replace('staging-v36207', 'staging-v36209')
          .replace('v36207-sdk6', 'v36209-sdk6')
          .replace('3.6.207-SDK6', '3.6.209-SDK6')
          .replace('V3.6.207', 'V3.6.209')
          .replace('3.6.207', '3.6.209'))   # pelados: la verificación post-build
# del hub que grep-ea '3.6.207' dentro del COMPLETO (build_zip heredado, ~447)

# ── 4. guardas: nada de la era 36207 debe quedar vivo ────────────
for prohibido in ('v36207', '3.6.207', 'release-v36207'):
    if prohibido in txt:
        raise SystemExit(f'✗ quedó un literal de la era anterior: {prohibido}')
if txt.count('v36209-sdk6') < 5:
    raise SystemExit('✗ pocas cuerdas v36209-sdk6 (¿sed incompleto?)')

BZ.write_text(txt, encoding='utf-8')
py_compile.compile(str(BZ), doraise=True)
print(f'· build_zip.py reescrito: notas FASES 185-186 ({len(_LINEAS)} líneas),'
      ' versiones → v36209-sdk6 · sintaxis verificada')
print('OK — ejecuta: python3 scripts/release-v36209/build_zip.py')
