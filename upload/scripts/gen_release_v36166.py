#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36166.py — FASE 171 · r75 · generador del release.
Re-sella scripts/release-v36165/build_zip.py → scripts/release-v36166/:
  · tokens de versión (v36165→v36166 · 3.6.165→3.6.166) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASES 168-170 → FASE 171 (LA RED EN SERIO).
Auxiliares (mock_host.mjs · package.json · server.mjs · voz-alerta/) se
copian del kit v36165 intactos.
"""
import re
import shutil
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload/scripts')
ORIGEN = RAIZ / 'release-v36165'
DESTINO = RAIZ / 'release-v36166'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36165/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

# 1 · notas FASES 168-170 → FASE 171 (ANTES de los tokens de versión)
ini = t.find("'Rama    : main · SDK6 (FASES 168-170")
fin = t.find("'  3.6.165\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASES 168-170 no hallado')
fin += len("'  3.6.165\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 171 — LA RED EN SERIO: informe del dueño\\n'
    'con Quest 3 + Quest 2 en la MISMA WiFi: «la partida va a saltos y\\n'
    'trompicones y no es jugable» y «en la segunda partida yo tenía que\\n'
    'sacar y la bola la tenía el rival». La red es lo primero: sin red no\\n'
    'hay juego).\\n'
    '  · BUFFER QUE RESPIRA (tirones · 1/2): el jitter buffer del avatar\\n'
    '    sube su techo adaptativo 120→220 ms y la extrapolación 100→160 ms;\\n'
    '    autoDelay reserva 3×jitter (el PICO del Wi-Fi de casco — ráfagas de\\n'
    '    ahorro de energía — no la media). El retraso del avatar es\\n'
    '    PURAMENTE visual (principio 3 de la spec): mejor respiro que el\\n'
    '    ciclo starves→congelar→SALTO que era el trompicon.\\n'
    '  · CONTRAPRESIÓN (tirones · 2/2): _sendFast ya NO envía la pose si el\\n'
    '    canal arrastra cola (bufferedAmount > 32 KB: la pose es\\n'
    '    reemplazable — la nueva corrige la vieja; > 128 KB ahogado: ni\\n'
    '    eventos, al próximo tick). El túnel de emergencia (SCTP\\n'
    '    fiable+ordenado por el relevo de PeerJS) baja la pose a 30 Hz DE\\n'
    '    ORIGEN en _enterTunnel: a 60 Hz cada pérdida paraba TODA la cola\\n'
    '    (head-of-line).\\n'
    '  · DEGRADACIÓN POR JITTER: pérdida >10 % o jitter EMA > 28 ms → 30 Hz\\n'
    '    honestos; < 18 ms recupera. El Wi-Fi del casco junta paquetes SIN\\n'
    '    perderlos — la pérdida sola nunca lo veía.\\n'
    '  · EL SAQUE DE LA SEGUNDA PARTIDA (fantasma): revancha de AMBOS a la\\n'
    '    vez dispara DOS mstart con startAt distintos — el «yo tenía que\\n'
    '    sacar y la bola la tenía el rival». GUARDA anti doble-arranque (el\\n'
    '    r que llega tarde se ignora: mstart en los últimos 8 s o partido\\n'
    '    vivo) + el anfitrión SELA cada partida con un RESYNC autoridad 700\\n'
    '    ms tras el MATCH_START (marcador, sacador, gameOpener, rallySeq y\\n'
    '    setHeld del invitado — auto-curación al abrir CADA partida).\\n'
    '  · QA: test_red_nucleo 60/0 (agujas r75: tope 220, extrap 160, 3×\\n'
    '    jitter) · qa_vestibulo_r75 35/0 (regresión r74 íntegra + 7 agujas\\n'
    '    de red) · arnes_r75 6/0 (30 páginas · rankini 1 GET · 0 errores).\\n'
    '  · Ensamblado 12.244.118 B (golden 6929c490).\\n'
    '  SE CONSERVA TODO: r55-r74 íntegro (escoger hall, candado global,\\n'
    '    multijugador en 3 zonas, alerta de duelo, placa de museo r73,\\n'
    '    guarda _rankiniFresh, anclaje r69/r71, ola data-driven, BOLA LOCA,\\n'
    '    Hall FASE 29, multijugador, ELO, taller UGC, PWA, PRO TRAINING).\\n'
    '  · sellada a\\n'
    '  3.6.166\\n'"""

t = t[:ini] + NOTAS + t[fin:]

# 2 · tokens de versión (orden: el más largo primero)
for a, b in [('v36165-sdk6', 'v36166-sdk6'),
             ('V3.6.165-SDK6', 'V3.6.166-SDK6'),
             ('3.6.165-SDK6', '3.6.166-SDK6'),
             ('v36165', 'v36166'),
             ('3.6.165', '3.6.166')]:
    t = t.replace(a, b)

# 3 · veto explícito de la versión anterior en el hub
t = t.replace("'v36166-sdk6' not in hub",
              "'v36166-sdk6' not in hub or 'v36165-sdk6' in hub")

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
res = t.count('36165')
print(f'gen_release_v36166 OK → {DESTINO} (notas FASE 171 · vetos v36165: {res})')
