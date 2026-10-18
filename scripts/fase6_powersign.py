#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 6 (V3.6.4-SDK4): createPowerSign — las 4 copias del cartel de
SUPERPODER (ForajidoPowerSign/WizardPowerSign/ArcadePowerSign/PwSignEO)
quedan en DELEGADORES finos sobre la fábrica del SDK, con los knobs exactos
de cada módulo (coreo clasica/v240, halo, arte, respaldo, ownTex, dims).
Además: imports del SDK y manifests (oeste v51 · magia v31 · locura v22 ·
orbital v15). Re-entrante: si un bloque ya está migrado, no lo toca."""
import json
from pathlib import Path

RAIZ = Path('/home/z/my-project')
CH = RAIZ / 'public' / 'championships'

DELEGADOR_COMUN = """  }
  build() { this._impl.build(); }
  show(iconUrl) { this._impl.show(iconUrl); }
  hide() { this._impl.hide(); }
  update(dt) { this._impl.update(dt); }
  dispose() { this._impl.dispose(); }
  get group() { return this._impl.group; }   // acceso QA/interno (solo lectura)
"""  # SIN la llave de cierre de clase: se añade al final (tras el cuerpo extra si lo hay)

TRIO_T = """    this.T_IN = this._impl.T_IN;
    this.T_HOLD = this._impl.T_HOLD;
    this.T_OUT = this._impl.T_OUT;
"""

MODS = {
    'oeste': {
        'clase': 'ForajidoPowerSign',
        'fin': '/* ============================================================================\n *  v2.86 · FX del duelo',
        'import_nuevo': "import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';",
        'delegador_extra': """    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'clasica',
      arte: 'plano',
      url: () => new URL('./assets/superpoder.webp', import.meta.url).href,
      pintar: (aplicar) => this._pintarRespaldo(aplicar),
      dims: () => ODIMS(),
    });
""" + TRIO_T,
        'cuerpo_extra': """  /* Respaldo: tablón quemado del Oeste (mismo pintor que había en el
   * build: vetas, quemaduras de borde, marco con clavos, estrella del
   * sheriff, ¡SUPERPODER! DEL FORAJIDO y agujeros de bala). */
  _pintarRespaldo(aplicar) {
    const cv = oesteCanvas(1024, 560);
    const c = cv.getContext('2d');
    // tablones quemados
    const gr = c.createLinearGradient(0, 0, 0, 560);
    gr.addColorStop(0, '#3c2a16');
    gr.addColorStop(0.5, '#4c3418');
    gr.addColorStop(1, '#2c1c0c');
    c.fillStyle = gr; c.fillRect(0, 0, 1024, 560);
    c.strokeStyle = 'rgba(20,12,4,0.5)'; c.lineWidth = 3;
    for (let i = 0; i < 9; i++) {
      const y = 30 + i * 62;
      c.beginPath(); c.moveTo(0, y);
      c.bezierCurveTo(340, y + 8, 700, y - 8, 1024, y + 3);
      c.stroke();
    }
    // quemaduras de borde
    for (let i = 0; i < 26; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() < 0.5 ? Math.random() * 46 : 560 - Math.random() * 46;
      const r = 8 + Math.random() * 26;
      const rg = c.createRadialGradient(x, y, 0, x, y, r);
      rg.addColorStop(0, 'rgba(8,4,0,0.85)');
      rg.addColorStop(1, 'rgba(8,4,0,0)');
      c.fillStyle = rg;
      c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    }
    // marco con clavos
    c.strokeStyle = '#c89b4a'; c.lineWidth = 12;
    c.strokeRect(18, 18, 988, 524);
    c.fillStyle = '#e8c87a';
    [[40, 40], [984, 40], [40, 520], [984, 520]].forEach(([x, y]) => {
      c.beginPath(); c.arc(x, y, 9, 0, Math.PI * 2); c.fill();
    });
    // estrella del sheriff arriba
    c.save();
    c.translate(512, 108);
    c.fillStyle = '#e8c87a'; c.strokeStyle = '#7a5a1e'; c.lineWidth = 5;
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const r = (i % 2 === 0) ? 44 : 19;
      const a = -Math.PI / 2 + i * Math.PI / 5;
      const px = Math.cos(a) * r, py = Math.sin(a) * r;
      if (i === 0) c.moveTo(px, py); else c.lineTo(px, py);
    }
    c.closePath(); c.fill(); c.stroke();
    c.restore();
    // letras
    c.textAlign = 'center';
    c.fillStyle = '#ffdf8f';
    c.font = 'bold 104px Georgia, serif';
    c.strokeStyle = '#20120a'; c.lineWidth = 8;
    c.strokeText('¡SUPERPODER!', 512, 300);
    c.fillText('¡SUPERPODER!', 512, 300);
    c.fillStyle = '#e8b25f';
    c.font = 'bold 60px Georgia, serif';
    c.strokeText('DEL FORAJIDO', 512, 388);
    c.fillText('DEL FORAJIDO', 512, 388);
    // agujeros de bala
    for (const [bx, by] of [[150, 180], [880, 200], [200, 440], [840, 460]]) {
      c.fillStyle = '#120a04';
      c.beginPath(); c.arc(bx, by, 13, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(232,200,122,0.4)'; c.lineWidth = 3;
      c.beginPath(); c.arc(bx, by, 13, 0, Math.PI * 2); c.stroke();
    }
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    aplicar(t);
  }
