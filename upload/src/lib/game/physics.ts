/**
 * Motor de física de la bola: integración semi-implícita con sub-pasos fijos,
 * colisión barrida (swept) pala-bola, rebotes en mesa, red, suelo y paredes.
 * Todo el cálculo ocurre en el espacio local del "rig" del jugador.
 */
import * as THREE from 'three'
import { DIMS } from './constants'

export type PhysEventType = 'table' | 'net' | 'floor' | 'wall' | 'paddle'

export interface PhysEvent {
  type: PhysEventType
  /** Lado de la mesa donde rebota (solo 'table'). */
  side?: 'player' | 'ai'
  /** Quién golpeó con la pala (solo 'paddle'). */
  who?: 'player' | 'ai'
  speed: number
  pos: THREE.Vector3
  paddleIndex?: number
}

export interface PaddleSim {
  pos: THREE.Vector3
  prev: THREE.Vector3
  vel: THREE.Vector3
  /** Base ortonormal de la pala en el espacio del rig. */
  normal: THREE.Vector3
  right: THREE.Vector3
  up: THREE.Vector3
  cooldown: number
  who: 'player' | 'ai'
  index: number
  active: boolean
}

export interface BallSim {
  pos: THREE.Vector3
  vel: THREE.Vector3
}

const MAX_SUBSTEP_DT = 1 / 240
const tmpPrev = new THREE.Vector3()
// Vectores de trabajo exclusivos de collidePaddle
const padPos = new THREE.Vector3()
const relPrev = new THREE.Vector3()
const relNow = new THREE.Vector3()
const crossPoint = new THREE.Vector3()
const relVel = new THREE.Vector3()

export function createPaddleSim(who: 'player' | 'ai', index: number): PaddleSim {
  return {
    pos: new THREE.Vector3(),
    prev: new THREE.Vector3(),
    vel: new THREE.Vector3(),
    normal: new THREE.Vector3(0, 0, 1),
    right: new THREE.Vector3(1, 0, 0),
    up: new THREE.Vector3(0, 1, 0),
    cooldown: 0,
    who,
    index,
    active: false,
  }
}

/** Actualiza la base ortonormal de la pala a partir de un quaternion (espacio rig). */
export function setPaddleBasis(p: PaddleSim, q: THREE.Quaternion): void {
  p.normal.set(0, 0, 1).applyQuaternion(q)
  p.right.set(1, 0, 0).applyQuaternion(q)
  p.up.set(0, 1, 0).applyQuaternion(q)
}

function collidePaddle(ball: BallSim, pad: PaddleSim, k: number, events: PhysEvent[]): void {
  // Posición interpolada de la pala dentro del frame (pad.prev -> pad.pos)
  padPos.copy(pad.prev).lerp(pad.pos, k)

  // Distancia firmada de la bola (antes y ahora) al plano de la pala
  relPrev.copy(tmpPrev).sub(padPos)
  const dPrev = relPrev.dot(pad.normal)
  relNow.copy(ball.pos).sub(padPos)
  const dNow = relNow.dot(pad.normal)

  const crossing = dPrev > 0 !== dNow > 0
  const touching = Math.abs(dNow) <= DIMS.ballRadius + 0.012
  if (!crossing && !touching) return

  // Punto de cruce con el plano de la pala
  if (crossing) {
    const t = Math.min(1, Math.max(0, dPrev / (dPrev - dNow)))
    crossPoint.copy(tmpPrev).lerp(ball.pos, t)
  } else {
    crossPoint.copy(ball.pos)
  }

  // Coordenadas locales del cruce en la superficie de la pala
  const lx = relNow.copy(crossPoint).sub(padPos).dot(pad.right)
  const ly = relNow.dot(pad.up)
  const reach = DIMS.bladeRadius + DIMS.ballRadius
  if (lx * lx + ly * ly > reach * reach) return

  // Velocidad relativa normal: solo si la bola se acerca a la cara frontal
  const vRelN = relVel.copy(ball.vel).sub(pad.vel).dot(pad.normal)
  if (vRelN >= 0) return

  // Reflexión con pala "infinitamente masiva" en movimiento
  ball.vel.addScaledVector(pad.normal, -(1 + DIMS.paddleRestitution) * vRelN)

  // Velocidad mínima de salida para jugabilidad
  const vn = ball.vel.dot(pad.normal)
  if (vn < 1.5) ball.vel.addScaledVector(pad.normal, 1.5 - vn)

  // Límite de velocidad
  const sp = ball.vel.length()
  if (sp > DIMS.maxBallSpeed) ball.vel.multiplyScalar(DIMS.maxBallSpeed / sp)

  // Colocar la bola sobre la superficie frontal de la pala
  const front = DIMS.ballRadius + 0.002
  ball.pos
    .copy(padPos)
    .addScaledVector(pad.normal, front)
    .addScaledVector(pad.right, lx)
    .addScaledVector(pad.up, ly)

  pad.cooldown = DIMS.paddleHitCooldown
  events.push({
    type: 'paddle',
    who: pad.who,
    speed: Math.abs(vRelN),
    pos: ball.pos.clone(),
    paddleIndex: pad.index,
  })
}

