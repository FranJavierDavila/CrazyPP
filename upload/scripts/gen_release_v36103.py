#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36103 — hereda scripts/release-v36102 → scripts/release-v36103
e inserta las NOTAS de la FASE 105 «AJUSTES DEL DUEÑO (r113)».

Ronda 113: seis peticiones del dueño sobre el juego vivo —
  · CHINCHETA del menú: icono en el centro superior; por defecto OFF; al
    pulsarla el panel queda ANCLADO en su punto del espacio; otro pulso lo
    suelta (vuelve a seguir a la cabeza).
  · FÍSICA DEL GOLPE FUERTE: velocidad REAL según el swing (techo de pala
    12→16, techo de bola 14→18, filtro más rápido, empuje de cuerpo
    0,22→0,40) y DIRECCIÓN AL OBJETIVO (la salida gira hacia el swing).
  · CPU INTELIGENTE: no falla bolas fáciles; el fallo es esfuerzo (bolas
    rápidas, escoradas o de colocación extrema).
  · SUPERPODERES: NUNCA se anuncian con la bola viniendo hacia el jugador
    (el congelado le robaba el golpeo) — flanco invertido en los 5
    campeonatos.
  · LA LOCURA · ETAPA 4 (ARKANOID 2) relajada: 45 ladrillos, 3,5 min,
    menos azules, conversión más lenta, bomba cada 20 s.
  (La mesa de palas del Hall ya se retiró en la FASE 32, a petición propia.)

Lección de la r93 aplicada: los tokens heredados se re-anclan TODOS antes
de insertar el bloque de notas. Idempotente (regenera desde v36102).
"""
import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36102"
DEST = RAIZ / "scripts" / "release-v36103"
BZ = DEST / "build_zip.py"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

# ── bloque FASE 104 completo en el build_zip heredado (ini → fin exactos) ──
# (el fin se busca TRAS la pasada de tokens: la cola heredada "sellada a
# 3.6.102" ya quedó re-anclada a 3.6.103 por la pasada 1)
BLOQUE_VIEJO_INI = "    'Rama    : main · SDK6 (FASE 104 — M5a IA CON ESTILOS" + NL + "'"
BLOQUE_VIEJO_FIN = " · sellada a 3.6.103" + NL + "'"

# líneas de texto PLANO de las notas FASE 105 (se unen abajo con NL + "'")
_NOTAS = [
    "    'Rama    : main · SDK6 (FASE 105 — AJUSTES DEL DUEÑO",
    "    '(r113).",
    "    " + "'" + "Seis ajustes pedidos a boca de jarra sobre el juego vivo: cómo se",
    "    'sujeta el menú, cómo se siente el golpe fuerte, cómo falla la IA,",
    "    'cuándo anuncia sus poderes el rival y cuánto exige la etapa 4.",
    "    '",
    "    'Novedades de esta version (frente a V3.6.102-SDK6):",
    "    '",
    "    '  · CHINCHETA DEL MENÚ: icono de chincheta SIEMPRE visible en el",
    "    '    centro superior del panel. Por defecto OFF (el menú se ancla",
    "    '    delante de ti, flota 1,8 s y queda fijo — como siempre). Al",
    "    '    pulsarla, el menú queda ANCLADO al punto del espacio donde",
    "    '    estaba en ese instante (ni flotación ni re-anclajes al",
    "    '    reabrir). Otro pulso lo suelta: regresa a tu cabeza.",
    "    '  · FÍSICA DEL GOLPE FUERTE: la bola sale con la VELOCIDAD REAL",
    "    '    del swing — techo de pala 12→16 m/s, techo de bola 14→18 m/s,",
    "    '    filtro de mano más rápido (ventana 45→32 ms) y el cuerpo de",
    "    '    la pala empuja el doble (0,22→0,40). Y DIRECCIÓN AL OBJETIVO:",
    "    '    en swings vivos la salida gira hacia donde mueves la mano",
    "    '    (hasta 45°), no hacia donde apunta la madera — los toques",
    "    '    suaves no se tocan y el saque sigue validado por su solver.",
    "    '  · CPU INTELIGENTE: la IA ya NO falla bolas cómodas a la pala.",
    "    '    El fallo ahora es ESFUERZO: bolas rápidas, escoradas que",
    "    '    obligan a viajar o colocaciones extremas. La torpeza del",
    "    '    nivel fácil y las 12 personalidades M5a se conservan.",
    "    '  · SUPERPODERES JUSTOS: en los CINCO campeonatos (Locura, Magia,",
    "    '    Oeste, Halloween y Estación Orbital) el rival anuncia su",
    "    '    poder SÓLO con la bola yendo hacia él — nunca con la bola",
    "    '    viniendo a ti: el congelado del anuncio ya no te roba el",
    "    '    golpeo.",
    "    '  · LA LOCURA · ETAPA 4 (ARKANOID 2) RELAJADA: muro 9×5 (45",
    "    '    ladrillos, antes 54), 3,5 minutos (antes 2,5), 24% de",
    "    '    azules (antes 30%), conversión rojo→azul más lenta (20 s de",
    "    '    gracia y cada 11 s) y bomba cada 20 s (antes 15).",
    "    '  · El Hall ya no tenía mesa de palas (se retiró en la FASE 32):",
    "    '    esta ronda lo confirma — nada que quitar hoy.",
    "    '",
    "    '  QA r113 en verde (gate completo re-anclado: arnés físico con",
    "    '  hash nuevo por la física honesta del golpe · capas de versión",
    "    '  a 3.6.103) · sellada a 3.6.103",
]

NOTAS_NUEVAS = chr(10).join(ln + NL + "'" for ln in _NOTAS)


def main():
    if not ORIGEN.exists():
        sys.exit(f"FALLO: no existe {ORIGEN}")
    if DEST.exists():
        shutil.rmtree(DEST)
        print("· release-v36103 previo retirado (regeneración íntegra)")
    shutil.copytree(ORIGEN, DEST)
    print(f"· release heredado: {ORIGEN.name} → {DEST.name}")

    t = BZ.read_text(encoding="utf-8")
    n_ok = 0

    # 1) tokens de versión (headers, guards, nombres de ZIP). Se re-anclan
    #    PRIMERO: la cola del bloque heredado queda ya a 3.6.103.
    for viejo, nuevo in (("V3.6.102-SDK6", "V3.6.103-SDK6"),
                         ("3.6.102-SDK6", "3.6.103-SDK6"),
                         ("v36102-sdk6", "v36103-sdk6"),
                         ("3.6.102", "3.6.103"),
                         ("V3.6.102", "V3.6.103"),
                         ("v36102", "v36103"),
                         ("release-v36102", "release-v36103"),
                         ("staging-v36102", "staging-v36103")):
        n = t.count(viejo)
        if n:
            t = t.replace(viejo, nuevo)
            n_ok += n
            print(f"· tokens {viejo} → {nuevo}: {n}")

    # 2) bloque de notas FASE 104 → FASE 105 (después de los tokens)
    i0 = t.find(BLOQUE_VIEJO_INI)
    i1 = t.find(BLOQUE_VIEJO_FIN)
    if i0 >= 0 and i1 > i0:
        t = t[:i0] + NOTAS_NUEVAS + t[i1 + len(BLOQUE_VIEJO_FIN):]
        print("· notas FASE 104 → FASE 105 insertadas")
    else:
        sys.exit("FALLO: bloque FASE 104 no encontrado para sustituir")

    BZ.write_text(t, encoding="utf-8")
    print(f"· build_zip reescrito ({BZ}) — {n_ok} tokens re-anclados")


if __name__ == "__main__":
    main()
