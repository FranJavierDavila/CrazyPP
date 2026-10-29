#!/usr/bin/env python3
"""gen_release_v3684 — hereda scripts/release-v3683 → scripts/release-v3684
e inserta las NOTAS de la FASE 86 «LAS CUATRO DEL INFORME (r92)» en
build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3684 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3683"
DEST = RAIZ / "scripts" / "release-v3684"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 85 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 85 — INFORME r91: EL INFORME QUE POR FIN" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    sin montículo, mapa WizardMap, calabaza procedural)." + NL + "'"

# líneas de texto PLANO de las notas FASE 86 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 86 — INFORME r92: LAS CUATRO DEL",
    "    'INFORME. El dueño tras V3.6.83: «las manos de los zombis deben",
    "    'salir justa de la mesa de tal forma que su parte inferior toque",
    "    'la mesa y no quede suspendida en el aire · cambiamos la textura",
    "    'de la mesa por la nueva que adjunto · el rival no la golpea",
    "    'correctamente con su pala, parece que tiene un desplazamiento",
    "    'y el efecto no queda bien · la calabaza debería girar sobre si",
    "    'misma al golpearla tal como haría la bola». Cuatro raíces,",
    "    'cuatro arreglos verificados en escena viva.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.83-SDK6):",
    "    '",
    "    '  · MANOS ANCLADAS A LA MESA (informe: «deben salir justa de la",
    "    '    mesa, su parte inferior toca la mesa y no queda suspendida",
    "    '    en el aire»): la base del plano vive a MANO_Y (tableTopY +",
    "    '    0,005) en TODAS las fases — fuera el ascenso +0,12 y el",
    "    '    vaivén vertical de la r89, que eran EXACTAMENTE lo que dejaba",
    "    '    la mano colgando sobre la mesa. El «nacer de abajo» sigue",
    "    '    leyéndose: el plano DESENROLLA desde la mesa (repeat.y 0→1",
    "    '    con la base fija) y la punta asciende al crecer; el movimien-",
    "    '    to vivo queda en el vaivén de ROTACIÓN (pivote en la base) y",
    "    '    en la respiración de ESCALA (crece desde la base, la punta",
    "    '    respira). Verificado en vivo: y=0,765 constante en subir/",
    "    '    arriba/bajar.",
    "    '",
    "    '  · MESA NUEVA DEL DUEÑO (informe: «cambiamos la textura de la",
    "    '    mesa por la nueva que adjunto»): mesa.webp (2048×1024, cuatro",
    "    '    losas de piedra oscura con grietas, musgo y salpicaduras de",
    "    '    sangre) viste el ppTableTop por el mismo camino de siempre",
    "    '    (_losaOn: SRGB + anisotropía + marco/patas piedra oscura",
    "    '    0x3d4145 + restauración garantizada por _losaSaved). losa.jpg",
    "    '    se CONSERVA en assets para rollback.",
    "    '",
    "    '  · GOLPE DEL RIVAL A LA CALABAZA (informe: «el rival no la",
    "    '    golpea correctamente con su pala, parece que tiene un",
    "    '    desplazamiento»): la calabaza mide Ø 0,13 m (3× la bola) pero",
    "    '    el contacto saltaba con el alcance genérico de 21 cm — la",
    "    '    pala se paraba JUNTO a la calabaza, nunca sobre ella. Ahora",
    "    '    el módulo marca la bola (ppCalabaza, puesta en inicio y lim-",
    "    '    piada en estallido/fin) y el núcleo la lee: el alcance baja a",
    "    '    0,12 m y el punto de contacto se ARRASTRA hasta la TANGENTE",
    "    '    con la hoja (centro de calabaza a 7,5 cm del centro de pala,",
    "    '    corrección ≤4,5 cm — ni un teleporte). La salida parte del",
    "    '    punto tocado con computeShotVelocityReal al mismo blanco: la",
    "    '    trayectoria de la devolución no cambia. Verificado con la IA",
    "    '    REAL en los dos sentidos: con marca dist=0,0753 (toca); sin",
    "    '    marca dist=0,18 (norma genérica intacta).",
    "    '",
    "    '  · CALABAZA QUE GIRA SOBRE SÍ MISMA (informe: «debería girar",
    "    '    sobre si misma al golpearla tal como haría la bola»): el",
    "    '    quaternion de la bola (r88) apenas se APRECIABA en un cuerpo",
    "    '    de 13 cm (la bola suma spin·dt·0,05 — media vuelta por segun-",
    "    '    do y la superficie apenas se mueve). La calabaza lleva SU",
    "    '    rotación propia ARRASTRADA POR EL SPIN de la bola a ritmo de",
    "    '    cuerpo grande (spin·dt·0,15 = ×3 la tasa visual de la bola,",
    "    '    la misma sensación de rodadura en su tamaño): cada golpe",
    "    '    CAMBIA el spin (remate liftado, push cortado, saque) y la",
    "    '    vuelta REARRANCA en el acto — se la ve girar al golpearla.",
    "    '    Verificado en vivo: spin 20/8 → Δrot 0,30/0,12 rad en 0,1 s.",
    "    '",
    "    '  · QA r92 NUEVA 39/0 (estática + runtime: mesa.webp en el",
    "    '    ppTableTop, mano base=0,765 en las 3 fases, contacto tangente",
    "    '    con la IA real en los dos sentidos, giro propio y ciclo",
    "    '    completo de la marca) + re-anclajes honestos r87 (MANO_Y) y",
    "    '    r88 (giro propio por spin en vez del quaternion).",
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
    ("release-v3683", "release-v3684"),
    ("staging-v3683", "staging-v3684"),
    ("v3683-sdk6", "v3684-sdk6"),
    ("V3.6.83-SDK6", "V3.6.84-SDK6"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 85 completo por el FASE 86
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 85'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 85'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implicit-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 86 ({len(_NOTAS)} líneas), versiones → v3684-sdk6')
print('OK — ejecuta: python3 scripts/release-v3684/build_zip.py')
