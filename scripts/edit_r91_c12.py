#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""edit_r91_c12.py — r91 · parte del núcleo en c12: rama de pose por fases de
la cadena, brazo visible (hombro→codo→muñeca con IK) y cableado del frame."""
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
C12 = 'src/game/core/c12_pingponggame.js'

def editar(viejo, nuevo, etiqueta):
    p = RAIZ / C12
    t = p.read_text(encoding='utf-8')
    n = t.count(viejo)
    if n != 1:
        sys.exit(f'ABORTA [{etiqueta}]: {n} apariciones del ancla')
    p.write_text(t.replace(viejo, nuevo), encoding='utf-8')
    print(f'  ✓ {etiqueta}')

# 1 · import de solveArmIK desde c06
editar(
  "import { ACHIEVEMENTS, GameStats, OpponentAI, Rules } from './c06_logros_stats_ia_rival.js';",
  "import { ACHIEVEMENTS, GameStats, OpponentAI, Rules, solveArmIK } from './c06_logros_stats_ia_rival.js';",
  'import solveArmIK')

# 2 · arañas del brazo (cero allocs por frame)
editar(
  "import { ACHIEVEMENTS, GameStats, OpponentAI, Rules, solveArmIK } from './c06_logros_stats_ia_rival.js';",
  "import { ACHIEVEMENTS, GameStats, OpponentAI, Rules, solveArmIK } from './c06_logros_stats_ia_rival.js';\n"
  "// r91 · arañas del brazo visible del rival (cero allocs por frame)\n"
  "const _armS = new THREE.Vector3(); const _armW = new THREE.Vector3();\n"
  "const _armE = new THREE.Vector3(); const _armP = new THREE.Vector3();\n"
  "const _armD = new THREE.Vector3(); const _armA = new THREE.Vector3();\n"
  "const _armY = new THREE.Vector3(0, 1, 0); const _armX = new THREE.Vector3(1, 0, 0);",
  'arañas _arm*')

# 3 · creación del brazo junto a la pala del rival
editar(
  "    // Pala de la IA y del jugador demo: modelo GLB con la hoja en el origen.\n"
  "    // Sin cuerpos: solo la pala flotante del rival (más limpio y no estorba).\n"
  "    this.aiPaddleMesh = makePaddleVisual(paddleModel, 'center');\n"
  "    this.rig.add(this.aiPaddleMesh);",
  "    // Pala de la IA y del jugador demo: modelo GLB con la hoja en el origen.\n"
  "    // r91 · CADENA CINEMÁTICA: el rival ya NO es solo una pala flotante —\n"
  "    // un brazo sobrio (hombro→brazo→antebrazo→muñeca, cápsulas carbón) la\n"
  "    // sujeta; la IK lo articula cada frame desde la posición REAL de la\n"
  "    // pala (cadena, saque o espera). El demo sigue sin cuerpo.\n"
  "    this.aiPaddleMesh = makePaddleVisual(paddleModel, 'center');\n"
  "    this.rig.add(this.aiPaddleMesh);\n"
  "    {\n"
  "      const _am = new THREE.MeshStandardMaterial({ color: 0x2b2e34, roughness: 0.55, metalness: 0.18 });\n"
  "      const _arm = new THREE.Group();\n"
  "      const hombro = new THREE.Mesh(new THREE.SphereGeometry(0.048, 14, 10), _am);\n"
  "      const brazo = new THREE.Mesh(new THREE.CapsuleGeometry(0.030, 1, 5, 10), _am);\n"
  "      const antebrazo = new THREE.Mesh(new THREE.CapsuleGeometry(0.025, 1, 5, 10), _am);\n"
  "      const muneca = new THREE.Mesh(new THREE.SphereGeometry(0.032, 12, 9), _am);\n"
  "      _arm.add(hombro, brazo, antebrazo, muneca);\n"
  "      _arm.visible = false;\n"
  "      _arm.userData = { hombro, brazo, antebrazo, muneca };\n"
  "      this.aiArm = _arm;\n"
  "      this.rig.add(_arm);\n"
  "    }",
  'brazo visible creado')

# 4 · método updateAIArm antes de updateAIPaddlePose
editar(
  "  updateAIPaddlePose(mesh, ai, who, dt) {",
  """  /** r91 · BRAZO VISIBLE del rival: articulaciones hombro→codo→muñeca
   *  resueltas por IK analítica desde el hombro anclado al cuerpo del rival,
   *  SIEMPRE a partir de la posición real de la pala (cadena, saque o espera)
   *  — el antebrazo nunca se despega del mango. Cápsulas orientadas entre
   *  articulaciones; polo del codo anatómico (cae en drive, sube en revés). */
  updateAIArm(ai) {
    if (!this.aiArm || !ai || !this.aiPaddleMesh) return;
    const u = this.aiArm.userData;
    const s = ai.sign || -1;
    const fh = (ai.chain && ai.chain.fh) || ai.fhSide || 1;
    // hombro: detrás-bajo de la pala, al lado del brazo (sigue al cuerpo)
    _armS.copy(ai.pos);
    _armS.x += fh * s * 0.09;
    _armS.y += 0.16;
    _armS.z += s * 0.17;
    // muñeca: extremo del mango (10,5 cm desde el centro de la hoja por la
    // dirección REAL del mango en el mundo)
    _armW.copy(this.aiPaddleMesh.position);
    _armA.set(0, -1, 0).applyQuaternion(this.aiPaddleMesh.quaternion);
    _armW.addScaledVector(_armA, 0.105);
    // polo del codo: por debajo-detrás en drive, alzado en revés (±jitter vivo)
    _armP.set(0, -1, 0).addScaledVector(_armX, fh * s * 0.8);
    const ik = solveArmIK(_armS, _armW, 0.26, 0.24, _armP, _armE);
    u.hombro.position.copy(_armS);
    _armD.copy(_armE).sub(_armS);
    const l1 = Math.max(0.05, _armD.length());
    u.brazo.position.copy(_armS).addScaledVector(_armD, 0.5);
    u.brazo.quaternion.setFromUnitVectors(_armY, _armD.normalize());
    u.brazo.scale.set(1, l1, 1);
    _armD.copy(_armW).sub(_armE);
    const l2 = Math.max(0.05, _armD.length());
    u.antebrazo.position.copy(_armE).addScaledVector(_armD, 0.5);
    u.antebrazo.quaternion.setFromUnitVectors(_armY, _armD.normalize());
    u.antebrazo.scale.set(1, l2, 1);
    u.muneca.position.copy(_armW);
  }

  updateAIPaddlePose(mesh, ai, who, dt) {""",
  'updateAIArm método')

# 5 · rama de la cadena en updateAIPaddlePose (entre el saque y el rally)
editar(
  "      bladePose(AIM_BLADE, AIM_FACE, fhServe * 0.18, 0);\n"
  "      mesh.quaternion.copy(poseQ);\n"
  "      this.clampPaddlePose(mesh.position, mesh.quaternion, false);\n"
  "      return;\n"
  "    }\n\n"
  "    // rally / espera (v2.17: movimiento natural — v2.23: golpes con lado y giro)\n",
  "      bladePose(AIM_BLADE, AIM_FACE, fhServe * 0.18, 0);\n"
  "      mesh.quaternion.copy(poseQ);\n"
  "      this.clampPaddlePose(mesh.position, mesh.quaternion, false);\n"
  "      return;\n"
  "    }\n\n"
  "    // r91 · CADENA CINEMÁTICA (solo el rival real): la pala es el extremo\n"
  "    // del plan de golpe — fases reacción→carga→golpeo→acompañamiento→\n"
  "    // recuperación con trayectorias de mínimo jerk (c06). La pose sigue\n"
  "    // la spec del dueño (r90: cara ⟂ mesa, mango ∥ mesa, cierre sobre el\n"
  "    // eje del mango) y ai.chain.vel lleva la velocidad REAL de la pala.\n"
  "    if (who === 'ai' && ai.chain && ai.chain.phase) {\n"
  "      const ch = ai.chain;\n"
  "      mesh.position.copy(ch.cur);\n"
  "      const pF = ch.u || 0;\n"
  "      const Kc = SWING_POSE[ch.kind] || SWING_POSE.drive;\n"
  "      const fhC = ch.fh || 1;\n"
  "      if (ch.phase === 'react' || ch.phase === 'back') {\n"
  "        // CARGA: eje horizontal cruzado al lado del golpe, cara que se\n"
  "        // ABRE al armar (el jugador suaviza la cara para acelerar después)\n"
  "        AIM_BLADE.set(0, 0.22, 0).addScaledVector(AIM_RIGHT, fhC * 0.9);\n"
  "        AIM_BLADE.normalize();\n"
  "        AIM_FACE.copy(AIM_FWD);\n"
  "        closAx.copy(AIM_BLADE); closX.crossVectors(closAx, AIM_FACE);\n"
  "        if (closX.y < 0) closAx.negate();\n"
  "        closQ.setFromAxisAngle(closAx, 0.16 - 0.12 * pF);\n"
  "        AIM_FACE.applyQuaternion(closQ);\n"
  "        bladePose(AIM_BLADE, AIM_FACE, fhC * 0.2, 0);\n"
  "      } else if (ch.phase === 'strike' || ch.phase === 'follow') {\n"
  "        // GOLPEO/ACOMPAÑAMIENTO: las fórmulas del golpeo r90 con la firma\n"
  "        // de cada golpe y el cierre por efecto sobre el eje del mango\n"
  "        AIM_BLADE.set(0, 0.25, 0)\n"
  "          .addScaledVector(AIM_RIGHT, fhC * (Kc.side0 * (1 - pF) - Kc.side1 * pF) * 0.95);\n"
  "        AIM_BLADE.normalize();\n"
  "        AIM_FACE.copy(ch.vdir || AIM_FWD);\n"
  "        if (AIM_FACE.lengthSq() < 1e-8) AIM_FACE.copy(AIM_FWD);\n"
  "        AIM_FACE.y *= 0.35;\n"
  "        AIM_FACE.normalize();\n"
  "        closAx.copy(AIM_BLADE); closX.crossVectors(closAx, AIM_FACE);\n"
  "        if (closX.y < 0) closAx.negate();\n"
  "        closQ.setFromAxisAngle(closAx, -(Kc.clos0 + Kc.clos1 * pF));\n"
  "        AIM_FACE.applyQuaternion(closQ);\n"
  "        bladePose(AIM_BLADE, AIM_FACE,\n"
  "          (ch.roll || 0) * (0.35 + 0.85 * pF) + fhC * (0.24 - 0.46 * pF), 0);\n"
  "      } else {\n"
  "        // RECUPERACIÓN: pose de espera (r90) mientras la pala vuelve al cuerpo\n"
  "        const sideR = THREE.MathUtils.clamp((this.ball.pos.x - mesh.position.x) * s * 2.6, -1, 1);\n"
  "        AIM_BLADE.set(0, 0.22, 0).addScaledVector(AIM_RIGHT, 0.8 + sideR * 0.25);\n"
  "        AIM_BLADE.normalize();\n"
  "        AIM_FACE.copy(AIM_FWD);\n"
  "        AIM_FACE.x += (this.ball.pos.x - mesh.position.x) * 0.5;\n"
  "        AIM_FACE.normalize();\n"
  "        closAx.copy(AIM_BLADE); closX.crossVectors(closAx, AIM_FACE);\n"
  "        if (closX.y < 0) closAx.negate();\n"
  "        closQ.setFromAxisAngle(closAx, this.ball.pos.y > 1.25 ? -0.10 : 0.12);\n"
  "        AIM_FACE.applyQuaternion(closQ);\n"
  "        bladePose(AIM_BLADE, AIM_FACE, 0, 0);\n"
  "      }\n"
  "      mesh.quaternion.slerp(poseQ, Math.min(1, dt * 18));\n"
  "      this.clampPaddlePose(mesh.position, mesh.quaternion, false);\n"
  "      return;\n"
  "    }\n\n"
  "    // rally / espera (v2.17: movimiento natural — v2.23: golpes con lado y giro)\n",
  'rama de la cadena en updateAIPaddlePose')

# 6 · cableado del frame: el brazo se pinta con la pala del rival
editar(
  "    } else {\n"
  "      // v2.40: congelado — la pala IA conserva su última pose\n"
  "      if (!frozen) this.updateAIPaddlePose(this.aiPaddleMesh, this.ai, 'ai', dt);\n"
  "    }",
  "    } else {\n"
  "      // v2.40: congelado — la pala IA conserva su última pose\n"
  "      if (!frozen) this.updateAIPaddlePose(this.aiPaddleMesh, this.ai, 'ai', dt);\n"
  "      // r91 · el brazo visible va con la pala del rival local (online: la\n"
  "      // pala remota llega por red y no hay cuerpo que pintar)\n"
  "      if (this.aiArm) {\n"
  "        const armVis = this.aiPaddleMesh.visible && !this.net.online && !this.calib;\n"
  "        if (this.aiArm.visible !== armVis) this.aiArm.visible = armVis;\n"
  "        if (armVis) this.updateAIArm(this.ai);\n"
  "      }\n"
  "    }",
  'cableado del brazo en el frame')

print('c12 OK')
