export function createRoom() {
  const g = new THREE.Group();
  const zC = (DIMS.roomBackZ + DIMS.roomFrontZ) / 2;
  const depth = DIMS.roomBackZ - DIMS.roomFrontZ;

  const floorMat = new THREE.MeshStandardMaterial({ color: COLORS.floor, roughness: 0.9, metalness: 0.05 });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth), floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.set(0, 0, zC);
  floor.receiveShadow = true;
  g.add(floor);

  const grid = new THREE.GridHelper(Math.max(DIMS.roomHalfX * 2, depth), 20, 0x4a4038, 0x2c2622);
  grid.position.set(0, 0.002, zC);
  g.add(grid);

  // refs para los TEMAS DE SALA (v2.14): applyTheme recolorea en vivo
  g.userData.floorMat = floorMat;
  g.userData.grid = grid;

  // v2.85: CADA PARED tiene SU material (antes compartían uno) para que el
  // campeonato activo pueda vestirlas con arte distinto por plano (room).
  // Visualmente idéntico al núcleo clásico: mismos color/roughness y el
  // applyTheme recolorea las cuatro. Orden FIJO: [izq, der, trasera, frontal].
  const wallMats = [0, 1, 2, 3].map(() => new THREE.MeshStandardMaterial({ color: COLORS.wall, roughness: 1 }));
  g.userData.wallMats = wallMats;
  g.userData.wallMat = wallMats[0];   // compat con referencias antiguas
  const mkWall = (i, w, h, pos, rotY) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMats[i]);
    m.position.copy(pos);
    m.rotation.y = rotY;
    g.add(m);
  };
  const cx = DIMS.roomHalfX;
  mkWall(0, depth, DIMS.roomHeight, new THREE.Vector3(-cx, DIMS.roomHeight / 2, zC), Math.PI / 2);
  mkWall(1, depth, DIMS.roomHeight, new THREE.Vector3(cx, DIMS.roomHeight / 2, zC), -Math.PI / 2);
  mkWall(2, DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomBackZ), Math.PI);
  mkWall(3, DIMS.roomHalfX * 2, DIMS.roomHeight, new THREE.Vector3(0, DIMS.roomHeight / 2, DIMS.roomFrontZ), 0);

  const ceil = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.roomHalfX * 2, depth),
    new THREE.MeshStandardMaterial({ color: 0x14171b, roughness: 1 }),
  );
  ceil.rotation.x = Math.PI / 2;
  ceil.position.set(0, DIMS.roomHeight, zC);
  g.add(ceil);
  g.userData.ceilMat = ceil.material;

  const panelMat = new THREE.MeshBasicMaterial({ color: 0xf5efe2 });
  g.userData.panelMat = panelMat;
  g.userData.panels = [];   // v2.85: refs para ocultarlos bajo el arte del techo
  for (const px of [-1.4, 1.4]) {
    const panel = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 2.4), panelMat);
    panel.rotation.x = Math.PI / 2;
    panel.position.set(px, DIMS.roomHeight - 0.01, -1.2);
    g.add(panel);
    g.userData.panels.push(panel);
  }

  const stripMat = new THREE.MeshBasicMaterial({ color: COLORS.accentAmber });
  g.userData.stripMat = stripMat;
  g.userData.strips = [];   // v2.85: refs para ocultarlas bajo el arte de las paredes
  for (const sx of [-cx + 0.02, cx - 0.02]) {
    const strip = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.02, depth * 0.9), stripMat);
    strip.position.set(sx, 2.1, zC);
    g.add(strip);
    g.userData.strips.push(strip);
  }

  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.26, 0.33, 48),
    new THREE.MeshBasicMaterial({
      color: COLORS.accentAmber, transparent: true, opacity: 0.45, side: THREE.DoubleSide,
    }),
  );
  ring.rotation.x = -Math.PI / 2;
  ring.position.set(0, 0.004, 0);
  g.add(ring);
  g.userData.ringMat = ring.material;

  // v2.30: FUERA las vallas publicitarias del suelo — no aportan nada y
  // distraen al jugador (petición expresa: "fuera todos los carteles del
  // suelo con los mensajes"). La pista queda limpia.

  return g;
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { COLORS, DIMS } from './c02_cfg_escena.js';
import { tmpV } from './c04_fisica_ccd.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

