#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163 · CARTELA JUGAR + 5 mejoras del informe del dueño:
1 · MENÚ ANTIGUO AL ARRANCAR: _uiModoMainVal se congelaba a false en el
    primer drawMenu (el arte no había llegado — precarga a 5 s) y NUNCA
    se re-decidía (sin reset al cerrar) → vestíbulo legado para siempre.
    FIX: precarga temprana (900 ms) + _uiModo POR CARTELA + _uiArteLlego
    re-decide si el arte llega SIN NADIE APUNTANDO (hover vacío: los rects
    jamás mudan bajo la mano — r161f intacto).
2 · RÓTULOS MÁS PEQUEÑOS: la fuente arranca en min(f, 40) (solapaban el
    arte de los botones).
3 · BANDERAS es/en en la esquina superior derecha de la cartela Main
    (pintadas a canvas, ids lang:xx del despachador de v2.27).
4 · PALAS: suben al centro de su hueco (y 772→630) + VAIVÉN ligero; la
    cartela permanece estática.
5 · SONIDO DE SELECCIÓN: blip común en TODA pulsación (menuClick) + tick
    de foco más perceptible; quitados los blips redundantes por-caso.
6 · CARTELA JUGAR: base común (fondo de Main) + título de sección T() +
    RECURSO dinámico del modo seleccionado con crossfade ágil (240 ms) +
    5 botones (start/traingo/survgo/escalera:soon/tut:go); por defecto
    btn_maquina (jugar.png en pantalla al abrir); escalera avisa — su
    cartela propia llega en la siguiente ronda (encargo del dueño)."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
F_HTM = '/home/z/my-project/public/game.html'

B = {}
for f in (F_C02, F_C12, F_HTM):
    with open(f, 'r', encoding='utf-8') as fh:
        B[f] = fh.read()

P = []


def p(f, old, new, n=1):
    P.append((f, old, new, n))


# ───────────────────────── c02 · CONFIG_UI_TEMAS ─────────────────────────
p(F_C02, """        Main: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          capas: [
            { img: 'Main/Logo.png', x: 210, y: 53, w: 862, h: 481 },
            { img: 'Main/Palas.png', x: 0, y: 772, w: 1100, h: 615 },
          ],""",
"""        Main: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          // r163 · BANDERAS es/en en la ESQUINA SUPERIOR DERECHA (petición
          // del dueño) — pintadas a canvas, ids lang:xx del despachador.
          banderas: { x: 1240, y: 34, w: 86, h: 58 },
          capas: [
            { img: 'Main/Logo.png', x: 210, y: 53, w: 862, h: 481 },
            // r163 · las palas SUBEN al centro de su hueco (informe del
            // dueño: «muy abajo») y respiran con un VAIVÉN ligero; la
            // cartela permanece estática por comodidad.
            { img: 'Main/Palas.png', x: 0, y: 630, w: 1100, h: 615,
              vaiven: 16 },
          ],""")

for clave, tx in (('hub_jugar', '150'), ('hub_multi', '118'), ('sec_crazy', '118'),
                  ('perfil_title', '118'), ('opts_title', '118'),
                  ('dock_salir', '118')):
    p(F_C02, f"etiquetaKey: '{clave}', tx: {tx}, f: 48 }},",
      f"etiquetaKey: '{clave}', tx: {tx}, f: 40 }},   // r163 rótulo menor")

