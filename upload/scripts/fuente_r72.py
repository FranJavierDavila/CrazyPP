#!/usr/bin/env python3
# r72 · PORTA los parches al CÓDIGO FUENTE (src/game/core/) — la casa
# ensambla public/game.html desde las fuentes (bump_version → build_game),
# así que los cambios viven AQUÍ, no en el artefacto.
#  · c12_pingponggame.js: P0 anti-bucle (3 parches) + maquillaje btn/rank/
#    rankme + re-espaciado de optsCat.
#  · c02_cfg_escena.js: fuera la tarjeta kofi de la rejilla de AJUSTES.
import re
import sys

C12 = '/home/z/my-project/upload/src/game/core/c12_pingponggame.js'
C02 = '/home/z/my-project/upload/src/game/core/c02_cfg_escena.js'

fail = False

# ───────────────────────────── c12 ─────────────────────────────
s = open(C12, encoding='utf-8').read()
orig = len(s)

EDITS12 = []
EDITS12.append(('P0-1 guarda anti-bucle', """    // r70 · WORLDRANK fresco al aterrizar (silencioso, como r67)
    WORLDRANK.load(true).then(() => {
      if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();
    }).catch(() => { /* nunca rompe */ });
  }""", """    // r72 · FIX CONGELAMIENTO (informe del dueño: «al pulsar Ranking Mundial
    // se queda congelado»): el reloj vivía DENTRO del dibujo y su .then()
    // redibujaba ESTA MISMA página, que volvía a disparar el load(true) —
    // ciclo GET+redibujo sin fin que en la Quest saturaba el navegador
    // (juego congelado). Ahora UNA sola revalidación por aterrizaje:
    // _rankiniFresh se arma al ENTRAR en la página (page:/wrl:open) y el
    // dibujo jamás vuelve a disparar la petición.
    if (!this._rankiniFresh) {
      this._rankiniFresh = true;
      WORLDRANK.load(true).then(() => {
        if (this.menuOpen && this.menuPage === 'rankini') this.drawMenu();
      }).catch(() => { /* nunca rompe */ });
    }
  }"""))
EDITS12.append(('P0-2 wrl:open', """        if (arg === 'open') {
          this.menuPage = 'rankini';
          WORLDRANK.load(true).then(() => {
            if (this.menuOpen && this.menuPage === 'rank') this.drawMenu();
          }).catch(() => { /* nunca rompe */ });
        } else if (arg === 'tab') {""", """        if (arg === 'open') {
          this.menuPage = 'rankini';
          // r72 · re-arma el reloj único de aterrizaje (fuera el load(true)
          // muerto que miraba 'rank': el refresco lo hace el propio landing,
          // UNA sola vez, con su guarda anti-bucle).
          this._rankiniFresh = false;
        } else if (arg === 'tab') {"""))
EDITS12.append(('P0-3 case page', """          this.menuPage = arg;
          this._resetArm = false;""", """          this.menuPage = arg;
          this._resetArm = false;
          if (arg === 'rankini') this._rankiniFresh = false;   // r72 · reloj único de aterrizaje"""))
EDITS12.append(('btn radio 16', """      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 14);
      if (active) {""", """      const hovered = this.menuHover.includes(rects.length);
      rr(x, y, w, h, 16);
      if (active) {"""))
EDITS12.append(('btn latón+degradado', """      } else {
        c.fillStyle = 'rgba(255,255,255,0.07)';
        c.fill();
        // r104 · borde más DEFINIDO (0.18 → 0.30): «opciones más claras y
        // mejor definidas» — cada botón se recorta bien sobre el fondo
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(255,255,255,0.30)';""", """      } else {
        // r72 · maquillaje del NIVEL 3 (petición del dueño: «los menús de
        // tercer nivel siguen en el formato antiguo»): el botón compartido
        // viste el lenguaje de las landings — relleno en degradado sutil y
        // MARCO DE LATÓN en reposo (antes gris neutro). OptCat, teclados,
        // asks, sala y las páginas de c13 reciben el mismo pintor: el nivel
        // 3 entero se maqueta en una sola pieza.
        const _g72 = c.createLinearGradient(x, y, x, y + h);
        _g72.addColorStop(0, 'rgba(255,255,255,0.10)');
        _g72.addColorStop(1, 'rgba(255,255,255,0.045)');
        c.fillStyle = _g72;
        c.fill();
        // r104 · borde DEFINIDO (conservado) · r72 · reposo en latón
        c.strokeStyle = hovered ? '#ffffff' : 'rgba(232,180,90,0.32)';"""))