export function createTable() {
  const g = new THREE.Group();
  const topY = DIMS.tableTopY;
  const L = DIMS.tableHalfLength * 2;
  const W = DIMS.tableHalfWidth * 2;

  const topMat = new THREE.MeshStandardMaterial({ color: COLORS.tableBlue, roughness: 0.55, metalness: 0.05 });
  const top = new THREE.Mesh(new THREE.BoxGeometry(W, DIMS.tableThickness, L), topMat);
  top.name = 'ppTableTop';   // v2.56: los campeonatos pueden teñir la superficie (y restaurarla)
  top.position.set(0, topY - DIMS.tableThickness / 2, DIMS.tableCenterZ);
  top.castShadow = true;
  top.receiveShadow = true;
  g.add(top);

  const lineMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.6 });
  const lineH = 0.002;
  const mkLine = (w, d, x, z) => {
    const m = new THREE.Mesh(new THREE.BoxGeometry(w, lineH, d), lineMat);
    m.position.set(x, topY + lineH / 2 - 0.0005, DIMS.tableCenterZ + z);
    g.add(m);
  };
  mkLine(W, 0.02, 0, -DIMS.tableHalfLength + 0.01);
  mkLine(W, 0.02, 0, DIMS.tableHalfLength - 0.01);
  mkLine(0.02, L, -DIMS.tableHalfWidth + 0.01, 0);
  mkLine(0.02, L, DIMS.tableHalfWidth - 0.01, 0);
  mkLine(0.003, L, 0, 0);

  const frameMat = new THREE.MeshStandardMaterial({ color: COLORS.frame, roughness: 0.7 });
  const apron = new THREE.Mesh(new THREE.BoxGeometry(W * 0.96, 0.1, 0.03), frameMat);
  apron.position.set(0, topY - DIMS.tableThickness - 0.06, DIMS.tableCenterZ - DIMS.tableHalfLength + 0.05);
  // v2.87: nombres ppTableApron / ppTableLeg para que los campeonatos tiñan
  // el MARCO (mismo patrón que ppTableTop de v2.56). Sólo nombres aditivos.
  apron.name = 'ppTableApron';
  g.add(apron);
  const apron2 = apron.clone();
  apron2.position.z = DIMS.tableCenterZ + DIMS.tableHalfLength - 0.05;
  g.add(apron2);

  for (const lx of [-W / 2 + 0.12, W / 2 - 0.12]) {
    for (const lz of [-L / 2 + 0.15, L / 2 - 0.15]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.06, topY - DIMS.tableThickness, 0.06), frameMat);
      leg.position.set(lx, (topY - DIMS.tableThickness) / 2, DIMS.tableCenterZ + lz);
      leg.castShadow = true;
      leg.name = 'ppTableLeg';    // v2.87
      g.add(leg);
    }
  }

  const netCanvas = document.createElement('canvas');
  netCanvas.width = 256;
  netCanvas.height = 64;
  const nctx = netCanvas.getContext('2d');
  if (nctx) {
    nctx.clearRect(0, 0, 256, 64);
    nctx.strokeStyle = 'rgba(20,22,25,0.9)';
    nctx.lineWidth = 2;
    for (let x = 0; x <= 256; x += 10) {
      nctx.beginPath(); nctx.moveTo(x, 0); nctx.lineTo(x, 64); nctx.stroke();
    }
    for (let y = 0; y <= 64; y += 10) {
      nctx.beginPath(); nctx.moveTo(0, y); nctx.lineTo(256, y); nctx.stroke();
    }
  }
  const netTex = new THREE.CanvasTexture(netCanvas);
  netTex.wrapS = THREE.RepeatWrapping;
  netTex.wrapT = THREE.RepeatWrapping;
  netTex.repeat.set(6, 1.2);

  const netMesh = new THREE.Mesh(
    new THREE.PlaneGeometry(DIMS.netHalfWidth * 2, DIMS.netTopY - topY),
    new THREE.MeshBasicMaterial({ map: netTex, transparent: true, side: THREE.DoubleSide, alphaTest: 0.05 }),
  );
  netMesh.position.set(0, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
  g.add(netMesh);

  const band = new THREE.Mesh(
    new THREE.BoxGeometry(DIMS.netHalfWidth * 2, 0.014, 0.006),
    new THREE.MeshStandardMaterial({ color: 0xf2f2f2, roughness: 0.5 }),
  );
  band.position.set(0, DIMS.netTopY, DIMS.tableCenterZ);
  g.add(band);

  const postMat = new THREE.MeshStandardMaterial({ color: 0x30343a, roughness: 0.4, metalness: 0.6 });
  for (const px of [-DIMS.netHalfWidth, DIMS.netHalfWidth]) {
    const post = new THREE.Mesh(
      new THREE.CylinderGeometry(0.012, 0.012, DIMS.netTopY - topY + 0.02, 12),
      postMat,
    );
    post.position.set(px, topY + (DIMS.netTopY - topY) / 2, DIMS.tableCenterZ);
    g.add(post);
  }

  return g;
}

