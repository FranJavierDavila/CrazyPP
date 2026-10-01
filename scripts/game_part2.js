/* =====================================================================
 *  ÁRBITRO · reglas del tenis de mesa (ITTF simplificadas)
 *  - Partido a 11, ventaja de 2, saque alternado cada 2 puntos.
 *  - SAQUE: bote obligatorio en el campo propio y luego en el rival.
 *    Tocar la red y pasar = LET (se repite). Falta de saque = punto
 *    del receptor. El lanzamiento fallido no puntúa (se repite).
 *  - IGUALA: volea antes del bote, doble golpe o no pasar la red = falta.
 * ===================================================================== */
class Rules {
  constructor() {
    this.state = 'serve';
    this.server = 'player';
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.message = 'Tu saque · la bola espera en tu mano libre';
    this.totalPoints = 0;
    this.stateTimer = 0;
    this.lastHitter = null;
    this.isServeBall = false;
    this.serveOwnPending = false;   // falta el bote del sacador en su campo
    this.mustBounceOpp = false;     // debe botar en el campo del receptor
    this.validBounce = false;       // ya botó en el campo del receptor
    this.netTouched = false;
    this.rallyHits = 0;
  }

  other(s) { return s === 'player' ? 'ai' : 'player'; }

  startMatch() {
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.totalPoints = 0;
    this.server = 'player';
    this.state = 'serve';
    this.stateTimer = 0;
    this.lastHitter = null;
    this.isServeBall = false;
    this.serveOwnPending = false;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.netTouched = false;
    this.rallyHits = 0;
    this.message = 'Tu saque · la bola espera en tu mano libre';
  }

  /** Comienza el rally tras un golpe de saque válido (al caer, tras la línea). */
  beginServeRally(server) {
    this.state = 'rally';
    this.lastHitter = server;
    this.isServeBall = true;
    this.serveOwnPending = true;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  registerPaddleHit(who) {
    if (this.state !== 'rally') return [];
    // Nadie puede golpear dos veces seguidas (doble golpe = falta)
    if (who === this.lastHitter) {
      return this.applyPoint(this.other(who), 'doble golpe');
    }
    // Volea: golpear antes de que la bote en su campo el receptor
    if (this.serveOwnPending || (this.mustBounceOpp && !this.validBounce)) {
      return this.applyPoint(this.lastHitter, 'golpe antes del bote');
    }
    this.lastHitter = who;
    this.mustBounceOpp = true;
    this.validBounce = false;
    this.isServeBall = false;
    this.rallyHits++;
    return [];
  }

  applyPoint(winner, cause) {
    if (winner === 'player') this.scorePlayer++;
    else this.scoreAi++;
    this.totalPoints++;
    this.state = 'point';
    this.stateTimer = 2.2;
    const rallyTxt = this.rallyHits >= 6 ? ` · ${this.rallyHits} golpes` : '';
    this.message = winner === 'player' ? `¡Punto para ti! · ${cause}${rallyTxt}` : `Punto para la CPU · ${cause}${rallyTxt}`;
    return [{ type: 'point', winner, cause }];
  }

  retryServe(cause) {
    this.state = 'serve';
    this.message = `${cause} · repite el saque`;
    return [{ type: 'retry-serve', cause }];
  }

  computeNextServer() {
    const n = this.totalPoints;
    if (this.scorePlayer >= 10 && this.scoreAi >= 10) {
      return n % 2 === 0 ? 'player' : 'ai';
    }
    return Math.floor(n / 2) % 2 === 0 ? 'player' : 'ai';
  }

  handleEvents(events) {
    const intents = [];
    for (const e of events) {
      if (e.consumed) continue;
      if (this.state !== 'rally') break;

      switch (e.type) {
        case 'paddle': {
          if (e.who) intents.push(...this.registerPaddleHit(e.who));
          break;
        }
        case 'net': {
          this.netTouched = true;
          break;
        }
        case 'table': {
          if (!e.side || !this.lastHitter) break;
          const own = this.lastHitter;
          const opp = this.other(own);

          if (this.serveOwnPending) {
            if (e.side === own) {
              // 1er bote del saque en el campo del sacador: correcto
              this.serveOwnPending = false;
              this.mustBounceOpp = true;
              this.netTouched = false;
            } else {
              intents.push(...this.applyPoint(opp, 'saque sin bote propio'));
            }
          } else if (this.mustBounceOpp) {
            if (e.side === opp) {
              this.validBounce = true;
              if (this.isServeBall && this.netTouched) {
                // LET: rozó la red en saque pero pasó y botó bien
                intents.push(...this.retryServe('LET · la bola rozó la red'));
              } else {
                this.mustBounceOpp = false;
                this.netTouched = false;
              }
            } else {
              const cause = this.isServeBall
                ? 'el saque no pasó la red'
                : own === 'player' ? 'golpeaste tu propio campo' : 'la CPU golpeó su campo';
              intents.push(...this.applyPoint(opp, cause));
            }
          } else if (this.validBounce) {
            if (e.side === opp) {
              const cause = own === 'player' ? 'doble bote: la CPU no llegó' : 'doble bote: no llegaste';
              intents.push(...this.applyPoint(own, cause));
            } else {
              const cause = own === 'player' ? 'la bola volvió a tu campo' : 'la bola volvió al campo de la CPU';
              intents.push(...this.applyPoint(opp, cause));
            }
          }
          break;
        }
        case 'floor':
        case 'wall': {
          if (!this.lastHitter) break;
          if (this.serveOwnPending || this.mustBounceOpp) {
            const cause = this.isServeBall
              ? (this.netTouched ? 'saque a la red' : 'saque fuera')
              : (this.netTouched ? 'se quedó en la red' : (e.type === 'wall' ? 'a la pared' : 'bola fuera'));
            intents.push(...this.applyPoint(this.other(this.lastHitter), cause));
          } else {
            const cause = this.lastHitter === 'player' ? 'la CPU no la devolvió' : 'no la devolviste';
            intents.push(...this.applyPoint(this.lastHitter, cause));
          }
          break;
        }
      }
    }
    return intents;
  }

  update(dt) {
    const intents = [];

    if (this.state === 'point') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        const finished =
          (this.scorePlayer >= 11 || this.scoreAi >= 11) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= 2;
        if (finished) {
          this.state = 'over';
          this.stateTimer = 8;
          const winner = this.scorePlayer > this.scoreAi ? 'player' : 'ai';
          this.message = winner === 'player' ? '¡Has ganado el partido!' : 'La CPU gana el partido';
          intents.push({ type: 'game-over', winner });
        } else {
          this.state = 'serve';
          this.server = this.computeNextServer();
          this.message = this.server === 'player'
            ? 'Tu saque · la bola espera en tu mano libre'
            : 'Saque de la CPU…';
          intents.push({ type: 'serve', server: this.server });
        }
      }
    } else if (this.state === 'over') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        this.startMatch();
        intents.push({ type: 'serve', server: this.server });
      }
    }

    return intents;
  }
}