p(F_C02, """            { id: 'salirweb', img: 'Main/btn_Salir', x: 898, y: 1230, w: 520, h: 130,
              etiquetaKey: 'dock_salir', tx: 118, f: 40 },   // r163 rótulo menor
          ],
        },
      },
    },
  },
};""",
"""            { id: 'salirweb', img: 'Main/btn_Salir', x: 898, y: 1230, w: 520, h: 130,
              etiquetaKey: 'dock_salir', tx: 118, f: 40 },   // r163 rótulo menor
          ],
        },
        // r163 · CARTELA JUGAR (encargo del dueño): cartela COMÚN (la
        // misma base de cristal de Main) sobre la que se superponen el
        // título de sección, el RECURSO del modo seleccionado (fade ágil)
        // y los 5 botones del zip. Botones en la MISMA colocación que
        // Main (columna derecha 898·520·130, misma línea de arranque).
        // El arte no hornea texto: título y rótulos los pinta T().
        Jugar: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          tituloKey: 'hub_jugar',
          recurso: {
            // el recurso ocupa la mayor parte del espacio IZQUIERDO
            x: 36, y: 560, w: 830, h: 415, vaiven: 14,
            defecto: 'btn_maquina',
            imgs: {
              btn_maquina: 'Jugar/jugar.png',
              btn_entrenamiento: 'Jugar/entrenamiento.png',
              btn_supervivencia: 'Jugar/supervivencia.png',
              btn_escalera: 'Jugar/escalera.png',
              btn_tutorial: 'Jugar/tutorial.png',
            },
          },
          botones: [
            // «Todos lanzarán el modo de juego correspondiente salvo el
            // modo escalera» (dueño) — escalera: aviso honesto, su
            // cartela propia llega en la siguiente ronda.
            { id: 'start', img: 'Jugar/btn_maquina', x: 898, y: 490, w: 520, h: 130,
              etiquetaKey: 'jug_maquina', tx: 118, f: 40 },
            { id: 'traingo', img: 'Jugar/btn_entrenamiento', x: 898, y: 638, w: 520, h: 130,
              etiquetaKey: 'jug_entrena', tx: 118, f: 40 },
            { id: 'survgo', img: 'Jugar/btn_supervivencia', x: 898, y: 786, w: 520, h: 130,
              etiquetaKey: 'sec_surv', tx: 118, f: 40 },
            { id: 'escalera:soon', img: 'Jugar/btn_escalera', x: 898, y: 934, w: 520, h: 130,
              etiquetaKey: 'jug_escalera', tx: 118, f: 40 },
            { id: 'tut:go', img: 'Jugar/btn_tutorial', x: 898, y: 1082, w: 520, h: 130,
              etiquetaKey: 'tut_hub', tx: 118, f: 40 },
          ],
        },
      },
    },
  },
};""")

# ───────────────────────────── c12 · el motor ────────────────────────────
# constructor: estado por cartela + precarga temprana
p(F_C12, """    this._uiModoMainVal = null;   // r161f: congelado al abrir el menú
    setTimeout(() => { try { this._uiPrecarga(); } catch (eUIPC) { /* */ } }, 5000);""",
"""    // r163 · congelado POR CARTELA (Main/Jugar) + vida de la cartela
    // JUGAR (selección de modo + crossfade del recurso).
    this._uiModoVals = {};
    this._uiJugarSel = null;      // null → el defecto del manifiesto
    this._uiJugarFade = null;     // { de, a, t0 } del crossfade
    // r163 · precarga TEMPRANA (antes 5 s): el menú abre al arrancar y el
    // arte debía estar camino YA (informe del dueño: «el menú no se abre
    // al principio, sigue estando antiguo»).
    setTimeout(() => { try { this._uiPrecarga(); } catch (eUIPC) { /* */ } }, 900);""")

# onload → helper re-decidible
p(F_C12, """        im.onload = () => {
          delete this._uiPidendo[clave];
          this._uiCv[clave] = im;
          // el arte completo acaba de llegar → repinta si el menú está
          // abierto en una página que usa cartela (Main)
          if (this.menuOpen && this.menuPage === 'main' &&
              this._uiCartelaLista('Main')) {
            try { this.drawMenu(); } catch (eUIR) { /* */ }
          }
        };""",
"""        im.onload = () => {
          delete this._uiPidendo[clave];
          this._uiCv[clave] = im;
          try { this._uiArteLlego(); } catch (eUIR) { /* */ }
        };""")

# _uiCartelaLista incluye los recursos dinámicos
p(F_C12, """    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img))
      .map((u) => this._uiK(u));
    return urls.every((u) => !!this._uiCv[base + u]);""",
"""    const urls = [def.fondo]
      .concat((def.capas || []).map((l) => l.img))
      .concat((def.botones || []).map((b) => b.img))
      .concat(def.recurso ? Object.values(def.recurso.imgs || {}) : [])
      .map((u) => this._uiK(u));
    return urls.every((u) => !!this._uiCv[base + u]);""")

