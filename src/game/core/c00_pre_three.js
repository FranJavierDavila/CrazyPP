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
export let __ppLang = 'es';
try {
  const saved = localStorage.getItem('pp_lang');
  if (saved === 'en' || saved === 'es') __ppLang = saved;
  else {
    // M4 (r111) · IDIOMA DETECTADO antes del primer toque: sólo para quien
    // NUNCA ha jugado (las huellas pp_tut_asked/pp_seen_v1 intactas delatan
    // la primera instalación; quien ya jugaba no cambia de idioma jamás).
    // es* → ES · resto → EN. Queda recordado en pp_lang como si el jugador
    // lo hubiera elegido (el selector de la portada lo cambia igual).
    const primera = !localStorage.getItem('pp_tut_asked') &&
                    !localStorage.getItem('pp_seen_v1');
    if (primera) {
      const nav = String(navigator.language || 'es').toLowerCase();
      __ppLang = (nav.slice(0, 2) === 'es') ? 'es' : 'en';
      try { localStorage.setItem('pp_lang', __ppLang); } catch { /* */ }
    }
  }
} catch { /* sin localStorage: castellano */ }

const I18N_STRINGS = {
  /* --------------------------- CASTELLANO --------------------------- */
  es: {
    // ---- nombres de oponente / personas
    opp_cpu: 'la CPU',
    opp_rival: 'tu rival',
    opp_machine: 'la máquina',
    opp_wizard: 'WIZARD', // v2.54: rival del Nuevo truco de Magia (Nubes ELIMINADO en v2.56)
    opp_clown: 'CLOWN', // v2.86: faltaba — la clave cruda salía en los duelos de La Locura
    opp_forajido: 'el FORAJIDO', // v2.86: rival del Campeonato del Salvaje Oeste
    who_you: 'ti',
    // ---- mensajes del árbitro (Rules)
    serve_wait: 'Tu saque · la bola espera en tu mano libre',
    // r128 · E2 (auditoría r120): aviso de almacenamiento lleno o bloqueado
    storage_lleno: 'AVISO: el almacenamiento está lleno o bloqueado y el progreso puede no guardarse. Libera espacio en el navegador del casco.',
    // M4 (r111) · ONBOARDING < 60 s: tres claves nuevas (ES)
    hub_play: '▶ JUGAR',
    // r67 · FASE 161 · EL VESTÍBULO (títulos de paneles + dock)
    vest_jugar: 'JUGAR',
    vest_compite: 'COMPITE',
    vest_casa: 'TU CASA',
    dock_tv: 'TV en vivo',
    dock_intro: 'Intro',
    dock_instalar: 'Instalar',
    dock_apoyar: 'Apoyar',
    dock_salir: 'Salir a la web',
    // r58 · FASE 152 · CONFIG_MENU: tarjeta SALIR A LA WEB del HUB (ES)
    hub_salirweb: 'SALIR A LA WEB',
    hub_salirweb_sub: 'Cerrar el juego y volver a la página principal',
    salirask_title: '¿SALIR A LA WEB?',
    salirask_sub: 'El juego se cerrará y volverás a la página principal.',
    salirask_yes_btn: 'SÍ, SALIR',
    salirask_no_btn: 'NO, SEGUIR JUGANDO',
    salirask_hint: 'B: cancelar',
    hint_salirweb: 'Cierra el juego · vuelve a la web principal',
    first_hint: 'Bienvenido · pulsa ▶ JUGAR y estarás jugando en segundos',
    srv_guide: 'GUÍA DE SAQUE · GATILLO para lanzar → golpéala al caer y pásala por el aro dorado',
    // M5a (r112) · IA CON ESTILOS: selector y anuncio
    estilo_lbl: 'Estilo del rival',
    msg_estilo: 'Rival: {v} · misma física, otro carácter',
    // M5b (r115) · ESCALERA DE CARRERA: divisiones, rivales y progreso
    carrera_lbl: 'Escalera de carrera',
    carrera_sub: 'Bronce → Leyenda · tres rivales por división',
    carrera_hint: 'Gana a los 3 para ascender · las derrotas no bajan: revancha cuando quieras',
    carrera_hub_sub: '{v} · {n}/3 rivales',
    carrera_d_bronce: 'BRONCE',
    carrera_d_plata: 'PLATA',
    carrera_d_oro: 'ORO',
    carrera_d_diamante: 'DIAMANTE',
    carrera_d_leyenda: 'LEYENDA',
    carrera_actual: 'DIVISIÓN ACTUAL',
    carrera_superada: 'SUPERADA',
    carrera_bloqueada: 'BLOQUEADA',
    carrera_challenge: 'DESAFIAR A {v}',
    carrera_rematch: 'REVANCHA CONTRA {v}',
    carrera_vencido: 'VENCIDO',
    carrera_pendiente: 'PRÓXIMO',
    carrera_win_msg: '¡Victoria de la escalera contra {v}!',
    carrera_lose_msg: 'Derrota contra {v} · la revancha te espera',
    carrera_promo_msg: '¡ASCIENDES A LA DIVISIÓN {v}!',
    carrera_crown_msg: '¡CORONA DE LEYENDA! La escalera es tuya',
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
    // v3.6.29 · MEJOR DE 3 (ronda 37): mensajes de juego y enfrentamiento
    game_won_you: 'JUEGO PARA TI · {p}-{q} · serie {a}-{b} · ¡sigue así!',
    game_won_opp: 'JUEGO PARA {opp} · {p}-{q} · serie {a}-{b} · ¡al siguiente!',
    over_win_bo: '¡ENFRENTAMIENTO PARA TI! · Juegos {a}-{b} · último {p}-{q}',
    over_lose_bo: 'ENFRENTAMIENTO PARA {opp} · Juegos {a}-{b} · último {p}-{q}',
    // ---- causas (viajan por red como CLAVES; se traducen al pintar)
    cause_dblhit: 'doble golpe',
    cause_volley: 'golpe antes del bote',
    cause_burla: 'comodín de la Burla',
    cause_elec: 'fulminada por la SÚPER ELECTRICIDAD',
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
    // v3.6.29 · MEJOR DE 3: megafonía de juego y de enfrentamiento
    ann_game_you: 'Juego para ti. {a} a {b} en juegos',
    ann_game_opp: 'Juego para {opp}. {a} a {b} en juegos',
    ann_victory_bo: '¡Enfrentamiento para ti! {a} juegos a {b}',
    ann_match_end_bo: 'Enfrentamiento para {opp}. {a} juegos a {b}',
    ann_rally_record: '¡Rallye de {n} golpes! Nuevo récord',
    ann_ach: '¡Logro desbloqueado: {name}!',
    ann_room: 'Sala {room}',
    mode_survival: 'Modo supervivencia. ¡Aguanta el rallye!',
    mode_match: 'Modo partido. ¡Buena suerte!',
    welcome: 'Bienvenido al partido. ¡Buena suerte!',
    welcome_menu: 'Bienvenido a Crazy Ping Pong, escoge una modalidad de juego',
    hall_sign: 'HALL OF FAME',
    hall_sign_sub: 'CRAZY PING PONG · SALÓN DEL ANFITRIÓN',
    hall_welcome: 'Bienvenido a tu hall · escoge modalidad en el panel',
    hall_champs: 'CAMPEONATOS CONSEGUIDOS',
    hall_achs: 'LOGROS CRAZY',
    hall_circ: 'PRO CIRCUITO',
    hall_palas: 'PIEL DE PALA',
    hall_rank_title: 'RÉCORD Y RANKING',
    hall_rank_v: 'VICTORIAS',
    hall_rank_s: 'MEJOR RACHA',
    hall_rank_r: 'MEJOR RALLYE',
    hall_rank_a: 'SAQUES DIRECTOS',
    hall_quote: '«Un campeón se forja en los rallyes que nadie ve»',
    hall_locked: 'BLOQUEADA',
    hall_trophy_wait: 'EL TROFEO ESPERA A SU PRIMER CAMPEÓN',
    hall_trophy_won: 'SALÓN DE CAMPEONES',
    menu_pin_off: 'Chincheta: el menú sigue tu cabeza',
    menu_pin_on: 'Chincheta puesta: menú anclado aquí',
    hall_door: 'A LA CANCHA ›',
    hall_home_btn: '⌂ VOLVER AL HALL',
    hall_home_hint: 'El hall es tu casa: ajustes y cambio de modo viven allí',
    // r74 · FASE 168 · ESCOGER HALL
    hall_pick_btn: '⌂ ESCOGER HALL',
    hall_pick_t: 'ESCOGER HALL',
    hall_pick_hint: 'tu estancia: el museo clásico y los salones que desbloquees',
    hall_actual: 'ACTUAL',
    hall_disponible: 'disponible',
    hall_visita: 'De visita online ves el salón del ANFITRIÓN',
    hallask_title: 'MENÚ PRINCIPAL',
    hallask_sub: '¿Salir al Hall del anfitrión?',
    hallask_yes_btn: 'SÍ, SALIR AL HALL',
    hallask_no_btn: 'No, seguir aquí',
    hallask_hint: 'SÍ te lleva al Hall con el menú abierto · NO cierra esta ventana y sigues jugando',
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
    theme_nocturna: 'Nocturna 🌙',
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
    // M4 (r118) · ELO unificado + matchmaking + MI RANKING
    mm_label: 'MATCHMAKING POR ELO',
    mm_btn: 'Rival a tu nivel · ELO ~{n}',
    mm_armado: 'Rival a tu nivel armado: ELO ~{n} ({d})',
    mm_rival: 'Rival ELO ~{n}',
    rankme_btn: 'MI RANKING (ELO)',
    rankme_t: 'MI RANKING',
    // r70 · FASE 164 · apartados en formato Ajustes (landing rejilla)
    rank_tab_t: 'TABLA MUNDIAL',
    trainext_t: 'PERFIL Y EXTRAS',
    rankme_sub: 'Tu número de habilidad — local y honesto',
    rankme_hist: 'HISTORIAL · últimos cambios',
    rankme_racha_a: 'Racha actual',
    rankme_racha_m: 'Mejor racha',
    rankme_mejordia: 'Mejor día',
    rankme_marca: 'Victorias {w} · derrotas {l}',
    rankme_dia: '{v} victorias',
    rankme_vacio: 'Sin partidos todavía — juega uno y tu ELO vivirá',
    rankme_leyenda: 'K por modo: IA 24 · escalera 20 · humano 32 · diario/entreno no cuentan',
    rankme_ia: 'IA', rankme_carrera: 'escalera', rankme_p2p: 'humano',
    // M7c (r119) · DOBLES 2v2 (prototipo)
    dobles_btn: 'DOBLES 2v2 — pruébalo',
    dobles_msg: '¡DOBLES! Tu compañero cubre la bola que no llegues a tocar',
    room_label: 'SALA',
    extras_label: 'EXTRAS',
    lang_label: 'IDIOMA',
    btn_amb: 'Ambiente: {v}',
    btn_trail: 'Estela: {v}',
    // r61 · IA adaptativa visible + repetición del mejor intercambio
    btn_adapt: 'Rival adaptativo: {v}',
    // r115: rep_t/rep_slow/rep_chip retirados con la repetición del mejor
    // intercambio (petición del dueño)
    btn_mic: 'Megáfono del marcador: {v}',
    btn_music: 'Música: {v}',
    msg_music: 'Música {v}',
    // v2.50 · FASE 1 · confort + telemetría + apoyo Ko-fi
    btn_hapt: 'Vibración en los golpes: {v}',
    msg_hapt: 'Vibración {v}',
    btn_tips: 'Consejos para empezar: {v}',
    msg_tips: 'Consejos {v}',
    btn_tele: 'Telemetría anónima: {v}',
    msg_tele: 'Telemetría {v}',
    tele_hint: 'Anónima: sin datos personales. Ayuda a mejorar el juego.',
    btn_kofi: '☕ Apoyar el proyecto (Ko-fi)',
    msg_kofi: '¡Gracias! ☕ Se abre Ko-fi en el navegador',
    tip_1: 'CONSEJO · Saca con el gatillo: lanza la bola hacia arriba y golpéala',
    tip_2: 'CONSEJO · Gira la muñeca para dar EFECTO (topspin/cut) a la bola',
    tip_3: 'CONSEJO · Botón B = menú · A/X = cambiar pala de mano',
    tip_bye: '¡A jugar! Gana al CLOWN y conquista el Campeonato de la Locura',
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
    voz_error: 'Sin micrófono en este dispositivo',
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
    // r79 · submenú multijugador: NORMAL + DUELOS LOCOS (petición del dueño)
    mj_norm_t: 'NORMAL · PARTIDA',
    mj_norm_s: '1 vs 1 online · mejor de 3 juegos · golpe propio sin latencia',
    mj_duel_t: 'DUELOS LOCOS',
    mj_duel_s: '1 vs 1 online con poderes locos · gatillo para lanzarlos',
    // r74 · FASE 169 · EL MULTIJUGADOR EN TRES ZONAS
    mj_crear_t: 'CREAR PARTIDA',
    mj_disp_t: 'PARTIDAS DISPONIBLES',
    mj_priv_t: 'SALA PRIVADA',
    mj_priv_hint: 'entra con el código que te haya pasado el creador',
    mj_sin_pub: 'no hay partidas públicas ahora mismo · crea la tuya',
    mj_sin_soc: 'la capa social está sin conexión: sin listado en vivo',
    mj_entrar: 'ENTRAR',
    mj_hace: 'hace {n}s',
    mj_mas_pub: '+{n} más en la lista del pulso',
    mj_vis_pregunta: '¿Cómo abres la sala?',
    mj_vis_pub: 'PÚBLICA · para todos',
    mj_vis_pub_sub: 'se anuncia a los conectados y aparece en Partidas disponibles',
    mj_vis_pri: 'PRIVADA · sólo código',
    mj_vis_pri_sub: 'nadie la ve: entra quien tenga el código que les pases',
    rs_jugador: 'Jugador',
    // r74 · FASE 170 · LA ALERTA DE DUELO
    duelo_alerta_voz: 'Un jugador ha aceptado tu invitación de duelo',
    duelo_alerta_msg: 'DUELO EN ESPERA: un jugador aceptó tu invitación — icono arriba o Multijugador',
    dueloask_t: 'ACEPTAR EL DUELO',
    dueloask_sub: 'Un jugador ha aceptado tu invitación de duelo.',
    dueloask_hint: 'si aceptas, se cierra lo que estás haciendo y saltas a la partida — perderás cualquier registro generado',
    dueloask_si: 'SÍ, ACEPTAR Y JUGAR',
    dueloask_no: 'NO, SEGUIR AQUÍ (colgar)',
    // r84 · DUELOS LOCOS desbloqueado: poderes de la partida online
    mode_duelos: '¡DUELOS LOCOS! · mejor de 3 con poderes',
    dl_listo: '¡Poder listo! · gatillo para lanzarlo',
    dl_poder_listo: 'PODER LISTO · gatillo',
    dl_gigante: 'PALA GIGANTE',
    dl_fuego: 'BOLA FUEGO',
    dl_loca: 'BOLA LOCA',
    dl_bolaloca: 'BOLA LOCA',
    dl_rival: 'de tu rival',
    // r84 · cartel del HALL para EL PULSO CRAZY (puerta física del museo)
    pulso_hall_t: 'EL PULSO CRAZY',
    pulso_hall_m: 'Reto de hoy: {m}',
    pulso_racha_t: 'TU RACHA',
    pulso_racha_s: '{n} día(s) · récord {r}',
    pulso_racha_0: 'Aún sin racha · ¡juega el reto de hoy!',
    mj_ping: '{n} ms',
    net_syncing: 'Sincronizando con el rival…',
    // r80 · submenú que respira + EL RETO DIARIO EN LA PUERTA (dueño)
    mj_pick: 'Elige un modo de juego para continuar',
    mj_sel_back: '◀  MODOS',
    daily_btn_t: 'Reto Diario!',
    daily_btn_new: 'Duelo de hoy: {m} · racha: {n}',
    daily_btn_done: 'Completado hoy · racha: {n} · vuelve mañana',
    daily_btn_zona: 'zonas el doble de amplias · nuevo duelo cada medianoche',
    net_paused: 'RIVAL EN PAUSA · el partido queda detenido',
    net_paused_long: 'RIVAL EN PAUSA (mucho tiempo) · esperando…',
    net_legacy: 'Sin canal rápido: modo compatible 30 Hz',
    // r82 · AL MILÍMETRO: el enlace se canta y se diagnostica
    net_link_direct: 'Enlace directo establecido',
    net_link_tunnel: 'Enlace por túnel establecido',
    // r126 · P4.1 · aviso de build EN LA SALA (primera partida real: nadie
    // veía el del menú con la visera puesta). Texto genérico, versiones vivas.
    net_build_warn: 'Tu rival usa OTRA versión ({a} vs {b}): recargad el juego en los DOS visores y cread la sala de nuevo',
    net_build_voice: 'rival con otra versión recargad el juego en los dos visores',
    // r127 · P4.2 · autodiagnóstico de versión al arrancar: si los DOS
    // cascos quedaron viejos, el HELLO no lo ve — el propio build se
    // compara contra la web (PAGES-VERSION.txt, red primero).
    net_selfcheck_warn: 'Estás en una versión ANTIGUA ({b}) · en la web hay la {a}: cierra y reabre la web para actualizarte',
    net_selfcheck_voice: 'versión antigua cierra y reabre la web para actualizarte',
    net_v2_down: 'Sin enlace binario con el rival · revisad Internet y recargad',
    join_title: 'CÓDIGO DE LA SALA DE TU AMIGO',
    btn_connect: 'CONECTAR',
    // ---- v2.28 · MENÚ PRINCIPAL (gran panel flotante con acordeón)
    sec_match: 'JUGAR PARTIDO',
    sec_train: 'ENTRENAR',
    sec_surv: 'SUPERVIVENCIA',
    sec_crazy: 'CAMPEONATOS',
    sec_opts: 'OPCIONES',
    btn_start: '▶  EMPEZAR PARTIDO',
    btn_start_surv: '▶  EMPEZAR SUPERVIVENCIA',
    btn_train_go: '▶  ENTRENAR GOLPES',
    crazy_msg: '¡Sorpresas pronto..! 🎁',
    // ---- v2.66 · NOMBRE PARA EL RANKING + REINICIO DE REGISTROS
    opts_name: 'TU NOMBRE: {v}',
    name_title: 'TU NOMBRE PARA EL RANKING',
    name_hint: 'Apunta con el rayo y pulsa el gatillo para escribir',
    name_save: 'GUARDAR NOMBRE',
    reset_btn: 'REINICIAR REGISTROS',
    reset_arm: '¿BORRAR TODO? TOCA OTRA VEZ',
    reset_done: '¡Registros borrados! A empezar de cero.',
    no_name: '—',
    // ---- r156 · MI PERFIL (ficha del jugador + tienda de avatares)
    perfil_title: 'MI PERFIL',
    perfil_sub: 'Tu ficha de jugador: nivel, rango ELO, insignias y tienda',
    hub_jugar: 'JUGAR',
    jugar_sub: 'Partido · Carrera · Entrenamiento · Supervivencia · Tutorial',
    perfil_editar: 'EDITAR PERFIL',
    perfil_edit_t: 'EDITAR PERFIL',
    perfil_nivel: 'Nivel',
    perfil_rango: 'Rango actual',
    perfil_partidos: 'Partidos',
    perfil_victorias: 'Victorias',
    perfil_racha: 'Racha',
    perfil_monedas: 'Monedas',
    perfil_insignias: 'Insignias',
    perfil_pais: 'País',
    perfil_avatar: 'Avatar',
    perfil_marco: 'Marco',
    perfil_guardar: 'GUARDAR',
    perfil_guardado: '¡Perfil guardado!',
    perfil_sin_pais: 'Internacional',
    perfil_rank_btn: 'RANKING MUNDIAL',
    perfil_tienda: 'Tienda de avatares y marcos',
    perfil_compra: '¿Comprar {v} por {n} monedas? TOCA OTRA VEZ',
    perfil_compra_ok: '¡Comprado y equipado!',
    perfil_falta: 'Te faltan {n} monedas',
    perfil_lock_logro: 'Se desbloquea con la insignia «{v}»',
    perfil_lock_elo: 'Requiere ELO {v}',
    perfil_equipado: 'Equipado',
    perfil_xp_txt: '{a} / {b} XP',
    perfil_nombre: 'Nombre',
    perfil_movida: 'El nombre, el país y el avatar se editan en MI PERFIL › EDITAR.',
    // ---- v2.67 · RANKING MUNDIAL (top 10 por campeonato)
    sec_rank: 'RANKING MUNDIAL',
    wrl_open: '🌍  ABRIR RANKING MUNDIAL',
    wrl_points: 'PUNTOS',
    wrl_wins: 'VICTORIAS',
    wrl_col_name: 'NOMBRE',
    wrl_col_logros: 'LOGROS',
    wrl_online: 'Mundial · en línea',
    wrl_offline: 'Sin conexión · últimos datos guardados',
    wrl_loading: 'Cargando ranking mundial…',
    wrl_you: 'TÚ',
    wrl_need_name: 'Escribe tu nombre en Opciones → TU NOMBRE para firmar tus registros',
    wrl_refresh: '↻ ACTUALIZAR',
    wrl_refresh_short: '↻',
    wrl_2d_hint: 'El ranking se publica solo al ganar: firma tus registros con TU NOMBRE en Opciones (dentro del juego).',
    best_surv: 'Récord: {n} golpes',
    // ---- v2.110 · MENÚ HUB (tarjetas de modos + páginas) ----
    hub_match: 'PARTIDO',
    hub_vs: 'vs CPU · {v}',
    hub_train_sub: 'PRO TRAINING · 5 áreas + skins',
    hub_surv_sub: 'Aguanta la ráfaga',
    hub_multi: 'MULTIJUGADOR',
    hub_multi_sub: 'Partido online P2P',
    // r87 · RED SOCIAL DEL PULSO (medallón + invitaciones)
    rs_aviso: '🎮 ¡INVITACIÓN RECIBIDA! — Menú ▸ Multijugador',
    rs_online: '{n} jugador(es) online',
    rs_invita_de: 'Invitación de {n}',
    rs_invita_code: 'Código de sala: {c} — únete ya',
    rs_unirse: 'UNIRSE',
    rs_invitar: 'INVITAR',
    rs_descartar: 'Descartar',
    hub_multi_on: 'Conectados · sala {c}',
    hub_champ_sub: 'Locura · Magia · Oeste',
    hub_rank_sub: 'Top 10 mundial',
    hub_diff: 'DIFICULTAD DE LA CPU',
    dock_label: 'AJUSTES RÁPIDOS',
    dock_mic: 'Megáfono',
    dock_hapt: 'Vibración',
    page_back: '‹  MENÚ',
    page_champs: 'CAMPEONATOS',
    page_opts: 'AJUSTES ›',
    opts_title: 'AJUSTES',
    // r71 · AJUSTES POR SUBCATEGORÍAS (petición del dueño: «mejor organizado
    // por subcategorías con iconos explícitos de cada una, un diseño bonito»)
    opts_elegir: 'Toca una categoría para entrar',
    cat_juego: 'JUEGO',
    cat_juego_sub: 'Dificultad de la CPU, rival adaptativo y pala mejorada',
    cat_sala: 'SALA Y ESCENA',
    cat_sala_sub: 'La sala, la vista y el passthrough',
    cat_sonido: 'SONIDO',
    cat_sonido_sub: 'Música, ambiente, megáfono y prueba',
    cat_visual: 'VISUALES',
    cat_visual_sub: 'Estela, vibración y consejos',
    cat_perfil: 'PERFIL Y DATOS',
    cat_perfil_sub: 'Tu nombre, telemetría y borrado',
    // r81 · RENDIMIENTO: autocalibrador de FPS (≥60 seguros en cualquier casco)
    cat_rendi: 'RENDIMIENTO',
    cat_rendi_sub: 'FPS, calidad automática y calibración por casco',
    perf_device: 'Dispositivo: {v}',
    perf_fps: 'FPS ahora: {v} · casco a {r} Hz',
    perf_fps_short: '{v} FPS',
    perf_auto: 'Calibración automática: {v}',
    perf_calidad: 'PERFIL DEL CASCO',
    perf_tier_auto: 'AUTO',
    perf_t_quest3: 'Quest 3 · máxima',
    perf_t_quest2: 'Quest 2 · fluida',
    perf_escala: 'Resolución de la próxima sesión: ×{v}',
    perf_recal: 'RECALIBRAR AHORA',
    perf_recal_next: 'RECALIBRAR AL ENTRAR EN VR',
    perf_calibrando: 'Calibrando… ronda {s}',
    perf_cal_ok: 'Listo: {f} FPS estables en tu visor',
    perf_estado_ok: 'FLUIDO',
    perf_estado_bajo: 'BAJO FPS · ajustando',
    perf_stepdown: 'Optimizando la imagen para ir fluido',
    msg_perf_auto: 'Autocalibración {v}: la calidad se adapta sola a tu visor',
    msg_perf_recal_next: 'Perfecto: la calibración arrancará al entrar en VR',
    // r77 · FASE 173 · RED: calidad de servicio en una línea
    net_red: 'RED {p} ms · {e}',
    net_q_excelente: 'EXCELENTE',
    net_q_bien: 'BIEN',
    net_q_ajustada: 'AJUSTADA',
    net_q_tun60: 'TÚNEL · 60',
    net_q_tun30: 'TÚNEL · 30',
    // r78 · FASE 174 · ALERTAS + SALA PÚBLICA EN ESPERA
    btn_alertas: 'Alertas de retos: {v}',
    msg_alertas_on: 'Alertas activadas: te avisamos de los retos públicos',
    msg_alertas_off: 'Alertas silenciadas: los retos públicos no interrumpen (se aceptan en MULTIJUGADOR)',
    btn_espera: 'Dejar en espera · MI CASA',
    hub_multi_espera: 'SALA {c} EN ESPERA · pública',
    // r79 · FASE 175 · el MENÚ NUNCA SE DESANCLA + arreglos del dueño
    btn_gestiona: 'GESTIONAR SALA',
    pala_salir_ask: '¿Abandonar el ajuste de la pala?',
    pala_salir_hint: 'El ajuste sigue vivo hasta que confirmes con SÍ (B abre este menú dentro del modo)',
    hist_empty_hint: 'Vence campeonatos y quedarán aquí sellados con su fecha y sus victorias',
    // r80 · FASE 176 · nombres de las ÁREAS de entrenamiento (el título de
    // la concha salía con la clave cruda «a_dir»)
    a_dir: 'DIRECCIÓN', a_alt: 'ALTURA', a_spin: 'EFECTO',
    a_saq: 'SAQUE', a_rit: 'RITMO',
    // r83 · AJUSTES › PALA: el ajuste de la pala abandona el PRO TRAINING y
    // gana su propio subapartado con botón bonito, passthrough al instante,
    // ejes X/Y/Z completos y agarres guardados en el dispositivo.
    cat_pala: 'PALA',
    cat_pala_sub: 'Agarre, posición y colocación al milímetro',
    pala_actual: 'Agarre actual: {v}',
    pala_go: 'AJUSTAR LA PALA EN VR',
    pala_go_sub: 'Passthrough al instante · verás tu mando real para colocarla perfecta',
    pala_help: 'Sticks: girar (der.) · mover (izq.) · stick pulsado o GRIP = eje Z',
    pala_guardados: 'AGARRES GUARDADOS',
    pala_ninguno: 'Aún no hay agarres guardados (guárdalos con A dentro del ajuste)',
    pala_nat: 'VOLVER AL AGARRE NATURAL',
    pala_gname: 'GUARDAR EL AJUSTE ACTUAL CON NOMBRE',
    pala_gname_title: 'NOMBRE DEL AGARRE',
    pala_pst: 'PASSTHROUGH ACTIVO · mandos reales a la vista',
    pala_replica: 'RÉPLICA 3D DE LOS MANDOS · referencia de colocación',
    msg_pala_on: 'Coloca la pala sobre tu mando real: passthrough activado',
    msg_pala_del: 'Agarre borrado',
    msg_pala_online: 'El ajuste de pala no está disponible en partida online',
    hub_champ_hint: 'Toca para entrar',
    champ_intro_btn: 'VER PRESENTACIÓN · vídeo del rival',   // v3.6.31: re-ver la intro (opcional)
    // ---- v2.34 · ARCADE "Campeonato de la Locura" (rival CLOWN) ----
    arcade_go: '▶  CAMPEONATO DE LA LOCURA',
    arcade_hint: 'Partida a 11 contra el CLOWN · cada victoria suma al ranking y desbloquea el poder MEGA PALA.',
    arcade_record: 'Rondas ganadas: {n} · Racha actual: {s}',
    arcade_none: 'Aún sin rondas ganadas · ¡derrota al Clown!',
    arc_rank_empty1: 'Aún sin rondas ganadas',
    arc_rank_empty2: '¡derrota al Clown!',
    best_arcade: 'Rondas ganadas: {n}',
    // M7e (r124) · historial de torneos + perfil recordado
    hist_title: 'HISTORIAL DE TORNEOS',
    hist_btn: '📜 Ver historial de torneos',
    hist_empty: 'Aún no has sellado ningún torneo. Gana un campeonato y quedará aquí para siempre.',
    hist_wins: '{n} victorias',
    hist_sellado: 'sellado el {f}',
    perfil_titulo: 'TU PERFIL · RECORDADO',
    perfil_skin: 'Piel de la mesa: {v}',
    perfil_alto: 'Alto de la mesa: {v}',
    perfil_pala: 'Pala mejorada: {v}',
    perfil_estilo: 'Rivales con estilo: {v}',
    perfil_pid: 'Jugador anónimo: {v}…',
    msg_arcade: '¡CAMPEONATO DE LA LOCURA! Derrota al Clown',
    msg_arcade_menu: 'El Clown te espera en el Campeonato de la Locura',
    arc_title: 'CAMPEONATO DE LA LOCURA',
    arc_announce: 'Bienvenido al Campeonato de la Locura. Derrota al Clown.',
    arc_no_data: 'Campeonato no disponible en esta build',
    cartel_new: '¡PARTIDA NUEVA!',
    cartel_vs: 'VS CLOWN · Ronda {n}',
    // v3.6.34 · MEGA PALA NORMATIVA (núcleo): la carga llega con un rally
    // que SUPERA los 10 golpes (norma en TODOS los campeonatos), el aviso
    // es el ICONO sobre el mango + jingle propio (adiós núcleo dorado) y
    // el uso sigue siendo VOLUNTARIO (gatillo con la bola en juego).
    arc_combo: '¡CRAZY COMBO! ¡MEGA PALA CARGADA!',
    arc_combo_locked: '¡CRAZY COMBO! Gana una ronda para desbloquear la MEGA PALA',
    arc_mega_go: '¡MEGA PALA ACTIVA!',
    arc_mega_ready: 'MEGA PALA lista · gatillo la libera',
    arc_mega_cd: 'SIN CARGAS · cada 20 toques de rally te da una (hasta ×3) · SOLO en campeonatos',
    arc_mega_hint: 'SUPERPODER DE PALA: cada 20 toques del rally = +1 carga (hasta ×3) · SOLO en campeonatos · un poder distinto ENTRA en la matriz: joystick ⟷ cambia de poder (flechas en el icono) · gatillo del mando LIBRE suelta el seleccionado',
    arc_mega_full: 'TOPE ×3 · ¡gasta una con el gatillo libre!',
    arc_efecto_go: '¡SÚPER EFECTO! · golpea con GIRO (arrastra la pala al golpear): spin ×3 · 10 s',
    arc_efecto_fin: 'SÚPER EFECTO agotado',
    poder_mega: '¡POTENCIADOR DE PALA GIGANTE!',
    poder_efecto: '¡POTENCIADOR DE SÚPER EFECTO!',
    // FASE 160 · BOLA LOCA (15.º poder; la original del Wizard de magia:
    // bola grande arcoíris con deriva aleatoria — SIEMPRE desbloqueada,
    // primer puesto del Arcano; sustituye a la vieja loca de duelos)
    arc_bolaloca_go: '¡BOLA LOCA! · la bola crece, cambia de color y voltea su trayectoria al azar · 10 s',
    arc_bolaloca_fin: 'BOLA LOCA agotada',
    poder_bolaloca: '¡BOLA LOCA!',
    // FASE 160 · REGLA DEL DUEÑO: un solo superpoder de pala en marcha
    poder_uno_activo: 'Ya hay un superpoder activo · espera a que termine',
    // v3.6.37 · SÚPER IMÁN (tercer poder)
    arc_iman_go: '¡SÚPER IMÁN! · tus ataques dan SIEMPRE en la mesa rival (más fuerte y rápido) · 10 s',
    arc_iman_fin: 'SÚPER IMÁN agotado',
    iman_asistido: 'IMPACTO ASISTIDO por el imán',
    poder_iman: '¡POTENCIADOR DE SÚPER IMÁN!',
    // v3.6.41 · SÚPER PORTAL (cuarto poder)
    arc_portal_go: '¡SÚPER PORTAL! · la bola cruza el vórtice · 8 s / 3 golpes',
    arc_portal_fin: 'SÚPER PORTAL agotado',
    poder_portal: '¡PORTAL DIMENSIONAL!',
    // v3.6.50 (r58) · SÚPER CLONACIÓN (quinto poder) + VOZ del selector
    arc_clon_go: '¡SÚPER CLONACIÓN! · 2 palas fantasma te cubren los lados (90 % de acierto) y limpian globos y confeti · 10 s',
    arc_clon_fin: 'SÚPER CLONACIÓN agotada',
    clon_salva: '¡LA PALA CLON TE HA SALVADO!',
    poder_clon: '¡POTENCIADOR DE CLONACIÓN!',
    // v3.6.120 (r25) · SÚPER RED + SÚPER ELECTRICIDAD (6.º y 7.º poder)
    arc_red_go: '¡SÚPER RED! · la red crece AL DOBLE · 10 s',
    arc_red_fin: 'SÚPER RED agotada · la red vuelve a su altura',
    poder_red: '¡POTENCIADOR DE SÚPER RED!',
    arc_elec_go: '¡SÚPER ELECTRICIDAD! · tormenta sobre tu rival · 10 s',
    arc_elec_fin: 'la tormenta se disipa',
    // r34 (v3.6.130) · el rayo ALCANZA la bola: retención visible de 1 s
    arc_elec_caza: '¡ALCANZADA! · el rayo retiene la bola',
    poder_elec: '¡POTENCIADOR DE SÚPER ELECTRICIDAD!',
    // v3.6.122 (r26b) · SÚPER FÉNIX + SÚPER CRONO + SÚPER HIELO
    // (8.º, 9.º y 10.º poder — nombres pedidos por el dueño:
    // «SuperPoder de XXXX»)
    poder_fenix: '¡SUPERPODER DE FÉNIX!',
    arc_fenix_go: '¡SÚPER FÉNIX! · bola de fuego · 10 s',
    arc_fenix_fin: 'el fénix se apaga',
    poder_crono: '¡SUPERPODER DE CRONO!',
    arc_crono_go: '¡SÚPER CRONO! · tiempo lento · 10 s',
    arc_crono_fin: 'el tiempo vuelve a su cauce',
    poder_oscuridad: '¡SUPERPODER DE OSCURIDAD!',
    arc_oscuridad_go: '¡SÚPER OSCURIDAD! · niebla en el golpeo rival · 20 s',
    // r33 (v3.6.129) · el lote aprobado: Prisma · Onda de Choque · Salvavidas · Ancla
    poder_prisma: '¡SUPERPODER PRISMA!',
    arc_prisma_go: '¡SÚPER PRISMA! · estela arcoíris y guía en tu golpeo · 10 s',
    poder_onda: '¡SUPERPODER ONDA DE CHOQUE!',
    arc_onda_go: '¡ONDA DE CHOQUE! · tus smashes aturden al rival · 10 s',
    poder_salva: '¡SUPERPODER SALVAVIDAS!',
    arc_salva_go: '¡SALVAVIDAS! · una bola escapada, devuelta sola · 10 s',
    arc_salva_save: '¡SALVAVIDAS! · la bola escapada, devuelta al 80 %',
    poder_ancla: '¡SUPERPODER ANCLA!',
    arc_ancla_go: '¡SÚPER ANCLA! · inmune a los poderes del rival · 10 s',
    ancla_bloqueo: '¡Las cadenas del ANCLA bloquean el poder rival!',
    arc_oscuridad_fin: 'la oscuridad se disipa',
    sin_poder: 'Sin poder',
    // =====================================================================
    // r39 (v3.6.135) · FASE 137 · EL APARTADO ARCANO — el búho del hall
    // guarda la galería de superpoderes de pala: espacio infinito azul,
    // materialización uno a uno, candados y desbloqueo por campeonato
    // ganado. Los desbloqueados se juegan en DUELOS LOCOS.
    // =====================================================================
    arcono_titulo: 'EL ARCANO',
    arcono_sub: 'SUPERPODERES DE PALA',
    arcono_pie: 'Los desbloqueados se juegan en DUELOS LOCOS',
    arcono_candado: 'BLOQUEADO · gana un campeonato para revelarlo',
    arcono_desbloq: 'DESBLOQUEADO',
    arcono_tipo_ataque: 'ATAQUE',
    arcono_tipo_defensa: 'DEFENSA',
    arcono_tipo_distraccion: 'DISTRACCIÓN',
    arcono_metricas: 'Métricas',
    arcono_indice: '{i} de {n}',
    arcono_gana: 'Cada campeonato completo ganado libera un superpoder al azar',
    arcono_todos: 'El Arcano te lo ha revelado todo',
    arcono_hint: 'El búho del Arcano custodia los superpoderes de pala · apunta y gatillo',
    arcono_salir: 'El búho te devuelve al salón',
    arcono_boton_salir: 'Salir',   // r43 · el letrero sobre el búho al apuntarlo
    arcono_nuevo: 'EL ARCANO TE REVELA: {p}',
    arcono_ninguno: 'El Arcano ya lo sabía todo · nada nuevo que revelar',
    // — descripciones de la galería (una por poder; el índice es AUTOMÁTICO:
    //   un poder nuevo en PODERES_PALA hereda galería con añadir aquí su
    //   arc_desc_<id> y arc_met_<id>) —
    arc_desc_mega: 'Tu pala crece con canto de oro y onda de choque: más superficie, más radio de golpeo. Activa y vuelve a disparar para alargar la ventana.',
    arc_met_mega: 'Pala ×1,30 · radio ×1,38 · 15 s por carga · tope ×3',
    arc_desc_efecto: 'Golpea con GIRO arrastrando la pala: el spin que generas se triplica, la bola curva en vuelo y el bote muerde el campo rival.',
    arc_met_efecto: 'Spin ×3 · Magnus ×2,2 · bote amplificado · 10 s / 5 golpes',
    arc_desc_iman: 'Un campo magnético suave atrae la bola hacia el punto dulce de tu pala: la asistencia centra el impacto, tú sigues dirigiendo el golpe.',
    arc_met_iman: 'Radio 0,95 m · plena a 0,26 m · acel. 6,5 m/s² · 10 s',
    arc_desc_portal: 'Tras tu golpe válido la bola se hunde en un vórtice, viaja oculta un segundo y sale disparada sobre la mesa rival con bote jugable garantizado.',
    arc_met_portal: 'Desvío 0,25–0,70 m · rapidez 90–100 % · 8 s / 3 golpes',
    arc_desc_clon: 'Dos palas fantasma flotan a tus lados y cazan la bola escapada; de paso limpian globos y confeti que el rival suelte sobre tu campo.',
    arc_met_clon: 'Palas a ±0,50 m · rescate 90 % · 10 s',
    arc_desc_red: 'La red crece al doble de su altura reglamentaria y cierra el paso a los tiros rasos; al acabar vuelve exacta a su altura.',
    arc_met_red: 'Altura ×2 · física viva en ambos campos · 10 s',
    arc_desc_elec: 'Nubes a metro y medio sobre la mesa rival descargan ráfagas con gran estruendo y destello; si un rayo intercepta la bola, la rompe en pedacitos y pierde el punto.',
    arc_met_elec: 'Nubes a 1,5 m · ~35 rayos · noche eléctrica · 10 s',
    arc_desc_fenix: 'Tu bola arde con bocanadas, ascuas y estela naranja: el rival, deslumbrado, decide mal y estrella más devoluciones.',
    arc_met_fenix: 'Faltas del rival +15 % · bola de fuego · 10 s',
    arc_desc_crono: 'El tiempo se dobla: la bola vuela al 62 % de su rapidez rodeada de anillos de reloj; al acabar, la velocidad se restaura exacta.',
    arc_met_crono: 'Rapidez ×0,62 · restauración exacta · 10 s',
    arc_desc_oscuridad: 'Niebla densa en cada zona de golpeo del rival y bola negra con halo de fuego: el rival, ciego, manda fuera buena parte de sus devoluciones.',
    arc_met_oscuridad: 'Niebla 5 s + 2 s de disipación · 6 zonas · faltas +35 % · 20 s',
    arc_desc_prisma: 'Tu bola deja una estela arcoíris viva y al golpear ves una guía sutil de trayectoria; la estela del rival parpadea y le cuesta leer el vuelo.',
    arc_met_prisma: 'Guía 3 s tras tu golpeo · estela arcoíris · faltas rival +10 % · 10 s',
    arc_desc_onda: 'Cada smash tuyo genera un anillo expansivo con temblor de sala: si el rival está en pleno swing, su devolución sale floja.',
    arc_met_onda: 'Smash ≥ 5,2 m/s · devolución rival ×0,75 · margen 1 s · 10 s',
    arc_desc_salva: 'Una vez por activación, si la bola te pasa, tu pala hace un warp de luz hasta su punto de caída y la devuelve sola, aunque llega cansada.',
    arc_met_salva: '1 rescate por activación · devolución ×0,80 · 10 s',
    arc_desc_ancla: 'Cadenas de energía anclan tu pala al suelo: los poderes del rival se estrellan contra ti con destello metálico, sin entrar en juego.',
    arc_met_ancla: 'Inmunidad a poderes rivales · sin bonus activo · 10 s',
    // FASE 160 · la ficha que FALTABA (informe r108 del dueño: «el super
    // poder de bola loca no tiene descripciones y le faltarían por poner
    // en su tarjeta»)
    arc_desc_bolaloca: 'La bola crece y vive su caos: ciclo arcoíris y deriva imprevisible que descoloca a cualquiera y revienta los planes del rival.',
    arc_met_bolaloca: 'Tamaño ×1,65 · ciclo arcoíris · deriva aleatoria · 10 s',
    // r108 · SUPER CRIPTONITA (el dueño: nuevo poder de pala, 12 s)
    arc_desc_cripto: 'La bola se vuelve kryptonita: verde fosforito pulsante con estela de luz verde que se disipa a medio metro; cada bote en la mesa del rival siembra cristales de cuarzo veteados de 20 a 50 cm y si la bola los rompe, sale despedida al 33 % en dirección imposible.',
    arc_met_cripto: 'Bola verde pulsante · estela verde 50 cm · 1-5 cristales (20-50 cm) · romper = ×1/3 + dirección aleatoria · 12 s',
    poder_cripto: 'SUPER CRIPTONITA',
    arc_cripto_go: '¡SUPER CRIPTONITA! La bola es kryptonita y siembra cristales en la mesa rival',
    arc_cripto_fin: 'La criptonita se apaga: bola y mesa vuelven a la normalidad',
    cripto_rompe: '¡Cristal roto! La bola sale despedida al 33 % en dirección imposible',
    // — nombres cortos para el cable 'pow' de DUELOS LOCOS —
    dl_mega: 'MEGA PALA', dl_efecto: 'SÚPER EFECTO', dl_iman: 'SÚPER IMÁN',
    dl_portal: 'SÚPER PORTAL', dl_clon: 'SÚPER CLONACIÓN', dl_red: 'SÚPER RED',
    dl_elec: 'SÚPER ELECTRICIDAD', dl_fenix: 'SÚPER FÉNIX', dl_crono: 'SÚPER CRONO',
    dl_oscuridad: 'SÚPER OSCURIDAD', dl_prisma: 'SÚPER PRISMA', dl_onda: 'ONDA DE CHOQUE',
    dl_salva: 'SALVAVIDAS', dl_ancla: 'SÚPER ANCLA',
    // v3.6.42 · conmutador de PASSTHROUGH dentro de la sesión (por defecto off)
    btn_psthru: 'Passthrough · tu habitación: {v}',
    msg_psthru_on: 'Passthrough ACTIVADO · tu habitación (sin salir de la partida)',
    msg_psthru_off: 'Passthrough desactivado · sala virtual (sin salir de la partida)',
    msg_psthru_next_on: 'Passthrough activado · se aplicará al entrar',
    msg_psthru_next_off: 'Passthrough desactivado · se aplicará al entrar',
    btn_pmej: 'Pala Mejorada: {v}',
    msg_pmej: 'Pala Mejorada: {v} · superpoderes de la pala',
    // r95 · AJUSTES NUEVOS: volúmenes separados, SALA/MESA, rivales con
    // estilo y estadísticas del duelo (ES)
    btn_musvol: 'Volumen música',
    btn_fxvol: 'Volumen efectos',
    msg_musicvol: 'Música: {v}%',
    msg_fxvol: 'Efectos: {v}%',
    sub_sala: 'SALA',
    sub_mesa: 'MESA',
    mesa_altura_lbl: 'Altura de la mesa',
    mesa_aspecto_lbl: 'Aspecto de la mesa',
    mesa_alto_baja: 'Baja',
    mesa_alto_normal: 'Normal',
    mesa_alto_alta: 'Alta',
    mesa_asp_azul: 'Azul oficial',
    mesa_asp_verde: 'Verde clásica',
    mesa_asp_neon: 'Neón locura',
    mesa_asp_oro: 'Oro campeón',
    mesa_asp_carbon: 'Carbono pro',
    // r21 (v3.6.117) · SKINS DE BOLA (ES)
    bola_aspecto_lbl: 'Aspecto de la bola',
    cat_salabola: 'BOLA',
    sub_bola_sub: 'skins de la bola: clásicas, locura y planetas',
    bola_cosmetica: 'Solo visual: la física de la bola NO cambia jamás',
    msg_bola_skin: 'Bola: {v}',
    bola_asp_blanca: 'Blanca oficial',
    bola_asp_naranja: 'Naranja 40 mm',
    bola_asp_menta: 'Menta fresca',
    bola_asp_estrellas: 'Estrellas doradas',
    bola_asp_playa: 'Pelota de playa',
    bola_asp_futbol: 'Balón de fútbol',
    bola_asp_ocho: 'Bola 8',
    bola_asp_ojo: 'Ojo loco',
    bola_asp_neon: 'Neón locura',
    bola_asp_holo: 'Holográfica',
    bola_asp_disco: 'Disco espejo',
    bola_asp_marte: 'Marte',
    bola_asp_luna: 'Luna',
    bola_asp_tierra: 'Tierra',
    bola_asp_lava: 'Lava',
    bola_asp_saturno: 'Saturno',
    mesa_lock_wins: '🔒 Oro campeón: gana 10 partidos',
    mesa_lock_streak: '🔒 Carbono pro: encadena una racha de 5',
    mesa_lock_hint: 'Las mesas con 🔒 se liberan con recompensas',
    mesa_no_champ: 'La mesa no se toca durante un campeonato',
    msg_mesa_alto: 'Altura de la mesa: {v}',
    msg_mesa_skin: 'Aspecto de la mesa: {v}',
    btn_rivstyle: 'Rivales con estilo visible: {v}',
    msg_rivstyle: 'Estilo de los rivales: {v}',
    fanf_stats: '⚡ {v} m/s · Rally {r} · Precisión {p}%',
    // r97 · MAPA DE CALOR + RETOS SEMANALES
    heat_t: 'MAPA DE CALOR',
    heat_sub: 'zonas donde pierdes puntos',
    heat_sin: 'sin datos todavía — juega duelos',
    heat_total: '{n} puntos perdidos',
    heat_corta: 'corta',
    heat_media: 'media',
    heat_fondo: 'fondo',
    retos_t: 'RETOS DE LA SEMANA',
    retos_star: 'estrellas: {n}',
    retos_r1: 'Gana {n} duelos',
    retos_r2: 'Completa un rally de {n}+ golpes',
    retos_r3: 'Golpea la bola a {n} m/s o más',
    retos_r4: 'Completa {n} sesiones de entrenamiento',
    retos_r5: 'Consigue {n} aces',
    retos_r6: 'Juega {n} duelos',
    retos_premio: 'alimenta los desbloqueos de mesa y sala',
    mesa_lock_wins_stars: '10 victorias — o {n}★ de retos',
    mesa_lock_streak_stars: 'racha de 5 — o {n}★ de retos',
    // v3.6.122 (r26b) · candados por HITOS de los 3 hall nuevos
    mesa_lock_rally20: 'Hito: un rally de 20 golpes',
    mesa_lock_elo1100: 'Hito: alcanza ELO 1100',
    mesa_lock_aces5: 'Hito: 5 saques directos',
    // r38 (v3.6.134) · hito del RASCACIELOS
    mesa_lock_won25: 'Hito: 25 victorias',
    // r85 · ECONOMÍA CRAZY — monedas y tienda de bolas/mesas
    mon_bal: 'Monedas: {n}',
    mon_hint: 'gana partidos · +25 victoria · +8 derrota',
    shop_t: 'TIENDA CRAZY',
    shop_ask: '¿Comprar «{v}» por {n} monedas?',
    shop_buy: 'COMPRAR · {n}',
    shop_cancel: 'Cancelar',
    shop_ok: '¡«{v}» es tuyo! −{n} monedas',
    shop_falta: 'te faltan {n} monedas',
    shop_hint: 'Los candados se abren con hitos o comprándolos con monedas',
    sala_lock_stars: 'consigue {n}★ en los retos semanales',
    // r23 (v3.6.118) · HALL DEL ANFITRIÓN (ES) — pared de insignias + visita
    cat_salahall: 'HALL',
    sub_hall_sub: 'el Hall del Anfitrión: insignias y skins a la vista',
    hall_gloria_t: 'PARED DE INSIGNIAS',
    hall_gloria_peer: 'HALL DEL ANFITRIÓN',
    hall_gloria_sub: '{w} victorias · racha {r} · {s}★ · ELO {e}',
    hall_gloria_sub_peer: 'victorias {w} · racha {r} · {s}★ · ELO {e}',
    hall_stats: '{w} victorias · racha {r} · {s}★ de retos · ELO {e}',
    hall_visitando: 'Estás viendo EL HALL DEL ANFITRIÓN: su vitrina, su gloria',
    hall_en_rally: 'En pleno rally no se visita el museo',
    hall_entrar: '⌂ ENTRAR AL HALL',
    hall_cosmetica: 'El hall es de todos: conecta online y presume de lo tuyo',
    gloria_bola: 'BOLA',   // v3.6.143: chips de la pared de insignias con idioma
    gloria_mesa: 'MESA',
    hint_sala_bola: 'Las 16 skins de la bola: clásicas, locura y planetas — solo visual',
    hint_sala_hall: 'Entra al Hall: tus insignias… o las del anfitrión si juegas online',
    hint_hall_entrar: 'Visita el museo de las insignias (en online, el del anfitrión)',
    // r24 (v3.6.119) · VARIANTE DEL HALL + SPIN REALISTA (ES)
    hall_var_lbl: 'Arte del hall',
    hall_var_anfitrion: 'MUSEO',
    hall_var_cabana: 'LA CABAÑA',
    msg_hall_var: 'Arte del hall: {v}',
    hint_hall_var_a: 'El museo clásico: pared de insignias y bolas doradas',
    hint_hall_var_c: 'La Cabaña: chimenea, barra y nieve — se libera con 10 victorias',
    // v3.6.122 (r26b) · los 3 HALL nuevos (desbloqueo por hitos)
    hall_var_neon: 'SALÓN NEÓN ARCADE',
    hall_var_observatorio: 'OBSERVATORIO ESTELAR',
    hall_var_dojo: 'DOJO ZEN',
    // r38 (v3.6.134) · 4.º salón del dueño (mismo comportamiento)
    hall_var_rascacielos: 'RASCACIELOS',
    hint_hall_var_rascacielos: 'Vistas de ciudad al anochecer: 25 victorias levantan tu torre',
    hint_hall_var_neon: 'Synthwave: recreativas, rejillas de neón — un rally de 20 golpes lo abre',
    hint_hall_var_observatorio: 'La Tierra al ventanal del observatorio: ELO 1100 lo abre',
    hint_hall_var_dojo: 'Shoji, tatami y ensō: 5 saques directos y entra a meditar',
    // r32 (v3.6.128) · MÚSICA AMBIENTAL DEL SALÓN (icono de la pared)
    msg_hallmus: 'Música del salón: {v}',
    // r96 · SALA Y ESCENA: submenús-botón, deslizador de altura, vista en
    // vivo de la sala de partidos y HINTS al apuntar en el menú
    cat_salaroom: 'SALA',
    cat_salamesa: 'MESA',
    sub_sala_sub: 'Temas de la estancia y passthrough · se ven EN VIVO',
    sub_mesa_sub: 'Altura y aspecto de la mesa · se ve EN VIVO',
    sala_preview: 'Sala de partidos · los cambios se aplican en vivo',
    mesa_alto_lbl: 'Altura de la mesa',
    mesa_alto_cm: '{v} cm',
    mesa_alto_grab: 'Agarra la mesa: apunta, mantén el gatillo y muévela arriba/abajo',
    mesa_zona_baja: 'Baja',
    mesa_zona_media: 'Media',
    mesa_zona_alta: 'Alta',
    msg_mesa_altoy: 'Altura de la mesa: {v} cm',
    perf_ffr: 'NITIDEZ DEL VISOR (FOVEADO)',
    perf_ffr_max: 'Máxima',
    perf_ffr_alta: 'Alta',
    perf_ffr_normal: 'Normal',
    perf_ffr_rinde: 'Rinde',
    perf_ffr_v: 'Nitidez aplicada ahora: fovea {v}',
    msg_perf_ffr: 'Nitidez del visor: {v} · el gobernador nunca pasará de ahí',
    // r96 · HINTS DEL MENÚ (tooltips al apuntar): una línea por control
    hint_close: 'Cierra el menú y vuelve al juego (también el botón B)',
    hint_back: 'Volver a la página anterior',
    hint_modo_match: 'Partido libre contra la CPU al mejor de 3 juegos',
    hint_modo_train: 'Entrenamiento con áreas de tiro, dirección, altura y más',
    hint_modo_surv: 'Supervivencia: la CPU acelera rallye a rallye, ¿cuánto aguantas?',
    hint_modo_multi: 'Multijugador online: salas, duelos y el medallón del Pulso',
    hint_modo_champs: 'Campeonatos: Halloween, Estación Orbital, Oeste, Magia y Locura',
    hint_modo_rank: 'Ranking mundial por campeonato (top 10)',
    hint_modo_tut: 'La Academia: tutorial de primeros pasos',
    hint_modo_opts: 'Todas las opciones del juego en subapartados',
    hint_cat_juego: 'Dificultad de la CPU, rival adaptativo, pala mejorada y estilo',
    hint_cat_sala: 'Sala y mesa: se abre la sala de partidos para ver los cambios',
    hint_cat_sonido: 'Música, efectos, voz del megáfono y volúmenes separados',
    hint_cat_visual: 'Estela de la bola, haptics al golpear y consejos',
    hint_cat_perfil: 'Tu nombre, telemetría y reinicio de registros',
    hint_cat_rendi: 'FPS, calibración por casco y nitidez del visor',
    hint_cat_pala: 'Colocación de la pala en el mando, agarres guardados',
    hint_diff: 'Nivel de la CPU en el partido libre (fácil · media · difícil)',
    hint_adapt: 'La CPU sube o baja su nivel según el marcador',
    hint_pmej: 'Superpoderes de la pala en los duelos con poderes',
    hint_rivstyle: 'La personalidad del rival se ve: se acerca si es agresivo y celebra sus puntos',
    hint_theme: 'Cambia el ambiente de la sala al instante (suelo, paredes y luces)',
    hint_psthru: 'Usa tu habitación real como fondo (passthrough del Quest)',
    hint_mesa_altoy: 'Apunta a la mesa, mantén el gatillo y súbela o bájala moviendo el mando: verás su altura en grande',
    hint_mesa_altomen: 'Baja la mesa 1 cm',
    hint_mesa_altomas: 'Sube la mesa 1 cm',
    hint_mesa_skin: 'Color de la mesa; las con 🔒 se liberan ganando partidos',
    hint_music: 'Música del menú y de los campeonatos sí/no',
    hint_amb: 'Ambiente de la sala (público y sala) sí/no',
    hint_voz: 'Voz del megáfono (marcador y anuncios) sí/no',
    hint_sndtest: 'Prueba de sonido; dos pulsaciones reparan el audio',
    hint_mvol: 'Volumen de la MÚSICA: apunta a la barra o usa − y +',
    hint_fvol: 'Volumen de los EFECTOS (bola, mesa, red): barra o − y +',
    hint_mvolset: 'Mantén el gatillo sobre la barra y desliza el mando a izquierda o derecha',
    hint_fvolset: 'Mantén el gatillo sobre la barra y desliza el mando a izquierda o derecha',
    hint_trail: 'Estela luminosa tras la bola sí/no',
    hint_tips: 'Consejos de primera sesión sí/no',
    hint_hapt: 'Vibración del mando al golpear sí/no',
    hint_pname: 'Escribe tu nombre para el ranking y el multijugador',
    hint_tele: 'Telemetría anónima de fallos y rendimiento',
    hint_reset: 'Borra ranking, récords, logros y poderes (dos pulsaciones)',
    hint_perfAuto: 'El juego se calibra solo para mantener 60 FPS seguros',
    hint_perfTier: 'Perfil de calidad manual según tu casco',
    hint_perfRecal: 'Mide de nuevo los FPS de tu casco y ajusta la calidad',
    hint_perfFfr: 'Nitidez del visor: menos foveado = imagen más limpia en los bordes',
    hint_kofi: 'Apoya el desarrollo con un café',
    hint_sala_sala: 'El ambiente de la estancia: Pabellón, Neón, Atardecer y Ártico + passthrough',
    hint_sala_mesa: 'La mesa: sube y baja con el deslizador y cambia su color — todo en vivo',
    arc_power_clown: '¡El Clown enloquece! ¡Confeti a la vista!',
    arc_power_warn: '¡SUPERPODER ENTRANTE! ¡PREPÁRATE…',
    // v2.106 · cartel explicativo de la prueba ARKANOID (La Locura)
    instr_ark_t: 'PRUEBA · ARKANOID LOCO',
    instr_ark: [
      'En lugar de mesa hay un MURO DE LADRILLOS: golpea la bola con las PALAS para arrancar ladrillos.',
      'Tienes 2 MINUTOS y 5 VIDAS (saques). Cada ladrillo roto suma; el rebote es real, ¡calcula los ángulos!',
      'Al avanzar tendrás una PISTOLA DE RAYOS en la mano libre: apunta y dispara a los ladrillos que la bola no alcanza.',
      'Alarma a los últimos 10 segundos: ¡da lo mejor de ti!',
    ],
    arc_power_confetti: '¡SUPER PODER! ¡CONFETI CAÓTICO 8 s!',
    arc_power_ball: '¡SUPER PODER! ¡BOLA LOCA: roja, gigante y lenta!',
    arc_power_globos: '¡SUPER PODER! ¡LLUVIA DE GLOBOS en tu campo: revienta la pala!',
    arc_power_burla: '¡SUPER PODER! ¡BURLA: cartones burlescos que frenan la bola! El COMODÍN negro: golpéalo y ganas el punto',
    burla_comodin: '¡COMODÍN! La bola se ha puesto NEGRA y gigante: ¡golpéala y el punto es TUYO!',
    arc_music: 'Música del campeonato (BSO de fondo)',
    arc_music_global: 'Música de los campeonatos (todos por igual)',
    arc_music_msg: 'Música de los campeonatos: {v}',
    arc_music_off_word: 'silenciada',
    arc_music_muted: 'SILENCIADA',
    arc_music_hint: '−/+ volumen',
    arc_map_title: 'RUTA DEL CAMPEONATO',
    arc_map_sub: 'Vence a cada rival y supera las pruebas de habilidad',
    arc_map_start: 'INICIO',
    arc_map_locked: 'próximamente',
    arc_map_trophy: 'TROFEO',
    arc_map_legend: 'Pruebas de habilidad con la pala entre rivales · anillo dorado: tu progreso',
    // ---- v2.38 · PRUEBA ARKANOID (2ª parada del camino)
    btn_ark_go: 'PRUEBA: ARKANOID · el muro de ladrillos',
    ark_locked: 'Vence al CLOWN Nv. 1 para desbloquear la prueba ARKANOID',
    ark_map_clown: 'CLOWN Nv.1',
    ark_map_ark: 'ARKANOID',
    ark_title: '¡ARKANOID!',
    ark_intro: 'Rompe TODOS los ladrillos en 2 minutos',
    ark_serve_hint: 'GATILLO: lanza la bola · golpéala con la pala',
    ark_autoserve: 'Saque automático…',
    ark_life: '¡Bola perdida! Te quedan {n} vidas',
    ark_timeup: '¡TIEMPO!',
    ark_nolives: '¡SIN VIDAS!',
    ark_retry: 'La prueba se repite: ¡otra oportunidad, vuelve a intentarlo!',   // v3.6.12 (ronda 15)
    ark_win: '¡MURO DESTRUIDO!',
    // v2.96 · rejugadas de etapas superadas
    replay_up: 'REJUGANDO LA ETAPA {n} · ¡suerte, forastero!',
    replay_done: '¡REJUGADA! El camino sigue igual: apunta a otra etapa o sigue la ruta',
    ark_gun_get: '¡SUPERPODER: PISTOLA en tu mano libre!',
    // ---- v2.44 · CAMINO COMPLETO (5 pasos) + ARKANOID 2 + TROFEO ----
    btn_ark2_go: 'PRUEBA: ARKANOID 2 · ladrillos rojos y azules',
    ark2_locked: 'Vence al CLOWN Nv. 2 para desbloquear el ARKANOID 2',
    ark_map_clown2: 'CLOWN Nv.2',
    ark_map_clown3: 'CLOWN Nv.3',
    ark_map_ark2: 'ARKANOID 2',
    ark2_title: '¡ARKANOID 2!',
    ark2_intro: 'Láser a los AZULES · pala a los ROJOS · 2,5 min',
    ark2_hint: 'AZUL: sólo el LÁSER lo convierte en rojo · ROJO: sólo la PALA lo rompe',
    ark2_win: '¡MURO DESTRUIDO!',
    ark2_back: 'Vuelves al paso anterior: nueva partida vs CLOWN Nv. 2',
    ark2_next: '¡Siguiente: CLOWN Nv. 3, el rivalsazo final!',
    ark_gun_on: 'PISTOLA LÁSER equipada · gatillo de la mano libre',
    clown2_up: '¡NIVEL 2! El Clown viene más listo',
    clown3_up: '¡NIVEL 3! Cuidado: ¡bola doble a la vista!',
    arc_power_split: '¡SUPER PODER! ¡LA BOLA SE DIVIDE EN DOS!',
    split_saved: '¡Perdiste una bola… pero la OTRA sigue viva!',
    split_end: '¡Bola doble terminada!',
    trophy_get: '¡¡TROFEO: CAMPEONATO DE LA LOCURA!!',
    champdone_big: '¡CONSEGUIDO!',
    champdone_sub: 'CAMPEONATO SUPERADO',
    champdone_msg: '¡Insignia conseguida!',
    champdone_replay: 'Puedes rejugar cualquier etapa cuando quieras',
    champ_done_chip: '★ SUPERADO',
    champ_done_hint: '★ SUPERADO · rejuega cualquier etapa desde el mapa',
    // r72 · candados de campeonatos + telón de carga
    champ_locked_soon: 'Próximamente',
    champ_locked_chip: 'PRÓXIMAMENTE',
    champ_locked_hint: 'Aún en preparación · pronto anunciamos cómo desbloquearlo',
    champ_telon: 'Montando el escenario...',
    // r73 · índice resiliente + telón de teatro
    champ_cargando: 'Cargando campeonatos…',
    champ_reintentar: '⟳  REINTENTAR',
    champ_telon_presenta: 'CRAZY PING PONG PRESENTA',
    champ_stage_hint: 'Etapa {n}/{total} · sigue donde la dejaste',   // v3.6.17 (ronda 21, la de la ronda 19 al fin en producción)
    champ_leyenda_chip: '★ LEYENDA',   // v3.6.18 (ronda 24)
    champ_leyenda_hint: '★ LEYENDA · camino sellado 5/5 en modo leyenda',
    trophy_sub: 'Eres el CAMPEÓN · trofeo registrado en tu palmarés',
    trophy_rank: 'TROFEO: ¡CAMPEÓN!',
    // v2.48 · palmarés ampliado (récords reales en el panel RANKING)
    arc_rec_rally: 'Rallye récord: {n} golpes',
    arc_rec_streak: 'Mejor racha: {n} rondas',
    arc_rec_surv: 'Mejor supervivencia: {n} golpes',
    arc_rec_ach: 'Logros: {n}/{m}',
    fan_hint: '¡Abanica la pala (izq-der rápida) para crear viento y empujar la bola!',
    // v2.46 · ladrillo negro del TIEMPO EXTRA (ARKANOID 2)
    ark_extra_min: '¡+1 MINUTO EXTRA!',
    // v3.6.44 · ladrillo BOMBA del ARKANOID 2 (etapa 4 de La Locura)
    ark_bomba_boom: '¡BOOM! ¡DETONACIÓN!',
    // v3.6.45 · ladrillo ELÉCTRICO del ARKANOID 2 (los últimos 30 s)
    ark_elec_on: '¡LADRILLO ELÉCTRICO! Dale con la BOLA',
    ark_elec_aran: '¡PARED ELECTRIFICADA! Un golpe y… ¡CADENA!',
    hud_time: 'TIEMPO',
    hud_bricks: 'LADRILLOS',
    hud_lives: 'VIDAS',
    gun_hint: 'PISTOLA lista · gatillo de la mano libre para disparar rayos',
    sb_clown: 'CLOWN',
    arc_rank_win: 'VICTORIA',
    arc_rank_lose: 'DERROTA',
    arc_rank_tot: 'Ganadas: {n} · Racha: {s}',
    online_lbl: 'ONLINE · contra otra persona',
  multi_hint: 'Crear sala e introducir código viven en MULTIJUGADOR',
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
    msg_adapt: 'Rival adaptativo: {v} — se ajusta con el marcador',
    msg_mic: 'Megáfono del marcador: {v}',
    hint_hit: '¡Golpea la bola hacia la mesa con la pala!',
    hint_toss_high: 'Lanza la bola un poco más arriba',
    hint_behind: 'Saca desde detrás de la línea de fondo',
    srv_reancla: 'Bola recolocada · saca tras la línea de fondo',
    hint_dropped: 'Bola caída · repite el lanzamiento',
    online_first: '¡Conectado! Esperando al anfitrión…',
    online_serve: 'Partido online · tu saque (GATILLO para lanzar)',
    net_ended: '{msg} · partido local reiniciado',
    // ---- estados de red (NetLink)
    peer_gone: 'El rival se ha ido',
    conn_lost: 'Conexión perdida',
    peer_closed: 'El rival cerró la sala',
    bye_self: 'Has cerrado la conexión',   // r37 (v3.6.133): hangup i18n
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
    sb_bo: 'MEJOR DE {n}',
    calib_msg: 'ENTRENAMIENTO · Y: volver al entrenamiento',
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
    // v3.6.51 (r59) · LA ACADEMIA — tutorial interactivo (texto ES)
    tut_hub: 'TUTORIAL',
    tut_hub_sub: 'Aprende a jugar en 3 minutos · paso a paso y con práctica real',
    tutask_title: '¿PRIMERA VEZ?',
    tutask_sub: 'Te enseñamos a jugar: el mando, el saque y todos los modos',
    tutask_yes: 'EMPEZAR TUTORIAL',
    tutask_no: 'AHORA NO',
    tut_title: 'LA ACADEMIA CRAZY',
    tut_step: 'PASO {n} DE {m}',
    tut_hint_next: 'GATILLO · continuar',
    tut_hint_skip: 'B · saltar · STICK · repetir la voz',
    tut_s0_t: 'BIENVENIDO A LA ACADEMIA',
    tut_s0_l1: 'En 3 minutos sabrás sacar, golpear y elegir tu modo favorito.',
    tut_s0_l2: 'Cada paso tiene una práctica real: hazla para continuar.',
    tut_s0_go: 'GATILLO · empezar',
    tut_s1_t: 'TUS MANDOS',
    tut_s1_l1: 'IZQUIERDO: botones Y y X · DERECHO: B y A.',
    tut_s1_l2: 'GATILLO: lanzar y golpear · GRIP (lateral): soltar la bola.',
    tut_s1_l3: 'B: menú · Y: volver · STICK: oír el poder elegido en partido.',
    tut_s1_task: 'PRÁCTICA: pulsa el GATILLO',
    tut_s2_t: 'LA PALA',
    tut_s2_l1: 'La pala ya está en tu mano: es tu raqueta. Sin botones raros.',
    tut_s2_l2: 'Golpea el aire con un movimiento firme para continuar.',
    tut_s2_task: 'PRÁCTICA: mueve la pala con fuerza',
    tut_s3_t: 'EL SAQUE',
    tut_s3_l1: 'La bola descansa en tu MANO LIBRE (la que no lleva la pala).',
    tut_s3_l2: 'Pulsa el GATILLO para lanzarla y golpéala con la pala',
    tut_s3_l3: 'para que cruce la red (debe botar en los dos campos).',
    tut_s3_task: 'PRÁCTICA: realiza 3 saques válidos',
    tut_s3_again: 'Otra vez: la bola vuelve a tu mano libre',
    tut_s3_cnt: 'SAQUES VÁLIDOS',
    tut_s3_ok: '¡Saque válido! Sigue así',
    tut_s4_t: 'EL INTERCAMBIO',
    tut_s4_l1: 'Tu profesor te devuelve la bola. Golpéala de nuevo',
    tut_s4_l2: 'por encima de la red. Seis devoluciones y pasas.',
    tut_s4_task: 'PRÁCTICA: devuelve 6 bolas',
    tut_s4_n: 'Devoluciones: {n}/6',
    tut_s5_t: 'LOS BOTONES EN JUEGO',
    tut_s5_l1: 'A o X: cambia la pala de mano (¡pruébalo ahora!).',
    tut_s5_l2: 'B: menú · STICK (en partido): oír el poder seleccionado.',
    tut_s5_l3: 'Cada 20 golpes del rally te dan una carga de poder.',
    tut_s5_task: 'PRÁCTICA: pulsa A o X',
    tut_s6_t: 'LOS MODOS · 1 DE 2',
    tut_mods_t: 'LOS MODOS',
    tut_mod_p: 'Contra la CPU al mejor de 3',
    tut_mod_s: 'Aguanta el máximo de rallyes',
    tut_mod_m: 'Online con un código de 5 letras',
    tut_mod_c: '6 rivales con su historia',
    tut_mod_r: 'Compite con el mundo',
    tut_mod_t: '5 áreas para tu técnica',
    tut_m_t: 'TU MANDO, TU RAQUETA',
    tut_lab_pala: 'TU RAQUETA',
    tut_pow_t: 'PODERES · SOLO CAMPEONATOS: 20 toques seguidos cargan · gatillo lanza · 10 s',
    tut_s6_m1: 'PARTIDO · contra la CPU (3 niveles). Al mejor de 3 sets.',
    tut_s6_m2: 'SUPERVIVENCIA · aguanta el máximo de rallyes seguidos.',
    tut_s6_m3: 'MULTIJUGADOR · online con un código de 5 letras.',
    tut_s7_t: 'LOS MODOS · 2 DE 2',
    tut_s7_m1: 'CAMPEONATOS · 6 rivales con su historia. ¡Corona la OESTE!',
    tut_s7_m2: 'RANKING MUNDIAL · compite con jugadores de todo el mundo.',
    tut_s7_m3: 'ENTRENAR · PRO TRAINING: 5 áreas para pulir tu técnica.',
    tut_s7_p: 'PODERES: Mega Pala · Efecto · Imán · Portal · Clonación — con la bola viva, el GATILLO de la mano libre suelta el que tengas cargado.',
    tut_s8_t: '¡YA SABES JUGAR!',
    tut_s8_l1: 'Eso es todo: saca, intercambia, gana cargas y suelta poderes.',
    tut_s8_l2: 'GATILLO = jugar YA contra la CPU · B = volver al menú.',
    tut_s8_go: 'GATILLO · JUGAR YA',
    tut_done_msg: '¡Ya sabes jugar! Bienvenido a Crazy Ping Pong',
    tut_bad_online: 'El tutorial no está disponible en multijugador',
    tut_bad_busy: 'Termina primero la prueba activa para entrar a la Academia',
    tut_lab_trigger: 'GATILLO',
    tut_lab_stick: 'STICK',
    tut_lab_grip: 'GRIP',
    tut_lab_btns: 'A/X · B/Y',
    tut_lab_btns_i: 'Y · X (izquierdo)',
    tut_lab_btns_d: 'B · A (derecho)',
    // r65 · academia gamificada (voz nativa + mando GLB + reglas visuales)
    tut_rep: 'STICK · repetir la voz',
    tut_m1_gat: 'ACCIÓN · aprieta el GATILLO',
    tut_m1_grip: 'ACCIÓN · aprieta el botón lateral (GRIP)',
    tut_m1_stick: 'ACCIÓN · inclina el STICK',
    tut_m1_a: 'ACCIÓN · pulsa A (o X)',
    tut_m1_ok: '¡Mandos dominados!',
    tut_m1_raf: 'TU MANDO ES TU RAQUETA · gatillo para seguir',
    tut_m1_lado: 'MUÉVELA HACIA LOS LADOS · vaivén firme con la pala',
    // r66 · pasos rediseñados: saque e intercambio REALES sobre la mesa
    tut_d3_t: 'EL SAQUE · MIRA LA MESA',
    tut_d3_l1: 'La bola descansa en la mano libre; el GATILLO la suelta.',
    tut_d3_l2: 'Debe botar en TU campo y después en el del rival.',
    tut_d3_l3: 'Si el rival no la devuelve: PUNTO para ti.',
    tut_d3_go: 'GATILLO · TU TURNO: 3 SAQUES VÁLIDOS',
    tut_d3_p1: '1º TU CAMPO',
    tut_p1r: '1º SU CAMPO (rival)',
    tut_d3_p2: '2º EL RIVAL',
    tut_d3_pto: '¡PUNTO!',
    tut_d4_t: 'EL INTERCAMBIO',
    tut_d4_l1: 'Saca de nuevo: el rival devuelve y el intercambio empieza.',
    tut_d4_l2: 'Cuando alguien lo pierde, es PUNTO del otro…',
    tut_d4_l3: 'y CADA 2 SAQUES rota el sacador: 2 tú, 2 el rival.',
    tut_d4_task: 'Saca y gana el intercambio (el rival fallará al final)',
    tut_d4_ok: '¡PUNTO! Así discurre el partido',
    tut_d5_t: 'EL MARCADOR',
    tut_d5_l1: 'Se juega a 11 puntos, ganando por 2.',
    tut_d5_l2: 'El saque rota cada 2 puntos…',
    tut_d5_l3: 'y a 10-10, CADA punto. Gana el que llegue a +2.',
    tut_ent: 'ENTENDIDO · gatillo para seguir',
    tut_h_tu: 'TÚ',
    tut_h_ia: 'RIVAL',
    tut_h_saq: 'SAQUE',
    tut_h_10: '¡10-10!',
    tut_h_p2: '¡+2 PARA GANAR!',
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
    ov_kofi: '☕ Apoyar en Ko-fi',
    ov_tv: 'Mira las partidas en vivo sin visor',
    // r109 · M3 PWA (portada): botón instalar + toasts
    ov_pwa: '📲 INSTALAR EN EL CASCO',
    pwa_manual: '<b>Instálala en 2 toques:</b> abre el menú <b>⋮</b> del navegador y elige <b>«Instalar app»</b>. Icono propio en el casco, sin teclear URL y actualizaciones automáticas.',
    pwa_installed: '<b>¡App instalada!</b> CRAZY PING PONG ya vive en tu casco: búscala entre tus apps.',
    pwa_ready: 'Listo para instalar: pulsa de nuevo y elige «Instalar» en el diálogo.',
    music_title: 'Música (portada y menú VR)',
    ov_hint: '<b>En el visor:</b> sube esta carpeta a <b>Netlify Drop</b> y abre el enlace con el <b>Meta Quest Browser</b> (requiere HTTPS).',
    ov_lang: '🌐 Idioma / Language',
  },

  /* ----------------------------- ENGLISH ---------------------------- */
  en: {
    opp_cpu: 'the CPU',
    opp_rival: 'your opponent',
    opp_machine: 'the machine',
    opp_wizard: 'WIZARD', // v2.54: New Magic Trick rival (Nubes removed in v2.56)
    opp_clown: 'the CLOWN',
    opp_forajido: 'the OUTLAW',
    who_you: 'you',
    serve_wait: 'Your serve · the ball waits in your free hand',
    // r128 · E2 (auditoría r120): full-storage warning
    storage_lleno: 'NOTICE: storage is full or blocked and progress may not be saved. Free up space in the headset browser.',
    // M4 (r111) · ONBOARDING < 60 s: tres claves nuevas (EN)
    hub_play: '▶ PLAY',
    // r67 · FASE 161 · THE LOBBY (panel titles + dock)
    vest_jugar: 'PLAY',
    vest_compite: 'COMPETE',
    vest_casa: 'YOUR HOME',
    dock_tv: 'Live TV',
    dock_intro: 'Intro',
    dock_instalar: 'Install',
    dock_apoyar: 'Support',
    dock_salir: 'Exit to web',
    // r58 · FASE 152 · CONFIG_MENU: EXIT TO WEB card in the HUB (EN)
    hub_salirweb: 'EXIT TO WEB',
    hub_salirweb_sub: 'Close the game and return to the main website',
    salirask_title: 'EXIT TO WEB?',
    salirask_sub: 'The game will close and you will return to the main website.',
    salirask_yes_btn: 'YES, EXIT',
    salirask_no_btn: 'NO, KEEP PLAYING',
    salirask_hint: 'B: cancel',
    hint_salirweb: 'Close the game · back to the main website',
    first_hint: 'Welcome · press ▶ PLAY and you will be playing in seconds',
    srv_guide: 'SERVE GUIDE · TRIGGER to toss → hit it as it falls and send it through the golden ring',
    // M5a (r112) · IA STYLES: selector and announcement
    estilo_lbl: 'Rival style',
    msg_estilo: 'Rival: {v} · same physics, new character',
    // M5b (r115) · CAREER LADDER: divisions, rivals and progress
    carrera_lbl: 'Career ladder',
    carrera_sub: 'Bronze → Legend · three rivals per division',
    carrera_hint: 'Beat all 3 to climb up · losses never demote: rematch whenever you like',
    carrera_hub_sub: '{v} · {n}/3 rivals',
    carrera_d_bronce: 'BRONZE',
    carrera_d_plata: 'SILVER',
    carrera_d_oro: 'GOLD',
    carrera_d_diamante: 'DIAMOND',
    carrera_d_leyenda: 'LEGEND',
    carrera_actual: 'CURRENT DIVISION',
    carrera_superada: 'CLEARED',
    carrera_bloqueada: 'LOCKED',
    carrera_challenge: 'CHALLENGE {v}',
    carrera_rematch: 'REMATCH {v}',
    carrera_vencido: 'BEATEN',
    carrera_pendiente: 'NEXT',
    carrera_win_msg: 'Ladder win against {v}!',
    carrera_lose_msg: 'Loss against {v} · the rematch awaits',
    carrera_promo_msg: 'PROMOTED TO THE {v} DIVISION!',
    carrera_crown_msg: 'LEGEND CROWN! The ladder is yours',
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
    // v3.6.29 · BEST OF 3 (round 37): game and matchup messages
    game_won_you: 'GAME FOR YOU · {p}-{q} · series {a}-{b} · keep it up!',
    game_won_opp: 'GAME FOR {opp} · {p}-{q} · series {a}-{b} · next one!',
    over_win_bo: 'MATCHUP FOR YOU! · Games {a}-{b} · last {p}-{q}',
    over_lose_bo: 'MATCHUP FOR {opp} · Games {a}-{b} · last {p}-{q}',
    cause_dblhit: 'double hit',
    cause_volley: 'hit before the bounce',
    cause_burla: 'mock wildcard',
    cause_elec: 'struck down by SUPER ELECTRICITY',
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
    // v3.6.29 · BEST OF 3: game and matchup announcer lines
    ann_game_you: 'Game for you. {a} to {b} in games',
    ann_game_opp: 'Game for {opp}. {a} to {b} in games',
    ann_victory_bo: 'Matchup for you! {a} games to {b}',
    ann_match_end_bo: 'Matchup for {opp}. {a} games to {b}',
    ann_rally_record: 'Rally of {n} hits. New record!',
    ann_ach: 'Achievement unlocked: {name}!',
    ann_room: '{room} arena',
    mode_survival: 'Survival mode. Keep the rally going!',
    mode_match: 'Match mode. Good luck!',
    welcome: 'Welcome to the match. Good luck!',
    welcome_menu: 'Welcome to Crazy Ping Pong, choose a game mode',
    hall_sign: 'HALL OF FAME',
    hall_sign_sub: 'CRAZY PING PONG · HOST LOUNGE',
    hall_welcome: 'Welcome to your hall · pick a mode on the panel',
    hall_home_btn: '⌂ BACK TO HALL',
    hall_home_hint: 'The hall is home: settings and mode changes live there',
    // r74 · FASE 168 · PICK A HALL
    hall_pick_btn: '⌂ PICK A HALL',
    hall_pick_t: 'PICK A HALL',
    hall_pick_hint: 'your room: the classic museum and the halls you unlock',
    hall_actual: 'CURRENT',
    hall_disponible: 'available',
    hall_visita: 'Online visits show the hall of the HOST',
    hallask_title: 'MAIN MENU',
    hallask_sub: 'Exit to the Host Hall?',
    hallask_yes_btn: 'YES, GO TO THE HALL',
    hallask_no_btn: 'No, stay here',
    hallask_hint: 'YES takes you to the Hall with the menu open · NO closes this panel and you keep playing',
    hall_champs: 'CHAMPIONSHIPS WON',
    hall_achs: 'CRAZY ACHIEVEMENTS',
    hall_circ: 'PRO CIRCUIT',
    hall_palas: 'PADDLE SKIN',
    hall_rank_title: 'CAREER & RANKING',
    hall_rank_v: 'WINS',
    hall_rank_s: 'BEST STREAK',
    hall_rank_r: 'BEST RALLY',
    hall_rank_a: 'ACES',
    hall_quote: '“A champion is forged in rallies nobody sees”',
    hall_locked: 'LOCKED',
    hall_trophy_wait: 'THE TROPHY AWAITS ITS FIRST CHAMPION',
    hall_trophy_won: 'HALL OF CHAMPIONS',
    menu_pin_off: 'Pushpin: menu follows your head',
    menu_pin_on: 'Pushpin set: menu pinned here',
    hall_door: '› TO THE COURT',
    opp_connected: 'Opponent connected. Let’s play!',
    opp_disconnected: 'Opponent disconnected',
    diff_easy: 'Easy difficulty',
    diff_medium: 'Medium difficulty',
    diff_hard: 'Hard difficulty',
    theme_pabellon: 'Gym',
    theme_neon: 'Neon',
    theme_atardecer: 'Sunset',
    theme_artico: 'Arctic',
    theme_nocturna: 'Night 🌙',
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
    // M4 (r118) · unified ELO + matchmaking + MY RANKING
    mm_label: 'ELO MATCHMAKING',
    mm_btn: 'Level-matched rival · ELO ~{n}',
    mm_armado: 'Level-matched rival armed: ELO ~{n} ({d})',
    mm_rival: 'ELO ~{n} rival',
    rankme_btn: 'MY RANKING (ELO)',
    rankme_t: 'MY RANKING',
    // r70 · FASE 164 · sections in Ajustes format (grid landing)
    rank_tab_t: 'WORLD TABLE',
    trainext_t: 'PROFILE & EXTRAS',
    rankme_sub: 'Your skill number — local and honest',
    rankme_hist: 'HISTORY · last changes',
    rankme_racha_a: 'Current streak',
    rankme_racha_m: 'Best streak',
    rankme_mejordia: 'Best day',
    rankme_marca: 'Wins {w} · losses {l}',
    rankme_dia: '{v} wins',
    rankme_vacio: 'No matches yet — play one and your ELO comes alive',
    rankme_leyenda: 'K by mode: AI 24 · ladder 20 · human 32 · daily/training not counted',
    rankme_ia: 'AI', rankme_carrera: 'ladder', rankme_p2p: 'human',
    // M7c (r119) · DOBLES 2v2 (prototype)
    dobles_btn: 'DOUBLES 2v2 — give it a try',
    dobles_msg: 'DOUBLES! Your partner covers the ball you can\'t reach',
    room_label: 'ROOM',
    extras_label: 'EXTRAS',
    lang_label: 'LANGUAGE',
    btn_amb: 'Crowd: {v}',
    btn_trail: 'Trail: {v}',
    // r61 · adaptive rival toggle + best-rally replay
    btn_adapt: 'Adaptive rival: {v}',
    // r115: rep_t/rep_slow/rep_chip removed with the best-rally replay
    // (owner request)
    btn_mic: 'Announcer: {v}',
    btn_music: 'Music: {v}',
    msg_music: 'Music {v}',
    // v2.50 · PHASE 1 · comfort + telemetry + Ko-fi support
    btn_hapt: 'Haptics on hits: {v}',
    msg_hapt: 'Haptics {v}',
    btn_tips: 'Beginner tips: {v}',
    msg_tips: 'Tips {v}',
    btn_tele: 'Anonymous telemetry: {v}',
    msg_tele: 'Telemetry {v}',
    tele_hint: 'Anonymous: no personal data. Helps improve the game.',
    btn_kofi: '☕ Support the project (Ko-fi)',
    msg_kofi: 'Thank you! ☕ Ko-fi opens in the browser',
    tip_1: 'TIP · Serve with the trigger: toss the ball up and hit it',
    tip_2: 'TIP · Twist your wrist to add SPIN (topspin/slice)',
    tip_3: 'TIP · B button = menu · A/X = switch paddle hand',
    tip_bye: 'Go play! Beat the CLOWN and conquer the Championship of Madness',
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
    voz_error: 'No microphone found on this device',
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
    btn_connect: 'CONNECT',
    btn_retry: 'RETRY',
    btn_back: 'BACK',
    mj_off_hint: 'Create a room or join with a code.',
    btn_host: 'CREATE ROOM (code for your rival)',
    btn_join: 'ENTER A FRIEND’S CODE',
    mj_p2p: 'Direct P2P (WebRTC). Needs internet on both headsets.',
    mj_mic_hint: 'Voice uses the microphone: accept the browser permission.',
    // r79 · multiplayer submenu: NORMAL + CRAZY DUELS (owner request)
    mj_norm_t: 'NORMAL · MATCH',
    mj_norm_s: '1 v 1 online · best of 3 games · your own hit has zero lag',
    mj_duel_t: 'CRAZY DUELS',
    mj_duel_s: '1 v 1 online with crazy powers · trigger to fire them',
    // r74 · FASE 169 · MULTIJUGADOR IN THREE ZONES
    mj_crear_t: 'CREATE MATCH',
    mj_disp_t: 'OPEN MATCHES',
    mj_priv_t: 'PRIVATE ROOM',
    mj_priv_hint: 'join with the code the host gave you',
    mj_sin_pub: 'no public matches right now · create yours',
    mj_sin_soc: 'social layer is offline: no live listing',
    mj_entrar: 'JOIN',
    mj_hace: '{n}s ago',
    mj_mas_pub: '+{n} more in the pulse list',
    mj_vis_pregunta: 'How do you open the room?',
    mj_vis_pub: 'PUBLIC · for everyone',
    mj_vis_pub_sub: 'announced to connected players and listed under Open matches',
    mj_vis_pri: 'PRIVATE · code only',
    mj_vis_pri_sub: 'nobody sees it: only players with your code can join',
    rs_jugador: 'Player',
    // r74 · FASE 170 · THE DUEL ALERT
    duelo_alerta_voz: 'A player has accepted your duel invitation',
    duelo_alerta_msg: 'DUEL WAITING: a player accepted your invitation — icon above or Multiplayer',
    dueloask_t: 'ACCEPT THE DUEL',
    dueloask_sub: 'A player has accepted your duel invitation.',
    dueloask_hint: 'if you accept, what you are doing closes and you jump into the match — any progress will be lost',
    dueloask_si: 'YES, ACCEPT AND PLAY',
    dueloask_no: 'NO, STAY HERE (hang up)',
    // r84 · CRAZY DUELS unlocked: online match powers
    mode_duelos: 'CRAZY DUELS! · best of 3 with powers',
    dl_listo: 'Power ready! · trigger to fire it',
    dl_poder_listo: 'POWER READY · trigger',
    dl_gigante: 'GIANT PADDLE',
    dl_fuego: 'FIRE BALL',
    dl_loca: 'CRAZY BALL',
    dl_bolaloca: 'CRAZY BALL',
    dl_rival: 'from your rival',
    // r84 · HALL plaque for EL PULSO CRAZY (museum physical gate)
    pulso_hall_t: 'EL PULSO CRAZY',
    pulso_hall_m: 'Today’s challenge: {m}',
    pulso_racha_t: 'YOUR STREAK',
    pulso_racha_s: '{n} day(s) · best {r}',
    pulso_racha_0: 'No streak yet · play today’s challenge!',
    mj_ping: '{n} ms',
    net_syncing: 'Syncing with your rival…',
    // r80 · breathing submenu + DAILY CHALLENGE AT THE GATE (owner)
    mj_pick: 'Pick a game mode to continue',
    mj_sel_back: '◀  MODES',
    daily_btn_t: 'Daily Challenge!',
    daily_btn_new: 'Today’s duel: {m} · streak: {n}',
    daily_btn_done: 'Done today · streak: {n} · back tomorrow',
    daily_btn_zona: 'zones twice as wide · a new duel every midnight',
    net_paused: 'RIVAL PAUSED · match clock stopped',
    net_paused_long: 'RIVAL PAUSED (a while) · waiting…',
    net_legacy: 'No fast channel: 30 Hz compatibility mode',
    // r82 · DOWN TO THE MILLIMETRE: the link announces and diagnoses itself
    net_link_direct: 'Direct link established',
    net_link_tunnel: 'Tunnelled link established',
    // r126 · P4.1 · build warning inside the room (first real match lesson)
    net_build_warn: 'Your rival runs ANOTHER build ({a} vs {b}): reload the game on BOTH headsets and re-create the room',
    net_build_voice: 'rival on another build reload the game on both headsets',
    // r127 · P4.2 · boot-time version self-check: if BOTH headsets stayed
    // old, the HELLO cannot see it — the running build is compared against
    // the web itself (PAGES-VERSION.txt, network-first).
    net_selfcheck_warn: 'You are on an OLD build ({b}) · the web has {a}: close and reopen the web to update',
    net_selfcheck_voice: 'old version close and reopen the web to update',
    net_v2_down: 'No binary link with your rival · check Internet and reload',
    join_title: 'YOUR FRIEND’S ROOM CODE',
    // ---- v2.28 · MAIN MENU (big floating panel with accordion)
    sec_match: 'PLAY MATCH',
    sec_train: 'TRAINING',
    sec_surv: 'SURVIVAL',
    sec_crazy: 'CHAMPIONSHIPS',
    sec_opts: 'OPTIONS',
    btn_start: '▶  START MATCH',
    btn_start_surv: '▶  START SURVIVAL',
    btn_train_go: '▶  PRACTICE SHOTS',
    crazy_msg: 'Surprises coming soon..! 🎁',
    // ---- v2.66 · NAME FOR THE RANKING + RECORDS RESET
    opts_name: 'YOUR NAME: {v}',
    name_title: 'YOUR NAME FOR THE RANKING',
    name_hint: 'Point with the beam and pull the trigger to write',
    name_save: 'SAVE NAME',
    reset_btn: 'RESET RECORDS',
    reset_arm: 'DELETE ALL? TAP AGAIN',
    reset_done: 'Records wiped! Fresh start.',
    no_name: '—',
    // ---- r156 · MY PROFILE (player card + avatar/frame shop)
    perfil_title: 'MY PROFILE',
    perfil_sub: 'Your player card: level, ELO rank, badges and shop',
    hub_jugar: 'PLAY',
    jugar_sub: 'Match · Career · Training · Survival · Tutorial',
    perfil_editar: 'EDIT PROFILE',
    perfil_edit_t: 'EDIT PROFILE',
    perfil_nivel: 'Level',
    perfil_rango: 'Current rank',
    perfil_partidos: 'Matches',
    perfil_victorias: 'Wins',
    perfil_racha: 'Streak',
    perfil_monedas: 'Coins',
    perfil_insignias: 'Badges',
    perfil_pais: 'Country',
    perfil_avatar: 'Avatar',
    perfil_marco: 'Frame',
    perfil_guardar: 'SAVE',
    perfil_guardado: 'Profile saved!',
    perfil_sin_pais: 'International',
    perfil_rank_btn: 'WORLD RANKING',
    perfil_tienda: 'Avatar & frame shop',
    perfil_compra: 'Buy {v} for {n} coins? TAP AGAIN',
    perfil_compra_ok: 'Purchased and equipped!',
    perfil_falta: 'You need {n} more coins',
    perfil_lock_logro: 'Unlocked with the "{v}" badge',
    perfil_lock_elo: 'Requires ELO {v}',
    perfil_equipado: 'Equipped',
    perfil_xp_txt: '{a} / {b} XP',
    perfil_nombre: 'Name',
    perfil_movida: 'Name, country and avatar are edited in MY PROFILE › EDIT.',
    // ---- v2.67 · WORLD RANKING (top 10 per championship)
    sec_rank: 'WORLD RANKING',
    wrl_open: '🌍  OPEN WORLD RANKING',
    wrl_points: 'POINTS',
    wrl_wins: 'WINS',
    wrl_col_name: 'NAME',
    wrl_col_logros: 'AWARDS',
    wrl_online: 'World · online',
    wrl_offline: 'Offline · last known data',
    wrl_loading: 'Loading world ranking…',
    wrl_you: 'YOU',
    wrl_need_name: 'Set your name in Options → YOUR NAME to sign your records',
    wrl_refresh: '↻ REFRESH',
    wrl_refresh_short: '↻',
    wrl_2d_hint: 'The ranking is published when you win: sign your records with YOUR NAME in Options (inside the game).',
    best_surv: 'Best: {n} hits',
    // ---- v2.110 · HUB MENU (mode cards + pages) ----
    hub_match: 'MATCH',
    hub_vs: 'vs CPU · {v}',
    hub_train_sub: 'PRO TRAINING · 5 areas + skins',
    hub_surv_sub: 'Survive the barrage',
    hub_multi: 'MULTIPLAYER',
    hub_multi_sub: 'Online P2P match',
    // r87 · RED SOCIAL DEL PULSO (medallón + invitaciones)
    rs_aviso: '🎮 INVITATION RECEIVED! — Menu ▸ Multiplayer',
    rs_online: '{n} player(s) online',
    rs_invita_de: 'Invitation from {n}',
    rs_invita_code: 'Room code: {c} — join now',
    rs_unirse: 'JOIN',
    rs_invitar: 'INVITE',
    rs_descartar: 'Dismiss',
    hub_multi_on: 'Connected · room {c}',
    hub_champ_sub: 'Madness · Magic · West',
    hub_rank_sub: 'World top 10',
    hub_diff: 'CPU DIFFICULTY',
    dock_label: 'QUICK SETTINGS',
    dock_mic: 'Announcer',
    dock_hapt: 'Haptics',
    page_back: '‹  MENU',
    page_champs: 'CHAMPIONSHIPS',
    page_opts: 'SETTINGS ›',
    opts_title: 'SETTINGS',
    opts_elegir: 'Tap a category to enter',
    cat_juego: 'GAME',
    cat_juego_sub: 'CPU difficulty, adaptive rival & enhanced paddle',
    cat_sala: 'ROOM & SCENE',
    cat_sala_sub: 'The room, the view and passthrough',
    cat_sonido: 'AUDIO',
    cat_sonido_sub: 'Music, ambience, voice and test',
    cat_visual: 'VISUALS',
    cat_visual_sub: 'Trail, haptics and tips',
    cat_perfil: 'PROFILE & DATA',
    cat_perfil_sub: 'Your name, telemetry and reset',
    // r81 · PERFORMANCE: FPS auto-calibrator (steady 60+ on any headset)
    cat_rendi: 'PERFORMANCE',
    cat_rendi_sub: 'FPS, auto quality and per-headset calibration',
    perf_device: 'Device: {v}',
    perf_fps: 'FPS now: {v} · headset at {r} Hz',
    perf_fps_short: '{v} FPS',
    perf_auto: 'Auto calibration: {v}',
    perf_calidad: 'HEADSET PROFILE',
    perf_tier_auto: 'AUTO',
    perf_t_quest3: 'Quest 3 · max quality',
    perf_t_quest2: 'Quest 2 · smooth',
    perf_escala: 'Resolution next session: ×{v}',
    perf_recal: 'RECALIBRATE NOW',
    perf_recal_next: 'RECALIBRATE ON VR ENTRY',
    perf_calibrando: 'Calibrating… round {s}',
    perf_cal_ok: 'Done: {f} steady FPS on your headset',
    perf_estado_ok: 'SMOOTH',
    perf_estado_bajo: 'LOW FPS · adjusting',
    perf_stepdown: 'Optimizing visuals to keep it smooth',
    msg_perf_auto: 'Auto calibration {v}: quality adapts to your headset',
    msg_perf_recal_next: 'Great: calibration will start when you enter VR',
    // r77 · FASE 173 · NET: quality of service in one line
    net_red: 'NET {p} ms · {e}',
    net_q_excelente: 'EXCELLENT',
    net_q_bien: 'GOOD',
    net_q_ajustada: 'STRAINED',
    net_q_tun60: 'TUNNEL · 60',
    net_q_tun30: 'TUNNEL · 30',
    // r78 · FASE 174 · ALERTS + PUBLIC ROOM WAITING
    btn_alertas: 'Challenge alerts: {v}',
    msg_alertas_on: 'Alerts on: we announce public challenges',
    msg_alertas_off: 'Alerts off: public challenges stay silent (accept them in MULTIPLAYER)',
    btn_espera: 'Keep waiting · MY HOME',
    hub_multi_espera: 'ROOM {c} WAITING · public',
    // r79 · FASE 175 · the menu never unpins + owner fixes
    btn_gestiona: 'MANAGE ROOM',
    pala_salir_ask: 'Leave the paddle fitting?',
    pala_salir_hint: 'The fitting stays live until you confirm YES (B opens this menu inside the mode)',
    hist_empty_hint: 'Win championships and they will be sealed here with date and wins',
    // r80 · FASE 176 · training area names (the shell title showed the raw key)
    a_dir: 'Direction', a_alt: 'Height', a_spin: 'Spin',
    a_saq: 'Serve', a_rit: 'Rhythm',
    // r83 · AJUSTES › PADDLE: the paddle fitting leaves PRO TRAINING and
    // gets its own subsection with instant passthrough, full X/Y/Z axes and
    // named grips stored on the device.
    cat_pala: 'PADDLE',
    cat_pala_sub: 'Grip, position and millimetre placement',
    pala_actual: 'Current grip: {v}',
    pala_go: 'FIT THE PADDLE IN VR',
    pala_go_sub: 'Instant passthrough · you will see your real controller to place it perfectly',
    pala_help: 'Sticks: rotate (right) · move (left) · stick press or GRIP = Z axis',
    pala_guardados: 'SAVED GRIPS',
    pala_ninguno: 'No saved grips yet (save them with A inside the fitting)',
    pala_nat: 'BACK TO NATURAL GRIP',
    pala_gname: 'SAVE CURRENT FIT WITH A NAME',
    pala_gname_title: 'GRIP NAME',
    pala_pst: 'PASSTHROUGH ON · real controllers in sight',
    pala_replica: '3D CONTROLLER REPLICA · placement reference',
    msg_pala_on: 'Place the paddle over your real controller: passthrough on',
    msg_pala_del: 'Grip deleted',
    msg_pala_online: 'Paddle fitting is not available during an online match',
    hub_champ_hint: 'Tap to enter',
    champ_intro_btn: 'WATCH THE INTRO · rival video',   // v3.6.31: re-watch the intro (optional)
    // ---- v2.34 · ARCADE "Championship of Madness" (CLOWN rival) ----
    arcade_go: '▶  CHAMPIONSHIP OF MADNESS',
    arcade_hint: '11-point match vs the CLOWN · every win adds to your ranking and unlocks the MEGA PADDLE power.',
    arcade_record: 'Rounds won: {n} · Current streak: {s}',
    arcade_none: 'No rounds won yet · beat the Clown!',
    arc_rank_empty1: 'No rounds won yet',
    arc_rank_empty2: 'beat the Clown!',
    best_arcade: 'Rounds won: {n}',
    // M7e (r124) · historial de torneos + perfil recordado
    hist_title: 'TOURNAMENT HISTORY',
    hist_btn: '📜 View tournament history',
    hist_empty: 'No tournaments sealed yet. Win a championship and it will live here forever.',
    hist_wins: '{n} wins',
    hist_sellado: 'sealed on {f}',
    perfil_titulo: 'YOUR PROFILE · REMEMBERED',
    perfil_skin: 'Table skin: {v}',
    perfil_alto: 'Table height: {v}',
    perfil_pala: 'Enhanced paddle: {v}',
    perfil_estilo: 'Styled rivals: {v}',
    perfil_pid: 'Anonymous player: {v}…',
    msg_arcade: 'CHAMPIONSHIP OF MADNESS! Beat the Clown',
    msg_arcade_menu: 'The Clown awaits you in the Championship of Madness',
    arc_title: 'CHAMPIONSHIP OF MADNESS',
    arc_announce: 'Welcome to the Championship of Madness. Beat the Clown.',
    arc_no_data: 'Championship not available in this build',
    cartel_new: 'NEW MATCH!',
    cartel_vs: 'VS CLOWN · Round {n}',
    // v3.6.34 · MEGA PADDLE CORE NORM: charged by an 11+ hit rally
    // (all championships), announced by the handle icon + its own jingle;
    // voluntary use (trigger while the ball is in play).
    arc_combo: 'CRAZY COMBO! MEGA PADDLE CHARGED!',
    arc_combo_locked: 'CRAZY COMBO! Win a round to unlock the MEGA PADDLE',
    arc_mega_go: 'MEGA PADDLE ACTIVE!',
    arc_mega_ready: 'MEGA PADDLE ready · trigger to release it',
    arc_mega_cd: 'NO CHARGES · every 20 rally shots grants one (up to ×3) · championships only',
    arc_mega_hint: 'PADDLE SUPERPOWER: every 20 rally shots = +1 charge (up to ×3) · championships only · a different power JOINS the row: cycle with the stick ⟷ (arrows on the icon) · FREE-hand trigger releases the selected one',
    arc_mega_full: 'MAX ×3 · spend one with the free-hand trigger!',
    arc_efecto_go: 'SUPER SPIN! · brush the ball WITH SPIN (drag the paddle on impact): ×3 spin · 10 s',
    arc_efecto_fin: 'SUPER SPIN worn off',
    poder_mega: 'GIANT PADDLE BOOSTER!',
    poder_efecto: 'SUPER SPIN BOOSTER!',
    // FASE 160 · CRAZY BALL (15th power; the magic Wizard's original:
    // big rainbow ball with random drift — ALWAYS unlocked, first seat
    // of the Arcana; replaces the old duels loca)
    arc_bolaloca_go: 'CRAZY BALL! · the ball grows, shifts color and jinks at random · 10 s',
    arc_bolaloca_fin: 'CRAZY BALL worn off',
    poder_bolaloca: 'CRAZY BALL!',
    // FASE 160 · OWNER RULE: only one paddle superpower at a time
    poder_uno_activo: 'A superpower is already active · wait for it to end',
    // v3.6.37 · SUPER MAGNET (third power)
    arc_iman_go: 'SUPER MAGNET! · your shots ALWAYS land on the rival table (stronger and faster) · 10 s',
    arc_iman_fin: 'SUPER MAGNET worn off',
    iman_asistido: 'MAGNET-ASSISTED impact',
    poder_iman: 'SUPER MAGNET BOOSTER!',
    // v3.6.41 · SUPER PORTAL (fourth power)
    arc_portal_go: 'SUPER PORTAL! · the ball crosses the vortex · 8 s / 3 hits',
    arc_portal_fin: 'SUPER PORTAL worn off',
    poder_portal: 'DIMENSIONAL PORTAL!',
    // v3.6.50 (r58) · SUPER CLONE (fifth power) + SELECTOR VOICE
    arc_clon_go: 'SUPER CLONE! · 2 ghost paddles cover your sides (90% success) and clear balloons and confetti · 10 s',
    arc_clon_fin: 'SUPER CLONE worn off',
    clon_salva: 'THE CLONE PADDLE SAVED YOU!',
    poder_clon: 'CLONE BOOSTER!',
    // v3.6.120 (r25) · SUPER NET + SUPER ELECTRICITY (6th & 7th powers)
    arc_red_go: 'SUPER NET! · the net grows TWICE as tall · 10 s',
    arc_red_fin: 'SUPER NET worn off · the net is back to its height',
    poder_red: 'SUPER NET BOOSTER!',
    arc_elec_go: 'SUPER ELECTRICITY! · storm over your rival · 10 s',
    arc_elec_fin: 'the storm clears',
    // r34 (v3.6.130) · the bolt CATCHES the ball: 1 s visible hold
    arc_elec_caza: 'CAUGHT! · the bolt holds the ball',
    poder_elec: 'SUPER ELECTRICITY BOOSTER!',
    // v3.6.122 (r26b) · SUPER FÉNIX + SUPER CRONO + SUPER HIELO (8th,
    // 9th and 10th powers — owner naming: “SuperPoder de XXXX”)
    poder_fenix: 'PHOENIX SUPERPOWER!',
    arc_fenix_go: 'SUPER PHOENIX! · fireball · 10 s',
    arc_fenix_fin: 'the phoenix fades out',
    poder_crono: 'CHRONO SUPERPOWER!',
    arc_crono_go: 'SUPER CHRONO! · slow motion · 10 s',
    arc_crono_fin: 'time flows back to normal',
    poder_oscuridad: 'DARKNESS SUPERPOWER!',
    arc_oscuridad_go: 'SUPER DARKNESS! · fog on rival hits · 20 s',
    // r33 (v3.6.129) · the approved batch: Prism · Shockwave · Life Saver · Anchor
    poder_prisma: 'PRISM SUPERPOWER!',
    arc_prisma_go: 'SUPER PRISM! · rainbow trail and hit guide · 10 s',
    poder_onda: 'SHOCKWAVE SUPERPOWER!',
    arc_onda_go: 'SHOCKWAVE! · your smashes stun the rival · 10 s',
    poder_salva: 'LIFE SAVER SUPERPOWER!',
    arc_salva_go: 'LIFE SAVER! · one lost ball, returned alone · 10 s',
    arc_salva_save: 'LIFE SAVER! · lost ball returned at 80%',
    poder_ancla: 'ANCHOR SUPERPOWER!',
    arc_ancla_go: 'SUPER ANCHOR! · immune to rival powers · 10 s',
    ancla_bloqueo: 'The ANCHOR chains block the rival power!',
    arc_oscuridad_fin: 'the darkness fades away',
    sin_poder: 'No power',
    // r39 (v3.6.135) · FASE 137 · THE ARCANE WING — hall owl, infinite
    // space, one-by-one gallery, locks and championship unlocks. The
    // unlocked ones are playable in CRAZY DUELS.
    arcono_titulo: 'THE ARCANE',
    arcono_sub: 'PADDLE SUPERPOWERS',
    arcono_pie: 'Unlocked ones are playable in CRAZY DUELS',
    arcono_candado: 'LOCKED · win a championship to reveal it',
    arcono_desbloq: 'UNLOCKED',
    arcono_tipo_ataque: 'ATTACK',
    arcono_tipo_defensa: 'DEFENSE',
    arcono_tipo_distraccion: 'DISTRACTION',
    arcono_metricas: 'Metrics',
    arcono_indice: '{i} of {n}',
    arcono_gana: 'Every full championship win releases one random superpower',
    arcono_todos: 'The Arcane has revealed everything to you',
    arcono_hint: 'The Arcane owl guards the paddle superpowers · aim and trigger',
    arcono_salir: 'The owl takes you back to the lounge',
    arcono_boton_salir: 'Exit',   // r43 · the sign above the owl while aiming at it
    arcono_nuevo: 'THE ARCANE REVEALS: {p}',
    arcono_ninguno: 'The Arcane already knew it all · nothing new to reveal',
    arc_desc_mega: 'Your paddle grows with a golden rim and a shock wave: more surface, wider hit radius. Activate and fire again to extend the window.',
    arc_met_mega: 'Paddle ×1.30 · radius ×1.38 · 15 s per charge · max ×3',
    arc_desc_efecto: 'Hit WITH SPIN by dragging the paddle: the spin you generate triples, the ball curves in flight and the bounce bites into the rival court.',
    arc_met_efecto: 'Spin ×3 · Magnus ×2.2 · amplified bounce · 10 s / 5 hits',
    arc_desc_iman: 'A soft magnetic field pulls the ball toward your paddle sweet spot: the assist centers the impact, you still own the shot.',
    arc_met_iman: 'Radius 0.95 m · full under 0.26 m · accel 6.5 m/s² · 10 s',
    arc_desc_portal: 'After your valid hit the ball sinks into a vortex, travels hidden for a second and shoots out over the rival table with a guaranteed playable bounce.',
    arc_met_portal: 'Drift 0.25–0.70 m · speed 90–100% · 8 s / 3 hits',
    arc_desc_clon: 'Two ghost paddles float at your sides and catch the runaway ball; they also clear balloons and confetti the rival drops on your court.',
    arc_met_clon: 'Paddles at ±0.50 m · 90% rescue · 10 s',
    arc_desc_red: 'The net grows to twice its regulation height and blocks low shots; when it ends it returns to its exact height.',
    arc_met_red: 'Height ×2 · live physics on both courts · 10 s',
    arc_desc_elec: 'Clouds a meter and a half over the rival table fire bolt barrages with thunder and flash; if a bolt catches the ball it shatters it and the point is lost.',
    arc_met_elec: 'Clouds at 1.5 m · ~35 bolts · electric night · 10 s',
    arc_desc_fenix: 'Your ball burns with flames, embers and an orange trail: the rival, dazzled, misjudges and sends more returns out.',
    arc_met_fenix: 'Rival faults +15% · fireball · 10 s',
    arc_desc_crono: 'Time bends: the ball flies at 62% of its speed wrapped in clock rings; when it ends the speed is restored exactly.',
    arc_met_crono: 'Speed ×0.62 · exact restore · 10 s',
    arc_desc_oscuridad: 'Dense fog on every rival hit zone and a black ball with a fire halo: the rival, blind, sends a good share of returns out.',
    arc_met_oscuridad: 'Fog 5 s + 2 s fade · 6 zones · faults +35% · 20 s',
    arc_desc_prisma: 'Your ball leaves a living rainbow trail and on your hits you see a subtle trajectory guide; the rival trail blinks and costs them reads.',
    arc_met_prisma: 'Guide 3 s after your hit · rainbow trail · rival faults +10% · 10 s',
    arc_desc_onda: 'Every smash of yours spawns an expanding ring with a room shake: if the rival is mid-swing, their return comes out weak.',
    arc_met_onda: 'Smash ≥ 5.2 m/s · rival return ×0.75 · 1 s window · 10 s',
    arc_desc_salva: 'Once per activation, if the ball gets past you, your paddle warps with a light trail to its landing spot and returns it alone, though tired.',
    arc_met_salva: '1 rescue per activation · return ×0.80 · 10 s',
    arc_desc_ancla: 'Energy chains anchor your paddle to the floor: rival powers crash against you with a metallic flash, never entering play.',
    arc_met_ancla: 'Immune to rival powers · no active bonus · 10 s',
    // FASE 160 · the missing card (r108 owner report: Bola Loca had no
    // description on its gallery card)
    arc_desc_bolaloca: 'The ball grows and lives its chaos: rainbow cycle and unpredictable drift that throws anyone off and wrecks the rival\'s plans.',
    arc_met_bolaloca: 'Size ×1.65 · rainbow cycle · random drift · 10 s',
    // r108 · SUPER CRYPTONITE (owner: new paddle power, 12 s)
    arc_desc_cripto: 'The ball becomes kryptonite: pulsing phosphor green with a light-green trail that fades within half a meter; every bounce on the rival table grows veined quartz crystals 20-50 cm tall, and if the ball smashes one it crawls away at 33% on an impossible heading.',
    arc_met_cripto: 'Pulsing green ball · 50 cm green trail · 1-5 crystals (20-50 cm) · breaking = ×1/3 + random heading · 12 s',
    poder_cripto: 'SUPER CRYPTONITE',
    arc_cripto_go: 'SUPER CRYPTONITE! The ball is kryptonite and seeds crystals on the rival table',
    arc_cripto_fin: 'The kryptonite fades: ball and table are back to normal',
    cripto_rompe: 'Crystal shattered! The ball crawls away at 33% on an impossible heading',
    dl_mega: 'MEGA PADDLE', dl_efecto: 'SUPER SPIN', dl_iman: 'SUPER MAGNET',
    dl_portal: 'SUPER PORTAL', dl_clon: 'SUPER CLONE', dl_red: 'SUPER NET',
    dl_elec: 'SUPER ELECTRICITY', dl_fenix: 'SUPER PHOENIX', dl_crono: 'SUPER CHRONO',
    dl_oscuridad: 'SUPER DARKNESS', dl_prisma: 'SUPER PRISM', dl_onda: 'SHOCKWAVE',
    dl_salva: 'LIFE SAVER', dl_ancla: 'SUPER ANCHOR',
    // v3.6.42 · in-session passthrough switch (default off)
    btn_psthru: 'Passthrough · your room: {v}',
    msg_psthru_on: 'Passthrough ON · your room (no leaving the match)',
    msg_psthru_off: 'Passthrough off · virtual room (no leaving the match)',
    msg_psthru_next_on: 'Passthrough enabled · applies on entry',
    msg_psthru_next_off: 'Passthrough disabled · applies on entry',
    btn_pmej: 'Enhanced Paddle: {v}',
    msg_pmej: 'Enhanced Paddle: {v} · paddle superpowers',
    // r95 · NEW SETTINGS: split volumes, ROOM/TABLE, visible rival style and
    // duel stats (EN)
    btn_musvol: 'Music volume',
    btn_fxvol: 'Effects volume',
    msg_musicvol: 'Music: {v}%',
    msg_fxvol: 'Effects: {v}%',
    sub_sala: 'ROOM',
    sub_mesa: 'TABLE',
    mesa_altura_lbl: 'Table height',
    mesa_aspecto_lbl: 'Table look',
    mesa_alto_baja: 'Low',
    mesa_alto_normal: 'Standard',
    mesa_alto_alta: 'Tall',
    mesa_asp_azul: 'Official blue',
    mesa_asp_verde: 'Classic green',
    mesa_asp_neon: 'Crazy neon',
    mesa_asp_oro: 'Champion gold',
    mesa_asp_carbon: 'Pro carbon',
    // r21 (v3.6.117) · BALL SKINS (EN)
    bola_aspecto_lbl: 'Ball look',
    cat_salabola: 'BALL',
    sub_bola_sub: 'ball skins: classic, crazy and planets',
    bola_cosmetica: 'Visual only: ball physics NEVER changes',
    msg_bola_skin: 'Ball: {v}',
    bola_asp_blanca: 'Official white',
    bola_asp_naranja: 'Orange 40 mm',
    bola_asp_menta: 'Fresh mint',
    bola_asp_estrellas: 'Golden stars',
    bola_asp_playa: 'Beach ball',
    bola_asp_futbol: 'Football',
    bola_asp_ocho: 'Eight ball',
    bola_asp_ojo: 'Crazy eye',
    bola_asp_neon: 'Crazy neon',
    bola_asp_holo: 'Holographic',
    bola_asp_disco: 'Mirror disc',
    bola_asp_marte: 'Mars',
    bola_asp_luna: 'Moon',
    bola_asp_tierra: 'Earth',
    bola_asp_lava: 'Lava',
    bola_asp_saturno: 'Saturn',
    mesa_lock_wins: '🔒 Champion gold: win 10 matches',
    mesa_lock_streak: '🔒 Pro carbon: chain a 5-win streak',
    mesa_lock_hint: '🔒 tables unlock with rewards',
    mesa_no_champ: 'The table is locked during a championship',
    msg_mesa_alto: 'Table height: {v}',
    msg_mesa_skin: 'Table look: {v}',
    btn_rivstyle: 'Visible rival style: {v}',
    msg_rivstyle: 'Rival style: {v}',
    fanf_stats: '⚡ {v} m/s · Rally {r} · Accuracy {p}%',
    // r97 · HEAT MAP + WEEKLY CHALLENGES (EN)
    heat_t: 'HEAT MAP',
    heat_sub: 'zones where you lose points',
    heat_sin: 'no data yet — play matches',
    heat_total: '{n} points lost',
    heat_corta: 'short',
    heat_media: 'mid',
    heat_fondo: 'deep',
    retos_t: 'WEEKLY CHALLENGES',
    retos_star: 'stars: {n}',
    retos_r1: 'Win {n} duels',
    retos_r2: 'Finish a {n}+ shot rally',
    retos_r3: 'Hit the ball at {n} m/s or more',
    retos_r4: 'Complete {n} training sessions',
    retos_r5: 'Score {n} aces',
    retos_r6: 'Play {n} duels',
    retos_premio: 'feeds the table and room unlocks',
    mesa_lock_wins_stars: '10 wins — or {n}★ from challenges',
    mesa_lock_streak_stars: '5 streak — or {n}★ from challenges',
    // v3.6.122 (r26b) · milestone locks of the 3 new halls
    mesa_lock_rally20: 'Milestone: a 20-hit rally',
    mesa_lock_elo1100: 'Milestone: reach ELO 1100',
    mesa_lock_aces5: 'Milestone: 5 aces',
    // r38 (v3.6.134) · SKYSCRAPER milestone
    mesa_lock_won25: 'Milestone: 25 wins',
    // r85 · CRAZY ECONOMY — coins and ball/table shop
    mon_bal: 'Coins: {n}',
    mon_hint: 'win matches · +25 win · +8 loss',
    shop_t: 'CRAZY SHOP',
    shop_ask: 'Buy "{v}" for {n} coins?',
    shop_buy: 'BUY · {n}',
    shop_cancel: 'Cancel',
    shop_ok: '"{v}" is yours! −{n} coins',
    shop_falta: 'you need {n} more coins',
    shop_hint: 'Locks open with milestones or by buying them with coins',
    sala_lock_stars: 'earn {n}★ in the weekly challenges',
    // r23 (v3.6.118) · HALL DEL ANFITRIÓN (EN) — badge wall + visit
    cat_salahall: 'HALL',
    sub_hall_sub: 'the Host’s Hall: badges and skins on display',
    hall_gloria_t: 'BADGE WALL',
    hall_gloria_peer: 'HOST’S HALL',
    hall_gloria_sub: '{w} wins · streak {r} · {s}★ · ELO {e}',
    hall_gloria_sub_peer: 'wins {w} · streak {r} · {s}★ · ELO {e}',
    hall_stats: '{w} wins · streak {r} · {s}★ challenges · ELO {e}',
    hall_visitando: 'You are looking at THE HOST’S HALL: his showcase, his glory',
    hall_en_rally: 'No museum visits mid-rally',
    hall_entrar: '⌂ ENTER THE HALL',
    hall_cosmetica: 'The hall belongs to everyone: go online and show yours off',
    gloria_bola: 'BALL',   // v3.6.143: chips of the badge wall follow the language
    gloria_mesa: 'TABLE',
    hint_sala_bola: 'All 16 ball skins: classic, crazy and planets — visual only',
    hint_sala_hall: 'Enter the Hall: your badges… or the host’s when playing online',
    hint_hall_entrar: 'Visit the badge museum (online: the host’s hall)',
    // r24 (v3.6.119) · HALL VARIANT + REALISTIC SPIN (EN)
    hall_var_lbl: 'Hall art',
    hall_var_anfitrion: 'MUSEUM',
    hall_var_cabana: 'THE CABIN',
    msg_hall_var: 'Hall art: {v}',
    hint_hall_var_a: 'The classic museum: badge wall and golden balls',
    hint_hall_var_c: 'The Cabin: fireplace, bar and snow — unlocks with 10 wins',
    // v3.6.122 (r26b) · the 3 new halls (milestone unlocks)
    hall_var_neon: 'NEON ARCADE LOUNGE',
    hall_var_observatorio: 'STAR OBSERVATORY',
    hall_var_dojo: 'ZEN DOJO',
    // r38 (v3.6.134) · 4th owner hall (same behavior)
    hall_var_rascacielos: 'SKYSCRAPER',
    hint_hall_var_rascacielos: 'City views at dusk: 25 wins raise your tower',
    hint_hall_var_neon: 'Synthwave: arcade cabinets and neon grids — a 20-hit rally opens it',
    hint_hall_var_observatorio: 'Earth at the observatory window: ELO 1100 opens it',
    hint_hall_var_dojo: 'Shoji, tatami and ensō: 5 aces and come in to meditate',
    // r32 (v3.6.128) · HALL AMBIENT MUSIC (wall icon)
    msg_hallmus: 'Lounge music: {v}',
    // r96 · SALA Y ESCENA: button submenus, height slider, live game-room
    // view and HINTS when aiming at menu controls (EN)
    cat_salaroom: 'ROOM',
    cat_salamesa: 'TABLE',
    sub_sala_sub: 'Room themes and passthrough · LIVE preview',
    sub_mesa_sub: 'Table height and look · LIVE preview',
    sala_preview: 'Game room · changes apply live',
    mesa_alto_lbl: 'Table height',
    mesa_alto_cm: '{v} cm',
    mesa_alto_grab: 'Grab the table: aim, hold the trigger and move it up or down',
    mesa_zona_baja: 'Low',
    mesa_zona_media: 'Mid',
    mesa_zona_alta: 'High',
    msg_mesa_altoy: 'Table height: {v} cm',
    perf_ffr: 'HEADSET SHARPNESS (FOVEATED)',
    perf_ffr_max: 'Sharpest',
    perf_ffr_alta: 'High',
    perf_ffr_normal: 'Normal',
    perf_ffr_rinde: 'Fast',
    perf_ffr_v: 'Sharpness applied now: fovea {v}',
    msg_perf_ffr: 'Headset sharpness: {v} · the governor will never go past it',
    // r96 · MENU HINTS (aim tooltips): one line per control
    hint_close: 'Close the menu and go back to the game (B works too)',
    hint_back: 'Back to the previous page',
    hint_modo_match: 'Free match vs the CPU, best of 3 games',
    hint_modo_train: 'Training with aim areas, direction, height and more',
    hint_modo_surv: 'Survival: the CPU speeds up every rally — how long can you last?',
    hint_modo_multi: 'Online multiplayer: rooms, duels and the Pulse badge',
    hint_modo_champs: 'Championships: Halloween, Orbital Station, West, Magic and Madness',
    hint_modo_rank: 'World ranking per championship (top 10)',
    hint_modo_tut: 'The Academy: first-steps tutorial',
    hint_modo_opts: 'Every game option, sorted in sub-sections',
    hint_cat_juego: 'CPU difficulty, adaptive rival, boosted paddle and style',
    hint_cat_sala: 'Room and table: opens the game room so you SEE the changes',
    hint_cat_sonido: 'Music, effects, megaphone voice and separate volumes',
    hint_cat_visual: 'Ball trail, hit haptics and tips',
    hint_cat_perfil: 'Your name, telemetry and records reset',
    hint_cat_rendi: 'FPS, per-headset calibration and headset sharpness',
    hint_cat_pala: 'Paddle placement on the controller, saved grips',
    hint_diff: 'CPU level in free match (easy · medium · hard)',
    hint_adapt: 'The CPU raises or lowers its level with the score',
    hint_pmej: 'Paddle superpowers in power duels',
    hint_rivstyle: 'Rival personality made visible: aggressive ones step in and celebrate',
    hint_theme: 'Instantly change the room vibe (floor, walls and lights)',
    hint_psthru: 'Use your real room as the backdrop (Quest passthrough)',
    hint_mesa_altoy: 'Point at the table, hold the trigger and move it up or down: its height shows BIG',
    hint_mesa_altomen: 'Lower the table by 1 cm',
    hint_mesa_altomas: 'Raise the table by 1 cm',
    hint_mesa_skin: 'Table color; 🔒 ones unlock by winning matches',
    hint_music: 'Menu and championship music on/off',
    hint_amb: 'Room ambience (crowd and hall) on/off',
    hint_voz: 'Megaphone voice (score calls) on/off',
    hint_sndtest: 'Sound test; press twice to repair audio',
    hint_mvol: 'MUSIC volume: aim at the bar or use − and +',
    hint_fvol: 'EFFECTS volume (ball, table, net): bar or − and +',
    hint_mvolset: 'Hold the trigger on the bar and slide your controller left or right',
    hint_fvolset: 'Hold the trigger on the bar and slide your controller left or right',
    hint_trail: 'Glowing trail behind the ball on/off',
    hint_tips: 'First-session tips on/off',
    hint_hapt: 'Controller vibration on hits on/off',
    hint_pname: 'Type your name for ranking and multiplayer',
    hint_tele: 'Anonymous crash and performance telemetry',
    hint_reset: 'Erases ranking, records, achievements and powers (press twice)',
    hint_perfAuto: 'The game calibrates itself to hold steady 60 FPS',
    hint_perfTier: 'Manual quality profile for your headset',
    hint_perfRecal: 'Measure your headset FPS again and adjust quality',
    hint_perfFfr: 'Headset sharpness: less foveation = cleaner image at the edges',
    hint_kofi: 'Support development with a coffee',
    hint_sala_sala: 'The room vibe: Pabellón, Neón, Sunset and Arctic + passthrough',
    hint_sala_mesa: 'The table: slide it up/down and recolor it — all live',
    arc_power_clown: 'The Clown goes crazy! Confetti incoming!',
    arc_power_warn: 'SUPER POWER INCOMING! GET READY…',
    // v2.106 · ARKANOID instruction poster (La Locura)
    instr_ark_t: 'TEST · CRAZY ARKANOID',
    instr_ark: [
      'A BRICK WALL takes the place of the table: swing your PADDLES and knock bricks out with the ball.',
      'You get 2 MINUTES and 5 LIVES (serves). Every broken brick scores; bounces are physical, mind the angles!',
      'Later you get a RAY GUN in your free hand: aim and shoot the bricks the ball cannot reach.',
      'Alarm at the last 10 seconds: give it your best!',
    ],
    arc_power_confetti: 'SUPER POWER! CHAOTIC CONFETTI 8 s!',
    arc_power_ball: 'SUPER POWER! CRAZY BALL: red, giant and slow!',
    arc_power_globos: 'SUPER POWER! BALLOON SHOWER on your court: pop them with the paddle!',
    arc_power_burla: 'SUPER POWER! MOCK: mocking cardboards stop the ball! The black WILDCARD: hit it and win the point',
    burla_comodin: 'WILDCARD! The ball turned BLACK and giant: hit it and the point is YOURS!',
    arc_music: 'Championship music (background)',
    arc_music_global: 'Championships music (same for all)',
    arc_music_msg: 'Championships music: {v}',
    arc_music_off_word: 'muted',
    arc_music_muted: 'MUTED',
    arc_music_hint: '−/+ volume',
    arc_map_title: 'CHAMPIONSHIP ROUTE',
    arc_map_sub: 'Beat every rival and pass the skill tests',
    arc_map_start: 'START',
    arc_map_locked: 'coming soon',
    arc_map_trophy: 'TROPHY',
    arc_map_legend: 'Paddle skill tests between rivals · golden ring: your progress',
    // ---- v2.38 · ARKANOID TRIAL (2nd stop of the path)
    btn_ark_go: 'TRIAL: ARKANOID · the brick wall',
    ark_locked: 'Beat CLOWN Lv. 1 to unlock the ARKANOID trial',
    ark_map_clown: 'CLOWN Lv.1',
    ark_map_ark: 'ARKANOID',
    ark_title: 'ARKANOID!',
    ark_intro: 'Break ALL the bricks within 2 minutes',
    ark_serve_hint: 'TRIGGER: toss the ball · hit it with your paddle',
    ark_autoserve: 'Auto-serve…',
    ark_life: 'Ball lost! {n} lives left',
    ark_timeup: "TIME'S UP!",
    ark_nolives: 'NO LIVES LEFT!',
    ark_retry: 'The trial repeats: one more chance, try again!',   // v3.6.12 (ronda 15)
    ark_win: 'WALL DESTROYED!',
    // v2.96 · replay cleared stages
    replay_up: 'REPLAYING STAGE {n} · good luck, stranger!',
    replay_done: 'REPLAY CLEARED! The route stays as it was: aim at another stage or ride on',
    ark_gun_get: 'SUPERPOWER: RAY GUN on your free hand!',
    // ---- v2.44 · FULL PATH (5 steps) + ARKANOID 2 + TROPHY ----
    btn_ark2_go: 'TRIAL: ARKANOID 2 · red and blue bricks',
    ark2_locked: 'Beat CLOWN Lv. 2 to unlock ARKANOID 2',
    ark_map_clown2: 'CLOWN Lv.2',
    ark_map_clown3: 'CLOWN Lv.3',
    ark_map_ark2: 'ARKANOID 2',
    ark2_title: 'ARKANOID 2!',
    ark2_intro: 'LASER the BLUE ones · paddle the RED ones · 2.5 min',
    ark2_hint: 'BLUE: only the LASER turns it red · RED: only the PADDLE breaks it',
    ark2_win: 'WALL DESTROYED!',
    ark2_back: 'Back to the previous step: new match vs CLOWN Lv. 2',
    ark2_next: 'Up next: CLOWN Lv. 3, the final boss!',
    ark_gun_on: 'LASER GUN equipped · free-hand trigger',
    clown2_up: 'LEVEL 2! The Clown got smarter',
    clown3_up: 'LEVEL 3! Careful: double ball incoming!',
    arc_power_split: 'SUPER POWER! THE BALL SPLITS IN TWO!',
    split_saved: 'You lost one ball… but the OTHER one is still alive!',
    split_end: 'Double ball over!',
    trophy_get: 'TROPHY: CHAMPIONSHIP OF MADNESS!',
    champdone_big: 'ACHIEVED!',
    champdone_sub: 'CHAMPIONSHIP COMPLETED',
    champdone_msg: 'Badge achieved!',
    champdone_replay: 'You can replay any stage anytime',
    champ_done_chip: '★ COMPLETED',
    champ_done_hint: '★ COMPLETED · replay any stage from the map',
    // r72 · championship locks + loading curtain
    champ_locked_soon: 'Coming soon',
    champ_locked_chip: 'COMING SOON',
    champ_locked_hint: 'Still in the works · unlock rules announced soon',
    champ_telon: 'Setting up the arena...',
    // r73 · resilient index + theatre curtain
    champ_cargando: 'Loading championships…',
    champ_reintentar: '⟳  RETRY',
    champ_telon_presenta: 'CRAZY PING PONG PRESENTS',
    champ_stage_hint: 'Stage {n}/{total} · pick up where you left off',   // v3.6.17 (ronda 21)
    champ_leyenda_chip: '★ LEGEND',   // v3.6.18 (ronda 24)
    champ_leyenda_hint: '★ LEGEND · route sealed 5/5 in legend mode',
    trophy_sub: 'You are the CHAMPION · trophy added to your collection',
    trophy_rank: 'TROPHY: CHAMPION!',
    // v2.48 · expanded palmarés (real records in the RANKING panel)
    arc_rec_rally: 'Best rally: {n} hits',
    arc_rec_streak: 'Best streak: {n} rounds',
    arc_rec_surv: 'Survival best: {n} hits',
    arc_rec_ach: 'Achievements: {n}/{m}',
    fan_hint: 'Fan the paddle (quick left-right) to make wind and push the ball!',
    // v2.46 · black TIME-EXTRA brick (ARKANOID 2)
    ark_extra_min: '+1 EXTRA MINUTE!',
    // v3.6.44 · bomb brick of ARKANOID 2 (stage 4 of Madness)
    ark_bomba_boom: 'BOOM! DETONATION!',
    // v3.6.45 · electric brick of ARKANOID 2 (the last 30 s)
    ark_elec_on: 'ELECTRIC BRICK! Hit it with the BALL',
    ark_elec_aran: 'WALL ELECTRIFIED! One more hit… CHAIN!',
    hud_time: 'TIME',
    hud_bricks: 'BRICKS',
    hud_lives: 'LIVES',
    gun_hint: 'GUN ready · pull the free-hand trigger to fire rays',
    sb_clown: 'CLOWN',
    arc_rank_win: 'WIN',
    arc_rank_lose: 'LOSS',
    arc_rank_tot: 'Won: {n} · Streak: {s}',
    online_lbl: 'ONLINE · vs another player',
  multi_hint: 'Create room and enter a friend\u2019s code live inside MULTIPLAYER',
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
    msg_adapt: 'Adaptive rival: {v} — adjusts to the score',
    msg_mic: 'Scoreboard announcer: {v}',
    hint_hit: 'Hit the ball toward the table with your paddle!',
    hint_toss_high: 'Toss the ball a bit higher',
    hint_behind: 'Serve from behind the end line',
    srv_reancla: 'Ball repositioned · serve behind the end line',
    hint_dropped: 'Ball dropped · toss again',
    online_first: 'Connected! Waiting for the host…',
    online_serve: 'Online match · your serve (TRIGGER to toss)',
    net_ended: '{msg} · local match restarted',
    peer_gone: 'Your rival has left',
    conn_lost: 'Connection lost',
    peer_closed: 'Your rival closed the room',
    bye_self: 'You closed the connection',   // r37 (v3.6.133): hangup i18n
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
    sb_bo: 'BEST OF {n}',
    calib_msg: 'TRAINING · Y: back to the training hub',
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
    // v3.6.51 (r59) · LA ACADEMIA — interactive tutorial (EN text)
    tut_hub: 'TUTORIAL',
    tut_hub_sub: 'Learn to play in 3 minutes · step by step, with real practice',
    tutask_title: 'FIRST TIME?',
    tutask_sub: 'We teach you how to play: the controller, the serve and every mode',
    tutask_yes: 'START TUTORIAL',
    tutask_no: 'NOT NOW',
    tut_title: 'CRAZY ACADEMY',
    tut_step: 'STEP {n} OF {m}',
    tut_hint_next: 'TRIGGER · continue',
    tut_hint_skip: 'B · skip · STICK · repeat the voice',
    tut_s0_t: 'WELCOME TO THE ACADEMY',
    tut_s0_l1: 'In 3 minutes you will serve, rally and pick your favorite mode.',
    tut_s0_l2: 'Every step has a real exercise: do it to continue.',
    tut_s0_go: 'TRIGGER · start',
    tut_s1_t: 'YOUR CONTROLLERS',
    tut_s1_l1: 'LEFT: Y and X buttons · RIGHT: B and A.',
    tut_s1_l2: 'TRIGGER: launch and hit · GRIP (side): release the ball.',
    tut_s1_l3: 'B: menu · Y: back · STICK: hear the selected power in a match.',
    tut_s1_task: 'PRACTICE: press the TRIGGER',
    tut_s2_t: 'THE PADDLE',
    tut_s2_l1: 'The paddle is already in your hand: it is your racket. No fiddly buttons.',
    tut_s2_l2: 'Swing it firmly through the air to continue.',
    tut_s2_task: 'PRACTICE: swing the paddle hard',
    tut_s3_t: 'THE SERVE',
    tut_s3_l1: 'The ball rests in your FREE HAND (the one without the paddle).',
    tut_s3_l2: 'Press the TRIGGER to toss it and hit it with the paddle',
    tut_s3_l3: 'so it crosses the net (it must bounce on both sides).',
    tut_s3_task: 'PRACTICE: land 3 valid serves',
    tut_s3_again: 'Again: the ball returns to your free hand',
    tut_s3_cnt: 'VALID SERVES',
    tut_s3_ok: 'Valid serve! Keep going',
    tut_s4_t: 'THE RALLY',
    tut_s4_l1: 'Your coach returns the ball. Hit it back',
    tut_s4_l2: 'over the net. Six returns and you pass.',
    tut_s4_task: 'PRACTICE: return 6 balls',
    tut_s4_n: 'Returns: {n}/6',
    tut_s5_t: 'BUTTONS IN A MATCH',
    tut_s5_l1: 'A or X: switch the paddle to that hand (try it now!).',
    tut_s5_l2: 'B: menu · STICK (in a match): hear the selected power.',
    tut_s5_l3: 'Every 20 rally hits grant you one power charge.',
    tut_s5_task: 'PRACTICE: press A or X',
    tut_s6_t: 'THE MODES · 1 OF 2',
    tut_mods_t: 'THE MODES',
    tut_mod_p: 'vs the CPU · best of 3',
    tut_mod_s: 'Survive endless rallies',
    tut_mod_m: 'Online with a 5-letter code',
    tut_mod_c: '6 rivals, each with a story',
    tut_mod_r: 'Compete with the world',
    tut_mod_t: '5 areas to polish technique',
    tut_m_t: 'YOUR CONTROLLER, YOUR RACKET',
    tut_lab_pala: 'YOUR RACKET',
    tut_pow_t: 'POWERS · CHAMPIONSHIPS ONLY: 20 straight hits charge · trigger fires · 10 s',
    tut_s6_m1: 'MATCH · against the CPU (3 levels). Best of 3 sets.',
    tut_s6_m2: 'SURVIVAL · survive as many consecutive rallies as you can.',
    tut_s6_m3: 'MULTIPLAYER · online with a 5-letter code.',
    tut_s7_t: 'THE MODES · 2 OF 2',
    tut_s7_m1: 'CHAMPIONSHIPS · 6 rivals with their own story. Crown the WEST!',
    tut_s7_m2: 'WORLD RANKING · compete with players from everywhere.',
    tut_s7_m3: 'TRAINING · PRO TRAINING: 5 areas to polish your technique.',
    tut_s7_p: 'POWERS: Mega Paddle · Spin · Magnet · Portal · Clone — with the ball alive, the free-hand TRIGGER releases the one you have charged.',
    tut_s8_t: 'YOU KNOW HOW TO PLAY!',
    tut_s8_l1: 'That is it: serve, rally, earn charges and release powers.',
    tut_s8_l2: 'TRIGGER = play NOW against the CPU · B = back to the menu.',
    tut_s8_go: 'TRIGGER · PLAY NOW',
    tut_done_msg: 'You know how to play! Welcome to Crazy Ping Pong',
    tut_bad_online: 'The tutorial is not available in multiplayer',
    tut_bad_busy: 'Finish the active trial first to enter the Academy',
    tut_lab_trigger: 'TRIGGER',
    tut_lab_stick: 'STICK',
    tut_lab_grip: 'GRIP',
    tut_lab_btns: 'A/X · B/Y',
    tut_lab_btns_i: 'Y · X (left)',
    tut_lab_btns_d: 'B · A (right)',
    // r65 · gamified academy (native voice + GLB controller + visual rules)
    tut_rep: 'STICK · repeat the voice',
    tut_m1_gat: 'ACTION · squeeze the TRIGGER',
    tut_m1_grip: 'ACTION · squeeze the side GRIP button',
    tut_m1_stick: 'ACTION · tilt the STICK',
    tut_m1_a: 'ACTION · press A (or X)',
    tut_m1_ok: 'Controllers mastered!',
    tut_m1_raf: 'YOUR CONTROLLER IS YOUR RACKET · trigger to continue',
    tut_m1_lado: 'MOVE IT SIDE TO SIDE · firm swing with the paddle',
    // r66 · redesigned steps: REAL serve and rally on the table
    tut_d3_t: 'THE SERVE · WATCH THE TABLE',
    tut_d3_l1: 'The ball rests in the free hand; the TRIGGER releases it.',
    tut_d3_l2: 'It must bounce on YOUR side first, then on theirs.',
    tut_d3_l3: 'No return from the rival: POINT for you.',
    tut_d3_go: 'TRIGGER · YOUR TURN: 3 VALID SERVES',
    tut_d3_p1: '1st YOUR SIDE',
    tut_p1r: '1st HIS SIDE (rival)',
    tut_d3_p2: '2nd OPPONENT',
    tut_d3_pto: 'POINT!',
    tut_d4_t: 'THE RALLY',
    tut_d4_l1: 'Serve again: the rival returns and the rally begins.',
    tut_d4_l2: 'Whoever loses the rally concedes the point…',
    tut_d4_l3: 'and every 2 SERVES the server rotates: 2 you, 2 them.',
    tut_d4_task: 'Serve and win the rally (the rival will miss at the end)',
    tut_d4_ok: 'POINT! That is how a match flows',
    tut_d5_t: 'THE SCOREBOARD',
    tut_d5_l1: 'Games go to 11 points, winning by 2.',
    tut_d5_l2: 'The serve rotates every 2 points…',
    tut_d5_l3: 'and at 10-10, EVERY point. First to lead by 2 wins.',
    tut_ent: 'GOT IT · trigger to continue',
    tut_h_tu: 'YOU',
    tut_h_ia: 'RIVAL',
    tut_h_saq: 'SERVE',
    tut_h_10: '10-10!',
    tut_h_p2: '+2 TO WIN!',
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
    ov_kofi: '☕ Support on Ko-fi',
    ov_tv: 'Watch live matches without a headset',
    // r109 · M3 PWA (portada): install button + toasts
    ov_pwa: '📲 INSTALL ON HEADSET',
    pwa_manual: '<b>Install it in 2 taps:</b> open the browser <b>⋮</b> menu and choose <b>"Install app"</b>. Its own icon on the headset, no URL typing and automatic updates.',
    pwa_installed: '<b>App installed!</b> CRAZY PING PONG now lives on your headset: find it among your apps.',
    pwa_ready: 'Ready to install: press again and choose "Install" in the dialog.',
    music_title: 'Music (landing and VR menu)',
    ov_hint: '<b>On the headset:</b> upload this folder to <b>Netlify Drop</b> and open the link with the <b>Meta Quest Browser</b> (HTTPS required).',
    ov_lang: '🌐 Language / Idioma',
  },
};

