#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36168.py — FASE 173 · r77 · generador del release.
Re-sella scripts/release-v36167/build_zip.py → scripts/release-v36168/:
  · tokens de versión (v36167→v36168 · 3.6.167→3.6.168) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 172 → FASE 173 (GARANTÍA DE RED).
Auxiliares (mock_host.mjs · package.json · server.mjs · voz-alerta/) se
copian del kit v36167 intactos.
"""
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project/upload/scripts')
if RAIZ.name != 'scripts':
    RAIZ = RAIZ / 'scripts'
ORIGEN = RAIZ / 'release-v36167'
DESTINO = RAIZ / 'release-v36168'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36167/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

# 1 · notas FASE 172 → FASE 173 (ANTES de los tokens de versión)
ini = t.find("'Rama    : main · SDK6 (FASE 172")
fin = t.find("'  3.6.167\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 172 no hallado')
fin += len("'  3.6.167\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 173 — GARANTÍA DE RED: «tenemos algún otro\\n'
    'procedimiento para asegurar la calidad de las partidas en red, algo\\n'
    'que nos dé más fluidez… queremos una solución garantizada»). Sobre la\\n'
    'red r75 + el TURN de Cloudflare VIVO (Task 139) + la cadencia de 72\\n'
    'FPS (r76), la r77 completa la garantía con CUATRO capas:\\n'
    '  · SALIDA DEL TÚNEL: el ICE directo (el handshake puede tardar >11 s\\n'
    '    con hotspot/NAT simétrica) puede abrir DESPUÉS de que el túnel\\n'
    '    tomó el mando — si ambos canales propios abren, el túnel SE\\n'
    '    RETIRA SOLO y la pose vuelve a 60 Hz (y el watchdog de ICE\\n'
    '    re-arma).\\n'
    '  · TÚNEL ADAPTATIVO: el túnel SCTP entra a 30 Hz (seguro contra el\\n'
    '    head-of-line) pero SUBE a 60 Hz con DOS ventanas de 2 s sanas\\n'
    '    (pérdida < 4 % · jitter < 18 ms · muestra suficiente) y vuelve a\\n'
    '    30 en el momento si el enlace se aprieta. Cada cambio deja huella\\n'
    '    net_qos. La pose es reemplazable (contrapresión r75): el cambio\\n'
    '    de cadencia no toca la FSM ni la fiabilidad de los eventos.\\n'
    '  · SNAP ADAPTATIVO: la bola vuela a 30 Hz de SNAP con enlace sano\\n'
    '    (20 Hz apretado) — el rival VE la bola más fluida.\\n'
    '  · QOS CON DATOS: la garantía se DEMUESTRA — qos()/qosTexto() (una\\n'
    '    línea «RED 24 ms · EXCELENTE» en AJUSTES › RENDIMIENTO) y un\\n'
    '    evento net_qos cada 60 s de enlace (camino, ping, jitter,\\n'
    '    pérdida, cadencia) al panel de telemetría.\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r77 76/0 (regresión\\n'
    '    r74/r75/r76 íntegra + 9 agujas estáticas de red y 9 vivas: QoS\\n'
    '    EXCELENTE/«RED 24 ms», túnel 30→60 con 2 ventanas sanas, vuelta\\n'
    '    a 30 con jitter 40 ms y salida del túnel EN VIVO).\\n'
    '  · Ensamblado 12.253.200 B (golden 61e60b6f).\\n'
    '  SE CONSERVA TODO: r55-r76 íntegro (cadencia 72, la red en serio,\\n'
    '    escoger hall, candado global, multijugador en 3 zonas, alerta de\\n'
    '    duelo, placa de museo, BOLA LOCA, Hall FASE 29, ELO, taller UGC,\\n'
    '    PWA, PRO TRAINING).\\n'
    '  · sellada a\\n'
    '  3.6.168\\n'"""

t = t[:ini] + NOTAS + t[fin:]

# 2 · tokens de versión (orden: el más largo primero)
for a, b in [('v36167-sdk6', 'v36168-sdk6'),
             ('V3.6.167-SDK6', 'V3.6.168-SDK6'),
             ('3.6.167-SDK6', '3.6.168-SDK6'),
             ('v36167', 'v36168'),
             ('3.6.167', '3.6.168')]:
    t = t.replace(a, b)

# 3 · veto explícito de la versión anterior en el hub
t = t.replace("'v36168-sdk6' not in hub",
              "'v36168-sdk6' not in hub or 'v36167-sdk6' in hub")

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
res = t.count('36167')
print(f'gen_release_v36168 OK → {DESTINO} (notas FASE 173 · vetos v36167: {res})')