# _uiModoMain → _uiModo(nombre) + _uiArteLlego
p(F_C12, """  _uiModoMain() {
    if (this._uiModoMainVal === null) {
      this._uiModoMainVal = this._uiCartelaLista('Main');
    }
    return this._uiModoMainVal;
  }""",
"""  /** r163 · ¿cartela o legado en esta apertura? CONGELADO POR CARTELA:
   *  se decide al abrir (primer drawMenu de la página) y NO cambia hasta
   *  que el arte llegue SIN NADIE APUNTANDO (swap del arranque, abajo) —
   *  los rects jamás mudan bajo la mano (clicks por índice estables,
   *  r161f). */
  _uiModo(nombre) {
    if (this._uiModoVals[nombre] === undefined ||
        this._uiModoVals[nombre] === null) {
      this._uiModoVals[nombre] = this._uiCartelaLista(nombre);
    }
    return this._uiModoVals[nombre];
  }

  /** r163 · una pieza del arte acabó de llegar: si la página abierta es
   *  una de cartela, el arte ya está COMPLETO y NADIE está apuntando un
   *  botón, el congelado se re-decide (el vestíbulo del ARRANQUE muda a
   *  cartela sola — informe del dueño: «el menú no se abre al principio,
   *  sigue estando antiguo»; además el congelado de r161f no se reseteaba
   *  al cerrar: false pegado para siempre). Con una mano encima, espera. */
  _uiArteLlego() {
    if (!this.menuOpen) return;
    const pag = this.menuPage === 'main' ? 'Main'
      : this.menuPage === 'jugar' ? 'Jugar' : null;
    if (!pag) return;
    if (this._uiCartelaLista(pag)) {
      if (this._uiModoVals[pag] === false &&
          !this.menuHover.some((h) => h >= 0)) {
        this._uiModoVals[pag] = true;
      }
      if (this._uiModoVals[pag] === true) {
        try { this.drawMenu(); } catch (eUIR) { /* */ }
      }
    }
  }""")

# precarga de los recursos dinámicos
p(F_C12, """      for (const l of def.capas || []) this._uiPide(base, l.img, false);
      for (const b of def.botones || []) this._uiPide(base, b.img, true);
    }
  }""",
"""      for (const l of def.capas || []) this._uiPide(base, l.img, false);
      for (const b of def.botones || []) this._uiPide(base, b.img, true);
      // r163 · los recursos dinámicos de la cartela (fade del modo)
      if (def.recurso) {
        for (const uR of Object.values(def.recurso.imgs || {})) {
          this._uiPide(base, uR, false);
        }
      }
    }
  }""")

# drawMenu: montaje del arco para main Y jugar
p(F_C12, """    const uiMain = this.menuPage === 'main' ? this._uiCartelaDef('Main') : null;
    this._menuArco(uiMain && this._uiModoMain()
      ? (uiMain.lados || ['C']) : ladosPag);""",
"""    // r163 · la cartela manda el montaje en main Y jugar (panela C
    // única); sin arte, los lados legado de CONFIG_SECCIONES.
    const _uiNom = this.menuPage === 'main' ? 'Main'
      : this.menuPage === 'jugar' ? 'Jugar' : null;
    const uiCart = _uiNom ? this._uiCartelaDef(_uiNom) : null;
    this._menuArco(uiCart && this._uiModo(_uiNom)
      ? (uiCart.lados || ['C']) : ladosPag);""")

# drawMenu: despacho de la cartela Main con el nuevo _uiModo
p(F_C12, """      if (this._uiModoMain() && this._uiCartela('Main', rects)) {""",
"""      if (this._uiModo('Main') && this._uiCartela('Main', rects)) {""")

