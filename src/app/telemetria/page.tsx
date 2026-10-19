"use client";

import { useCallback, useEffect, useState } from "react";

/**
 * CRAZY PING PONG · PANEL DE TELEMETRÍA (ronda 6 · roadmap P1 · ronda 8 doble fuente)
 * Vista en vivo del receptor LOCAL (/api/telemetria) y del WORKER DE PRODUCCIÓN
 * (D1 en Cloudflare, ronda 8) con la clave del dueño. Misma estética que el hub
 * de descargas. Anónima por diseño: sólo contadores, sids aleatorios y FPS —
 * sin IP, sin user-agent, sin contenido de partida.
 */

type Ev = Record<string, unknown> & { e?: string; sid?: string; t?: number; _rec?: number };

type Resumen = {
  ok: boolean;
  ts: number;
  total: number;
  sesionesUnicas: number;
  arranques24h: number;
  porEvento: Record<string, number>;
  sesiones: { sid: string; primero: number; ultimo: number; n: number }[];
  fps: { medio: number | null; muestras: number };
  erroresTop: [string, number][];
  champRank: Record<string, { partidas: number; victorias: number; mejor: number; estrellas: number }>;
  ultimos: Ev[];
  almacen: string;
};

const WORKER_DEF = "https://crazypp-tele.escala3dcorreoia.workers.dev/api/tele";

const hhmm = (t: number) =>
  t ? new Date(t).toLocaleString("es-ES", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }) : "—";

const fmt = (n: number) => n.toLocaleString("es-ES");

