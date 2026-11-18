/**
 * PingPongGame: orquestador del juego.
 * - Sesión WebXR inmersiva con Meta Quest Browser (immersive-vr, local-floor).
 * - Seguimiento 1:1 de los mandos (grip space) con palas asociadas.
 * - Vibración háptica en los impactos, recalibrado automático de orientación
 *   (recentrado) al entrar en VR y modo demostración en escritorio.
 */
import * as THREE from 'three'
import { AI_PRESETS, DIMS, type Difficulty, type Side } from './constants'
import { GameAudio } from './audio'
import {
  createBall,
  createPaddle,
  createRoom,
  createScoreboard,
  createTable,
  MOUNT_QUAT,
} from './scene-builder'
import {
  computeShotVelocity,
  createPaddleSim,
  setPaddleBasis,
  stepPhysics,
  type BallSim,
  type PaddleSim,
  type PhysEvent,
} from './physics'
import { Rules, type RulesIntent } from './rules'
import { OpponentAI } from './ai'

export interface GameCallbacks {
  onScore?(player: number, ai: number, server: Side): void
  onMessage?(message: string): void
  onXRState?(inVR: boolean): void
}

interface HapticActuator {
  pulse?(intensity: number, duration: number): Promise<boolean> | boolean
}
type GamepadWithHaptics = Gamepad & { hapticActuators?: HapticActuator[] }

const SERVE_OFFSET = new THREE.Vector3(0, 0.13, 0)
const tmpQ = new THREE.Quaternion()
const tmpV = new THREE.Vector3()
const tmpTarget = new THREE.Vector3()

export class PingPongGame {
  private canvas: HTMLCanvasElement
  private callbacks: GameCallbacks
  private renderer: THREE.WebGLRenderer
  private scene = new THREE.Scene()
  private rig = new THREE.Group()
  private camera: THREE.PerspectiveCamera

  private audio = new GameAudio()
  private rules = new Rules()
  private ball: BallSim = { pos: new THREE.Vector3(0, 1, DIMS.tableCenterZ + 0.4), vel: new THREE.Vector3() }
  private ballMesh!: THREE.Mesh
  private trailUpdate!: () => void

  private controllerPaddles: [PaddleSim, PaddleSim] = [
    createPaddleSim('player', 0),
    createPaddleSim('player', 1),
  ]
  private grips: [THREE.Group, THREE.Group] | null = null
  private connected: [boolean, boolean] = [false, false]
  private sources: (XRInputSource | null)[] = [null, null]
  private attachHand: 0 | 1 = 0

  private ai: OpponentAI
  private demoAI: OpponentAI
  private aiPaddleMesh!: THREE.Group
  private demoPaddleMesh!: THREE.Group

  private scoreboardUpdate: (d: { player: number; ai: number; server: Side; message: string }) => void

  private difficulty: Difficulty = 'medium'
  private events: PhysEvent[] = []
  private lastTime = -1
  private orbitAngle = 0.7
  private recenterFrames = 0
  private aiServeTimer = 0
  private demoServeTimer = 1.2
  private lastSentScore = ''
  private lastSentMessage = ''
  private disposed = false

