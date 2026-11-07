#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_r75_verifica.py — verifica EN VIVO la contención de la pantalla LOS
MODOS tras el arreglo r75: evalúa el cardWrap SERVIDO (extraído del propio
game.html) y replica el layout exacto de modeCard para las 6 tarjetas en
ES y EN, midiendo con measureText real. Además compila el fuente servido."""
import asyncio
import json
import re
import sys

from playwright.async_api import async_playwright

GAME = "/home/z/my-project/public/game.html"

TARJETAS = [
    # (etiqueta, w, h, título ES, sub ES, extra ES, título EN, sub EN, extra EN)
    ("PARTIDO", 480, 88, "PARTIDO", "Contra la CPU al mejor de 3",
     "PARTIDO · contra la CPU (3 niveles). Al mejor de 3 sets.",
     "MATCH", "vs the CPU · best of 3",
     "MATCH · against the CPU (3 levels). Best of 3 sets."),
    ("SUPERVIVENCIA", 480, 88, "SUPERVIVENCIA", "Aguanta el máximo de rallyes",
     "SUPERVIVENCIA · aguanta el máximo de rallyes seguidos.",
     "SURVIVAL", "Survive endless rallies",
     "SURVIVAL · survive as many consecutive rallies as you can."),
    ("MULTIJUGADOR", 480, 88, "MULTIJUGADOR", "Online con un código de 5 letras",
     "MULTIJUGADOR · online con un código de 5 letras.",
     "MULTIPLAYER", "Online with a 5-letter code",
     "MULTIPLAYER · online with a 5-letter code."),
    ("CAMPEONATOS", 480, 88, "CAMPEONATOS", "6 rivales con su historia",
     "CAMPEONATOS · 6 rivales con su historia. ¡Corona la OESTE!",
     "CHAMPIONSHIPS", "6 rivals, each with a story",
     "CHAMPIONSHIPS · 6 rivals with their own story. Crown the WEST!"),
    ("RANKING MUNDIAL", 300, 80, "RANKING MUNDIAL", "Compite con el mundo",
     "RANKING MUNDIAL · compite con jugadores de todo el mundo.",
     "WORLD RANKING", "Compete with the world",
     "WORLD RANKING · compete with players from everywhere."),
    ("ENTRENAR", 300, 80, "ENTRENAR", "5 áreas para tu técnica",
     "ENTRENAR · PRO TRAINING: 5 áreas para pulir tu técnica.",
     "TRAINING", "5 areas to polish technique",
     "TRAINING · PRO TRAINING: 5 areas to polish your technique."),
]

PODERES = ("PODERES: Mega Pala · Efecto · Imán · Portal · Clon — gatillo con la bola viva.",
           "POWERS: Mega Paddle · Spin · Magnet · Portal · Clone — trigger with a live ball.")


def extrae_funcion(src, nombre):
    """Extrae `function nombre(...) {...}` del fuente por apareamiento de llaves."""
    m = re.search(r"function " + nombre + r"\(", src)
    if not m:
        return None
    i = src.index("{", m.end() - 1)
    prof = 0
    for j in range(i, len(src)):
        if src[j] == "{":
            prof += 1
        elif src[j] == "}":
            prof -= 1
            if prof == 0:
                return src[m.start():j + 1]
    return None


JS = """(args) => {
  const cardWrapSrc = args[0], tarjetas = args[1], poderes = args[2];
  const cv = document.createElement('canvas');
  cv.width = 1408; cv.height = 768;
  const c = cv.getContext('2d');
  const fitFont = (cc, txt, size, weight, maxW, minSize) => {
    let s = size; const min = minSize || 15;
    cc.font = weight + ' ' + s + 'px system-ui, sans-serif';
    while (s > min && cc.measureText(txt).width > maxW) {
      s -= 1; cc.font = weight + ' ' + s + 'px system-ui, sans-serif';
    }
    return s;
  };
  eval(cardWrapSrc);
  const rep = [];
  let fallos = 0;
  for (const [lab, w, h, tES, sES, eES, tEN, sEN, eEN] of tarjetas) {
    for (const idi of ['ES', 'EN']) {
      const title = idi === 'ES' ? tES : tEN;
      const sub = idi === 'ES' ? sES : sEN;
      const extra = idi === 'ES' ? eES : eEN;
      const y = 0, tw = w - 86;
      const filaAlta = h >= 88;
      const tt = cardWrap(c, title, 21, '800', 14, tw, 1);
      const ts = cardWrap(c, sub, 15, '500', 10, tw, 1);
      const te = cardWrap(c, extra, 13, '600', 9, tw, 2);
      c.font = '800 ' + tt.size + 'px system-ui, sans-serif';
      const wT = c.measureText(tt.lines[0]).width;
      c.font = '500 ' + ts.size + 'px system-ui, sans-serif';
      const wS = c.measureText(ts.lines[0]).width;
      let wE = 0;
      for (const ln of te.lines) {
        c.font = '600 ' + te.size + 'px system-ui, sans-serif';
        wE = Math.max(wE, c.measureText(ln).width);
      }
      // métrica vertical real (ink) de cada fila pintada por modeCard
      const filas = [];
      filas.push({ y: y + (filaAlta ? 27 : 24), px: tt.size, t: 'titulo' });
      filas.push({ y: y + (filaAlta ? 50 : 42), px: ts.size, t: 'sub' });
      const n = te.lines.length;
      if (n === 2) {
        filas.push({ y: y + h - 26, px: te.size, t: 'extra1' });
        filas.push({ y: y + h - 13, px: te.size, t: 'extra2' });
      } else {
        filas.push({ y: y + h - 14, px: te.size, t: 'extra' });
      }
      let vOk = true, vDet = '';
      for (const f of filas) {
        c.font = (f.t === 'titulo' ? '800 ' : f.t === 'sub' ? '500 ' : '600 ')
          + f.px + 'px system-ui, sans-serif';
        const txt = f.t === 'titulo' ? tt.lines[0] : f.t === 'sub' ? ts.lines[0]
          : (f.t === 'extra' ? te.lines[0] : te.lines[f.t === 'extra1' ? 0 : 1]);
        const m = c.measureText(txt);
        const arriba = f.y - (m.actualBoundingBoxAscent || f.px * 0.7);
        const abajo = f.y + (m.actualBoundingBoxDescent || f.px * 0.25);
        if (arriba < y + 2 || abajo > y + h - 2) {
          vOk = false;
          vDet += f.t + '[' + Math.round(arriba) + '..' + Math.round(abajo) + '] ';
        }
      }
      const okH = wT <= tw && wS <= tw && wE <= tw;
      const ok = okH && vOk && tt.lines.length <= 1 && ts.lines.length <= 1 && te.lines.length <= 2;
      if (!ok) fallos++;
      rep.push({ lab: lab + '·' + idi, tw, wT: Math.round(wT * 10) / 10,
        wS: Math.round(wS * 10) / 10, wE: Math.round(wE * 10) / 10,
        lineasT: tt.lines.length, lineasS: ts.lines.length, lineasE: te.lines.length,
        sizeE: te.size, okH, vOk, ok });
    }
  }
  // wrap2 blindado: mitades de PODERES re-ajustadas a 312
  const pod = [];
  for (const txt of poderes) {
    fitFont(c, txt, 14, '600', 312, 12);
    let lineas;
    if (c.measureText(txt).width <= 312) { lineas = [txt]; }
    else {
      const sep = txt.lastIndexOf(' ', Math.ceil(txt.length / 2));
      lineas = [txt.slice(0, sep), txt.slice(sep + 1)];
    }
    let maxW = 0, minS = 99;
    for (const ln of lineas) {
      const s = fitFont(c, ln, 14, '600', 312, 9);
      minS = Math.min(minS, s);
      maxW = Math.max(maxW, c.measureText(ln).width);
    }
    pod.push({ n: lineas.length, maxW: Math.round(maxW * 10) / 10, minS, ok: maxW <= 312 });
  }
  return { rep, pod, fallos };
}"""


async def main():
    with open(GAME, "r", encoding="utf-8", errors="replace") as f:
        src = f.read()
    cw = extrae_funcion(src, "cardWrap")
    if not cw:
        print("✗ FALLO: cardWrap no encontrado en el fuente")
        sys.exit(1)
    # el fuente servido debe compilar entero (sintaxis)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 800, "height": 600})
        await page.goto("about:blank")
        # 1) sintaxis del fuente completo: cada <script> a .mjs y node --check
        #    (el script del juego es type=module: new Function no vale)
        import subprocess
        import tempfile
        scripts = re.findall(r"<script[^>]*>([\s\S]*?)</script>", src)
        ok_sint = True
        err_sint = ""
        n_chk = 0
        for cuerpo in scripts:
            if "cardWrap" not in cuerpo and len(cuerpo) < 100000:
                continue
            with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False) as tf:
                tf.write(cuerpo)
                ruta = tf.name
            r2 = subprocess.run(["node", "--check", ruta],
                                capture_output=True, text=True, timeout=60)
            n_chk += 1
            if r2.returncode != 0:
                ok_sint = False
                err_sint = r2.stderr[:300]
            try:
                import os
                os.unlink(ruta)
            except Exception:
                pass
        sintaxis = {"ok": ok_sint, "bloques": n_chk, "err": err_sint}
        chk1 = sintaxis.get("ok")
        print(("✓" if chk1 else "✗ FALLO") + f" sintaxis del fuente servido: {sintaxis}")
        res = await page.evaluate(JS, [cw, [list(t) for t in TARJETAS], list(PODERES)])
        await browser.close()
    fallos = res["fallos"]
    for r in res["rep"]:
        print(("  ✓ " if r["ok"] else "  ✗ FALLO: ")
              + f"{r['lab']:22s} tw={r['tw']} T={r['wT']}({r['lineasT']}l) "
              f"S={r['wS']}({r['lineasS']}l) E={r['wE']}({r['lineasE']}l @{r['sizeE']}px) "
              f"horiz={'ok' if r['okH'] else 'DESBORDA'} vert={'ok' if r['vOk'] else 'FUERA'}")
    for p in res["pod"]:
        print(("  ✓ " if p["ok"] else "  ✗ FALLO: ")
              + f"wrap2 PODERES: {p['n']} líneas, máx {p['maxW']} ≤ 312 (fuente min {p['minS']})")
    total = fallos + (0 if chk1 else 1) + sum(0 if p["ok"] else 1 for p in res["pod"])
    print(f"\nRESULTADO: {'TODO DENTRO ✓' if total == 0 else str(total) + ' FALLOS'}")
    sys.exit(1 if total else 0)


asyncio.run(main())
