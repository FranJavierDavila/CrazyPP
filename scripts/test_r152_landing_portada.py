#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r152 · ARNÉS DE LA PORTADA EN LA RAÍZ + ENTRADA VR EN UN TOQUE.

Petición del dueño: «la LANDING informativa es la que quiero que quede como
teníamos la game.html, se entra desde ahí, así la game.html ya debemos estar
dentro de VR». La activación del clic no cruza la navegación (WebXR exige un
gesto dentro del propio documento), así que el flujo fiel es:
  LANDING (portada clásica) → game.html?vr=1 → UN TOQUE en cualquier parte → VR.

Parte A — LANDING renderizada (plantilla de deploy_pages.py con sustituciones):
  1. 0 pageerrors · hero visible · 2 palas de idioma · badge de versión.
  2. #vrbtn es <a href="game.html?vr=1"> (el camino del dueño).
  3. Pulsar ENGLISH → localStorage pp_lang='en' (la MISMA clave que lee c00)
     y la imagen PLAY IN VR queda visible.
  4. Estado WebXR: texto final (headless sin xr → mensaje honesto de 2D).
  5. Passthrough oculto sin soporte AR (headless) — en Quest aparece.

Parte B — game.html?vr=1 (Chromium headless, sin WebXR):
  6. Boot con el salón como pantalla de entrada (r151 intacto: inHall=true).
  7. #tapvr visible con el texto TOCA/TAP (aviso de toque único).
  8. Un pointerdown dispara enterVR → rechazo LIMPIO y ATRAPADO en
     headless (#tapvr.mal) — 0 pageerrors, el salón sigue en 2D.

Capturas: scripts/_r152_landing.png · scripts/_r152_tapvr.png
Ejecución: python3 -I scripts/test_r152_landing_portada.py   (≈30 s)
"""
import http.server
import os
import re
import shutil
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, 'public')
PORT = 3008


def render_landing():
    src = open(os.path.join(HERE, 'deploy_pages.py'), encoding='utf-8').read()
    m = re.search(r'LANDING = """(.*?)"""', src, re.DOTALL)
    if not m:
        sys.exit('✗ No encuentro la plantilla LANDING en deploy_pages.py')
    html = m.group(1)
    for k, v in (('@@VERSION@@', '3.6.235-SDK6'), ('@@COMMIT@@', 'test0000000'),
                 ('@@REPO@@', 'FranJavierDavila/CrazyPP'), ('@@FECHA@@', '01-01-2026 00:00'),
                 ('@@GAME12@@', 'testsha12xx')):
        html = html.replace(k, v)
    return html


def make_site(tmp):
    with open(os.path.join(tmp, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(render_landing())
    # TODO el árbol public/ por symlink EXCEPTO index.html (si existiera):
    # el juego necesita core/, vendor/, assets/, championships/… — un solo
    # 404 y el boot entero muere (lección r152: enlazar a mano se queda corto)
    for name in os.listdir(PUBLIC):
        if name == 'index.html':
            continue
        dst = os.path.join(tmp, name)
        if os.path.exists(dst) or os.path.islink(dst):
            continue
        src_p = os.path.join(PUBLIC, name)
        try:
            os.symlink(src_p, dst)
        except OSError:
            (shutil.copytree if os.path.isdir(src_p) else shutil.copy)(src_p, dst)


def serve(tmp):
    os.chdir(tmp)

    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):   # silencio
            pass

    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    tmp = tempfile.mkdtemp(prefix='r152_landing_')
    make_site(tmp)
    serve(tmp)

    from playwright.sync_api import sync_playwright

    fails = []
    ok = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--use-gl=swiftshader'])
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        perr = []
        page.on('pageerror', lambda e: perr.append(str(e)))

        # ---------- PARTE A · la portada en la raíz ----------
        page.goto(f'http://127.0.0.1:{PORT}/', wait_until='load', timeout=30_000)
        page.wait_for_timeout(1_500)

        if perr:
            fails.append(f'[A] pageerrors ({len(perr)}): {perr[:2]}')
        else:
            ok += 1

        a = page.evaluate('''() => {
            const hero = document.querySelector('.hero-wrap img');
            const vr = document.getElementById('vrbtn');
            const pads = document.querySelectorAll('.padbtn').length;
            const badge = document.getElementById('verBadge');
            return {
                heroOk: !!(hero && hero.naturalWidth > 0),
                vrHref: vr ? vr.getAttribute('href') : null,
                pads,
                badge: badge ? badge.textContent : null,
                arDisp: (document.getElementById('arlink') || {}).style?.display ?? null,
            };
        }''')
        if a.get('heroOk'):
            ok += 1
        else:
            fails.append('[A] hero de la portada no carga (naturalWidth=0)')
        if a.get('vrHref') == 'game.html?vr=1':
            ok += 1
        else:
            fails.append(f'[A] #vrbtn href={a.get("vrHref")} (esperado game.html?vr=1)')
        if a.get('pads') == 2:
            ok += 1
        else:
            fails.append(f'[A] palas de idioma={a.get("pads")} (esperado 2)')
        if a.get('badge') == 'V3.6.235-SDK6':
            ok += 1
        else:
            fails.append(f'[A] badge={a.get("badge")} (esperado V3.6.235-SDK6)')

        # idioma: la MISMA clave pp_lang que lee el juego (c00)
        page.click('.padbtn[data-lang="en"]')
        page.wait_for_timeout(300)
        b = page.evaluate('''() => ({
            lang: localStorage.getItem('pp_lang'),
            enVis: document.getElementById('playEn').style.display === '',
            esVis: document.getElementById('playEs').style.display === 'none',
            selEn: document.querySelector('.padbtn[data-lang="en"]').classList.contains('sel'),
        })''')
        if b.get('lang') == 'en' and b.get('enVis') and b.get('esVis') and b.get('selEn'):
            ok += 1
        else:
            fails.append(f'[A] idioma EN no se fija/pinta: {b}')
        # y de vuelta a español (deja pp_lang=es para la parte B)
        page.click('.padbtn[data-lang="es"]')
        page.wait_for_timeout(200)

        st = page.evaluate('() => document.getElementById("status").textContent || ""')
        if st and 'Comprobando' not in st and 'Checking' not in st:
            ok += 1
        else:
            fails.append(f'[A] status WebXR sin resolver: "{st}"')
        if a.get('arDisp') == 'none':
            ok += 1
        else:
            fails.append('[A] passthrough debería estar OCULTO sin soporte AR (headless)')

        page.screenshot(path=os.path.join(HERE, '_r152_landing.png'))

        # ---------- PARTE B · game.html?vr=1 → un toque → intento de VR ----------
        page.goto(f'http://127.0.0.1:{PORT}/game.html?vr=1', wait_until='load', timeout=40_000)
        page.wait_for_timeout(8_000)

        g = page.evaluate('''() => {
            const g = window.__game;
            const h = document.getElementById('tapvr');
            const c = document.getElementById('c');
            return {
                inHall: !!(g && g.inHall),
                tapvr: h ? (h.textContent || '') : null,
                tapvrPE: h ? getComputedStyle(h).pointerEvents : null,
                listo: !!(c && c.classList.contains('listo')),
            };
        }''')
        if g.get('inHall'):
            ok += 1
        else:
            fails.append('[B] el salón no es la pantalla de entrada (inHall=false)')
        if g.get('tapvr') and ('TOCA' in g['tapvr'] or 'TAP' in g['tapvr']):
            ok += 1
        else:
            fails.append(f'[B] aviso #tapvr ausente o raro: {g.get("tapvr")!r}')
        if g.get('tapvrPE') == 'none':
            ok += 1
        else:
            fails.append(f'[B] #tapvr pointer-events={g.get("tapvrPE")} (esperado none: el toque es del lienzo)')
        if g.get('listo'):
            ok += 1
        else:
            fails.append('[B] canvas sin .listo')

        page.screenshot(path=os.path.join(HERE, '_r152_tapvr.png'))

        # el toque: en headless (sin WebXR) enterVR rechaza y el aviso queda
        # en rojo (.mal) — el rechazo DEBE estar atrapado, 0 pageerrors
        page.mouse.click(640, 300)
        page.wait_for_timeout(1_000)
        t = page.evaluate('''() => {
            const h = document.getElementById('tapvr');
            return { cls: h ? h.className : null, txt: h ? (h.textContent || '') : null };
        }''')
        if t.get('cls') and 'mal' in t['cls']:
            ok += 1
        else:
            fails.append(f'[B] el toque no llegó a enterVR (o el rechazo no se atrapó): {t}')
        if not perr:
            ok += 1
        else:
            fails.append(f'[B] pageerrors tras el toque ({len(perr)}): {perr[:2]}')

        browser.close()

    shutil.rmtree(tmp, ignore_errors=True)
    total = ok + len(fails)
    print(f'— r152 portada en la raíz + un toque a VR: {ok}/{total} OK')
    for f in fails:
        print(f'  ✗ {f}')
    if fails:
        sys.exit(1)
    print('  ✓ la raíz ES la portada clásica; ?vr=1 acepta UN toque en cualquier parte')


if __name__ == '__main__':
    main()
