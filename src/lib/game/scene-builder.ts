/**
 * Construcción de todos los objetos visuales de la escena:
 * sala, mesa reglamentaria, red, palas, bola, marcador y estela de la bola.
 */
import * as THREE from 'three'
import { COLORS, DIMS } from './constants'

export const MOUNT_QUAT = new THREE.Quaternion().setFromEuler(
  new THREE.Euler(0, Math.PI, 0),
)

/** Grupo vacío de la sala: suelo, paredes, franjas LED y rejilla sutil. */
export function createRoom(): THREE.Group {
  const g = new THREE.Group()
  const zC = (DIMS.roomBackZ + DIMS.roomFrontZ) / 2
  const depth = DIMS.roomBackZ - DIMS.roomFrontZ

  const floorMat = new THREE.MeshStandardMaterial({
    color: COLORS.floor,
    roughness: 0.9,
    metalness: 0.05,
  })
  const floor = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth),
    floorMat,
  )
  floor.rotation.x = -Math.PI / 2
  floor.position.set(0, 0, zC)
  floor.receiveShadow = true
  g.add(floor)

  const grid = new THREE.GridHelper(
    Math.max(DIMS.roomHalfX * 2, depth),
    20,
    0x4a4038,
    0x2c2622,
  )
  grid.position.set(0, 0.002, zC)
  g.add(grid)

  const wallMat = new THREE.MeshStandardMaterial({
    color: COLORS.wall,
    roughness: 1,
  })
  const mkWall = (w: number, h: number, pos: THREE.Vector3, rotY: number) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat)
    m.position.copy(pos)
    m.rotation.y = rotY
    g.add(m)
  }
  const cx = DIMS.roomHalfX
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(-cx, DIMS.roomHeight / 2, zC), Math.PI / 2)
  mkWall(depth, DIMS.roomHeight, new THREE.Vector3(cx, DIMS.roomHeight / 2, zC), -Math.PI / 2)
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomBackZ), Math.PI)
  mkWall(DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomFrontZ), 0)

  // Techo
  const ceil = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth),
    new THREE.MeshStandardMaterial({ color: 0x14171b, roughness: 1 }),
  )
  ceil.rotation.x = Math.PI / 2
  ceil.position.set(0, DIMS.roomHeight, zC)
  g.add(ceil)

  // Paneles de luz emisivos en el techo
  const panelMat = new THREE.MeshBasicMaterial({ color: 0xf5efe2 })
  for (const px of [-1.4, 1.4]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.4), panelMat)
    panel.rotation.x = Math.PI / 2
    panel.position.set(px, DIMS.roomHeight - 0.01, -1.2)
    g.add(panel)
  }

  // Franja LED ámbar a media altura para dar profundidad
  const stripMat = new THREE.MeshBasicMaterial({ color: COLORS.accentAmber })
  for (const sx of [-cx + 0.02, cx - 0.02]) {
    const strip = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, depth * 0.9), stripMat)
    strip.position.set(sx, 2.1, zC)
    g.add(strip)
  }

  // Marca circular en el suelo: punto de referencia del jugador
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.26, 0.33, 48),
    new THREE.MeshBasicMaterial({
      color: COLORS.accentAmber,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide,
    }),
  )
  ring.rotation.x = -Math.PI / 2
  ring.position.set(0, 0.004, 0)
  g.add(ring)

  return g
}

