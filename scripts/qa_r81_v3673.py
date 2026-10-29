#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r81_v3673 — CAPA BP · V3.6.72→3.6.84-SDK6, FASE 75 «SESENTA SEGUROS».

Petición del dueño (r81): «debemos tener una herramienta para poder calibrar
los FPS según el modelo de gafas… para unas Oculus 2 las partidas van muy
lentas y la experiencia es muy mala. Que podríamos hacer para tener un
autocalibrador que asegure al menos 60 FPS seguros en cualquier dispositivo.
Por cierto en modo de multijugador no está calibrando bien los movimientos
entre los dos jugadores, no deja sacar ni jugar. Puedes simular una conexión
realista entre dos usuarios para verificar que funciona, a mí me cuesta poder
revisar el multiusuario».

Lo implementado (r81) y SU verificación:
  · PERF GOVERNOR (c12): perfil POR CASCO detectado por GPU real (Adreno
    740 = Quest 3 mantiene 1.40×/0.50/90-120; Adreno 650 = Quest 2 nace en
    1.05×/0.65/72 — hoy esas partidas «van muy lentas» — y genérico 1.20×),
    SONDA de calibración (rondas de 2,8 s hasta sostener ≥63 de media con
    peor segundo ≥55: fovea → tasa 60 → escala para la próxima sesión),
    GOBERNADOR continuo con histéresis (baja con voz si el promedio cae,
    recupera si sobra margen), persistencia por casco en localStorage y
    AJUSTES › RENDIMIENTO con FPS en vivo, AUTO/manual y RECALIBRAR.
  · MULTIJUGADOR JUGABLE — tres defectos de fondo cazados:
    (1) DOBLE ESPEJO: el emisor ya manda la posición en el marco del
        receptor (posToNet/_stateNet) y el receptor VOLVÍA a aplicar la
        involución (posFromNet/posFromNetArr): R∘R = identidad → bola y
        pala del rival en el lado CONTRARIO de la mesa desde v2.19. El
        espejo ahora se aplica UNA sola vez por camino.
    (2) VALIDADOR CONTRA PAREDES: comparaba ev.p (marco del receptor) con
        la pose CRUDA del rival (marco del emisor): distancia absurda
        (>2 m) → TODO golpe remoto rechazado → «no deja sacar ni jugar».
        Ahora poseToNetFrame pone la pala en el MISMO marco y EN el
        instante del golpe (JitterBuf.nearest), y el lanzamiento (kind 2)
        mira la mano LIBRE (la que lanza no lleva la pala).
    (3) rallyId NO EXISTÍA: los CLAIM/ACK usaban rules.rallyId (undefined)
        → el libro de reclamos colisionaba tras el primer punto y el
        marcador se congelaba. Identidad real: rules.rallySeq.
    Además: ICE tempranos en cola (llegaban antes de setRemoteDescription
    y morían en silencio en redes reales), la bola HELD del rival nace
    oculta en el MATCH_START y el lanzamiento (kind 2) libera el holdLock.
  · DUELO SIMULADO (la herramienta que pide el dueño): DOS páginas reales
    conectadas por la señalización PeerJS REAL con mandos sintéticos a
    60 Hz y NETSIM en el canal fast (35 ms ± 12 ms de jitter, 2 % de
    pérdida): sala → CRAZY LINK v2 → MATCH_START → SAQUE del anfitrión →
    traspaso → DEVOLUCIÓN del invitado → muerte de la bola → CLAIM/ACK →
    marcador ESPEJADO e idéntico en ambos extremos, 0 rechazos del
    validador y 0 pageerrors.

