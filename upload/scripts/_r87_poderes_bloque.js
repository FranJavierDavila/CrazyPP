/* -- 0 · POOL DE TEXTURAS DE MANO (r87 · anti-trompicones) ---------------
 * texture.clone() crea un RECURSO GPU nuevo: clonar por cada aparición de
 * mano subía 512×885 a la GPU en plena partida (el tirón que notaba el
 * dueño). Pool de 3 clones reciclados (máx. 3 manos vivas): la imagen se
 * re-asingna si el slot trae otra base — UNA subida por slot y sólo cuando
 * cambia de mano. __r86usada marca el slot ocupado. */
function _manoTexLibre(M, baseTex) {
  let t = M.pool.find((x) => x && !x.__r86usada && x.__r86src === baseTex);
  if (!t) t = M.pool.find((x) => x && !x.__r86usada);
  if (!t) {
    if (M.pool.length < 3) { t = baseTex.clone(); t.__r86src = baseTex; M.pool.push(t); }
    else { t = baseTex.clone(); t.__r86extra = true; }   // fuera de pool: muere con el poder
  }
  t.__r86usada = true;
  if (t.__r86src !== baseTex) { t.image = baseTex.image; t.__r86src = baseTex; t.needsUpdate = true; }
  return t;
}
function _manoTexSuelta(M, t) {
  if (!t) return;
  if (t.__r86extra) { try { t.dispose(); } catch (e) { /* */ } M.pool = M.pool.filter((x) => x !== t); }
  else t.__r86usada = false;
}

/* -- 1 · MANO DE ZOMBI (r87 · reescrita según el guion del dueño) --------
 * «en cualquier sitio de la mesa aparece la imagen monticulo.png OJO lo he
 * adjuntado (actualmente no se ve, pero debería aparecer sobre la mesa
 * antes de que aparezca la mano) desde la que sale aleatoriamente una de
 * las tres imágenes de manos zombis… movimiento rápido que se frena un
 * poco en el último momento (como para dar un susto), unos 3 segundos:
 * medio segundo para aparecer/desaparecer y 2 segundos arriba».
 *
 * CINE EXACTO: montículo plano sobre la mesa (0,32 s pop) → la mano
 * DESENROLLA desde el montículo (0,50 s, easeOutCubic + sobresalto 7 %)
 * → 2,00 s de vaivén siniestro → retracto (0,50 s) → montículo y mano se
 * funden JUNTOS (0,25 s). La bola que toca la mano queda PARADA y se cae;
 * la mano sale empujada y revienta en 6 trocitos (el montículo se hunde). */
const MANO_CULTIVO = 0.70;   // el 30 % inferior del arte del dueño es tierra
const MANO_OFF_Y = 0.30;     // recorte: la mano sale de NUESTRO montículo

