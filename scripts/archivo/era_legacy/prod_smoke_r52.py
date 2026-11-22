#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prod_smoke_r52.py — humo de PRODUCCIÓN FASE 146 (v3.6.144-SDK6).
Carga real del juego en Chromium headless contra GitHub Pages:
  · window.__PP_VERSION === '3.6.144-SDK6'
  · badge 2D contiene V3.6.144-SDK6
  · juego arrancado (__PP_GAME presente)
  · PRECALENTAMIENTO ARCANO: la caché _arconoIconos nace llena
    (una Image por poder del registro PODERES_PALA) — el fix de la fase
    es observable en producción, no sólo en el fuente
  · 0 pageerrors
"""
import sys
from playwright.sync_api import sync_playwright

URL = 'https://franjavierdavila.github.io/CrazyPP/game.html?v=3.6.144-SDK6'
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
    chk(ver == '3.6.144-SDK6', f'__PP_VERSION = {ver!r}')
    badge = pg.evaluate("() => { const b = document.querySelector('#verBadge');"
                        " return b ? b.textContent : ''; }")
    chk('V3.6.144-SDK6' in badge, f'badge = {badge!r}')
    juego = False
    try:
        # __PP_GAME vive en c13 (FIN del módulo): en producción el módulo
        # entero (c01-c13) evalúa tras descargar 11,5 MB — hasta 60 s.
        pg.wait_for_function("() => !!window.__PP_GAME", timeout=60000)
        juego = True
    except Exception:
        juego = False
    chk(juego, 'juego arrancado (__PP_GAME presente)')
    n_icons = -1
    if juego:
        try:
            n_icons = pg.evaluate(
                "() => { const G = window.__PP_GAME;"
                " return (G && G._arconoIconos)"
                " ? Object.keys(G._arconoIconos).length : -1; }")
        except Exception:
            n_icons = -1
    chk(n_icons >= 10,
        f'precalentamiento arcano: _arconoIconos = {n_icons} (≥10)')
    chk(len(ERR) == 0, f'0 pageerrors ({len(ERR)}): {ERR[:2]}')
    b.close()

print('PROD SMOKE r52: ' + ('TODO OK' if OK else 'FALLO'))
sys.exit(0 if OK else 1)
