// QA V3.0.2 · PRO TRAINING — las 9 pruebas, por la ruta real del módulo.
// Se ejecuta con agent-browser eval por bloques (el contexto es el de la página).
// Helpers colgados en window.__QA para persistir entre evals.
(() => {
  if (window.__QA) { window.__QA.results = []; }
  const T = window.__PP_TRAIN, G = window.__PP_GAME, D = T.__debug, TT = T.__test;
  const DIMS = G.dims || (G.core && G.core.dims) || null;
  const C = () => G.tableCenterZ !== undefined ? G.tableCenterZ : -1.6;
  window.__QA = {
    T, G, D, TT,
    results: [],
    // sampler de bola: graba pos/vel cada frame y detecta teleports
    startSample(ms) {
      const b = G.ball;
      const rec = { rows: [], teleports: [], netY: null, netTowardPlayer: 0, netHits: 0 };
      const prev = { x: null, y: null, z: null, vy: null, vlen: null, live: false, aiTouched: false };
      const C = -1.6, HL = 1.37;
      const settled = (x, y, z, vy, vlen) =>
        (y < 0.06 && Math.abs(vy) < 0.6) ||                       // reposo en suelo
        (Math.abs(x) < 0.81 && Math.abs(z - C) < HL + 0.05 && y < 0.825 && vlen < 0.45) || // reposo en mesa
        Math.abs(z - C) > HL + 1.5 || y < -0.4 || z > C + HL + 0.4;  // perdida / pasada
      const t0 = performance.now();
      function frame() {
        const t = performance.now() - t0;
        if (t > ms) { window.__QA.sample = rec; window.__QA.sampling = false; return; }
        const p = b.pos, v = b.vel;
        if (prev.x !== null) {
          const jump = Math.hypot(p.x - prev.x, p.y - prev.y, p.z - prev.z);
          if (jump > 0.35) {
            rec.teleports.push({ t, from: [prev.x, prev.y, prev.z], to: [p.x, p.y, p.z],
              prevLive: prev.live, prevAiTouched: prev.aiTouched,
              prevSettled: settled(prev.x, prev.y, prev.z, prev.vy, prev.vlen) });
          }
          // cruce de red hacia el jugador (vel.z > 0): registra la altura
          const nz = C;
          if ((prev.z - nz) * (p.z - nz) < 0 && v.z > 0) {
            const k = (nz - prev.z) / (p.z - prev.z);
            const yAtNet = prev.y + (p.y - prev.y) * k;
            rec.rows.push({ t, kind: 'cross', y: yAtNet });
            if (rec.netY === null || yAtNet < rec.netY) rec.netY = yAtNet;
            rec.netTowardPlayer++;
          }
          if ((prev.z - nz) * (p.z - nz) < 0 && v.z < 0) {
            const k = (nz - prev.z) / (p.z - prev.z);
            rec.rows.push({ t, kind: 'crossBack', y: prev.y + (p.y - prev.y) * k });
          }
        }
        prev.x = p.x; prev.y = p.y; prev.z = p.z;
        prev.vy = v.y; prev.vlen = v.length();
        prev.live = D.st.live; prev.aiTouched = D.st.aiTouched;
        requestAnimationFrame(frame);
      }
      window.__QA.sampling = true;
      requestAnimationFrame(frame);
      return 'sampling ' + ms + 'ms';
    },
    log(name, ok, info) {
      window.__QA.results.push({ name, ok, info });
      console.log((ok ? 'PASS' : 'FAIL') + ' · ' + name + ' · ' + info);
    },
  };
  return 'QA helpers listos · active=' + JSON.stringify(T.state.active) + ' · ball=' + !!G.ball;
})()