  constructor(canvas: HTMLCanvasElement, callbacks: GameCallbacks = {}) {
    this.canvas = canvas
    this.callbacks = callbacks

    this.renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      powerPreference: 'high-performance',
      preserveDrawingBuffer: true,
    })
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    this.renderer.setSize(window.innerWidth, window.innerHeight, false)
    this.renderer.shadowMap.enabled = true
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping
    this.renderer.toneMappingExposure = 1.1
    this.renderer.xr.enabled = true
    this.renderer.xr.setReferenceSpaceType('local-floor')

    this.scene.background = new THREE.Color(0x0b0e11)
    this.scene.fog = new THREE.Fog(0x0b0e11, 9, 18)
    this.scene.add(this.rig)

    this.camera = new THREE.PerspectiveCamera(
      60,
      window.innerWidth / window.innerHeight,
      0.05,
      60,
    )
    this.camera.position.set(2.2, 1.5, 1.4)
    this.rig.add(this.camera)

    this.buildScene()

    // IA: lado CPU (-Z) y "jugador demo" en escritorio (+Z)
    this.ai = new OpponentAI(AI_PRESETS.medium, -1, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.15, new THREE.Vector3(0, 1.05, DIMS.tableCenterZ - DIMS.tableHalfLength - 0.45))
    this.demoAI = new OpponentAI(AI_PRESETS.easy, 1, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.15, new THREE.Vector3(0, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.55))

    const sb = createScoreboard()
    this.scoreboardUpdate = sb.update
    this.rig.add(sb.group)

    this.setupControllers()
    this.rules.startMatch()

    window.addEventListener('resize', this.onResize)
    this.renderer.xr.addEventListener('sessionstart', this.onSessionStart)
    this.renderer.xr.addEventListener('sessionend', this.onSessionEnd)
    this.renderer.setAnimationLoop(this.animate)
    // Expuesto para depuración y verificación automatizada
    ;(window as unknown as { __pingpong?: PingPongGame }).__pingpong = this
  }

  // ---------- Construcción de escena ----------

  private buildScene(): void {
    const hemi = new THREE.HemisphereLight(0xdfe8f0, 0x30271f, 0.85)
    this.rig.add(hemi)

    const dir = new THREE.DirectionalLight(0xffffff, 2.4)
    dir.position.set(2.2, 3.6, 0.6)
    dir.castShadow = true
    dir.shadow.mapSize.set(1024, 1024)
    dir.shadow.camera.left = -3
    dir.shadow.camera.right = 3
    dir.shadow.camera.top = 3
    dir.shadow.camera.bottom = -3
    dir.shadow.camera.near = 0.5
    dir.shadow.camera.far = 9
    dir.shadow.bias = -0.0004
    this.rig.add(dir)
    dir.target.position.set(0, 0.7, DIMS.tableCenterZ)
    this.rig.add(dir.target)

    this.rig.add(createRoom())
    this.rig.add(createTable())

    const { mesh, trail, trailUpdate } = createBall()
    this.ballMesh = mesh
    this.trailUpdate = trailUpdate
    this.ballMesh.position.copy(this.ball.pos)
    this.rig.add(mesh)
    this.rig.add(trail)

    this.aiPaddleMesh = createPaddle()
    this.aiPaddleMesh.rotation.x = 0.12
    this.rig.add(this.aiPaddleMesh)

    this.demoPaddleMesh = createPaddle()
    this.demoPaddleMesh.rotation.y = Math.PI
    this.demoPaddleMesh.rotation.x = 0.12
    this.rig.add(this.demoPaddleMesh)
  }

  private setupControllers(): void {
    const grips: THREE.Group[] = []
    for (let i = 0; i < 2; i++) {
      const grip = this.renderer.xr.getControllerGrip(i)
      const targetRay = this.renderer.xr.getController(i)

      const mount = new THREE.Group()
      mount.quaternion.copy(MOUNT_QUAT)
      mount.position.set(0, 0.015, -0.08)
      mount.add(createPaddle())
      grip.add(mount)

      grip.addEventListener('connected', ((e: CustomEvent<XRInputSource>) => {
        this.connected[i] = true
        this.sources[i] = e.data
        if (!this.connected[1 - this.attachHand] || e.data.handedness === 'right') {
          this.attachHand = i as 0 | 1
        }
      }) as EventListener)
      grip.addEventListener('disconnected', () => {
        this.connected[i] = false
        this.sources[i] = null
      })
      const onSelect = () => this.onSelectStart(i)
      grip.addEventListener('selectstart', onSelect)
      targetRay.addEventListener('selectstart', onSelect)

      this.rig.add(grip)
      this.rig.add(targetRay)
      grips.push(grip)
    }
    this.grips = [grips[0], grips[1]]
  }

  // ---------- API pública ----------

  async enterVR(): Promise<void> {
    this.audio.ensure()
    const xr = (navigator as Navigator & { xr?: XRSystem }).xr
    if (!xr) throw new Error('Este navegador no soporta WebXR. Usa Meta Quest Browser.')
    const session = await xr.requestSession('immersive-vr', {
      optionalFeatures: ['local-floor', 'bounded-floor', 'hand-tracking'],
    })
    await this.renderer.xr.setSession(session)
  }

  setDifficulty(d: Difficulty): void {
    this.difficulty = d
    this.ai.setConfig(AI_PRESETS[d])
  }

  getDifficulty(): Difficulty {
    return this.difficulty
  }

  dispose(): void {
    this.disposed = true
    this.renderer.setAnimationLoop(null)
    window.removeEventListener('resize', this.onResize)
    this.renderer.xr.removeEventListener('sessionstart', this.onSessionStart)
    this.renderer.xr.removeEventListener('sessionend', this.onSessionEnd)
    this.audio.dispose()
    this.renderer.dispose()
  }

  // ---------- Eventos XR ----------

  private onResize = (): void => {
    const w = window.innerWidth
    const h = window.innerHeight
    this.camera.aspect = w / h
    this.camera.updateProjectionMatrix()
    this.renderer.setSize(w, h, false)
  }

  private onSessionStart = (): void => {
    this.recenterFrames = 25
    this.audio.ensure()
    this.rules.startMatch()
    this.ai.reset()
    this.demoServeTimer = 1.2
    this.callbacks.onXRState?.(true)
  }

  private onSessionEnd = (): void => {
    this.rules.startMatch()
    this.demoServeTimer = 1.4
    this.callbacks.onXRState?.(false)
  }

  private onSelectStart(i: number): void {
    if (this.disposed) return
    this.audio.ensure()
    if (!this.renderer.xr.isPresenting) return
    if (this.rules.state !== 'serve' || this.rules.server !== 'player') return
    if (!this.connected[i] || !this.controllerPaddles[i].active) return

    this.attachHand = i as 0 | 1
    this.launchPlayerServe()
  }

  private launchPlayerServe(): void {
    const pad = this.controllerPaddles[this.attachHand]
    const v = tmpV.copy(pad.vel).multiplyScalar(1.35)
    v.addScaledVector(pad.normal, 2.1)
    v.y += 0.6
    // El saque siempre viaja hacia el lado de la CPU
    v.z = Math.min(v.z, -2.0)
    let sp = v.length()
    if (sp < 3.2) {
      v.multiplyScalar(3.2 / Math.max(sp, 0.01))
      sp = 3.2
    }
    if (sp > 10) v.multiplyScalar(10 / sp)

    this.ball.pos.copy(pad.pos).addScaledVector(pad.normal, DIMS.ballRadius + 0.006)
    this.ball.vel.copy(v)
    this.rules.beginRally('player', true)
    this.audio.serve()
    this.haptic(this.attachHand, 0.6)
  }

  private haptic(index: number, strength: number): void {
    const gp = this.sources[index]?.gamepad as GamepadWithHaptics | undefined | null
    const act = gp?.hapticActuators?.[0]
    try {
      act?.pulse?.(Math.min(1, Math.max(0.2, strength)), 45)
    } catch {
      /* algunos navegadores no lo soportan */
    }
  }

  // ---------- Bucle principal ----------

  private animate = (time: number): void => {
    if (this.disposed) return
    const now = time * 0.001
    const dt = this.lastTime < 0 ? 0.016 : Math.min(now - this.lastTime, 0.05)
    this.lastTime = now

    const presenting = this.renderer.xr.isPresenting

    if (presenting && this.recenterFrames > 0) {
      this.updateRecenter()
      this.recenterFrames--
    }

    // 1) Palas de los mandos (solo en VR)
    if (presenting && this.grips) {
      for (let i = 0; i < 2; i++) {
        const ps = this.controllerPaddles[i]
        const grip = this.grips[i]
        ps.prev.copy(ps.pos)
        ps.pos.copy(grip.position)
        tmpQ.copy(grip.quaternion).multiply(MOUNT_QUAT)
        setPaddleBasis(ps, tmpQ)
        if (dt > 0) {
          tmpV.copy(ps.pos).sub(ps.prev).divideScalar(dt)
          ps.vel.lerp(tmpV, 0.55)
        }
        ps.active = this.connected[i]
      }
    }

    // 2) IA(s)
    const canHit = this.rules.state === 'rally'
    const aiHit = this.ai.update(dt, this.ball, canHit, 'ai')
    let demoHit: THREE.Vector3 | null = null
    if (!presenting) {
      demoHit = this.demoAI.update(dt, this.ball, canHit, 'player')
    }
    if (aiHit) {
      this.ball.vel.copy(aiHit)
      this.rules.registerPaddleHit('ai')
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, aiHit.length() / 9),
      )
    }
    if (demoHit) {
      this.ball.vel.copy(demoHit)
      this.rules.registerPaddleHit('player')
      this.audio.paddle(
        THREE.MathUtils.clamp(this.ball.pos.x / 2.5, -1, 1),
        Math.min(1, demoHit.length() / 9),
      )
    }

    // 3) Preparación del saque
    if (this.rules.state === 'serve') {
      this.ball.vel.set(0, 0, 0)
      if (this.rules.server === 'player') {
        if (presenting) {
          const pad = this.controllerPaddles[this.attachHand]
          if (pad.active) this.ball.pos.copy(pad.pos).add(SERVE_OFFSET)
        } else {
          this.ball.pos.copy(this.demoAI.pos).add(SERVE_OFFSET)
          this.demoServeTimer -= dt
          if (this.demoServeTimer <= 0) this.serveFromAI(this.demoAI, 'player')
        }
      } else {
        this.ball.pos.copy(this.ai.pos).add(SERVE_OFFSET)
        this.aiServeTimer -= dt
        if (this.aiServeTimer <= 0) this.serveFromAI(this.ai, 'ai')
      }
    }

    // 4) Física (solo las palas de los mandos colisionan físicamente)
    this.events.length = 0
    const pads: PaddleSim[] = []
    if (presenting) {
      for (const ps of this.controllerPaddles) if (ps.active) pads.push(ps)
    }
    stepPhysics(dt, this.ball, pads, this.events)

    // 5) Reglas y eventos
    const intents = this.rules.handleEvents(this.events)
    this.processIntents(intents)
    this.processIntents(this.rules.update(dt))
    this.processEvents(this.events)

    // 6) Sincronizar visuales
    this.ballMesh.position.copy(this.ball.pos)
    this.trailUpdate()
    this.aiPaddleMesh.position.copy(this.ai.pos)
    this.demoPaddleMesh.position.copy(this.demoAI.pos)
    this.scoreboardUpdate({
      player: this.rules.scorePlayer,
      ai: this.rules.scoreAi,
      server: this.rules.server,
      message: this.rules.message,
    })
    this.syncDom()

    // 7) Cámara de escritorio (órbita suave)
    if (!presenting) {
      this.orbitAngle += dt * 0.1
      const r = 2.8
      const cx = Math.sin(this.orbitAngle) * r
      const cz = DIMS.tableCenterZ + Math.cos(this.orbitAngle) * r
      this.camera.position.set(cx, 1.45 + Math.sin(this.orbitAngle * 0.6) * 0.25, cz)
      this.camera.lookAt(0, 0.95, DIMS.tableCenterZ)
    }

    // 8) Render (en XR usa la cámara del visor automáticamente)
    this.renderer.render(this.scene, this.camera)
  }

  /** Recentrada: gira el mundo para que la mesa quede frente al usuario. */
  private updateRecenter(): void {
    const f = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion)
    if (Math.abs(f.x) + Math.abs(f.z) < 1e-4) return
    this.rig.rotation.y = Math.atan2(f.x, f.z) - Math.PI
  }

  private serveFromAI(who: OpponentAI, side: Side): void {
    // La mesa completa está en Z negativa. El saque debe botar en la mitad del receptor:
    // si sirve la CPU -> bota en la mitad del jugador [-1.3, -0.35];
    // si sirve el jugador demo -> bota en la mitad de la CPU [-2.8, -1.75].
    const tx = (Math.random() * 2 - 1) * 0.4
    const tz = side === 'ai' ? -(0.35 + Math.random() * 0.95) : -(1.75 + Math.random() * 1.05)
    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz)
    const v = computeShotVelocity(who.pos, tmpTarget, 0.82, side === 'ai' ? 6.5 : 5.5)
    this.ball.pos.copy(who.pos)
    this.ball.vel.copy(v)
    this.rules.beginRally(side, true)
    this.audio.serve()
  }

  private processIntents(intents: RulesIntent[]): void {
    for (const it of intents) {
      switch (it.type) {
        case 'point':
          this.audio.point(it.winner === 'player')
          if (this.renderer.xr.isPresenting) {
            this.haptic(this.attachHand, it.winner === 'player' ? 0.8 : 0.35)
          }
          break
        case 'retry-serve':
          this.demoServeTimer = 1.2
          break
        case 'serve':
          if (it.server === 'ai') this.aiServeTimer = 1.3 + Math.random() * 0.6
          else this.demoServeTimer = 1.4
          break
        case 'game-over':
          break
      }
    }
  }

  private processEvents(events: PhysEvent[]): void {
    for (const e of events) {
      const pan = THREE.MathUtils.clamp(e.pos.x / 2.5, -1, 1)
      switch (e.type) {
        case 'table':
          this.audio.tableBounce(pan, Math.min(1, e.speed / 6))
          break
        case 'net':
          this.audio.net(pan)
          break
        case 'floor':
          this.audio.thud(pan, Math.min(1, e.speed / 5))
          break
        case 'wall':
          this.audio.thud(pan, Math.min(0.5, e.speed / 6))
          break
        case 'paddle':
          this.audio.paddle(pan, Math.min(1, e.speed / 9))
          if (e.paddleIndex !== undefined && e.paddleIndex >= 0) {
            this.haptic(e.paddleIndex, Math.min(1, e.speed / 8))
          }
          break
      }
    }
  }

  private syncDom(): void {
    const scoreKey = `${this.rules.scorePlayer}-${this.rules.scoreAi}-${this.rules.server}`
    if (scoreKey !== this.lastSentScore) {
      this.lastSentScore = scoreKey
      this.callbacks.onScore?.(this.rules.scorePlayer, this.rules.scoreAi, this.rules.server)
    }
    if (this.rules.message !== this.lastSentMessage) {
      this.lastSentMessage = this.rules.message
      this.callbacks.onMessage?.(this.rules.message)
    }
  }
}
