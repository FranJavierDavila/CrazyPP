#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""err_boot_r83.py — captura el error de arranque del build v3.6.174."""
import subprocess
import sys
import time

RAIZ = '/home/z/my-project'
server = subprocess.Popen(
    [sys.executable, '-m', 'http.server', '3672', '--bind', '127.0.0.1',
     '--directory', RAIZ + '/public'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1.0)
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        pg = b.new_page(viewport={'width': 960, 'height': 540})
        pg.add_init_script("""
          window.__errs = [];
          window.addEventListener('error', (e) => {
            window.__errs.push({ msg: String(e.message), line: e.lineno,
              col: e.colno, src: e.filename || 'inline' });
          }, true);
        """)
        errs = []
        cons = []
        pg.on('pageerror', lambda e: errs.append('PAGEERROR: ' + str(e)))
        pg.on('console', lambda m: cons.append(m.type + ': ' + m.text)
              if m.type in ('error', 'warning') else None)
        pg.goto('http://127.0.0.1:3672/game.html', wait_until='domcontentloaded',
                timeout=45000)
        time.sleep(9)
        tiene = pg.evaluate('() => !!window.__PP_GAME')
        print('__PP_GAME:', tiene)
        try:
            info = pg.evaluate('() => window.__errs || []')
            print('--- errores con ubicación:')
            for e in info[:6]:
                print(' ', e)
        except Exception as e2:
            print('eval errs:', e2)
        print('--- pageerrors (%d):' % len(errs))
        for e in errs[:6]:
            print(' ', e[:500])
        print('--- console error/warning (%d):' % len(cons))
        for e in cons[:8]:
            print(' ', e[:300])
        pg.close()
        b.close()
finally:
    server.terminate()
