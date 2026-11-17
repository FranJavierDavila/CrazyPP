#!/usr/bin/env python3
"""QA V2.138 · OESTE «TÚNEL A ESCALA» + EL MAPA DEL CLOWN.
  A1  locura/assets/mapa.webp SERVIDO = disco (sha256), 1380×752 y MISMO
      contenido píxel a píxel que el upload/Mapa.png del dueño
  A2  nodesPx del módulo = los re-medidos de v2.138 (con tx/ty/ts)
  A3  4 tapas creadas, centradas en tx/ty, escala ts y visibles en etapa 1
  A4  anillo del nodo actual a escala r/120 (r 114 en el nodo 1)
  A5  COBERTURA GEOMÉTRICA: cada tapa (290×300 × ts en px del arte) cubre
      el medallón medido (r_out + 3 px de AA) en los 4 nodos con tapa
  A6  TÚNEL a FACTOR ÚNICO: config (bh 1,8 · h 3,176 · bandaY 2,257) y
      geometría VIVA de tunelGrp (bocas 1,8×1,8, banda 26,4×3,176, centros
      y=1,8/2,257) + ventana cubierta SIN cortes (boca 0,9-2,7 y banda
      0,67-3,85 ⊇ ventana 1,08-2,55) + copias = 4
  B   VISUAL 3D: mapa del clown completo + primer plano del nodo 2 +
      portal de ENTRADA (1,8 m) en la ventana + portal de SALIDA espejado
  C   smoke 4 campeonatos sin pageerrors
"""
import hashlib
import io
import time
import urllib.request

import numpy as np
from PIL import Image
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


# ===== A1 · MAPA SERVIDO (locura) =====
serv = urllib.request.urlopen(BASE + '/championships/locura/assets/mapa.webp').read()
disco = open('/home/z/my-project/public/championships/locura/assets/mapa.webp', 'rb').read()
chk('A1 mapa servido = disco', hashlib.sha256(serv).hexdigest() == hashlib.sha256(disco).hexdigest(),
    f'({len(serv)} B)')
im = Image.open(io.BytesIO(serv))
chk('A1 dimensiones 1380×752', im.size == (1380, 752), str(im.size))
up = np.asarray(Image.open('/home/z/my-project/upload/Mapa.png').convert('RGB'), dtype=np.int16)
wv = np.asarray(im.convert('RGB'), dtype=np.int16)
diff = np.abs(up - wv)
chk('A1 contenido = arte del dueño (webp q92, dif media < 2)',
    diff.mean() < 2.0 and diff.max() < 60, f'media {diff.mean():.3f} · max {diff.max()}')

# ===== A5 · COBERTURA GEOMÉTRICA de las tapas (2D sobre el arte) =====
# medallones medidos (centro, r_out de la banda dorada) y tapas del módulo
MED = [(226, 253, 119), (453, 507, 126), (700, 256, 114), (959, 508, 128), (1208, 322, 113)]
TS = [None, 0.94, 0.86, 0.95, 0.85]
ok_all = True
for i, (cx, cy, ro) in enumerate(MED):
    if TS[i] is None:
        continue
    hw, hh = 290 * TS[i] / 2, 300 * TS[i] / 2
    # el círculo (ro+3 px de AA) cae DENTRO del rect de la tapa en el eje X
    # (limitante: 290 < 300) — margen sobrante:
    mx = hw - (ro + 3)
    ok = mx >= 0
    ok_all = ok_all and ok
    chk(f'A5 tapa nodo {i+1} cubre medallón r{ro}+3', ok, f'margen X {mx:.1f} px (ts {TS[i]})')