export function createBall() {
  const mesh = new THREE.Mesh(
    new THREE.SphereGeometry(DIMS.ballRadius, 48, 32),
    new THREE.MeshStandardMaterial({
      color: COLORS.ball, roughness: 0.35, emissive: 0x555044, emissiveIntensity: 0.35,
    }),
  );
  mesh.castShadow = true;

  const TRAIL_N = 22;
  const positions = new Float32Array(TRAIL_N * 3);
  const colors = new Float32Array(TRAIL_N * 3);
  const ages = new Float32Array(TRAIL_N);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
  const trail = new THREE.Points(
    geo,
    new THREE.PointsMaterial({
      color: 0xffffff, size: 0.02, transparent: true, opacity: 0.55,
      vertexColors: true, depthWrite: false,
    }),
  );
  let idx = 0;
  const tmpSpinCross = new THREE.Vector3();
  /** Estela "de retransmisión": color según el EFECTO de la bola.
   *  naranja = lift/topspin (la Magnus la hunde), azul = slice/backspin
   *  (flota), violeta = lateral. Se desvanece con la edad del punto.
   *  r61 · ESTELA DE PODER: si el juego pasa un tinte (poder de pala
   *  ACTIVO), la estela viste SU firma y el color por spin pasa a ser el
   *  respaldo — un vistazo a la bola y sabes qué poder está corriendo. */
  const trailUpdate = (ball, dt, tint) => {
    positions[idx * 3] = mesh.position.x;
    positions[idx * 3 + 1] = mesh.position.y;
    positions[idx * 3 + 2] = mesh.position.z;
    ages[idx] = 0;
    let r = 0.75, g = 0.75, b = 0.75;
    if (tint && tint.length === 3) {
      // firma del poder ACTIVO (el núcleo la prepara ya lerp-eada)
      r = tint[0]; g = tint[1]; b = tint[2];
    } else if (ball && ball.spin && ball.vel) {
      tmpSpinCross.crossVectors(ball.spin, ball.vel);   // dirección de la Magnus
      const lift = tmpSpinCross.y;                      // + flota · - se hunde
      const force = Math.min(1, Math.abs(lift) / 9);
      if (force > 0.06) {
        if (lift < 0) {        // topspin → naranja
          r = 0.55 + 0.45 * force; g = 0.32 * force; b = 0.12 * force;
        } else {               // backspin → azul
          r = 0.16 * force; g = 0.55 * force; b = 0.55 + 0.45 * force;
        }
      }
      const side = Math.abs(ball.spin.y) / 18;
      if (side > 0.35 && force <= 0.06) {   // lateral → violeta
        r = 0.55; g = 0.3; b = 0.75;
      }
    }
    colors[idx * 3] = r;
    colors[idx * 3 + 1] = g;
    colors[idx * 3 + 2] = b;
    idx = (idx + 1) % TRAIL_N;
    for (let i = 0; i < TRAIL_N; i++) {
      ages[i] += dt;
      const fade = Math.max(0, 1 - ages[i] / 0.42);
      colors[i * 3] *= 0.86 + 0.14 * fade;
      colors[i * 3 + 1] *= 0.86 + 0.14 * fade;
      colors[i * 3 + 2] *= 0.86 + 0.14 * fade;
    }
    geo.attributes.position.needsUpdate = true;
    geo.attributes.color.needsUpdate = true;
  };

  return { mesh, trail, trailUpdate };
}

export function createBlobShadow() {
  const m = new THREE.Mesh(
    new THREE.CircleGeometry(0.05, 20),
    new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.3, depthWrite: false }),
  );
  m.rotation.x = -Math.PI / 2;
  m.renderOrder = 2;
  return m;
}

