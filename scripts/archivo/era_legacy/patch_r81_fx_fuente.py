# -*- coding: utf-8 -*-
"""r81 · FASE 177 «MENÚS EN ESCENA» — parche en la FUENTE (src/game/core).

c12_pingponggame.js: P1-P6, P8-P13 (toggle FX, aperturas, menuClick pulso,
flash en troceo, foco vivo, estado FX, tick del bucle, métodos FX).
c13_ui_arranque.js: P7 (salida animada de la academia).
El sello de versión NO va aquí: bump_version.py 3.6.172-SDK6 lo hace
(regenera public/game.html desde la fuente).
"""
import sys

C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
C13 = '/home/z/my-project/src/game/core/c13_ui_arranque.js'
T12 = open(C12, encoding='utf-8').read()
T13 = open(C13, encoding='utf-8').read()
N12, N13 = len(T12), len(T13)
PARCHES = []


def parche(nombre, viejo, nuevo, esperado=1):
    global T12, T13
    # aplica al archivo que contenga el patrón (exactamente una vez)
    for etiqueta, t, fich in (('c12', T12, C12), ('c13', T13, C13)):
        n = t.count(viejo)
        if n == esperado:
            if etiqueta == 'c12':
                T12 = t.replace(viejo, nuevo)
            else:
                T13 = t.replace(viejo, nuevo)
            PARCHES.append(etiqueta + ':' + nombre)
            print('OK  [%s · %s]' % (nombre, etiqueta))
            return
        if n > 1:
            print('FALLO [%s]: %d apariciones en %s' % (nombre, n, etiqueta))
            sys.exit(1)
    print('FALLO [%s]: patrón no encontrado en ninguna fuente' % nombre)
    sys.exit(1)


parche('P1a toggle apertura', """    this.menuOpen = !this.menuOpen;
    this.menuGroup.visible = this.menuOpen;
    for (const l of this.menuLines) l.visible = false;
    for (const d of this.menuDots) d.visible = false;
    this.menuHover = [-1, -1];
    if (this.menuOpen) {
""",
"""    this.menuOpen = !this.menuOpen;
    for (const l of this.menuLines) l.visible = false;
    for (const d of this.menuDots) d.visible = false;
    this.menuHover = [-1, -1];
    if (this.menuOpen) {
      this.menuFxInicia('in');   // r81 · FASE 177: entra en escena (cascada+rebote)
""")

parche('P1b toggle cierre', """    } else {
      this.audio.playOsc(990, 660, 0.06, 'sine', 0.1, 0);
""",
"""    } else {
      this.menuFxInicia('out');   // r81 · FASE 177: sale de escena (encoge y se funde)
      this.audio.playOsc(990, 660, 0.06, 'sine', 0.1, 0);
""")

parche('P2 optsPala (B en ajuste de pala)', """      this.menuPage = 'optsPala';
      this._palaSalirAsk = true;
      this.menuOpen = true;
      this.menuGroup.visible = true;
      this.menuHover = [-1, -1];
""",
"""      this.menuPage = 'optsPala';
      this._palaSalirAsk = true;
      this.menuOpen = true;
      this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
      this.menuHover = [-1, -1];
""")

parche('P3 train (B en entrenamiento)', """        this.menuPage = 'train';
        this.menuOpen = true;
        this.menuGroup.visible = true;
        this.menuHover = [-1, -1];
""",
"""        this.menuPage = 'train';
        this.menuOpen = true;
        this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
        this.menuHover = [-1, -1];
""")

parche('P4 openHallAsk (prompt B)', """    this.menuPage = 'hallask';
    this.menuSec = '';
    this.menuOpen = true;
    this.menuGroup.visible = true;
    this.menuHover = [-1, -1];
""",
"""    this.menuPage = 'hallask';
    this.menuSec = '';
    this.menuOpen = true;
    this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
    this.menuHover = [-1, -1];
""")

parche('P5 opts tras entrenar (Y)', """      this.menuPage = 'opts';
      this.menuOpen = true;
      this.menuGroup.visible = true;
      this.menuHover = [-1, -1];
""",
"""      this.menuPage = 'opts';
      this.menuOpen = true;
      this.menuFxInicia('in');   // r81 · nace EN ESCENA (cascada+rebote)
      this.menuHover = [-1, -1];
""")

