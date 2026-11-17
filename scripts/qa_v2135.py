#!/usr/bin/env python3
"""QA V2.135 · carteles de NORMAS con el arte del artista (clown/wizard/forajido).

Comprueba, por la ruta natural (showInstrucciones con los textos REALES):
  A) las 3 pieles precargan y se usan (arte=true, skin=<tema>)
  B) TODO el texto queda DENTRO del hueco interior del cartel
     (diff por píxel contra el arte escalado por el propio navegador)
  C) tamaño de fuente >= 19 px del lienzo (legibilidad) y columnas correctas
  D) piel «estacion» sin cambios (fallback dibujado intacto)
  E) botón EMPEZAR (ruta wait=true): mesh hijo, textura pintada, raycast seguro
  F) render in-situ: screenshot del panel sobre la escena 2D
  G) smoke de los 4 campeonatos sin pageerrors
"""
import base64
import io
import json
import time

from PIL import Image
from playwright.sync_api import sync_playwright

BASE = "http://localhost:3000"
OUT = "/home/z/my-project/scripts/out_v2135"

TEXTOS = {
    "locura": ("PRUEBA · ARKANOID LOCO", [
        "En lugar de mesa hay un MURO DE LADRILLOS: golpea la bola con las PALAS para arrancar ladrillos.",
        "Tienes 2 MINUTOS y 5 VIDAS (saques). Cada ladrillo roto suma; el rebote es real, ¡calcula los ángulos!",
        "Al avanzar tendrás una PISTOLA DE RAYOS en la mano libre: apunta y dispara a los ladrillos que la bola no alcanza.",
        "Alarma a los últimos 10 segundos: ¡da lo mejor de ti!",
    ]),
    "magia": ("PRUEBA · EL ORBE MÁGICO", [
        "Una ESFERA de bloques mágicos flota ante ti: golpéala con la BOLA usando las PALAS para romper sus bloques.",
        "Se rompe por CAPAS: primero la corteza, luego el interior… hasta apagar el NÚCLEO que brilla.",
        "Tendrás tiempo extra y una PISTOLA MÁGICA en la mano libre para rematar los bloques que la bola no alcanza.",
        "En la versión COMPLEJA el orbe gira y se protege más: ¡calcula bien los ángulos!",
    ]),
    "oeste": ("ASEDIO AL ESCONDITE", [   # el texto MÁS LARGO (5 entradas)
        "Golpea con las PALAS las bolas-bomba hacia las FACHADAS del pueblo.",
        "Cada IMPACTO rompe la madera; acierta en la DIANA con faro dorado para DESTAPAR al forajido escondido.",
        "Cuando salga, DISPÁRALE AL CORAZÓN con el revólver de la mano libre… pero corre: te disparará en 1 segundo.",
        "Caza la ESTRELLA DEL SHERIFF con una bomba o con el revólver: destapa al forajido y regala +12 s de reloj.",
        "3 OLEADAS de 2 minutos. Cuidado con la DINAMITA escondida: dale con una bola y salta por los aires.",
    ]),
}

FALLOS = []


def chk(nombre, cond, detalle=""):
    print(f"  [{'OK' if cond else 'FALLO'}] {nombre}{(' — ' + detalle) if detalle else ''}",
          flush=True)
    if not cond:
        FALLOS.append(f"{nombre}: {detalle}")


def espera_boot(page, timeout=40):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            if page.evaluate("!!window.__PP_GAME"):
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def eval_json(page, js):
    return json.loads(page.evaluate(f"JSON.stringify((() => {{ {js} }})())"))


