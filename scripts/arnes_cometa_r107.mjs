/* r107 · ARNÉS COMETA + PRISMAS FACETADOS + ESFERA-ESCUDO — el six-pack
 *  del dueño contra las FÁBRICAS REALES de c07 (cero réplicas):
 *   T1 cometa: las chispas salen DETRÁS de la bola (contra el vuelo) y
 *      hay DOS capas (chispas + rastro).
 *   T2 cometa: el rastro se DISIPA (freno fuerte + vida corta) y sin
 *      emisión las dos capas se ocultan solas.
 *   T3 prismas: SOMBRADO DE FACETAS horneado — la geometría trae colores
 *      por cara (≥ 3 tonos distintos) y el pool r106 sigue vivo
 *      (nace/flota/encoge/desaparece/reusa sin asignar).
 *   T4 esfera: nace en la pala, crece PERSIGUIENDO a la bola (la
 *      superficie la alcanza), muere encogiéndose ≤ 0,2 s y tiene tope
 *      de vida 1,6 s.
 *   T5 cables: los 14 del núcleo presentes en disco.
 */
globalThis.window = globalThis;
const ctxStub = new Proxy({}, {
  get: () => (() => null),
  set: () => true,
});
const fakeCanvas = () => ({ width: 0, height: 0, getContext: () => ctxStub, style: {} });
globalThis.document = {
  getElementById: () => null,
  createElement: (tag) => (tag === 'canvas' ? fakeCanvas() : {}),
  addEventListener: () => {},
  visibilityState: 'visible',
};
try { globalThis.navigator = { userAgent: 'node-r107' }; } catch (e) { /* getter */ }

import * as THREE from 'three';
const c07 = await import('/home/z/my-project/src/game/core/c07_escena_sala.js');
const { createEstelaPoder, createNubePrismas, createOndaEsfera } = c07;
const fs = await import('node:fs');
const c12 = fs.readFileSync('/home/z/my-project/src/game/core/c12_pingponggame.js', 'utf8');

let ok = 0, fail = 0;
function CHK(cond, msg) {
  if (cond) { ok++; console.log('  ✓ ' + msg); }
  else { fail++; console.log('  ✗ FALLO: ' + msg); }
}

/* ── T1+T2 · COMETA ── */
{
  const E = createEstelaPoder();
  const rgb = [0.22, 0.78, 0.85];                // imán — cian
  const velBola = new THREE.Vector3(0.3, 0.1, -6.0);   // envío hacia el rival
  const posBola = new THREE.Vector3(0.1, 1.05, 0.8);
  E.emitir(posBola, velBola, 1 / 60, rgb);
  const capaPts = E.group.children.filter((c) => c.isPoints);
  CHK(capaPts.length === 2 && E.group.children.some((c) => c.visible),
    `T1 cometa con DOS capas (chispas + rastro) · nacidas y visibles`);
  // las chispas deben salir HACIA ATRÁS: velocidad media +z (contra el vuelo)
  let vzMed = 0, n = 0;
  const L = capaPts[0];
  const vel = L.geometry.attributes.position.array; // no se usa — vel interna
  for (let i = 0; i < 4; i++) E.emitir(posBola, velBola, 1 / 60, rgb);
  // tras varios emitir, integra y compara contra la posición de la bola
  E.update(1 / 60);
  const pa = L.geometry.attributes.position.array;
  let detras = 0, tot = 0;
  for (let i = 0; i < L.geometry.attributes.position.count; i++) {
    if (pa[i * 3 + 1] <= -5) continue;            // muertas fuera de vista
    tot++;
    if (pa[i * 3 + 2] > posBola.z) detras++;      // por detrás (z mayor)
  }
  CHK(tot > 0 && detras === tot,
    `T1 chispas DETRÁS de la bola (${detras}/${tot} con z mayor que la bola)`);
  // disipación: sin emitir, 1,3 s → ambas capas ocultas
  for (let i = 0; i < 80; i++) E.update(1 / 60);
  CHK(!capaPts.some((c) => c.visible),
    'T2 el cometa se DISIPA entero (1,3 s sin emisión → capas ocultas)');
  // el freno disipa: una chispa recién nacida se queda ATRÁS de la bola
  // (la bola recorrería 8*0,42 = 3,36 m; la chispa frena por el drag)
  const E2 = createEstelaPoder();
  const vFast = new THREE.Vector3(0, 0, -8);
  E2.emitir(new THREE.Vector3(0, 1, 0), vFast, 1 / 60, rgb);
  const L2 = E2.group.children[0];
  const p0 = L2.geometry.attributes.position.array.slice(0, 3);
  for (let i = 0; i < 25; i++) E2.update(1 / 60);   // 0,42 s
  const p1 = L2.geometry.attributes.position.array;
  const desplaz = Math.abs(p1[2] - p0[2]);
  const bolaDist = vFast.length() * 0.42;
  CHK(desplaz < 0.6 && desplaz < 0.25 * bolaDist,
    `T2 el freno DISIPA el empuje (chispa ${(desplaz * 100).toFixed(0)} cm vs bola ${(bolaDist * 100).toFixed(0)} cm — se queda atrás disipándose)`);
}