/** Mesa reglamentaria con líneas blancas, patas y red. */
export function createTable(): THREE.Group {
  const g = new THREE.Group()
  const topY = DIMS.tableTopY
  const L = DIMS.tableHalfLength * 2
  const W = DIMS.tableHalfWidth * 2

  const topMat = new THREE.MeshStandardMaterial({
    color: COLORS.tableBlue,
    roughness: 0.55,
    metalness: 0.05,
  })
  const top = new THREE.Mesh(new THREE.BoxGeometry(W, DIMS.tableThickness, L), topMat)
  top.position.set(0, topY - DIMS.tableThickness / 2, DIMS.tableCenterZ)
  top.castShadow = true
  top.receiveShadow = true
  g.add(top)

  // Líneas blancas perimetrales (2 cm) + línea central (3 mm)
  const lineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 })
  const lineH = 0.002
  const mkLine = (w: number, d: number, x: number, z: number) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, lineH, d), lineMat)
    m.position.set(x, topY + lineH / 2 - 0.0005, DIMS.tableCenterZ + z)
    g.add(m)
  }
  mkLine(W, 0.02, 0, -DIMS.tableHalfLength + 0.01)
  mkLine(W, 0.02, 0, DIMS.tableHalfLength - 0.01)
  mkLine(0.02, L, -DIMS.tableHalfWidth + 0.01, 0)
  mkLine(0.02, L, DIMS.tableHalfWidth - 0.01, 0)
  mkLine(0.003, L, 0, 0)

  // Estructura y patas
  const frameMat = new THREE.MeshStandardMaterial({ color: COLORS.frame, roughness: 0.7 })
  const apron = new THREE.Mesh(new THREE.BoxGeometry(W * 0.96, 0.1, 0.03), frameMat)
  apron.position.set(0, topY - DIMS.tableThickness - 0.06, DIMS.tableCenterZ - DIMS.tableHalfLength + 0.05)
  g.add(apron)
  const apron2 = apron.clone()
  apron2.position.z = DIMS.tableCenterZ + DIMS.tableHalfLength - 0.05
  g.add(apron2)

  for (const lx of [-W / 2 + 0.12, W / 2 - 0.12]) {
    for (const lz of [-L / 2 + 0.15, L / 2 - 0.15]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, topY - DIMS.tableThickness, 0.06), frameMat)
      leg.position.set(lx, (topY - DIMS.tableThickness) / 2, DIMS.tableCenterZ + lz)
      leg.castShadow = true
      g.add(leg)
    }
  }

  // Red
  const netCanvas = document.createElement('canvas')
  netCanvas.width = 256
  netCanvas.height = 64
  const nctx = netCanvas.getContext('2d')
  if (nctx) {
    nctx.clearRect(0, 0, 256, 64)
    nctx.strokeStyle = 'rgba(20,22,25,0.9)'
    nctx.lineWidth = 2
    for (let x = 0; x <= 256; x += 10) {
      nctx.beginPath()
      nctx.moveTo(x, 0)
      nctx.lineTo(x, 64)
      nctx.stroke()
    }
    for (let y = 0; y <= 64; y += 10) {
      nctx.beginPath()
      nctx.moveTo(0, y)
      nctx.lineTo(256, y)
      nctx.stroke()
    }
  }
  const netTex = new THREE.CanvasTexture(netCanvas)
  netTex.wrapS = THREE.RepeatWrapping
  netTex.wrapT = THREE.RepeatWrapping
  netTex.repeat.set(6, 1.2)

  const netMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.netHalfWidth * 2, DIMS.netTopY - topY),
    new THREE.MeshBasicMaterial({
      map: netTex,
      transparent: true,
      side: THREE.DoubleSide,
      alphaTest: 0.05,
    }),
  )
  netMesh.position.set(0, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ)
  g.add(netMesh)

  // Banda blanca superior de la red
  const band = new THREE.Mesh(
    new THREE.BoxGeometry(DIMS.netHalfWidth * 2, 0.014, 0.006),
    new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.5 }),
  )
  band.position.set(0, DIMS.netTopY, DIMS.tableCenterZ)
  g.add(band)

  // Postes
  const postMat = new THREE.MeshStandardMaterial({ color: 0x30343a, roughness: 0.4, metalness: 0.6 })
  for (const px of [-DIMS.netHalfWidth, DIMS.netHalfWidth]) {
    const post = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, DIMS.netTopY - topY + 0.02, 12), postMat)
    post.position.set(px, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ)
    g.add(post)
  }

  return g
}

/** Pala: cara roja hacia el frente (+Z local), goma negra detrás, mango de madera. */
export function createPaddle(): THREE.Group {
  const g = new THREE.Group()
  const R = DIMS.bladeRadius

  const sideMat = new THREE.MeshStandardMaterial({ color: COLORS.wood, roughness: 0.7 })
  const frontMat = new THREE.MeshStandardMaterial({ color: COLORS.rubberRed, roughness: 0.95 })
  const backMat = new THREE.MeshStandardMaterial({ color: COLORS.rubberBlack, roughness: 0.95 })

  const blade = new THREE.Mesh(
    new THREE.CylinderGeometry(R, R, 0.012, 36),
    [sideMat, frontMat, backMat],
  )
  blade.rotation.x = Math.PI / 2
  blade.castShadow = true
  g.add(blade)

  const handle = new THREE.Mesh(
    new THREE.BoxGeometry(0.028, 0.024, 0.11),
    new THREE.MeshStandardMaterial({ color: 0x8a6540, roughness: 0.8 }),
  )
  handle.position.set(0, -0.006, -0.068)
  handle.rotation.x = -0.16
  handle.castShadow = true
  g.add(handle)

  return g
}

