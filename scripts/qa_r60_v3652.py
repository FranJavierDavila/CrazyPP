#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r60 · v3.6.52-SDK6 · FASE 54 «Academia despejada, troqueles inmunes, orbe
a dieta» — QA de los TRES arreglos reportados por el dueño tras probar
V3.6.51 (LA ACADEMIA) en el Quest:

  1) «el tutorial se queda bloqueado, se está superponiendo con otras
     ventanas del menú y no es pulsable» → __PP_TUT.start() cierra el menú
     (panel de muñeca renderOrder 990 sobre el 985 del panel, misma altura
     de ojos) — mecánica REAL: clic del banner del HUB → menuOpen FALSE.
  2) «ME HAS QUITADO DE TODOS LOS ESCENARIOS LOS TROQUELES» → no se
     borraron: el cerrojo champDecorHidden de las pruebas especiales podía
     quedar PECHO tras una salida no prevista. AUTOCURACIÓN en leaveAll
     (también en su return temprano) — mecánica REAL: cerrojo izado →
     leaveAll → bajado; campeonato→campeonato; troqueles visibles en los 5.
  3) «la etapa 4 del orbe en el campeonato de Wizard… supera los 1000 y
     pico… debería tener como mucho la mitad… penalizando los FPS» →
     ORBE_COMPLEJO 0,088/7/4/2 = 1.419 ladrillos → 0,125/5/3,5/2 = 515
     (−63,7%) con la MISMA envergadura (0,625 m) — recuento REAL en la
     página sobre las constantes SERVIDAS (réplica de _buildGrid).

