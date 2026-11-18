#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_r85_fase181.py — r85 · FASE 181 «SALIDAS Y MONEDAS» · V3.6.176-SDK6.

Informe del dueño tras la V3.6.175 en el visor (4 frentes):
  1) «en la configuración de la posición de la pala no se puede salir» —
     FIX raíz: los casos 'pala:si'/'pala:no' del despacho de menuClick están
     escritos con el id COMPLETO pero el switch compara el PREFIJO anterior
     al primer ':' (ns='pala') — jamás casaban: el SÍ/NO de la autorización
     era DECORATIVO y el ajuste quedaba atrapado.
  2) «el botón B abre un panel que no hace nada, es puramente cosmético» —
     el mismo bug (1): el panel SÍ/NO abre, los clics no hacen nada.
  3) «la ventana de información de ajuste y colocación de la pala se arrastra
     hacia otros menús y no desaparece; a partir de ahí ya no es posible
     cerrar el menú» — dos fugas: palaRecoger() NO ocultaba calibPanel (la
     ventana quedaba flotando para siempre) y toggleMenu() tenía el guard
     `if (this.calib) return` que dejaba el menú INCIERRABLE durante el
     ajuste (B, «NO» y «CERRAR MENÚ» muertos). Además el ancla del panel se
     herdaba de la sesión anterior (lerp 0,35 sin reset de posición).
  4) «NO existen bloqueos de bolas ni de mesas, cosa que debería
     configurarse con la economía del juego» — ECONOMÍA CRAZY: monedas que
     se ganan JUGANDO (+25 victoria · +8 derrota, en recordMatch) y TIENDA
     CRAZY: coste en los aspectos de mesa/bola, candado+precio en la rejilla,
     modal de compra con confirmación; el hito por logros sigue siendo la
     vía GRATIS (candado superado ⇒ seleccionable sin comprar).

Parches: c12 (menú/salidas/tienda), c02 (costes de catálogo), c06 (monedero
en ppxr_stats_v1), c00 (i18n ES/EN). Anclajes únicos con aserción — aborta
sin escribir si algo no casa.
"""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = RAIZ / 'src/game/core/c12_pingponggame.js'
C02 = RAIZ / 'src/game/core/c02_cfg_escena.js'
C06 = RAIZ / 'src/game/core/c06_logros_stats_ia_rival.js'
C00 = RAIZ / 'src/game/core/c00_pre_three.js'

P = []   # (fichero, viejo, nuevo, etiqueta)


def p(fich, viejo, nuevo, et):
    P.append((fich, viejo, nuevo, et))


# ════════════════════════════════════════════════════════════════════════
# c12 · FIX A — el despacho muerto 'pala:si'/'pala:no' → case 'pala' + arg
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""      case 'pala:si':
        // r79 · AUTORIZACIÓN concedida: recoger el ajuste (passthrough,
        // ejes, mandos) con la salida limpia al Hall de la r83.
        this._palaSalirAsk = false;
        this.closeMenu();
        this.exitCalib();
        break;
      case 'pala:no':
        // r79 · seguir ajustando: el menú se cierra, el modo sigue vivo
        this._palaSalirAsk = false;
        this.closeMenu();
        break;
""",
"""      case 'pala':
        // r85 · FIX RAÍZ del panel «cosmético» (informe del dueño: «no se
        // puede salir… un panel que no hace nada»): el switch compara el
        // PREFIJO anterior al primer ':' — los casos escritos como
        // 'pala:si'/'pala:no' JAMÁS casaban (ns era 'pala') y la
        // autorización SÍ/NO del ajuste era decorativa. SÍ = recoger el
        // ajuste (passthrough, ejes, mandos) con la salida limpia al Hall
        // de la r83 · NO = seguir ajustando con el menú cerrado.
        if (arg === 'si') {
          this._palaSalirAsk = false;
          this.closeMenu();
          this.exitCalib();
        } else if (arg === 'no') {
          this._palaSalirAsk = false;
          this.closeMenu();
        }
        break;
""",
"FIX A: case 'pala' con despacho por arg (SÍ/NO vivos)")

