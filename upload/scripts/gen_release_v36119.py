#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.119-SDK6 (r24).
Crea scripts/release-v36119/ a partir de scripts/release-v36118/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 121
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36119 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36119.py
    python3 scripts/release-v36119/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36118"
DEST = RAIZ / "scripts" / "release-v36119"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 121 — SPIN REALISTA +",
    "HALL CABAÑA: la bola rueda de verdad y el hall estrena refugio).",
    "  · 1 · SPIN REALISTA (queja del dueño tras probar la r23: «el giro",
    "    es muy sutil y poco realista, al dar efecto no se nota el spin",
    "    que debería tener la bola»). Dos causas, DOS CURAS:",
    "      a) GANANCIA 0.14 → 0.45 (×3.2, c12): |ω|=110 (tope) marca",
    "         ~7,9 rev/s (39,5°/frame a 72 Hz — bajo el umbral de",
    "         estrobo); |ω|=25 (EFECTO_SPIN_MIN) ~1,8 rev/s; un efecto",
    "         medio (|ω|≈60) rueda a ~4,3 rev/s: SE VE girar. El",
    "         LATIGAZO del bote sigue saliendo gratis (la fricción ya",
    "         actualiza ω en cada rebote).",
    "      b) TEXTURA: las 4 skins planas (blanca/naranja/menta/neón)",
    "         eran COLOR LISO — una esfera uniforme NO delata su ω ni a",
    "         8 rev/s. bolaTex (c07) les pinta como a las bolas de",
    "         verdad: COSTURA ecuatorial de poliplástico + MARCA de",
    "         fábrica «CRAZY» con pala en miniatura, en dos caras",
    "         opuestas (legible desde cualquier ángulo). El mapa",
    "         multiplica el color: las marcas salen del tono de cada",
    "         bola. Canvas procedural: cero bytes en el bundle.",
    "  · 2 · HALL CABAÑA (las 6 imágenes del dueño, Hallcabana.zip):",
    "    chimenea de piedra con brasero, barra con botellas y perchero",
    "    de astas, ventanal nevado con banco de pieles, alfombra sobre",
    "    parqué de espiga y techo de vigas con lámpara de astas. Arte en",
    "    assets/hall/cabana/ (1,06 MB re-comprimidos, proporciones",
    "    EXACTAS de los planos: 1849×864 · 2395×864 · 1296×1678). Se",
    "    libera con 10 victorias («wins10» — el mismo candado de las",
    "    skins de gala, _mesaLibre). HALL_VARIANTES + hallVariantePorId",
    "    en c02; createHall(base) + vestir() + applyHallVariant en c08",
    "    (re-vestido EN VIVO, dispose del arte anterior, carga a prueba",
    "    de fallos — el juego sigue sin arte).",
    "  · 3 · AJUSTES→SALA→HALL: fila ARTE DEL HALL (MUSEO / LA CABAÑA 🔒)",
    "    con hint por botón; elegir guarda en LS «pp_hallvar» y re-viste",
    "    al vuelo. Oculto de visita online (el arte manda el anfitrión).",
    "  · 4 · ONLINE: el HELLO v2 lleva hv dentro de hp (id saneado contra",
    "    catálogo, patrón sk/hp de las r22/r23; builds viejos no lo envían",
    "    ni lo leen). De visita se entra AL ARTE DEL ANFITRIÓN aunque a",
    "    uno no le hayan liberado la cabaña: se VE, no se elige. c09 sin",
    "    cambios de códec.",
    "  · 5 · I18N: 6 claves nuevas ES/EN (hall_var_* · msg_hall_var ·",
    "    hint_hall_var_*).",
    "  · FÍSICA INTACTA (garantía del dueño): ni c04 ni c05 conocen el",
    "    mesh, el giro visible, el arte del hall ni pp_hallvar.",
    "  · TEST NUEVO: test_r24_spin_cabana_v36119 (89/0) — ganancia,",
    "    costura/marca, catálogo, re-vestido, red hv, assets JPEG con",
    "    proporciones, i18n doble y garantía de física intacta.",
    "    Regresión r23 81/0 y r21 63/0 (2 aserciones actualizadas a la",
    "    evolución r24, comentadas). QA A-D verde. bump BYTE-EXACTO",
    "    (10.787.766 B · golden 50fc0842…).",
    "  SE CONSERVA TODO: skins r21, P4.1/P4.2, M-RED3, M7e, CRAZY",
    "    LINK v2, ELO, matchmaking, retos, superpoderes, hall r23.",
    "  · sellada a",
    "  3.6.119",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36118", "release-v36119"),
    ("staging-v36118", "staging-v36119"),
    ("V3.6.118-SDK6", "V3.6.119-SDK6"),
    ("3.6.118-SDK6", "3.6.119-SDK6"),
    ("v36118-sdk6", "v36119-sdk6"),
    ("v36118", "v36119"),
    ("3.6.118", "3.6.119"),
    ("fase 120", "fase 121"),
    ("FASE 120", "FASE 121"),
]

# Marcadores sobre el ESTADO POST-SWEEP (el sweep convierte las notas de
# v36118 a 3.6.119; después sustituimos el bloque entero por el de FASE 121).
# NOTA r24: la r23 no llegó a sustituir las notas del ZIP (su marcador
# «FASE 119» no casó tras el sweep) — el bloque heredado es el de P4.2
# re-sellado a FASE 121; este generator SÍ lo sustituye de raíz.
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 121 — P4.2"
FIN_MARCADOR = "'  3.6.119" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.119-SDK6 lista: SPIN VISIBLE (la bola gira sobre su ω real) + HALL DEL ANFITRIÓN (pared de insignias por HELLO v2 y visita online al museo).')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.119-SDK6 lista: SPIN REALISTA (ganancia ×3.2 + costura y marca CRAZY en las planas) + HALL CABAÑA (el arte del dueño, liberado con 10 victorias, viaja por hp.hv).')"


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
        # bloque de notas → FASE 121 (entre marcadores literales).
        # r24 · fix: el slice conservaba la comilla de cierre del marcador
        # (bug heredado del generador r23, que nunca llegó a dispararse) y
        # partía el literal — ahora el bloque se sustituye EXACTO.
        i = txt.find(INI_MARCADOR)
        j = txt.find(FIN_MARCADOR, i) if i >= 0 else -1
        if i >= 0 and j >= 0:
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    print(f"\nrelease-v36119 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36119/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
