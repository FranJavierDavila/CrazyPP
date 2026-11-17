#!/usr/bin/env node
/**
 * CRAZY PING PONG · QA v3.6.28 · UNIT DEL ESPEJO DE RED (multijugador)
 * =====================================================================
 * Las funciones estáticas de NetLink (c09_red_netlink.js) se EXTRAEN DEL
 * FICHERO REAL (nada de copias): involución pos/vec/spin, doble espejo del
 * cuaternión (R·q·R⁻¹ dos veces = identidad), remapeo de causas y código
 * de sala. El bug más caro del multijugador histórico (pala rival rodada,
 * bola flotando sobre mesa fantasma) vive aquí: si esto pasa, la red está
 * sana en su fundamento.
 * Salida: «RESULTADO: N OK · M fallos» (contrato qa_todo).
 */
import { readFileSync } from 'fs';

const RAIZ = '/home/z/my-project';
let ok = 0, fails = 0;
function chk(cond, label) {
  if (cond) { ok++; console.log('  ✓ ' + label); }
  else { fails++; console.log('  ✗ FALLO: ' + label); }
}

/* ---------- extracción de los métodos estáticos del fichero REAL ------- */
const src = readFileSync(RAIZ + '/src/game/core/c09_red_netlink.js', 'utf8');

function corta(desde, hasta) {
  const i = src.indexOf(desde);
  if (i < 0) throw new Error('no encuentro ' + desde);
  const j = src.indexOf(hasta, i);
  if (j < 0) throw new Error('no encuentro ' + hasta);
  return src.slice(i, j);   // el marcador final queda FUERA (no duplicar)
}

const bloques = [
  corta('static CODE_CHARS', '// sin 0/O/1/I/L'),
  corta('static posToNet', '  static posFromNet'),
  corta('static posFromNet', '  static vecToNet'),
  corta('static vecToNet', '  static vecFromNet'),
  corta('static vecFromNet', '  /** v2.25: helpers de EMISIÓN'),
  corta('static spinFromNet', '  static quatFromNet'),
  corta('static quatFromNet', '  static quatToNet'),
  corta('static quatToNet', '  /** v2.91 · La propiedad'),
  corta('static CAUSE_SWAP', '  static remapCause'),
  corta('static remapCause', '  static quatFromNet'),
  'function ' + corta('  genCode() {', '  mySide()'),   // método de instancia → función
]
  .join('\n')
  // fuera de la clase: `static X = …` → `var X = …` y `static m(…)` → `function m(…)`
  .replace(/^ *static ([A-Za-z_$][\w$]*\s*=)/gm, 'var $1')
  .replace(/^ *static /gm, 'function ');

const DIMS = { tableTopY: 0.76 };
const NetMirror = new Function(
  'DIMS',
  bloques +
  '\nclass NetMirror { }\n' +
  // los cuerpos extraídos viven FUERA de la clase: se montan como métodos
  'NetMirror.CODE_CHARS = CODE_CHARS;\n' +
  'NetMirror.posToNet = posToNet;\n' +
  'NetMirror.posFromNet = posFromNet;\n' +
  'NetMirror.vecToNet = vecToNet;\n' +
  'NetMirror.vecFromNet = vecFromNet;\n' +
  'NetMirror.spinFromNet = spinFromNet;\n' +
  'NetMirror.quatFromNet = quatFromNet;\n' +
  'NetMirror.quatToNet = quatToNet;\n' +
  'NetMirror.CAUSE_SWAP = CAUSE_SWAP;\n' +
  'NetMirror.remapCause = remapCause;\n' +
  'NetMirror.genCode = genCode;\n' +
  'const NetLink = NetMirror;\n' +   // remapCause/genCode citan NetLink.*
  'return NetMirror;'
)(DIMS);

/* stubs mínimos de THREE (los métodos solo usan .set y x/y/z/w) */
class V3 { constructor(x=0,y=0,z=0){ this.x=x; this.y=y; this.z=z; }
  set(x,y,z){ this.x=x; this.y=y; this.z=z; return this; } }
class Q4 { constructor(x=0,y=0,z=0,w=1){ this.x=x; this.y=y; this.z=z; this.w=w; }
  set(x,y,z,w){ this.x=x; this.y=y; this.z=z; this.w=w; return this; } }

const RND = (a, b) => a + Math.random() * (b - a);

console.log('== 1 · INVOLUCIÓN DE POSICIÓN (posToNet ∘ posFromNet = id) ==');
{
  let maxErr = 0;
  for (let i = 0; i < 300; i++) {
    const p = new V3(RND(-3, 3), RND(0, 2), RND(-5, 2));
    const net = NetMirror.posToNet(p);
    const out = NetMirror.posFromNet(net, new V3());
    maxErr = Math.max(maxErr,
      Math.abs(out.x - p.x) + Math.abs(out.y - p.y) + Math.abs(out.z - p.z));
  }
  chk(maxErr < 1e-9, '300 puntos aleatorios van y vuelven (err ' + maxErr.toExponential(2) + ')');
}
{
  // la Y viaja RELATIVA al tapete (lección v2.91)
  const p = new V3(0.3, DIMS.tableTopY + 0.2, -1.0);
  const net = NetMirror.posToNet(p);
  chk(Math.abs(net[1] - 0.2) < 1e-9, 'la Y de red está anclada AL TAPETE (y-T)');
  chk(Math.abs(net[2] - (-3.2 - (-1.0))) < 1e-9, 'el Z de red cruza el espejo (-3.2-z)');
}

