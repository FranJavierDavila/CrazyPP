#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v3698 — hereda scripts/release-v3697 → scripts/release-v3698
e inserta las NOTAS de la FASE 100 «M1 GAME FEEL · HÁPTICAS CALIBRADAS
(r106)».

Ronda 106: primer hito del roadmap MEJORAS.md (mejoras ordenadas de más
sencillo a más complicado). Auditoría corregida: la mitad de AUDIO de M1 ya
existía desde r62 «SFX REALES» (muestras modales físicas de mesa/pala/canto/
red/suelo con tono por velocidad y jitter ±1,5 %) — se verifica como
regresión. Lo que r106 implementa es la HÁPTICA:

  (1) bote de mesa calibrado (antes 0,18 fija y fuera del guard de 60 ms =
      ametralladora en ráfagas esquina+canto; ahora dentro del guard y
      proporcional: 0,08+0,16·s · 50–80 ms);
  (2) canto distinguible al tacto (pico 0,14+0,16·s, seco, 28 ms);
  (3) red palpable (0,15 / 45 ms).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v3697).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3697"
DEST = RAIZ / "scripts" / "release-v3698"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 99 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.98)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 99 — DERIVA DEL PUNTERO + RENDIMIENTO DEL" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.98" + NL + "'"

# líneas de texto PLANO de las notas FASE 100 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 100 — M1 GAME FEEL · HÁPTICAS CALIBRADAS",
    "    '(r106).",
    "    'Primer hito del roadmap MEJORAS.md (mejoras ordenadas de más sencillo",
    "    'a más complicado): GAME FEEL. Auditoría corregida: la mitad de AUDIO",
    "    'ya existía desde r62 «SFX REALES» — muestras modales físicas de",
    "    'mesa/pala/canto/red/suelo con tono por velocidad y jitter ±1,5 % —",
    "    'y se verifica aquí como regresión. Lo que r106 implementa es la",
    "    'HÁPTICA.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.97-SDK6):",
    "    '",
    "    '  · HÁPTICA DEL BOTE CALIBRADA: antes 0,18 FIJA y FUERA del guard",
    "    '    anti-spam de 60 ms — cada evento de mesa vibraba (ráfaga",
    "    '    esquina+canto = ametralladora). Ahora DENTRO del guard y",
    "    '    proporcional a la velocidad: bote llano 0,08+0,16·s con 50–80 ms.",
    "    '",
    "    '  · CANTO DISTINGUIBLE AL TACTO: pico más alto (0,14+0,16·s) y seco",
    "    '    (28 ms) frente al bote llano — la esquina se SIENTE distinta.",
    "    '",
    "    '  · RED PALPABLE: vibración sutil nueva 0,15/45 ms al roce de la",
    "    '    malla (los eventos de red son raros: sin riesgo de spam).",
    "    '",
    "    '  · Háptica de pala escalada r62 intacta (intensidad 0,35+0,65·s y",
    "    '    duración 34–96 ms por velocidad) · SFX reales r62 verificados ·",
    "    '    NADA de gameplay tocado (los 6 módulos core pasan node --check;",
    "    '    física determinista 11/0).",
    "    '",
    "    '  QA r106 en verde (35 agujas estáticas + juego en vivo: guard de",
    "    '  ráfaga 2 botes → 1 vibración, amplitud/duración medidas en vivo,",
    "    '  canto y red distinguibles, r62/r105/r104 intactos) · sellada a 3.6.98",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v3698 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.98.
    for viejo, nuevo in (("V3.6.97-SDK6", "V3.6.98-SDK6"),
                         ("3.6.97-SDK6", "3.6.98-SDK6"),
                         ("v3697-sdk6", "v3698-sdk6"),
                         ("3.6.97", "3.6.98"),
                         ("V3.6.97", "V3.6.98"),
                         ("v3697", "v3698"),
                         ("release-v3697", "release-v3698"),
                         ("staging-v3697", "staging-v3698")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 99 → FASE 100 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 99 → FASE 100 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 99 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
