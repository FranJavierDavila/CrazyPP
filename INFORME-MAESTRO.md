# INFORME MAESTRO · CRAZY PING PONG — Base de conocimiento absoluta para el agente de desarrollo

> **Fecha de corte**: 2026-11-26 · r152 (16ª pasada) · versión **3.6.235-SDK6** · fase 190 · golden `617643ca…` · r151 (15ª) en la historia.
> **Para quién**: un agente de IA que retome el desarrollo. Esta base + `worklog.md` (41 secciones de lecciones en vivo) + los arneses de `scripts/` son TODO lo necesario.
> **Cómo usarla**: cada afirmación se cita con `fichero:línea` para que puedas verificarla contra el código real. Si el código y esta base discrepan, **manda el código** — y actualiza esta base. El `worklog.md` es el diario cronológico con la historia completa de por qué existe cada cosa; esta base es el mapa atemporal.

---

## 0 · Qué es este proyecto en una frase

**Crazy Ping Pong** es un juego VR de ping-pong (WebXR, Three.js, monolítico sin framework, íntegramente en español) desplegado como estático en GitHub Pages con telemetría/red en un worker de Cloudflare: partida local contra CPU con IA física real, multijugador 1v1 por WebRTC con árbitro autoritativo, seis campeonatos data-driven con rivales expresivos, economía de recompensas (logros, skins con candado, poderes) y una batería de calidad de 500+ checks verdes que protege cada cambio.

### Filosofía del código (leída de sus propios comentarios, obrigatoria)

1. **«Un fallo JAMÁS congela el frame»** — cada subsistema corre bajo try/catch propio; el bucle `animate` tiene además un escudo global que deduplica errores por firma y continúa (c12:18529, catch en c12:20146). Nunca dejes que una excepción mate el `setAnimationLoop`.
2. **El DATO manda** — toda la configuración (dimensiones, dificultad, logros, audio, menús, skins, torneos) vive como datos en `c02_cfg_escena.js`; la lógica la lee en vivo. Cambiar comportamiento = cambiar datos siempre que sea posible.
3. **UNA sola ecuación física** (doctrina v3.0.5-FIS1) — vuelo RK4 `integraVuelo` y bote `bounceOnTable` (c04) son compartidos por física real, predictor de IA y solver de saque. **Prohibido replicar la física a mano** en cualquier simulador nuevo.
4. **Convención del ganador/sacador: SIEMPRE `'player' | 'ai'`** (c06:234 `other`, applyPoint c06:336). El FIX CRÍTICO v3.2 de estacion_orbital nació de tratar `'rival'` (string truthy) como booleano. Jamás introduzcas otra etiqueta.
5. **Defecto cazado ⇒ arnés reproducible** — ningún fix se considera hecho sin un script en `scripts/test_*.mjs|py` que lo ampare (método de extracción: código REAL ejecutado sobre mocks, ver §16).
6. **Autocuración antes que guardia** — los caminos de salida (leaveAll, mute, over) restauran el estado global aunque el camino de entrada fallara (lección r60/r97/F-O1/F-A1, §17).

---

## 1 · Mapa del repositorio

```
/home/z/my-project/
├── INFORME-MAESTRO.md          ← ESTA BASE (vivirás aquí)
├── worklog.md                  ← diario cronológico, 41 secciones (§1..§41)
├── Caddyfile                   ← proxy del dueño: :81 → 3000 (Next), ?XTransformPort=3004 → live-service, /peerjs/* → :3005
├── package.json / bun.lock     ← deps raíz (Next HUB, devDeps ws+peer para arneses)
├── src/game/                   ← FUENTE DEL JUEGO
│   ├── core/c00..c13*.js       ← los 14 subsistemas (§4); módulos ES con bloques DEPS-FASE2
│   ├── 00_head/02_importmap/03_body/04_boot/07_tail.html ← piezas del ensamblado
│   ├── VERSION.json            ← fuente única de versión (fase, hub, manifests, golden, tamano)
│   ├── DEPS.json + DEPENDENCIAS.md ← grafo de dependencias generado por mod_fase2_analizar.mjs
│   └── GOLDEN_SHA256.txt       ← sha256 del game.html esperado (byte-exacto)
├── public/                     ← LO QUE SE DESPLIEGA
│   ├── game.html               ← ENSAMBLADO (no editar a mano: build_game.py lo genera)
│   ├── championships/          ← índice championships.json + _plantilla + PLANTILLA-GUIA.md + championship.schema.json + sdk/ + los 6 campeonatos
│   ├── assets/                 ← arte (salones, decor, voz, campeonatos)
│   ├── vendor/three/           ← three vendado (importmap apunta aquí)
│   ├── sw.js                   ← service worker (caché por versión, §14)
│   ├── descargas/              ← los 4 ZIPs de release (se regeneran; el reciclaje los borra)
│   └── telemetria.html         ← panel estático con LED y rankings
├── scripts/                    ← build + QA + arneses + worker (§15-§16)
│   ├── build_game.py, bump_version.py, c2_sellar.py, qa_version.py, deploy_pages.py, deploy_worker.py
│   ├── gen_campeonato.py, qa_plantilla.py   ← fábrica de campeonatos
│   ├── worker-tele/            ← worker.js + wrangler.toml + test_local.mjs + .github-pat (gitignored)
│   ├── test_*.mjs/py           ← la batería (§16) y las serie históricas r21-r148 (todas verdes)
│   └── archivo/era_legacy/     ← historia preservada (no ejecutar)
├── mini-services/              ← live-service (:3004, Bun+socket.io) y peer-server (:3005, node+peer)
├── src/app/                    ← HUB Next.js: telemetria/page.tsx, descargas/page.tsx, api/telemetria/route.ts, api/channels/route.ts
└── upload/                     ← entrada del dueño (NO modificar en sitio)
```

Regla de repositorio: **todo lo que el reciclaje del sandbox borra (node_modules, ZIPs, download/) se regenera byte-exacto desde git** — no hay artefacto único irrecuperable. Los procesos arrancados por tools mueren al acabar la llamada; solo lo supervisado por pid 1 sobrevive.

---

## 2 · Ensamblado de `game.html` (pipeline de build)

`public/game.html` es un **único monolito** generado — jamás editarlo a mano (bump_version.py lo aborta si detecta sellos tocados).

- **Orden fijo** (`scripts/build_game.py:61-87`): `00_head.html` (DOCTYPE, manifest PWA) → `01_vendor.html` (socket.io inline) → `02_importmap.html` (three → `./vendor/three/build/three.module.js`, addons → `./vendor/three/addons/`; rutas RELATIVAS para el prefijo `/CrazyPP/`) → `03_body.html` (canvas `#c`, portada, badge `#verBadge`) → `04_boot.html` (Ko-fi, `PP_TELEMETRY_ENDPOINT` con routing por host — localhost va al receptor Next `/api/telemetria`, producción al worker — y **watchdog de arranque 15 s** que muestra panel si el grafo de módulos muere) → apertura `<script type="module">` → `core/c00…c13` → cierre → `07_tail.html` (PeerJS minificado inline + música de portada `__PP_MUSIC_URL`).
- **Un fichero nuevo en `core/` NO entra solo**: hay que añadirlo a `ORDER`.
- **Patrón DEPS-FASE2**: los módulos de core/ se generan como módulos ES reales (bloques `DEPS-FASE2-INICIO/FIN` + prefijos `export ` en columna 0, producidos por `node scripts/mod_fase2_generar.mjs`); al ensamblar, `pieza_pura()` (build_game.py:25,40-58) elimina esos bloques y prefijos para que el monolito comparta ámbito como siempre. **`export ` en columna 0 dentro de core/ está reservado al generador.**
- **Escritura atómica** temp + `os.replace` (r29): escribir directo sobre un fichero que encoge deja bytes nulos de cola (incidente 3.6.127).
- **Golden**: `build_game.py` sin `--escribir` es ensayo y compara byte-exacto con `GOLDEN_SHA256.txt`; `bump_version.py` y `c2_sellar.py` lo refrescan; `qa_version.py` cruza game.html == golden == VERSION.json.golden == servidores :3000/:81 si están vivos.
- **Doble `import * as THREE` en un core/ es normal** (uno vive en bloque DEPS-FASE2 que el ensamblado elimina; verificado con node — en ESM puro sería SyntaxError).

---
## 3 · Los 14 subsistemas del núcleo (`src/game/core/`, 51.378 líneas)

| Fichero | Líneas | Rol |
|---|---|---|
| c00_pre_three.js | 3637 | Pre-Three: i18n `T/TLang`, banco de voz `VOICE_B64/VOICE_B64_EN`, `const VERSION`, `PP_ICONS`, `WORLDRANK`, `__PP_TELE`, `ppDebugMode`, `applyLangDOM` |
| c01_modelos_3d.js | 291 | Modelos: `loadPaddleModel/loadGunModel` con **fallback procedural en fallo**, `fixInvertedMeshes`, `makePaddleVisual` |
| c02_cfg_escena.js | 1440 | **El bloque de datos maestro** (DIMS, CONFIG_*, skins, ELO, IA) — ver §3.4 |
| c03_audio_voz.js | 2084 | Audio: canales música/salón/BSO/voz, invariantes UNA MELODÍA, LRU de buffers (§9) |
| c04_fisica_ccd.js | 544 | Física compartida: RK4, CCD por SDF, bote slip-coupled, sim de pala (§5) |
| c05_colisiones_ia_golpeo.js | 1496 | Colisiones mesa/red/mundo/palas + emisión de eventos + IA de golpeo (§5) |
| c06_logros_stats_ia_rival.js | 1824 | **Árbitro `Rules` + estadísticas `GameStats` + motor de IA rival** (§6) |
| c07_escena_sala.js | 1454 | Sala, mesa, skins de bola, partículas, troqueles champDecor (§10) |
| c08_hall_hud.js | 2929 | Salón principal (paredes pintadas en canvas), HUD/marcador, fanfarria, confeti (§11) |
| c09_red_netlink.js | 3357 | `NetLink`: salas PeerJS host/guest, voz MediaConnection, presencia (§7) |
| c09b_red_nucleo.js | 993 | `PPNET`: núcleo binario de red (claims/ACK/watchdog/extrapolación) (§7) |
| c09c_red_social.js | 432 | `RedSocial`: medallón de presencia + buzón de invitaciones vía worker (§7) |
| c10_menu_saque.js | 113 | **NO es un menú**: constantes del saque y poses IA (`SWING_POSE`, `AI_TOSS_T`, `CHAMPS_STATE='champtest'`, raycaster del mapa de ruta far 9 m) |
| c11_champloader.js | 1139 | `ChampLoader`: carga/gestión de campeonatos (§8) |
| c12_pingponggame.js | 22781 | **El corazón**: clase `PingPongGame`, bucle animate, DUELOS, poderes (§3.3) |
| c13_ui_arranque.js | 6864 | Boot, portada 2D, PP_TRAIN, LA ACADEMIA, laboratorios QA (§11) |

