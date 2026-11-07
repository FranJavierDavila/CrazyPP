#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r63 · v3.6.55-SDK6 · FASE 57 «La academia cierra bien» — QA del arreglo
del bug del dueño: «la última pantalla del tutorial se queda fija y no hay
forma de eliminarla de pantalla, con lo que es imposible seguir o jugar».

CAUSA RAÍZ: stop() anulaba G ANTES de teardownPanel() — y teardownPanel
necesita G.rig para QUITAR el panel de la escena. El if cortocircuitaba, el
remove() no corría y el panel quedaba HUÉRFANO y VISIBLE delante del jugador
para siempre (el módulo ya no lo controla: activo=false). La QA r59 no lo
vio porque estado() mira el closure del módulo, no el GRAFO DE ESCENA.

FIX r63 (doble cinturón): (1) el panel se desmonta PRIMERO, con G vivo;
(2) teardownPanel gana un fallback por grp.parent que quita el panel de
CUALQUIER padre si G no estuviera disponible.

Uso: python3 scripts/qa_r63_v3655.py        (servidor dev en :3000)
"""
import asyncio
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


AGUJAS = [
    ("fix: el panel se desmonta CON G vivo (orden crítico)",
     "    teardownPanel();\n    G = null;\n    gm.tutV1 = null;"),
    ("fix: fallback por grp.parent en teardownPanel",
     "else if (grp && grp.parent) grp.parent.remove(grp);"),
    ("fix: nota de la ronda en el cierre",
     "r63 \u00b7 ORDEN CR\u00cdTICO (bug del due\u00f1o"),
]

NEGATIVAS = [
    ("fix: el orden viejo (G=null ANTES de desmontar) retirado",
     "    G = null;\n    teardownPanel();\n    gm.tutV1 = null;"),
]

MECANICA = """async () => {
  const out = [];
  const g = window.__game;
  // huella del panel en el GRAFO DE ESCENA (no en el closure del módulo):
  // Group en y=1.52 · z=-0.86 con hijos — lo que el jugador VE delante
  const buscaPanel = () => g.rig.children.filter(ch =>
    ch.type === 'Group' && Math.abs(ch.position.y - 1.52) < 0.01 &&
    Math.abs(ch.position.z + 0.86) < 0.01 && ch.children.length > 0);

  // ---------- SALIDA 1 · gatillo del paso 8 (aJugar + sello) ----------
  window.__PP_TUT.start(g);
  await new Promise(r => setTimeout(r, 250));
  out.push({ ok: buscaPanel().length === 1 && window.__PP_TUT.estado().panelVisible,
             lab: 'academia: el panel nace EN EL RIG y visible (1 grupo)' });
  window.__PP_TUT.stop({ aJugar: true, done: true });
  await new Promise(r => setTimeout(r, 200));
  let sello = '0';
  try { sello = localStorage.getItem('pp_tut_done') || '0'; } catch (e) { /* */ }
  out.push({ ok: buscaPanel().length === 0,
             lab: 'academia: GATILLO del paso 8 → el panel DESAPARECE del grafo (0 grupos)' });
  out.push({ ok: window.__PP_TUT.estado().activo === false,
             lab: 'academia: el módulo queda inactivo tras la salida' });
  out.push({ ok: sello === '1',
             lab: 'academia: el sello pp_tut_done queda grabado (1)' });
  out.push({ ok: g.calib === false,
             lab: 'academia: calib limpio (fuera del ajuste)' });
  out.push({ ok: g.rules.state === 'serve' || g.rules.state === 'rally',
             lab: 'academia: el juego queda JUGABLE (state ' + g.rules.state + ')' });

  // ---------- SALIDA 2 · B/Y (skip sin sello) ----------
  try { localStorage.removeItem('pp_tut_done'); } catch (e) { /* */ }
  window.__PP_TUT.start(g);
  await new Promise(r => setTimeout(r, 250));
  window.__PP_TUT.stop({ done: false });
  await new Promise(r => setTimeout(r, 200));
  sello = '1';
  try { sello = localStorage.getItem('pp_tut_done') || '0'; } catch (e) { /* */ }
  out.push({ ok: buscaPanel().length === 0,
             lab: 'academia: B/Y (saltar) → el panel DESAPARECE del grafo' });
  out.push({ ok: sello === '0',
             lab: 'academia: saltar NO graba el sello (sólo jugar ya)' });

  // ---------- SALIDA 3 · idempotencia (doble arranque, sin duplicados) ----------
  window.__PP_TUT.start(g);
  await new Promise(r => setTimeout(r, 150));
  window.__PP_TUT.start(g);
  await new Promise(r => setTimeout(r, 150));
  out.push({ ok: buscaPanel().length === 1,
             lab: 'academia: doble arranque NO duplica el panel (1 grupo)' });
  window.__PP_TUT.stop({ aJugar: true, done: true });
  await new Promise(r => setTimeout(r, 150));
  out.push({ ok: buscaPanel().length === 0,
             lab: 'academia: la salida del doble arranque también limpia (0 grupos)' });

  // ---------- SIN FANTASMAS: rig sin residuos del tutorial ----------
  const residuo = g.rig.children.filter(ch => ch.name === 'ppTutPanel').length;
  out.push({ ok: residuo === 0,
             lab: 'academia: cero residuos del panel en el rig' });
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
        await page.wait_for_timeout(1000)

        print("--- 1 · AGUJAS r63 en el juego servido ---")
        src = await page.content()
        for label, aguja in AGUJAS:
            chk(aguja in src, label)

        print("--- 2 · NEGATIVAS (el orden viejo retirado) ---")
        for label, aguja in NEGATIVAS:
            chk(aguja not in src, label)

        print("--- 3 · MECÁNICA REAL headless (grafo de escena) ---")
        filas = await page.evaluate(MECANICA)
        for fila in filas:
            chk(fila["ok"], fila["lab"])

        await browser.close()

    print("--- ERRORES DE PÁGINA ---")
    chk(len(errors) == 0, "sin errores JS durante toda la batería")
    for e in errors[:6]:
        print("  ·", e[:200])

    print(f"\nRESULTADO: {ok} OK · {fails} fallos")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
