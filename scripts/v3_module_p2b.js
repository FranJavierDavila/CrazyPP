
  /* =================================================================
   *  MÁQUINA DE BOLAS Y SAQUE
   *  ================================================================= */
  function resetSessJudge() {
    st.live = false; st.deadT = 0; st.cross = null; st.apex = 0;
    st.hitPos = null; st.bouncePos = null; st.aiBounce = 0; st.shotRec = false;
    st.shotPts.length = 0;
  }
  /** Saque reglamentario de la máquina hacia el jugador (opcionalmente
   *  con efecto real: el solver lo compensa con Magnus incluido). */
  function feedToPlayer(opts) {
    opts = opts || {};
    const b = G.ball;
    G.resetToss();
    b.pos.set(opts.x !== undefined ? opts.x : (Math.random() * 2 - 1) * 0.18,
      1.02, C() - HL() - 0.30);
    let v, sp;
    if (opts.target && opts.spin) {
      // tiro resuelto con efecto REAL (arrastre + Magnus simulados)
      v = computeShotVelocityReal(b.pos, opts.target, opts.tIn || 0.62, opts.max || 8.5, opts.spin);
      sp = opts.spin;
    } else {
      const r = findServeVelocity(b.pos, -1);
      v = r.v; sp = r.spin;
      if (opts.speedMul) v.multiplyScalar(opts.speedMul);
    }
    b.vel.copy(v);
    b.spin.copy(sp || new THREE.Vector3());
    G.audio.serve();
    resetSessJudge();
    st.beat = 0;
  }
  /** Bola en el soporte de saque (fija hasta que el jugador la golpea). */
  function serveTee() {
    const b = G.ball;
    G.resetToss();
    b.pos.set(0.03, TOP() + 0.15, C() + 1.04);
    b.vel.set(0, 0, 0);
    b.spin.set(0, 0, 0);
    resetSessJudge();
    st.phase = 'tee';
  }

  /* ---------------- puntuación y avisos ---------------- */
  function toast(msg, ok) {
    st.toast = msg; st.toastT = 2.1; st.toastOk = !!ok; panelDirty = true;
  }
  function addPts(n) {
    S.pts += n; st.sessPts += n;
    // desbloqueo de skins
    for (const sk of SKINS) {
      if (S.pts >= sk.min && S.unlocked.indexOf(sk.id) < 0) {
        S.unlocked.push(sk.id);
        toast(t('nuevo_skin', { s: sk.name[LANG] || sk.name.es }), true);
        G.audio.playOsc(880, 1560, 0.16, 'triangle', 0.14, 0.12);
      }
    }
    save(); panelDirty = true;
  }
  function recordBest(mode, val) {
    if (!S.best[mode] || val > S.best[mode]) { S.best[mode] = val; save(); }
  }
  function okHit(key, pts) {
    st.streak++; st.done++;
    addPts(pts);
    toast(t(key), true);
    G.audio.playOsc(760, 1180, 0.07, 'sine', 0.13, 0);
    const M = MODES[active];
    const hitGoal = active === 't5a'
      ? (st.rally === 30 || st.rally === 50 || st.rally === 100)
      : (st.streak >= M.n);
    if (hitGoal) {
      const bonus = active === 't5a' ? (st.rally === 30 ? 15 : st.rally === 50 ? 25 : 50) : M.bonus;
      addPts(bonus);
      if (active === 't5a') recordBest(active, st.rally);
      toast(active === 't5a'
        ? t('hito', { n: st.rally, n2: bonus })
        : t('hecho', { n: bonus }), true);
      st.streak = 0; st.done = 0;
      G.audio.playOsc(660, 990, 0.1, 'triangle', 0.14, 0.0);
      G.audio.playOsc(880, 1320, 0.1, 'triangle', 0.14, 0.11);
      G.audio.playOsc(990, 1760, 0.14, 'triangle', 0.14, 0.22);
      if (active === 't1a') st.target = pickTarget();
      if (active === 't5a') { /* el rally continúa: los hitos suman */ }
    }
    if (active !== 't5a') recordBest(active, Math.max(st.streak, S.best[active] || 0));
    st.live = false; st.wait = 0.9; panelDirty = true;
  }
  function failHit(key) {
    st.streak = 0;
    if (active === 't5a' && st.rally > 0) {
      recordBest(active, st.rally);
      toast(t('fin_rally', { n: st.rally }), false);
    } else toast(t(key || 'mal_fuera'), false);
    st.rally = 0;
    G.audio.playOsc(340, 210, 0.12, 'sawtooth', 0.09, 0);
    st.live = false; st.wait = 1.0; panelDirty = true;
  }

  /* ---------------- objetivos y overlay de cada modo ---------------- */
  function pickTarget() {
    // zona dorada: profundas y medias izquierda/derecha (nunca centro)
    const zs = ['deep', 'mid'];
    const z = zs[(Math.random() * zs.length) | 0];
    const x = Math.random() < 0.5 ? -1 : 1;
    return { z, x };
  }
  function drawQuad(mode) {
    const g = quadCtx, W = 512, H = 512;
    g.clearRect(0, 0, W, H);
    const mx = (x) => W / 2 + (x / HW()) * (W / 2);          // x mundo -> lienzo
    const mz = (z) => H * ((C() - z) / HL());                // z mundo -> lienzo (0 = fondo rival)
    if (mode === 't1a') {
      // 6 zonas: profundas/medias/cortas × izq/der + centro prohibido
      const rows = [[C() - HL(), C() - HL() / 2], [C() - HL() / 2, C() - HL() / 4], [C() - HL() / 4, C()]];
      g.lineWidth = 3; g.strokeStyle = 'rgba(255,255,255,0.5)';
      for (const r of rows) {
        g.beginPath(); g.moveTo(mx(-HW()), mz(r[0])); g.lineTo(mx(HW()), mz(r[0])); g.stroke();
        g.beginPath(); g.moveTo(mx(-HW()), mz(r[1])); g.lineTo(mx(HW()), mz(r[1])); g.stroke();
      }
      g.beginPath(); g.moveTo(mx(0), 0); g.lineTo(mx(0), H); g.stroke();
      // centro prohibido (rojo translúcido)
      g.fillStyle = 'rgba(230,70,70,0.24)';
      g.fillRect(mx(-0.15), 0, mx(0.15) - mx(-0.15), H);
      g.fillStyle = 'rgba(255,120,120,0.95)';
      g.font = '700 26px system-ui, sans-serif'; g.textAlign = 'center';
      g.save();
      g.translate(mx(0), H - 26); g.rotate(Math.PI);
      g.fillText('EVITA', 0, 0);
      g.restore();
      // zona objetivo dorada
      if (st.target) {
        const zr = st.target.z === 'deep' ? [C() - HL(), C() - HL() / 2] : [C() - HL() / 2, C() - HL() / 4];
        const xr = st.target.x < 0 ? [-HW(), 0] : [0, HW()];
        g.fillStyle = 'rgba(242,193,78,0.5)';
        g.fillRect(mx(xr[0]), mz(zr[0]), mx(xr[1]) - mx(xr[0]), mz(zr[1]) - mz(zr[0]));
        g.strokeStyle = '#f2c14e'; g.lineWidth = 6;
        g.strokeRect(mx(xr[0]) + 3, mz(zr[0]) + 3, mx(xr[1]) - mx(xr[0]) - 6, mz(zr[1]) - mz(zr[0]) - 6);
        g.fillStyle = '#1a1408'; g.font = '900 64px system-ui, sans-serif';
        g.textAlign = 'center';
        g.save();
        g.translate((mx(xr[0]) + mx(xr[1])) / 2, (mz(zr[0]) + mz(zr[1])) / 2);
        g.rotate(Math.PI);
        g.fillText('OBJETIVO', 0, 20);
        g.restore();
      }
    } else if (mode === 't1b') {
      // bandas: laterales 10 cm + fondo 12 cm
      g.fillStyle = 'rgba(99,179,237,0.42)';
      g.fillRect(0, 0, mx(-HW() + 0.10), H);
      g.fillRect(mx(HW() - 0.10), 0, W - mx(HW() - 0.10), H);
      g.fillRect(0, 0, W, mz(C() - HL() + 0.12));
      g.strokeStyle = '#63b3ed'; g.lineWidth = 5;
      g.strokeRect(3, 3, W - 6, H - 6);
      g.fillStyle = '#0c1826'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
      g.save(); g.translate(W / 2, 44); g.rotate(Math.PI); g.fillText('FONDO', 0, 0); g.restore();
    } else if (mode === 't4a') {
      // zona de doble bote junto a la red (lado rival)
      const zr = [C() - 0.56, C() - 0.05];
      g.fillStyle = 'rgba(246,173,85,0.45)';
      g.fillRect(0, mz(zr[0]), W, mz(zr[1]) - mz(zr[0]));
      g.strokeStyle = '#f6ad55'; g.lineWidth = 6;
      g.strokeRect(3, mz(zr[0]) + 3, W - 6, mz(zr[1]) - mz(zr[0]) - 6);
      g.fillStyle = '#241206'; g.font = '900 40px system-ui, sans-serif'; g.textAlign = 'center';
      g.save(); g.translate(W / 2, (mz(zr[0]) + mz(zr[1])) / 2); g.rotate(Math.PI);
      g.fillText('DOBLE BOTE', 0, 0); g.restore();
    } else if (mode === 't4b') {
      // franja de fondo: últimos 15 cm
      const zr = [C() - HL(), C() - HL() + 0.15];
      g.fillStyle = 'rgba(246,173,85,0.5)';
      g.fillRect(0, mz(zr[0]), W, mz(zr[1]) - mz(zr[0]));
      g.strokeStyle = '#f6ad55'; g.lineWidth = 6;
      g.strokeRect(3, mz(zr[0]) + 3, W - 6, mz(zr[1]) - mz(zr[0]) - 6);
      g.fillStyle = '#241206'; g.font = '900 30px system-ui, sans-serif'; g.textAlign = 'center';
      g.save(); g.translate(W / 2, (mz(zr[0]) + mz(zr[1])) / 2); g.rotate(Math.PI);
      g.fillText('FONDO 15 cm', 0, 0); g.restore();
    }
    quadTex.needsUpdate = true;
  }

  function applyModeScene() {
    quadMesh.visible = (active === 't1a' || active === 't1b' || active === 't4a' || active === 't4b');
    ribbonG.visible = (active === 't2a');
    apexG.visible = (active === 't2b');
    metroG.visible = (active === 't5a');
    panel.visible = !!active;
    if (quadMesh.visible) drawQuad(active);
  }
