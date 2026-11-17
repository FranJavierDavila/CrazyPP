#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r70_fumo2.py — humo de las páginas PROFUNDAS nuevas (r70): champuno,
carreradiv, sala multijugador y prompts, con capturas."""
import base64
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

URL = 'http://127.0.0.1:3672/game.html'

JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  if (!G) { out.sinJuego = true; return out; }
  if (!G.menuOpen) G.toggleMenu();
  await dorme(300);
  const cap = async (key) => {
    G.drawMenu(); await dorme(140);
    out[key] = G.menuCanvas.toDataURL('image/png');
  };
  // 1 · DETALLE DE CAMPEONATO (champsel → champuno)
  const lista = G.champs ? G.champs.list() : [];
  out.nChamps = lista.length;
  const clickId = (id) => {
    const i = G.menuRects.findIndex((r) => String(r.id) === id);
    if (i >= 0) G.menuClick(i, 0);
    return i;
  };
  if (lista.length) {
    G.menuPage = 'champs';
    G.drawMenu(); await dorme(60);
    clickId('champsel:' + lista[0].id);
    await dorme(120);
    out.champunoPage = G.menuPage;
    out.champunoLados = G._menuLados.join('');
    out.champunoRects = G.menuRects.length;
    out.champunoTitulo = G.menuRects.length;
    await cap('capChampuno');
    // volver por el ATRÁS de la concha
    const atras = G.menuRects.find((r) => r.id === 'page:champs');
    out.champunoAtrasOk = !!atras;
  }
  // 2 · DIVISIÓN DE CARRERA (carrera:sel → carreradiv)
  G.menuPage = 'carrera';
  G.drawMenu(); await dorme(80);
  const divRect = G.menuRects.find((r) => String(r.id).indexOf('carrera:sel:') === 0);
  if (divRect) {
    clickId(String(divRect.id));
    await dorme(120);
    out.carreradivPage = G.menuPage;
    out.carreradivLados = G._menuLados.join('');
    out.carreradivRects = G.menuRects.length;
    await cap('capCarreradiv');
  }
  // 3 · SALA MULTIJUGADOR (mjnorm → panel crear/unirse en la C)
  G.menuPage = 'multi';
  G._mjMode = null;
  G.drawMenu(); await dorme(60);
  clickId('mjnorm');
  await dorme(120);
  out.multiElegirPage = G.menuPage;
  out.multiRects = G.menuRects.length;
  out.multiIds = G.menuRects.map((r) => String(r.id)).join('|');
  await cap('capMultiSala');
  // 4 · prompt de salida (C única)
  G.menuPage = 'salirask';
  G.drawMenu(); await dorme(120);
  out.saliraskLados = G._menuLados.join('');
  await cap('capSalirask');
  return out;
}"""

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def main():
    global ok, fails
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3672', '--bind', '127.0.0.1'],
        cwd='/home/z/my-project/upload/public',
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        errores = []
        page.on('pageerror', lambda e: errores.append(str(e)[:300]))
        page.goto(URL)
        page.wait_for_function('!!window.__PP_GAME', timeout=45000)
        page.wait_for_timeout(1200)
        rt = page.evaluate(JS)
        for key, name in [('capChampuno', 'r70_champuno.png'),
                          ('capCarreradiv', 'r70_carreradiv.png'),
                          ('capMultiSala', 'r70_multisala.png'),
                          ('capSalirask', 'r70_salirask.png')]:
            if rt.get(key):
                raw = base64.b64decode(rt[key].split(',', 1)[1])
                open('/home/z/my-project/download/' + name, 'wb').write(raw)
        chk(not rt.get('sinJuego'), 'juego presente')
        print('   champs:', rt.get('nChamps'))
        if rt.get('champunoPage') is not None:
            chk(rt.get('champunoPage') == 'champuno', 'champsel abre champuno')
            chk(rt.get('champunoLados') == 'C', 'champuno en panela C')
            chk(rt.get('champunoRects', 0) >= 3, 'champuno con botones')
            chk(rt.get('champunoAtrasOk'), 'ATRÁS de la concha presente')
        if rt.get('carreradivPage') is not None:
            chk(rt.get('carreradivPage') == 'carreradiv', 'sel abre carreradiv')
            chk(rt.get('carreradivLados') == 'C', 'carreradiv en panela C')
        chk('net:host' in (rt.get('multiIds') or ''), 'sala: botón CREAR en la C')
        chk('net:join' in (rt.get('multiIds') or ''), 'sala: botón UNIRSE en la C')
        chk('mjsel' in (rt.get('multiIds') or ''), 'sala: volver a modos')
        chk(rt.get('saliraskLados') == 'C', 'prompt de salida en panela C')
        chk(not errores, 'sin pageerrors' +
            ('' if not errores else ' → ' + str(errores[:2])))
        if errores:
            print('   errores:', errores[:3])
        browser.close()
    server.terminate()
    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