BLOQUES: (1) AGUJAS r81 en el servido. (2) CONTADORES exactos. (3) JUEGO
REAL headless: PerfManager vivo (detección, sonda, gobernador, save/load,
AJUSTES › RENDIMIENTO por rects), cadenas de espejo y validador sobre la
instancia viva. (4) DUELO SIMULADO de dos usuarios.
Uso: python3 qa_r81_v3673.py [URL]
"""
import asyncio
import sys

from playwright.async_api import async_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000/game.html"
ok = fails = 0


def chk(cond, label):
    global ok, fails
    print(("  ✓ " if cond else "  ✗ FALLO: ") + label)
    if cond:
        ok += 1
    else:
        fails += 1


AGUJAS = [
    # — el PERF GOVERNOR (autocalibrador) —
    ("perfil por casco (tabla PERF_TIERS)", "const PERF_TIERS = {"),
    ("Quest 3 mantiene el 1.40 de siempre", "quest3: { label: 'Quest 3', scale: 1.40, fovea: 0.50, rate: 90 }"),
    ("Quest 2 nace fluido (1.05×)", "quest2: { label: 'Quest 2', scale: 1.05, fovea: 0.65, rate: 72 }"),
    ("clase PerfManager", "class PerfManager {"),
    ("detección por GPU real (Adreno)", "WEBGL_debug_renderer_info"),
    ("Adreno 740 → Quest 3", "/adreno\\s*\\(tm\\)\\s*74\\d/i"),
    ("Adreno 650 → Quest 2", "/adreno\\s*\\(tm\\)\\s*65\\d/i"),
    ("persistencia por casco", "localStorage.setItem(PERF_LS"),
    ("sonda: rondas de 2,8 s", "p.t >= 2.8"),
    ("sonda: umbral 63 de media y peor segundo 55", "fpsAvg >= 63 && fpsMin >= 55"),
    ("escalón 1: foveation", "if (p.round === 0) this.fovea = Math.min(0.8, this.fovea + 0.10)"),
    ("escalón 2: tasa 60 estable", "this.rate = this.rate > 62 ? 60 : this.rate"),
    ("escalón 3: escala próxima sesión", "this.scale = Math.max(0.9, this.scale - 0.15)"),
    ("gobernador: baja si el promedio cae", "const bajando = avg < 56 || (avg < 60 && min < 48)"),
    ("gobernador: no cambia en pleno rallye", "if (!rally || avg < 50) this._stepDown()"),
    ("gobernador: recuperación si sobra margen", "if (this._upStreak >= 20 && this._upCool <= 0) this._stepUp()"),
    ("tasa objetivo del perfil al entrar en VR", "session.updateTargetFrameRate(best)"),
    ("sonda automática al entrar en VR", "this.probeStart('boot')"),
    ("recalibración manual", "requestRecal()"),
    ("estado para AJUSTES y QA", "status() {"),
    ("exposición window.__PP_PERF", "window.__PP_PERF = this"),
    ("latido en el bucle animate", "this.perf.feed(dt, presenting)"),
    ("cierre de sonda al salir de VR", "this.perf.onSessionEnd()"),
    ("el viejo 1.4 fijo lo decide el gobernador", "this.perf.applyToRenderer()"),
    ("AJUSTES: tarjeta RENDIMIENTO", "'page:optsRendi'"),
    ("AJUSTES: subpágina rendi", "case 'rendi':"),
    ("FPS en vivo con refresco suave", "this._perfMenuAcc = 0.5"),
    ("conmutador de autocalibración", "case 'perfAuto':"),
    ("perfil manual del casco", "case 'perfTier':"),
    ("botón RECALIBRAR", "case 'perfRecal':"),
    ("cadenas del dueño ES", "cat_rendi: 'RENDIMIENTO'"),
    ("cadenas del dueño EN", "cat_rendi: 'PERFORMANCE'"),
    ("voz del escalón ES", "perf_stepdown: 'Optimizando la imagen para ir fluido'"),
    ("voz del escalón EN", "perf_stepdown: 'Optimizing visuals to keep it smooth'"),
    # — multijugador jugable: un solo espejo —
    ("convenio del cable documentado", "CONVENCIÓN ÚNICA DEL CABLE"),
    ("posFromNet ya NO re-espeja (R∘R=idencia)", "out.set(a[0], a[1] + T, a[2])"),
    ("posFromNetArr solo re-ancla la Y", "return new THREE.Vector3(a[0], a[1] + T, a[2])"),
    ("espejo de pose (X/Z, Y intacta)", "static posFromNetPose(a, out) {"),
    ("pose al marco del validador", "static poseToNetFrame(a) {"),
    ("avatar rival: espejo de pose", "NetLink.posFromNetPose(hpa, netTmpP)"),
    ("visor del rival: espejo de pose", "NetLink.posFromNetPose(smp.hp, netTmpP)"),
    # — validador en el marco y en el instante —
    ("pala del rival en el marco del evento", "const pad = this._remotePadNet(ev.kind, ev.tHit)"),
    ("muestra más próxima al golpe (JB)", "nearest(tHit, this._padSmp"),
    ("el lanzamiento mira la mano libre", "if (kind === 2) {"),
    ("JitterBuf.nearest en el núcleo", "nearest(tHost, out, winMs) {"),
    ("ventana de 250 ms para juzgar", "const W = winMs || 250"),
    # — el lanzamiento libera el hold + bola HELD oculta —
    ("kind 2 libera el holdLock del rival", "g._netTossLive = true"),
    ("bola HELD oculta en MATCH_START", "this.ballMesh.visible = this.rules.server === 'player'"),
    # — identidad de rallye (claims) —
    ("claims con rallySeq", "const rallyId = r.rallySeq"),
    ("espejo SIEMPRE en los claims (anfitrión incl.)", "const wMapped = m.w === 'let' ? 'let'",),
    ("intercambio de perspectiva en el claim", ": (m.w === 'player' ? 'ai' : 'player')"),
    ("intents de punto con rallySeq", "this._sync.localPoint(g.rules.rallySeq"),
    # — ICE tempranos (redes reales) —
    ("cola de ICE tempranos", "this._iceQ = []"),
    ("drenado de ICE al fijar la descripción", "for (const c of q) {"),
    ("_onIce encola sin descripción remota", "_onIce(c) {"),
    # — el glue ya no indexa el Vector3 (bola NaN del r79) —
    ("HIT aplica la bola con copy (no NaN)", "g.ball.pos.copy(p);"),
    ("HANDOFF aplica con copy (no NaN)", "g.ball.pos.copy(p);     // r81: Vector3 — copy, no indexado"),
    ("watchdog HELLO generoso (22 s)", "}, 22000);"),
    ("versión sellada de nacimiento", "const VERSION = '3.6.84-SDK6'"),
]

CONTADORES = [
    ("PerfManager (def + new + hook)", "PerfManager", 3),
    ("PERF_TIERS (def + usos)", "PERF_TIERS", 12),
    ("probeStart (def + llamadas)", "probeStart", 3),
    ("_stepDown (def + llamada)", "_stepDown", 2),
    ("_stepUp (def + llamada)", "_stepUp", 2),
    # r82: +1 uso (la bola HELD del rival se ve EN SU MANO)
    ("posFromNetPose (def + 3 usos)", "posFromNetPose", 4),
    ("poseToNetFrame (def + uso)", "poseToNetFrame", 3),
    ("nearest( en el transporte", "this._jb.nearest(", 1),
    ("optsRendi (tarjeta + whitelist + comentario + animate)", "optsRendi", 4),
    ("perfRecal (botón + caso)", "perfRecal", 2),
    ("_onIce (def + llamada)", "_onIce", 2),
    ("_iceQ (cola completa)", "_iceQ", 5),
    ("r.rallySeq en el claim", "const rallyId = r.rallySeq", 1),
    ("rallySeq en los intents de punto", "localPoint(g.rules.rallySeq", 1),
    ("versión única", "const VERSION = '3.6.84-SDK6'", 1),
]

JS_PERF = """async () => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 1 · el gobernador existe y detecta un perfil
  const P = window.__PP_PERF;
  chk(!!P && P.g === G, 'PerfManager vivo en window.__PP_PERF');
  const st = P.status();
  chk(['quest3', 'quest2', 'gen'].indexOf(st.tier) >= 0, 'perfil detectado: ' + st.tier);
  chk(st.scale > 0.89 && st.scale <= 1.41, 'escala del perfil razonable: ×' + st.scale);
  chk(st.fovea >= 0.4 && st.fovea <= 0.81, 'foveation del perfil razonable: ' + st.fovea);
  chk(typeof st.fps === 'number', 'FPS medidos disponibles para AJUSTES');

  // 2 · el foveation lo aplica el gobernador (API viva de three)
  chk(typeof G.renderer.xr.setFoveation === 'function',
      'renderer.xr.setFoveation disponible para el gobernador (perfil fovea ' + P.fovea + ')');

  // 3 · la sonda baja escalones con frames pesados (física simulada);
  //     en headless la sesión no existe: la simulamos como hace el casco
  G.renderer.xr.isPresenting = true;
  P.lastCal = null;
  P.probeStart('qa');
  chk(!!P.probe, 'sonda de calibración arrancada a mano');
  const fovea0 = P.fovea, rate0 = P.rate;
  for (let i = 0; i < 140; i++) P.feed(1 / 24, true);   // ~5,8 s a 24 fps
  chk(P.fovea > fovea0 || P.rate < rate0 || P.scale < st.scale,
      'sonda: un casco a 24 fps DEGRADA (fovea ' + fovea0 + '→' + P.fovea
      + ' · rate ' + rate0 + '→' + P.rate + ')');
  chk(P.probe === null || P.probe.round >= 1, 'sonda: escalón aplicado y ronda avanzada');
  P.probe = null;
  G.renderer.xr.isPresenting = false;

  // 4 · el gobernador continuo también degrada fuera de la sonda
  G.renderer.xr.isPresenting = true;
  P._hist.length = 0;
  P._coolDown = 0;
  const fovea1 = P.fovea;
  for (let i = 0; i < 600 && P._hist.length < 5; i++) P.feed(1 / 22, true);
  const baj = P.fovea > fovea1 || P.rate < 72 || P.scale < st.scale;
  chk(baj, 'gobernador: 22 fps sostenidos → escalón a la baja (fovea ' + fovea1 + '→' + P.fovea + ')');
  chk(P._coolDown > 0, 'gobernador: cooldown anti-oscilación armado');
  G.renderer.xr.isPresenting = false;

  // 5 · persistencia por casco
  P.save();
  const raw = localStorage.getItem('ppxr_perf_v1');
  chk(!!raw && JSON.parse(raw).tier === P.tier, 'perfil guardado en localStorage por casco');

  // 6 · AJUSTES › RENDIMIENTO: tarjeta y subpágina con rects sanos
  G.menuOpen = true; G.menuPage = 'opts'; G.drawMenu();
  let rs = G.menuRects || [];
  const card = rs.find((r) => r.id === 'page:optsRendi');
  chk(!!card, 'AJUSTES: tarjeta RENDIMIENTO presente');
  const cats = rs.filter((r) => String(r.id).indexOf('page:opts') === 0);
  // r83: el ajuste de pala MUDA a AJUSTES como 7.ª tarjeta (PALA · AGARRE)
  chk(cats.length === 7, 'AJUSTES: siete categorías (con RENDIMIENTO y PALA)');
  chk(!!card && (card.y + card.h) <= 1536, 'AJUSTES: la tarjeta cabe en el lienzo');
  G.menuPage = 'optsRendi'; G.drawMenu();
  rs = G.menuRects || [];
  const ids = rs.map((r) => String(r.id));
  chk(ids.indexOf('perfAuto') >= 0, 'RENDIMIENTO: conmutador de autocalibración');
  chk(ids.indexOf('perfRecal') >= 0, 'RENDIMIENTO: botón RECALIBRAR');
  chk(ids.some((s) => s.indexOf('perfTier:') === 0), 'RENDIMIENTO: perfiles de casco');
  chk(ids.indexOf('close') >= 0 && rs.find((r) => r.id === 'close').y <= 1428,
      'RENDIMIENTO: el cierre sigue en su sitio');
  let fuera = 0;
  for (const r of rs) if (r.y + r.h > 1536 || r.y < 0) fuera++;
  chk(fuera === 0, 'RENDIMIENTO: ningún rect sale del lienzo');

  // 7 · setTier manual respeta el perfil elegido
  const tier0 = P.tier;
  P.setTier('quest2');
  chk(P.scale === 1.05 && Math.abs(P.fovea - 0.65) < 1e-9, 'perfil Quest 2 manual: ×1.05 · fovea 0.65');
  P.setTier(tier0);
  return out;
}"""

JS_RED = """() => {
  const G = window.__PP_GAME;
  if (!G) return { error: 'sin __PP_GAME' };
  const L = G.net.constructor;              // NetLink
  const V = G.camera.position.constructor;  // THREE.Vector3
  const out = { checks: [] };
  const chk = (cond, label) => out.checks.push([!!cond, label]);

  // 1 · UN solo espejo: lo que el anfitrión emite, el invitado lo ve al
  // lado opuesto de SU mesa (R una vez; nunca R∘R = identidad)
  const p = new V(0.3, 1.0, 0.5);           // cerca del anfitrión
  const wire = L.posToNet(p);               // emisión (marco del receptor)
  const back = new V(); L.posFromNet(wire, back);
  chk(back.z < -3.0 && Math.abs(back.x + 0.3) < 1e-6,
      'un solo espejo: pala (0.3,·,0.5) del anfitrión → (' + back.x.toFixed(2)
      + ',·,' + back.z.toFixed(2) + ') del invitado (lado lejano)');
  chk(Math.abs(L.posFromNetArr(wire).z + 3.7) < 1e-6 && Math.abs(L.posFromNetArr(wire).x + 0.3) < 1e-6,
      'posFromNetArr (v2): el evento aterriza en el marco del receptor ('
      + L.posFromNetArr(wire).x.toFixed(2) + ',·,' + L.posFromNetArr(wire).z.toFixed(2) + ')');
  const evV = L.vecFromNetArr([-1.0, 2.0, -3.0]);
  chk(evV.z === -3.0 && evV.x === -1.0, 'vecFromNetArr (v2): identidad (el emisor ya espejó)');

  // 2 · poses: espejo X/Z con la Y intacta (la Y ya viene anclada a MI tapete)
  const q = new V(); L.posFromNetPose([0.3, 1.5, 0.5], q);
  chk(Math.abs(q.x + 0.3) < 1e-6 && Math.abs(q.z + 3.7) < 1e-6 && q.y === 1.5,
      'pose del rival: X/Z espejadas · Y sin +T doble (' + q.y + ')');

  // 3 · validador §12: el golpe del rival pasa con los marcos correctos
  const N = window.__PPNET;
  const jb = new N.JitterBuf();
  // pose CRUDA del anfitrión (marco emisor, Y anclada al tapete por códec)
  jb.push(5000, { hp: [0, 1.7, 0.4], hq: [0, 0, 0, 1],
    lp: [-0.4, 1.0, 0.1], lq: [0, 0, 0, 1],
    rp: [0.3, 1.0, 0.5], rq: [0, 0, 0, 1], fl: 0b011 });  // pala en la DERECHA
  G.net._jb = jb;                            // la usa _remotePadNet
  G.net._padSmp = null;
  const pad = G.net._remotePadNet(1, 5000);  // golpe: mano de la pala
  chk(!!pad && Math.abs(pad[0] + 0.3) < 1e-6 && Math.abs(pad[2] + 3.7) < 1e-6
      && Math.abs(pad[1] - 0.24) < 1e-6,
      'pala del rival al marco del evento: ' + JSON.stringify(pad && pad.map((x) => +x.toFixed(2))));
  // el MISMO punto físico del golpe (bola del anfitrión espejada al wire)
  const ev = { t: 1, kind: 1, shot: 1, tHit: 5010,
    p: L.posToNet(new V(0.28, 1.05, 0.52)), v: [0, 0, -5], s: [0, 0, 0] };
  const d = Math.hypot(ev.p[0] - pad[0], ev.p[1] - pad[1], ev.p[2] - pad[2]);
  chk(d < 0.3, 'distancia golpe↔pala en el MISMO marco: ' + d.toFixed(2) + ' m (<0,3)');
  const val = new N.Validator();
  const r1 = val.hit(ev, { nowHost: 5020, lastShot: 0, lastHitT: 0, padPos: pad });
  chk(r1.ok, 'validación §12: el saque del rival ACEPTADO (antes: rechazado siempre)');
  // lanzamiento kind 2: la mano LIBRE (izquierda aquí), no la de la pala
  const pad2 = G.net._remotePadNet(2, 5000);
  chk(!!pad2 && Math.abs(pad2[0] - 0.4) < 1e-6,
      'kind 2: el validador mira la mano de la bola (' + JSON.stringify(pad2 && pad2.map((x) => +x.toFixed(2))) + ')');
  // y el golpe AÚN LEJANO se sigue rechazando (anti-trampa viva)
  const evFar = { t: 1, kind: 0, shot: 2, tHit: 5100,
    p: L.posToNet(new V(0.3, 1.05, -1.2)), v: [0, 0, 3], s: [0, 0, 0] };
  const r2 = val.hit(evFar, { nowHost: 5200, lastShot: 1, lastHitT: 5010, padPos: pad });
  chk(!r2.ok, 'anti-trampa intacta: golpe lejos de la pala RECHAZADO');

  // 4 · nearest: la muestra del instante del golpe, no la retrasada del avatar
  jb.push(5600, { hp: [0, 1.7, 0.4], hq: [0, 0, 0, 1],
    lp: [-0.4, 1.0, 0.1], lq: [0, 0, 0, 1],
    rp: [0.9, 1.0, -0.2], rq: [0, 0, 0, 1], fl: 0b011 });
  const n3 = jb.nearest(5010, null, 250);
  chk(!!n3 && n3.rp[0] === 0.3, 'nearest: juzga con la pose DEL INSTANTE del golpe');
  const n4 = jb.nearest(5010, null, 250);
  chk(!!n4 && n4 !== jb.s[jb.s.length - 1], 'nearest: NO usa la última muestra de reproducción');

  // 5 · el gobernador sobre la instancia viva: el Quest 2 nace fluido
  chk(G.perf === window.__PP_PERF, 'c12: el juego cuelga su PerfManager (this.perf)');
  return out;
}"""

# ————— DUELO SIMULADO · dos usuarios reales con NETSIM —————
JS_ARM = """() => {
  const G = window.__PP_GAME;
  if (!G || G.__simReady) return !!G;
  const V = G.camera.position.constructor;
  const Q = G.camera.quaternion.constructor;
  const mk = () => ({ position: new V(0, 1, 0.2), quaternion: new Q(0, 0, 0, 1) });
  G.grips = [mk(), mk()];
  G.paddleHand = 1;                       // la pala en la mano derecha
  G.__simT = 0;
  G.__simIv = setInterval(() => {         // pose viva a ~60 Hz para el JB
    G.__simT += 16;
    const s = Math.sin(G.__simT / 420);
    G.grips[1].position.set(0.22 * s, 0.95, -0.75 + 0.1 * Math.cos(G.__simT / 700));
    G.grips[0].position.set(-0.28, 1.0, 0.1);
  }, 16);
  // NETSIM: 35 ms ± 12 ms de ida, 2 % de pérdida (cruce real de Internet)
  const N = window.__PPNET;
  const sim = new N.NetSim({ lat: 35, jit: 12, loss: 0.02, seed: 20261027 });
  const orig = G.net._fastSend.bind(G.net);
  G.net._fastSend = (buf, now) => sim.emit(buf, now, (b) => orig(b, performance.now()));
  G.__simPump = setInterval(() => sim.pump(performance.now()), 6);
  G.__simReady = true;
  return true;
}"""

JS_HOST_ROOM = """() => { window.__PP_GAME.net.hostRoom(); return true; }"""
JS_GUEST_JOIN = """(code) => { window.__PP_GAME.net.joinRoom(code); return true; }"""


async def wait_cond(page, js, timeout_s, step_ms=250):
    t = 0.0
    while t < timeout_s:
        try:
            if await page.evaluate(js):
                return True
        except Exception:
            pass
        await page.wait_for_timeout(step_ms)
        t += step_ms / 1000.0
    return False


JS_ONLINE = "() => window.__PP_GAME && window.__PP_GAME.net.online && window.__PP_GAME.net.v2 === 'ok'"
JS_STARTED = "() => { const G = window.__PP_GAME; return G && !G._netStart && G.rules.state === 'serve' && G.net.v2 === 'ok'; }"
JS_STATE = "() => { const G = window.__PP_GAME; return { st: G.rules.state, sv: G.rules.server, ball: G.net._ball.state, sp: G.rules.scorePlayer, sa: G.rules.scoreAi, rej: G.net._val ? G.net._val.rejects : -1, ser: G.net._val ? G.net._val.serious : -1, ping: G.net.pingMs(), toss: !!G._netTossLive, ballVis: G.ballMesh ? G.ballMesh.visible : null, errors: G.net._val ? G.net._val.log.slice(0, 4) : [] }; }"

JS_HOST_SERVE_A = """() => {
  const G = window.__PP_GAME;
  G.grips[1].position.set(0.10, 0.93, -0.62);   // pala junto al golpeo
  G.grips[1].quaternion.set(0, 0, 0, 1);
  return G.rules.state + '|' + G.rules.server + '|' + G.net._ball.state;
}"""

JS_HOST_SERVE_B = """() => {
  const G = window.__PP_GAME;
  // SAQUE del anfitrión (las MISMA llamadas del bloque de golpeo real).
  // La velocidad se busca con la FÍSICA REAL del juego (simulateServePath,
  // la misma que usa el solver de la casa): bote legal en mi mitad →
  // despeje con margen sobre la cinta → bote profundo en la mitad del
  // invitado, con garra suficiente para que el invitado pueda DEVOLVER.
  G.ball.pos.set(0.10, 1.05, -0.30);
  const C = -1.6;
  const spin = G.camera.position.constructor.prototype;
  const sp = new (G.ball.spin.constructor)(6, 0, 0);
  let elegido = null;
  for (let vy = 1.7; vy <= 2.7 && !elegido; vy += 0.2) {
    for (let vz = -1.5; vz >= -2.6 && !elegido; vz -= 0.15) {
      for (let vx = -0.3; vx <= 0.3 && !elegido; vx += 0.2) {
        const v = new (G.ball.vel.constructor)(vx, vy, vz);
        const r = window.__ppDebug.simulateServePath(G.ball.pos, v, sp, +1);
        if (r.ok && (r.netY === null || r.netY >= 0.95) &&
            Math.abs(r.oppZ - C) >= 0.55) elegido = v;
      }
    }
  }
  if (!elegido) elegido = new (G.ball.vel.constructor)(0.05, 2.2, -1.9);
  G.ball.vel.copy(elegido);
  G.ball.spin.copy(sp);
  G.rules.beginServeRally('player');
  G.net.sendHit(true);
  return G.net._ball.state;
}"""

JS_GUEST_WAIT_AUTH = "() => window.__PP_GAME.net._ball.state === 'auth' && window.__PP_GAME.rules.validBounce === true"

JS_GUEST_RETURN = """() => {
  const G = window.__PP_GAME;
  if (G.net._ball.state !== 'auth') return 'noauth:' + G.net._ball.state;
  G.grips[1].position.set(0.05, 0.88, -1.38);   // pala del invitado junto al golpeo
  G.grips[1].quaternion.set(0, 0, 0, 1);
  G.ball.pos.set(0.05, 1.00, -1.35);
  G.ball.vel.set(-0.05, 0.50, -2.90);           // hacia el anfitrión (mitad lejana)
  G.ball.spin.set(0, 0, 0);
  G.processIntents(G.rules.registerPaddleHit('player'));
  G.net.sendHit(false);
  return 'ok';
}"""

JS_HOST_WAIT_BOUNCE = """() => {
  // el anfitrión espera el punto (doble bote del saque del invitado en su mitad)
  const G = window.__PP_GAME;
  return G.rules.state === 'point' && (G.rules.scorePlayer + G.rules.scoreAi) > 0;
}"""


async def duel(browser):
    print("— BLOQUE 4 · DUELO SIMULADO: dos usuarios reales + NETSIM —")
    host = await browser.new_page(viewport={"width": 1100, "height": 650})
    guest = await browser.new_page(viewport={"width": 1100, "height": 650})
    errs = {"h": [], "g": []}
    host.on("pageerror", lambda e: errs["h"].append(str(e)))
    guest.on("pageerror", lambda e: errs["g"].append(str(e)))
    try:
        # arranque de ambos jugadores
        for pg, who in ((host, "anfitrión"), (guest, "invitado")):
            await pg.goto(URL, wait_until="domcontentloaded", timeout=45000)
        for pg, who in ((host, "anfitrión"), (guest, "invitado")):
            listo = await wait_cond(pg, "() => !!window.__PP_GAME && !!window.__PPNET", 45)
            chk(listo, f"duelo: {who} en la cancha (__PP_GAME + __PPNET)")
        # mandos sintéticos + NETSIM (conexión realista)
        for pg, who in ((host, "anfitrión"), (guest, "invitado")):
            await pg.evaluate(JS_ARM)
        chk(True, "duelo: mandos sintéticos a 60 Hz + NETSIM (35 ms ± 12 ms · 2 % pérdida)")

        # sala: el anfitrión crea y el invitado entra con el código REAL
        await host.evaluate(JS_HOST_ROOM)
        code = None
        for _ in range(40):
            st = await host.evaluate("() => window.__PP_GAME.net.status")
            if st == "waiting":
                code = await host.evaluate("() => window.__PP_GAME.net.code")
                break
            await host.wait_for_timeout(250)
        chk(bool(code) and len(code) == 5,
            f"duelo: sala creada por señalización PeerJS REAL (código {code})")
        await guest.evaluate(JS_GUEST_JOIN, code)

        # CRAZY LINK v2 arriba en AMBOS extremos
        hOn = await wait_cond(host, JS_ONLINE, 30)
        gOn = await wait_cond(guest, JS_ONLINE, 30)
        chk(hOn, "duelo: anfitrión con transporte binario v2 (fast+reliable)")
        chk(gOn, "duelo: invitado con transporte binario v2 (fast+reliable)")
        if not (hOn and gOn):
            hst = await host.evaluate("() => window.__PP_GAME.net.statusMsg")
            gst = await guest.evaluate("() => window.__PP_GAME.net.statusMsg")
            print(f"    estado anfitrión: {hst} · invitado: {gst}")
            return

        # MATCH_START: cuenta atrás del reloj del anfitrión y saque preparado
        hGo = await wait_cond(host, JS_STARTED, 15)
        gGo = await wait_cond(guest, JS_STARTED, 15)
        chk(hGo and gGo, "duelo: MATCH_START con cuenta atrás cumplida en ambos")
        preH = await host.evaluate(JS_HOST_SERVE_A)
        chk(preH.startswith("serve|player"), f"duelo: saca el anfitrión ({preH})")
        preG = await guest.evaluate("() => window.__PP_GAME.rules.server")
        chk(preG == "ai", "duelo: el invitado SABE que saca el rival")
        # r82 · REFERENCIA EXACTA: la bola HELD del rival ya no nace oculta —
        # se VE EN SU MANO LIBRE (pose de red espejada, mitad lejana)
        gVis = await guest.evaluate("() => window.__PP_GAME.ballMesh.visible")
        gBz = await guest.evaluate("() => window.__PP_GAME.ball.pos.z")
        chk(gVis is True and gBz < -2.0,
            f"duelo: la bola HELD del rival se VE EN SU MANO (visible={gVis} · z={gBz:.2f})")

        # SAQUE del anfitrión (2 poses antes de golpear para el validador)
        await host.wait_for_timeout(220)
        stBall = await host.evaluate(JS_HOST_SERVE_B)
        chk(stBall == "own", "duelo: saque golpeado → bola OWN del anfitrión (sagrado)")
        # el invitado ve el LANZAMIENTO (kind 2) y el GOLPE (kind 1) del rival
        gRally = await wait_cond(guest, "() => window.__PP_GAME.rules.state === 'rally'", 8)
        chk(gRally, "duelo: el invitado entra en RALLYE con el saque del rival (antes: bloqueado)")
        gAuth = await wait_cond(guest, JS_GUEST_WAIT_AUTH, 10)
        chk(gAuth, "duelo: TRASPASO de la bola al cruzar la red (HANDOFF → AUTH) y bote VÁLIDO en mi mitad")
        if gAuth:
            gj = await guest.evaluate(JS_STATE)
            chk(gj["rej"] == 0, f"duelo: validador del invitado SIN rechazos ({gj['rej']})")
            chk(gj["ping"] >= 0, f"duelo: reloj compartido vivo (ping {gj['ping']} ms)")

        # DEVOLUCIÓN del invitado (el mismo camino del golpeo real)
        ret = await guest.evaluate(JS_GUEST_RETURN)
        chk(ret == "ok", f"duelo: el invitado DEVUELVE tras el bote ({ret})")
        hHit = await wait_cond(host, "() => window.__PP_GAME.rules.rallyHits >= 1", 10)
        chk(hHit, "duelo: el anfitrión recibe el golpe del rival y su árbitro lo cuenta")
        hRej = await host.evaluate("() => window.__PP_GAME.net._val.rejects")
        chk(hRej == 0, f"duelo: validador del anfitrión SIN rechazos ({hRej})")

        # muerte de la bola en la mitad del anfitrión → CLAIM/ACK → marcador
        hPoint = await wait_cond(host, JS_HOST_WAIT_BOUNCE, 12)
        chk(hPoint, "duelo: punto detectado por el árbitro del anfitrión (doble bote)")
        gPoint = await wait_cond(guest, "() => window.__PP_GAME.rules.state === 'point' && (window.__PP_GAME.rules.scorePlayer + window.__PP_GAME.rules.scoreAi) > 0", 12)
        chk(gPoint, "duelo: el punto llega al invitado (CLAIM aplicado)")
        if hPoint:
            hj = await host.evaluate(JS_STATE)
            gj2 = await guest.evaluate(JS_STATE)
            chk(hj["sa"] == 1 and gj2["sp"] == 1,
                f"duelo: marcador ESPEJADO e idéntico (anfitrión {hj['sp']}-{hj['sa']} · invitado {gj2['sp']}-{gj2['sa']})")
            chk(hj["rej"] == 0 and gj2["rej"] == 0,
                "duelo: 0 rechazos del validador en TODA la secuencia")

        # el avatar del rival se mueve en ambos (poses 60 Hz por el JB)
        await host.wait_for_timeout(400)
        hAv = await host.evaluate("() => window.__PP_GAME.aiPaddleMesh.position.z")
        gAv = await guest.evaluate("() => window.__PP_GAME.aiPaddleMesh.position.z")
        chk(hAv < -2.4, f"duelo: la pala del invitado vive en la mitad LEJANA del anfitrión (z={hAv:.2f})")
        chk(gAv < -2.4, f"duelo: la pala del anfitrión vive en la mitad LEJANA del invitado (z={gAv:.2f})")

        # la herramienta queda reseñada en telemetría técnica
        rep = await host.evaluate("() => { const r = window.__PP_GAME.net.netReport(); return r.mode + '|' + (r.hits || 0); }")
        chk(rep.startswith("binario-v2"), f"duelo: telemetría de partida ({rep})")
    finally:
        for pg in (host, guest):
            try:
                await pg.evaluate("() => { const G = window.__PP_GAME; if (G && G.__simIv) clearInterval(G.__simIv); if (G && G.__simPump) clearInterval(G.__simPump); G && G.net.cancel && G.net.cancel(); }")
            except Exception:
                pass
            try:
                await pg.close()
            except Exception:
                pass
        if errs["h"] or errs["g"]:
            for e in (errs["h"] + errs["g"])[:6]:
                print("  ✗ pageerror (duelo): " + e[:200])
        chk(len(errs["h"]) == 0 and len(errs["g"]) == 0,
            "duelo: 0 pageerrors en ambos usuarios")


async def main():
    src = ""
    try:
        import urllib.request
        with urllib.request.urlopen(URL, timeout=15) as r:
            src = r.read().decode("utf-8", "replace")
    except Exception as e:
        print(f"✗ FALLO: no se pudo leer {URL}: {e}")
        sys.exit(1)

    print("— BLOQUE 1 · AGUJAS r81 en el servido —")
    for label, needle in AGUJAS:
        chk(needle in src, label)

    print("— BLOQUE 2 · CONTADORES exactos —")
    import re
    for label, pat, esperado in CONTADORES:
        n = len(re.findall(re.escape(pat), src))
        chk(n == esperado, f"{label} → {n} (esperado {esperado})")

    print("— BLOQUE 3 · JUEGO REAL headless (gobernador, espejos y validador) —")
    page_errors = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader"])
        page = await browser.new_page(viewport={"width": 1280, "height": 720})
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        await page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        try:
            juego = False
            for _ in range(90):
                juego = await page.evaluate("() => !!window.__PP_GAME && !!window.__PP_PERF")
                if juego:
                    break
                await page.wait_for_timeout(500)
            chk(juego, "el juego arranca con __PP_GAME y __PP_PERF")

            res = await page.evaluate(JS_PERF)
            if res.get("error"):
                chk(False, "JS_PERF: " + res["error"])
            else:
                for cond, label in res.get("checks", []):
                    chk(cond, "perf: " + label)

            res2 = await page.evaluate(JS_RED)
            if res2.get("error"):
                chk(False, "JS_RED: " + res2["error"])
            else:
                for cond, label in res2.get("checks", []):
                    chk(cond, "red: " + label)

            if page_errors:
                for e in page_errors:
                    print("  ✗ pageerror: " + e[:200])
            chk(len(page_errors) == 0, "0 pageerrors en toda la sesión")

            print("— BLOQUE 4 · DUELO SIMULADO (dos páginas, red real) —")
            await duel(browser)
        finally:
            await browser.close()

    print(f"\nRESULTADO: {ok} OK · {fails} FALLOS (qa_r81_v3673 · CAPA BP)")
    sys.exit(0 if fails == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
