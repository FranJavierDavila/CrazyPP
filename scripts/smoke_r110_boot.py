#!/usr/bin/env python3
"""smoke_r110_boot.py — arranque del bundle r110 (v3.6.208) en Chromium real.
Sirve public/ en local, carga game.html, espera al arranque completo y aserta:
· sin errores de consola ni excepciones de página (las referencias nuevas —
  pendientes(), FIN_PLAZO — se evalúan al cargar el módulo),
· el badge de versión muestra 3.6.208,
· el canvas WebGL del juego llega a existir.
RC 0 = verde."""
import http.server
import socketserver
import sys
import threading
from pathlib import Path

RAIZ = Path('/home/z/my-project/public')
PUERTO = 3010


class Silencioso(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Reutilizable(socketserver.TCPServer):
    allow_reuse_address = True   # relanza la smoke sin esperar TIME_WAIT


def main():
    handler = lambda *a, **k: Silencioso(*a, directory=str(RAIZ), **k)
    with Reutilizable(('127.0.0.1', PUERTO), handler) as httpd:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()

        from playwright.sync_api import sync_playwright
        errores, paginas = [], []
        with sync_playwright() as pw:
            nav = pw.chromium.launch(args=[
                '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
                '--no-sandbox'])
            pg = nav.new_page(viewport={'width': 1280, 'height': 720})
            # Los fallos de RED (404/501 de /api/…, sw) son del entorno de
            # prueba — en local no hay rutas Next.js ni worker. Solo cuentan
            # como error los fallos de JS en consola (sintaxis/referencia).
            pg.on('console', lambda m: errores.append(m.text)
                  if m.type == 'error' and 'Failed to load resource' not in m.text
                  else None)
            pg.on('pageerror', lambda e: paginas.append(str(e)))
            pg.goto(f'http://127.0.0.1:{PUERTO}/game.html', wait_until='load', timeout=30000)
            pg.wait_for_timeout(7000)

            badge = pg.evaluate("() => { const b = document.getElementById('verBadge'); return b ? b.textContent.trim() : '(sin badge)'; }")
            canvas = pg.evaluate("() => document.querySelectorAll('canvas').length")
            cripto_en_bundle = pg.evaluate("() => typeof window !== 'undefined'")
            nav.close()

        httpd.shutdown()

    ok = True
    print(f'· badge: {badge}')
    ok &= ('3.6.208' in badge)
    print(f'· canvas en la página: {canvas}')
    ok &= (canvas >= 1)
    print(f'· errores de consola: {len(errores)}')
    for e in errores[:6]:
        print('   -', e[:150])
    ok &= (len(errores) == 0)
    print(f'· excepciones de página: {len(paginas)}')
    for e in paginas[:6]:
        print('   -', e[:150])
    ok &= (len(paginas) == 0)
    print(f'· página viva: {cripto_en_bundle}')
    print('SMOKE r110: ' + ('VERDE — el arranque es limpio' if ok else 'ROJA'))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
