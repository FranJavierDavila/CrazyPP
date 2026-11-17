
  /* =================================================================
   *  TICK · se llama cada frame desde el bucle del núcleo
   *  (siempre: actualiza cosmética global; entrena sólo si hay modo)
   *  ================================================================= */
  function modeFeed() {
    // alimentación específica por modo (máquina o soporte de saque)
    if (active === 't1a' || active === 't1b' || active === 't2a' || active === 't2b' || active === 't5a') {
      feedToPlayer({ speedMul: active === 't2a' ? 1.08 : 1.0 });
      st.phase = 'rally';
    } else if (active === 't3a') {
      const spin = new THREE.Vector3(-(58 + Math.random() * 22), (Math.random() - 0.5) * 10, 0);
      feedToPlayer({
        spin, target: new THREE.Vector3((Math.random() * 2 - 1) * 0.22, 0, C() + HL() * 0.62),
        tIn: 0.6, max: 7.5,
      });
      st.phase = 'rally';
    } else if (active === 't3b') {
      const spin = new THREE.Vector3(62 + Math.random() * 26, (Math.random() - 0.5) * 8, 0);
      feedToPlayer({
        spin, target: new THREE.Vector3((Math.random() * 2 - 1) * 0.24, 0, C() + HL() * (0.5 + Math.random() * 0.3)),
        tIn: 0.52 + Math.random() * 0.18, max: 9.5,
      });
      st.phase = 'rally';
    } else if (active === 't4a' || active === 't4b') {
      serveTee();
    }
  }

  function zoneOf(p) {
    // clasifica un bote del lado rival: 'deep'|'mid'|'short' × 'L'|'R'|'C'
    const dz = C() - p.z;
    const row = dz > HL() * 0.5 ? 'deep' : dz > HL() * 0.25 ? 'mid' : 'short';
    const col = p.x < -0.15 ? 'L' : p.x > 0.15 ? 'R' : 'C';
    return { row, col };
  }

  function judgeAiBounce(p) {
    // p = posición del bote en el campo rival (primer bote tras el golpe)
    if (active === 't1a') {
      const z = zoneOf(p);
      if (st.target && z.row === st.target.z && ((st.target.x < 0 && z.col === 'L') || (st.target.x > 0 && z.col === 'R'))) {
        okHit(MODES[active].ok, MODES[active].pts);
      } else if (z.col === 'C') {
        st.done = 0; failHit('mal_corta');
      } else {
        st.done = 0; failHit('mal_fuera');
      }
    } else if (active === 't1b') {
      const band = Math.abs(p.x) > HW() - 0.10 || p.z < C() - HL() + 0.12;
      if (band) okHit(MODES[active].ok, MODES[active].pts);
      else { st.done = 0; failHit('mal_corta'); }
    } else if (active === 't2a') {
      const deep = p.z < C() - 0.60;
      const under = st.cross && st.cross.y < RIBBON_Y();
      if (under && deep) okHit(MODES[active].ok, MODES[active].pts);
      else if (!under) { st.done = 0; failHit('mal_alto'); }
      else { st.done = 0; failHit('mal_corta'); }
    } else if (active === 't2b') {
      const deep = p.z < C() - 0.65;
      if (st.apex >= APEX_Y && deep) okHit(MODES[active].ok, MODES[active].pts);
      else if (st.apex < APEX_Y) { st.done = 0; failHit('mal_alto'); }
      else { st.done = 0; failHit('mal_corta'); }
    } else if (active === 't3a') {
      const low = st.cross && st.cross.y < CROSS_LOW();
      const popped = st.cross && st.cross.y > CROSS_HI();
      if (popped) { st.done = 0; failHit('mal_alto'); }
      else if (low) okHit(MODES[active].ok, MODES[active].pts);
      else { st.done = 0; failHit('mal_alto'); }
    } else if (active === 't3b') {
      okHit(MODES[active].ok, MODES[active].pts);       // bote rival = bloqueo válido
    } else if (active === 't4a') {
      st.aiBounce++;
      if (st.aiBounce >= 2) okHit(MODES[active].ok, MODES[active].pts);
      else st.live = true;                               // espera el 2.º bote
    } else if (active === 't4b') {
      const deep = p.z < C() - HL() + 0.15;
      if (deep) {
        if (st.cross && st.cross.spd > 4.5) addPts(1);   // bonus saque tenso
        okHit(MODES[active].ok, MODES[active].pts);
      } else { st.done = 0; failHit('mal_larga'); }
    }
  }

  /** muestreo del cruce de red (entre el frame previo y el actual) */
  let prevBallZ = null;
  function sampleCross() {
    const b = G.ball;
    if (prevBallZ === null) { prevBallZ = b.pos.z; return; }
    const z0 = prevBallZ, z1 = b.pos.z, nz = C();
    if ((z0 - nz) * (z1 - nz) < 0) {
      if (st.live && b.vel.z < 0) {
        st.cross = { y: b.pos.y, spd: Math.abs(b.vel.z) };
      }
    }
    prevBallZ = b.pos.z;
  }

  function ballDead() {
    const b = G.ball;
    const restFloor = b.pos.y < DIMS.ballRadius + 0.04 && Math.abs(b.vel.y) < 0.6;
    const onTable = Math.abs(b.pos.x) < HW() + 0.05 &&
      Math.abs(b.pos.z - C()) < HL() + 0.05;
    const restTable = onTable && b.pos.y < TOP() + 0.06 && b.vel.length() < 0.45;
    const gone = Math.abs(b.pos.z - C()) > HL() + 1.5 || b.pos.y < -0.4;
    return restFloor || restTable || gone;
  }

  function trainTick(dt) {
    // 1) eventos del frame
    const evs = G.events || [];
    for (const ev of evs) {
      if (ev.type === 'paddle' && ev.who === 'player') {
        st.hitPos = ev.pos ? ev.pos.clone() : null;
        if (st.phase === 'tee') st.phase = 'serve';
        st.live = true; st.apex = G.ball.pos.y; st.aiBounce = 0;
        st.cross = null; st.deadT = 0; st.shotRec = true; st.shotPts.length = 0;
      } else if (ev.type === 'table') {
        if (ev.side === 'ai') {
          spawnMark(ev.pos, st.live ? 0xffe08a : 0x9fb3c8);
          if (st.live) {
            st.bouncePos = ev.pos;
            judgeAiBounce(ev.pos.clone());
          }
        } else if (ev.side === 'player' && st.live) {
          spawnMark(ev.pos, 0x9fb3c8);
        }
      } else if (ev.type === 'net' && st.live) {
        spawnMark(ev.pos, 0xfc8181);
        failHit('mal_red');
      }
    }
    // 2) física viva del modo
    const b = G.ball;
    if (st.live) {
      if (b.pos.y > st.apex) st.apex = b.pos.y;
      if (st.shotRec && st.shotPts.length < 96) st.shotPts.push(b.pos.clone());
      if (ballDead()) {
        st.deadT += dt;
        if (st.deadT > 0.55) {
          if (active === 't4a' && st.aiBounce === 1) { st.done = 0; failHit('mal_larga'); }
          else if (st.live) failHit('mal_fuera');
          st.shotRec = false;
        }
      } else st.deadT = 0;
    }
    sampleCross();
    // 3) soporte de saque fijo hasta el golpe
    if ((active === 't4a' || active === 't4b') && st.phase === 'tee') {
      b.pos.set(0.03, TOP() + 0.15, C() + 1.04);
      b.vel.set(0, 0, 0);
      b.spin.set(0, 0, 0);
    }
    // 4) alimentación temporizada
    if (!st.live) {
      st.wait -= dt;
      if (st.wait <= 0) { modeFeed(); st.wait = active === 't5a' ? 1.65 : 2.2; }
    } else if (active === 't5a') {
      // el metrónomo NO espera: ritmo constante, la bola nueva sustituye
      st.feedT += dt;
      if (st.feedT >= 1.65) { st.feedT = 0; modeFeed(); }
    }
    // 5) metrónomo visual
    if (active === 't5a') {
      st.beat += dt;
      const ph = (st.beat % 1.65) / 1.65;
      const s = 1 + 0.5 * Math.max(0, 1 - ph * 4);
      metroG.scale.set(s, s, 1);
      metroG.material.opacity = 0.35 + 0.55 * Math.max(0, 1 - ph * 3);
    }
    // 6) línea de tiro
    if (st.live && S.fb.line && st.shotPts.length > 1) shotLineShow();
  }

  /* ---------------- cosméticos globales (todo modos) ---------------- */
  function cosmeticsTick(dt) {
    // flecha de efecto sobre la bola (también en campeonatos: sólo avisa)
    if (!spinSprite) return;
    const b = G.ball;
    let show = false;
    if (S.fb.spin && b && b.vel && b.vel.lengthSq() > 1.2 && b.spin && b.spin.lengthSq() > 320) {
      const lift = b.spin.z * b.vel.x - b.spin.x * b.vel.z;   // (spin×vel).y
      const force = Math.min(1, Math.abs(lift) / 9);
      const side = Math.abs(b.spin.y) / 18;
      if (force > 0.12 || side > 0.5) {
        show = true;
        spinSprite.position.set(b.pos.x, b.pos.y + 0.1, b.pos.z);
        const col = lift < -0.8 ? 0xff9a4a : lift > 0.8 ? 0x4ab8ff : 0xc07aff;
        spinSprite.material.color.setHex(col);
        spinSprite.material.rotation += dt * (lift < 0 ? 6 : -6);
      }
    }
    spinSprite.material.opacity += ((show ? 0.9 : 0) - spinSprite.material.opacity) * Math.min(1, dt * 9);
    if (!show && spinSprite.material.opacity < 0.05) spinSprite.visible = false;
    else spinSprite.visible = true;
    // marcas: desvanecer
    for (const m of marks) {
      if (!m.visible) continue;
      m.userData.ttl -= dt;
      if (m.userData.ttl <= 0) { m.visible = false; continue; }
      m.material.opacity = Math.min(0.95, m.userData.ttl);
    }
    // línea de tiro: desvanecer
    if (shotTtl > 0) {
      shotTtl -= dt;
      shotLine.material.opacity = Math.max(0, Math.min(0.85, shotTtl * 0.5));
      if (shotTtl <= 0) shotLine.visible = false;
    }
    // skin arcoíris
    if (S.skin === 'arcoiris' && skinMats.length) {
      rainbowT += dt * 0.6;
      const col = new THREE.Color().setHSL(rainbowT % 1, 0.75, 0.55);
      for (const m of skinMats) m.color.copy(col);
    }
    // iconos de efecto en la pala
    if (st.spinIconT > 0) {
      st.spinIconT -= dt;
      const op = Math.max(0, Math.min(1, st.spinIconT / 0.5));
      for (const s of faceIcons) s.material.opacity = op;
      if (st.spinIconT <= 0) for (const s of faceIcons) s.visible = false;
    }
    // panel
    if (panelDirty && panel) { drawPanel(); panelDirty = false; }
    if (st.toastT > 0) {
      st.toastT -= dt;
      if (st.toastT <= 0) panelDirty = true;
    }
  }
