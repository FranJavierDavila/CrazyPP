#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_r83_fase179.py — r83 · FASE 179 «MENÚS NÍTIDOS» · parche del FUENTE
(src/game/core/c12_pingponggame.js; bump_version regenera el build).

Informe del dueño tras la V3.6.173 en el visor:
  1. «Los menús se leen muy mal, están muy borrosos» — el r82 puso mips+
     trilineal para el crawl del FX r81, pero el lienzo tiene 1.474
     texels/m frente a ~800-900 px/m de pantalla a 1,15 m: el trilinear
     mezcla el mip 1 y SUAVIZA el texto. Vuelta al r105 (bilinear, sin
     mips: nítido, probado) Y el FX deja de ESCALAR (causa del crawl):
     anima POSICIÓN+OPACIDAD y el pulso BRILLA POR COLOR.
  2. «El deslizador de campeonatos está mal maquetado y no permite
     deslizarlo con el mando» — DOS bugs: (a) _menuDragUpdate trataba el
     arrastre de 'chmus' como volumen de FX (la barra se quedaba quieta);
     (b) la etiqueta pisaba el botón − y la leyenda del pie (y=1348)
     rozaba la caja de la banda (1254-1334).
  3. «Quiero un barrido de luz estilo la competencia» — BARRIDO DE LUZ:
     banda aditiva que cruza cada panela (C→lados, 850 ms, cada 7 s con
     el menú abierto), GPU pura (position.x+opacity, cero repintados),
     raycast anulado, sin strobe.

