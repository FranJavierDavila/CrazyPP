#!/usr/bin/env python3
"""gen_release_v3683 — hereda scripts/release-v3682 → scripts/release-v3683
e inserta las NOTAS de la FASE 85 «EL INFORME QUE POR FIN SE ATACA DE RAÍZ
(r91)» en build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3683 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3682"
DEST = RAIZ / "scripts" / "release-v3683"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 84 COMPLETO en el build_zip heredado (ini → fin exactos) ──
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 84 — INFORME r90: HALLOWEEN SUENA Y SE" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    ESTÁNDAR (decisión del dueño)." + NL + "'"

# líneas de texto PLANO de las notas FASE 85 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 85 — INFORME r91: EL INFORME QUE POR FIN",
    "    'SE ATACA DE RAÍZ. El dueño tras V3.6.82: «no suena la música de",
    "    'fondo · las manos están mal recortadas y no sale la parte inferior",
    "    '(la tierra y el brazo) · de la calabaza sólo se ve un trocito del",
    "    'rabito verde · NO TENEMOS EL MAPA EN LA PARED (en TODOS los cam-",
    "    'peonatos aparece perfectamente colocado) · ha vuelto el solapamien-",
    "    'to del rival con dos imágenes superpuestas · los sonidos del zombi",
    "    'sólo suenan algunos · no he visto zombi_defeated ni cambios de",
    "    'cara en el resto del partido». SIETE raíces cazadas con sonda en",
    "    'escena viva y arregladas de verdad.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.82-SDK6):",
    "    '",
    "    '  · BSO MUERTA POR FORMA (cazada en vivo): la r90 pasó url como",
    "    '    STRING y vol como NÚMERO y el motor createMusic los INVOCABA",
    "    '    (o.url()/o.vol()) → TypeError silencioso bajo el catch de",
    "    '    arrancar() → mus=null SIN error visible. Ahora forma CANÓNICA",
    "    '    (funciones, la de magia/oeste) en el módulo y el SDK TOLERANTE",
    "    '    (val(): acepta función o valor) — el motor ya no puede quedar",
    "    '    mudo por la forma de los parámetros. Verificado en vivo: la",
    "    '    BSO arranca al pulsar JUGAR de la intro y SIGUE durante el",
    "    '    duelo entero.",
    "    '",
    "    '  · MAPA = RECETA WIZARDMAP EXACTA (la que el dueño ve «perfecta-",
    "    '    mente colocada en TODOS los campeonatos»): GRUPO colgado del",
    "    '    RIG, pos [-2.98, 1.5, -0.9] rotY π/2, ancho 1.68 y respaldo de",
    "    '    madera de 22 mm que lo ancla como un cuadro. Y el fallo REAL",
    "    '    del póster invisible: el opacity-gate por setInterval DORMIDO",
    "    '    — la sonda r91b cazó opacity 0 con la textura DESCARGADA y",
    "    '    viva. Ahora el material nace sin mapa y la textura se asigna",
    "    '    DENTRO DEL CALLBACK del TextureLoader (el callback ES el",
    "    '    evento de llegada — no puede perderse) + respaldo por-frame",
    "    '    en refresco(): si hay imagen y el póster sigue apagado, se",
    "    '    enciende. SRGB intacto (saturación del arte del dueño).",
    "    '",
    "    '  · CALABAZA — EL BUG RAÍZ DE CUATRO RONDAS (informe: «sólo se le",
    "    '    ve un trocito del rabito verde»): _preparaCuerpoR88 convertía",
    "    '    el material SIEMPRE en ARRAY y el renderer (THREE r186, pro-",
    "    '    jectObject) con material-array SÓLO dibuja los geometry.groups:",
    "    '    LatheGeometry (el CUERPO) y TorusGeometry (el zarcillo) NO",
    "    '    TIENEN grupos → CERO draw calls → invisible; el rabo era lo",
    "    '    único vivo porque CylinderGeometry SÍ trae grupos. FIX: mate-",
    "    '    rial único vuelve SINGLE + DoubleSide a prueba de casco +",
    "    '    color naranja sólido (si la textura tarda, el cuerpo ES",
    "    '    naranja — jamás invisible) + frustumCulled OFF. Verificado en",
    "    '    captura viva: calabaza naranja con costillas EN LA MESA.",
    "    '",
    "    '  · MANOS CON ARTE INTEGRAL (informe: «no sale la parte inferior,",
    "    '    la tierra y el brazo saliendo»): el cultivo 0.70/offset 0.30",
    "    '    de la r90 escondía EXACTAMENTE la franja que el dueño quería",
    "    '    ver. Cultivo 1.0/offset 0.0 — el arte COMPLETO del dueño (ma-",
    "    '    no + tierra + brazo) sube desde la mesa al desenrollarse.",
    "    '",
    "    '  · RIVAL BAJO LA NORMA ÚNICA (informe: «no he visto cambios en el",
    "    '    resto del partido ni zombi_defeated… dos imágenes superpues-",
    "    '    tas»): TRES motores se pisaban (reaccion() por punto + el",
    "    '    motor legacy picando/loosing/panic POR FRAME + la norma r57",
    "    '    del núcleo) — las caras iban imposibles de seguir. Los dos",
    "    '    motores locales SE RETIRAN: la emoción llega SÓLO del núcleo",
    "    '    (rivalEmocion) y el zombi la viste con SU arte + SU sonido",
    "    '    (laugh/crazy/victory/defeated). Cada etapa nueva RECOMPONE la",
    "    '    cara y el FINAL VIVE: hold de 4,2 s — la vuelta a sala ya NO",
    "    '    pisa defeated/victory el mismo frame (el dueño jamás llegó a",
    "    '    ver zombi_defeated). Verificado en vivo: cadena núcleo→módulo",
    "    '    cambia la cara y EXACTAMENTE UN plano del zombi en TODO el",
    "    '    ciclo de vida (entrada→tormenta→duelo→final→re-entrada).",
    "    '",
    "    '  · SONIDOS DEL ZOMBI COMPLETOS (informe: «sólo suenan algunos»):",
    "    '    los cuatro (risas/crazy/victory/defeated) verificados a",
    "    '    44100 Hz por decodificación real y disparados AHORA TAMBIÉN",
    "    '    por la norma de emociones — antes victory/defeated sólo sona-",
    "    '    ban al final del partido y crazy al lanzar el poder.",
    "    '",
    "    '  · LIMPIEZA: power_0.png/power_1.png (provisionales muertos desde",
    "    '    la r86) fuera del repo. QA r91 NUEVA 55/0 + re-anclajes hon-",
    "    '   estos r85/r86/r87/r88/r90 (gelatina 12 s, BSO Midnight, mano",
    "    '    sin montículo, mapa WizardMap, calabaza procedural).",
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
    ("release-v3682", "release-v3683"),
    ("staging-v3682", "staging-v3683"),
    ("v3682-sdk6", "v3683-sdk6"),
    ("V3.6.82-SDK6", "V3.6.83-SDK6"),
]:
    src = src.replace(a, b)

# bloque de notas: sustituir el FASE 84 completo por el FASE 85
i0 = src.find(BLOQUE_VIEJO_INI)
assert i0 >= 0, 'no encuentro el inicio del bloque FASE 84'
i1 = src.find(BLOQUE_VIEJO_FIN, i0)
assert i1 >= 0, 'no encuentro el fin del bloque FASE 84'
i1 += len(BLOQUE_VIEJO_FIN)
# cada línea: abre comilla (ya viene en _NOTAS) + texto + \n + cierra comilla,
# unidas por salto de línea REAL (implicit-concatenation como el bloque original)
nuevo = chr(10).join(ln + NL + "'" for ln in _NOTAS)
src = src[:i0] + nuevo + src[i1:]
BZ.write_text(src, encoding='utf-8')
print(f'· build_zip.py reescrito: notas FASE 85 ({len(_NOTAS)} líneas), versiones → v3683-sdk6')
print('OK — ejecuta: python3 scripts/release-v3683/build_zip.py')