/* ── T3 · PRISMAS FACETADOS + pool r106 intacto ── */
{
  const NB = createNubePrismas();
  const geo = NB.group.geometry;
  CHK(!!geo.attributes.color,
    'T3 la geometría del prisma trae COLORES horneados (vertexColors)');
  // ≥ 3 tripletes distintos de color en el atributo (caras con tonos
  // diferentes) — nada plano
  const ca = geo.attributes.color.array;
  const claves = new Set();
  for (let v = 0; v < geo.attributes.color.count; v++) {
    claves.add(`${ca[v * 3].toFixed(2)},${ca[v * 3 + 1].toFixed(2)},${ca[v * 3 + 2].toFixed(2)}`);
  }
  CHK(claves.size >= 3,
    `T3 caras de DIFERENTES TONOS (${claves.size} facetas distintas — no plano)`);
  // el pool r106 sigue vivo: nace, flota, desaparece, reusa
  const p0 = new THREE.Vector3(0.2, 1.05, 0.9);
  NB.nace(p0, 30);
  CHK(NB.group.visible, 'T3 nube visible al nacer (30 prismas)');
  const readPos = (i) => {
    const a = NB.group.instanceMatrix.array;
    return [a[i * 16 + 12], a[i * 16 + 13], a[i * 16 + 14]];
  };
  for (let i = 0; i < 60; i++) NB.update(1 / 60);
  let dMed = 0;
  for (let i = 0; i < 30; i++) {
    const [x, y, z] = readPos(i);
    dMed += Math.hypot(x - p0.x, y - p0.y, z - p0.z);
  }
  dMed /= 30;
  CHK(dMed > 0.10 && dMed < 2.0,
    `T3 nube flotando: dispersión media ${(dMed * 100).toFixed(0)} cm a 1 s`);
  for (let i = 0; i < 420; i++) NB.update(1 / 60);   // 7 s
  const aFin = NB.group.instanceMatrix.array;
  let muertas = 0;
  for (let i = 0; i < 36; i++) {
    if (aFin[i * 16] === 0 && aFin[i * 16 + 5] === 0) muertas++;
  }
  CHK(!NB.group.visible && muertas >= 30,
    `T3 desaparece entera ≤ 5,5 s (${muertas}/36 a escala 0 · grupo oculto)`);
  NB.nace(p0, 30);
  NB.nace(new THREE.Vector3(-0.2, 1.0, 0.8), 30);
  NB.update(1 / 60);
  CHK(NB.group.visible && NB.group.count === 36,
    'T3 dos nubes seguidas re-usan el pool (36 instancias, sin asignar)');
}

