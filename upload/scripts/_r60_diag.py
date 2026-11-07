#!/usr/bin/env python3
"""r60 · DIAGNÓSTICO EN VIVO (juego real headless) de las 3 incidencias del dueño:
  A) TUTORIAL: al entrar queda bloqueado/superpuesto con el menú y no es pulsable.
  B) TROQUELES: desaparecidos de «todos los escenarios» — ciclo real champDecor.
  C) ORBE etapa 4 (Wizard): nº de ladrillos servidos (esperado 1419)."""
import asyncio
import json
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

async def main():
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append("PAGEERROR: " + str(e)))
        page.on("console", lambda m: errors.append("CONSOLE: " + m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        await page.wait_for_timeout(1200)

        ok = await page.evaluate("() => !!window.__game && !!window.__game.champs")
        print("boot __game:", ok)
        if not ok:
            print("FALLO: sin __game"); return 1

        print("\n=== A · TUTORIAL: entrada por el banner del HUB (camino REAL) ===")
        a = await page.evaluate("""() => {
          const g = window.__game;
          g.menuPage = 'main';
          if (!g.menuOpen) g.toggleMenu();
          g.drawMenu();
          const rects = g.menuRects || [];
          const idx = rects.findIndex(r => r && r.id === 'tut:go');
          const pre = {
            menuOpen: g.menuOpen, idx_banner: idx,
            totalRects: rects.length,
          };
          if (idx >= 0) g.menuClick(idx);          // «pulsar» el banner de verdad
          const tut = window.__PP_TUT ? window.__PP_TUT.estado() : null;
          // geometría: panel del MENÚ vs panel del TUTORIAL
          const geo = {};
          try {
            const mg = g.menuGroup || g.menuMesh && g.menuMesh.parent;
            if (mg) {
              const p = new (mg.children[0].constructor.prototype.position.constructor)(0,0,0);
              mg.getWorldPosition(p);
              geo.menuPos = {x:+p.x.toFixed(2), y:+p.y.toFixed(2), z:+p.z.toFixed(2)};
              geo.menuVisible = mg.visible;
            }
          } catch (e) { geo.menuErr = String(e); }
          try {
            const any = g.scene || g.rig;
            geo.menuPage = g.menuPage;
            geo.calib = !!g.calib;
            geo.mode = g.mode;
            geo.rulesState = g.rules.state;
          } catch (e) {}
          return {pre, tut, geo, menuOpenTras: g.menuOpen};
        }""")
        print(json.dumps(a, indent=1, ensure_ascii=False))

        print("\n=== A2 · ¿sigue el menú abierto encima? (solape real) ===")
        a2 = await page.evaluate("""() => {
          const g = window.__game;
          // localizar el mesh del menú y el del tutorial y comparar alturas Y
          const out = {menuOpen: g.menuOpen, menuPage: g.menuPage};
          const tut = window.__PP_TUT.estado();
          out.tut = tut;
          // buscar el panel del tutorial (renderOrder 985) y el del menú
          let tutMesh = null, menuMesh = null;
          g.rig.traverse(o => { if (o.isMesh && o.renderOrder === 985) tutMesh = o; });
          g.scene.traverse(o => { if (o.isMesh && o.renderOrder === 985) tutMesh = tutMesh || o; });
          // el menú: mesh con textura canvas grande (el que recibe raycast de menú)
          try {
            const cand = g.menuMesh || (g.menuGroup && g.menuGroup.children[0]);
            if (cand) { menuMesh = cand; }
          } catch (e) {}
          const info = m => { if (!m) return null;
            const p = m.getWorldPosition(new m.position.constructor());
            const s = m.getWorldScale(new m.position.constructor());
            return {x:+p.x.toFixed(2), y:+p.y.toFixed(2), z:+p.z.toFixed(2),
                    sx:+s.x.toFixed(2), sy:+s.y.toFixed(2), vis: m.visible,
                    order: m.renderOrder}; };
          out.tutPanel = info(tutMesh);
          out.menuPanel = menuMesh ? info(menuMesh) : 'no_encontrado';
          return out;
        }""")
        print(json.dumps(a2, indent=1, ensure_ascii=False))
        # salir de la academia para las pruebas siguientes
        await page.evaluate("() => { try { window.__PP_TUT.stop({}); } catch (e) {} }")

        print("\n=== B · TROQUELES: ciclo real champDecor por campeonato ===")
        b = await page.evaluate("""async () => {
          const g = window.__game;
          const ids = ['oeste', 'locura', 'magia', 'valle_neon', 'estacion_orbital'];
          const out = {};
          for (const id of ids) {
            try {
              await g.champs.preload(id);
              g.exitHall();
              g.champs.leaveAll();
              g.champs.activeId = id;                    // activar el decorado
              // dejar respirar el update real (texturas async)
              for (let i = 0; i < 40; i++) {
                g.champDecor.update(0.05, performance.now() / 1000);
                await new Promise(r => setTimeout(r, 25));
              }
              const d = g.champDecor;
              const pieces = d.pieces.map(p => ({
                ready: p.ready, h: +p.h.toFixed(2), w: +p.w.toFixed(2),
                x: p.cfg.x, z: p.cfg.z,
              }));
              out[id] = {
                builtFor: d.builtFor, visible: d.group.visible,
                hijosGrupo: d.group.children.length, piezas: pieces,
                decorEnModulo: !!(g.champs.moduleIfLoaded(id) || {}).decor !== false
                  ? (() => { const m = g.champs.moduleIfLoaded(id);
                      return m && m.decor ? (m.decor.pieces || []).length : null; })()
                  : null,
              };
            } catch (e) { out[id] = {error: String(e)}; }
          }
          g.champs.leaveAll();
          return out;
        }""")
        print(json.dumps(b, indent=1, ensure_ascii=False))

        print("\n=== C · ORBE etapa 4 (Wizard): cfg servida ===")
        c = await page.evaluate("""async () => {
          await window.__game.champs.preload('magia');
          const m = window.__game.champs.moduleIfLoaded('magia');
          const src = await (await fetch('championships/magia/index.js')).text();
          const grab = re => { const r = src.match(re); return r ? r[1] : null; };
          return {
            brickSize_c: grab(/ORBE_COMPLEJO = \\s*\\{[^}]*brickSize:\\s*([0-9.]+)/s),
            radiusOuter_c: grab(/ORBE_COMPLEJO = \\s*\\{[^}]*radiusOuter:\\s*([0-9.]+)/s),
            radiusMid_c: grab(/ORBE_COMPLEJO = \\s*\\{[^}]*radiusMid:\\s*([0-9.]+)/s),
            radiusCore_c: grab(/ORBE_COMPLEJO = \\s*\\{[^}]*radiusCore:\\s*([0-9.]+)/s),
            tieneObjetosOrbe: !!(m),
          };
        }""")
        print(json.dumps(c, indent=1))

        await browser.close()

    print("\n=== ERRORES DE PÁGINA ===")
    for e in errors[:8]:
        print("  ·", e[:200])
    print(f"total errores JS: {len(errors)}")
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