/* =====================================================================
 *  IA · predice dónde botará la bola en SU campo, camina hasta el punto
 *  de golpeo, espera el bote (nada de voleas) y devuelve buscando el
 *  hueco lejos del rival. Puede fallar de forma natural (no llega).
 * ===================================================================== */
function gauss() {
  return (Math.random() * 2 - 1) * 0.7 + (Math.random() * 2 - 1) * 0.3;
}

class OpponentAI {
  constructor(cfg, sign, home) {
    this.cfg = cfg;
    this.sign = sign;
    this.home = home.clone();
    this.pos = home.clone();
    this.vel = new THREE.Vector3();
    this.predict = new THREE.Vector3();
    this.predictValid = false;
    this.predictTimer = 0;
    this.hitCooldown = 0;
    this.errX = 0;
    this.errY = 0;
  }

  setConfig(cfg) { this.cfg = cfg; }

  reset() {
    this.pos.copy(this.home);
    this.vel.set(0, 0, 0);
    this.predictValid = false;
    this.hitCooldown = 0;
  }

  update(dt, ball, ctx) {
    this.hitCooldown -= dt;
    const C = DIMS.tableCenterZ;
    const sign = this.sign;
    const toward = ball.vel.z * sign > 0;

    if (ctx.canHit && toward) {
      this.predictTimer -= dt;
      if (this.predictTimer <= 0) {
        this.predictTimer = this.cfg.predictInterval;
        const strike = predictStrike(ball, sign);
        if (strike) {
          this.predict.copy(strike.point);
          this.errX = gauss() * this.cfg.errStd;
          this.errY = gauss() * this.cfg.errStd * 0.6;
          this.predictValid = true;
        } else {
          this.predictValid = false;
        }
      }
    } else {
      this.predictValid = false;
    }

    if (this.predictValid) {
      const baseline = C + sign * DIMS.tableHalfLength;
      let inDist = (this.predict.z - baseline) * -sign;
      inDist = THREE.MathUtils.clamp(inDist, -0.45, DIMS.tableHalfLength + 0.15);
      const zClamp = baseline + inDist * -sign;
      let yClamp = THREE.MathUtils.clamp(this.predict.y + this.errY, 0.55, 1.55);
      const overTable =
        Math.abs(this.predict.x) < DIMS.tableHalfWidth + 0.1 &&
        Math.abs(zClamp - C) < DIMS.tableHalfLength;
      if (overTable) yClamp = Math.max(yClamp, DIMS.tableTopY + 0.08);
      tmpT.set(
        THREE.MathUtils.clamp(this.predict.x + this.errX, -(DIMS.tableHalfWidth + 0.35), DIMS.tableHalfWidth + 0.35),
        yClamp,
        zClamp,
      );
    } else {
      tmpT.set(
        this.home.x + ball.pos.x * 0.3,
        this.home.y,
        this.home.z + (toward ? -sign * 0.2 : 0),
      );
    }

    tmpD.copy(tmpT).sub(this.pos);
    const dist = tmpD.length();
    const desiredSpeed = Math.min(this.cfg.maxSpeed, dist * 4.5);
    if (dist > 1e-5) tmpD.setLength(desiredSpeed); else tmpD.set(0, 0, 0);
    this.vel.lerp(tmpD, Math.min(1, dt * this.cfg.accel));
    this.pos.addScaledVector(this.vel, dt);

    if (!ctx.canHit || !ctx.validBounce || !toward || this.hitCooldown > 0) return null;
    const reach = 0.185;
    if (this.pos.distanceToSquared(ball.pos) > reach * reach) return null;
    if ((ball.pos.z - C) * sign < 0.04) return null;
    if (ball.pos.y < DIMS.tableTopY - 0.08 || ball.pos.y > 1.65) return null;

    const ballSpeed = ball.vel.length();
    const pMiss = this.cfg.missBase + Math.max(0, ballSpeed - 7) * 0.05;
    this.hitCooldown = 0.55;
    if (Math.random() < pMiss) return null;

    const away = ctx.oppPadX !== undefined
      ? -Math.sign(ctx.oppPadX || (Math.random() - 0.5))
      : (Math.random() < 0.5 ? -1 : 1);
    let tx = away * (0.16 + Math.random() * 0.38) + gauss() * this.cfg.errStd * 0.8;
    tx = THREE.MathUtils.clamp(tx, -0.55, 0.55);
    const drop = Math.random() < this.cfg.short;
    const depthRel = drop ? 0.25 + Math.random() * 0.25 : 0.55 + Math.random() * 0.65;
    const tz = C - sign * depthRel * DIMS.tableHalfLength;

    const high = ball.pos.y > 1.15;
    const smash = high && Math.random() < this.cfg.smash;
    const T = smash ? this.cfg.minT * 0.8 : this.cfg.minT + Math.random() * (this.cfg.maxT - this.cfg.minT);
    const maxV = smash ? this.cfg.maxShotSpeed * 1.15 : this.cfg.maxShotSpeed;

    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const v = computeShotVelocity(ball.pos, tmpTarget, T, maxV);

    ball.spin.set(
      -sign * (8 + Math.random() * 8),
      (Math.random() - 0.5) * 8,
      0,
    );
    return v;
  }
}