function collideTable(ball: BallSim, prevY: number, events: PhysEvent[]): void {
  const topR = DIMS.tableTopY + DIMS.ballRadius
  const { pos, vel } = ball
  const C = DIMS.tableCenterZ
  const inX = Math.abs(pos.x) <= DIMS.tableHalfWidth + DIMS.ballRadius * 0.5
  const inZ = Math.abs(pos.z - C) <= DIMS.tableHalfLength + DIMS.ballRadius * 0.5

  // Rebote en la superficie superior
  if (vel.y < 0 && prevY >= topR && pos.y < topR && inX && Math.abs(pos.z - C) <= DIMS.tableHalfLength) {
    pos.y = topR
    const impact = -vel.y
    vel.y = impact * DIMS.tableRestitution
    vel.x *= DIMS.tableFriction
    vel.z *= DIMS.tableFriction
    events.push({
      type: 'table',
      side: pos.z > C ? 'player' : 'ai',
      speed: impact,
      pos: pos.clone(),
    })
    return
  }

  // Choque lateral contra el canto de la mesa
  const insideSlab =
    Math.abs(pos.x) < DIMS.tableHalfWidth + DIMS.ballRadius &&
    Math.abs(pos.z - C) < DIMS.tableHalfLength + DIMS.ballRadius &&
    pos.y > DIMS.tableTopY - DIMS.tableThickness - DIMS.ballRadius &&
    pos.y < topR
  if (insideSlab) {
    const penX = DIMS.tableHalfWidth + DIMS.ballRadius - Math.abs(pos.x)
    const penZ = DIMS.tableHalfLength + DIMS.ballRadius - Math.abs(pos.z - C)
    if (penX < penZ) {
      pos.x += Math.sign(pos.x) * penX
      vel.x *= -0.45
    } else {
      pos.z = C + Math.sign(pos.z - C) * (DIMS.tableHalfLength + DIMS.ballRadius)
      vel.z *= -0.45
    }
  }
}

function collideNet(ball: BallSim, prevZ: number, events: PhysEvent[]): void {
  const { pos, vel } = ball
  const nz = DIMS.tableCenterZ
  const from = prevZ - nz
  const to = pos.z - nz
  if (from > 0 === to > 0) return
  if (Math.abs(pos.x) > DIMS.netHalfWidth) return
  if (pos.y <= DIMS.tableTopY || pos.y >= DIMS.netTopY + DIMS.ballRadius) return

  if (pos.y < DIMS.netTopY) {
    // Impacto directo contra la malla: la bola rebota hacia atrás
    pos.z = nz + Math.sign(from) * (DIMS.ballRadius + 0.004)
    vel.z *= -0.18
    vel.x *= 0.55
    vel.y *= 0.75
    events.push({ type: 'net', speed: Math.abs(vel.z), pos: pos.clone() })
  } else {
    // Toca el borde superior (cord): frena pero puede pasar
    vel.z *= 0.35
    vel.y *= 0.4
    events.push({ type: 'net', speed: Math.abs(vel.z), pos: pos.clone() })
  }
}

function collideWorld(ball: BallSim, events: PhysEvent[]): void {
  const { pos, vel } = ball
  const r = DIMS.ballRadius

  if (pos.y < r && vel.y < 0) {
    const impact = -vel.y
    pos.y = r
    vel.y = impact * 0.45
    vel.x *= 0.85
    vel.z *= 0.85
    events.push({ type: 'floor', speed: impact, pos: pos.clone() })
  }
  if (pos.y > DIMS.roomHeight - r && vel.y > 0) {
    pos.y = DIMS.roomHeight - r
    vel.y *= -0.4
    events.push({ type: 'wall', speed: Math.abs(vel.y), pos: pos.clone() })
  }
  for (const sx of [-1, 1]) {
    if (pos.x * sx > DIMS.roomHalfX - r && vel.x * sx > 0) {
      pos.x = sx * (DIMS.roomHalfX - r)
      vel.x *= -0.4
      events.push({ type: 'wall', speed: Math.abs(vel.x), pos: pos.clone() })
    }
  }
  if (pos.z > DIMS.roomBackZ - r && vel.z > 0) {
    pos.z = DIMS.roomBackZ - r
    vel.z *= -0.4
    events.push({ type: 'wall', speed: Math.abs(vel.z), pos: pos.clone() })
  }
  if (pos.z < DIMS.roomFrontZ + r && vel.z < 0) {
    pos.z = DIMS.roomFrontZ + r
    vel.z *= -0.4
    events.push({ type: 'wall', speed: Math.abs(vel.z), pos: pos.clone() })
  }

  // Red de seguridad: si la bola escapa del mundo, se considera punto
  if (
    Math.abs(pos.x) > 30 ||
    Math.abs(pos.z) > 30 ||
    pos.y < -5 ||
    !Number.isFinite(pos.x) ||
    !Number.isFinite(pos.y) ||
    !Number.isFinite(pos.z)
  ) {
    pos.set(0, 0.5, DIMS.tableCenterZ)
    vel.set(0, 0, 0)
    events.push({ type: 'floor', speed: 1, pos: pos.clone() })
  }
}