Cada parche exige su conteo exacto: si algo no casa, ABORTA sin escribir.
"""
import sys

F = '/home/z/my-project/src/game/core/c12_pingponggame.js'
t = open(F, encoding='utf-8').read()
orig = t
PARCHES = []


def parche(nombre, viejo, nuevo, esperado=1):
    global t
    n = t.count(viejo)
    if n != esperado:
        print('FALLO [%s]: %d apariciones (esperaba %d)' % (nombre, n, esperado))
        print('--- viejo ---')
        print(viejo[:400])
        sys.exit(1)
    t = t.replace(viejo, nuevo)
    PARCHES.append(nombre)
    print('OK  [%s]' % nombre)


# ---------- P1 · texturas del arco: vuelta al r105 (NÍTIDO) ----------
parche('P1 revert mipmaps → r105', """      // r82 · MIPMAPS+ANISO: r105 los quitó («magnificación pura a ~1,15 m»)
      // y con el menú ESTÁTICO era cierto — pero el FX r81 ESCALA las
      // panelas (cascada 0.82→1.06→1 + pulso 1.03) y en minificación el
      // bilinear puro con anisotropy=1 hace CRAWLEAR el texto (aliasing del
      // arco que reportó el dueño). WebGL2 (Quest) admite NPOT con mips;
      // la magnificación sigue Lineal y el coste (mips en trozos de lienzo,
      // ~3 repintados del flash a 60 ms) es despreciable.
      tex.generateMipmaps = true;
      tex.minFilter = THREE.LinearMipmapLinearFilter;
      tex.anisotropy = 4;""",
"""      // r83 · F179 «MENÚS NÍTIDOS»: vuelta al r105 (sin mips, bilinear).
      // El r82 puso mipmaps+trilineal contra el crawl del FX r81 y el
      // dueño reportó el RESULTADO real en el visor: «los menús se leen
      // muy mal, están muy borrosos» — el lienzo tiene ~1.474 texels/m y
      // la pantalla ~800-900 px/m a 1,15 m: el trilinear mezclaba el mip
      // 1 y SUAVIZABA el texto. La causa raíz del crawl era el ESCALADO
      // de panelas del FX (P13) y la F179 lo elimina: el FX anima
      // POSICIÓN+OPACIDAD (nada re-muestrea la textura) y el pulso brilla
      // por color, no por escala.
      tex.generateMipmaps = false;
      tex.minFilter = THREE.LinearFilter;
      tex.anisotropy = 1;""")

# ---------- P2 · barrido de luz: hijo aditivo por panela ----------
parche('P2 sweep meshes', """      this.menuGroup.add(mesh);
      this._menuPanelaDe[pa.id] = mesh;
      if (pa.id === 'C') { this.menuTex = tex; this.menuMesh = mesh; }
    }""",
"""      this.menuGroup.add(mesh);
      this._menuPanelaDe[pa.id] = mesh;
      if (pa.id === 'C') { this.menuTex = tex; this.menuMesh = mesh; }
      // r83 · F179 · BARRIDO DE LUZ (la competencia): banda aditiva que
      // cruza cada panela de lado a lado. Hijo de la panela (hereda yaw y
      // curva), textura gradiente compartida, raycast ANULADO para no
      // estorbar al rayo del menú. GPU pura: menuFxSweep sólo mueve
      // position.x y opacity — cero repintados de lienzo.
      if (!this._menuSweepTex) {
        const cvS = document.createElement('canvas');
        cvS.width = 256;
        cvS.height = 64;
        const cS = cvS.getContext('2d');
        const gS = cS.createLinearGradient(0, 0, 256, 0);
        gS.addColorStop(0, 'rgba(255,238,196,0)');
        gS.addColorStop(0.5, 'rgba(255,238,196,0.9)');
        gS.addColorStop(1, 'rgba(255,238,196,0)');
        cS.fillStyle = gS;
        cS.fillRect(0, 0, 256, 64);
        const vS = cS.createLinearGradient(0, 0, 0, 64);
        vS.addColorStop(0, 'rgba(255,255,255,0.25)');
        vS.addColorStop(0.5, 'rgba(255,255,255,1)');
        vS.addColorStop(1, 'rgba(255,255,255,0.25)');
        cS.globalCompositeOperation = 'destination-in';
        cS.fillStyle = vS;
        cS.fillRect(0, 0, 256, 64);
        const tS = new THREE.CanvasTexture(cvS);
        tS.colorSpace = THREE.SRGBColorSpace;
        this._menuSweepTex = tS;
      }
      const mS = new THREE.Mesh(
        new THREE.PlaneGeometry(pa.anchoM * 0.30, pa.altoM * 1.02),
        new THREE.MeshBasicMaterial({ map: this._menuSweepTex,
          transparent: true, blending: THREE.AdditiveBlending,
          depthWrite: false, depthTest: false, opacity: 0 }));
      mS.position.z = 0.004;
      mS.renderOrder = 9999;
      mS.raycast = () => {};
      mesh.add(mS);
      this._menuSweep = this._menuSweep || { t0: 0, last: 0, meshes: {} };
      this._menuSweep.meshes[pa.id] = mS;
    }""")

# ---------- P3 · estado del sweep en buildMenu ----------
parche('P3 estado sweep', """    this._menuFlash = null;
    this._menuFlashRepinta = 0;
    this.menuPin = true;              // r68: ON por defecto (petición expresa)""",
"""    this._menuFlash = null;
    this._menuFlashRepinta = 0;
    // r83 · F179 · estado del BARRIDO DE LUZ (t0 = barrido en curso)
    this._menuSweep = { t0: 0, last: 0, meshes: {} };
    this._menuSweepTex = null;
    this.menuPin = true;              // r68: ON por defecto (petición expresa)""")