/** Bola con estela de puntos. */
export function createBall(): { mesh: THREE.Mesh; trail: THREE.Points; trailUpdate: () => void } {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(DIMS.ballRadius, 24, 16),
    new THREE.MeshStandardMaterial({
      color: COLORS.ball,
      roughness: 0.35,
      emissive: 0x555044,
      emissiveIntensity: 0.35,
    }),
  )
  mesh.castShadow = true

  const TRAIL_N = 22
  const positions = new Float32Array(TRAIL_N * 3)
  const geo = new THREE.BufferGeometry()
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  const trail = new THREE.Points(
    geo,
    new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.016,
      transparent: true,
      opacity: 0.35,
      depthWrite: false,
    }),
  )
  let idx = 0
  const trailUpdate = () => {
    positions[idx * 3] = mesh.position.x
    positions[idx * 3 + 1] = mesh.position.y
    positions[idx * 3 + 2] = mesh.position.z
    idx = (idx + 1) % TRAIL_N
    geo.attributes.position.needsUpdate = true
  }

  return { mesh, trail, trailUpdate }
}

export interface ScoreboardData {
  player: number
  ai: number
  server: 'player' | 'ai'
  message: string
}

/** Marcador flotante con textura de canvas (visible dentro del visor). */
export function createScoreboard(): {
  group: THREE.Group
  update: (d: ScoreboardData) => void
} {
  const group = new THREE.Group()
  const canvas = document.createElement('canvas')
  canvas.width = 1024
  canvas.height = 512
  const ctx = canvas.getContext('2d')!
  const tex = new THREE.CanvasTexture(canvas)
  tex.colorSpace = THREE.SRGBColorSpace

  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(1.7, 0.85),
    new THREE.MeshBasicMaterial({ map: tex }),
  )
  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(1.76, 0.91, 0.04),
    new THREE.MeshStandardMaterial({ color: 0x101316, roughness: 0.6 }),
  )
  frame.position.z = -0.025
  group.add(frame)
  group.add(panel)
  group.position.set(0, 1.95, DIMS.roomFrontZ + 0.9)

  let last = ''
  const update = (d: ScoreboardData) => {
    const key = `${d.player}|${d.ai}|${d.server}|${d.message}`
    if (key === last) return
    last = key

    ctx.fillStyle = '#101418'
    ctx.fillRect(0, 0, 1024, 512)
    ctx.strokeStyle = '#2a3138'
    ctx.lineWidth = 10
    ctx.strokeRect(10, 10, 1004, 492)

    ctx.fillStyle = '#8b949c'
    ctx.font = '600 34px "Noto Sans SC", sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText('P I N G   P O N G   X R', 512, 70)

    ctx.textAlign = 'left'
    ctx.fillStyle = '#e8b45a'
    ctx.font = '700 52px "Noto Sans SC", sans-serif'
    ctx.fillText('TÚ', 150, 170)
    if (d.server === 'player') {
      ctx.beginPath()
      ctx.arc(118, 152, 13, 0, Math.PI * 2)
      ctx.fill()
    }
    ctx.textAlign = 'right'
    ctx.fillStyle = '#7fb069'
    ctx.font = '700 52px "Noto Sans SC", sans-serif'
    ctx.fillText('CPU', 874, 170)
    if (d.server === 'ai') {
      ctx.fillStyle = '#7fb069'
      ctx.beginPath()
      ctx.arc(906, 152, 13, 0, Math.PI * 2)
      ctx.fill()
    }

    ctx.textAlign = 'center'
    ctx.fillStyle = '#f2f4f6'
    ctx.font = '800 190px "Noto Sans SC", sans-serif'
    ctx.fillText(`${d.player} : ${d.ai}`, 512, 340)

    ctx.fillStyle = '#c8ced4'
    ctx.font = '500 40px "Noto Sans SC", sans-serif'
    const msg = d.message.length > 46 ? d.message.slice(0, 46) : d.message
    ctx.fillText(msg, 512, 440)

    tex.needsUpdate = true
  }

  update({ player: 0, ai: 0, server: 'player', message: '' })
  return { group, update }
}
