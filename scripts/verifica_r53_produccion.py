#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verifica_r53_produccion.py — el dashboard de telemetría en Pages (FASE 147).
  1 · telemetria.html servido lleva los marcadores de la versión nueva
  2 · Playwright contra la URL REAL: clave por localStorage, dashboard
      visible, 6 KPIs, donuts SVG, tabla de jugadores, 0 pageerrors
La clave nunca viaja en la URL ni se imprime.
"""
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'https://franjavierdavila.github.io/CrazyPP/telemetria.html'
CLAVE = open('/home/z/my-project/upload/scripts/worker-tele/.clave-produccion',
             encoding='utf-8').read().strip()
OK = True


def chk(cond, msg):
    global OK
    print(f'  [{"OK" if cond else "FALLO"}] {msg}')
    OK = OK and bool(cond)


req = urllib.request.Request(BASE + '?v=' + str(int(time.time())),
                             headers={'User-Agent': 'Mozilla/5.0'})
html = ''
print('· sondeando el builder de Pages (hasta 6 min)…')
for _ in range(36):
    try:
        html = urllib.request.urlopen(req, timeout=60).read().decode('utf-8', 'replace')
        if 'El cuadro de mando de' in html:
            break
    except Exception:
        pass
    time.sleep(10)
chk('El cuadro de mando de' in html, 'panel nuevo servido (portada «cuadro de mando»)')
chk('svgArea' in html and 'svgDonut' in html, 'gráficas SVG propias presentes')
chk('pp_tele_clave' in html, 'contrato de clave en localStorage intacto')

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1360, 'height': 900})
    errores = []
    pg.on('pageerror', lambda e: errores.append(str(e)))
    pg.goto(BASE, wait_until='domcontentloaded', timeout=60000)
    pg.evaluate("k => localStorage.setItem('pp_tele_clave', k)", CLAVE)
    pg.reload(wait_until='domcontentloaded')
    try:
        pg.wait_for_selector('#contenido:not(.oculto)', timeout=30000)
        datos = True
    except Exception:
        datos = False
    chk(datos, 'dashboard visible en producción')
    if datos:
        pg.wait_for_timeout(1500)
        chk(pg.locator('.kpi').count() == 6,
            f'KPIs ({pg.locator(".kpi").count()} de 6)')
        chk(pg.locator('#gDias svg').count() == 1, 'gráfica de actividad por día')
        chk(pg.locator('#tJugadores tbody tr').count() >= 1, 'tabla de jugadores')
        chk(pg.locator('#timeline .ev').count() >= 1, 'timeline con eventos')
    chk(len(errores) == 0, f'0 pageerrors ({len(errores)}): {errores[:2]}')
    pg.screenshot(path='/home/z/my-project/scripts/_dashboard_r53_prod.png',
                  full_page=True)
    b.close()

print('VERIFICACIÓN PRODUCCIÓN r53: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
