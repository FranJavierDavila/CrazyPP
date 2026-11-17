// QA V3.0.2 · bloque 2: jueces de t5a/t4a/t4b por ruta directa + fallo del beat
(() => {
  window.__QA.results.length = 0;
  const Q = window.__QA, T = Q.T, G = Q.G, D = Q.D, TT = Q.TT;
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const C = -1.6, HL = 1.37;
  const pts0 = () => Q.T.state.pts;

  window.__QA.run = (async () => {
    // ---------- t5a · rally que SÍ cuenta ----------
    T.startMode(G, 't5a');
    await wait(300);
    D.st.live = true; D.st.shotRec = true; D.st.aiTouched = false; D.st.rally = 0;
    TT.judgeAiBounce({ x: 0.3, y: 0.76, z: -2.3, clone() { return this; } });
    const r1 = D.st.rally, a1 = D.st.aiTouched, p1 = T.state.pts;
    TT.judgeAiBounce({ x: 0.3, y: 0.76, z: -2.3, clone() { return this; } });   // rebote extra: NO suma
    Q.log('t5a el rally cuenta (y sin dobles)', r1 === 1 && a1 === true && D.st.rally === 1 && p1 >= 1,
      'rally=' + r1 + ' aiTouched=' + a1 + ' trasRebote=' + D.st.rally + ' pts=+' + (p1 - pts0() + 1));
    // hito a 30
    D.st.rally = 29;
    TT.judgeAiBounce({ x: -0.3, y: 0.76, z: -2.5, clone() { return this; } });
    Q.log('t5a hito 30 = bonus +15', D.st.rally === 30 && T.state.pts >= p1 + 15,
      'rally=' + D.st.rally + ' best=' + (T.state.best.t5a || 0) + ' pts=' + T.state.pts);

    // ---------- t5a · el beat cierra el rally si no se devuelve ----------
    G.ball.pos.set(0, 0.01, 2.5); G.ball.vel.set(0, 0, 0); G.ball.spin.set(0, 0, 0);
    D.st.live = true; D.st.aiTouched = false; D.st.feedT = 1.7; D.st.rally = 3;
    await wait(700);
    Q.log('t5a fallo sin devolución cierra el rally', D.st.rally === 0,
      'rally=' + D.st.rally + ' toast="' + (D.st.toast || '').slice(0, 28) + '"');
    await wait(1200);
    Q.log('t5a tras el fallo vuelve a alimentar', G.ball.pos.z < -3.0,
      'bola z=' + G.ball.pos.z.toFixed(2) + ' (máquina ~-3.27) live=' + D.st.live);
    T.stopMode(G);
    await wait(300);

    // ---------- t4a · el juez exige la zona pintada ----------
    T.startMode(G, 't4a');
    await wait(300);
    D.st.live = true; D.st.shotRec = true; D.st.aiBounce = 0; D.st.streak = 0;
    TT.judgeAiBounce({ x: 0.2, y: 0.76, z: C - 1.2, clone() { return this; } });   // fuera (larga)
    const s0 = D.st.streak, t0 = D.st.toast;
    TT.judgeAiBounce({ x: 0.2, y: 0.76, z: C - 0.30, clone() { return this; } });  // dentro 1
    const b1 = D.st.aiBounce;
    TT.judgeAiBounce({ x: -0.15, y: 0.76, z: C - 0.10, clone() { return this; } }); // dentro 2 → ok
    Q.log('t4a zona exigida y doble bote puntúa', s0 === 0 && b1 === 1 && D.st.streak === 1,
      'fuera→streak=' + s0 + ' ("' + t0.slice(0, 16) + '") · dentro×2→streak=' + D.st.streak + ' pts=+' + (T.state.pts - pts0() + 3));
    T.stopMode(G);
    await wait(300);

    // ---------- t4b · fallo semántico correcto ----------
    T.startMode(G, 't4b');
    await wait(300);
    D.st.live = true; D.st.shotRec = true; D.st.streak = 0;
    TT.judgeAiBounce({ x: 0, y: 0.76, z: C - 0.7, clone() { return this; } });   // corta
    const toastCorta = D.st.toast;
    TT.judgeAiBounce({ x: 0, y: 0.76, z: C - HL + 0.07, clone() { return this; } }); // fondo 15cm
    Q.log('t4b «corta» al no llegar al fondo y pica el fondo', toastCorta.indexOf('corta') >= 0 && D.st.streak === 1,
      'toast="' + toastCorta.slice(0, 18) + '" · streak=' + D.st.streak);
    T.stopMode(G);
    await wait(300);
  })().then(() => { window.__QA.done = true; })
      .catch(e => { window.__QA.done = true; window.__QA.err = String(e && e.stack || e); });
  return 'lanzado';
})()
