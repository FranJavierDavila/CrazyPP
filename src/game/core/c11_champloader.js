export class ChampLoader {
  constructor(game) {
    this.game = game;
    // v2.125: entries lleva { id, folder, title, storage, eager, estado,
    //   manifest, error } — el manifest YA PARSEADO viaja al módulo vía
    //   ctx.manifest (adiós al doble fetch obligatorio).
    this.entries = [];
    this.modules = {};      // id -> módulo importado (perezoso)
    this.activeId = '';     // '' = ningún campeonato externo activo
    this.replayHover = -1;  // v2.96: nodo del mapa apuntado con la pala (-1 = ninguno)
    this._loadIndex();
  }

  get active() { return !!this.activeId; }
  get mod() { return this.activeId ? (this.modules[this.activeId] || null) : null; }

  /** v2.125 · ID del campeonato de PORTADA (BSO del núcleo, rankings 2D/VR):
   *  el primero marcado eager en el índice — sustituye a los literales
   *  'locura' repartidos por el núcleo (descubrimiento dinámico real). */
  get portadaId() {
    const e = this.entries.find((x) => x.eager);
    return e ? e.id : 'locura';
  }

  /** ¿Hay una PRUEBA externa con la bola tomada? (El núcleo consulta
   *  SIEMPRE antes la prueba de La Locura: arkanoid tiene prioridad.) */
  get testActive() {
    const m = this.mod;
    return !!(m && typeof m.testActive === 'function' && m.testActive());
  }

  _loadIndex() {
    // file:// no puede fetchear el índice: sin botones y sin ruido en
    // consola (lección v2.52). El juego local sigue igual que siempre.
    if (typeof location !== 'undefined' && !/^https?:$/.test(location.protocol)) return;
    fetch('championships/championships.json')
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error('sin índice'))))
      .then(async (idx) => {
        const list = (idx && Array.isArray(idx.championships)) ? idx.championships : [];
        for (const raw of list) {
          // v2.69: cada entrada es "id" o { id, eager } — eager importa e
          // inicializa el módulo AL ARRANCAR (sin lanzarlo): La Locura
          // existe desde el primer frame, igual que hasta v2.68.
          // v2.125: la entrada también puede llevar "estado" (el del ciclo
          // de vida); el del manifest manda si lo declara.
          const ent = (typeof raw === 'string') ? { id: raw } : (raw || {});
          const id = String(ent.id || '');
          if (!/^[a-z0-9_-]+$/i.test(id)) continue;   // id seguro (sin ../)
          try {
            const r2 = await fetch(`championships/${id}/manifest.json`);
            const man = r2.ok ? await r2.json() : null;
            if (!man) continue;
            // v2.125 · CONTRATO: un manifest de un contrato futuro no se
            // integra (y queda VISIBLE, no mudo).
            const contrato = man.contract || 1;
            if (contrato > 1) {
              console.warn(`[champs] ${id} declara contract ${contrato} > 1 ` +
                '(núcleo más viejo que el campeonato): no se integra');
              this.entries.push({
                id, folder: `championships/${id}/`,
                title: man.title || { es: id, en: id }, storage: man.storage || '',
                eager: false, estado: 'incompatible', manifest: man,
                error: `contract ${contrato} > 1`,
              });
              continue;
            }
            // v2.125 · CICLO DE VIDA: sólo "publicado" sale en el menú;
            // borrador/validación/listo se cargan bajo demanda (previsualización
            // con ?champ=<id>); desactivado ni eso.
            const estado = man.estado || ent.estado || 'publicado';
            if (estado === 'desactivado') continue;
            this.entries.push({
              id,
              folder: `championships/${id}/`,
              title: man.title || { es: id, en: id },
              storage: man.storage || '',
              eager: !!ent.eager,
              estado,
              manifest: man,
              error: null,
            });
          } catch (e) { /* carpeta incompleta: se ignora sola */ }
        }
        // v2.69: módulos eager — importar SIN lanzar (init puede devolver
        // promesa: el campeonato fusiona su data.json antes de estar listo)
        for (const e of this.entries) {
          if (!e.eager) continue;
          try { await this.preload(e.id); }
          catch (err) { console.warn('[champs.eager] ' + e.id, err); }
        }
        // v2.125 · PREVISUALIZACIÓN AISLADA: ?champ=<id> lanza un campeonato
        // aunque esté en borrador/validación (jamás altera el menú público).
        try {
          const q = new URLSearchParams(location.search).get('champ');
          const ent = q && this.entries.find((x) => x.id === q && x.estado !== 'incompatible');
          if (ent) {
            console.info('[champs] previsualización de ' + q);
            this.launch(q);
          }
        } catch (e) { /* */ }
        // el menú pudo dibujarse antes de llegar la carpeta: repíntalo
        try { if (this.game && this.game.drawMenu) this.game.drawMenu(); } catch (e) { /* */ }
      })
      .catch(() => { /* sin índice: sólo el núcleo (comportamiento clásico) */ });
  }

  /** v2.69 · IMPORTA E INICIALIZA un módulo SIN lanzarlo (idempotente).
   *  La usa el arranque eager y launch() justo antes de start(). */
  async preload(id) {
    if (!/^[a-z0-9_-]+$/i.test(id)) return null;
    let m = this.modules[id];
    if (!m) {
      try {
        // El prefijo './' es OBLIGATORIO: sin él el navegador trata la
        // ruta como nombre de paquete y el import falla (lección v2.52).
        m = (await import(`./championships/${id}/index.js`)).default;
      } catch (e) {
        console.warn('[champs] import ' + id, e);
        return null;
      }
      this.modules[id] = m;
    }
    if (!m || typeof m.start !== 'function') return null;
    if (!m._ppInited) {
      m._ppInited = true;
      try {
        // v2.125: el manifest ya parseado viaja en el ctx — el módulo puede
        // seguir re-fetcheando su bloque propio, pero el fetch doble deja de
        // ser obligatorio.
        const ent = this.entries.find((x) => x.id === id);
        const r = m.init({ game: this.game, id, stateName: CHAMPS_STATE,
          manifest: ent ? ent.manifest : null });
        // v3.6.32 (ronda 40): la promesa de init queda REGISTRADA en el
        // módulo — el bloque de abajo espera las init EN VUELO.
        m._ppInitP = (r && typeof r.then === 'function') ? r : null;
        if (m._ppInitP) await m._ppInitP;                 // data.json listo
      } catch (e) {
        // v2.120: un init roto NO deja pasar el módulo a start() — se
        // re-permite el reintento en el siguiente intento de launch.
        console.warn('[champs] init ' + id, e);
        m._ppInited = false;
        m._ppInitP = null;
        return null;
      }
    } else if (m._ppInitP) {
      // v3.6.32 (ronda 40): CARRERA eager↔launch — el arranque eager marca
      // _ppInited ANTES de que su init (fetch del manifest) resuelva; un
      // launch() dentro de esa ventana recibía el módulo con CTRL aún null
      // y m.start() era un NO-OP silencioso (el campeonato no arrancaba:
      // informe del QA capa AA). Esperamos la init en vuelo: start() SIEMPRE
      // encuentra el módulo cableado.
      try { await m._ppInitP; } catch (eI) { /* init rota: start decidirá */ }
    }
    return m;
  }

  /** Entradas para el menú: [{ id, label }] con el idioma del jugador. */
  list() {
    const lang = (typeof __ppLang !== 'undefined' && __ppLang === 'en') ? 'en' : 'es';
    // v2.125: el catálogo público son SOLO los publicados (los borradores se
    // prueban con ?champ=<id>; los incompatibles se avisan en consola).
    return this.entries
      .filter((e) => (e.estado || 'publicado') === 'publicado')
      .map((e) => ({
        id: e.id,
        label: '▶  ' + String((e.title && (e.title[lang] || e.title.es)) || e.id).toUpperCase(),
      }));
  }

  /** v3.6.31 · ¿TOCA INTRO? — la primera vez que se entra al campeonato
   *  (registro pp_intro_<id> aún vacío). Las siguientes entradas van
   *  DIRECTAS a jugar; re-ver el vídeo queda OPCIONAL (botón VER
   *  PRESENTACIÓN de su tarjeta → launch(id, { intro: true })). */
  introPendiente(id) {
    try { return !localStorage.getItem('pp_intro_' + id); } catch (e) { return true; }
  }

  /** Lanza un campeonato externo (botón del menú CRAZY). Importa el
   *  módulo de su carpeta LA PRIMERA VEZ y le entrega el juego.
   *  v3.6.31 · opts.intro = fuerza el vídeo de la historia (VER
   *  PRESENTACIÓN); sin él, la intro SOLO se muestra la primera vez. */
  async launch(id, opts) {
    const g = this.game;
    if (g.closeTrainingV3) g.closeTrainingV3();   // v3.0.3 · estanqueidad
    if (!/^[a-z0-9_-]+$/i.test(id)) return;
    if (g.net.online) { g.rules.message = T('msg_guest_mode'); return; }
    g.exitHall();             // v3.1.0-SRV2: un campeonato se juea en la cancha
    // v2.69: import + init viven en preload() (compartido con el arranque
    // eager); aquí sólo falta arrancar. Excluyente con TODO campeonato.
    const m = await this.preload(id);
    if (!m) { g.rules.message = T('arc_no_data'); return; }
    this.leaveAll();
    this.activeId = id;
    // v3.6.29 · MEJOR DE 3: los duelos de campeonato siguen siendo a UN juego
    // (el mejor de 3 es del partido libre; se reactiva al arrancar cualquier
    // modo libre — menú/B/online). Así el camino calibrado no se altera.
    g.rules.bestOf = 1;
    try { m.start(); }
    catch (e) {
      console.warn('[champs] start ' + id, e);
      this.leaveAll();   // un módulo roto nunca deja el juego colgado
      return;
    }
    // v2.130 · INTRO común: vídeo de la historia del rival + gran botón
    // JUGAR (estructura común de todos los campeonatos; el vídeo es
    // opcional y si falta assets/intro.mp4 queda un póster con el título).
    // v3.6.31 · SÓLO LA PRIMERA VEZ: la primera entrada muestra el vídeo
    // (conocer al rival y dar contexto); las siguientes entran directo a
    // jugar. Re-verlo: botón VER PRESENTACIÓN de la tarjeta, o ?intro=1
    // en la URL (pruebas del dueño). Si no hay localStorage, se muestra
    // (camino seguro: nadie se pierde la historia).
    let verIntro = this.introPendiente(id);
    try {
      if (verIntro) localStorage.setItem('pp_intro_' + id, '1');
    } catch (eI0) { /* sin localStorage: se muestra siempre */ }
    if (!verIntro && opts && opts.intro) verIntro = true;
    if (!verIntro) {
      try { verIntro = new URLSearchParams(location.search).has('intro'); }
      catch (eI1) { /* */ }
    }
    if (verIntro) { try { this.game.showChampIntro(id); } catch (e2) { /* */ } }
  }

  /* ---------------- v2.69 · enchufe universal del núcleo ----------------
   *  El núcleo YA NO CONOCE campeonatos: todo pasa por aquí. Cada método
   *  delega en el módulo ACTIVO con guard (un módulo roto no tumba nada). */

  /** Módulo ya cargado (aunque no activo) — menú: menuItems/menú extras. */
  moduleIfLoaded(id) { return this.modules[id] || null; }

  /** Acción de menú de un campeonato (case 'champact'). */
  menuAction(id, act) {
    const m = this.modules[id];
    if (m && m.menuAction) {
      try { m.menuAction(act); } catch (e) { console.warn('[champs.menuAction] ' + id, e); }
    }
  }

  /** Subtítulo de la sección CAMPEONATOS: récord del activo o del último
   *  con victorias (campo "storage" del manifest de cada carpeta). */
  menuHint() {
    const m = this.mod;
    if (m && m.hint) {
      try { const h = m.hint(); if (h) return h; } catch (e) { /* */ }
    }
    try {
      for (const e of this.entries) {
        const base = String(e.storage || '').replace(/\*$/, '');
        if (!base) continue;
        if (this.leyendaFlag(e.id)) return T('champ_leyenda_hint');   // v3.6.18 (ronda 24): LEYENDA > SUPERADO
        if (this.championFlag(e.id)) return T('champ_done_hint');   // v2.128
        // v3.6.17 (ronda 21): etapa en curso antes que victorias
        const st = this._stageHint(e.id, base);
        if (st) return st;
        const w = parseInt(localStorage.getItem(base + 'wins') || '0', 10) || 0;
        if (w > 0) return T('best_arcade', { n: w });
      }
    } catch (e) { /* */ }
    return '';
  }

  /** v2.128 · ¿CAMPEONATO SUPERADO? — primero pregunta al módulo
   *  (isChampion()); si no lo expone, aplica la CONVENCIÓN de registros:
   *  <base>trophy (locura pp_arcade_trophy, magia pp_champ_magia_trophy)
   *  o <base>champ (oeste pp_champ_oeste_champ; plantilla stock). */
  championFlag(id) {
    try {
      const m = this.moduleIfLoaded(id);
      if (m && typeof m.isChampion === 'function') {
        const v = m.isChampion();
        if (v === true || v === false) return v;
      }
    } catch (e) { /* */ }
    try {
      const ent = (this.entries || []).find((x) => x.id === id);
      const base = String((ent && ent.storage) || '').replace(/\*$/, '');
      if (base) {
        if (localStorage.getItem(base + 'champ') === '1') return true;
        if (localStorage.getItem(base + 'trophy') === '1') return true;
      }
    } catch (e2) { /* */ }
    return false;
  }

  /** v3.6.18 · ronda 24 · ¿LEYENDA? — el campeón que selló las 5 etapas
   *  en modo leyenda (registro <base>leyenda = '1'; hoy sólo oeste,
   *  convención extensible a cualquier campeonato por su storage). */
  leyendaFlag(id) {
    try {
      const ent = (this.entries || []).find((x) => x.id === id);
      const base = String((ent && ent.storage) || '').replace(/\*$/, '');
      if (base && localStorage.getItem(base + 'leyenda') === '1') return true;
    } catch (e) { /* */ }
    return false;
  }

  /** v3.6.17 · ronda 21 · «Etapa X/5 · sigue donde la dejaste» — hint de
   *  progreso para las tarjetas del menú y el subtítulo de la sección.
   *  Convención de registros: <base>stage. Oeste guarda 1..5 (su constructor
   *  carga clamp(1,5)); los otros 4 guardan 0..total-1 (por eso el +1). La
   *  etapa de SALIDA (oeste 1 / resto 0) no se anuncia: no es progreso. Si
   *  el registro supera el camino (p. ej. locura marca 5 al ser campeón) se
   *  calla: el chip ★ SUPERADO ya lo cubre. Devuelve '' si nada que anunciar. */
  _stageHint(id, base) {
    try {
      const sv = parseInt(localStorage.getItem(base + 'stage') || '', 10);
      if (isNaN(sv)) return '';
      const total = CHAMP_STAGE_TOTAL[id] || 5;
      let n;                                                            // 1..total
      if (id === 'oeste') n = (sv >= 2 && sv <= total) ? sv : 0;        // 1-indexed
      else n = (sv >= 1 && sv <= total - 1) ? sv + 1 : 0;               // 0-indexed
      if (!n) return '';
      return T('champ_stage_hint', { n: n, total: total });
    } catch (e) { return ''; }
  }

  /** Al guardar TU NOMBRE: cada módulo cargado repinta sus paneles. */
  refreshAll() {
    for (const id of Object.keys(this.modules || {})) {
      const m = this.modules[id];
      try { if (m && typeof m.refresh === 'function') m.refresh(); } catch (e) { /* */ }
    }
  }

  /** PISTOLA (v2.38): sólo el campeonato activo decide si está armada. */
  get gunArmed() {
    const m = this.mod;
    return !!(m && m.gunArmed);
  }
  /** v2.89 · EL DUELO del forajido convierte la PALA en un revólver: mientras
   *  el módulo lo declare, el gatillo de ESA mano también dispara (ventana
   *  de 3 s). Aditivo: los módulos que no lo definan quedan como siempre. */
  get paddleGunArmed() {
    const m = this.mod;
    return !!(m && m.paddleGunArmed);
  }
  fireGun(i) {
    const m = this.mod;
    if (m && m.fireGun) { try { m.fireGun(i); } catch (e) { console.warn('[champs.fireGun]', e); } }
  }

  /** v3.6.33 · MEGA PALA VOLUNTARIA: con la bola en juego el gatillo llega
   *  al módulo activo (hoy sólo La Locura lo define). Devuelve true si la
   *  pulsación fue CONSUMIDA (el módulo liberó el poder, avisó de recarga o
   *  la ignoró por suya) — así el núcleo no la reenvía a saque/revancha. */
  megaTrigger(i) {
    const m = this.mod;
    if (m && m.megaTrigger) {
      try { return m.megaTrigger(i) === true; } catch (e) { console.warn('[champs.megaTrigger]', e); }
    }
    return false;
  }

  /** BOLA DOBLE (v2.44): clon vivo de la bola del campeonato activo. */
  get _split() {
    const m = this.mod;
    return (m && m._split) ? m._split : null;
  }
  splitFilterEvents(evs) {
    const m = this.mod;
    if (m && m.splitFilterEvents) { try { m.splitFilterEvents(evs); } catch (e) { console.warn('[champs.splitFilter]', e); } }
  }
  updateSplit(dt) {
    const m = this.mod;
    if (m && m.updateSplit) { try { m.updateSplit(dt); } catch (e) { console.warn('[champs.updateSplit]', e); } }
  }

  /** SALIR del campeonato externo activo (se juega otro modo). */
  leaveAll() {
    if (!this.activeId) return;
    const m = this.mod;
    try { this.game.hideChampIntro(false); } catch (e0) { /* */ }
    try { if (m && m.leave) m.leave(); }
    catch (e) { console.warn('[champs] leave', e); }
    this.activeId = '';
  }

  /* v2.130 · INTRO DE CAMPEONATO: puentes con el módulo activo — la BSO
   *  del campeonato se silencia mientras suena el vídeo de la historia y
   *  se reanuda al pulsar JUGAR (hook OPCIONAL champIntroPause del módulo;
   *  un módulo sin el hook simplemente no se silencia). */
  introShown() {
    const m = this.mod;
    if (m && typeof m.champIntroPause === 'function') {
      try { m.champIntroPause(true); } catch (e) { /* nunca rompe */ }
    }
  }
  introClosed() {
    const m = this.mod;
    if (m && typeof m.champIntroPause === 'function') {
      try { m.champIntroPause(false); } catch (e) { /* nunca rompe */ }
    }
  }

  /** v2.66: pide a cada campeonato CARGADO que borre SUS registros (método
   *  opcional resetRecords() del módulo; si no existe, se ignora).
   *  v2.68: además se borra FÍSICAMENTE de localStorage TODA clave del
   *  espacio de campeonatos (prefijo 'pp_champ_') esté o no el módulo
   *  cargado. v2.69: el resetRecords() de cada módulo borra también sus
   *  claves propias (p.ej. pp_arcade_* de La Locura) y su estado VIVO
   *  (rank, ronda, trofeo, mapa…) — borrar registros = primera arranque. */
  resetRecords() {
    for (const id of Object.keys(this.modules || {})) {
      const m = this.modules[id];
      try { if (m && typeof m.resetRecords === 'function') m.resetRecords(); }
      catch (e) { console.warn('[champs.resetRecords] ' + id, e); }
    }
    try {
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf('pp_champ_') === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e) { /* sin localStorage: nada que borrar */ }
  }

  /* ================== v2.96 · REJUGAR ETAPAS SUPERADAS ====================
   *  El módulo activo puede exponer replayMap(): { plane, nodesPx, imgW,
   *  imgH, maxIdx } — el póster del camino y sus nodos EN PÍXELES DEL ARTE
   *  (mismo convenio que las tapas). Cada frame el núcleo lanza el rayo de
   *  la PALA contra el plano, convierte el impacto a píxeles y busca el
   *  nodo apuntado (radio ×1,22; el más cercano gana). El módulo pinta el
   *  resaltado (replayHover) y lanza la etapa (replayLaunch); el gatillo
   *  consume el nodo apuntado (replayConsume). Un módulo sin replayMap
   *  simplemente nunca participa. */
  _updateReplayPick() {
    const g = this.game;
    const m = this.mod;
    let idx = -1;
    this._rbWant = false;   // v2.98: ¿la pala está apuntando al mapa?
    // v3.6.31 · durante la INTRO del campeonato el haz lo gobierna la
    // propia intro (botón JUGAR); el mapa no raycastea ni lo apaga.
    if (m && typeof m.replayMap === 'function' &&
        g.renderer.xr.isPresenting && !g.menuOpen && !g.champIntro) {
      let rm = null;
      try { rm = m.replayMap(); } catch (e) { rm = null; }
      if (rm && rm.plane && Array.isArray(rm.nodesPx) && rm.nodesPx.length) {
        // el raycaster de three.js IGNORA .visible: filtrar a mano toda la
        // cadena de padres (el mapa se oculta dejando la sala / en pruebas)
        let vis = true;
        for (let o = rm.plane; o; o = o.parent) {
          if (o.visible === false) { vis = false; break; }
        }
        const hand = g.paddleHand | 0;
        const ray = g.rays && g.rays[hand];
        if (vis && ray && g.connected && g.connected[hand]) {
          ray.getWorldPosition(rpOrigin);
          ray.getWorldQuaternion(rpQuat);
          rpDir.set(0, 0, -1).applyQuaternion(rpQuat);
          rpRaycaster.set(rpOrigin, rpDir);
          let hit = null;
          try { hit = rpRaycaster.intersectObject(rm.plane, false)[0]; }
          catch (eR) { hit = null; }   // v2.120: nunca tumba el frame
          if (hit && hit.point) {
            // v2.120: temporales de módulo (antes 2 Vector3 por FRAME aquí
            // dentro) + guard de geometría: un replayMap con plano no-Plane
            // (GLTF) ya no tumba el resto del frame.
            let pw = 0, ph = 0;
            const geo = rm.plane.geometry;
            if (geo && geo.parameters && geo.parameters.width) {
              pw = geo.parameters.width; ph = geo.parameters.height;
            } else {
              const bb = new THREE.Box3().setFromObject(rm.plane);
              const sz = bb.getSize(_rpSize);
              pw = sz.x || 1; ph = sz.y || 1;
            }
            const lp = rm.plane.worldToLocal(_rpV1.copy(hit.point));
            const px = (lp.x / pw + 0.5) * rm.imgW;
            const py = (0.5 - lp.y / ph) * rm.imgH;
            const maxI = Math.min((rm.maxIdx | 0), rm.nodesPx.length - 1);
            let best = -1, bestD = 1e9;
            for (let i = 0; i <= maxI; i++) {
              const n = rm.nodesPx[i];
              if (!n) continue;
              const dx = px - n.x, dy = py - n.y;
              const d = Math.sqrt(dx * dx + dy * dy);
              if (d <= n.r * 1.22 && d < bestD) { best = i; bestD = d; }
            }
            idx = best;
          }
          // v2.98 · HAZ DE LUZ puntero: la pala proyecta un rayo sobre
          // el mapa del camino (azul; DORADO al resaltar una etapa
          // superada) — así se sabe SIEMPRE a qué se apunta.
          // v2.100 · el haz SÓLO vive cuando el rayo TOCA el mapa
          // (enfocándolo): apuntar a la pared/techo/suelo NO muestra
          // puntero — el mapa es, de momento, el único sitio con
          // puntero de pala.
          if (hit && hit.point) {
            this._rbWant = true;
            this._replayBeamShow(rpOrigin, rpDir,
              Math.max(0.25, rpOrigin.distanceTo(hit.point)), idx >= 0);
          }
        }
      }
    }
    // v2.98: el haz sólo vive mientras la pala apunta al mapa del camino
    if (!this._rbWant) this._replayBeamHide();
    if (idx !== (this.replayHover | 0)) {
      this.replayHover = idx;
      if (m && typeof m.replayHover === 'function') {
        try { m.replayHover(idx); } catch (e2) { /* nunca tumba el frame */ }
      }
    }
  }

  /* ================== v2.98 · HAZ DE LUZ DEL SELECTOR ====================
   *  Al apuntar con la pala al mapa del camino sale un HAZ DE LUZ (hilo
   *  + halo + punta) que termina DONDE APUNTA la pala: azul celeste por
   *  defecto y DORADO cuando el nodo apuntado es una etapa superada (la
   *  misma que resalta el anillo del módulo). Hijos del RIG: el rayo
   *  llega en espacio MUNDO y se convierte a RIG como hace _gunRay.  */
  _replayBeamShow(oW, dW, len, hot) {
    const g = this.game;
    if (!this._rb) {
      const core = new THREE.Mesh(
        new THREE.BoxGeometry(0.004, 0.004, 1),
        new THREE.MeshBasicMaterial({ color: 0x9adfff, transparent: true,
          opacity: 0.92, depthWrite: false }));
      const glow = new THREE.Mesh(
        new THREE.BoxGeometry(0.017, 0.017, 1),
        new THREE.MeshBasicMaterial({ color: 0x4fa8ff, transparent: true,
          opacity: 0.3, blending: THREE.AdditiveBlending,
          depthWrite: false }));
      const tip = new THREE.Mesh(
        new THREE.SphereGeometry(0.013, 8, 6),
        new THREE.MeshBasicMaterial({ color: 0xaee6ff, transparent: true,
          opacity: 0.95, blending: THREE.AdditiveBlending,
          depthWrite: false }));
      core.renderOrder = 15; glow.renderOrder = 15; tip.renderOrder = 16;
      core.frustumCulled = glow.frustumCulled = tip.frustumCulled = false;
      core.visible = glow.visible = tip.visible = false;
      g.rig.add(core); g.rig.add(glow); g.rig.add(tip);
      this._rb = { core, glow, tip };
    }
    const B = this._rb;
    _rbV1.copy(oW); g.rig.worldToLocal(_rbV1);
    g.rig.getWorldQuaternion(_rbQ); _rbQ.invert();
    _rbV2.copy(dW).applyQuaternion(_rbQ).normalize();
    const mid = _rbV3.copy(_rbV1).addScaledVector(_rbV2, len / 2);
    B.core.position.copy(mid); B.glow.position.copy(mid);
    B.core.scale.set(1, 1, len); B.glow.scale.set(1, 1, len);
    B.core.quaternion.setFromUnitVectors(_rbV4.set(0, 0, 1), _rbV2);
    B.glow.quaternion.copy(B.core.quaternion);
    B.tip.position.copy(_rbV1).addScaledVector(_rbV2, len);
    B.core.material.color.setHex(hot ? 0xffd875 : 0x9adfff);
    B.glow.material.color.setHex(hot ? 0xffb45f : 0x4fa8ff);
    B.tip.material.color.setHex(hot ? 0xffe6a0 : 0xaee6ff);
    B.core.visible = B.glow.visible = B.tip.visible = true;
  }
  _replayBeamHide() {
    if (!this._rb) return;
    this._rb.core.visible = this._rb.glow.visible =
      this._rb.tip.visible = false;
  }

  /** v3.6.31 · haz-puntero de la INTRO (el MISMO haz del mapa del camino,
   *  v2.98): al apuntar con la pala al panel de la intro sale el rayo y
   *  se ve DÓNDE se apunta; DORADO sobre el botón JUGAR. El resto del
   *  tiempo permanece apagado (no molesta). */
  introBeamShow(oW, dW, len, hot) { this._replayBeamShow(oW, dW, len, hot); }
  introBeamHide() { this._replayBeamHide(); }

  /** v2.96: el gatillo cae con un nodo del camino apuntado → REJUGA esa
   *  etapa (el módulo la relanza). true = gatillo consumido. */
  replayConsume() {
    const idx = this.replayHover | 0;
    if (idx < 0) return false;
    const m = this.mod;
    if (!m || typeof m.replayLaunch !== 'function') return false;
    this.replayHover = -1;
    try { m.replayLaunch(idx); } catch (e) { console.warn('[champs.replay]', e); }
    return true;
  }

  /* ================== v2.108 · RÓTULO «MODO DEPURACIÓN» ==================
   *  Dentro del visor, un rótulo pequeñito anclado a la VISTA (esquina
   *  inferior-derecha del campo de visión) identifica la sesión de
   *  revisión. Es un plano con CanvasTexture hijo del RIG que se coloca
   *  CADA FRAME relativo a la pose de la cabeza — la cámara no es un
   *  anclaje fiable en WebXR y así el rótulo acompaña la mirada sin
   *  marear ni estorbar la vista de la mesa. Sólo existe si el nombre
   *  del jugador es foro3d (window.__PP_DEBUG) y hay sesión XR activa. */
  _updateDebugBadge() {
    const g = this.game;
    if (!g || !g.renderer || !g.renderer.xr || !g.rig) return;
    const show = (typeof window !== 'undefined' && !!window.__PP_DEBUG) &&
                 g.renderer.xr.isPresenting;
    if (!this._dbadge) {
      if (!show) return;                     // perezoso: sólo si hace falta
      const cv = document.createElement('canvas');
      cv.width = 512; cv.height = 96;
      const cx = cv.getContext('2d');
      if (cx.roundRect) {
        cx.beginPath(); cx.roundRect(4, 4, 504, 88, 22);
        cx.fillStyle = 'rgba(16,11,2,0.78)'; cx.fill();
        cx.strokeStyle = 'rgba(255,211,76,0.85)'; cx.lineWidth = 5; cx.stroke();
      } else {
        cx.fillStyle = 'rgba(16,11,2,0.78)'; cx.fillRect(4, 4, 504, 88);
        cx.strokeStyle = 'rgba(255,211,76,0.85)'; cx.lineWidth = 5;
        cx.strokeRect(4, 4, 504, 88);
      }
      cx.fillStyle = '#ffd34c';
      cx.font = '700 52px system-ui, sans-serif';
      cx.textAlign = 'center'; cx.textBaseline = 'middle';
      cx.fillText('MODO DEPURACIÓN', 256, 52);
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const mesh = new THREE.Mesh(
        new THREE.PlaneGeometry(0.30, 0.30 * 96 / 512),
        new THREE.MeshBasicMaterial({
          map: tex, transparent: true, depthWrite: false, depthTest: false,
        }),
      );
      mesh.renderOrder = 9999;
      mesh.frustumCulled = false;
      mesh.visible = false;
      g.rig.add(mesh);
      this._dbadge = mesh;
    }
    const b = this._dbadge;
    b.visible = show;
    if (!show) return;
    // pose de la cabeza en espacio del RIG (la del render anterior:
    // para un HUD el retardo de 1 frame es imperceptible)
    _dbV1.setFromMatrixPosition(g.camera.matrixWorld);
    g.rig.worldToLocal(_dbV1);
    _dbQ1.setFromRotationMatrix(g.camera.matrixWorld);
    g.rig.getWorldQuaternion(_dbQ2); _dbQ2.invert();
    _dbQ1.premultiply(_dbQ2);
    b.position.copy(_dbV1);
    b.quaternion.copy(_dbQ1);
    b.translateX(0.235);   // a la derecha de la vista
    b.translateY(-0.185);  // abajo, sin tapar la mesa ni el marcador
    b.translateZ(-0.62);   // delante de la cara (HUD a ~62 cm)
  }

  /* --- delegación con guard: un módulo roto NUNCA tumba el frame --- */
  update(dt) {
    this._updateReplayPick();   // v2.96: ¿la pala apunta a un nodo del camino?
    this._updateDebugBadge();   // v2.108: rótulo «MODO DEPURACIÓN» en el visor
    const m = this.mod;
    if (m && m.update) { try { m.update(dt); } catch (e) { console.warn('[champs.update]', e); } }
  }
  onPoint(it) {
    const m = this.mod;
    if (m && m.onPoint) { try { m.onPoint(it); } catch (e) { console.warn('[champs.onPoint]', e); } }
  }
  /** v3.6.49 (r57) · NORMA DE EMOCIONES DEL RIVAL: el núcleo reparte la
   *  emoción (idle/crazy/angry/laughing/focused/picando/surprised/panic/
   *  loosing/victory/defeated) y el módulo ACTIVO la viste con SU arte
   *  (convención <estado>.webp) y SUS sonidos. Hook opcional: los módulos
   *  sin rivalEmocion ignoran la norma en silencio. */
  rivalEmocion(st, info) {
    const m = this.mod;
    if (m && m.rivalEmocion) { try { m.rivalEmocion(st, info); } catch (e) { console.warn('[champs.rivalEmocion]', e); } }
  }
  onMatchOver(w) {
    const m = this.mod;
    if (m && m.onMatchOver) { try { m.onMatchOver(w); } catch (e) { console.warn('[champs.onMatchOver]', e); } }
  }
  aiMul() {
    const m = this.mod;
    try { return (m && m.aiMul) ? (m.aiMul() || 1) : 1; } catch { return 1; }
  }
  serveTrigger(i) {
    const m = this.mod;
    // v2.98: i = mando que aprieta el gatillo (revólver POR MANO)
    if (m && m.serveTrigger) { try { m.serveTrigger(i); } catch (e) { console.warn('[champs.serve]', e); } }
  }
  reenter() {
    const m = this.mod;
    if (m && m.reenter) { try { m.reenter(); } catch (e) { console.warn('[champs.reenter]', e); } }
  }
  testStep(dt) {
    const m = this.mod;
    if (m && m.testStep) { try { m.testStep(dt); } catch (e) { console.warn('[champs.testStep]', e); } }
  }
}
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { T, __ppLang } from './c00_pre_three.js';
import { CHAMPS_STATE, _dbQ1, _dbQ2, _dbV1, _rbQ, _rbV1, _rbV2, _rbV3, _rbV4, _rpSize, _rpV1, rpDir, rpOrigin, rpQuat, rpRaycaster } from './c10_menu_saque.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */

// temporales del anti-clipping de palas (mesa / red / suelo)
export const pcA = new THREE.Vector3();
export const pcN = new THREE.Vector3();
export const pcC = new THREE.Vector3();
export const pcT = new THREE.Vector3();

// temporales del MENÚ DE MUÑECA (v2.15, espacio mundo; no compartir)
export const muGrip = new THREE.Vector3();
export const muHead = new THREE.Vector3();
export const muDir = new THREE.Vector3();
const muPos = new THREE.Vector3();
export const muQ = new THREE.Quaternion();
export const muRaycaster = new THREE.Raycaster();
export const netTmpP = new THREE.Vector3();   // v2.19: poses del rival por red
export const netTmpQ = new THREE.Quaternion();
muRaycaster.far = 2.5;

/* v2.135 · PIELES DE CARTEL del artista para las NORMAS de las etapas:
 *  clown (La Locura), wizard (Magia) y forajido (Salvaje Oeste). El cartel
 *  de instrucciones se pinta sobre el ARTE real (marco + personaje) y TODO
 *  el texto vive DENTRO del hueco interior del cartel: título + cuerpo en
 *  crema/oro con sombra sobre un velo oscuro suave para que se lea perfecto
 *  («que entren en el espacio interior de los carteles y se lean
 *  perfectamente»). rect = hueco interior medido sobre el arte 1024×512 con
 *  margen de seguridad (el personaje asoma por el borde superior central y
 *  las manos agarran el marco). Las 3 imágenes precargan al arrancar; si
 *  alguna no llegó, showInstrucciones cae a la piel dibujada de siempre. */
