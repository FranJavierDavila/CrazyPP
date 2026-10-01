/* =====================================================================
 *  ORQUESTADOR · sesión WebXR, mandos Quest 3, saque con mano libre,
 *  háptica y bucle principal
 * ===================================================================== */
const BALL_HAND_LIFT = 0.08;   // bola "apoyada" sobre la palma de la mano libre
const SERVE_AI_LIFT = 0.16;    // bola en la "mano" de la IA

class PingPongGame {
  constructor(canvas, paddleModel, callbacks = {}) {
    this.canvas = canvas;
    this.callbacks = callbacks;
    this.disposed = false;

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight, false);
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.1;
    this.renderer.xr.enabled = true;
    this.renderer.xr.setReferenceSpaceType('local-floor');

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x0b0e11);
    this.scene.fog = new THREE.Fog(0x0b0e11, 9, 18);
    this.rig = new THREE.Group();
    this.scene.add(this.rig);

    // Entorno PBR para que la pala (materiales metálicos/texturizados) luzca real
    try {
      const pmrem = new THREE.PMREMGenerator(this.renderer);
      this.scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
      this.scene.environmentIntensity = 0.5;
    } catch { /* si falla, iluminación clásica */ }

    this.camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.05, 60);
    this.camera.position.set(2.2, 1.5, 1.4);
    this.rig.add(this.camera);

    this.audio = new GameAudio();
    this.rules = new Rules();
    this.ball = {
      pos: new THREE.Vector3(0, 1, DIMS.tableCenterZ + 0.4),
      vel: new THREE.Vector3(),
      spin: new THREE.Vector3(),
    };

    // seguimiento de ambos mandos (uno lleva la pala, otro la bola)
    this.paddleModelRef = paddleModel;
    this.controllerPaddles = [createPaddleSim('player', 0), createPaddleSim('player', 1)];
    this.paddleHand = 0;         // mando con la pala (0 izq / 1 der)
    this.manualHand = false;     // el usuario cambió de mano con A/X
    this.gripDown = [false, false];
    this.btn4Prev = [false, false];
    this.connected = [false, false];
    this.sources = [null, null];

    // IA: lado CPU (-Z) y "jugador demo" en escritorio (+Z)
    this.ai = new OpponentAI(
      AI_PRESETS.medium, -1,
      new THREE.Vector3(0, 1.05, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45),
    );
    this.demoAI = new OpponentAI(
      AI_PRESETS.easy, 1,
      new THREE.Vector3(0, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.70),
    );

    this.difficulty = 'medium';
    this.events = [];
    this.lastTime = -1;
    this.orbitAngle = 0.7;
    this.recenterFrames = 0;
    this.aiServeTimer = 1.3;
    this.demoServeTimer = 1.2;
    // saque del jugador: bola en la mano libre -> lanzamiento físico
    this.tossed = false;
    this.tossTimer = 0;
    this.tossReleaseY = 0;
    this.tossMaxY = 0;
    this.preVy = 0;
    this.aiToss = null;
    this.demoToss = null;

    this.buildScene(paddleModel);
    this.setupControllers();
    this.rules.startMatch();

    window.addEventListener('resize', this.onResize);
    this.renderer.xr.addEventListener('sessionstart', this.onSessionStart);
    this.renderer.xr.addEventListener('sessionend', this.onSessionEnd);
    this.renderer.setAnimationLoop(this.animate);
    window.__pingpong = this;
  }

  // ---------- Construcción ----------

  buildScene(paddleModel) {
    const hemi = new THREE.HemisphereLight(0xdfe8f0, 0x30271f, 0.85);
    this.rig.add(hemi);

    const dir = new THREE.DirectionalLight(0xffffff, 2.4);
    dir.position.set(2.2, 3.6, 0.6);
    dir.castShadow = true;
    dir.shadow.mapSize.set(1024, 1024);
    dir.shadow.camera.left = -3;
    dir.shadow.camera.right = 3;
    dir.shadow.camera.top = 3;
    dir.shadow.camera.bottom = -3;
    dir.shadow.camera.near = 0.5;
    dir.shadow.camera.far = 9;
    dir.shadow.bias = -0.0004;
    this.rig.add(dir);
    dir.target.position.set(0, 0.7, DIMS.tableCenterZ);
    this.rig.add(dir.target);

    this.rig.add(createRoom());
    this.rig.add(createTable());

    const { mesh, trail, trailUpdate } = createBall();
    this.ballMesh = mesh;
    this.trailUpdate = trailUpdate;
    this.ballMesh.position.copy(this.ball.pos);
    this.rig.add(mesh);
    this.rig.add(trail);

    this.blob = createBlobShadow();
    this.rig.add(this.blob);
    this.markers = createBounceMarkers();
    this.markerIdx = 0;
    for (const m of this.markers) this.rig.add(m);

    // Pala de la IA y del jugador demo: modelo GLB con la hoja en el origen.
    // Sin cuerpos: solo la pala flotante del rival (más limpio y no estorba).
    this.aiPaddleMesh = makePaddleVisual(paddleModel, 'center');
    this.rig.add(this.aiPaddleMesh);

    this.demoPaddleMesh = makePaddleVisual(paddleModel, 'center');
    this.rig.add(this.demoPaddleMesh);

    const sb = createScoreboard();
    this.scoreboardUpdate = sb.update;
    this.rig.add(sb.group);
  }

  setupControllers() {
    this.paddleMounts = [];
    this.grips = [];
    for (let i = 0; i < 2; i++) {
      const grip = this.renderer.xr.getControllerGrip(i);
      const targetRay = this.renderer.xr.getController(i);

      // pala (solo visible en el mando activo)
      const mount = new THREE.Group();
      mount.quaternion.copy(MOUNT_QUAT);
      mount.position.set(0, 0.012, 0.02);
      mount.add(makePaddleVisual(this.paddleModelRef, 'grip'));
      mount.visible = i === this.paddleHand;
      grip.add(mount);
      this.paddleMounts.push(mount);

      grip.addEventListener('connected', (e) => {
        this.connected[i] = true;
        this.sources[i] = e.data;
        if (e.data.handedness === 'right' && !this.manualHand) this.setPaddleHand(i);
        else if (!this.connected[this.paddleHand]) this.setPaddleHand(i);
      });
      grip.addEventListener('disconnected', () => {
        this.connected[i] = false;
        this.sources[i] = null;
      });

      const onSelect = () => this.onSelectStart(i);
      grip.addEventListener('selectstart', onSelect);
      targetRay.addEventListener('selectstart', onSelect);
      const onSqueezeStart = () => { this.gripDown[i] = true; };
      const onSqueezeEnd = () => {
        if (this.gripDown[i]) this.releaseBallHand(i);
        this.gripDown[i] = false;
      };
      grip.addEventListener('squeezestart', onSqueezeStart);
      grip.addEventListener('squeezeend', onSqueezeEnd);
      targetRay.addEventListener('squeezestart', onSqueezeStart);
      targetRay.addEventListener('squeezeend', onSqueezeEnd);

      this.rig.add(grip);
      this.rig.add(targetRay);
      this.grips.push(grip);
    }
  }

  setPaddleHand(i) {
    if (i === this.paddleHand) return;
    this.paddleHand = i;
    for (let k = 0; k < 2; k++) {
      if (this.paddleMounts[k]) this.paddleMounts[k].visible = k === this.paddleHand;
      const ps = this.controllerPaddles[k];
      ps.prev.copy(ps.pos);
      ps.vel.set(0, 0, 0);
    }
  }

  get ballHand() { return 1 - this.paddleHand; }

  // ---------- API pública ----------

  async enterVR() {
    this.audio.ensure();
    const xr = navigator.xr;
    if (!xr) throw new Error('Este navegador no soporta WebXR. Usa Meta Quest Browser.');
    const session = await xr.requestSession('immersive-vr', {
      optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking'],
    });
    await this.renderer.xr.setSession(session);
  }

  setDifficulty(d) {
    this.difficulty = d;
    this.ai.setConfig(AI_PRESETS[d]);
  }

  // ---------- Eventos XR ----------

  onResize = () => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h, false);
  };

  onSessionStart = () => {
    this.recenterFrames = 25;
    this.audio.ensure();
    this.rules.startMatch();
    this.ai.reset();
    this.demoAI.reset();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.aiServeTimer = 1.3;
    this.demoServeTimer = 1.4;
    this.callbacks.onXRState?.(true);
  };

  onSessionEnd = () => {
    this.rules.startMatch();
    this.resetToss();
    this.aiToss = null;
    this.demoToss = null;
    this.demoServeTimer = 1.4;
    this.callbacks.onXRState?.(false);
  };

  resetToss() {
    this.tossed = false;
    this.tossTimer = 0;
    this.gripDown[0] = false;
    this.gripDown[1] = false;
  }

  onSelectStart(i) {
    if (this.disposed) return;
    this.audio.ensure();
    if (!this.renderer.xr.isPresenting) return;

    if (this.rules.state === 'over') {
      this.rules.startMatch();
      this.resetToss();
      return;
    }
    // gatillo en la mano de la bola = saque asistido (con impulso mínimo)
    if (this.rules.state === 'serve' && this.rules.server === 'player' && !this.tossed && i === this.ballHand) {
      this.tossFromHand(i, true);
    }
  }

  /** Suelta la bola con la velocidad REAL de la mano (saque natural). */
  releaseBallHand(i) {
    if (this.rules.state !== 'serve' || this.rules.server !== 'player') return;
    if (this.tossed || i !== this.ballHand) return;
    if (!this.renderer.xr.isPresenting) return;
    const hand = this.controllerPaddles[i];
    if (!hand.active) return;
    const v = hand.vel;
    if (v.length() < 0.5 && v.y < 0.05) {
      this.rules.message = 'Suelta el GRIP lanzando la mano hacia arriba';
      return;
    }
    this.tossFromHand(i, false);
  }

  tossFromHand(i, assisted) {
    const hand = this.controllerPaddles[i];
    const v = new THREE.Vector3().copy(hand.vel);
    if (assisted && v.y < DIMS.serveAssistVy) {
      v.y = DIMS.serveAssistVy;
      v.x *= 0.4;
      v.z *= 0.4;
    }
    this.tossed = true;
    this.tossTimer = 0;
    this.tossReleaseY = this.ball.pos.y;
    this.tossMaxY = this.ball.pos.y;
    this.ball.vel.copy(v);
    this.ball.spin.set(0, 0, 0);
    this.rules.message = '¡Golpea la bola al caer!';
    this.audio.serve();
    this.haptic(i, 0.45);
  }

  haptic(index, strength) {
    const gp = this.sources[index]?.gamepad;
    const act = gp?.hapticActuators?.[0];
    try {
      act?.pulse?.(Math.min(1, Math.max(0.2, strength)), 45);
    } catch {
      /* algunos navegadores no lo soportan */
    }
  }

  // ---------- Bucle principal ----------

  animate = (time) => {
    if (this.disposed) return;
    const now = time * 0.001;
    const dt = this.lastTime < 0 ? 0.016 : Math.min(now - this.lastTime, 0.05);
    this.lastTime = now;

    const presenting = this.renderer.xr.isPresenting;

    if (presenting && this.recenterFrames > 0) {
      this.updateRecenter();
      this.recenterFrames--;
    }

    // 0) botón A/X: el mando donde se pulsa pasa a llevar la pala
    if (presenting) {
      for (let i = 0; i < 2; i++) {
        const gp = this.sources[i]?.gamepad;
        const b4 = !!gp?.buttons?.[4]?.pressed;
        if (b4 && !this.btn4Prev[i]) {
          this.manualHand = true;
          this.setPaddleHand(i);
        }
        this.btn4Prev[i] = b4;
      }
    }

    // 1) Palas de los mandos (solo en VR)
    if (presenting && this.grips) {
      for (let i = 0; i < 2; i++) {
        const ps = this.controllerPaddles[i];
        const grip = this.grips[i];
        ps.prev.copy(ps.pos);
        ps.pos.copy(grip.position);
        tmpQ.copy(grip.quaternion).multiply(MOUNT_QUAT);
        setPaddleBasis(ps, tmpQ);
        if (dt > 0) {
          tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt);
          ps.vel.lerp(tmpV, 0.55);
        }
        ps.active = this.connected[i];
      }
    }

    // 2) IA(s)
    const canHit = this.rules.state === 'rally';
    const playerPad = this.controllerPaddles[this.paddleHand];
    const oppPadX = presenting
      ? (playerPad.active ? playerPad.pos.x : 0)
      : this.demoAI.pos.x;
    const aiHit = this.ai.update(dt, this.ball, {
      canHit,
      validBounce: this.rules.validBounce,
      oppPadX,
    });
    let demoHit = null;
    if (!presenting) {
      demoHit = this.demoAI.update(dt, this.ball, {
        canHit,
        validBounce: this.rules.validBounce,
        oppPadX: this.ai.pos.x,
      });
    }
    if (aiHit) {
      this.ball.vel.copy(aiHit);
      this.processIntents(this.rules.registerPaddleHit('ai'));
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, aiHit.length() / 9),
      );
    }
    if (demoHit) {
      this.ball.vel.copy(demoHit);
      this.processIntents(this.rules.registerPaddleHit('player'));
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, demoHit.length() / 9),
      );
    }

    // 3) Preparación del saque
    let holdLock = false;
    if (this.rules.state === 'serve') {
      if (this.rules.server === 'player') {
        if (presenting) {
          if (!this.tossed) {
            // bola apoyada en la mano libre (cinemática pura)
            holdLock = true;
            const bh = this.controllerPaddles[this.ballHand];
            this.ball.vel.set(0, 0, 0);
            this.ball.spin.set(0, 0, 0);
            if (bh.active) {
              this.ball.pos.copy(bh.pos);
              this.ball.pos.y += BALL_HAND_LIFT;
            } else {
              this.ball.pos.set(0.3, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4);
            }
          } else {
            // bola lanzada: física real
            this.tossTimer += dt;
            this.preVy = this.ball.vel.y;
            if (this.tossMaxY < this.ball.pos.y) this.tossMaxY = this.ball.pos.y;
            if (this.tossTimer > 6) {
              this.resetToss();
              this.rules.message = 'Repite el lanzamiento';
            }
          }
        } else if (!this.demoToss) {
          holdLock = true;
          this.ball.vel.set(0, 0, 0);
          this.ball.spin.set(0, 0, 0);
          this.ball.pos.copy(this.demoAI.pos);
          this.ball.pos.y += SERVE_AI_LIFT;
          this.demoServeTimer -= dt;
          if (this.demoServeTimer <= 0) {
            this.demoToss = { timer: 0.5 };
            this.ball.vel.set(0, 2.3, 0.02);
            this.audio.serve();
          }
        } else {
          this.preVy = this.ball.vel.y;
          this.demoToss.timer -= dt;
          if (this.demoToss.timer <= 0) {
            this.demoToss = null;
            this.serveFromAI('player');
          }
        }
      } else if (!this.aiToss) {
        // la CPU sostiene la bola y luego la lanza
        holdLock = true;
        this.ball.vel.set(0, 0, 0);
        this.ball.spin.set(0, 0, 0);
        this.ball.pos.copy(this.ai.pos);
        this.ball.pos.y += SERVE_AI_LIFT;
        this.aiServeTimer -= dt;
        if (this.aiServeTimer <= 0) {
          this.aiToss = { timer: 0.5 };
          this.ball.vel.set(0, 2.3, -0.02);
          this.audio.serve();
        }
      } else {
        this.preVy = this.ball.vel.y;
        this.aiToss.timer -= dt;
        if (this.aiToss.timer <= 0) {
          this.aiToss = null;
          this.serveFromAI('ai');
        }
      }
    }

    // 4) Física (solo la pala del mando activo colisiona)
    this.events.length = 0;
    if (!holdLock) {
      const pads = [];
      if (presenting) {
        const ps = this.controllerPaddles[this.paddleHand];
        if (ps.active) pads.push(ps);
      }
      stepPhysics(dt, this.ball, pads, this.events);
    }

    // 5) Golpe de saque del jugador: validar regla ITTF
    if (presenting && this.tossed && this.rules.state === 'serve' && this.rules.server === 'player') {
      for (const e of this.events) {
        if (e.type !== 'paddle' || e.who !== 'player') continue;
        if (this.preVy > 0.05) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Golpea la bola cuando CAE, no cuando sube';
          break;
        }
        if (this.tossMaxY - this.tossReleaseY < DIMS.tossMinRise) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Lanza la bola al menos 16 cm hacia arriba';
          break;
        }
        if (this.ball.pos.z < DIMS.tableCenterZ + DIMS.tableHalfLength - DIMS.serveEndLineTol) {
          e.consumed = true;
          this.resetToss();
          this.rules.message = 'Saca desde detrás de la línea de fondo';
          break;
        }
        // golpe de saque válido
        e.consumed = true;
        this.tossed = false;
        this.rules.beginServeRally('player');
        this.haptic(e.paddleIndex ?? this.paddleHand, 0.6);
        break;
      }
      // lanzamiento fallido: la bola tocó algo sin ser golpeada
      if (this.tossed) {
        for (const e of this.events) {
          if (e.type === 'table' || e.type === 'floor' || e.type === 'wall') {
            this.resetToss();
            this.rules.message = 'Bola caída · repite el lanzamiento';
            break;
          }
        }
      }
    }

    // 6) Reglas y eventos
    const intents = this.rules.handleEvents(this.events);
    this.processIntents(intents);
    this.processIntents(this.rules.update(dt));
    this.processEvents(this.events);

    // 7) Sincronizar visuales
    this.ballMesh.position.copy(this.ball.pos);
    this.ballMesh.rotation.x += this.ball.spin.x * dt * 0.05;
    this.ballMesh.rotation.y += this.ball.spin.y * dt * 0.05;
    const ballHeld = holdLock;
    this.ballMesh.material.emissiveIntensity = ballHeld
      ? 0.75 + Math.sin(now * 6) * 0.25
      : 0.35;
    this.trailUpdate();
    this.updateBlobShadow();

    this.aiPaddleMesh.position.copy(this.ai.pos);
    this.aiPaddleMesh.lookAt(this.ball.pos);
    this.aiPaddleMesh.rotateX(0.18);
    this.demoPaddleMesh.position.copy(this.demoAI.pos);
    this.demoPaddleMesh.lookAt(this.ball.pos);
    this.demoPaddleMesh.rotateX(0.18);

    for (const m of this.markers) {
      if (!m.visible) continue;
      m.userData.t += dt * 2.4;
      if (m.userData.t >= 1) {
        m.visible = false;
        continue;
      }
      m.scale.setScalar(1 + m.userData.t * 1.6);
      m.material.opacity = 0.55 * (1 - m.userData.t);
    }

    this.scoreboardUpdate({
      player: this.rules.scorePlayer,
      ai: this.rules.scoreAi,
      server: this.rules.server,
      message: this.rules.message,
    });
    this.syncDom();

    // 8) Cámara de escritorio (órbita suave)
    if (!presenting) {
      this.orbitAngle += dt * 0.1;
      const r = 2.8;
      const cx = Math.sin(this.orbitAngle) * r;
      const cz = DIMS.tableCenterZ + Math.cos(this.orbitAngle) * r;
      this.camera.position.set(cx, 1.45 + Math.sin(this.orbitAngle * 0.6) * 0.25, cz);
      this.camera.lookAt(0, 0.95, DIMS.tableCenterZ);
    }

    // 9) Render
    this.renderer.render(this.scene, this.camera);
  };

  /** Recentrado: gira el mundo para que la mesa quede frente al usuario. */
  updateRecenter() {
    const f = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);
    if (Math.abs(f.x) + Math.abs(f.z) < 1e-4) return;
    this.rig.rotation.y = Math.atan2(f.x, f.z) - Math.PI;
  }

  /** Saque de una IA: trayectoria válida por simulación (bote propio + rival). */
  serveFromAI(side) {
    const ownSign = side === 'ai' ? -1 : 1;
    const { v, spin } = findServeVelocity(this.ball.pos, ownSign);
    this.ball.vel.copy(v);
    this.ball.spin.copy(spin);
    this.rules.beginServeRally(side);
    this.audio.serve();
  }

  updateBlobShadow() {
    const b = this.ball.pos;
    const over =
      Math.abs(b.x) < DIMS.tableHalfWidth + 0.06 &&
      Math.abs(b.z - DIMS.tableCenterZ) < DIMS.tableHalfLength + 0.06;
    const gy = over ? DIMS.tableTopY : 0;
    this.blob.position.set(b.x, gy + 0.004, b.z);
    const hgt = Math.max(0, b.y - gy);
    this.blob.scale.setScalar(THREE.MathUtils.clamp(1.15 - hgt * 0.45, 0.25, 1.15));
    this.blob.material.opacity = THREE.MathUtils.clamp(0.34 - hgt * 0.12, 0.04, 0.34);
  }

  flashMarker(pos) {
    const m = this.markers[this.markerIdx % this.markers.length];
    this.markerIdx++;
    m.position.set(pos.x, pos.y - DIMS.ballRadius + 0.004, pos.z);
    m.userData.t = 0;
    m.visible = true;
    m.scale.setScalar(1);
    m.material.opacity = 0.55;
  }

  processIntents(intents) {
    for (const it of intents) {
      switch (it.type) {
        case 'point':
          this.audio.point(it.winner === 'player');
          if (this.renderer.xr.isPresenting) {
            this.haptic(this.paddleHand, it.winner === 'player' ? 0.8 : 0.35);
          }
          break;
        case 'retry-serve':
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (this.rules.server === 'ai') this.aiServeTimer = 1.2;
          else this.demoServeTimer = 1.2;
          break;
        case 'serve':
          this.resetToss();
          this.aiToss = null;
          this.demoToss = null;
          if (it.server === 'ai') this.aiServeTimer = 1.3 + Math.random() * 0.6;
          else this.demoServeTimer = 1.4;
          break;
        case 'game-over':
          break;
      }
    }
  }

  processEvents(events) {
    for (const e of events) {
      const pan = THREE.MathUtils.clamp(e.pos.x / 2.5, -1, 1);
      switch (e.type) {
        case 'table':
          this.audio.tableBounce(pan, Math.min(1, e.speed / 6));
          this.flashMarker(e.pos);
          if (this.renderer.xr.isPresenting) this.haptic(this.paddleHand, 0.18);
          break;
        case 'net':
          this.audio.net(pan);
          break;
        case 'floor':
          this.audio.thud(pan, Math.min(1, e.speed / 5));
          break;
        case 'wall':
          this.audio.thud(pan, Math.min(0.5, e.speed / 6));
          break;
        case 'paddle':
          this.audio.paddle(pan, Math.min(1, e.speed / 9));
          if (e.paddleIndex !== undefined && e.paddleIndex >= 0) {
            this.haptic(e.paddleIndex, Math.min(1, e.speed / 8));
          }
          break;
      }
    }
  }

  syncDom() {
    const scoreKey = `${this.rules.scorePlayer}-${this.rules.scoreAi}-${this.rules.server}`;
    if (scoreKey !== this.lastSentScore) {
      this.lastSentScore = scoreKey;
      this.callbacks.onScore?.(this.rules.scorePlayer, this.rules.scoreAi, this.rules.server);
    }
    if (this.rules.message !== this.lastSentMessage) {
      this.lastSentMessage = this.rules.message;
      this.callbacks.onMessage?.(this.rules.message);
    }
  }
}

