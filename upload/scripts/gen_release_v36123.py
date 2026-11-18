#!/usr/bin/env python3
"""
CRAZY PING PONG · Generador del paquete de despliegue V3.6.123-SDK6 (r27).
Crea scripts/release-v36123/ a partir de scripts/release-v36122/ con:
  · rutas/strings re-selladas a la nueva versión (staging, ZIPs, notas)
  · el bloque de NOTAS del release sustituido por el de FASE 125
  · la línea final del build con el resumen de la ronda
Idempotente: si release-v36123 ya existe, lo regenera desde cero.

Uso:
    python3 scripts/gen_release_v36123.py
    python3 scripts/release-v36123/build_zip.py   (ZIPs)
"""
import shutil
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')   # r127: el mount vivo del repo
ORIGEN = RAIZ / "scripts" / "release-v36122"
DEST = RAIZ / "scripts" / "release-v36123"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 125 — MODO DEPURACIÓN (FORO3D)",
    "COMPLETO: informe del dueño — «recuerda que teníamos una clave",
    "secreta de tal forma que si el nombre de usuario es FORO3D entramos",
    "en el modo de depuración que nos permite ver o acceder a cualquier",
    "recurso aunque esté bloqueado, o nos permite entrar en cualquier",
    "prueba o etapa de los campeonatos aunque no estén disponibles para",
    "otros usuarios»). La clave VIVÍA (v2.108) pero la r26b dejó tres",
    "candados que no la consultaban: este parche los abre TODOS.",
    "  · 1 · LA CLAVE (intacta): ppDebugMode() en c00 — el nombre",
    "    «foro3d» (comparación en minúsculas: el teclado del menú escribe",
    "    en MAYÚSCULAS, FORO3D vale) publica window.__PP_DEBUG al",
    "    arrancar y se re-evalúa al guardar el nombre (ppDebugRefresh).",
    "    Con ella: rótulo «MODO DEPURACIÓN» (2D en portada y 3D en el",
    "    visor), NO genera registros (interceptor descarta pp_champ_* —",
    "    cubre oeste/magia/locura/halloween/estacion_orbital —,",
    "    pp_arcade_*, ranking mundial y ppxr_stats_v1) y no hay",
    "    telemetría de este jugador.",
    "  · 2 · AGUJERO 1 CERRADO — _mesaLibre() (c12) era el ÚNICO candado",
    "    que no consultaba __PP_DEBUG: con foro3d devuelve true ANTES de",
    "    mirar hitos → SALÓN NEÓN ARCADE (hito rally 20), OBSERVATORIO",
    "    ESTELAR (hito ELO 1100) y DOJO ZEN (hito aces 5) — los 3",
    "    salones de la r26b — quedan ABIERTOS para revisión, junto con",
    "    los aspectos de mesa (Oro/Carbono) y las skins de bola con",
    "    candado. Punto ÚNICO de corte: las 14 llamadas heredan el",
    "    bypass; los jugadores normales NO notan nada (el criterio de",
    "    hitos/estrellas queda byte a byte igual).",
    "  · 3 · AGUJERO 2 CERRADO — halloween: su mapa no consultaba",
    "    debug (oeste/locura/magia lo hacían desde v2.108 con ppDbg).",
    "    Ahora maxIdx() devuelve totalEtapas-1 con __PP_DEBUG: el mapa",
    "    levanta TODAS las tapas y el gatillo salta a CUALQUIER etapa",
    "    (hover/rejugar heredan el maxIdx); el progreso real se conserva",
    "    vía _replay y el interceptor no persiste nada de la sesión.",
    "  · 4 · AGUJERO 3 CERRADO — estacion_orbital: replayData().maxIdx",
    "    sólo daba mapa completo al CAMPEÓN; con __PP_DEBUG maxIdx = 4",
    "    (mapa completo para revisión). replayLaunch ya aceptaba",
    "    cualquier etapa (el salto escribe pp_champ_estacion_orbital_*",
    "    que el interceptor descarta en depuración).",
    "  · 5 · CAMPEONATOS BLOQUEADOS (sin cambios): c11 · isLocked() ya",
    "    consultaba ppDebugMode — con foro3d la Estación Orbital del",
    "    SDK es jugable; LOCKED intacto para jugadores normales.",
    "  · FÍSICA INTACTA (garantía de siempre): c04/c05 (física) sha256",
    "    BYTE-EXACTO contra la r26b; oeste/locura/magia conservan su",
    "    patrón ppDbg SIN tocar; interceptor de c00 sin cambios; cero",
    "    cambios de códec en c09.",
    "  · TEST NUEVO: test_r27_foro3d_v36123 (40/0) — clave, bypass de",
    "    _mesaLibre (orden bypass→hitos), halloween, estación orbital,",
    "    patrón v2.108 de los 3 módulos veteranos, interceptor y sellos",
    "    de build. Regresión r26b 158/0, r26 109/0, r25 150/0, r24 89/0,",
    "    r23 81/0 y r21 63/0. bump BYTE-EXACTO (11.174.904 B",
    "    · golden 30a0f2b8…).",
    "  SE CONSERVA TODO: niebla densa y bola atractora r26/r26b, los 3",
    "    superpoderes nuevos (Fénix/Crono/Hielo), los 3 salones nuevos",
    "    por hitos, barrera eléctrica en la Súper Red, skins r21, hall",
    "    cabaña, cortina etapas 2/4, _bolaGuard, P4, CRAZY LINK v2,",
    "    ELO, matchmaking, halloween.",
    "  · sellada a",
    "  3.6.123",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36122", "release-v36123"),
    ("staging-v36122", "staging-v36123"),
    ("V3.6.122-SDK6", "V3.6.123-SDK6"),
    ("3.6.122-SDK6", "3.6.123-SDK6"),
    ("v36122-sdk6", "v36123-sdk6"),
    ("v36122", "v36123"),
    ("3.6.122", "3.6.123"),
    ("fase 124", "fase 125"),
    ("FASE 124", "FASE 125"),
]

# Marcadores sobre el ESTADO POST-SWEEP (los TOKENS ya convirtieron el
# bloque heredado de la r26b a FASE 125/3.6.123 — el INI es la primera
# línea de ese bloque y el FIN su sello de versión YA re-sellado).
INI_MARCADOR = "'Rama    : main · SDK6 (FASE 125 — BOLA ATRACTORA +"
FIN_MARCADOR = "'  3.6.123" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.123-SDK6 lista: BOLA ATRACTORA (1 de cada 4 rayos la buscan) + SÚPER FÉNIX/CRONO/HIELO + HALLS NEÓN/OBSERVATORIO/DOJO por hitos.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.123-SDK6 lista: MODO DEPURACIÓN COMPLETO (foro3d): salones por hitos + mapas de halloween y estación orbital abiertos.')"


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
        # bloque de notas → FASE 125 (sustitución EXACTA, lección r24:
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
    print(f"\nrelease-v36123 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36123/build_zip.py (ZIPs)")


if __name__ == '__main__':
    main()
