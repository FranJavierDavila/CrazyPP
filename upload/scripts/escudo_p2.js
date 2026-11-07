
  /* ---------------- ciclo de vida ---------------- */
  start() {
    if (this.active) return;
    this._build();
    this.active = true;
    this.phase = 'prep';
    this.phaseT = ESC_CFG.prepT;
    this.fase = 0;
    this.faseT = 0;
    this.hull = ESC_CFG.hullMax;
    this.sobrecarga = 0;
    this.alerta = false;
    this._presionT = 0;
    this._presionK = 1;
    this.rally = 0;
    this._win = false;
    this._trackLostT = 0;
    this._limpiaOrbes();
    this._msgNova(tx('Comandante, el casco frontal ha sido perforado y la defensa automática está fuera de línea. Active el escudo manual.',
      'Commander, the frontal hull is breached and automated defense is offline. Activate the manual shield.'), ESC_CFG.prepT + 1.2);
    const g = this.game;
    /* ESCENARIO: fuera sala del núcleo, mesa, marcador, rival y recortes */
    if (g.roomGroup) g.roomGroup.visible = false;
    this.grp.visible = true;
    g.tableGroup.visible = false;            // SIN mesa tradicional
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    if (this.ctrl.rivalMesh) {
      this._rivalHome = this._rivalHome || this.ctrl.rivalMesh.position.clone();
      this.ctrl.rivalMesh.visible = false;   // el ASTRO sólo en la derrota
    }
    if (this.ctrl.cartel) this.ctrl.cartel.visible = false;
    if (this.ctrl.powerSign) this.ctrl.powerSign.visible = false;
    try { if (this.ctrl.mapa && this.ctrl.mapa.hide) this.ctrl.mapa.hide(); } catch (e) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = false; } catch (e1) { /* */ }
    /* SIN pelota, SIN base, SIN pistola: sólo la pala (mano libre ociosa) */
    g.ball.ignoreNet = true;
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = false;
    g.ballMesh.scale.setScalar(1);
    try { if (g.trailObj) g.trailObj.visible = false; } catch (e2) { /* */ }
    try { if (g.gunMounts) for (const gm of g.gunMounts) if (gm) gm.visible = false; } catch (e3) { /* */ }
    g.rules.state = 'arkanoid';              // estado genérico de PRUEBA (árbitro duerme)
    g.rules.message = 'ESCUDO DE PALA · DEFENSA DEL CASCO';
    this._hudKey = '';
    g.audio.playOsc(330, 392, 0.12, 'square', 0.11, 0);
    window.setTimeout(() => { try { g.audio.playOsc(494, 523, 0.2, 'square', 0.12, 0); } catch (e4) { /* */ } }, 150);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
  }

  reenter() {
    if (!this.active) return;
    const g = this.game;
    g.rules.state = 'arkanoid';
    if (g.roomGroup) g.roomGroup.visible = false;
    this.grp.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (this.ctrl.rivalMesh && this.phase !== 'result') this.ctrl.rivalMesh.visible = false;
    g.ballMesh.visible = false;
    this._hudKey = '';
  }

  stop() {
    this.active = false;
    this.phase = 'idle';
    if (!this.built) return;
    const g = this.game;
    this._limpiaOrbes();
    this._fxReset();
    this.grp.visible = false;
    /* la sala de la estación vuelve */
    if (g.roomGroup) g.roomGroup.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ball.ignoreNet = false;
    g.ballMesh.scale.setScalar(1);
    g.ballMesh.visible = true;
    try { if (g.trailObj) g.trailObj.visible = g.showTrail !== false; } catch (e) { /* */ }
    g.ball.vel.set(0, 0, 0);
    g.ball.spin.set(0, 0, 0);
    try {
      const D = this.ctrl.D;
      g.ball.pos.set(0, D.tableTopY + (D.ballRadius || 0.02), D.tableCenterZ + 0.45);
      if (g.ball.__exPrev) g.ball.__exPrev.copy(g.ball.pos);
    } catch (e0) { /* */ }
    if (this.ctrl.rivalMesh) {
      if (this._rivalHome) this.ctrl.rivalMesh.position.copy(this._rivalHome);
      this.ctrl.rivalMesh.visible = true;
    }
    try { if (this.ctrl.mapa && this.ctrl.mapa.show) this.ctrl.mapa.show(); } catch (e1) { /* */ }
    try { if (this.ctrl.mapa && this.ctrl.mapa.group) this.ctrl.mapa.group.visible = true; } catch (e2) { /* */ }
  }

  _limpiaOrbes() {
    for (const o of this.orbes) {
      o.alive = false;
      o.mesh.visible = false;
      o.glow.visible = false;
    }
  }

  _fxReset() {
    for (const f of this.flashes) { f.t = 9; f.m.visible = false; }
    for (const f of this.frags) { f.t = 9; f.m.visible = false; }
    for (const w of this.ondas) { w.t = 9; w.m.visible = false; }
    this.luzAlarma.intensity = 0;
    if (this.jefe) { this.jefe.visible = false; this.jefeOn = false; }
    if (this.cent) { this.cent.visible = false; this.centOn = false; }
    if (this.drones) for (const d of this.drones) { d.alive = false; d.grp.visible = false; }
  }

  /* ---------------- bucle de la prueba ---------------- */
  step(dt) {
    if (!this.active) return;
    const g = this.game;
    this._t += dt;
    if (this._msgT > 0) this._msgT -= dt;
    this._hudDirty();
    /* pérdida de tracking de la pala >0,5 s: los drones suspenden el disparo */
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    if (ps && ps.active) this._trackLostT = 0;
    else this._trackLostT += dt;
    const trackOk = this._trackLostT < ESC_CFG.trackTol;

    if (this.phase === 'prep') {
      this.phaseT -= dt;
      this._anims(dt);
      if (this.phaseT <= 0) this._faseArranca(0);
    } else if (this.phase === 'combate') {
      this.faseT += dt;
      /* PRESIÓN CRECIENTE (fases 1-2): tras 90 s, cada 15 s −8 % de cadencia */
      const F = ESC_CFG.fases[this.fase];
      if (F && !F.jefe) {
        if (this.faseT > ESC_CFG.presion.umbral) {
          this._presionT += dt;
          if (this._presionT >= ESC_CFG.presion.paso) {
            this._presionT -= ESC_CFG.presion.paso;
            this._presionK = Math.max(ESC_CFG.presion.minK, this._presionK * (1 - ESC_CFG.presion.reduc));
            this._msgNova(tx('Refuerzos enemigos en camino. Ritmo de fuego creciente.',
              'Enemy reinforcements inbound. Fire rate increasing.'), 2.4);
          }
        }
        /* enemigos */
        for (const d of this.drones) if (d.alive) this._dronStep(d, dt, trackOk);
        if (this.centOn) this._centStep(dt, trackOk);
      } else if (F && F.jefe) {
        this._jefeStep(dt, trackOk);
      }
      /* orbes + FX */
      this._orbesStep(dt);
      if (!this.active) return;              // pudo terminar dentro
      this._anims(dt);
      /* alerta crítica (≤30): luces rojas + alarma suave */
      if (this.hull <= ESC_CFG.alertaUmbral) {
        this.luzAlarma.intensity = 1.15 + Math.sin(this._t * 7) * 0.75;
        this._alarmCd -= dt;
        if (this._alarmCd <= 0) {
          this._alarmCd = 1.4;
          try { g.audio.playOsc(620, 430, 0.34, 'sawtooth', 0.1, 0); } catch (e) { /* */ }
        }
      } else {
        this.luzAlarma.intensity *= Math.max(0, 1 - dt * 5);
      }
    } else if (this.phase === 'inter') {
      this.phaseT -= dt;
      this._orbesStep(dt);                   // sólo disolución residual
      this._anims(dt);
      if (this.phaseT <= 0) this._faseArranca(this.fase + 1);
    } else if (this.phase === 'result') {
      this.phaseT -= dt;
      this._anims(dt);
      if (this.phaseT <= 0) { this._afterResult(); return; }
    }
    this._pantalla();
  }

  /* ---------------- fases (sección 10) ---------------- */
  _faseArranca(i) {
    this.fase = Math.min(i, 2);
    this.phase = 'combate';
    this.faseT = 0;
    this._presionT = 0;
    this._presionK = 1;
    this.rally = 0;
    const g = this.game;
    const F = ESC_CFG.fases[this.fase];
    if (F.jefe) {
      /* FASE 3: la nave abordadora se acopla en la brecha (entrada 4 s) */
      this.jefeOn = true;
      this.jefeEntrT = ESC_CFG.jefe.entradaT;
      this.jefeCanon = -1;
      this.jefeCanonT = 0;
      this.jefe.visible = true;
      this.jefe.position.set(0, ESC_CFG.jefe.y, ESC_CFG.room.fz - 4.5);
      this.jefe.getChildByName && null;
      for (const c of this.canones) { c.grp.visible = !c.dead; c.volT = 0; c.cola.length = 0; }
      this._msgNova(tx('Nave abordadora acoplándose. Destruya sus cañones.',
        'Boarding ship docking. Destroy its cannons.'), 4.4);
      try { g.audio.announce(tx('Nave abordadora detectada', 'Boarding ship detected'), true); } catch (e) { /* */ }
    } else {
      /* FASES 1-2: drones artilleros (+ Centinela en la fase 2) */
      for (let k = 0; k < F.drones; k++) {
        const d = this.drones[k];
        d.alive = true;
        d.grp.visible = true;
        d.grp.scale.setScalar(0.01);
        this._dronSpot(d, true);
        d.movT = ESC_CFG.droneMovT * (0.6 + Math.random() * 0.8);
        d.shootT = ESC_CFG.fases[this.fase].cadencia * (1 + Math.random() * 0.5);
        d.chargeT = 9;
      }
      this.centOn = !!F.centinela;
      this.centDead = false;
      if (this.centOn) {
        this.cent.visible = true;
        this.cent.position.set(0, ESC_CFG.cent.y, ESC_CFG.cent.z);
        this.centShield.material.opacity = 0.62;
        this.centCore.material.emissiveIntensity = 0.25;
        this.centSobreT = 0;
        this.centShootT = ESC_CFG.cent.disparaCada;
        this.centChargeT = 9;
      }
      const nombres = ['Drones de abordaje detectados. Devuelva sus disparos.',
        'Nuevos tipos de munición detectados. Los torpedos pesados exigen un golpe firme.'];
      this._msgNova(tx(nombres[this.fase] || '', nombres[this.fase] || ''), 4.2);
      try { g.audio.announce(tx('Fase ' + (this.fase + 1), 'Phase ' + (this.fase + 1)), true); } catch (e0) { /* */ }
    }
    this._hudKey = '';
  }

  /** Fin de fase: limpia enemigos y orbes con disolución visual (sección 14). */
  _faseCompleta() {
    const g = this.game;
    /* disolución: los drones vivos restantes (si los hubiera) se apagan */
    for (const d of this.drones) if (d.alive) { d.alive = false; d.grp.visible = false; }
    if (this.centOn) { this.centOn = false; this.cent.visible = false; }
    for (const o of this.orbes) if (o.alive) this._orbMuere(o, true);
    if (this.fase >= 2) { this._finish(true); return; }
    this.phase = 'inter';
    this.phaseT = ESC_CFG.interT;
    const antes = this.hull;
    this.hull = Math.min(ESC_CFG.hullMax, this.hull + ESC_CFG.interRegen);
    if (this.hull > ESC_CFG.alertaUmbral) this.alerta = false;
    this._msgNova(tx('Reparaciones de emergencia en curso. Integridad restaurada parcialmente (+' +
      Math.round(this.hull - antes) + ' %).',
      'Emergency repairs underway. Integrity partially restored (+' + Math.round(this.hull - antes) + ' %).'),
      ESC_CFG.interT);
    g.confettiBurst = 0;
    g.audio.fanfare(true);
    if (g.renderer.xr.isPresenting) {
      g.haptic(g.paddleHand, 0.7, 130);
      window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.4, 110); } catch (e) { /* */ } }, 200);
    }
    this._hudKey = '';
  }

  /* ---------------- final: victoria y derrota (sección 14) ---------------- */
  _finish(win) {
    const g = this.game;
    const a = this.ctrl;
    this.phase = 'result';
    this.phaseT = win ? ESC_CFG.jefe.explodeT + 1.4 : 4.2;
    this._win = win;
    this.jefeOn = false;
    this.centOn = false;
    if (win) {
      /* EL JEFE EXPLOTA (secuencia ~4 s): flashes + fragmentos + sacudida */
      this._jefeExplosion();
      this._msgNova(tx('Amenaza neutralizada. Buen trabajo, comandante.',
        'Threat neutralized. Good work, commander.'), this.phaseT);
      if (a._replay) {
        this._banner = { title: '¡CASCO DEFENDIDO!', sub: 'Rejugada terminada', col: '#7fb069' };
        try { g.audio.announce('Rejugada terminada', true); } catch (e) { /* */ }
      } else {
        a._pruebaFin(true);
        const sig = CFG.etapas[Math.min(a.stage, CFG.etapas.length - 1)];
        this._banner = {
          title: '¡CASCO DEFENDIDO!',
          sub: 'Siguiente: ' + sig.name, col: '#7fb069',
        };
        try { g.audio.announce(this._banner.sub, true); } catch (e0) { /* */ }
      }
      g.confettiBurst = 3;
      g.audio.fanfare(true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(g.paddleHand, 0.8, 140);
        window.setTimeout(() => { try { g.haptic(g.paddleHand, 0.5, 130); } catch (e1) { /* */ } }, 220);
      }
    } else {
      /* DERROTA: casco a 0 — alarma, mensaje, ASTRO riéndose y regreso */
      this._msgNova(tx('Casco comprometido…', 'Hull compromised…'), this.phaseT);
      this._banner = { title: '¡CASCO COMPROMETIDO!', sub: 'La defensa ha caído', col: '#e06c5a' };
      g.audio.fanfare(false);
      try { g.audio.announce(tx('Casco comprometido', 'Hull compromised'), true); } catch (e2) { /* */ }
      a._pruebaFin(false);
      if (a.rivalMesh) {
        a.rivalMesh.position.set(0, 1.075, -2.1);
        a.rivalMesh.visible = true;
        a.rivalEstado('laughing');       // astro_laughing, única aparición
      }
      this.luzAlarma.intensity = 1.6;
    }
    this._limpiaOrbes();
    this._hudKey = '';
  }

  _afterResult() {
    const a = this.ctrl;
    this.stop();
    a._despuesDePrueba();
  }
