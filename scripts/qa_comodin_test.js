(() => {
  const G = window.__PP_GAME;
  const c = G.champs.mod.controller;
  const B = c._burla;
  const estadoReal = G.rules.state;
  G.rules.state = 'rally';
  const com = B.cartones.find(x => x.kind === 'comodin');
  com.alive = true; com.age = 0.5; com.mat.opacity = 1; com.mesh.visible = true;
  com.cx = com.x = 0; com.cz = com.z = -1.6;
  com.mesh.position.set(0, B.tableTopY + 0.25, -1.6);
  const ball = G.ball;
  const r0 = window.__PP_CORE.DIMS.ballRadius;
  if (!c._burlaPrevV) c._burlaPrevV = new THREE.Vector3();
  c._burlaPrevV.set(0, 1.00, -1.45);
  c._burlaHasPrev = true;
  ball.pos.set(0, 1.00, -1.75);
  ball.vel.set(0.2, -0.2, -3.5);
  let paso1, paso2, err = null;
  try {
    c._updateBurla(0.016);
    paso1 = {
      cartonVivo: com.alive,
      fx: !!c._comodinFx,
      escala: +G.ballMesh.scale.x.toFixed(2),
      rNuevo: +window.__PP_CORE.DIMS.ballRadius.toFixed(4),
      rAntes: +r0.toFixed(4),
      velIntacta: ball.vel.toArray().map(v => +v.toFixed(2)),
    };
  } catch (e) { G.rules.state = estadoReal; return 'EXCEP1: ' + e.message; }
  try {
    G.events.push({ type: 'paddle', who: 'player', pos: ball.pos.clone(), speed: 4 });
    c._updateBurla(0.016);
    paso2 = {
      fx: !!c._comodinFx,
      rRestaurado: +window.__PP_CORE.DIMS.ballRadius.toFixed(4),
      cintas: B.ribbons.filter(r => r.t < r.life).length,
      estado: G.rules.state,
      scoreP: G.rules.scorePlayer,
      msg: (G.rules.message || '').slice(0, 48),
    };
  } catch (e) { G.rules.state = estadoReal; return 'EXCEP2: ' + e.message; }
  G.rules.state = estadoReal;
  return JSON.stringify({ paso1, paso2 });
})()