# ---------- P4 · FX sin escala (posición+opacidad+brillo) + menuFxSweep ----------
FX_NUEVO = """  /* r83 · F179 «MENÚS NÍTIDOS» — el FX de la F177 se rehace SIN ESCALA:
   * el informe del dueño tras la V3.6.172/173 es doble («borrosos» +
   * «crawleo»): escalar panelas re-muestrea la textura y SIEMPRE cuesta
   * nitidez (crawlea con bilinear, se suaviza con mips). La F179 anima
   * POSICIÓN (caída con rebote easeOutBack, sobreoscilación espacial no
   * textural) + OPACIDAD, y la PULSACIÓN brilla por COLOR (material.color
   * > 1) — cero re-muestreo, cero mips, texto nítido de la r105. Y estrena
   * el BARRIDO DE LUZ de la competencia (menuFxSweep). El ancla fija
   * r69/r114 NO se toca: nada recoloca el GRUPO ni escala panela alguna. */
  menuFxInicia(dir) {
    if (!this.menuGroup) return;
    const ahora = performance.now();
    if (dir === 'in') {
      this.menuGroup.visible = true;
      this._menuFxOut = 0;
      this._menuFxPulso = 0;
      const tC = ahora, tL = ahora + 70, tR = ahora + 70;
      this._menuFxCascada = { C: tC, L: tL, R: tR };
      for (const id of ['C', 'L', 'R']) {
        const m = this._menuPanelaDe && this._menuPanelaDe[id];
        if (!m) continue;
        m.userData.fxY0 = m.position.y;   // el asiento EXACTO es el de ahora
        m.material.color.setRGB(1, 1, 1); // sin brillo residual de un pulso
      }
      if (this._menuSweep) {
        this._menuSweep.t0 = ahora;       // el barrido estrena la entrada
        this._menuSweep.last = ahora;
      }
    } else if (dir === 'out') {
      if (!this.menuGroup.visible) return;
      this._menuFxCascada = null;
      this._menuFxPulso = 0;
      this._menuFxOut = ahora;
      for (const id of ['C', 'L', 'R']) {
        const m = this._menuPanelaDe && this._menuPanelaDe[id];
        if (!m) continue;
        if (m.userData.fxY0 == null) m.userData.fxY0 = m.position.y;
      }
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
    const eOB = (p) => {
      const c1 = 1.70158, c3 = c1 + 1;
      return 1 + c3 * Math.pow(p - 1, 3) + c1 * Math.pow(p - 1, 2);
    };
    // SALIDA: sube + funde (150 ms, easeInQuad) y esconde al terminar
    if (this._menuFxOut) {
      const p = Math.min(1, (ahora - this._menuFxOut) / 150);
      const e = p * p;
      for (const m of meshes) {
        if (!m) continue;
        m.position.y = m.userData.fxY0 + 0.035 * e;
        m.material.opacity = 1 - e;
      }
      if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1 - e;
      if (p >= 1) {
        this.menuGroup.visible = false;
        this._menuFxOut = 0;
        for (const m of meshes) {
          if (!m) continue;
          m.position.y = m.userData.fxY0;
          m.material.opacity = 1;
          m.material.color.setRGB(1, 1, 1);
        }
        if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1;
      }
      return;
    }
    // ENTRADA: cascada por panela (C, luego L/R) — CAEN desde arriba con
    // rebote easeOutBack en POSICIÓN (la textura jamás se re-muestrea)
    if (this._menuFxCascada) {
      let fin = true;
      for (const id of ['C', 'L', 'R']) {
        const m = this._menuPanelaDe[id];
        if (!m) continue;
        const y0 = m.userData.fxY0 == null
          ? (m.userData.fxY0 = m.position.y) : m.userData.fxY0;
        const p = Math.min(1, Math.max(0,
          (ahora - this._menuFxCascada[id]) / 320));
        if (p < 1) fin = false;
        m.position.y = y0 + 0.09 * (1 - eOB(p));
        m.material.opacity = Math.min(1, p * 1.6);
      }
      if (this._menuPinMesh) {
        const pC = Math.min(1, Math.max(0,
          (ahora - this._menuFxCascada.C) / 320));
        this._menuPinMesh.material.opacity = Math.min(1, pC * 1.6);
      }
      if (fin) {
        this._menuFxCascada = null;
        for (const m of meshes) {
          if (m && m.userData.fxY0 != null) m.position.y = m.userData.fxY0;
        }
      }
      return;
    }
    // PULSO de pulsación (130 ms) por BRILLO (color > 1, sin escala)
    // + repintado del flash a 60 ms
    if (this._menuFxPulso) {
      const p = (ahora - this._menuFxPulso) / 130;
      if (p >= 1) {
        this._menuFxPulso = 0;
        for (const m of meshes) {
          if (m) m.material.color.setRGB(1, 1, 1);
        }
      } else {
        const k = 0.16 * Math.sin(Math.PI * p);
        for (const m of meshes) {
          if (m) m.material.color.setRGB(1 + k, 1 + k, 1 + k * 0.9);
        }
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
    this.menuFxSweep(ahora);   // r83 · el barrido vive también con el menú quieto
  }

  /** r83 · F179 · BARRIDO DE LUZ (la competencia): banda aditiva cruzando
   * cada panela de lado a lado, escalonada C→lados (+120 ms), 850 ms, y
   * cada 7 s mientras el menú está abierto. Sin repintados (GPU pura:
   * position.x + opacity), sin strobe (UNA banda, envolvente sinusoidal,
   * pico 0.34), raycast anulado (no estorba al rayo del menú). */
  menuFxSweep(ahora) {
    const sw = this._menuSweep;
    if (!sw || !this.menuGroup) return;
    if (!sw.t0) {
      if (this.menuOpen && this.menuGroup.visible &&
          ahora - (sw.last || 0) >= 7000) {
        sw.t0 = ahora;
        sw.last = ahora;
      } else {
        return;
      }
    }
    const DUR = 850, RET = 120;
    let vivo = false;
    for (const id of ['C', 'L', 'R']) {
      const mS = sw.meshes[id];
      if (!mS || !mS.parent) continue;
      const paS = mS.parent.userData.panela;
      const ret = id === 'C' ? 0 : RET;
      const ps = (ahora - sw.t0 - ret) / DUR;
      if (ps <= 0) { mS.material.opacity = 0; vivo = true; continue; }
      if (ps >= 1) { mS.material.opacity = 0; continue; }
      vivo = true;
      const medio = mS.geometry.parameters.width / 2;
      const largo = paS.anchoM + medio * 2;
      mS.position.x = -paS.anchoM / 2 - medio + largo * ps;
      mS.material.opacity = 0.34 * Math.sin(Math.PI * ps);
    }
    if (!vivo) sw.t0 = 0;
  }

  anchorMenu(forzar) {"""

