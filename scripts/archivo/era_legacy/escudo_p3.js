
  /* ---------------- drones artilleros (sección 9.1) ---------------- */
  _dronSpot(d, init) {
    const Z = ESC_CFG.despliegue;
    for (let i = 0; i < 24; i++) {
      const x = (Math.random() * 2 - 1) * Z.xMax;
      const y = Z.yMin + Math.random() * (Z.yMax - Z.yMin);
      const z = Z.zMin + Math.random() * (Z.zMax - Z.zMin);
      let ok = true;
      for (const o of this.drones) {
        if (!o.alive || o === d) continue;
        if (o.pos.distanceToSquared(this._tmpA.set(x, y, z)) < ESC_CFG.droneMinSep * ESC_CFG.droneMinSep) { ok = false; break; }
      }
      if (ok) {
        if (init) d.pos.set(x, y, z);
        else { d.from.copy(d.pos); d.spot.set(x, y, z); d.movD = 0; }
        return;
      }
    }
    if (init) d.pos.set(0, 2, -8);
    else { d.from.copy(d.pos); d.spot.copy(d.pos); }
  }

  _dronStep(d, dt, trackOk) {
    const g = this.game;
    /* deriva + reposición cada 8 s (lerp suave hacia el nuevo spot) */
    d.thud += dt;
    d.grp.position.y += Math.sin(d.thud * 1.6) * dt * 0.05;
    d.grp.rotation.y += dt * 0.7;
    if (d.movD < 1) {
      d.movD = Math.min(1, d.movD + dt / 1.6);
      const e = d.movD * d.movD * (3 - 2 * d.movD);
      d.grp.position.lerpVectors(d.from, d.spot, e);
    } else {
      d.movT -= dt;
      if (d.movT <= 0) {
        d.movT = ESC_CFG.droneMovT * (0.7 + Math.random() * 0.6);
        this._dronSpot(d, false);
      }
    }
    /* escala de aparición */
    if (d.grp.scale.x < 1) d.grp.scale.setScalar(Math.min(1, d.grp.scale.x + dt * 1.8));
    /* TELEGRAFÍA 0,8 s (anillo de carga + sonido espacial) y disparo */
    if (d.chargeT < 9) {
      d.chargeT -= dt;
      const k = 1 - Math.max(0, d.chargeT) / ESC_CFG.telegrafT;
      d.aro.material.emissiveIntensity = 0.4 + k * 2.2;
      d.aro.scale.setScalar(1 + Math.sin(this._t * (8 + k * 22)) * 0.06 * (1 - k) + k * 0.25);
      if (d.chargeT <= 0) {
        d.chargeT = 9;
        d.aro.material.emissiveIntensity = 0;
        d.aro.scale.setScalar(1);
        this._orbSpawn(d.tipo, d.pos, null, 'enemigo');
      }
    } else {
      d.shootT -= dt * (trackOk ? 1 : 0);       // sin tracking: sin disparos
      if (d.shootT <= 0 && trackOk) {
        if (this._orbesEnemigos() >= (ESC_CFG.fases[this.fase].maxOrbes || 3)) {
          d.shootT = 0.5;                       // tope de orbes: espera
        } else {
          d.shootT = ESC_CFG.fases[this.fase].cadencia * this._presionK;
          d.tipo = this._tipoOrbe();
          d.chargeT = ESC_CFG.telegrafT;
          try { g.audio.playOsc(240, 340, ESC_CFG.telegrafT * 0.8, 'sine', 0.07, 0); } catch (e) { /* */ }
        }
      }
    }
  }

  _orbesEnemigos() {
    let n = 0;
    for (const o of this.orbes) if (o.alive && o.owner === 'enemigo') n++;
    return n;
  }

  _tipoOrbe() {
    const mix = ESC_CFG.fases[this.fase].mix;
    const r = Math.random();
    if (r < (mix.pesado || 0)) {
      /* NUNCA dos orbes pesados a la vez (sección 10) */
      for (const o of this.orbes) if (o.alive && o.owner === 'enemigo' && o.tipo === 'pesado') return 'std';
      return 'pesado';
    }
    if (r < (mix.pesado || 0) + (mix.rotor || 0)) return 'rotor';
    return 'std';
  }

  /* ---------------- Centinela (sección 9.2) ---------------- */
  _centStep(dt, trackOk) {
    const g = this.game;
    this.cent.rotation.y = Math.sin(this._t * 0.8) * 0.18;
    this.cent.position.y = ESC_CFG.cent.y + Math.sin(this._t * 1.3) * 0.12;
    if (this.centSobreT > 0) {
      /* ESCUDO ABIERTO (sobrecalentamiento): núcleo expuesto 3 s */
      this.centSobreT -= dt;
      this.centShield.material.opacity = 0.14;
      this.centCore.material.emissiveIntensity = 1.4 + Math.sin(this._t * 12) * 0.5;
      if (this.centSobreT <= 0) {
        this.centShield.material.opacity = 0.62;
        this.centCore.material.emissiveIntensity = 0.25;
        this.rally = 0;                     // cerró sin impacto: rally a 0
        this._hudKey = '';
      }
    }
    /* sus propios orbes estándar cada 4 s */
    if (this.centChargeT < 9) {
      this.centChargeT -= dt;
      if (this.centChargeT <= 0) {
        this.centChargeT = 9;
        this._orbSpawn('std', this.cent.position, null, 'enemigo');
      }
    } else {
      this.centShootT -= dt * (trackOk ? 1 : 0);
      if (this.centShootT <= 0 && trackOk &&
          this._orbesEnemigos() < (ESC_CFG.fases[this.fase].maxOrbes || 4)) {
        this.centShootT = ESC_CFG.cent.disparaCada;
        this.centChargeT = ESC_CFG.telegrafT;
        try { g.audio.playOsc(200, 300, ESC_CFG.telegrafT * 0.8, 'sine', 0.07, 0); } catch (e) { /* */ }
      }
    }
  }

  /** El escudo del Centinela devuelve el orbe: 70 % reflexión física +
   *  30 % hacia el jugador, +10 % de velocidad (tope 20 m/s). */
  _centRebota(o) {
    const sp = o.vel.length();
    this._tmpA.copy(o.vel).normalize();
    /* reflexión especular sobre el plano del escudo (normal +Z) */
    this._tmpA.z = Math.abs(this._tmpA.z);
    this._tmpA.normalize().multiplyScalar(sp);
    /* 30 % de sesgo hacia el jugador */
    this._tmpB.set(0, 1.55, 0.2).sub(o.mesh.position).normalize()
      .multiplyScalar(sp * ESC_CFG.cent.sesgoJugador);
    this._tmpA.add(this._tmpB);
    const v = Math.min(ESC_CFG.cent.velMax, sp * ESC_CFG.cent.velGain);
    o.vel.copy(this._tmpA).normalize().multiplyScalar(v);
    o.owner = 'enemigo';
    o.rebote = true;                         // si lo devuelvo de nuevo: rally++
    o.clean = false;
    o.perf = false;
    o.lifeT = 0;
    o.dist = 0;
    this.rally++;
    this._hudKey = '';
    const g = this.game;
    this._flash(o.mesh.position, 0x66d8ff, 0.55);
    try { g.audio.playOsc(520, 700, 0.07, 'square', 0.16, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.3, 50);
    /* rally completo → SOBRECALENTAMIENTO: escudo abierto 3 s */
    if (this.rally >= ESC_CFG.cent.rallyParaAbrir) {
      this.rally = 0;
      this.centSobreT = ESC_CFG.cent.sobreT;
      this._flash(this.cent.position, 0x35ff9d, 1.3);
      this._msgNova(tx('¡Escudo del Centinela sobrecalentado! Núcleo expuesto.',
        'Sentinel shield overheated! Core exposed.'), 2.6);
      try { g.audio.playOsc(700, 900, 0.2, 'square', 0.2, 0); } catch (e0) { /* */ }
    }
  }

  _centMuere() {
    const g = this.game;
    this.centOn = false;
    this.centDead = true;
    this.cent.visible = false;
    this._frags(this.cent.position, 12, 0x66d8ff);
    this._flash(this.cent.position, 0x9fe8ff, 1.6);
    try { g.audio.playNoise(0.35, 260, 0.4, 0.2, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(320, 140, 0.3, 'sawtooth', 0.18, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.75, 120);
    this._hudKey = '';
    this._compruebaFase();
  }

  /* ---------------- nave abordadora (sección 9.3) ---------------- */
  _jefeStep(dt, trackOk) {
    const g = this.game;
    this.jefe.rotation.z = Math.sin(this._t * 0.9) * 0.02;
    if (this.jefeCanon < 0) {
      /* ENTRADA 4 s: se desliza desde la brecha; no dispara */
      this.jefeEntrT -= dt;
      const k = 1 - Math.max(0, this.jefeEntrT) / ESC_CFG.jefe.entradaT;
      this.jefe.position.z = ESC_CFG.room.fz - 4.5 + k * (ESC_CFG.room.fz - 4.5 - ESC_CFG.jefe.z) * -1;
      this.jefe.position.z = ESC_CFG.room.fz - 4.5 + (ESC_CFG.jefe.z - (ESC_CFG.room.fz - 4.5)) * k;
      if (this.jefeEntrT <= 0) {
        this._canonSiguiente();
      }
      return;
    }
    this.jefeCanonT -= dt;
    const c = this.canones[this.jefeCanon];
    /* PATRONES de disparo del cañón activo (cada 3,5 s) */
    if (trackOk && this._orbesEnemigos() < ESC_CFG.fases[2].maxOrbes) {
      c.volT -= dt;
      if (c.volT <= 0) {
        c.volT = ESC_CFG.jefe.cadencia;
        if (this.jefeCanon === 0) {          // IZQUIERDO: 2 rotor alternados
          c.cola.push({ t: 0, tipo: 'rotor' }, { t: 0.9, tipo: 'rotor' });
        } else if (this.jefeCanon === 1) {   // CENTRAL: pesado + inestable
          c.cola.push({ t: 0, tipo: 'pesado' }, { t: 1.0, tipo: 'inest' });
        } else {                             // DERECHO: abanico de 3 estándar
          c.cola.push({ t: 0, tipo: 'std:0' }, { t: 0.25, tipo: 'std:-1' }, { t: 0.5, tipo: 'std:1' });
        }
        try { g.audio.playOsc(210, 300, ESC_CFG.telegrafT * 0.8, 'sine', 0.08, 0); } catch (e) { /* */ }
      }
      for (let i = c.cola.length - 1; i >= 0; i--) {
        const ev = c.cola[i];
        ev.t -= dt;
        if (ev.t <= 0) {
          c.cola.splice(i, 1);
          if (ev.tipo.startsWith('std:')) {
            this._orbSpawn('std', c.grp.position, parseFloat(ev.tipo.slice(4)), 'enemigo');
          } else {
            this._orbSpawn(ev.tipo, c.grp.position, null, 'enemigo');
          }
        }
      }
    }
    /* ciclo del cañón activo: 8 s → siguiente */
    if (this.jefeCanonT <= 0) this._canonSiguiente();
  }

  _canonSiguiente() {
    this.jefeCanonT = ESC_CFG.jefe.canonT;
    const orden = [0, 1, 2];
    const cur = this.jefeCanon;
    for (const i of orden) {
      if (i === cur) continue;
      const c = this.canones[i];
      if (!c.dead) {
        if (cur >= 0) this.canones[cur].tip.material.emissiveIntensity = 0.15;
        this.jefeCanon = i;
        c.grp.visible = true;
        c.tip.material.emissiveIntensity = 1.7;   // resplandor verde: activo
        c.volT = ESC_CFG.jefe.cadencia;
        c.cola.length = 0;
        this._hudKey = '';
        return;
      }
    }
  }

  _jefeCanonDano(c, dano, clean) {
    const g = this.game;
    c.hp -= dano;
    this._flash(c.grp.position, clean ? 0xffd257 : 0x9fe8ff, clean ? 1.2 : 0.8);
    try { g.audio.playOsc(clean ? 760 : 520, clean ? 980 : 620, 0.08, 'square', 0.2, 0); } catch (e) { /* */ }
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, clean ? 0.7 : 0.5, 90);
    if (c.hp <= 0) {
      c.dead = true;
      c.grp.visible = false;
      this._frags(c.grp.position, 14, 0xffb84d);
      this._flash(c.grp.position, 0xffb84d, 1.8);
      try { g.audio.playNoise(0.4, 220, 0.5, 0.22, 0); } catch (e0) { /* */ }
      if (this.jefeCanon === this.canones.indexOf(c)) this.jefeCanonT = 0;   // pasa al siguiente
      this._hudKey = '';
      this._compruebaFase();
    }
  }

  _jefeExplosion() {
    const g = this.game;
    for (let i = 0; i < 5; i++) {
      const p = this._tmpA.set((Math.random() - 0.5) * 3.6,
        ESC_CFG.jefe.y + (Math.random() - 0.5) * 1.6, ESC_CFG.jefe.z + Math.random());
      this._flash(p, i % 2 ? 0xffb84d : 0x9fe8ff, 1.4 + Math.random());
      this._frags(p, 6, 0xffb84d);
    }
    this.jefe.visible = false;
    this.jefeOn = false;
    try { g.audio.playNoise(0.9, 160, 0.6, 0.26, 0); } catch (e) { /* */ }
    try { g.audio.playOsc(220, 60, 0.8, 'sawtooth', 0.2, 0); } catch (e0) { /* */ }
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 1.0, 300);
      window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.7, 200); } catch (e1) { /* */ } }, 420);
    }
  }

  /** Comprueba si la fase termina (victoria de fase tiene prioridad). */
  _compruebaFase() {
    if (!this.active || this.phase !== 'combate') return;
    const F = ESC_CFG.fases[this.fase];
    if (F.jefe) {
      for (const c of this.canones) if (!c.dead) return;
      this._finish(true);                    // tercer cañón → victoria INMEDIA
    } else {
      for (const d of this.drones) if (d.alive) return;
      if (F.centinela && !this.centDead) return;
      this._faseCompleta();
    }
  }
