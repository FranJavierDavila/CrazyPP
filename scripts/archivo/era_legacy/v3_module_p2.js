
  /* =================================================================
   *  ESTADO DE SESIÓN Y REFERENCIAS
   *  ================================================================= */
  let G = null;                    // instancia del juego (window.__PP_GAME)
  let grp = null;                  // grupo de escena del módulo
  let active = null;               // id del modo en curso (MODES key) o null
  let uiPage = 'hub';              // 'hub' | 'area'
  let uiArea = 'dir';
  let rainbowT = 0;

  const st = {
    streak: 0, goal: 0, sessPts: 0, rally: 0, bounces: 0,
    live: false, deadT: 0, wait: 0.8, phase: 'feed',
    cross: null, apex: 0, hitPos: null, bouncePos: null, lastBounce: null,
    target: null, toast: '', toastT: 0, feedT: 0, beat: 0, shotRec: false,
    shotPts: [], spinIconT: 0, spinIconCol: null, done: 0,
  };

  /* ---------------- constantes geométricas locales ---------------- */
  const C = () => DIMS.tableCenterZ;
  const TOP = () => DIMS.tableTopY;
  const HW = () => DIMS.tableHalfWidth;
  const HL = () => DIMS.tableHalfLength;
  const RIBBON_Y = () => DIMS.netTopY + 0.17;          // cinta a 17 cm sobre la red
  const APEX_Y = 1.50;                                  // aro del globo defensivo
  const CROSS_LOW = () => DIMS.netTopY + 0.055;         // pase bajo correcto
  const CROSS_HI = () => DIMS.netTopY + 0.16;           // demasiado alto

  /* =================================================================
   *  CONSTRUCCIÓN DE ESCENA (una sola vez, grupo propio)
   *  ================================================================= */
  function mkCanvas(w, h) {
    const cv = document.createElement('canvas');
    cv.width = w; cv.height = h;
    return cv;
  }
  function texOf(cv) {
    const tx = new THREE.CanvasTexture(cv);
    tx.colorSpace = THREE.SRGBColorSpace;
    tx.anisotropy = 4;
    return tx;
  }

  // --- plano de mesa (cuadrantes / bandas / zona de saque) ---
  let quadTex = null, quadMesh = null, quadCtx = null;
  function buildQuadPlane() {
    const cv = mkCanvas(512, 512);
    quadCtx = cv.getContext('2d');
    quadTex = texOf(cv);
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(HW() * 2, HL()),
      new THREE.MeshBasicMaterial({ map: quadTex, transparent: true, depthWrite: false, opacity: 0.94 }),
    );
    m.rotation.x = -Math.PI / 2;
    m.position.set(0, TOP() + 0.0045, C() - HL() / 2);
    m.renderOrder = 3;
    m.visible = false;
    return m;
  }

  // --- cinta sobre la red (pase bajo) ---
  function buildRibbon() {
    const g = new THREE.Group();
    const band = new THREE.Mesh(
      new THREE.BoxGeometry(1.86, 0.035, 0.012),
      new THREE.MeshBasicMaterial({ color: 0xff8a2a, transparent: true, opacity: 0.85 }),
    );
    band.position.y = RIBBON_Y();
    g.add(band);
    const glow = new THREE.Mesh(
      new THREE.BoxGeometry(1.86, 0.006, 0.016),
      new THREE.MeshBasicMaterial({ color: 0xffd27a, transparent: true, opacity: 0.95 }),
    );
    glow.position.y = RIBBON_Y() + 0.02;
    g.add(glow);
    g.position.set(0, 0, C());
    g.visible = false;
    return g;
  }

  // --- aro de altura (globo defensivo) ---
  function buildApexRing() {
    const g = new THREE.Group();
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.16, 0.012, 10, 40),
      new THREE.MeshBasicMaterial({ color: 0x53e0a8, transparent: true, opacity: 0.9 }),
    );
    ring.rotation.x = Math.PI / 2;
    g.add(ring);
    const beam = new THREE.Mesh(
      new THREE.CylinderGeometry(0.004, 0.004, APEX_Y - TOP(), 6),
      new THREE.MeshBasicMaterial({ color: 0x53e0a8, transparent: true, opacity: 0.28 }),
    );
    beam.position.y = -(APEX_Y - TOP()) / 2;
    g.add(beam);
    g.position.set(0, APEX_Y, C() + 0.5);
    g.visible = false;
    return g;
  }

  // --- aro-metrónomo en el suelo ---
  function buildMetroRing() {
    const m = new THREE.Mesh(
      new THREE.TorusGeometry(0.22, 0.012, 8, 40),
      new THREE.MeshBasicMaterial({ color: 0xf687b3, transparent: true, opacity: 0.85 }),
    );
    m.rotation.x = -Math.PI / 2;
    m.position.set(0, 0.012, C() + 1.32);
    m.visible = false;
    return m;
  }

  // --- marcas de bote (pool) ---
  const MARKS_N = 10;
  let marks = [], markIdx = 0;
  function buildMarks() {
    const out = [];
    for (let i = 0; i < MARKS_N; i++) {
      const m = new THREE.Mesh(
        new THREE.TorusGeometry(0.05, 0.006, 6, 26),
        new THREE.MeshBasicMaterial({ color: 0xffe08a, transparent: true, opacity: 0 }),
      );
      m.rotation.x = -Math.PI / 2;
      m.visible = false;
      m.userData.ttl = 0;
      out.push(m);
    }
    return out;
  }
  function spawnMark(p, col) {
    if (!S.fb.marks) return;
    const m = marks[markIdx]; markIdx = (markIdx + 1) % MARKS_N;
    m.position.set(p.x, TOP() + 0.006, p.z);
    m.material.color.setHex(col || 0xffe08a);
    m.material.opacity = 0.95;
    m.userData.ttl = 1.6;
    m.visible = true;
  }

  // --- línea de tiro (trayectoria REAL del último golpe) ---
  const SHOT_N = 96;
  let shotLine = null, shotGeo = null, shotTtl = 0;
  function buildShotLine() {
    shotGeo = new THREE.BufferGeometry();
    shotGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(SHOT_N * 3), 3));
    const m = new THREE.Line(shotGeo, new THREE.LineBasicMaterial({
      color: 0x7ae0ff, transparent: true, opacity: 0, depthWrite: false,
    }));
    m.renderOrder = 4;
    m.frustumCulled = false;
    return m;
  }
  function shotLineShow() {
    const n = Math.min(st.shotPts.length, SHOT_N);
    const arr = shotGeo.attributes.position.array;
    for (let i = 0; i < n; i++) {
      arr[i * 3] = st.shotPts[i].x;
      arr[i * 3 + 1] = st.shotPts[i].y;
      arr[i * 3 + 2] = st.shotPts[i].z;
    }
    shotGeo.setDrawRange(0, n);
    shotGeo.attributes.position.needsUpdate = true;
    shotLine.material.opacity = 0.85;
    shotTtl = 2.4;
    shotLine.visible = true;
  }

  // --- flecha de efecto sobre la bola ---
  let spinSprite = null;
  function buildSpinSprite() {
    const cv = mkCanvas(64, 64);
    const g2 = cv.getContext('2d');
    g2.strokeStyle = '#ffffff';
    g2.lineWidth = 7;
    g2.beginPath();
    g2.arc(32, 32, 20, 0.25, Math.PI * 1.45);
    g2.stroke();
    g2.fillStyle = '#ffffff';
    g2.beginPath();
    g2.moveTo(46, 6); g2.lineTo(58, 20); g2.lineTo(38, 24);
    g2.closePath(); g2.fill();
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: texOf(cv), transparent: true, opacity: 0, depthWrite: false,
    }));
    sp.scale.setScalar(0.085);
    sp.renderOrder = 6;
    return sp;
  }

  // --- panel flotante HUD del entrenamiento ---
  let ribbonG = null, apexG = null, metroG = null;
  let panel = null, panelCv = null, panelCtx = null, panelTex = null, panelDirty = true;
  function buildPanel() {
    panelCv = mkCanvas(768, 400);
    panelCtx = panelCv.getContext('2d');
    panelTex = texOf(panelCv);
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(1.32, 0.687),
      new THREE.MeshBasicMaterial({ map: panelTex, transparent: true, depthWrite: false }),
    );
    m.position.set(0, 1.60, C() - 1.95);
    m.rotation.x = -0.05;
    m.scale.setScalar(1.15);
    m.renderOrder = 5;
    m.visible = false;
    return m;
  }

  function rr2(g, x, y, w, h, r) {
    g.beginPath();
    g.moveTo(x + r, y);
    g.arcTo(x + w, y, x + w, y + h, r);
    g.arcTo(x + w, y + h, x, y + h, r);
    g.arcTo(x, y + h, x, y, r);
    g.arcTo(x, y, x + w, y, r);
    g.closePath();
  }

  function drawPanel() {
    const g = panelCtx, W = 768, H = 400;
    const M = active ? MODES[active] : null;
    g.clearRect(0, 0, W, H);
    // fondo
    const bg = g.createLinearGradient(0, 0, 0, H);
    bg.addColorStop(0, 'rgba(10,14,24,0.96)');
    bg.addColorStop(1, 'rgba(16,22,38,0.96)');
    rr2(g, 6, 6, W - 12, H - 12, 26);
    g.fillStyle = bg; g.fill();
    g.strokeStyle = 'rgba(240,200,90,0.85)'; g.lineWidth = 5; g.stroke();
    // cabecera
    g.textAlign = 'left'; g.textBaseline = 'middle';
    g.fillStyle = '#f0c85a';
    g.font = '800 44px system-ui, sans-serif';
    g.fillText(t('hub_t'), 34, 52);
    g.fillStyle = '#8fa0b8';
    g.font = '600 22px system-ui, sans-serif';
    g.fillText(M ? t(M.nk) : t('hub_s'), 34, 96);
    if (M) {
      // contador grande
      const big = active === 't5a' ? String(st.rally) : (String(st.streak) + ' / ' + M.n);
      g.textAlign = 'center';
      g.fillStyle = '#ffffff';
      g.font = '900 110px system-ui, sans-serif';
      g.fillText(big, W / 2, 216);
      g.fillStyle = '#8fa0b8';
      g.font = '700 26px system-ui, sans-serif';
      g.fillText(active === 't5a' ? t('hud_rally') : t('hud_racha') + ' · ' + t('hud_meta'), W / 2, 292);
      // toast
      if (st.toastT > 0) {
        g.fillStyle = st.toastOk ? '#68d391' : '#fc8181';
        g.font = '800 34px system-ui, sans-serif';
        g.fillText(st.toast, W / 2, 340);
      } else {
        g.fillStyle = '#a9b8cc';
        g.font = '600 24px system-ui, sans-serif';
        g.fillText(active === 't4a' || active === 't4b' ? t('sirve') : t('obj') + ': ' + M.n + ' ' + t('seg'), W / 2, 340);
      }
      // puntos
      g.textAlign = 'left';
      g.fillStyle = '#f0c85a';
      g.font = '800 30px system-ui, sans-serif';
      g.fillText('+' + st.sessPts, 34, H - 32);
      g.textAlign = 'right';
      g.fillStyle = '#8fa0b8';
      g.font = '600 24px system-ui, sans-serif';
      g.fillText(t('hud_total') + ' ' + S.pts, W - 34, H - 32);
    }
    panelTex.needsUpdate = true;
  }

  /* ---------------- montaje del grupo ---------------- */
  function buildScene() {
    if (grp || !G || !G.scene) return;
    grp = new THREE.Group();
    grp.name = 'ppTrainGrp';
    quadMesh = buildQuadPlane();
    grp.add(quadMesh);
    ribbonG = buildRibbon();
    grp.add(ribbonG);
    apexG = buildApexRing();
    grp.add(apexG);
    metroG = buildMetroRing();
    grp.add(metroG);
    marks = buildMarks();
    for (const m of marks) grp.add(m);
    shotLine = buildShotLine();
    grp.add(shotLine);
    spinSprite = buildSpinSprite();
    grp.add(spinSprite);
    panel = buildPanel();
    grp.add(panel);
    grp.visible = false;
    G.scene.add(grp);
  }
