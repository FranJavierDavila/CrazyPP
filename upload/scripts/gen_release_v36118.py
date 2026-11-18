#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.118-SDK6 (r23).
Crea scripts/release-v36118/ a partir de scripts/release-v36117/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 120
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36118 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36118.py
    python3 scripts/release-v36118/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36117"
DEST = RAIZ / "scripts" / "release-v36118"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 120 — SPIN VISIBLE DE LA BOLA +",
    "HALL DEL ANFITRIÓN: la bola gira y el hall presume).",
    "  · F1 · SPIN VISIBLE: la bola GIRA sobre el eje de su ω REAL — el",
    "    mismo vector que ya calculaba la física para Magnus y el bote",
    "    (c04/c05 INTACTOS: es puro render). Adiós al Euler X/Y con",
    "    factor 0.05 que dejaba la textura de las skins pintada y",
    "    estática. rotateOnWorldAxis con ω normalizado y ganancia 0.14:",
    "    |ω|=110 (tope) ≈ 2,4 rev/s legibles a 72 Hz sin estrobar; el",
    "    LATIGAZO del bote sale gratis (la fricción actualiza ω en cada",
    "    rebote). Reposo honesto: |ω|<0,5 rad/s → sin giro fantasma.",
    "  · F1b · RED SIN CAMBIOS: ω YA viajaba al invitado — v1 lo trae",
    "    el stream (h/estado de bola con s:[x,y,z] + spinFromNet) y v2",
    "    lo traen HIT/TOSS/HANDOFF (ev.s) mientras el fantasma simula",
    "    con la física real. El invitado ve el MISMO giro desde el día 1.",
    "  · F2 · HALL DEL ANFITRIÓN: ambos jugadores pueden estar en el",
    "    hall del anfitrión para PRESUMIR de lo conseguido. El HELLO v2",
    "    lleva hp (perfil OPCIONAL: victorias, mejor racha, ★ de retos,",
    "    ELO, logros ACHIEVEMENTS y skins de bola/mesa desbloqueadas;",
    "    JSON tolerante como sk — builds viejos no lo envían ni lo",
    "    leen). El invitado lo SANEÍA a fondo (números acotados, ids",
    "    contra catálogo, arrays con tope).",
    "  · PARED DE INSIGNIAS: placa de museo 1024×640 100 % PROCEDURAL",
    "    (c08 drawHallGloria) en el frente del hall — 6 medallones de",
    "    logros (oro/gris), 16 chips de bola y 5 paletas de mesa; lo no",
    "    conseguido se pinta apagado: la vitrina que ANIMA a por él.",
    "    Cero bytes en el bundle, cero descargas (canvas como siempre).",
    "  · VISITA ONLINE: enterHall admite online (modo _hallVisit) — en",
    "    pleno rally no se visita; la física de red SIGUE VIVA detrás",
    "    del museo (fantasma v2 / stream v1 sin tocar); MATCH_START",
    "    saca al visitante antes de la cuenta atrás; la desconexión",
    "    re-entra al hall PROPIO. El avatar del rival duerme en el",
    "    museo (ni pala ni visor flotando entre cuadros).",
    "  · TARJETA HALL en AJUSTES→SALA (4.ª) con subpágina salahall y",
    "    botón ENTRAR AL HALL — la tuya, o LA DEL ANFITRIÓN online.",
    "  · _bolaSkinEfectiva: la restauración del hall NO desviste la",
    "    skin del anfitrión en el invitado (la r22 queda blindada).",
    "  · I18N: 14 claves nuevas ES/EN + hint_sala_bola (la r21 lo dejó",
    "    huérfano).",
    "  · FÍSICA INTACTA (garantía del dueño): ni c04 ni c05 conocen el",
    "    mesh, el giro visible ni el hall profile — cero rotaciones en",
    "    la física, cero campos nuevos en el códec binario.",
    "  · TEST NUEVO: test_r23_hall_spin_v36118 (81/0) — spin, red ω,",
    "    perfil hp saneado, placa, visita, menú, i18n doble y garantía",
    "    de física intacta. Regresión r21: 63/0. QA ronda: A-D verde",
    "    (23+11+29+14) · bump BYTE-EXACTO (10.777.222 B).",
    "  SE CONSERVA TODO: skins r21, P4.1/P4.2, M-RED3, M7e, CRAZY",
    "    LINK v2, ELO, matchmaking, retos, superpoderes.",
    "  · sellada a",
    "  3.6.118",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36117", "release-v36118"),
    ("staging-v36117", "staging-v36118"),
    ("V3.6.117-SDK6", "V3.6.118-SDK6"),
    ("3.6.117-SDK6", "3.6.118-SDK6"),
    ("v36117-sdk6", "v36118-sdk6"),
    ("v36117", "v36118"),
    ("3.6.117", "3.6.118"),
    ("fase 119", "fase 120"),
    ("FASE 119", "FASE 120"),
]

# Marcadores sobre el ESTADO POST-SWEEP (el sweep convierte las notas de
# v36117 a 3.6.118; después sustituimos el bloque entero por el de FASE 120).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 119"
FIN_MARCADOR = "'  3.6.118" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.118-SDK6 lista: SKINS DE BOLA — 16 skins cosméticas (estela a juego + chispas + Saturno con aro) y skin del anfitrión por el HELLO v2.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.118-SDK6 lista: SPIN VISIBLE (la bola gira sobre su ω real) + HALL DEL ANFITRIÓN (pared de insignias por HELLO v2 y visita online al museo).')"


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
        # bloque de notas → FASE 120 (entre marcadores literales)
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR) - 1:]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36118 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36118/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
