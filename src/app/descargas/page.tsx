import TvLiveBanner from "./TvLiveBanner";

export default function Descargas() {
  const files = [
    {
      emoji: "☁️",
      nombre: "Juego + CRAZY TV — V3.5.0-ESC1 (paquete Cloudflare)",
      detalle:
        "La web estática pura, lista para arrastrar a Cloudflare Pages sin wrangler: sin TypeScript ni package.json (por eso lo acepta la subida directa). Juego con la etapa 4 NUEVA — ESCUDO DE PALA · DEFENSA DEL CASCO (devuelve orbes de plasma con la pala-escudo contra drones piratas, el Centinela y la nave abordadora) —, el REACTOR DE IMPULSO ahora en la etapa 2 (cubos cuánticos, pistola láser, dianas y perturbaciones), el ASTRO bien colocado en la sala, PRECISIÓN CCD, saque VR realista, hall como hub + tv.html + los 5 campeonatos. El relay de TV va aparte: sácalo del paquete COMPLETO o del mini-zip para Railway/Render.",
      tamano: "113,7 MB · ZIP · Cloudflare Pages",
      href: "/descargas/crazypp-v350-esc1-CLOUDFLARE.zip",
      ver: null,
      color: "from-sky-500/20 to-transparent",
      borde: "border-sky-500/40",
      boton: "bg-sky-500 hover:bg-sky-400",
    },
    {
      emoji: "🧊",
      nombre: "Juego + CRAZY TV — V3.5.0-ESC1 (paquete completo)",
      detalle:
        "La V3.5.0-ESC1 íntegra: ETAPA 4 NUEVA — ESCUDO DE PALA · DEFENSA DEL CASCO — la pala es un escudo manual: devuelve los ORBES DE PLASMA (estándar, pesado, inestable y rotor) que disparan los drones piratas; el GOLPE LIMPIO (centro de la hoja + rápido) carga la SOBRECARGA y al 100 % lanza un ORBE PERFORANTE; 3 fases: drones artilleros, el CENTINELA de rally (5 rebotes exponen su núcleo) y la NAVE ABORDADORA con 3 cañones; la INTEGRIDAD DEL CASCO (100, +30 por interludio) manda y la BARRERA trasera recibe los impactos con onda incluida · ASTRO RECOLOCADO — el rival de la ESTACIÓN ORBITAL se coloca como los demás rivales de la casa (convención de duelos: junto a la esquina lejana derecha de la mesa, en espacio abierto y a la misma profundidad que CLOWN y WIZARD) y ya no se lee dentro de la pared frontal · ETAPA 4 NUEVA — REACTOR DE IMPULSO — sala propia de 6 imágenes del dueño SIN mesa: la BASE FLOTANTE repone la pelota, el núcleo alterna ESTABLE (azul) e INESTABLE (rojo con alarma) y expulsa CUBOS CUÁNTICOS en 3 oleadas de 3, 5 y 7 con 2 minutos por oleada; los destruyes con la bola y con la PISTOLA LÁSER de la mano libre aciertas las DIANAS cuánticas (1 s visibles / 1 s de espera) que desatan PERTURBACIONES: Gravedad 0, Atractor (¡un golpe los destruye todos!) y Supergravedad, con cambio automático cada 30 s; pantalla suspendida del techo con oleada, tiempo, cubos y estado; al perder, el ASTRO se ríe frente a ti · el REACTOR DE ENERGÍA INESTABLE sigue en la etapa 2 · ESTACIÓN ORBITAL afinada · PRECISIÓN CCD SDF en el contacto, saque VR realista, gracia del saque, bote honesto, prompt B, hall del anfitrión, física viva y palas con carácter. Incluye tv.html, el relay Node (live-service), la guía de despliegue, los 5 campeonatos y los extras Next.js. OJO: lleva extras con TypeScript — para la subida directa de Cloudflare Pages usa el paquete Cloudflare.",
      tamano: "113,7 MB · ZIP · completo",
      href: "/descargas/crazypp-v350-esc1-COMPLETO.zip",
      ver: null,
      color: "from-rose-500/20 to-transparent",
      borde: "border-rose-500/40",
      boton: "bg-rose-500 hover:bg-rose-400",
    },
    {
      emoji: "🪶",
      nombre: "V3.5.0-ESC1 — versión ligera (sin campeonatos)",
      detalle:
        "El mismo paquete para subir rápido a Netlify Drop: juego con el Escudo de pala (etapa 4) y el Reactor de impulso (ahora etapa 2), el ASTRO bien colocado en la sala, la precisión CCD del contacto, saque VR realista, hall como hub, física viva y palas con carácter + tv.html + relay + guía. El juego funciona igual; la carpeta championships/ queda preparada para copiar del paquete completo (ahí vive el campeonato de la Estación Orbital con sus dos reactores). Tampoco vale para Cloudflare directo (lleva TypeScript).",
      tamano: "11,5 MB · ZIP · Netlify",
      href: "/descargas/crazypp-v350-esc1-ligera.zip",
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
            <strong className="text-amber-300">V3.5.0-ESC1</strong>: la etapa 4{" "}
            estrena el{" "}
            <strong className="text-slate-200">ESCUDO DE PALA · DEFENSA DEL CASCO</strong>{" "}
            — la pala se convierte en escudo manual: devuelve los{" "}
            <strong className="text-slate-200">orbes de plasma</strong> de los
            drones piratas, carga la <strong className="text-slate-200">Sobrecarga</strong>{" "}
            con golpes limpios hasta lanzar un orbe perforante, resiste el{" "}
            <strong className="text-slate-200">rally del Centinela</strong> y
            tumba los tres cañones de la{" "}
            <strong className="text-slate-200">nave abordadora</strong> mientras
            la integridad del casco aguanta. Y el{" "}
            <strong className="text-slate-200">Reactor de impulso</strong> sube
            a la etapa 2 como pidió el dueño: cubos cuánticos, pistola láser,
            dianas y perturbaciones. Bajo todo ello: el ASTRO bien colocado, la{" "}
            <strong className="text-slate-200">PRECISIÓN CCD</strong>, el saque
            VR realista, el hall como hub (ya sin arrastres al volver), la
            física viva y las palas con carácter — también para zurdos en el
            entrenamiento. Pulsa un botón y listo.
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
          Crazy Ping Pong V3.5.0-ESC1 · WebXR · Escudo de pala · Reactor de
          impulso · Estación Orbital · Precisión CCD · CRAZY TV · Meta Quest 3
        </footer>
      </div>
    </main>
  );
}
