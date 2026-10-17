import TvLiveBanner from "./TvLiveBanner";

export default function Descargas() {
  const files = [
    {
      emoji: "☁️",
      nombre: "Juego + CRAZY TV — V3.2.0-ORB1 (paquete Cloudflare)",
      detalle:
        "La web estática pura, lista para arrastrar a Cloudflare Pages sin wrangler: sin TypeScript ni package.json (por eso lo acepta la subida directa). Juego con la ESTACIÓN ORBITAL vestida con el arte del dueño (sala, ASTRO, mapa, normas y MUROS ORBITALES tipo arkanoid), PRECISIÓN CCD en el contacto, saque VR realista, hall como hub + tv.html + los 5 campeonatos. El relay de TV va aparte: sácalo del paquete COMPLETO o del mini-zip para Railway/Render.",
      tamano: "113,7 MB · ZIP · Cloudflare Pages",
      href: "/descargas/crazypp-v320-orb1-CLOUDFLARE.zip",
      ver: null,
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
    },
    {
      emoji: "🎯",
      nombre: "Juego + CRAZY TV — V3.2.0-ORB1 (paquete completo)",
      detalle:
        "La V3.2.0-ORB1 íntegra: DECORADO REAL DE LA ESTACIÓN ORBITAL (los 6 planos de la sala con el arte del dueño, patrón vagón del Oeste) · el rival ASTRO con sus 12 poses (convención clown: focused en duelo, crazy con el superpoder, defeated al caer) · MUROS ORBITALES en las etapas 2 y 4: el arkanoid de La Locura con pistola láser pistol.glb en la variante 2 · mapa nuevo del dueño con nodos re-medidos · cartel de normas con la plantilla del artista (normas_astro.png) · cartel de superpoder con la etiqueta de la casa (superpower.png) + miniatura · recortables reales por el suelo · y TODO lo anterior: PRECISIÓN CCD SDF en el contacto de la pala (v3.1.2-CCD1), saque VR realista, gracia del saque, bote honesto, prompt B, hall del anfitrión, física viva y palas con carácter. Incluye tv.html, el relay Node (live-service), la guía de despliegue, los 5 campeonatos y los extras Next.js. OJO: lleva extras con TypeScript — para la subida directa de Cloudflare Pages usa el paquete Cloudflare.",
      tamano: "113,7 MB · ZIP · completo",
      href: "/descargas/crazypp-v320-orb1-COMPLETO.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "🪶",
      nombre: "V3.2.0-ORB1 — versión ligera (sin campeonatos)",
      detalle:
        "El mismo paquete para subir rápido a Netlify Drop: juego con la precisión CCD del contacto, saque VR realista, hall como hub, física viva y palas con carácter + tv.html + relay + guía. El juego funciona igual; la carpeta championships/ queda preparada para copiar del paquete completo (ahí vive el campeonato de la Estación Orbital con su decorado real). Tampoco vale para Cloudflare directo (lleva TypeScript).",
      tamano: "11,5 MB · ZIP · Netlify",
      href: "/descargas/crazypp-v320-orb1-ligera.zip",
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
      tamano: "12 KB · ZIP · solo live-service",
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
            <strong className="text-amber-300">V3.2.0-ORB1</strong>: la{" "}
            <strong className="text-slate-200">ESTACIÓN ORBITAL</strong> estrena
            su <strong className="text-slate-200">DECORADO REAL</strong> (el
            arte del dueño en los 6 planos de la sala, el rival ASTRO con sus
            12 poses, el mapa nuevo y los recortables del suelo), sus pruebas
            2 y 4 son ya{" "}
            <strong className="text-slate-200">MUROS ORBITALES</strong> (el
            arkanoid de La Locura con pistola láser) y el cartel de superpoder
            luce la etiqueta de la casa. Y bajo todo ello sigue la{" "}
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
          Crazy Ping Pong V3.2.0-ORB1 · WebXR · Decorado orbital real · Muros
          arkanoid · Precisión CCD · CRAZY TV · Meta Quest 3
        </footer>
      </div>
    </main>
  );
}