/* =====================================================================
 *  ESCENA · sala, mesa reglamentaria, bola con estela, rival con cuerpo,
 *  sombra proyectada, marcas de bote y marcador
 * ===================================================================== */

function createRoom() {
  const g = new THREE.Group();
  const zC = (DIMS.roomBackZ + DIMS.roomFrontZ) / 2;
  const depth = DIMS.roomBackZ - DIMS.roomFrontZ;

  const floorMat = new THREE.MeshStandardMaterial({ color: COLORS.floor, roughness: 0.9, metalness: 0.05 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0, zC);
  floor.receiveShadow = true;
  g.add(floor);

  const grid = new THREE.GridHelper(Math.max(DIMS.roomHalfX * 2, depth), 20, 0x4a4038, 0x2c2622);
  grid.position.set(0, 0.002, zC);
  g.add(grid);

  const wallMat = new THREE.MeshStandardMaterial({ color: COLORS.wall, roughness: 1 });
  const mkWall = (w, h, pos, rotY) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
    m.position.copy(pos);
    m.rotation.y = rotY;
    g.add(m);
  };
  const cx = DIMS.roomHalfX;
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(-cx, DIMS.roomHeight / 2, zC), Math.PI / 2);
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(cx, DIMS.roomHeight / 2, zC), -Math.PI / 2);
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomBackZ), Math.PI);
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomFrontZ), 0);

  const ceil = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth),
    new THREE.MeshStandardMaterial({ color: 0x14171b, roughness: 1 }),
  );
  ceil.rotation.x = Math.PI / 2;
  ceil.position.set(0, DIMS.roomHeight, zC);
  g.add(ceil);

  const panelMat = new THREE.MeshBasicMaterial({ color: 0xf5efe2 });
  for (const px of [-1.4, 1.4]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.4), panelMat);
    panel.rotation.x = Math.PI / 2;
    panel.position.set(px, DIMS.roomHeight - 0.01, -1.2);
    g.add(panel);
  }

  const stripMat = new THREE.MeshBasicMaterial({ color: COLORS.accentAmber });
  for (const sx of [-cx + 0.02, cx - 0.02]) {
    const strip = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, depth * 0.9), stripMat);
    strip.position.set(sx, 2.1, zC);
    g.add(strip);
  }

  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.26, 0.33, 48),
    new THREE.MeshBasicMaterial({
      color: COLORS.accentAmber, transparent: true, opacity: 0.45, side: THREE.DoubleSide,
    }),
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.set(0, 0.004, 0);
  g.add(ring);

  return g;
}

