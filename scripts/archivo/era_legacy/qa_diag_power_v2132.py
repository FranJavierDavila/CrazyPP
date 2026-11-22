#!/usr/bin/env python3
"""QA V2.132 · DIAGNÓSTICO powers — ¿por qué no saltan en el casco?

Experimento: boot → duelo → (a) dormir 6 s reales y leer _powerCd (¿baja el
RAF?), (b) bucle de puntos con ticks del MÓDULO entre ellos (¿sale el poder?).
"""
import json, time
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?champ=estacion_orbital"
errors = []

def js(page, expr):
    try:
        return page.evaluate(expr)
    except Exception as e:
        return {"__err": str(e)[:300]}

with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    page = browser.new_context(viewport={"width": 1280, "height": 720}).new_page()
    page.on("console", lambda m: errors.append(m.text[:200]) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append("PAGEERROR " + str(e)[:200]))

    page.add_init_script("window.__pp2DPlay = true; window.__PP_KEEP_FRAMEBUFFER = true;")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    for _ in range(45):
        s = js(page, "!!(window.__PP_GAME&&window.__PP_GAME.champs&&window.__PP_GAME.champs.mod&&window.__PP_GAME.champs.mod.controller)")
        if s is True:
            break
        time.sleep(1)

    # A · trigger → duelo
    print("A-trigger:", js(page, """(() => { const G=window.__PP_GAME,C=G.champs;
      if (G.rules.state !== 'champtest') return {__err:'rules='+G.rules.state};
      C.serveTrigger(0);
      const c = C.mod.controller;
      return { st: c.state, powerCd: c._powerCd }; })()"""))

    # A2 · dormir 6 s REALES (RAF del juego corriendo) → ¿baja powerCd?
    time.sleep(6)
    print("A2-tras-6s-reales:", js(page, """(() => { const G=window.__PP_GAME,c=G.champs.mod.controller;
      return { powerCd: +c._powerCd.toFixed(2), st: c.state, rules: G.rules.state }; })()"""))

    # B · bucle de 30 puntos con ticks del MÓDULO entre puntos (prob REAL)
    print("B-bucle:", js(page, """(() => {
      const G = window.__PP_GAME, C = G.champs, c = C.mod.controller;
      const res = { puntos: 0, warns: [], acts: [], efectos: [] };
      const realQ = c._quizasPoder.bind(c); let tiradas = 0;
      c._quizasPoder = () => { tiradas++; return realQ(); };
      for (let i = 0; i < 30 && c.state === 'duelo'; i++) {
        G.processIntents(G.rules.applyPoint(i % 3 ? 'rival' : 'player', 'out'));
        res.puntos++;
        // ticks del módulo: 2.5 s de juego en pasos de 50 ms (RAF simulado)
        for (let k = 0; k < 50; k++) {
          G.processIntents(G.rules.update(0.05));
          try { C.mod.update(0.05); } catch (e) { res.efectos.push('UPD_ERR:' + e.message); break; }
          if (c._warn && !res.warns.includes(c._warn.def.name)) res.warns.push(c._warn.def.name);
          if (c._act && !res.acts.includes(c._act.def.name)) {
            res.acts.push(c._act.def.name);
            // ¿el efecto tiene objetos visibles? (confeti/rocas/haz/motas)
            const vis = { beam: !!(c.beam && c.beam.visible), motas: (c.motas||[]).filter(m=>m.s.material.opacity>0).length,
                          confeti: !!(c._poolConfeti||[]).some(p=>p.on), rocas: (c.rocas||[]).filter(r=>r.on).length };
            res.efectos.push(c._act.def.name + '→' + JSON.stringify(vis));
          }
        }
      }
      c._quizasPoder = realQ;
      return { ...res, tiradas, powerCd: +c._powerCd.toFixed(1), st: c.state }; })()"""))

    browser.close()

print("\nERRORES:", *errors[-6:], sep="\n  ") if errors else print("\nSin errores de consola")
