/**
 * Sonido sintetizado con Web Audio API (sin assets externos).
 * Todos los efectos se generan proceduralmente con osciladores y ruido,
 * con paneo estéreo según la posición X de la bola.
 */

export class GameAudio {
  private ctx: AudioContext | null = null
  private master: GainNode | null = null
  private noiseBuffer: AudioBuffer | null = null

  /** Debe llamarse desde un gesto del usuario (clic / botón VR). */
  ensure(): void {
    if (this.ctx) {
      if (this.ctx.state === 'suspended') void this.ctx.resume()
      return
    }
    try {
      const Ctor =
        window.AudioContext ??
        (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext
      if (!Ctor) return
      this.ctx = new Ctor()
      this.master = this.ctx.createGain()
      this.master.gain.value = 0.5
      this.master.connect(this.ctx.destination)

      const len = Math.floor(this.ctx.sampleRate * 0.25)
      this.noiseBuffer = this.ctx.createBuffer(1, len, this.ctx.sampleRate)
      const data = this.noiseBuffer.getChannelData(0)
      for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1
    } catch {
      this.ctx = null
    }
  }

  private panNode(pan: number): StereoPannerNode | null {
    if (!this.ctx || !this.master) return null
    const p = this.ctx.createStereoPanner()
    p.pan.value = Math.max(-1, Math.min(1, pan))
    p.connect(this.master)
    return p
  }

  private playOsc(
    freq: number,
    endFreq: number,
    dur: number,
    type: OscillatorType,
    gain: number,
    pan: number,
  ): void {
    if (!this.ctx) return
    const dest = this.panNode(pan)
    if (!dest) return
    const t = this.ctx.currentTime
    const osc = this.ctx.createOscillator()
    const g = this.ctx.createGain()
    osc.type = type
    osc.frequency.setValueAtTime(Math.max(20, freq), t)
    osc.frequency.exponentialRampToValueAtTime(Math.max(20, endFreq), t + dur)
    g.gain.setValueAtTime(gain, t)
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur)
    osc.connect(g)
    g.connect(dest)
    osc.start(t)
    osc.stop(t + dur + 0.02)
  }

  private playNoise(
    dur: number,
    filterFreq: number,
    q: number,
    gain: number,
    pan: number,
    type: BiquadFilterType = 'bandpass',
  ): void {
    if (!this.ctx || !this.noiseBuffer) return
    const dest = this.panNode(pan)
    if (!dest) return
    const t = this.ctx.currentTime
    const src = this.ctx.createBufferSource()
    src.buffer = this.noiseBuffer
    const filter = this.ctx.createBiquadFilter()
    filter.type = type
    filter.frequency.value = filterFreq
    filter.Q.value = q
    const g = this.ctx.createGain()
    g.gain.setValueAtTime(gain, t)
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur)
    src.connect(filter)
    filter.connect(g)
    g.connect(dest)
    src.start(t)
    src.stop(t + dur + 0.02)
  }

  /** Golpe de pala: ataque seco con cuerpo de madera. */
  paddle(pan: number, strength: number): void {
    const s = Math.max(0.15, Math.min(1, strength))
    this.playNoise(0.05, 1400, 1.2, 0.55 * s, pan)
    this.playOsc(190 - 40 * s, 110, 0.09, 'triangle', 0.5 * s, pan)
  }

  /** Rebote en la mesa: "tok" agudo. */
  tableBounce(pan: number, strength: number): void {
    const s = Math.max(0.1, Math.min(1, strength))
    this.playOsc(950, 700, 0.05, 'sine', 0.4 * s, pan)
    this.playNoise(0.02, 3000, 2, 0.18 * s, pan)
  }

  /** Golpe contra la red: golpe sordo. */
  net(pan: number): void {
    this.playOsc(210, 150, 0.1, 'sine', 0.35, pan)
    this.playNoise(0.06, 420, 1, 0.25, pan, 'lowpass')
  }

  /** Bola contra suelo/pared. */
  thud(pan: number, strength: number): void {
    const s = Math.max(0.05, Math.min(1, strength))
    this.playOsc(140, 90, 0.09, 'sine', 0.28 * s, pan)
  }

  /** Lanzamiento del saque. */
  serve(): void {
    this.playNoise(0.14, 650, 0.8, 0.16, 0)
  }

  /** Jingle al ganar/perder el punto. */
  point(win: boolean): void {
    if (win) {
      this.playOsc(660, 660, 0.12, 'sine', 0.3, -0.3)
      window.setTimeout(() => this.playOsc(880, 880, 0.18, 'sine', 0.3, -0.3), 110)
    } else {
      this.playOsc(440, 440, 0.12, 'sine', 0.28, 0.3)
      window.setTimeout(() => this.playOsc(330, 330, 0.2, 'sine', 0.28, 0.3), 110)
    }
  }

  dispose(): void {
    try {
      void this.ctx?.close()
    } catch {
      /* ignorar */
    }
    this.ctx = null
    this.master = null
  }
}
