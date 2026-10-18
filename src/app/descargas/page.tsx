import TvLiveBanner from "./TvLiveBanner";

export default function Descargas() {
  const files = [
    {
      emoji: "☁️",
      nombre: "Juego + CRAZY TV — V3.3.0-NUC1 (paquete Cloudflare)",
      detalle:
        "La web estática pura, lista para arrastrar a Cloudflare Pages sin wrangler: sin TypeScript ni package.json (por eso lo acepta la subida directa). Juego con el REACTOR DE ENERGÍA INESTABLE estrenando la etapa 2 (núcleo de gravedad con rotación caótica, esferas de plasma y compuertas de energía), la ESTACIÓN ORBITAL afinada, PRECISIÓN CCD en el contacto, saque VR realista, hall como hub + tv.html + los 5 campeonatos. El relay de TV va aparte: sácalo del paquete COMPLETO o del mini-zip para Railway/Render.",
      tamano: "113,7 MB · ZIP · Cloudflare Pages",
      href: "/descargas/crazypp-v330-nuc1-CLOUDFLARE.zip",
      ver: null,
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
    },
    {
      emoji: "🎯",
      nombre: "Juego + CRAZY TV — V3.3.0-NUC1 (paquete completo)",
      detalle:
        "La V3.3.0-NUC1 íntegra: ETAPA 2 NUEVA — REACTOR DE ENERGÍA INESTABLE — el NÚCLEO DE GRAVEDAD (arte GLB del dueño) gira de forma caótica tras la mesa y lanza ESFERAS DE PLASMA que debes golpear con la pala para meterlas en las COMPUERTAS de energía: primero una compuerta GRANDE, luego pequeñas y móviles; cada acierto estabiliza el reactor, cada fallo dispara alarmas, vibraciones y CAMBIOS DE GRAVEDAD, y el ASTRO se burla al fallar y se sorprende con tus rachas · el ARKANOID II con pistola láser sigue en la etapa 4 · ESTACIÓN ORBITAL afinada (ASTRO en su sitio, mapa con tapas, SuperPower!! a la altura de la red, expresiones y poderes sobre la mesa) · PRECISIÓN CCD SDF en el contacto, saque VR realista, gracia del saque, bote honesto, prompt B, hall del anfitrión, física viva y palas con carácter. Incluye tv.html, el relay Node (live-service), la guía de despliegue, los 5 campeonatos y los extras Next.js. OJO: lleva extras con TypeScript — para la subida directa de Cloudflare Pages usa el paquete Cloudflare.",
      tamano: "113,7 MB · ZIP · completo",
      href: "/descargas/crazypp-v330-nuc1-COMPLETO.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "🪶",
      nombre: "V3.3.0-NUC1 — versión ligera (sin campeonatos)",
      detalle:
        "El mismo paquete para subir rápido a Netlify Drop: juego con el Reactor de energía inestable, la precisión CCD del contacto, saque VR realista, hall como hub, física viva y palas con carácter + tv.html + relay + guía. El juego funciona igual; la carpeta championships/ queda preparada para copiar del paquete completo (ahí vive el campeonato de la Estación Orbital). Tampoco vale para Cloudflare directo (lleva TypeScript).",
      tamano: "11,5 MB · ZIP · Netlify",
      href: "/descargas/crazypp-v330-nuc1-ligera.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "📡",
      nombre: "Relay TV en solitario — para GitHub / Railway (mini)",
      detalle:
        "Solo el live-service (12 KB): los 4 ficheros que van a tu repo de GitHub para Railway. Descomprime y arrastra el CONTENIDO de live-service/ a la raíz del repo. Para el canal DEMO: npm install → set RELAY_URL=https://tu-relay.up.railway.app → npm run demo.",
      tamano: "6 KB · ZIP · solo live-service",
      href: "/descargas/crazypp-live-service-SOLO.zip",
      ver: null,
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
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
            El paquete actual es la{" "}
            <strong className="text-amber-300">V3.3.0-NUC1</strong>: la etapa 2
            de la <strong className="text-slate-200">ESTACIÓN ORBITAL</strong>{" "}
            estrena el{" "}
            <strong className="text-slate-200">REACTOR DE ENERGÍA INESTABLE</strong>
            : el núcleo de gravedad gira de forma caótica y lanza esferas de
            plasma que devuelves con la pala a las{" "}
            <strong className="text-slate-200">compuertas</strong> de energía;
            cada acierto estabiliza el reactor y cada fallo sacude la nave con
            alarmas y cambios de gravedad, mientras el ASTRO se burla o se
            sorprende. Y bajo todo ello siguen la{" "}
            <strong className="text-slate-200">PRECISIÓN CCD</strong> en el
            contacto de la pala, el saque VR realista, el hall como hub, la
            física viva y las palas con carácter. Pulsa un botón y listo.
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
                </div>
              </div>
            </article>
          ))}
        </section>

        {/* Cómo se usa */}
        <section className="mt-12 rounded-2xl border border-slate-700/60 bg-[#101E33] p-6">
          <h2 className="text-center text-xl font-bold">
            Cómo usar el paquete (3 paradas)
          </h2>
          <ol className="mt-5 grid gap-4 sm:grid-cols-3">
            {[
              {
                n: "1",
                t: "Sube la web",
                d: "Arrastra el ZIP descomprimido a Cloudflare Pages o Netlify Drop: index.html es el juego y tv.html la TV. Para Cloudflare usa el paquete Cloudflare; para Netlify, el ligero va más rápido.",
              },
              {
                n: "2",
                t: "Enciende la antena",
                d: "En un PC o servidor con Node: cd live-service && npm install && node server.mjs. Sin Quest puedes probar con node tools/mock_host.mjs (canal DEMO).",
              },
              {
                n: "3",
                t: "Juega y emite",
                d: "Abre el juego con ?relay=http://IP:3004 y arranca una partida: se publica sola. Los espectadores entran en tv.html con el mismo ?relay=.",
              },
            ].map((p) => (
              <li
                key={p.n}
                className="rounded-xl border border-slate-700/50 bg-[#0B1526] p-4"
              >
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-rose-500 font-bold text-[#0B1526]">
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
            Pasos detallados, HTTPS y solución de problemas: mira el{" "}
            <strong className="text-slate-300">LEEME-DESPLIEGUE.txt</strong>{" "}
            que viene dentro de cualquiera de los paquetes.
          </p>
        </section>

        <footer className="mt-10 text-center text-xs text-slate-600">
          Crazy Ping Pong V3.3.0-NUC1 · WebXR · Reactor de energía inestable ·
          Estación Orbital · Precisión CCD · CRAZY TV · Meta Quest 3
        </footer>
      </div>
    </main>
  );
}
