#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.128-SDK6 (r32).
Crea scripts/release-v36128/ a partir de scripts/release-v36127/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 130
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36128 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36128.py
    python3 scripts/release-v36128/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36127"
DEST = RAIZ / "scripts" / "release-v36128"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 130 — SALONES DEL DUEÑO: tu arte en los",
    "3 salones y música ambiental propia con icono de silencio en la",
    "pared — prioridad total del salón sobre cualquier otra melodía).",
    "  · 1 · EL ARTE DEL DUEÑO: los 18 planos de DOJO ZEN (dojo/),",
    "    OBSERVATORIO ESTELAR (observatorio/) y SALÓN NEÓN ARCADE",
    "    (neon/) son AHORA los ficheros preparados por el dueño (ZIPs",
    "    Dojo/Observatorio/Arcade — sha256 byte-exacto en el test), en",
    "    las medidas EXACTAS de la spec v3.6.28 (frente/fondo 1849×864 ·",
    "    laterales 2395×864 · suelo/techo 1296×1678). Sustituyen al arte",
    "    IA de la r30 en las MISMAS fichas y rutas: cero código de carga",
    "    tocado.",
    "  · 2 · MÚSICA AMBIENTAL DEL SALÓN: dojo.mp3, arcade.mp3 y",
    "    observatorio.mp3 (pistas del dueño) junto a su arte; campo",
    "    `musica` en las TRES variantes de HALL_VARIANTES (c02 — museo y",
    "    CABAÑA callan). Canal hall NUEVO en c03 (setHallWanted/",
    "    startHallMusic/stopHallMusic/setHallMute/_loadHallMusic): bucle",
    "    con fundidos (entrada 1,2 s · salida 1,0 s), volumen 0,30",
    "    escalado por el canal MÚSICA (r95), caché de buffers por URL y",
    "    robustez de la casa (el fetch fallido nunca rompe el salón).",
    "    Ciclo de vida: enterHall la arranca, exitHall la apaga,",
    "    hall_var la cambia EN VIVO y la visita online suena COMO EL",
    "    ANFITRIÓN (la pista viaja con el arte, hp.hv).",
    "  · 3 · PRIORIDAD del dueño: «cuando en el Hall tenemos activada su",
    "    música no sonará ninguna otra en esta estancia» — INVARIANTE UNA",
    "    MELODÍA ampliado al sentido SALÓN→menú: startHallMusic retira la",
    "    del menú y el guard de startMusic impide que renazca mientras el",
    "    salón la tenga activada; al re-adoptar contexto (Quest) la pista",
    "    del salón rearranca ANTES que la del menú.",
    "  · 4 · ICONO DE SILENCIO EN LA PARED: placa vectorial 100 % canvas",
    "    (drawHallMusica — altavoz dorado con ondas SONANDO · barra roja",
    "    SILENCIADO) en la pared FRONTAL, sobre la placa de insignias;",
    "    sólo se ve en salones CON pista. El GATILLO VR apuntándola la",
    "    conmuta (raycast propio con far 10 m — el far=2,5 del menú queda",
    "    intacto), funciona con el menú abierto (si el rayo no cae en",
    "    botón) y cerrado; el hover la agranda con suavizado; el estado",
    "    persiste (pp_hallmus) y al silenciar el menú recupera su música",
    "    si la quería. i18n msg_hallmus ES/EN («Música del salón: Sí/No»).",
    "  · 5 · TEST NUEVO: test_r32_salones_v36128 (49/0) — 18 JPG + 3 MP3",
    "    byte-exacto contra los ZIPs del dueño, canal hall completo,",
    "    prioridad SALÓN→menú (guard + retirada + orden de re-adoptar),",
    "    icono (pintor, repinta, hover, raycast, doble gancho del",
    "    gatillo), i18n ES/EN, cableos enterHall/exitHall/hall_var/",
    "    onPeerHall y c04/c05 byte-exacto. Regresión re-anclada r32:",
    "    r31 47/0, r30 54/0 (el arte del dueño también supera la riqueza",
    "    y las medidas exactas), r29 75/0, r28 37/0, r27 40/0, r26b",
    "    171/0 (post-commit).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO contra la r26b; cero cambios de códec en c09.",
    "  · bump BYTE-EXACTO (11.185.934 B · golden 780de58f…).",
    "  SE CONSERVA TODO: higiene Fénix r31, Fénix jugable r30, Súper",
    "    Oscuridad, Crono centrado, voces Piper animosas, iconos del",
    "    dueño, bug de la bola oculta cerrado (r28), FORO3D completo",
    "    (r27), bola atractora y ráfagas r26/r26b, barrera eléctrica,",
    "    skins r21, hall cabaña, cortina etapas 2/4, _bolaGuard, P4,",
    "    CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.128",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36127", "release-v36128"),
    ("staging-v36127", "staging-v36128"),
    ("V3.6.127-SDK6", "V3.6.128-SDK6"),
    ("3.6.127-SDK6", "3.6.128-SDK6"),
    ("v36127-sdk6", "v36128-sdk6"),
    ("v36127", "v36128"),
    ("3.6.127", "3.6.128"),
    ("fase 129", "fase 130"),
    ("FASE 129", "FASE 130"),
    ("Fase 129", "Fase 130"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r31 a FASE 130/3.6.128 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 130 — HIGIENE TEXTUAL"
FIN_MARCADOR = "'  3.6.128" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.128-SDK6 lista: el registro de poderes ya cuenta la verdad de Fénix (dinámica normal, saques normales, la falta del 15 % para la IA) — deuda cosmética de la r30 pagada sin tocar una línea de lógica.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.128-SDK6 lista: los 3 salones visten el ARTE DEL DUEÑO con su música ambiental (prioridad sobre el menú) y el icono de silencio en la pared frontal.')"


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 130 (sustitución EXACTA, lección r24:
        # sin conservar la comilla de cierre del marcador FIN)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36128 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36128/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
