#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 29 · manifest del Oeste v52 → v53 (v3.6.23).

El dueño reporta que NO se oyen las 4 pistas del tren. Diagnóstico (QA
runtime, 24 checks): la cadena fetch/decode/ctx está SANA — el silencio
era el gate arcMute/_arcDucked de los motores SDK (mute de MÚSICA del
arcade aplicado a pistas que no lo son). Fix: SDK v1.5.1 «ignoraMute» en
rodadura, galopes y SFX de la etapa + auto-reparación por frame + sin
«¡YIHAAA!» sintético en las entradas (petición del dueño).
"""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/oeste/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 53:
    print('ya en v53 — nada que hacer')
else:
    assert m['version'] == 52, f'versión inesperada: {m["version"]}'
    m['version'] = 53
    m['note_v2143'] = (
        'v2.143 (módulo v53 · v3.6.23, ronda 29) EL TREN SE OYE SIEMPRE — '
        'informe del dueño: «no se escuchan los sonidos del tren, ni las '
        'llegadas, ni los túneles». CAUSA PROBADA (QA runtime de 24 checks '
        'sobre el juego real): la cadena fetch→decode→ctx estaba SANA (los 4 '
        'mp3 audibles en el propio contexto del juego); el silencio era el '
        'GATE arcMute/_arcDucked de los motores del SDK — el silencio de la '
        'MÚSICA del arcade se estaba aplicando a las pistas del tren, que no '
        'son música (los sintéticos de la casa nunca consultaron ese '
        'interruptor y por eso sí se oían). FIX: SDK v1.5.1 con '
        '«ignoraMute» — rodadura (vias), galopes (pool 1+3) y SFX de la '
        'etapa (llegadas, túnel, risas) suenan SIEMPRE; el mute sigue '
        'gobernando la MÚSICA (BSO del saloon y vagón). Además: '
        'auto-reparación por frame de los 3 bucles (el contexto renacido en '
        'un re-bind de VR ya no deja el trayecto mudo) y el primer play() de '
        'una pista ya no muere en silencio (play pendiente que se dispara al '
        'decodificar). Y a petición del dueño: FUERA el «¡YIHAAA!» '
        'sintético de las entradas del forajido y de los indios — entran '
        'galopando con su caballos.mp3 desfasado y paneado.')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
    print('manifest oeste → v53 con note_v2143')
