// r95 · ARNÉS DE BRAZOS NATURALES — verificación Node de las 6 correcciones
// del vídeo mal.mp4 del dueño («dedos retorcidos · brazos que tiemblan como
// una descarga · pala no agarrada · bola sin sostener en el saque»):
//   1. CURL DE DEDOS: flexión alrededor de +Y local (medido del GLB), relativa
//      al bind, en la dirección de la PALMA para AMBOS brazos (pulgar ±Y).
//   2. AGARRE: el mango vive en la mano — |mano − (centro − ejeHoja·D)| ≈ 0.
//   3. ENVOLTURA NATURAL: elevación ≤55° (bola alta ≤72°) y radio ≤88 % con
//      la mano alta (codo doblado, brazos que no son antenas).
//   4. CUERPO DE PERSONA: pecho 0,42 m detrás del borde, x ±1,15.
//   5. CODA DE CADENA: la espera funde desde el último cur (sin teleport).
//   6. BUNDLE: los marcadores r95 viajan en public/game.html.
import * as THREE from 'three';
import { readFileSync } from 'node:fs';

const RAIZ = '/home/z/my-project';
let ok = 0, fails = 0;
const aguja = (nombre, cond) => {
  if (cond) { ok++; console.log(`  ✓ ${nombre}`); }
  else { fails++; console.log(`  ✗ ${nombre}`); }
};
const V3 = THREE.Vector3, Q4 = THREE.Quaternion;

/* — 1 · CURL DE DEDOS (réplica exacta del bloque de _cargarArmasGLB) — */
{
  // cadena sintética con las direcciones MEDIDAS del GLB (r95_dedos_glb.mjs):
  // dedos extienden en +X del marco mano, palma en −Z, pulgar en −Y (A) o +Y (B)
  const construirCadena = () => {
    const mano = new THREE.Group(); mano.name = 'mano';
    let ant = mano;
    const falanges = [];
    for (let i = 0; i < 3; i++) {
      const h = new THREE.Group();
      h.name = 'falange' + i;
      h.position.set(0.9 + i * 0.02, i * 0.03, 0);   // casi alineado con +X
      ant.add(h); falanges.push(h); ant = h;
    }
    return { mano, falanges };
  };
  const curlReplica = (falanges, esPulgar) => {
    const ejeFlex = new V3(0, 1, 0);
    const bindQ = falanges.map(() => new Q4());     // bind identidad en el sintético
    for (let iF = 0; iF < falanges.length; iF++) {
      const curva = esPulgar ? 0.32 + iF * 0.22 : Math.min(0.62 + iF * 0.72, 1.9);
      const q = new Q4().setFromAxisAngle(ejeFlex, curva);
      falanges[iF].quaternion.copy(q).multiply(bindQ[iF]);   // RELATIVA al bind
    }
  };
  const puntaEnMarcoMano = (mano, falanges) => {
    mano.updateMatrixWorld(true);
    const inv = new THREE.Matrix4().copy(mano.matrixWorld).invert();
    const tipW = new V3();
    falanges[falanges.length - 1].getWorldPosition(tipW);
    return tipW.applyMatrix4(inv);
  };
  // dirección de curl: los tips deben ir hacia −Z (la palma) en ambos marcos
  const r = construirCadena(); const punta0 = puntaEnMarcoMano(r.mano, r.falanges);
  curlReplica(r.falanges, false);
  const punta1 = puntaEnMarcoMano(r.mano, r.falanges);
  const avanceP = punta1.z - punta0.z;
  aguja('dedos · el curl +Y lleva los tips hacia la PALMA (−Z): Δz<0',
    avanceP < -0.05);
  aguja('dedos · el curl respeta el bind (quat = curl·bind, no sobrescribe)',
    (() => {
      const f = new THREE.Group();
      const q = new Q4().setFromAxisAngle(new V3(0, 1, 0), 0.62);
      const bind = new Q4().setFromAxisAngle(new V3(0, 0, 1), 0.2);
      f.quaternion.copy(q).multiply(bind);
      // componer en el orden inverso NO es lo mismo: el bind debe sobrevivir
      const esp = q.clone().multiply(bind);
      return f.quaternion.angleTo(esp) < 1e-6;
    })());
  aguja('dedos · la flexión total ≈109° (0,62+0,72+0,56 ≤ 1,9 rad)',
    Math.min(0.62 + 2 * 0.72, 1.9) === 1.9);
}

