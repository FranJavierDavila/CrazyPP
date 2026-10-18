
  /* ---------------- orbes de plasma (sección 8) ---------------- */
  _orbLibre() {
    for (const o of this.orbes) if (!o.alive) return o;
    return null;
  }

  /** Lanza un orbe enemigo desde `from` (dron/cañón/centinela). Con
   *  abanico ≠ null desvía el rumbo ±ángulo (patrón del cañón derecho). */
  _orbSpawn(tipo, from, abanico, owner) {
    const o = this._orbLibre();
    if (!o) return;
    const g = this.game;
    const T = ESC_CFG.orb[tipo] || ESC_CFG.orb.std;
    o.alive = true;
    o.owner = 'enemigo';
    o.tipo = tipo;
    o.r = T.r;
    o.mesh.scale.setScalar(T.r);
    o.glow.scale.setScalar(T.r * 7);
    o.mat.color.setHex(T.col);
    o.mat.emissive.setHex(T.col);
    o.glow.material.color.setHex(T.col);
    o.mesh.visible = true;
    o.glow.visible = true;
    o.mesh.position.copy(from);
    o.mesh.position.z += 0.34;               // boca del dron/cañón
    o.prev.copy(o.mesh.position);
    o.vel.set(0, 0, 0);
    o.lifeT = 0;
    o.dist = 0;
    o.fuse = tipo === 'inest' ? ESC_CFG.orb.inest.fusible : -1;
    o.spinS = tipo === 'rotor' ? (Math.random() < 0.5 ? -1 : 1) : 0;
    o.clean = false;
    o.perf = false;
    o.rebote = false;
    o.blink = 0;
    /* objetivo: punto aleatorio de la zona de ataque, FUERA de la zona
     * segura de cabeza (cilindro de 0,35 m alrededor de la cabeza) */
    g.camera.getWorldPosition(this._tmpC);
    const H = ESC_CFG.headSafeR + T.r + 0.12;
    let tx = 0, ty = 1.2;
    for (let i = 0; i < 10; i++) {
      tx = (Math.random() * 2 - 1) * ESC_CFG.ataque.xMax;
      ty = ESC_CFG.ataque.yMin + Math.random() * (ESC_CFG.ataque.yMax - ESC_CFG.ataque.yMin);
      const dx = tx - this._tmpC.x, dy = ty - this._tmpC.y;
      if (dx * dx + dy * dy > H * H) break;
      tx = (tx >= 0 ? 1 : -1) * ESC_CFG.ataque.xMax;   // borde lateral: seguro
      break;
    }
    this._tmpA.set(tx, ty, 0).sub(o.mesh.position).normalize();
    if (abanico) {                            // abanico ±12° del cañón derecho
      const a = abanico * Math.PI / 180;
      const cs = Math.cos(a), sn = Math.sin(a);
      this._tmpB.set(this._tmpA.x * cs - this._tmpA.z * sn, this._tmpA.y,
        this._tmpA.x * sn + this._tmpA.z * cs);
      this._tmpA.copy(this._tmpB);
    }
    const F = ESC_CFG.fases[this.fase];
    let v = T.v;
    if (tipo === 'std') v = T.v[Math.min(this.fase, 2)];
    o.vel.copy(this._tmpA).multiplyScalar(v);
    try { g.audio.playOsc(500, 180, 0.09, 'square', 0.12, 0); } catch (e) { /* */ }
    this._hudKey = '';
  }

  _orbesStep(dt) {
    const SUB = 4, h = dt / SUB;
    for (const o of this.orbes) {
      if (!o.alive) continue;
      for (let s = 0; s < SUB && o.alive; s++) {
        o.prev.copy(o.mesh.position);
        /* ROTOR: trayectoria curvada (hasta 0,6 m en el recorrido) */
        if (o.spinS) {
          this._tmpA.set(-o.vel.z, 0, o.vel.x).normalize()
            .multiplyScalar(ESC_CFG.orb.rotor.curvaAcc * o.spinS * h);
          o.vel.add(this._tmpA);
        }
        o.mesh.position.addScaledVector(o.vel, h);
        o.lifeT += h;
        o.dist += o.vel.length() * h;
        /* INESTABLE: fusible 2,5 s con pulso cada vez más rápido */
        if (o.fuse >= 0) {
          o.fuse -= h;
          const k = 1 - Math.max(0, o.fuse) / ESC_CFG.orb.inest.fusible;
          o.blink += h * (5 + k * 26);
          o.mat.emissiveIntensity = 1.2 + (Math.sin(o.blink) > 0 ? k * 1.8 : 0);
          o.glow.material.opacity = 0.45 + (Math.sin(o.blink) > 0 ? 0.35 : 0);
          if (o.fuse <= 0) { this._orbExplota(o); break; }
        }
        /* vida: 8 s o 25 m */
        if (o.lifeT > ESC_CFG.vidaOrbe || o.dist > ESC_CFG.distOrbe) { this._orbMuere(o); break; }
        /* PALA: barrido del segmento prev→cur (esfera de la pala) */
        if (o.owner === 'enemigo' || true) this._paddleHit(o);
        if (!o.alive) break;
        /* COLISIONES por dueño */
        if (o.owner === 'enemigo') this._impactsEnemigo(o);
        else this._impactsJugador(o);
      }
      if (o.alive) {
        o.glow.position.copy(o.mesh.position);
        o.mesh.rotation.y += 0.1;
      }
    }
  }

  /** Golpe de la PALA: barrido esfera–pala por subpaso (CCD, sección 8).
   *  Aplica la física habitual (reflejo + velocidad de la pala — patrón
   *  REACTOR aprobado) SIN corregir dirección; valida limpio/perforante. */
  _paddleHit(o) {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (!ps || !ps.active || !ps.pos) return;
    const rr = 0.085 + o.r + (ps.extraReach || 0);
    /* punto más cercano del segmento prev→cur al centro de la pala */
    this._tmpA.copy(o.mesh.position).sub(o.prev);
    const dist2 = this._tmpA.lengthSq();
    let t = 0;
    if (dist2 > 1e-9) {
      this._tmpB.copy(ps.pos).sub(o.prev);
      t = Math.max(0, Math.min(1, this._tmpB.dot(this._tmpA) / dist2));
    }
    this._tmpC.copy(o.prev).addScaledVector(this._tmpA, t);
    if (this._tmpC.distanceToSquared(ps.pos) > rr * rr) return;
    if (this._cdO === o && this._cdT > 0) return;    // anti-rebote del mismo contacto
    this._cdO = o; this._cdT = 0.22;
    const n = this._tmpC.sub(ps.pos);
    if (n.lengthSq() < 1e-6) n.set(0, 0.2, -1);
    n.normalize();
    /* velocidad relativa normal ANTES del golpe (para limpio/perforante) */
    this._tmpB.copy(o.vel).sub(ps.vel || this._tmpB.set(0, 0, 0));
    const closing = -this._tmpB.dot(n);
    const hitPoint = this._tmpC.copy(ps.pos).addScaledVector(n, rr);
    /* física de rebote (la pala manda) */
    const rest = o.tipo === 'pesado' ? (ESC_CFG.orb.pesado.restit) : 0.42;
    const into = o.vel.dot(n);
    if (into < 0) o.vel.addScaledVector(n, -2 * into * (1 - rest * 0.55));
    o.vel.multiplyScalar(rest > 0 ? 1 - rest * 0.45 : 0.58);
    if (ps.vel) o.vel.addScaledVector(ps.vel, 0.85);
    const sp = o.vel.length();
    if (sp < ESC_CFG.devMin) o.vel.multiplyScalar(ESC_CFG.devMin / Math.max(sp, 0.01));
    else if (sp > ESC_CFG.devMax) o.vel.multiplyScalar(ESC_CFG.devMax / sp);
    const spAntes = o.vel.length();
    /* GOLPE LIMPIO: punto de contacto en la zona dulce + ≥4 m/s normales */
    let clean = false;
    if (this._bladeRefs && this._bladeRefs[g.paddleHand]) {
      this._bladeRefs[g.paddleHand].getWorldPosition(this._tmpA);
      if (this._tmpA.distanceTo(hitPoint) <= ESC_CFG.sweetR + o.r + 0.02) clean = true;
    }
    if (clean && closing < ESC_CFG.cleanV) clean = false;
    /* SOBRECARGA completa + golpe ≥3 m/s → ORBE PERFORANTE (sección 7) */
    if (this.sobrecarga >= 1 && closing >= ESC_CFG.perforanteV) {
      o.perf = true;
      o.clean = true;
      this.sobrecarga = 0;
      o.mat.color.setHex(0xffe27a);
      o.mat.emissive.setHex(0xffe27a);
      o.glow.material.color.setHex(0xffe27a);
      o.vel.multiplyScalar(1.12);
      this._flash(hitPoint, 0xffe27a, 1.5);
      this._msgNova(tx('¡ORBE PERFORANTE! Atravesará todo núcleo en su camino.',
        'PIERCING ORB! It will pierce every core in its path.'), 2.4);
      try { g.audio.playOsc(880, 1400, 0.22, 'sawtooth', 0.2, 0); } catch (e) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 160);
    } else if (clean) {
      o.clean = true;
      this.sobrecarga = Math.min(1, this.sobrecarga + ESC_CFG.cleanBonus);
      if (this.sobrecarga >= 1) {
        this._msgNova(tx('PALA CARGADA: el próximo golpe firme lanza un orbe perforante.',
          'PADDLE CHARGED: the next firm hit fires a piercing orb.'), 3);
        try { g.audio.playOsc(700, 1050, 0.18, 'square', 0.18, 0); } catch (e0) { /* */ }
      }
      this._flash(hitPoint, 0xffd257, 0.9);
      try { g.audio.playOsc(760, 1180, 0.07, 'square', 0.18, 0); } catch (e1) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.62, 80);
    } else {
      o.clean = false;
      /* golpe válido (sucio): también devuelve el orbe */
      this._flash(hitPoint, 0x9fe8ff, 0.6);
      try { g.audio.playOsc(430, 620, 0.06, 'square', 0.2, 0); } catch (e2) { /* */ }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.45, 60);
    }
    o.owner = 'jugador';
    o.rebote = o.rebote && false;              // se contabiliza abajo
    if (this._eraRebote && o === this._eraRebote) { o.rebote = true; this._eraRebote = null; }
    o.lifeT = 0;
    o.dist = 0;
    this._hudKey = '';
    /* rally: un rebote del Centinela que vuelvo a devolver suma (sección 9.2) */
    if (o.rebote) {
      o.rebote = false;
      if (this.centOn) this._rallySube();
    }
  }

  _rallySube() {
    this.rally++;
    this._hudKey = '';
    if (this.rally >= ESC_CFG.cent.rallyParaAbrir) {
      this.rally = 0;
      this.centSobreT = ESC_CFG.cent.sobreT;
      this.centShield.material.opacity = 0.14;
      this._flash(this.cent.position, 0x35ff9d, 1.4);
      this._msgNova(tx('¡Escudo del Centinela sobrecalentado! Núcleo expuesto.',
        'Sentinel shield overheated! Core exposed.'), 2.6);
      try { this.game.audio.playOsc(700, 900, 0.2, 'square', 0.2, 0); } catch (e) { /* */ }
    }
  }

  /* impactos de orbes ENEMIGOS: barrera de casco (único objetivo) */
  _impactsEnemigo(o) {
    const g = this.game;
    const R = ESC_CFG.room;
    if (o.mesh.position.z >= ESC_CFG.barrera.z - o.r) {
      /* ONDA visible en el punto exacto de impacto (sección 4) */
      this._onda(o.mesh.position);
      const T = ESC_CFG.orb[o.tipo] || ESC_CFG.orb.std;
      this._cascoDano(o.tipo === 'inest' ? ESC_CFG.orb.inest.danoExp : T.dano);
      this._orbMuere(o);
      return;
    }
    if (o.mesh.position.z > R.bz || o.mesh.position.z < R.fz ||
        Math.abs(o.mesh.position.x) > R.hx || o.mesh.position.y > R.hh ||
        o.mesh.position.y < 0.05) {
      this._orbMuere(o);                     // fuera del volumen: se disipa
    }
  }

  /* impactos de orbes DEVUELTOS: enemigos, escudo del Centinela, jefe */
  _impactsJugador(o) {
    const g = this.game;
    const R = ESC_CFG.room;
    const sp = o.vel.length();
    /* DRONES: destrucción por colisión válida (núcleo 0,3 m; el pesado a
     * ≥8 m/s derriba con el cuerpo). Un orbe ENEMIGO nunca daña a drones. */
    for (const d of this.drones) {
      if (!d.alive) continue;
      let hitR = 0.3 + o.r;
      if (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.derribaV) hitR = 0.55 + o.r;
      if (o.perf) hitR = 0.44 + o.r;
      this._tmpA.copy(o.mesh.position).sub(d.pos);
      if (this._tmpA.lengthSq() > hitR * hitR) continue;
      this._dronMuere(d);
      if (!o.perf) { this._orbMuere(o); return; }   // el perforante atraviesa
      continue;
    }
    /* CENTINELA: escudo (rebote) o núcleo (expuesto / pesado 14+ / perforante) */
    if (this.centOn) {
      const cen = this.cent.position;
      if (this.centSobreT <= 0) {
        /* escudo cerrado: plano del cuenco a +0,45 del centro */
        const planoZ = cen.z + 0.45;
        if (o.prev.z > planoZ && o.mesh.position.z <= planoZ) {
          const f = (o.prev.z - planoZ) / Math.max(1e-6, o.prev.z - o.mesh.position.z);
          const hx = o.prev.x + (o.mesh.position.x - o.prev.x) * f;
          const hy = o.prev.y + (o.mesh.position.y - o.prev.y) * f;
          const dx = hx - cen.x, dy = hy - cen.y;
          if (dx * dx + dy * dy <= (ESC_CFG.cent.shieldR + o.r) * (ESC_CFG.cent.shieldR + o.r)) {
            const atraviesa = (o.perf ||
              (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.atraviesaV));
            if (!atraviesa) {
              this._eraRebote = o;
              o.mesh.position.set(hx, hy, planoZ + 0.02);
              this._centRebota(o);
              return;
            }
            /* el pesado a ≥14 m/s y el perforante ATRAVIESAN el escudo */
          }
        }
      }
      /* núcleo */
      this._tmpA.copy(o.mesh.position).sub(cen);
      const coreR = ESC_CFG.cent.coreR + o.r;
      if (this._tmpA.lengthSq() <= coreR * coreR &&
          (this.centSobreT > 0 || o.perf ||
           (o.tipo === 'pesado' && sp >= ESC_CFG.orb.pesado.atraviesaV))) {
        this._centMuere();
        if (!o.perf) { this._orbMuere(o); return; }
      }
    }
    /* JEFE: cañones — sólo el ACTIVO recibe daño; los cerrados son inmunes
     * (incluso el perforante: está protegido, sección 19). */
    if (this.jefeOn && this.jefeCanon >= 0) {
      for (let i = 0; i < 3; i++) {
        const c = this.canones[i];
        if (c.dead || i !== this.jefeCanon) continue;
        this._tmpA.copy(o.mesh.position).sub(c.grp.position);
        const hitR = ESC_CFG.jefe.canonR + o.r;
        if (this._tmpA.lengthSq() > hitR * hitR) continue;
        const dano = o.perf ? ESC_CFG.jefe.perforanteDano && 2 : (o.clean ? 2 : 1);
        this._jefeCanonDano(c, Math.min(2, o.perf ? 2 : (o.clean ? 2 : 1)), o.clean && !o.perf);
        if (!o.perf) { this._orbMuere(o); return; }
        continue;                              // el perforante sigue
      }
    }
    /* paredes: orbe devuelto que no impacta nada se disipa al llegar a la
     * pared del frente; si llega a la BARRERA, falla y el rally cae a 0. */
    if (o.mesh.position.z <= R.fz + o.r) { this._orbMuere(o); return; }
    if (o.mesh.position.z >= ESC_CFG.barrera.z - o.r) {
      if (this.rally > 0) { this.rally = 0; this._hudKey = ''; }
      this._orbMuere(o);
      return;
    }
    if (o.mesh.position.z > R.bz || Math.abs(o.mesh.position.x) > R.hx ||
        o.mesh.position.y > R.hh || o.mesh.position.y < 0.05) this._orbMuere(o);
  }

  _cascoDano(dano) {
    const g = this.game;
    this.hull = Math.max(0, this.hull - dano);
    if (this.hull <= ESC_CFG.alertaUmbral && !this.alerta) {
      this.alerta = true;
      this._msgNova(tx('ALERTA CRÍTICA: integridad del casco al ' + this.hull + ' %.',
        'CRITICAL ALERT: hull integrity at ' + this.hull + ' %.'), 2.8);
    }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.85, 150);
    this._hudKey = '';
    if (this.hull <= 0 && this.phase === 'combate') this._finish(false);
  }

  /** El orbe INESTABLE explota (fusible): radio 1,5 m — destruye drones
   *  cercanos (cada uno una vez); si es enemigo y explota a <2 m del
   *  jugador, daña el casco. Sólo efectos visuales en el resto. */
  _orbExplota(o) {
    const g = this.game;
    const E = ESC_CFG.orb.inest;
    this._flash(o.mesh.position, 0xff6a4d, 2.2);
    try { g.audio.playNoise(0.5, 180, 0.5, 0.22, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(180, 60, 0.35, 'sawtooth', 0.16, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 110);
    for (const d of this.drones) {
      if (!d.alive) continue;
      if (d.pos.distanceTo(o.mesh.position) <= E.radioExp + 0.3) this._dronMuere(d);
    }
    if (o.owner === 'enemigo') {
      g.camera.getWorldPosition(this._tmpA);
      if (this._tmpA.distanceTo(o.mesh.position) < E.cercaJugador ||
          o.mesh.position.z >= ESC_CFG.barrera.z) {
        this._onda(o.mesh.position);
        this._cascoDano(E.danoExp);
      }
    }
    this._orbMuere(o);
  }

  _orbMuere(o, disolv) {
    o.alive = false;
    o.mesh.visible = false;
    o.glow.visible = false;
    if (this._cdO === o) { this._cdO = null; }
    if (this._eraRebote === o) this._eraRebote = null;
    if (disolv) this._flash(o.mesh.position, 0x9fe8ff, 0.5);
  }

  /* ---------------- FX (pools, exclusivamente visuales) ---------------- */
  _flash(p, col, size) {
    for (const f of this.flashes) {
      if (f.t < 0.4) continue;
      f.t = 0;
      f.m.visible = true;
      f.m.position.copy(p);
      f.m.material.color.setHex(col);
      f.m.scale.setScalar(size);
      f.m.material.opacity = 0.9;
      f.m.quaternion.copy(this.game.camera.quaternion);
      return;
    }
  }

  _frags(p, n, col) {
    let usados = 0;
    for (const f of this.frags) {
      if (usados >= n) break;
      if (f.t < 0.95) continue;
      f.t = 0;
      usados++;
      f.m.visible = true;
      f.m.position.copy(p);
      f.m.material.color.setHex(col);
      f.m.material.emissive.setHex(col);
      f.m.material.opacity = 1;
      f.vel.set((Math.random() - 0.5) * 3.2, Math.random() * 2.6, (Math.random() - 0.5) * 3.2);
    }
  }

  /** Onda de la Barrera de Casco en el punto exacto del impacto. */
  _onda(p) {
    for (const w of this.ondas) {
      if (w.t < 0.55) continue;
      w.t = 0;
      w.m.visible = true;
      w.m.position.set(p.x, Math.max(0.5, Math.min(3.4, p.y)), ESC_CFG.barrera.z + 0.06);
      w.m.material.opacity = 0.85;
      w.m.scale.setScalar(0.2);
      return;
    }
  }

  _anims(dt) {
    for (const f of this.flashes) {
      if (f.t > 0.4) continue;
      f.t += dt;
      f.m.material.opacity = Math.max(0, 0.9 * (1 - f.t / 0.4));
      f.m.scale.multiplyScalar(1 + dt * 3.4);
      if (f.t >= 0.4) f.m.visible = false;
    }
    for (const f of this.frags) {
      if (f.t > 0.95) continue;
      f.t += dt;
      f.vel.y -= 2.6 * dt;                   // gravedad suave de escombros
      f.m.position.addScaledVector(f.vel, dt);
      f.m.material.opacity = Math.max(0, 1 - f.t / 0.95);
      f.m.rotation.x += dt * 6; f.m.rotation.y += dt * 4;
      if (f.t >= 0.95) f.m.visible = false;
    }
    for (const w of this.ondas) {
      if (w.t > 0.55) continue;
      w.t += dt;
      const k = w.t / 0.55;
      w.m.scale.setScalar(0.2 + k * 2.6);
      w.m.material.opacity = 0.85 * (1 - k);
      if (w.t >= 0.55) w.m.visible = false;
    }
    /* plataforma y barrera respiran */
    this.plataforma.children[0].material.opacity = 0.42 + Math.sin(this._t * 2.4) * 0.16;
    this.barreraMat.opacity = 0.30 + Math.sin(this._t * 3.1) * 0.07;
    /* pulso del cañón activo del jefe */
    if (this.jefeOn && this.jefeCanon >= 0) {
      const tip = this.canones[this.jefeCanon].tip;
      tip.material.emissiveIntensity = 1.5 + Math.sin(this._t * 8) * 0.45;
    }
    /* glow de PALA CARGADA flotando junto a la hoja */
    if (this.sobrecarga >= 1 && this._bladeRefs && this._bladeRefs[this.game.paddleHand]) {
      this._bladeRefs[this.game.paddleHand].getWorldPosition(this._tmpA);
      if (!this.cargaGlow) {
        this.cargaGlow = new THREE.Sprite(new THREE.SpriteMaterial({
          map: this._glowTex(), color: 0xffe27a, transparent: true, opacity: 0.85,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }));
        this.cargaGlow.renderOrder = 30;
        this.game.scene.add(this.cargaGlow);
      }
      this.cargaGlow.visible = true;
      this.cargaGlow.position.copy(this._tmpA);
      this.cargaGlow.scale.setScalar(0.3 + Math.sin(this._t * 6) * 0.06);
    } else if (this.cargaGlow) {
      this.cargaGlow.visible = false;
    }
  }
