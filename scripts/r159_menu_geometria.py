#!/usr/bin/env python3
# r159 · petición del dueño (2026-11-28):
#   1. El menú 1 m más alejado: panelas dist 1,00 → 2,00 m.
#   2. Algo más grande: altoM 0,95 → 1,20 m (+26 %). La fórmula r69
#      recalcula tangencias y yaws sola; el hit-test mapea uv→lienzo y no
#      depende de la distancia.
#   3. La chincheta superior se ELIMINA (UI: malla+icono+toggle+hover -2+
#      raycast+FX+i18n). El ANCLA conserva el comportamiento por defecto
#      r68 (fija en la cabeza en cada apertura): menuPin=true interno.
# v2: opera sobre las FUENTES reales (src/game/core/*.js) — public/game.html
#     es un artefacto que bump_version.py regenera y me machacó el parche.
#     Cada parche exige N coincidencias exactas o aborta sin escribir.
#     NOTA: el reemplazo del láser lleva el paréntesis corregido (la v1
#     dejó un ')' huérfano — Unexpected token, cazado por la sonda boot).
import sys

RAIZ = '/home/z/my-project/src/game/'
F_C02 = RAIZ + 'core/c02_cfg_escena.js'
F_C12 = RAIZ + 'core/c12_pingponggame.js'
F_C00 = RAIZ + 'core/c00_pre_three.js'

with open(F_C02, 'r', encoding='utf-8') as f: src_c02 = f.read()
with open(F_C12, 'r', encoding='utf-8') as f: src_c12 = f.read()
with open(F_C00, 'r', encoding='utf-8') as f: src_c00 = f.read()

# (fichero, viejo, nuevo, N esperadas)
PARCHES = []

def p(f, old, new, n=1):
    PARCHES.append((f, old, new, n))

# ── 1. GEOMETRÍA DEL ARCO (c02) ────────────────────────────────────────
p(F_C02, """      { id: 'L', x: 0, w: 1112, altoM: 0.95, dist: 1.00 },
      { id: 'C', x: 1112, w: 1472, altoM: 0.95, dist: 1.00 },
      { id: 'R', x: 2584, w: 1112, altoM: 0.95, dist: 1.00 },""",
"""      // r159 · petición del dueño («1 metro más alejado y algo más
      // grande»): dist 1,00 → 2,00 m y altoM 0,95 → 1,20 m (+26 %). La
      // fórmula r69 recalcula tangencias y yaws sola; el hit-test vive en
      // el lienzo (uv) y no depende de la distancia.
      { id: 'L', x: 0, w: 1112, altoM: 1.20, dist: 2.00 },
      { id: 'C', x: 1112, w: 1472, altoM: 1.20, dist: 2.00 },
      { id: 'R', x: 2584, w: 1112, altoM: 1.20, dist: 2.00 },""")

# ── 2. CHINCHETA: alta de la malla + icono (c12) ──────────────────────
p(F_C12, """    /* r113 · LA CHINCHETA DEL MENÚ. r68 · FASE 162 · ON POR DEFECTO
     * (petición del dueño: «por defecto el menú aparecerá anclado en el
     * centro (chincheta pulsada) a una distancia que permita su lectura
     * cómoda, incluso los textos más pequeños»): cada APERTURA ancla el
     * arco EN LA CABEZA (anchorMenu) y el pin lo deja FIJO sin flotación.
     * Soltarla devuelve el modo flotante r113 (sigue a la cabeza 1,8 s). */""",
"""    /* r159 · LA CHINCHETA SE RETIRA (petición del dueño: «la chincheta
     * superior ya no tiene sentido, se puede eliminar»). Fuera malla,
     * icono, toggle y hover: el ANCLA conserva desde dentro el
     * comportamiento que la chincheta puesta daba por defecto desde r68 —
     * cada APERTURA firma el ancla EN LA CABEZA (anchorMenu) y el arco
     * queda FIJO sin flotación (menuPin=true interno, sin UI). */""")

