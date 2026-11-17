#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_r84_fase180.py — r84 · FASE 180 «ENTRENAMIENTO AL DÍA».

Informe del dueño tras la V3.6.174:
  1. «Se sigue leyendo mal» — DOS palancas:
     (a) el GOBERNADOR degradaba imagen (fovea→tope, escala→0.8) sin saber
         si el menú está abierto: con el visor escalonado, el menú se
         renderiza a resolución rebajada y NADA de textura lo arregla.
         Ahora: con el menú abierto la imagen RESTAURA el perfil del tier
         al instante y _stepDown NO toca fovea/escala (sólo la tasa, que
         no afecta a la nitidez).
     (b) el arco se ACERCA: panelas a 1,00 m (antes 1,15) — texto +15 %
         angular; la fórmula r69 recalcula tangencias sola.
  2. «Los subapartados de entrenamiento están con una maquetación antigua»
     — la deuda r80 («hasta su migración»): trainarea/trainext pintaban en
     espacio LEGADO 1024×1536 con placa y escala 0.911. Migrados al
     interior C del arco (gx/gw como _menuBandas), a placa cero y con
     _menuMap nulo — ids de acción intactos.

Aplica a: src/game/core/c12_pingponggame.js, c13_ui_arranque.js,
c02_cfg_escena.js. Cada parche exige su conteo exacto: si algo no casa,
ABORTA sin escribir.
"""
import sys

PARCHES = []


def parche_f(path, nombre, viejo, nuevo, esperado=1):
    n = path.count(viejo)
    if n != esperado:
        print('FALLO [%s]: %d apariciones en %s (esperaba %d)' %
              (nombre, n, path[-28:], esperado))
        print('--- viejo ---')
        print(viejo[:300])
        sys.exit(1)
    return path.replace(viejo, nuevo)


C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'
C13 = '/home/z/my-project/src/game/core/c13_ui_arranque.js'
C02 = '/home/z/my-project/src/game/core/c02_cfg_escena.js'
t12 = open(C12, encoding='utf-8').read()
t13 = open(C13, encoding='utf-8').read()
t02 = open(C02, encoding='utf-8').read()

# ---------- P1 · sinPlaca: migración consumada ----------
t12 = parche_f(t12, 'P1 sinPlaca + nota', """      // r80 · 'rank' se migra a banda (fuera la placa legada que se pintaba
      // DETRÁS de la tabla nueva); trainext/trainarea/tutask siguen siendo
      // painters legados en coords de tarjeta — SIN el transform LEG sus
      // tarjetas quedaban en la esquina del lienzo (las «áreas vacías» del
      // informe): vuelven al mapa y a la placa hasta su migración.
      if (!sinPlaca) {""",
"""      // r80 · 'rank' se migra a banda (fuera la placa legada que se pintaba
      // DETRÁS de la tabla nueva). r84 · F180: trainext y trainarea quedan
      // MIGRADOS al interior C del arco (painters nativos, _menuMap nulo) —
      // fuera de la placa y del transform LEG; tutask sigue legado.
      if (!sinPlaca) {""")
t12 = parche_f(t12, 'P1b sinPlaca lista', """        'join', 'name', 'gripname']
        .includes(this.menuPage);""",
"""        'join', 'name', 'gripname', 'trainext', 'trainarea']
        .includes(this.menuPage);""")

# ---------- P2 · gobernador: restaurar imagen con el menú abierto ----------
t12 = parche_f(t12, 'P2 feed imagen plena', """    if (!this.auto) return;
    if (this._coolDown > 0) this._coolDown -= dt;""",
"""    if (!this.auto) return;
    // r84 · F180 · MENÚ CON IMAGEN PLENA: el informe del dueño («se sigue
    // leyendo mal») — si el gobernador degradó imagen (fovea/escala),
    // abrir el menú RESTAURA el perfil del tier AL INSTANTE: el menú es
    // barato (tres panelas de texto) y es el momento de LEER. La tasa no
    // se toca (no afecta a la nitidez del texto); al cerrar, el gobernador
    // sigue desde el perfil y volverá a degradar si no lo sostiene.
    const pTier = PERF_TIERS[this.tier];
    const menuViendo = this.g.menuOpen && this.g.menuGroup &&
      this.g.menuGroup.visible;
    if (menuViendo && (this.fovea > pTier.fovea + 0.005 ||
        this.scale < pTier.scale - 0.005)) {
      this.fovea = pTier.fovea;
      this.scale = pTier.scale;
      this.applyLive(); this.save();
    }
    if (this._coolDown > 0) this._coolDown -= dt;""")

# ---------- P3 · _stepDown: con el menú abierto, sólo la tasa baja ----------
t12 = parche_f(t12, 'P3 stepDown guard', """  _stepDown(bajaTasa) {
    // r96 · techo del FFR también en el gobernador continuo
    if (bajaTasa && this.rate > PERF_PISO + 0.5) {
      this.rate = PERF_PISO;
    } else if (this.fovea < this.foveaMax() - 0.005) {
      this.fovea = Math.min(this.foveaMax(), this.fovea + 0.08);
    } else if (this.scale > 0.805) {
      this.scale = Math.max(0.8, this.scale - 0.10);   // ya para la próxima
    } else if (this.rate > PERF_PISO + 0.5) {
      this.rate = PERF_PISO;         // entró con 90 y la imagen ya al mínimo
    } else if (this.rate > 62) {
      this.rate = 60;                // EMERGENCIA honesta (imagen al mínimo)
    } else {
      this.scale = Math.max(0.75, this.scale - 0.05);  // colchón final
    }""",
"""  _stepDown(bajaTasa) {
    // r96 · techo del FFR también en el gobernador continuo
    // r84 · F180 · con el MENÚ ABIERTO la imagen NO se degrada (el dueño
    // está LEYENDO): fovea/escala intactas — sólo baja la tasa, que no
    // afecta a la nitidez del texto del arco.
    const menuViendo = this.g.menuOpen && this.g.menuGroup &&
      this.g.menuGroup.visible;
    if (bajaTasa && this.rate > PERF_PISO + 0.5) {
      this.rate = PERF_PISO;
    } else if (!menuViendo && this.fovea < this.foveaMax() - 0.005) {
      this.fovea = Math.min(this.foveaMax(), this.fovea + 0.08);
    } else if (!menuViendo && this.scale > 0.805) {
      this.scale = Math.max(0.8, this.scale - 0.10);   // ya para la próxima
    } else if (this.rate > PERF_PISO + 0.5) {
      this.rate = PERF_PISO;         // entró con 90 y la imagen ya al mínimo
    } else if (this.rate > 62) {
      this.rate = 60;                // EMERGENCIA honesta (imagen al mínimo)
    } else if (!menuViendo) {
      this.scale = Math.max(0.75, this.scale - 0.05);  // colchón final
    }""")

# ---------- P4 · c02: el arco se acerca a 1,00 m ----------
t02 = parche_f(t02, 'P4 dist arco', """    panelas: [
      { id: 'L', x: 0, w: 1112, altoM: 0.95, dist: 1.15 },
      { id: 'C', x: 1112, w: 1472, altoM: 0.95, dist: 1.15 },
      { id: 'R', x: 2584, w: 1112, altoM: 0.95, dist: 1.15 },
    ],""",
"""    panelas: [
      // r84 · F180 · dist 1,15 → 1,00 m (informe del dueño: «se sigue
      // leyendo mal»): el texto del arco gana +15 % angular sin tocar el
      // lienzo; la fórmula r69 recalcula tangencias y yaws sola.
      { id: 'L', x: 0, w: 1112, altoM: 0.95, dist: 1.00 },
      { id: 'C', x: 1112, w: 1472, altoM: 0.95, dist: 1.00 },
      { id: 'R', x: 2584, w: 1112, altoM: 0.95, dist: 1.00 },
    ],""")

# ---------- P5 · c13 drawArea migrada al interior C ----------
AREA_VIEJA = open(C13, encoding='utf-8').read()
iA = t13.find('    function drawArea(game, c, rects, btn, label) {')
iAfin = t13.find('    /* r70 · FASE 164 · PERFIL Y EXTRAS DE ENTRENAMIENTO', iA)
if iA < 0 or iAfin < 0 or iAfin - iA > 6000:
    print(f'FALLO [P5 anclajes drawArea]: iA={iA} iAfin={iAfin}')
    sys.exit(1)
AREA_NUEVA = """    function drawArea(game, c, rects, btn, label) {
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      const a = AREAS.find((x) => x.id === uiArea) || AREAS[0];
      // r84 · F180 · MIGRACIÓN al interior C del arco (la deuda r80: «hasta
      // su migración»): fuera el espacio legado 1024×1536, la placa y su
      // escala 0.911 — las tarjetas pintan NATIVAS a banda completa de la
      // panela C (gx/gw como _menuBandas). El informe del dueño: «los
      // subapartados de entrenamiento están con una maquetación antigua».
      // La división de área mantiene SU mecánica íntegra (ids intactos).
      game._menuMap = null;
      const pC = CONFIG_MENUS.arco.panelas.find((p) => p.id === 'C');
      const gx = pC.x + 80, gw = pC.w - 160;
      let y = 262;
      for (const id of Object.keys(MODES)) {
        const M = MODES[id];
        if (M.area !== a.id) continue;
        const isOn = active === id;
        // tarjeta del modo
        const idx = rects.length;
        btn('trv3:start:' + id, gx, y, gw, 180, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(gx, y, gw, 180, 22); else c.rect(gx, y, gw, 180);
        // r74 · FASE 168 · placa de museo en las tarjetas del ÁREA (el
        // color del área sobrevive en el aro del medallón, no en el relleno
        // saturado) — la estética nueva hasta el último subnivel.
        if (game._vestPlaca73) game._vestPlaca73(c, gx, y, gw, 180, 22);
        c.strokeStyle = isOn ? '#f0c85a' : 'rgba(232,180,90,0.32)'; c.lineWidth = isOn ? 5 : 3;
        c.stroke();
        c.textAlign = 'left'; c.textBaseline = 'middle';
        c.fillStyle = '#ffffff'; c.font = '800 34px system-ui, sans-serif';
        c.fillText(t(M.nk), gx + 28, y + 40);
        c.fillStyle = 'rgba(255,255,255,0.85)';
        const desc = t(M.dk, { n: M.n });
        // r116 · CUERPO A PRUEBA DE DESBORDE — ahora a lo ancho de la C
        // (gw−72 = 1240 px: casi todas las descripciones caben en 1-2 líneas)
        let dFs = 22;
        const wrapAt = (fs) => {
          c.font = '600 ' + fs + 'px system-ui, sans-serif';
          const ls = [''];
          for (const w of desc.split(' ')) {
            const cur = ls[ls.length - 1];
            const cand = cur ? cur + ' ' + w : w;
            if (!cur || c.measureText(cand).width <= gw - 72) {
              ls[ls.length - 1] = cand;
            } else {
              ls.push(w);
            }
          }
          return ls;
        };
        let dLines = wrapAt(dFs);
        if (dLines.length > 2) { dFs = 20; dLines = wrapAt(dFs); }
        const dCorta = dLines.length > 3;
        dLines = dLines.slice(0, 3);
        for (let i = 0; i < dLines.length; i++) {
          while (dLines[i].length > 2 &&
              c.measureText(dLines[i]).width > gw - 72) {
            dLines[i] = dLines[i].slice(0, -1);
          }
        }
        if (dCorta && dLines[2]) dLines[2] += '…';
        c.font = '600 ' + dFs + 'px system-ui, sans-serif';
        if (dLines.length > 2) {
          c.fillText(dLines[0], gx + 28, y + 72);
          c.fillText(dLines[1], gx + 28, y + 96);
          c.fillText(dLines[2], gx + 28, y + 120);
        } else if (dLines.length === 2) {
          c.fillText(dLines[0], gx + 28, y + 84);
          c.fillText(dLines[1], gx + 28, y + 110);
        } else {
          c.fillText(dLines[0] || '', gx + 28, y + 96);
        }
        c.fillStyle = '#f0c85a'; c.font = '700 20px system-ui, sans-serif';
        c.fillText((S.best[id] ? t('mejor') + ': ' + S.best[id] + '  ·  ' : '') +
          t('obj') + ': ' + M.n, gx + 28, y + 148);
        // v3.0.7-PLAY1 · estrellas logradas + mejor precisión de la prueba
        // M7d (r120) · MEDALLA del ejercicio delante de las estrellas
        if (GAMF()) {
          const stN = S.stars[id] || 0;
          c.textAlign = 'right';
          const md = medallaDe(id);
          let meta = (md ? MED_GLYPH[md] + ' ' : '') +
            '\\u2605'.repeat(stN) + '\\u2606'.repeat(3 - stN);
          if (S.acc[id]) meta += '  ' + S.acc[id] + '%';
          c.fillStyle = stN ? '#f0c85a' : 'rgba(255,255,255,0.35)';
          c.font = '800 22px system-ui, sans-serif';
          c.fillText(meta, gx + gw - 34, y + 148);
        }
        c.textAlign = 'right';
        c.fillStyle = isOn ? '#f0c85a' : '#ffffff';
        c.font = '900 26px system-ui, sans-serif';
        c.fillText(isOn ? t('activo') : t('iniciar'), gx + gw - 34, y + 88);
        c.restore();
        y += 198;
      }
    }
"""
t13 = t13[:iA] + AREA_NUEVA + t13[iAfin:]
PARCHES.append('P5 drawArea nativa')
print('OK  [P5 drawArea nativa]')

# ---------- P6 · c13 drawExtras migrada al interior C ----------
iE = t13.find('    function drawExtras(game, c, rects, btn, label) {')
iEfin = t13.find("    /* ---------------- acciones del menú (case 'trv3')", iE)
if iE < 0 or iEfin < 0 or iEfin - iE > 7000:
    print(f'FALLO [P6 anclajes drawExtras]: iE={iE} iEfin={iEfin}')
    sys.exit(1)
EXTRAS_NUEVA = """    function drawExtras(game, c, rects, btn, label) {
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
      // r84 · F180 · MIGRACIÓN al interior C del arco (la deuda r80):
      // chip de perfil, ayudas visuales y pieles NATIVOS a banda completa
      // de la panela C (gx/gw como _menuBandas) — fuera espacio legado,
      // placa y escala. El botón PARAR, que antes pintaba a y=1380 legado
      // (fuera de banda), ahora vive DENTRO del lienzo visible.
      game._menuMap = null;
      const pC = CONFIG_MENUS.arco.panelas.find((p) => p.id === 'C');
      const gx = pC.x + 80, gw = pC.w - 160;
      // — chip de perfil: puntos · nivel —
      const lvl = levelOf(S.pts);
      c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillStyle = '#f0c85a'; c.font = '900 58px system-ui, sans-serif';
      c.fillText(S.pts + ' ' + t('pts'), gx + 8, 316);
      c.fillStyle = '#a9b8cc'; c.font = '600 24px system-ui, sans-serif';
      c.fillText(t('nivel') + ' · ' + t(lvl.k), gx + 8, 364);
      // progreso al siguiente nivel + LOGROS n/9 (v3.0.7-PLAY1)
      if (GAMF()) {
        const li = LEVELS.indexOf(lvl), nx = LEVELS[li + 1] || null;
        const bw = 460, bx = gx + 8, by = 404;
        const prog = nx ? Math.min(1, (S.pts - lvl.min) / (nx.min - lvl.min)) : 1;
        c.fillStyle = 'rgba(255,255,255,0.14)';
        c.fillRect(bx, by, bw, 8);
        c.fillStyle = nx ? '#f0c85a' : '#68d391';
        c.fillRect(bx, by, Math.max(4, bw * prog), 8);
        c.font = '600 17px system-ui, sans-serif';
        c.fillStyle = '#a9b8cc';
        c.fillText(nx ? (S.pts + ' / ' + nx.min) : t('max'), bx + bw + 14, by + 5);
        const got = ACHS.filter((a2) => S.ach[a2]).length;
        c.font = '700 17px system-ui, sans-serif';
        c.fillText(t('logros') + ' ' + got + '/' + ACHS.length, bx, by + 34);
        for (let i = 0; i < ACHS.length; i++) {
          const cx = bx + i * 30;
          c.beginPath(); c.arc(cx, by + 62, 7, 0, Math.PI * 2);
          c.fillStyle = S.ach[ACHS[i]] ? '#f0c85a' : 'rgba(255,255,255,0.16)';
          c.fill();
        }
      }
      // — ayudas visuales (fb toggles, ids intactos) —
      label(t('fb_t'), gx + 8, 500, '#a9b8cc');
      const toggles = [['marks', t('fb_marks')], ['line', t('fb_line')],
        ['spin', t('fb_spin')]];
      const wT = Math.floor((gw - 34) / 3);
      let tx2 = gx;
      for (const [k, lbl] of toggles) {
        btn('trv3:fb:' + k, tx2, 522, wT, 72, lbl, !!S.fb[k],
          undefined, !!S.fb[k], 22);
        tx2 += wT + 17;
      }
      // — pieles de pala (tarjetas miniatura, ahora a lo ancho de la C) —
      label(t('skins_t'), gx + 8, 636, '#a9b8cc');
      const wS = 180, hS = 92, pasoS = 208;   // 6 por fila (6×208 ≤ gw)
      let sx = gx, sy = 664;
      for (const sk of SKINS) {
        if (sk.via === 'racha') continue;   // r76: las de asistencia en EL PULSO
        if (sx + wS > gx + gw) { sx = gx; sy += hS + 16; }
        const un = S.unlocked.indexOf(sk.id) >= 0;
        const idb = 'trv3:skin:' + sk.id;
        const idx = rects.length;
        btn(idb, sx, sy, wS, hS, '', false);
        c.save();
        c.beginPath();
        if (c.roundRect) c.roundRect(sx, sy, wS, hS, 14); else c.rect(sx, sy, wS, hS);
        c.fillStyle = S.skin === sk.id ? 'rgba(240,200,90,0.30)' : 'rgba(255,255,255,0.06)';
        c.fill();
        c.strokeStyle = S.skin === sk.id ? '#f0c85a' : (un ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)');
        c.lineWidth = S.skin === sk.id ? 4 : 2;
        c.stroke();
        c.beginPath(); c.arc(sx + 36, sy + hS / 2, 26, 0, Math.PI * 2);
        c.fillStyle = un ? 'rgba(255,255,255,0.92)' : 'rgba(255,255,255,0.12)';
        c.fill();
        c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 2; c.stroke();
        if (un) {
          c.save();
          c.beginPath(); c.arc(sx + 36, sy + hS / 2, 24, 0, Math.PI * 2); c.clip();
          c.drawImage(skinPreviewCv(sk), sx + 14, sy + 24, 44, 44);
          c.restore();
        }
        c.fillStyle = un ? '#e9edf2' : '#5a6a7d';
        const nmFull = un ? (sk.name[LANG] || sk.name.es) : '\\u{1F512} ' + sk.min;
        let nm = nmFull;
        c.font = '700 17px system-ui, sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
        while (nm.length > 2 && c.measureText(nm).width > wS - 70) {
          nm = nm.slice(0, -1);
        }
        c.fillText(nm, sx + 70, sy + hS / 2 - 12);
        if (un && S.skin === sk.id) {
          c.fillStyle = '#f0c85a'; c.font = '600 13px system-ui, sans-serif';
          c.fillText(t('skin_sel'), sx + 70, sy + hS / 2 + 14);
        }
        c.restore();
        sx += pasoS;
      }
      // r70 · parar la prueba activa (si la hay) — sin HALL aquí
      if (active) {
        btn('trv3:stop', gx, 1140, gw, 76, t('parar'), false, 'surv',
          undefined, 28);
      }
    }
"""
t13 = t13[:iE] + EXTRAS_NUEVA + t13[iEfin:]
PARCHES.append('P6 drawExtras nativa')
print('OK  [P6 drawExtras nativa]')

# ---------- escritura ----------
if True:
    open(C12, 'w', encoding='utf-8').write(t12)
    open(C13, 'w', encoding='utf-8').write(t13)
    open(C02, 'w', encoding='utf-8').write(t02)
    print('\nAPLICADOS:', len(PARCHES) + 4, 'parches (P1-P4 + P5/P6 por span)')
    print(' c12:', len(t12), '· c13:', len(t13), '· c02:', len(t02), 'bytes')
