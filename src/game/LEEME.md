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

PRÓXIMA FASE (plan P0 acordado con el dueño)
  · Fase 3: SDK de campeonato (Sala6/Rival/HUD/Sfx/FreezeClock compartidos)
    para que los 5 campeonatos dejen de reimplementar lo mismo. Los
    «candidatos SDK» de DEPENDENCIAS.md marcan el camino en el núcleo.
  · Cada fase conserva la cadena de release intacta: game.html sigue
    siendo un único fichero autocontenido para los ZIPs.
