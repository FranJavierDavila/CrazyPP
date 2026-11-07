/**
 * Dimensiones y constantes físicas del juego (unidades: metros, SI).
 * Tabla estándar ITTF: 2.74 x 1.525 m, superficie a 0.76 m, red 15.25 cm.
 */

export type Side = 'player' | 'ai'
export type Difficulty = 'easy' | 'medium' | 'hard'

export const DIMS = {
  tableTopY: 0.76,
  tableHalfLength: 1.37,
  tableHalfWidth: 0.7625,
  tableThickness: 0.05,
  netTopY: 0.9125,
  netHalfWidth: 0.915,
  ballRadius: 0.02,
  /** Centro de la mesa en el eje Z (el jugador se coloca en z = 0). */
  tableCenterZ: -1.6,
  gravity: -9.81,
  airDrag: 0.12,
  tableRestitution: 0.88,
  tableFriction: 0.96,
  paddleRestitution: 0.78,
  bladeRadius: 0.085,
  paddleHitCooldown: 0.14,
  maxBallSpeed: 12,
  roomHalfX: 3.05,
  roomBackZ: 2.35,
  roomFrontZ: -5.55,
  roomHeight: 2.85,
} as const

export interface AIConfig {
  maxSpeed: number
  errStd: number
  missBase: number
  minT: number
  maxT: number
  maxShotSpeed: number
  predictInterval: number
}

export const AI_PRESETS: Record<Difficulty, AIConfig> = {
  easy: {
    maxSpeed: 1.9,
    errStd: 0.1,
    missBase: 0.22,
    minT: 0.72,
    maxT: 0.95,
    maxShotSpeed: 5.2,
    predictInterval: 0.16,
  },
  medium: {
    maxSpeed: 2.6,
    errStd: 0.06,
    missBase: 0.12,
    minT: 0.58,
    maxT: 0.8,
    maxShotSpeed: 7,
    predictInterval: 0.11,
  },
  hard: {
    maxSpeed: 3.4,
    errStd: 0.032,
    missBase: 0.05,
    minT: 0.45,
    maxT: 0.65,
    maxShotSpeed: 9,
    predictInterval: 0.07,
  },
}

export const COLORS = {
  tableBlue: 0x17539e,
  tableEdge: 0x0e3a73,
  frame: 0x22262b,
  floor: 0x37302b,
  wall: 0x1a1e23,
  rubberRed: 0xc0392b,
  rubberBlack: 0x17181a,
  wood: 0xb98a5a,
  ball: 0xfff8ef,
  accentAmber: 0xe8b45a,
  accentGreen: 0x7fb069,
} as const
