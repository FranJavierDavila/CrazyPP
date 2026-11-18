#!/usr/bin/env python3
"""Parchea las suites de regresión antiguas a la semántica del acordeón v2.28."""
import sys

S = "/home/z/my-project/scripts"

def patch(path, subs):
    src = open(path, encoding="utf-8").read()
    for old, new in subs:
        if old not in src:
            print(f"NO ENCONTRADO en {path}:\n---\n{old[:160]}\n---")
            sys.exit(1)
        src = src.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(src)
    print("parcheado", path)

# ---------- verify_v218: secciones 9 y 10 ----------
patch(f"{S}/verify_v218.py", [
    ("            if (!g.menuOpen) g.toggleMenu();\n            g.updateMenu();\n        }\"\"\")\n        aim = await page.evaluate(",
     "            if (!g.menuOpen) g.toggleMenu();\n            g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:match'));\n            g.updateMenu();\n        }\"\"\")\n        aim = await page.evaluate("),
    ("            g.rules.state = 'over';\n            g.toggleMenu();\n            const hasR = g.menuRects.some((r) => r.id === 'revancha');",
     "            g.rules.state = 'over';\n            g.toggleMenu();\n            g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:match'));\n            const hasR = g.menuRects.some((r) => r.id === 'revancha');"),
])

# ---------- verify_v222: expandir OPCIONES para el megáfono ----------
patch(f"{S}/verify_v222.py", [
    ("            g.toggleMenu();\n            g.updateMenu();\n            const ids = g.menuRects.map((r) => r.id);\n            const voz = g.menuRects.find((r) => r.id === 'voz');",
     "            g.toggleMenu();\n            g.updateMenu();\n            g.menuClick(g.menuRects.findIndex((r) => r.id === 'sec:opts'));\n            const ids = g.menuRects.map((r) => r.id);\n            const voz = g.menuRects.find((r) => r.id === 'voz');"),
])

print("LISTO")
