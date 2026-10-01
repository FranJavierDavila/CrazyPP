'use client'

/**
 * Interfaz del juego: canvas WebGL a pantalla completa + HUD superpuesto.
 * La lógica Three.js/WebXR se carga dinámicamente solo en el cliente.
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import type { PingPongGame } from '@/lib/game/game'
import type { Difficulty, Side } from '@/lib/game/constants'

const DIFFICULTY_LABELS: { value: Difficulty; label: string }[] = [
  { value: 'easy', label: 'Fácil' },
  { value: 'medium', label: 'Medio' },
  { value: 'hard', label: 'Difícil' },
]

export function PingPongCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const gameRef = useRef<PingPongGame | null>(null)

  const [ready, setReady] = useState(false)
  const [fatalError, setFatalError] = useState<string | null>(null)
  const [xrSupported, setXrSupported] = useState<boolean | null>(null)
  const [inVR, setInVR] = useState(false)
  const [score, setScore] = useState({ player: 0, ai: 0 })
  const [server, setServer] = useState<Side>('player')
  const [message, setMessage] = useState<string>('')
  const [difficulty, setDifficulty] = useState<Difficulty>('medium')
  const [entering, setEntering] = useState(false)

  useEffect(() => {
    let disposed = false

    const init = async () => {
      try {
        const { PingPongGame: Game } = await import('@/lib/game/game')
        if (disposed || !canvasRef.current) return

        gameRef.current = new Game(canvasRef.current, {
          onScore: (p, a, s) => {
            setScore({ player: p, ai: a })
            setServer(s)
          },
          onMessage: (m) => setMessage(m),
          onXRState: (v) => setInVR(v),
        })
        setReady(true)

        const xr = (navigator as Navigator & { xr?: XRSystem }).xr
        if (xr) {
          const ok = await xr.isSessionSupported('immersive-vr')
          if (!disposed) setXrSupported(ok)
        } else if (!disposed) {
          setXrSupported(false)
        }
      } catch (err) {
        console.error('Error iniciando el juego:', err)
        if (!disposed) {
          setFatalError(
            err instanceof Error
              ? err.message
              : 'No se pudo iniciar WebGL en este dispositivo.',
          )
        }
      }
    }

    void init()
    return () => {
      disposed = true
      gameRef.current?.dispose()
      gameRef.current = null
    }
  }, [])

  const enterVR = useCallback(async () => {
    const game = gameRef.current
    if (!game) return
    setEntering(true)
    try {
      await game.enterVR()
    } catch (err) {
      setMessage(
        err instanceof Error ? `No se pudo iniciar VR: ${err.message}` : 'No se pudo iniciar VR',
      )
      window.setTimeout(() => setMessage(''), 4000)
    } finally {
      setEntering(false)
    }
  }, [])

  const changeDifficulty = useCallback((d: Difficulty) => {
    setDifficulty(d)
    gameRef.current?.setDifficulty(d)
  }, [])

  const vrButtonDisabled = !ready || xrSupported === false || entering || inVR

  return (
    <div className="fixed inset-0 bg-[#0b0e11] text-foreground">
      <canvas ref={canvasRef} className="absolute inset-0 h-full w-full" aria-label="Escena 3D de ping pong" />

      {/* HUD */}
      <div className="pointer-events-none absolute inset-0 flex flex-col justify-between p-4 sm:p-6">
        {/* Cabecera: título y marcador */}
        <header className="flex items-start justify-between gap-3">
          <div className="flex flex-col gap-2">
            <Badge variant="outline" className="w-fit border-amber-500/50 bg-black/50 text-amber-400 backdrop-blur">
              PING PONG XR · WEBXR
            </Badge>
            <Badge variant="outline" className="w-fit border-zinc-700 bg-black/40 text-zinc-300 backdrop-blur">
              {inVR
                ? 'Sesión inmersiva activa'
                : xrSupported === false
                  ? 'Vista previa (IA vs IA) · abre en Quest Browser para jugar'
                  : 'Comprobando WebXR...'}
            </Badge>
          </div>

          <div
            className={`flex items-center gap-3 rounded-xl border border-zinc-800 bg-black/60 px-4 py-2 backdrop-blur transition-opacity ${
              inVR ? 'opacity-0' : 'opacity-100'
            }`}
            role="status"
            aria-label="Marcador"
          >
            <span className="text-sm font-semibold text-amber-400">
              TÚ{server === 'player' ? ' ·' : ''}
            </span>
            <span className="text-2xl font-black tabular-nums tracking-tight">
              {score.player} : {score.ai}
            </span>
            <span className="text-sm font-semibold text-emerald-400">
              {server === 'ai' ? '· CPU' : 'CPU'}
            </span>
          </div>
        </header>

        {/* Mensaje del árbitro */}
        {message && !inVR && (
          <div className="mx-auto max-w-md">
            <p className="rounded-lg border border-zinc-800 bg-black/70 px-4 py-2 text-center text-sm font-medium text-zinc-100 backdrop-blur">
              {message}
            </p>
          </div>
        )}

        {/* Panel inferior: controles e instrucciones */}
        <footer className="pointer-events-auto mx-auto w-full max-w-3xl">
          {fatalError ? (
            <Alert variant="destructive" className="bg-black/80 backdrop-blur">
              <AlertTitle>No se pudo iniciar el juego</AlertTitle>
              <AlertDescription>{fatalError}</AlertDescription>
            </Alert>
          ) : (
            <div className="rounded-2xl border border-zinc-800 bg-black/60 p-4 backdrop-blur sm:p-5">
              <div className="flex flex-col items-center gap-4 sm:flex-row sm:justify-between">
                <div className="flex flex-col items-center gap-2 sm:items-start">
                  <Button
                    size="lg"
                    onClick={() => void enterVR()}
                    disabled={vrButtonDisabled}
                    className="h-12 bg-amber-500 px-6 text-base font-bold text-black hover:bg-amber-400"
                  >
                    {entering ? 'Iniciando VR...' : inVR ? 'Ya estás dentro' : 'Entrar en VR'}
                  </Button>
                  {xrSupported === false && (
                    <p className="text-xs text-zinc-400">
                      WebXR no disponible aquí. Ábrelo en <strong>Meta Quest Browser</strong> dentro
                      de tus Quest 3.
                    </p>
                  )}
                </div>

                <div className="flex flex-col items-center gap-2 sm:items-end">
                  <span className="text-xs font-medium uppercase tracking-wide text-zinc-500">
                    Dificultad de la CPU
                  </span>
                  <div className="flex gap-1 rounded-lg border border-zinc-800 bg-zinc-950 p-1">
                    {DIFFICULTY_LABELS.map((d) => (
                      <button
                        key={d.value}
                        type="button"
                        onClick={() => changeDifficulty(d.value)}
                        aria-pressed={difficulty === d.value}
                        className={`rounded-md px-3 py-1.5 text-sm font-semibold transition-colors ${
                          difficulty === d.value
                            ? 'bg-amber-500 text-black'
                            : 'text-zinc-400 hover:text-zinc-100'
                        }`}
                      >
                        {d.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-1 gap-x-6 gap-y-1 border-t border-zinc-800 pt-3 text-xs text-zinc-400 sm:grid-cols-2">
                <p>
                  <strong className="text-zinc-200">1.</strong> Abre esta página en Meta Quest
                  Browser y pulsa «Entrar en VR».
                </p>
                <p>
                  <strong className="text-zinc-200">2.</strong> Colócate sobre la marca circular del
                  suelo, frente a la mesa.
                </p>
                <p>
                  <strong className="text-zinc-200">3.</strong> Aprieta el <strong>gatillo</strong>{' '}
                  para sacar y mueve el mando para golpear.
                </p>
                <p>
                  <strong className="text-zinc-200">4.</strong> Partido a{' '}
                  <strong>11 puntos</strong> (ventaja de 2). Sentirás la vibración en cada golpe.
                </p>
              </div>
            </div>
          )}
        </footer>
      </div>
    </div>
  )
}