EDITS12.append(('rank cabeceras oro', """    // cabecera de columnas
    c.fillStyle = '#98a6b4';
    c.font = '700 20px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('wrl_col_name'), 150, 372);""", """    // cabecera de columnas — r72 · en ORO (placa de museo, lenguaje nuevo)
    c.fillStyle = '#e8b45a';
    c.font = '800 22px system-ui, sans-serif';
    c.textAlign = 'left';
    c.fillText(T('wrl_col_name'), 150, 372);"""))
EDITS12.append(('rankme ELO oro', """    c.fillStyle = '#ffffff';
    c.font = '900 92px system-ui, sans-serif';
    c.fillText(String(D.elo || 1000), 512, 445);""", """    // r72 · ELO en ORO (placa de RÉCORD del museo, lenguaje nuevo)
    c.fillStyle = '#ffd257';
    c.font = '900 92px system-ui, sans-serif';
    c.fillText(String(D.elo || 1000), 512, 445);"""))
EDITS12.append(('rankme tarjetas latón', """      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - 140, colY, 280, 92, 14); else c.rect(cx - 140, colY, 280, 92);
      c.fill();""", """      c.fillStyle = 'rgba(255,255,255,0.06)';
      c.beginPath();
      if (c.roundRect) c.roundRect(cx - 140, colY, 280, 92, 14); else c.rect(cx - 140, colY, 280, 92);
      c.fill();
      // r72 · marco de latón (lenguaje de las landings)
      c.strokeStyle = 'rgba(232,180,90,0.35)';
      c.lineWidth = 2;
      c.stroke();"""))

for nombre, old, new in EDITS12:
    n = s.count(old)
    print(f'[c12 · {nombre}] old={n}')
    if n != 1:
        print('  !! conteo inesperado'); fail = True; continue
    s = s.replace(old, new)

# — re-espaciado de optsCat (regex acotada a la función) —
i = s.find('drawMenuOptsCat(rects, cat) {')
if i < 0:
    print('FALLO: drawMenuOptsCat no hallado en c12'); fail = True
else:
    k = s.find('\n  /**', i)          # fin de la función (siguiente doc de clase)
    seg0 = s[i:k]
    def bump_h(m):
        return m.group(1) + str(min(int(m.group(2)) + 6, 92)) + m.group(3)
    def bump_y(m):
        return 'y += ' + str(int(m.group(1)) + 8) + ';'
    seg, n_h = re.subn(r'(, y, \d{2,3}, )(\d{2,3})(,)', bump_h, seg0)
    seg, n_y = re.subn(r'y \+= (\d+);', bump_y, seg)
    print(f'[c12 · optsCat re-espaciado] alturas={n_h} pasos={n_y} delta={len(seg)-len(seg0):+d} B')
    if n_h < 20 or n_y < 20:
        print('  !! demasiados pocos reemplazos'); fail = True
    else:
        s = s[:i] + seg + s[k:]

if not fail:
    open(C12, 'w', encoding='utf-8').write(s)
    print(f'c12: {orig} → {len(s)} B (delta {len(s)-orig:+d})')

# ───────────────────────────── c02 ─────────────────────────────
t = open(C02, encoding='utf-8').read()
orig2 = len(t)
old_kofi = """        { id: 'kofi', icono: 'apoyar', etiquetaKey: 'btn_kofi',
          gradiente: ['#ffd25e', '#e8a80e'] },
"""
n = t.count(old_kofi)
print(f"[c02 · kofi fuera] old={n}")
if n == 1:
    t = t.replace(old_kofi, """        // r72 · FUERA «Apoyar el proyecto (Ko-fi)» de AJUSTES (petición del
        // dueño): la tarjeta se retira de la rejilla; el canal kofi de la
        // portada web (dock/footlink) no se toca.
""")
    open(C02, 'w', encoding='utf-8').write(t)
    print(f'c02: {orig2} → {len(t)} B (delta {len(t)-orig2:+d})')
else:
    print('  !! conteo inesperado en c02'); fail = True

print('RESULTADO:', 'PARCIAL — revisar' if fail else 'TODO OK')
sys.exit(1 if fail else 0)
