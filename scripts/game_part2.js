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
    this.mode = 'match';            // 'match' (a 11) | 'survival' (rallyes infinitos)
    this.rallyesSurvived = 0;       // solo supervivencia: rallyes terminados
  }

  other(s) { return s === 'player' ? 'ai' : 'player'; }

  startMatch(mode) {
    this.mode = mode === 'survival' ? 'survival' : 'match';
    this.rallyesSurvived = 0;
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
    this.message = this.mode === 'survival'
      ? 'SUPERVIVENCIA · aguanta el rallye más largo'
      : 'Tu saque · la bola espera en tu mano libre';
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
    if (this.mode === 'survival') {
      // SUPERVIVENCIA: no hay puntos; lo que cuenta es el rallye terminado.
      // La CPU acelera con cada rallye (lo gestiona el juego con el intent).
      this.totalPoints++;
      this.rallyesSurvived++;
      this.state = 'point';
      this.stateTimer = 1.7;
      const golpes = this.rallyHits;
      this.message = golpes >= 8
        ? `¡Rallye de ${golpes} golpes! · ${cause}`
        : `Rallye de ${golpes} ${golpes === 1 ? 'golpe' : 'golpes'} · ${cause}`;
      return [{ type: 'point', winner, cause, survival: true, rallyHits: golpes }];
    }
    if (winner === 'player') this.scorePlayer++;
    else this.scoreAi++;
    this.totalPoints++;
    this.state = 'point';
    this.stateTimer = 2.2;
    const rallyTxt = this.rallyHits >= 6 ? ` · ${this.rallyHits} golpes` : '';
    this.message = winner === 'player' ? `¡Punto para ti! · ${cause}${rallyTxt}` : `Punto para la CPU · ${cause}${rallyTxt}`;
    return [{ type: 'point', winner, cause, rallyHits: this.rallyHits }];
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
        if (this.mode === 'survival') {
          // SUPERVIVENCIA: nunca se acaba el partido; bola nueva y a seguir
          this.state = 'serve';
          this.server = this.computeNextServer();
          this.message = this.server === 'player'
            ? 'Nueva bola en tu mano · ¡aguanta el rallye!'
            : 'Saque de la CPU… acelera cada vez más';
          intents.push({ type: 'serve', server: this.server });
          return intents;
        }
        const finished =
          (this.scorePlayer >= 11 || this.scoreAi >= 11) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= 2;
        if (finished) {
          this.state = 'over';
          this.stateTimer = 8;
          const winner = this.scorePlayer > this.scoreAi ? 'player' : 'ai';
          this.message = winner === 'player'
            ? `¡VICTORIA! · ${this.scorePlayer}-${this.scoreAi} · gatillo: revancha`
            : `DERROTA · ${this.scorePlayer}-${this.scoreAi} · gatillo: revancha`;
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
        this.startMatch(this.mode);   // reinicio automático en el MISMO modo
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

    if (ctx.holdTarget) {
      // saque propio: caminar a la posición reglamentaria y esperar allí
      tmpT.copy(ctx.holdTarget);
    } else if (this.predictValid) {
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

    // ---------- SELECCIÓN DE GOLPE (v2.11 · IA lista) ----------
    // Cuatro golpes según la situación: remate a bolas altas, dejada corta
    // si el rival está lejos de la mesa, push con slice a bolas bajas y
    // drive con lift (topspin) como golpe por defecto. Más un bloqueo
    // rápido para devolver bolas fuertes sin regalar velocidad.
    const oppDeep = ctx.oppPadZ !== undefined
      ? ((ctx.oppPadZ - DIMS.tableCenterZ) * -sign > DIMS.tableHalfLength * 0.3)
      : (Math.random() < 0.35);
    const high = ball.pos.y > 1.15;
    const low = ball.pos.y < DIMS.tableTopY + 0.16;
    let kind = 'drive';
    const rShot = Math.random();
    if (high && rShot < this.cfg.smash) {
      kind = 'smash';
    } else if (oppDeep && !low && (ctx.rallyHits || 0) >= 2 && rShot < this.cfg.smash + 0.32) {
      kind = 'dejada';
    } else if (low && rShot < 0.5) {
      kind = 'push';
    } else if (ballSpeed > 6.5 && rShot < 0.3) {
      kind = 'bloqueo';
    }

    let depthRel, T, spinX, speedMul = 1;
    switch (kind) {
      case 'smash':
        // palo seco y profundo: el punto suele acabar aquí
        depthRel = 0.72 + Math.random() * 0.32;
        T = this.cfg.minT * 0.8;
        spinX = -sign * (16 + Math.random() * 8);          // lift fuerte
        break;
      case 'dejada':
        // bola corta y flotada con slice para que "frene" al botar
        depthRel = 0.16 + Math.random() * 0.1;
        T = Math.max(this.cfg.minT, 0.92 + Math.random() * 0.25);
        spinX = sign * (6 + Math.random() * 5);            // slice (backspin)
        speedMul = 0.55;
        break;
      case 'push':
        depthRel = 0.55 + Math.random() * 0.3;
        T = this.cfg.minT + 0.14 + Math.random() * 0.2;
        spinX = sign * (5 + Math.random() * 6);            // slice
        speedMul = 0.8;
        break;
      case 'bloqueo':
        depthRel = 0.66 + Math.random() * 0.3;
        T = this.cfg.minT * 0.92;
        spinX = -sign * (10 + Math.random() * 6);
        speedMul = 0.92;
        break;
      default: // drive con lift: juego en largo (62%-112% hacia la línea)
        depthRel = 0.62 + Math.random() * 0.5;
        T = this.cfg.minT + Math.random() * (this.cfg.maxT - this.cfg.minT);
        spinX = -sign * (9 + Math.random() * 9);
    }

    const away = ctx.oppPadX !== undefined
      ? -Math.sign(ctx.oppPadX || (Math.random() - 0.5))
      : (Math.random() < 0.5 ? -1 : 1);
    let tx = away * (0.16 + Math.random() * 0.38) + gauss() * this.cfg.errStd * 0.8;
    // sorpresa: 14% de golpes "al cuerpo" (hacia su lado actual)
    if (kind !== 'dejada' && Math.random() < 0.14) {
      tx = -away * (0.05 + Math.random() * 0.12);
    }
    tx = THREE.MathUtils.clamp(tx, -0.55, 0.55);
    if (kind === 'dejada') tx *= 0.6;   // las dejadas buscan precisión, no ángulo

    const tz = DIMS.tableCenterZ - sign * depthRel * DIMS.tableHalfLength;
    const maxV = kind === 'smash'
      ? this.cfg.maxShotSpeed * 1.15
      : this.cfg.maxShotSpeed * speedMul;

    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const v = computeShotVelocity(ball.pos, tmpTarget, T, maxV);

    ball.spin.set(
      spinX,
      (Math.random() - 0.5) * 6,
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

  // refs para los TEMAS DE SALA (v2.14): applyTheme recolorea en vivo
  g.userData.floorMat = floorMat;
  g.userData.grid = grid;

  const wallMat = new THREE.MeshStandardMaterial({ color: COLORS.wall, roughness: 1 });
  g.userData.wallMat = wallMat;
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
  g.userData.ceilMat = ceil.material;

  const panelMat = new THREE.MeshBasicMaterial({ color: 0xf5efe2 });
  g.userData.panelMat = panelMat;
  for (const px of [-1.4, 1.4]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.4), panelMat);
    panel.rotation.x = Math.PI / 2;
    panel.position.set(px, DIMS.roomHeight - 0.01, -1.2);
    g.add(panel);
  }

  const stripMat = new THREE.MeshBasicMaterial({ color: COLORS.accentAmber });
  g.userData.stripMat = stripMat;
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
  g.userData.ringMat = ring.material;

  // ---------- VALLAS PUBLICITARIAS (v2.11 · ambiente de torneo) ----------
  // Vallas bajas tipo LED alrededor de la pista (van DENTRO de la sala:
  // en passthrough se ocultan con ella).
  const mkAd = (txt, bg, fg) => {
    const c = document.createElement('canvas');
    c.width = 512; c.height = 96;
    const a = c.getContext('2d');
    if (a) {
      a.fillStyle = bg;
      a.fillRect(0, 0, 512, 96);
      a.fillStyle = fg;
      a.font = '900 58px system-ui, sans-serif';
      a.textAlign = 'center';
      a.textBaseline = 'middle';
      a.fillText(txt, 256, 52);
    }
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    const m = new THREE.Mesh(
      new THREE.PlaneGeometry(1.35, 0.26),
      new THREE.MeshBasicMaterial({ map: t, side: THREE.DoubleSide }),
    );
    m.position.y = 0.13;
    return m;
  };
  const ads = [
    ['PING PONG XR', '#101418', '#e8b45a'],
    ['ARENA 480 Hz', '#e8b45a', '#101418'],
    ['MAGNUS SPORT', '#2f4a2a', '#9fd98a'],
    ['TOPSPIN CLUB', '#12324a', '#57c7ff'],
    ['QUEST 3 CUP', '#101418', '#f2f4f6'],
    ['EFECTO · SPIN', '#3a1c14', '#ff8a5c'],
    ['ITTF ARENA', '#1c1c2e', '#c9b3ff'],
  ];
  let adIdx = 0;
  const placeAd = (x, z, rotY) => {
    const [txt, bg, fg] = ads[adIdx % ads.length];
    adIdx++;
    const m = mkAd(txt, bg, fg);
    m.position.x = x;
    m.position.z = z;
    m.rotation.y = rotY;
    g.add(m);
  };
  // laterales (mirando a la mesa)
  placeAd(-1.95, -0.9, Math.PI / 2);
  placeAd(-1.95, -2.5, Math.PI / 2);
  placeAd(1.95, -0.9, -Math.PI / 2);
  placeAd(1.95, -2.5, -Math.PI / 2);
  // fondo de la CPU (mirando al jugador)
  placeAd(-0.8, -4.35, 0);
  placeAd(0.8, -4.35, 0);
  // detrás del jugador
  placeAd(0, 2.1, Math.PI);

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
  const colors = new Float32Array(TRAIL_N * 3);
  const ages = new Float32Array(TRAIL_N);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const trail = new THREE.Points(
    geo,
    new THREE.PointsMaterial({
      color: 0xffffff, size: 0.02, transparent: true, opacity: 0.55,
      vertexColors: true, depthWrite: false,
    }),
  );
  let idx = 0;
  const tmpSpinCross = new THREE.Vector3();
  /** Estela "de retransmisión": color según el EFECTO de la bola.
   *  naranja = lift/topspin (la Magnus la hunde), azul = slice/backspin
   *  (flota), violeta = lateral. Se desvanece con la edad del punto. */
  const trailUpdate = (ball, dt) => {
    positions[idx * 3] = mesh.position.x;
    positions[idx * 3 + 1] = mesh.position.y;
    positions[idx * 3 + 2] = mesh.position.z;
    ages[idx] = 0;
    let r = 0.75, g = 0.75, b = 0.75;
    if (ball && ball.spin && ball.vel) {
      tmpSpinCross.crossVectors(ball.spin, ball.vel);   // dirección de la Magnus
      const lift = tmpSpinCross.y;                      // + flota · - se hunde
      const force = Math.min(1, Math.abs(lift) / 9);
      if (force > 0.06) {
        if (lift < 0) {        // topspin → naranja
          r = 0.55 + 0.45 * force; g = 0.32 * force; b = 0.12 * force;
        } else {               // backspin → azul
          r = 0.16 * force; g = 0.55 * force; b = 0.55 + 0.45 * force;
        }
      }
      const side = Math.abs(ball.spin.y) / 18;
      if (side > 0.35 && force <= 0.06) {   // lateral → violeta
        r = 0.55; g = 0.3; b = 0.75;
      }
    }
    colors[idx * 3] = r;
    colors[idx * 3 + 1] = g;
    colors[idx * 3 + 2] = b;
    idx = (idx + 1) % TRAIL_N;
    for (let i = 0; i < TRAIL_N; i++) {
      ages[i] += dt;
      const fade = Math.max(0, 1 - ages[i] / 0.42);
      colors[i * 3] *= 0.86 + 0.14 * fade;
      colors[i * 3 + 1] *= 0.86 + 0.14 * fade;
      colors[i * 3 + 2] *= 0.86 + 0.14 * fade;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.color.needsUpdate = true;
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
    const key = d.mode === 'survival'
      ? `S|${d.rally}|${d.rallyes}|${d.best}|${d.server}|${d.message}`
      : `${d.player}|${d.ai}|${d.server}|${d.message}`;
    if (key === last) return;
    last = key;

    ctx.fillStyle = '#101418';
    ctx.fillRect(0, 0, 1024, 512);
    ctx.strokeStyle = '#2a3138';
    ctx.lineWidth = 10;
    ctx.strokeRect(10, 10, 1004, 492);

    ctx.textAlign = 'center';

    if (d.mode === 'survival') {
      // ---------- MODO SUPERVIVENCIA ----------
      ctx.fillStyle = '#e8b45a';
      ctx.font = '700 40px system-ui, sans-serif';
      ctx.fillText('S U P E R V I V E N C I A', 512, 78);

      ctx.fillStyle = '#f2f4f6';
      ctx.font = '800 210px system-ui, sans-serif';
      ctx.fillText(String(d.rally || 0), 512, 315);

      ctx.fillStyle = '#c8ced4';
      ctx.font = '600 44px system-ui, sans-serif';
      ctx.fillText(`golpes del rallye`, 512, 390);

      ctx.fillStyle = '#8b949c';
      ctx.font = '500 40px system-ui, sans-serif';
      ctx.fillText(`rallyes ${d.rallyes || 0}  ·  récord ${d.best || 0}`, 512, 452);
      tex.needsUpdate = true;
      return;
    }

    ctx.fillStyle = '#8b949c';
    ctx.font = '600 34px system-ui, sans-serif';
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

  update({ player: 0, ai: 0, server: 'player', message: '', mode: 'match', rally: 0, rallyes: 0, best: 0 });
  return { group, update };
}

/* =====================================================================
 *  PANEL DE AJUSTE DE PALA (modo entrenamiento en VR)
 *  Texto dinámico en CanvasTexture: nombre del agarre, valores actuales
 *  y controles. Solo se redibuja cuando cambian los valores.
 * ===================================================================== */
function roundRectPath(g, x, y, w, h, r) {
  g.beginPath();
  g.moveTo(x + r, y);
  g.arcTo(x + w, y, x + w, y + h, r);
  g.arcTo(x + w, y + h, x, y + h, r);
  g.arcTo(x, y + h, x, y, r);
  g.arcTo(x, y, x + w, y, r);
  g.closePath();
}

function createCalibPanel() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const g2 = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 4;
  const mat = new THREE.MeshBasicMaterial({
    map: tex, transparent: true, opacity: 0.95, side: THREE.DoubleSide, depthWrite: false,
  });
  const group = new THREE.Group();
  const plane = new THREE.Mesh(new THREE.PlaneGeometry(0.46, 0.46), mat);
  group.add(plane);

  function update(d) {
    g2.clearRect(0, 0, 512, 512);
    g2.fillStyle = 'rgba(13,17,23,0.93)';
    g2.strokeStyle = 'rgba(232,180,90,0.85)';
    g2.lineWidth = 4;
    roundRectPath(g2, 8, 8, 496, 496, 24);
    g2.fill();
    g2.stroke();

    g2.textAlign = 'left';
    g2.fillStyle = '#e8b45a';
    g2.font = 'bold 40px system-ui, sans-serif';
    g2.fillText('AJUSTE DE PALA', 34, 66);
    g2.fillStyle = '#9aa7b4';
    g2.font = '24px system-ui, sans-serif';
    g2.fillText('Agarre: ' + d.name, 34, 104);

    const o = d.off;
    const deg = (r) => ((r * 180) / Math.PI).toFixed(0);
    const mm = (m) => Math.round(m * 1000);
    g2.fillStyle = '#cfd8e0';
    g2.font = '21px ui-monospace, monospace';
    g2.fillText(`pos  ${mm(o.px)} · ${mm(o.py)} · ${mm(o.pz)} mm`, 34, 146);
    g2.fillText(`gir  ${deg(o.rx)}° · ${deg(o.ry)}° · ${deg(o.rz)}°`, 34, 176);

    const lines = [
      ['STICK D', 'girar / inclinar la cara'],
      ['GRIP D + stick D', 'rodar la pala'],
      ['STICK I', 'mover la pala'],
      ['GRIP I + stick I', 'acercar / alejar'],
      ['A', 'guardar este agarre'],
      ['B', 'cargar el siguiente'],
      ['X', 'volver al agarre natural'],
      ['GATILLO', 'lanzar bola de entrenamiento'],
      ['Y', 'volver al modo anterior'],
      ['B (en juego)', 'partido ⇄ supervivencia'],
      ['STICK ←→ (en juego)', 'tema de la sala'],
    ];
    let y = 224;
    for (const [k, v] of lines) {
      g2.fillStyle = '#e8b45a';
      g2.font = 'bold 20px system-ui, sans-serif';
      g2.fillText(k, 34, y);
      g2.fillStyle = '#aeb9c5';
      g2.font = '20px system-ui, sans-serif';
      g2.fillText(v, 196, y);
      y += 29;
    }
    tex.needsUpdate = true;
  }

  return { group, update };
}

/* =====================================================================
 *  FANFARRIA DE FIN DE PARTIDO · banner 3D flotante sobre la red con el
 *  resultado (¡VICTORIA! en dorado / DERROTA en gris azulado) y lluvia de
 *  confeti 3D cuando se gana. Se muestra durante todo el estado 'over'.
 * ===================================================================== */
function createFanfareBanner() {
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1.6, 0.8),
    // FrontSide: de detrás se ve transparente (en la órbita de la demo) en
    // lugar del texto en espejo; en VR el jugador siempre está de frente.
    new THREE.MeshBasicMaterial({
      map: tex, transparent: true, side: THREE.FrontSide, depthWrite: false,
    }),
  );
  group.add(mesh);
  group.position.set(0, 1.78, DIMS.tableCenterZ);
  group.visible = false;
  group.renderOrder = 5;

  function draw(win, pScore, aScore) {
    ctx.clearRect(0, 0, 1024, 512);
    // panel con borde festivo
    ctx.fillStyle = win ? 'rgba(43,26,4,0.94)' : 'rgba(12,16,22,0.94)';
    ctx.strokeStyle = win ? '#ffd35c' : '#5b6673';
    ctx.lineWidth = 14;
    roundRectPath(ctx, 14, 14, 996, 484, 40);
    ctx.fill();
    ctx.stroke();

    // confeti estático dibujado en el canvas (victoria)
    if (win) {
      const cols = ['#ffd35c', '#ff6b57', '#57c7ff', '#7be07b', '#e57be0', '#ffffff'];
      let seed = 7;
      const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
      for (let i = 0; i < 46; i++) {
        ctx.save();
        ctx.translate(rnd() * 1024, rnd() * 512);
        ctx.rotate(rnd() * Math.PI);
        ctx.fillStyle = cols[i % cols.length];
        ctx.globalAlpha = 0.85;
        ctx.fillRect(-7, -3, 14, 6);
        ctx.restore();
      }
      ctx.globalAlpha = 1;
    }

    // coronas (victoria) o nubes (derrota) dibujadas con paths
    const drawCrown = (cx, cy, s) => {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.fillStyle = win ? '#ffd35c' : '#5b6673';
      ctx.beginPath();
      ctx.moveTo(-s, s * 0.55);
      ctx.lineTo(-s, -s * 0.45);
      ctx.lineTo(-s * 0.5, 0);
      ctx.lineTo(0, -s * 0.75);
      ctx.lineTo(s * 0.5, 0);
      ctx.lineTo(s, -s * 0.45);
      ctx.lineTo(s, s * 0.55);
      ctx.closePath();
      ctx.fill();
      ctx.beginPath();
      ctx.arc(0, -s * 0.85, s * 0.14, 0, Math.PI * 2);
      ctx.arc(-s * 0.52, -s * 0.55, s * 0.12, 0, Math.PI * 2);
      ctx.arc(s * 0.52, -s * 0.55, s * 0.12, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    };
    const drawZzz = (cx, cy) => {
      ctx.save();
      ctx.translate(cx, cy);
      ctx.fillStyle = '#7d8894';
      ctx.font = '900 64px system-ui, sans-serif';
      ctx.textAlign = 'center';
      ctx.globalAlpha = 0.75;
      ctx.fillText('Z', 0, 0);
      ctx.font = '900 46px system-ui, sans-serif';
      ctx.fillText('Z', 42, -30);
      ctx.font = '900 32px system-ui, sans-serif';
      ctx.fillText('Z', 74, -54);
      ctx.restore();
    };
    if (win) {
      drawCrown(150, 170, 58);
      drawCrown(874, 170, 58);
    } else {
      drawZzz(150, 175);
      drawZzz(874, 175);
    }

    // título con sombra
    ctx.textAlign = 'center';     // ¡CLAVE! sin esto el texto sale desde x=512
    ctx.shadowColor = win ? 'rgba(255,196,40,0.9)' : 'rgba(0,0,0,0.8)';
    ctx.shadowBlur = 26;
    ctx.fillStyle = win ? '#ffd35c' : '#aab4c0';
    ctx.font = '900 150px system-ui, sans-serif';
    ctx.fillText(win ? '¡VICTORIA!' : 'DERROTA', 512, 250);
    ctx.shadowBlur = 0;

    // marcador final
    ctx.fillStyle = '#f2f4f6';
    ctx.font = '800 78px system-ui, sans-serif';
    ctx.fillText(`${pScore} - ${aScore}`, 512, 360);

    // subtítulo
    ctx.fillStyle = win ? 'rgba(255,224,150,0.95)' : '#939ea9';
    ctx.font = '600 42px system-ui, sans-serif';
    ctx.fillText(
      win ? '¡Partidazo! · gatillo para la revancha' : 'La próxima será tuya · gatillo: revancha',
      512, 440,
    );

    tex.needsUpdate = true;
  }

  return { group, draw };
}

function createConfetti() {
  const N = 120;
  const pos = new Float32Array(N * 3);
  const col = new Float32Array(N * 3);
  const fall = new Float32Array(N);
  const sway = new Float32Array(N);
  const phase = new Float32Array(N);
  const palette = [
    [1.0, 0.83, 0.36], [1.0, 0.42, 0.34], [0.34, 0.78, 1.0],
    [0.48, 0.88, 0.48], [0.9, 0.48, 0.88], [1.0, 1.0, 1.0],
  ];
  const topY = 2.3;
  const floorY = 0.8;
  const reset = (i, first) => {
    pos[i * 3] = (Math.random() * 2 - 1) * 0.95;
    pos[i * 3 + 1] = first ? floorY + Math.random() * (topY - floorY) : topY;
    pos[i * 3 + 2] = DIMS.tableCenterZ + (Math.random() * 2 - 1) * 1.15;
    fall[i] = 0.45 + Math.random() * 0.55;
    sway[i] = 0.12 + Math.random() * 0.2;
    phase[i] = Math.random() * Math.PI * 2;
    const c = palette[(Math.random() * palette.length) | 0];
    col[i * 3] = c[0]; col[i * 3 + 1] = c[1]; col[i * 3 + 2] = c[2];
  };
  for (let i = 0; i < N; i++) reset(i, true);

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const points = new THREE.Points(geo, new THREE.PointsMaterial({
    size: 0.03, vertexColors: true, transparent: true, opacity: 0.95, depthWrite: false,
  }));
  points.visible = false;
  points.renderOrder = 6;

  let t = 0;
  const update = (dt, active) => {
    if (!active) { points.visible = false; return; }
    points.visible = true;
    t += dt;
    for (let i = 0; i < N; i++) {
      pos[i * 3 + 1] -= fall[i] * dt;
      pos[i * 3] += Math.sin(t * 2.4 + phase[i]) * sway[i] * dt;
      pos[i * 3 + 2] += Math.cos(t * 1.8 + phase[i]) * sway[i] * dt * 0.6;
      if (pos[i * 3 + 1] < floorY) reset(i, false);
    }
    geo.attributes.position.needsUpdate = true;
  };

  return { points, update };
}

/** Mini-indicador del estado del audio (solo llama la atención si algo va
 *  mal): verde tenue "♪" cuando todo suena; ámbar/rojo con mensaje cuando el
 *  contexto está suspendido o mudo. Segunda línea de diagnóstico técnico:
 *  reloj de audio (T+ avanza / T- congelado), nº de contextos creados, foco
 *  de la ventana y sesión VR. Sirve de diagnóstico a la vista en VR. */
function createAudioStatus() {
  const group = new THREE.Group();
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 88;
  const ctx = canvas.getContext('2d');
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(0.84, 0.145),
    new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite: false }),
  );
  group.add(mesh);
  // Justo bajo el marcador (que está a y=1.95 con 0,85 m de alto)
  group.position.set(0, 1.44, DIMS.roomFrontZ + 0.9);

  let last = '';
  const update = (state, info) => {
    const alive = !info || info.alive !== false;
    const builds = info?.builds ?? 0;
    const focus = !!(info && info.focus);
    const sig = state + '|' + (alive ? 1 : 0) + '|' + (focus ? 1 : 0) + '|' + builds;
    if (sig === last) return;
    last = sig;
    ctx.clearRect(0, 0, 512, 88);
    ctx.fillStyle = 'rgba(8,10,13,0.72)';
    ctx.beginPath();
    ctx.roundRect(6, 6, 500, 76, 30);
    ctx.fill();
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    let color = '#69d97e';
    let label = '♪ audio: OK';
    if (state === 'suspended' || state === 'interrupted') {
      color = '#f0b429';
      label = '♪ audio: reconectando… (pulsa el gatillo)';
    } else if (state === 'closed' || state === 'failed') {
      color = '#ff6b57';
      label = '♪ audio: mudo — pulsa el gatillo';
    } else if (state !== 'running') {
      color = '#8b949c';
      label = '♪ audio: ' + state;
    } else if (!alive) {
      // estado 'running' pero reloj de audio congelado: grafo zombi
      color = '#f0b429';
      label = '♪ audio: reloj parado — pulsa el gatillo';
    }
    ctx.fillStyle = color;
    ctx.font = '700 34px system-ui, sans-serif';
    ctx.fillText(label, 256, 30);
    // línea 2 · diagnóstico técnico (reportar esto si el sonido falla)
    const bits = [alive ? 'T+' : 'T-', 'ctx ' + builds, 'foco ' + (focus ? 'sí' : 'NO')];
    if (info?.xr) bits.push('VR');
    ctx.fillStyle = 'rgba(255,255,255,0.55)';
    ctx.font = '600 25px ui-monospace, SFMono-Regular, Menlo, monospace';
    ctx.fillText(bits.join(' · '), 256, 64);
    tex.needsUpdate = true;
  };
  update('running');
  return { group, update };
}
