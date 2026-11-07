#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 19 · GENERADOR DEL DIRECTORIO DE RELEASE v3616
======================================================================
Crea scripts/release-v3616/ a partir de scripts/release-v3615/ con:
  · reemplazos de versión (3.6.15-SDK6 → 3.6.16-SDK6 · v3615-sdk6 → v3616-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 18 — TU CAMINO TE ESPERA:
    el hub muestra «Etapa X/5 · sigue donde la dejaste», ronda 19)
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3616 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3615"
DEST = RAIZ / "scripts" / "release-v3616"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo).
# La aguja EMPIEZA en 'Rama    : main · SDK6 (FASE 17 — …' y termina con
# «…los 5 campeonatos.\n\n'»: el reemplazo respeta la sangría de 4 espacios
# que ya tiene cada línea en el fichero.
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 17 — EMBUDO COMPLETO: telemetría en los 5 campeonatos)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.14-SDK6):\\n'\n"
    "    '  · FASE 17 — EMBUDO COMPLETO (ronda 18): OESTE, ESTACIÓN\\n'\n"
    "    '    ORBITAL y VALLE NEÓN ya reportan champ_rank (intentos y\\n'\n"
    "    '    victorias de cada prueba y duelo), avance de etapa (stage)\\n'\n"
    "    '    y campeón conseguido (champion) — hasta hoy sólo La Locura\\n'\n"
    "    '    y Magia reportaban.\\n'\n"
    "    '  · Oeste: duelos Nv 1-3, asedio (bajas, oleada) y tren\\n'\n"
    "    '    (lingotes, parada). Estación Orbital: dianas, ARKANOID 1/2,\\n'\n"
    "    '    reactor inestable, reactor de impulso, jefe y duelos.\\n'\n"
    "    '    Valle Neón: dianas del taller (golpes, perdidas) y duelos.\\n'\n"
    "    '  · Telemetría pura: cero cambios de jugabilidad — cada envío\\n'\n"
    "    '    va blindado en try{} y respeta el opt-out y el modo\\n'\n"
    "    '    depuración, igual que Locura y Magia.\\n'\n"
    "    '  · La próxima sesión que toque CUALQUIER campeonato deja\\n'\n"
    "    '    datos comparables: el embudo porCampeonato deja de ser\\n'\n"
    "    '    territorio exclusivo de La Locura.\\n'\n"
    "    '  · Limpieza: texto huérfano ark_back_clown retirado del\\n'\n"
    "    '    diccionario (sin referencias desde la ronda 15).\\n'\n"
    "    '  · Fluidez: la 3.6.12 cerró una sesión de 69 MINUTOS en el\\n'\n"
    "    '    casco (4 pings 73-78 fps) — récord de permanencia.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 18 — TU CAMINO TE ESPERA: el hub muestra tu etapa)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.15-SDK6):\\n'\n"
    "    '  · FASE 18 — TU CAMINO TE ESPERA (ronda 19): las tarjetas del\\n'\n"
    "    '    menú CAMPEONATOS muestran «Etapa X/5 · sigue donde la\\n'\n"
    "    '    dejaste» en cada campeonato con progreso guardado (antes\\n'\n"
    "    '    sólo decían «Toca para entrar» o «Rondas ganadas»).\\n'\n"
    "    '  · Precedencia del rótulo: ★ SUPERADO > etapa en curso >\\n'\n"
    "    '    victorias. La etapa de SALIDA (1 en formato humano en\\n'\n"
    "    '    los cinco) no se anuncia: no es progreso todavía.\\n'\n"
    "    '  · Detalle fino: el Oeste guarda su camino como 1..5 y los\\n'\n"
    "    '    otros cuatro como 0..4 — el núcleo normaliza y siempre\\n'\n"
    "    '    enseña etapas humanas (1..5), sin sorpresas.\\n'\n"
    "    '  · El subtítulo de la sección CAMPEONATOS respeta la misma\\n'\n"
    "    '    precedencia cuando ningún módulo está cargado.\\n'\n"
    "    '  · Auditoría previa (ronda 19): los 5 campeonatos guardan\\n'\n"
    "    '    su etapa en localStorage (pp_arcade_stage y\\n'\n"
    "    '    pp_champ_<id>_stage) — tu progreso sobrevive al cierre\\n'\n"
    "    '    del casco: retomar un campeonato a medias es seguro.\\n'\n"
    "    '  · Telemetría: el embudo champ_rank (rondas 17-18) se\\n'\n"
    "    '    estrena con las próximas partidas — intentos, victorias\\n'\n"
    "    '    y métricas reales de las pruebas de los 5 campeonatos.\\n'\n"
    "    '  · Fluidez: la sesión del casco en la 3.6.14 cerró 12,7 min\\n'\n"
    "    '    con 76/75 fps y vr_end limpio; la 3.6.15 ya arrancó en\\n'\n"
    "    '    producción el mismo día.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.15-SDK6", "V3.6.16-SDK6"),
    ("3.6.15-SDK6", "3.6.16-SDK6"),
    ("v3615-sdk6", "v3616-sdk6"),
]


def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    print(f"· copiado {ORIGEN.name} → {DEST.name}")

    for f in sorted(DEST.iterdir()):
        if f.suffix not in (".py", ".txt", ".json", ".mjs"):
            continue
        txt = f.read_text(encoding="utf-8")
        antes = len(txt)
        if f.name == "build_zip.py":
            if txt.count(BLOQUE_VIEJO) != 1:
                print(f"FALLO: bloque de notas ×{txt.count(BLOQUE_VIEJO)} en build_zip.py")
                sys.exit(1)
            txt = txt.replace(BLOQUE_VIEJO, BLOQUE_NUEVO)
            print(f"  ✓ {f.name}: notas FASE 18 insertadas")
            # guard del COMPLETO (lección ronda 10/…/18): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.15"' in txt:
                txt = txt.replace('grep -c "3.6.15"', 'grep -c "3.6.16"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.16")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.16-SDK6") == 1:
            txt = txt.replace("frente a V3.6.16-SDK6", "frente a V3.6.15-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.15)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3616 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.15-SDK6", "v3615-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.16-SDK6" not in bz or "FASE 18" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    print("· release-v3616 listo → python3 scripts/release-v3616/build_zip.py")


if __name__ == "__main__":
    main()
