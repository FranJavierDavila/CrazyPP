#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SONDEA LA TELEMETRÍA DE PRODUCCIÓN CON UN NAVEGADOR REAL (ronda 37).
Carga el game.html de producción en Chromium, deja que el juego dispare su
primer flush (5 s) y comprueba: (1) __PP_TELE.st.sent/lastErr dentro del
navegador, (2) el latido del Worker ANTES y DESPUÉS (el total debe subir con
el boot de esta sesión). Evidencia del informe «la telemetría no se actualiza».
Uso: python3 scripts/probe_tele_prod.py
"""
import json
import subprocess
import sys
import time
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
URL_LATIDO = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele"
URL_GAME = "https://franjavierdavila.github.io/CrazyPP/game.html"


def latido():
    req = urllib.request.Request(URL_LATIDO)
    req.add_header("User-Agent", UA)
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main():
    total0 = latido().get("total")
    print(f"latido ANTES: total={total0}")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(args=[
            "--use-gl=swiftshader", "--enable-unsafe-swiftshader",
            "--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context()
        page = ctx.new_page()
        fallos = []
        page.on("pageerror", lambda e: fallos.append(str(e)))
        page.on("console", lambda m: fallos.append(m.text)
                if "[TELE]" in m.text else None)
        page.goto(URL_GAME, wait_until="load", timeout=45000)
        # el juego dispara el primer flush a los 5 s: espera con margen
        page.wait_for_timeout(12000)
        st = page.evaluate("""() => {
          try {
            const t = window.__PP_TELE && window.__PP_TELE.st;
            if (!t) return { hay: false };
            return { hay: true, on: t.on, q: t.q.length, sent: t.sent,
                     lastOk: t.lastOk, lastErr: t.lastErr,
                     ep: window.PP_TELEMETRY_ENDPOINT || '',
                     sid: t.sid };
          } catch (e) { return { hay: false, err: String(e) }; }
        }""")
        browser.close()

    print("estado __PP_TELE en el navegador:", json.dumps(st, ensure_ascii=False))
    if fallos:
        print("consola TELE:", fallos[:6])
    time.sleep(2)
    total1 = latido().get("total")
    print(f"latido DESPUÉS: total={total1}")
    if not st.get("hay"):
        print("FALLO: window.__PP_TELE no existe")
        sys.exit(1)
    delta = (total1 or 0) - (total0 or 0)
    print(f"DELTA total del Worker: {delta:+d}")
    if delta > 0 and st.get("sent", 0) > 0:
        print("VEREDICTO: la cadena de producción ENVÍA y el Worker RECIBE ✓")
        sys.exit(0)
    if delta == 0 and st.get("sent", 0) == 0:
        print("VEREDICTO: el navegador NO envió (o el Worker no recibió) ✗")
        print("  lastErr:", st.get("lastErr", ""), "· endpoint:", st.get("ep", ""))
        sys.exit(2)
    print("VEREDICTO: ambiguo — revisar sent/lastErr arriba")
    sys.exit(3)


if __name__ == "__main__":
    main()