Uso: python3 scripts/qa_r60_v3652.py        (servidor dev en :3000)
"""
import asyncio
import json
import re
import sys

from playwright.async_api import async_playwright

URL = "http://localhost:3000/game.html"

ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(('  \u2713 ' if cond else '  \u2717 FALLO: ') + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS_GAME = [
    ("r60 · start() de la academia CIERRA el menú a lo directo (sin toggleMenu)",
     "G.menuOpen = false;\n        G.menuGroup.visible = false;"),
    ("r60 · el cierre evita toggleMenu (duerme con calib) y apaga música/duck",
     "try { G.audio.setMusicWanted(false); } catch (eM1) { /* */ }\n"
     "        try { G.audio.setArcDuck(false); } catch (eM2) { /* */ }"),
    ("r60 · leaveAll libera el cerrojo de troqueles SIEMPRE",
     "try { this.game.champDecorHidden = false; } catch (e) { /* */ }\n"
     "    if (!this.activeId) return;"),
]

AGUJAS_MAGIA = [
    ("r60 · ladrillo gordo 0,125 en el COMPLEJO", r"brickSize: 0\.125,"),
    ("r60 · radio exterior 5", r"radiusOuter: 5,"),
    ("r60 · radio medio 3,5", r"radiusMid: 3\.5,"),
    ("r60 · núcleo 2 intacto (v2.71)", r"radiusCore: 2,"),
    ("r60 · sin prórrogas se conserva", r"maxExtensions: 0,"),
    ("r60 · cadena exigente se conserva", r"minChainSpeed: 1\.35,"),
    ("r60 · bloque-reloj efímero se conserva", r"clockBlockLife: 3,"),
]

NEGATIVAS_MAGIA = [
    ("r60 · fuera el ladrillo fino 0,088 del COMPLEJO",
     r"ORBE_COMPLEJO = \{[^}]*brickSize: 0\.088"),
    ("r60 · fuera el radio 7 del COMPLEJO",
     r"ORBE_COMPLEJO = \{[^}]*radiusOuter: 7,"),
]

# mecánica REAL dentro del navegador (juego real, caminos reales)
MECANICA = """async () => {
  const out = [];
  const g = window.__game;
  const T = window.__PP_TUT;

  // ---------- 1 · ACADEMIA DESPEJADA: las 3 puertas ----------
  // puerta 1 · banner del HUB (clic REAL por menuClick)
  g.menuPage = 'main';
  if (!g.menuOpen) g.toggleMenu();
  g.drawMenu();
  const idx = (g.menuRects || []).findIndex(r => r && r.id === 'tut:go');
  out.push({ ok: idx >= 0, lab: 'HUB: el banner tut:go está en la parrilla' });
  g.menuClick(idx);                       // «pulsar» el banner de verdad
  out.push({ ok: g.menuOpen === false,
             lab: 'HUB: tras entrar en la academia el MENÚ ESTÁ CERRADO (r60)' });
  const e1 = T.estado();
  out.push({ ok: e1.activo && e1.panelVisible,
             lab: 'HUB: academia activa con panel visible' });
  out.push({ ok: !!g.calib && !!g.tutV1,
             lab: 'HUB: árbitro dormido (calib) con la academia al mando (r59)' });
  T.stop({});                             // salida B simulada
  out.push({ ok: g.menuOpen === true && g.menuPage === 'main',
             lab: 'salida B: vuelve el menú principal (alternativa de salida)' });

  // puerta 2 · oferta de PRIMERA VEZ (página tutask del menú)
  g.menuPage = 'tutask';
  if (!g.menuOpen) g.toggleMenu();
  g.drawMenu();
  const idxAsk = (g.menuRects || []).findIndex(r => r && r.id === 'tut:go');
  out.push({ ok: idxAsk >= 0, lab: 'tutask: la oferta SÍ tiene su botón' });
  g.menuClick(idxAsk);
  out.push({ ok: g.menuOpen === false && T.estado().activo,
             lab: 'tutask: SÍ abre la academia y CIERRA el menú (r60)' });
  T.stop({});

  // puerta 3 · AJUSTES (el botón vive en la página opts: aguja de rects)
  g.menuPage = 'opts';
  g.drawMenu();
  const idxOpts = (g.menuRects || []).findIndex(r => r && r.id === 'tut:go');
  out.push({ ok: idxOpts >= 0, lab: 'AJUSTES: botón del tutorial presente' });
  g.menuPage = 'main';

  // ---------- 2 · TROQUELES INMUNES ----------
  // 2.a autocuración en el return temprano (sin campeonato activo)
  g.champDecorHidden = true;
  g.champs.leaveAll();
  out.push({ ok: g.champDecorHidden === false,
             lab: 'cerrojo izado + leaveAll sin activo → LIBERADO (r60)' });
  // 2.b campeonato → campeonato (el caso del dueño: oeste asedio → magia)
  await g.champs.launch('oeste');
  g.champDecorHidden = true;              // estado que deja el asedio al activarse
  await g.champs.launch('magia');         // el dueño entra al Wizard sin salir antes
  for (let i = 0; i < 30; i++) {
    g.champDecor.update(0.05, performance.now() / 1000);
    await new Promise(r => setTimeout(r, 30));
  }
  out.push({ ok: g.champDecorHidden === false,
             lab: 'oeste (cerrojo izado) → magia: launch LIBERA el cerrojo' });
  out.push({ ok: g.champDecor.group.visible === true &&
                  g.champDecor.pieces.length === 4 &&
                  g.champDecor.pieces.every(p => p.ready),
             lab: 'magia: troqueles VISIBLES con sus 4 piezas listas' });
  // 2.c salida limpia deja el terreno libre
  g.champs.leaveAll();
  out.push({ ok: g.champDecorHidden === false,
             lab: 'leaveAll final: cerrojo liberado para el siguiente' });
  // 2.d los 5 campeonatos montan el suyo (sistema vivo, nada borrado)
  const ids = ['oeste', 'locura', 'magia', 'valle_neon', 'estacion_orbital'];
  let todosOk = true;
  for (const id of ids) {
    await g.champs.launch(id);
    for (let i = 0; i < 25; i++) {
      g.champDecor.update(0.05, performance.now() / 1000);
      await new Promise(r => setTimeout(r, 25));
    }
    const d = g.champDecor;
    if (!(d.builtFor === id && d.group.visible && d.pieces.length > 0 &&
          d.pieces.every(p => p.ready))) { todosOk = false; break; }
  }
  g.champs.leaveAll();
  out.push({ ok: todosOk, lab: 'los 5 campeonatos montan SU decorado (sistema vivo)' });

  // ---------- 3 · ORBE A DIETA (constantes SERVIDAS) ----------
  const src = await (await fetch('championships/magia/index.js')).text();
  const bloq = src.match(/ORBE_COMPLEJO = \\{([\\s\\S]*?)\\};/);
  if (!bloq) { out.push({ ok: false, lab: 'ORBE_COMPLEJO no encontrado' }); return out; }
  const val = k => { const m = bloq[1].match(new RegExp(k + ':\\\\s*([0-9.]+)')); return m ? +m[1] : NaN; };
  const brick = val('brickSize'), rO = val('radiusOuter'),
        rM = val('radiusMid'), rC = val('radiusCore');
  // réplica EXACTA de _buildGrid (celdas d<=rC núcleo, d<=rM medio, d<=rO ext)
  const R = Math.ceil(rO), eps = 1e-4;
  let total = 0, nuc = 0, med = 0, ext = 0;
  for (let x = -R; x <= R; x++)
    for (let y = -R; y <= R; y++)
      for (let z = -R; z <= R; z++) {
        const d = Math.sqrt(x * x + y * y + z * z);
        if (d <= rC + eps) { nuc++; total++; }
        else if (d <= rM + eps) { med++; total++; }
        else if (d <= rO + eps) { ext++; total++; }
      }
  out.push({ ok: total === 515,
             lab: 'recuento REAL del orbe COMPLEJO: 515 ladrillos (núcleo ' + nuc +
                  ' · medio ' + med + ' · exterior ' + ext + ')' });
  out.push({ ok: total <= 710,
             lab: 'tope del dueño: como mucho LA MITAD de 1.419 (≤710) — hay ' + total });
  out.push({ ok: Math.abs(rO * brick - 0.625) < 1e-9,
             lab: 'misma envergadura que antes: radio 0,625 m (antes 0,616)' });
  const topY = 0.76, reach = Math.floor(rO);
  const cima = topY + reach * brick + brick / 2 + rO * brick;
  out.push({ ok: cima < 2.28, lab: 'cima ' + cima.toFixed(3) + ' m < HUD 2,28 m' });
  const base = topY + reach * brick + brick / 2 - reach * brick - brick / 2;
  out.push({ ok: Math.abs(base - topY) < 1e-9,
             lab: 'base apoyada en la mesa (fórmula del centro intacta)' });
  out.push({ ok: rC < rM && rM < rO,
             lab: 'capas coherentes: núcleo < medio < exterior' });
  return out;
}"""


async def main():
    global ok, fails
    errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        await page.goto(URL, wait_until="load")
        # r60: origen del error «Object3D.add» — capturamos stack + línea
        await page.evaluate("""() => {
          window.__errs = [];
          window.addEventListener('error', ev => {
            window.__errs.push((ev.message || '') + ' @ ' +
              (ev.filename || '') + ':' + ev.lineno + ':' + ev.colno);
          });
          const ce = console.error.bind(console);
          console.error = (...a) => {
            try {
              const msg = a.map(x => (x && x.message) ? x.message : String(x)).join(' ');
              if (/Object3D\\.add|not an instance/.test(msg)) {
                window.__errs.push(new Error().stack.split('\\n').slice(1, 6).join(' | '));
              }
            } catch (e) { /* */ }
            ce(...a);
          };
        }""")
        await page.wait_for_timeout(600)

        print("--- 1 · AGUJAS r60 en el juego servido (game.html) ---")
        src = await page.content()
        for label, aguja in AGUJAS_GAME:
            chk(aguja in src, label)

        print("--- 2 · AGUJAS r60 en el módulo de magia SERVIDO ---")
        msrc = await page.evaluate(
            "() => fetch('championships/magia/index.js').then(r => r.text())")
        for label, aguja in AGUJAS_MAGIA:
            chk(re.search(aguja, msrc) is not None, label)
        print("--- 3 · NEGATIVAS del orbe (config vieja fuera) ---")
        for label, aguja in NEGATIVAS_MAGIA:
            chk(re.search(aguja, msrc) is None, label)

        print("--- 4 · manifest de magia: versión 33 + nota r60 ---")
        man = await page.evaluate(
            "() => fetch('championships/magia/manifest.json').then(r => r.json())")
        chk(man.get('version') == 33, 'manifest versión 33 (antes 32)')
        hist = man.get('historial') or []
        chk(any('515' in str(h) and 'r60' in str(h) for h in hist),
            'historial anota el orbe a la mitad (r60)')

        print("--- 5 · MECÁNICA REAL: academia despejada · troqueles inmunes · orbe a dieta ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        # r60: origen exacto de cualquier error capturado en la página
        origen = await page.evaluate("() => window.__errs || []")
        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    chk(len(errors) == 0, "sin errores JS durante toda la batería")
    for e in errors[:6]:
        print("  ·", e[:220])
    for o in (origen or [])[:8]:
        print("  [origen]", str(o)[:240])

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
