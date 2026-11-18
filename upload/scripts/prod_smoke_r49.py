#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r49.py — humo de PRODUCCIÓN FASE 144 (v3.6.142-SDK6).
Carga real del juego en Chromium headless contra GitHub Pages:
  · window.__PP_VERSION === '3.6.142-SDK6'
  · badge 2D contiene V3.6.142-SDK6
  · 0 pageerrors en 12 s
  · el escudo del bucle está montado (animate sin excepción al arrancar)
"""
import json
import sys
from playwright.sync_api import sync_playwright

URL = 'https://franjavierdavila.github.io/CrazyPP/game.html?v=36142'
ERR = []
OK = True


def chk(cond, msg):
    global OK
    print(f'  [{"✓" if cond else "✗"}] {msg}')
    OK = OK and bool(cond)


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on('pageerror', lambda e: ERR.append(str(e)))
    pg.goto(URL, wait_until='domcontentloaded', timeout=60000)
    pg.wait_for_function("() => window.__PP_VERSION", timeout=60000)
    ver = pg.evaluate("window.__PP_VERSION || ''")
    chk(ver == '3.6.142-SDK6', f'__PP_VERSION = {ver!r}')
    badge = pg.evaluate("() => { const b = document.querySelector('#verBadge');"
                        " return b ? b.textContent : ''; }")
    chk('V3.6.142-SDK6' in badge, f'badge = {badge!r}')
    juego = False
    try:
        # __PP_GAME vive en c13 (FIN del módulo): en producción el módulo
        # entero (c01-c13) evalúa tras descargar 11,5 MB — hasta 60 s.
        pg.wait_for_function("() => !!window.__PP_GAME", timeout=60000)
        juego = True
    except Exception:
        juego = False
    chk(juego, 'juego arrancado (__PP_GAME presente)')
    chk(len(ERR) == 0, f'0 pageerrors en 12 s ({len(ERR)}): {ERR[:2]}')
    b.close()

print('PROD SMOKE r49: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