p(F_C12, """    this._menuPinCv = document.createElement('canvas');
    this._menuPinCv.width = 128;
    this._menuPinCv.height = 128;
    this._menuPinTex = new THREE.CanvasTexture(this._menuPinCv);
    this._menuPinTex.colorSpace = THREE.SRGBColorSpace;
    this._menuPinMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(0.085, 0.085),
      new THREE.MeshBasicMaterial({ map: this._menuPinTex, transparent: true, depthTest: false }),
    );
    // centro superior del panel 0,90×1,35: borde arriba en y=+0,675 — la
    // chincheta cabalga el borde (+0,032 hacia arriba) como un pin real
    // r68 · el pin cabalga el borde superior de la PANELA CENTRAL del arco
    this._menuPinMesh.position.set(0,
      CONFIG_MENUS.arco.yCentro + 0.475 + 0.032, 0.006);
    this._menuPinMesh.renderOrder = 9998;
    this.menuGroup.add(this._menuPinMesh);
    this._menuPinDraw();
""", "")

# ── 3. Aperturas: sin _menuPinDraw (c12) ──────────────────────────────
p(F_C12, """      // r68 · cada apertura nace EN LA CABEZA y CON LA CHINCHETA PUESTA
      // (petición del dueño): el arco aparece centrado, equidistante y fijo.
      // La honestidad r114 sigue garantizada: el ancla se re-firma aquí
      // (estancia + rig z) y el heal r114 re-ancla si la escena viaja.
      this.menuPin = true;
      this._menuPinDraw();""",
"""      // r68 · cada apertura nace EN LA CABEZA y FIJA (r159: sin chincheta,
      // el ancla interior es la misma que la chincheta puesta): el arco
      // aparece centrado, equidistante y fijo. La honestidad r114 sigue
      // garantizada: el ancla se re-firma aquí (estancia + rig z) y el
      // heal r114 re-ancla si la escena viaja.
      this.menuPin = true;""")

p(F_C12, """    // r68 · el prompt B también nace en la cabeza con la chincheta puesta
    this.menuPin = true;
    this._menuPinDraw();""",
"""    // r68 · el prompt B también nace en la cabeza y fijo (r159: sin pin)
    this.menuPin = true;""")

# ── 4. FX de entrada/salida: sin la malla del pin (c12) ───────────────
p(F_C12, """      if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1 - e;
""", "")
p(F_C12, """        if (this._menuPinMesh) this._menuPinMesh.material.opacity = 1;
""", "")
p(F_C12, """      if (this._menuPinMesh) {
        const pC = Math.min(1, Math.max(0,
          (ahora - this._menuFxCascada.C) / 320));
        this._menuPinMesh.material.opacity = Math.min(1, pC * 1.6);
      }
""", "")

