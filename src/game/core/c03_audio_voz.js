const VOICE_FULL = {
  es: {
    'modo supervivencia aguanta el rallye': ['modo_supervivencia'],
    'modo partido buena suerte': ['modo_partido'],
    'bienvenido al partido buena suerte': ['bienvenido'],
    'bienvenido a crazy ping pong escoge una modalidad de juego': ['bienvenida_modo'],
    'pasajeros al tren partimos hacia dry gulch': ['mega_salida_dg'],
    'pasajeros al tren partimos hacia perdido': ['mega_salida_pd'],
    'pasajeros al tren partimos hacia bravos': ['mega_salida_br'],
    'en menos de 25 segundos llegaremos a dry gulch': ['mega_llega_dg'],
    'en menos de 25 segundos llegaremos a perdido': ['mega_llega_pd'],
    'en menos de 25 segundos llegaremos a bravos': ['mega_llega_br'],
    'pasajeros al tren partimos hacia gold dust': ['mega_salida_gd'],
    'pasajeros al tren partimos hacia silver creek': ['mega_salida_sc'],
    'en menos de 25 segundos llegaremos a gold dust': ['mega_llega_gd'],
    'en menos de 25 segundos llegaremos a silver creek': ['mega_llega_sc'],
    'cargamento de oro a buen recaudo': ['mega_oro'],
    'rival conectado a jugar': ['rival_conectado'],
    'rival desconectado': ['rival_desconectado'],
    'sala pabellon': ['sala_pabellon'],
    'sala neon': ['sala_neon'],
    'sala atardecer': ['sala_atardecer'],
    'sala artico': ['sala_artico'],
    'dificultad facil': ['dificultad_facil'],
    'dificultad media': ['dificultad_media'],
    'dificultad dificil': ['dificultad_dificil'],
  },
  en: {
    'survival mode keep the rally going': ['modo_supervivencia'],
    'match mode good luck': ['modo_partido'],
    'welcome to the match good luck': ['bienvenido'],
    'welcome to crazy ping pong choose a game mode': ['bienvenida_modo'],
    'all aboard we are departing towards dry gulch': ['mega_salida_dg'],
    'all aboard we are departing towards perdido': ['mega_salida_pd'],
    'all aboard we are departing towards bravos': ['mega_salida_br'],
    'in less than 25 seconds we will arrive at dry gulch': ['mega_llega_dg'],
    'in less than 25 seconds we will arrive at perdido': ['mega_llega_pd'],
    'in less than 25 seconds we will arrive at bravos': ['mega_llega_br'],
    'all aboard we are departing towards gold dust': ['mega_salida_gd'],
    'all aboard we are departing towards silver creek': ['mega_salida_sc'],
    'in less than 25 seconds we will arrive at gold dust': ['mega_llega_gd'],
    'in less than 25 seconds we will arrive at silver creek': ['mega_llega_sc'],
    'the gold shipment is safe and sound': ['mega_oro'],
    'opponent connected let s play': ['rival_conectado'],
    'opponent disconnected': ['rival_desconectado'],
    'gym arena': ['sala_pabellon'],
    'neon arena': ['sala_neon'],
    'sunset arena': ['sala_atardecer'],
    'arctic arena': ['sala_artico'],
    'easy difficulty': ['dificultad_facil'],
    'medium difficulty': ['dificultad_media'],
    'hard difficulty': ['dificultad_dificil'],
  },
};
const VOICE_ACH = {
  es: {
    'primera victoria': 'ach_primera',
    'en racha': 'ach_racha',
    'gigante': 'ach_gigante',
    'maratonista': 'ach_maraton',
    'superviviente': 'ach_superviv',
    'saque directo': 'ach_aces',
  },
  en: {
    'first victory': 'ach_primera',
    'on a roll': 'ach_racha',
    'giant': 'ach_gigante',
    'marathoner': 'ach_maraton',
    'survivor': 'ach_superviv',
    'ace serve': 'ach_aces',
  },
};
const VOICE_NUM = {};
for (let vi = 0; vi <= 29; vi++) VOICE_NUM[vi] = `n${vi}`;
VOICE_NUM[30] = 'n30'; VOICE_NUM[40] = 'n40'; VOICE_NUM[50] = 'n50';
VOICE_NUM[60] = 'n60'; VOICE_NUM[70] = 'n70'; VOICE_NUM[80] = 'n80';
VOICE_NUM[90] = 'n90';

/** Número 0-99 -> fragmentos. v2.27: por idioma — castellano con 'y'
 *  (treinta y cinco), inglés sin ella (thirty five). */
function voiceNumPlan(n, lang) {
  n = Math.floor(Number(n));
  if (!Number.isFinite(n) || n < 0 || n > 99) return null;
  if (VOICE_NUM[n]) return [VOICE_NUM[n]];
  const d = Math.floor(n / 10) * 10;
  const u = n % 10;
  if (!VOICE_NUM[d] || !VOICE_NUM[u]) return null;
  return (lang === 'en') ? [VOICE_NUM[d], VOICE_NUM[u]] : [VOICE_NUM[d], 'y', VOICE_NUM[u]];
}

