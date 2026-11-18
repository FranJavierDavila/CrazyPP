#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 21 · GENERADOR DEL DIRECTORIO DE RELEASE v3617
======================================================================
Crea scripts/release-v3617/ a partir de scripts/release-v3616/ con:
  · reemplazos de versión (3.6.16-SDK6 → 3.6.17-SDK6 · v3616-sdk6 → v3617-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 19 — TU CAMINO TE ESPERA
    en producción de verdad, ronda 21)
  · PROTECCIÓN de la estirpe histórica V3.6.9-SDK5 / v369-sdk5 (FASE 7):
    solo se reemplazan los sufijos -SDK6 (lección de la ronda 13).
Idempotente: si release-v3617 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v3616"
DEST = RAIZ / "scripts" / "release-v3617"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo).
BLOQUE_VIEJO = (
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
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 19 — TU CAMINO TE ESPERA, en producción de verdad)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.16-SDK6):\\n'\n"
    "    '  · FASE 19 — TU CAMINO TE ESPERA (ronda 21): las tarjetas del\\n'\n"
    "    '    menú CAMPEONATOS muestran «Etapa X/5 · sigue donde la\\n'\n"
    "    '    dejaste» en cada campeonato con progreso guardado.\\n'\n"
    "    '  · Transparencia: la 3.6.16 ANUNCIABA esta función pero el\\n'\n"
    "    '    parche no llegó al ensamblado (se escribió en el\\n'\n"
    "    '    artefacto y el bump regenera public/game.html desde\\n'\n"
    "    '    src/game/). La 3.6.17 lo trae DE VERDAD, verificado en\\n'\n"
    "    '    producción con un navegador real (qa_hub_hints.py).\\n'\n"
    "    '  · Precedencia del rótulo: ★ SUPERADO > etapa en curso >\\n'\n"
    "    '    victorias. La etapa de SALIDA no se anuncia: no es\\n'\n"
    "    '    progreso todavía.\\n'\n"
    "    '  · Detalle fino: el Oeste guarda su camino como 1..5 y los\\n'\n"
    "    '    otros cuatro como 0..4 — el núcleo normaliza a etapas\\n'\n"
    "    '    humanas (1..5), sin sorpresas.\\n'\n"
    "    '  · Limpieza pendiente APLICADA: el texto huérfano\\n'\n"
    "    '    ark_back_clown (anunciado retirado en la 3.6.15) sale\\n'\n"
    "    '    ahora sí del diccionario ES/EN.\\n'\n"
    "    '  · QA nuevo permanente: qa_hub_hints.py carga el juego en\\n'\n"
    "    '    un navegador real con el estado del dueño y afirma los\\n'"
    "    '    hints («Etapa 3/5» en Oeste y Locura; callados la etapa\\n'\n"
    "    '    de salida y el marcador de campeón).\\n'\n"
    "    '  · Fluidez: la sesión del casco cerró 15m42s con pings\\n'\n"
    "    '    74/89/83 y vr_end a 93 fps — récord de fluidez (antes\\n'\n"
    "    '    el máximo era 78).\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.16-SDK6", "V3.6.17-SDK6"),
    ("3.6.16-SDK6", "3.6.17-SDK6"),
    ("v3616-sdk6", "v3617-sdk6"),
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
            print(f"  ✓ {f.name}: notas FASE 19 insertadas")
            # guard del COMPLETO (lección ronda 10/…/18): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.16"' in txt:
                txt = txt.replace('grep -c "3.6.16"', 'grep -c "3.6.17"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.17")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (heredada de la ronda 12): «frente a» cita
        # la versión ANTERIOR (los GLOBALES la adelantarían a la nueva)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.17-SDK6") == 1:
            txt = txt.replace("frente a V3.6.17-SDK6", "frente a V3.6.16-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.16)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v3617 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.16-SDK6", "v3616-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.17-SDK6" not in bz or "FASE 19" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    # la estirpe histórica SDK5 (FASE 7) debe sobrevivir intacta
    if "V3.6.9-SDK5" not in bz:
        print("FALLO: la referencia histórica V3.6.9-SDK5 se perdió")
        sys.exit(1)
    print("· release-v3617 listo → python3 scripts/release-v3617/build_zip.py")


if __name__ == "__main__":
    main()
