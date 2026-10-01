/**
 * Árbitro del juego: reglas simplificadas del tenis de mesa.
 * - Partido a 11 puntos con ventaja de 2.
 * - Saque alternado cada 2 puntos (cada 1 en el desempate a partir de 10-10).
 * - Un golpe es válido si bota en el campo rival; falla si bota en el propio,
 *   se queda en la red o sale fuera. Saque fallado se repite (modo amable).
 */
import type { PhysEvent } from './physics'
import type { Side } from './constants'

export type RulesState = 'serve' | 'rally' | 'point' | 'over'

export type RulesIntent =
  | { type: 'point'; winner: Side; cause: string }
  | { type: 'retry-serve'; cause: string }
  | { type: 'serve'; server: Side }
  | { type: 'game-over'; winner: Side }

export class Rules {
  state: RulesState = 'serve'
  server: Side = 'player'
  scorePlayer = 0
  scoreAi = 0
  message = 'Saca cuando quieras: aprieta el gatillo'

  private totalPoints = 0
  private stateTimer = 0
  private lastHitter: Side | null = null
  private firstHitter: Side | null = null
  private mustBounceOpp = false
  private validBounce = false
  private isServeBall = false
  private netTouched = false

  private other(s: Side): Side {
    return s === 'player' ? 'ai' : 'player'
  }

  startMatch(): void {
    this.scorePlayer = 0
    this.scoreAi = 0
    this.totalPoints = 0
    this.server = 'player'
    this.state = 'serve'
    this.stateTimer = 0
    this.lastHitter = null
    this.firstHitter = null
    this.mustBounceOpp = false
    this.validBounce = false
    this.isServeBall = false
    this.netTouched = false
    this.message = 'Saca cuando quieras: aprieta el gatillo'
  }

  /** El servidor pone la bola en juego. */
  beginRally(who: Side, isServe: boolean): void {
    this.state = 'rally'
    this.lastHitter = who
    this.firstHitter = who
    this.mustBounceOpp = true
    this.validBounce = false
    this.isServeBall = isServe
    this.netTouched = false
  }

  /** Registro de un golpe de pala durante el intercambio. */
  registerPaddleHit(who: Side): void {
    if (this.state !== 'rally') return
    if (this.isServeBall && who !== this.firstHitter) this.isServeBall = false
    this.lastHitter = who
    this.mustBounceOpp = true
    this.validBounce = false
  }

  private applyPoint(winner: Side, cause: string): RulesIntent[] {
    if (winner === 'player') this.scorePlayer++
    else this.scoreAi++
    this.totalPoints++
    this.state = 'point'
    this.stateTimer = 2.1
    this.message =
      winner === 'player' ? `¡Punto para ti! · ${cause}` : `Punto para la CPU · ${cause}`
    return [{ type: 'point', winner, cause }]
  }

  private retryServe(cause: string): RulesIntent[] {
    this.state = 'serve'
    this.message = `${cause} · repite el saque`
    return [{ type: 'retry-serve', cause }]
  }

  private computeNextServer(): Side {
    const n = this.totalPoints
    if (this.scorePlayer >= 10 && this.scoreAi >= 10) {
      return n % 2 === 0 ? 'player' : 'ai'
    }
    return Math.floor(n / 2) % 2 === 0 ? 'player' : 'ai'
  }

  /** Consume los eventos de física y devuelve intenciones para el juego. */
  handleEvents(events: PhysEvent[]): RulesIntent[] {
    const intents: RulesIntent[] = []
    for (const e of events) {
      if (this.state !== 'rally') break

      switch (e.type) {
        case 'paddle': {
          if (e.who) this.registerPaddleHit(e.who)
          break
        }
        case 'net': {
          this.netTouched = true
          break
        }
        case 'table': {
          if (!e.side || !this.lastHitter) break
          const own = this.lastHitter
          const opp = this.other(own)
          if (this.mustBounceOpp) {
            if (e.side === opp) {
              this.mustBounceOpp = false
              this.validBounce = true
              this.netTouched = false
            } else {
              // Bota en el propio campo: falta
              if (this.isServeBall) {
                intents.push(...this.retryServe('Saque a tu campo'))
              } else {
                const cause =
                  own === 'player' ? 'golpeaste tu propio campo' : 'la CPU golpeó su campo'
                intents.push(...this.applyPoint(opp, cause))
              }
            }
          } else if (this.validBounce) {
            if (e.side === opp) {
              // Doble bote en el campo rival: el receptor no llegó
              const cause =
                own === 'player' ? 'doble bote: la CPU no llegó' : 'doble bote: no llegaste'
              intents.push(...this.applyPoint(own, cause))
            } else {
              // La bola volvió por efecto al campo del que golpeó
              const cause = own === 'player' ? 'la bola volvió a tu campo' : 'la bola volvió al campo de la CPU'
              intents.push(...this.applyPoint(opp, cause))
            }
          }
          break
        }
        case 'floor':
        case 'wall': {
          if (!this.lastHitter) break
          if (this.mustBounceOpp) {
            // Nunca botó en el campo rival: falta del último golpeador
            if (this.isServeBall) {
              intents.push(...this.retryServe(this.netTouched ? 'Saque a la red' : 'Saque fuera'))
            } else {
              const cause = this.netTouched
                ? 'se quedó en la red'
                : e.type === 'wall'
                  ? 'a la pared'
                  : 'bola fuera'
              intents.push(...this.applyPoint(this.other(this.lastHitter), cause))
            }
          } else {
            // Botó correctamente y el rival no la devolvió
            const cause = this.lastHitter === 'player' ? 'la CPU no la devolvió' : 'no la devolviste'
            intents.push(...this.applyPoint(this.lastHitter, cause))
          }
          break
        }
      }
    }
    return intents
  }

  /** Avanza los temporizadores de estado; devuelve intenciones (saques, fin de partido). */
  update(dt: number): RulesIntent[] {
    const intents: RulesIntent[] = []

    if (this.state === 'point') {
      this.stateTimer -= dt
      if (this.stateTimer <= 0) {
        const finished =
          (this.scorePlayer >= 11 || this.scoreAi >= 11) &&
          Math.abs(this.scorePlayer - this.scoreAi) >= 2
        if (finished) {
          this.state = 'over'
          this.stateTimer = 6
          const winner: Side = this.scorePlayer > this.scoreAi ? 'player' : 'ai'
          this.message = winner === 'player' ? '¡Has ganado el partido!' : 'La CPU gana el partido'
          intents.push({ type: 'game-over', winner })
        } else {
          this.state = 'serve'
          this.server = this.computeNextServer()
          this.message =
            this.server === 'player'
              ? 'Tu saque: aprieta el gatillo'
              : 'Saque de la CPU...'
          intents.push({ type: 'serve', server: this.server })
        }
      }
    } else if (this.state === 'over') {
      this.stateTimer -= dt
      if (this.stateTimer <= 0) {
        this.startMatch()
        this.message = 'Nuevo partido · saca con el gatillo'
        intents.push({ type: 'serve', server: this.server })
      }
    }

    return intents
  }
}