# ── 5. _menuPinDraw + _menuPinToggle: funciones enteras fuera (c12) ───
# v1 renombró la cabecera y dejó el cuerpo huérfano (lo arregló
# r159_fix_residuos por índice); v2 borra de una pieza, sin trucos.
p(F_C12, """  /* r113 · CHINCHETA DEL MENÚ — dibujo del icono (128², estilo de la casa):
   * badge circular oscuro + chincheta de silueta. OFF: pin PLATEADO con
   * puntas fuera (menú libre, sigue a la cabeza). ON: pin DORADO clavado
   * con aro de anclaje (menú fijo en el espacio). */
  _menuPinDraw() {
    const c = this._menuPinCv.getContext('2d');
    c.clearRect(0, 0, 128, 128);
    // badge de fondo (target de pulso legible sobre cualquier arte)
    c.beginPath();
    c.arc(64, 64, 56, 0, Math.PI * 2);
    c.fillStyle = 'rgba(13,16,23,0.82)';
    c.fill();
    c.lineWidth = 4;
    c.strokeStyle = this.menuPin ? 'rgba(232,180,90,0.95)' : 'rgba(255,255,255,0.35)';
    c.stroke();
    // chincheta (vista lateral): cabeza + cuello + aguja
    const oro = this.menuPin;
    c.lineCap = 'round';
    c.lineJoin = 'round';
    // aguja (clavada hacia abajo-derecha si ON; recta si OFF)
    c.strokeStyle = oro ? '#ffe9a8' : '#aeb9c4';
    c.lineWidth = 7;
    c.beginPath();
    c.moveTo(64, 62);
    if (oro) { c.lineTo(84, 96); }
    else { c.lineTo(64, 100); }
    c.stroke();
    // punta
    c.lineWidth = 2.5;
    c.beginPath();
    c.arc(oro ? 84 : 64, oro ? 96 : 100, 2.5, 0, Math.PI * 2);
    c.fillStyle = oro ? '#ffe9a8' : '#aeb9c4';
    c.fill();
    // cabeza del pin (domo)
    c.beginPath();
    c.arc(64, 48, 19, 0, Math.PI * 2);
    const g = c.createLinearGradient(45, 29, 83, 67);
    if (oro) { g.addColorStop(0, '#fff3cf'); g.addColorStop(0.55, '#e8b45a'); g.addColorStop(1, '#8f6a24'); }
    else { g.addColorStop(0, '#e8eef4'); g.addColorStop(0.55, '#93a1ae'); g.addColorStop(1, '#525d68'); }
    c.fillStyle = g;
    c.fill();
    c.lineWidth = 3;
    c.strokeStyle = oro ? 'rgba(255,233,168,0.9)' : 'rgba(255,255,255,0.45)';
    c.stroke();
    // brillo del domo
    c.beginPath();
    c.ellipse(57, 42, 6, 4, -0.5, 0, Math.PI * 2);
    c.fillStyle = 'rgba(255,255,255,0.55)';
    c.fill();
    // con el pin puesto: aro de ANCLAJO alrededor (estado inequívoco)
    if (oro) {
      c.beginPath();
      c.arc(64, 64, 47, 0, Math.PI * 2);
      c.setLineDash([9, 7]);
      c.lineWidth = 4;
      c.strokeStyle = 'rgba(232,180,90,0.8)';
      c.stroke();
      c.setLineDash([]);
    }
    if (this._menuPinTex) this._menuPinTex.needsUpdate = true;
  }

  /* r113 · pulso de la chincheta: ancla el menú en su punto del espacio /
   * lo suelta (vuelve a anclarse delante de la cabeza). Feedback: arpegio,
   * háptica por la mano que pulsa y rótulo breve en el mensaje del HUD. */
  _menuPinToggle(hand) {
    this.menuPin = !this.menuPin;
    this._menuPinDraw();
    try { this.audio.playOsc(this.menuPin ? 620 : 470, this.menuPin ? 930 : 340, 0.09, 'sine', 0.14, 0); } catch (ePin1) { /* */ }
    if (this.renderer.xr.isPresenting) this.haptic(hand, 0.5, 90);
    try {
      const mPin = T(this.menuPin ? 'menu_pin_on' : 'menu_pin_off');
      this.rules.message = mPin;
      clearTimeout(this._menuPinMsgTo);
      this._menuPinMsgTo = setTimeout(() => {
        try { if (this.rules.message === mPin) this.rules.message = ''; } catch (ePM2) { /* */ }
      }, 2600);
    } catch (ePin2) { /* */ }
    // soltar = el panel regresa a la cabeza (la flotación se reanuda sola)
    if (!this.menuPin) this.anchorMenu();
  }
""", "")