### 3.1 · c00 — i18n y voz
- `T(key, {vars})` (c00:2925) traduce con plantillas; `setLang/__setLang` cambia es/en (menú VR `case 'lang'` c12:7772, portada `[data-lang]` c13:4096). Las claves nuevas se añaden a las tablas de c00.
- El banco de voz (`VOICE_B64/VOICE_B64_EN`, `export let`) se carga externo desde `assets/audio/voz_*.json` + evento `pp-voz-lista` → `reloadVoice` (c03). El banco es-ES real tiene 112 claves, incluyendo `'y'`.
- Añadir logros ⇒ añadir sus textos `ach_*` aquí.

### 3.2 · c02 — el DATO manda (configuración)
- **`DIMS`** (c02:1-206): constantes físicas y de sala — `tableTopY 0.76`, `tableHalfLength 1.37`, `tableHalfWidth 0.7625`, `netTopY 0.9125`, `ballRadius 0.02`, `tableCenterZ -1.6`, `gravity -9.81`, `airDragK 0.1267` (calibrada a velocidad terminal 8,8 m/s ITTF), `tableRestitution 0.935`, `paddleRestitution 0.85`, `bladeRadius 0.0795`, `hitAssistRadius 0.05`, `minExitSpeed 2.3`, `paddleHitCooldown 0.24` (mata el doble golpe fantasma; NO bajar sin rebatir la lección), `paddleVelClamp 16` (r113: el smash real no se recorta), `maxBallSpeed 18`, `physicsRealism 1` (0 = rollback a la ruta legada). Sala: `roomHalfX 3.05`, `roomBackZ 2.35`, `roomFrontZ -5.55`, `roomHeight 2.85`.
- **`CONFIG_TORNEOS.partido`** (c02:1277-1288): `puntosGanar 11`, `ventajaMinima 2`, `igualaEn 10`, `saqueCada 2`, `saqueIguala 1` (deuce), `pausaPuntoS 2.2`, `pausaSupervivenciaS 1.7`, `bestOfLibre 3`, `serieFactor 2` (serie acabada cuando victorias×factor > bestOf). Más `caminos` (5 etapas por campeonato), `portada 'locura'`, `candados ['estacion_orbital']`, `circuito` (niveles, combo x2/x3, estrellas).
- **`CONFIG_DIFICULTAD`** (c02:233-274): `presets` easy/medium/hard (`maxSpeed, accel, errStd, missBase, minT/maxT, maxShotSpeed, predictInterval, smash, short`); `saque` (asistencia por tier); `escala` (topes legales y exponentes de `scalePreset`, k ∈ [0.7, 2.2] — "nunca un muro"); `elo` (anclas CPU 900/1050/1200, bandas matchmaking <975/<1125, jitter ±120); `adaptativo` (paso por punto, topeDif 6); `supervivencia` (+0.08/rallye, techo 2.1); `esfuerzo` (fórmula del fallo CPU). Aliases: `AI_PRESETS`, `SERVE_ASSIST_TIERS`, `ELO_CPU`; `rivalPorElo(elo, jitter)` (c02:390) es función pura con k = 10^((objetivo−base)/400).
- **`CONFIG_LOGROS`** (c02:1322-1344): `core` = 6 medallones `{key, emoji, nameKey, descKey, cond:{tipo, valor}}` (primera, racha3, gigante=hard, maraton=rallye 20, superviv=25, aces10) + `train` = 10 honores del PRO TRAINING. El catálogo `ACHIEVEMENTS` de c06 **se deriva solo** de aquí (c06:1-6) — añadir fila basta para el catálogo; el disparo de la condición va en GameStats (c06).
- **Catálogos**: `OPPONENT_STYLES` 12 personalidades (c02:414) + `CARRERA_DIVISIONES` 5×3 rivales (c02:517), `MESA_ASPECTOS` 5 skins (c02:578), `BOLA_ASPECTOS` 16 (c02:608), `MESA_ALTOS` [0.70..0.84], `ROOM_THEMES` 5 (c02:742), `HALL_VARIANTES` (museo/cabaña), `ARCANO_CFG` ventanas de poderes (c02:843), `CONFIG_AUDIO` (c02:1228), `CONFIG_MENU/S/SECCIONES`, `CONFIG_PIELES` 9 skins de pala (c02:1374), `CONFIG_RALLY`, `CONFIG_MEDALLAS`, `SERVE_TUNE` (vivo en `__ppDebug.serveTune`), `MOUNT_QUAT_*` (montura de pala, c02:805).

### 3.3 · c12 — el corazón (clase `PingPongGame`, 22.781 líneas)
- **Constructor** (c12:2): renderer XR con guard de framebuffer (`__PP_KEEP_FRAMEBUFFER`), `perf = PerfManager` (61), `audio = GameAudio` (64), **`rules = new Rules()`** (65) con hook `rules.onMatchStart` (77-113: recogida de poderes, re-ancla `oppName`, música del salón — ÚNICO punto de recogida de estado pegajoso, 15 caminos de startMatch), `ball = {pos,vel,spin}` (101), `controllerPaddles = [paddleSim×2]` (120: uno lleva la pala, otro la bola — cambio de mano A/X), `champDecor` (810), `hallGroup` (823), sala Arcano (829), NetLink/social.
- **Bucle `animate`** (arrow en 18524, `setAnimationLoop` en 618). Orden sagrado de bloques: escudo try global → **0)** botones A/X/B y menú (18644) → **0.85)** red: emitir pose/bola, MATCH_START cuenta atrás (18767) → **1)** palas VR (18813) → **2)** IA + compañero + rival 2 (18856) → **3)** preparación de saque (19041) → **4)** `stepPhysics` (19305) → **4.5-4.95)** ventanas de poderes sobre la bola (19516) → **5)** golpe de saque ITTF (19537) → **5.5-5.6)** golpeos de rally/portal/fénix (19602) → **6)** árbitro: `processIntents(rules.handleEvents(events))` + `processIntents(rules.update(dt))` (19713-19736) → PP_TRAIN/ACADEMIA → **7)** sincronizar visuales y HUD (19754) → **8)** cámara órbita 2D → **9)** render. `dt` (UI) capado 1/30 s; `dtFis` (física) tiempo real capado 1/12 s (18539) — la bola integra a tiempo real (r43), no reintroducir caps que la ralenticen.
- **`processIntents`** (c12:21086): consume los intents del árbitro — sonido/applause, stats y récords, retos, CLAIM/ACK online (21100-21110), y `game-over` (21268): telemetría, dilatación del último vuelo, `startFanfare` (21349).
- **DUELOS LOCOS §DUELOS** (r84): estado `_dl*` (222-232); `_dlTrigger` (16061, un poder activo a la vez, ventana `_dlT`), `_dlArma` (16095) reutiliza los triggers de campeonato con ent sintético en `_megaMatriz` (14 triggers: red, elec, fenix, crono, bolaloca, oscuridad, prisma, onda, salva, ancla, clon, portal, efecto, iman — 11327-15087), espejo online `onRemoteDueloPower`/`sendDueloPower` (16150), tick `_dlUpdate` (16212).
- **Poderes locales de pala**: `megaTrigger` (10730), carga por rally 11+ (`_megaCharge` 10993), desbloqueo persistente `pp_poderes_v1` (9371), recogida en `_megaNormReset` (15708). En pruebas de habilidad se cortinan (`_poderesEnPrueba` 10705).
- **Ganchos públicos** (lo que el resto del juego y los campeonatos piden): `audio.setMusicWanted(bool)` (6391/6405), `audio.setHallWanted(mus, url)` (8564/9108/9672/20246/20360), `setArcWanted` (BSO campeonato), `champDecor`, `showChampIntro/hideChampIntro` (17714/17896), `showChampCurtain` (17528), `showChampConseguido` (17150), `showInstrucciones` (17969), `alertaDuelo` (17402), `_mesaSkinReapply` (9025)/`_bolaSkinReapply` (9155), `enterVR` (1858), `enterHall/exitHall` (20225/20339), `goHomeHall` (6438), `enterCalib/exitCalib` (1071/1110), `switchMode` (1333), `startOnlineSession/Match` (1367/1445), `buildMenu` (2051)/`menuClick` (7508)/`toggleMenu` (6361), `resetToss` (10254), `onSelectStart` (10279), `resetAllRecords` (9976), carrera `_carrera*` (9870).
- **Puente para campeonatos externos**: `window.__PP_CORE` (c13:4340, lectura: DIMS, stepPhysics, T…), `__PP_PADDLE_SWEEP` (c13:101), `globalThis.PP_SIGNAL_ENDPOINT` (c09:59).

