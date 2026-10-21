export const ACHIEVEMENTS = [
  { key: 'primera',  emoji: '🥇', nameKey: 'ach_first',    descKey: 'ach_first_d' },
  { key: 'racha3',   emoji: '🔥', nameKey: 'ach_streak',   descKey: 'ach_streak_d' },
  { key: 'gigante',  emoji: '💪', nameKey: 'ach_giant',    descKey: 'ach_giant_d' },
  { key: 'maraton',  emoji: '🏃', nameKey: 'ach_marathon', descKey: 'ach_marathon_d' },
  { key: 'superviv', emoji: '⏱️', nameKey: 'ach_survivor', descKey: 'ach_survivor_d' },
  { key: 'aces10',   emoji: '🎯', nameKey: 'ach_aces',     descKey: 'ach_aces_d' },
];
/* DEPS-FASE2-INICIO (generado por scripts/mod_fase2_generar.mjs — no editar a mano) */
import { DIMS } from './c02_cfg_escena.js';
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

export class GameStats {
  constructor() {
    this.KEY = 'ppxr_stats_v1';
    this.data = {
      won: 0, lost: 0, streak: 0, bestStreak: 0,
      pointsWon: 0, pointsLost: 0, aces: 0, bestRally: 0,
      winsByDiff: { easy: 0, medium: 0, hard: 0 },
      ach: {},
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
  }

  save() {
    try { localStorage.setItem(this.KEY, JSON.stringify(this.data)); } catch { /* */ }
  }

  unlock(key) {
    if (this.data.ach[key]) return false;
    this.data.ach[key] = Date.now();
    this.save();
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
        if (this.data.aces >= 10 && this.unlock('aces10')) out.push('aces10');
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
    if (n >= 20 && this.unlock('maraton')) out.push('maraton');
    return out;
  }

  /** Rallye de SUPERVIVENCIA: récord histórico + logro dedicado. */
  recordSurvivalRally(golpes, bestEver) {
    const out = this.recordRally(golpes);
    if (bestEver >= 25 && this.unlock('superviv')) out.push('superviv');
    this.save();
    return out;
  }

  /** Fin de PARTIDO. Devuelve logros nuevos. */
  recordMatch(win, difficulty) {
    const out = [];
    if (win) {
      this.data.won++;
      this.data.streak++;
      if (this.data.streak > this.data.bestStreak) this.data.bestStreak = this.data.streak;
      this.data.winsByDiff[difficulty] = (this.data.winsByDiff[difficulty] || 0) + 1;
      if (this.unlock('primera')) out.push('primera');
      if (this.data.streak >= 3 && this.unlock('racha3')) out.push('racha3');
      if (difficulty === 'hard' && this.unlock('gigante')) out.push('gigante');
    } else {
      this.data.lost++;
      this.data.streak = 0;
    }
    this.save();
    return out;
  }
}


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
    this.bestOf = 1;                // 1 = juego único · 3 = mejor de 3
    this.gamesPlayer = 0;           // juegos ganados por el jugador
    this.gamesAi = 0;               // juegos ganados por el rival
    this.gameNo = 1;                // juego en curso dentro del enfrentamiento
    this.firstServer = 'player';    // primer sacador del ENFRENTAMIENTO
  }

  /** Nombre del oponente para los mensajes (CPU o humano remoto). */
  opp() { return T('opp_' + (this.oppLabel || 'cpu')); }

  other(s) { return s === 'player' ? 'ai' : 'player'; }

  /** v3.6.29: reset de UN juego (marcador y botes a cero SIN tocar la serie).
   *  startMatch = resetGame + serie a cero + bestOf intacto. */
  resetGame() {
    this.scorePlayer = 0;
    this.scoreAi = 0;
    this.totalPoints = 0;
    this.server = this.gameNo % 2 === 1
      ? this.firstServer
      : this.other(this.firstServer);   // cada juego saca el otro (ITTF)
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
    this.mode = mode === 'survival' ? 'survival' : 'match';
    this.rallyesSurvived = 0;
    // v3.6.29: NUEVO ENFRENTAMIENTO — la serie arranca a cero (bestOf se
    // conserva: lo fija el juego en los caminos del partido libre).
    this.gamesPlayer = 0;
    this.gamesAi = 0;
    this.gameNo = 1;
    this.firstServer = 'player';
    this.resetGame();
    this.message = this.mode === 'survival'
      ? T('surv_start')
      : T('serve_wait');
  }

  /** Comienza el rally tras un golpe de saque válido (al caer, tras la línea). */
  beginServeRally(server) {
    this.state = 'rally';
    this.lastHitter = server;
    this.isServeBall = true;
    this.serveOwnPending = true;
    this.mustBounceOpp = false;
    this.validBounce = false;
    this.netTouched = false;
    this.rallyHits = 0;
  }

  registerPaddleHit(who) {
    if (this.state !== 'rally') return [];
    // Nadie puede golpear dos veces seguidas (doble golpe = falta)
    if (who === this.lastHitter) {
      return this.applyPoint(this.other(who), 'dblhit');
    }
    // Volea: golpear antes de que la bote en su campo el receptor
    if (this.serveOwnPending || (this.mustBounceOpp && !this.validBounce)) {
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
    if (this.mode === 'survival') {
      // SUPERVIVENCIA: no hay puntos; lo que cuenta es el rallye terminado.
      // La CPU acelera con cada rallye (lo gestiona el juego con el intent).
      this.totalPoints++;
      this.rallyesSurvived++;
      this.state = 'point';
      this.stateTimer = 1.7;
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
    this.stateTimer = 2.2;
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

  computeNextServer() {
    const n = this.totalPoints;
    if (this.scorePlayer >= 10 && this.scoreAi >= 10) {
      return n % 2 === 0 ? 'player' : 'ai';
    }
    return Math.floor(n / 2) % 2 === 0 ? 'player' : 'ai';
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
        const finished =
          (this.scorePlayer >= 11 || this.scoreAi >= 11) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= 2;
        if (finished) {
          const winner = this.scorePlayer > this.scoreAi ? 'player' : 'ai';
          const p = this.scorePlayer, q = this.scoreAi;
          // v3.6.29 · MEJOR DE 3: el juego contado alimenta la serie; el
          // enfrentamiento se decide al ganar 2 juegos (2·victorias > bestOf).
          if (this.mode === 'match' && this.bestOf > 1) {
            if (winner === 'player') this.gamesPlayer++; else this.gamesAi++;
            const a = this.gamesPlayer, b = this.gamesAi;
            const serieAcabada = a * 2 > this.bestOf || b * 2 > this.bestOf;
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
    this.swing = null;   // animación de follow-through del último golpe (v2.17)
    this.prep = new THREE.Vector3();   // retroceso de preparación (visual)
    // v2.23: lado del golpe en curso — +1 derecha (forehand), -1 revés.
    // Se sortea al APARECER la bola (con la posición del cuerpo aún lejos del
    // punto de contacto) y se mantiene durante todo el rallye de esa bola.
    this.fhSide = 1;
  }

  setConfig(cfg) { this.cfg = cfg; }

  reset() {
    this.pos.copy(this.home);
    this.vel.set(0, 0, 0);
    this.predictValid = false;
    this.hitCooldown = 0;
  }

  update(dt, ball, ctx) {
    this.hitCooldown -= dt;
    if (this.swing) {
      this.swing.t += dt;
      if (this.swing.t > this.swing.dur) this.swing = null;
    }
    const C = DIMS.tableCenterZ;
    const sign = this.sign;
    const toward = ball.vel.z * sign > 0;

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
            this.errX = gauss() * this.cfg.errStd;
            this.errY = gauss() * this.cfg.errStd * 0.6;
            this.predict.copy(strike.point);
            // v2.23: ¿golpe de DERECHA o de REVÉS? Según el lado en que queda
            // la bola respecto al cuerpo al empezar a reaccionar (con sign:
            // positivo = lado de la mano derecha). Con bola centrada, se
            // prefiere la derecha como un jugador diestro.
            const dxf = (strike.point.x - this.pos.x) * sign;
            this.fhSide = Math.abs(dxf) > 0.05 ? (dxf > 0 ? 1 : -1) : (Math.random() < 0.55 ? 1 : -1);
          } else {
            // refinamiento de la MISMA bola: suavizar, sin saltos
            this.predict.lerp(strike.point, 0.45);
          }
          this.predictValid = true;
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
      tmpT.set(
        this.home.x + ball.pos.x * 0.3,
        this.home.y,
        this.home.z + (toward ? -sign * 0.2 : 0),
      );
    }

    tmpD.copy(tmpT).sub(this.pos);
    const dist = tmpD.length();
    const desiredSpeed = Math.min(this.cfg.maxSpeed, dist * 4.5);
    if (dist > 1e-5) tmpD.setLength(desiredSpeed); else tmpD.set(0, 0, 0);
    this.vel.lerp(tmpD, Math.min(1, dt * this.cfg.accel));
    this.pos.addScaledVector(this.vel, dt);

    if (!ctx.canHit || !ctx.validBounce || !toward || this.hitCooldown > 0) return null;
    // v2.84 · ALCANCE BARRIDO (anti-túnel): la decisión llega un frame tarde
    // (la IA ve la bola ya integrada). Con smashes la bola salta >0,21 m
    // entre frames y se COLABA por la esfera de alcance: atravesaba la pala
    // sin ser vista. Ahora se mide la distancia al SEGMENTO recorrido por la
    // bola en el último paso de física (ctx.prevBall, capturado en el bucle)
    // y el contacto se produce en el punto exacto de ese trayecto. Tope de
    // longitud 0,5 m: un salto mayor es un TELEPORTE (reposición de saque,
    // resets) y no debe contar como contacto.
    const reach = 0.21;
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
    if ((cz - C) * sign < 0.04) return null;
    if (cy < DIMS.tableTopY - 0.08 || cy > 1.65) return null;

    const ballSpeed = ball.vel.length();
    const pMiss = this.cfg.missBase + Math.max(0, ballSpeed - 7) * 0.05;
    this.hitCooldown = 0.55;
    // v2.84 · GOLPE MALO (petición del artista): el fallo decidido de la IA
    // YA NO deja pasar la bola a través de la pala (efecto pésimo). La toca
    // MAL: contacto flojo y desviado que se queda en su campo (red o corto),
    // se marcha larga/fuera o cruza floja y alta — el punto se pierde igual
    // pero con contacto, sonido y pose creíbles en lugar del cruce fantasma.
    if (Math.random() < pMiss) {
      if (cx !== ball.pos.x || cy !== ball.pos.y || cz !== ball.pos.z) {
        ball.pos.set(cx, cy, cz);   // recolocar en el punto del barrido
      }
      return this.mishit(ball);
    }
    // v2.84: golpe LIMPIO con contacto barrido — la salida parte del punto
    // real donde la pala alcanzó la bola (no del punto ya pasado)
    if (cx !== ball.pos.x || cy !== ball.pos.y || cz !== ball.pos.z) {
      ball.pos.set(cx, cy, cz);
    }

    // ---------- SELECCIÓN DE GOLPE (v2.11 · IA lista) ----------
    // Cuatro golpes según la situación: remate a bolas altas, dejada corta
    // si el rival está lejos de la mesa, push con slice a bolas bajas y
    // drive con lift (topspin) como golpe por defecto. Más un bloqueo
    // rápido para devolver bolas fuertes sin regalar velocidad.
    const oppDeep = ctx.oppPadZ !== undefined
      ? ((ctx.oppPadZ - DIMS.tableCenterZ) * -sign > DIMS.tableHalfLength * 0.3)
      : (Math.random() < 0.35);
    const high = ball.pos.y > 1.15;
    const low = ball.pos.y < DIMS.tableTopY + 0.16;
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
    // bota donde apunta en vez de 15-27 cm corto
    const v = computeShotVelocityReal(ball.pos, tmpTarget, T, maxV, shotSpin);
    ball.spin.copy(shotSpin);
    ball.ppEfecto = false;   // v3.6.36: la devolución de la IA LIMPIA la marca

    // swing visual: follow-through del golpe en la dirección del tiro.
    // v2.23: lleva TAMBIÉN el tipo de golpe, el lado (derecha/revés) y la
    // velocidad de salida 3D — la pose de la pala los usa para girar la hoja,
    // abrir/cerrar la cara y cruzar el cuerpo como un jugador real.
    this.swing = {
      t: 0,
      dur: 0.3,
      contact: ball.pos.clone(),
      dir: new THREE.Vector3(v.x, 0, v.z).normalize(),
      vdir: v.clone().normalize(),
      speed: THREE.MathUtils.clamp(v.length() / 6, 0.6, 1.5),
      // roll de muñeca propio de cada golpe (la cara acompaña el tiro
      // con un giro natural, nunca dos golpes idénticos)
      roll: (Math.random() - 0.5) * 0.34,
      kind,                       // drive/smash/push/dejada/bloqueo
      fh: this.fhSide || 1,       // +1 derecha · -1 revés
    };
    return v;
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
  mishit(ball) {
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
    this.swing = {
      t: 0, dur: 0.26,
      contact: ball.pos.clone(),
      dir: _miD.copy(_miV).setY(0).normalize().clone(),
      vdir: _miD.copy(_miV).normalize().clone(),
      speed: 0.5,                 // follow-through corto: toque sin cuerpo
      roll: (Math.random() - 0.5) * 0.5,
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

/* =====================================================================
 *  ESCENA · sala, mesa reglamentaria, bola con estela, rival con cuerpo,
 *  sombra proyectada, marcas de bote y marcador
 * ===================================================================== */

