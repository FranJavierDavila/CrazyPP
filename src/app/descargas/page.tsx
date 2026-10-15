import TvLiveBanner from "./TvLiveBanner";

export default function Descargas() {
  const files = [
    {
      emoji: "📺",
      nombre: "Juego + CRAZY TV — V3.0.4-EXP·TV1 (paquete completo)",
      detalle:
        "Tu V3.0.3 intacta más la rama experimental de TV en vivo: la Quest emite sus partidas como canales y cualquiera las mira desde el móvil sin visor. Incluye tv.html, el relay Node (live-service), guía de despliegue y los 5 campeonatos.",
      tamano: "103 MB · ZIP · experimental",
      href: "/descargas/crazypp-v304-exp-tv1-COMPLETO.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "🪶",
      nombre: "V3.0.4-EXP·TV1 — versión ligera (sin campeonatos)",
      detalle:
        "El mismo paquete para subir rápido a Netlify Drop y probar la TV: juego + tv.html + relay + guía. El juego funciona igual; la carpeta championships/ queda preparada para copiar del paquete completo.",
      tamano: "7,8 MB · ZIP · experimental",
      href: "/descargas/crazypp-v304-exp-tv1-ligera.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "📄",
      nombre: "Guía de campeonatos (PDF)",
      detalle:
        "Documento maquetado de 14 páginas, paso a paso y sin tecnicismos: cómo se crea un campeonato, dónde se prueba y desde dónde se juega al juego final.",
      tamano: "1,0 MB · 14 páginas",
      href: "/descargas/guia-campeonatos-crazy-pingpong.pdf",
      ver: "/descargas/guia-campeonatos-crazy-pingpong.pdf",
      color: "from-orange-500/20 to-transparent",
      borde: "border-orange-500/40",
      boton: "bg-orange-500 hover:bg-orange-400",
    },
    {
      emoji: "🌐",
      nombre: "Guía de campeonatos (HTML)",
      detalle:
        "La misma guía en una página web autónoma (fuentes incrustadas). Se abre en cualquier navegador, incluso sin internet.",
      tamano: "1,4 MB · un solo archivo",
      href: "/descargas/guia-campeonatos-crazy-pingpong.html",
      ver: "/descargas/guia-campeonatos-crazy-pingpong.html",
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
    },
    {
      emoji: "🏓",
      nombre: "Juego final — Crazy Ping Pong V2.124",
      detalle:
        "La versión definitiva del juego (build V2.124) lista para arrastrar a Netlify Drop y abrir en el Meta Quest Browser de la Quest 3.",
      tamano: "5,3 MB · ZIP",
      href: "/descargas/pingpong-quest3-v2.zip",
      ver: null,
      color: "from-emerald-500/20 to-transparent",
      borde: "border-emerald-500/40",
      boton: "bg-emerald-500 hover:bg-emerald-400",
    },
    {
      emoji: "🛠️",
      nombre: "Editor de campeonatos — «el Taller»",
      detalle:
        "Asistente de 7 fases para crear campeonatos: ficha, rivales, superpoderes, materiales, pruebas, sala y montaje. Genera los paquetes de pruebas y definitivos.",
      tamano: "27 KB · ZIP",
      href: "/descargas/editor-campeonatos.zip",
      ver: null,
      color: "from-violet-500/20 to-transparent",
      borde: "border-violet-500/40",
      boton: "bg-violet-500 hover:bg-violet-400",
    },
    {
      emoji: "📋",
      nombre: "README del proyecto (V2.124)",
      detalle:
        "Ficha técnica completa: historial de versiones, controles, despliegue y la tabla de descargas con el viaje Taller → Laboratorio → Estadio.",
      tamano: "41 KB · Markdown",
      href: "/descargas/README.md",
      ver: null,
      color: "from-slate-500/20 to-transparent",
      borde: "border-slate-500/40",
      boton: "bg-slate-500 hover:bg-slate-400",
    },
  ];

  return (
    <main className="min-h-screen bg-[#0B1526] text-slate-100">
      <div className="mx-auto max-w-3xl px-5 py-12">
        {/* Cabecera */}
        <header className="text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-orange-400">
            Crazy Ping Pong · Meta Quest 3
          </p>
          <h1 className="mt-3 text-4xl font-extrabold leading-tight sm:text-5xl">
            Centro de{" "}
            <span className="bg-gradient-to-r from-orange-400 to-amber-300 bg-clip-text text-transparent">
              descargas
            </span>
          </h1>
          <p className="mx-auto mt-4 max-w-xl text-slate-400">
            Todo el proyecto: la versión estable <strong className="text-slate-200">V2.124</strong> (guía, juego y
            editor) y el paquete experimental <strong className="text-rose-300">V3.0.4-EXP·TV1</strong> con CRAZY TV,
            la TV en vivo de tus partidas. Pulsa un botón y listo.
          </p>
        </header>

        {/* CRAZY TV · emisiones en vivo */}
        <TvLiveBanner />

        {/* Tarjetas de descarga */}
        <section className="mt-10 space-y-4">
          {files.map((f) => (
            <article
              key={f.href}
              className={`rounded-2xl border ${f.borde} bg-gradient-to-r ${f.color} bg-[#101E33] p-5 transition hover:-translate-y-0.5 hover:shadow-lg hover:shadow-black/40`}
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-[#0B1526] text-3xl">
                  {f.emoji}
                </div>
                <div className="min-w-0 flex-1">
                  <h2 className="text-lg font-bold leading-snug">{f.nombre}</h2>
                  <p className="mt-1 text-sm leading-relaxed text-slate-400">
                    {f.detalle}
                  </p>
                  <p className="mt-2 text-xs font-medium uppercase tracking-wider text-slate-500">
                    {f.tamano}
                  </p>
                </div>
                <div className="flex shrink-0 flex-col gap-2 sm:w-44">
                  <a
                    href={f.href}
                    download
                    className={`rounded-xl ${f.boton} px-4 py-2.5 text-center text-sm font-bold text-[#0B1526] transition`}
                  >
                    ⬇ Descargar
                  </a>
                  {f.ver && (
                    <a
                      href={f.ver}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-xl border border-slate-600 px-4 py-2 text-center text-xs font-semibold text-slate-300 transition hover:border-slate-400 hover:text-white"
                    >
                      Ver en pestaña nueva
                    </a>
                  )}
                </div>
              </div>
            </article>
          ))}
        </section>

        {/* Cómo se usa */}
        <section className="mt-12 rounded-2xl border border-slate-700/60 bg-[#101E33] p-6">
          <h2 className="text-center text-xl font-bold">
            El viaje en 3 paradas
          </h2>
          <ol className="mt-5 grid gap-4 sm:grid-cols-3">
            {[
              {
                n: "1",
                t: "Taller",
                d: "Abre el editor de campeonatos y crea tu campeonato con el asistente de 7 fases. Descarga el paquete que genera.",
              },
              {
                n: "2",
                t: "Laboratorio",
                d: "Arrastra el paquete de pruebas a Netlify Drop y ábrelo en la Quest 3 con la lista de comprobación de la guía.",
              },
              {
                n: "3",
                t: "Estadio",
                d: "Cuando todo pase la revisión, sube el paquete definitivo y juega al campeonato desde el navegador de la Quest.",
              },
            ].map((p) => (
              <li
                key={p.n}
                className="rounded-xl border border-slate-700/50 bg-[#0B1526] p-4"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-orange-500 font-bold text-[#0B1526]">
                  {p.n}
                </span>
                <h3 className="mt-3 font-bold">{p.t}</h3>
                <p className="mt-1 text-sm leading-relaxed text-slate-400">
                  {p.d}
                </p>
              </li>
            ))}
          </ol>
          <p className="mt-5 text-center text-sm text-slate-500">
            Dudas técnicas o pasos detallados: mira la{" "}
            <strong className="text-slate-300">guía de campeonatos (PDF)</strong>
            , escrita para quien nunca ha visto el desarrollo.
          </p>
        </section>

        <footer className="mt-10 text-center text-xs text-slate-600">
          Crazy Ping Pong V2.124 · WebXR · Netlify Drop · Meta Quest 3
        </footer>
      </div>
    </main>
  );
}