"""

    },
    'magia': {
        'clase': 'WizardPowerSign',
        'fin': '/* ============================================================================\n *  WizardMap',
        'import_nuevo': "import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';",
        'delegador_extra': """    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'clasica',
      arte: 'canvas1024',
      url: () => this.ctrl.manifest && this.ctrl.manifest.powerUrl,
      fallbackURL: () => paintPowerBanner(),
      dims: () => (window.__PP_CORE && window.__PP_CORE.DIMS) || null,
    });
""" + TRIO_T,
        'cuerpo_extra': "",
    },
    'locura': {
        'clase': 'ArcadePowerSign',
        'fin': 'const ppSignPos',
        'import_nuevo': "import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';",
        'delegador_extra': """    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'v240',
      halo: true,
      arte: 'fit1833',
      url: () => (ctrl.data && ctrl.data.powerBannerUrl) || '',
      dims: () => (window.__PP_CORE && window.__PP_CORE.DIMS) || null,
    });
""" + TRIO_T,
        'cuerpo_extra': "",
    },
    'estacion_orbital': {
        'clase': 'PwSignEO',
        'fin': '/* ============================================================================\n *  StockController',
        'import_nuevo': "import { createPowerSign, createSfx, congela } from '../sdk/champ_sdk.js';",
        'delegador_extra': """    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'v240',
      halo: true,
      arte: 'fit1833',
      url: () => this.ctrl._A('superpower.png'),
      dims: () => this.ctrl.D || null,
      onTex: (tex) => { try { this.ctrl._ownTex.add(tex); } catch (e) { /* */ } },
    });