### 3.4 · c13 — boot y módulos de UI
- Boot: `loadPaddleModel().then(...)` → `new PingPongGame(canvas#c, ...)` (c13:54-72); sin canvas no hay boot (guard r145). Expone `window.__game`, `__NetLink`, `__PPNET`, `__T/__setLang` y laboratorios QA headless (`__PP_SERVE_LAB` 119, `__PP_FEEL_LAB` 185, `__PP_CCD_LAB` 334, `__PP_GAME` 611) — los arneses los usan.
- ENTRADA EN UN TOQUE r152: la LANDING de la raíz (plantilla en deploy_pages.py) vuelve a ser LA PORTADA CLÁSICA (logo, palas de idioma escribiendo pp_lang, JUGAR EN VR) y llega con `game.html?vr=1` / `?ar=1` — c13 añade `#tapvr` (pointer-events:none) y un listener en window: CUALQUIER toque/tecla dispara `enterVR` directo (la activación del clic no cruza navegaciones — WebXR exige un gesto dentro del documento). El aviso se retira en onXRState(true); en escritorio sin WebXR queda en rojo con el mensaje atrapado.
- ARRANQUE r151 (c13, tras crear el juego): `game.enterHall()` SIN sesión VR — **el Hall del usuario ES la pantalla de entrada, la portada se retiró** (#overlay pasa a HUD mínimo transparente: PLAY IN VR compacto abajo, palas de idioma arriba-derecha, pie completo; CSS en 00_head). La sesión VR sigue necesitando un gesto → el botón compacto la pide igual que siempre (`enterVR(false, arPref)` c13:4075). Primer gesto 2D → `game.rearmHallAudio()` (c12, nuevo: el AudioContext solo nace en un gesto; setHallWanted sin ctx se descarta en silencio, c03:712). La cámara 2D del animate (bloque 8, c12:20124) tiene rama de salón: local (0, 1.55±vaivén, 0) mirando la pared frente de insignias (HALL.cz−2,4); el canvas hace fade-in con clase `.listo`. `enterVR` (c12:1858) prepara audio DENTRO del gesto y pide 'immersive-ar' si el casco lo soporta (alternar passthrough en AJUSTES sin cerrar sesión), optionalFeatures local-floor/hand-tracking/dom-overlay.
- **PP_TRAIN** Pro Training (c13:618-4034, `window.__PP_TRAIN`): entrenamiento estructurado con retos semanales (`_retosSemanaKey` c12:22771).
- **LA ACADEMIA** tutorial (c13:4373-6790): guion de 9 pasos sobre la mesa real con árbitro dormido vía `enterCalib`; muere con la sesión; oferta única `pp_tut_asked/done`.
- Menú VR: NO está en c13 — es el **arco de 3 panelas** de c12 (buildMenu 2051, lienzo virtual 3696×1400 troceado a 3 texturas curvas, yaw ±36°; hover `updateMenu` 6935, click `menuClick` 7508, chincheta `_menuPinToggle` 6915; vive en espacio MUNDO, inmune al recentrado, 2217). Raycaster del menú far 2,5 m — los rayos propios (hall, mapa de ruta) usan far mayor para no pisarlo.
- `onSessionStart` (c12:10016): perf por casco, passthrough, `rules.startMatch`, menú HUB abierto, oferta de ACADEMIA, altura auto sentado (`pp_hauto_v1`) y **`enterHall()` (10097)** — se nace en el salón (post-gesto: el AudioContext ya existe).

---

## 4 · Flujo completo de una partida (secuencia)

0. **LANDING-PORTADA (r152)**: la raíz /CrazyPP/ ES la portada clásica; su JUGAR EN VR lleva a `game.html?vr=1` → un toque en cualquier parte → VR (passthrough con `?ar=1`).
1. **URL → SALÓN 2D (r151)**: el boot llama `enterHall()` sin sesión — el salón es la pantalla de entrada; «JUGAR EN VR» (compacto) → `enterVR` (c12:1858) → requestSession.
2. `sessionstart` → `onSessionStart` (c12:10016): perf, passthrough, `rules.startMatch(mode)`, HUB, `enterHall()` — naces en el salón con bola/pala ocultas (`_hallHidden`).
3. **Menú arco** → ▶ JUGAR → `case 'start'` (c12:7717): `champs.leaveAll()` + `exitHall` → `rules.startMatch('match')` + `resetToss` (10254) → `closeMenu`. (`case 'survgo'` 7739 para supervivencia; online → `startOnlineMatch` 1445 con cuenta atrás `onNetMatchStart` 1498.)
4. **Saque**: bola en la mano libre; gatillo suelta (`onSelectStart` 10279 → `tossFromHand` 10607, asistencia por tier SERVE_ASSIST_TIERS); golpe con la pala (bloque 5).
5. **Rally**: `stepPhysics` (bloque 4) → eventos físico → árbitro `handleEvents`/`update` (c06:417/492) → intents → `processIntents` (c12:21086): punto, audio, stats, retos, marcador (HUD alimentado en bloque 7).
6. **Fin**: c06 detecta 11 con +2 (o serie), `state='over'`, intent `game-over` → telemetría, dilatación, fanfarria + banner de revancha (c08:2660) + confeti; online `sendMatchEnd`.
7. **Revancha**: auto-start a los 8 s SOLO local (c06:500; online el 'over' solo lo mueve un `mstart`, c12:19724) o botón del banner; ⌂ `goHomeHall` (6438) al salón.

---
## 5 · Física y colisiones (c04 + c05)

### 5.1 · Vuelo de la bola (c04)
- **RK4** `integraVuelo` (c04:289): gravedad + arrastre cuadrático + Magnus `a = Cm·(ω×v)` con `magnus 0.0035`; spin congelado en el paso, decaimiento aplicado UNA vez por paso (`spinDecayAir 0.3`, tope `spinMax 110` ≈ 1050 rpm, `spinImpulse 10` convierte barrido de pala en spin). `_aeroAccel` (c04:280) es la derivada compartida — UNA ecuación para física, predictor IA y solver (FIS1).
- **Subpasos**: `n = ceil(dt / MAX_SUBSTEP_DT)`, `MAX_SUBSTEP_DT = 1/480`, capado a 96 (c05:958). Cero asignaciones por frame (temporales preasignados c04:6-37).
- **Bote en mesa** `bounceOnTable` (c04:463): slip-coupled — rebote `vel.y = impact·tableRestitution`, deslizamiento del cascarón (ux = vx + r·ωz), agarre saturado `bounceGripMin 0.22 → bounceGripMax 0.60` (a 4,5 m/s), tope de Coulomb, acoplo Δω = (3/2r)·Δv. Impacto < `SOLVER_TUNE.mesaEnter 1.0` ⇒ **apoyo persistente** muelle-amortiguador (k 40000, c 200, μ 0.28, despega a 6 mm), no impulso. Ruta legada `applyBounceSpin` (c04:444) si `physicsRealism < 0.5`.
- **Los valores de `BOTE_TUNE` son el golden de trayectorias** (`test_fisica.mjs` manda) — moverlos cambia la sim: cada valor tiene comentario de por qué existe.
- **Pala** `updatePaddleSim` (c04:356): Kalman constante-velocidad por eje (KF_TUNE c04:132, gating de innovación), ω de muñeca por delta de cuaterniones, **cuarentena de glitch §7.5-LITE**: salto > `paddleGlitchSpeed 30 · dt` ⇒ ventana contaminada, buffer vaciado, `glitchT 0.10` que BLOQUEA contactos (c05:30).

### 5.2 · CCD y colisiones (c05)
- **CCD bola↔pala** exacta por **SDF** en espacio local de la pala (`sdfBlade` c04:146): el segmento se transforma a las poses τa/τb interpoladas y se resuelve «segmento+radio contra forma fija» con avance conservador (1-Lipschitz: nunca salta superficie), maxIter 32, eps 1e-5, rasante glaze 2e-4; `faceK 0.7` separa cara vs canto.
- **Contra qué colisiona la bola** (por subpaso, c05:961-1013): mesa `collideTable` (c05:502, **huella interpolada en la fracción de cruce** — r144 H1: evaluar con la posición de fin de subpaso perdía botes de smash y atribuía el punto al lado contrario, causaba disputas online), red `collideNet` (c05:643, banda interpolada igualmente, r144 H2), mundo `collideWorld` (c05:678, zona muerta 0.3, flag `__floorRest` = UN evento por aterrizaje), palas `collidePaddleSweep` (c05:24). Mesa y red desactivables (`ball.ignoreTable/ignoreNet`) para modos especiales.
- **Golpe** `collidePaddleSweep` (c05:24-445): margen = `hitAssistRadius + extraReach` + gracia de saque; restitución con punto dulce (`edgeRestLoss·offC²`), transferencia de cuerpo `padN·0.40` (r113), suelo de salida escalado con la velocidad de pala, dirección por swing (mezcla ≤45°, sólo jugador), spin desde superficie de contacto + reversión parcial −35 % del spin entrante, fricción de goma con tope, perks de skin (`PADDLE_PERKS` c04:508), Súper Imán como guía que reconstruye velocidad con `computeShotVelocityReal` (c05:406). **El evento paddle se emite SIEMPRE que la física aplica impulso** (flag `soft` < 0.35) — suprimirlo desincroniza `lastHitter` y el fantasma online (r144 H3). Tras el golpe, mesa/red se aplazan al siguiente subpaso (`padHit → continue`, c05:1002).
- **Rescate de bola perdida** (c05:755): teleport tras la línea de fondo, visible, SIN evento (es teletransporte, no bote).

### 5.3 · IA de golpeo (sin trampas)
- `predictStrike` (c05:1050): predice el MEJOR punto de golpeo — clona estado, simula a 1/240 con el RK4 compartido, cuenta botes propios (2 ⇒ urgente), puntúa por altura óptima y≈1.02 m y tiempo; fallback al plano trasero.
- `computeShotVelocityReal` (c05:1226): solver de tiro con física real — parábola balística sembrada y corrección POR SIMULACIÓN hasta botar a ±1,5 cm del objetivo con despeje de red garantizado (+0.085 sobre netTopY); 16+4 iteraciones, caché LRU de 96 claves a 1 cm, devuelve clon.
- La cfg IA: `CONFIG_DIFICULTAD.presets` → `scalePreset(cfg, k)` (c02:355) → `estiloAplicar(cfg, estilo)` (c02:468, 12 personalidades) → tabla `esfuerzo` gobierna el fallo decidido. Velocidad clampada por el solver legal; palas ancladas a su mitad.

---

## 6 · Árbitro, reglas y modos (c06)

### 6.1 · La clase `Rules` (c06:177)
- Estado: `mode` ('match'|'survival'|'duelos'), `state` ('serve'|'rally'|'point'|'over'), `server`, `scorePlayer/scoreAi`, `gamesPlayer/gamesAi/gameNo/bestOf` (mejor de 3 en partida libre), `rallySeq`/`_appliedRally` (identidad del rally, r79), `mStats {vmax, bestRally}` (r95) y `mHeat` rejilla 3×3 de botes perdidos (r97), `firstServer/gameOpener`.
- **`handleEvents(events)`** (c06:417): consume los eventos de c05 — `'paddle'` (registro de golpeo; doble golpe = falta `'dblhit'`; la volea la juzga el árbitro de esa mitad, r81 — un golpe REMOTO llega ya validado, el juicio local de voleas remotas daba faltas falsas), `'net'` (netTouched → LET en saque), `'table'` con `e.side` (máquina de estados del bote: `serveOwnPending → mustBounceOpp → validBounce`; bote propio en saque = falta `'serve_no_own'`; doble bote `'dbl_opp'`; back `'back_you'`), `'floor'/'wall'` (out/noret con causas 'serve_net'/'serve_out'/'net_stay'/'wall'). Sale del bucle cuando el estado deja de ser 'rally' (un punto por rally).
- **`applyPoint(winner, cause)`** (c06:336): guardia anti-duplicado por `rallySeq` SOLO con red v2; `_applyPointSinGuard` aplica el punto (survival: sin puntos, cuenta rallyes; match: score++).
- **`forcePoint(winner, cause, rallyId)`** (c06:387): PUNTO IMPUESTO POR LA RED (CLAIM del extremo con autoridad) — **fail-closed r140/r141**: `Number.isInteger(rallyId)` obligatorio (2.5 burlaba la guardia y duplicaba puntos), idempotente por `_appliedRally`.
- **`computeNextServer()`** (c06:398): rotación RELATIVA AL ABRIDOR del juego (`gameOpener`, r82) — en el invitado el abridor es 'ai' en SU perspectiva; la fórmula antigua hardcodeada daba el sacador al revés y ATASCABA el partido online (dos bolas HELD, cazado en vivo). Deuce: alterna cada punto (`saqueIguala 1`).
- **`update(dt)`** (c06:492): temporizadores — 'point' → pausa → serve (survival nunca acaba); detección de fin 11/+2 (c02 datos); serie mejor-de-3 con `serieFactor`; 'over' → auto-reinicio en el MISMO modo tras 8 s (solo local) con `onMatchStart`.
- **`beginServeRally(server)`** (c06:300): `rallySeq++`, resetea flags de rally. **`resetGame`/`startMatch`** (238/260): ITTF — cada juego saca el otro; `startMatch` normaliza 'duelos' y resetea mStats/mHeat/rallyesSurvived; UN SOLO punto de aviso `onMatchStart` para TODOS los caminos (v3.6.39).

### 6.2 · GameStats y recompensas (§13) y el motor de IA rival (c06:752-1824)
- `GameStats` (c06:27): `recordPoint(winner, rallyHits)`, `recordRally`, `recordSurvivalRally`, `recordMatch(win, dificultad, info)`, `unlock(key)` — persistencia localStorage, alimenta logros e historial.
- IA rival avanzada (cadenas de golpes): `_rollCadena/planCadena/_armaCurva/cadenaContacto/updateCadena` (c06:804-1212) — planifica secuencia de golpes con curvas simuladas; `mishit` (c06:1768). Se alimenta de c05 y CONFIG_DIFICULTAD.

### 6.3 · Los modos de juego
| Modo | Qué es | Puntos de entrada |
|---|---|---|
| **Partido libre ('match')** | 11 con +2, mejor de 3 si `bestOf>1`, ELO y matchmaking | menú ▶ JUGAR (`case 'start'` c12:7717) |
| **Supervivencia ('survival')** | sin puntos: la CPU acelera +0.08/rallye (techo 2.1); récord `ppxr_surv_best` | `case 'survgo'` c12:7739 |
| **Duelos locos ('duelos')** | misma puntuación que match + poderes `_dl*` | `_dueloArrancar` c12:1394 |
| **Entrenamiento** | PP_TRAIN (c13:618), retos semanales, heatmap | menú Entrenar |
| **La Academia** | tutorial 9 pasos, árbitro dormido (`enterCalib`) | oferta única tras HUB |
| **Carrera/ELO** | divisiones `CARRERA_DIVISIONES`, rival por ELO, WORLDRANK | menú carrera (c12:9870) |
| **Campeonatos** | ver §8 — 6 mundos con etapas y pruebas | botón CAMPEONATOS del menú |

---

## 7 · Red multijugador (c09 + c09b + c09c + worker + broker)

### 7.1 · NetLink (c09) — salas y transporte
- `NetLink` (c09:1): `peer` (PeerJS), `conn` DataConnection, `call` MediaConnection + `micStream/remoteAudio` (**voz en el juego**), `role 'host'|'guest'`. Sala **PRIVADA por defecto** (r74): solo `vis='pub'` sale en el listado público; modalidad y visibilidad viajan en el latido de presencia.
- Señalización: cloud de PeerJS por defecto, o broker propio con `globalThis.PP_SIGNAL_ENDPOINT = 'https://dominio/peerjs'` antes de host/join (peer-server/server.js:17-26). El cliente no cambia de protocolo.
- Sesión: `startOnlineSession` (c12:1367) crea sala / muestra el HUB de salas; `startOnlineMatch` (1445) → `onNetMatchStart` (1498) con cuenta atrás sincronizada; presencia via worker (§14).
- **F1 intruso**: una tercera conexión es rechazada (arnés test_r146 lo ampara: intruso, colisión de sala, bye, muerte del broker).

### 7.2 · PPNET (c09b) — núcleo binario (r79, spec v1.0 dictada por el dueño)
- **Principios**: 1) el golpe propio es SAGRADO (se resuelve local sin esperar red); 2) **AUTORIDAD POR MITAD DE MESA**: quien tiene la bola en SU mitad decide botes, fallos y puntos de esa mitad.
- Claims/ACK con `rallyId` = `rallySeq` (identidad del rally, c06:300); el árbitro aplica el claim ajeno con `forcePoint` (fail-closed entero, idempotente). Espejo de marcador, pausa, revancha y `sendMode`/`sendDueloPower` viajan por el mismo canal binario.
- **Watchdog + resync**: la batería multipartida ampara canal adverso, resync-req, watchdog y REPROS r140 (test_r130_multipartida, 206 escenarios). Extrapolación de pose con `VP.EXTRAP_MAX` (c09b:543).
- **Convención de perspectiva**: el ganador siempre 'player'|'ai' en local; el invitado remapea causas; `oppLabel` es clave i18n ('cpu'|'rival'). La rotación de saque deriva del `gameOpener` de cada extremo (r82) — jamás hardcodear 'player'.