/** Traducción con parámetros: T('clave', {p: 3}) sustituye {p}. */
/** v2.66 · NOMBRE del jugador para los rankings. Se escribe desde
 *  Opciones del menú VR (página TU NOMBRE, teclado en pantalla) y se
 *  muestra presidiendo las tarjetas de ranking de TODOS los campeonatos.
 *  Máx. 12 caracteres, se recorta y limpia en cada lectura. */
export function ppPlayerName() {
  try { return String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); }
  catch { return ''; }
}

/* ==========================================================================
 *  v2.110 · MENÚ HUB — el feedback del juego fue claro: los menús se veían
 *  «liosos» y con demasiadas opciones a la vez. La página principal deja el
 *  acordeón y pasa a ser un HUB de TARJETAS grandes con ACCESO DIRECTO a
 *  cada modo de juego (PARTIDO · ENTRENAR · SUPERVIVENCIA · MULTIJUGADOR ·
 *  CAMPEONATOS · RANKING), cada una con icono propio, color identitario,
 *  una sola línea de contexto (récord/estado) y chevron. La DIFICULTAD de
 *  la CPU queda siempre a la vista (afecta a PARTIDO) y los mandos
 *  frecuentes se agrupan en AJUSTES RÁPIDOS (música, ambiente, voz,
 *  vibración, estela, sala en ciclo, tu nombre). NADA se pierde: la página
 *  AJUSTES conserva TODAS las opciones que tenía Opciones y los
 *  CAMPEONATOS ganan su propia página con tarjeta+insignia por campeonato,
 *  la música global y los controles que declare cada módulo. Iconos
 *  vectoriales (PP_ICONS) sin imágenes nuevas; mismo panel 1024×1536,
 *  mismo rayo/gatillo y mismos ids de acción que el acordeón.
 *  ==========================================================================
 *  v2.108 · MODO DEPURACIÓN — el nombre especial «foro3d» desbloquea el
 *  modo de revisión del creador. Comparación en minúsculas: el teclado del
 *  menú escribe en MAYÚSCULAS («FORO3D») y vale igual.
 *  Qué habilita (todo lo demás queda EXACTAMENTE igual):
 *   1) El mapa del camino de CUALQUIER campeonato muestra las 5 ETAPAS y el
 *      gatillo salta a cualquiera sin requisitos de progreso (los módulos
 *      consultan window.__PP_DEBUG en replayMap/replayLaunch/_refreshMap).
 *   2) NO genera registros: interceptor de escritura que descarta en frío
 *      las claves de progreso (pp_champ_* de Oeste y Magia, pp_arcade_* de
 *      La Locura) y la caché del ranking mundial; WORLDRANK.submit() no
 *      contacta con el almacén remoto y __PP_TELE.ev() no encola eventos.
 *   3) Un rótulo discreto «MODO DEPURACIÓN» en una esquina (2D en la
 *      portada y 3D anclado a la vista dentro del visor).
 *  Se re-evalúa al guardar el nombre (nkey:ok) y al arrancar: activar o
 *  quitar el nombre surte efecto al instante, sin recargar la página. */
