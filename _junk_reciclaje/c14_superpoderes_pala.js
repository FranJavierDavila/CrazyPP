/* v3.6.28-POD1 · SUPERPODERES DE PALA DEL JUGADOR — ronda del dueño.
 * =====================================================================
 *  SISTEMA COMPLETO (petición del dueño, ronda 56):
 *  · CONCESIÓN: un rallye que SUPERA los 20 toques carga 1 superpoder
 *    al azar (nunca antes — «superados los 20 toques no antes»).
 *  · SELECTOR: flick lateral del joystick derecho — si hay poderes
 *    cargados cicla la selección y la VOZ dice el nombre (rápido, solo
 *    el nombre: «Imán», «Super Pala», «Super Efecto», «Portal»,
 *    «Clonación»); si no hay nada, la voz dice «Sin poder».
 *  · ACTIVACIÓN: gatillo del mando de la pala — el poder dura 10 s.
 *  · PODERES:
 *      - Super Pala: pala más grande y forgiving (reach extra + aura oro).
 *      - Imán: corrección de trayectoria — NUESTRO ataque SIEMPRE cae
 *        en la mesa del rival (siempre que vaya hacia su campo, aunque
 *        la dirección sea errónea). Admite golpes fuertes (el solver
 *        usa la velocidad real del golpe como techo, nunca la baja).
 *      - Super Efecto: SOLO en el intercambio (NUNCA en saques) y SOLO
 *        en NUESTROS golpes: la bola sale con efecto brutal y el bote
 *        en el campo rival dispara (ventaja sólo para el jugador).
 *      - Portal: rescate de tiros fuera — el ataque nuestro que iría
 *        fuera (largo/ancho) se re-direcciona por un portal a un punto
 *        legal de la mesa rival (destello violeta).
 *      - Super Poder Clonación: 2 palas fantasma (material Ghost azul
 *        translúcido) a ±50 cm del jugador. La derecha caza las bolas
 *        que se escapan por la derecha y la izquierda por la izquierda
 *        (SOLO si el jugador no las devuelve), con 90% de acierto.
 *        Además DESTRUYEN los poderes de molestia visual (globos del
 *        Clown, confeti): barren la escena reventándolos.
 *  · ÁRBITRO DE EXPRESIONES (REGLA del dueño para TODOS los rivales):
 *      5 toques _focused · 10 _picando · 15 _surprised · 20 _panic ·
 *      >20 aleatorio _loosing/_surprised/_panic · rival pierde punto
 *      _angry (+queja) · fallo del jugador _laughing (+burla) ·
 *      superpoder del rival _crazy · rival gana el punto _victory ·
 *      rival pierde el partido _defeated.
 *  Nada de esto toca el árbitro ni la física base: es una CAPA que se
 *  engancha por hooks del núcleo y jamás rompe el bucle (guards).
 * ===================================================================== */
export const PODER_DUR = 10;            // segundos de TODOS los poderes
export const UMBRAL_TOQUES = 20;        // concesión SOLO superados los 20
export const CLON_EXITO = 0.90;         // 90% de acierto de las palas clon
export const CLON_DIST = 0.50;          // 50 cm a cada lado del jugador

/* Catálogo: id → átomo de voz (banco ES/EN), nombre i18n y color de aura. */
const PODERES = [
  { id: 'pala',    voz: 'poder_pala',   nombre: 'nombre_pala',   aura: 0xffd24a },
  { id: 'iman',    voz: 'poder_iman',   nombre: 'nombre_iman',   aura: 0x57c7ff },
  { id: 'efecto',  voz: 'poder_efecto', nombre: 'nombre_efecto', aura: 0x7fb069 },
  { id: 'portal',  voz: 'poder_portal', nombre: 'nombre_portal', aura: 0xc07fff },
  { id: 'clon',    voz: 'poder_clon',   nombre: 'nombre_clon',   aura: 0x9fd8ff },
];

/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { DIMS } from './c02_cfg_escena.js';
import { createPaddleSim } from './c04_fisica_ccd.js';
import { computeShotVelocityReal } from './c05_colisiones_ia_golpeo.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

const tmpP1 = new THREE.Vector3();
const tmpP2 = new THREE.Vector3();

