"""Prueba del MAREO TOTAL con control total del azar.

`window.__PP_ARCADE_DATA.powerTrigger` (lo lee La Locura) se parchea con
chance 1.1 y warn 0.5; Math.random devuelve siempre 0.80 → el índice de
poder cae SIEMPRE en 'giro'. Se fuerza un rally vivo y se muestrea la
rotación del rig durante el vaivén.
"""
import json

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(6000)

    pg.evaluate("""() => {
      window.__pp2DPlay = true;
      Math.random = () => 0.80;            // índice (0.8*4)|0 = 3 → 'giro'
    }""")
    pg.evaluate("() => window.__PP_GAME.champs.launch('locura')")
    pg.wait_for_timeout(1500)
    # parchear el trigger DESPUÉS del launch (el módulo leyó data al init):
    pg.evaluate("""() => {
      const d = window.__PP_ARCADE_DATA;
      if (d) d.powerTrigger = Object.assign({}, d.powerTrigger,
        { chance: 1.1, warn: 0.5, cooldown: 0, minRallyHits: 0 });
      // el CTRL capturó this.data por referencia: la mutación vale
    }""")
    pg.evaluate("""() => {
      const g = window.__PP_GAME;
      g.rules.state = 'rally';
      g.rules.rallyHits = 3;
      if (g.ball && g.ball.vel) g.ball.vel.set(0, 1.5, 1.2);
      window.__mant = setInterval(() => {
        const gg = window.__PP_GAME;
        if (gg.rules.state !== 'point' && gg.rules.state !== 'over') {
          gg.rules.state = 'rally';
        }
        gg.rules.rallyHits = Math.max(gg.rules.rallyHits | 0, 3);
        if (gg.ball && gg.ball.vel && gg.ball.vel.z < 0.2) {
          gg.ball.vel.set(0, 1.2, 1.0);
        }
      }, 150);
    }""")

    datos = pg.evaluate("""async () => {
      const g = window.__PP_GAME;
      const out = [];
      for (let i = 0; i < 90; i++) {
        out.push({ t: +(i * 0.1).toFixed(1),
          y: +g.rig.rotation.y.toFixed(4), z: +g.rig.rotation.z.toFixed(4),
          msg: String(g.rules.message || '').slice(0, 28) });
        await new Promise((r) => setTimeout(r, 100));
      }
      return out;
    }""")
    pg.evaluate("() => clearInterval(window.__mant)")
    b.close()

base_y = datos[0]["y"]
amp_y = max(abs(m["y"] - base_y) for m in datos)
msgs = []
for m in datos:
    if m["msg"] and (not msgs or msgs[-1][1] != m["msg"]):
        msgs.append((m["t"], m["msg"]))

print(f"Amplitud yaw observada: {amp_y:.4f} rad ({amp_y * 57.3:.1f}°)")
print("Mensajes del árbitro (t, texto):")
for t, m in msgs[:10]:
    print(f"  t={t}s · {m}")
print("Muestras clave:", json.dumps([datos[5], datos[15], datos[30], datos[45]], ensure_ascii=False))
print("VEREDICTO:", "EL MUNDO SE TAMBALEA" if amp_y > 0.05 else "SIN MOVIMIENTO: BUG DE MAREO CONFIRMADO")
print("Errores JS:", len(errs))
for e in errs[:5]:
    print("  -", e[:180])
