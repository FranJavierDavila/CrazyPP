#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r115_v36105.py — capa de QA de la ronda 115 (V3.6.111-SDK6).

DOS AJUSTES DEL DUEÑO sobre el juego vivo:

  1) ADIÓS A LA REPETICIÓN DEL MEJOR PUNTO (c12+c08+c00): al terminar la
     partida ya NO se reproduce el mejor intercambio — fuera grabadora,
     fantasmas azul fantasma, cartel, cámara lenta del replay y las claves
     i18n rep_*. La fanfarria respira sola y el gatillo en 'over' es
     revancha DESDE EL PRIMER PULSO. La cámara lenta de la BOLA DE PARTIDO
     (dilatación del match point, r62) SE CONSERVA.
  2) SUPERPODER DEL RIVAL EN SU JUSTO MOMENTO (5 campeonatos): el anuncio
     con la partida congelada nace EXACTAMENTE cuando el rival GOLPEA la
     bola con la bola en SU campo — el flanco lee el golpeo real del
     árbitro (rules.lastHitter pasa a 'ai' en el contacto, registerPaddleHit)
     y exige bola en su campo (z < −1,6 del centro de mesa). Ni en pleno
     vuelo hacia el jugador ni tras el golpeo del jugador (flanco r113
     retirado). Locura/Magia/Oeste/Halloween/Orbital.