/* =====================================================================
 *  v2.80 · DECORADO DE CAMPEONATOS — TROQUELES DE CARTÓN
 *  ---------------------------------------------------------------------
 *  v2.80 · TROQUELES DE CARTÓN — DECORADO POR CAMPEONATO.
 *  Cada campeonato decora la sala con SUS troqueles: el módulo ACTIVO
 *  declara su config en «decor» (locura/index.js y magia/index.js desde
 *  v2.81) y el núcleo —
 *  que sigue sin conocer campeonato alguno — se la lee y monta los
 *  recortes como troqueles de cartón apoyados en el suelo. Un módulo
 *  sin «decor» no muestra troquel alguno (v2.81: ambos campeonatos
 *  traen el suyo — el payaso en locura, el wizard en magia —).
 *  · ANCLADOS AL RIG en offsets fijos respecto a la MESA (el recentrado
 *    de la Quest los mueve con la sala, lección v2.62) y orientados
 *    hacia el punto del JUGADOR (rotación fija, son cartón rígido).
 *  · La textura se usa TAL CUAL: el PNG del artista viene recortado a
 *    SU propia transparencia (v2.80, sin borde añadido) y el plano
 *    cuelga de la base, que queda EXACTAMENTE en el suelo.
 *  · NO tapan nada: marcador y portal (centro del fondo), mapa de
 *    etapas (pared izquierda) y RIVAL (zona derecha del fondo quedan
 *    fuera de los troqueles).
 *  · INTERACTIVOS sin tocar la física de la bola: si la bola pasa cerca
 *    o el jugador roza un troquel con la pala, el cartón se tambalea
 *    (muelle amortiguado anclado a la base) con su "toc" de cartón.
 *    En reposo un vaivén sutil hace que el decorado respire.
 *  · Al cambiar de campeonato (leaveAll/launch) el set anterior se
 *    destruye (dispose de GPU) y se construye el del módulo nuevo; si
 *    el activo no trae decorado, la sala queda limpia.
 *  · Sin textura (file:// o ruta rota) el troquel simplemente no nace.
 * ===================================================================== */