class GameAudio {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;
    this._wdAcc = 0;
    this._wdFails = 0;
    this._lastRebuild = 0;
    this.hadGesture = false;   // ya hubo gesto de usuario (clic, gatillo XR…)
    this.rebuilds = 0;
    this.xrActive = false;     // sesión XR inmersiva activa (lo marca el juego)
    // v2.31 · ¿hay ya un contexto CONFIRMADO dentro del casco? Un contexto
    // creado fuera de la sesión puede quedar 'running' pero MUDO en VR (la
    // Quest cambia el dispositivo de salida al entrar en inmersivo). Los
    // rescates antiguos solo actuaban si el estado NO era 'running': un
    // 'running'-pero-mudo nunca se reemplazaba -> silencio total y eterno.
    this.vrBound = false;
    this.ambWanted = false;    // v2.31: el murmullo debe seguir tras un swap de contexto
    this._lastAlive = 0;
    this._lastCT = -1;         // último currentTime medido (watchdog)
    this._ctAdvanced = true;   // ¿el reloj de audio avanza? (estado 'running' vivo)
    this._ctStalls = 0;        // ticks consecutivos con el reloj congelado
    // --- ambiente de torneo (v2.11) ---
    this.ambience = true;      // murmullo + aplausos + megafonía
    try { this.ambience = localStorage.getItem('ppxr_amb_v1') !== '0'; } catch { /* */ }
    // --- v2.22 · MEGÁFONO del marcador: conmutador propio e independiente ---
    // (chime + voz del narrador). Difiere del ambiente: puedes tener el
    // pabellón en silencio pero con el marcador hablando, o al revés.
    this.voice = true;
    try { this.voice = localStorage.getItem('ppxr_voz_v1') !== '0'; } catch { /* */ }
    this._amb = null;          // nodos del murmullo en marcha
    this._ambBuffer = null;    // buffer de ruido "grumoso" reutilizable
    this._lastOhh = 0;
    this._lastAnnounce = 0;
    // v2.20: banco de voz (AudioBuffer por fragmento, válido SOLO en su ctx)
    this.vb = null;
    this.vbGain = null;
    this.vbCtx = null;
    // v2.22: recorte de silencios [t0, t1] por fragmento (Piper deja cabecera
    // y cola silenciosas que, sumadas a los gaps, creaban pausas artificiales
    // — el "corte" antes de la segunda cifra del marcador).
    this.vbTrim = null;
    // v2.23: duración de la última locución compuesta (para el ducking)
    this._voiceDur = 0;
    // v2.29 · MÚSICA DE FONDO EN VR (menú principal): el mismo tema de la
    // portada (star) decodificado a AudioBuffer y en bucle por WebAudio —
    // así sobrevive a los re-vínculos de contexto y suena por el altavoz del
    // casco. Respeta la MISMA preferencia que el botón 🔊 de la portada.
    this.musicOn = true;
    try { this.musicOn = localStorage.getItem('pp_music') !== '0'; } catch { /* */ }
    this.musicWanted = false;   // ¿el juego la pide ahora? (menú abierto)
    this.musicPlaying = false;
    this._musicBuf = null;
    this._musicSrc = null;
    this._musicGain = null;
    this._musicLoading = false;
    this._musicCtx = null;   // v2.31: solo informativo (el buffer sirve para cualquier ctx)
    // v2.36 · BANDA SONORA DEL CAMPEONATO: pista propia (manifest "music"
    // del campeonato) que suena BAJITA y en bucle SOLO mientras dura la
    // partida arcade. Volumen y silencio persistentes e independientes de
    // la música del menú (pp_arcade_vol / pp_arcade_mute).
    this.arcWanted = false;
    this.arcPlaying = false;
    this._arcBuf = null;
    this._arcSrc = null;
    this._arcGain = null;
    this._arcLoading = false;
    this._arcDucked = false; // v2.37: silenciada por el MENÚ abierto
    this.arcVol = 0.18;      // "bajita" por defecto
    this.arcMute = false;
    try {
      const v = parseFloat(localStorage.getItem('pp_arcade_vol'));
      if (Number.isFinite(v)) this.arcVol = Math.min(1, Math.max(0, v));
      this.arcMute = localStorage.getItem('pp_arcade_mute') === '1';
    } catch { /* */ }
    // El sensor de proximidad de la Quest suspende la pestaña al ajustar el
    // visor; al volver, el contexto de audio queda a veces suspendido.
    // Al recuperar visibilidad: rescate SUAVE (resume + recrear solo si el
    // contexto no arranca; nunca destruye uno sano).
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.hadGesture = true;
        this.kick();
      }
    });
    // RECUPERACIÓN DEL FOCO DE LA VENTANA: al volver de la interfaz del
    // sistema (Quest Link / menú universal) el navegador puede dejar el
    // contexto suspendido o con la salida re-enrutada. Rescate suave + blip
    // de confirmación: si el usuario OYE el blip al enfocar la ventana, la
    // salida funciona; si no, el chip en pared dirá si el contexto vive.
    window.addEventListener('focus', () => {
      this.hadGesture = true;
      this.kick();
      if (this.ctx && this.ctx.state === 'running' && this.xrActive) {
        this.blipAlive();
      }
    });
    // CUALQUIER toque en la página (menú 2D, dificultad, HUD…) es un gesto
    // válido para reactivar el audio: vía de rescate principal fuera de VR.
    const gesture = () => { this.hadGesture = true; this.kick(); };
    document.addEventListener('pointerdown', gesture, { passive: true });
    document.addEventListener('click', gesture, { passive: true });
  }

  /** Cablea el grafo de salida (master -> compresor -> destino) y el buffer
   *  de ruido SOBRE un contexto dado. */
  _wire(ctx) {
    this.master = ctx.createGain();
    this.master.gain.value = 0.9;
    // Compresor: golpes más presentes y audibles en el altavoz del visor
    const comp = ctx.createDynamicsCompressor();
    comp.threshold.value = -16;
    comp.knee.value = 22;
    comp.ratio.value = 5;
    comp.attack.value = 0.002;
    comp.release.value = 0.12;
    this.master.connect(comp);
    comp.connect(ctx.destination);
    // v2.23 · BUS del ambiente (murmullo, aplausos, "ohh"): se agrupa para
    // poder AGACHARLO (ducking) mientras el megáfono dice las cifras — los
    // números se oyen por ENCIMA del pabellón, sin ruido de fondo.
    this.ambBus = ctx.createGain();
    this.ambBus.gain.value = 1;
    this.ambBus.connect(this.master);
    const len = Math.floor(ctx.sampleRate * 0.25);
    this.noiseBuffer = ctx.createBuffer(1, len, ctx.sampleRate);
    const data = this.noiseBuffer.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
    // v2.20: (re)cargar el banco de voz para este contexto (asíncrono)
    this._loadVoice(ctx);
    // v2.29: (re)cargar la música para este contexto y reanudarla si toca
    this._loadMusic(ctx);
    // v2.36: (re)cargar la BSO del campeonato y reanudarla si tocaba
    this._loadArcMusic();
  }

  /* ---------- v2.29 · MÚSICA DE FONDO EN VR (menú principal) ----------
   * La pista de la portada (star, data URL audio/ogg incrustado) se
   * decodifica al contexto ACTIVO y suena en bucle mientras el menú esté
   * abierto, con fundidos suaves. Al re-vincular el audio (entrada/salida
   * de VR, rescate del watchdog) el _wire() la recarga y la reanuda sola.
   * Preferencia compartida con el botón 🔊 de la portada (pp_music). */

  /** v2.31 · INICIO DE SESIÓN INMERSIVA: marca XR activa y re-apunta la
   *  salida del contexto vigente al dispositivo por defecto (el casco). */
  markVRStart() {
    this.xrActive = true;
    this.nudgeSink();
  }

  /** v2.31 · Re-liga el contexto a la SALIDA POR DEFECTO ACTUAL. Al entrar
   *  en VR la Quest cambia el dispositivo de audio; un contexto creado antes
   *  puede quedar anclado a la salida 2D (sigue 'running' pero MUDO).
   *  setSinkId('') re-apunta al dispositivo vigente (el casco) SIN necesitar
   *  gesto ni recrear nada. Si no está soportado, no hace nada. */
  nudgeSink() {
    try {
      if (this.ctx && this.ctx.state === 'running' &&
          typeof this.ctx.setSinkId === 'function') {
        const p = this.ctx.setSinkId('');
        if (p && p.catch) p.catch(() => { /* sin efecto */ });
        console.info("[Audio] setSinkId('') — salida re-apuntada al dispositivo por defecto");
      }
    } catch { /* no soportado: sin efecto */ }
  }

  /** v2.31 · GESTO XR (gatillo/grip/input conectado): activación de usuario
   *  garantizada DENTRO de la sesión. Si el audio aún no está confirmado en
   *  el casco (vrBound) se RE-CREA el contexto aquí aunque el actual diga
   *  'running': uno nacido fuera de la sesión puede estar 'running' y ser
   *  mudo; uno nacido en el gesto nace 'running' y ligado al casco. */
  gestureKick() {
    this.hadGesture = true;
    this.ensure();
    if (this.xrActive && !this.vrBound) {
      this.rebind('gesto XR: contexto re-creado dentro del casco');
      return;
    }
    if (this.ctx && this.ctx.state !== 'running') {
      void this.ctx.resume().catch(() => {});
      this.tryFreshRunning('kick (resume sin efecto)');
    }
  }

  /** Conmutador de música (menú Opciones y botón 🔊 de la portada). */
  setMusic(on) {
    this.musicOn = !!on;
    try { localStorage.setItem('pp_music', this.musicOn ? '1' : '0'); } catch { /* */ }
    if (!this.musicOn) this.stopMusic();
    else if (this.musicWanted) this.startMusic();
  }

  /** El juego marca si la música debe sonar ahora (menú abierto en VR). */
  setMusicWanted(wanted) {
    const w = !!wanted;
    if (w === this.musicWanted) {
      if (w && !this.musicPlaying && this.musicOn) this.startMusic();
      if (!w && this.musicPlaying) this.stopMusic();
      return;
    }
    this.musicWanted = w;
    if (w) this.startMusic(); else this.stopMusic();
  }

  /** Descarga y decodifica la pista (UNA sola vez: el AudioBuffer sirve
   *  para CUALQUIER contexto — BufferSource remuestrea solo; v2.31 elimina
   *  la carrera _musicLoading que dejaba la música sin cargar si el contexto
   *  cambiaba mientras llegaba el fetch, p. ej. al entrar en VR). */
  _loadMusic() {
    if (this._musicBuf || this._musicLoading) return;
    const url = (typeof window !== 'undefined') ? window.__PP_MUSIC_URL : null;
    if (!url || typeof fetch !== 'function') return;
    const ctx = this.ctx;
    if (!ctx) return;
    this._musicLoading = true;
    fetch(url).then((r) => r.arrayBuffer()).then((ab) =>
      new Promise((res, rej) => {
        try { res(ctx.decodeAudioData(ab.slice(0))); } catch (e) { rej(e); }
      }),
    ).then((buf) => {
      this._musicBuf = buf;
      console.info('[Audio] música lista (' + (buf.duration || 0).toFixed(1) + ' s)');
      if (this.ctx && this.musicWanted && this.musicOn) this.startMusic();
    }).catch(() => { /* sin música: nunca rompe el juego */ })
      .finally(() => { this._musicLoading = false; });
  }

  /** Bucle de música con fundido de entrada (ganancia 0,26). */
  startMusic() {
    try {
      this.kick();
      if (!this.ctx || !this.master || !this.musicOn || !this.musicWanted) return;
      if (this.musicPlaying) return;
      // v2.122 · INVARIANTE UNA MELODÍA (ANTES de la carga del buffer): la
      // música del menú JAMÁS comparte aire con la BSO del campeonato. Todos
      // los caminos actuales emparejan setMusicWanted(true) con
      // setArcDuck(true); si alguno futuro se olvida, el duck se arma AQUÍ
      // aunque la pista del menú siga cargando — el canal del núcleo baja al
      // momento y los módulos (oeste/magia) leen _arcDucked en su
      // _syncMusicGain cada frame.
      if (!this._arcDucked) this.setArcDuck(true);
      if (!this._musicBuf) { this._loadMusic(); return; }
      const src = this.ctx.createBufferSource();
      src.buffer = this._musicBuf;
      src.loop = true;
      const g = this.ctx.createGain();
      const t = this.ctx.currentTime;
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(0.26, t + 0.9);
      src.connect(g); g.connect(this.master);
      src.start(t);
      this._musicSrc = src;
      this._musicGain = g;
      this.musicPlaying = true;
    } catch { /* nunca rompe el juego */ }
  }

  /** Fundido de salida (0,7 s) y parada. */
  stopMusic() {
    const src = this._musicSrc;
    const g = this._musicGain;
    this._musicSrc = null;
    this._musicGain = null;
    this.musicPlaying = false;
    if (!src || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      g.gain.cancelScheduledValues(t);
      g.gain.setValueAtTime(Math.max(0.0001, g.gain.value || 0.26), t);
      g.gain.linearRampToValueAtTime(0.0001, t + 0.7);
      window.setTimeout(() => { try { src.stop(); } catch { /* ya parada */ } }, 800);
    } catch { /* */ }
  }

  /* ---------- v2.36 · BANDA SONORA DEL CAMPEONATO ----------
   * Igual de robusta que la música del menú: UNA decodificación (el
   * AudioBuffer sirve para cualquier contexto), bucle con fundido de
   * entrada, y SOLO suena cuando el arcade marca arcWanted (empieza al
   * empezar la partida, se detiene al acabar / salir). El volumen es
   * propio, persistente y silenciable desde el menú CRAZY. */

  setArcWanted(wanted) {
    const w = !!wanted;
    if (w === this.arcWanted) {
      if (w && !this.arcPlaying && !this.arcMute) this.startArcadeMusic();
      if (!w && this.arcPlaying) this.stopArcadeMusic();
      return;
    }
    this.arcWanted = w;
    if (w && !this.arcMute) this.startArcadeMusic(); else this.stopArcadeMusic();
  }

  _loadArcMusic() {
    if (this._arcBuf || this._arcLoading) return;
    let url = null;
    try {
      url = (typeof window !== 'undefined' && window.__PP_ARCADE_DATA &&
        window.__PP_ARCADE_DATA.musicUrl) || null;
    } catch { /* */ }
    if (!url || typeof fetch !== 'function') return;
    const ctx = this.ctx;
    if (!ctx) return;
    this._arcLoading = true;
    fetch(url).then((r) => r.arrayBuffer()).then((ab) =>
      new Promise((res, rej) => {
        try { res(ctx.decodeAudioData(ab.slice(0))); } catch (e) { rej(e); }
      }),
    ).then((buf) => {
      this._arcBuf = buf;
      console.info('[Audio] BSO del campeonato lista (' +
        (buf.duration || 0).toFixed(1) + ' s)');
      if (this.ctx && this.arcWanted && !this.arcMute) this.startArcadeMusic();
    }).catch(() => { /* sin BSO: nunca rompe el juego */ })
      .finally(() => { this._arcLoading = false; });
  }

  startArcadeMusic() {
    try {
      this.kick();
      if (!this.ctx || !this.master || !this.arcWanted || this.arcMute) return;
      if (this.arcPlaying) return;
      // v2.124 · INVARIANTE UNA MELODÍA (sentido BSO→menú): si la BSO va a
      // sonar DE VERDAD, la música del menú se retira ella (v2.122 cubría
      // solo el sentido contrario: menú→duck de la BSO). Así NINGÚN camino
      // futuro que olvide emparejar setMusicWanted/setArcDuck puede poner
      // dos melodías a la vez, ni siquiera con las carreras de re-bind de
      // la Quest al salir/entrar de VR.
      if (!this._arcDucked && this.musicPlaying) this.setMusicWanted(false);
      if (!this._arcBuf) { this._loadArcMusic(); return; }
      const src = this.ctx.createBufferSource();
      src.buffer = this._arcBuf;
      src.loop = true;
      const g = this.ctx.createGain();
      const t = this.ctx.currentTime;
      const vol = Math.max(0.0001,
        (this.arcMute || this._arcDucked) ? 0.0001 : this.arcVol);
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(vol, t + 0.8);
      src.connect(g); g.connect(this.master);
      src.start(t);
      this._arcSrc = src;
      this._arcGain = g;
      this.arcPlaying = true;
      // v2.125 · INVARIANTE UNA MELODÍA (extendido a BSOs PRIVADAS): si un
      // módulo de campeonato con motor propio (oeste/magia) tuviera su BSO
      // viva, la retira EL MISMO — nunca dos melodías a la vez, ni siquiera
      // por carreras de re-bind o caminos futuros sin emparejar.
      try {
        const mod = window.__PP_GAME && window.__PP_GAME.champs &&
          window.__PP_GAME.champs.mod;
        if (mod && typeof mod.musicOff === 'function') mod.musicOff();
      } catch { /* sin módulo: nada que retirar */ }
    } catch { /* nunca rompe el juego */ }
  }

  stopArcadeMusic() {
    const src = this._arcSrc;
    const g = this._arcGain;
    this._arcSrc = null;
    this._arcGain = null;
    this.arcPlaying = false;
    if (!src || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      g.gain.cancelScheduledValues(t);
      g.gain.setValueAtTime(Math.max(0.0001, g.gain.value || this.arcVol), t);
      g.gain.linearRampToValueAtTime(0.0001, t + 0.6);
      window.setTimeout(() => { try { src.stop(); } catch { /* ya parada */ } }, 700);
    } catch { /* */ }
  }

  /** Aplica EN VIVO la ganancia que toca a la BSO según mute/duck/vol.
   *  v2.37: unifica los rampas de setArcVol/setArcMute/setArcDuck. */
  _applyArcGain(ms = 150) {
    if (!this.arcPlaying || !this._arcGain || !this.ctx) return;
    try {
      const t = this.ctx.currentTime;
      const to = (this.arcMute || this._arcDucked)
        ? 0.0001 : Math.max(0.0001, this.arcVol);
      this._arcGain.gain.cancelScheduledValues(t);
      this._arcGain.gain.setValueAtTime(
        Math.max(0.0001, this._arcGain.gain.value || 0.0001), t);
      this._arcGain.gain.linearRampToValueAtTime(to, t + ms / 1000);
    } catch { /* nunca rompe el juego */ }
  }

  /** v2.37: DUCK de la BSO — el MENÚ del campeonato la silencia al abrirse
   *  y al cerrarse vuelve EXACTAMENTE al volumen que ya tenía (sin tocar
   *  arcVol ni el silencio manual del usuario). */
  setArcDuck(duck) {
    duck = !!duck;
    if (duck === !!this._arcDucked) return;
    this._arcDucked = duck;
    if (!duck && this.arcWanted && !this.arcMute && !this.arcPlaying) {
      // el menú abrió antes de que la BSO llegara a sonar: arranca ahora
      this.startArcadeMusic();   // nace silenciosa si sigue el duck
    }
    this._applyArcGain(duck ? 250 : 500);
  }

  /** Volumen de la BSO (0..1) — persistente y aplicado EN VIVO. */
  setArcVol(v) {
    const x = Number.isFinite(v) ? Math.min(1, Math.max(0, v)) : this.arcVol;
    this.arcVol = Math.round(x * 100) / 100;
    try { localStorage.setItem('pp_arcade_vol', String(this.arcVol)); } catch { /* */ }
    if (this.arcVol === 0) { this.setArcMute(true); return; }
    if (this.arcMute) { this.setArcMute(false); }
    this._applyArcGain(150);   // v2.37: respeta el duck del menú
  }

  /** Silencio de la BSO — persistente, sin tocar el volumen guardado. */
  setArcMute(mute) {
    this.arcMute = !!mute;
    try { localStorage.setItem('pp_arcade_mute', this.arcMute ? '1' : '0'); } catch { /* */ }
    if (this.arcMute) this.stopArcadeMusic();
    else if (this.arcWanted) {
      this.startArcadeMusic();      // v2.37: nace silenciosa si el menú la ducks
      this._applyArcGain(150);
    }
  }

  /** Observador de estado por contexto: reintenta y avisa al recover() global. */
  _hookState(ctx) {
    if (!ctx || ctx.__ppHooked) return;
    ctx.__ppHooked = true;
    ctx.addEventListener?.('statechange', () => {
      if (this.ctx !== ctx) return;
      console.info('[Audio] estado ->', ctx.state, this.xrActive ? '(VR)' : '(2D)');
      if (ctx.state === 'running') {
        this._wdFails = 0;
        if (this.xrActive) this.blipAlive();  // el jugador OYE que el audio volvió
      } else if (ctx.state === 'suspended' && this.xrActive) {
        void ctx.resume().catch(() => {});
        window.setTimeout(() => {
          if (this.ctx === ctx && ctx.state !== 'running' && this.xrActive) {
            this.tryFreshRunning('statechange (suspended en VR)');
          }
        }, 900);
      }
    });
  }

  _create() {
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return false;
      try {
        this.ctx = new Ctor({ latencyHint: 'interactive' });
      } catch {
        this.ctx = new Ctor();
      }
      this._wire(this.ctx);
      this._hookState(this.ctx);
      this.rebuilds++;
      console.info('[Audio] contexto creado · estado:', this.ctx.state);
      return true;
    } catch (e) {
      console.warn('[Audio] no se pudo crear el contexto:', e?.message);
      this.ctx = null;
      this.master = null;
      this.noiseBuffer = null;
      return false;
    }
  }

  /** Crea un contexto NUEVO y lo adopta SOLO si consigue arrancar 'running'.
   *  Si no lo consigue, lo descarta y CONSERVA el contexto anterior: el audio
   *  NUNCA queda peor que antes del intento.
   *  (v2.8 cerraba el contexto viejo ANTES de crear el nuevo; si el nuevo
   *  nacía suspendido dentro de la sesión XR de la Quest, el resultado era
   *  mudez total e irreversible. Con esta política eso es imposible.) */
  tryFreshRunning(reason) {
    const now = performance.now();
    if (now - this._lastRebuild < 900) return false;
    this._lastRebuild = now;
    const old = this.ctx;
    let fresh = null;
    try {
      const Ctor = window.AudioContext || window.webkitAudioContext;
      if (!Ctor) return false;
      try { fresh = new Ctor({ latencyHint: 'interactive' }); }
      catch { fresh = new Ctor(); }
    } catch (e) {
      console.warn('[Audio] contexto nuevo falló:', e?.message);
      return false;
    }
    this.rebuilds++;
    console.info('[Audio] contexto nuevo ·', fresh.state, '·', reason);
    this._hookState(fresh);
    let done = false;
    const adopt = () => {
      if (done) return;
      done = true;
      this.master = null;
      this.noiseBuffer = null;
      if (old && old !== fresh) { try { old.close(); } catch { /* ya cerrado */ } }
      this.ctx = fresh;
      try { this._wire(fresh); } catch { /* playOsc/playNoise quedan inermes */ }
      this._wdFails = 0;
      // v2.31: el contexto antiguo se CERRÓ — su música y su murmullo
      // murieron con él. Rearrancarlos en el nuevo (si tocaba haberlos).
      this.musicPlaying = false;
      if (this._amb) { this._amb = null; }
      if (this.musicWanted && this.musicOn) this.startMusic();
      if (this.ambWanted && this.ambience) {
        window.setTimeout(() => this.startMurmur(), 250);
      }
      // v2.36: la BSO del campeonato también muere con el contexto viejo
      this.arcPlaying = false;
      if (this.arcWanted && !this.arcMute) this.startArcadeMusic();
      if (this.xrActive) this.vrBound = true;   // confirmado DENTRO del casco
      console.info('[Audio] contexto NUEVO ADOPTADO (running) ·', reason);
      if (this.xrActive) this.blipAlive();
    };
    const discard = () => {
      if (done) return;
      done = true;
      try { fresh.close(); } catch { /* */ }
      console.info('[Audio] contexto nuevo descartado · se conserva el anterior ·', reason);
    };
    const decide = () => {
      if (done || !fresh) return;
      if (fresh.state === 'running') { adopt(); return; }
      void fresh.resume().catch(() => {});
      // v2.31: 1200 ms (600 se quedaba corto en la Quest; el resume del
      // contexto recién creado puede tardar más en decidirse)
      window.setTimeout(() => {
        if (done || !fresh) return;
        if (fresh.state === 'running') adopt(); else discard();
      }, 1200);
    };
    decide();
    return true;
  }

  /** Blip doble de confirmación: suena cuando el audio (re)arranca dentro de
   *  la sesión VR, para que el jugador sepa que ya hay sonido otra vez. */
  blipAlive() {
    const now = performance.now();
    if (now - this._lastAlive < 4000) return;
    this._lastAlive = now;
    this.playOsc(880, 1320, 0.14, 'sine', 0.35, 0);
    window.setTimeout(() => this.playOsc(1320, 1760, 0.18, 'sine', 0.3, 0), 160);
  }

  /** v2.29 · PRUEBA DE SONIDO del menú (Opciones): arpegio ascendente bien
   *  audible. Si el jugador NO lo oye y vuelve a pulsar (< 5 s), se interpreta
   *  como "no oigo nada": re-vinculación de la salida (contexto nuevo dentro
   *  del gesto del gatillo) + blip de confirmación. Auto-reparación en la
   *  mano del propio jugador, sin depender de la consola. */
  testSound() {
    const now = performance.now();
    const silent = (now - (this._lastSndTest || 0)) < 5000;
    this._lastSndTest = now;
    if (silent) {
      // reparación: la pulsación del gatillo es un gesto válido -> un ctx
      // nuevo creado aquí nace 'running' (se adopta SOLO si arranca)
      this.rebind('prueba de sonido: el jugador no la oyó');
      window.setTimeout(() => {
        this.blipAlive();
        this.playOsc(660, 660, 0.14, 'sine', 0.4, 0);
        window.setTimeout(() => this.playOsc(990, 990, 0.18, 'sine', 0.4, 0), 150);
      }, 250);
      return true;   // true = se intentó reparar
    }
    this.playOsc(523, 523, 0.16, 'sine', 0.45, 0);
    window.setTimeout(() => this.playOsc(659, 659, 0.16, 'sine', 0.45, 0), 170);
    window.setTimeout(() => this.playOsc(784, 784, 0.24, 'sine', 0.45, 0), 340);
    window.setTimeout(() => this.playOsc(1047, 1047, 0.3, 'sine', 0.3, 0), 510);
    return false;
  }

  ensure() {
    if (this.ctx) {
      const st = this.ctx.state;
      if (st === 'running') return;
      // 'closed'/'failed': un resume() ya no sirve NUNCA -> recrear.
      // (Antes este caso quedaba en silencio para siempre: la causa raíz
      // del "no suena nada".)
      if (st === 'closed' || st === 'failed') {
        this.ctx = null;
        this.master = null;
        this.noiseBuffer = null;
        this._create();
        return;
      }
      void this.ctx.resume().catch(() => {});
      return;
    }
    this._create();
  }

  /** Reactiva el audio SIEMPRE antes de sonar. Si tras el resume() el
   *  contexto sigue sin arrancar y ya hubo gesto de usuario, se RECONSTRUYE
   *  dentro de ese gesto: un AudioContext nuevo creado durante el gatillo
   *  de la Quest nace 'running'. */
  kick() {
    this.hadGesture = true;
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      void this.ctx.resume().catch(() => {});
      // Intento recreativo SIN destruir el actual: si el nuevo arranca, se
      // adopta; si no, se conserva el previo (nunca queda peor).
      this.tryFreshRunning('kick (resume sin efecto)');
    }
  }

  /** Preparación AL PULSAR ENTRAR EN VR (gesto garantizado): repara un
   *  contexto enfermo y deja uno 'running' antes de la sesión inmersiva.
   *  NO destruye un contexto sano (era contraproducente en la Quest). */
  prepareVR() {
    this.hadGesture = true;
    this.ensure();
    if (this.ctx && this.ctx.state !== 'running') {
      this.tryFreshRunning('preparación VR (contexto enfermo)');
    }
  }

  /** RE-VINCULACIÓN al entrar/salir de VR: crea un contexto nuevo dentro de
   *  la sesión (nace ligado a la salida activa del casco) y lo adopta SOLO si
   *  arranca 'running'; en caso contrario conserva el anterior. */
  rebind(reason) {
    this.hadGesture = true;
    this.tryFreshRunning(reason || 're-vinculación de salida');
  }

  /** ¿El reloj de audio avanza? (false = estado 'running' pero grafo muerto) */
  clockAlive() {
    return this._ctAdvanced !== false;
  }

  watchdog(dt) {
    this._wdAcc += dt;
    if (this._wdAcc < 0.7) return;
    this._wdAcc = 0;
    if (!this.ctx) {
      if (this.hadGesture) this._create();
      return;
    }
    if (this.ctx.state === 'running') {
      this._wdFails = 0;
      // DETECCIÓN DE GRAFO MUERTO: el estado dice 'running' pero el reloj
      // de audio (currentTime) lleva congelado ~2,8 s (4 ticks). Algunos
      // navegadores/VR dejan el contexto en ese estado zombi al cambiar el
      // foco de la ventana o re-enrutar la salida. Recreación de rescate
      // (adoptar-solo-si-running: nunca queda peor que antes).
      const ct = this.ctx.currentTime;
      this._ctAdvanced = Number.isFinite(ct) && ct > this._lastCT + 1e-4;
      this._lastCT = ct;
      if (this._ctAdvanced) {
        this._ctStalls = 0;
      } else if (++this._ctStalls >= 4 && this.hadGesture) {
        this._ctStalls = 0;
        this.tryFreshRunning('watchdog (reloj de audio congelado)');
      }
      return;
    }
    this.ctx.resume().catch(() => {});
    this._wdFails++;
    if (this._wdFails >= 5 && this.hadGesture) {
      this.tryFreshRunning('watchdog (suspended persistente)');
    }
  }

  panNode(pan) {
    if (!this.ctx || !this.master) return null;
    const p = this.ctx.createStereoPanner();
    // NaN/Infinity -> 0 (un valor no finito aquí LANZA y mata el frame)
    p.pan.value = Number.isFinite(pan) ? Math.max(-1, Math.min(1, pan)) : 0;
    p.connect(this.master);
    return p;
  }

  playOsc(freq, endFreq, dur, type, gain, pan) {
    try {
      this.kick();
      if (!this.ctx || !this.master) return;
      if (![freq, endFreq, dur, gain].every(Number.isFinite)) return;
      const dest = this.panNode(pan);
      if (!dest) return;
      const t = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const g = this.ctx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(Math.max(20, freq), t);
      osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), t + dur);
      g.gain.setValueAtTime(Math.max(0.001, gain), t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      osc.connect(g); g.connect(dest);
      osc.start(t); osc.stop(t + dur + 0.02);
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  playNoise(dur, filterFreq, q, gain, pan, type = 'bandpass') {
    try {
      this.kick();
      if (!this.ctx || !this.noiseBuffer) return;
      if (![dur, filterFreq, q, gain].every(Number.isFinite)) return;
      const dest = this.panNode(pan);
      if (!dest) return;
      const t = this.ctx.currentTime;
      const src = this.ctx.createBufferSource();
      src.buffer = this.noiseBuffer;
      const filter = this.ctx.createBiquadFilter();
      filter.type = type;
      filter.frequency.value = filterFreq;
      filter.Q.value = q;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(Math.max(0.001, gain), t);
      g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
      src.connect(filter); filter.connect(g); g.connect(dest);
      src.start(t); src.stop(t + dur + 0.02);
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }
  paddle(pan, strength) {
    const s = Math.max(0.15, Math.min(1, strength));
    this.playNoise(0.05, 1400, 1.2, 0.55 * s, pan);
    this.playOsc(190 - 40 * s, 110, 0.09, 'triangle', 0.5 * s, pan);
  }
  tableBounce(pan, strength) {
    const s = Math.max(0.1, Math.min(1, strength));
    this.playOsc(950, 700, 0.05, 'sine', 0.4 * s, pan);
    this.playNoise(0.02, 3000, 2, 0.18 * s, pan);
  }
  net(pan) {
    this.playOsc(210, 150, 0.1, 'sine', 0.35, pan);
    this.playNoise(0.06, 420, 1, 0.25, pan, 'lowpass');
  }
  thud(pan, strength) {
    const s = Math.max(0.05, Math.min(1, strength));
    this.playOsc(140, 90, 0.09, 'sine', 0.28 * s, pan);
  }
  serve() { this.playNoise(0.14, 650, 0.8, 0.16, 0); }
  /** Pitido corto del punto muerto del saque (señal para golpear). */
  tick() { this.playOsc(1320, 1150, 0.05, 'sine', 0.22, 0); }

  /* ---------- SFX DE PERSONALIDAD DEL RIVAL (ARCADE) ----------
   * Cada estado del personaje del campeonato tiene su propia voz.
   * v2.35: síntesis con FORMANTES (glotis de sierra + 2 bandpass por
   * vocal) — suena a VOZ, no a bleeps — y bus de voz más presente (x1.6).
   * Si el campeonato declara archivos en el manifest ("sounds"), esos
   * data URLs se decodifican y suenan EN SU LUGAR (fallback: síntesis).
   * El audio NUNCA rompe el bucle del juego (todo dentro de try/catch). */
  rivalSfx(kind) {
    try {
      this.kick();
      if (!this.ctx || !this.master) return;
      if (!kind) return;
      // throttle: gap global + gap por tipo (las risas no se ametrallan)
      const nowMs = Date.now();
      const GAPS = { laugh: 3200, crazy: 3600, angry: 3600, surprised: 2200,
        sad: 3500, panic: 3500, taunt: 3000, victory: 4000, present: 4000,
        powerup: 1600 };
      if (this._rivalLastG && nowMs - this._rivalLastG < 250 &&
          kind !== 'powerup') return;   // v2.35: el aviso de poder NUNCA se calla
      if (this._rivalLast && nowMs - (this._rivalLast[kind] || 0) < (GAPS[kind] || 3000)) return;
      this._rivalLastG = nowMs;
      this._rivalLast = this._rivalLast || {};
      this._rivalLast[kind] = nowMs;
      // override por archivo del campeonato (si existe, suena el archivo;
      // si ya falló su decodificación, se queda en la síntesis para siempre)
      let url = '';
      try {
        url = (window.__PP_ARCADE_DATA && window.__PP_ARCADE_DATA.sounds &&
          window.__PP_ARCADE_DATA.sounds[kind]) || '';
      } catch { /* */ }
      this._rivalBufs = this._rivalBufs || {};
      const failedBuf = !!(url && this._rivalBufs[kind] && this._rivalBufs[kind].failed);
      if (url && !failedBuf) { this._playRivalBuffer(kind, url); return; }
      const out = this.panNode(0);
      if (!out) return;
      const ctx = this.ctx;
      const now = ctx.currentTime;
      // v2.35: bus de voz del rival — más presencia que el resto de SFX
      const bus = ctx.createGain();
      bus.gain.value = 1.6;
      bus.connect(out);
      // blip del rival: oscilador con envolvente, opcionalmente filtrado
      const blip = (t, f0, f1, dur, type, gain, lp) => {
        const osc = ctx.createOscillator();
        const g = ctx.createGain();
        osc.type = type || 'triangle';
        osc.frequency.setValueAtTime(Math.max(20, f0), t);
        osc.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
        g.gain.setValueAtTime(0.001, t);
        g.gain.exponentialRampToValueAtTime(Math.max(0.002, gain), t + 0.015);
        g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
        osc.connect(g);
        if (lp) {
          const f = ctx.createBiquadFilter();
          f.type = 'lowpass';
          f.frequency.value = lp;
          g.connect(f); f.connect(bus);
        } else {
          g.connect(bus);
        }
        osc.start(t); osc.stop(t + dur + 0.03);
      };
      // ráfaga de ruido filtrado (siseos, platillos, gruñido sucio)
      const rush = (t, dur, freq, q, gain, type) => {
        if (!this.noiseBuffer) return;
        const src = ctx.createBufferSource();
        src.buffer = this.noiseBuffer;
        src.loop = true;
        const f = ctx.createBiquadFilter();
        f.type = type || 'bandpass';
        f.frequency.value = freq;
        f.Q.value = q;
        const g = ctx.createGain();
        g.gain.setValueAtTime(Math.max(0.001, gain), t);
        g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
        src.connect(f); f.connect(g); g.connect(bus);
        src.start(t); src.stop(t + dur + 0.02);
      };
      // v2.35: sílaba CANTADA con formantes — glotis (sierra con contorno
      // de tono) filtrada por 2 formantes de la vocal + cuerpo apagado.
      // Es lo que hace que suene a risa humana y no a robot.
      const FORMANTS = { a: [780, 1240], e: [540, 1900], i: [330, 2400],
        o: [500, 900], u: [360, 700] };
      const vox = (t, dur, f0, f1, vow, gain) => {
        const gl = ctx.createOscillator();
        gl.type = 'sawtooth';
        gl.frequency.setValueAtTime(Math.max(60, f0), t);
        gl.frequency.exponentialRampToValueAtTime(Math.max(60, f1), t + dur);
        const env = ctx.createGain();
        env.gain.setValueAtTime(0.001, t);
        env.gain.exponentialRampToValueAtTime(Math.max(0.002, gain), t + Math.min(0.035, dur * 0.35));
        env.gain.setValueAtTime(Math.max(0.002, gain), t + dur * 0.6);
        env.gain.exponentialRampToValueAtTime(0.0001, t + dur);
        const F = FORMANTS[vow] || FORMANTS.a;
        for (let fi = 0; fi < 2; fi++) {
          const bp = ctx.createBiquadFilter();
          bp.type = 'bandpass';
          bp.frequency.value = F[fi];
          bp.Q.value = fi === 0 ? 6.5 : 9;
          const bg = ctx.createGain();
          bg.gain.value = fi === 0 ? 1.0 : 0.5;
          gl.connect(bp); bp.connect(bg); bg.connect(bus);
        }
        const lp = ctx.createBiquadFilter();
        lp.type = 'lowpass';
        lp.frequency.value = 950;
        const lg = ctx.createGain();
        lg.gain.value = 0.35;
        gl.connect(lp); lp.connect(lg); lg.connect(bus);
        gl.start(t); gl.stop(t + dur + 0.03);
      };
      switch (kind) {
        case 'present': {
          // fanfarria de circo: arpegio C-E-G-C + platillo
          blip(now, 523, 523, 0.12, 'square', 0.10);
          blip(now + 0.13, 659, 659, 0.12, 'square', 0.10);
          blip(now + 0.26, 784, 784, 0.12, 'square', 0.10);
          blip(now + 0.39, 1046, 1046, 0.34, 'square', 0.11);
          rush(now + 0.39, 0.4, 6500, 0.7, 0.05);
          break;
        }
        case 'laugh': {
          // risa burlona "¡je, je, jeee!" — sílabas REALES de voz
          vox(now, 0.15, 305, 250, 'e', 0.9);
          vox(now + 0.17, 0.15, 288, 236, 'e', 0.9);
          vox(now + 0.34, 0.15, 302, 246, 'e', 0.85);
          vox(now + 0.52, 0.42, 275, 148, 'e', 1.0);
          break;
        }
        case 'crazy': {
          // risa loca: carcajada "ja-ja-ja" que SE ACELERA y SUBE de tono
          let t = now;
          for (let i = 0; i < 7; i++) {
            const f = 215 + i * 38;
            vox(t, 0.12, f, f * 0.86, 'a', 0.8 + i * 0.045);
            t += 0.15 - i * 0.012;
          }
          rush(t, 0.3, 5200, 0.8, 0.05);
          break;
        }
        case 'angry': {
          // gruñido grave con temblor (LFO en la ganancia) + voz airada
          const osc = ctx.createOscillator();
          const g = ctx.createGain();
          const lfo = ctx.createOscillator();
          const lg = ctx.createGain();
          const lp = ctx.createBiquadFilter();
          osc.type = 'sawtooth';
          osc.frequency.setValueAtTime(96, now);
          osc.frequency.exponentialRampToValueAtTime(66, now + 0.85);
          lp.type = 'lowpass'; lp.frequency.value = 420;
          g.gain.setValueAtTime(0.001, now);
          g.gain.exponentialRampToValueAtTime(0.24, now + 0.05);
          g.gain.exponentialRampToValueAtTime(0.0001, now + 0.9);
          lfo.frequency.value = 11; lg.gain.value = 0.09;
          lfo.connect(lg); lg.connect(g.gain);
          osc.connect(lp); lp.connect(g); g.connect(bus);
          osc.start(now); osc.stop(now + 0.95);
          lfo.start(now); lfo.stop(now + 0.95);
          rush(now, 0.55, 260, 0.8, 0.10, 'lowpass');
          vox(now + 0.12, 0.5, 150, 118, 'o', 0.5);
          break;
        }
        case 'surprised': {
          // "¡Oh!" — vocal con caída real de tono + aire al principio
          rush(now, 0.07, 2400, 0.6, 0.05);
          vox(now + 0.04, 0.34, 350, 165, 'o', 1.0);
          break;
        }
        case 'sad': {
          // trombón triste "va·va·vaaah" descendente
          blip(now, 392, 370, 0.26, 'triangle', 0.15);
          blip(now + 0.3, 330, 300, 0.26, 'triangle', 0.15);
          blip(now + 0.6, 262, 185, 0.55, 'triangle', 0.16);
          break;
        }
        case 'panic': {
          // "wah wah wah wah" agitado + aleteo de ruido
          for (let i = 0; i < 4; i++) {
            const f = i % 2 === 0 ? 520 : 385;
            blip(now + i * 0.16, f, f * 0.85, 0.13, 'square', 0.10, 1500);
          }
          rush(now + 0.62, 0.35, 3800, 0.9, 0.04);
          break;
        }
        case 'taunt': {
          // "ña·ña·ña·ña" burlona de patio de colegio (voz)
          vox(now, 0.11, 400, 392, 'e', 0.7);
          vox(now + 0.13, 0.11, 336, 330, 'i', 0.7);
          vox(now + 0.26, 0.11, 400, 392, 'e', 0.7);
          vox(now + 0.39, 0.2, 336, 295, 'i', 0.78);
          break;
        }
        case 'victory': {
          // fanfarria del vencedor + dos "je je" de desprecio
          blip(now, 392, 392, 0.16, 'square', 0.11);
          blip(now + 0.15, 523, 523, 0.16, 'square', 0.11);
          blip(now + 0.3, 659, 659, 0.16, 'square', 0.11);
          blip(now + 0.45, 784, 784, 0.5, 'square', 0.12);
          rush(now + 0.45, 0.5, 6800, 0.7, 0.05);
          vox(now + 0.98, 0.15, 300, 248, 'e', 0.8);
          vox(now + 1.15, 0.15, 300, 232, 'e', 0.8);
          break;
        }
        case 'powerup': {
          // v2.35: ¡SUPER PODER! — riser ascendente + destello + "¡ah!"
          blip(now, 190, 780, 0.34, 'sawtooth', 0.17, 3200);
          blip(now + 0.3, 660, 1320, 0.3, 'square', 0.13);
          rush(now + 0.28, 0.45, 6000, 0.7, 0.06);
          vox(now + 0.42, 0.32, 420, 540, 'a', 0.95);
          break;
        }
        default: break;
      }
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  /** v2.34: override del SFX por ARCHIVO (data URL del campeonato).
   *  Decodifica una vez por tipo+contexto y la reproduce; si falla el
   *  decode, la síntesis procedural queda como respaldo. */
  _playRivalBuffer(kind, url) {
    try {
      if (!this.ctx) return;
      this._rivalBufs = this._rivalBufs || {};
      const key = kind;
      const cached = this._rivalBufs[key];
      const play = (buf) => {
        try {
          if (!this.ctx || !this.master) return;
          const out = this.panNode(0);
          if (!out) return;
          const src = this.ctx.createBufferSource();
          src.buffer = buf;
          const g = this.ctx.createGain();
          g.gain.value = 1.0;   // v2.35: las voces de archivo, bien presentes
          src.connect(g); g.connect(out);
          src.start();
        } catch { /* */ }
      };
      if (cached && cached.ctx === this.ctx && cached.buf) { play(cached.buf); return; }
      if (cached && (cached.busy || cached.failed)) return;
      const entry = { ctx: this.ctx, buf: null, busy: true };
      this._rivalBufs[key] = entry;
      fetch(url)
        .then((r) => r.arrayBuffer())
        .then((ab) => this.ctx.decodeAudioData(ab))
        .then((buf) => { entry.buf = buf; entry.busy = false; play(buf); })
        .catch(() => { entry.busy = false; entry.failed = true; this.rivalSfxSynth(kind); });
    } catch { /* */ }
  }

  /** v2.34: ruta de síntesis DIRECTA (sin throttles ni overrides) usada
   *  como respaldo cuando un archivo del campeonato no se pudo decodificar. */
  rivalSfxSynth(kind) {
    try {
      this._rivalLast = this._rivalLast || {};
      this._rivalLast[kind] = 0;   // permite reintentar el sonido ya throttled
      this.rivalSfx(kind);
    } catch { /* */ }
  }

  point(win) {
    if (win) {
      this.playOsc(660, 660, 0.12, 'sine', 0.3, -0.3);
      window.setTimeout(() => this.playOsc(880, 880, 0.18, 'sine', 0.3, -0.3), 110);
    } else {
      this.playOsc(440, 440, 0.12, 'sine', 0.28, 0.3);
      window.setTimeout(() => this.playOsc(330, 330, 0.2, 'sine', 0.28, 0.3), 110);
    }
  }

  /** FANFARRIA de fin de partido.
   *  Victoria: arpegio mayor ascendente (C5-E5-G5) + acorde final brillante
   *  con capa de octava y platillo -> "¡ta-da!".
   *  Derrota: "trombón triste" descendente (bend hacia abajo + lowpass). */
  fanfare(win) {
    try {
      this.kick();
      if (!this.ctx || !this.master) return;
      const t0 = this.ctx.currentTime + 0.06;
      const seq = win
        ? [
            [523.25, 0.00, 0.17, 0.30],
            [659.25, 0.14, 0.17, 0.30],
            [783.99, 0.28, 0.17, 0.32],
            [1046.50, 0.42, 0.75, 0.34],
            [1318.51, 0.42, 0.75, 0.20],
            [1567.98, 0.62, 0.55, 0.14],
          ]
        : [
            [329.63, 0.00, 0.32, 0.28],
            [293.66, 0.32, 0.32, 0.28],
            [261.63, 0.64, 0.32, 0.28],
            [246.94, 0.96, 0.32, 0.26],
            [220.00, 1.28, 0.95, 0.30],
          ];
      for (const [f, dt, dur, vol] of seq) {
        const t = t0 + dt;
        const o = this.ctx.createOscillator();
        const g = this.ctx.createGain();
        o.type = win ? 'triangle' : 'sawtooth';
        o.frequency.setValueAtTime(f, t);
        if (!win) o.frequency.linearRampToValueAtTime(f * 0.93, t + dur);
        g.gain.setValueAtTime(0.0001, t);
        g.gain.linearRampToValueAtTime(vol, t + 0.02);
        g.gain.setValueAtTime(vol, t + Math.max(0.03, dur - 0.07));
        g.gain.linearRampToValueAtTime(0.0001, t + dur);
        o.connect(g);
        if (win) {
          g.connect(this.master);
        } else {
          const lp = this.ctx.createBiquadFilter();
          lp.type = 'lowpass';
          lp.frequency.value = 900;
          g.connect(lp); lp.connect(this.master);
        }
        o.start(t); o.stop(t + dur + 0.05);
        if (win) {
          // capa de brillo una octava arriba
          const o2 = this.ctx.createOscillator();
          const g2 = this.ctx.createGain();
          o2.type = 'sine';
          o2.frequency.setValueAtTime(f * 2, t);
          g2.gain.setValueAtTime(0.0001, t);
          g2.gain.linearRampToValueAtTime(vol * 0.32, t + 0.02);
          g2.gain.linearRampToValueAtTime(0.0001, t + dur);
          o2.connect(g2); g2.connect(this.master);
          o2.start(t); o2.stop(t + dur + 0.05);
        }
      }
      if (win) this.playNoise(0.4, 6200, 0.7, 0.2, 0, 'highpass');
    } catch { /* el audio NUNCA rompe el bucle del juego */ }
  }

  /* ================= AMBIENTE DE TORNEO (v2.11) ================= */

  /** Activa/desactiva el ambiente (murmullo + aplausos + megafonía).
   *  Se guarda en localStorage para recordar la preferencia. */
  setAmbience(on) {
    this.ambience = !!on;
    try { localStorage.setItem('ppxr_amb_v1', this.ambience ? '1' : '0'); } catch { /* */ }
    if (!this.ambience) this.stopMurmur();
  }

  /** v2.22 · Conmutador del megáfono del marcador (chime + voz del narrador),
   *  persistente e independiente del ambiente de torneo. */
  setVoice(on) {
    this.voice = !!on;
    try { localStorage.setItem('ppxr_voz_v1', this.voice ? '1' : '0'); } catch { /* */ }
  }

  /** Murmullo de público de fondo: bucle de ruido filtrado con vaivén lento.
   *  Se arranca al entrar en VR y se detiene al salir / apagar el ambiente. */
  startMurmur() {
    try {
      this.kick();
      this.ambWanted = true;   // v2.31: debe sobrevivir a un swap de contexto
      if (!this.ctx || !this.master || this._amb || !this.ambience) return;
      if (!this._ambBuffer) {
        const len = Math.floor(this.ctx.sampleRate * 2);
        const buf = this.ctx.createBuffer(1, len, this.ctx.sampleRate);
        const d = buf.getChannelData(0);
        let acc = 0;
        for (let i = 0; i < len; i++) {
          // ruido rosa "grumoso": media móvil = murmullo, no siseo
          acc = acc * 0.92 + (Math.random() * 2 - 1) * 0.08;
          d[i] = acc * 8;
        }
        this._ambBuffer = buf;
      }
      const src = this.ctx.createBufferSource();
      src.buffer = this._ambBuffer;
      src.loop = true;
      const lp = this.ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.value = 520;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(0.0001, this.ctx.currentTime);
      g.gain.linearRampToValueAtTime(0.05, this.ctx.currentTime + 1.5);
      const lfo = this.ctx.createOscillator();
      lfo.frequency.value = 0.13;
      const lfoG = this.ctx.createGain();
      lfoG.gain.value = 0.02;
      lfo.connect(lfoG); lfoG.connect(g.gain);
      src.connect(lp); lp.connect(g); g.connect(this.ambBus || this.master);
      src.start();
      lfo.start();
      this._amb = { src, lfo, gain: g };
    } catch { /* nunca rompe el juego */ }
  }

  stopMurmur() {
    this.ambWanted = false;   // v2.31
    const amb = this._amb;
    if (!amb || !this.ctx) return;
    this._amb = null;
    try {
      const t = this.ctx.currentTime;
      amb.gain.gain.cancelScheduledValues(t);
      amb.gain.gain.setValueAtTime(amb.gain.gain.value, t);
      amb.gain.gain.linearRampToValueAtTime(0.0001, t + 0.8);
      window.setTimeout(() => {
        try { amb.src.stop(); amb.lfo.stop(); } catch { /* ya parado */ }
      }, 900);
    } catch { /* */ }
  }

  /** APLAUSOS sintetizados: ruido con envolvente "espiky" aleatoria
   *  (cientos de micro-chasquidos = público aplaudiendo). big = ovación. */
  applause(big) {
    try {
      this.kick();
      if (!this.ctx || !this.master || !this.noiseBuffer || !this.ambience) return;
      if (![this.ctx.currentTime].every(Number.isFinite)) return;
      const t = this.ctx.currentTime + 0.02;
      const dur = big ? 2.6 : 1.15;
      const vol = big ? 0.5 : 0.3;
      for (let layer = 0; layer < (big ? 2 : 1); layer++) {
        const src = this.ctx.createBufferSource();
        src.buffer = this.noiseBuffer;
        src.loop = true;
        const bp = this.ctx.createBiquadFilter();
        bp.type = 'bandpass';
        bp.frequency.value = 1500 + Math.random() * 700;
        bp.Q.value = 0.55;
        const g = this.ctx.createGain();
        const N = 72;
        const curve = new Float32Array(N);
        for (let i = 0; i < N; i++) {
          const spiky = Math.random() < 0.55 ? Math.random() : Math.random() * 0.3;
          curve[i] = spiky;
        }
        // arranque rápido y cola que se apaga
        for (let i = 0; i < N; i++) {
          const f = i / (N - 1);
          curve[i] *= Math.min(1, f * 6) * (1 - f * f);
        }
        const t0 = t + layer * 0.18;
        g.gain.setValueAtTime(0.0001, t0);
        g.gain.setValueCurveAtTime(curve.map((v) => Math.max(0.0001, v * vol)), t0, dur * 0.82);
        g.gain.setValueAtTime(0.0001, t0 + dur * 0.82 + 0.01);
        g.gain.linearRampToValueAtTime(0.0001, t0 + dur);
        const pan = this.ctx.createStereoPanner();
        pan.pan.value = layer === 0 ? -0.35 : 0.35;
        src.connect(bp); bp.connect(g); g.connect(pan); pan.connect(this.ambBus || this.master);
        src.start(t0);
        src.stop(t0 + dur + 0.15);
      }
    } catch { /* */ }
  }

  /** "Ohh" del público (red, bola fuera…): dos sierras graves con formantes
   *  de vocal, hinchándose y apagándose. Throttle interno de 3,5 s. */
  ohh() {
    try {
      const now = performance.now();
      if (now - this._lastOhh < 3500) return;
      this._lastOhh = now;
      this.kick();
      if (!this.ctx || !this.master || !this.ambience) return;
      const t = this.ctx.currentTime + 0.02;
      const g = this.ctx.createGain();
      g.gain.setValueAtTime(0.0001, t);
      g.gain.linearRampToValueAtTime(0.15, t + 0.24);
      g.gain.setValueAtTime(0.15, t + 0.42);
      g.gain.exponentialRampToValueAtTime(0.0001, t + 0.95);
      for (const [f0, fq, q] of [[112, 470, 2.2], [138, 920, 2.6]]) {
        const o = this.ctx.createOscillator();
        o.type = 'sawtooth';
        o.frequency.setValueAtTime(f0, t);
        o.frequency.linearRampToValueAtTime(f0 * 0.82, t + 0.95);
        const bp = this.ctx.createBiquadFilter();
        bp.type = 'bandpass';
        bp.frequency.value = fq;
        bp.Q.value = q;
        o.connect(bp); bp.connect(g);
        o.start(t); o.stop(t + 1.05);
      }
      g.connect(this.ambBus || this.master);
    } catch { /* */ }
  }

  /* ---------- v2.20/2.27 · VOZ REAL DEL MEGÁFONO ----------
   * Meta Quest Browser NO reproduce speechSynthesis durante la sesión
   * inmersiva (en la pestaña 2D del escritorio sí). La voz del marcador
   * pasa a ser audio real (banco de voz Piper es-ES/en-US → Opus) por
   * WebAudio, la misma vía que ya se oye en el visor (efectos, chimes,
   * público). v2.27: el banco se elige según el idioma (VOICE_B64S) y se
   * puede recargar en caliente al cambiar de idioma (reloadVoice). */

  /** Banco de voz base64 del idioma activo (con respaldos por si falta). */
  _voiceBank() {
    const banks = (typeof VOICE_B64S !== 'undefined') ? VOICE_B64S
      : { es: (typeof VOICE_B64 !== 'undefined' ? VOICE_B64 : null), en: (typeof VOICE_B64_EN !== 'undefined' ? VOICE_B64_EN : null) };
    return banks[TLang()] || banks.es || banks.en || null;
  }

  /** v2.27: recarga del banco de voz (cambio de idioma en caliente). */
  reloadVoice() {
    if (this.ctx) this._loadVoice(this.ctx);
  }

  /** Decodifica el banco de voz del idioma activo para el contexto dado.
   *  v2.120: los AudioBuffer son válidos en CUALQUIER contexto (igual que la
   *  música de _loadMusic) — se decodifican UNA vez por idioma y se reusan
   *  en cada _wire(): entrar/salir de VR ya no re-decodifica el banco entero.
   *  Normalización 0.60. */
  _loadVoice(ctx) {
    this.vb = null; this.vbGain = null; this.vbTrim = null; this.vbCtx = ctx;
    const BANK = this._voiceBank();
    if (!BANK || !ctx || !ctx.decodeAudioData) return;
    const lang = TLang();
    const C = (this._voiceCache && this._voiceCache.lang === lang)
      ? this._voiceCache : null;
    if (C && C.bufs && C.bufs.size) {
      this.vb = C.bufs; this.vbGain = C.gains; this.vbTrim = C.trims;
      console.info('[Audio] banco de voz listo (caché ' + lang + ') ·',
        C.bufs.size, 'fragmentos');
      return;
    }
    const keys = Object.keys(BANK);
    if (!keys.length) return;
    const bank = new Map();
    const gains = new Map();
    const trims = new Map();
    let pend = keys.length;
    const done = () => {
      if (pend > 0) return;
      if (this.vbCtx === ctx && bank.size) {
        this.vb = bank;
        this.vbGain = gains;
        this.vbTrim = trims;
        this._voiceCache = { lang, bufs: bank, gains, trims };
        console.info('[Audio] banco de voz listo (' + TLang() + ') ·', bank.size, 'fragmentos · silencios recortados');
      }
    };
    for (const k of keys) {
      try {
        const bin = atob(BANK[k]);
        const ab = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) ab[i] = bin.charCodeAt(i);
        const onOk = (buf) => {
          try {
            let peak = 0;
            const ch = buf.getChannelData(0);
            for (let i = 0; i < ch.length; i += 16) {
              const v = Math.abs(ch[i]);
              if (v > peak) peak = v;
            }
            bank.set(k, buf);
            gains.set(k, peak > 1e-4 ? Math.min(2.4, Math.max(0.35, 0.6 / peak)) : 1);
            // v2.22 · RECORTE DE SILENCIOS: Piper deja ~0,1-0,3 s de silencio
            // a cada lado de cada fragmento; al encadenarlos se acumulaba una
            // pausa artificial (el "corte" antes de la segunda cifra).
            // Detectamos el primer/último muestra con voz y guardamos [t0,t1];
            // speakPlan reproducirá solo ese tramo.
            try {
              const sr = buf.sampleRate || 44100;
              const thr = Math.max(0.012, peak * 0.07);   // umbral relativo al pico
              const n = ch.length;
              let i0 = 0, i1 = n - 1;
              while (i0 < n && Math.abs(ch[i0]) < thr) i0++;
              while (i1 > i0 && Math.abs(ch[i1]) < thr) i1--;
              if (i1 > i0) {
                const t0 = Math.max(0, i0 / sr - 0.010);   // pre-roll corto
                const t1 = Math.min(buf.duration, i1 / sr + 0.030); // cola natural
                if (t1 - t0 > 0.04) trims.set(k, [t0, t1]);
              }
            } catch { /* sin recorte: se reproduce el buffer entero */ }
          } catch { /* */ }
          pend--; done();
        };
        const onErr = () => { pend--; done(); };
        try { ctx.decodeAudioData(ab.buffer.slice(0)).then(onOk, onErr); }
        catch { onErr(); }
      } catch { pend--; done(); }
    }
  }

  /** Normaliza texto para comparar: minúsculas, sin acentos ni signos. */
  _normVoice(s) {
    return String(s).toLowerCase()
      .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
  }

  /** Texto del anuncio -> plan [{k, gap}] de fragmentos, o null si el
   *  texto no está cubierto por el banco (respaldo speechSynthesis).
   *  v2.27: patrones POR IDIOMA (el texto llega en el idioma activo); los
   *  planes resultantes usan claves compartidas es/en. */
  voicePlan(text) {
    try {
      const s = this._normVoice(text);
      if (!s) return null;
      // v2.23: gaps intra-frase MUY cortos — con el buffer compuesto el silencio
      // entre palabras es EXACTAMENTE este (sin colas de Piper añadidas).
      const P = (keys, gaps) => keys.map((k, i) => ({ k, gap: (gaps && gaps[i]) || 0.042 }));
      const lang = (typeof TLang === 'function') ? TLang() : 'es';
      const num = (v) => voiceNumPlan(v, lang);
      const full = (VOICE_FULL[lang] || VOICE_FULL.es)[s];
      if (full) return P(full);
      let m;
      if (lang === 'en') {
        // Achievement unlocked: <name>
        m = s.match(/^achievement unlocked (.+)$/);
        if (m) {
          const ach = (VOICE_ACH.en || {})[m[1]];
          return ach ? P(['logro_desbloqueado', ach], [0.18]) : null;
        }
        // Rally of <N> hits. New record!
        m = s.match(/^rally of (\d+) hits new record$/);
        if (m) {
          const n1 = num(m[1]);
          return n1 ? P(['rallye_de', ...n1, 'golpes', 'nuevo_record'], [0.03, 0.03, 0.26]) : null;
        }
        // <p> to <q>, serve for you / your opponent / the machine
        m = s.match(/^(\d+) to (\d+) serve for (you|your opponent|the machine)$/);
        if (m) {
          const n1 = num(m[1]);
          const n2 = num(m[2]);
          const who = m[3] === 'you' ? 'saque_para_ti'
            : m[3] === 'your opponent' ? 'saque_para_rival' : 'saque_para_maquina';
          return (n1 && n2) ? P([...n1, 'a', ...n2, who], [0.036, 0.036, 0.26]) : null;
        }
        // Victory! <p> to <q>
        m = s.match(/^victory (\d+) to (\d+)$/);
        if (m) {
          const n1 = num(m[1]);
          const n2 = num(m[2]);
          return (n1 && n2) ? P(['victoria', ...n1, 'a', ...n2], [0.1, 0.036, 0.036]) : null;
        }
        // Match for the machine / your opponent. <q> to <p>
        m = s.match(/^match for (the machine|your opponent) (\d+) to (\d+)$/);
        if (m) {
          const n1 = num(m[2]);
          const n2 = num(m[3]);
          const who = m[1] === 'your opponent' ? 'partido_para_rival' : 'partido_para_cpu';
          return (n1 && n2) ? P([who, ...n1, 'a', ...n2], [0.26, 0.036, 0.036]) : null;
        }
        return null;
      }
      // ---- castellano ----
      // ¡Logro desbloqueado: <nombre>!
      m = s.match(/^logro desbloqueado (.+)$/);
      if (m) {
        const ach = (VOICE_ACH.es || {})[m[1]];
        return ach ? P(['logro_desbloqueado', ach], [0.18]) : null;
      }
      // ¡Rallye de <N> golpes! Nuevo récord
      m = s.match(/^rallye de (\d+) golpes nuevo record$/);
      if (m) {
        const n1 = num(m[1]);
        return n1 ? P(['rallye_de', ...n1, 'golpes', 'nuevo_record'], [0.03, 0.03, 0.26]) : null;
      }
      // <p> a <q>, saque para ti / tu rival / la máquina
      m = s.match(/^(\d+) a (\d+) saque para (ti|tu rival|la maquina)$/);
      if (m) {
        const n1 = num(m[1]);
        const n2 = num(m[2]);
        const quien = m[3] === 'ti' ? 'saque_para_ti'
          : m[3] === 'tu rival' ? 'saque_para_rival' : 'saque_para_maquina';
        return (n1 && n2) ? P([...n1, 'a', ...n2, quien], [0.036, 0.036, 0.26]) : null;
      }
      // ¡Victoria! <p> a <q>
      m = s.match(/^victoria (\d+) a (\d+)$/);
      if (m) {
        const n1 = num(m[1]);
        const n2 = num(m[2]);
        return (n1 && n2) ? P(['victoria', ...n1, 'a', ...n2], [0.1, 0.036, 0.036]) : null;
      }
      // Partido para la CPU / tu rival. <p> a <q>
      m = s.match(/^partido para (la cpu|tu rival) (\d+) a (\d+)$/);
      if (m) {
        const n1 = num(m[2]);
        const n2 = num(m[3]);
        const quien = m[1] === 'tu rival' ? 'partido_para_rival' : 'partido_para_cpu';
        return (n1 && n2) ? P([quien, ...n1, 'a', ...n2], [0.26, 0.036, 0.036]) : null;
      }
      return null;
    } catch { return null; }
  }

  /** Locución del plan. v2.23 · BUFFER COMPUESTO: en lugar de encadenar N
   *  AudioBufferSourceNodes (cada frontera era un mini-corte audible en el
   *  visor — el "corte antes de la segunda cifra"), se COPIA cada fragmento
   *  (recortado por vbTrim, normalizado y con micro-fades de 4/9 ms para
   *  eliminar chasquidos en las juntas) dentro de UN solo AudioBuffer que se
   *  reproduce con UNA única fuente: cero discontinuidades de planificación,
   *  cifras fluidas y las pausas EXACTAS del plan. */
  speakPlan(plan) {
    try {
      if (!plan || !plan.length || !this.ctx || !this.master) return false;
      if (!this.vb || this.vbCtx !== this.ctx) return false;
      const sr = this.ctx.sampleRate;
      const HEAD = 0.34;                      // deja sonar el chime primero
      const items = [];
      let total = HEAD;
      for (const a of plan) {
        const buf = this.vb.get(a.k);
        if (!buf) return false;
        const tr = (this.vbTrim && this.vbTrim.get(a.k)) || null;
        const off = tr ? tr[0] : 0;
        const dur = tr ? Math.max(0.04, tr[1] - tr[0]) : buf.duration;
        const g = (this.vbGain && this.vbGain.get(a.k)) || 1;
        items.push({ buf, off, dur, g, gap: a.gap || 0.042 });
        total += dur + (a.gap || 0.042);
      }
      const n = Math.ceil((total + 0.12) * sr);
      const out = this.ctx.createBuffer(1, n, sr);
      const dst = out.getChannelData(0);
      const fIn = Math.max(1, Math.floor(0.004 * sr));
      const fOut = Math.max(1, Math.floor(0.009 * sr));
      let w = Math.floor(HEAD * sr);
      for (const it of items) {
        const src = it.buf.getChannelData(0);
        const r = it.buf.sampleRate / sr;     // re-muestreo lineal si difiere
        const i0 = Math.floor(it.off * it.buf.sampleRate);
        const len = Math.min(Math.floor(it.dur * it.buf.sampleRate), src.length - i0);
        for (let i = 0; i < len; i++) {
          const s = src[i0 + i] * it.g;
          let env = 1;
          if (i < fIn) env = i / fIn;         // fade-in: adiós los chasquidos
          const rem = len - 1 - i;
          if (rem < fOut) env = Math.min(env, rem / fOut);   // fade-out
          const wi = w + Math.round(i / r);
          if (wi >= 0 && wi < n) dst[wi] += s * env;
        }
        w += Math.round(len / r) + Math.floor(it.gap * sr);
      }
      this._voiceDur = Math.max(0.4, w / sr - HEAD);
      const src = this.ctx.createBufferSource();
      src.buffer = out;
      const g = this.ctx.createGain();
      g.gain.value = 1.12;                    // megáfono: por encima de la sala
      src.connect(g);
      g.connect(this.master);
      src.start(this.ctx.currentTime + 0.02);
      return true;
    } catch { return false; }
  }

  /** MEGAFONÍA del marcador: chime de torneo + voz ("5-3, saque para ti").
   *  v2.20: voz por WebAudio (clips del banco), audible en VR; si falta un
   *  fragmento o el banco no está listo, respaldo speechSynthesis (2D).
   *  v2.22: el conmutador del megáfono (audio.voice) lo silencia TODO
   *  (chime incluido), independiente del ambiente de torneo.
   *  v2.23: DUCKING — el ambiente (murmullo/aplausos) baja a un 24% durante
   *  la locución: las cifras se oyen con claridad total, sin ruido de fondo.
   *  Throttle de 6 s salvo force. */
  announce(text, force) {
    try {
      const now = performance.now();
      if (!force && now - this._lastAnnounce < 6000) return;
      this._lastAnnounce = now;
      // v2.29: el megáfono SOLO depende de su propio interruptor — antes,
      // apagar el AMBIENTE silenciaba también la voz del marcador.
      if (!this.voice) return;
      const duckOn = () => {
        const b = this.ambBus;
        if (!b || !this.ctx) return;
        const t = this.ctx.currentTime;
        const gg = b.gain;
        gg.cancelScheduledValues(t);
        gg.setValueAtTime(Math.min(1, gg.value || 1), t);
        gg.linearRampToValueAtTime(0.24, t + 0.22);
      };
      const duckOff = (delay) => {
        const b = this.ambBus;
        if (!b || !this.ctx) return;
        b.gain.setTargetAtTime(1, this.ctx.currentTime + delay, 0.45);
      };
      this.playOsc(660, 660, 0.12, 'sine', 0.2, 0);
      window.setTimeout(() => this.playOsc(990, 990, 0.16, 'sine', 0.2, 0), 140);
      const plan = this.voicePlan(text);
      if (plan && this.speakPlan(plan)) {
        duckOn();
        duckOff(0.4 + (this._voiceDur || 2.5));
        return;
      }
      duckOn();
      duckOff(3.4);                       // respaldo: duración estimada
      const ss = window.speechSynthesis;
      if (!ss || typeof SpeechSynthesisUtterance === 'undefined') return;
      ss.cancel();
      const u = new SpeechSynthesisUtterance(String(text));
      // v2.27: idioma del respaldo según el selector
      const loc = (typeof TLang === 'function' && TLang() === 'en') ? 'en-US' : 'es-ES';
      u.lang = loc;
      u.rate = 0.98;
      u.pitch = 0.78;
      u.volume = 0.95;
      try {
        const v = ss.getVoices().find((x) => x.lang && x.lang.toLowerCase().startsWith(loc.slice(0, 2)));
        if (v) u.voice = v;
      } catch { /* voz por defecto */ }
      ss.speak(u);
    } catch { /* */ }
  }
}

/* =====================================================================
 *  FÍSICA · integración semi-implícita con sub-pasos fijos (1/240 s),
 *  efecto (spin) con fuerza de Magnus, colisión barrida pala-bola (dos
 *  caras) y rebotes en TODA la mesa: cara superior, cantos, parte
 *  inferior y red.
 * ===================================================================== */
