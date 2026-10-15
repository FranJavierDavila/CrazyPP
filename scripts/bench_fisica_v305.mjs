#!/usr/bin/env node
/**
 * CRAZY PING PONG · Banco de pruebas v3.0.5-FIS1 (física viva + palas con carácter)
 * Extrae las funciones REALES de public/game.html (fuente única de verdad) y
 * ejecuta 27 escenarios en Node sin navegador.
 *   node scripts/bench_fisica_v305.mjs
 */
import { readFileSync } from 'node:fs';

const SRC = readFileSync(new URL('../public/game.html', import.meta.url), 'utf8');

/* ── extracción por llaves ─────────────────────────────────────────── */
function extractFn(name) {
  const i = SRC.indexOf('function ' + name + '(');
  if (i < 0) throw new Error('función no encontrada: ' + name);
  const d = SRC.indexOf('{', i);
  let depth = 0;
  for (let j = d; j < SRC.length; j++) {
    if (SRC[j] === '{') depth++;
    else if (SRC[j] === '}') { depth--; if (depth === 0) return SRC.slice(i, j + 1); }
  }
  throw new Error('llaves desequilibradas en ' + name);
}
function extractConstObj(name) {
  const i = SRC.indexOf('const ' + name + ' = {');
  if (i < 0) throw new Error('const no encontrada: ' + name);
  const d = SRC.indexOf('{', i);
  let depth = 0;
  for (let j = d; j < SRC.length; j++) {
    if (SRC[j] === '{') depth++;
    else if (SRC[j] === '}') { depth--; if (depth === 0) return SRC.slice(i, j + 1) + ';'; }
  }
  throw new Error('llaves desequilibradas en ' + name);
}

// vectores temporales del módulo (colisiones comparten estado temporal)
const vecs = [...SRC.matchAll(/^const (\w+) = new THREE\.Vector3\(\);$/gm)].map(m => m[0]).join('\n');

// bloque PALAS CON CARÁCTER completo: const PADDLE_PERKS … fin de paddlePerkFor
const pStart = SRC.indexOf('const PADDLE_PERKS = {');
const ppfI = SRC.indexOf('function paddlePerkFor(');
if (pStart < 0 || ppfI < 0) throw new Error('bloque PADDLE_PERKS no encontrado');
const ppfEnd = (() => { let d = 0; const dd = SRC.indexOf('{', ppfI);
  for (let j = dd; j < SRC.length; j++) {
    if (SRC[j] === '{') d++; else if (SRC[j] === '}') { d--; if (d === 0) return j + 1; } } })();
const perksBlock = SRC.slice(pStart, ppfEnd);

const CODE = [
  extractConstObj('DIMS'), vecs, perksBlock,
  extractFn('applyAerodynamics'), extractFn('applyBounceSpin'), extractFn('bounceOnTable'),
  extractFn('collidePaddle'), extractFn('collideTable'), extractFn('predictStrike'),
  extractFn('simulateServePath'),
  `return { DIMS, tmpPrev, applyAerodynamics, applyBounceSpin, bounceOnTable,
    collidePaddle, collideTable, predictStrike, simulateServePath,
    paddlePerkFor, PADDLE_PERKS, setSkin: __ppSetPaddleSkin };`,
].join('\n');

/* ── stub mínimo de THREE.Vector3 (suficiente para la física extraída) ── */
class V3 {
  constructor(x = 0, y = 0, z = 0) { this.x = x; this.y = y; this.z = z; }
  set(x, y, z) { this.x = x; this.y = y; this.z = z; return this; }
  copy(v) { this.x = v.x; this.y = v.y; this.z = v.z; return this; }
  clone() { return new V3(this.x, this.y, this.z); }
  add(v) { return this.copy(this.clone().addVectors(this, v)); }
  addVectors(a, b) { this.x = a.x + b.x; this.y = a.y + b.y; this.z = a.z + b.z; return this; }
  addScaledVector(v, s) { this.x += v.x * s; this.y += v.y * s; this.z += v.z * s; return this; }
  sub(v) { this.x -= v.x; this.y -= v.y; this.z -= v.z; return this; }
  multiplyScalar(s) { this.x *= s; this.y *= s; this.z *= s; return this; }
  dot(v) { return this.x * v.x + this.y * v.y + this.z * v.z; }
  cross(v) { const x = this.y * v.z - this.z * v.y, y = this.z * v.x - this.x * v.z, z = this.x * v.y - this.y * v.x; return this.set(x, y, z); }
  crossVectors(a, b) { return this.set(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x); }
  length() { return Math.hypot(this.x, this.y, this.z); }
  lengthSq() { return this.x * this.x + this.y * this.y + this.z * this.z; }
  distanceTo(v) { return Math.hypot(this.x - v.x, this.y - v.y, this.z - v.z); }
  distanceToSquared(v) { const dx = this.x - v.x, dy = this.y - v.y, dz = this.z - v.z; return dx * dx + dy * dy + dz * dz; }
  lerpVectors(a, b, t) { this.x = a.x + (b.x - a.x) * t; this.y = a.y + (b.y - a.y) * t; this.z = a.z + (b.z - a.z) * t; return this; }
  angleTo(v) { const d = this.clone().dot(v) / Math.max(1e-12, this.length() * v.length()); return Math.acos(Math.min(1, Math.max(-1, d))); }
  normalize() { const l = this.length(); return l ? this.multiplyScalar(1 / l) : this; }
  setLength(l) { return this.normalize().multiplyScalar(l); }
  lerp(v, a) { this.x += (v.x - this.x) * a; this.y += (v.y - this.y) * a; this.z += (v.z - this.z) * a; return this; }
  negate() { return this.multiplyScalar(-1); }
}
const THREE = { Vector3: V3 };

