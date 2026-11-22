#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36167.py — FASE 172 · r76 · generador del release.
Re-sella scripts/release-v36166/build_zip.py → scripts/release-v36167/:
  · tokens de versión (v36166→v36167 · 3.6.166→3.6.167) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 171 → FASE 172 (CADENCIA ASEGURADA).
Auxiliares (mock_host.mjs · package.json · server.mjs · voz-alerta/) se
copian del kit v36166 intactos.
"""
import os
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project/upload/scripts')
if RAIZ.name != 'scripts':
    RAIZ = RAIZ / 'scripts'
ORIGEN = RAIZ / 'release-v36166'
DESTINO = RAIZ / 'release-v36167'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36166/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

# 1 · notas FASE 171 → FASE 172 (ANTES de los tokens de versión)
ini = t.find("'Rama    : main · SDK6 (FASE 171")
fin = t.find("'  3.6.166\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 171 no hallado')
fin += len("'  3.6.166\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 172 — CADENCIA ASEGURADA: petición del\\n'
    'dueño: «mejorar las partidas en red para que funcionen 100 %\\n'
    'correctas, y sincronizadas y con una cadencia de FPS asegurada de al\\n'
    'menos 72 FPS que es lo mínimo recomendado para las gafas»). Sobre la\\n'
    'red de r75 — y el TURN de Cloudflare ya VIVO en producción desde el\\n'
    'hotfix del worker: /api/ice → turn:true con 6 variantes de\\n'
    'turn.cloudflare.com y credenciales efímeras de 6 h — la r76 asegura\\n'
    'LA CADENCIA: el gobernador de rendimiento (r81/r96) sube su PISO de\\n'
    '60 a 72 Hz.\\n'
    '  · PISO 72 (PERF_PISO): la degradación regala IMAGEN primero —\\n'
    '    fovea → escala (tope 0,80) — y la tasa solo baja 90→72 (MÁS\\n'
    '    presupuesto de GPU por frame SIN bajar del piso). El 60 queda\\n'
    '    SOLO como EMERGENCIA honesta: imagen al mínimo y media < 60.\\n'
    '  · SONDA DE CALIBRACIÓN: pasa con 68 de media y peor segundo ≥55\\n'
    '    (72 sostenidos con margen; antes 63/55 para el suelo 60). El\\n'
    '    perfil guardado bajo 72 se recupera AL PISO al cargar.\\n'
    '  · SINCRONIZACIÓN INVISIBLE: en partida en red la telemetría se\\n'
    '    congela bajo 68 FPS (antes 58) — la partida manda; y el vr_ping\\n'
    '    de 5 min lleva el ESTADO DEL GOBERNADOR (tasa objetivo y real\\n'
    '    del visor, perfil, escalones, ¿partida en red?) para VER en el\\n'
    '    panel si cada casco rinde a 72/90.\\n'
    '  · RED heredada viva: TURN de Cloudflare · jitter buffer 220/160 ms\\n'
    '    con 3×jitter · contrapresión 32/128 KB · túnel a 30 Hz · guarda\\n'
    '    de revancha + resync del anfitrión (r75).\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r76 59/0 (regresión\\n'
    '    r74/r75 íntegra + 14 agujas de cadencia: piso, escalera, sonda,\\n'
    '    emergencia, ping con perf y la carga del perfil a 60→72 en\\n'
    '    vivo).\\n'
    '  · Ensamblado 12.247.534 B (golden c3def1e5).\\n'
    '  SE CONSERVA TODO: r55-r75 íntegro (la red en serio, escoger hall,\\n'
    '    candado global, multijugador en 3 zonas, alerta de duelo, placa\\n'
    '    de museo r73, guarda _rankiniFresh, anclaje r69/r71, ola\\n'
    '    data-driven, BOLA LOCA, Hall FASE 29, multijugador, ELO, taller\\n'
    '    UGC, PWA, PRO TRAINING).\\n'
    '  · sellada a\\n'
    '  3.6.167\\n'"""

t = t[:ini] + NOTAS + t[fin:]

# 2 · tokens de versión (orden: el más largo primero)
for a, b in [('v36166-sdk6', 'v36167-sdk6'),
             ('V3.6.166-SDK6', 'V3.6.167-SDK6'),
             ('3.6.166-SDK6', '3.6.167-SDK6'),
             ('v36166', 'v36167'),
             ('3.6.166', '3.6.167')]:
    t = t.replace(a, b)

# 3 · veto explícito de la versión anterior en el hub
t = t.replace("'v36167-sdk6' not in hub",
              "'v36167-sdk6' not in hub or 'v36166-sdk6' in hub")

DESTINO.mkdir(exist_ok=True)
(DESTINO / 'build_zip.py').write_text(t, encoding='utf-8')
# TODO el kit auxiliar del release anterior, excepto el build_zip re-sellado
for f in ORIGEN.iterdir():
    if f.name == 'build_zip.py':
        continue
    d = DESTINO / f.name
    if f.is_dir():
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(f, d)
    else:
        shutil.copy2(f, d)

# verificación mínima: sin tokens viejos salvo los vetos deliberados
res = t.count('36166')
print(f'gen_release_v36167 OK → {DESTINO} (notas FASE 172 · vetos v36166: {res})')
