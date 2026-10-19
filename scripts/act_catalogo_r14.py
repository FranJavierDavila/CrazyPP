#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RONDA 14 · actualiza el catálogo de telemetría:
  · el resumen añade sesionesVR: permanencia REAL en el casco (ciclos
    vr_start → vr_ping* → vr_end), con duración real o estimada por el
    último ping, estado (cerrada/interrumpida/abierta), fps y curva.
  · el vr_ping ya documentado (ronda 12) estrena datos reales: 1.er ping
    en producción el 10-19 (68 fps al minuto 5 de la 1.ª sesión 3.6.10).
  · reversión de nitidez 1.5→1.4 por la regla pre-comprometida (media
    63 < 72 en el vr_end de la 3.6.10) — se documenta en notas.
Idempotente: los reemplazos se cuentan."""
import json
from pathlib import Path

P = Path('/home/z/my-project/scripts/telemetria_catalogo.json')
d = json.loads(P.read_text(encoding='utf-8'))

hechos = 0
for e in d['eventos']:
    if e.get('nombre') == 'vr_ping':
        e['notas'] = (
            "ronda 12: LATIDO EN VR — las sesiones cerradas abruptamente (casco apagado, "
            "pestaña muerta) nunca llegan a vr_end ni a page_close y desaparecían del "
            "análisis (la ronda 11 cazó una: vr_start+stage sin cierre). El ÚLTIMO ping "
            "fecha el fin real aunque no haya vr_end. ronda 14: PRIMER PING REAL en "
            "producción (10-19, 68 fps al minuto 5 de la 1.ª sesión 3.6.10) y el resumen "
            "ya lo consume: sesionesVR fecha la duración con él")
        hechos += 1

d['ronda'] = 14
d['actualizado'] = '2026-10-19'
d['ronda14'] = {
    'cambios': [
        'resumen.sesionesVR (worker + receptor local en paridad): hasta 12 ciclos VR '
        'recientes — sid, versión, inicio, dur (real del vr_end o ≈ estimada del último '
        'vr_ping), durReal, estado (cerrada/interrumpida/abierta), fps media (min-max) '
        'del vr_end, pings y curva (hasta 24 pings: minuto de sesión + fps)',
        'panel /telemetria: tabla «Sesiones VR (lentes)» con sparkline de fps (línea '
        'punteada = 72 de confort) y badge de estado; ≈ marca la duración estimada',
        'reversión de nitidez 1.5→1.4 (regla pre-comprometida: media 63 < 72 en la 1.ª '
        'sesión real 3.6.10) — el juego recupera fluidez; nota en el catálogo por ser '
        'la decisión que gobierna qué fps veremos en la curva',
        'verify_pages_live con opt-out pp_tele=0: los bots de verificación dejan de '
        'emitir boot 2d a producción (contaminación cazada el 10-19: 6 boots de bots)',
    ],
    'sesionesVR': {
        'estado': {
            'cerrada': 'el ciclo terminó con vr_end: dur real y fps/fpsMin/fpsMax del vr_end',
            'interrumpida': 'sin vr_end pero CON vr_ping: dur ≈ estimada por el último ping (caso k5ui6abo)',
            'abierta': 'vr_start sin vr_end ni pings (sesión de < 5 min, en curso o muerta muy pronto)',
        },
        'curva': 'muestras {m: minutos desde vr_start, fps} — hasta 24 por ciclo; dibuja la caída o estabilidad del rendimiento DENTRO de la sesión',
    },
}
P.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'OK · {hechos} cambios · ronda={d["ronda"]} · eventos={len(d["eventos"])}')
