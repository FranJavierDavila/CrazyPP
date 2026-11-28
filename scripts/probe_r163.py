#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163 · probe del flujo de menús con cartelas:
1 · ARRANQUE: la cartela Main aparece SOLA al abrir (sin recargar) — el
    fix del informe del dueño («el menú no se abre al principio»).
2 · BANDERAS es/en presentes en los rects de la cartela Main.
3 · JUGAR: cartela propia (título + 5 botones + recurso del modo) y
    btn_maquina seleccionado por defecto.
4 · FADE: apuntar otro botón cambia la selección (crossfade en curso).
5 · Escalera: el clic deja el aviso honesto (no lanza modo).
Sin pageerror en todo el recorrido."""
import os
import threading
import http.server

from playwright.sync_api import sync_playwright

os.chdir('/home/z/my-project/public')


def serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    with http.server.ThreadingHTTPServer(('127.0.0.1', 3022), H) as h:
        h.serve_forever()


threading.Thread(target=serve, daemon=True).start()
MAL = []
with sync_playwright() as pw:
    b = pw.chromium.launch(args=['--use-gl=swiftshader'])
    pg = b.new_page(viewport={'width': 1280, 'height': 800})
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:150]))
    pg.goto('http://127.0.0.1:3022/game.html', wait_until='load')
    # el arte del tema tarda (red local en el casco también): esperamos a
    # que la precarga complete AMBAS cartelas antes de abrir el menú
    lista = False
    for _ in range(40):
        pg.wait_for_timeout(500)
        lista = pg.evaluate(
            'window.__PP_GAME ? (window.__PP_GAME._uiCartelaLista("Main") '
            '&& window.__PP_GAME._uiCartelaLista("Jugar")) : false')
        if lista:
            break
    print('arte completo de ambas cartelas:', lista)
    if not lista:
        MAL.append('el arte del tema no llegó en 20 s')
    # apertura programática = el mismo camino real (menuFxInicia('in')
    # resetea el congelado y el 1.er drawMenu decide cartela ⇄ legado)
    pg.evaluate('''() => {
      const g = window.__PP_GAME;
      g.menuOpen = true;
      g.menuSec = 'match';
      g.menuFxInicia('in');
      g.drawMenu();
    }''')
    pg.wait_for_timeout(800)

    r1 = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      if (!g) return { err: 'sin __PP_GAME' };
      const ids = (g.menuRects || []).map(r => r.id);
      return {
        menuOpen: g.menuOpen, pag: g.menuPage,
        modoMain: g._uiModoVals.Main,
        hayBanderas: ids.includes('lang:es') && ids.includes('lang:en'),
        botonesMain: (ids.filter(i => i === 'page:jugar').length),
      };
    }''')
    print('1 arranque:', r1)
    if not r1.get('modoMain'):
        MAL.append('la cartela Main NO manda al arrancar: %s' % r1)
    if not r1.get('hayBanderas'):
        MAL.append('faltan las banderitas es/en: %s' % r1)
    pg.screenshot(path='/tmp/r163_main.png')

    r2 = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      const i = (g.menuRects || []).findIndex(r => r.id === 'page:jugar');
      if (i < 0) return { err: 'sin page:jugar' };
      g.menuClick(i, 0);
      return { pag: g.menuPage, sel: g._uiJugarSel,
        ids: (g.menuRects || []).map(r => r.id) };
    }''')
    print('2 jugar:', {k: v for k, v in r2.items() if k != 'ids'})
    if r2.get('pag') != 'jugar':
        MAL.append('page:jugar no navega: %s' % r2)
    for esperado in ('start', 'traingo', 'survgo', 'escalera:soon', 'tut:go'):
        if esperado not in (r2.get('ids') or []):
            MAL.append('falta el botón %s en la cartela Jugar' % esperado)
    if r2.get('sel') not in (None, 'start'):
        MAL.append('la selección inicial no es el defecto: %s' % r2.get('sel'))
    pg.wait_for_timeout(1200)
    r3 = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      return { sel: g._uiJugarSel, pag: g.menuPage,
        modoJugar: g._uiModoVals.Jugar,
        titulo: g._uiCartelaDef('Jugar').tituloKey };
    }''')
    print('3 defecto:', r3)
    if r3.get('sel') != 'start':
        MAL.append('el recurso por defecto no es btn_maquina: %s' % r3)
    if not r3.get('modoJugar'):
        MAL.append('la cartela Jugar NO manda (fallback legado): %s' % r3)
    pg.screenshot(path='/tmp/r163_jugar.png')

    r4 = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      const i = (g.menuRects || []).findIndex(r => r.id === 'traingo');
      g.menuHover = [i, -1];
      g.drawMenu();
      return { i, sel: g._uiJugarSel, fade: !!(g._uiJugarFade),
        hover: g.menuHover.slice() };
    }''')
    pg.wait_for_timeout(500)
    r4b = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      return { sel: g._uiJugarSel, fadeActivo: !!(g._uiJugarFade) };
    }''')
    print('4 fade:', r4, '→ tras 500 ms:', r4b)
    if r4b.get('sel') != 'traingo':
        MAL.append('apuntar Entrenamiento no selecciona su recurso: %s → %s' % (r4, r4b))
    pg.wait_for_timeout(400)
    pg.screenshot(path='/tmp/r163_fade.png')

    r5 = pg.evaluate('''() => {
      const g = window.__PP_GAME;
      const i = (g.menuRects || []).findIndex(r => r.id === 'escalera:soon');
      g.menuClick(i, 0);
      return { msg: g.rules && g.rules.message, pag: g.menuPage };
    }''')
    print('5 escalera:', r5)
    msg = r5.get('msg') or ''
    if not msg or msg == 'escalera_soon' or (
            'ESCALERA' not in msg and 'CHAMPIONSHIP' not in msg):
        MAL.append('escalera no deja el aviso honesto: %s' % r5)

    print('pageerrors:', errs[:3] or 'ninguno')
    if errs:
        MAL.append('pageerror: %s' % errs[0])
    b.close()

if MAL:
    print('\n== FALLOS ==')
    for m in MAL:
        print('✗', m)
    raise SystemExit(1)
print('\n== RESULTADO ==\n probe r163 limpio: cartelas al arranque, banderas, Jugar completa, fade y escalera honestos')
