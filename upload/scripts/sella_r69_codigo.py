#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r69_codigo.py — FASE 163 · r69 · CORRECCIÓN DEL ARCO.
Informe del dueño tras V3.6.159 en el casco:
  1 · «los tres bloques no se pueden pisar o superponer, deben ir unos
      seguidos a los otros» → panelas TANGENTES y consecutivas: las tres
      a la MISMA distancia 1,15 m (equidistancia real), cada una
      perpendicular a su radio; yaw = γC + γL + 0,8° → bordes paralelos
      con ranura uniforme ~1,7 cm, sin solape angular ni físico.
  2 · «estás colocando mal el menú» → r68 puso el origen del grupo EN la
      cabeza y lookAt hacia delante: el arco nacía a la ESPALDA (la
      convención r67 es grupo DELANTE + lookAt a la cara). Restaurada y
      el arco se centra en la cabeza vía posiciones locales.
  3 · semántica del ancla: al abrir nace justo delante de la mirada y
      queda FIJO; sin chincheta SIGUE a la cabeza SIEMPRE (de frente a
      donde miramos); el botón chincheta congela DONDE ESTÁ (y lo
      recuerda); heal r114 intacto.
  4 · tooltips espacio-conscientes (abrazadera al lienzo de SU espacio —
      1024 legado / 3696 virtual) y nunca bajo la cabecera ni desbordados
      + dedup de los 7 títulos legados que duplicaban la concha."""
import re
import sys
from pathlib import Path

C02 = Path('/home/z/my-project/upload/src/game/core/c02_cfg_escena.js')
C12 = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
n_ok = 0


def edit(path, nombre, ancla, nuevo, esperados=1):
    global n_ok
    t = path.read_text(encoding='utf-8')
    k = t.count(ancla)
    if k != esperados:
        sys.exit(f'ABORTA {nombre}: count={k} (esperaba {esperados})')
    path.write_text(t.replace(ancla, nuevo), encoding='utf-8')
    n_ok += 1


# ------------------------------------------------ c02 · arco sin pisarse
ARCO_NUEVO = """    panelas: [
      // r69 · TANGENTES y SEGUIDAS (petición del dueño: «no se pueden pisar
      // o superponer, deben ir unos seguidos a los otros»): las TRES a la
      // MISMA distancia 1,15 m (equidistancia real), cada panela
      // perpendicular a su radio — los bordes quedan paralelos con una
      // ranura uniforme de ~1,7 cm. yaw = γC + γL + 0,8° con
      // γ = atan(w/2 / d): sin solape angular ni físico.
      { id: 'L', x: 0, w: 1112, anchoM: 0.66, altoM: 0.95, yaw: 37.8, dist: 1.15 },
      { id: 'C', x: 1112, w: 1472, anchoM: 0.88, altoM: 0.95, yaw: 0, dist: 1.15 },
      { id: 'R', x: 2584, w: 1112, anchoM: 0.66, altoM: 0.95, yaw: -37.8, dist: 1.15 },
    ],"""
ARCO_VIEJO = """    panelas: [
      { id: 'L', x: 0, w: 1112, anchoM: 0.74, altoM: 0.95, yaw: 36, dist: 1.25 },
      { id: 'C', x: 1112, w: 1472, anchoM: 0.98, altoM: 0.95, yaw: 0, dist: 1.15 },
      { id: 'R', x: 2584, w: 1112, anchoM: 0.74, altoM: 0.95, yaw: -36, dist: 1.25 },
    ],"""
edit(C02, 'arco v3 tangente', ARCO_VIEJO, ARCO_NUEVO)

# ------------------------------------------- c12 · colocación y anclaje
edit(C12, 'anchorMenu r69', """  anchorMenu() {
    this.camera.getWorldPosition(muHead);
    this.camera.getWorldQuaternion(muQ);
    muDir.set(0, 0, -1).applyQuaternion(muQ);
    muDir.y = 0;
    if (muDir.lengthSq() < 1e-6) muDir.set(0, 0, -1);
    muDir.normalize();
    // r68 · el ORIGEN del grupo es la cabeza: el arco se despliega delante
    this.menuGroup.position.copy(muHead);
    this.menuGroup.lookAt(muHead.x + muDir.x, muHead.y, muHead.z + muDir.z);
    if (this.menuPin) this._menuAnchorUntil = 0;   // fijo: sin flotación
    else this._menuAnchorUntil = performance.now() / 1000 + 1.8;
    this._menuAnchorEst = this._menuEstancia();
    this._menuAnchorRigZ = this.rig ? this.rig.position.z : 0;
  }""", """  anchorMenu(forzar) {
    // r69 · SEMÁNTICA DEL ANCLA (petición del dueño): al ABRIR, el menú
    // nace SIEMPRE justo delante de la mirada y queda FIJO (anclado).
    // Con chincheta, anchorMenu sólo mueve el arco cuando se le OBLIGA
    // (aperturas y heal r114): el botón chincheta congela DONDE ESTÁ y
    // ahí recuerda. Sin chincheta, updateMenu lo re-ancla cada frame:
    // sigue a la cabeza siempre de frente a donde miramos (comportamiento
    // anterior). La firma r114 (estancia + rig z) se conserva.
    if (this.menuPin && !forzar) { this._menuAnchorUntil = 0; return; }
    this.camera.getWorldPosition(muHead);
    this.camera.getWorldQuaternion(muQ);
    muDir.set(0, 0, -1).applyQuaternion(muQ);
    muDir.y = 0;
    if (muDir.lengthSq() < 1e-6) muDir.set(0, 0, -1);
    muDir.normalize();
    // r69 · CONVENCIÓN r67 RESTAURADA (informe del dueño: «estás colocando
    // mal el menú»): el grupo va DELANTE de la cara y mira A la cara
    // (+Z hacia el jugador — así las panelas en -Z quedan delante, como
    // toda la vida). r68 puso el origen EN la cabeza y el arco nacía a la
    // espalda. El arco se centra en la cabeza con las posiciones locales
    // de las panelas (ver buildMenu).
    const D_REF = CONFIG_MENUS.arco.panelas[1].dist;
    this.menuGroup.position.copy(muHead).addScaledVector(muDir, D_REF);
    this.menuGroup.lookAt(muHead);
    this._menuAnchorUntil = 0;
    this._menuAnchorEst = this._menuEstancia();
    this._menuAnchorRigZ = this.rig ? this.rig.position.z : 0;
  }""")

edit(C12, 'panelas en el arco de la cabeza', """      const yaw = (pa.yaw * Math.PI) / 180;
      mesh.position.set(-Math.sin(yaw) * pa.dist,
        CONFIG_MENUS.arco.yCentro, -Math.cos(yaw) * pa.dist);""",
"""      const yaw = (pa.yaw * Math.PI) / 180;
      // r69 · arco centrado en la CABEZA (que vive en local (0,0,D_REF)
      // porque el grupo va delante y mira a la cara): cada panela a su
      // dist sobre el arco — tangentes y seguidas, sin pisarse
      const D_REF = CONFIG_MENUS.arco.panelas[1].dist;
      mesh.position.set(-Math.sin(yaw) * pa.dist,
        CONFIG_MENUS.arco.yCentro, D_REF - Math.cos(yaw) * pa.dist);""")

edit(C12, 'chincheta clicable', """    this._menuPinMesh.position.set(0,
      CONFIG_MENUS.arco.yCentro + 0.475 + 0.032,
      -(CONFIG_MENUS.arco.panelas[1].dist - 0.006));""",
"""    this._menuPinMesh.position.set(0,
      CONFIG_MENUS.arco.yCentro + 0.475 + 0.032, 0.006);""")

edit(C12, 'seguir siempre sin ancla',
     "    if ((performance.now() / 1000) < (this._menuAnchorUntil || 0)) this.anchorMenu();",
     """    // r69 · sin chincheta el arco SIGUE a la cabeza SIEMPRE (de frente a
    // donde miramos — petición del dueño); con chincheta queda clavado
    if (!this.menuPin) this.anchorMenu();""")

edit(C12, 'apertura con forzar (toggle)',
     """      this.menuPin = true;
      this._menuPinDraw();
      this.anchorMenu();          // r68: el arco nace en la cabeza""",
     """      this.menuPin = true;
      this._menuPinDraw();
      this.anchorMenu(true);      // r69: nace delante de la mirada y fijo""")

