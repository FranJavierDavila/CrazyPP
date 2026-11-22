#!/usr/bin/env node
/* DEBUG r86 · escenario P0-3: scoop con pala viva — por qué no hay golpe */
import { fileURLToPath } from 'node:url';
import * as THREE from 'three';
globalThis.window = globalThis.window || globalThis;
const { c05, c04, DIMS } = await (async () => {
  const m5 = await import(fileURLToPath(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url)));
  const m4 = await import(fileURLToPath(new URL('../src/game/core/c04_fisica_ccd.js', import.meta.url)));
  const m2 = await import(fileURLToPath(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url)));
  return { c05: m5, c04: m4, DIMS: m2.DIMS };
})();
const C = DIMS.tableCenterZ;
console.log('DIMS hitAssistRadius', DIMS.hitAssistRadius, 'bladeRadius', DIMS.bladeRadius, 'bladeCenterUp', DIMS.bladeCenterUp);
function palaBase(who, index, x, y, z, vx = 0, vy = 0, vz = 0) {
  const p = c04.createPaddleSim(who, index);
  p.pos.set(x, y, z); p.prev.copy(p.pos); p.vel.set(vx, vy, vz);
  p.active = true; p.serveFlight = false; p.intercambio = false; p.extraReach = 0;
  console.log('pala basis default: normal', p.normal.toArray(), 'up', p.up.toArray(), 'right', p.right.toArray());
  return p;
}
const b = { pos: new THREE.Vector3(0, 1.10, C + 0.70), vel: new THREE.Vector3(0, -0.15, 0.2), spin: new THREE.Vector3(), __ppRestIdx: -1 };
const p = palaBase('player', 0, 0, 0.90, C + 0.72, 0, 0.8, 0);
const ev = [];
for (let f = 0; f < 20; f++) {
  const zFace = p.pos.z;   // plano de cara (normal (0,0,1))
  const dist = zFace - b.pos.z;   // + = la bola está detrás del plano (lado −z)
  c05.stepPhysics(1 / 60, b, [p], ev);
  console.log(`f${f} y=${b.pos.y.toFixed(3)} z=${b.pos.z.toFixed(3)} distCara=${dist.toFixed(3)} restIdx=${b.__ppRestIdx} ev=[${ev.map(e => e.type + ':' + (e.speed || 0).toFixed(2))}]`);
  ev.length = 0;
}
