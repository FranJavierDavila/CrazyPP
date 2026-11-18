# MEMORIA PERSISTENTE · CRAZY PING PONG (Quest 3)

> Archivo de memoria para sesiones futuras. LÉEME ANTES DE TRABAJAR si el
> usuario pide "enlace de descarga", "zip" o "copia de seguridad".

## 1. Entregable canónico

| Qué | Dónde |
|-----|-------|
| Build final (1 HTML autocontenido) | `/home/z/my-project/download/pingpong-quest3-v2/index.html` |
| ZIP para Netlify Drop | `/home/z/my-project/download/pingpong-quest3-v2.zip` |
| Copia servida (raíz del preview) | `/home/z/my-project/public/game.html` + `/home/z/my-project/public/pingpong-quest3-v2.zip` |
| Página de descarga del preview | ruta web `/descarga` (src/app/descarga/page.tsx) |
| README del paquete | `/home/z/my-project/download/README.md` |

- **Estado actual: v2.50** (index.html 9,42 MB · ZIP 13,8 MB · incluye
  pistol.glb del JUGADOR (opt. WebP 512, 230 KB) + viento.webp + reloj.webp +
  extra.webp + mapa.webp + tapa.webp + regalo.png + Superpoder_pistola.jpg +
  carteles victoria/derrota ES y victory/lost EN (del USUARIO, con alfa)
  embebidos; el ZIP lleva ADEMÁS assets/intro.mp4 (5,78 MB, vídeo del botón
  INTRO de la portada — único archivo externo).
  v2.50 añade (FASE 1 CERRADA con datos reales): `PP_KOFI_URL` =
  **https://ko-fi.com/escala3d** y `PP_TELEMETRY_ENDPOINT` =
  **https://crazypp.escala3dcorreoia.workers.dev/api/tele** (servidor del
  USUARIO en Cloudflare Workers; receptor listo en
  `download/worker-telemetria-crazypp.js`); VERSION interna 2.50.0;
  build `scripts/build_v250.py` (42 checks) · promo vertical
  `download/promo-vertical-v2.50.mp4` (33,4 s, 1080x1920, 9,2 MB).
  v2.49 añadió (FASE 1): TELEMETRÍA anónima `__PP_TELE` (cola localStorage +
  sendBeacon por lotes, opt-out en Opciones), CONFORO (vibración pp_hapt +
  consejos de 1ª sesión pp_seen_v1) y APOYO KO-FI (botón portada `#kofibtn`
  + Opciones VR); Opciones reorganizado en rejilla 2×2.
- **NUEVO: ZIP específico para Netlify Drop**: `download/netlify-drop-v2.50.zip`
  (index.html EN LA RAÍZ + assets/intro.mp4) — arrastrar tal cual a
  app.netlify.com/drop (o subir a tu hosting, p. ej. el Worker crazypp).
  v2.48 añade: COPA 3D del Campeonato (_buildTrophy/_revealTrophy, rig,
  (1.18,0,-1.05), giro+halo+pop, permanente para campeones) y RANKING con
  bloque de RÉCORDS reales (arc_rec_* ES/EN; 4 rondas recientes).
- **FUENTE EDITABLE CANÓNICA (05-oct-2026)**: `scripts/game_v242.js` (módulo
  completo con placeholders `__DATAURL0..9__` / `__BLOB7..44__`) +
  `v242_recovery/` (shell v2.42 + blobs.json) en el workspace CANÓNICO
  `/home/z/my-project`. Build: `python3 scripts/build_v248.py` (verify:
  `verify_v248.py`, 18 checks de comportamiento + regresiones v244-v247).
  El directorio
  `/tmp/my-project` de sesiones anteriores ya NO es necesario (todo
  recuperado y copiado aquí).
- **AVISO IMPORTANTE (05-oct-2026)**: el workspace /tmp/my-project de la
  sesión anterior quedó SINCRONIZADO AL REVÉS y las fuentes v2.37-v2.43 de
  game_part1/2/3, game_i18n y build_html se PERDIÓN — se reconstruyeron
  desde el backup v2.36 (download/crazy-pingpong-backup-v2.36-*.tar.gz) +
  game_arcade.js v2.43 (sobrevivió) + las suites verify (documentan el
  comportamiento). El workspace CANÓNICO es /home/z/my-project. Las suites
  v239-v243 pasan de nuevo sobre la reconstrucción.
- El servidor Next del workspace reescribe `/` → `/game.html` (build jugable).
- Pipeline de build: `python scripts/build_html.py` (embebe GLB pala+pistola +
  12 PNG→WebP del Clown + risas.mp3 + BSO ogg + SuperPower.png + regalo.png +
  Superpoder_pistola.jpg) → verificar con `python scripts/verify_v244.py` (+
  `verify_v243.py` + `verify_v242.py` + `verify_v241.py` + `verify_v240.py` +
  `verify_v239.py` + `verify_v238_stability.py`; verify_v238.py está
  OBSOLETA — testea la física antigua retirada en v2.42)
  → regenerar ZIP → copiar a `public/` → actualizar `/descarga` y README.

## 1q. v2.98 (09-oct-2026) — ASEDIO 3.0 + HAZ DE LUZ DEL SELECTOR

- El artista probó la v2.97 (gofile J12WvNJE) y pidió: haz de luz al apuntar
  a etapas superadas, mecánicas nuevas del desierto (dos palas, bombas cada
  2 s con giro natural y explosión en pared/suelo, forajido de pie/estático
  con el corazón en el pecho, dos revólveres de 1 disparo con asistente,
  decorado fijo, mesita de madera en vez de mesa, cielo con cúpula y
  montañas 360°, sin recortes, sin pájaros).
- ENTREGA: crazypp-v298.zip (40.468.986 B, md5 3df3e02687cb667b3ff12092f21e1f4d)
  → gofile **https://gofile.io/d/sch7Y072** (store4 EU, md5 servidor
  idéntico). Fuente editable: download/crazypp-v298-work (núcleo
  index.html 2.98.0 + _mods_src oeste v16). Build: scripts/v298/
  package_v298.py · verify_v298.py 47/47 TODO OK + regresión duelo.
- TÉCNICA CLAVE v2.98: gatillo POR MANO (serveTrigger(i) hasta el módulo),
  ball.ignoreTable en collideTable (convenio ignoreNet), _twoPaddles/
  _twoGunApply/_gunHandRemove/_gunRayHand/_gunLoaded en el ctrl del oeste,
  _tumbleHit (rodadura ω=v⊥/r) integrada con quaternion en fxStep,
  _boomAt = receta dinamita, asistente diana assistR 0.36 y corazón
  heartAssist 1.75, láser ×2 (slot por mano), cúpula r=30 + banda IA
  r=29.2 + anillo montañas r=26 + arena r=24, mesita 0.95×0.55 a
  tableTopY. BUG resuelto: los sprites de cactus NECESITAN depthWrite:false
  (el quad con alfa escribía depth y rechazaba la banda → cajas pálidas de
  la cúpula); banda renderOrder -2 y anillo -1 (cielo antes que sprites).
- AVISO: gofile ya NO deja descargar por API a invitados (error-notPremium).
  El sandbox se reinició al 3-oct esta mañana: /tmp/my-project salvó el
  proyecto. MANTENER ESTA COPIA EN /home/z/my-project.

## 1r. v2.99 (10-oct-2026) — ASEDIO 3.1: OLEADAS + FACHADAS QUE SE AGUJEREAN

- El artista no le gustó el pueblo procedural de v2.98 y rediseñó la
  mecánica: 3 EDIFICIOS INTERACTIVOS con SU arte (Fachada1.png delante,
  Interior1.png detrás, forajido ENTRE ambos), PUEBLO LEJANO de
  ambientación (pueblohorizonte.png a z=-21.5), bombas CADA 1 SEGUNDO,
  fachadas que se AGUJEREAN con rotura.png (transparencia real: se ve el
  interior), dianas SIEMPRE visibles delante de la fachada sobre las
  ZONAS VERDES de zonas1.jpg (3 barras: ático/entreplanta/baja -> 33
  zonas), forajido DE PIE en la calle con CORAZÓN en el pecho y SU
  revólver que APUNTA a tu cabeza y DISPARA A LOS 2 s (sangre en la
  cara) salvo disparo al corazón, OLEADAS de 2 min (3/4/5 forajidos)
  con carteles oleada1/2/3.png + oleada.mp3 (velocidad entrada 0,5 s,
  vaivén 4 s, salida 0,5 s; 5 s en pausa) y ALARMA a los 20 s.
