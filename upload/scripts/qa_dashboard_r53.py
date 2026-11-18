#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_dashboard_r53.py — prueba del panel de telemetría visual (FASE 147).
Sirve public/ en local, inyecta la CLAVE por localStorage (jamás en la URL)
y verifica con Chromium headless:
  · portada amable sin clave → al meter clave, dashboard
  · KPIs pintados (6 tarjetas)
  · gráficas SVG presentes (área, 2 donuts)
  · tabla de jugadores con filas reales
  · timeline con frases legibles
  · 0 pageerrors
"""
import http.server
import os
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project/upload/public'
PUERTO = 3117
CLAVE = open('/home/z/my-project/upload/scripts/worker-tele/.clave-produccion',
             encoding='utf-8').read().strip()
OK = True


def chk(cond, msg):
    global OK
    print(f'  [{"OK" if cond else "FALLO"}] {msg}')
    OK = OK and bool(cond)


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=RAIZ, **k)

    def log_message(self, *a):
        pass


httpd = socketserver.ThreadingTCPServer(('127.0.0.1', PUERTO), Silencioso)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{PUERTO}/telemetria.html'

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1360, 'height': 900})
    errores = []
    pg.on('pageerror', lambda e: errores.append(str(e)))

    # 1 · sin clave: portada
    pg.goto(URL, wait_until='domcontentloaded', timeout=30000)
    pg.wait_for_timeout(2500)
    chk(pg.locator('#portada').is_visible(), 'sin clave: portada visible')
    chk('CRAZY' in pg.title() and 'Telemetría' in pg.title(), f'título = {pg.title()!r}')

    # 2 · inyecta clave y recarga
    pg.evaluate("k => localStorage.setItem('pp_tele_clave', k)", CLAVE)
    pg.goto(URL, wait_until='domcontentloaded', timeout=30000)
    try:
        pg.wait_for_selector('#contenido:not(.oculto)', timeout=30000)
        datos = True
    except Exception:
        datos = False
    chk(datos, 'con clave: dashboard visible')
    if not datos:
        print('  · refresco:', pg.locator('#refresco').inner_text())
        b.close(); sys.exit(1)
    pg.wait_for_timeout(1200)

    # 3 · KPIs y gráficas
    n_kpi = pg.locator('.kpi').count()
    chk(n_kpi == 6, f'KPIs pintados ({n_kpi} de 6)')
    chk(pg.locator('#gDias svg').count() == 1, 'gráfica de actividad por día (SVG)')
    chk(pg.locator('#gDias svg rect').count() >= 1, 'barras de encendidos presentes')
    n_donut = pg.locator('#gTipos svg circle, #gVersiones svg circle').count()
    chk(n_donut >= 3, f'donuts de familias y versiones ({n_donut} segmentos)')
    chk(pg.locator('#tJugadores tbody tr').count() >= 1, 'tabla de jugadores con filas')
    chk(pg.locator('#timeline .ev').count() >= 1, 'timeline con acontecimientos')
    texto = pg.locator('#timeline').inner_text()
    chk('hace' in texto or 'ahora mismo' in texto, 'timeline con tiempos legibles')
    chk('hace' in pg.locator('#tJugadores').inner_text(), 'jugadores con "visto hace…"')
    chk(len(errores) == 0, f'0 pageerrors ({len(errores)}): {errores[:2]}')

    # 4 · captura para revisión visual
    pg.screenshot(path='/home/z/my-project/scripts/_dashboard_r53.png', full_page=True)
    print('  · captura: scripts/_dashboard_r53.png')
    b.close()

httpd.shutdown()
print('QA DASHBOARD r53: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
