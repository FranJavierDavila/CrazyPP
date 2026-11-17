#!/usr/bin/env node
/**
 * DIAGNÓSTICO DEL SAQUE · v3.0.5-FIS1
 * Simula el saque completo del JUGADOR con las funciones REALES de game.html:
 * toss asistido (vy 3.1) → vuelo libre → contacto pala (collidePaddle) →
 * validación sección 5 (simulateServePath + findServeVelocity) → vuelo real
 * (colisiones mesa/red/mundo) → clasificación del resultado.
 * Compara FIS1 (physicsRealism=1) contra legacy (=0).
 *   node scripts/diag_saque_v305.mjs
 */
import { readFileSync } from 'node:fs';

const SRC = readFileSync(new URL('../public/game.html', import.meta.url), 'utf8');

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

const vecs = [...SRC.matchAll(/^const (\w+) = new THREE\.Vector3\(\);$/gm)].map(m => m[0]).join('\n');
const pStart = SRC.indexOf('const PADDLE_PERKS = {');
const ppfI = SRC.indexOf('function paddlePerkFor(');
const ppfEnd = (() => { let d = 0; const dd = SRC.indexOf('{', ppfI);
  for (let j = dd; j < SRC.length; j++) {
    if (SRC[j] === '{') d++; else if (SRC[j] === '}') { d--; if (d === 0) return j + 1; } } })();
const perksBlock = SRC.slice(pStart, ppfEnd);

const CODE = [
  extractConstObj('DIMS'), vecs, perksBlock,
  extractFn('applyAerodynamics'), extractFn('applyBounceSpin'), extractFn('bounceOnTable'),
  extractFn('collidePaddle'), extractFn('collideTable'), extractFn('collideNet'), extractFn('collideWorld'),
  extractFn('computeShotVelocity'), extractFn('simulateBounceUntilTable'),
  extractFn('computeShotVelocityReal'), extractFn('findServeVelocity'), extractFn('simulateServePath'),
  `return { DIMS, tmpPrev, applyAerodynamics, applyBounceSpin, bounceOnTable, collidePaddle,
    collideTable, collideNet, collideWorld, computeShotVelocity, simulateBounceUntilTable,
    computeShotVelocityReal, findServeVelocity, simulateServePath,
    paddlePerkFor, PADDLE_PERKS, setSkin: __ppSetPaddleSkin };`,
].join('\n');

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
  lerpVectors(a, b, t) { this.x = a.x + (b.x - a.x) * t; this.y = a.y + (b.y - a.y) * t; this.z = a.z + (b.z - a.z) * t; return this; }
  normalize() { const l = this.length(); return l ? this.multiplyScalar(1 / l) : this; }
  setLength(l) { return this.normalize().multiplyScalar(l); }
  lerp(v, a) { this.x += (v.x - this.x) * a; this.y += (v.y - this.y) * a; this.z += (v.z - this.z) * a; return this; }
  negate() { return this.multiplyScalar(-1); }
}
const THREE = { Vector3: V3, MathUtils: { clamp: (v, a, b) => Math.min(b, Math.max(a, v)) } };

const R = new Function('THREE', `const localStorage = { getItem: () => null }; const window = {};
  ${CODE}`)(THREE);
const { DIMS } = R;
const V = (x, y, z) => new V3(x, y, z);
const rnd = (a, b) => a + Math.random() * (b - a);

/* ── vuelo físico real (como stepPhysics: sub-pasos 1/480) ─────────── */
function fly(ball, maxT = 3.5) {
  const h = 1 / 480;
  let t = 0, ownBounce = 0, oppBounce = 0, netEvents = 0, floor = false;
  const ev = [];
  while (t < maxT) {
    R.tmpPrev.copy(ball.pos);
    const prevY = ball.pos.y, prevZ = ball.pos.z;
    ball.vel.y += DIMS.gravity * h;
    R.applyAerodynamics(ball.vel, ball.spin, h);
    ball.pos.addScaledVector(ball.vel, h);
    const n0 = ev.length;
    R.collideTable(ball, prevY, ev);
    R.collideNet(ball, prevZ, ev);
    R.collideWorld(ball, ev);
    for (let i = n0; i < ev.length; i++) {
      const e = ev[i];
      if (e.type === 'table') { if (e.side === 'player') ownBounce++; else oppBounce++; }
      else if (e.type === 'net') netEvents++;
      else if (e.type === 'floor') floor = true;
    }
    if (floor) break;
    if (oppBounce >= 1 && ownBounce >= 1) {
      // seguir un poco para ver el 2.º bote rival
      if (oppBounce >= 2) break;
    }
    t += h;
  }
  return { ownBounce, oppBounce, netEvents, floor, ev };
}