function createTable() {
  const g = new THREE.Group();
  const topY = DIMS.tableTopY;
  const L = DIMS.tableHalfLength * 2;
  const W = DIMS.tableHalfWidth * 2;

  const topMat = new THREE.MeshStandardMaterial({ color: COLORS.tableBlue, roughness: 0.55, metalness: 0.05 });
  const top = new THREE.Mesh(new THREE.BoxGeometry(W, DIMS.tableThickness, L), topMat);
  top.position.set(0, topY - DIMS.tableThickness / 2, DIMS.tableCenterZ);
  top.castShadow = true;
  top.receiveShadow = true;
  g.add(top);

  const lineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
  const lineH = 0.002;
  const mkLine = (w, d, x, z) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, lineH, d), lineMat);
    m.position.set(x, topY + lineH / 2 - 0.0005, DIMS.tableCenterZ + z);
    g.add(m);
  };
  mkLine(W, 0.02, 0, -DIMS.tableHalfLength + 0.01);
  mkLine(W, 0.02, 0, DIMS.tableHalfLength - 0.01);
  mkLine(0.02, L, -DIMS.tableHalfWidth + 0.01, 0);
  mkLine(0.02, L, DIMS.tableHalfWidth - 0.01, 0);
  mkLine(0.003, L, 0, 0);

  const frameMat = new THREE.MeshStandardMaterial({ color: COLORS.frame, roughness: 0.7 });
  const apron = new THREE.Mesh(new THREE.BoxGeometry(W * 0.96, 0.1, 0.03), frameMat);
  apron.position.set(0, topY - DIMS.tableThickness - 0.06, DIMS.tableCenterZ - DIMS.tableHalfLength + 0.05);
  g.add(apron);
  const apron2 = apron.clone();
  apron2.position.z = DIMS.tableCenterZ + DIMS.tableHalfLength - 0.05;
  g.add(apron2);

  for (const lx of [-W / 2 + 0.12, W / 2 - 0.12]) {
    for (const lz of [-L / 2 + 0.15, L / 2 - 0.15]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, topY - DIMS.tableThickness, 0.06), frameMat);
      leg.position.set(lx, (topY - DIMS.tableThickness) / 2, DIMS.tableCenterZ + lz);
      leg.castShadow = true;
      g.add(leg);
    }
  }

  const netCanvas = document.createElement('canvas');
  netCanvas.width = 256;
  netCanvas.height = 64;
  const nctx = netCanvas.getContext('2d');
  if (nctx) {
    nctx.clearRect(0, 0, 256, 64);
    nctx.strokeStyle = 'rgba(20,22,25,0.9)';
    nctx.lineWidth = 2;
    for (let x = 0; x <= 256; x += 10) {
      nctx.beginPath(); nctx.moveTo(x, 0); nctx.lineTo(x, 64); nctx.stroke();
    }
    for (let y = 0; y <= 64; y += 10) {
      nctx.beginPath(); nctx.moveTo(0, y); nctx.lineTo(256, y); nctx.stroke();
    }
  }
  const netTex = new THREE.CanvasTexture(netCanvas);
  netTex.wrapS = THREE.RepeatWrapping;
  netTex.wrapT = THREE.RepeatWrapping;
  netTex.repeat.set(6, 1.2);

  const netMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.netHalfWidth * 2, DIMS.netTopY - topY),
    new THREE.MeshBasicMaterial({ map: netTex, transparent: true, side: THREE.DoubleSide, alphaTest: 0.05 }),
  );
  netMesh.position.set(0, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
  g.add(netMesh);

  const band = new THREE.Mesh(
    new THREE.BoxGeometry(DIMS.netHalfWidth * 2, 0.014, 0.006),
    new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.5 }),
  );
  band.position.set(0, DIMS.netTopY, DIMS.tableCenterZ);
  g.add(band);

  const postMat = new THREE.MeshStandardMaterial({ color: 0x30343a, roughness: 0.4, metalness: 0.6 });
  for (const px of [-DIMS.netHalfWidth, DIMS.netHalfWidth]) {
    const post = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, DIMS.netTopY - topY + 0.02, 12),
      postMat,
    );
    post.position.set(px, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
    g.add(post);
  }

  return g;
}

