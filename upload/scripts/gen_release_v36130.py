#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.130-SDK6 (r34).
Crea scripts/release-v36130/ a partir de scripts/release-v36129/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 132
    (con ABORTE DURO si los marcadores no casan — lección r33: la
    sustitución silenciosa dejó las notas de la r32 en el ZIP v36129)
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36130 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36130.py
    python3 scripts/release-v36130/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36129"
DEST = RAIZ / "scripts" / "release-v36130"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 132 — CORRECCIONES A LOS SUPERPODERES",
    "DE PALA: informe del dueño tras V3.6.129 — Red alineada, voz de",
    "selección para todos, Electricidad con retención visible y fin por",
    "baja, y Prisma que sólo pinta en campo rival).",
    "  · 1 · FIX A · FX DE MESA AL RIG (alineación, informe del dueño:",
    "    «el efecto de electricidad sobre la red no está correctamente",
    "    alineado con el plano de la red»): los FX de r25 colgaban de",
    "    this.scene en coordenadas de MESA, pero la mesa vive dentro de",
    "    this.rig y onSessionStart GIRA el rig (updateRecenter, 25 frames)",
    "    según hacia dónde mire el dueño al entrar en el visor. Ahora el",
    "    cuerpo/arcos/riel de la BARRERA DE LA SÚPER RED, la niebla/los",
    "    rayos/los pedacitos de la TORMENTA, el anillo de bote del SÚPER",
    "    EFECTO y los sprites del PORTAL cuelgan del rig (patrón r33:",
    "    «¡espacio de la mesa, NO this.scene!»). Mismas coordenadas y",
    "    misma lógica — sólo cambia el padre. scene.add queda para lo que",
    "    es MUNDO de verdad (rig, hall, menú, flechas del icono, visor",
    "    de red, anillos-billboard del portal, tutorial del servido).",
    "  · 2 · FIX B · VOZ DEL SELECTOR PARA TODOS (informe del dueño:",
    "    «todos los nuevos deben tener el audio disparador cuando se",
    "    seleccionan — en inglés el poder de Fénix no tiene su audio»):",
    "    Fénix/Crono/Oscuridad (r26b/r29) estaban FUERA del mapeo",
    "    _vozSelFuente y el joystick los ciclaba EN SILENCIO. Entran con",
    "    su voz de concesión (patrón red/elec r25) + precaliente: los 14",
    "    poderes + «Sin poder» hablan en ES y EN.",
    "  · 3 · FIX C · ELECTRICIDAD TERMINA CON LA BAJA (informe del dueño:",
    "    «si al aplicarlo en algún momento el rival pierde una bola, el",
    "    superpoder se suspende y termina — la penalización no puede ser",
    "    mayor de 1 bola perdida»): _elecRompe cierra la tormenta al",
    "    instante (_elecFin(true), sin pisar el mensaje del punto).",
    "  · 4 · FIX D · EL RAYO SE VÉ ALCANZAR LA BOLA (informe del dueño:",
    "    «no te enteras de que un rayo ha alcanzado la bola; más bien",
    "    reforzar el efecto cuando existe alcance parando la bola 1",
    "    segundo con un halo de luz y pequeños rayos saliendo de ella",
    "    antes de ser destruida»): el impacto YA NO rompe al vuelo —",
    "    _elecAgarra congela la bola con el ppTransito del PORTAL (c04 no",
    "    la integra, c05 no la golpea, el árbitro no ve un evento: física",
    "    INTACTA), la bola cuelga 1 s (ELEC_AGARRA_T) con HALO DE LUZ y 6",
    "    MINI-RAYOS saltando + mensaje «¡ALCANZADA!» (i18n ES/EN), y al",
    "    agotarse ESTALLA (pedacitos + punto + fin por baja). Las salidas",
    "    de emergencia (cortina 2/4, salida del partido, fin de ventana)",
    "    LIBERAN el agarre en _elecFin — la bola nunca queda congelada",
    "    para siempre (lección r28) y el bloque del portal que oculta la",
    "    bola en tránsito queda EXENTO durante el agarre. El hide+revive",
    "    del r28 se retira: la bola muerta cae VISIBLE (patrón de punto",
    "    normal) — el saque del rival, indemne.",
    "  · 5 · FIX E · PRISMA SÓLO EN CAMPO RIVAL (informe del dueño:",
    "    «estaría bien que el jugador pudiese ver el efecto solo en el",
    "    campo del rival para que no le molestase cuando la bola entra en",
    "    nuestro campo»): _trailFirmaPoder devuelve la firma arcoíris SOLO",
    "    con la bola en la mitad rival (z < centro); en nuestro campo la",
    "    estela vuelve al color de la skin (lerp suave dt·6; los puntos",
    "    ya nacidos se apagan solos en 0,42 s). La guía del golpeo y la",
    "    desventaja IA (PRISMA_OUT_P) intactas.",
    "  · 6 · REPOSICIÓN: la ficha del ZIP v36129 llevó las notas de la",
    "    r32 (la sustitución de notas de r33 falló en silencio por",
    "    marcador) — aquí la sustitución es ASERTADA (aborte duro). El",
    "    LOTE APROBADO r33 (Prisma · Onda · Salvavidas · Ancla + ASTRO",
    "    en rig) viaja íntegro dentro del 3.6.130.",
    "  · 7 · QA: test_r34_fixes_v36130 61/0 · probe EN VIVO (voces 15×",
    "    ES/EN · 8 padres en rig · agarre→estallido→fin por baja ·",
    "    liberación de emergencia · prisma por campos · 0 errores de",
    "    página) · regresión re-anclada r34: r33 77/0 · r32 49/0 · r31",
    "    47/0 · r30 54/0.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 sha256",
    "    BYTE-EXACTO (df8f71a3 / 8bb62082); cero cambios de códec en c09.",
    "  SE CONSERVA TODO: lote aprobado r33, salones del dueño r32 con",
    "    su música y su icono de silencio, higiene Fénix r31, Fénix",
    "    jugable r30, Súper Oscuridad, Crono, voces Piper, iconos del",
    "    dueño, bola atractora r26b, barrera eléctrica, FORO3D r27,",
    "    skins r21, cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2,",
    "    ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.130",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36129", "release-v36130"),
    ("staging-v36128", "staging-v36129"),
    ("V3.6.129-SDK6", "V3.6.130-SDK6"),
    ("3.6.129-SDK6", "3.6.130-SDK6"),
    ("v36129-sdk6", "v36130-sdk6"),
    ("v36129", "v36130"),
    ("3.6.129", "3.6.130"),
    ("fase 131", "fase 132"),
    ("FASE 131", "FASE 132"),
    ("Fase 131", "Fase 132"),
]

