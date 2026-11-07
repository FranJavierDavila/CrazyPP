#!/usr/bin/env python3
# r103 · ANCLAJE AL RIG EN HALLOWEEN — petición del dueño: los rivales de los
# campeonatos SIEMPRE anclados a la posición de la mesa (independiente de
# recentrados y escaneos). Halloween era el único módulo que colgaba el rival
# (y cartel, manos, dianas, efectos) de game.SCENE en vez de game.RIG — el rig
# es el marco que rota updateRecenter(); al recentrar, mesa+sala giran y lo
# anclado a scene se queda atrás («el zombi detrás de la mesa a la altura de
# la raqueta»). Cambio mecánico scene→(rig || scene) en TODO lo anclado a
# mesa; se PRESERVAN los casos de mundo real: visor de cámara (moscas),
# calabaza hija del padre de la bola (r97) y haz de la pistola (rayo XR en
# mundo). + conversión mundo→rig del billboard de manos y del rayo de dianas.
import io, sys

P = '/home/z/my-project/public/championships/halloween/index.js'
src = io.open(P, encoding='utf-8').read().split('\n')

def swap(lineno, old, new, tag):
    i = lineno - 1
    if old not in src[i]:
        print(f'FALLO {tag}: linea {lineno} no contiene el texto esperado:\n  {src[i]!r}')
        sys.exit(1)
    src[i] = src[i].replace(old, new)
    print(f'ok {tag} @ {lineno}')

# --- sustituciones mecánicas scene → (rig || scene) -------------------------
RIG = '(game.rig || game.scene).'
RIGT = '(this.game.rig || this.game.scene).'

swap(167,  '(this.game.scene || this.game.rig).add(this.r.node)',
           '(this.game.rig || this.game.scene).add(this.r.node)', 'RIVAL')
swap(290,  'game.scene.add(cartel.mesh);',  RIG + 'add(cartel.mesh);', 'CARTEL')
swap(586,  'game.scene.add(m);',            RIG + 'add(m);',            'GLOBOS-ini')
swap(609,  'game.scene.remove(o.s);',       RIG + 'remove(o.s);',       'GLOBOS-fin')
swap(720,  'game.scene.add(m);',            RIG + 'add(m);',            'TROZO-al')
swap(732,  'game.scene.add(s);',            RIG + 'add(s);',            'HUMO-r88')
swap(750,  'game.scene.remove(t.m);',       RIG + 'remove(t.m);',       'TROZO-kill')
swap(766,  'game.scene.remove(h.s);',       RIG + 'remove(h.s);',       'HUMO-kill')
swap(770,  'game.scene.remove(t.m);',       RIG + 'remove(t.m);',       'TROZO-limpia')
swap(772,  'game.scene.remove(h.s);',       RIG + 'remove(h.s);',       'HUMO-limpia')
swap(926,  'game.scene.add(M.grupo);',      RIG + 'add(M.grupo);',      'MANOS-grupo')
swap(1168, 'game.scene.remove(M.grupo);',   RIG + 'remove(M.grupo);',   'MANOS-fin')
swap(1482, 'game.scene.add(m);',            RIG + 'add(m);',            'MANCHA')
swap(1510, 'game.scene.add(s);',            RIG + 'add(s);',            'SALPICA')
swap(1578, 'game.scene.add(s);',            RIG + 'add(s);',            'HUMO-diana')
swap(1589, 'game.scene.remove(h.s);',       RIG + 'remove(h.s);',       'HUMO-diana-kill')
swap(1600, 'game.scene.remove(m);',         RIG + 'remove(m);',         'MANCHAS-fin')
swap(1601, 'game.scene.remove(h.s);',       RIG + 'remove(h.s);',       'HUMO-fin')
swap(1643, 'game.scene.add(mesh);',         RIG + 'add(mesh);',         'WARM-mesh')
swap(1649, 'game.scene.add(sp);',           RIG + 'add(sp);',           'WARM-sp')
swap(1652, 'game.scene.remove(w);',         RIG + 'remove(w);',         'WARM-off')
swap(1781, 'this.game.scene.add(this.hud);', RIGT + 'add(this.hud);',   'HUD')
swap(1794, 'this.game.scene.add(s);',       RIGT + 'add(s);',           'DIANA')
swap(1917, 'this.game.scene.remove(this.hud);', RIGT + 'remove(this.hud);', 'HUD-fin')
swap(1918, 'this.game.scene.remove(d.s);',  RIGT + 'remove(d.s);',      'VIVAS-fin')
swap(2136, 'this.game.scene.remove(this.cartel.mesh);', RIGT + 'remove(this.cartel.mesh);', 'CARTEL-fin')
swap(2137, 'this.game.scene.remove(this._insignia);',   RIGT + 'remove(this._insignia);', 'INSIGNIA-fin')
swap(2306, 'this.game.scene.add(m);',       RIGT + 'add(m);',           'CARTE-ARTISTA')

