#!/usr/bin/env python3
"""QA V2.137 · MAGIA «MAPA NUEVO DEL WIZARD» — mapa.webp reemplazado + nodos
re-medidos + tapas con tx/ty/ts.
  A1  el mapa.webp SERVIDO es byte a byte el disco (sha256) y mide 1380×752
  A2  nodesPx del módulo = los re-medidos de v2.137
  A3  4 tapas creadas con centro (tx/ty) y escala (ts) correctos
  A4  anillo del nodo actual a escala r/120 (r 126 en el nodo 1)
  B   VISUAL 3D: mapa completo + primeros planos de los nodos 2 y 5
  C   smoke 4 campeonatos sin pageerrors
"""
import hashlib
import time
import urllib.request

from playwright.sync_api import sync_playwright

BASE = 'http://localhost:3000'
RES = []


def chk(name, ok, extra=''):
    RES.append((name, ok, extra))
    print(f"{'✓' if ok else '✗'} {name} {extra}")


def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {'__err': str(e)[:200]}


TICK = """(() => { const G = window.__PP_GAME;
  if (!window.__t) window.__t = performance.now();
  for (let i = 0; i < (window.__n || 4); i++) {
    window.__t += 50; G.lastTime = window.__t / 1000 - 0.05; G.freezeT = 0;
    G.animate(window.__t);
  } return 1; })()"""

POSE_JS = """(() => {
  if (!window.__renderPatch) {
    const r = window.__PP_GAME.renderer;
    const real = r.render.bind(r);
    r.render = (scene, cam) => {
      const p = window.__camPose;
      if (p) { cam.position.set(p[0], p[1], p[2]); cam.lookAt(p[3], p[4], p[5]); }
      return real(scene, cam);
    };
    window.__renderPatch = true;
  }
  window.__camPose = window.__posePendiente || null;
  window.__posePendiente = null;
  return 1; })()"""


def pose(page, px, py, pz, tx, ty, tz):
    page.evaluate(f"window.__posePendiente = [{px},{py},{pz},{tx},{ty},{tz}]")
    page.evaluate(POSE_JS)


# ===== A1 · MAPA SERVIDO =====
serv = urllib.request.urlopen(BASE + '/championships/magia/assets/mapa.webp').read()
disco = open('/home/z/my-project/public/championships/magia/assets/mapa.webp', 'rb').read()
chk('A1 mapa servido = disco', hashlib.sha256(serv).hexdigest() == hashlib.sha256(disco).hexdigest(),
    f'({len(serv)} B)')
