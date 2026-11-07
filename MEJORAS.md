# CRAZY PING PONG · ROADMAP MAESTRO DE MEJORAS (M1 → M8)

> **Memoria viva del proyecto** — creada r106 (nov 2026). El dueño mandó
> implementar TODAS las mejoras del análisis crítico; Z (arquitecto) fija el
> orden **de más sencillo a más complicado**. Este fichero se actualiza al
> cerrar cada hito: marca `[x]`, anota la ronda/versión en la que se cerró y
> queda señalado cuál es la SIGUIENTE. Persiste en el repo (GitHub) y en el
> sandbox — nunca se pierde entre sesiones.
>
> Regla de oro: **cada hito = rondas QA→bump→empaquetar→deploy→verificación
> tres vías** completas, como siempre. Nada se da por hecho sin agujas verdes.

## Cola de ejecución (estado)

| # | Hito | Esfuerzo | Estado |
|---|------|----------|--------|
| M1 | Game feel · capas de sonido + hápticas calibradas | ★☆☆ | ✅ HECHA r106 · v3.6.98-SDK6 en producción |
| M2 | Arnés anti-regresión + alarmas de telemetría | ★★☆ | ✅ HECHA r107 (M2a arnés-gate) + r108 (M2b alarmas, worker vivo) |
| M3 | PWA instalable (adiós `?v=`, icono en el casco) | ★★☆ | ✅ HECHA r109 · v3.6.99-SDK6 en producción |
| MP | **MULTIJUGADOR REPARADO** (prioridad del dueño: partida con amigos injugable) | ★★★ | ✅ HECHA r110 · v3.6.100-SDK6 en producción |
| M4 | Onboarding < 60 s (rally demo + JUGAR + saque guiado) | ★★☆ | ✅ HECHA r111 · v3.6.101-SDK6 en producción |
| M5 | IA con estilos (8-12 personalidades) + escalera de carrera | ★★★ | ◐ M5a ✅ r112 · M5b escalera → r113 |
| M6 | Identidad "locura + entrenador" (power-ups, 2v2, campeonatos) | ★★★ | ⬜ pendiente |
| M7 | Matchmaking + ELO online + reto diario/torneo semanal | ★★★★ | ⬜ pendiente |
| M8 | Port nativo a tienda (App Lab / Horizon) | ★★★★★ | ⬜ pendiente (decisión estratégica) |

> **HALLAZGO REAL de M2b (r108, estreno del sistema):** con los datos reales
> del casco del dueño la alarma fps_bajo disparó ROJA al instante — media
> **58,1 FPS en VR** sobre 17 sesiones vr_end (umbral 60). La pérdida de
> rendimiento que el dueño reportó en r105 queda CONFIRMADA con telemetría:
> a investigar en las próximas rondas (candidatos: NITIDEZ/FFR elegida en
> r96, perfil Quest 2 a 72 Hz mezclado en la media, o coste del hall+HUD).
>
> **MP (r110) — REPORTE DEL DUEÑO que reordenó la cola:** «es imposible
> golpear la bola… las palas no aparecen donde deberían… veo su pelota
> cuando mueve su pala». Causa raíz: el BIT 4 de la pose (ver sección MP).

---

## MP · MULTIJUGADOR REPARADO ✅ HECHA (r110 · v3.6.100-SDK6) · VERIFICADO AL 100% (r121 · v3.6.110-SDK6)

> **r121 · GARANTÍA EXTENDIDA (requisito Nº 1 del dueño)**: dos defectos
> REALES del validador §12 cazados por el banco y reparados — (1) la pose
> para juzgar un golpe/saque remoto ahora es la MÁS PRÓXIMA a tHit en ambas
> direcciones y a ±150 ms (POSE_FRESH_MS): un hueco sin pose ya no juzga
> contra una pala fantasma que «no deja sacar»; (2) la cadencia cuenta
> GOLPES, no lanzamientos: el toss ya no dispara el rechazo del saque
> rápido. Cobertura nueva del hueco sin probar: el SAQUE DEL INVITADO con
> ROTACIÓN ITTF — banco S3 (18/0, también a 120 ms ±40/5 %) y batería de 4
> puntos con PeerJS real (P1 67 · P2 68 · P3 69 checks, 0 fallos).

