export const ACHIEVEMENTS = CONFIG_LOGROS.core.map((a) => ({   // r61 · FASE 155: deriva de CONFIG_LOGROS.core (c02)
  key: a.key, emoji: a.emoji, nameKey: a.nameKey, descKey: a.descKey,
}));
// La tabla manda: orden/emoji/i18n/condiciones viven en CONFIG_LOGROS.core —
// copia plana por entrada para que los getters name/desc de abajo vengan en
// las copias, como siempre.
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { CONFIG_DIFICULTAD, CONFIG_LOGROS, CONFIG_TORNEOS, DIMS } from './c02_cfg_escena.js';
import { tmpD, tmpT, tmpTarget } from './c04_fisica_ccd.js';
import { computeShotVelocityReal, predictStrike } from './c05_colisiones_ia_golpeo.js';
import * as THREE from 'three';
/* DEPS-FASE2-FIN */
// accesibilidad de compatibilidad: name/desc dinámicos (por si algún código
// antiguo los lee) — se actualizan al idioma activo en cada arranque.
for (const a of ACHIEVEMENTS) {
  Object.defineProperty(a, 'name', { get() { return T(this.nameKey); } });
  Object.defineProperty(a, 'desc', { get() { return T(this.descKey); } });
}

// r61 · FASE 155 · condición de un logro del catálogo — el DATO manda
// (CONFIG_LOGROS.core en c02); el umbral ya no vive en la lógica.
const COND_LOGRO = (key) => {
  const e = CONFIG_LOGROS.core.find((a) => a.key === key);
  return (e && e.cond) || {};
};

export class GameStats {
  constructor() {
    this.KEY = 'ppxr_stats_v1';
    this.data = {
      won: 0, lost: 0, streak: 0, bestStreak: 0,
      pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
      monedas: 0,   // r85 · ECONOMÍA CRAZY: el monedero vive con las stats
      winsByDiff: { easy: 0, medium: 0, hard: 0 },
      ach: {},
      // M4 (r118) · ELO unificado (roadmap MEJORAS.md M4): el número de
      // habilidad ÚNICO para IA local, escalera y P2P. eloHist guarda los
      // últimos 40 cambios {t, d:±delta, m:modo}; mejorDia = el día con más
      // victorias; hoyDia = contador vivo del día en curso.
      elo: CONFIG_DIFICULTAD.elo.inicial,   // r60: dato (fábrica del número)
      eloHist: [],
      mejorDia: { dia: '', v: 0 },
      hoyDia: { dia: '', v: 0 },
    };
    try {
      const raw = localStorage.getItem(this.KEY);
      if (raw) {
        const saved = JSON.parse(raw);
        Object.assign(this.data, saved);
        this.data.winsByDiff = Object.assign({ easy: 0, medium: 0, hard: 0 }, saved.winsByDiff || {});
        this.data.ach = saved.ach || {};
      }
    } catch { /* datos corruptos: se recrean limpios */ }
    // M4 · migración tolerante (datos viejos sin ELO o corruptos)
    if (typeof this.data.elo !== 'number' || !(this.data.elo > 0)) this.data.elo = CONFIG_DIFICULTAD.elo.inicial;   // r60: dato
    if (!Array.isArray(this.data.eloHist)) this.data.eloHist = [];
    if (!this.data.mejorDia || typeof this.data.mejorDia !== 'object') this.data.mejorDia = { dia: '', v: 0 };
    if (!this.data.hoyDia || typeof this.data.hoyDia !== 'object') this.data.hoyDia = { dia: '', v: 0 };
    // r85 · migración tolerante del MONEDERO (datos viejos sin monedas)
    if (typeof this.data.monedas !== 'number') this.data.monedas = 0;
  }

  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.data)); } catch { /* */ }
  }

  unlock(key) {
    if (this.data.ach[key]) return false;
    this.data.ach[key] = Date.now();
    this.save();
    // r46 · el evento de DESBLOQUEO lo firma c12·celebrate (única vía por la
    // que pasan TODOS los logros: recordPoint/survival/match → celebrate) —
    // aquí NO se duplica: un logro = un evento 'logro'.
    return true;
  }

  /** Punto de PARTIDO (a 11). Devuelve las claves de logros nuevos. */
  recordPoint(winner, rallyHits) {
    const out = [];
    if (winner === 'player') {
      this.data.pointsWon++;
      // SAQUE DIRECTO (ace): solo tocó la bola el sacador
      if (rallyHits === 1) {
        this.data.aces++;
        if (this.data.aces >= COND_LOGRO('aces10').valor && this.unlock('aces10')) out.push('aces10');   // r61: dato
      }
    } else {
      this.data.pointsLost++;
    }
    out.push(...this.recordRally(rallyHits));
    this.save();
    return out;
  }

  /** Rallye terminado en cualquier modo. Devuelve logros nuevos. */
  recordRally(rallyHits) {
    const out = [];
    const n = rallyHits || 0;
    if (n > this.data.bestRally) this.data.bestRally = n;
    if (n >= COND_LOGRO('maraton').valor && this.unlock('maraton')) out.push('maraton');   // r61: dato
    return out;
  }

  /** Rallye de SUPERVIVENCIA: récord histórico + logro dedicado. */
  recordSurvivalRally(golpes, bestEver) {
    const out = this.recordRally(golpes);
    if (bestEver >= COND_LOGRO('superviv').valor && this.unlock('superviv')) out.push('superviv');   // r61: dato
    this.save();
    return out;
  }

  /** Fin de PARTIDO. Devuelve logros nuevos.
   *  M4 (r118) · ELO: info opcional { modo, oppElo } — modo 'ia'|'carrera'|
   *  'p2p' elige el factor K (24 · 20 · 32: los duelos humanos valen más);
   *  oppElo es el valor de referencia del rival (ELO_CPU / rivalPorElo /
   *  simétrico en P2P). Sin info, K=24 y rival 1000 — compatibilidad
   *  byte-idéntica con las llamadas antiguas de dos argumentos. */
  recordMatch(win, difficulty, info) {
    const out = [];
    const inf = info || {};
    const M = CONFIG_DIFICULTAD.elo;   // r60: el K por modo y los límites del número viven en datos
    const KMOD = M.kModo;
    const modo = KMOD[inf.modo] ? inf.modo : 'ia';
    const miElo = this.data.elo;
    const oppElo = (typeof inf.oppElo === 'number' && inf.oppElo > 0) ? inf.oppElo : M.rivalPorDefecto;
    const esperado = 1 / (1 + Math.pow(10, (oppElo - miElo) / M.paso));
    const delta = Math.round(KMOD[modo] * ((win ? 1 : 0) - esperado));
    this.data.elo = Math.max(M.piso, miElo + delta);   // r60: piso de la tabla
    this.data.eloHist.push({ t: Date.now(), d: delta, m: modo });
    if (this.data.eloHist.length > M.historialMax) {
      this.data.eloHist.splice(0, this.data.eloHist.length - M.historialMax);
    }
    if (win) {
      this.data.won++;
      this.data.streak++;
      if (this.data.streak > this.data.bestStreak) this.data.bestStreak = this.data.streak;
      this.data.winsByDiff[difficulty] = (this.data.winsByDiff[difficulty] || 0) + 1;
      // M4 · mejor día: victorias de HOY contra el récord histórico del día
      const d = new Date(); const p2 = (n) => (n < 10 ? '0' : '') + n;
      const hoy = d.getFullYear() + '-' + p2(d.getMonth() + 1) + '-' + p2(d.getDate());
      const hv = (this.data.hoyDia.dia === hoy) ? this.data.hoyDia.v + 1 : 1;
      this.data.hoyDia = { dia: hoy, v: hv };
      if (hv >= (this.data.mejorDia.v || 0)) this.data.mejorDia = { dia: hoy, v: hv };
      if (this.unlock('primera')) out.push('primera');
      if (this.data.streak >= COND_LOGRO('racha3').valor && this.unlock('racha3')) out.push('racha3');   // r61: dato
      if (difficulty === COND_LOGRO('gigante').dificultad && this.unlock('gigante')) out.push('gigante');   // r61: dato
    } else {
      this.data.lost++;
      this.data.streak = 0;
    }
    // r85 · ECONOMÍA CRAZY: el monedero se gana JUGANDO — +25 por victoria,
    // +8 por derrota (participar también paga). Alimenta la TIENDA de
    // bolas y mesas (c12 · _comprar) sin tocar ELO, logros ni física.
    this.data.monedas = (this.data.monedas | 0) + (win ? 25 : 8);
    this.save();
    return out;
  }
}


// M4 (r118) · gancho de tests (patrón __PP_WORLD: visible para la QA
// qa_r118_dirigida — el dev de Next no sirve los módulos crudos)
try { if (typeof window !== 'undefined') window.__PP_GameStats = GameStats; } catch { }


/* =====================================================================
 *  ÁRBITRO · reglas del tenis de mesa (ITTF simplificadas)
 *  - Partido a 11, ventaja de 2, saque alternado cada 2 puntos.
 *  - SAQUE: bote obligatorio en el campo propio y luego en el rival.
 *    Tocar la red y pasar = LET (se repite). Falta de saque = punto
 *    del receptor. El lanzamiento fallido no puntúa (se repite).
 *  - IGUALA: volea antes del bote, doble golpe o no pasar la red = falta.
 * ===================================================================== */
export class Rules {
  constructor() {
    this.state = 'serve';
    this.server = 'player';
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.message = T('serve_wait');
    this.totalPoints = 0;
    this.stateTimer = 0;
    this.lastHitter = null;
    this.isServeBall = false;
    this.serveOwnPending = false;   // falta el bote del sacador en su campo
    this.mustBounceOpp = false;     // debe botar en el campo del receptor
    this.validBounce = false;       // ya botó en el campo del receptor
    this.netTouched = false;
    this.rallyHits = 0;
    this.mode = 'match';            // 'match' (a 11) | 'survival' (rallyes infinitos)
    this.rallyesSurvived = 0;       // solo supervivencia: rallyes terminados
    this.oppLabel = 'cpu';          // v2.27: CLAVE ('cpu'|'rival') -> T('opp_…')
    // v3.6.29 · MEJOR DE 3 (ronda 37, petición del dueño): el PARTIDO libre
    // (vs CPU y online P2P) se disputa al mejor de 3 JUEGOS seguidos — quien
    // gana 2 juegos es campeón del enfrentamiento. bestOf=1 conserva el
    // partido a juego único de los campeonatos (sus duelos NO se tocan).
    this.bestOf = CONFIG_TORNEOS.partido.bestOfFabrica;   // r61: dato (c12 sube el PARTIDO libre a bestOfLibre)
    this.gamesPlayer = 0;           // juegos ganados por el jugador
    this.gamesAi = 0;               // juegos ganados por el rival
    this.gameNo = 1;                // juego en curso dentro del enfrentamiento
    this.firstServer = 'player';    // primer sacador del ENFRENTAMIENTO
    // v3.6.71 · r79 · IDENTIDAD DE RALLYE para el multijugador binario:
    // rallySeq se incrementa en CADA beginServeRally (los dos extremos lo
    // hacen en el mismo instante lógico: el sacador al golpear y el
    // receptor al recibir su BALL_HIT kind 1) — determinista y correlativo.
    // _appliedRally guarda el último rally resuelto para no duplicar puntos
    // (CLAIM recibido + detección local del mismo rally).
    this.rallySeq = 0;
    this._appliedRally = -1;
    // v3.6.71 · r79: la guardia anti-duplicado SOLO vive con red v2 activa
    // (NetLink.startV2 la enciende). En local y en los bancos QA el
    // comportamiento es EXACTAMENTE el de siempre (regresión cero).
    this._netGuard = false;
    // v3.6.39 · HOOK de arranque: el núcleo (c12) registra aquí la recogida
    // de los superpoderes de pala — CADA startMatch avisa y NINGUNA partida
    // nueva hereda cargas/FX de la anterior (reporte del dueño: «los poderes
    // de una partida previa que no se han gastado permanecen»). El árbitro
    // no conoce la pala: solo avisa, el núcleo hace la recogida.
    this.onMatchStart = null;
  }

