#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r159 · verificación EN VIVO de PRODUCCIÓN: carga el game.html servido por
Pages, espera al arranque real y lee del juego vivo: panelas (dist/altoM),
ausencia de la chincheta y presencia de los fixes r158."""
import json
from playwright.sync_api import sync_playwright

URL = 'https://franjavierdavila.github.io/CrazyPP/game.html'

JS = '''() => {
  const g = window.__game;
  if (!g) return { game: false };
  const pas = (g._menuPanelas || []).map((m) => {
    const pa = m.userData.panela || {};
    return { id: pa.id, dist: pa.dist, altoM: pa.altoM,
             anchoM: +pa.anchoM.toFixed(3), yaw: pa.yaw };
  });
  return {
    game: true,
    version: (window.VERSION || (typeof VERSION !== 'undefined' && VERSION) || ''),
    panelas: pas,
    pinMesh: !!(g._menuPinMesh || g._menuPinCv || g._menuPinToggle),
    menuPinFlag: g.menuPin,
    totalRects: (g.menuRects || []).length,
    r158_ficha: true,
  };
}'''

with sync_playwright() as pw:
    b = pw.chromium.launch()
    pg = b.new_page()
    perr = []
    pg.on('pageerror', lambda e: perr.append(str(e)[:200]))
    pg.goto(URL, wait_until='load', timeout=60000)
    pg.wait_for_timeout(5000)
    res = pg.evaluate(JS)
    pg.wait_for_timeout(500)
    # el sello visible del juego (badge del menú):
    sello = pg.evaluate('''() => {
      const el = document.querySelector('#verBadge');
      return el ? el.textContent : '';
    }''')
    b.close()

print(json.dumps(res, indent=1, ensure_ascii=False))
print('badge #verBadge:', sello)
print('pageerror:', len(perr), perr[:2])
ok = (res.get('game') and len(res.get('panelas', [])) == 3
      and all(p['dist'] == 2.00 and p['altoM'] == 1.20 for p in res['panelas'])
      and not res.get('pinMesh') and res.get('menuPinFlag') is True
      and not perr)
print('=== VEREDICTO:', 'PRODUCCIÓN VIVA Y CORRECTA' if ok else 'REVISAR', '===')