### 7.3 · RedSocial (c09c, r87) — El Pulso
- Medallón con el número de jugadores online + buzón de invitaciones con código. Backend = worker: `/api/presencia` (latido TTL 90 s con token anti-suplantación) y `/api/invita` (buzón de 5, con `?tok=` o `X-Tok`). Detalles del worker en §14.

### 7.4 · Cómo tocar la red sin romperla
1. Cualquier cambio de protocolo debe pasar por la **spec §7 y los claims**: versiona el mensaje, mantén fail-closed (sin rallyId entero no se aplica punto), y añade el escenario al arnés multipartida (test_r130) y al vivo (test_r146, requiere `ws` + `peer` instalados y arranca su propio broker :3005 con `pkill PeerServer` previo anti-EADDRINUSE).
2. El 'over' online solo lo mueve un `mstart` — nunca el auto-reinicio local.
3. La voz usa MediaConnection aparte; su micStream se corta en leave/disconnect.

---
## 8 · Campeonatos (c11 + public/championships/)

### 8.1 · El loader `ChampLoader` (c11)
- `_loadIndex()` (c11:69) lee `championships.json` — **el núcleo SOLO importa lo listado ahí**. `isLocked(id)` (30) gestiona candados (`candados ['estacion_orbital']` en CONFIG_TORNEOS). Carga dinámica: `await import('./championships/${id}/index.js')` (c11:268) — **superficie de contenido externo: cualquier dato del módulo lleva guard** (F-A2).
- Ciclo de vida: `launch` del módulo corre DESPUÉS de `leaveAll()` y antes de start. **`leaveAll()`** (c11:658) es el cerrojo universal de salida: libera `game.champDecorHidden` SIEMPRE (autocuración r60), llama `mod.leave()` + `mod.musicOff()` si existen (r97: candado universal — los one-shots/bucles del módulo mueren al salir aunque su reloj haya muerto), retira la voz publicada (`window.__PP_ARCADE_DATA.__ppCoreVoz` / `__PP_CHAMP_PERS`), re-aplica la skin de mesa elegida (`_mesaSkinReapply`). Intros: `introShown/introClosed` (c11:705/711) con hook opcional `champIntroPause(bool)` del módulo (la BSO se silencia durante el vídeo de la historia). `resetRecords()` (c11:725) pide `mod.resetRecords()` a cada módulo cargado Y borra físicamente toda clave `pp_champ_*` de localStorage (v2.68/2.69).
- Rejugabilidad: `replayMap/replayHover/replayLaunch/replayConsume` (c11:750+, el póster del camino con nodos en píxeles del arte; rayo de la pala, radio ×1.22, desactivado durante la intro). `_updateReplayPick` usa `rpRaycaster` de c10 (far 9).
- Delegación con guard (c11:962-981): `update/onPoint/onMatchOver/menuAction/leaveAll` — un módulo sin un hook simplemente no participa; los hooks JAMÁS rompen el núcleo.
- **C-F1 (segunda oportunidad, r147/148)**: al perder una prueba del camino, la siguiente jugada repetible es SIEMPRE la prueba jugada (convenión `stageClear(idx, won, 'duelo')`); amparado por test_r147 (gemelo magia, 20 OK) y test_r148 (sweep de 4 campeonatos + ciclo de rejugada de oeste, 15 OK).
- Pistas de filtro: `splitFilterEvents/updateSplit` (c11:648/652) — eventos de UI que solo el campeonato consume.

### 8.2 · El contrato de un campeonato
- **Estructura**: `public/championships/<id>/{manifest.json, index.js, assets/}` — la config del artista vive DENTRO del manifest (bloques «cfg» en locura, «level» en magia; data.json retirado).
- **manifest.json** (contrato 1 + bloques unificados, validado por `championship.schema.json`): `id` (=carpeta, inmutable), `version`, `contract: 1`, `estado` (borrador→validacion→listo→**publicado**→desactivado; solo 'publicado' sale en el menú), `title/description {es,en}`, `tema`, `rival {id, name, kind, states[], oppLabel, personalidad{agresividad,precision,constancia 1..5}}`, `storage` (`pp_champ_<id>_*`; locura usa `pp_arcade_*` por legado), `audio {music, musicVolume, sounds{}}`, y los bloques unificados (`camino` con `patron: "duelo_prueba"` que genera duelo1→prueba1→…→final, coronación, RUTA LEYENDA, bolsa rotatoria de poderes, pistola opcional, mapa arte|canvas, i18n). La plantilla COMPLETA comentada: `public/championships/_plantilla/manifest.json`; la guía: `PLANTILLA-GUIA.md`.
- **index.js** (módulo ES): exporta el objeto del campeonato. Ganchos usados por el núcleo: `launch(game)` / `leave()` / `musicOff()` / `resetRecords()` / `update(dt)` / `onPoint(ev)` / `onMatchOver` / `menuAction(id, act)` / `replayMap()` / `champIntroPause(bool)`. `decor.pieces` = troqueles `{file, x, z, h, sway}` (rutas relativas a `championships/<id>/`; **sway SIEMPRE definido** — guard F-A2 c07:1387). Puede pedir al núcleo: `setArcWanted` (BSO), `setHallWanted`, poderes vía triggers de `_megaMatriz`, `window.__PP_CORE`.
- **Rivales**: sprites `assets/<estado>.webp` por `rival.states` (el rico usa 12: present, idle, focused, surprised, hungry, panic, laughing, crazy, angry, picando, loosing, defeated, victory); motor de expresiones por umbrales de `rival.expresiones`; `kind: stock|clown|wizard|forajido` — y la **convención del ganador**: las reglas envían 'player'|'ai' (el FIX CRÍTICO v3.2 de estacion nació de tratar 'rival' como booleano).