edit(C12, 'apertura con forzar (prompt B)',
     """    this.menuPin = true;
    this._menuPinDraw();
    this.anchorMenu();""",
     """    this.menuPin = true;
    this._menuPinDraw();
    this.anchorMenu(true);""")

edit(C12, 'apertura con forzar (opts rápida)',
     """      this.menuHover = [-1, -1];
      this.anchorMenu();
      this.drawMenu();""",
     """      this.menuHover = [-1, -1];
      this.anchorMenu(true);
      this.drawMenu();""")

# ------------------------------------------------- c12 · tooltip limpio
edit(C12, 'tooltip espacio consciente (envoltura)',
     """    // envoltura a 2 líneas máx. (860 px de ancho)
    c.font = '600 21px system-ui, sans-serif';""",
     """    // r69 · ESPACIO CONSCIENTE: bajo el transform del legado el rect
    // vive en 1024×1536; en el Vestíbulo/rejilla/prompts (identidad) en
    // el lienzo virtual 3696×1400. La burbuja se abrazadera a SU espacio:
    // siempre sobre el objeto apuntado, sin desbordes ni fuera de lugar.
    const ESP = this._menuMap
      ? { w: 1024, techo: 60, env: 860 }
      : { w: CONFIG_MENUS.lienzo.ancho, techo: 226, env: 2200 };
    // envoltura a 2 líneas máx.
    c.font = '600 21px system-ui, sans-serif';""")
