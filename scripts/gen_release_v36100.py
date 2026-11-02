#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36100 — hereda scripts/release-v3699 → scripts/release-v36100
e inserta las NOTAS de la FASE 102 «DUELO REPARADO (r110)».

Ronda 110: PRIORIDAD MÁXIMA del dueño tras la partida real con amigos —
«es imposible golpear la bola… las palas no aparecen donde deberían… veo
su pelota cuando mueve su pala». Cuatro reparaciones de NetLink con banco
de duelo propio en Node (capa GATE r110) y batería BQ intacta.

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v3699).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3699"
DEST = RAIZ / "scripts" / "release-v36100"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 101 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada ya dice 3.6.100)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 101 — M3 PWA INSTALABLE" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.100" + NL + "'"

# líneas de texto PLANO de las notas FASE 102 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 102 — DUELO REPARADO",
    "    '(r110).",
    "    " + "'" + "PRIORIDAD MAXIMA del dueño tras su partida real con amigos: «es",
    "    'imposible golpear la bola… las palas no aparecen donde deberían…",
    "    'veo su pelota cuando mueve su pala». Cuatro reparaciones de fondo en",
    "    'NetLink, probadas con un BANCO DE DUELO nuevo en Node (código real de",
    "    'producción + cable simulado con latencia, jitter y pérdida).",
    "    '",
    "    'Novedades de esta version (frente a V3.6.99-SDK6):",
    "    '",
    "    '  · EL BIT 4 DE LA POSE (la madre del cordero): el emisor lo ponía",
    "    '    con la pala en CUALQUIER mano, pero todos los lectores lo",
    "    '    interpretan como «pala en la mano IZQUIERDA». Un jugador diestro",
    "    '    (el 95%) viajaba mal leído: el rival pintaba su pala en la MANO",
    "    '    LIBRE — donde está la bola del saque («veo su pelota, no su",
    "    '    pala») — y el validador comparaba cada golpe contra la mano",
    "    '    equivocada: rechazos masivos («la bola cae irremediablemente»).",
    "    '    Fix en el emisor + PROTO 3 (builds mezclados caen a v1 honesto).",
    "    '",
    "    '  · VALIDADOR JUSTO: MAX_SPIN 160→220, TOL_FUTURE 120→250 ms y",
    "    '    HIT_NEAR_PAD 0,60→0,85 m — ya no se rechazan golpes legítimos",
    "    '    con latencia/efecto real (rechazar un golpe honesto regala un",
    "    '    punto y congela el rallye). Los topes anti-trampa siguen vivos.",
    "    '",
    "    '  · LA MITAD PROPIA ES JUGABLE EN FANTASMA: el fantasma se simulaba",
    "    '    SIN palas aunque la bola ya estuviera en MI mitad — ventana",
    "    '    muerta de RTT..300 ms por golpeo (a 5 m/s son 1,5 m injugables).",
    "    '    Ahora mi pala participa en mi mitad: mi contacto reclama la",
    "    '    autoridad (HIT validado en el rival, anti-trampa intacto).",
    "    '",
    "    '  · REPARACIÓN DE SAQUE ATASCADO: si el lanzamiento/golpe del saque",
    "    '    rival se pierde, mi bola quedaba HELD para siempre — los SNAPs",
    "    '    del rival (su bola viva) liberan el hold y toman el estado.",
    "    '",
    "    '  · BANCO DE DUELO r110 (capa GATE nueva qa_duelo_r110): dos",
    "    '    extremos completos con el código real (c09+c09b+física c04/c05)",
    "    '    sobre cable 40 ms ±12 ms con pérdida — espejo de pose exacto",
    "    '    diestro y zurdo (0,0 cm · 0,1°), duelo con saque legal",
    "    '    (solucionador real del juego), autoridad, contacto y 0 rechazos.",
    "    '",
    "    '  QA r110 en verde (banco de duelo 9/0 · test_red_nucleo 59/0 ·",
    "    '  batería BQ de 3 duelos reales en paralelo intacta) · sellada a 3.6.100",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36100 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.100.
    for viejo, nuevo in (("V3.6.99-SDK6", "V3.6.100-SDK6"),
                         ("3.6.99-SDK6", "3.6.100-SDK6"),
                         ("v3699-sdk6", "v36100-sdk6"),
                         ("3.6.99", "3.6.100"),
                         ("V3.6.99", "V3.6.100"),
                         ("v3699", "v36100"),
                         ("release-v3699", "release-v36100"),
                         ("staging-v3699", "staging-v36100")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 101 → FASE 102 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 101 → FASE 102 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 101 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