  /** Nombre del oponente para los mensajes (CPU o humano remoto).
   *  M5b (r115) · oppName: nombre PROPIO del rival de la escalera de
   *  carrera (ROKO, MARTA…); lo pone el núcleo al desafiar y lo retira
   *  al terminar. Sin él, el rótulo clásico opp_label de siempre. */
  opp() {
    if (this.oppName) return this.oppName;
    return T('opp_' + (this.oppLabel || 'cpu'));
  }

  other(s) { return s === 'player' ? 'ai' : 'player'; }

  /** v3.6.29: reset de UN juego (marcador y botes a cero SIN tocar la serie).
   *  startMatch = resetGame + serie a cero + bestOf intacto. */
  resetGame() {
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.totalPoints = 0;
    this.rallySeq = 0;          // v3.6.71 · r79
    this._appliedRally = -1;    // v3.6.71 · r79
    this.server = this.gameNo % 2 === 1
      ? this.firstServer
      : this.other(this.firstServer);   // cada juego saca el otro (ITTF)
    this.gameOpener = this.server;  // v3.6.74 · r82: referencia de la rotación
                                    // dentro del juego (firstServer es del PARTIDO)
    this.state = 'serve';
    this.stateTimer = 0;
    this.lastHitter = null;
    this.isServeBall = false;
    this.serveOwnPending = false;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  startMatch(mode) {
    // r84 · DUELOS LOCOS: nuevo id de modo — misma puntuación y fin de
    // juego que 'match' (el árbitro no cambia NADA), sólo activa los
    // poderes del núcleo (c12 §DUELOS). Normalizador explícito.
    this.mode = mode === 'survival' ? 'survival'
      : (mode === 'duelos' ? 'duelos' : 'match');
    this.rallyesSurvived = 0;
    // v3.6.29: NUEVO ENFRENTAMIENTO — la serie arranca a cero (bestOf se
    // conserva: lo fija el juego en los caminos del partido libre).
    this.gamesPlayer = 0;
    this.gamesAi = 0;
    this.gameNo = 1;
    this.firstServer = 'player';
    // r95 · ESTADÍSTICAS DEL PARTIDO (petición del dueño: «estadísticas al
    // final de cada duelo»: velocidad máx. de bola, rally más largo y %
    // precisión). Se RESETTAN en cada partida nueva y las alimenta el
    // núcleo en vivo (vmax en animate, rally en el punto); la fanfarria
    // las muestra al terminar. El % precisión sale del marcador final.
    this.mStats = { vmax: 0, bestRally: 0 };
    // r97 · MAPA DE CALOR (petición del dueño: «zonas donde pierdes puntos»):
    // por PARTIDO, los botes del lado del jugador en los que se pierde el
    // punto — rejilla 3×3 (corta/media/fondo × izq/centro/der). La fanfarria
    // pinta el mapa del partido; el entrenamiento acumula el histórico
    // (pp_heat_v1 vía c12). Reset por partido como mStats.
    this.mHeat = [0, 0, 0, 0, 0, 0, 0, 0, 0];
    this.resetGame();
    this.message = this.mode === 'survival'
      ? T('surv_start')
      : T('serve_wait');
    // v3.6.39 · PARTIDA NUEVA = PALA LIMPIA: UN SOLO punto de aviso cubre
    // TODOS los caminos (menú, revancha por gatillo, revancha de menú,
    // cambio de modo, online, vuelta de calibración, hall y el reinicio
    // automático del estado 'over' — imposible olvidar uno). Idempotente:
    // el hall ya recogía antes de llamar startMatch y repetir no rompe.
    try { if (this.onMatchStart) this.onMatchStart(); } catch (e) { /* nunca rompe el árbitro */ }
  }

  /** Comienza el rally tras un golpe de saque válido (al caer, tras la línea).
   *  v3.6.71 · r79: cada rallye recibe identidad única (rallySeq) — viaja
   *  en los POINT_CLAIM/ACK del multijugador binario. */
  beginServeRally(server) {
    this.state = 'rally';
    this.rallySeq++;
    this.lastHitter = server;
    this.isServeBall = true;
    this.serveOwnPending = true;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  registerPaddleHit(who, remote) {
    if (this.state !== 'rally') return [];
    // Nadie puede golpear dos veces seguidas (doble golpe = falta)
    if (who === this.lastHitter) {
      return this.applyPoint(this.other(who), 'dblhit');
    }
    // Volea: golpear antes de que la bote en su campo el receptor.
    // r81 · la VOLEA la juzga el ÁRBITRO DE ESA MITAD (spec §7): un golpe
    // REMOTO llega ya validado por el árbitro del que golpea (si hubiera
    // volea, SU mitad la cantó y llega por CLAIM) — el fantasma propio va
    // SIEMPRE un poco por detrás del vuelo real (avance ≤120 ms + lag de
    // red) y un juicio de volea local daba FALTAS FALSAS que partían el
    // marcador (el duelo simulado r81 lo cazó en vivo).
    if (!remote && (this.serveOwnPending || (this.mustBounceOpp && !this.validBounce))) {
      return this.applyPoint(this.lastHitter, 'volley');
    }
    this.lastHitter = who;
    this.mustBounceOpp = true;
    this.validBounce = false;
    this.isServeBall = false;
    this.rallyHits++;
    return [];
  }

  applyPoint(winner, cause) {
    // v3.6.71 · r79: guardia anti-duplicado — un rallye SOLO puede
    // resolverse una vez (la detección local y el CLAIM remoto del mismo
    // rallyId no pueden sumar dos). SOLO con red v2 activa: en local el
    // árbitro es único y la guardia no existe (comportamiento intacto).
    if (this._netGuard && this._appliedRally === this.rallySeq) return [];
    this._appliedRally = this.rallySeq;
    return this._applyPointSinGuard(winner, cause);
  }

  /** cuerpo real de applyPoint SIN la guardia de rally (la pone el
   *  llamador: applyPoint con rallySeq vivo, forcePoint con rallyId
   *  del CLAIM — nunca las dos, lección de la capa BN en página). */
  _applyPointSinGuard(winner, cause) {
    if (this.mode === 'survival') {
      // SUPERVIVENCIA: no hay puntos; lo que cuenta es el rallye terminado.
      // La CPU acelera con cada rallye (lo gestiona el juego con el intent).
      this.totalPoints++;
      this.rallyesSurvived++;
      this.state = 'point';
      this.stateTimer = CONFIG_TORNEOS.partido.pausaSupervivenciaS;   // r61: dato
      const golpes = this.rallyHits;
      const causeTxt = T('cause_' + cause, { opp: this.opp() });
      this.message = golpes >= 8
        ? T('rally_big', { n: golpes, cause: causeTxt })
        : T('rally_n', { n: golpes, s: T(golpes === 1 ? 'word_hit' : 'word_hits'), cause: causeTxt });
      return [{ type: 'point', winner, cause, survival: true, rallyHits: golpes }];
    }
    if (winner === 'player') this.scorePlayer++;
    else this.scoreAi++;
    this.totalPoints++;
    this.state = 'point';
    this.stateTimer = CONFIG_TORNEOS.partido.pausaPuntoS;   // r61: dato
    const rallyTxt = this.rallyHits >= 6 ? T('rally_suffix', { n: this.rallyHits }) : '';
    const causeTxt = T('cause_' + cause, { opp: this.opp() });
    this.message = winner === 'player'
      ? T('point_you', { cause: causeTxt, rally: rallyTxt })
      : T('point_opp', { opp: this.opp(), cause: causeTxt, rally: rallyTxt });
    return [{ type: 'point', winner, cause, rallyHits: this.rallyHits }];
  }

  retryServe(cause) {
    this.state = 'serve';
    this.message = T('retry_serve', { cause: T('cause_' + cause) });
    return [{ type: 'retry-serve', cause }];
  }

  /** v3.6.71 · r79 · PUNTO IMPUESTO POR LA RED: aplica el resultado de un
   *  POINT_CLAIM del extremo con autoridad, con guardia por rallyId. Espeja
   *  EXACTAMENTE applyPoint (mismo intent, mismos mensajes) para que el
   *  receptor viva el punto idéntico al local. */
  forcePoint(winner, cause, rallyId) {
    if (rallyId !== undefined && rallyId !== null) {
      if (this._appliedRally === rallyId) return [];
      this._appliedRally = rallyId;
    }
    return this._applyPointSinGuard(winner, cause);
  }

  computeNextServer() {
    // v3.6.74 · r82 · LA ROTACIÓN ES RELATIVA AL PRIMER SACADOR DEL JUEGO
    // (gameOpener), no a 'player': en el INVITADO el abridor es 'ai' en SU
    // perspectiva (el anfitrión abre) y la fórmula antigua (hardcode
    // 'player') daba el sacador AL REVÉS desde el primer punto — el
    // anfitrión creía sacar él y el invitado TAMBIÉN: dos bolas HELD,
    // ningún saque llega, el partido se atasca tras el punto 1 en
    // dispositivos reales (cazado EN VIVO por la batería multi). El espejo
    // de perspectiva sale gratis derivándolo del abridor del juego.
    const n = this.totalPoints;
    const base = this.gameOpener || this.firstServer;
    const otro = base === 'player' ? 'ai' : 'player';
    const F = CONFIG_TORNEOS.partido;   // r61: el formato del partido es dato
    if (this.scorePlayer >= F.igualaEn && this.scoreAi >= F.igualaEn) {
      return Math.floor(n / F.saqueIguala) % 2 === 0 ? base : otro;   // deuce: alterna cada saqueIguala
    }
    return Math.floor(n / F.saqueCada) % 2 === 0 ? base : otro;
  }

  handleEvents(events) {
    const intents = [];
    for (const e of events) {
      if (e.consumed) continue;
      if (this.state !== 'rally') break;

      switch (e.type) {
        case 'paddle': {
          if (e.who) intents.push(...this.registerPaddleHit(e.who));
          break;
        }
        case 'net': {
          this.netTouched = true;
          break;
        }
        case 'table': {
          if (!e.side || !this.lastHitter) break;
          const own = this.lastHitter;
          const opp = this.other(own);

          if (this.serveOwnPending) {
            if (e.side === own) {
              // 1er bote del saque en el campo del sacador: correcto
              this.serveOwnPending = false;
              this.mustBounceOpp = true;
              this.netTouched = false;
            } else {
              intents.push(...this.applyPoint(opp, 'serve_no_own'));
            }
          } else if (this.mustBounceOpp) {
            if (e.side === opp) {
              this.validBounce = true;
              if (this.isServeBall && this.netTouched) {
                // LET: rozó la red en saque pero pasó y botó bien
                intents.push(...this.retryServe('let'));
              } else {
                this.mustBounceOpp = false;
                this.netTouched = false;
              }
            } else {
              const cause = this.isServeBall
                ? 'serve_net'
                : own === 'player' ? 'own_you' : 'own_opp';
              intents.push(...this.applyPoint(opp, cause));
            }
          } else if (this.validBounce) {
            if (e.side === opp) {
              const cause = own === 'player' ? 'dbl_opp' : 'dbl_you';
              intents.push(...this.applyPoint(own, cause));
            } else {
              const cause = own === 'player' ? 'back_you' : 'back_opp';
              intents.push(...this.applyPoint(opp, cause));
            }
          }
          break;
        }
        case 'floor':
        case 'wall': {
          if (!this.lastHitter) break;
          if (this.serveOwnPending || this.mustBounceOpp) {
            const cause = this.isServeBall
              ? (this.netTouched ? 'serve_net_touch' : 'serve_out')
              : (this.netTouched ? 'net_stay' : (e.type === 'wall' ? 'wall' : 'out'));
            intents.push(...this.applyPoint(this.other(this.lastHitter), cause));
          } else {
            const cause = this.lastHitter === 'player' ? 'noret_opp' : 'noret_you';
            intents.push(...this.applyPoint(this.lastHitter, cause));
          }
          break;
        }
      }
    }
    return intents;
  }

  update(dt) {
    const intents = [];

    if (this.state === 'point') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        if (this.mode === 'survival') {
          // SUPERVIVENCIA: nunca se acaba el partido; bola nueva y a seguir
          this.state = 'serve';
          this.server = this.computeNextServer();
          this.message = this.server === 'player'
            ? T('surv_new')
            : T('surv_opp', { opp: this.opp() });
          intents.push({ type: 'serve', server: this.server });
          return intents;
        }
        const F2 = CONFIG_TORNEOS.partido;   // r61: dato (a 11 con ventaja de 2)
        const finished =
          (this.scorePlayer >= F2.puntosGanar || this.scoreAi >= F2.puntosGanar) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= F2.ventajaMinima;
        if (finished) {
          const winner = this.scorePlayer > this.scoreAi ? 'player' : 'ai';
          const p = this.scorePlayer, q = this.scoreAi;
          // v3.6.29 · MEJOR DE 3: el juego contado alimenta la serie; el
          // enfrentamiento se decide al ganar 2 juegos (v×serieFactor > bestOf).
          // r84 · DUELOS LOCOS entra en la serie (idéntico al 'match': los
          // CLAIM/ACK y el espejo de marcador son agnósticos del modo).
          if ((this.mode === 'match' || this.mode === 'duelos') && this.bestOf > 1) {
            if (winner === 'player') this.gamesPlayer++; else this.gamesAi++;
            const a = this.gamesPlayer, b = this.gamesAi;
            const SF = CONFIG_TORNEOS.partido.serieFactor;   // r61: dato
            const serieAcabada = a * SF > this.bestOf || b * SF > this.bestOf;
            if (!serieAcabada) {
              // Juego terminado, el enfrentamiento SIGUE: juego nuevo con la
              // serie ya escrita y el saque cambiado (el otro abre).
              this.gameNo++;
              this.resetGame();
              this.message = winner === 'player'
                ? T('game_won_you', { p, q, a, b })
                : T('game_won_opp', { opp: this.opp(), p, q, a, b });
              intents.push({
                type: 'serve', server: this.server,
                gameEnd: { winner, p, q, gp: a, ga: b, bo: this.bestOf },
              });
              return intents;
            }
            // SERIE ACABADA: mensaje con el enfrentamiento completo.
            this.state = 'over';
            this.stateTimer = 8;
            this.message = winner === 'player'
              ? T('over_win_bo', { p, q, a, b })
              : T('over_lose_bo', { opp: this.opp(), p, q, a, b });
            intents.push({ type: 'game-over', winner });
            return intents;
          }
          // v2.26: mensajes alineados con los carteles oficiales (v2.27: i18n)
          this.state = 'over';
          this.stateTimer = 8;
          this.message = winner === 'player'
            ? T('over_win', { p, q })
            : T('over_lose', { p, q });
          intents.push({ type: 'game-over', winner });
        } else {
          this.state = 'serve';
          this.server = this.computeNextServer();
          this.message = this.server === 'player'
            ? T('serve_go')
            : T('serve_opp', { opp: this.opp() });
          intents.push({ type: 'serve', server: this.server });
        }
      }
    } else if (this.state === 'over') {
      this.stateTimer -= dt;
      if (this.stateTimer <= 0) {
        this.startMatch(this.mode);   // reinicio automático en el MISMO modo
        intents.push({ type: 'serve', server: this.server });
      }
    }

    return intents;
  }
}