Uso: python3 scripts/qa_r115_v36105.py
"""
import os
import re
import socket
import sys
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler

RAIZ = '/home/z/my-project'
OK = []
FAIL = []


def CHK(cond, label):
    (OK if cond else FAIL).append(label)
    print(('  \u2713 ' if cond else '  \u2717 FALLO: ') + label)


import json
GH = open(os.path.join(RAIZ, 'public/game.html'), encoding='utf-8').read()
V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json'), encoding='utf-8'))
VER = V['version']

# ── 1 · SELLO ──
print('== SELLO ==')
CHK(f"const VERSION = '{VER}'" in GH, f'sello c00 = {VER}')
CHK(f"crazypp-v{VER}" in open(os.path.join(RAIZ, 'public/sw.js'),
                              encoding='utf-8').read(),
    f'PWA: caché sw.js gobernada por el bump ({VER})')

# ── 2 · RETIRO DE LA REPETICIÓN (servido) ──
print('== RETIRO DE LA REPETICIÓN ==')
PRESENTE = [
    ('RETIRO DEL DUEÑO: la REPETICIÓN DEL MEJOR INTERCAMBIO (r61)',
     'marcador del retiro en c12 (servido)'),
    ('es YA revancha en el MISMO modo',
     'el 1.er pulso en over es revancha (comentario)'),
]
for aguja, nombre in PRESENTE:
    CHK(aguja in GH, 'repetición: ' + nombre)
FUERA = [
    ('la grabadora ya no existe', '_repGrabando'),
    ('el motor de frames ya no existe', '_repStride'),
    ('los fantasmas ya no existen', 'ghostRival'),
    ('el cartel del replay ya no existe', 'createReplayBanner'),
    ('la cámara lenta del replay ya no existe', 'REP_SLOWMO'),
    ('i18n rep_t retirado', "rep_t: '"),
    ('i18n rep_slow retirado', "rep_slow: '"),
    ('i18n rep_chip retirado', "rep_chip: '"),
]
for nombre, aguja in FUERA:
    CHK(aguja not in GH, 'repetición: ' + nombre)
# la dilatación del match point (r62) SIGUE viva
CHK('this._dilT = 0;' in GH and 'this._dilF = 1;' in GH,
    'repetición: la dilatación del match point se conserva')

# ── 3 · SUPERPODER EN EL GOLPEO (5 campeonatos) ──
print('== SUPERPODER EN EL GOLPEO (5 campeonatos) ==')
FLANCOS = {
    'locura': "const golpeAi = r.lastHitter === 'ai' && ball.pos.z < -1.6;",
    'magia': "const golpeAi = r.lastHitter === 'ai' && ball.pos.z < -1.6;",
    'oeste': "const golpeAi = r.lastHitter === 'ai' && ball.pos.z < -1.6;",
    'halloween': "const golpeAi = r.lastHitter === 'ai' && !!b && !!b.pos && b.pos.z < -1.6;",
    'estacion_orbital': "const golpeAi = g.rules.lastHitter === 'ai' && g.ball.pos.z < -1.6;",
}
VIEJOS = ['ball.vel.z > 0.35', 'ball.vel.z < -0.35',
          'b.vel.z > 0.35', 'b.vel.z < -0.35',
          'g.ball.vel.z > 0.35', 'g.ball.vel.z < -0.35']
for champ, aguja in FLANCOS.items():
    t = open(os.path.join(RAIZ, f'public/championships/{champ}/index.js'),
             encoding='utf-8').read()
    CHK(aguja in t,
        f'{champ}: el poder nace EN EL GOLPEO del rival (bola en su campo)')
    for viejo in VIEJOS:
        if viejo in t:
            CHK(False, f'{champ}: flanco viejo por velocidad PRESENTE ({viejo})')
            break
    else:
        CHK(True, f'{champ}: sin flancos viejos por velocidad')

# ── EN VIVO: el flanco lee el golpeo real del árbitro ──
print('== EN VIVO (golpeo del árbitro + retiro del replay) ==')


def _puerto_libre():
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    p = s.getsockname()[1]
    s.close()
    return p


PORT = _puerto_libre()


def _servir():
    clase = partial(SimpleHTTPRequestHandler,
                    directory=os.path.join(RAIZ, 'public'))
    clase.log_message = lambda *a, **k: None
    httpd = HTTPServer(('127.0.0.1', PORT), clase)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


_httpd = _servir()
try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load')
        page.wait_for_timeout(1200)

        MECANICA = """async () => {
  const out = [];
  const g = window.__game;
  if (!g) { out.push({ ok: false, lab: 'no hay window.__game' }); return out; }

  // 1 · el flanco r115 lee el GOLPEO REAL: registerPaddleHit('ai') pone
  //     lastHitter='ai' en el MISMO instante del contacto (y rallyHits++)
  const st0 = g.rules.state;
  const hits0 = g.rules.rallyHits || 0;
  g.rules.state = 'rally';
  g.rules.serveOwnPending = false;
  g.rules.mustBounceOpp = true;
  g.rules.validBounce = true;         // sin volea: el golpeo es limpio
  g.rules.registerPaddleHit('ai');
  out.push({ ok: g.rules.lastHitter === 'ai',
             lab: 'flanco: registerPaddleHit(\\'ai\\') marca lastHitter=ai EN el contacto' });
  out.push({ ok: (g.rules.rallyHits || 0) === hits0 + 1,
             lab: 'flanco: el golpeo rival cuenta su toque (rallyHits+1)' });
  // doble golpe = falta (el árbitro manda): el flanco nunca lo verá
  const antes = g.rules.rallyHits;
  const falta = g.rules.registerPaddleHit('ai');
  out.push({ ok: Array.isArray(falta) && falta.length > 0 &&
                  g.rules.rallyHits === antes,
             lab: 'flanco: el doble golpe del rival es FALTA (no alimenta el flanco)' });
  g.rules.state = st0;

  // 2 · el retiro del replay: NADA del sistema r61 sobrevive en el objeto
  out.push({ ok: typeof g._repArranca === 'undefined' &&
                  typeof g._repTick === 'undefined' &&
                  typeof g._repReset === 'undefined' &&
                  typeof g._repFrame === 'undefined' &&
                  typeof g._repCierra === 'undefined',
             lab: 'retiro: ningún método del replay sobrevive' });
  out.push({ ok: !('ghostBall' in g) && !('ghostRival' in g) &&
                  !('replayBanner' in g) && !('_repBuf' in g) &&
                  !('_repBest' in g) && !('_repEstado' in g) &&
                  !('_repPendiente' in g),
             lab: 'retiro: sin fantasmas, cartel, buffer, estado ni pendiente' });

  // 3 · fin de partido EN VIVO: fanfarria directa (sin repetición pendiente)
  //     y la dilatación del match point sigue armándose (local)
  const dil0 = g._dilT;
  g._dilT = 0;
  g.processIntents([{ type: 'game-over', winner: 'player' }]);
  out.push({ ok: !('_repPendiente' in g),
             lab: 'retiro: la fanfarria NO arma repetición pendiente' });
  out.push({ ok: g._dilT > 0,
             lab: 'retiro: la dilatación del match point SÍ se arma (r62 viva)' });
  g._dilT = dil0; g._dilF = 1;

  return out;
}"""
        filas = page.evaluate(MECANICA)
        for fila in filas:
            CHK(fila['ok'], fila['lab'])

        browser.close()
finally:
    _httpd.shutdown()

print('== ERRORES DE PÁGINA ==')
CHK(len(errors) == 0, 'sin errores JS durante toda la batería')
for e in errors[:5]:
    print('  ·', e[:200])

print(f"\nRESULTADO: {len(OK)} OK · {len(FAIL)} fallos")
sys.exit(1 if FAIL else 0)