- TÉCNICA CLAVE v2.99: alphaMap de fachada = lienzo blanco 512² que
  _perfora() agujerea estampando rotura_mascara (RGB negro + alfa) con
  source-over (el canal VERDE cae = transparencia; el rotura se convirtió
  en DOS piezas: máscara de boquete + chapas para el decal); zona con la
  fachada destruida PROHIBIDA (_zonaLibre vs b.holes); _aiCut() = PLANOS
  FIJOS orientados UNA vez (adiós sprites que bailan); _aiTexCut DEBE
  nacer del MISMO tamaño que la imagen final (cambiar image en un
  CanvasTexture a otro tamaño desborda la GL: glTexSubImage2D overflow).
- FIX DE RECORTE: el arte del artista trae el TABLERO DE AJEDREZ horneado
  (gris 193/blanco 255 opacos; 3,1% alfa real) -> relleno desde los
  BORDES con scipy.ndimage.label + defringe anti-franja-roja (el pueblo).
  Recorte real: 33%.
- ENTREGA: crazypp-v299.zip (41.569.105 B, md5 59e0c702d770e77f2c82d5e67b
  02e97c) -> gofile https://gofile.io/d/zPTcO7XZ (store5, md5 servidor
  idéntico). Fuente editable: download/crazypp-v299-work (núcleo 2.99.0 +
  _mods_src oeste v17). verify_v299.py 47/47 TODO OK.
- AVISO: el sandbox se ha reiniciado YA 3 veces al snapshot del 3-oct;
  el proyecto sobrevive en /tmp/my-project (worklog Task 40). COPIAR
  SIEMPRE crazypp-v299-work y scripts/v299 a /home/z/my-project antes de
  trabajar y MANTENER /tmp/my-project sincronizado al terminar.

## 1p. v2.51 (06-oct-2026) — MULTIJUGADOR REPARADO (auditoría + banco E2E)

- El usuario reportó: sesiones sin sincronizar, movimientos del rival mal,
  voz sin sincronizar, imposible sacar, bola caótica, marcas que no
  desaparecen. Auditoría + banco de 2 navegadores con PeerJS real.
- DOS BUGS CRÍTICOS en `NetLink` (scripts/game_v242.js):
  1) **ECO INFINITO**: `collectEvents` re-enviaba los eventos que
     `drainNetwork` había inyectado por red -> bucle a 20 Hz (55.386
     eventos/45 s medidos) -> puntos fantasma del árbitro, marcas eternas,
     audio spam. FIX: eventos de red con `remote:true` + `if (e.remote)
     continue;` en collectEvents.
  2) **FLAP DE PROPIEDAD**: `applySync` pisaba el claim del invitado tras
     su golpeo con el `ow` atrasado del anfitrión -> bola saltando entre
     simulaciones. FIX: `_lastHitSent` + ventana 600 ms en rallye.
- FIXES menores: handoff inmediato del 'h' (bola aplicada al instante),
  pala remota con lerp+slerp (f=1-exp(-16dt)), hits en estado muerto
  descartados, demo-saque bloqueada en online 2D, watchdog de unión 15 s.
- BANCO (`scripts/net_bench.py`): HTTPS local autofirmado + 2 Chromium
  headless (mic fake) + señalización 0.peerjs.com + bots que juegan puntos.
  v2.50 reproducía todo; **v2.51: 0 fallos** (voz OK, pala ~200 ms,
  50/50 eventos exactos, marcador espejado sincronizado, 3º rechazado,
  desconexión limpia). Lecciones: 2 navegadores (throttling de tabs),
  viewport 480x360 (SwiftShader 1 fps), THREE no global,
  computeShotVelocityReal exige spin, congelar con freezeT=999.
- REGRESIÓN: v249/v248/v247/v246/v245/v244/v244_regress/v240/v238 TODO OK
  + IA OK. v245-247 parcheadas para interceptar **/api/tele**: el Worker
  del usuario sigue SIN el receptor (POST 404, curl verificado 06-oct).
- ENTREGA: html 9,42 MB (md5 d69613de) · netlify-drop-v2.51.zip (md5
  c5467ad7) -> gofile **dFBaiBOm** · pingpong-quest3-v2.zip (md5 a4c6aa3c)
  -> gofile **YfhjL4pR** · public/ sincronizado.
- **PENDIENTE USUARIO**: subir v2.51 a su Worker (el online roto sigue
  publicado) + pegar worker-telemetria-crazypp.js + re-test con 2 Quest.

## 1o. v2.50 (06-oct-2026) — PROMO VERTICAL EN INGLÉS CON LOCUCIÓN (voz "jam")

- El usuario pidió "montar el video promo en inglés con voces". REDENCIÓN
  TTS: el fallo de las voces TTS era SOLO del español; en inglés funcionan.
  3 candidatos con el mismo guion de 8 frases: SDK **jam** (británica)
  8/8 · 34,7 s, SDK luodo 7/8 · 52,2 s (descartada: ritmo lento + 429),
  Piper en_US-lessac 8/8 · 25,3 s (seg8 ASR None, probable rate-limit).
- Verificación ASR ida-vuelta (`scripts/promo_vo_asr.py`): jam 7/8 fiel +
  1 parcial ("right in" → ASR "riding", probable artefacto del ASR; se
  intentó regenerar seg2 con frase más simple pero la cuota TTS quedó
  agotada con 429 persistente — se conservó el original).
- **ENTREGADO** `download/promo-vertical-en-v2.50.mp4` (40,3 s, 1080x1920,
  30 fps, 10,4 MB, H.264+AAC faststart): mismos 8 planos que el promo ES
  con textos cinéticos EN (PING PONG + ARKANOID + CLOWNS / REAL PHYSICS /
  48 BRICKS / LASER GUN / CHAMPIONSHIP OF MADNESS / LIFT THE TROPHY /
  BEAT YOUR RECORDS / tarjeta FREE·META QUEST 3 con las 2 URLs).
- SINCRONÍA voz-plano: duración de cada plano = 0,30 (lead) + VO + 0,50
  (cola) (+1,6 s en la tarjeta); VO a 1,07x (atempo, energía); BSO del
  juego con DUCKING por sidechaincompress (threshold 0.02, ratio 6) bajo
  la voz + loudnorm -14 LUFS. QA: 8 frames visuales OK + niveles OK
  (BSO -31,5 dB medio antes de la voz; VO -18,7 dB medio, pico -1,2 dB).
- Scripts: `scripts/promo_vo_en.py` (genera 3 candidatos),
  `scripts/promo_vo_asr.py` (verificación), `scripts/make_promo_en.py`
  (montaje; ojo: el render completo tarda >600 s — tras un timeout
  aparente VERIFICAR siempre los ficheros, el proceso sí termina).
- ENLACE público: gofile **HLD3uWo0** (MD5 9a228128c9da6adb8c95ca628a20a334
  verificado = local; subida directa a store-eu-par-6,
  scripts/upload_promo_en.py).
- Lección: para futuras locuciones en inglés usar jam (o Piper lessac);
  luodo demasiado lento; tener en cuenta la cuota TTS (429) y no
  generar los 24 WAV de golpe si solo hacen falta 8.

## 1n. v2.50 (06-oct-2026) — FASE 1 CERRADA: Ko-fi + telemetría reales + promo vertical