# drawMenu: cartela JUGAR antes de la rejilla legado
p(F_C12, """    if (this.menuPage === 'jugar') {
      this._menuRejilla(rects, 'jugar', this._jugarSubs());""",
"""    if (this.menuPage === 'jugar') {
      // r163 · CARTELA JUGAR: si el arte completo del tema llegó, cartela
      // única (título + recurso con fade + 5 botones); si falta UNA pieza
      // la rejilla legado sigue sin cambios (fallback progresivo).
      if (this._uiModo('Jugar') && this._uiCartela('Jugar', rects)) {
        this.menuRects = rects;
        this._menuState = this.rules.state;
        this._menuTipDraw(c, rects);   // tooltip del control apuntado
        this._menuTexSube();
        return;
      }
      this._menuRejilla(rects, 'jugar', this._jugarSubs());""")

# _uiCartela completa: título + vaivén + recurso + banderas + fuente 40
p(F_C12, """    const c = this.menuCanvas.getContext('2d');
    const ox = pa.x;
    const im = (k) => this._uiCv[base + k];
    // fondo a rodaja completa (el alfa del PNG deja entrever el hall)
    c.drawImage(im(kf), ox, 0, pa.w, CONFIG_MENUS.lienzo.alto);
    // capas pre-compuestas (logo, palas — el arte del dueño a su rect)
    for (const L of def.capas || []) {
      c.drawImage(im(this._uiK(L.img)), ox + L.x, L.y, L.w, L.h);
    }
    // botones: estado _on al apuntar (misma nomenclatura + _on) y
    // RÓTULO vivo (r161c · el arte del tema no hornea texto — T() manda)
    for (const b of def.botones || []) {""",
"""    const c = this.menuCanvas.getContext('2d');
    const ox = pa.x;
    const im = (k) => this._uiCv[base + k];
    // fondo a rodaja completa (el alfa del PNG deja entrever el hall)
    c.drawImage(im(kf), ox, 0, pa.w, CONFIG_MENUS.lienzo.alto);
    // r163 · TÍTULO DE SECCIÓN (cartela Jugar: «JUGAR» arriba en dorado —
    // el arte no hornea texto: el rótulo lo pinta T() como en los botones)
    if (def.tituloKey) {
      const tit = T(def.tituloKey);
      c.font = '900 72px system-ui, sans-serif';
      c.textAlign = 'center';
      c.textBaseline = 'middle';
      c.fillStyle = 'rgba(255,210,87,0.98)';
      c.shadowColor = 'rgba(6,20,44,0.65)';
      c.shadowBlur = 10;
      c.fillText(tit, ox + pa.w / 2, 104);
      c.shadowBlur = 0;
      c.strokeStyle = 'rgba(255,210,87,0.5)';
      c.lineWidth = 3;
      const tw = Math.min(c.measureText(tit).width, pa.w - 200);
      c.beginPath();
      c.moveTo(ox + pa.w / 2 - tw / 2, 152);
      c.lineTo(ox + pa.w / 2 + tw / 2, 152);
      c.stroke();
      c.textAlign = 'left';
      c.font = '800 34px system-ui, sans-serif';
    }
    // capas pre-compuestas (logo, palas — el arte del dueño a su rect);
    // r163 · VAIVÉN: una capa puede respirar (amplitud px) con la cartela
    // estática — la petición del dueño para las palas de Main.
    for (const L of def.capas || []) {
      const vx = L.vaiven ? Math.sin(performance.now() / 950) * L.vaiven : 0;
      c.drawImage(im(this._uiK(L.img)), ox + L.x + vx, L.y, L.w, L.h);
    }
    // r163 · RECURSO DINÁMICO (cartela Jugar): el arte del modo SELECCIO-
    // NADO con crossfade ágil (240 ms). Selección = botón apuntado; sin
    // apuntado permanece el último («siempre esté en pantalla el recurso
    // relativo al botón seleccionado» — dueño). Al abrir: el defecto
    // (btn_maquina → jugar.png).
    if (def.recurso) {
      const R = def.recurso;
      const hi = this.menuHover.find((h) => h >= 0);
      if (hi !== undefined && hi >= 0 && hi < (def.botones || []).length) {
        const rid = (def.botones[hi] || {}).id;
        if (rid && R.imgs[rid] && rid !== this._uiJugarSel) {
          this._uiJugarFade = { de: this._uiJugarSel || R.defecto,
            a: rid, t0: performance.now() };
          this._uiJugarSel = rid;
        }
      }
      if (!this._uiJugarSel) this._uiJugarSel = R.defecto;
      const pro = this._uiJugarFade
        ? Math.min(1, (performance.now() - this._uiJugarFade.t0) / 240) : 1;
      const pintar = (clave, alfa) => {
        const uR = R.imgs[clave];
        const imR = uR && this._uiCv[base + this._uiK(uR)];
        if (!imR) return;
        c.save();
        c.globalAlpha = Math.max(0, Math.min(1, alfa));
        const vx = R.vaiven ? Math.sin(performance.now() / 900) * R.vaiven : 0;
        c.drawImage(imR, ox + R.x + vx, R.y, R.w, R.h);
        c.restore();
      };
      if (this._uiJugarFade && pro < 1 && this._uiJugarFade.de &&
          this._uiJugarFade.de !== this._uiJugarSel) {
        pintar(this._uiJugarFade.de, 1 - pro);
      }
      pintar(this._uiJugarSel, this._uiJugarFade ? pro : 1);
      if (this._uiJugarFade && pro >= 1) this._uiJugarFade = null;
    }
    // r163 · BANDERAS es/en (cartela Main, esquina superior derecha —
    // petición del dueño): pintadas a canvas (sin asset); los ids
    // lang:es / lang:en ya existían en el despachador desde v2.27.
    if (def.banderas) {
      const B2 = def.banderas;
      const activo = this._uiLang();
      for (let i2 = 0; i2 < 2; i2++) {
        const iso = i2 === 0 ? 'es' : 'en';
        const bx = ox + B2.x + i2 * (B2.w + 14);
        const hovB = this.menuHover.includes(rects.length);
        this._uiBandera(c, iso, bx, B2.y, B2.w, B2.h, hovB, iso === activo);
        rects.push(this._mapRect({ x: bx, y: B2.y, w: B2.w, h: B2.h,
          id: 'lang:' + iso }));
      }
    }
    // botones: estado _on al apuntar (misma nomenclatura + _on) y
    // RÓTULO vivo (r161c · el arte del tema no hornea texto — T() manda)
    for (const b of def.botones || []) {""")

