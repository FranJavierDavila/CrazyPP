#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 33 · manifest del Oeste v55 → v56 (v3.6.26).

El dueño reporta (tras V3.6.25 en el dispositivo real): «es increíble la
entrada en el túnel no suena… las llegadas tampoco, igual concatenando el
sonido con la voz que sí suena». LOS ONE-SHOTS SORDOS EN EL CASCO:

  Cambio de MOTOR (oeste, módulo v56): cuatro versiones del camino
  createSfx (v3.6.22→25) no llegaron al hardware de la Quest, mientras el
  MISMO SDK con createBucle lleva galopes y rodadura al casco desde el
  primer día. Los one-shots VIAJAN ahora en el motor PROBADO:

    · Cada pista (Tunel, Tren_Llegada) es un createBucle propio
      (ignoraMute, fadeIn 0,06, stopFade 0,35): el disparo es on() — con
      revival por statechange y espera de buffer DENTRO del motor, todo
      lo que ya demostró sonar en el dispositivo.
    · _pistaTrenStep conduce: on() idempotente por frame, reloj de play
      SÓLO con suena() honesto, corte con off() ANTES del wrap de
      src.loop (margen 0,45 s sobre el fin real del mp3), desistir en
      paz a los 12 s.
    · Tunel.mp3 entra CUANDO SE BAJA LA LUZ (petición literal del dueño:
      «ver de lanzarlo cuando se baja la luz») — paso 'pre'→'in' de
      _tunnelStep, ya no al nacer la boca a lo lejos.
    · Tren_Llegada.mp3 CONCATENADO CON LA VOZ (petición literal del
      dueño: «igual concatenando el sonido con la voz que sí suena») —
      entra justo al terminar la locución real (audio._voiceDur + 0,35;
      fallback 2,8 s si el megáfono está apagado).
    · Precarga EN LOS DOS MOTORES al montar la etapa (createSfx
      heredado + el motor del galope nuevo).
    · Tunel.mp3 y Tren_Llegada.mp3 re-codificados al PERFIL PROBADO de
      caballos.mp3 (44100 Hz · 256 kbps CBR) — cero rarezas de encoder
      para el decoder de la Quest (vias a 24 kHz suena; Tunel a 24 kHz
      no: el perfil unificado elimina la variable).

  SDK v1.5.4 (FASE 12, una vez para los 5 campeonatos):
    · createBucle.precarga() — pedir + decodificar SIN sonar (el patrón
      load* de la casa, idéntico al de createSfx) para calentar el
      buffer de un one-shot minutos antes del disparo. CERO cambios de
      conducta en on()/off()/setVol/suena().

  QA: capa V re-anclada y ampliada a 74 checks (qa_tren_audio_v3626) +
  arnés runtime v3626 (36 checks: Tunel 1 vez AL BAJAR LA LUZ, Llegada 1
  vez CONCATENADA con la voz, galopes intactos, precarga sin sonido).
"""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/oeste/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 56:
    print('ya en v56 — nada que hacer')
else:
    assert m['version'] == 55, f'versión inesperada: {m["version"]}'
    m['version'] = 56
    m['note_v2146'] = (
        'v2.146 (módulo v56 · v3.6.26, ronda 33) LOS ONE-SHOTS SORDOS EN '
        'EL DISPOSITIVO — informe del dueño tras V3.6.25: «la entrada en '
        'el túnel no suena… las llegadas tampoco, igual concatenando el '
        'sonido con la voz que sí suena». CAMBIO DE MOTOR: cuatro '
        'versiones del camino createSfx no llegaron al hardware de la '
        'Quest mientras createBucle (galopes + rodadura) sonaba desde el '
        'primer día — los one-shots VIAJAN ahora en el motor PROBADO: '
        'cada pista es un createBucle (ignoraMute, fades cortos), el '
        'disparo es on() con revival y espera de buffer dentro del '
        'motor, _pistaTrenStep conduce con reloj de play sólo con '
        'suena() honesto y corte con off() antes del wrap de src.loop. '
        'MOMENTOS DEL DUEÑO: Tunel.mp3 CUANDO SE BAJA LA LUZ (paso '
        'pre→in del túnel) y Tren_Llegada.mp3 CONCATENADO CON LA VOZ '
        '(entra al caer la locución real, _voiceDur + 0,35). Las dos '
        'pistas re-codificadas al perfil probado de caballos.mp3 '
        '(44100 Hz · 256 kbps). SDK v1.5.4: createBucle.precarga() '
        '(decodificar sin sonar). QA: capa V a 74 checks + arnés '
        'runtime 36 checks.')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
    print('manifest oeste → v56 con note_v2146')
