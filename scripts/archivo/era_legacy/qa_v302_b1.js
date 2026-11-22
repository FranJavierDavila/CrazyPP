(() => {
// QA V3.0.2 · bloque 1: despeje de red de los 6 modos con máquina + t5a sin robos
window.__QA.run = (async () => {
  const Q = window.__QA, T = Q.T, G = Q.G, D = Q.D, TT = Q.TT;
  const NET = 0.9125, C = -1.6, HL = 1.37;
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const out = [];

  // --- t5a primero: 10 s de observación del beat ---
  T.startMode(G, 't5a');
  Q.startSample(26000);
  // deja que el módulo alimente solo (wait 0.9 inicial)
  await wait(27000);
  {
    const s = Q.sample;
    const illegal = s.teleports.filter(tp => {
      // el robo ILEGAL: la bola estaba VIVA y NO asentada justo antes del salto
      return tp.prevLive && !tp.prevAiTouched && !tp.prevSettled;
    });
    Q.log('t5a beat sin robar bola en vuelo', illegal.length === 0,
      'teleports=' + s.teleports.length + ' ilegales=' + illegal.length +
      (illegal.length ? ' · 1º t=' + illegal[0].t.toFixed(0) + 'ms' : ''));
    Q.log('t5a la máquina alimenta', s.teleports.length >= 3,
      'feeds en 26 s = ' + s.teleports.length);
  }
  T.stopMode(G);

  // --- despeje de red en los 6 modos con máquina ---
  for (const id of ['t1a', 't1b', 't2a', 't2b', 't3a', 't3b']) {
    T.startMode(G, id);
    Q.startSample(15000);
    await wait(15400);
    const s = Q.sample;
    const crosses = s.rows.filter(r => r.kind === 'cross');
    const minY = crosses.length ? Math.min(...crosses.map(r => r.y)) : null;
    const clears = crosses.length > 0 && minY > NET + 0.005;
    const netBack = s.rows.filter(r => r.kind === 'crossBack').length;
    Q.log(id + ' feed despeja la red', clears,
      'cruces=' + crosses.length + ' yMinRed=' + (minY === null ? 'null' : minY.toFixed(3)) +
      ' (netTop ' + NET + ') · vueltas=' + netBack);
    T.stopMode(G);
    await wait(250);
  }
  return JSON.stringify(Q.results, null, 1);
})().then(r => { window.__QA.done = true; window.__QA.err = null; })
  .catch(e => { window.__QA.done = true; window.__QA.err = String(e && e.stack || e); });

return "lanzado";
})()