with sync_playwright() as p:
    browser = p.chromium.launch(args=[
        "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
        "--disable-web-security", "--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 1280, "height": 720})
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)[:200]))
    page.add_init_script("window.__pp2DPlay = true;")

    print("== BOOT 2D ==")
    page.goto(f"{BASE}/game.html", wait_until="domcontentloaded", timeout=60000)
    chk("boot __PP_GAME", espera_boot(page))
    t0 = time.time()
    while time.time() - t0 < 20:
        listas = page.evaluate(
            "Object.keys(window.__PP_NORMAS.imgs).every(k => window.__PP_NORMAS.imgs[k].complete)")
        if listas:
            break
        time.sleep(0.3)
    chk("3 pieles NORMAS precargadas", listas)
    urls = page.evaluate(
        "Object.keys(window.__PP_NORMAS.defs).map(k => window.__PP_NORMAS.defs[k].url)")
    chk("URLs de arte correctas",
        urls == ["championships/locura/assets/normas_clown.png",
                 "championships/magia/assets/normas_wizard.png",
                 "championships/oeste/assets/normas_forajido.png"], str(urls))

    # referencia del arte escalado por el NAVEGADOR (mismo drawImage que el cartel)
    page.evaluate("""(() => {
      window.__REF = {};
      for (const k of Object.keys(window.__PP_NORMAS.defs)) {
        const cv = document.createElement('canvas');
        cv.width = 1280; cv.height = 640;
        cv.getContext('2d').drawImage(window.__PP_NORMAS.imgs[k], 0, 0, 1280, 640);
        window.__REF[k] = cv.toDataURL('image/png');
      }
    })()""")

    print("\n== CARTELES con los textos reales (ruta natural) ==")
    for tema, (titulo, filas) in TEXTOS.items():
        meta = eval_json(page, f"""
          window.__PP_GAME.showInstrucciones(
            {json.dumps(titulo)}, {json.dumps(filas)}, 7.5, null,
            '{tema}', {{ empezar: true }});
          const it = window.__PP_GAME._instr;
          const r = {{ arte: !!it.arte, skin: it.skin, cols: it.cols,
            fuente: it.fuente, rect: it.skinRect,
            png: it.tex.image.toDataURL('image/png') }};
          window.__PP_GAME.hideInstrucciones(true);
          return r;
        """)
        chk(f"[{tema}] piel de arte activa", meta["arte"] and meta["skin"] == tema,
            f"skin={meta['skin']}")
        chk(f"[{tema}] fuente legible (>=19 px lienzo)", meta["fuente"] >= 19,
            f"fuente={meta['fuente']} cols={meta['cols']}")
        Image.open(io.BytesIO(base64.b64decode(meta["png"].split(",", 1)[1]))
                   ).save(f"{OUT}/panel_{tema}.png")
        # diff contra el arte escalado: todo pixel cambiado DENTRO del hueco
        ref = Image.open(io.BytesIO(base64.b64decode(
            eval_json(page, f"return window.__REF['{tema}'];").split(",", 1)[1])
            )).convert("RGB")
        pnl = Image.open(f"{OUT}/panel_{tema}.png").convert("RGB")
        rx = [meta["rect"][0], meta["rect"][1], meta["rect"][2], meta["rect"][3]]
        w, h = pnl.size
        rp, pp = ref.load(), pnl.load()
        fuera, dentro = 0, 0
        for y in range(h):
            for x in range(w):
                a, b = rp[x, y], pp[x, y]
                if abs(a[0]-b[0]) + abs(a[1]-b[1]) + abs(a[2]-b[2]) > 40:
                    if (rx[0]-6 <= x <= rx[2]+6 and rx[1]-6 <= y <= rx[3]+6):
                        dentro += 1
                    else:
                        fuera += 1
        chk(f"[{tema}] texto DENTRO del hueco del cartel", fuera == 0,
            f"px cambiados dentro={dentro} fuera={fuera} rect={rx}")

    print("\n== Piel «estacion» sin cambios (fallback dibujado) ==")
    meta = eval_json(page, """
      window.__PP_GAME.showInstrucciones('Duelo contra AX-9',
        ['Primero a 11 puntos.', 'El AX-9 pelea a máxima potencia.'],
        7.5, null, 'estacion', { empezar: true });
      const it = window.__PP_GAME._instr;
      const r = { arte: !!it.arte, tiene_banda: true };
      window.__PP_GAME.hideInstrucciones(true);
      return r;
    """)
    chk("[estacion] conserva su panel dibujado", meta["arte"] is False)

    print("\n== Botón EMPEZAR (ruta wait=true sobre el arte) ==")
    btn = eval_json(page, """
      const D = window.__PP_NORMAS.defs.oeste, I = window.__PP_NORMAS.imgs.oeste;
      window.__PP_GAME._instrArte('ASALTO AL TREN', """ + json.dumps(TEXTOS['oeste'][1][:4]) + """,
        7.5, null, D, I, true);
      const it = window.__PP_GAME._instr;
      const bctx = it.bcv.getContext('2d');
      const d1 = bctx.getImageData(0, 0, it.bcv.width, it.bcv.height).data;
      window.__PP_GAME._pintaBtnEmpezar(true);
      const d2 = bctx.getImageData(0, 0, it.bcv.width, it.bcv.height).data;
      let pintado = 0, cambio = 0;
      for (let i = 3; i < d1.length; i += 4) { if (d1[i] > 40) pintado++; }
      for (let i = 0; i < d1.length; i++) { if (d1[i] !== d2[i]) { cambio++; break; } }
      const r = { waitBtn: !!it.waitBtn, btn: !!it.btn, pintado, cambio: cambio > 0,
        bw: it.bcv.width, bh: it.bcv.height,
        hit_sin_mando: window.__PP_GAME._instrBtnHit(0),
        png: it.bcv.toDataURL('image/png') };
      window.__PP_GAME.hideInstrucciones(true);
      return r;
    """)
    chk("waitBtn + mesh botón", btn["waitBtn"] and btn["btn"])
    chk(f"botón pintado ({btn['bw']}×{btn['bh']})", btn["pintado"] > 20000,
        f"px opacos={btn['pintado']}")
    chk("re-pintado al apuntar (hot) funciona", btn["cambio"])
    chk("raycast sin mando = false (seguro)", btn["hit_sin_mando"] is False)
    Image.open(io.BytesIO(base64.b64decode(btn["png"].split(",", 1)[1]))
               ).save(f"{OUT}/btn_empezar.png")

    print("\n== Render in-situ (screenshot escena 2D) ==")
    page.evaluate("""
      window.__PP_GAME.showInstrucciones('ASEDIO AL ESCONDITE',
        """ + json.dumps(TEXTOS['oeste'][1]) + """, 7.5, null, 'oeste',
        { empezar: true });
      window.__PP_GAME._instr.mat.opacity = 1;
    """)
    time.sleep(1.2)
    page.screenshot(path=f"{OUT}/insitu_oeste.png")

    ctx.close()

    print("\n== SMOKE 4 campeonatos ==")
    for ch in ["locura", "magia", "oeste", "estacion_orbital"]:
        c2 = browser.new_context(viewport={"width": 800, "height": 450})
        pg = c2.new_page()
        e2 = []
        pg.on("pageerror", lambda e: e2.append(str(e)[:160]))
        pg.add_init_script("window.__pp2DPlay = true;")
        pg.goto(f"{BASE}/game.html?champ={ch}", wait_until="domcontentloaded",
                timeout=60000)
        t0 = time.time()
        ok = False
        while time.time() - t0 < 40:
            try:
                ok = pg.evaluate(
                    "!!(window.__PP_GAME&&window.__PP_GAME.champs&&"
                    "window.__PP_GAME.champs.mod&&window.__PP_GAME.champs.mod.controller)")
            except Exception:
                ok = False
            if ok:
                break
            time.sleep(1)
        time.sleep(3)
        chk(f"smoke {ch}", ok and not e2, f"pageerrors={len(e2)} {e2[:2]}")
        c2.close()

    browser.close()

print("\n==== QA V2.135 ====")
if errs:
    print("pageerrors del boot:", errs[:3])
    FALLOS.append(f"pageerrors boot: {errs[:3]}")
if FALLOS:
    print("FALLOS:", len(FALLOS))
    for f in FALLOS:
        print(" -", f)
    raise SystemExit(1)
print("TODO OK ✔")
