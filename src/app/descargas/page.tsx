import TvLiveBanner from "./TvLiveBanner";

export default function Descargas() {
  const files = [
    {
      emoji: "☁️",
      nombre: "Juego + CRAZY TV — V3.6.34-SDK6 (paquete Cloudflare)",
      detalle:
        "La web estática pura, lista para arrastrar a Cloudflare Pages sin wrangler: sin TypeScript ni package.json (por eso lo acepta la subida directa). Juego con el SDK v1.x CERRADO (FASE 7: el STANDEE del rival en createRival y los tableros de etapa en createCartel viven en el champ_sdk v1.4.0 — ningún campeonato conserva ya decodeAudioData propio), el CARTEL DE SUPERPODER unificado en createPowerSign (FASE 6) y la MÚSICA unificada en createMusic (FASE 5), con el SDK DE CAMPEONATOS adoptado por los 5 campeonatos (FASE 4, kernel único: SFX, congelado, puente), con los SUPERPODERES REDEFINIDOS (aviso con la partida congelada, meteoritos en 3D, rayo tractor con dron que atrapa la bola, gravedad cero que hace rebotar la bola entre partículas), la voz del ASTRO (risa y enfado), el REACTOR DE IMPULSO en la etapa 2 (dianas visibles 2 s y la pelota que siempre vuelve a la base), el ESCUDO DE PALA en la etapa 4, PRECISIÓN CCD, saque VR realista, hall como hub + tv.html + los 5 campeonatos. El relay de TV va aparte: sácalo del paquete COMPLETO o del mini-zip para Railway/Render.",
      tamano: "125,2 MB · ZIP · Cloudflare Pages",
      href: "/descargas/crazypp-v3634-sdk6-CLOUDFLARE.zip",
      ver: null,
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
    },
    {
      emoji: "🧊",
      nombre: "Juego + CRAZY TV — V3.6.34-SDK6 (paquete completo)",
      detalle:
        "La V3.6.34-SDK6 íntegra: la FASE 8 repara la TELEMETRÍA anónima (el lote __PP_TELE viaja como array directo — el receptor de producción rechazaba el wrapper con 400 y los lotes se perdían en silencio desde v2.50 — y el endpoint se enruta por host: desarrollo → receptor local con panel /telemetria; producción → Worker; sin PII, con opt-out) · la FASE 7 CIERRA el SDK v1.x (champ_sdk v1.4.0) — createRival unifica el STANDEE del rival (el ASTRO orbital con su motor «perezoso» y ZETA-7 de Valle Neón con el suyo de «precarga», que además estrena FIX: carga el arte real rival_kraken.png y abandona la silueta gris que pintaba desde su v1) y createCartel unifica los tableros de etapa (la fontanería canvas→textura→plano; el ARTE sigue siendo de cada módulo) — y la música de la Estación Orbital (el ÚLTIMO decodeAudioData propio que quedaba) pasa a createMusic · antes, createPowerSign (champ_sdk v1.3.0) unificó el CARTEL DE SUPERPODER de los 4 campeonatos con duelos — la FASE 6 bajó al SDK el tablón «¡Super Power!!» con sus DOS coreografías exactas (la clásica del Oeste/Mago y la v2.40 de La Locura con su halo que respira) — · la FASE 5 (createMusic v1.2.0) unificó la MÚSICA en bucle (BSO del saloon, vagón y WAV de Valle Neón) con conducta idéntica · sobre la FASE 4, en la que el SDK DE CAMPEONATOS ya lo usan LOS 5 (SFX, congelados y puente en el kernel); adiós del todo a la familia de bugs copiados entre módulos · SUPERPODERES REDEFINIDOS por el dueño — el aviso «Super Power!!» CONGELA la partida de verdad (IA, física, saque y árbitro) hasta que desaparece, como siempre se presupuso · los METEORITOS son pequeñas ROCAS EN 3D procedurales (basalto con vetas de óxido, calor de entrada y tumbling) que estallan al bloquear la bola · el RAYO TRACTOR sale de un mini DRON posado encima del haz y la bola que lo cruza queda ATRAPADA flotando dentro del rayo hasta que desaparece y cae VERTICALMENTE · la GRAVEDAD CERO atrae la bola y la hace rebotar ENTRE las partículas blancas de manera aleatoria hasta que desaparecen y la dejan caer · AUDIOS del ASTRO (mp3 del dueño): risa_astro.mp3 con la pose de risas y enfado_astro.mp3 cuando pierde un punto · el REACTOR DE IMPULSO (etapa 2) conserva sus correcciones: la diana cuántica se ve 2 s (antes 1 s) y la pelota SIEMPRE vuelve a botar sobre la base flotante · más el ESCUDO DE PALA en la etapa 4 (orbes de plasma, drones piratas, Centinela y nave abordadora) · PRECISIÓN CCD SDF, saque VR realista, gracia del saque, bote honesto, prompt B, hall del anfitrión, física viva y palas con carácter. Incluye tv.html, el relay Node (live-service), la guía de despliegue, los 5 campeonatos y los extras Next.js. OJO: lleva extras con TypeScript — para la subida directa de Cloudflare Pages usa el paquete Cloudflare.",
      tamano: "125,2 MB · ZIP · completo",
      href: "/descargas/crazypp-v3634-sdk6-COMPLETO.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "🪶",
      nombre: "V3.6.34-SDK6 — versión ligera (sin campeonatos)",
      detalle:
        "El mismo paquete para subir rápido a Netlify Drop: juego con el SDK v1.x cerrado (FASE 7: createRival + createCartel + cero decodeAudioData fuera del SDK), el tablón de superpoder unificado en createPowerSign (FASE 6), la música unificada en createMusic (FASE 5) y el SDK de campeonatos ya adoptado por los 5 (FASE 4), los superpoderes redefinidos, la voz del ASTRO, el Reactor de impulso (etapa 2), el Escudo de pala (etapa 4), la precisión CCD del contacto, saque VR realista, hall como hub, física viva y palas con carácter + tv.html + relay + guía. El juego funciona igual; la carpeta championships/ (con el SDK de campeonatos dentro) queda preparada para copiar del paquete completo (ahí viven la Estación Orbital con sus dos reactores y los 5 campeonatos). Tampoco vale para Cloudflare directo (lleva TypeScript).",
      tamano: "11,5 MB · ZIP · Netlify",
      href: "/descargas/crazypp-v3634-sdk6-ligera.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "📡",
      nombre: "Relay TV en solitario — para GitHub / Railway (mini)",
      detalle:
        "Solo el live-service (6 KB): los 4 ficheros que van a tu repo de GitHub para Railway. Descomprime y arrastra el CONTENIDO de live-service/ a la raíz del repo. Para el canal DEMO: npm install → set RELAY_URL=https://tu-relay.up.railway.app → npm run demo.",
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
            <strong className="text-amber-300">V3.6.34-SDK6</strong>: la{" "}
            <strong className="text-slate-200">FASE 8</strong> repara el{" "}
            <strong className="text-slate-200">flujo de la telemetría</strong>{" "}
            anónima — el lote de <strong className="text-slate-200">__PP_TELE</strong>{" "}
            ahora viaja como{" "}
            <strong className="text-slate-200">array directo</strong> (el
            receptor de producción rechazaba el wrapper anterior con 400 y los
            lotes se perdían en silencio desde v2.50) y el endpoint se{" "}
            <strong className="text-slate-200">enruta por host</strong>:
            desarrollo → receptor local con panel de lectura; producción →
            Worker. Sin PII y con opt-out, como siempre. La{" "}
            <strong className="text-slate-200">FASE 7</strong> CIERRA el SDK
            v1.x — el{" "}
            <strong className="text-slate-200">standee del rival</strong> vive
            en <strong className="text-slate-200">createRival</strong> (el
            ASTRO con su motor «perezoso» y ZETA-7 con el suyo de «precarga»
            + FIX: ya carga el arte real .png) y los{" "}
            <strong className="text-slate-200">tableros de etapa</strong> en{" "}
            <strong className="text-slate-200">createCartel</strong> (el champ_sdk v1.4.0): ningún campeonato conserva ya
            <strong className="text-slate-200"> decodeAudioData propio</strong> —
            un bug del kernel se arregla UNA vez y sirven los 5. La{" "}
            <strong className="text-slate-200">FASE 6</strong> estrenó{" "}
            <strong className="text-slate-200">createPowerSign</strong> — el
            tablón «¡Super Power!!» de los 4 campeonatos con duelos vive ahora
            en{" "}
            <strong className="text-slate-200">una sola fuente</strong> con sus DOS coreografías exactas: la clásica y
            la v2.40 con su halo que respira. La{" "}
            <strong className="text-slate-200">FASE 4</strong> puso el SDK en
            los 5 (el kernel que nació en la FASE 3 mueve SFX, congelados y
            puente: el fix del audio llegó a estar copiado 7 veces en el
            Oeste). Bajo todo ello siguen los{" "}
            <strong className="text-slate-200">superpoderes</strong> redefinidos
            a petición del dueño — el aviso{" "}
            <strong className="text-slate-200">congela la partida</strong>{" "}
            hasta desaparecer, los{" "}
            <strong className="text-slate-200">meteoritos</strong> son rocas en
            3D con vetas de óxido, el{" "}
            <strong className="text-slate-200">rayo tractor</strong> sale de un
            dron y atrapa la bola flotando dentro del rayo hasta soltarla en
            caída vertical, la{" "}
            <strong className="text-slate-200">gravedad cero</strong> hace
            rebotar la bola entre las partículas blancas y el{" "}
            <strong className="text-slate-200">ASTRO</strong> estrena voz:{" "}
            <strong className="text-slate-200">risa</strong> cuando se burla con
            la pose de risas y <strong className="text-slate-200">enfado</strong>{" "}
            cuando pierde un punto. En el{" "}
            <strong className="text-slate-200">Reactor de impulso</strong> la
            diana se ve 2 segundos y la pelota siempre vuelve a botar sobre la
            base. Pulsa un botón y listo.
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
          Crazy Ping Pong V3.6.34-SDK6 · WebXR · SDK v1.x cerrado ·
          createRival · createPowerSign · createMusic · Superpoderes redefinidos ·
          Escudo de pala · Estación Orbital · Precisión CCD · CRAZY TV · Meta
          Quest 3
        </footer>
      </div>
    </main>
  );
}