# fuente del rótulo: tapa más baja (min 40)
p(F_C12, """        // r161d · AUTOAJUSTE: la fuente baja hasta que el rótulo cabe en
        // el botón (tx..borde-26) — cualquier idioma, cualquier tema
        let fUI = b.f || 48;""",
"""        // r161d · AUTOAJUSTE: la fuente baja hasta que el rótulo cabe en
        // el botón (tx..borde-26) — cualquier idioma, cualquier tema
        // r163 · TAPA MÁS BAJA: los rótulos solapaban partes del arte del
        // botón (informe del dueño) — la fuente arranca en min(f, 40).
        let fUI = Math.min(b.f || 48, 40);""")

# fin de _uiCartela: pedir repintado vivo + helper de banderas
p(F_C12, """      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    return true;
  }

  drawMenuVestibulo(rects) {""",
"""      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    // r163 · vida viva: vaivén/fade piden el siguiente repintado
    this._menuAnimCartela();
    return true;
  }

  /** r163 · BANDERA MINI a canvas (clip redondeado manual — roundRect()
   *  no existe en todas las versiones del navegador del casco). ES:
   *  tricolor roja-amarilla; EN: union jack simplificado. Activa → borde
   *  dorado; apuntada → halo. */
  _uiBandera(c, iso, x, y, w, h, hov, activo) {
    const rr = (px, py, pw, ph, r2) => {
      c.beginPath();
      c.moveTo(px + r2, py);
      c.arcTo(px + pw, py, px + pw, py + ph, r2);
      c.arcTo(px + pw, py + ph, px, py + ph, r2);
      c.arcTo(px, py + ph, px, py, r2);
      c.arcTo(px, py, px + pw, py, r2);
      c.closePath();
    };
    c.save();
    rr(x, y, w, h, 10);
    c.clip();
    if (iso === 'es') {
      c.fillStyle = '#c60b1e';
      c.fillRect(x, y, w, h);
      c.fillStyle = '#ffc400';
      c.fillRect(x, y + h * 0.25, w, h * 0.5);
    } else {
      c.fillStyle = '#012169';
      c.fillRect(x, y, w, h);
      c.strokeStyle = '#ffffff';
      c.lineWidth = h * 0.22;
      c.beginPath();
      c.moveTo(x, y); c.lineTo(x + w, y + h);
      c.moveTo(x + w, y); c.lineTo(x, y + h);
      c.stroke();
      c.strokeStyle = '#c8102e';
      c.lineWidth = h * 0.09;
      c.beginPath();
      c.moveTo(x, y); c.lineTo(x + w, y + h);
      c.moveTo(x + w, y); c.lineTo(x, y + h);
      c.stroke();
      c.fillStyle = '#ffffff';
      c.fillRect(x + w * 0.36, y, w * 0.28, h);
      c.fillRect(x, y + h * 0.36, w, h * 0.28);
      c.fillStyle = '#c8102e';
      c.fillRect(x + w * 0.41, y, w * 0.18, h);
      c.fillRect(x, y + h * 0.41, w, h * 0.18);
    }
    c.restore();
    rr(x, y, w, h, 10);
    if (activo) {
      c.strokeStyle = 'rgba(255,210,87,0.95)';
      c.lineWidth = 4;
    } else {
      c.strokeStyle = 'rgba(255,255,255,0.4)';
      c.lineWidth = 2.5;
    }
    if (hov) {
      c.shadowColor = 'rgba(255,210,87,0.85)';
      c.shadowBlur = 14;
    }
    c.stroke();
    c.shadowBlur = 0;
  }

  drawMenuVestibulo(rects) {""")

