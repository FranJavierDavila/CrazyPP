#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r111 · catálogo de telemetría v5 → v6: + primer_rally + tut_end (M4)."""
import json
from pathlib import Path

P = Path('/home/z/my-project/scripts/telemetria_catalogo.json')
d = json.loads(P.read_text(encoding='utf-8'))

nombres = {e['nombre'] for e in d['eventos']}
assert len(d['eventos']) == 14, f"esperaba 14 eventos, hay {len(d['eventos'])}"
assert 'primer_rally' not in nombres and 'tut_end' not in nombres

d['version'] = 6
d['ronda'] = 111
d['actualizado'] = '2026-11-03'

d['eventos'].append({
    "nombre": "primer_rally",
    "origen": "src/game/core/c12_pingponggame.js (animate, M4 r111)",
    "momento": "el árbitro entra en 'rally' por PRIMERA vez de la sesión en partido local (no hall, no calibración, no online)",
    "campos": [
        {"nombre": "lat", "tipo": "number",
         "desc": "segundos desde vr_start (redondeado a 0,1) — la métrica del hito M4: un jugador nuevo en rallye real en <60 s"},
        {"nombre": "dif", "tipo": "string",
         "desc": "dificultad de la CPU vigente (easy/medium/hard)"}
    ],
    "desde": "v3.6.101",
    "notas": "M4 (r111): UNA sola vez por sesión; lat + 60 s de media en jugadores nuevos = onboarding cumplido. En duelo online no sale (la mesa la acuerda el anfitrión)."
})

d['eventos'].append({
    "nombre": "tut_end",
    "origen": "src/game/core/c13_ui_arranque.js (LA ACADEMIA, stop(), M4 r111)",
    "momento": "cierre de la academia: fin del guion, botón ▶ JUGAR YA o salida con B/Y",
    "campos": [
        {"nombre": "res", "tipo": "string",
         "desc": "'done' fin del guion · 'aJugar' botón ▶ JUGAR YA (paso final) · 'skip' saltó con B/Y"},
        {"nombre": "paso", "tipo": "number",
         "desc": "paso del guion en el que acabó (0..8; -1 si no llegó a contarse)"}
    ],
    "desde": "v3.6.101",
    "notas": "M4 (r111): mide si la academia se termina o se salta ahora que ya NO bloquea la primera entrada (el HUB nace en ▶ JUGAR)."
})

P.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('catálogo v6 OK:', len(d['eventos']), 'eventos')