# ── 6. Raycast del pin (hover -2) fuera (c12) ─────────────────────────
p(F_C12, """        // r113 · CHINCHETA: el rayo también busca el pin (prioridad sobre el
        // panel: cuelga 6 mm por delante del plano). Sólo con el menú abierto.
        let pinHit = null;
        if (this.menuOpen && !this._arconoOn && this._menuPinMesh) {
          pinHit = muRaycaster.intersectObject(this._menuPinMesh, false)[0] || null;
        }
""", "")
p(F_C12, """        // r113 · hover del PIN: el cursor salta a la chincheta y el haz se
        // engorda como sobre un botón (idx especial -2 — nunca colisiona con
        // los índices reales de menuRects)
        if (pinHit) {
          idx = -2;
          dot.visible = true;
          dot.position.copy(this.menuGroup.worldToLocal(pinHit.point.clone()));
        }
""", "")
p(F_C12, """        line.visible = enEstancia || !!hit || !!pinHit;""",
"""        line.visible = enEstancia || !!hit;""")
p(F_C12, """          (pinHit ? pinHit.distance : (hit ? hit.distance : (enEstancia ? 3 : 0.5)));""",
"""          (hit ? hit.distance : (enEstancia ? 3 : 0.5));""")
p(F_C12, """        const thick = (idx >= 0 || idx === -2 || sobreMesa) ? 1.7 : 1;""",
"""        const thick = (idx >= 0 || sobreMesa) ? 1.7 : 1;""")

# ── 7. onSelectStart: sin rama -2 (c12) ───────────────────────────────
p(F_C12, """      const hov = this.menuHover[i];
      // r113 · CHINCHETA: hover -2 = el gatillo pega/suelta el panel
      if (hov === -2) this._menuPinToggle(i);
      else if (hov >= 0) this.menuClick(hov, i);   // r96: mano que pulsa (deslizadores)""",
"""      const hov = this.menuHover[i];
      if (hov >= 0) this.menuClick(hov, i);   // r96: mano que pulsa (deslizadores)""")

# ── 8. sitio r85: nace fijo, sin pin (c12) ────────────────────────────
p(F_C12, """      this.menuPin = true;       // r85 · nace CON CHINCHETA (convención de la casa)
      this._menuPinDraw();
""",
"""      this.menuPin = true;       // r85 · nace FIJO (r159: convención sin pin)
""")

# ── 9. i18n: claves del pin fuera (c00, es + en) ──────────────────────
p(F_C00, """    menu_pin_off: 'Chincheta: el menú sigue tu cabeza',
    menu_pin_on: 'Chincheta puesta: menú anclado aquí',
""", "")
p(F_C00, """    menu_pin_off: 'Pushpin: menu follows your head',
    menu_pin_on: 'Pushpin set: menu pinned here',
""", "")

# ── aplicar ────────────────────────────────────────────────────────────
BUFF = {F_C02: src_c02, F_C12: src_c12, F_C00: src_c00}
fallos = []
for i, (f, old, new, n) in enumerate(PARCHES):
    c = BUFF[f].count(old)
    if c != n:
        fallos.append((i, f.split('/')[-1], c, n, old[:60].replace('\n', '⏎')))
if fallos:
    for i, nom, c, n, frag in fallos:
        print(f"✗ parche {i} [{nom}]: {c} coincidencias (esperaba {n}) — {frag}…")
    sys.exit(1)

for f, old, new, _ in PARCHES:
    BUFF[f] = BUFF[f].replace(old, new)

for f, s in BUFF.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")

todo = ''.join(BUFF.values())
# residuos que NO deben quedar (código vivo del pin):
residuos = ['_menuPinCv', '_menuPinTex', '_menuPinMesh', '_menuPinDraw',
            '_menuPinToggle', 'pinHit', "menu_pin_off", "menu_pin_on",
            "idx === -2", "hov === -2", "altoM: 0.95", "dist: 1.00",
            "RETIRADA_R159"]
mal = [r for r in residuos if r in todo]
print("✓ sin residuos de la chincheta" if not mal else f"✗ RESIDUOS: {mal}")
print(f"  menuPin=true restante (ancla interna): {todo.count('this.menuPin = true')} sitios")