# repintado vivo de cartelas (tras _menuAnimPide)
p(F_C12, """  _menuAnimPide(ms) {
    clearTimeout(this._menuAnimT);
    this._menuAnimT = setTimeout(() => {
      if (!this.menuOpen || this.menuPage !== 'carrera') return;
      this.drawMenu();
    }, ms || 130);
  }""",
"""  _menuAnimPide(ms) {
    clearTimeout(this._menuAnimT);
    this._menuAnimT = setTimeout(() => {
      if (!this.menuOpen || this.menuPage !== 'carrera') return;
      this.drawMenu();
    }, ms || 130);
  }

  /** r163 · repintado VIVO de las cartelas (vaivén de la pala + crossfade
   *  del recurso): encadena repintados a ~16 fps SOLO mientras la página
   *  abierta tenga vida en el tema activo — se autodetiene al cerrar o al
   *  cambiar de página (sin bucles huérfanos, como r79). */
  _menuAnimCartela(ms) {
    clearTimeout(this._menuAnimT);
    this._menuAnimT = setTimeout(() => {
      if (!this.menuOpen) return;
      const pag = this.menuPage === 'main' ? 'Main'
        : this.menuPage === 'jugar' ? 'Jugar' : null;
      if (!pag || !this._uiModoVals[pag]) return;
      const def = this._uiCartelaDef(pag);
      if (!def) return;
      const vida = (def.capas || []).some((l) => l.vaiven) || !!def.recurso ||
        !!this._uiJugarFade;
      if (!vida) return;
      this.drawMenu();
    }, ms || 62);
  }""")

# menuClick: blip común de selección en toda pulsación
p(F_C12, """    const mh = this._menuHitPx || [null, null];
    this._menuClickPx = mh[hand] || mh[0] || mh[1] || null;""",
"""    const mh = this._menuHitPx || [null, null];
    this._menuClickPx = mh[hand] || mh[0] || mh[1] || null;
    // r163 · SONIDO DE SELECCIÓN en TODA pulsación (petición del dueño:
    // «que siempre que se seleccione un botón suene un sonido») — blip
    // corto y consistente antes del despacho; los sonidos especiales
    // (acorde crazy, convocatoria social) suenan ENCIMA de este.
    try { this.audio.playOsc(640, 880, 0.05, 'sine', 0.11, 0); } catch (eBlip) { /* */ }""")

