#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
e2e_salas_produccion.py — E2E de la cadena SALAS en producción (r129·cierre).

Prueba EN VIVO la cadena completa que r74·FASE169 construyó y A2 (r129)
agregó, que nadie había verificado de punta a punta contra el worker real:

  1 · POST /api/presencia  — latido con sala pública (st=sala, vis=pub)
  2 · GET  /api/tele?salas=1            — el registro vivo la ve (A2)
  3 · GET  /api/presencia?lista=1       — el lobby del cliente la ve
  4 · POST /api/presencia {bye:1}       — baja inmediata (limpieza)
  5 · GET  /api/tele?salas=1            — tras la baja ya no aparece

Uso: python3 scripts/e2e_salas_produccion.py [URL_BASE]
"""
import json
import sys
import time
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1
        else 'https://crazypp-tele.escala3dcorreoia.workers.dev/api')
PID = 'cpp-e2e-salas-01'
CODE = 'E2E01'
UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/129.0 Safari/537.36')

fallos = []


def pide(path, cuerpo=None):
    """GET o POST (text/plain, como sendBeacon) contra el worker."""
    dato = json.dumps(cuerpo).encode() if cuerpo is not None else None
    pet = urllib.request.Request(BASE + path, data=dato, method='POST' if dato else 'GET')
    pet.add_header('User-Agent', UA)
    if dato:
        pet.add_header('Content-Type', 'text/plain;charset=UTF-8')
    with urllib.request.urlopen(pet, timeout=20) as r:
        return json.loads(r.read().decode())


def paso(num, texto, cond, detalle=''):
    print(f"{'OK ' if cond else 'FALLO'} · {num} · {texto}" + (f' — {detalle}' if detalle else ''))
    if not cond:
        fallos.append(f'{num} · {texto} {detalle}')


print('== E2E SALAS EN PRODUCCIÓN ==')
print(f'   worker: {BASE}')

# 1 · latido con sala pública (el anfitrión "respire")
r1 = pide('/presencia', {
    'pid': PID, 'n': 'E2E salas', 'v': '3.6.210-SDK6',
    'st': 'sala', 'code': CODE, 'mj': 'normal', 'vis': 'pub',
})
paso(1, 'POST presencia · latido con sala pública aceptado',
     isinstance(r1, dict) and r1.get('ok') is True, json.dumps(r1)[:90])

time.sleep(1)

# 2 · A2: el registro vivo de salas la ve
r2 = pide('/tele?salas=1')
salas = r2.get('salas', []) if isinstance(r2, dict) else []
la_mia = [s for s in salas if s.get('code') == CODE]
paso(2, 'GET tele?salas=1 · la sala aparece en el registro vivo (A2)',
     bool(la_mia), f'total={r2.get("total")} · salas={[s.get("code") for s in salas][:5]}')
paso('2b', 'la sala trae haceSeg fresco (< 90 s · TTL del latido)',
     bool(la_mia) and 0 <= la_mia[0].get('haceSeg', 999) < 90,
     f'haceSeg={la_mia[0].get("haceSeg") if la_mia else "?"}')

# 3 · el lobby del cliente (presencia?lista=1) también la ve
r3 = pide('/presencia?lista=1')
jug = r3.get('jugadores', []) if isinstance(r3, dict) else []
yo = [j for j in jug if j.get('pid') == PID]
paso(3, 'GET presencia?lista=1 · el lobby del cliente la ve (st=sala · vis=pub)',
     bool(yo) and yo[0].get('st') == 'sala' and yo[0].get('vis') == 'pub'
     and yo[0].get('code') == CODE,
     f'nOnline={r3.get("n")} · yo={json.dumps(yo[0])[:90] if yo else "ausente"}')

# 4 · baja inmediata (pagehide → bye)
r4 = pide('/presencia', {'pid': PID, 'bye': 1})
paso(4, 'POST presencia {bye:1} · baja aceptada',
     isinstance(r4, dict) and r4.get('ok') is True, json.dumps(r4)[:60])

time.sleep(1)

# 5 · tras la baja, el registro vivo vuelve a estar limpio
r5 = pide('/tele?salas=1')
quedan = [s for s in (r5.get('salas', []) if isinstance(r5, dict) else [])
          if s.get('code') == CODE]
paso(5, 'GET tele?salas=1 · tras la baja la sala ya no aparece',
     not quedan, f'total={r5.get("total")}')

print()
if fallos:
    print(f'✗ E2E SALAS: {len(fallos)} FALLO(S)')
    for f in fallos:
        print('   ·', f)
    sys.exit(1)
print('✓ E2E SALAS COMPLETO: presencia → registro vivo (A2) → lobby → baja · 5/5 OK')
