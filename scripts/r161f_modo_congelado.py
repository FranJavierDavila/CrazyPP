#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161f · MODO CONGELADO de la cartela (bug real detectado por
qa_hittest_vivo): si el arte terminaba de cargar CON el menú abierto, la
siguiente repintada cambiaba el vestíbulo legado por la cartela EN MITAD
de la interacción — los rects mudaban bajo la mano (el click por índice
caía en otro botón; el test acababa en salirask). Ahora el modo se decide
al ABRIR el menú (toggleMenu) y queda congelado hasta la próxima
apertura: o cartela o legado, sin mutaciones a medias."""
import sys

F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

P = []


def p(old, new, n=1):
    P.append((old, new, n))


# 1 · init del valor congelado (junto a la caché UI del constructor)
p("""    this._uiCv = {};
    this._uiFalla = {};
    this._uiPidendo = {};""",
"""    this._uiCv = {};
    this._uiFalla = {};
    this._uiPidendo = {};
    this._uiModoMainVal = null;   // r161f: congelado al abrir el menú""")

# 2 · toggleMenu: cada APERTURA re-decide (el congelado dura una apertura)
p("""    if (this.calib && !this.calibPala) return;
    this.menuOpen = !this.menuOpen;""",
"""    if (this.calib && !this.calibPala) return;
    // r161f · el modo de la cartela (arte cargado o vestíbulo legado) se
    // RE-DEcide SOLO aquí, al abrir: congelado durante toda la apertura,
    // el menú jamás muta bajo la mano del dueño
    this._uiModoMainVal = null;
    this.menuOpen = !this.menuOpen;""")

# 3 · el congelado se consulta (nuevo método junto a _uiCartelaLista)
p("""  /** Precarga en reposo: TODAS las cartelas del tema activo (base y _on). */""",
"""  /** r161f · ¿cartela o legado en esta apertura? Se decide al abrir (el
   *  primer drawMenu tras toggleMenu congela) y NO cambia hasta cerrar:
   *  los rects jamás mudan bajo la mano (clicks por índice estables). */
  _uiModoMain() {
    if (this._uiModoMainVal === null) {
      this._uiModoMainVal = this._uiCartelaLista('Main');
    }
    return this._uiModoMainVal;
  }

  /** Precarga en reposo: TODAS las cartelas del tema activo (base y _on). */""")

# 4 · lados: consulta el congelado (no la lista en vivo)
p("""    const uiMain = this.menuPage === 'main' ? this._uiCartelaDef('Main') : null;
    this._menuArco(uiMain && this._uiCartelaLista('Main')
      ? (uiMain.lados || ['C']) : ladosPag);""",
"""    const uiMain = this.menuPage === 'main' ? this._uiCartelaDef('Main') : null;
    this._menuArco(uiMain && this._uiModoMain()
      ? (uiMain.lados || ['C']) : ladosPag);""")

# 5 · despacho 'main': consulta el congelado
p("""      if (this._uiCartela('Main', rects)) {
        this.menuRects = rects;""",
"""      if (this._uiModoMain() && this._uiCartela('Main', rects)) {
        this.menuRects = rects;""")

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
print(f'✓ c12 modo congelado: {len(c12)} bytes · _uiModoMain x{c12.count("_uiModoMain")}')