export function ppDebugMode() {
  try { return String(localStorage.getItem('pp_player_name') || '').trim().toLowerCase() === 'foro3d'; }
  catch { return false; }
}
try { window.__PP_DEBUG = ppDebugMode(); } catch { /* */ }
try {
  window.ppDebugRefresh = function () {
    try { window.__PP_DEBUG = ppDebugMode(); } catch { /* */ }
    try { if (window.__ppDbg2D) window.__ppDbg2D(); } catch { /* */ }
  };
} catch { /* */ }

/* v2.108 · interceptor de PERSISTENCIA del modo depuración: mientras
 * __PP_DEBUG esté activo, las claves de REGISTRO no se escriben (el resto
 * — idioma, música, nombre, opt-outs — sigue igual). Al desactivar el modo
 * el interceptor deja pasar todo: cero riesgo para el jugador normal. */
(function () {
  try {
    const OP = Storage.prototype;
    if (OP.__ppDebugGuard) return;
    const _si = OP.setItem;
    OP.setItem = function (k, v) {
      try {
        if (typeof window !== 'undefined' && window.__PP_DEBUG) {
          const s = String(k);
          if (s.indexOf('pp_champ_') === 0 || s.indexOf('pp_arcade_') === 0 ||
              s === 'pp_worldrank_cache' || s === 'ppxr_stats_v1') return;
        }
      } catch (e) { /* */ }
      // r128 · E2 (auditoría r120): QuotaExceeded avisa UNA vez por sesión
      // (toast reutilizable de la portada + telemetría) y re-lanza: los
      // saves que ya tragaban el error siguen igual, pero el jugador deja
      // de perder progreso en silencio.
      try {
        return _si.call(this, k, v);
      } catch (err) {
        try {
          const llena = err && (err.name === 'QuotaExceededError' ||
            err.name === 'NS_ERROR_DOM_QUOTA_REACHED' || err.code === 22);
          if (llena && typeof window !== 'undefined' && !window.__ppStorageAviso) {
            window.__ppStorageAviso = true;
            if (typeof T === 'function') {
              if (window.__ppPwaToast) window.__ppPwaToast(T('storage_lleno'), 9000);
            }
            if (window.__PP_TELE) window.__PP_TELE.ev('storage_lleno', { k: String(k).slice(0, 24) });
          }
        } catch (e2) { /* el aviso nunca revienta */ }
        throw err;
      }
    };
    OP.__ppDebugGuard = true;
  } catch (e) { /* sin Storage: nada que proteger */ }
})();