- El usuario dio su hosting (**https://crazypp.escala3dcorreoia.workers.dev/**,
  Cloudflare Workers) y su Ko-fi (**https://ko-fi.com/escala3d**).
- Fijados en el shell (`v242_recovery/extracted/index.html`):
  `window.PP_KOFI_URL='https://ko-fi.com/escala3d'` y
  `window.PP_TELEMETRY_ENDPOINT='https://crazypp.escala3dcorreoia.workers.dev/api/tele'`.
- `scripts/build_v250.py` (derivado de build_v249): 42 checks estáticos
  incluidos los 2 valores reales. `verify_v249.py` 25/25 TODO OK sobre la
  build (telemetría informa v2.50.0) + regresión verify_v248 TODO OK.
- `download/worker-telemetria-crazypp.js`: receptor completo para su Worker
  (POST /api/tele → console.log + KV opcional binding TELE; resto de rutas →
  env.ASSETS). Instrucciones caso A (editar worker con assets) y caso B
  (worker separado) en la cabecera.
- PROMO VERTICAL `download/promo-vertical-v2.50.mp4` (33,4 s, 1080x1920,
  30 fps, 9,2 MB, H.264+AAC faststart): 8 planos Ken Burns sobre capturas +
  clip intro.mp4 + tarjeta final (URLs del usuario). Música: la BSO ogg del
  propio juego (extraída del shell, segmento 18-51 s, loudnorm -14 LUFS).
  SIN LOCUCIÓN: las 7 voces TTS pronuncian mal el español (verificado con
  ASR: "física real" → "Gangka Rihah Li Tiuma"); estilo texto cinético.
  Scripts: `scripts/make_promo_v250.py` + `scripts/make_promo_fix05.py`
  (plano 5 re-hecho: captura-v247-mapa-tapas.png era NEGRA — usar
  captura-v247-mapa-avanzado.png).
- ENTREGA: ZIP completo → gofile **AJKfujjQ** · netlify-drop → gofile
  **tBFIzIWT** · promo → gofile **VqZe2Cnm** (MD5 de los tres verificados
  = local). README v2.50 + /descarga v2.50 (con SERVIDOR OFICIAL y link
  Ko-fi reales) + public/ sincronizado.

## 1m. v2.49 (06-oct-2026) — FASE 1: telemetría anónima + confort/onboarding + Ko-fi

- **TELEMETRÍA `__PP_TELE`** (game_v242.js): eventos boot / vr_start /
  vr_end (duración+FPS) / stage / champion / error / page_close; cola
  `pp_tele_q` (máx 60) + envío cada 10 eventos o 30 s con sendBeacon
  (**text/plain — Chromium BLOQUEA application/json en beacons**) o fetch
  no-cors keepalive; endpoint leído EN CADA envío de
  `window.PP_TELEMETRY_ENDPOINT` (vacío = no sale nada del dispositivo);
  opt-out `pp_tele` con interruptor en Opciones + aviso tele_hint;
  expuesta como `window.__PP_TELE` para pruebas. FPS con noteFrame()
  desde animate().
- **CONFORO**: `pp_hapt` (haptic() corta si hapticsOn=false) + `pp_tips_v1`
  / `pp_seen_v1` (3 consejos + despedida CONSEJO/TIP solo 1ª sesión, ceden
  cartel al árbitro) — interruptores btn_hapt/btn_tips en Opciones.
- **KO-FI**: shell parcheado (patch_shell_v249.py) con `#kofibtn` en el pie
  + bloque `<script>` config (PP_KOFI_URL + PP_TELEMETRY_ENDPOINT) + btn
  'kofi' en Opciones VR (window.open con fallback a mensaje).
- **Opciones 2×2**: amb/voz · music/hapt · trail/tips · sndtest/tele +
  kofi a lo ancho + tele_hint (cierre del panel en y=1247 < 1392 ✓).
- **Suites**: `verify_v249.py` NUEVO 25/25 TODO OK (incl. beacon end-to-end
  interceptado con Playwright route + defineProperty contra el shell).
  Regresiones v248/v247/v246/v245/v244/v244_regress/v240/v238_stability +
  IA 14/14 TODO OK. **verify_v241/v242/v243 OBSOLETAS** (fallan igual sobre
  la v2.48 pura — A/B verificado con las fuentes de /tmp/my-project).
- **Pipeline**: build_v249.py (40 checks) → ZIP 13,8 MB (MD5
  b7bac5179e244a0a558d53c1ff7b7eeb) → public/ → README v2.49 → /descarga
  v2.49 → netlify-drop-v2.49.zip (raíz) → gofile **pPcXLtUB** (MD5 ok).
- **PDF FASE 1**: `download/CRAZY-PING-PONG-Fase1-Plan-de-Lanzamiento.pdf`
  (9 págs, 194 KB, ruta Report + portada HTML Template 01 validada con
  cover_validate) + fuente `download/fase1_cover.html`. Contenido: hosting
  (Netlify Drop/itch), Ko-fi (textos ES/EN + niveles), telemetría (eventos
  + Worker Cloudflare), guion vídeo 30-45 s y checklist Fase 1.

## 1l. v2.48 (05-oct-2026) — COPA física del Campeonato + RANKING con récords reales

- **HALLAZGO**: la COPA 3D de la v2.44 (worklog: `_buildTrophy` + copa en
  (1.18, 0, -1.05)) NO existía en la fuente canónica — se perdió con la
  reconstrucción del workspace y las suites sólo comprobaban el ESTADO
  (`pp_arcade_trophy`). v2.48 la recupera.
- **COPA 3D** (`_buildTrophy`/`_revealTrophy` en ArcadeController):
  pedestal oscuro + remates ámbar + placa canvas «CAMPEÓN · CAMPEONATO DE
  LA LOCURA» + copa dorada (LatheGeometry, TorusGeometry asas, goldMat
  metálico con emisivo) + halo Sprite aditivo que respira. Animación en
  `body.onBeforeRender` (OJO: un Group NO recibe onBeforeRender, sólo las
  mallas renderizables — por eso no arrancaba en la 1ª iteración):
  giro 0.55 rad/s + halo 0.22..0.32 + pop de escala al revelarse.
  Anclada a `g.rig` en (1.18, 0, -1.05) rot.y -0.62. `G.visible =
  !!this.trophy` (campeón previo la ve desde el primer build); reveal con
  pop en `onMatchOver` etapa 4. NO se oculta en leave(): pieza permanente.
- **RANKING ampliado** (ArcadeRanking.refresh): bloque RÉCORDS con datos
  reales — `stats.data.bestRally`, `stats.data.bestStreak`,
  `g.survivalBest` (ppxr_surv_best) y logros `Object.keys(ach).length /
  ACHIEVEMENTS.length`; rondas recientes 6→4 (step 64) para hacer sitio;
  separadores y pie re-colocados (sep 446, sep pie 648, totales 688).
  i18n: `arc_rec_rally/arc_rec_streak/arc_rec_surv/arc_rec_ach` ES/EN.
  Con récords a cero queda SOLO «Logros: 0/{m}" (comportamiento esperado).
- Suites: `verify_v248.py` NUEVO 18/18 TODO OK (modo 2D + toDataURL —
  falsificar isPresenting MATA el bucle de render y las capturas salen
  negras: no hacerlo) + regresiones verify_v247/v246/v245/v244/
  v244_regress/v238_stability TODO OK + test_ai_returns 14/14 (100%).
  Capturas: captura-v248-{copa,ranking}.png.
- Pipeline: build_v248.py → ZIP 13,8 MB (MD5 5d110edef601aeff1fdf6ce39c5be6cf)
  → public/ → README v2.48 → /descarga v2.48 → gofile
  **https://gofile.io/d/4fyeveYH** (MD5 verificado).
- Git: tag `v2.47` (retro) + commit v2.48 + tag `v2.48`.

## 1k. v2.47 (05-oct-2026) — botón INTRO (assets/intro.mp4), mapa OFICIAL con tapas y muros ARK1 = ARK2

- **RECUPERACIÓN**: el sandbox de esta sesión venía del snapshot v2.31; el
  estado real (v2.46) sobrevivió en `/tmp/my-project` (y el ZIP en gofile).
  rsync /tmp/my-project → /home/z/my-project antes de trabajar.
- **PORTADA**: botón `#introbtn` en el pie + visor `#introov` con
  `<video src="assets/intro.mp4" muted playsinline>` (patch_shell_v247.py
  sobre la SHELL v242_recovery/extracted/index.html). SILENCIADO: en la
  portada sólo suena la música principal. Cierre con ✕/ESC/fin/VR
  (`window.__ppIntro.close`). Si falta el archivo, aviso en `#status`.
- **MAPA OFICIAL** (scripts/v247_arcademap.js): ArcadeMap SIN canvas — plano
  1.68 × 0.9157 m (arte 1380x752, `__PP_MAPA_URL` DATAURL10, opacity 0 hasta
  cargar) + 4 TAPAS (`__PP_TAPA_URL` DATAURL11, 0.353×0.365 m en los centros
  medidos por diff Mapa vs iniciomapa: (438,503.5) (690,262) (934,503)
  (1216,178); r120/145/120/145/120). Tapa del nodo N visible SOLO si
  stage < N; stage 5 (campeón) = sin tapas y sin anillo. Anillo dorado
  escalado n.r/120.
- **MUROS ARK1 = ARK2**: `ARK_CFG.sideZ0 = DIMS.tableCenterZ + 0.80`.
- **intro.mp4 NO embebido**: archivo en `download/pingpong-quest3-v2/assets/`
  (y `public/assets/`); el build lo copia.
- Suites: `verify_v247.py` NUEVO 47/47 TODO OK; verify_v244/v245/v246
  parcheadas (ARK1 −1.1→−0.8; "ARK2 sin póster" → exige póster viento, era
  obsoleto desde v2.45) TODO OK; v238_stability OK; test_ai_returns 12/14.
- Capturas captura-v247-{portada-intro,mapa-tapas,mapa-avanzado,arkanoid1}.png.
- Pipeline: build_v247.py → ZIP 13,8 MB (MD5 deb7ff1b96b528c9057512d40ff3417e)
  → public/ → README v2.47 → /descarga v2.47 → gofile
  **https://gofile.io/d/vRFxvkVO** (MD5 verificado).

## 1j. v2.46 (05-oct-2026) — muros +20 cm con colisión real, marcos finos, ladrillo negro del TIEMPO EXTRA y carteles EN del usuario

- **MUROS +20 cm**: ARK_CFG.sideZ0 = red+0.50 · ARK2_CFG.sideZ0 = red+0.80.
- **BUG CRÍTICO DE COLISIÓN ARREGLADO**: `_extraCollide`, `_crossed` y
  `_checkLost` leían ARK_CFG FIJO — en el ARKANOID 2 el cristal ampliado
  (red+60) NO colisionaba más allá de red+30 (el reporte "se ve ampliada
  pero no detecta colisión"). Ahora TODO usa `this.C` (config de variante).
- **MARCOS FINOS**: pilares del muro 0.06→0.022 y FUERA de los ladrillos
  (x=±(W/2+0.011)); marcos de cristal 0.05→0.022 centrados fuera del plano
  (x=±(sideX+0.013)); listón superior 0.016 alto × 0.04. Suite comprueba
  0 solapes marco↔ladrillo.
- **LADRILLO NEGRO DEL TIEMPO EXTRA (ARK2)**: `_timeUpdate/_timeSpawn/
  _timePlace/_timeJump/_breakTimeBrick` + bloque propio en `_extraCollide` +
  `hitTime` en `fireGun`. Aparece con time≤30 s (apremio: 3 dobles-bips,
  flag `_time30`), reloj.png anclado (timeClock plano bw×0.62), salta cada
  2 s a otro hueco destruido distinto, la bola o el láser lo revientan:
  escombros NEGROS (blackMat), `time += 60`, msg `ark_extra_min`, extra.png
  flotando delante del muro 2 s (sube 0.16 m, fade). `_timeUsed` = UNO por
  intento (blindaje también en _timeSpawn); start() rearma, stop() limpia.
  Las mallas se crean en la sección COMPARTIDA de build() (sobreviven al
  cambio de variante). i18n: `ark_extra_min` ES/EN.
- **CARTELES EN = arte del USUARIO**: victory.png/lost.png (1024², alfa) →
  v244_assets/poster_win_en.webp / poster_lose_en.webp (DATAURL2/3, byte
  match en el build). reloj.webp (DATAURL8 → __PP_RELOJ_URL) y extra.webp
  (DATAURL9 → __PP_EXTRA_URL).
- Suites: `verify_v246.py` NUEVO 29/29 TODO OK; verify_v245/v244
  actualizadas (sideZ0 −0,8/−1,1) TODO OK; verify_v244_regress TODO OK.
  Capturas captura-v246-{arkanoid2,arkanoid1,victory-en,lost-en}.png.
- Pipeline: build_v246.py → ZIP 7,81 MB (MD5 46cb1a0f…) → public/ → README
  v2.46 → gofile **https://gofile.io/d/2cVv4BOw** (MD5 verificado).
- Git: commit v2.46 pendiente.

## 1i. v2.45 (05-oct-2026) — pistola del jugador, viento tras el muro, cristales con textura

- **PISTOLA REAL (pistol.glb del usuario, 2,94 MB → 230 KB)**: optimizada con
  gltf-transform (`optimize --compress false --texture-compress webp
  --texture-size 512 --simplify false`; EXT_texture_webp, three r186 la
  soporta). Análisis de geometría (`scripts/analyze_pistol.py`,
  `pistol_world_bounds.py`): cañón YA a -Z (PCA corrediza: 1,4°), empuñadura
  a -Y; escala x0,05 (18,8×13,4×3,2 cm); puño en el origen del grip
  (GUN_GRIP 1.5504, -0.9415, 1.4313). `GUN_MOUNT_PITCH = 0` (el 60° de v2.44
  apuntaba el cañón al cielo). `GUN_MUZZLE (0, 0.092, -0.163)`: el rayo nace
  en la boca. BLOB44 = pistola nueva (build la sobrescribe ANTES del bucle).
- **ESCOMBROS COLOREADOS**: `_breakBrick` fija `d.mesh.material =
  this.redMats[b.matIdx]` (antes quedaba el material del último uso → rojos
  soltaban restos azules). `_laserConvert` ya usaba blueMats (azules →
  trocitos azules).
- **PÓSTER DEL VIENTO (viento.png → WebP 1280, 126 KB, DATAURL7 →
  __PP_WIND_URL)**: el bloque del póster sale del `if (variant === 1)` y se
  construye en AMBAS variantes; arte según variante (1 = superpoder,
  2 = viento). Misma fórmula de tamaño (aspecto 16:9 coincidente).
- **CRISTALES ESCARCHADOS**: `arkGlassTexture()` (256², moteado determinista
  + junta central + brillo diagonal + marco); glassMat opacity 0,12 → 0,52
  con map. La pared SE VE (petición: "no totalmente transparentes").
- **SAQUE POR GRIP EN ARKANOID**: `releaseBallHand` añade rama arkanoid
  (state='arkanoid' && phase='serve' && i===ballHand → serveTrigger()). El
  gatillo sigue sirviendo. NOTA suite: el menú nace ABIERTO en VR
  (menuOpen=true) → hay que cerrarlo en el test antes de soltar el grip.
- Suites: `verify_v245.py` NUEVO 33 checks TODO OK (caja del arma 0,032 ×
  0,134 × 0,188 m, cañón z∈[-0,166, +0,021], viento cargado 1280 px,
  escombros por color, saque grip, + regresión v2.44 completa) +
  `verify_v244_regress.py` TODO OK + saque normal natural/asistido OK +
  test_ai_returns 13/14 (baseline). Capturas: captura-v245-{arkanoid2,
  arkanoid1, viento, portada}.png.
- Pipeline: build_v245.py → ZIP 7,70 MB (MD5 16c833a5…) → public/ → README
  v2.45 → gofile **https://gofile.io/d/MDFzKWfF** (MD5 verificado).
- Git: pendiente commit v2.45.

## 1h. v2.44 (05-oct-2026) — CAMPEONATO DE LA LOCURA completo (5 etapas) + copa

- **CAMINO DE 5 ETAPAS** (`pp_arcade_stage` 0..5): Clown1 → ARKANOID →
  Clown2 → ARKANOID 2 → Clown3 → ¡CAMPEÓN! Cada victoria avanza; las
  derrotas REPITEN el nivel (sin retroceder). Mapa con 6 nodos reales
  (clown lv1/2/3 + arkanoid + arkanoid2 + TROFEO). Cartel "¡PARTIDA
  NUEVA!" muestra el nivel del Clown.
- **CLOWN Nv. 2/Nv. 3**: `clownSkill()` 1.15/1.35 (multiplica la IA en
  applyAISkill, part3); superpoderes ×1.25/×1.5 más frecuentes y cooldown
  ×0.85/×0.72.
- **ARKANOID 2 (etapa 3)**: `arkanoid.start(level)` — muro 8×6=48 ladrillos
  (cols2/rows2/bh2), ROJOS (`_redMats`) y AZULES (`_blueMats`):
  - La bola NO rompe azules (`_blueClank`: inmunes, "clank" + aviso).
  - El LÁSER (`fireGun` → `laserHit` slab-test → `laserStrike`) CONVIERTE
    el azul en rojo (no lo destruye).
  - Conversión automática: cada `blueEvery: 9` s un rojo vivo → azul.
  - Semilla: `blueStart: 10` azules iniciales.
  - SIN póster del superpoder (`poster.visible = level === 1`).
  - HUD con contador de azules vivos.
- **PISTOLA (política)**: `updateGun` solo la equipa con
  `arkanoid.active && level === 2 && phase === 'play'` — en el SAQUE se
  esconde (se ve la bola). `fireGun` corta el haz en el impacto y golpea.
  Montaje: `loadGunModel()` en part3 setupControllers; pistola.glb con
  cañón -Z → montada SIN giro el cañón mira AL FRENTE.
- **DIVISIÓN DE BOLA (Clown 3)**: `_updateSplit/_doSplit/_stepGhost/
  _consumeGhost/_endSplit` — con 4 golpes de rallye la bola se parte en
  dos BLANCAS (±9°). La bola dividida usa la MISMA física (colisión con tu
  pala incluida) pero sus eventos no van al árbitro; si muere en campo del
  rival → `applyPoint('player','noret_opp')` = PUNTO; en el tuyo no cuesta.
  Una por rallye; sin división si hay poder del rival activo.
- **COPA**: `_buildTrophy` (pedestal + copa dorada en (1.18, 0, -1.05)) +
  `_champion()` — registra `{id:'locura', d}` en `pp_trofeos`,
  confeti + fanfarria + voz. El menú CRAZY podría mostrarla (futuro).
- **MUROS LATERALES +30 cm**: `ARK_CFG.sideZ0Ext: 0.30` →
  `ARK_CFG.sideZ0 = tableCenterZ + 0.30` (visual + colisión + `_crossed`).
- **SAQUE LIBRE (pico del gesto)**: part3 (holdLock) y arcade (serve)
  detectan el lanzamiento: pico `velInst.y > tossAutoVy (1.35)` y sueltan
  cuando la mano FRENA (`vy < pico*0.6`) o con gesto potente (vy > 2.9).
  `tossFromHand` mezcla velInst 65 %. Ventana 22 ms en saque.
- Suites: `verify_v244.py` NUEVO TODO OK (40+ checks) + v243/v242/v241/
  v240/v239/v238-stability actualizadas y TODO OK (v239: reload + stage 0
  para el duck; v243: strings del pico). `verify_v238.py` OBSOLETA.
- Capturas: `captura-v244-arkanoid2.png` (rojos+azules, laterales largos)
  y `captura-v244-mapa.png` (5 etapas + copa).
- Git: commit v2.44.

## 1g. v2.43 (04-oct-2026) — ARKANOID realista + saque natural + música en contexto

- **PAREDES VISIBLES = COLISIONABLES**: cristales opacity 0.30 con marco
  ámbar naciendo EN la superficie de la mesa (glassVis 0.94); pared del
  fondo desde el canto lejano (wallVis 1.04); eliminados rodapiés del suelo
  y postes de 1,81 m (lo que el usuario veía como "paredes mal colocadas").
- **COLISIONES FINITAS**: y-gates en _extraCollide — sin rebotes en aire por
  encima de las paredes (causa real de "zonas de impacto que no coinciden").
- **LADRILLOS**: AABB runtime = mesh (0,000 mm) + brickBoost 1.35 m/s hacia
  el jugador tras la reflexión especular.
- **PERDER = REPETIR** la misma prueba (sin _setStage(0); ark_retry).
- **REFERENCIADO A LA MESA**: fieldGroup/wallGroup/hudGroup en tableGroup.
- **SAQUE NATURAL**: tossAutoVy 1.35 (bola sale sola con el gesto), mezcla
  velInst 0.65, ventana 22 ms en saque; también en ARKANOID (_naturalToss).
- **MÚSICA**: setMusic(false) calla TODO; BSO apagada al salir de VR y con
  invariante "sin arcade activo no hay BSO"; vuelve al reanudar.
- Suites: verify_v243 NUEVO TODO OK + v242/v241 actualizadas TODO OK +
  v240/v239/v238-stability TODO OK. Capturas captura-v243-*.
- Git: tag `v2.43`.

## 1f. v2.42 (04-oct-2026) — ARKANOID = física de PARTIDA NORMAL + alineación con la mesa + regalo ×2

- **FEEDBACK del usuario (4 puntos) resuelto**:
  1. REGALO ×2: manifest v10 `giftBox {w:2.1, h:1.05}` (el doble) — tapa al Clown.
  2. ALINEACIÓN: ARK_CFG ahora se deriva de DIMS (mesa ITTF): muro con el
     ancho EXACTO de la mesa y enrasado al borde de fondo (4 mm), cristales
     laterales EN ±tableHalfWidth (0,7625), pared del fondo EN el borde
     lejano (sideZ1 = tableCenterZ - tableHalfLength = -2,97). Nada fuera
     de la mesa.
  3. BOLA NORMAL: `ballMesh.scale 1` y radio DIMS.ballRadius (40 mm) — fuera
     la bola roja x2 del superpoder (antes Ark usaba r=0.042 y escala 2).
  4. FÍSICA NORMAL: `_physics()` llama a `stepPhysics()` de la partida
     (gravedad real, arrastre, Magnus, MISMO golpeo de pala con velocidad
     real del mando) + hook `_extraCollide` POR SUBPASO (ladrillos con
     reflexión ESPECULAR sin falseo, 3 paredes, bote mínimo). Eliminados:
     grav suave -3.2, speedMin/Max, _playerReturn (devolución falsa) y
     _paddleContact propio. SIN red también en física (`ball.ignoreNet`,
     restaurado en stop()).
- Extras: anti-atasco (_stuckT 1,5 s → saque gratis), _tokCd anti-spam,
  extraReach de saque, escombros con gravedad real.
- Suites: `verify_v242.py` NUEVO (TODO OK) + regresiones v2.41/v2.40/v2.39/
  v2.38-stability TODO OK. Capturas: `download/captura-v242-{arkanoid,regalo}.png`.
- Pipeline: rebuild determinista (MD5 27c0d9cb…) → ZIP (MD5 115e4cc5…) →
  public/ sincronizado → /descarga v2.42 → README v2.42.
- Git: tag `v2.42`.

## 1e. v2.41 (04-oct-2026) — regalo 2D + ARKANOID rediseñado (jugable)

- **REGALO 2D (regalo.png)**: fuera la caja 3D — plano con alfa delante del
  Clown (x=0,42 · z=-3,5 · renderOrder 7). ESTÁTICO (solo posición de build).
  manifest **v9** `giftBox {w:1.05, h:0.525, z:-3.5, x:0.42}`. Arte embebido
  como `__GIFT_PNG_B64__` (WebP con alfa) en `window.__PP_GIFT_URL`.
- **FIX reaparición**: `_afterResult()` restaura `a.rival.gift.visible=true`
  al volver del ARKANOID (antes desaparecía el regalo).
- **ARKANOID v2.41** (game_arcade.js, ArcadeArkanoid reescrito):
  - MURO SOBRE LA MESA: ARK_CFG `baseY: 0.765 · z: -2.75`; 6×5 ladrillos
    biselados (arkBrickTexture, 3 tonos) + peana + pilares; **SIN respaldo
    sólido** (los huecos dejan ver el póster).
  - PERÍMETRO del campo rival: `sideX: 0.92 · sideZ0: -1.55 · sideZ1: -3.22`
    (2 laterales de cristal opacity 0.12 + pared del FONDO) — colisiones con
    pérdida de fuerza + ápice mínimo + _wallTok (sonido).
  - PÓSTER DEL SUPERPODER: `__GUNPOSTER_JPG_B64__` → `window.__PP_GUNPOSTER_URL`
    → plano MeshBasic sobre la pared del fondo (z=-3,215, y=1,2055); oculto
    por los ladrillos, visible por los huecos; LA PARED REBOTA (sideZ1).
  - SIN RED: `_netParts` (plano+banda+postes por posición en tableGroup)
    ocultas en start/reenter, restauradas en stop.
  - SAQUE NORMAL: `serveTrigger()` (lanzamiento asistido serveAssistVy) desde
    onSelectStart (game_part3); pistola solo en fase 'play'; auto-serve 12 s
    (`serveAutoT`); textos ark_serve_hint/ark_autoserve.
  - MESA con FUERZA MÍNIMA: colisión de superficie + _apex (bote nunca muerto).
  - LADRILLOS: destrucción SIEMPRE (flash arkFlashTexture + escombros) y
    DEVOLUCIÓN SIEMPRE `_playerReturn` (arco hacia el jugador, llegada 1,22 m).
  - VIDAS JUSTAS: `_crossed` (cruce de red) — solo pierde vida si cruzó.
- Suites: `verify_v241.py` (TODO OK) · `verify_v240.py` (TODO OK) ·
  `verify_v239.py` ACTUALIZADO (TODO OK) · `verify_v238_stability.py`
  ACTUALIZADO (TODO OK: 13 golpes, 11 rotos, 15 s sin NaN).
- Capturas: `download/captura-v241-arkanoid.png` (muro sobre mesa + póster)
  y `download/captura-v241-regalo.png` (regalo 2D + Clown) — también en public/.
- Git: tag `v2.41` commit `8148005`.

## 1d. v2.40 (04-oct-2026) — anuncio ÉPICO de Super Poder congelando la partida

- **Fuera el «efecto raro de luz»**: eliminados el destello radial y el
  barrido blanco del cartel SUPER POWER.
- **Coreografía (ArcadePowerSign, game_arcade.js)**: ENTRADA rápida desde la
  izquierda (0→0,40 s) · PARADA con leve vaivén (x/inclinación/escala) hasta
  1,45 s · SALIDA rápida por la derecha (1,45→1,90 s). Total ≈2 s. Anclado a
  la CABEZA a 1,05 m; arte 0,92 m.
- **Halo de contorno real**: `_buildHaloFrom()` dibuja la silueta alfa del
  arte con 2 pasadas de sombra (dorado + ámbar) sobre plano aditivo ×1,2
  que respira.
- **Congelación**: `Game.freezeT` (game_part3.js) gatea IA, saque,
  stepPhysics, arkanoid.step y árbitro; `arcade.update` sigue (cartel +
  aviso). `firePower()` fija `freezeT = max(T_OUT, warn)+0,1` = 2,1 s →
  el poder entra justo al reanudarse. `enter()`/`leave()` lo limpian.
- Suite: `verify_v240.py` (TODO OK, incluye coreografía determinista y
  bucle real) + regresiones v2.39 (61) y estabilidad v2.38 TODO OK.
- Git: tag `v2.40` commit `6f65957`. Captura: `download/captura-v240-superpoder.png`.

## 1c. v2.39 (04-oct-2026) — FIX congelación + rival/caja estáticos

- **BUG CRÍTICO CORREGIDO**: `onMatchOver()` (game_arcade.js) usaba la
  variable inexistente `g` («g.rules.stateTimer = 1e9») → ReferenceError
  dentro de processIntents (intent 'game-over') → **el juego se congelaba
  al ganar al CLOWN Nv. 1 y nunca pasaba al ARKANOID**. Ahora:
  `this.game.rules.stateTimer = 1e9` y la cadena funciona (victoria →
  ~4,4 s → startArkanoid). LECCIÓN: SIEMPRE probar la ruta onMatchOver
  (verify_v239 la ejercita: victoria, derrota, processIntents y 2ª
  victoria con pistola).
- **Blindaje**: try/catch en los 4 hooks del campeonato (game_part3.js):
  onPoint, onMatchOver, arcade.update, arkanoid.step.
- **Rival ESTÁTICO**: Clown sin seguimiento de raqueta (X fija = giftX)
  y **10 cm más bajo**: manifest v8 `baseY: 0.52` (era 0,62).
- **Caja de regalo ESTÁTICA**: ya no sigue al Clown; decorado fijo en
  (0.42, 0, -3.42).
- Suite: `scripts/verify_v239.py` (61 checks TODO OK) + estabilidad v2.38
  (15 s física). Capturas: `download/captura-v239-{arkanoid,regalo,mapa}.png`.
- Git: tag `v2.39` commit `aa555af`.

## 1b. v2.38 (04-oct-2026) — qué se añadió y dónde

- **PRUEBA ARKANOID** (2ª parada del camino del campeonato): clase
  `ArcadeArkanoid` en `scripts/game_arcade.js` (muro 6×5 de UN color,
  física con ápice mínimo 0,95 m garantizado, rebote físico en ladrillo +
  sesgo hacia el jugador solo cuando ya vuelve, 120 s con aviso <1 min y
  alarma ≤10 s, 5 vidas, HUD canvas, escombros). Entradas: cola automática
  tras vencer al CLOWN (`arkQueued`) y botón `arkgo` del menú CRAZY.
  Ganar → `pistola` en `pp_arcade_powers` (persistente) + etapa 2.
  Perder → etapa 0 y nueva partida CLOWN Nv. 1.
- **PISTOLA de rayos**: `scripts/make_pistola.py` (trimesh) genera
  `download/pingpong-quest3-v2/assets/pistola.glb` (16 KB); se embebe con
  `__GUN_GLB_B64__` en build_html.py; se monta en la mano LIBRE
  (`game.gunMounts`); gatillo dispara rayos (`ArcadeController.fireGun`).
- **ETAPA del camino**: `pp_arcade_stage` (0 CLOWN · 1 ARKANOID · 2
  pistola) — la lee ArcadeMap para el anillo de progreso.
- **Caja de regalo** pequeña a la derecha: manifest `giftBox` con `x`
  (0,42) y `baseY` 0,62 (el Clown SALE de la caja).
- **Mapa-póster**: pared izquierda x=-2,98 con respaldo propio.
- Capturas: `download/captura-v238-{arkanoid,regalo,mapa}.png`
  (también en public/). Suite: `scripts/verify_v238.py` (86 checks) +
  `scripts/verify_v238_stability.py`.

## 2. Procedimiento "dame un enlace de descarga" (probado 03-oct-2026)

Servicios de subida, en orden de preferencia:

1. **gofile.io (RECOMENDADO, estable ~10 días sin descargas)**
   ```bash
   # 1) obtener servidor:  curl -s https://api.gofile.io/servers
   # 2) subir (usar el name devuelto, p.ej. store10):
   curl -s -m 180 -F "file=@/home/z/my-project/download/pingpong-quest3-v2.zip" \
        https://store10.gofile.io/contents/uploadfile
   # 3) del JSON: data.downloadPage (enlace para el usuario) y data.md5
   #    (COMPARAR con md5sum local — integridad end-to-end gratis).
   ```
   - El enlace "directo" de servidor
     (`https://{srv}.gofile.io/download/web/{id}/{file}`) YA NO devuelve el
     archivo: devuelve HTML. Dar SIEMPRE el downloadPage.
2. **tmpfiles.org (rápido, caduca ~60 min)**
   ```bash
   curl -s -m 90 -F "file=@<zip>" https://tmpfiles.org/api/v1/upload
   # data.url = página de descarga para el usuario (la ruta /dl/ ahora
   # devuelve página intermedia, NO descarga directa).
   ```
3. **BLOQUEADOS desde este entorno (no reintentar)**:
   - `catbox.moe` → rechaza con "Invalid uploader".
   - `0x0.st` → HTTP 000 (conexión imposible).

### Enlaces vigentes (06-oct-2026)
- gofile v2.50 ZIP completo (principal): **https://gofile.io/d/AJKfujjQ** (MD5 69910f1d86c98c39aeef0142adf1a9d0 = local)
- gofile v2.50 netlify-drop: **https://gofile.io/d/tBFIzIWT** (MD5 b06b4d0f364cc3be4ef4c26733572c52 = local)
- gofile v2.50 PROMO vídeo: **https://gofile.io/d/VqZe2Cnm** (MD5 f0958dfbccb9139c9b5cf3831d207a70 = local)
- gofile v2.49 (principal): **https://gofile.io/d/pPcXLtUB** (MD5 b7bac5179e244a0a558d53c1ff7b7eeb verificado = local)
- gofile v2.48: https://gofile.io/d/4fyeveYH (MD5 5d110edef601aeff1fdf6ce39c5be6cf)
- gofile v2.47: https://gofile.io/d/vRFxvkVO (MD5 deb7ff1b96b528c9057512d40ff3417e verificado = local)
- gofile v2.46: https://gofile.io/d/2cVv4BOw (MD5 46cb1a0fe5c7e34d95bb5f87f02a3564)
- gofile v2.45: https://gofile.io/d/MDFzKWfF (MD5 16c833a577cf106cde85585cc4dc5f36 verificado = local)
- gofile v2.44: https://gofile.io/d/tE9Lz48h · v2.43: https://gofile.io/d/wH5MwZeS (MD5 2a4a43f6... verificado = local)
- gofile v2.42: https://gofile.io/d/TFi3iwec (MD5 115e4cc5...)
- gofile v2.41: https://gofile.io/d/i7m5l484 · v2.40: https://gofile.io/d/klvbS2HL · v2.39: https://gofile.io/d/zl7TlAmW · v2.38: https://gofile.io/d/8atbEEGi · v2.37: https://gofile.io/d/q0fRH71u · v2.36: https://gofile.io/d/tBtwTuGB
- backup completo v2.47 (155 MB, 05-oct-2026): **https://gofile.io/d/dlhFG0G1** (MD5 2640c1afaed8400697f4fbc3bea6d336 verificado = local)
- backup completo v2.36: https://gofile.io/d/8jFfrolN
- Si caducan: re-subir el ZIP actual con los comandos de arriba y MD5-check.

## 3. Copias de seguridad

- **Tags git**: `v2.36` (44eae2d), `v2.37`, `v2.38` (dd7b8c1) y `v2.39`
  (aa555af: fix congelación, rival/caja estáticos; repo con autocommit).
- **Respaldo completo (tar.gz, 52 MB, MD5 348c0e9a9da94035dd2c05169c815604)**:
  - Local: `/home/z/my-project/download/crazy-pingpong-backup-v2.36-20261004.tar.gz`
  - Externo (gofile, estable): **https://gofile.io/d/8jFfrolN**
  - Contenido: fuentes (`scripts/`: game_part*.js, game_arcade.js,
    game_i18n.js, build_html.py, verify_*.py, championships/clown completo),
    originales del usuario (`upload/`: GLB, Clown.zip, mp3, PNG carteles),
    build final (`download/pingpong-quest3-v2/`), README, página `/descarga`,
    copia servida (`public/`), worklog y este MEMORIA.md.
  - Regenerar en el futuro: `bash scripts/backup/make_backup.sh [version]`
    (p.ej. `make_backup.sh v2.37`; por defecto sigue etiquetando el punto
    v2.36; el script también queda incluido en el propio backup).

## 4. Lecciones aprendidas (resumen operativo)

- Tras CUALQUIER cambio: rebuild + verify (suite pytest-style en
  `scripts/verify_v2xx.py`) + ZIP + `public/` + `/descarga` + README +
  worklog, SIEMPRE en ese orden (el ZIP y public/ se quedan viejos a menudo).
- Worklog canónico compartido: `/home/z/my-project/worklog.md` (append-only).
- Assets originales del artista/usuario SIEMPRE en `/home/z/my-project/upload/`
  (Clown.zip, SuperPower.png, risas.mp3, Four Funny Voices.mp3, pala GLB…).

## 1q. v2.53 (06-oct-2026) — CAMPEONATO DE LAS NUBES (clon estructural de La Locura en carpeta)

**DECISIÓN DE ARQUITECTURA (petición expresa del usuario):** los campeonatos
nuevos se hacen DUPLICANDO la estructura de "De la Locura" (el Clown) en una
carpeta autocontenida `championships/<id>/` y sustituyendo rival, temática y
mecánicas — mismas poses/gestos (12 estados), mismo itinerario de 6 pasos,
pruebas intermedias nuevas entre jefes. La arquitectura v2.52 (ChampHost +
hooks + El Relojero) se REVERTIÓ (commit `1ac2da5`; nunca llegó a desplegarse).

**NÚCLEO (aditivo, La Locura intacta — verify_v249 25/25):**
- `ChampLoader` (~140 líneas): descubre `championships/championships.json`
  (en file:// se omite en silencio), botón por campeonato en el menú CRAZY
  (bajo todo el bloque de La Locura), `import()` dinámico CON './' y
  delegación con guard de update/onPoint/onMatchOver/serve/reenter/testStep.
- 14+3 enganches aditivos (bucle, árbitro game-over/point, menú, despachador
  `ppchamp:`, leaveAll en start/survgo/traingo/arcgo/arkgo/arkgo2, física en
  pausa con `rules.state='champtest'`, saque por gatillo/grip, reenter VR,
  pala IA oculta, aiMul). Excluyentes en ambos sentidos con La Locura.
- `window.__PP_CORE` (puente de solo-lectura: DIMS, stepPhysics, T, lang,
  AI_PRESETS, scalePreset) — el juego vive en un módulo ES y sus globals NO
  son visibles desde las carpetas. Los módulos importan 'three' por el
  importmap (misma instancia).
- i18n: `opp_nubes: 'NIMBO'` (es/en). VERSION 2.53.0.

**CAMPEONATO DE LAS NUBES (`championships/nubes/`, 0 binarios, todo
procedural):** manifest.json + index.js (~2.400 líneas ESM). Rival **NIMBO**
(espíritu de nube, banco de nubes delante = rol del regalo) con las MISMAS
12 poses/estados que el Clown y voz sintética propia; ranking lateral con
récords reales; cartel «¡PARTIDA NUEVA! VS NIMBO»; mapa procedural con 5
medallones y tapas; superpoderes con cartel épico + congelación:
RÁFAGA DE VIENTO (desviación ACOTADA 2,2 m/s²) y BOLA DE VAPOR (clon de la
bola loca en blanco), TORMENTA en Nv.3; poder del jugador VIENTO A FAVOR
(= mega pala) por Crazy Combo; pruebas **CAZANUBES 1 y 2** (revienta nubes
con la física real del juego + recinto de cristal y muro de viento
(idéntico al Arkanoid), 5 vidas, saque asistido, saque automático; la 2 con
nubes móviles, viento y RÁFAGA con el gatillo); trofeo **Nube de Plata**
que vive en la sala. Storage propio `pp_champ_nubes_*` (no pisa
`pp_arcade_*`).

**PRUEBAS:** build `scripts/build_v253.py` (46 checks + ESM + endpoint
crazypp-tele + championships/ al paquete) · banco E2E
`scripts/nubes_bench.py` **39/39 TODO OK** (import, exclusividad, victoria→
cola→prueba→pop→redirección→recompensa→Nv.2→trofeo→leave restore) ·
verify_v249 25/25 · IA 11/14 (= récord histórico guardado, sin regresión).
Fuente del módulo en 4 partes: `scripts/nubes_p{1..4}.js`.

**LECCIONES (bugs pillados por el banco):**
1. Los módulos externos deben desestructurar `window.__PP_CORE` (DIMS etc.
   no son globals reales desde un import()).
2. `applySpriteAspect` se llama DESPUÉS de crear sprite+gotas (el Clown
   llegaba en el onload; la llamada temprana rompía con stars undefined).
3. `this.ctrl` en TODAS las clases del clon (PowerSign lo pedía).
4. En el banco headless: `window.__pp2DPlay = true` SIEMPRE (árbitro gated)
   y conducir fases con `champs.testStep(dt)` (dt clampeado en SwiftShader).
5. gofile hoy caído (HTTP 000): el zip queda en
   `download/netlify-drop-v2.53.zip` (13,6 MB, md5 del html
   32214078776039f5f171db6624f10f14); subir a Cloudflare con el flujo de
   siempre (New deployment → arrastrar; AHORA incluye championships/).

## 1r · v2.54 — NUEVO TRUCO DE MAGIA (WIZARD) · segundo clon de la familia

**PETICIÓN:** Nimbo → Wizard; campeonato «Nuevo truco de Magia»; 12 poses
REALES del artista (Wizrad.zip), regalo.png = PORTAL que tapa la parte baja
del mago y GIRA LENTAMENTE sobre su centro (posición fija), WizardRisas.mp3
(risa real), NewTrick.mp3 (BSO), Mapa.png (mapa oficial). Mecánicas
intermedias: MÁS ADELANTE (quedan provisionales).

**ARQUITECTURA (misma filosofía de carpeta autocontenida):**
`championships/magia/` = clon de `nubes/` generado por
`scripts/make_magia.py` (transformación ASERTADA de nubes/index.js: cada
edición exige conteo exacto; si el fuente cambia, aborta). Assets reales en
`championships/magia/assets/` (16 ficheros, 2,4 MB): 12 poses webp
(present…defeated), regalo.webp, mapa.webp, risas.mp3 (128k), bso.mp3 (64k).
Los URL se resuelven con `new URL('./assets/x', import.meta.url)` — sin
rutas relativas al documento. Core ADITIVO mínimo: `opp_wizard: 'WIZARD'`
(es+en) + VERSION 2.54.0; championships.json = ["nubes","magia"].

**TEMÁTICA:** rival WIZARD (oppLabel 'wizard') · itinerario idéntico de 6
pasos · PORTAL (regalo.webp) girando a 0,35 rad/s en update() del rival ·
risa REAL en laugh/crazy (decodeAudioData + throttle 3,2 s, gain 1.0 por
panNode) · BSO real en bucle a 0,15 (musicOn perezoso: carga al primer uso,
arranca cuando el ctx está running) · mapa = mapa.webp + etiquetas doradas
con trazo, tapas por nodo (tapaS 0,36 / 0,46 final) calibradas sobre los 5
medallones REALES medidos con `scripts/measure_mapa_magia2.py`
(0.165,0.350 · 0.328,0.671 · 0.506,0.376 · 0.691,0.675 · 0.880,0.253 v=desde
ARRIBA) · poderes renombrados (HECHIZO DE VIENTO / BOLA ESPECTRAL /
TORMENTA ARCANA; recompensa PALA ENCANTADA = clave 'pala_encantada') ·
prueba provisional ORBE MÁGICO (clon de Cazanubes con orbes violeta 0xc4a4f4
+ muro de niebla púrpura) · trofeo VARITA DORADA (fuste dorado inclinado +
orbe arcánico + luz púrpura) · paleta arcano: #c9a6ff/#f6d34c sobre
rgba(18,12,38).

**PRUEBAS:** build_v254 (checks + ESM de ambos módulos + 16 assets al
paquete + índice ['nubes','magia']) · NUEVO `scripts/magia_bench.py`
**48/48 TODO OK** (assets por HTTP, portal girando medido, camino completo,
exclusividad externa-externa en AMBOS sentidos) · nubes_bench TODO OK
(expectativa del índice actualizada a 2 entradas) · verify_v249 25/25.
Capturas: download/captura-v254-{wizard,cartel,orbes,mapa}.png.

**LECCIONES nuevas:**
1. El título del mapa pintado sobre el arte debe caber ANTES de la tapa del
   Nv.3 (46px; a 54px la tapa en u=0.744 se comía la "A").
2. Al renombrar config (giftBox→portal) hay que buscar usos ocultos
   (sprite.position y stars usaban giftBox.x → NaN silencioso).
3. El barrido de comentarios regex debe aplicar TODOS los patrones (el
   early-return dejaba restos en bloques grandes).
4. El paquete v2.54 crece a 16,0 MB (assets del mago); el html no cambia
   (los assets van en la carpeta, no embebidos).

## 1º · v2.95 — ASEDIO AL ESCONDITE 2.0 (módulo oeste v13 · la prueba 1, rehecha)

**PETICIÓN:** «las pruebas de habilidad del oeste están muy cutres» → reconstruir la etapa 2 como la AVENIDA del pueblo (spec detallada del artista: casas con porches, calle embarrada, desierto, buitres, huesos) y FUERA los troqueles de la sala en las dos pruebas.

**MÓDULO (`championships/championships/oeste/index.js`, +32 KB):** clase AsedioAction REESCRITA (~800 líneas): cúpula de cielo con nubes salpicadas + sol aditivo, montañas rojizas ×2 capas, pueblo lejano con molino, arena infinita (CircleGeometry) + AVENIDA EMBARRADA con charcos/rodadas + tablón, 6 CASAS de zona (FUNERARIA · HOTEL 2 plantas · SALOON · ALMACÉN 2 plantas · BANCO · BARBERÍA) + iglesia/herrería de relleno, cada zona = TROQUEL (puerta/ventana canvas) que oculta al forajido, GRAN DEPÓSITO DE AGUA (torre), 5 cactus, 3 BUITRES orbitando, costillas+cráneo de bisonte a la espalda. BOLA-BOMBA negra (color 0x17120d, em 0x2a1408) con MECHA (cuerda + chispa aditiva + bufido cada 0,5 s, hijo de ballMesh, restauración en dispose). DIANA = diana.webp del artista (fallback procedural) + halo aditivo latiendo; CAMBIA SOLA (dwell 30/20/10 s por oleada) a zona libre distinta. ACIERTO (bola vs diana r=0,24 en el colisionador _extra a 480 Hz): boom + 14 astillas + troquel FUERA + forajido (pose duelo del artista, pop 0,18 s) + CORAZÓN (2,06 puertas / 2,42 ventanas) → reveal 3 s → _shotAt vs corazón r=0,215 → kill (pose defeated, desplome+fade) o _punish: ÉL DISPARA (flash+bang+humo) y manchones PERSISTENTES (SangreManchon.trigger(n, persist): sin fade, opacidad 0,52, se acumulan con _heridas, se retiran al cerrar/leave). 6 kills (2 por oleada) → WIN → _endAsedio(true); reloj 3:00 corre en play Y reveal. La sala se ABRE igual que en el tren (room/decor/mapa/cartel/rival/arbusto fuera).

**FIX CORE ADITIVO (2 líneas):** champDecor.update forzaba group.visible cada frame → los troqueles reaparecían en las pruebas (bug cosmético de v2.94 también en el tren). Nuevo flag `game.champDecorHidden` (inicial false) respetado en el want del decor; asedio/tren lo activan al abrir y _endPrueba/leave/dispose lo apagan. FIX módulo: si la prueba arranca sin GLB del revólver cargado, _freeGunApply se re-aplica en el onload.

**ARNÉS:** `scripts/v295/` — splice_v295.py (11 ediciones asertadas), patch_v295b.py (flag troqueles), package_v295.py (manifest v13 + championships.json + núcleo 2.95.0 + zip), verify_v295.py **54/54 TODO OK** (estáticos, sala, asedio completo: diana sola→breach→kill→punish→manchones→6 kills→stage 3→restauración; regresiones v2.94: GUN_PITCH, DUELO_NV, TREN con candados; leave restaura todo). Capturas: scripts/v295/v295_asedio_{avenida,destapado,manchones}.png.

**LECCIONES nuevas:**
1. champDecor/champRoom del núcleo son IDEMPOTENTES por frame: ocultar sus grupos desde un módulo no basta → hace falta flag de supresión.
2. El GLB del revólver llega ASÍNCRONO: toda prueba que monte el arma debe re-aplicar el montaje en el onload si ya está activa.
3. En headless la carga del GLB tarda >2,6 s: el arnés debe esperar a _revolverReady antes de comprobar monturas.

**ENTREGA:** gofile caído (servidores vacíos) → litterbox 72 h: https://litter.catbox.moe/5xpg4d.zip (39.103.326 B, md5 08e0b1956337ff082e9f25a4a52db43f, unzip -t OK). Copia local: download/crazypp-v295.zip (y /home/z/my-project/download/).
