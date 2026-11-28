#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r161 · CARTELA MAIN data-driven (tema UI_Default) — informes del dueño:
«Vamos a reorganizar y rediseñar los menús… cartelas únicas al tamaño y
distancia que la tenemos ahora… todo el arte en UI_Default por temporadas
(Halloween, Navidad…)… todo data-driven».
· c02: CONFIG_UI_TEMAS (manifiesto: base del tema, cartela Main con panela
  única C, fondo, capas pre-compuestas, 6 botones con ids EXACTOS del
  despachador; coords relativas a la rodaja de la panela).
· c12: motor de cartelas — caché de imágenes (variante de idioma <img>_<lang>
  antes que base, fallos recordados), precarga en reposo a los 5 s, pintado
  fondo+capas+botones con estado _on al apuntar, fallback TOTAL al vestíbulo
  legado si falta una sola pieza."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

with open(F_C02, 'r', encoding='utf-8') as f: c02 = f.read()
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

P = []


def p(f, old, new, n=1):
    P.append((f, old, new, n))


# ── c02 · manifiesto CONFIG_UI_TEMAS (antes de CONFIG_SECCIONES) ───────
p(F_C02, """/* =====================================================================
 *  r68 · FASE 162 · CONFIG_SECCIONES — CONCHA DE LOS SUBAPARTADOS""",
"""/* =====================================================================
 *  r161 · CONFIG_UI_TEMAS — ARTE DE LOS MENÚS DATA-DRIVEN
 *  ---------------------------------------------------------------------
 *  «…todo el arte dentro de una carpeta UI_Default, por si los menús se
 *  pueden tematizar por temporadas (Halloween, Navidad, San Valentín…),
 *  misma estructura y nomenclatura, todo data-driven» (dueño). Cada tema
 *  vive en assets/ui/<tema>/ y declara SUS cartelas: fondo, capas (arte
 *  pre-compuesto a lienzo 1376×768) y botones (imagen base + su variante
 *  _on por nomenclatura + id de acción EXACTO del despachador). Las
 *  coordenadas son RELATIVAS a la rodaja de la panela indicada (C:
 *  1472×1400 del lienzo panorámico 3696×1400) — un tema nuevo copia la
 *  estructura, cambia el arte y el manifiesto apunta a su carpeta. El
 *  cargador prueba <img>_<idioma>.png antes que la base (pp_lang) y si
 *  falta UNA sola pieza la cartela no se pinta: el vestíbulo legado
 *  sigue tal cual (fallback progresivo, cero riesgo).
 *  ===================================================================== */
export const CONFIG_UI_TEMAS = {
  version: 1,
  activo: 'UI_Default',        // pp_uitema puede sustituirlo en vivo
  temas: {
    UI_Default: {
      base: 'assets/ui/UI_Default/',
      cartelas: {
        // r161 · CARTELA MAIN (menú inicial del dueño): UNA panela (la C,
        // mismo tamaño y distancia del arco) con el logo, las palas y los
        // 6 botones del mock (Jugar resalta en dorado al apuntar — _on).
        Main: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          capas: [
            { img: 'Main/Logo.png', x: 210, y: 53, w: 862, h: 481 },
            { img: 'Main/Palas.png', x: 0, y: 772, w: 1100, h: 615 },
          ],
          botones: [
            { id: 'page:jugar', img: 'Main/btn_Play', x: 898, y: 490, w: 520, h: 130 },
            { id: 'tab:multi', img: 'Main/btn_multijugador', x: 898, y: 638, w: 520, h: 130 },
            { id: 'page:champs', img: 'Main/btn_campeonatos', x: 898, y: 786, w: 520, h: 130 },
            { id: 'page:perfil', img: 'Main/btn_Perfil', x: 898, y: 934, w: 520, h: 130 },
            { id: 'page:opts', img: 'Main/btn_Ajustes', x: 898, y: 1082, w: 520, h: 130 },
            { id: 'salirweb', img: 'Main/btn_Salir', x: 898, y: 1230, w: 520, h: 130 },
          ],
        },
      },
    },
  },
};

/* =====================================================================
 *  r68 · FASE 162 · CONFIG_SECCIONES — CONCHA DE LOS SUBAPARTADOS""")