i = t.find("  /* r81 · FASE 177 «MENÚS EN ESCENA» — el arco ENTRA con cascada")
j = t.find("\n  anchorMenu(forzar) {", i)
if i < 0 or j < 0 or j - i > 9000:
    print(f'FALLO [P4 bloque FX]: anclajes i={i} j={j}')
    sys.exit(1)
t = t[:i] + FX_NUEVO + t[j:]
PARCHES.append('P4 FX sin escala + menuFxSweep')
print('OK  [P4 FX sin escala + menuFxSweep]')

# ---------- P5 · ARREGLO del arrastre de chmus ----------
parche('P5 drag chmus', """    const frac = this._menuSliderFrac(r, (this._menuHitPx || [])[d.hand]);
    if (frac == null) return;
    const nuevo = Math.round(frac * 10) / 10;
    const esMus = d.id === 'mvolset';
    const actual = esMus ? this.audio.musicVol : this.audio.fxVol;
    if (nuevo === actual) return;
    if (esMus) this.audio.setMusicVol(nuevo); else this.audio.setFxVol(nuevo);
    this.rules.message = esMus
      ? T('msg_musicvol', { v: Math.round(nuevo * 100) })
      : T('msg_fxvol', { v: Math.round(nuevo * 100) });""",
"""    const frac = this._menuSliderFrac(r, (this._menuHitPx || [])[d.hand]);
    if (frac == null) return;
    // r83 · F179 · ARREGLO del informe del dueño («no permite deslizarlo
    // con el mando»): el arrastre de la MÚSICA DE CAMPEONATOS (id chmus)
    // caía al else y MOVÍA EL VOLUMEN DE FX — la barra se quedaba quieta.
    // Ahora chmus regula arcVol (cuantizado a 1/20 como su clic) y
    // des-silencia al arrastrar, igual que su pulsación.
    const esChmus = d.id === 'chmus';
    const esMus = d.id === 'mvolset';
    const paso = esChmus ? 20 : 10;
    const nuevo = Math.round(frac * paso) / paso;
    const actual = esChmus ? (this.audio.arcMute ? 0 : this.audio.arcVol)
      : esMus ? this.audio.musicVol : this.audio.fxVol;
    if (nuevo === actual) return;
    if (esChmus) {
      this.audio.setArcVol(nuevo);
      if (this.audio.arcMute) this.audio.setArcMute(false);
      this.rules.message = T('arc_music_msg',
        { v: Math.round(nuevo * 100) + '%' });
    } else if (esMus) {
      this.audio.setMusicVol(nuevo);
      this.rules.message = T('msg_musicvol', { v: Math.round(nuevo * 100) });
    } else {
      this.audio.setFxVol(nuevo);
      this.rules.message = T('msg_fxvol', { v: Math.round(nuevo * 100) });
    }""")