# --- NOTA r103: el billboard de la mano (999) y el rayo de la pistola
# (_disparaDianas) ya están aplicados a mano con el editor — aquí sólo los
# swaps mecánicos, que el primer intento perdió al abortar sin escribir.
MODO = 'solo_swaps'

if MODO != 'solo_swaps':
    # --- billboard de la mano: cámara MUNDO → espacio RIG ----------------------
    i = 999  # línea 1000
    blob = '\n'.join(src[998:1006])
    if '_v86.setFromMatrixPosition(cam.matrixWorld);' not in blob or 'mano.rotation.y = Math.atan2(_v86.x - x' not in blob:
        print('FALLO MANO-BILLBOARD: contexto no encontrado'); sys.exit(1)
    old = """      _v86.setFromMatrixPosition(cam.matrixWorld);
      mano.rotation.y = Math.atan2(_v86.x - x, _v86.z - z);"""
    new = """      _v86.setFromMatrixPosition(cam.matrixWorld);
      /* r103 · la cámara vive en MUNDO y la mano en el RIG (marco de la
       * mesa): convertir antes del billboard (patron c12 r73 worldToLocal) */
      const raiz103 = game.rig || game.scene;
      if (raiz103 && raiz103.worldToLocal) raiz103.worldToLocal(_v86);
      mano.rotation.y = Math.atan2(_v86.x - x, _v86.z - z);"""
    for k in range(998, 1006):
        if old in '\n'.join(src[k:k+2]):
            src[k:k+2] = new.split('\n')
            print(f'ok MANO-BILLBOARD @ {k+1}')
            break
    else:
        print('FALLO MANO-BILLBOARD: par de líneas no encontrado'); sys.exit(1)

    # --- rayo de la pistola: origen/dir MUNDO → espacio de las dianas (RIG) ----
    j = next(k for k, l in enumerate(src) if '_disparaDianas(origen, dir) {' in l)
    old_d = """  _disparaDianas(origen, dir) {
    const pr = this.ctrl.pruebaActual();
    for (const d of pr.vivas) {
      if (d.vida < 0 || !d.s.visible) continue;
      const t0 = new THREE.Vector3().subVectors(d.s.position, origen);
      const tProy = t0.dot(dir);
      if (tProy < 0 || tProy > this.alcance) continue;
      const punto = origen.clone().addScaledVector(dir, tProy);"""
    new_d = """  _disparaDianas(origen, dir) {
    const pr = this.ctrl.pruebaActual();
    /* r103 · las dianas viven en el RIG (marco de la mesa — anclaje al
     * recentrado) y el rayo de la cámara XR viene en MUNDO: convertir
     * origen+dir al espacio de las dianas (patron c12 r73 worldToLocal).
     * El HAZ visual sigue en mundo (scene): nace de la cámara XR. */
    const raiz = this.game.rig || this.game.scene;
    let oR = origen, dR = dir;
    try {
      if (raiz && raiz.worldToLocal) {
        oR = origen.clone(); raiz.worldToLocal(oR);
        dR = dir.clone().applyQuaternion(
          raiz.getWorldQuaternion(new THREE.Quaternion()).invert());
      }
    } catch (e) { oR = origen; dR = dir; }
    for (const d of pr.vivas) {
      if (d.vida < 0 || !d.s.visible) continue;
      const t0 = new THREE.Vector3().subVectors(d.s.position, oR);
      const tProy = t0.dot(dR);
      if (tProy < 0 || tProy > this.alcance) continue;
      const punto = oR.clone().addScaledVector(dR, tProy);"""
    if '\n'.join(src[j:j+8]) != old_d:
        print('FALLO PISTOLA: bloque no coincide:\n' + '\n'.join(src[j:j+8])); sys.exit(1)
    src[j:j+8] = new_d.split('\n')
    print(f'ok PISTOLA @ {j+1}')

io.open(P, 'w', encoding='utf-8', newline='\n').write('\n'.join(src))
print('ESCRITO OK')