# menuClick: caso escalera (aviso honesto)
p(F_C12, """      case 'docktv':
      case 'dockintro':""",
"""      case 'escalera':
        // r163 · ESCALERA DE CAMPEONATO: su cartela propia llega en la
        // siguiente ronda (encargo del dueño) — por ahora, aviso honesto.
        this.rules.message = T('escalera_soon');
        this.drawMenu();
        break;
      case 'docktv':
      case 'dockintro':""")

# blips redundantes fuera (el común de menuClick los cubre)
p(F_C12, """        } else {
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        }""",
"""        } else {
          // r163 · el blip común de menuClick cubre la selección
        }""")
p(F_C12, """          this.syncDom();
          this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        }
        this.drawMenu();""",
"""          this.syncDom();
          // r163 · el blip común de menuClick cubre la selección
        }
        this.drawMenu();""")
p(F_C12, """        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);
        this.closeMenu();
        const elDock = document.getElementById(elId);""",
"""        // r163 · el blip común de menuClick cubre la selección
        this.closeMenu();
        const elDock = document.getElementById(elId);""")

# tick de foco más perceptible (sonido de selección al apuntar)
p(F_C12, """          try { this.audio.playOsc(1180, 1180, 0.028, 'sine', 0.05, 0); } catch (eFoco) { /* */ }""",
"""          // r163 · más perceptible (era casi inaudible — el dueño pide
          // oír la selección al apuntar cada botón)
          try { this.audio.playOsc(1180, 1420, 0.045, 'sine', 0.075, 0); } catch (eFoco) { /* */ }""")

# navegar a jugar: la selección vuelve al defecto (btn_maquina)
p(F_C12, """          this.menuPage = arg;
          // r79 · FIX «ESCOGER HALL NO HACE NADA»: 'hallpick' faltaba en la""",
"""          this.menuPage = arg;
          // r163 · entrar en JUGAR: la selección vuelve al defecto
          // (btn_maquina — jugar.png en pantalla al abrir la cartela)
          if (arg === 'jugar') { this._uiJugarSel = null; this._uiJugarFade = null; }
          // r79 · FIX «ESCOGER HALL NO HACE NADA»: 'hallpick' faltaba en la""")

# ───────────────────────── game.html · diccionarios T ────────────────────
p(F_HTM, """    jugar_sub: 'Partido · Carrera · Entrenamiento · Supervivencia · Tutorial',""",
"""    jugar_sub: 'Partido · Carrera · Entrenamiento · Supervivencia · Tutorial',
    // r163 · cartela JUGAR
    jug_maquina: 'JUGAR CONTRA LA MÁQUINA',
    jug_entrena: 'ENTRENAMIENTO',
    jug_escalera: 'ESCALERA DE CAMPEONATO',
    escalera_soon: 'ESCALERA DE CAMPEONATO · cartela propia en camino',""")
p(F_HTM, """    jugar_sub: 'Match · Career · Training · Survival · Tutorial',""",
"""    jugar_sub: 'Match · Career · Training · Survival · Tutorial',
    // r163 · JUGAR board
    jug_maquina: 'PLAY AGAINST THE MACHINE',
    jug_entrena: 'TRAINING',
    jug_escalera: 'CHAMPIONSHIP LADDER',
    escalera_soon: 'CHAMPIONSHIP LADDER · its own board is on the way',""")

mal = []
for i, (f, old, new, nn) in enumerate(P):
    cc = B[f].count(old)
    if cc != nn:
        mal.append((i, f.split('/')[-1], old[:60], cc, nn))
        continue
    B[f] = B[f].replace(old, new)
if mal:
    for i, nom, o, cc, nn in mal:
        print(f'✗ parche {i} [{nom}] «{o}…»: {cc} coincidencias (esperaba {nn})')
    sys.exit(1)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")
print('✓ r163: cartela JUGAR + banderas + vaivén + rótulos 40 + sonido de selección + arranque con cartela')