/* =====================================================================
 *  IA · predice dónde botará la bola en SU campo, camina hasta el punto
 *  de golpeo, espera el bote (nada de voleas) y devuelve buscando el
 *  hueco lejos del rival. Puede fallar de forma natural (no llega).
 * ===================================================================== */
function gauss() {
  return (Math.random() * 2 - 1) * 0.7 + (Math.random() * 2 - 1) * 0.3;
}

/* =====================================================================
 *  r91 · CADENA CINEMÁTICA DEL RIVAL (informe del dueño: el movimiento de
 *  la pala «no es creíble… muy robótico, se posiciona de manera previsible
 *  y da un empujoncito»). Investigación aplicada (Bańkosz & Winiarski 2025
 *  J Sports Sci Med 24:311 · Bańkosz 2018 PMC5950751 · Malagoli Lanzoni
 *  2021 Appl Sci 11:5178 · Wong 2020 Appl Sci 10:5203 · Flash & Hogan
 *  1985 J Neurosci 5:1688):
 *   · La pala es el EXTREMO de un plan de golpe con fases humanas:
 *     reacción (190-300 ms) → carga (backswing, altura mínima de pala AQUÍ
 *     — medido en 550 Hz) → golpeo (pico de velocidad sincronizado a la
 *     LLEGADA de la bola) → acompañamiento (la pala sigue subiendo tras el
 *     contacto) → recuperación. Nada de teletransportes ni empujones.
 *   · Trayectorias de MÍNIMO JERK (quíntico de Hermite con velocidades en
 *     los extremos) y correcciones por EMPALME con continuidad de
 *     velocidad — el modelo neurocientífico real del brazo humano.
 *   · Variabilidad funcional por golpe (±12 % en amplitudes, codo con polo
 *     anatómico que cae en drive y sube en revés): el rival nunca repite
 *     pose idéntica, como los jugadores reales del estudio de 2025.
 *   · La FÍSICA del golpe (solver, árbitro, efectos) NO cambia: la cadena
 *     hace VISIBLE y SINCRONIZADO el golpe que ya existía.
 * ===================================================================== */

/* amplitudes por golpe (m) — dbs/hbs: carga detrás/abajo del contacto ·
 * dft/hft: acompañamiento delante/arriba · vPeakMul: velocidad visual de
 * pala × velocidad de salida de la bola */
export const CADENA_GOLPE = {
  drive:   { dbs: 0.24, hbs: 0.10, dft: 0.30, hft: 0.16, vPeakMul: 0.80 },
  smash:   { dbs: 0.28, hbs: 0.14, dft: 0.36, hft: 0.10, vPeakMul: 0.95 },
  push:    { dbs: 0.14, hbs: 0.03, dft: 0.18, hft: 0.04, vPeakMul: 0.60 },
  dejada:  { dbs: 0.16, hbs: 0.05, dft: 0.20, hft: 0.06, vPeakMul: 0.55 },
  bloqueo: { dbs: 0.09, hbs: 0.02, dft: 0.10, hft: 0.03, vPeakMul: 0.45 },
  mala:    { dbs: 0.07, hbs: 0.02, dft: 0.10, hft: 0.02, vPeakMul: 0.35 },
};

/* r91 · quíntico de Hermite con velocidades en los extremos (v0=v1=0 ⇒
 * MÍNIMO JERK exacto — Flash & Hogan 1985). Generador de TODAS las
 * trayectorias del brazo: acelera suave, pico en el punto planificado,
 * frena suave. */
export function mjQuintic(u, p0, v0, p1, v1, T, out) {
  u = THREE.MathUtils.clamp(u, 0, 1);
  const u2 = u * u, u3 = u2 * u, u4 = u3 * u, u5 = u4 * u;
  const h0 = 10 * u3 - 15 * u4 + 6 * u5;
  const h10 = u - 6 * u3 + 8 * u4 - 3 * u5;
  const h11 = -4 * u3 + 7 * u4 - 3 * u5;
  out.set(
    p0.x + (p1.x - p0.x) * h0 + T * (v0.x * h10 + v1.x * h11),
    p0.y + (p1.y - p0.y) * h0 + T * (v0.y * h10 + v1.y * h11),
    p0.z + (p1.z - p0.z) * h0 + T * (v0.z * h10 + v1.z * h11));
  return out;
}

/* derivada del quíntico (velocidad exacta de la trayectoria) */
export function mjQuinticVel(u, p0, v0, p1, v1, T, out) {
  u = THREE.MathUtils.clamp(u, 0, 1);
  const u2 = u * u, u3 = u2 * u, u4 = u3 * u;
  const d0 = (30 * u2 - 60 * u3 + 30 * u4) / T;
  const d10 = 1 - 18 * u2 + 32 * u3 - 15 * u4;
  const d11 = -12 * u2 + 28 * u3 - 15 * u4;
  out.set(
    (p1.x - p0.x) * d0 + v0.x * d10 + v1.x * d11,
    (p1.y - p0.y) * d0 + v0.y * d10 + v1.y * d11,
    (p1.z - p0.z) * d0 + v0.z * d10 + v1.z * d11);
  return out;
}

/* r91 · IK ANALÍTICA de 2 huesos (ley de cosenos) con polo anatómico del
 * codo: el codo CAE en el drive y sube en el revés, como un brazo real
 * (rango humano 25-145°). Objetivo imposible ⇒ brazo estirado al 94 % del
 * alcance — nunca NaN, nunca desarticulado. Devuelve { dist, flex }. */
export function solveArmIK(S, W, L1, L2, pole, outE) {
  const dx = W.x - S.x, dy = W.y - S.y, dz = W.z - S.z;
  const raw = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
  const dist = THREE.MathUtils.clamp(raw, 0.30, 0.94 * (L1 + L2));
  const nx = dx / raw, ny = dy / raw, nz = dz / raw;
  const a1 = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist);
  const h = Math.sqrt(Math.max(L1 * L1 - a1 * a1, 1e-6));
  const dp = pole.x * nx + pole.y * ny + pole.z * nz;
  let px = pole.x - nx * dp, py = pole.y - ny * dp, pz = pole.z - nz * dp;
  const pl = Math.sqrt(px * px + py * py + pz * pz) || 1e-6;
  px /= pl; py /= pl; pz /= pl;
  outE.set(S.x + nx * a1 + px * h, S.y + ny * a1 + py * h, S.z + nz * a1 + pz * h);
  const cosE = THREE.MathUtils.clamp((L1 * L1 + L2 * L2 - dist * dist) / (2 * L1 * L2), -1, 1);
  return { dist, flex: 180 - Math.acos(cosE) * 180 / Math.PI };
}

/* r93 · IK de 2 huesos RÍGIDA para el esqueleto GLB (informe del dueño:
 * «los huesos no son elásticos… NUNCA se pueden estirar o escalar los
 * huesos»): las LONGITUDES son invariables — el objetivo se clampar al
 * anillo de alcance ANTES de resolver y la MUÑECA RESUELTA sale por outW
 * (puede quedar corta respecto al deseo: el cuerpo cubre la diferencia,
 * el hueso jamás estira). Devuelve { dist, flex, alcanzado }. */
