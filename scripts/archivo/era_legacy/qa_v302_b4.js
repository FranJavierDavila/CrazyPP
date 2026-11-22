// QA V3.0.2 · bloque 4: despeje del PRIMER cruce tras cada feed + jueces t4a/t4b
(() => {
  const Q = window.__QA, T = Q.T, G = Q.G, D = Q.D, TT = Q.TT;
  const NET = 0.9125, C = -1.6, HL = 1.37;
  Q.results.length = 0; Q.err = null; Q.done = false;

  let origRender = null, origLoop = null;
  function engineOn() {
    origRender = G.renderer.render;
    G.renderer.render = function () {};
    try { origLoop = G.renderer.getAnimationLoop(); } catch (e) { origLoop = null; }
    G.renderer.setAnimationLoop(null);
  }
  function engineOff() {
    G.renderer.render = origRender;
    if (origLoop) G.renderer.setAnimationLoop(origLoop);
    else G.renderer.setAnimationLoop(G.animate);
  }
  function steps(n, onFrame) {
    for (let i = 0; i < n; i++) {
      const now = (G.lastTime + 1 / 240) * 1000;
      G.animate(now);
      if (onFrame) onFrame(G, (G.events || []), i);
    }
  }

  Q.run = (async () => {
    // ===== A · primer cruce de red tras cada feed (6 modos con máquina) =====
    for (const id of ['t1a', 't1b', 't2a', 't2b', 't3a', 't3b']) {
      T.startMode(G, id);
      engineOn();
      let firstCross = null, allFirst = [], netEvents = 0, lastBallPos = null, violations = 0;
      let prevZ = null, prevY = null;
      TT.modeFeed();
      steps(1200, (g, evs) => {
        for (const e of evs) if (e.type === 'net') netEvents++;
        const p = g.ball.pos, v = g.ball.vel;
        // nuevo feed = salto a la zona de la máquina → reset del primer cruce
        if (prevZ !== null && Math.hypot(p.x - (lastBallPos ? lastBallPos[0] : 99),
            p.y - (lastBallPos ? lastBallPos[1] : 99), p.z - (lastBallPos ? lastBallPos[2] : 99)) > 0.35
            && p.z < -3.0) {
          if (firstCross !== null) allFirst.push(firstCross);
          firstCross = null;
        }
        if (prevZ !== null && (prevZ - C) * (p.z - C) < 0 && v.z > 0 && Math.abs(p.x) < 0.90) {
          const k = (C - prevZ) / (p.z - prevZ);
          const y = prevY + (p.y - prevY) * k;
          if (y > NET + 0.005) { if (firstCross === null) firstCross = y; }
          else if (y > 0.78) violations++;   // por ENCIMA de la mesa y bajo la cinta: tocaría red
        }
        prevZ = p.z; prevY = p.y; lastBallPos = [p.x, p.y, p.z];
      });
      if (firstCross !== null) allFirst.push(firstCross);
      engineOff();
      const minY = allFirst.length ? Math.min(...allFirst) : null;
      Q.log(id + ' · feeds sobre la cinta, jamás la tocan',
        allFirst.length >= 2 && minY > NET + 0.005 && netEvents === 0,
        'feedsSobreCinta=' + allFirst.length + ' yMin=' + (minY === null ? '—' : minY.toFixed(3)) +
        ' (post-bote junto al poste: ' + violations + ', informativo) netEvents=' + netEvents);
      T.stopMode(G);
    }

    // ===== B · jueces t4a (zona) y t4b (semántica) =====
    T.startMode(G, 't4a');
    D.st.live = true; D.st.shotRec = true; D.st.aiBounce = 0; D.st.streak = 0;
    TT.judgeAiBounce({ x: 0.2, y: 0.76, z: C - 1.2, clone() { return this; } });
    const s0 = D.st.streak, tOut = D.st.toast;
    TT.judgeAiBounce({ x: 0.2, y: 0.76, z: C - 0.30, clone() { return this; } });
    const b1 = D.st.aiBounce;
    TT.judgeAiBounce({ x: -0.15, y: 0.76, z: C - 0.10, clone() { return this; } });
    Q.log('t4a · el juez exige la zona pintada',
      s0 === 0 && /largo/i.test(tOut) && b1 === 1 && D.st.streak === 1,
      'fuera→"' + tOut.slice(0, 14) + '" · dentro×2→streak=' + D.st.streak);
    T.stopMode(G);

    T.startMode(G, 't4b');
    D.st.live = true; D.st.shotRec = true; D.st.streak = 0;
    TT.judgeAiBounce({ x: 0, y: 0.76, z: C - 0.7, clone() { return this; } });
    const toastCorta = D.st.toast;
    TT.judgeAiBounce({ x: 0, y: 0.76, z: C - HL + 0.07, clone() { return this; } });
    Q.log('t4b · «corta» si no llega al fondo; el fondo puntúa',
      /corta/i.test(toastCorta) && D.st.streak === 1,
      'toast="' + toastCorta.slice(0, 16) + '" streak=' + D.st.streak);
    T.stopMode(G);

    // ===== C · t5a: el beat cierra el rally si no se devuelve =====
    T.startMode(G, 't5a');
    engineOn();
    G.ball.pos.set(0, 0.01, 2.5); G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
    D.st.live = true; D.st.aiTouched = false; D.st.feedT = 1.7; D.st.rally = 3;
    let passedMachine = false;
    steps(700, (g) => { if (g.ball.pos.z < -3.0) passedMachine = true; });
    const r0 = D.st.rally;
    Q.log('t5a · fallo sin devolución cierra el rally y realimenta',
      r0 === 0 && passedMachine,
      'rally=' + r0 + ' · pasóPorMáquina=' + passedMachine + ' · bola z=' + G.ball.pos.z.toFixed(2));
    engineOff();
    T.stopMode(G);
  })().then(() => { Q.done = true; })
      .catch(e => { Q.done = true; Q.err = String(e && e.stack || e); });
  return 'lanzado';
})()