> **PRIORIDAD MÁXIMA dictada por el dueño** (por delante de M4): el
> multijugador era INJUGABLE en duelo real. Diagnóstico con un BANCO DE
> DUELO nuevo en Node (`scripts/diag_multijugador_r110.mjs`): dos extremos
> completos con el CÓDIGO REAL de producción (c09 NetLink + c09b PPNET +
> física c04/c05 + c02) sobre un cable simulado (40 ms ±12 ms, pérdida 1 %
> en fast, canales RTC falsos con SDP/ICE/Hello reales del juego).

**Causa raíz y reparaciones (las 4):**
- [x] **BIT 4 DE POSE (la madre del cordero)** — el emisor (`c09
      _samplePose`) ponía `fl |= 4` con la pala en CUALQUIER mano, pero los
      TRES lectores (c12 render 10311, c12 saque 9928, c09 `_remotePadNet`
      1754) lo interpretan como «pala en la mano IZQUIERDA (slot 0)». Un
      jugador diestro (paddleHand=1, el 95 %) viajaba mal leído: el rival
      pintaba su pala en la MANO LIBRE — donde está la bola del saque («veo
      su pelota, no su pala», palabra literal del dueño) — y el validador
      §12 comparaba cada golpe contra la mano equivocada: distancias de >1 m
      → TODO golpe remoto rechazado → «la bola cae irremediablemente aunque
      la trate de golpear». Fix en el emisor (bit4 sólo slot 0) + **PROTO 3**
      (builds mezclados rechazan el HELLO y caen a v1 honesto, sin
      malinterpretar el cable).
- [x] **VALIDADOR JUSTO** (c09b VP): MAX_SPIN 160→220 · TOL_FUTURE
      120→250 ms · HIT_NEAR_PAD 0,60→0,85 m. Con latencia/efecto real se
      rechazaban golpes LEGÍTIMOS (rechazar un golpe honesto regala un
      punto y congela el rallye). El anti-trampa sigue vivo: +400 ms sigue
      rechazado, shot+1 sigue exigido, 0,85 m sigue siendo imposible desde
      lejos.
- [x] **MITAD PROPIA JUGABLE EN FANTASMA** (c12 bloque FSM): el fantasma se
      simulaba con palas VACÍAS aunque la bola ya estuviera EN MI MITAD —
      ventana muerta de RTT..300 ms por golpeo (a 5 m/s = 1,5 m injugable).
      Ahora mi pala participa en mi mitad y mi contacto reclama la
      autoridad (netLocalHit → HIT con validación §12 en el rival). En
      mitad ajena sigue prohibido tocar.
- [x] **REPARACIÓN DE SAQUE ATASCADO** (c09 `_applyFastEv` SNAP): si el
      TOSS/HIT del saque rival se perdía o era rechazado, mi bola quedaba
      HELD del rival PARA SIEMPRE («no deja ni sacar ni jugar»). Ahora los
      SNAPs del rival (su bola viva) liberan el hold y pasan a fantasma
      desde el estado exacto del SNAP.

**Banco de duelo (capa GATE nueva `qa_duelo_r110.py`):** S1 espejo de pose
EXACTO diestro y zurdo (0,0 cm · 0,1° — el bit4 zurdo viaja ON y el lector
elige lp) · S2 saque legal con el solucionador REAL del juego → cruce →
autoridad del invitado → CONTACTO → validación del anfitrión **0 rechazos**
→ FSM own/ghost/auth correcta. 9/0 verde. `test_red_nucleo` 59/0 (anti-
trampa intacta: +400 ms rechazado, shot+1 exigido). Batería BQ (3 duelos
reales en paralelo con PeerJS real) intacta.

**Criterios de aceptación:** dos cascos en el mismo build juegan un duelo
completo: palas donde deben (diestro y zurdo), bola del saque legible en la
mano del rival, golpes del invitado ACEPTADOS, sin bolas congeladas.
Verificación final: el dueño repite la partida con amigos en producción.

---