# Marcadores sobre el ESTADO POST-TOKENS del bloque heredado (las notas
# del v36129 siguen siendo las de la r32 — el fallo silencioso de r33):
INI_MARCADOR = ("'Rama    : main · SDK6 (FASE 130 — SALONES DEL DUEÑO: tu arte en los"
                + NL + "'")
FIN_MARCADOR = ("    '  3.6.128" + NL + "'")

LINEA_FINAL_VIEJA = ("print('" + NL + "V3.6.130-SDK6 lista: los 4 superpoderes del "
                     "LOTE APROBADO (Prisma · Onda de Choque · Salvavidas · Ancla) con "
                     "iconos y voces de la casa + el ASTRO visible de nuevo en la "
                     "Estación Orbital.')")
LINEA_FINAL_NUEVA = ("print('" + NL + "V3.6.130-SDK6 lista: los superpoderes corregidos "
                     "según el informe del dueño (Red alineada en el rig · voz de "
                     "selección para los 14 · Electricidad con retención de 1 s y fin "
                     "por baja · Prisma sólo en campo rival).')")


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    notas_ok = 0
    linea_ok = 0
    for f in sorted(DEST.iterdir()):
        if not f.is_file():
            continue
        txt = f.read_text(encoding='utf-8')
        orig = txt
        for a, b in TOKENS:
            txt = txt.replace(a, b)
        # bloque de notas → FASE 132 (sustitución ASERTADA — lección r33).
        # Sólo exige los marcadores en los ficheros que LLEVAN el bloque
        # (build_zip.py); los demás (chuleta, leemes) sólo reciben tokens.
        i = txt.find(INI_MARCADOR)
        if i >= 0:
            j = txt.find(FIN_MARCADOR, i)
            if j < 0:
                raise SystemExit(
                    f'ABORTA: INI sin FIN en {f.name} — nada escrito.')
            txt = txt[:i] + _NOTAS.rstrip('\n') + txt[j + len(FIN_MARCADOR):]
            notas_ok += 1
        if LINEA_FINAL_VIEJA in txt:
            txt = txt.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
            linea_ok += 1
        if txt != orig:
            f.write_text(txt, encoding='utf-8')
            tocados += 1
    if notas_ok != 1 or linea_ok != 1:
        raise SystemExit(
            f'ABORTA: sustituciones esperadas 1/1, obtenidas '
            f'notas={notas_ok} · linea_final={linea_ok}.')
    print(f"\nrelease-v36130 generado ({tocados} ficheros tocados · "
          f"notas sustituidas {notas_ok} · línea final {linea_ok}).")
    print("Siguiente: python3 scripts/release-v36130/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
