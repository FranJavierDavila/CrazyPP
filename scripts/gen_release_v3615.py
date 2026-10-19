#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 18 · GENERADOR DEL DIRECTORIO DE RELEASE v3615
======================================================================
Crea scripts/release-v3615/ a partir de scripts/release-v3614/ con:
  · reemplazos de versión (3.6.14-SDK6 → 3.6.15-SDK6 · v3614-sdk6 → v3615-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 17 — EMBUDO COMPLETO:
    champ_rank + stage + champion en Oeste, Estación Orbital y Valle
    Neón, ronda 18)
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3615 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3614"
DEST = RAIZ / "scripts" / "release-v3615"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo).
# La aguja EMPIEZA en 'Rama (sin indentar): el reemplazo respeta la
# sangría de 4 espacios que ya tiene la línea en el fichero.
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 16 — EMBUDO VIVO: champ_rank de las pruebas de La Locura)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.13-SDK6):\\n'\n"
    "    '  · FASE 16 — EMBUDO VIVO (ronda 17): las pruebas ARKANOID de\\n'\n"
    "    '    La Locura ya reportan champ_rank (victoria, ladrillos\\n'\n"
    "    '    rotos, vidas restantes y tiempo al acabar). Magia lo\\n'\n"
    "    '    emitía desde la ronda 11 y el agregado champRank llevaba\\n'\n"
    "    '    CERO datos pese a los intentos reales: 3 sesiones VR y\\n'\n"
    "    '    45 min de juego sin un solo reporte.\\n'\n"
    "    '  · Con el embudo vivo, la próxima decisión de dificultad\\n'\n"
    "    '    (p. ej. suavizar el ARKANOID 2) se toma con la tasa real\\n'\n"
    "    '    de intentos y victorias del dueño, no a ciegas.\\n'\n"
    "    '  · La prueba no puntúa ni da estrellas (score/stars a 0,\\n'\n"
    "    '    igual que el orbe de Magia): el agregador del worker suma\\n'\n"
    "    '    victorias por campeonato.\\n'\n"
    "    '  · Fluidez: la sesión en la 3.6.12 llegó a 45 MINUTOS con 78\\n'\n"
    "    '    fps en el último ping — la nitidez 1.4× confirmada en\\n'\n"
    "    '    sesiones largas.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
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

GLOBALES = [
    ("V3.6.14-SDK6", "V3.6.15-SDK6"),
    ("3.6.14-SDK6", "3.6.15-SDK6"),
    ("v3614-sdk6", "v3615-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 17 insertadas")
            # guard del COMPLETO (lección ronda 10/…/16): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.14"' in txt:
                txt = txt.replace('grep -c "3.6.14"', 'grep -c "3.6.15"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.15")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.15-SDK6") == 1:
            txt = txt.replace("frente a V3.6.15-SDK6", "frente a V3.6.14-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.14)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3615 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.14-SDK6", "v3614-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.15-SDK6" not in bz or "FASE 17" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    print("· release-v3615 listo → python3 scripts/release-v3615/build_zip.py")


if __name__ == "__main__":
    main()
