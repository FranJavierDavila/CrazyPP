---
Task ID: 1
Agent: Super Z (main agent)
Task: Crear videojuego de ping pong WebXR inmersivo para Meta Quest 3 (Type 3: desarrollo web interactivo)

Work Log:
- Inicializado entorno fullstack Next.js 16 (script init-fullstack.sh)
- Instalado three@0.186 + @types/three
- Creado motor del juego en src/lib/game/:
  - constants.ts: dimensiones ITTF reales (mesa 2.74×1.525m, red 15.25cm), presets de IA
  - audio.ts: sonido sintetizado con Web Audio (pala, mesa, red, puntos) con paneo estéreo
  - scene-builder.ts: sala, mesa reglamentaria con líneas, red con textura, palas (goma roja/negra), bola con estela, marcador con CanvasTexture
  - physics.ts: integración semi-implícita con sub-pasos fijos (1/240s), colisión barrida pala-bola (transfiere velocidad real del mando), rebotes mesa/red/suelo/paredes, simulador de interceptación y calculador de tiros parabólicos
  - rules.ts: árbitro simplificado (partido a 11, ventaja 2, saques alternos cada 2 puntos, saque fallado se repite)
  - ai.ts: IA con predicción de trayectoria, movimiento con velocidad máxima, errores y fallos según dificultad
  - game.ts: orquestador WebXR (immersive-vr, local-floor), tracking de grip spaces de mandos Quest 3, háptica (pulse), recentrado automático de orientación al entrar en VR, modo demostración IA vs IA en escritorio
- UI: src/components/ping-pong-canvas.tsx (HUD, botón Entrar en VR, selector de dificultad, instrucciones) + page.tsx + layout.tsx en español
- Bugs corregidos durante verificación:
  1. Faltaba renderer.render() en el bucle de animación
  2. Vectores temporales compartidos en collidePaddle (posición previa de la bola incorrecta)
  3. Objetivos de saque/golpe de IA fuera de la mesa (la mesa completa está en Z negativa) que causaban bucle infinito de saques fallados
  4. Typo en color hexadecimal del grid

Stage Summary:
- Juego WebXR completo y funcional, verificado con agent-browser: render 3D OK (56 draw calls), ciclo rally→punto→saque funcional, marcador 2:1 en vivo, dificultad cambiable en tiempo real, sin errores de consola, ESLint limpio
- El modo escritorio muestra demo IA vs IA; en Quest 3 el botón "Entrar en VR" inicia sesión inmersiva con tracking 1:1 y vibración
- Requiere HTTPS + Meta Quest Browser (WebXR); verificado el estado deshabilitado del botón en navegadores sin soporte

---
Task ID: 2
Agent: Super Z (main agent)
Task: Portar el juego WebXR de ping pong (sesión anterior, Next.js) a un único archivo HTML autónomo listo para Netlify Drop + Meta Quest 3