/** v2.67 · RANKING MUNDIAL — top 10 PERSISTENTE por campeonato.
 *  Almacén remoto: un objeto JSON público y mutable (api.restful-api.dev)
 *  con GET (traer) y PUT (publicar). SIEMPRE queda caché local
 *  (pp_worldrank_cache): sin conexión se sigue mostrando el último ranking
 *  conocido. submit() hace GET → fusión por NOMBRE (el mejor resultado de
 *  cada jugador se conserva; una persona = una fila) → orden → top 10 →
 *  PUT. Entrada: { n: nombre, p: puntos/victorias, a: logros, t: fecha }.
 *  Nada de esto rompe nunca el juego: todo fallo de red se ignora en
 *  silencio y la partida sigue igual. Expuesto como window.__PP_WORLD
 *  para que los campeonatos externos (magia) también puedan publicar. */
export const WORLDRANK = {
  URL: 'https://api.restful-api.dev/objects/ff808181a09d98f701a113379f070d41',
  CACHE: 'pp_worldrank_cache',
  status: 'idle',              // idle | loading | online | offline
  data: null,                  // { champs: { locura: […], magia: […] } }
  lastTs: 0,

  _sanitize(e) {
    try {
      const p = Math.max(0, Math.min(1e7, parseInt(e.p, 10) || 0));
      const n = String(e.n || '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, 12);
      if (!n) return null;
      const a = String(e.a || '').replace(/[\u0000-\u001f]/g, '').slice(0, 12);
      const t = Math.max(0, parseInt(e.t, 10) || Date.now());
      return { n, p, a, t };
    } catch { return null; }
  },

  /** Normaliza cualquier forma remota ({data:{…}} o pelada) a una lista
   *  sana por campeonato: filas válidas, ordenadas por puntos, máx. 10. */
  _normalize(raw) {
    const out = { champs: {} };
    const src = (raw && raw.data) ? raw.data : (raw || {});
    const ch = (src && src.champs) || {};
    for (const k of Object.keys(ch)) {
      if (!Array.isArray(ch[k])) continue;
      out.champs[k] = ch[k]
        .map((e) => this._sanitize(e)).filter(Boolean)
        .sort((x, y) => (y.p - x.p) || ((x.t || 0) - (y.t || 0)))
        .slice(0, 10);
    }
    return out;
  },

  _saveCache() {
    try { localStorage.setItem(this.CACHE, JSON.stringify({ data: this.data, ts: this.lastTs })); } catch { /* */ }
  },

  list(champ) {
    if (this.data && this.data.champs && Array.isArray(this.data.champs[champ])) return this.data.champs[champ];
    try {
      const c = JSON.parse(localStorage.getItem(this.CACHE) || 'null');
      if (c && c.data && c.data.champs && Array.isArray(c.data.champs[champ])) return c.data.champs[champ];
    } catch { /* */ }
    return [];
  },

  _timeout() {
    const ctl = new AbortController();
    const to = window.setTimeout(() => ctl.abort(), 8000);
    return [ctl, to];
  },

  /** Carga (GET) del ranking mundial. force=true revalida siempre;
   *  sin fuerza solo la primera vez (después sirve la caché). */
  async load(force) {
    if (this.status === 'loading') return this.data;
    if (!force && this.data) return this.data;
    if (!this.data) {
      try {
        const c = JSON.parse(localStorage.getItem(this.CACHE) || 'null');
        if (c && c.data) { this.data = this._normalize(c.data); this.lastTs = c.ts || 0; }
      } catch { /* */ }
    }
    if (typeof fetch !== 'function') { this.status = 'offline'; return this.data; }
    this.status = 'loading';
    try {
      const [ctl, to] = this._timeout();
      const res = await fetch(this.URL, { method: 'GET', signal: ctl.signal, mode: 'cors' });
      window.clearTimeout(to);
      if (!res.ok) throw new Error('HTTP ' + res.status);
      this.data = this._normalize(await res.json());
      this.lastTs = Date.now();
      this.status = 'online';
      this._saveCache();
    } catch { this.status = 'offline'; }
    return this.data;
  },

  /** Publica un resultado: GET fresco → fusión por nombre (mejor p) →
   *  orden → top 10 → PUT. Devuelve true si el PUT salió. */
  async submit(champ, entry) {
    // v2.108: MODO DEPURACIÓN — el jugador especial jamás publica en el
    // ranking mundial (ni GET ni PUT): ni siquiera se contacta con la red.
    try { if (typeof window !== 'undefined' && window.__PP_DEBUG) return false; } catch { /* */ }
    const e = this._sanitize(entry);
    if (!e || !e.p) return false;          // sin puntos no ensuciamos el ranking
    const rows = [];
    const add = (row) => {
      if (!row) return;
      const i = rows.findIndex((r) => r.n.toLowerCase() === row.n.toLowerCase());
      if (i === -1) rows.push(row);
      else if (row.p > rows[i].p || (row.p === rows[i].p && rows[i].t && row.t < rows[i].t)) rows[i] = row;
    };
    let remote = null;
    try {
      const [ctl, to] = this._timeout();
      const res = await fetch(this.URL, { method: 'GET', signal: ctl.signal, mode: 'cors' });
      window.clearTimeout(to);
      if (res.ok) remote = this._normalize(await res.json());
    } catch { /* sin red: publicamos lo local y el PUT decidirá */ }
    for (const row of (remote && remote.champs && remote.champs[champ]) || []) add(row);
    add(e);
    rows.sort((x, y) => (y.p - x.p) || ((x.t || 0) - (y.t || 0)));
    if (!this.data) this.data = remote || { champs: {} };
    if (!this.data.champs) this.data.champs = {};
    this.data.champs[champ] = rows.slice(0, 10);
    this.lastTs = Date.now();
    this.status = 'online';
    this._saveCache();
    try {
      const [ctl, to] = this._timeout();
      // r128 · B1 (auditoría r120): el PUT se considera publicado SOLO con
      // 2xx — antes devolvía true incluso con 429/404/5xx y el jugador
      // creía publicada una puntuación que nadie guardó.
      const res = await fetch(this.URL, {
        method: 'PUT',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ name: 'crazypp-world-ranking', data: this.data }),
        signal: ctl.signal,
        mode: 'cors',
      });
      window.clearTimeout(to);
      if (!res.ok) { this.status = 'offline'; return false; }
      return true;
    } catch { this.status = 'offline'; return false; }
  },
};
window.__PP_WORLD = WORLDRANK;   // lo usan el núcleo y los campeonatos externos