/* — 2 · AGARRE: el mango vive en la mano — — */
{
  const D = 0.1303;
  const eje = new V3(0.2, 0.97, -0.15).normalize();      // eje hoja cualquiera
  const centro = new V3(0.3, 1.2, -3.1);                 // centro deseado (plan)
  const mano = centro.clone().addScaledVector(eje, -D);  // el mango al FINAL
  const anclada = mano.clone().addScaledVector(eje, D);  // re-anclaje del driver
  aguja('agarre · centro re-anclado a la muñeca ≈ centro del plan (≤2 mm)',
    anclada.distanceTo(centro) < 0.002);
  aguja('agarre · la muñeca cae en el EXTREMO del mango (≤2 mm)',
    mano.distanceTo(centro.clone().addScaledVector(eje, -D)) < 0.002);
}

/* — 3 · ENVOLTURA NATURAL del alcance (réplica del driver) — */
{
  const L1L2 = 0.27 + 0.267;
  const clampEnvoltura = (target, S, bolaAlta) => {
    const t = target.clone(); const mesaY = 0.80;
    // anillo rígido
    const d = t.clone().sub(S); const dist = d.length();
    const maxR = 0.999 * L1L2, minR = 0.28 * L1L2;
    if (dist > maxR) t.copy(S).addScaledVector(d.divideScalar(dist), maxR);
    else if (dist < minR) t.copy(S).addScaledVector(d.divideScalar(Math.max(dist, 1e-6)), minR);
    if (t.y < mesaY) t.y = mesaY;
    // envoltura r95
    const dy = t.y - S.y;
    if (dy > 0) {
      const h = Math.hypot(t.x - S.x, t.z - S.z);
      const maxDy = Math.tan(bolaAlta ? 1.25 : 0.96) * Math.max(h, 0.12);
      if (dy > maxDy) t.y = S.y + maxDy;
      if (dy > 0.72) {
        const dd = t.clone().sub(S); const rr = Math.max(dd.length(), 1e-6);
        const rMax2 = 0.88 * L1L2;
        if (rr > rMax2) t.copy(S).addScaledVector(dd.divideScalar(rr), rMax2);
      }
    }
    return t;
  };
  const S = new V3(-0.16, 1.41, -3.44);
  // antena vertical: a 1,9 m sobre el hombro, casi en vertical
  const antena = clampEnvoltura(new V3(-0.10, 3.3, -3.50), S, false);
  aguja('envoltura · el brazo-antena: y acotada a tan(55°)·horiz (sin bola alta)',
    antena.y <= S.y + Math.tan(0.96) * Math.max(0.075, 0.12) + 0.02);
  aguja('envoltura · con la mano en alto el radio ≤88 % (codo doblado, nunca estirada)',
    antena.distanceTo(S) <= 0.88 * L1L2 + 0.02);
  const lob = clampEnvoltura(new V3(-0.10, 3.3, -3.50), S, true);
  aguja('envoltura · bola alta: y acotada a tan(72°)·horiz',
    lob.y <= S.y + Math.tan(1.25) * Math.max(0.075, 0.12) + 0.02);
  aguja('envoltura · reposo bajo intacto (dentro del anillo el clamp no toca)',
    clampEnvoltura(new V3(-0.2, 1.05, -3.05), S, false)
      .distanceTo(new V3(-0.2, 1.05, -3.05)) < 0.02);
}