parche('P6 HUB directo (arranque VR)', """    this.menuSec = 'match';
    this.menuOpen = true;
    if (this.menuGroup) {
      this.menuGroup.visible = true;
""",
"""    this.menuSec = 'match';
    this.menuOpen = true;
    if (this.menuGroup) {
      this.menuFxInicia('in');   // r81 · el HUB nace EN ESCENA (cascada+rebote)
""")

parche('P7 academia cierre', """        G.menuOpen = false;
        G.menuGroup.visible = false;
""",
"""        G.menuOpen = false;
        G.menuFxInicia('out');   // r81 · la academia sale DE ESCENA
""")

parche('P8 menuClick pulsación viva', """  menuClick(idx, hand) {
    const r = this.menuRects[idx];
    if (!r) return;
""",
"""  menuClick(idx, hand) {
    const r = this.menuRects[idx];
    if (!r) return;
    // r81 · FASE 177 · PULSACIÓN VIVA (feedback de la competencia): flash
    // blanco en la fila pulsada + pulso del arco + haptic fuerte.
    this._menuFlash = { r: { x: r.x, y: r.y, w: r.w, h: r.h },
      t0: performance.now() };
    this._menuFlashRepinta = 0;
    this.menuFxInicia('pulse');
    this.haptic(hand, 0.5, 55);
""")

parche('P9 flash en el troceo', """  _menuTexSube() {
    const li = CONFIG_MENUS.lienzo;
""",
"""  _menuTexSube() {
    const li = CONFIG_MENUS.lienzo;
    // r81 · FASE 177 · FLASH de pulsación: velo blanco sobre la fila
    // pulsada, horneado en el troceo; decae con los repintados vivos
    // (menuFxTick re-pinta a 60 ms mientras el flash esté vivo).
    const fl = this._menuFlash;
    if (fl) {
      const dtF = performance.now() - fl.t0;
      if (dtF >= 170) this._menuFlash = null;
      else {
        const aF = 0.5 * (1 - dtF / 170);
        const cF = this.menuCanvas.getContext('2d');
        cF.save();
        cF.fillStyle = 'rgba(255,255,255,' + aF.toFixed(3) + ')';
        cF.beginPath();
        if (cF.roundRect) cF.roundRect(fl.r.x, fl.r.y, fl.r.w, fl.r.h, 14);
        else cF.rect(fl.r.x, fl.r.y, fl.r.w, fl.r.h);
        cF.fill();
        cF.restore();
      }
    }
""")

parche('P10 foco vivo', """      if (idx !== this.menuHover[h]) { this.menuHover[h] = idx; dirty = true; }
""",
"""      if (idx !== this.menuHover[h]) {
        this.menuHover[h] = idx; dirty = true;
        // r81 · FASE 177 · FOCO VIVO: tick sonoro + haptic al ganar el
        // foco una fila (la competencia navega «con vida»).
        if (idx >= 0) {
          try { this.audio.playOsc(1180, 1180, 0.028, 'sine', 0.05, 0); } catch (eFoco) { /* */ }
          if (this.renderer.xr && this.renderer.xr.isPresenting) {
            this.haptic(h, 0.15, 18);
          }
        }
      }
""")

parche('P11 estado FX', """    this.menuPin = true;              // r68: ON por defecto (petición expresa)
    this._menuAnchorEst = '';         // r114: estancia donde nació el ancla
""",
"""    // r81 · FASE 177 · estado del FX de entrada/salida/pulso del arco
    this._menuFxCascada = null;
    this._menuFxOut = 0;
    this._menuFxPulso = 0;
    this._menuFlash = null;
    this._menuFlashRepinta = 0;
    this.menuPin = true;              // r68: ON por defecto (petición expresa)
    this._menuAnchorEst = '';         // r114: estancia donde nació el ancla
""")

parche('P12 tick en el bucle', """    if (presenting && (this.menuOpen || this.inHall || this._arconoOn)) {
      this.updateMenu(dt);   // r87: dt para el pulso del medallón
    }
""",
"""    if (presenting && (this.menuOpen || this.inHall || this._arconoOn)) {
      this.updateMenu(dt);   // r87: dt para el pulso del medallón
    }
    this.menuFxTick();   // r81 · vida del arco (cascada/pulso/salida), con o sin menú
""")

