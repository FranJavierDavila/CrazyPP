#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r75_diag.py — mide EN VIVO (measureText real) los desbordes de la
pantalla LOS MODOS (tutorial) ANTES del arreglo. Sólo diagnóstico."""
import asyncio
import json

from playwright.async_api import async_playwright

CADENAS = {
    "tut_s6_m1 (PARTIDO)": ("PARTIDO · contra la CPU (3 niveles). Al mejor de 3 sets.", 394),
    "tut_s6_m2 (SUPERV.)": ("SUPERVIVENCIA · aguanta el máximo de rallyes seguidos.", 394),
    "tut_s6_m3 (MULTI)": ("MULTIJUGADOR · online con un código de 5 letras.", 394),
    "tut_s7_m1 (CAMPEON.)": ("CAMPEONATOS · 6 rivales con su historia. ¡Corona la OESTE!", 394),
    "tut_s7_m2 (RANKING)": ("RANKING MUNDIAL · compite con jugadores de todo el mundo.", 214),
    "tut_s7_m3 (ENTRENAR)": ("ENTRENAR · PRO TRAINING: 5 áreas para pulir tu técnica.", 214),
    "EN s6_m1 (MATCH)": ("MATCH · against the CPU (3 levels). Best of 3 sets.", 394),
    "EN s6_m2 (SURV.)": ("SURVIVAL · survive as many consecutive rallies as you can.", 394),
    "EN s6_m3 (MULTI)": ("MULTIPLAYER · online with a 5-letter code.", 394),
    "EN s7_m1 (CHAMP.)": ("CHAMPIONSHIPS · 6 rivals with their own story. Crown the WEST!", 394),
    "EN s7_m2 (RANKING)": ("WORLD RANKING · compete with players from everywhere.", 214),
    "EN s7_m3 (TRAINING)": ("TRAINING · PRO TRAINING: 5 areas to polish your technique.", 214),
    "sub RANKING (tut_mod_r)": ("Compite con el mundo", 214),
    "sub ENTRENAR (tut_mod_t)": ("5 áreas para tu técnica", 214),
    "title RANKING": ("RANKING MUNDIAL", 214),
    "title ENTRENAR": ("ENTRENAR", 214),
    "PODERES ES (líneas wrap2)": ("PODERES: Mega Pala · Efecto · Imán · Portal · Clon — gatillo con la bola viva.", 312),
}

JS = """(cadenas) => {
  const cv = document.createElement('canvas');
  cv.width = 10; cv.height = 10;
  const c = cv.getContext('2d');
  const mide = (txt, px, w, min) => {
    let s = px;
    c.font = '600 ' + s + 'px system-ui, sans-serif';
    while (s > min && c.measureText(txt).width > w) {
      s -= 1;
      c.font = '600 ' + s + 'px system-ui, sans-serif';
    }
    return { ancho: Math.round(c.measureText(txt).width * 10) / 10, sizeFinal: s };
  };
  const out = {};
  for (const [k, [txt, w]] of Object.entries(cadenas)) {
    const esExtra = k.indexOf('(') > 0 && (k.indexOf('tut_s') === 0 || k.indexOf('EN s') === 0);
    out[k] = esExtra ? mide(txt, 13, w, 10) : mide(txt, 21, w, 10);
  }
  return out;
}"""


async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 800, "height": 600})
        await page.goto("about:blank")
        res = await page.evaluate(JS, {k: list(v) for k, v in CADENAS.items()})
        await browser.close()
    print(f"{'cadena':34s} {'dispo':>6s} {'ancho':>8s} {'px final':>8s}  estado")
    for k, (txt, disp) in CADENAS.items():
        r = res[k]
        mal = r["ancho"] > disp
        print(f"{k:34s} {disp:6d} {r['ancho']:8.1f} {r['sizeFinal']:8d}  "
              + ("✗ DESBORDA" if mal else "✓ cabe")
              + ("" if r["sizeFinal"] > 10 else "  (min 10 agotado)" if mal else ""))


asyncio.run(main())