# ── c12 · P1 caché en el constructor (junto al lienzo virtual) ─────────
p(F_C12, """    this.menuCanvas = document.createElement('canvas');   // LIENZO VIRTUAL
    this.menuCanvas.width = CONFIG_MENUS.lienzo.ancho;
    this.menuCanvas.height = CONFIG_MENUS.lienzo.alto;""",
"""    this.menuCanvas = document.createElement('canvas');   // LIENZO VIRTUAL
    this.menuCanvas.width = CONFIG_MENUS.lienzo.ancho;
    this.menuCanvas.height = CONFIG_MENUS.lienzo.alto;
    // r161 · ARTE DATA-DRIVEN (CONFIG_UI_TEMAS): caché de imágenes del
    // tema activo, fallos recordados (el fallback legado decide en el
    // acto) y precarga en reposo tras el arranque.
    this._uiCv = {};
    this._uiFalla = {};
    this._uiPidendo = {};
    setTimeout(() => { try { this._uiPrecarga(); } catch (eUIPC) { /* */ } }, 5000);""")

# ── c12 · P2 lados: la cartela monta SOLO su panela ────────────────────
p(F_C12, """    this._menuArco((CONFIG_SECCIONES.lados &&
      CONFIG_SECCIONES.lados[this.menuPage]) || CONFIG_SECCIONES.defaultLados);""",
"""    // r161 · CARTELA ÚNICA: la cartela del tema monta SÓLO su panela
    // (Main → la C, tamaño y distancia del arco actual); sin arte cargado
    // el vestíbulo legado conserva sus L·C·R tal cual.
    const ladosPag = (CONFIG_SECCIONES.lados &&
      CONFIG_SECCIONES.lados[this.menuPage]) || CONFIG_SECCIONES.defaultLados;
    const uiMain = this.menuPage === 'main' ? this._uiCartelaDef('Main') : null;
    this._menuArco(uiMain && this._uiCartelaLista('Main')
      ? (uiMain.lados || ['C']) : ladosPag);""")

# ── c12 · P3 despacho 'main': cartela si hay arte, legado si no ────────
p(F_C12, """    if (this.menuPage === 'main') {
      this.drawMenuVestibulo(rects);
      this.menuRects = rects;""",
"""    if (this.menuPage === 'main') {
      // r161 · CARTELA ARTÍSTICA del tema (Main): si el arte COMPLETO del
      // tema está en caché pinta la cartela única (fondo + logo + palas +
      // botones con estado _on al apuntar); si falta UNA pieza, el
      // vestíbulo legado sigue sin cambios (fallback progresivo).
      if (this._uiCartela('Main', rects)) {
        this.menuRects = rects;
        this._menuState = this.rules.state;
        this._menuTipDraw(c, rects);   // tooltip del control apuntado
        this._menuTexSube();
        return;
      }
      this.drawMenuVestibulo(rects);
      this.menuRects = rects;""")

