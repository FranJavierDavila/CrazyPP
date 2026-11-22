#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r68_codigo2.py — FASE 162 · r68 · CIRUGÍA DE c12 (PARTE 2).
drawMenuHeader→concha · drawMenuVestibulo v2 (héroe, sin dock) · rejilla
de AJUSTES en drawMenuOpts · prompts caramelo (_vestPrompt) · dedup de
botones atrás legados · needsUpdate→_menuTexSube (mecánico)."""
import re
import sys
from pathlib import Path

F = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
t = F.read_text(encoding='utf-8')
n_ok = 0


def edit(nombre, ancla, nuevo, esperados=1):
    global t, n_ok
    k = t.count(ancla)
    if k != esperados:
        sys.exit(f'ABORTA {nombre}: count={k} (esperaba {esperados})')
    t = t.replace(ancla, nuevo)
    n_ok += 1


# ------------------------------------------- E9 · drawMenuHeader → concha
m = re.search(r'  drawMenuHeader\(rects\) \{[^\0]*?\n  \}\n\n'
              r'  /\*\* r67 · FASE 161 · mapea un rect', t)
if not m:
    sys.exit('ABORTA drawMenuHeader: bloque no hallado')
t = t[:m.start()] + """  drawMenuHeader(rects) {
    // r68 · la cabecera legada ES la concha de secciones (CONFIG_SECCIONES):
    // cristal + atrás + título + idiomas + sello, pintada UNA vez por frame
    // justo antes del contenido (drawMenu). Los painters legados siguen
    // llamando aquí — idempotente por bandera, sin doble pintado.
    if (!this._menuConchaPintada) this.drawMenuConcha(rects);
  }

  /** r67 · FASE 161 · mapea un rect"""+ t[m.end():]
n_ok += 1

# --------------------------------------- E10 · drawMenuVestibulo v2 (arco)
m = re.search(r'  drawMenuVestibulo\(rects\) \{[^\0]*?\n  \}\n\n'
              r'  /\*\* Página principal: el HUB\.', t)
if not m:
    sys.exit('ABORTA drawMenuVestibulo: bloque no hallado')
VEST2 = """  /* r68 · FASE 162 · EL VESTÍBULO v2 — el arco del dueño: TRES panelas
   * físicas (cristal + marco cian por slice), cabecera repartida (logo en
   * la C, cierre en la L, idiomas + sello en la R), héroe ▶ JUGAR con
   * protagonismo (380 px, halo verde, medallón grande), CARRERA al nivel
   * del resto, dock ELIMINADO y «SALIR A LA WEB» como tarjeta fina al pie
   * de TU CASA. Todo sale de CONFIG_MENUS v2 — ids del despachador
   * intactos; los subtítulos vivos siguen en _vestSubPorId. */
  drawMenuVestibulo(rects) {
    const c = this.menuCanvas.getContext('2d');
    const CM = CONFIG_MENUS;
    const W = CM.lienzo.ancho, H = CM.lienzo.alto;

    const hov = () => this.menuHover.includes(rects.length);

    // — fondo: cristal profundo + marcos por panela (las 3 pantallas) —
    const g0 = c.createLinearGradient(0, 0, 0, H);
    g0.addColorStop(0, 'rgba(18,30,66,0.97)');
    g0.addColorStop(1, 'rgba(6,10,22,0.98)');
    c.fillStyle = g0;
    c.fillRect(0, 0, W, H);
    for (const pa of CM.arco.panelas) {
      this._vestRR(c, pa.x + 4, 4, pa.w - 8, H - 8, 26);
      c.strokeStyle = 'rgba(90,190,255,0.75)';
      c.lineWidth = 3;
      c.stroke();
      this._vestRR(c, pa.x + 10, 10, pa.w - 20, H - 20, 22);
      c.strokeStyle = 'rgba(255,255,255,0.12)';
      c.lineWidth = 2;
      c.stroke();
    }

    // — panela de contenido con título —
    const panel = (p) => {
      this._vestRR(c, p.x, p.y, p.w, p.h, 30);
      c.fillStyle = 'rgba(16,28,62,0.94)';
      c.fill();
      c.strokeStyle = 'rgba(90,190,255,0.75)';
      c.lineWidth = 3;
      c.stroke();
      c.textAlign = 'left';
      c.textBaseline = 'middle';
      c.fillStyle = '#ffffff';
      c.font = '800 40px system-ui, sans-serif';
      c.fillText(T(p.tituloKey), p.x + 34, p.y + 40);
      c.strokeStyle = 'rgba(255,255,255,0.18)';
      c.lineWidth = 2;
      c.beginPath();
      c.moveTo(p.x + 34, p.y + 72);
      c.lineTo(p.x + p.w - 34, p.y + 72);
      c.stroke();
    };

    // — tarjeta (héroe prominente · resto al mismo nivel · fina) —
    const card = (cardDef, x, y, w, h) => {
      const hovered = hov();
      const rad = cardDef.heroe ? 38 : 26;
      this._vestCandy(c, x, y, w, h, cardDef.gradiente, rad);
      if (cardDef.heroe) {
        // halo de protagonismo del héroe (petición del dueño)
        c.save();
        this._vestRR(c, x, y, w, h, rad);
        c.shadowColor = 'rgba(74,240,94,0.55)';
        c.shadowBlur = 30;
        c.strokeStyle = 'rgba(255,255,255,0.65)';
        c.lineWidth = 5;
        c.stroke();
        c.restore();
      }
      const ir = cardDef.heroe ? 84
        : (cardDef.fino ? 34 : (h < 130 ? 36 : 48));
      const icx = x + 34 + ir, icy = y + h / 2;
      this._vestMedallion(c, icx, icy, ir, cardDef.icono);
      const tx = icx + ir + 26, maxw = x + w - tx - 30;
      const sub = this._vestSubPorId(cardDef.id, cardDef);
      c.textAlign = 'left';
      let f1 = cardDef.heroe ? 72
        : (cardDef.fino ? 34 : (w >= 620 ? 44 : 36));
      c.font = `800 ${f1}px system-ui, sans-serif`;
      let lab = T(cardDef.etiquetaKey);
      while (c.measureText(lab).width > maxw && f1 > 20) {
        f1 -= 2;
        c.font = `800 ${f1}px system-ui, sans-serif`;
      }
      if (sub) {
        c.textBaseline = 'alphabetic';
        c.fillStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.97)';
        c.fillText(lab, tx, y + h * 0.44);
        let f2 = cardDef.heroe ? 34 : 24;
        c.font = `600 ${f2}px system-ui, sans-serif`;
        let sub2 = sub;
        while (c.measureText(sub2).width > maxw && f2 > 14) {
          f2 -= 2;
          c.font = `600 ${f2}px system-ui, sans-serif`;
        }
        while (c.measureText(sub2).width > maxw && sub2.length > 2) {
          sub2 = sub2.slice(0, -1);
        }
        if (sub2 !== sub) sub2 += '\u2026';
        c.fillStyle = 'rgba(228,240,255,0.92)';
        c.fillText(sub2, tx, y + h * 0.76);
      } else {
        c.textBaseline = 'middle';
        c.fillStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.97)';
        c.fillText(lab, tx, y + h / 2 + 1);
      }
      if (hovered) {
        this._vestRR(c, x, y, w, h, rad);
        c.strokeStyle = '#ffffff';
        c.lineWidth = 4;
        c.stroke();
      }
      rects.push({ x: x - 6, y: y - 4, w: w + 12, h: h + 8, id: cardDef.id });
    };

    // — cabecera repartida en el arco —
    // logo centrado en la panela C + sello
    {
      const pC = CM.arco.panelas[1];
      if (this.menuLogo.complete && this.menuLogo.naturalWidth) {
        const lh = 150;
        const lw = lh * (this.menuLogo.naturalWidth /
          this.menuLogo.naturalHeight);
        c.drawImage(this.menuLogo, pC.x + pC.w / 2 - lw / 2, 22, lw, lh);
      }
      if (CM.cabecera.sello) {
        c.textAlign = 'right';
        c.textBaseline = 'alphabetic';
        c.fillStyle = '#ffd257';
        c.font = '800 22px system-ui, sans-serif';
        c.fillText('V' + (typeof window !== 'undefined' &&
          window.__PP_VERSION ? window.__PP_VERSION : ''),
          pC.x + pC.w - 24, 200);
      }
    }
    // cierre (panela L, arriba a la derecha) — ✕ dibujado
    {
      const pL = CM.arco.panelas[0];
      const cx = pL.x + pL.w - 66, cy = 88, r = 46;
      const hovered = hov();
      this._vestCandy(c, cx - r, cy - r, r * 2, r * 2,
        ['#96a8c2', '#4a5872'], r);
      c.beginPath();
      c.arc(cx, cy, r - 4, 0, Math.PI * 2);
      c.fillStyle = 'rgba(10,16,34,0.92)';
      c.fill();
      c.lineWidth = 3;
      c.strokeStyle = 'rgba(255,255,255,0.8)';
      c.stroke();
      c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.92)';
      c.lineWidth = 7;
      c.lineCap = 'round';
      c.beginPath();
      c.moveTo(cx - 15, cy - 15);
      c.lineTo(cx + 15, cy + 15);
      c.moveTo(cx + 15, cy - 15);
      c.lineTo(cx - 15, cy + 15);
      c.stroke();
      if (hovered) {
        c.beginPath();
        c.arc(cx, cy, r, 0, Math.PI * 2);
        c.strokeStyle = '#ffffff';
        c.lineWidth = 4;
        c.stroke();
      }
      rects.push({ x: cx - r - 6, y: cy - r - 6, w: r * 2 + 12,
        h: r * 2 + 12, id: 'close' });
    }
    // palas de idioma (panela R, arriba a la derecha) — id «lang:xx» intacto
    {
      const pR = CM.arco.panelas[2];
      this._langPaddle(rects, 'es', pR.x + pR.w - 306, 36);
      this._langPaddle(rects, 'en', pR.x + pR.w - 162, 36);
    }

    // — panelas de tarjetas (héroe 380 · nivel 215 · fina 100) —
    CM.paneles.forEach((p) => {
      panel(p);
      const pad = 34, gap = 30;
      let y = p.y + 96;
      const wIn = p.w - pad * 2;
      const hero = p.tarjetas.find((t) => t.heroe);
      const pars = p.tarjetas.filter((t) => t.par);
      const fino = p.tarjetas.find((t) => t.fino);
      const rest = p.tarjetas.filter((t) => !t.heroe && !t.par && !t.fino);
      let bottom = p.y + p.h - 26;
      if (fino) bottom -= 100 + gap;
      if (hero) {
        card(hero, p.x + pad, y, wIn, 380);
        y += 380 + gap;
      }
      if (rest.length) {
        // r68 · sin héroe/par delante: reparten la altura (COMPITE y TU
        // CASA); con héroe o par: altura ESTÁNDAR — la CARRERA al nivel
        // del resto (petición del dueño).
        const hayPrevio = hero || pars.length;
        const ch = hayPrevio ? 215
          : Math.max(180, Math.floor((bottom - y - (rest.length - 1) * gap)
            / rest.length));
        rest.forEach((tt) => {
          card(tt, p.x + pad, y, wIn, ch);
          y += ch + gap;
        });
      }
      for (let i = 0; i < pars.length; i += 2) {
        const cw = (wIn - gap) / 2;
        card(pars[i], p.x + pad, y, cw, 215);
        if (pars[i + 1]) card(pars[i + 1], p.x + pad + cw + gap, y, cw, 215);
        y += 215 + gap;
      }
      if (fino) {
        card(fino, p.x + pad, y, wIn, 100);
      }
    });
    // r87 · EL MEDALLÓN DEL PULSO sobre la tarjeta Multijugador (intacto)
    if (this.social && this.social.medallonVivo &&
      this.social.medallonVivo()) {
      const rMulti = rects.find((r) => r.id === 'tab:multi');
      if (rMulti) this._pintaMedallon(rMulti, this.social);
    }
  }

  /** Página principal: el HUB."""
t = t[:m.start()] + VEST2 + t[m.end():]
n_ok += 1

# ------------------------------------------ E11 · AJUSTES: rejilla de dato
E11_A = """    const CH2 = 128, GY2 = 14;   // r83 · 7 categorías: tarjetas algo más"""
E11_B = """    btn('close', 56, closeY, 912, 68, T('close_menu') + ' · B', false, undefined, undefined, 26);"""
i = t.find(E11_A)
if i < 0:
    sys.exit('ABORTA E11: inicio no hallado')
j = t.find(E11_B, i)
if j < 0:
    sys.exit('ABORTA E11: fin no hallado')
t = t[:i] + """    // r68 · FASE 162 · la rejilla de AJUSTES es DATO (CONFIG_SECCIONES.
    // rejillas.ajustes): 8 tarjetas-icono (7 categorías + apoyo Ko-fi) en
    // dos columnas sobre las panelas C y R del arco — iconos explicativos,
    // mínimo texto. Los subtítulos vivos siguen calculados aquí arriba.
    this._menuRejilla(rects, 'ajustes', {
      optsJuego: subJuego, optsSala: subSala, optsSonido: subSonido,
      optsVisual: subVisual, optsPerfil: subPerfil, optsRendi: subRendi,
      optsPala: subPala,
    });
  }""" + t[j + len(E11_B):]
n_ok += 1

# ------------------------------------------------- E12 · prompts caramelo
E12A_ANCLA = """  drawMenuSalidaAsk(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;
    const CONF = CONFIG_MENU.salir.confirmacion;

    label(T(CONF.tituloKey), 240, 54, '#e8b45a', 'center');
    label(T(CONF.subKey), 310, 28, '#9aa7b4', 'center');
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 2;
    c.beginPath(); c.moveTo(132, 360); c.lineTo(892, 360); c.stroke();

    btn('salirweb_si', 132, 470, 760, 170, T(CONF.siKey), true, 'green', undefined, 46);
    btn('salirweb_no', 132, 700, 760, 170, T(CONF.noKey), false, undefined, undefined, 46);

    label(T(CONF.hintKey), 940, 22, '#9aa7b4', 'center');
    this.menuRects = rects;
    this._menuState = this.rules.state;
    this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
    this.menuTex.needsUpdate = true;
  }"""
E12A_NUEVO = """  drawMenuSalidaAsk(rects) {
    // r68 · prompt caramelo: medallón + pregunta + SI/NO en la panela C
    const CONF = CONFIG_MENU.salir.confirmacion;
    this._vestPrompt(rects, {
      icono: 'salir', tituloKey: CONF.tituloKey, subKey: CONF.subKey,
      hintKey: CONF.hintKey,
      si: { id: 'salirweb_si', key: CONF.siKey },
      no: { id: 'salirweb_no', key: CONF.noKey },
    });
  }"""
edit('prompt de salida', E12A_ANCLA, E12A_NUEVO)

E12B_ANCLA = """  drawMenuHallAsk(rects) {
    const c = this.menuCanvas.getContext('2d');
    const btn = this._menuBtn;
    const label = this._menuLabel;

    // título
    label(T('hallask_title'), 240, 54, '#e8b45a', 'center');
    label(T('hallask_sub'), 310, 28, '#9aa7b4', 'center');
    // separador fino
    c.strokeStyle = 'rgba(232,180,90,0.35)';
    c.lineWidth = 2;
    c.beginPath(); c.moveTo(132, 360); c.lineTo(892, 360); c.stroke();

    // las dos respuestas, grandes y sin ambigüedad
    btn('hallask_si', 132, 470, 760, 170, T('hallask_yes_btn'), true, 'green', undefined, 46);
    btn('hallask_no', 132, 700, 760, 170, T('hallask_no_btn'), false, undefined, undefined, 46);

    // ayuda
    label(T('hallask_hint'), 940, 22, '#9aa7b4', 'center');
    this.menuRects = rects;
    this._menuState = this.rules.state;
    this._menuTipDraw(c, rects);   // r96 · tooltip del control apuntado
    this.menuTex.needsUpdate = true;
  }"""
E12B_NUEVO = """  drawMenuHallAsk(rects) {
    // r68 · prompt caramelo del PROMPT B (volver al hall)
    this._vestPrompt(rects, {
      icono: 'vestibulo', tituloKey: 'hallask_title', subKey: 'hallask_sub',
      hintKey: 'hallask_hint',
      si: { id: 'hallask_si', key: 'hallask_yes_btn' },
      no: { id: 'hallask_no', key: 'hallask_no_btn' },
    });
  }"""
edit('prompt del hall', E12B_ANCLA, E12B_NUEVO)

# método _vestPrompt — insertado antes de «Página principal: el HUB»
E12C_ANCLA = "  /** Página principal: el HUB."
E12C_NUEVO = """  /** r68 · PROMPT caramelo genérico (salir a la web / volver al hall):
   *  medallón protagonista + pregunta + dos respuestas lado a lado en la
   *  panela C del arco. Sin ambigüedad, mínimo texto, ids intactos. */
  _vestPrompt(rects, cfg) {
    const c = this.menuCanvas.getContext('2d');
    const pC = CONFIG_MENUS.arco.panelas[1];
    const cx = pC.x + pC.w / 2;
    this._vestMedallion(c, cx, 300, 110, cfg.icono);
    c.textAlign = 'center';
    c.textBaseline = 'middle';
    c.fillStyle = '#e8b45a';
    c.font = '900 56px system-ui, sans-serif';
    c.fillText(T(cfg.tituloKey), cx, 470);
    c.fillStyle = '#9aa7b4';
    c.font = '600 30px system-ui, sans-serif';
    let sub = T(cfg.subKey);
    const sub0 = sub;
    while (c.measureText(sub).width > pC.w - 160 && sub.length > 2) {
      sub = sub.slice(0, -1);
    }
    c.fillText(sub + (sub !== sub0 ? '\u2026' : ''), cx, 540);
    const bw = 470, bh = 140, gy = 640, gapP = 60;
    const hoverSi = this.menuHover.includes(rects.length);
    this._vestCandy(c, cx - bw - gapP / 2, gy, bw, bh,
      ['#4af05e', '#189e2c'], 30);
    c.fillStyle = hoverSi ? '#ffffff' : 'rgba(255,255,255,0.97)';
    c.font = '800 46px system-ui, sans-serif';
    c.fillText(T(cfg.si.key), cx - bw / 2 - gapP / 2, gy + bh / 2 + 1);
    rects.push({ x: cx - bw - gapP / 2 - 6, y: gy - 4, w: bw + 12,
      h: bh + 8, id: cfg.si.id });
    const hoverNo = this.menuHover.includes(rects.length);
    this._vestCandy(c, cx + gapP / 2, gy, bw, bh,
      ['#5f7183', '#3a4754'], 30);
    c.fillStyle = hoverNo ? '#ffffff' : 'rgba(255,255,255,0.97)';
    c.font = '800 46px system-ui, sans-serif';
    c.fillText(T(cfg.no.key), cx + bw / 2 + gapP / 2, gy + bh / 2 + 1);
    rects.push({ x: cx + gapP / 2 - 6, y: gy - 4, w: bw + 12, h: bh + 8,
      id: cfg.no.id });
    c.fillStyle = '#9aa7b4';
    c.font = '600 24px system-ui, sans-serif';
    c.fillText(T(cfg.hintKey), cx, 900);
    this.menuRects = rects;
    this._menuState = this.rules.state;
    this._menuTipDraw(c, rects);
    this._menuTexSube();
  }

  /** Página principal: el HUB."""
edit('método _vestPrompt', E12C_ANCLA, E12C_NUEVO)

# ------------------------------------------- E13 · dedup de botones atrás
edit('atrás page:main legados',
     "    btn('page:main', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);\n",
     '', esperados=4)
edit('atrás page:opts legado',
     "    btn('page:opts', 40, 216, 240, 60, T('page_back'), false, undefined, undefined, 25);\n",
     '', esperados=1)

# --------------------------------- E14 · needsUpdate → _menuTexSube (todo)
k = t.count('this.menuTex.needsUpdate = true;')
if k < 15:
    sys.exit(f'ABORTA E14: needsUpdate count={k}')
t = t.replace('this.menuTex.needsUpdate = true;', 'this._menuTexSube();')
n_ok += 1
print(f'PARTE 2 OK: {n_ok} ediciones · needsUpdate sustituidos: {k}')

F.write_text(t, encoding='utf-8')
