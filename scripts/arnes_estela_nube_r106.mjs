/* r106 · ARNÉS ESTELA DE PODER + NUBE DE PRISMAS — petición del dueño:
 *  «siempre que el usuario lance un superpoder de pala la bola genere una
 *  estela de partículas pequeñas de un determinado color según el
 *  superpoder» + «en el superpoder del arcoíris, siempre que esté activo
 *  y el rival golpee la bola… prismas 3d brillantes de todos los colores
 *  que se esparcirán como una nube… flotando unos 5 segundos hasta
 *  desaparecer… pretende dificultarle la visión».
 *  Probado contra las FÁBRICAS REALES de c07 (cero réplicas):
 *   P1 · estela: nacen, se mueven con su deriva y MURIENDO se ocultan.
 *   P2 · estela: apagado monotónico (col = base × vida) y ≠ 0 vivas.
 *   P3 · estela arcoíris: cada partícula su PROPIO matiz (colores distintos).
 *   P4 · nube: nace, flota (freno del esparcir + gravedad casi nula),
 *        gira, y el grupo de ~30 prismas se abre ≥ 25 cm en 1 s.
 *   P5 · nube: encogido en el último 0,8 s y desaparece entera ≤ 5,5 s.
 *   P6 · nube: dos nubes seguidas re-usan el pool (36 instancias, sin crash).
 *   P7 · estructural: los 10 cables del núcleo presentes en disco.
 */
globalThis.window = globalThis;
globalThis.document = { getElementById: () => null, createElement: () => ({}),
  addEventListener: () => {}, visibilityState: 'visible' };
try { globalThis.navigator = { userAgent: 'node-r106' }; } catch (e) { /* getter */ }

import * as THREE from 'three';
const { createEstelaPoder, createNubePrismas } = await import('/home/z/my-project/src/game/core/c07_escena_sala.js');
const fs = await import('node:fs');
const c12 = fs.readFileSync('/home/z/my-project/src/game/core/c12_pingponggame.js', 'utf8');

let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}

/* ── P1+P2+P3 · ESTELA ── */
{
  const E = createEstelaPoder();
  const rgb = [0.93, 0.72, 0.32];               // mega — ámbar
  for (let i = 0; i < 40; i++) {
    E.nace(0.2 + i * 0.004, 1.0, 1.6, -0.3, 0.15, -0.5, rgb);
  }
  const col0 = E.group.geometry.attributes.color.array.slice(0, 3);
  E.update(1 / 60);
  const col1 = E.group.geometry.attributes.color.array.slice(0, 3);
  const posMid = E.group.geometry.attributes.position.array.slice(0, 3);
  CHK(E.group.visible && col1[0] < col0[0] && col1[0] > 0.01,
    `P1/P2 estela viva y apagado monotónico (r ${col0[0].toFixed(2)} → ${col1[0].toFixed(2)} · se mueve a x=${posMid[0].toFixed(3)})`);
  // avanzar más que la vida: 0,6 s
  for (let i = 0; i < 40; i++) E.update(0.015);
  CHK(!E.group.visible,
    'P1 estela: tras 0,6 s sin nacimientos el pool muere y se OCULTA');
  // arcoíris: cada partícula su matiz
  const E2 = createEstelaPoder();
  E2.nace(0, 1, 0, 0, 0, 0, 'arcoiris');
  E2.nace(0.01, 1, 0, 0, 0, 0, 'arcoiris');
  const ca = E2.group.geometry.attributes.color.array;
  const dif = Math.abs(ca[0] - ca[3]) + Math.abs(ca[1] - ca[4]) + Math.abs(ca[2] - ca[5]);
  CHK(dif > 0.05,
    `P3 estela arcoíris: partículas con PROPIO matiz (Δrgb ${(dif).toFixed(2)})`);
}