# ── c12 · P4 motor de cartelas (antes de drawMenuVestibulo) ────────────
p(F_C12, """  drawMenuVestibulo(rects) {""",
"""  /* ===== r161 · CARTELAS DATA-DRIVEN (CONFIG_UI_TEMAS) ================
   *  El arte del tema (PNG en assets/ui/<tema>/) viste las cartelas del
   *  menú: fondo, capas pre-compuestas y botones con estado _on al
   *  apuntar. Todo declarado en c02 — añadir una temporada es crear la
   *  carpeta con la MISMA nomenclatura y registrarla en temas. El
   *  cargador prueba la variante de idioma (<img>_<lang>.png) y cae a la
   *  base; si falta una sola pieza la cartela no se pinta.
   *  ===================================================================== */
  _uiTema() {
    try {
      const t = localStorage.getItem('pp_uitema');
      if (t && CONFIG_UI_TEMAS.temas[t]) return t;
    } catch (eUIT) { /* */ }
    return CONFIG_UI_TEMAS.activo;
  }

  _uiCartelaDef(nombre) {
    const tema = CONFIG_UI_TEMAS.temas[this._uiTema()];
    return (tema && tema.cartelas && tema.cartelas[nombre]) || null;
  }

  _uiLang() {
    try {
      const l = String(localStorage.getItem('pp_lang') || 'es').toLowerCase();
      return l === 'en' ? 'en' : 'es';
    } catch (eUIL) { return 'es'; }
  }

  /** Pide una imagen del tema (con variante de idioma si procede y su
   *  gemela _on si es un botón). La clave de caché es el nombre SIN
   *  extensión del manifiesto; los fallos se recuerdan (sin re-intentos). */
  _uiPide(base, nombre, conOn) {
    const claves = conOn ? [nombre, nombre + '_on'] : [nombre];
    for (const k of claves) {
      const clave = base + k;
      if (this._uiCv[clave] || this._uiFalla[clave] || this._uiPidendo[clave]) continue;
      this._uiPidendo[clave] = true;
      const lang = this._uiLang();
      const candidatos = (lang && lang !== 'es')
        ? [base + k + '_' + lang + '.png', base + k + '.png']
        : [base + k + '.png'];
      const siguiente = (i) => {
        if (i >= candidatos.length) {
          this._uiFalla[clave] = true;
          delete this._uiPidendo[clave];
          return;
        }
        const im = new Image();
        im.onload = () => {
          delete this._uiPidendo[clave];
          this._uiCv[clave] = im;
          // el arte completo acaba de llegar → repinta si el menú está
          // abierto en una página que usa cartela (Main)
          if (this.menuOpen && this.menuPage === 'main' &&
              this._uiCartelaLista('Main')) {
            try { this.drawMenu(); } catch (eUIR) { /* */ }
          }
        };
        im.onerror = () => siguiente(i + 1);
        im.src = candidatos[i];
      };
      siguiente(0);
    }
  }

  /** ¿Está el arte COMPLETO de la cartela en caché? (fondo + capas +
   *  botones base — las _on son opcionales: el apuntado cae a la base). */
  _uiCartelaLista(nombre) {
    const tema = CONFIG_UI_TEMAS.temas[this._uiTema()];
    const def = tema && tema.cartelas && tema.cartelas[nombre];
    if (!def) return false;
    const base = tema.base;
    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img));
    return urls.every((u) => !!this._uiCv[base + u]);
  }

  /** Precarga en reposo: TODAS las cartelas del tema activo (base y _on). */
  _uiPrecarga() {
    const tema = CONFIG_UI_TEMAS.temas[this._uiTema()];
    if (!tema) return;
    const base = tema.base;
    for (const nombre of Object.keys(tema.cartelas || {})) {
      const def = tema.cartelas[nombre];
      this._uiPide(base, def.fondo, false);
      for (const l of def.capas || []) this._uiPide(base, l.img, false);
      for (const b of def.botones || []) this._uiPide(base, b.img, true);
    }
  }

  /** Pinta la cartela (fondo + capas + botones) en la rodaja de SU
   *  panela y pusha los rects de los botones (ids EXACTOS del
   *  despachador). Devuelve false si falta arte → painter legado. */
  _uiCartela(nombre, rects) {
    const tema = CONFIG_UI_TEMAS.temas[this._uiTema()];
    const def = tema && tema.cartelas && tema.cartelas[nombre];
    if (!def) return false;
    const base = tema.base;
    const pa = CONFIG_MENUS.arco.panelas.find(
      (p2) => p2.id === (def.panela || 'C'));
    if (!pa) return false;
    const urls = [def.fondo]
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
      const img = (hov && im(b.img + '_on')) || im(b.img);
      if (img) c.drawImage(img, ox + b.x, b.y, b.w, b.h);
      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    return true;
  }

  drawMenuVestibulo(rects) {""")

# ── aplicar ────────────────────────────────────────────────────────────
B = {F_C02: c02, F_C12: c12}
mal = []
for i, (f, old, new, n) in enumerate(P):
    c = B[f].count(old)
    if c != n:
        mal.append((i, f.split('/')[-1], c, n))
if mal:
    for i, nom, cc, nn in mal:
        print(f"✗ parche {i} [{nom}]: {cc} coincidencias (esperaba {nn})")
    sys.exit(1)
for f, old, new, _ in P:
    B[f] = B[f].replace(old, new)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")

assert 'CONFIG_UI_TEMAS' in B[F_C02], 'manifiesto falta'
n12 = B[F_C12].count('_uiCartela')
assert n12 >= 6, f'motor de cartelas incompleto ({n12})'
print(f'✓ manifiesto + motor de cartelas ({n12} referencias _uiCartela en c12)')
