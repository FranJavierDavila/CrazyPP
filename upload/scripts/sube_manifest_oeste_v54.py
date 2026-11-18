#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ronda 30 · manifest del Oeste v53 → v54 (v3.6.24).

El dueño reporta (tras V3.6.23): «solo caballos» — la única pista que
llegaba al hardware de la Quest era la que escribe su ganancia DIRECTO
por frame. Tres agujeros del dispositivo + dos momentos equivocados:

  SDK v1.5.2 (una vez para los 5 campeonatos):
    (a) createSfx.play() con el AudioContext aún no «running» DESCARTABA
        el disparo — un one-shot (llegada, túnel) no tiene segunda
        oportunidad: ahora queda PENDIENTE y el «statechange» del propio
        contexto lo dispara al despertar.
    (b) createBucle.on() con el contexto dormido olvidaba el arranque:
        wanted + (desfase, pan) quedan guardados y el mismo statechange
        arranca el bucle al despertar.
    (c) suena() devolvía TRUE con una instancia de un contexto MUERTO
        (re-bind de VR) y bloqueaba la auto-reparación de los módulos.
    (d) setVol() aplicaba el gate arcMute/_arcDucked sin consultar
        ignoraMute — la escritura viva re-introducía el mute de MÚSICA.

  Oeste (TrenAction):
    · vias.mp3 con setVol DIRECTO por frame en marcha (el mecanismo que
      sí llegó al hardware en los galopes) + auto-reparación.
    · Tren_Llegada.mp3 suena «poco después de que se anuncien los
      segundos para llegar a la estación» (a +1,2 s del anuncio de
      megafonía) — petición literal del dueño; ya no al frenar.
    · Tunel.mp3 suena «cuando en el parallax del plano exterior se
      cargan las imágenes tunelboca.png, que es el comienzo de la
      entrada al túnel» (nace la fase 'pre') — petición literal.
    · one-shots CON REINTENTOS (_pistaTren/_pistaTrenStep): ningún
      disparo único se pierde por un fallo transitorio.
"""
import json
from pathlib import Path

P = Path('/home/z/my-project/public/championships/oeste/manifest.json')
m = json.loads(P.read_text(encoding='utf-8'))
if m['version'] == 54:
    print('ya en v54 — nada que hacer')
else:
    assert m['version'] == 53, f'versión inesperada: {m["version"]}'
    m['version'] = 54
    m['note_v2144'] = (
        'v2.144 (módulo v54 · v3.6.24, ronda 30) EL TREN EN EL DISPOSITIVO '
        'REAL — informe del dueño tras V3.6.23: «solo caballos» (la única '
        'pista que llegaba al hardware de la Quest era la que escribe su '
        'ganancia DIRECTO por frame). FIX EN EL SDK v1.5.2, una vez para '
        'los 5 campeonatos: (a) createSfx.play() con el AudioContext aún '
        'no «running» DESCARTABA el disparo — y un one-shot (llegada, '
        'túnel) no tiene segunda oportunidad: queda PENDIENTE y el '
        '«statechange» del propio contexto lo dispara al despertar; (b) '
        'createBucle.on() con el contexto dormido olvidaba el arranque — '
        'ahora recuerda wanted+(desfase,pan) y despierta igual; (c) '
        'suena() devolvía TRUE con una instancia de un contexto MUERTO '
        '(re-bind de VR) y bloqueaba la auto-reparación; (d) setVol() '
        'aplicaba el gate arcMute/_arcDucked sin consultar ignoraMute — '
        'la escritura viva de los SFX re-introducía el mute de MÚSICA. '
        'Y EN EL VAGÓN, los momentos EXACTOS que pidió el dueño: vias.mp3 '
        'con setVol directo por frame en marcha (el mecanismo probado del '
        'galope) + auto-reparación; Tren_Llegada.mp3 «poco después de que '
        'se anuncien los segundos para llegar a la estación» (a +1,2 s '
        'del anuncio de megafonía, no al frenar); Tunel.mp3 «cuando en el '
        'parallax del plano exterior se cargan las imágenes tunelboca.png, '
        'que es el comienzo de la entrada al túnel» (al nacer la fase '
        "pre'); one-shots CON REINTENTOS (_pistaTren/_pistaTrenStep). QA: "
        'capa V ampliada a 52 checks (qa_tren_audio_v3624) + arnés runtime '
        'que CONDUCE el juego real por los eventos reales (23 checks: '
        'departa→vias en bucle, boca del túnel→Tunel, anuncio→Tren_Llegada '
        'a +1,2 s, sin doble disparo, fixes del SDK a nivel unidad).')
    P.write_text(json.dumps(m, ensure_ascii=False, indent=2) + '\n',
                 encoding='utf-8')
    print('manifest oeste → v54 con note_v2144')