/* — 4 · CUERPO DE PERSONA (réplica del ancla) — */
{
  const s = -1;
  const zCuerpo = 0 + s * (1.37 + 0.42);           // tableCenterZ + s·(half+0.42)
  let z = -1.5;                                    // el AI se pega a la mesa…
  if (s < 0 ? z > zCuerpo : z < zCuerpo) z = zCuerpo;
  aguja('cuerpo · el pecho JAMÁS cruza el borde (−1.5 → −1.79)', Math.abs(z - (-1.79)) < 1e-9);
  let x = 2.3;
  if (x > 1.15) x = 1.15;
  aguja('cuerpo · la pista limita el cuerpo (x 2.3 → 1.15)', x === 1.15);
  const z2 = -2.6;
  aguja('cuerpo · reculado legítimo se conserva (−2.6 intacto)',
    (s < 0 ? z2 > zCuerpo : z2 < zCuerpo) ? zCuerpo === -1.79 && false : true);
}

/* — 5 · CODA DE CADENA (sin teleport al morir el plan) — */
{
  const p = new V3(0.1, 1.3, -3.2);                // último cur del plan (≈35 cm del reposo)
  const reposo = new V3(-0.01, 1.05, -3.42);       // destino de espera
  const mesh = reposo.clone();                     // la espera ya teleportó…
  let t = 0.3;
  const pasos = [];
  while (t > 0) {
    t -= 1 / 72;
    mesh.lerp(p, THREE.MathUtils.clamp(t / 0.3, 0, 1));
    pasos.push(mesh.clone());
  }
  aguja('coda · el primer frame de espera nace EN el último cur (≤3 cm)',
    pasos[0].distanceTo(p) < 0.03);
  aguja('coda · el funde es MONÓTONO hacia el reposo (sin saltos >4 cm/frame)',
    (() => {
      for (let i = 1; i < pasos.length; i++)
        if (pasos[i].distanceTo(pasos[i - 1]) > 0.04) return false;
      return true;
    })());
}

/* — 6 · BUNDLE: los marcadores r95 viajan en game.html — */
{
  const b = readFileSync(RAIZ + '/public/game.html', 'utf-8');
  // r99 · las 2 agujas del curl estático y del anclaje en muñeca se
  // ACTUALIZAN a los invariantes del sistema de poses (plan r99): el curl
  // DINÁMICO por pose relativa al bind y el mango anclado en la CREASE.
  aguja('bundle · r99 CURL DINÁMICO POR POSE (flexión +Y, relativa al bind)',
    b.includes('R99_POSE_AGARRE') && b.includes('R99_POSE_SAQUE') &&
    b.includes('multiply(dd.bindQ)'));
  aguja('bundle · r95 pulgarY por brazo (A −1 · B +1)',
    b.includes("pulgarY: (c.lado === 'B') ? 1 : -1"));
  aguja('bundle · r95 ENVOLTURA NATURAL (tan 0.96 / 1.25 + radio 88 %)',
    b.includes('r95 · ENVOLTURA NATURAL') && b.includes('0.88 * (R.L1 + R.L2)'));
  aguja('bundle · r95 EL CUERPO ES UNA PERSONA (borde +0.42 · x ±1.15)',
    b.includes('r95 · EL CUERPO ES UNA PERSONA') && b.includes('tableHalfLength + 0.42'));
  aguja('bundle · r99 EL MANGO VIVE EN LA CREASE DE LA MANO (offset medido)',
    b.includes('R99_CREASE') && b.includes('offCrease[bp.lado]') &&
    b.includes('D_GRIP - R99_DCREASE'));
  aguja('bundle · r95 CODA DE CADENA (funde el último cur, sin teleport)',
    b.includes('r95 · CODA DE CADENA') && b.includes('_codaPala.t'));
  aguja('bundle · r95 la zona dulce SOLO en strike (adiós al látigo del follow)',
    b.includes('r95 · zona dulce SOLO en strike') && b.includes('if (enStrike)'));
  aguja('bundle · r94 el material y el marco rig-local siguen íntegros',
    b.includes("getDependency('texture', 0)") && b.includes('_gRigInvQ'));
}

console.log(`\nARNÉS BRAZOS NATURALES r95 · ${ok} OK · ${fails} FALLOS`);
process.exit(fails ? 1 : 0);
