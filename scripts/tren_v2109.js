/* ============================================================================
 *  v2.109 · ETAPA 4 — «ASALTO AL TREN» · EL VAGÓN DE MERCANCÍAS (interior).
 *  ---------------------------------------------------------------------
 *  La escena SE CIERRA sobre el jugador: la mesa viaja DENTRO de un vagón
 *  de mercancías (suelo, techo, frontal con cajas pintadas, trasera con
 *  puerta — arte del artista en assets/room/vagon/). Las paredes laterales
 *  traen VENTANAS con marco de hierro (recorte ALFA medido píxel a píxel
 *  sobre el arte) y fuera de ellas corre el desierto en 4 PLANOS de
 *  PARALLAX (regla del artista, multiplicadores sobre el plano cercano):
 *    P1 montañas 0,05× · P2 colinas/estructuras 0,15× ·
 *    P3 postes/terreno 0,40× · P4 arbustos/rocas 1,00×
 *  Las ventanas son la ÚNICA referencia visual de movimiento: dentro del
 *  vagón no tiembla nada. El trayecto son 3 PARADAS de 2 minutos máximo:
 *  el tren nace DETENIDO en la estación 1, silba y arranca; cada parada
 *  trae su OLEADA de cajas fuertes (repisas → raíles → compuertas); al
 *  completarla el tren FRENA hasta el andén siguiente, espera y vuelve a
 *  arrancar. El SILBATO anuncia TÚNELES: las ventanas se apagan y sólo
 *  brillan los candados. Arte por planos: si existen
 *  assets/parallax/plano1..4.png se usan; si no, siluetas procedurales.
 *  ============================================================================ */
