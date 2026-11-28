#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161b · normalización de nombres en el cargador de cartelas: el
manifiesto puede traer «Main/fondo.png» o «Main/fondo» — la clave de caché
es SIEMPRE sin extensión (el cargador la recorta una sola vez)."""
import sys

F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

P = []


def p(old, new, n=1):
    P.append((old, new, n))


# helper de normalización (junto a _uiLang)
p("""  _uiLang() {""",
"""  /** Clave de caché SIN extensión: el manifiesto puede traer
   *  «Main/Logo.png» o «Main/Logo» — ambos acaban en la misma clave. */
  _uiK(u) {
    return String(u).replace(/\\.png$/i, '');
  }

  _uiLang() {""")

# _uiPide: normaliza el nombre antes de partir claves
p("""  _uiPide(base, nombre, conOn) {
    const claves = conOn ? [nombre, nombre + '_on'] : [nombre];""",
"""  _uiPide(base, nombre, conOn) {
    const nombre2 = this._uiK(nombre);
    const claves = conOn ? [nombre2, nombre2 + '_on'] : [nombre2];""")

# _uiCartelaLista: normaliza las URLs del manifiesto
p("""    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img));
    return urls.every((u) => !!this._uiCv[base + u]);""",
"""    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img))
      .map((u) => this._uiK(u));
    return urls.every((u) => !!this._uiCv[base + u]);""")

# _uiCartela: normaliza URLs y claves de pintado
p("""    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img));
    if (!urls.every((u) => !!this._uiCv[base + u])) return false;
    const c = this.menuCanvas.getContext('2d');
    const ox = pa.x;
    const im = (k) => this._uiCv[base + k];
    // fondo a rodaja completa (el alfa del PNG deja entrever el hall)
    c.drawImage(im(def.fondo), ox, 0, pa.w, CONFIG_MENUS.lienzo.alto);
    // capas pre-compuestas (logo, palas — el arte del dueño a su rect)
    for (const L of def.capas || []) {
      c.drawImage(im(L.img), ox + L.x, L.y, L.w, L.h);
    }
    // botones: estado _on al apuntar (misma nomenclatura + _on)
    for (const b of def.botones || []) {
      const hov = this.menuHover.includes(rects.length);
      const img = (hov && im(b.img + '_on')) || im(b.img);""",
"""    const kf = this._uiK(def.fondo);
    const urls = [kf]
      .concat((def.capas || []).map((l) => this._uiK(l.img)))
      .concat((def.botones || []).map((b) => this._uiK(b.img)));
    if (!urls.every((u) => !!this._uiCv[base + u])) return false;
    const c = this.menuCanvas.getContext('2d');
    const ox = pa.x;
    const im = (k) => this._uiCv[base + k];
    // fondo a rodaja completa (el alfa del PNG deja entrever el hall)
    c.drawImage(im(kf), ox, 0, pa.w, CONFIG_MENUS.lienzo.alto);
    // capas pre-compuestas (logo, palas — el arte del dueño a su rect)
    for (const L of def.capas || []) {
      c.drawImage(im(this._uiK(L.img)), ox + L.x, L.y, L.w, L.h);
    }
    // botones: estado _on al apuntar (misma nomenclatura + _on)
    for (const b of def.botones || []) {
      const bi = this._uiK(b.img);
      const hov = this.menuHover.includes(rects.length);
      const img = (hov && im(bi + '_on')) || im(bi);""")

mal = [(i, cc, nn) for i, (old, new, nn) in enumerate(P)
       if (cc := c12.count(old)) != nn]
if mal:
    for i, cc, nn in mal:
        print(f'✗ parche {i}: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for old, new, _ in P:
    c12 = c12.replace(old, new)
with open(F_C12, 'w', encoding='utf-8') as fh:
    fh.write(c12)
print(f'✓ c12 normalizado: {len(c12)} bytes · _uiK x{c12.count("_uiK(")}')