export function createChampDecor(game) {
  const group = new THREE.Group();     // se añade al RIG una sola vez
  group.visible = false;
  let builtFor = null;                 // activeId del set construido (null = aún nada)
  let set = null;                      // { pieces, disposables } del campeonato activo
  const loader = new THREE.TextureLoader();
  let maxAniso = 4;
  try { maxAniso = game.renderer.capabilities.getMaxAnisotropy(); } catch { /* */ }

  function disposeSet() {
    group.clear();
    if (set) for (const d of set.disposables) { try { d.dispose(); } catch { /* */ } }
    set = null;
  }

  /** Construye el decorado del campeonato «id» leyendo mod.decor. */
  function buildFor(id) {
    disposeSet();
    builtFor = id;
    const mod = id ? game.champs.moduleIfLoaded(id) : null;
    const cfg = (mod && mod.decor && Array.isArray(mod.decor.pieces)) ? mod.decor : null;
    if (!cfg || !cfg.pieces.length) return;    // campeonato sin troqueles: sala limpia
    const base = 'championships/' + id + '/';  // rutas relativas a SU carpeta
    const mine = { pieces: [], disposables: [] };
    set = mine;
    for (const pc of cfg.pieces) {
      const p = {
        cfg: pc, holder: null, panel: null, h: pc.h || 1, w: 1,
        angX: 0, avX: 0, angZ: 0, avZ: 0, cool: 0,
        phase: Math.random() * Math.PI * 2, ready: false,
      };
      mine.pieces.push(p);
      loader.load(base + (pc.file || ''), (tex) => {
        if (set !== mine) { try { tex.dispose(); } catch { /* */ } return; }  // set ya sustituido
        try {
          tex.colorSpace = THREE.SRGBColorSpace;
          tex.anisotropy = maxAniso;
          const img = tex.image || {};
          const aspect = (img.width && img.height) ? (img.width / img.height) : 1;
          p.h = pc.h || 1;
          p.w = p.h * aspect;
          mine.disposables.push(tex);

          // panel con el pivote EN LA BASE: el tambaleo parte del suelo
          const pg = new THREE.Group();
          const mat = new THREE.MeshStandardMaterial({
            map: tex, transparent: true, alphaTest: 0.5,
            side: THREE.DoubleSide, roughness: 0.95, metalness: 0,
          });
          const plane = new THREE.Mesh(new THREE.PlaneGeometry(p.w, p.h), mat);
          plane.position.y = p.h / 2;          // base del arte en y=0 (toca suelo)
          plane.castShadow = true;
          // sombra con la FORMA del recorte (no del quad entero)
          plane.customDepthMaterial = new THREE.MeshDepthMaterial({
            depthPacking: THREE.RGBADepthPacking, map: tex, alphaTest: 0.5,
          });
          pg.add(plane);
          // pie de apoyo (caballete de cartón, como los troqueles reales)
          const leg = new THREE.Mesh(
            new THREE.BoxGeometry(p.w * 0.42, 0.022, 0.26),
            new THREE.MeshStandardMaterial({ color: 0x9a7448, roughness: 1 }),
          );
          leg.position.set(0, 0.012, -0.11);
          leg.rotation.x = 0.55;
          pg.add(leg);

          const holder = new THREE.Group();
          holder.add(pg);
          holder.position.set(pc.x || 0, 0, pc.z || 0);
          // ORIENTACIÓN FIJA hacia el punto donde se coloca el jugador
          holder.rotation.y = Math.atan2(-(pc.x || 0), 0.55 - (pc.z || 0));
          group.add(holder);

          // sombra suave pintada bajo el troquel (patrón del blob de la bola)
          const blob = new THREE.Mesh(
            new THREE.CircleGeometry(Math.max(p.w * 0.55, 0.34), 22),
            new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.24, depthWrite: false }),
          );
          blob.rotation.x = -Math.PI / 2;
          blob.position.set(pc.x || 0, 0.004, pc.z || 0);
          blob.renderOrder = 2;
          group.add(blob);

          mine.disposables.push(plane.geometry, mat, plane.customDepthMaterial,
            leg.geometry, leg.material, blob.geometry, blob.material);
          p.holder = holder;
          p.panel = pg;
          p.ready = true;
        } catch { /* el decorado NUNCA rompe el juego */ }
      }, undefined, () => { /* sin textura: el troquel no nace (file://) */ });
    }
  }

  const tmpV = new THREE.Vector3();
  const knock = (x, strong) => {
    const pan = THREE.MathUtils.clamp(x / 3, -0.9, 0.9);
    game.audio.playOsc(150, 88, 0.11, 'triangle', strong ? 0.18 : 0.14, pan);
    game.audio.playNoise(0.07, 720, 1.1, strong ? 0.12 : 0.09, pan, 'lowpass');
  };
  return {
    group,
    /** Piezas del set ACTIVO (lectura; [] si el campeonato no trae decor). */
    get pieces() { return set ? set.pieces : []; },
    /** Campeonato del set construido ('' = sala sin decorado). */
    get builtFor() { return builtFor || ''; },
    /** Reconstrucción perezosa al cambiar de campeonato + animación viva.
     *  Visible SIEMPRE con el campeonato ACTIVO que declara decor (r70:
     *  también con passthrough — el dueño quiere sus troqueles siempre). */
    update(dt, now) {
      const activeId = (game.champs && game.champs.activeId) || '';
      if (activeId !== builtFor) buildFor(activeId);
      // v2.80: visible sólo si el campeonato activo TRAE decor (v2.81:
      // locura y magia lo traen — cada uno monta SOLO el suyo al activarse).
      // r70 · VISIBLE SIEMPRE, también con passthrough (inAR): el dueño
      // insiste en que los troqueles «han desaparecido» — jugaba con el
      // passthrough del Quest y la condición !game.inAR los escondía
      // SIEMPRE en esas sesiones (la QA headless no lo veía: inAR=false).
      // Los troqueles son cartón apoyado en el suelo del JUGADOR: con
      // passthrough quedan en su sala real, que es donde los quiere.
      const want = !!(set && set.pieces.length) &&
        !game.champDecorHidden;   // v2.95: las pruebas pueden taparlo
      if (group.visible !== want) group.visible = want;
      if (!want || !set) return;
      for (const p of set.pieces) {
        if (!p.ready) continue;
        p.cool = Math.max(0, p.cool - dt);
        // muelles amortiguados sobre la base
        p.avX += (-34 * p.angX - 3.1 * p.avX) * dt;
        p.avZ += (-30 * p.angZ - 3.0 * p.avZ) * dt;
        p.angX = THREE.MathUtils.clamp(p.angX + p.avX * dt, -0.22, 0.22);
        p.angZ = THREE.MathUtils.clamp(p.angZ + p.avZ * dt, -0.26, 0.26);
        p.panel.rotation.x = p.angX;
        p.panel.rotation.z = p.angZ + Math.sin(now * 0.9 + p.phase) * 0.006 * p.cfg.sway;

        if (p.cool > 0) continue;
        // 1) la bola pasa cerca → el cartón se tambalea (la bola NO se toca)
        const bp = game.ball.pos;
        if (Math.hypot(bp.x - p.cfg.x, bp.z - p.cfg.z) < 0.5 && bp.y < p.h + 0.25) {
          p.avX += (game.ball.vel.z > 0 ? -1 : 1) * (1.1 + Math.random() * 0.5);
          p.avZ += (Math.random() - 0.5) * 1.4;
          p.cool = 0.8;
          knock(p.cfg.x, false);
          continue;
        }
        // 2) el jugador roza el troquel con la pala → empujón + háptica
        for (const sim of game.controllerPaddles) {
          if (!sim || !sim.pos || sim.pos.lengthSq() < 1e-4) continue;
          tmpV.copy(sim.pos);
          if (Math.hypot(tmpV.x - p.cfg.x, tmpV.z - p.cfg.z) < 0.55 && tmpV.y < p.h + 0.2) {
            p.avZ += (tmpV.x > p.cfg.x ? 1 : -1) * (1.5 + Math.random() * 0.6);
            p.avX += (Math.random() - 0.5) * 0.8;
            p.cool = 0.5;
            knock(p.cfg.x, true);
            try { game.haptic(sim.index, 0.35, 40); } catch { /* */ }
            break;
          }
        }
      }
    },
  };
}

