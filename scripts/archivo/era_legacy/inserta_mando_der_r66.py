#!/usr/bin/env python3
"""r66 · Inserta el MANDO DERECHO del dueño (mando_derecho.glb → base64) en
c13 justo después del TUT_MANDO_GLB existente. Idempotente."""
import base64

C13 = "/home/z/my-project/src/game/core/c13_ui_arranque.js"
GLB = "/home/z/my-project/upload/mando_derecho.glb"

b64 = base64.b64encode(open(GLB, "rb").read()).decode("ascii")
assert "</" not in b64

txt = open(C13, encoding="utf-8").read()
MARCA = "const TUT_MANDO_DER_GLB = '"
if MARCA in txt:
    # sustituye el valor existente
    i = txt.index(MARCA)
    j = txt.index("';", i)
    txt = txt[:i] + MARCA + b64 + txt[j:]
    print("TUT_MANDO_DER_GLB sustituido")
else:
    i = txt.index("const TUT_MANDO_GLB = '")
    j = txt.index("';", i)
    ins = "\n  const TUT_MANDO_DER_GLB = '" + b64 + "';"
    txt = txt[:j + 2] + ins + txt[j + 2:]
    print("TUT_MANDO_DER_GLB insertado")
open(C13, "w", encoding="utf-8").write(txt)
print("c13:", len(txt), "bytes")