/* ── fábrica del módulo físico ─────────────────────────────────────── */
const R = new Function('THREE', '__ls', `
  const localStorage = __ls; const window = {};
  ${CODE}
`)(THREE, { getItem: () => null });
const { DIMS } = R;

/* ── utilidades de escenario ───────────────────────────────────────── */
const V = (x, y, z) => new V3(x, y, z);
const mkBall = (pos, vel, spin) => ({
  pos: pos.clone(), prev: pos.clone(), vel: vel.clone(), spin: spin.clone(),
  ignoreTable: false,
});
const mkPad = (o = {}) => ({
  prev: o.pos ? o.pos.clone() : V(0, 0.86, 0.5),
  pos: o.pos ? o.pos.clone() : V(0, 0.86, 0.5),
  prevNormal: V(0, 0, 1), normal: V(0, 0, 1),
  prevRight: V(1, 0, 0), right: V(1, 0, 0),
  prevUp: V(0, 1, 0), up: V(0, 1, 0),
  vel: o.vel ? o.vel.clone() : V(), omega: o.omega ? o.omega.clone() : V(),
  who: o.who || 'player', index: 0, extraReach: 0, cooldown: 0,
});
/** golpe estándar: bola entrando en −z CRUZANDO el plano de la pala quieta mirando a +z */
function hit({ ballVel, ballSpin = V(), ballX = 0, padVel = V(), padOmega = V(), who = 'player', skin = null, fis = null }) {
  const keep = { fis: DIMS.physicsRealism, perks: DIMS.paddlePerks };
  if (fis !== null) DIMS.physicsRealism = fis;
  const prevSkin = typeof window !== 'undefined' ? window.__PP_PADDLE_SKIN : undefined;
  R.setSkin(skin || 'clasica');
  const bpos = V(ballX, 1.0, 0.49);                  // dNow = −0,01 (ya cruzó el plano)
  const ball = mkBall(bpos, ballVel, ballSpin);
  R.tmpPrev.copy(bpos).add(V(0, 0, 0.05));           // venía de +z (dPrev = +0,04)
  const pad = mkPad({ vel: padVel, omega: padOmega, who });
  const ev = [];
  R.collidePaddle(ball, pad, 1, ev);
  R.setSkin(prevSkin || 'clasica');
  DIMS.physicsRealism = keep.fis; DIMS.paddlePerks = keep.perks;
  return { ball, events: ev, hitDone: ev.length > 0 };
}
/** bote estándar en mesa vía collideTable (física real) */
function bounce({ vel, spin, fis = null }) {
  const keep = DIMS.physicsRealism;
  if (fis !== null) DIMS.physicsRealism = fis;
  const ball = { pos: V(0, DIMS.tableTopY + DIMS.ballRadius - 0.001, -2.2), vel: vel.clone(), spin: spin.clone(), ignoreTable: false };
  const ev = [];
  R.collideTable(ball, DIMS.tableTopY + DIMS.ballRadius + 0.01, ev);
  DIMS.physicsRealism = keep;
  return ball;
}

/* ── corredor de pruebas ───────────────────────────────────────────── */
let ok = 0, fails = 0;
const T = (name, cond, detail = '') => {
  if (cond) { ok++; console.log(`  ✅ ${name}${detail ? '  — ' + detail : ''}`); }
  else { fails++; console.log(`  ❌ ${name}${detail ? '  — ' + detail : ''}`); }
};
const f1 = (x) => Math.round(x * 10) / 10;
const f2 = (x) => Math.round(x * 100) / 100;

