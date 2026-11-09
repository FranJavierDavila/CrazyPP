#!/usr/bin/env python3
"""r33 · DIAGNÓSTICO del informe del dueño: «en el campeonato de Estación
Estelar (Orbital) no aparece el rival Astro en las partidas».

Sonda en vivo (Playwright, SwiftShader): lanza el campeonato, entra en la
sala, ARRANCA EL DUELO 1 y muestrea el standee del ASTRO (visible, padres
hasta la escena, textura viva, posición, escala) — primero en la sala y
luego durante el duelo, varias muestras para cazar ocultadores por frame.
Además: leave() + re-launch para reprobar el ciclo de texturas (sospecha
dispose de _ownTex). Guarda capturas en download/.
"""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

BASE = 'http://127.0.0.1:8123'
OUT = '/home/z/my-project/download'

MUESTREA = """() => {
  const G = window.__PP_GAME || window.__game;
  if (!G) return { error: 'sin juego' };
  const mod = G.champs && (G.champs.moduleIfLoaded
    ? G.champs.moduleIfLoaded('estacion_orbital') : null);
  if (!mod) return { error: 'módulo no cargado' };
  const ctrl = mod.controller || mod;
  const m = ctrl.rivalMesh;
  if (!m) return { error: 'sin rivalMesh', sdk: !!ctrl._rivalSDK };
  const padres = [];
  let n = m;
  while (n) { padres.push({ vis: n.visible, tipo: n.type || '?',
                            nom: n.name || '' });
               if (!n.parent) break; n = n.parent; }
  const mat = m.material;
  const map = mat && mat.map;
  return {
    visible: m.visible,
    grupoVisible: ctrl.group ? ctrl.group.visible : null,
    padreCount: padres.length,
    cadena: padres.map(p => (p.vis ? 1 : 0)).join('→'),
    enEscena: (() => { let n = m, s = false;
      while (n) { if (n.isScene) { s = true; break; } n = n.parent; }
      return s; })(),
    pos: [+m.position.x.toFixed(2), +m.position.y.toFixed(2),
          +m.position.z.toFixed(2)],
    escala: [+m.scale.x.toFixed(2), +m.scale.y.toFixed(2)],
    tieneMap: !!map,
    mapImg: map && map.image ? (map.image.width + 'x' + map.image.height)
                             : null,
    mapVersion: map ? map.version : null,
    matOpacity: mat ? +mat.opacity.toFixed(2) : null,
    alphaTest: mat ? mat.alphaTest : null,
    estadoRival: ctrl._rivalEstado,
    estadoSDK: ctrl._rivalSDK && ctrl._rivalSDK.estado
      ? ctrl._rivalSDK.estado() : null,
    enFrustum: (() => { try {
      const Gg = window.__PP_GAME || window.__game;
      const cam = Gg.camera || (Gg.cameras && Gg.cameras[0]);
      if (!cam) return null;
      const box = new (m.geometry.constructor)();
      // frustum rápido: proyecta el centro del mesh
      const v = m.getWorldPosition(new (Object.getPrototypeOf(
        m.position).constructor)()).project(cam);
      return { x: +v.x.toFixed(2), y: +v.y.toFixed(2),
               z: +v.z.toFixed(2) };
    } catch (e) { return 'err:' + e.message; } })(),
  };
}"""


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=['--enable-unsafe-swiftshader'])
        page = await browser.new_page(viewport={'width': 1280, 'height': 800})
        errs = []
        page.on('pageerror', lambda e: errs.append(str(e)))
        print('== carga game.html ==')
        # el dueño entra a la Orbital en MODO DEPURACIÓN (r72: sólo abre así)
        await page.add_init_script(
            "try { localStorage.setItem('pp_player_name', 'foro3d'); }"
            " catch (e) {}")
        await page.goto(BASE + '/game.html', wait_until='domcontentloaded',
                        timeout=60000)
        try:
            await page.wait_for_function('!!(window.__PP_GAME||window.__game)',
                                         timeout=45000)
        except Exception:
            print('!! el juego no llegó a montarse'); print(errs[:6])
            await browser.close(); return 1
        ver = await page.evaluate('window.__PP_VERSION || "?"')
        print('versión:', ver)

        print('== launch estacion_orbital (sala) ==')
        r0 = await page.evaluate(
            """async () => { const G = window.__PP_GAME || window.__game;
             try { await G.champs.launch('estacion_orbital');
                   return { ok: true, activeId: G.champs.activeId,
                     mods: Object.keys(G.champs.modules || {}) }; }
             catch (e) { return { ok: false, err: String(e && e.stack || e) }; }
             }""")
        print('launch:', json.dumps(r0, ensure_ascii=False))
        await page.wait_for_timeout(3500)
        sala = await page.evaluate(MUESTREA)
        print('SALA:', json.dumps(sala, ensure_ascii=False, indent=1))
        await page.screenshot(path=f'{OUT}/_r33_astro_sala.png')

        print('== arranca DUELO 1 (serveTrigger en sala) ==')
        duelo = await page.evaluate("""async () => {
          const G = window.__PP_GAME || window.__game;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          if (!mod) return { error: 'módulo no cargado tras launch' };
          const ctrl = mod.controller || mod;
          const et0 = ctrl._etapa ? ctrl._etapa().id : null;
          ctrl.serveTrigger();
          await new Promise(r => setTimeout(r, 2500));
          return { etapa: et0, estadoChamp: ctrl.state,
                   rules: G.rules.state };
        }""")
        print('DUELO arranque:', json.dumps(duelo, ensure_ascii=False))
        for i in range(4):
            await page.wait_for_timeout(1200)
            d = await page.evaluate(MUESTREA)
            print(f'DUELO t+{(i + 1) * 1.2:.1f}s:',
                  json.dumps(d, ensure_ascii=False))
        await page.screenshot(path=f'{OUT}/_r33_astro_duelo.png')

        print('== FOTO con cámara manual (el standee en cuadro) ==')
        for nombre, pos, look in [
            ('rival', '0.6,1.55,0.6', '1.26,1.05,-3.3'),
            ('rival_cerca', '0.9,1.3,-2.0', '1.26,1.05,-3.3'),
        ]:
            data = await page.evaluate(
                """async ([pos, look]) => {
              const G = window.__PP_GAME || window.__game;
              const cam = G.camera.clone();
              cam.aspect = 16 / 9; cam.fov = 75;
              cam.updateProjectionMatrix();
              const V = G.camera.position.constructor;
              cam.position.set(...pos.split(',').map(Number));
              cam.lookAt(new V(...look.split(',').map(Number)));
              G.renderer.render(G.scene, cam);
              return G.renderer.domElement.toDataURL('image/png');
            }""", [pos, look])
            import base64 as b64
            png = b64.b64decode(data.split(',', 1)[1])
            with open(f'{OUT}/_r33_astro_foto_{nombre}.png', 'wb') as f:
                f.write(png)
            print('toma', nombre, f'({len(png):,} B)')

        print('== ciclo leave() + re-launch (sospecha dispose de texturas) ==')
        rL = await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          if (!mod) return 'sin módulo';
          const ctrl = mod.controller || mod;
          try { ctrl.leave(); return 'leave ok'; }
          catch (e) { return 'leave err: ' + e.message; }
        }""")
        print('leave:', rL)
        await page.wait_for_timeout(800)
        await page.evaluate(
            """async () => { const G = window.__PP_GAME || window.__game;
             try { await G.champs.launch('estacion_orbital'); } catch (e) {} }""")
        await page.wait_for_timeout(4500)
        sala2 = await page.evaluate(MUESTREA)
        print('SALA (2.ª entrada):', json.dumps(sala2, ensure_ascii=False,
                                                indent=1))
        await page.evaluate("""() => {
          const G = window.__PP_GAME || window.__game;
          const mod = G.champs.moduleIfLoaded('estacion_orbital');
          const ctrl = mod.controller || mod;
          ctrl.serveTrigger();
        }""")
        await page.wait_for_timeout(2500)
        d2 = await page.evaluate(MUESTREA)
        print('DUELO (2.ª entrada):', json.dumps(d2, ensure_ascii=False))
        await page.screenshot(path=f'{OUT}/_r33_astro_duelo2.png')

        print('== errores de página ==')
        print(json.dumps(errs[:8], ensure_ascii=False, indent=1)
              if errs else 'ninguno')
        await browser.close()
        return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