/* ── T4 · ESFERA-ESCUDO ── */
{
  const OE = createOndaEsfera();
  const centro = new THREE.Vector3(0.1, 1.0, 1.2);    // la pala al impacto
  OE.nace(centro);
  CHK(OE.group.visible && OE.group.scale.x <= 0.15,
    'T4 esfera nace en la PALA (visible, radio inicial de bola)');
  CHK(OE.viva(), 'T4 viva tras nacer');
  // la bola huye a 2× — la superficie la PERSIGUE
  const bola = new THREE.Vector3(0.1, 1.05, 0.2);     // 1,0 m por delante
  for (let i = 0; i < 30; i++) OE.update(1 / 60, bola);   // 0,5 s
  const r = OE.group.scale.x;
  CHK(r > 0.8 && r <= 1.5,
    `T4 la superficie EMPUJA: radio ${(r * 100).toFixed(0)} cm persigue una bola a 1 m (empuja con su superficie)`);
  // muerte con encogido ≤ 0,2 s
  OE.muere();
  for (let i = 0; i < 14; i++) OE.update(1 / 60, bola);
  CHK(!OE.group.visible && !OE.viva(),
    'T4 muere ENCOGIÉNDOSE ≤ 0,2 s (grupo oculto)');
  // tope de vida 1,6 s: nace y suelta la bola — muere sola
  OE.nace(centro);
  for (let i = 0; i < 120; i++) OE.update(1 / 60, null);  // 2 s sin bola
  CHK(!OE.group.visible && !OE.viva(),
    'T4 tope de vida 1,6 s: muere sola aunque la bola escape');
}

/* ── T5 · LOS 14 CABLES DEL NÚCLEO EN DISCO ── */
{
  const cables = [
    ["import esfera", "createNubePrismas, createOndaEsfera, createRoom"],
    ["campo mia", "this._megaActivaMia = true;"],
    ["build esfera", "this.ondaEsfera = createOndaEsfera();"],
    ["megaTrigger mia", "this._megaActivaMia = true;   // r107: esta ventana la arma YO"],
    ["dlTrigger mia", "this._megaActivaMia = true;      // r107: lanzamiento PROPIO en duelos"],
    ["remote no-cometa", "this._megaActivaMia = false;   // r107: la armó EL RIVAL — su cometa no es mío"],
    ["verja lanzador", "this._megaActivaMia && this._megaActivaRest() > 0"],
    ["verja envío propio", "bE.vel.z < -0.05"],
    ["sin estelas propias", "!R107_SIN_COMETA[this._megaActivaId]"],
    ["emisión cometa", "this.estelaPoder.emitir(bE.pos, bE.vel, dt, firmaE);"],
    ["gancho esfera", "this._ondaEsferaNace(this.ball.pos, this.ball.vel);"],
    ["bote sorpresivo", "vEf.x += (Math.random() - 0.5) * 2 * EFECTO_SORPRESA_X;"],
    ["muerte pala IA", "try { if (this.ondaEsfera && this.ondaEsfera.viva()) this._ondaEsferaMuere(); }"],
    ["muerte rival 2", "catch (eOEr2) { /* */ }"],
    ["fin ventana", "try { if (this.ondaEsfera) this.ondaEsfera.muere(); } catch (eOEfin) { /* */ }"],
    ["métodos esfera", "_ondaEsferaNace(pos, vel) {"],
    ["const sin-cometa", "const R107_SIN_COMETA = {"],
    ["const sorpresa", "const EFECTO_SORPRESA_X = 1.1;"],
    ["sonido grave", "this.audio.playOsc(52, 118, 0.5, 'sawtooth', 0.2, 0);"],
    ["doble velocidad", "vOn.multiplyScalar(2);   // AL DOBLE"],
  ];
  for (const [tag, txt] of cables) {
    CHK(c12.includes(txt), `T5 cable ${tag} presente en c12`);
  }
}

console.log(`\nCOMETA+FACETAS+ESFERA r107 · ${ok} OK · ${fail} FALLOS`);
process.exit(fail ? 1 : 0);