### 8.3 · Fábrica oficial (r25, generalizada de valle_neon)
```bash
# 1) arte con los nombres exactos de _plantilla/assets/LEEME-ARTE.txt
#    (mínimo: 6 paredes de sala + rival + estados + bso + insignia)
python3 scripts/gen_campeonato.py --id bosque --titulo-es "Bosque Encantado" \
    --rival-nombre "DRÍADA" --dificultad media --arte ./mi-arte/
python3 scripts/qa_plantilla.py public/championships/bosque   # validación
python3 scripts/gen_campeonato.py --id bosque --titulo-es "Bosque Encantado" --registrar
#    (estado 'borrador' = invisible en el menú; pasar a 'publicado' al final)
```
El generador copia el módulo, sustituye MOD_ID, adapta manifest, copia arte por nombre convencional, **desactiva la pistola sola si falta pistol.glb** y ejecuta el validador.

### 8.4 · Los campeonatos vivos
| id | manifest v | Notas |
|---|---|---|
| oeste | 56 | el más rico (duelos con pistola) |
| magia | 32 | física de vaivén propia (`swayAmp/swayFreq`), gemelo QA r147 |
| locura | 23 | el ORIGINAL; rival zombi con one-shots (lección r97); storage legado `pp_arcade_*` |
| estacion_orbital | 16 | recortables reales del dueño (decor v3.2.0); FIX CRÍTICO v3.2 del ganador |
| valle_neon | (Taller V3.0.3) | prueba de concepto data-driven (100% manifest) |
| halloween | 3 | el más reciente; fix F-O1 (r148): stageClear en el camino de derrota del duelo |
| _plantilla / sdk | — | plantilla de fabricación / SDK `champ_sdk.js` (qa_version cruza `SDK_VERSION`) |

---

## 9 · Audio y voz (c03)

### 9.1 · Canales e invariantes
- Canales independientes sobre un AudioContext único (`kick()` lo crea dentro del gesto): **música de menú** (`musicWanted/musicPlaying`, `setMusicWanted`), **música del salón** (`hallWanted/hallMute/hallPlaying`, pista por URL con caché), **BSO de campeonato** (`setArcWanted`, con `_arcDucked` — el duck del núcleo se arma aunque la pista siga cargando, v2.122), **one-shots/SFX** y **voz**.
- **INVARIANTE UNA MELODÍA**: jamás dos pistas a la vez. Sentido SALÓN→menú: `startHallMusic` retira la del menú — **r149 F-A1**: la petición se RECUERDA (`_menuReq = this.musicWanted` antes de consumirla) para que el icono de mute de la pared pueda devolver el aire (`setHallMute(true)` → `setMusicWanted(true)` re-arma y nace — `startMusic()` a secas NO basta: exige musicWanted); la recuerda EXPIRA al salir del salón (`setHallWanted(false)`) o ante petición fresca del menú (`setMusicWanted(true)` la limpia). Sentido inverso: `startMusic` NO nace si el salón suena (`hallWanted && !hallMute → return`, c03).
- Todos los caminos del menú emparejan `setMusicWanted(true)` con `setArcDuck(true)` (c12:6391/6405/6411, c13:6627).
- **LRU de AudioBuffers tope 3** (v3.6.142): cada buffer son PCM — la caché por URL evita re-descargas al alternar salones; paradas con fundido (`stopHallMusic/stopMusic`: rampa a 0.0001 + stop diferido con setTimeout).
- **El audio NUNCA rompe el juego**: `Number.isFinite` en TODOS los parámetros de playOsc/playNoise/panNode (un NaN lanzaba TypeError y mataba el frame — el guard de referencia del repo) + try/catch total en cada canal.
- Voz: banco base64 externo `assets/audio/voz_*.json` → `pp-voz-lista` → `reloadVoice`; tras re-vinculación de contexto `tryFreshRunning/adopt` rearranca la pista del salón (c03:884). El guard `typeof VOICE_B64S` de c03:1727 es seguro. Sin `__PP_CORE` disponible, el bloque rico de La Locura gestiona lo suyo (leaveAll no lo toca).

### 9.2 · Recetas
- Nueva pista de salón: `setHallWanted(true, 'assets/hall/<id>/arcade.mp3')` — el resto (caché, fundidos, prioridad) es automático.
- SFX nuevo: tabla del canal correspondiente en c03 con `Number.isFinite` en cada parámetro.
- Cambiar volúmenes: `CONFIG_AUDIO` (c02:1228 — `salon {base, entradaS, salidaS}`, `musica {base, entradaS, salidaS}`).

---

## 10 · Sala, escena, skins y troqueles (c07)

- **Sala** `createRoom` (c07:1): suelo con GridHelper, 4 paredes con material propio cada una (`wallMats` [izq, der, trasera, frontal] — los campeonatos las visten plano a plano), techo, paneles, tiras LED; todo en `g.userData` para `applyTheme` (ROOM_THEMES).
- **Mesa** `createTable` (c07:93): piezas con nombre `ppTable*` (contrato para teñidos); `relayoutMesa` (c07:203) reacomoda la mesa VIVA al cambiar `DIMS.tableTopY` sin reconstruir (patas con `userData.h ∈ [0.65,0.79]`, red conserva `MESA_NET_H 0.1525`).
- **Skins**: `MESA_ASPECTOS` tiñen ppTableTop/Apron/Leg; `BOLA_ASPECTOS` (16) cambian SOLO material vía `applyBallSkin` (c07:419; nunca física) — texturas **procedurales** pintadas en canvas por `bolaTex` (c07:245, RNG de semilla fija, costura + marca "CRAZY" para que el giro sea legible, aro de Saturno). Cero bytes de textura en el bundle.
- **Bola y estela**: `createBall` (c07:453) + estela de 22 puntos coloreada por efecto (naranja topspin / azul backspin / violeta lateral).
- **Partículas en pools fijos** (cero asignaciones por emisión): chispas (c07:539), cometa de 3 capas (c07:628), nube de prismas InstancedMesh (c07:785), onda-escudo de pentágonos (c07:928), cristales de criptonita (c07:1037, con **vigilante r110 de destrucción garantizada**: `fin()` arranca plazo duro y `pendientes()` mantiene el update hasta limpiar — el patrón para cualquier efecto con limpieza asegurada).
- **champDecor** (c07:1254): troqueles de cartón por campeonato — lee `mod.decor.pieces`, planos con pivote en base + caballete + blob-shadow, anclados al RIG orientados al jugador; interactivos sin tocar física (la bola cerca o la pala los tambalea: muelle amortiguado + "toc" + háptica); sway sutil en reposo — **guard F-A2** (`p.cfg.sway != null ? p.cfg.sway : 0.5`, c07:1387 — un pack sin sway corrompía rotation.z con NaN CADA frame); reconstrucción perezosa por campeonato (`builtFor`), dispose completo del set anterior, visible SIEMPRE incluso con passthrough (lección r70, c07:1367-1374).

---
## 11 · UI: arranque, salón, HUD y menús (c08 + c13)

- **c08 pintores de pared** (canvas 2D→textura): `hallCanvas` (28), `drawHallSign/Musica/Gloria/Door/Header/Medal/Ranking/Nameplate/Neon/Quote` (37-457). `createHall(base)` (473) construye la estancia (`HALL`, cz −18,5) con arte por variante: museo `assets/hall/` o CABAÑA `assets/hall/cabana/` (HALL_VARIANTES); placa de insignias, icono de música en la pared frontal, cuadro del Arcano, carteles «EL PULSO CRAZY»/«TU RACHA». Devuelve `userData.hall` (922-935). `applyHallVariant` (945) re-viste en vivo (`hallv:<id>` desde menuClick c12:8540); `updateHallFx` (960) corre desde animate sólo con el hall visible.
- **Salón Arcano**: `montarArcano` (c08:1575) + `updateArcanoFx` (1773); se entra con `_arconoEntrar` (c12:9641). **Prioridad de rayos/gatillos** (respetar SIEMPRE): Arcano > alerta duelo > menú > cartel instrucciones > intro campeonato > academia; el icono de música de la pared usa rayo propio `_hallMusicaRay` far 10 m (c12:9319) para no pisar el far 2,5 del menú.
- **HUD**: `createScoreboard` (c08:2331) — panel 1024×512 sobre la pared frontal con `update(d)` **deduplicada por clave de estado** (survival vs match con games/ping/oppLabel); se alimenta del bloque 7 del animate. `createFanfareBanner` (2660: cartel de fin con chip marcador + revancha), `createConfetti` (2831), `createBounceMarkers` (2313), `createCalibPanel` (2492), `createChampRoom` (2100). `drawHall` (c12:20541) repinta los lienzos vivos.
- **Cambio de salón/música**: picker de salones (`setHallWanted` con pista por salón, c12:8564/9108-9131), icono de música de la pared (`_hallMusicaPulsa` c12:9337 → `setHallMute`, persistente `pp_hallmus`).
- **Preferencias (localStorage `pp_*`)** — mapa completo: `pp_player_name`, `pp_pid` (identidad), `ppxr_dif/_theme/_trail_v1/_adapt_v1/_surv_best/_pending_ar`, `pp_mesaalto/pp_mesaskin/pp_mesaaltoy`, `pp_bolaskin`, `pp_rivstyle_v1`, `pp_estilo_v1`, `pp_pala_mejorada_v1`, `pp_poderes_v1`, `pp_hauto_v1`, `pp_seen_v1`, `pp_hapt/pp_tips_v1/pp_alertas_v1`, `pp_srv_v1`, `pp_mega_norm_hint`, `ppxr_train_v1`, `pp_train_barra_v1`, `pp_tut_asked/done`, `pp_heat_v1`, `pp_hallmus`. Convención: claves "una sola vez" para ofertas (`pp_tut_asked`).

