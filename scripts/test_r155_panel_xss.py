#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r152 · AUDITORÍA 9-10 · ARNÉS r155 · PANEL DE TELEMETRÍA ANTE DATOS HOSTILES
==============================================================================
Única superficie web que jamás había sido probada dinámicamente: el panel
del dueño (telemetria.html) renderiza nombres de EVENTO, sid, versiones y
mensajes de error que llegan de CLIENTES ARBITRARIOS a través del worker de
D1 (sanea() acota longitudes pero el CONTENIDO es libre: `<img src=x
onerror=…>` cabe en 40 caracteres). Este arnés abre el panel en Chromium
headless, intercepta TODAS las respuestas del worker y las sustituye por un
resumen/eventos/rank HOSTIL SINTÉTICO (payload en cada campo remoto) y
exige: cero ejecución, cero nodos inyectados, texto escapado y atributos
intactos. El mismo contrato que qa_ugc_guardia amarra en el núcleo.

Ejecución: python3 -I scripts/test_r155_panel_xss.py   (≈15 s)
"""
import http.server
import json
import os
import socketserver
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(os.path.dirname(HERE), 'public')
PORT = 3009

# ── payloads: caben en los límites reales de sanea() (e ≤40, sid ≤48) ──
PAY = '__ppPwned'
E_HOSTIL = '<img src=x onerror=%s=1>' % PAY          # 35 B (nombre de evento)
SID_HOSTIL = '"><svg onload=%s=2>' % PAY             # 26 B
N_HOSTIL = '<img src=x onerror=%s=3>' % PAY          # nombre de jugador
V_HOSTIL = '<script>%s()</script>' % PAY             # versión
MSG_HOSTIL = '<svg onload=%s=4>' % PAY               # error
EST_HOSTIL = '<img src=x onerror=%s=5>' % PAY        # estado VR
CHAMP_HOSTIL = '"><img src=x onerror=%s=6>' % PAY    # clave de champRank
TS = 1795717752532

RESUMEN = {
    'ok': True, 'total': 42, 'ts': TS, 'sesionesUnicas': 1, 'arranques24h': 1,
    'sesiones': [{'sid': SID_HOSTIL, 'n': 3, 'primero': TS, 'ultimo': TS}],
    'porEvento': {E_HOSTIL: 2},
    'porDia': [{'dia': '2026-11-26', 'eventos': 12}],
    'duraciones': {'n': 1, 'media': 300, 'max': 300},
    'fps': {'medio': 90, 'muestras': 12},
    'versiones': [{'v': V_HOSTIL, 'eventos': 5}],
    'sesionesVR': [{'sid': SID_HOSTIL, 'inicio': TS, 'dur': 120,
                    'estado': EST_HOSTIL, 'fps': 90, 'fpsMin': 85, 'fpsMax': 92,
                    'curva': [{'m': 1, 'fps': 90}]}],
    'vrDuracion': {'n': 1, 'media': 120, 'max': 120},
    'champRank': {CHAMP_HOSTIL: {'partidas': 3, 'victorias': 1, 'mejor': 100,
                                 'estrellas': 2}},
    'erroresTop': [{'e': MSG_HOSTIL, 'n': 4}],
    'ultimos': [{'e': E_HOSTIL, 't': TS, 'n': N_HOSTIL, 'sid': SID_HOSTIL}],
    'alarmas': {'nivel': 'verde', 'items': []},
}
EVENTOS = [
    {'e': 'boot', 't': TS, 'v': V_HOSTIL, 'sid': SID_HOSTIL, 'platform': '2d',
     'n': N_HOSTIL},
    {'e': 'vr_end', 't': TS, 'v': V_HOSTIL, 'sid': SID_HOSTIL, 'dur': 120,
     'fps': 90},
    {'e': 'page_close', 't': TS, 'v': V_HOSTIL, 'sid': SID_HOSTIL},
]
RANK = {'rank': {'elo': [{'pid': 'p1', 'n': N_HOSTIL, 'el': 1200, 'w': 3,
                          'part': 5, 'p2p': 2, 'ach': 4, 'bs': 100, 'pt': 40,
                          'st': 2, 'hace': 60}],
                 'vics': [], 'pts': [], 'logros': []}}


def serve():
    os.chdir(PUBLIC)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):   # silencio
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()

    from playwright.sync_api import sync_playwright

    fails = []
    ok = 0

    def chk(cond, label):
        nonlocal ok
        print(('  ✓ ' if cond else '  ✗ FALLO: ') + label)
        ok += 1 if cond else 0
        if not cond:
            fails.append(label)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--use-gl=swiftshader'])
        ctx = browser.new_context(viewport={'width': 1280, 'height': 900})
        ctx.add_init_script(
            "try { localStorage.setItem('pp_tele_clave','qa-clave-r8');"
            " localStorage.setItem('pp_tele_url','https://panel-mock.test/api/tele');"
            " } catch (e) {}")
        page = ctx.new_page()
        perr = []
        page.on('pageerror', lambda e: perr.append(str(e)))
        cons = []
        page.on('console', lambda m: cons.append(m.text) if m.type == 'error' else None)

        def mock_worker(route):
            url = route.request.url
            cors = {
                'status': 200,
                'headers': {'access-control-allow-origin': '*',
                            'content-type': 'application/json'},
            }
            if '?salud=1' in url:
                route.fulfill(**cors, body=json.dumps(
                    {'ok': True, 'total': 42, 'ts': TS}))
            elif '?resumen=1' in url:
                route.fulfill(**cors, body=json.dumps(RESUMEN))
            elif '?eventos=' in url:
                route.fulfill(**cors, body=json.dumps({'eventos': EVENTOS}))
            elif '?rank=1' in url:
                route.fulfill(**cors, body=json.dumps(RANK))
            else:
                route.fulfill(**cors, body=json.dumps({'ok': True}))
        ctx.route('https://panel-mock.test/**', mock_worker)

        page.goto('http://127.0.0.1:%d/telemetria.html' % PORT,
                  wait_until='networkidle')
        page.wait_for_timeout(1200)

        # 1 · el panel completó la carga sin excepciones fatales
        chk(not perr, 'carga del panel sin pageerrors (%s)' %
            (perr[:1] or 'limpio'))

        # 2 · NINGÚN payload se ejecutó
        pwned = page.evaluate('window.__ppPwned === undefined')
        chk(pwned, 'cero ejecución de payloads (window.__ppPwned undefined)')

        # 3 · #timeline: el evento hostil es TEXTO, no nodos
        tl = page.evaluate('''() => {
          const el = document.getElementById('timeline');
          const malos = el.querySelectorAll('img,svg,script,iframe').length;
          const txt = el.innerText.includes('<img src=x onerror=');
          return { malos, txt };
        }''')
        chk(tl['malos'] == 0 and tl['txt'],
            'timeline: nombre de evento hostil escapado, 0 nodos inyectados')

        # 4 · #tJugadores: el sid hostil queda LITERAL en data-sid (atributo
        #     intacto) y no hay svg dentro
        jug = page.evaluate('''() => {
          const tr = document.querySelector('#tJugadores tr[data-sid]');
          if (!tr) return { ok: false };
          const literal = tr.getAttribute('data-sid') === %s;
          const malos = tr.querySelectorAll('svg,img,script').length;
          return { ok: true, literal, malos };
        }''' % json.dumps(SID_HOSTIL))
        chk(jug.get('ok') and jug.get('literal') and jug.get('malos') == 0,
            'tJugadores: data-sid LITERAL (atributo no roto) y 0 nodos svg')

        # 5 · #tVR: estado hostil como texto, 0 img dentro
        vr = page.evaluate('''() => {
          const el = document.getElementById('tVR');
          return { malos: el.querySelectorAll('img,svg,script').length,
                   txt: el.innerText.includes('<img src=x onerror=') };
        }''')
        chk(vr['malos'] == 0 and vr['txt'],
            'tVR: estado hostil escapado, 0 nodos inyectados')

        # 6 · #gCampeonatos: la CLAVE hostil de champRank es texto
        #     (textContent: el bloque puede vivir en un contenedor sin
        #     layout, y innerText devolvería '' aunque esté bien escapado)
        ch = page.evaluate('''() => {
          const el = document.getElementById('gCampeonatos');
          return { malos: el.querySelectorAll('img,svg,script').length,
                   txt: el.textContent.includes('<img src=x onerror=') };
        }''')
        chk(ch['malos'] == 0 and ch['txt'],
            'gCampeonatos: clave champRank hostil escapada')

        # 7 · #problemas: el mensaje de error hostil es texto
        pb = page.evaluate('''() => {
          const el = document.getElementById('problemas');
          return { malos: el.querySelectorAll('img,svg,script').length,
                   txt: el.innerText.includes('<svg onload=') };
        }''')
        chk(pb['malos'] == 0 and pb['txt'],
            'problemas: mensaje de error hostil escapado')

        # 8 · notaVersion: la versión hostil NO crea <script> ejecutable
        nv = page.evaluate('''() => {
          const el = document.getElementById('notaVersion');
          return { scripts: el.querySelectorAll('script').length,
                   txt: el.innerText.includes('<script>') };
        }''')
        chk(nv['scripts'] == 0 and nv['txt'],
            'notaVersion: versión hostil como TEXTO, 0 <script> creados')

        # 9 · en TODO el documento no hay nodo inyectado por los payloads
        doc = page.evaluate('''() => ({
          malos: document.querySelectorAll(
            'img[src="x"], svg[onload], script:empty').length,
        })''')
        chk(doc['malos'] == 0,
            'documento entero: 0 nodos nacidos de los payloads')

        # 10 · el JSON crudo va por textContent (nunca innerHTML)
        jr = page.evaluate('''() => {
          const el = document.getElementById('jsonResumen');
          return { seguro: el && el.children.length === 0,
                   txt: el && el.textContent.includes('<script>') };
        }''')
        chk(jr['seguro'] and jr['txt'],
            'jsonResumen: JSON crudo por textContent, sin hijos')

        # 11 · el panel está VIVO: salud (mock) encendió el LED verde
        led = page.evaluate(
            "document.getElementById('led').className.includes('verde') || "
            "document.getElementById('led').classList.length > 0")
        chk(led, 'salud(): el LED reaccionó al mock (panel funcional)')

        # 12 · la ficha no se abrió sola (sólo por click del dueño)
        ficha = page.evaluate(
            "document.getElementById('ficha').className.includes('oculto')")
        chk(ficha, 'ficha individual cerrada (sin autoclicks)')

        # diagnóstico de render (siempre): consola de errores y alarma
        diag = page.evaluate('''() => ({
          alarma: (document.getElementById('alarma') || {}).innerText || '',
          kpis: (document.getElementById('kpis') || {}).innerHTML.length,
          timeline: (document.getElementById('timeline') || {}).innerHTML.length,
          champs: (document.getElementById('gCampeonatos') || {}).innerHTML.slice(0, 400),
        })''')
        print('  DIAG · consola-errores:', cons[:2])
        print('  DIAG · alarma:', repr(diag['alarma'][:200]),
              '· kpis:', diag['kpis'], '· timeline:', diag['timeline'])
        print('  DIAG · gCampeonatos:', repr(diag['champs']))

        browser.close()

    print()
    if fails:
        print('✗ r155 PANEL HOSTIL: %d OK · %d FALLO(S): %s' %
              (ok, len(fails), ' · '.join(fails)))
        sys.exit(1)
    print('✓ PANEL r155: %d OK · resumen/eventos/rank HOSTILES → cero '
          'ejecución, cero nodos, texto escapado, atributos intactos' % ok)
    sys.exit(0)


if __name__ == '__main__':
    main()