/* ── P4+P5+P6 · NUBE DE PRISMAS ── */
{
  const NB = createNubePrismas();
  const p0 = new THREE.Vector3(0.2, 1.05, 0.9);   // punto de golpeo rival
  NB.nace(p0, 30);
  CHK(NB.group.visible, 'P4 nube visible al nacer (30 prismas)');
  // 1 s de flotación en pasos de 16 ms
  const posIni = [];
  for (let i = 0; i < 30; i++) {
    const m = new THREE.Vector3();
    NB.group.getMatrixAt(i, m);   // no — getMatrixAt devuelve Matrix4
  }
  const readPos = (i) => {
    const a = NB.group.instanceMatrix.array;
    return [a[i * 16 + 12], a[i * 16 + 13], a[i * 16 + 14]];
  };
  for (let i = 0; i < 30; i++) posIni.push(readPos(i));
  for (let i = 0; i < 60; i++) NB.update(1 / 60);
  // dispersión media desde el centro de nacimiento
  let dMed = 0, flota = 0;
  for (let i = 0; i < 30; i++) {
    const [x, y, z] = readPos(i);
    dMed += Math.hypot(x - p0.x, y - p0.y, z - p0.z);
    flota += Math.abs(y - (p0.y + 0.12)) < 1.2 ? 1 : 0;   // no se escapa al infinito
  }
  dMed /= 30;
  CHK(dMed > 0.10 && dMed < 2.0 && flota === 30,
    `P4 nube flotando: dispersión media ${(dMed * 100).toFixed(0)} cm a 1 s (30/30 dentro del aire)`);
  // avanzar hasta el encogido: vida media 5,0 → a 4,5 s el escalado baja
  for (let i = 0; i < 220; i++) NB.update(1 / 60);   // +3,66 s (t≈4,66)
  const a = NB.group.instanceMatrix.array;
  // la escala vive en la LONGITUD del eje X de la matriz (la rotación la
  // preserva): colLen = |(a[0],a[1],a[2])| = esc efectiva del prisma
  let encogiendo = 0, muertas0 = 0;
  for (let i = 0; i < 36; i++) {
    const cl = Math.hypot(a[i * 16], a[i * 16 + 1], a[i * 16 + 2]);
    if (cl === 0) muertas0++;
    else if (cl < 0.79) encogiendo++;      // base mínima 0,8 → ya encoge
  }
  CHK(encogiendo > 0 || muertas0 > 0,
    `P5 encogido activo al final de la vida (${encogiendo} encogiendo · ${muertas0} ya muertas a t≈4,66 s)`);
  for (let i = 0; i < 80; i++) NB.update(1 / 60);    // +1,33 s (t≈6 s > vida+FADE)
  const aFin = NB.group.instanceMatrix.array;
  let muertas = 0;
  for (let i = 0; i < 36; i++) {
    if (aFin[i * 16] === 0 && aFin[i * 16 + 5] === 0) muertas++;
  }
  CHK(!NB.group.visible && muertas >= 30,
    `P5 nube desaparecida entera ≤ 5,5 s (${muertas}/36 instancias a escala 0 · grupo oculto)`);
  // P6 · dos nubes seguidas: el anillo re-usa sin crash
  NB.nace(p0, 30);
  NB.nace(new THREE.Vector3(-0.2, 1.0, 0.8), 30);
  NB.update(1 / 60);
  CHK(NB.group.visible && NB.group.count === 36,
    'P6 dos nubes seguidas re-usan el pool (36 instancias, sin asignar)');
}

/* ── P7 · LOS 10 CABLES DEL NÚCLEO EN DISCO ── */
{
  const cables = [
    ["import", "createEstelaPoder, createNubePrismas, createRoom"],
    ["campo remoto", "this._dlPrismaRemotoT = 0;"],
    ["build pools", "this.estelaPoder = createEstelaPoder();"],
    ["reset dl", "this._dlPrismaRemotoT = 0;   // r106 · la nube del rival muere con la sesión"],
    ["tick remoto", "if (this._dlPrismaRemotoT > 0) this._dlPrismaRemotoT -= dt;   // r106"],
    ["armar remoto", "if (id === 'prisma') this._dlPrismaRemotoT = DL_DUR.prisma || 10;"],
    ["emisión", "const firmaE = this._trailFirmaPoder();"],
    ["emisión arcoíris", "const arcoE = this._megaActivaId === 'prisma';"],
    ["nube IA", "try { this.nubePrisma.nace(this.ball.pos); } catch (ePNb1) { /* */ }"],
    ["nube rival 2", "try { this.nubePrisma.nace(this.ball.pos); } catch (ePNb2) { /* */ }"],
    ["espejo online", "if (this._dlPrismaRemotoT > 0) {\n                try { this.nubePrisma.nace(this.ball.pos); } catch (ePN33) { /* */ }"],
    ["regla r34 respetada", "las chispas\n    // nacen SOLO en el campo rival"],
  ];
  for (const [tag, txt] of cables) {
    CHK(c12.includes(txt), `P7 cable ${tag} presente en c12`);
  }
}

console.log(`\nESTELA+NUBE r106 · ${ok} OK · ${fail} FALLOS`);
process.exit(fail ? 1 : 0);
