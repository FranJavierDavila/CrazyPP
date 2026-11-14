#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_vestibulo_r69.py — QA FASE 163 · CORRECCIÓN DEL ARCO (r69).

Informe del dueño verificado:
  1 · «los tres bloques no se pueden pisar o superponer, deben ir unos
      seguidos a los otros» — panelas tangentes y consecutivas: las tres
      a 1,15 m, yaw = γC + γL + 0,8°, ranura ~1,7 cm (chequeado con las
      fórmulas, no a ojo).
  2 · «estás colocando mal el menú» — el grupo vuelve a ir DELANTE de la
      cara mirando a la cara: la panela central queda a ~1,15 m en la
      dirección de la vista (comprobado en MUNDO, no solo en local).
  3 · ancla: abrir = delante de la mirada y FIJO · sin chincheta SIGUE
      (anchorMenu reposiciona aunque el grupo esté desplazado) · con
      chincheta CONGELA donde esté aunque se la desplace.
  4 · limpieza: títulos legados duplicados fuera, tooltips espacio-
      conscientes y barrido de TODAS las páginas (rects dentro del
      lienzo virtual 3696×1400).

Salida: RESULTADO: N OK · M fallos + capturas (main · AJUSTES>Sala · nombre)."""
import asyncio
import base64
import subprocess
import sys
import time
import urllib.request

from playwright.async_api import async_playwright

URL = 'http://127.0.0.1:3667/game.html'
OUT = '/home/z/my-project/download/'

ok, fails = 0, 0


def chk(cond, label):
    global ok, fails
    print(('  OK  ' if cond else '  FALLO: ') + label)
    ok, fails = ok + (1 if cond else 0), fails + (0 if cond else 1)


def get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')


JS = """async () => {
  const G = window.__PP_GAME;
  const out = {};
  if (!G) { out.sinJuego = true; return out; }
  const dorme = (ms) => new Promise((r) => setTimeout(r, ms));
  const V3 = G.menuGroup.position.constructor;
  const Q4 = G.menuGroup.quaternion.constructor;

  // — 1 · ARCO SIN PISARSE (fórmulas, no a ojo) —
  const CM = G._menuPanelas.map((m) => m.userData.panela);
  const grads = CM.map((pa) => Math.atan2(pa.anchoM / 2, pa.dist)
    * 180 / Math.PI);
  out.dists = CM.map((pa) => pa.dist);
  out.equi = out.dists.every((d) => Math.abs(d - 1.15) < 0.001);
  const th = Math.abs(CM[0].yaw);
  out.hueco = +(th - grads[0] - grads[1]).toFixed(2);
  out.sinSolape = th - grads[0] >= grads[1] + 0.5;

  // — 2 · COLOCACIÓN EN MUNDO (delante de la mirada a ~1,15 m) —
  if (!G.menuOpen) G.toggleMenu();
  await dorme(450);
  G.menuPin = true;
  G.anchorMenu(true);
  await dorme(120);
  const cp = new V3();
  G.camera.getWorldPosition(cp);
  const q = new Q4();
  G.camera.getWorldQuaternion(q);
  const fwd = new V3(0, 0, -1).applyQuaternion(q);
  const g2c = G.menuGroup.position.clone().sub(cp);
  out.delante = +g2c.dot(fwd).toFixed(3);
  out.distGrp = +g2c.length().toFixed(3);
  out.colocacion = out.delante > 1.05 &&
    Math.abs(out.distGrp - 1.15) < 0.02 &&
    (out.delante / out.distGrp) > 0.9;
  // la panela central SIEMPRE delante: su mundo ≈ posición del grupo
  const pC = G._menuPanelas[1].getWorldPosition(new V3());
  const c2c = pC.clone().sub(cp);
  out.panelaCDelante = +c2c.dot(fwd).toFixed(3);
  out.colocacionC = out.panelaCDelante > 1.10 &&
    Math.abs(c2c.length() - out.panelaCDelante) < 0.02;

  // — 3 · SEMÁNTICA DEL ANCLA —
  const p0 = G.menuGroup.position.clone();
  G.menuGroup.position.set(5, 5, 5);
  G.anchorMenu();                      // con chincheta: NO mueve
  out.congela = G.menuGroup.position.distanceTo(new V3(5, 5, 5)) < 0.001;
  G.menuPin = false;
  G.anchorMenu();                      // sin chincheta: recoloca en la cara
  out.sigue = G.menuGroup.position.distanceTo(p0) < 0.03;
  G.menuPin = true;
  G._menuPinDraw();
  G.anchorMenu(true);
  await dorme(100);

  // — 4 · BARRIDO DE TODAS LAS PÁGINAS (rects en el lienzo virtual) —
  const pags = ['main', 'multi', 'join', 'name', 'gripname', 'rank',
    'rankme', 'champs', 'champhist', 'opts', 'optsJuego', 'optsSala',
    'optsSonido', 'optsVisual', 'optsPerfil', 'optsRendi', 'optsPala',
    'salirask', 'hallask', 'tutask', 'train', 'carrera'];
  out.paginasMalas = [];
  for (const pg of pags) {
    G.menuPage = pg;
    G.menuSec = '';
    G.drawMenu();
    await dorme(30);
    const rs = G.menuRects || [];
    const malas = rs.filter((r) => r.x < -2 || r.y < -2 ||
        r.x + r.w > 3698 || r.y + r.h > 1402).map((r) => r.id);
    if (!rs.length || malas.length) {
      out.paginasMalas.push(pg + (malas.length ? ':' + malas.join(',') : ''));
    }
    if (pg === 'main') out.pngMain = G.menuCanvas.toDataURL('image/png');
    if (pg === 'optsSala') out.pngSala = G.menuCanvas.toDataURL('image/png');
    if (pg === 'name') out.pngName = G.menuCanvas.toDataURL('image/png');
  }
  out.todasLimpias = out.paginasMalas.length === 0;

  // dedup: los títulos legados ya no pintan (la concha manda)
  G.menuPage = 'opts';
  G.drawMenu();
  await dorme(60);
  out.idsOpts = ['page:optsJuego', 'page:optsSala', 'kofi']
    .every((id) => (G.menuRects || []).some((r) => r.id === id));
  G.menuPage = 'main';
  G.drawMenu();
  await dorme(60);
  return out;
}"""


async def main():
    server = subprocess.Popen(
        [sys.executable, '-m', 'http.server', '3667', '--bind', '127.0.0.1',
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

    agujas = [
        ('{ id: \'L\', x: 0, w: 1112, anchoM: 0.66, altoM: 0.95, yaw: 37.8, dist: 1.15 }',
         'panela L 0,66 m a 1,15 m (equidistancia real)'),
        ('{ id: \'C\', x: 1112, w: 1472, anchoM: 0.88, altoM: 0.95, yaw: 0, dist: 1.15 }',
         'panela C 0,88 m a 1,15 m'),
        ('yaw = γC + γL + 0,8°', 'fórmula sin solape documentada'),
        ('anchorMenu(forzar) {', 'anchorMenu con forzar'),
        ('CONVENCIÓN r67 RESTAURADA', 'grupo delante mirando a la cara'),
        ('D_REF - Math.cos(yaw) * pa.dist', 'arco centrado en la cabeza'),
        ('CONFIG_MENUS.arco.yCentro + 0.475 + 0.032, 0.006)',
         'chincheta clicable (z +6 mm)'),
        ('if (!this.menuPin) this.anchorMenu();',
         'sin ancla: sigue siempre'),
        ('this.anchorMenu(true);      // r69: nace delante de la mirada y fijo',
         'apertura: delante de la mirada y fijo'),
        ('this.anchorMenu(true);', 'prompt B y opts rápida con forzar', ),
        ('const ESP = this._menuMap', 'tooltip espacio-consciente'),
        ('ESP.w - wBox / 2 - 14', 'tooltip abrazadera a su lienzo'),
        ("    label(T('tab_multi'), 244, 26)", 'título multi duplicado FUERA', True),
        ("    label(T('join_title'), 240, 26)", 'título join duplicado FUERA', True),
        ("    label(T('name_title'), 240, 26)", 'título name duplicado FUERA', True),
        ("    label(T('pala_gname_title'), 240, 26)", 'título gripname duplicado FUERA', True),
        ("    label(T('sec_rank'), 240, 26)", 'título rank duplicado FUERA', True),
        ("    c.fillText(T('rankme_t'), 512, 312)", 'título rankme duplicado FUERA', True),
        ("    c.fillText(T('carrera_lbl'), 512, 312)", 'título carrera duplicado FUERA', True),
        ("const VERSION = '3.6.160-SDK6'", 'sello a 3.6.160'),
        ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 'r160: regla'),
        ('LA BOLA SIEMPRE VUELVE A TU MANO', 'r65: blindaje del saque'),
    ]
    for item in agujas:
        needle, label = item[0], item[1]
        invertir = len(item) > 2 and item[2] is True
        presente = needle in game
        chk((not presente) if invertir else presente, label)
    n_icons = game.count('data:image/png;base64,')
    chk(n_icons >= 24, f'24+ iconos embebidos (hay {n_icons})')

    errors = []
    rt = {}
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=[
            '--use-gl=swiftshader', '--enable-unsafe-swiftshader',
            '--autoplay-policy=no-user-gesture-required',
        ])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on('pageerror', lambda e: errors.append(str(e)))
        try:
            await page.goto(URL, wait_until='domcontentloaded', timeout=90000)
            await page.wait_for_timeout(9000)
            rt = await page.evaluate(JS)
        except Exception as e:
            print('✗ El juego no arrancó en headless:', e)
            print(f'RESULTADO: {ok} OK · {fails + 1} fallos')
            await browser.close()
            server.terminate()
            sys.exit(1)
        await browser.close()
    server.terminate()

    chk(not rt.get('sinJuego'), 'window.__PP_GAME presente')
    chk(rt.get('equi') is True,
        'las tres panelas a 1,15 m (equidistancia real)')
    chk(rt.get('sinSolape') is True,
        f'sin solape: ranura angular {rt.get("hueco")}° (≥0,5°)')
    chk(rt.get('colocacion') is True,
        f'grupo DELANTE de la mirada ({rt.get("delante")} m de proyección'
        f' · dist {rt.get("distGrp")} m)')
    chk(rt.get('colocacionC') is True,
        f'panela central delante a {rt.get("panelaCDelante")} m')
    chk(rt.get('congela') is True,
        'con chincheta CONGELA donde esté (aunque se la desplace)')
    chk(rt.get('sigue') is True,
        'sin chincheta SIGUE (recoloca en la cara al re-anclar)')
    chk(rt.get('todasLimpias') is True,
        'barrido de 22 páginas: rects dentro del lienzo virtual'
        + (f' · malas: {rt.get("paginasMalas")[:4]}' if rt.get('paginasMalas') else ''))
    chk(rt.get('idsOpts') is True, 'rejilla de AJUSTES intacta tras el barrido')
    chk(not errors, f'sin pageerrors ({len(errors)})')
    if errors:
        print('   pageerrors:', errors[:3])

    for key, name in [('pngMain', 'qa_arco69_main.png'),
                      ('pngSala', 'qa_arco69_salacfg.png'),
                      ('pngName', 'qa_arco69_nombre.png')]:
        if rt.get(key) and rt[key].startswith('data:image/png;base64,'):
            raw = base64.b64decode(rt[key].split(',', 1)[1])
            open(OUT + name, 'wb').write(raw)
            print(f'  captura: {name} ({len(raw):,} B)')
        else:
            chk(False, f'captura {name}')

    print(f'RESULTADO: {ok} OK · {fails} fallos')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    asyncio.run(main())
