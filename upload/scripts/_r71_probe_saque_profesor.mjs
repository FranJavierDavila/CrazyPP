// r71 · SONDA EMPÍRICA del saque del profesor (academia, tickDemoSaque)
// 1) REPRODUCE el bug: con la palma ACTUAL (bola 17 cm DETRÁS del borde de
//    la mesa, a la ALTURA de la mesa) el solver nunca encuentra un saque
//    con bote propio -> cae al FALLBACK (lob directo a nuestro campo:
//    UN solo bote). Eso es exactamente lo que ve el dueño.
// 2) BUSCA la posición de la bola-para-el-golpe que hace que el solver
//    devuelta SIEMPRE un saque reglamentario (bote propio profundo en SU
//    campo + bote en el nuestro), con margen cómodo.
// Uso: node scripts/_r71_probe_saque_profesor.mjs
globalThis.window = globalThis;
globalThis.document = { createElement: () => ({ getContext: () => null }), addEventListener() {}, documentElement: {} };
globalThis.localStorage = { getItem: () => null, setItem: () => {}, removeItem: () => {} };
const { findServeVelocity, simulateServePath } = await import('../src/game/core/c05_colisiones_ia_golpeo.js');
const { DIMS } = await import('../src/game/core/c02_cfg_escena.js');

const C = DIMS.tableCenterZ, HL = DIMS.tableHalfLength, TY = DIMS.tableTopY;
const R = DIMS.ballRadius;
const { Vector3 } = await import('three');
const V3 = (x, y, z) => new Vector3(x, y, z);

function probe(from, runs = 200, etiqueta = '') {
  let okN = 0, ownMin = -1e9, oppMin = 1e9, netMin = 1e9;
  let ownDeep = -1e9; // el bote propio más CERCANO a la red (queremos MARGEN)
  for (let i = 0; i < runs; i++) {
    const { v, spin } = findServeVelocity(from, -1, { x: -0.05, spd: 1.22 });
    const sim = simulateServePath(from, v, spin, -1);
    if (sim.ok && sim.ownBounce && sim.oppBounce) {
      okN++;
      ownDeep = Math.max(ownDeep, Math.abs(sim.ownZ ?? sim.oppZ)); // aprox
      if (sim.oppZ !== undefined) oppMin = Math.min(oppMin, Math.abs(sim.oppZ - C));
      if (sim.netY !== null && sim.netY !== undefined) {
        netMin = Math.min(netMin, sim.netY - (DIMS.netTopY + R));
      }
    }
  }
  const pct = Math.round((100 * okN) / runs);
  console.log(`${etiqueta} -> saque reglamentario ${pct}% (${okN}/${runs})` +
    (netMin < 1e8 ? ` · margen red mín ${Math.round(netMin * 1000)} mm` : ''));
  return pct;
}

console.log('DIMS: C=' + C + ' HL=' + HL + ' TY=' + TY +
  ' · mesa z∈[' + (C - HL) + ',' + (C + HL) + '] · red arriba=' + DIMS.netTopY);

// ---------- 1 · REPRODUCCIÓN del bug con la palma ACTUAL ----------
const palmaActual = V3(0.10, TY + R + 0.004, C - HL - 0.17);
probe(palmaActual, 200, 'PALMA ACTUAL (0.10, TY+r+4mm, C-HL-17cm)');

// el fallback: ¿dónde botaría? simulamos el fallback directo
{
  const from = palmaActual;
  const { v, spin } = findServeVelocity(from, -1, { x: -0.05, spd: 1.22 });
  const sim = simulateServePath(from, v, spin, -1);
  console.log('  diagnóstico palma actual: ok=' + sim.ok +
    ' ownBounce=' + sim.ownBounce + ' oppBounce=' + sim.oppBounce +
    (sim.oppZ !== undefined ? ' · bote rival z=' + sim.oppZ.toFixed(3) : ''));
}

// ---------- 2 · CANDIDATOS de palma (sobre la mesa y ELEVADA) ----------
// La bola debe estar DENTRO del rango z de la mesa (para que el arco pueda
// botar en SU campo) y ELEVADA (para que el golpeador llegue con un arco
// natural y el solver tenga recorrido). Barrido acotado:
for (const dz of [-0.16, -0.10, 0.06]) {
  for (const dy of [0.18, 0.26, 0.34]) {           // altura sobre la mesa
    const p = V3(0.10, TY + dy, C - HL + dz);
    const pct = probe(p, 30, `palma z=C-HL${dz >= 0 ? '+' : ''}${dz} y=TY+${dy}`);
    if (pct >= 97) console.log('   ^^^ CANDIDATO FUERTE');
  }
}