---

## 12 · Logros, recompensas y estadísticas

- **Catálogo data-driven**: `CONFIG_LOGROS.core` (c02:1322-1344) = 6 medallones `{key, emoji, nameKey, descKey, cond:{tipo, valor}}` (primera, racha3, gigante=victoriaEn hard, maraton=rallye 20, superviv=mejorSupervivencia 25, aces10) + `train` = 10 honores PRO TRAINING. `ACHIEVEMENTS` (c06:1) se DERIVA — añadir fila basta para el catálogo; textos `ach_*` en c00; disparo de la condición en `GameStats` (c06:27) con `COND_LOGRO(key)` (c06:24) leyendo el dato.
- **Estadísticas de partido**: `mStats {vmax, bestRally}` (r95, «estadísticas al final de cada duelo», alimenta la fanfarria) y `mHeat` 3×3 (r97, «zonas donde pierdes puntos» — histórico en `pp_heat_v1` vía c12). Precisión al final: sale del marcador.
- **Economía de recompensas**: skins de mesa/bola con `lock` ('wins10'/'streak5') y `coste`; poderes desbloqueables persistentes (`pp_poderes_v1`, carga por rally 11+); circuito de campeonatos (niveles de puntos, combo x2/x3, estrellas en CONFIG_TORNEOS.circuito); placa de insignias del salón (c08); historial de torneos (`historialTorneos` c11:550); rankings por ELO (carrera `CARRERA_DIVISIONES` 5 divisiones × 3 rivales, `WORLDRANK`, y rankings del worker `?rank=1` por pid).
- **Telemetría como reccompensa/QA**: todo evento clave sale por `__PP_TELE` (c00) al endpoint (worker en producción, receptor Next en local) — jamás rompe el juego (try/catch, c12:21391).

---

## 13 · Infraestructura y despliegue

### 13.1 · Mapa de producción
| Pieza | Dónde | Qué sirve |
|---|---|---|
| Juego estático | GitHub Pages, rama `pages` (commits HUÉRFANOS, push --force), `https://franjavierdavila.github.io/CrazyPP/` | game.html, championships/, assets/, vendor/, sw.js, telemetria.html, actualizar.html, PAGES-VERSION.txt |
| Worker Cloudflare | `crazypp-tele.escala3dcorreoia.workers.dev` | telemetría, red social (presencia/invitas), ICE/TURN, salas públicas |
| Caddy del dueño (:81) | proxy | defecto → `localhost:3000` (Next HUB); `?XTransformPort=3004` → live-service (único puerto admitido por query — fix SSRF r128); `/peerjs/*` → `localhost:3005` |
| live-service (:3004) | Bun + socket.io | relay tonto de CRAZY TV: HOST publica (`publish`), emite `state` ~30 Hz sellado con reloj del servidor (`state.t`) para interpolación común + `event` discretos; espectadores `watch/leave-watch`; canales fantasma fuera a los 12 s; anti-secuestro `owner = socket.id` (r112) |
| peer-server (:3005) | node + `peer` ^1.5.4 | broker PeerJS propio (mismo protocolo que el cloud); activar con `PP_SIGNAL_ENDPOINT` |
| HUB Next (:3000) | src/app | telemetría (panel dual con sparkline, X-Clave), descargas (4 ZIPs + banner TV), receptor `/api/telemetria`, proxy `/api/channels` → :3004 |

### 13.2 · Worker-tele (`scripts/worker-tele/worker.js`, 1586 líneas) — API completa
| Ruta | Método | Auth | Función |
|---|---|---|---|
| `/api/tele` | POST | ninguna | lote `{app, events}` ≤256 KB, evento ≤2000 B, lote ≤500; respuesta **204 sin cuerpo**; evento inválido se descarta sin romper el lote |
| `/api/tele` | GET | pública | latido `{ok, total, ts}` (caché 60 s); `?salud=1` LED del panel; `?resumen=1` agregados + alarmas (CLAVE); `?eventos=N` crudos (CLAVE); `?csv=1` export (CLAVE, máx 50.000 filas); `?rank=1` rankings por pid (CLAVE); `?salas=1` salas públicas vivas |
| `/api/tele` | DELETE | CLAVE | purga por `?sid=` / `?dias=N` / total |
| `/api/ice` | GET | pública | TURN efímero Cloudflare Realtime (TTL 21600 s) o ruta Metered; caché 4 min; degradación limpia a STUN; campo `fuente` |
| `/api/presencia` | POST/GET | ninguna | latido TTL 90 s con token anti-suplantación (devuelve `tok`); `{pid, bye:1}` baja; GET contador y `?lista=1` jugadores (código de sala solo si vis='pub') |
| `/api/invita` | POST/GET/DELETE | token de latido | requiere sala viva del remitente y latido vivo del destinatario; buzón de 5; GET/DELETE con `?tok=` o `X-Tok` |

- **Auth CLAVE**: `env.CLAVE` por `?clave=` o cabecera `X-Clave`; POST sin clave (el juego es público y no guarda secretos); 30 fallos/min → 429.
- **Cuotas** (memoria del isolate): POST 2000 req/min y 20.000 filas/min global, 300/min por sid, 2000/min por IP; social 60/min por pid; invitaciones 120/min global, 10/h por remitente, 8/h por destinatario. Purga social perezosa 1 de cada 20.
- **D1** (auto-CREATE): `eventos(id, e, t, v, sid, json, rec)` + 3 índices; `presencia(pid, n, v, st, code, mj, vis, token, t)`; `invitas(id, de, deN, para, code, mj, t)`; `cfg(k, v)`. Los DROP de migración legacy NO viven en el worker (un isolate nuevo los re-ejecutaría).
- **Cron retención** `"37 4 * * *"` (wrangler.toml:17): purga eventos > 30 días.
- **Variables**: `CLAVE` (secret), binding `DB` (D1 crazypp-tele), `TURN_API_TOKEN` (+TURN_KEY_ID/SECRET opcionales, auto-provisiona y guarda en `cfg`), `CF_ACCOUNT_ID`, `METERED_APP`/`METERED_API_KEY` (ruta TURN sin coste), `ICE_TTL_MS`.

### 13.3 · PWA y caché (public/sw.js)
- `const CACHE = 'crazypp-v3.6.233-SDK6'` — el bump parchea el sello: cambiar el byte actualiza el SW y `activate` purga cachés viejas (invalidación automática). Install precachea solo la CÁSCARA (game.html, manifest, logos). Fetch: **game.html RED-PRIMERO con límite 4 s** (r98: el dueño veía siempre la copia vieja con SWR); datos vivos (`championships/`, `ugc/`, PAGES-VERSION.txt, telemetria.html) NETWORK-FIRST; resto CACHE-FIRST con relleno al volar. Solo GET same-origin (worker y PeerJS pasan de largo). Activate: claim inmediato + purga diferida a los 5 min (r96).

---
## 14 · Versionado, sellado y release (punta a punta)

1. **`python3 scripts/bump_version.py X.Y.Z-NAME [--fase N --fase-nombre ... --sdk ...]`** — ÚNICO camino legítimo de versión. En una pasada asertada: verifica sellos actuales (aborta si hay edits a mano), parchea los **4 sellos físicos** (`const VERSION` en c00, badge `#verBadge` en 03_body.html, menciones del hub descargas, `const CACHE` de sw.js), reescribe VERSION.json, regenera game.html (`build_game.py --escribir`), refresca GOLDEN + golden/tamano y contra-verifica BYTE-EXACTO.
2. **QA verde** (§15) antes de continuar.
3. **`gen_release_vXXXX.py`** (patrón: hereda del release anterior con copytree, reescribe cuerdas/notas) → `build_zip.py` produce los **4 ZIPs** en `public/descargas`: COMPLETO (~186 MB), ligera sin championships (~58 MB), CLOUDFLARE (estático puro), live-service-SOLO (~6 KB).
4. **Commit + push** (con escaneo de secretos ANTES: `grep -rn "github_pat_\|ghp_\|sk-\|AKIA"` sobre los ficheros del commit — los hits históricos del worklog sobre gestión de tokens y los WAV base64 de c03 son conocidos, sin secretos vivos).
5. **`GIT_TOKEN=… python3 scripts/deploy_pages.py --push --release --backup`** — ensambla `pages-site/` desde `git archive HEAD` (solo ficheros trackeados), verifica sellos EN EL SITIO ensamblado (aborta si el commit olvidó un fichero), 2 reescrituras contadas ruta absoluta→relativa, genera index + .nojekyll + **PAGES-VERSION.txt** (versión, commit fuente, game_sha256, fecha), smoke Playwright en :3006 bajo `/CrazyPP/` (0 pageerrors/4xx), commit huérfano. `--push` exige GIT_TOKEN y fuerza `refs/heads/pages`; `--backup` empuja `main:proyecto`; `--release` crea tag `v<ver>` + GitHub Release con EXACTAMENTE 4 ZIPs (asset cambiado de tamaño ⇒ el viejo se renombra `ANTIGUO-`, el PAT no puede borrar). `--backup` sin `--push` NO publica.
6. **Si tocó el worker**: `CF_API_TOKEN=… python3 scripts/deploy_worker.py` — re-entrante (verifica token, localiza cuenta, reutiliza/crea D1, preserva secrets con keep_bindings, sube módulo, fija CLAVE por endpoint de secrets y la guarda UNA vez en `scripts/worker-tele/.clave-produccion` 0600 gitignored, activa subdomain, fija cron, E2E real con curl + UA de navegador — workers.dev bloquea urllib con error 1010).
7. **Verificación CDN post-deploy**: `curl -s …/CrazyPP/PAGES-VERSION.txt` (versión + commit fuente) y `curl -s …/CrazyPP/game.html | grep -c '<marcador del cambio>'` (p. ej. r149: `_menuReq` ×6 y `sway != null` ×1).

Notas críticas: el commit huérfano de pages necesita `--force` SIEMPRE (es raíz); el push a main en este sandbox usa el PAT por URL (persistido en `scripts/worker-tele/.github-pat` 0600 gitignored) o GIT_TOKEN; el reciclaje del sandbox puede REBOBINAR la historia git local (el contenido del árbol permanece — verificar que los fixes siguen en el fichero antes de re-trabajar; push `-f` de HEAD:main).