# ════════════════════════════════════════════════════════════════════════
# c12 · FIX B — toggleMenu: el guard comía el cierre durante el ajuste
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""  toggleMenu() {
    if (this.calib) return;   // en entrenamiento manda el panel propio
""",
"""  toggleMenu() {
    // r85 · FIX «ya no es posible cerrar el menú»: el guard antiguo
    // (`if (this.calib) return`) también comía el AJUSTE DE PALA, cuya
    // interfaz ES el menú común (B abre, «CERRAR MENÚ» y «NO» cierran) —
    // el menú quedaba INCIERRABLE durante el ajuste. El paraguas del
    // entrenamiento clásico sigue bloqueado (allí manda su panel propio).
    if (this.calib && !this.calibPala) return;
""",
"FIX B1: toggleMenu permite cerrar durante calibPala")

# — rama de APERTURA: la ventana del ajuste se aparta mientras el menú manda
p(C12,
"""      this.menuPin = true;
      this._menuPinDraw();
      this.anchorMenu(true);      // r69: nace delante de la mirada y fijo
""",
"""      this.menuPin = true;
      this._menuPinDraw();
      // r85 · en el AJUSTE DE PALA el menú manda: su ventana de información
      // se aparta mientras se lee el menú (vuelve al cerrarlo).
      if (this.calibPala && this.calibPanel) {
        this.calibPanel.group.visible = false;
      }
      this.anchorMenu(true);      // r69: nace delante de la mirada y fijo
""",
"FIX C: apertura del menú aparta la ventana del ajuste")

# — rama de CIERRE: la ventana del ajuste vuelve (el modo sigue vivo)
p(C12,
"""    } else {
      this.menuFxInicia('out');   // r81 · FASE 177: sale de escena (encoge y se funde)
""",
"""    } else {
      // r85 · el ajuste de pala sigue vivo tras cerrar el menú: su ventana
      // de información vuelve a su sitio (el modo nunca se fue).
      if (this.calibPala && this.calibPanel) {
        this.calibPanel.group.visible = true;
      }
      this.menuFxInicia('out');   // r81 · FASE 177: sale de escena (encoge y se funde)
""",
"FIX C: cierre del menú devuelve la ventana del ajuste")

# ════════════════════════════════════════════════════════════════════════
# c12 · FIX B2 — bloque 0.6 (B del mando derecho): calibPala entra
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""    if (presenting && (!this.calib || this.trainV3 || this.trainV3Hub) &&
        this.readButton(this.handIndex('right'), 5)) {
""",
"""    if (presenting && (!this.calib || this.calibPala ||
        this.trainV3 || this.trainV3Hub) &&
        this.readButton(this.handIndex('right'), 5)) {
""",
"FIX B2: B del mando también vive durante calibPala")

# ════════════════════════════════════════════════════════════════════════
# c12 · bloque 0.55 — nace con chincheta y aparta la ventana
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""      this.menuPage = 'optsPala';
      this._palaSalirAsk = true;
      this.menuOpen = true;
      this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
      this.menuHover = [-1, -1];
      this.anchorMenu(true);
      this.drawMenu();
""",
"""      this.menuPage = 'optsPala';
      this._palaSalirAsk = true;
      this.menuOpen = true;
      this.menuPin = true;       // r85 · nace CON CHINCHETA (convención de la casa)
      this._menuPinDraw();
      this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
      this.menuHover = [-1, -1];
      if (this.calibPanel) this.calibPanel.group.visible = false;   // r85 · el menú manda: la ventana se aparta
      this.anchorMenu(true);
      this.drawMenu();
""",
"bloque 0.55: chincheta + ventana apartada")

# ════════════════════════════════════════════════════════════════════════
# c12 · FIX C — exitCalib: pregunta vieja y ancla heredada fuera
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""    const eraPala = !!this.calibPala;
    this.calib = false;
    this.calibPala = false;
    this.calibPanel.group.visible = false;
""",
"""    const eraPala = !!this.calibPala;
    this.calib = false;
    this.calibPala = false;
    this.calibPanel.group.visible = false;
    // r85 · la ventana se RECOGE DE VERDAD: sin pregunta vieja (que
    // reaparecía en AJUSTES›PALA) y con la posición a cero — la próxima
    // entrada nace FRONTAL exacta (el lerp 0,35 ya no arrastra la ancla
    // de la sesión anterior: «la ventana se arrastra hacia otros menús»).
    this._palaSalirAsk = false;
    this.calibPanel.group.position.set(0, 0, 0);
""",
"FIX C: exitCalib resetea pregunta y ancla de la ventana")

# ════════════════════════════════════════════════════════════════════════
# c12 · FIX C — palaRecoger: la ventana TAMBIÉN se recoge aquí
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""  palaRecoger() {
    if (!this.calibPala) return;
    this.calibPala = false;
    this._palaAxesOff();
    this._palaMandosOff();
    this._pstRestaurar();
  }
""",
"""  palaRecoger() {
    if (!this.calibPala) return;
    this.calibPala = false;
    // r85 · ESTANQUEIDAD: la ventana de información se recoge AQUÍ TAMBIÉN.
    // Los caminos de entrenamiento/tutorial que llaman palaRecoger dejaban
    // el panel flotando en la escena para siempre (informe del dueño: «se
    // arrastra hacia otros menús y no desaparece»). Posición a cero: la
    // próxima entrada nace FRONTAL exacta.
    this._palaSalirAsk = false;
    this.calibPanel.group.visible = false;
    this.calibPanel.group.position.set(0, 0, 0);
    this._palaAxesOff();
    this._palaMandosOff();
    this._pstRestaurar();
  }
