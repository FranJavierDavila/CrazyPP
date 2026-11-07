#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""patch_r73_telon.py — reemplaza el bloque del telón (showChampCurtain ..
hideChampCurtain) en c12 por el TELÓN DE TEATRO r73."""
import io

P = '/home/z/my-project/src/game/core/c12_pingponggame.js'
src = io.open(P, encoding='utf-8').read()

START = '  showChampCurtain(id) {'
END = '  showChampIntro(id) {'
i0 = src.index(START)
i1 = src.index(END)
assert i0 < i1, 'orden inesperado'

NUEVO = '''  /* ====================================================================
   *  r73 · TELÓN DE TEATRO (rediseño total a petición del dueño:
   *  «no es poner un pegote de pantalla sino que todo el entorno que nos
   *  rodea esté negro con el texto delante hasta que carga el escenario»).
   *  - ENTORNO NEGRO COMPLETO: esfera invertida (BackSide) de 12 m de
   *    radio colgada del rig y CENTRADA EN LA CABEZA cada tick — pared,
   *    mesa, troqueles y passthrough desaparecen: el mundo entero se
   *    apaga mientras llega el escenario.
   *  - CARTEL A 2 METROS: tarjeta de intermedio de teatro que sigue a la
   *    cabeza (giro y altura) a 2,00 m exactos, SIEMPRE de cara al visor.
   *  - TARJETA: doble marco dorado, «CRAZY PING PONG PRESENTA», título
   *    del campeonato en SU color (autoajuste), «Montando el escenario…»
   *    con puntos y una BOLA que va y viene sobre una pista con red — el
   *    ping pong nunca se apaga. Fundido de salida que desmonta TODO.
   *  Tick en TIEMPO REAL (r72), tope 12 s, API {cierra, espera} intacta.
   *  ==================================================================== */
  showChampCurtain(id) {
    try {
      if (!this.rig) return null;
      this.hideChampCurtain(true);
      // título del campeonato para la tarjeta
      let ttl = id;
      try {
        const ent = ((this.champs && this.champs.entries) || []).find((x) => x.id === id);
        const tt = ent && ent.title;
        if (tt) ttl = String((__ppLang === 'en') ? (tt.en || tt.es) : (tt.es || tt.en)) || id;
      } catch (e0) { /* */ }
      const cols = this._telonCols(id);
      const W = 1024, H = 640;
      const cv = document.createElement('canvas');
      cv.width = W; cv.height = H;
      const c = cv.getContext('2d');
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      // 1) LA NADA: esfera negra que se TRAGA el mundo (pinta ANTES del cartel)
      const matEs = new THREE.MeshBasicMaterial({
        color: 0x000000, side: THREE.BackSide,
        depthTest: false, depthWrite: false, fog: false, transparent: true,
      });
      const esfera = new THREE.Mesh(new THREE.SphereGeometry(12, 28, 18), matEs);
      esfera.renderOrder = 65;          // tapa TODO lo de abajo (paredes, mesa, sala)
      esfera.frustumCulled = false;
      this.rig.add(esfera);
      // 2) EL CARTEL a 2,00 m: tarjeta de intermedio de teatro
      const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true,
        depthTest: false, depthWrite: false, fog: false });
      const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1.92, 1.2), mat);
      mesh.renderOrder = 70;            // el texto SIEMPRE sobre la esfera
      const group = new THREE.Group();
      group.add(mesh);
      group.position.set(0, 1.6, -2.0);   // 2 m delante (el tick lo afina a la cabeza)
      this.rig.add(group);
      const S = { id, ttl, cols, group, mesh, mat, tex, cv, c, esfera, matEs,
        t: 0, rt0: null, listoDesde: null, espera: null, fade: -1,
        _v1: null, _v2: null, _q1: null };
      this.champCurtain = S;
      this._pintaCurtain(S, 0);
      return {
        cierra: () => { try { this.hideChampCurtain(); } catch (e1) { /* */ } },
        espera: (fn) => { S.espera = fn; },
      };
    } catch (e) { console.warn('[curtain] show', e); return null; }
  }

  /** r73 · color de la tarjeta por campeonato (fallback: oro de la casa). */
  _telonCols(id) {
    const M = {
      locura: ['#ff6b6b', '#ffd257'],
      magia: ['#b07cff', '#8a5cf6'],
      oeste: ['#e8a25e', '#c98a4b'],
      estacion_orbital: ['#7fd4e8', '#4c9fd6'],
      valle_neon: ['#ff6ad5', '#b07cff'],
    };
    return M[id] || ['#ffd257', '#e8b45a'];
  }

  /** Pinta la TARJETA DE INTERMEDIO: marco doble, «PRESENTA», título en el
   *  color del campeonato (autoajuste), «Montando el escenario...» con
   *  puntos y una bola que va y viene sobre la pista — redibujado barato. */
  _pintaCurtain(S, dots, rt) {
    try {
      const c = S.c, W = 1024, H = 640;
      const colA = (S.cols && S.cols[0]) || '#ffd257';
      const colB = (S.cols && S.cols[1]) || '#e8b45a';
      c.clearRect(0, 0, W, H);
      c.fillStyle = '#000000';
      c.fillRect(0, 0, W, H);
      // doble marco dorado (tarjeta de teatro)
      c.strokeStyle = colA; c.globalAlpha = 0.9; c.lineWidth = 5;
      if (c.roundRect) { c.beginPath(); c.roundRect(26, 26, W - 52, H - 52, 26); c.stroke(); }
      else c.strokeRect(26, 26, W - 52, H - 52);
      c.globalAlpha = 0.45; c.lineWidth = 2;
      if (c.roundRect) { c.beginPath(); c.roundRect(44, 44, W - 88, H - 88, 18); c.stroke(); }
      else c.strokeRect(44, 44, W - 88, H - 88);
      c.globalAlpha = 1;
      // «CRAZY PING PONG PRESENTA» con aire entre letras
      c.textAlign = 'center'; c.textBaseline = 'middle';
      c.fillStyle = 'rgba(238,242,245,0.62)';
      c.font = '700 27px system-ui, sans-serif';
      c.fillText(T('champ_telon_presenta').split('').join(' '), W / 2, 108);
      // título del campeonato en SU color (autoajuste, nunca cortado)
      const ttl = String(S.ttl || '').toUpperCase();
      let fs = 58;
      c.font = '900 ' + fs + 'px system-ui, sans-serif';
      while (fs > 26 && c.measureText(ttl).width > W - 200) {
        fs -= 2;
        c.font = '900 ' + fs + 'px system-ui, sans-serif';
      }
      c.fillStyle = colA;
      c.fillText(ttl, W / 2, H / 2 - 46);
      // «Montando el escenario...» con puntos animados
      c.fillStyle = '#eef2f5';
      c.font = '800 44px system-ui, sans-serif';
      const pts = '.'.repeat(dots % 4);
      c.fillText(T('champ_telon').replace(/\\.+$/, '') + pts, W / 2, H / 2 + 30);
      // la pista: línea fina con red central + BOLA que va y viene
      const ly = H - 128, half = 250;
      const k = (Math.sin((rt || S.t) * 2.1) + 1) / 2;   // 0..1 vaivén
      c.strokeStyle = 'rgba(255,255,255,0.22)'; c.lineWidth = 3;
      c.beginPath(); c.moveTo(W / 2 - half, ly); c.lineTo(W / 2 + half, ly); c.stroke();
      c.strokeStyle = 'rgba(255,255,255,0.4)'; c.lineWidth = 2;
      c.beginPath(); c.moveTo(W / 2, ly - 14); c.lineTo(W / 2, ly + 6); c.stroke();
      const bx = W / 2 - half + k * half * 2;
      const by = ly - 10 - Math.abs(Math.sin((rt || S.t) * 2.1)) * 34;
      c.fillStyle = '#ffffff';
      c.beginPath(); c.arc(bx, by, 9, 0, Math.PI * 2); c.fill();
      c.strokeStyle = colB; c.lineWidth = 2;
      c.beginPath(); c.arc(bx, by, 12.5, 0, Math.PI * 2); c.stroke();
      S.tex.needsUpdate = true;
    } catch (e) { /* decorativo */ }
  }

  _updateChampCurtain() {
    const S = this.champCurtain;
    if (!S) return;
    // r72 · el telón es INTERFAZ, no física: corre en TIEMPO REAL — una
    // carga a 20 fps no alarga la espera del dueño y el QA headless (1 fps
    // con SwiftShader) no se queda colgado 30 s por el cap de dt (1/30).
    const rt = (typeof performance !== 'undefined' ? performance.now() : Date.now()) / 1000;
    if (S.rt0 == null) { S.rt0 = rt; S.listoDesde = null; }
    S.t = rt - S.rt0;
    this._pintaCurtain(S, Math.floor(S.t * 2.6), rt);
    // r73 · SEGUIR A LA CABEZA: esfera centrada en el visor (nadie escapa
    // de la nada andando) y cartel a 2,00 m por donde se mire, de frente.
    try {
      if (!S._v1) {
        S._v1 = new THREE.Vector3(); S._v2 = new THREE.Vector3();
        S._q1 = new THREE.Quaternion();
      }
      S._v1.setFromMatrixPosition(this.camera.matrixWorld);       // cabeza (mundo)
      this.rig.worldToLocal(S._v1);                                // → espacio rig
      S.esfera.position.copy(S._v1);
      S._q1.setFromRotationMatrix(this.camera.matrixWorld);
      S._v2.set(0, 0, -1).applyQuaternion(S._q1); S._v2.y = 0;
      if (S._v2.lengthSq() < 1e-6) S._v2.set(0, 0, -1); else S._v2.normalize();
      const dy = Math.max(0.5, Math.min(2.6, S._v1.y));   // altura del ojo acotada
      S.group.position.set(S._v1.x + S._v2.x * 2.0, dy, S._v1.z + S._v2.z * 2.0);
      S.group.lookAt(S._v1.x, dy, S._v1.z);
    } catch (eF) { /* una cabeza tardía no tumba el telón */ }
    if (S.fade >= 0) {
      const k = Math.max(0, 1 - (rt - S.fade) / 0.42);
      S.mat.opacity = k;
      S.matEs.opacity = k;
      S.mesh.visible = k > 0.01;
      S.esfera.visible = k > 0.01;
      if (k <= 0.01) this.hideChampCurtain(true);
      return;
    }
    // ¿se levanta? mínimo 0,9 s de estancia + 0,3 s de check estable · tope 12 s
    if (S.t < 0.9) return;
    let listo = false;
    try { listo = S.espera ? !!S.espera() : true; } catch (e) { listo = true; }
    if (listo) {
      if (S.listoDesde == null) S.listoDesde = rt;
      if (rt - S.listoDesde >= 0.3 || S.t >= 12) S.fade = rt;
    } else {
      S.listoDesde = null;
      if (S.t >= 12) S.fade = rt;
    }
  }

  /** Cierra el telón: SIN argumento = fundido suave por el tick (la vía
   *  normal); con true = desmonte inmediato (limpieza/seguridad). */
  hideChampCurtain(inmediato) {
    const S = this.champCurtain;
    if (!S) return;
    if (!inmediato && S.fade < 0 && this.rig) {
      S.fade = (typeof performance !== 'undefined' ? performance.now() : Date.now()) / 1000;
      return;
    }
    this.champCurtain = null;
    try {
      if (S.group.parent) S.group.parent.remove(S.group);
      if (S.esfera && S.esfera.parent) S.esfera.parent.remove(S.esfera);
      try { S.tex.dispose(); } catch (e0) { /* */ }
      try { S.mat.dispose(); } catch (e1) { /* */ }
      try { S.mesh.geometry.dispose(); } catch (e2) { /* */ }
      try { S.matEs.dispose(); } catch (e3) { /* */ }
      try { S.esfera.geometry.dispose(); } catch (e4) { /* */ }
    } catch (e) { /* el telón NUNCA rompe */ }
  }

'''

out = src[:i0] + NUEVO + src[i1:]
io.open(P, 'w', encoding='utf-8').write(out)
print('OK — telón de teatro instalado,', len(NUEVO), 'caracteres')
