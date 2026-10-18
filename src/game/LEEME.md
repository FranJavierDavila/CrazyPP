CRAZY PING PONG · FUENTE MODULAR DEL JUEGO (fase 2 de modularización P0)
=========================================================================

QUÉ ES ESTO
  La fuente de verdad del juego ya no es un monolito de 6,3 MB: es ESTA
  carpeta. public/game.html es un ARTEFACTO GENERADO que debe coincidir
  byte a byte con lo que produce el ensamblador.

  Desde la FASE 2, los 14 subsistemas de core/ son MÓDULOS ES REALES:
  tienen import/export explícitos y el grafo de dependencias está
  verificado por AST (scripts/mod_fase2_analizar.mjs, acorn). El
  ensamblador aplica la transformación INVERSA («build de inserción»):
  quita los bloques de import generados y los prefijos export, de modo
  que game.html sale BYTE-EXACTO con el único ámbito compartido de
  siempre. Ejecución real: cero cambios.

ESTRUCTURA
  00_head.html          doctype + <head> + todo el CSS (<style>)
  01_vendor.html        <script src="/vendor/socket.io.min.js">
  02_importmap.html     el import map de three.js y addons
  03_body.html          marcado de la portada (cover, HUD 2D, paneles)
  04_boot.html          script pequeño previo al módulo
  05_module_open.html   apertura <script type="module">
  core/c00_pre_three.js      utilidades previas a THREE: i18n (T/setLang),
                             nombre de jugador, ranking mundial, iconos,
                             telemetría __PP_TELE, voces base64
  core/c01_modelos_3d.js     import REAL de THREE + modelos GLB en base64
                             (pala, pistola) y su montaje
  core/c02_cfg_escena.js     DIMS (dimensiones/gravedad), presets de IA,
                             asistencia de saque, colores, temas de sala
  core/c03_audio_voz.js      VOICE_*, plan de números y clase GameAudio
  core/c04_fisica_ccd.js     substeps, CCD_TUNE, SDF de hoja/cápsula,
                             barridos, simulador de pala, aerodinámica,
                             botes, PERKS de pala
  core/c05_colisiones_ia_golpeo.js  collidePaddle(+Sweep), mesa/red/mundo,
                             stepPhysics y el SOLVER de la IA de golpeo
  core/c06_logros_stats_ia_rival.js ACHIEVEMENTS, GameStats, gauss,
                             clase OpponentAI
  core/c07_escena_sala.js    createRoom/Table/Ball/BlobShadow/ChampDecor
  core/c08_hall_hud.js       skins del Hall, createHall, sala de campeonato,
                             marcadores, calibración, fanfarria, confeti
  core/c09_red_netlink.js    clase NetLink (P2P WebRTC multijugador)
  core/c10_menu_saque.js     logo base64 del menú y constantes de saque
  core/c11_champloader.js    clase ChampLoader + skin de normas
  core/c12_pingponggame.js   clase PingPongGame (el orquestador, ~5.100
                             líneas — importa de 13 ficheros, 96 símbolos)
  core/c13_ui_arranque.js    UI de portada, calibración y arranque
  06_module_close.html  cierre </script>
  07_tail.html          scripts finales (sellos EN VIVO, poses, etc.)
  GOLDEN_SHA256.txt     SHA256 del game.html producido por la división
  DEPS.json             grafo de dependencias (máquina)
  DEPENDENCIAS.md       grafo de dependencias (humano) + candidatos SDK

  Dentro de cada pieza core/ hay un bloque marcado:
    /* DEPS-FASE2-INICIO (generado …) */ import …; /* DEPS-FASE2-FIN */
  — NO editar a mano: se regenera con el generador. Los prefijos
  `export ` en columna 0 también están RESERVADOS al generador.

CÓMO SE EDITA (EL ÚNICO CAMINO LEGÍTIMO)
  1. Edita el subsistema que toque en src/game/core/ (o el wrapper HTML/CSS).
  2. Si usaste símbolos de OTRO subsistema (o creaste símbolos que otros
     deban usar), regenera el grafo y los bloques:
        node scripts/mod_fase2_analizar.mjs   # informe + DEPS.json + DEPENDENCIAS.md
        node scripts/mod_fase2_generar.mjs    # reescribe bloques/exports
  3. Regenera el juego:   python3 scripts/build_game.py --escribir
  4. El script compara con GOLDEN_SHA256.txt:
       · BYTE-EXACTO → no tocaste nada de código (o solo comentarios).
       · DIFIERE     → cambio legítimo: sube versión, QA, release.
  5. Nunca edites public/game.html a mano: el ensamblador lo detecta
     («DIFIERE de lo ensamblado») y el siguiente build lo machacaría.