PLANTILLA_PODERES.mano = {
  inicio(game, p, ctrl, ctx) {
    const M = { grupo: new THREE.Group(), vivos: [], trocitos: [], t: 0, prox: 0.35,
      tex: [], pool: [], texMonticulo: null, texTrozo: _texTerron() };
    [1, 2, 3].forEach((i) => TEX_R86.pedir('mano' + i + '.webp', (t) => { M.tex.push(t); }));
    TEX_R86.pedir('monticulo.webp', (t) => { M.texMonticulo = t; });
    game.scene.add(M.grupo);
    ctx.mano = M;                       // r87: ctx ANTES de los callbacks
  },
  _spawn(game, M) {
    const cz = DIMS.tableCenterZ;
    const x = rand(-0.56, 0.56);
    const z = clamp(cz + rand(-0.95, 0.85), cz - 1.30, cz + 1.10);
    const b = game.ball ? game.ball.pos : null;
    if (b && Math.abs(b.x - x) < 0.24 && Math.abs(b.z - z) < 0.24) return; // no nacer sobre la bola
    if (!M.tex.length || !M.texMonticulo) return;
    const baseTex = pick(M.tex);
    const tex = _manoTexLibre(M, baseTex);
    const W = 0.34, HF = W * (885 / 512);
    // MONTÍCULO plano sobre la mesa (aparece PRIMERO — guion del dueño)
    const mMat = new THREE.MeshBasicMaterial({ map: M.texMonticulo, transparent: true, depthWrite: false });
    const mont = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.46), mMat);
    mont.rotation.x = -Math.PI / 2;
    mont.rotation.z = rand(0, Math.PI * 2);
    mont.position.set(x, DIMS.tableTopY + 0.004 + Math.random() * 0.002, z);
    mont.renderOrder = 3;
    mont.scale.setScalar(0.01);
    M.grupo.add(mont);
    // MANO vertical anclada al centro del montículo (desenrollado)
    const tex2 = tex; tex2.wrapT = THREE.ClampToEdgeWrapping;
    tex2.offset.y = MANO_OFF_Y; tex2.repeat.y = 0.001;
    const geo = new THREE.PlaneGeometry(W, HF);
    geo.translate(0, HF / 2, 0);
    const mat = new THREE.MeshBasicMaterial({ map: tex2, transparent: true, alphaTest: 0.30, side: THREE.DoubleSide, depthWrite: false });
    const mano = new THREE.Mesh(geo, mat);
    mano.position.set(x, DIMS.tableTopY + 0.012, z);
    try {
      const cam = game.camera;
      _v86.setFromMatrixPosition(cam.matrixWorld);
      mano.rotation.y = Math.atan2(_v86.x - x, _v86.z - z);
    } catch (e) { mano.rotation.y = Math.atan2(-x, 0.55 - z); }
    mano.scale.y = 0.001;
    M.grupo.add(mano);
    M.vivos.push({ mont, mano, tex: tex2, W, HF, fase: 'monticulo', t: 0, golpeada: false, vx: 0, vz: 0, va: 0 });
  },
  _revienta(game, M, v, bola) {
    v.fase = 'golpeada'; v.t = 0;
    const dir = Math.atan2(v.mano.position.x - bola.x, v.mano.position.z - bola.z) || rand(0, 6.3);
    v.vx = Math.sin(dir) * rand(0.9, 1.5); v.vz = Math.cos(dir) * rand(0.9, 1.5);
    v.va = rand(-7, 7);
    for (let i = 0; i < 6; i++) {
      const geo = new THREE.PlaneGeometry(rand(0.04, 0.075), rand(0.04, 0.075));
      const mat = new THREE.MeshBasicMaterial({ map: M.texTrozo, transparent: true, alphaTest: 0.3, side: THREE.DoubleSide, depthWrite: false });
      const m = new THREE.Mesh(geo, mat);
      m.position.copy(v.mano.position).add(_v86.set(rand(-0.1, 0.1), v.mano.scale.y * v.HF * rand(0.3, 0.9), rand(-0.05, 0.05)));
      M.grupo.add(m);
      M.trocitos.push({ mesh: m, vx: rand(-0.8, 0.8), vy: rand(0.9, 1.8), vz: rand(-0.5, 0.5), va: rand(-9, 9), vida: 0.55, t: 0 });
    }
  },
  paso(dt, game, p, ctrl, ctx) {
    const M = ctx.mano; if (!M) return;
    M.t += dt;
    if (M.t >= M.prox && M.tex.length && M.texMonticulo && M.vivos.length < 3) {
      this._spawn(game, M);
      M.prox = M.t + rand(2.0, 2.5);
    }
    const bola = game.ball ? game.ball.pos : null;
    const r = DIMS.ballRadius;
    for (let i = M.vivos.length - 1; i >= 0; i--) {
      const v = M.vivos[i];
      v.t += dt;
      if (v.fase === 'monticulo') {
        // el montículo nace con un pop rápido (0,32 s) y queda latiendo
        const k = Math.min(1, v.t / 0.32);
        const e = 1 - Math.pow(1 - k, 3);
        v.mont.scale.setScalar(e * (1 + (k < 0.7 ? (1 - k / 0.7) * 0.18 : 0)));
        v.mont.material.opacity = Math.min(1, k * 1.6);
        if (k >= 1) { v.fase = 'subir'; v.t = 0; }
      } else if (v.fase === 'subir') {
        // rápida que se FRENA al final (susto) — guion del dueño: 0,5 s
        const k = Math.min(1, v.t / 0.5);
        const e = 1 - Math.pow(1 - k, 3);
        v.mano.scale.y = Math.max(0.001, e);
        const sobre = k < 0.24 ? (1 - k / 0.24) * 0.07 : 0;
        v.mano.scale.x = v.mano.scale.z = 1 + sobre;
        v.tex.repeat.y = Math.max(0.001, MANO_CULTIVO * e);
        if (k >= 1) { v.fase = 'arriba'; v.t = 0; }
      } else if (v.fase === 'arriba') {
        v.mano.rotation.z = Math.sin(v.t * 3.1) * 0.05;           // vaivén siniestro
        v.mano.scale.y = 1 + Math.sin(v.t * 4.7) * 0.015;
        if (v.t >= 2.0) { v.fase = 'bajar'; v.t = 0; v.mano.rotation.z = 0; }
      } else if (v.fase === 'bajar') {
        const k = Math.min(1, v.t / 0.5);
        v.mano.scale.y = Math.max(0.001, 1 - k * k);
        v.tex.repeat.y = Math.max(0.001, MANO_CULTIVO * (1 - k * k));
        if (k >= 1) { v.fase = 'fundir'; v.t = 0; }
      } else if (v.fase === 'fundir') {
        const op = Math.max(0, 1 - v.t / 0.25);
        v.mano.material.opacity = op;
        v.mont.material.opacity = op;
        v.mont.scale.setScalar(Math.max(0.01, op));
        if (v.t >= 0.25) {
          M.grupo.remove(v.mano); M.grupo.remove(v.mont);
          v.mano.geometry.dispose(); v.mano.material.dispose();
          v.mont.geometry.dispose(); v.mont.material.dispose();
          _manoTexSuelta(M, v.tex);
          M.vivos.splice(i, 1);
          continue;
        }
      } else if (v.fase === 'golpeada') {
        // mano empujada (tumba) + montículo hundido; trocitos por el aire
        v.mano.position.x += v.vx * dt; v.mano.position.z += v.vz * dt;
        v.mano.rotation.z += v.va * dt;
        const op = Math.max(0, 1 - v.t / 0.4);
        v.mano.material.opacity = op;
        v.mont.material.opacity = Math.max(0, op * 0.6 - 0.3);
        if (v.t >= 0.4) {
          M.grupo.remove(v.mano); M.grupo.remove(v.mont);
          v.mano.geometry.dispose(); v.mano.material.dispose();
          v.mont.geometry.dispose(); v.mont.material.dispose();
          _manoTexSuelta(M, v.tex);
          M.vivos.splice(i, 1);
          continue;
        }
      }
      // la bola choca contra la mano: PARADA y se cae (guion del dueño)
      if (bola && !v.golpeada && (v.fase === 'subir' || v.fase === 'arriba') && v.mano.scale.y > 0.6) {
        const dx = bola.x - v.mano.position.x;
        const dy = bola.y - (v.mano.position.y + v.mano.scale.y * v.HF * 0.55);
        const dz = bola.z - v.mano.position.z;
        if (Math.abs(dx) < 0.19 + r && Math.abs(dy) < v.mano.scale.y * v.HF * 0.48 + r && Math.abs(dz) < 0.10 + r) {
          v.golpeada = true;
          bola.vel.set(rand(-0.25, 0.25), 0.05, rand(-0.25, 0.25));   // parada y se cae
          try { game.audio.paddle(clamp(bola.x / 2.5, -1, 1), 0.4); } catch (e) { /* */ }
          ctrl.fxPop(v.mano.position);
          this._revienta(game, M, v, bola);
        }
      }
    }
    for (let i = M.trocitos.length - 1; i >= 0; i--) {
      const tr = M.trocitos[i];
      tr.t += dt;
      tr.vy -= 5.5 * dt;
      tr.mesh.position.x += tr.vx * dt; tr.mesh.position.y += tr.vy * dt; tr.mesh.position.z += tr.vz * dt;
      tr.mesh.rotation.z += tr.va * dt;
      tr.mesh.material.opacity = Math.max(0, 1 - tr.t / tr.vida);
      if (tr.t >= tr.vida) {
        M.grupo.remove(tr.mesh); tr.mesh.geometry.dispose(); tr.mesh.material.dispose();
        M.trocitos.splice(i, 1);
      }
    }
  },
  fin(game, p, ctrl, ctx) {
    const M = ctx && ctx.mano; if (!M) return;
    M.vivos.forEach((v) => {
      try { v.mano.geometry.dispose(); v.mano.material.dispose(); } catch (e) { /* */ }
      try { v.mont.geometry.dispose(); v.mont.material.dispose(); } catch (e) { /* */ }
      _manoTexSuelta(M, v.tex);
    });
    M.trocitos.forEach((tr) => { tr.mesh.geometry.dispose(); tr.mesh.material.dispose(); });
    M.pool.forEach((t) => { try { t.dispose(); } catch (e) { /* */ } });
    game.scene.remove(M.grupo);
    ctx.mano = null;
  },
};

