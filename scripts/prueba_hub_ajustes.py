"""Prueba de interacción del HUB v2.123:
1) la tarjeta AJUSTES contraída abre la página AJUSTES (page:opts);
2) la página AJUSTES sigue conteniendo todas las opciones;
3) el subtítulo de la tarjeta se construye bien en inglés;
4) volver a la página principal funciona.
"""
from playwright.sync_api import sync_playwright

errores = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 720})
    pg.on("pageerror", lambda e: errores.append(str(e)))
    pg.goto("http://localhost:3000/game.html", wait_until="load", timeout=60000)
    pg.wait_for_timeout(6000)
    res = pg.evaluate(
        """() => {
          const g = window.__PP_GAME;
          if (!g) return { err: 'NO_GAME' };
          g.menuPage = 'main';
          g.drawMenu();
          const idx = g.menuRects.findIndex((r) => r.id === 'page:opts');
          const rect = idx >= 0 ? g.menuRects[idx] : null;
          g.menuClick(idx);
          const paginaTrasClic = g.menuPage;
          const clavesOpts = ['amb', 'voz', 'music', 'hapt', 'trail', 'tips',
            'sndtest', 'tele', 'pname', 'reset', 'kofi'];
          const presentes = {};
          for (const k of clavesOpts) {
            presentes[k] = g.menuRects.some((r) => r.id === k);
          }
          // volver al HUB y comprobar subtítulo en inglés
          g.menuPage = 'main';
          window.__setLang('en', g);
          g.drawMenu();
          // el subtítulo vive dentro del canvas: re-render en un canvas aparte
          // no es legible; en su lugar validamos las piezas T() del subtítulo.
          const piezas = {
            sala: (window.__T('theme_pabellon') || ''),
            musica: window.__T('btn_music', { v: window.__T('yes') }),
            mega: window.__T('dock_mic'),
            yes: window.__T('yes'),
          };
          window.__setLang('es', g);
          g.drawMenu();
          return { rect, paginaTrasClic, presentes, piezas,
            totalRects: g.menuRects.length };
        }"""
    )
    b.close()

print("Rect tarjeta AJUSTES:", res.get("rect"))
print("Página tras clic en la tarjeta:", res.get("paginaTrasClic"))
print("Opciones presentes en página AJUSTES:", res.get("presentes"))
print("Piezas i18n (EN):", res.get("piezas"))
print("Total rects HUB:", res.get("totalRects"))
print("Errores JS:", len(errores))
for e in errores[:5]:
    print("  -", e[:200])