/* ── un saque completo del jugador ─────────────────────────────────── */
const MODE_ASSIST = process.env.ASSIST === 'nuevo' ? 'nuevo' : 'antiguo';
function playerServe({ fis = 1, swingPow = 1, contact = 'center' }) {
  DIMS.physicsRealism = fis;
  // 1) toss asistido desde la mano libre (vy = serveAssistVy)
  const hand = V(rnd(-0.05, 0.35), 1.13, rnd(0.05, 0.45));   // bola apoyada (mano + lift 8 cm)
  const ball = { pos: hand.clone(), vel: V(rnd(-0.1, 0.1), DIMS.serveAssistVy, rnd(-0.25, -0.05)), spin: V(), ignoreTable: false };
  // vuelo libre hasta la altura de golpeo (1.24-1.42 m, bola cayendo)
  let hitY = rnd(1.24, 1.42);
  const h = 1 / 480;
  let t = 0;
  while (ball.pos.y > hitY || ball.vel.y > 0) {
    ball.vel.y += DIMS.gravity * h;
    R.applyAerodynamics(ball.vel, ball.spin, h);
    ball.pos.addScaledVector(ball.vel, h);
    t += h;
    if (t > 2) return { cls: 'no-hit', note: 'toss no alcanzado' };
  }
  const hitPos = ball.pos.clone();
  if (hitPos.z < DIMS.tableCenterZ + DIMS.tableHalfLength - DIMS.serveEndLineTol) {
    return { cls: 'rechazado-behind', z: hitPos.z };
  }
  // 2) contacto: pala bajo la bola, cara abierta, swing adelante-arriba
  const theta = rnd(0.15, 0.55);                      // apertura de cara (9°-31°)
  const n = V(0, Math.sin(theta), Math.cos(theta));
  const up = V(0, Math.cos(theta), -Math.sin(theta));
  const right = V(1, 0, 0);
  const padVel = V(rnd(-0.4, 0.4), rnd(0.7, 2.0) * swingPow, -rnd(2.4, 4.6) * swingPow);
  const grip = hitPos.clone().addScaledVector(up, -0.14).addScaledVector(n, 0.005);
  if (contact === 'edge') grip.addScaledVector(right, rnd(0.05, 0.08));
  const pad = {
    prev: grip.clone(), pos: grip.clone(),
    prevNormal: n.clone(), normal: n.clone(),
    prevRight: right.clone(), right: right.clone(),
    prevUp: up.clone(), up: up.clone(),
    vel: padVel, omega: V(0, 0, rnd(-2, 2)),
    who: 'player', index: 1, extraReach: DIMS.serveExtraReach, cooldown: 0,
  };
  R.tmpPrev.copy(ball.pos).addScaledVector(n, 0.045);
  ball.pos.addScaledVector(n, -0.012);
  const ev = [];
  R.collidePaddle(ball, pad, 0.5, ev);
  if (!ev.length) return { cls: 'no-contact' };
  const rawVel = ball.vel.clone(), rawSpin = ball.spin.clone();
  // 3) sección 5: validación + asistencia
  const sim1 = R.simulateServePath(ball.pos, ball.vel, ball.spin, 1);
  let stage = 'jugador-100%';
  if (!sim1.ok) {
    if (sim1.netTouch) failReason.net = (failReason.net || 0) + 1;
    else if (sim1.ownBounce && !sim1.oppBounce) failReason.sinBoteRival = (failReason.sinBoteRival || 0) + 1;
    else if (!sim1.ownBounce) failReason.sinBotePropio = (failReason.sinBotePropio || 0) + 1;
    else failReason.otro = (failReason.otro || 0) + 1;
    if (MODE_ASSIST === 'nuevo') {
      // v3.0.6-SRV1 · cascada suave + hint del swing + roce de red conservado
      const fix = R.findServeVelocity(ball.pos, 1, {
        x: ball.pos.x * 0.35 + pad.vel.x * 0.22,
        spd: pad.vel.length(),
      });
      if (sim1.ownBounce && sim1.oppBounce) {
        ball.vel.y += 0.35;                             // LET conservado
      } else {
        ball.vel.lerp(fix.v, 0.45); ball.spin.lerp(fix.spin, 0.35);
        if (!R.simulateServePath(ball.pos, ball.vel, ball.spin, 1).ok) {
          ball.vel.lerp(fix.v, 0.75); ball.spin.lerp(fix.spin, 0.6);
          if (!R.simulateServePath(ball.pos, ball.vel, ball.spin, 1).ok) {
            ball.vel.copy(fix.v); ball.spin.copy(fix.spin); stage = 'solver-100%';
          } else stage = 'mezcla-75%';
        } else stage = 'mezcla-45%';
      }
    } else {
      // v2.x/v3.0.5 · 65 % → solver total
      const fix = R.findServeVelocity(ball.pos, 1);
      ball.vel.lerp(fix.v, 0.65); ball.spin.lerp(fix.spin, 0.5);
      const sim2 = R.simulateServePath(ball.pos, ball.vel, ball.spin, 1);
      if (!sim2.ok) { ball.vel.copy(fix.v); ball.spin.copy(fix.spin); stage = 'solver-100%'; }
      else stage = 'mezcla-65%';
    }
  }
  if (ball.vel.length() < 3.2) ball.vel.setLength(3.2);
  if (ball.vel.length() > 8.8) ball.vel.setLength(8.8);
  const finalSpeed = ball.vel.length();
  // 4) vuelo real
  const res = fly(ball);
  let cls;
  if (res.ownBounce >= 1 && res.oppBounce >= 1) cls = 'VALIDO';
  else if (res.netEvents > 0 && res.ownBounce >= 1) cls = 'red/let';
  else if (res.floor) cls = 'fuera/suelo';
  else if (res.ownBounce >= 2) cls = 'doble-propio';
  else cls = 'otro';
  return { cls, stage, rawSim: sim1, finalSpeed, ownBounce: res.ownBounce, oppBounce: res.oppBounce,
           netEvents: res.netEvents, hitZ: +hitPos.z.toFixed(2), rawSpeed: +rawVel.length().toFixed(2),
           rawVy: +rawVel.y.toFixed(2), rawVz: +rawVel.z.toFixed(2) };
}

