#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_halloween_rt_r85.py — RUNTIME de humo (Playwright + SwiftShader):
   el juego REAL descubre y LANZA el campeonato halloween (?champ=halloween):
   · console '[champs] previsualización de halloween' (lanzado)
   · SIN '[champs] import halloween' de error ni '[champs] start' fallido
   · SIN pageerrors durante el arranque
   · TODOS los assets de halloween (12 poses webp + mapa + normas + salas + bso)
     sirven HTTP 200 y NINGUNO requestfailed (el rival no queda en silueta)
   · championships.json servido con halloween y SIN valle_neon"""
import json, os, subprocess, sys, threading, time, functools
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project'
PUB = os.path.join(RAIZ, 'public')
PORT = 8741

ok = fallos = 0
def CHK(cond, nombre):
    global ok, fallos
    print(('  [OK]    ' if cond else '  [FALLO] ') + nombre)
    if cond: ok += 1
    else: fallos += 1

Handler = functools.partial(SimpleHTTPRequestHandler, directory=PUB)
srv = ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

URL = 'http://127.0.0.1:%d/game.html?champ=halloween&pp_tele=0' % PORT
print('servidor :%d · %s' % (PORT, URL))

with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                 '--use-angle=swiftshader', '--autoplay-policy=no-user-gesture-required'])
    pg = b.new_page(viewport={'width': 1280, 'height': 720})
    cons, errs, fallidos = [], [], []
    pg.on('console', lambda m: cons.append((m.type, m.text)))
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('requestfailed', lambda r: fallidos.append((r.url, r.failure)))
    pg.goto(URL, wait_until='load', timeout=60000)
    # espera al arranque del campeonato (import + start del módulo + assets)
    t0 = time.time()
    lanzado = False
    while time.time() - t0 < 30:
        lanzado = any(t == 'info' and 'previsualización de halloween' in tx for t, tx in cons)
        if lanzado:
            break
        pg.wait_for_timeout(500)
    CHK(lanzado, 'champloader LANZA halloween (console.info previsualización)')
    pg.wait_for_timeout(6000)   # margen para poses/mapa/bso

    warns_champ = [tx for t, tx in cons if t == 'warning' and '[champs]' in tx]
    CHK(not any('halloween' in w for w in warns_champ),
        'sin warnings del champloader sobre halloween %s' % ([w for w in warns_champ if 'halloween' in w][:2] or ''))
    CHK(len(errs) == 0, 'cero pageerrors (%d)' % len(errs))
    if errs: print('   pageerrors:', errs[:3])

    fal_hall = [(u, f) for u, f in fallidos if 'halloween' in u]
    CHK(not fal_hall, 'ningún asset de halloween fallido (%d)' % len(fal_hall))
    if fal_hall:
        for u, f in fal_hall[:5]:
            print('   ✗', u, f)

    # assets servidos: comprobar por HTTP directo (12 poses + mapa + normas + salas + bso + risa)
    nombres = (['present', 'idle', 'focused', 'surprised', 'panic', 'laughing', 'crazy',
                'angry', 'picando', 'loosing', 'defeated', 'victory', 'rival'])
    mal200 = []
    for n in nombres:
        r = pg.request.get('http://127.0.0.1:%d/championships/halloween/assets/%s.webp' % (PORT, n))
        if r.status != 200: mal200.append(n)
    for extra in ['mapa.webp', 'normas_halloween.png', 'sala_floor.jpg', 'sala_back.jpg',
                  'sala_ceil.jpg', 'sala_front.jpg', 'sala_left.jpg', 'sala_right.jpg',
                  'bso.wav', 'risas.mp3', 'insignia.png',
                  # r86 · escenario real + superpoderes
                  'mano1.webp', 'mano2.webp', 'mano3.webp', 'losa.jpg', 'superpower.webp',
                  'gelatina.webp', 'calabaza.glb', 'mosca.webp',
                  'power_mano.webp', 'power_moscas.webp', 'power_calabaza.webp', 'power_gelatina.webp',
                  'decor_arana.png', 'decor_calabaza.png', 'decor_lapida.png', 'decor_ojos.png']:
        r = pg.request.get('http://127.0.0.1:%d/championships/halloween/assets/%s' % (PORT, extra))
        if r.status != 200: mal200.append(extra)
    CHK(not mal200, 'todos los assets de halloween responden 200 (%d fallos: %s)' % (len(mal200), mal200[:5]))

    reg = pg.request.get('http://127.0.0.1:%d/championships/championships.json' % PORT).json()
    ids = [e['id'] if isinstance(e, dict) else e for e in reg['championships']]
    CHK('halloween' in ids and 'valle_neon' not in ids, 'championships.json SERVIDO: halloween sí · valle_neon no')

    # el editor UGC también se sirve
    r = pg.request.get('http://127.0.0.1:%d/ugc/index.html' % PORT)
    CHK(r.status == 200 and 'TALLER UGC' in r.text(), '/ugc/index.html servido con EL TALLER UGC')

    pg.screenshot(path=os.path.join(RAIZ, 'scripts', '_r85_halloween_rt.png'))
    b.close()
srv.shutdown()

print()
print('RUNTIME HALLOWEEN · RESUMEN: %d OK · %d FALLO' % (ok, fallos))
sys.exit(1 if fallos else 0)