""" + TRIO_T,
        'cuerpo_extra': "",
    },
}

NOTAS = {
    'oeste': (51, '2026-10-19 v3.6.4-SDK4 · FASE 6 de la modularización P0 · '
              'createPowerSign (SDK v1.3.0): el tablón «¡SUPERPODER! DEL FORAJIDO» '
              '(v2.120) se migra a la fábrica única del SDK con su coreografía '
              '«clasica» exacta (entrada 1,4 m · vaivén · salida 1,5·e²), anclado '
              'a la red, icono del poder y respaldo pintado propio conservados.'),
    'magia': (31, '2026-10-19 v3.6.4-SDK4 · FASE 6 de la modularización P0 · '
              'createPowerSign (SDK v1.3.0): el cartel del Wizard (v2.120) se '
              'migra a la fábrica única del SDK con su coreografía «clasica» '
              'exacta, el arte por canvas 1024 con respaldo a paintPowerBanner() '
              'y el icono del poder anunciado.'),
    'locura': (22, '2026-10-19 v3.6.4-SDK4 · FASE 6 de la modularización P0 · '
               'createPowerSign (SDK v1.3.0): el cartel «SUPER POWER!!» (el patrón '
               'v2.40 que NACIÓ aquí, con su HALO DE CONTORNO que respira) se '
               'migra a la fábrica única del SDK; ahora el orbital comparte '
               'exactamente SU coreografía.'),
    'estacion_orbital': (15, '2026-10-19 v3.6.4-SDK4 · FASE 6 de la modularización P0 · '
                         'createPowerSign (SDK v1.3.0): el cartel de superpoder de la '
                         'casa (PwSignEO) se migra a la fábrica única del SDK con la '
                         'coreografía v2.40 de La Locura, el halo que respira, el '
                         'registro de texturas propias (_ownTex) y el dispose de la '
                         'regla Quest.'),
}

for mod, cfg in MODS.items():
    p = CH / mod / 'index.js'
    s = p.read_text(encoding='utf-8')
    # Re-OPERABLE: si ya hay delegador (aunque esté roto de una pasada
    # anterior), se re-sustituye el span completo — la cirugía es idempotente.
    # import del SDK
    import re
    m = re.search(r"import \{[^}]+\} from '\.\./sdk/champ_sdk\.js';", s)
    assert m, f'{mod}: no encuentro el import del SDK'
    s = s[:m.start()] + cfg['import_nuevo'] + s[m.end():]
    # clase → delegador
    start_marker = f"class {cfg['clase']} {{"
    i = s.index(start_marker)
    j = s.index(cfg['fin'], i)
    bloque = s[i:j]
    assert bloque.count('class ') == 1, f'{mod}: el bloque contiene más de una clase'
    head = (f"class {cfg['clase']} {{\n"
            f"  constructor(ctrl) {{\n"
            f"    this.ctrl = ctrl;\n"
            f"    this.game = ctrl.game;\n")
    if cfg['clase'] == 'ArcadePowerSign':
        head = (f"class {cfg['clase']} {{\n"
                f"  constructor(ctrl) {{\n"
                f"    this.game = ctrl.game;\n"
                f"    this.ctrl = ctrl;\n")
    nota = ('    // v3.6.4-SDK4 · FASE 6: la fábrica del SDK (createPowerSign) sustituye\n'
            f"    // la copia — UNA sola fuente para el tablón de superpoder ({cfg['clase']}).\n")
    delegador = head + nota + cfg['delegador_extra'] + DELEGADOR_COMUN + cfg['cuerpo_extra'] + '}\n'
    s = s[:i] + delegador + s[j:]
    p.write_text(s, encoding='utf-8')
    print(f'· {mod}: {cfg["clase"]} → delegador del SDK (bloque reemplazado: {len(bloque)} chars)')

# manifests
for mod, (vnew, nota) in NOTAS.items():
    p = CH / mod / 'manifest.json'
    mjs = json.loads(p.read_text(encoding='utf-8'))
    cur = mjs.get('version')
    if cur == vnew:
        print(f'· {mod}: manifest ya está en v{vnew}')
        continue
    if cur != vnew - 1:
        raise SystemExit(f'FALLO: manifest de {mod} está en v{cur}, esperaba v{vnew - 1}')
    mjs['version'] = vnew
    clave = 'notes' if isinstance(mjs.get('notes'), list) else 'cambios'
    mjs.setdefault(clave, []).append(nota)
    p.write_text(json.dumps(mjs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'· {mod}: manifest v{vnew} · nota FASE 6 añadida')

print('FASE 6: PowerSign unificado en los 4 campeonatos.')