## M1 · GAME FEEL — capas de sonido de impacto + hápticas calibradas ✅ HECHA (r106 · v3.6.98-SDK6)

> **CORRECCIÓN DE AUDITORÍA (r106):** el análisis crítico inicial se hizo sobre
> un árbol reciclado a r35 por error del sandbox. El juego r105 YA TRAE desde
> la r62 «SFX REALES»: muestras físicas modales (cáscara 40 mm + transitorio +
> cuerpo) para mesa/pala/canto/red/suelo, playbackRate mapeado a la velocidad,
> jitter ±1,5 % y fallback sintético. La mitad de AUDIO de M1 estaba hecha.
> Lo que quedaba vivo era la HÁPTICA del bote (0,18 fija, fuera del guard
> anti-spam) — eso es lo que r106 implementa.

**Alcance:**
- [x] Capas por material ≥3 variantes × 2 alturas + jitter — **YA EXISTÍA
      (r62 SFX REALES)**: 5 muestras físicas (mesa/pala/canto/red/suelo),
      rate 0,84→1,34 por velocidad, jitter ±1,5 %; verificado en r106.
- [x] Hápticas calibradas (r106): bote de mesa proporcional a velocidad
      (0,08+0,16·s · 50–80 ms) y DENTRO del guard de 60 ms (antes: 0,18 fija
      en cada evento = ametralladora en ráfagas esquina+canto).
- [x] Canto distinguible al tacto (r106): pico más alto (0,14+0,16·s) y seco
      (28 ms) frente al bote llano.
- [x] Red palpable (r106): vibración sutil 0,15/45 ms al roce de la malla
      (eventos raros: sin riesgo de spam).
- [x] Háptica de pala ya escalada (r62: intensidad 0,35+0,65·s y duración
      34–96 ms por velocidad) — intacta; anti-ametralladora por diseño.

**Criterios de aceptación:** 12 golpes seguidos suenan distintos (r62 ya
cumple: jitter + rate por velocidad) · háptica bote suave≠bote fuerte≠canto
percibible · net-cord se siente · sin regresión de FPS (cascada presupuesto) ·
agujas r106 en producción.

---

## M2 · ARNÉS ANTI-REGRESIÓN + ALARMAS DE TELEMETRÍA ✅ HECHA (M2a r107 · M2b r108)

> **DIVISIÓN HONESTA (r107):** M2 se parte en dos rondas. **M2a (r107, HECHA)**:
> el arnés que JUEGA (gate de ronda). **M2b (r108, HECHA)**: alarmas de
> telemetría en el worker — DESPLEGADAS en producción con deploy_worker.py
> (sin dashboard: token del dueño, D1 y CLAVE preservadas, E2E de sonda verde).

### M2a · EL ARNÉS QUE JUEGA ✅ HECHA (r107)

**Alcance:**
- [x] **Arnés físico** (`scripts/arnes_rallies_v3698.mjs`, node puro, 0,6 s):
      200 rallies completos con el código REAL del juego (c05.stepPhysics +
      c06.Rules + c06.OpponentAI + c05.findServeVelocity), presets reales
      (9 combinaciones easy/medium/hard), determinista por semilla (mulberry32,
      hash estable 81dc1942…). Invariantes por subpaso: I1 finitos · I2 bola en
      sala · I3 IAs ancladas (nunca cruzan la red; tope legal de persecución
      2·HL+0,15 de c06) · I4 árbitro vivo (15 s sin golpeo con bola viva) ·
      I5 reparto de puntos (89-103 en la batería).
- [x] **Arnés vivo** (`scripts/qa_arnes_vivo_v3698.py`, Playwright): el juego
      REAL juega 45 s de partido en navegador (bucle completo + piloto IA
      inyectado en la mitad del jugador, casa espejo del rival). Reloj propio
      (setAnimationLoop(null) + animate paso a paso — en headless el rAF corre
      a 1,5 fps). Invariantes V1-V3 por frame; señales de vida exigidas
      (puntos, botes, saques). Lección clave: el reloj sintético debe arrancar
      POR DELANTE del real (dt negativo corrompe) y la mesa está en C=−1,6.
