#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CRAZY PING PONG · ronda 124 · GENERADOR DEL DIRECTORIO DE RELEASE v36113
========================================================================
Crea scripts/release-v36113/ a partir de scripts/release-v36112/ con:
  · reemplazos de versión (3.6.112-SDK6 → 3.6.113-SDK6 · v36112 → v36113)
  · bloque de notas del VERSION.txt nuevo (FASE 115 — M7e · PERSISTENCIA
    COMPLETA: historial de torneos + perfil recordado; test M7e nuevo
    19/0), por MARCADORES (NL literal, patrón gen_release de la casa).
  · guards del build_zip conservados (SDK 1.6.0 no cambia esta ronda).
Idempotente: si release-v36113 ya existe, lo regenera desde cero.
"""

import shutil
import sys
from pathlib import Path

RAIZ = Path("/home/z/my-project")
ORIGEN = RAIZ / "scripts" / "release-v36112"
DEST = RAIZ / "scripts" / "release-v36113"

NL = chr(92) + "n"          # secuencia LITERAL \n (2 caracteres)

_NOTAS_TXT = [
    "Rama    : main · SDK6 (FASE 115 — M7e · PERSISTENCIA COMPLETA:",
    "HISTORIAL DE TORNEOS + PERFIL RECORDADO (r124): se cierra el M7",
    "del roadmap — cada sub-fase desplegada por separado.",
    "  · HISTORIAL DE TORNEOS (c11): historialTorneos() sella en",
    "    pp_torneos_historial_v1 la FECHA en que cada campeonato se ve",
    "    campeón por primera vez (retroactivo y honesto — lo ya ganado",
    "    entra con la fecha de la primera pasada, sin fechas inventadas).",
    "    Append-only, una fila por torneo, cap 50; victorias y LEYENDA",
    "    se refrescan de sus registros; convenciones <base>champ y",
    "    <base>trophy; fusión pura testeable (historialFusionar).",
    "  · PÁGINA HISTORIAL (c12): botón «Ver historial de torneos» en",
    "    CAMPEONATOS + página champhist con una fila por torneo vencido",
    "    (nombre vivo por idioma, victorias, sello LEYENDA y fecha).",
    "  · PERFIL RECORDADO (c12): AJUSTES › PERFIL Y DATOS muestra TU",
    "    perfil vivo: piel de la mesa, alto, pala mejorada, rivales con",
    "    estilo y pid anónimo — todo leído de SUS registros existentes",
    "    (pp_mesaskin, pp_mesaalto, pp_pala_mejorada_v1, pp_rivstyle_v1,",
    "    pp_pid): nada nuevo que sincronizar — el perfil ES el estado.",
    "  · TEST NUEVO test_m7e_persistencia_v36113 (19/0): fusión pura y",
    "    ChampLoader real con shim de localStorage (carga al estilo",
    "    build_game: bloque DEPS-FASE2 eliminado antes de importar).",
    "  SE CONSERVA TODO: M-RED3 (decodificador fast endurecido), CRAZY",
    "    LINK v2, ELO unificado, matchmaking, reto diario y semanal, MI",
    "    RANKING, estilos de IA, superpoderes, dobles 2v2, academia y",
    "    PRO TRAINING.",
    "  QA r124 en verde: test_m7e_persistencia 19/0 · test_red_nucleo",
    "    60/0 · test_f1_decode 6/0 · build BYTE-EXACTO (golden",
    "    bc1d80a9 · 10.716.901 B).",
    "  · sellada a",
    "  3.6.113",
]
_NOTAS = "".join(f"    '{linea}{NL}'\n" for linea in _NOTAS_TXT)

TOKENS = [
    ("release-v36112", "release-v36113"),
    ("staging-v36112", "staging-v36113"),
    ("V3.6.112-SDK6", "V3.6.113-SDK6"),
    ("3.6.112-SDK6", "3.6.113-SDK6"),
    ("v36112-sdk6", "v36113-sdk6"),
    ("v36112", "v36113"),
    ("3.6.112", "3.6.113"),
]

INI_MARCADOR = "'Rama    : main · SDK6 (FASE 114"
FIN_MARCADOR = "'  3.6.112" + NL + "'"

LINEA_FINAL_VIEJA = "print('" + NL + "V3.6.112-SDK6 lista: ENDURECIMIENTO del decodificador fast (cap de eventos spec §5 + escudo en el canal fast) sobre la revisión completa M-RED2.')"
LINEA_FINAL_NUEVA = "print('" + NL + "V3.6.113-SDK6 lista: M7e PERSISTENCIA COMPLETA (historial de torneos + perfil recordado) — se cierra el M7 del roadmap.')"

def main():
    if DEST.exists():
        shutil.rmtree(DEST)
    shutil.copytree(ORIGEN, DEST)
    tocados = 0
    for p in DEST.rglob("*"):
        if not p.is_file():
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        orig = t
        # 1 · notas FASE 115 (del marcador INI al FIN inclusive)
        i = t.find(INI_MARCADOR)
        if i >= 0:
            j = t.find(FIN_MARCADOR, i)
            if j >= 0:
                t = t[:i] + _NOTAS.rstrip("\n") + t[j + len(FIN_MARCADOR):]
        # 2 · línea final de resumen
        if LINEA_FINAL_VIEJA in t:
            t = t.replace(LINEA_FINAL_VIEJA, LINEA_FINAL_NUEVA)
        # 3 · barrido de tokens de versión
        for viejo, nuevo in TOKENS:
            t = t.replace(viejo, nuevo)
        if t != orig:
            p.write_text(t, encoding="utf-8")
            tocados += 1
            print(f"  ✓ {p.relative_to(DEST)}")
    print(f"\nrelease-v36113 generado ({tocados} ficheros tocados).")
    print("Siguiente: python3 scripts/release-v36113/build_zip.py")
    return 0

if __name__ == "__main__":
    sys.exit(main())
