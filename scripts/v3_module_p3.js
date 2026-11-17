
  /* =================================================================
   *  CICLO DE VIDA DE LOS MODOS
   *  ================================================================= */
  function startMode(game, id) {
    if (!game) return;
    if (!MODES[id]) return;
    G = game;
    buildScene();
    LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
    active = id;
    const M = MODES[id];
    if (!game.calib) game.enterCalib();      // aísla: sin árbitro, sin IA, sin marcador
    game.trainV3 = id;                        // el núcleo desactiva su rutina de calib
    game.calibPanel.group.visible = false;    // el panel de agarre fuera en los modos
    st.streak = 0; st.done = 0; st.sessPts = 0; st.rally = 0;
    st.target = pickTarget(); st.wait = 0.9; st.feedT = 0; st.toast = ''; st.toastT = 0;
    grp.visible = true;
    applyModeScene();
    panelDirty = true;
    game.audio.playOsc(720, 1080, 0.09, 'triangle', 0.13, 0);
    if (game.rules) game.rules.message = '';
  }
  function stopMode(game) {
    if (!G) return;
    active = null;
    if (grp) grp.visible = false;
    applyModeScene();
    const g = game || G;
    g.trainV3 = null;
    if (g.calib) g.exitCalib();               // vuelve al modo previo (match/survival)
    G.audio.playOsc(900, 560, 0.1, 'sine', 0.1, 0);
  }
  /** El subapartado 0: posición de la pala (panel clásico). */
  function startCalib(game) {
    G = game;
    active = null;
    if (grp) { grp.visible = false; applyModeScene(); }
    if (game.trainV3) game.trainV3 = null;
    game.enterCalib();
  }

  /* =================================================================
   *  SKINS DE LA PALA + ICONOS DE EFECTO EN AMBAS CARAS (global)
   *  ================================================================= */
  let skinMats = [], faceIcons = [];
  const BLADE_Y = (PALA_BLADE_Y - PALA_GRIP_Y) * PALA_SCALE;   // centro hoja en la montura
  function clearNamed(mount, name) {
    const dead = [];
    mount.traverse((o) => { if (o.userData && o.userData.ppTrainTag === name) dead.push(o); });
    for (const d of dead) if (d.parent) d.parent.remove(d);
  }
  function applySkin(skinId) {
    const sk = SKINS.find((s) => s.id === skinId) || SKINS[0];
    S.skin = sk.id; save();
    if (!G || !G.paddleMounts) return;
    skinMats = [];
    for (const mount of G.paddleMounts) {
      clearNamed(mount, 'skin');
      const ringMat = new THREE.MeshStandardMaterial({
        color: sk.ring === -1 ? 0xff0000 : sk.ring, roughness: 0.4, metalness: 0.35,
        emissive: sk.ring === -1 ? 0x220000 : sk.ring, emissiveIntensity: 0.35,
      });
      if (sk.ring === -1) skinMats.push(ringMat);
      const ring = new THREE.Mesh(new THREE.TorusGeometry(0.0835, 0.005, 8, 40), ringMat);
      ring.position.set(0, BLADE_Y, 0);
      ring.userData.ppTrainTag = 'skin';
      mount.add(ring);
      const gripMat = new THREE.MeshStandardMaterial({ color: sk.grip, roughness: 0.75 });
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.021, 0.023, 0.055, 12), gripMat);
      grip.position.set(0, -0.045, 0);
      grip.userData.ppTrainTag = 'skin';
      mount.add(grip);
    }
  }
  function buildFaceIcons() {
    if (!G || !G.paddleMounts) return;
    // limpiar previos
    for (const mount of G.paddleMounts) clearNamed(mount, 'faceicon');
    faceIcons = [];
    const mkTex = () => {
      const cv = mkCanvas(64, 64);
      const g2 = cv.getContext('2d');
      g2.strokeStyle = '#ffffff'; g2.lineWidth = 7;
      g2.beginPath(); g2.arc(32, 32, 19, 0.2, Math.PI * 1.5); g2.stroke();
      g2.fillStyle = '#ffffff';
      g2.beginPath(); g2.moveTo(44, 4); g2.lineTo(57, 17); g2.lineTo(37, 22);
      g2.closePath(); g2.fill();
      return texOf(cv);
    };
    const tx = mkTex();
    for (const mount of G.paddleMounts) {
      for (const side of [1, -1]) {
        const sp = new THREE.Sprite(new THREE.SpriteMaterial({
          map: tx, transparent: true, opacity: 0, depthWrite: false,
        }));
        sp.position.set(0, BLADE_Y + 0.045, side * 0.017);
        sp.scale.setScalar(0.05);
        sp.visible = false;
        sp.userData.ppTrainTag = 'faceicon';
        mount.add(sp);
        faceIcons.push(sp);
      }
    }
  }
  /** Icono en AMBAS caras cuando el jugador aplica efecto (en TODO el juego). */
  function pulseFaceIcons(lift) {
    const col = lift < 0 ? 0xff9a4a : lift > 0 ? 0x4ab8ff : 0xc07aff;
    for (const s of faceIcons) {
      s.material.color.setHex(col);
      s.material.opacity = 1;
      s.visible = true;
    }
    st.spinIconT = 1.15;
  }

  /* =================================================================
   *  MENÚ VR · PRO TRAINING HUB (páginas 'train' y 'trainarea')
   *  ================================================================= */
  function drawHeader(game, c, rects, btn, label, subTxt) {
    c.fillStyle = '#f0c85a';
    c.font = '900 54px system-ui, sans-serif';
    c.textAlign = 'left'; c.textBaseline = 'middle';
    c.fillText(t('hub_t'), 40, 78);
    c.fillStyle = '#7d8ea6';
    c.font = '600 24px system-ui, sans-serif';
    c.fillText(subTxt || t('hub_s'), 40, 122);
    c.strokeStyle = 'rgba(240,200,90,0.55)'; c.lineWidth = 3;
    c.beginPath(); c.moveTo(40, 152); c.lineTo(984, 152); c.stroke();
    btn('trv3:back', 820, 34, 164, 56, t('menu'), false, undefined, undefined, 24);
  }

  function drawHub(game, c, rects, btn, label) {
    LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
    drawHeader(game, c, rects, btn, label);
    // chip de perfil
    const lvl = levelOf(S.pts);
    c.textAlign = 'right'; c.textBaseline = 'middle';
    c.fillStyle = '#f0c85a'; c.font = '800 30px system-ui, sans-serif';
    c.fillText(S.pts + ' ' + t('pts'), 800, 82);
    c.fillStyle = '#8fa0b8'; c.font = '600 20px system-ui, sans-serif';
    c.fillText(t('nivel') + ' · ' + t(lvl.k), 800, 112);
    // tarjetas de áreas (2 × 3)
    const CW = 456, CH = 150, GX = 32, GY = 16, X0 = 40, X1 = X0 + CW + GX;
    let y = 190;
    const card = (x, yy, id, ik, sk, g0, g1, col, act) => {
      const idx = rects.length;
      btn('trv3:area:' + id, x, yy, CW, CH, '', false);
      // repintar encima con estilo propio (btn pinta un botón plano)
      c.save();
      c.beginPath();
      if (c.roundRect) c.roundRect(x, yy, CW, CH, 20); else c.rect(x, yy, CW, CH);
      const gr = c.createLinearGradient(x, yy, x + CW, yy + CH);
      gr.addColorStop(0, g0); gr.addColorStop(1, g1);
      c.fillStyle = gr; c.fill();
      c.strokeStyle = act ? '#f0c85a' : (game.menuHover && game.menuHover.includes(idx) ? '#ffffff' : 'rgba(255,255,255,0.25)');
      c.lineWidth = act ? 5 : 3;
      c.stroke();
      c.fillStyle = col; c.globalAlpha = 0.16;
      c.beginPath(); c.arc(x + CW - 56, yy + CH / 2, 44, 0, Math.PI * 2); c.fill();
      c.globalAlpha = 1;
      c.fillStyle = '#ffffff'; c.textAlign = 'left'; c.textBaseline = 'middle';
      let fs = 34;
      c.font = '800 ' + fs + 'px system-ui, sans-serif';
      while (fs > 22 && c.measureText(t(ik)).width > CW - 60) { fs -= 2; c.font = '800 ' + fs + 'px system-ui, sans-serif'; }
      c.fillText(t(ik), x + 26, yy + 52);
      c.fillStyle = 'rgba(255,255,255,0.8)'; c.font = '600 19px system-ui, sans-serif';
      let sub2 = t(sk);
      while (sub2.length > 2 && c.measureText(sub2).width > CW - 52) sub2 = sub2.slice(0, -1);
      if (sub2 !== t(sk)) sub2 += '…';
      c.fillText(sub2, x + 26, yy + 86);
      const bests = Object.keys(MODES).filter((m) => MODES[m].area === id && S.best[m]);
      c.fillStyle = '#f0c85a'; c.font = '700 18px system-ui, sans-serif';
      c.fillText(bests.length ? t('mejor') + ': ' + bests.map((m) => S.best[m]).join(' / ') : '·', x + 26, yy + 120);
      c.restore();
    };
    for (let i = 0; i < AREAS.length; i++) {
      const a = AREAS[i];
      card(i % 2 === 0 ? X0 : X1, y + Math.floor(i / 2) * (CH + GY), a.id, a.ik, a.sk, a.g0, a.g1, a.col);
    }
    // tarjeta POSICIÓN DE LA PALA (subapartado 0) a lo ancho
    const yPal = y + 3 * (CH + GY);
    btn('trv3:calib', X0, yPal, CW * 2 + GX, 96, '', false);
    c.save();
    c.beginPath();
    if (c.roundRect) c.roundRect(X0, yPal, CW * 2 + GX, 96, 20); else c.rect(X0, yPal, CW * 2 + GX, 96);
    c.fillStyle = 'rgba(232,180,90,0.14)'; c.fill();
    c.strokeStyle = 'rgba(232,180,90,0.55)'; c.lineWidth = 3; c.stroke();
    c.fillStyle = '#f0c85a'; c.textAlign = 'left'; c.textBaseline = 'middle';
    c.font = '800 32px system-ui, sans-serif';
    c.fillText('⌂ ' + t('a_pala'), X0 + 26, yPal + 34);
    c.fillStyle = 'rgba(255,255,255,0.75)'; c.font = '600 19px system-ui, sans-serif';
    c.fillText(t('a_pala_s'), X0 + 26, yPal + 66);
    c.restore();
    // ayudas técnicas
    const yFb = yPal + 112;
    label(t('fb_t'), yFb, 22, '#7d8ea6');
    const toggles = [['marks', t('fb_marks')], ['line', t('fb_line')], ['spin', t('fb_spin')]];
    let tx = X0;
    for (const [k, lbl] of toggles) {
      const w = 290;
      btn('trv3:fb:' + k, tx, yFb + 18, w, 64, lbl, !!S.fb[k], undefined, !!S.fb[k], 22);
      tx += w + 24;
    }
    // skins
    const ySk = yFb + 108;
    label(t('skins_t'), ySk, 22, '#7d8ea6');
    let sx = X0;
    for (const sk of SKINS) {
      const w = 180, h = 76;
      const un = S.unlocked.indexOf(sk.id) >= 0;
      const idb = 'trv3:skin:' + sk.id;
      const idx = rects.length;
      btn(idb, sx, ySk + 18, w, h, '', false);
      c.save();
      c.beginPath();
      if (c.roundRect) c.roundRect(sx, ySk + 18, w, h, 14); else c.rect(sx, ySk + 18, w, h);
      c.fillStyle = S.skin === sk.id ? 'rgba(240,200,90,0.30)' : 'rgba(255,255,255,0.06)';
      c.fill();
      c.strokeStyle = S.skin === sk.id ? '#f0c85a' : (un ? 'rgba(255,255,255,0.4)' : 'rgba(255,255,255,0.15)');
      c.lineWidth = S.skin === sk.id ? 4 : 2;
      c.stroke();
      // muestra circular del color
      c.beginPath(); c.arc(sx + 34, ySk + 56, 20, 0, Math.PI * 2);
      c.fillStyle = sk.ring === -1 ? '#c07aff' : '#' + sk.ring.toString(16).padStart(6, '0');
      if (!un) c.fillStyle = 'rgba(255,255,255,0.12)';
      c.fill();
      c.strokeStyle = 'rgba(255,255,255,0.5)'; c.lineWidth = 2; c.stroke();
      c.fillStyle = un ? '#e9edf2' : '#5a6a7d';
      c.font = '700 18px system-ui, sans-serif'; c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillText(un ? (sk.name[LANG] || sk.name.es) : '🔒 ' + sk.min, sx + 64, ySk + 46);
      if (un && S.skin === sk.id) {
        c.fillStyle = '#f0c85a'; c.font = '600 15px system-ui, sans-serif';
        c.fillText(t('skin_sel'), sx + 64, ySk + 68);
      }
      c.restore();
      sx += w + 14;
    }
    // botón parar si hay modo activo
    if (active) btn('trv3:stop', X0, 1380, 944, 76, t('parar'), false, 'surv', undefined, 28);
  }

  function drawArea(game, c, rects, btn, label) {
    LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
    const a = AREAS.find((x) => x.id === uiArea) || AREAS[0];
    drawHeader(game, c, rects, btn, label, t(a.ik) + ' · ' + t(a.sk));
    let y = 196;
    for (const id of Object.keys(MODES)) {
      const M = MODES[id];
      if (M.area !== a.id) continue;
      const isOn = active === id;
      // tarjeta del modo
      const idx = rects.length;
      btn('trv3:start:' + id, 40, y, 944, 172, '', false);
      c.save();
      c.beginPath();
      if (c.roundRect) c.roundRect(40, y, 944, 172, 22); else c.rect(40, y, 944, 172);
      const gr = c.createLinearGradient(40, y, 984, y + 172);
      gr.addColorStop(0, a.g0); gr.addColorStop(1, a.g1);
      c.fillStyle = gr; c.globalAlpha = isOn ? 0.95 : 0.8; c.fill(); c.globalAlpha = 1;
      c.strokeStyle = isOn ? '#f0c85a' : 'rgba(255,255,255,0.28)'; c.lineWidth = isOn ? 5 : 3;
      c.stroke();
      c.textAlign = 'left'; c.textBaseline = 'middle';
      c.fillStyle = '#ffffff'; c.font = '800 34px system-ui, sans-serif';
      c.fillText(t(M.nk), 68, y + 42);
      c.fillStyle = 'rgba(255,255,255,0.85)'; c.font = '600 20px system-ui, sans-serif';
      const desc = t(M.dk, { n: M.n });
      // cuerpo envuelto a 2 líneas
      let l1 = desc, l2 = '';
      if (c.measureText(desc).width > 700) {
        const words = desc.split(' ');
        l1 = ''; l2 = '';
        for (const w of words) {
          if (c.measureText(l1 + ' ' + w).width <= 700 && !l2) l1 = l1 ? l1 + ' ' + w : w;
          else l2 = l2 ? l2 + ' ' + w : w;
        }
      }
      c.fillText(l1, 68, y + 82);
      if (l2) c.fillText(l2, 68, y + 110);
      c.fillStyle = '#f0c85a'; c.font = '700 20px system-ui, sans-serif';
      c.fillText((S.best[id] ? t('mejor') + ': ' + S.best[id] + '  ·  ' : '') + t('obj') + ': ' + M.n, 68, y + 142);
      c.textAlign = 'right';
      c.fillStyle = isOn ? '#f0c85a' : '#ffffff';
      c.font = '900 26px system-ui, sans-serif';
      c.fillText(isOn ? t('activo') : t('iniciar'), 950, y + 86);
      c.restore();
      y += 190;
    }
    btn('trv3:back', 40, 1380, 944, 76, t('volver'), false, undefined, undefined, 28);
  }

  /* ---------------- acciones del menú (case 'trv3') ---------------- */
  function menuAction(game, arg) {
    const p = arg.split(':');
    const cmd = p[0];
    if (cmd === 'area') { uiArea = p[1] || 'dir'; uiPage = 'area'; game.menuPage = 'trainarea'; game.drawMenu(); }
    else if (cmd === 'back') { game.menuPage = 'main'; game.drawMenu(); }
    else if (cmd === 'start') {
      game.closeMenu();
      startMode(game, p[1]);
    }
    else if (cmd === 'calib') { game.closeMenu(); startCalib(game); }
    else if (cmd === 'stop') { stopMode(game); game.menuPage = 'main'; game.drawMenu(); }
    else if (cmd === 'skin') { applySkin(p[1]); game.drawMenu(); }
    else if (cmd === 'fb') { S.fb[p[1]] = S.fb[p[1]] ? 0 : 1; save(); game.drawMenu(); }
  }

  /* ---------------- tick público ---------------- */
  function tick(dt) {
    if (!G) {
      const g = (typeof window !== 'undefined') ? window.__PP_GAME : null;
      if (!g) return;
      G = g;
      buildScene();
      applySkin(S.skin);
      buildFaceIcons();
      //Lang persistente
      LANG = (typeof __ppLang !== 'undefined' && __ppLang) || 'es';
    }
    if (!G || G.disposed) return;
    try {
      cosmeticsTick(dt);
      if (active && G.trainV3 && G.calib) trainTick(dt);
      // detección de efecto del jugador en CUALQUIER modo (iconos en caras)
      if (faceIcons.length && G.events && G.events.length) {
        for (const ev of G.events) {
          if (ev.type === 'paddle' && ev.who === 'player' && G.ball && G.ball.spin &&
              G.ball.spin.lengthSq() > 330) {
            const lift = G.ball.spin.z * G.ball.vel.x - G.ball.spin.x * G.ball.vel.z;
            pulseFaceIcons(lift);
            break;
          }
        }
      }
    } catch (e) { /* el módulo NUNCA rompe el bucle del juego */ }
  }

  return {
    tick, startMode, stopMode, startCalib, menuAction, applySkin,
    drawHub, drawArea,
    get state() { return { active, pts: S.pts, best: S.best, skin: S.skin, unlocked: S.unlocked.slice() }; },
    __debug: { S, st, MODES },
  };
})();
window.__PP_TRAIN = PP_TRAIN;
