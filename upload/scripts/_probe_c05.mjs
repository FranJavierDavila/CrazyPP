#!/usr/bin/env node
/* sonda rápida de c05 (scratch r57): confirma que el golden captura física real */
globalThis.window = globalThis.window || globalThis;
const m5 = await import(new URL('../src/game/core/c05_colisiones_ia_golpeo.js', import.meta.url).pathname);
const m2 = await import(new URL('../src/game/core/c02_cfg_escena.js', import.meta.url).pathname);
const THREE = await import('three');
const { stepPhysics, predictStrike } = m5;
const DIMS = m2.DIMS;
const V = THREE.Vector3;

const b = { pos: new V(0.1, 0.6, DIMS.tableCenterZ - 0.5), vel: new V(0.3, -2.5, -1.5), spin: new V(-40, 0, 0), __ppRestIdx: -1 };
const ev = [];
for (let f = 0; f < 90; f++) stepPhysics(1 / 60, b, [], ev);
console.log('eventos boteTopspin:', JSON.stringify(ev.map(e => e.type)));
console.log('vel tras botes:', b.vel.toArray().map(n => +n.toFixed(3)).join(','));

const C = DIMS.tableCenterZ;
const bi = { pos: new V(0.1, 1.0, C - 0.8), vel: new V(0.2, -1.2, -3.0), spin: new V(-30, 0, 0) };
const r = predictStrike(bi, -1, true);
console.log('predictStrike:', r ? ('punto y=' + r.point.y.toFixed(3) + ' z=' + r.point.z.toFixed(3) + ' t=' + r.t.toFixed(3) + ' urgent=' + r.urgent) : 'null');