edit(C12, 'tooltip abrazadera',
     """      if (c.measureText(cand).width > 860 && lin) { lines.push(lin); lin = w; }""",
     """      if (c.measureText(cand).width > ESP.env && lin) { lines.push(lin); lin = w; }""")
edit(C12, 'tooltip burbuja',
     """    const wBox = Math.min(924, Math.max(...lines.map((l) => c.measureText(l).width)) + 48);
    const hBox = lines.length * 28 + 22;
    const cx = Math.min(Math.max(r.x + r.w / 2, wBox / 2 + 14), 1024 - wBox / 2 - 14);
    // encima del botón; si no cabe, debajo (14 px de hueco para la cola)
    const above = r.y - hBox - 14 > 60;
    const yBox = above ? r.y - hBox - 14 : r.y + r.h + 14;""",
     """    const wBox = Math.min(ESP.w - 100,
      Math.max(...lines.map((l) => c.measureText(l).width)) + 48);
    const hBox = lines.length * 28 + 22;
    const cx = Math.min(Math.max(r.x + r.w / 2, wBox / 2 + 14),
      ESP.w - wBox / 2 - 14);
    // encima del objeto; si no cabe o invade la cabecera, debajo
    const above = r.y - hBox - 14 > ESP.techo;
    let yBox = above ? r.y - hBox - 14 : r.y + r.h + 14;
    yBox = Math.min(yBox, (this._menuMap ? 1536 : CONFIG_MENUS.lienzo.alto)
      - hBox - 10);""")

# ------------------------------------- c12 · dedup de títulos del legado
for ancla in [
    "    label(T('tab_multi'), 244, 26);\n",
    "    label(T('join_title'), 240, 26);\n",
    "    label(T('name_title'), 240, 26);\n",
    "    label(T('pala_gname_title'), 240, 26);\n",
    "    label(T('sec_rank'), 240, 26);\n",
    "    c.fillText(T('rankme_t'), 512, 312);\n",
    "    c.fillText(T('carrera_lbl'), 512, 312);\n",
]:
    edit(C12, f'dedup {ancla.strip()[8:30]}…', ancla, '')

F.write_text if False else None
