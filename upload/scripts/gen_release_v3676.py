#!/usr/bin/env python3
"""gen_release_v3676 — hereda scripts/release-v3675 → scripts/release-v3676
e inserta las NOTAS de la FASE 78 «DUELOS LOCOS» en build_zip.py.

Las notas se construyen desde una LISTA de líneas de texto plano y se
unen con la secuencia LITERAL \\n (backslash+n) que espera el string
multi-línea de build_zip.py — cero ambigüedad de escapes.

Idempotente: si release-v3676 ya existe, se regenera desde cero.
"""
import shutil
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3675"
DEST = RAIZ / "scripts" / "release-v3676"

BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)
NLL = NL + NL               # \n\n literal

BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 77 — LA PALA AL MILÍMETRO: «Dentro del Pro" + NL + "'"
BLOQUE_VIEJO_FIN = "    '    campeonatos, 5 poderes, CCD, CRAZY TV y el Hall Of Fame)." + NLL + "'"

# líneas de texto PLANO de las notas FASE 78 (sin escapes: se unen abajo)
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 78 — DUELOS LOCOS: «Vamos con 2 y 3» — el",
    "    'modo multijugador que llevaba el candado de PRÓXIMAMENTE desde la r79",
    "    '(«más adelante se definirán las reglas») se DESBLOQUEA y juega de",
    "    'verdad, y EL PULSO CRAZY completa su puerta física con dos placas de",
    "    'museo en el Hall.",
    "    '",
    "    'Novedades de esta versión (frente a V3.6.75-SDK6):",
    "    '",
    "    '  · DUELOS LOCOS DESBLOQUEADO: la tarjeta del submenú multijugador",
    "    '    deja el velo, el candado y el chip PRÓXIMAMENTE y pasa a ser una",
    "    '    tarjeta con estética común (rayo, hover y chevron como NORMAL).",
    "    '    El flujo de dos pasos r80 se conserva: eliges el modo y la sala",
    "    '    y el código aparecen.",
    "    '",
    "    '  · REGLAS (diseño r84): 1 vs 1 online con el marcador EXACTO de",
    "    '    Normal (mejor de 3, árbitro, CLAIM/ACK y RESYNC intactos) + TRES",
    "    '    PODERES netcode-safe: cada 5 golpes propios (saque incluido)",
    "    '    carga 1 poder ALEATORIO y el gatillo de la mano libre lo libera",
    "    '    con la bola en juego.",
    "    '",
    "    '  · GIGANTE (12 s): tu pala ×1,30 y radio de golpeo ×1,38; el rival",
    "    '    lo VE por el bit 16 del byte de pose (transporte gratis: el",
    "    '    paquete POSE=31 B queda intacto).",
    "    '",
    "    '  · FUEGO (10 s): tus golpes de rally salen ×1,18 (tope interno 26",
    "    '    m/s, por debajo del cap 30 del validador anti-trampa: jamás se",
    "    '    rechaza un golpe legítimo). La velocidad viaja dentro del HIT.",
    "    '",
    "    '  · LOCA (10 s): tus golpes de rally llevan efecto vivo (spin ×2) por",
    "    '    el canal estándar del SÚPER EFECTO; la curva viaja en el spin del",
    "    '    HIT/HANDOFF y el rival la ve en el stream de su mitad.",
    "    '",
    "    '  · EL AVISO SE CANTA: cuando el rival dispara, un mensaje fiable",
    "    '    (\\'pow\\') anuncia «PALA GIGANTE / BOLA FUEGO / BOLA LOCA de tu",
    "    '    rival» con voz y blip — el efecto real viaja por los canales",
    "    '    existentes.",
    "    '",
    "    '  · EL MODO VIAJA EN EL MATCH_START (md): lo decide la tarjeta que",
    "    '    el ANFITRIÓN eligió; el invitado la recibe y obedece (antes el",
    "    '    modo era \\'match\\' hard-coded en el invitado).",
    "    '",
    "    '  · EL PULSO CRAZY EN LA PUERTA DEL HALL: dos placas de museo (el",
    "    '    pintor drawHallSign de la gloria) a los flancos de la pared de",
    "    '    la puerta — «EL PULSO CRAZY · Reto de hoy: <modo>» y «TU RACHA ·",
    "    '    n día(s) · récord r» — repintadas con i18n viva y el estado",
    "    '    diario real cada vez que entras al Hall (drawHall revive del",
    "    '    stub r58).",
    "    '",
    "    '  · Conserva TODO lo anterior (r83: la pala al milímetro con",
    "    '    passthrough inmediato; r82: multijugador al milímetro con",
    "    '    batería en paralelo; r81: autocalibrador de FPS; r80: Reto",
    "    '    Diario en la puerta; r79-r71: CRAZY LINK v2, academia en tus",
    "    '    manos, AJUSTES por subcategorías, passthrough en caliente; 5",
    "    '    campeonatos, 5 poderes, CCD, CRAZY TV y el Hall Of Fame).",
    "    '",
]

BLOQUE_NUEVO = None  # (el bloque real lo construye _construir_bloque())


def _construir_bloque():
    """Une las líneas planas en el formato multi-string de build_zip.py:
    cada línea del texto plano YA trae el prefijo     '... ; entre línea y
    línea del string fuente va un salto REAL, y el contenido interior lleva
    la secuencia LITERAL \\n justo antes de cerrar cada '."""
    partes = []
    for i, ln in enumerate(_NOTAS):
        # el texto plano de cada nota termina con la secuencia literal \n
        partes.append(ln + NL + "'")
    return chr(10).join(partes) + chr(10)


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    txt = BZ.read_text(encoding="utf-8")

    # 1 · identidad de la release: v3675 → v3676 / V3.6.75 → V3.6.76
    txt = txt.replace("V3.6.75-SDK6", "V3.6.76-SDK6")
    txt = txt.replace("3.6.75-SDK6", "3.6.76-SDK6")   # guards contra game_src
    txt = txt.replace("v3675-sdk6", "v3676-sdk6")
    txt = txt.replace("release-v3675", "release-v3676")
    txt = txt.replace("staging-v3675", "staging-v3676")
    txt = txt.replace('grep -c "3.6.75"', 'grep -c "3.6.76"')
    txt = txt.replace("menciones 3.6.75", "menciones 3.6.76")
    txt = txt.replace("no es el v3675", "no es el v3676")
    txt = txt.replace("n3675 = int", "n3676 = int")
    txt = txt.replace("{n3675}", "{n3676}")
    txt = txt.replace("if n3675 < 4:", "if n3676 < 4:")

    # 2 · notas: bloque FASE 77 → bloque FASE 78
    i = txt.find(BLOQUE_VIEJO_INI)
    j = txt.find(BLOQUE_VIEJO_FIN)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("FALLO: bloque de notas FASE 77 no encontrado")
    j += len(BLOQUE_VIEJO_FIN)
    txt = txt[:i] + _construir_bloque() + txt[j:]

    BZ.write_text(txt, encoding="utf-8")

    # 3 · verificación de los guards de versión
    assert "const VERSION = '3.6.76-SDK6'" in txt, "guard VERSION"
    assert "V3.6.76-SDK6" in txt, "badge"
    assert "FASE 78" in txt, "notas FASE 78"
    assert "FASE 77" not in txt, "quedan notas FASE 77"
    print("✓ release-v3676 creada (notas FASE 78, guards V3.6.76-SDK6)")


if __name__ == "__main__":
    main()
