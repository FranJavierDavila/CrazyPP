/* =====================================================================
 *  v2.27 · I18N · SELECTOR DE IDIOMA (castellano / inglés)
 *  - Todos los textos del juego (overlay 2D, menú de muñeca, mensajes del
 *    árbitro, marcador 3D, cartel de fin de partido, logros, estados de red)
 *  - La megafonía usa el banco de voz del idioma activo (VOICE_B64 es/en
 *    con las MISMAS claves: los planes de voz valen para ambos).
 *  - Persistencia en localStorage ('pp_lang'). El idioma por defecto es el
 *    castellano (compatibilidad total con partidas y tests previos).
 *  Uso: T('clave', {param: valor}) sustituye {param} en la plantilla.
 * ===================================================================== */
let __ppLang = 'es';
try {
  const saved = localStorage.getItem('pp_lang');
  if (saved === 'en' || saved === 'es') __ppLang = saved;
} catch { /* sin localStorage: castellano */ }

const I18N_STRINGS = {
  /* --------------------------- CASTELLANO --------------------------- */
  es: {
    // ---- nombres de oponente / personas
    opp_cpu: 'la CPU',
    opp_rival: 'tu rival',
    opp_machine: 'la máquina',
    who_you: 'ti',
    // ---- mensajes del árbitro (Rules)
    serve_wait: 'Tu saque · la bola espera en tu mano libre',
    surv_start: 'SUPERVIVENCIA · aguanta el rallye más largo',
    surv_new: 'Nueva bola · GATILLO para lanzar y golpear',
    surv_opp: 'Saque de {opp}… acelera cada vez más',
    rally_big: '¡Rallye de {n} golpes! · {cause}',
    rally_n: 'Rallye de {n} {s} · {cause}',
    word_hit: 'golpe',
    word_hits: 'golpes',
    point_you: '¡Punto para ti! · {cause}{rally}',
    point_opp: 'Punto para {opp} · {cause}{rally}',
    rally_suffix: ' · {n} golpes',
    retry_serve: '{cause} · repite el saque',
    serve_go: 'Tu saque · GATILLO para lanzar y golpear',
    serve_opp: 'Saque de {opp}…',
    over_win: '¡HAS GANADO! · {p}-{q} · gatillo: revancha',
    over_lose: '¡HAS PERDIDO! · {p}-{q} · gatillo: revancha',
    // ---- causas (viajan por red como CLAVES; se traducen al pintar)
    cause_dblhit: 'doble golpe',
    cause_volley: 'golpe antes del bote',
    cause_serve_no_own: 'saque sin bote propio',
    cause_let: 'LET · la bola rozó la red',
    cause_serve_net: 'el saque no pasó la red',
    cause_own_you: 'golpeaste tu propio campo',
    cause_own_opp: '{opp} golpeó su campo',
    cause_dbl_you: 'doble bote: no llegaste',
    cause_dbl_opp: 'doble bote: {opp} no llegó',
    cause_back_you: 'la bola volvió a tu campo',
    cause_back_opp: 'la bola volvió al campo de {opp}',
    cause_serve_net_touch: 'saque a la red',
    cause_serve_out: 'saque fuera',
    cause_net_stay: 'se quedó en la red',
    cause_wall: 'a la pared',
    cause_out: 'bola fuera',
    cause_noret_you: 'no la devolviste',
    cause_noret_opp: '{opp} no la devolvió',
    // ---- megafonía (textos; el plan de voz los cubre es/en)
    ann_score: '{p} a {q}, saque para {who}',
    ann_victory: '¡Victoria! {p} a {q}',
    ann_match_end: 'Partido para {opp}. {p} a {q}',
    ann_rally_record: '¡Rallye de {n} golpes! Nuevo récord',
    ann_ach: '¡Logro desbloqueado: {name}!',
    ann_room: 'Sala {room}',
    mode_survival: 'Modo supervivencia. ¡Aguanta el rallye!',
    mode_match: 'Modo partido. ¡Buena suerte!',
    welcome: 'Bienvenido al partido. ¡Buena suerte!',
    opp_connected: 'Rival conectado. ¡A jugar!',
    opp_disconnected: 'Rival desconectado',
    diff_easy: 'Dificultad fácil',
    diff_medium: 'Dificultad media',
    diff_hard: 'Dificultad difícil',
    // ---- salas (temas)
    theme_pabellon: 'Pabellón',
    theme_neon: 'Neón',
    theme_atardecer: 'Atardecer',
    theme_artico: 'Ártico',
    // ---- menú de muñeca
    menu_title: 'MENÚ',
    menu_hint: 'apunta con la pala y elige con el GATILLO',
    menu_b: 'B · cerrar',
    tab_settings: 'AJUSTES',
    tab_multi: 'MULTIJUGADOR',
    close_menu: 'Cerrar menú',
    mode_label: 'MODO DE JUEGO',
    mode_match: 'Partido',
    mode_survival: 'Supervivencia',
    diff_label: 'DIFICULTAD DE LA CPU',
    diff_easy_btn: 'Fácil',
    diff_medium_btn: 'Media',
    diff_hard_btn: 'Difícil',
    room_label: 'SALA',
    extras_label: 'EXTRAS',
    lang_label: 'IDIOMA',
    btn_amb: 'Ambiente: {v}',
    btn_trail: 'Estela: {v}',
    btn_mic: 'Megáfono del marcador: {v}',
    btn_music: 'Música: {v}',
    msg_music: 'Música {v}',
    btn_sndtest: '🔊 Probar sonido (3 notas)',
    msg_sndtest: '¿Lo oyes? Si no, vuelve a pulsar y lo reparo',
    msg_sndrepair: 'Reconstruyendo la salida de audio… pulsa de nuevo',
    btn_rematch: 'REVANCHA',
    yes: 'Sí',
    no: 'No',
    // ---- menú MULTIJUGADOR
    mj_head: 'JUEGA CONTRA OTRA PERSONA POR INTERNET',
    mj_connected: 'CONECTADO',
    mj_rival: 'rival: {code} · {st}',
    mj_playing: 'jugando',
    mj_over: 'partido terminado',
    voz_on_mic: 'Voz activa (micrófono abierto)',
    voz_on_silent: 'Voz activa (tu micro está en silencio)',
    voz_asking: 'Pidiendo micrófono…',
    voz_denied: 'Micrófono denegado',
    voz_off: 'Sin voz (pulsa Voz para activarla)',
    btn_voz: 'Voz: {v}',
    btn_hangup: 'COLGAR',
    mj_rematch_hint: 'La revancha está en la pestaña AJUSTES.',
    mj_room_code: 'CÓDIGO DE LA SALA',
    mj_waiting: 'Esperando al rival… comparte este código',
    btn_cancel_room: 'CANCELAR SALA',
    mj_creating: 'Creando sala…',
    mj_connecting: 'Conectando a {code}…',
    btn_cancel: 'CANCELAR',
    mj_error: 'Error de red',
    btn_retry: 'REINTENTAR',
    btn_back: 'VOLVER',
    mj_off_hint: 'Crea una sala o únete con un código.',
    btn_host: 'CREAR SALA (código para tu rival)',
    btn_join: 'INTRODUCIR CÓDIGO DE UN AMIGO',
    mj_p2p: 'P2P directo (WebRTC). Necesita internet en ambos visores.',
    mj_mic_hint: 'La voz usa el micrófono: acepta el permiso del navegador.',
    join_title: 'CÓDIGO DE LA SALA DE TU AMIGO',
    btn_connect: 'CONECTAR',
    // ---- v2.28 · MENÚ PRINCIPAL (gran panel flotante con acordeón)
    sec_match: 'JUGAR PARTIDO',
    sec_train: 'ENTRENAR',
    sec_surv: 'SUPERVIVENCIA',
    sec_crazy: 'CRAZY',
    sec_opts: 'OPCIONES',
    btn_start: '▶  EMPEZAR PARTIDO',
    btn_start_surv: '▶  EMPEZAR SUPERVIVENCIA',
    btn_train_go: '▶  ENTRENAR GOLPES',
    crazy_msg: '¡Sorpresas pronto..! 🎁',
    best_surv: 'Récord: {n} golpes',
    online_lbl: 'ONLINE · contra otra persona',
    train_hint: 'Máquina de bolas + panel para ajustar tu pala con los sticks.',
    surv_hint: 'La CPU acelera cada vez · ¿cuántos golpes aguantas?',
    // ---- mensajes de estado (panel / menú)
    menu_open: 'Menú principal · apunta y pulsa el GATILLO',
    msg_guest_mode: 'Pidiendo cambio de modo al anfitrión…',
    msg_mode_changed: 'Modo: {m} · cierra el menú para jugar',
    mode_surv_word: 'SUPERVIVENCIA',
    mode_match_word: 'PARTIDO',
    msg_no_cpu: 'En online no hay CPU · la dificultad no aplica',
    msg_diff: 'DIFICULTAD: {d}',
    msg_room: 'SALA: {r}',
    msg_trail: 'Estela de la bola: {v}',
    msg_mic: 'Megáfono del marcador: {v}',
    hint_hit: '¡Golpea la bola hacia la mesa con la pala!',
    hint_toss_high: 'Lanza la bola un poco más arriba',
    hint_behind: 'Saca desde detrás de la línea de fondo',
    hint_dropped: 'Bola caída · repite el lanzamiento',
    online_first: '¡Conectado! Esperando al anfitrión…',
    online_serve: 'Partido online · tu saque (GATILLO para lanzar)',
    net_ended: '{msg} · partido local reiniciado',
    // ---- estados de red (NetLink)
    peer_gone: 'El rival se ha ido',
    conn_lost: 'Conexión perdida',
    peer_closed: 'El rival cerró la sala',
    net_unavailable: 'Red no disponible en este navegador',
    invalid_code: 'Código no válido (5 caracteres)',
    net_fail: 'No se pudo iniciar la red: {m}',
    status_creating: 'Creando sala…',
    status_waiting: 'Sala {c} · esperando al rival…',
    status_joining: 'Conectando a la sala {c}…',
    room_not_found: 'No hay ninguna sala {c}',
    no_lobby_server: 'Sin conexión con el servidor de salas',
    // ---- marcador 3D
    sb_you: 'TÚ',
    sb_cpu: 'CPU',
    sb_rival: 'RIVAL',
    calib_msg: 'ENTRENAMIENTO · Y: volver al modo anterior',
    sb_surv: 'S U P E R V I V E N C I A',
    sb_rally_hits: 'golpes del rallye',
    sb_rallies: 'rallyes {r}  ·  récord {b}',
    // ---- cartel de fin de partido
    fanf_win: '¡HAS GANADO!',
    fanf_lose: '¡HAS PERDIDO!',
    fanf_chip: '{p} - {q} · gatillo: revancha',
    // ---- logros
    ach_first: 'Primera victoria',
    ach_first_d: 'Gana tu primer partido',
    ach_streak: 'En racha',
    ach_streak_d: '3 victorias seguidas',
    ach_giant: 'Gigante',
    ach_giant_d: 'Vence en dificultad Difícil',
    ach_marathon: 'Maratonista',
    ach_marathon_d: 'Rallye de 20 o más golpes',
    ach_survivor: 'Superviviente',
    ach_survivor_d: '25 o más golpes en Supervivencia',
    ach_aces: 'Saque directo',
    ach_aces_d: '10 saques ganados sin respuesta',
    stats_line: '{won} victorias · {lost} derrotas · racha {streak} (máx. {best}) · mejor rallye {rally} · saques directos {aces}',
    // ---- overlay 2D (estado y controles)
    status_pause: 'Pausa · pulsa el botón para volver a VR.',
    status_vr_checking: 'Comprobando compatibilidad con WebXR…',
    status_vr_ok: '✅ Visor compatible detectado. Ponte las gafas y pulsa el botón.',
    status_no_vr: '🖥️ Sin visor VR: disfruta del modo espectador (IA contra IA).',
    status_no_webxr: '🖥️ WebXR no disponible aquí: modo espectador activo.',
    status_no_2d: '🖥️ Este navegador no soporta WebXR: modo espectador activo.',
    status_starting_vr: 'Iniciando sesión VR…',
    status_starting_train: 'Iniciando VR en modo entrenamiento…',
    status_starting_surv: 'Iniciando VR en modo supervivencia…',
    status_starting_ar: 'Iniciando passthrough…',
    status_vr_fail: 'No se pudo iniciar la sesión VR.',
    status_ar_fail: 'No se pudo iniciar el passthrough.',
    amb_yes: '🔊 Ambiente de torneo: SÍ',
    amb_no: '🔇 Ambiente de torneo: NO',
    ov_tag: 'Reglas ITTF · saque con mano libre y física real · pala 3D · Meta Quest 3',
    ov_serve: '<b>SAQUE</b> La bola descansa en tu <b>mano libre</b>. Pulsa el <b>GATILLO</b> (cualquier mando) para lanzarla y golpéala con la pala; o suelta el <b>GRIP</b> de la mano libre lanzando la mano hacia arriba. Ya no hay que esperar al punto muerto: golpea cuando quieras — el saque se endereza solo.',
    ov_hit: '<b>GOLPE</b> Golpea la bola con la pala (otro mando) desde detrás de la línea de fondo. Zona de impacto muy asistida, aún mayor en el saque: no hace falta milimetrar. El saque debe botar en <b>tu campo</b> y luego en el del rival.',
    ov_hand: '<b>A / X</b> Cambia la pala de mano en cualquier momento',
    ov_menu: '<b>MENÚ</b> En VR pulsa <b>B</b> (mando derecho): se abre un panel <b>sobre tu muñeca libre</b>. Apunta con <b>cualquier mando</b> (la pala también tiene láser) y elige con el <b>gatillo</b>: modo (Partido / Supervivencia), dificultad de la CPU, sala (Pabellón · Neón · Atardecer · Ártico), ambiente de torneo, estela de la bola, megáfono del marcador e idioma. Todo se aplica al instante y se recuerda entre sesiones.',
    ov_online: '<b>ONLINE</b> En el menú, pestaña <b>MULTIJUGADOR</b>: crea una sala, comparte el <b>código de 5 caracteres</b> y tu rival lo introduce en su menú. Partida P2P directa entre visores (ambos con la web abierta) e <b>incluso podréis hablaros</b>: acepta el permiso de micrófono.',
    ov_rules: '<b>REGLAS</b> Rozar la red en saque y pasar = <b>LET</b> (se repite) · volear antes del bote o dar doble golpe = falta · partido a 11 con ventaja de 2',
    ov_spin: '<b>EFECTO</b> Barre la pala de abajo a arriba al golpear para dar lift; de arriba abajo para cortar',
    ov_train: '<b>ENTRENAR</b> En VR pulsa <b>Y</b> (en cualquier momento): máquina de bolas + panel para ajustar la pala con los sticks. Guarda tus agarres con nombre y cárgalos siempre.',
    ov_difficulty: 'DIFICULTAD',
    ov_room: 'SALA',
    ov_grips: 'AGARRES DE PALA',
    ov_grip_ph: 'Nombre para guardar el ajuste actual',
    ov_grip_load: 'Cargar',
    ov_grip_save: 'Guardar',
    ov_grip_del: 'Borrar',
    ov_grip_reset: 'Natural',
    ov_progress: 'TU PROGRESO',
    ov_clear: 'Borrar',
    ov_surv: '🏆 SUPERVIVENCIA EN VR · ¿cuántos golpes aguantas?',
    ov_train_btn: 'ENTRENAR GOLPES EN VR · ajustar pala',
    ov_vr: 'ENTRAR EN VR',
    ov_ar: '🏠 PASSTHROUGH · tu habitación',
    ov_demo: 'Ver demo en pantalla (sin visor)',
    music_title: 'Música (portada y menú VR)',
    ov_hint: '<b>En el visor:</b> sube esta carpeta a <b>Netlify Drop</b> y abre el enlace con el <b>Meta Quest Browser</b> (requiere HTTPS). Sin visor, el modo demo juega IA contra IA.',
    ov_lang: '🌐 Idioma / Language',
  },

  /* ----------------------------- ENGLISH ---------------------------- */
  en: {
    opp_cpu: 'the CPU',
    opp_rival: 'your opponent',
    opp_machine: 'the machine',
    who_you: 'you',
    serve_wait: 'Your serve · the ball waits in your free hand',
    surv_start: 'SURVIVAL · keep the longest rally going',
    surv_new: 'New ball · TRIGGER to toss and hit',
    surv_opp: '{opp}’s serve… faster and faster',
    rally_big: 'Rally of {n} hits! · {cause}',
    rally_n: 'Rally of {n} {s} · {cause}',
    word_hit: 'hit',
    word_hits: 'hits',
    point_you: 'Point for you! · {cause}{rally}',
    point_opp: 'Point for {opp} · {cause}{rally}',
    rally_suffix: ' · {n} hits',
    retry_serve: '{cause} · serve again',
    serve_go: 'Your serve · TRIGGER to toss and hit',
    serve_opp: '{opp}’s serve…',
    over_win: 'YOU WON! · {p}-{q} · trigger: rematch',
    over_lose: 'YOU LOST! · {p}-{q} · trigger: rematch',
    cause_dblhit: 'double hit',
    cause_volley: 'hit before the bounce',
    cause_serve_no_own: 'serve without bouncing on your side',
    cause_let: 'LET · the ball clipped the net',
    cause_serve_net: 'the serve didn’t clear the net',
    cause_own_you: 'you hit your own side',
    cause_own_opp: '{opp} hit their own side',
    cause_dbl_you: 'double bounce: you didn’t reach it',
    cause_dbl_opp: 'double bounce: {opp} didn’t reach it',
    cause_back_you: 'the ball came back to your side',
    cause_back_opp: 'the ball came back to {opp}’s side',
    cause_serve_net_touch: 'serve into the net',
    cause_serve_out: 'serve out',
    cause_net_stay: 'it died in the net',
    cause_wall: 'into the wall',
    cause_out: 'ball out',
    cause_noret_you: 'you didn’t return it',
    cause_noret_opp: '{opp} didn’t return it',
    ann_score: '{p} to {q}, serve for {who}',
    ann_victory: 'Victory! {p} to {q}',
    ann_match_end: 'Match for {opp}. {p} to {q}',
    ann_rally_record: 'Rally of {n} hits. New record!',
    ann_ach: 'Achievement unlocked: {name}!',
    ann_room: '{room} arena',
    mode_survival: 'Survival mode. Keep the rally going!',
    mode_match: 'Match mode. Good luck!',
    welcome: 'Welcome to the match. Good luck!',
    opp_connected: 'Opponent connected. Let’s play!',
    opp_disconnected: 'Opponent disconnected',
    diff_easy: 'Easy difficulty',
    diff_medium: 'Medium difficulty',
    diff_hard: 'Hard difficulty',
    theme_pabellon: 'Gym',
    theme_neon: 'Neon',
    theme_atardecer: 'Sunset',
    theme_artico: 'Arctic',
    menu_title: 'MENU',
    menu_hint: 'aim with the paddle and pick with the TRIGGER',
    menu_b: 'B · close',
    tab_settings: 'SETTINGS',
    tab_multi: 'MULTIPLAYER',
    close_menu: 'Close menu',
    mode_label: 'GAME MODE',
    mode_match: 'Match',
    mode_survival: 'Survival',
    diff_label: 'CPU DIFFICULTY',
    diff_easy_btn: 'Easy',
    diff_medium_btn: 'Medium',
    diff_hard_btn: 'Hard',
    room_label: 'ROOM',
    extras_label: 'EXTRAS',
    lang_label: 'LANGUAGE',
    btn_amb: 'Crowd: {v}',
    btn_trail: 'Trail: {v}',
    btn_mic: 'Announcer: {v}',
    btn_music: 'Music: {v}',
    msg_music: 'Music {v}',
    btn_sndtest: '🔊 Sound test (3 notes)',
    msg_sndtest: 'Hear it? If not, press again to repair',
    msg_sndrepair: 'Rebuilding audio output… press again',
    btn_rematch: 'REMATCH',
    yes: 'On',
    no: 'Off',
    mj_head: 'PLAY AGAINST A REAL PERSON OVER THE INTERNET',
    mj_connected: 'CONNECTED',
    mj_rival: 'opponent: {code} · {st}',
    mj_playing: 'playing',
    mj_over: 'match over',
    voz_on_mic: 'Voice on (mic open)',
    voz_on_silent: 'Voice on (your mic is muted)',
    voz_asking: 'Asking for microphone…',
    voz_denied: 'Microphone denied',
    voz_off: 'No voice (press Voice to enable it)',
    btn_voz: 'Voice: {v}',
    btn_hangup: 'HANG UP',
    mj_rematch_hint: 'The rematch is in the SETTINGS tab.',
    mj_room_code: 'ROOM CODE',
    mj_waiting: 'Waiting for your rival… share this code',
    btn_cancel_room: 'CANCEL ROOM',
    mj_creating: 'Creating room…',
    mj_connecting: 'Connecting to {code}…',
    btn_cancel: 'CANCEL',
    mj_error: 'Network error',
    btn_retry: 'RETRY',
    btn_back: 'BACK',
    mj_off_hint: 'Create a room or join with a code.',
    btn_host: 'CREATE ROOM (code for your rival)',
    btn_join: 'ENTER A FRIEND’S CODE',
    mj_p2p: 'Direct P2P (WebRTC). Needs internet on both headsets.',
    mj_mic_hint: 'Voice uses the microphone: accept the browser permission.',
    join_title: 'YOUR FRIEND’S ROOM CODE',
    // ---- v2.28 · MAIN MENU (big floating panel with accordion)
    sec_match: 'PLAY MATCH',
    sec_train: 'TRAINING',
    sec_surv: 'SURVIVAL',
    sec_crazy: 'CRAZY',
    sec_opts: 'OPTIONS',
    btn_start: '▶  START MATCH',
    btn_start_surv: '▶  START SURVIVAL',
    btn_train_go: '▶  PRACTICE SHOTS',
    crazy_msg: 'Surprises coming soon..! 🎁',
    best_surv: 'Best: {n} hits',
    online_lbl: 'ONLINE · vs another player',
    train_hint: 'Ball machine + panel to tune your paddle with the sticks.',
    surv_hint: 'The CPU speeds up every rally · how many can you return?',
    menu_open: 'Main menu · aim and press the TRIGGER',
    msg_guest_mode: 'Asking the host to change mode…',
    msg_mode_changed: 'Mode: {m} · close the menu to play',
    mode_surv_word: 'SURVIVAL',
    mode_match_word: 'MATCH',
    msg_no_cpu: 'No CPU online · difficulty doesn’t apply',
    msg_diff: 'DIFFICULTY: {d}',
    msg_room: 'ROOM: {r}',
    msg_trail: 'Ball trail: {v}',
    msg_mic: 'Scoreboard announcer: {v}',
    hint_hit: 'Hit the ball toward the table with your paddle!',
    hint_toss_high: 'Toss the ball a bit higher',
    hint_behind: 'Serve from behind the end line',
    hint_dropped: 'Ball dropped · toss again',
    online_first: 'Connected! Waiting for the host…',
    online_serve: 'Online match · your serve (TRIGGER to toss)',
    net_ended: '{msg} · local match restarted',
    peer_gone: 'Your rival has left',
    conn_lost: 'Connection lost',
    peer_closed: 'Your rival closed the room',
    net_unavailable: 'Network unavailable in this browser',
    invalid_code: 'Invalid code (5 characters)',
    net_fail: 'Couldn’t start the network: {m}',
    status_creating: 'Creating room…',
    status_waiting: 'Room {c} · waiting for your rival…',
    status_joining: 'Connecting to room {c}…',
    room_not_found: 'Room {c} not found',
    no_lobby_server: 'No connection to the room server',
    sb_you: 'YOU',
    sb_cpu: 'CPU',
    sb_rival: 'RIVAL',
    calib_msg: 'TRAINING · Y: back to the previous mode',
    sb_surv: 'S U R V I V A L',
    sb_rally_hits: 'rally hits',
    sb_rallies: 'rallies {r}  ·  best {b}',
    fanf_win: 'YOU WON!',
    fanf_lose: 'YOU LOST!',
    fanf_chip: '{p} - {q} · trigger: rematch',
    ach_first: 'First victory',
    ach_first_d: 'Win your first match',
    ach_streak: 'On a roll',
    ach_streak_d: '3 wins in a row',
    ach_giant: 'Giant',
    ach_giant_d: 'Beat Hard difficulty',
    ach_marathon: 'Marathoner',
    ach_marathon_d: 'A rally of 20 or more hits',
    ach_survivor: 'Survivor',
    ach_survivor_d: '25 or more hits in Survival',
    ach_aces: 'Ace serve',
    ach_aces_d: '10 serves won unanswered',
    stats_line: '{won} wins · {lost} losses · streak {streak} (max {best}) · best rally {rally} · aces {aces}',
    status_pause: 'Paused · press the button to return to VR.',
    status_vr_checking: 'Checking WebXR compatibility…',
    status_vr_ok: '✅ Compatible headset detected. Put it on and press the button.',
    status_no_vr: '🖥️ No VR headset: enjoy spectator mode (AI vs AI).',
    status_no_webxr: '🖥️ WebXR not available here: spectator mode active.',
    status_no_2d: '🖥️ This browser does not support WebXR: spectator mode active.',
    status_starting_vr: 'Starting VR session…',
    status_starting_train: 'Starting VR in training mode…',
    status_starting_surv: 'Starting VR in survival mode…',
    status_starting_ar: 'Starting passthrough…',
    status_vr_fail: 'Could not start the VR session.',
    status_ar_fail: 'Could not start passthrough.',
    amb_yes: '🔊 Tournament crowd: ON',
    amb_no: '🔇 Tournament crowd: OFF',
    ov_tag: 'ITTF rules · free-hand serve and real physics · 3D paddle · Meta Quest 3',
    ov_serve: '<b>SERVE</b> The ball rests in your <b>free hand</b>. Press the <b>TRIGGER</b> (either controller) to toss and hit it with the paddle; or release the <b>GRIP</b> of your free hand flicking your hand upward. No dead-point waiting: hit whenever you like — the serve self-corrects.',
    ov_hit: '<b>HIT</b> Strike the ball with the paddle (your other controller) from behind the end line. The sweet spot is very forgiving, even larger on serves: no pixel-perfect aim needed. The serve must bounce on <b>your side</b> and then on the opponent’s.',
    ov_hand: '<b>A / X</b> Switch the paddle between hands at any time',
    ov_menu: '<b>MENU</b> In VR press <b>B</b> (right controller): a panel opens <b>on your free wrist</b>. Aim with <b>either controller</b> (the paddle has a laser too) and pick with the <b>trigger</b>: mode (Match / Survival), CPU difficulty, room (Gym · Neon · Sunset · Arctic), tournament crowd, ball trail, scoreboard announcer and language. Everything applies instantly and is remembered between sessions.',
    ov_online: '<b>ONLINE</b> In the menu, <b>MULTIPLAYER</b> tab: create a room, share the <b>5-character code</b> and your rival types it in their menu. Direct P2P match between headsets (both with the web open) and <b>you can even talk</b>: accept the microphone permission.',
    ov_rules: '<b>RULES</b> Grazing the net on a serve and landing in = <b>LET</b> (replay) · volleying before the bounce or double-hitting = fault · first to 11, win by 2',
    ov_spin: '<b>SPIN</b> Brush the paddle bottom-up at impact for topspin; top-down for backspin',
    ov_train: '<b>TRAIN</b> In VR press <b>Y</b> (any time): ball machine + panel to fine-tune the paddle with the sticks. Save your grips with a name and load them any time.',
    ov_difficulty: 'DIFFICULTY',
    ov_room: 'ROOM',
    ov_grips: 'PADDLE GRIPS',
    ov_grip_ph: 'Name to save the current setup',
    ov_grip_load: 'Load',
    ov_grip_save: 'Save',
    ov_grip_del: 'Delete',
    ov_grip_reset: 'Natural',
    ov_progress: 'YOUR PROGRESS',
    ov_clear: 'Clear',
    ov_surv: '🏆 SURVIVAL IN VR · how many hits can you take?',
    ov_train_btn: 'TRAIN SHOTS IN VR · adjust paddle',
    ov_vr: 'ENTER VR',
    ov_ar: '🏠 PASSTHROUGH · your room',
    ov_demo: 'Watch demo on screen (no headset)',
    music_title: 'Music (landing and VR menu)',
    ov_hint: '<b>On the headset:</b> upload this folder to <b>Netlify Drop</b> and open the link with the <b>Meta Quest Browser</b> (HTTPS required). Without a headset, demo mode plays AI vs AI.',
    ov_lang: '🌐 Language / Idioma',
  },
};

