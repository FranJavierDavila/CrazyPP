#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""V3.0 · Instalador quirúrgico del módulo PRO TRAINING en public/game.html.
Cada edición verifica su ancla EXACTA (1 aparición) y aborta si falla."""
import io, re, subprocess, sys

P = '/home/z/my-project/public/game.html'
src = io.open(P, encoding='utf-8').read()
orig_len = len(src)
log = []

def rep(name, old, new, count=1):
    global src
    n = src.count(old)
    if n != count:
        print(f'FAIL ancla {name}: {n} apariciones (esperaba {count})')
        sys.exit(1)
    src = src.replace(old, new)
    log.append(f'OK {name}')

# ---------- 1 · versión ----------
rep('version',
    "const VERSION = '2.141.0';   // v2.141 · ",
    "const VERSION = '3.0.0';   // v3.0 · PRO TRAINING — hub de entrenamiento profesional (window.__PP_TRAIN), feedback técnico, puntos y skins · antes v2.141 · ")

# ---------- 2 · guardia en updateCalibration ----------
rep('calib-guard',
    "  updateCalibration(dt) {\n",
    "  updateCalibration(dt) {\n"
    "    if (this.trainV3) return;   // v3.0: PRO TRAINING lleva su propia rutina (máquina/jueces)\n")

# ---------- 3 · gancho de tick ----------
rep('tick-hook',
    "    if (this.calib) this.updateCalibration(dt);\n",
    "    if (this.calib) this.updateCalibration(dt);\n"
    "    if (window.__PP_TRAIN) window.__PP_TRAIN.tick(dt);   // v3.0: cosmética global + entrenamiento\n")

# ---------- 4 · tarjeta ENTRENAR abre el hub ----------
rep('traingo',
    "      case 'traingo':\n"
    "        // ENTRENAR desde el menú: máquina de bolas + panel de agarre\n"
    "        if (this.champs) this.champs.leaveAll();   // v2.53\n"
    "        this.closeMenu();\n"
    "        this.enterCalib();\n"
    "        break;\n",
    "      case 'traingo':\n"
    "        // v3.0: ENTRENAR abre el HUB PRO TRAINING (la posición de la pala\n"
    "        // queda como subapartado 0 y se añaden los modos profesionales)\n"
    "        if (this.champs) this.champs.leaveAll();   // v2.53\n"
    "        this.menuPage = 'train';\n"
    "        this.drawMenu();\n"
    "        break;\n")

# ---------- 5 · páginas del menú ----------
rep('menu-pages',
    "    if (this.menuPage === 'opts') {\n"
    "      this.drawMenuOpts(rects);\n"
    "      this.menuRects = rects;\n"
    "      this._menuState = this.rules.state;\n"
    "      this.menuTex.needsUpdate = true;\n"
    "      return;\n"
    "    }\n",
    "    if (this.menuPage === 'opts') {\n"
    "      this.drawMenuOpts(rects);\n"
    "      this.menuRects = rects;\n"
    "      this._menuState = this.rules.state;\n"
    "      this.menuTex.needsUpdate = true;\n"
    "      return;\n"
    "    }\n"
    "    // v3.0 · PRO TRAINING: páginas del hub de entrenamiento\n"
    "    if (this.menuPage === 'train' && window.__PP_TRAIN) {\n"
    "      window.__PP_TRAIN.drawHub(this, c, rects, this._menuBtn, this._menuLabel);\n"
    "      this.menuRects = rects;\n"
    "      this._menuState = this.rules.state;\n"
    "      this.menuTex.needsUpdate = true;\n"
    "      return;\n"
    "    }\n"
    "    if (this.menuPage === 'trainarea' && window.__PP_TRAIN) {\n"
    "      window.__PP_TRAIN.drawArea(this, c, rects, this._menuBtn, this._menuLabel);\n"
    "      this.menuRects = rects;\n"
    "      this._menuState = this.rules.state;\n"
    "      this.menuTex.needsUpdate = true;\n"
    "      return;\n"
    "    }\n")

# ---------- 6 · acciones del menú ----------
rep('menu-action',
    "      case 'start':\n"
    "        // ARRANQUE RÁPIDO: partido contra la CPU (o revancha online)\n",
    "      case 'trv3':\n"
    "        // v3.0 · PRO TRAINING: acciones del hub de entrenamiento\n"
    "        if (window.__PP_TRAIN) window.__PP_TRAIN.menuAction(this, arg);\n"
    "        break;\n"
    "      case 'start':\n"
    "        // ARRANQUE RÁPIDO: partido contra la CPU (o revancha online)\n")

# ---------- 7 · subtítulo de la tarjeta ENTRENAR ----------
rep('hub-sub-es', "    hub_train_sub: 'Máquina de bolas',",
    "    hub_train_sub: 'PRO TRAINING · 5 áreas + skins',")
rep('hub-sub-en', "    hub_train_sub: 'Ball machine',",
    "    hub_train_sub: 'PRO TRAINING · 5 areas + skins',")

# ---------- 8 · módulo (tras window.__PP_GAME = game;) ----------
anchor = "  window.__PP_GAME = game;\n"
n = src.count(anchor)
if n != 1:
    print(f'FAIL ancla modulo: {n}')
    sys.exit(1)
parts = []
for f in ('v3_module_p1.js', 'v3_module_p2.js', 'v3_module_p2b.js', 'v3_module_p2c.js', 'v3_module_p3.js'):
    parts.append(io.open(f'/home/z/my-project/scripts/{f}', encoding='utf-8').read())
mod = ('  /* ===========================================================\n'
       '   *  v3.0 · PRO TRAINING — módulo completo (autocontenido)\n'
       '   *  =========================================================== */\n'
       + '\n'.join(parts).replace('\n', '\n  ') + '\n')
src = src.replace(anchor, anchor + mod + '\n')

io.open(P, 'w', encoding='utf-8').write(src)
log.append(f'OK modulo ({len(mod)} bytes)')
print('\n'.join(log))
print(f'TAM: {orig_len} -> {len(src)} bytes (+{len(src)-orig_len})')

# ---------- verificación sintáctica del script principal ----------
h = io.open(P, encoding='utf-8').read()
m = re.search(r'<script type="module">(.*?)</script>', h, re.S)
if not m:
    print('FAIL: no se encuentra el script principal')
    sys.exit(1)
io.open('/tmp/v3_main_check.mjs', 'w', encoding='utf-8').write(m.group(1))
r = subprocess.run(['node', '--check', '/tmp/v3_main_check.mjs'], capture_output=True, text=True)
print('node --check main:', 'OK' if r.returncode == 0 else 'FAIL\n' + r.stderr[:3000])
sys.exit(r.returncode)
