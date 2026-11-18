#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · SONDEADOR DEL RECEPTOR DE PRODUCCIÓN (evidencia, no QA).
Probeta NEGRA del Worker de Cloudflare que recibe la telemetría anónima
(window.PP_TELEMETRY_ENDPOINT en 04_boot.html). Descubrimiento de la ronda 6
(telemetría, roadmap P1):

  · POST con el FORMATO DEL JUEGO  {"app":"crazy-pingpong","events":[…]}  → 400
  · POST con ARRAY DIRECTO         [{…},{…}]                             → 204  ✓
  · GET  /api/tele                 → texto fijo «telemetry: ok», SIN API de lectura

Es decir: el lote de __PP_TELE.flush() muere en el receptor con 400 desde
siempre, PERO sendBeacon devuelve true (éxito de TRANSPORTE) → el juego
vacía la cola y los eventos se pierden. El champ_rank de Magia (array
directo, application/json) SÍ llega. Además el Worker no expone NINGÚN
modo de lectura: aunque los POST entraran, no hay forma de ver los datos.

Este script NO forma parte de qa_todo (no debe depender de una red externa
en las verificaciones): es la EVIDENCIA del diagnóstico y sirve para
re-comprobar el estado del Worker cuando el dueño toque su código.
Uso: python3 scripts/sondea_tele_worker.py
"""
import json
import sys
import time
import urllib.request
import urllib.error

URL = 'https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele'
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def peticion(metodo, cuerpo=None, ctype='text/plain;charset=UTF-8', origen=None):
    # OJO: Cloudflare bloquea UAs no-navegador con «error code: 1010» (403).
    # El Quest Browser envía UA de Chromium real → para sondear la conducta
    # que ve el JUEGO hay que emular una UA de navegador.
    req = urllib.request.Request(URL, method=metodo)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                   '(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36')
    if cuerpo is not None:
        req.add_header('Content-Type', ctype)
        if isinstance(cuerpo, (dict, list)):
            cuerpo = json.dumps(cuerpo)
        req.data = cuerpo.encode('utf-8')
    if origen:
        req.add_header('Origin', origen)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, r.read().decode('utf-8', 'replace')[:200]
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b'').decode('utf-8', 'replace')[:200]
    except Exception as e:
        return -1, str(e)


def main():
    ahora = int(time.time() * 1000)
    ev_boot = {'e': 'boot', 't': ahora, 'v': 'sonda', 'sid': 'sonda-' + str(ahora)[-6:],
               'platform': '2d'}

    print('== SONDEA EL RECEPTOR DE PRODUCCIÓN ==')
    print('   ' + URL)

    # 1. vivo
    st, cuerpo = peticion('GET')
    chk(st == 200, f'GET /api/tele responde 200 (recibió {cuerpo[:40]!r}…)')
    chk('telemetry' in cuerpo.lower(), 'el texto identifica el receptor de telemetría')

    # 2. preflight CORS (lo que necesita champ_rank con application/json)
    st, _ = peticion('OPTIONS')
    chk(st in (204, 200), f'OPTIONS preflight → {st}')

    # 3. EL FORMATO DEL JUEGO (wrapper {app, events} por text/plain): HOY da 400
    st, _ = peticion('POST', {'app': 'crazy-pingpong', 'events': [ev_boot]})
    print(f'      POST wrapper del juego → {st}')
    chk(st == 204, 'POST formato del juego {app,events} ACEPTADO (204)')

    # 4. array directo (el formato que SÍ acepta y el de champ_rank de Magia)
    st, _ = peticion('POST', [ev_boot])
    chk(st == 204, f'POST array directo aceptado ({st})')

    # 5. array por application/json (camino champ_rank, con CORS)
    st, _ = peticion('POST', [dict(ev_boot, e='champ_rank')],
                     ctype='application/json', origen='https://franjavierdavila.github.io')
    chk(st == 204, f'POST application/json + Origin aceptado ({st})')

    # 6. basura → rechazo digno
    st, _ = peticion('POST', 'esto no es json')
    chk(st in (400, 415, 422), f'POST basura rechazado ({st})')

    print(f'\nRESULTADO: {ok} OK · {fails} FALLOS')
    if fails:
        print('\nDIAGNÓSTICO CONOCIDO (ronda 6): el Worker rechaza el wrapper')
        print('{"app","events"} que envía __PP_TELE.flush() con 400 y no expone')
        print('lectura. FIX propuesto (ronda de release): enviar el ARRAY directo')
        print('en c00_pre_three.js (mismo contrato que champ_rank de Magia).')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