/** Traducción con parámetros: T('clave', {p: 3}) sustituye {p}. */
function T(key, params) {
  let s = (I18N_STRINGS[__ppLang] || I18N_STRINGS.es)[key];
  if (s === undefined) s = I18N_STRINGS.es[key];
  if (s === undefined) return key;
  if (params) {
    for (const p in params) {
      if (Object.prototype.hasOwnProperty.call(params, p)) {
        s = s.split('{' + p + '}').join(String(params[p]));
      }
    }
  }
  return s;
}

/** Idioma activo. */
function TLang() { return __ppLang; }

/** Aplica el idioma activo al overlay 2D (elementos con data-i18n). */
function applyLangDOM() {
  try {
    document.querySelectorAll('[data-i18n]').forEach((el) => {
      el.textContent = T(el.getAttribute('data-i18n'));
    });
    document.querySelectorAll('[data-i18n-html]').forEach((el) => {
      el.innerHTML = T(el.getAttribute('data-i18n-html'));
    });
    document.querySelectorAll('[data-i18n-ph]').forEach((el) => {
      el.placeholder = T(el.getAttribute('data-i18n-ph'));
    });
    document.querySelectorAll('[data-i18n-title]').forEach((el) => {
      el.title = T(el.getAttribute('data-i18n-title'));
    });
    document.documentElement.lang = __ppLang;
    // botones ES/EN del overlay
    document.querySelectorAll('[data-lang]').forEach((b) => {
      b.classList.toggle('active', b.dataset.lang === __ppLang);
    });
    // dificultad (Fácil/Media/Difícil) y salas (emoji + nombre)
    document.querySelectorAll('[data-diff]').forEach((b) => {
      b.textContent = T('diff_' + b.dataset.diff + '_btn');
    });
    document.querySelectorAll('[data-theme]').forEach((b) => {
      const m = b.textContent.trim().match(/^(\S+)\s/);
      const emoji = m ? m[1] + ' ' : '';
      b.textContent = emoji + T('theme_' + b.dataset.theme);
    });
    if (typeof window !== 'undefined' && window.__game) {
      // el estado puede haber quedado en otro idioma: repintar UI viva
      if (window.__game.menuOpen && window.__game.drawMenu) window.__game.drawMenu();
      if (window.__game.stats) window.__game.emitStats();
    }
  } catch { /* DOM aún no listo */ }
}

/** Cambia el idioma, persiste y avisa al resto del juego. Los textos que se
 *  regeneran en cada estado (mensajes del árbitro, menú, marcador) salen en
 *  el idioma nuevo en cuanto vuelven a pintarse; los estáticos (overlay 2D)
 *  se actualizan con applyLangDOM(). */
function setLang(l, game) {
  if (l !== 'es' && l !== 'en') return;
  __ppLang = l;
  try { localStorage.setItem('pp_lang', l); } catch { /* */ }
  if (game) {
    // banco de voz del idioma nuevo + cartel en pantalla + menú vivo
    if (game.audio && game.audio.reloadVoice) game.audio.reloadVoice();
    if (game.fanfareBanner && game.fanfareBanner.langChanged) game.fanfareBanner.langChanged();
    if (game.menuOpen && game.drawMenu) game.drawMenu();
  }
  applyLangDOM();
  try { document.dispatchEvent(new CustomEvent('pp-lang')); } catch { /* */ }
}