/* -- 2 · PLAGA DE MOSCAS (r87 · «más trabajadas, aleteo, zumbido, más
 * cantidad y calidad» — informe del dueño) -------------------------------
 * 24 moscas de 2 FRAMES de aleteo (mosca_a/mosca_b, alternancia ~22 Hz con
 * fase propia), órbitas elípticas con deriva y dardos ocasionales, ZUMBIDO
 * de enjambre en bucle (createBucle + fly_buzz.mp3) y espantado con la
 * pala (proximidad real del mando) — igual que confetti de Clown, pero
 * vivo. */
PLANTILLA_PODERES.moscas = {
  inicio(game, p, ctrl, ctx) {
    const S = { grupo: new THREE.Group(), moscas: [], t: 0, texA: null, texB: null, bucle: null };
    S.grupo.position.set(0, -0.045, -0.44);
    try { game.camera.add(S.grupo); } catch (e) { game.scene.add(S.grupo); }
    ctx.moscas = S;                     // r87: ctx ANTES de los callbacks
    const nace = () => {
      if (!S.texA || !S.texB || S.moscas.length) return;
      for (let i = 0; i < 24; i++) {
        const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: S.texA, transparent: true, depthWrite: false }));
        const esc = rand(0.026, 0.055);
        s.scale.set(esc, esc * 0.82, 1);
        s.userData.r87 = {
          radio: rand(0.07, 0.26), fase: rand(0, 6.3),
          vel: rand(0.8, 1.9) * (Math.random() < 0.5 ? 1 : -1),
          bob: rand(0.25, 0.7), aleteo: rand(0, 6.3), aleteoV: rand(17, 26),
          dart: rand(1.5, 4.0), dartT: 0, cx: 0, cy: 0, cz: 0,
          muerta: 0, fx: 0, fy: 0,
        };
        S.grupo.add(s);
        S.moscas.push(s);
      }
    };
    TEX_R86.pedir('mosca_a.webp', (t) => { S.texA = t; nace(); });
    TEX_R86.pedir('mosca_b.webp', (t) => { S.texB = t; nace(); });
    // ZUMBIDO del enjambre (bucle del SDK, perfil de audio probado)
    try {
      S.bucle = createBucle(() => game, { url: () => A('fly_buzz.mp3'), vol: () => 0.34, fadeIn: 0.15, stopFade: 0.3 });
      S.bucle.on();
    } catch (e) { S.bucle = null; }
  },
  paso(dt, game, p, ctrl, ctx) {
    const S = ctx.moscas; if (!S) return;
    S.t += dt;
    const pad = game.controllerPaddles ? game.controllerPaddles[(game.paddleHand | 0) || 0] : null;
    for (let i = S.moscas.length - 1; i >= 0; i--) {
      const s = S.moscas[i];
      const u = s.userData.r87;
      if (u.muerta > 0) {
        u.muerta -= dt;
        s.position.x += u.fx * dt; s.position.y += u.fy * dt;
        s.material.opacity = Math.max(0, u.muerta / 0.35);
        if (u.muerta <= 0) { S.grupo.remove(s); s.material.dispose(); S.moscas.splice(i, 1); }
        continue;
      }
      // ALETEO: 2 frames alternando con fase propia (~20 Hz, se ve vivo)
      u.aleteo += dt * u.aleteoV;
      const frame = (Math.floor(u.aleteo) & 1) ? S.texB : S.texA;
      if (s.material.map !== frame) { s.material.map = frame; s.material.needsUpdate = true; }
      // DARDOS: cada 1,5-4 s la mosca re-centra su órbita (enjambre vivo)
      u.dartT += dt;
      if (u.dartT >= u.dart) {
        u.dartT = 0; u.dart = rand(1.5, 4.0);
        u.cx = rand(-0.05, 0.05); u.cy = rand(-0.03, 0.04); u.cz = rand(-0.04, 0.04);
      }
      const a = u.fase + S.t * u.vel;
      s.position.x = u.cx + Math.cos(a) * u.radio;
      s.position.y = u.cy + Math.sin(a * 1.6) * 0.05 + Math.sin(S.t * u.bob + u.fase) * 0.035;
      s.position.z = u.cz + Math.sin(a) * u.radio * 0.55;
      if (pad && pad.pos) {
        s.getWorldPosition(_v86);
        if (_v86.distanceTo(pad.pos) < 0.16) {          // ¡espantada con la pala!
          u.muerta = 0.35;
          const inv = 1 / (Math.hypot(s.position.x, s.position.z) || 1);
          u.fx = s.position.x * inv * rand(1.2, 2.4);
          u.fy = rand(0.4, 1.0);
          ctrl.fxPop(_v86);
          try { game.audio.playOsc(520 + Math.random() * 260, 180, 0.06, 'sawtooth', 0.05, 0); } catch (e) { /* */ }
        }
      }
    }
  },
  fin(game, p, ctrl, ctx) {
    const S = ctx && ctx.moscas; if (!S) return;
    if (S.bucle) { try { S.bucle.off(); } catch (e) { /* */ } S.bucle = null; }
    S.moscas.forEach((s) => s.material.dispose());
    try { game.camera.remove(S.grupo); } catch (e) { /* */ }
    try { game.scene.remove(S.grupo); } catch (e) { /* */ }
    ctx.moscas = null;
  },
};