- [x] **Canarios (test canario del criterio de aceptación):** el arnés físico
      detecta la bola teletransportada (I-2) y el vivo la suya (V2, muestreando
      antes de que el juego se autocure en 1 frame). Si el canario NO se
      detecta, el arnés ROJA (un arnés que no muerde no sirve).
- [x] **Gate de ronda:** `qa_todo.py` gana dos capas M2a (físico 1 s · vivo
      ~112 s). Si el arnés roja, NO se despliega.
- [x] Hallazgos del propio arnés (sin cambio de juego necesario): los rallyes
      largos hard-vs-hard (60+ intercambios, missBase 0,03) son comportamiento
      ESPERADO, no bug; el juego se autocura de bolas envenenadas en 1 frame;
      entre puntos la bola se APARCA en (3, 50, 2,3) — el arnés lo tolera.

**Criterios de aceptación:** ✓ canario cazado en ambos arneses · ✓ gate verde
dentro de qa_todo · ✓ determinismo (mismo hash en 2 ejecuciones).

### M2b · ALARMAS DE TELEMETRÍA ✅ HECHA (r108)

**Alcance:**
- [x] Bloque `alarmas` en el resumen del worker (worker.js): fps_bajo (media
      de vr_end.fps <72 amarillo / <60 rojo, ≥3 muestras) · errores_js (media
      por sesión ≥1 amarillo / ≥3 rojo, mensaje top incluido) · vr_cortas
      (sesiones VR cerradas de <60 s: ≥25% con ≥3 amarillo / ≥50% rojo).
      Nivel global = el peor de los items; sin datos suficientes → verde.
      Tolerante y compatible: campo NUEVO, los lectores viejos no lo leen.
- [x] E2E local con eventos sembrados (test_local.mjs bloque O, 61 checks
      en total): perfil malo → rojo global con las 3 alarmas bien caladas ·
      perfil sano → verde sin items · fronteras (68 = amarillo, 3/sesión =
      rojo, top inequívoco) · filtro ?sid reescala · almacén vacío → verde.
- [x] Tarjeta «Alarmas de producción» en el panel de Pages
      (public/telemetria.html): nivel global coloreado + items (o «Sin
      alarmas» verde), tolerante con worker viejo. QA capa J 131/0.
- [x] DESPLIEGUE REAL (r108, sin dashboard): scripts/deploy_worker.py con el
      token del dueño — D1 reutilizada, CLAVE reutilizada (sin rotación),
      E2E de sonda en producción verde (latido 270 · 403 sin clave · POST
      204 · resumen · purga · restauración).
- [x] **Estreno con hallazgo real:** la alarma fps_bajo disparó ROJA con los
      datos vivos del dueño — media 58,1 FPS en 17 sesiones vr_end. Ver
      nota en la cola de ejecución.

---

## M3 · PWA INSTALABLE ✅ HECHA (r109 · v3.6.99-SDK6)

**Por qué:** mata el mayor matador de retención (URL + `?v=` + caché del Quest)
sin esperar el port nativo. Icono en el casco, arranque en 2 clics, actualización
por service worker.

**Alcance:**
- [x] `manifest.webmanifest` (fullscreen landscape, start_url `./game.html`,
      scope `./` — compatible con Pages bajo `/CrazyPP/`) + iconos 192/512
      + variante maskable (emblema de la casa: palas cruzadas + bola en oro,
      `scripts/gen_iconos_pwa.py`) + service worker `sw.js` con estrategia
      por tipo: game.html stale-while-revalidate · datos vivos
      (campeonatos/UGC/PAGES-VERSION) network-first · assets cache-first con
      relleno bajo demanda · purga de cachés viejas en activate.
- [x] **El bump gobierna la caché (4.º sello físico):** `const CACHE =
      'crazypp-v<versión>'` en sw.js — `bump_version.py` lo parchea y
      `qa_version.py` lo verifica; cada versión invalida la caché sola.
