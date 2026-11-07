#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 31 · manifest del Oeste v54 → v55 (v3.6.25).

El dueño reporta (tras V3.6.24): «los caballos no se amortiguan ni
desaparecen cuando los jinetes no están, se alejan o mueren (antes sí) ·
vias.mp3 casi imperceptible · tunel y llegada no suenan nunca». EL GALOPE
FANTASMA, diagnosticado y sellado:

  SDK v1.5.3 (una vez para los 5 campeonatos):
    (a) createSfx.play() devuelve BOOLEANO — true SÓLO cuando src.start()
        disparó de verdad; los módulos que reintentan ya no dan un
        disparo por perdido (éste era el silencio eterno de los
        one-shots: el retiro se hacía por LLAMAR a play, no por sonar).
    (b) opción «sinPend» de play(): sin auto-disparo por pend — el que
        reintenta cada frame gobierna; el pend sigue siendo el camino de
        los llamantes de un solo disparo; y un arranque real CONSUME el
        pend del mismo nombre (cero dobles disparos con rebotes).
    (c) createBucle.on() MATA la instancia huérfana de un contexto viejo
        (stop + disconnect) en vez de soltarla viva — no hay galope
        fantasma eterno tras un re-bind de VR.
    (d) vigilante anti-decode-colgado (busyAt, 20 s) en createSfx y
        createBucle: un decodeAudioData que nunca resuelve ya no bloquea
        las peticiones para siempre.

  Oeste (TrenAction):
    · LA REPARACIÓN DEL GALOPE SÓLO CON JINETE VIVO (paso/ida/ventana/
      fuga) — la auto-reparación v3.6.23 sin filtro REVIVÍA el bucle cada
      frame tras el off(true) de la muerte: el galope seguía sonando en
      herido, en el fade y tras gone (simetría forajido/indios).
    · Rodadura vias.mp3 0,13 → 0,30 (a 0,13 quedaba enterrada bajo la
      música del vagón — «casi imperceptible»).
    · _pistaTrenStep con RETIRO HONESTO: la agenda sólo se cierra cuando
      el play() devuelve TRUE (disparo real), con sinPend y margen 9 s.
    · La precarga de los one-shots ya vivía en el start() (v3.6.22): el
      silencio eterno no era buffer frío — era el play tragado.
"""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/oeste/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 55:
    print('ya en v55 — nada que hacer')
else:
    assert m['version'] == 54, f'versión inesperada: {m["version"]}'
    m['version'] = 55
    m['note_v2145'] = (
        'v2.145 (módulo v55 · v3.6.25, ronda 31) EL GALOPE FANTASMA — '
        'informe del dueño tras V3.6.24: «los caballos no se amortiguan '
        'ni desaparecen cuando los jinetes no están, se alejan o mueren '
        '(antes sí) · vias casi imperceptible · tunel y llegada no suenan '
        'nunca». FIX EN EL SDK v1.5.3, una vez para los 5 campeonatos: '
        '(a) createSfx.play() devuelve BOOLEANO — true sólo cuando el '
        'disparo fue REAL (src.start()); los one-shots del vagón se '
        'retiraban de la agenda por LLAMAR a play(), y un disparo '
        'tragado (contexto dormido / buffer tarde) era silencio eterno; '
        '(b) opción sinPend: el que reintentA cada frame gobierna y el '
        'arranque real CONSUME el pend del nombre (cero dobles); (c) '
        'createBucle.on() MATA la instancia huérfana de un contexto '
        'viejo (stop+disconnect) — sin galope fantasma eterno; (d) '
        'vigilante anti-decode-colgado (20 s). Y EN EL VAGÓN: la '
        'auto-reparación del galope SÓLO con jinete VIVO (paso/ida/'
        'ventana/fuga) — sin el filtro revivía el bucle cada frame tras '
        'el off seco de la muerte (seguía galopando herido, en el fade y '
        'tras gone: lo que el dueño ya no podía callar); rodadura vias '
        '0,13 → 0,30 (enterrada bajo la música); reintentos honestos con '
        'margen 9 s. QA: capa V a 63 checks (qa_tren_audio_v3625) + '
        'arnés runtime del CICLO DE VIDA del galope (32 checks: nace '
        '0,45, se amortigua en fuga 0,45→0,16, calla SECO al balazo, '
        'cero resurrecciones, indios simétricos, one-shots del juego 1 '
        'vez en su momento, contrato del SDK a nivel unidad).')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
    print('manifest oeste → v55 con note_v2145')
