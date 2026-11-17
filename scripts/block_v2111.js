  /* ======================================================================
   *  v2.111 · LA PIRÁMIDE DE CAJONES (arkanoid del botín)
   *  10 cajones en pirámide 5-3-2 sobre el muelle de madera. Reparto
   *  ALEATORIO: 2-3 cajones llevan CANDADO-lingote (cubolingote*.png del
   *  artista, al menos 2 y nunca más de un lingote por cajón); el resto
   *  son neutros (cubo1-3.png). FÍSICA: cada cajón se APOYA en los dos de
   *  su fila inferior — si los pierde, CAE por gravedad hasta el apoyo
   *  siguiente. Pirámide nueva (reparto nuevo) al vaciarla.
   *  ====================================================================== */
  _clearPiramide() {
    for (const rec of this.cubos) {
      this.piramide.remove(rec.mesh);
    }
    this.cubos = [];
  }
  _cuboX(row, i) {
    const n = 5 - row * 2;                    // 5 · 3 · 2
    return (i - (n - 1) / 2) * TREN.cubo.size;
  }
  _buildPiramide() {
    this._clearPiramide();
    const C = TREN.cubo;
    const nLing = C.minLingote +
      ((Math.random() * (C.maxLingote - C.minLingote + 1)) | 0);
    const slots = [];
    for (let r = 0; r < 3; r++) {
      for (let i = 0; i < 5 - r * 2; i++) slots.push({ row: r, i });
    }
    for (let i = slots.length - 1; i > 0; i--) {   // barajo
      const j = (Math.random() * (i + 1)) | 0;
      const t = slots[i]; slots[i] = slots[j]; slots[j] = t;
    }
    const lingSet = new Set(slots.slice(0, nLing).map((s) => s.row + ':' + s.i));
    let k = 0;
    for (const s of slots) {
      const isLing = lingSet.has(s.row + ':' + s.i);
      const tipo = isLing
        ? 1 + ((Math.random() * 2) | 0)          // cubolingote1|2
        : 1 + ((Math.random() * 3) | 0);         // cubo1|2|3
      const mesh = new THREE.Mesh(this._cuboGeo,
        isLing ? this._matLingote[tipo - 1] : this._matCubo[tipo - 1]);
      const x = this._cuboX(s.row, s.i);
      const y = C.peanaH + C.size * s.row + C.size / 2;
      mesh.position.set(x, y, C.z);
      mesh.scale.setScalar(0.01);
      this.piramide.add(mesh);
      this.cubos.push({
        mesh, row: s.row, i: s.i, tipo,
        base: new THREE.Vector3(x, y, C.z),
        lingote: isLing, abierto: false, muerto: false,
        cae: false, vy: 0, shakeT: 0, born: 0.16 + k * 0.045,
      });
      k++;
    }
  }
  /** Apoyos del cajón: los DOS de la fila inferior que lo flanquean. */
  _soportes(rec) {
    if (rec.row === 0) return [];               // fila base: muelle siempre
    const out = [];
    for (const o of this.cubos) {
      if (o === rec || o.muerto || o.row !== rec.row - 1) continue;
      if (Math.abs(o.base.x - rec.base.x) <= TREN.cubo.size * 0.55) out.push(o);
    }
    return out;
  }
  _apoyado(rec) {
    return rec.row === 0 || this._soportes(rec).length > 0;
  }
  /** Superficie donde aterrizaría el cajón (cima del apoyo restante o muelle). */
  _sueloBajo(rec) {
    let top = TREN.cubo.peanaH;
    for (const o of this.cubos) {
      if (o === rec || o.muerto || o.row >= rec.row) continue;
      if (Math.abs(o.base.x - rec.base.x) <= TREN.cubo.size * 0.55) {
        top = Math.max(top, o.base.y + TREN.cubo.size / 2);
      }
    }
    return top;
  }

  /* --------------------- impacto de la bola en un cajón ------------------- */
  _golpeCubo(rec) {
    const g = this.game;
    if (rec.lingote) {
      /* CANDADO-lingote: cambia la textura a ABIERTO, tiembla 1 s y
       * REVIENTA soltando el lingote en parábola (petición literal). */
      rec.abierto = true;
      rec.shakeT = 1.0;
      rec.mesh.material = this._matAbierto[rec.tipo - 1];
      this.ctrl.sfx('impacto', 0);
      this.ctrl.sfx('madera', 0);
      this.ctrl.fx.flash(rec.mesh.position, 1.3, 0xffd24a);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.55, 110);
    } else {
      this._revientaCubo(rec);
    }
  }
  _revientaCubo(rec) {
    rec.muerto = true;
    rec.mesh.visible = false;
    this.ctrl.sfx('madera', 0);
    this.ctrl.fx.spark(rec.mesh.position, 10, 0xc99a5a, 2.6, 1.1);
    this.ctrl.fx.smoke(rec.mesh.position, 1, false);
    const g = this.game;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 90);
    this._checkPiramide();
  }
  _explotaLingote(rec) {
    rec.muerto = true;
    rec.mesh.visible = false;
    this.ctrl.sfx('boom', 0);
    this.ctrl.fx.flash(rec.mesh.position, 2.0, 0xffd24a);
    this.ctrl.fx.spark(rec.mesh.position, 16, 0xffd24a, 3.2, 1.4);
    this.ctrl.fx.smoke(rec.mesh.position, 2, false);
    const g = this.game;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 150);
    this._lanzaLingote(rec.mesh.position.clone());
    this._checkPiramide();
  }
  _checkPiramide() {
    if (this.cubos.length && this.cubos.every((r) => r.muerto)) {
      this._pirT = TREN.cubo.respawn;
      this._msg = tx('tren_piramide');
      this._msgT = 1.8;
    }
  }

  /* ------------------------ lingotes (vuelo + pila) ----------------------- */
  _pileSlot(n) {
    const D = ODIMS();
    n = Math.min(n, 11);
    if (n >= 9) {                               // segunda capa de la pila
      const k = n - 9;
      return new THREE.Vector3(k % 2 ? 0.1 : -0.1, D.tableTopY + 0.095,
        D.tableCenterZ - 0.75 - Math.floor(k / 2) * 0.3);
    }
    const gx = n % 3, gz = Math.floor(n / 3);
    return new THREE.Vector3(-0.2 + gx * 0.2, D.tableTopY + 0.002,
      D.tableCenterZ - 0.45 - gz * 0.38);
  }
  _lanzaLingote(from) {
    if (!this._lingoteProto) {                  // GLB aún cargando: caja reserva
      const g0 = new THREE.Group();
      g0.add(new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.05, 0.08), this.goldMat));
      this._lingoteProto = g0;
    }
    const D = ODIMS();
    const mesh = this._lingoteProto.clone(true);
    mesh.visible = true;
    const dest = this._pileSlot(this._pileN);
    const T = 0.9, grav = 6.5;
    const v = new THREE.Vector3(
      (dest.x - from.x) / T,
      (dest.y - from.y + 0.5 * grav * T * T) / T,
      (dest.z - from.z) / T);
    mesh.position.copy(from);
    this.pile.add(mesh);
    this.ingotes.push({
      mesh, t: 0, T, v, grav, volando: true, robado: false,
      dest, yaw: (Math.random() - 0.5) * 1.4,
    });
    this._pileN++;
    this.ctrl.sfx('coin', 0);
  }
  _limpiaPila() {
    for (const it of this.ingotes) this.pile.remove(it.mesh);
    this.ingotes = [];
    this._pileN = 0;
  }
  _enLingote() {
    this.ingots++;
    const meta = TREN.meta[this.wave - 1] || 3;
    if (this.ingots === meta) {
      this._msg = tx('tren_objetivo', { n: this.ingots, m: meta });
      this._msgT = 3.0;
      this.ctrl.sfx('diana', 0);
    } else {
      this._msg = tx('tren_lingote', { n: this.ingots, m: meta });
      this._msgT = 1.6;
    }
  }
  /** El forajido se lleva UN lingote de la pila (si hay): sale despedido. */
  _robaLingote() {
    let tgt = null;
    for (let i = this.ingotes.length - 1; i >= 0; i--) {
      if (!this.ingotes[i].volando && !this.ingotes[i].robado) {
        tgt = this.ingotes[i]; break;
      }
    }
    if (!tgt) return false;
    tgt.robado = true;
    tgt.volando = true;
    tgt.t = 0; tgt.T = 0.75; tgt.grav = 5.5;
    tgt.v.set((Math.random() < 0.5 ? -1 : 1) * 2.6, 2.3, 2.4);
    this.ctrl.sfx('impacto', 0);
    return true;
  }

  /* ======================================================================
   *  v2.111 · EL FORAJIDO GALOPANTE — sprite sheet en BUCLE (galope1-3)
   *  que cabalga PARALELO al tren y lo ADELA; aparece cada cierto tiempo
   *  al azar, por ambos lados (nunca los dos a la vez), unas 10 veces por
   *  trayecto. Dos comportamientos:
   *   · PASO — cruza la ventana y sigue su camino (galope de perfil).
   *   · ATAQUE — alcanza el centro de la ventana, iguala la marcha y se
   *     queda 4 s (galope_ventana1-3); en 6 de cada 10 saca el REVÓLVER
   *     (galope_ventana*_dispara) con la DIANA del artista encima: acierto =
   *     galope_herido 1 s + fundido a negro; fallo = humo, disparo y ROBO
   *     de un lingote.
   *  ====================================================================== */
  _fjFrameOf(kind) {
    const arr = this._fjTex[kind] || this._fjTex.paso;
    return arr[this._fjFrame % arr.length];
  }
  _fjSetFrame(kind) {
    const e = this._fjFrameOf(kind);
    this.fjPlane.material = e.mat;
    const F = TREN.forajido;
    const h = F.h, w = h * (e.aspect || 1);
    this._fjW = w;
    // ESPEJO en la ventana DERECHA: el arte galopa mirando a su derecha;
    // así el caballo SIEMPRE encara el sentido de su galope (hacia -z).
    this.fjPlane.scale.set(w * (this._fjSide > 0 ? -1 : 1), h, 1);
  }
  _fjPose(bob) {
    const F = TREN.forajido;
    this.fj.position.set(this._fjSide * F.xOut, bob, this._fjZ);
    this.fjPlane.rotation.y = this._fjSide < 0 ? Math.PI / 2 : -Math.PI / 2;
  }
  _fjSpawn() {
    const F = TREN.forajido;
    this._fjCount++;
    // lados alternados sin caer en la monotonía (nunca 3 iguales seguidos)
    this._fjSide =
      (this._fjLastSide === this._fjPrevSide) ? -this._fjLastSide
        : (Math.random() < 0.5 ? -1 : 1);
    this._fjPrevSide = this._fjLastSide;
    this._fjLastSide = this._fjSide;
    const paso = Math.random() < 0.45;          // 45% cruza sin pararse
    this._fjState = paso ? 'paso' : 'ida';
    this._fjAtk = !paso && Math.random() < 0.6; // 60% de las paradas: dispara
    this._fjZ = F.zIn;
    this._fjT = 0; this._fjFrame = 0; this._fjFrameT = 0; this._fjV = 0;
    this.fj.visible = true;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
  }
  _fjGone() {
    this.fj.visible = false;
    this.fjDiana.visible = false;
    this._fjState = 'off';
    const F = TREN.forajido;
    this._fjNext = (this._fjCount >= F.total) ? 9999
      : F.nextMin + Math.random() * (F.nextMax - F.nextMin);
  }
  _fjDianaPos() {
    const F = TREN.forajido;
    // posición VARIABLE sobre el jinete (torso/cabeza), delante del plano
    this.fjDiana.position.set(
      -this._fjSide * 0.06,
      (0.04 + Math.random() * 0.24) * F.h,
      (Math.random() - 0.5) * 0.34);
  }
  _fjHerido() {
    this.fjDiana.visible = false;
    this._fjState = 'herido';
    this._fjT = 0; this._fjFrame = 0;
    this._fjSetFrame('herido');
    this.ctrl.sfx('grito', 0);
    this._msg = tx('tren_herido');
    this._msgT = 2.2;
    this.ctrl.fx.flash(this.fj.position, 1.4, 0xff6a4a);
  }
  _fjFuga() {
    this._fjState = 'fuga';
    this._fjT = 0; this._fjFrame = 0; this._fjV = 1.2;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
  }
  _fjDispara() {
    const g = this.game;
    // humo + fogonazo en la BOCA del revólver (fracción del plano del arte)
    _AS_V1.set(-0.10 * this._fjW, 0.10 * TREN.forajido.h, -this._fjSide * 0.10);
    this.fjPlane.localToWorld(_AS_V1);
    _AS_V1.x -= this._fjSide * 0.06;
    this.ctrl.fx.smokeGun(_AS_V1, 3);
    this.ctrl.fx.flash(_AS_V1, 1.3, 0xffd98a);
    this.ctrl.sfx('disparo', 0);
    if (g.renderer.xr.isPresenting) { g.haptic(0, 0.6, 160); g.haptic(1, 0.6, 160); }
    if (this._robaLingote()) {
      this._msg = tx('tren_robo');
      this._msgT = 2.4;
    }
  }
  _fjUpdate(dt) {
    const F = TREN.forajido;
    if (this._fjState === 'off') {
      if (this.phase !== 'run') return;
      this._fjNext -= dt;
      if (this._fjNext <= 0 && this._fjCount < F.total) this._fjSpawn();
      return;
    }
    this._fjT += dt;
    // bucle del galope (sprite sheet de 3 frames del artista)
    this._fjFrameT += dt;
    if (this._fjFrameT >= F.loopT) {
      this._fjFrameT -= F.loopT;
      this._fjFrame++;
      if (this._fjState === 'ventana') {
        this._fjSetFrame(this._fjAtk ? 'dispara' : 'ventana');
      } else if (this._fjState !== 'herido' && this._fjState !== 'fade') {
        this._fjSetFrame('paso');
      }
    }
    const bob = Math.abs(Math.sin(this._fjT * F.bobW)) * F.bobA;
    if (this._fjState === 'paso') {
      // GALOPE DE PASO: cruza la ventana adelantando al tren y sigue
      this._fjZ -= F.vPaso * dt;
      if (this._fjZ < F.zOut) return this._fjGone();
      this._fjPose(bob);
    } else if (this._fjState === 'ida') {
      // aproximación frenando hasta el CENTRO de la ventana
      const k = Math.min(1, this._fjT / 1.6);
      const e2 = 1 - Math.pow(1 - k, 3);
      this._fjZ = F.zIn + (F.zAtk - F.zIn) * e2;
      if (k >= 1) {
        this._fjState = 'ventana';
        this._fjT = 0; this._fjFrame = 0; this._fjFrameT = F.loopT;
        if (this._fjAtk) {
          this._fjDianaPos();
          this.fjDiana.visible = true;
          this._msg = tx('tren_forajido');
          this._msgT = 2.6;
          this.ctrl.sfx('desenfundar', 0);
        }
      }
      this._fjPose(bob);
    } else if (this._fjState === 'ventana') {
      // iguala la velocidad del tren: 4 s a la altura de la ventana
      this._fjZ = F.zAtk;
      if (this._fjT >= F.atkT) {
        this._fjDispara();
        this._fjFuga();
      }
      this._fjPose(bob);
    } else if (this._fjState === 'herido') {
      // galope_herido.png 1 s (se endereza hacia atrás)…
      this._fjZ = F.zAtk + this._fjT * 0.4;
      if (this._fjT >= F.heridoT) {
        this._fjState = 'fade';
        this._fjT = 0;
        if (this._fjFadeMat) this.fjPlane.material = this._fjFadeMat;
      }
      this._fjPose(bob * 0.4);
    } else if (this._fjState === 'fade') {
      // …y la imagen se FUNDE A NEGRO (petición literal del artista)
      const k = Math.min(1, this._fjT / F.fadeT);
      if (this._fjFadeMat) {
        this._fjFadeMat.opacity = 1 - k;
        this._fjFadeMat.color.setScalar(1 - k * 0.92);
      }
      this._fjPose(0);
      if (k >= 1) this._fjGone();
    } else if (this._fjState === 'fuga') {
      // se va ADELANTANDO y pierde la ventana por delante
      this._fjV = Math.min(F.vPaso * 1.35, this._fjV + 2.6 * dt);
      this._fjZ -= this._fjV * dt;
      if (this._fjZ < F.zOut) return this._fjGone();
      this._fjPose(bob);
    }
  }

  /* ======================================================================
   *  v2.111 · GATILLO del vagón: el revólver de la MANO LIBRE dispara
   *  durante toda la prueba (la pala sigue en la otra mano). El rayo sale
   *  de la boca REAL del cañón (mismo convenio WYSIWYG del duelo) y sólo
   *  cuenta la DIANA del forajido de la ventana.
   *  ====================================================================== */
  trigger(hand) {
    if (this.phase !== 'run' || !this.ctrl._revInHand) return;
    const g = this.game;
    if (((hand | 0) === g.paddleHand) && g.renderer.xr.isPresenting) return;
    const ray = this.ctrl._gunRay();
    if (!ray) return;
    const now = performance.now() / 1000;
    if (now - this._gunLast < 0.16) return;   // disparos libres cada 0,16 s
    this._gunLast = now;
    let len = 8;
    this.ctrl.fx.flash(ray.pos.clone().addScaledVector(ray.dir, 0.02), 1.1, 0xffd98a);
    this.ctrl.sfx('disparo', 0);
    if (g.renderer.xr.isPresenting) g.haptic(1 - g.paddleHand, 0.5, 110);
    if (this._fjState === 'ventana' && this._fjAtk && this.fjDiana.visible) {
      const wp = this.fjDiana.getWorldPosition(new THREE.Vector3());
      const toD = wp.clone().sub(ray.pos);
      const t = clamp(toD.dot(ray.dir), 0, 9);
      const closest = ray.dir.clone().multiplyScalar(t).add(ray.pos);
      if (closest.distanceTo(wp) < TREN.forajido.dianaR) {
        len = Math.max(0.3, t);
        this._fjHerido();
        if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 130);
      }
    }
    if (this.ctrl.fx) this.ctrl.fx.beam(ray.pos, ray.dir, len);
  }

  /* ======================================================================
   *  v2.111 · MÚSICA DEL VAGÓN — vagon.mp3 del artista EN BUCLE mientras
   *  dura la prueba (sustituye a la BSO del saloon: musicOn() se retira
   *  durante la etapa). Mismo canal y volúmenes que la BSO del módulo.
   *  ====================================================================== */
  _musicVol() {
    try {
      const A = this.game.audio;
      if (!A) return 0.15;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return 0.15; }
  }
  _musicStart() {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      this._musWanted = true;
      if (!this._musBuf && !this._musBusy) {
        this._musBusy = true;
        const url = this.ctrl.manifest && this.ctrl.manifest.vagonMusicUrl;
        if (!url) { this._musBusy = false; return; }
        fetch(url)
          .then((r) => r.arrayBuffer())
          .then((ab) => new Promise((res, rej) => {
            try { actx.decodeAudioData(ab, res, rej); } catch (e) { rej(e); }
          }))
          .then((buf) => {
            this._musBuf = buf; this._musBusy = false;
            if (this._musWanted) this._musicPlay();
          })
          .catch(() => { this._musBusy = false; });
      } else if (this._musBuf && !this._mus) {
        this._musicPlay();
      }
    } catch (e) { /* sin música: nunca rompe */ }
  }
  _musicPlay() {
    try {
      if (this._mus || !this._musBuf) return;
      const actx = this.game.audio.ctx;
      const gain = actx.createGain();
      gain.gain.value = this._musicVol();
      gain.connect(actx.destination);
      const src = actx.createBufferSource();
      src.buffer = this._musBuf;
      src.loop = true;
      src.connect(gain);
      src.start();
      this._mus = { gain, src };
    } catch (e) { this._mus = null; }
  }
  _musicSync() {
    if (!this._mus || !this._mus.gain) return;
    try {
      const want = this._musicVol();
      if (Math.abs((this._mus.gain.gain.value || 0) - want) > 0.001) {
        this._mus.gain.gain.value = want;
      }
    } catch (e) { /* */ }
  }
  _musicStop() {
    this._musWanted = false;
    if (this._mus) {
      try { this._mus.src.stop(); } catch (e) { /* */ }
      try { this._mus.gain.disconnect(); } catch (e) { /* */ }
      this._mus = null;
    }
  }