- [x] Portada instaladora (c13): botón «📲 INSTALAR EN EL CASCO» con diálogo
      nativo (beforeinstallprompt → pwaOn dorado) y caminito manual de 2
      toques si el navegador no lo dispara (toast `#ppToast`); detección de
      standalone (el botón se oculta dentro de la app ya instalada);
      telemetría anónima `pwa_standalone/pwa_prompt/pwa_installed/
      pwa_manual_hint` (catálogo v5).
- [x] Deploy compatible con GitHub Pages bajo `/CrazyPP/` (deploy_pages
      publica manifest+sw+iconos; build_zip los lleva a los 4 ZIPs) + hub
      /descargas con la guía PWA + i18n ES/EN.

**Criterios de aceptación:** ✓ instalable desde el navegador (headless
Chromium captura beforeinstallprompt = criterios de instalabilidad
cumplidos; el dueño instala desde el Quest Browser con el botón o
⋮ → Instalar app) · ✓ arranque sin teclear URL (icono propio) · ✓ el bump
de versión invalida la caché sola (4.º sello) · ✓ agujas r109 en producción
tres vías byte-exacto (31/0) + K/L post-deploy verdes.

---

## M4 · ONBOARDING < 60 SEGUNDOS ✅ HECHA (r111 · v3.6.101-SDK6)

**Alcance:**
- [x] Rally demostración IA-vs-IA en vivo de fondo en el menú principal —
      **LA MESA DE LA CASA**: diorama IA-vs-IA sobre pedestal del hall
      (mesa miniatura ~55 %, palas disco, bola en parábolas scriptadas —
      cinemática pura, coste cero en cancha, hijo del hallGroup).
- [x] Botón único **JUGAR** por delante de todo lo demás — tarjeta ▶ JUGAR
      (hub_play) a toda fila 944×136 en y=240, verde vivo; la academia deja
      de bloquear (HUB DIRECTO: menuPage='main' SIEMPRE; bienvenida de
      1.ª instalación en UNA línea del árbitro, first_hint).
- [x] Saque guiado la primera vez — tres aros dorados aditivos en la cancha
      real (bola → golpe → red) + UNA línea que sobrevive al startMatch
      (srv_guide); se marca pp_srv_v1 a los 3 saques legales; nunca en
      academia ni online; desmonte con dispose.
- [x] Idioma y altura de mesa detectados/recordados antes del primer toque —
      c00 detecta navigator.language en la 1.ª instalación (huellas
      pp_tut_asked/pp_seen_v1 como guardia; es*→ES · resto→EN, recordado en
      pp_lang) y c12 muestrea la altura de la cabeza (2,6/4,7 s, mediana,
      <1,30 m → mesa baja 0,70, guardia pp_hauto_v1, nunca online).

**Criterios de aceptación:** un jugador nuevo está en un rally real en <60 s
sin tocar nada más que JUGAR (medible con telemetría: evento **primer_rally**,
lat = segundos desde vr_start, una vez por sesión, sólo partido local; catálogo
v6 con 16 eventos + tut_end del cierre de la academia).

**Cierre (r111):** GATE de ronda VERDE (A 31/0 · B 11/0 · C 29/0 · D 14/0 ·
F 66/0 · G 54/0 · H 208/0 · J 132/0 · arnés físico 200/0 · arnés vivo 11/0 ·
r109 VERDE · r110 VERDE · **r111 49/0** · T 17/0 · U 17/0 · V 74/0 · W 43/0 ·
X 37/0 · Y 31/0 · Z 36/0) + batería multi BQ (P1 LAN verde · P3 túnel 42/42 ·
P2 con 1 fallo de sincronía = flameo documentado r109/r110, NetLink intacto).
Re-anclas honestas: qa_telemetria (catálogo v6/16 + panel por su ruta REAL de
producción /telemetria.html — el SSR del dev server de ESTE sandbox muere por
los directorios root-owned heredados del reciclado, artefacto del entorno) y
locale es-ES en los arneses que leen la portada (qa_r109, qa_train_zonas,
qa_partido_sala — la detección de idioma M4 respeta navigator.language y el
Chromium de QA nace en-US). QA r111 nueva ya venía del intento perdido de la
encarnación anterior (qa_r111_v36101 + gen_release_v36101 + sella_r111 en el
repo) — la implementación en src se reconstruyó sobre esas agujas.