/* ── monte carlo ───────────────────────────────────────────────────── */
let failReason = {};
function sweep(label, fis, swingPow) {
  const N = 300;
  const acc = { VALIDO: 0, 'red/let': 0, 'fuera/suelo': 0, 'doble-propio': 0, otro: 0, 'no-contact': 0 };
  const stages = { 'jugador-100%': 0, mezcla: 0, 'solver-100%': 0 };
  const speeds = [];
  failReason = {};
  for (let i = 0; i < N; i++) {
    const contact = Math.random() < 0.15 ? 'edge' : 'center';
    const r = playerServe({ fis, swingPow, contact });
    if (r.cls === 'no-hit' || r.cls === 'rechazado-behind') { acc.otro++; continue; }
    acc[r.cls] = (acc[r.cls] || 0) + 1;
    if (stages[r.stage] !== undefined) stages[r.stage]++;
    else if (r.stage && r.stage.startsWith('mezcla')) stages.mezcla++;
    if (r.finalSpeed) speeds.push(r.finalSpeed);
  }
  const pct = (n) => (100 * n / N).toFixed(0) + '%';
  const avg = speeds.length ? (speeds.reduce((a, b) => a + b, 0) / speeds.length).toFixed(1) : '—';
  console.log(`\n== ${label} (swing ×${swingPow}) ==`);
  console.log(`  VÁLIDOS ${pct(acc.VALIDO)} · red/let ${pct(acc['red/let'])} · fuera ${pct(acc['fuera/suelo'])} · otro ${pct(acc.otro)}`);
  console.log(`  trayectoria: del jugador ${pct(stages['jugador-100%'])} · mezcla ${pct(stages.mezcla)} · solver total ${pct(stages['solver-100%'])}`);
  const fr = Object.entries(failReason).map(([k, v]) => `${k} ${pct(v)}`).join(' · ') || '—';
  console.log(`  fallo del tiro propio: ${fr}`);
  console.log(`  velocidad final media ${avg} m/s`);
}

console.log('DIAGNÓSTICO SAQUE · funciones reales de game.html (N=300 por config)');
sweep('LEGACY (pre-FIS1, physicsRealism=0)', 0, 1.0);
sweep('FIS1 swing natural', 1, 1.0);
sweep('FIS1 swing suave (miedo al fallo)', 1, 0.72);
sweep('FIS1 swing fuerte', 1, 1.25);

/* ── micro-test: el asistente del solver desde posiciones típicas ──── */
console.log('\n== findServeVelocity desde posiciones de golpeo típicas ==');
for (const p of [V(0.2, 1.38, 0.25), V(-0.15, 1.30, 0.05), V(0.3, 1.45, 0.40), V(0.0, 1.20, -0.10)]) {
  const f = R.findServeVelocity(p.clone(), 1);
  const res = R.simulateServePath(p, f.v, f.spin, 1);
  console.log(`  from (${p.x},${p.y},${p.z}) → |v| ${f.v.length().toFixed(1)} m/s ok=${res.ok} oppZ=${res.oppZ ? res.oppZ.toFixed(2) : '—'} netY=${res.netY ? res.netY.toFixed(2) : '—'}`);
}