export function createPoderes(game) {
  const cargados = [];          // ids de poderes cargados (máx 6)
  let sel = 0;                  // índice seleccionado
  let activo = null;            // { id, t0 }
  let concedadoRally = false;   // 1 concesión por rallye
  let flickPrev = 0, flickCool = 0, sinCool = 0;
  let aura = null, auraMat = null;
  let emisivoBase = null;       // color emisivo original de la bola
  // --- clones ---
  let clonL = null, clonR = null;         // { pad, mesh }
  let clonCoolL = 0, clonCoolR = 0;
  let clonLimpiezaT = 0;
  // --- portal ---
  let portalChequeado = false;  // 1 rescate por golpe nuestro
  let portalFlash = null, portalFlashT = 0;

  const presente = () => !!(game.renderer && game.renderer.xr && game.renderer.xr.isPresenting);
  const enJuego = () => !game.inHall && !game.calib;
  const nom = (id) => { const p = PODERES.find((x) => x.id === id); return p ? T(p.nombre) : id; };

  /* ---------- visual: aura de la pala + tinte de la bola ---------- */
  function asegurarAura() {
    if (aura || !game.scene) return;
    auraMat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0.55,
      blending: THREE.AdditiveBlending, depthWrite: false });
    aura = new THREE.Mesh(new THREE.TorusGeometry(0.115, 0.009, 8, 36), auraMat);
    aura.visible = false;
    game.scene.add(aura);
  }
  function tinteBola(hex) {
    try {
      if (!game.ballMesh || !game.ballMesh.material) return;
      if (emisivoBase === null) emisivoBase = game.ballMesh.material.emissive.getHex();
      game.ballMesh.material.emissive.setHex(hex || emisivoBase || 0x555044);
    } catch { /* */ }
  }
  function apagarVisual() {
    if (aura) aura.visible = false;
    tinteBola(null);
    emisivoBase = null;
  }

  /* ---------- concesión / selección / activación ---------- */
  function concedir() {
    if (cargados.length >= 6) return;
    const p = PODERES[Math.floor(Math.random() * PODERES.length)];
    cargados.push(p.id);
    sel = cargados.length - 1;
    game.rules.message = T('poder_cargado', { n: nom(p.id) });
    try { game.audio.poderVoz(p.voz); } catch { /* */ }
    try { game.haptic(game.paddleHand, 0.55, 90); } catch { /* */ }
    window.setTimeout(() => { try { game.haptic(game.paddleHand, 0.4, 80); } catch { /* */ } }, 170);
    try { game.audio.swell(); } catch { /* */ }
  }

  function activar(id) {
    if (activo) return;
    const p = PODERES.find((x) => x.id === id);
    if (!p) return;
    activo = { id, t0: performance.now() / 1000 };
    game.rules.message = T('poder_activo', { n: nom(id) });
    try { game.audio.poderVoz(p.voz); } catch { /* */ }
    try { game.haptic(game.paddleHand, 0.5, 80); } catch { /* */ }
    window.setTimeout(() => { try { game.haptic(game.paddleHand, 0.75, 110); } catch { /* */ } }, 130);
    window.setTimeout(() => { try { game.haptic(game.paddleHand, 0.5, 90); } catch { /* */ } }, 300);
    asegurarAura();
    if (auraMat) auraMat.color.setHex(p.aura);
    const tintes = { iman: 0x2a6fd0, efecto: 0x2f8f3f, portal: 0x7a3fd0, pala: 0x8a6a10, clon: 0x3f7fbf };
    tinteBola(tintes[id] || null);
    if (id === 'clon') montarClones();
    if (id === 'portal') portalChequeado = false;
    try { game.audio.swell(); } catch { /* */ }
  }

  function desactivar() {
    if (!activo) return;
    const id = activo.id;
    game.rules.message = T('poder_fin', { n: nom(id) });
    activo = null;
    apagarVisual();
    if (id === 'clon') desmontarClones();
    if (id === 'pala') { try { game.controllerPaddles[game.paddleHand].extraReach = 0; } catch { /* */ } }
  }

  /* ---------- palas clon (Super Poder Clonación) ---------- */
  function montarClones() {
    if (!game.scene) return;
    desmontarClones();
    const mat = new THREE.MeshStandardMaterial({
      color: 0xbfe3ff, emissive: 0x5fa8ff, emissiveIntensity: 0.85,
      transparent: true, opacity: 0.42, roughness: 0.25, metalness: 0.1,
      depthWrite: false });
    const mk = (lado) => {
      const g = new THREE.Group();
      const hoja = new THREE.Mesh(new THREE.CylinderGeometry(0.0795, 0.0795, 0.012, 22), mat);
      hoja.rotation.x = Math.PI / 2;
      g.add(hoja);
      const mango = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.105, 0.028), mat);
      mango.position.y = -0.135;
      g.add(mango);
      g.visible = false;
      game.scene.add(g);
      const pad = createPaddleSim('player', game.paddleHand);
      pad.active = true;
      pad.pos.set(lado * CLON_DIST, 1.0, 0.55);
      return { pad, mesh: g, lado };
    };
    clonL = mk(-1);
    clonR = mk(1);
  }
  function desmontarClones() {
    for (const c of [clonL, clonR]) {
      if (!c) continue;
      try { game.scene.remove(c.mesh); } catch { /* */ }
      c.mesh.traverse((o) => { try { if (o.geometry) o.geometry.dispose(); } catch { /* */ } });
    }
    clonL = null; clonR = null;
  }

  /* Destruye los estorbos visuales (globos/confeti) mientras el clon vive. */
  function limpiezaVision() {
    if (!game.scene) return 0;
    let n = 0;
    const muertos = [];
    game.scene.traverse((o) => {
      if (n > 40 || muertos.length > 40) return;
      if (o.userData && o.userData.__clonMuerto) return;
      let ruta = '';
      try {
        const mp = o.material && o.material.map && o.material.map.image;
        ruta = (mp && (mp.src || mp.currentSrc || '')) || '';
      } catch { /* */ }
      const nombre = o.name || '';
      if (/(globo|confeti|balloon)/i.test(ruta) || /(globo|confeti|balloon)/i.test(nombre)) {
        if (o.isMesh || o.isSprite || o.isPoints) { muertos.push(o); }
      }
    });
    for (const o of muertos) {
      o.userData.__clonMuerto = true;
      o.visible = false;
      n++;
      window.setTimeout(() => {
        try {
          game.audio.playOsc(820, 160, 0.14, 'square', 0.14, (Math.random() - 0.5) * 1.4);
          game.audio.playNoise(0.08, 2400, 1.2, 0.1, 0, 'highpass');
        } catch { /* */ }
      }, 60 * n);
    }
    if (n) { try { game.haptic(game.paddleHand, 0.4, 60); } catch { /* */ } }
    return n;
  }

  /* ---------- IMÁN: corrección de trayectoria al golpe nuestro ---------- */
  function imanCorregir() {
    const b = game.ball;
    if (!b || !b.vel) return;
    // SÓLO ataques que van hacia el campo rival (el requisito del dueño:
    // «siempre que sea más o menos hacia su lado»)
    if (b.vel.z > -0.35) return;
    const ai = game.ai && game.ai.pos ? game.ai.pos.x : 0;
    // objetivo: mesa rival, lejos de donde está el rival
    const tz = DIMS.tableCenterZ - DIMS.tableHalfLength * (0.32 + Math.random() * 0.42);
    const tx = THREE.MathUtils.clamp((ai >= 0 ? -1 : 1) * (0.18 + Math.random() * 0.34), -0.6, 0.6);
    tmpP1.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const velHit = b.vel.length();
    const dist = tmpP2.copy(tmpP1).sub(b.pos).length();
    const tIn = THREE.MathUtils.clamp(dist / Math.max(4.5, velHit), 0.42, 0.9);
    const maxV = Math.max(6.8, velHit);       // NUNCA frena un golpe fuerte
    const v = computeShotVelocityReal(b.pos, tmpP1, tIn, maxV, null);
    if (v && Number.isFinite(v.x)) {
      b.vel.copy(v);
      if (b.spin) { b.spin.multiplyScalar(0.35); b.spin.x += 14; }  // vivo pero controlado
    }
  }

  /* ---------- SUPER EFECTO: efecto brutal SOLO en golpes nuestros ---------- */
  function efectoAplicar() {
    const b = game.ball;
    if (!b || !b.spin) return;
    // topspin agresivo hacia el campo rival (Magnus lo hunde y el bote
    // en la mesa rival DISPARA — bounceSpinKick de la física base) +
    // lateral aleatorio: la ventaja del bote es SÓLO nuestra.
    b.spin.x += 55 + Math.random() * 25;
    b.spin.y += (Math.random() - 0.5) * 46;
    const s = b.spin.length();
    if (s > DIMS.spinMax * 1.25) b.spin.multiplyScalar((DIMS.spinMax * 1.25) / s);
  }

  /* ---------- PORTAL: rescate del tiro que iba fuera ---------- */
  function portalRescate() {
    const b = game.ball;
    if (!b || !b.vel || game.rules.lastHitter !== 'player') return;
    if (b.vel.z >= 0 || portalChequeado) return;
    // predicción balística gruesa (gravedad + arrastre) del punto de caída
    const p = tmpP1.copy(b.pos), v = tmpP2.copy(b.vel);
    let aterriza = null;
    for (let i = 0; i < 220; i++) {
      const h = 0.012;
      v.y += DIMS.gravity * h;
      const sp = v.length();
      if (sp > 1e-6) v.multiplyScalar(Math.max(0, 1 - DIMS.airDragK * sp * h));
      p.addScaledVector(v, h);
      if (v.z >= 0) return;                       // ya no llega a la mesa rival
      if (p.y <= DIMS.tableTopY + DIMS.ballRadius && p.z < DIMS.tableCenterZ) { aterriza = p; break; }
    }
    if (!aterriza) return;
    const fuera = Math.abs(aterriza.x) > DIMS.tableHalfWidth - 0.02 ||
      aterriza.z < DIMS.tableCenterZ - DIMS.tableHalfLength + 0.01;
    if (!fuera) { portalChequeado = true; return; }  // iba dentro: no se toca
    // rescate: re-direccionar AHORA (por el portal) a un punto legal
    portalChequeado = true;
    const tz = DIMS.tableCenterZ - DIMS.tableHalfLength * (0.35 + Math.random() * 0.4);
    const tx = THREE.MathUtils.clamp((Math.random() - 0.5) * 0.9, -0.55, 0.55);
    tmpP1.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    const dist = tmpP2.copy(tmpP1).sub(b.pos).length();
    const v2 = computeShotVelocityReal(b.pos, tmpP1, THREE.MathUtils.clamp(dist / 5.2, 0.4, 0.8),
      Math.max(5.5, b.vel.length()), null);
    if (v2 && Number.isFinite(v2.x)) {
      b.vel.copy(v2);
      destelloPortal(b.pos);
      try {
        game.audio.playOsc(340, 980, 0.16, 'sine', 0.22, 0);
        game.audio.playOsc(980, 340, 0.2, 'sine', 0.16, 0);
      } catch { /* */ }
    }
  }
  function destelloPortal(pos) {
    if (!game.scene) return;
    if (!portalFlash) {
      portalFlash = new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.014, 8, 36),
        new THREE.MeshBasicMaterial({ color: 0xc07fff, transparent: true, opacity: 0.9,
          blending: THREE.AdditiveBlending, depthWrite: false }));
      game.scene.add(portalFlash);
    }
    portalFlash.position.copy(pos);
    portalFlash.lookAt(game.rig && game.rig.position ? game.rig.position.x : 0,
      pos.y, game.rig && game.rig.position ? game.rig.position.z : 2);
    portalFlash.visible = true;
    portalFlashT = 0.5;
  }

  /* ---------- CLONES: caza de la bola que se escapa ---------- */
  function clonesCazar() {
    const b = game.ball;
    if (!b || game.rules.lastHitter !== 'ai') return;
    const pad = game.controllerPaddles[game.paddleHand];
    if (!pad) return;
    // ¿se le escapa al jugador? (pasó la línea de la pala hacia atrás,
    // o cae ya sin que la pala esté cerca)
    const escapando = (b.vel.z > 0.45 && b.pos.z > pad.pos.z + 0.1) ||
      (b.pos.z > pad.pos.z + 0.28 && b.vel.z > -0.2);
    if (!escapando || b.__clonTocado) return;
    const lado = (b.pos.x - pad.pos.x) >= 0 ? clonR : clonL;
    if (!lado) return;
    const cool = lado.lado > 0 ? clonCoolR : clonCoolL;
    if (cool > 0) return;
    if (lado.lado > 0) clonCoolR = 1.0; else clonCoolL = 1.0;
    b.__clonTocado = true;                       // un intento por bola
    const exito = Math.random() < CLON_EXITO;    // 90% de acierto
    // punto de interceptación: un pelín por delante de la bola
    tmpP1.copy(b.pos).addScaledVector(b.vel, 0.045);
    tmpP1.y = Math.max(0.35, tmpP1.y);
    if (!exito) tmpP1.x += lado.lado * 0.16;     // fallo: llega tarde al lado
    lado.pad.prev.copy(lado.pad.pos);
    lado.pad.pos.copy(tmpP1);
    // swing del clon hacia el campo rival (la CCD hace el contacto real)
    lado.pad.vel.set((Math.random() - 0.5) * 0.8, 0.6, -3.6);
    lado.pad.velInst.copy(lado.pad.vel);
    lado.pad.normal.set(0, 0, -1);
    lado.pad.right.set(1, 0, 0);
    lado.pad.up.set(0, 1, 0);
    lado.pad.prevNormal.copy(lado.pad.normal);
    lado.pad.prevRight.copy(lado.pad.right);
    lado.pad.prevUp.copy(lado.pad.up);
    lado.pad.quatInit = true;
    lado.pad.__clonGolpe = true;
    lado.mesh.position.copy(tmpP1);
    lado.mesh.visible = true;
    if (exito) {
      try { game.haptic(game.paddleHand, 0.6, 90); } catch { /* */ }
      try { game.audio.swell(0.5); } catch { /* */ }
    }
  }

  /* ---------- hooks del núcleo ---------- */
  /** Golpe de PALA del jugador en el RALLY (lo llama c12 §5.5, nunca en
   *  saques — el árbitro está en 'rally'). Aquí aplican Imán y Efecto. */
  function onGolpeJugador() {
    if (!activo) return;
    if (activo.id === 'iman') imanCorregir();
    if (activo.id === 'efecto') efectoAplicar();
    if (activo.id === 'portal') portalChequeado = false;
  }

  /** Pads extra para la física este frame (clones activos y cazando). */
  function padsExtras(pads, presenting) {
    if (!activo || activo.id !== 'clon' || !presenting) return;
    for (const c of [clonL, clonR]) {
      if (c && c.pad.__clonGolpe && c.pad.cooldown <= 0.19) pads.push(c.pad);
    }
  }

  /** Fin de partido → expresión del rival + ovación. */
  function onFinPartido(winner) {
    rivalEstado(winner === 'player' ? 'defeated' : 'victory', 6);
  }

  /* ---------- EXPRESIONES (regla del dueño, todos los rivales) ---------- */
  let exprToques = -1, exprRandomT = 0, exprWarnT = 0;
  function rivalEstado(estado, dur) {
    try {
      const champs = game.champs;
      if (!champs || !champs.activeId) return;
      const m = champs.moduleIfLoaded(champs.activeId);
      if (m && typeof m.rivalEstado === 'function') m.rivalEstado(estado, dur);
    } catch { /* nunca rompe */ }
  }
  function expresionesUpdate(dt) {
    const r = game.rules;
    if (!r) return;
    // crazy: el cartel de «SUPERPODER ENTRANTE» del campeonato
    try {
      const warn = T('arc_power_warn');
      if (warn && r.message === warn) {
        if (exprWarnT <= 0) { rivalEstado('crazy', 3.2); exprWarnT = 4; }
      }
    } catch { /* */ }
    exprWarnT = Math.max(0, exprWarnT - dt);
    if (r.state !== 'rally') { exprToques = r.rallyHits; return; }
    const h = r.rallyHits;
    if (h !== exprToques) {
      const antes = exprToques;
      exprToques = h;
      if (antes < 5 && h >= 5) rivalEstado('focused', 3);
      if (antes < 10 && h >= 10) { rivalEstado('picando', 3); try { game.audio.swell(); } catch { /* */ } }
      if (antes < 15 && h >= 15) rivalEstado('surprised', 3);
      if (antes < 20 && h >= 20) rivalEstado('panic', 3);
      if (h > 20) {
        exprRandomT -= dt;
        if (exprRandomT <= 0) {
          exprRandomT = 2.4;
          const opts = ['loosing', 'surprised', 'panic'];
          rivalEstado(opts[Math.floor(Math.random() * opts.length)], 2.2);
        }
      }
    }
  }

  /** Punto del árbitro → expresión + sonido según la REGLA del dueño. */
  function onPunto(it) {
    if (!it) return;
    if (it.winner === 'player') {
      rivalEstado('angry', 2.6);
      try { game.audio.queja(); } catch { /* */ }
    } else {
      const falloMio = ['out', 'wall', 'net_stay', 'own_you', 'serve_net', 'serve_out',
        'serve_net_touch', 'dblhit', 'volley', 'back_you'].indexOf(it.cause) >= 0;
      if (falloMio) {
        rivalEstado('laughing', 2.6);
        try { game.audio.burla(); } catch { /* */ }
      } else {
        rivalEstado('victory', 2.6);
      }
    }
  }

  /* ---------- bucle ---------- */
  function update(dt, now) {
    flickCool = Math.max(0, flickCool - dt);
    sinCool = Math.max(0, sinCool - dt);
    clonCoolL = Math.max(0, clonCoolL - dt);
    clonCoolR = Math.max(0, clonCoolR - dt);
    if (portalFlashT > 0 && portalFlash) {
      portalFlashT -= dt;
      portalFlash.scale.setScalar(1 + (0.5 - portalFlashT) * 2.4);
      portalFlash.material.opacity = Math.max(0, portalFlashT * 1.8);
      if (portalFlashT <= 0) portalFlash.visible = false;
    }
    expresionesUpdate(dt);
    // concesión: rallye que SUPERA los 20 toques (nunca antes)
    const r = game.rules;
    if (r && r.state === 'rally') {
      if (r.rallyHits <= 1) concedadoRally = false;
      if (!concedadoRally && r.rallyHits > UMBRAL_TOQUES) {
        concedadoRally = true;
        concedir();
      }
    }
    if (!presente() || !enJuego()) { if (aura) aura.visible = false; return; }

    // entrada: flick lateral = selección · gatillo = activar
    const Ri = game.handIndex('right');
    const st = game.stickAxis(Ri);
    if (flickCool <= 0 && Math.abs(st.x) > 0.62 && Math.abs(flickPrev) <= 0.62) {
      flickCool = 0.3;
      if (!cargados.length) {
        if (sinCool <= 0) { sinCool = 1.6; try { game.audio.poderVoz('poder_sin'); } catch { /* */ } }
      } else {
        sel = (sel + (st.x > 0 ? 1 : -1) + cargados.length) % cargados.length;
        const p = PODERES.find((x) => x.id === cargados[sel]);
        if (p) { try { game.audio.poderVoz(p.voz); } catch { /* */ } }
        try { game.haptic(game.paddleHand, 0.25, 40); } catch { /* */ }
      }
    }
    flickPrev = st.x;
    if (cargados.length && !activo && game.readButton(Ri, 0)) {
      const id = cargados.splice(sel, 1)[0];
      sel = Math.min(sel, Math.max(0, cargados.length - 1));
      activar(id);
    }

    // timer del poder activo
    if (activo && now - activo.t0 >= PODER_DUR) desactivar();

    // efectos continuos
    if (activo) {
      const pad = game.controllerPaddles[game.paddleHand];
      if (pad && aura) {
        aura.visible = true;
        aura.position.copy(pad.pos).addScaledVector(pad.up, DIMS.bladeCenterUp);
        aura.rotation.y = now * 2.1;
        aura.rotation.x = Math.sin(now * 1.3) * 0.5;
      }
      if (activo.id === 'pala') {
        try { pad.extraReach = 0.1; } catch { /* */ }
      }
      if (activo.id === 'portal') portalRescate();
      if (activo.id === 'clon') {
        clonesCazar();
        clonLimpiezaT -= dt;
        if (clonLimpiezaT <= 0) { clonLimpiezaT = 0.4; limpiezaVision(); }
        // clones siguen al jugador con suavidad (Ghost vivos)
        if (pad) {
          for (const c of [clonL, clonR]) {
            if (!c) continue;
            tmpP1.copy(pad.pos); tmpP1.y = Math.max(0.35, tmpP1.y);
            tmpP1.x += c.lado * CLON_DIST;
            c.pad.prev.copy(c.pad.pos);
            c.pad.pos.lerp(tmpP1, 0.14);
            if (!c.pad.__clonGolpe || c.pad.cooldown <= 0) c.mesh.visible = presenting;
            c.mesh.position.copy(c.pad.pos);
            c.mesh.rotation.y = Math.PI;
          }
        }
      }
    }
  }

  function reset() {
    cargados.length = 0;
    sel = 0;
    desactivar();
    concedadoRally = false;
  }

  return {
    update, padsExtras, onGolpeJugador, onPunto, onFinPartido, reset,
    get activoId() { return activo ? activo.id : null; },
    get cargados() { return cargados.length; },
    get seleccionado() { return cargados[sel] || null; },
  };
}