---

## M5 · IA CON ESTILOS + ESCALERA DE CARRERA

> **r112 · M5a ✅ (v3.6.102-SDK6):** DOCE personalidades sobre la MISMA
> física, sin trampas: Clásico (byte-idéntico, mul=null) · Looper · Chopero ·
> Bloqueador · Atacante · Defensivo · Dejadas · All-round · Joven nervioso ·
> Veterano frío · Gigante · Relámpago. Registro `OPPONENT_STYLES` (c02) con
> multiplicadores ACOTADOS (errStd/missBase/velocidad/predicción/smash/T) +
> colocación por el canal r95 (zIdle/bias) + celebración propia. Selector ‹ ›
> en AJUSTES › JUEGO (persistencia pp_estilo_v1, recálculo EN VIVO, anuncio
> del árbitro). NUNCA en online/campeonato/calibración/academia. PRUEBA DE
> NO-TRAMPA: arnés Node qa_estilos_r112 (12 estilos × 30 rallies con física,
> árbitro e IA reales): cfg acotada NT-1, invariantes I1-I4 (la IA jamás
> cruza la red), firma ≠ clásico D-1 y 66/66 parejas distinguibles D-2.
> Telemetría ai_style (catálogo v7, 17 eventos). Los rivales de campeonato
> NO cambian (la herencia de estilos llega con M5b, junto a la escalera).

**Alcance:**
- [ ] 8-12 personalidades con parámetros y tácticas propias SOBRE la física
      compartida (sin trampas): Looper (lift desde lejos), Chopero (slice
      profundo), Bloqueador (pegado, reflejos), Atacante (smash temprano),
      Defensivo (lobs), Cortador de dejadas, All-round, Joven nervioso,
      Veterano frío, Gigante (alcance), Pequeño rápido…
- [ ] Cada estilo = perfil (posición de casa, profundidad, pesos de selección
      de golpe, errStd, velocidad, estética de swing) + UI con retrato/nombre.
- [ ] Escalera de carrera: divisiones de bronce→leyenda, rivales concretos por
      división, progreso guardado, rematches con revancha.
- [ ] Integración con campeonatos existentes (los rivales heredan estilos).

**Criterios de aceptación:** la IA juega por las MISMA reglas físicas (agujas
de no-trampa) · 12 rivales distinguibles jugando 1 minuto contra cada uno.

---

## M6 · IDENTIDAD "LOCURA + ENTRENADOR"

**Alcance:**
- [ ] Modo fiesta: power-ups (bola loca, mesa encogida, pala gigante…) 1v1/2v2
      local + online-ready.
- [ ] 2-3 campeonatos temáticos nuevos (heredando champloader).
- [ ] PRO TRAINING expandido: nuevos ejercicios, progresión semanal y TARJETA
      DE PROGRESO compartible (captura con stats del mes).

**Criterios de aceptación:** los tres frentes jugables y con agujas; el
entrenador diferencia frente a Eleven (nuestro estandarte de marketing).

---

## M7 · MATCHMAKING + ELO ONLINE + COMPETICIÓN

**Alcance:**
- [ ] Backend de emparejamiento en el worker Cloudflare (D1): cola por nivel
      ELO + región, salas efímeras, señalización PeerJS asistida (el anfitrión
      publica su ID; el guest lo recibe del servidor — sin compartir códigos).
- [ ] ELO server-side con antifraude básico (firma de resultados, tasas sospechosas).
- [ ] Reto diario (semilla por fecha) + torneo semanal con tabla.
- [ ] Lista de amigos (códigos persistentes) e historial de rivales.

**Criterios de aceptación:** dos cascos se encuentran solos por nivel en <30 s ·
ELO persiste y sube/baja correctamente · el modo por códigos sigue intacto.

---

## M8 · PORT NATIVO A TIENDA

**La decisión estratégica mayor.** Evaluar: empaquetado nativo del motor propio
(WebXR→OpenXR) vs reconstrucción. Incluye assets de tienda, cumplimiento de
políticas, logros/plataforma, precio. Se abre el análisis cuando M1-M4 estén
cerradas (mejora el producto a presentar) y M7 decida si el online va en web o
nativo.