console.log('· Aerodinámica y bote legacy (rollback exacto)');
{
  // 1a · drag cuadrático real: 6 m/s cae claramente en 0,5 s
  const v = V(0, 0, 6), s = V();
  for (let i = 0; i < 120; i++) R.applyAerodynamics(v, s, 1 / 240);
  T('1a Drag real: 6 m/s pierde velocidad en 0,5 s', v.z < 5.4, `6.00 → ${f2(v.z)} m/s`);
  // 1b · Magnus: topspin about x, bola +z: curva hacia abajo (vy negativo)
  const v2 = V(0, 0, 6), s2 = V(70, 0, 0);
  for (let i = 0; i < 120; i++) R.applyAerodynamics(v2, s2, 1 / 240);
  T('1b Magnus del topspin curva hacia abajo', v2.y < -0.01, `vy ${f2(v2.y)}`);
}
{
  // 2 · LEGACY GOLPE byte-exacto (physicsRealism=0): spin = brush v2.x
  const h = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), fis: 0 });
  const e = DIMS.spinImpulse * 3;                      // tmpSurf=(0,3,0)×N=3 → ×10
  T('2 Legacy golpe: spin = brush exacto v2.x', Math.abs(h.ball.spin.x - e) < 1e-6,
    `ωx ${f1(h.ball.spin.x)} (esperado ${e})`);
}
{
  // 3 · LEGACY BOTE byte-exacto (fricción 0,94 + kick + 0,72)
  const b = bounce({ vel: V(1, -3, -4), spin: V(-50, 0, 0), fis: 0 });
  T('3 Legacy bote: vy exacta 2,64', Math.abs(b.vel.y - 2.64) < 1e-9, `vy ${f2(b.vel.y)}`);
  T('3b Legacy bote: vx 0,94 y kick exactos', Math.abs(b.vel.x - (0.94 - 0.012 * 0)) < 1e-9 &&
    Math.abs(b.vel.z - (-4 * 0.94 + 0.012 * -50)) < 1e-9 && Math.abs(b.spin.x - -36) < 1e-9,
    `vz ${f2(b.vel.z)} ωx ${f1(b.spin.x)}`);
}

console.log('· P1 · GOLPE VIVO (goma con fricción, punto dulce)');
{
  // 4 · golpe centrado sólido
  const h = hit({ ballVel: V(0, 0, -10) });
  const sp = h.ball.vel.length();
  T('4 Golpe centrado sólido (≥ 8 m/s de salida)', sp >= 8, `${f2(sp)} m/s`);
  // 5 · el canto pega sordo (≥ 15 % menos que el centro)
  const hc = hit({ ballVel: V(0, 0, -6) });
  const he = hit({ ballVel: V(0, 0, -6), ballX: 0.078 });   // offC ≈ 0,98
  const rc = hc.ball.vel.length(), re = he.ball.vel.length();
  T('5 El CANTO pega sordo: ≥ 15 % menos velocidad', re <= rc * 0.85, `canto ${f2(re)} vs centro ${f2(rc)} m/s`);
  // 6 · brush ARRASTRA: pala sube 3 m/s → la bola sale con vy +
  const hb = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0) });
  T('6 La goma ARRASTRA en el brush (vy de salida > 0,25)', hb.ball.vel.y > 0.25, `vy ${f2(hb.ball.vel.y)} m/s`);
  // 7 · REVERSIÓN: bloquear un topspin devuelve giro invertido
  const hb2 = hit({ ballVel: V(0, 0, -6), ballSpin: V(80, 0, 0) });  // topspin entrante
  T('7 Bloque de topspin sale CARGADO (giro invertido)', hb2.ball.spin.x < 0,
    `ωx +80 → ${f1(hb2.ball.spin.x)}`);
  // 8 · el brush da giro enorme (rpm razonables, tope spinMax)
  const hb3 = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0) });
  const rpm = Math.abs(hb3.ball.spin.x) * 60 / (2 * Math.PI);
  T('8 Brush de 3 m/s imprime giro fuerte (≥ 400 rpm)', rpm >= 400, `~${Math.round(rpm)} rpm`);
}