export const NORMAS_SKIN = {
  defs: {
    locura: {
      url: 'championships/locura/assets/normas_clown.png',
      rect: [140, 152, 872, 438],
      fFam: '"Trebuchet MS", Verdana, sans-serif',
      colTitle: '#ffdf8e', colBody: '#f6ecd8', colBull: '#ffb347',
      colBand: '#c0272d', colBand2: '#8a1016',
    },
    magia: {
      url: 'championships/magia/assets/normas_wizard.png',
      rect: [166, 158, 858, 444],
      fFam: 'Georgia, "Times New Roman", serif',
      colTitle: '#ffe08a', colBody: '#f0e8ff', colBull: '#ffd76e',
      colBand: '#5b2f96', colBand2: '#3c1f6e',
    },
    oeste: {
      url: 'championships/oeste/assets/normas_forajido.png',
      rect: [142, 140, 876, 440],
      fFam: 'Georgia, "Times New Roman", serif',
      colTitle: '#f8d98c', colBody: '#f3e9d2', colBull: '#ffcc66',
      colBand: '#7c3f14', colBand2: '#5a2c0e',
    },
    estacion: {
      // v2.135 · piel del ARTISTA para Estación Orbital (plantilla del
      // dueño con el ASTRO asomándose; hueco interior medido 152..872 ×
      // 152..432 sobre el lienzo 1024×512)
      url: 'championships/estacion_orbital/assets/normas_astro.png',
      rect: [152, 152, 872, 432],
      fFam: '"Trebuchet MS", Verdana, sans-serif',
      colTitle: '#7fe8ff', colBody: '#dcecff', colBull: '#ffb347',
      colBand: '#12324a', colBand2: '#0b2033',
    },
  },
  imgs: {},
};
for (const nk of Object.keys(NORMAS_SKIN.defs)) {
  const nim = new Image();
  nim.src = NORMAS_SKIN.defs[nk].url;
  NORMAS_SKIN.imgs[nk] = nim;
}
window.__PP_NORMAS = NORMAS_SKIN;   // v2.135 · gancho QA (el módulo no expone consts)


/* v3.6.17 · ronda 21 · TU CAMINO TE ESPERA — total de etapas del camino de
 * cada campeonato (NODOS/nodesPx/etapas de cada módulo; los 5 declaran ruta
 * de 5 hoy). Un campeonato futuro con otra longitud: añadir aquí. Va AL
 * FINAL de la pieza porque build_game.py exige el token de identidad en la
 * 1.ª línea (class ChampLoader) y _stageHint sólo lo lee en runtime.
 * HISTORIA: el parche de la ronda 19 se escribió en el ARTEFACTO
 * (public/game.html) y bump_version lo regeneró desde aquí — la ronda 21
 * lo rehace en la fuente. */
const CHAMP_STAGE_TOTAL = {
  locura: 5, magia: 5, oeste: 5, estacion_orbital: 5, valle_neon: 5,
};
