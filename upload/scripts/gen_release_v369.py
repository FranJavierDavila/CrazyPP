#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 12 · GENERADOR DEL DIRECTORIO DE RELEASE v369
=====================================================================
Crea scripts/release-v369/ a partir de scripts/release-v368/ con:
  · reemplazos de versión (3.6.8-SDK6 → 3.6.9-SDK6 · v368-sdk6 → v369-sdk6)
  · bloque de notas del VERSION.txt nuevo (FASE 11 — TELEMETRÍA: plataforma
    real + latido VR)
Idempotente: si release-v369 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v368"
DEST = RAIZ / "scripts" / "release-v369"

# bloque de notas del VERSION.txt en build_zip.py (aguja → reemplazo)
BLOQUE_VIEJO = (
    "'Rama    : main · SDK6 (FASE 10 — ANÁLISIS DE VENTA: embudo por campeonato)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.8-SDK6):\\n'\n"
    "    '  · FASE 10 — ANÁLISIS (ronda 11): los eventos stage y champion\\n'\n"
    "    '    llevan el ID del campeonato (Magia, La Locura) — el panel\\n'\n"
    "    '    /telemetria separa el embudo POR CAMPEONATO: etapas, títulos,\\n'\n"
    "    '    partidas, victorias, mejor puntuación y estrellas.\\n'\n"
    "    '  · champ_rank VIAJA POR la cola __PP_TELE: versión REAL del juego\\n'\n"
    "    '    (antes 2.81.0 clavada a mano), t y sid propios, y RESPETA el\\n'\n"
    "    '    opt-out (pp_tele=0) y el modo depuración.\\n'\n"
    "    '  · Manifests: Magia v32 y La Locura v23 (telemetría identificada).\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)
BLOQUE_NUEVO = (
    "'Rama    : main · SDK6 (FASE 11 — TELEMETRÍA: plataforma real + latido VR)\\n\\n'\n"
    "    'Novedades de esta versión (frente a V3.6.8-SDK6):\\n'\n"
    "    '  · FASE 11 — TELEMETRÍA (ronda 12): boot.platform es REAL — xr en\\n'\n"
    "    '    el dispositivo con WebXR inmersivo (Quest) vs 2d escritorio\\n'\n"
    "    '    (antes estaba CLAVADO a 2d y el casco era indistinguible).\\n'\n"
    "    '  · LATIDO EN VR: vr_ping cada 5 min durante la sesión — fecha el\\n'\n"
    "    '    fin real de las sesiones cerradas abruptamente (casco apagado\\n'\n"
    "    '    sin vr_end) y dibuja la curva de fps a lo largo de la partida.\\n'\n"
    "    '  · La telemetría confirma la optimización de la ronda 10: 38 →\\n'\n"
    "    '    55 fps de media (picos 91) en 49 min reales de campeonato.\\n'\n"
    "    '  · Nitidez sin cambios (1.4): a la espera de más lecturas vr_end.\\n'\n"
    "    '  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta,\\n'\n"
    "    '    superpoderes, reactor, escudo y duelos exactamente igual.\\n'\n"
    "    '  · Conserva TODO: el ESCUDO DE PALA en la etapa 4, el REACTOR\\n'\n"
    "    '    DE IMPULSO en la etapa 2, la CCD SDF de contacto, el saque\\n'\n"
    "    '    VR realista, el hall del anfitrión, PRO CIRCUITO, intro\\n'\n"
    "    '    oficial, física viva, palas con carácter, CRAZY TV en\\n'\n"
    "    '    directo y los 5 campeonatos.\\n\\n'\n"
)

GLOBALES = [
    ("V3.6.8-SDK6", "V3.6.9-SDK6"),
    ("3.6.8-SDK6", "3.6.9-SDK6"),
    ("v368-sdk6", "v369-sdk6"),
    ("v368", "v369"),
    ("V3.6.8", "V3.6.9"),
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
            print(f"  ✓ {f.name}: notas FASE 11 insertadas")
            # guard del COMPLETO (lección ronda 10/11): el grep del hub
            # empaquetado debe apuntar a la versión NUEVA
            if 'grep -c "3.6.8"' in txt:
                txt = txt.replace('grep -c "3.6.8"', 'grep -c "3.6.9"')
                print("  ✓ build_zip.py: guard del COMPLETO grep actualizado a 3.6.9")
        for viejo, nuevo in GLOBALES:
            txt = txt.replace(viejo, nuevo)
        # corrección cosmética (ronda 12): «frente a» cita la versión ANTERIOR
        # (la ronda 11 la dejaba autorreferida: los GLOBALES la reescribían)
        if f.name == "build_zip.py" and txt.count("frente a V3.6.9-SDK6") == 1:
            txt = txt.replace("frente a V3.6.9-SDK6", "frente a V3.6.8-SDK6")
            print("  ✓ build_zip.py: «frente a» corregido a la versión anterior (3.6.8)")
        f.write_text(txt, encoding="utf-8")
        print(f"  · {f.name} ({antes} → {len(txt)} B)")

    # verificación: el build_zip del v369 no debe quedar con sellos viejos
    bz = (DEST / "build_zip.py").read_text(encoding="utf-8")
    for sello_viejo in ("3.6.8-SDK6", "v368-sdk6"):
        n = bz.count(sello_viejo)
        if n:
            print(f"aviso: {sello_viejo} queda ×{n} en build_zip.py (revisar)")
    if "3.6.9-SDK6" not in bz or "FASE 11" not in bz:
        print("FALLO: build_zip.py sin sellos nuevos")
        sys.exit(1)
    print("· release-v369 listo → python3 scripts/release-v369/build_zip.py")


if __name__ == "__main__":
    main()
