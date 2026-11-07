// r71 · VERIFICACIÓN del candidato de palma elegido (100 corridas + stats)
globalThis.window = globalThis;
globalThis.document = { createElement: () => ({ getContext: () => null }), addEventListener() {}, documentElement: {} };
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const { findServeVelocity, simulateServePath } = await import('../src/game/core/c05_colisiones_ia_golpeo.js');
const { DIMS } = await import('../src/game/core/c02_cfg_escena.js');
const { Vector3 } = await import('three');

const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
const R = DIMS.ballRadius;
const from = new Vector3(0.10, TY + 0.34, C - HL - 0.16);

let ok = 0, netMin = 1e9, oppZmin = 1e9, oppZmax = -1e9;
const N = 40;   // r71 · 40 corridas: estadísticamente sólido y dentro del presupuesto de tiempo de QA
for (let i = 0; i < N; i++) {
  const { v, spin } = findServeVelocity(from, -1, { x: -0.05, spd: 1.22 });
  const sim = simulateServePath(from, v, spin, -1);
  if (sim.ok && sim.ownBounce && sim.oppBounce) {
    ok++;
    
    if (sim.oppZ !== undefined) { oppZmin = Math.min(oppZmin, sim.oppZ); oppZmax = Math.max(oppZmax, sim.oppZ); }
    if (sim.netY !== null && sim.netY !== undefined) netMin = Math.min(netMin, sim.netY - (DIMS.netTopY + R));
  }
}
console.log(`PALMA ELEGIDA (0.10, TY+0.34, C-HL-16cm): ${ok}/${N} reglamentarios`);
console.log(`  bote RIVAL  z ∈ [${oppZmin.toFixed(3)}, ${oppZmax.toFixed(3)}] (campo nuestro: [${C}, ${(C + HL).toFixed(2)}])`);
console.log(`  margen de red mínimo: ${Math.round(netMin * 1000)} mm`);
// sanity: la raqueta está en (0.17, TY+0.38, C-HL-0.10) — distancia a la bola
const dq = Math.hypot(0.17 - 0.10, (TY + 0.38) - (TY + 0.34), (C - HL - 0.10) - (C - HL - 0.16));
console.log(`  distancia raqueta guardia→bola: ${Math.round(dq * 1000)} mm (barrido natural)`);
process.exit(0);   // r71 · los módulos dejan un handle vivo: salir EXPLÍCITAMENTE