FX = """  /* r81 · FASE 177 «MENÚS EN ESCENA» — el arco ENTRA con cascada
   * (panela C primero, lados +70 ms) con rebote easeOutBack y fundido,
   * SALE encogiendo y desvaneciendo, y cada PULSACIÓN respira
   * (pulso 1→1.03→1 del arco). El ancla fija r69/r114 NO se toca:
   * el FX sólo escala panelas y opacidad, nunca recoloca el grupo. */
  menuFxInicia(dir) {
    if (!this.menuGroup) return;
    const ahora = performance.now();
    if (dir === 'in') {
      this.menuGroup.visible = true;
      this._menuFxOut = 0;
      this._menuFxPulso = 0;
      const tC = ahora, tL = ahora + 70, tR = ahora + 70;
      this._menuFxCascada = { C: tC, L: tL, R: tR };
    } else if (dir === 'out') {
      if (!this.menuGroup.visible) return;
      this._menuFxCascada = null;
      this._menuFxPulso = 0;
      this._menuFxOut = ahora;
    } else if (dir === 'pulse') {
      if (this._menuFxOut) return;   // nunca pisa una salida en curso
      this._menuFxPulso = ahora;
    }
    this.menuFxTick();
  }

  menuFxTick() {
    const ahora = performance.now();
    const meshes = [this._menuPanelaDe && this._menuPanelaDe.L,
      this._menuPanelaDe && this._menuPanelaDe.C,
      this._menuPanelaDe && this._menuPanelaDe.R];
    // SALIDA: encoge + funde (150 ms, easeInQuad) y esconde al terminar
    if (this._menuFxOut) {
      const p = Math.min(1, (ahora - this._menuFxOut) / 150);
      const e = p * p;
      for (const m of meshes) {
        if (!m) continue;
        m.scale.setScalar(1 - 0.12 * e);
        m.material.opacity = 1 - e;
      }
      if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1 - e;
      if (p >= 1) {
        this.menuGroup.visible = false;
        this._menuFxOut = 0;
        for (const m of meshes) {
          if (!m) continue;
          m.scale.setScalar(1);
          m.material.opacity = 1;
        }
        if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1;
      }
      return;
    }
    // ENTRADA: cascada por panela (C, luego L/R) con rebote y fundido
    if (this._menuFxCascada) {
      let fin = true;
      const eOB = (p) => {
        const c1 = 1.70158, c3 = c1 + 1;
        return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
      };
      for (const id of ['C', 'L', 'R']) {
        const m = this._menuPanelaDe[id];
        if (!m) continue;
        const p = Math.min(1, Math.max(0,
          (ahora - this._menuFxCascada[id]) / 320));
        if (p < 1) fin = false;
        m.scale.setScalar(0.82 + 0.18 * eOB(p));
        m.material.opacity = Math.min(1, p * 1.6);
      }
      if (this._menuPinMesh) {
        const pC = Math.min(1, Math.max(0,
          (ahora - this._menuFxCascada.C) / 320));
        this._menuPinMesh.material.opacity = Math.min(1, pC * 1.6);
      }
      if (fin) this._menuFxCascada = null;
      return;
    }
    // PULSO de pulsación (130 ms) + repintado del flash a 60 ms
    if (this._menuFxPulso) {
      const p = (ahora - this._menuFxPulso) / 130;
      if (p >= 1) {
        this._menuFxPulso = 0;
        this.menuGroup.scale.setScalar(1);
      } else {
        this.menuGroup.scale.setScalar(1 + 0.03 * Math.sin(Math.PI * p));
      }
      if (this._menuFlash && ahora - (this._menuFlashRepinta || 0) >= 60) {
        this._menuFlashRepinta = ahora;
        this.drawMenu();
      }
      return;
    }
    // flash residual sin pulso (el pulso acabó antes que el flash)
    if (this._menuFlash) {
      if (performance.now() - this._menuFlash.t0 >= 170) {
        this._menuFlash = null;
      } else if (ahora - (this._menuFlashRepinta || 0) >= 60) {
        this._menuFlashRepinta = ahora;
        this.drawMenu();
      }
    }
  }

  anchorMenu(forzar) {"""
parche('P13 métodos FX', "  anchorMenu(forzar) {", FX)

open(C12, 'w', encoding='utf-8').write(T12)
open(C13, 'w', encoding='utf-8').write(T13)
print('\nAPLICADOS: %d parches · c12 %+d B · c13 %+d B' %
      (len(PARCHES), len(T12) - N12, len(T13) - N13))
