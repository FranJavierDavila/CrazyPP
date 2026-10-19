#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 12 · actualiza el catálogo de telemetría:
  · boot.platform deja de estar clavado a '2d': detección XR real ('xr' | '2d')
  · evento NUEVO vr_ping: latido cada 5 min durante la sesión VR
    (sesiones cerradas abruptamente + curva de fps a lo largo de la sesión)
Idempotente: los reemplazos se cuentan."""
import json
from pathlib import Path

P = Path('/home/z/my-project/scripts/telemetria_catalogo.json')
d = json.loads(P.read_text(encoding='utf-8'))

hechos = 0
for e in d['eventos']:
    n = e.get('nombre')
    if n == 'boot':
        for c in e.get('campos', []):
            if c['nombre'] == 'platform':
                c['desc'] = ("ronda 12: 'xr' si el dispositivo declara soporte WebXR "
                             "inmersivo al cargar (navigator.xr.isSessionSupported, p. ej. "
                             "Quest) · '2d' escritorio/navegador sin XR. Antes estaba "
                             "CLAVADO a '2d' y el casco era indistinguible del escritorio")
                hechos += 1
        e['notas'] = ("ronda 12: la detección XR es asíncrona (tope 1.5 s) — el boot sale "
                      "ya con '2d' y se corrige IN SITU en la cola si la promesa confirma "
                      "XR; el evento no se duplica ni se reordena")
        hechos += 1

VR_PING = {
    "nombre": "vr_ping",
    "origen": "src/game/core/c00_pre_three.js (vrPing, intervalo 300000 ms) — activado desde c12_pingponggame.js al vr_start, parado al vr_end",
    "momento": "cada 5 min mientras dura la sesión VR",
    "campos": [
        {"nombre": "dur", "tipo": "number", "desc": "segundos de VR transcurridos en el momento del ping"},
        {"nombre": "fps", "tipo": "number", "desc": "fps medio del momento (misma métrica que vr_end) — dibuja la curva a lo largo de la sesión"},
    ],
    "desde": "v3.6.9-SDK6",
    "notas": ("ronda 12: LATIDO EN VR — las sesiones cerradas abruptamente (casco apagado, "
              "pestaña muerta) nunca llegan a vr_end ni a page_close y desaparecían del "
              "análisis (la ronda 11 cazó una: vr_start+stage sin cierre). El ÚLTIMO ping "
              "fecha el fin real aunque no haya vr_end"),
}
if not any(e.get('nombre') == 'vr_ping' for e in d['eventos']):
    d['eventos'].append(VR_PING)
    hechos += 1

d['ronda'] = 12
d['actualizado'] = '2026-10-19'
d['ronda12'] = {
    'cambios': [
        'boot.platform REAL: xr (dispositivo con WebXR inmersivo) vs 2d (escritorio) — antes clavado a 2d',
        'evento nuevo vr_ping cada 5 min en VR: fecha sesiones cerradas abruptamente y dibuja la curva de fps',
        'worker y receptor local sin cambios (vr_ping es un evento estándar de la cola: lo cuentan porEvento y el embudo lo ignora)',
        'nitidez 1.4→1.5 pospuesta a datos: la sesión 3.6.8 seguía abierta al cerrar la ronda',
    ],
}
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'OK · {hechos} cambios · ronda={d["ronda"]} · eventos={len(d["eventos"])}')