GARANTÍAS DEL ENSAMBLADOR (scripts/build_game.py)
  · Orden fijo de piezas: un fichero nuevo en core/ NO entra solo — hay
    que registrarlo en ORDER (a propósito: el orden es semántico).
  · Token de identidad en la 1.ª línea de cada pieza: si un trozo se
    corrompe o se reordena, el build FALLA con el trozo culpable.
  · Transformación de inserción verificada: tras quitar bloques/exports,
    el ensamblado NO DEBE contener restos (guardas anti-fugas duras).
  · Sin --escribir es un ensayo: no toca public/.

GARANTÍAS DEL GENERADOR (scripts/mod_fase2_generar.mjs)
  · Analiza SIEMPRE la fuente pura (bloques generados fuera) → grafo
    estable e idempotente: re-ejecutar produce ficheros byte-idénticos.
  · Jamás emite self-imports (aserción dura) ni imports de símbolos
    duplicados o reasignados (los imports de ESM no son reasignables).
  · Inserta el bloque tras el PRIMER statement (los tokens de identidad
    de la 1.ª línea quedan intactos).

LIMITACIONES DOCUMENTADAS (DEPENDENCIAS.md las detalla)
  · Un símbolo reasignado desde otro fichero (hoy: T en c06) no se
    importa — sigue viviendo en el ámbito compartido del ensamblado.
  · La ejecución real sigue siendo el ensamblado en un solo ámbito; los
    módulos son la fuente con dependencias explícitas, listos para un
    futuro bundler o para la Fase 3.

DIVISIÓN ORIGINAL
  scripts/divide_game.py troceó game.html v3.6.0-SUP1 (sha256 de109e09…)
  con cortes validados por token y recomposición byte-exacta.

FASES COMPLETADAS (plan P0 acordado con el dueño)
  · Fase 1: división BYTE-EXACTA del monolito en esta carpeta
    (scripts/divide_game.py) + ensamblador con identidad.
  · Fase 2: los 14 subsistemas de core/ son MÓDULOS ES REALES (grafo
    verificado por AST; build de inserción inversa).
  · Fase 3 (V3.6.1-SDK1): SDK DE CAMPEONATOS —
    public/championships/sdk/champ_sdk.js v1.0.0 con el kernel que los
    5 campeonatos reimplementaban (SFX canónico con la lección v2.125,
    congela()/descongela() del patrón locura v2.40, getCore, assetURL).
    El orbital estrena la adopción (manifest v14) y los ZIPs llevan el
    SDK dentro de championships/sdk/.
  · Fase 4 (V3.6.2-SDK2): el SDK v1.1.0 (precarga() + opts.pan) lo
    usan LOS 5 campeonatos — oeste (4 motores SFX one-shot + 3
    congelados + puente; manifest v49), magia (risa del mago +
    congelado + puente; v29), locura (el congelado patrón v2.40 que
    nació ahí + puente; v21) y valle_neon (puente; v2). Conducta
    idéntica: volúmenes, anti-spam y paneo intactos.
  · Fase 5 (V3.6.3-SDK3): el SDK v1.2.0 estrena createMusic() — los
    tres motores de MÚSICA en bucle que seguían duplicados (BSO del
    saloon v2.78+v2.124 y música del vagón v2.111 en el Oeste, BSO de
    Magia v30, WAV de Valle Neón v3) convergen en UNA máquina de
    estados con variantes por opciones y conducta idéntica: fundidos,
    sincronía en vivo con el ajuste global, UNA MELODÍA, resurrección
    de contexto (v2.124) y parada instantánea o con fundido. El fix
    v2.125 del decodeAudioData ya vive UNA sola vez también para la
    música (ningún módulo conserva decodeAudioData propio).
  · Fase 6 (V3.6.4-SDK4): el SDK v1.3.0 estrena createPowerSign() — el
    CARTEL DE SUPERPODER de los 4 campeonatos con duelos (Forajido/
    Wizard/Arcade/PwSignEO) vive en UNA fábrica con DOS coreografías
    exactas («clasica» v2.120 y «v240» con el halo que respira) y knobs
    por módulo (arte, respaldo pintado, ownTex, dims). El anclado a la
    red (v2.88) y el icono del poder (v2.120) son comunes; el dispose
    de la regla Quest pasa a los cuatro (oeste v51 · magia v31 ·
    locura v22 · orbital v15).
PRÓXIMA FASE
  · SDK v1.x: Rival/HUD compartidos (el standee del rival y el
    marcador de etapa siguen duplicados entre módulos) y el SFX de
    arsenal del orbital (su decodeAudioData propio). Los «candidatos
    SDK» de DEPENDENCIAS.md marcan el camino en el núcleo.
  · Cada fase conserva la cadena de release: game.html sigue siendo
    un único fichero autocontenido para los ZIPs.
