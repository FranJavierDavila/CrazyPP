#!/usr/bin/env python3
"""Humo r46: carga game.html en :3000, comprueba versión, errores de página
y las sellos nuevos del gobernador de telemetría."""
import json
import sys
from playwright.sync_api import sync_playwright

URL = "http://localhost:3000/game.html?v=36139"
res = {"pageerrors": [], "console": [], "version": None, "badge": None,
       "gobernador": None, "telemetria": None}

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("pageerror", lambda e: res["pageerrors"].append(str(e)[:200]))
    pg.on("console", lambda m: res["console"].append(m.type + ":" + m.text[:120])
          if m.type in ("error", "warning") else None)
    pg.goto(URL, wait_until="domcontentloaded", timeout=60000)
    pg.wait_for_timeout(6000)
    res["version"] = pg.evaluate("() => window.__PP_VERSION || null")
    res["badge"] = pg.evaluate("() => (document.getElementById('verBadge')||{}).textContent || null")
    res["telemetria"] = pg.evaluate("() => !!window.__PP_TELE")
    res["gobernador"] = pg.evaluate("() => ({partida: !!(window.__PP_TELE && window.__PP_TELE.partida), hold: window.__PP_TELE ? window.__PP_TELE.hold : null, st: !!(window.__PP_TELE && window.__PP_TELE.st)})")
    b.close()

print(json.dumps(res, ensure_ascii=False, indent=1))
fallos = []
if res["version"] != "3.6.139-SDK6":
    fallos.append("version")
if not res["telemetria"]:
    fallos.append("telemetria ausente")
if not (res["gobernador"] or {}).get("partida"):
    fallos.append("gobernador.partida ausente")
if res["pageerrors"]:
    fallos.append("pageerrors: " + "; ".join(res["pageerrors"][:2]))
print("RESULTADO:", "OK" if not fallos else "FALLOS: " + " · ".join(fallos))
sys.exit(0 if not fallos else 1)