/* -- 3 · CALABAZA (r87 · arreglo del fallo del dueño: «NO SE VE POR
 * NINGÚN LADO, Y LA BOLA DESAPARECE») -----------------------------------
 * CAUSA: la precarga del constructor terminaba ANTES del disparo → el
 * callback de _pumpkinGet era SÍNCRONO y corría ANTES de ctx.calabaza = C
 * → el guard lo saltaba: bola oculta y calabaza nunca añadida.
 * ARREGLO: ctx primero, callback después; y la bola JAMÁS se queda sin
 * cuerpo: si el GLB tarda >2,5 s hay calabaza PROCEDURAL de respaldo. */
function _calabazaProcedural() {
  if (TEX_R86.cache.__calProc) return TEX_R86.cache.__calProc;
  const cv = document.createElement('canvas'); cv.width = 128; cv.height = 128;
  const g = cv.getContext('2d');
  g.fillStyle = '#e8720c'; g.fillRect(0, 0, 128, 128);
  for (let i = 0; i < 8; i++) {
    g.fillStyle = i % 2 ? '#c25e06' : '#f08a1d';
    g.fillRect(i * 16 + 4, 0, 9, 128);
  }
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  const grp = new THREE.Group();
  const cuerpo = new THREE.Mesh(
    new THREE.SphereGeometry(0.062, 20, 16),
    new THREE.MeshStandardMaterial({ map: tex, roughness: 0.7 }),
  );
  cuerpo.scale.y = 0.82;
  const rabo = new THREE.Mesh(
    new THREE.CylinderGeometry(0.008, 0.012, 0.035, 8),
    new THREE.MeshStandardMaterial({ color: 0x3f6b23, roughness: 0.9 }),
  );
  rabo.position.y = 0.062;
  grp.add(cuerpo); grp.add(rabo);
  TEX_R86.cache.__calProc = grp;
  return grp;
}

