// QA V3.0.2 · bloque determinista: física a 240 Hz con render en no-op.
// (El headless va a <10 fps y el sampler por frames no resuelve trayectorias.)
(() => {
  const Q = window.__QA, T = Q.T, G = Q.G, D = Q.D, TT = Q.TT;
  const NET = 0.9125, C = -1.6, HL = 1.37;
  Q.results.length = 0; Q.err = null; Q.done = false;

  // --- motor de pasos determinista ---
  let origRender = null, origLoop = null;
  function engineOn() {
    origRender = G.renderer.render;
    G.renderer.render = function () {};            // sin pintar: pura física
    try { origLoop = G.renderer.getAnimationLoop(); } catch (e) { origLoop = null; }
    G.renderer.setAnimationLoop(null);             // el bucle rAF deja de pisar
  }
  function engineOff() {
    G.renderer.render = origRender;
    if (origLoop) G.renderer.setAnimationLoop(origLoop);
    else G.renderer.setAnimationLoop(G.animate);
  }
  // pasa n pasos de 1/240 s
  function steps(n, onFrame) {
    for (let i = 0; i < n; i++) {
      const now = (G.lastTime + 1 / 240) * 1000;
      G.animate(now);
      if (onFrame) onFrame(G, (G.events || []), i);
    }
  }

  Q.run = (async () => {
    // ================= A · despeje de red en los 6 modos =================
    for (const id of ['t1a', 't1b', 't2a', 't2b', 't3a', 't3b']) {
      T.startMode(G, id);
      engineOn();
      const crossings = []; let netEvents = 0, playerBounce = 0;
      let prevZ = null, prevY = null;
      TT.modeFeed();
      steps(900, (g, evs) => {
        for (const e of evs) {
          if (e.type === 'net') netEvents++;
          if (e.type === 'table' && e.side === 'player') playerBounce++;
        }
        const p = g.ball.pos, v = g.ball.vel;
        if (prevZ !== null && (prevZ - C) * (p.z - C) < 0 && v.z > 0 && Math.abs(p.x) < 0.92) {
          const k = (C - prevZ) / (p.z - prevZ);
          crossings.push(prevY + (p.y - prevY) * k);
        }
        prevZ = p.z; prevY = p.y;
      });
      engineOff();
      const minY = crossings.length ? Math.min(...crossings) : null;
      Q.log(id + ' · feed despeja la red (240 Hz)',
        crossings.length > 0 && minY > NET + 0.005 && netEvents === 0 && playerBounce > 0,
        'cruces=' + crossings.length + ' yMin=' + (minY === null ? '—' : minY.toFixed(3)) +
        ' netEvents=' + netEvents + ' boteJugador=' + playerBounce);
      T.stopMode(G);
    }

    // ================= B · metrónomo end-to-end =================
    T.startMode(G, 't5a');
    engineOn();
    const rallySnap = []; let steals = 0, feeds = 1, returned = false;
    let prev = { x: null, y: null, z: null, live: false, aiT: false };
    TT.modeFeed();
    steps(14 * 240, (g, evs) => {
      const p = g.ball.pos, v = g.ball.vel, s = D.st;
      if (prev.x !== null) {
        const jump = Math.hypot(p.x - prev.x, p.y - prev.y, p.z - prev.z);
        if (jump > 0.35) {
          const prevSettled = (prev.z > C + HL + 0.4) || prev.y < 0.06 ||
            (Math.abs(prev.x) < 0.81 && Math.abs(prev.z - C) < HL + 0.05 && prev.y < 0.83);
          if (prev.live && !prev.aiT && !prevSettled) steals++;
          if (p.z < -3.0) feeds++;
        }
      }
      // devolución del jugador EMULADA (bloqueo: la bola llega a su campo)
      if (!returned && s.live && p.z > C + 0.55 && p.y < 1.15 && v.z > 0) {
        g.ball.vel.set((Math.random() - 0.5) * 0.3, 2.25, -3.45);
        g.ball.spin.set(0, 0, 0);
        s.live = true; s.shotRec = true; s.aiTouched = false;   // como el evento de pala
        returned = true;
      }
      for (const e of evs) {
        if (e.type === 'table' && e.side === 'ai' && s.aiTouched) {
          rallySnap.push(s.rally); returned = false;
        }
      }
      prev = { x: p.x, y: p.y, z: p.z, live: s.live, aiT: s.aiTouched };
    });
    engineOff();
    Q.log('t5a · el beat NO roba bolas en vuelo', steals === 0, 'robos=' + steals);
    Q.log('t5a · el metrónomo alimenta con ritmo', feeds >= 5, 'feeds=' + feeds + ' en 14 s de juego');
    Q.log('t5a · las devoluciones SUMAN al rally', rallySnap.length > 0 && Math.max(...rallySnap) >= 3,
      'rally final=' + D.st.rally + ' snapshot=' + JSON.stringify(rallySnap.slice(-6)));
    T.stopMode(G);
  })().then(() => { Q.done = true; })
      .catch(e => { Q.done = true; Q.err = String(e && e.stack || e); });
  return 'lanzado';
})()