---

## Registro de cierre de hitos

| Hito | Ronda(s) | Versión | Fecha | Notas |
|------|----------|---------|-------|-------|
| M1 · game feel | r106 | 3.6.98-SDK6 (FASE 100) | 2026-11-01 | Audio r62 verificado como regresión · háptica del bote calibrada dentro del guard · canto distinguible · red palpable · QA 35/0 · cascada verde · tres vías 24/0 |
| M2a · arnés que juega (gate) | r107 | (sin cambio de juego — 3.6.98-SDK6 sigue) | 2026-11-01 | Arnés físico 200 rallies determinista (0,6 s) + arnés vivo 45 s con piloto IA + canarios cazados en ambos · gate en qa_todo · 0 cambios de gameplay |
| M2b · alarmas de telemetría | r108 | (sin cambio de juego — 3.6.98-SDK6 sigue) · worker vivo actualizado | 2026-11-02 | Bloque `alarmas` en el resumen (fps_bajo/errores_js/vr_cortas) · harness 61/0 · capa J 131/0 · arneses M2a verdes · desplegado con deploy_worker.py (D1+CLAVE preservadas, E2E sonda verde) · panel Pages con tarjeta · hallazgo real: fps_bajo ROJO 58,1 FPS/17 sesiones |
| M3 · PWA instalable | r109 | 3.6.99-SDK6 (FASE 101) | 2026-11-02 | manifest+sw.js+iconos de la casa · 4.º sello físico (const CACHE gobernado por el bump) · portada instaladora (diálogo nativo + camino manual + standalone) · telemetría pwa_* (catálogo v5) · build_zip lleva la PWA a los 4 ZIPs · QA gate 13/13 (r109 nueva capa) · cascada histórica re-anclada (20+ capas, BK retirada) · tres vías 31/0 · K/L post-deploy verdes |
| P4 · verificación de producción + F1-F3 + F4 TURN (ronda 21) | r21 | (sin cambio de juego ni worker — 3.6.116-SDK6 sigue en producción) | 2026-11-07 | game.html?v=3.6.116-SDK6 servido = sha256 f6093b99… EXACTO (10.731.285 B) · marcadores F1-F3 vivos (verCompara×8 · onBuildMismatch×4 · net_build_warn×6) · QA verde: 6 suites juego 174/0 + worker 85/0 · Open Relay re-verificado RETIRADO hoy (192.0.2.1 RFC 5737 + Allocate UDP mudo RFC 5766) → la ruta Metered de ronda 20 espera METERED_APP+METERED_API_KEY del dueño (LEEME: CF 1 TB/mes gratis · Metered 20 GB/mes sin tarjeta) · /api/ice sin secrets responde STUN honesto (turn:false — ningún turn muerto al cliente) · telemetría P4 VIVA en producción: net_ice p2p srflx→srflx rtt 58 ms y net_match completo (rtt med 710 ms · jitter 55 · dur 58 s) — la partida entre casas YA abre por p2p sin TURN en estas redes |
| SKINS DE BOLA · primera personalización de la bola (ronda 22) | r22 | 3.6.117-SDK6 (FASE 119) | 2026-11-07 | 16 skins 100 % cosméticas (BOLA_ASPECTOS c02): clásicas (blanca/naranja/menta) + locura (estrellas/playa/fútbol/bola 8/ojo) + neón-arcade (neón/holográfica/disco) + planetas (Marte/Luna/Tierra/Lava/Saturno CON ARO) · texturas PROCEDURALES en canvas 512×256 con RNG semillado (deterministas entre cascos · cero bytes en el bundle · cero descargas) · candados igual que mesas reutilizando _mesaLibre (9 libres · 7 por 10 victorias/6★ o racha 5/3★) · REGLA DEL DUEÑO: campeonato → bola oficial, salida del hall recobra la skin (adiós blanco seco) · ESTELA A JUEGO (reposo = RGB de skin; poder/spin siguen mandando) · CHISPAS AL BOTAR (pool fijo 5×8, vida 0,32 s, cero asignaciones por bote) · ONLINE: skin del ANFITRIÓN por el HELLO v2 (campo OPCIONAL sk — JSON tolerante, builds viejos intactos; sólo el invitado la viste, sin candado) · UI: tarjeta BOLA en SALA + subpágina salabola + case bola_skin · I18N 21 claves ES/EN · FÍSICA INTACTA (c04/c05 no conocen las skins — garantía del dueño) · test_r21_bolas_v36117 63/0 · QA 322 checks verde · bump BYTE-EXACTO 10.756.498 B · release v36117 (4 ZIPs + hub) · DESPLEGADO: game ca1a23b0… en producción (commit b6fea97, pages 1717e61, proyecto=backup) |
| SPIN REALISTA + HALL CABAÑA (ronda 24) | r24 | 3.6.119-SDK6 (FASE 121) | 2026-11-07 | Informe del dueño tras probar la r23: «el giro es muy sutil y poco realista, al dar efecto no se nota el spin» — DOS CURAS: (1) GANANCIA 0.14→0.45 (×3.2, c12): |ω|=110 (tope) ≈ 7,9 rev/s (39,5°/frame a 72 Hz, bajo el umbral de estrobo) · |ω|=25 (EFECTO_SPIN_MIN) ≈ 1,8 rev/s · efecto medio (|ω|≈60) ≈ 4,3 rev/s — el LATIGAZO del bote sigue saliendo gratis (fricción c04) · (2) TEXTURA: las 4 skins planas (blanca/naranja/menta/neón) eran COLOR LISO — una esfera uniforme NO delata su ω ni a 8 rev/s: bolaTex (c07) les pinta como a las bolas de verdad, COSTURA ecuatorial de poliplástico + MARCA de fábrica «CRAZY» con pala en miniatura en dos caras opuestas (mapa × color: las marcas salen del tono de cada bola; canvas procedural, cero bytes) · HALL CABAÑA (las 6 imágenes del dueño, Hallcabana.zip): chimenea de piedra con brasero, barra con botellas y perchero de astas, ventanal nevado con banco de pieles, alfombra sobre parqué de espiga, techo de vigas con lámpara de astas — 2.ª variante del arte del Hall del Anfitrión en assets/hall/cabana/ (1,06 MB recomprimidos, proporciones EXACTAS de los planos 1849×864 · 2395×864 · 1296×1678) · liberada con 10 victorias («wins10», candado _mesaLibre como las skins de gala) · HALL_VARIANTES + hallVariantePorId (c02) · createHall(base) + vestir() + applyHallVariant (c08): re-vestido EN VIVO sin reconstruir el grupo, dispose del arte anterior, carga a prueba de fallos · UI ARTE DEL HALL en AJUSTES→SALA→HALL (MUSEO / LA CABAÑA 🔒 + hints, oculto de visita online) · LS «pp_hallvar» · ONLINE: hp lleva hv (id saneado contra catálogo, patrón sk/hp r22/r23; builds viejos ni lo envían ni lo leen; c09 SIN cambios de códec) — de visita se entra al ARTE DEL ANFITRIÓN aunque no lo tengas liberado (se VE, no se elige; si llega el hello dentro del hall, el arte cambia al vuelo) · I18N 6 claves ES/EN · FÍSICA INTACTA (c04/c05 no conocen mesh, arte del hall ni pp_hallvar) · test_r24_spin_cabana_v36119 89/0 · regresión r23 81/0 y r21 63/0 (2 aserciones re-ancladas a la evolución r24, comentadas) · QA: A 29 · B 11 escenarios · C 29 · D 10 · E 151 (re-anclada 3.6.119) · H 208 (re-anclada v36119 + tamaños ZIP reales) · J 132 · T 17 · U 17 · V 74 · arnés físico 200 rallies 0 fallos · duelo r110 18/0 · bump BYTE-EXACTO 10.787.766 B (+10.544) golden 50fc0842 · release v36119 (4 ZIPs + hub) · FIX del generador de release: el marcador de notas de la r23 nunca llegó a disparar (el ZIP heredaba el bloque P4.2 re-sellado) — la r24 sustituye el bloque de raíz y repara el slice de la comilla de cierre |