PLANTILLA_PODERES.calabaza = {
  inicio(game, p, ctrl, ctx) {
    const C = { gltf: null, grav0: DIMS.gravity, prevVelY: 0, prevY: 1, spin: 0, listo: false };
    ctx.calabaza = C;                   // r87: ANTES del callback (era el bug)
    DIMS.gravity = C.grav0 * 2.1;       // más pesada
    _pumpkinGet((sc) => {
      if (!ctx.calabaza || C.listo) return;
      C.listo = true;
      C.gltf = sc.clone(true);
      game.scene.add(C.gltf);
      if (game.ballMesh) game.ballMesh.visible = false;   // la bola la sustituye EL CUERPO
    });
    C.fallbackT = 2.5;                  // si el GLB no llega: calabaza de la casa
  },
  paso(dt, game, p, ctrl, ctx) {
    const C = ctx.calabaza; if (!C) return;
    // r87 · respaldo: el GLB tarda o falló → calabaza procedural (la bola
    // NUNCA invisible — el fallo exacto que veía el dueño)
    if (!C.listo && C.fallbackT > 0) {
      C.fallbackT -= dt;
      if (C.fallbackT <= 0) {
        C.listo = true;
        C.gltf = _calabazaProcedural().clone(true);
        game.scene.add(C.gltf);
        if (game.ballMesh) game.ballMesh.visible = false;
      }
    }
    const b = game.ball; if (!b) return;
    // bote en la mesa → la salida puede ir en CUALQUIER dirección (caos del dueño)
    const enMesa = Math.abs(b.pos.x) <= DIMS.tableHalfWidth + 0.03 &&
      Math.abs(b.pos.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength + 0.03;
    if (enMesa && C.prevVelY < -0.5 && b.vel.y > 0.5) {
      const hs = Math.hypot(b.vel.x, b.vel.z) * rand(0.75, 1.05);
      const th = rand(0, Math.PI * 2);
      b.vel.x = Math.sin(th) * hs;
      b.vel.z = Math.cos(th) * hs;
      b.vel.y = Math.max(b.vel.y, rand(1.2, 2.4));
    }
    C.prevVelY = b.vel.y; C.prevY = b.pos.y;
    if (C.gltf) {
      C.gltf.position.set(b.pos.x, b.pos.y + 0.035, b.pos.z);
      C.spin += dt * (2.2 + Math.hypot(b.vel.x, b.vel.z) * 0.6);
      C.gltf.rotation.y = C.spin;
      C.gltf.rotation.x = clamp(-b.vel.z * 0.05, -0.45, 0.45);
    }
  },
  fin(game, p, ctrl, ctx) {
    const C = ctx && ctx.calabaza; if (!C) return;
    DIMS.gravity = C.grav0;
    if (game.ballMesh) game.ballMesh.visible = true;
    if (C.gltf && !TEX_R86.cache.__calProc || (C.gltf && C.gltf !== TEX_R86.cache.__calProc)) {
      // sólo se dispone lo CLONADO del GLB; el procedural es cache de la casa
      const esProc = C.gltf.type === 'Group' && !C.gltf.isGLTF;
      game.scene.remove(C.gltf);
      if (!esProc) {
        C.gltf.traverse((o) => {
          if (o.isMesh) { if (o.geometry) o.geometry.dispose(); if (o.material) { const ms = Array.isArray(o.material) ? o.material : [o.material]; ms.forEach((mm) => mm.dispose()); } }
        });
      }
    } else if (C.gltf) {
      game.scene.remove(C.gltf);
    }
    ctx.calabaza = null;
  },
};

/* -- 4 · GELATINA ASQUEROSA (r87 · arreglo ctx-timing + guion del dueño)
 * «aparecerán unas manchas sobre la mesa de forma aleatoria… COLOCAR
 * ALEATORIAMENTE UN POCO POR ENCIMA DE LA MESA»: 5 manchas del dueño que
 * FLOTAN un pelín sobre la losa (y +0,006…+0,012, sin z-fighting), la bola
 * que las toca se pone VERDE FOSFORITO y pesa POR LO MENOS 3 VECES más
 * (gravedad ×3 + frenado), soltando humillo verde que se desvanece. */
PLANTILLA_PODERES.gelatina = {
  inicio(game, p, ctrl, ctx) {
    const G = { manchas: [], humo: [], t: 0, humoT: 0, contaminada: false, grav0: null, col0: 0, emis0: 0 };
    ctx.gelatina = G;                   // r87: ANTES del callback (era el bug)
    TEX_R86.pedir('gelatina.webp', (t) => {
      if (!ctx.gelatina || G.manchas.length) return;
      const cz = DIMS.tableCenterZ;
      for (let i = 0; i < 5; i++) {
        const tam = rand(0.26, 0.38);
        const geo = new THREE.PlaneGeometry(tam, tam);
        const mat = new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity: 0.94, depthWrite: false });
        const m = new THREE.Mesh(geo, mat);
        m.rotation.x = -Math.PI / 2;
        m.rotation.z = rand(0, Math.PI * 2);
        // UN POCO POR ENCIMA DE LA MESA (guion del dueño) — escalonado
        m.position.set(rand(-0.55, 0.55), DIMS.tableTopY + 0.006 + i * 0.0012, cz + rand(-1.0, 0.9));
        game.scene.add(m);
        G.manchas.push(m);
      }
    });
  },
  paso(dt, game, p, ctrl, ctx) {
    const G = ctx.gelatina; if (!G) return;
    G.t += dt;
    // respiración sutil de las manchas (vivas, pegajosas)
    for (let i = 0; i < G.manchas.length; i++) {
      G.manchas[i].material.opacity = 0.90 + Math.sin(G.t * 2.4 + i * 1.7) * 0.06;
    }
    const b = game.ball; const r = DIMS.ballRadius;
    if (!G.contaminada && b && b.pos.y - r <= DIMS.tableTopY + 0.045) {
      for (const m of G.manchas) {
        const dx = b.pos.x - m.position.x;
        const dz = b.pos.z - m.position.z;
        if (dx * dx + dz * dz < 0.11 * 0.11) {
          G.contaminada = true;
          G.grav0 = DIMS.gravity; DIMS.gravity = G.grav0 * 3.0;   // ≥3 VECES más pesada
          const mesh = game.ballMesh;
          if (mesh && mesh.material) {
            G.col0 = mesh.material.color.getHex();
            G.emis0 = mesh.material.emissive ? mesh.material.emissive.getHex() : 0;
            mesh.material.color.setHex(0x39ff14);                  // verde fosforito
            if (mesh.material.emissive) mesh.material.emissive.setHex(0x1f8f0a);
          }
          ctrl.fxPop(b.pos);
          break;
        }
      }
    }
    if (G.contaminada && b) {
      // necesita más fuerza para avanzar: la gelatina frena la bola
      b.vel.x *= (1 - 0.35 * dt);
      b.vel.z *= (1 - 0.35 * dt);
      // humillo verde fosforito que se desvanece
      G.humoT -= dt;
      if (G.humoT <= 0) {
        G.humoT = 0.075;
        const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: _texHumo(), transparent: true, opacity: 0.62, depthWrite: false }));
        s.position.set(b.pos.x + rand(-0.01, 0.01), b.pos.y + 0.02, b.pos.z + rand(-0.01, 0.01));
        s.scale.set(0.05, 0.05, 1);
        game.scene.add(s);
        G.humo.push({ s, vida: 0.55, t: 0, vy: rand(0.16, 0.24) });
      }
    }
    for (let i = G.humo.length - 1; i >= 0; i--) {
      const h = G.humo[i];
      h.t += dt;
      h.s.position.y += h.vy * dt;
      const k = h.t / h.vida;
      h.s.scale.setScalar(0.05 + k * 0.09);
      h.s.material.opacity = Math.max(0, 0.62 * (1 - k));
      if (h.t >= h.vida) { game.scene.remove(h.s); h.s.material.dispose(); G.humo.splice(i, 1); }
    }
  },
  fin(game, p, ctrl, ctx) {
    const G = ctx && ctx.gelatina; if (!G) return;
    if (G.contaminada && G.grav0 != null) DIMS.gravity = G.grav0;
    const mesh = game.ballMesh;
    if (mesh && mesh.material && G.col0) {
      mesh.material.color.setHex(G.col0);
      if (mesh.material.emissive) mesh.material.emissive.setHex(G.emis0);
    }
    G.manchas.forEach((m) => { game.scene.remove(m); m.geometry.dispose(); m.material.dispose(); });
    G.humo.forEach((h) => { game.scene.remove(h.s); h.s.material.dispose(); });
    ctx.gelatina = null;
  },
};

