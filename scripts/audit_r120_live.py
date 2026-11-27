#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit_r120_live.py — medición en vivo del juego REAL (SOLO LECTURA).

Patrón «arnés vivo» del proyecto (qa_r119/qa_rendimiento):
  · servidor estático de public/ en un puerto propio
  · Chromium headless con SwiftShader
  · reloj sintético: setAnimationLoop(null) + __paso() llama a g.animate(t)
    (rAF headless corre a ~1,5 fps y no sirve para medir)
  · pp_tele=0 para NO escribir telemetría real del dueño

Mide, sin modificar nada:
  1 · arranque (navegación → __PP_GAME && __PP_VERSION)
  2 · configuración del render (pixelRatio, foveación, sombras, tone mapping)
  3 · estadísticas de escena en el HALL/menú (mallas, instancias, luces,
      texturas más grandes, geometrías más pesadas, programas de shaders)
  4 · POR FRAME en el menú: draw calls, triángulos, heap JS (180 pasos de
      33,4 ms = 6 s de tiempo de juego)
  5 · lo mismo DENTRO de un partido real (__pp2DPlay=true + menuClick)
  6 · pageerrors y errores de consola durante toda la sesión

Uso: python3 scripts/audit_r120_live.py
"""
import functools
import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PORT = 8867
RAIZ = '/home/z/my-project'
PUB = RAIZ + '/public'

RELOJ = """() => {
  window.__t0 = performance.now() + 500;
  window.__tMs = window.__t0;
  window.__PP_GAME.renderer.setAnimationLoop(null);
  window.__paso = () => {
    window.__tMs += 33.4;
    try { window.__PP_GAME.animate(window.__tMs); } catch (e) {
      window.__pasosErr = (window.__pasosErr || 0) + 1;
    }
  };
  return typeof window.__PP_GAME.animate;
}"""

MUESTREA = """(n) => {
  const g = window.__PP_GAME, out = [];
  const info = g.renderer.info;
  const heap = () => (performance.memory ? performance.memory.usedJSHeapSize : 0);
  for (let i = 0; i < n; i++) {
    window.__paso();
    out.push([info.render.calls, info.render.triangles, heap()]);
  }
  return { out, errores: window.__pasosErr || 0,
           estado: g.rules ? g.rules.state : null,
           marcador: g.rules ? [g.rules.scorePlayer, g.rules.scoreAi] : null };
}"""

ESCENA = """() => {
  const g = window.__PP_GAME, r = g.renderer, sc = g.scene, info = r.info;
  const stats = { mesh: 0, inst: 0, luz: 0, sombra: 0, group: 0, sprites: 0,
                  lineas: 0, puntos: 0, canvasTex: 0 };
  const tex = new Map(), geo = new Map();
  const MAPS = ['map','normalMap','roughnessMap','metalnessMap','aoMap',
                'emissiveMap','envMap','alphaMap','specularMap'];
  sc.traverse((o) => {
    if (o.isInstancedMesh) stats.inst++;
    if (o.isMesh) stats.mesh++;
    if (o.isSprite) stats.sprites++;
    if (o.isLine || o.isLine2) stats.lineas++;
    if (o.isPoints) stats.puntos++;
    if (o.isGroup) stats.group++;
    if (o.isLight) { stats.luz++;
      if (o.castShadow) stats.sombra++; }
    const ms = Array.isArray(o.material) ? o.material : (o.material ? [o.material] : []);
    for (const m of ms) {
      for (const k of MAPS) {
        const t = m && m[k];
        if (t && t.uuid) {
          const img = t.image;
          const w = img && (img.width || img.videoWidth) || 0;
          const h = img && (img.height || img.videoHeight) || 0;
          if (t.isCanvasTexture) stats.canvasTex++;
          const prev = tex.get(t.uuid);
          if (!prev || w * h > prev.wh) tex.set(t.uuid, { w, h, k, wh: w * h });
        }
      }
    }
    const gm = o.geometry;
    if (gm && gm.uuid && !geo.has(gm.uuid)) {
      const pos = gm.attributes && gm.attributes.position;
      geo.set(gm.uuid, { v: pos ? pos.count : 0,
                         idx: gm.index ? gm.index.count : 0 });
    }
  });
  const tList = [...tex.values()].filter(t => t.wh > 0)
    .sort((a, b) => (b.w * b.h) - (a.w * a.h)).slice(0, 12);
  const gList = [...geo.values()].sort((a, b) => (b.v + b.idx) - (a.v + a.idx))
    .slice(0, 10);
  let smap = null;
  try { smap = r.shadowMap ? { on: r.shadowMap.enabled,
        tipo: r.shadowMap.type === 1 ? 'PCF' : (r.shadowMap.type === 2 ? 'PCFSoft' : r.shadowMap.type) } : null;
  } catch (e) {}
  let fov = null;
  try { fov = r.xr && r.xr.getFoveation ? r.xr.getFoveation() : null; } catch (e) {}
  return {
    pixelRatio: r.getPixelRatio ? r.getPixelRatio() : null,
    foveacion: fov, xrEnabled: !!(r.xr && r.xr.enabled),
    sombras: smap, tone: r.toneMapping,
    antialias: (r.getContext().getContextAttributes() || {}).antialias || false,
    memoria: { geoms: info.memory.geometries, texs: info.memory.textures },
    programas: info.programs ? info.programs.length : null,
    ...stats,
    texturasTop: tList, geometriasTop: gList,
  };
}"""

ARRANCA = """() => {
  const g = window.__PP_GAME;
  window.__pp2DPlay = true;
  g.menuPage = g.menuPage || 'main';
  g.menuSec = '';
  try { g.drawMenu(); } catch (e) { return { error: 'drawMenu: ' + e.message }; }
  const rects = (g._menuRects || []).map((x, i) => ({ i, id: x.id }));
  return { menuPage: g.menuPage, menuSec: g.menuSec, ids: rects,
           estado: g.rules ? g.rules.state : null,
           online: !!g.net && !!g.net.online };
}"""

CLIC = """(idx) => {
  const g = window.__PP_GAME;
  try { g.menuClick(idx, 0); } catch (e) { return { error: e.message }; }
  return { estado: g.rules ? g.rules.state : null,
           pagina: g.menuPage || null };
}"""


def pct(lista, q):
    if not lista:
        return 0
    s = sorted(lista)
    return s[min(len(s) - 1, int(q * len(s)))]


def resumen(nombre, muestras):
    calls = [c for c, t, h in muestras]
    tris = [t for c, t, h in muestras]
    heap = [h for c, t, h in muestras]
    heap_ok = [h for h in heap if h > 0]
    r = {
        'pasos': len(muestras),
        'draw_calls': {'media': round(sum(calls) / len(calls), 1),
                       'p95': pct(calls, 0.95), 'max': max(calls)},
        'triangulos': {'media': round(sum(tris) / len(tris)),
                       'p95': pct(tris, 0.95), 'max': max(tris)},
    }
    if len(heap_ok) > 2:
        r['heap_MB_ini'] = round(heap_ok[0] / 1e6, 1)
        r['heap_MB_fin'] = round(heap_ok[-1] / 1e6, 1)
        r['heap_MB_max'] = round(max(heap_ok) / 1e6, 1)
        r['heap_MB_delta'] = round((heap_ok[-1] - heap_ok[0]) / 1e6, 1)
    print(f'== {nombre} ==')
    for k, v in r.items():
        print(f'  · {k}: {v}')
    return r


def main():
    # :3000 es el servidor del propio proyecto (qa_version verifica que sirve
    # el game.html byte-exacto); mi http.server de Python tardaba 23 s en el
    # arranque por el tamaño del fichero — se usa el del proyecto.
    srv = None

    from playwright.sync_api import sync_playwright
    resultado = {'pageerrors': [], 'consola_err': []}
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--enable-unsafe-swiftshader', '--use-gl=angle',
                                     '--use-angle=swiftshader',
                                     '--autoplay-policy=no-user-gesture-required'])
        pg = b.new_page(viewport={'width': 1280, 'height': 800})
        pg.on('pageerror', lambda e: resultado['pageerrors'].append(str(e)[:200]))
        pg.on('console', lambda m: resultado['consola_err'].append(m.text[:200])
              if m.type == 'error' else None)

        t0 = time.monotonic()
        pg.goto('http://localhost:3000/game.html?pp_tele=0', wait_until='load')
        pg.wait_for_function("() => window.__PP_GAME && window.__PP_VERSION", timeout=90000)
        resultado['boot_ms'] = round((time.monotonic() - t0) * 1000)
        resultado['version'] = pg.evaluate('() => window.__PP_VERSION')
        print(f'boot: {resultado["boot_ms"]} ms · versión {resultado["version"]}')

        cfg = pg.evaluate(ESCENA)
        resultado['config_render'] = {k: cfg[k] for k in
                                      ('pixelRatio', 'foveacion', 'xrEnabled', 'sombras',
                                       'tone', 'antialias', 'memoria', 'programas')}
        resultado['escena_hall'] = cfg

        pg.evaluate(RELOJ)
        m_menu = pg.evaluate("""(n) => {
            const g = window.__PP_GAME, out = [];
            const info = g.renderer.info;
            const heap = () => (performance.memory ? performance.memory.usedJSHeapSize : 0);
            for (let i = 0; i < n; i++) {
              window.__paso();
              out.push([info.render.calls, info.render.triangles, heap()]);
            }
            return { out, errores: window.__pasosErr || 0,
                     estado: g.rules ? g.rules.state : null,
                     marcador: g.rules ? [g.rules.scorePlayer, g.rules.scoreAi] : null };
          }""", 180)
        resultado['menu'] = resumen('HALL/MENÚ · 180 pasos (6 s juego)', m_menu['out'])
        resultado['menu_estado'] = m_menu.get('estado')
        resultado['menu_errores_pasos'] = m_menu.get('errores')

        arranque = pg.evaluate(ARRANCA)
        ids = arranque.get('ids', [])
        resultado['menu_ids'] = [x['id'] for x in ids][:40]
        print('menu ids:', resultado['menu_ids'])
        print('estado tras abrir menú:', arranque.get('estado'), '· page:', arranque.get('menuPage'))

        marcado = False
        patron = ('jugar', 'play', 'partido', 'match', 'vsai', 'unjug', '1p')
        candidatos = [c for c in ids
                      if any(p in str(c.get('id') or '').lower() for p in patron)]
        if not candidatos:
            candidatos = ids[:1]          # plan B: primer rect del menú
        for cand in candidatos:
            r2 = pg.evaluate(CLIC, cand['i'])
            print('click', cand.get('id'), cand.get('i'), '→', r2)
            if r2.get('estado') in ('serve', 'rally', 'point'):
                marcado = True
                break
        resultado['partido_arrancado'] = marcado

        if marcado:
            # deja vivir el partido unos pasos para que se monte todo
            pg.evaluate("() => { for (let i = 0; i < 60; i++) window.__paso(); }")
            m2 = pg.evaluate("""(n) => {
                const g = window.__PP_GAME, out = [];
                const info = g.renderer.info;
                const heap = () => (performance.memory ? performance.memory.usedJSHeapSize : 0);
                for (let i = 0; i < n; i++) {
                  window.__paso();
                  out.push([info.render.calls, info.render.triangles, heap()]);
                }
                return { out, estado: g.rules ? g.rules.state : null,
                         marcador: g.rules ? [g.rules.scorePlayer, g.rules.scoreAi] : null };
              }""", 240)
            resultado['partido'] = resumen('PARTIDO · 240 pasos (8 s juego)', m2['out'])
            resultado['partido_estado'] = m2.get('estado')
            resultado['partido_marcador'] = m2.get('marcador')
            resultado['escena_partido'] = pg.evaluate(ESCENA)
        else:
            print('no se encontró botón de jugar: se mide solo el hall')

        b.close()
    if srv:
        srv.shutdown()

    print('== ERRORES ==')
    print('pageerrors:', len(resultado['pageerrors']), resultado['pageerrors'][:5])
    print('console.error:', len(resultado['consola_err']), resultado['consola_err'][:8])
    resultado['n_pageerrors'] = len(resultado['pageerrors'])
    resultado['n_consola_err'] = len(resultado['consola_err'])

    print('== JSON COMPLETO ==')
    completo = json.dumps(resultado, ensure_ascii=False, indent=1, default=str)
    with open('/tmp/render/audit_r120_live.json', 'w', encoding='utf-8') as f:
        f.write(completo)
    print(completo[:12000])


if __name__ == '__main__':
    main()