/** v2.75 · INSIGNIAS de campeonato (arte del artista): completar un
 *  campeonato gana SU insignia y ésta preside el ranking. En la tabla
 *  RANKING MUNDIAL las filas campeonas (a === '🏆') lucen la insignia
 *  del campeonato en la columna LOGROS (reserva: el emoji de siempre).
 *  Ruta por convención de módulo: championships/<id>/assets/insignia.png.
 *  Carga perezosa una sola vez por campeonato; sin imagen no cambia nada. */
const WRL_BADGES = {};
export function wrlBadgeImg(id) {
  if (Object.prototype.hasOwnProperty.call(WRL_BADGES, id)) return WRL_BADGES[id];
  let img = null;
  try {
    img = new Image();
    img.onload = () => {
      try {
        const G = window.__game;
        if (G && G.menuOpen && G.drawMenu) G.drawMenu();   // repinta con la insignia
      } catch (e) { /* */ }
    };
    img.onerror = () => { WRL_BADGES[id] = null; };          // reserva al emoji
    img.src = new URL('championships/' + id + '/assets/insignia.png', document.baseURI).href;
  } catch { img = null; }
  WRL_BADGES[id] = img;
  return img;
}
window.__PP_WRL_BADGE = wrlBadgeImg;   // visible para tests y módulos (patrón __PP_WORLD)