console.log('· P2 · BOTE FÍSICO (slip-coupled, Coulomb, impacto)');
{
  // 9 · topspin drive ACELERA al botar
  const vi = V(0, -3, -4), si = V(-300, 0, 0);
  const b = bounce({ vel: vi, spin: si });
  T('9 Topspin drive ACELERA al botar', b.vel.length() > vi.length(), `${f2(vi.length())} → ${f2(b.vel.length())} m/s`);
  // 10 · topspin suave GANA giro
  const b2 = bounce({ vel: V(0, -3, -4), spin: V(-70, 0, 0) });
  T('10 Topspin conserva/gana giro al botar', b2.spin.x < -70, `ωx −70 → ${f1(b2.spin.x)}`);
  // 11 · backspin FRENA en seco
  const vbi = V(0, -2.4, -3.2);
  const b3 = bounce({ vel: vbi, spin: V(70, 0, 0) });
  T('11 Backspin FRENA (≥ 15 % de pérdida)', b3.vel.length() <= vbi.length() * 0.85, `${f2(vbi.length())} → ${f2(b3.vel.length())} m/s`);
  // 12 · a la mesa se le COME el efecto del backspin
  T('12 La mesa come el backspin (≥ 80 % de pérdida)', Math.abs(b3.spin.x) <= 14, `ωx +70 → ${f1(b3.spin.x)}`);
  // 13 · lateral DESVÍA
  const b4 = bounce({ vel: V(0, -2.5, -4), spin: V(0, 0, 120) });
  T('13 Sidespin desvía el bote (|vx| > 0,3)', Math.abs(b4.vel.x) > 0.3, `vx ${f2(b4.vel.x)}`);
  // 14 · el agarre ESCALA con el impacto
  const soft = bounce({ vel: V(0, -1, -3.2), spin: V(90, 0, 0) });
  const hard = bounce({ vel: V(0, -4, -3.2), spin: V(90, 0, 0) });
  const dSoft = Math.abs(soft.vel.z - -3.2), dHard = Math.abs(hard.vel.z - -3.2);
  T('14 El bote fuerte cambia más (grip 0,22→0,60)', dHard > dSoft, `Δvz suave ${f2(dSoft)} vs fuerte ${f2(dHard)}`);
  // 15 · UNA SOLA ECUACIÓN: collideTable ≡ bounceOnTable
  const v1 = V(0.3, -3, -4), s1 = V(-120, 0, 40);
  const b1 = bounce({ vel: v1, spin: s1 });
  const v2b = v1.clone(), s2b = s1.clone();
  R.bounceOnTable(v2b, s2b, 3);
  const same = v1.x * 0 === 0 && Math.abs(b1.vel.x - v2b.x) < 1e-9 &&
    Math.abs(b1.vel.z - v2b.z) < 1e-9 && Math.abs(b1.spin.x - s2b.x) < 1e-9;
  T('15 La física real y bounceOnTable son LA MISMA ecuación', same);
}

console.log('· IA y saque alineados con la física nueva');
{
  // 16 · la IA recibe un punto de intercepción (predictStrike corre con P2)
  const ball = { pos: V(0, 1.2, -0.6), vel: V(0, -0.5, -6), spin: V(-60, 0, 0) };
  const strike = R.predictStrike(ball, -1, false);
  T('16 predictStrike (IA) devuelve intercepción con física nueva', !!strike && !!strike.point,
    strike ? `t ${f2(strike.t)} s` : '');
  // 17 · el solver de saque encuentra saques legales con P2
  let found = null;
  outer: for (const vz of [3.4, 3.8, 4.2, 4.6, 5.0]) for (const vy of [2.0, 2.4, 2.8, 1.6]) {
    const res = R.simulateServePath(V(0, 1.0, 0.35), V(0, vy, -vz), V(0, 0, 0), 1);
    if (res.ok) { found = res; break outer; }
  }
  T('17 El solver de saque encuentra saques legales', !!found, found ? `vz ${f1(found.oppZ)} rival` : '');
}

console.log('· Interruptores: rollback exacto a v2.x');
{
  // 18 · physicsRealism=0 → bote legacy exacto con spin (kick + 0,72)
  const b = bounce({ vel: V(0, -3, -4), spin: V(-50, 0, 0), fis: 0 });
  const expect = -4 * 0.94 + 0.012 * -50;
  T('18 Legacy: bote v2.x intacto', Math.abs(b.vel.z - expect) < 1e-9 && Math.abs(b.spin.x - (-36)) < 1e-9,
    `vz ${f2(b.vel.z)} (esp ${f2(expect)}) ωx ${f1(b.spin.x)}`);
  // 19 · paddlePerks=0 → jugador neutra EXACTO aunque lleve skin
  const neut = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), skin: 'clasica', fis: 1 });
  DIMS.paddlePerks = 0;
  const off = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), skin: 'arcoiris', fis: 1 });
  DIMS.paddlePerks = 1;
  T('19 Interruptor perks OFF = goma neutra exacta',
    Math.abs(off.ball.spin.x - neut.ball.spin.x) < 1e-9 &&
    Math.abs(off.ball.vel.y - neut.ball.vel.y) < 1e-9,
    `ω ${f1(off.ball.spin.x)} vs neutra ${f1(neut.ball.spin.x)}`);
}

