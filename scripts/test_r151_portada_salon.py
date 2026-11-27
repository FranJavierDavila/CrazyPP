#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r151 · ARNÉS DEL ARRANQUE DIRECTO AL SALÓN (petición del dueño:
«la pantalla del juego que entre directamente en el Hall del usuario sin
pantalla intermedia»).

Sirve public/ en :3007 y abre game.html en Chromium headless (sin WebXR —
igual que un escritorio). Comprueba que:
  1. 0 pageerrors durante la carga y 8 s de vida.
  2. window.__game existe y ARRANCA EN EL SALÓN: game.inHall === true.
  3. El Hall visible y la cancha guardada: hallGroup.visible === true,
     roomGroup.visible === false y la mesa oculta (v3.6.30).
  4. La portada se RETIRÓ: .hero-wrap display:none y #overlay transparente.
  5. El HUD mínimo vive: #vrbtn clicable (offsetParent ≠ null), palas de
     idioma presentes, mutebtn presente.
  6. La cámara 2D está DENTRO del salón: rig en HALL.cz+2,3 (z −16,2) y
     cámara local (0, ~1.55, 0).
  7. El canvas recibió la clase 'listo' (fade-in del boot r151).
Guarda captura en scripts/_r151_salon.png para el ojo del dueño.

Ejecución: python3 -I scripts/test_r151_portada_salon.py   (≈25 s)
"""
import http.server
import socketserver
import sys
import threading
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.join(os.path.dirname(HERE), 'public')
PORT = 3007

sys.path.insert(0, HERE)


def serve():
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(PUBLIC)

    class H(handler):
        def log_message(self, *a):   # silencio
            pass

    with http.server.ThreadingHTTPServer(('127.0.0.1', PORT), H) as httpd:
        httpd.serve_forever()


def main():
    t = threading.Thread(target=serve, daemon=True)
    t.start()

    from playwright.sync_api import sync_playwright

    fails = []
    ok = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=['--use-gl=swiftshader'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})
        perr = []
        page.on('pageerror', lambda e: perr.append(str(e)))
        page.goto(f'http://127.0.0.1:{PORT}/game.html', wait_until='load', timeout=30_000)
        page.wait_for_timeout(8_000)   # boot + salón + fade-in

        # 1) 0 pageerrors
        if perr:
            fails.append(f'pageerrors ({len(perr)}): {perr[:3]}')
        else:
            ok += 1

        # 2-3 · 6-7 · estado del juego (una sola evaluación)
        st = page.evaluate('''() => {
            const g = window.__game;
            if (!g) return { err: 'sin window.__game' };
            const vis = (o) => !!(o && o.visible);
            const mesa = g.tableGroup ? !g.tableGroup.visible : null;
            const cam = g.camera ? { x: +g.camera.position.x.toFixed(3),
                y: +g.camera.position.y.toFixed(3), z: +g.camera.position.z.toFixed(3) } : null;
            const rigZ = g.rig ? +g.rig.position.z.toFixed(3) : null;
            const cEl = document.getElementById('c');
            return {
                inHall: !!g.inHall,
                hallVis: vis(g.hallGroup),
                roomVis: vis(g.roomGroup),
                mesaOculta: mesa,
                cam, rigZ,
                canvasListo: !!(cEl && cEl.classList.contains('listo')),
            };
        }''')
        if st.get('err'):
            fails.append('eval: ' + st['err'])
        else:
            if st['inHall'] is True:
                ok += 1
            else:
                fails.append(f'inHall={st["inHall"]} (esperado True)')
            if st['hallVis'] and not st['roomVis']:
                ok += 1
            else:
                fails.append(f'hallVis={st["hallVis"]} roomVis={st["roomVis"]}')
            if st['mesaOculta'] is True:
                ok += 1
            else:
                fails.append(f'mesaOculta={st["mesaOculta"]}')
            if st['rigZ'] is not None and abs(st['rigZ'] + 16.2) < 0.01:
                ok += 1
            else:
                fails.append(f'rigZ={st["rigZ"]} (esperado −16,2 = HALL.cz+2,3)')
            if st['cam'] and abs(st['cam']['y'] - 1.55) < 0.15 and abs(st['cam']['x']) < 0.01 \
               and abs(st['cam']['z']) < 0.01:
                ok += 1
            else:
                fails.append(f'cámara local={st["cam"]} (esperado ~(0,1.55,0))')
            if st['canvasListo']:
                ok += 1
            else:
                fails.append('canvas sin clase listo')

        # 4) portada retirada (CSS)
        css = page.evaluate('''() => {
            const hero = document.querySelector('.hero-wrap');
            const ov = document.getElementById('overlay');
            const heroD = hero ? getComputedStyle(hero).display : null;
            const bg = ov ? getComputedStyle(ov).backgroundColor : null;
            return { heroD, bg, ovPE: ov ? getComputedStyle(ov).pointerEvents : null };
        }''')
        if css.get('heroD') == 'none':
            ok += 1
        else:
            fails.append(f'hero display={css.get("heroD")} (esperado none)')
        if css.get('bg') in ('rgba(0, 0, 0, 0)', 'transparent'):
            ok += 1
        else:
            fails.append(f'overlay bg={css.get("bg")} (esperado transparente)')

        # 5) HUD mínimo vivo (r151: offsetParent es NULL para position:fixed —
        #    el criterio honesto es caja visible con getBoundingClientRect)
        hud = page.evaluate('''() => {
            const vivo = (id) => {
                const e = document.getElementById(id);
                if (!e) return false;
                const r = e.getBoundingClientRect();
                return r.width > 0 && r.height > 0 &&
                    getComputedStyle(e).visibility !== 'hidden';
            };
            return { vrbtn: vivo('vrbtn'), padEs: vivo('padEs'), mute: vivo('mutebtn') };
        }''')
        if all(hud.values()):
            ok += 1
        else:
            fails.append(f'HUD={hud}')

        # captura para el ojo del dueño
        shot = os.path.join(HERE, '_r151_salon.png')
        page.screenshot(path=shot)
        browser.close()

    total = ok + len(fails)
    print(f'— r151 arranque directo al salón: {ok}/{total} OK')
    for f in fails:
        print(f'  ✗ {f}')
    if fails:
        sys.exit(1)
    print('  ✓ el Hall es la pantalla de entrada; portada retirada; HUD mínimo vivo')


if __name__ == '__main__':
    main()