---

## 15 · La batería de calidad (arneses)

**Regla del repo**: defecto cazado ⇒ arnés reproducible en `scripts/`. Método de extracción: se ejecuta el CÓDIGO REAL del juego (funciones/métodos extraídos con Regex de llaves balanceadas) sobre mocks mínimos (AudioContext simulado, THREE MathUtils, etc.) — los arneses de núcleo NO renderizan.

| Arnés | Checks | Qué cubre |
|---|---|---|
| `qa_version.py` | 31 | sellos de versión c00/badge/hub, sw.js, manifest PWA, 5 manifests, SDK_VERSION, golden triple-cruce, ensamblador byte-exacto, servidores vivos |
| `test_red_nucleo.mjs` (PPNET r82) | 60 | núcleo binario: claims, ACK, watchdog, extrapolación |
| `test_r128_claims.mjs` | 22 | claims verificados/fail-closed (auditoría r120 A1) |
| `test_r130_multipartida.mjs` | 206 | MULTIPARTIDA COMPLETA: arranque, rallye, claims, revancha, guardas, espejo v1, pausa, duelos, partida completa, canal adverso, resync-req, watchdog, REPROS r140 |
| `test_worker_r169.mjs` | 25 | worker: rutas, saneo, cuotas, ICE, CSV |
| `worker-tele/test_local.mjs` | 109 | worker local: D1 simulada, social, invitaciones, retención |
| `test_r146_peerjs_vivo.mjs` | 21 | broker REAL en :3005: sala, join, intruso F1, colisión, bye, muerte del servidor (requiere `ws`+`peer`; pkill PeerServer anti-EADDRINUSE integrado) |
| `test_r112_live_service.mjs` | — | relay TV: publish/state/event/ghost/owner |
| `test_r129_signal.mjs` | — | PP_SIGNAL_ENDPOINT |
| `test_r147_gemelo_magia.mjs` | 20 | gemelo QA + C-F1 REAL en magia |
| `test_r148_campeonatos.mjs` | 15 | sweep C-F1 de 4 campeonatos + ciclo rejugada oeste |
| `test_r149_nucleo_ligero.mjs` | 14 | F-A1 máquina de música REAL (6 escenarios) + F-A2 guard sway |
| `test_fisica.mjs` / `test_fisica_c05.mjs` / `test_fisica_perf.mjs` | — | golden de trayectorias (BOTE_TUNE manda), c05, rendimiento |
| `qa_rendimiento.py` / `qa_telemetria.py` / `qa_sup1_v366.py` | — | presupuesto de rendimiento, telemetría de catálogo, supervivencia |
| `test_encode_nan.mjs` | — | guardas NaN |
| Serie histórica `test_r21…r45_*.mjs` + `qa_r46…r119` | — | regresiones por ronda, TODAS verdes; no se borran |
| `qa_plantilla.py` | — | validador de campeonatos (arreglo de la fábrica §8.3) |

Batería principal r149: **523 checks verdes** (206+109+60+31+25+22+21+20+15+14). Ejecución de la pasada completa:
```bash
python3 -I scripts/qa_version.py
node --no-warnings scripts/test_red_nucleo.mjs
node --no-warnings scripts/test_r128_claims.mjs
node --no-warnings scripts/test_r130_multipartida.mjs
node --no-warnings scripts/test_worker_r169.mjs
node scripts/worker-tele/test_local.mjs
node --no-warnings scripts/test_r146_peerjs_vivo.mjs
node --no-warnings scripts/test_r147_gemelo_magia.mjs
node --no-warnings scripts/test_r148_campeonatos.mjs
node --no-warnings scripts/test_r149_nucleo_ligero.mjs
```
(`python3 -I` para los que leen ficheros externos; timeout 60-480 s según arnés.)

---

## 16 · Historia de lecciones — la familia de bugs y sus reglas

**(ESTA SECCIÓN ES LA MÁS IMPORTANTE: cada regla nació de un bug real en producción o en headset. El worklog.md tiene el relato completo.)**

1. **Estado pegajoso** (la familia que más daño ha hecho): un camino de entrada activa algo que su camino inverso necesita y no restaura.
   - r60: `champDecorHidden` quedaba PECHO al salir a mitad de prueba → troqueles invisibles en TODOS los escenarios → autocuración en `leaveAll` SIEMPRE (c11:658).
   - r97: «salí al Hall y seguía escuchando al zombi» → one-shots que son bucles cortados por un reloj que solo corre desde update() → `musicOff()` universal en leaveAll + módulo corta su tren en su leave().
   - r148 F-O1: halloween no marcaba la etapa de duelo en el camino de derrota → `stageClear(idx, won, 'duelo')` también en perder.
   - r149 F-A1: `startHallMusic` CONSUMÍA la petición de música del menú → la restauración del icono de mute quedaba MUERTA → recordar (`_menuReq`), re-armar con `setMusicWanted(true)`, expirar en los bordes.
   - **Regla**: `rules.onMatchStart` (c12:77) es el ÚNICO punto de recogida de poderes/estado (15 caminos de startMatch); los cierres restauran el estado global aunque la entrada fallara.
2. **NaN silencioso**: un valor no finito en audio (panNode) o en transformaciones por frame (sway F-A2) LANZA y mata el frame o corrompe la matriz sin excepción. **Regla**: `Number.isFinite` en audio; `x != null ? x : default` en datos de packs externos; el cero explícito se respeta.
3. **Convención del ganador**: SIEMPRE 'player'|'ai'. 'rival' string truthy como booleano = el FIX CRÍTICO v3.2 de estacion.
4. **Rotación de saque online** (r82): relativa al `gameOpener`, nunca hardcodeada al 'player' — dos bolas HELD y partido atascado tras el punto 1 en dispositivos reales.
5. **Guardias de rally** (r79/r140/r141): un rallye se resuelve UNA vez; claims con rallyId ENTERO fail-closed (2.5 burlaba la guardia y duplicaba el punto).
6. **Huella/banda interpoladas** (r144 H1/H2): atribución opuesta del punto entre extremos si se evalúa con la posición de fin de subpaso.
7. **El evento paddle se emite SIEMPRE** (r144 H3) que la física aplica impulso.
8. **Cooldown 0.24** (c02:29): con 0.08 la pala reclutzaba por detrás y disparaba la bola hacia atrás.
9. **Un fallo JAMÁS congela el frame**: defensa fina por subsistema primero; escudo global del animate como última capa; vigilante de efectos (r110 cristales congelados toda la partida → plazo duro + pendientes()).
10. **Volea de golpes remotos** (r81): la juzga el árbitro de la mitad del que golpea; el fantasma propio va por detrás del vuelo real (avance ≤120 ms + lag).
11. **Infra**: EADDRINUSE de brokers huérfanos (pkill previo); procesos efímeros muertos al acabar la tool; node_modules/ZIPs/download borrados por el reciclaje (regenerar con bun install / gen_release); historia git local rebobinable (verificar árbol, push -f); workers.dev bloquea urllib 1010 (curl + UA); mount sin truncate (escritura atómica); Push pages SIEMPRE -f (huérfano); menú abierto congela el saque de la CPU (c12:10048); guardia anti-doble-selectstart 70 ms (c12:10286); raycaster del menú far 2,5 vs rayos propios far 9-10.
12. **Secretos**: jamás en el repo; tokens efímeros por diseño; escaneo de secretos antes de cada commit; el PAT persiste solo en `scripts/worker-tele/.github-pat` (0600, gitignored).

---
## 17 · Convenciones de código y de trabajo

- **Idioma**: comentarios, mensajes, i18n y documentación en ESPAÑOL (es/en solo en los catálogos `title/description` de campeonatos y TLang).
- **Estilo defensivo**: try/catch con comentario de causa («nunca rompe el juego»); guardias `!= null` (cero explícito respetado) sobre datos de packs externos; `Number.isFinite` en audio; escritura atómica para ficheros grandes.
- **El DATO manda**: comportamiento nuevo → primero intentar moverlo a c02 como datos; la lógica lee en vivo (`COND_LOGRO`, `CONFIG_TORNEOS`, `SERVE_TUNE` en `__ppDebug`).
- **Flujo de trabajo por ronda (el patrón de las 14 pasadas)**:
  1. Línea base: `qa_version.py` + `test_red_nucleo.mjs` + `test_r128_claims.mjs`.
  2. Auditoría del territorio (leer los ficheros; verificar cada contrato con grep antes de afirmar).
  3. Defectos → fix mínimo + arnés reproducible (extracción de código REAL) → bucle hasta 0 fallos.
  4. Batería completa (§15) → `bump_version.py` → `c2_sellar.py` → escaneo de secretos → commit (formato: `rXXX · descripción con los fixes F-XX nombrados`) → push `HEAD:main` (PAT por URL o GIT_TOKEN; `-f` si la historia local fue rebobinada).
  5. `deploy_pages.py --push --release --backup` → empujar el huérfano pages si el script no lo hace → verificar CDN (PAGES-VERSION.txt + marcadores del cambio en game.html).
  6. `worklog.md`: nueva sección §N con fecha, hallazgos, fixes con nombres F-XX, batería, versión. SIEMPRE en el mismo commit.
- **Arneses**: nombre `test_rXXX_<tema>.mjs|py`; jamás borrar los históricos; `python3 -I` para scripts que leen ficheros; los arneses v2 deben arrancar su propio broker con `pkill PeerServer` previo.
- **Entorno sandbox**: procesos efímeros (morirán al acabar la tool); reciclaje borra node_modules/ZIPs/download y puede rebobinar .git; `upload/` es entrada (no modificar); todo entregable del usuario va a `download/`; los scripts se guardan en `scripts/` (persistencia); jamás escribir fuera de `/home/z/my-project/` salvo `/tmp/render/`.
- **Deuda conocida §37**: `CF_API_TOKEN` NO está en el entorno (verificado de nuevo en r149) — `deploy_worker.py` lo exige (exit 2 sin él). El worker VIEJO sigue en producción y el panel de telemetría usa un fold de respaldo. El dueño debe crear el token (plantilla «Edit Cloudflare Workers» + permiso D1 Edit) y exportarlo; entonces `deploy_worker.py` es re-entrante y hace todo (D1, secrets, cron, E2E).

---