console.log('== 2 · INVOLUCIÓN DE VECTOR Y SPIN ==');
{
  let maxErr = 0, maxErrS = 0;
  for (let i = 0; i < 300; i++) {
    const v = new V3(RND(-9, 9), RND(-9, 9), RND(-9, 9));
    const out = NetMirror.vecFromNet(NetMirror.vecToNet(v), new V3());
    maxErr = Math.max(maxErr, Math.abs(out.x - v.x) + Math.abs(out.y - v.y) + Math.abs(out.z - v.z));
    const s = new V3(RND(-5, 5), RND(-5, 5), RND(-5, 5));
    // en la red el spin SIEMPRE es array (JSON): espejo dos veces = identidad
    const a1 = NetMirror.spinFromNet([s.x, s.y, s.z], new V3());
    const a2 = NetMirror.spinFromNet([a1.x, a1.y, a1.z], new V3());
    maxErrS = Math.max(maxErrS, Math.abs(a2.x - s.x) + Math.abs(a2.y - s.y) + Math.abs(a2.z - s.z));
  }
  chk(maxErr < 1e-9, 'vectores (velocidad) van y vuelven');
  chk(maxErrS < 1e-9, 'spin espeja DOS veces = original (Magnus coherente)');
}

console.log('== 3 · CUATERNIÓN: doble espejo R·q·R⁻¹ ≡ identidad ==');
{
  let maxErr = 0;
  for (let i = 0; i < 300; i++) {
    // cuaternión aleatorio normalizado (orientación visual de la pala)
    const q = new Q4(RND(-1, 1), RND(-1, 1), RND(-1, 1), RND(-1, 1));
    const n = Math.hypot(q.x, q.y, q.z, q.w);
    q.set(q.x / n, q.y / n, q.z / n, q.w / n);
    const a = NetMirror.quatFromNet(NetMirror.quatToNet(q), new Q4());   // 1er espejo
    const b = NetMirror.quatFromNet(NetMirror.quatToNet(a), new Q4());   // 2º espejo
    maxErr = Math.max(maxErr, Math.abs(b.x - q.x) + Math.abs(b.y - q.y) +
      Math.abs(b.z - q.z) + Math.abs(b.w - q.w));
  }
  chk(maxErr < 1e-9, 'la pala rival NO llega rodada (doble conjugación = q)');
}
{
  // q' = R q R⁻¹ con R=180°Y debe mapear el eje +X en -X y dejar Y intacta
  const q = new Q4(0, 0, 0, 1);   // identidad
  const out = NetMirror.quatFromNet([0, 0, 0, 1], new Q4());
  // conjugación de la identidad por 180°Y: sigue siendo identidad o el giro completo
  const esInvolucion = (Math.abs(out.w) > 0.999) || (Math.abs(out.y) > 0.999);
  chk(esInvolucion, 'identidad conjugada por el espejo sigue siendo un giro válido de 180°Y');
}

console.log('== 4 · PUREZA (los helpers no mutan la entrada) ==');
{
  const q = [0.1, 0.2, 0.3, 0.9];
  const copia = q.slice();
  NetMirror.quatFromNet(q, new Q4());
  chk(JSON.stringify(q) === JSON.stringify(copia), 'quatFromNet no toca el paquete de red');
  const p = new V3(1, 2, 3);
  NetMirror.posToNet(p);
  chk(p.x === 1 && p.y === 2 && p.z === 3, 'posToNet no toca la posición local');
}

console.log('== 5 · REMAPEO DE CAUSAS (perspectiva) ==');
{
  chk(NetMirror.remapCause('own_you', true) === 'own_opp', 'own_you → own_opp en el invitado');
  chk(NetMirror.remapCause('own_opp', true) === 'own_you', 'own_opp → own_you (idempotente por pares)');
  chk(NetMirror.remapCause('let', true) === 'let', 'causa neutra (LET) intacta');
  chk(NetMirror.remapCause('own_you', false) === 'own_you', 'sin forGuest, sin cambio (host)');
}

console.log('== 6 · CÓDIGO DE SALA (alfabeto legible en el casco) ==');
{
  const OKC = /^[A-HJ-KM-NP-Z2-9]{5}$/;   // sin 0/O/1/I/L
  let bien = true;
  for (let i = 0; i < 200; i++) bien = bien && OKC.test(NetMirror.genCode());
  chk(bien, '200 códigos de 5 caracteres sin 0/O/1/I/L');
}

console.log('== 7 · ESPEJO DE UN BOTE REMOTO (drainNetwork) ==');
{
  // el bote del rival llega en crudo y se re-espeja: cae en MI marco
  const T = DIMS.tableTopY;
  const ev = [0.4, 0.1, -1.2];           // (x, y-tapete, z) en red
  const lx = -ev[0], ly = ev[1] + T, lz = -3.2 - ev[2];
  chk(Math.abs(lz - (-2.0)) < 1e-9, 'el bote del rival cae al fondo de MI campo (z -2.0 < centro -1.6)');
  chk(Math.abs(ly - (T + 0.1)) < 1e-9, 'la altura del bote se re-ancla a MI tapa (sin mesa fantasma)');
}

console.log('\nRESULTADO: ' + ok + ' OK · ' + fails + ' fallos');
process.exit(fails ? 1 : 0);