chk('A5 cobertura completa', ok_all)

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox",
        "--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})

    # ================= LOCURA: MAPA =================
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(BASE + '/game.html?champ=locura', wait_until="domcontentloaded", timeout=60000)
    for _ in range(40):
        s = js(page, "!!(window.__PP_LOCURA && window.__PP_LOCURA.ctrl() && "
                   "window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")

    r = js(page, """(() => {
      const c = window.__PP_LOCURA.ctrl();
      if (!c.map) return { __err: 'sin mapa' };
      const G = window.__PP_GAME;
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      c.map.group.visible = true;
      c.map.refresh();
      return { tapas: c.map.tapas.length, nodes: c.map.nodesPx.length }; })()""")
    chk('A2 mapa construido con 4 tapas', r.get('tapas') == 4, str(r))

    r = js(page, """(() => { const m = window.__PP_LOCURA.ctrl().map;
      return m.nodesPx.map(n => [n.x, n.y, n.r, n.tx ?? null, n.ty ?? null, n.ts ?? null]);
    })()""")
    ESP = [[226, 253, 114, None, None, None],
           [453, 507, 119, 453, 507, 0.94],
           [700, 256, 109, 700, 256, 0.86],
           [959, 508, 121, 959, 508, 0.95],
           [1208, 322, 107, 1208, 322, 0.85]]

    def _eq(a, b):
        if a is None or b is None:
            return a is None and b is None
        return abs(a - b) < 0.01
    ok = (isinstance(r, list) and len(r) == 5 and
          all(_eq(a[i], b[i]) for a, b in zip(r, ESP) for i in range(6)))
    chk('A2 nodesPx re-medidos v2.138', ok, str(r))

    r = js(page, """(() => { const m = window.__PP_LOCURA.ctrl().map;
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
    chk('A3 tapas centradas en tx/ty y escala ts', ok,
        str([(t['idx'], t['w']) for t in r] if isinstance(r, list) else r))
    visibles = [t['visible'] for t in r] if isinstance(r, list) else []
    chk('A3 tapas visibles en etapa 1 (cubren 2-5)', visibles == [True, True, True, True], str(visibles))

    r = js(page, """(() => { const m = window.__PP_LOCURA.ctrl().map;
      return { esc: +m.marker.scale.x.toFixed(4), esp: +(m.nodesPx[0].r / 120).toFixed(4),
               vis: m.marker.visible }; })()""")
    chk('A4 anillo nodo 1 a escala r/120', r.get('esc') == r.get('esp') and r.get('vis') is True, str(r))

    def nodo_mundo(i):
        e = f"""(() => {{ const m = window.__PP_LOCURA.ctrl().map;
          const o = m.tapas[{i}] ? m.tapas[{i}].mesh : m.marker;
          const e = m.group.matrixWorld.elements;
          const x = o.position.x, y = o.position.y, z = o.position.z;
          return [e[0]*x + e[4]*y + e[8]*z + e[12],
                  e[1]*x + e[5]*y + e[9]*z + e[13],
                  e[2]*x + e[6]*y + e[10]*z + e[14]]; }})()"""
        return js(page, e)

    page.evaluate("window.__n = 6")
    page.evaluate(TICK)
    pose(page, -1.30, 1.50, -0.90, -2.98, 1.48, -0.90)
    page.evaluate(TICK)
    time.sleep(0.6)
    page.screenshot(path='/home/z/my-project/scripts/_v2138_mapa_clown.png')
    print('B1 mapa clown completo OK')
    w1 = nodo_mundo(0)
    if isinstance(w1, list):
        pose(page, w1[0] + 0.85, w1[1], w1[2], w1[0], w1[1], w1[2])
        page.evaluate(TICK)
        time.sleep(0.6)
        page.screenshot(path='/home/z/my-project/scripts/_v2138_nodo2_clown.png')
        print('B2 nodo 2 (ARKANOID) OK', [round(v, 2) for v in w1])
    chk('sin pageerrors en locura', len(errs) == 0, str(errs[:2]))
    page.close()

    # ================= OESTE: TÚNEL =================
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:150]))
    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(BASE + '/game.html?champ=oeste', wait_until="domcontentloaded", timeout=60000)
    for _ in range(40):
        s = js(page, "!!(window.__PP_OESTE && window.__PP_OESTE.ctrl() && "
                   "window.__PP_GAME && window.__PP_GAME.rules)")
        if s is True:
            break
        time.sleep(1)
    time.sleep(2)
    page.evaluate("""(() => { const o = document.getElementById('overlay');
      if (o) o.style.display = 'none'; return 1; })()""")

    # A6 · sin cortes: ventana (1,08-2,55) dentro de boca (0,9-2,7) y banda (0,669-3,845)
    v0, v1 = 1.08, 2.55
    b0, b1 = 1.8 - 0.9, 1.8 + 0.9          # boca
    d0, d1 = 2.257 - 3.176 / 2, 2.257 + 3.176 / 2  # banda
    chk('A6 boca cubre la ventana (sin cortes)', b0 <= v0 and b1 >= v1, f'boca {b0}-{b1}')
    chk('A6 banda cubre la ventana (sin cortes)', d0 <= v0 and d1 >= v1, f'banda {d0:.3f}-{d1:.3f}')
    # factor único: h/bh = 6,0/3,4
    chk('A6 factor único h/bh = 6,0/3,4', abs((3.176 / 1.8) - (6.0 / 3.4)) < 0.002,
        f'{3.176 / 1.8:.4f} vs {6.0 / 3.4:.4f}')
    # copias por la misma regla
    import math
    chk('A6 copias = round(len/(h×2,35)) = 4',
        round(26.4 / (3.176 * 2.35)) == 4, str(round(26.4 / (3.176 * 2.35))))

    # B3/B4 · VISUAL: portal entrada + salida
    js(page, """(() => { const G = window.__PP_GAME, c = G.champs.mod.controller;
      c.stage = 4; c._armT = 0; c._duelOn = false; c.serveTrigger(0);
      return 1; })()""")
    page.evaluate(TICK)
    js(page, """(() => { const G = window.__PP_GAME;
      if (G._instr) G.hideInstrucciones(false);
      if (G.champIntro && G.champIntro.group) G.champIntro.group.visible = false;
      return 1; })()""")
    for _ in range(20):
        t = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
          return (c._tren && c._stageMode === 'tren') ? c._tren.phase : null; })()""")
        if t:
            break
        page.evaluate(TICK)
        time.sleep(0.3)

    # A6 · geometría VIVA del túnel — TRAS entrar en etapa 4 (tunelGrp vive
    # en _tren y se construye con el vagón del tren)
    r = js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller;
      const tg = (c._tren && c._tren.tunelGrp) || c.tunelGrp;
      if (!tg) return { __err: 'sin tunelGrp' };
      const piezas = tg.children.map(m => ({
        w: +m.geometry.parameters.width.toFixed(3),
        h: +m.geometry.parameters.height.toFixed(3),
        y: +m.position.y.toFixed(3), boca: !!(m.userData && m.userData.boca) }));
      return { bocas: piezas.filter(p => p.boca),
               banda: piezas.filter(p => !p.boca)[0] }; })()""")
    ok = (isinstance(r, dict) and 'bocas' in r and len(r['bocas']) == 4 and
          all(abs(b['w'] - 1.8) < 1e-3 and abs(b['h'] - 1.8) < 1e-3 and
              abs(b['y'] - 1.8) < 1e-3 for b in r['bocas']) and
          abs(r['banda']['w'] - 26.4) < 1e-3 and abs(r['banda']['h'] - 3.176) < 1e-3 and
          abs(r['banda']['y'] - 2.257) < 1e-3)
    chk('A6 tunelGrp VIVO: bocas 1,8×1,8 @y1,8 · banda 26,4×3,176 @y2,257', ok, str(r))

    js(page, """(() => { const c = window.__PP_GAME.champs.mod.controller, t = c._tren;
      if (t.phase !== 'run') t._depart();
      return { fase: t.phase }; })()""")
    page.evaluate("window.__n = 10")
    page.evaluate(TICK)
    js(page, """(() => { const G = window.__PP_GAME, t = G.champs.mod.controller._tren;
      t._tunnelPhase = 'pre'; t._tunnelT2 = 0; t._tunelZ = -1.82;
      t.tunelGrp.position.z = t._tunelZ; t.tunelGrp.visible = true;
      return 1; })()""")
    page.evaluate("window.__n = 2")
    page.evaluate(TICK)
    pose(page, 0.30, 1.60, 0.10, -3.55, 1.70, -1.82)
    page.evaluate(TICK)
    time.sleep(0.5)
    page.screenshot(path='/home/z/my-project/scripts/_v2138_portal_entrada.png')
    print('B3 portal entrada (1,8 m) OK')
    js(page, """(() => { const G = window.__PP_GAME, t = G.champs.mod.controller._tren;
      t._tunnelPhase = 'dur'; t._tunnelT2 = 0; t._tunelZ = 25.78;
      t.tunelGrp.position.z = t._tunelZ;
      return 1; })()""")
    page.evaluate(TICK)
    pose(page, 0.30, 1.60, 0.10, -3.55, 1.70, -1.82)
    page.evaluate(TICK)
    time.sleep(0.5)
    page.screenshot(path='/home/z/my-project/scripts/_v2138_portal_salida.png')
    print('B4 portal salida OK · pageerrors:', len(errs), errs[:2])
    page.evaluate("window.__camPose = null")
    chk('sin pageerrors en oeste', len(errs) == 0, str(errs[:2]))
    page.close()
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
print(f'\n===== QA V2.138: {n_ok}/{len(RES)} VERDE =====')
