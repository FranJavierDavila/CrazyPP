#!/usr/bin/env python3
"""gen_release_v3686 — hereda scripts/release-v3685 → scripts/release-v3686
e inserta las NOTAS de la FASE 88 «LA CALABAZA ES LA BOLA (r94)» en
build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Lección de la r93 aplicada: los guards en MINÚSCULA (const VERSION '3.6.85',
grep -c "3.6.85") se heredan REEMPLAZADOS aquí — nada de correcciones post-gen.

Idempotente: si release-v3686 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3685"
DEST = RAIZ / "scripts" / "release-v3686"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 87 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 87 — TRES RÁPIDAS (r93). El dueño" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    calabaza ya NO se arrastra a la tangente — r93)." + NL + "'"

# líneas de texto PLANO de las notas FASE 88 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 88 — LA CALABAZA ES LA BOLA (r94). El dueño",
    "    'tras V3.6.85: «cuando jugamos con calabaza en determinados momentos se",
    "    'produce un desfase y se ve por un lado la calabaza y por otro la bola.",
    "    'No debería pasar, la calabaza debería ocupar el lugar exacto de la bola",
    "    'y esta no verse mientras tengamos la calabaza sin destruir». Una raíz,",
    "    'tres garantías duras cada frame, cero cambios de núcleo.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.85-SDK6):",
    "    '",
    "    '  · LA BOLA JAMÁS SE VE mientras la calabaza vive (informe: «esta no",
    "    '    verse mientras tengamos la calabaza sin destruir»): el núcleo re-",
    "    '    enseñaba la bola en varios caminos (toss del saque, HELD del",
    "    '    sacador, reset de punto, tránsitos y restauraciones) y el módulo",
    "    '    sólo la ocultaba UNA VEZ al nacer el poder. Ahora paso() la vuelve",
    "    '    a ocultar CADA frame, DESPUÉS de esos caminos y ANTES del render:",
    "    '    ver bola y calabaza a la vez es imposible por construcción.",
    "    '",
    "    '  · EL LUGAR EXACTO (informe: «la calabaza debería ocupar el lugar",
    "    '    exacto de la bola»): la calabaza copia la posición RENDERIZADA de",
    "    '    la bola (ballMesh.position, que el núcleo sincroniza de ball.pos",
    "    '    en el mismo frame) — bit a bit con donde la bola estaría pintada,",
    "    '    inmune a interpolaciones, HELD o caminos especiales. Verificado",
    "    '    en vivo: bola movida 0,6 m → la calabaza la clava con deriva 0.",
    "    '",
    "    '  · NACIMIENTO EN SITIO + GUARD r92: inicio() coloca la calabaza en el",
    "    '    punto vivo de la bola (antes pasaba un frame en el origen) y la",
    "    '    marca ppCalabaza (contacto de la IA pegado a la calabaza, r92)",
    "    '    renace cada frame — aunque el núcleo recree la bola entre puntos,",
    "    '    el contacto no caduca a mitad del poder.",
    "    '",
    "    '  · ENTREGA DEL ESTALLIDO INTACTA: al podrirse del todo, la calabaza",
    "    '    se oculta y la bola VUELVE en el mismo punto (CHOFFF + 12 trozos).",
    "    '    Nunca calabaza y bola a la vez: ni al nacer, ni en el rallye, ni",
    "    '    en la transición.",
    "    '",
    "    '  · QA r94 NUEVA (estática + runtime: sonda viva del desfase — la bola",
    "    '    re-enseñada a mano vuelve a ocultarse en ≤2 frames, calabaza",
    "    '    clavada a la bola con deriva < 1e-6 m, guard ppCalabaza, estallido",
    "    '    y cierre limpios, cero pageerrors) + sellos 3.6.86.",
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
    ("release-v3685", "release-v3686"),
    ("staging-v3685", "staging-v3686"),
    ("v3685-sdk6", "v3686-sdk6"),
    ("V3.6.85-SDK6", "V3.6.86-SDK6"),
    ("3.6.85-SDK6", "3.6.86-SDK6"),   # guard en minúscula (const VERSION) — lección r93
    ('grep -c "3.6.85"', 'grep -c "3.6.86"'),
    ("n3685", "n3686"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 87 completo por el FASE 88
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 87'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 87'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implicit-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 88 ({len(_NOTAS)} líneas), versiones → v3686-sdk6')
print('OK — ejecuta: python3 scripts/release-v3686/build_zip.py')