/** Avanza la simulación `dt` segundos con sub-pasos fijos. */
export function stepPhysics(
  dt: number,
  ball: BallSim,
  paddles: PaddleSim[],
  events: PhysEvent[],
): void {
  const n = Math.max(1, Math.min(32, Math.ceil(dt / MAX_SUBSTEP_DT)))
  const h = dt / n

  for (let i = 0; i < n; i++) {
    const k = (i + 0.5) / n
    for (const p of paddles) if (p.cooldown > 0) p.cooldown -= h

    tmpPrev.copy(ball.pos)
    const prevY = ball.pos.y
    const prevZ = ball.pos.z

    // Integración semi-implícita + resistencia del aire
    ball.vel.y += DIMS.gravity * h
    ball.vel.multiplyScalar(Math.max(0, 1 - DIMS.airDrag * h))
    ball.pos.addScaledVector(ball.vel, h)

    for (const pad of paddles) {
      if (!pad.active || pad.cooldown > 0) continue
      collidePaddle(ball, pad, k, events)
    }

    collideTable(ball, prevY, events)
    collideNet(ball, prevZ, events)
    collideWorld(ball, events)
  }
}

/**
 * Simula la trayectoria de la bola y devuelve el punto donde cruza el plano
 * z = planeZ (viniendo desde el lado opuesto), o null si toca red/suelo antes.
 */
export function simulateIntercept(
  ball: BallSim,
  planeZ: number,
  sign: number,
  maxT = 1.8,
): THREE.Vector3 | null {
  const pos = ball.pos.clone()
  const vel = ball.vel.clone()
  const h = 1 / 120
  let t = 0
  while (t < maxT) {
    const prevZ = pos.z
    const prevY = pos.y
    vel.y += DIMS.gravity * h
    vel.multiplyScalar(Math.max(0, 1 - DIMS.airDrag * h))
    pos.addScaledVector(vel, h)
    t += h

    // Rebote en mesa
    const topR = DIMS.tableTopY + DIMS.ballRadius
    if (
      vel.y < 0 &&
      prevY >= topR &&
      pos.y < topR &&
      Math.abs(pos.x) <= DIMS.tableHalfWidth &&
      Math.abs(pos.z - DIMS.tableCenterZ) <= DIMS.tableHalfLength
    ) {
      pos.y = topR
      vel.y = -vel.y * DIMS.tableRestitution
      vel.x *= DIMS.tableFriction
      vel.z *= DIMS.tableFriction
    }
    // Red
    if (prevZ - DIMS.tableCenterZ > 0 !== pos.z - DIMS.tableCenterZ > 0 && pos.y < DIMS.netTopY) {
      if (Math.abs(pos.x) <= DIMS.netHalfWidth && pos.y > DIMS.tableTopY) return null
    }
    // Suelo
    if (pos.y < DIMS.ballRadius) return null
    // Plano objetivo
    if (pos.z * sign >= planeZ * sign && t > 0.04) return pos.clone()
  }
  return null
}

/**
 * Calcula una velocidad parabólica desde `from` hasta `target` (bota en la mesa)
 * garantizando que pasa por encima de la red, con límite de velocidad.
 */
export function computeShotVelocity(
  from: THREE.Vector3,
  target: THREE.Vector3,
  tIn: number,
  maxSpeed: number,
): THREE.Vector3 {
  const T = Math.max(0.3, tIn)
  const ty = DIMS.tableTopY + DIMS.ballRadius
  let vy = (ty - from.y) / T - 0.5 * DIMS.gravity * T
  let vx = (target.x - from.x) / T
  let vz = (target.z - from.z) / T

  // Verificar holgura sobre la red
  const nz = DIMS.tableCenterZ
  if (vz !== 0) {
    const t0 = (nz - from.z) / vz
    if (t0 > 0 && t0 < T) {
      let y0 = from.y + vy * t0 + 0.5 * DIMS.gravity * t0 * t0
      let tries = 0
      while (y0 < DIMS.netTopY + 0.04 && tries < 3) {
        const T2 = T + 0.09 * (tries + 1)
        vy = (ty - from.y) / T2 - 0.5 * DIMS.gravity * T2
        vx = (target.x - from.x) / T2
        vz = (target.z - from.z) / T2
        const t02 = (nz - from.z) / vz
        y0 = t02 > 0 ? from.y + vy * t02 + 0.5 * DIMS.gravity * t02 * t02 : DIMS.netTopY + 1
        tries++
      }
      if (y0 < DIMS.netTopY + 0.03) {
        vy += (DIMS.netTopY + 0.06 - y0) * 2
      }
    }
  }

  const v = new THREE.Vector3(vx, vy, vz)
  const sp = v.length()
  if (sp > maxSpeed) v.multiplyScalar(maxSpeed / sp)
  return v
}