console.log('· PALAS CON CARÁCTER (perks)');
{
  const blockSpeed = (skin) => f2(hit({ ballVel: V(0, 0, -4), skin }).ball.vel.length());
  const brushSpin = (skin) => hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), skin }).ball.spin.x;
  // 20 · estructura: 6 pieles con tag, carbon dual
  const P = R.PADDLE_PERKS;
  T('20 6 pieles con carácter · Pro Carbon DOBLE GOMA',
    Object.keys(P).length === 6 && !!(P.carbon && P.carbon.dual) &&
    P.fuego.tag === 'perk_of' && P.hielo.tag === 'perk_de');
  // 21 · FUEGO = OFENSIVA: bloquea más fuerte
  const cl = blockSpeed('clasica'), fu = blockSpeed('fuego');
  T('21 Fuego OFENSIVA: golpea más fuerte (≥ +5 %)', fu >= cl * 1.05, `${cl} → ${fu} m/s`);
  // 22 · FUEGO imprime más efecto que la clásica
  T('22 Fuego +8 % de efecto', brushSpin('fuego') > brushSpin('clasica'), 'ω mayor con Fuego');
  // 23 · HIELO = DEFENSIVA: el canto PERDONA
  const rCl = hit({ ballVel: V(0, 0, -6), ballX: 0.076, skin: 'clasica' }).ball.vel.length() /
              hit({ ballVel: V(0, 0, -6), skin: 'clasica' }).ball.vel.length();
  const rHi = hit({ ballVel: V(0, 0, -6), ballX: 0.076, skin: 'hielo' }).ball.vel.length() /
              hit({ ballVel: V(0, 0, -6), skin: 'hielo' }).ball.vel.length();
  T('23 Hielo: el CANTO PERDONA (mejor ratio que clásica)', rHi > rCl, `hielo ${f2(rHi)} vs clásica ${f2(rCl)}`);
  // 24 · HIELO: el centro pega más suave
  const hiC = blockSpeed('hielo');
  T('24 Hielo DEFENSIVA: centro más suave (−8 % ±)', hiC < cl * 0.97, `${cl} → ${hiC} m/s`);
  // 25 · ORO = POTENCIA
  const or_ = blockSpeed('oro');
  T('25 Oro GOLPEA MÁS FUERTE (≥ +5 %)', or_ >= cl * 1.05, `${cl} → ${or_} m/s`);
  // 26 · ARCOÍRIS = EFECTO (+22 %)
  const spCl = Math.abs(brushSpin('clasica')), spAr = Math.abs(brushSpin('arcoiris'));
  T('26 Arcoíris IMPRIME MÁS EFECTO (≥ +15 %)', spAr >= spCl * 1.15, `${f1(spCl)} → ${f1(spAr)} rad/s`);
  // 27 · ARCOÍRIS arrastra más en el brush
  const vyCl = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), skin: 'clasica' }).ball.vel.y;
  const vyAr = hit({ ballVel: V(0, 0, -6), padVel: V(0, 3, 0), skin: 'arcoiris' }).ball.vel.y;
  T('27 La goma holo ARRASTRA más (vy del brush)', vyAr > vyCl, `vy ${f2(vyCl)} → ${f2(vyAr)} m/s`);
  // 27b · PRO CARBON: cara A giro / cara B dura — selección por CARA
  const pA = R.paddlePerkFor('player', 1), pB = R.paddlePerkFor('player', -1);
  R.setSkin('carbon');
  const pA2 = R.paddlePerkFor('player', 1), pB2 = R.paddlePerkFor('player', -1);
  T('27b Carbon DOBLE GOMA: cara A giro (1,20) · cara B dura (1,18 potencia)',
    pA2.spin === 1.20 && pA2.power === 1.00 && pB2.spin === 0.92 && pB2.power === 1.18,
    `A spin ${pA2.spin}/pow ${pA2.power} · B spin ${pB2.spin}/pow ${pB2.power}`);
}

console.log(`\n${ok + fails} pruebas ejecutadas`);
if (fails === 0) console.log(`🎉 ${ok}/${ok} pruebas OK — física v3.0.5 verificada`);
else { console.log(`💥 ${fails} FALLOS de ${ok + fails}`); process.exit(1); }
