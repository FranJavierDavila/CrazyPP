#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.125-SDK6 (r29).
Crea scripts/release-v36125/ a partir de scripts/release-v36124/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 127
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36125 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36125.py
    python3 scripts/release-v36125/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36124"
DEST = RAIZ / "scripts" / "release-v36125"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 127 — SUPERPODERES R29: Fénix con el",
    "fuego real del Wizard, anillos del Crono centrados y el Hielo",
    "SUSTITUIDO por el Superpoder de la Oscuridad — informe del dueño).",
    "  · 1 · SÚPER FÉNIX (bola de fuego REAL): «No aparece la llama en la",
    "    bola ni las ascuas naranja… ya teníamos una bola en llamas con un",
    "    poder que lanza Wizard y que funcionaba bien» — CAUSA RAÍZ: el",
    "    halo de r26b vivía en this.scene con coordenadas del RIG; el rig",
    "    rota/recentra y el fx se DESPEGABA de la bola. CURA: el fuego de",
    "    magia v2.120 PORTADO a c12 — tinta brasa 0xff5a12 + emisivo",
    "    0xff3608, pool de 16 bocanadas aditivas (~35/s nacen en la bola,",
    "    suben, encogen y se apagan), ESTELA naranja (TRAIL_PODER.fenix)",
    "    y EXPLOSIÓN de 14 ascuas con gravedad + chasquido cada vez que la",
    "    bola encendida golpea PALA o MESA (gancho en los eventos «table»",
    "    y «paddle»). TODO en el rig (la lección r29).",
    "  · 2 · SÚPER CRONO (anillos centrados): «los 3 anillos de reloj",
    "    deben estar perfectamente centrados en la bola… tienen un",
    "    desplazamiento hacia la derecha» — el grupo de anillos es HIJO",
    "    de ballMesh: centrado POR CONSTRUCCIÓN, cero lag de frame (antes",
    "    se posicionaba con ball.pos un frame atrás y en espacio escena),",
    "    re-anclaje en el trigger e idempotente. Órbita y 62 % intactos.",
    "  · 3 · SÚPER OSCURIDAD (10.º poder; SUSTITUYE a SÚPER HIELO, que se",
    "    ANULA — orden del dueño): ventana de 20 s; la bola se vuelve",
    "    NEGRA (carbón 0x0d0b0e) con emisivo rojo fuego + HALO aditivo",
    "    que respira pegado a ella; CADA golpeo del rival cria en su",
    "    zona una NIEBLA densa de humo oscuro (~0,5 m — tres palas) que",
    "    reduce la visibilidad ~75 %: 5 s plena + ~2 s de disipación",
    "    (expandiéndose y subiendo), hasta 6 zonas simultáneas (recicla",
    "    la más vieja), con 4 destellos rojos PARPADEANDO dentro (los",
    "    «pequeños ojos»). La IA, ciega, manda LARGO el 35 % de sus",
    "    devoluciones (sorteo por golpeo; el solucionador c05 apunta",
    "    0,25-0,70 m más allá de la línea de fondo; el saque de la IA no",
    "    se sabotea; en dobles también el rival 2). Icono del dueño",
    "    SuperPala_Oscuridad.png. c04/c05 INTACTOS.",
    "  · 4 · VOCES PIPER (la voz de siempre): «la voz que has usado para",
    "    los superpoderes me gustaría que fuese la misma que ya estábamos",
    "    usando para los superpoderes anteriores… una voz en castellano",
    "    mucho más animosa y enérgica» — red/elec (r25 las dejó en",
    "    espeak-ng) y fénix/crono REGENERADAS con Piper es_ES-davefx-",
    "    medium (ES) / en_US-lessac-medium (EN) — la MISMA receta r44",
    "    (length-scale 0,92/0,95 + recorte de silencios + loudnorm +",
    "    MP3 48 kHz mono 64k) — y voz NUEVA «¡Súper oscuridad!».",
    "  · 5 · ICONOS DEL DUEÑO: SuperPala_Fenix.png, SuperPala_Cronos.png",
    "    y SuperPala_Oscuridad.png (256×256, cuantizados a 256 colores)",
    "    sustituyen a los generados en r26b (los viejos, eliminados).",
    "  · 6 · FIX DEL ENSAMBLADOR: el mount del repo NO trunca al",
    "    sobrescribir — el build 3.6.125 es el PRIMERO que ENCOGE (los",
    "    assets Piper pesan menos que espeak) y salió un game.html",
    "    HÍBRIDO (cola vieja pegada). Escritura atómica temp +",
    "    os.replace en build_game.py (patrón deploy_pages.py).",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO contra la r26b; cero cambios de códec en c09.",
    "  · TEST NUEVO: test_r29_sup_poderes_v36125 (75/0) — fuego real,",
    "    ascuas con gancho ×2, anillos hijos de la bola, oscuridad",
    "    completa, Hielo anulado, iconos/voces del dueño, i18n, dobles,",
    "    lección rig. Regresión r28 37/0 (re-anclada r29), r27 40/0",
    "    (re-anclada r29), r26b 173/0 (re-anclada r29), r26 109/0,",
    "    r25 150/0 (re-anclada r29), r24 89/0, r23 81/0 y r21 63/0.",
    "    bump BYTE-EXACTO (11.165.405 B · golden 12e7a09a…).",
    "  SE CONSERVA TODO: bug de la bola oculta cerrado (r28), salones",
    "    de lujo y mobiliario 3D (r28), FORO3D completo (r27), bola",
    "    atractora y ráfagas r26/r26b, Súper Fénix/Crono, barrera",
    "    eléctrica, skins r21, hall cabaña, cortina etapas 2/4,",
    "    _bolaGuard, P4, CRAZY LINK v2, ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.125",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36124", "release-v36125"),
    ("staging-v36124", "staging-v36125"),
    ("V3.6.124-SDK6", "V3.6.125-SDK6"),
    ("3.6.124-SDK6", "3.6.125-SDK6"),
    ("v36124-sdk6", "v36125-sdk6"),
    ("v36124", "v36125"),
    ("3.6.124", "3.6.125"),
    ("fase 126", "fase 127"),
    ("FASE 126", "FASE 127"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r28 a FASE 127/3.6.125 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 127 — BOLA JAMÁS OCULTA +"
FIN_MARCADOR = "'  3.6.125" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.125-SDK6 lista: la bola JAMÁS queda oculta (cura triple en la tormenta) + 3 salones rediseñados con arte de lujo y mobiliario 3D vivo.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.125-SDK6 lista: Fénix arde con el fuego real del Wizard, los anillos del Crono van centrados en la bola y el Hielo deja paso al Superpoder de la Oscuridad (niebla + IA 35 % fuera).')"


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
        # bloque de notas → FASE 127 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36125 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36125/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