from PIL import Image
import io
im = Image.open(io.BytesIO(serv))
chk('A1 dimensiones 1380×752', im.size == (1380, 752), str(im.size))

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(BASE + '/game.html?champ=magia', wait_until="domcontentloaded", timeout=60000)
    for _ in range(40):
        s = js(page, "!!(window.__PP_MAGIA && window.__PP_MAGIA.ctrl() && "
                   "window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")

    # preparar mapa 3D
    r = js(page, """(() => {
      const c = window.__PP_MAGIA && window.__PP_MAGIA.ctrl();
      if (!c) return { __err: 'sin ctrl' };
      if (!c.map) c.build();
      if (!c.map.inited) c.map.build();
      const G = window.__PP_GAME;
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      c.map.group.visible = true;
      c.map.refresh();
      return { tapas: c.map.tapas.length, nodes: c.map.nodesPx.length }; })()""")
    chk('A2 mapa construido con 4 tapas', r.get('tapas') == 4, str(r))

    # ===== A2 · nodesPx =====
    r = js(page, """(() => { const m = window.__PP_MAGIA.ctrl().map;
      return m.nodesPx.map(n => [n.x, n.y, n.r, n.tx ?? null, n.ty ?? null, n.ts ?? null]);
    })()""")
    ESP = [[229, 258, 126, None, None, None],
           [456, 508, 131, 456, 490, 1.18],
           [701, 253, 122, 701, 220, 1.20],
           [966, 506, 132, 966, 477, 1.25],
           [1232, 162, 126, 1205, 150, 1.22]]
    def _eq(a, b):
        if a is None or b is None:
            return a is None and b is None
        return abs(a - b) < 0.01
    ok = (isinstance(r, list) and len(r) == 5 and
          all(_eq(a[i], b[i]) for a, b in zip(r, ESP) for i in range(6)))
    chk('A2 nodesPx re-medidos v2.137', ok, str(r))

    # ===== A3 · tapas: centro y escala =====
    r = js(page, """(() => { const m = window.__PP_MAGIA.ctrl().map;
      return m.tapas.map(t => {
        const n = m.nodesPx[t.idx];
        const p = m._pxToLocal((n.tx !== undefined) ? n.tx : n.x,
                               (n.ty !== undefined) ? n.ty : n.y);
        return { idx: t.idx, posOk:
                  Math.abs(t.mesh.position.x - p[0]) < 1e-5 &&
                  Math.abs(t.mesh.position.y - p[1]) < 1e-5,
                 w: +(t.mesh.geometry.parameters.width / m.TAPA_W).toFixed(4),
                 h: +(t.mesh.geometry.parameters.height / m.TAPA_H).toFixed(4),
                 ts: n.ts, visible: t.mesh.visible };
      }); })()""")
    ok = (isinstance(r, list) and len(r) == 4 and
          all(t['posOk'] and abs(t['w'] - t['ts']) < 1e-3 and
              abs(t['h'] - t['ts']) < 1e-3 for t in r))
    visibles = [t['visible'] for t in r] if isinstance(r, list) else []
    chk('A3 tapas centradas en tx/ty y escala ts', ok, str([(t['idx'], t['w']) for t in r] if isinstance(r, list) else r))
    chk('A3 tapas visibles en etapa 1 (cubren 2-5)', visibles == [True, True, True, True], str(visibles))

    # ===== A4 · anillo del nodo actual =====
    r = js(page, """(() => { const m = window.__PP_MAGIA.ctrl().map;
      return { esc: +m.marker.scale.x.toFixed(4), esp: +(m.nodesPx[0].r / 120).toFixed(4),
               vis: m.marker.visible }; })()""")
    chk('A4 anillo nodo 1 a escala r/120', r.get('esc') == r.get('esp') and r.get('vis') is True, str(r))

    # helper: mundo de un nodo (tapa i; THREE no es global → matrixWorld a mano)
    def nodo_mundo(i, tapa=True):
        e = f"""(() => {{ const m = window.__PP_MAGIA.ctrl().map;
          const o = m.tapas[{i}] ? m.tapas[{i}].mesh : m.marker;
          const p = o.getWorldPosition || null;
          const e = m.group.matrixWorld.elements;
          const x = o.position.x, y = o.position.y, z = o.position.z;
          return [e[0]*x + e[4]*y + e[8]*z + e[12],
                  e[1]*x + e[5]*y + e[9]*z + e[13],
                  e[2]*x + e[6]*y + e[10]*z + e[14]]; }})()"""
        return js(page, e)

    # ===== B · VISUAL =====
    page.evaluate("window.__n = 6")
    page.evaluate(TICK)
    # B1 · mapa completo
    pose(page, -1.30, 1.50, -0.90, -2.98, 1.48, -0.90)
    page.evaluate(TICK)
    time.sleep(0.6)
    page.screenshot(path='/home/z/my-project/scripts/_v2137_mapa.png')
    print('B1 mapa completo OK')
    # B2 · primer plano nodo 2 (tapa grande)
    w2 = nodo_mundo(0)
    if isinstance(w2, list):
        pose(page, w2[0] + 0.85, w2[1], w2[2], w2[0], w2[1], w2[2])
        page.evaluate(TICK)
        time.sleep(0.6)
        page.screenshot(path='/home/z/my-project/scripts/_v2137_nodo2.png')
        print('B2 nodo 2 OK', [round(v, 2) for v in w2])
    # B3 · primer plano nodo 5 (burbuja)
    w4 = nodo_mundo(3)
    if isinstance(w4, list):
        pose(page, w4[0] + 0.85, w4[1], w4[2], w4[0], w4[1], w4[2])
        page.evaluate(TICK)
        time.sleep(0.6)
        page.screenshot(path='/home/z/my-project/scripts/_v2137_nodo5.png')
        print('B3 nodo 5 OK', [round(v, 2) for v in w4])
    page.evaluate("window.__camPose = null")

    chk('C sin pageerrors en magia', len(errs) == 0, str(errs[:2]))
    browser.close()

# ===== C · SMOKE 4 CAMPEONATOS =====
with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 960, "height": 540})
    for champ in ('locura', 'magia', 'oeste', 'estacion_orbital'):
        page = ctx.new_page()
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)[:120]))
        page.goto(f'{BASE}/game.html?champ={champ}', wait_until='domcontentloaded', timeout=60000)
        for _ in range(30):
            s = js(page, "!!(window.__PP_GAME && window.__PP_GAME.rules)")
            if s is True:
                break
            time.sleep(1)
        time.sleep(3)
        chk(f'smoke {champ}: 0 pageerrors', len(errs) == 0, str(errs[:2]))
        page.close()
    browser.close()

n_ok = sum(1 for _, ok, _ in RES if ok)
print(f'\n===== QA V2.137: {n_ok}/{len(RES)} VERDE =====')