export function solveArmIKRigido(S, W, L1, L2, pole, outE, outW) {
  const dx = W.x - S.x, dy = W.y - S.y, dz = W.z - S.z;
  const raw = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1e-6;
  const maxR = 0.999 * (L1 + L2), minR = 0.28 * (L1 + L2);
  const dist = THREE.MathUtils.clamp(raw, minR, maxR);
  const nx = dx / raw, ny = dy / raw, nz = dz / raw;
  const a1 = (L1 * L1 - L2 * L2 + dist * dist) / (2 * dist);
  const h = Math.sqrt(Math.max(L1 * L1 - a1 * a1, 1e-6));
  const dp = pole.x * nx + pole.y * ny + pole.z * nz;
  let px = pole.x - nx * dp, py = pole.y - ny * dp, pz = pole.z - nz * dp;
  const pl = Math.sqrt(px * px + py * py + pz * pz) || 1e-6;
  px /= pl; py /= pl; pz /= pl;
  outE.set(S.x + nx * a1 + px * h, S.y + ny * a1 + py * h, S.z + nz * a1 + pz * h);
  outW.set(S.x + nx * dist, S.y + ny * dist, S.z + nz * dist);
  const cosE = THREE.MathUtils.clamp((L1 * L1 + L2 * L2 - dist * dist) / (2 * L1 * L2), -1, 1);
  return { dist, flex: 180 - Math.acos(cosE) * 180 / Math.PI,
    alcanzado: raw <= maxR && raw >= minR };
}

/* r93 · ZONA DULCE: nudge del AGARRE (≤ 4 cm) para que el CENTRO de la
 * hoja cubra la bola en el impacto — informe del dueño: «en vez de hacerlo
 * sobre la zona dulce de la pala parece que la golpea desde un canto».
 * Puro cálculo (testeable en Node): si la bola cae fuera del disco
 * central (62 % del radio), el agarre se corre hacia ella lo justo. */
export function zonaDulceNudge(grip, ballPos, bladeCenter, bladeR, out) {
  const dx = ballPos.x - bladeCenter.x;
  const dy = ballPos.y - bladeCenter.y;
  const dz = ballPos.z - bladeCenter.z;
  const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
  const exceso = d - bladeR * 0.62;
  if (exceso <= 0) return out.copy(grip);
  const k = Math.min(exceso, 0.04) / (d || 1e-6);
  return out.set(grip.x + dx * k, grip.y + dy * k, grip.z + dz * k);
}

/* r93 · ONE EURO (Casiez et al. 2012) para VECTORES — anti-temblor del
 * informe del dueño («articulaciones con mucho ruido… movimientos
 * temblorosos y caóticos»): forma canónica — derivada con corte
 * adaptativo (fc_d = fcMin + β·|ẋ|) y estado integrado. Casi parado
 * filtra fuerte, movimiento rápido apenas retrasa. Cero allocs. */
export class OneEuroV3 {
  constructor(fcMin = 1.2, beta = 0.045) {
    this.fcMin = fcMin; this.beta = beta;
    this.init = false;
    this.prev = new THREE.Vector3();     // x̂ (estado)
    this.dPrev = new THREE.Vector3();    // ẋ filtrada (por segundo)
    this.tmp = new THREE.Vector3();
  }
  reset() { this.init = false; this.dPrev.set(0, 0, 0); }
  _alfa(dt, fc) {
    const tau = 1 / (2 * Math.PI * Math.max(fc, 0.01));
    return 1 / (1 + tau / Math.max(dt, 1e-4));
  }
  filtrar(v, dt) {
    if (!this.init) { this.init = true; this.prev.copy(v); this.dPrev.set(0, 0, 0); return this.tmp.copy(v); }
    this.tmp.copy(v).sub(this.prev).divideScalar(Math.max(dt, 1e-4));   // ẋ bruta
    const ad = this._alfa(dt, this.fcMin + this.beta * this.tmp.length());
    this.dPrev.lerp(this.tmp, ad);                       // ẋ filtrada
    this.prev.addScaledVector(this.dPrev, dt);           // integra
    return this.tmp.copy(this.prev);
  }
}

/* r93 · ONE EURO para CUATERNIONES (articulaciones): la «velocidad» es el
 * ángulo de la diferencia q_prev⁻¹·q_deseado por dt; el mezclado slerp
 * usa la misma familia de corte adaptativo. FC_MIN por contexto: nítido en
 * golpeo/acompañamiento (dt·20 en r92), suave en el resto. */
export class OneEuroQ {
  constructor(fcMin = 2.2, beta = 0.09) {
    this.fcMin = fcMin; this.beta = beta;
    this.init = false;
    this.prev = new THREE.Quaternion();
  }
  reset() { this.init = false; }
  filtrar(q, dt) {
    if (!this.init) { this.init = true; this.prev.copy(q); return this.prev; }
    const qd = _oeqA.copy(q);
    const dif = Math.abs(2 * Math.acos(THREE.MathUtils.clamp(
      Math.abs(this.prev.dot(qd)), 0, 1))) / Math.max(dt, 1e-4);   // rad/s
    const fc = this.fcMin + this.beta * dif;
    const tau = 1 / (2 * Math.PI * fc);
    const a = 1 / (1 + tau / Math.max(dt, 1e-4));
    this.prev.slerp(qd, THREE.MathUtils.clamp(a, 0.05, 1));
    return this.prev;
  }
}
const _oeqA = new THREE.Quaternion();

/* r91 · adivinanza temprana del golpe (para la CARGA visual, antes de que
 * la bola llegue): el golpe REAL lo decide el cerebro en el contacto de
 * siempre — esto solo elige la firma del backswing. */
export function adivinaKind(ball, pt) {
  if (pt.y > 1.15) return 'smash';                  // bola alta: remate probable
  if (ball.vel.length() > 6.5) return 'bloqueo';    // bola rápida: bloqueo
  if (pt.y < 0.75) return 'push';                   // bola baja: push
  return 'drive';
}

/* rascadores de la cadena (cero allocs por frame) */
const _cadA = new THREE.Vector3();
const _cadB = new THREE.Vector3();
const _cadC = new THREE.Vector3();
const _cadD = new THREE.Vector3();
const _cadV = new THREE.Vector3();
const _cadT = new THREE.Vector3();   // r92 · cuerda/tangente del ARCO del golpe
const _cadP = new THREE.Vector3();   // r99bis · paso por frame del tope de gesto

export class OpponentAI {
  constructor(cfg, sign, home) {
    this.cfg = cfg;
    this.sign = sign;
    this.home = home.clone();
    this.pos = home.clone();
    this.vel = new THREE.Vector3();
    this.predict = new THREE.Vector3();
    this.predictValid = false;
    this.predictTimer = 0;
    this.hitCooldown = 0;
    this.errX = 0;
    this.errY = 0;
    this._ppPortalVisto = false;   // v3.6.42: flanco de la marca del portal
    this.swing = null;   // animación de follow-through del último golpe (v2.17)
    this.prep = new THREE.Vector3();   // retroceso de preparación (visual)
    // v2.23: lado del golpe en curso — +1 derecha (forehand), -1 revés.
    // Se sortea al APARECER la bola (con la posición del cuerpo aún lejos del
    // punto de contacto) y se mantiene durante todo el rallye de esa bola.
    this.fhSide = 1;
    // r95 · RIVALES CON ESTILO VISIBLE (petición del dueño): la personalidad
    // del manifest (agresivo/defensivo) SE NOTA en la COLOCACIÓN y en las
    // CELEBRACIONES. El juego inyecta { zIdle, bias, celeb } aquí; cero =
    // comportamiento clásico byte-idéntico (toggle AJUSTES › JUEGO).
    this.style = null;
    this.celebT = 0;   // celebración en curso (segundos que quedan)
    // r91 · CADENA CINEMÁTICA: plan de golpe vivo (fases reacción→carga→
    // golpeo→acompañamiento→recuperación) + tiempo de vuelo predicho
    this.chain = null;
    this.predictT = 0;
    // r99 · DISPARO DIFERIDO: el golpe de la IA ya NO sale el frame en que
    // se decide — se guarda aquí y se aplica cuando la cadena de la pala
    // LLEGA al punto de barrido (el dueño VE cómo la pala golpea la bola:
    // adiós al «empujón invisible» que despegaba la bola antes del toque).
    this._disparo = null;
    this._retPend = null;
  }

  setConfig(cfg) { this.cfg = cfg; }

  /* ============ r91 · MÉTODOS DE LA CADENA CINEMÁTICA ============ */

  /** roll de muñeca por efecto, ligado al kind (la firma r88: topspin
   *  cierra, cortada abre); cadenaContacto lo refresca con el REAL. */
  _rollCadena(kind) {
    const r = kind === 'smash' ? 0.30 : kind === 'push' ? -0.22 :
      kind === 'dejada' ? -0.16 : kind === 'bloqueo' ? 0.10 :
      kind === 'mala' ? (Math.random() - 0.5) * 0.4 : 0.20;
    return r + (Math.random() - 0.5) * 0.08;
  }

  /** r91 · PLAN del golpe (nace con la primera predicción válida): fases
   *  reacción→carga→golpeo (pico EN tBall)→acompañamiento→recuperación,
   *  amplitudes de CADENA_GOLPE con variabilidad funcional ±12 %. */
  planCadena(contact, tBall, kind, fh) {
    const G = CADENA_GOLPE[kind] || CADENA_GOLPE.drive;
    const jit = () => 0.88 + Math.random() * 0.24;
    // estimación de salida (el impacto real la refina): hacia el campo del
    // jugador con sesgo lateral aleatorio
    const tz = DIMS.tableCenterZ - this.sign * DIMS.tableHalfLength * 0.7;
    _cadD.set((Math.random() - 0.5) * 0.6 - contact.x,
      DIMS.tableTopY + 0.30 - contact.y, tz - contact.z).normalize();
    const vPeak = 6.5 * G.vPeakMul * (0.9 + Math.random() * 0.2);
    const esc = (this.chain && this.chain.flat) ? 0.5 : 1;   // calabaza: carga corta
    let T_react = THREE.MathUtils.clamp(tBall * 0.30, 0.12, 0.30);
    let T_back = THREE.MathUtils.clamp((tBall - T_react) * 0.45, 0.10, 0.24);
    let T_strike = tBall - T_react - T_back;
    if (T_strike < 0.07) {          // bola rápida: comprime reacción y carga
      T_back = Math.max(0.06, T_back - (0.07 - T_strike));
      T_strike = Math.max(0.07, tBall - T_react - T_back);
      if (T_react + T_back + T_strike > tBall)
        T_react = Math.max(0.04, tBall - T_back - T_strike);
    }
    const cur = this.chain ? this.chain.cur.clone() : this.pos.clone();
    const vel = this.chain ? this.chain.vel.clone() : new THREE.Vector3();
    // r92 · ARCO REAL del golpe (informe del dueño: «la pala se posiciona y
    // empuja de forma lineal» + video Gatien): la CARGA se abre al LADO del
    // golpe y el ACOMPAÑAMIENTO CRUZA al lado contrario — B→C→F dejan de
    // ser colineales y dibujan el arco que culmina en el impacto y lo
    // prolonga con la continuidad del arco previo.
    const B = _cadA.copy(contact).addScaledVector(_cadD, -G.dbs * jit() * esc);
    B.x += fh * this.sign * G.dbs * 0.85 * jit() * esc;
    B.y = Math.max(0.5, contact.y - G.hbs * jit() * esc);
    const F = _cadB.copy(contact).addScaledVector(_cadD, G.dft * jit());
    F.x -= fh * this.sign * G.dft * 0.62 * jit();
    F.y = Math.max(0.5, contact.y + G.hft * jit());
    // tangente del arco EN el contacto (suma de las cuerdas B→C y C→F, el
    // criterio de paso-suave de splines): la velocidad pico atraviesa C
    // DENTRO del arco — no a lo largo de la cuerda de salida.
    const uC = _cadT.copy(contact).sub(B).normalize();   // cuerda carga→C
    const uF = _cadC.copy(F).sub(contact).normalize();   // cuerda C→cruce
    const tC = uC.clone().add(uF);
    if (tC.lengthSq() < 1e-6) tC.copy(_cadD);            // degenerado: cuerda
    tC.normalize().multiplyScalar(vPeak);
    this.chain = {
      phase: 'react', t: 0, tSeg: 0, u: 0, kind, fh, flat: !!(this.chain && this.chain.flat),
      contact: contact.clone(), tBall,
      dir: _cadD.clone(), vdir: _cadD.clone(), roll: this._rollCadena(kind),
      cur, vel, segIdx: 0,
      segs: [
        { phase: 'react', T: T_react, p0: cur.clone(), v0: vel.clone(),
          p1: cur.clone().lerp(B, 0.25), v1: new THREE.Vector3() },
        { phase: 'back', T: T_back, p0: cur.clone(), v0: new THREE.Vector3(),
          p1: B.clone(), v1: uC.clone().multiplyScalar(0.32 * vPeak) },
        { phase: 'strike', T: T_strike, p0: B.clone(), v0: new THREE.Vector3(),
          p1: contact.clone(), v1: tC },
        { phase: 'follow', T: 0.16 + Math.random() * 0.06,
          p0: contact.clone(), v0: tC,
          p1: F.clone(), v1: uF.clone().multiplyScalar(vPeak * 0.25) },
        { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
          v0: _cadD.clone().multiplyScalar(vPeak * 0.25), p1: this.pos.clone(),
          v1: new THREE.Vector3() },
      ],
    };
    // continuidad exacta: cada segmento parte del extremo del anterior
    // (p0/v0 de react ya son CLONES de cur/vel en el literal — nunca alias
    // del estado vivo: el quíntico ESCRIBE en cur y no debe corromper su
    // propio origen; con alias el plan moría en ~0,4 s por el guard NaN)
    const sgs = this.chain.segs;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
  }