/* =====================================================================
 *  INTERFAZ · overlay, botón VR, dificultad y HUD
 * ===================================================================== */
const overlay = document.getElementById('overlay');
const statusEl = document.getElementById('status');
const vrbtn = document.getElementById('vrbtn');
const spectateBtn = document.getElementById('spectate');
const hud = document.getElementById('hud');
const hudScore = document.getElementById('hud-score');
const hudMsg = document.getElementById('hud-msg');
const hudInfo = document.getElementById('hud-info');

// Cargar el modelo de la pala antes de arrancar la escena
loadPaddleModel().then((paddleModel) => {
  const game = new PingPongGame(document.getElementById('c'), paddleModel, {
    onScore(player, ai) {
      hudScore.textContent = `${player} : ${ai}`;
    },
    onMessage(message) {
      hudMsg.textContent = message;
    },
    onXRState(inVR) {
      if (inVR) {
        overlay.classList.add('hidden');
        hud.classList.remove('show');
      } else {
        overlay.classList.remove('hidden');
        statusEl.textContent = 'Pausa · pulsa ENTRAR EN VR para continuar la partida.';
      }
    },
  });
  window.__game = game;

  // Compatibilidad WebXR
  if (navigator.xr && navigator.xr.isSessionSupported) {
    navigator.xr.isSessionSupported('immersive-vr')
      .then((ok) => {
        if (ok) {
          vrbtn.disabled = false;
          statusEl.textContent = '✅ Visor compatible detectado. Ponte las gafas y pulsa el botón.';
        } else {
          statusEl.textContent = '🖥️ Sin visor VR: disfruta del modo espectador (IA contra IA).';
        }
      })
      .catch(() => {
        statusEl.textContent = '🖥️ WebXR no disponible aquí: modo espectador activo.';
      });
  } else {
    statusEl.textContent = '🖥️ Este navegador no soporta WebXR: modo espectador activo.';
  }

  vrbtn.addEventListener('click', () => {
    vrbtn.disabled = true;
    statusEl.textContent = 'Iniciando sesión VR…';
    game.enterVR()
      .then(() => {
        vrbtn.disabled = false;
      })
      .catch((err) => {
        vrbtn.disabled = false;
        statusEl.textContent = '⚠️ ' + (err?.message || 'No se pudo iniciar la sesión VR.');
      });
  });

  document.querySelectorAll('.diff').forEach((btn) => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.diff').forEach((b) => b.classList.remove('active'));
      btn.classList.add('active');
      game.setDifficulty(btn.dataset.diff);
    });
  });
});

spectateBtn.addEventListener('click', () => {
  overlay.classList.add('hidden');
  hud.classList.add('show');
});
hudInfo.addEventListener('click', () => {
  overlay.classList.remove('hidden');
});