""",
"FIX C: palaRecoger oculta la ventana de información")

# ════════════════════════════════════════════════════════════════════════
# c12 · estado de menú: init de la autorización y de la tienda
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""    this.menuHover = [-1, -1];   // hover INDEPENDIENTE por mando (v2.16)
""",
"""    this.menuHover = [-1, -1];   // hover INDEPENDIENTE por mando (v2.16)
    this._palaSalirAsk = false;  // r85 · autorización de salida del ajuste
    this._tiendaCompra = null;   // r85 · TIENDA CRAZY: compra pendiente {tipo, id}
""",
"init: _palaSalirAsk y _tiendaCompra en el constructor")

# ════════════════════════════════════════════════════════════════════════
# c12 · closeMenu y 'page': la tienda es estado de página, muere con ella
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""  closeMenu() {
    this._resetArm = false;   // v2.66: cerrar el menú desarma el borrado
""",
"""  closeMenu() {
    this._resetArm = false;   // v2.66: cerrar el menú desarma el borrado
    this._tiendaCompra = null;   // r85 · la tienda no sobrevive al cierre
""",
"closeMenu limpia la tienda")

p(C12,
"""        // r81 · + optsRendi (RENDIMIENTO: autocalibrador de FPS).
        if (arg === 'main' || arg === 'champs' || arg === 'champhist' || arg === 'opts' ||
""",
"""        // r81 · + optsRendi (RENDIMIENTO: autocalibrador de FPS).
        this._tiendaCompra = null;   // r85 · la tienda no sobrevive a la navegación
        if (arg === 'main' || arg === 'champs' || arg === 'champhist' || arg === 'opts' ||
""",
"'page' limpia la tienda")

# ════════════════════════════════════════════════════════════════════════
# c12 · MONEDERO + TIENDA: accessors tras _mesaLockTxt
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""    return '';
  }
  /** r96 · definición de aspecto por id (con guard de recompensas). */
""",
"""    return '';
  }
  /* ---------- r85 · ECONOMÍA CRAZY: MONEDERO + TIENDA -------------------
   * Las monedas viven en ppxr_stats_v1 (recordMatch las gana JUGANDO:
   * +25 victoria · +8 derrota) y las compras en pp_compras (JSON
   * ['mesa:oro', 'bola:saturno'…]). Un aspecto es seleccionable si su
   * hito está superado O está comprado. El clic sobre uno bloqueado con
   * precio abre la TIENDA (modal de confirmación en la propia página). */
  _comprado(tipo, id) {
    try {
      const arr = JSON.parse(localStorage.getItem('pp_compras') || '[]');
      return Array.isArray(arr) && arr.indexOf(tipo + ':' + id) >= 0;
    } catch { return false; }
  }
  _comprar(tipo, id, coste) {
    const mon = ((this.stats && this.stats.data.monedas) || 0) | 0;
    if (mon < coste) return false;
    this.stats.data.monedas = mon - coste;
    if (this.stats && this.stats.save) this.stats.save();
    try {
      const arr = JSON.parse(localStorage.getItem('pp_compras') || '[]');
      if (Array.isArray(arr) && arr.indexOf(tipo + ':' + id) < 0) {
        arr.push(tipo + ':' + id);
        localStorage.setItem('pp_compras', JSON.stringify(arr));
      }
    } catch { /* */ }
    return true;
  }
  /** ¿El aspecto (MESA_ASPECTOS/BOLA_ASPECTOS) es seleccionable? Hito
   *  superado O comprado (r85). */
  _aspectoLibre(tipo, def) {
    if (def.lock && this._mesaLibre(def.lock)) return true;
    return this._comprado(tipo, def.id);
  }
  /** r96 · definición de aspecto por id (con guard de recompensas). */
""",
"accessors del monedero y compras")

# ════════════════════════════════════════════════════════════════════════
# c12 · _mesaSkinDef/_bolaSkinDef: comprado desbloquea al cargar
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""  _mesaSkinDef(skinId) {
    let skin = MESA_ASPECTOS.find((s) => s.id === skinId) || MESA_ASPECTOS[0];
    if (skin.lock && !this._mesaLibre(skin.lock)) skin = MESA_ASPECTOS[0];
    return skin;
  }
""",
"""  _mesaSkinDef(skinId) {
    let skin = MESA_ASPECTOS.find((s) => s.id === skinId) || MESA_ASPECTOS[0];
    // r85 · comprado cuenta: la economía desbloquea sin esperar el hito
    if (skin.lock && !this._mesaLibre(skin.lock) &&
        !this._comprado('mesa', skin.id)) skin = MESA_ASPECTOS[0];
    return skin;
  }
""",
"_mesaSkinDef honra las compras")

p(C12,
"""  /** definición por id CON candado (para elegir la PROPIA skin). */
  _bolaSkinDef(skinId) {
    let sk = BOLA_ASPECTOS.find((s) => s.id === skinId) || BOLA_ASPECTOS[0];
    if (sk.lock && !this._mesaLibre(sk.lock)) sk = BOLA_ASPECTOS[0];
    return sk;
  }
""",
"""  /** definición por id CON candado (para elegir la PROPIA skin).
   *  r85 · comprado cuenta: la economía desbloquea sin esperar el hito. */
  _bolaSkinDef(skinId) {
    let sk = BOLA_ASPECTOS.find((s) => s.id === skinId) || BOLA_ASPECTOS[0];
    if (sk.lock && !this._mesaLibre(sk.lock) &&
        !this._comprado('bola', sk.id)) sk = BOLA_ASPECTOS[0];
    return sk;
  }
""",
"_bolaSkinDef honra las compras")

# ════════════════════════════════════════════════════════════════════════
# c12 · página SALAMESA: modal de tienda + monedero + rejilla con precio
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""      case 'salamesa': {
        // r96/r98 · MESA: altura con LECTURA viva (se agarra en 3D) y
        // −/+ a banda completa; aspectos en grid 3 col; retos como filas.
        const ocup = this.mesaOcupada();
""",
"""      case 'salamesa': {
        // r96/r98 · MESA: altura con LECTURA viva (se agarra en 3D) y
        // −/+ a banda completa; aspectos en grid 3 col; retos como filas.
        // r85 · TIENDA CRAZY: modal de compra de aspecto con monedas
        if (this._tiendaCompra && this._tiendaCompra.tipo === 'mesa') {
          const skT = MESA_ASPECTOS.find((x) => x.id === this._tiendaCompra.id);
          if (skT && skT.coste) {
            const monT = ((this.stats && this.stats.data.monedas) || 0) | 0;
            const faltaT = Math.max(0, skT.coste - monT);
            items.push(
              { tipo: 'titulo', et: T('shop_t'), col: '#ffd257' },
              { tipo: 'lectura', et: T('shop_ask', { v: T(skT.nameKey), n: skT.coste }),
                f: 24, col: '#e9edf2' },
              { tipo: 'lectura', col: faltaT ? '#ffa94d' : '#8ce99a', f: 19,
                et: T('mon_bal', { n: monT }) +
                  (faltaT ? ' · ' + T('shop_falta', { n: faltaT }) : '') },
              { tipo: 'lectura', et: T('mon_hint'), col: '#93a1b0', f: 17 },
              { tipo: 'filaN', wFr: [0.5, 0.5], cells: [
                { id: 'shop:si', et: T('shop_buy', { n: skT.coste }), act: true,
                  grad: ['#f0873f', '#d05c1f'] },
                { id: 'shop:no', et: T('shop_cancel') },
              ] },
            );
            break;
          }
          this._tiendaCompra = null;
        }
        const ocup = this.mesaOcupada();
""",
"salamesa: modal de tienda")

p(C12,
"""          { tipo: 'titulo', et: T('mesa_aspecto_lbl'), col: '#98a6b4' },
          { tipo: 'grid', cols: 3, fs: 20,
            celdas: MESA_ASPECTOS.map((s) => ({
              id: 'mesa_skin:' + s.id, et: T(s.nameKey),
              act: this.mesaSkin === s.id,
              check: this.mesaSkin === s.id,
              lock: !!(s.lock && !this._mesaLibre(s.lock)),
            })) },
        );
        if (MESA_ASPECTOS.some((s) => s.lock && !this._mesaLibre(s.lock))) {
          items.push({ tipo: 'lectura', et: T('mesa_lock_hint'),
            col: '#93a1b0', f: 17 });
        }
""",
"""          { tipo: 'titulo', et: T('mesa_aspecto_lbl'), col: '#98a6b4' },
          { tipo: 'lectura', col: '#ffd257', f: 20,
            et: T('mon_bal', { n: ((this.stats && this.stats.data.monedas) || 0) | 0 }) +
              ' · ' + T('mon_hint') },
          { tipo: 'grid', cols: 3, fs: 20,
            celdas: MESA_ASPECTOS.map((s) => ({
              id: 'mesa_skin:' + s.id, et: T(s.nameKey),
              act: this.mesaSkin === s.id,
              check: this.mesaSkin === s.id,
              lock: !this._aspectoLibre('mesa', s),   // r85 · hito superado O comprado
              precio: s.coste || 0,
            })) },
        );
        if (MESA_ASPECTOS.some((s) => !this._aspectoLibre('mesa', s))) {
          items.push({ tipo: 'lectura', et: T('shop_hint'),
            col: '#93a1b0', f: 17 });
        }
""",
"salamesa: monedero + rejilla con precio")

# ════════════════════════════════════════════════════════════════════════
# c12 · página SALABOLA: modal de tienda + monedero + rejilla con precio
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""      case 'salabola': {
        // r21 · BOLA: 16 skins (clásicas + locura + planetas), candados
        items.push(
          { tipo: 'titulo', et: T('bola_aspecto_lbl'), col: '#98a6b4' },
          { tipo: 'grid', cols: 3, fs: 20,
            celdas: BOLA_ASPECTOS.map((s) => ({
              id: 'bola_skin:' + s.id, et: T(s.nameKey),
              act: this._bolaSkinLS() === s.id,
              check: this._bolaSkinLS() === s.id,
              lock: !!(s.lock && !this._mesaLibre(s.lock)),
            })) },
        );
        if (BOLA_ASPECTOS.some((s) => s.lock && !this._mesaLibre(s.lock))) {
          items.push({ tipo: 'lectura', et: T('mesa_lock_hint'),
            col: '#93a1b0', f: 17 });
        }
""",
"""      case 'salabola': {
        // r21 · BOLA: 16 skins (clásicas + locura + planetas), candados
        // r85 · TIENDA CRAZY: modal de compra de aspecto con monedas
        if (this._tiendaCompra && this._tiendaCompra.tipo === 'bola') {
          const skT = BOLA_ASPECTOS.find((x) => x.id === this._tiendaCompra.id);
          if (skT && skT.coste) {
            const monT = ((this.stats && this.stats.data.monedas) || 0) | 0;
            const faltaT = Math.max(0, skT.coste - monT);
            items.push(
              { tipo: 'titulo', et: T('shop_t'), col: '#ffd257' },
              { tipo: 'lectura', et: T('shop_ask', { v: T(skT.nameKey), n: skT.coste }),
                f: 24, col: '#e9edf2' },
              { tipo: 'lectura', col: faltaT ? '#ffa94d' : '#8ce99a', f: 19,
                et: T('mon_bal', { n: monT }) +
                  (faltaT ? ' · ' + T('shop_falta', { n: faltaT }) : '') },
              { tipo: 'lectura', et: T('mon_hint'), col: '#93a1b0', f: 17 },
              { tipo: 'filaN', wFr: [0.5, 0.5], cells: [
                { id: 'shop:si', et: T('shop_buy', { n: skT.coste }), act: true,
                  grad: ['#f0873f', '#d05c1f'] },
                { id: 'shop:no', et: T('shop_cancel') },
              ] },
            );
            break;
          }
          this._tiendaCompra = null;
        }
        items.push(
          { tipo: 'titulo', et: T('bola_aspecto_lbl'), col: '#98a6b4' },
          { tipo: 'lectura', col: '#ffd257', f: 20,
            et: T('mon_bal', { n: ((this.stats && this.stats.data.monedas) || 0) | 0 }) +
              ' · ' + T('mon_hint') },
          { tipo: 'grid', cols: 3, fs: 20,
            celdas: BOLA_ASPECTOS.map((s) => ({
              id: 'bola_skin:' + s.id, et: T(s.nameKey),
              act: this._bolaSkinLS() === s.id,
              check: this._bolaSkinLS() === s.id,
              lock: !this._aspectoLibre('bola', s),   // r85 · hito superado O comprado
              precio: s.coste || 0,
            })) },
        );
        if (BOLA_ASPECTOS.some((s) => !this._aspectoLibre('bola', s))) {
          items.push({ tipo: 'lectura', et: T('shop_hint'),
            col: '#93a1b0', f: 17 });
        }
""",
"salabola: tienda + monedero + rejilla con precio")

# ════════════════════════════════════════════════════════════════════════
# c12 · despachos mesa_skin/bola_skin → economía + TIENDA + case 'shop'
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""        const skin = MESA_ASPECTOS.find((s) => s.id === arg);
        if (skin) {
          if (skin.lock && !this._mesaLibre(skin.lock)) {
            this.rules.message = this._mesaLockTxt(skin.lock) || T('mesa_lock_hint');
            this.audio.playOsc(330, 260, 0.12, 'sine', 0.16, 0);
          } else {
            try { localStorage.setItem('pp_mesaskin', skin.id); } catch { /* */ }
            this._mesaTinte(skin);   // r96: la altura NO se toca, sólo el tinte
            this.rules.message = T('msg_mesa_skin', { v: T(skin.nameKey) });
            this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
          }
        }
        this.drawMenu();
        break;
""",
"""        const skin = MESA_ASPECTOS.find((s) => s.id === arg);
        if (skin) {
          if (!this._aspectoLibre('mesa', skin)) {
            // r85 · ECONOMÍA: bloqueado — con precio abre la TIENDA (compra
            // con monedas); sin precio repite el texto del hito.
            if (skin.coste) {
              this._tiendaCompra = { tipo: 'mesa', id: skin.id };
              this.audio.playOsc(520, 780, 0.08, 'sine', 0.12, 0);
            } else {
              this.rules.message = this._mesaLockTxt(skin.lock) || T('mesa_lock_hint');
              this.audio.playOsc(330, 260, 0.12, 'sine', 0.16, 0);
            }
          } else {
            try { localStorage.setItem('pp_mesaskin', skin.id); } catch { /* */ }
            this._mesaTinte(skin);   // r96: la altura NO se toca, sólo el tinte
            this.rules.message = T('msg_mesa_skin', { v: T(skin.nameKey) });
            this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
          }
        }
        this.drawMenu();
        break;
""",
"mesa_skin: economía + tienda")

p(C12,
"""        const skB = BOLA_ASPECTOS.find((s) => s.id === arg);
        if (skB) {
          if (skB.lock && !this._mesaLibre(skB.lock)) {
            this.rules.message = this._mesaLockTxt(skB.lock) || T('mesa_lock_hint');
            this.audio.playOsc(330, 260, 0.12, 'sine', 0.16, 0);
          } else {
            try { localStorage.setItem('pp_bolaskin', skB.id); } catch { /* */ }
            this._bolaTinte(skB);   // aplica en vivo (champ → oficial)
            this.rules.message = T('msg_bola_skin', { v: T(skB.nameKey) });
            this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
          }
        }
        this.drawMenu();
        break;
""",
"""        const skB = BOLA_ASPECTOS.find((s) => s.id === arg);
        if (skB) {
          if (!this._aspectoLibre('bola', skB)) {
            // r85 · ECONOMÍA: bloqueado — con precio abre la TIENDA (compra
            // con monedas); sin precio repite el texto del hito.
            if (skB.coste) {
              this._tiendaCompra = { tipo: 'bola', id: skB.id };
              this.audio.playOsc(520, 780, 0.08, 'sine', 0.12, 0);
            } else {
              this.rules.message = this._mesaLockTxt(skB.lock) || T('mesa_lock_hint');
              this.audio.playOsc(330, 260, 0.12, 'sine', 0.16, 0);
            }
          } else {
            try { localStorage.setItem('pp_bolaskin', skB.id); } catch { /* */ }
            this._bolaTinte(skB);   // aplica en vivo (champ → oficial)
            this.rules.message = T('msg_bola_skin', { v: T(skB.nameKey) });
            this.audio.playOsc(720, 900, 0.06, 'sine', 0.14, 0);
          }
        }
        this.drawMenu();
        break;
""",
"bola_skin: economía + tienda")

p(C12,
"""      case 'hall_var': {
        // r24 · ARTE DEL HALL: museo clásico o LA CABAÑA (10 victorias,
""",
"""      case 'shop': {
        // r85 · TIENDA CRAZY — compra del aspecto pendiente (_tiendaCompra).
        // El despacho vive en el PREFIJO ('shop' + arg si/no): la lección
        // del panel SÍ/NO muerto ('pala:si' jamás casaba en el switch del
        // ns). Comprado = seleccionado (misma vía que el clic de skin).
        const tc = this._tiendaCompra;
        this._tiendaCompra = null;
        if (tc && arg === 'si') {
          const def = tc.tipo === 'mesa'
            ? MESA_ASPECTOS.find((x) => x.id === tc.id)
            : BOLA_ASPECTOS.find((x) => x.id === tc.id);
          if (def && def.coste) {
            if (this._comprar(tc.tipo, tc.id, def.coste)) {
              try { localStorage.setItem(
                tc.tipo === 'mesa' ? 'pp_mesaskin' : 'pp_bolaskin', def.id);
              } catch { /* */ }
              if (tc.tipo === 'mesa') this._mesaTinte(def);
              else this._bolaTinte(def);
              this.rules.message = T('shop_ok', { v: T(def.nameKey), n: def.coste });
              this.audio.playOsc(720, 1180, 0.12, 'triangle', 0.16, 0);
            } else {
              this.rules.message = T('shop_falta', { n: def.coste });
              this.audio.playOsc(330, 260, 0.12, 'sine', 0.14, 0);
            }
          }
        }
        this.drawMenu();
        break;
      }
      case 'hall_var': {
        // r24 · ARTE DEL HALL: museo clásico o LA CABAÑA (10 victorias,
""",
"case 'shop': compra con monedas")

# ════════════════════════════════════════════════════════════════════════
# c12 · rejilla: celda bloqueada con PRECIO (nombre · moneda + precio)
# ════════════════════════════════════════════════════════════════════════
p(C12,
"""          const txI = bx + (cl.icono ? 22 + icoR * 2 : 14);
          const maxw = cellW - (txI - bx) - 10 - (hasCheck ? 40 : 0) - delW;
          etq(cl.et, txI, by + cellH * 0.54, maxw, it.fs || 21, 700,
            cl.act ? '#ffe9a8' : 'rgba(255,255,255,0.95)');
""",
"""          const txI = bx + (cl.icono ? 22 + icoR * 2 : 14);
          const maxw = cellW - (txI - bx) - 10 - (hasCheck ? 40 : 0) - delW;
          if (cl.lock && cl.precio) {
            // r85 · ECONOMÍA CRAZY: celda bloqueada con PRECIO — fila doble
            // (nombre arriba · moneda dorada + precio abajo, candado a la derecha)
            etq(cl.et, txI, by + cellH * 0.36, maxw, it.fs || 21, 700,
              cl.act ? '#ffe9a8' : 'rgba(255,255,255,0.95)');
            c.fillStyle = '#ffd257';
            c.beginPath();
            c.arc(txI + 9, by + cellH * 0.72, 8, 0, Math.PI * 2);
            c.fill();
            c.fillStyle = '#8a6a12';
            c.font = '800 10px system-ui, sans-serif';
            c.textAlign = 'center';
            c.textBaseline = 'middle';
            c.fillText('C', txI + 9, by + cellH * 0.72 + 0.5);
            c.textAlign = 'left';
            c.textBaseline = 'alphabetic';
            c.font = '800 ' + Math.max(12, (it.fs || 21) - 7) +
              'px system-ui, sans-serif';
            c.fillStyle = '#ffd257';
            c.fillText(String(cl.precio), txI + 21, by + cellH * 0.72 + 5);
          } else {
            etq(cl.et, txI, by + cellH * 0.54, maxw, it.fs || 21, 700,
              cl.act ? '#ffe9a8' : 'rgba(255,255,255,0.95)');
          }
""",
"rejilla: celda con candado + precio")

# ════════════════════════════════════════════════════════════════════════
# c02 · costes de catálogo (mesas 2 · bolas 12 — el hito sigue gratis)
# ════════════════════════════════════════════════════════════════════════
p(C02,
"""  { id: 'oro', top: 0xc9932f, edge: 0x8f6a1e, lock: 'wins10', nameKey: 'mesa_asp_oro' },
  { id: 'carbon', top: 0x171a20, edge: 0x0d0f13, lock: 'streak5', nameKey: 'mesa_asp_carbon' },
""",
"""  { id: 'oro', top: 0xc9932f, edge: 0x8f6a1e, lock: 'wins10', coste: 400, nameKey: 'mesa_asp_oro' },
  { id: 'carbon', top: 0x171a20, edge: 0x0d0f13, lock: 'streak5', coste: 600, nameKey: 'mesa_asp_carbon' },
""",
"c02: coste de las mesas Oro y Carbono")

p(C02,
""" *   · CANDADOS igual que las mesas: lock 'wins10' (10 victorias o 6★ de
 *     retos) y 'streak5' (racha de 5 o 3★) — reutiliza _mesaLibre().
""",
""" *   · CANDADOS igual que las mesas: lock 'wins10' (10 victorias o 6★ de
 *     retos) y 'streak5' (racha de 5 o 3★) — reutiliza _mesaLibre().
 *   · r85 · ECONOMÍA CRAZY: `coste` en monedas — el aspecto también se
 *     COMPRA (TIENDA CRAZY en AJUSTES › SALA/BOLA); el hito sigue siendo
 *     la vía GRATIS (candado superado ⇒ seleccionable sin comprar).
""",
"c02: nota de economía en el catálogo de bolas")

BOLAS_COSTE = [
    ("bola_asp_estrellas", 250, "lock: 'streak5'"),
    ("bola_asp_futbol", 350, "lock: 'wins10'"),
    ("bola_asp_ocho", 350, "lock: 'wins10'"),
    ("bola_asp_ojo", 300, None),
    ("bola_asp_neon", 200, None),
    ("bola_asp_holo", 450, "lock: 'wins10'"),
    ("bola_asp_disco", 400, "lock: 'streak5'"),
    ("bola_asp_marte", 250, None),
    ("bola_asp_luna", 250, None),
    ("bola_asp_tierra", 300, None),
    ("bola_asp_lava", 400, "lock: 'streak5'"),
    ("bola_asp_saturno", 500, "lock: 'wins10'"),
]
for nameKey, coste, lock in BOLAS_COSTE:
    if lock:
        viejo = lock + ", nameKey: '" + nameKey + "'"
        nuevo = lock + ", coste: " + str(coste) + ", nameKey: '" + nameKey + "'"
    else:
        viejo = "lock: null, nameKey: '" + nameKey + "'"
        nuevo = "lock: null, coste: " + str(coste) + ", nameKey: '" + nameKey + "'"
    p(C02, viejo, nuevo, "c02: coste " + nameKey + " = " + str(coste))

# ════════════════════════════════════════════════════════════════════════
# c06 · el monedero vive en ppxr_stats_v1 y recordMatch lo gana
# ════════════════════════════════════════════════════════════════════════
p(C06,
"""      won: 0, lost: 0, streak: 0, bestStreak: 0,
      pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
""",
"""      won: 0, lost: 0, streak: 0, bestStreak: 0,
      pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
      monedas: 0,   // r85 · ECONOMÍA CRAZY: el monedero vive con las stats
""",
"c06: campo monedas en el esquema")

p(C06,
"""    if (!this.data.hoyDia || typeof this.data.hoyDia !== 'object') this.data.hoyDia = { dia: '', v: 0 };
  }
""",
"""    if (!this.data.hoyDia || typeof this.data.hoyDia !== 'object') this.data.hoyDia = { dia: '', v: 0 };
    // r85 · migración tolerante del MONEDERO (datos viejos sin monedas)
    if (typeof this.data.monedas !== 'number') this.data.monedas = 0;
  }
""",
"c06: migración del monedero")

p(C06,
"""    } else {
      this.data.lost++;
      this.data.streak = 0;
    }
    this.save();
    return out;
  }
}
""",
"""    } else {
      this.data.lost++;
      this.data.streak = 0;
    }
    // r85 · ECONOMÍA CRAZY: el monedero se gana JUGANDO — +25 por victoria,
    // +8 por derrota (participar también paga). Alimenta la TIENDA de
    // bolas y mesas (c12 · _comprar) sin tocar ELO, logros ni física.
    this.data.monedas = (this.data.monedas | 0) + (win ? 25 : 8);
    this.save();
    return out;
  }
}
""",
"c06: recordMatch gana monedas")

# ════════════════════════════════════════════════════════════════════════
# c00 · i18n ES/EN — monedero y tienda
# ════════════════════════════════════════════════════════════════════════
p(C00,
"""    // r38 (v3.6.134) · hito del RASCACIELOS
    mesa_lock_won25: 'Hito: 25 victorias',
""",
"""    // r38 (v3.6.134) · hito del RASCACIELOS
    mesa_lock_won25: 'Hito: 25 victorias',
    // r85 · ECONOMÍA CRAZY — monedas y tienda de bolas/mesas
    mon_bal: 'Monedas: {n}',
    mon_hint: 'gana partidos · +25 victoria · +8 derrota',
    shop_t: 'TIENDA CRAZY',
    shop_ask: '¿Comprar «{v}» por {n} monedas?',
    shop_buy: 'COMPRAR · {n}',
    shop_cancel: 'Cancelar',
    shop_ok: '¡«{v}» es tuyo! −{n} monedas',
    shop_falta: 'te faltan {n} monedas',
    shop_hint: 'Los candados se abren con hitos o comprándolos con monedas',
""",
"c00: i18n ES de la economía")

p(C00,
"""    // r38 (v3.6.134) · SKYSCRAPER milestone
    mesa_lock_won25: 'Milestone: 25 wins',
""",
"""    // r38 (v3.6.134) · SKYSCRAPER milestone
    mesa_lock_won25: 'Milestone: 25 wins',
    // r85 · CRAZY ECONOMY — coins and ball/table shop
    mon_bal: 'Coins: {n}',
    mon_hint: 'win matches · +25 win · +8 loss',
    shop_t: 'CRAZY SHOP',
    shop_ask: 'Buy "{v}" for {n} coins?',
    shop_buy: 'BUY · {n}',
    shop_cancel: 'Cancel',
    shop_ok: '"{v}" is yours! −{n} coins',
    shop_falta: 'you need {n} more coins',
    shop_hint: 'Locks open with milestones or by buying them with coins',
""",
"c00: i18n EN de la economía")


def main():
    for fich, viejo, nuevo, et in P:
        t = fich.read_text(encoding='utf-8')
        n = t.count(viejo)
        if n != 1:
            sys.exit('ABORTA (nada escrito aún por este parche): [' + et + '] ' +
                     fich.name + ' · ancla con ' + str(n) +
                     ' apariciones (esperaba 1): ' + viejo[:90].replace('\n', '⏎'))
    print('anclajes verificados: ' + str(len(P)) + ' — escribiendo…')
    tocados = {}
    for fich, viejo, nuevo, et in P:
        t = tocados.get(fich, fich.read_text(encoding='utf-8'))
        tocados[fich] = t.replace(viejo, nuevo, 1)
        print('  OK  ' + fich.name + ' · ' + et)
    for fich, t in tocados.items():
        fich.write_text(t, encoding='utf-8')
    print('escritos: ' + ', '.join(f.name for f in tocados))


if __name__ == '__main__':
    main()