  /** r91 · RE-ANCLAJE con la predicción refinada: el plan restante se
   *  reconstruye desde el estado ACTUAL (cur/vel) — empalme con continuidad
   *  de velocidad, el submovimiento del modelo humano. */
  _reanclaCadena(newContact, newT) {
    const ch = this.chain;
    if (!ch) return;
    const G = CADENA_GOLPE[ch.kind] || CADENA_GOLPE.drive;
    const tRem = Math.max(0.10, newT);
    const T_back = THREE.MathUtils.clamp(tRem * 0.45, 0.05, 0.16);
    const T_strike = Math.max(0.05, tRem - T_back);
    const vPeak = 6.5 * G.vPeakMul;
    const B = _cadA.copy(newContact).addScaledVector(_cadD.copy(ch.dir), -G.dbs * 0.8);
    B.x += ch.fh * this.sign * G.dbs * 0.68;   // r92 · arco: carga al lado
    B.y = Math.max(0.5, newContact.y - G.hbs * 0.8);
    const F = _cadB.copy(newContact).addScaledVector(_cadD, G.dft);
    F.x -= ch.fh * this.sign * G.dft * 0.5;    // r92 · arco: cruce al otro
    F.y = Math.max(0.5, newContact.y + G.hft);
    // r92 · tangente del arco en el re-anclaje (mismo criterio que el plan)
    const uC = _cadT.copy(newContact).sub(B).normalize();
    const uF = _cadC.copy(F).sub(newContact).normalize();
    const tC = uC.clone().add(uF);
    if (tC.lengthSq() < 1e-6) tC.copy(_cadD);
    tC.normalize().multiplyScalar(vPeak);
    ch.contact.copy(newContact);
    ch.tBall = newT;
    ch.segs = [
      { phase: 'back', T: T_back, p0: ch.cur.clone(), v0: ch.vel.clone(),
        p1: B.clone(), v1: uC.clone().multiplyScalar(0.32 * vPeak) },
      { phase: 'strike', T: T_strike, p0: B.clone(), v0: new THREE.Vector3(),
        p1: newContact.clone(), v1: tC },
      { phase: 'follow', T: 0.15 + Math.random() * 0.06, p0: newContact.clone(),
        v0: tC, p1: F.clone(),
        v1: uF.clone().multiplyScalar(vPeak * 0.25) },
      { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
        v0: _cadD.clone().multiplyScalar(vPeak * 0.25), p1: this.pos.clone(),
        v1: new THREE.Vector3() },
    ];
    const sgs = ch.segs;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
    ch.t = 0; ch.tSeg = 0; ch.segIdx = 0; ch.phase = 'back';
  }

  /** r91 · IMPACTO REAL: en el frame del golpe (barrido de siempre) el plan
   *  se afina al punto EXACTO del contacto con el pico de velocidad alineado
   *  a la salida real de la bola — el golpe visible ES el golpe físico. */
  cadenaContacto(cx, cy, cz, v, TBola) {
    const ch = this.chain;
    if (!ch) return;   // r99: sin cadena el aplicador del disparo cubre
    if (ch.phase === 'follow' || ch.phase === 'recover') {
      // r99 · con disparo diferido SIEMPRE se re-ancla el plan: el golpe se
      // decidió contra el punto de barrido FRESCO y la cadena debe llegar
      // a él exactamente cuando la bola (sin TBola, guard clásico r91).
      if (!TBola) return;
    }
    const G = CADENA_GOLPE[ch.kind] || CADENA_GOLPE.drive;
    const vP = _cadV.copy(v).multiplyScalar(G.vPeakMul);
    if (vP.lengthSq() < 0.25) vP.setLength(3.0);
    _cadD.copy(vP).normalize();
    const pC = _cadA.set(cx, cy, cz);
    const d = ch.cur.distanceTo(pC);
    // r99bis · ACOMPAÑAMIENTO NATURAL (el dueño: «movimientos progresivos,
    // nada bruscos, ni empujones»): el strike JAMÁS dura menos de 80 ms y
    // su T crece con la DISTANCIA (d/3.5): el pico del quíntico (~1.875×d/T)
    // queda ≤ 7 m/s para cualquier distancia — un gesto humano que acelera,
    // atraviesa el contacto y acompaña, sin látigos. Si la bola llega antes,
    // la pala la ENCUENTRA en vuelo (_enContacto), no con un salto.
    const T = TBola !== undefined
      ? THREE.MathUtils.clamp(Math.max(TBola, d / 6), 0.08, 0.30)
      : THREE.MathUtils.clamp(d / Math.max(3, vP.length()), 0.03, 0.09);
    const F = _cadB.copy(pC).addScaledVector(_cadD, G.dft);
    F.x -= ch.fh * this.sign * G.dft * 0.5;    // r92 · arco: cruce del gesto
    F.y = Math.max(0.5, pC.y + G.hft);
    // r92 · tangente del arco EN el impacto (bisectriz de las cuerdas):
    // el pico atraviesa C DENTRO del gesto curvo que ya traía el brazo —
    // la bola sale por su plan (aiHit), la pala golpea en arco (fin del
    // «empujón» lineal: el empuje ahora continúa el arco previo).
    const uC = _cadC.copy(pC).sub(ch.cur).normalize();
    const uF = _cadT.copy(F).sub(pC).normalize();
    const tC = uC.clone().add(uF);
    if (tC.lengthSq() < 1e-6) tC.copy(_cadD);
    tC.normalize().multiplyScalar(vP.length());
    ch.contact.copy(pC);
    ch.dir.copy(_cadD);
    ch.vdir.copy(v).normalize();
    ch.roll = this._rollCadena(ch.kind);
    ch.segs = [
      { phase: 'strike', T, p0: ch.cur.clone(), v0: ch.vel.clone(),
        p1: pC.clone(), v1: tC },
      { phase: 'follow', T: 0.15 + Math.random() * 0.06, p0: pC.clone(),
        v0: tC, p1: F.clone(),
        v1: uF.clone().multiplyScalar(vP.length() * 0.25) },
      { phase: 'recover', T: 0.30 + Math.random() * 0.10, p0: F.clone(),
        v0: vP.clone().multiplyScalar(0.25), p1: this.pos.clone(),
        v1: new THREE.Vector3() },
    ];
    const sgs = ch.segs;
    for (let i = 1; i < sgs.length; i++) { sgs[i].p0 = sgs[i - 1].p1; sgs[i].v0 = sgs[i - 1].v1; }
    ch.t = 0; ch.tSeg = 0; ch.segIdx = 0; ch.phase = 'strike';
  }

  /** r91 · frame de la cadena: fase activa, cur/vel por quíntico, re-anclaje
   *  con la predicción refinada, recuperación viva sobre el cuerpo y guard
   *  anti-NaN (una cifra rara no tumba la partida). */
  updateCadena(dt) {
    // r99 · VIGÍA DEL DISPARO DIFERIDO: sin cadena viva (NaN, agotamiento)
    // o con espera excesiva, la salida se aplica igualmente — jamás se
    // pierde un rallye por el mecanismo de sincronización.
    if (this._disparo) {
      this._disparo.t += dt;
      if (!this.chain || this._disparo.t > this._disparo.tMax) this._aplicaDisparo();
    }
    const ch0 = this.chain;
    if (!ch0) return;
    if ((ch0.phase === 'react' || ch0.phase === 'back') && this.predictValid &&
        ch0.contact.distanceTo(this.predict) > 0.055) {
      this._reanclaCadena(this.predict, Math.max(this.predictT, 0.12));
      return;
    }
    let ch = ch0;
    ch.t += dt;
    ch.tSeg = (ch.tSeg || 0) + dt;          // tiempo LOCAL del segmento activo:
    let seg = ch.segs[ch.segIdx];           // el global ch.t nunca se compara
    while (seg && ch.tSeg > seg.T) {        // contra el T de un segmento (r91:
      ch.tSeg -= seg.T;                     // agotaba el plan en cascada al
      ch.segIdx++;                          // entrar en strike)
      seg = ch.segs[ch.segIdx];
      if (seg) {
        // r99 · la pala ACABA DE LLEGAR al punto de barrido (fin del strike):
        // contacto (la bola sale) o re-anclaje progresivo para encontrarla.
        if (ch.phase === 'strike' && seg.phase !== 'strike') {
          this._enContacto();               // r99bis: puede RE-ANCLAR los segs
          break;                            // el plan nuevo integra el próximo dt
        }
        ch.phase = seg.phase;
      }
    }
    if (!this.chain) return;                // el re-anclaje o el vigía la cerraron
    seg = this.chain.segs[this.chain.segIdx] || this.chain.segs[0];
    ch = this.chain;                        // misma instancia, segs renovados
    if (!seg) { this.chain = null; return; }
    ch.u = THREE.MathUtils.clamp(ch.tSeg / seg.T, 0, 1);
    mjQuintic(ch.u, seg.p0, seg.v0, seg.p1, seg.v1, seg.T, ch.cur);
    mjQuinticVel(ch.u, seg.p0, seg.v0, seg.p1, seg.v1, seg.T, ch.vel);
    // r99bis · TOPE DE PASO (garantía dura: «nada brusco, sin empujones»):
    // el quíntico puede pedir picos antinaturales para cumplir sus empalmes
    // de velocidad; la pala NUNCA supera 7,8 m/s (13 cm a 60 fps) — el gesto
    // se ve siempre progresivo y el re-anclaje absorbe el ajuste de llegada.
    if (!ch._curPrev) ch._curPrev = ch.cur.clone();
    _cadP.copy(ch.cur).sub(ch._curPrev);
    if (_cadP.length() > 0.13) {
      _cadP.setLength(0.13);
      ch.cur.copy(ch._curPrev).add(_cadP);
      ch.vel.copy(_cadP).multiplyScalar(60);   // la velocidad REAL acotada
    }
    ch._curPrev.copy(ch.cur);
    if (ch.phase === 'recover') ch.cur.lerp(this.pos, Math.min(1, dt * 2.5));
    if (!Number.isFinite(ch.cur.x + ch.cur.y + ch.cur.z)) this.chain = null;
  }

