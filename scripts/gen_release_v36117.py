#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.117-SDK6 (r21).
Crea scripts/release-v36117/ a partir de scripts/release-v36116/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 119
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36117 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36117.py
    python3 scripts/release-v36117/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36116"
DEST = RAIZ / "scripts" / "release-v36117"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 119 — SKINS DE BOLA: primera",
    "personalización de la bola en la historia del juego).",
    "  · CATÁLOGO BOLA_ASPECTOS (c02): 16 skins 100 % COSMÉTICAS —",
    "    clásicas (blanca oficial, naranja 40 mm, menta), locura",
    "    (estrellas doradas, pelota de playa, balón de fútbol, bola 8,",
    "    ojo loco) y planetas (Marte, Luna, Tierra, Lava, Saturno CON",
    "    ARO). Texturas PROCEDURALES en canvas (512×256, RNG con",
    "    semilla fija: Marte es idéntico en los dos cascos) — CERO",
    "    bytes nuevos en el bundle y CERO descargas en el casco.",
    "  · CANDADOS igual que las mesas (r96): reutiliza _mesaLibre() —",
    "    9 libres y 7 con candado (10 victorias o 6★ · racha de 5 o",
    "    3★ de los retos semanales).",
    "  · REGLA DEL DUEÑO: en campeonato la bola cae a la OFICIAL",
    "    (_mesaNativo/_mesaSkinReapply del champloader la cubren sin",
    "    tocar c11); la salida del hall recobra la skin guardada",
    "    (adiós al «blanco seco» tras un campeonato).",
    "  · ESTELA A JUEGO: el reposo de la estela viste el RGB de la",
    "    skin (la firma del poder y el color por spin siguen mandando",
    "    cuando hay efecto).",
    "  · CHISPAS AL BOTAR: pool FIJO 5×8 puntos (40 en total, sin",
    "    asignaciones por bote, vida 0,32 s) del color de la skin —",
    "    el Quest 3 no nota la diferencia.",
    "  · ONLINE: la bola viste la skin del ANFITRIÓN — campo OPCIONAL",
    "    sk en el HELLO v2 (JSON tolerante: los builds viejos no lo",
    "    envían ni lo leen; PROTO/PHYS/códec INTACTOS). Sólo el",
    "    invitado la viste, sin candado (el host ya la desbloqueó).",
    "  · FÍSICA INTACTA (garantía del dueño): ni c04 ni c05 conocen",
    "    las skins — radio, masa, rebote y Magnus untouchables.",
    "  · I18N: 21 claves nuevas en ES y EN (nombres de skins, tarjeta",
    "    BOLA, aviso cosmético, mensaje de elección).",
    "  · TEST NUEVO: test_r21_bolas_v36117 (63/0) — catálogo vivo",
    "    importado, pintores, candados, reglas de champ, red sk,",
    "    i18n doble y garantía de física intacta. QA r21 en verde:",
    "    test_red_nucleo 60/0 · test_p4_selfcheck 41/0 ·",
    "    test_p4_ver_mismatch 27/0 · test_p4_ice 21/0 ·",
    "    test_f1_decode 6/0 · test_m7e_persistencia 19/0 ·",
    "    worker local 85/0 · bump BYTE-EXACTO (10.756.498 B).",
    "  SE CONSERVA TODO: P4.1/P4.2 (avisos de build), M-RED3, M7e,",
    "    CRAZY LINK v2, ELO, matchmaking, retos, superpoderes.",
    "  · sellada a",
    "  3.6.117",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36116", "release-v36117"),
    ("staging-v36116", "staging-v36117"),
    ("V3.6.116-SDK6", "V3.6.117-SDK6"),
    ("3.6.116-SDK6", "3.6.117-SDK6"),
    ("v36116-sdk6", "v36117-sdk6"),
    ("v36116", "v36117"),
    ("3.6.116", "3.6.117"),
    ("fase 118", "fase 119"),
    ("FASE 118", "FASE 119"),
]

# Marcadores sobre el ESTADO POST-SWEEP (el sweep convierte las notas de
# v36116 a 3.6.117; después sustituimos el bloque entero por el de FASE 119).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 118"
FIN_MARCADOR = "'  3.6.117" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.117-SDK6 lista: P4.2 autodiagnóstico de versión al arrancar — ningún build viejo vuelve a colarse en silencio.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.117-SDK6 lista: SKINS DE BOLA — 16 skins cosméticas (estela a juego + chispas + Saturno con aro) y skin del anfitrión por el HELLO v2.')"


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
        # bloque de notas → FASE 119 (entre marcadores literales)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR) - 1:]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36117 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36117/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
