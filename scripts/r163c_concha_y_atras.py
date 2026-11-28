#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r163c · el probe r163 destapó el defecto real: la CONCHA r68 corre para
toda página ≠ main y 'jugar' tiene entrada en CONFIG_SECCIONES.shell → sus
rects (page:main, lang:es, lang:en) entraban EN LA MATRIZ antes que los de
la cartela: los índices del hover se desplazaban (el apuntado a traingo
resolvía def.botones[4] = tut:go → nada se seleccionaba) y el cristal de la
concha se transparentaba bajo el fondo semi-opaco de la cartela.
FIX triple:
1 · PUERTA LÓGICA del LEG: con cartela completa NO hay concha (ni su mapa
    legado _menuMap — los rects de la cartela van a coords de panela
    directas). Sin arte, la concha legado sigue (fallback progresivo).
2 · ATRÁS propio de la cartela (def.atras): medallón-icono 'atras' (sin
    texto — la directiva r68 del dueño) con id page:main — la navegación
    de vuelta que la concha llevaba.
3 · SELECCIÓN POR ID: el recurso se resuelve con rects[hi].id (a prueba de
    cualquier rect extra futuro), pintando tras empujar todos los rects."""
import sys

F_C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

B = {}
for f in (F_C02, F_C12):
    with open(f, 'r', encoding='utf-8') as fh:
        B[f] = fh.read()

P = [
    # 1a · apertura del gate en el LEG
    (F_C12, """    if (LEG) {
      // r68 · CONCHA de secciones (cristal + ATRÁS + título, de
      // CONFIG_SECCIONES) y luego el contenido legado 1024×1536 centrado
      // (escala 0,911) sobre una placa serena. Los rects de todos los
      // painters se mapean (btn + _mapRect — misma cuenta).
      const S68 = H / 1536, DX68 = (W - 1024 * S68) / 2;
      this._menuMap = { s: S68, dx: DX68, dy: 0 };
      this.drawMenuConcha(rects);""",
     """    if (LEG) {
      // r163c · CON CARTELA, SIN CONCHA: la cartela pinta SU panela
      // completa (el cristal de la concha se transparentaba mal bajo el
      // fondo semi-opaco) y SIN el mapa legado ni SUS rects — el
      // page:main/lang:es/lang:en de la concha desplazaban los índices de
      // los botones de la cartela (el hover caía en la pieza equivocada).
      // Sin arte, la concha legado sigue tal cual (fallback progresivo).
      if (_uiNom && this._uiModo(_uiNom)) {
        this._menuMap = null;
      } else {
      // r68 · CONCHA de secciones (cristal + ATRÁS + título, de
      // CONFIG_SECCIONES) y luego el contenido legado 1024×1536 centrado
      // (escala 0,911) sobre una placa serena. Los rects de todos los
      // painters se mapean (btn + _mapRect — misma cuenta).
      const S68 = H / 1536, DX68 = (W - 1024 * S68) / 2;
      this._menuMap = { s: S68, dx: DX68, dy: 0 };
      this.drawMenuConcha(rects);""", 1),
    # 1b · cierre del gate (tras el if de la placa)
    (F_C12, """      if (!sinPlaca) {
        c.setTransform(S68, 0, 0, S68, DX68, 0);
        rr(8, 200, 1024 - 16, 1536 - 208, 30);
        c.fillStyle = 'rgba(8,12,24,0.72)';
        c.fill();
        c.strokeStyle = 'rgba(232,180,90,0.35)';
        c.lineWidth = 3;
        c.stroke();
      }
    } else {
      this._menuMap = null;
    }""",
     """      if (!sinPlaca) {
        c.setTransform(S68, 0, 0, S68, DX68, 0);
        rr(8, 200, 1024 - 16, 1536 - 208, 30);
        c.fillStyle = 'rgba(8,12,24,0.72)';
        c.fill();
        c.strokeStyle = 'rgba(232,180,90,0.35)';
        c.lineWidth = 3;
        c.stroke();
      }
      }   // r163c · fin del else «sin cartela»
    } else {
      this._menuMap = null;
    }""", 1),
    # 2 · el ATRÁS de la cartela Jugar (def)
    (F_C02, """        Jugar: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          tituloKey: 'hub_jugar',""",
     """        Jugar: {
          panela: 'C',
          lados: ['C'],
          fondo: 'Main/fondo.png',
          tituloKey: 'hub_jugar',
          // r163c · ATRÁS icono (la concha lo llevaba — al saltarla, la
          // cartela pinta su propio medallón 'atras' con id page:main)
          atras: { x: 44, y: 40, d: 66 },""", 1),
    # 3a · el recurso se MUDA tras los rects (selección por id)
    (F_C12, """    // r163 · RECURSO DINÁMICO (cartela Jugar): el arte del modo SELECCIO-
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
    // r163 · BANDERAS es/en (cartela Main, esquina superior derecha —""",
     """    // r163 · BANDERAS es/en (cartela Main, esquina superior derecha —""", 1),
    # 3b · el recurso (ya por id) pinta al FINAL, con TODOS los rects vivos
    (F_C12, """      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    // r163 · vida viva: vaivén/fade piden el siguiente repintado
    this._menuAnimCartela();
    return true;
  }""",
     """      rects.push(this._mapRect({ x: ox + b.x, y: b.y, w: b.w, h: b.h, id: b.id }));
    }
    // r163c · ATRÁS de la cartela (medallón-icono 'atras' — sin texto,
    // directiva r68 del dueño): id page:main del despachador.
    if (def.atras) {
      const A = def.atras;
      const hovA = this.menuHover.includes(rects.length);
      if (hovA) {
        c.save();
        c.shadowColor = 'rgba(255,210,87,0.85)';
        c.shadowBlur = 16;
      }
      this._vestMedallion(c, ox + A.x + A.d / 2, A.y + A.d / 2, A.d / 2,
        'atras');
      if (hovA) c.restore();
      rects.push(this._mapRect({ x: ox + A.x, y: A.y, w: A.d, h: A.d,
        id: 'page:main' }));
    }
    // r163c · RECURSO DINÁMICO (cartela Jugar): el arte del modo SELECCIO-
    // NADO con crossfade ágil (240 ms). Selección POR ID del rect apuntado
    // (a prueba de rects extra: concha, atras, banderas…); sin apuntado
    // permanece el último («siempre esté en pantalla el recurso relativo
    // al botón seleccionado» — dueño). Al abrir: el defecto
    // (btn_maquina → jugar.png). Pinta al final: sin solape con botones.
    if (def.recurso) {
      const R = def.recurso;
      const hi = this.menuHover.find((h) => h >= 0);
      const rid = (hi !== undefined && hi >= 0 && hi < rects.length)
        ? rects[hi].id : null;
      if (rid && R.imgs[rid] && rid !== this._uiJugarSel) {
        this._uiJugarFade = { de: this._uiJugarSel || R.defecto,
          a: rid, t0: performance.now() };
        this._uiJugarSel = rid;
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
    // r163 · vida viva: vaivén/fade piden el siguiente repintado
    this._menuAnimCartela();
    return true;
  }""", 1),
]

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
print('✓ r163c: concha fuera con cartela · ATRÁS propio · selección por id')
