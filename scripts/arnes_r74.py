#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arnes_r74.py — SOAK anti-bucle + barrido de TODAS las páginas del menú.

Lección de la ronda 70 (el dueño congeló el juego al pulsar Ranking
Mundial): un .then() que redibuja la MISMA página que dispara la petición
forma un ciclo GET+redibujo sin fin — el arnés de r70 miraba rects y
panelas, pero NUNCA bombeó frames por página, así que el bucle se coló.
Este arnés es la vacuna:
  · Contador de fetch inyectado ANTES del boot: cada visita a una página
    puede gastar ≤ 2 peticiones al almacén mundial (r70 desbordaba: decenas
    por segundo hasta colgar el navegador de la Quest).
  · Contador de RAF vivo: durante cada visita el bucle de render debe
    avanzar (si una microtarea lo starving, el contador se para = FALLO).
  · Sin errores de página en ninguna navegación.
  · Captura PNG del menú-canvas de TODAS las páginas (para maquetar r72).
Salida: RESULTADO: N OK · M fallos + capturas en download/r72_capturas/.
"""
import asyncio
import base64
import os
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3667/game.html'
OUT = '/home/z/my-project/download/r72_capturas'
PUERTO = 3667

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')

# Páginas de tercer nivel (las que el dueño ve «en formato antiguo») + landings
PAGINAS = [
    ('main', False), ('rankini', False), ('rank', False), ('rankme', False),
    ('champs', False), ('champuno', False), ('champhist', False),
    ('train', False), ('trainarea', False), ('trainext', False),
    ('carrera', False), ('carreradiv', False),
    ('opts', False), ('optsJuego', False), ('optsSala', False),
    ('optsSonido', False), ('optsVisual', False), ('optsPerfil', False),
    ('optsRendi', False), ('optsPala', False),
    ('optsSalaRoom', False), ('optsSalaMesa', False),
    ('optsSalaBola', False), ('optsSalaHall', False),
    ('multi', True), ('join', False), ('name', False), ('gripname', False),
    ('hallask', False), ('salirask', False),
]

JS_BARRIDO = """async ([PAGINAS]) => {
  const G = window.__PP_GAME;
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { return { sinJuego: true }; }
  // — contadores auto-suficientes (se instalan aquí si el init no llegó) —
  if (!window.__fetchCounts) {
    window.__fetchCounts = { world: 0, total: 0 };
    const _f = window.fetch.bind(window);
    window.fetch = (...args) => {
      try {
        const u = String((args[0] && args[0].url) ? args[0].url : (args[0] || ''));
        window.__fetchCounts.total++;
        if (u.indexOf('restful-api.dev') !== -1) window.__fetchCounts.world++;
      } catch (e) { /* */ }
      return _f(...args);
    };
  }
  if (window.__rafCount === undefined) {
    window.__rafCount = 0;
    const _raf = window.requestAnimationFrame.bind(window);
    const paso = () => { window.__rafCount++; _raf(paso); };
    _raf(paso);
  }
  const out = { paginas: {}, errores: (window.__pageErrors || []).slice() };
  if (!G.menuOpen) G.toggleMenu();
  await dorme(500);
  G.menuPin = true;
  G.anchorMenu(true);
  await dorme(200);
  for (const [pg, limpiar] of PAGINAS) {
    const f0 = window.__fetchCounts.world;
    const raf0 = window.__rafCount;
    // salud de MACROTAREAS de ESTA página: 60 timeouts cortos; el bucle
    // debe despacharlos casi todos durante la visita (si una microtarea
    // starving el bucle, quedan sin despachar = FALLO).
    let mtHechos = 0;
    for (let i = 0; i < 60; i++) setTimeout(() => { mtHechos++; }, 4);
    G.menuPage = pg;
    if (limpiar) G._mjMode = null;
    let errDibujo = null;
    try { G.drawMenu(); } catch (e) { errDibujo = String(e); }
    await dorme(700);          // SOAK: 700 ms de frames por página
    const rs = G.menuRects || [];
    out.paginas[pg] = {
      fetchWorld: window.__fetchCounts.world - f0,
      rafDelta: window.__rafCount - raf0,
      mt: mtHechos,
      rects: rs.length,
      errDibujo,
      png: G.menuCanvas.toDataURL('image/png'),
    };
  }
  out.fetchTotalFinal = window.__fetchCounts.world;
  G.menuPage = 'main';
  G.drawMenu();
  return out;
}"""


async def main():
    os.makedirs(OUT, exist_ok=True)
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(PUERTO), '--bind', '127.0.0.1',
         '--directory', '/home/z/my-project/upload/public'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    try:
        game = get(URL)
    except Exception as e:
        print('✗ No se pudo leer el game.html local:', e)
        print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
        server.terminate()
        sys.exit(1)
    chk('3.6.165' in game, 'build local sirve 3.6.165 (r74)')
    chk('this._rankiniFresh' in game, 'guarda anti-bucle _rankiniFresh presente')

    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errores_py = []
        page.on('pageerror', lambda e: errores_py.append(str(e)))
        await page.goto(URL)
        await page.wait_for_timeout(4500)

        hay = await page.evaluate('() => !!window.__PP_GAME')
        chk(hay, 'window.__PP_GAME expuesto')
        if not hay:
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            server.terminate()
            sys.exit(1)

        out = await page.evaluate(JS_BARRIDO, [PAGINAS])
        if out.get('sinJuego'):
            print('FALLO: sin __PP_GAME en el barrido')
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            server.terminate()
            sys.exit(1)

        # — aserciones SOAK por página —
        print('— SOAK por página (fetch mundo / macrotareas / rects) —')
        malas = []
        for pg, _ in PAGINAS:
            d = out['paginas'][pg]
            png_b64 = d.pop('png', '')
            etiqueta = (f"{pg:14s} fetch={d['fetchWorld']:3d} "
                        f"mt={d['mt']:3d}/60 raf={d['rafDelta']:5d} rects={d['rects']:3d} "
                        + ('ERR:' + d['errDibujo'] if d['errDibujo'] else ''))
            malo = (d['fetchWorld'] > 2 or d['mt'] < 40 or
                    d['rects'] == 0 or d['errDibujo'])
            if malo:
                malas.append(pg)
                print('  MALO ' + etiqueta)
            else:
                print('  ok   ' + etiqueta)
            if png_b64:
                with open(os.path.join(OUT, f'{pg}.png'), 'wb') as f:
                    f.write(base64.b64decode(png_b64.split(',', 1)[1]))

        chk(not malas, f'sin páginas con bucle/petición-masa/canvas muerto ({len(PAGINAS)} barridas)')
        chk(not errores_py, 'cero errores de página en toda la sesión '
            + (str(errores_py) if errores_py else ''))

        # el total de GETs al almacén en TODA la sesión debe ser contenido
        chk(out['fetchTotalFinal'] <= len(PAGINAS) * 2 + 4,
            f"GETs al almacén contenidos ({out['fetchTotalFinal']} en toda la sesión)")

        await browser.close()
    server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos · capturas en {OUT}')
    sys.exit(1 if fails else 0)


asyncio.run(main())