/* v2.110 · ICONOS del HUB del menú (dibujo vectorial sobre el canvas:
 * pala, diana, llama, palas cruzadas, trofeo y podio — sin imágenes). */
export const PP_ICONS = {
  match(c, x, y) {          // pala + bola
    c.save(); c.translate(x, y); c.rotate(-0.5);
    c.fillStyle = '#ffdb99';
    c.beginPath(); c.ellipse(0, -6, 16, 21, 0, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#c98a4b';
    c.fillRect(-4, 12, 8, 17);
    c.restore();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x + 22, y + 17, 8, 0, Math.PI * 2); c.fill();
  },
  train(c, x, y) {          // diana + bola
    c.strokeStyle = '#bfe3ff'; c.lineWidth = 5;
    c.beginPath(); c.arc(x, y + 2, 25, 0, Math.PI * 2); c.stroke();
    c.beginPath(); c.arc(x, y + 2, 13, 0, Math.PI * 2); c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x + 19, y - 19, 9, 0, Math.PI * 2); c.fill();
  },
  surv(c, x, y) {           // llama
    c.fillStyle = '#ffe0b3';
    c.beginPath();
    c.moveTo(x, y - 30);
    c.bezierCurveTo(x + 26, y - 6, x + 20, y + 26, x, y + 28);
    c.bezierCurveTo(x - 20, y + 26, x - 26, y - 6, x, y - 30);
    c.fill();
    c.fillStyle = '#ff9d3f';
    c.beginPath();
    c.moveTo(x, y - 8);
    c.bezierCurveTo(x + 13, y + 6, x + 10, y + 22, x, y + 24);
    c.bezierCurveTo(x - 10, y + 22, x - 13, y + 6, x, y - 8);
    c.fill();
  },
  multi(c, x, y) {          // dos palas cruzadas
    c.save();
    c.strokeStyle = '#e0d1ff'; c.lineWidth = 7; c.lineCap = 'round';
    c.beginPath(); c.moveTo(x - 21, y - 21); c.lineTo(x + 21, y + 21); c.stroke();
    c.beginPath(); c.moveTo(x + 21, y - 21); c.lineTo(x - 21, y + 21); c.stroke();
    c.restore();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x, y, 7, 0, Math.PI * 2); c.fill();
  },
  duelo(c, x, y) {          // r79: rayo de los DUELOS LOCOS (poderes)
    c.fillStyle = '#ffe066';
    c.beginPath();
    c.moveTo(x + 7, y - 28);
    c.lineTo(x - 14, y + 3);
    c.lineTo(x - 2, y + 3);
    c.lineTo(x - 8, y + 28);
    c.lineTo(x + 16, y - 6);
    c.lineTo(x + 3, y - 6);
    c.closePath();
    c.fill();
    c.fillStyle = 'rgba(255,255,255,0.85)';
    c.beginPath(); c.arc(x - 20, y - 19, 5, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(x + 22, y + 16, 4, 0, Math.PI * 2); c.fill();
  },
  opts(c, x, y) {           // v2.123 · engranaje (AJUSTES)
    c.save();
    c.strokeStyle = '#d3dee8'; c.lineWidth = 7; c.lineCap = 'round';
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4;
      c.beginPath();
      c.moveTo(x + Math.cos(a) * 15, y + Math.sin(a) * 15);
      c.lineTo(x + Math.cos(a) * 26, y + Math.sin(a) * 26);
      c.stroke();
    }
    c.beginPath(); c.arc(x, y, 14, 0, Math.PI * 2); c.lineWidth = 8; c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x, y, 4.5, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  champ(c, x, y) {          // trofeo
    c.fillStyle = '#ffe08a';
    c.beginPath();
    c.moveTo(x - 16, y - 22); c.lineTo(x + 16, y - 22);
    c.lineTo(x + 12, y + 2);
    c.quadraticCurveTo(x, y + 12, x - 12, y + 2);
    c.closePath(); c.fill();
    c.strokeStyle = '#ffe08a'; c.lineWidth = 4;
    c.beginPath(); c.arc(x - 21, y - 14, 8, Math.PI * 0.5, Math.PI * 1.5); c.stroke();
    c.beginPath(); c.arc(x + 21, y - 14, 8, Math.PI * 1.5, Math.PI * 0.5); c.stroke();
    c.fillRect(x - 4, y + 10, 8, 8);
    c.fillRect(x - 14, y + 18, 28, 6);
  },
  rank(c, x, y) {           // podio + estrella
    c.fillStyle = '#a5f0d8';
    c.fillRect(x - 26, y + 4, 15, 22);
    c.fillRect(x + 11, y + 12, 15, 14);
    c.fillRect(x - 7, y - 10, 14, 36);
    c.fillStyle = '#ffffff';
    c.beginPath();
    for (let i = 0; i < 5; i++) {
      const a = -Math.PI / 2 + i * Math.PI * 2 / 5;
      const a2 = a + Math.PI / 5;
      c.lineTo(x + Math.cos(a) * 11, y - 24 + Math.sin(a) * 11);
      c.lineTo(x + Math.cos(a2) * 4.5, y - 24 + Math.sin(a2) * 4.5);
    }
    c.closePath(); c.fill();
  },
  tut(c, x, y) {            // v3.6.51 (r59) · birrete (LA ACADEMIA)
    c.save();
    c.fillStyle = '#ffe08a';
    c.beginPath();           // palco del birrete (rombo)
    c.moveTo(x, y - 16); c.lineTo(x + 30, y - 4);
    c.lineTo(x, y + 8); c.lineTo(x - 30, y - 4);
    c.closePath(); c.fill();
    c.beginPath();           // base (mitad inferior)
    c.moveTo(x - 18, y + 1); c.lineTo(x - 18, y + 13);
    c.quadraticCurveTo(x, y + 22, x + 18, y + 13);
    c.lineTo(x + 18, y + 1); c.quadraticCurveTo(x, y + 9, x - 18, y + 1);
    c.closePath(); c.fill();
    c.strokeStyle = '#ffe08a'; c.lineWidth = 4; c.lineCap = 'round';
    c.beginPath();           // borla
    c.moveTo(x + 28, y - 2); c.lineTo(x + 28, y + 16);
    c.stroke();
    c.beginPath(); c.arc(x + 28, y + 20, 4.5, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  carrera(c, x, y) {        // M5b (r115) · escalera (LA CARRERA)
    c.save();
    c.strokeStyle = '#ffd9ec'; c.lineWidth = 7; c.lineCap = 'round';
    c.beginPath();           // dos montantes
    c.moveTo(x - 14, y - 26); c.lineTo(x - 14, y + 26); c.stroke();
    c.beginPath();
    c.moveTo(x + 14, y - 26); c.lineTo(x + 14, y + 26); c.stroke();
    c.lineWidth = 6;
    c.beginPath();           // travesaños ascendentes
    c.moveTo(x - 14, y - 10); c.lineTo(x + 14, y - 10); c.stroke();
    c.beginPath();
    c.moveTo(x - 14, y + 8); c.lineTo(x + 14, y + 8); c.stroke();
    c.fillStyle = '#ffffff';  // la bola en lo alto
    c.beginPath(); c.arc(x + 21, y - 23, 8, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  // ---- r71 · ICONOS EXPLÍCITOS de las subcategorías de AJUSTES ----
  cpu(c, x, y) {            // chip (JUEGO: dificultad, adaptativo, mega pala)
    c.save();
    c.fillStyle = '#ffe08a';
    c.fillRect(x - 20, y - 20, 40, 40);                 // cuerpo
    c.strokeStyle = '#10131a'; c.lineWidth = 3;
    c.strokeRect(x - 11, y - 11, 22, 22);               // núcleo
    c.strokeStyle = '#ffe08a'; c.lineWidth = 4; c.lineCap = 'round';
    for (let i = -1; i <= 1; i++) {                     // pines a cada lado
      c.beginPath(); c.moveTo(x + i * 13, y - 20); c.lineTo(x + i * 13, y - 30); c.stroke();
      c.beginPath(); c.moveTo(x + i * 13, y + 20); c.lineTo(x + i * 13, y + 30); c.stroke();
      c.beginPath(); c.moveTo(x - 20, y + i * 13); c.lineTo(x - 30, y + i * 13); c.stroke();
      c.beginPath(); c.moveTo(x + 20, y + i * 13); c.lineTo(x + 30, y + i * 13); c.stroke();
    }
    c.restore();
  },
  sala(c, x, y) {           // casa (SALA Y ESCENA)
    c.save();
    c.fillStyle = '#a5d8ff';
    c.beginPath();                                     // tejado
    c.moveTo(x - 28, y + 2); c.lineTo(x, y - 26); c.lineTo(x + 28, y + 2);
    c.closePath(); c.fill();
    c.fillRect(x - 20, y + 2, 40, 24);                 // muro
    c.fillStyle = '#10131a';
    c.fillRect(x - 7, y + 12, 14, 14);                 // puerta
    c.fillRect(x + 8, y + 7, 8, 8);                    // ventana
    c.restore();
  },
  mesa(c, x, y) {           // r96 · mesa de ping pong vista lateral (AJUSTES › MESA)
    c.save();
    c.strokeStyle = '#b3f0cc'; c.lineWidth = 6; c.lineCap = 'round';
    c.beginPath();                                     // tablero
    c.moveTo(x - 26, y - 2); c.lineTo(x + 26, y - 2); c.stroke();
    c.lineWidth = 5;
    c.beginPath();                                     // patas
    c.moveTo(x - 18, y + 2); c.lineTo(x - 18, y + 24);
    c.moveTo(x + 18, y + 2); c.lineTo(x + 18, y + 24);
    c.stroke();
    c.lineWidth = 4;                                   // red
    c.beginPath();
    c.moveTo(x, y - 2); c.lineTo(x, y - 14);
    c.stroke();
    c.restore();
    c.fillStyle = '#ffffff';                           // bola
    c.beginPath(); c.arc(x + 24, y - 13, 5, 0, Math.PI * 2); c.fill();
  },
  sonido(c, x, y) {         // altavoz (SONIDO)
    c.save();
    c.fillStyle = '#d8f5a2';
    c.beginPath();                                     // caja
    c.moveTo(x - 24, y - 8); c.lineTo(x - 10, y - 8);
    c.lineTo(x + 4, y - 22); c.lineTo(x + 4, y + 22);
    c.lineTo(x - 10, y + 8); c.lineTo(x - 24, y + 8);
    c.closePath(); c.fill();
    c.strokeStyle = '#d8f5a2'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath(); c.arc(x + 12, y, 9, -0.9, 0.9); c.stroke();   // onda 1
    c.beginPath(); c.arc(x + 12, y, 18, -0.9, 0.9); c.stroke();  // onda 2
    c.restore();
  },
  visual(c, x, y) {         // ojo (VISUALES)
    c.save();
    c.strokeStyle = '#d0bfff'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath();
    c.moveTo(x - 28, y);
    c.quadraticCurveTo(x, y - 26, x + 28, y);
    c.quadraticCurveTo(x, y + 26, x - 28, y);
    c.stroke();
    c.fillStyle = '#d0bfff';
    c.beginPath(); c.arc(x, y, 10, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#10131a';
    c.beginPath(); c.arc(x, y, 4.5, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  perfil(c, x, y) {         // persona (PERFIL Y DATOS)
    c.save();
    c.fillStyle = '#ffc9c9';
    c.beginPath(); c.arc(x, y - 12, 12, 0, Math.PI * 2); c.fill();   // cabeza
    c.beginPath();                                     // hombros
    c.moveTo(x - 22, y + 26);
    c.quadraticCurveTo(x - 22, y + 2, x, y + 2);
    c.quadraticCurveTo(x + 22, y + 2, x + 22, y + 26);
    c.closePath(); c.fill();
    c.restore();
  },
  pala(c, x, y) {           // r83 · pala con mini-ejes (AJUSTES › PALA)
    c.save();
    c.translate(x - 4, y - 4);
    c.rotate(0.45);
    c.fillStyle = '#ffd8a8';
    c.beginPath(); c.ellipse(0, -7, 14, 19, 0, 0, Math.PI * 2); c.fill();
    c.strokeStyle = 'rgba(16,19,26,0.5)'; c.lineWidth = 3;
    c.beginPath(); c.ellipse(0, -7, 8, 12, 0, 0, Math.PI * 2); c.stroke();
    c.fillStyle = '#e8b45a';
    c.fillRect(-3.5, 10, 7, 16);
    c.restore();
    // mini-ejes locales: X roja · Y verde · Z azul (los mismos que se
    // dibujan sobre la pala dentro del ajuste)
    c.lineWidth = 3.4; c.lineCap = 'round';
    c.strokeStyle = '#ff8787';
    c.beginPath(); c.moveTo(x + 14, y + 10); c.lineTo(x + 26, y + 10); c.stroke();
    c.strokeStyle = '#8ce99a';
    c.beginPath(); c.moveTo(x + 14, y + 17); c.lineTo(x + 26, y + 17); c.stroke();
    c.strokeStyle = '#74c0fc';
    c.beginPath(); c.moveTo(x + 14, y + 24); c.lineTo(x + 26, y + 24); c.stroke();
  },
  // ---- r72 · ICONOS de las 5 ÁREAS del ENTRENAMIENTO (PRO TRAINING) ----
  dir(c, x, y) {            // DIRECCIÓN: diana + flecha al objetivo
    c.save();
    c.strokeStyle = '#8fd3ff'; c.lineWidth = 5;
    c.beginPath(); c.arc(x - 3, y + 3, 21, 0, Math.PI * 2); c.stroke();
    c.beginPath(); c.arc(x - 3, y + 3, 10, 0, Math.PI * 2); c.stroke();
    c.fillStyle = '#8fd3ff';
    c.beginPath(); c.arc(x - 3, y + 3, 3.5, 0, Math.PI * 2); c.fill();
    c.lineCap = 'round'; c.lineWidth = 6;
    c.beginPath(); c.moveTo(x + 7, y - 7); c.lineTo(x + 24, y - 24); c.stroke();
    c.beginPath();
    c.moveTo(x + 28, y - 28); c.lineTo(x + 15, y - 26); c.lineTo(x + 26, y - 15);
    c.closePath(); c.fill();
    c.restore();
  },
  alt(c, x, y) {            // ALTURA: arco limpio por encima de la red
    c.save();
    c.strokeStyle = '#8fe3b0'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath();
    c.moveTo(x - 26, y + 18);
    c.quadraticCurveTo(x, y - 34, x + 26, y + 18);
    c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x, y - 22, 7, 0, Math.PI * 2); c.fill();
    c.strokeStyle = '#8fe3b0'; c.lineWidth = 4;
    c.beginPath(); c.moveTo(x - 20, y + 14); c.lineTo(x + 20, y + 14); c.stroke();
    c.lineWidth = 2.5;
    for (let i = -2; i <= 2; i++) {
      c.beginPath(); c.moveTo(x + i * 9, y + 14); c.lineTo(x + i * 9, y + 26); c.stroke();
    }
    c.restore();
  },
  spin(c, x, y) {           // EFECTO: bola con estela de giro
    c.save();
    c.fillStyle = '#e6c6ff';
    c.beginPath(); c.arc(x, y, 11, 0, Math.PI * 2); c.fill();
    c.strokeStyle = '#e6c6ff'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath(); c.arc(x, y, 22, Math.PI * 1.15, Math.PI * 1.85); c.stroke();
    c.beginPath(); c.arc(x, y, 22, Math.PI * 0.15, Math.PI * 0.85); c.stroke();
    c.fillStyle = '#e6c6ff';
    c.beginPath(); c.moveTo(x + 24, y - 14); c.lineTo(x + 13, y - 12); c.lineTo(x + 21, y - 3); c.closePath(); c.fill();
    c.beginPath(); c.moveTo(x - 24, y + 14); c.lineTo(x - 13, y + 12); c.lineTo(x - 21, y + 3); c.closePath(); c.fill();
    c.restore();
  },
  saque(c, x, y) {          // SAQUE: la trayectoria del doble bote
    c.save();
    c.strokeStyle = '#ffd8a8'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath(); c.arc(x - 15, y + 8, 12, Math.PI * 1.05, Math.PI * 1.95); c.stroke();
    c.beginPath(); c.arc(x + 15, y - 2, 12, Math.PI * 1.05, Math.PI * 1.95); c.stroke();
    c.fillStyle = '#ffffff';
    c.beginPath(); c.arc(x - 15, y + 8, 5, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(x + 15, y - 2, 5, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.arc(x + 26, y - 18, 6, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  rit(c, x, y) {            // RITMO: metrónomo
    c.save();
    c.fillStyle = '#ffb3d1';
    c.beginPath();
    c.moveTo(x - 16, y + 22); c.lineTo(x - 6, y - 24);
    c.lineTo(x + 6, y - 24); c.lineTo(x + 16, y + 22);
    c.closePath(); c.fill();
    c.strokeStyle = '#10131a'; c.lineWidth = 3.5; c.lineCap = 'round';
    c.beginPath(); c.moveTo(x, y - 2); c.lineTo(x + 12, y - 18); c.stroke();
    c.fillStyle = '#10131a';
    c.beginPath(); c.arc(x + 12, y - 18, 3.5, 0, Math.PI * 2); c.fill();
    c.restore();
  },
  candado(c, x, y, s) {     // r73 · candado (campeonatos PRÓXIMAMENTE)
    /* r73 · FIX DEL DESPLAZAMIENTO: la v72 hacía scale(k,k) ANTES de
     * dibujar en (x, y) absolutos — el candado se pintaba a 1,35× la
     * posición pedida (un candado flotando junto al pie del menú).
     * Ahora se TRASLADA al ancla y se escala DESPUÉS: el cuerpo se dibuja
     * alrededor del ORIGEN y (x, y) es el centro real del candado. */
    const k = s || 1;
    c.save(); c.translate(x, y); c.scale(k, k);
    c.strokeStyle = '#c9d4de'; c.lineWidth = 5;
    c.beginPath(); c.arc(0, -8, 9, Math.PI, 0); c.stroke();
    c.fillStyle = '#c9d4de';
    c.beginPath();
    if (c.roundRect) c.roundRect(-13, -8, 26, 20, 5); else c.rect(-13, -8, 26, 20);
    c.fill();
    c.fillStyle = '#10131a';
    c.beginPath(); c.arc(0, 2, 3.2, 0, Math.PI * 2); c.fill();
    c.fillRect(-1.6, 2, 3.2, 6);
    c.restore();
  },
};

export function T(key, params) {
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
export function TLang() { return __ppLang; }

/** Aplica el idioma activo al overlay 2D (elementos con data-i18n). */
export function applyLangDOM() {
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
export function setLang(l, game) {
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


/* =====================================================================
 *  v2.50 · FASE 1 · TELEMETRÍA LIGERA Y ANÓNIMA (__PP_TELE)
 *  - Cuenta SOLO eventos de uso: arranque/salida de VR, avance del
 *    campeonato, campeón, errores de página y FPS medios. SIN datos
 *    personales: sin IP almacenada, sin identificadores de usuario,
 *    sin contenido de partida. El id de sesión es aleatorio y caduca.
 *  - OPT-OUT fácil desde Opciones («Telemetría anónima: No») — se
 *    persiste en localStorage ('pp_tele') y detiene TODO envío.
 *  - Cola en localStorage ('pp_tele_q', máx 60) + envío por lotes con
 *    navigator.sendBeacon (o fetch keepalive): 5 s tras arrancar (v2.76),
 *    luego cada 30 s, al ocultar la pestaña y al cerrar.
 *  - v2.76 · DIAGNÓSTICO: st.sent / st.lastOk / st.lastErr cuentan envíos
 *    y su resultado (visibles vía window.__PP_TELE.st en consola).
 *  - Sin ENDPOINT configurado (window.PP_TELEMETRY_ENDPOINT vacío, el
 *    valor por defecto) los eventos SOLO se encolan localmente y se
 *    rotan: nada sale del dispositivo.
 *  - v2.89 · DUELO DEL «DISPARO CERTERO» (módulo oeste v7): la bola se
 *    CONGELA, la pala se vuelve el revólver del forajido y una DIANA
 *    salta por las 5 zonas de su cuerpo — 3 s para acertar (poses de
 *    impacto del artista) o la bola vuelve re-dirigida, rápida y oscura.
 *    Bola blanca en el oeste. Dinamita 0,27 m con brillo+halo+luz (fix
 *    raíz: centrado de GLB en el nodo interno — estaba BAJO EL SUELO) y
 *    cortina de humo densa ~6 s. Puerta aditiva champs.paddleGunArmed
 *    para el gatillo de la mano de la pala durante el duelo.
 *  - v2.94 · EL CAMINO COMPLETO DEL SALVAJE OESTE (módulo oeste v12):
 *    RUTA de 5 etapas con progreso (DUELO 1 · ASEDIO AL ESCONDITE · DUELO 2
 *    · ASALTO AL TREN · DUELO FINAL); el revólver del jugador pica el
 *    cañón 5° hacia abajo (petición del artista); revólver en la mano
 *    libre para el asedio (corazón = punto débil, manchones de sangre
 *    acumulables en el visor 5 s); tren con parallax, oleadas de candados
 *    dorados, silbato+túnel y ESTACIÓN BRAVOS; duelos Nv.2/FINAL más duros
 *    (aiMul 1,2/1,4) y CAMPEÓN con insignia del sheriff. Pruebas con
 *    física propia vía testStep/testActive (patrón orbe de Magia).
 *  - v2.95 · ASEDIO AL ESCONDITE 2.0 (módulo oeste v13): la prueba 1 del
 *    Salvaje Oeste se RECONSTRUYE — avenida del pueblo del lejano oeste
 *    (fachadas de madera con porches: funeraria, hotel, saloon, almacén,
 *    banco, barbería + iglesia y herrería), calle embarrada con charcos,
 *    gran depósito de agua, cactus, montañas rojizas de Arizona, buitres
 *    en el cielo y huesos de bisonte a la espalda; BOLA-BOMBA negra con
 *    la mecha encendida; DIANA del artista en puertas y ventanas que
 *    CAMBIA DE SITIO SOLA (30/20/10 s por oleada); al acertar REVIENTA el
 *    troquel (astillas) y el forajido se DESTAPA con su corazón: 3 s para
 *    rematarlo con el revólver de la mano libre; si falla, él dispara y
 *    deja MANCHONES DE SANGRE PERMANENTES que se acumulan toda la etapa;
 *    3 oleadas × 2 forajidos · 3 minutos. Fuera los troqueles de la sala
 *    durante las pruebas (igual que en el tren). Duelos y tren intactos.
 *  - v2.96 · REGISTROS + REJUGAR: (a) «Eliminar registros» reinicia TODOS
 *    los campeonatos A CERO de verdad — el módulo oeste ahora resetea su
 *    estado VIVO (la sala volvía a la etapa 3 con el storage vacío) y
 *    reabre la sala en la etapa 1 al momento; (b) REJUGAR etapas ya
 *    superadas en CUALQUIER campeonato: apunta con la PALA al nodo del
 *    mapa de la ruta (el anillo salta y se tiñe azul), tira del GATILLO
 *    y esa etapa se relanza guardando el progreso real (ni avanza ni
 *    retrocede). Mecánica genérica en ChampLoader (replayMap/replayHover/
 *    replayLaunch): oeste, locura y magia la implementan sobre su mapa.
 *  - v2.97 · DESIERTO DE LUJO + FÍSICA DE LA DINAMITA (todo en oeste v15):
 *  v2.98 · ASEDIO 3.0 — DOS PALAS · MESITA DE MADERA · EXPLOSIONES ·
 *         FORAJIDO ESTABLE · REVÓLVERES ×2 · ASISTENTE · CIELO CON CÚPULA
 *  v2.99 · ASEDIO 3.1 — OLEADAS · FACHADAS QUE SE AGUJEREAN · FORAJIDO CON
 *         REVÓLVER QUE DISPARA A LOS 2 s (oeste v17):
 *    (a) 3 EDIFICIOS INTERACTIVOS del artista: Fachada1 DELANTE (alphaMap
 *        que las explosiones AGUJEREAN estampando rotura.png como
 *        transparencia: se ve el Interior1 detrás) y forajido ENTRE ambas;
 *    (b) bombas CADA 1 SEGUNDO; (c) DIANAS de fachada SIEMPRE visibles
 *        sobre las ZONAS VERDES de zonas1.jpg (ático/entreplanta/baja);
 *    (d) forajido DE PIE en la calle, estático, con CORAZÓN en el pecho y
 *        SU revolver.glb apuntándote: a los 2 s DISPARA (sangre en la cara)
 *        salvo disparo al corazón; (e) OLEADAS de 2 min (3/4/5 forajidos)
 *        con carteles oleada1/2/3.png + oleada.mp3 (entra con velocidad,
 *        flota 4 s, sale; 5 s en pausa) y ALARMA a los 20 s; (f) asistente
 *        de puntería también en las dianas de fachada; (g) DECORADO 100%
 *        FIJO (cactus/rocas/huesos/torre en planos orientados una vez);
 *        (h) PUEBLO LEJANO del artista de ambientación al fondo.
 *  v2.100 · MIRILLA VISIBLE + PUNTERO SÓLO EN EL MAPA:
 *    (a) la MIRILLA del asedio ya no se camufla (retícula roja sobre
 *        ladrillo rojo): PLACA crema de alto contraste con borde oscuro,
 *        retícula más grande (0,52→0,64 · halo 0,84→1,00) y un FARO de
 *        luz dorado que sube desde el escondite y ASOMA SOBRE LOS
 *        TEJADOS; centrada EN LA LÍNEA VERDE de zonas1.jpg (donde
 *        aparece el forajido), no a la altura del pecho;
 *    (b) el HAZ de la pala del selector de etapas SÓLO sale cuando el
 *        rayo TOCA el mapa del camino (antes bastaba con que el mapa
 *        estuviera visible): fuera del mapa, la pala no muestra
 *        puntero — de momento es el único sitio con puntero de pala.
 *    (a) los cartuchos de dinamita ya NO se plantan de pie al tocar la
 *    mesa: aterrizan, dan un bote de asentamiento y se TUMBAN de costado,
 *    rodando y balanceándose mientras arde la mecha; (b) la bola-bomba del
 *    asedio cae JUNTO AL CANTO de la mesa del jugador (antes a media mesa,
 *    inalcanzable); (c) las dianas van DELANTE de los troqueles (antes
 *    quedaban sandwitchadas entre fachada y troquel) y son MÁS GRANDES
 *    (0,42→0,52 la cara · 0,68→0,84 el halo); (d) el pueblo del asedio se
 *    reconstruye con ARTE IA DETALLADO: 8 fachadas con cartel pintado
 *    (funeraria, hotel, saloon, almacén, banco, barbería, iglesia,
 *    herrería), depósito de agua, saguaro y biznaga, buitres, esqueleto de
 *    bisonte, rocas rojizas, cielo panorámico, sierra de mesas, pueblo
 *    lejano, arena y avenida de tierra — todo con RESPALDO procedural si
 *    una imagen no cargara. Las ventanas de hotel/almacén mueven su
 *    troquel a la VENTANA pintada (antes flotaban en la pared).
 *  v2.103 · ASEDIO 3.2 — DESCUBRIMIENTO CINEMATOGRÁFICO + CASAS:
 *    (a) el forajido DESTAPADO sale como SU IMAGEN (Forajido_duelo) y,
 *        acto seguido, se FUNDE A NEGRO y aparece SU DIBUJO APUNTANDO
 *        (Forajido_focused.png); el CORAZÓN-diana se enciende con el
 *        dibujo, está a MEDIA TALLA (0,30→0,15) y PARPADEA;
 *    (b) SU REVÓLVER apunta al JUGADOR: encaro VERIFICADO midiendo la boca
 *        del cañón en el mundo (el heurístico fijo lo invertía);
 *    (c) al DISPARAR: humo de la boca y BALA trazadora que vuela hasta la
 *        cara — la sangre y el tirón del mando llegan con la bala;
 *    (d) CASAS MÚLTIPLES del artista (Fachada2-4/Interior2-4 con las
 *        líneas verdes de zonas2-4.jpg): 3 casas DIFERENTES por oleada y,
 *        cuando lleguen las 9, las 3 oleadas no repetirán ninguna.
 *  v2.104 · ASEDIO 3.3 — SETOS RODANTES + FACHADA TRASERA + CASAS 5-7:
 *    (a) SETOS SECOS RODANTES (regalo.png) cruzan el pueblo de DERECHA a
 *        IZQUIERDA empujados por el viento; entran y se pierden FUERA de
 *        campo; talla al azar (cuanto más pequeños, MÁS RÁPIDOS), giran
 *        sobre sí mismos y aparecen cada cierto tiempo al azar;
 *    (b) FACHADA TRASERA DESTRUIBLE: un impacto sobre zona YA agujereada
 *        rompe la zona CORRESPONDIENTE del interior — HUECO REAL de lado
 *        a lado en la vivienda (se ve el horizonte a través);
 *    (c) CASAS 5-7 del artista (capilla, barbería, almacén) con las
 *        líneas verdes de zonas6-7.jpg medidas píxel a píxel (zonas5.jpg
 *        no llegó: casa 5 con filas provisionales a ras de suelo).
 *  v2.105 · ASEDIO 3.4 — ¡ESTRELLA DEL SHERIFF + POOL COMPLETO DE CASAS!:
 *    (a) MECÁNICA SORPRESA: 2-3 veces por oleada aparece una ESTRELLA
 *        dorada del sheriff flotando delante de una casa (gira, brilla,
 *        suelta chispas y parpadea al acabar); si la aciertas con una
 *        BOMBA el sheriff DESTAPA AL FORAJIDO al instante (revólveres
 *        cargados sin acertar la diana) y regala +12 s de reloj;
 *    (b) CASAS 8-9 del artista (Saloon Coyote Run y Grand Frontier Opera
 *        House) con las líneas verdes de zonas8-9.jpg medidas píxel a
 *        píxel + zonas5.jpg DEFINITIVA para la capilla: el pool llega a
 *        9 y las 3 oleadas ya NO repiten NINGUNA casa (3-3-3).
 *
 *  v2.106 · EL PUEBLO A PUNTO (informe del visor):
 *    (a) OLEADAS: la oleada dura los 2 MINUTOS COMPLETOS (el cupo de
 *        forajidos ya no corta la partida a mitad de la 3ª); al acabarse
 *        el tiempo de la 3ª → VICTORIA. Transición ESPECTACULAR: el
 *        escenario se FUNDE A NEGRO, el cartel de oleada cruza a oscuras
 *        mientras las casas se rehacen y el pueblo NUEVO reaparece.
 *    (b) GRÁFICOS: casas MÁS GRANDES y hasta el suelo (adiós hueco y
 *        dinamita visible), MÁS SEPARADAS (adiós parpadeo), línea de
 *        casas del fondo NUEVA del artista (lineapueblo.webp) mayor y
 *        más lejana, costura cielo-montañas curada (fundido de alfa),
 *        NUBES a la deriva y setos que giran bien.
 *    (c) FORAJIDO: silueta real en el desvanecimiento (adiós plano
 *        negro), corazón IMPREDECIBLE (sobre cualquier parte del cuerpo),
 *        humo que SALE DE SU PISTOLA, bala que se ve venir, más sangre,
 *        vibración en ambos mandos y GRITO. Descubierto = 2 s.
 *    (d) DERROTA: Forajido_lauging riéndose, fundido a negro y
 *        Forajido_victory con la risa del pueblo (risas_pueblo.mp3).
 *    (e) CARTELES EXPLICATIVOS antes de TODAS las pruebas de habilidad
 *        de TODOS los campeonatos (asedio, tren, arkanoid y orbe), bien
 *        maquetados y sin cortar el texto.
 *
 *  v2.107 · AJUSTES FINOS DEL VISOR (informe de la Quest):
 *    (a) FORAJIDO: descubierto = 1 s (la secuencia de foco se comprime
 *        para que el corazón dé tiempo a verse y dispararse).
 *    (b) SANGRE DEL VISOR: salpicadón FIJO pintado en la pantalla del
 *        visor (imagen sin seguimiento del mundo) + MÁS gotas que
 *        escurran con su reguero; pose copiada de la cámara XR del FRAME
 *        (adiós el retardo de 1 frame que la hacía «nadar» al girar la
 *        cabeza); en el ASEDIO cada disparo recibido también escurre.
 *    (c) CARTELES EXPLICATIVOS con la ESTÉTICA DE CADA CAMPEONATO:
 *        pergamino del oeste, carpa de circo de La Locura y pergamino
 *        arcano de Magia; y se CIERRAN AL PULSAR EL GATILLO (arranca
 *        la prueba al momento; la misma pulsación no filtra al juego).
 * ===================================================================== */
/* v3.1.1-FEEL1 · GAME-FEEL (los 3 ajustes del dueño tras probar la SRV2):
 *  1) GRACE del saque — la detección de la colisión bola-pala sigue viva unos
 *     milisegundos MÁS cuando la bola llega muy justa al borde de la hoja
 *     (SOLO en el vuelo del saque): lo que se ve que conecta, conecta.
 *  2) REBOTE REAL sobre pala quieta — fuera el suelo de rebote: peloteando
 *     en horizontal SIN fuerza, los botes decaen hasta pararse. Con swing
 *     real el suelo de salida (2,3 m/s) queda INTACTO: el resto del juego
 *     no cambia. Los micro-contactos de reposo son mudos (sin audio,
 *     sin háptica, sin árbitro) y la bola no atraviesa nunca la hoja.
 *  3) BOTÓN B = PROMPT «MENÚ PRINCIPAL ¿SI/No?» — en cualquier estancia que
 *     no sea el Hall, B muestra la pregunta: NO cierra y sigues en la
 *     escena; SI sale al HALL con el menú principal en pantalla. En el Hall
 *     (y en online/passthrough) B sigue abriendo/cerrando el menú normal.
 *  Laboratorio QA de los 3 ajustes: window.__PP_FEEL_LAB (grace/decay/
 *  stroke). Todo lo palancable vive en SERVE_TUNE (lateMs, lateInPlane,
 *  lateSkin, exitFloorFrom/To, restPadSpeed, restEventMin).
 * ===================================================================== */
export const __PP_TELE = (() => {
  /* v3.3.0-NUC1 · REACTOR DE ENERGÍA INESTABLE (etapa 2 del camino) — nueva
   * mecánica descrita por el dueño: el NÚCLEO DE GRAVEDAD (nucleo_gravedad_lp
   * .glb, GLB procedural del artista: NucleoGravedad_Principal + Halo) flota
   * tras el borde lejano (0 · 1,62 · −3,35) con ROTACIÓN CAÓTICA procedural
   * (3 ejes con senos desfasados; se calma al acertar) y lanza ESFERAS DE
   * PLASMA (una a la vez, arco balístico T 0,95-1,25 s al campo del jugador;
   * la bola real queda aparcada en HOLD). El jugador las GOLPEA con la pala
   * (bumper esfera-esfera r 0,045+0,085 + velocidad de pala ×0,85, anti-
   * rebote 250 ms, salida 2,7-7,2 m/s con arco mínimo) y las devuelve a
   * COMPUERTAS de energía (anillo + película aditiva pulsante): la
   * estabilización es el CRUCE REAL del plano de la compuerta dentro del
   * radio interior (segmento prev→pos con quaternion inverso). FASE A: 1
   * compuerta GRANDE (r 0,40) fija que rota por 4 spots (3 aciertos). FASE
   * B: 2 PEQUEÑAS (r 0,24) simultáneas, una MÓVIL con deriva sinusoidal
   * (5 aciertos). FALLO (mesa sin golpear, suelo, 2.º bote, pasada, parada,
   * tiempo): ALARMA (3 flashes rojos de sala + luz/halo rojo pulsante +
   * zumbido sawtooth + haptics en ambas manos) + MODIFIER DE GRAVEDAD de la
   * próxima esfera (PESADA ×1,45 naranja / LIGERA ×0,55 violeta, 75%) — el
   * acierto re-estabiliza la gravedad. EXPRESIONES DEL ASTRO: laughing al
   * fallar (se burla), surprised cada 3 aciertos encadenados, derrotado/
   * triunfante al cerrar; base focused con retorno programado propio
   * (_exprHold: el _exprUpdate del duelo no pisa en prueba). HUD propio
   * (tiempo · X/8 compuertas · estabilidad ●●○ · gravedad activa) + cartel
   * showInstrucciones con la skin 'estacion' y botón EMPEZAR + re-explicación
   * en reintento (regla v2.106). 2 min 30 s · 5 fallos. Fin por _finish →
   * _pruebaFin/_despuesDePrueba (patrón muro) + reenter propio en el export.
   * Regla Quest: pools en el constructor, GLB con pereza (fallback
   * procedural), CERO asignaciones por frame (vectores tmp reutilizados).
   */
  /* v3.2.1-ORB2 · AJUSTE FINO DEL DECORADO DE LA ESTACIÓN ORBITAL (informe
   * del dueño en casco): (1) ASTRO a la convención FORAJIDO — plano de
   * cuerpo entero de 2,15 m (como OESTE.spriteHeight), pies en el suelo y
   * su mismo spot (x 1,62 · z −4,5): fuera de la pared derecha y a la misma
   * altura que el resto de rivales. (2) MAPA: nodo 5 re-medido (y 266→335)
   * y TAPAS de 240 px que cubren ENTEROS los medalliones del arte (165 px
   * se quedaban cortas). (3) CARTEL DE SUPERPODER = el de la CASA (port del
   * ArcadePowerSign de La Locura: SuperPower!! a la altura de la red +
   * medallón circular del poder). (4) PODERES ENCIMA DE LA MESA (tractor/
   * motas/rocas/estrellas a TU campo). (5) EXPRESIONES DEL ASTRO por
   * momento de partida (motor del clown: angry/surprised/laughing/crazy/
   * picando/loosing/panic + derrotado/triunfante). (6) Cartel de bienvenida
   * fuera de la pared del fondo (−5,44 → −5,28).
   * ===================================================================== */
  /* v3.2.0-ORB1 · DECORADO REAL DEL CAMPEONATO ESTACIÓN ORBITAL + MUROS
   * ORBITALES (assets del dueño): (1) SALA con el arte del dueño en los 6
   * planos del módulo (literas y ventanal con la Tierra, esclusa, suelo y
   * techo — patrón vagón del Oeste). (2) RIVAL ASTRO con las 12 poses del
   * artista (convención clown assets/<estado>.webp; en duelo focused, con
   * superpoder crazy, al caer defeated/laughing). (3) MAPA nuevo del dueño
   * (1376×768, nodos re-medidos) que dibuja las etapas 2 y 4 como MUROS →
   * las pruebas del camino son ahora MUROS ORBITALES: port íntegro del
   * ARKANOID de La Locura (variante 1 clásica · variante 2 rojos/azules
   * con PISTOLA LÁSER pistol.glb, ladrillo negro +1 min y abanico
   * anti-atasco), con cartel explicativo sobre la plantilla del artista
   * (normas_astro.png vía NORMAS_SKIN v2.135). (4) CARTEL DE SUPERPODER
   * con la etiqueta de la casa (superpower.png) + miniatura del poder.
   * (5) RECORTABLES reales por el suelo (cohete, astro, lander, telescopio).
   * Núcleo intacto: CCD SDF (v3.1.2-CCD1), saque SRV2, feel FEEL1, hall,
   * CRAZY TV y el resto de campeonatos.
   * ===================================================================== */
  // v3.6.1-SDK1 · SDK DE CAMPEONATOS (FASE 3 de la modularización P0): los
  // 5 campeonatos dejan de reimplementar el kernel — nace
  // championships/sdk/champ_sdk.js v1.0.0 (SFX canónico con la lección
  // v2.125 «forma promesa» + cache + arcMute, congela()/descongela() del
  // patrón locura v2.40, puente getCore y assetURL). El orbital (el módulo
  // con QA profundo) estrena la adopción: su motor _sfx y el congelado del
  // aviso vienen ahora del SDK, con conducta idéntica. Cero cambios de
  // gameplay del núcleo: física CCD/SRV2/FEEL1 INTACTA. FASE 4: adoptar en
  // oeste (7 copias del fix v2.125), magia (2), locura y valle_neon.
  // v3.6.0-SUP1 · SUPERPODERES REDEFINIDOS + VOZ DEL ASTRO (informe del
  // dueño): (1) FREEZE REAL en el aviso de superpoder — la Locura congela la
  // partida con g.freezeT durante el cartel y el orbital NUNCA lo activaba;
  // ahora el aviso congela IA/física/saque/árbitro como siempre se presupuso.
  // (2) METEORITOS 3D: adiós a las imágenes recortadas — rocas procedurales
  // (icosaedro deformado + color por vértice basalto/óxido + flat shading)
  // que caen con calor de entrada y tumbling. (3) RAYO TRACTOR con DRON: un
  // mini dron flota encima del haz y el rayo sale de su emisor; la bola que
  // cruza o es interceptada QUEDA ATRAPADA flotando dentro del rayo y sólo
  // cuando el rayo desaparece cae VERTICALMENTE. (4) GRAVEDAD CERO real:
  // las partículas blancas ATRAEN la bola y la hacen rebotar entre ellas de
  // manera aleatoria hasta que desaparecen y la dejan caer. (5) AUDIOS del
  // ASTRO (mp3 del dueño): risa_astro.mp3 con la pose de risas (punto
  // perdido + derrotas de pruebas) y enfado_astro.mp3 cuando pierde un
  // punto. (6) REACTOR: la diana cuántica visible 2 s (antes 1 s, imposible
  // de disparar) y la pelota SIEMPRE vuelve a botar sobre la base (reposo →
  // respawn). Hereda íntegro v3.5.1-IMP2.
  // v3.5.1-IMP2 · AJUSTE FINO del REACTOR DE IMPULSO (informe del dueño en
  // casco) + ASTRO de la etapa 1 a distancia fija de la mesa: (1) GOLPEO DE
  // PALA REAL en el reactor — barrido esfera-hoja del núcleo vía el puente
  // __PP_PADDLE_SWEEP (el mismo del Escudo y del rally), adiós al bumper de
  // agarre imposible; bote-en-espera más vivo (0,80 s) y salida 3..9 m/s.
  // (2) PISTOLA LÁSER pistol.glb VISIBLE en la mano libre durante el reactor
  // (_gunUpdate corría sólo con el muro activo: nunca se montaba; ahora
  // también con impulso, desde la intro). (3) DIANAS con DESINTEGRACIÓN
  // shader (dissolve + borde de energía) al aparecer y al desaparecer y
  // restos; el láser la desintegra rápido. (4) CUBOS CUÁNTICOS a la MITAD
  // (0,16 m) y elaborados: marco de paneles de la sala + nodos ámbar +
  // carcasa + núcleo azul/rojo (geometrías fusionadas, 4 mallas/cubo).
  // (5) VELOCIDAD LUMÍNICA REORIENTADA: ventanas laterales con el cristal
  // RECORTADO (alpha real en izquierda/derecha.png), partículas FUERA de la
  // sala corriendo de DELANTE hacia ATRÁS sobre fondo negro del espacio (la
  // nave avanza). (6) ATRACTOR: racimo casi unido SIN penetraciones (huecos
  // propios + separación por pares 0,19). (7) HUD del pantallainfo: todo el
  // texto DENTRO de la pantalla del arte, sin cortes ni solapes. (8) NÚCLEO
  // detallado: columna de plasma + vidrio + blindaje con costillas y marcas
  // ámbar + domo/antena/peana + anillos de contención. Hereda íntegro
  // v3.5.0-ESC1.
  // v3.5.0-ESC1 · ETAPA 4 NUEVA «ESCUDO DE PALA · DEFENSA DEL CASCO» (mecánica reactiva del dueño): pala-escudo que devuelve ORBES DE PLASMA (estándar/pesado/inestable/rotor) con la física de siempre + GOLPE LIMPIO (zona dulce 3,5 cm + ≥4 m/s) que carga la SOBRECARGA (+20 %) hasta el ORBE PERFORANTE · 3 FASES: 3 drones artilleros → 4 drones + CENTINELA de rally (5 rebotes exponen su núcleo) → NAVE ABORDADORA con 3 cañones (uno activo cada 8 s) · INTEGRIDAD DEL CASCO (100, +30 por interludio, alerta ≤30) · BARRERA DE CASCO trasera con onda de impacto (los orbes jamás tocan al jugador) · sala propia de 14×10×6 m con arte propio v3.5.0 (escudo_pala/) · PRESSIÓN creciente tras 90 s · pantalla del techo + NOVA · derrota con astro_laughing y regreso · REORDEN del dueño: el REACTOR DE IMPULSO sube a la ETAPA 2 (el reactor NUC1 sale del camino, clase conservada) · FIX Hall: al volver de un campeonato el hall nace en saque limpio (la bola ya no rueda sobre la mesa invisible) · FIX entrenamiento: A/X cambia la pala de mano también en el PRO TRAINING (zurdos) · hereda íntegro v3.4.1-RIV1
  // v3.4.1-RIV1 · ASTRO RECOLOCADO (etapa 1 del orbital): el rival v3.2.1 (x 1,62 · z −4,5) se leía DENTRO de la pared frontal — ahora convención EXACTA de rivales bien colocados (REGLA FIJA de duelos locura/magia v2.71): x = borde derecho de la mesa + 0,50 = 1,26 · z = −3,82 (misma profundidad que CLOWN y WIZARD, 1,73 m libre de la pared) · hereda íntegro v3.4.0-IMP1
  const VERSION = '3.6.236-SDK6';
  // v3.4.0-IMP1 · REACTOR DE IMPULSO (IMP1): NUEVA ETAPA 4 del campeonato Estación Orbital (mecánica del dueño) — sala propia de 6 imágenes del dueño SIN mesa (BASE FLOTANTE base.png como punto de reposición de la pelota) · núcleo del reactor ESTABLE azul / INESTABLE rojo con rotación caótica, alarma y expulsión de CUBOS CUÁNTICOS (3/5/7 · oleadas de 120 s independientes) · destrucción por golpeo REAL de la pelota (integración por subpasos + barrido del segmento prev→cur, bumper con la velocidad de la pala, patrón REACTOR) con fragmentación en cubitos visuales · PISTOLA LÁSER (pistol.glb, pegamento del muro reutilizado; FIX: el export del módulo nunca exponía gunArmed/fireGun y el gatillo no llegaba) contra DIANAS cuánticas (diana_quantica.png, ciclo 1 s visible / 1 s de espera) que desatan PERTURBACIONES: Gravedad 0 / Atractor (un golpe destruye TODOS los cubos agrupados) / Supergravedad, con cambio automático cada 30 s INDEPENDIENTE del disparo · ventanas laterales con viaje a velocidad lumínica (estrellas con estelas del centro afuera, el mismo efecto en ambas) · PANTALLA suspendida del techo (pantallainfo.png + capa de texto): oleada, tiempo, cubos restantes, estado del reactor y perturbación activa · derrota = astro_laughing frente al jugador y regreso a la sala (etapa 1) · hereda íntegro v3.3.0-NUC1 (Reactor de energía inestable en la etapa 2) · (la CCD SDF de v3.1.2-CCD1 queda intacta) · física del núcleo sin cambios
  // v3.0.1 · sello de versión visible: la portada 2D (#verBadge) y el menú VR
  // (drawMenuHeader) leen de aquí — UNA sola fuente de verdad para verificar
  // la build dentro del casco sin depender del nombre del zip.
  try {
    if (typeof window !== 'undefined') {
      window.__PP_VERSION = VERSION;
      var __vb = document.getElementById('verBadge');
      if (__vb) __vb.textContent = 'V' + VERSION;
    }
  } catch (e) {}
  // r98 · AVISO DE VERSIÓN NUEVA: el canal de actualización falló 4 rondas
  // seguidas en el casco (r97: sw.js sin commitear → el SW viejo nunca murió;
  // además stale-while-revalidate en game.html = la 1.ª visita SIEMPRE mues-
  // tra la copia cacheada: el dueño abre UNA vez, ve la versión vieja y re-
  // porta «no cambió nada»). El juego compara su sello con PAGES-VERSION.txt
  // (network-first en el SW: siempre fresco con red) y si hay otra versión
  // levanta un BANNER ROJO imposible de perder: tocarlo pide SKIP_WAITING al
  // SW y recarga — con game.html en red-primero la carga trae la versión
  // nueva. Sin red: silencio, jamás molesta. Comprueba también cada 5 min
  // por si el casco queda abierto con la página dormida.
  try {
    if (typeof window !== 'undefined' && window.fetch) {
      var __ppAvisoVer = function () {
        fetch('PAGES-VERSION.txt?cb=' + Date.now(), { cache: 'no-store' })
          .then(function (r) { return r && r.ok ? r.text() : ''; })
          .then(function (t) {
            var m = /version=([^\s]+)/.exec(String(t || ''));
            var nueva = m && m[1];
            if (!nueva || nueva === VERSION) return;
            if (document.getElementById('ppAvisoVer')) return;
            var b = document.createElement('div');
            b.id = 'ppAvisoVer';
            b.textContent = 'NUEVA VERSIÓN ' + nueva + ' DISPONIBLE — TOCA AQUÍ PARA ACTUALIZAR';
            b.setAttribute('style', 'position:fixed;left:0;right:0;top:0;z-index:2147483647;'
              + 'background:#c62828;color:#fff;font:bold 18px sans-serif;text-align:center;'
              + 'padding:14px 8px;cursor:pointer;box-shadow:0 2px 10px rgba(0,0,0,.55)');
            b.onclick = function () {
              try {
                if (navigator.serviceWorker && navigator.serviceWorker.controller) {
                  navigator.serviceWorker.controller.postMessage('SKIP_WAITING');
                }
              } catch (e) {}
              setTimeout(function () { location.reload(); }, 500);
            };
            (document.body || document.documentElement).appendChild(b);
          })
          .catch(function () {});
      };
      setTimeout(__ppAvisoVer, 2500);
      setInterval(__ppAvisoVer, 300000);
    }
  } catch (e) {}
  const MAXQ = 60;
  // v2.50: endpoint leído EN CADA envío (perezoso): así la configuración del
  // shell es la única fuente de verdad y puede cambiarse sin recargar.
  function endpoint() {
    try { return String((typeof window !== 'undefined' && window.PP_TELEMETRY_ENDPOINT) || ''); }
    catch { return ''; }
  }

  const st = {
    on: true,          // opt-out persistente ('pp_tele')
    q: [],             // cola de eventos pendientes
    sid: null,         // id de sesión aleatorio (sin valor identificativo)
    t0: Date.now(),
    frames: 0, fpsAcc: 0, fpsSamples: [], fpsLo: null, fpsHi: null,
    // v2.76: diagnóstico de envío (sin PII: sólo contadores y hora)
    sent: 0,           // lotes aceptados por sendBeacon/fetch
    lastOk: 0,         // Date.now() del último envío aceptado
    lastErr: '',       // último fallo (texto corto)
    // r46 · GOBERNADOR DE RENDIMIENTO — la telemetría jamás cuesta FPS en
    // una partida en red: mientras dura el duelo online, si la media cae
    // bajo 58 en DOS ventanas seguidas de 5 s, la telemetría se CONGELA
    // (la cola espera en memoria, nada toca la red ni el GC) hasta que la
    // partida recupera 60+. Fuera de partida el congelado se levanta solo.
    partida: false,    // ¿hay un duelo online en curso? (c12 lo declara)
    hold: false,       // telemetría congelada por rendimiento
    bajas: 0,          // ventanas consecutivas de 5 s con fps < 58
    congelada: 0,      // nº de veces que se ha congelado en la sesión
  };

  /** r46 · el juego declara el ESTADO DE PARTIDA ONLINE: dentro, el
   *  gobernador vigila; al salir, se descongela y se vacía la cola. */
  function partida(on) {
    try {
      const antes = st.partida;
      st.partida = !!on;
      if (antes && !st.partida) {
        st.hold = false; st.bajas = 0;
        flush();           // la cola esperada sale al terminar el duelo
      }
    } catch (eGP) { /* jamás rompe el juego */ }
  }
  try { st.on = localStorage.getItem('pp_tele') !== '0'; } catch { /* */ }
  try {
    st.sid = Math.random().toString(36).slice(2, 10) + '-' +
      Date.now().toString(36).slice(-4);
  } catch { st.sid = 'sess'; }
  try {
    const saved = JSON.parse(localStorage.getItem('pp_tele_q') || '[]');
    if (Array.isArray(saved)) st.q = saved.slice(-MAXQ);
  } catch { /* */ }

  function persist() {
    try { localStorage.setItem('pp_tele_q', JSON.stringify(st.q.slice(-MAXQ))); } catch { /* */ }
  }

  function ev(name, data) {
    // v2.108: MODO DEPURACIÓN — el jugador especial no genera telemetría:
    // los eventos de revisión no llegan a la cola ni al endpoint.
    try { if (typeof window !== 'undefined' && window.__PP_DEBUG) return; } catch { /* */ }
    if (!st.on) return;
    // r45 · RANKINGS MUNDIALES — identidad MÍNIMA en cada evento: el pid
    // anónimo PERSISTENTE del social (pp_pid, 16 hex aleatorios sin valor
    // identificativo) y el nombre elegido por el jugador (pp_player_name,
    // ≤12 caracteres, ya público en la presencia del multijugador). Sin
    // ellos no hay ranking posible; con ellos el panel agrega por jugador.
    let pid = st.pid;
    if (!pid) {
      try { pid = st.pid = localStorage.getItem('pp_pid') || ''; } catch { pid = ''; }
    }
    let nom = '';
    try { nom = ppPlayerName(); } catch { /* */ }
    const e = Object.assign(
      { e: String(name), t: Date.now(), v: VERSION, sid: st.sid },
      (pid || nom) ? { pid: pid || undefined, n: nom || undefined } : {},
      data || {}
    );
    st.q.push(e);
    if (st.q.length > MAXQ) st.q.splice(0, st.q.length - MAXQ);
    persist();
    if (st.q.length >= 10) flush();
  }

  function flush(sync) {
    const ep = endpoint();
    if (!st.on || !ep || !st.q.length) return;
    // r46 · GOBERNADOR: partida online congelada → NADA sale a la red. Los
    // eventos esperan en la cola (tope MAXQ, se recortan los viejos) y
    // saldrán al descongelar o al terminar la partida. Coste del hold: cero.
    if (st.hold) return;
    // v3.6.5-SDK6 (ronda 7): el LOTE es un ARRAY DIRECTO — el receptor de
    // producción (Worker) SOLO acepta arrays (rechazó con 400 el wrapper
    // {app,events} desde v2.50: sendBeacon daba true por transporte, el juego
    // vaciaba la cola y los lotes se perdían en silencio). Es el MISMO
    // contrato que el champ_rank de Magia. El receptor local (/api/telemetria,
    // con lectura y panel) tolera ambos formatos por tolerancia histórica.
    const batch = JSON.stringify(st.q);
    try {
      // OJO: Chromium SOLO admite sendBeacon con tipos CORS-safelisted —
      // application/json se bloquea. Se envía como text/plain y el receptor
      // parsea el cuerpo JSON igualmente (Cloudflare Worker: request.text()).
      if (navigator.sendBeacon) {
        const ok = navigator.sendBeacon(ep,
          new Blob([batch], { type: 'text/plain;charset=UTF-8' }));
        if (ok) {
          // v2.76: diagnóstico (beacon aceptado por el navegador)
          st.sent++; st.lastOk = Date.now(); st.lastErr = '';
          try { console.info('[TELE] lote enviado (' + st.q.length + ' eventos)'); } catch { /* */ }
          st.q = []; persist(); return;
        }
      }
      fetch(ep, {
        method: 'POST', keepalive: !!sync,
        headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
        body: batch, mode: 'no-cors',
      }).then(() => {
        st.sent++; st.lastOk = Date.now(); st.lastErr = '';
        try { console.info('[TELE] lote enviado (' + st.q.length + ' eventos)'); } catch { /* */ }
        st.q = []; persist();
      }).catch((err) => {
        // v2.76: se reintenta; queda reflejado en __PP_TELE.st.lastErr
        try { st.lastErr = String((err && err.message) || 'fetch').slice(0, 80); } catch { /* */ }
      });
    } catch { /* red ausente: la cola espera */ }
  }

  /** Muestreo de FPS barato: 1 llamada por frame desde el bucle del juego. */
  function noteFrame(dt) {
    if (!st.on) return;
    st.frames++; st.fpsAcc += dt;
    if (st.fpsAcc >= 5) {
      const fps = st.frames / st.fpsAcc;
      const red = Math.round(fps);
      st.fpsSamples.push(red);
      if (st.fpsSamples.length > 12) st.fpsSamples.shift();
      // ronda 10: récord de la sesión (no solo las últimas 12 muestras)
      if (st.fpsLo === null || red < st.fpsLo) st.fpsLo = red;
      if (st.fpsHi === null || red > st.fpsHi) st.fpsHi = red;
      // r46 · GOBERNADOR DE PARTIDA ONLINE: dos ventanas de 5 s por debajo
      // del piso congelan la telemetría; dos ventanas recuperadas la
      // descongelan. La experiencia de juego manda — la telemetría es la
      // primera en pagar. r76 · el piso es 72: congela bajo 68, descongela
      // en 70+ (antes 58/60 para el suelo de 60).
      if (st.partida) {
        if (red < 68) {
          st.bajas++;
          if (st.bajas >= 2 && !st.hold) {
            st.hold = true; st.congelada++;
            try { console.info('[TELE] gobernador: telemetría congelada (fps ' + red + ' en partida en red)'); } catch { /* */ }
          }
        } else if (red >= 70) {
          st.bajas = 0;
          if (st.hold) {
            st.hold = false;
            try { console.info('[TELE] gobernador: descongelada (fps ' + red + ')'); } catch { /* */ }
          }
        }
      }
      st.frames = 0; st.fpsAcc = 0;
    }
  }

  function fpsAvg() {
    const s = st.fpsSamples.slice();
    return s.length ? Math.round(s.reduce((a, b) => a + b, 0) / s.length) : null;
  }

  /** ronda 10: mínimo/máximo DE LA SESIÓN VR (reset al entrar en VR). */
  function resetFps() { st.fpsLo = null; st.fpsHi = null; }
  function fpsLo() { return st.fpsLo; }
  function fpsHi() { return st.fpsHi; }

  /** ronda 12: LATIDO EN VR — las sesiones cerradas abruptamente (casco
   *  apagado, pestaña muerta) nunca llegan a vr_end ni a page_close y
   *  desaparecen del análisis (ronda 11 cazó una: vr_start+stage sin cierre).
   *  Un ping cada 5 min mientras dura la VR deja huella periódica: el ÚLTIMO
   *  ping fecha el fin real aunque no haya vr_end, y el fps de cada ping
   *  dibuja la curva a lo largo de la sesión (diagnóstico de caídas).
   *  Sin PII: sólo dur en segundos y fps del momento. */
  function vrPing(on) {
    try {
      if (st.vrPingT) { clearInterval(st.vrPingT); st.vrPingT = null; }
      if (on) {
        var tvr = Date.now();
        st.vrPingT = window.setInterval(function () {
          // r76 · CADENCIA ASEGURADA: el ping lleva el ESTADO DEL
          // GOBERNADOR — tasa objetivo y real del visor, perfil y
          // escalones — para ver en el panel si el casco RINDE a 72/90
          // y si una partida en red degrada la imagen.
          var perf = null;
          try {
            var pf = (typeof window !== 'undefined' && window.__PP_PERF) || null;
            if (pf && typeof pf.status === 'function') {
              var s2 = pf.status();
              perf = { tgt: s2.rate, srate: s2.sessionRate, tier: s2.tier,
                       sc: s2.scale, fv: s2.fovea, onl: st.partida ? 1 : 0 };
            }
          } catch (ePP) { perf = null; }
          var d2 = { dur: Math.round((Date.now() - tvr) / 1000), fps: fpsAvg() };
          if (perf) d2.perf = perf;
          ev('vr_ping', d2);
        }, 300000);
      }
    } catch (e) { /* entornos sin timers */ }
  }

  // arranque + cola de ciclo de vida
  // ronda 12: plataforma REAL del dispositivo (antes '2d' clavado — el casco
  // era indistinguible del escritorio en el análisis). La detección XR es
  // asíncrona (navigator.xr.isSessionSupported): el boot sale YA con la
  // estimación '2d' y, si la promesa confirma XR inmersivo antes de 1.5 s,
  // se corrige IN SITU en la cola (mismo evento: no duplica el recuento de
  // boots ni reordena la cola). Privacidad intacta: es una capability del
  // dispositivo, nunca el user-agent.
  ev('boot', { platform: '2d' });
  try {
    if (typeof navigator !== 'undefined' && navigator.xr &&
        typeof navigator.xr.isSessionSupported === 'function') {
      Promise.race([
        navigator.xr.isSessionSupported('immersive-vr'),
        new Promise(function (r) { setTimeout(function () { r(false); }, 1500); }),
      ]).then(function (si) {
        if (!si) return;
        for (var i = st.q.length - 1; i >= 0; i--) {
          if (st.q[i] && st.q[i].e === 'boot' && st.q[i].sid === st.sid &&
              st.q[i].platform === '2d') {
            st.q[i].platform = 'xr';
            persist();
            break;
          }
        }
      }).catch(function () { /* sin WebXR: escritorio */ });
    }
  } catch (e) { /* entornos sin navigator.xr */ }
  try {
    window.addEventListener('pagehide', () => {
      ev('page_close', { dur: Math.round((Date.now() - st.t0) / 1000) });
      flush(true);
    });
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') flush(true);
    });
    window.addEventListener('error', (e) => {
      ev('error', { m: String((e && e.message) || 'error').slice(0, 140) });
    });
  } catch { /* entornos sin DOM */ }
  window.setInterval(() => flush(), 30000);
  // v2.76: PRIMER ENVÍO TEMPRANO (5 s tras arrancar) — así una prueba corta
  // deja el 'boot' en el receptor sin esperar los 30 s. Inofensivo si la
  // cola está vacía (flush no hace nada) o si el receptor aún no está.
  try { window.setTimeout(() => flush(), 5000); } catch { /* */ }

  return { ev, flush, noteFrame, fpsAvg, resetFps, fpsLo, fpsHi, vrPing, partida, get on() { return st.on; }, set on(v) { st.on = !!v; persist(); }, get hold() { return st.hold; }, st };
})();
// v2.50: exposición para diagnóstico y pruebas (el módulo la usa por cierre)
try { window.__PP_TELE = __PP_TELE; } catch { /* */ }


/* =====================================================================
 *  v2.20 · BANCO DE VOZ del megáfono. Meta Quest Browser NO reproduce
 *  speechSynthesis dentro de la sesión inmersiva (en la pestaña 2D sí):
 *  la voz del marcador pasa a ser audio real, decodificado con WebAudio
 *  (la misma vía por la que ya se oyen los efectos en el visor).
 *  Clips es-ES generados con Piper TTS (modelo es_ES-davefx-medium) y
 *  comprimidos a Opus 28k mono. El juego los concatena según el plan de
 *  cada anuncio (voicePlan en game_part1.js); speechSynthesis queda
 *  como respaldo en escritorio. Regenerar: gen_voice.py + build_voice.py
 * ===================================================================== */
/* C2 (r129 · ola 3) · banco de voz EXTERNO: los clips OGG Opus ya no
 * viajan dentro del HTML (~2 MB de base64 fuera). Se descargan de
 * assets/audio/voz_*.json (el SW los cachea con cacheFirst y los ZIP los
 * llevan). Si la descarga falla (file://, red) el juego sigue — sin
 * megafonía. Al aterrizar el banco se emite 'pp-voz-lista' y GameAudio
 * recarga en caliente (reloadVoice). Regenerar: gen_voice.py + build_voice.py */
export let VOICE_B64 = null;
export let VOICE_B64_EN = null;
(() => {
  // C1 (r129) · GUARDIA DE CONTEXTO: el banco solo se descarga en la web
  // (http/https). En Node (los arneses importan esta fuente directamente)
  // un fetch relativo deja un socket colgado; en file:// fallaría igual.
  if (typeof location === 'undefined' || !/^https?:$/.test(location.protocol)) return;
  const aplicar = (lang, json) => {
    if (lang === 'es') VOICE_B64 = json; else VOICE_B64_EN = json;
    try { window.dispatchEvent(new Event('pp-voz-lista')); } catch (e) { /* */ }
  };
  const cargar = (url, lang) => fetch(url)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status))))
    .then((j) => aplicar(lang, j))
    .catch(() => { /* sin banco: megafonía en silencio, el juego sigue */ });
  cargar('assets/audio/voz_es.json', 'es');
  cargar('assets/audio/voz_en.json', 'en');
})();


