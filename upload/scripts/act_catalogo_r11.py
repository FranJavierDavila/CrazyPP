#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 11 · actualiza el catálogo de telemetría:
  · stage / champion llevan 'id' del campeonato desde 3.6.8-SDK6
  · champ_rank viaja POR la cola __PP_TELE (v real, t, sid, opt-out)
Idempotente: los reemplazos se cuentan."""
import json
from pathlib import Path

P = Path('/home/z/my-project/scripts/telemetria_catalogo.json')
d = json.loads(P.read_text(encoding='utf-8'))

ID_STAGE = {"nombre": "id", "tipo": "string",
            "desc": "ronda 11: id del campeonato ('magia', 'locura'); los eventos anteriores a 3.6.8-SDK6 no lo llevan"}
ID_CHAMP = {"nombre": "id", "tipo": "string",
            "desc": "ronda 11: id del campeonato ganado (los anteriores a 3.6.8-SDK6 no lo llevan)"}
hechos = 0
for e in d['eventos']:
    n = e.get('nombre')
    if n == 'stage':
        if not any(c['nombre'] == 'id' for c in e['campos']):
            e['campos'].append(ID_STAGE)
            hechos += 1
    elif n == 'champion':
        if not any(c['nombre'] == 'id' for c in e.get('campos', [])):
            e['campos'] = [ID_CHAMP]
            hechos += 1
    elif n == 'champ_rank':
        e['origen'] = ("public/championships/magia/index.js (_reportRank) — ronda 11: "
                       "viaja POR la cola __PP_TELE.ev (antes: POST propio application/json)")
        for c in e['campos']:
            if c['nombre'] == 'v':
                c['desc'] = ("versión del juego (ronda 11: la REAL de __PP_TELE; antes "
                             "'2.81.0' hardcodeado — drift conocido cerrado)")
        e['notas'] = ("ronda 11: va en la cola estándar de __PP_TELE (t, sid, v reales; respeta opt-out "
                      "pp_tele=0 y modo depuración; la cola persistida reintenta si no hay red)")
        hechos += 1

d['ronda'] = 11
d['actualizado'] = '2026-10-19'
sec = d.setdefault('ronda11', {})
d['ronda11'] = {
    'cambios': [
        'stage y champion llevan id del campeonato (magia + locura) desde 3.6.8-SDK6',
        'champ_rank viaja por __PP_TELE: v real del juego (antes 2.81.0 clavado), t y sid propios, respeta opt-out y modo depuración',
        'resumen nuevo: porCampeonato {id: {stage, champion}} en worker y receptor local (tolerante con datos sin id)',
        'panel: tabla «Embudo por campeonato» (etapas, títulos, partidas, victorias, mejor, estrellas)',
    ],
}
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'OK · {hechos} eventos actualizados · ronda={d["ronda"]}')