class TrenAction {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.phase = 'idle';      // intro|run|arrive|stop|win|fail
    this.t = 0;
    this.done = false;
    this.wave = 1;            // parada actual 1..3
    this.opened = 0;          // candados abiertos en la parada
    this.waveTotal = 0;
    this.time = TREN.time;    // reloj DE LA PARADA (2:00)
    this.v = 0;               // velocidad del tren (m/s)
    this.W = 0;               // distancia recorrida (m, mundo)
    this.meetW = 0;           // W del próximo andén (freno hasta aquí)
    this.stationW = 0;        // W del andén COLOCADO en la escena
    this._stoppedT = 0;
    this._tunnelT = TREN.tunnelFirst;
    this._tunnelPhase = 'none';  // none|in|dur|out
    this._tunnelT2 = 0;
    this._resultT = 0;
    this._wavePause = 0;
    this._respawnT = 0;
    this._dead = false;
    this._floorB = 0;
    this._msg = '';
    this._msgT = 0;
    this._extra = (ball) => this._collide(ball);
  }

  /* ------------------------------ texturas -------------------------------- */
  _ct(cv) {
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  _anisoOf() {
    try { return Math.min(8, this.game.renderer.capabilities.getMaxAnisotropy()); }
    catch (e) { return 4; }
  }
  /* CIELO del desierto (degradado cálido + nubes largas). */
  _texSky() {
    const cv = oesteCanvas(512, 256);
    const c = cv.getContext('2d');
    const gr = c.createLinearGradient(0, 0, 0, 256);
    gr.addColorStop(0, '#6fa7d6'); gr.addColorStop(0.55, '#a8c8dd');
    gr.addColorStop(0.8, '#ecd9ae'); gr.addColorStop(1, '#f2d9a8');
    c.fillStyle = gr; c.fillRect(0, 0, 512, 256);
    for (const [x, y, w, a] of [[70, 60, 150, 0.16], [300, 90, 190, 0.13],
      [180, 130, 210, 0.10], [430, 50, 120, 0.14]]) {
      const rg = c.createRadialGradient(x, y, 4, x, y, w / 2);
      rg.addColorStop(0, 'rgba(255,250,240,' + a + ')');
      rg.addColorStop(1, 'rgba(255,250,240,0)');
      c.fillStyle = rg;
      c.beginPath(); c.ellipse(x, y, w / 2, w / 7, 0, 0, Math.PI * 2); c.fill();
    }
    return this._ct(cv);
  }
  /* Los 4 PLANOS del artista (reserva procedural hasta que llegue
   * parallax/plano1..4.png). Lienzo 1024x256: el HORIZONTE del plano k se
   * dibuja donde dicta su geometría (ver _layerCfg). */
  _layerCanvas(k) {
    const cv = oesteCanvas(1024, 256);
    const c = cv.getContext('2d');
    if (k === 0) {
      /* P1 · MONTAÑAS: mesetas violáceas con bruma (horizonte y≈128). */
      const mesa = (x0, w, h, a) => {
        c.fillStyle = 'rgba(122,104,142,' + a + ')';
        c.beginPath();
        c.moveTo(x0, 128); c.lineTo(x0 + w * 0.16, 128 - h);
        c.lineTo(x0 + w * 0.84, 128 - h); c.lineTo(x0 + w, 128);
        c.closePath(); c.fill();
      };
      mesa(10, 200, 92, 0.50); mesa(235, 140, 62, 0.40);
      mesa(400, 240, 104, 0.52); mesa(665, 165, 74, 0.42);
      mesa(850, 150, 56, 0.38);
      c.fillStyle = 'rgba(122,104,142,0.26)';
      for (let i = 0; i < 6; i++) {
        const x = i * 180 + 60, w = 110 + (i % 3) * 46;
        c.beginPath(); c.moveTo(x, 128); c.lineTo(x + w / 2, 92);
        c.lineTo(x + w, 128); c.closePath(); c.fill();
      }
      const gr = c.createLinearGradient(0, 122, 0, 256);
      gr.addColorStop(0, 'rgba(205,188,205,0)');
      gr.addColorStop(0.45, 'rgba(205,188,205,0.85)');
      gr.addColorStop(1, 'rgba(210,196,206,1)');
      c.fillStyle = gr; c.fillRect(0, 122, 1024, 134);
    } else if (k === 1) {
      /* P2 · COLINAS Y ESTRUCTURAS (granero, molino, depósito). */
      c.fillStyle = 'rgba(158,124,84,0.92)';
      c.beginPath(); c.moveTo(0, 150);
      for (let x = 0; x <= 1024; x += 64) {
        c.lineTo(x, 142 + Math.sin(x * 0.011) * 16 + Math.sin(x * 0.033) * 8);
      }
      c.lineTo(1024, 150); c.lineTo(1024, 256); c.lineTo(0, 256);
      c.closePath(); c.fill();
      c.fillStyle = 'rgba(140,108,72,0.85)';
      c.beginPath(); c.moveTo(0, 176);
      for (let x = 0; x <= 1024; x += 48) {
        c.lineTo(x, 168 + Math.sin(x * 0.017 + 2) * 12);
      }
      c.lineTo(1024, 176); c.lineTo(1024, 256); c.lineTo(0, 256);
      c.closePath(); c.fill();
      // granero
      c.fillStyle = 'rgba(96,66,40,0.9)';
      c.fillRect(252, 118, 66, 34);
      c.beginPath(); c.moveTo(246, 118); c.lineTo(285, 96); c.lineTo(324, 118);
      c.closePath(); c.fill();
      // molino de viento
      c.strokeStyle = 'rgba(96,66,40,0.9)'; c.lineWidth = 4;
      c.beginPath(); c.moveTo(560, 152); c.lineTo(572, 84); c.stroke();
      const wx = 572, wy = 84;
      for (let b = 0; b < 4; b++) {
        const a = b * Math.PI / 2 + 0.4;
        c.beginPath(); c.moveTo(wx, wy);
        c.lineTo(wx + Math.cos(a) * 26, wy + Math.sin(a) * 26); c.stroke();
      }
      // depósito de agua
      c.fillStyle = 'rgba(96,66,40,0.9)';
      c.fillRect(818, 100, 40, 26);
      c.beginPath(); c.moveTo(812, 100); c.lineTo(864, 100);
      c.lineTo(838, 84); c.closePath(); c.fill();
      c.fillRect(824, 126, 5, 28); c.fillRect(847, 126, 5, 28);
      const gr = c.createLinearGradient(0, 150, 0, 256);
      gr.addColorStop(0, 'rgba(176,140,96,0)');
      gr.addColorStop(0.5, 'rgba(176,140,96,0.9)');
      gr.addColorStop(1, 'rgba(184,148,102,1)');
      c.fillStyle = gr; c.fillRect(0, 150, 1024, 106);
    } else if (k === 2) {
      /* P3 · POSTES Y TERRENO: llano arenoso con línea de telégrafo. */
      const gr = c.createLinearGradient(0, 150, 0, 256);
      gr.addColorStop(0, '#d8b984'); gr.addColorStop(1, '#c9a06a');
      c.fillStyle = gr; c.fillRect(0, 150, 1024, 106);
      c.fillStyle = 'rgba(120,90,50,0.18)';
      for (let i = 0; i < 60; i++) {
        c.beginPath();
        c.ellipse(Math.random() * 1024, 165 + Math.random() * 85,
          3 + Math.random() * 8, 1.5 + Math.random() * 3, 0, 0, Math.PI * 2);
        c.fill();
      }
      // postes + hilos
      c.strokeStyle = 'rgba(92,66,38,0.95)';
      c.fillStyle = 'rgba(92,66,38,0.95)';
      const px0 = 60, paso = 146, py = 168;
      for (let i = 0; i < 8; i++) {
        const x = px0 + i * paso;
        c.fillRect(x - 3, 84, 6, py - 84);
        c.fillRect(x - 16, 92, 32, 5);
        c.fillRect(x - 12, 104, 24, 4);
      }
      c.lineWidth = 1.6; c.strokeStyle = 'rgba(70,52,30,0.8)';
      c.beginPath();
      for (let i = 0; i < 8; i++) {
        const x = px0 + i * paso;
        if (i === 0) c.moveTo(x, 96);
        else c.lineTo(x, 96);
      }
      c.moveTo(px0, 108);
      for (let i = 0; i < 8; i++) c.lineTo(px0 + i * paso, 108);
      c.stroke();
      // cactus pequeños
      c.fillStyle = 'rgba(122,132,76,0.9)';
      for (const [x, h] of [[210, 22], [672, 18], [940, 24]]) {
        c.fillRect(x - 3, py - h, 6, h);
        c.fillRect(x - 10, py - h + 6, 7, 4);
        c.fillRect(x - 10, py - h + 6, 4, 12);
      }
    } else {
      /* P4 · ARBUSTOS Y ROCAS: terreno cercano con vegetación. */
      const gr = c.createLinearGradient(0, 120, 0, 256);
      gr.addColorStop(0, '#e2c088'); gr.addColorStop(1, '#c99f66');
      c.fillStyle = gr; c.fillRect(0, 120, 1024, 136);
      c.fillStyle = 'rgba(120,90,50,0.22)';
      for (let i = 0; i < 90; i++) {
        c.beginPath();
        c.ellipse(Math.random() * 1024, 135 + Math.random() * 115,
          4 + Math.random() * 12, 2 + Math.random() * 4, 0, 0, Math.PI * 2);
        c.fill();
      }
      const arbusto = (x, y, s) => {
        for (let i = 0; i < 7; i++) {
          c.fillStyle = 'rgba(' + (96 + Math.random() * 30 | 0) + ',' +
            (104 + Math.random() * 26 | 0) + ',58,0.95)';
          c.beginPath();
          c.ellipse(x + (Math.random() - 0.5) * 26 * s,
            y - Math.random() * 10 * s, 9 * s, 6 * s, 0, 0, Math.PI * 2);
          c.fill();
        }
      };
      const roca = (x, y, s) => {
        c.fillStyle = 'rgba(148,118,88,0.95)';
        c.beginPath(); c.ellipse(x, y, 14 * s, 8 * s, 0, Math.PI, 0); c.fill();
        c.fillStyle = 'rgba(120,94,68,0.9)';
        c.beginPath(); c.ellipse(x + 8 * s, y, 8 * s, 5 * s, 0, Math.PI, 0); c.fill();
      };
      for (const [x, s] of [[70, 1.3], [240, 0.9], [410, 1.5], [560, 0.8],
        [730, 1.2], [900, 1.0]]) arbusto(x, 150, s);
      for (const [x, s] of [[150, 1.1], [330, 0.8], [500, 1.2], [820, 0.9]]) roca(x, 158, s);
      // cactus medianos
      c.fillStyle = 'rgba(110,124,64,0.95)';
      for (const [x, h] of [[640, 40], [80, 34]]) {
        c.fillRect(x - 4, 150 - h, 8, h);
        c.fillRect(x - 14, 150 - h + 10, 10, 5);
        c.fillRect(x - 14, 150 - h + 10, 5, 20);
        c.fillRect(x + 4, 150 - h + 16, 10, 5);
        c.fillRect(x + 9, 150 - h + 16, 5, 16);
      }
    }
    return cv;
  }
  _texLayer(k) { return this._ct(this._layerCanvas(k)); }
  _texRock() {
    const cv = oesteCanvas(256, 256);
    const c = cv.getContext('2d');
    c.fillStyle = '#241a12'; c.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 60; i++) {
      const a = 0.05 + Math.random() * 0.14;
      c.fillStyle = Math.random() < 0.5 ? 'rgba(10,6,3,' + a + ')' : 'rgba(64,52,44,' + a * 0.7 + ')';
      c.beginPath();
      c.arc(Math.random() * 256, Math.random() * 256, 6 + Math.random() * 26, 0, Math.PI * 2);
      c.fill();
    }
    c.fillStyle = 'rgba(12,8,4,0.55)';
    c.fillRect(38, 0, 12, 256); c.fillRect(206, 0, 12, 256);
    c.fillRect(0, 40, 256, 10);
    return this._ct(cv);
  }

  /* --------------------- pared lateral CON VENTANA ------------------------ */
  /* Carga el arte del lateral y RECORTA la ventana (alfa) con las medidas
   * tomadas píxel a píxel sobre el 2395x864 del artista. Mientras carga —
   * o si falla — la pared queda opaca con el paisaje pintado (fallback). */
  _mkSide(A, ld, file, side) {
    const RH = 2.85;
    const url = A('room/vagon/' + file + '.jpg');
    const t0 = ld.load(url);
    t0.colorSpace = THREE.SRGBColorSpace;
    t0.anisotropy = this._aniso;
    const mat = new THREE.MeshStandardMaterial({
      map: t0, roughness: 0.95, metalness: 0.02,
    });
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(7.90, RH), mat);
    wall.position.set(side * 3.05, RH / 2, -1.6);
    wall.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
    this.group.add(wall);
    const px = side < 0
      ? { x0: 715, x1: 1545, y0: 150, y1: 505, r: 44 }   // izquierda
      : { x0: 805, x1: 1595, y0: 165, y1: 545, r: 44 };  // derecha
    ld.load(url, (t) => {
      try {
        const img = t.image;
        if (!img || !img.width) return;
        const cv = oesteCanvas(img.width, img.height);
        const c = cv.getContext('2d');
        c.drawImage(img, 0, 0);
        c.globalCompositeOperation = 'destination-out';
        c.beginPath();
        c.moveTo(px.x0 + px.r, px.y0);
        c.arcTo(px.x1, px.y0, px.x1, px.y1, px.r);
        c.arcTo(px.x1, px.y1, px.x0, px.y1, px.r);
        c.arcTo(px.x0, px.y1, px.x0, px.y0, px.r);
        c.arcTo(px.x0, px.y0, px.x1, px.y0, px.r);
        c.closePath(); c.fill();
        const t2 = new THREE.CanvasTexture(cv);
        t2.colorSpace = THREE.SRGBColorSpace;
        t2.anisotropy = this._aniso;
        mat.map = t2;
        mat.transparent = true;
        mat.needsUpdate = true;
        try { t0.dispose(); } catch (e) { /* */ }
      } catch (e) { /* sin recorte: pared opaca */ }
    });
    return wall;
  }

  /* ------------------------- cartel de andén ------------------------------ */
  _signPaint(name) {
    if (!this._signCv) {
      this._signCv = oesteCanvas(512, 128);
      this._signTex = this._ct(this._signCv);
    }
    const c = this._signCv.getContext('2d');
    c.clearRect(0, 0, 512, 128);
    c.fillStyle = '#2c1d0e'; c.fillRect(0, 0, 512, 128);
    c.strokeStyle = '#c89b4a'; c.lineWidth = 7; c.strokeRect(7, 7, 498, 114);
    c.textAlign = 'center';
    c.fillStyle = '#f6e3b0';
    c.font = 'bold 54px Georgia, serif';
    c.fillText(name, 256, 84);
    this._signTex.needsUpdate = true;
  }

  /* ------------------------------- escena --------------------------------- */
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.group = new THREE.Group();
    this.group.visible = false;
    g.rig.add(this.group);
    this._aniso = this._anisoOf();
    const A = (p) => new URL('./assets/' + p, import.meta.url).href;
    const ld = new THREE.TextureLoader();

    /* ==== EL VAGÓN (6 planos con las medidas de la sala núcleo) ==== */
    const RH = 2.85, RW = 6.10, RD = 7.90, zC = -1.6;
    const plainTex = (url) => {
      const t = ld.load(url);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = this._aniso;
      return t;
    };
    const boxMat = (tex) => new THREE.MeshStandardMaterial({
      map: tex, roughness: 0.95, metalness: 0.02,
    });
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(RW, RD),
      boxMat(plainTex(A('room/vagon/suelo.jpg'))));
    floor.rotation.x = -Math.PI / 2;
    floor.position.set(0, 0, zC);
    this.group.add(floor);
    const ceil = new THREE.Mesh(new THREE.PlaneGeometry(RW, RD),
      boxMat(plainTex(A('room/vagon/techo.jpg'))));
    ceil.rotation.x = Math.PI / 2;
    ceil.position.set(0, RH, zC);
    this.group.add(ceil);
    const front = new THREE.Mesh(new THREE.PlaneGeometry(RW, RH),
      boxMat(plainTex(A('room/vagon/frente.jpg'))));
    front.position.set(0, RH / 2, -5.55);
    this.group.add(front);
    const back = new THREE.Mesh(new THREE.PlaneGeometry(RW, RH),
      boxMat(plainTex(A('room/vagon/fondo.jpg'))));
    back.rotation.y = Math.PI;
    back.position.set(0, RH / 2, 2.35);
    this.group.add(back);
    this._mkSide(A, ld, 'izquierda', -1);
    this._mkSide(A, ld, 'derecha', +1);

    /* ==== PARALLAX: cielo + 4 planos a CADA ventana ====
     * Cada plano se centra en el CONO visible por su ventana desde la
     * posición de juego (ojo ~1,6 m) y su horizonte cae donde toca.
     * Los lienzos se generan UNA vez y se comparten entre lados. */
    this.scrollers = [];   // { tex, mPerRep, mult, sign }
    this._layerCanvases = [0, 1, 2, 3].map((k) => this._layerCanvas(k));
    const skyCan = this._texSky().image;
    for (const side of [-1, 1]) {
      // sentido del scroll: el mundo pasa de DELANTE (-z) a DETRÁS (+z)
      const scrollSign = side < 0 ? 1 : -1;
      const skyT = new THREE.CanvasTexture(skyCan);
      skyT.colorSpace = THREE.SRGBColorSpace;
      skyT.wrapS = THREE.RepeatWrapping;
      skyT.repeat.set(2, 1);
      const sky = new THREE.Mesh(new THREE.PlaneGeometry(240, 130),
        new THREE.MeshBasicMaterial({ map: skyT, fog: false, depthWrite: false }));
      sky.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
      sky.position.set(side * 205, 7, -156);
      sky.renderOrder = 1;
      this.group.add(sky);
      this.scrollers.push({ tex: skyT, mPerRep: 240 / 2, mult: TREN.cloudMult, sign: scrollSign });
      TREN.layers.forEach((L, k) => {
        const tex = new THREE.CanvasTexture(this._layerCanvases[k]);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.wrapS = THREE.RepeatWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;
        tex.repeat.set(L.rep, 1);
        tex.anisotropy = this._aniso;
        const m = new THREE.Mesh(new THREE.PlaneGeometry(L.w, L.h),
          new THREE.MeshBasicMaterial({ map: tex, transparent: true, fog: false }));
        m.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
        m.position.set(side * L.dist, L.cy, L.cz);
        m.renderOrder = 2 + k;
        this.group.add(m);
        this.scrollers.push({ tex, mPerRep: L.w / L.rep, mult: L.mult, sign: scrollSign });
        // arte real del artista si existe (plano1..4.png)
        try {
          ld.load(A('parallax/plano' + (k + 1) + '.png'), (t2) => {
            try {
              if (t2.image && t2.image.width) {
                tex.image = t2.image;
                tex.needsUpdate = true;
              }
            } catch (e) { /* reserva procedural */ }
          }, undefined, () => { /* sin arte: silueta procedural */ });
        } catch (e) { /* */ }
      });
    }

    /* ==== TÚNEL: roca que apaga las ventanas (fundido) ==== */
    this.texRock = this._texRock();
    this.tunnelMats = [];
    this.tunnel = new THREE.Group();
    for (const side of [-1, 1]) {
      const mat = new THREE.MeshBasicMaterial({
        map: this.texRock, transparent: true, opacity: 0,
        fog: false, depthWrite: false, side: THREE.DoubleSide,
      });
      mat.renderOrder = 9;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), mat);
      m.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
      m.position.set(side * 5.2, 1.9, -1.45);
      this.tunnel.add(m);
      this.tunnelMats.push(mat);
    }
    this.group.add(this.tunnel);

    /* ==== ESTACIÓN: andén a ambos lados (se alinea al frenar) ==== */
    this.station = new THREE.Group();
    const platM = new THREE.MeshStandardMaterial({ color: 0x6b4a26, roughness: 0.9 });
    const darkM = new THREE.MeshStandardMaterial({ color: 0x46301a, roughness: 0.9 });
    const roofM = new THREE.MeshStandardMaterial({ color: 0x39301f, roughness: 0.95 });
    for (const side of [-1, 1]) {
      const s = side;
      const plat = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.25, 30), platM);
      plat.position.set(s * TREN.stationX, -0.72, -1.4);
      this.station.add(plat);
      const edge = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.1, 30), darkM);
      edge.position.set(s * (TREN.stationX - 1.2), -0.06, -1.4);
      this.station.add(edge);
      for (let i = 0; i < 7; i++) {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.13, 2.75, 0.13), darkM);
        post.position.set(s * (TREN.stationX + 0.95), 1.27, -11.6 + i * 3.6);
        this.station.add(post);
      }
      const roof = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.16, 26), roofM);
      roof.position.set(s * (TREN.stationX + 0.4), 2.72, -1.4);
      this.station.add(roof);
      const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 0.62),
        new THREE.MeshBasicMaterial({ map: this._signTex, transparent: true }));
      sign.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
      sign.position.set(s * 3.62, 2.18, -1.4);
      this.station.add(sign);
    }
    this.station.visible = false;
    this.group.add(this.station);

    /* ==== CAJAS FUERTES (oleadas de la parada) ==== */
    this.safes = new THREE.Group();
    this.group.add(this.safes);
    this.locks = [];
    this._safeColors = [0x2f4a2c, 0x24262a, 0x5a1f22];
    this.goldMat = new THREE.MeshStandardMaterial({
      color: 0xd9a93c, roughness: 0.28, metalness: 0.85,
      emissive: 0x6a4a08, emissiveIntensity: 0.5,
    });
    this.goldMat2 = new THREE.MeshStandardMaterial({
      color: 0xe8c25a, roughness: 0.35, metalness: 0.7,
      emissive: 0x5a3c06, emissiveIntensity: 0.4,
    });
    this.ironMat = new THREE.MeshStandardMaterial({
      color: 0x2e2a26, roughness: 0.5, metalness: 0.7,
    });
    this.railWood = new THREE.MeshStandardMaterial({
      color: 0x7c5426, roughness: 0.85, metalness: 0.04,
    });

    /* ==== BOTÍN + mitades del candado ==== */
    this.coins = [];
    for (let i = 0; i < 14; i++) {
      const sp = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texDot, color: 0xffd24a, transparent: true,
        opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      sp.visible = false;
      sp.renderOrder = 12;
      this.group.add(sp);
      this.coins.push({ sp, v: new THREE.Vector3(), life: 0, t: 0 });
    }
    this.halves = [];
    for (let i = 0; i < 8; i++) {
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(0.05, 0.055, 0.035), this.goldMat);
      m.visible = false;
      this.group.add(m);
      this.halves.push({ m, v: new THREE.Vector3(), w: 0, life: 0, t: 0 });
    }
    this._hud = new HudOeste(this.ctrl);
  }

  /* ------------------------- oleadas (construcción) ----------------------- */
  _clearWave() {
    for (const l of this.locks) {
      if (l.grp) {
        this.safes.remove(l.grp);
        this._disposeTree(l.grp);
      }
    }
    this.locks = [];
    this.opened = 0;
  }
  /** Caja fuerte: cuerpo + cenefa + manija + candado DORADO con halo. */
  _mkSafe(x, y, z, colorIdx) {
    const grp = new THREE.Group();
    const bodyMat = new THREE.MeshStandardMaterial({
      color: this._safeColors[colorIdx % 3], roughness: 0.6, metalness: 0.35,
    });
    const body = new THREE.Mesh(new THREE.BoxGeometry(0.52, 0.52, 0.44), bodyMat);
    body.position.y = 0.26;
    grp.add(body);
    const trim = new THREE.Mesh(new THREE.BoxGeometry(0.56, 0.05, 0.46), this.goldMat2);
    trim.position.y = 0.44;
    grp.add(trim);
    const trim2 = trim.clone();
    trim2.position.y = 0.08;
    grp.add(trim2);
    const dial = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 0.03, 12), this.goldMat2);
    dial.rotation.x = Math.PI / 2;
    dial.position.set(0, 0.27, 0.225);
    grp.add(dial);
    for (const [lx, lz] of [[-0.2, -0.16], [0.2, -0.16], [-0.2, 0.16], [0.2, 0.16]]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.1, 0.06), bodyMat);
      leg.position.set(lx, 0.05, lz);
      grp.add(leg);
    }
    const doorPivot = new THREE.Group();
    doorPivot.position.set(-0.235, 0.26, 0.225);
    const door = new THREE.Mesh(new THREE.BoxGeometry(0.47, 0.47, 0.03), bodyMat);
    door.position.set(0.235, 0, 0);
    doorPivot.add(door);
    const hingeT = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.08, 0.045), this.goldMat2);
    hingeT.position.set(0.02, 0.2, 0.005);
    doorPivot.add(hingeT);
    const hingeB = hingeT.clone();
    hingeB.position.y = -0.2;
    doorPivot.add(hingeB);
    grp.add(doorPivot);
    const lock = new THREE.Group();
    const lbody = new THREE.Mesh(new THREE.BoxGeometry(0.13, 0.15, 0.055), this.goldMat);
    lock.add(lbody);
    const shackle = new THREE.Mesh(new THREE.TorusGeometry(0.055, 0.014, 8, 14, Math.PI), this.goldMat2);
    shackle.position.y = 0.075;
    lock.add(shackle);
    const eye = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.06, 8),
      new THREE.MeshStandardMaterial({ color: 0x3a2a08, roughness: 0.6 }));
    eye.rotation.x = Math.PI / 2;
    eye.position.z = 0.028;
    lock.add(eye);
    lock.position.set(0, 0.27, 0.265);
    grp.add(lock);
    const halo = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.ctrl.fx.texDot, color: 0xffd24a, transparent: true,
      opacity: 0.38, blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    halo.scale.setScalar(0.34);
    halo.renderOrder = 11;
    halo.position.set(0, 0.27, 0.28);
    grp.add(halo);
    grp.position.set(x, y, z);
    this.safes.add(grp);
    return {
      grp, lock, door: doorPivot, halo,
      pos: new THREE.Vector3(x, y + 0.27, z + 0.265),
      baseX: x, opened: false, openT: 0,
      slide: null, hatch: null,
    };
  }
  _mkShelf(x, y, z) {
    const shelf = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.06, 0.5), this.railWood);
    shelf.position.set(x, y - 0.02, z);
    this.safes.add(shelf);
    for (const px of [-0.4, 0.4]) {
      const post = new THREE.Mesh(new THREE.BoxGeometry(0.07, y, 0.07), this.railWood);
      post.position.set(x + px, y / 2 - 0.02, z);
      this.safes.add(post);
    }
  }
  _mkRail(y) {
    const rail = new THREE.Mesh(new THREE.BoxGeometry(2.9, 0.06, 0.06), this.goldMat2);
    rail.position.set(0, y, TREN.safeZ - 0.2);
    this.safes.add(rail);
    const rail2 = new THREE.Mesh(new THREE.BoxGeometry(2.9, 0.05, 0.05), this.ironMat);
    rail2.position.set(0, y + 0.12, TREN.safeZ - 0.2);
    this.safes.add(rail2);
  }
  _mkHatch(x, y, z, phase) {
    const frame = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.62, 0.07), this.ironMat);
    frame.position.set(x, y, z);
    this.safes.add(frame);
    const doorPivot = new THREE.Group();
    doorPivot.position.set(x, y + 0.30, z);
    const hatch = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.58, 0.04), this.ironMat);
    hatch.position.set(0, -0.29, 0);
    const hint = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.05, 0.045),
      new THREE.MeshStandardMaterial({ color: 0xd9b23c, roughness: 0.5 }));
    hint.position.set(0, -0.52, 0.001);
    doorPivot.add(hatch, hint);
    this.safes.add(doorPivot);
    const lamp = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.ctrl.fx.texDot, color: 0xffb45f, transparent: true,
      opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    lamp.scale.setScalar(0.16);
    lamp.position.set(x + 0.42, y + 0.42, z + 0.05);
    this.safes.add(lamp);
    return { doorPivot, lamp, phase };
  }
  /** Construye la OLEADA de la parada n (1 repisas · 2 raíles · 3 compuertas). */
  _buildWave(n) {
    this._clearWave();
    const Z = TREN.safeZ;
    if (n === 1) {
      const spots = [
        { x: -0.95, y: 1.30, ci: 0 },
        { x: 0.0, y: 0.72, ci: 1 },
        { x: 0.95, y: 1.02, ci: 2 },
      ];
      for (const s of spots) {
        this._mkShelf(s.x, s.y, Z - 0.18);
        this.locks.push(this._mkSafe(s.x, s.y, Z, s.ci));
      }
      this.waveTotal = 3;
    } else if (n === 2) {
      this._mkRail(1.44); this._mkRail(0.90);
      const a = this._mkSafe(-1.0, 1.18, Z, 1);
      a.slide = { amp: 1.0, w: 0.52, ph: 0 };
      const b = this._mkSafe(1.0, 0.64, Z, 0);
      b.slide = { amp: 1.05, w: -0.68, ph: 2.1 };
      this.locks.push(a, b);
      this.waveTotal = 2;
    } else {
      const spots = [
        { x: -0.9, y: 1.28, ci: 2 },
        { x: 0.0, y: 0.74, ci: 0 },
        { x: 0.9, y: 1.20, ci: 1 },
      ];
      let i = 0;
      for (const s of spots) {
        const safe = this._mkSafe(s.x, s.y, Z, s.ci);
        safe.hatch = this._mkHatch(s.x, s.y + 0.26, Z + 0.24, i * 1.35);
        this.locks.push(safe);
        i++;
      }
      this.waveTotal = 3;
    }
    this.opened = 0;
  }

  /* ------------------------------- ciclo ---------------------------------- */
  start() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    this.wave = 1;
    this.time = TREN.time;
    this.v = 0;
    this.W = 0;
    this.meetW = 0;
    this.stationW = 0;         // la PARADA 1 nace DETENIDA en la estación
    this._signPaint(TREN.stationNames[0]);
    this.station.visible = true;
    this.station.position.z = 0;
    this.phase = 'intro';
    this.t = 0;
    this._stoppedT = 0;
    this._tunnelT = TREN.tunnelFirst;
    this._tunnelPhase = 'none';
    this._tunnelT2 = 0;
    this._dead = false;
    this._floorB = 0;
    this._resultT = 0;
    this._wavePause = 0;
    this._buildWave(1);
    // EL VAGÓN MANDA: fuera saloon, troqueles, mapa, cartel y forajido
    if (g.roomGroup) g.roomGroup.visible = false;
    if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = false;
    this.ctrl.mapa.visible = false;
    this.ctrl.cartel.visible = false;
    if (this.ctrl.sprite) this.ctrl.sprite.visible = false;
    if (this.ctrl.arbustoGroup) this.ctrl.arbustoGroup.visible = false;
    if (this.ctrl.arbustoSombra) this.ctrl.arbustoSombra.visible = false;
    g.champDecorHidden = true;
    // escena de juego: red visible, árbitro dormido, bola automática
    if (!this.ctrl._netParts || !this.ctrl._netParts.length) {
      this.ctrl._netParts = this.ctrl._findNetParts();
    }
    for (const m of this.ctrl._netParts) m.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.rules.state = this.ctrl.stateName;
    g.rules.message = tx('tren_up');
    g.ball.ignoreNet = false;
    this.ctrl._parkMainBall();
    g.ballMesh.visible = false;
    this.ctrl.musicOn();
    this._hud.show();
    this._msg = tx('tren_up');
    this._msgT = TREN.introPause;
    this._hud.set(this.time, this._prog(), this._msg);
    this._respawnT = 1.0;
    this.ctrl.sfx('whistle', 0);
    this._startRumble();
    this._setRumble(0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 140);
  }

  /** El tren ARRANCA desde el andén (o tras la parada). */
  _depart() {
    this.phase = 'run';
    this.time = TREN.time;
    this._stoppedT = 0;
    this._buildWave(this.wave);
    this._serveBall();
    this._msg = tx('tren_sale', { n: this.wave, txt: tx('tren_oleada' + this.wave) });
    this._msgT = 2.8;
    this.ctrl.sfx('whistle', 0);
  }

  /** El tren llega AL ANDÉN: frena del todo y espera. */
  _arrived() {
    const g = this.game;
    this.v = 0;
    this.W = this.meetW;
    this.phase = 'stop';
    this._stoppedT = 0;
    this.ctrl.sfx('brake', 0);
    this._setRumble(0);
    if (this.wave >= 3) return this._stationReached();   // andén FINAL: victoria
    this.wave++;                                        // próxima parada
    this._msg = tx('tren_llega');
    this._msgT = TREN.arrivePause;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 120);
  }

  /** ¡ESTACIÓN FINAL! Freno largo, silbato y botín completo: SUPERADA. */
  _stationReached() {
    const g = this.game;
    this.phase = 'win';
    this._resultT = 6.0;
    this._signPaint(TREN.stationNames[3]);
    this.ctrl.sfx('whistle_long', 0);
    g.rules.message = tx('tren_estacion');
    this._msg = tx('tren_estacion');
    this._msgT = 5.0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 220);
  }
  _fail() {
    const g = this.game;
    this.phase = 'fail';
    this._resultT = 4.0;
    this._msg = tx('tren_falla');
    this._msgT = 4.0;
    g.rules.message = tx('tren_falla');
    this._hud.set(0, this._prog(), tx('tren_falla'));
  }
  _finish() {
    const won = this.phase === 'win';
    this.phase = 'idle';
    this.ctrl._endTren(won);
    this.done = true;
  }
  _prog() {
    return 'PARADA ' + this.wave + '/3 · ' + this.opened + '/' + this.waveTotal;
  }

  /** FÍSICA + FASES (testStep). */
  step(dt) {
    if (this.done || this.phase === 'idle') return;
    const g = this.game;
    this.t += dt;
    if (this._msgT > 0) this._msgT -= dt;
    if (this.phase === 'intro') {
      // DETENIDO en la estación 1: el andén espera tras las ventanas
      this._parkBall();
      this._stoppedT += dt;
      if (this._stoppedT >= TREN.introPause) this._depart();
    } else if (this.phase === 'run') {
      this.time -= dt;
      if (this.time <= 0) { this.time = 0; this._fail(); return; }
      // crucero hacia delante
      this.v = Math.min(TREN.vMax, this.v + TREN.accel * dt);
      this.W += this.v * dt;
      this._tunnelStep(dt);
      if (this._wavePause > 0) {
        this._wavePause -= dt;
        this._parkBall();
        if (this._wavePause <= 0) {
          this._buildWave(this.wave);
          this._serveBall();
          this._msg = tx('tren_oleada', {
            n: this.wave, txt: tx('tren_oleada' + this.wave),
          });
          this._msgT = 2.6;
        }
      } else if (this._dead) {
        this._respawnT -= dt;
        if (this._respawnT <= 0) this._serveBall();
      } else {
        this._simBall(dt);
      }
      this._waveStep(dt);
    } else if (this.phase === 'arrive') {
      // FRENO calculado: v² = 2·a·d hasta el andén
      this._parkBall();
      const D = Math.max(0.05, this.meetW - this.W);
      const a = clamp((this.v * this.v) / (2 * D), 0.12, 1.1);
      this.v = Math.max(0, this.v - a * dt);
      this.W += this.v * dt;
      if (this.W >= this.meetW - 0.02 || this.v <= 0.001) this._arrived();
    } else if (this.phase === 'stop') {
      this._parkBall();
      this._stoppedT += dt;
      if (this._stoppedT >= TREN.arrivePause) this._depart();
    } else if (this.phase === 'win' || this.phase === 'fail') {
      this._parkBall();
      if (this.phase === 'fail') {
        this.v = Math.max(0, this.v - 0.8 * dt);
        this.W += this.v * dt;
      }
      this._resultT -= dt;
      if (this._resultT <= 0) this._finish();
    }
    this._hud.set(this.time, this._prog(), this._msgT > 0 ? this._msg : '');
  }

  /** VISUAL por frame (CTRL.update): parallax, andén, túnel, botín, halos. */
  fxStep(dt) {
    if (this.done || !this.inited) return;
    const dW = this.v * dt;
    // PARALLAX: cada plano a SU multiplicador (offset de textura)
    for (const s of this.scrollers) {
      if (!s.tex) continue;
      const du = (dW * s.mult / s.mPerRep) * s.sign;
      s.tex.offset.x = (s.tex.offset.x + du) % 1;
    }
    // ANDÉN: corre con el mundo (z = W - estación) y se esconde al pasar
    if (this.station) {
      const rel = this.W - this.stationW;
      this.station.position.z = rel;
      this.station.visible = Math.abs(rel) < 32;
    }
    // rumor de la locomotora acorde a la velocidad
    this._setRumble(this.v / TREN.vMax);
    // fundido del TÚNEL
    let top = 0;
    if (this._tunnelPhase === 'in') {
      top = Math.min(0.97, this._tunnelT2 / TREN.tunnelIn * 0.97);
    } else if (this._tunnelPhase === 'dur') top = 0.97;
    else if (this._tunnelPhase === 'out') {
      top = 0.97 * Math.max(0, 1 - this._tunnelT2 / TREN.tunnelOut);
    }
    for (const m of this.tunnelMats) m.opacity = top;
    // botín en el aire
    for (const c of this.coins) {
      if (c.life <= 0) continue;
      c.t += dt;
      c.v.y -= 5.5 * dt;
      c.sp.position.addScaledVector(c.v, dt);
      const f = 1 - c.t / c.life;
      if (f <= 0) { c.life = 0; c.sp.visible = false; continue; }
      c.sp.material.opacity = Math.min(1, f * 2);
    }
    // mitades del candado
    for (const h of this.halves) {
      if (h.life <= 0) continue;
      h.t += dt;
      h.v.y -= 6.5 * dt;
      h.m.position.addScaledVector(h.v, dt);
      h.m.rotation.z += h.w * dt;
      if (h.t >= h.life) { h.life = 0; h.m.visible = false; }
    }
    // candados: halo latiendo (MÁS fuerte en el túnel), deslizamiento visual
    const inTunnel = this._tunnelPhase === 'dur' || this._tunnelPhase === 'in';
    for (const l of this.locks) {
      if (l.opened) {
        if (l.openT > 0 && l.door) {
          l.openT = Math.min(1.35, l.openT + dt * 2.6);
          l.door.rotation.y = -l.openT;
        }
        continue;
      }
      l.halo.material.opacity = (inTunnel ? 0.62 : 0.34) +
        Math.sin(this.t * 5.2 + l.pos.x * 3) * 0.10;
      l.halo.scale.setScalar(inTunnel ? 0.5 : 0.34);
      l.lock.position.y = 0.27 + Math.sin(this.t * 3.1 + l.pos.z) * 0.004;
    }
    // lámparas de compuerta (visibles con la trampilla abierta)
    for (const l of this.locks) {
      if (!l.hatch) continue;
      const openK = Math.max(0, Math.min(1, l.hatch.doorPivot.rotation.x / 1.2));
      l.hatch.lamp.material.opacity = openK * (inTunnel ? 0.9 : 0.55) +
        (openK > 0.5 ? Math.sin(this.t * 4) * 0.08 : 0);
    }
    if (this.ctrl.fx) this.ctrl.fx.update(dt);
  }

  /** Movimiento de la oleada: raíles deslizantes + compuertas. */
  _waveStep(dt) {
    for (const l of this.locks) {
      if (l.opened) continue;
      if (l.slide) {
        l.grp.position.x = l.baseX +
          Math.sin(this.t * l.slide.w * Math.PI * 2 + l.slide.ph) * l.slide.amp;
        l.pos.set(l.grp.position.x, l.grp.position.y + 0.27, TREN.safeZ + 0.265);
      }
      if (l.hatch) {
        const c = (this.t + l.hatch.phase) % 4.7;
        let ang = 0;
        if (c < 1.5) ang = 0;
        else if (c < 2.05) ang = ((c - 1.5) / 0.55) * 1.75;
        else if (c < 4.15) ang = 1.75;
        else ang = 1.75 * Math.max(0, 1 - (c - 4.15) / 0.55);
        l.hatch.doorPivot.rotation.x = ang;
      }
    }
  }

  /** SILBATO + TÚNEL: las ventanas se apagan y SÓLO BRILLAN LOS CANDADOS. */
  _tunnelStep(dt) {
    if (this._tunnelPhase === 'none') {
      this._tunnelT -= dt;
      if (this._tunnelT <= 0) {
        this._tunnelPhase = 'in';
        this._tunnelT2 = 0;
        this.ctrl.sfx('whistle', 0);
        this._msg = tx('tren_tunel');
        this._msgT = 2.6;
      }
    } else if (this._tunnelPhase === 'in') {
      this._tunnelT2 += dt;
      if (this._tunnelT2 >= TREN.tunnelIn) { this._tunnelPhase = 'dur'; this._tunnelT2 = 0; }
    } else if (this._tunnelPhase === 'dur') {
      this._tunnelT2 += dt;
      if (this._tunnelT2 >= TREN.tunnelDur) { this._tunnelPhase = 'out'; this._tunnelT2 = 0; }
    } else if (this._tunnelPhase === 'out') {
      this._tunnelT2 += dt;
      if (this._tunnelT2 >= TREN.tunnelOut) {
        this._tunnelPhase = 'none';
        this._tunnelT = TREN.tunnelEvery * (0.82 + Math.random() * 0.36);
      }
    }
  }

  /* ------------------------------ bola ------------------------------------ */
  _parkBall() {
    const g = this.game;
    if (g.ball.pos.y > -3.5) {
      g.ball.pos.set(0, -4, 0);   // v2.101: fuera del teleporte de seguridad
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = false;
    }
  }
  _serveBall() {
    const g = this.game;
    const D = ODIMS();
    this._dead = false;
    this._floorB = 0;
    g.ball.pos.set((Math.random() - 0.5) * 0.5, 1.42, D.tableCenterZ + 0.85);
    g.ball.vel.set((Math.random() - 0.5) * 0.5, -0.6, -0.55);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = true;
    this.ctrl.sfx('lanzar', 0);
  }
  _simBall(dt) {
    const g = this.game;
    const D = ODIMS();
    const presenting = g.renderer.xr.isPresenting;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (presenting && ps && ps.active) ? [ps] : [];
    g.events.length = 0;
    stepPhysics(dt, g.ball, pads, g.events, this._extra);
    for (const e of g.events) {
      if (e.type === 'paddle') {
        this._floorB = 0;
        if (e.speed) this.ctrl.sfx('pala', 0);
      }
    }
    const b = g.ball;
    if (b.pos.z > 2.3 || b.pos.z < TREN.safeZ - 0.55 ||
        b.pos.x > 2.7 || b.pos.x < -2.7) {
      this._killBall();
      return;
    }
    const overTable = Math.abs(b.pos.x) <= D.tableHalfWidth + 0.25 &&
      b.pos.z >= D.tableCenterZ - D.tableHalfLength - 0.25 &&
      b.pos.z <= D.tableCenterZ + D.tableHalfLength + 0.6;
    if (!overTable && b.pos.y < 0.06 && b.vel.y < 0.4) {
      this._floorB++;
      if (this._floorB >= 2) { this._killBall(); return; }
      b.vel.y = Math.abs(b.vel.y) * 0.45;
    }
    if (b.vel.lengthSq() < 0.09 && b.pos.y < D.tableTopY + 0.15) {
      this._deadT = (this._deadT || 0) + dt;
      if (this._deadT > 0.9) { this._deadT = 0; this._killBall(); }
    } else this._deadT = 0;
  }
  _killBall() {
    if (this._dead) return;
    this._dead = true;
    this._deadT = 0;
    this._respawnT = TREN.respawnT;
    this.game.ballMesh.visible = false;
    this._parkBall();
  }

  /* ------------------------- colisionador extra --------------------------- */
  _collide(ball) {
    if (this.phase !== 'run' || this._wavePause > 0) return;
    const r = (ODIMS() ? ODIMS().ballRadius : 0.02) + TREN.lockR;
    const p = ball.pos;
    for (const l of this.locks) {
      if (l.opened) continue;
      if (l.hatch && l.hatch.doorPivot.rotation.x < 1.1) continue;
      const dx = p.x - l.pos.x, dy = p.y - l.pos.y, dz = p.z - l.pos.z;
      if (dx * dx + dy * dy + dz * dz < r * r) {
        const d = Math.max(0.02, Math.sqrt(dx * dx + dy * dy + dz * dz));
        p.x = l.pos.x + dx / d * r;
        p.y = l.pos.y + dy / d * r;
        p.z = l.pos.z + dz / d * r;
        const nX = dx / d, nY = dy / d, nZ = dz / d;
        const dot = ball.vel.x * nX + ball.vel.y * nY + ball.vel.z * nZ;
        ball.vel.x -= 2 * dot * nX * 0.55;
        ball.vel.y -= 2 * dot * nY * 0.55;
        ball.vel.z -= 2 * dot * nZ * 0.55;
        this._openSafe(l);
        break;
      }
    }
  }

  /* --------------------------- apertura de caja --------------------------- */
  _openSafe(l) {
    const g = this.game;
    l.opened = true;
    l.lock.visible = false;
    l.halo.visible = false;
    this.opened++;
    this.ctrl.sfx('coin', 0);
    this.ctrl.sfx('madera', 0);
    l.openT = 0.0001;
    let placed = 0;
    for (const h of this.halves) {
      if (h.life > 0) continue;
      h.life = 0.8 + Math.random() * 0.4;
      h.t = 0;
      h.m.visible = true;
      h.m.position.copy(l.pos);
      h.v.set((Math.random() - 0.5) * 1.6, 1.6 + Math.random() * 1.2, 0.8 + Math.random());
      h.w = 6 + Math.random() * 10;
      if (++placed >= 2) break;
    }
    for (let i = 0; i < 9; i++) {
      const c = this.coins.find((cc) => cc.life <= 0);
      if (!c) break;
      c.life = 0.9 + Math.random() * 0.5;
      c.t = 0;
      c.sp.visible = true;
      c.sp.position.copy(l.pos).add(new THREE.Vector3(
        (Math.random() - 0.5) * 0.2, Math.random() * 0.1, 0.05));
      c.v.set((Math.random() - 0.5) * 1.3, 1.8 + Math.random() * 1.6, 0.6 + Math.random() * 0.8);
      const s = 0.05 + Math.random() * 0.06;
      c.sp.scale.setScalar(s);
      c.sp.material.opacity = 1;
    }
    this.ctrl.fx.flash(l.pos, 1.5, 0xffd24a);
    this.ctrl.fx.spark(l.pos, 12, 0xffd24a, 2.8, 1.2);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 110);
    if (this.opened >= this.waveTotal) {
      // PARADA COMPLETADA: el tren frena hasta el andén siguiente
      if (this._tunnelPhase === 'in' || this._tunnelPhase === 'dur') {
        this._tunnelPhase = 'out';
        this._tunnelT2 = 0;
      }
      this.meetW = this.W + TREN.brakeDist;
      this.stationW = this.meetW;
      this._signPaint(TREN.stationNames[this.wave]);
      this.phase = 'arrive';
      this._msg = tx('tren_oleada_ok');
      this._msgT = 2.4;
      this.ctrl.sfx('whistle', 0);
      this._parkBall();
    } else {
      this._msg = tx('tren_caja', { n: this.opened, m: this.waveTotal });
      this._msgT = 1.8;
    }
  }

  /** RUMOR de la locomotora: ruido grave en bucle (volumen con la marcha). */
  _startRumble() {
    try {
      const A = this.game.audio;
      if (!A || !A.ctx || A.ctx.state !== 'running' || this._rumble) return;
      const ctx = A.ctx;
      const len = 1.6;
      const buf = ctx.createBuffer(1, ctx.sampleRate * len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      let last = 0;
      for (let i = 0; i < d.length; i++) {
        const white = Math.random() * 2 - 1;
        last = (last + 0.035 * white) / 1.035;   // brown noise
        d[i] = last * 5.2;
      }
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      const lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.value = 130;
      const gain = ctx.createGain();
      gain.gain.value = 0.05;
      src.connect(lp); lp.connect(gain); gain.connect(ctx.destination);
      src.start();
      this._rumble = { src, gain };
    } catch (e) { this._rumble = null; }
  }
  _setRumble(k) {
    if (!this._rumble) return;
    try {
      this._rumble.gain.gain.value = 0.045 + 0.085 * clamp(k, 0, 1);
    } catch (e) { /* */ }
  }
  _stopRumble() {
    if (!this._rumble) return;
    try { this._rumble.src.stop(); } catch (e) { /* */ }
    try { this._rumble.gain.disconnect(); } catch (e) { /* */ }
    this._rumble = null;
  }

  dispose() {
    const g = this.game;
    this._stopRumble();
    this._clearWave();
    if (this.group) {
      g.rig.remove(this.group);
      this._disposeTree(this.group);
      this.group = null;
    }
    if (this._hud) {
      this._hud.hide();
      if (this._hud.group) { g.rig.remove(this._hud.group); }
    }
    this.done = true;
  }
  _disposeTree(o) {
    o.traverse((n) => {
      if (n.geometry) n.geometry.dispose();
      if (n.material) {
        const mats = Array.isArray(n.material) ? n.material : [n.material];
        for (const mm of mats) { if (mm.map) mm.map.dispose(); mm.dispose(); }
      }
    });
  }
}