# ---------- P6 · maquetación de las barras: la etiqueta NO pisa el − ----------
parche('P6 barra etiqueta', """      if (it.tipo === 'barra') {
        // volumen: etiqueta + raíl CLICABLE (r99: % sobre el raíl) + −/+
        const h = hDe(it);
        const bw = 170;
        etq(it.et, gx + 4, y + h * 0.42, gw - 8, 21, 700, '#9aa7b4');
        const ry = y + h * 0.66, rx = gx + bw + 24, rw = gw - 2 * bw - 88;""",
"""      if (it.tipo === 'barra') {
        // volumen: −/+ a los extremos · r83 · F179: la ETIQUETA se pinta
        // SOBRE EL RAÍL (antes arrancaba en gx+4 y PISABA el botón −,
        // informe del dueño «el deslizador está mal maquetado») · raíl
        // CLICABLE (r99: % sobre el raíl) + −/+
        const h = hDe(it);
        const bw = 170;
        const ry = y + h * 0.72, rx = gx + bw + 24, rw = gw - 2 * bw - 88;
        etq(it.et, rx + 4, y + h * 0.30, rw - 8, 21, 700, '#9aa7b4');""")

# ---------- P7 · banda de champs con hueco limpio (rejilla ↑ · leyenda 1348 ↓)
parche('P7 banda champs', """    this._menuBandas(rects, [{
      tipo: 'barra', et: T('arc_music_global'),
      vol: AM.arcMute ? 0 : AM.arcVol,
      idSet: 'chmus:set', minus: 'chmus:down', plus: 'chmus:up',
    }], { y0: 1258, yMax: 1334, gap: 8 });""",
"""    this._menuBandas(rects, [{
      tipo: 'barra', et: T('arc_music_global'),
      vol: AM.arcMute ? 0 : AM.arcVol,
      idSet: 'chmus:set', minus: 'chmus:down', plus: 'chmus:up',
      // r83 · F179: 1228-1304 — hueco limpio entre la rejilla (~1150) y la
      // leyenda del pie (menu_hint en y=1348), que antes rozaba la caja
    }], { y0: 1228, yMax: 1304, gap: 8 });""")

# ---------- P8 · bump de versión (lo hace bump_version.py, aquí solo guard)
if '3.6.173-SDK6' not in t:
    print('AVISO: el fuente no lleva el sello 3.6.173 (bump lo parchea)')

if t == orig:
    print('SIN CAMBIOS — nada que escribir')
    sys.exit(1)
open(F, 'w', encoding='utf-8').write(t)
print('\nAPLICADOS:', len(PARCHES), 'parches →', F)
print(' bytes:', len(orig), '→', len(t))
