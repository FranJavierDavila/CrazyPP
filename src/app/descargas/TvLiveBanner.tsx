"use client";

import { useEffect, useState } from "react";

/**
 * CRAZY TV · banner de emisiones en vivo para el centro de descargas.
 * Consulta la parrilla del relay (puerto 3004 vía gateway) y muestra
 * cuántos canales hay EN DIRECTO ahora mismo. Enlace al espectador /tv.html.
 */
export default function TvLiveBanner() {
  const [canales, setCanales] = useState<number | null>(null);
  const [vivo, setVivo] = useState(false);

  useEffect(() => {
    let muerto = false;
    const consulta = async () => {
      try {
        const r = await fetch("/api/channels?XTransformPort=3004", { cache: "no-store" });
        const j = await r.json();
        if (!muerto) {
          const n = (j?.channels ?? []).length;
          setCanales(n);
          setVivo(n > 0);
        }
      } catch {
        if (!muerto) setCanales(null);
      }
    };
    consulta();
    const t = setInterval(consulta, 5000);
    return () => { muerto = true; clearInterval(t); };
  }, []);

  return (
    <a
      href="/tv.html"
      className="group mt-8 flex items-center gap-4 rounded-2xl border border-amber-400/40 bg-gradient-to-r from-[#241d0e] via-[#101E33] to-[#101E33] p-5 transition hover:-translate-y-0.5 hover:border-amber-300 hover:shadow-lg hover:shadow-amber-500/10"
    >
      {/* Icono de televisión */}
      <span className="relative flex h-14 w-14 shrink-0 items-center justify-center rounded-xl border border-amber-400/50 bg-[#0B1526]">
        <svg viewBox="0 0 24 24" fill="none" stroke="#fbbf24" strokeWidth="1.8" strokeLinecap="round" className="h-8 w-8">
          <rect x="2.5" y="7" width="19" height="13" rx="2.5" />
          <path d="M8.5 3.5 12 7l3.5-3.5" />
        </svg>
        {vivo && (
          <span className="absolute -right-1.5 -top-1.5 h-3.5 w-3.5 animate-pulse rounded-full bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.9)]" />
        )}
      </span>

      <span className="min-w-0 flex-1">
        <span className="flex flex-wrap items-center gap-2">
          <span className="text-lg font-extrabold tracking-wide text-amber-300">
            CRAZY TV · Emisiones en vivo
          </span>
          {vivo ? (
            <span className="inline-flex items-center gap-1.5 rounded-md bg-red-600 px-2 py-0.5 text-[11px] font-extrabold tracking-widest text-white">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-white" />
              EN DIRECTO
            </span>
          ) : canales !== null ? (
            <span className="rounded-md border border-slate-600 px-2 py-0.5 text-[11px] font-bold tracking-wider text-slate-400">
              SIN EMISIONES
            </span>
          ) : null}
        </span>
        <span className="mt-1 block text-sm leading-relaxed text-slate-400">
          {vivo
            ? `Hay ${canales === 1 ? "1 partida" : `${canales} partidas`} jugándose ahora mismo — entra como espectador sin visor y míralas en directo, con repeticiones y cámaras.`
            : "Cuando un jugador arranque una partida en su Quest 3, su mesa aparecerá aquí como un canal de TV. Entra a la parrilla y mira en directo sin visor."}
        </span>
      </span>

      <span className="shrink-0 rounded-xl bg-amber-400 px-4 py-2.5 text-sm font-extrabold text-[#0B1526] transition group-hover:bg-amber-300">
        📺 Abrir la TV
      </span>
    </a>
  );
}
