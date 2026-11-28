#!/usr/bin/env python3
# r159 · corrección: borrar el cuerpo huérfano de _menuPinDraw_RETIRADA_R159
# (parche previo renombró la cabecera en vez de eliminarla) y quitar la
# llamada restante en el sitio r85 (AJUSTES › PALA, salir SÍ/NO).
import sys

RUTA = '/home/z/my-project/public/game.html'
with open(RUTA, 'r', encoding='utf-8') as f:
    src = f.read()

# 1. sitio r85: sin _menuPinDraw()
OLD_R85 = """      this.menuPin = true;       // r85 · nace CON CHINCHETA (convención de la casa)
      this._menuPinDraw();
"""
NEW_R85 = """      this.menuPin = true;       // r85 · nace FIJO (r159: convención sin pin)
"""
c85 = src.count(OLD_R85)
if c85 != 1:
    print(f"✗ sitio r85: {c85} coincidencias"); sys.exit(1)

# 2. cuerpo huérfano: desde el stub hasta el método siguiente (exclusivo)
STUB = "  /* r159 · el icono de la chincheta se retiró con su función (dueño). */\n  _menuPinDraw_RETIRADA_R159() {\n"
FIN = "  /** Coloca el panel (flotación inicial)"
cs, cf = src.count(STUB), src.count(FIN)
if cs != 1 or cf != 1:
    print(f"✗ marcadores huérfano: stub={cs} fin={cf}"); sys.exit(1)
i0 = src.index(STUB)
i1 = src.index(FIN)
if not (i0 < i1 and (i1 - i0) < 4000):
    print(f"✗ rango huérfano sospechoso: {i0}..{i1} ({i1-i0} bytes)"); sys.exit(1)

src = src[:i0] + src[i1:].lstrip('\n') if False else src[:i0] + src[i1:]
src = src.replace(OLD_R85, NEW_R85)

with open(RUTA, 'w', encoding='utf-8') as f:
    f.write(src)

print(f"✓ huérfano ({i1-i0} bytes) y sitio r85 corregidos · {len(src)} bytes")
residuos = ['_menuPinCv', '_menuPinTex', '_menuPinMesh', '_menuPinDraw',
            '_menuPinToggle', 'pinHit', "menu_pin_off", "menu_pin_on",
            "idx === -2", "hov === -2", "altoM: 0.95", "dist: 1.00",
            "RETIRADA_R159"]
mal = [r for r in residuos if r in src]
print("✓ sin residuos del pin" if not mal else f"✗ RESIDUOS: {mal}")
print(f"  menuPin=true (ancla interna): {src.count('this.menuPin = true')} sitios")
