#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3696 — hereda scripts/release-v3695 → scripts/release-v3696
e inserta las NOTAS de la FASE 98 «MENÚS A PANTALLA COMPLETA (r104)».

Ronda 104: petición del dueño — «los textos pequeños de los menús no se
leen muy bien, y revisar que no desborden y estén bien encajadas…
que se distribuyan a pantalla completa para ganar todo el espacio posible».

r104: panel 0,72×1,08 → 0,90×1,35 m (+25 % lineal), fuentes del menú ×1,16
(interceptación de `font`), contraste y definición (label 28 px, bordes
0,30, casillas mayores, palas de idioma 132 px), grises luminosos en todas
las páginas, recortes anti-desborde (pulso/invitación/hints) y 3 parches
de encaje vistos en captura (mapa de calor en crudo, subtítulo del hub de
entrenamiento, hint de campeonatos).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v3695).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3695"
DEST = RAIZ / "scripts" / "release-v3696"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 97 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.96)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 97 — ETIQUETAS FUERA DE LA VISTA +" + NL + "'"
BLOQUE_VIEJO_FIN = "    '  sellada a 3.6.96" + NL + "'"

# líneas de texto PLANO de las notas FASE 98 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 98 — MENÚS A PANTALLA COMPLETA (r104).",
    "    'El dueño pide: «los textos pequeños de los menús no se leen muy",
    "    'bien, y revisar que no desborden y estén bien encajadas… que se",
    "    'distribuyan a pantalla completa para ganar todo el espacio posible",
    "    'y ser más cómodos y legibles». r104 rehace la legibilidad del menú",
    "    'VR de arriba abajo, sin tocar ni un handler.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.95-SDK6):",
    "    '",
    "    '  · PANEL A PANTALLA COMPLETA: el menú pasa de 0,72×1,08 m a",
    "    '    0,90×1,35 m (+25 % lineal, proporción 2:3 intacta; a 1,08 m",
    "    '    ~1 texel = 1 píxel del visor) y sube la anisotropía 4 → 8.",
    "    '    TODO el texto gana un 25 % de tamaño físico sin tocar una",
    "    '    sola coordenada de página. Cursor proporcional (0,011 m).",
    "    '",
    "    '  · FUENTES ×1,16: interceptación de la propiedad `font` del",
    "    '    contexto del lienzo del menú — CUALQUIER texto (c12, PRO",
    "    '    TRAINING, champloader, tutorial) se dibuja un 16 % más",
    "    '    grande. Los autofits (measureText) siguen cuadrando por",
    "    '    diseño. Texto físico total: ~+45 % (panel + fuentes).",
    "    '",
    "    '  · MÁS CLARAS Y MEJOR DEFINIDAS: label por defecto 24 → 28 px",
    "    '    y gris luminoso; borde de botones 0,18 → 0,30; casillas",
    "    '    ☑ mayores; palas de idioma 118 → 132 px; sello de versión",
    "    '    19 px oro sólido; los grises apagados (#75828f/#5c6672/",
    "    '    #5f6b78/#7d8ea6) desaparecen de TODAS las páginas del menú.",
    "    '",
    "    '  · SIN DESBORDES: nombres de la lista del PULSO (16 chars) y",
    "    '    anfitrión de la invitación (14 chars) recortados; hint de",
    "    '    campeonatos con elipsis; subtítulo del hub de entrenamiento",
    "    '    recortado (no pisa puntos/logros); 3 parches de encaje",
    "    '    vistos en captura del lienzo (el mapa de calor mostraba las",
    "    '    claves en CRUDO: heat_t/heat_sin/… ya traducidos en ES/EN).",
    "    '",
    "    '  · ANCLAJE compensado: panel 1,35 m repartido arriba/abajo",
    "    '    (centro a cabeza − 0,12 m).",
    "    '",
    "    '  QA r104 54/0 (agujas estáticas + juego en vivo: malla 0,90×",
    "    '  1,35, fuentes 20 px → 23,2 px medidas sobre lienzo limpio,",
    "    '  ratio ×1,159, anclaje cabeza−0,12, capturas main/opts/multi/",
    "    '  champs/salamesa/train, regresión r103 del rótulo) · cascada",
    "    '  r101/r102/r103 re-anclada y verde (58/51/49) · sellada a 3.6.96",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3696 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.96.
    for viejo, nuevo in (("V3.6.95-SDK6", "V3.6.96-SDK6"),
                         ("3.6.95-SDK6", "3.6.96-SDK6"),
                         ("v3695-sdk6", "v3696-sdk6"),
                         ("3.6.95", "3.6.96"),
                         ("V3.6.95", "V3.6.96"),
                         ("v3695", "v3696"),
                         ("release-v3695", "release-v3696"),
                         ("staging-v3695", "staging-v3696")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 97 → FASE 98 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 97 → FASE 98 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 97 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
