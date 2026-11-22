#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36102 — hereda scripts/release-v36101 → scripts/release-v36102
e inserta las NOTAS de la FASE 104 «M5a IA CON ESTILOS (r112)».

Ronda 112: hito M5a del roadmap MEJORAS.md — 12 personalidades de IA sobre
la MISMA física (sin trampas): ▶ registro OPPONENT_STYLES con multiplicadores
acotados + colocación (canal r95), selector ‹ › en AJUSTES › JUEGO con
persistencia pp_estilo_v1 y recálculo EN VIVO, telemetría ai_style (catálogo
v7, 17 eventos) y ARNÉS DE ESTILOS Node (12 estilos × 30 rallies reales:
cfg acotada + invariantes I1-I4 + 66 parejas distinguibles).

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v36101).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36101"
DEST = RAIZ / "scripts" / "release-v36102"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 103 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.102)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 103 — M4 ONBOARDING" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.102" + NL + "'"

# líneas de texto PLANO de las notas FASE 104 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 104 — M5a IA CON ESTILOS",
    "    '(r112).",
    "    " + "'" + "Hito M5a del roadmap MEJORAS.md: DOCE personalidades de IA sobre",
    "    'la MISMA física — sin trampas, sin atajos, sin parámetros nuevos de",
    "    'motor: multiplicadores ACOTADOS sobre la dificultad que ya tienes.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.101-SDK6):",
    "    '",
    "    '  · 12 ESTILOS DE RIVAL: Clásico (el de siempre, byte-idéntico),",
    "    '    Looper (lifta desde lejos), Chopero (cortada y paciencia),",
    "    '    Bloqueador (pegado a la mesa), Atacante (smash a la primera),",
    "    '    Defensivo (bolas altas del fondo), Dejadas (juego corto),",
    "    '    All-round, Joven nervioso (rápido y desordenado), Veterano",
    "    '    frío (no falla dos veces), Gigante (alcance) y Relámpago",
    "    '    (pequeño y velocísimo). Colocación y celebración propias.",
    "    '  · SELECTOR ‹ › en AJUSTES › JUEGO: el nombre queda a la vista,",
    "    '    persiste (pp_estilo_v1) y se aplica EN VIVO sin reiniciar.",
    "    '  · SIN TRAMPAS, CON PRUEBA: arnés de estilos Node (qa_estilos_",
    "    '    r112) — 12 estilos × 30 rallies con física, árbitro e IA reales:",
    "    '    cfg acotada (NT-1), invariantes I1-I4, firma ≠ clásico (D-1) y",
    "    '    66/66 parejas de estilos distinguibles (D-2). La IA jamás cruza",
    "    '    la red y su velocidad sigue clamped por el solver legal.",
    "    '  · TELEMETRÍA (catálogo v7, 17 eventos): ai_style (est + dif) en",
    "    '    cada partido local con estilo ≠ clásico — qué personalidades",
    "    '    eligen los jugadores, con datos.",
    "    '  · LA ESCALERA DE CARRERA (bronce→leyenda) llega con M5b: los",
    "    '    rivales de campeonato heredarán estilos entonces (hoy el",
    "    '    campeonato manda, como siempre).",
    "    '",
    "    '  QA r112 en verde (capa r112 con arnés de estilos integrado ·",
    "    '  qa_telemetria 132/0 · presupuesto refrescado) · sellada a 3.6.102",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36102 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.102.
    for viejo, nuevo in (("V3.6.101-SDK6", "V3.6.102-SDK6"),
                         ("3.6.101-SDK6", "3.6.102-SDK6"),
                         ("v36101-sdk6", "v36102-sdk6"),
                         ("3.6.101", "3.6.102"),
                         ("V3.6.101", "V3.6.102"),
                         ("v36101", "v36102"),
                         ("release-v36101", "release-v36102"),
                         ("staging-v36101", "staging-v36102")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 103 → FASE 104 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 103 → FASE 104 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 103 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
