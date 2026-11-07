#!/usr/bin/env python3
"""gen_release_v3685 — hereda scripts/release-v3684 → scripts/release-v3685
e inserta las NOTAS de la FASE 87 «TRES RÁPIDAS (r93)» en build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3685 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3684"
DEST = RAIZ / "scripts" / "release-v3685"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 86 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 86 — INFORME r92: LAS CUATRO DEL" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    r88 (giro propio por spin en vez del quaternion)." + NL + "'"

# líneas de texto PLANO de las notas FASE 87 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 87 — TRES RÁPIDAS (r93). El dueño",
    "    'tras V3.6.84: «sustituimos la melodía por melodia.mp3 del",
    "    'campeonato por la que adjunto · en el superpoder de la calabaza",
    "    'existe un desfase de la bola cuando la golpea el rival, en",
    "    'cambio cuando la golpeo yo está correcta, es una deriva de",
    "    'precisión entre ambas palas · los diseños de las etiquetas que",
    "    'salen con cada superpoder: cuatro diseños más realistas y",
    "    'tenebrosos según el superpoder». Tres raíces, tres arreglos",
    "    'verificados en escena viva.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.84-SDK6):",
    "    '",
    "    '  · BSO NUEVA DEL DUEÑO (informe: «sustituimos la melodía»):",
    "    '    melodia.mp3 (178,4 s, re-codificada al perfil probado",
    "    '    44100 Hz / 256 kbps CBR — el que el casco decodifica)",
    "    '    sustituye a midnight_volley.mp3 (RETIRADO del repo). Mismo",
    "    '    motor createMusic / manifest.audio.music: cero cambios de",
    "    '    código, la melodía entra por el camino de siempre. Verifi-",
    "    '    cado en vivo: buffer cargado, querida tras JUGAR y SONANDO.",
    "    '",
    "    '  · DESFASE DEL RIVAL CON LA CALABAZA CAZADO (informe: «un",
    "    '    desfase de la bola cuando la golpea el rival… es una deriva",
    "    '    de precisión entre ambas palas»): la r92 arrastraba el punto",
    "    '    de contacto hacia la pala y RECOLOCABA la bola en la",
    "    '    tangente — con la calabaza (Ø 0,13 m, 3× la bola) ese salto",
    "    '    de hasta 4,5 cm SE VE (la calabaza salta hacia la pala en el",
    "    '    frame del golpe) y el follow-through arrancaba con la hoja",
    "    '    5 cm por encima. El golpe del dueño está correcto porque su",
    "    '    física jamás recoloca la bola — la deriva era SÓLO del lado",
    "    '    de la IA. Ahora la bola se queda en el punto del BARRIDO",
    "    '    (el MISMO trato que la bola normal) y es la HOJA la que",
    "    '    viaja hasta la piel de la calabaza: el swing nace en el",
    "    '    punto TANGENTE (centro de calabaza a 7,5 cm del centro de",
    "    '    hoja) y SIN el ascenso inicial (flat). Contacto sólido,",
    "    '    cero teleportes, física intacta: la salida se calcula desde",
    "    '    ball.pos real con computeShotVelocityReal al mismo blanco.",
    "    '    Verificado con la IA real: la bola se queda a 0,10 m de la",
    "    '    pala (sin salto), la hoja nace a 0,0752 (en la piel) y el",
    "    '    swing sale flat en las 3 repeticiones; bola normal intacta",
    "    '    (0,18, sin flat).",
    "    '",
    "    '  · ETIQUETAS TERRORÍFICAS DE LOS CUATRO SUPERPODERES (informe:",
    "    '    «más realistas y tenebrosos según el superpoder»): los",
    "    '    cuatro iconos power_*.webp RE-DISEÑADOS — arte fotorealista",
    "    '    1024×1024 por poder (mano zombi saliendo de la tierra,",
    "    '    plaga de moscas, calabaza siniestra, gelatina asquerosa)",
    "    '    recortado en MEDALLÓN CIRCULAR 512×512 RGBA con anillo de",
    "    '    hierro viejo y filo ember (paleta calabaza 0xe8720c). Los",
    "    '    nombres de salida SON los del manifest: cero cambios de",
    "    '    código — el cartel los muestra por powers[].icon como",
    "    '    siempre. Verificado en vivo: textura 512×512 decodificada y",
    "    '    visible bajo el cartel en el anuncio del poder.",
    "    '",
    "    '  · QA r93 NUEVA 54/0 (estática + runtime: perfil de la",
    "    '    melodía, medallones circulares distintos por poder, agujas",
    "    '    c06/c12 en el servido, BSO querida+sonando, sondeo del",
    "    '    golpe IA sin arrastre con hoja en la piel y etiqueta viva",
    "    '    en el cartel) + re-anclaje honesto r92 (el contacto de la",
    "    '    calabaza ya NO se arrastra a la tangente — r93).",
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
    ("release-v3684", "release-v3685"),
    ("staging-v3684", "staging-v3685"),
    ("v3684-sdk6", "v3685-sdk6"),
    ("V3.6.84-SDK6", "V3.6.85-SDK6"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 86 completo por el FASE 87
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 86'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 86'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implicit-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 87 ({len(_NOTAS)} líneas), versiones → v3685-sdk6')
print('OK — ejecuta: python3 scripts/release-v3685/build_zip.py')
