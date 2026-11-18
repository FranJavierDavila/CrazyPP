#!/usr/bin/env python3
"""r66 · Reemplaza el bloque del mando único r65 (const ANCLAS_MANDO … fin de
tickMando) por el sistema DUAL de mandos: dos GLB reales del dueño (izquierdo
Y/X + derecho B/A), halos OPACOS con etiqueta, raquetas fantasma y pose propia
(centro / saque / oculto). El bloque se delimita por los marcadores exactos.
Idempotente: sólo sustituye si encuentra el bloque r65."""
import re

C13 = "/home/z/my-project/src/game/core/c13_ui_arranque.js"
txt = open(C13, encoding="utf-8").read()

INI = "  /* ---------- MANDO GLB REAL del dueño (Touch Plus) · r65 -----------"
FIN = "  /* ---------------- pintura del panel (PIZARRA) · r65 ----------------"
i = txt.index(INI)
j = txt.index(FIN)

NUEVO = r'''  /* ---------- MANDOS GLB REALES del dueño (Touch Plus) · r66 ---------
   * «El mando que te he pasado corresponde con el izquierdo (botones Y y
   * X), así que te voy a pasar el derecho también (mando_derecho.glb, con
   * los botones B y A) para que pongas ambos en el tutorial. El mando
   * debería mostrarse delante en el centro en un punto de visión cómodo».
   * DOS modelos EXACTOS (izq Mando.glb · der mando_derecho.glb, meshes
   * fusionados) flotando CENTRADOS bajo la pizarra, con HALOS OPACOS por
   * pieza (anclas espejo verificadas por clustering geométrico) +
   * ETIQUETA de la pieza pedida + RAQUETA FANTASMA que aparece sobre
   * ellos («para asociar que el mando va a ser nuestra raqueta»).        */
  const ANCLAS_MANDO = {
    gatillo: [-0.0189, -0.021, 0.036],
    stick:   [0.0076, 0.0192, 0.0342],
    botones: [-0.004, 0.0162, 0.0219],
    grip:    [-0.0157, -0.0079, -0.0102],
  };
  /* El derecho es el ESPEJO geométrico del izquierdo (verificado por
   * clustering de vértices r66: cabeza X negada, mango simétrico). */
  const ANCLAS_MANDO_DER = {
    gatillo: [0.0189, -0.021, 0.036],
    stick:   [-0.0076, 0.0192, 0.0342],
    botones: [0.004, 0.0162, 0.0219],
    grip:    [0.0157, -0.0079, -0.0102],
  };
  function _haloTex() {
    const cvh = document.createElement('canvas');
    cvh.width = 64; cvh.height = 64;
    const g2 = cvh.getContext('2d');
    // r66 · núcleo OPACO (el dueño: «las zonas deben verse mejor, menos
    // transparentes y más fáciles de identificar»): disco blanco sólido
    // con borde ámbar grueso y halo corto.
    const rg = g2.createRadialGradient(32, 32, 1, 32, 32, 30);
    rg.addColorStop(0, 'rgba(255,255,255,1)');
    rg.addColorStop(0.42, 'rgba(255,214,90,0.98)');
    rg.addColorStop(0.72, 'rgba(255,180,40,0.55)');
    rg.addColorStop(1, 'rgba(255,180,40,0)');
    g2.fillStyle = rg;
    g2.fillRect(0, 0, 64, 64);
    const t = new THREE.CanvasTexture(cvh);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  /* etiqueta de la pieza pedida: píldora legible (fondo oscuro + borde
   * ámbar + texto blanco grande), billboard sobre el mando */
  function _etiquetaSprite() {
    const cvh = document.createElement('canvas');
    cvh.width = 512; cvh.height = 160;
    const t = new THREE.CanvasTexture(cvh);
    t.colorSpace = THREE.SRGBColorSpace;
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: t, transparent: true, opacity: 0, depthTest: false,
    }));
    sp.scale.set(0.30, 0.094, 1);
    sp.renderOrder = 996;
    sp.__cv = cvh;
    return sp;
  }
  function pintaEtiqueta(sp, txt) {
    if (!sp || sp.__txt === txt) return;
    sp.__txt = txt;
    const g2 = sp.__cv.getContext('2d');
    g2.clearRect(0, 0, 512, 160);
    g2.font = '800 58px system-ui, sans-serif';
    const w = Math.min(488, g2.measureText(txt).width + 56);
    g2.fillStyle = 'rgba(10,14,22,0.86)';
    g2.beginPath();
    if (g2.roundRect) g2.roundRect((512 - w) / 2, 26, w, 108, 34);
    else g2.rect((512 - w) / 2, 26, w, 108);
    g2.fill();
    g2.strokeStyle = 'rgba(255,210,87,0.95)';
    g2.lineWidth = 7;
    g2.stroke();
    g2.fillStyle = '#ffffff';
    g2.textAlign = 'center'; g2.textBaseline = 'middle';
    let s = 58;
    g2.font = '800 ' + s + 'px system-ui, sans-serif';
    while (s > 30 && g2.measureText(txt).width > w - 40) {
      s -= 2;
      g2.font = '800 ' + s + 'px system-ui, sans-serif';
    }
    g2.fillText(txt, 256, 82);
    sp.material.map.needsUpdate = true;
  }
  /* material FANTASMA para la raqueta (el dueño: «una raqueta con material
   * tipo fantasma para asociar que el mando va a ser nuestra raqueta») */
  function _fantasmaMats(grupo, coleccion) {
    grupo.traverse((o) => {
      if (!o.isMesh) return;
      const fant = new THREE.MeshBasicMaterial({
        color: 0x9fd8ff, transparent: true, opacity: 0,
        blending: THREE.AdditiveBlending, depthWrite: false,
        side: THREE.DoubleSide,
      });
      o.material = fant;
      o.castShadow = false;
      o.renderOrder = 992;
      coleccion.push(fant);
    });
  }
  function _montaMando(gltf, anclas, texHalo) {
    const modelo = gltf.scene;
    const box = new THREE.Box3().setFromObject(modelo);
    const cen = box.getCenter(new THREE.Vector3());
    const tam = box.getSize(new THREE.Vector3());
    const esc = 0.205 / Math.max(tam.x, tam.y, tam.z, 0.01);
    modelo.position.sub(cen);
    modelo.scale.setScalar(esc);
    modelo.traverse((o) => {
      if (o.isMesh) {
        const mats = Array.isArray(o.material) ? o.material : [o.material];
        for (const m of mats) {
          m.emissive = new THREE.Color('#ffd257');
          m.emissiveIntensity = 0;
          mandoMats.push(m);
        }
      }
    });
    const grupo = new THREE.Group();
    const tilt = new THREE.Group();
    tilt.rotation.set(-Math.PI / 2, 0, Math.PI);   // cabeza arriba, cara visible
    const spin = new THREE.Group();
    tilt.add(spin);
    spin.add(modelo);
    grupo.add(tilt);
    // halos OPACOS sobre las piezas (anclas espejo del derecho)
    const hs = {};
    for (const k in anclas) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: texHalo, color: 0xffd257, transparent: true,
        opacity: 0, depthTest: false, blending: THREE.AdditiveBlending,
      }));
      sp.position.fromArray(anclas[k]).multiplyScalar(esc * 1.12);
      sp.scale.setScalar(0.052);              // r66 · más GRANDE (era 0.03)
      sp.renderOrder = 990;
      spin.add(sp);
      hs[k] = sp;
    }
    return { grupo, spin, esc, halos: hs, fantasma: null };
  }
  function buildMandos() {
    if (mandosGrp || !G || !G.rig || typeof THREE === 'undefined' ||
        !GLTFLoader || !TUT_MANDO_GLB || !TUT_MANDO_DER_GLB) return;
    try {
      mandosGrp = new THREE.Group();
      mandosGrp.name = 'ppTutMandos';
      mandosGrp.position.set(0, 1.07, -0.56);
      mandosGrp.visible = false;
      G.rig.add(mandosGrp);
      const texHalo = _haloTex();
      etiqueta = _etiquetaSprite();
      etiqueta.position.set(0, 0.205, 0.02);
      mandosGrp.add(etiqueta);
      const binI = Uint8Array.from(atob(TUT_MANDO_GLB), (ch) => ch.charCodeAt(0));
      new GLTFLoader().parse(binI.buffer, '', (gltf) => {
        if (!mandosGrp) return;
        mandosI = _montaMando(gltf, ANCLAS_MANDO, texHalo);
        mandosI.grupo.position.x = -0.145;
        mandosI.grupo.rotation.y = 0.16;
        mandosGrp.add(mandosI.grupo);
        mando = mandosI.grupo;              // compat QA r65 (mando visible)
        mandoSpin = mandosI.spin;
        mandosI.grupo.name = 'ppTutMandoGLB';
        if (G.paddleModelRef) _ponFantasma(mandosI);
      }, () => { /* sin GLB: el panel funciona igual */ });
      const binD = Uint8Array.from(atob(TUT_MANDO_DER_GLB), (ch) => ch.charCodeAt(0));
      new GLTFLoader().parse(binD.buffer, '', (gltf) => {
        if (!mandosGrp) return;
        mandosD = _montaMando(gltf, ANCLAS_MANDO_DER, texHalo);
        mandosD.grupo.position.x = 0.145;
        mandosD.grupo.rotation.y = -0.16;
        mandosGrp.add(mandosD.grupo);
        if (G.paddleModelRef) _ponFantasma(mandosD);
      }, () => { /* sin GLB: el panel funciona igual */ });
    } catch (e) { /* nunca rompe el arranque de la academia */ }
  }
  /* RAQUETA FANTASMA sobre un mando: clon de la pala REAL del juego con
   * material aditivo translúcido, empuñadura en el cuerpo del mando */
  function _ponFantasma(mm) {
    try {
      if (!mm || mm.fantasma || !G.paddleModelRef || !makePaddleVisual) return;
      const f = makePaddleVisual(G.paddleModelRef, 'grip');
      const mats = [];
      _fantasmaMats(f, mats);
      f.position.set(0.004, -0.028, -0.008);
      f.rotation.set(-0.62, 0.10, 0.06);   // hoja arriba, abierta hacia el jugador
      mm.grupo.add(f);
      mm.fantasma = f;
      if (!fantasmaMats) fantasmaMats = [];
      fantasmaMats.push(...mats);
    } catch (e) { /* decorativo: sin fantasma todo sigue */ }
  }
  /* resalte por paso/subfase: ¿qué pieza menciona el guion ahora mismo? */
  function hlDePaso() {
    if (step === 1) {
      if (subfase >= 4) return null;   // momento RAQUETA: sin halo
      return ['gatillo', 'grip', 'stick', 'botones'][Math.min(subfase, 3)];
    }
    if (step === 5 && submodo === 'demo') return 'gatillo';
    return null;
  }
  function txtDeEtiqueta(parte) {
    if (!parte) return '';
    if (parte === 'botones') {
      return T('tut_lab_btns_i') + '  ·  ' + T('tut_lab_btns_d');
    }
    return T('tut_lab_' + parte) || '';
  }
  /* pose del grupo de mandos (r66): centro (pasos 0-2) · saque (demos sobre
   * la mesa, en coords de MESA convertidas al rig) · oculto (práctica) */
  function _poseMandos() {
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    if (mandosPose === 'saque') {
      return { x: 0.15, y: TY + 0.30, z: C + HL + 0.16, s: 1, giro: 0 };
    }
    if (mandosPose === 'oculto') {
      return { x: 0, y: -2.2, z: -0.5, s: 0.85, giro: 0 };
    }
    return { x: 0, y: 1.07, z: -0.56, s: 1, giro: 0 };   // centro
  }
  function tickMandos(dt) {
    if (!mandosGrp || !G || !G.rig) return;
    mandoT += dt;
    const p = _poseMandos();
    // coordenada de MESA (mundo) → local del rig (el jugador puede andar)
    G.rig.updateMatrixWorld(true);
    const destino = new THREE.Vector3(p.x, p.y, p.z);
    if (mandosPose === 'saque') destino.copy(G.rig.worldToLocal(destino));
    const k = 1 - Math.exp(-dt * 4.5);
    mandosGrp.position.x += (destino.x - mandosGrp.position.x) * k;
    mandosGrp.position.y += (destino.y - mandosGrp.position.y) * k;
    mandosGrp.position.z += (destino.z - mandosGrp.position.z) * k;
    const s = mandosGrp.scale.x + (p.s - mandosGrp.scale.x) * k;
    mandosGrp.scale.setScalar(s);
    mandosGrp.visible = mandosGrp.position.y > -1;
    // giro: sólo en exhibición; se DETIENE cuando la fantasma aparece
    const giroMeta = (fantasmaMeta > 0.02 || mandosPose !== 'centro') ? 0
      : (step === 1 ? 0.35 : 0.55);
    for (const mm of [mandosI, mandosD]) {
      if (!mm) continue;
      mm.__g = (mm.__g === undefined ? giroMeta : mm.__g + (giroMeta - mm.__g) * k);
      mm.spin.rotation.y += mm.__g * dt;
      mm.grupo.position.y = Math.sin(mandoT * 1.4 + (mm === mandosI ? 0 : 1.1)) * 0.008;
    }
    // fantasma: fade in/out con la opacidad objetivo
    fantasmaOp += (fantasmaMeta - fantasmaOp) * Math.min(1, dt * 3.2);
    if (fantasmaMats) {
      for (const m of fantasmaMats) {
        try { m.opacity = fantasmaOp * 0.42; } catch (e) { /* */ }
      }
    }
    // halos + etiqueta de la pieza pedida
    hlParte = hlDePaso();
    const pulso = 0.72 + 0.28 * Math.sin(mandoT * 5);
    for (const mm of [mandosI, mandosD]) {
      if (!mm) continue;
      for (const kk in mm.halos) {
        try {
          mm.halos[kk].material.opacity = (kk === hlParte) ? pulso : 0;
        } catch (e) { /* */ }
      }
    }
    if (etiqueta) {
      const t = txtDeEtiqueta(hlParte);
      if (t) {
        pintaEtiqueta(etiqueta, t);
        etiqueta.material.opacity = Math.min(1, etiqueta.material.opacity + dt * 6);
      } else {
        etiqueta.material.opacity = Math.max(0, etiqueta.material.opacity - dt * 6);
      }
    }
  }
  function bolaPalmDemo() {
    // posición de la bola en la palma del mando IZQUIERDO de la demo
    const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
    return new THREE.Vector3(0.06, TY + 0.415, C + HL + 0.24);
  }
  function puntoSaqueDemo() {
    return bolaPalmDemo();
  }

'''
txt = txt[:i] + NUEVO + txt[j:]
open(C13, "w", encoding="utf-8").write(txt)
print("bloque mandos r66 instalado:", len(txt), "bytes")