/* =====================================================================
 *  v2.85 · DECORADO DE SALA del campeonato ACTIVO («room»)
 *  ---------------------------------------------------------------------
 *  Cada campeonato puede VESTIR LOS 6 PLANOS de la sala (suelo, techo y
 *  las 4 paredes) declarando en su módulo:
 *
 *    room: {
 *      floor: 'assets/room/suelo.jpg',   ceil: 'assets/room/techo.jpg',
 *      back:  'assets/room/fondo.jpg',   // trasera (detrás del jugador)
 *      front: 'assets/room/frente.jpg',  // pared del rival
 *      left:  'assets/room/izquierda.jpg',
 *      right: 'assets/room/derecha.jpg',
 *      variants: {                       // OPCIONAL: mood por etapa
 *        final: { tint: 0xb06050 },      //   teñido multiplicativo
 *      },
 *    }
 *
 *  Rutas RELATIVAS a la carpeta del campeonato (como «decor»). Cada clave
 *  es independiente: si falta, ese plano VISTE EL ARTE POR DEFECTO DEL
 *  PARTIDO (v3.6.29, assets/partido/ — antes quedaba con el color del
 *  tema). El sistema es del núcleo (patrón createChampDecor v2.80): se monta al
 *  activar el campeonato, se destruye (dispose GPU) al salir y un fallo
 *  de carga NUNCA rompe el juego (file:// incluido). Los complementos de
 *  la sala clásica que ensuciarían el arte (rejilla del suelo, paneles
 *  luminosos del techo, tiras ámbar de las paredes) se ocultan SOLO
 *  mientras haya arte y vuelven solos al salir. El módulo puede cambiar
 *  el mood por etapa con game.champRoom.useVariant('clave'|null).
 *  ===================================================================== */
/* =====================================================================
 *  v3.0.9-HALL1 · HALL DEL ANFITRIÓN — la estancia donde NACE la sesión
 *  VR: entrar al juego ya no te planta en la cancha vacía sino en la
 *  estancia del anfitrión, que se decora sola con lo conseguido
 *  (insignias de campeonatos, logros CRAZY, PRO CIRCUITO y pieles de
 *  pala). El menú principal se abre aquí delante; al arrancar un modo
 *  el guardián del bucle (exitHall) devuelve al jugador a la cancha.
 *  La estancia vive a 13 m de la cancha: la distancia (y el hecho de
 *  renderizar sólo una de las dos) las aíslan por completo.
 *  ===================================================================== */