  /** r99bis · ÁRBITRO DEL CONTACTO (fin del strike): si la bola está en el
   *  punto de barrido (±5 cm) el golpe es REAL y sale aquí. Si quedó lejos
   *  (llegó antes que la pala), NADA de saltos: la cadena se re-ancla con
   *  un quíntico que vuela a ENCONTRAR la bola en su propio vuelo (predic-
   *  ción lineal al tiempo de encuentro) y continúa con el arco de acompa-
   *  ñamiento — el dueño ve un gesto que persigue y acompaña, no un empujón. */
  _enContacto() {
    const d = this._disparo;
    if (!d) return;
    const b = d.ball;
    if (b.pos.distanceTo(d.pos) < 0.05) { this._aplicaDisparo(); return; }
    const ch = this.chain;
    if (!ch) { this._aplicaDisparo(); return; }
    // T2 de PERSECUCIÓN (d/7): la pala corre cerca de su tope (7 m/s ≈ 11,7
    // cm/frame, dentro del tope de gesto de 13 cm) — así GANA a la recesión
    // de la bola y el encuentro converge en 1-2 re-anclajes, sin látigo.
    const T2 = THREE.MathUtils.clamp(
      Math.max(ch.cur.distanceTo(b.pos) / 6, 0.08), 0.08, 0.20);
    const obj = b.pos.clone().addScaledVector(b.vel, T2 * 0.9);
    this.cadenaContacto(obj.x, obj.y, obj.z, d.v, T2);
    if (!this.chain) { this._aplicaDisparo(); return; }   // guard NaN
    d.pos.copy(obj);                       // el nuevo punto de encuentro
    d.t = Math.max(d.t, d.tMax - 0.15);    // el tope global sigue mandando
  }

  reset() {
    this.pos.copy(this.home);
    this.vel.set(0, 0, 0);
    this.predictValid = false;
    this.hitCooldown = 0;
    this._ppPortalVisto = false;   // v3.6.42: el flanco del portal a limpio
    this.chain = null;          // r91: sin plan de golpe colgado
    this._disparo = null;       // r99: sin salida pendiente entre puntos
    this._retPend = null;
    this.predictT = 0;
  }