export default function Telemetria() {
  const [r, setR] = useState<Resumen | null>(null);
  const [err, setErr] = useState<string>("");
  const [pausa, setPausa] = useState(false);
  const [filtro, setFiltro] = useState("");
  const [fuente, setFuente] = useState<"local" | "prod">("local");
  const [prodUrl, setProdUrl] = useState(WORKER_DEF);
  const [prodClave, setProdClave] = useState("");

  // preferencias persistidas (solo en el cliente: el SSR arranca en local)
  useEffect(() => {
    try {
      const f = localStorage.getItem("pp_tele_fuente");
      if (f === "prod" || f === "local") setFuente(f);
      const u = localStorage.getItem("pp_tele_prod_url");
      if (u) setProdUrl(u);
      const c = localStorage.getItem("pp_tele_prod_clave");
      if (c) setProdClave(c);
    } catch {}
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem("pp_tele_fuente", fuente);
      localStorage.setItem("pp_tele_prod_url", prodUrl);
      localStorage.setItem("pp_tele_prod_clave", prodClave);
    } catch {}
  }, [fuente, prodUrl, prodClave]);

  const carga = useCallback(async () => {
    try {
      const esProd = fuente === "prod";
      const base = esProd ? prodUrl.trim() : "/api/telemetria";
      if (esProd && !prodClave.trim()) {
        setR(null);
        setErr("Producción: escribe la CLAVE del worker para leer (se guarda solo en este navegador)");
        return;
      }
      const p = new URLSearchParams({ resumen: "1" });
      if (filtro.trim()) p.set("sid", filtro.trim());
      if (esProd) p.set("clave", prodClave.trim());
      const res = await fetch(`${base}?${p}`, { cache: "no-store" });
      const texto = await res.text();
      if (!res.ok) {
        throw new Error(
          res.status === 403
            ? "clave incorrecta o sin CLAVE en el worker (HTTP 403)"
            : `HTTP ${res.status}: ${texto.slice(0, 120)}`
        );
      }
      const j = JSON.parse(texto) as Resumen;
      if (!j.ok) throw new Error("ok=false");
      setR(j);
      setErr("");
    } catch (e) {
      setErr(String((e as Error).message || e));
    }
  }, [filtro, fuente, prodUrl, prodClave]);

  useEffect(() => {
    carga();
    if (pausa) return;
    const iv = setInterval(carga, 10000);
    return () => clearInterval(iv);
  }, [carga, pausa]);

  const purga = async () => {
    const esProd = fuente === "prod";
    if (!confirm(`¿Borrar TODOS los eventos de ${esProd ? "PRODUCCIÓN (D1 del worker)" : "el almacén local"}?`)) return;
    const p = new URLSearchParams();
    if (filtro.trim()) p.set("sid", filtro.trim());
    if (esProd) p.set("clave", prodClave.trim());
    await fetch(`${esProd ? prodUrl.trim() : "/api/telemetria"}?${p}`, { method: "DELETE" });
    carga();
  };

  const eventos = r ? Object.entries(r.porEvento).sort((a, b) => b[1] - a[1]) : [];

  return (
    <main className="min-h-screen bg-[#0B1526] text-slate-100">
      <div className="mx-auto max-w-6xl px-5 py-10">
        {/* Cabecera */}
        <header className="mb-8 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-orange-400">
            CRAZY PING PONG
          </p>
          <h1 className="mt-2 text-4xl font-black tracking-tight">📡 Telemetría anónima</h1>
          <p className="mt-2 text-sm text-slate-400">
            {fuente === "local" ? (
              <>
                Receptor local <code className="rounded bg-slate-800 px-1">/api/telemetria</code>
              </>
            ) : (
              <>
                Producción <code className="rounded bg-slate-800 px-1">worker /api/tele (D1)</code>
              </>
            )}{" "}
            · almacén <code className="rounded bg-slate-800 px-1">{r?.almacen ?? (fuente === "local" ? "telemetria/eventos.jsonl" : "d1:crazypp-tele")}</code> · sin IP · sin
            user-agent · opt-out desde Opciones del juego
          </p>
        </header>

        {/* Controles */}
        <div className="mb-6 flex flex-wrap items-center justify-center gap-3 text-sm">
          <div className="flex overflow-hidden rounded-md border border-slate-700">
            <button
              onClick={() => setFuente("local")}
              className={`px-4 py-1.5 ${fuente === "local" ? "bg-orange-500 font-bold text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}
            >
              Local
            </button>
            <button
              onClick={() => setFuente("prod")}
              className={`px-4 py-1.5 ${fuente === "prod" ? "bg-orange-500 font-bold text-slate-950" : "text-slate-300 hover:bg-slate-800"}`}
            >
              Producción (D1)
            </button>
          </div>
          {fuente === "prod" && (
            <>
              <input
                value={prodUrl}
                onChange={(e) => setProdUrl(e.target.value)}
                placeholder="URL del worker…"
                className="w-72 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 font-mono text-xs outline-none focus:border-orange-400"
              />
              <input
                value={prodClave}
                onChange={(e) => setProdClave(e.target.value)}
                type="password"
                placeholder="CLAVE del worker…"
                className="w-40 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 outline-none focus:border-orange-400"
              />
            </>
          )}
          <input
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
            placeholder="filtrar por sid…"
            className="w-56 rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 outline-none focus:border-orange-400"
          />
          <button
            onClick={carga}
            className="rounded-md bg-orange-500 px-4 py-1.5 font-semibold text-slate-950 hover:bg-orange-400"
          >
            Refrescar
          </button>
          <button
            onClick={() => setPausa((p) => !p)}
            className="rounded-md border border-slate-700 px-4 py-1.5 hover:border-slate-500"
          >
            {pausa ? "▶ Reanudar auto" : "⏸ Pausar auto"}
          </button>
          <button
            onClick={purga}
            className="rounded-md border border-rose-800 px-4 py-1.5 text-rose-300 hover:bg-rose-950"
          >
            🗑 Purgar
          </button>
        </div>

        {err && (
          <p className="mb-6 rounded-md border border-rose-800 bg-rose-950/50 px-4 py-3 text-center text-rose-200">
            Receptor sin respuesta: {err}
          </p>
        )}

        {!r ? (
          <p className="py-16 text-center text-slate-500">Cargando resumen…</p>
        ) : (
          <>
            {/* KPIs */}
            <section className="mb-8 grid grid-cols-2 gap-3 md:grid-cols-4">
              {[
                { t: "Eventos", v: fmt(r.total), s: `últ. ${hhmm(r.ts)}` },
                { t: "Sesiones únicas", v: fmt(r.sesionesUnicas), s: "sid aleatorios" },
                { t: "Arranques 24 h", v: fmt(r.arranques24h), s: "eventos boot" },
                {
                  t: "FPS medio (VR)",
                  v: r.fps.medio === null ? "—" : fmt(r.fps.medio),
                  s: `${r.fps.muestras} sesiones vr_end`,
                },
              ].map((k) => (
                <div key={k.t} className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 text-center">
                  <p className="text-xs uppercase tracking-wider text-slate-400">{k.t}</p>
                  <p className="mt-1 text-3xl font-black text-orange-300">{k.v}</p>
                  <p className="mt-1 text-xs text-slate-500">{k.s}</p>
                </div>
              ))}
            </section>

            <div className="grid gap-6 lg:grid-cols-2">
              {/* Por evento */}
              <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
                <h2 className="mb-3 text-lg font-bold">Eventos por tipo</h2>
                {eventos.length === 0 ? (
                  <p className="text-sm text-slate-500">Sin eventos aún. Juega una sesión o espera el primer flush (5 s).</p>
                ) : (
                  <ul className="space-y-1.5 text-sm">
                    {eventos.map(([k, n]) => (
                      <li key={k} className="flex items-center gap-3">
                        <span className="w-36 shrink-0 font-mono text-slate-300">{k}</span>
                        <div className="h-2.5 flex-1 overflow-hidden rounded bg-slate-800">
                          <div
                            className="h-full rounded bg-gradient-to-r from-orange-600 to-orange-400"
                            style={{ width: `${Math.max(3, Math.round((n / eventos[0][1]) * 100))}%` }}
                          />
                        </div>
                        <span className="w-12 text-right font-bold text-orange-300">{fmt(n)}</span>
                      </li>
                    ))}
                  </ul>
                )}
                <p className="mt-4 border-t border-slate-800 pt-3 text-xs text-slate-500">
                  Catálogo y contrato: <code>scripts/telemetria_catalogo.json</code> · sondeo de producción:{" "}
                  <code>scripts/sondea_tele_worker.py</code>
                </p>
              </section>

              {/* champ_rank */}
              <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
                <h2 className="mb-3 text-lg font-bold">Resultados de campeonatos (champ_rank)</h2>
                {Object.keys(r.champRank).length === 0 ? (
                  <p className="text-sm text-slate-500">Sin reportes champ_rank aún (prueba del orbe de Magia).</p>
                ) : (
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-xs uppercase text-slate-500">
                        <th className="pb-2">Campeonato</th>
                        <th className="pb-2 text-right">Partidas</th>
                        <th className="pb-2 text-right">Victorias</th>
                        <th className="pb-2 text-right">Mejor</th>
                        <th className="pb-2 text-right">★</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(r.champRank).map(([c, d]) => (
                        <tr key={c} className="border-t border-slate-800">
                          <td className="py-1.5 font-mono text-slate-200">{c}</td>
                          <td className="py-1.5 text-right">{fmt(d.partidas)}</td>
                          <td className="py-1.5 text-right text-emerald-300">{fmt(d.victorias)}</td>
                          <td className="py-1.5 text-right">{fmt(d.mejor)}</td>
                          <td className="py-1.5 text-right text-amber-300">{fmt(d.estrellas)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </section>

              {/* Sesiones */}
              <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
                <h2 className="mb-3 text-lg font-bold">Últimas sesiones</h2>
                {r.sesiones.length === 0 ? (
                  <p className="text-sm text-slate-500">Sin sesiones registradas.</p>
                ) : (
                  <div className="max-h-64 overflow-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="text-left text-xs uppercase text-slate-500">
                          <th className="pb-2">sid</th>
                          <th className="pb-2">Inicio</th>
                          <th className="pb-2">Último</th>
                          <th className="pb-2 text-right">Eventos</th>
                        </tr>
                      </thead>
                      <tbody>
                        {r.sesiones.map((s) => (
                          <tr key={s.sid} className="border-t border-slate-800">
                            <td className="py-1.5 font-mono text-xs text-slate-300">{s.sid}</td>
                            <td className="py-1.5 text-slate-400">{hhmm(s.primero)}</td>
                            <td className="py-1.5 text-slate-400">{hhmm(s.ultimo)}</td>
                            <td className="py-1.5 text-right">{fmt(s.n)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </section>

              {/* Errores */}
              <section className="rounded-xl border border-slate-800 bg-slate-900/60 p-5">
                <h2 className="mb-3 text-lg font-bold">Errores de página (top)</h2>
                {r.erroresTop.length === 0 ? (
                  <p className="text-sm text-slate-500">Sin errores capturados. 🎉</p>
                ) : (
                  <ul className="space-y-1 text-sm">
                    {r.erroresTop.map(([m, n]) => (
                      <li key={m} className="flex gap-2 border-b border-slate-800/60 pb-1">
                        <span className="shrink-0 font-bold text-rose-300">×{n}</span>
                        <span className="break-all font-mono text-xs text-slate-300">{m}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>

            {/* Últimos crudos */}
            <section className="mt-6 rounded-xl border border-slate-800 bg-slate-900/60 p-5">
              <h2 className="mb-3 text-lg font-bold">Últimos 20 eventos (crudos)</h2>
              <div className="max-h-72 overflow-auto font-mono text-xs">
                {r.ultimos.length === 0 ? (
                  <p className="text-slate-500">—</p>
                ) : (
                  r.ultimos
                    .slice()
                    .reverse()
                    .map((e, i) => (
                      <p key={i} className="whitespace-pre-wrap border-b border-slate-800/60 py-1 text-slate-400">
                        <span className="text-slate-600">{hhmm(e._rec ?? e.t ?? 0)}</span>{" "}
                        <span className="text-orange-300">{e.e}</span> {JSON.stringify(e)}
                      </p>
                    ))
                )}
              </div>
            </section>

            <footer className="mt-10 text-center text-xs text-slate-600">
              Ronda 8 · Local ⇄ Producción (D1) — el juego no cambia: receptor, worker y panel son herramientas del ecosistema.
            </footer>
          </>
        )}
      </div>
    </main>
  );
}