function createBall() {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(DIMS.ballRadius, 48, 32),
    new THREE.MeshStandardMaterial({
      color: COLORS.ball, roughness: 0.35, emissive: 0x555044, emissiveIntensity: 0.35,
    }),
  );
  mesh.castShadow = true;

  const TRAIL_N = 22;
  const positions = new Float32Array(TRAIL_N * 3);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const trail = new THREE.Points(
    geo,
    new THREE.PointsMaterial({
      color: 0xffffff, size: 0.016, transparent: true, opacity: 0.35, depthWrite: false,
    }),
  );
  let idx = 0;
  const trailUpdate = () => {
    positions[idx * 3] = mesh.position.x;
    positions[idx * 3 + 1] = mesh.position.y;
    positions[idx * 3 + 2] = mesh.position.z;
    idx = (idx + 1) % TRAIL_N;
    geo.attributes.position.needsUpdate = true;
  };

  return { mesh, trail, trailUpdate };
}

function createBlobShadow() {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(0.05, 20),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.3, depthWrite: false }),
  );
  m.rotation.x = -Math.PI / 2;
  m.renderOrder = 2;
  return m;
}

function createBounceMarkers() {
  const pool = [];
  for (let i = 0; i < 4; i++) {
    const m = new THREE.Mesh(
      new THREE.RingGeometry(0.02, 0.036, 20),
      new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, side: THREE.DoubleSide,
      }),
    );
    m.rotation.x = -Math.PI / 2;
    m.userData.t = 1;
    m.visible = false;
    m.renderOrder = 3;
    pool.push(m);
  }
  return pool;
}

function createScoreboard() {
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;

  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(1.7, 0.85),
    new THREE.MeshBasicMaterial({ map: tex }),
  );
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(1.76, 0.91, 0.04),
    new THREE.MeshStandardMaterial({ color: 0x101316, roughness: 0.6 }),
  );
  frame.position.z = -0.025;
  group.add(frame);
  group.add(panel);
  group.position.set(0, 1.95, DIMS.roomFrontZ + 0.9);

  let last = '';
  const update = (d) => {
    const key = `${d.player}|${d.ai}|${d.server}|${d.message}`;
    if (key === last) return;
    last = key;

    ctx.fillStyle = '#101418';
    ctx.fillRect(0, 0, 1024, 512);
    ctx.strokeStyle = '#2a3138';
    ctx.lineWidth = 10;
    ctx.strokeRect(10, 10, 1004, 492);

    ctx.fillStyle = '#8b949c';
    ctx.font = '600 34px system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('P I N G   P O N G   X R', 512, 70);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#e8b45a';
    ctx.font = '700 52px system-ui, sans-serif';
    ctx.fillText('TÚ', 150, 170);
    if (d.server === 'player') {
      ctx.beginPath();
      ctx.arc(118, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.textAlign = 'right';
    ctx.fillStyle = '#7fb069';
    ctx.font = '700 52px system-ui, sans-serif';
    ctx.fillText('CPU', 874, 170);
    if (d.server === 'ai') {
      ctx.beginPath();
      ctx.arc(906, 152, 13, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.textAlign = 'center';
    ctx.fillStyle = '#f2f4f6';
    ctx.font = '800 190px system-ui, sans-serif';
    ctx.fillText(`${d.player} : ${d.ai}`, 512, 340);

    ctx.fillStyle = '#c8ced4';
    ctx.font = '500 40px system-ui, sans-serif';
    const msg = d.message.length > 46 ? d.message.slice(0, 46) : d.message;
    ctx.fillText(msg, 512, 440);

    tex.needsUpdate = true;
  };

  update({ player: 0, ai: 0, server: 'player', message: '' });
  return { group, update };
}