  update(dt, ball, ctx) {
    this.hitCooldown -= dt;
    if (this.celebT > 0) this.celebT -= dt;   // r95: celebración con estilo
    if (this.swing) {
      this.swing.t += dt;
      if (this.swing.t > this.swing.dur) this.swing = null;
    }
    // r91 · el plan de golpe avanza (fases, re-anclaje con la predicción)
    this.updateCadena(dt);
    // r99 · la cadena acaba de LLEGAR al contacto → la salida de la bola
    // viaja AQUÍ (el frame en que el dueño ve el golpe: ni antes, ni después)
    if (this._retPend) {
      const r = this._retPend;
      this._retPend = null;
      return r;
    }
    const C = DIMS.tableCenterZ;
    const sign = this.sign;
    const toward = ball.vel.z * sign > 0;

    // v3.6.42 · CORRECCIÓN CRÍTICA (el dueño: «he sacado y no las
    // devuelve… una cosa es que se le penalice en un % y otra que se anule
    // su respuesta»): en r49 la predicción moría CADA FRAME mientras la
    // marca ppPortal estuviera viva — y la marca solo se limpia al
    // devolver la propia IA, así que la IA pasaba casi TODOS los frames
    // sin predicción válida (deriva perezosa) y no volvía a golpear NUNCA.
    // AHORA la muerte de la predicción es PUNTUAL (flanco de subida de la
    // marca): la bola que desaparece por el portal borra la predicción UNA
    // sola vez y la IA reacciona tras SU predictInterval natural. La
    // penalización queda en los % de siempre (error ×1,6 · piernas ×0,75 ·
    // +10 % de fallo decidido) y SOLO con la ventana del poder viva.
    if (ball.ppPortal && !this._ppPortalVisto) {
      this._ppPortalVisto = true;
      this.predictValid = false;
      this.predictTimer = Math.max(this.predictTimer, this.cfg.predictInterval);
    }
    if (!ball.ppPortal && this._ppPortalVisto) this._ppPortalVisto = false;

    if (ctx.canHit && toward) {
      this.predictTimer -= dt;
      if (this.predictTimer <= 0) {
        this.predictTimer = this.cfg.predictInterval;
        const strike = predictStrike(ball, sign, ctx.validBounce);
        if (window.__aiDbg) {
          if (strike) window.__aiDbg.ok++;
          else window.__aiDbg.null++;
        }
        if (strike) {
          if (!this.predictValid) {
            // bola NUEVA viniendo: el error de puntería se sortea UNA sola vez
            // y se mantiene durante todo el rallye (antes se re-sorteba cada
            // re-predicción y la pala temblaba persiguiendo objetivos distintos)
            // v3.6.37 · SÚPER EFECTO NOTORIO (petición del dueño): la bola
            // MARCADA «dificulta en un %» el éxito del rival — el error se
            // sortea con la marca YA puesta (el golpe con el poder activo
            // precede al vuelo) y se amplifica ×efectoRivalErrMul.
            // v3.6.41 · SÚPER PORTAL: la bola que reaparece tras el portal
            // amplifica TAMBIÉN el error (×portalRivalErrMul) — el sorteo
            // de una bola recién aparecida es ciego por naturaleza.
            const eMulIA = (ball.ppEfecto ? (DIMS.efectoRivalErrMul || 1) : 1) *
              (ball.ppPortal ? (DIMS.portalRivalErrMul || 1) : 1);
            this.errX = gauss() * this.cfg.errStd * eMulIA;
            this.errY = gauss() * this.cfg.errStd * 0.6 * eMulIA;
            this.predict.copy(strike.point);
            // v2.23: ¿golpe de DERECHA o de REVÉS? Según el lado en que queda
            // la bola respecto al cuerpo al empezar a reaccionar (con sign:
            // positivo = lado de la mano derecha). Con bola centrada, se
            // prefiere la derecha como un jugador diestro.
            const dxf = (strike.point.x - this.pos.x) * sign;
            this.fhSide = Math.abs(dxf) > 0.05 ? (dxf > 0 ? 1 : -1) : (Math.random() < 0.55 ? 1 : -1);
            // r91 · tiempo de vuelo a la bola (ancla del pico del golpeo)
            this.predictT = strike.t;
          } else {
            // refinamiento de la MISMA bola: suavizar, sin saltos
            this.predict.lerp(strike.point, 0.45);
            this.predictT += (strike.t - this.predictT) * 0.45;   // r91
          }
          this.predictValid = true;
          // r91 · CADENA: el plan de golpe nace con la PRIMERA predicción
          // válida de la bola (reacción humana ANTES de que llegue) y se
          // re-ancla en cada refinamiento; el impacto real lo afina.
          if (!this.chain && this.predictT < 1.15) {
            this.planCadena(this.predict, this.predictT,
              adivinaKind(ball, strike.point), this.fhSide);
          }
        } else {
          this.predictValid = false;
        }
      }
    } else {
      this.predictValid = false;
    }

    // preparación visual del golpe: la pala se retrae un poco al acercarse la
    // bola a su punto de contacto (solo estético: ai.pos sigue siendo el
    // punto lógico de detección). v2.23: además se CARGA hacia el lado del
    // golpe (unidad de giro real: la pala va por delante del cuerpo hacia el
    // lado de la bola) para que el swing parta de una preparación creíble.
    if (this.predictValid && ctx.canHit) {
      tmpT.copy(this.predict).sub(this.pos);
      const dl = tmpT.length();
      const w = THREE.MathUtils.clamp(1 - dl / 0.9, 0, 1) * 0.55;
      tmpT.normalize().multiplyScalar(-0.075 * w);
      this.prep.copy(tmpT);
      this.prep.y = 0.045 * w;
      this.prep.x += sign * this.fhSide * 0.075 * w;   // carga al lado del golpe
    } else {
      this.prep.multiplyScalar(Math.max(0, 1 - dt * 5));
    }

    if (ctx.holdTarget) {
      // saque propio: caminar a la posición reglamentaria y esperar allí
      tmpT.copy(ctx.holdTarget);
    } else if (this.predictValid) {
      const baseline = C + sign * DIMS.tableHalfLength;
      let inDist = (this.predict.z - baseline) * -sign;
      // r95 · ESTILO VISIBLE: el agresivo se ADELANTA al golpe (juega más
      // cerca de la mesa), el defensivo espera más atrás. bias en metros,
      // simétrico para los dos lados (inDist es normalizada por sign).
      inDist -= (this.style ? (this.style.bias || 0) : 0);
      inDist = THREE.MathUtils.clamp(inDist, -0.45, DIMS.tableHalfLength + 0.15);
      const zClamp = baseline + inDist * -sign;
      let yClamp = THREE.MathUtils.clamp(this.predict.y + this.errY, 0.55, 1.55);
      const overTable =
        Math.abs(this.predict.x) < DIMS.tableHalfWidth + 0.1 &&
        Math.abs(zClamp - C) < DIMS.tableHalfLength;
      if (overTable) yClamp = Math.max(yClamp, DIMS.tableTopY + 0.08);
      tmpT.set(
        THREE.MathUtils.clamp(this.predict.x + this.errX, -(DIMS.tableHalfWidth + 0.35), DIMS.tableHalfWidth + 0.35),
        yClamp,
        zClamp,
      );
    } else {
      // r95 · ESTILO VISIBLE · COLOCACIÓN: el agresivo espera MÁS CERCA de
      // la mesa (zIdle positivo hacia la red), el defensivo más atrás.
      tmpT.set(
        this.home.x + ball.pos.x * 0.3,
        this.home.y,
        this.home.z + (toward ? -sign * 0.2 : 0) +
          (this.style ? (this.style.zIdle || 0) * -sign : 0),
      );
    }

    tmpD.copy(tmpT).sub(this.pos);
    const dist = tmpD.length();
    // v3.6.37 · SÚPER EFECTO NOTORIO: con la bola marcada viniendo, el rival
    // va un % más lento (le CUESTA llegar — visible y honesto: la física de
    // salida no cambia, solo las piernas de la IA mientras sufre el efecto).
    // v3.6.41 · SÚPER PORTAL: la bola recién aparecida también frena las
    // piernas (×portalRivalVel) — dos poderes a la vez se multiplican.
    let vMulIA = 1;
    if (toward) {
      if (ball.ppEfecto) vMulIA *= (DIMS.efectoRivalVel || 1);
      if (ball.ppPortal) vMulIA *= (DIMS.portalRivalVel || 1);
    }
    const desiredSpeed = Math.min(this.cfg.maxSpeed * vMulIA, dist * 4.5);
    if (dist > 1e-5) tmpD.setLength(desiredSpeed); else tmpD.set(0, 0, 0);
    this.vel.lerp(tmpD, Math.min(1, dt * this.cfg.accel));
    this.pos.addScaledVector(this.vel, dt);
    // r88 · el steering vuelve a ser DIRECTO (revert del arco/goal de r87):
    // el informe del dueño tras la V3.6.178 — «movimientos curvos muy raros
    // y falla muchos golpes, totalmente ilógicos». El arco tangente y el
    // objetivo suavizado (90 ms) AÑADÍAN CAMINO y RETRASO a la llegada: la
    // pala llegaba tarde al punto de contacto y los barridos fallaban. Un
    // jugador real se COLOCA donde va a recibir (trayecto corto y decidido)
    // y la naturalidad vive en el GOLPE (carga previa + follow-through +
    // giro de hoja según el efecto — ver el swing de devolver()).
    // Lo que SÍ se conserva del P0-8: el SUELO SOBRE LA MESA.
    if (Math.abs(this.pos.x) < DIMS.tableHalfWidth + DIMS.ballRadius &&
        Math.abs(this.pos.z - DIMS.tableCenterZ) < DIMS.tableHalfLength + DIMS.ballRadius &&
        this.pos.y < DIMS.tableTopY + 0.03) {
      this.pos.y = DIMS.tableTopY + 0.03;
      if (this.vel.y < 0) this.vel.y = 0;
    }

    if (!ctx.canHit || !ctx.validBounce || !toward || this.hitCooldown > 0) return null;
    // v2.84 · ALCANCE BARRIDO (anti-túnel): la decisión llega un frame tarde
    // (la IA ve la bola ya integrada). Con smashes la bola salta >0,21 m
    // entre frames y se COLABA por la esfera de alcance: atravesaba la pala
    // sin ser vista. Ahora se mide la distancia al SEGMENTO recorrido por la
    // bola en el último paso de física (ctx.prevBall, capturado en el bucle)
    // y el contacto se produce en el punto exacto de ese trayecto. Tope de
    // longitud 0,5 m: un salto mayor es un TELEPORTE (reposición de saque,
    // resets) y no debe contar como contacto.
    // r92 · CALABAZA AL ALCANCE DE LA PALA (informe del dueño: «el rival no
    // la golpea correctamente con su pala, parece que tiene un desplaza-
    // miento y el efecto no queda bien»): la calabaza del Halloween mide
    // Ø 0,13 m (3× la bola) pero el contacto saltaba con el alcance gené-
    // rico de 21 cm — la pala se paraba JUNTO a la calabaza, nunca sobre
    // ella. Con la marca ppCalabaza (que ponia el módulo en la bola): el
    // alcance baja a 0,12 m para que el golpe nazca CERCA de la piel de
    // la calabaza y el ajuste del punto (abajo) sea de centímetros, no un
    // salto visible. Sin marca: el alcance probado de siempre.
    const reach = ball.ppCalabaza ? 0.12 : 0.21;
    const r2 = reach * reach;
    let cx = ball.pos.x, cy = ball.pos.y, cz = ball.pos.z;   // punto de contacto
    const prevB = ctx.prevBall || null;
    if (prevB) {
      _segAB.copy(ball.pos).sub(prevB);
      const l2 = _segAB.lengthSq();
      if (l2 > 1e-10 && l2 <= 0.25) {            // segmento válido (≤ 0,5 m)
        _segAP.copy(this.pos).sub(prevB);
        const tseg = THREE.MathUtils.clamp(_segAP.dot(_segAB) / l2, 0, 1);
        _segC.copy(prevB).addScaledVector(_segAB, tseg);
        cx = _segC.x; cy = _segC.y; cz = _segC.z;
        if (this.pos.distanceToSquared(_segC) > r2) return null;
      } else if (this.pos.distanceToSquared(ball.pos) > r2) return null;
    } else if (this.pos.distanceToSquared(ball.pos) > r2) return null;
    // r93 · CONTACTO TANGENTE INVERTIDO (informe del dueño tras la r92:
    // «existe un desfase de la bola cuando la golpea el rival… es una
    // deriva de precisión entre ambas palas»): la r92 arrastraba el PUNTO
    // DE CONTACTO hacia la pala y RECOLOCABA la bola en él — con la
    // calabaza (Ø 0,13 m, 3× la bola) ese salto de hasta 4,5 cm SE VE
    // (la calabaza salta hacia la pala en el frame del golpe) y encima el
    // follow-through arrancaba con la hoja 5 cm por encima del contacto.
    // El golpe del DUEÑO «está correcto» porque su física jamás recoloca
    // la bola — la deriva era SÓLO del lado de la IA. r93: la bola se
    // queda en el punto del barrido y es la HOJA la que viaja a la piel.
    // r97 · INFORME DEL DUEÑO («otra vez veo la calabaza desincronizada
    // con el bote de la pelota y el rival golpea en un sitio diferente a
    // donde está la calabaza»): el punto del barrido (cx,cy,cz) vive en el
    // SUBPASO de física — hasta UN FRAME POR DETRÁS de la posición
    // RENDERIZADA (ballMesh se sincroniza al final del update). Con la
    // bola normal (Ø 4 cm, veloz) ese retroceso es invisible; la calabaza
    // (Ø 13 cm) SALTABA hacia atrás en el frame del golpe y la hoja
    // golpeaba donde la calabaza YA NO ESTÁ. DOS garantías duras ahora:
    // (1) LA BOLA CALABAZA JAMÁS SE RECOLOCA al punto del barrido — igual
    //     que la física del dueño, que nunca recoloca la bola: la salida
    //     nace de ball.pos VIVO (frame renderizado) y el solver apunta al
    //     MISMO blanco — trayectoria honesta, cero saltos.
    // (2) LA HOJA VIAJA A LA CALABAZA RENDERIZADA: el tangente se calcula
    //     desde ball.pos (donde la calabaza está PINTADA este frame), no
    //     desde el punto del subpaso — centro de calabaza a 7,5 cm del
    //     centro de hoja (radio 0,065 + canto), flat sin ascenso (r93).
    let toca = null;                      // punto tangente para el swing (r93)
    if (ball.ppCalabaza) {
      const dcx = ball.pos.x - this.pos.x,
            dcy = ball.pos.y - this.pos.y,
            dcz = ball.pos.z - this.pos.z;
      const dC = Math.sqrt(dcx * dcx + dcy * dcy + dcz * dcz) || 1e-6;
      const TOCA = 0.075;
      const sT = Math.min(1, TOCA / dC);  // nunca pasarse de la bola viva
      toca = { x: this.pos.x + dcx * sT,
               y: this.pos.y + dcy * sT,
               z: this.pos.z + dcz * sT };
    }
    if ((cz - C) * sign < 0.04) return null;
    if (cy < DIMS.tableTopY - 0.08 || cy > 1.65) return null;

    const ballSpeed = ball.vel.length();
    // r113 · CPU INTELIGENTE (petición del dueño: «la CPU no falla bolas
    // fáciles; sólo escoradas, rápidas o de colocación extrema»). Antes el
    // fallo era un impuesto FIJO (missBase) que repartía muertes por igual:
    // la IA fallaba bolas cómodas a la pala. Ahora el fallo es ESFUERZO:
    //  · base tibia (la torpeza del nivel — easy sigue fallando algo más);
    //  · RAPIDA: +0,06 por m/s por encima de 7 (sube un pelín: 0,05);
    //  · ESCORADA/COLOCACIÓN EXTREMA: +0,60 por cada metro de VIAJE por
    //    encima de 0,85 — una bola al rincón que obliga a desplazarse 1,6 m
    //    se paga (+0,45); una bola cómoda junto a la pala NO se falla.
    //  · portal: igual de decisivo que siempre (DIMS.portalMissExtra).
    // Los estilos M5a (errStd/miss ×) siguen multiplicando la cfg — sus
    // clamps acotan y la distinción entre personalidades se conserva.
    // (NOTA: el `reach` de arriba es el RADIO de la pala — este es `viaje`.)
    const viaje = Math.hypot(cx - this.pos.x, cz - this.pos.z);
    const EF = CONFIG_DIFICULTAD.esfuerzo;   // r60: la fórmula del fallo vive en datos
    const pMiss = Math.min(EF.tope,
      this.cfg.missBase * EF.baseFrac +
      Math.max(0, ballSpeed - EF.velUmbral) * EF.velPaso +
      Math.max(0, viaje - EF.viajeUmbral) * EF.viajePaso +
      (ball.ppPortal ? (DIMS.portalMissExtra || 0) : 0));
    this.hitCooldown = EF.cooldownS;   // r60: cadencia de la tabla
    // v2.84 · GOLPE MALO (petición del artista): el fallo decidido de la IA
    // YA NO deja pasar la bola a través de la pala (efecto pésimo). La toca
    // MAL: contacto flojo y desviado que se queda en su campo (red o corto),
    // se marcha larga/fuera o cruza floja y alta — el punto se pierde igual
    // pero con contacto, sonido y pose creíbles en lugar del cruce fantasma.
    if (Math.random() < pMiss) {
      // r99 · GOLPE TORPE DIFERIDO: la bola NO se recoloca ni sale este
      // frame — vuela a su punto de barrido y la cadena llega al contacto
      // cuando ella llega (el toque flojo SE VE: la pala roza la bola).
      // r97: la calabaza NUNCA se recoloca (la bola viva manda — ver arriba)
      const _mv = this.mishit(ball, toca);
      this._preparaDisparo(ball, _mv, cx, cy, cz);
      this.cadenaContacto(cx, cy, cz, _mv, this._tBolaDe(ball, cx, cy, cz));
      return null;
    }
    // v2.84: golpe LIMPIO con contacto barrido — la salida parte del punto
    // real donde la pala alcanzó la bola (no del punto ya pasado).
    // r97: con la calabaza la bola VIVA manda (cero saltos visibles).
    // r99 · la bola ya NO se teletransporta al punto del barrido: el
    // disparo nace del intercepto PREDICHO (cx,cy,cz) cuando la pala y la
    // bola están juntas — el vuelo de la bola NUNCA se toca hasta el toque.
    _aiInt.set(cx, cy, cz);

    // ---------- SELECCIÓN DE GOLPE (v2.11 · IA lista) ----------
    // Cuatro golpes según la situación: remate a bolas altas, dejada corta
    // si el rival está lejos de la mesa, push con slice a bolas bajas y
    // drive con lift (topspin) como golpe por defecto. Más un bloqueo
    // rápido para devolver bolas fuertes sin regalar velocidad.
    const oppDeep = ctx.oppPadZ !== undefined
      ? ((ctx.oppPadZ - DIMS.tableCenterZ) * -sign > DIMS.tableHalfLength * 0.3)
      : (Math.random() < 0.35);
    const high = _aiInt.y > 1.15;
    const low = _aiInt.y < DIMS.tableTopY + 0.16;
    let kind = 'drive';
    const rShot = Math.random();
    if (high && rShot < this.cfg.smash) {
      kind = 'smash';
    } else if (oppDeep && !low && (ctx.rallyHits || 0) >= 2 && rShot < this.cfg.smash + 0.32) {
      kind = 'dejada';
    } else if (low && rShot < 0.5) {
      kind = 'push';
    } else if (ballSpeed > 6.5 && rShot < 0.3) {
      kind = 'bloqueo';
    }

    let depthRel, T, spinX, speedMul = 1;
    switch (kind) {
      case 'smash':
        // palo seco y profundo: el punto suele acabar aquí
        depthRel = 0.72 + Math.random() * 0.32;
        T = this.cfg.minT * 0.8;
        spinX = -sign * (16 + Math.random() * 8);          // lift fuerte
        break;
      case 'dejada':
        // bola corta y flotada con slice para que "frene" al botar
        depthRel = 0.16 + Math.random() * 0.1;
        T = Math.max(this.cfg.minT, 0.92 + Math.random() * 0.25);
        spinX = sign * (6 + Math.random() * 5);            // slice (backspin)
        speedMul = 0.55;
        break;
      case 'push':
        depthRel = 0.55 + Math.random() * 0.3;
        T = this.cfg.minT + 0.14 + Math.random() * 0.2;
        spinX = sign * (5 + Math.random() * 6);            // slice
        speedMul = 0.8;
        break;
      case 'bloqueo':
        depthRel = 0.66 + Math.random() * 0.3;
        T = this.cfg.minT * 0.92;
        spinX = -sign * (10 + Math.random() * 6);
        speedMul = 0.92;
        break;
      default: // drive con lift: juego en largo (62%-112% hacia la línea)
        depthRel = 0.62 + Math.random() * 0.5;
        T = this.cfg.minT + Math.random() * (this.cfg.maxT - this.cfg.minT);
        spinX = -sign * (9 + Math.random() * 9);
    }

    const away = ctx.oppPadX !== undefined
      ? -Math.sign(ctx.oppPadX || (Math.random() - 0.5))
      : (Math.random() < 0.5 ? -1 : 1);
    let tx = away * (0.16 + Math.random() * 0.38) + gauss() * this.cfg.errStd * 0.8;
    // sorpresa: 14% de golpes "al cuerpo" (hacia su lado actual)
    if (kind !== 'dejada' && Math.random() < 0.14) {
      tx = -away * (0.05 + Math.random() * 0.12);
    }
    tx = THREE.MathUtils.clamp(tx, -0.55, 0.55);
    if (kind === 'dejada') tx *= 0.6;   // las dejadas buscan precisión, no ángulo

    // profundidad SIEMPRE dentro de la mesa (antes algunos tiros apuntaban
    // hasta un 112% de la media mesa y solo entraban por accidente con el arrastre)
    const depth = Math.min(depthRel, 0.94) * DIMS.tableHalfLength;
    const tz = DIMS.tableCenterZ - sign * depth;
    const maxV = kind === 'smash'
      ? this.cfg.maxShotSpeed * 1.15
      : this.cfg.maxShotSpeed * speedMul;

    tmpTarget.set(tx, DIMS.tableTopY + DIMS.ballRadius, tz);
    // el giro se decide ANTES: el solver necesita el spin para el Magnus
    const spinY = (Math.random() - 0.5) * 6;
    const shotSpin = _aiSpin.set(spinX, spinY, 0);
    // FÍSICA REAL (v2.17): tiro corregido por simulación (arrastre + Magnus):
    // bota donde apunta en vez de 15-27 cm corto. r99: el origen del disparo
    // es el INTERCEPTO (donde pala y bola se encontrarán), no la bola viva.
    const v = computeShotVelocityReal(_aiInt, tmpTarget, T, maxV, shotSpin);

    // r91/r99 · CADENA: el plan se re-ancla al punto de barrido con el
    // strike durando EXACTAMENTE lo que la bola tarda en llegar a él —
    // y la salida se aplica cuando la pala LLEGA (contacto real, sonido
    // y árbitro en el instante visual del golpe).
    this._preparaDisparo(ball, v, cx, cy, cz, shotSpin, tmpTarget, T, maxV);
    this.cadenaContacto(cx, cy, cz, v, this._tBolaDe(ball, cx, cy, cz));

    // swing visual: follow-through del golpe en la dirección del tiro.
    // v2.23: lleva TAMBIÉN el tipo de golpe, el lado (derecha/revés) y la
    // velocidad de salida 3D — la pose de la pala los usa para girar la hoja,
    // abrir/cerrar la cara y cruzar el cuerpo como un jugador real.
    // r88 · el roll de muñeca ya NO es azar: se LIGA al EFECTO real del tiro
    // (informe del dueño: «giro de pala según el efecto que quiera darle a
    // la bola»). lift > 0 = liftado (topspin: la hoja BARRERÁ por ENCIMA,
    // pronación) · lift < 0 = cortada (backspin: por DEBAJO, supinación).
    // El azar queda como firma mínima: nunca dos golpes idénticos.
    // `back` = CARGA PREVIA del golpe (el acompañamiento que pide el dueño):
    // la hoja arranca DETRÁS del contacto y barre A TRAVÉS de él — el
    // follow-through existente completa el gesto (carga → contacto → salida).
    const lift = -spinX * sign;                     // >0 topspin · <0 backspin
    const carga = kind === 'smash' ? 0.14
      : kind === 'drive' ? 0.10
      : kind === 'bloqueo' ? 0.05
      : 0.08;                                       // push / dejada
    // r91 · con la cadena activa el STROKE COMPLETO ya se dibuja (carga→
    // golpeo→acompañamiento): el swing de emergencia solo nace si el plan
    // no llegó a tiempo (bola sin predicción válida).
    if (!this.chain || this.chain.phase === 'follow' ||
        this.chain.phase === 'recover') this.swing = {
      t: 0,
      dur: 0.3,
      // r93 · CALABAZA: el swing nace en el punto TANGENTE (la hoja en la
      // piel de la calabaza) — la bola NO se mueve del punto barrido.
      contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)
                    : ball.pos.clone(),
      flat: !!toca,               // sin ascenso inicial: hoja ya EN contacto
      dir: new THREE.Vector3(v.x, 0, v.z).normalize(),
      vdir: v.clone().normalize(),
      speed: THREE.MathUtils.clamp(v.length() / 6, 0.6, 1.5),
      // r88 · roll de muñeca = EFECTO real del tiro (topspin / cortada)
      roll: THREE.MathUtils.clamp(lift * 0.016, -0.30, 0.34) +
        (Math.random() - 0.5) * 0.08,
      back: carga * (toca ? 0.5 : 1),   // calabaza: la hoja ya está en la piel
      kind,                       // drive/smash/push/dejada/bloqueo
      fh: this.fhSide || 1,       // +1 derecha · -1 revés
    };
    // r99 · DISPARO DIFERIDO: update() devuelve null este frame — la salida
    // viaja en _disparo y update() la devuelve el frame en que la pala
    // llega al contacto (el juego aplica v, árbitro y sonido AQUÍ).
    return null;
  }

  /** r99 · TIEMPO DE LA BOLA AL CONTACTO: cuánto tarda la bola viva en
   *  alcanzar el punto de barrido (d/|v| con piso 2 m/s). Es la T del
   *  strike: la pala y la bola llegan juntas. */
  _tBolaDe(ball, cx, cy, cz) {
    const dx = cx - ball.pos.x, dy = cy - ball.pos.y, dz = cz - ball.pos.z;
    const d = Math.sqrt(dx * dx + dy * dy + dz * dz);
    return THREE.MathUtils.clamp(d / Math.max(2.0, ball.vel.length()), 0.03, 0.32);
  }

  /** r99 · GUARDA DEL DISPARO: la salida calculada espera a que la cadena
   *  de la pala llegue al punto de barrido (payload completo: bola, vel,
   *  spin, intercepto, blanco del solver, T y tope para el recálculo). */
  _preparaDisparo(ball, v, cx, cy, cz, spin, target, T, maxV) {
    this._disparo = {
      ball,
      v: v.clone(),
      spin: spin ? spin.clone() : new THREE.Vector3(),
      pos: new THREE.Vector3(cx, cy, cz),
      target: target ? target.clone() : null,
      T: T || 0.7,
      maxV: maxV || 10,
      t: 0,
      tMax: 0.75,
    };
  }

  /** r99 · APLICADOR DEL DISPARO: la pala GOLPEA la bola donde esté —
   *  si la bola está en el punto de barrido (±8 cm) se ajusta (deriva de
   *  predicción invisible); si pasó de largo (la pala llegó tarde), la
   *  PALA la atrapa: chain.cur salta a la bola (toque de muñeca real) y
   *  el follow-through arranca de ahí. El tiro se RECALCULA desde la
   *  posición real de la bola hacia el MISMO blanco: bota donde apunta,
   *  con contacto visible, sonido y árbitro sincronizados. */
  _aplicaDisparo() {
    const d = this._disparo;
    if (!d) return;
    this._disparo = null;
    const b = d.ball;
    if (b.pos.distanceTo(d.pos) < 0.08) b.pos.copy(d.pos);
    const vReal = d.target
      ? computeShotVelocityReal(b.pos, d.target, d.T, d.maxV, d.spin)
      : d.v;
    b.vel.copy(vReal);
    b.spin.copy(d.spin);
    b.ppEfecto = false;      // la devolución de la IA LIMPIA la marca
    b.ppEfectoTipo = '';
    b.ppEfectoLado = 0;
    b.ppPortal = false;      // la devolución de la IA LIMPIA el portal
    b.ppImanTocada = false;
    if (b.ppIman) b.ppIman.dv = 0;
    // la pala ATRAPA: su cur (y el arranque del follow) quedan EN la bola
    if (this.chain) {
      this.chain.cur.copy(b.pos);
      const s0 = this.chain.segs[this.chain.segIdx];
      if (s0) s0.p0.copy(b.pos);
    }
    this._retPend = vReal;
  }

  /** v2.84 · GOLPE MALO — contacto torpe cuando la IA falla a propósito.
   *  Salida débil y desviada (NUNCA una devolución limpia):
   *   · 50% toque flojo → cae en su campo (a la red o corto): doble bote
   *     propio, el árbitro lo resuelve con la causa que ya tenía.
   *   · 30% escacharrada → larga, cruzada y fuera (piso/pared).
   *   · 20% bola muerta que apenas cruza → regalo fácil (bote válido).
   *  La física (red, mesa, suelo) y el árbitro EXISTENTES resuelven cada
   *  desenlace sin ningún cambio: mismo reparto de puntos, pero el fallo
   *  se VE (la bola sale despedida torpe de la pala) y se OYE (toc flojo). */
  mishit(ball, toca) {
    const s = this.sign;
    const r = Math.random();
    if (r < 0.5) {
      // toque flojo: apenas empuja, cae en su propio campo
      _miV.set((Math.random() - 0.5) * 1.0, 0.25 + Math.random() * 0.55,
               -s * (0.35 + Math.random() * 0.7));
    } else if (r < 0.8) {
      // escacharrada: sale rápida, alta y cruzada — se marcha larga/fuera
      _miV.set((Math.random() - 0.5) * 2.0, 1.5 + Math.random() * 1.0,
               -s * (4.2 + Math.random() * 1.2));
    } else {
      // bola muerta: arco alto y lento que apenas pasa la red
      _miV.set((Math.random() - 0.5) * 0.8, 1.9 + Math.random() * 0.9,
               -s * (2.1 + Math.random() * 0.9));
    }
    _miV.addScaledVector(ball.vel, 0.05);   // hereda un 5% del impulso entrante
    ball.spin.set((Math.random() - 0.5) * 16, (Math.random() - 0.5) * 10, 0);
    ball.ppEfecto = false;   // v3.6.36: el golpe torpe de la IA LIMPIA la marca
    ball.ppEfectoTipo = '';  // v3.6.46: fuera también el tipo de spin
    ball.ppEfectoLado = 0;
    ball.ppPortal = false;   // v3.6.41: el golpe torpe LIMPIA el portal
    ball.ppImanTocada = false;             // v3.6.37: aproximación nueva
    if (ball.ppIman) ball.ppIman.dv = 0;   // v3.6.37: Δv del imán a cero
    this.swing = {
      t: 0, dur: 0.26,
      // r93 · CALABAZA: contacto tangente también en el golpe torpe
      contact: toca ? new THREE.Vector3(toca.x, toca.y, toca.z)
                    : ball.pos.clone(),
      flat: !!toca,
      dir: _miD.copy(_miV).setY(0).normalize().clone(),
      vdir: _miD.copy(_miV).normalize().clone(),
      speed: 0.5,                 // follow-through corto: toque sin cuerpo
      roll: (Math.random() - 0.5) * 0.5,
      back: 0.03,                 // r88: carga mínima — el toque no arma brazo
      kind: 'mala',               // pose torpe (SWING_POSE.mala)
      fh: this.fhSide || 1,
    };
    return _miV;   // el llamador copia la velocidad a la bola en el mismo frame
  }
}
const _aiSpin = new THREE.Vector3();
/* v2.84: rascadores del alcance barrido + del golpe malo (cero allocs/frame) */
const _segAB = new THREE.Vector3();
const _segAP = new THREE.Vector3();
const _segC = new THREE.Vector3();
const _miV = new THREE.Vector3();
const _miD = new THREE.Vector3();
/* r99 · intercepto del golpe (la bola ya NO se recoloca: el disparo nace
 * del punto de barrido sin tocar la bola viva) */
const _aiInt = new THREE.Vector3();

/* =====================================================================
 *  ESCENA · sala, mesa reglamentaria, bola con estela, rival con cuerpo,
 *  sombra proyectada, marcas de bote y marcador
 * ===================================================================== */

