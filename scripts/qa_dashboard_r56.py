#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_dashboard_r56.py — prueba del panel de telemetría ampliado (FASE 150).
Extiende qa_dashboard_r53.py: mismo arnés (servidor local + Chromium headless
+ clave por localStorage, jamás en la URL) y añade los bloques nuevos:
  · sección «Rankings por jugador» con 4 pestañas desde ?rank=1
  · ficha individual al pulsar una fila de jugadores (drill-down ?eventos=500&sid=)
  · ficha individual al pulsar una fila de rankings (por pid)
  · cambio de pestaña y cierre de ficha
  · 0 pageerrors
"""
import http.server
import socketserver
import sys
import threading

from playwright.sync_api import sync_playwright

RAIZ = '/home/z/my-project/upload/public'
PUERTO = 3118
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


socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.ThreadingTCPServer(('127.0.0.1', PUERTO), Silencioso)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{PUERTO}/telemetria.html'

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1360, 'height': 900})
    errores = []
    pg.on('pageerror', lambda e: errores.append(str(e)))

    # 1 · inyecta clave y carga
    pg.goto(URL, wait_until='domcontentloaded', timeout=30000)
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
    pg.wait_for_timeout(1500)

    # 2 · bloque clásico r53 sigue intacto
    n_kpi = pg.locator('.kpi').count()
    chk(n_kpi == 6, f'KPIs pintados ({n_kpi} de 6)')
    chk(pg.locator('#gDias svg').count() == 1, 'gráfica de actividad por día (SVG)')
    chk(pg.locator('#tJugadores tbody tr').count() >= 1, 'tabla de jugadores con filas')

    # 3 · NUEVO · rankings por jugador
    n_tabs = pg.locator('#tabsRank button').count()
    chk(n_tabs == 4, f'pestañas de rankings ({n_tabs} de 4)')
    n_rank = pg.locator('#tRank tbody tr').count()
    chk(n_rank >= 1, f'tabla de ranking con filas ({n_rank})')
    if n_tabs == 4:
        pg.locator('#tabsRank button').nth(1).click()
        pg.wait_for_timeout(250)
        chk(pg.locator('#tabsRank button.act').inner_text().strip() == 'Victorias',
            'cambio de pestaña a «Victorias»')

    # 4 · NUEVO · ficha por sesión (tabla de jugadores)
    if pg.locator('#tJugadores tbody tr[data-sid]').count() >= 1:
        pg.locator('#tJugadores tbody tr[data-sid]').first.click()
        pg.wait_for_selector('#ficha:not(.oculto)', timeout=20000)
        pg.wait_for_timeout(1500)
        cuerpo = pg.locator('#fichaCuerpo').inner_text()
        chk('ficha' in pg.locator('#fichaCab').inner_text().lower(), 'ficha abierta con cabecera')
        chk('acciones registradas' in cuerpo.lower(), 'ficha con KPIs de actividad')
        chk('últimas acciones' in cuerpo.lower(), 'ficha con últimas acciones')
        pg.locator('#ficha [data-cerrar]').click()
        pg.wait_for_timeout(250)
        chk(pg.locator('#ficha.oculto').count() == 1, 'cierre de ficha')
    else:
        chk(False, 'no hay filas de jugadores para abrir ficha')

    # 5 · NUEVO · ficha por jugador (ranking)
    if pg.locator('#tRank tbody tr[data-pid]').count() >= 1:
        pg.locator('#tRank tbody tr[data-pid]').first.click()
        pg.wait_for_selector('#ficha:not(.oculto)', timeout=10000)
        cuerpo = pg.locator('#fichaCuerpo').inner_text()
        chk('elo de temporada' in cuerpo.lower(), 'ficha de ranking con Elo/Victorias/Logros')
        pg.locator('#ficha [data-cerrar]').click()
    else:
        print('  · (sin jugadores con perfil aún: ficha de ranking sin probar)')

    chk(len(errores) == 0, f'0 pageerrors ({len(errores)}): {errores[:2]}')

    # 6 · captura para revisión visual
    pg.screenshot(path='/home/z/my-project/scripts/_dashboard_r56.png', full_page=True)
    print('  · captura: scripts/_dashboard_r56.png')
    b.close()

httpd.shutdown()
print('QA DASHBOARD r56: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
