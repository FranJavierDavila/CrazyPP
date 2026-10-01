/**
 * Oponente controlado por IA (también usado en modo demo para "el jugador").
 * Predice la trayectoria de la bola, se desplaza hacia el punto de intercepción
 * y devuelve con velocidad parabólica, con errores según la dificultad.
 */
import * as THREE from 'three'
import { DIMS, type AIConfig, type Side } from './constants'
import { computeShotVelocity, simulateIntercept, type BallSim } from './physics'

function gauss(): number {
  return (Math.random() * 2 - 1) * 0.7 + (Math.random() * 2 - 1) * 0.3
}

export class OpponentAI {
  private cfg: AIConfig
  /** +1 para el lado del jugador (+Z), -1 para el lado de la CPU (-Z). */
  private sign: number
  private planeZ: number
  private home: THREE.Vector3

  pos = new THREE.Vector3()
  private vel = new THREE.Vector3()
  private predict = new THREE.Vector3()
  private predictValid = false
  private predictTimer = 0
  private hitCooldown = 0

  constructor(cfg: AIConfig, sign: number, planeZ: number, home: THREE.Vector3) {
    this.cfg = cfg
    this.sign = sign
    this.planeZ = planeZ
    this.home = home.clone()
    this.pos.copy(home)
  }

  setConfig(cfg: AIConfig): void {
    this.cfg = cfg
  }

  reset(): void {
    this.pos.copy(this.home)
    this.vel.set(0, 0, 0)
    this.predictValid = false
    this.hitCooldown = 0
  }

  /**
   * Actualiza el movimiento. Devuelve la velocidad de golpeo si la IA alcanza
   * la bola en este frame (el llamador debe aplicarla a la bola).
   */
  update(dt: number, ball: BallSim, canHit: boolean, who: Side): THREE.Vector3 | null {
    this.hitCooldown -= dt
    const toward = ball.vel.z * this.sign < 0

    if (canHit && toward) {
      this.predictTimer -= dt
      if (this.predictTimer <= 0) {
        this.predictTimer = this.cfg.predictInterval
        const p = simulateIntercept(ball, this.planeZ, this.sign)
        if (p) {
          this.predict.copy(p)
          this.predictValid = true
        } else {
          this.predictValid = false
        }
      }
    } else {
      this.predictValid = false
    }

    // Objetivo de desplazamiento
    const target = new THREE.Vector3()
    if (this.predictValid) {
      target.set(
        THREE.MathUtils.clamp(this.predict.x, -0.8, 0.8),
        THREE.MathUtils.clamp(this.predict.y, DIMS.tableTopY + 0.04, 1.55),
        this.planeZ + this.sign * 0.06,
      )
    } else {
      target.set(
        this.home.x + ball.pos.x * 0.25,
        this.home.y,
        this.home.z + (toward ? this.sign * 0.25 : 0),
      )
    }

    const desired = target.clone().sub(this.pos)
    const dist = desired.length()
    const maxStep = this.cfg.maxSpeed * dt
    if (dist > 1e-4) {
      desired.multiplyScalar(Math.min(1, maxStep / dist))
      this.vel.copy(desired).divideScalar(Math.max(dt, 1e-4))
      this.pos.add(desired)
    } else {
      this.vel.set(0, 0, 0)
    }

    // Intento de golpe
    if (!canHit || !toward || this.hitCooldown > 0) return null
    const reach = 0.16
    const d2 = this.pos.distanceToSquared(ball.pos)
    // Debe estar en su propia mitad de la mesa (pasada la red)
    const onMyHalf = (ball.pos.z - DIMS.tableCenterZ) * this.sign > 0.12
    const goodHeight = ball.pos.y > DIMS.tableTopY - 0.05 && ball.pos.y < 1.6
    if (d2 > reach * reach || !onMyHalf || !goodHeight) return null

    // ¿Falla adrede? (más probable con bolas rápidas)
    const ballSpeed = ball.vel.length()
    const pMiss = this.cfg.missBase + Math.max(0, ballSpeed - 7) * 0.06
    this.hitCooldown = 0.5
    if (Math.random() < pMiss) return null

    // Devolución con objetivo aleatorio DENTRO de la mitad rival de la mesa
    // (toda la mesa está en Z negativa: mitad jugador [-1.6, -0.23], mitad CPU [-2.97, -1.6])
    const tx = (Math.random() * 2 - 1) * 0.42 + gauss() * this.cfg.errStd
    const tz =
      this.sign < 0
        ? -(0.35 + Math.random() * 0.95) // la CPU golpea hacia la mitad del jugador
        : -(1.75 + Math.random() * 0.95) // la demo golpea hacia la mitad de la CPU
    const T = this.cfg.minT + Math.random() * (this.cfg.maxT - this.cfg.minT)
    const targetPoint = new THREE.Vector3(tx, DIMS.tableTopY + DIMS.ballRadius, tz)
    const v = computeShotVelocity(ball.pos, targetPoint, T, this.cfg.maxShotSpeed)

    // Estadística: registrar quién golpeó (informativo)
    void who
    return v
  }
}