Work Log:
- Leído worklog.md: se recuperó el motor ya depurado de la sesión anterior (src/lib/game/*.ts)
- Portado 1:1 a JavaScript plano en /home/z/my-project/download/pingpong-quest3/index.html (~1.680 líneas, Three.js 0.170 vía importmap CDN):
  - constants (DIMS ITTF, AI_PRESETS, COLORS, MOUNT_QUAT), audio (GameAudio sintetizado), physics (sub-pasos 1/240s, colisión barrida, simulateIntercept, computeShotVelocity), rules (árbitro a 11 con ventaja 2 y saque repetido), ai (OpponentAI), scene-builder (sala, mesa, red, palas, bola con estela, marcador canvas), game (orquestador XR: recenter 25 frames, grips, háptica, saque con velocidad del mando, cámara órbita demo)
  - UI propia en DOM: overlay glass con instrucciones en español, selector de dificultad (Fácil/Media/Difícil), botón ENTRAR EN VR personalizado, botón modo espectador y HUD inferior con marcador
- Bug corregido durante la verificación: el canvas fijo tapaba los clics del HUD en pruebas headless -> añadido pointer-events:none a #c (el canvas no necesita eventos: el input XR viene de los mandos)
- Verificación con agent-browser: sintaxis JS validada con node --check; página sin errores de consola; modo demo juega IA vs IA (marcador progresó 2:0 -> 2:1 -> 2:2 con rallies reales); dificultad cambiable en caliente (hard/easy verificados); 42 draw calls; captura guardada en download/pingpong-demo-captura.png
- Empaquetado: download/pingpong-quest3.zip (carpeta con index.html, 57 KB) lista para arrastrar a Netlify Drop

Stage Summary:
- Entregable: /home/z/my-project/download/pingpong-quest3/index.html (+ .zip) — juego completo en un solo archivo, sin build ni dependencias locales (solo CDN de three.js)
- Flujo usuario: arrastrar carpeta/zip a Netlify Drop -> abrir URL HTTPS en Meta Quest Browser -> ENTRAR EN VR -> jugar con mandos (gatillo saca, pala anclada al mando, vibración en impactos)
- Sin visor: modo espectador IA vs IA con cámara orbital y HUD
- Verificado en headless: cero errores, física/reglas/IA/scoring operativos

---
Task ID: 3
Agent: Super Z (main agent)
Task: El usuario no veía las nuevas palas GLB en el preview — integrar el juego v2 terminado en la raíz del preview

Work Log:
- Diagnóstico: el preview (Caddy -> next dev :3000) servía la app Next.js antigua (palas procedurales), mientras que el juego v2 con pala GLB solo existía como HTML autónomo en download/pingpong-quest3-v2/index.html
- Verificado el v2: GLTFLoader + GLB del usuario incrustado en base64 (1.5 MB), sintaxis JS OK (node --check)
- Integración: copiado a public/game.html y añadida rewrite en next.config.ts (beforeFiles: "/" -> "/game.html"); next dev la aplicó en caliente
- Verificación con agent-browser: raíz HTTP 200 sirve el v2 (1.506.717 B); demo IA vs IA jugando (marcador 0:0 -> 1:0 -> 2:2), mensajes de saque/bote/punto en vivo; ambas palas son el GLB (goma roja vista de frente, madera vista por detrás); cero errores de consola
- Actualizado download/README.md (v2: pala GLB incrustada, saque con mano libre, regla de dos botes, LET, faltas) y creado download/pingpong-quest3-v2.zip (solo index.html, 820 KB)

Stage Summary:
- El preview en la raíz ahora muestra el juego v2 completo (pala GLB real, saque con mano libre y física, regla ITTF de dos botes, LET, rival con cuerpo)
- Entregable Netlify Drop sin cambios: download/pingpong-quest3-v2/index.html (autocontenido) o .zip

---
Task ID: 4
Agent: Super Z (main agent)
Task: Eliminar los cuerpos de los avatares — el usuario quiere solo las palas ("los cuerpos molestan")

Work Log:
- Localizado createOpponent() en scripts/game_part2.js (torso, caderas, piernas, zapatos, cabeza, pelo, brazo procedural) y sus usos en scripts/game_part3.js (creación de aiAvatar/demoAvatar, llamadas a updateAvatar en el bucle y el método updateAvatar)
- Verificado que las palas de IA/demo son independientes de los cuerpos (se posicionan directamente desde ai.pos/demoAI.pos), así que quitar los cuerpos no afecta a la IA, el saque ni las colisiones
- Eliminado: función createOpponent completa, bloques de creación de avatares en buildScene, llamadas updateAvatar + método updateAvatar
- Reconstruido index.html con build_html.py (sintaxis OK, 1.50 MB, GLB incrustado intacto); sin referencias colgantes (rg limpia)
- Desplegado a public/game.html; verificado en agent-browser: escena sin cuerpos, las dos palas GLB flotantes visibles y siguiendo la IA, rally vivo (1:0), cero errores de consola; captura scripts/preview_v3_nobody.png
- Actualizados download/pingpong-quest3-v2.zip y download/README.md (nueva viñeta "Solo palas, sin cuerpos")

Stage Summary:
- El preview (raíz) y el entregable Netlify Drop muestran ahora solo las palas: la del rival la mueve la IA, sin avatar humanoide
- Física, reglas ITTF, saque con mano libre y marcador sin cambios

---
Task ID: 5
Agent: Super Z (main agent)
Task: Dotar al juego de la mayor precisión y calidad posible

Work Log:
- FÍSICA: arrastre lineal (0.12) sustituido por aerodinámica real de bola ITTF (40 mm/2,7 g): arrastre cuadrático a = k·|v|·v con k=0.142 (½·ρ·Cd·A/m, ρ=1.225, Cd=0.5) + Magnus; nueva función applyAerodynamics() usada por stepPhysics, predictStrike y simulateServePath (una sola ecuación para física real y simuladores de IA); sub-pasos 240 Hz -> 480 Hz (cap 96); h de predictores 1/120 -> 1/240; maxBallSpeed 12->14, spinMax 90->110, spinImpulse 9->10, cooldown 0.14->0.10
- TRACKING: nueva updatePaddleSim(): velocidad del mando por media móvil en ventana de 70 ms (estable ante jitter) y velocidad angular (rad/s) por delta de cuaterniones; el efecto del golpe ahora usa la velocidad de superficie (lineal + ω×r de la muñeca, paddleWristSpin 0.16); reset completo al cambiar de mano
- CALIDAD VR: renderer.xr.setFoveation(0) + setFramebufferScaleFactor(1.7) (nitidez en toda la lente), outputColorSpace SRGB, exposición 1.05, environmentIntensity 0.5->0.75, sombras 1024->2048, bola 24x16 -> 48x32 segmentos
- Verificación agent-browser: sin errores de consola; demo IA vs IA progresa en ambos sentidos (1:0 -> 2:0 -> 2:1) con saques válidos y faltas naturales; el solver de saque (findServeVelocity) se adapta a la nueva aerodinámica; captura scripts/preview_v4_quality.png
- Reconstruido index.html (1.51 MB), desplegado en public/game.html (preview raíz) y reempaquetado download/pingpong-quest3-v2.zip; README actualizado

Stage Summary:
- Física de nivel simulador: aerodinámica ITTF real compartida por física y IA, integración 480 Hz, tracking de mandos con ventana móvil + efecto de muñeca, nitidez máxima en el visor
- Reglas/saque/palas GLB sin cambios; todo verificado sin errores

---
Task ID: 6
Agent: Super Z (main agent)
Task: Actualizar la descarga (petición literal del usuario: "actualiza la descarga")

Work Log:
- Verificado que el código fuente (game_part1/2/3.js) contiene las mejoras de precisión/calidad de Task 5 (applyAerodynamics k=0.142, sub-pasos 1/480, setFoveation(0), setFramebufferScaleFactor(1.7))
- Reconstrucción determinista con build_html.py: sintaxis OK, index.html 1.51 MB
- Diff contra el index.html del zip existente: IDÉNTICO (la descarga ya estaba sincronizada con la última build)
- Redesplegado a public/game.html (preview raíz) y verificado con agent-browser: cero errores de consola, demo IA vs IA activa, marcador 1:0 con mensaje "doble bote: la CPU no llegó"
- Reempaquetado download/pingpong-quest3-v2.zip (solo index.html, 818 KB) y captura scripts/download_final_check.png

Stage Summary:
- Descarga confirmada al día: download/pingpong-quest3-v2/index.html (+ .zip) = última versión con física aerodinámica ITTF, 480 Hz, tracking con ventana móvil y nitidez VR máxima
- Preview funcionando sin errores

---
Task ID: 7
Agent: Super Z (main agent)
Task: Corregir pala (caras invertidas, agarre antinatural) y facilitar el golpeo (feedback del usuario)

Work Log:
- DOBLE CARA: loadPaddleModel ahora fuerza m.side = THREE.DoubleSide + needsUpdate en TODOS los materiales del GLB (y en la pala procedural de respaldo); elimina el problema de caras invertidas del modelo
- MONTURA NATURAL: MOUNT_QUAT (hoja hacia +Y_grip, perpendicular al mango = "bandera") sustituido por montura alineada con el mango: RotX(-90°) lleva la hoja a -Z_grip (sale por la parte alta del mando siguiendo el mango) + roll ±(90°-0.12) para cara casi vertical, espejo por mano (MOUNT_QUAT_RIGHT/LEFT + mountQuatFor); handOf[i] se fija en 'connected' con e.data.handedness; mount.position (0,0.012,0.02) -> (0,0,0) para que colisionador y visual coincidan exactamente (el punto de agarre de la pala = origen del grip)
- GOLPEO ASISTIDO: hitAssistRadius 0.024 (radio de impacto = hoja+bola+2,4 cm), grosor del plano de contacto 12->22 mm, zona del mango más amplia, cooldown 0.10->0.08, serveAssistVy 1.9->2.3 (toss más alto = más tiempo), validación "al caer" preVy 0.05->0.3 (margen ±30 ms alrededor del punto muerto), timeout de toss 6->8 s
- IA más amable en easy (maxShotSpeed 5.5->4.8, errStd 0.11, missBase 0.22) y medium (maxShotSpeed 7.5->6.2, errStd 0.06, missBase 0.11)
- Overlay: nota "Zona de impacto asistida: no hace falta milimetrar"
- Rebuild (sintaxis OK, 1.51 MB), desplegado a public/game.html, verificado con agent-browser: cero errores de consola, demo IA vs IA progresa (1:0), palas GLB visibles por ambos lados; captura scripts/preview_v5_fixes.png
- Reempaquetado download/pingpong-quest3-v2.zip y actualizado README (secciones v2.1)

Stage Summary:
- Pala sin caras invertidas (doble cara) y montada de forma natural: agarre del mando = agarre de la pala, hoja siguiendo el mango, montura espejo por mano
- Golpeo y saque claramente más accesibles (hitbox ampliada, toss alto, validación permisiva) manteniendo la física realista
- Descarga y preview actualizados y verificados sin errores

---
Task ID: 8
Agent: Super Z (main agent)
Task: Normales del GLB, agarres configurables con entrenamiento, sonido en VR y golpeo aún más fácil

Work Log:
- NORMALES GLB: nueva fixInvertedMeshes(root) en loadPaddleModel — calcula el volumen firmado de cada malla y si es negativo (interior-exterior) invierte el winding (index o no-indexado) y niega las normales; shadowSide = DoubleSide en los materiales; consola informa "N malla(s) corregida(s)". La pala se ve bien sin problemas de normales en cara y contorno
- AGARRES CONFIGURABLES: sistema de presets {px,py,pz,rx,ry,rz} sobre la montura natural, persistidos en localStorage (ppxr_grips_v1); UI en el overlay (nombre + select Cargar/Guardar/Borrar/Natural) y métodos saveCurrentGrip/loadGripByName/deleteGripByName/resetGripNatural; sync overlay<->VR vía callback onGrips
- MODO ENTRENAMIENTO (VR): botón "ENTRENAR GOLPES EN VR · ajustar pala" (entra en VR directo al modo) o pulsar Y en cualquier momento; panel 3D (createCalibPanel, CanvasTexture 512², se redibuja solo si hay cambios) con nombre del agarre, valores y controles; sticks: derecha gira/inclina la cara, izquierda mueve, +GRIP rueda/acercar; A guarda, B carga siguiente, X reset natural, gatillo lanza bola; MÁQUINA DE BOLAS: findServeVelocity alimenta saques reglamentarios (dos botes) cuando la bola está muerta o por tiempo; sin marcador (reglas en pausa); Y sale al partido
- SONIDO EN VR: GameAudio.kick() (ensure + resume) llamado en CADA reproducción; en sessionstart kick + reintentos 400/1200/2500 ms + blip de confirmación a 350 ms; corrige el contexto suspendido de Quest Browser
- GOLPEO MÁS FÁCIL: hitAssistRadius 0.024->0.038 (radio de detección ≈13,8 cm), plano de contacto 22->30 mm, mango 45x200 mm
- Overlay: sección AGARRES DE PALA + botón ENTRENAR + instrucción Y del modo entrenamiento
- Rebuild (1.53 MB, sintaxis OK), desplegado a public/game.html; verificado con agent-browser: cero errores, demo 1:0, agarres guardar/cargar/borrar OK (offsets restaurados exactos), panel renderiza, máquina de bolas lanza saque válido (3,3 m/s); captura scripts/preview_v6_grips.png
- Reempaquetado download/pingpong-quest3-v2.zip

Stage Summary:
- Pala corregida a nivel geometría (normales/winding) + doble cara: sin artefactos
- Sistema completo de agarres con nombre (persistente) + modo entrenamiento con máquina de bolas y panel de ajuste en VR
- Audio reforzado para VR (kick+reintentos) y detección de golpeo mucho más generosa

---
Task ID: 9
Agent: Super Z (main agent)
Task: Saque IA realista, golpeos sólidos, saque natural fácil y sonido estable en VR (feedback del usuario)

Work Log:
- SAQUE IA (posición ilógica + canto): causa raíz = aiPaddleMesh.lookAt(ball.pos) con la bola justo encima (caso degenerado de lookAt -> volteo/canto) y bola anclada a ai.pos (donde la pillara el punto). Nuevo sistema: setupAIServe/setupDemoServe fijan spot reglamentario (0,3 m tras la línea de fondo, x aleatoria ±0,2 m) y postura lateral; la IA camina al stance (holdTarget en OpponentAI.update), sostiene la bola y lanza tras llegar (o a los 3 s); updateAIPaddlePose sustituye a lookAt: euler con yaw limitado (±66° hacia el rival) y pitch acotado; animación de saque completa (postura cara abierta -> swing p^1.7 siguiendo la bola -> instante de impacto con cara cerrada, flash 0,22 s); demoPaddleMesh oculto en VR (era una pala fantasma tras el jugador)
- GOLPEOS SÓLIDOS: transferencia de velocidad pala->bola (+0,22·v_pala en la dirección de salida), restitución 0,78->0,85, velocidad mínima de salida 1,5->2,3 (DIMS.minExitSpeed), y en rally los golpes del jugador que salen hacia atrás o sin fuerza (vz>0,5 o |v|<2,2) se enderezan 40-60% hacia el campo rival con computeShotVelocity
- SAQUE NATURAL FÁCIL: ventana de validación ±30 ms -> preVy<=0,6 (punto muerto ±60 ms y toda la caída), pitido GameAudio.tick() + vibración + destello de la bola en el punto muerto (apexSignaled/apexPulse), margen extra de detección solo en saque (pad.extraReach=serveExtraReach 0,06; plano de contacto +45 mm), tolerancia de línea de fondo 4->10 cm, toss asistido 2,3->2,6 m/s, y SOLIDEZ por simulación: tras el golpe válido, simulateServePath valida; si falla, se mezcla 65% con findServeVelocity (y si aún falla, trayectoria completa) -> el saque siempre cumple el doble bote conservando parte del toque
- SONIDO VR: confirmado en headless el contexto suspendido; watchdog(dt) cada 0,7 s reanuda el contexto y, si tras 5 intentos no responde, cierra y RECONSTRUYE el AudioContext (master 0,9 + DynamicsCompressor -16/5:1), más visibilitychange->resume; verificado por consola "Audio: contexto reconstruido tras quedar suspendido"
- Overlay: instrucciones actualizadas (pitido del punto muerto, zona extra en saque)
- Rebuild (1,54 MB, sintaxis OK), desplegado a public/game.html; verificado con agent-browser: cero errores; monitor de saques: spot IA (0,01,1,02,-3,27) reglamentario, bola clavada al spot, quaternion de pose {x:-0.25,0,0,w:0.97} (cara abierta, sin canto); swing registrado de backswing (1,17/-3,39, qw=0.92) a contacto siguiendo la bola (qw=1); demo 5:5 y 2:1 en ciclos largos; capturas scripts/preview_v7_swing.png y preview_v7_final.png
- Reempaquetado download/pingpong-quest3-v2.zip (1,53 MB, solo index.html) y README con secciones v2.3

Stage Summary:
- La CPU saca desde una posición reglamentaria con animación natural (postura lateral, toss, swing, cara cerrada en el impacto): sin canto ni posiciones raras
- Golpeos con cuerpo: la velocidad de la mano se transfiere a la bola, salida mínima mayor y los golpes muertos se enderezan; el saque es casi imposible de fallar tras el lanzamiento (pitido + vibración + trayectoria garantizada por simulación)
- El audio ya no desaparece en VR: watchdog que reanuda y reconstruye el contexto + compresor y más volumen
- Descarga y preview actualizados y verificados sin errores

---
Task ID: 10
Agent: Super Z (main agent)
Task: Vibración háptica del mando al golpear la pelota (petición del usuario)

Work Log:
- Diagnóstico: ya existían llamadas haptic() en golpeos/toss/mesa/puntos, pero usaban el XRInputSource cacheado del evento 'connected'; en Quest Browser ese gamepad se re-crea (hand tracking, cambios de modo) y hapticActuators queda obsoleto/inexistente -> no se sentía nada
- haptic(index, strength, ms) reescrito: resuelve el mando EN VIVO desde renderer.xr.getSession().inputSources por handedness (fallback a la caché) y prueba en cadena pulse(intensity,ms) -> playEffect('dual-rumble') -> vibrationActuator.playEffect; saturación 0.2-1 y return boolean
- hapticProbe() en sessionstart (+700 ms): pulso de prueba de 120 ms en cada mando con actuador (se SIENTE al entrar en VR) + log [Haptics] por mando con disponibilidad
- Intensidades: golpeo de pala = 0.5 + velocidad/9 (mínimo perceptible 0.63, saque 0.8/90 ms, punto ganado 0.85/110 ms); los golpeos de la IA (paddleIndex -1) no vibran
- Verificación headless con actuadores simulados: rutas pulse/playEffect/vibrationActuator OK, sin actuador devuelve false sin excepción, clamp OK; demo IA vs IA progresa (1:0), evento de golpeo simulado del jugador dispara haptic(0,1,70)/(0,0.63,70) y el de la IA no vibra; cero errores de consola; captura scripts/preview_v8_haptics.png
- Rebuild 1.54 MB (sintaxis OK), desplegado a public/game.html y reempaquetado download/pingpong-quest3-v2.zip; README con sección v2.4

Stage Summary:
- Vibración háptica fiable y proporcional en cada golpeo del jugador, con autotest al entrar en VR
- Descarga y preview actualizados y verificados sin errores

---
Task ID: 11
Agent: Super Z (main agent)
Task: Las palas no deben atravesar la mesa (ni red ni suelo) - feedback de inmersión

Work Log:
- Causa: la pala del jugador sigue al mando sin restricciones (el mando puede bajar de la superficie dentro de la huella de la mesa) y la pala IA/demo seguía la bola sin límite vertical
- Nuevo clampPaddlePose(pos, q, fromGrip) en game_part3: geometría exacta de pala (hoja = disco fino R=79,5 mm + mango; punto más bajo = centro_y - R·sqrt(1-n_y²) - halfT·|n_y|, más el mango como cilindro), con dos modos de ancla: mango (jugador, incluye offset de calibración) y centro de hoja (IA/demo)
- Resolución: 1) losa de mesa por mínima penetración (empuja arriba a superficie+4 mm o deja pasar por debajo si venía de abajo; con la mano bajo la mesa se mueve LIBRE, sin saltos); 2) red como losa vertical (empuja al lado del ancla, no del centro de hoja - corregido tras test); 3) suelo a +15 mm
- Integración: jugador = clamp de grip.position ANTES de updatePaddleSim (física y visual sincronizados, la montura es hija del grip); IA/demo = clamp en las 4 salidas de updateAIPaddlePose (swing, impacto, preparación, rally)
- Correcciones durante verificación: (a) en modo IA el ancla ya es el centro de hoja (no sumar mango->hoja D=0,1303); (b) signo del empuje de red basado en el ancla
- Verificación headless: 8 tests geométricos OK (solape desde arriba +8 mm exactos, mano bajo mesa libre, red empuja al lado correcto -1,3828, suelo +15 mm, IA hundida sube hasta apoyar mango, fuera de huella intacto, idempotente, cara plana IA a superficie+espesor); demo 1:0, palas a y=1,05 sobre la mesa, cero errores; captura scripts/preview_v9_noclip.png
- Rebuild 1.54 MB (sintaxis OK), preview actualizado, zip reempaquetado (checksum OK), README sección v2.5

Stage Summary:
- Pala jugador/IA/demo ya no penetra mesa, red ni suelo; resolución por mínima penetración sin teletransportes (mano bajo la mesa libre)
- Física y visual de la pala permanecen alineados; descarga y preview verificados sin errores

---
Task ID: 12
Agent: Super Z (main agent)
Task: Sin sonido en VR (con palas), CPU juega muy corto y háptica sin probar

Work Log:
- AUDIO VR: identificado el agujero de gesto de usuario: el contexto se creaba/reanudaba en la demo 2D (toques en el menú), pero dentro de la sesión XR resume() sin activación falla y el watchdog reconstruía un contexto que nacía suspendido. Fix triple: (1) enterVR llama audio.rebuildFresh() DENTRO del clic (contexto nuevo nace running); (2) selectstart/squeezestart/inputsourceschange de la SESIÓN XR y onSqueezeStart de los mandos llaman audio.kick() (los eventos de input XR son intención del usuario -> resume funciona); (3) se mantiene el watchdog
- CPU EN LARGO: hallazgo clave midiendo la física: con bote propio profundo y vuelo balístico lento (T 0.5-0.84 s) el bote rival caía a solo 0,13 m de la red (drag aerodinámico acorta) -> varios botes en la mesa del receptor. findServeVelocity rediseñado: barre multiplicadores de velocidad (1.0-1.75) sobre la solución balística con bote propio profundo (0.62-0.85); el bote rival cae ahora en la mitad profunda (mediana 0,83-0,86 m de 1,37 = ~61%, antes 0,13); velocidad media 4,5 m/s
- ANTI-LET: la colisión real de red usa el centro de la bola (netTopY + ballRadius); la simulación usaba solo netTopY -> margen de 12 mm < radio 20 mm = LETs casi seguros en física real (bucle de LET detectado en demo). simulateServePath ahora replica la banda real y findServeVelocity exige despeje >= netTop + R + 6 mm; además registra netY (altura al cruzar)
- RALLY EN LARGO: depthRel de fondo 0.62-1.12 (antes 0.55-1.20 con cortas 0.25-0.50); short en presets: easy 0.06->0.03, medium 0.10->0.05, hard 0.12->0.06
- Gancho de depuración permanente window.__ppDebug = { findServeVelocity, simulateServePath, DIMS }
- Verificación: 40/40 saques válidos (mediana 0,83, todos >= 0,68 de profundidad, despeje mínimo 2,3 cm); demo larga sin bucles de LET (1:0 -> 2:0, mensajes correctos), cero errores de consola; audio headless queda 'suspended' (sin gesto ni dispositivo: esperado en pruebas; en el clic real nace running)
- Rebuild 1,55 MB (sintaxis OK), preview desplegado, zip reempaquetado (checksum OK), README secciones v2.6

Stage Summary:
- Audio: contexto nuevo dentro del gesto de entrada + reactivación con gatillo/grip en sesión = cadena completa de gestos para VR
- CPU saca y juega en largo con margen anti-LET real; adiós a los saques que mueren botando
- Descarga y preview actualizados y verificados sin errores

---
Task ID: 13
Agent: Super Z (main agent)
Task: Sonido completamente muerto, panel de entrenamiento sobre la mesa y fanfarria de fin de partido

Work Log:
- AUDIO MUERTO (causa raíz encontrada y reparada): (1) GameAudio.ensure() no reparaba contextos en estado 'closed'/'failed' - hacía resume() (que falla en silencio) y NUNCA recreaba: silencio permanente tras cualquier close() (el rebuildFresh de v2.6 podía dejar el sistema en ese estado); (2) kick() solo hacía resume(): si el contexto quedaba "zombie" (resume promete pero no arranca), ningún gesto lo recuperaba; (3) rebuildFresh() en enterVR destruía un contexto SANO antes de entrar en XR (contraproducente en Quest)
- GameAudio v3 (defensa en profundidad): ensure() recrea ante 'closed'/'failed'; _rebuild(reason) con throttle 1,2 s (cierra -> recrea grafo completo: master+compresor+noiseBuffer); kick() ahora RECREA el contexto si tras resume() sigue sin running y hubo gesto (los gatillos XR son gestos: el contexto nuevo nace 'running'); prepareVR() en enterVR repara enfermos SIN destruir sanos; watchdog() reconstruye tras 5 fallos con hadGesture; gesto global pointerdown/click en document (hadGesture + kick) reactiva el audio con cualquier toque del menú 2D; playOsc/playNoise/panNode blindados: Number.isFinite en TODOS los parámetros (NaN lanzaba TypeError y mataba el frame entero) + try/catch total (el audio NUNCA rompe el bucle); logs [Audio] (estado al crear/reconstruir y al entrar en VR)
- FANFARRIA DE FIN DE PARTIDO: GameAudio.fanfare(win) - victoria: arpegio mayor C5-E5-G5 + acorde final C6 con capa de octava y platillo (highpass noise); derrota: "trombón triste" de 5 notas descendentes con bend -7% y lowpass 900 Hz; Rules: mensaje final festivo con marcador ("¡VICTORIA! · 11-4 · gatillo: revancha"); banner 3D createFanfareBanner (1,6x0,8 m sobre la red a y=1,78, CanvasTexture 1024x512: título con sombra, coronas o Zzz dibujados con paths, confeti estático, marcador final y subtítulo) con animación de entrada elástica + pulso + vaivén, visible durante todo el estado 'over'; confeti 3D createConfetti (120 partículas vertexColors con caída+vaivén y reciclado, solo en victoria); háptica: victoria 3 pulsos crecientes (0,55/0,75/1,0), derrota 2 pulsos graves; gancho en processIntents case 'game-over' -> startFanfare()
- PANEL DE ENTRENAMIENTO: desplazado de x=-0,62 a x=-1,04 (borde derecho del panel en -0,853 vs borde de mesa -0,7625: 9 cm FUERA de la mesa) y rotación 0,5 -> 0,62 rad (encarado al jugador desde su nueva posición); verificado numérica y visualmente
- Verificación headless: contexto 'running' tras clic (hadGesture OK); guardas NaN probadas (paddle/tableBounce/net/thud/fanfare con NaN no lanzan); reparación real: ctx.close() -> estado 'closed' -> kick() -> 'running' con recreate (la causa raíz queda reparada); fanfarria victoria natural (11-4 forzado): msg "¡VICTORIA! · 11-4", banner visible, confeti activo, escala animándose; derrota natural (6-11): msg "DERROTA · 6-11", banner gris sin confeti; capturas scripts/preview_v10_fanfarria_victoria.png, preview_v10_fanfarria_derrota.png, preview_v10_panel_izquierda.png, preview_v10_gameover_natural.png; demo IA vs IA estable, cero errores de consola
- Rebuild 1,56 MB (sintaxis OK), desplegado a public/game.html, zip reempaquetado (834 KB, integridad OK), README con secciones v2.7

Stage Summary:
- El audio ya no puede quedar muerto: estados cerrados/rotos se recrean solos, los gestos (gatillo XR, toques 2D) lo reconstruyen al vuelo y ningún valor inválido rompe el frame
- Fin de partido con fanfarria completa (sonido + banner 3D + confeti + vibración + mensaje festivo); revancha inmediata con el gatillo
- Panel de ajuste de pala fuera de la mesa, a la izquierda del jugador
- Descarga y preview actualizados y verificados sin errores

---
Task ID: 12
Agent: main
Task: Fix audio en VR (solo sonaba en navegador 2D) — usuario: "el sonido solo se escucha antes de la sesion de VR en el navegador normal"

Work Log:
- Diagnóstico: v2.7 ya tenía rescates (kick/watchdog/rebuild) pero SOLO actúan si el contexto NO está 'running'. Pista del usuario (sonido OK en 2D, silencio en VR) + histórico (v2.6 destruyó y recreó el contexto en el clic y aún así silencio en VR) => causa raíz: Quest Browser mantiene el contexto 'running' al pasar a inmersivo pero RE-ENRUTA su salida a un dispositivo no audible en el casco; ningún rescate lo detecta porque el estado es 'sano'
- FIX: GameAudio._rebuild(reason, force) con flag force (salta throttle 1,2 s) + nuevo método público rebind(reason) (recreación INCONDICIONAL); onSessionStart ahora llama audio.rebind() (contexto nuevo creado DENTRO de la sesión XR => nace ligado a la salida activa del casco y 'running' por activación persistente del clic); onSessionEnd re-vincula a la salida 2D; mantenidos kicks a 400/1200/2500 ms, watchdog, kicks por selectstart/squeezestart
- Verificado: el resto de tareas ya estaban hechas en v2.7 (fanfarria audio+banner+confeti, panel x=-1,04, saques IA largos v2.6 mediana 0,83 m) => sin cambios
- agent-browser: demo #spectate en rally, cero errores de consola; rebind('test') ejecuta (rebuilds 9->15, estado 'suspended' esperado en headless sin dispositivo de audio); paddle/tableBounce sin excepciones; captura scripts/preview_v28_demo.png
- Rebuild 1,56 MB (sintaxis OK) -> download/pingpong-quest3-v2/index.html + public/game.html; zip reempaquetado (820 KB, integridad OK); README sección v2.8

Stage Summary:
- Audio en VR reparado por re-vinculación de salida: recreación forzada del AudioContext en sessionstart (dentro de la sesión) y en sessionend; los rescates v2.7 quedan como red de seguridad
- Fanfarria, panel de entrenamiento y saques largos confirmados intactos de v2.6/v2.7
- Build v2.8 desplegado y verificado sin errores

---
Task ID: 13
Agent: main
Task: Audio sigue mudo en VR tras v2.8 (usuario: "solo suena en la página antes de entrar en VR"; entra por Entrenar golpes -> loading -> silencio) + banner de derrota descentrado

Work Log:
- BANNER (bug encontrado): createFanfareBanner.draw() nunca fijaba ctx.textAlign -> título/marcador/subtítulo dibujados desde x=512 hacia la derecha (DERROTA se salía del lienzo). FIX: ctx.textAlign='center' antes del título. Además DoubleSide mostraba texto en ESPEJO desde atrás en la órbita de la demo -> FrontSide (invisible por detrás; en VR el jugador siempre está de frente). Verificado con game-over natural forzado: "DERROTA · 5-11" centrado en el panel (captura preview_v29_derrota5.png, vista espejo demuestra el centrado); victoria natural 11-6: confeti + HUD "¡VICTORIA! · 11-6 · gatillo: revancha" + banner escala pulsando ~1.0
- AUDIO v4 (política adoptar-solo-si-running): la v2.8 rebind() cerraba el contexto viejo ANTES de crear el nuevo -> si el nuevo nacía suspendido dentro de la sesión XR (activación no concedida), mudez total irreversible. tryFreshRunning(reason): crea contexto nuevo, lo ADOPTA solo si alcanza 'running' (tras resume + 600 ms de gracia) y si no lo DESCARTA conservando el anterior -> imposible quedar peor; _wire(ctx) extraído (master+compresor+noiseBuffer sobre ctx dado); _hookState(ctx): observador statechange por contexto -> en VR: resume inmediato si suspended, reintento a 900 ms, blip al recuperar; blipAlive(): doble blip audible cuando el audio (re)arranca en VR (throttle 4 s); kick()/watchdog()/prepareVR()/rebind() migrados de _rebuild(destruía) a tryFreshRunning; xrActive flag desde part3; reintento tardío a 3400 ms en onSessionStart; xrActive=false en onSessionEnd
- INDICADOR DE AUDIO EN VR: createAudioStatus() (part2) mini-panel 0,84x0,145 m bajo el marcador (y=1.44, roomFrontZ+0.9): verde "♪ audio: OK" / ámbar "♪ audio: reconectando… (pulsa el gatillo)" / rojo "mudo — pulsa el gatillo"; actualizado por poll cada frame en el bucle (this.audioStatus.update(ctx?.state)); si vuelve a fallar, el visor mismo muestra el estado -> diagnóstico sin consola
- Verificación headless: cero errores de consola; tryFreshRunning/kick/rebind sin excepciones (estado suspended esperado sin dispositivo de audio); chip ámbar "reconectando…" visible en capturas (comportamiento correcto en headless); rebuild 1,57 MB sintaxis OK -> index.html + public/game.html; zip 820 KB integridad OK; README sección v2.9

Stage Summary:
- La mudez irreversible de v2.8 es imposible por diseño: todo rescate ahora es adoptar-si-running o conservar el previo
- Red de seguridad completa en VR: rebind en sessionstart/sessionend, statechange observer, kicks (gatillo/grip), watchdog, reintento tardío 3,4 s y blip de confirmación audible al recuperar
- El visor muestra el estado del audio (chip bajo el marcador) -> si el usuario lo vuelve a reportar, sabremos si dice OK (running) o reconectando (suspended)
- Banner fin de partido centrado y sin espejo; victoria (dorado+confeti) y derrota (gris+Zzz) verificadas en demo

---
Task ID: 14
Agent: main
Task: Audio en VR suena SOLO con la ventana del navegador sin foco (v2.9: audio OK en VR, se apaga al entrar en la ventana de Chrome) — diagnóstico + rescates de foco

Work Log:
- Análisis de la pista del usuario: audio funciona en VR (v2.9 OK) pero se apaga al ENFOCAR la ventana del navegador; suena de nuevo al volver a la interfaz del sistema (Quest Link/menú). La sala sigue renderizando con el sonido apagado => la sesión XR sigue viva; no es sessionend. Revisión de GameAudio: no hay PannerNode/listener espacial (solo StereoPanner con guardas NaN) => hipótesis NaN-listener DESCARTADA. El código v2.9 es adoptar-solo-si-running (no puede autodestruir un contexto sano) => el muteo viene del sistema/navegador al cambiar el foco, con dos casos: (a) contexto suspendido (detectable) o (b) grafo zombi 'running' con reloj currentTime congelado (INDETECTABLE por el watchdog anterior)
- GameAudio v5 (game_part1.js): (1) watchdog ampliado con detección de grafo zombi: en estado 'running' compara ctx.currentTime con el tick anterior (_lastCT/_ctAdvanced/_ctStalls); 4 ticks congelados (~2,8 s) => tryFreshRunning('reloj de audio congelado') (adoptar-solo-si-running, nunca queda peor); nuevo método clockAlive(); (2) window 'focus' => hadGesture + kick() + blipAlive() si running&&xrActive (feedback audible inmediato al enfocar: si OYE el blip la salida va, si no el contexto está muerto); (3) visibilitychange=>visible ahora además kick() completo (antes solo resume())
- Indicador en pared v2 (game_part2.js): chip de audio con 2ª línea de diagnóstico técnico: 'T+/T- · ctx N · foco sí/NO · VR' (reloj avanza, nº contextos creados, document.hasFocus(), sesión XR); nuevo estado ámbar 'reloj parado — pulsa el gatillo' (running+reloj congelado); update(state, info) con firma por cambios (state|alive|focus|builds)
- Bucle (game_part3.js): audioStatus.update() ahora pasa {alive: clockAlive(), builds: rebuilds, focus: document.hasFocus(), xr: isPresenting}
- Banner derrota/victoria: ya corregido y verificado en v2.9 (textAlign center + FrontSide); el usuario no lo re-reporta => intacto
- Verificación headless (agent-browser): cero errores de consola; demo #spectate con ctx running, rebuilds 1, clockAlive() true, chip de 2 líneas visible bajo el marcador (captura preview_v210_chip.png); prueba controlada de reloj falsado (_lastCT=999999): detecta 1 tick congelado (alive=false, stalls=1), _lastCT se actualiza cada tick (autolimitante), contador se auto-recupera y no lanza excepciones; la ruta completa tryFreshRunning ya validada en v2.9
- Build 1,57 MB sintaxis OK -> download/pingpong-quest3-v2/index.html + public/game.html; zip reempaquetado LIMPIO (838 KB: solo index.html, eliminado assets/pala.glb residual que el HTML no referencia - GLB va embebido); zip integridad OK; README sección v2.10 con guía de lectura del chip
Stage Summary:
- El audio ya se autorepara si el navegador congela el grafo al cambiar el foco (grafo zombi), y al enfocar la ventana suena un blip de confirmación
- El chip en pared permite distinguir sin consola: 'OK · T+ · foco sí' con silencio = enrutado del SISTEMA (Quest Link/navegador, fuera del alcance del juego) vs 'reconectando/reloj parado' = el juego lo recupera solo
- Build v2.10 desplegado, zip limpio 838 KB, sin errores

---
Task ID: 14-bis
Agent: main
Task: Cierre del caso audio — usuario confirma: "si la pruebo directamente sin link se escucha perfectamente"

Work Log:
- Confirmación del usuario: en Meta Quest Browser del casco (SIN Quest Link) el audio funciona perfectamente => la causa del muteo por foco era el ENRUTADO DE AUDIO DE QUEST LINK (sistema: Link/Windows re-enruta/silencia el audio de la página al enfocar su ventana), no el juego
- Cadena de causalidad final: v2.8/v2.9 arreglaron la mudez real en VR (re-vinculación de salida + adoptar-solo-si-running); el síntoma restante (silencio al enfocar la ventana) era exclusivo de la vía Quest Link + Chrome de escritorio
- v2.10 queda igualmente como blindaje: rescate de grafo zombi (reloj congelado), rescate en focus/visibilitychange, blip de confirmación y chip de diagnóstico en pared (T+/T- · ctx · foco · VR)
- README actualizado con advertencia: probar SIEMPRE en el navegador del casco, no vía Quest Link (nota con la firma del chip que delata el muteo de Link)
- Sin cambios de código ni rebuild (solo documentación); zip intacto (838 KB, index.html autocontenido)

Stage Summary:
- AUDIO EN VR: CASO CERRADO Y CONFIRMADO POR EL USUARIO en el entorno objetivo (Quest 3 + Meta Quest Browser)
- Quest Link + Chrome de escritorio no es la vía soportada: documentado en README
- v2.10 desplegada como versión final de esta ronda, lista para seguir con nuevas mejoras

---
Task ID: 15
Agent: main
Task: v2.11 "torneo completo" — IA lista + adaptativa, modo Supervivencia, passthrough opcional, ambiente de torneo y polish 3D (elección del usuario vía AskUserQuestion)

Work Log:
- IA LISTA (game_part2.js OpponentAI): selección de golpe por situación: smash (bola alta y>1.15, T=minT*0.8, lift 16-24), dejada (rival detrás de media mesa + rally>=2: depth 0.16-0.26, T 0.92-1.17, slice -6..-11, vel 55%), push (bola baja: slice, vel 80%), bloqueo (bola entrante >6.5 m/s: profundo y rápido) y drive con lift como base (depth 0.62-1.12); 14% de golpes "al cuerpo" (hacia el lado del rival); dejadas más centradas (tx*0.6) para no fallar; spin.y lateral reducido a ±3
- IA ADAPTATIVA (game_part1 scalePreset + game_part3 applyAISkill): nivel efectivo = preset base × k; k = 1 + diff*0.055 (ganando, hasta +22%) o diff*0.05 (perdiendo, clamp 0.8); modo supervivencia multiplica k por 1+rallyes*0.08 (cap 2.1); scalePreset escala maxSpeed/accel/errStd/missBase/minT/maxT/maxShotSpeed/predictInterval/smash con clamps; verificado headless: 5-1 → k=1.22, 1-5 → k=0.80, supervivencia 8 rallyes → 1.64
- MODO SUPERVIVENCIA: Rules.startMatch(mode) + mode 'survival' en applyPoint (sin puntos: message "Rallye de N golpes", intent {survival, rallyHits}) y update (point→serve directo, NUNCA game-over); marcador con layout propio (SUP + rallye grande + rallyes + récord); récord en localStorage 'ppxr_surv_best' (guardado al batirlo con ovación applause(true) + announce); botón #survbtn en menú → enterVR(false,false,'survival'); la CPU acelera vía applyAISkill tras cada rallye
- PASSTHROUGH OPCIONAL: renderer alpha:true; enterVR(startCalib, useAR, mode) → requestSession('immersive-ar') ; onSessionStart detecta environmentBlendMode!=='opaque' → oculta roomGroup, background y fog, muestra shadowCatcher (ShadowMaterial 0.32) para sombra sobre el suelo real; onSessionEnd restaura todo; botón #arbtn (solo si isSessionSupported('immersive-ar')); verificado: roomVisible/shadowCatcher estados correctos en 2D
- AMBIENTE DE TORNEO (game_part1 GameAudio): startMurmur/stopMurmur (ruido rosa grumoso 2s loop + lowpass 520 + LFO 0.13Hz), applause(big) (2 capas estéreo, envolvente spiky 72 puntos via setValueCurveAtTime), ohh() (2 sierras 112/138Hz con formantes 470/920Hz, throttle 3.5s), announce(text,force) (chime 660/990Hz + speechSynthesis es-ES pitch 0.78, throttle 6s, force en bienvenidas/récord/game-over); setAmbience persiste 'ppxr_amb_v1'; cableado: murmullo al entrar en VR (900ms), bienvenida (1.4s), aplauso al punto del jugador, ohh en red y en faltas del jugador, megafonía en cada saque ("5-3, saque para ti"), ovación+megafonía en récord y game-over; botón #ambbtn SÍ/NO
- POLISH 3D: luz hemisférica cálida 0xffe6c4/0x35271b + direccional 0xfff1dc + 2 PointLights ámbar sobre la mesa; 7 vallas publicitarias LED (CanvasTexture 512x96, MeshBasic DoubleSide) dentro del roomGroup (laterales x=±1.95, fondo CPU z=-4.35, tras el jugador z=2.1); estela de bola por efecto: 22 puntos vertexColors, color por dirección de Magnus (spin×vel .y): naranja topspin / azul backspin / violeta lateral, fade por edad (0.42s); trailUpdate(ball,dt)
- GLB: se restauró assets/pala.glb desde upload/ping_pong_paddle.glb (5MB) y se REOPTIMIZÓ con scripts/glb_shrink.py (texturas 1024² → 512², PNG conservando alfa, geometría intacta) → 1.41 MB; index.html 2.05 MB
- Verificación headless: cero errores de consola; smoke tests (adaptativa k, supervivencia intents/messages, ambiente toggle+persist, nuevos métodos de audio sin excepciones); demo #spectate con vallas visibles y rally OK; marcador supervivencia dibujado (capturas preview_v211_demo.png, preview_v211_survival.png); zip 1.40 MB integridad OK; README v2.11

Stage Summary:
- v2.11 completa: IA con 5 golpes y adaptativa, supervivencia con récord persistente, passthrough opcional, ambiente de torneo completo (público+megafonía) y sala de pabellón con vallas y estela de efecto
- GLB reoptimizado (1.41MB) tras pérdida accidental del comprimido: nuevo script reutilizable glb_shrink.py
- Build desplegado en preview y zip listo para el casco

---
Task ID: 16
Agent: Super Z (main agent)
Task: Reparar la pala GLB rota + permitir cambiar de modo de juego en VR (reportado por el usuario)

Work Log:
- DIAGNÓSTICO GLB: el usuario tenía razón, la pala GLB no cargaba (fallback procedural activo).
  Tres daños causados por scripts/glb_shrink.py en la Task 15:
  1) Chunk BIN con tipo inválido 0x494E4942 ("BINI") en vez de 0x004E4942 ("BIN\0") del spec glTF.
  2) buffers[0].byteLength desincronizado con el chunk BIN real.
  3) 20 bufferViews reconstruidos SIN el campo obligatorio "buffer": 0 (crasheaba GLTFLoader:
     "Cannot read properties of undefined (reading 'type')" en loadBuffer), y 5 imágenes JPEG
     re-guardadas como PNG con mimeType incorrecto (PIL pierde .format tras resize).
- Corregido glb_shrink.py (tipo de chunk + campo buffer) para usos futuros.
- Nuevo scripts/glb_repair.py: parchea tipo de chunk, sincroniza byteLength, añade buffer:0 a
  cada bufferView, corrige mimeTypes por firma real de bytes y valida chunks/accesorios/mallas.
- assets/pala.glb reparado y validado (1,411,116 bytes; 24 bufferViews; 20 imágenes OK).
- MODO DE JUEGO: no se podía salir de un modo a otro en VR (solo desde el overlay 2D).
  - Nuevo switchMode(mode) en game_part3.js: reinicia en el nuevo modo, sincroniza IA (applyAISkill),
    anuncia por megafonía y vibra.
  - Botón B (mando derecho, button 5) FUERA del entrenamiento: alterna Partido ⇄ Supervivencia.
    Dentro del entrenamiento B sigue cambiando el agarre (sin conflicto).
  - Y (izquierdo) entra en entrenamiento recordando preCalibMode; al salir vuelve al modo anterior
    (antes siempre caía a un partido normal y desincronizaba this.mode vs rules.mode).
  - exitCalib ahora llama applyAISkill() y restaura aiToss/demoToss.
  - Revancha con gatillo y auto-reinicio tras 'over' mantienen el MISMO modo (rules.startMatch(this.mode)).
  - Textos: panel de entrenamiento ('Y: volver al modo anterior', nueva línea 'B (en juego):
    partido ⇄ supervivencia'), overlay con sección B·MODO, hint del marcador actualizado.
- Verificación headless (Playwright, scripts/verify_v212.py + shot_v212.py):
  - GLB cargado: 5 mallas BufferGeometry del modelo real, CERO errores de consola.
  - switchMode('survival') → mode=rules=survival; switchMode('match') → ambos match. OK.
  - Capturas: preview_v212_demo_nova.png / nova2.png — palas GLB con goma roja y mango de madera.

Stage Summary:
- index.html reconstruido (2.05 MB) en download/pingpong-quest3-v2/ con la pala GLB funcional
  y cambio de modo en VR: B = Partido ⇄ Supervivencia, Y = entrenamiento que ahora SÍ devuelve
  al modo previo. glb_shrink.py corregido; glb_repair.py nuevo (reutilizable para validar GLB).
- Pendiente de confirmación del usuario en el visor: pala GLB visible y B/Y en el juego real.

---
Task ID: 17
Agent: Super Z (main agent)
Task: Dificultad en VR + estadísticas y logros persistentes (v2.13)

Work Log:
- DIFICULTAD EN VR: pulsar el STICK de cualquier mando (buttons[3], fuera del
  entrenamiento) cicla Fácil → Media → Difícil al vuelo; setDifficulty ya
  recalibra la IA (applyAISkill), la megafonía anuncia, hay haptic y el
  marcador muestra "DIFICULTAD: X" hasta el siguiente estado. Sin conflicto
  con B (modo), Y (entrenamiento) ni A/X (cambio de pala).
- ESTADÍSTICAS (game_part1.js): nueva clase GameStats + ACHIEVEMENTS (6 logros:
  Primera victoria, En racha (3 seguidas), Gigante (victoria en Difícil),
  Maratonista (rallye 20+), Superviviente (25+ en Supervivencia), Saque
  directo (10 aces)). Persistencia en localStorage 'ppxr_stats_v1' con
  carga tolerante a datos corruptos.
- Integración en processIntents (game_part3.js): 'point' de partido registra
  punto (con detección de ace: rallyHits===1) y rallye; 'point' de
  supervivencia registra rallye + récord; 'game-over' registra V/D, racha y
  victoria por dificultad. El intent 'point' de partido ahora incluye
  rallyHits (game_part2.js).
- celebrate(): al desbloquear, megafonía + mensaje "LOGRO · X" en el marcador
  + ráfaga de confeti (confettiBurst 2.4 s integrado en confetti.update) +
  doble vibración en VR.
- Overlay (build_html.py): caja "TU PROGRESO" con línea de estadísticas y 6
  chips de logro (dorados al desbloquearse, tooltip con la descripción) +
  botón Borrar (limpia stats y ppxr_surv_best). Nueva línea de ayuda del
  STICK. Callback onStats → renderStats, con repintado al arrancar.
- Verificación headless (verify_v213.py): GLB ok (regresión), desbloqueo de
  5 logros secuenciado correcto, aces, persistencia localStorage, 6 chips
  (5 activos tras el test), presets easy/hard cambian la config de la IA,
  reset limpia todo. Captura preview_v213_stats.png.

Stage Summary:
- v2.13 (index.html 2.06 MB): dificultad cambiable en VR con el stick,
  progresión persistente con 6 logros celebrados por megafonía+confeti,
  y panel de progreso en el overlay. Sin errores de consola.
- Pendiente de confirmación en visor: buttons[3] (stick click) en Quest
  Browser y celebraciones de logro dentro del casco.

---
Task ID: 18
Agent: Super Z (main agent)
Task: Temas de sala intercambiables en VR (v2.14)

Work Log:
- Nuevo ROOM_THEMES en game_part1.js: 4 ambientes completos (Pabellón clásico,
  Neón arcade, Atardecer, Ártico). Cada tema define suelo/paredes/techo/
  paneles de luz/tira LED/anillo, colores de la rejilla, las 3 luces
  (hemi/direccional/focos), fondo+niebla y environmentIntensity. La mesa,
  bola, marcador y vallas LED no cambian (legibilidad del juego).
- createRoom (game_part2.js): expone refs en roomGroup.userData (floorMat,
  wallMat, ceilMat, panelMat, stripMat, ringMat, grid) para recolorear en vivo.
- Game (game_part3.js): loadTheme/setTheme/cycleTheme/applyTheme + rebuildGrid
  (la GridHelper hornea colores en vértices: se sustituye y se dispone la vieja).
  Persistencia localStorage 'ppxr_theme' con validación de clave; en passthrough
  (inAR) solo toca luces (fondo/niebla quedan null y la sala oculta).
- CONTROL: flick LATERAL del stick (cualquier mando, fuera del entrenamiento)
  cicla el tema. Ejes de stick estaban libres (el click ya es dificultad);
  umbral |x|>0.82 con |x|>|y|*1.4, retorno a centro y 250 ms entre cambios.
  Megafonía "Sala X", mensaje del marcador "SALA: X" y haptic.
- Overlay: fila SALA con 4 chips (clase .them, independiente de .diff para no
  pisar el .active de dificultad), callback onTheme para sincronizar cuando el
  cambio llega del flick en VR, repintado al arrancar con el tema persistido.
  Ayuda: nueva línea SALA en ul.keys y línea nueva en el panel de entrenamiento
  ('STICK ←→ (en juego)', 'tema de la sala').
- Verificación headless (verify_v214.py + shot_v214.py): GLB ok (regresión),
  0 errores de página; temas cambian materiales/luces/fondo y la rejilla se
  reconstruye bien; cycleTheme envuelve en ambas direcciones; persistencia
  tras reload (artico -> #1c2830/#0d1418); chips sincronizados y clic de chip
  aplica tema. Capturas de los 4 temas en modo espectador (shot_v214_*.png):
  transformaciones claramente distintas y coherentes.

Stage Summary:
- v2.14 (index.html 2.07 MB): 4 salas intercambiables al vuelo con flick del
  stick, persistentes entre sesiones y elegibles también desde el overlay 2D.
  Sin tocar controles existentes (click stick=dificultad, B=modo, Y=entreno,
  A/X=mano, gatillo/grip=saque). Sin errores de consola.
- Pendiente de confirmación en visor: gesto de flick no dispara la dificultad
  por accidente y los 4 temas lucen en el Quest 3 (especialmente Neón en OLED).

---
Task ID: 19
Agent: Super Z (main agent)
Task: Menú de muñeca — consolidar TODA la configuración en un panel VR (v2.15)

Work Log:
- ELIMINADOS los gestos sueltos: stick-click de dificultad (0.7) y flick
  lateral de sala (0.8) fuera del código; B ya no cambia de modo directo.
- NUEVO MENÚ DE MUÑECA (game_part3.js): buildMenu crea panel 3D (0.28×0.35 m,
  CanvasTexture 512×640, depthTest off + renderOrder alto) con cursor-punto y
  línea guía de apuntado; vive en espacio MUNDO (inmune al recentrado del rig).
- drawMenu pinta tarjeta redondeada con secciones: MODO (Partido/Supervivencia),
  DIFICULTAD (Fácil/Media/Difícil), SALA (2×2: Pabellón/Neón/Atardecer/Ártico),
  AMBIENTE DE TORNEO (Sí/No), REVANCHA (solo con state 'over') y Cerrar menú.
  Estado activo en ámbar; hover con borde blanco; menuRects guarda zonas
  clicables en px de canvas para el hit-test por UV.
- Anclaje (updateMenu): panel flotando ~15 cm de la muñeca de la MANO LIBRE
  (1 - paddleHand, salta sola al cambiar la pala de mano), mirando a la cabeza.
  Raycaster desde el targetRay del mismo mando (this.rays guardado en
  setupControllers); hover redibuja solo al cambiar de botón (barato).
- INTERACCIÓN: B (derecho, fuera del entrenamiento) abre/cierra; dentro del
  entrenamiento B sigue cambiando agarre (toggleMenu guardado por calib).
  GATILLO con menú abierto = clic en panel (ni saque asistido ni revancha);
  grip de soltar bola ignorado con menú abierto. Y sigue abriendo entrenamiento
  (enterCalib cierra el menú). Al iniciar sesión el menú nace cerrado.
- Clics: modo → switchMode + cierra; dificultad/tema/ambiente → aplican en
  vivo (megafonía, mensaje, haptic según acción) y el menú queda abierto para
  seguir probando; revancha → startMatch(this.mode) + cierra.
- Textos: overlay reescrito (una sola línea MENÚ en ul.keys; REGLAS/EFECTO
  restauradas tras editar), panel de entrenamiento con 'B (en juego): abrir /
  cerrar el MENÚ' y resumen del menú. Chips 2D del overlay siguen funcionando.
- Verificación headless (verify_v215.py): GLB ok, 0 errores; menú abre con los
  12 botones esperados; clics diff:hard/theme:neon/amb:off aplican y persisten
  (localStorage) sin cerrar; mode:survival aplica y CIERRA; REVANCHA aparece
  solo con state 'over', reinicia y cierra; botón Cerrar funciona. Capturas
  shot_v215_menu.png / _hover.png (panel sobre la mesa, hover en Difícil).

Stage Summary:
- v2.15 (index.html 2.08 MB): un solo punto de configuración en VR — B abre el
  menú en la muñeca libre, gatillo elige. Mapa mental final: B=menú, Y=entreno,
  A/X=mano de la pala, gatillo/grip=saque. Nada más que memorizar.
- Pendiente de confirmación en visor: legibilidad del panel a distancia de
  muñeca (0.28 m ancho) y que el rayo del mando libre apunte con comodidad.

---
Task ID: 20
Agent: Super Z (main agent)
Task: Corregir el menú de muñeca según feedback del visor (v2.16)

Work Log:
- FEEDBACK USUARIO: (1) el panel estaba muy cerca de la cara/despegado de la
  mano; (2) imposible seleccionar: la otra mano tiene la pala y no había
  forma de apuntar.
- CAUSA RAÍZ 2: updateMenu raycasteaba SOLO con el mando que aloja el panel
  (mano libre) y onSelectStart solo aceptaba clics de ese mando.
- REDISEÑO (game_part3.js): rayo + láser + cursor + hover INDEPENDIENTES por
  mando (menuLines[2], menuDots[2], menuHover[2]); gatillo de CUALQUIER mano
  hace clic con el menú abierto; colores de láser por mano (ámbar/cian).
  drawMenu pinta hover si CUALQUIER mano lo toca; un solo repintado por frame.
- ANCLAJE: panel a distancia CONSTANTE 0,16 m sobre la muñeca libre (bandeja);
  eliminado el desplazamiento hacia la cabeza (antes 0,15 hacia la cara +
  0,09 arriba: se iba hasta 0,21-0,23 m con la mano baja). La orientación
  sigue mirando a la cara y la distancia de lectura la manda el brazo.
- Caso borde cerrado: mando desconectado con menú abierto apaga su láser
  (antes quedaba congelado el visible=true del frame anterior).
- Textos: overlay y subtítulo del panel ('apunta con la pala y elige con el
  GATILLO'), README v2.16.
- Verificación (verify_v216.py): 2 obstáculos técnicos resueltos — (a) los
  espacios targetRay tienen matrixAutoUpdate=false y matrixWorld obsoleta en
  2D: hay que componer ray.updateMatrix() y orientar con Matrix4.lookAt
  (Object3D.lookAt lee la matriz vieja); (b) cámara de demo orbital:
  congelada con monkey-patch de camera.getWorldPosition. 11 pruebas OK:
  GLB, apertura, 12 botones, arrays 2/2, anclaje 0,16 m, hover de la PALA
  (índice correcto, láser+cursor visibles), clic con gatillo de la pala
  aplica Difícil y deja el menú abierto, hover independiente por mano, tema
  Neón desde la mano libre persiste, modo cierra, REVANCHA condicional,
  Cerrar apaga láseres. 0 errores de página. Capturas shot_v216_*.png.
- Entrega: index.html reconstruido (2,08 MB), ZIP regenerado, capturas en
  download/ (captura-v216-menu-*.png).

Stage Summary:
- v2.16: el menú de muñeca ya es seleccionable con la mano de la pala (láser
  propio) y el panel vive pegado a la muñeca libre, no flotando hacia la
  cara. Mapa de interacción intacto: B=menú, Y=entreno, A/X=mano,
  gatillo/grip=saque; con menú abierto el gatillo elige desde cualquier mando.
- Pendiente de confirmación en visor: distancia de lectura con el brazo en
  reposo y comodidad del apuntado con la pala.

---
Task ID: 21
Agent: Super Z (main agent)
Task: v2.17 — haz del menú visible + IA reconstruida (feedback de visor)

Work Log:
- FEEDBACK: (1) panel mejor pero el haz mando->botón no se ve, solo el
  resaltado; (2) la CPU golpea mal, falla mucho, parece calcular mal las
  trayectorias y mueve la pala de forma robótica.
- LÁSER (part3): THREE.Line dibuja 1 px — invisible en el visor. Sustituido
  por cilindro de 2,2 mm (geometry rotada a -Z, nace en el mando),
  depthTest false, renderOrder 940, opacity 0.85, se engorda x1.7 sobre
  hover. Colores por mano (ámbar/cian) mantenidos.
- IA · DIAGNÓSTICO (tests headless con física replicada en Python + recorder
  in-page): (a) computeShotVelocity resolvía la parábola SIN arrastre/Magnus
  → tiros 15-27 cm cortos y muertes en la red por el lift; (b) predictStrike
  devolvía null tras el bote (no sembraba botes ya ocurridos) → la IA se
  quedaba CIEGA justo al golpear ("no llega"); (c) errX/errY se re-sorteba
  cada re-predicción (0.1 s) → pala temblorosa; (d) sin swing: la pala se
  desliza; (e) depthRel hasta 1.12 apuntaba FUERA de la mesa.
- IA · SOLVER (part1, computeShotVelocityReal): siembra balística + 16
  iteraciones de corrección simulando con la física REAL (240 Hz, aero,
  bote); guarda el MEJOR iterado (err mínimo con red superada; el último
  podía oscilar con el clamp de velocidad); verificación final anti-red con
  loft extra; margen anti-cinta 8.5 cm; clamp de profundidad 0.94.
- IA · RESTO: predictStrike(ball, sign, bounced) siembra myBounces=1 cuando
  rules.validBounce (adiós a la ceguera); errores estables por bola entrante
  + lerp 0.45 de refinamiento; swing de follow-through (0.3 s, ease-out
  2.4, amplitud según velocidad del tiro) disparado en cada golpeo;
  preparación (retroceso ≤9 cm al acercarse la bola) y bob de espera;
  reach 0.185→0.21; presets: missBase easy/med/hard 0.22/0.11/0.04 →
  0.15/0.08/0.03, errStd 0.11/0.06/0.028 → 0.09/0.05/0.024.
- VERIFICACIÓN CUANTITATIVA (test_ai_returns.py, 14 tiros sintéticos
  calibrados con física real hacia el campo CPU): v2.16 → ~7-20% devueltos
  con ~35% de tiros a su propia red; v2.17c → **13/14 (93%)**, botes
  profundos 0.81-1.33 m, 2 rozadas de cinta, 1 bola ganadora. Regresión del
  menú (verify_v216.py) TODO OK, 0 errores de página. Hook de diagnóstico
  opt-in (__wantSolverHook/__logAiHits/__aiDbg) añadido para futuros tests.
- Entrega: index.html 2.09 MB, capturas captura-v217-menu-haz*.png, ZIP
  regenerado, README actualizado.

Stage Summary:
- v2.17: la CPU devuelve el 93% de las bolas con tiros que botan donde
  apunta (física real en el solver), se mueve con preparación/swing/bob y
  el menú muestra un haz láser grueso y visible desde cualquier mando.
- Pendiente visor: sensación de dificultad (media ahora devuelve mucho más;
  la adaptativa + supervivencia siguen escalando), legibilidad del haz y
  naturalidad del swing.

---
Task ID: 22
Agent: Super Z (main agent)
Task: v2.18 (saque fácil + panel desbordado + estela) y v2.19 (multijugador online + voz)

Work Log:
- FEEDBACK de varios usuarios: (1) saque difícil, (2) panel lateral con texto
  sobrepasado, (3) falta opción para ocultar la estela; después, añados
  grandes: (4) jugar contra otra persona en remoto y (5) voz entre ambos.
- v2.18 · SAQUE: gatillo de CUALQUIER mando lanza (antes solo mano libre);
  eliminada la puerta del punto muerto (cualquier contacto tras el toss vale,
  el asistente findServeVelocity endereza igual); tossMinRise 0.14→0.06;
  serveAssistVy 2.6→3.1 (más tiempo de vuelo); serveExtraReach 0.06→0.09;
  serveEndLineTol 0.10→0.25; mensajes reescritos ("¡Golpea la bola hacia la
  mesa!", "Tu saque · GATILLO para lanzar y golpear").
- v2.18 · PANELES: createCalibPanel re-espaciado (y 224→214, paso 29→25; la
  última línea caía en y=514 fuera del canvas 512); marcador: mensaje con
  auto-ajuste de fuente (measureText, 40→22 px) en vez del recorte a 46 chars.
- v2.18 · ESTELA: showTrail persistente (ppxr_trail_v1), trailObj.visible,
  fila EXTRAS en el menú con [Ambiente][Estela] basculantes; menú compactado
  (cierre en y≤568).
- v2.19 · RED (NetLink en part2, PeerJS 1.5.4 incrustado en el HTML): salas
  'ppxr3-XXXXX' (código sin 0/O/1/I); anfitrión autoridad de reglas, invitado
  con reglas sombra (applySync); dueño de la bola = último golpeador, emite a
  20 Hz pos/vel/spin; el no-dueño sigue la emisión (lerp) y solo testa el
  contacto de SU pala (testPaddleContact nuevo en part1); espejo de mundo =
  rotación 180° en Y sobre el centro de mesa (x,z → -x, -3.2-z), quaternion
  premultiplicado por (0,1,0,0) [corregido: era 90° por error]; golpes viajan
  como {k:'h'} y el anfitrión los valida/registra; eventos T/N/F/W marcados
  _net para no hacer eco; revancha y cambio de modo del invitado por mensajes;
  desconexión → partido local con 'la CPU'.
- v2.19 · VOZ: getUserMedia(audio) al conectar + peer.call (anfitrión llama,
  invitado responde); <audio autoplay> para el remoto; Voz: Sí/No (tracks
  enabled); estados asking/on/denied en el panel; sin micrófono se juega igual.
- v2.19 · MENÚ: páginas main/multi/join con pestañas [AJUSTES][MULTIJUGADOR];
  página multi con código grande, estado y voz; página join con 5 huecos +
  teclado 7×5 (31 teclas + ⌫) + CONECTAR/VOLVER; difficulty no-op online.
- VERIFICACIÓN: verify_v218.py (12 pruebas OK: saque fácil con gatillo de la
  pala vy=3.1, extraReach 0.09 solo en saque, estela alterna/persiste, marcador
  largo, calib, regresión menú v2.16) + verify_v219.py (12 pruebas OK con Peer
  simulado: sala, conexión, protocolo con espejo, sync invitado, ida/vuelta de
  espejo pos+quat, teclado ABC29→conectado como invitado, voz, colgar×2).
  test_ai_returns.py: 13/14 (93%) sin regresión. Capturas captura-v219-*.
- Nota de entorno: en headless, los timers anidados con SwiftShader no disparan
  de forma fiable — el mock de Peer usa queueMicrotask (artefacto del test,
  no del juego). Bug real encontrado y corregido: quaternion del espejo.
- Entrega: index.html 2.21 MB (PeerJS incrustado), ZIP, README v2.18-v2.19,
  capturas captura-v219-menu-{ajustes,multi,teclado}.png.

Stage Summary:
- v2.18: el saque lo saca cualquiera (gatillo en ambos mandos, sin punto
  muerto, margen +50%); el panel lateral ya no corta texto; estela opcional.
- v2.19: partidas P2P por código de sala de 5 caracteres + voz integrada,
  todo dentro del mismo HTML autocontenido (PeerJS inline).
- Pendiente de visor: probar el online entre dos visores reales (latencia,
  permiso de micro en Meta Quest Browser) y la sensación del saque nuevo.

---
Task ID: 23
Agent: Super Z (main agent)
Task: v2.20 — la voz del megáfono (marcador) audible dentro de la experiencia VR

Work Log:
- FEEDBACK: "la voz que da los puntos solo la escucho en la página del
  ordenador". Causa raíz: el megáfono usaba window.speechSynthesis, que el
  Meta Quest Browser NO reproduce durante la sesión inmersiva (sí en la
  pestaña 2D); el chime sí se oía porque va por WebAudio (misma vía que los
  efectos, que funcionan en VR).
- SOLUCIÓN: voz real incrustada. 67 fragmentos es-ES generados con Piper TTS
  (modelo es_ES-davefx-medium, binario oficial 2023.11.14-2) → Opus 28k mono
  con ffmpeg (235 KB) → scripts/game_voice.js (315 KB base64, const
  VOICE_B64). Átomos: números 0-29 + decenas + 'y'/'a', frases completas
  (bienvenida, modos, rival conectado/desconectado, salas ×4, dificultades
  ×3, victoria, partido para CPU/rival, saque para ti/rival/máquina, logro
  desbloqueado, rallye de/golpes/nuevo récord) y los 6 nombres de logros.
- TROPIEZOS: z-ai TTS/ASR (SDK) no pronuncia español usable (7 voces
  probadas; verificado con ASR: "Atardecer"→"ata yi manakot"); piper-tts
  1.8.0 pip produce audio estirado corrupto con onnxruntime 1.30 → binario
  oficial de piper OK. El binario lee el texto por STDIN (argumento
  positional se cuelga). ASR de palabras aisladas falla por falta de
  contexto (transcribe fonéticamente en otro idioma) → validación final con
  clip-lista: "cinco a tres"→"5a3", "rallye de veinte golpes"→"de 20
  golpes", números→dígitos correctos: pronunciación VALIDADA. Rate limit
  429 del ASR: reintentos con backoff (asr_check.py).
- CÓDIGO (game_part1.js): tablas VOICE_FULL/VOICE_ACH/VOICE_NUM +
  voiceNumPlan (0-99 compuesto) a nivel de módulo; GameAudio._loadVoice(ctx)
  decodifica VOICE_B64 con normalización de pico 0.60 por fragmento (se
  engancha en _wire → se recarga con cada contexto nuevo al entrar/salir de
  VR); _normVoice/voicePlan (texto→plan [{k,gap}] o null) y speakPlan
  (encadena BufferSources sobre this.master tras el chime); announce()
  prioriza el banco (WebAudio, audible en VR) y solo usa speechSynthesis
  como respaldo 2D si falta un fragmento (sin doble voz).
- BUILD: build_html.py incluye game_voice.js como primera parte. index.html
  2.21 → 2.54 MB.
- VERIFICACIÓN (verify_v220.py): TODO OK — banco 67/67 decodificado en el
  AudioContext real (Opus OK, sampleRate 44100, ganancias finitas);
  voicePlan cubre 30/32 frases de prueba (100% de las que emite el juego;
  2 casos de respaldo correctos); announce('5 a 3, saque para ti') programa
  exactamente 4 BufferSources encadenadas y NO llama a speechSynthesis;
  texto desconocido cae al respaldo; regresión menú OK; 0 errores de página.
  Regresiones completas: verify_v218.py TODO OK, verify_v219.py TODO OK,
  test_ai_returns.py 12/14→14/14, 14/14 (la variación es estocástica: seed
  salado por hash() de Python; sin regresión).
- ENTREGA: index.html 2.54 MB, ZIP regenerado (3.0 MB, integridad OK),
  README con sección v2.20. scripts nuevos: gen_voice.py, build_voice.py,
  asr_check.py, verify_v220.py.

Stage Summary:
- v2.20: la megafonía del marcador ("5 a 3, saque para ti", victoria,
  logros, récord…) ya se oye DENTRO del visor de la Quest 3: clips es-ES
  reales por WebAudio en vez del TTS del navegador; speechSynthesis queda
  como respaldo en escritorio.
- Pendiente de visor: confirmar con el usuario que la voz ya suena en VR
  (volumen/claridad en el altavoz del casco) y seguir con la fase online
  real (dos visores, latencia, permiso de micro).

---
Task ID: 24
Agent: Super Z (main agent)
Task: v2.21 — fin del "efecto invertido" de la pala (transparencia fantasma del GLB)

Work Log:
- FEEDBACK: "la pala sigue estando mal… asegurar que las caras no se viesen
  invertidas, el efecto sigue estando presente; una solución es renderizar
  por el lado frontal y el reverso". El DoubleSide ya estaba desde v2.13 y
  fixInvertedMeshes (volumen firmado) desde la versión siguiente → la causa
  era OTRA.
- AUDITORÍA GEOMÉTRICA (glb_face_audit.py): winding (volumen firmado) y
  alineación de normales de las 5 primitivas PERFECTOS (ndot ≈ 1.00,
  0 problemas) → descartado el modelo.
- AUDITORÍA DE MATERIALES (glb_material_audit.py): los 5 materiales
  (rubber/trim/paddle/inner_padding/handle) exportados con alphaMode=BLEND
  pese a texturas RGB SIN canal alfa y alfa base 1 (transparencia fantasma
  del exportador).
- CONFIRMACIÓN EN VIVO (diag_pala_faces.py sobre index.html): GLTFLoader
  three 0.170 con BLEND fija transparent=true Y depthWrite=false
  (three#17706, comprobado en el fuente del CDN, línea 3581) → la pala se
  dibuja sin escribir profundidad: con DoubleSide se ven caras internas y
  traseras mezcladas por orden de dibujo (efecto radiografía).
- FIX EN DOS CAPAS: (1) glb_fix_blend.py reescribe el JSON del GLB a
  alphaMode=OPAQUE (5 materiales, padding de espacios según spec, BIN
  intacto, 1.411.380 → 1.411.384 bytes) — copia de seguridad
  scripts/pala.glb.bak; (2) guardia en runtime en loadPaddleModel
  (game_part1.js): si m.transparent && opacity>=1 && !alphaTest →
  transparent=false + depthWrite=true. DoubleSide + shadowSide SE MANTIENEN
  (petición explícita del usuario: renderizar frontal y reverso).
- BUILD: build_html.py → index.html 2.54 MB (sintaxis OK).
- VERIFICACIÓN: diag en vivo → 5/5 materiales transparent=False,
  depthWrite=True, side=DoubleSide; capturas del canvas (toDataURL,
  bypassing overlay DOM): frontal, reverso, 2 rasantes y canto — hoja
  COMPLETA (adiós la media luna), oclusión correcta de red/mesa, banda del
  canto limpia. Regresiones: verify_v220.py TODO OK (voz 67/67), 
  verify_v219.py TODO OK (sala P2P RZJ9N, protocolo), verify_v218.py TODO
  OK (menú 14 botones, saque fácil). 0 errores de página.
- ENTREGA: ZIP regenerado (3,0 MB, integridad OK), README sección v2.21,
  4 capturas download/captura-v221-pala-*.png.

Stage Summary:
- v2.21: la pala se ve SIEMPRE correcta (anverso/reverso/canto/rasantes):
  la causa real era alphaMode=BLEND ficticio → depthWrite=false del
  GLTFLoader; ya no hay radiografía ni caras internas, con DoubleSide
  conservado.
- Pendiente visor: que el usuario confirme voz v2.20 en VR + pala limpia.
- Siguiente fase (petición del usuario): parte estética "vidilla" del
  entorno (iluminación, materiales, detalles de sala).

---
Task ID: 25
Agent: Super Z (main agent)
Task: v2.22 — pala de la IA con golpeo realista + conmutador del megáfono + dicción natural (sin cortes entre cifras)

Work Log:
- FEEDBACK: (1) "la pala de la máquina se oriente de forma realista al
  golpear, como un jugador real; ahora golpea con la pala perpendicular al
  suelo"; (2) conmutador para activar/desactivar los audios del narrador;
  (3) "en todas las pistas de audio hay un pequeño corte antes de decir la
  segunda cifra".
- (3) CAUSA: los clips de Piper traían 0,1-0,3 s de silencio por lado;
  verificado midiendo el banco: 23,74 s de silencio sobre 72,31 s (33 %).
  FIX: _loadVoice (game_part1.js) ahora calcula por fragmento el tramo con
  voz [t0,t1] (umbral relativo al pico 7%, pre-roll 12 ms, cola 55 ms) y lo
  guarda en audio.vbTrim; speakPlan reproduce src.start(t, off, dur) con ese
  tramo y avanza t += dur + gap → las ÚNICAS pausas son las del plan. Gaps
  inter-palabra 0,075 → 0,06 s. Verificado con hook de
  AudioBufferSourceNode.start: "5 a 3, saque para ti" → 4 fuentes, gaps
  reales [0.07, 0.07, 0.2999]; "cinco" 0,82 s → 0,42 s.
- (2) FIX: audio.voice (persistente ppvr_voz_v1... clave 'ppxr_voz_v1') +
  setVoice() espejo de setAmbience; announce() gatea con
  if (!this.voice || !this.ambience) return (megáfono OFF = sin chime ni
  voz ni respaldo). Menú EXTRAS: nuevo botón 'voz' "Megáfono del marcador:
  Sí/No" (fila propia a 412); layout compactado (SALA 242, EXTRAS 356, filas
  h40-42, revancha/pestañas/cerrar 460+) — todo cabe con margen (cerrar
  termina en 548 sin revancha, 602 con ella). menuClick case 'voz'.
- (1) FIX: updateAIPaddlePose (game_part3.js) reescrito: helper faceTo(dir,
  roll) construye la base ortonormal de la cara (normal +Z hacia dir, mango
  abajo) con guiñada ±1.3 rad alrededor de faceYaw y elevación [-0.5, 0.72],
  roll de muñeca alrededor de la normal (quaternion local Z). Ramas: espera
  → cara MIRA la bola (+ vaivén); saque-toss → cara SIGUE el lanzamiento;
  saque-impacto → cara hacia la velocidad de salida; follow-through → cara
  acompaña ball.vel con apertura por spin.x (cortada abre, liftado cierra,
  signo según el campo atacado: tilt=clamp(0.2+s·spin.x·0.12)) y cierre
  progresivo (−0.24·e) + roll creciente del swing. OpponentAI.swing gana
  roll aleatorio ±0.17 rad (game_part2.js). Online sin cambios (pose real
  por red). Temps nuevos: aimV/aimX/aimY/aimM/aimUP/aimRollQ/AIM_Z.
- VERIFICACIÓN (verify_v222.py, TODO OK): menú 15 botones con 'voz' y
  persistencia; gate del megáfono (OFF → 0 fuentes y sin speechSynthesis;
  ON → 4); vbTrim 67/67 válido, 23,74 s recortados; cadena con offsets>0 y
  gaps ≤0.12 entre cifras; orientación: idleDot=1.0/ny=0.046 (cara a la bola
  e inclinada), swingDot=1.0, serveDot=1.0, tossDot=1.0. Regresiones:
  verify_v220 TODO OK, verify_v218 TODO OK, verify_v219 TODO OK,
  test_ai_returns 14/14. Capturas: menu_v222 (sin desbordes), ia_espera e
  ia_swing (postura natural visible). 0 errores de página.
- BUILD: index.html 2.55 MB; ZIP 3,0 MB integridad OK; README sección
  v2.22; capturas download/captura-v222-*.png.

Stage Summary:
- v2.22: la IA golpea "de verdad" (cara mirando bola/salida, abre-cierra
  con el efecto, muñeca con roll), el narrador tiene conmutador propio en
  EXTRAS y la dicción es compacta (adiós el corte antes de la segunda
  cifra: 23,7 s de silencio muerto eliminados del banco).
- Pendiente visor: confirmar sensación del golpeo de la IA y claridad de la
  nueva dicción en el casco; sigue pendiente la confirmación de la voz en
  VR (v2.20). Siguiente fase: estética/"vidilla" del entorno.

---
Task ID: 26
Agent: Super Z (main agent)
Task: v2.23 — cifras del megáfono sin cortes ni ruidos + pala de la IA que
golpea de derecha y revés girando la hoja + menú con casillas vivas

Work Log:
- FEEDBACK: (1) "el audio se sigue cortando, los números deben escucharse
  con total claridad sin ruidos ni cortes"; (2) "la pala no se mueve de
  forma natural y prácticamente siempre permanece vertical; lo suyo es que
  golpee de izquierda y de derechas rotando la pala para que el golpe tenga
  sentido, vertical o más horizontal según proceda"; (3) "el menú tiene
  marcadas casillas que no son seleccionables ni cambian visualmente de
  estado".
- (1) CAUSA REAL: v2.22 encadenaba N AudioBufferSourceNodes con offsets —
  cada frontera entre fuentes era un mini-corte audible en el visor, y el
  silencio real entre cifras sumaba cola recortada + gap + pre-roll ≈ 0,14 s.
  FIX v2.23: speakPlan COMPONE UN SOLO AudioBuffer: copia cada fragmento
  (recortado por vbTrim con pre 10 ms / cola 30 ms, normalizado por vbGain)
  con micro-fades de 4 ms (entrada) y 9 ms (salida) — cero chasquidos en las
  juntas — y lo reproduce con UNA única fuente (src.start simple). Gaps del
  plan ahora EXACTOS: intra-cifra 0,036-0,042 s → silencio real medido
  0,045-0,053 s; pausa de frase 0,26 s → 0,276 s. El chime conserva su hueco
  (cabecera 0,34 s dentro del buffer). Ganancia del megáfono 1.12.
- (1b) DUCKING: nuevo bus this.ambBus (murmullo + aplausos + "ohh" van a él)
  en _wire; announce() lo baja a 0.24 con rampa de 0,22 s y lo restaura con
  setTargetAtTime al terminar la locución (usando this._voiceDur) — las
  cifras se oyen por ENCIMA del pabellón. Re-entradas seguras
  (cancelScheduledValues antes de cada rampa).
- (2) CAUSA: faceTo (v2.22) construía la base con el eje Y local ≈ vertical
  SIEMPRE (mango abajo) → pala vertical perpetua. FIX v2.23:
  updateAIPaddlePose REESCRITA con bladePose(bladeDir, faceDir, roll, pitch):
  la orientación se compone desde el EJE DE LA HOJA (mango→punta) y la
  NORMAL DE LA CARA como direcciones independientes, más pitch de muñeca
  alrededor del eje local X (cierra/abre la cara DESPUÉS de ortogonalizar:
  no se deforma) y roll alrededor de Z.
  · OpponentAI decide el LADO del golpe (fhSide: +1 derecha, -1 revés) al
    aparecer la bola (dx respecto al cuerpo * sign, zona muerta 5 cm con
    sesgo diestro 55 %) y lo mantiene durante el rallye de esa bola; la
    preparación (prep) además CARGA 7,5 cm hacia el lado del golpe.
  · El swing lleva kind/fh/vdir; SWING_POSE define la firma de cada golpe
    (side0/side1 carga y cruce de la punta, fwd0/fwd1 inclinación de la
    hoja, clos0/clos1 cierre de la cara, rise, cross): drive diagonal que
    cruza el cuerpo (hoja 45°→66°), push de hoja casi vertical con cara
    abierta, smash cerrado, dejada abierta y alta, bloqueo compacto.
  · Saque diestro: la postura pasa al lado contrario de la bola (stance
    x - s*0.17) y el impacto deriva la hoja ⟂ a la salida → la cara queda
    EXACTA hacia donde vuela (serveDot = 1.00).
  · Espera: hoja inclinada 14° hacia delante/lado de la bola (no pared),
    cara ofrecida con pitch según altura de la bola.
- (3) CAUSA: el hover SOLO dibujaba borde en botones inactivos (los marcados
  no respondían visualmente) y los rects eran exactamente el dibujo (2 cm
  imposibles de puntear). FIX: hover también en activos (borde blanco +
  brillo del relleno), casilla ☑/☐ dibujada en los basculantes (amb, trail,
  voz, net:mic), rects inflados +10×6 px (táctil > dibujo) y case 'mode' YA
  NO CIERRA el menú (el cambio se ve; mensaje "cierra el menú para jugar").
  Fila voz movida a y=414 por el padding.
- VERIFICACIÓN (verify_v223.py TODO OK): voz = 1 fuente compuesta, gaps
  [0.045, 0.053, ...] con pausa de frase 0.276, peak 0.724 (sin saturación),
  cabecera 0.347; ducking 0.24 → 1.0; gate del megáfono intacto; pose de la
  pala: idleTilt 14.1° (no vertical), drive fh punta -0.62→+0.47 (cruce),
  hoja 45°→66°, cara cerrada con liftado (-0.38) y abierta con cortada
  (+0.34 relativa), revés espejo, brazo cruza el cuerpo, postura de saque
  diestra (±0.17); menú: 15 botones TODOS con feedback de píxeles al
  apuntarlos (1332-18231 px), área táctil 146×48, modo/dificultad cambian
  con el menú abierto, persistencias OK. Regresiones: verify_v218 TODO OK,
  verify_v219 TODO OK (sala P2P), verify_v220 TODO OK (67/67, actualizada a
  1 fuente), verify_v222 TODO OK (serveDot 1.00, idleTilt 11.3°),
  test_ai_returns 14/14 (100 %). 0 errores de página.
- BUILD: index.html 2.56 MB; capturas captura-v223-pala-{espera,swing}.png y
  captura-v223-menu{,-hover}.png; ZIP regenerado; README sección v2.23.

Stage Summary:
- v2.23: las cifras suenan fluidas y por encima del pabellón (buffer
  compuesto + ducking), la IA golpea de derecha y revés con la hoja girando
  y la cara abriendo/cerrando según el efecto, y el menú responde también en
  sus casillas marcadas con área táctil holgada.
- Pendiente visor: confirmar en el Quest 3 la dicción (sin cortes), la
  naturalidad del golpeo y el menú; sigue pendiente la parte estética
  ("vidilla" del entorno) como siguiente fase.

---
Task ID: 27
Agent: Super Z (main agent)
Task: v2.24 — puntero del menú sin espejo vertical, fin de la doble pulsación (casillas/teclado) y multijugador utilizable

Work Log:
- FEEDBACK: (1) casillas marcadas en amarillo que "no se pueden desmarcar ni
  cambian de estado"; (2) al apuntar con la mano de la pala la intersección
  es correcta en horizontal pero INVERTIDA en vertical; (3) en el menú
  multijugador el puntero no apunta bien y CREAR SALA / INTRODUCIR CÓDIGO
  tienen zonas pulsables desplazadas; (4) CREAR SALA no hace nada (no se ve
  el código); (5) el teclado del código DUPLICA cada tecla.
- CAUSA RAÍZ #1 (clics dobles): three.js (WebXRController.dispatchEvent,
  r170 verificado en el fuente) entrega selectstart/squeezestart por TODOS
  los espacios del mismo inputSource (targetRay, grip, hand). El juego
  registraba selectstart en grip Y targetRay (y squeeze en ambos) → cada
  pulsación entraba DOS veces: toggles 2×=estado original ("parecen
  muertos"), teclado letra×2, hostRoom×2 (teardown destruía la sala que se
  creaba). FIX: listener ÚNICO por evento (select→targetRay,
  squeeze→grip) + guardia temporal 70 ms por mando en onSelectStart
  (_lastSelect).
- CAUSA RAÍZ #2 (espejo vertical): el cursor del panel se pintaba con
  (0.5 - uv.y)*0.35 → coordenada Y invertida respecto al impacto real (el
  hit-testing con (1-uv.y)*640 SÍ era correcto). El usuario apunta con el
  punto → clics en el botón equivocado → percibe "zonas desplazadas" y
  "CREAR SALA no hace nada" (el espejo de los botones cae en zona vacía).
  FIX: dot.position.y = (uv.y - 0.5)*0.35 + descarte de intersecciones
  degeneradas (hit.distance > 0.02).
- HARDENING NetLink: hostRoom ignora si status creating/waiting; joinRoom
  ignora si joining/online (re-entrada imposible por más vías).
- VERIFICACIÓN (verify_v224.py, TODO OK): estáticos (1 listener select
  targetRay / 0 grip; squeeze grip=1/targetRay=0; fórmula del cursor;
  guardias); rayos sintéticos: apuntando a 'mode:match' (arriba) hover+dot
  EXACTOS (±0.004 m, dot.y=+0.097) y a 'close' (abajo) dot.y=-0.113 — sin
  espejo; toggles: entrega duplicada simulada = UNA basculación (amb/voz/
  trail) y la pulsación siguiente restaura; voz persiste (ppxr_voz_v1);
  teclado: net:join abre el teclado y A,B,2,C,D → 'AB2CD' (sin duplicar),
  del → 'AB2C'; crear sala: clic (duplicado incluido) → 'creating' →
  'waiting' con código de 5 (BYVTF) dibujado grande y botón CANCELAR SALA.
  Regresiones: verify_v218 TODO OK (15 botones, saque fácil), verify_v219
  TODO OK (sala FFM6H, protocolo), verify_v220 TODO OK (1 fuente, 2.86 s),
  verify_v222 TODO OK (gate, orientación), verify_v223 TODO OK, test_ai_
  returns exit 0 (12-13/14, varianza del modelo de error). 0 errores página.
- Capturas: captura-v224-cursor.png (punto + borde blanco EXACTAMENTE sobre
  'Cerrar menú' — prueba visual del anti-espejo), captura-v224-menu.png,
  captura-v224-multi.png. Nota técnica: con isPresenting simulado el render
  va por la ruta XR → frames negros; las capturas desactivan isPresenting
  solo para el render.
- BUILD: index.html 2.56 MB (sintaxis OK); ZIP regenerado; README v2.24.

Stage Summary:
- v2.24: el menú es totalmente utilizable — el punto sigue al láser (sin
  espejo), cada clic cuenta UNA vez (casillas vivas, teclado limpio) y
  CREAR SALA muestra el código para invitar a un amigo.
- Pendiente visor: que el usuario pruebe el flujo de dos jugadores
  (crear sala → código → unirse) y confirme dicción v2.23 en el casco.
- Siguiente fase declarada: estética del entorno ("vidilla").

---
Task ID: 28
Agent: Super Z (main agent)
Task: v2.25 — rigor multijugador: jugadores en el mismo lado, audio muerto
en online (voz entre jugadores + sonidos + megafonía del invitado)

Work Log:
- FEEDBACK de la primera partida real online: (1) "el audio no funciona — no
  escucho nuestras voces ni los sonidos de la partida"; (2) "está
  instanciando a los jugadores en el mismo lado de la mesa". El usuario pide
  rigor total en multijugador.
- CAUSA RAÍZ #1 (mismo lado / bolas fantasma): el espejo de 180° en Y
  alrededor del centro de la mesa (involución (x,z)->(-x,-3.2-z)) se
  aplicaba DOS veces: NetLink.tick()/sendHit() emitían con posToNet/
  vecToNet/quatToNet Y los tres puntos de recepción (part3 render de pala
  remota, applyBallStream, drainNetwork) volvían a aplicar posFromNet/
  quatFromNet. Doble involución = identidad: la pala rival se pintaba EXACTO
  donde está la propia y las bolas del rival seguían trayectorias espejadas
  dos veces. FIX: emisión EN CRUDO (rawPos/rawQuat) y espejo UNA sola vez al
  recibir; nuevos helpers NetLink.rawPos/rawQuat/spinFromNet; añadido el
  espejado del SPIN (pseudovector (-x,y,-z)) que antes viajaba crudo.
- CAUSA RAÍZ #2 (perspectiva invertida): applySync aplicaba etiquetas
  host-relativas ('player'=anfitrión) sin remapear: el invitado veía el
  marcador invertido, se creía sacador cuando sacaba el anfitrión (AMBOS
  sostenían y lanzaban la bola: caos total en el arranque de cada punto),
  celebraba los puntos del rival y copiaba mensajes del anfitrión en su
  perspectiva. FIX: applySync remapea por punto de vista (sp<->sa, server
  invertido, ganador invertido), regenera MENSAJES locales y remapea causas
  con NetLink.CAUSE_SWAP (4 pares exactos de Rules, semántica verificada);
  el punto viaja ESTRUCTURADO (y.pt {w,c,rh}) send-once capturado en
  processIntents del anfitrión; el LET viaja como causa neutra (y.rt).
- CAUSA RAÍZ #3 (invitado mudo en megafonía): el invitado no ejecuta el
  árbitro (reglas sombra) así que nunca disparaba announce/chime/fanfarria.
  FIX: applySync genera la megafonía local ("3 a 2, saque para ti"), chime
  ganado/perdido, "ohh" según causa, fanfarria + announce + stats
  (recordMatch) en fin de partido con perspectiva remapeada.
- CAUSA RAÍZ #4 (voz entre jugadores): la llamada WebRTC la iniciaba el
  ANFITRIÓN hacia ROOM_PREFIX+code... ¡su PROPIO peer id! (bucle hacia sí
  mismo; el invitado nunca recibía llamada). FIX: la inicia el INVITADO
  (conoce el código) y el anfitrión responde en peer.on('call'). Además:
  micrófono TEMPRANO en hostRoom/joinRoom (gesto 2D del menú, fuera de VR —
  pedirlo en plena sesión XR cambia la ruta de audio de Android y mataba el
  WebAudio del juego), initVoiceWithCap() con TOPE de 4 s (getUserMedia
  puede colgarse: verificado en el entorno headless) con stream SILENTE de
  respaldo (createMediaStreamDestination) para que la voz del rival llegue
  aunque el micro muera, y kick() de rescate de audio al abrir la sesión y
  al llegar el stream remoto.
- Extra: owner cambia AL INSTANTE en el invitado al recibir un golpeo (sin
  esperar sync) y _pendingHits solo se encola en el anfitrión (fuga de
  memoria eliminada); estado sombra del invitado arranca con server='ai'.
- VERIFICACIÓN (verify_v225.py, TODO OK): estáticos (peer.call solo en rama
  invitado; initVoice temprano x3; rawPos/rawQuat en tick y sendHit;
  spinFromNet en ambas recepciones; guardia de fuga; CAUSE_SWAP). Protocolo
  con cable virtual FakeConn<->FakeConn por fases host/invitado: pose en
  crudo (0.2,1.0,-0.3); golpeo rival (0.3,1.0,-0.3) -> (-0.3,1.0,-2.9) lado
  LEJANO; spin (0.4,1,-0.2)->(-0.4,1,0.2); pala remota z=-2.85 + quat 180°;
  bote del sacador -> side 'player' correcto; punto estructurado send-once;
  marcador sombra 0-1 con chime perdedor; "0 a 1, saque para ti"; causa
  remapeada "doble bote: no llegaste"; derrota con fanfarria false +
  "Partido para tu rival"; voz: llamada al ID de sala con stream (tope 4 s
  disparado con stream silencioso en headless); respuesta anfitrión con
  voiceState 'on'. Regresiones: v218 OK, v219 OK (sección 6 actualizada a la
  nueva semántica de perspectiva), v220 OK, v222 OK, v223 OK, v224 OK,
  test_ai_returns 13/14 (93%). 0 errores de página.
- BUILD: index.html 2,57 MB; ZIP regenerado; README con sección v2.25;
  captura-v225-banco.png.

Stage Summary:
- v2.25: el protocolo multijugador es coherente por primera vez — cada
  jugador en su lado, bolas y efectos en el marco correcto, marcador/saque/
  puntos desde la perspectiva de cada casco, megafonía y sonidos en ambos
  lados y voz entre jugadores con degradación elegante.
- Pendiente visor: repetir la partida online real de dos jugadores y
  confirmar (1) lado de mesa, (2) voz mutua, (3) marcador y megafonía en
  ambos cascos.
- Siguiente fase declarada: estética del entorno ("vidilla").

---
Task ID: 29
Agent: Super Z (main agent)
Task: v2.26 — recomprobación del multijugador (petición expresa) + carteles
oficiales de victoria/derrota con el arte adjuntado por el usuario

Work Log:
- El usuario pidió: (1) nueva comprobación del funcionamiento multijugador,
  (2) sustituir los mensajes y carteles de victoria/derrota por sus imágenes
  (upload/victoria.png, upload/derrota.png — arte "CRAZY PING PONG").
- RECOMPROBACIÓN MULTIJUGADOR: verify_v225.py re-ejecutada COMPLETA sobre la
  build nueva (estáticos + protocolo host/invitado por fases + voz P2P) TODO
  OK; regresiones v218/v219/v220/v222/v223/v224 TODO OK; test_ai_returns
  13/14 (93%, baseline). 0 errores de página en todas.
- CARTELES v2.26:
  * prepare_posters.py: PNG 1536x1024 (1,8 MB c/u) -> JPEG 1024x683 q82
    (~120 KB c/u), aspecto 3:2 exacto del arte.
  * createFanfareBanner (game_part2.js) reescrita: canvas 1024x683 (antes
    1024x512), plano 1,5x1,0 m (antes 1,6x0,8), imágenes incrustadas via
    placeholders __POSTER_WIN_B64__/__POSTER_LOSE_B64__ que build_html.py
    sustituye por data URLs JPEG (HTML autocontenido, 2,57 -> 2,89 MB);
    preload con repintado en onload; chip inferior con marcador final +
    "gatillo: revancha"; panel de respaldo si la imagen tarda (mismo texto).
  * Mensajes de fin de partido alineados con el arte: "¡HAS GANADO! · X-Y ·
    gatillo: revancha" / "¡HAS PERDIDO! · ..." en Rules.update (anfitrión) y
    applySync (invitado, perspectiva remapeada). La megafonía de voz no
    cambia (el banco ya cubre "¡Victoria!" / "Partido para...").
  * Gancho de diagnóstico: createFanfareBanner devuelve también el canvas
    (solo lectura) para los tests.
- verify_v226.py (nueva): estáticos (2 data URLs, mensajes x2 en ambas ramas,
  sin restos de "¡VICTORIA!/DERROTA", plano 3:2, gancho) + headless: fin de
  partido real 11-4 y 6-11 (applyPoint -> update(2.5) -> processIntents),
  mensaje correcto ANTES del intento de logro (el logro pisa el mensaje en
  el HUD: comportamiento existente v2.13), cartel visible con fanfareWin
  correcto, canvas con arte real (franja superior azul dominante: victoria
  48/129/230, derrota 37/83/177), revancha retira el cartel (bucle animate),
  invitado ve "¡HAS PERDIDO! · 5-11" con marcador 5-11, capturas
  captura-v226-victoria.png / captura-v226-derrota.png (14-15% cielo azul).
- BUILD: index.html 2,89 MB; ZIP regenerado (3,26 MB, integridad OK);
  README con sección v2.26.

Stage Summary:
- v2.26: fin de partido con el arte oficial del usuario en 3D (victoria y
  derrota), mensajes coherentes en ambos roles y el multijugador re-verificado
  de punta a punta sobre esta build (todas las suites en verde).
- Pendiente visor: repetir partida online real y confirmar (1) lados, (2)
  voz mutua, (3) megafonía; el cartel nuevo se ve al acabar cualquier modo.
- Siguiente fase declarada: estética del entorno ("vidilla": público, vallas,
  marcas en el suelo, mejor iluminación).

---
Task ID: 30
Agent: Super Z (main agent)
Task: v2.27 — selector de idioma castellano/inglés (todos los textos y TODOS
los audios), revisando el cambio en toda la estructura

Work Log:
- BANCO DE VOZ INGLÉS: descargado modelo Piper en_US-lessac-medium (63 MB,
  HuggingFace); gen_voice_en.py genera 67 átomos con las MISMAS claves que el
  banco español (n0-n90, "y"="to", frases, logros, salas, dificultades) ->
  ogg_en/ (211 KB) + game_voice_en.js (282 KB). Los planes de voz son
  idénticos para ambos bancos (claves compartidas).
- game_i18n.js (NUEVO, carga PRIMERA): diccionario ~160 claves x es/en
  (mensajes del árbitro, causas, anuncios, menú, multijugador, teclado,
  estados de red, marcador 3D, cartel, logros, stats, overlay 2D completo),
  T(clave,{params}), TLang(), setLang() con persistencia localStorage
  'pp_lang' (defecto: castellano) y applyLangDOM() para el overlay.
- game_part1.js: VOICE_FULL/VOICE_ACH POR IDIOMA; voiceNumPlan(lang) (sin 'y'
  en inglés); voicePlan(text) con patrones es/en ("Victory! 11 to 4" ->
  [victoria,n11,a,n4], "3 to 3, serve for you" -> [...]); _voiceBank()
  elige VOICE_B64/VOICE_B64_EN según idioma + reloadVoice() en caliente;
  speechSynthesis de respaldo con u.lang es-ES/en-US; ROOM_THEMES con
  nameKey; ACHIEVEMENTS con nameKey/descKey + getters T().
- game_part2.js: las CAUSAS de punto viajan como CLAVES por la red (dblhit,
  volley, serve_no_own, let, serve_net, own_you/own_opp, dbl_you/dbl_opp,
  back_you/back_opp, serve_net_touch, serve_out, net_stay, wall, out,
  noret_you/noret_opp) — CAUSE_SWAP ahora intercambia claves (perspectiva
  invitado intacta); OHH_CAUSES como Set de claves (sustituye al regex
  /red|fuera|pared/); Rules/applySync generan mensajes con T (perspectiva
  remapeada intacta); oppLabel como CLAVE ('cpu'|'rival'); estados de red
  con T; marcador 3D con T (YOU/CPU/RIVAL, supervivencia) y oppLabel del
  juego; cartel de fin de partido POR IDIOMA (POSTER_SRC es/en con carga
  diferida y langChanged() para repintar; panel de respaldo con T).
- game_part3.js: menú de muñeca 100% T (títulos, modo, dificultad, salas,
  extras, multijugador, teclado, mensajes de clic); selector de idioma
  ES/EN en la fila de pestañas de TODAS las páginas (case 'lang' ->
  setLang + repintado); anuncios (sala, dificultad, bienvenida, rally
  récord, marcador, victoria/derrota) con T; partidas online (conectado,
  saque, desconexión) con T; estados DOM (compatibilidad, arranques, fallos)
  con setStatusKey + re-aplicación en 'pp-lang'; renderStats con stats_line;
  ganchos __T/__TLang/__setLang para pruebas headless.
- build_html.py: overlay 2D con data-i18n/data-i18n-html/data-i18n-ph +
  fila selector (ESPAÑOL/ENGLISH, CSS .langrow) ; PARTS = i18n + 2 bancos de
  voz + part1-3; placeholders __POSTER_*_EN_B64__ (vacío = respaldo sin arte).
- CARTELES INGLESES: editados con IA (image-edit) conservando el arte del
  usuario: YOU WON! / YOU LOST! (1344x768 -> cover 1024x683 JPEG q82, 124/109
  KB). El cartel EN se pinta al cambiar de idioma (y el ES al volver).
- VERIFICACIÓN (verify_v227.py TODO OK): estáticos; por defecto castellano
  (mensaje/anuncio/banco 67 claves); setLang('en') -> mensajes del árbitro
  en inglés ("Point for you! · you didn't return it", "YOU WON! · 11-4 ·
  trigger: rematch"), voicePlan EN correcto, banco de voz cambió, overlay
  re-traducido (ENTER VR / Easy), persistencia pp_lang='en', cartel con arte
  EN (franja azul); invitado EN ("YOU LOST! · 5-11 · trigger: rematch");
  vuelta a castellano en caliente. Capturas: captura-v227-menu-en.png (menú
  VR en inglés), captura-v227-victoria-en.png (cartel YOU WON! + chip
  "11 - 7 · trigger: rematch"), captura-v227-overlay-en.png (overlay).
- REGRESIONES actualizadas a la semántica de claves (patch_v225.py + parches
  en v219/v226: oppLabel clave, remapCause con claves, gancho del cartel):
  v219/v220/v221-v226 TODO OK; v222/v223/v224/v218 TODO OK; IA 13/14.
  0 errores de página en todas.
- BUILD: index.html 3,53 MB; ZIP 3,71 MB (integridad OK); README con sección
  v2.27 (selector, textos, audios, carteles bilingües, protocolo por claves).
- Detalle final: botón ESPAÑOL del overlay (antes CASTELLANO se salía del
  ancho) y re-verificación v227+v226 TODO OK tras el ajuste.

Stage Summary:
- v2.27: el juego está BILINGÜE — selector al inicio (2D) y en el menú de
  muñeca; cambia textos de TODA la estructura y la VOZ del megáfono (banco
  Piper inglés de 67 clips); cartel oficial por idioma; persistente y con
  cambio en caliente dentro y fuera del visor.
- Pendiente visor: probar el selector en el casco y una partida online con
  cada idioma (la voz del megáfono debe sonar en el idioma elegido).
- Siguiente fase declarada: estética del entorno ("vidilla").
---
Task ID: 31
Agent: Super Z (main agent)
Task: v2.28 — nuevo arranque del juego: portada web animada (arte + palas de
idioma + gran botón cartoon + música) y MENÚ PRINCIPAL EN VR como gran panel
flotante con acordeón (petición expresa del usuario)

Work Log:
- ASSETS (prepare_launch_assets.py): Cabecera.png -> hero.jpg 1280px (161 KB)
  + recorte del logo completo para la cabecera del menú (menulogo.jpg 840x388,
  82 KB; el primer recorte en franja 1024x220 cortaba "PING PONG" y se
  descartó); palas de bandera 160x160 PNG (12/18 KB); botones JUGAR/PLAY
  recortados al bbox (~90 KB); star.mp3 (89,7 s, 2 MB) -> star.ogg q2 (929 KB).
- I18N (game_i18n.js): claves nuevas es/en — sec_match/train/surv/crazy/opts,
  btn_start, btn_start_surv, btn_train_go, crazy_msg ("¡Sorpresas pronto..! 🎁"),
  best_surv, online_lbl, train_hint, surv_hint; status_pause reescrito;
  soporte data-i18n-title en applyLangDOM (+ music_title).
- game_part3.js (reescritura del menú):
  * buildMenu: lienzo 512x640 -> 1024x1536; plano 0,28x0,35 -> 0,72x1,08 m;
    imágenes del logo y las palas cargadas desde los data URLs de la portada
    (#padEs/#padEn) con repintado en onload.
  * Cabecera común (drawMenuHeader): franja azul degradada + arte del juego +
    DOS palas de bandera con anillo dorado en la activa (rects lang:es/en).
  * Página principal en ACORDEÓN (menuSec, defecto 'match'): cabeceras
    siempre visibles con chevron y pista (dificultad / récord / sala); solo UNA
    sección abierta; segunda pulsación contrae. JUGAR PARTIDO: REVANCHA (si
    over) + ▶ EMPEZAR PARTIDO + dificultad + bloque ONLINE integrado (crear/
    unirse/estado/voz) + acceso a la página completa; ENTRENAR: ▶ ENTRENAR
    GOLPES (enterCalib); SUPERVIVENCIA: ▶ EMPEZAR + récord; CRAZY: mensaje al
    pulsarla ("¡Sorpresas pronto..! 🎁" + jingle); OPCIONES: salas 2x2 +
    ambiente + megáfono + estela. Cierre inferior fijo + "B · cerrar".
  * multi/join reescalados al panel grande (código a 124 px, teclado 118x86,
    volver al pie); el idioma vive ahora en la cabecera.
  * Anclaje: updateMenu ya NO se cuelga de la muñeca libre — anchorMenu()
    coloca el panel DELANTE de la cabeza (1,08 m, y = cabeza - 0,05, mín.
    0,85) con flotación de 1,8 s (re-ancla en updateMenu mientras dure la
    ventana) y queda fijo en el mundo; sin dependencia del segundo mando.
  * Arranque: onSessionStart abre SOLO el menú (menuSec 'match') y congela el
    saque de la CPU mientras esté abierto (gate en el tick de aiServeTimer);
    onSessionEnd lo cierra. menuClick: casos nuevos sec/start/survgo/traingo;
    'mode:*' retirado (survgo respeta el camino de invitado online).
  * CORRECCIÓN LATENTE: wrapText se USABA desde v2.19 (estado de error de red
    del menú) pero NUNCA estuvo definida — definida a nivel de módulo.
  * Interfaz 2D: portada minimalista; retirados los listeners de la tarjeta
    antigua (agarres, stats, dificultad, salas, amb, train/surv); el gran
    botón (#vrbtn) entra en VR con guardia de compatibilidad; renderPlayBtn()
    intercambia JUGAR/PLAY con el idioma; onXRState pausa/reanuda la música.
- build_html.py: plantilla nueva (título "CRAZY PING PONG"); CSS de portada
  animada (Ken Burns difuminado, haces de luz, 3 bolas flotantes, 6 estrellas,
  hero flotante con glow, palas que se balancean, botón que late y se sacude,
  botón 🔊, pie discreto); script de música no-módulo (primer gesto, loop,
  volumen 0,5, persistencia pp_music, hook window.__ppMusic.pause/resume);
  placeholders nuevos __HERO/PAD_ES/PAD_EN/PLAY_ES/PLAY_EN/MUSIC/MENU_LOGO__
  (el logo también en game_part3.js). index.html 3,53 -> 5,65 MB.
- VERIFICACIÓN (verify_v228.py TODO OK): estáticos (assets incrustados, sin
  restos de la tarjeta antigua); portada (hero, idioma por defecto ES, palas
  activas, JUGAR/PLAY conmuta y persiste, demo+🔊 presentes); menú (1024x1536,
  plano 0,72x1,08, acordeón con UNA sección, contenido contraído, CRAZY con
  mensaje directo, segunda pulsación contrae, EMPEZAR cierra y arranca, gate
  del saque IA congelado/reanudado, multi/join completos, 0 errores de página).
  Capturas: captura-v228-portada-es/en.png + captura-v228-menu-es/en.png.
- REGRESIONES adaptadas a la semántica del acordeón (los clics expanden su
  sección primero; 'mode:*' -> 'survgo'/'start'; 'close' multi -> 'tab:main';
  dimensiones del plano en los helpers de apuntado 1024x1536 / 0,72x1,08;
  ventana de flotación congelada en los tests para que el rayo sea
  determinista): v218 v219 v220 v222 v223 v224 TODO OK (v224 estable en 3
  ejecuciones); v225 (multijugador completo), v226 (carteles), v227 (idioma)
  TODO OK sobre la build final; IA 13/14 (93%, baseline).
- BUGS encontrados por los tests durante el desarrollo: cabecera de sección
  ABIERTA sin feedback de hover (corregido: relleno + tramo blancos al
  apuntar); el bucle 2D orbitaba la cámara entre evaluates y arruinaba las
  capturas (capturas en un solo evaluate); 'survgo' vive en su sección (el
  test lo buscaba en MATCH).
- BUILD: index.html 5,65 MB; ZIP regenerado 5,31 MB (integridad OK); README
  con sección v2.28 (portada, menú, arranque rápido, wrapText).

Stage Summary:
- v2.28: el arranque es un escaparate — portada animada con el arte oficial,
  palas de idioma y un gran botón cartoon que mete en VR de un clic; dentro,
  un menú principal flotante estilo consola (cabecera con el arte + acordeón
  de una sola sección) que te deja jugar con un solo gatillo.
- Pendiente visor: comprobar en la Quest la portada (música, animaciones) y
  el panel grande (legibilidad a 1,08 m, flotación, acordeón, Crazy).
- Siguiente fase declarada: estética del entorno ("vidilla": público, vallas,
  marcas en el suelo, mejor iluminación).

---
Task ID: 32
Agent: Super Z (main agent)
Task: v2.29 — colisión precisa en golpeos rápidos, auditoría a fondo del audio
y música de fondo en la portada + menú VR; cierre de versión y ZIP para
descarga (petición expresa del usuario: "actualiza para poder descargar el zip")

Work Log:
- Implementación v2.29 (sesión previa, presente en game_part1.js /
  game_part3.js / game_i18n.js / build_html.py) y CIERRE en esta sesión:
  verificación completa, README, worklog y regeneración del ZIP.
- COLISIÓN (game_part1.js):
  * paddleHitCooldown 0,24 s por pala: un swing que sobrepasa la bola no
    re-registra contacto fantasma (adiós al "doble golpe" del saque rápido).
  * Barrido pala-bola con base de pala INTERPOLADA dentro del subpaso
    (prevNormal/ipNormal): los cruzamientos a máxima velocidad se detectan en
    el instante justo.
  * paddleVelClamp + ventana de velocidad 45 ms (velInst): mando más ágil en
    smashes y sin velocidades irreales por jitter del tracking.
  * Un solo contacto por subpaso: nunca eventos pala+mesa simultáneos.
- AUDIO:
  * Megáfono desacoplado del ambiente (ya no comparten gate: "if (!this.voice)
    return;" independiente).
  * Hooks de reactivación por sesión XR (__audioHooksSession): rescate del
    AudioContext al abrir/cerrar la sesión inmersiva.
  * Prueba de sonido con AUTO-REPARACIÓN en Opciones (btn_sndtest): la 2ª
    pulsación reconstruye contexto/ganancias/nodos (msg_sndrepair).
- MÚSICA VR: la pista star.ogg (__PP_MUSIC_URL, incrustada UNA vez) suena en
  bucle en la portada y dentro del visor mientras el menú principal está
  abierto; se desvanece al empezar a jugar y vuelve al cerrar el menú;
  preferencia compartida pp_music (portada 🔊 y Opciones → Música).
- VERIFICACIÓN (verify_v229.py, TODO OK): estáticos (cooldown, clamp,
  interpolación, música deduplicada, megáfono libre); física unit vía
  __solverHook — smash con follow-through = EXACTAMENTE 1 evento 'paddle' en
  1,2 s y salida hacia la mesa (vz=-11,10), swing con rotación registra UNA
  vez, 0 eventos pala+mesa simultáneos; audio — contexto 'running',
  setMusicWanted enciende/apaga el bucle, pp_music persiste, prueba de sonido
  repara (2ª pulsación re-vincula); menú — acordeón intacto, Opciones con
  Música y Probar sonido; portada con hero+pista+botón; 0 errores de página.
- REGRESIONES sobre la build final: v224 (menú) TODO OK, v225 (multijugador)
  TODO OK, test_ai_returns 13/14 (93%, baseline).
- BUILD: index.html 5,65 MB (10:22); ZIP regenerado 5,31 MB con
  index.html v2.29 + assets/pala.glb, integridad verificada (unzip -t OK y
  marcadores v2.29 presentes dentro del ZIP); README con sección v2.29.

Stage Summary:
- v2.29: golpeos rápidos bajo control (un impacto, detectado en el instante
  justo, sin fantasmas ni eventos pisados), audio auditado con rescate por
  sesión y auto-reparación manual, y la música del usuario como hilo sonoro
  de portada y menú VR con un solo interruptor.
- ZIP listo para Netlify Drop: download/pingpong-quest3-v2.zip (v2.29).
- Pendiente visor: probar en la Quest el saque rápido (sin doble golpe),
  la prueba de sonido y el comportamiento de la música dentro del menú.
- Siguiente fase declarada: estética del entorno ("vidilla": público, vallas,
  marcas en el suelo, mejor iluminación).

---
Task ID: 33
Agent: Super Z (main agent)
Task: v2.30 — portada sin partida de fondo, fuera la demo y su HUD, fuera el
panel de audio del marcador y fuera las vallas del suelo (petición expresa:
"cero estímulos que desconcentre al jugador")

Work Log:
- PORTADA SIN PARTIDA (game_part3.js): nuevo gate `active = presenting ||
  net.online || window.__pp2DPlay` en el bucle. En 2D (sin visor) el juego
  queda EN PAUSA: sin IA, sin demo, sin física, sin árbitro, sin sonidos ni
  narrador; la bola permanece posada en la mesa y solo corren escena, cámara
  orbital y música. La partida solo existe dentro del visor.
- DEMO RETIRADA: eliminado el bloque del "jugador demo" (demoHit y su
  golpeo), el botón #spectate ("Ver demo en pantalla (sin visor)"), su HUD
  (#hud/#hud-score/#hud-msg/#hud-info + CSS + listeners) y los callbacks 2D
  onScore/onMessage. La maquinaria del saque demo queda solo para el modo de
  pruebas (inaccesible en producción).
- PANEL DE AUDIO FUERA (game_part2/3.js): eliminado createAudioStatus (el
  cartel "♪ audio: OK / reconectando…" bajo el marcador, residuo de debug
  que aparecía en partido/entrenamiento/supervivencia) y su llamada en el
  bucle. El diagnóstico interno del audio (watchdog, kick, rebuild) sigue
  intacto — solo desaparece el estímulo visual.
- VALLAS DEL SUELO FUERA (game_part2.js): eliminada la sección completa de
  vallas publicitarias (7 carteles con mensajes: PING PONG XR, ARENA 480 Hz,
  MAGNUS SPORT, TOPSPIN CLUB, QUEST 3 CUP, EFECTO·SPIN, ITTF ARENA).
- I18N (game_i18n.js): retiradas las claves ov_demo (es/en) y la mención a la
  demo en ov_hint.
- MODO PRUEBAS: window.__pp2DPlay=true reactiva el rally 2D SOLO para tests
  headless; test_ai_returns.py adaptado (usa el flag en vez de #spectate);
  verify_v228.py adaptado (gate del saque IA con el flag); verify_v227.py
  adaptado (comprueba AUSENCIA del botón demo).
- VERIFICACIÓN (verify_v230.py, TODO OK): estáticos (sin #spectate, sin HUD,
  sin ov_demo, sin createAudioStatus/audioStatus, sin vallas, sección
  eliminada); portada inactiva — bola parada (v=0) que NO se mueve en 2,5 s,
  marcador 0-0 constante, 0 sonidos de pala/saque, 0 anuncios/chimes, música
  activa; VR simulado — la CPU saca (2 saques) y hay juego real; modo pruebas
  2D reactiva el rally; menú acordeón intacto; 0 errores de página. Captura
  captura-v230-portada.png.
- REGRESIONES sobre la build final: v224 TODO OK, v225 (multijugador) TODO
  OK, v229 (colisión+audio) TODO OK, v227 (idioma) TODO OK, v228 (arranque)
  TODO OK tras adaptar el gate del saque al modo de pruebas;
  test_ai_returns 11-13/14 entre ejecuciones (varianza del seed salgado;
  baseline 13/14 reproducido).
- BUILD: index.html 5,65 MB; ZIP regenerado 5,31 MB (integridad OK; solo un
  comentario del código menciona #spectate — sin referencias funcionales);
  README con sección v2.30.

Stage Summary:
- v2.30: la portada es un escaparate en calma — arte, cámara orbital y
  música, sin partidas fantasma ni narrador; dentro del visor, el campo está
  limpio: sin panel de audio, sin carteles del suelo; el jugador solo ve lo
  que importa (mesa, bola, marcador y menú).
- ZIP listo para Netlify Drop: download/pingpong-quest3-v2.zip (v2.30).
- Pendiente visor: confirmar en la Quest que la portada queda silenciosa
  (solo música) y que el campo no muestra ningún estímulo extra.
- Siguiente fase declarada: estética del entorno ("vidilla": público, mejor
  iluminación) SIN carteles con mensajes.

---
Task ID: 33
Agent: Super Z (main agent)
Task: v2.31 — Rescate definitivo del audio en VR (Quest: ni música, ni efectos, ni narrador dentro del visor; la háptica sí funcionaba)

Work Log:
- Diagnóstico: el contexto de audio nace fuera de la sesión (tap en la portada) y al entrar en inmersivo la Quest re-asigna la salida; el contexto queda 'running' pero MUDO. Todos los rescates previos (kick/watchdog/tryFreshRunning) solo actuaban si el estado NO era 'running' -> un 'running'-pero-mudo nunca se reemplazaba. Confirmado con diffs git (v2.27→v2.30 no tocaron la ruta XR de audio; el problema venía del arranque v2.28 + política del navegador).
- game_part1.js (GameAudio): nuevo flag vrBound (contexto confirmado dentro del casco); markVRStart(); nudgeSink() con ctx.setSinkId('') (re-apunta la salida al dispositivo vigente sin destruir nada); gestureKick() para gestos XR (re-crea el contexto dentro del gesto si !vrBound aunque el actual esté 'running'); adopt() rearranca música y murmullo al cerrar el contexto viejo; ventana de decisión de tryFreshRunning 600→1200 ms; _loadMusic decodifica UNA sola vez (eliminada la carrera _musicLoading que dejaba la música sin cargar si el contexto cambiaba durante el fetch).
- game_part3.js: enterVR() re-crea el contexto tras setSession DENTRO de la ventana de activación del tap (capa principal); onSessionStart usa markVRStart() + rebind condicional (!vrBound); hooks XR (selectstart/squeezestart/inputsourceschange) y onSelectStart llaman gestureKick(); onSessionEnd resetea vrBound; reintento tardío 3400 ms también si !vrBound.
- build_html.py: cabecera v2.31; rebuild index.html (5,66 MB, sintaxis OK).
- verify_v231.py (nuevo): 32 comprobaciones — estáticos (nuevos métodos, enterVR en-gesto, hooks XR, música single-decode, adopt() rearranca, 1200 ms) + funcionales (gestureKick 2D no recrea; VR simulado recrea y adopta con vrBound=true; throttle evita churn; onSessionEnd limpia; música reutiliza buffer) + regresión portada/menú. TODO OK.
- Regresiones: verify_v229 TODO OK · verify_v230 TODO OK · test_ai_returns 13/14 (baseline).
- ZIP regenerado (5,31 MB, unzip -t OK, marcadores v2.31 dentro) y README actualizado (sección v2.31).

Stage Summary:
- v2.31 cerrada: 4 capas de rescate de audio en VR (contexto en el gesto de solicitud, setSinkId, gestureKick en gestos XR, prueba de sonido manual) + música/murmullo a prueba de swaps de contexto.
- Entregado download/pingpong-quest3-v2.zip (index.html v2.31 + assets/pala.glb).
- Pendiente (deuda): replicación P2P de SFX/voces por DataConnection y spawn host/guest en lados opuestos; siguiente fase declarada: embellecer el entorno (público, vallas decorativas, líneas de suelo, iluminación).

---
Task ID: 34
Agent: Super Z (main agent)
Task: Documento maquetado (PDF + HTML) "Guía sin tecnicismos" de Crazy Ping Pong V2.124: cómo se crean nuevos campeonatos, dónde se prueban y desde dónde se juega al juego final, paso a paso para público no técnico.

Work Log:
- Contexto recuperado: juego CRAZY PING PONG (WebXR, Meta Quest 3); despliegue real vía Netlify Drop + Meta Quest Browser (README v2.31); campeonatos actuales Partido/Entrenamiento/Supervivencia + Crazy en preparación; sistema modular de campeonatos diseñado en la sesión previa (asistente de 7 fases, ciclo de 6 estados, validación previa).
- Ruta PDF skill → Creative Flow (guide/handbook). Leídos SKILL.md, briefs/creative-flow.md, configs/fonts.md.
- Outline de 11 secciones: portada, mapa 3 zonas (Taller/Laboratorio/Estadio), regla de oro, 7 fases de creación, 6 estados, laboratorio de pruebas (paquete → Netlify Drop → Quest 3 → checklist de 8 puntos), estadio (publicar + jugar en Quest 2 minutos), red de seguridad (7 chequeos), chuleta, glosario, contraportada.
- HTML maquetado 720x1020: Baloo 2 + Nunito Sans + Noto Color Emoji, paleta crema/azul #0E2A47/naranja #F97316, tarjetas con break-inside:avoid, stepper de estados, checklist, chuleta con chips, glosario a 2 columnas.
- BUGS resueltos: (1) cover_validate en documento flujo → validar portada standalone (extracción temporal) y corregir solapes reales (título dividido en 2 líneas hermana, gaps 42-44px); (2) Paged.js rompe @font-face (fuentes caían a Liberation) → solución: fuentes base64 data-URI inline + render con --nopaged (Chromium nativo); (3) rutas relativas de woff2 sin prefijo fonts/ corregidas antes de incrustar; (4) strong azul sobre fondo azul oscuro en portada y callouts → blanco/naranja; (5) chips de la chuleta desbordaban → inline-block con wrap; (6) página 14 en blanco por padding-bottom 44px que desbordaba el fragmento → 8px; (7) rayas/puntos medios a inicio de línea ligados con &nbsp;; (8) body background = crema para evitar bandas oscuras al paginar con Paged/Chromium.
- QA final: pdf_qa.py --no-tables PASS completo (sin blanks, sin overflow, fill OK, full-bleed portada, márgenes simétricos, puntuación OK); 0 caracteres U+FFFD; metadatos Title/Author/Subject/Creator establecidos.
- Entregables: download/guia-campeonatos-crazy-pingpong.pdf (14 págs, 1,0 MB) + download/guia-campeonatos-crazy-pingpong.html (autónomo, fuentes incrustadas). Limpieza: download/fonts/ eliminado (innecesario, fuentes inline).

Stage Summary:
- Guía maquetada lista para compartir con personal no técnico: explica con analogías (restaurante, cajas, pasaporte) cómo se crea un campeonato (7 fases asistidas), dónde se prueba (URL privada de pruebas + Quest 3 + lista de comprobación) y dónde se juega (URL definitiva + Meta Quest Browser + ENTRAR EN VR), con chuleta de 1 página y glosario.
- Lecciones técnicas para futuras builds de este proyecto: con html2pdf-next.js, incrustar SIEMPRE las fuentes como data-URI y usar --nopaged para documentos con @font-face propias; validar portadas por separado.
- Pendiente posible: versión imprimible A4 si el usuario la pide.

---
Task ID: 35
Agent: Super Z (main agent)
Task: Entrega de descargas — documentos (PDF/HTML guía), ZIP del juego final V2.124 y ZIP del editor de campeonatos (el Taller), construido y probado de cero.

Work Log:
- Verificación inicial: la guía (guia-campeonatos-crazy-pingpong.pdf, 14 págs + .html autónomo) y el ZIP del juego (pingpong-quest3-v2.zip, build v2.31 = V2.124 del usuario; 16 marcadores v2.31, vrBound/markVRStart dentro, unzip -t OK) estaban íntegros en download/.
- El editor NO existía (solo diseñado en la especificación y descrito en la guía) → construido en esta sesión como app HTML autónoma (vanilla JS, sin dependencias, fuentes Google CDN con fallback): download/editor-campeonatos/index.html (90 KB).
- Fuente en scripts/editor_src/ (head/style/body/app1/app2/app3) + scripts/build_editor.py (ensamblado + sanity de llaves). Bugs de generación corregidos: helper campoArea roto, campo duplicado "premier", emoji pegado en DIFICULTADES.
- Funcionalidad alineada 1:1 con la guía: asistente de 7 fases (Ficha con auto-etiqueta slug, Rival con 3 deslizadores de personalidad y cerebro base, Superpoderes con aviso-consulta al elegir efecto nuevo, Materiales con inventario derivado + generar/aportar ≤600 KB, Pruebas de habilidad, Sala con música propia, Montaje con resumen); ciclo de 6 estados (Borrador→…→Desactivado) con tira de pasaporte; revisión automática de 7 chequeos (caja completa, materiales, etiqueta única contra reservadas y otras cajas, encaje, referencias, intocables, partida de control); diario de bordo (localStorage); plantillas-copia de Partido/Entrenamiento/Supervivencia (originales jamás modificados); autosave + persistencia; export: caja .json, paquete-pruebas-<etiqueta>.zip y paquete-definitivo-<etiqueta>.zip con campeonato.json + LEEME.txt (pasos del Laboratorio/Estadio + checklist de 8 puntos).
- BUGS encontrados y corregidos durante las pruebas con agent-browser: (1) data-ruta de tarjetas repetibles ("sp.0.x") no apuntaba al array real → deepSet escribía en objetos basura y ningún campo de superpoder/reto persistía → rutas "superpoderes.i.x"/"retos.i.x" + saneo de claves viejas; (2) selects con doble listener (input+change) apilaban modales → un solo listener; (3) EOCD del ZIP con tamaño/offset del directorio central intercambiados → ZIP corrupto → corregido; validado con unzip -t + JSON + acentos/emoji UTF-8 vía scripts/test_zip_editor.mjs.
- Verificación agent-browser completa, 0 errores de consola: flujo feliz (crear de cero → 7 fases → revisión OK → «Listo para probar» → checklist 8 puntos → descargas paquete-pruebas-orbita-cero.zip y paquete-definitivo-orbita-cero.zip capturadas), ruta bloqueada (caja a medias → modal que lista fases pendientes 1/2/4/5/6), ruta con fallos (etiqueta reservada «partido» → 2 chequeos en rojo → estado vuelve a preparación → corregido → revisión OK), persistencia tras reload (estado listo + 6 pasos hechos), diario con 6 entradas, duplicar/eliminar en Inicio. Capturas: editor-captura-inicio.png, -fase1.png, -fase7.png.
- Empaquetado: download/editor-campeonatos.zip (index.html en raíz, listo para Netlify Drop, unzip -t OK). README.md con nueva sección «Descargas del proyecto (V2.124)» (tabla de los 6 entregables + el viaje Taller→Laboratorio→Estadio).

Stage Summary:
- Descargas completas en /home/z/my-project/download/: guia-campeonatos-crazy-pingpong.pdf + .html (documentos), pingpong-quest3-v2.zip (juego final V2.124), editor-campeonatos.zip + editor-campeonatos/index.html (el Taller), editor-captura-*.png (vistas), README.md actualizado.
- El editor implementa exactamente lo que promete la guía: 7 fases, 6 estados, revisión de 7 chequeos, plantillas no destructivas y paquetes de pruebas/definitivo con instrucciones para Netlify Drop y la Quest 3.
- Lección técnica: en formularios declarativos con data-ruta, las rutas de colecciones deben nombrar el array real; y probar SIEMPRE el ZIP generado con unzip -t (el EOCD es traicionero).
- Pendiente posible: integrar la carga de campeonato.json en el juego (menú → caja importada), y versión imprimible A4 de la guía si se pide.

---
Task ID: 36
Agent: Super Z (main agent)
Task: Verificación final de integridad y entrega de los archivos de descarga solicitados.

Work Log:
- unzip -t sobre ambos ZIP: sin errores (pingpong-quest3-v2.zip y editor-campeonatos.zip íntegros).
- Marcadores de versión confirmados extrayendo contenido: index.html del juego con 16 ocurrencias v2.31 (build = V2.124 definitiva); editor con título "Crazy Ping Pong · Editor de campeonatos · V2.124".

Stage Summary:
- Descargas confirmadas en /home/z/my-project/download/: guia-campeonatos-crazy-pingpong.pdf (14 págs) + .html, pingpong-quest3-v2.zip (juego V2.124, 5,31 MB), editor-campeonatos.zip (Taller, 26,6 KB). Todo listo para el usuario.