## 18 · Recetas operativas (índice de «cómo se modifica X»)

| Quiero… | Dónde tocar | Sección |
|---|---|---|
| Cambiar una constante física | `DIMS` (c02) si es de simulación global; tablas c04 (`CCD/BOTE/SOLVER/KF_TUNE`) si es de contacto — golden de trayectorias manda | §5 |
| Ajustar dificultad de la IA | `CONFIG_DIFICULTAD.presets` / `esfuerzo`; topes en `escala`; pasar por `scalePreset`/`estiloAplicar` | §3.2, §5.3 |
| Añadir un logro/recompensa | fila en `CONFIG_LOGROS.core` (c02) + textos `ach_*` en c00 + disparo en GameStats (c06) | §12 |
| Añadir skin (mesa/bola/pala) | `MESA_ASPECTOS`/`BOLA_ASPECTOS`/`CONFIG_PIELES` (c02); pintor procedural en `bolaTex` (c07) si hace falta | §10 |
| Crear un campeonato | `gen_campeonato.py` → `qa_plantilla.py` → `--registrar` (plantilla `_plantilla` + guía + schema) | §8.3 |
| Añadir un poder | (a) local: trigger + FX junto a los de c12:11327+; (b) DUELOS: estado `_dl*`, registro en `_dlArma` (16095), `sendDueloPower` si online. JAMÁS tocar c04/c05 directo: congelar/tintar y RESTAURAR en `_fin` | §3.3 |
| Botón nuevo en el salón | pintor `drawHall*` (c08) + mesh en `createHall` + rayo/pulsa propio en c12 (clonar `_hallMusicaRay/Pulsa`), respetando la prioridad de rayos | §11 |
| Cambiar el HUD | `createScoreboard` (c08:2331) con dedupe por clave; datos del bloque 7 del animate | §11 |
| Paso nuevo en el arranque | dentro de `onSessionStart` (c12:10016) tras `enterHall()`, con try/catch y clave pp_* "una sola vez" | §3.4 |
| Tocar el bucle animate | respetar el orden de bloques; `dt` UI vs `dtFis` física; try/catch propio; el escudo global es última capa | §3.3 |
| Cambiar física de red/salas | spec §7: versiona el mensaje, fail-closed, arnés multipartida + vivo | §7.4 |
| Añadir ruta al worker | `worker.js` (patrón social/ruta en fetch), saneo + CORS + cuotas + sin PII; arneses `diag_tele_produccion.py`/`e2e_salas_produccion.py`; deploy con CF_API_TOKEN (§37) | §13.2 |
| Cambiar versión de three | `02_importmap.html` + copiar builds a `public/vendor/three/` + build + golden + qa_version | §2 |
| Precachear un asset | `SHELL` de sw.js (cáscara) o CACHE-FIRST; si es dato vivo → regex `VIVAS`; añadirlo a `SITE_PATHS` de deploy_pages si es nuevo | §13.3 |
| Publicar versión nueva | bump → QA → gen_release → commit → deploy_pages --push --release --backup → CDN verify | §14 |
| Añadir idioma | tablas de c00 (`T/TLang`) + `[data-lang]` de la portada | §3.1 |

---

## 19 · Estado actual (corte r149) y pendientes

- **Versión**: 3.6.235-SDK6 · fase 190 (PORTADA CLÁSICA EN LA RAÍZ + ENTRADA VR EN UN TOQUE, r152)
- **Revisión integral (r152-b)**: 6 hallazgos corregidos con verificación (PII cf-* en el worker → techo por sid; harness PII a cero-cf; QA telemetría H18; golden c05 re-bendecido determinista; presupuesto de tamaño; r130 watchdog + veredicto único) + arnés r153 de señalización REAL sobre el server.js del repo (21 OK, ciclo sala→sync→reset→reconexión) + auditoría estática del núcleo sin defectos abiertos. Matriz final toda verde; sello de game.html VÁLIDO (sin cambios de núcleo). Informe: download/REVISION-INTEGRAL-r152.md.
 **Auditoría 9 (r152-c)**: 3 hallazgos más corregidos (cubo «x» del techo por sid para filas anónimas; prueba de comportamiento del techo 109→114 checks; arnés r154 de caos de tipos en el protocolo, 11 OK) + zonas profundas verificadas limpias (escudo del bucle c12, guardas localStorage 13/13, UGC→DOM sin XSS, Caddyfile). Informe: download/AUDITORIA-9-r152-c.md.
 **Auditoría 10 (r152-d)**: primera revisión de la superficie web jamás tocada (sw.js, panel telemetría, tv.html, live-service, peer-server, champloader). HALLAZGO REAL: XSS en el panel del dueño (fraseDe() pintaba el nombre de evento sin escapar para eventos desconocidos — robo de la CLAVE del localStorage) corregido con esc(k) y demostrado con el arnés nuevo r155 (12/12, route-mock con datos hostiles: antes ejecutaba, después cero ejecución). sw.js limpiado (swr() muerto). Pendiente histórico AbortController: ya estaba resuelto en código (AbortSignal.timeout 4000). Informe: download/AUDITORIA-10-r152-d.md.
 **Auditoría 11 (r152-e)**: últimos módulos sin revisión propia (c01-c08, c10, storage de c12, contenido real de championships/) — CERO defectos nuevos con evidencia: 15/15 JSON.parse con guard, caché WORLDRANK sanitizada (_normalize+_sanitize), voz sin texto de peer y personalidad externa reducida a multiplicadores acotados ±22%, sounds del manifest sólo same-origin como audio, c01/c10/c08 limpios por lectura completa. Cobertura completa: todos los módulos, páginas y mini-services tienen revisión documentada. Informe: download/AUDITORIA-11-r152-e.md.
 **Análisis de cobertura (r152-e2)**: mapeo exhaustivo repo vs 11 auditorías — superficie de riesgo del juego cubierta al 100%. Dos hallazgos propios: (1) CRÍTICO corregido en vivo — el despliegue Pages estaba atrasado (servía el commit b051162, ANTERIOR al parche XSS del panel): deploy_pages.py --push ejecutado + verificado en vivo (fuente_commit=HEAD, parche presente grep=1, smoke Playwright 0 fallos); lección operativa: cada ronda con correcciones termina en --push. (2) Credenciales verificadas (3ª vez pedida): .clave-produccion no trackeada, valor ausente del repo, sin PATs en contenido, worker en producción respondiendo 403/200 en vivo, D1 viva, cron activo. Supply chain: engine.io 6.6.11 fuera de los rangos CVE-2026-59724/102599; scaffold Next.js CVE React2Shell no aplica (sitio estático) — recomendado podar. Higiene: .env placeholder y db/custom.db des-trackeados. Informe: download/ANALISIS-COBERTURA.md. · golden `617643cab092164a…` · manifests (oeste 56, magia 32, locura 23, estacion_orbital 16, halloween 3). La portada 2D vive ahora en la LANDING de la raíz (r152) y game.html entra directo al Hall (r151) — arneses test_r151 (10 OK) y test_r152 (14 OK).
- **Producción**: Pages built `c2851836e` (CDN verificada: `_menuReq` ×6, `sway != null` ×1 en game.html); main en `8fc7f4b`; Release GitHub con los 4 ZIPs de la versión vigente.
- **Calidad**: batería principal 523 checks verde; 14 pasadas de supervisión documentadas en worklog.md (§1-§41).
- **Pendientes**:
  1. **§37 (heredado)**: `CF_API_TOKEN` ausente del entorno → deploy_worker bloqueado; el worker en producción es el ANTERIOR. Requiere el token del dueño.
  2. Los gen_release `scripts/release-v36209/v36210` son los últimos vivos — el patrón copytree se hereda en cada versión (ver §14.3).
  3. `download/` y `public/descargas/` se regeneran si el reciclaje los borra (byte-exacto desde git/scripts).

---

## 20 · Cheat sheet de comandos

```bash
# LÍNEA BASE (empezar SIEMPRE aquí)
python3 -I scripts/qa_version.py                                   # 31 checks
node --no-warnings scripts/test_red_nucleo.mjs                     # 60
node --no-warnings scripts/test_r128_claims.mjs                    # 22

# BUILD Y VERSIÓN
python3 -I scripts/build_game.py                # ensayo byte-exacto vs golden
python3 -I scripts/build_game.py --escribir     # ensamblar de verdad
python3 -I scripts/bump_version.py 3.6.234-SDK6 # versión nueva (único camino)
python3 -I scripts/c2_sellar.py                 # re-sellar sin cambiar versión

# BATERÍA COMPLETA (ver §15 para timeouts)
node --no-warnings scripts/test_r130_multipartida.mjs             # 206
node --no-warnings scripts/test_worker_r169.mjs                   # 25
node scripts/worker-tele/test_local.mjs                           # 109
node --no-warnings scripts/test_r146_peerjs_vivo.mjs              # 21 (necesita ws+peer)
node --no-warnings scripts/test_r147_gemelo_magia.mjs             # 20
node --no-warnings scripts/test_r148_campeonatos.mjs              # 15
node --no-warnings scripts/test_r149_nucleo_ligero.mjs            # 14

# CAMPEONATOS
python3 scripts/gen_campeonato.py --id X --titulo-es "..." --rival-nombre "..." --dificultad media --arte ./arte/
python3 scripts/qa_plantilla.py public/championships/X
python3 scripts/gen_campeonato.py --id X --titulo-es "..." --registrar

# RELEASE / DEPLOY
GIT_TOKEN=… python3 -I scripts/deploy_pages.py --push --release --backup
CF_API_TOKEN=… python3 -I scripts/deploy_worker.py               # exige token (§37)
git push -f "https://x-access-token:$GIT_TOKEN@github.com/FranJavierDavila/CrazyPP.git" HEAD:refs/heads/main

# VERIFICAR CDN POST-DEPLOY
curl -s https://franjavierdavila.github.io/CrazyPP/PAGES-VERSION.txt | head -2
curl -s https://franjavierdavila.github.io/CrazyPP/game.html | grep -c "_menuReq"

# SERVICIOS LOCALES
cd mini-services/peer-server && PORT=3005 npm start            # broker señal (node + peer)
cd mini-services/live-service && bun start                     # relay TV :3004 (bun install primero)
```

---

*Cierre: esta base se mantiene VIVA — cada ronda de supervisión que toque comportamiento debe actualizar la sección correspondiente (y el worklog con la lección). Última actualización: r149, 2026-11-27, commit 8fc7f4b.*
