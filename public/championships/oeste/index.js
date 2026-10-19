/* ============================================================================
 *  CAMPEONATO DEL SALVAJE OESTE — módulo v2 (ANDAMIO «sala de espera»).
 *  ---------------------------------------------------------------------
 *  v2.141 (módulo v48) · LOS CAJONES DEL ORO + PARADAS CON NOMBRE — ajustes
 *      del dueño sobre la v2.140: (1) LINGOTES SOBRE DOS GRANDES CAJONES:
 *      «los lingotes van a caer a ambos lados de la mesa pero cerca del
 *      centro de las ventanas, en el suelo, sobre dos grandes cajones de
 *      madera (podemos usar alguno de los que ya colocamos para destruir,
 *      los que no tienen el dibujo del candado)» — DOS cajones limpios del
 *      artista (cubo1/cubo2) ACHATADOS (el doble de anchos: 0,72 m de
 *      huella —y la mitad de altos: 0,18 m) sobre el suelo del vagón, uno a
 *      cada lado de la mesa CERCA DEL CENTRO DE LAS VENTANAS laterales (z
 *      -1,38 izq · -1,59 der, medidas sobre el arte 2395×864). En su cara
 *      superior se apilan los lingotes: rejilla 3×3 por capa con hueco
 *      uniforme, capas EXACTAS (altura real del GLB + 1,5 mm) y una
 *      PEQUEÑA VARIACIÓN de colocación (±7 mm · ±3 mm · ±1,7° de yaw) para
 *      que «no parezca tan perfecta» — sin solaparse ni meterse unos
 *      dentro de otros (cada robo LIBERA su hueco). (2) PARADAS CON
 *      NOMBRE Y ARTE PROPIO: la voz dirá los nombres de los CARTELES del
 *      artista — parada 1 «Bravos» (PARADA1.png nueva) · parada 2 «GOLD
 *      DUST» (PARADA2.png) · parada 3 «Silver Creek» (PARADA3.png) — en
 *      las llegadas y las salidas de la megafonía (2 átomos nuevos × 2
 *      frases × 2 idiomas; BRAVOS ya sonaba desde v2.140).
 *  v2.140 (módulo v47) · EL VAGÓN A PUNTO — 4 observaciones del dueño en el
 *      casco (etapa 4): (1) BOTES FANTASMA junto a la red: si la bola botaba
 *      en el campo ENEMIGO cerca de la red (z -2,2…-1,6) el bote arkanoi la
 *      secuestraba («viene devuelta al jugador como si rebotase contra algo
 *      invisible»): la frontera zonaZ -2,2 dejaba 60 cm de MESA RIVAL dentro
 *      de la zona del jugador → ahora zonaZ = red (-1,6): el bote gestionado
 *      sólo vive en el campo del JUGADOR y en campo enemigo la bola SIGUE SU
 *      TRAYECTORIA física (si se queda quieta, la recoge el vórtice de
 *      siempre). (2) LINGOTES: pila NUEVA en el SUELO del vagón, a AMBOS
 *      LADOS de la mesa y visible desde la cámara (antes se apilaban sobre
 *      la mesa rival) — capas de 6 lingotes por pila (2×3) que alternan
 *      izquierda/derecha; al completar un plano se apila ENCIMA con la
 *      altura REAL del lingote medida del prototipo GLB (nada de offsets a
 *      ojo): unos PERFECTAMENTE encima de otros, y yaw a 0 al aterrizar.
 *      (3) SUELO del vagón con el TARIMA del dueño (suelo.jpg, mapeo 1:1 al
 *      plano 6,10×7,90) — fuera la arena procedural de v2.111. (4)
 *      MEGAFONÍA DE ESTACIÓN: voz pregrabada (banco Piper del núcleo, vía
 *      announce VR-safe con el chime del megáfono): a la SALIDA «Pasajeros
 *      al tren, partimos hacia…» [destino]; a los 30 s del final del
 *      trayecto «En menos de 25 segundos llegaremos a…» [estación]; al
 *      llegar CON el oro «¡Cargamento de oro a buen recaudo!» + panel
 *      recompensa.png; si faltó oro, panel forajido_robo.png + las RISAS
 *      del forajido (risas_forajido.mp3). Frases i18n es/en (claves
 *      tren_mega_*) con los NOMBRES de las estaciones interpolados.
 *  v2.138 (módulo v46) · TÚNEL A ESCALA — el dueño: «has reducido las
 *      entradas y las salidas pero no la imagen repetida central del
 *      túnel, con lo que esa sigue quedando igual de grande y las otras
 *      pequeñas. Es preciso ponerlas todas al mismo factor». FACTOR ÚNICO
 *      f = 1,8/3,4 = 0,529 en TODO el rig: bocas 1,2 → 1,8 m (los cortes
 *      inferior/superior salen del hueco de la ventana — antes se veía el
 *      corte por abajo) y banda interior 6,0 → 3,176 m con centro
 *      TU.bandaY 2,257 (el centro antiguo 2,65 escalado anclado al centro
 *      de la ventana). Secuencia cosida y fases por distancia intactas.
 *  v2.136 (módulo v45) · EL TÚNEL COMO ANTES + MAPA NUEVO:
 *  (1) TÚNEL: la profundidad de v2.134 (subgrupos inclinados ∓0,24 rad)
 *      ESTROPEÓ las bocas de entrada/salida — viviendo dentro del subgrupo,
 *      el reparto de la textura tunelboca.png (que recorría
 *      tunelGrp.children) dejaba de encontrarlas y los arcos quedaban SIN
 *      arte; la inclinación además las torcía. El dueño: «dejarlas como
 *      antes, solo que más pequeñas para que parezca que están más lejos».
 *      Fix: piezas COPLANARES de nuevo a x 3,55 (sin rotación), bocas
 *      3,4 → 1,2 m centradas en la ventana (caben enteras: portal lejano),
 *      y el reparto de textura ahora usa traverse() — a prueba de futuro.
 *  (2) MAPA DE ETAPAS NUEVO (mapa.png del dueño, 1699×926): medallones
 *      más grandes (nodo 2 SAGEBRUSH, nodo 4 TREN+ORO) → NODOS re-medidos
 *      (los 1/3/5 bajan ~26/36/24 px), tapa 240×248 → 284×292 y anillo
 *      r 95 → 110 para abrazar los medallones nuevos.
 *  v2.134 (módulo v44) · EL TREN A PUNTO — 5 observaciones del dueño en el
 *  casco (etapa 4 «ASALTO AL TREN»):
 *  (1) PARADAS SIN REPETIR: la estación de SALIDA (BRAVOS) lucía PARADA1.png
 *      — la MISMA imagen que la parada 1 — y el jugador veía el arte dos
 *      veces seguidas. Ahora la salida tiene SU arte PARADA0.png (nueva,
 *      con placa «BRAVOS») y las 4 estaciones del trayecto son distintas.
 *  (2) MÁS VEGETACIÓN en la panorámica exterior p1_* (el desierto se veía
 *      escaso): arbustos/cactus del propio artista compuestos sobre el
 *      suelo de arena de las DOS panorámicas con perspectiva, racimos y
 *      bruma de distancia (scripts/make_vegetacion_p1.py).
 *  (3) TÚNEL CON PROFUNDIDAD: las 3 piezas del túnel (boca·banda·boca)
 *      vivían COPLANARES a 0,5 m de la ventana — «muy pegado», sin
 *      perspectiva. Ahora cada pared del túnel se INCLINA hacia fuera
 *      (rotación Y ∓13,7°) y arranca algo más lejos (x 3,55→3,75): la
 *      boca queda junto a la ventana y el interior SE PIERDE a lo lejos —
 *      se ve DENTRO del túnel, no un decorado pegado.
 *  (4) LA PARED DEL FONDO REBOTA: la bola que sobrevuela la pirámide ya no
 *      muere contra el frontal del vagón (z=-5,55) — REBOTA (0,72) y puede
 *      golpear las cajas DESDE ATRÁS, con chispazo y golpe seco de madera.
 *  (5) SUPERPODERES DE VERDAD sobre la mesa: X3 = TRES bolas con TIRO
 *      BALÍSTICO a cajas apiladas reales (izquierda·centro·derecha, el
 *      impacto queda asegurado) y DINAMITA = CADENA: la bola-bomba ya no
 *      muere en la 1.ª detonación — ESTALLA SIEMPRE que toca caja, rebota
 *      y sale CAZANDO la caja viva más cercana (tiro balístico) hasta
 *      agotar TODAS las cajas activas en el momento del poder, con brote
 *      final. (Vigilante anti-atasco: si la bola encadenada se queda sin
 *      camino 3,2 s, re-apunta sola.)
 *  v2.120 (módulo v39) · AUDITORÍA + DOS SUPERPODERES NUEVOS DEL FORAJIDO:
 *  TORMENTA DE ARENA (polvo cálido sobre tu campo + rodantes, 8 s) y
 *  ESTAMPIDA (6 bisontes cruzan el pueblo con polvo/retumbe/vibración,
 *  6,5 s) — bolsa del forajido = 4 (disparo · dinamita · arena · estampida)
 *  y el cartel ¡SUPERPODER! enseña el ICONO del poder (arte nueva).
 *  Auditoría: pool de la bala trazadora, rayo del revólver sin allocs por
 *  frame, recambio de bolas extra del tren, HudOeste.dispose, listener
 *  pp-lang con nombre, _endPower cierra aviso+flancos, diana con arte
 *  tardío re-enganchada. TODO lo demás queda intacto.
 *  v2.121 (módulo v40) · MINIATURAS PARA LOS PODERES CLÁSICOS: disparo y
 *  dinamita estrenan powerdisparo.png y powertnt.png — los CUATRO poderes
 *  lucen SU icono propio en el cartel. Cero cambios de gameplay.
 *  v2.106 (módulo v25) · EL PUEBLO A PUNTO: oleadas de 2 MINUTOS COMPLETOS
 *  (el cupo ya no corta la partida), transición de oleada con FUNDIDO A
 *  NEGRO + cartel + casas rehechas en negro, casas más grandes y separadas
 *  llegando al suelo, línea de casas nueva del artista, costura del
 *  horizonte curada, nubes a la deriva, setos girando bien, estrella del
 *  sheriff con arte nuevo (siempre visible), silueta real en el
 *  desvanecimiento del forajido, corazón impredecible, humo de pistola en
 *  su sitio, bala visible + más sangre + vibración + grito, derrota con
 *  Forajido_lauging → negro → Forajido_victory + risas_pueblo.mp3,
 *  dinamita estática en la mesa y detonable con la bola, y CARTELES
 *  EXPLICATIVOS antes de entrar en cada prueba (compartidos con locura y
 *  magia vía el núcleo: game.showInstrucciones()).
 *  v2.107 · descubierto = 1 s, SANGRE DEL VISOR con salpicadón FIJO
 *  (imagen sin seguimiento del mundo, pose de la cámara XR del frame) y
 *  gotas que escurran en CADA disparo recibido, y carteles con la
 *  estética del oeste que se CIERRAN AL PULSAR EL GATILLO.
 *  v2.110 (módulo v29) · ETAPA 4 con el PARALLAX DEFINITIVO: horizonte
 *  continuo cosido con las dos panorámicas p1_* del artista (la única
 *  tira que va una imagen pegada a la siguiente) y ELEMENTOS sueltos
 *  p2_/p3_/p4_* en cintas aleatorias a AMBOS lados del tren (textura,
 *  escala, profundidad y suelo aleatorios; reciclado con pieza nueva al
 *  salir del cinturón — spawn periódico). Terrenos procedurales P2-P4
 *  quedan NEUTROS (sin adornos pintados: los ponen las piezas).
 *  v2.112 (módulo v31) · POR LAS VENTANAS SÓLO ARTE DEL ARTISTA: fuera
 *  los lienzos de terreno paramétrico (mesetas y arenas pintadas con
 *  puntos) — el desierto lo pinta la panorámica p1_* y las cintas de
 *  piezas van recalibradas (nada de muros de 15 m tapando la ventana) y
 *  más densas. EL VÓRTICE de la bola SÓLO se ve al salir ésta (fundido
 *  de entrada/salida) y la bola sale con un BRINCO ALTO (ápice 1,45 m)
 *  quedando botando SIEMPRE a la misma altura tras cada bote en la zona
 *  del jugador (arkanoi: esperando el golpe cómodo).
 *  v2.113 (módulo v32) · AJUSTES DEL VISOR: (1) el vórtice SUELTA LA
 *  BOLA HACIA EL JUGADOR — deriva de salida hacia +z y cada bote
 *  gestionado apunta a la ZONA CÓMODA (zComoda) donde queda botando al
 *  mismo ápice; (2) la DIANA del jinete ya no falla: radio ampliado y
 *  CUALQUIER impacto en el cuerpo del jinete (plano del arte) mata
 *  durante la ventana de duelo; (3) GRITO «¡YIHAA!» sintetizado al
 *  entrar el forajido (alerta sonora de aproximación); (4) BUG del
 *  HUMO ETERNO resuelto: los cajones que aterrizan quedan ASIENTADOS
 *  y no re-caen cada frame (humo + madera infinitos); (5) SUELO DE
 *  ARENA EXTERIOR a ambos lados del vagón, desplazándose con el mundo;
 *  (6) el ROBO se ve CLARO: el lingote LEVITA 1 m sobre la mesa
 *  GIRANDO EN ROJO y sale disparado por la ventana hacia el jinete
 *  que huye, con ZUMBIDO de escapatoria.
 *  v2.114 (módulo v33) · EL VÓRTICE, A PUNTO: (1) MÁS PEGADO A LA RED —
 *  nace a 30 cm de ella sobre la mesa del jugador (antes al canto de la
 *  mesa, a 1,07 m); (2) LAS BOLAS SALEN CON MÁS FRECUENCIA: recambio tras
 *  morir 1,05 → 0,55 s y bola GASTADA tras entregar golpe en la pirámide
 *  (rebota visible 1,5 s y se retira sola — antes la MISMA bola volvía
 *  una y otra vez con el bote arkanoi y el vórtice casi no reaparecía).
 *  v2.115 (módulo v34) · EL GRAN ESPECTÁCULO DEL VAGÓN: (1) ESTACIONES
 *  DEL ARTISTA — cada parada muestra SU imagen PARADA1/2/3.png (edificio
 *  2:1 con alfa) en vez del andén procedural; (2) LAS PELOTAS NACEN CADA
 *  SEGUNDO — pool multi-bola (máx 6) que nace en el vórtice con la MISMA
 *  física (pala, cajones, arkanoi, gastada); (3) SUPERPODERES en la mesa
 *  rival: medallones circulares (tamaño del vórtice) que aparecen 3 s y
 *  con cadencia mínima de 15 s — POWERCAJAS (lluvia de 5 cajones con
 *  física real que se apilan, máximo 30 y algunos explotan para hacer
 *  sitio), POWERX3 (la bola se convierte en 3 con abanico hacia las
 *  cajas) y POWERDINAMITA (bola-bomba oscura con mecha que revienta el
 *  cajón y TODOS los de su radio); (4) separación 1/4 del tamaño entre
 *  cajones DESDE EL PRINCIPIO (muelle ensanchado a 2,5 m); (5) TÚNEL DEL
 *  ARTISTA en la capa P4: boca tunelboca.png + banda tunel.png repetida
 *  desfilando a velocidad real + boca ESPEJADA a la salida, y la luz de
 *  TODA la escena baja al 20 % dentro (difícil jugar) hasta recuperar.
 *  v2.116 (módulo v35) · BETA1 — CALIBRADO DEL VAGÓN Y EL PUEBLO: (1) las
 *  bolas EXTRA salen del vórtice CADA 4 SEGUNDOS (antes 1 s: demasiado
 *  rápido); (2) el TÚNEL NACE LEJOS (10 m) con fase 'pre' — la boca se
 *  VE LLEGAR con luz normal, entra y la luz cae al 20 %; duración
 *  ampliada para que la boca de SALIDA también se aprecie; (3) EN EL
 *  TÚNEL NO APARECE EL JINETE (desaparece y su agenda se pausa); (4) los
 *  SUPERPODERES están en escena 5 s (antes 3); (5) FÍSICA DE CAJONES:
 *  soportes por POSICIÓN REAL (antes filas lógicas) — nada flota: si lo
 *  que hay debajo revienta o cae, la de encima cae también; (6) EL
 *  PUEBLO: marcador contador.png arriba a la izquierda con los forajidos
 *  que FALTAN por oleada (3/5/7, reparto original recuperado), y la
 *  sangre del visor varía de SITIO en cada disparo (posición y giro del
 *  salpicadón al azar).
 *  v2.117 (módulo v36) · EL PUEBLO, CON LO PEDIDO: (1) MARCADOR REAL —
 *  contador.png DEL ARTISTA (la carta pergamino con el forajido que se
 *  había perdido y se regeneró mal) arriba a la izquierda, con la cuenta
 *  pintada en su zona libre, y JUNTO a él el RELOJ de la oleada
 *  (reloj.png) con el tiempo restante — fuera el reloj central duplicado
 *  en el asedio; (2) LA CASA DEL SHERIFF CORREGIDA: Fachada2/Interior2
 *  nuevos que SÍ LLEGAN AL SUELO (el arte viejo flotaba 33 cm) y línea
 *  verde de zonas2.jpg re-medida (v 0.238 → 0.114); (3) LA ESTRELLA DEL
 *  SHERIFF SE CAZA TAMBIÉN CON EL REVÓLVER (rayo con asistente ×1.5, el
 *  láser se calienta al apuntarle y el disparo se gasta); (4) PARADAS:
 *  mapeo corregido — la parada N muestra SU PARADAn.png (antes un
 *  off-by-one: la 1 mostraba PARADA2 y la 3 PARADA1); (5) TÚNEL QUE SE
 *  VE ENTERO: bocas de 3,4 m centradas en la ventana, banda cosida
 *  borde a borde (sin hueco ni solape) y fases por DISTANCIA.
 *  v2.119 (módulo v38) · CORRECCIONES DEL ARTISTA + RANKING CON SENTIDO:
 *  (1) TÚNEL PARED DERECHA — las bocas tunelboca.png salían «espejadas y
 *  mal»: el cosido va SIEMPRE por el borde u=1 de la textura (el arco
 *  abierto), así que en la derecha los signos se INVIERTEN (entrada
 *  espejada/salida normal) y por las DOS ventanas se ve el mismo túnel
 *  continuo boca→banda→boca; (2) LA PISTOLA DE LA ESTRELLA NO SE COME
 *  LOS REVÓLVERES — al cazar la estrella con ella, el destape monta DOS
 *  revólveres frescos y ya no se gasta uno: hay pistola para el forajido
 *  que aparece; (3) ESTACIONES Y PARALLAX MÁS ALTOS — «sólo vemos el
 *  techo»: PARADA1 0,75→1,85 · PARADA2 1,75→1,95 · PARADA3 1,03→1,85
 *  y los pies del parallax suben (P2 -3,6→-2,2 · P3 -1,7→-0,6 ·
 *  P4 -0,30→0,35); el hueco transparente del arte de PARADA1 se RELLENA
 *  en carga (andén sólido, sin «hueca la parte inferior»); (4) SISTEMA
 *  DE PUNTOS coherente con el RANKING MUNDIAL: forajido +100 · estrella
 *  +150 · oleada +200 · asedio +300 · punto de duelo +25 · duelo +250 ·
 *  cajón +20 · lingote +100 · jinete de la ventana +150 · indio +150 ·
 *  parada +250 · trayecto +300 — persistente, con «+N» dorado flotante,
 *  chip de estrella en el HUD y p: puntos en el ranking; (5) EL INDIO
 *  CABALGANTE (indio1-4.png + indioalcanzado.png): grupos de 1-3
 *  jinetes «ligeramente separados» que aparecen SOLO cuando el forajido
 *  no está (nunca en el túnel), cabalgan hasta la parte media de la
 *  ventana con la MIRILLA siempre encima, sueltan una FLECHA que roba
 *  un lingote (mismo efecto rojo que el forajido) y se marchan; si les
 *  das: indioalcanzado.png 1 s y se desvanecen.
 *  v2.118 (módulo v37) · AJUSTES DEL ARTISTA: (1) NINGÚN TÚNEL CERCA
 *  DE LA ESTACIÓN — el túnel no nace si la parada llega en menos de
 *  30 s (bloquea), se retira en la llegada y espera 12 s tras
 *  arrancar: boca y andén ya no se solapan; (2) BOCAS DEL TÚNEL
 *  CORRECTAS en las DOS paredes: tunelboca.png NORMAL al ENTRAR
 *  (antes la izquierda iba espejada) y ESPEJADA al SALIR (antes la
 *  izquierda iba normal); (3) SUPERPODERES 8 s en escena (antes 5);
 *  (4) ESTACIONES AL SUELO: cada PARADA{n}.png se cota a SU altura
 *  (TREN.estacionY) para que sus raíles/andén asienten en la arena —
 *  PARADA1 bajaba flotando ~1 m y se veía hueca por debajo; (5) HUD
 *  DEL ASEDIO CLARO: progreso corto «OLEADA n/3» (sin duplicar la
 *  cuenta del marcador), mensajes envueltos a 2 líneas con auto-ajuste
 *  de fuente, HUD subido a y 2,52 y cartel de oleada bajado a y 1,38
 *  — ya no se solapan textos ni cartel con banderín; (6) LA ESTRELLA
 *  DEL SHERIFF DA SU PISTOLA: al aparecer, la pala de la mano libre
 *  se cambia por el revólver (sin munición, láser incluido) y al
 *  desaparecer la estrella vuelve la pala.
 *  ---------------------------------------------------------------------
 *  Organización inicial con los assets recibidos del artista (12 poses del
 *  FORAJIDO + mapa + BSO «El Duelo» + risas). El núcleo NO cambia: todo
 *  pasa por los ganchos genéricos de ChampLoader (init/start/leave/update),
 *  el mismo contrato de La Locura y Magia. Un error aquí no tumba el frame
 *  (ChampLoader delega con guard).
 *
 *  QUÉ MUESTRA ESTA v2:
 *   · El FORAJIDO de pie en su sala (pose present → idle, con balanceo
 *     suave de espera), misma composición que el WIZARD en modo sala
 *     (x 1,62 · z -4,50 · base 1,0 m) y el mismo tamaño de sprite.
 *   · ARBUSTO RODANTE delante de él (v2.83): bola de ramas secas que rueda
 *     por el suelo como empujada por el viento — péndulo de ±50 cm partiendo
 *     del centro del personaje (primer tramo 50 cm a un extremo, vuelta de
 *     100 cm al contrario), SIEMPRE rozando el suelo (efecto de película).
 *   · Los 4 TROQUELES de cartón del Oeste (saloon, cactus, carruaje y
 *     cartel de SE BUSCA) con el sistema decor del núcleo (v2.80/81).
 *   · El MAPA de 5 etapas con TAPAS en los nodos pendientes (misma
 *     tapa.webp que los otros campeonatos) y anillo dorado en el nodo 1.
 *   · INSIGNIA del campeonato (convención assets/insignia.png, v2.75) y
 *     pistol.glb copiado a assets/ para el revólver del nivel futuro.
 *   · BSO «El Duelo» en bucle siguiendo el AJUSTE GLOBAL del núcleo
 *     («Música de los campeonatos», pp_arcade_vol) con sincronización en
 *     vivo — el mismo motor v2.78 del mago.
 *
 *  QUÉ AÑADE LA v3 (v2.86) — EL PRIMER DUELO + LOS 2 SUPERPODERES:
 *   · DUELO Nv. 1 contra el FORAJIDO EN PERSONA: partida a 11 con la IA del
 *     núcleo (arquitectura v2.70 del mago — el rival viste el duelo, el
 *     árbitro es el de siempre). El ARBUSTO RODANTE lo acompaña como
 *     «tapador» en la mesa. La SALA DE ESPERA queda intacta: gatillo y a jugar.
 *   · Motor de SUPERPODERES de dos fases (aviso «¡SUPERPODER!» 2 s con la
 *     partida congelada → efecto en pleno rallye), el mismo del CLOWN y el
 *     WIZARD, con los poderes NUEVOS del forajido:
 *     1) DISPARO CERTERO — aparece un REVÓLVER (revolver.glb) al lado de la
 *        pala rival: desenfunde girando sobre sí mismo, apunta a la bola con
 *        trayectoria predictiva y DISPARA una bala trazadora que la impacta:
 *        la bola sale al DOBLE de velocidad con una desviación ligera, se
 *        pone OSCURA (manchada) y suelta chispas. Disparo e impacto suenan
 *        FUERTE, como un duelo.
 *     2) DINAMITA — el forajido LANZA un cartucho (small_tnt.glb) con la
 *        MECHA ENCENDIDA (chispas + bufido) hacia la mesa del jugador.
 *        Se neutraliza GOLPEÁNDOLA con la pala en vuelo (sale despedida y
 *        estalla lejos) o DISPÁRANDLE UNA VEZ toca la mesa (pistola de la
 *        mano libre, la de siempre en otros niveles): 3 s de mecha con
 *        cuenta atrás 3·2·1 y un «bullet time» de 0,85 s al aterrizar. Si
 *        ESTALLA en la mesa, la bola de la jugada se pierde y el punto es
 *        suyo. La explosión suelta HUMO CARTOON y deja un MANCHÓN QUEMADO
 *        que perdura ~6 s y se desvanece.
 *   · PISTOLA del artista (pistol.glb) montada en la mano libre durante el
 *     duelo (misma normalización del mago) + haz de disparo en el RIG.
 *   · Sonidos sintetizados del duelo (Web Audio, banco del núcleo) y las
 *     RISAS reales del forajido al anunciar poderes y reaccionar (v2.54).
 *
 *  QUÉ AÑADE LA v7 (v2.89) — EL DUELO DEL «DISPARO CERTERO» + DINAMITA
 *  IMPOSIBLE DE PERDER:
 *   · DISPARO CERTERO ES AHORA UN DUELO (arte nuevo del artista): el
 *     forajido desenfunda (retrato duelo), la bola se CONGELA, la PALA del
 *     jugador se convierte en el MISMO revólver y aparece una DIANA sobre
 *     su cuerpo (salta entre las 5 zonas de duelo_zonas.jpg). 3 s para
 *     acertar con todos los disparos que queramos: si acertamos, muestra
 *     la pose de la zona alcanzada (Arriba/Alto/Centro/AbajoCentro/Abajo)
 *     y la partida sigue con la bola en SU recorrido original; si fallamos,
 *     el forajido DISPARA (estampido fuerte + humo del cañón) y la bola
 *     retoma el movimiento RE-DIRIGIDA hacia nuestra mesa, MÁS RÁPIDA y
 *     OSCURA. El resto del tiempo la bola es BLANCA (visible en la madera).
 *   · DINAMITA: cartucho con BRILLO PROPIO + HALO aditivo que viaja con él
 *     + LUZ cálida en la mesa — imposible de perder. Al estallar suelta una
 *     CORTINA DE HUMO DENSA que tapa algo la bola durante ~6 s (como el
 *     manchón) y se desvanece.
 *
 *  QUÉ AÑADE LA v8 (v2.90) — PALA SIEMPRE EN MANO, DUELO A PUNTERÍA FINA
 *  Y SALVA DE DINAMITA (indicaciones del artista):
 *   · LA PALA está SIEMPRE en la mano del jugador. La pistola antigua
 *     (pistol.glb) se RETIRA del campeonato: nada de pistola en la mano
 *     libre. El REVÓLVER (revolver.glb, el MISMO modelo que usa el
 *     forajido) SOLO aparece durante el duelo del «Disparo certero»: la
 *     pala desaparece, empuñamos el revólver (misma orientación y escala
 *     que tenía la pistola) y al acabar vuelve la pala.
 *   · MIRA LÁSER CONTINUA durante el duelo: el rayo sale EXACTAMENTE de
 *     la boca del cañón (medida con VÉRTICES reales del modelo) y sigue
 *     el eje del cañón — lo que marca el láser es EXACTAMENTE lo que
 *     dispara (WYSIWYG). El punto se enciende sobre las dianas móviles
 *     del cuerpo del forajido: puntería fina.
 *   · DISPAROS LIBRES durante TODO el duelo (3 s): un tiro cada 0,16 s
 *     hasta acertar en la diana.
 *   · FUERA los contadores 3·2·1: ni sobre la diana ni sobre los
 *     cartuchos de dinamita (solo queda el tic-tac sonoro).
 *   · DINAMITA NUEVA — SALVA DE 2 A 5 CARTUCHOS: el forajido lanza entre
 *     2 y 5 cartuchos a CUALQUIER punto de la mesa, con 1 segundo entre
 *     lanzamiento y lanzamiento, de modo que explotan en momentos
 *     distintos. El ARCO DE LANZAMIENTO nunca supera la altura del techo
 *     (ápice limitado por debajo de los 2,85 m de la sala). La partida
 *     SIGUE normalmente: si la bola pasa por una explosión SALE DESPEDIDA
 *     en una dirección cualquiera. Cartuchos un 33 % MÁS PEQUEÑOS
 *     (0,27 → 0,18 m). Sin «bullet time» ni punto regalado: solo el caos
 *     de las explosiones (y se pueden seguir bateando en el aire).
 *   · pistol.glb ELIMINADO de assets/ (no se usa en este campeonato).
 *
 *  QUÉ AÑADE LA v10 (v2.92) — LOS DOS REVÓLVERES APUNTAN BIEN Y LA SALVA
 *  NO FRENA LA PARTIDA (informe del visor):
 *   · VOLTEO DE LOS DOS REVÓLVERES: el del FORAJIDO (rotación 0 + boca de
 *     caché en -Z) apuntaba a la PARED y el del JUGADOR (boca -Z del grip)
 *     apuntaba AL JUGADOR — «cada una mirando al lado contrario». Ahora
 *     los dos giran 180° en Y: el cañón del forajido ENCARA al jugador y
 *     el del jugador apunta AL CONTRINCANTE. El láser y el disparo siguen
 *     el arte (art.localToWorld con el giro incluido): WYSIWYG intacto.
 *     El muzzle del forajido (fogonazo/humo/bala) pasa a +Z con el volteo
 *     y el desenfundado termina su giro en π.
 *   · SALVA DE DINAMITA SIN TIRONES: cada cartucho POSADO añadía un
 *     PointLight — cambiar el número de luces obliga a Three.js a
 *     recompilar programas de shaders (y cada luz cuesta fragment en la
 *     Quest): la salva se «atropellaba y iba a saltos». FUERA luces: la
 *     brasa la simula el HALO aditivo del cartucho (más grande, naranja y
 *     latiendo). Además: cero asignaciones por frame en el camino caliente
 *     (mecha/láser/beams con temporales de módulo), el BEAM del disparo
 *     pasa a POOL (antes 2 mallas + 2 geos + 2 mats por tiro) y el
 *     tic-tac de mecha se limita globalmente.
 *
 *  QUÉ AÑADE LA v11 (v2.93) — EL REVÓLVER DEL JUGADOR APUNTA AL FORAJIDO,
 *  EL DEL FORAJIDO TE MIRA A TI (A LA CÁMARA) Y LA SANGRE DEL DUELO PERDIDO:
 *   · FIX RAÍZ DEL REVÓLVER DEL JUGADOR (informe del visor: «al sostenerla
 *     apunta al propio jugador»): el espacio GRIP de WebXR apunta hacia
 *     -Z (el núcleo ya lo usa así: el cañón de la pistola ARKANOID vive en
 *     -Z del grip). La v10 garantizó la boca en +Z del grip — justo AL
 *     REVÉS — y por eso el revólver miraba al jugador. Ahora se garantiza
 *     la boca en -Z del grip (volteando el arte SOLO si la medición da
 *     +Z): el cañón apunta AL FORAJIDO. El láser y el disparo siguen el
 *     arte (art.localToWorld con el giro incluido): WYSIWYG intacto.
 *   · EL REVÓLVER DEL FORAJIDO ENCARA A LA CÁMARA VR: durante el margen
 *     del duelo el cañón SIGUE LA CABEZA del jugador (g.camera) con
 *     slerp suave — tú a tú de verdad, como pide el artista. Al disparar
 *     recalcula la boca EXACTA con el encaramiento vigente (la bala sigue
 *     saliendo hacia la bola congelada: mecánica intacta).
 *   · BOCA DEL CAÑÓN EXACTA: se guarda la boca medida por VÉRTICES en la
 *     carga (unidades locales del arte) y se aplica con la ESCALA real de
 *     la malla — se sustituye la heurística del bbox (daba el offset en
 *     unidades equivocadas: fogonazo/humo/bala nacían lejos del cañón).
 *   · SANGRE EN LA PANTALLA (detalle gracioso pedido): si el forajido
 *     GANA el duelo (no acertamos ninguna diana) su disparo NOS SALPICA:
 *     la cámara se llena de GOTAS DE SANGRE pegadas al visor (grupo
 *     bloqueado a la cabeza a 0,5 m) que se ESCURREN hacia abajo dejando
 *     un REGUERO; todo se DESVAYECE en ~10 s y molesta PARCIALMENTE la
 *     visión mientras la partida sigue. 100 % visual: sin colisiones, sin
 *     raycast, pool pre-creado (cero asignaciones por frame) y se limpia
 *     al salir de la sala.
 *
 *  QUÉ AÑADE LA v13 (v2.95) — ASEDIO AL ESCONDITE 2.0 (la prueba 1, rehecha):
 *   · AVENIDA DEL PUEBLO del lejano oeste como escenario de la etapa 2:
 *     fachadas de madera con porches en fila (FUNERARIA · HOTEL de dos
 *     plantas · SALOON · ALMACÉN de dos plantas · BANCO · BARBERÍA, más
 *     iglesia y herrería), calle EMBARRADA con charcos, tablón-porción,
 *     GRAN DEPÓSITO DE AGUA, cactus, montañas ROJIZAS de Arizona, BUITRES
 *     orbitando en el cielo salpicado de nubes y HUESOS de bisonte medio
 *     enterrados a nuestra espalda. Fuera los troqueles de la sala (igual
 *     que en el tren): la sala se ABRE y la avenida manda.
 *   · BOLA-BOMBA NEGRA con la mecha encendida (chispa + bufido) sobre la
 *     mesa: hay que golpearla con la pala hacia el pueblo. Una DIANA (el
 *     arte del artista) se marca en PUERTAS y VENTANAS predefinidas y
 *     CAMBIA DE SITIO SOLA si no la aciertas: 30 s en la oleada 1, 20 s en
 *     la 2 y 10 s en la 3. Recambio automático de bombas.
 *   · ACIERTO: la bomba EXPLOTA (estruendo + astillas), el TROQUEL de esa
 *     fachada desaparece y el FORAJIDO se destapa con su pistola y un
 *     CORAZÓN flotando sobre él — 3 s para rematarlo con el revólver de la
 *     mano libre (mira láser). Si falla la ventana, ÉL DISPARA y deja
 *     MANCHONES DE SANGRE PERMANENTES en el visor que se ACUMULAN toda la
 *     etapa (cada fallo, más herido). 6 forajidos (2 por oleada) · 3 min.
 *
 *  QUÉ AÑADE LA v12 (v2.94) — EL CAMINO COMPLETO: ETAPAS 2 · 3 · 4 · 5
 *  Y EL REVÓLVER DEL JUGADOR CON EL CAÑÓN 5° HACIA ABAJO:
 *   · REVÓLVER MÁS NATURAL (petición del artista: «unos 5 grados apuntando
 *     el cañón hacia abajo»): el revólver EN MANO del jugador se inclina 5°
 *     hacia abajo (art.rotation.x = -5° tras el volteo; Euler XYZ = Rx·Ry:
 *     el picado se aplica sobre la boca YA volteada). Láser y disparo usan
 *     art.localToWorld/worldQuaternion: incluyen el picado — WYSIWYG intacto.
 *   · RUTA COMPLETA DE 5 ETAPAS con PROGRESO (pp_champ_oeste_stage): el
 *     gatillo de la sala lanza la etapa ACTUAL; al superar una etapa se
 *     levanta la TAPA del mapa, el ANILLO dorado salta al nodo siguiente
 *     y el cartel de sala se repinta:
 *      1 DUELO Nv.1 (el de siempre) · 2 ASEDIO AL ESCONDITE ·
 *      3 DUELO Nv.2 (rival duro) · 4 ASALTO AL TREN · 5 DUELO FINAL (JEFE).
 *   · ETAPA 2 «ASEDIO AL ESCONDITE» (bola + revólver, 3 minutos): el
 *     forajido se PARAPETA tras BARRILES y TABLONES al fondo. La COBERTURA
 *     aguanta 3 GOLPES DE BOLA (cada golpe la rompe más: tablones sueltos,
 *     barriles torcidos) y el TERCERO la REVIENTA EN ASTILLAS que saltan
 *     por los aires. Al quedar expuesto se abre una VENTANA de 1,7 s para
 *     DISPARARLE con el revólver de la MANO LIBRE a su PUNTO DÉBIL (el
 *     corazón que brilla sobre su pecho, con mira láser). Si no aciertas
 *     te DISPARA y NOS DEJA MANCHONES DE SANGRE en la pantalla (salpicaduras
 *     fijas que desaparecen en 5 s; cada impacto acumula MÁS manchones —
 *     cada duelo estás más herido) y la cobertura se reconstruye. Recambio
 *     automático de bolas para que el rallye no se pare nunca.
 *   · ETAPA 4 «ASALTO AL TREN» (movimiento y puntería, 3 minutos): la mesa
 *     VIAJA SOBRE UN VAGÓN de plataforma (suelo de tablones, barandillas,
 *     ruedas, enganche) en pleno desierto — la sala se abre: CIELO cálido,
 *     mesetas lejanas, colinas y llano con DESFASE DE PROFUNDIDAD que se
 *     desliza lateralmente (parallax), rieles y traviesas pasando bajo el
 *     vagón, cactus y postes de telégrafo. DELANTE, los vagones llevan
 *     CAJAS FUERTES con CANDADO DORADO (el elemento más brillante) en 3
 *     OLEADAS: repisas fijas a tres alturas → raíles deslizantes →
 *     compuertas que se abren y cierran. ACIERTA CON LA BOLA en el candado
 *     para ABRIR las cajas antes de llegar a la estación: la puerta se
 *     abre, LLUEVE EL BOTÍN (monedas y fajos) y destello dorado. De vez en
 *     cuando suena el SILBATO y llega un TÚNEL: la visión BAJA ~6,5 s (roca
 *     oscura alrededor) y SÓLO BRILLAN LOS CANDADOS. Al abrir las 3
 *     oleadas el tren LLEGA A LA ESTACIÓN (silbato largo + frenado + cartel
 *     «ESTACIÓN BRAVOS»).
 *   · DUELOS Nv.2 y FINAL: el forajido devuelve más (aiMul 1,0 → 1,2 → 1,4)
 *     y sus superpoderes caen MÁS SEGUIDO. Al ganar el DUELO FINAL se gana
 *     el CAMPEONATO: la INSIGNIA del sheriff brilla en la sala, risa
 *     amarga del forajido y registro pp_champ_oeste_champ.
 *   · El REYOLVER DE LA MANO LIBRE (etapa 2): montaje en gunMounts de la
 *     mano libre con la MISMA medición de boca/eje del cañón (WYSIWYG) y
 *     mira láser continua; el gatillo llega vía serveTrigger (el árbitro
 *     duerme en 'champtest') y en escritorio apunta con la cámara.
 *
 *  La lista de detalles vive en manifest.json → «pendientes_artista».
 *  ============================================================================ */
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// v3.6.2-SDK2 · FASE 4 de la modularización P0: kernel compartido de los 5
// campeonatos (championships/sdk/champ_sdk.js). Los 4 motores SFX one-shot
// y los 3 congelados delegan en él (el fix «forma promesa» v2.125 llegó a
// estar copiado 6 veces en este módulo). Desde el SDK v1.2.0 también la
// MÚSICA en bucle (BSO del saloon y vagón) vive en el SDK (createMusic).
import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js';

/* Parámetros de la sala (mismo patrón que MAGIA en el módulo del mago). */
const OESTE = {
  spriteWidth: 1.7,     // ancho del rival BUSTO (mago/locura; alto por aspecto)
  baseY: 1.0,           // base del rival BUSTO en modo sala (misma composición)
  // v2.87 · FORAJIDO DE CUERPO ENTERO: a diferencia del mago y de La Locura
  // (bustos flotantes a baseY 1,0), el arte del forajido (512x1024, vertical)
  // es un PERSONAJE COMPLETO y está pensado para verse con SU proporción
  // original y con los PIES EN EL SUELO. Nada de comprimir: la ALTURA manda
  // (spriteHeight) y el ancho sale del aspecto real de cada pose.
  fullBody: true,
  spriteHeight: 2.15,   // plano de 2,15 m → personaje visible ≈ 1,8 m (pies a 0)
  x: 1.62, z: -4.5,     // posición en la sala (junto al fondo, lado derecho)
  musicVol: 0.15,       // respaldo si el núcleo no está disponible
  // v2.89: bola BLANCA — el artista la pide «blanca para distinguirla sobre
  // la mesa de madera» (el cuero marrón se perdía contra los tablones).
  ballColors: [0xf3eee2, 0xe8dcc0, 0xfff8ea],   // hueso, marfil, blanco
  ballEmissive: 0x181410,   // brillo propio neutro muy tenue (bola blanca)
};
/* Posición del cartel EN MONTAJE: la del panel RANKING del mago (probada:
 * no tapa marcador, rival, mapa ni portal). */
const CARTEL = { x: 1.46, y: 1.12, z: -1.7, rotY: -0.42 };
/* Mapa de etapas: MISMA posición/escala que el WizardMap del mago
 * (-2,98 / 1,5 / -0,9 mirando al centro; arte 1699x926 → mismo aspecto). */
const MAPA = { x: -2.98, y: 1.5, z: -0.9, PW: 1.68 };
/* Nodos de la ruta MEDIDOS sobre el arte oficial del oeste (1699x926;
 * v2.83: el artista reubicó los nodos — NO valen los del mago;
 * v2.136: arte NUEVO del dueño (mapa.png) — medallones más GRANDES
 * (~230-265 px) y los nodos 1/3/5 algo más abajo → centros re-medidos
 * con scripts/mide_nodos.py y verificados con cruces):
 * 1 DUELO Nv. 1 · 2 PRUEBA (SAGEBRUSH) · 3 DUELO Nv. 2 · 4 PRUEBA
 * COMPLEJA (TREN+ORO) · 5 JEFE. */
const NODOS = [
  { x: 198,  y: 367, r: 110, tapa: false },  // 1 · DUELO vs FORAJIDO Nv. 1
  { x: 516,  y: 458, r: 110, tapa: true },   // 2 · PRUEBA de habilidad
  { x: 863,  y: 349, r: 110, tapa: true },   // 3 · DUELO vs FORAJIDO Nv. 2
  { x: 1173, y: 461, r: 110, tapa: true },   // 4 · PRUEBA COMPLEJA
  { x: 1536, y: 293, r: 110, tapa: true },   // 5 · DUELO FINAL Nv. 3 (JEFE)
];
/* Arbusto rodante (v2.83, el «tapador» del forajido): péndulo de ±50 cm
 * partiendo del CENTRO del personaje — primer tramo hasta un extremo
 * (50 cm) y vuelta al contrario (100 cm) —, rodando sobre sí mismo y
 * SIEMPRE rozando el suelo, como en las películas del oeste. */
const ARBUSTO = { x: 1.62, z: -3.70, h: 0.52, amplitud: 0.50, periodo: 7.0 };

/* ============================================================================
 *  v2.86 · DUELO + SUPERPODERES (constantes del forajido).
 *  ============================================================================ */
/* Posición del duelo: la REGLA FIJA del mago probada en partida real
 * (DUEL_X = tableHalfWidth + 0,5 + offset 0,25 ≈ 1,51 · z -3,82) — el
 * forajido viste el duelo desde ahí y el arbusto rueda delante.
 * v2.87: dy=0 — cuerpo entero DE PIE en el suelo, sin elevación del busto. */
const DUELO = { x: 1.51, z: -3.82, dy: 0, arbustoZ: -3.35, aiMul: 1.0 };
/* Motor de dos fases del CLOWN/WIZARD: aviso 2 s congelado → efecto. */
const OESTE_POWER = {
  chance: 0.30,        // probabilidad por bola que viene hacia ti
  cooldown: 13.0,      // s entre superpoderes
  minRallyHits: 1,     // mínimo de golpes del rallye
  warn: 2.0,           // s de aviso con el cartel SUPERPODER
  primer: 8.0,         // s hasta el PRIMER superpoder del duelo
};
/* 1) DISPARO CERTERO v2.89 — EL DUELO: la bola se CONGELA, la PALA del
 * jugador se convierte en el MISMO revólver del forajido y aparece una
 * DIANA sobre el cuerpo del forajido: 3 s para acertar (disparos libres).
 *   · ACIERTO  → el forajido muestra la pose de la zona alcanzada (arte del
 *                artista) y la partida SIGUE con la bola en su recorrido
 *                original (se descongela tal cual estaba).
 *   · FALLO    → pasados los 3 s el forajido DISPARA (estampido fuerte +
 *                humo del cañón): la bola retoma el movimiento desde donde
 *                estaba, RE-DIRIGIDA hacia nuestra mesa, MÁS RÁPIDA y
 *                OSCURA. Después recuperamos la pala y sigue la partida. */
const DISPARO = {
  drawT: 0.72,         // desenfundado girando (s)
  bulletSpeed: 26,     // velocidad de la bala (m/s)
  maxLife: 1.1,        // vida máxima de la bala (s)
  radioImpacto: 0.11,  // radio de impacto bala-bola (m)
  escala: 0.34,        // longitud del revólver (m)
};
/* v2.94 · PICADO del revólver EN MANO del jugador: el artista lo pide «unos
 * 5 grados apuntando el cañón hacia abajo» — gesto natural de duelo. */
const GUN_PITCH = 5 * Math.PI / 180;
/* El DUELO (v2.89): timings y diana. */
const DUELO_P = {
  drawT: 0.70,         // desenfundado del revólver del forajido (s)
  window: 3.0,         // margen para acertar a la diana (s)
  dianaSize: 0.30,     // tamaño visual de la diana (m)
  dianaRadio: 0.17,    // radio de acierto del disparo (m, generoso en VR)
  hopT: 0.95,          // s entre saltos de la diana de zona (m±50 %)
  swayX: 0.12,         // vaivén horizontal de la diana sobre el cuerpo (m)
  boost: 1.85,         // multiplicador de velocidad del disparo del forajido
  poseT: 4.0,          // v2.91: s mostrando la pose de impacto (4 s con temblor + llanto)
  fadeT: 1.0,          // v2.91: fundido final — la pose se oscurece a negro 1 s
                       // y de él va apareciendo la pose normal (retorn suave)
};
/* Las 5 ZONAS del cuerpo del forajido (duelo_zonas.jpg del artista, de la
 * 1 ARRIBA a la 5 ABAJO) con SU pose de impacto: la diana salta entre ellas
 * (siempre sobre el cuerpo) y, al acertar, el forajido muestra la imagen
 * de la zona alcanzada. Alturas sobre el suelo (cuerpo entero de 2,15 m). */
const DUELO_ZONAS = [
  { y: 1.78, pose: 'duelo_arriba' },       // 1 · sombrero/cabeza
  { y: 1.47, pose: 'duelo_alto' },         // 2 · hombros/pecho alto
  { y: 1.14, pose: 'duelo_centro' },       // 3 · pecho/brazos
  { y: 0.80, pose: 'duelo_abajocentro' },  // 4 · cintura/caderas
  { y: 0.42, pose: 'duelo_abajo' },        // 5 · piernas/botas
];
/* Arte NUEVO del artista cargado junto a las poses (v2.89). */
const DUELO_POSES = ['duelo', 'duelo_arriba', 'duelo_alto', 'duelo_centro',
  'duelo_abajocentro', 'duelo_abajo'];
/* 2) DINAMITA v2.90 — SALVA de 2 a 5 cartuchos: lanzamientos separados 1 s
 *    a puntos ALEATORIOS de la mesa, arco SIEMPRE bajo el techo (el ápice
 *    se limita por debajo de la altura de la sala), mecha corta SIN contador
 *    y explosión que DESVÍA la bola si pasa cerca (la partida sigue). */
const DINAMITA = {
  cartMin: 2,          // cartuchos mínimos por salva
  cartMax: 5,          // cartuchos máximos por salva
  intervalo: 1.0,      // s entre lanzamientos (explotan en momentos distintos)
  g: 9.81,             // gravedad (m/s²)
  radio: 0.075,        // radio de colisión del cartucho (m) — v2.90 −33 %
  escala: 0.18,        // tamaño del cartucho (m) — v2.90: 0,27 × 0,67 ≈ 0,18
  mechaT: 2.0,         // s de mecha una vez toca la mesa (SIN contador visual)
  palaRadio: 0.175,    // radio de interceptación pala+cartucho (m)
  bateoVel: 8.5,       // velocidad del bateo de vuelta (m/s)
  bateoSube: 3.0,      // componente vertical del bateo (m/s)
  bateoT: 0.85,        // s hasta estallar en el aire tras el bateo
  marcaT: 6.0,         // vida del manchón quemado (s) — 4,4 fijos + 1,6 de fundido
  apexUp: 0.62,        // altura del ápice del arco SOBRE la mano (m)
  techoMargen: 0.42,   // margen de seguridad bajo el techo (sala: 2,85 m)
  tipDur: 0.42,        // v2.97: s del VOLTEO con bote al tocar la mesa
  tumbaSube: 0.036,    // v2.97: subida del pivote al tumbarse (radio seccion)
  tipMax: 1.47,        // v2.97: angulo medio final del volteo (rad ~ 84 gr)
  blastR: 0.90,        // radio de la onda expansiva (m)
  blastT: 0.60,        // ventana en la que la bola puede salir despedida (s)
};

/* ============================================================================
 *  v2.94 · EL CAMINO COMPLETO — ETAPAS 1..5 (progreso en pp_champ_oeste_stage)
 *  1 DUELO Nv.1 · 2 ASEDIO AL ESCONDITE · 3 DUELO Nv.2 · 4 ASALTO AL TREN ·
 *  5 DUELO FINAL (JEFE). Los tres DUELOS comparten el motor de siempre con
 *  IA y superpoderes MÁS DUROS por nivel. Las dos PRUEBAS son modos propios
 *  (física vía testStep/testActive con stepPhysics del núcleo, patrón magia).
 *  ============================================================================ */
/* Dificultad de CADA duelo: IA del núcleo × aiMul + superpoderes más vivos. */
const DUELO_NV = [
  { aiMul: 1.0, chance: 0.30, cooldown: 13.0, primer: 8.0, warn: 2.0 },   // Nv.1 (siempre igual)
  { aiMul: 1.2, chance: 0.38, cooldown: 11.0, primer: 6.5, warn: 2.0 },   // Nv.2
  { aiMul: 1.4, chance: 0.46, cooldown: 9.0, primer: 5.0, warn: 1.7 },    // FINAL (JEFE)
];

/* ============================================================================
 *  v2.98 · ASEDIO 3.0 — las mecánicas que pide el artista:
 *   · DOS PALAS (una por mano): la bola-bomba se golpea con cualquiera.
 *   · La bola-bomba cae CADA 2 s, BOTa en la MESITA de madera delante del
 *     jugador (adiós mesa de ping pong) y GIRA de manera natural al botar.
 *   · La bomba SIEMPRE EXPLOTA al tocar pared (fachada), suelo, techo o
 *     los límites: misma explosión que la dinamita (estruendo + destello
 *     + chispas + humo).
 *   · Asistente de puntería: si la trayectoria se acerca bastante a la
 *     DIANA, el impacto cuenta (assistR); el revólver perdona casi-
 *     aciertos al CORAZÓN (heartAssist).
 *   · Forajido: ESTÁTICO, mirando al jugador (el sprite le encara), PIES
 *     EN EL SUELO (no flota, aunque su diana sea una ventana) y el
 *     CORAZÓN SOBRE SU PECHO (nunca separado de él).
 *   · Al destaparse el forajido, las DOS PALAS se convierten en
 *     REVÓLVERES (uno por mano, 1 disparo cada uno); al gastarse vuelve
 *     la pala hasta la próxima diana.
 *   · Dianas y decorado COMPLETAMENTE ESTÁTICOS (nada de bailes); fuera
 *     los buitres (pose fija = falso). Cielo con cúpula y montañas 360°.
 *  v2.101 — AJUSTES del artista:
 *   · FUERA el MURO INVISIBLE de la sala (x=±3,05 del núcleo): las dianas
 *     de los edificios extremos eran INALCANZABLES (la bola explotaba
 *     antes de llegar). El asedio juega con ball.ignoreWalls.
 *   · La DIANA se MUDA DE SITIO cada 20 s (polvo + zona libre).
 *   · HUMO bajo la mesita ELIMINADO: la bola aparcada en (0,-10,0)
 *     disparaba el teletransporte de seguridad del núcleo, que emitía un
 *     evento 'floor' fantasma en (0, 0.5, -1.6) → segunda explosión junto
 *     a la mesita. Ahora se aparca en (0,-4,0) y se tragan los eventos
 *     viejos del mismo paso de física.
 *   · Forajido más PEQUEÑO (1,78 → 1,52 m), acorde a las casas.
 *   · v2.102 — ASISTENTE ELÍPTICO en la diana (el drag aéreo dejaba los
 *     tiros 1-1,5 m por debajo de la mirilla: «aciertas y no sale») y la
 *     DINAMITA emite SEÑAL: faro ROJO sobre el tejado de su casa + siseo.
 *   · CARTUCHO DE DINAMITA ESCONDIDO detrás de una casa (al azar por
 *     oleada, el mismo small_tnt.glb de la etapa 1): se VE por los
 *     boquetes; si una bola entra por un agujero y le da → MEDIA CASA por
 *     los aires: ráfaga de explosiones pequeñas próximas, estruendo y los
 *     DOS MANDOS tiemblan. */
/*  v2.103 · ASEDIO 3.2 — DESCUBRIMIENTO CINEMATOGRÁFICO + CASAS MÚLTIPLES
 *   · El forajido DESTAPADO sale como SU IMAGEN (Forajido_duelo) y, acto
 *     seguido, se FUNDE A NEGRO y aparece SU DIBUJO APUNTANDO
 *     (Forajido_focused.png). El CORAZÓN-diana se enciende con el dibujo,
 *     está a MEDIA TALLA (0,30→0,15) y PARPADEA.
 *   · SU REVÓLVER apunta AL JUGADOR: encaro VERIFICADO (se mide la boca del
 *     cañón en el mundo; sólo se gira si apunta mal — el heurístico fijo lo
 *     invertía).
 *   · Al DISPARAR: humo de la boca y BALA trazadora que vuela hasta tu
 *     cara; la sangre y el tirón del mando llegan con la bala.
 *   · CASAS MÚLTIPLES del artista (fachada2-4/interior2-4 con las líneas
 *     verdes de zonas2-4.jpg): 3 casas DIFERENTES por oleada y, cuando
 *     lleguen las 9, las 3 oleadas no repetirán ninguna.
 *   · v2.104: SETOS SECOS RODANTES (regalo.png) cruzando la calle de
 *     DERECHA a IZQUIERDA (entran y se pierden FUERA de campo); tamaños
 *     al azar — CUANTO MÁS PEQUEÑOS, MÁS RÁPIDOS — girando sobre sí
 *     mismos; aparecen cada cierto tiempo al azar para ambientar.
 *   · v2.104: FACHADA TRASERA DESTRUIBLE — un impacto sobre una zona YA
 *     agujereada rompe la zona CORRESPONDIENTE del interior: HUECO REAL
 *     de lado a lado en la vivienda (se ve el horizonte a través).
 *   · v2.104: CASAS 5-7 del artista (capilla, barbería, almacén) con las
 *     líneas verdes de zonas6-7.jpg medidas píxel a píxel. zonas5.jpg NO
 *     llegó (límite de adjuntos): casa 5 con filas PROVISIONALES a ras de
 *     suelo hasta recibir su arte de marcas.
 *   · v2.105: ¡MECÁNICA SORPRESA «LA ESTRELLA DEL SHERIFF»! Cada oleada,
 *     2-3 veces al azar, una ESTRELLA dorada del sheriff (recorte del
 *     emblema del artista) aparece flotando delante de una casa: gira,
 *     brilla, suelta chispas y parpadea antes de irse. Si la aciertas con
 *     una BOMBA el sheriff DESTAPA AL FORAJIDO al instante (revólveres
 *     cargados sin acertar la diana) y te regala +12 s de reloj.
 *   · v2.105: CASAS 8-9 del artista (Saloon Coyote Run y Grand Frontier
 *     Opera House) + zonas5.jpg DEFINITIVA para la capilla: el pool llega
 *     a 9 y las 3 oleadas ya NO repiten NINGUNA casa (3-3-3 del barajado).
 */
const ASEDIO = {
  facadeZ: -4.70,            // plano de las FACHADAS interactivas
  interiorDZ: -0.24,         // el INTERIOR va este DELTAS detrás (se ve por los boquetes)
  outZ: -4.25,               // donde se planta el forajido al DESTAPARSE (la calle)
  dianaDZ: 0.12,             // la diana flota DELANTE de la fachada (siempre visible)
  waveTime: 120.0,           // v2.99: CADA oleada dura 2 minutos
  alarmAt: 20.0,             // v2.99: ALARMA al quedar 20 s de la oleada
  respawnT: 1.0,             // v2.99: bola-bomba nueva CADA 1 SEGUNDO
  perWave: [3, 5, 7],        // v2.116: forajidos por oleada (3 / 5 / 7) —
                             //         el reparto ORIGINAL del artista, que se
                             //         había perdido con el reinicio del sandbox
  shotWindow: 1.0,           // v2.107: el duelo descubierto dura 1 s — pasado,
                             //         DISPARA (ajuste del artista)
  outFocusDelay: 0.10,       // v2.107: SU IMAGEN aguanta este tiempo antes
  outFadeT: 0.15,            //         del fundido (0,15 s por tramo — silueta
                             //         con alfa, sin plano negro). Secuencia
                             //         entera 0,40 s: el corazón se ve ~0,6 s
                             //         dentro de la ventana de 1 s
  dianaR: 0.26,              // radio de acierto de la BOMBA en la diana (m)
  heartR: 0.15,              // v2.103: corazón a MEDIA TALLA y PARPADEANDO
                             //         (su diana vital; el acierto baja con
                             //         él: 0,15 × 1,75 de asistente)
  assistR: 0.38,             // v2.99: asistente redondo (revólver usa heartAssist)
  assistRX: 0.62,            // v2.102: asistente ELÍPTICO de la bomba (medio ancho)
  assistRY: 0.95,            // v2.102: ...y medio ALTO de la onda expansiva
  assistDrop: 0.30,          // v2.102: centro del óvalo BAJO la mirilla (el drag
                             //         comía los tiros: la bola cruzaba la fachada
                             //         1-1,5 m por debajo y «la diana no salía»)
  heartAssist: 1.75,         // el revólver perdona casi-aciertos (× heartR)
  dianaMoveT: 20.0,          // v2.101: la diana CAMBIA DE SITIO cada 20 s
  outH: 1.52,                // v2.101: forajido más pequeño, acorde a las casas
  heartY: 1.08,              // v2.101: corazón en SU pecho (escala nueva)
  gunY: 0.92,                // v2.101: SU revólver a la altura de SU mano
  mesita: { x: 0, z: -0.35, w: 0.95, d: 0.55 }, // mesita de madera
  rowHalf: 5.6,              // media anchura de la calle (m) — v2.106
  facadeH: 3.45,             // altura de impactos de fachada (m)
  killZ: -5.75, sideX: 5.30, backZ: 2.65,   // límites de bola muerta (v2.106:
                             // sideX ampliado: las casas son MÁS GRANDES y
                             // MÁS SEPARADAS — sus dianas exteriores deben
                             // seguir al alcance de la bola)
  /* v2.101 · CARTUCHO DE DINAMITA ESCONDIDO (small_tnt.glb, el de la etapa
   * 1): cada oleada se guarda DETRÁS de una casa (al azar). Se VE por los
   * boquetes; si una bola entra por un agujero y le da, REVIENTA MEDIA
   * CASA: ráfaga de explosiones pequeñas próximas + estruendo + los DOS
   * MANDOS tiemblan. */
  tnt: {
    zDZ: -0.12,              // entre fachada (0) e interior (-0.24)
    passR: 0.24,             // radio del agujero por el que la bola ATRAVIESA
    hitR: 0.55,              // v2.106: radio de acierto de la BOLA en el
                             //         cartucho (0,38: casi imposible — las
                             //         bombas entraban por boquetes altos y
                             //         NUNCA lo tocaban)
    hitH: 1.10,              // v2.106: altura máxima de acierto (se valora el
                             //         paso cerca del cartucho, no sólo a ras)
    revealR: 0.55,           // un boquete a menos de esto LO DESTAPA (aviso)
    halfW: 0.95,             // MEDIA CASA: radio horizontal demolido
    halfH: 1.45,             // MEDIA CASA: altura demolida desde el suelo
    puffs: 9,                // explosiones pequeñas de la ráfaga
    gap: 0.13,               // s entre explosiones de la ráfaga
  },
  /* v2.106 · LOS 3 EDIFICIOS INTERACTIVOS: MÁS GRANDES, MÁS SEPARADOS y
   *  LLEGANDO AL SUELO (petición del artista): w/h suben (2,9→3,3/3,35),
   *  la base se HUNDE 10 cm en la arena (adiós hueco bajo las fachadas y
   *  adiós dinamita visible entre casas y suelo) y los centros pasan de
   *  ±2,75 a ±3,80 — HUECO REAL de ~1 m entre casas (antes 0,15 m: se
   *  tocaban y sus planos coplanares PARPADEABAN). */
  edif: { xs: [-3.80, 0, 3.80], w: 3.3, h: 3.35, y: -0.10,
          holeW: 0.62, chapW: 0.80 },
  /* v2.103 · LAS CASAS DEL PUEBLO (arte del artista): fachada + interior +
   * LÍNEAS VERDES de zonasN.jpg (v/u medidos PÍXEL A PÍXEL sobre cada
   * imagen). Cada PARTIDA reparte 3 casas DIFERENTES por oleada y, cuando
   * artista ya entregó LAS 9 (v2.105): el barajado reparte 3-3-3 y las
   * 3 oleadas NO repiten NINGUNA casa (cada una juega 3 distintas). */
  casas: [
    { fac: 'fachada1.webp', int: 'interior1.webp',
      zonas: [
        { v: 0.722, u0: 0.398, u1: 0.623, n: 3 },   // ático
        { v: 0.456, u0: 0.157, u1: 0.858, n: 4 },   // entreplanta
        { v: 0.098, u0: 0.142, u1: 0.891, n: 4 },   // planta baja
      ] },
    { fac: 'fachada2.webp', int: 'interior2.webp',   // SHERIFF
      zonas: [
        /* v2.117 · ARTE CORREGIDO del artista (Fachada2/Interior2.png): la
         * casa AHORA LLEGA AL SUELO (su contenido baja de v_bottom 0.13 a
         * 0.006 en el mismo encuadre) y la línea verde de zonas2.jpg se
         * REMIDE píxel a píxel sobre el arte nuevo: v 0.238 → 0.114
         * (banda y 894-921 de 1024), u sin cambios (0.100-0.907). */
        { v: 0.114, u0: 0.100, u1: 0.907, n: 4 },   // planta baja (zonas2.jpg)
      ] },
    { fac: 'fachada3.webp', int: 'interior3.webp',
      zonas: [
        { v: 0.574, u0: 0.186, u1: 0.803, n: 3 },   // alta
        { v: 0.128, u0: 0.176, u1: 0.804, n: 3 },   // planta baja
      ] },
    { fac: 'fachada4.webp', int: 'interior4.webp',
      zonas: [
        { v: 0.537, u0: 0.231, u1: 0.765, n: 3 },   // alta
        { v: 0.123, u0: 0.218, u1: 0.776, n: 3 },   // planta baja
      ] },
    /* v2.105 · CASA 5 DEFINITIVA: zonas5.jpg llegó con este lote — la
     * línea verde REAL de la capilla (medida píxel a píxel) sustituye a
     * la fila provisional a ras de suelo de la v2.104. */
    { fac: 'fachada5.webp', int: 'interior5.webp',   // CAPILLA MOONLIT
      zonas: [
        { v: 0.083, u0: 0.181, u1: 0.861, n: 4 },   // planta baja (zonas5.jpg)
      ] },
    { fac: 'fachada6.webp', int: 'interior6.webp',   // BARBERÍA
      zonas: [
        { v: 0.158, u0: 0.190, u1: 0.882, n: 4 },   // porche (zonas6.jpg)
      ] },
    { fac: 'fachada7.webp', int: 'interior7.webp',   // ALMACÉN
      zonas: [
        { v: 0.563, u0: 0.188, u1: 0.784, n: 3 },   // balcón (zonas7.jpg)
        { v: 0.165, u0: 0.112, u1: 0.883, n: 4 },   // planta baja
      ] },
    /* v2.105 · CASAS 8-9 del artista: con ellas el POOL LLEGA A 9 y el
     * reparto 3-3-3 ya NO repite NINGUNA casa entre las 3 oleadas. */
    { fac: 'fachada8.webp', int: 'interior8.webp',   // COYOTE RUN SALOON
      zonas: [
        { v: 0.519, u0: 0.146, u1: 0.877, n: 3 },   // balcón (zonas8.jpg)
        { v: 0.115, u0: 0.171, u1: 0.903, n: 4 },   // porche (zonas8.jpg)
      ] },
    { fac: 'fachada9.webp', int: 'interior9.webp',   // GRAND FRONTIER OPERA
      zonas: [
        { v: 0.494, u0: 0.142, u1: 0.876, n: 3 },   // balcón (zonas9.jpg)
        { v: 0.113, u0: 0.137, u1: 0.888, n: 4 },   // planta baja
      ] },
  ],
  /* v2.106 · LINEA DE CASAS del FONDO (lineapueblo.webp del artista, la
   *  nueva y limpia — sustituye a pueblohorizonte con su alfa roto y su
   *  segunda fila fantasma): MÁS GRANDE (7,2 m) y un poco MÁS ALEJADA.
   *  Aspecto real del arte 2172×724 (w = h × 3.0). */
  pueblo: { z: -23.5, h: 7.2, ar: 3.0 },
  /* v2.99 · CARTEL de oleada (oleada1/2/3 + oleada.mp3): entra por la
   * DERECHA con efecto de velocidad (0,5 s), flota delante con un vaivén
   * ligero (4 s) y sale por la IZQUIERDA (0,5 s). 5 s EN PAUSA. */
  banner: { y: 1.38, z: -2.35, size: 1.42, tIn: 0.5, tFloat: 4.0,
            tOut: 0.5, xIn: 3.4 },   // v2.118: y 1,62→1,38 — el cartel ya NO
                                     // tapa el banderín de mensajes del HUD
  /* v2.104 · SETOS SECOS RODANTES (regalo.png): ambiente del pueblo.
   * Entran por la DERECHA fuera de campo (xIn, en m) y se pierden por la
   * IZQUIERDA rodando a una profundidad al azar entre zMin y zMax (entre
   * el jugador y las casas, sin pisar la mesita ni el tablón). La
   * velocidad sale de la TALLA: v = kVel / h — pequeño = RÁPIDO. Aparecen
   * cada tMin..tMax segundos al azar; pool = simultáneos como máximo. */
  setos: { zMin: -3.40, zMax: -1.40, hMin: 0.26, hMax: 0.72, kVel: 0.68,
           xIn: 7.40, tMin: 3.5, tMax: 9.0, pool: 3 },
  /* v2.105 · ¡LA ESTRELLA DEL SHERIFF! — mecánica sorpresa de la avenida:
   *  2-3 veces por oleada (al azar) una estrella dorada aparece flotando
   *  delante de una casa (vida ~7,5 s; parpadea los 2 últimos). Si la
   *  aciertas con una BOMBA: el sheriff DESTAPA AL FORAJIDO del momento
   *  (revólveres cargados sin acertar la diana) y regala +12 s de reloj.
   *  r = radio generoso de acierto; zDZ la separa de la fachada; t1 la
   *  agenda por 1ª vez y rest las siguientes. */
  estrella: { vida: 7.5, parp: 2.0, r: 0.42, extraT: 12.0,
              yMin: 1.15, yMax: 2.30, zDZ: 0.62, size: 0.46,
              t1Min: 16, t1Max: 36, restMin: 13, restMax: 27 },
};
/* v2.99 · ZONAS VERDES de zonas1.jpg (arte del artista): las únicas líneas
 * donde el forajido puede aparecer DE PIE — ático, entreplanta y planta
 * baja. Coordenadas NORMALIZADAS de la fachada (u: ancho 0..1, v: altura
 * 0..1 desde abajo), medidas píxel a píxel sobre la imagen. */
const AS_ZONAS_UV = [
  { v: 0.722, u0: 0.398, u1: 0.623, n: 3 },  // ático
  { v: 0.456, u0: 0.157, u1: 0.858, n: 4 },  // entreplanta
  { v: 0.098, u0: 0.142, u1: 0.891, n: 4 },  // planta baja
];
/* Temporales de módulo SOLO para esta clase (no pisar los del duelo). */
const _AS_V1 = new THREE.Vector3();
const _AS_V2 = new THREE.Vector3();
const _AS_V3 = new THREE.Vector3();
const _AS_Q = new THREE.Quaternion();   // v2.98: giro natural de la bola
const _AS_V4 = new THREE.Vector3();     // v2.99: encaramiento del revólver
const _AS_V5 = new THREE.Vector3();     // v2.103: bala del forajido (origen)
const _AS_V6 = new THREE.Vector3();     // v2.103: bala del forajido (destino)

/* ETAPA 4 · ASALTO AL TREN — v2.109 EL VAGÓN DE MERCANCÍAS: la mesa viaja
 * DENTRO del vagón cerrado (arte room/vagon/). 3 PARADAS de 2 minutos
 * máximo: el tren nace en la estación, corre el tramo y frena en el andén
 * siguiente. v2.111 «EL BOTÍN DEL TREN»: pirámide ARKANOID de cajones con
 * candados-lingote (5-3-2, gravedad real, reparto aleatorio), la bola sale
 * de un PORTAL sobre la mesa del jugador y el ORO se acumula en la mesa
 * contraria (HUD ligotes.png «X / Y», objetivos 3·5·7) mientras el FORAJIDO
 * GALOPANTE (galope1-3 + galope_ventana*, sprite sheet en bucle) cabalga
 * junto al tren: cruza la ventana, se planta 4 s con la DIANA del artista y
 * roba un lingote si no le das con el revólver. Música propia (vagon.mp3),
 * suelo de ARENA procedural y parallax de 4 PLANOS por las ventanas con los
 * multiplicadores del artista (montañas 0,05 · colinas 0,15 · postes 0,40 ·
 * arbustos 1,00). */
const TREN = {
  safeZ: -4.95,              // (v2.134: sustituido por paredZ para la bola)
  /* v2.134 · PARED DEL FONDO del vagón (el frontal, z=-5,55): la bola
   * REBOTA en ella (restitución 0,72) en vez de morir — así puede golpear
   * las cajas de la pirámide DESDE ATRÁS (petición del dueño). */
  paredZ: -5.55,
  paredRebote: 0.72,         // restitución del rebote en la pared del fondo
  time: 120.0,               // 2 minutos MÁXIMO por parada
  respawnT: 0.55,            // v2.114: recambio de bola tras morir (s) — MÁS FRECUENTE
  introPause: 4.2,           // espera DETENIDO en la estación 1 (s)
  arrivePause: 4.6,          // parada en cada andén (s)
  brakeDist: 13.0,           // distancia de frenado hasta el andén (m)
  vMax: 2.6,                 // crucero (m/s) = velocidad del plano 4 (1,00×)
  accel: 0.55,               // m/s² de arranque
  tunnelFirst: 22.0,         // s hasta el PRIMER túnel
  tunnelEvery: 34.0,         // s entre túneles (± 6 s aleatorio)
  tunnelIn: 1.6,             // s de fundido a oscuridad
  tunnelOut: 1.6,            // s de fundido de salida
  /* v2.117: las fases del túnel ya NO usan relojes (tunnelPre/tunnelDur
   * fuera): avanzan por DISTANCIA del mundo — la secuencia boca → banda
   * → boca espejada queda COSIDA a cualquier velocidad del tren. */
  lockR: 0.135,              // radio de impacto del candado (m)
  /* Parallax del artista: multiplicadores sobre el plano más cercano.
   * v2.112 · SÓLO P1 lleva MALLA (la panorámica cosida p1_*); P2-P4 son
   * ELEMENTOS sueltos (sus lienzos de terreno paramétrico FUERA: el suelo
   * del desierto lo pinta la propia panorámica del artista). dist/mult se
   * conservan para las cintas de piezas y sus velocidades. */
  layers: [
    { mult: 0.05, dist: 140, w: 530, h: 88.4, cy: 9.2, cz: -150, rep: 1.0 },  // P1 horizonte cosido p1_* (v2.112: horizonte en la ventana)
    { mult: 0.15, dist: 70,  w: 130, h: 30,  cy: 3.4,  cz: -51,  rep: 1.6 },  // P2 (sólo cinta)
    { mult: 0.40, dist: 28,  w: 60,  h: 12,  cy: 2.3,  cz: -19.7, rep: 2.0 }, // P3 (sólo cinta)
    { mult: 1.00, dist: 9,   w: 24,  h: 4.2, cy: 1.84, cz: -5.1, rep: 2.5 },  // P4 (sólo cinta)
  ],
  cloudMult: 0.02,           // deriva de las nubes (0,02×)
  /* v2.110 · PARALLAX POR ELEMENTOS (arte real p1_/p2_/p3_/p4_ del artista,
   * 41 PNG en assets/parallax/). P1 = las DOS panorámicas cosidas PUNTO A
   * PUNTO en un único lienzo 4344×524 — son las ÚNICAS que forman un
   * horizonte continuo (una pegada a la siguiente, misma línea de base) y
   * las que MÁS LENTO se mueven (0,05×). P2/P3/P4 = ELEMENTOS sueltos que
   * nacen aleatorios (textura, escala, profundidad y altura) y viajan de
   * DELANTE (-z) hacia DETRÁS (+z) en una cinta por PLANO y LADO: al salir
   * del cinturón se reciclan con nueva pieza — el spawn «cada cierto
   * tiempo» es la propia cinta (un elemento nuevo entra cada gap medio).
   * Distribución aleatoria e independiente en los DOS lados del tren.
   * gaps/bandas calibrados con el cono visible de cada ventana (ojo en
   * z≈0,4 · pared x≈3,05): P4 [-9,0] · P3 [-30,-3] · P2 [-71,-8]. */
  spawn: {
    pano: ['p1_paisajedesierto1.png', 'p1_paisajedesierto2.png'],
    /* v2.112 · Recalibrado contra el HORIZONTE de la panorámica (la línea
     * montañas/desierto se ve por la ventana a la altura del ojo ~1,4 m):
     * piezas proporcionadas (nada de muros de 15 m tapando la ventana),
     * bases cerca de esa línea y MÁS DENSO (el desierto ya no tiene
     * terreno paramétrico detrás: sólo arte del artista + cielo). */
    planes: [
      { key: 'p2', n: 9, h: 6.0, feet: -2.2, jitF: 0.9, jitD: 8,
        gapMin: 9, gapMax: 16, bandFront: -80, bandBack: 20,
        files: ['p2_rancho1.png', 'p2_rancho2.png', 'p2_rancho3.png', 'p2_rancho4.png',
          'p2_estructura1.png', 'p2_estructura2.png', 'p2_estructura3.png',
          'p2_estructura4.png', 'p2_estructura5.png', 'p2_roca1.png', 'p2_roca2.png',
          'p2_roca3.png', 'p2_roca4.png', 'p2_roca5.png', 'p2_roca6.png',
          'p2_poste1.png', 'p2_poste2.png'] },
      { key: 'p3', n: 9, h: 4.2, feet: -0.6, jitF: 0.5, jitD: 3.5,
        gapMin: 4.5, gapMax: 8, bandFront: -45, bandBack: 16,
        files: ['p3_arbusto1.png', 'p3_arbusto2.png', 'p3_arbusto3.png',
          'p3_arbusto4.png', 'p3_arbusto5.png', 'p3_arbusto6.png', 'p3_arbusto7.png',
          'p3_arbusto8.png', 'p3_arbusto9.png', 'p3_poste1.png', 'p3_poste2.png'] },
      { key: 'p4', n: 10, h: 2.1, feet: 0.35, jitF: 0.25, jitD: 1.1,
        gapMin: 2.2, gapMax: 4.2, bandFront: -17, bandBack: 9,
        files: ['p4_cactus1.png', 'p4_cactus2.png', 'p4_cambio.png', 'p4_caseta.png',
          'p4_poste1.png', 'p4_roca1.png', 'p4_roca2.png', 'p4_senal.png',
          'p4_senal2.png', 'p4_valla.png', 'p4_valla2.png'] },
    ],
  },
  stationX: 4.75,            // centro del andén respecto al eje (m)
  /* v2.119 · ALTURA del ARTE de cada estación — SUBIDAS (petición del
   * artista: «las estaciones… sólo vemos el techo, se deben subir para
   * verlo mejor»). El ojo real en la Quest queda por DEBAJO del centro de
   * la ventana (y 1,08-2,55) y la banda visible sobre el plano del andén
   * (x 4,75) arranca en y≈1,0-1,6: con PARADA1 a 0,75 y PARADA3 a 1,03
   * sólo asomaba la azotea. Ahora el CUERPO del edificio llena la ventana
   * (arte 8,4×4,2 · centro 1,85-1,95 → edificio en y 0,6-3,5) y los
   * raíles/hueco quedan bajo la banda visible.
   * v2.134 · la estación de SALIDA (0, BRAVOS) cota SU arte PARADA0. */
  estacionY: { 0: 1.85, 1: 1.85, 2: 1.95, 3: 1.85 },
  /* v2.141 · LOS NOMBRES DE LOS CARTELES DEL ARTISTA: parada 1 «Bravos»
   * (PARADA1.png nueva) · parada 2 «GOLD DUST» · parada 3 «Silver Creek» —
   * «Estos son los nombres que deberá decir la voz en las llegadas y las
   * salidas». El índice 0 es el DEPÓSITO de salida (PARADA0.png). */
  stationNames: ['BRAVOS', 'BRAVOS', 'GOLD DUST', 'SILVER CREEK'],

  /* ======================================================================
   *  v2.111 · EL BOTÍN DEL TREN — pirámide ARKANOID de cajones + LINGOTES.
   *  Cada PARADA (2 min) exige un mínimo de lingotes: 3 · 5 · 7. La pelota
   *  sale de un PORTAL (portals.webp, el arte del wizard) sobre la mesa del
   *  jugador y golpea los CANDADOS de la pirámide 5-3-2 apoyada en un
   *  muelle de madera junto al frontal. Cajón con candado = 1 lingote que
   *  vuela en PARÁBOLA hasta la mesa del rival y se acumula en pila. Cajones
   *  con GRAVEDAD: si pierden el apoyo, caen. Pirámide nueva al vaciarla.
   *  ====================================================================== */
  meta: [3, 5, 7],           // lingotes exigidos por parada
  /* v2.112 · EL BOTE DEL VÓRTICE: la bola sale del portal con un brinco
   * ALTO (ápice 1,45 m sobre el suelo, cómodo para golpear) y VUELVE A
   * SUBIR SIEMPRE hasta el MISMO ápice tras cada bote en la zona del
   * jugador (mesa o suelo) — arkanoi: la bola queda botando a una misma
   * altura esperando el golpe. comp compensa el roz del núcleo. */
  bote: {
    apex: 1.45,              // ápice constante del bote (m sobre el suelo)
    comp: 1.045,             // compensación del roz del núcleo
    /* v2.140 · SÓLO el campo del JUGADOR (la red está en z=-1,6): antes el
     * umbral -2,2 dejaba 60 cm de mesa RIVAL dentro de la zona y los botes
     * ahí se «devolvían solos» al jugador (botes fantasma junto a la red). */
    zonaZ: -1.6,
    vMaxH: 5.5,              // |v horizontal| máx para normalizar (vuelos rápidos no)
    exitVz: 0.95,            // v2.113: SUELTA LA BOLA HACIA EL JUGADOR (+z)
    zComoda: 1.05,           // v2.113: zona de reposo del bote (a su alcance)
  },
  /* v2.114 · EL VÓRTICE MÁS PEGADO A LA RED: nace a zRed metros de la red
   * (tableCenterZ) hacia el jugador — antes estaba al canto de la mesa
   * (a 1,07 m de la red) y ahora se ve ARRIMADO a ella. */
  vortice: { zRed: 0.30 },
  /* v2.116 · LAS PELOTAS SALEN CADA 4 SEGUNDOS: antes (v2.115) nacía una
   * EXTRA cada segundo y el vórtice escupía bolas sin tregua. spawner de
   * bolas EXTRA que nacen en el vórtice con la MISMA física (pala,
   * cajones, bote arkanoi, gastada tras cajón). max = simultáneas
   * contando la principal. */
  bolas: { cada: 4.0, max: 6 },
  /* v2.115 · SUPERPODERES del tren: medallones circulares (tamaño similar
   * al vórtice) sobre la MESA RIVAL, repartidos al azar. v2.116: están en
   * escena 5 s (antes 3) para dar tiempo a verlos y apuntarlos; nueva
   * aparición 15 s como MÍNIMO después. Al impactar la bola: powercajas
   * (lluvia de cajones) / powerx3 (triple bola) / powerdinamita
   * (bola-bomba que revienta el cajón y su alrededor). */
  poder: {
    vida: 8.0,             // v2.118: s en escena (8 s, petición del artista)
    size: 0.54,            // diámetro = el del anillo del vórtice
    trigoR: 0.30,          // radio de activación (bola rozando el medallón)
    alto: 0.20,            // la bola activa a baja altura (y < topY + alto)
    x: 0.45,               // media anchura de reparto (media mesa rival)
    zMin: -2.78, zMax: -1.85,   // mitad rival, sin pisar la red ni la pila
    t1Min: 8, t1Max: 14,        // primer poder (s de parada)
    restMin: 15, restMax: 24,   // cadencia MÍNIMA 15 s
    pLingote: 0.30,        // prob. de candado en las cajas de la lluvia
  },
  /* v2.115 · LLUVIA DE CAJONES (powercajas): n cajas caen ENCIMA de la
   * pirámide con física real (colisionan con las existentes, se apilan o
   * caen al suelo del vagón). Máximo max CAJONES: si no caben, algunos
   * viejos EXPLOTAN para hacer sitio a las nuevas. landY = cima máxima. */
  lluvia: { n: 5, max: 30, y0: 2.5, x: 0.85, zJit: 0.09, landY: 2.1 },
  /* v2.115 · TÚNEL del artista (capa P4): boca (tunelboca.png) + banda
   * interior (tunel.png repetida) desfilando a velocidad REAL del mundo
   * (1,00×) y boca ESPEJADA a la salida. La luz de toda la escena baja al
   * 20 % (oscuro 0,80) y se recupera al salir.
   * v2.117 · SE VE TODO: las bocas pasan de 6 m (sólo se veía una franja
   * de rocas por la ventana, y leía como «más banda») a 3,4 m CENTRADAS
   * EN LA VENTANA (y 1,08-2,55) — boca → banda COSIDA sin hueco → boca
   * espejada — y las fases cambian por DISTANCIA (sincronía exacta con
   * la velocidad real del mundo, no por reloj). */
  tunel: {
    /* v2.138 · TODAS LAS PIEZAS AL MISMO FACTOR — el dueño: «has reducido
     * las entradas y las salidas pero no la imagen repetida central del
     * túnel… es preciso ponerlas todas al mismo factor» y las bocas «han
     * quedado muy pequeñas… ser algo mayores para que no se vean los
     * cortes por abajo de la ventana (quizás unos 1,8 metros)». FACTOR
     * ÚNICO f = 1,8/3,4 = 0,529 aplicado a TODO el rig: BOCAS
     * (tunelboca.png) 1,2 → 1,8 m — sus cortes inferior/superior (0,9 y
     * 2,7) salen del hueco de la ventana (y 1,08-2,55): ya no se ve
     * NINGÚN corte — y BANDA interior (tunel.png repetida) 6,0 → 3,176 m
     * con centro bandaY 2,65 → 2,257 (escala del centro antiguo anclada
     * al CENTRO de la ventana: la franja visible del arte conserva su
     * centro — 36 % de la altura del arte — y la banda sigue cubriendo la
     * ventana entera sin cortes). La secuencia boca→banda→boca sigue
     * COSIDA (todo se deriva de bh/len), copias sale de la MISMA regla
     * (len/(h×2,35) → 4) y las fases por DISTANCIA intactas.
     * v2.136 · DE VUELTA AL TÚNEL COPLANAR: la profundidad de v2.134
     * (subgrupos inclinados ∓0,24 rad) ESTROPEÓ las bocas — al vivir
     * dentro del subgrupo, el reparto de texturas (que mira
     * tunelGrp.children) dejaba de encontrarlas y los arcos de
     * tunelboca.png desaparecían; además la inclinación las torcía. Las
     * 3 piezas vuelven a ser COPLANARES a x 3,55. */
    x: 3.55,               // pared del túnel (justo fuera de la ventana)
    h: 3.176,              // v2.138: BANDA 6,0 × f (m) — mismo factor que las bocas
    bh: 1.8,               // v2.138: BOCAS 1,8 m (petición del dueño) — sin cortes
    bocaY: 1.8,            // centro de las bocas (centro de la ventana)
    bandaY: 2.257,         // v2.138: centro de la banda (escala del 2,65 antiguo
                           // anclada al centro de la ventana 1,815)
    len: 26.4,             // banda ENTRE bocas, cosida sin hueco (m)
    zIn: -12.0,            // la boca NACE LEJOS (12 m) y se VE LLEGAR
    ojo: 0.4,              // z del ojo del jugador (aprox)
    ver: 3.0,              // la boca de SALIDA enciende la luz al asomar (m)
    oscuro: 0.80,          // opacidad de la caja de oscuridad (luz 20 %)
    /* v2.118 · NO TÚNEL CERCA DE LA ESTACIÓN: si la parada llega en menos
     * de este tiempo (s de reloj de parada), el túnel NO NACE — la boca y
     * el andén se solapaban (túnel 3º con tunnelEvery 34×0,82≈27,9 s
     * empezaba ~2 s antes de _llegaEstacion). El túnel entero dura ~20 s
     * a crucero: 30 s de margen lo deja terminar ANTES de frenar. */
    bloquea: 30.0,
  },
  cubo: {
    size: 0.36,              // arista del cajón (m)
    sep: 1.25,               // v2.115: separación horizontal = size×1,25 (hueco 1/4)
    z: -4.62,                // centro del muelle (contra el frontal)
    peanaH: 0.55,            // altura del muelle de madera (m) — saca la base
    peanaW: 2.50, peanaD: 0.92,   // v2.115: muelle ANCHO (pirámide separada)
    minLingote: 2, maxLingote: 3, // cajones con candado-lingote por pirámide
    respawn: 1.15,           // s hasta la pirámide siguiente
    hitBoost: 0.035,         // generosidad del impacto (m)
  },
  /* v2.141 · LOS CAJONES DEL ORO — dos cajones limpios del artista (los
   * de destruir SIN candado) ACHATADOS: el doble de anchos (0,72 m de
   * huella) y la mitad de altos (0,18 m) que un cajón de la pirámide
   * (0,36). Uno a CADA LADO de la mesa, CERCA DEL CENTRO DE LAS VENTANAS
   * laterales (centros medidos sobre el arte 2395×864: izquierda u=0,472
   * → z -1,38 · derecha u=0,501 → z -1,59). En su cara superior (y = h)
   * se apilan los lingotes en rejilla 3×3 con capas EXACTAS y una
   * PEQUEÑA VARIACIÓN (jX/jZ/yaw) «para que no parezca tan perfecta» —
   * con holguras que NUNCA llegan a solapar (lingote 0,17×0,08). */
  cajonOro: {
    w: 0.72, h: 0.18, d: 0.36,   // doble de ancho · mitad de alto (cajón 0,36)
    x: 1.35,                     // entre la mesa (x ±0,76) y la pared (±3,05)
    zIzq: -1.38, zDer: -1.59,    // centro de la ventana izquierda / derecha
    sepX: 0.19, sepZ: 0.095,     // rejilla 3×3 (lingote 0,17×0,08 + holgura)
    jX: 0.007, jZ: 0.003, yaw: 0.03,   // pequeñas variaciones de colocación
  },
  forajido: {
    total: 10,               // ~10 apariciones por trayecto
    h: 1.62,                 // altura del caballo con jinete (m)
    yBase: 1.38,             // centro del plano: cascos ~0,57 y jinete en la ventana
    xOut: 3.72,              // distancia del plano al eje (fuera de la pared)
    zAtk: -1.82,             // centro de la ventana (medido en el arte)
    zIn: 1.4, zOut: -5.45,   // entra detrás de la pared, sale tras el frontal
    vPaso: 3.3,              // m/s de galope (adelanta al tren: 2,6)
    atkT: 4.0,               // s a la altura de la ventana
    heridoT: 1.0,            // s de la imagen herida
    fadeT: 0.55,             // s de fundido a negro
    loopT: 0.22,             // s por frame del galope
    nextMin: 6.0, nextMax: 14.0,  // s entre apariciones (aleatorio)
    dianaSize: 0.30,         // v2.113: diana algo mayor (m)
    dianaR: 0.23,            // v2.113: radio de acierto generoso (media diagonal + margen)
    cuerpoK: 0.85,           // v2.113: fracción del plano del jinete que mata
    bobA: 0.05, bobW: 10.5,  // rebote del galope
  },
  /* ======================================================================
   *  v2.119 · EL INDIO CABALGANTE (indio1-4.png, UN estado de cabalgada)
   *  Sale por el EXTERIOR cuando el forajido NO está en pantalla: cabalga
   *  hasta la PARTE MEDIA de la ventana, dispara una FLECHA para robar un
   *  lingote (mismo efecto sobre el oro que el disparo del forajido) y se
   *  marcha. SIEMPRE lleva la mirilla encima (diana fija mientras vuela).
   *  Si le das: indioalcanzado.png 1 s y se DESVANECE. Pueden venir en
   *  GRUPOS de hasta 3, ligeramente separados (cada uno roba lo suyo).
   *  ====================================================================== */
  indio: {
    total: 6,                // grupos máximos por trayecto
    grupoMax: 3,             // hasta 3 jinetes por grupo
    sepZ: 0.95,              // separación longitudinal del grupo (m)
    h: 1.70,                 // altura del plano (arte cuadrado 512x512)
    yBase: 1.75,             // CENTRO en la parte media de la ventana (1,08-2,55)
    xOut: 3.72,              // misma calle que el forajido
    zAtk: -1.82,             // centro de la ventana (líder; el resto detrás)
    zIn: 1.4, zOut: -5.45,
    vPaso: 3.3,
    atkT: 3.2,               // s en la ventana antes de soltar la flecha
    alcanzadoT: 1.0,         // s de indioalcanzado.png
    fadeT: 0.55,
    loopT: 0.22,             // s por frame de cabalgada (4 frames)
    nextMin: 9.0, nextMax: 18.0,  // s entre grupos
    dianaSize: 0.30,
    dianaR: 0.23,
    cuerpoK: 0.85,
    bobA: 0.05, bobW: 10.5,
    flechaT: 0.5,            // s de vuelo de la flecha hasta tu cara
  },
};

/* Los 12 ESTADOS del forajido (contrato del manifest.json). «angry» sustituye
 * a «hungry» del payaso: cada rival tiene SU abanico. */
const STATES = ['present', 'idle', 'focused', 'surprised', 'angry', 'panic',
  'laughing', 'defeated', 'victory', 'crazy', 'picando', 'loosing'];

/* v2.110 · CACHÉ DEL PARALLAX POR ELEMENTOS — a nivel de MÓDULO: la etapa se
 * reconstruye al rejugar y así las 38 texturas del artista se decodifican UNA
 * sola vez por sesión. `texs[p2|p3|p4][file]` = { tex, mat, ready, aspect };
 * `fit` = piezas esperando el aspecto real de su textura; `panoDone` = las
 * dos panorámicas P1 ya cosidas. */
const PX = { texs: {}, fit: [], panoDone: false };
function pxMat(key, file, ld, A, aniso) {
  PX.texs[key] = PX.texs[key] || {};
  let e = PX.texs[key][file];
  if (!e) {
    const tex = ld.load(A('parallax/' + file), (t) => {
      e.ready = true;
      try { e.aspect = t.image.width / t.image.height || 1; } catch (err) { /* */ }
    }, undefined, () => { e.ready = true; /* fallo: pieza invisible */ });
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = aniso || 4;
    tex.wrapS = THREE.ClampToEdgeWrapping;
    tex.wrapT = THREE.ClampToEdgeWrapping;
    e = PX.texs[key][file] = {
      tex, ready: false, aspect: 1,
      mat: new THREE.MeshBasicMaterial({ map: tex, alphaTest: 0.5, fog: false }),
    };
  }
  return e;
}
/* Geometría UNITARIA compartida por todas las piezas (escala por mesh). */
const PX_GEO = new THREE.PlaneGeometry(1, 1);

/* v2.111 · CACHÉ del GALOPE del forajido — los 10 PNG del artista en
 * assets/galope/ (galope1-3 = perfil de paso · galope_ventana1-3 = de frente
 * en la ventana · *_dispara = apuntando · galope_herido = abatido).
 * Materiales OPACOS con alphaTest (pase opaco, recorte exacto del PNG,
 * sin orden de transparencias — la misma receta que el parallax). */
const FJ = { texs: {} };
function fjMat(file, ld, A, aniso) {
  let e = FJ.texs[file];
  if (!e) {
    const tex = ld.load(A('galope/' + file), (t) => {
      e.ready = true;
      try { e.aspect = t.image.width / t.image.height || 1; } catch (err) { /* */ }
    }, undefined, () => { e.ready = true; });
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = aniso || 4;
    e = FJ.texs[file] = {
      tex, ready: false, aspect: 1,
      mat: new THREE.MeshBasicMaterial({
        map: tex, alphaTest: 0.5, fog: false, side: THREE.DoubleSide,
      }),
    };
  }
  return e;
}

/* v2.119 · CACHÉ del GALOPE DEL INDIO — indio1-4.png (UN estado de
 * cabalgada, sprite sheet por imágenes como el forajido) e
 * indioalcanzado.png (al darle con el revólver). Misma receta OPACA con
 * alphaTest que el parallax y el forajido. */
const IND = { texs: {} };
function indMat(file, ld, A, aniso) {
  let e = IND.texs[file];
  if (!e) {
    const tex = ld.load(A(file), (t) => {
      e.ready = true;
      try { e.aspect = t.image.width / t.image.height || 1; } catch (err) { /* */ }
    }, undefined, () => { e.ready = true; });
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = aniso || 4;
    e = IND.texs[file] = {
      tex, ready: false, aspect: 1,
      mat: new THREE.MeshBasicMaterial({
        map: tex, alphaTest: 0.5, fog: false, side: THREE.DoubleSide,
      }),
    };
  }
  return e;
}

/* v2.111 · CACHÉ de los CUBOS de la pirámide (cubos/ del artista: cubo1-3
 * neutros · cubolingote1-2 con candado dorado · cubolingoteabierto1-2
 * abiertos). MeshStandard para que las luces del vagón los bañen. */
const CB = { texs: {} };
function cuboMat(file, ld, A, aniso) {
  let e = CB.texs[file];
  if (!e) {
    const tex = ld.load(A('cubos/' + file));
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = aniso || 4;
    e = CB.texs[file] = {
      tex, mat: new THREE.MeshStandardMaterial({
        map: tex, roughness: 0.85, metalness: 0.02,
      }),
    };
  }
  return e.mat;
}

let CTRL = null;
let _ppLangFnO = null;   // v2.120: handler con nombre (no apilar listeners)
let GAME = null;
let STATE_NAME = 'champtest';
let TL = 'es';

/* ------------------------------ utilidades -------------------------------- */
function oesteCanvas(w, h) { const cv = document.createElement('canvas'); cv.width = w; cv.height = h; return cv; }
function tx(k, params) {
  const L = TXT[TL] || TXT.es;
  let s = (L && L[k]) || (TXT.es && TXT.es[k]) || k;
  /* v2.94: interpolación de parámetros (patrón magia: «{n}/{m}»). */
  if (params) {
    for (const pk of Object.keys(params)) {
      s = s.split('{' + pk + '}').join(String(params[pk]));
    }
  }
  return s;
}
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
function ODIMS() { return (window.__PP_CORE && window.__PP_CORE.DIMS) || null; }

/* v2.108 · MODO DEPURACIÓN («foro3d»): el núcleo publica window.__PP_DEBUG
 * cuando el nombre del jugador es foro3d. Con él, el mapa de la sala
 * levanta TODAS las tapas y el gatillo salta a CUALQUIER etapa (1–5) sin
 * requisitos de progreso (revisión directa del creador; el progreso real
 * se conserva vía _replayReal). El núcleo, además, no persiste registros
 * ni publica rankings ni telemetría de este jugador. */
function ppDbg() {
  try { return typeof window !== 'undefined' && !!window.__PP_DEBUG; } catch { return false; }
}
/* v2.94 · Física del NÚCLEO para las PRUEBAS (patrón magia): stepPhysics +
 * colisionador extra corre a 480 Hz dentro del integrador (anti-túnel). */
// v3.6.2-SDK2: el puente al núcleo vive en el SDK (getCore) — una sola fuente.
const __CORE = getCore() || {};
const stepPhysics = __CORE.stepPhysics;

/* v2.92 · TEMPORALES de módulo para el CAMINO CALIENTE por frame (chispas
 *  de mecha, láser, beams): antes cada llamada asignaba Vector3 nuevos y
 *  en salvas de 5 cartuchos a 72 Hz el GC pegaba tirones («va a saltos»).
 *  Sólo se pasan a consumidores que COPIAN (position.copy, etc.), nunca
 *  se retienen. */
const _OE_V1 = new THREE.Vector3();
const _OE_V2 = new THREE.Vector3();
const _OE_V3 = new THREE.Vector3();
/* v2.93 · Temporales extra del encaramiento a cámara del forajido. */
const _OE_M4 = new THREE.Matrix4();
const _OE_Q1 = new THREE.Quaternion();
const _OE_UP = new THREE.Vector3(0, 1, 0);
const _OE_ZERO = new THREE.Vector3();

/* Textos del andamio (castellano + inglés incrustados, patrón del módulo). */
const TXT = {
  es: {
    cartel_t1: 'CAMPEONATO DEL',
    cartel_t2: 'SALVAJE OESTE',
    cartel_st: 'EN MONTAJE',
    cartel_sub: 'El forajido ya está en su sala…',
    plan: 'PLAN DE LA RUTA',
    e1: '1 · DUELO vs FORAJIDO Nv. 1',
    e2: '2 · ASEDIO AL ESCONDITE',
    e3: '3 · DUELO vs FORAJIDO Nv. 2',
    e4: '4 · ASALTO AL TREN',
    e5: '5 · DUELO FINAL · Nv. 3 (JEFE)',
    falta: 'Cinco etapas te separan de la estrella…',
    duelo_ribbon: 'DUELO 1 · ¡GATILLO!',
    duelo_ribbon2: 'DUELO 2 · ¡GATILLO!',
    duelo_ribbon3: 'DUELO FINAL · ¡GATILLO!',
    duelo_sub: 'El forajido te espera en la mesa…',
    duelo_up: 'DUELO vs FORAJIDO · a 11 puntos · ¡suerte, forastero!',
    duelo_up2: 'DUELO 2 · el forajido devuelve más fuerte…',
    duelo_up3: 'DUELO FINAL · todo o nada, forastero…',
    duelo_gana: '¡HAS SUPERADO EL DUELO 1!',
    duelo_gana2: '¡HAS SUPERADO EL DUELO 2!',
    duelo_gana3: '¡HAS SUPERADO EL DUELO FINAL!',
    duelo_pierde: 'El forajido gana… gatillo para la revancha',
    duelo_pierde2: 'Demasiado rápido… gatillo para la revancha',
    duelo_pierde3: 'El forajido resiste… ¡gatillo para el FINAL!',
    etapa_hecho: '¡ETAPA SUPERADA! El mapa se destapa…',
    // v2.96 · REJUGAR etapas superadas (apuntar con la pala al mapa)
    replay_ribbon: 'REJUGAR ETAPA {n} · ¡GATILLO!',
    replay_up: 'REJUGANDO LA ETAPA {n} · ¡suerte, forastero!',
    replay_done: '¡REJUGADA SUPERADA! El camino sigue igual…',
    replay_hint: 'Apunta con la pala a una etapa superada y dispara para rejugarla',
    // v3.6.18 (ronda 24 · POST-CAMPEÓN): RUTA LEYENDA — siendo campeón,
    // cada rejugada es una etapa LEYENDA (más dura) y sella el camino 5/5.
    leyenda_on: '¡RUTA LEYENDA! Rejuega las 5 etapas: cada una sella tu leyenda (5/5)',
    leyenda_ribbon: 'RUTA LEYENDA · ETAPA {n} · ¡GATILLO!',
    leyenda_up: '¡ETAPA {n} DE LEYENDA! El Oeste va en serio…',
    leyenda_sello: '¡SELLO DE LEYENDA {n}/5! El Oeste te va temiendo…',
    leyenda_cstat: 'Sellos de leyenda: {n}/5',
    leyenda_completa: '★ LEYENDA DEL OESTE ★ · camino sellado 5/5 en modo leyenda',
    leyenda_medalla_titulo: '¡LEYENDA DEL OESTE!',
    leyenda_medalla_msg: '5/5 sellos · tu nombre ya es canción de cantina',
    coronacion_titulo: '¡CAMPEÓN DEL SALVAJE OESTE!',
    coronacion_msg: 'El forajido entrega su estrella: el Oeste es TUYO, sheriff',
    coronacion_pts: 'Puntos',
    coronacion_duelos: 'Duelos ganados',
    coronacion_fecha: 'Coronado',
    champ_gana: '¡¡CAMPEÓN DEL SALVAJE OESTE!! ¡La estrella es tuya!',
    champ_sub: 'El forajido se rinde: insignia ganada con honor',
    // ETAPA 2 · ASEDIO (v2.95 · el escondite del pueblo)
    asedio_up: 'ASEDIO AL ESCONDITE · revienta las FACHADAS con las BOMBAS y remata con los REVÓLVERES',
    asedio_diana: '¡DIANA! ¡FORAJIDO A LA VISTA! ¡DISPÁRALE AL CORAZÓN!',
    asedio_muere: '¡BUEN DISPARO! Forajido abatido ({n} de {m})',
    asedio_oleada: '¡OLEADA {n} de 3! ¡Acaba con {m} forajidos en 2 minutos!',
    asedio_alarma: '¡20 SEGUNDOS! ¡DALE CON TODO!',
    asedio_te_da: '¡TE HA DISPARADO! Manchones de sangre…',
    asedio_tnt: '¡DINAMITA! ¡MEDIA CASA POR LOS AIRES!',
    asedio_estrella: '¡ESTRELLA DEL SHERIFF! ¡DALE CON UNA BOMBA O CON EL REVÓLVER!',
    asedio_estrella_ok: '¡LA ESTRELLA SEÑALA AL FORAJIDO! ¡+{n} s!',
    asedio_estrella_solo: '¡ESTRELLA DEL SHERIFF! ¡+{n} s!',
    asedio_gana: '¡EL ESCONDITE HA CAÍDO! ¡Doce forajidos menos!',
    asedio_falla: 'EL TIEMPO SE ACABÓ… el escondite resiste',
    // v2.106 · CARTEL EXPLICATIVO antes de entrar en cada prueba
    instr_asedio_t: 'ASEDIO AL ESCONDITE',
    instr_asedio: [
      'Golpea con las PALAS las bolas-bomba hacia las FACHADAS del pueblo.',
      'Cada IMPACTO rompe la madera; acierta en la DIANA con faro dorado para DESTAPAR al forajido escondido.',
      'Cuando salga, DISPÁRALE AL CORAZÓN con el revólver de la mano libre… pero corre: te disparará en 1 segundo.',
      'Caza la ESTRELLA DEL SHERIFF con una bomba o con el revólver: destapa al forajido y regala +12 s de reloj.',
      '3 OLEADAS de 2 minutos. Cuidado con la DINAMITA escondida: dale con una bola y salta por los aires.',
    ],
    instr_tren_t: 'ASALTO AL TREN',
    instr_tren: [
      'Cada PARADA dura 2 minutos: consigue los lingotes de oro que pide el objetivo (3 · 5 · 7) y consérvalos hasta llegar a la estación.',
      'La pelota sale del PORTAL de tu mesa: golpea los CANDADOS de la pirámide de cajones. Cada cajón con candado esconde UN lingote.',
      'El lingote sale disparado en parábola y se apila SOBRE LOS GRANDES CAJONES de madera junto a las ventanas, a ambos lados de la mesa. ¡Ojo!: el FORAJIDO galopa junto al tren y aparece de vez en cuando.',
      'Si se planta a la altura de tu ventana, apunta con el REVÓLVER de la mano libre y acierta la DIANA en 4 s; si falla… te roba un lingote.',
    ],
    // ETAPA 4 · TREN
    tren_up: 'Guarda el ORO del tren: abre los candados de los cajones y llega a la estación con el botín',
    tren_llega: '¡ESTACIÓN! El tren se detiene…',
    tren_sale: '¡El tren ARRANCA! Parada {n} de 3 · objetivo: {m} lingotes',
    tren_lingote: '¡LINGOTE AL CAJÓN! ({n}/{m})',
    tren_objetivo: '¡OBJETIVO CUBIERTO ({n}/{m})! Consérvalo hasta la estación',
    tren_ok: '¡PARADA CUMPLIDA! El oro llega entero a la estación…',
    tren_piramide: '¡PIRÁMIDE NUEVA! Más cajones a la vista',
    tren_pcajas: '¡SUPERPODER! ¡LLUVIA DE CAJONES!',
    tren_px3: '¡SUPERPODER! ¡TRIPLE BOLA!',
    tren_pdina: '¡SUPERPODER! ¡BOLA DE DINAMITA!',
    tren_forajido: '¡FORAJIDO EN LA VENTANA! ¡DISPARA A LA DIANA!',
    tren_herido: '¡BIEN HECHO, FORASTERO! Forajido abatido',
    tren_robo: '¡EL FORAJIDO TE HA ROBADO UN LINGOTE!',
    tren_indio: '¡INDIOS! ¡DERÍBALOS O TE ROBARÁN EL ORO CON SUS FLECHAS!',
    tren_indio_ok: '¡INDIO ALCANZADO! Se desvanece…',
    tren_tunel: '¡SILBATO! Túnel a la vista… SÓLO BRILLAN LOS CANDADOS',
    tren_estacion: '¡ESTACIÓN ALCANZADA! Botín completo, forastero',
    tren_falla: 'SIN EL ORO SUFICIENTE… la parada se pierde',
    // v2.140 · MEGAFONÍA de las estaciones (voz del banco del núcleo; los
    // {e} son los NOMBRES de las paradas — el texto normalizado debe
    // coincidir EXACTO con las claves VOICE_FULL de game.html)
    tren_mega_salida: 'Pasajeros al tren, partimos hacia {e}',
    tren_mega_llega: 'En menos de 25 segundos llegaremos a {e}',
    tren_mega_oro: 'Cargamento de oro a buen recaudo',
    msg_guest: 'El duelo es en solitario (sin conexión)',
    pw_warn: '¡SUPERPODER DE FORAJIDO!',
    pw_disparo: '¡DUELO! Acierta a la diana en 3 s · la bola está congelada',
    pw_arena: '¡TORMENTA DE ARENA! Polvo y rodantes en tu campo · apártalos de la vista',
    pw_estampida: '¡ESTAMPIDA! La manada cruza el pueblo · no te despistes',
    duelo_acierta: '¡DIANA! La partida sigue tal cual · buen disparo',
    duelo_falla: '¡DISPARO DEL FORAJIDO! Bola más rápida y OSCURA',
    pw_dinamita: '¡DINAMITA! Golpea los cartuchos en el aire · cuidado con las explosiones',
    dyn_mesa: '¡DINAMITA EN LA MESA! Que no te alcance la explosión',
    dyn_desvia: '¡BOOM! ¡La bola sale despedida!',
    dyn_bateada: '¡La has mandado de vuelta! ¡Bien golpeada!',
    dyn_boom: '¡BOOM! La dinamita ha estallado…',
    msg_enter: 'El Salvaje Oeste llega pronto… ¡la sala ya es del FORAJIDO!',
  },
  en: {
    cartel_t1: 'WILD WEST',
    cartel_t2: 'CHAMPIONSHIP',
    cartel_st: 'UNDER CONSTRUCTION',
    cartel_sub: 'The outlaw is already in his room…',
    plan: 'ROUTE PLAN',
    e1: '1 · DUEL vs OUTLAW Lv. 1',
    e2: '2 · SIEGE OF THE HIDEOUT',
    e3: '3 · DUEL vs OUTLAW Lv. 2',
    e4: '4 · TRAIN ASSAULT',
    e5: '5 · FINAL DUEL · Lv. 3 (BOSS)',
    falta: 'Five stages keep you from the star…',
    duelo_ribbon: 'DUEL 1 · TRIGGER!',
    duelo_ribbon2: 'DUEL 2 · TRIGGER!',
    duelo_ribbon3: 'FINAL DUEL · TRIGGER!',
    duelo_sub: 'The outlaw awaits you at the table…',
    duelo_up: 'DUEL vs OUTLAW · first to 11 · good luck, stranger!',
    duelo_up2: 'DUEL 2 · the outlaw hits back harder…',
    duelo_up3: 'FINAL DUEL · all or nothing, stranger…',
    duelo_gana: 'DUEL 1 SURVIVED!',
    duelo_gana2: 'DUEL 2 SURVIVED!',
    duelo_gana3: 'FINAL DUEL SURVIVED!',
    duelo_pierde: 'The outlaw wins… trigger for a rematch',
    duelo_pierde2: 'Too fast for you… trigger for a rematch',
    duelo_pierde3: 'The outlaw holds… trigger for the FINAL!',
    etapa_hecho: 'STAGE CLEARED! The map unfolds…',
    // v2.96 · REPLAY cleared stages (aim the paddle at the map)
    replay_ribbon: 'REPLAY STAGE {n} · TRIGGER!',
    replay_up: 'REPLAYING STAGE {n} · good luck, stranger!',
    replay_done: 'REPLAY CLEARED! The route stays as it was…',
    replay_hint: 'Aim the paddle at a cleared stage and pull the trigger to replay it',
    // v3.6.18 (ronda 24 · POST-CHAMPION): LEGEND ROUTE
    leyenda_on: 'LEGEND ROUTE! Replay all 5 stages: each one seals your legend (5/5)',
    leyenda_ribbon: 'LEGEND ROUTE · STAGE {n} · TRIGGER!',
    leyenda_up: 'LEGEND STAGE {n}! The West means business…',
    leyenda_sello: 'LEGEND SEAL {n}/5! The West is starting to fear you…',
    leyenda_cstat: 'Legend seals: {n}/5',
    leyenda_completa: '★ WEST LEGEND ★ · route sealed 5/5 in legend mode',
    leyenda_medalla_titulo: 'WEST LEGEND!',
    leyenda_medalla_msg: '5/5 seals · your name is already a saloon song',
    coronacion_titulo: 'WILD WEST CHAMPION!',
    coronacion_msg: 'The outlaw hands over his star: the West is YOURS, sheriff',
    coronacion_pts: 'Points',
    coronacion_duelos: 'Duels won',
    coronacion_fecha: 'Crowned',
    champ_gana: 'WILD WEST CHAMPION!! The star is yours!',
    champ_sub: 'The outlaw surrenders: badge earned with honor',
    // ETAPA 2 · SIEGE
    asedio_up: 'SIEGE OF THE HIDEOUT · blast the FACADES with the BOMBS, finish with the REVOLVERS',
    asedio_diana: 'TARGET HIT! OUTLAW SPOTTED! SHOOT THE HEART!',
    asedio_muere: 'NICE SHOT! Outlaw down ({n} of {m})',
    asedio_oleada: 'WAVE {n} of 3! Take out {m} outlaws in 2 minutes!',
    asedio_alarma: '20 SECONDS! FIRE AT WILL!',
    asedio_te_da: 'HE SHOT YOU! Blood stains…',
    asedio_tnt: 'DYNAMITE! HALF THE HOUSE BLEW UP!',
    asedio_estrella: 'SHERIFF STAR! HIT IT WITH A BOMB OR THE REVOLVER!',
    asedio_estrella_ok: 'THE STAR POINTS THE OUTLAW OUT! +{n} s!',
    asedio_estrella_solo: 'SHERIFF STAR! +{n} s!',
    asedio_gana: 'THE HIDEOUT HAS FALLEN! Twelve outlaws down!',
    asedio_falla: 'TIME IS UP… the hideout holds',
    // v2.106 · instruction poster before each test
    instr_asedio_t: 'SIEGE OF THE HIDEOUT',
    instr_asedio: [
      'Swing your PADDLES to hit the bomb-balls at the town FACADES.',
      'Each hit breaks the wood; hit the golden-beacon TARGET to flush the hidden outlaw out.',
      'When he steps out, SHOOT THE HEART with your free-hand revolver… hurry: he fires back in 2 seconds.',
      'Hunt the SHERIFF STAR with a bomb or the revolver: it flushes the outlaw out and grants +12 s on the clock.',
      '3 WAVES of 2 minutes. Watch out for the hidden DYNAMITE: hit it and it all blows up.',
    ],
    instr_tren_t: 'TRAIN ASSAULT',
    instr_tren: [
      'Each STOP lasts 2 minutes: collect the gold ingots the goal asks for (3 · 5 · 7) and keep them until the station.',
      'The ball comes out of the PORTAL on your table side: hit the LOCKS of the crate pyramid. Every padlock crate hides ONE ingot.',
      'The ingot flies in an arc and piles up on the BIG WOODEN CRATES by the windows, at both sides of the table. Careful!: the OUTLAW rides along the train and shows up now and then.',
      'If he stops at your window height, aim the free-hand REVOLVER and hit the TARGET within 4 s; if you miss… he steals an ingot.',
    ],
    // ETAPA 4 · TRAIN
    tren_up: 'Guard the train GOLD: open the crate padlocks and reach the station with the loot',
    tren_llega: 'STATION! The train comes to a halt…',
    tren_sale: 'The train DEPARTS! Stop {n} of 3 · goal: {m} ingots',
    tren_lingote: 'INGOT ON THE CRATE! ({n}/{m})',
    tren_objetivo: 'GOAL COVERED ({n}/{m})! Keep it until the station',
    tren_ok: 'STOP CLEARED! The gold reaches the station intact…',
    tren_piramide: 'NEW PYRAMID! More crates in sight',
    tren_pcajas: 'SUPERPOWER! CRATE RAIN!',
    tren_px3: 'SUPERPOWER! TRIPLE BALL!',
    tren_pdina: 'SUPERPOWER! DYNAMITE BALL!',
    tren_forajido: 'OUTLAW AT THE WINDOW! SHOOT THE TARGET!',
    tren_herido: 'WELL DONE, STRANGER! Outlaw down',
    tren_robo: 'THE OUTLAW STOLE ONE OF YOUR INGOTS!',
    tren_indio: 'INDIANS! SHOOT THEM DOWN OR THEY WILL ARROW YOUR GOLD AWAY!',
    tren_indio_ok: 'INDIAN DOWN! He fades away…',
    tren_tunel: 'WHISTLE! Tunnel ahead… ONLY THE LOCKS GLOW',
    tren_estacion: 'STATION REACHED! Full loot, stranger',
    tren_falla: 'NOT ENOUGH GOLD… the stop is lost',
    // v2.140 · STATION PA announcements (core voice bank; the {e} slots get
    // the stop names — the normalized text must match game.html VOICE_FULL)
    tren_mega_salida: 'All aboard! We are departing towards {e}',
    tren_mega_llega: 'In less than 25 seconds we will arrive at {e}',
    tren_mega_oro: 'The gold shipment is safe and sound',
    msg_guest: 'Online guest mode: duel not available',
    pw_warn: 'OUTLAW SUPERPOWER!',
    pw_disparo: 'DUEL! Hit the target within 3 s · ball is frozen',
    pw_arena: 'SANDSTORM! Dust and tumbleweeds on your court · shake them off your sight',
    pw_estampida: 'STAMPEDE! The herd crosses the town · stay focused',
    duelo_acierta: 'BULLSEYE! The rally continues as it was · nice shot',
    duelo_falla: 'THE OUTLAW FIRES! Faster and DARK ball',
    pw_dinamita: 'DYNAMITE! Bat the cartridges mid-air · watch out for the blasts',
    dyn_mesa: 'DYNAMITE ON THE TABLE! Keep the blast away from the ball',
    dyn_desvia: 'BOOM! The ball flies off!',
    dyn_bateada: 'You sent it back! Well hit!',
    dyn_boom: 'BOOM! The dynamite went off…',
    msg_enter: 'The Wild West is coming… this room is the OUTLAW\u2019s now!',
  },
};

/* ============================================================================
 *  v2.86 · CARTEL DE SUPERPODER del forajido (mismo motor y tiempos del
 *  WizardPowerSign: entra en zig-zag, se sostiene y sale despedido). Usa la
 *  MISMA IMAGEN DE SIEMPRE (assets/superpoder.webp, el «Super Power!!» de
 *  La Locura y Magia — v2.88: el archivo viaja SIEMPRE en el zip, nada de
 *  cartel procedural distinto). v2.88: el cartel se ANCLA A LA RED de la
 *  mesa (a la altura de la red, sobre la mesa) en TODOS los campeonatos —
 *  nada de pegarlo a la cara del jugador.
 *  ============================================================================ */
class ForajidoPowerSign {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    // v3.6.4-SDK4 · FASE 6: la fábrica del SDK (createPowerSign) sustituye
    // la copia — UNA sola fuente para el tablón de superpoder (ForajidoPowerSign).
    this._impl = createPowerSign(THREE, () => this.game, {
      coreo: 'clasica',
      arte: 'plano',
      url: () => new URL('./assets/superpoder.webp', import.meta.url).href,
      pintar: (aplicar) => this._pintarRespaldo(aplicar),
      dims: () => ODIMS(),
    });
    this.T_IN = this._impl.T_IN;
    this.T_HOLD = this._impl.T_HOLD;
    this.T_OUT = this._impl.T_OUT;
  }
  build() { this._impl.build(); }
  show(iconUrl) { this._impl.show(iconUrl); }
  hide() { this._impl.hide(); }
  update(dt) { this._impl.update(dt); }
  dispose() { this._impl.dispose(); }
  get group() { return this._impl.group; }   // acceso QA/interno (solo lectura)
  /* Respaldo: tablón quemado del Oeste (mismo pintor que había en el
   * build: vetas, quemaduras de borde, marco con clavos, estrella del
   * sheriff, ¡SUPERPODER! DEL FORAJIDO y agujeros de bala). */
  _pintarRespaldo(aplicar) {
    const cv = oesteCanvas(1024, 560);
    const c = cv.getContext('2d');
    // tablones quemados
    const gr = c.createLinearGradient(0, 0, 0, 560);
    gr.addColorStop(0, '#3c2a16');
    gr.addColorStop(0.5, '#4c3418');
    gr.addColorStop(1, '#2c1c0c');
    c.fillStyle = gr; c.fillRect(0, 0, 1024, 560);
    c.strokeStyle = 'rgba(20,12,4,0.5)'; c.lineWidth = 3;
    for (let i = 0; i < 9; i++) {
      const y = 30 + i * 62;
      c.beginPath(); c.moveTo(0, y);
      c.bezierCurveTo(340, y + 8, 700, y - 8, 1024, y + 3);
      c.stroke();
    }
    // quemaduras de borde
    for (let i = 0; i < 26; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() < 0.5 ? Math.random() * 46 : 560 - Math.random() * 46;
      const r = 8 + Math.random() * 26;
      const rg = c.createRadialGradient(x, y, 0, x, y, r);
      rg.addColorStop(0, 'rgba(8,4,0,0.85)');
      rg.addColorStop(1, 'rgba(8,4,0,0)');
      c.fillStyle = rg;
      c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    }
    // marco con clavos
    c.strokeStyle = '#c89b4a'; c.lineWidth = 12;
    c.strokeRect(18, 18, 988, 524);
    c.fillStyle = '#e8c87a';
    [[40, 40], [984, 40], [40, 520], [984, 520]].forEach(([x, y]) => {
      c.beginPath(); c.arc(x, y, 9, 0, Math.PI * 2); c.fill();
    });
    // estrella del sheriff arriba
    c.save();
    c.translate(512, 108);
    c.fillStyle = '#e8c87a'; c.strokeStyle = '#7a5a1e'; c.lineWidth = 5;
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const r = (i % 2 === 0) ? 44 : 19;
      const a = -Math.PI / 2 + i * Math.PI / 5;
      const px = Math.cos(a) * r, py = Math.sin(a) * r;
      if (i === 0) c.moveTo(px, py); else c.lineTo(px, py);
    }
    c.closePath(); c.fill(); c.stroke();
    c.restore();
    // letras
    c.textAlign = 'center';
    c.fillStyle = '#ffdf8f';
    c.font = 'bold 104px Georgia, serif';
    c.strokeStyle = '#20120a'; c.lineWidth = 8;
    c.strokeText('¡SUPERPODER!', 512, 300);
    c.fillText('¡SUPERPODER!', 512, 300);
    c.fillStyle = '#e8b25f';
    c.font = 'bold 60px Georgia, serif';
    c.strokeText('DEL FORAJIDO', 512, 388);
    c.fillText('DEL FORAJIDO', 512, 388);
    // agujeros de bala
    for (const [bx, by] of [[150, 180], [880, 200], [200, 440], [840, 460]]) {
      c.fillStyle = '#120a04';
      c.beginPath(); c.arc(bx, by, 13, 0, Math.PI * 2); c.fill();
      c.strokeStyle = 'rgba(232,200,122,0.4)'; c.lineWidth = 3;
      c.beginPath(); c.arc(bx, by, 13, 0, Math.PI * 2); c.stroke();
    }
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    aplicar(t);
  }
}
/* ============================================================================
 *  v2.86 · FX del duelo (pools reutilizables — regla Quest: nada por partida).
 *  Chispas (planos aditivos), humo cartoon (sprites), fogonazos, rayos del
 *  jugador y MANCHONES QUEMADOS persistentes (~6 s). TODO en el RIG.
 *  ============================================================================ */
function oesteTexDot() {
  const cv = oesteCanvas(64, 64);
  const c = cv.getContext('2d');
  const rg = c.createRadialGradient(32, 32, 0, 32, 32, 30);
  rg.addColorStop(0, 'rgba(255,255,255,1)');
  rg.addColorStop(0.35, 'rgba(255,235,180,0.9)');
  rg.addColorStop(1, 'rgba(255,200,90,0)');
  c.fillStyle = rg; c.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function oesteTexPuff() {
  const cv = oesteCanvas(128, 128);
  const c = cv.getContext('2d');
  for (const [x, y, r, a] of [[64, 66, 46, 0.9], [42, 58, 30, 0.75], [88, 60, 28, 0.72], [60, 44, 24, 0.6], [78, 84, 26, 0.6]]) {
    const rg = c.createRadialGradient(x, y, r * 0.1, x, y, r);
    rg.addColorStop(0, 'rgba(255,255,255,' + a + ')');
    rg.addColorStop(0.7, 'rgba(235,228,218,' + a * 0.5 + ')');
    rg.addColorStop(1, 'rgba(235,228,218,0)');
    c.fillStyle = rg;
    c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
  }
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}
function oesteTexScorch() {
  const cv = oesteCanvas(256, 256);
  const c = cv.getContext('2d');
  // mancha irregular: varios blotches superpuestos
  for (const [x, y, r] of [[128, 128, 78], [96, 108, 44], [166, 140, 40], [120, 168, 38], [150, 96, 30], [88, 150, 26]]) {
    const rg = c.createRadialGradient(x, y, r * 0.08, x, y, r);
    rg.addColorStop(0, 'rgba(10,6,2,0.95)');
    rg.addColorStop(0.55, 'rgba(26,14,6,0.75)');
    rg.addColorStop(0.85, 'rgba(58,32,14,0.28)');
    rg.addColorStop(1, 'rgba(58,32,14,0)');
    c.fillStyle = rg;
    c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
  }
  // brasas
  c.fillStyle = 'rgba(120,60,18,0.5)';
  for (let i = 0; i < 26; i++) {
    const a = Math.random() * Math.PI * 2, r = Math.random() * 66;
    c.beginPath();
    c.arc(128 + Math.cos(a) * r, 128 + Math.sin(a) * r, 1.6 + Math.random() * 2.4, 0, Math.PI * 2);
    c.fill();
  }
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

/* v2.120: scratch del humo/efectos de ForajidoFx (cero allocs por ráfaga). */
const _FX_V1 = new THREE.Vector3();

class ForajidoFx {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
  }
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.root = new THREE.Group();
    g.rig.add(this.root);
    this.texDot = oesteTexDot();
    this.texPuff = oesteTexPuff();
    this.texScorch = oesteTexScorch();
    // chispas
    this.sparks = [];
    for (let i = 0; i < 56; i++) {
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(0.028, 0.028),
        new THREE.MeshBasicMaterial({
          map: this.texDot, transparent: true, depthWrite: false,
          blending: THREE.AdditiveBlending, color: 0xffd77a, opacity: 0,
        }),
      );
      m.visible = false; m.renderOrder = 12;
      this.root.add(m);
      this.sparks.push({ m, v: new THREE.Vector3(), life: 0, t: 0, gr: 6 });
    }
    // humo cartoon
    this.smokes = [];
    for (let i = 0; i < 12; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.texPuff, transparent: true, depthWrite: false,
        opacity: 0, color: 0xd8d2c8, rotation: Math.random() * Math.PI,
      }));
      s.visible = false; s.renderOrder = 11;
      this.root.add(s);
      this.smokes.push({ s, v: new THREE.Vector3(), life: 0, t: 0, r0: 0.2, r1: 0.66 });
    }
    // v2.89 · CORTINA DE HUMO DENSA de la dinamita: tapa ALGO la bola y
    // dura como el manchón (~6 s) desvaneciéndose, como pide el artista.
    this.curtains = [];
    for (let i = 0; i < 14; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.texPuff, transparent: true, depthWrite: false,
        opacity: 0, color: 0x877f76, rotation: Math.random() * Math.PI,
      }));
      s.visible = false; s.renderOrder = 15;
      this.root.add(s);
      this.curtains.push({ s, v: new THREE.Vector3(), life: 0, t: 0, r0: 0.22, r1: 0.8, peak: 0.62 });
    }
    // fogonazos
    this.flashes = [];
    for (let i = 0; i < 3; i++) {
      const m = new THREE.Mesh(
        new THREE.SphereGeometry(0.14, 14, 10),
        new THREE.MeshBasicMaterial({
          color: 0xffc966, transparent: true, opacity: 0,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }),
      );
      m.visible = false; m.renderOrder = 13;
      this.root.add(m);
      this.flashes.push({ m, life: 0, t: 0, r: 0.14 });
    }
    // rayos del jugador (patrón magia: 0.16 s de vida)
    this.beams = [];
    // v2.90 · MIRA LÁSER CONTINUA del duelo: un hilo fino que sale de la
    // boca del cañón del revólver EN MANO y sigue el EJE del cañón (mismo
    // rayo que el disparo: WYSIWYG). Punto rojo al final (se enciende al
    // tocar la diana). Se construye aquí y el DueloAction la dirige.
    this.laser = null;
    this.lasers = null;   // v2.98: DOS miras (una por revólver)
    // manchones quemados (persistentes ~6 s)
    this.scorches = [];
    for (let i = 0; i < 4; i++) {
      const m = new THREE.Mesh(
        new THREE.PlaneGeometry(0.34, 0.34),
        new THREE.MeshBasicMaterial({
          map: this.texScorch, transparent: true, depthWrite: false, opacity: 0,
        }),
      );
      m.rotation.x = -Math.PI / 2;
      m.visible = false; m.renderOrder = 4;
      this.root.add(m);
      this.scorches.push({ m, life: 0, t: 0, hold: DINAMITA.marcaT - 1.6, fade: 1.6 });
    }
  }
  /** v2.90 · Construye (una vez) los tríos del láser: hilo + halo +
   *  punto. v2.98: DOS miras, una por revólver (slot 0/1). */
  _laserBuild() {
    if (this.lasers || !this.inited) return;
    this.lasers = [];
    for (let i = 0; i < 2; i++) {
      const core = new THREE.Mesh(
        new THREE.BoxGeometry(0.0035, 0.0035, 1),
        new THREE.MeshBasicMaterial({ color: 0xff4433, transparent: true, opacity: 0.85 }),
      );
      const glow = new THREE.Mesh(
        new THREE.BoxGeometry(0.014, 0.014, 1),
        new THREE.MeshBasicMaterial({
          color: 0xff6a3c, transparent: true, opacity: 0.28,
          blending: THREE.AdditiveBlending, depthWrite: false,
        }),
      );
      const dot = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.texDot, color: 0xff5533, transparent: true,
        opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      dot.scale.setScalar(0.028);
      core.renderOrder = 16; glow.renderOrder = 16; dot.renderOrder = 17;
      core.visible = glow.visible = dot.visible = false;
      core.frustumCulled = glow.frustumCulled = false;
      this.root.add(core, glow, dot);
      this.lasers.push({ core, glow, dot });
    }
    this.laser = this.lasers[0];   // compat duelo (v2.90)
  }
  /** v2.90 · Dibuja la mira: rayo rPos→rPos+len·rDir (espacio RIG) con
   *  punto al final; hot=true cuando el punto cae SOBRE la diana.
   *  v2.98: slot = 0/1 (la mira del revólver de ESA mano). */
  laserUpdate(rPos, rDir, len, hot, slot) {
    this._laserBuild();
    if (!this.lasers) return;
    const L = this.lasers[Math.max(0, Math.min(1, slot | 0))] ||
      this.lasers[0];
    // v2.92: temporales de módulo (antes 2-3 Vector3 por FRAME aquí dentro)
    const mid = _OE_V1.copy(rPos).addScaledVector(rDir, len / 2);
    L.core.position.copy(mid); L.glow.position.copy(mid);
    L.core.scale.set(1, 1, len); L.glow.scale.set(1, 1, len);
    L.core.quaternion.setFromUnitVectors(
      _OE_V2.set(0, 0, 1), _OE_V3.copy(rDir).normalize());
    L.glow.quaternion.copy(L.core.quaternion);
    L.dot.position.copy(rPos).addScaledVector(rDir, len);
    const s = hot ? 0.05 : 0.028;
    L.dot.scale.setScalar(s);
    L.dot.material.color.setHex(hot ? 0xff2211 : 0xff8844);
    L.core.visible = L.glow.visible = L.dot.visible = true;
  }
  laserVisible(on, slot) {
    if (!this.lasers) return;
    if (slot === undefined || slot === null) {
      for (const L of this.lasers) {
        L.core.visible = L.glow.visible = L.dot.visible = !!on;
      }
      return;
    }
    const L = this.lasers[slot | 0];
    if (!L) return;
    L.core.visible = L.glow.visible = L.dot.visible = !!on;
  }
  spark(pos, n, color, speed, up) {
    if (!this.inited) return;
    let placed = 0;
    for (const s of this.sparks) {
      if (s.life > 0) continue;
      s.life = 0.28 + Math.random() * 0.18;
      s.t = 0;
      s.gr = 5.5;
      s.m.position.copy(pos);
      s.m.material.color.setHex(color || 0xffd77a);
      s.m.material.opacity = 1;
      s.m.visible = true;
      s.v.set((Math.random() - 0.5) * 2, (Math.random() * 0.6 + 0.3) * (up || 1), (Math.random() - 0.5) * 2)
        .normalize().multiplyScalar((speed || 2.6) * (0.5 + Math.random() * 0.8));
      if (++placed >= (n || 8)) break;
    }
  }
  mecha(pos, n) {
    // chispas de mecha: cortas, hacia arriba
    if (!this.inited) return;
    let placed = 0;
    for (const s of this.sparks) {
      if (s.life > 0) continue;
      s.life = 0.14 + Math.random() * 0.12;
      s.t = 0;
      s.gr = 3.5;
      s.m.position.copy(pos);
      s.m.material.color.setHex(Math.random() < 0.5 ? 0xffe9a0 : 0xff9d3c);
      s.m.material.opacity = 1;
      s.m.visible = true;
      s.v.set((Math.random() - 0.5) * 1.1, 0.5 + Math.random() * 1.1, (Math.random() - 0.5) * 1.1);
      if (++placed >= (n || 2)) break;
    }
  }
  smoke(pos, n, big) {
    if (!this.inited) return;
    let placed = 0;
    for (const s of this.smokes) {
      if (s.life > 0) continue;
      s.life = 1.25 + Math.random() * 0.5;
      s.t = 0;
      s.r0 = (big ? 0.16 : 0.10) + Math.random() * 0.08;
      s.r1 = big ? (0.6 + Math.random() * 0.3) : (0.3 + Math.random() * 0.2);
      s.s.position.copy(pos).add(_FX_V1.set(
        (Math.random() - 0.5) * (big ? 0.34 : 0.16),
        Math.random() * 0.10,
        (Math.random() - 0.5) * (big ? 0.34 : 0.16),
      ));
      s.v.set((Math.random() - 0.5) * 0.22, 0.42 + Math.random() * 0.3, (Math.random() - 0.5) * 0.22);
      s.s.material.opacity = 0;
      s.s.material.rotation = Math.random() * Math.PI;
      s.s.visible = true;
      if (++placed >= (n || 5)) break;
    }
  }
  /** v2.106 · HUMO DE PISTOLA: bocanada que NACE en la boca del cañón y
   *  se queda CERCA (sube poco y se disipa rápido) — el humo genérico
   *  (smoke) subía 0,42-0,72 m/s y al final flotaba MUY POR ENCIMA del
   *  revólver: «el humo no sale desde su pistola». */
  smokeGun(pos, n) {
    if (!this.inited) return;
    let placed = 0;
    for (const s of this.smokes) {
      if (s.life > 0) continue;
      s.life = 0.65 + Math.random() * 0.4;
      s.t = 0;
      s.r0 = 0.06 + Math.random() * 0.05;
      s.r1 = 0.22 + Math.random() * 0.14;
      s.s.position.copy(pos).add(_FX_V1.set(
        (Math.random() - 0.5) * 0.07,
        Math.random() * 0.05,
        (Math.random() - 0.5) * 0.07,
      ));
      s.v.set((Math.random() - 0.5) * 0.16, 0.14 + Math.random() * 0.16,
        (Math.random() - 0.5) * 0.16);
      s.s.material.opacity = 0;
      s.s.material.rotation = Math.random() * Math.PI;
      s.s.visible = true;
      if (++placed >= (n || 6)) break;
    }
  }
  flash(pos, scale, color) {
    if (!this.inited) return;
    for (const f of this.flashes) {
      if (f.life > 0) continue;
      f.life = 0.14;
      f.t = 0;
      f.r = 0.14 * (scale || 1);
      f.m.position.copy(pos);
      f.m.material.color.setHex(color || 0xffc966);
      f.m.material.opacity = 0.95;
      f.m.visible = true;
      break;
    }
  }
  /** v2.89 · CORTINA DE HUMO: nube GRUESA y DURA (~6 s como el manchón)
   *  que se planta sobre la explosión (entre la bola y el jugador) para
   *  dificultar ALGO ver la pelota, sin cegar. Se desvanece sola. */
  smokeCurtain(pos, n) {
    if (!this.inited) return;
    const T = DINAMITA.marcaT;             // ~6 s, la vida del manchón
    let placed = 0;
    for (const s of this.curtains) {
      if (s.life > 0) continue;
      s.life = T * (0.82 + Math.random() * 0.2);
      s.t = 0;
      s.r0 = 0.22 + Math.random() * 0.14;
      s.r1 = 0.62 + Math.random() * 0.36;
      s.peak = 0.5 + Math.random() * 0.22;
      s.s.position.copy(pos).add(_FX_V1.set(
        (Math.random() - 0.5) * 0.9,
        0.06 + Math.random() * 0.55,
        (Math.random() - 0.5) * 0.44 + 0.12,   // algo más cerca del jugador
      ));
      s.v.set((Math.random() - 0.5) * 0.16, 0.16 + Math.random() * 0.22,
        (Math.random() - 0.5) * 0.16);
      s.s.material.opacity = 0;
      s.s.material.rotation = Math.random() * Math.PI;
      s.s.visible = true;
      if (++placed >= (n || 10)) break;
    }
  }
  beam(rPos, rDir, len) {
    if (!this.inited) return;
    // v2.92 · POOL del beam: antes cada tiro creaba 2 mallas + 2 geometrías
    // + 2 materiales y los DESTROYÍA a los 0,16 s — con re-disparo libre el
    // churn pegaba tirones en la Quest. Ahora: geometría UNITARIA escalada
    // en Z y 4 ranuras recicladas (cero asignaciones por disparo).
    if (!this._beamPool) {
      this._beamPool = [];
      for (let i = 0; i < 4; i++) {
        const core = new THREE.Mesh(
          new THREE.BoxGeometry(0.010, 0.010, 1),
          new THREE.MeshBasicMaterial({ color: 0xfff2cf, transparent: true, opacity: 0.95 }),
        );
        const glow = new THREE.Mesh(
          new THREE.BoxGeometry(0.034, 0.034, 1),
          new THREE.MeshBasicMaterial({
            color: 0xffb45f, transparent: true, opacity: 0.4,
            blending: THREE.AdditiveBlending, depthWrite: false,
          }),
        );
        core.visible = glow.visible = false;
        this.root.add(core, glow);
        this._beamPool.push({ core, glow });
      }
    }
    let slot = this._beamPool.find((b) => !b.core.visible);
    if (!slot) slot = this._beamPool[0];   // la más antigua se recicla
    slot.core.position.copy(rPos).addScaledVector(rDir, len / 2);
    slot.glow.position.copy(slot.core.position);
    slot.core.scale.set(1, 1, len); slot.glow.scale.set(1, 1, len);
    slot.core.quaternion.setFromUnitVectors(
      _OE_V2.set(0, 0, 1), _OE_V3.copy(rDir).normalize());
    slot.glow.quaternion.copy(slot.core.quaternion);
    slot.core.material.opacity = 0.95; slot.glow.material.opacity = 0.4;
    slot.core.visible = slot.glow.visible = true;
    this.beams.push({ core: slot.core, glow: slot.glow, t: 0 });
  }
  scorch(x, y, z, size) {
    if (!this.inited) return;
    for (const s of this.scorches) {
      if (s.life > 0) continue;
      s.life = s.hold + s.fade;
      s.t = 0;
      s.m.position.set(x, y, z);
      s.m.rotation.z = Math.random() * Math.PI;
      s.m.scale.setScalar((size || 1) * (0.85 + Math.random() * 0.3));
      s.m.material.opacity = 0.92;
      s.m.visible = true;
      break;
    }
  }
  update(dt) {
    if (!this.inited) return;
    for (const s of this.sparks) {
      if (s.life <= 0) continue;
      s.t += dt;
      s.v.y -= s.gr * dt;
      s.m.position.addScaledVector(s.v, dt);
      const f = 1 - s.t / s.life;
      s.m.material.opacity = Math.max(0, f);
      if (s.t >= s.life) { s.life = 0; s.m.visible = false; }
    }
    for (const s of this.smokes) {
      if (s.life <= 0) continue;
      s.t += dt;
      const k = s.t / s.life;
      s.s.position.addScaledVector(s.v, dt);
      const r = s.r0 + (s.r1 - s.r0) * (1 - Math.pow(1 - Math.min(1, k * 1.6), 2));
      s.s.scale.setScalar(r);
      s.s.material.opacity = 0.88 * (k < 0.18 ? k / 0.18 : 1 - Math.pow((k - 0.18) / 0.82, 1.6));
      s.s.material.rotation += dt * 0.5;
      if (k >= 1) { s.life = 0; s.s.visible = false; }
    }
    // cortina de humo densa (v2.89): sube lenta, aguanta y se desvanece
    for (const s of this.curtains) {
      if (s.life <= 0) continue;
      s.t += dt;
      const k = s.t / s.life;
      s.s.position.addScaledVector(s.v, dt);
      s.s.material.rotation += dt * 0.22;
      const r = s.r0 + (s.r1 - s.r0) * Math.min(1, k * 1.5);
      s.s.scale.setScalar(r);
      const fadeIn = Math.min(1, s.t / 0.5);
      const fadeOut = k > 0.62 ? 1 - (k - 0.62) / 0.38 : 1;
      s.s.material.opacity = s.peak * fadeIn * fadeOut;
      if (k >= 1) { s.life = 0; s.s.visible = false; }
    }
    for (const f of this.flashes) {
      if (f.life <= 0) continue;
      f.t += dt;
      const k = f.t / f.life;
      f.m.scale.setScalar(0.4 + k * 2.2);
      f.m.material.opacity = 0.95 * (1 - k);
      if (k >= 1) { f.life = 0; f.m.visible = false; }
    }
    for (let i = this.beams.length - 1; i >= 0; i--) {
      const b = this.beams[i];
      b.t += dt;
      const f = 1 - b.t / 0.16;
      if (f <= 0) {
        // v2.92: vuelven al POOL (visibles=false) — sin dispose por tiro
        b.core.visible = b.glow.visible = false;
        this.beams.splice(i, 1);
        continue;
      }
      b.core.material.opacity = 0.95 * f;
      b.glow.material.opacity = 0.4 * f;
    }
    for (const s of this.scorches) {
      if (s.life <= 0) continue;
      s.t += dt;
      if (s.t > s.hold) {
        const k = Math.min(1, (s.t - s.hold) / s.fade);
        s.m.material.opacity = 0.92 * (1 - k);
      }
      if (s.t >= s.life) { s.life = 0; s.m.visible = false; }
    }
  }
}

/* ============================================================================
 *  v2.86/89 · SUPERPODER 1: «DISPARO CERTERO» — AHORA ES UN DUELO (v2.89).
 *  El forajido DESENFUNDA su revólver DELANTE de él (retrato duelo del
 *  artista) y aparece una DIANA sobre su cuerpo (salta entre las 5 zonas de
 *  duelo_zonas.jpg). La bola queda CONGELADA en su posición y la PALA del
 *  jugador se convierte en el MISMO revólver: 3 s para acertar con todos los
 *  disparos que queramos.
 *    · ACIERTO (en cualquier zona) → el forajido muestra la pose de la zona
 *      alcanzada, la bola RETOMA su recorrido original (se descongela tal
 *      cual) y recuperamos la pala: la partida sigue exactamente igual.
 *    · FALLO (pasan los 3 s) → el forajido ENCARA la bola congelada y
 *      DISPARA (estampido FUERTE + humo saliendo del cañón): la bala
 *      trazadora la alcanza y la RE-DIRIGE hacia nuestra mesa, MÁS RÁPIDA
 *      y OSCURA. Recuperamos la pala y la partida sigue con la bola
 *      alterada. El resto del tiempo la bola es BLANCA (OESTE.ballColors).
 *  El revólver se carga UNA vez y se guarda en caché del CTRL (regla Quest:
 *  nada por partida).
 *  ============================================================================ */
/* Temporales del DUELO (v2.120): el vuelo de la bala corre cada frame y no
 * puede alocar ni un Vector3 (GC churn = tirones en la Quest). */
const _DU_V1 = new THREE.Vector3();
const _DU_V2 = new THREE.Vector3();
const _DU_V3 = new THREE.Vector3();
const _DU_AXIS_Z = new THREE.Vector3(0, 0, 1);
/* v2.120 · POOL DE LA BALA TRAZADORA: geometrías/materiales/mallas UNA vez
 * (antes: 2 mallas + 2 geometrías + 2 materiales creados y destruidos por
 * disparo — el mismo churn que el beamPool erradicó en ForajidoFx). */
const _DU_BULLET_GEO = new THREE.BoxGeometry(0.016, 0.016, 0.30);
const _DU_GLOW_GEO = new THREE.BoxGeometry(0.05, 0.05, 0.34);
const _DU_BULLET_MAT = new THREE.MeshBasicMaterial({ color: 0xffe9b0 });
const _DU_GLOW_MAT = new THREE.MeshBasicMaterial({
  color: 0xffb45f, transparent: true, opacity: 0.5,
  blending: THREE.AdditiveBlending, depthWrite: false,
});
/* v2.120: scratch del rayo del revólver (_gunRay/_gunRayHand) — los
 * llamadores lo consumen SIEMPRE dentro del mismo frame. */
const _GR_V1 = new THREE.Vector3(); const _GR_V2 = new THREE.Vector3();
const _GR_V3 = new THREE.Vector3(); const _GR_V4 = new THREE.Vector3();
const _GR_Q1 = new THREE.Quaternion(); const _GR_Q2 = new THREE.Quaternion();
class DueloAction {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.done = false;
    this.phase = 'idle';
    this.t = 0;
    this.mesh = null;
    this.bullet = null;
    this.bulletGlow = null;
    this.dir = new THREE.Vector3();
    this._muzzleW = new THREE.Vector3();
    this._muzzleLocal = null;    // v2.93: boca del cañón en unidades locales
    this._smokeT = 0;
    this._zone = 3;
    this._hopT = 0;
    this._swayT = 0;
    this._lastTick = 99;
  }
  start() {
    const g = this.game;
    // retrato: el forajido DESENFUNDA (arte nuevo del artista, v2.89)
    this.ctrl._showDuelArt('duelo', 0);
    // ancla: DELANTE DEL FORAJIDO, a la altura del pecho — el revólver se
    // coloca junto al personaje como si lo tuviese ya desenfundado
    this.anchor = new THREE.Vector3(DUELO.x + 0.30, 1.24, DUELO.z + 0.52);
    // mesh: el GLB en caché o un revólver de reserva (cajas)
    this.mesh = this.ctrl._revolverModel
      ? this.ctrl._revolverModel.clone(true)
      : this._fallbackGun();
    this.mesh.position.copy(this.anchor);
    // v2.92 · VOLTEO DEL REVÓLVER DEL FORAJIDO: con la caché (boca en -Z)
    // y rotación 0 el cañón quedaba mirando a la PARED (lado contrario al
    // del jugador — informe del visor). Girando 180° en Y la boca apunta
    // AL JUGADOR: el duelo queda de tú a tú. (En _forajidoFire el
    // encaramiento a la bola se recalcula con el cuaternión absoluto, así
    // que este giro no afecta al disparo.)
    this.mesh.rotation.set(0, Math.PI, 0);
    // v2.88: ESCALA RELATIVA — el clon del GLB conserva la normalización
    // (0,34 m) hecha en _normalizeGunArt; pisar la escala con setScalar(0.25)
    // multiplicaba el modelo RAW (24,6 unidades -> un revólver de 6 METROS).
    this._s0 = this.mesh.scale.x || 1;
    this.mesh.scale.setScalar(this._s0 * 0.25);
    g.rig.add(this.mesh);
    // v2.93 · BOCA EXACTA en unidades locales del arte (medida por VÉRTICES
    // en la carga y garantizada en -Z LOCAL): el volteo visual (π) no la
    // cambia en local y _muzzlePos() la aplica con la ESCALA real de la
    // malla y el cuaternión VIGENTE. (Antes el bbox daba el offset en
    // unidades equivocadas: fogonazo/humo/bala nacían lejos del cañón.)
    // Reserva (revólver de cajas): boca local (0, 0.024, -0.185).
    this._muzzleLocal = (this.ctrl._revMuzzleLocal
      ? this.ctrl._revMuzzleLocal.clone()
      : new THREE.Vector3(0, 0.024, -0.185));
    // LA PALA DEL JUGADOR SE CONVIERTE EN EL MISMO REVÓLVER (v2.89)
    this.ctrl._paddleGunApply(true);
    // DIANA sobre el cuerpo del forajido (zona aleatoria de las 5)
    this.ctrl._dianaShow();
    this._zone = this.ctrl.dianaZone || 3;
    this._hopT = DUELO_P.hopT;
    // BOLA CONGELADA en su posición durante todo el margen del duelo
    // v3.6.2-SDK2: congela() del SDK (el patrón de la casa, una sola fuente).
    congela(g, DUELO_P.drawT + DUELO_P.window + 0.35);
    this.phase = 'draw';
    this.t = 0;
    this.ctrl.sfx('desenfundar', 0.4);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 110);
  }
  /** Reserva si el GLB no llegó: pistola de cajas creíble (no se usa si hay arte). */
  _fallbackGun() {
    const grp = new THREE.Group();
    const metal = new THREE.MeshStandardMaterial({ color: 0x4a4a52, roughness: 0.45, metalness: 0.75 });
    const madera = new THREE.MeshStandardMaterial({ color: 0x5c3a20, roughness: 0.8, metalness: 0.05 });
    const tambor = new THREE.Mesh(new THREE.CylinderGeometry(0.024, 0.024, 0.05, 10), metal);
    tambor.rotation.x = Math.PI / 2; tambor.position.set(0, 0.012, -0.02);
    const canion = new THREE.Mesh(new THREE.BoxGeometry(0.02, 0.034, 0.15), metal);
    canion.position.set(0, 0.024, -0.11);
    const puño = new THREE.Mesh(new THREE.BoxGeometry(0.024, 0.075, 0.036), madera);
    puño.position.set(0, -0.045, 0.028);
    puño.rotation.x = 0.35;
    const martillo = new THREE.Mesh(new THREE.BoxGeometry(0.012, 0.022, 0.016), metal);
    martillo.position.set(0, 0.05, 0.004);
    grp.add(tambor, canion, puño, martillo);
    const s = DISPARO.escala / 0.34;
    grp.scale.setScalar(s);
    return grp;
  }
  /** Predicción de la bola a t s (gravedad, sin drag — igual que el vuelo real). */
  _predictBall(t) {
    const b = this.game.ball;
    return new THREE.Vector3(
      b.pos.x + b.vel.x * t,
      b.pos.y + b.vel.y * t - 4.905 * t * t,
      b.pos.z + b.vel.z * t,
    );
  }
  update(dt) {
    if (this.done || this.phase === 'idle') return;
    this.t += dt;
    const g = this.game;
    if (this.phase === 'draw') {
      // desenfundar: sube girando sobre sí misma y crece hasta su tamaño
      // (v2.92: el giro TERMINA en π — boca hacia el jugador, ver start())
      const k = Math.min(1, this.t / DUELO_P.drawT);
      const e = 1 - Math.pow(1 - k, 3);
      this.mesh.position.set(this.anchor.x, this.anchor.y - 0.28 * (1 - e), this.anchor.z);
      this.mesh.rotation.y = Math.PI + (1 - e) * Math.PI * 5.5;
      this.mesh.scale.setScalar(this._s0 * (0.25 + 0.75 * e));
      if (k >= 1) { this.phase = 'duel'; this.t = 0; this._lastTick = 99; }
    } else if (this.phase === 'duel') {
      // EL MARGEN CORRE SIEMPRE (la bola sigue congelada: freezeT reposado)
      congela(g, 0.10);   // v3.6.2-SDK2: congela() del SDK
      // v2.90: SIN contador 3·2·1 sobre la diana — solo el tic-tac sonoro
      const n = Math.ceil(DUELO_P.window - this.t);
      if (n !== this._lastTick && n >= 0) {
        this._lastTick = n;
        if (n > 0) this.ctrl.sfx('tick', 0);
      }
      // la diana se mece SIEMPRE sobre el cuerpo del forajido y salta de zona
      this._hopT -= dt;
      this._swayT += dt;
      if (this.ctrl.diana && this.ctrl.diana.visible) {
        const z = DUELO_ZONAS[this._zone - 1] || DUELO_ZONAS[2];
        this.ctrl.diana.position.set(
          DUELO.x + Math.sin(this._swayT * 2.1) * DUELO_P.swayX,
          z.y + Math.sin(this._swayT * 3.3) * 0.02,
          DUELO.z + 0.10);
        this.ctrl.diana.scale.setScalar(
          DUELO_P.dianaSize * (1 + Math.sin(this._swayT * 5.2) * 0.06));
        if (this._hopT <= 0) {
          this._hopT = DUELO_P.hopT * (0.85 + Math.random() * 0.5);
          const nz = 1 + ((Math.random() * DUELO_ZONAS.length) | 0);
          if (nz !== this._zone) { this._zone = nz; this.ctrl.dianaZone = nz; }
        }
      }
      // el revólver del forajido «respira» en su mano (tino de duelo)
      if (this.mesh) {
        this.mesh.position.set(
          this.anchor.x + Math.sin(this._swayT * 1.4) * 0.012,
          this.anchor.y + Math.sin(this._swayT * 2.2) * 0.010,
          this.anchor.z);
        // v2.93 · EL FORAJIDO ENCARA A LA CÁMARA VR (realismo tú a tú, a
        // petición del artista): el cañón (boca local -Z) sigue a la
        // CABEZA del jugador con slerp suave. Temporales de módulo: cero
        // asignaciones por frame. En _forajidoFire el encaramiento pasa a
        // la bola congelada (mecánica intacta) en un frame.
        try {
          const cam = g.camera;
          if (cam) {
            this._muzzlePos(_OE_V1);
            _OE_V2.copy(cam.position).sub(_OE_V1).normalize();
            if (_OE_V2.lengthSq() > 1e-6) {
              _OE_M4.lookAt(_OE_ZERO, _OE_V2, _OE_UP);
              _OE_Q1.setFromRotationMatrix(_OE_M4);
              this.mesh.quaternion.slerp(_OE_Q1, Math.min(1, dt * 7));
            }
          }
        } catch (e) { /* sin encaramiento dinámico: se queda horizontal */ }
      }
      // v2.90 · MIRA LÁSER: rayo continuo desde la boca del cañón del
      // revólver EN MANO, con el MISMO origen y la MISMA dirección que el
      // disparo (WYSIWYG: lo que marca el punto es lo que vas a acertar).
      this._aimLaser();
      // ¿tiempo cumplido sin acertar? → el forajido DISPARA
      if (this.t >= DUELO_P.window) this._forajidoFire();
    } else if (this.phase === 'fire') {
      // la bala nace en el muzzle ya encarado (transición de 1 frame)
      this._spawnBullet();
    } else if (this.phase === 'bullet') {
      this._bt += dt;
      // BARRIDO (lección v2.84): a dt grandes la bala salta 1,3 m por frame —
      // la colisión se comprueba sobre el SEGMENTO previo→actual.
      if (!this._prev) this._prev = new THREE.Vector3();
      this._prev.copy(this.bullet.position);
      const step = DISPARO.bulletSpeed * dt;
      this.bullet.position.addScaledVector(this.dir, step);
      this.bulletGlow.position.copy(this.bullet.position);
      // chispas de la estela
      this._smokeT -= dt;
      if (this._smokeT <= 0) {
        this._smokeT = 0.05;
        this.ctrl.fx.mecha(this.bullet.position, 1);
      }
      // ¿impacto con la bola? + homing SUAVE (corrige botes de última hora)
      const b = this.game.ball;
      if (b && b.vel) {
        const to = _DU_V1.copy(b.pos).sub(this.bullet.position);
        const d = to.length();
        if (d > 0.001 && this._bt < DISPARO.maxLife * 0.8) {
          to.multiplyScalar(1 / d);
          this.dir.lerp(to, Math.min(0.15, 0.05 + dt * 2.2)).normalize();
          this.bullet.quaternion.setFromUnitVectors(_DU_AXIS_Z, this.dir);
          this.bulletGlow.quaternion.copy(this.bullet.quaternion);
        }
        const seg = _DU_V2.copy(this.bullet.position).sub(this._prev);
        const t = THREE.MathUtils.clamp(
          _DU_V3.copy(b.pos).sub(this._prev).dot(seg) /
            Math.max(1e-6, seg.lengthSq()), 0, 1);
        const closest = _DU_V3.copy(this._prev).addScaledVector(seg, t);
        const D = ODIMS();
        if (closest.distanceTo(b.pos) <
            DISPARO.radioImpacto + (D ? D.ballRadius : 0.04)) {
          this._impacto(b);
          this._holster();
          return;
        }
      }
      if (this._bt > DISPARO.maxLife) {
        // por si la bola se movió antes de tiempo: la bala se apaga sola
        this.ctrl.fx.smoke(this.bullet.position, 1, false);
        this._holster();
      }
    } else if (this.phase === 'out') {
      const k = Math.min(1, this.t / 0.26);
      this.mesh.rotation.y += dt * 14;
      this.mesh.scale.setScalar(Math.max(0.01, 1 - k) * this._s0);
      this.mesh.position.y -= dt * 0.55;
      if (k >= 1) this.done = true;
    }
  }
  /** BALA TRAZADORA: nace en el muzzle con la dirección ya encarada.
   *  v2.120: reusa el POOL (mallas/geometrías/materiales de módulo) — cero
   *  create/dispose de GPU por disparo. */
  _spawnBullet() {
    const g = this.game;
    const mz = this._muzzlePos(this._muzzleW);   // v2.93: boca exacta
    if (!this.bullet) {
      this.bullet = new THREE.Mesh(_DU_BULLET_GEO, _DU_BULLET_MAT);
      this.bulletGlow = new THREE.Mesh(_DU_GLOW_GEO, _DU_GLOW_MAT);
    }
    this.bullet.position.copy(mz);
    this.bulletGlow.position.copy(mz);
    this.bullet.quaternion.setFromUnitVectors(_DU_AXIS_Z, this.dir);
    this.bulletGlow.quaternion.copy(this.bullet.quaternion);
    g.rig.add(this.bullet);
    g.rig.add(this.bulletGlow);
    this._bt = 0;
    this.phase = 'bullet';
    this.t = 0;
  }
  /** v2.90 · MIRA LÁSER del duelo: mismo rayo que el disparo
   *  (ctrl._gunRay: boca del cañón real + eje del cañón). El hilo termina
   *  en la diana (punto caliente) o en la mesa/pared más cercana. */
  _aimLaser() {
    const g = this.game;
    const ray = this.ctrl._gunRay();
    if (!ray) { if (this.ctrl.fx) this.ctrl.fx.laserVisible(false); return; }
    let len = 7.0;
    let hot = false;
    // ¿el rayo alcanza la DIANA? → punto encima y calor de acierto
    if (this.ctrl.diana && this.ctrl.diana.visible) {
      const dp = this.ctrl.diana.position;
      const toD = _DU_V1.copy(dp).sub(ray.pos);
      const t = THREE.MathUtils.clamp(toD.dot(ray.dir), 0, len);
      const closest = _DU_V2.copy(ray.dir).multiplyScalar(t).add(ray.pos);
      if (closest.distanceTo(dp) < DUELO_P.dianaRadio) {
        len = t; hot = true;
      }
    }
    if (!hot) {
      // recorta el rayo contra el plano de la mesa (punto sobre el tapete)
      const D = ODIMS();
      const ty = D ? D.tableTopY : 0.76;
      if (ray.dir.y < -1e-4) {
        const t = (ty - ray.pos.y) / ray.dir.y;
        if (t > 0.05 && t < len) len = t;
      }
    }
    this.ctrl.fx.laserUpdate(ray.pos, ray.dir, len, hot);
  }
  /** v2.93 · Posición EXACTA de la boca del cañón en espacio RIG: boca
   *  local (unidades del arte, garantizada en -Z) × escala real de la
   *  malla, girada por el CUATERNIÓN VIGENTE (el encaramiento a cámara la
   *  mueve cada frame) y sumada al ancla. La usan el fogonazo, el humo y
   *  la bala del forajido. Escribe en `out` (cero asignaciones). */
  _muzzlePos(out) {
    return out.copy(this._muzzleLocal || _OE_V3.set(0, 0.024, -0.185))
      .multiplyScalar(this.mesh ? (this.mesh.scale.x || 1) : 1)
      .applyQuaternion(this.mesh.quaternion)
      .add(this.anchor);
  }
  /** FIN DE MARGEN: el forajido ENCARA la bola CONGELADA y DISPARA
   *  (estampido fuerte + humo saliendo del cañón). v2.93: al disparar sin
   *  acierto NOS SALPICA LA SANGRE a la cámara (reguero de ~10 s). */
  _forajidoFire() {
    const g = this.game;
    if (this.ctrl.fx) this.ctrl.fx.laserVisible(false);
    this.ctrl._dianaHide();
    // v2.93 · ENCAMADO EN DOS PASADAS: 1) gira el cañón (-Z local) hacia
    // la bola; 2) con el cuaternión FINAL la boca se recoloca y se
    // recalcula la dirección EXACTA bola←boca. (Con una sola pasada la
    // bala nacía en la boca nueva pero salía con la dirección de la
    // boca vieja — hasta 0,4 m de desvío: la bala pasaba de largo.)
    this.dir.copy(g.ball.pos).sub(this._muzzlePos(this._muzzleW)).normalize();
    this.mesh.quaternion.setFromUnitVectors(
      new THREE.Vector3(0, 0, -1), this.dir);
    this.mesh.position.copy(this.anchor);
    this._muzzlePos(this._muzzleW);   // boca con el encaramiento final
    this.dir.copy(g.ball.pos).sub(this._muzzleW).normalize();
    this.ctrl.fx.flash(this._muzzleW, 1.9, 0xffd98a);
    this.ctrl.fx.smoke(this._muzzleW, 3, false);
    this.ctrl.sfx('disparo', 0.55);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 130);
    // v2.93 · ¡NOS HA DADO! — el forajido ganó el duelo (ninguna diana
    // acertada): la cámara se llena de gotas de sangre con su reguero.
    this.ctrl._sangreTrigger();
    this.phase = 'fire';
    this.t = 0;
  }
  /** ACIERTO del jugador (disparo del revólver en mano contra la diana):
   *  v2.91 · SECUENCIA de IMPACTO — ¡BANG! fuerte del oeste, la pose de la
   *  zona se queda 4 s mientras el forajido TIEMBLA y LLORA; después 1 s
   *  de fundido: la imagen se oscurece hasta el negro y de él va
   *  apareciendo la pose normal. La partida SIGUE TAL CUAL desde ya. */
  acierto() {
    if (this.phase !== 'duel') return false;
    const g = this.game;
    const zone = this.ctrl.dianaZone || this._zone;
    const dp = this.ctrl.diana
      ? this.ctrl.diana.position.clone() : this.anchor.clone();
    this.ctrl.fx.spark(dp, 15, 0xffd77a, 3.2, 1.3);
    this.ctrl.fx.flash(dp, 1.3, 0xffe2a0);
    this.ctrl.fx.smoke(dp, 1, false);
    this.ctrl.sfx('diana', 0);
    this.ctrl.sfx('disparo', 0);   // v2.91: estampido FUERTE del oeste al acertar
    this.ctrl._dianaHide();
    // pose de impacto de la zona alcanzada (arte del artista) 4 s + temblor
    const zi = DUELO_ZONAS[zone - 1] || DUELO_ZONAS[2];
    this.ctrl._showDuelArt(zi.pose, DUELO_P.poseT);
    this.ctrl._hitShakeT = DUELO_P.poseT;      // v2.91: tiembla los 4 s
    this.ctrl.sfx('llanto', 0);                 // v2.91: llanto (fuera risa)
    // la bola RETOMA SU recorrido original: sólo descongelar
    g.rules.message = tx('duelo_acierta');
    g.freezeT = 0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 140);
    this._holster();
    return true;
  }
  /** La bala alcanza la bola congelada: RE-DIRIGIDA hacia NUESTRA mesa,
   *  MÁS RÁPIDA y OSCURA; después la bola retoma el movimiento desde
   *  donde había quedado parada. */
  _impacto(b) {
    const g = this.game;
    const D = ODIMS();
    // chispas + fogonazo + sonido FUERTE del impacto
    this.ctrl.fx.spark(b.pos, 16, 0xffe08a, 3.8, 1.5);
    this.ctrl.fx.flash(b.pos, 1.3, 0xffcf7a);
    this.ctrl.fx.smoke(b.pos, 2, false);
    this.ctrl.sfx('impacto', 0.3);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.55, 100);
    // rumbo NUEVO hacia la mesa del jugador (punto de bote aleatorio)
    const v = b.vel;
    const L = Math.max(v.length(), 2.6);
    const hw = D ? D.tableHalfWidth : 0.76;
    const hl = D ? D.tableHalfLength : 1.37;
    const aim = new THREE.Vector3(
      (Math.random() * 2 - 1) * hw * 0.55,
      (D ? D.tableTopY : 0.76) + 0.22,
      (D ? D.tableCenterZ : 0) + hl * (0.35 + Math.random() * 0.4),
    );
    const dir = aim.sub(b.pos).normalize();
    const speed = Math.min(L * DUELO_P.boost,
      (D && D.maxBallSpeed ? D.maxBallSpeed : 12) * 0.95);
    v.copy(dir).multiplyScalar(speed);
    b.spin.set(0, 0, 0);
    // pelota OSCURA (casi negra, «manchada» por el disparo)
    this.ctrl._ballDarkApply();
    g.rules.message = tx('duelo_falla');
    this.ctrl._setStateSilent('angry', 2.2);
    // la bola RETOMA el juego YA (desde donde estaba parada, nueva ruta)
    g.freezeT = 0;
  }
  _holster() {
    // la bala desaparece en la colisión (v2.120: el pool NO se dispone —
    // sólo se descolga del rig; geometrías/materiales son de módulo)
    if (this.bullet) {
      this.game.rig.remove(this.bullet);
      this.bullet = null;
    }
    if (this.bulletGlow) {
      this.game.rig.remove(this.bulletGlow);
      this.bulletGlow = null;
    }
    this.phase = 'out';
    this.t = 0;
    // v2.90: la mira láser se apaga con el duelo
    if (this.ctrl.fx) this.ctrl.fx.laserVisible(false);
    // fin del duelo: recuperamos la PALA (v2.89)
    this.ctrl._paddleGunApply(false);
  }
  dispose() {
    const g = this.game;
    if (this.mesh) {
      g.rig.remove(this.mesh);
      // el GLB en CACHÉ no se destruye; el de reserva, sí
      if (!this.ctrl._revolverModel) this._disposeTree(this.mesh);
      this.mesh = null;
    }
    if (this.bullet) { g.rig.remove(this.bullet); this.bullet.geometry.dispose(); this.bullet.material.dispose(); this.bullet = null; }
    if (this.bulletGlow) { g.rig.remove(this.bulletGlow); this.bulletGlow.geometry.dispose(); this.bulletGlow.material.dispose(); this.bulletGlow = null; }
    this.ctrl._dianaHide();
    if (this.ctrl.fx) this.ctrl.fx.laserVisible(false);   // v2.90
    this.ctrl._paddleGunApply(false);   // la pala SIEMPRE vuelve (v2.89)
    this.done = true;
  }
  _disposeTree(o) {
    o.traverse((n) => {
      if (n.geometry) n.geometry.dispose();
      if (n.material) {
        const mats = Array.isArray(n.material) ? n.material : [n.material];
        for (const mm of mats) { if (mm.map) mm.map.dispose(); mm.dispose(); }
      }
    });
  }
}

/* ============================================================================
 *  v2.107 · POSE DEL VISOR SIN RETARDO (compartida por SangreCara y
 *  SangreManchon). ANTES se copiaba g.camera: three.js sincroniza esa
 *  cámara DENTRO de render(), así que en el callback de animación traía
 *  la pose del FRAME ANTERIOR — la sangre «nadaba» un pelín al girar la
 *  cabeza (el «seguimiento de cabeza» que reportó el artista). La cámara
 *  XR (renderer.xr.getCamera()) SÍ se actualiza ANTES del callback
 *  (WebXRManager.onAnimationFrame), así que copiarla = imagen FIJA en la
 *  pantalla del visor, sin seguimiento del mundo y sin retardo. Respaldo:
 *  fuera de VR (escritorio/headless) se sigue usando g.camera.
 *  ============================================================================ */
function visorPose(g, group) {
  let ok = false;
  try {
    const xr = g.renderer && g.renderer.xr;
    if (xr && xr.isPresenting && typeof xr.getCamera === 'function') {
      const cx = xr.getCamera();
      if (cx) {
        group.position.copy(cx.position);
        group.quaternion.copy(cx.quaternion);
        ok = true;
      }
    }
  } catch (e) { ok = false; }
  if (!ok && g.camera) {
    group.position.copy(g.camera.position);
    group.quaternion.copy(g.camera.quaternion);
  }
  return ok;
}

/* ============================================================================
 *  v2.93/107 · SANGRE EN LA PANTALLA — el forajido GANA el duelo (o nos
 *  acierta en el ASEDIO, v2.107) y su disparo NOS SALPICA la cara.
 *  ---------------------------------------------------------------------
 *  La cámara se llena de sangre pegada al VISOR: grupo bloqueado a la
 *  CABEZA con la pose de la CÁMARA XR del frame en curso (visorPose —
 *  imagen FIJA, sin seguimiento del mundo ni retardo) a 0,5 m del rostro.
 *  v2.107 · SALPICADÓN FIJO: cada disparo pinta sobre un canvas UNA
 *  mancha grande (blob central + satélites + regueros) = «imagen fija en
 *  la pantalla del visor»; ENCIMA siguen las GOTAS que ESCURREN con su
 *  reguero animado (más gotas y más gordas: 20 + 14 salpicaduras fijas).
 *  Todo el conjunto se DESVANECE en ~10 s mientras la partida SIGUE:
 *  molesta PARCIALMENTE la visión, sin colisiones, sin raycast y sin
 *  tocar el juego.
 *
 *  Rendimiento (lección de la dinamita v2.92): pool PRE-CREADO (20 gotas
 *  con su reguero + 14 salpicaduras fijas + fogonazo rojo + 1 quad del
 *  salpicadón), CERO asignaciones por frame, materiales compartidos con
 *  opacidad global y texturas de canvas generadas UNA sola vez (el
 *  salpicadón se repinta SOLO al recibir un disparo nuevo, liberando la
 *  textura anterior). ~65 mallas MeshBasicMaterial: nada para la Quest 3.
 *  ============================================================================ */
class SangreCara {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.group = null;
    this.on = false;
    this.t = 0;
    this.flashT = 0;
    this.built = false;
    this.drops = [];          // { mesh, trail, x, y, y0, vy, size, delay, g, phase }
    this.dots = [];           // salpicadura fija { mesh, delay, size }
    this.flash = null;
    this.splat = null;        // v2.107: SALPICADÓN FIJO (imagen en el visor)
    this.texSplat = null;
    this.matSplat = null;
    this.matDrop = null; this.matTrail = null; this.matFlash = null;
    this.geoDrop = null; this.geoTrail = null; this.geoFlash = null;
    this.texTrail = null; this.texFlash = null;
  }

  /* Constantes del efecto (t = tiempo desde el disparo): */
  static get DUR() { return 10.5; }      // s total («desapareciendo ~10 s»)
  static get FADE0() { return 7.8; }     // s donde empieza el desvanecido
  static get Z_FACE() { return -0.5; }   // m delante del rostro (visor)
  static get Y_MIN() { return -0.42; }   // m: borde inferior del reguero

  /** Construye el pool UNA vez (perezoso: nada en escena hasta el 1er disparo). */
  _build() {
    if (this.built) return;
    const g = this.game;
    this.group = new THREE.Group();
    this.group.visible = false;
    this.group.renderOrder = 962;
    g.rig.add(this.group);

    // textura del REGUERO: banda vertical suave, más sangre arriba (el
    // punto de impacto) que junto a la gota. UNA vez, 32x64.
    const cv = document.createElement('canvas');
    cv.width = 32; cv.height = 64;
    const c2 = cv.getContext('2d');
    const gr = c2.createLinearGradient(0, 0, 0, 64);
    gr.addColorStop(0.0, 'rgba(110,13,18,0.95)');   // v=1 · punto de impacto
    gr.addColorStop(0.55, 'rgba(110,13,18,0.72)');
    gr.addColorStop(1.0, 'rgba(110,13,18,0.40)');   // v=0 · junto a la gota
    c2.fillStyle = gr;
    c2.fillRect(0, 0, 32, 64);
    c2.globalCompositeOperation = 'destination-in';
    const gh = c2.createLinearGradient(0, 0, 32, 0);
    gh.addColorStop(0.0, 'rgba(0,0,0,0)');
    gh.addColorStop(0.35, 'rgba(0,0,0,1)');
    gh.addColorStop(0.65, 'rgba(0,0,0,1)');
    gh.addColorStop(1.0, 'rgba(0,0,0,0)');
    c2.fillStyle = gh;
    c2.fillRect(0, 0, 32, 64);
    this.texTrail = new THREE.CanvasTexture(cv);

    // textura del FOGONAZO rojo: salpicadura radial desde el centro.
    const cv2 = document.createElement('canvas');
    cv2.width = 128; cv2.height = 128;
    const c3 = cv2.getContext('2d');
    const gr2 = c3.createRadialGradient(64, 64, 6, 64, 64, 64);
    gr2.addColorStop(0.0, 'rgba(146,18,22,0.62)');
    gr2.addColorStop(0.45, 'rgba(120,12,16,0.28)');
    gr2.addColorStop(1.0, 'rgba(120,12,16,0)');
    c3.fillStyle = gr2;
    c3.fillRect(0, 0, 128, 128);
    this.texFlash = new THREE.CanvasTexture(cv2);

    // materiales compartidos (opacidad global animada; visor: sin depth)
    this.matDrop = new THREE.MeshBasicMaterial({
      color: 0x6e0d12, transparent: true, opacity: 0.92,
      depthTest: false, depthWrite: false, fog: false,
    });
    this.matTrail = new THREE.MeshBasicMaterial({
      color: 0x7a1015, map: this.texTrail, transparent: true, opacity: 0.62,
      depthTest: false, depthWrite: false, fog: false, side: THREE.DoubleSide,
    });
    this.matFlash = new THREE.MeshBasicMaterial({
      color: 0xffffff, map: this.texFlash, transparent: true, opacity: 0,
      depthTest: false, depthWrite: false, fog: false, side: THREE.DoubleSide,
    });

    // geometrías compartidas
    this.geoDrop = new THREE.SphereGeometry(1, 10, 8);
    this.geoTrail = new THREE.PlaneGeometry(1, 1);
    this.geoTrail.translate(0, -0.5, 0);   // borde SUPERIOR en el origen: crece hacia abajo
    this.geoFlash = new THREE.PlaneGeometry(2.4, 2.4);

    // pool de gotas que ESCURREN (cada una con su reguero) — v2.107: 20
    for (let i = 0; i < 20; i++) {
      const mesh = new THREE.Mesh(this.geoDrop, this.matDrop);
      const trail = new THREE.Mesh(this.geoTrail, this.matTrail);
      mesh.renderOrder = 964;
      trail.renderOrder = 962;
      mesh.visible = false;
      trail.visible = false;
      mesh.position.z = SangreCara.Z_FACE;
      trail.position.z = SangreCara.Z_FACE - 0.002;
      this.group.add(mesh);
      this.group.add(trail);
      this.drops.push({ mesh, trail, x: 0, y: 0, y0: 0, vy: 0, size: 0.01, delay: 0, g: 0.2, phase: 0 });
    }
    // pool de salpicadura FIJA (microgotas que no escurren) — v2.107: 14
    for (let i = 0; i < 14; i++) {
      const mesh = new THREE.Mesh(this.geoDrop, this.matDrop);
      mesh.renderOrder = 964;
      mesh.visible = false;
      mesh.position.z = SangreCara.Z_FACE + 0.002;
      this.group.add(mesh);
      this.dots.push({ mesh, delay: 0, size: 0.003 });
    }
    // fogonazo rojo del impacto en la cara
    this.flash = new THREE.Mesh(this.geoFlash, this.matFlash);
    this.flash.renderOrder = 960;
    this.flash.visible = false;
    this.flash.position.z = SangreCara.Z_FACE - 0.01;
    this.group.add(this.flash);
    // v2.107 · SALPICADÓN FIJO (la «imagen fija en la pantalla del
    // visor»): quad grande con la mancha PINTADA del disparo. La textura
    // se repinta en cada trigger() (aleatoria: cada disparo es distinto)
    // y se libera al parar — mientras dura, es una imagen quieta.
    this.matSplat = new THREE.MeshBasicMaterial({
      color: 0xffffff, transparent: true, opacity: 0.88,
      depthTest: false, depthWrite: false, fog: false,
      side: THREE.DoubleSide,
    });
    this.splat = new THREE.Mesh(
      new THREE.PlaneGeometry(1.06, 0.74), this.matSplat);
    this.splat.renderOrder = 963;
    this.splat.visible = false;
    this.splat.position.set(0, 0.10, SangreCara.Z_FACE - 0.004);
    this.group.add(this.splat);
    this.built = true;
  }

  /** v2.107 · PINTA el salpicadón fijo del visor (canvas 384x256 → textura).
   *  Mancha central irregular + satélites + regueros que cuelgan: la
   *  silueta de un buen salpicón en la lente. Cada disparo repinta (aleatorio). */
  _paintSplat() {
    const cv = document.createElement('canvas');
    cv.width = 384; cv.height = 256;
    const c = cv.getContext('2d');
    const blob = (x, y, r, a) => {
      const rg = c.createRadialGradient(x, y, r * 0.15, x, y, r);
      rg.addColorStop(0, 'rgba(112,10,14,' + a + ')');
      rg.addColorStop(0.72, 'rgba(96,8,12,' + a * 0.82 + ')');
      rg.addColorStop(1, 'rgba(96,8,12,0)');
      c.fillStyle = rg;
      c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    };
    // mancha central desplazada AL AZAR (el impacto nunca es igual)
    const cx = 192 + (Math.random() - 0.5) * 96;
    const cy = 108 + (Math.random() - 0.5) * 44;
    blob(cx, cy, 58 + Math.random() * 22, 0.95);
    blob(cx - 34 - Math.random() * 18, cy + 18, 30, 0.9);
    blob(cx + 38 + Math.random() * 20, cy + 12, 26, 0.86);
    blob(cx + 6, cy - 34, 20, 0.8);
    // satélites alrededor
    const nS = 16 + (Math.random() * 8) | 0;
    for (let i = 0; i < nS; i++) {
      const a = Math.random() * Math.PI * 2;
      const rr = 62 + Math.random() * 74;
      blob(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr * 0.72,
        2.5 + Math.random() * 8, 0.5 + Math.random() * 0.4);
    }
    // regueros que cuelgan (ya pintados en la imagen fija)
    const nD = 3 + (Math.random() * 3) | 0;
    for (let i = 0; i < nD; i++) {
      const x = cx + (Math.random() - 0.5) * 120;
      const w = 6 + Math.random() * 9;
      const h = 40 + Math.random() * 78;
      const grd = c.createLinearGradient(0, cy, 0, cy + h);
      grd.addColorStop(0, 'rgba(104,9,13,0.85)');
      grd.addColorStop(1, 'rgba(104,9,13,0.25)');
      c.fillStyle = grd;
      c.fillRect(x - w / 2, cy - 8, w, h);
      blob(x, cy + h, w * 0.85, 0.75);
    }
    // libera la textura ANTERIOR antes de crear la nueva (higiene GPU)
    if (this.texSplat) {
      try { this.texSplat.dispose(); } catch (e) { /* */ }
      this.texSplat = null;
    }
    this.texSplat = new THREE.CanvasTexture(cv);
    this.texSplat.colorSpace = THREE.SRGBColorSpace;
    this.matSplat.map = this.texSplat;
    this.matSplat.needsUpdate = true;
  }

  /** ¡EL FORAJIDO NOS HA DADO! (re-armable: nuevo duelo perdido = nueva salpicadura) */
  trigger() {
    this._build();
    this.t = 0;
    this.flashT = 0.95;
    this.on = true;
    this.group.visible = true;
    // pose de cabeza YA (cámara XR del frame: imagen FIJA en el visor)
    const g = this.game;
    visorPose(g, this.group);
    // v2.107: SALPICADÓN FIJO repintado — cada disparo deja una mancha
    // distinta, quieta en la pantalla del visor mientras se escurre.
    // v2.116: el QUAD del salpicadón también SE MUEVE por la pantalla
    // (posición y giro al azar) — antes siempre centrado y derecho.
    this._paintSplat();
    this.splat.position.set(
      (Math.random() * 2 - 1) * 0.22,
      0.10 + (Math.random() * 2 - 1) * 0.13,
      SangreCara.Z_FACE - 0.004);
    this.splat.rotation.z = (Math.random() * 2 - 1) * 0.55;
    this.splat.visible = true;
    this.matSplat.opacity = 0.88;
    // gotas escurridoras: reparto en la mitad ALTA del visor, algo
    // cargado al centro; varias GRANDES para leer «salpicadura»
    for (let i = 0; i < this.drops.length; i++) {
      const d = this.drops[i];
      const cx = (Math.random() * 2 - 1);
      d.x = cx * 0.46 * (0.55 + Math.random() * 0.45);
      d.y0 = 0.12 + Math.random() * 0.32;
      d.y = d.y0;
      d.vy = 0.04 + Math.random() * 0.05;
      d.size = (i < 3) ? (0.014 + Math.random() * 0.006)   // 3 gordas
        : (0.005 + Math.random() * 0.008);
      d.delay = Math.random() * 2.2;                        // la salpicadura CAE muy escalonada
      d.g = 0.13 + Math.random() * 0.16;                    // cada gota escurre a su ritmo
      d.phase = Math.random() * Math.PI * 2;
      d.mesh.visible = false;
      d.mesh.scale.setScalar(d.size);
      d.trail.visible = false;
      d.trail.scale.set(d.size * 1.9, 0.001, 1);
      d.trail.position.set(d.x, d.y0, SangreCara.Z_FACE - 0.002);
    }
    for (let i = 0; i < this.dots.length; i++) {
      const s = this.dots[i];
      s.delay = Math.random() * 0.5;
      s.size = 0.0025 + Math.random() * 0.004;
      s.mesh.visible = false;
      s.mesh.scale.setScalar(s.size);
      s.mesh.position.set(
        (Math.random() * 2 - 1) * 0.5,
        -0.05 + Math.random() * 0.52,
        SangreCara.Z_FACE + 0.002);
    }
    this.flash.visible = true;
    this.matFlash.opacity = 0.55;
    this.matDrop.opacity = 0.92;
    this.matTrail.opacity = 0.62;
  }

  /** Paro INMEDIATO (salida de la sala / fin del ciclo): sin desvanecido
   *  y con las opacidades RESTAURADAS para el próximo disparo. La textura
   *  del salpicadón se LIBERA (v2.107: higiene GPU entre disparos). */
  stop() {
    this.on = false;
    if (!this.built) return;
    this.group.visible = false;
    this.splat.visible = false;
    this.matDrop.opacity = 0.92;
    this.matTrail.opacity = 0.62;
    this.matFlash.opacity = 0;
    this.matSplat.opacity = 0.88;
    if (this.texSplat) {
      try { this.texSplat.dispose(); } catch (e) { /* */ }
      this.texSplat = null;
      this.matSplat.map = null;
      this.matSplat.needsUpdate = true;
    }
    for (let i = 0; i < this.drops.length; i++) {
      this.drops[i].mesh.visible = false;
      this.drops[i].trail.visible = false;
    }
    for (let i = 0; i < this.dots.length; i++) this.dots[i].mesh.visible = false;
    this.flash.visible = false;
  }

  /** Frame a frame: visor bloqueado (pose XR del frame), escurrido,
   *  reguero y desvanecido. CERO asignaciones: sólo aritmética. */
  update(dt) {
    if (!this.on || !this.built) return;
    const g = this.game;
    this.t += dt;
    if (this.t >= SangreCara.DUR) { this.stop(); return; }
    // 1) grupo PEGADO AL VISOR: cámara XR del frame EN CURSO (imagen fija)
    visorPose(g, this.group);
    // 2) fogonazo rojo inicial (decae rápido, cuadrático)
    if (this.flashT > 0) {
      this.flashT -= dt;
      const k = Math.max(0, this.flashT / 0.95);
      this.matFlash.opacity = 0.55 * k * k;
      if (this.flashT <= 0) this.flash.visible = false;
    }
    // 3) desvanecido global (~8 → 10,5 s): gotas, regueros y salpicadón JUNTOS
    const fade = (this.t <= SangreCara.FADE0) ? 1
      : 1 - (this.t - SangreCara.FADE0) / (SangreCara.DUR - SangreCara.FADE0);
    this.matDrop.opacity = 0.92 * fade;
    this.matTrail.opacity = 0.62 * fade;
    this.matSplat.opacity = 0.88 * fade;
    // 4) gotas: nacen escalonadas, ESCURREN con gravedad de visor y
    //    estiran su reguero entre el impacto y la posición actual
    const yMin = SangreCara.Y_MIN;
    for (let i = 0; i < this.drops.length; i++) {
      const d = this.drops[i];
      if (d.delay > 0) {
        d.delay -= dt;
        if (d.delay > 0) continue;
        d.mesh.visible = true;          // nace justo al agotarse el retardo
        d.trail.visible = true;
      }
      // gravedad de visor PROPIA DE CADA GOTA (0,13-0,29 m/s²): unas
      // escurren pronto y otras tardan — el reguero evoluciona todo el ciclo
      d.vy += d.g * dt;
      d.y -= d.vy * dt;
      if (d.y < yMin) { d.y = yMin; d.vy = 0; }   // charco abajo: se queda
      // deriva lateral mínima (la gota «busca» camino)
      d.x += Math.sin(this.t * 1.6 + d.phase) * 0.004 * dt;
      d.mesh.position.set(d.x, d.y, SangreCara.Z_FACE);
      const len = d.y0 - d.y;
      if (len > d.size * 1.2) {
        d.trail.visible = true;
        d.trail.position.set(d.x, d.y0, SangreCara.Z_FACE - 0.002);
        d.trail.scale.set(d.size * 1.9, len, 1);
      } else {
        d.trail.visible = false;
      }
    }
    // 5) salpicadura fija: sólo el retardo de aparición
    for (let i = 0; i < this.dots.length; i++) {
      const s = this.dots[i];
      if (s.delay > 0) {
        s.delay -= dt;
        if (s.delay <= 0) s.mesh.visible = true;
      }
    }
  }
}

/* ============================================================================
 *  v2.86/90 · SUPERPODER 2: «DINAMITA» — SALVA DE 2 A 5 CARTUCHOS (v2.90).
 *  El forajido lanza ENTRE 2 Y 5 cartuchos (small_tnt.glb) con la mecha
 *  encendida a PUNTOS ALEATORIOS de la mesa, con 1 SEGUNDO entre
 *  lanzamiento y lanzamiento (explotan en momentos distintos). El ARCO de
 *  lanzamiento NUNCA supera la altura del techo: el ápice se limita por
 *  debajo de la altura real de la sala (2,85 m). La partida SIGUE
 *  normalmente — si la bola pasa por una explosión, SALE DESPEDIDA en una
 *  dirección cualquiera. SIN contador 3·2·1, SIN «bullet time» y SIN punto
 *  regalado: solo el caos de las explosiones. Los cartuchos se pueden
 *  seguir BATEANDO con la pala en pleno vuelo (estallan lejos, sin daño).
 *  Estados de CADA cartucho:
 *    fly    — vuelo parabólico con volteretas; interceptable con la pala
 *    fused  — posado en la mesa: mecha de 2 s chispeando (sin contador)
 *    bateada— golpeada en vuelo: vuela lejos y estalla en el aire
 *    boom   — fogonazo + HUMO + CORTINA DENSA + MANCHÓN (~6 s) + onda
 *             expansiva (blastT) que desvía la bola si pasa cerca
 *  ============================================================================ */
class DinamitaAction {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.done = false;
    this.phase = 'idle';
    this.t = 0;
    this.carts = [];        // los cartuchos de la salva (v2.90)
    this.blasts = [];       // ondas expansivas activas (desvían la bola)
    this._n = 0;            // cartuchos de esta salva (2..5)
    this._launched = 0;
    this._launchT = 0;
    this._finT = 0;
    this.totalT = 0;        // duración estimada (para el cooldown de poderes)
    this._hissT = 0;
  }
  start() {
    const g = this.game;
    // v2.90: SALVA de 2 a 5 cartuchos
    this._n = DINAMITA.cartMin +
      ((Math.random() * (DINAMITA.cartMax - DINAMITA.cartMin + 1)) | 0);
    this._launched = 0;
    this._launchT = 0.05;   // el primero sale YA
    this.phase = 'volley';
    this.t = 0;
    this.totalT = (this._n - 1) * DINAMITA.intervalo + 2.6 +
      DINAMITA.mechaT + DINAMITA.blastT + 0.8;
    this.ctrl._setStateSilent('picando', 1.6);
  }
  /** NUEVO CARTUCHO de la salva: objetivo ALEATORIO de la mesa y arco con
   *  el ápice LIMITADO por la altura del techo (v2.90: nunca se pasa). */
  _nuevoCartucho() {
    const g = this.game;
    const D = ODIMS();
    const mesh = this.ctrl._tntModel
      ? this.ctrl._tntModel.clone(true)
      : this._fallbackTnt();
    const c = {
      mesh, halo: null,
      pos: new THREE.Vector3(), vel: new THREE.Vector3(),
      t: 0, phase: 'fly', fuseT: 0, hissT: 0,
      spinA: 5.5 + Math.random() * 4, spinB: 3.5 + Math.random() * 3,
      s0: mesh.scale.x || 1,
    };
    // sale de la mano del forajido (con un poco de variación por cartucho)
    c.pos.set(DUELO.x - 0.28 + (Math.random() - 0.5) * 0.22, 1.55,
      DUELO.z + 0.5 + (Math.random() - 0.5) * 0.2);
    // objetivo: CUALQUIER punto de la mesa (entera, ambos lados)
    const tx = (Math.random() * 2 - 1) * D.tableHalfWidth * 0.82;
    const tz = D.tableCenterZ + (Math.random() * 2 - 1) * D.tableHalfLength * 0.75;
    // el objetivo del arco es la SUPERFICIE de la mesa (pivote base-en-origen)
    const ty = D.tableTopY + 0.02;
    // v2.90 · ARCO BAJO EL TECHO: balística con el ápice ELEGIDO. Se lanza
    // con la vy que da EXACTAMENTE el ápice pedido (min entre el arco bonito
    // y el máximo permitido por la sala) — la integración sigue siendo la de
    // siempre (gravedad única), así que el vuelo es físicamente exacto.
    const salaH = (window.__PP_CORE && window.__PP_CORE.DIMS &&
      window.__PP_CORE.DIMS.roomHeight) || 2.85;
    const y0 = c.pos.y;
    const apex = Math.max(y0 + 0.12,
      Math.min(y0 + DINAMITA.apexUp, salaH - DINAMITA.techoMargen));
    const vy = Math.sqrt(2 * DINAMITA.g * Math.max(0.05, apex - y0));
    const T = (vy + Math.sqrt(vy * vy + 2 * DINAMITA.g * (y0 - ty))) / DINAMITA.g;
    c.vueloT = T;
    c.vel.set((tx - c.pos.x) / T, vy, (tz - c.pos.z) / T);
    // el clon conserva la normalización del GLB (nada de pisar la escala fija)
    c.mesh.position.copy(c.pos);
    // brillo propio cálido en TODOS sus materiales (visible en el saloon)
    c.mesh.traverse((n) => {
      if (n.isMesh && n.material && n.material.emissive) {
        n.material.emissive.setHex(0x8a3410);
        n.material.emissiveIntensity = 0.55;
      }
    });
    // HALO aditivo que viaja con el cartucho (se ve aunque el GLB falle)
    try {
      c.halo = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texPuff, color: 0xff8a3c, transparent: true,
        opacity: 0.30, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      c.halo.scale.setScalar(0.34);
      c.halo.renderOrder = 13;
      g.rig.add(c.halo);
      c.halo.position.copy(c.pos);
    } catch (e) { c.halo = null; }
    g.rig.add(c.mesh);
    this.carts.push(c);
    this.ctrl.sfx('lanzar', 0.35);
  }
  /** Reserva: cartucho de cajas (rojo brillante con mecha) si el GLB no llegó. */
  _fallbackTnt() {
    const grp = new THREE.Group();
    const rojo = new THREE.MeshStandardMaterial({
      color: 0xb03018, roughness: 0.6, metalness: 0.05,
      emissive: 0x7a1e08, emissiveIntensity: 0.6,
    });
    const palo = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.15, 12), rojo);
    palo.rotation.z = Math.PI / 2;
    const cinta = new THREE.Mesh(new THREE.CylinderGeometry(0.037, 0.037, 0.03, 12),
      new THREE.MeshStandardMaterial({ color: 0xd9a441, roughness: 0.6, emissive: 0x6a4410, emissiveIntensity: 0.5 }));
    cinta.rotation.z = Math.PI / 2;
    const mecha = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.06, 6),
      new THREE.MeshStandardMaterial({ color: 0x2c2018, roughness: 0.9 }));
    mecha.position.set(0.06, 0.05, 0);
    mecha.rotation.z = -0.5;
    const brasa = new THREE.Mesh(new THREE.SphereGeometry(0.011, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0xffb45f }));
    brasa.position.set(0.086, 0.072, 0);
    grp.add(palo, cinta, mecha, brasa);
    grp.scale.setScalar(DINAMITA.escala / 0.2);
    return grp;
  }
  /** Punta de la MECHA (chispas) de un cartucho, en espacio RIG.
   *  v2.92: escribe en un temporal de módulo (se llama por cartucho y por
   *  frame; fx.mecha COPIA la posición, así que el temporal se consume al
   *  momento — cero basura por frame). */
  _mechaTip(c) {
    const p = c.mesh ? c.mesh.position : c.pos;
    return _OE_V1.set(p.x + 0.05, p.y + DINAMITA.radio * 1.6, p.z);
  }
  /** Barrido pala-cartucho: 4 muestras entre prev y pos del mando. */
  _paddleHit(ps, c) {
    const R = DINAMITA.palaRadio;
    for (let k = 0; k <= 4; k++) {
      const f = k / 4;
      const px = ps.prev.x + (ps.pos.x - ps.prev.x) * f;
      const py = ps.prev.y + (ps.pos.y - ps.prev.y) * f;
      const pz = ps.prev.z + (ps.pos.z - ps.prev.z) * f;
      const dx = c.pos.x - px, dy = c.pos.y - py, dz = c.pos.z - pz;
      if (dx * dx + dy * dy + dz * dz < R * R) return true;
    }
    return false;
  }
  /** GOLPE CON LA PALA en vuelo: sale despedida hacia el rival (sin daño). */
  _batear(ps, c) {
    const g = this.game;
    const dir = new THREE.Vector3(
      (c.pos.x - ps.pos.x) + 0.4,
      0.55,
      -(Math.abs(c.pos.z - DUELO.z) + 1.2),
    ).normalize();
    c.vel.copy(dir).multiplyScalar(DINAMITA.bateoVel);
    c.vel.y = DINAMITA.bateoSube;
    c.phase = 'bateada';
    c.t = 0;
    this.ctrl.sfx('pala', 0);
    this.ctrl.fx.spark(c.pos, 8, 0xffd77a, 2.2, 1);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.65, 90);
    g.rules.message = tx('dyn_bateada');
    this.ctrl._setStateSilent('surprised', 2.0);
  }
  /** Tocó la mesa: se planta y la mecha arde 2 s (SIN contador, SIN
   *  «bullet time»: la partida sigue en todo momento).
   *  v2.106 · SE QUEDA TOTALMENTE ESTÁTICA: nada de volteo, bote ni
   *  rodadura — aterriza donde aterriza y se queda clavada hasta estallar
   *  (petición del artista: «cuando impacta en la mesa se queda estática
   *  sin girar»). */
  _aterrizar(c) {
    const g = this.game;
    const D = ODIMS();
    c.phase = 'fused';
    c.t = 0;
    c.fuseT = DINAMITA.mechaT;
    c._fuseY = D.tableTopY + 0.004;
    c.pos.y = c._fuseY;
    c.vel.set(0, 0, 0);
    c.mesh.position.copy(c.pos);
    // v2.106: SOLO se conserva el giro PLANO del aterrizaje — el cartucho
    // queda TUMBADO en el punto exacto de impacto, sin animación alguna.
    c.mesh.rotation.order = 'YXZ';
    c.yaw0 = c.mesh.rotation.y || (Math.random() * Math.PI * 2);
    c.mesh.rotation.set(0, c.yaw0, 0);
    c.mesh.scale.setScalar(c.s0);
    // v2.92 · BRASA SIN LUCES: hasta ahora cada cartucho posado añadía un
    // PointLight — Three.js recompila TODOS los programas de shaders al
    // cambiar el número de luces (y cada luz viva cuesta fragment en la
    // Quest): con una salva de 5 el juego iba «a saltos». La LUZ cálida
    // la SIMULA el halo aditivo que ya viaja con el cartucho: más grande,
    // más naranja y latiendo (el relajo del flash de la explosión no
    // cambia). Cero recompilaciones, cero coste por fragmento.
    if (c.halo) {
      c.halo.material.color.setHex(0xff7a30);
      c.halo.material.opacity = 0.5;
      c.halo.scale.setScalar(0.44);
      c.halo.position.copy(c.pos).add(_OE_V2.set(0, 0.10, 0));
    }
    g.rules.message = tx('dyn_mesa');
    this.ctrl.sfx('aterrizar', 0);
    this.ctrl.fx.spark(c.pos, 10, 0xffe9a0, 2.4, 1.2);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 140);
  }
  /** Explosión de UN cartucho: FX completos + manchón + ONDA EXPANSIVA que
   *  desvía la bola si pasa cerca. La partida SIGUE: nada de puntos aquí. */
  _boom(c, onTable) {
    const g = this.game;
    const D = ODIMS();
    c.phase = 'boom';
    // FX: fogonazo + chispas + HUMO CARTOON + CORTINA DENSA + MANCHÓN
    this.ctrl.fx.flash(c.pos, 2.6, 0xffb45f);
    this.ctrl.fx.spark(c.pos, 16, 0xffcf7a, 4.2, 1.6);
    this.ctrl.fx.smoke(c.pos, 8, true);
    // CORTINA DE HUMO DENSA que tapa ALGO la bola ~6 s y se desvanece (v2.89)
    this.ctrl.fx.smokeCurtain(c.pos, 9);
    this.ctrl.sfx('boom', c.pos.x > 0 ? 0.35 : -0.15);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 1.0, 220);
    // el manchón: DEBAJO de donde ha explotado (mesa o suelo)
    if (onTable) {
      this.ctrl.fx.scorch(c.pos.x, D.tableTopY + 0.004, c.pos.z, 1.05);
    } else {
      const gx = clamp(c.pos.x, -D.roomHalfX + 0.4, D.roomHalfX - 0.4);
      const gz = clamp(c.pos.z, D.roomFrontZ + 0.4, D.roomBackZ - 0.4);
      this.ctrl.fx.scorch(gx, 0.005, gz, 1.2);
    }
    // v2.90 · ONDA EXPANSIVA: durante blastT segundos, si la bola pasa por
    // aquí SALE DESPEDIDA en una dirección cualquiera (la partida sigue).
    this.blasts.push({
      pos: c.pos.clone(), r: DINAMITA.blastR,
      t: DINAMITA.blastT, hit: false,
    });
    g.rules.message = tx('dyn_boom');
    if (onTable && g.rules.state === 'rally') {
      this.ctrl._setStateSilent('laughing', 2.2);
    }
    // el cartucho desaparece con la explosión (el halo también)
    if (c.mesh) {
      g.rig.remove(c.mesh);
      if (!this.ctrl._tntModel) this._disposeTree(c.mesh);
      c.mesh = null;
    }
    if (c.halo) { g.rig.remove(c.halo); c.halo.material.dispose(); c.halo = null; }
  }
  /** v2.90 · LA BOLA SALE DESPEDIDA por la explosión: dirección CUALQUIERA
   *  (azimut aleatorio, elevación mayormente lateral/arriba), velocidad
   *  barajada y acotada. El árbitro decide el punto con las reglas de
   *  siempre — nada se regala a nadie. */
  _desviarBola(b) {
    const g = this.game;
    const D = ODIMS();
    const az = Math.random() * Math.PI * 2;
    const el = -0.12 + Math.random() * 0.68;   // entre -7° y +32°
    const dir = new THREE.Vector3(
      Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el));
    const sp = THREE.MathUtils.clamp(
      b.vel.length() * (0.9 + Math.random() * 0.5), 2.6,
      (D && D.maxBallSpeed ? D.maxBallSpeed : 12) * 0.95);
    b.vel.copy(dir).multiplyScalar(sp);
    b.spin.set(0, 0, 0);
    this.ctrl.fx.spark(b.pos, 12, 0xffcf7a, 3.4, 1.4);
    this.ctrl.fx.flash(b.pos, 1.1, 0xffb45f);
    this.ctrl.sfx('impacto', 0.2);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 140);
    g.rules.message = tx('dyn_desvia');
  }
  update(dt) {
    if (this.done || this.phase === 'idle') return;
    const g = this.game;
    const D = ODIMS();
    this.t += dt;
    // v2.106 · LA BOLA TAMBIÉN DETONA el cartucho: barrido del recorrido de
    // la bola del frame (prev→pos) contra esfera generosa — en vuelo o
    // posada en la mesa, si la pelota/bomba pasa cerca REVIENTA (antes la
    // salvava sólo la PALA y «nunca se llegaba a impactar con la bola»).
    if (g.ball && g.rules.state === 'rally') {
      const b = g.ball;
      const bp = b.pos;
      if (!this._pb) this._pb = bp.clone();
      const R = 0.15 + (D ? D.ballRadius : 0.02);
      for (const c of this.carts) {
        if (c.phase === 'boom' || !c.mesh) continue;
        // punto más cercano del segmento prev→pos al cartucho
        _OE_V1.copy(bp).sub(this._pb);
        const L2 = _OE_V1.lengthSq();
        let tt = 0;
        if (L2 > 1e-8) {
          tt = THREE.MathUtils.clamp(
            _OE_V2.copy(c.pos).sub(this._pb).dot(_OE_V1) / L2, 0, 1);
        }
        _OE_V2.multiplyScalar(tt).add(this._pb);
        if (_OE_V2.distanceToSquared(c.pos) < R * R) {
          this._boom(c, c.phase === 'fused');
          break;
        }
      }
      this._pb.copy(bp);
    }
    // PROGRAMADOR de la salva: un lanzamiento cada DINAMITA.intervalo
    if (this._launched < this._n) {
      this._launchT -= dt;
      if (this._launchT <= 0) {
        this._nuevoCartucho();
        this._launched++;
        this._launchT = DINAMITA.intervalo;
      }
    }
    // cada cartucho: vuelo → mecha en la mesa → explosión
    let vivos = 0;
    for (const c of this.carts) {
      if (c.phase === 'boom') continue;
      vivos++;
      c.t += dt;
      // chispas de la mecha SIEMPRE + bufido (tic-tac limitado GLOBALMENTE:
      // cada tic crea nodos de audio y en salvas de 5 la lluvia pesa)
      this.ctrl.fx.mecha(this._mechaTip(c), c.phase === 'fused' ? 3 : 2);
      c.hissT -= dt;
      if (c.hissT <= 0) {
        c.hissT = 0.22;
        const nowS = performance.now() / 1000;
        if (nowS - (this._mechaSfxLast || 0) >= 0.07) {
          this._mechaSfxLast = nowS;
          this.ctrl.sfx('mecha', 0);
        }
      }
      // el HALO sigue al cartucho — v2.92: en vuelo, latido suave; en
      // 'fused' manda la BRASA (más grande, naranja, latido rápido — la
      // sustituta sin luces del antiguo PointLight)
      if (c.halo) {
        c.halo.position.copy(c.pos);
        if (c.phase === 'fused') {
          c.halo.position.y += 0.10;
          c.halo.material.opacity = 0.42 + Math.sin(c.t * 22) * 0.16;
          c.halo.scale.setScalar(0.44 + Math.sin(c.t * 17) * 0.05);
        } else {
          c.halo.position.y += 0.04;
          c.halo.material.opacity = 0.24 + Math.sin(c.t * 7.0) * 0.08;
        }
      }
      if (c.phase === 'fly') {
        // vuelo parabólico con volteretas (ápice ya limitado al lanzar)
        c.vel.y -= DINAMITA.g * dt;
        c.pos.addScaledVector(c.vel, dt);
        c.mesh.position.copy(c.pos);
        c.mesh.rotation.x -= dt * c.spinA;
        c.mesh.rotation.z += dt * c.spinB;
        c.mesh.scale.setScalar(c.s0 * Math.min(1, 0.7 + c.t * 1.4));
        // INTERCEPTACIÓN CON LA PALA (barrido prev→pos del mando activo)
        const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
        if (ps && ps.active && this._paddleHit(ps, c)) { this._batear(ps, c); continue; }
        // ¿tocó la mesa? — la BASE del cartucho (pivote) roza el tapete
        const dentroX = Math.abs(c.pos.x) <= D.tableHalfWidth + 0.03;
        const dentroZ = c.pos.z >= D.tableCenterZ - D.tableHalfLength - 0.03 &&
                        c.pos.z <= D.tableCenterZ + D.tableHalfLength + 0.03;
        if (dentroX && dentroZ && c.pos.y <= D.tableTopY + 0.024 &&
            c.vel.y < 0) {
          this._aterrizar(c);
          continue;
        }
        if (c.pos.y < 0.02) this._boom(c, false);   // cayó fuera: estalla abajo
      } else if (c.phase === 'bateada') {
        c.vel.y -= DINAMITA.g * dt;
        c.pos.addScaledVector(c.vel, dt);
        c.mesh.position.copy(c.pos);
        c.mesh.rotation.x -= dt * 16;
        c.mesh.rotation.z += dt * 11;
        if (c.t >= DINAMITA.bateoT) this._boom(c, false);
      } else if (c.phase === 'fused') {
        // v2.106 · QUIETA del todo: la mecha arde 2 s y el cartucho NO se
        // mueve (fuera el volteo con bote, el balanceo y el giro plano).
        // Sólo vive su BRASA (el halo, en el bloque común del HALO).
        c.fuseT -= dt;
        if (c.fuseT <= 0) this._boom(c, true);
      }
    }
    // ONDAS EXPANSIVAS: la bola que pase cerca sale despedida (una vez)
    if (this.blasts.length) {
      const b = g.ball;
      const enRally = g.rules.state === 'rally';
      for (const bl of this.blasts) {
        if (bl.t <= 0) continue;
        bl.t -= dt;
        if (bl.hit || !enRally || !b || !b.vel) continue;
        if (b.pos.distanceTo(bl.pos) < bl.r) {
          bl.hit = true;
          this._desviarBola(b);
        }
      }
      this.blasts = this.blasts.filter((bl) => bl.t > 0 && !bl.hit);
    }
    // fin de la salva: todo lanzado, todo estallado, ondas apagadas + margen
    if (this._launched >= this._n && vivos === 0 && !this.blasts.length) {
      this._finT += dt;
      if (this._finT >= 0.35) this.done = true;
    }
  }
  dispose() {
    const g = this.game;
    for (const c of this.carts) {
      if (c.mesh) {
        g.rig.remove(c.mesh);
        if (!this.ctrl._tntModel) this._disposeTree(c.mesh);
        c.mesh = null;
      }
      if (c.halo) { g.rig.remove(c.halo); c.halo.material.dispose(); c.halo = null; }
    }
    this.carts = [];
    this.blasts = [];
    this.done = true;
  }
  _disposeTree(o) {
    o.traverse((n) => {
      if (n.geometry) n.geometry.dispose();
      if (n.material) {
        const mats = Array.isArray(n.material) ? n.material : [n.material];
        for (const mm of mats) { if (mm.map) mm.map.dispose(); mm.dispose(); }
      }
    });
  }
}

/* ============================================================================
 *  v2.120 · TERCER Y CUARTO SUPERPODER DEL FORAJIDO
 *  -------------------------------------------------------------------------
 *  3) TORMENTA DE ARENA — una nube de polvo CÁLIDA se asienta sobre TU campo
 *     (~8 s): velos girando que estorban la vista y 3 rodantes que botan por
 *     la mesa. Visual (no toca la física): molesta como el confeti del CLOWN
 *     pero en TU cara y con arte del Oeste. Icono: powerarena.png.
 *  4) ESTAMPIDA — una manada de bisontes cruza el pueblo DETRÁS de la mesa
 *     (~6,5 s): siluetas al galope, polvo a lo ancho, retumbe del suelo y
 *     vibración. Puro espectáculo que despista. Icono: powerestampida.png.
 *  Ambos siguen el motor de DOS FASES (firePower → _launchPending) y la
 *  regla Quest: se construyen UNA vez y se reusan toda la sesión.
 *  ========================================================================== */
const TORMENTA = {
  dur: 8.0,           // s de tormenta
  n: 16,              // velos de polvo
  x: 1.20,            // semianchura sobre TU campo
  // v2.125 FIX: la franja z ANTERIOR (-0.15..+1.30) quedaba DETRÁS del jugador
  // (z+ es la espalda; el campo propio es z negativo, convención confeti/mareo
  // de locura: z -1,50..+0,05). Ahora la nube se asienta DELANTE, en TU cara.
  z0: -1.50, z1: 0.05,// franja z (TU lado de la red, como el confeti del CLOWN)
  y0: 0.50, y1: 1.85, // alturas de los velos
  rodantes: 3,        // rodantes que cruzan la mesa
  op: 0.62,           // opacidad base de cada velo
  rodZ: -1.05,        // v2.125: z base de los rodantes (sobre TU media mesa;
                      // antes 0.55 = detrás del jugador)
};
const ESTAMPIDA = {
  dur: 6.5,           // s de manada
  n: 6,               // bisontes
  z: -3.05,           // calle DETRÁS de la mesa (lado forajido)
  xIn: 4.0, xOut: -4.0,
  h: 1.18,            // altura del bisonte (m)
};

/** Textura de VOLO DE POLVO (cálida y Densa) — canvas UNA vez por sesión.
 *  Doble capa: nube ancha + corazón denso para que la tormenta se VEA. */
function _oeTexPolvo() {
  const cv = oesteCanvas(128, 128);
  const c = cv.getContext('2d');
  const g = c.createRadialGradient(64, 64, 6, 64, 64, 62);
  g.addColorStop(0, 'rgba(214,176,116,0.95)');
  g.addColorStop(0.45, 'rgba(196,156,100,0.62)');
  g.addColorStop(0.8, 'rgba(168,130,80,0.28)');
  g.addColorStop(1, 'rgba(150,114,70,0)');
  c.fillStyle = g; c.fillRect(0, 0, 128, 128);
  const g2 = c.createRadialGradient(64, 64, 2, 64, 64, 34);
  g2.addColorStop(0, 'rgba(228,196,140,0.9)');
  g2.addColorStop(1, 'rgba(228,196,140,0)');
  c.fillStyle = g2; c.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(cv);
  t.colorSpace = THREE.SRGBColorSpace;
  return t;
}

class TormentaAction {
  constructor(ctrl) {
    this.ctrl = ctrl; this.game = ctrl.game;
    this.done = false; this.t = 0;
  }
  start() {
    const g = this.game;
    if (!this.ctrl._tormentaGrp) this._build();
    this.ctrl._tormentaGrp.visible = true;
    this.t = 0; this.done = false;
    this._windT = 0.4;
    // re-nacer los velos repartidos
    for (const p of this.ctrl._tormentaPuffs) this._respawnPuff(p, true);
    // rodantes: cruzan desde -x o +x al azar
    for (const r of this.ctrl._tormentaRod) {
      r.x = (Math.random() < 0.5 ? -1 : 1) * (2.6 + Math.random() * 1.2);
      r.vx = (r.x > 0 ? -1 : 1) * (1.5 + Math.random() * 0.9);
      r.y = 0.14; r.vy = 1.4 + Math.random() * 0.8;
      r.spin = 0;
      r.s.visible = true;
    }
  }
  _build() {
    const g = this.game;
    const grp = new THREE.Group();
    const tex = _oeTexPolvo();   // reserva pintada (por si el arte tarda)
    // v2.120: arte REAL del polvo (polvo.png) en cuanto cargue
    try {
      new THREE.TextureLoader().load(this.ctrl._A('polvo.png'), (t) => {
        try {
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = this.ctrl._aniso || 4;
          for (const p of puffs) { p.s.material.map = t; p.s.material.needsUpdate = true; }
        } catch (e) { /* reserva */ }
      }, undefined, () => { /* reserva */ });
    } catch (e) { /* reserva */ }
    const puffs = [];
    for (let i = 0; i < TORMENTA.n; i++) {
      const m = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex, transparent: true, depthWrite: false, opacity: 0,
        color: 0xffffff,
      }));
      m.renderOrder = 30;
      grp.add(m);
      puffs.push({ s: m, a: 0, va: 0, rx: 0, ry: 0, cx: 0, cy: 0, cz: 0, r0: 0.5 });
    }
    const rod = [];
    for (let i = 0; i < TORMENTA.rodantes; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: null, transparent: true, depthWrite: false, opacity: 0.96,
        color: 0xffffff,
      }));
      // reserva: bola de ramas pintada (si el arte no llega, sigue habiendo rodante)
      const cv = oesteCanvas(128, 128);
      const c = cv.getContext('2d');
      c.strokeStyle = '#7a5c34'; c.lineWidth = 3;
      for (let k = 0; k < 26; k++) {
        const a = Math.random() * Math.PI * 2, rr = 12 + Math.random() * 46;
        c.beginPath();
        c.moveTo(64 + Math.cos(a) * rr, 64 + Math.sin(a) * rr);
        c.quadraticCurveTo(64, 64,
          64 + Math.cos(a + 1.2 + Math.random()) * rr * (0.4 + Math.random() * 0.6),
          64 + Math.sin(a + 1.2) * rr * (0.4 + Math.random() * 0.6));
        c.stroke();
      }
      const t0 = new THREE.CanvasTexture(cv);
      t0.colorSpace = THREE.SRGBColorSpace;
      s.material.map = t0;
      s.material.needsUpdate = true;
      try {
        new THREE.TextureLoader().load(this.ctrl._A('rodante.png'), (t) => {
          try {
            t.colorSpace = THREE.SRGBColorSpace;
            t.anisotropy = this.ctrl._aniso || 4;
            s.material.map = t; s.material.needsUpdate = true;
          } catch (e) { /* reserva */ }
        }, undefined, () => { /* reserva */ });
      } catch (e) { /* reserva */ }
      s.scale.set(0.30, 0.30, 1);
      s.renderOrder = 31;
      grp.add(s);
      rod.push({ s, x: 0, y: 0.14, vx: 1.6, vy: 1.6, spin: 0 });
    }
    grp.visible = false;
    g.rig.add(grp);
    this.ctrl._tormentaGrp = grp;
    this.ctrl._tormentaPuffs = puffs;
    this.ctrl._tormentaRod = rod;
  }
  _respawnPuff(p, seed) {
    const T = TORMENTA;
    p.cx = (Math.random() * 2 - 1) * T.x;
    p.cz = T.z0 + Math.random() * (T.z1 - T.z0);
    p.cy = T.y0 + Math.random() * (T.y1 - T.y0);
    p.rx = 0.60 + Math.random() * 1.00;
    p.ry = p.rx * (0.30 + Math.random() * 0.25);
    p.a = seed ? Math.random() * Math.PI * 2 : 0;
    p.va = (0.35 + Math.random() * 0.55) * (Math.random() < 0.5 ? 1 : -1);
    p.r0 = 0.70 + Math.random() * 0.85;
  }
  update(dt) {
    const g = this.game;
    this.t += dt;
    const T = TORMENTA;
    // envolvente: entra 0,9 s · sale 1,2 s
    const kIn = Math.min(1, this.t / 0.9);
    const kOut = Math.min(1, Math.max(0, (T.dur - this.t) / 1.2));
    const k = kIn * kOut;
    for (const p of this.ctrl._tormentaPuffs) {
      p.a += dt * p.va;
      const wob = Math.sin(this.t * 1.7 + p.a * 3.0) * 0.14;
      p.s.position.set(
        p.cx + Math.cos(p.a) * p.rx,
        Math.max(0.35, p.cy + wob + Math.sin(p.a * 0.7) * p.ry),
        p.cz + Math.sin(p.a) * p.ry * 0.6,
      );
      const sc = p.r0 * (0.85 + 0.3 * Math.sin(p.a * 1.3));
      p.s.scale.set(sc, sc, 1);
      p.s.material.opacity = TORMENTA.op * k;
    }
    // rodantes: bote + rodadura + cruce; al salir, vuelven a entrar
    for (const r of this.ctrl._tormentaRod) {
      r.x += r.vx * dt;
      r.vy -= 9.81 * dt * 0.55;
      r.y += r.vy * dt;
      if (r.y < 0.14) { r.y = 0.14; r.vy = 1.9 + Math.random() * 0.9; }
      r.spin -= dt * (r.vx / 0.30);
      if (r.spin > Math.PI * 2) r.spin -= Math.PI * 2;
      if (r.spin < -Math.PI * 2) r.spin += Math.PI * 2;
      r.s.position.set(r.x, r.y + 0.05, TORMENTA.rodZ + (r.x * 0.05));
      r.s.material.rotation = r.spin;
      if (r.x < -3.2 || r.x > 3.2) {
        r.x = (r.vx > 0 ? -3.1 : 3.1);
        r.vx = (r.vx > 0 ? 1 : -1) * (1.5 + Math.random() * 0.9);
        r.vy = 1.4 + Math.random() * 0.8;
      }
    }
    // viento cadenciado (nunca rompe el frame)
    this._windT -= dt;
    if (this._windT <= 0) {
      this._windT = 0.9 + Math.random() * 0.6;
      try { g.audio.playNoise(0.75, 520, 0.5, 0.055, 0); } catch (e) { /* */ }
    }
    if (this.t >= T.dur) { this._hide(); this.done = true; }
  }
  _hide() {
    if (!this.ctrl._tormentaGrp) return;
    this.ctrl._tormentaGrp.visible = false;
    for (const p of this.ctrl._tormentaPuffs) p.s.material.opacity = 0;
  }
  dispose() { this._hide(); this.done = true; }
}

class EstampidaAction {
  constructor(ctrl) {
    this.ctrl = ctrl; this.game = ctrl.game;
    this.done = false; this.t = 0;
  }
  start() {
    const g = this.game;
    if (!this.ctrl._stampGrp) this._build();
    this.ctrl._stampGrp.visible = true;
    this.t = 0; this.done = false;
    this._rumbleT = 0.05; this._hapT = 0.05;
    // manada escalonada (2 filas) cruzando de derecha a IZQUIERDA (el arte
    // del bisonte mira a la izquierda: nada de espejos)
    for (let i = 0; i < this.ctrl._stampBis.length; i++) {
      const b = this.ctrl._stampBis[i];
      b.x = ESTAMPIDA.xIn - i * (1.15 + Math.random() * 0.5);
      b.vx = -(2.7 + Math.random() * 0.8);
      b.row = i % 2;
      b.phase = Math.random() * Math.PI * 2;
      b.s.visible = true;
    }
  }
  _build() {
    const g = this.game;
    const grp = new THREE.Group();
    const bis = [];
    const mkReserva = () => {
      const cv = oesteCanvas(256, 192);
      const c = cv.getContext('2d');
      c.fillStyle = '#241a10';
      c.beginPath();
      c.moveTo(30, 150); c.lineTo(30, 92); c.lineTo(70, 58); c.lineTo(150, 50);
      c.lineTo(206, 74); c.lineTo(226, 96); c.lineTo(196, 108);
      c.lineTo(196, 150); c.lineTo(160, 150); c.lineTo(160, 116);
      c.lineTo(120, 116); c.lineTo(120, 150); c.closePath(); c.fill();
      const t = new THREE.CanvasTexture(cv);
      t.colorSpace = THREE.SRGBColorSpace;
      return t;
    };
    const texRes = mkReserva();
    for (let i = 0; i < ESTAMPIDA.n; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: texRes, transparent: true, depthWrite: false, opacity: 1,
        color: 0xffffff, fog: false,
      }));
      s.material.map = texRes;
      s.renderOrder = 22;
      s.visible = false;
      grp.add(s);
      bis.push({ s, x: 0, vx: -3, row: 0, phase: 0 });
    }
    // arte del artista (bisonte.png) en cuanto cargue — para TODOS
    try {
      new THREE.TextureLoader().load(this.ctrl._A('bisonte.png'), (t) => {
        try {
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = this.ctrl._aniso || 4;
          for (const b of bis) { b.s.material.map = t; b.s.material.needsUpdate = true; }
        } catch (e) { /* reserva */ }
      }, undefined, () => { /* reserva */ });
    } catch (e) { /* reserva */ }
    // polvo propio (10 bocanadas a la altura de las patas) — polvo.png con
    // reserva pintada
    const tex = _oeTexPolvo();
    try {
      new THREE.TextureLoader().load(this.ctrl._A('polvo.png'), (t) => {
        try {
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = this.ctrl._aniso || 4;
          for (const p of polvo) { p.s.material.map = t; p.s.material.needsUpdate = true; }
        } catch (e) { /* reserva */ }
      }, undefined, () => { /* reserva */ });
    } catch (e) { /* reserva */ }
    const polvo = [];
    for (let i = 0; i < 10; i++) {
      const m = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex, transparent: true, depthWrite: false, opacity: 0,
      }));
      m.renderOrder = 23;
      grp.add(m);
      polvo.push({ s: m, life: 0, t: 0, x: 0, z: 0, r0: 0.6 });
    }
    grp.visible = false;
    g.rig.add(grp);
    this.ctrl._stampGrp = grp;
    this.ctrl._stampBis = bis;
    this.ctrl._stampPolvo = polvo;
  }
  update(dt) {
    const g = this.game;
    this.t += dt;
    const E = ESTAMPIDA;
    const kOut = Math.min(1, Math.max(0, (E.dur + 0.6 - this.t) / 1.0));
    for (const b of this.ctrl._stampBis) {
      b.x += b.vx * dt;
      const bob = Math.abs(Math.sin(this.t * 7.5 + b.phase)) * 0.075;
      const y = 0.02 + bob + b.row * 0.10;
      const h = E.h * (1 - b.row * 0.10);
      b.s.position.set(b.x, y + h * 0.5, E.z - b.row * 0.42);
      b.s.scale.set(h * 1.2, h, 1);
      b.s.material.opacity = kOut;
      // reciclaje: sale por la izquierda, vuelve a la derecha mientras dure
      if (b.x < E.xOut) {
        b.x = E.xIn - Math.random() * 0.8;
        b.vx = -(2.7 + Math.random() * 0.8);
      }
    }
    // polvo bajo las patas: la manada levanta la calle
    for (const p of this.ctrl._stampPolvo) {
      if (p.life > 0) {
        p.t += dt;
        const f = 1 - p.t / p.life;
        if (f <= 0) { p.life = 0; p.s.material.opacity = 0; continue; }
        p.s.position.y += dt * 0.42;
        const sc = p.r0 * (1 + p.t * 1.4);
        p.s.scale.set(sc, sc, 1);
        p.s.material.opacity = 0.62 * f * kOut;
      }
    }
    this._polvoT = (this._polvoT || 0) - dt;
    if (this._polvoT <= 0) {
      this._polvoT = 0.10;
      for (const p of this.ctrl._stampPolvo) {
        if (p.life > 0) continue;
        const b = this.ctrl._stampBis[(Math.random() * this.ctrl._stampBis.length) | 0];
        p.life = 0.9 + Math.random() * 0.5; p.t = 0;
        p.x = b.x + (Math.random() - 0.5) * 0.5;
        p.z = b.s.position.z + (Math.random() - 0.5) * 0.25;
        p.r0 = 0.5 + Math.random() * 0.5;
        p.s.position.set(p.x, 0.25, p.z);
        p.s.material.rotation = Math.random() * Math.PI;
        break;
      }
    }
    // retumbe + vibración (VR comfort: sin sacudida de cámara)
    this._rumbleT -= dt;
    if (this._rumbleT <= 0) {
      this._rumbleT = 0.55;
      try { g.audio.playNoise(0.5, 110, 0.8, 0.10, 0); } catch (e) { /* */ }
    }
    this._hapT -= dt;
    if (this._hapT <= 0 && g.renderer.xr.isPresenting) {
      this._hapT = 0.62;
      try { g.haptic(g.paddleHand, 0.32, 90); } catch (e) { /* */ }
    }
    if (this.t >= E.dur) { this._hide(); this.done = true; }
  }
  _hide() {
    if (!this.ctrl._stampGrp) return;
    this.ctrl._stampGrp.visible = false;
    for (const p of this.ctrl._stampPolvo) p.s.material.opacity = 0;
  }
  dispose() { this._hide(); this.done = true; }
}
/* ============================================================================
 *  v2.95 · ETAPA 2 — «ASEDIO AL ESCONDITE» 2.0 (bola-bomba + revólver · 3 min)
 *  ---------------------------------------------------------------------
 *  RECONSTRUCCIÓN COMPLETA (la barricada de barriles se jubila): la prueba
 *  transcurre en la AVENIDA del pueblo del lejano oeste — casas de madera
 *  con porches en fila (SALOON, BANCO, FUNERARIA, BARBERÍA y dos edificios
 *  de DOS PLANTAS), calle EMBARRADA bajo los pies y tablón-porción delante
 *  de las fachadas. Alrededor, el desierto del EXTREMO CALOR: cactus
 *  saguaro, el GRAN DEPÓSITO DE AGUA, montañas ROJIZAS de Arizona, BUITRES
 *  dando vueltas en el cielo salpicado de nubes y, a nuestra espalda, arena
 *  que se pierde en la lejanía con HUESOS de bisonte medio enterrados.
 *  La sala se ABRE igual que en el tren: fuera saloon y troqueles de sala.
 *
 *  MECÁNICA (v2.99 · 3 OLEADAS de 2 MINUTOS · 3 + 4 + 5 forajidos):
 *   · Delante del jugador, 3 EDIFICIOS INTERACTIVOS del artista: la
 *     FACHADA (Fachada1.png) delante, el INTERIOR (Interior1.png) detrás y
 *     el forajido ESCONDIDO ENTRE AMBAS. Al fondo, el PUEBLO LEJANO
 *     (pueblohorizonte.png) solo de ambientación.
 *   · Una BOLA-BOMBA cae CADA 1 SEGUNDO en la mesita: hay que golpearla
 *     (pala en cada mano) contra las fachadas.
 *   · CADA IMPACTO rompe la fachada: se estampa el ROTURA del artista como
 *     transparencia (¡BOQUETE!) y por él se ve el INTERIOR, soltando
 *     trocitos. La fachada AGUJEREA PROGRESIVAMENTE durante toda la
 *     oleada; una OLEADA NUEVA rehace las casas.
 *   · Una DIANA (delante de la fachada, siempre visible) marca el SITIO
 *     VERDE de zonas1.jpg donde se esconde un forajido. ACERTAR la bomba
 *     en la diana abre OTRO boquete y el FORAJIDO SALE DE PIE A LA CALLE:
 *     estático, mirándote, CORAZÓN en el pecho (su diana, nunca separado)
 *     y SU REVÓLVER apuntándote. AL 1 SEGUNDO DISPARA (sangre en la
 *     cara, manchones que se acumulan) salvo que le des al corazón.
 *   · Alarma a los 20 s del final de cada oleada. Sin acabar los forajidos
 *     de la oleada (o sin tiempo) → prueba perdida.
 *  Física: stepPhysics del NÚCLEO + colisionador propio de fachada vía
 *  _extra (patrón orbe de Magia, subpasos a 480 Hz anti-túnel). Sin luces
 *  dinámicas (lección v2.92): halos aditivos y cero asignaciones por frame.
 *  ============================================================================ */
class AsedioAction {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.phase = 'idle';        // intro|play|reveal|duck|win|fail
    this.t = 0;
    this.done = false;
    this.wave = 1;              // oleada 1..3
    this.kills = 0;             // forajidos abatidos en la etapa (0..12)
    this.killsWave = 0;         // abatidos en la oleada en curso
    this._zona = null;          // zona con la DIANA activa (v2.99)
    this._alarmOn = false;      // v2.99: alarma de 20 s ya sonada
    this.edif = [];             // v2.99: los 3 edificios interactivos
    this.zonas = [];            // v2.99: zonas verdes (u,v de zonas1.jpg)
    this._bannerN = 0;          // v2.99: cartel de oleada en pantalla
    this._bannerT = 0;
    this._bannerAfter = null;
    this._bannerTex = {};
    this._bannerAR = 1;
    this._outlawGun = null;     // v2.99: revólver del forajido apuntándote
    this._outCock = false;      // v2.99: ya apretó el gatillo (aviso)
    this._rotMask = null;       // v2.99: imagen del BOQUETE (rotura)
    this._rotChapas = null;     // v2.99: imagen de las CHAPAS del rotura
    this.revealT = 0;
    this.duckT = 0;
    this.duckKind = '';
    this.time = ASEDIO.waveTime;
    this._resultT = 0;
    this._hitCd = 0;            // antirrebote de golpes de fachada
    this._wallCd = 0;           // antirrebote del impacto de madera (sfx)
    this._mechaT = 0;           // cadencia del bufido de la mecha
    this._respawnT = 0;
    this._dead = false;
    this._deadT = 0;
    this._floorB = 0;
    this._msg = ''; this._msgT = 0;
    this._hud = null;
    this._ownTex = new Set();   // texturas PROPIAS (las de ctrl NO se tocan)
    this._debris = [];
    this._prev = null;
    this._tumbleW = new THREE.Vector3(); // v2.98: ω del giro natural
    this._dianaMoveT = 0;       // v2.101: cuenta atrás de la MUDANZA de la diana
    this._dentro = false;       // v2.101: la bola está DENTRO de una casa
    this._tnt = null;           // v2.101: cartucho escondido (mesh + sitio)
    this._tntSeq = null;        // v2.101: ráfaga pendiente de explosiones
    this._tntT = 0;             // v2.101: reloj de la ráfaga
    this.casasOleada = null;    // v2.103: reparto de casas [oleada][edificio]
    this._outFocus = null;      // v2.103: fundido imagen → NEGRO → apuntando
    this._balas = [];           // v2.103: balas trazadoras de SU disparo
    this._setos = [];           // v2.104: setos rodantes (pool)
    this._setoT = 1.6;          // v2.104: cuenta atrás del PRÓXIMO seto
    this._star = null;          // v2.105: estrella del sheriff (lazy)
    this._starT = 20.0;         // v2.105: cuenta atrás de la PRÓXIMA estrella
    this._starLife = 0;         // v2.105: vida restante de la estrella activa
    this._fadeT = 0;            // v2.106: reloj del fundido a negro
    this._fadeDuring = null;    // v2.106: callback DURANTE el negro (reset)
    this._fadeDone = true;      // v2.106: ¿ya corrió el callback del negro?
    this._derrota = null;       // v2.106: cinemática de derrota (risa→victoria)
    this._extra = (ball) => this._collide(ball);
  }
  _ct(cv) {
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(t);
    return t;
  }
  /* --- v2.97 · TEXTURA IA con RESPALDO procedural ----------------------
   * Crea/reausa una textura cuyo mapa parte del arte procedural de siempre
   * y CAMBIA a la imagen IA en cuanto carga (onload). Si la imagen falla
   * (sin red, 404…), el desierto sigue igual de jugable con el respaldo.
   * rx/ry: repetición (mirror=true usa MirroredRepeatWrapping). */
  _aiTex(rel, fallback, rx, ry, mirror) {
    const t = fallback;
    try {
      const img = new Image();
      img.onload = () => {
        t.image = img;
        t.colorSpace = THREE.SRGBColorSpace;
        if (rx || ry) {
          t.wrapS = t.wrapT = mirror ? THREE.MirroredRepeatWrapping
            : THREE.RepeatWrapping;
          t.repeat.set(rx || 1, ry || 1);
        }
        t.needsUpdate = true;
      };
      img.onerror = () => { /* el respaldo procedural queda intacto */ };
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* respaldo */ }
    return t;
  }
  /* --- v2.99 · TEXTURA del artista (sin respaldo): nace de un color
   *  plano DEL MISMO TAMAÑO que la imagen final y CAMBIA a la imagen en
   *  cuanto carga (onload). El mismo tamaño importa: reservar 4x4 y luego
   *  subir 1024² desborda la textura GL ya creada (glTexSubImage2D) y el
   *  cambio no se ve. fbCol=null -> lienzo TRANSPARENTE (invisible hasta
   *  que llegue el arte). */
  _aiTexCut(rel, fbCol, w, h) {
    const cv = oesteCanvas(w || 1024, h || 1024);
    const c0 = cv.getContext('2d');
    if (fbCol) {
      c0.fillStyle = fbCol;
      c0.fillRect(0, 0, cv.width, cv.height);
    } else {
      c0.clearRect(0, 0, cv.width, cv.height);
    }
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(t);
    try {
      const img = new Image();
      img.onload = () => { t.image = img; t.needsUpdate = true; };
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* se queda el color plano */ }
    return t;
  }
  /* --- v2.99 · IMAGEN suelta (para estampar el rotura en los lienzos) --- */
  _loadImg(rel, cb) {
    try {
      const img = new Image();
      img.onload = () => cb(img);
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* sin imagen: sin boquetes */ }
  }
  /* --- v2.99 · RECORTE FIJO (antes sprite): se orienta UNA VEZ hacia el
   *  punto de partida del jugador y queda COMPLETAMENTE quieto — el
   *  decorado YA NO "baila" al girar la cabeza (cactus, rocas, huesos,
   *  torre de agua…). Base a ras de suelo, ancho por aspecto. */
  _aiCut(rel, fallbackTex, x, z, h, onReady) {
    const mat = new THREE.MeshBasicMaterial({
      alphaTest: 0.35, fog: false, side: THREE.DoubleSide });
    if (fallbackTex) { mat.map = fallbackTex; }
    const m = new THREE.Mesh(new THREE.PlaneGeometry(h, h), mat);
    m.position.set(x, h / 2, z);
    m.rotation.y = Math.atan2(-x, -z);   // encarado al jugador SOLO al nacer
    m.visible = !!fallbackTex;
    this.group.add(m);
    try {
      const img = new Image();
      img.onload = () => {
        const t = new THREE.Texture(img);
        t.colorSpace = THREE.SRGBColorSpace;
        t.needsUpdate = true;
        this._ownTex.add(t);
        mat.map = t;
        mat.needsUpdate = true;
        m.scale.set(img.width / img.height, 1, 1);
        m.visible = true;
        if (onReady) onReady(m, img);
      };
      img.onerror = () => {
        if (!fallbackTex) { this.group.remove(m); }
      };
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* respaldo */ }
    return m;
  }
  /* ========================================================================
   *  v2.99 · EDIFICIO INTERACTIVO (Fachada1 + Interior1 + rotura)
   *  ------------------------------------------------------------------------
   *  · INTERIOR: plano FIJO detrás (mismo recorte que la fachada).
   *  · FACHADA: plano delante con alphaMap = lienzo BLANCO que los
   *    impactos AGUJEREAN estampando rotura_mascara (negro = transparencia):
   *    la explosión "abre" el boquete y por él se ve el INTERIOR.
   *  · DECAL: lienzo con las CHAPAS (trozos de pared del rotura) alrededor
   *    de cada boquete. El forajido ESCONDIDO vive ENTRE ambas imágenes. */
  _buildEdificio(bx) {
    const E = ASEDIO.edif;
    const zF = ASEDIO.facadeZ;
    /* v2.104 · MÁSCARA del INTERIOR (fachada TRASERA): lienzo blanco que
     *  los impactos sobre zona YA destruida AGUJEREAN igual que la
     *  fachada delantera — queda un HUECO REAL de lado a lado (por él se
     *  ve el desierto/horizonte detrás de la casa). */
    const icv = oesteCanvas(512, 512);
    const icc = icv.getContext('2d');
    icc.fillStyle = '#ffffff';
    icc.fillRect(0, 0, 512, 512);
    const intMaskTex = new THREE.CanvasTexture(icv);
    intMaskTex.colorSpace = THREE.NoColorSpace;
    this._ownTex.add(intMaskTex);
    const interior = new THREE.Mesh(
      new THREE.PlaneGeometry(E.w, E.h),
      new THREE.MeshBasicMaterial({ map: this.texInterior,
        transparent: true, alphaMap: intMaskTex, alphaTest: 0.35,
        fog: false }));
    interior.position.set(bx, E.y + E.h / 2, zF + ASEDIO.interiorDZ);
    this.group.add(interior);
    const cv = oesteCanvas(512, 512);
    const cc = cv.getContext('2d');
    cc.fillStyle = '#ffffff';
    cc.fillRect(0, 0, 512, 512);
    const maskTex = new THREE.CanvasTexture(cv);
    maskTex.colorSpace = THREE.NoColorSpace;
    this._ownTex.add(maskTex);
    const fac = new THREE.Mesh(
      new THREE.PlaneGeometry(E.w, E.h),
      new THREE.MeshBasicMaterial({ map: this.texFachada,
        transparent: true, alphaMap: maskTex, fog: false }));
    fac.position.set(bx, E.y + E.h / 2, zF);
    this.group.add(fac);
    const dcv = oesteCanvas(512, 512);
    const dcc = dcv.getContext('2d');
    dcc.clearRect(0, 0, 512, 512);
    const decTex = new THREE.CanvasTexture(dcv);
    decTex.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(decTex);
    const dec = new THREE.Mesh(
      new THREE.PlaneGeometry(E.w, E.h),
      new THREE.MeshBasicMaterial({ map: decTex, transparent: true,
        depthWrite: false, fog: false }));
    dec.position.set(bx, E.y + E.h / 2, zF + 0.008);
    dec.renderOrder = 3;
    this.group.add(dec);
    const b = { x: bx, fac, interior, maskCv: cv, maskC: cc, maskTex,
      decCv: dcv, decC: dcc, decTex, dec, holes: [], casa: 0,
      intMaskCv: icv, intMaskC: icc, intMaskTex, iholes: [] };
    this.edif.push(b);
    return b;
  }
  /** Zonas verdes de UN edificio: posiciones de pie sobre las líneas. */
  _buildZonas(b) {
    const E = ASEDIO.edif;
    const list = [];
    // v2.103: las líneas verdes de SU casa (zonasN.jpg), no siempre las de
    // la casa 1 — cada edificio sabe a qué CASA pertenece esta oleada
    const filas = (ASEDIO.casas[b.casa || 0] &&
      ASEDIO.casas[b.casa || 0].zonas) || AS_ZONAS_UV;
    for (const bar of filas) {
      const feetY = bar.v * E.h + E.y;
      for (let k = 0; k < bar.n; k++) {
        const t = (k + 0.5) / bar.n;
        const jit = (Math.random() - 0.5) * (bar.u1 - bar.u0) / bar.n;
        const u = bar.u0 + (bar.u1 - bar.u0) * clamp(t + jit, 0.05, 0.95);
        // v2.100: my = altura de la MIRILLA — EN la línea verde; mínimo
        // 0.37 m para que la placa nunca se meta bajo la calle
        const my = Math.max(feetY, 0.37);
        list.push({ b, x: b.x + (u - 0.5) * E.w, feetY, my });
      }
    }
    return list;
  }
  /** v2.99 · ¿puede esconderse ahí? NO si su fachada está AGUJEREADA. */
  _zonaLibre(z) {
    for (const h of z.b.holes) {
      if (Math.abs(h.x - z.x) < 0.80 &&
          h.y > z.feetY - 0.35 && h.y < z.feetY + 2.20) return false;
    }
    return true;
  }
  /** ¿en qué EDIFICIO cae la x? (null = entre casas o fuera) */
  _edificioEn(x) {
    for (const b of this.edif) {
      if (Math.abs(x - b.x) <= ASEDIO.edif.w / 2) return b;
    }
    return null;
  }
  /** v2.99 · BOQUETE (rotura del artista): estampa la MÁSCARA del rotura
   *  en el alphaMap de la fachada (negro = transparencia: se ve el
   *  interior) y las CHAPAS alrededor en el decal. */
  _perfora(b, ix, iy) {
    const E = ASEDIO.edif;
    const u = (ix - (b.x - E.w / 2)) / E.w;
    const v = clamp((iy - E.y) / E.h, 0.03, 0.97);
    if (u < 0.03 || u > 0.97) return;
    const px = u * 512, py = (1 - v) * 512;
    const sp = (E.holeW / E.w) * 512, sc = (E.chapW / E.w) * 512;
    if (this._rotMask) {
      b.maskC.globalCompositeOperation = 'source-over';
      b.maskC.drawImage(this._rotMask, px - sp / 2, py - sp / 2, sp, sp);
      b.maskTex.needsUpdate = true;
    }
    if (this._rotChapas) {
      b.decC.clearRect(px - sc / 2 - 3, py - sc / 2 - 3, sc + 6, sc + 6);
      b.decC.drawImage(this._rotChapas, px - sc / 2, py - sc / 2, sc, sc);
      b.decTex.needsUpdate = true;
    }
    b.holes.push({ x: ix, y: iy });
    // v2.101: ¿el boquete DESTAPA el cartucho escondido? (brasa + siseo:
    // el jugador SABE que hay algo ahí y busca el tiro por el agujero)
    if (this._tnt && this._tnt.b === b && !this._tnt.revealed) {
      const TR = ASEDIO.tnt;
      if (Math.abs(ix - this._tnt.x) < TR.revealR && iy < 1.7) {
        this._tntReveal();
      }
    }
  }
  /** v2.104 · ¿el impacto cae sobre ZONA YA DESTRUIDA de la fachada?
   *  Miro el ALPHA real del boquete (píxel del alphaMap de la fachada) y,
   *  por si la máscara del rotura tardara en cargar, la distancia a los
   *  boquetes ya conocidos (0,23 m). */
  _zonaRota(b, ix, iy) {
    const E = ASEDIO.edif;
    const u = (ix - (b.x - E.w / 2)) / E.w;
    const v = clamp((iy - E.y) / E.h, 0.03, 0.97);
    if (u < 0.03 || u > 0.97) return false;
    try {
      const d = b.maskC.getImageData((u * 512) | 0, ((1 - v) * 512) | 0,
        1, 1).data;
      if (d[1] < 110) return true;   // verde del alphaMap OSCURO = agujero
    } catch (e) { /* lienzo intocado: sigo con los boquetes */ }
    const r2 = 0.23 * 0.23;
    for (const h of b.holes) {
      const dx = ix - h.x, dy = iy - h.y;
      if (dx * dx + dy * dy < r2) return true;
    }
    return false;
  }
  /** v2.104 · BOQUETE EN LA FACHADA TRASERA (el INTERIOR): la pelota-bomba
   *  que impacta sobre una zona YA destruida rompe la MISMA zona del fondo
   *  — queda un HUECO REAL a través de la vivienda (el horizonte asoma por
   *  él). Petición del artista para dar realismo a las ruinas. */
  _perforaFondo(b, ix, iy) {
    const E = ASEDIO.edif;
    const u = (ix - (b.x - E.w / 2)) / E.w;
    const v = clamp((iy - E.y) / E.h, 0.03, 0.97);
    if (u < 0.03 || u > 0.97) return;
    const px = u * 512, py = (1 - v) * 512;
    const sp = (E.holeW / E.w) * 512;
    if (this._rotMask) {
      b.intMaskC.globalCompositeOperation = 'source-over';
      b.intMaskC.drawImage(this._rotMask, px - sp / 2, py - sp / 2, sp, sp);
      b.intMaskTex.needsUpdate = true;
    }
    b.iholes.push({ x: ix, y: iy });
  }
  /** OLEADA NUEVA: fachadas REHECHAS (sin boquetes) y zonas de nuevo. */
  _resetEdificios() {
    this._visteCasas();   // v2.103: las 3 casas de ESTA oleada (distintas)
    for (const b of this.edif) {
      b.maskC.globalCompositeOperation = 'source-over';
      b.maskC.fillStyle = '#ffffff';
      b.maskC.fillRect(0, 0, 512, 512);
      b.maskTex.needsUpdate = true;
      b.decC.clearRect(0, 0, 512, 512);
      b.decTex.needsUpdate = true;
      b.holes.length = 0;
      // v2.104: la fachada TRASERA también se rehace (sin huecos)
      b.intMaskC.globalCompositeOperation = 'source-over';
      b.intMaskC.fillStyle = '#ffffff';
      b.intMaskC.fillRect(0, 0, 512, 512);
      b.intMaskTex.needsUpdate = true;
      b.iholes.length = 0;
    }
    this._zonasRebuild();
    // v2.101: cartucho de dinamita ESCONDIDO en otra casa, al azar
    this._tntPlace();
  }
  /* ========================================================================
   *  v2.103 · REPARTO DE CASAS DEL PUEBLO: cada PARTIDA baraja las casas;
   *  cada oleada juega con 3 DIFERENTES entre sí y, cuando el artista
   *  entregue las 9 (3 por oleada), las 3 oleadas no repetirán NINGUNA.
   *  Con menos casas el recambio reutiliza las menos recientes (con 4 es
   *  matemáticamente imposible no repetir en la 2ª y 3ª oleada). Con las
   *  9 del artista (v2.105) el barajado saca 3-3-3 SIN repeticiones.
   *  ======================================================================== */
  _asignaCasas() {
    const NC = ASEDIO.casas.length;
    const todos = [];
    for (let i = 0; i < NC; i++) todos.push(i);
    for (let i = todos.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const t = todos[i]; todos[i] = todos[j]; todos[j] = t;
    }
    const ondas = [];
    for (let w = 0; w < 3; w++) {
      const pick = todos.splice(0, 3);      // primeras 3 SIN usar
      while (pick.length < 3) {
        // recambio: cualquiera que NO esté ya en esta oleada
        const resto = [];
        for (let h = 0; h < NC; h++) {
          if (pick.indexOf(h) < 0) resto.push(h);
        }
        pick.push(resto[(Math.random() * resto.length) | 0]);
      }
      ondas.push(pick);
    }
    return ondas;
  }
  /** v2.103 · VESTIR los 3 edificios con las casas de la oleada vigente:
   *  cambia map de fachada e interior y re-etiqueta b.casa (las zonas
   *  verdes se reconstruyen con las de ESA casa). */
  _visteCasas() {
    if (!this.casasOleada) this.casasOleada = this._asignaCasas();
    const onda = this.casasOleada[
      Math.min(2, Math.max(0, this.wave - 1))] || [0, 0, 0];
    for (let k = 0; k < this.edif.length; k++) {
      const b = this.edif[k];
      const ci = Math.min(ASEDIO.casas.length - 1, onda[k] || 0);
      b.casa = ci;
      if (b.fac && this.texFacCasa && this.texFacCasa[ci]) {
        b.fac.material.map = this.texFacCasa[ci];
        b.fac.material.needsUpdate = true;
      }
      if (b.interior && this.texIntCasa && this.texIntCasa[ci]) {
        b.interior.material.map = this.texIntCasa[ci];
        b.interior.material.needsUpdate = true;
      }
    }
  }
  /* ========================================================================
   *  v2.101 · EL CARTUCHO DE DINAMITA ESCONDIDO (small_tnt.glb, el MISMO
   *  cartucho de la etapa 1). Cada oleada se guarda DETRÁS de una casa al
   *  azar, de pie en el suelo ENTRE la fachada y el interior. Se VE por
   *  los boquetes (su brasa brilla); una bola que entre por un agujero y
   *  le dé REVIENTA MEDIA CASA: demolición grande + ráfaga de explosiones
   *  pequeñas próximas + estruendo + LOS DOS MANDOS TIEMBLAN.
   *  ======================================================================== */
  _tntPlace() {
    this._tntRemove();
    const g = this.game;
    const E = ASEDIO.edif;
    const T = ASEDIO.tnt;
    const b = this.edif[(Math.random() * this.edif.length) | 0];
    const x = b.x + (Math.random() - 0.5) * E.w * 0.56;
    const z = ASEDIO.facadeZ + T.zDZ;
    const mesh = this.ctrl._tntModel
      ? this.ctrl._tntModel.clone(true)
      : this._fallbackTntAs();
    // brillo propio cálido, el MISMO que los cartuchos de la etapa 1
    mesh.traverse((n) => {
      if (n.isMesh && n.material && n.material.emissive) {
        n.material.emissive.setHex(0x8a3410);
        n.material.emissiveIntensity = 0.55;
      }
    });
    mesh.position.set(x, 0.01, z);
    mesh.rotation.y = (Math.random() - 0.5) * 1.2;
    g.rig.add(mesh);
    let halo = null;
    try {
      halo = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texPuff, color: 0xff8a3c, transparent: true,
        opacity: 0.14, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      halo.scale.setScalar(0.30);
      halo.renderOrder = -1;   // ANTES de la fachada: sólo se ve POR el boquete
      halo.position.set(x, 0.13, z + 0.02);
      g.rig.add(halo);
    } catch (e) { halo = null; }
    // v2.102 · SEÑAL DE HUMO DEL ARTISTA: «la dinamita debe emitir alguna
    // señal para identificarla mejor» — FARO ROJO pulsante que asoma SOBRE
    // el tejado de la casa que la esconde (dorado = mirilla · ROJO = TNT)
    let beacon = null;
    try {
      beacon = new THREE.Mesh(new THREE.PlaneGeometry(0.30, 4.4),
        new THREE.MeshBasicMaterial({
          map: this._texFaroRojo(), color: 0xffffff, transparent: true,
          opacity: 0.72, blending: THREE.NormalBlending,
          depthWrite: false, side: THREE.DoubleSide, fog: false,
        }));
      beacon.position.set(x, 2.2, ASEDIO.facadeZ - 0.14);
      beacon.renderOrder = 2;
      g.rig.add(beacon);
    } catch (e) { beacon = null; }
    this._tntSisT = 2.2;       // v2.102: primer siseo pronto
    this._tnt = { mesh, halo, beacon, b, x, z, revealed: false,
      glb: !!this.ctrl._tntModel };
    this._tntSeq = null;
  }
  _tntRemove() {
    const t = this._tnt;
    if (!t) return;
    const g = this.game;
    if (t.mesh && t.mesh.parent) t.mesh.parent.remove(t.mesh);
    if (t.halo && t.halo.parent) t.halo.parent.remove(t.halo);
    if (t.beacon && t.beacon.parent) t.beacon.parent.remove(t.beacon);  // v2.102
    if (t.mesh && !t.glb) this._disposeTree(t.mesh);   // la reserva es PROPIA
    if (t.halo && t.halo.material) t.halo.material.dispose();
    this._tnt = null;
    // NOTA v2.101: NO se toca this._tntSeq — _tntBoom la llena ANTES de
    // retirar el mesh y la ráfaga debe sonar COMPLETA (el bug D15).
  }
  /** Reserva (mismo look que la etapa 1): cartucho de cajas rojo con mecha. */
  _fallbackTntAs() {
    const grp = new THREE.Group();
    const rojo = new THREE.MeshStandardMaterial({
      color: 0xb03018, roughness: 0.6, metalness: 0.05,
      emissive: 0x7a1e08, emissiveIntensity: 0.6,
    });
    const palo = new THREE.Mesh(
      new THREE.CylinderGeometry(0.035, 0.035, 0.15, 12), rojo);
    palo.rotation.z = Math.PI / 2;
    const cinta = new THREE.Mesh(
      new THREE.CylinderGeometry(0.037, 0.037, 0.03, 12),
      new THREE.MeshStandardMaterial({ color: 0xd9a441, roughness: 0.6,
        emissive: 0x6a4410, emissiveIntensity: 0.5 }));
    cinta.rotation.z = Math.PI / 2;
    const mecha = new THREE.Mesh(new THREE.CylinderGeometry(0.006, 0.006, 0.06, 6),
      new THREE.MeshStandardMaterial({ color: 0x2c2018, roughness: 0.9 }));
    mecha.position.set(0.06, 0.05, 0);
    mecha.rotation.z = -0.5;
    const brasa = new THREE.Mesh(new THREE.SphereGeometry(0.011, 8, 6),
      new THREE.MeshBasicMaterial({ color: 0xffb45f }));
    brasa.position.set(0.086, 0.072, 0);
    grp.add(palo, cinta, mecha, brasa);
    grp.scale.setScalar(DINAMITA.escala / 0.2);
    return grp;
  }
  /** v2.101 · UN BOQUETE HA DESTAPADO el cartucho: su brasa late más viva
   *  (se ve POR EL AGUJERO) y sisea — la pista para el jugador. */
  _tntReveal() {
    const t = this._tnt;
    if (!t || t.revealed) return;
    t.revealed = true;
    this.ctrl.sfx('mecha', 0);
    if (t.halo) t.halo.material.opacity = 0.26;
    if (t.beacon) t.beacon.material.opacity = 0.85;  // v2.102: faro más vivo
  }
  /** v2.101 · ¡LE HAN DADO AL CARTUCHO! MEDIA CASA POR LOS AIRES:
   *  demolición grande en la fachada + fogonazo + DOBLE estruendo +
   *  ráfaga de explosiones pequeñas próximas + LOS DOS MANDOS tiemblan. */
  _tntBoom() {
    const g = this.game;
    const t = this._tnt;
    if (!t) return;
    const T = ASEDIO.tnt;
    const bx = t.x;
    // 1) MEDIA CASA abajo: gran boquete + borde dentado + chapas + zonas
    //    de esa casa PROHIBIDAS (nadie se esconde en una ruina)
    this._demolicion(t.b, bx);
    // 2) fogonazo inicial y DOBLE ESTRUENDO (delante de la fachada: se ve)
    _AS_V1.set(bx, 0.55, ASEDIO.facadeZ + 0.15);
    this.ctrl.sfx('boom', 0);
    this.ctrl.sfx('boom', 0.13);
    this.ctrl.fx.flash(_AS_V1, 2.6, 0xffd28a);
    this.ctrl.fx.spark(_AS_V1, 24, 0xd9b06a, 4.2, 1.5);
    this.ctrl.fx.smoke(_AS_V1, 4, true);
    this._splinters(bx, 0.7);
    this._splinters(bx + 0.3, 1.4);
    this._polvoDentro(bx, 0.8, t.z + 0.05, 3);
    // 3) RÁFAGA: muchas explosiones PEQUEÑAS y PRÓXIMAS entre sí
    //    («realmente son como muchas explosiones pequeñas próximas»)
    this._tntT = 0;
    this._tntSeq = [];
    for (let i = 0; i < T.puffs; i++) {
      this._tntSeq.push({
        t: 0.10 + i * T.gap + Math.random() * 0.05,
        x: bx + (Math.random() - 0.5) * 1.6,
        y: 0.15 + Math.random() * 1.8,
        z: ASEDIO.facadeZ + 0.08 + Math.random() * 0.30,
      });
    }
    // 4) LOS DOS MANDOS TIEMBLAN (ráfaga larga; los pulsos por explosión
    //    los añade step() mientras la ráfaga avanza)
    if (g.renderer.xr.isPresenting) {
      g.haptic(0, 1.0, 520);
      g.haptic(1, 1.0, 520);
    }
    // 5) el cartucho YA NO ESTÁ: explotó
    this._tntRemove();
    // 6) la bola muere y, si la diana vivía en ESA casa, se muda
    this._killBall();
    if (this.dianaGrp.visible && this._zona &&
        !this._zonaLibre(this._zona)) {
      this._spawnTarget();
    }
    this._msg = tx('asedio_tnt');
    this._msgT = 3.0;
    g.rules.message = this._msg;
  }
  /** v2.101 · DEMOLICIÓN GRANDE (media casa): elipse negra en la MÁSCARA
   *  (transparencia) + rotura del artista en el borde (dentado) + chapas
   *  alrededor + agujeros registrados (zonas de esa casa PROHIBIDAS). */
  _demolicion(b, bx) {
    const E = ASEDIO.edif;
    const T = ASEDIO.tnt;
    const u = (bx - (b.x - E.w / 2)) / E.w;
    const px = clamp(u, 0.08, 0.92) * 512;
    const cyV = 0.245, ryV = 0.305;          // desde el suelo hasta ~v 0,55
    const cy = (1 - cyV) * 512;
    const rx = (T.halfW / E.w) * 512;
    const ry = ryV * 512;
    b.maskC.globalCompositeOperation = 'source-over';
    b.maskC.fillStyle = '#000000';
    b.maskC.beginPath();
    b.maskC.ellipse(px, cy, rx, ry, 0, 0, Math.PI * 2);
    b.maskC.fill();
    if (this._rotMask) {
      const sp = (E.holeW * 1.35 / E.w) * 512;
      for (let i = 0; i < 10; i++) {
        const a = (i / 10) * Math.PI * 2 + Math.random() * 0.5;
        const qx = px + Math.cos(a) * rx * 0.92;
        const qy = cy + Math.sin(a) * ry * 0.92;
        b.maskC.drawImage(this._rotMask, qx - sp / 2, qy - sp / 2, sp, sp);
      }
    }
    b.maskTex.needsUpdate = true;
    if (this._rotChapas) {
      const sc = (E.chapW / E.w) * 512;
      for (let i = 0; i < 8; i++) {
        const a = (i / 8) * Math.PI * 2 + Math.random() * 0.4;
        const qx = px + Math.cos(a) * rx * 1.04;
        const qy = cy + Math.sin(a) * ry * 1.04;
        b.decC.clearRect(qx - sc / 2 - 3, qy - sc / 2 - 3, sc + 6, sc + 6);
        b.decC.drawImage(this._rotChapas, qx - sc / 2, qy - sc / 2, sc, sc);
      }
      b.decTex.needsUpdate = true;
    }
    for (const [hx, hy] of [[bx - 0.45, 0.5], [bx + 0.45, 0.5],
        [bx - 0.45, 1.5], [bx + 0.45, 1.5], [bx, 1.0], [bx, 2.0]]) {
      b.holes.push({ x: hx, y: hy });
    }
  }
  /** v2.101 · POLVO DENTRO de la casa: sprites con renderOrder -1 (se
   *  dibujan ANTES que la fachada) — se ven SÓLO por los boquetes. */
  _polvoDentro(x, y, z, n) {
    if (!this._polvo) return;
    let placed = 0;
    for (const s of this._polvo) {
      if (s.life > 0) continue;
      s.life = 1.1 + Math.random() * 0.5;
      s.t = 0;
      s.s.position.set(x + (Math.random() - 0.5) * 0.4,
        Math.max(0.15, y + (Math.random() - 0.5) * 0.3), z);
      s.v.set((Math.random() - 0.5) * 0.2, 0.35 + Math.random() * 0.25,
        (Math.random() - 0.5) * 0.2);
      s.r0 = 0.12 + Math.random() * 0.08;
      s.s.material.opacity = 0;
      s.s.material.rotation = Math.random() * Math.PI;
      s.s.visible = true;
      if (++placed >= (n || 3)) break;
    }
  }
  /** v2.99 · Re-reparte las posiciones de pie sobre las líneas verdes. */
  _zonasRebuild() {
    this.zonas.length = 0;
    for (const b of this.edif) {
      const zs = this._buildZonas(b);
      for (const z of zs) this.zonas.push(z);
    }
  }
  /* --- v2.99 · CARTEL de OLEADA (oleada1/2/3.png): quad que cruza la
   *  calle — entra por la derecha con EFECTO DE VELOCIDAD, flota con un
   *  vaivén ligero y sale por la izquierda. Mientras cruza, PAUSA. */
  _buildBanner() {
    const B = ASEDIO.banner;
    this.bannerGrp = new THREE.Group();
    this.bannerGrp.position.set(B.xIn, B.y, B.z);
    this.bannerGrp.visible = false;
    this.bannerMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(1, 1),
      new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false,
        depthTest: false, fog: false }));
    // v2.106: 9995 — el cartel se dibuja SOBRE el fundido negro (9990):
    // durante la transición el cartel cruza la pantalla a oscuras.
    this.bannerMesh.renderOrder = 9995;
    this.bannerGrp.add(this.bannerMesh);
    this.group.add(this.bannerGrp);
  }
  /* --- v2.106 · FUNDIDO A NEGRO del escenario (transición de oleada y
   *  derrota): quad negro GRANDE pegado al jugador (delante de la cara,
   *  depthTest off) — el desvanecimiento a negro pedido por el artista:
   *  «desvanecimiento del escenario a negro, cartel de oleada y aparición
   *  de nuevo escenario». */
  _buildFade() {
    const g = this.game;
    this.fadeNegro = new THREE.Mesh(
      new THREE.PlaneGeometry(11, 7),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true,
        opacity: 0, depthWrite: false, depthTest: false, fog: false }));
    this.fadeNegro.position.set(0, 1.35, -0.72);
    this.fadeNegro.renderOrder = 9990;
    this.fadeNegro.visible = false;
    g.rig.add(this.fadeNegro);          // pegado AL JUGADOR (cubre la vista)
    // v2.106 · IMAGEN de la DERROTA (Forajido_lauging → Forajido_victory)
    this.derrotaImg = new THREE.Sprite(new THREE.SpriteMaterial({
      transparent: true, depthWrite: false, depthTest: false, fog: false,
    }));
    this.derrotaImg.center.set(0.5, 0.5);
    this.derrotaImg.position.set(0, 1.45, -1.65);
    this.derrotaImg.renderOrder = 9996;
    this.derrotaImg.visible = false;
    this.derrotaImg.scale.set(1.4, 2.6, 1);
    g.rig.add(this.derrotaImg);
    this._derrota = null;
  }
  /** v2.106 · Esconde el fundido y la cinemática de derrota (fin/vuelta). */
  _fadeHide() {
    if (this.fadeNegro) {
      this.fadeNegro.material.opacity = 0;
      this.fadeNegro.visible = false;
    }
    if (this.derrotaImg) this.derrotaImg.visible = false;
    this._derrota = null;
  }
  _bannerTexN(n) {
    if (this._bannerTex[n]) return this._bannerTex[n];
    const t = new THREE.Texture();
    t.colorSpace = THREE.SRGBColorSpace;
    this._ownTex.add(t);
    try {
      const img = new Image();
      img.onload = () => { t.image = img; t.needsUpdate = true; };
      img.src = new URL('./assets/decor/asedio/oleada' + n + '.webp',
        import.meta.url).href;
    } catch (e) { /* */ }
    this._bannerTex[n] = t;
    return t;
  }
  _showBanner(n, after, during) {
    const B = ASEDIO.banner;
    this._bannerN = n;
    this._bannerT = 0;
    this._bannerAfter = after || null;
    // v2.106 · TRANSICIÓN de OLEADA: fundido del escenario a negro (0,5 s)
    // → mientras negro, las casas se REHACEN (dur) → el cartel cruza la
    // pantalla a oscuras → el escenario NUEVO reaparece (0,6 s) → cartel
    // sigue hasta salir. En el arranque (oleada 1) sin fundido.
    this._fadeDuring = during || null;
    this._fadeDone = !during;
    this._fadeT = 0;
    if (during && this.fadeNegro) {
      this.fadeNegro.material.opacity = 0;
      this.fadeNegro.visible = true;
    }
    const tex = this._bannerTexN(n);
    this.bannerMesh.material.map = tex;
    this.bannerMesh.material.needsUpdate = true;
    this._bannerAR = tex.image ? tex.image.width / tex.image.height : 1;
    this.bannerMesh.scale.set(B.size * this._bannerAR, B.size, 1);
    this.bannerGrp.position.set(B.xIn, B.y, B.z);
    this.bannerGrp.visible = true;
    this.phase = 'banner';
    this._parkBall();
    this.ctrl._playWaveJingle(0.9);   // música del cartel (oleada.mp3)
  }

  /* ------------------------------ texturas -------------------------------- */
  _texSky() {
    const cv = oesteCanvas(1024, 256);
    const c = cv.getContext('2d');
    const gr = c.createLinearGradient(0, 0, 0, 256);
    gr.addColorStop(0, '#6fa5cf'); gr.addColorStop(0.5, '#a9c4cf');
    gr.addColorStop(0.78, '#e8d3a2'); gr.addColorStop(1, '#f0d8a4');
    c.fillStyle = gr; c.fillRect(0, 0, 1024, 256);
    // NUBES SALPICADAS: manchas suaves alargadas (cielo de extremo calor)
    const cloud = (x, y, w, a) => {
      const rg = c.createRadialGradient(x, y, 2, x, y, w / 2);
      rg.addColorStop(0, 'rgba(255,251,240,' + a + ')');
      rg.addColorStop(0.6, 'rgba(255,246,228,' + a * 0.55 + ')');
      rg.addColorStop(1, 'rgba(255,246,228,0)');
      c.fillStyle = rg;
      c.beginPath(); c.ellipse(x, y, w / 2, w / 6.5, 0, 0, Math.PI * 2); c.fill();
    };
    for (const [x, y, w, a] of [[60, 52, 170, 0.20], [230, 96, 130, 0.14],
      [340, 44, 200, 0.18], [520, 84, 150, 0.13], [640, 40, 120, 0.16],
      [780, 100, 190, 0.13], [900, 56, 150, 0.18], [130, 150, 190, 0.10],
      [600, 150, 170, 0.09], [850, 158, 140, 0.09]]) cloud(x, y, w, a);
    const t = this._ct(cv);
    t.wrapS = THREE.RepeatWrapping;
    t.repeat.set(2, 1);
    return t;
  }
  _texMontes() {
    const cv = oesteCanvas(1024, 256);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 1024, 256);
    // montañas ROJIZAS de Arizona (mesetas) — baja saturación por la lejanía
    const col = (a) => 'rgba(168,92,62,' + a + ')';
    const mesa = (x0, w, h, a) => {
      c.fillStyle = col(a);
      c.beginPath();
      c.moveTo(x0, 256); c.lineTo(x0 + w * 0.16, 256 - h);
      c.lineTo(x0 + w * 0.84, 256 - h); c.lineTo(x0 + w, 256);
      c.closePath(); c.fill();
      // banda superior más clara (luz del sol alto)
      c.fillStyle = 'rgba(205,130,90,' + a * 0.5 + ')';
      c.fillRect(x0 + w * 0.16, 256 - h, w * 0.68, 7);
    };
    mesa(20, 230, 150, 0.40); mesa(300, 170, 108, 0.34);
    mesa(520, 260, 168, 0.38); mesa(820, 180, 120, 0.32);
    c.fillStyle = col(0.22);
    for (let i = 0; i < 8; i++) {
      const x = i * 128 + 30, w = 80 + (i % 3) * 36;
      c.beginPath(); c.moveTo(x, 256); c.lineTo(x + w / 2, 206 - (i % 2) * 18);
      c.lineTo(x + w, 256); c.closePath(); c.fill();
    }
    const t = this._ct(cv);
    t.wrapS = THREE.RepeatWrapping;
    t.repeat.set(2, 1);
    return t;
  }
  _texPuebloLejos() {
    const cv = oesteCanvas(1024, 160);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 1024, 160);
    // siluetas de más pueblo y un molino, al fondo de la avenida
    const col = 'rgba(122,92,58,0.34)';
    for (let i = 0; i < 14; i++) {
      const x = i * 74 + (i % 3) * 9, w = 40 + (i % 4) * 12;
      const h = 42 + (i % 3) * 22;
      c.fillStyle = col;
      c.fillRect(x, 160 - h, w, h);
      c.beginPath();
      c.moveTo(x - 4, 160 - h); c.lineTo(x + w / 2, 160 - h - 14);
      c.lineTo(x + w + 4, 160 - h); c.closePath(); c.fill();
    }
    // molino de viento
    c.strokeStyle = col; c.lineWidth = 5;
    c.beginPath(); c.moveTo(940, 160); c.lineTo(940, 52); c.stroke();
    c.beginPath(); c.arc(940, 48, 18, 0, Math.PI * 2); c.stroke();
    const t = this._ct(cv);
    t.wrapS = THREE.RepeatWrapping;
    t.repeat.set(2, 1);
    return t;
  }
  _texArena() {
    const cv = oesteCanvas(512, 512);
    const c = cv.getContext('2d');
    c.fillStyle = '#d9ad76'; c.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 300; i++) {
      const a = 0.05 + Math.random() * 0.12;
      c.fillStyle = Math.random() < 0.5
        ? 'rgba(150,110,60,' + a + ')' : 'rgba(240,210,160,' + a + ')';
      c.beginPath();
      c.arc(Math.random() * 512, Math.random() * 512, 1.5 + Math.random() * 5,
        0, Math.PI * 2);
      c.fill();
    }
    // matas secas
    for (let i = 0; i < 24; i++) {
      c.fillStyle = 'rgba(150,140,80,0.20)';
      c.beginPath();
      c.ellipse(Math.random() * 512, Math.random() * 512,
        7 + Math.random() * 9, 3 + Math.random() * 4, 0, 0, Math.PI * 2);
      c.fill();
    }
    const t = this._ct(cv);
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(6, 6);
    return t;
  }
  _texBarro() {
    const cv = oesteCanvas(512, 512);
    const c = cv.getContext('2d');
    // AVENIDA EMBARRADA: marrón mojado con charcos que reflejan el cielo
    c.fillStyle = '#6b4d33'; c.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 200; i++) {
      const a = 0.05 + Math.random() * 0.14;
      c.fillStyle = Math.random() < 0.55
        ? 'rgba(46,30,16,' + a + ')' : 'rgba(140,105,66,' + a + ')';
      c.beginPath();
      c.arc(Math.random() * 512, Math.random() * 512, 2 + Math.random() * 7,
        0, Math.PI * 2);
      c.fill();
    }
    // rodadas de carreta (dos surcos oscuros)
    c.fillStyle = 'rgba(40,24,12,0.30)';
    c.fillRect(148, 0, 26, 512); c.fillRect(338, 0, 26, 512);
    // CHARCOS: elipses con borde claro
    for (const [x, y, w, h] of [[180, 120, 92, 30], [340, 300, 120, 38],
      [150, 420, 76, 24], [390, 80, 60, 18]]) {
      c.fillStyle = 'rgba(32,22,12,0.55)';
      c.beginPath(); c.ellipse(x, y, w, h, 0, 0, Math.PI * 2); c.fill();
      c.fillStyle = 'rgba(190,205,200,0.20)';
      c.beginPath(); c.ellipse(x - w * 0.12, y - h * 0.18, w * 0.62, h * 0.55,
        0, 0, Math.PI * 2); c.fill();
    }
    // v2.98: bordes FUNDIDOS y sin tesela (1×1): la avenida se queda
    // pegada a la arena sin borde duro de recorte
    this._edgeFade(cv, c, 0.14);
    const t = this._ct(cv);
    t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
    t.repeat.set(1, 1);
    return t;
  }
  _texTablones(base, dark) {
    const cv = oesteCanvas(128, 128);
    const c = cv.getContext('2d');
    c.fillStyle = base; c.fillRect(0, 0, 128, 128);
    c.strokeStyle = 'rgba(30,18,8,0.45)'; c.lineWidth = 2;
    for (let i = 0; i < 6; i++) {
      c.beginPath(); c.moveTo(0, 10 + i * 21);
      c.bezierCurveTo(40, 14 + i * 21, 88, 6 + i * 21, 128, 12 + i * 21);
      c.stroke();
    }
    if (dark) {
      c.fillStyle = 'rgba(0,0,0,0.18)';
      for (let i = 0; i < 20; i++) {
        c.fillRect(Math.random() * 128, Math.random() * 128, 8, 2);
      }
    }
    return this._ct(cv);
  }
  /* --- v2.98 · CÚPULA del cielo (equirect): degradado de CENIT azul a
   *  horizonte cálido con nubes bajas — cierra el cielo POR ENCIMA de la
   *  banda IA (antes el cilindro abierto dejaba ver el negro). */
  _texSkyDome() {
    const cv = oesteCanvas(1024, 512);
    const c = cv.getContext('2d');
    const gr = c.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, '#4f8fc4'); gr.addColorStop(0.45, '#8fb8d8');
    gr.addColorStop(0.75, '#cfd8cf'); gr.addColorStop(1, '#f0d8a4');
    c.fillStyle = gr; c.fillRect(0, 0, 1024, 512);
    for (let i = 0; i < 26; i++) {
      const x = Math.random() * 1024, y = 300 + Math.random() * 180;
      const w = 90 + Math.random() * 190;
      const rg = c.createRadialGradient(x, y, 2, x, y, w / 2);
      rg.addColorStop(0, 'rgba(255,251,240,0.16)');
      rg.addColorStop(1, 'rgba(255,246,228,0)');
      c.fillStyle = rg;
      c.beginPath(); c.ellipse(x, y, w / 2, w / 6.5, 0, 0, Math.PI * 2);
      c.fill();
    }
    return this._ct(cv);
  }
  /* --- v2.106 · NUBE suave para la deriva del horizonte (RGBA) ----------- */
  _texNube() {
    const cv = oesteCanvas(256, 128);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 256, 128);
    const puff = (x, y, r, a) => {
      const rg = c.createRadialGradient(x, y, r * 0.1, x, y, r);
      rg.addColorStop(0, 'rgba(255,251,242,' + a + ')');
      rg.addColorStop(0.55, 'rgba(255,247,232,' + a * 0.62 + ')');
      rg.addColorStop(1, 'rgba(255,247,232,0)');
      c.fillStyle = rg;
      c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    };
    puff(78, 74, 42, 0.85); puff(122, 60, 52, 0.95); puff(168, 74, 44, 0.85);
    puff(100, 84, 36, 0.80); puff(146, 86, 34, 0.75); puff(58, 86, 26, 0.55);
    puff(196, 88, 24, 0.50);
    return this._ct(cv);
  }
  /* --- v2.98 · BORDES FUNDIDOS: desvanece los 4 bordes de un canvas a
   *  alfa 0 (destination-out) para que los recortes IA no se vean como
   *  alfombras puestas encima del suelo. */
  _edgeFade(cv, c, frac) {
    const w = cv.width, h = cv.height, f = frac || 0.10;
    c.globalCompositeOperation = 'destination-out';
    const gs = [
      [0, 0, w * f, 0, 0, 0, w * f, h],
      [w, 0, w - w * f, 0, w - w * f, 0, w * f, h],
      [0, 0, 0, h * f, 0, 0, w, h * f],
      [0, h, 0, h - h * f, 0, h - h * f, w, h * f],
    ];
    for (const [x0, y0, x1, y1, rx, ry, rw, rh] of gs) {
      const g = c.createLinearGradient(x0, y0, x1, y1);
      g.addColorStop(0, 'rgba(0,0,0,1)'); g.addColorStop(1, 'rgba(0,0,0,0)');
      c.fillStyle = g; c.fillRect(rx, ry, rw, rh);
    }
    c.globalCompositeOperation = 'source-over';
  }
  /* --- v2.98 · TEXTURA IA con bordes fundidos (variante de _aiTex):
   *  la imagen IA se pinta en un lienzo y se le DESVANECEN los bordes.
   *  Pensada para la avenida de barro sobre la arena. */
  _aiTexFade(rel, fallback, rx, ry, mirror) {
    const t = fallback;
    try {
      const img = new Image();
      img.onload = () => {
        const cv = oesteCanvas(img.width, img.height);
        const c = cv.getContext('2d');
        c.drawImage(img, 0, 0);
        this._edgeFade(cv, c, 0.12);
        t.image = cv;
        t.colorSpace = THREE.SRGBColorSpace;
        if (rx || ry) {
          t.wrapS = t.wrapT = mirror ? THREE.MirroredRepeatWrapping
            : THREE.RepeatWrapping;
          t.repeat.set(rx || 1, ry || 1);
        }
        t.needsUpdate = true;
      };
      img.onerror = () => { /* el respaldo procedural queda (ya fundido) */ };
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* respaldo */ }
    return t;
  }
  /* --- v2.106 · TEXTURA IA con FUNDIDO de alfa ARRIBA y ABAJO (la cura
   *  de la costura del horizonte): montes.webp llega SIN alfa (RGB con su
   *  propio cielo) y su borde superior pintaba una LÍNEA dura entre cielo
   *  y montañas. Al cargar, la imagen se re-pinta en un lienzo y se
   *  multiplica su alfa con un degradado: 0 en el borde superior → 1 en
   *  topFrac, y 1 → 0 en la franja inferior (botFrac). Las cimas se
   *  disuelven en el cielo de la banda y la transición es continua. */
  _aiTexFadeTop(rel, fallback, rx, ry, mirror, topFrac, botFrac) {
    const t = fallback;
    try {
      const img = new Image();
      img.onload = () => {
        const cv = oesteCanvas(img.width, img.height);
        const c = cv.getContext('2d');
        c.drawImage(img, 0, 0);
        const w = cv.width, h = cv.height;
        const ft = Math.max(1, Math.round((topFrac || 0.42) * h));
        const fb = Math.max(0, Math.round((botFrac || 0.10) * h));
        const im = c.getImageData(0, 0, w, h);
        const d = im.data;
        for (let y = 0; y < h; y++) {
          let a = 1;
          if (y < ft) a = y / ft;                       // cima → disuelve
          if (fb > 0 && y >= h - fb) {
            const ab = (h - 1 - y) / fb;                // falda → funde al suelo
            if (ab < a) a = ab;
          }
          if (a >= 0.999) continue;
          const row = y * w * 4;
          for (let x = 0; x < w; x++) d[row + x * 4 + 3] *= a;
        }
        c.putImageData(im, 0, 0);
        t.image = cv;
        t.colorSpace = THREE.SRGBColorSpace;
        if (rx || ry) {
          t.wrapS = t.wrapT = mirror ? THREE.MirroredRepeatWrapping
            : THREE.RepeatWrapping;
          t.repeat.set(rx || 1, ry || 1);
        }
        t.needsUpdate = true;
      };
      img.onerror = () => { /* el respaldo procedural queda (ya con alfa) */ };
      img.src = new URL('./assets/decor/asedio/' + rel,
        import.meta.url).href;
    } catch (e) { /* respaldo */ }
    return t;
  }
  /* --- props del desierto ------------------------------------------------- */
  _texCactus(v) {
    const cv = oesteCanvas(256, 384);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 256, 384);
    c.fillStyle = '#7d8a52';
    c.fillRect(112, 84, 34, 280);
    c.fillRect(104, 78, 50, 16);
    if (v === 0) {
      c.fillRect(62, 150, 22, 74); c.fillRect(62, 150, 62, 20);
      c.fillRect(174, 116, 22, 96); c.fillRect(136, 116, 60, 20);
    } else {
      c.fillRect(72, 190, 22, 64); c.fillRect(72, 190, 54, 20);
    }
    c.fillStyle = 'rgba(52,62,30,0.55)';
    c.fillRect(112, 84, 8, 280); c.fillRect(104, 78, 8, 16);
    // espinas
    c.strokeStyle = 'rgba(230,230,190,0.35)'; c.lineWidth = 2;
    for (let i = 0; i < 16; i++) {
      const x = 112 + Math.random() * 34, y = 90 + Math.random() * 260;
      c.beginPath(); c.moveTo(x, y); c.lineTo(x + 5, y - 5); c.stroke();
    }
    return this._ct(cv);
  }
  _texBuitre() {
    const cv = oesteCanvas(128, 80);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 128, 80);
    c.strokeStyle = '#241d18'; c.lineWidth = 7; c.lineCap = 'round';
    c.beginPath();
    c.moveTo(10, 44); c.quadraticCurveTo(40, 14, 64, 40);
    c.quadraticCurveTo(88, 14, 118, 44);
    c.stroke();
    c.fillStyle = '#241d18';
    c.beginPath(); c.ellipse(64, 44, 9, 6, 0, 0, Math.PI * 2); c.fill();
    return this._ct(cv);
  }
  _texCostillas() {
    const cv = oesteCanvas(256, 192);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 256, 192);
    const bone = '#e6dcc4', shade = 'rgba(120,100,70,0.5)';
    // columna vertebral
    c.strokeStyle = bone; c.lineWidth = 10; c.lineCap = 'round';
    c.beginPath(); c.moveTo(30, 176); c.quadraticCurveTo(120, 8, 226, 150);
    c.stroke();
    // costillas curvadas hacia abajo
    c.lineWidth = 7;
    for (let i = 0; i < 5; i++) {
      const t = 0.18 + i * 0.16;
      const x = 30 + (226 - 30) * t;
      const y = 176 - (176 - 8) * Math.sin(Math.PI * t) * 0.9 - 8;
      c.beginPath(); c.moveTo(x, y);
      c.quadraticCurveTo(x + 8, y + 52, x - 14, y + 86);
      c.stroke();
    }
    c.fillStyle = shade;
    c.beginPath(); c.ellipse(128, 170, 84, 12, 0, 0, Math.PI * 2); c.fill();
    return this._ct(cv);
  }
  _texCraneo() {
    const cv = oesteCanvas(160, 112);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 160, 112);
    c.fillStyle = '#e6dcc4';
    c.beginPath(); c.ellipse(80, 66, 40, 28, 0, 0, Math.PI * 2); c.fill();
    // hocico
    c.beginPath(); c.ellipse(116, 74, 22, 14, 0, 0, Math.PI * 2); c.fill();
    // cuernos
    c.strokeStyle = '#e6dcc4'; c.lineWidth = 8; c.lineCap = 'round';
    c.beginPath(); c.moveTo(48, 58); c.quadraticCurveTo(16, 48, 10, 22);
    c.stroke();
    c.beginPath(); c.moveTo(58, 46); c.quadraticCurveTo(40, 20, 44, 4);
    c.stroke();
    // cuencas
    c.fillStyle = '#2c2118';
    c.beginPath(); c.ellipse(70, 60, 8, 9, 0, 0, Math.PI * 2); c.fill();
    c.beginPath(); c.ellipse(94, 58, 7, 8, 0, 0, Math.PI * 2); c.fill();
    return this._ct(cv);
  }
  /* --- CORAZÓN-diana del forajido (canvas, latirá por código) ------------- */
  _texCorazon() {
    const cv = oesteCanvas(128, 128);
    const c = cv.getContext('2d');
    const hg = c.createRadialGradient(64, 60, 8, 64, 60, 56);
    hg.addColorStop(0, '#ff9a8a'); hg.addColorStop(0.45, '#d81f2a');
    hg.addColorStop(1, 'rgba(120,10,16,0)');
    c.fillStyle = hg;
    c.beginPath();
    c.moveTo(64, 106);
    c.bezierCurveTo(10, 66, 26, 16, 64, 44);
    c.bezierCurveTo(102, 16, 118, 66, 64, 106);
    c.fill();
    c.strokeStyle = '#f6d34c'; c.lineWidth = 6;
    c.beginPath();
    c.moveTo(64, 106);
    c.bezierCurveTo(10, 66, 26, 16, 64, 44);
    c.bezierCurveTo(102, 16, 118, 66, 64, 106);
    c.stroke();
    return this._ct(cv);
  }
  /* --- diana de respaldo si el arte del artista aún no cargó -------------- */
  _texDianaFB() {
    const cv = oesteCanvas(128, 128);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 128, 128);
    const rings = [[60, '#f2e6c8'], [46, '#c8322a'], [32, '#f2e6c8'],
      [18, '#c8322a']];
    for (const [r, col] of rings) {
      c.fillStyle = col;
      c.beginPath(); c.arc(64, 64, r, 0, Math.PI * 2); c.fill();
    }
    return this._ct(cv);
  }
  /* --- halo/anillo rojo alrededor de la diana (aditivo) ------------------- */
  _texAnillo() {
    const cv = oesteCanvas(128, 128);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 128, 128);
    c.strokeStyle = 'rgba(255,70,52,0.9)'; c.lineWidth = 9;
    c.beginPath(); c.arc(64, 64, 52, 0, Math.PI * 2); c.stroke();
    c.strokeStyle = 'rgba(255,180,120,0.55)'; c.lineWidth = 4;
    c.beginPath(); c.arc(64, 64, 60, 0, Math.PI * 2); c.stroke();
    return this._ct(cv);
  }
  /* --- v2.100 · PLACA crema detrás de la retícula (contraste total) -------
   *  La retícula roja del artista sobre ladrillo rojo era INVISIBLE en el
   *  visor: ahora lleva detrás una placa de pergamino con borde oscuro que
   *  resalta sobre la fachada Y contra el cielo. */
  _texDianaBadge() {
    const cv = oesteCanvas(256, 256);
    const c = cv.getContext('2d');
    c.clearRect(0, 0, 256, 256);
    c.fillStyle = 'rgba(52,36,20,0.94)';           // borde oscuro
    c.beginPath(); c.arc(128, 128, 122, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#f6ecd2';                       // placa pergamino
    c.beginPath(); c.arc(128, 128, 110, 0, Math.PI * 2); c.fill();
    c.strokeStyle = 'rgba(200,50,42,0.85)';        // aro rojo fino
    c.lineWidth = 7;
    c.beginPath(); c.arc(128, 128, 92, 0, Math.PI * 2); c.stroke();
    return this._ct(cv);
  }
  /* --- v2.100 · FARO de luz: columna dorada que ASOMA SOBRE LOS TEJADOS --
   *  Se ve el escondite de un vistazo desde cualquier distancia (la
   *  fachada mide 2,9 m y el faro sube hasta ~5,5 m en las zonas altas).
   *  Columna FIJA (nada baila), alfa que se desvanece hacia arriba. */
  /** v2.102 · FARO ROJO del TNT: cuerpo SÓLIDO (el faro dorado de la
   *  mirilla se desvanece a 0 arriba y sobre el tejado no se veía). */
  _texFaroRojo() {
    const cv = oesteCanvas(64, 256);
    const c = cv.getContext('2d');
    const g = c.createLinearGradient(0, 256, 0, 0);
    g.addColorStop(0, 'rgba(224,52,30,1)');
    g.addColorStop(0.55, 'rgba(224,52,30,0.95)');
    g.addColorStop(0.8, 'rgba(224,52,30,0.42)');
    g.addColorStop(1, 'rgba(224,52,30,0)');
    c.fillStyle = g;
    c.fillRect(0, 0, 64, 256);
    const im = c.getImageData(0, 0, 64, 256);
    const d = im.data;
    for (let y = 0; y < 256; y++) {
      for (let x = 0; x < 64; x++) {
        const ex = Math.min(x, 63 - x) / 12;
        if (ex < 1) d[(y * 64 + x) * 4 + 3] *= Math.max(0, ex);
      }
    }
    c.putImageData(im, 0, 0);
    return this._ct(cv);
  }
  _texBeacon() {
    const cv = oesteCanvas(64, 256);
    const c = cv.getContext('2d');
    const g = c.createLinearGradient(0, 256, 0, 0);
    g.addColorStop(0, 'rgba(255,238,196,0.95)');
    g.addColorStop(0.45, 'rgba(255,212,126,0.40)');
    g.addColorStop(1, 'rgba(255,212,126,0)');
    c.fillStyle = g;
    c.fillRect(0, 0, 64, 256);
    const im = c.getImageData(0, 0, 64, 256);
    const d = im.data;
    for (let y = 0; y < 256; y++) {
      for (let x = 0; x < 64; x++) {
        const ex = Math.min(x, 63 - x) / 14;       // bordes laterales suaves
        if (ex < 1) d[(y * 64 + x) * 4 + 3] *= Math.max(0, ex);
      }
    }
    c.putImageData(im, 0, 0);
    return this._ct(cv);
  }

  /* ------------------------------- escena --------------------------------- */
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.group = new THREE.Group();
    this.group.visible = false;
    g.rig.add(this.group);

    /* --- CIELO v2.98: CÚPULA + banda IA alrededor + sol -------------------
     * Adiós plano negro al mirar arriba: la CÚPULA (respaldo procedural
     * con degradado de cenit) cierra el cielo y la franja IA del artista
     * rodea el horizonte en espejo (antes un cilindro corto y abierto). */
    this.sky = new THREE.Mesh(
      new THREE.SphereGeometry(30, 36, 20),
      new THREE.MeshBasicMaterial({
        map: this._texSkyDome(), side: THREE.BackSide, fog: false,
      }));
    this.sky.position.set(0, 0, 0);
    this.group.add(this.sky);
    this.texSky = this._aiTex('cielo.webp', this._texSky(), 10, 1, true);
    const banda = new THREE.Mesh(
      new THREE.CylinderGeometry(29.2, 29.2, 13.0, 36, 1, true),
      new THREE.MeshBasicMaterial({
        map: this.texSky, side: THREE.BackSide, fog: false,
      }));
    banda.position.set(0, 4.9, 0);
    banda.renderOrder = -2;   // v2.98: el cielo se pinta ANTES que los sprites
    this.group.add(banda);
    // SOL: resplandor cálido (el disco lo pinta la propia neblina del cielo)
    const sun = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.ctrl.fx.texDot, color: 0xfff2c8, transparent: true,
      opacity: 0.85, blending: THREE.AdditiveBlending, depthWrite: false,
      fog: false,
    }));
    sun.scale.setScalar(4.6);
    sun.position.set(6.4, 6.8, -11.8);
    this.group.add(sun);

    /* --- HORIZONTE v2.98: MONTAÑAS 360° (adiós línea del horizonte) -------
     * La sierra IA corre en espejo por un ANILLO cerrado que rodea toda
     * la escena; sus faldas bajan por debajo del suelo para que no se
     * vea el borde de la arena. El pueblo lejano sigue al fondo este. */
    // v2.106: la sierra IA se carga con FUNDIDO DE ALFA arriba/abajo —
    // adiós la línea continua mal recortada entre el cielo y las montañas.
    this.texMontes = this._aiTexFadeTop('montes.webp', this._texMontes(),
      8, 1, true, 0.46, 0.10);
    const montesRing = new THREE.Mesh(
      new THREE.CylinderGeometry(26, 26, 8.0, 36, 1, true),
      new THREE.MeshBasicMaterial({
        map: this.texMontes, transparent: true, side: THREE.BackSide,
        fog: false,
      }));
    montesRing.position.set(0, 3.4, 0);
    montesRing.renderOrder = -1;   // v2.98: sierra antes que los sprites
    this.group.add(montesRing);
    const pue = ASEDIO.pueblo;
    // v2.106 · LINEA DE CASAS del FONDO (lineapueblo.webp del artista): la
    // nueva y limpia, MÁS GRANDE y un poco MÁS ALEJADA — sensación de
    // pueblo tras las casas interactivas. Su alfa sano elimina la segunda
    // fila fantasma y las manchas del arte anterior.
    this.texPueblo = this._aiTexCut('lineapueblo.webp', null, 2048, 512);
    this.puebloMesh = new THREE.Mesh(
      new THREE.PlaneGeometry(pue.h * (pue.ar || 3.0), pue.h),
      new THREE.MeshBasicMaterial({ map: this.texPueblo, transparent: true,
        alphaTest: 0.3, fog: false, side: THREE.DoubleSide }));
    this.puebloMesh.position.set(0, pue.h / 2 - 0.42, pue.z);
    this.puebloMesh.renderOrder = -1;
    this.group.add(this.puebloMesh);
    // v2.106 · NUBES A LA DERIVA: puffs suaves que cruzan el cielo del
    // horizonte lejano empujadas por el viento (lentas, en bucle). Planos
    // FIJOS orientados una vez (nada de billboards que bailan).
    this.texNube = this._texNube();
    this.nubes = [];
    const nubeAt = (x, y, z, w, h, v, op) => {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
        new THREE.MeshBasicMaterial({ map: this.texNube, transparent: true,
          opacity: op, depthWrite: false, fog: false }));
      m.position.set(x, y, z);
      m.rotation.y = Math.atan2(-x, -z);   // encarada al jugador UNA vez
      m.renderOrder = 0;
      this.group.add(m);
      this.nubes.push({ m, v, x0: x });
    };
    nubeAt(-11.5, 6.6, -14.5, 7.4, 2.6, 0.42, 0.62);
    nubeAt(3.2, 7.6, -17.0, 9.2, 3.1, 0.30, 0.55);
    nubeAt(13.0, 6.1, -12.5, 6.2, 2.2, 0.55, 0.60);
    nubeAt(-16.5, 7.0, -9.0, 5.6, 2.0, 0.48, 0.50);
    nubeAt(9.4, 8.1, -15.8, 7.8, 2.7, 0.36, 0.58);
    nubeAt(-5.0, 8.5, -19.5, 8.6, 2.9, 0.26, 0.52);
    nubeAt(18.0, 5.6, -8.0, 5.0, 1.8, 0.62, 0.45);
    // v2.99 · PUEBLO LEJANO del ARTISTA (pueblohorizonte.png): recorte IA
    // de ambientación, lejos y frente al jugador, cerrando el horizonte
    // ENTRE las fachadas y la sierra. Fijo (plano, nada de billboards).

    /* --- SUELO: arena infinita + AVENIDA EMBARRADA + tablón-porción ------- */
    // v2.98: arena IA hasta el anillo de montañas (radio 24, antes 17)
    this.texArena = this._aiTex('arena.webp', this._texArena(), 8, 8, true);
    this.arena = new THREE.Mesh(new THREE.CircleGeometry(24, 40),
      new THREE.MeshBasicMaterial({ map: this.texArena, fog: false }));
    this.arena.rotation.x = -Math.PI / 2;
    this.group.add(this.arena);
    // v2.98: avenida IA con BORDES FUNDIDOS (adiós alfombra recortada)
    this.texBarro = this._aiTexFade('barro.webp', this._texBarro(), 1, 1, false);
    this.barro = new THREE.Mesh(new THREE.PlaneGeometry(3.9, 9.4),
      new THREE.MeshBasicMaterial({ map: this.texBarro, fog: false }));
    this.barro.rotation.x = -Math.PI / 2;
    this.barro.position.set(0, 0.008, -0.1);
    this.group.add(this.barro);
    const texBoard = this._texTablones('#5d3d1e', true);
    const matBoard = new THREE.MeshBasicMaterial({ map: texBoard });
    const board = new THREE.Mesh(new THREE.BoxGeometry(9.3, 0.06, 0.8), matBoard);
    board.position.set(0, 0.03, -4.30);
    this.group.add(board);
    const texWood = this._texTablones('#7a4a20', false);
    const matWood = new THREE.MeshBasicMaterial({ map: texWood });
    this.matWood = matWood;

    /* --- v2.98 · LA MESITA DE MADERA (adiós mesa de ping pong): un trozo
     * pequeño delante del jugador sobre el que BOTAN las bolas-bomba al
     * aparecer. MISMA ALTURA que la mesa (tableTopY): la física de la mesa
     * del núcleo queda desactivada (ignoreTable) y el módulo bota la
     * bola aquí con giro natural. */
    this.mesita = new THREE.Group();
    const MW = ASEDIO.mesita.w, MD = ASEDIO.mesita.d;
    const topY = ODIMS() ? ODIMS().tableTopY : 0.76;
    const mtop = new THREE.Mesh(new THREE.BoxGeometry(MW, 0.045, MD),
      matBoard);
    mtop.position.set(ASEDIO.mesita.x, topY - 0.0225, ASEDIO.mesita.z);
    mtop.renderOrder = 1;
    this.mesita.add(mtop);
    const legH = topY - 0.045;
    for (const [lx, lz] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.07, legH, 0.07),
        matWood);
      leg.position.set(ASEDIO.mesita.x + lx * (MW / 2 - 0.09),
        legH / 2, ASEDIO.mesita.z + lz * (MD / 2 - 0.09));
      this.mesita.add(leg);
    }
    this.group.add(this.mesita);

    /* --- v2.99 · LOS 3 EDIFICIOS INTERACTIVOS (arte del artista) ----------
     * Fuera la fila de 8 fachadas que no gustó: delante del jugador, tres
     * edificios IGUALES con Fachada1.png (delante, PERFORABLE con el
     * rotura), Interior1.png (detrás, se ve POR los boquetes) y el forajido
     * escondido ENTRE ambas imágenes. Sus zonas verdes salen de zonas1. */
    this.texFachada = this._aiTexCut('fachada1.webp', '#7a3d2c', 1024, 1024);
    this.texInterior = this._aiTexCut('interior1.webp', '#171009', 1024, 1024);
    /* v2.103 · UNA TEXTURA POR CASA: las fachadas e interiores 2-4 del
     * artista cargan junto a la 1; cada oleada VISTE sus 3 edificios al
     * empezar (con respaldo de color si una imagen tardara). */
    this.texFacCasa = [this.texFachada];
    this.texIntCasa = [this.texInterior];
    for (let i = 1; i < ASEDIO.casas.length; i++) {
      this.texFacCasa.push(this._aiTexCut(ASEDIO.casas[i].fac,
        '#7a3d2c', 1024, 1024));
      this.texIntCasa.push(this._aiTexCut(ASEDIO.casas[i].int,
        '#171009', 1024, 1024));
    }
    this.edif.length = 0;
    for (const bx of ASEDIO.edif.xs) this._buildEdificio(bx);
    this._zonasRebuild();
    this._loadImg('rotura_mascara.webp', (im) => { this._rotMask = im; });
    this._loadImg('rotura_chapas.webp', (im) => { this._rotChapas = im; });

    /* --- GRAN DEPÓSITO DE AGUA (torre de madera, junto a las casas) ------- */
    const tank = new THREE.Group();
    for (const [lx, lz] of [[-0.30, -0.30], [0.30, -0.30], [-0.30, 0.30],
      [0.30, 0.30]]) {
      const leg = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.72, 0.08), matWood);
      leg.position.set(lx, 0.86, lz);
      leg.rotation.z = lx > 0 ? 0.06 : -0.06;
      tank.add(leg);
    }
    const cuba = new THREE.Mesh(new THREE.CylinderGeometry(0.52, 0.56, 0.74, 12),
      matWood);
    cuba.position.y = 2.05;
    tank.add(cuba);
    const iron = new THREE.MeshBasicMaterial({ color: 0x3c3a38 });
    for (const by of [1.82, 2.28]) {
      const band = new THREE.Mesh(new THREE.CylinderGeometry(0.575, 0.575, 0.05, 12),
        iron);
      band.position.y = by;
      tank.add(band);
    }
    const roof = new THREE.Mesh(new THREE.ConeGeometry(0.64, 0.36, 10), matWood);
    roof.position.y = 2.6;
    tank.add(roof);
    // v2.106: torre de agua MÁS AFUERA (la casa exterior ahora llega hasta
    // x≈5,45 — la torre no puede quedar incrustada en su fachada)
    tank.position.set(6.15, 0, -4.55);
    this.group.add(tank);
    // v2.97 · DEPÓSITO IA: el recorte del artista TAPA la torre 3D al
    // cargar (si la imagen falla, la torre 3D procedural sigue ahí).
    // v2.99: PLANO FIJO (nada de sprites que giran con la cabeza).
    this._aiCut('torre.webp', null, 6.15, -4.55, 3.14, () => {
      tank.visible = false;
    });

    /* --- CACTUS IA repartidos (delante, lados y a nuestra espalda) --------
     * v2.97: saguaro y biznaga del artista con respaldo procedural; la
     * anchura sale del ASPECTO real de cada imagen (0,52 / 0,82). */
    this.cactusTex = [
      this._aiTex('cactus1.webp', this._texCactus(0)),
      this._aiTex('cactus2.webp', this._texCactus(1)),
    ];
    // v2.99: PLANOS FIJOS orientados una vez al jugador (sin baile)
    const cactusAt = (x, z, h, v) => {
      this._aiCut(v % 2 ? 'cactus2.webp' : 'cactus1.webp',
        this.cactusTex[v % 2], x, z, h);
    };
    cactusAt(-4.9, -2.5, 1.55, 0);
    cactusAt(4.8, -1.3, 1.25, 1);
    cactusAt(-6.4, -4.6, 1.75, 1);
    cactusAt(-3.15, 3.45, 1.05, 0);
    cactusAt(3.35, 2.85, 1.3, 1);
    cactusAt(-6.0, 0.8, 1.15, 0);      // v2.97: 3 de refuerzo
    cactusAt(6.3, -3.0, 1.35, 0);
    cactusAt(1.9, 5.2, 0.95, 1);

    /* --- v2.104 · SETOS SECOS RODANTES (regalo.png del artista) ----------
     *  Ambiente del pueblo: empujados por el viento ENTRAN por la DERECHA
     *  (fuera de campo) y RUEDAN hasta perderse por la IZQUIERDA (también
     *  fuera). Talla al azar — CUANTO MÁS PEQUEÑOS, MÁS RÁPIDOS — giran
     *  sobre sí mismos (ω = v/r, como rueda que no patina) y botan un
     *  pelín. Aparecen cada cierto tiempo al azar (pool de 3 simultáneos
     *  como máximo). Sólo ambiente: no chocan con bola ni jugador. */
    this.texSeto = this._aiTexCut('regalo.webp', null, 512, 512);
    this.setos = [];
    for (let i = 0; i < ASEDIO.setos.pool; i++) {
      const sMat = new THREE.MeshBasicMaterial({ map: this.texSeto,
        transparent: true, alphaTest: 0.25, depthWrite: false,
        fog: false });
      const sMesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), sMat);
      sMesh.renderOrder = 7;   // delante del forajido, como el arbusto
      const sGrp = new THREE.Group();
      sGrp.add(sMesh);
      sGrp.visible = false;
      this.group.add(sGrp);
      const sSom = new THREE.Mesh(new THREE.CircleGeometry(0.5, 16),
        new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true,
          opacity: 0.20, depthWrite: false }));
      sSom.rotation.x = -Math.PI / 2;
      sSom.renderOrder = 2;
      sSom.visible = false;
      this.group.add(sSom);
      this.setos.push({ grp: sGrp, mesh: sMesh, sombra: sSom,
        on: false, v: 0, h: 0.5 });
    }
    this._setoT = 1.4 + Math.random() * 1.8;   // el primero, pronto

    /* --- v2.98: BUITRES FUERA (petición del artista: pose fija sin
     * aleteo se ve artificial). El cielo queda limpio con su cúpula,
     * la banda de nubes IA y el sol. */
    this.buitres = [];

    /* --- HUESOS medio enterrados A NUESTRA ESPALDA (bisonte) ---------------
     * v2.97: ESQUELETO completo IA (costillaje + cráneo con cuernos) de una
     * pieza; fuera las dos planchas procedurales sueltas. */
    this._aiCut('huesos.webp', null, 0.1, 3.7, 0.85);
    /* --- ROCAS ROJIZAS IA (v2.97) — v2.99: PLANOS FIJOS ------------------- */
    this._aiCut('rocas.webp', null, -3.8, -3.6, 0.5);
    this._aiCut('rocas.webp', null, 5.7, 0.3, 0.4);
    this._aiCut('rocas.webp', null, 2.7, 5.0, 0.34);
    this._aiCut('rocas.webp', null, -5.4, 2.2, 0.3);
    for (const [bx, bz, ry] of [[2.1, 2.95, 0.6], [-0.45, 3.75, -0.4]]) {
      const b = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.035, 0.045),
        new THREE.MeshBasicMaterial({ color: 0xe0d6bc }));
      b.position.set(bx, 0.02, bz);
      b.rotation.y = ry;
      this.group.add(b);
    }

    /* --- ASTILLAS (pool de 18 trozos que saltan al reventar el troquel) --- */
    for (let i = 0; i < 18; i++) {
      const m = new THREE.Mesh(
        new THREE.BoxGeometry(0.05 + Math.random() * 0.08, 0.025,
          0.14 + Math.random() * 0.2), matWood);
      m.visible = false;
      m.renderOrder = 5;
      this.group.add(m);
      this._debris.push({ m, v: new THREE.Vector3(), w: new THREE.Vector3(),
        life: 0, t: 0 });
    }

    /* --- v2.101 · POLVO DENTRO de las casas (pool de 6): sprites que se
     *  dibujan ANTES que la fachada (renderOrder -1) — el jugador ve el
     *  polvo de una explosión INTERIOR SÓLO por los boquetes. */
    this._polvo = [];
    for (let i = 0; i < 6; i++) {
      const s = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texPuff, color: 0xb0a898, transparent: true,
        opacity: 0, depthWrite: false,
      }));
      s.visible = false;
      s.renderOrder = -1;
      this.group.add(s);
      this._polvo.push({ s, v: new THREE.Vector3(), life: 0, t: 0, r0: 0.15 });
    }

    /* --- MIRILLA (v2.100): retícula + PLACA crema + FARO sobre los tejados
     * El artista NO LA VEÍA (retícula roja sobre ladrillo rojo = camuflaje).
     * Ahora: (1) PLACA circular crema con borde oscuro detrás de la
     * retícula — resalta sobre fachada y cielo; (2) retícula MÁS GRANDE
     * (0,52→0,64 · halo 0,84→1,00); (3) FARO de luz dorado que sube desde
     * el escondite y ASOMA SOBRE LOS TEJADOS; (4) todo en PLANOS FIJOS
     * delante de la fachada: clavado, sin girarse ni bailar nunca. */
    this.texAnillo = this._texAnillo();
    this.dianaFBTex = this._texDianaFB();
    this.dianaBadgeTex = this._texDianaBadge();
    this.dianaBeaconTex = this._texBeacon();
    this.dianaHalo = new THREE.Mesh(new THREE.PlaneGeometry(1.00, 1.00),
      new THREE.MeshBasicMaterial({
        map: this.texAnillo, color: 0xff5040, transparent: true, opacity: 0.45,
        blending: THREE.AdditiveBlending, depthWrite: false, fog: false,
      }));
    this.dianaHalo.renderOrder = 8;
    this.dianaBeacon = new THREE.Mesh(new THREE.PlaneGeometry(0.17, 3.2),
      new THREE.MeshBasicMaterial({
        map: this.dianaBeaconTex, color: 0xffd27a, transparent: true,
        opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false,
        side: THREE.DoubleSide, fog: false,
      }));
    this.dianaBeacon.position.y = 0.28 + 1.6;    // sube desde la placa
    this.dianaBeacon.renderOrder = 8;
    this.dianaBadge = new THREE.Mesh(new THREE.PlaneGeometry(0.74, 0.74),
      new THREE.MeshBasicMaterial({
        map: this.dianaBadgeTex, transparent: true, depthWrite: false,
        fog: false,
      }));
    this.dianaBadge.renderOrder = 9;
    this.dianaFace = new THREE.Mesh(new THREE.PlaneGeometry(0.64, 0.64),
      new THREE.MeshBasicMaterial({
        map: this.dianaFBTex, transparent: true, depthWrite: false, fog: false,
      }));
    this.dianaFace.renderOrder = 10;
    this.dianaGrp = new THREE.Group();
    this.dianaGrp.add(this.dianaHalo);
    this.dianaGrp.add(this.dianaBeacon);
    this.dianaGrp.add(this.dianaBadge);
    this.dianaGrp.add(this.dianaFace);
    this.dianaGrp.visible = false;
    this.group.add(this.dianaGrp);

    /* --- CORAZÓN sobre el forajido destapado ------------------------------- */
    this.heart = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this._texCorazon(), transparent: true, depthWrite: false, fog: false,
    }));
    this.heart.scale.setScalar(0.30);   // v2.98: vive EN el pecho, no flotando
    this.heart.renderOrder = 11;
    this.heart.visible = false;
    this.group.add(this.heart);

    /* --- BOLA-BOMBA: mecha encendida enganchada a la bola del juego ------- */
    this.fuse = new THREE.Group();
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.0035, 0.0055, 0.052, 6),
      new THREE.MeshBasicMaterial({ color: 0x2e2114 }));
    rope.position.set(0, 0.02, 0);
    rope.rotation.z = 0.42;
    this.fuse.add(rope);
    this.spark = new THREE.Sprite(new THREE.SpriteMaterial({
      map: this.ctrl.fx.texDot, color: 0xffb25a, transparent: true,
      opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false,
    }));
    this.spark.scale.setScalar(0.06);
    this.spark.position.set(-0.0105, 0.0475, 0);
    this.fuse.add(this.spark);
    this.fuse.visible = false;
    if (g.ballMesh) g.ballMesh.add(this.fuse);

    /* --- v2.99 · EL FORAJIDO (uno solo: sale a la calle al destaparse) ----
     * ESTÁTICO (posición fija), de pie con la base EN EL SUELO y SIEMPRE
     * mirando al jugador (el sprite le encara). El CORAZÓN vive en su
     * pecho y SU REVÓLVER apunta a tu cabeza hasta disparar. */
    this.outlaw = new THREE.Sprite(new THREE.SpriteMaterial({
      transparent: true, depthWrite: false,
    }));
    this.outlaw.visible = false;
    this.outlaw.renderOrder = 8;
    this.outlaw.center.set(0.5, 0);
    this._outH = ASEDIO.outH;   // v2.101: 1,52 m — más pequeño, acorde a las casas
    this._outAR = 0.5;
    this._outSt = 'hidden';
    this._outAnimT = -1;
    this._outPopT = 0;
    this.group.add(this.outlaw);

    /* --- v2.103 · FUNDO NEGRO del descubrimiento: SU IMAGEN se funde a
     *  NEGRO y aparece SU DIBUJO APUNTANDO (Forajido_focused.png). Quad
     *  negro DELANTE del forajido (renderOrder 9: tapa al sprite 8 y a SU
     *  revólver opaco, que se dibuja antes), se funde con él y se retira. */
    this.outFadeNegro = new THREE.Mesh(new THREE.PlaneGeometry(1.5, 2.2),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true,
        opacity: 0, depthWrite: false, fog: false }));
    this.outFadeNegro.position.set(0, 1.0, ASEDIO.outZ + 0.22);
    this.outFadeNegro.renderOrder = 9;
    this.outFadeNegro.visible = false;
    this.group.add(this.outFadeNegro);
    /* --- v2.103 · BALAS trazadoras de SU disparo: vuelan hasta TU cara --- */
    this._balas = [];
    for (let i = 0; i < 2; i++) {
      const bs = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texDot, color: 0xffd27a, transparent: true,
        opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false,
      }));
      bs.scale.setScalar(0.07);
      bs.visible = false;
      bs.renderOrder = 12;
      this.group.add(bs);
      this._balas.push({ s: bs, from: new THREE.Vector3(),
        to: new THREE.Vector3(), t: 0, dur: 0.20, onHit: null });
    }

    this._buildBanner();
    this._buildFade();            // v2.106: fundido negro + imagen de derrota
    this._starEnsure();           // v2.106: precalienta la estrella (textura
                                  // cargada antes del primer spawn — ya no
                                  // aparece "sólo el halo")
    this._hud = new HudOeste(this.ctrl);
  }

  /* ------------------------------- ciclo ---------------------------------- */
  start() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    this.wave = 1;
    this.kills = 0;
    this.killsWave = 0;
    this.time = ASEDIO.waveTime;   // v2.99: 2 min POR OLEADA
    this.t = 0;
    this.revealT = 0;
    this.duckT = 0;
    this.duckKind = '';
    this._resultT = 0;
    this._dead = false;
    this._deadT = 0;
    this._floorB = 0;
    this._respawnT = 0.9;
    this._alarmOn = false;
    this._zona = null;
    this._outCock = false;
    this._outFocus = null;      // v2.103
    this.casasOleada = this._asignaCasas();   // v2.103: reparto de la PARTIDA
    // v2.105: la ESTRELLA DEL SHERIFF se agenda pronto (16-36 s) y no
    // arrastra ninguna visible de una partida anterior
    this._starT = ASEDIO.estrella.t1Min + Math.random() *
      (ASEDIO.estrella.t1Max - ASEDIO.estrella.t1Min);
    if (this._star) this._star.grp.visible = false;
    // v2.98: SIN mesa de ping pong NI red — sólo la MESITA de madera
    // delante del jugador; la SALA SE ABRE: fuera saloon, troqueles,
    // mapa, cartel, forajido de sala y arbusto (la avenida manda)
    if (!this.ctrl._netParts || !this.ctrl._netParts.length) {
      this.ctrl._netParts = this.ctrl._findNetParts();
    }
    for (const m of this.ctrl._netParts) m.visible = false;
    if (g.tableGroup) g.tableGroup.visible = false;
    g.ball.ignoreNet = true;
    g.ball.ignoreTable = true;   // v2.98: SIN mesa del núcleo (sólo la mesita)
    // v2.101: FUERA el muro invisible de la sala (x=±3,05): las dianas de
    // los edificios extremos eran INALCANZABLES — la bola rebotaba y
    // explotaba ANTES de llegar. En el desierto mandan los límites propios
    // (sideX/backZ/killZ); el SUELO sigue activo (la bomba estalla en la
    // arena) y la restauración está en dispose().
    g.ball.ignoreWalls = true;
    // v2.102: BOMBA PESADA — corta el aire (dragMul 0.30): los tiros altos
    // llegan a las dianas altas en vez de caer 2-4 m antes (el artista
    // «acertaba en dianas y el forajido no salía»)
    g.ball.dragMul = 0.30;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (g.roomGroup) g.roomGroup.visible = false;
    if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = false;
    this.ctrl.mapa.visible = false;
    this.ctrl.cartel.visible = false;
    if (this.ctrl.sprite) this.ctrl.sprite.visible = false;
    if (this.ctrl.arbustoGroup) this.ctrl.arbustoGroup.visible = false;
    if (this.ctrl.arbustoSombra) this.ctrl.arbustoSombra.visible = false;
    g.champDecorHidden = true;   // v2.95: el núcleo DEJA DE re-mostrarlos
    g.rules.state = this.ctrl.stateName;      // el árbitro duerme
    g.rules.message = tx('asedio_up');
    // v2.98: la bola ya no cruza red ninguna (no hay mesa): ignoreNet
    this.ctrl._parkMainBall();
    g.ballMesh.visible = false;                // hasta el primer lanzamiento
    // BOLA-BOMBA: negra, con brillo propio cálido y la MECHA encendida
    const bm = g.ballMesh;
    if (bm && bm.material) {
      if (!this._ballSaved) {
        this._ballSaved = {
          col: bm.material.color ? bm.material.color.getHex() : null,
          em: bm.material.emissive ? bm.material.emissive.getHex() : null,
          ei: bm.material.emissiveIntensity !== undefined
            ? bm.material.emissiveIntensity : 1,
        };
      }
      try {
        bm.material.color.setHex(0x17120d);
        if (bm.material.emissive) bm.material.emissive.setHex(0x2a1408);
        if (bm.material.emissiveIntensity !== undefined) {
          bm.material.emissiveIntensity = 0.55;
        }
      } catch (e) { /* material sin emisivo: da igual */ }
    }
    if (this.fuse) this.fuse.visible = true;
    // v2.99: fachadas REHECHAS (sin boquetes), zonas nuevas, nadie a la vista
    this._resetEdificios();
    this.heart.visible = false;
    this.dianaGrp.visible = false;
    this.outlaw.visible = false;
    this._outlawGunRemove();
    // v2.98: DOS PALAS, una por mano — se golpea con cualquiera; los
    // REVÓLVERES (1 disparo por mano) llegan al DESTAPAR un forajido
    this.ctrl._starGunApply(false);   // v2.118: sin pistola de la estrella
    this.ctrl._twoGunApply(false);
    this.ctrl._twoPaddles(true);
    this.ctrl.musicOn();
    this._hud.show();
    this._hud.set(this.time, this._prog(), tx('asedio_up'), undefined, this._marc(),
      this.ctrl.puntos);
    this.ctrl.sfx('desenfundar', 0);
    this.ctrl.sfx('whistle', 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 120);
    // v2.99: la partida EMPIEZA con el cartel «OLEADA 1» (5 s en pausa)
    this._showBanner(1, function () {
      this._spawnTarget();
      this._serveBall();
      this.phase = 'play';
      this.game.rules.message = tx('asedio_oleada',
        { n: 1, m: this._waveNeed() });
      this._msg = '';
      this._msgT = 0;
    });
  }

  /** v2.99 · Forajidos que toca matar en la OLEADA vigente (3/5/7 v2.116). */
  _waveNeed() { return (this.ctrl && this.ctrl._leyendaOn ? 1 : 0) + (ASEDIO.perWave[this.wave - 1] || 5); }   // v3.6.18 (ronda 24): LEYENDA +1 forajido
  /** v2.116 · MARCADOR: forajidos que FALTAN por matar en la oleada
   *  (se pinta con contador.png en la esquina superior izquierda). */
  _marc() {
    const m = this._waveNeed();
    return { n: Math.max(0, m - this.killsWave), m };
  }
  /** v2.99 · Progresión para el HUD (v2.106: alcanzado el cupo, la oleada
   *  SIGUE hasta agotar sus 2 minutos — se marca COMPLETA y se sigue
   *  contando bajas). */
  _prog() {
    if (this.phase === 'win') {
      return '¡LIMPIO! ' + this.kills + ' FORAJIDOS';
    }
    /* v2.118 · SÓLO «OLEADA n/3»: la cuenta de bajas vive en el cartel
     * contador.png — el «· k/N» duplicaba el dato y CHOCABA con el reloj
     * de la oleada (textos solapados en la banda). */
    return 'OLEADA ' + this.wave + '/3';
  }
  _hudMsg() {
    if (this.phase === 'reveal') return tx('asedio_diana');
    return this._msgT > 0 ? this._msg : '';
  }

  /** FÍSICA + FASES (lo llama el núcleo vía testStep, 1 vez por frame). */
  step(dt) {
    if (this.done || this.phase === 'idle') return;
    const g = this.game;
    this.t += dt;
    this._hitCd = Math.max(0, this._hitCd - dt);
    this._wallCd = Math.max(0, this._wallCd - dt);
    if (this._msgT > 0) this._msgT -= dt;
    // v2.101 · RÁFAGA del cartucho de dinamita: explosiones pequeñas y
    // próximas entre sí (estruendo + MANDOS temblando por tandas).
    if (this._tntSeq && this._tntSeq.length) {
      this._tntT += dt;
      while (this._tntSeq.length && this._tntSeq[0].t <= this._tntT) {
        const ev = this._tntSeq.shift();
        _AS_V1.set(ev.x, ev.y, ev.z);
        this.ctrl.fx.flash(_AS_V1, 0.9 + Math.random() * 0.7, 0xffc98a);
        this.ctrl.fx.spark(_AS_V1, 8, 0xd9b06a, 2.6, 1.2);
        this.ctrl.fx.smoke(_AS_V1, 1, false);
        this.ctrl.sfx('boom', 0);
        if (g.renderer.xr.isPresenting) {
          const hi = 0.45 + Math.random() * 0.4;
          g.haptic(0, hi, 130);
          g.haptic(1, hi, 130);
        }
      }
      if (!this._tntSeq.length) this._tntSeq = null;
    }
    // v2.101 · LA DIANA SE MUDA cada 20 s (siempre a una zona libre):
    // polvo en el sitio viejo, polvo en el nuevo (¡persíguela!)
    if (this.phase === 'play' && this.dianaGrp.visible && this._zona) {
      this._dianaMoveT -= dt;
      if (this._dianaMoveT <= 0) this._moverDiana();
    }
    // v2.104 · SETOS RODANTES: el pueblo respira (en TODAS las fases)
    this._setosStep(dt);
    // v2.105 · ESTRELLA DEL SHERIFF: vive, gira y agenda la próxima
    this._starStep(dt);
    // v2.106 · NUBES a la deriva + FUNDIDO de la transición de oleada
    this._nubesStep(dt);
    this._fadeStep(dt);
    this._derrotaStep(dt);   // v2.106: cinemática de derrota (risa→victoria)
    if (this.phase === 'banner') {
      // v2.99: cartel de OLEADA cruzando la calle — juego y reloj EN PAUSA
      this._parkBall();
    } else if (this.phase === 'play') {
      this.time -= dt;
      // v2.99: ALARMA al quedar 20 s de la oleada
      if (this.time <= ASEDIO.alarmAt && !this._alarmOn) {
        this._alarmOn = true;
        this.ctrl.sfx('alarma', 0);
        this._msg = tx('asedio_alarma');
        this._msgT = 2.6;
        g.rules.message = this._msg;
      }
      if (this.time <= 0) {
        // v2.106 · LA OLEADA DURA LOS 2 MINUTOS COMPLETOS: al agotarse el
        // reloj, la 1ª/2ª pasan a la siguiente y la 3ª es VICTORIA — nunca
        // se corta la partida a mitad de tiempo (el cupo de forajidos ya
        // no adelanta el final: alcanzado el cupo, SIGUEN saliendo).
        this.time = 0;
        if (this.wave >= 3) this._win(); else this._nextWave();
      }
      else if (this._dead) {
        this._respawnT -= dt;
        if (this._respawnT <= 0) this._serveBall();
      } else {
        this._simBall(dt);
      }
    } else if (this.phase === 'reveal') {
      this.time -= dt;
      if (this.time <= 0) {
        this.time = 0;
        if (this.wave >= 3) this._win(); else this._nextWave();
      }
      else {
        this._parkBall();
        this.revealT -= dt;
        // v2.99: SE NOTA que va a disparar — el forajido APRIETA el gatillo
        if (!this._outCock && this.revealT <= 0.65) {
          this._outCock = true;
          this.ctrl.sfx('desenfundar', 0);
        }
        if (this.revealT <= 0) this._punish();
      }
    } else if (this.phase === 'duck') {
      this._parkBall();
      this.duckT -= dt;
      if (this.duckT <= 0) this._duckEnd();
    } else if (this.phase === 'win' || this.phase === 'fail') {
      this._parkBall();
      this._resultT -= dt;
      if (this._resultT <= 0) this._finish();
    }
    this._hud.set(this.time, this._prog(), this._hudMsg(), undefined, this._marc(),
      this.ctrl.puntos);
  }

  /** v2.104 · SETOS SECOS RODANTES (regalo.png): cruzan la calle de
   *  DERECHA a IZQUIERDA empujados por el viento. Talla al azar —
   *  pequeño = RÁPIDO (v = kVel/h) —, giran sobre sí mismos (ω = v/r
   *  como una rueda que rueda de verdad) y botan un pelín (la avenida no
   *  es lisa). Ambiente puro: nada de física ni colisiones. */
  _setosStep(dt) {
    const S = ASEDIO.setos;
    if (!this.setos || !this.setos.length) return;
    this._setoT -= dt;
    if (this._setoT <= 0) {
      this._setoT = S.tMin + Math.random() * (S.tMax - S.tMin);
      const libres = [];
      for (const s of this.setos) if (!s.on) libres.push(s);
      if (libres.length) {
        const s = libres[(Math.random() * libres.length) | 0];
        s.h = S.hMin + Math.random() * (S.hMax - S.hMin);
        s.v = S.kVel / s.h;            // pequeño → RÁPIDO
        s.on = true;
        const z = S.zMin + Math.random() * (S.zMax - S.zMin);
        s.grp.position.set(S.xIn, 0, z);
        s.mesh.scale.setScalar(s.h);
        s.mesh.rotation.z = Math.random() * Math.PI * 2;
        s.sombra.scale.setScalar(s.h);
        s.sombra.position.set(S.xIn, 0.004, z);
        s.grp.visible = true;
        s.sombra.visible = true;
      }
    }
    for (const s of this.setos) {
      if (!s.on) continue;
      s.grp.position.x -= s.v * dt;
      // v2.106 · GIRO CORREGIDO: rueda hacia -X ⇒ ω_z POSITIVO (la rueda
      //  gira como una rueda de verdad — antes giraba AL REVÉS, patinando
      //  al estilo «luna circular»). ω = v/r.
      s.mesh.rotation.z += (s.v * dt) / (s.h * 0.5);  // rueda SIN patinar
      s.mesh.position.y = s.h *
        (0.50 + 0.05 * Math.abs(Math.sin(s.mesh.rotation.z)));
      s.sombra.position.x = s.grp.position.x;
      if (s.grp.position.x < -S.xIn) {
        s.on = false;
        s.grp.visible = false;
        s.sombra.visible = false;
      }
    }
  }

    // v2.106 · NUBES: cruzan el horizonte empujadas por el viento y se
    // reciclan por el otro lado (bucle infinito, sin saltos visibles).
    _nubesStep(dt) {
      if (!this.nubes || !this.nubes.length) return;
      for (const n of this.nubes) {
        n.m.position.x += n.v * dt;
        if (n.m.position.x > 24) n.m.position.x = -24;
      }
    }
    /* ========================================================================
   *  v2.105 · ¡LA ESTRELLA DEL SHERIFF! (mecánica sorpresa de la avenida)
   *  ------------------------------------------------------------------
   *  Cada oleada, 2-3 veces al azar, una ESTRELLA dorada del sheriff
   *  aparece flotando DELANTE de una casa (gira, brilla y suelta
   *  chispas) durante ~7,5 s. Si la aciertas con una BOMBA:
   *    · el sheriff DESTAPA AL FORAJIDO al instante (breach de la diana
   *      vigente: revólveres cargados sin acertar la diana), y
   *    · te regala +12 s de reloj (oro que compra tiempo).
   *  Riesgo/recompensa: desvías la puntería de la diana para cazarla
   *  mientras las bombas siguen cadenzando.
   *  ======================================================================== */
  _starEnsure() {
    if (this._star) return this._star;
    const E = ASEDIO.estrella;
    const grp = new THREE.Group();
    grp.visible = false;
    const tex = this._aiTexCut('estrella.webp', null, 256, 256);
    // v2.106: depthTest FALSE — la estrella JAMÁS se lo traga una fachada
    // ni una casa vecina (antes, con la casa al fondo y el z-fighting, la
    // estrella desaparecía y sólo quedaba su halo).
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true,
      depthWrite: false, depthTest: false, fog: false });
    const star = new THREE.Sprite(mat);
    star.scale.setScalar(E.size);
    star.renderOrder = 9;
    grp.add(star);
    let halo = null;
    try {
      halo = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.ctrl.fx.texPuff, color: 0xffd77a, transparent: true,
        opacity: 0.28, blending: THREE.AdditiveBlending,
        depthWrite: false, depthTest: false, fog: false }));
      halo.scale.setScalar(E.size * 2.1);
      halo.renderOrder = 8;
      grp.add(halo);
    } catch (e) { halo = null; }
    this.group.add(grp);
    this._star = { grp, mat, halo, spkT: 0.4 };
    return this._star;
  }
  /** Aparece frente a una casa al azar (sin comerse a la diana vigente). */
  _starSpawn() {
    const E = ASEDIO.estrella;
    const s = this._starEnsure();
    let px = 0, py = E.yMin;
    for (let i = 0; i < 8; i++) {
      const ed = this.edif[(Math.random() * this.edif.length) | 0];
      px = ed.x + (Math.random() - 0.5) * ASEDIO.edif.w * 0.52;
      py = E.yMin + Math.random() * (E.yMax - E.yMin);
      const dz = this._zona ? Math.abs(px - this._zona.x) : 1;
      const dy = this._zona ? Math.abs(py - this._zona.my) : 1;
      if (dz > 0.85 || dy > 1.05) break;   // separada de la diana
    }
    s.grp.position.set(px, py, ASEDIO.facadeZ + E.zDZ);
    s.mat.opacity = 1;
    s.mat.rotation = Math.random() * Math.PI;
    s.grp.visible = true;
    this._starLife = E.vida;
    this.ctrl.sfx('coin', 0);
    this._msg = tx('asedio_estrella');
    this._msgT = 2.2;
    /* v2.118 · AL APARECER la estrella, la pala de UNA mano se cambia
     * por el REVÓLVER (petición del artista: «puede alcanzarse
     * disparando con la pistola») — al desaparecer la estrella, la pala
     * vuelve (_starHide). Si ya hay revólveres de diana, no toca nada. */
    if (!(this.ctrl && this.ctrl._twoGuns)) this.ctrl._starGunApply(true);
    _AS_V1.copy(s.grp.position);
    this.ctrl.fx.flash(_AS_V1, 1.0, 0xffd77a);
    this.ctrl.fx.spark(_AS_V1, 8, 0xffd77a, 2.2, 1.0);
  }
  /** Vive, gira, brilla, parpadea al acabar y agenda la PRÓXIMA. */
  _starStep(dt) {
    const E = ASEDIO.estrella;
    const on = this._star && this._star.grp.visible;
    if (!on) {
      // sólo se AGENDA en juego real (con diana viva para el destape)
      if (this.phase === 'play' && this.dianaGrp.visible && this._zona) {
        this._starT -= dt;
        if (this._starT <= 0) this._starSpawn();
      }
      return;
    }
    const s = this._star;
    this._starLife -= dt;
    s.mat.rotation += dt * 2.6;                    // gira sobre sí misma
    if (s.halo) {
      s.halo.material.opacity = 0.22 + Math.sin(this.t * 6.2) * 0.10;
      s.halo.scale.setScalar(E.size *
        (2.0 + Math.sin(this.t * 4.4) * 0.22));
    }
    s.spkT -= dt;
    if (s.spkT <= 0) {
      s.spkT = 0.38 + Math.random() * 0.3;
      _AS_V1.copy(s.grp.position);
      this.ctrl.fx.spark(_AS_V1, 3, 0xffd77a, 1.3, 0.7);
    }
    if (this._starLife < E.parp) {                 // parpadeo final
      s.mat.opacity = 0.35 + 0.65 *
        (0.5 + 0.5 * Math.sin(this._starLife * 16));
    }
    if (this._starLife <= 0) this._starHide();
  }
    // v2.106 · FUNDIDO A NEGRO: subida (0,5 s) → negro con las casas
    // rehechas → bajada (0,6 s) mientras el cartel sigue su cruce.
    // SOLO manda en la fase 'banner' (en 'fail' manda la cinemática).
    _fadeStep(dt) {
      if (this.phase !== 'banner') return;
      if (!this.fadeNegro || !this.fadeNegro.visible) return;
      this._fadeT += dt;
      const t = this._fadeT;
      if (t < 0.5) {
        this.fadeNegro.material.opacity = t / 0.5;
      } else if (t < 1.4) {
        this.fadeNegro.material.opacity = 1;
        if (!this._fadeDone && this._fadeDuring) {
          this._fadeDone = true;
          try { this._fadeDuring.call(this); } catch (e) { /* */ }
          this._fadeDuring = null;
        }
      } else if (t < 2.0) {
        this.fadeNegro.material.opacity = 1 - (t - 1.4) / 0.6;
      } else {
        this.fadeNegro.material.opacity = 0;
        this.fadeNegro.visible = false;
        this._fadeDuring = null;
      }
    }
    /** ¡BOMBA A LA ESTRELLA! El sheriff señala al forajido y regala tiempo. */
  _starHit() {
    const g = this.game;
    const E = ASEDIO.estrella;
    const s = this._star;
    if (!s || !s.grp.visible) return;
    _AS_V1.copy(s.grp.position);
    this.ctrl.sfx('coin', 0);
    this.ctrl.fx.flash(_AS_V1, 1.9, 0xffd77a);
    this.ctrl.fx.spark(_AS_V1, 26, 0xffd77a, 3.4, 1.6);
    this.ctrl.fx.smoke(_AS_V1, 2, false);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 160);
    this.time += E.extraT;                        // ¡ORO = TIEMPO!
    this.ctrl._puntosAdd(150, s.grp.position);    // v2.119: estrella +150
    if (this.phase === 'play' && this.dianaGrp.visible && this._zona) {
      this._breach(this._zona);     // destape inmediato + revólveres
      this._msg = tx('asedio_estrella_ok', { n: E.extraT | 0 });
      this._msgT = 2.6;
      g.rules.message = this._msg;
    } else {
      this._msg = tx('asedio_estrella_solo', { n: E.extraT | 0 });
      this._msgT = 2.4;
      g.rules.message = this._msg;
    }
    this._starHide();
  }
  /** Se esfuma y agenda la próxima (restMin..restMax s). */
  _starHide() {
    if (this._star) this._star.grp.visible = false;
    /* v2.118 · al DESAPARECER la estrella vuelve la PALA (la pistola
     * estaba atada a su vida; si montaron los revólveres de diana, esto
     * ya es no-op — _twoGunApply la retiró). */
    this.ctrl._starGunApply(false);
    const E = ASEDIO.estrella;
    this._starT = E.restMin + Math.random() * (E.restMax - E.restMin);
  }
  _starDispose() {
    if (!this._star) return;
    this._disposeTree(this._star.grp);
    this._star = null;
  }

  /** VISUAL por frame (lo llama CTRL.update): buitres, diana, corazón,
   *  mecha, forajidos (pop/caída/escondite) y mira láser. */
  fxStep(dt) {
    if (this.done || !this.inited) return;
    const g = this.game;
    // astillas: vuelo + giro + caída
    for (const d of this._debris) {
      if (d.life <= 0) continue;
      d.t += dt;
      d.v.y -= 7.5 * dt;
      d.m.position.addScaledVector(d.v, dt);
      d.m.rotation.x += d.w.x * dt;
      d.m.rotation.z += d.w.z * dt;
      const f = 1 - d.t / d.life;
      if (f <= 0) { d.life = 0; d.m.visible = false; continue; }
      d.m.scale.setScalar(Math.max(0.05, f));
      if (d.m.position.y < 0.03) {
        d.m.position.y = 0.03;
        d.v.multiplyScalar(0.4);
        d.v.y = Math.abs(d.v.y) * 0.3;
      }
    }
    // v2.101: polvo DENTRO de las casas (sube y se funde; visible sólo por
    // los boquetes porque se dibuja ANTES que la fachada)
    if (this._polvo) {
      for (const s of this._polvo) {
        if (s.life <= 0) continue;
        s.t += dt;
        const k = s.t / s.life;
        s.s.position.addScaledVector(s.v, dt);
        s.s.scale.setScalar(s.r0 * (1 + k * 2.4));
        s.s.material.opacity = 0.55 * (k < 0.2 ? k / 0.2 : 1 - (k - 0.2) / 0.8);
        if (k >= 1) { s.life = 0; s.s.visible = false; }
      }
    }
    // v2.101: brasa del CARTUCHO ESCONDIDO (late; al DESTAPARLO late más)
    if (this._tnt && this._tnt.halo) {
      const h = this._tnt.halo;
      const rev = this._tnt.revealed;
      h.material.opacity = (rev ? 0.26 : 0.14) +
        Math.sin(this.t * (rev ? 8.2 : 4.6)) * (rev ? 0.08 : 0.04);
      h.scale.setScalar((rev ? 0.37 : 0.30) + Math.sin(this.t * 7.1) * 0.03);
    }
    // v2.102: FARO ROJO del TNT — late sobre el tejado de SU casa (y sisea:
    // pista sonora para encontrarla, se oye aunque no la veas)
    if (this._tnt && this._tnt.beacon) {
      const bc = this._tnt.beacon;
      const rev = this._tnt.revealed;
      bc.material.opacity = (rev ? 0.85 : 0.62) +
        Math.sin(this.t * (rev ? 6.4 : 3.1)) * (rev ? 0.10 : 0.14);
      const sx = (rev ? 1.10 : 1.0) + Math.sin(this.t * 2.3) * 0.10;
      bc.scale.set(sx, 1, 1);
    }
    if (this._tnt && (this.phase === 'play' || this.phase === 'reveal')) {
      this._tntSisT -= dt;
      if (this._tntSisT <= 0) {
        this._tntSisT = 3.4 + Math.random() * 2.2;
        this.ctrl.sfx('mecha', 0);
      }
    }
    // v2.98: buitres retirados — el decorado NO se mueve
    // diana: arte del artista en cuanto cargue + vaivén + halo latiendo
    if (this.dianaGrp.visible) {
      const dtex = this.ctrl.dianaTex;
      if (dtex && dtex.image && this.dianaFace.material.map !== dtex) {
        this.dianaFace.material.map = dtex;
        this.dianaFace.material.needsUpdate = true;
      }
      // v2.98: diana ESTÁTICA mientras esté presente (sin vaivén ni
      // latido) — y el corazón fijo en el pecho del forajido
      this.dianaHalo.material.opacity = 0.45;
      this.dianaHalo.scale.setScalar(1.0);
    }
    // mecha de la bola-bomba: chispa + bufido cadenciado (bola viva)
    if (this.fuse) {
      const on = g.ballMesh.visible && this.phase === 'play';
      this.fuse.visible = on;
      if (on) {
        this.spark.scale.setScalar(0.045 + Math.abs(Math.sin(this.t * 23)) * 0.03);
        this.spark.material.opacity = 0.65 + Math.sin(this.t * 17) * 0.3;
        this._mechaT -= dt;
        if (this._mechaT <= 0) { this._mechaT = 0.5; this.ctrl.sfx('mecha', 0); }
      }
    }
    // v2.98 · GIRO NATURAL de la bola-bomba (rueda según su ω acumulada)
    if (g.ballMesh && g.ballMesh.visible &&
        this._tumbleW.lengthSq() > 1e-6) {
      const w = this._tumbleW.length();
      _AS_Q.setFromAxisAngle(_AS_V1.copy(this._tumbleW).normalize(),
        w * dt);
      g.ballMesh.quaternion.premultiply(_AS_Q);
      this._tumbleW.multiplyScalar(Math.pow(0.86, dt * 60));
    }
    // v2.98: las DOS palas siguen en su sitio (el núcleo puede re-ocultar
    // la montura libre al reconectar un mando a mitad de etapa)
    if (this.ctrl._twoPaddlesOn && g.paddleMounts) {
      for (let k = 0; k < 2; k++) {
        if (g.paddleMounts[k] && !this.ctrl._gunLoaded(k)) {
          g.paddleMounts[k].visible = true;
        }
      }
    }
    // v2.99 · FORAJIDO único: pop al salir, desplome al morir, taparse al huir
    if (this.outlaw && this.outlaw.visible) {
      if (this._outPopT > 0) {
        this._outPopT -= dt;
        const k = 1 - Math.max(0, this._outPopT) / 0.18;
        const s = 0.6 + 0.4 * k;
        this.outlaw.scale.set(this._outH * (this._outAR || 0.5) * s,
          this._outH * s, 1);
      }
      if (this._outSt === 'down' && this._outAnimT >= 0) {
        this._outAnimT += dt;
        this.outlaw.position.y = Math.max(0.0, 0.02 - this._outAnimT * 0.4);
        this.outlaw.material.rotation = Math.min(0.9, this._outAnimT * 1.1);
        this.outlaw.material.opacity = Math.max(0, 1 - this._outAnimT / 1.4);
        if (this._outAnimT >= 1.5) {
          this.outlaw.visible = false;
          this._outAnimT = -1;
        }
      } else if (this._outSt === 'duck' && this._outAnimT >= 0) {
        this._outAnimT += dt;
        this.outlaw.material.opacity = Math.max(0, 1 - this._outAnimT / 0.45);
        this.outlaw.position.y = 0.02 - Math.min(0.18, this._outAnimT * 0.5);
        if (this._outAnimT >= 0.5) {
          this.outlaw.visible = false;
          this._outAnimT = -1;
        }
      }
    }
    // v2.103 · CORAZÓN: MEDIA TALLA y PARPADEANDO (la diana vital; petición
    // del artista: «esta diana debe ser la mitad de tamaño y estar
    // parpadeando (su corazón)»)
    if (this.heart.visible) {
      const pul = Math.abs(Math.sin(this.t * 5.4));
      this.heart.scale.setScalar(ASEDIO.heartR * (0.82 + pul * 0.42));
      this.heart.material.opacity = 0.60 + pul * 0.40;
    }
    // v2.103 · DESCUBRIMIENTO: imagen → FUNDO A NEGRO → dibujo APUNTANDO
    if (this._outFocus && this._outSt === 'up' && this.phase === 'reveal') {
      this._outFocusStep(dt);
    }
    // v2.103 · BALAS del forajido en vuelo (hacia tu cara)
    if (this._balas) {
      for (const b of this._balas) {
        if (b.t <= 0) continue;
        b.t += dt;
        const k = Math.min(1, b.t / b.dur);
        b.s.position.lerpVectors(b.from, b.to, k);
        b.s.material.opacity = 0.95;
        b.s.scale.setScalar(0.07 + k * 0.05);
        if (k >= 1) {
          b.t = 0;
          b.s.visible = false;
          if (b.onHit) { const cb = b.onHit; b.onHit = null; cb(); }
        }
      }
    }
    // v2.99 · SU REVÓLVER te APUNTA sin descanso mientras está destapado
    if (this._outlawGun && this._outlawGun.grp.visible) {
      const cam = g.camera;
      if (cam) {
        cam.getWorldPosition(_AS_V4);
        this._outlawGun.grp.lookAt(_AS_V4);
      }
    }
    // v2.99 · CARTEL de oleada: velocidad de entrada, vaivén, velocidad de salida
    if (this.bannerGrp && this.bannerGrp.visible) {
      const B = ASEDIO.banner;
      this._bannerT += dt;
      const bt = this._bannerT;
      if (bt < B.tIn) {
        const k = bt / B.tIn;
        const e = k * k;                       // acelera: EFECTO DE VELOCIDAD
        this.bannerGrp.position.x = B.xIn * (1 - e);
        this.bannerGrp.position.y = B.y;
        this.bannerMesh.scale.x = B.size * this._bannerAR * (1 + (1 - e) * 0.55);
      } else if (bt < B.tIn + B.tFloat) {
        const tf = bt - B.tIn;
        this.bannerGrp.position.x = Math.sin(tf * 1.3) * 0.035;
        this.bannerGrp.position.y = B.y + Math.sin(tf * 2.1) * 0.028;
        this.bannerMesh.rotation.z = Math.sin(tf * 1.7) * 0.02;
        this.bannerMesh.scale.x = B.size * this._bannerAR;
      } else if (bt < B.tIn + B.tFloat + B.tOut) {
        const k = (bt - B.tIn - B.tFloat) / B.tOut;
        const e = 1 - (1 - k) * (1 - k);       // acelera hacia la izquierda
        this.bannerGrp.position.x = -B.xIn * e;
        this.bannerMesh.scale.x = B.size * this._bannerAR * (1 + e * 0.55);
      } else {
        this.bannerGrp.visible = false;
        this.bannerMesh.rotation.z = 0;
        const after = this._bannerAfter;
        this._bannerAfter = null;
        if (after) after.call(this);
      }
    }
    // v2.98 · MIRA LÁSER de CADA revólver cargado (una por mano); se
    // enciende (hot) cuando la orientación se acerca bastante al corazón
    if (this.phase === 'play' || this.phase === 'reveal') {
      let any = false;
      /* v2.118 · láser para los revólveres de diana Y para la pistola de
       * la estrella (mismo trato: se calienta al apuntarle). */
      const guns = (this.ctrl._twoGuns || []).slice();
      if (this.ctrl._starGunRec && this.ctrl._starGunRec.art) {
        guns.push(this.ctrl._starGunRec);
      }
      for (const rrec of guns) {
        if (!rrec.art) continue;
        const ray = this.ctrl._gunRayHand(rrec.hand) || this._cameraRay();
        if (!ray) continue;
        any = true;
        let len = 8.0, hot = false;
        // v2.117: la estrella TAMBIÉN calienta el láser (fase 'play')
        if (!hot && this.phase === 'play' && this._star &&
            this._star.grp.visible) {
          const sp = this._star.grp.position;
          const toS = _AS_V1.copy(sp).sub(ray.pos);
          const tS = clamp(toS.dot(ray.dir), 0, len);
          const cS = _AS_V2.copy(ray.dir).multiplyScalar(tS).add(ray.pos);
          if (cS.distanceToSquared(sp) <
              Math.pow(ASEDIO.estrella.r * 1.5, 2)) {
            hot = true;
            len = Math.max(0.4, tS);
          }
        }
        const target = (this.phase === 'reveal' && this.heart.visible)
          ? this.heart.position : null;
        if (target) {
          const toT = _AS_V1.copy(target).sub(ray.pos);
          const tHit = clamp(toT.dot(ray.dir), 0, len);
          const closest = _AS_V2.copy(ray.dir).multiplyScalar(tHit).add(ray.pos);
          hot = closest.distanceTo(target) <
            ASEDIO.heartR * ASEDIO.heartAssist;
          len = hot ? Math.max(0.4, tHit) : len;
        }
        if (!hot && ray.dir.z < -1e-4) {
          const tF = (ASEDIO.facadeZ + 0.02 - ray.pos.z) / ray.dir.z;
          if (tF > 0.05 && tF < len) len = tF;
        }
        this.ctrl.fx.laserUpdate(ray.pos, ray.dir, len, hot, rrec.hand);
      }
      if (!any) this.ctrl.fx.laserVisible(false);
    } else {
      this.ctrl.fx.laserVisible(false);
    }
    if (this.ctrl.fx) this.ctrl.fx.update(dt);
  }

  /* ------------------------------ gatillo -------------------------------- */
  /** v2.98 · GATILLO POR MANO: cada revólver tiene SU disparo (1 por
   *  arma). hand = mando que aprieta (el núcleo lo trae desde
   *  onSelectStart); sin mano (escritorio/pruebas) dispara la primera
   *  cargada. Al gastarse, el revólver desaparece y vuelve la PALA. */
  trigger(hand) {
    if (this.phase !== 'play' && this.phase !== 'reveal') return;
    let rec = null;
    if (hand === undefined || hand === null) {
      rec = this.ctrl._twoGuns && this.ctrl._twoGuns.find((r) => r.art);
      /* v2.118 · sin revólveres de diana, el gatillo dispara la PISTOLA
       * de la estrella (si está en mano). */
      if (!rec && this.ctrl._starGunRec && this.ctrl._starGunRec.art) {
        rec = this.ctrl._starGunRec;
      }
      if (!rec) return;
      hand = rec.hand;
    } else {
      hand = hand | 0;
      rec = this.ctrl._twoGuns &&
        this.ctrl._twoGuns.find((r) => r.hand === hand && r.art);
      if (!rec && this.ctrl._starGunRec &&
          this.ctrl._starGunRec.hand === hand && this.ctrl._starGunRec.art) {
        rec = this.ctrl._starGunRec;
      }
      if (!rec) return;                  // esa mano no tiene revólver
    }
    const ray = this.ctrl._gunRayHand(hand) || this._cameraRay();
    if (!ray) return;
    const now = performance.now() / 1000;
    if (!this._gunLastH) this._gunLastH = {};
    if (now - (this._gunLastH[hand] || 0) < 0.16) return;
    this._gunLastH[hand] = now;
    this._shotAt(ray.pos, ray.dir, hand);
  }
  /** DISPARO contra un rayo concreto (VR o escritorio/cámara). */
  _shotAt(pos, dir, hand) {
    const g = this.game;
    let len = 8.0;
    this.ctrl.fx.flash(_AS_V1.copy(pos).addScaledVector(dir, 0.02), 1.1, 0xffd98a);
    this.ctrl.sfx('disparo', 0);
    if (g.renderer.xr.isPresenting) {
      g.haptic(hand === undefined ? 1 - g.paddleHand : hand, 0.5, 110);
    }
    // v2.117 · ¿AL DISPARO CAZA LA ESTRELLA DEL SHERIFF? (petición del
    // artista: la estrella se alcanza con el revólver TAMBIÉN, no sólo
    // con la bomba). Rayo contra la esfera de la estrella con un
    // asistente generoso (×1.5, como el corazón) — si entra, la estrella
    // destapa al forajido y regala el tiempo (v2.119: el revólver de
    // diana se gasta; la pistola de la estrella no gasta nada).
    if (this._star && this._star.grp.visible) {
      const sp = this._star.grp.position;
      const rHit = ASEDIO.estrella.r * 1.5;
      const toS = _AS_V2.copy(sp).sub(pos);
      const tS = clamp(toS.dot(dir), 0, len);
      const cS = _AS_V3.copy(dir).multiplyScalar(tS).add(pos);
      if (cS.distanceToSquared(sp) < rHit * rHit) {
        _AS_V2.copy(sp).sub(pos).normalize();
        this.ctrl.fx.beam(pos, _AS_V2, Math.max(0.4, toS.length()));
        /* v2.119 · ¿QUIÉN disparó? Si fue la PISTOLA DE LA ESTRELLA (arma
         * sin munición), NO se gasta nada: _starHit puede DESTAPAR al
         * forajido (_breach monta DOS revólveres frescos) y antes
         * _gunHandRemove se COMÍA uno de ellos — el jugador se quedaba
         * sin pistola para el forajido que aparecía. Los revólveres de
         * diana sí se gastan (1 disparo, como siempre). */
        const starGunWas = !!(this.ctrl._starGunRec &&
          this.ctrl._starGunRec.art &&
          this.ctrl._starGunRec.hand === (hand | 0));
        this._starHit();
        if (!starGunWas) this.ctrl._gunHandRemove(hand);
        return;
      }
    }
    // ¿al corazón? (ventana del forajido destapado) — v2.98: con
    // ASISTENTE, los casi-aciertos también abaten (la orientación se
    // acerca bastante) y el trazo ENTRA en el corazón
    if (this.phase === 'reveal' && this.heart.visible) {
      const toH = _AS_V2.copy(this.heart.position).sub(pos);
      const t = clamp(toH.dot(dir), 0, len);
      const closest = _AS_V3.copy(dir).multiplyScalar(t).add(pos);
      if (closest.distanceTo(this.heart.position) <
          ASEDIO.heartR * ASEDIO.heartAssist) {
        _AS_V2.copy(this.heart.position).sub(pos).normalize();
        this.ctrl.fx.beam(pos, _AS_V2, Math.max(0.4,
          _AS_V3.copy(this.heart.position).sub(pos).length()));
        this._killOutlaw();
        this.ctrl._gunHandRemove(hand);   // gastado: pala otra vez
        return;
      }
    }
    // impacto en las fachadas de madera (chispas y polvo)
    if (dir.z < -1e-4) {
      const tF = (ASEDIO.facadeZ + 0.03 - pos.z) / dir.z;
      if (tF > 0.05 && tF < len) {
        _AS_V2.copy(pos).addScaledVector(dir, tF);
        if (Math.abs(_AS_V2.x) < ASEDIO.rowHalf && _AS_V2.y > 0 &&
            _AS_V2.y < ASEDIO.facadeH) {
          len = tF;
          this.ctrl.fx.spark(_AS_V2, 8, 0xd9b06a, 2.4, 1);
          this.ctrl.fx.smoke(_AS_V2, 1, false);
          this.ctrl.sfx('madera', 0);
        }
      }
    } else if (dir.y < -1e-4) {
      const D = ODIMS();
      const ty = D ? D.tableTopY : 0.76;
      const tFloor = (ty - pos.y) / dir.y;
      if (tFloor > 0.05 && tFloor < len) len = tFloor;
    }
    this.ctrl.fx.beam(pos, dir, len);
    this.ctrl._gunHandRemove(hand);   // v2.98: disparo gastado → la pala vuelve
  }
  /** Rayo de cámara para escritorio/headless (sin XR no hay mandos). */
  _cameraRay() {
    const g = this.game;
    try {
      const cam = g.camera;
      if (!cam) return null;
      return {
        pos: cam.position.clone(),
        dir: cam.getWorldDirection(new THREE.Vector3()).normalize(),
      };
    } catch (e) { return null; }
  }

  /* ------------------------------ bola ----------------------------------- */
  _parkBall() {
    const g = this.game;
    if (g.ball.pos.y > -5) {
      // v2.101: (0,-4,0) y NO (0,-10,0) — aparcando a -10 el núcleo creía
      // la bola PERDIDA bajo el mundo, la TELETRANSPORTABA a (0, 0.5, -1.6)
      // y emitía un 'floor' FANTASMA: la módulo la explotaba allí y el
      // humo salía DEBAJO DE LA MESITA.
      g.ball.pos.set(0, -4, 0);
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = false;
    }
  }
  /** SERVIDOR de bolas-bomba: cae sobre la media mesa del jugador. */
  _serveBall() {
    const g = this.game;
    const D = ODIMS();
    this._dead = false;
    this._dentro = false;      // v2.101: bola nueva, fuera de las casas
    this._deadT = 0;
    this._floorB = 0;
    // v2.97 · JUNTO AL CANTO (petición del artista): antes caía a media mesa
    // (+0,85) y no se llegaba bien. Ahora suelta al 92-98 % de la media
    // longitud y con poca deriva hacia dentro: aterriza a 10-18 cm del canto
    // de NUESTRA mesa, al alcance de la pala sin estirarse.
    const hl = D ? D.tableHalfLength : 1.37;
    const cz = D ? D.tableCenterZ : 0;
    g.ball.pos.set((Math.random() - 0.5) * 0.5, 1.42,
      cz + hl * (0.92 + Math.random() * 0.06));
    g.ball.vel.set((Math.random() - 0.5) * 0.35, -0.6, -0.22);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = true;
    this.ctrl.sfx('lanzar', 0);
  }
  /** v2.102 · ¿la bomba estalló AL PIE de la mirilla? (arena al pie de la
   *  fachada, ±0,62 m del centro): la ONDA EXPANSIVA alcanza la diana. */
  _dianaAlAlcance(p) {
    if (!this.dianaGrp.visible || !this._zona) return false;
    // sólo las mirillas a RAS DE SUELO (planta baja): la onda de una bomba
    // que estalla en la arena llega hasta ahí; para media/álta hay que
    // acertar a la fachada (el tiro pesado ya llega con dragMul)
    if (this._zona.feetY >= 0.60) return false;
    if (Math.abs(p.x - this._zona.x) > ASEDIO.assistRX) return false;
    return p.z <= ASEDIO.facadeZ + 1.15 && p.z >= ASEDIO.facadeZ - 0.35;
  }
  /** Física de la bola del núcleo + muerte/recambio + colisionador propio. */
  _simBall(dt) {
    const g = this.game;
    const D = ODIMS();
    const presenting = g.renderer.xr.isPresenting;
    // v2.98: DOS PALAS — se golpea con cualquiera de las dos manos
    // (salvo cuando esa mano sostiene un revólver cargado)
    const pads = [];
    if (presenting && g.controllerPaddles) {
      for (let k = 0; k < 2; k++) {
        const ps = g.controllerPaddles[k];
        if (ps && ps.active && !this.ctrl._gunLoaded(k)) pads.push(ps);
      }
    }
    g.events.length = 0;
    if (this._prev) this._prev.copy(g.ball.pos);
    else this._prev = g.ball.pos.clone();
    stepPhysics(dt, g.ball, pads, g.events, this._extra);
    // v2.101: si la bola MURIÓ DENTRO del paso de física (fachada, diana o
    // cartucho), los eventos que vengan DESPUÉS son viejos: el teletransporte
    // de seguridad del núcleo emitía un 'floor' falso que explotaba junto a
    // la mesita (EL HUMO BAJO LA MESA).
    if (this._dead) return;
    for (const e of g.events) {
      if (e.type === 'paddle') {
        this._floorB = 0;
        if (e.speed) this.ctrl.sfx('pala', 0);
        this._tumbleHit(e.speed || 2);       // v2.98: giro natural
      } else if (e.type === 'floor' || e.type === 'wall') {
        // v2.98: la bomba SIEMPRE EXPLOTA en el suelo o contra paredes
        // v2.102: ...SALVO que estalle en la ARENA al pie de la mirilla:
        // la onda expansiva alcanza la diana y sale el forajido
        const ep = e.pos || g.ball.pos;
        if (e.type === 'floor' && this._dianaAlAlcance(ep)) {
          this._breach(this._zona);
          return;
        }
        this._bolaBoom(ep);
        this._killBall();
        return;
      }
    }
    // v2.105 · ¿la bomba CAZÓ la estrella del sheriff? (esfera generosa:
    //  se mira el TRAZADO completo del frame, el arco de la bomba la roza
    //  y cuenta)
    if (this._star && this._star.grp.visible) {
      const sp = this._star.grp.position;
      const R = ASEDIO.estrella.r;
      _AS_V2.copy(g.ball.pos).sub(this._prev);       // delta del frame
      const L2 = _AS_V2.lengthSq();
      let tSeg = 0;
      if (L2 > 1e-8) {
        tSeg = clamp(_AS_V3.copy(sp).sub(this._prev).dot(_AS_V2) / L2,
          0, 1);
      }
      _AS_V2.multiplyScalar(tSeg).add(this._prev);   // punto más cercano
      if (_AS_V2.distanceToSquared(sp) < R * R) {
        this._starHit();
        return;
      }
    }
    const b = g.ball;
    // v2.98: fuera de límites → EXPLOTA en el aire (fin del recorrido)
    if (b.pos.z > ASEDIO.backZ || b.pos.z < ASEDIO.killZ ||
        b.pos.x > ASEDIO.sideX || b.pos.x < -ASEDIO.sideX) {
      this._bolaBoom(b.pos);
      this._killBall();
      return;
    }
    // v2.98: sin botes en la arena — al tocar el SUELO, EXPLOTA (además
    // del evento 'floor' del núcleo, por si baja ya sin empuje)
    if (b.pos.y < 0.05 && b.vel.y < 0.4) {
      // v2.102: estallido AL PIE de la mirilla → la onda la alcanza
      if (this._dianaAlAlcance(b.pos)) {
        this._breach(this._zona);
        return;
      }
      this._bolaBoom(b.pos);
      this._killBall();
      return;
    }
    // bola PARADA (en la mesita): la mecha acaba de ESTALLAR
    if (b.vel.lengthSq() < 0.09 && b.pos.y < D.tableTopY + 0.15) {
      this._deadT += dt;
      if (this._deadT > 0.9) {
        this._deadT = 0;
        this._bolaBoom(b.pos);
        this._killBall();
      }
    } else this._deadT = 0;
  }
  /** v2.101 · Explosión de la bola: si muere DENTRO de una casa (entró por
   *  un boquete) y cae CERCA del cartucho escondido, lo DETONA. */
  _bolaBoom(p) {
    const t = this._tnt;
    const T = ASEDIO.tnt;
    if (t && p.z < ASEDIO.facadeZ - 0.02 &&
        Math.abs(p.x - t.x) < T.hitR && p.y < T.hitH) {
      this._tntBoom();
      return;
    }
    this._boomAt(p, false);
  }
  /** v2.98 · EXPLOSIÓN de la bola-bomba (la receta de la dinamita:
   *  estruendo + destello + chispas + humo; big=true la de la diana). */
  _boomAt(p, big) {
    _AS_V1.set(p.x, Math.max(0.12, p.y), p.z);
    this.ctrl.sfx('boom', 0);
    this.ctrl.fx.flash(_AS_V1, big ? 1.7 : 1.3, 0xffd28a);
    this.ctrl.fx.spark(_AS_V1, big ? 20 : 14, 0xd9b06a, big ? 3.6 : 2.8,
      1.2);
    this.ctrl.fx.smoke(_AS_V1, big ? 4 : 3, !!big);
    const g = this.game;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.55, 120);
  }
  /** v2.98 · GIRO NATURAL: al botar/golpear la bola rueda (ω = v⊥/r
   *  alrededor del eje perpendicular al movimiento horizontal). */
  _tumbleHit(speed) {
    const g = this.game;
    const v = g.ball.vel;
    _AS_V1.set(v.x, 0, v.z);
    const sp = clamp(Math.max(1.2, Math.min(6, speed || _AS_V1.length())),
      1.2, 6);
    if (_AS_V1.lengthSq() < 1e-4) _AS_V1.set(1, 0, 0);
    _AS_V1.normalize();
    _AS_V2.set(-_AS_V1.z, 0, _AS_V1.x);   // eje de rodadura
    const w = clamp(sp * 2.6, 2.0, 14.0);
    this._tumbleW.copy(_AS_V2).multiplyScalar(w * (0.7 + Math.random() * 0.6));
    this._tumbleW.x += (Math.random() - 0.5) * 4;
  }
  _killBall() {
    if (this._dead) return;
    this._dead = true;
    this._dentro = false;      // v2.101: la bola ya no está dentro de una casa
    this._deadT = 0;
    this._respawnT = ASEDIO.respawnT;
    this.game.ballMesh.visible = false;
    this._parkBall();
  }

  /* ------------------------- colisionador extra --------------------------- */
  /** Bola vs FACHADA (barrido del subpaso a 480 Hz): ¿DIANA o madera? */
  _collide(ball) {
    if (this.phase !== 'play') return;
    const p = ball.pos;
    const D = ODIMS();
    const r = D ? D.ballRadius : 0.02;
    /* --- v2.98 · MESITA de madera (el núcleo juega SIN mesa): bote con
     *  la misma restitución que la mesa de siempre + giro natural. */
    const topR = (D ? D.tableTopY : 0.76) + r;
    const inX = Math.abs(p.x - ASEDIO.mesita.x) <=
      ASEDIO.mesita.w / 2 + r * 0.5;
    const inZ = Math.abs(p.z - ASEDIO.mesita.z) <=
      ASEDIO.mesita.d / 2 + r * 0.5;
    const prevY = this._prev ? this._prev.y : p.y;
    if (ball.vel.y < 0 && prevY >= topR && p.y < topR && inX && inZ) {
      p.y = topR;
      const impact = -ball.vel.y;
      ball.vel.y = impact * (D ? D.tableRestitution : 0.88);
      ball.vel.x *= (D ? D.tableFriction : 0.94);
      ball.vel.z *= (D ? D.tableFriction : 0.94);
      this._tumbleHit(impact);
      this.ctrl.sfx('madera', 0);
      return;
    }
    if (ball.vel.z > -0.02) return;            // fachadas: ACERCÁNDOSE
    const zPlane = ASEDIO.facadeZ + r;
    if (!this._dentro) {
      if (p.z > zPlane) return;
      p.z = zPlane + 0.002;
      // v2.99 · ¿DIANA de fachada? (delante de la fachada, SIEMPRE visible)
      // con ASISTENTE: si la trayectoria se acerca bastante, el impacto CUENTA
      if (this.dianaGrp.visible && this._zona) {
        // v2.102 · ASISTENTE ELÍPTICO: la ONDA EXPANSIVA de la bomba cubre un
        // óvalo alrededor de la mirilla (centrado un poco POR DEBAJO: el aire
        // frena los tiros altos y la bola llegaba 1-1,5 m baja — el artista
        // «acertaba en la diana y el forajido no salía»). Sigue valiendo el
        // tiro directo al centro y el de la propia placa.
        const dx = p.x - this._zona.x;
        const dy = p.y - (this._zona.my - ASEDIO.assistDrop);
        const ex = dx / ASEDIO.assistRX;
        const ey = dy / ASEDIO.assistRY;
        if (ex * ex + ey * ey <= 1) {
          this._breach(this._zona);
          return;
        }
      }
      // v2.101 · ¿POR UN BOQUETE? — la fachada ya agujereada DEJA PASAR la
      // bola: entra en la casa (y puede darse con el CARTUCHO ESCONDIDO)
      const TP = ASEDIO.tnt;
      let thru = false;
      for (const eb of this.edif) {
        if (Math.abs(p.x - eb.x) > ASEDIO.edif.w / 2 + TP.passR) continue;
        for (const h of eb.holes) {
          const dx = p.x - h.x, dy = p.y - h.y;
          if (dx * dx + dy * dy < TP.passR * TP.passR) { thru = true; break; }
        }
        if (thru) break;
      }
      if (thru) { this._dentro = true; return; }   // la bola SIGUE volando
      // v2.99 · IMPACTO en FACHADA: BOQUETE (rotura del artista) + TROCITOS
      // que salen despedidos + la bomba explota SIEMPRE contra la pared
      const eb = this._edificioEn(p.x);
      if (eb && p.y > ASEDIO.edif.y && p.y < ASEDIO.edif.h + 0.25) {
        // v2.104: si el impacto cae sobre zona YA destruida, rompe la
        // FACHADA TRASERA (el interior) en el MISMO sitio: hueco real
        if (this._zonaRota(eb, p.x, p.y)) {
          this._perforaFondo(eb, p.x, p.y);
        } else {
          this._perfora(eb, p.x, p.y);
        }
        this._splinters(p.x, p.y);
        this.ctrl.sfx('madera', 0);
        // v2.99: si el boquete DESTRUYÓ el escondite de la diana vigente, la
        // diana salta a otra zona (nadie se esconde en una ruina)
        if (this.dianaGrp.visible && this._zona &&
            !this._zonaLibre(this._zona)) {
          this._spawnTarget();
        }
      }
      _AS_V1.set(p.x, clamp(p.y, 0.2, ASEDIO.facadeH), ASEDIO.facadeZ + 0.03);
      this._boomAt(_AS_V1, false);
      this._killBall();
      return;
    }
    // --- v2.101 · LA BOLA ESTÁ DENTRO DE LA CASA (entró por un boquete):
    // ¿le da al CARTUCHO DE DINAMITA? o estalla contra la pared del fondo
    const TI = ASEDIO.tnt;
    if (this._tnt && p.z <= ASEDIO.facadeZ + TI.zDZ + r &&
        Math.abs(p.x - this._tnt.x) < TI.hitR && p.y < TI.hitH) {
      this._tntBoom();                       // ¡MEDIA CASA POR LOS AIRES!
      return;
    }
    if (p.z <= ASEDIO.facadeZ + ASEDIO.interiorDZ + r) {
      // v2.104: la bola que entró por un boquete ESTALLA contra el fondo y
      // ROMPE la fachada trasera: hueco real de lado a lado de la casa
      const eb = this._edificioEn(p.x);
      if (eb && p.y > ASEDIO.edif.y && p.y < ASEDIO.edif.h + 0.25) {
        this._perforaFondo(eb, p.x, p.y);
      }
      _AS_V1.set(p.x, clamp(p.y, 0.2, ASEDIO.facadeH),
        ASEDIO.facadeZ + ASEDIO.interiorDZ + 0.05);
      this._polvoDentro(p.x, p.y,
        ASEDIO.facadeZ + ASEDIO.interiorDZ + 0.06, 3);
      this._bolaBoom(_AS_V1);
      this._killBall();
    }
  }

  /* --------------------- diana, destape y castigo ------------------------- */
  /** v2.100 · MIRILLA sobre una ZONA VERDE libre de zonas1.jpg (aleatoria,
   *  distinta de la actual, y SOLO en sitios con la fachada ENTERA):
   *  planos fijos DELANTE de la fachada, centrada EN LA LÍNEA VERDE
   *  (donde asoma el forajido — lo pide la vista), con placa de
   *  contraste y faro que asoma sobre los tejados. */
  _spawnTarget() {
    const libres = this.zonas.filter((z) => this._zonaLibre(z));
    // v2.106 · SIN RECAMBIO NO SE PIERDE LA PRUEBA: si TODAS las zonas
    // están agujereadas, el forajido SE ASOMA por un boquete (se reutiliza
    // la menos destrozada) — el fin de la prueba SOLO lo manda el reloj.
    if (!libres.length) {
      const resto = this.zonas.filter((z) => z !== this._zona);
      if (!resto.length) {
        this._fail();                 // caso extremo: sin zonas ni reciclaje
        return;
      }
      this._zona = resto[(Math.random() * resto.length) | 0];
      this.dianaGrp.position.set(this._zona.x, this._zona.my,
        ASEDIO.facadeZ + ASEDIO.dianaDZ);
      this.dianaGrp.visible = true;
      this._dianaMoveT = ASEDIO.dianaMoveT;
      return;
    }
    const pool = libres.filter((z) => z !== this._zona);
    const src = pool.length ? pool : libres;
    const z = src[(Math.random() * src.length) | 0];
    this._zona = z;
    this.dianaGrp.position.set(z.x, z.my,
      ASEDIO.facadeZ + ASEDIO.dianaDZ);
    this.dianaGrp.visible = true;
    this._dianaMoveT = ASEDIO.dianaMoveT;   // v2.101: mudanza en 20 s
  }
  /** v2.101 · ¡LA DIANA SE MUDA DE SITIO! (cada 20 s, petición del
   *  artista: «la diana va cambiando de posición cada 20 segundos»).
   *  Ráfaga de polvo en el sitio viejo, salto a una zona libre y polvo
   *  en el nuevo. Si su fachada quedó agujereada, _spawnTarget ya
   *  excluye las zonas prohibidas. */
  _moverDiana() {
    const vieja = this._zona;
    if (vieja) {
      _AS_V1.set(vieja.x, vieja.my, ASEDIO.facadeZ + 0.06);
      this.ctrl.fx.smoke(_AS_V1, 2, false);
      this.ctrl.fx.spark(_AS_V1, 5, 0xc9b088, 1.6, 1);
    }
    this._spawnTarget();                    // re-pone el contador a 20 s
    if (this._zona && this._zona !== vieja) {
      _AS_V1.set(this._zona.x, this._zona.my, ASEDIO.facadeZ + 0.06);
      this.ctrl.fx.smoke(_AS_V1, 2, false);
      this.ctrl.sfx('mecha', 0);
    }
  }
  /** v2.99 · EL FORAJIDO SE PLANTA EN LA CALLE: de pie (base en el suelo),
   *  estático, mirándote, CORAZÓN en el pecho (su diana, NUNCA separado)
   *  y SU REVÓLVER apuntándote desde que sale. */
  _outReveal(z) {
    const td = this.ctrl.texsDuelo || {};
    const ts = this.ctrl.texs || {};
    const tex = td['duelo'] || ts['panic'] || ts['angry'] || ts['idle'];
    if (tex) {
      this.outlaw.material.map = tex;
      this.outlaw.material.needsUpdate = true;
      const img = tex.image;
      this._outAR = (img && img.width && img.height)
        ? img.width / img.height : 0.5;
    }
    this.outlaw.material.opacity = 1;
    this.outlaw.material.rotation = 0;
    this.outlaw.position.set(z.x, 0.02, ASEDIO.outZ);
    this.outlaw.scale.set(this._outH * (this._outAR || 0.5), this._outH, 1);
    this.outlaw.visible = true;
    this._outSt = 'up';
    this._outAnimT = -1;
    this._outPopT = 0.18;
    // v2.106 · CORAZÓN IMPREDECIBLE: aparece SOBRE CUALQUIER PARTE de su
    // cuerpo (altura al azar entre las piernas y los hombros, y deriva
    // lateral ±0,18 m) — nada de apuntar siempre al mismo sitio.
    this.heart.position.set(
      z.x + (Math.random() - 0.5) * 0.36,
      0.55 + Math.random() * 0.85,
      ASEDIO.outZ + 0.06);
    this.heart.scale.setScalar(ASEDIO.heartR);   // v2.103: MEDIA TALLA
    this.heart.material.opacity = 1;
    // v2.103: el CORAZÓN se enciende con el dibujo APUNTANDO, no antes
    this.heart.visible = false;
    // v2.103 · DESCUBRIMIENTO EN 2 FASES (petición del artista): primero SU
    // IMAGEN; acto seguido SU SILUETA se desvanece (alfa real, SIN plano
    // negro — v2.106) y aparece SU DIBUJO APUNTANDO (Forajido_focused.png).
    this._outFocus = ((this.ctrl.texs || {})['focused'])
      ? { fase: 'espera', t: ASEDIO.outFocusDelay } : null;
    if (this.outFadeNegro) {
      // v2.106: el quad negro RECTANGULAR del fundido JUBILADO — su borde
      // duro delataba el truco («no está recortada su silueta»)
      this.outFadeNegro.visible = false;
    }
    this._outlawGunApply(z.x, ASEDIO.outZ);
  }
  /** v2.106 · FUNDO DEL DESCUBRIMIENTO (alfa real): espera → SU IMAGEN se
   *  desvanece POR SU SILUETA (transparencia del recorte, cero planos
   *  negros) → CAMBIO al dibujo APUNTANDO (Forajido_focused.png) → vuelve
   *  a aparecer. Al terminar se enciende SU CORAZÓN como diana. */
  _outFocusStep(dt) {
    const f = this._outFocus;
    if (!f) return;
    if (f.fase === 'espera') {
      f.t -= dt;
      if (f.t <= 0) {
        f.fase = 'a'; f.t = ASEDIO.outFadeT;
      }
      return;
    }
    if (f.fase === 'a') {              // SU IMAGEN se desvanece (silueta)
      f.t -= dt;
      const k = 1 - Math.max(0, f.t) / ASEDIO.outFadeT;
      this.outlaw.material.opacity = 1 - k;
      if (f.t <= 0) {
        const ts = this.ctrl.texs || {};
        const tex = ts['focused'];
        if (tex) {
          this.outlaw.material.map = tex;
          this.outlaw.material.needsUpdate = true;
          const img = tex.image;
          if (img && img.width && img.height) {
            this._outAR = img.width / img.height;
            this.outlaw.scale.set(this._outH * this._outAR, this._outH, 1);
          }
        }
        this.outlaw.material.opacity = 0;
        f.fase = 'b'; f.t = ASEDIO.outFadeT;
      }
      return;
    }
    if (f.fase === 'b') {              // aparece APUNTANDO desde la nada
      f.t -= dt;
      const k = 1 - Math.max(0, f.t) / ASEDIO.outFadeT;
      this.outlaw.material.opacity = k;
      if (f.t <= 0) {
        this.outlaw.material.opacity = 1;
        f.fase = 'fin';
        this.heart.visible = true;     // AHORA sí: su corazón es la diana
      }
    }
  }
  /** v2.99 · REVÓLVER del forajido (revolver.glb) apuntando AL JUGADOR. */
  _outlawGunApply(x, zpos) {
    this._outlawGunRemove();
    const C = this.ctrl;
    if (!C._revolverModel) return;    // GLB aún cargando: el onload re-aplica
    const art = C._revolverModel.clone(true);
    art.scale.multiplyScalar(0.34 / (DISPARO.escala || 0.34));
    const m = C._medirCañon(art);
    const grp = new THREE.Group();
    grp.add(art);
    grp.position.set(x + 0.16, ASEDIO.gunY, zpos + 0.12);
    this.group.add(grp);
    this._outlawGun = { grp, art, muzzle: m.muzzle };
    /* v2.103 · ENCARO VERIFICADO (el heurístico fijo se equivocaba con este
     * GLB: el revólver apuntaba AL LADO CONTRARIO AL JUGADOR). Ahora: miro
     * al jugador, mido hacia dónde sale el cañón EN EL MUNDO y giro 180°
     * SÓLO si de verdad apunta al otro lado. La realidad manda. */
    try {
      const g = this.game;
      if (g.camera && m.muzzle) {
        g.camera.getWorldPosition(_AS_V4);
        grp.lookAt(_AS_V4);
        this.group.updateMatrixWorld(true);
        art.updateWorldMatrix(true, false);
        const mw = art.localToWorld(m.muzzle.clone());
        const base = grp.getWorldPosition(_AS_V5);
        const alJug = _AS_V4.sub(base);            // jugador - revólver
        const sal = _AS_V6.copy(mw).sub(base);     // boca del cañón - revólver
        if (sal.dot(alJug) < 0) art.rotation.y += Math.PI;
      }
    } catch (e) { /* sin cámara: queda tal cual */ }
  }
  _outlawGunRemove() {
    if (!this._outlawGun) return;
    if (this._outlawGun.grp.parent) {
      this._outlawGun.grp.parent.remove(this._outlawGun.grp);
    }
    this._outlawGun = null;   // SIN dispose: la geometría es COMPARTIDA
  }
  /** v2.103 · BALA trazadora: vuela de la boca de SU revólver a TU cara
   *  (~0,16 s) y AL LLEGAR ejecuta el impacto (sangre + tirón del mando).
   *  El artista: «debe salir humo y una bala que se vea hacia la cara del
   *  jugador para que quede claro que le acaba de disparar». */
  _balaVuela(from, onHit) {
    if (!this._balas || !this._balas.length) return false;
    const g = this.game;
    try { g.camera.getWorldPosition(_AS_V5); } catch (e) { return false; }
    for (const b of this._balas) {
      if (b.t > 0 && b.t < b.dur) continue;    // ocupada
      b.from.copy(from);
      b.to.copy(_AS_V5);
      b.t = 1e-4;
      b.onHit = onHit || null;
      b.s.visible = true;
      return true;
    }
    return false;
  }
  /** ¡LA BOMBA EN LA DIANA! OTRO BOQUETE en la fachada (se ve el interior)
   *  y el FORAJIDO sale DE PIE a la calle, con su revólver apuntándote. */
  _breach(z) {
    const g = this.game;
    if (!z) return;
    // 1) BOQUETE donde está la MIRILLA: la explosión abre la fachada
    const dyT = z.my;   // v2.100: en la línea verde
    this._perfora(z.b, z.x, dyT);
    // 2) ¡EXPLOSIÓN! estruendo + astillas + humo + destello + trocitos
    _AS_V1.set(z.x, dyT, ASEDIO.facadeZ + 0.10);
    this.ctrl.sfx('boom', 0);
    this.ctrl.sfx('diana', 0.15);
    this.ctrl.fx.flash(_AS_V1, 1.7, 0xffd28a);
    this.ctrl.fx.spark(_AS_V1, 20, 0xd9b06a, 3.6, 1.5);
    this.ctrl.fx.smoke(_AS_V1, 4, true);
    this._splinters(z.x, dyT);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.85, 170);
    // 3) el forajido sale a la CALLE (de cuerpo completo, mirándote)
    this.dianaGrp.visible = false;
    this._outReveal(z);
    // la bola-bomba EXPLOTA: recambio corto
    this._killBall();
    g.rules.message = tx('asedio_diana');
    this.phase = 'reveal';
    this.revealT = ASEDIO.shotWindow;   // v2.107: 1 s — pasados, DISPARA
    this._outCock = false;
    this._msg = '';
    this._msgT = 0;
    // v2.98: ¡PALAS FUERA, UN REVÓLVER EN CADA MANO! (1 disparo cada uno)
    this.ctrl._twoGunApply(true);
  }
  /** v2.99 · TROCITOS que saltan al ROMPERSE la fachada (pool, 14 piezas). */
  _splinters(x, y) {
    let placed = 0;
    for (const d of this._debris) {
      if (d.life > 0) continue;
      d.life = 1.4 + Math.random() * 0.7;
      d.t = 0;
      d.m.visible = true;
      d.m.position.set(
        x + (Math.random() - 0.5) * 0.6,
        Math.max(0.2, y + (Math.random() - 0.5) * 0.6),
        ASEDIO.facadeZ + 0.10);
      d.v.set((Math.random() - 0.5) * 2.8, 2.0 + Math.random() * 2.6,
        1.3 + Math.random() * 2.4);
      d.w.set(3 + Math.random() * 9, 0, 2 + Math.random() * 8);
      if (++placed >= 14) break;
    }
  }
  /** ¡DARDO AL CORAZÓN! El forajido se desploma: uno menos. */
  _killOutlaw() {
    const g = this.game;
    this.ctrl.sfx('diana', 0);
    this.ctrl.sfx('disparo', 0.1);
    _AS_V1.copy(this.heart.position);
    this.ctrl.fx.flash(_AS_V1, 2.0, 0xff6a4a);
    this.ctrl.fx.spark(_AS_V1, 18, 0xd81f2a, 3.2, 1.3);
    this.ctrl.fx.smoke(_AS_V1, 2, false);
    this.heart.visible = false;
    const ts = this.ctrl.texs || {};
    const tex = ts['defeated'] || ts['panic'];
    if (tex) {
      this.outlaw.material.map = tex;
      this.outlaw.material.needsUpdate = true;
      const img = tex.image;
      if (img && img.width && img.height) {
        this._outAR = img.width / img.height;
        this.outlaw.scale.set(this._outH * this._outAR, this._outH, 1);
      }
    }
    this._outlawGunRemove();       // v2.99: SU revólver cae con él
    this._outFocus = null;         // v2.103: cancela el fundido a mitad
    this._outSt = 'down';
    this._outAnimT = 0;
    this.kills++;
    this.killsWave++;
    this.ctrl._puntosAdd(100, this.heart.position);   // v2.119: forajido abatido
    this._msg = tx('asedio_muere',
      { n: this.killsWave, m: this._waveNeed() });
    this._msgT = 2.2;
    g.rules.message = this._msg;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 180);
    this._killBall();
    this.ctrl._twoGunApply(false);   // v2.98: palas de vuelta
    this.phase = 'duck';
    this.duckT = 1.7;
    this.duckKind = 'kill';
  }
  /** v2.107 · PASÓ EL 1 s: el forajido DISPARA desde SU revólver (SANGRE
   *  EN LA PANTALLA DEL VISOR — salpicadón fijo + gotas que escurran — y
   *  manchones que se acumulan) y se TAPA de nuevo.
   *  v2.106 · EL HUMO SALE DE SU PISTOLA (bocanada baja y densa en la boca
   *  del cañón), la bala se VE volar hasta tu cara, vibran LOS DOS mandos
   *  y suena un GRITO. */
  _punish() {
    const g = this.game;
    // fogonazo desde la BOCA de SU revólver (o desde su pecho a falta de GLB)
    let mp = null;
    if (this._outlawGun && this._outlawGun.muzzle) {
      try {
        this._outlawGun.art.updateWorldMatrix(true, false);
        mp = this._outlawGun.art.localToWorld(
          this._outlawGun.muzzle.clone());
      } catch (e) { mp = null; }
    }
    if (!mp && this._outlawGun && this._outlawGun.grp) {
      try {   // v2.106: respaldo EXACTO — la posición REAL del revólver
        mp = this._outlawGun.grp.getWorldPosition(new THREE.Vector3());
        mp.y += 0.05;
      } catch (e) { mp = null; }
    }
    if (!mp) {
      const zx = this._zona ? this._zona.x : 0;
      mp = _AS_V1.set(zx + 0.16, ASEDIO.gunY + 0.05, ASEDIO.outZ + 0.2);
    }
    this.ctrl.fx.flash(mp, 0.6, 0xffd98a);        // fogonazo contenido
    this.ctrl.fx.smokeGun(mp, 9);                 // v2.106: HUMO DE PISTOLA
    this.ctrl.sfx('disparo', 0.3);
    // v2.103/106 · BALA VISIBLE hacia tu cara (más grande y un pelín más
    // lenta para que se la vea venir): la sangre, el GRITO y el tirón de
    // LOS DOS MANDOS llegan CUANDO LA BALA LLEGA.
    const self = this;
    this._balaVuela(mp, function () {
      // v2.107 · SANGRE EN LA PANTALLA DEL VISOR: salpicadón FIJO (imagen
      // sin seguimiento del mundo) + gotas que ESCURREN + manchones que
      // se acumulan con las heridas de la etapa.
      self.ctrl._sangreTrigger();
      self.ctrl._manchasTrigger(4 + Math.min(6, self.ctrl._heridas), true);
      if (g.renderer.xr.isPresenting) {
        g.haptic(0, 0.9, 220);
        g.haptic(1, 0.9, 220);
      }
      self.ctrl.sfx('grito', 0);                  // v2.106: ¡AAAH!
    });
    this.ctrl._heridas++;
    try {
      localStorage.setItem(this.ctrl.storageKey('asedio_heridas'),
        String(this.ctrl._heridas));
    } catch (e) { /* */ }
    this._msg = tx('asedio_te_da');
    this._msgT = 2.4;
    g.rules.message = this._msg;
    this._outFocus = null;   // v2.103: cancela el fundido a mitad
    this.heart.visible = false;
    this._outlawGunRemove();
    this._outSt = 'duck';
    this._outAnimT = 0;
    this._killBall();
    this.ctrl._twoGunApply(false);   // v2.98: palas de vuelta
    this.phase = 'duck';
    this.duckT = 1.15;
    this.duckKind = 'punish';
  }
  /** v2.99 · Fin de la pausa de bajas: siguiente forajido, OLEADA NUEVA
   *  (fundido a negro + cartel + casas rehechas) o victoria si la 3ª
   *  agotó su tiempo limpia.
   *  v2.106 · EL CUPO YA NO CORTA LA OLEADA: alcanzadas las bajas de la
   *  oleada SIGUEN saliendo forajidos hasta agotar los 2 minutos (el
   *  cambio de oleada/victoria manda SOLO el reloj — petición del artista:
   *  «en la oleada 3 antes de terminar el tiempo me termina la partida»). */
  _duckEnd() {
    const g = this.game;
    // siguiente forajido (la zona usada quedó AGUJEREADA: no se reutiliza)
    this._zona = null;
    this._spawnTarget();
    // v2.102: si _spawnTarget no encontró NINGÚN escondite ya puso phase
    // 'fail' — no pisarla con 'play' (la oleada se quedaba CIEGA: sin diana,
    // sin forajidos y el HUD clavado para siempre)
    if (this.phase === 'fail') return;
    this._respawnT = 0.35;     // la bomba llega CASI al instante
    this._dead = true;
    this.phase = 'play';
  }
  /** v2.99 · OLEADA NUEVA: cartel (5 s en pausa, con su música) y al
   *  salir — fachadas REHECHAS (sin boquetes), zonas de nuevo, reloj a 2 min. */
  _nextWave() {
    const g = this.game;
    const nw = this.wave + 1;
    this.wave = nw;
    this.killsWave = 0;
    this.time = ASEDIO.waveTime;
    this._alarmOn = false;
    this._zona = null;
    this.dianaGrp.visible = false;
    this.heart.visible = false;
    this._parkBall();
    this._starHide();          // v2.105: la estrella no cruza oleadas
    this.ctrl._puntosAdd(200, null);   // v2.119: oleada superada (+200)
    this._showBanner(nw, function () {
      this._spawnTarget();
      this._serveBall();
      this.phase = 'play';
      this.game.rules.message = tx('asedio_oleada',
        { n: this.wave, m: this._waveNeed() });
      this._msg = '';
      this._msgT = 0;
    }, function () {
      // v2.106: las casas nuevas se levantan EN NEGRO (invisible al jugador)
      this._resetEdificios();
    });
  }
  /** ¡SE ACABÓ EL TIEMPO DE LA 3ª OLEADA! ETAPA SUPERADA. */
  _win() {
    const g = this.game;
    this.phase = 'win';
    this._outFocus = null;   // v2.103: fundido cancelado
    if (this.outFadeNegro) this.outFadeNegro.visible = false;
    this._fadeHide();          // v2.106: sin fundido ni cinemática pendiente
    this._resultT = 5.2;
    this.heart.visible = false;
    this.dianaGrp.visible = false;
    this._starHide();          // v2.105
    this.ctrl._puntosAdd(300, null);   // v2.119: asedio superado (+300)
    this.ctrl.fx.laserVisible(false);
    this.ctrl.sfx('diana', 0);
    this.ctrl.sfx('whistle', 0);
    g.rules.message = tx('asedio_gana');
    this._hud.set(this.time, '¡LIMPIO! 12/12', tx('asedio_gana'), undefined,
      { n: 0, m: this._waveNeed() }, this.ctrl.puntos);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 220);
    // heridas se limpian al superar la etapa
    this.ctrl._heridas = 0;
    try {
      localStorage.removeItem(this.ctrl.storageKey('asedio_heridas'));
    } catch (e) { /* */ }
  }
  /** v2.106 · SIN TIEMPO (o sin escondites): SECUENCIA de DERROTA —
   *  Forajido_lauging riéndose de ti mientras el escenario se FUNDE A
   *  NEGRO, y sobre el negro aparece Forajido_victory con la RISA del
   *  pueblo (risas_pueblo.mp3). Luego, vuelta a la sala. */
  _fail() {
    const g = this.game;
    this.phase = 'fail';
    this._outFocus = null;   // v2.103: fundido cancelado
    if (this.outFadeNegro) this.outFadeNegro.visible = false;
    this._resultT = 6.4;       // v2.106: la cinemática respira (risa incluida)
    this.heart.visible = false;
    this.dianaGrp.visible = false;
    this._starHide();          // v2.105
    this.ctrl.fx.laserVisible(false);
    this._derrotaCine();       // v2.106: risa → negro → victoria + risas
    g.rules.message = tx('asedio_falla');
    this._hud.set(0, '', tx('asedio_falla'), undefined, null, this.ctrl.puntos);
  }
  /** v2.106 · CINEMÁTICA de DERROTA: Forajido_lauging entra riéndose,
   *  el escenario se desvanece a NEGRO detras de él, se cambia a
   *  Forajido_victory y suena risas_pueblo.mp3. (las poses ya viven en
   *  ctrl.texs: laughing/victory — mismo arte del artista). */
  _derrotaCine() {
    const g = this.game;
    if (!this.derrotaImg) return;
    const ts = this.ctrl.texs || {};
    const texL = ts['laughing'] || null;
    if (texL) {
      this.derrotaImg.material.map = texL;
      this.derrotaImg.material.needsUpdate = true;
      const img = texL.image;
      if (img && img.width && img.height) {
        const ar = img.width / img.height;
        this.derrotaImg.scale.set(2.35 * ar, 2.35, 1);
      }
      this.derrotaImg.material.opacity = 0;
      this.derrotaImg.visible = true;
    }
    if (this.fadeNegro) {
      this.fadeNegro.material.opacity = 0;
      this.fadeNegro.visible = true;
    }
    this._derrota = { fase: 'risa', t: 0 };
  }
  /** v2.106 · Frame a frame de la cinemática (lo llama fxStep).
   *  SOLO en fase 'fail' (en 'banner' el fundido manda el cartel). */
  _derrotaStep(dt) {
    if (this.phase !== 'fail') return;
    const d = this._derrota;
    if (!d) return;
    d.t += dt;
    if (d.fase === 'risa') {
      // 0-0.45s: el forajido ENTRA riéndose · 0.25-1.5s: todo a NEGRO
      if (this.derrotaImg.visible) {
        this.derrotaImg.material.opacity = Math.min(1, d.t / 0.45);
      }
      if (this.fadeNegro) {
        this.fadeNegro.material.opacity = clamp((d.t - 0.25) / 1.25, 0, 1);
      }
      if (d.t >= 1.5) {
        d.fase = 'victoria'; d.t = 0;
        const ts = this.ctrl.texs || {};
        const texV = ts['victory'] || null;
        if (texV) {
          this.derrotaImg.material.map = texV;
          this.derrotaImg.material.needsUpdate = true;
          const img = texV.image;
          if (img && img.width && img.height) {
            const ar = img.width / img.height;
            this.derrotaImg.scale.set(2.35 * ar, 2.35, 1);
          }
          this.derrotaImg.material.opacity = 0;
        } else {
          this.derrotaImg.visible = false;
        }
        this.ctrl._playRisaPueblo(0.9);   // ¡RISA del pueblo en la oscuridad!
      }
    } else if (d.fase === 'victoria') {
      if (this.derrotaImg.visible) {
        this.derrotaImg.material.opacity = Math.min(1, d.t / 1.1);
      }
      if (this.fadeNegro) this.fadeNegro.material.opacity = 1;
    }
  }
  /** Cierre: StageClear (si ganó) + vuelta a la SALA. */
  _finish() {
    const won = this.phase === 'win';
    this.phase = 'idle';
    this._fadeHide();          // v2.106: apaga fundido y cinemática
    this.ctrl._endAsedio(won);
    this.done = true;
  }

  dispose() {
    const g = this.game;
    this._fadeHide();                     // v2.106: fundido + derrota fuera
    if (this.fadeNegro && this.fadeNegro.parent) {
      this.fadeNegro.parent.remove(this.fadeNegro);
      this.fadeNegro.material.dispose();
      this.fadeNegro.geometry.dispose();
      this.fadeNegro = null;
    }
    if (this.derrotaImg && this.derrotaImg.parent) {
      this.derrotaImg.parent.remove(this.derrotaImg);
      this.derrotaImg.material.dispose();
      this.derrotaImg = null;
    }
    this._outlawGunRemove();              // v2.99: adiós al revólver del forajido
    this.ctrl._starGunApply(false);       // v2.118: la pistola de la estrella fuera
    this.ctrl._twoGunApply(false);        // v2.98: adiós revólveres
    this.ctrl._twoPaddles(false);         // v2.98: pala sólo en SU mano
    g.ball.ignoreTable = false;           // v2.98: la mesa del núcleo vuelve
    g.ball.ignoreWalls = false;           // v2.101: los muros de la SALA vuelven
    g.ball.dragMul = 1;                   // v2.102: aire NORMAL fuera del asedio
    this._tntRemove();                    // v2.101: el cartucho escondido fuera
    this._starDispose();                  // v2.105: fuera la estrella
    if (g.tableGroup) g.tableGroup.visible = true;  // la mesa vuelve
    if (this.fuse && g.ballMesh) {
      g.ballMesh.remove(this.fuse);
      this._disposeTree(this.fuse);
    }
    this.fuse = null;
    if (this._ballSaved && g.ballMesh && g.ballMesh.material) {
      try {
        if (this._ballSaved.col !== null) {
          g.ballMesh.material.color.setHex(this._ballSaved.col);
        }
        if (this._ballSaved.em !== null && g.ballMesh.material.emissive) {
          g.ballMesh.material.emissive.setHex(this._ballSaved.em);
        }
        if (g.ballMesh.material.emissiveIntensity !== undefined) {
          g.ballMesh.material.emissiveIntensity = this._ballSaved.ei;
        }
      } catch (e) { /* */ }
      this._ballSaved = null;
    }
    if (this.group) {
      g.rig.remove(this.group);
      this._disposeTree(this.group);
      this.group = null;
    }
    if (this._hud) {
      // v2.120: cierre completo (textura/material/geometría incluidos)
      if (typeof this._hud.dispose === 'function') this._hud.dispose();
      else {
        this._hud.hide();
        if (this._hud.group) { g.rig.remove(this._hud.group); }
      }
    }
    this.ctrl.fx.laserVisible(false);
    g.champDecorHidden = false;  // los troqueles de sala pueden volver
    // los MANCHONES permanentes se retiran al cerrar la etapa
    if (this.ctrl._manchas) this.ctrl._manchas.stop();
    this.done = true;
  }
  /** Dispone SOLO lo propio: las texturas compartidas de ctrl se respetan. */
  _disposeTree(o) {
    const own = this._ownTex;
    o.traverse((n) => {
      if (n.geometry) n.geometry.dispose();
      if (n.material) {
        const mats = Array.isArray(n.material) ? n.material : [n.material];
        for (const mm of mats) {
          if (mm.map && own && own.has(mm.map)) mm.map.dispose();
          mm.dispose();
        }
      }
    });
  }
}

/* ============================================================================
 *  v2.94 · SANGRE MANCHON — salpicaduras FIJAS en el visor (etapa 2 ASEDIO).
 *  ---------------------------------------------------------------------
 *  Cuando el forajido nos DISPARA en el asedio, la pantalla se llena de
 *  MANCHONES DE SANGRE fijos (no escurren: salpicadura secándose) que
 *  DESAPARECEN PROGRESIVAMENTE en 5 s. Cada impacto ACUMULA más manchones
 *  (cada duelo estás más herido) — mientras la partida SIGUE. Pool
 *  pre-creado (14 salpicaduras v2.107), textura de canvas única, cero
 *  asignaciones por frame; grupo bloqueado a la CABEZA con la pose de la
 *  cámara XR del frame (visorPose — fijo en la pantalla del visor).
 *  renderOrder 958 (bajo la sangre que escurre y el menú de pausa 990).
 *  ============================================================================ */
class SangreManchon {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.group = null;
    this.built = false;
    this.spots = [];          // { m, t, life, alive }
    this.tex = null;
  }
  static get DUR() { return 5.0; }        // s («desaparece en 5 segundos»)
  static get Z_FACE() { return -0.42; }   // m delante del rostro
  _build() {
    if (this.built) return;
    const g = this.game;
    // textura: salpicadura irregular con gotitas alrededor y reguero corto
    const cv = oesteCanvas(256, 256);
    const c = cv.getContext('2d');
    const blob = (x, y, r, a) => {
      const rg = c.createRadialGradient(x, y, r * 0.1, x, y, r);
      rg.addColorStop(0, 'rgba(112,10,14,' + a + ')');
      rg.addColorStop(0.7, 'rgba(96,8,12,' + a * 0.8 + ')');
      rg.addColorStop(1, 'rgba(96,8,12,0)');
      c.fillStyle = rg;
      c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    };
    blob(128, 120, 62, 0.95); blob(96, 140, 34, 0.9); blob(160, 138, 30, 0.85);
    blob(120, 88, 26, 0.8); blob(150, 168, 24, 0.7);
    // gotitas satélite
    for (let i = 0; i < 14; i++) {
      const a = Math.random() * Math.PI * 2;
      const r = 66 + Math.random() * 52;
      blob(128 + Math.cos(a) * r, 122 + Math.sin(a) * r * 0.8,
        3 + Math.random() * 7, 0.55 + Math.random() * 0.3);
    }
    // reguero corto hacia abajo
    c.fillStyle = 'rgba(104,9,13,0.75)';
    c.fillRect(120, 150, 13, 74);
    blob(126, 226, 10, 0.8);
    const tex = new THREE.CanvasTexture(cv);
    this.tex = tex;
    // v2.107: UN material por manchón — cada uno desvanece POR SÍ (antes
    // compartían material y la opacidad de la última vencía a las demás)
    this.group = new THREE.Group();
    this.group.visible = false;
    this.group.renderOrder = 958;
    const geo = new THREE.PlaneGeometry(1, 1);
    // v2.107: pool 10 → 14 manchones (más sangre acumulada en la etapa)
    for (let i = 0; i < 14; i++) {
      const m = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({
        map: tex, transparent: true, opacity: 0.9, depthTest: false,
        depthWrite: false, fog: false, side: THREE.DoubleSide,
      }));
      m.renderOrder = 958;
      m.visible = false;
      m.position.z = SangreManchon.Z_FACE + (i % 3) * 0.004;
      this.group.add(m);
      this.spots.push({ m, t: 0, life: 0, persist: false });
    }
    g.rig.add(this.group);
    this.built = true;
  }
  /** n = cuántos manchones NUEVOS (se acumulan); persist = NO se borran
   *  (v2.95: permanecen TODA la etapa del asedio, opacidad suave). */
  trigger(n, persist) {
    this._build();
    let placed = 0;
    for (const s of this.spots) {
      if (s.life > 0) continue;
      s.persist = !!persist;
      s.life = persist ? 1e9 : SangreManchon.DUR * (0.85 + Math.random() * 0.3);
      s.t = 0;
      s.m.visible = true;
      s.m.position.x = (Math.random() * 2 - 1) * 0.46;
      s.m.position.y = (Math.random() * 2 - 1) * 0.30 + 0.02;
      const sz = 0.08 + Math.random() * 0.16;   // v2.107: manchones mayores
      s.m.scale.set(sz, sz * (0.85 + Math.random() * 0.4), 1);
      s.m.rotation.z = Math.random() * Math.PI * 2;
      s.m.material.opacity = s.persist ? 0.52 : 0.9;   // v2.107: pose propia
      if (++placed >= n) break;
    }
    this.group.visible = true;
    // pose de cabeza YA (cámara XR del frame: imagen FIJA en el visor)
    visorPose(this.game, this.group);
  }
  stop() {
    if (!this.built) return;
    this.group.visible = false;
    for (const s of this.spots) { s.life = 0; s.m.visible = false; }
  }
  update(dt) {
    if (!this.built || !this.group.visible) return;
    // pose del visor EN CURSO (cámara XR: fija en la pantalla)
    visorPose(this.game, this.group);
    let vivos = 0;
    for (const s of this.spots) {
      if (s.life <= 0) continue;
      s.t += dt;
      const f = 1 - s.t / s.life;
      if (f <= 0) { s.life = 0; s.m.visible = false; continue; }
      s.m.material.opacity = s.persist ? 0.52
        : 0.9 * Math.min(1, f * 1.6);
      vivos++;
    }
    if (!vivos) this.group.visible = false;
  }
}

/* ============================================================================
 *  v2.110 · EL PARALLAX CON ARTE REAL: P1 = las dos panorámicas p1_*.png
 *  COSIDAS en un horizonte continuo (las únicas que van una pegada a la
 *  siguiente); P2/P3/P4 = piezas sueltas del artista (p2_/p3_/p4_*.png)
 *  en CINTAS aleatorias por plano y lado — textura, escala, profundidad y
 *  suelo aleatorios, reciclado con dotación nueva al salir del cinturón
 *  (spawn «cada cierto tiempo» = la propia cinta). Velocidades
 *  0,05× / 0,15× / 0,40× / 1,00× intactas.
 *  v2.109 · ETAPA 4 — «ASALTO AL TREN» · EL VAGÓN DE MERCANCÍAS (interior).
 *  ---------------------------------------------------------------------
 *  La escena SE CIERRA sobre el jugador: la mesa viaja DENTRO de un vagón
 *  de mercancías (suelo, techo, frontal con cajas pintadas, trasera con
 *  puerta — arte del artista en assets/room/vagon/). Las paredes laterales
 *  traen VENTANAS con marco de hierro (recorte ALFA medido píxel a píxel
 *  sobre el arte) y fuera de ellas corre el desierto en 4 PLANOS de
 *  PARALLAX (regla del artista, multiplicadores sobre el plano cercano):
 *    P1 montañas 0,05× · P2 colinas/estructuras 0,15× ·
 *    P3 postes/terreno 0,40× · P4 arbustos/rocas 1,00×
 *  Las ventanas son la ÚNICA referencia visual de movimiento: dentro del
 *  vagón no tiembla nada. El trayecto son 3 PARADAS de 2 minutos máximo:
 *  el tren nace DETENIDO en la estación 1, silba y arranca; cada parada
 *  trae su OLEADA de cajas fuertes (repisas → raíles → compuertas); al
 *  completarla el tren FRENA hasta el andén siguiente, espera y vuelve a
 *  arrancar. El SILBATO anuncia TÚNELES: las ventanas se apagan y sólo
 *  brillan los candados. Arte por planos: si existen
 *  assets/parallax/plano1..4.png se usan; si no, siluetas procedurales.
 *  ============================================================================ */
class TrenAction {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.phase = 'idle';      // intro|run|arrive|stop|win|fail
    this.t = 0;
    this.done = false;
    this.wave = 1;            // parada actual 1..3
    this.ingots = 0;          // v2.111: lingotes acumulados en la parada
    this.time = TREN.time;    // reloj DE LA PARADA (2:00)
    this.v = 0;               // velocidad del tren (m/s)
    this.W = 0;               // distancia recorrida (m, mundo)
    this.meetW = 0;           // W del próximo andén (freno hasta aquí)
    this.stationW = 0;        // W del andén COLOCADO en la escena
    this._stoppedT = 0;
    this._tunnelT = TREN.tunnelFirst;
    this._tunnelPhase = 'none';  // none|in|dur|out
    this._tunnelT2 = 0;
    this._resultT = 0;
    this._respawnT = 0;
    this._dead = false;
    this._floorB = 0;
    this._msg = '';
    this._msgT = 0;
    this._extra = (ball) => this._collide(ball);
    /* v2.111 · EL BOTÍN DEL TREN */
    this.cubos = [];          // registros de la pirámide activa
    this._pirT = 0;           // respawn de la pirámide
    this.ingotes = [];        // lingotes (vuelo + pila)
    /* v2.141 · PILA POR CAJÓN: un contador y una lista de huecos libres
     * POR LADO (el robo devuelve SU hueco — nunca se solapan). */
    this._pileN = [0, 0];     // hueco de pila siguiente [izq, der]
    this._pileFree = [[], []];  // huecos liberados por robo
    this._pileAlt = false;    // alterna IZQUIERDA / DERECHA
    this._lingoteProto = null;
    /* v2.111 · FORAJIDO GALOPANTE */
    this._fjState = 'off';    // off|paso|ida|ventana|herido|fade|fuga
    this._fjT = 0; this._fjZ = 0; this._fjV = 0;
    this._fjSide = 1; this._fjLastSide = 1; this._fjPrevSide = -1;
    this._fjNext = 5.0; this._fjCount = 0;
    this._fjFrame = 0; this._fjFrameT = 0;
    this._fjAtk = false; this._fjW = 1;
    this._gunLast = 0;
    /* v2.119 · INDIO CABALGANTE (grupos de 1-3 con flecha ladrona) */
    this._inds = [];           // jinetes vivos { grp, plane, diana, mat, side,
                               //  z, zAtk, state, t, frame, frameT, fadeMat, w }
    this._indNext = 14.0;      // s hasta el PRÓXIMO grupo
    this._indCount = 0;        // grupos lanzados (tope TREN.indio.total)
    this._indLastSide = 1; this._indPrevSide = -1;
    this._indAny = false;      // ¿algún jinete en pantalla? (pausa al forajido)
    this._flechas = [];        // flechas en vuelo { grp, t, dur, from, to }
    this._indFrame = 0; this._indFrameT = 0;
    this._flechaRobo = [];
    /* v2.111 · MÚSICA DEL VAGÓN (vagon.mp3) — v3.6.3-SDK3: el estado vive
     * en el SDK (createMusic, variante «direct»). */
    this.__musSDKv = null;
    /* v2.112 · VÓRTICE efímero + bote a altura constante */
    this._portalT = 0; this._portalK = 0; this._prevVy = 0;
    /* v2.115 · PELOTAS CADA SEGUNDO (pool multi-bola) */
    this.extras = [];          // { ball, mesh, alive, gastada, gastadaT,
                               //   floorB, prevVy, deadT, events, zc, bomba }
    this._spawnT = 0;          // cadencia del spawner (s)
    /* v2.115 · SUPERPODERES de la mesa rival */
    this._podT = 8;            // s hasta el próximo medallón
    this._pod = null;          // { tipo, x, z, vida, k } activo
    /* v2.115 · TÚNEL del artista */
    this._tunelZ = 0;          // z del grupo del túnel (viaja con el mundo)
  }

  /* ------------------------------ texturas -------------------------------- */
  _ct(cv) {
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }
  _anisoOf() {
    try { return Math.min(8, this.game.renderer.capabilities.getMaxAnisotropy()); }
    catch (e) { return 4; }
  }
  /* CIELO del desierto (degradado cálido + nubes largas). */
  _texSky() {
    const cv = oesteCanvas(512, 256);
    const c = cv.getContext('2d');
    const gr = c.createLinearGradient(0, 0, 0, 256);
    gr.addColorStop(0, '#6fa7d6'); gr.addColorStop(0.55, '#a8c8dd');
    gr.addColorStop(0.8, '#ecd9ae'); gr.addColorStop(1, '#f2d9a8');
    c.fillStyle = gr; c.fillRect(0, 0, 512, 256);
    for (const [x, y, w, a] of [[70, 60, 150, 0.16], [300, 90, 190, 0.13],
      [180, 130, 210, 0.10], [430, 50, 120, 0.14]]) {
      const rg = c.createRadialGradient(x, y, 4, x, y, w / 2);
      rg.addColorStop(0, 'rgba(255,250,240,' + a + ')');
      rg.addColorStop(1, 'rgba(255,250,240,0)');
      c.fillStyle = rg;
      c.beginPath(); c.ellipse(x, y, w / 2, w / 7, 0, 0, Math.PI * 2); c.fill();
    }
    return this._ct(cv);
  }
  /* Los 4 PLANOS del artista (reserva transparente hasta que llegue
   * parallax/plano1..4.png). v2.112: NADA de siluetas pintadas — mientras
   * carga el pano del artista (1 s) sólo se ve el CIELO, jamás mesetas
   * paramétricas. Lienzo 4x4 vacío. */
  _layerCanvas(k) {
    return oesteCanvas(4, 4);
  }
  _texLayer(k) { return this._ct(this._layerCanvas(k)); }
  _texRock() {
    const cv = oesteCanvas(256, 256);
    const c = cv.getContext('2d');
    c.fillStyle = '#241a12'; c.fillRect(0, 0, 256, 256);
    for (let i = 0; i < 60; i++) {
      const a = 0.05 + Math.random() * 0.14;
      c.fillStyle = Math.random() < 0.5 ? 'rgba(10,6,3,' + a + ')' : 'rgba(64,52,44,' + a * 0.7 + ')';
      c.beginPath();
      c.arc(Math.random() * 256, Math.random() * 256, 6 + Math.random() * 26, 0, Math.PI * 2);
      c.fill();
    }
    c.fillStyle = 'rgba(12,8,4,0.55)';
    c.fillRect(38, 0, 12, 256); c.fillRect(206, 0, 12, 256);
    c.fillRect(0, 40, 256, 10);
    return this._ct(cv);
  }

  /* v2.111 · ARENA del suelo del vagón — textura PROCEDURAL (el arte
   * room/vagon/suelo.jpg no convence): arena cálida con grano, piedritas y
   * vadíos de viento, teselable (RepeatWrapping 3×4 sobre el suelo). */
  _texArena() {
    const cv = oesteCanvas(512, 512);
    const c = cv.getContext('2d');
    const gr = c.createLinearGradient(0, 0, 0, 512);
    gr.addColorStop(0, '#d8b475'); gr.addColorStop(1, '#c39a5e');
    c.fillStyle = gr; c.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 2600; i++) {          // grano de arena
      const a = 0.05 + Math.random() * 0.12;
      c.fillStyle = Math.random() < 0.5
        ? 'rgba(255,238,200,' + a + ')'
        : 'rgba(120,88,44,' + a + ')';
      c.fillRect(Math.random() * 512, Math.random() * 512,
        1 + Math.random() * 2, 1 + Math.random() * 2);
    }
    for (let i = 0; i < 26; i++) {            // piedritas
      c.fillStyle = 'rgba(150,116,70,' + (0.22 + Math.random() * 0.3) + ')';
      c.beginPath();
      c.ellipse(Math.random() * 512, Math.random() * 512,
        2 + Math.random() * 5, 1.5 + Math.random() * 3,
        Math.random() * 3, 0, Math.PI * 2);
      c.fill();
    }
    for (let i = 0; i < 9; i++) {             // vadíos suaves del viento
      c.strokeStyle = 'rgba(255,240,205,' + (0.05 + Math.random() * 0.06) + ')';
      c.lineWidth = 6 + Math.random() * 14;
      c.beginPath();
      const y = Math.random() * 512;
      c.moveTo(-20, y);
      c.bezierCurveTo(170, y + (Math.random() - 0.5) * 60,
        340, y + (Math.random() - 0.5) * 60,
        532, y + (Math.random() - 0.5) * 40);
      c.stroke();
    }
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(3, 4);
    t.anisotropy = this._aniso;
    return t;
  }
  /** v2.113 · ARENA EXTERIOR (suelo fuera del vagón): como _texArena pero
   *  ISOTRÓPICA — sin el degradado direccional que, repetido 90 veces,
   *  se veía como tablones de madera — y con base un pelín más clara para
   *  fundirse con el desierto de la panorámica del artista. */
  _texArenaExt(aniso) {
    const cv = oesteCanvas(512, 512);
    const c = cv.getContext('2d');
    c.fillStyle = '#dcae74';
    c.fillRect(0, 0, 512, 512);
    for (let i = 0; i < 2400; i++) {          // grano de arena (puntos suaves)
      const a = 0.05 + Math.random() * 0.12;
      c.fillStyle = Math.random() < 0.5
        ? 'rgba(255,238,200,' + a + ')'
        : 'rgba(120,88,44,' + a + ')';
      const r = 1 + Math.random() * 2;
      c.beginPath();
      c.arc(Math.random() * 512, Math.random() * 512, r, 0, Math.PI * 2);
      c.fill();
    }
    for (let i = 0; i < 46; i++) {            // piedritas
      c.fillStyle = 'rgba(' + (140 + (Math.random() * 60 | 0)) + ',' +
        (110 + (Math.random() * 40 | 0)) + ',80,0.5)';
      c.beginPath();
      c.ellipse(Math.random() * 512, Math.random() * 512,
        2 + Math.random() * 4, 1.4 + Math.random() * 2.6,
        Math.random() * Math.PI, 0, Math.PI * 2);
      c.fill();
    }
    for (let i = 0; i < 16; i++) {            // matas secas
      c.fillStyle = 'rgba(150,140,80,0.16)';
      c.beginPath();
      c.ellipse(Math.random() * 512, Math.random() * 512,
        7 + Math.random() * 9, 3 + Math.random() * 4,
        Math.random() * Math.PI, 0, Math.PI * 2);
      c.fill();
    }
    const t = new THREE.CanvasTexture(cv);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.anisotropy = aniso || 4;
    return t;
  }

  /* -------------------- HORIZONTE COSIDO (P1) + CINTAS DE ELEMENTOS ------ */
  /* v2.110 · Las DOS panorámicas p1_*.png se COSEN punto a punto (una pegada
   * a la siguiente, misma línea de base) en un lienzo que viste el plano P1
   * — es la ÚNICA imagen que forma un horizonte continuo y la que más
   * despacio se mueve (0,05×). Mientras carga (o si falla) sólo se ve el
   * CIELO (reserva transparente, nada de mesetas paramétricas).
   * v2.112 · DOS lecciones duras del banco de pruebas:
   *  1) EL LIENZO CRECE HACIA ABAJO (arte arriba + desierto estirado) para
   *     que el horizonte montañas/desierto caiga EN la ventana (v2.110 lo
   *     dejaba MUY abajo: por la ventana sólo se veía cielo).
   *  2) NO se intercambia tex.image sobre la CanvasTexture vieja: algunos
   *     drivers NO re-suben (se quedaba la reserva de 4×4 transparente y
   *     la ventana en blanco). Se crea una CanvasTexture NUEVA y se
   *     sustituye en el material y en su cinta de scroll (offset incluido). */
  _buildPano(ld, A) {
    const files = TREN.spawn.pano;
    const g = this.game;
    let maxT = 4096;
    try { maxT = Math.min(4096, g.renderer.capabilities.maxTextureSize || 4096); }
    catch (e) { /* reserva 4096 */ }
    const EXT = 190;                       // desierto estirado bajo el arte
    const imgs = [];
    let pend = files.length;
    const done = () => {
      if (pend > 0) return;
      try {
        const w0 = imgs[0].width, h0 = imgs[0].height;
        const per = Math.floor(maxT / imgs.length);      // px por imagen
        const dh = Math.round(h0 * (per / w0));
        const cv = oesteCanvas(maxT, dh + EXT);
        const c = cv.getContext('2d');
        imgs.forEach((im, j) => {
          c.drawImage(im, j * per, 0, per, dh);
          /* v2.112: el desierto del artista alcanza el pie del lienzo */
          c.drawImage(im, 0, h0 - 60, w0, 60, j * per, dh, per, EXT);
        });
        /* v2.112: textura NUEVA por lado (offsets de scroll distintos) */
        (this._panoMats || []).forEach((mat, i) => {
          const old = this._panoScrollers[i] ? this._panoScrollers[i].tex : null;
          const nt = new THREE.CanvasTexture(cv);
          nt.colorSpace = THREE.SRGBColorSpace;
          nt.wrapS = THREE.RepeatWrapping;
          nt.wrapT = THREE.ClampToEdgeWrapping;
          nt.anisotropy = this._aniso;
          if (old) nt.offset.x = old.offset.x;   // deriva ya acumulada
          if (this._panoScrollers[i]) this._panoScrollers[i].tex = nt;
          mat.map = nt;
          mat.needsUpdate = true;
          if (old) old.dispose();
        });
        PX.panoDone = true;
      } catch (e) { /* sin arte: cielo (reserva transparente) */ }
    };
    files.forEach((f, i) => {
      ld.load(A('parallax/' + f), (t) => {
        imgs[i] = t.image;
        pend--; done();
      }, undefined, () => { pend--; done(); });
    });
  }

  /* v2.110 · CINTA DE ELEMENTOS por PLANO y LADO (p2_/p3_/p4_): n piezas
   * repartidas con hueco aleatorio en el cinturón [bandFront, bandBack];
   * viajan de delante (-z) hacia detrás (+z) a la velocidad de su plano
   * (mult) y al salir del cinturón se RECICLAN con textura, escala,
   * profundidad y altura nuevas — spawn aleatorio constante a ambos lados.
   * Las piezas viven en el pase OPACO (alphaTest 0.5): sin orden de
   * transparencias y con el recorte exacto del PNG del artista. */
  _buildPx(ld, A) {
    for (const side of [-1, 1]) {
      TREN.spawn.planes.forEach((P, pi) => {
        const L = TREN.layers[pi + 1];       // P2..P4
        let z = P.bandBack;
        for (let i = 0; i < P.n; i++) {
          z -= P.gapMin + Math.random() * (P.gapMax - P.gapMin);
          const mesh = new THREE.Mesh(PX_GEO);
          mesh.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
          mesh.renderOrder = 3 + pi;
          this.group.add(mesh);
          const it = { mesh, P, L, side, z, h: 1, w: 1, e: null };
          this._pxRandomize(it, ld, A);
          it.z = z;
          mesh.position.z = z;
          this.pxItems.push(it);
        }
      });
    }
  }

  /** Dotación aleatoria de UNA pieza: textura del plano, escala ±22%,
   * profundidad lateral ±jitD (respetando la distancia del plano) y línea
   * de suelo ±jitF (los PNG apoyan los pies en su borde inferior). */
  _pxRandomize(it, ld, A) {
    const P = it.P, L = it.L;
    const f = P.files[(Math.random() * P.files.length) | 0];
    const e = pxMat(P.key, f, ld || this._ld, A || this._A, this._aniso);
    it.e = e;
    it.mesh.material = e.mat;
    const j = 0.8 + Math.random() * 0.44;
    it.h = P.h * j;
    it.w = it.h * (e.aspect || 1);
    it.mesh.scale.set(it.w, it.h, 1);
    it.mesh.position.x = it.side * (L.dist + (Math.random() - 0.5) * 2 * P.jitD);
    const feet = P.feet + (Math.random() - 0.5) * 2 * P.jitF;
    it.mesh.position.y = feet + it.h / 2;
    if (!e.ready) {
      PX.fit.push({ it, e });
      if (PX.fit.length > 90) PX.fit.shift();
    }
  }

  /* --------------------- pared lateral CON VENTANA ------------------------ */
  /* Carga el arte del lateral y RECORTA la ventana (alfa) con las medidas
   * tomadas píxel a píxel sobre el 2395x864 del artista. Mientras carga —
   * o si falla — la pared queda opaca con el paisaje pintado (fallback). */
  _mkSide(A, ld, file, side) {
    const RH = 2.85;
    const url = A('room/vagon/' + file + '.jpg');
    const t0 = ld.load(url);
    t0.colorSpace = THREE.SRGBColorSpace;
    t0.anisotropy = this._aniso;
    // v2.109: CUTOUT con alphaTest — la pared vive en el pase OPACO (escribe
    // depth sólo en sus texels sólidos) y el hueco de la ventana deja VER
    // el parallax y el andén; con transparent+depthWrite el hueco tapaba
    // cielo/capas (lección de la primera pasada).
    const mat = new THREE.MeshStandardMaterial({
      map: t0, roughness: 0.95, metalness: 0.02, alphaTest: 0.5,
    });
    const wall = new THREE.Mesh(new THREE.PlaneGeometry(7.90, RH), mat);
    wall.position.set(side * 3.05, RH / 2, -1.6);
    wall.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
    this.group.add(wall);
    const px = side < 0
      ? { x0: 715, x1: 1545, y0: 150, y1: 505, r: 44 }   // izquierda
      : { x0: 805, x1: 1595, y0: 165, y1: 545, r: 44 };  // derecha
    ld.load(url, (t) => {
      try {
        const img = t.image;
        if (!img || !img.width) return;
        const cv = oesteCanvas(img.width, img.height);
        const c = cv.getContext('2d');
        c.drawImage(img, 0, 0);
        c.globalCompositeOperation = 'destination-out';
        c.beginPath();
        c.moveTo(px.x0 + px.r, px.y0);
        c.arcTo(px.x1, px.y0, px.x1, px.y1, px.r);
        c.arcTo(px.x1, px.y1, px.x0, px.y1, px.r);
        c.arcTo(px.x0, px.y1, px.x0, px.y0, px.r);
        c.arcTo(px.x0, px.y0, px.x1, px.y0, px.r);
        c.closePath(); c.fill();
        const t2 = new THREE.CanvasTexture(cv);
        t2.colorSpace = THREE.SRGBColorSpace;
        t2.anisotropy = this._aniso;
        mat.map = t2;
        mat.alphaTest = 0.5;
        mat.transparent = false;
        mat.needsUpdate = true;
        try { t0.dispose(); } catch (e) { /* */ }
      } catch (e) { /* sin recorte: pared opaca */ }
    });
    return wall;
  }

  /* ------------------------- cartel de andén ------------------------------ */
  _signPaint(name) {
    if (!this._signCv) {
      this._signCv = oesteCanvas(512, 128);
      this._signTex = this._ct(this._signCv);
    }
    const c = this._signCv.getContext('2d');
    c.clearRect(0, 0, 512, 128);
    c.fillStyle = '#2c1d0e'; c.fillRect(0, 0, 512, 128);
    c.strokeStyle = '#c89b4a'; c.lineWidth = 7; c.strokeRect(7, 7, 498, 114);
    c.textAlign = 'center';
    c.fillStyle = '#f6e3b0';
    c.font = 'bold 54px Georgia, serif';
    c.fillText(name, 256, 84);
    this._signTex.needsUpdate = true;
  }
  /* v2.115 · ESTACIÓN DEL ARTISTA por parada: carga PARADA{n}.png (con
   * caché) y SUSTITUYE al andén procedural en cuanto está lista. idx es
   * la PARADA del HUD (1..3); v2.117 · MAPEO CORREGIDO — la parada N
   * muestra SU imagen PARADAn.png (antes un off-by-one: la parada 1
   * mostraba PARADA2, la 2 PARADA3 y la 3 PARADA1).
   * v2.134 · LA SALIDA DEJA DE REPETIR: la estación de SALIDA (idx 0,
   * BRAVOS) usaba PARADA1 — la MISMA imagen que la parada 1 — y el
   * jugador veía el arte dos veces seguidas. Ahora idx 0 carga SU arte
   * PARADA0.png (nuevo, placa «BRAVOS») y las 4 estaciones del trayecto
   * lucen imágenes distintas. Si PARADA0 tarda/carga mal: andén pintado. */
  _signArt(idx) {
    const n = (idx >= 0 && idx <= 3) ? idx : 1;
    if (this._paradaTex[n]) { this._signApply(this._paradaTex[n], n); return; }
    if (this._paradaTry[n]) return;
    this._paradaTry[n] = true;
    try {
      const url = this._A('PARADA' + n + '.png');
      const im = new Image();
      im.onload = () => {
        try {
          /* v2.119 · PARADA sobre LIENZO con HUECOS CERRADOS: el arte trae
           * franjas 100 % transparentes ENTRE zonas opacas (PARADA1: andén
           * arriba y raíles abajo con hueco en medio — «se ve hueca la
           * parte inferior»). Cada franja se RELLENA extendiendo hacia
           * abajo el color del borde opaco de encima (sombreado), así la
           * estación queda SÓLIDA de arriba a abajo y se puede SUBIR sin
           * que se vea el interior vacío. El cielo (sin nada opaco
           * encima) se queda como está. */
          const cv = document.createElement('canvas');
          cv.width = im.width; cv.height = im.height;
          const cx = cv.getContext('2d');
          cx.drawImage(im, 0, 0);
          try {
            const data = cx.getImageData(0, 0, cv.width, cv.height);
            const d = data.data, W = cv.width, H = cv.height;
            const alphaRow = (r) => {
              let mn = 255;
              for (let x = 0; x < W; x++) {
                const a = d[(r * W + x) * 4 + 3];
                if (a < mn) mn = a;
              }
              return mn;
            };
            for (let r = 1; r < H - 1; r++) {
              if (alphaRow(r) >= 25) continue;           // fila con cuerpo
              // ¿franja interior? (opaca por encima Y por debajo)
              let up = -1, dn = -1;
              for (let q = r - 1; q >= 0; q--) {
                if (alphaRow(q) >= 25) { up = q; break; }
              }
              if (up < 0) continue;                      // cielo: no tocar
              for (let q = r + 1; q < H; q++) {
                if (alphaRow(q) >= 25) { dn = q; break; }
              }
              if (dn < 0) continue;                      // suelo abierto: no
              const depth = (r - up) / Math.max(1, dn - up);
              for (let x = 0; x < W; x++) {
                const i = (r * W + x) * 4;
                if (d[i + 3] >= 25) continue;
                // busca el píxel opaco más cercano ARRIBA en esta columna
                let su = -1;
                for (let q = up; q >= 0; q--) {
                  if (d[(q * W + x) * 4 + 3] >= 25) { su = q; break; }
                }
                if (su < 0) continue;
                const j = (su * W + x) * 4;
                const sh = 1 - depth * 0.45;             // sombreado del hueco
                d[i] = d[j] * sh;
                d[i + 1] = d[j + 1] * sh;
                d[i + 2] = d[j + 2] * sh;
                d[i + 3] = 255;
              }
            }
            cx.putImageData(data, 0, 0);
          } catch (e0) { /* sin píxeles: textura tal cual */ }
          const t = new THREE.CanvasTexture(cv);
          t.colorSpace = THREE.SRGBColorSpace;
          t.anisotropy = this._aniso;
          this._paradaTex[n] = t;
          this._signApply(t, n);
        } catch (e) { /* fallback: andén pintado */ }
      };
      im.onerror = () => { /* fallback: andén pintado */ };
      im.src = url;
    } catch (e) { /* */ }
  }
  _signApply(t, n) {
    if (!this.estArt || !this.estArt.length) return;
    const ar = t.image ? t.image.width / t.image.height : 2;
    const h = 4.2, w = h * ar;
    /* v2.118 · cada PARADA se cota a SU altura (TREN.estacionY): la base
     * del arte (raíles/andén) asiente en la arena — antes todas a 1,75 y
     * PARADA1 flotaba con hueco bajo el edificio. */
    const yArt = (TREN.estacionY && TREN.estacionY[n]) || 1.75;
    for (const m of this.estArt) {
      m.material.map = t;
      m.material.needsUpdate = true;
      m.scale.set(w / 8.4, h / 4.2, 1);
      m.position.y = yArt;
      m.visible = true;
    }
    for (const p of this._stationParts) p.visible = false;   // fuera andén viejo
  }

  /* ------------------------------- escena --------------------------------- */
  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;
    this.group = new THREE.Group();
    this.group.visible = false;
    g.rig.add(this.group);
    this._aniso = this._anisoOf();
    const A = (p) => new URL('./assets/' + p, import.meta.url).href;
    this._A = A;        // v2.115: los métodos de clase también cargan assets
    const ld = new THREE.TextureLoader();

    /* ==== EL VAGÓN (6 planos con las medidas de la sala núcleo) ==== */
    const RH = 2.85, RW = 6.10, RD = 7.90, zC = -1.6;
    const plainTex = (url) => {
      const t = ld.load(url);
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = this._aniso;
      return t;
    };
    const boxMat = (tex) => new THREE.MeshStandardMaterial({
      map: tex, roughness: 0.95, metalness: 0.02,
    });
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(RW, RD),
      boxMat(plainTex(A('room/vagon/suelo.jpg'))));   // v2.140: TARIMA del dueño (mapeo 1:1)
    floor.rotation.x = -Math.PI / 2;
    floor.position.set(0, 0, zC);
    this.group.add(floor);
    const ceil = new THREE.Mesh(new THREE.PlaneGeometry(RW, RD),
      boxMat(plainTex(A('room/vagon/techo.jpg'))));
    ceil.rotation.x = Math.PI / 2;
    ceil.position.set(0, RH, zC);
    this.group.add(ceil);
    const front = new THREE.Mesh(new THREE.PlaneGeometry(RW, RH),
      boxMat(plainTex(A('room/vagon/frente.jpg'))));
    front.position.set(0, RH / 2, -5.55);
    this.group.add(front);
    const back = new THREE.Mesh(new THREE.PlaneGeometry(RW, RH),
      boxMat(plainTex(A('room/vagon/fondo.jpg'))));
    back.rotation.y = Math.PI;
    back.position.set(0, RH / 2, 2.35);
    this.group.add(back);
    this._mkSide(A, ld, 'izquierda', -1);
    this._mkSide(A, ld, 'derecha', +1);

    /* ==== PARALLAX: cielo + 4 planos a CADA ventana ====
     * Cada plano se centra en el CONO visible por su ventana desde la
     * posición de juego (ojo ~1,6 m) y su horizonte cae donde toca.
     * Los lienzos se generan UNA vez y se comparten entre lados. */
    this.scrollers = [];   // { tex, mPerRep, mult, sign }
    this._panoMats = []; this._panoScrollers = [];   // v2.112: P1 (panorámica)
    this._A = A; this._ld = ld;
    this._layerCanvases = [0, 1, 2, 3].map((k) => this._layerCanvas(k));
    const skyCan = this._texSky().image;
    for (const side of [-1, 1]) {
      // sentido del scroll: el mundo pasa de DELANTE (-z) a DETRÁS (+z)
      const scrollSign = side < 0 ? 1 : -1;
      const skyT = new THREE.CanvasTexture(skyCan);
      skyT.colorSpace = THREE.SRGBColorSpace;
      skyT.wrapS = THREE.RepeatWrapping;
      skyT.repeat.set(2, 1);
      // v2.111: cielo AMPLIADO (400×180 m) — ningún rayo que entre por las
      // ventanas puede escaparse por encima/debajo: fuera, manchones negros.
      const sky = new THREE.Mesh(new THREE.PlaneGeometry(400, 180),
        new THREE.MeshBasicMaterial({ map: skyT, fog: false, depthWrite: false }));
      sky.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
      sky.position.set(side * 205, 7, -156);
      sky.renderOrder = 1;
      this.group.add(sky);
      this.scrollers.push({ tex: skyT, mPerRep: 400 / 2, mult: TREN.cloudMult, sign: scrollSign });
      TREN.layers.forEach((L, k) => {
        /* v2.112 · SÓLO P1 lleva MALLA: la panorámica cosida del artista.
         * P2-P4 son cintas de ELEMENTOS (sin lienzo de terreno: el suelo
         * del desierto lo pinta la propia panorámica). */
        if (k > 0) return;
        const tex = new THREE.CanvasTexture(this._layerCanvases[k]);
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.wrapS = THREE.RepeatWrapping;
        tex.wrapT = THREE.ClampToEdgeWrapping;
        tex.repeat.set(L.rep, 1);
        tex.anisotropy = this._aniso;
        /* v2.111 · ANTI-MANCHÓN NEGRO: P1 OPACO con alphaTest 0.5 —
         * recorte exacto en el pase opaco, sin transparencias. */
        const matL = new THREE.MeshBasicMaterial({ map: tex, alphaTest: 0.5, fog: false });
        const m = new THREE.Mesh(new THREE.PlaneGeometry(L.w, L.h), matL);
        m.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
        m.position.set(side * L.dist, L.cy, L.cz);
        m.renderOrder = 2 + k;
        this.group.add(m);
        const sc = { tex, mPerRep: L.w / L.rep, mult: L.mult, sign: scrollSign };
        this.scrollers.push(sc);
        // v2.112: materiales/cintas del P1 para el vestido con la panorámica
        if (k === 0) {
          this._panoMats = this._panoMats || [];
          this._panoScrollers = this._panoScrollers || [];
          this._panoMats.push(matL);
          this._panoScrollers.push(sc);
        }
      });
    }
    /* v2.110 · ARTE REAL DEL PARALLAX: P1 horizonte continuo + cintas de
     * ELEMENTOS aleatorios (p2/p3/p4) a AMBOS lados del tren. */
    this.pxItems = [];
    this._buildPano(ld, A);
    this._buildPx(ld, A);

    /* ==== v2.113 · SUELO DE ARENA EXTERIOR — el desierto PISA la ventana ====
     * Hasta ahora fuera sólo había cielo, panorámica y piezas: bajo el
     * horizonte no había NADA (se veía el vacío). Dos planos de arena a
     * cada lado, DESPLAZÁNDOSE con el mundo (offset.y con la marcha) como
     * el resto del parallax. Nacen bajo la pared (x=±2,6) y corren hasta
     * 66 m — la panorámica p1 (a 140 m) sigue pintando el horizonte.
     * · fog:false — la NIEBLA del núcleo (Fog 0x0b0e11, 9→18 m) teñía de
     *   NEGRO la arena a 10+ m (el arte del artista va con fog:false);
     * · textura ISOTRÓPICA (sin degradado direccional: con repeat alto el
     *   degradado se veía como tablones). */
    this._gndTex = this._texArenaExt(this._aniso);
    this._gndTex.repeat.set(24, 90);           // 64×240 m → celda ~2,7 m
    for (const side of [-1, 1]) {
      const gnd = new THREE.Mesh(new THREE.PlaneGeometry(64, 240),
        new THREE.MeshBasicMaterial({ map: this._gndTex, fog: false }));
      gnd.rotation.x = -Math.PI / 2;
      gnd.position.set(side * 34.8, -0.35, -1.6);
      gnd.renderOrder = 1;                     // bajo el cielo(1)/P1(2): decide el depth
      this.group.add(gnd);
    }

    /* ==== TÚNEL: roca que apaga las ventanas (fundido) ==== */
    this.texRock = this._texRock();
    this.tunnelMats = [];
    this.tunnel = new THREE.Group();
    for (const side of [-1, 1]) {
      const mat = new THREE.MeshBasicMaterial({
        map: this.texRock, transparent: true, opacity: 0,
        fog: false, depthWrite: false, side: THREE.DoubleSide,
      });
      mat.renderOrder = 9;
      const m = new THREE.Mesh(new THREE.PlaneGeometry(10, 5), mat);
      m.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
      m.position.set(side * 5.2, 1.9, -1.45);
      this.tunnel.add(m);
      this.tunnelMats.push(mat);
    }
    this.group.add(this.tunnel);

    /* ==== ESTACIÓN: andén a ambos lados (se alinea al frenar) ====
     * Materiales CLAROS con brillo propio: fuera del vagón no hay luces
     * que lo bañen y sin el emisivo se veía negro por la ventana. */
    this.station = new THREE.Group();
    // v2.112: el cartel se PINTA YA — si no, su material nace SIN mapa y el
    // plano 2,5×0,62 se ve BLANCO tapando la ventana hasta la 1ª parada.
    this._signPaint(TREN.stationNames[this.wave] || 'BRAVOS');
    this._stationParts = [];     // v2.115: piezas procedurales (fuera si hay arte)
    const platM = new THREE.MeshStandardMaterial({
      color: 0x8a6234, roughness: 0.9, emissive: 0x241608, emissiveIntensity: 0.55,
    });
    const darkM = new THREE.MeshStandardMaterial({
      color: 0x6b4a26, roughness: 0.9, emissive: 0x1a1008, emissiveIntensity: 0.5,
    });
    const roofM = new THREE.MeshStandardMaterial({
      color: 0x54452e, roughness: 0.95, emissive: 0x181208, emissiveIntensity: 0.5,
    });
    for (const side of [-1, 1]) {
      const s = side;
      const plat = new THREE.Mesh(new THREE.BoxGeometry(2.6, 1.25, 30), platM);
      plat.position.set(s * TREN.stationX, -0.72, -1.4);
      this.station.add(plat);
      this._stationParts.push(plat);
      const edge = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.1, 30), darkM);
      edge.position.set(s * (TREN.stationX - 1.2), -0.06, -1.4);
      this.station.add(edge);
      this._stationParts.push(edge);
      for (let i = 0; i < 7; i++) {
        const post = new THREE.Mesh(new THREE.BoxGeometry(0.13, 2.75, 0.13), darkM);
        post.position.set(s * (TREN.stationX + 0.95), 1.27, -11.6 + i * 3.6);
        this.station.add(post);
        this._stationParts.push(post);
      }
      const roof = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.16, 26), roofM);
      roof.position.set(s * (TREN.stationX + 0.4), 2.72, -1.4);
      this.station.add(roof);
      this._stationParts.push(roof);
      const sign = new THREE.Mesh(new THREE.PlaneGeometry(2.5, 0.62),
        new THREE.MeshBasicMaterial({ map: this._signTex, transparent: true }));
      sign.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
      sign.position.set(s * 3.62, 2.18, -1.4);
      this.station.add(sign);
      this._stationParts.push(sign);
    }
    /* ==== v2.115 · ESTACIONES DEL ARTISTA (PARADA1/2/3.png) ====
     * Cada parada tiene SU estación (arte 2:1 con alfa: edificio + andén
     * + raíles) y SUSTITUYE al andén procedural. Fallback: si el arte no
     * carga, el andén de madera pintado sigue en su sitio. */
    this.estArt = [];
    for (const side of [-1, 1]) {
      const ar = new THREE.Mesh(new THREE.PlaneGeometry(8.4, 4.2),
        new THREE.MeshBasicMaterial({
          transparent: true, depthWrite: false, side: THREE.DoubleSide, fog: false,
        }));
      ar.rotation.y = side < 0 ? Math.PI / 2 : -Math.PI / 2;
      ar.position.set(side * (TREN.stationX + 0.3), 1.75, -1.4);
      ar.renderOrder = 3;
      ar.visible = false;
      this.station.add(ar);
      this.estArt.push(ar);
    }
    this._paradaTex = {}; this._paradaTry = {};
    this._signArt(0);
    this.station.visible = false;
    this.group.add(this.station);

    /* ==== v2.111 · LA PIRÁMIDE DE CAJONES (arkanoid del botín) ====
     * Muelle de madera (peana) + cubos del artista con candados. Los
     * MATERIALES viven en caché de módulo (CB) — la etapa se reconstruye
     * al rejugar y las 7 texturas del artista se decodifican una vez. */
    this.piramide = new THREE.Group();
    this.group.add(this.piramide);
    const C = TREN.cubo;
    this._cuboGeo = new THREE.BoxGeometry(C.size, C.size, C.size);
    this._matCubo = [1, 2, 3].map((i) => cuboMat('cubo' + i + '.png', ld, A, this._aniso));
    this._matLingote = [1, 2].map((i) => cuboMat('cubolingote' + i + '.png', ld, A, this._aniso));
    this._matAbierto = [1, 2].map((i) => cuboMat('cubolingoteabierto' + i + '.png', ld, A, this._aniso));
    this.railWood = new THREE.MeshStandardMaterial({
      color: 0x7c5426, roughness: 0.85, metalness: 0.04,
    });
    this.ironMat = new THREE.MeshStandardMaterial({
      color: 0x2e2a26, roughness: 0.5, metalness: 0.7,
    });
    const peana = new THREE.Mesh(
      new THREE.BoxGeometry(C.peanaW, C.peanaH, C.peanaD), this.railWood);
    peana.position.set(0, C.peanaH / 2, C.z);
    this.piramide.add(peana);
    // flejes de hierro del muelle
    for (const fx of [-0.7, 0, 0.7]) {
      const fleje = new THREE.Mesh(
        new THREE.BoxGeometry(0.05, C.peanaH + 0.01, C.peanaD + 0.01), this.ironMat);
      fleje.position.set(fx, C.peanaH / 2, C.z);
      this.piramide.add(fleje);
    }
    this.goldMat = new THREE.MeshStandardMaterial({
      color: 0xd9a93c, roughness: 0.28, metalness: 0.85,
      emissive: 0x6a4a08, emissiveIntensity: 0.5,
    });

    /* ==== v2.111 · PORTAL de la bola (el arte del wizard, portals.webp) ====
     * Anillo GIRATORIO sobre la mesa del jugador, junto a su canto: la bola
     * sale de él con un brinco (éste es el saque del vagón). */
    try {
      const pTex = ld.load(A('portals.webp'));
      pTex.colorSpace = THREE.SRGBColorSpace;
      pTex.anisotropy = this._aniso;
      const D0 = ODIMS();
      // v2.114: el vórtice MÁS PEGADO A LA RED (a zRed hacia el jugador)
      const pz = D0.tableCenterZ + TREN.vortice.zRed;
      this._portalZ = pz;
      this.portalGrp = new THREE.Group();
      this.portalSpin = new THREE.Group();
      const ring = new THREE.Mesh(new THREE.PlaneGeometry(0.54, 0.54),
        new THREE.MeshBasicMaterial({
          map: pTex, transparent: true, depthWrite: false, side: THREE.DoubleSide,
        }));
      ring.rotation.x = -Math.PI / 2;
      ring.renderOrder = 6;
      ring.material.opacity = 0.95;
      ring.material._baseOp = 0.95;              // v2.112: base del fundido
      this.portalSpin.add(ring);
      const hole = new THREE.Mesh(new THREE.CircleGeometry(0.14, 24),
        new THREE.MeshBasicMaterial({
          color: 0x120b06, transparent: true, opacity: 0.85, depthWrite: false,
        }));
      hole.rotation.x = -Math.PI / 2;
      hole.position.y = -0.003;
      hole.renderOrder = 5;
      hole.material._baseOp = 0.85;              // v2.112: base del fundido
      this.portalSpin.add(hole);
      this.portalSpin.position.set(0, D0.tableTopY + 0.012, pz);
      this.portalGrp.add(this.portalSpin);
      this.portalGrp.visible = false;
      this.group.add(this.portalGrp);
    } catch (e) { this._portalZ = 0; }

    /* ==== v2.115 · SUPERPODERES: 3 medallones (cajas/x3/dinamita) ====
     * Círculos del tamaño del vórtice que nacen al azar sobre la MESA
     * RIVAL, visibles 3 s; la bola que los roce a baja altura ACTIVA el
     * poder. Reserva canvas dorada hasta que cargue el arte. */
    this._buildPoderes();

    /* ==== v2.115 · TÚNEL DEL ARTISTA (capa P4, velocidad real) ====
     * boca (tunelboca.png) → banda interior (tunel.png repetida, el
     * scroll del interior) → boca ESPEJADA a la salida. El grupo VIAJA
     * con el mundo (z += dW) como las piezas P4 (multiplicador 1,00×) y
     * la caja tunelOscuro baja la luz de TODA la escena al 20 %.
     * v2.117 · COSIDO EXACTO: la banda ABUTA contra la boca de entrada
     * (borde a borde en -bh/2) y contra la boca de salida — sin hueco
     * ni solape; bocas de 3,4 m centradas en la ventana (bocaY) para
     * que se VEAN las tres piezas de la secuencia. */
    this.tunelGrp = new THREE.Group();
    this.tunelGrp.visible = false;
    {
      const TU = TREN.tunel;
      const bocaMat = () => new THREE.MeshBasicMaterial({
        transparent: true, depthWrite: false, side: THREE.DoubleSide, fog: false,
      });
      const bandaMat = new THREE.MeshBasicMaterial({
        transparent: true, depthWrite: false, side: THREE.DoubleSide, fog: false,
      });
      bandaMat.renderOrder = 8;
      this._bandaMat = bandaMat;
      const copias = Math.max(1, Math.round(TU.len / (TU.h * 2.35)));
      for (const side of [-1, 1]) {
        const s = side;
        /* v2.136 · FIN de los subgrupos inclinados de v2.134: las 3 piezas
         * vuelven a ser HIJAS DIRECTAS de tunelGrp y COPLANARES a s*TU.x —
         * el reparto de texturas vuelve a encontrar las bocas (era la causa
         * del «se han estropeado las imágenes de entrada y salida») y el
         * espejado v2.119 se lee como siempre. Bocas de 1,2 m: portal
         * pequeño y lejano, caben enteras en la ventana. */
        const bocaIn = new THREE.Mesh(new THREE.PlaneGeometry(TU.bh, TU.bh), bocaMat());
        bocaIn.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
        /* v2.119 · COSIDO POR EL BORDE u=1 EN LAS DOS PAREDES: la banda
         * vive en z<0 y toca SIEMPRE el borde u=1 de la textura (el ARCO
         * abierto de tunelboca.png). En la pared IZQUIERDA u=1 cae hacia
         * -z (hondo) con scale +1; en la DERECHA u=1 cae hacia +z, así
         * que hay que INVERTIR los signos — con la receta v2.118 (iguales
         * en ambas) la boca de la derecha quedaba con el arco mirando
         * FUERA de la banda: «espejadas y mal» (petición del artista).
         * IZQUIERDA: entrada normal / salida espejada (igual que siempre).
         * DERECHA: entrada espejada / salida normal — mismo resultado
         * visual: túnel continuo boca→banda→boca por las DOS ventanas. */
        bocaIn.scale.x = s < 0 ? 1 : -1;
        bocaIn.position.set(s * TU.x, TU.bocaY, 0);
        bocaIn.renderOrder = 9;
        bocaIn.userData.boca = 1;
        this.tunelGrp.add(bocaIn);
        const bocaOut = new THREE.Mesh(new THREE.PlaneGeometry(TU.bh, TU.bh), bocaMat());
        bocaOut.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
        bocaOut.scale.x = s < 0 ? -1 : 1;
        bocaOut.position.set(s * TU.x, TU.bocaY, -(TU.len + TU.bh));
        bocaOut.renderOrder = 9;
        bocaOut.userData.boca = 1;
        this.tunelGrp.add(bocaOut);
        const banda = new THREE.Mesh(new THREE.PlaneGeometry(TU.len, TU.h), bandaMat);
        banda.rotation.y = s < 0 ? Math.PI / 2 : -Math.PI / 2;
        // v2.117: de -bh/2 (borde de la boca de ENTRADA) a -(bh/2+len)
        // (borde de la boca de SALIDA) — COSIDA, cero hueco
        // v2.138: el centro vertical sale de TU.bandaY (antes h/2-0,35,
        // calibrado para la banda de 6 m — con la banda a f esa cuenta
        // hundía el arte y se veía el CORTE superior por la ventana)
        banda.position.set(s * TU.x, TU.bandaY,
          -(TU.bh / 2 + TU.len / 2));
        this.tunelGrp.add(banda);
      }
      try {
        new THREE.TextureLoader().load(A('tunelboca.png'), (t) => {
          try {
            t.colorSpace = THREE.SRGBColorSpace;
            t.anisotropy = this._aniso;
            /* v2.136: traverse() en vez de children — aunque mañana las
             * bocas vivan dentro de subgrupos, la textura SIEMPRE llega
             * (la causa real de que las bocas «se estropearan» en v2.134:
             * hijas de un subgrupo, el reparto no las encontraba). */
            this.tunelGrp.traverse((m) => {
              if (m.userData && m.userData.boca) {
                m.material.map = t;
                m.material.needsUpdate = true;
              }
            });
          } catch (e) { /* sin arte: oscuro de reserva */ }
        }, undefined, () => { /* */ });
        new THREE.TextureLoader().load(A('tunel.png'), (t) => {
          try {
            t.colorSpace = THREE.SRGBColorSpace;
            t.anisotropy = this._aniso;
            t.wrapS = THREE.RepeatWrapping;
            t.repeat.set(copias, 1);   // pegadas una detrás de otra (scroll)
            bandaMat.map = t;
            bandaMat.needsUpdate = true;
          } catch (e) { /* */ }
        }, undefined, () => { /* */ });
      } catch (e) { /* */ }
    }
    this.group.add(this.tunelGrp);
    this.tunelOscuro = new THREE.Mesh(
      new THREE.BoxGeometry(7.0, 3.4, 8.6),
      new THREE.MeshBasicMaterial({
        color: 0x000000, transparent: true, opacity: 0,
        depthWrite: false, depthTest: false, side: THREE.BackSide, fog: false,
      }));
    this.tunelOscuro.position.set(0, 1.35, -1.3);
    this.tunelOscuro.renderOrder = 900;
    this.tunelOscuro.visible = false;
    this.group.add(this.tunelOscuro);

    /* ==== v2.111 · LINGOTE de oro (lowpoly_gold_bar.glb del artista) ====
     * Se normaliza UNA vez (barra tumbada de ~0,17 m, base en y=0) y los
     * lingotes del juego son clones ligeros del prototipo. */
    this.pile = new THREE.Group();
    this.group.add(this.pile);
    /* ==== v2.141 · LOS CAJONES DEL ORO — dos cajones limpios del artista
     * (cubo1/cubo2: los de destruir SIN candado) ACHATADOS (el doble de
     * anchos y la mitad de altos) sobre el suelo del vagón, uno a cada
     * lado de la mesa CERCA DEL CENTRO DE LAS VENTANAS laterales. Su cara
     * superior (y = h) es la base de las pilas de lingotes. ==== */
    {
      const CR = TREN.cajonOro;
      this._cuboOroGeo = new THREE.BoxGeometry(CR.w, CR.h, CR.d);
      this.cajonesOro = [1, -1].map((side) => {
        const m = new THREE.Mesh(this._cuboOroGeo,
          side > 0 ? this._matCubo[1] : this._matCubo[0]);
        m.position.set(side * CR.x, CR.h / 2,
          side > 0 ? CR.zDer : CR.zIzq);
        this.group.add(m);
        return m;
      });
    }
    try {
      new GLTFLoader().load(A('lowpoly_gold_bar.glb'), (gltf) => {
        try {
          const root = gltf.scene;
          const box = new THREE.Box3().setFromObject(root);
          const sz = box.getSize(new THREE.Vector3());
          const s = 0.17 / (Math.max(sz.x, sz.y, sz.z) || 0.17);
          root.scale.setScalar(s);
          const wrap = new THREE.Group();
          wrap.add(root);
          wrap.updateMatrixWorld(true);
          const bb = new THREE.Box3().setFromObject(wrap);
          const ctr = bb.getCenter(new THREE.Vector3());
          root.position.x -= ctr.x;
          root.position.z -= ctr.z;
          root.position.y -= bb.min.y;
          this._lingoteProto = wrap;
          /* v2.140 · ALTURA REAL del lingote para el apilado EXACTO de la
           * pila (capas «unos perfectamente encima de otros»). */
          this._lingoteH = bb.getSize(new THREE.Vector3()).y + 0.0015;
        } catch (e) { /* sin GLB: reserva de caja dorada */ }
      }, undefined, () => { /* sin GLB: reserva */ });
    } catch (e) { /* */ }

    /* ==== v2.111 · EL FORAJIDO GALOPANTE (galope del artista) ====
     * Plano del caballo con jinete FUERA de las ventanas (x=±3,72) con la
     * animación en BUCLE de 3 frames (sprite sheet por imágenes) y la
     * DIANA del artista (diana.webp) para la ventana de ataque. */
    this.fj = new THREE.Group();
    this.fjPlane = new THREE.Mesh(PX_GEO);
    this.fjPlane.renderOrder = 7;
    this.fj.add(this.fjPlane);
    this._fjTex = {
      paso: ['galope1.png', 'galope2.png', 'galope3.png'].map((f) => fjMat(f, ld, A, this._aniso)),
      ventana: ['galope_ventana1.png', 'galope_ventana2.png', 'galope_ventana3.png'].map((f) => fjMat(f, ld, A, this._aniso)),
      dispara: ['galope_ventana1_dispara.png', 'galope_ventana2_dispara.png', 'galope_ventana3_dispara.png'].map((f) => fjMat(f, ld, A, this._aniso)),
      herido: [fjMat('galope_herido.png', ld, A, this._aniso)],
    };
    // material del FUNDIDO a negro (clona el de herido, con opacidad)
    try {
      this._fjFadeMat = this._fjTex.herido[0].mat.clone();
      this._fjFadeMat.transparent = true;
      this._fjFadeMat.depthWrite = false;
      this._fjFadeMat.opacity = 1;
    } catch (e) { this._fjFadeMat = null; }
    this.fjDiana = new THREE.Sprite(new THREE.SpriteMaterial({
      map: (this.ctrl.dianaTex || null), transparent: true, depthWrite: false,
      color: this.ctrl.dianaTex ? 0xffffff : 0xff5a3c,
    }));
    if (!this.ctrl.dianaTex) {
      // sin arte aún: reserva circular de la diana
      const cvD = oesteCanvas(128, 128);
      const cd = cvD.getContext('2d');
      cd.fillStyle = '#e33'; cd.beginPath(); cd.arc(64, 64, 60, 0, Math.PI * 2); cd.fill();
      cd.fillStyle = '#fff'; cd.beginPath(); cd.arc(64, 64, 40, 0, Math.PI * 2); cd.fill();
      cd.fillStyle = '#e33'; cd.beginPath(); cd.arc(64, 64, 20, 0, Math.PI * 2); cd.fill();
      this.fjDiana.material.map = new THREE.CanvasTexture(cvD);
      this.fjDiana.material.needsUpdate = true;
    }
    this.fjDiana.scale.setScalar(TREN.forajido.dianaSize);
    this.fjDiana.renderOrder = 8;
    this.fjDiana.visible = false;
    this.fj.add(this.fjDiana);
    this.fj.visible = false;
    this.group.add(this.fj);

    /* ==== v2.119 · EL INDIO CABALGANTE (pool de 3, grupos 1-3) ====
     * Mismo plano-sprite que el forajido con los 4 frames indio1-4.png
     * (UN estado de cabalgada) e indioalcanzado.png al darle. Cada jinete
     * lleva SU mirilla (diana) SIEMPRE visible mientras está en escena y
     * SU material de fundido (clon transparente) para desvanecerse. */
    this._indPool = [];
    {
      const I = TREN.indio;
      this._indLd = ld; this._indA = A;   // loaders para las texturas diferidas
      for (let i = 0; i < 3; i++) {
        const grp = new THREE.Group();
        const plane = new THREE.Mesh(PX_GEO);
        plane.renderOrder = 7;
        grp.add(plane);
        const diana = new THREE.Sprite(new THREE.SpriteMaterial({
          map: (this.ctrl.dianaTex || null), transparent: true, depthWrite: false,
          color: this.ctrl.dianaTex ? 0xffffff : 0xff5a3c,
        }));
        if (!this.ctrl.dianaTex) {
          diana.material.map = this.fjDiana.material.map;   // reserva circular
          diana.material.needsUpdate = true;
        }
        diana.scale.setScalar(I.dianaSize);
        diana.renderOrder = 8;
        diana.visible = false;
        grp.add(diana);
        let fadeMat = null;
        try {
          const base = indMat('indioalcanzado.png', ld, A, this._aniso);
          fadeMat = base.mat.clone();
          fadeMat.transparent = true;
          fadeMat.depthWrite = false;
          fadeMat.alphaTest = 0;          // el fundido necesita alpha real
          fadeMat.opacity = 1;
        } catch (e) { fadeMat = null; }
        grp.visible = false;
        this.group.add(grp);
        this._indPool.push({ grp, plane, diana, fadeMat });
      }
    }

    this._hud = new HudOeste(this.ctrl);
  }

  /* ======================================================================
   *  v2.111 · LA PIRÁMIDE DE CAJONES (arkanoid del botín)
   *  10 cajones en pirámide 5-3-2 sobre el muelle de madera. Reparto
   *  ALEATORIO: 2-3 cajones llevan CANDADO-lingote (cubolingote*.png del
   *  artista, al menos 2 y nunca más de un lingote por cajón); el resto
   *  son neutros (cubo1-3.png). FÍSICA: cada cajón se APOYA en los dos de
   *  su fila inferior — si los pierde, CAE por gravedad hasta el apoyo
   *  siguiente. Pirámide nueva (reparto nuevo) al vaciarla.
   *  ====================================================================== */
  _clearPiramide() {
    for (const rec of this.cubos) {
      this.piramide.remove(rec.mesh);
    }
    this.cubos = [];
  }
  _cuboX(row, i) {
    const NROWS = [5, 3, 2];                    // 5 · 3 · 2 (no lineal)
    const n = NROWS[row] || 5;
    // v2.115: separación 1/4 del tamaño entre cajones (desde el principio)
    return (i - (n - 1) / 2) * TREN.cubo.size * (TREN.cubo.sep || 1);
  }
  _buildPiramide() {
    this._clearPiramide();
    const C = TREN.cubo;
    const nLing = C.minLingote +
      ((Math.random() * (C.maxLingote - C.minLingote + 1)) | 0);
    const slots = [];
    // v2.111 · PIRÁMIDE 5-3-2 (filas del artista, NO lineal)
    const NROWS = [5, 3, 2];
    for (let r = 0; r < NROWS.length; r++) {
      for (let i = 0; i < NROWS[r]; i++) slots.push({ row: r, i });
    }
    for (let i = slots.length - 1; i > 0; i--) {   // barajo
      const j = (Math.random() * (i + 1)) | 0;
      const t = slots[i]; slots[i] = slots[j]; slots[j] = t;
    }
    const lingSet = new Set(slots.slice(0, nLing).map((s) => s.row + ':' + s.i));
    let k = 0;
    for (const s of slots) {
      const isLing = lingSet.has(s.row + ':' + s.i);
      const tipo = isLing
        ? 1 + ((Math.random() * 2) | 0)          // cubolingote1|2
        : 1 + ((Math.random() * 3) | 0);         // cubo1|2|3
      const mesh = new THREE.Mesh(this._cuboGeo,
        isLing ? this._matLingote[tipo - 1] : this._matCubo[tipo - 1]);
      const x = this._cuboX(s.row, s.i);
      const y = C.peanaH + C.size * s.row + C.size / 2;
      mesh.position.set(x, y, C.z);
      mesh.scale.setScalar(0.01);
      this.piramide.add(mesh);
      this.cubos.push({
        mesh, row: s.row, i: s.i, tipo,
        base: new THREE.Vector3(x, y, C.z),
        lingote: isLing, abierto: false, muerto: false,
        cae: false, vy: 0, shakeT: 0, born: 0.16 + k * 0.045,
      });
      k++;
    }
  }
  /* v2.116 · SOPORTES FÍSICOS (posiciones REALES, no filas): el bug de
   * las CAJAS FLOTANDO venía de decidir el apoyo por `row` lógico — una
   * caja caída conservaba su fila vieja y las recién aterrizadas
   * «heredaban» apoyos fantasma. Ahora un cajón sostiene a otro si está
   * VIVO, ASENTADO (ni cayendo ni de caída libre), lo SOLAPA horizontalmente
   * (la MISMA ventana que usa la lluvia para aterrizar) y su cara
   * superior queda a la altura de la cara inferior del de encima. */
  _soportes(rec) {
    const C = TREN.cubo, half = C.size / 2;
    const out = [];
    const bot = rec.base.y - half;
    for (const o of this.cubos) {
      if (o === rec || o.muerto || o.cayendo || o.cae) continue;
      if (Math.abs(o.base.x - rec.base.x) >= C.size * 0.98) continue;
      if (Math.abs(o.base.z - rec.base.z) >= C.size * 0.62) continue;
      if (Math.abs((o.base.y + half) - bot) <= 0.10) out.push(o);
    }
    return out;
  }
  _apoyado(rec) {
    const C = TREN.cubo, half = C.size / 2;
    // sobre el MUELLE (su cara inferior a ras del muelle, dentro de la huella)
    if (rec.base.y - half <= C.peanaH + 0.03 &&
        Math.abs(rec.base.x) <= C.peanaW / 2 + C.size * 0.1 &&
        Math.abs(rec.base.z - C.z) <= C.peanaD / 2) return true;
    return this._soportes(rec).length > 0;
  }
  /** Superficie donde aterrizaría el cajón: la cima de las cajas DEBAJO
   *  de él (por altura, no por fila) o el muelle. v2.116 físico. */
  _sueloBajo(rec) {
    const C = TREN.cubo, half = C.size / 2;
    let top = C.peanaH;
    const bot = rec.base.y - half;
    for (const o of this.cubos) {
      if (o === rec || o.muerto || o.cayendo) continue;
      if (Math.abs(o.base.x - rec.base.x) >= C.size * 0.98) continue;
      if (Math.abs(o.base.z - rec.base.z) >= C.size * 0.62) continue;
      const t2 = o.base.y + half;
      if (t2 > top && t2 <= bot + 0.02) top = t2;   // SÓLO lo que hay debajo
    }
    return top;
  }

  /* --------------------- impacto de la bola en un cajón ------------------- */
  _golpeCubo(rec) {
    const g = this.game;
    if (rec.lingote) {
      /* CANDADO-lingote: cambia la textura a ABIERTO, tiembla 1 s y
       * REVIENTA soltando el lingote en parábola (petición literal). */
      rec.abierto = true;
      rec.shakeT = 1.0;
      rec.mesh.material = this._matAbierto[rec.tipo - 1];
      this.ctrl.sfx('impacto', 0);
      this.ctrl.sfx('madera', 0);
      this.ctrl.fx.flash(rec.mesh.position, 1.3, 0xffd24a);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.55, 110);
    } else {
      this._revientaCubo(rec);
    }
  }
  _revientaCubo(rec) {
    rec.muerto = true;
    rec.mesh.visible = false;
    this.ctrl._puntosAdd(20, rec.mesh.position);   // v2.119: cajón reventado
    this.ctrl.sfx('madera', 0);
    this.ctrl.fx.spark(rec.mesh.position, 10, 0xc99a5a, 2.6, 1.1);
    this.ctrl.fx.smoke(rec.mesh.position, 1, false);
    const g = this.game;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 90);
    this._checkPiramide();
  }
  _explotaLingote(rec) {
    rec.muerto = true;
    rec.mesh.visible = false;
    this.ctrl.sfx('boom', 0);
    this.ctrl.fx.flash(rec.mesh.position, 2.0, 0xffd24a);
    this.ctrl.fx.spark(rec.mesh.position, 16, 0xffd24a, 3.2, 1.4);
    this.ctrl.fx.smoke(rec.mesh.position, 2, false);
    const g = this.game;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 150);
    this._lanzaLingote(rec.mesh.position.clone());
    this._checkPiramide();
  }
  _checkPiramide() {
    if (this.cubos.length && this.cubos.every((r) => r.muerto)) {
      this._pirT = TREN.cubo.respawn;
      this._msg = tx('tren_piramide');
      this._msgT = 1.8;
    }
  }

  /* ------------------------ lingotes (vuelo + pila) ----------------------- */
  _pileSlot(side, slot) {
    /* v2.141 · PILA SOBRE LOS CAJONES DEL ORO — el dueño: «los lingotes
     * van a caer a ambos lados de la mesa pero cerca del centro de las
     * ventanas, en el suelo, sobre dos grandes cajones de madera… Estarán
     * bien colocados uno al lado del otro y encima respetando sus
     * dimensiones para que no se superpongan ni se metan unos dentro de
     * otros, bien colocados aunque pueden tener pequeñas variaciones de
     * colocación para que no parezca tan perfecta».
     * Cada cajón (mitad IZQ / mitad DER) llena CAPAS de 9 (3 columnas ×
     * 3 filas) con hueco uniforme; al completar un plano se apila ENCIMA
     * con la altura REAL del lingote (GLB + 1,5 mm) — y cada hueco lleva
     * su PEQUEÑA variación (±7 mm en x · ±3 mm en z · ±1,7° de yaw) con
     * holguras que NUNCA llegan a tocar el vecino. */
    const hL = this._lingoteH || 0.0515;       // altura real de capa (GLB + gap)
    const CR = TREN.cajonOro;
    const layer = Math.floor(slot / 9);         // plano de apilamiento (3×3)
    const k = slot % 9;                         // hueco dentro del plano
    const gx = k % 3;                           // 3 columnas a lo ancho (x)
    const gz = Math.floor(k / 3);               // 3 filas a lo largo (z)
    const jx = (Math.random() - 0.5) * 2 * CR.jX;
    const jz = (Math.random() - 0.5) * 2 * CR.jZ;
    const yaw = (Math.random() - 0.5) * 2 * CR.yaw;
    return {
      pos: new THREE.Vector3(
        side * CR.x + (gx - 1) * CR.sepX + jx,
        CR.h + layer * hL,
        (side < 0 ? CR.zIzq : CR.zDer) + (gz - 1) * CR.sepZ + jz),
      yaw,
    };
  }
  _lanzaLingote(from) {
    if (!this._lingoteProto) {                  // GLB aún cargando: caja reserva
      const g0 = new THREE.Group();
      g0.add(new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.05, 0.08), this.goldMat));
      this._lingoteProto = g0;
    }
    const mesh = this._lingoteProto.clone(true);
    mesh.visible = true;
    /* v2.141 · el lingote alterna IZQ/DER y ocupa el PRIMER hueco libre de
     * SU cajón (si el forajido robó uno, SU hueco vuelve a la lista). */
    const side = this._pileAlt ? 1 : -1;
    this._pileAlt = !this._pileAlt;
    const idx = side > 0 ? 1 : 0;
    const slot = this._pileFree[idx].length
      ? this._pileFree[idx].pop()
      : this._pileN[idx]++;
    const dest = this._pileSlot(side, slot);
    const T = 0.9, grav = 6.5;
    const v = new THREE.Vector3(
      (dest.pos.x - from.x) / T,
      (dest.pos.y - from.y + 0.5 * grav * T * T) / T,
      (dest.pos.z - from.z) / T);
    mesh.position.copy(from);
    this.pile.add(mesh);
    this.ingotes.push({
      mesh, t: 0, T, v, grav, volando: true, robado: false,
      dest: dest.pos, yaw: dest.yaw,
      side, slot,   // v2.141: hueco PROPIO por cajón (el robo lo libera)
    });
    this.ctrl.sfx('coin', 0);
  }
  _limpiaPila() {
    for (const it of this.ingotes) this.pile.remove(it.mesh);
    this.ingotes = [];
    this._pileN = [0, 0];       // v2.141: contadores POR CAJÓN
    this._pileFree = [[], []];  // y huecos libres en cero
  }
  _enLingote() {
    this.ingots++;
    this.ctrl._puntosAdd(100, this.pile.position);   // v2.119: oro asegurado
    const meta = (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0);   // v3.6.18 (ronda 24): LEYENDA +1 lingote
    if (this.ingots === meta) {
      this._msg = tx('tren_objetivo', { n: this.ingots, m: meta });
      this._msgT = 3.0;
      this.ctrl.sfx('diana', 0);
    } else {
      this._msg = tx('tren_lingote', { n: this.ingots, m: meta });
      this._msgT = 1.6;
    }
  }
  /** v2.113 · ROBO ESPECTÁCULO: el forajido se lleva UN lingote y se VE
   *  TODO — el lingote LEVITA 1 m sobre la mesa GIRANDO y TEÑIDO DE ROJO,
   *  se queda un instante flotando y SALE DISPARADO por la ventana hacia
   *  el jinete que huye (con ZUMBIDO de escapatoria). Fases en fxStep:
   *   robo 0 → levitación (0,9 s) · robo 1 → vuelo por la ventana. */
  _robaLingote() {
    let tgt = null;
    for (let i = this.ingotes.length - 1; i >= 0; i--) {
      if (!this.ingotes[i].volando && !this.ingotes[i].robado) {
        tgt = this.ingotes[i]; break;
      }
    }
    if (!tgt) return false;
    tgt.robado = true;
    tgt.volando = false;
    tgt.robo = 0;                              // fase: levitación
    tgt.roboT = 0;
    tgt.base = tgt.mesh.position.clone();      // hueco que ocupaba en la pila
    tgt.spin = (Math.random() < 0.5 ? -1 : 1) * (6 + Math.random() * 4);
    // MATERIALES PROPIOS (el clon los comparte con el proto): teñir de
    // ROJO sólo este lingote, sin enrojecer la pila ni los futuros.
    try {
      tgt.mesh.traverse((n) => {
        if (!n.isMesh || !n.material) return;
        const arr = Array.isArray(n.material) ? n.material : [n.material];
        const cl = arr.map((m) => {
          const c = m.clone();
          if (c.color) c.color.setHex(0xff2a1a);
          if (c.emissive) { c.emissive.setHex(0x9c0e00); c.emissiveIntensity = 0.9; }
          return c;
        });
        n.material = Array.isArray(n.material) ? cl : cl[0];
      });
    } catch (e) { /* sin tinte: sigue visible igualmente */ }
    this.ingots = Math.max(0, this.ingots - 1);   // la cuenta también baja
    /* v2.141 · el hueco que ocupaba VUELVE a la lista de su cajón: el
     * próximo lingote lo reutiliza (nunca se solapan). */
    {
      const idx = tgt.side > 0 ? 1 : 0;
      if (!this._pileFree[idx].includes(tgt.slot)) this._pileFree[idx].push(tgt.slot);
    }
    this._sndZumbido();
    return true;
  }

  /* ============ v2.140 · RESULTADO DE LA ESTACIÓN (paneles + risas) ======
   * recompensa.png (llegar CON el oro) · forajido_robo.png (robo) + las
   * risas del forajido. Plano RGBA del artista con pop elástico (patrón
   * insignia), en el hueco entre la mesa rival y la pirámide; se retira al
   * partir (_depart), al cerrar la etapa (_finish) y en dispose(). */
  _showPremio(kind) {
    const robo = kind === 'robo';
    const url = robo ? (this.ctrl.manifest && this.ctrl.manifest.roboUrl)
                     : (this.ctrl.manifest && this.ctrl.manifest.recompensaUrl);
    if (!url) return;
    this._hidePremio();
    const tex = new THREE.TextureLoader().load(url);
    tex.colorSpace = THREE.SRGBColorSpace;
    // aspecto NATIVO del arte: recompensa 1:1 (1,15 m) · robo 1:2 (0,78×1,56)
    const h = robo ? 1.56 : 1.15, w = robo ? h * 0.5 : h;
    const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h),
      new THREE.MeshBasicMaterial({
        map: tex, transparent: true, fog: false, side: THREE.DoubleSide,
      }));
    m.position.set(0, robo ? 1.72 : 1.62, -3.55);
    m.renderOrder = 40;
    this.premio = m;
    this.premioT = 0;
    m.scale.setScalar(0.2);            // nace pequeño: pop elástico en fxStep
    this.group.add(m);
  }
  _hidePremio() {
    if (this.premio) { this.group.remove(this.premio); this.premio = null; }
  }

  /* ============ v2.140 · RISAS del FORAJIDO (robo de la parada) ==========
   *  v3.6.2-SDK2 (FASE 4): el motor vive en el SDK de campeonatos (cache +
   *  lección v2.125 + silencio del arcade respetado). Aquí queda la
   *  orquestación: precarga al montar la etapa y reintentos hasta que
   *  suena (tiene() marca el «ya sonaron» exactamente como antes). */
  loadRisasForajido() {
    try { this.__sfxSDK().precarga('risas_forajido.mp3'); } catch (e) { /* */ }
  }
  _playRisasForajido(vol) {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      const eng = this.__sfxSDK();
      if (!eng.tiene('risas_forajido.mp3')) {
        eng.precarga('risas_forajido.mp3');   // aún decodificando: reintento
        return;
      }
      eng.play('risas_forajido.mp3', vol || 0.9);
      this._risaFt = 9;                // ya sonaron: sin reintentos
    } catch (e) { /* */ }
  }

  /* v3.6.2-SDK2 · motor SFX del SDK de campeonatos (una instancia por
   * controlador, cache propia; assets relativos a ESTE módulo). */
  __sfxSDK() {
    if (!this.__sdkSfx) this.__sdkSfx = createSfx(import.meta.url, () => this.game);
    return this.__sdkSfx;
  }

  /* ======================================================================
   *  v2.111 · EL FORAJIDO GALOPANTE — sprite sheet en BUCLE (galope1-3)
   *  que cabalga PARALELO al tren y lo ADELA; aparece cada cierto tiempo
   *  al azar, por ambos lados (nunca los dos a la vez), unas 10 veces por
   *  trayecto. Dos comportamientos:
   *   · PASO — cruza la ventana y sigue su camino (galope de perfil).
   *   · ATAQUE — alcanza el centro de la ventana, iguala la marcha y se
   *     queda 4 s (galope_ventana1-3); en 6 de cada 10 saca el REVÓLVER
   *     (galope_ventana*_dispara) con la DIANA del artista encima: acierto =
   *     galope_herido 1 s + fundido a negro; fallo = humo, disparo y ROBO
   *     de un lingote.
   *  ====================================================================== */
  _fjFrameOf(kind) {
    const arr = this._fjTex[kind] || this._fjTex.paso;
    return arr[this._fjFrame % arr.length];
  }
  _fjSetFrame(kind) {
    const e = this._fjFrameOf(kind);
    this.fjPlane.material = e.mat;
    const F = TREN.forajido;
    const h = F.h, w = h * (e.aspect || 1);
    this._fjW = w;
    // ESPEJO en la ventana DERECHA: el arte galopa mirando a su derecha;
    // así el caballo SIEMPRE encara el sentido de su galope (hacia -z).
    this.fjPlane.scale.set(w * (this._fjSide > 0 ? -1 : 1), h, 1);
  }
  _fjPose(bob) {
    const F = TREN.forajido;
    // yBase: los cascos pisan el llano (~0,57 m) y el JINETE queda en el
    // hueco visible de la ventana (y 1,08–2,55 en el plano del forajido)
    this.fj.position.set(this._fjSide * F.xOut, F.yBase + bob, this._fjZ);
    this.fjPlane.rotation.y = this._fjSide < 0 ? Math.PI / 2 : -Math.PI / 2;
  }
  _fjSpawn() {
    const F = TREN.forajido;
    this._fjCount++;
    // lados alternados sin caer en la monotonía (nunca 3 iguales seguidos)
    this._fjSide =
      (this._fjLastSide === this._fjPrevSide) ? -this._fjLastSide
        : (Math.random() < 0.5 ? -1 : 1);
    this._fjPrevSide = this._fjLastSide;
    this._fjLastSide = this._fjSide;
    const paso = Math.random() < 0.45;          // 45% cruza sin pararse
    this._fjState = paso ? 'paso' : 'ida';
    this._fjAtk = !paso && Math.random() < 0.6; // 60% de las paradas: dispara
    this._fjZ = F.zIn;
    this._fjT = 0; this._fjFrame = 0; this._fjFrameT = 0; this._fjV = 0;
    this.fj.visible = true;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
    this._sndYihha();   // v2.113: ¡ALERTA! grito del jinete al acercarse
  }
  _fjGone() {
    this.fj.visible = false;
    this.fjDiana.visible = false;
    this._fjState = 'off';
    const F = TREN.forajido;
    this._fjNext = (this._fjCount >= F.total) ? 9999
      : F.nextMin + Math.random() * (F.nextMax - F.nextMin);
  }
  _fjDianaPos() {
    const F = TREN.forajido;
    // posición VARIABLE sobre el jinete (torso/cabeza), delante del plano
    this.fjDiana.position.set(
      -this._fjSide * 0.06,
      (0.04 + Math.random() * 0.24) * F.h,
      (Math.random() - 0.5) * 0.34);
  }
  _fjHerido() {
    this.fjDiana.visible = false;
    this._fjState = 'herido';
    this._fjT = 0; this._fjFrame = 0;
    this._fjSetFrame('herido');
    this.ctrl.sfx('grito', 0);
    this._msg = tx('tren_herido');
    this._msgT = 2.2;
    this.ctrl.fx.flash(this.fj.position, 1.4, 0xff6a4a);
    this.ctrl._puntosAdd(150, this.fj.position);   // v2.119: puntería +150
  }
  _fjFuga() {
    this._fjState = 'fuga';
    this._fjT = 0; this._fjFrame = 0; this._fjV = 1.2;
    this.fjDiana.visible = false;
    this._fjSetFrame('paso');
  }
  _fjDispara() {
    const g = this.game;
    // humo + fogonazo en la BOCA del revólver (fracción del plano del arte)
    _AS_V1.set(-0.10 * this._fjW, 0.10 * TREN.forajido.h, -this._fjSide * 0.10);
    this.fjPlane.localToWorld(_AS_V1);
    _AS_V1.x -= this._fjSide * 0.06;
    this.ctrl.fx.smokeGun(_AS_V1, 3);
    this.ctrl.fx.flash(_AS_V1, 1.3, 0xffd98a);
    this.ctrl.sfx('disparo', 0);
    if (g.renderer.xr.isPresenting) { g.haptic(0, 0.6, 160); g.haptic(1, 0.6, 160); }
    if (this._robaLingote()) {
      this._msg = tx('tren_robo');
      this._msgT = 2.4;
    }
  }
  _fjUpdate(dt) {
    const F = TREN.forajido;
    /* v2.116 · EN EL TÚNEL NO HAY JINETE: en cuanto el túnel entra en
     * escena ('pre' incluido) el jinete DESAPARECE y su agenda se PAUSA;
     * al salir del túnel vuelve a programarse con un intervalo nuevo. */
    if (this._tunnelPhase !== 'none') {
      if (this._fjState !== 'off') this._fjGone();
      return;
    }
    if (this._fjState === 'off') {
      if (this.phase !== 'run') return;
      /* v2.119 · los INDIOS tienen prioridad en la ventana: mientras haya
       * un grupo cabalgando, la agenda del forajido se PAUSA (los jinetes
       * aparecen «cuando no está el forajido en pantalla» — y viceversa,
       * para no solapar dos duelos en la misma ventana). */
      if (this._indAny) return;
      this._fjNext -= dt;
      if (this._fjNext <= 0 && this._fjCount < F.total) this._fjSpawn();
      return;
    }
    this._fjT += dt;
    // bucle del galope (sprite sheet de 3 frames del artista)
    this._fjFrameT += dt;
    if (this._fjFrameT >= F.loopT) {
      this._fjFrameT -= F.loopT;
      this._fjFrame++;
      if (this._fjState === 'ventana') {
        this._fjSetFrame(this._fjAtk ? 'dispara' : 'ventana');
      } else if (this._fjState !== 'herido' && this._fjState !== 'fade') {
        this._fjSetFrame('paso');
      }
    }
    const bob = Math.abs(Math.sin(this._fjT * F.bobW)) * F.bobA;
    if (this._fjState === 'paso') {
      // GALOPE DE PASO: cruza la ventana adelantando al tren y sigue
      this._fjZ -= F.vPaso * dt;
      if (this._fjZ < F.zOut) return this._fjGone();
      this._fjPose(bob);
    } else if (this._fjState === 'ida') {
      // aproximación frenando hasta el CENTRO de la ventana
      const k = Math.min(1, this._fjT / 1.6);
      const e2 = 1 - Math.pow(1 - k, 3);
      this._fjZ = F.zIn + (F.zAtk - F.zIn) * e2;
      if (k >= 1) {
        this._fjState = 'ventana';
        this._fjT = 0; this._fjFrame = 0; this._fjFrameT = F.loopT;
        if (this._fjAtk) {
          this._fjDianaPos();
          this.fjDiana.visible = true;
          this._msg = tx('tren_forajido');
          this._msgT = 2.6;
          this.ctrl.sfx('desenfundar', 0);
        }
      }
      this._fjPose(bob);
    } else if (this._fjState === 'ventana') {
      // iguala la velocidad del tren: 4 s a la altura de la ventana
      this._fjZ = F.zAtk;
      if (this._fjT >= F.atkT) {
        // v2.111: SÓLO la variante CON revólver dispara y roba — el galope
        // «sin disparo» (galope_ventana1-3) pasa limpio (petición literal)
        if (this._fjAtk) this._fjDispara();
        this._fjFuga();
      }
      this._fjPose(bob);
    } else if (this._fjState === 'herido') {
      // galope_herido.png 1 s (se endereza hacia atrás)…
      this._fjZ = F.zAtk + this._fjT * 0.4;
      if (this._fjT >= F.heridoT) {
        this._fjState = 'fade';
        this._fjT = 0;
        if (this._fjFadeMat) this.fjPlane.material = this._fjFadeMat;
      }
      this._fjPose(bob * 0.4);
    } else if (this._fjState === 'fade') {
      // …y la imagen se FUNDE A NEGRO (petición literal del artista)
      const k = Math.min(1, this._fjT / F.fadeT);
      if (this._fjFadeMat) {
        this._fjFadeMat.opacity = 1 - k;
        this._fjFadeMat.color.setScalar(1 - k * 0.92);
      }
      this._fjPose(0);
      if (k >= 1) this._fjGone();
    } else if (this._fjState === 'fuga') {
      // se va ADELANTANDO y pierde la ventana por delante
      this._fjV = Math.min(F.vPaso * 1.35, this._fjV + 2.6 * dt);
      this._fjZ -= this._fjV * dt;
      if (this._fjZ < F.zOut) return this._fjGone();
      this._fjPose(bob);
    }
  }

  /* ======================================================================
   *  v2.119 · EL INDIO CABALGANTE — sprite sheet indio1-4.png (UN estado
   *  de cabalgada). Aparece en GRUPOS de 1 a 3 jinetes «ligeramente
   *  separados» SOLO cuando el forajido NO está en pantalla (y nunca en
   *  el túnel): cabalgan hasta la parte media de la ventana, se plantan
   *  un instante con la MIRILLA SIEMPRE encima, sueltan una FLECHA que
   *  roba un lingote (el mismo espectáculo rojo que el disparo del
   *  forajido) y se marchan. Si le das: indioalcanzado.png 1 s y fade.
   *  ====================================================================== */
  _indFrameOf() {
    const arr = this._indTex || (this._indTex = [
      indMat('indio1.png', this._indLd, this._indA, this._aniso),
      indMat('indio2.png', this._indLd, this._indA, this._aniso),
      indMat('indio3.png', this._indLd, this._indA, this._aniso),
      indMat('indio4.png', this._indLd, this._indA, this._aniso),
    ]);
    return arr[this._indFrame % arr.length];
  }
  _indSetFrame(rec, mat) {
    const e = mat || this._indFrameOf();
    rec.plane.material = e.mat;
    const I = TREN.indio;
    const h = I.h, w = h * (e.aspect || 1);
    rec.w = w;
    // ESPEJO en la ventana DERECHA (el arte galopa mirando a su derecha):
    // el caballo SIEMPRE encara su marcha (hacia -z), como el forajido.
    rec.plane.scale.set(w * (rec.side > 0 ? -1 : 1), h, 1);
  }
  _indPose(rec, bob) {
    const I = TREN.indio;
    rec.grp.position.set(
      rec.side * (I.xOut + rec.k * 0.02),   // 2 cm por jinete: sin z-fight
      I.yBase + bob, rec.z);
    rec.plane.rotation.y = rec.side < 0 ? Math.PI / 2 : -Math.PI / 2;
  }
  _indSpawn() {
    const I = TREN.indio;
    this._indCount++;
    // lados alternados (nunca 3 iguales seguidos), TODO el grupo por un lado
    const side =
      (this._indLastSide === this._indPrevSide) ? -this._indLastSide
        : (Math.random() < 0.5 ? -1 : 1);
    this._indPrevSide = this._indLastSide;
    this._indLastSide = side;
    // tamaño del grupo: 1 (55%) · 2 (30%) · 3 (15%)
    const r = Math.random();
    const n = r < 0.55 ? 1 : (r < 0.85 ? 2 : 3);
    this._inds = [];
    for (let k = 0; k < n; k++) {
      const pool = this._indPool[k];
      const rec = {
        grp: pool.grp, plane: pool.plane, diana: pool.diana,
        fadeMat: pool.fadeMat, side, k,
        z: I.zIn - k * I.sepZ,            // grupo «ligeramente separado»
        zAtk: I.zAtk - k * I.sepZ,
        state: 'ida', t: 0, frame: 0, frameT: 0, w: I.h,
      };
      this._indSetFrame(rec);
      rec.diana.position.set(-side * 0.06, 0.16 * I.h, 0);
      rec.diana.visible = true;           // MIRILLA SIEMPRE encima
      rec.grp.visible = true;
      this._indPose(rec, 0);
      this._inds.push(rec);
    }
    this._indAny = true;
    this._sndYihha();                     // ¡ALERTA! igual que el forajido
    this._msg = tx('tren_indio');
    this._msgT = 2.6;
  }
  _indGoneAll() {
    for (const rec of this._inds) {
      rec.grp.visible = false;
      rec.diana.visible = false;
    }
    this._inds = [];
    this._indAny = false;
    const I = TREN.indio;
    this._indNext = (this._indCount >= I.total) ? 9999
      : I.nextMin + Math.random() * (I.nextMax - I.nextMin);
  }
  /** El tren llega al andén: los indios se van galopando (nada cruza). */
  _indFleeAll() {
    for (const rec of this._inds) {
      if (rec.state === 'ida' || rec.state === 'ventana') {
        rec.state = 'fuga';
        rec.v = 1.2;
        rec.diana.visible = false;
      }
    }
  }
  _indHerido(rec) {
    rec.diana.visible = false;
    rec.state = 'alcanzado';
    rec.t = 0;
    this._indSetFrame(rec, indMat('indioalcanzado.png',
      this._indLd, this._indA, this._aniso));
    this.ctrl.sfx('grito', 0);
    this._msg = tx('tren_indio_ok');
    this._msgT = 2.2;
    this.ctrl.fx.flash(rec.grp.position, 1.4, 0xff6a4a);
    this.ctrl._puntosAdd(150, rec.grp.position);   // puntería: +150
  }
  _indDispara(rec) {
    const g = this.game;
    // fogonazo suave en el ARCO (parte alta del plano del arte)
    _AS_V1.set(-0.16 * rec.w, 0.24 * TREN.indio.h, -rec.side * 0.10);
    rec.plane.localToWorld(_AS_V1);
    this.ctrl.fx.flash(_AS_V1, 0.9, 0xffe9b0);
    this.ctrl.sfx('desenfundar', 0);
    // LA FLECHA vuela hasta tu cara y AL LLEGAR roba el lingote (mismo
    // efecto rojo-levitante que el disparo del forajido)
    let from;
    try { from = _AS_V1.clone(); } catch (e) { from = rec.grp.position.clone(); }
    let to = null;
    try {
      to = g.camera ? g.camera.getWorldPosition(new THREE.Vector3()) : null;
    } catch (e) { to = null; }
    if (!to) to = new THREE.Vector3(0.4, 1.6, 0.4);
    this._flecha(from, to, rec);
  }
  _flecha(from, to, rec) {
    const I = TREN.indio;
    // astilla de flecha: astil fino + punta, orientado al vuelo
    const grp = new THREE.Group();
    const shaft = new THREE.Mesh(
      new THREE.CylinderGeometry(0.008, 0.008, 0.30, 6),
      new THREE.MeshBasicMaterial({ color: 0x8a5a28, fog: false }));
    shaft.rotation.x = Math.PI / 2;
    shaft.position.z = -0.05;
    grp.add(shaft);
    const tip = new THREE.Mesh(
      new THREE.ConeGeometry(0.016, 0.06, 6),
      new THREE.MeshBasicMaterial({ color: 0xb9b9c4, fog: false }));
    tip.rotation.x = -Math.PI / 2;
    tip.position.z = -0.23;
    grp.add(tip);
    grp.position.copy(from);
    grp.lookAt(to);
    grp.renderOrder = 9;
    this.group.add(grp);
    this._flechas.push({ grp, t: 0, dur: I.flechaT, from: from.clone(), to: to.clone() });
    this._flechaRobo = this._flechaRobo || [];
    this._flechaRobo.push({ t: I.flechaT, rec });
  }
  _indUpdate(dt) {
    const I = TREN.indio;
    /* EN EL TÚNEL NO HAY JINETES (igual que el forajido): desaparecen y
     * su agenda se pausa hasta salir. */
    if (this._tunnelPhase !== 'none') {
      if (this._inds.length) this._indGoneAll();
      this._flechaStep(dt);
      return;
    }
    if (!this._inds.length) {
      if (this.phase === 'run' && this._fjState === 'off' &&
          this._indCount < I.total) {
        this._indNext -= dt;
        if (this._indNext <= 0) this._indSpawn();
      }
      this._flechaStep(dt);
      return;
    }
    this._indFrameT += dt;
    let vivos = 0;
    for (const rec of this._inds) {
      if (rec.state !== 'alcanzado' && rec.state !== 'fade' &&
          rec.state !== 'fuga') {
        rec.frameT = (rec.frameT || 0) + dt;
        if (rec.frameT >= I.loopT) {
          rec.frameT -= I.loopT;
          this._indFrame++;                     // contador compartido
          this._indSetFrame(rec);
        }
      }
      rec.t += dt;
      const bob = Math.abs(Math.sin(rec.t * I.bobW)) * I.bobA;
      if (rec.state === 'ida') {
        // aproximación frenando hasta SU sitio de la ventana
        const k = Math.min(1, rec.t / 1.6);
        const e2 = 1 - Math.pow(1 - k, 3);
        rec.z = (I.zIn - rec.k * I.sepZ) +
          (rec.zAtk - (I.zIn - rec.k * I.sepZ)) * e2;
        if (k >= 1) { rec.state = 'ventana'; rec.t = 0; }
        this._indPose(rec, bob);
      } else if (rec.state === 'ventana') {
        if (rec.t >= I.atkT) {
          this._indDispara(rec);                // SIEMPRE dispara la flecha
          rec.state = 'fuga';
          rec.v = 1.2;
        }
        this._indPose(rec, bob);
      } else if (rec.state === 'alcanzado') {
        // indioalcanzado.png 1 s (se endereza hacia atrás)
        rec.z += 0.4 * dt;
        this._indPose(rec, bob * 0.4);
        if (rec.t >= I.alcanzadoT) {
          rec.state = 'fade';
          rec.t = 0;
          if (rec.fadeMat) rec.plane.material = rec.fadeMat;
        }
      } else if (rec.state === 'fade') {
        const k = Math.min(1, rec.t / I.fadeT);
        if (rec.fadeMat) {
          rec.fadeMat.opacity = 1 - k;
          rec.fadeMat.color.setScalar(1 - k * 0.92);
        }
        this._indPose(rec, 0);
        if (k >= 1) { rec.grp.visible = false; rec.state = 'gone'; }
      } else if (rec.state === 'fuga') {
        rec.v = Math.min(I.vPaso * 1.35, rec.v + 2.6 * dt);
        rec.z -= rec.v * dt;
        this._indPose(rec, bob);
        if (rec.z < I.zOut) { rec.grp.visible = false; rec.state = 'gone'; }
      }
      if (rec.state !== 'gone') vivos++;
      else rec.diana.visible = false;
    }
    if (!vivos) this._indGoneAll();
    this._flechaStep(dt);
  }
  _flechaStep(dt) {
    if (!this._flechas.length) return;
    const I = TREN.indio;
    const g = this.game;
    for (const f of this._flechas) {
      if (f.done) continue;
      f.t += dt;
      const k = Math.min(1, f.t / f.dur);
      f.grp.position.lerpVectors(f.from, f.to, k);
      // leve arco: sube y baja
      f.grp.position.y += Math.sin(k * Math.PI) * 0.18;
      if (k >= 1) {
        f.done = true;
        f.grp.visible = false;
        try { this.group.remove(f.grp); } catch (e) { /* */ }
      }
    }
    this._flechas = this._flechas.filter((f) => !f.done);
    // el ROBO aterriza con la flecha (una por jinete, si hay lingotes)
    if (this._flechaRobo && this._flechaRobo.length) {
      const quedan = [];
      for (const r of this._flechaRobo) {
        r.t -= dt;
        if (r.t <= 0) {
          if (this.phase === 'run' && this._robaLingote()) {
            this._msg = tx('tren_robo');
            this._msgT = 2.4;
            if (g.renderer.xr.isPresenting) {
              g.haptic(0, 0.6, 160); g.haptic(1, 0.6, 160);
            }
          }
        } else quedan.push(r);
      }
      this._flechaRobo = quedan;
    }
  }

  /* ======================================================================
   *  v2.111 · GATILLO del vagón: el revólver de la MANO LIBRE dispara
   *  durante toda la prueba (la pala sigue en la otra mano). El rayo sale
   *  de la boca REAL del cañón (mismo convenio WYSIWYG del duelo) y sólo
   *  cuenta la DIANA del forajido de la ventana.
   *  ====================================================================== */
  trigger(hand) {
    if (this.phase !== 'run' || !this.ctrl._revInHand) return;
    const g = this.game;
    if (((hand | 0) === g.paddleHand) && g.renderer.xr.isPresenting) return;
    const ray = this.ctrl._gunRay();
    if (!ray) return;
    const now = performance.now() / 1000;
    if (now - this._gunLast < 0.16) return;   // disparos libres cada 0,16 s
    this._gunLast = now;
    let len = 8;
    this.ctrl.fx.flash(ray.pos.clone().addScaledVector(ray.dir, 0.02), 1.1, 0xffd98a);
    this.ctrl.sfx('disparo', 0);
    if (g.renderer.xr.isPresenting) g.haptic(1 - g.paddleHand, 0.5, 110);
    /* v2.113 · ACIERTO GENEROSO — «al dispararle no muere»: la diana era
     * un disco de 0,16 m frente a un sprite de 0,30 m (los tiros del borde
     * NO contaban). Ahora valen la diana (esfera amplia) y TAMBIÉN el
     * CUERPO del jinete: cualquier impacto en el plano del arte durante la
     * ventana de duelo lo tumba. */
    let hit = false, tHit = 9;
    if (this._fjState === 'ventana' && this._fjAtk) {
      const F = TREN.forajido;
      if (this.fjDiana.visible) {
        const wp = this.fjDiana.getWorldPosition(new THREE.Vector3());
        const toD = wp.clone().sub(ray.pos);
        const t = clamp(toD.dot(ray.dir), 0, 9);
        const closest = ray.dir.clone().multiplyScalar(t).add(ray.pos);
        if (t > 0.2 && closest.distanceTo(wp) < F.dianaR) {
          hit = true; tHit = t;
        }
      }
      if (!hit) {
        // CUERPO: intersección del rayo con el plano del jinete (x = fj.x)
        const den = ray.dir.x;
        if (Math.abs(den) > 1e-4) {
          const t2 = (this.fj.position.x - ray.pos.x) / den;
          if (t2 > 0.2 && t2 < 9) {
            const p = ray.pos.clone().addScaledVector(ray.dir, t2);
            const halfW = this._fjW * 0.5 * F.cuerpoK;
            const halfH = F.h * 0.5 * F.cuerpoK;
            if (Math.abs(p.z - this.fj.position.z) <= halfW &&
                Math.abs(p.y - this.fj.position.y) <= halfH) {
              hit = true; tHit = t2;
            }
          }
        }
      }
    }
    /* v2.119 · SI NO fue el forajido, pruebo con los INDIOS: diana y
     * cuerpo, igual de generoso. Un indio 'alcanzado' muestra
     * indioalcanzado.png y se desvanece (nada de robo). */
    if (!hit) {
      const I = TREN.indio;
      for (const rec of this._inds) {
        if (rec.state !== 'ida' && rec.state !== 'ventana') continue;
        // 1) la mirilla (esfera amplia como la del forajido)
        const wp = rec.diana.getWorldPosition(new THREE.Vector3());
        const toD = wp.clone().sub(ray.pos);
        const t = clamp(toD.dot(ray.dir), 0, 9);
        const closest = ray.dir.clone().multiplyScalar(t).add(ray.pos);
        if (t > 0.2 && closest.distanceTo(wp) < I.dianaR) {
          hit = true; tHit = t; this._indHitRec = rec; break;
        }
        // 2) el CUERPO del jinete (plano del arte)
        const den = ray.dir.x;
        if (Math.abs(den) > 1e-4) {
          const t2 = (rec.grp.position.x - ray.pos.x) / den;
          if (t2 > 0.2 && t2 < 9) {
            const p = ray.pos.clone().addScaledVector(ray.dir, t2);
            const halfW = rec.w * 0.5 * I.cuerpoK;
            const halfH = I.h * 0.5 * I.cuerpoK;
            if (Math.abs(p.z - rec.grp.position.z) <= halfW &&
                Math.abs(p.y - rec.grp.position.y) <= halfH) {
              hit = true; tHit = t2; this._indHitRec = rec; break;
            }
          }
        }
      }
    }
    if (hit) {
      len = Math.max(0.3, tHit);
      if (this._indHitRec) {
        this._indHerido(this._indHitRec);
        this._indHitRec = null;
      } else {
        this._fjHerido();
      }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 130);
    }
    if (this.ctrl.fx) this.ctrl.fx.beam(ray.pos, ray.dir, len);
  }

  /* ======================================================================
   *  v2.111 · MÚSICA DEL VAGÓN — vagon.mp3 del artista EN BUCLE mientras
   *  dura la prueba (sustituye a la BSO del saloon: musicOn() se retira
   *  durante la etapa). Mismo canal y volúmenes que la BSO del módulo.
   *  ====================================================================== */
  _musicVol() {
    try {
      const A = this.game.audio;
      if (!A) return 0.15;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return 0.15; }
  }
  /* v3.6.3-SDK3 · MOTOR DEL VAGÓN (SDK v1.2.0, createMusic): variante
   * «direct» del motor v2.111 que sustituye — sin fundido, sin gate
   * arcPlaying, sync directo sin rampa y sin resurrección. La exclusivi-
   * dad con la BSO del saloon (antes, la ranura _mus compartida) se
   * reproduce con excluso(): si la BSO suena, el vagón no entra. */
  get _musSDKv() {
    if (!this.__musSDKv) {
      this.__musSDKv = createMusic(() => this.game, {
        url: () => this.ctrl.manifest && this.ctrl.manifest.vagonMusicUrl,
        vol: () => this._musicVol(),
        fadeIn: 0,
        syncMode: 'direct',
        gateStart: false,
        gateOn: false,
        renace: false,
        excluso: () => this.ctrl._musSDK.sonando(),
      });
    }
    return this.__musSDKv;
  }
  _musicStart() { this._musSDKv.on(); }
  _musicSync() { this._musSDKv.sync(); }
  _musicStop() { this._musSDKv.off(); }

  /* ------------------------------- ciclo ---------------------------------- */
  start() {
    const g = this.game;
    this.build();
    this.group.visible = true;
    // v2.109: los planos lejanos del parallax (140-205 m) exigen FAR mayor
    this._farWas = g.camera ? g.camera.far : 0;
    if (g.camera && this._farWas < 500) {
      g.camera.far = 500;
      g.camera.updateProjectionMatrix();
    }
    // v2.111: el FONDO del mundo pasa a CIELO — cualquier hueco por las
    // ventanas muestra cielo, NUNCA el negro del salón (anti-manchón).
    this._bgWas = g.scene.background;
    g.scene.background = new THREE.Color(0x9ec7e6);
    this.wave = 1;
    this.ingots = 0;
    this.time = TREN.time;
    this.v = 0;
    this.W = 0;
    this.meetW = 0;
    this.stationW = 0;         // la PARADA 1 nace DETENIDA en la estación
    this._signPaint(TREN.stationNames[0]);
    this._signArt(0);
    this.station.visible = true;
    this.station.position.z = 0;
    this.phase = 'intro';
    this.t = 0;
    this._stoppedT = 0;
    this._tunnelT = TREN.tunnelFirst;
    this._tunnelPhase = 'none';
    this._tunnelT2 = 0;
    /* v2.115 · tanda NUEVA: pool de bolas, poderes, bomba y túnel en cero */
    /* v2.120: además del mesh, se libera el material clonado de cada extra
     * (el recambio ya reutiliza entradas muertas; aquí es el cierre duro). */
    for (const ex of this.extras) {
      this.group.remove(ex.mesh);
      if (ex.mesh && ex.mesh.material &&
          ex.mesh.material !== this._extraMat) ex.mesh.material.dispose();
    }
    this.extras = [];
    this._spawnT = TREN.bolas.cada;   // v2.116: la 1ª EXTRA a los 4 s
    this._bomba = false; this._bombaSave = null;
    this._bombaSerie = null;          // v2.134: cadena de la dinamita en cero
    if (this._fuseMain) this._fuseMain.visible = false;
    if (this.pods) for (const p of this.pods) p.mesh.visible = false;
    this._pod = null;
    this._podT = TREN.poder.t1Min + Math.random() * (TREN.poder.t1Max - TREN.poder.t1Min);
    this._tunelZ = TREN.tunel.zIn;   // v2.116: nace LEJOS y se ve llegar
    if (this.tunelGrp) this.tunelGrp.visible = false;
    if (this.tunelOscuro) {
      this.tunelOscuro.material.opacity = 0;
      this.tunelOscuro.visible = false;
    }
    this._dead = false;
    this._floorB = 0;
    this._resultT = 0;
    this._pirT = 0;
    this._buildPiramide();
    this._limpiaPila();
    /* v2.140 · estado de la parada en cero: sin panel, sin anuncio de
     * llegada y con las RISAS del forajido YA precargadas. */
    this._hidePremio();
    this._megaLlegada = false;
    this.loadRisasForajido();
    // EL VAGÓN MANDA: fuera saloon, troqueles, mapa, cartel y forajido
    if (g.roomGroup) g.roomGroup.visible = false;
    if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = false;
    this.ctrl.mapa.visible = false;
    this.ctrl.cartel.visible = false;
    if (this.ctrl.sprite) this.ctrl.sprite.visible = false;
    if (this.ctrl.arbustoGroup) this.ctrl.arbustoGroup.visible = false;
    if (this.ctrl.arbustoSombra) this.ctrl.arbustoSombra.visible = false;
    g.champDecorHidden = true;
    // escena de juego: red visible, árbitro dormido, bola automática
    if (!this.ctrl._netParts || !this.ctrl._netParts.length) {
      this.ctrl._netParts = this.ctrl._findNetParts();
    }
    for (const m of this.ctrl._netParts) m.visible = true;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    g.rules.state = this.ctrl.stateName;
    g.rules.message = tx('tren_up');
    g.ball.ignoreNet = false;
    this.ctrl._parkMainBall();
    g.ballMesh.visible = false;
    // v2.111: PALA + REVÓLVER todo el trayecto (uno por mano)
    this.ctrl._freeGunApply(true);
    // v2.111: MÚSICA del vagón (vagon.mp3) — fuera la BSO del saloon
    this._musicStart();
    this._hud.show();
    this._msg = tx('tren_up');
    this._msgT = TREN.introPause;
    this._hud.set(this.time, this._prog(), this._msg, this._ling(), undefined,
      this.ctrl.puntos);
    this._respawnT = 1.0;
    this.ctrl.sfx('whistle', 0);
    this._startRumble();
    this._setRumble(0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.5, 140);
  }

  /** El tren ARRANCA desde el andén (o tras la parada). */
  _depart() {
    this.phase = 'run';
    this.time = TREN.time;
    this._stoppedT = 0;
    this._megaLlegada = false;      // v2.140: el anuncio de llegada, por trayecto
    this._hidePremio();             // v2.140: fuera el panel de la parada
    /* v2.118 · el primer túnel del tramo NO pisa la salida del andén: al
     * menos 12 s de viaje antes de que la boca aparezca a lo lejos. */
    this._tunnelT = Math.max(this._tunnelT, 12);
    const meta = (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0);   // v3.6.18 (ronda 24): LEYENDA +1 lingote
    // (la pirámide de la parada ya está en escena: la monta start() o _arrived())
    this._serveBall();
    this._msg = tx('tren_sale', { n: this.wave, m: meta });
    this._msgT = 2.8;
    this.ctrl.sfx('whistle', 0);
    /* v2.140 · MEGAFONÍA DE ESTACIÓN: «Pasajeros al tren, partimos hacia…»
     * [destino] — el destino es la parada de ESTA wave (Dry Gulch · Perdido
     * · Bravos final). Voz pregrabada del banco del núcleo por la vía
     * VR-safe (WebAudio), con el chime del megáfono y ducking incluidos. */
    try {
      this.game.audio.announce(
        tx('tren_mega_salida', { e: TREN.stationNames[this.wave] }), true);
    } catch (e) { /* */ }
    // forajido: agenda de apariciones nueva por trayecto (~10)
    if (this._fjState !== 'off') this._fjGone();
    this._fjCount = 0;
    this._fjNext = 3.5 + Math.random() * 4;
  }

  /** FIN del reloj de la parada: el tren FRENA hasta el andén y allí se
   *  comprueba el objetivo de lingotes (3·5·7). */
  _llegaEstacion() {
    if (this.phase !== 'run') return;
    this._parkBall();
    if (this._fjState === 'ventana') {          // el duelo de ventana no cruza
      this._fjFuga();
    }
    this._indFleeAll();                         // v2.119: los indios tampoco
    /* v2.118 · NUNCA un túnel en la llegada: con el guard de bloquea no
     * debería haber ninguno vivo, pero si lo hubiera (reloj congelado,
     * reajuste) se RETIRA AQUÍ — la boca y el andén se solapaban. */
    if (this._tunnelPhase !== 'none') {
      this._tunnelPhase = 'none';
      if (this.tunelGrp) this.tunelGrp.visible = false;
      if (this.tunelOscuro) {
        this.tunelOscuro.material.opacity = 0;
        this.tunelOscuro.visible = false;
      }
    }
    this._tunnelT = Math.max(this._tunnelT, 12);  // el próximo, ya en marcha
    this.meetW = this.W + TREN.brakeDist;
    this.stationW = this.meetW;
    this._signPaint(TREN.stationNames[this.wave]);
    this._signArt(this.wave);   // v2.115: la ESTACIÓN DEL ARTISTA que llega
    this.phase = 'arrive';
    this._msg = tx('tren_llega');
    this._msgT = 3.2;
    this.ctrl.sfx('whistle', 0);
  }

  /** El tren llega AL ANDÉN: frena del todo y comprueba el BOTÍN. */
  _arrived() {
    const g = this.game;
    this.v = 0;
    this.W = this.meetW;
    this.phase = 'stop';
    this._stoppedT = 0;
    this.ctrl.sfx('brake', 0);
    this._setRumble(0);
    const meta = (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0);   // v3.6.18 (ronda 24): LEYENDA +1 lingote
    if (this.ingots < meta) return this._fail();   // sin el oro mínimo: DERROTA
    this.ctrl._puntosAdd(250, this.pile.position); // v2.119: parada completa
    /* v2.140 · ¡CARGAMENTO DE ORO A BUEN RECAUDO!: voz de estación + panel
     * recompensa.png (se ve durante toda la parada; en el andén FINAL
     * permanece hasta cerrar la etapa). */
    this._showPremio('recompensa');
    try { this.game.audio.announce(tx('tren_mega_oro'), true); } catch (e) { /* */ }
    if (this.wave >= 3) return this._stationReached(); // andén FINAL: victoria
    this.wave++;                                    // próxima parada
    this.ingots = 0;                                // cada etapa inicia a 0
    this._limpiaPila();
    this._buildPiramide();
    this._msg = tx('tren_ok');
    this._msgT = TREN.arrivePause;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.4, 120);
  }

  /** ¡ESTACIÓN FINAL! Freno largo, silbato y botín completo: SUPERADA. */
  _stationReached() {
    const g = this.game;
    this.phase = 'win';
    this._resultT = 6.0;
    this._signPaint(TREN.stationNames[3]);
    this.ctrl._puntosAdd(300, this.pile.position); // v2.119: trayecto entero
    this.ctrl.sfx('whistle_long', 0);
    g.rules.message = tx('tren_estacion');
    this._msg = tx('tren_estacion');
    this._msgT = 5.0;
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 220);
  }
  _fail() {
    const g = this.game;
    this.phase = 'fail';
    this._resultT = 4.0;
    this._msg = tx('tren_falla');
    this._msgT = 4.0;
    g.rules.message = tx('tren_falla');
    this._hud.set(0, this._prog(), tx('tren_falla'), this._ling(), undefined,
      this.ctrl.puntos);
    /* v2.140 · EL FORAJIDO SE RÍE: panel forajido_robo.png + sus RISAS
     * (risas_forajido.mp3; si el buffer aún decodifica, el step reintenta). */
    this._showPremio('robo');
    this._risaFt = 0;
    this._playRisasForajido();
  }
  _finish() {
    const won = this.phase === 'win';
    this.phase = 'idle';
    this._hidePremio();   // v2.140: fuera el panel de la estación
    this.ctrl._endTren(won);
    this.done = true;
  }
  _prog() {
    return 'PARADA ' + this.wave + '/3';
  }
  _ling() {
    return { n: this.ingots, m: (TREN.meta[this.wave - 1] || 3) + (this.ctrl && this.ctrl._leyendaOn ? 1 : 0) };   // v3.6.18 (ronda 24)
  }

  /** FÍSICA + FASES (testStep). */
  step(dt) {
    if (this.done || this.phase === 'idle') return;
    const g = this.game;
    this.t += dt;
    if (this._msgT > 0) this._msgT -= dt;
    if (this.phase === 'intro') {
      // DETENIDO en la estación 1: el andén espera tras las ventanas
      this._parkBall();
      this._stoppedT += dt;
      if (this._stoppedT >= TREN.introPause) this._depart();
    } else if (this.phase === 'run') {
      this.time -= dt;
      if (this.time <= 0) { this.time = 0; this._llegaEstacion(); return; }
      /* v2.140 · MEGAFONÍA: a los 30 s del final del trayecto la estación
       * anuncia la llegada inminente («En menos de 25 segundos llegaremos
       * a…» [estación]) — UNA vez por trayecto. */
      if (!this._megaLlegada && this.time <= 30) {
        this._megaLlegada = true;
        try {
          this.game.audio.announce(
            tx('tren_mega_llega', { e: TREN.stationNames[this.wave] }), true);
        } catch (e) { /* */ }
      }
      // crucero hacia delante
      this.v = Math.min(TREN.vMax, this.v + TREN.accel * dt);
      this.W += this.v * dt;
      this._tunnelStep(dt);
      if (this._dead) {
        this._respawnT -= dt;
        if (this._respawnT <= 0) this._serveBall();
      } else {
        this._simBall(dt);
      }
      /* v2.115 · LAS PELOTAS NACEN CADA SEGUNDO (pool multi-bola) */
      this._spawnT -= dt;
      if (this._spawnT <= 0) {
        this._spawnT += TREN.bolas.cada;
        this._naceExtra();
      }
      for (const e of this.extras) {
        if (e.alive) this._simExtra(e, dt);
      }
      /* v2.115 · SUPERPODERES de la mesa rival */
      this._poderStep(dt);
      // respawn de la pirámide (al vaciar la actual sale otra con reparto nuevo)
      if (this._pirT > 0) {
        this._pirT -= dt;
        if (this._pirT <= 0) this._buildPiramide();
      }
    } else if (this.phase === 'arrive') {
      // FRENO calculado: v² = 2·a·d hasta el andén
      this._parkBall();
      const D = Math.max(0.05, this.meetW - this.W);
      const a = clamp((this.v * this.v) / (2 * D), 0.12, 1.1);
      this.v = Math.max(0, this.v - a * dt);
      this.W += this.v * dt;
      if (this.W >= this.meetW - 0.02 || this.v <= 0.001) this._arrived();
    } else if (this.phase === 'stop') {
      this._parkBall();
      this._stoppedT += dt;
      if (this._stoppedT >= TREN.arrivePause) this._depart();
    } else if (this.phase === 'win' || this.phase === 'fail') {
      this._parkBall();
      if (this.phase === 'fail') {
        this.v = Math.max(0, this.v - 0.8 * dt);
        this.W += this.v * dt;
        if (this._risaFt < 3) {            // v2.140: las RISAS suenan aunque
          this._risaFt += dt;              // el buffer tarde en decodificar
          if (this._risaFBuf) this._playRisasForajido();
        }
      }
      this._resultT -= dt;
      if (this._resultT <= 0) this._finish();
    }
    this._hud.set(this.time, this._prog(), this._msgT > 0 ? this._msg : '',
      this._ling(), undefined, this.ctrl.puntos);
  }

  /** VISUAL por frame (CTRL.update): parallax, andén, túnel, botín, halos. */
  fxStep(dt) {
    if (this.done || !this.inited) return;
    const dW = this.v * dt;
    // v2.120 · DIANA CON ARTE TARDÍO: si diana.webp cargó DESPUÉS de
    // construir el tren, las dianas del forajido y de los indios quedaron
    // con el disco de reserva toda la sesión. Mismo re-engache por frame
    // que ya usa el asedio (5393).
    if (this.ctrl.dianaTex && this.ctrl.dianaTex.image) {
      const dtex = this.ctrl.dianaTex;
      if (this.fjDiana && this.fjDiana.material.map !== dtex) {
        this.fjDiana.material.map = dtex;
        this.fjDiana.material.color.setHex(0xffffff);
        this.fjDiana.material.needsUpdate = true;
        for (const it of this._indPool) {
          it.diana.material.map = dtex;
          it.diana.material.color.setHex(0xffffff);
          it.diana.material.needsUpdate = true;
        }
      }
    }
    // PARALLAX: cada plano a SU multiplicador (offset de textura)
    for (const s of this.scrollers) {
      if (!s.tex) continue;
      const du = (dW * s.mult / s.mPerRep) * s.sign;
      s.tex.offset.x = (s.tex.offset.x + du) % 1;
    }
    // v2.113 · ARENA EXTERIOR: el suelo corre con el mundo (offset.y —
    // el plano girado hace que +offset.y = flujo hacia +z, como las piezas)
    if (this._gndTex) {
      this._gndTex.offset.y = (this._gndTex.offset.y + dW / (240 / 90)) % 1;
    }
    // v2.110 · ELEMENTOS del parallax: cintas por plano y lado — el mundo
    // fluye de DELANTE (-z) hacia DETRÁS (+z) al multiplicador de SU plano;
    // al salir del cinturón la pieza se recicla con dotación nueva.
    for (const it of this.pxItems) {
      it.z += dW * it.L.mult;
      if (it.z > it.P.bandBack) {
        it.z -= it.P.bandBack - it.P.bandFront;
        this._pxRandomize(it);
      }
      it.mesh.position.z = it.z;
    }
    // re-encaje de piezas cuya textura acabó de cargar (aspecto real)
    for (let i = PX.fit.length - 1; i >= 0; i--) {
      const f = PX.fit[i];
      if (!f.e.ready) continue;
      if (f.it.e === f.e) {
        f.it.w = f.it.h * (f.e.aspect || 1);
        f.it.mesh.scale.set(f.it.w, f.it.h, 1);
      }
      PX.fit.splice(i, 1);
    }
    // ANDÉN: corre con el mundo (z = W - estación) y se esconde al pasar
    if (this.station) {
      const rel = this.W - this.stationW;
      this.station.position.z = rel;
      this.station.visible = Math.abs(rel) < 32;
    }
    /* v2.115 · las bolas EXTRA del pool siguen a SU bola */
    for (const e of this.extras) {
      if (e.alive) e.mesh.position.copy(e.ball.pos);
    }
    // rumor de la locomotora acorde a la velocidad
    this._setRumble(this.v / TREN.vMax);
    // fundido del TÚNEL
    let top = 0;
    if (this._tunnelPhase === 'in') {
      top = Math.min(0.97, this._tunnelT2 / TREN.tunnelIn * 0.97);
    } else if (this._tunnelPhase === 'dur') top = 0.97;
    else if (this._tunnelPhase === 'out') {
      top = 0.97 * Math.max(0, 1 - this._tunnelT2 / TREN.tunnelOut);
    }
    for (const m of this.tunnelMats) m.opacity = top;
    /* v2.115 · TÚNEL DEL ARTISTA: el grupo viaja con el mundo (1,00×) y
     * la caja de oscuridad baja la luz de TODA la escena al 20 % hasta la
     * salida. Las mechas de las bombas chispean. */
    if (this.tunelGrp) {
      const viv = this._tunnelPhase !== 'none';
      this.tunelGrp.visible = viv;
      if (viv) {
        this._tunelZ += dW;
        this.tunelGrp.position.z = this._tunelZ;
      }
      let osc = 0;
      if (this._tunnelPhase === 'in') {
        osc = Math.min(1, this._tunnelT2 / TREN.tunnelIn) * TREN.tunel.oscuro;
      } else if (this._tunnelPhase === 'dur') osc = TREN.tunel.oscuro;
      else if (this._tunnelPhase === 'out') {
        osc = TREN.tunel.oscuro * Math.max(0, 1 - this._tunnelT2 / TREN.tunnelOut);
      }
      if (this.tunelOscuro) {
        this.tunelOscuro.material.opacity = osc;
        this.tunelOscuro.visible = osc > 0.01;
      }
      const fl = 0.55 + Math.random() * 0.45;
      if (this._fuseMain && this._fuseMain.visible && this._fuseMain.children[1]) {
        this._fuseMain.children[1].material.opacity = fl;
      }
      for (const e of this.extras) {
        if (e.alive && e.fuse && e.fuse.visible && e.fuse.children[1]) {
          e.fuse.children[1].material.opacity = fl;
        }
      }
    }
    /* ==== v2.112 · PORTAL de la bola: SÓLO se ve al salir la bola ====
     * _serveBall fija _portalT (tiempo visible) y el fundido corre aquí:
     * entrada 0,18 s · visible hasta agotar · salida 0,45 s. */
    if (this.portalSpin) {
      this.portalSpin.rotation.y += dt * 1.15;
      const viv = this._portalT > 0;
      this.portalGrp.visible = viv;
      if (viv) {
        this._portalT -= dt;
        this._portalK = Math.min(1, (this._portalK || 0) + dt / 0.18);
        if (this._portalT <= 0.45) {
          this._portalK = Math.max(0, this._portalT / 0.45);
        }
        const k = this._portalK;
        for (const k2 of this.portalSpin.children) {
          if (k2.material) k2.material.opacity = (k2._baseOp || 0.9) * k;
        }
      }
    }
    /* ==== v2.111 · PIRÁMIDE: pop de aparición, temblor y GRAVEDAD ==== */
    for (const rec of this.cubos) {
      if (rec.muerto) continue;
      const m = rec.mesh;
      /* v2.115 · LLUVIA DE CAJONES: caída LIBRE con colisión contra el
       * muelle y las cajas ya asentadas (se apilan o caen al suelo). Si la
       * cima queda por ENCIMA de landY: NO HAY SITIO → una caja vieja
       * EXPLOTA para hacer hueco y la nueva sigue bajando. */
      if (rec.cayendo) {
        const C = TREN.cubo, L = TREN.lluvia;
        rec.vy -= 9.81 * dt;
        m.position.y += rec.vy * dt;
        let top = -99, soporte = null;
        if (Math.abs(m.position.x) <= C.peanaW / 2 + C.size * 0.1 &&
            Math.abs(m.position.z - C.z) <= C.peanaD / 2) {
          top = C.peanaH;
        }
        for (const o of this.cubos) {
          if (o === rec || o.muerto || o.cayendo) continue;
          if (Math.abs(o.mesh.position.x - m.position.x) < C.size * 0.98 &&
              Math.abs(o.mesh.position.z - m.position.z) < C.size * 0.62) {
            const t2 = o.mesh.position.y + C.size / 2;
            if (t2 > top) { top = t2; soporte = o; }
          }
        }
        const mitad = C.size / 2;
        if (m.position.y - mitad <= top) {
          if (top > L.landY) {
            const cand = this.cubos.filter((r) => !r.muerto && !r.cayendo && r !== rec);
            if (cand.length) {
              this._revientaCubo(cand[(Math.random() * cand.length) | 0]);
            }
            m.position.y = top + mitad + 0.02;
            rec.vy = -0.4;
            continue;
          }
          m.position.y = top + mitad;
          rec.base.copy(m.position);
          rec.cayendo = false;
          rec.vy = 0;
          rec.row = soporte ? Math.min(9, soporte.row + 1) : 0;
        }
        continue;
      }
      if (rec.born > 0) {                      // pop escalonado de aparición
        rec.born -= dt;
        m.scale.setScalar(clamp(1 - rec.born / 0.16, 0.01, 1));
        continue;
      }
      if (m.scale.x < 1) m.scale.setScalar(1);
      if (rec.shakeT > 0) {                    // cajón abierto: TIEMBLA 1 s
        rec.shakeT -= dt;
        m.position.set(
          rec.base.x + (Math.random() - 0.5) * 0.02,
          rec.base.y + (Math.random() - 0.5) * 0.02,
          rec.base.z + (Math.random() - 0.5) * 0.014);
        if (rec.shakeT <= 0) {
          m.position.copy(rec.base);
          this._explotaLingote(rec);
        }
        continue;
      }
      // GRAVEDAD: sin apoyo (los dos cajones de debajo, o el muelle) CAE.
      // v2.113 · BUG DEL HUMO ETERNO: un cajón YA apoyado en su suelo se
      // re-evaluaba «sin apoyo» cada frame (apoyos muertos) → caía 2 mm,
      // aterriza, humo + 'madera'… CADA FRAME, para siempre. Ahora sólo
      // cae si de verdad hay HUECO bajo él (>2 cm): si ya toca su suelo
      // queda anclado — y si un apoyo revienta LUEGO, el hueco nuevo sí
      // lo hace caer otra vez.
      if (!rec.cae && !this._apoyado(rec)) {
        const suelo0 = this._sueloBajo(rec) + TREN.cubo.size / 2;
        if (m.position.y - suelo0 > 0.02) { rec.cae = true; rec.vy = 0; }
      }
      if (rec.cae) {
        rec.vy -= 7.5 * dt;
        const suelo = this._sueloBajo(rec) + TREN.cubo.size / 2;
        let ny = m.position.y + rec.vy * dt;
        if (ny <= suelo) {
          ny = suelo;
          rec.cae = false;
          rec.vy = 0;
          /* v2.116: fila refrescada según el APOYO REAL (cosmética: la
           * física ya no la usa) — sobre el muelle fila 0, si aterriza
           * sobre otra caja, la suya +1. */
          const sup = this._soportes(rec);
          rec.row = sup.length ? Math.min(9, sup[0].row + 1) : 0;
          this.ctrl.sfx('madera', 0);
          this.ctrl.fx.smoke(m.position, 1, false);
        }
        rec.base.y = ny;
        m.position.y = ny;
      }
    }
    /* ==== v2.111 · LINGOTES: vuelo en parábola + asentamiento en la pila ====
     * v2.113 · ROBO: fases levitación roja (0) y vuelo por la ventana (1). */
    for (let i = this.ingotes.length - 1; i >= 0; i--) {
      const it = this.ingotes[i];
      if (it.robado && it.robo !== undefined) {
        it.roboT += dt;
        const m2 = it.mesh;
        if (it.robo === 0) {
          /* LEVITA: sube 1 m sobre la mesa (frenado suave), sin parar de
           * girar y bamboleándose — IMPOSIBLE no verlo. */
          const k = Math.min(1, it.roboT / 0.9);
          const e2 = 1 - Math.pow(1 - k, 2.2);
          m2.position.set(
            it.base.x + Math.sin(it.roboT * 9) * 0.025,
            it.base.y + e2,
            it.base.z + Math.cos(it.roboT * 7.3) * 0.025);
          m2.rotation.y += it.spin * dt;
          if (k >= 1) {
            it.robo = 1; it.roboT = 0;
            this.ctrl.fx.flash(m2.position, 1.7, 0xff4030);
            this.ctrl.sfx('impacto', 0);
            /* SALE DISPARADO hacia la VENTANA del forajido que se marcha */
            const side = (this._fjState !== 'off') ? this._fjSide
              : (this._fjLastSide || (Math.random() < 0.5 ? -1 : 1));
            it.v.set(side * 7.4, 1.35,
              clamp((TREN.forajido.zAtk - m2.position.z) * 1.1, -2.4, 2.4));
            it.grav = 0;
          }
        } else {
          m2.position.addScaledVector(it.v, dt);
          m2.rotation.y += it.spin * 2.6 * dt;
          if (Math.abs(m2.position.x) > 3.28 || it.roboT > 1.4) {
            this.ctrl.fx.spark(m2.position, 8, 0xff5040, 2.2, 1);
            this.pile.remove(it.mesh);
            this.ingotes.splice(i, 1);
          }
        }
        continue;
      }
      if (!it.volando) continue;
      it.t += dt;
      it.v.y -= it.grav * dt;
      it.mesh.position.addScaledVector(it.v, dt);
      it.mesh.rotation.y += dt * 5;
      if (it.t >= it.T) {
        it.volando = false;
        if (it.robado) {
          this.ctrl.fx.spark(it.mesh.position, 6, 0xffd24a, 2, 1);
          this.pile.remove(it.mesh);
          this.ingotes.splice(i, 1);
        } else {
          it.mesh.position.copy(it.dest);
          it.mesh.rotation.set(0, it.yaw, 0);
          this.ctrl.sfx('coin', 0);
          this.ctrl.fx.spark(it.mesh.position, 8, 0xffe9a0, 2, 0.8);
          this._enLingote();
        }
      }
    }
    /* ==== v2.140 · PANEL de resultado de la estación: pop elástico ==== */
    if (this.premio) {
      this.premioT += dt;
      const k = Math.min(1, this.premioT / 0.5);
      const p = 1 - Math.pow(1 - k, 3);
      this.premio.scale.setScalar(
        Math.max(0.05, (0.2 + 0.8 * p) * (1 + Math.sin(p * Math.PI) * 0.1)));
    }
    /* ==== v2.111 · EL FORAJIDO GALOPANTE (sprite sheet + estados) ==== */
    this._fjUpdate(dt);
    /* ==== v2.119 · EL INDIO CABALGANTE (grupos 1-3, flecha ladrona) ==== */
    this._indUpdate(dt);
    this._musicSync();   // v3.6.3-SDK3: el SDK guarda si suena (no-op si no)
    if (this.ctrl.fx) this.ctrl.fx.update(dt);
  }

  /** SILBATO + TÚNEL: las ventanas se apagan y SÓLO BRILLAN LOS CANDADOS.
   *  v2.117 · el túnel NACE LEJOS (zIn = -12 m) y se VE LLEGAR: fase
   *  'pre' — la boca (3,4 m, centrada en la ventana) cruza el paisaje con
   *  luz NORMAL (el silbato avisa), la banda entra COSIDA a ella, la luz
   *  cae al 20 % y a la salida asoma la boca ESPEJADA. Transiciones POR
   *  DISTANCIA: la secuencia queda clavada a la velocidad real. */
  _tunnelStep(dt) {
    const TU = TREN.tunel;
    if (this._tunnelPhase === 'none') {
      this._tunnelT -= dt;
      /* v2.118 · el túnel SÓLO nace si la parada está LEJOS (reloj >
       * bloquea): nunca un túnel solapado con la llegada del andén. Si el
       * contador vence tarde, ESPERA — el reloj de parada se resetea a
       * 120 s en _depart y el túnel sale entonces. */
      if (this._tunnelT <= 0 && this.time > TU.bloquea) {
        this._tunnelPhase = 'pre';
        this._tunnelT2 = 0;
        this.ctrl.sfx('whistle', 0);
        this._msg = tx('tren_tunel');
        this._msgT = 2.6;
        /* v2.116 · el grupo del túnel (boca + banda + boca espejada) entra
         * EN ESCENA LEJOS y viaja con el mundo a velocidad REAL: la boca
         * se acerca, cruza la ventana y DA PASO a la oscuridad.
         * v2.117 · las transiciones pasan a ser POR DISTANCIA: la secuencia
         * boca → banda cosida → boca espejada queda clavada a la
         * velocidad real del mundo (nada de desfases por reloj). */
        this._tunelZ = TU.zIn;
        if (this.tunelGrp) {
          this.tunelGrp.position.z = this._tunelZ;
          this.tunelGrp.visible = true;
        }
      }
    } else if (this._tunnelPhase === 'pre') {
      this._tunnelT2 += dt;
      // la boca ENTRA completa (su borde trasero pasa el ojo) y a
      // continuación asoma la banda ya cosida a ella
      if (this._tunelZ >= TU.ojo + TU.bh / 2) {
        this._tunnelPhase = 'in';
        this._tunnelT2 = 0;
      }
    } else if (this._tunnelPhase === 'in') {
      this._tunnelT2 += dt;
      if (this._tunnelT2 >= TREN.tunnelIn - 1e-6) { this._tunnelPhase = 'dur'; this._tunnelT2 = 0; }
    } else if (this._tunnelPhase === 'dur') {
      this._tunnelT2 += dt;
      // el borde DELANTERO de la boca de SALIDA asoma por el cono de la
      // ventana (a TU.ver del ojo) → empieza el fundido de salida
      if (this._tunelZ >= TU.len + TU.bh / 2 - TU.ver - 1e-6) {
        this._tunnelPhase = 'out';
        this._tunnelT2 = 0;
      }
    } else if (this._tunnelPhase === 'out') {
      this._tunnelT2 += dt;
      if (this._tunnelT2 >= TREN.tunnelOut - 1e-6) {
        this._tunnelPhase = 'none';
        this._tunnelT = TREN.tunnelEvery * (0.82 + Math.random() * 0.36);
      }
    }
  }

  /* ------------------------------ bola ------------------------------------ */
  _parkBall() {
    const g = this.game;
    if (g.ball.pos.y > -3.5) {
      g.ball.pos.set(0, -4, 0);   // v2.101: fuera del teleporte de seguridad
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = false;
    }
  }
  _serveBall() {
    /* v2.112 · SAQUE DEL VÓRTICE: la bola sale del anillo con un BRINCO
     * ALTO — ápice TREN.bote.apex (1,45 m) — y a partir de ahí CADA bote
     * en la zona del jugador vuelve a subir hasta el MISMO ápice (botando
     * a una misma altura para golpearla cómodo). El vórtice SÓLO se ve al
     * salir la bola (fundido de entrada/salida en fxStep). */
    const g = this.game;
    const D = ODIMS() || { tableCenterZ: -1.6, tableHalfLength: 1.37, tableTopY: 0.76 };
    this._dead = false;
    this._floorB = 0;
    this._prevVy = 0;
    this._gastada = false; this._gastadaT = 0;   // v2.114: bola NUEVA, no gastada
    const pz = this._portalZ || (D.tableCenterZ + TREN.vortice.zRed);
    const y0 = D.tableTopY + 0.035;
    const B = TREN.bote;
    const vy0 = Math.sqrt(2 * 9.81 * Math.max(0.05, B.apex - y0)) * B.comp;
    g.ball.pos.set((Math.random() - 0.5) * 0.08, y0, pz);
    g.ball.vel.set((Math.random() - 0.5) * 0.3, vy0, B.exitVz);
    g.ball.spin.set(0, 0, 0);
    g.ballMesh.visible = true;
    this._portalT = 1.6;                       // vórtice visible AL SALIR
    this._portalK = 0;                         // fundido de entrada
    this.ctrl.sfx('lanzar', 0);
    this.ctrl.fx.flash(new THREE.Vector3(0, D.tableTopY + 0.06, pz), 1.2, 0x9ad7ff);
  }
  /** v2.113 · recalibra el bote al ÁPICE y dirige la deriva horizontal a
   *  la ZONA CÓMODA del jugador (TREN.bote.zComoda): la bola viene HACIA
   *  él tras salir del vórtice y se planta botando a su alcance. */
  _calmaBote(b, B, desdeY, targetZ) {
    b.vel.y = Math.sqrt(2 * 9.81 * Math.max(0.05, B.apex - desdeY)) * B.comp;
    b.vel.x *= 0.5;
    const dz = (targetZ || B.zComoda) - b.pos.z;
    b.vel.z = Math.abs(dz) < 0.18
      ? (Math.random() - 0.5) * 0.12           // en zona: bota en su sitio
      : clamp(dz * 1.35, -0.95, 0.95);         // camina HACIA la zona
  }
  _simBall(dt) {
    const g = this.game;
    const D = ODIMS();
    const presenting = g.renderer.xr.isPresenting;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    const pads = (presenting && ps && ps.active) ? [ps] : [];
    g.events.length = 0;
    const prevVy = g.ball.vel.y;
    stepPhysics(dt, g.ball, pads, g.events, this._extra);
    for (const e of g.events) {
      if (e.type === 'paddle') {
        this._floorB = 0;
        if (e.speed) this.ctrl.sfx('pala', 0);
      }
    }
    /* v2.113 · BOTE GESTIONADO: si la bola acaba de botar en la zona del
     * jugador (mesa, margen o suelo, vuelo lento), su vy se RECALIBRA al
     * ápice y la deriva horizontal APUNTA A LA ZONA CÓMODA (zComoda):
     * el vórtice la suelta HACIA el jugador, la bola se acerca botando y
     * se planta a su alcance esperando el golpe (arkanoi). */
    const b = g.ball;
    const B = TREN.bote;
    const bh = Math.hypot(b.vel.x, b.vel.z);
    const botMesa = prevVy < -0.5 && b.vel.y > 0 &&
      b.pos.y < D.tableTopY + 0.12;
    if (botMesa && b.pos.z > B.zonaZ && bh < B.vMaxH && !this._gastada) {
      this._calmaBote(b, B, b.pos.y);
      this._floorB = 0;   // el bote está gestionado: la espera no lo mata
    }
    /* v2.114 · BOLA GASTADA: ya golpeó la pirámide; al agotar su rebote
     * visible se retira y el vórtice saca la siguiente (TREN.respawnT). */
    if (this._gastada) {
      this._gastadaT -= dt;
      if (this._gastadaT <= 0) { this._killBall(); return; }
    }
    /* v2.134 · VIGILANTE de la CADENA de la dinamita: si la bola-bomba
     * lleva 3,2 s sin estallar (rebote imprevisto, camino raro) se
     * RE-APUNTA sola a la caja viva más cercana de su serie. */
    if (this._bomba && this._bombaSerie && this._bombaSerie.rest.size > 0) {
      this._bombaSerie.t += dt;
      if (this._bombaSerie.t > 3.2) this._bombaReapunta(g.ball, this._bombaSerie);
    }
    /* v2.134 · PARED DEL FONDO (frontal del vagón, z=-5,55): la bola que
     * sobrevuela la pirámide REBOTA en vez de morir — puede volver y
     * golpear las cajas DESDE ATRÁS (petición del dueño). */
    if (b.pos.z < TREN.paredZ + 0.02) {
      b.pos.z = TREN.paredZ + 0.02;
      if (b.vel.z < 0) this._paredRebote(b);
    }
    if (b.pos.z > 2.3 || b.pos.x > 2.7 || b.pos.x < -2.7) {
      this._killBall();
      return;
    }
    const overTable = Math.abs(b.pos.x) <= D.tableHalfWidth + 0.25 &&
      b.pos.z >= D.tableCenterZ - D.tableHalfLength - 0.25 &&
      b.pos.z <= D.tableCenterZ + D.tableHalfLength + 0.6;
    if (!overTable && b.pos.y < 0.06 && b.vel.y < 0.4) {
      this._floorB++;
      if (this._floorB >= 2) { this._killBall(); return; }
      // el bote en el suelo del vagón también sube AL MISMO ÁPICE
      b.vel.y = Math.sqrt(2 * 9.81 * Math.max(0.05, B.apex - 0.03)) * B.comp;
      b.vel.x *= 0.55; b.vel.z *= 0.55;
    }
    if (b.vel.lengthSq() < 0.09 && b.pos.y < D.tableTopY + 0.15) {
      this._deadT = (this._deadT || 0) + dt;
      if (this._deadT > 0.9) { this._deadT = 0; this._killBall(); }
    } else this._deadT = 0;
    /* v2.115 · superpoder bajo la bola principal (el mismo camino que las
     * extras) — medallón de la mesa rival rozado a baja altura. */
    this._poderToque(b);
  }
  _killBall() {
    if (this._dead) return;
    this._dead = true;
    this._deadT = 0;
    this._respawnT = TREN.respawnT;
    this.game.ballMesh.visible = false;
    /* v2.115 · la bola-bomba principal SE APAGA al morir */
    if (this._bomba) {
      this._bomba = false;
      this._bombaSerie = null;   // v2.134: la cadena muere con la bola
      this.game.ball.dragMul = 1;   // v2.134: aire NORMAL fuera de la bomba
      if (this._bombaSave && this.game.ballMesh && this.game.ballMesh.material) {
        this.game.ballMesh.material.color.setHex(this._bombaSave.col);
      }
      if (this._fuseMain) this._fuseMain.visible = false;
      this._bombaSave = null;
    }
    this._parkBall();
  }

  /* ======================================================================
   *  v2.115 · PELOTAS CADA SEGUNDO + SUPERPODERES + LLUVIA DE CAJONES
   *  ====================================================================== */
  _pads() {
    const g = this.game;
    const ps = g.controllerPaddles && g.controllerPaddles[g.paddleHand];
    return (g.renderer.xr.isPresenting && ps && ps.active) ? [ps] : [];
  }
  /** Nace una bola EXTRA en `pos` (el vórtice o el punto del X3).
   *  v2.134 · `fuerza` SALTÁ el tope de simultáneas: el X3 SACA SIEMPRE
   *  sus 3 bolas contra las cajas aunque el pool esté lleno. */
  _naceExtraEn(pos, fuerza) {
    const g = this.game;
    const D = ODIMS() || { tableCenterZ: -1.6, tableTopY: 0.76 };
    const B = TREN.bote;
    const vivas = (this._dead ? 0 : 1) +
      this.extras.filter((e) => e.alive).length;
    if (vivas >= TREN.bolas.max && !fuerza) return null;
    if (!this._extraGeo) {
      this._extraGeo = new THREE.SphereGeometry(
        ODIMS() ? ODIMS().ballRadius : 0.02, 12, 10);
    }
    // v2.120: RECAMBIO — reutiliza una bola extra muerta (mesh + material
    // propio) antes de crear una nueva: el array deja de crecer sin tope.
    let e = this.extras.find((x) => !x.alive) || null;
    if (e) {
      e.mesh.material.color.setHex(0xf3eee2);   // vuelve a crema (anti-bomba)
      e.mesh.visible = true;
      e.mesh.position.copy(pos);
      e.mesh.scale.setScalar(1);
      e.ball.pos.copy(pos);
      e.ball.vel.set(0, 0, 0);
      e.ball.spin.set(0, 0, 0);
      e.alive = true; e.gastada = false; e.gastadaT = 0;
      e.floorB = 0; e.prevVy = 0; e.deadT = 0; e.bomba = false;
      e.ball.dragMul = 1;                      // v2.134: recambio con aire NORMAL
      e.zc = 0.75 + Math.random() * 0.55;
      if (e.fuse) e.fuse.visible = false;
      e.events.length = 0;
      return e;
    }
    const mesh = new THREE.Mesh(this._extraGeo,
      (this._extraMat = this._extraMat ||
        new THREE.MeshStandardMaterial({ color: 0xf3eee2, roughness: 0.4 })).clone());
    mesh.visible = true;
    mesh.position.copy(pos);
    this.group.add(mesh);
    e = {
      ball: { pos: pos.clone(), vel: new THREE.Vector3(),
              spin: new THREE.Vector3(), ignoreNet: false, dragMul: 1 },
      mesh, alive: true, gastada: false, gastadaT: 0,
      floorB: 0, prevVy: 0, deadT: 0, bomba: false, fuse: null,
      events: [], zc: 0.75 + Math.random() * 0.55,  // zona cómoda PERSONAL
    };
    this.extras.push(e);
    return e;
  }
  /** Nacimiento en el VÓRTICE (spawner de 1 s): mismo brinco que el saque. */
  _naceExtra() {
    const D = ODIMS() || { tableCenterZ: -1.6, tableTopY: 0.76 };
    const B = TREN.bote;
    const pz = this._portalZ || (D.tableCenterZ + TREN.vortice.zRed);
    const y0 = D.tableTopY + 0.035;
    const pos = new THREE.Vector3((Math.random() - 0.5) * 0.08, y0, pz);
    const e = this._naceExtraEn(pos);
    if (!e) return null;
    const vy0 = Math.sqrt(2 * 9.81 * Math.max(0.05, B.apex - y0)) * B.comp;
    e.ball.vel.set((Math.random() - 0.5) * 0.3, vy0, B.exitVz);
    // el vórtice TAMBIÉN SE VE en cada nacimiento (fundido completo)
    this._portalT = 1.6; this._portalK = 0;
    this.ctrl.sfx('lanzar', 0);
    this.ctrl.fx.flash(new THREE.Vector3(0, D.tableTopY + 0.06, pz), 1.2, 0x9ad7ff);
    return e;
  }
  _muereExtra(e) {
    e.alive = false;
    e.mesh.visible = false;
    if (e.bomba) {
      e.bomba = false;
      e.bombaSerie = null;       // v2.134: la cadena muere con la bola
      e.ball.dragMul = 1;        // v2.134: aire NORMAL fuera de la bomba
      e.mesh.material.color.setHex(0xf3eee2);
      if (e.fuse) e.fuse.visible = false;
    }
  }
  /** Física de una bola EXTRA: la MISMA del juego (pala, cajones, arkanoi). */
  _simExtra(e, dt) {
    const D = ODIMS();
    const B = TREN.bote;
    e.events.length = 0;
    e.prevVy = e.ball.vel.y;
    stepPhysics(dt, e.ball, this._pads(), e.events, this._extra);
    for (const ev of e.events) {
      if (ev.type === 'paddle') {
        e.floorB = 0;
        if (ev.speed) this.ctrl.sfx('pala', 0);
      }
    }
    const b = e.ball;
    const bh = Math.hypot(b.vel.x, b.vel.z);
    const botMesa = e.prevVy < -0.5 && b.vel.y > 0 &&
      b.pos.y < D.tableTopY + 0.12;
    if (botMesa && b.pos.z > B.zonaZ && bh < B.vMaxH && !e.gastada) {
      this._calmaBote(b, B, b.pos.y, e.zc);
      e.floorB = 0;
    }
    if (e.gastada) {
      e.gastadaT -= dt;
      if (e.gastadaT <= 0) { this._muereExtra(e); return; }
    }
    /* v2.134 · VIGILANTE de la cadena (bolas EXTRA bomba): re-apunte
     * automático si la bola encadenada se queda sin camino. */
    if (e.bomba && e.bombaSerie && e.bombaSerie.rest.size > 0) {
      e.bombaSerie.t += dt;
      if (e.bombaSerie.t > 3.2) this._bombaReapunta(b, e.bombaSerie);
    }
    /* v2.134 · PARED DEL FONDO: las EXTRAS también rebotan (mismo trato
     * que la bola principal — pueden golpear las cajas desde atrás). */
    if (b.pos.z < TREN.paredZ + 0.02) {
      b.pos.z = TREN.paredZ + 0.02;
      if (b.vel.z < 0) this._paredRebote(b);
    }
    if (b.pos.z > 2.3 || b.pos.x > 2.7 || b.pos.x < -2.7) {
      this._muereExtra(e); return;
    }
    const overTable = Math.abs(b.pos.x) <= D.tableHalfWidth + 0.25 &&
      b.pos.z >= D.tableCenterZ - D.tableHalfLength - 0.25 &&
      b.pos.z <= D.tableCenterZ + D.tableHalfLength + 0.6;
    if (!overTable && b.pos.y < 0.06 && b.vel.y < 0.4) {
      e.floorB++;
      if (e.floorB >= 2) { this._muereExtra(e); return; }
      b.vel.y = Math.sqrt(2 * 9.81 * Math.max(0.05, B.apex - 0.03)) * B.comp;
      b.vel.x *= 0.55; b.vel.z *= 0.55;
    }
    if (b.vel.lengthSq() < 0.09 && b.pos.y < D.tableTopY + 0.15) {
      e.deadT += dt;
      if (e.deadT > 0.9) { this._muereExtra(e); return; }
    } else e.deadT = 0;
    this._poderToque(b);
  }

  /* ------------------------- superpoderes (v2.115) ------------------------ */
  _podY() {
    const D = ODIMS();
    return (D ? D.tableTopY : 0.76) + 0.012;
  }
  _buildPoderes() {
    const P = TREN.poder;
    this.pods = [];
    const defs = [
      { key: 'cajas', file: 'powerCajas.png', msg: 'tren_pcajas' },
      { key: 'x3', file: 'powerx3.png', msg: 'tren_px3' },
      { key: 'dina', file: 'powerdinamita.png', msg: 'tren_pdina' },
    ];
    for (const d of defs) {
      // reserva: disco dorado con anillo (si el arte tarda, YA se ve algo)
      const cv = oesteCanvas(128, 128);
      const c = cv.getContext('2d');
      c.fillStyle = '#e9c05a'; c.beginPath(); c.arc(64, 64, 60, 0, Math.PI * 2); c.fill();
      c.fillStyle = '#7a4f14'; c.beginPath(); c.arc(64, 64, 40, 0, Math.PI * 2); c.fill();
      const tex0 = this._ct(cv);
      const m = new THREE.Mesh(new THREE.PlaneGeometry(P.size, P.size),
        new THREE.MeshBasicMaterial({
          map: tex0, transparent: true, depthWrite: false, fog: false,
          side: THREE.DoubleSide,
        }));
      m.rotation.x = -Math.PI / 2;
      m.renderOrder = 6;
      m.position.set(0, -9, 0);
      m.visible = false;
      this.group.add(m);
      try {
        new THREE.TextureLoader().load(this._A(d.file), (t) => {
          try {
            t.colorSpace = THREE.SRGBColorSpace;
            t.anisotropy = this._aniso;
            m.material.map = t;
            m.material.needsUpdate = true;
          } catch (e) { /* disco de reserva */ }
        }, undefined, () => { /* disco de reserva */ });
      } catch (e) { /* */ }
      this.pods.push({ key: d.key, msg: d.msg, mesh: m });
    }
    this._podT = P.t1Min + Math.random() * (P.t1Max - P.t1Min);
  }
  _poderStep(dt) {
    const P = TREN.poder;
    if (this.phase !== 'run') {
      if (this._pod) { this._pod.ref.mesh.visible = false; this._pod = null; }
      return;
    }
    if (this._pod) {
      const pod = this._pod;
      pod.vida -= dt;
      pod.k = Math.min(1, (pod.k || 0) + dt / 0.22);
      if (pod.vida <= 0.4) pod.k = Math.max(0, pod.vida / 0.4);   // salida
      const m = pod.ref.mesh;
      m.visible = pod.vida > 0;
      m.scale.setScalar(0.55 + 0.45 * pod.k);
      m.position.set(pod.x, this._podY(), pod.z);
      m.rotation.z += dt * 0.8;
      if (pod.vida <= 0) {
        m.visible = false;
        this._pod = null;
        this._podT = P.restMin + Math.random() * (P.restMax - P.restMin);
      }
    } else {
      this._podT -= dt;
      if (this._podT <= 0) this._poderNace();
    }
  }
  _poderNace() {
    const P = TREN.poder;
    const ref = this.pods[(Math.random() * this.pods.length) | 0];
    const x = (Math.random() * 2 - 1) * P.x;
    const z = P.zMin + Math.random() * (P.zMax - P.zMin);
    this._pod = { ref, tipo: ref.key, x, z, vida: P.vida, k: 0 };
    ref.mesh.visible = true;
    ref.mesh.position.set(x, this._podY(), z);
    ref.mesh.scale.setScalar(0.55);
    this.ctrl.fx.flash(new THREE.Vector3(x, this._podY() + 0.05, z), 1.4, 0xffd24a);
    this.ctrl.sfx('lanzar', 0);
  }
  /** La bola (principal o extra) roza el medallón → SE ACTIVA el poder. */
  _poderToque(b) {
    const P = TREN.poder;
    if (!this._pod) return;
    const yTop = this._podY() + P.alto;
    if (b.pos.y > yTop) return;
    const dx = b.pos.x - this._pod.x, dz = b.pos.z - this._pod.z;
    if (dx * dx + dz * dz > P.trigoR * P.trigoR) return;
    const tipo = this._pod.tipo;
    this._pod.ref.mesh.visible = false;
    this._pod = null;
    this._podT = P.restMin + Math.random() * (P.restMax - P.restMin);
    this.ctrl.fx.flash(b.pos.clone(), 1.8, 0xffd24a);
    this.ctrl.sfx('impacto', 0);
    if (tipo === 'cajas') {
      this._msg = tx('tren_pcajas'); this._msgT = 1.8;
      this._lluviaCajas();
    } else if (tipo === 'x3') {
      this._msg = tx('tren_px3'); this._msgT = 1.8;
      this._tripleBola(b);
    } else {
      this._msg = tx('tren_pdina'); this._msgT = 1.8;
      this._hazBomba(b);
    }
  }
  /** POWERCAJAS: lluvia de n cajones sobre la pirámide (con física). */
  _lluviaCajas() {
    const C = TREN.cubo, L = TREN.lluvia, P = TREN.poder;
    const vivos = () => this.cubos.filter((r) => !r.muerto).length;
    // MÁX 30 cajones: si no caben, algunas VIEJAS EXPLOTAN para hacer sitio
    let sitio = vivos() + L.n - L.max;
    while (sitio-- > 0) {
      const cand = this.cubos.filter((r) => !r.muerto);
      if (!cand.length) break;
      this._revientaCubo(cand[(Math.random() * cand.length) | 0]);
    }
    for (let i = 0; i < L.n; i++) {
      const isLing = Math.random() < P.pLingote;
      const tipo = isLing ? 1 + ((Math.random() * 2) | 0)
                          : 1 + ((Math.random() * 3) | 0);
      const mesh = new THREE.Mesh(this._cuboGeo,
        isLing ? this._matLingote[tipo - 1] : this._matCubo[tipo - 1]);
      const x = (Math.random() * 2 - 1) * L.x;
      const z = C.z + (Math.random() - 0.5) * 2 * L.zJit;
      mesh.position.set(x, L.y0 + i * 0.14, z);
      this.piramide.add(mesh);
      this.cubos.push({
        mesh, row: 0, i: -1, tipo,
        base: new THREE.Vector3(x, L.y0 + i * 0.14, z),
        lingote: isLing, abierto: false, muerto: false,
        cae: false, vy: 0, shakeT: 0, born: 0,
        cayendo: true,          // v2.115: caída LIBRE hasta asentarse
      });
    }
    this.ctrl.sfx('madera', 0);
  }
  /** POWERX3 (v2.134 · «ASEGURA LOS IMPACTOS»): las 3 bolas SALEN con
   *  TIRO BALÍSTICO contra cajas apiladas REALES de la pirámide (vivas,
   *  asentadas, sin candado abierto) repartidas izquierda·centro·derecha
   *  — cada bola vuela a SU caja y el impacto queda asegurado. Si no hay
   *  apiladas (pirámide recién vaciada) apuntan al centro del muelle,
   *  donde la siguiente pirámide está a punto de nacer. */
  _tripleBola(b) {
    const g = this.game;
    const C = TREN.cubo;
    const apiladas = this.cubos
      .filter((r) => !r.muerto && !r.cayendo && !r.abierto)
      .sort((p, q) => p.mesh.position.x - q.mesh.position.x);
    const pool = apiladas.slice();
    const objs = [];
    for (const ax of [-0.62, 0, 0.62]) {          // abanico: izq · centro · der
      if (!pool.length) break;
      let bi = 0, bd = 1e9;
      for (let i = 0; i < pool.length; i++) {
        const d = Math.abs(pool[i].mesh.position.x - ax);
        if (d < bd) { bd = d; bi = i; }
      }
      objs.push(pool.splice(bi, 1)[0]);
    }
    for (let i = 0; i < 3; i++) {
      const e = this._naceExtraEn(b.pos, true);   // el X3 SACA SIEMPRE 3
      if (!e) break;
      /* v2.134 · BOLAS DE PLOMO del X3 (receta v2.102 de la bomba del
       * asedio): dragMul 0.30 — cortan el aire y el tiro balístico llega
       * al cajón (el drag normal se comía ~30 % de la velocidad en el
       * vuelo y las 3 bolas caían CORTAS sin tocar la pirámide). */
      e.ball.dragMul = 0.30;
      const rec = objs[i % Math.max(1, objs.length)];
      const dest = rec ? rec.mesh.position
        : new THREE.Vector3((i - 1) * 0.55, C.peanaH + C.size, C.z);
      const T = 0.52 + i * 0.09;                  // escalonadas (ola)
      this._apuntaBalistica(e.ball, dest, T);
    }
    if (b === g.ball) this._killBall();       // la original DESAPARECE
    else {
      const e0 = this.extras.find((x) => x.ball === b);
      if (e0) this._muereExtra(e0);
    }
  }
  /** v2.134 · TIRO BALÍSTICO: velocidad para llegar a `dest` en `T` s con
   *  gravedad real (misma receta del lingote: vy = Δy/T + ½gT). Se apunta
   *  al CENTRO del cajón — la esfera de impacto (r≈0,235) perdona el
   *  rozamiento del vuelo, así el choque está asegurado. */
  _apuntaBalistica(ball, dest, T) {
    const G = 10.2;                    // 9,81 + compensación del roz del núcleo
    ball.vel.set(
      (dest.x - ball.pos.x) / T,
      (dest.y - ball.pos.y + 0.5 * G * T * T) / T,
      (dest.z - ball.pos.z) / T);
  }
  /** v2.134 · La caja viva más cercana de la serie (para re-apuntar). */
  _bombaCajaVivaDe(serie, pos) {
    let best = null, bd = 1e9;
    for (const o of serie.rest) {
      if (o.muerto || o.abierto) continue;
      const d = o.mesh.position.distanceTo(pos);
      if (d < bd) { bd = d; best = o; }
    }
    return best;
  }
  /** v2.134 · Re-apunte de la bola-bomba (vigilante anti-atasco): tiro
   *  balístico a la caja viva más cercana y el reloj de la serie a cero. */
  _bombaReapunta(ball, serie) {
    const rec = this._bombaCajaVivaDe(serie, ball.pos);
    if (!rec) { serie.rest.clear(); return; }
    const T = clamp(0.42 + ball.pos.distanceTo(rec.mesh.position) * 0.075, 0.42, 0.9);
    this._apuntaBalistica(ball, rec.mesh.position, T);
    serie.t = 0;
  }
  /** POWERDINAMITA (v2.134 · CADENA DE EXPLOSIONES): la bola se vuelve la
   *  BOLA-BOMBA del asedio (oscura con mecha encendida) y su SERIE toma
   *  la foto de las cajas ACTIVAS en ese momento. Ya no muere en la
   *  primera detonación: ESTALLA SIEMPRE que toca caja, rebota y sale
   *  CAZANDO la caja viva más cercana hasta agotar TODAS las de la foto
   *  (petición literal del dueño: «una secuencia de explosiones que acaban
   *  con todas las cajas activas en ese momento»). */
  _bombaMake(mesh) {
    const fuse = new THREE.Group();
    const rope = new THREE.Mesh(new THREE.CylinderGeometry(0.0035, 0.0055, 0.052, 6),
      new THREE.MeshBasicMaterial({ color: 0x2e2114 }));
    rope.position.set(0, 0.02, 0);
    rope.rotation.z = 0.42;
    fuse.add(rope);
    const spark = new THREE.Sprite(new THREE.SpriteMaterial({
      map: (this.ctrl.fx && this.ctrl.fx.texDot) || null, color: 0xffb25a,
      transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending,
      depthWrite: false,
    }));
    spark.scale.setScalar(0.06);
    spark.position.set(-0.0105, 0.0475, 0);
    fuse.add(spark);
    fuse.visible = false;
    mesh.add(fuse);
    return fuse;
  }
  _hazBomba(b) {
    const g = this.game;
    /* v2.134 · la SERIE de la cadena: FOTO de las cajas activas en el
     * momento del poder — la bola no descansará hasta agotarlas. */
    const serie = {
      rest: new Set(this.cubos.filter((r) => !r.muerto && !r.abierto)),
      t: 0,
    };
    if (b === g.ball) {
      this._bomba = true;
      this._bombaSerie = serie;
      g.ball.dragMul = 0.30;     // v2.134: la bomba del tren PESA (v2.102)
      if (g.ballMesh && g.ballMesh.material) {
        if (!this._bombaSave) {
          const mm = g.ballMesh.material;
          this._bombaSave = { col: mm.color.getHex() };
        }
        g.ballMesh.material.color.setHex(0x181310);
      }
      if (!this._fuseMain && g.ballMesh) this._fuseMain = this._bombaMake(g.ballMesh);
      if (this._fuseMain) this._fuseMain.visible = true;
    } else {
      const e = this.extras.find((x) => x.ball === b);
      if (e) {
        if (!e.fuse) e.fuse = this._bombaMake(e.mesh);
        e.bomba = true;
        e.bombaSerie = serie;
        e.ball.dragMul = 0.30;   // v2.134: bomba pesada también en extras
        e.mesh.material.color.setHex(0x181310);
        if (e.fuse) e.fuse.visible = true;
      }
    }
  }
  /** BOOM de la bola-bomba (v2.134 · CADENA): revienta el cajón impactado
   *  + TODOS los del radio y — si quedan cajas de la SERIE — la bola
   *  SOBREVIVE, rebota y sale CAZANDO la caja viva más cercana con tiro
   *  balístico. Cuando la serie se agota: brote final y la bola se
   *  consume (la secuencia acaba con TODAS las cajas activas). */
  _explotaBomba(recImp, ball) {
    const g = this.game;
    const R = 0.65;                       // radio de metralla (m)
    this.ctrl.fx.flash(recImp.mesh.position, 2.4, 0xffb45f);
    this.ctrl.fx.spark(recImp.mesh.position, 16, 0xffcf7a, 4.0, 1.5);
    this.ctrl.fx.smoke(recImp.mesh.position, 3, true);
    this.ctrl.sfx('boom', 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.9, 200);
    for (const o of this.cubos) {
      if (o === recImp || o.muerto) continue;
      if (o.mesh.position.distanceTo(recImp.mesh.position) <= R) {
        this._golpeCubo(o);
      }
    }
    const esMain = ball === this.game.ball;
    const serie = esMain ? this._bombaSerie
      : ((this.extras.find((x) => x.ball === ball) || {}).bombaSerie || null);
    if (serie) {
      serie.rest.delete(recImp);
      for (const o of serie.rest) {
        if (o.muerto || o.abierto) serie.rest.delete(o);   // resueltas fuera
      }
      if (serie.rest.size > 0) {
        /* la bola SIGUE VIVA: sale cazando la caja viva más cercana */
        this._bombaReapunta(ball, serie);
        return;
      }
    }
    /* cadena completa (o serie perdida): BROTE FINAL y la bola se consume */
    this.ctrl.fx.flash(ball.pos.clone(), 1.6, 0xffb45f);
    this.ctrl.fx.smoke(ball.pos.clone(), 1, true);
    if (esMain) this._killBall();
    else {
      const e = this.extras.find((x) => x.ball === ball);
      if (e) this._muereExtra(e);
    }
  }

  /* ------------------------- colisionador extra --------------------------- */
  /** v2.134 · REBOTE en la PARED DEL FONDO del vagón (el frontal): golpe
   *  seco de madera + chispazo de polvo. La bola queda viva y vuelve hacia
   *  la pirámide — puede golpear las cajas desde atrás. */
  _paredRebote(b) {
    b.vel.z = -b.vel.z * TREN.paredRebote;
    b.vel.x *= 0.92;
    const p = b.pos.clone();
    p.y = Math.max(0.12, p.y); p.z = TREN.paredZ + 0.05;
    this.ctrl.fx.spark(p, 6, 0xd9c39a, 1.7, 0.8);
    this.ctrl.sfx('madera', 0);
  }
  _collide(ball) {
    /* v2.111 · bola vs CAJONES de la pirámide (esfera generosa por cajón,
     * rebote arkanoid y regla del candado-lingote).
     * v2.115 · la MISMA colisión sirve para las bolas EXTRA del pool y
     * para la BOLA-BOMBA (revienta el cajón y su alrededor). */
    if (this.phase !== 'run') return;
    const C = TREN.cubo;
    const r = (ODIMS() ? ODIMS().ballRadius : 0.02) + C.size / 2 + C.hitBoost;
    const p = ball.pos;
    const esMain = ball === this.game.ball;
    const holder = esMain ? null
      : (this.extras.find((x) => x.ball === ball) || null);
    const esBomba = esMain ? !!this._bomba : !!(holder && holder.bomba);
    for (const rec of this.cubos) {
      if (rec.muerto || rec.abierto) continue;   // abiertos: ya gastados
      const mp = rec.mesh.position;
      const dx = p.x - mp.x, dy = p.y - mp.y, dz = p.z - mp.z;
      if (dx * dx + dy * dy + dz * dz >= r * r) continue;
      const d = Math.max(0.02, Math.sqrt(dx * dx + dy * dy + dz * dz));
      const nX = dx / d, nY = dy / d, nZ = dz / d;
      p.x = mp.x + nX * r;
      p.y = mp.y + nY * r;
      p.z = mp.z + nZ * r;
      const dot = ball.vel.x * nX + ball.vel.y * nY + ball.vel.z * nZ;
      ball.vel.x -= 2 * dot * nX * 0.58;
      ball.vel.y -= 2 * dot * nY * 0.58;
      ball.vel.z -= 2 * dot * nZ * 0.58;
      this._golpeCubo(rec);
      if (esBomba) { this._explotaBomba(rec, ball); return; }
      /* v2.114 · LA BOLA ENTREGÓ SU GOLPE en la pirámide: queda GASTADA —
       * rebota visible un momento y se RETIRA SOLA para que el vórtice
       * saque OTRA enseguida (las bolas salen con más frecuencia). */
      if (esMain) { this._gastada = true; this._gastadaT = 1.5; }
      else if (holder) { holder.gastada = true; holder.gastadaT = 1.5; }
      break;
    }
  }

  /** RUMOR de la locomotora: ruido grave en bucle (volumen con la marcha). */
  _startRumble() {
    try {
      const A = this.game.audio;
      if (!A || !A.ctx || A.ctx.state !== 'running' || this._rumble) return;
      const ctx = A.ctx;
      const len = 1.6;
      const buf = ctx.createBuffer(1, ctx.sampleRate * len, ctx.sampleRate);
      const d = buf.getChannelData(0);
      let last = 0;
      for (let i = 0; i < d.length; i++) {
        const white = Math.random() * 2 - 1;
        last = (last + 0.035 * white) / 1.035;   // brown noise
        d[i] = last * 5.2;
      }
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = true;
      const lp = ctx.createBiquadFilter();
      lp.type = 'lowpass';
      lp.frequency.value = 130;
      const gain = ctx.createGain();
      gain.gain.value = 0.05;
      src.connect(lp); lp.connect(gain); gain.connect(ctx.destination);
      src.start();
      this._rumble = { src, gain };
    } catch (e) { this._rumble = null; }
  }
  _setRumble(k) {
    if (!this._rumble) return;
    try {
      this._rumble.gain.gain.value = 0.045 + 0.085 * clamp(k, 0, 1);
    } catch (e) { /* */ }
  }
  _stopRumble() {
    if (!this._rumble) return;
    try { this._rumble.src.stop(); } catch (e) { /* */ }
    try { this._rumble.gain.disconnect(); } catch (e) { /* */ }
    this._rumble = null;
  }

  /* ======================================================================
   *  v2.113 · SONIDOS PROPIOS DE LA ETAPA (Web Audio en crudo, el mismo
   *  camino del rumor de la locomotora — sin depender del mapa sfx).
   *  ====================================================================== */
  _sndCtx() {
    try {
      const A = this.game.audio;
      const ctx = A && A.ctx;
      return (ctx && ctx.state === 'running') ? ctx : null;
    } catch (e) { return null; }
  }
  /** v2.113 · «¡YIHAAAA!» del forajido al ENTRAR en escena: alerta sonora
   *  de aproximación. Grito de vaquero sintetizado: un "yi" corto que
   *  SUBE y una "haaa" larga que CAE, con vibrato y dos formantes de voz
   *  (pasa-banda 760/1350 Hz) sobre una sierra. FUERTE (gana al rumor). */
  _sndYihha() {
    const ctx = this._sndCtx();
    if (!ctx) return;
    try {
      const t0 = ctx.currentTime;
      const out = ctx.createGain();
      out.gain.setValueAtTime(0.0001, t0);
      out.gain.exponentialRampToValueAtTime(0.55, t0 + 0.07);
      out.gain.setValueAtTime(0.55, t0 + 0.88);
      out.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.28);
      const osc = ctx.createOscillator();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(300, t0);
      osc.frequency.linearRampToValueAtTime(655, t0 + 0.15);   // ¡YI!
      osc.frequency.setValueAtTime(655, t0 + 0.15);
      osc.frequency.linearRampToValueAtTime(470, t0 + 0.3);    // transición
      osc.frequency.setValueAtTime(470, t0 + 0.3);
      osc.frequency.linearRampToValueAtTime(295, t0 + 1.05);   // HAAAA...
      const vib = ctx.createOscillator();
      vib.frequency.value = 6.4;
      const vibG = ctx.createGain();
      vibG.gain.value = 24;
      vib.connect(vibG); vibG.connect(osc.frequency);
      const f1 = ctx.createBiquadFilter();
      f1.type = 'bandpass'; f1.frequency.value = 760; f1.Q.value = 1.1;
      const f2 = ctx.createBiquadFilter();
      f2.type = 'bandpass'; f2.frequency.value = 1350; f2.Q.value = 2.2;
      const g2 = ctx.createGain(); g2.gain.value = 0.55;
      osc.connect(f1); f1.connect(out);
      osc.connect(f2); f2.connect(g2); g2.connect(out);
      out.connect(ctx.destination);
      osc.start(t0); vib.start(t0);
      osc.stop(t0 + 1.32); vib.stop(t0 + 1.32);
      osc.onended = () => { try { out.disconnect(); } catch (e) { /* */ } };
    } catch (e) { /* el sonido nunca rompe el frame */ }
  }
  /** v2.113 · ZUMBIDO de ESCAPATORIA: suena cuando el forajido roba un
   *  lingote — zumbido grave que VIBRA durante la levitación y SUBE de
   *  golpe (bip-bip de huida) cuando el oro sale disparado por la
   *  ventana. Dos osciladores desafinados (batido) + barrido final. */
  _sndZumbido() {
    const ctx = this._sndCtx();
    if (!ctx) return;
    try {
      const t0 = ctx.currentTime;
      const g = ctx.createGain();
      g.gain.setValueAtTime(0.0001, t0);
      g.gain.exponentialRampToValueAtTime(0.3, t0 + 0.06);
      g.gain.setValueAtTime(0.3, t0 + 0.9);
      g.gain.exponentialRampToValueAtTime(0.0001, t0 + 1.5);
      const lp = ctx.createBiquadFilter();
      lp.type = 'lowpass'; lp.frequency.value = 1500; lp.Q.value = 1.6;
      const sweep = (type, f0, det) => {
        const o = ctx.createOscillator();
        o.type = type;
        o.frequency.setValueAtTime(f0, t0);
        o.frequency.linearRampToValueAtTime(f0 * 1.45, t0 + 0.9);   // levita
        o.frequency.exponentialRampToValueAtTime(f0 * 5.2, t0 + 1.26); // ¡huida!
        o.frequency.exponentialRampToValueAtTime(f0 * 2.1, t0 + 1.5);
        o.detune.value = det;
        return o;
      };
      const o1 = sweep('sawtooth', 96, 0);
      const o2 = sweep('square', 99, 34);
      const g2 = ctx.createGain(); g2.gain.value = 0.4;
      o1.connect(lp); o2.connect(g2); g2.connect(lp);
      lp.connect(g); g.connect(ctx.destination);
      o1.start(t0); o2.start(t0);
      o1.stop(t0 + 1.55); o2.stop(t0 + 1.55);
      o1.onended = () => { try { g.disconnect(); } catch (e) { /* */ } };
    } catch (e) { /* el sonido nunca rompe el frame */ }
  }

  dispose() {
    const g = this.game;
    this._stopRumble();
    this._musicStop();                 // v2.111: fuera la música del vagón
    // v2.111: restaurar el FONDO del salón
    if (this._bgWas !== undefined) {
      g.scene.background = this._bgWas;
      this._bgWas = undefined;
    }
    // v2.109: restaurar el FAR de la cámara
    if (this._farWas && g.camera) {
      g.camera.far = this._farWas;
      g.camera.updateProjectionMatrix();
    }
    this._clearPiramide();
    this._limpiaPila();
    if (this.group) {
      g.rig.remove(this.group);
      this._disposeTree(this.group);
      this.group = null;
    }
    if (this._hud) {
      // v2.120: cierre completo (textura/material/geometría incluidos)
      if (typeof this._hud.dispose === 'function') this._hud.dispose();
      else {
        this._hud.hide();
        if (this._hud.group) { g.rig.remove(this._hud.group); }
      }
    }
    this.done = true;
  }
  _disposeTree(o) {
    o.traverse((n) => {
      if (n.geometry) n.geometry.dispose();
      if (n.material) {
        const mats = Array.isArray(n.material) ? n.material : [n.material];
        for (const mm of mats) { if (mm.map) mm.map.dispose(); mm.dispose(); }
      }
    });
  }
}

/* ============================================================================
 *  v2.94 · HUD de las PRUEBAS (asedio/tren): banda de madera arriba con el
 *  RELOJ grande, el progreso y el mensaje del momento. Canvas pintado SOLO
 *  cuando cambia (HUD sucio) — cero coste por frame en la Quest.
 *  ============================================================================ */
class HudOeste {
  constructor(ctrl) {
    this.ctrl = ctrl;
    this.game = ctrl.game;
    this.cv = oesteCanvas(640, 280);   // v2.118: 280 px — banderín de 2 líneas
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    this.group = new THREE.Group();
    const mat = new THREE.MeshBasicMaterial({
      map: this.tex, transparent: true, depthWrite: false,
    });
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(1.12, 1.12 * 280 / 640), mat);
    this.group.add(plane);
    /* v2.118 · y 2,52 (antes 2,36): el cartel 3D de oleada (y 1,38) ya no
     * alcanza al HUD — antes su borde superior cubría el banderín de
     * mensajes (textos solapados). Techo del vagón a 2,85: cabe. */
    this.group.position.set(0, 2.52, -2.55);
    this.group.visible = false;
    this._dirty = true;
    this.time = 0;
    this.prog = '';
    this.msg = '';
    this.ling = null;
    this.plateImg = null;
    this.marc = null;          // v2.116: marcador de forajidos (asedio)
    this.cntImg = null;        // contador.png del artista (se perdió y se regeneró)
    this.pts = -1;             // v2.119: PUNTOS del campeonato (chip dorado)
    this._lastSec = -1;
    this._lastLing = '';
    this._lastMarc = '';
    // v2.111 · placa del BOTÍN (ligotes.png del artista): contador de
    // lingotes «X / Y» en la esquina superior izquierda del visor.
    try {
      const im = new Image();
      im.onload = () => { this.plateImg = im; this._dirty = true; };
      im.onerror = () => { this.plateImg = null; };
      im.src = (this.ctrl.manifest && this.ctrl.manifest.ligotesUrl) ||
        new URL('./assets/ligotes.png', import.meta.url).href;
    } catch (e) { this.plateImg = null; }
    // v2.116 · MARCADOR del ASEDIO (contador.png): forajidos que FALTAN
    // por matar en la oleada (3/5/7), esquina superior izquierda.
    try {
      const cm = new Image();
      cm.onload = () => { this.cntImg = cm; this._dirty = true; };
      cm.onerror = () => { this.cntImg = null; };
      cm.src = (this.ctrl.manifest && this.ctrl.manifest.contadorUrl) ||
        new URL('./assets/contador.png', import.meta.url).href;
    } catch (e) { this.cntImg = null; }
    // v2.117 · RELOJ DE LA OLEADA (reloj.png del artista): reloj de arena
    // TEÑIDO de marrón (el arte es blanco con alfa) para leerse sobre la
    // banda de madera — se pinta JUNTO al cartel del marcador del asedio.
    this.relojImg = null;
    try {
      const ri = new Image();
      ri.onload = () => {
        try {
          const rc = document.createElement('canvas');
          rc.width = 128; rc.height = 128;
          const rcx = rc.getContext('2d');
          rcx.drawImage(ri, 0, 0, 128, 128);
          rcx.globalCompositeOperation = 'source-in';
          rcx.fillStyle = '#3d2708';
          rcx.fillRect(0, 0, 128, 128);
          this.relojImg = rc;
        } catch (e0) { this.relojImg = null; }
        this._dirty = true;
      };
      ri.onerror = () => { this.relojImg = null; };
      ri.src = new URL('./assets/reloj.png', import.meta.url).href;
    } catch (e) { this.relojImg = null; }
    this.game.rig.add(this.group);
  }
  show() { this.group.visible = true; this._dirty = true; }
  hide() { this.group.visible = false; }
  /** v2.120 · CIERRE DEL HUD: libera textura/material/geometría GPU (antes
   *  el teardown sólo retiraba el grupo y la VRAM de cada rejugada
   *  quedaba filtrada hasta cerrar la pestaña). */
  dispose() {
    const g = this.game;
    this.hide();
    if (this.group && g) g.rig.remove(this.group);
    try {
      this.group.traverse((o) => {
        if (o.geometry) o.geometry.dispose();
        if (o.material) {
          if (o.material.map && o.material.map !== this.tex) o.material.map.dispose();
          o.material.dispose();
        }
      });
    } catch (e) { /* cierre defensivo */ }
    if (this.tex) { this.tex.dispose(); this.tex = null; }
    this.group = null;
  }
  set(time, prog, msg, ling, marc, pts) {
    if (prog !== undefined && prog !== null && prog !== this.prog) {
      this.prog = prog; this._dirty = true;
    }
    if (msg !== undefined && msg !== this.msg) { this.msg = msg; this._dirty = true; }
    // v2.111: contador de lingotes {n, m} — repinta si cambia
    if (ling) {
      const key = ling.n + '/' + ling.m;
      if (key !== this._lastLing) { this._lastLing = key; this.ling = ling; this._dirty = true; }
      // v2.117: la placa del tren y el marcador del asedio son EXCLUYENTES
      if (this.marc) { this.marc = null; this._dirty = true; }
    }
    // v2.116: marcador de forajidos {n, m} — repinta si cambia
    if (marc !== undefined) {
      const key = marc ? (marc.n + '/' + marc.m) : '';
      if (key !== this._lastMarc) { this._lastMarc = key; this.marc = marc; this._dirty = true; }
      if (marc && this.ling) { this.ling = null; this._dirty = true; }
    }
    // v2.119: PUNTOS del campeonato — repinta si cambian
    if (pts !== undefined) {
      const p = pts | 0;
      if (p !== this.pts) { this.pts = p; this._dirty = true; }
    }
    this.time = time;
    const sec = Math.max(0, Math.ceil(time));
    if (sec !== this._lastSec) { this._lastSec = sec; this._dirty = true; }
    if (this._dirty) this._paint();
  }
  _paint() {
    this._dirty = false;
    const cv = this.cv, c = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    c.clearRect(0, 0, W, H);
    // banda de madera curvada
    c.fillStyle = 'rgba(38,24,10,0.82)';
    c.beginPath();
    c.moveTo(8, 10); c.lineTo(W - 8, 10); c.lineTo(W - 8, 108);
    c.quadraticCurveTo(W / 2, 150, 8, 108); c.closePath(); c.fill();
    c.strokeStyle = '#c89b4a'; c.lineWidth = 5;
    c.stroke();
    /* v2.119 · CHIP DE PUNTOS (arriba a la DERECHA, línea propia sobre el
     * progreso): estrella dorada pequeña + puntería acumulada — coherente
     * con el RANKING. El progreso («OLEADA n/3» / «PARADA n/3») sigue en
     * SU línea (y 66): sin solapes. */
    if (this.pts >= 0) {
      const pTxt = String(this.pts);
      c.font = 'bold 24px Georgia, serif';
      c.textAlign = 'right';
      c.textBaseline = 'alphabetic';
      const tw = (c.measureText(pTxt).width || pTxt.length * 13);
      const tx = W - 26, ty = 41;
      c.strokeStyle = '#1a0e04'; c.lineWidth = 5;
      c.fillStyle = '#f6e3b0';
      c.strokeText(pTxt, tx, ty);
      c.fillText(pTxt, tx, ty);
      c.save();
      c.translate(tx - tw - 16, 32);
      c.beginPath();
      for (let i = 0; i < 10; i++) {
        const r = i % 2 === 0 ? 15 : 6.8;
        const a = -Math.PI / 2 + i * Math.PI / 5;
        if (i === 0) c.moveTo(Math.cos(a) * r, Math.sin(a) * r);
        else c.lineTo(Math.cos(a) * r, Math.sin(a) * r);
      }
      c.closePath();
      c.fillStyle = '#ffd24a';
      c.fill();
      c.strokeStyle = '#3d2708'; c.lineWidth = 2.5;
      c.stroke();
      c.restore();
      c.textAlign = 'center';
    }
    // v2.111 · CONTADOR DE LINGOTES (esquina superior izquierda): la placa
    // ligotes.png del artista con la cuenta «X / Y» encima.
    if (this.ling && this.ling.m > 0) {
      const pw = 190, ph = 95;
      if (this.plateImg) {
        try { c.drawImage(this.plateImg, 12, 8, pw, ph); } catch (e) { /* */ }
      } else {
        c.fillStyle = 'rgba(246,238,220,0.94)';
        c.beginPath();
        if (c.roundRect) c.roundRect(12, 8, pw, ph, 18); else c.rect(12, 8, pw, ph);
        c.fill();
        c.strokeStyle = '#4a2f14'; c.lineWidth = 6;
        c.stroke();
      }
      c.textAlign = 'center';
      c.textBaseline = 'alphabetic';
      c.fillStyle = '#3d2708';
      c.font = 'bold 52px Georgia, serif';
      const txt = this.ling.n + ' / ' + this.ling.m;
      c.strokeStyle = 'rgba(255,250,235,0.9)'; c.lineWidth = 6;
      c.strokeText(txt, 128, 74);
      c.fillText(txt, 128, 74);
    } else if (this.marc && this.marc.m > 0) {
      /* v2.117 · MARCADOR DEL ASEDIO con el arte REAL del artista:
       * contador.png (carta pergamino con el forajido) arriba a la
       * IZQUIERDA; los que FALTAN por matar se pintan en la ZONA LIBRE
       * de la carta — «N» grande y «DE M» debajo — y JUNTO al cartel el
       * RELOJ de la oleada (reloj.png) con el tiempo restante al lado. */
      const pw = 190, ph = 95;
      if (this.cntImg) {
        try { c.drawImage(this.cntImg, 12, 8, pw, ph); } catch (e) { /* */ }
      } else {
        c.fillStyle = 'rgba(246,238,220,0.94)';
        c.beginPath();
        if (c.roundRect) c.roundRect(12, 8, pw, ph, 18); else c.rect(12, 8, pw, ph);
        c.fill();
        c.strokeStyle = '#4a2f14'; c.lineWidth = 6;
        c.stroke();
      }
      c.textAlign = 'center';
      c.textBaseline = 'alphabetic';
      // cuenta en la zona libre de la carta (derecha del forajido)
      c.fillStyle = '#3d2708';
      c.strokeStyle = 'rgba(255,250,235,0.85)'; c.lineWidth = 5;
      c.font = 'bold 48px Georgia, serif';
      const sN = String(Math.max(0, this.marc.n));
      c.strokeText(sN, 134, 66);
      c.fillText(sN, 134, 66);
      c.font = 'bold 21px Georgia, serif';
      const sM = 'DE ' + this.marc.m;
      c.strokeText(sM, 134, 90);
      c.fillText(sM, 134, 90);
      // RELOJ de la oleada, junto al cartel: icono + tiempo restante
      if (this.relojImg) {
        try { c.drawImage(this.relojImg, 214, 32, 48, 48); } catch (e) { /* */ }
      } else {
        c.beginPath(); c.arc(238, 56, 24, 0, Math.PI * 2);
        c.strokeStyle = '#3d2708'; c.lineWidth = 5; c.stroke();
      }
      const mm2 = Math.floor(Math.max(0, this.time) / 60);
      const ss2 = Math.floor(Math.max(0, this.time) % 60);
      const urg2 = this.time <= 20;
      c.font = 'bold 40px Georgia, serif';
      c.strokeStyle = '#1a0e04'; c.lineWidth = 6;
      c.fillStyle = urg2 ? '#ff6a4a' : '#f6e3b0';
      const tTxt2 = mm2 + ':' + String(ss2).padStart(2, '0');
      c.textAlign = 'left';
      c.strokeText(tTxt2, 274, 70);
      c.fillText(tTxt2, 274, 70);
      c.textAlign = 'center';
    }
    // reloj central (v2.117: SÓLO en el TREN — en el asedio el reloj de
    // la oleada vive JUNTO al cartel del marcador, petición del artista)
    if (!(this.marc && this.marc.m > 0)) {
      const mm = Math.floor(Math.max(0, this.time) / 60);
      const ss = Math.floor(Math.max(0, this.time) % 60);
      const urg = this.time <= 20;
      c.textAlign = 'center';
      c.fillStyle = urg ? '#ff6a4a' : '#f6e3b0';
      c.font = 'bold 64px Georgia, serif';
      c.strokeStyle = '#1a0e04'; c.lineWidth = 7;
      const tTxt = mm + ':' + String(ss).padStart(2, '0');
      c.strokeText(tTxt, W / 2, 84);
      c.fillText(tTxt, W / 2, 84);
    }
    // progreso (derecha)
    c.textAlign = 'right';
    c.fillStyle = '#e8c87a';
    c.font = 'bold 30px Georgia, serif';
    c.strokeText(this.prog || '', W - 26, 66);
    c.fillText(this.prog || '', W - 26, 66);
    // v2.118 · mensaje (banderín bajo la banda): los textos LARGOS se
    // salían del plano y se leían cortados — ahora se ENVUELVEN a 2 líneas
    // con auto-ajuste de fuente (31→28→25→22 px) y el banderín crece.
    if (this.msg) {
      c.textAlign = 'center';
      c.textBaseline = 'alphabetic';
      const maxW = W - 80;
      let fs = 22, lines = null;
      for (const f of [31, 28, 25, 22]) {
        c.font = 'bold ' + f + 'px Georgia, serif';
        const ls = this._wrapMsg(c, this.msg, maxW);
        if (ls.length <= 2) { fs = f; lines = ls; break; }
      }
      if (!lines) lines = [this.msg];
      const two = lines.length > 1;
      const wMax = Math.max.apply(null,
        lines.map((s) => c.measureText(s).width));
      const wTxt = Math.min(W - 40, wMax + 48);
      const x0 = (W - wTxt) / 2;
      const yTop = 130;
      let yBot, bases;
      if (two) {
        const b1 = yTop + 30, b2 = b1 + fs + 5;
        yBot = b2 + 10; bases = [b1, b2];
      } else {
        yBot = yTop + 48; bases = [yTop + 35];
      }
      const yTip = yBot + 28;
      c.fillStyle = 'rgba(140,47,30,0.88)';
      c.beginPath();
      c.moveTo(x0, yTop); c.lineTo(x0 + wTxt, yTop); c.lineTo(x0 + wTxt, yBot);
      c.lineTo(W / 2 + 26, yBot); c.lineTo(W / 2, yTip); c.lineTo(W / 2 - 26, yBot);
      c.lineTo(x0, yBot); c.closePath(); c.fill();
      c.strokeStyle = '#e8c87a'; c.lineWidth = 3; c.stroke();
      c.fillStyle = '#ffe9b8';
      c.font = 'bold ' + fs + 'px Georgia, serif';
      for (let i = 0; i < bases.length; i++) {
        c.fillText(lines[i], W / 2, bases[i]);
      }
    }
    this.tex.needsUpdate = true;
  }
  /** v2.118 · parte el mensaje en líneas que caben en maxW (greedy). */
  _wrapMsg(c, txt, maxW) {
    const words = String(txt).split(' ');
    const lines = [];
    let cur = '';
    for (const w of words) {
      const t = cur ? cur + ' ' + w : w;
      if (!cur || c.measureText(t).width <= maxW) cur = t;
      else { lines.push(cur); cur = w; }
    }
    if (cur) lines.push(cur);
    return lines;
  }
}

/* ============================================================================
 *  ForajidoStand — la sala de espera del forajido.
 *  Sprite con las 12 poses (mismo pipeline asíncrono del WizardRival),
 *  mapa de etapas y cartel EN MONTAJE. TODO se crea bajo UN grupo en el
 *  rig (lección v2.62: el recentrado de la Quest mueve la sala entera).
 *  ============================================================================ */
class ForajidoStand {
  constructor(game, manifest) {
    this.game = game;
    this.manifest = manifest;
    // v2.120: resolvedor de assets del PROPIO campeonato (los iconos de los
    // superpoderes nuevos lo usan; mismo convenio que el tren y el stand)
    try { this._A = (p) => new URL('./assets/' + p, import.meta.url).href; }
    catch (e) { this._A = () => ''; }
    this.inited = false;
    this.active = false;
    this.state = 'present';
    this._transient = 0;
    this.texs = {};
    // v2.87: plano inicial YA de cuerpo entero (2,15 m, proporción 0,5 del arte)
    // y base EN EL SUELO — applySpriteAspect lo afina con el aspecto real.
    this.spriteBaseY = OESTE.spriteHeight / 2;
    this._t = 0;
    this._ballSaved = null;
    this.__musSDK = null;   // v3.6.3-SDK3: el estado de la BSO vive en el SDK (createMusic)
    this._netParts = null;
    this._woodSaved = null; this._woodTex = null; this._woodFrameMat = null; this._woodFrameCol = 0;   // v2.87 mesa de madera
    this.tapas = []; this.mapaMarker = null;            // v2.83
    this.arbustoGroup = null; this.arbustoMesh = null; this.arbustoSombra = null;
    // v2.86 · DUELO + SUPERPODERES
    this._duelOn = false; this._duelT = 0; this._armT = 0; this._duelPose = false;
    this._rivalOn = false;
    this._powerCd = 0; this._powerT = 0; this._pendingPower = null; this._pendT = 0;
    this._powerKind = null; this._lastPower = null; this._rallyFired = false; this._toward = false;
    this._rev = null; this._dyn = null;   // v2.90: fuera _dynSide (objetivos aleatorios)
    // v2.89 · EL DUELO del Disparo certero: diana, arte de duelo, pala-revólver
    this._duelo = null;
    this.diana = null; this.dianaTex = null; this.dianaZone = 3;
    this.texsDuelo = {};
    this._paddleVisHidden = null; this._revInHand = null;
    this._twoGuns = null; this._twoPaddlesOn = false;   // v2.98: asedio 3.0
    this._starGunRec = null;                            // v2.118: pistola de la estrella
    this._revHandMuzzle = null; this._revHandDir = null;   // v2.90: eje del cañón
    this._gunCoreHidden = null; this._paddleGunFlag = false;
    this._hitShakeT = 0; this._fadeT = 0;                   // v2.91: temblor + fundido
    this._fadeFrom = null; this._fadeTo = null;             // v2.91: texturas del fundido
    this._ballDark = false; this._ballDarkSaved = null;
    this._gunLast = 0;
    this._sangre = null;                                   // v2.93: sangre en la cámara
    // v2.94 · EL CAMINO COMPLETO: etapa actual (1..5), modo de prueba activo
    // (duelo/asedio/tren), duelo Nv (1..3) y heridas acumuladas del asedio
    this.stage = 1; this._stageMode = null; this._duelNv = 1; this._heridas = 0;
    this._instrK = null;   // v2.106: cartel explicativo pendiente ('asedio'|'tren')
    this._asedio = null; this._tren = null;
    this._insignia = null; this._champion = false;
    this._replayReal = null; this._hoverNodo = -1;   // v2.96: rejugada + nodo apuntado
    this._leyendaOn = false;   // v3.6.18 (ronda 24): rejugada LEYENDA activa (sólo campeón)
    try {
      this.stage = clamp(parseInt(localStorage.getItem('pp_champ_oeste_stage') || '1', 10) || 1, 1, 5);
      this._champion = localStorage.getItem('pp_champ_oeste_champ') === '1';
      this._heridas = parseInt(localStorage.getItem('pp_champ_oeste_asedio_heridas') || '0', 10) || 0;
    } catch (e) { this.stage = 1; }
    this._revolverModel = null; this._revolverReady = false; this._revolverTried = false;
    this._tntModel = null; this._tntReady = false; this._tntTried = false;
    this._propsLoading = false; this._laughBuf = null; this._laughBusy = false; this._laughLast = 0;
    this.rank = []; this.duelWins = 0; this.round = 1; this.streakP = 0; this.streakAi = 0;
    try {
      this.duelWins = parseInt(localStorage.getItem('pp_champ_oeste_duelwins') || '0', 10) || 0;
      this.rank = JSON.parse(localStorage.getItem('pp_champ_oeste_rank') || '[]');
      if (!Array.isArray(this.rank)) this.rank = [];
    } catch (e) { this.rank = []; }
    /* v2.119 · PUNTOS del campeonato — recolección PERSISTENTE durante las
     * fases de habilidad (asedio, duelo y tren). Da sentido al RANKING
     * MUNDIAL: lo que se publica es la puntería acumulada, no sólo las
     * victorias de duelo. */
    this.puntos = 0;
    this._pops = [];
    try {
      this.puntos = parseInt(localStorage.getItem('pp_champ_oeste_puntos') || '0', 10) || 0;
    } catch (e2) { this.puntos = 0; }
  }

  build() {
    if (this.inited) return;
    this.inited = true;
    const g = this.game;

    /* --- GRUPO raíz en el rig --- */
    this.group = new THREE.Group();
    this.group.visible = false;
    g.rig.add(this.group);

    /* --- FORAJIDO (sprite del rival, patrón WizardRival) --- */
    const mat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
    });
    this.sprite = new THREE.Mesh(
      new THREE.PlaneGeometry(OESTE.spriteHeight * 0.5, OESTE.spriteHeight),  // v2.87: cuerpo entero
      mat,
    );
    this.sprite.position.set(OESTE.x, this.spriteBaseY, OESTE.z);
    this.sprite.renderOrder = 6;
    this.sprite.visible = false;      // visible sólo con la sala abierta
    this.group.add(this.sprite);
    this.loadTextures();

    /* --- MAPA de etapas (pared izquierda, patrón WizardMap) --- */
    const PH = MAPA.PW * 926 / 1699;
    const mapMat = new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false });
    this.mapa = new THREE.Mesh(new THREE.PlaneGeometry(MAPA.PW, PH), mapMat);
    // respaldo de madera detrás del mapa (como el back del mago)
    const back = new THREE.Mesh(
      new THREE.BoxGeometry(MAPA.PW + 0.06, PH + 0.06, 0.022),
      new THREE.MeshStandardMaterial({ color: 0x3a2718, roughness: 0.9, metalness: 0.05 }),
    );
    back.position.z = -0.013;
    this.mapa.add(back);
    this.mapa.position.set(MAPA.x, MAPA.y, MAPA.z);
    this.mapa.rotation.y = Math.PI / 2;
    this.mapa.visible = false;
    this.group.add(this.mapa);
    try {
      const img = new Image();
      img.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = img; t.needsUpdate = true;
        mapMat.map = t; mapMat.needsUpdate = true;
      };
      img.src = new URL('./assets/mapa.webp', import.meta.url).href;
    } catch (e) { /* sin mapa: la sala sigue */ }

    /* --- TAPAS de los nodos pendientes (v2.83: misma tapa.webp que los
     *     otros campeonatos) + anillo dorado en el nodo actual (1). --- */
    try {
      const PHm = MAPA.PW * 926 / 1699;
      /* v2.136: los medallones del arte nuevo son MÁS GRANDES (~230-265 px)
       * → la tapa crece 240×248 → 284×292 para cubrirlos ENTERA. */
      const TW = 284 / 1699 * MAPA.PW, TH = 292 / 926 * PHm;
      const timg = new Image();
      timg.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = timg; t.needsUpdate = true;
        for (const n of NODOS) {
          if (!n.tapa) continue;
          const m = new THREE.Mesh(
            new THREE.PlaneGeometry(TW, TH),
            new THREE.MeshBasicMaterial({ map: t, transparent: true, depthWrite: false }),
          );
          m.position.set((n.x / 1699 - 0.5) * MAPA.PW, (0.5 - n.y / 926) * PHm, 0.003);
          m.userData.nodo = NODOS.indexOf(n);   // v2.94: índice del nodo (0..4)
          m.renderOrder = 2;
          this.mapa.add(m);
          this.tapas.push(m);
        }
        // v2.94: si la tapa llega TARDE (imagen asíncrona), el progreso manda
        try { this._refreshMap(); } catch (e2) { /* */ }
      };
      timg.src = (this.manifest && this.manifest.tapaUrl) || '';
    } catch (e) { /* sin tapas: los nodos se ven */ }
    try {
      const n0 = NODOS[0], PHm2 = MAPA.PW * 926 / 1699;
      this.mapaMarker = new THREE.Mesh(
        new THREE.RingGeometry(0.118, 0.144, 48),
        new THREE.MeshBasicMaterial({
          color: 0xf6d34c, transparent: true, depthWrite: false, side: THREE.DoubleSide,
        }),
      );
      this.mapaMarker.material.opacity = 0.9;
      this.mapaMarker.position.set(
        (n0.x / 1699 - 0.5) * MAPA.PW, (0.5 - n0.y / 926) * PHm2, 0.006,
      );
      this.mapaMarker.scale.setScalar(n0.r / 120);
      this.mapaMarker.renderOrder = 3;
      this.mapa.add(this.mapaMarker);
    } catch (e) { /* sin anillo: la sala sigue */ }

    /* --- CARTEL EN MONTAJE (canvas, patrón WizardRanking) --- */
    this.cv = oesteCanvas(512, 720);
    this.tex = new THREE.CanvasTexture(this.cv);
    this.tex.colorSpace = THREE.SRGBColorSpace;
    const cMat = new THREE.MeshBasicMaterial({ map: this.tex, transparent: true, depthWrite: false });
    this.cartel = new THREE.Group();
    const plane = new THREE.Mesh(new THREE.PlaneGeometry(0.62, 0.62 * 720 / 512), cMat);
    this.cartel.add(plane);
    this.cartel.position.set(CARTEL.x, CARTEL.y, CARTEL.z);
    this.cartel.rotation.y = CARTEL.rotY;
    this.cartel.visible = false;
    this.group.add(this.cartel);
    this.paintCartel();

    /* --- ARBUSTO RODANTE (v2.83): el «tapador» del forajido. Bola de
     *     ramas secas en el suelo delante de él; el grupo mira al jugador
     *     (misma fórmula de guiñada que el decor del núcleo) y el mesh
     *     gira sobre su centro (h/2) para rodar SIN perder el suelo. --- */
    const ab = ARBUSTO;
    const aMat = new THREE.MeshBasicMaterial({
      transparent: true, depthWrite: false, side: THREE.DoubleSide,
    });
    this.arbustoGroup = new THREE.Group();
    this.arbustoMesh = new THREE.Mesh(new THREE.PlaneGeometry(ab.h * 1.043, ab.h), aMat);
    this.arbustoMesh.position.y = ab.h / 2;
    this.arbustoMesh.renderOrder = 7;      // delante del forajido (renderOrder 6)
    this.arbustoGroup.add(this.arbustoMesh);
    this.arbustoGroup.position.set(ab.x, 0, ab.z);
    this.arbustoGroup.rotation.y = Math.atan2(-ab.x, 0.55 - ab.z);
    this.arbustoGroup.visible = false;
    this.group.add(this.arbustoGroup);
    // sombra que lo acompaña en su vaivén (patrón blob)
    this.arbustoSombra = new THREE.Mesh(
      new THREE.CircleGeometry(ab.h * 0.55, 20),
      new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.22, depthWrite: false }),
    );
    this.arbustoSombra.rotation.x = -Math.PI / 2;
    this.arbustoSombra.position.set(ab.x, 0.004, ab.z);
    this.arbustoSombra.renderOrder = 2;
    this.arbustoSombra.visible = false;
    this.group.add(this.arbustoSombra);
    try {
      const aimg = new Image();
      aimg.onload = () => {
        const t = new THREE.Texture();
        t.colorSpace = THREE.SRGBColorSpace;
        t.image = aimg; t.needsUpdate = true;
        aMat.map = t; aMat.needsUpdate = true;
        const ar = aimg.width && aimg.height ? aimg.width / aimg.height : 0;
        if (ar && isFinite(ar)) {
          this.arbustoMesh.geometry.dispose();
          this.arbustoMesh.geometry = new THREE.PlaneGeometry(ab.h * ar, ab.h);
        }
      };
      aimg.src = new URL('./assets/decor/arbusto.png', import.meta.url).href;
    } catch (e) { /* sin arbusto: la sala sigue */ }

    /* --- v2.86 · DUELO: cartel de poder + FX + cuenta atrás + GLBs --- */
    this.powerSign = new ForajidoPowerSign(this);
    this.powerSign.build();
    this.fx = new ForajidoFx(this);
    this.fx.build();
    this._loadProps();     // revolver.glb + small_tnt.glb (caché del módulo)
    this.loadLaugh();
  }

  /* Carga ASÍNCRONA de las 12 poses (idéntica al WizardRival: Texture por
   * Image webp, aspecto aplicado con la 1.ª que llegue). */
  loadTextures() {
    for (const st of STATES) {
      const tex = new THREE.Texture();
      tex.colorSpace = THREE.SRGBColorSpace;
      const img = new Image();
      img.onload = () => {
        tex.image = img; tex.needsUpdate = true;
        if (!this._aspectHooked && img.width && img.height) {
          this._aspectHooked = true;
          this.applySpriteAspect(img.width / img.height);
        }
        this.texs[st] = tex;
        if (this.state === st) this.applyStateTexture();
      };
      img.onerror = () => { /* sin arte para ese estado: sigue el anterior */ };
      img.src = new URL('./assets/' + st + '.webp', import.meta.url).href;
    }
    // v2.89 · ARTE DEL DUELO (duelo + 5 poses de zona) + DIANA — el mismo
    // cargador asíncrono; si algo falta, el duelo usa la pose actual.
    for (const nm of DUELO_POSES) {
      const tex = new THREE.Texture();
      tex.colorSpace = THREE.SRGBColorSpace;
      const img = new Image();
      img.onload = () => { tex.image = img; tex.needsUpdate = true; this.texsDuelo[nm] = tex; };
      img.onerror = () => { /* sin arte de duelo: sigue la pose actual */ };
      img.src = new URL('./assets/' + nm + '.webp', import.meta.url).href;
    }
    try {
      const dtex = new THREE.Texture();
      dtex.colorSpace = THREE.SRGBColorSpace;
      const dimg = new Image();
      dimg.onload = () => { dtex.image = dimg; dtex.needsUpdate = true; this.dianaTex = dtex; };
      dimg.onerror = () => { /* sin diana: el duelo cae al aviso genérico */ };
      dimg.src = new URL('./assets/diana.webp', import.meta.url).href;
    } catch (e) { /* */ }
  }

  applySpriteAspect(ar) {
    if (!this.inited || !ar || !isFinite(ar)) return;
    let w, h;
    if (OESTE.fullBody) {
      /* v2.87 · CUERPO ENTERO: proporción original SIEMPRE — la ALTURA manda
       * (spriteHeight) y el ancho sale del aspecto real del arte. Nada de la
       * rama fija 1,4×1,75 que comprimía al forajido (su arte es vertical,
       * ar 0,5, y caía ahí por no superar 1,2). Base EN EL SUELO: el plano
       * arranca en y=0 y los pies del personaje quedan pegados al suelo,
       * sin la elevación de 1 m de los bustos flotantes (mago/locura). */
      h = OESTE.spriteHeight;
      w = h * ar;
      this.spriteBaseY = h / 2;
    } else {
      w = 1.4; h = 1.75;
      if (ar > 1.2) { w = OESTE.spriteWidth; h = w / ar; }   // igual que el wizard
      this.spriteBaseY = OESTE.baseY + h / 2;
    }
    this.sprite.geometry.dispose();
    this.sprite.geometry = new THREE.PlaneGeometry(w, h);
    this.sprite.position.y = this.spriteBaseY;
  }

  applyStateTexture() {
    const t = this.texs[this.state];
    if (t && this.sprite) {
      this.sprite.material.map = t;
      this.sprite.material.needsUpdate = true;
    }
  }

  /** Cambia de pose (y de voz cuando llegue la de risas por estado). */
  setState(state, dur) {
    this.state = STATES.indexOf(state) >= 0 ? state : this.state;
    this._transient = dur || 0;
    this.applyStateTexture();
  }
  /** v2.86: pose sin anuncio (los superpoderes y las reacciones del duelo). */
  _setStateSilent(state, dur) {
    this.state = STATES.indexOf(state) >= 0 ? state : this.state;
    this._transient = dur || 0;
    this.applyStateTexture();
  }
  /** v2.89 · Arte EXTRA del duelo (fuera del abanico de estados): pone la
 *  textura directamente en el sprite y programa el retorno con _transient
 *  (dur 0 = se queda hasta el siguiente cambio). */
  _showDuelArt(name, dur) {
    const t = this.texsDuelo[name];
    if (t && this.sprite) {
      this.sprite.material.map = t;
      this.sprite.material.needsUpdate = true;
    }
    this._transient = dur || 0;
  }
  /* ====== v2.91 · FUNDIDO de la pose de impacto (duelo) ==================
   *  Al expirar los 4 s de pose: 1 s en dos mitades — la imagen de
   *  impacto se OSCURECE hasta negro (color del material → 0) y desde el
   *  negro va apareciendo la pose normal (color → 1). Al acabar, estado
   *  'focused' limpio. */
  _duelFadeStart() {
    this._fadeT = DUELO_P.fadeT;
    this._transient = 0;
    this._fadeFrom = this.sprite ? this.sprite.material.map : null;
    this._fadeTo = this.texs && this.texs['focused'] ? this.texs['focused'] : null;
  }
  _duelFadeStep(dt) {
    this._fadeT -= dt;
    if (!this.sprite) { this._fadeT = 0; this._duelFadeEnd(); return; }
    const mat = this.sprite.material;
    const t = 1 - Math.max(0, this._fadeT) / (DUELO_P.fadeT || 1);   // 0→1
    if (t < 0.5) {
      if (this._fadeFrom) mat.map = this._fadeFrom;
      mat.color.setScalar(Math.max(0.02, 1 - t * 2));      // → negro
    } else {
      if (this._fadeTo) mat.map = this._fadeTo;
      mat.color.setScalar(Math.max(0.02, (t - 0.5) * 2));  // desde el negro
    }
    mat.needsUpdate = true;
    if (this._fadeT <= 0) this._duelFadeEnd();
  }
  _duelFadeEnd() {
    this._fadeT = 0;
    this._fadeFrom = null;
    this._fadeTo = null;
    if (this.sprite) {
      this.sprite.material.color.setScalar(1);
      this.sprite.material.needsUpdate = true;
    }
    this.setState('focused');
  }
  /* ====== v2.89 · LA DIANA del duelo (diana.png del artista) ========== */
  /** Aparece SIEMPRE sobre el cuerpo del forajido, en una zona aleatoria
   *  de las 5 (duelo_zonas.jpg). Devuelve true si hay arte. */
  _dianaShow() {
    if (!this.diana) {
      if (!this.dianaTex) return false;
      this.diana = new THREE.Sprite(new THREE.SpriteMaterial({
        map: this.dianaTex, transparent: true, depthWrite: false,
      }));
      this.diana.scale.setScalar(DUELO_P.dianaSize);
      this.diana.renderOrder = 12;
      this.group.add(this.diana);
    }
    this.dianaZone = 1 + ((Math.random() * DUELO_ZONAS.length) | 0);
    const z = DUELO_ZONAS[this.dianaZone - 1];
    this.diana.position.set(DUELO.x, z.y, DUELO.z + 0.10);
    this.diana.visible = true;
    return true;
  }
  _dianaHide() { if (this.diana) this.diana.visible = false; }
  /* ====== v2.89/90 · LA PALA SE CONVIERTE EN EL REVÓLVER DEL FORAJIDO ====
   *  Durante el duelo la mano de la pala empuña el MISMO revólver que el
   *  forajido (revolver.glb — v2.90: la pistola antigua pistol.glb está
   *  RETIRADA del campeonato y NUNCA se muestra; la pala está SIEMPRE en
   *  la mano salvo en estos 3 s). El clon usa la ESCALA que tenía la
   *  pistola (0,32 m) y se miden con VÉRTICES la BOCA del cañón y el EJE
   *  del cañón: la mira láser y el disparo salen exactamente del cañón
   *  (WYSIWYG). Al acabar, la pala vuelve EXACTAMENTE como estaba; los
   *  recursos del clon se COMPARTEN con la caché (_revolverModel). */
  _paddleGunApply(on) {
    const g = this.game;
    if (!g.gunMounts || !g.paddleMounts) return;
    const ph = g.paddleHand;
    const pm = g.paddleMounts[ph];
    const gm = g.gunMounts[ph];
    if (on) {
      this._paddleGunFlag = true;
      if (pm) {
        if (!this._paddleVisHidden) this._paddleVisHidden = [];
        for (const ch of pm.children) {
          if (ch.visible) { ch.visible = false; this._paddleVisHidden.push(ch); }
        }
      }
      if (gm && this._revolverModel && !this._revInHand) {
        // v2.90: NADA de pistola antigua apilada — oculta cualquier otro
        // hijo de la montura (el revólver será el ÚNICO objeto en la mano)
        if (!this._gunCoreHidden) this._gunCoreHidden = [];
        for (const ch of gm.children) {
          if (ch.visible) { ch.visible = false; this._gunCoreHidden.push(ch); }
        }
        const art = this._revolverModel.clone(true);
        // v2.90: MISMA ESCALA que tenía la pistola del artista (0,32 m;
        // el revólver en caché mide DISPARO.escala = 0,34 m)
        art.scale.multiplyScalar(0.32 / (DISPARO.escala || 0.34));
        // v2.93 · FIX RAÍZ DEL «APUNTA AL PROPIO JUGADOR»: el espacio GRIP
        // de WebXR apunta hacia -Z (el núcleo lo lleva usando desde v2.38:
        // «espacio grip SIN cuaternión de pala: cañón hacia -Z, mango
        // abajo»). La v10 garantizó la boca en +Z del grip — justo AL
        // REVÉS — y el revólver acabó mirando al jugador. Ahora se
        // garantiza la boca en -Z del grip (hacia el contrincante),
        // volteando el arte SOLO si la medición da +Z. El láser y el
        // disparo siguen el ARTE (art.localToWorld incluye este giro):
        // WYSIWYG intacto.
        const m = this._medirCañon(art);
        if (m.muzzle && m.muzzle.z > 0) art.rotation.y += Math.PI;
        // v2.94 · CAÑÓN 5° HACIA ABAJO (petición del artista: «si estuviese
        // unos 5 grados apuntando el cañón hacia abajo quedaría mejor»):
        // picado natural de duelo. Euler XYZ = Rx·Ry·Rz (Rx se aplica AL
        // FINAL sobre la boca ya volteada): con Ry(π) o sin él, la boca
        // (0,0,∓1) queda en (0, -sin5°, -cos5°) — abajo y adelante. El láser
        // y el disparo usan art.localToWorld/worldQuaternion: incluyen el
        // picado — WYSIWYG intacto.
        art.rotation.x = -GUN_PITCH;
        gm.add(art);
        gm.visible = true;
        this._revInHand = { mount: gm, art };
        // v2.91: boca y eje medidos en ESPACIO LOCAL del arte — _gunRay
        // los reconstruye con la matriz mundial del arte (cero desfase)
        this._revHandMuzzle = m.muzzle;
        this._revHandDir = m.dir;
      }
    } else {
      this._paddleGunFlag = false;
      if (pm && this._paddleVisHidden) {
        for (const ch of this._paddleVisHidden) ch.visible = true;
        this._paddleVisHidden = null;
      }
      if (this._revInHand) {
        // sólo descolgar: la geometría/material vive en la CACHÉ compartida
        this._revInHand.mount.remove(this._revInHand.art);
        this._revInHand = null;
        this._revHandMuzzle = null;
        this._revHandDir = null;
      }
      if (gm) gm.visible = false;
      if (this._gunCoreHidden) {
        for (const ch of this._gunCoreHidden) ch.visible = true;
        this._gunCoreHidden = null;
      }
      // v2.90: la mano libre queda LIBRE — sin pistola (la pala lo es todo)
      this._gunVisible(false);
    }
  }

  /* ====== v2.94 · REVÓLVER EN LA MANO LIBRE (etapa 2 ASEDIO) ============
   *  La pala SIGUE en su mano (para romper la cobertura con la bola) y la
   *  mano libre empuña el revólver para disparar al punto débil. Mismo
   *  montaje que la pala-revólver del duelo: medición de boca/eje por
   *  vértices, volteo si la boca cae en +Z y picado de 5° (mismo gesto
   *  natural). El gatillo llega vía serveTrigger (el árbitro duerme en
   *  'champtest') y _gunRay() funciona igual (usa _revInHand). */
  _freeGunApply(on) {
    const g = this.game;
    if (!g.gunMounts) return;
    const fh = 1 - g.paddleHand;
    const gm = g.gunMounts[fh];
    if (on) {
      if (!this._revolverModel) return;   // sin GLB cargado: nada en la mano
      if (this._revInHand) return;        // ya hay un revólver montado
      if (!this._gunCoreHidden) this._gunCoreHidden = [];
      for (const ch of (gm ? gm.children : [])) {
        if (ch.visible) { ch.visible = false; this._gunCoreHidden.push(ch); }
      }
      const art = this._revolverModel.clone(true);
      art.scale.multiplyScalar(0.32 / (DISPARO.escala || 0.34));
      const m = this._medirCañon(art);
      if (m.muzzle && m.muzzle.z > 0) art.rotation.y += Math.PI;
      art.rotation.x = -GUN_PITCH;        // mismo picado natural de 5°
      gm.add(art);
      gm.visible = true;
      this._revInHand = { mount: gm, art };
      this._revHandMuzzle = m.muzzle;
      this._revHandDir = m.dir;
    } else {
      if (this._revInHand && this._revInHand.mount === gm) {
        gm.remove(this._revInHand.art);
        this._revInHand = null;
        this._revHandMuzzle = null;
        this._revHandDir = null;
      }
      if (gm) gm.visible = false;
      if (this._gunCoreHidden) {
        for (const ch of this._gunCoreHidden) ch.visible = true;
        this._gunCoreHidden = null;
      }
    }
  }
  /* ====== v2.98 · ASEDIO 3.0 — DOS PALAS y DOS REVÓLVERES ================
   *  · _twoPaddles(on): pala visible en AMBAS manos (el núcleo sólo
   *    enseña la del mando de la pala). Se golpea con cualquiera.
   *  · _twoGunApply(on): al DESTAPARSE un forajido, las dos palas se
   *    convierten en revólveres (revolver.glb, el modelo del artista)
   *    con UN disparo cada uno. Montaje WYSIWYG del duelo: boca y eje
   *    medidos por vértices + picado de 5° (GUN_PITCH).
   *  · _gunHandRemove(h): gasta el revólver de UNA mano — desaparece y
   *    la pala vuelve, hasta la próxima diana.
   *  · _gunLoaded(h)/_gunRayHand(h): estado y rayo WYSIWYG por mano.  */
  _twoPaddles(on) {
    const g = this.game;
    this._twoPaddlesOn = !!on;
    if (!g.paddleMounts) return;
    for (let k = 0; k < 2; k++) {
      if (g.paddleMounts[k]) {
        g.paddleMounts[k].visible = on ? true : (k === g.paddleHand);
      }
    }
  }
  _twoGunApply(on) {
    const g = this.game;
    if (!g.gunMounts) return;
    if (on) {
      if (!this._revolverModel) return;   // GLB aún cargando: nada
      if (this._twoGuns) return;          // ya montados
      /* v2.118 · la pistola de la estrella CEDE la mano limpia: si un
       * forajido se destapa mientras la estrella vuela, los dos revólveres
       * de la diana toman el relevo (la estrella sigue disparable con
       * ellos — _shotAt la comprueba antes que al corazón). */
      this._starGunApply(false);
      this._twoGuns = [];
      for (let h = 0; h < 2; h++) {
        const gm = g.gunMounts[h];
        const pm = g.paddleMounts ? g.paddleMounts[h] : null;
        const rec = { hand: h, mount: gm, art: null, muzzle: null,
          dir: null, hiddenPaddle: [], hiddenGun: [] };
        if (pm) {
          for (const ch of pm.children) {
            if (ch.visible) { ch.visible = false; rec.hiddenPaddle.push(ch); }
          }
        }
        if (gm) {
          for (const ch of gm.children) {
            if (ch.visible) { ch.visible = false; rec.hiddenGun.push(ch); }
          }
          const art = this._revolverModel.clone(true);
          art.scale.multiplyScalar(0.32 / (DISPARO.escala || 0.34));
          const m = this._medirCañon(art);
          if (m.muzzle && m.muzzle.z > 0) art.rotation.y += Math.PI;
          art.rotation.x = -GUN_PITCH;    // picado natural de 5°
          gm.add(art);
          gm.visible = true;
          rec.art = art; rec.muzzle = m.muzzle; rec.dir = m.dir;
        }
        this._twoGuns.push(rec);
      }
    } else {
      const guns = this._twoGuns;
      this._twoGuns = null;
      if (!guns) return;
      for (const rec of guns) {
        for (const ch of rec.hiddenPaddle) ch.visible = true;
        if (rec.art && rec.mount) rec.mount.remove(rec.art);
        if (rec.mount) rec.mount.visible = false;
        for (const ch of rec.hiddenGun) ch.visible = true;
      }
    }
  }
  /** Gasta el revólver de UNA mano: desaparece y la PALA vuelve. */
  _gunHandRemove(h) {
    if (!this._twoGuns) return;
    const rec = this._twoGuns.find((r) => r.hand === (h | 0));
    if (!rec || !rec.art) return;
    if (rec.mount) rec.mount.remove(rec.art);
    if (rec.mount) rec.mount.visible = false;
    for (const ch of rec.hiddenGun) ch.visible = true;
    for (const ch of rec.hiddenPaddle) ch.visible = true;
    rec.hiddenPaddle = [];
    rec.art = null; rec.muzzle = null; rec.dir = null;
  }
  /** ¿hay revólver CARGADO en esa mano? (esa mano no golpea con pala) */
  _gunLoaded(h) {
    /* v2.118 · la pistola de la ESTRELLA también carga: su mano no
     * golpea con la pala (está oculta bajo el arma). */
    if (this._starGunRec && this._starGunRec.hand === (h | 0) &&
        this._starGunRec.art) return true;
    return !!(this._twoGuns &&
      this._twoGuns.some((r) => r.hand === (h | 0) && r.art));
  }
  /* ====== v2.118 · LA ESTRELLA DEL SHERIFF DA SU PROPIA PISTOLA ==========
   *  Petición del artista: al APARECER la estrella, la PALA de UNA mano
   *  (la libre) se cambia por el REVÓLVER para poder dispararle; al
   *  DESAPARECER la estrella (caduca o cazada), la pala vuelve. El arma
   *  no gasta munición: vive lo que vive la estrella. Si un forajido se
   *  destapa mientras vuela, _twoGunApply(true) retira esta pistola y
   *  montan los DOS revólveres de la diana (la estrella sigue
   *  disparable con ellos: _shotAt la comprueba primero). */
  _starGunApply(on) {
    const g = this.game;
    if (!g.gunMounts) return;
    const h = 1 - g.paddleHand;          // la pala principal sigue libre
    if (on) {
      if (!this._revolverModel) return;  // GLB aún cargando: nada
      if (this._twoGuns) return;         // los revólveres de la diana mandan
      if (this._starGunRec && this._starGunRec.hand === h) return;
      this._starGunApply(false);         // re-monta si cambió la mano
      const gm = g.gunMounts[h];
      const pm = g.paddleMounts ? g.paddleMounts[h] : null;
      const rec = { hand: h, mount: gm, art: null, muzzle: null,
        dir: null, hiddenPaddle: [], hiddenGun: [] };
      if (pm) {
        for (const ch of pm.children) {
          if (ch.visible) { ch.visible = false; rec.hiddenPaddle.push(ch); }
        }
      }
      if (gm) {
        for (const ch of gm.children) {
          if (ch.visible) { ch.visible = false; rec.hiddenGun.push(ch); }
        }
        const art = this._revolverModel.clone(true);
        art.scale.multiplyScalar(0.32 / (DISPARO.escala || 0.34));
        const m = this._medirCañon(art);
        if (m.muzzle && m.muzzle.z > 0) art.rotation.y += Math.PI;
        art.rotation.x = -GUN_PITCH;     // mismo picado natural de 5°
        gm.add(art);
        gm.visible = true;
        rec.art = art; rec.muzzle = m.muzzle; rec.dir = m.dir;
      }
      this._starGunRec = rec;
    } else {
      const rec = this._starGunRec;
      if (!rec) return;
      this._starGunRec = null;
      if (rec.art && rec.mount) rec.mount.remove(rec.art);
      if (rec.mount) rec.mount.visible = false;
      for (const ch of rec.hiddenGun) ch.visible = true;
      for (const ch of rec.hiddenPaddle) ch.visible = true;
    }
  }
  /** RAYO del revólver en la mano h (WYSIWYG, espacio RIG) — el mismo
   *  convenio que _gunRay() del duelo, pero POR MANO. */
  _gunRayHand(h) {
    const g = this.game;
    /* v2.118 · el rayo también sale de la PISTOLA de la estrella (su
     * láser y su disparo son WYSIWYG igual que los de diana). */
    const rec = (this._twoGuns &&
      this._twoGuns.find((r) => r.hand === (h | 0) && r.art)) ||
      (this._starGunRec && this._starGunRec.hand === (h | 0) &&
       this._starGunRec.art ? this._starGunRec : null);
    if (!rec || !rec.muzzle || !rec.dir) return null;
    try {
      rec.art.updateWorldMatrix(true, false);
      // v2.120: rayo de MÓDULO (0 allocs por frame; síncrono en el llamador)
      const posW = rec.art.localToWorld(_GR_V1.copy(rec.muzzle));
      const qW = rec.art.getWorldQuaternion(_GR_Q1);
      const dirW = _GR_V2.copy(rec.dir).applyQuaternion(qW).normalize();
      const qRig = g.rig.getWorldQuaternion(_GR_Q2).invert();
      return {
        pos: g.rig.worldToLocal(_GR_V3.copy(posW)),
        dir: _GR_V4.copy(dirW).applyQuaternion(qRig).normalize(),
      };
    } catch (e) { return null; }
  }
  /** v2.91 · Medición del cañón EN ESPACIO LOCAL del arte: boca = extremo
   *  Z opuesto al puño (vértice más bajo) y eje = franja media→boca.
   *  Devuelve { muzzle, dir } en espacio LOCAL del arte (o nulls). */
  _medirCañon(art) {
    /* v2.91 · Medición en espacio LOCAL del ARTE (independiente de la
     *  montura, del mando y del rig): los vértices se transforman al mundo
     *  y se VUELVEN al espacio propio del arte con la inversa de su
     *  matrixWorld. Así el rayo se puede reconstruir EXACTO con
     *  art.localToWorld() pase lo que pase alrededor (v2.90 medía en mundo
     *  y lo usaba como espacio de montura: desfase del láser en el casco).
     *  La BOCA se elige con el vértice MÁS BAJO (la base del puño): la
     *  boca del cañón está en el extremo Z OPUESTO al puño — nada de
     *  supuestos de signo. Devuelve { muzzle, dir } en espacio local del
     *  arte (o { null, null } si no hay geometría). */
    const out = { muzzle: null, dir: null };
    try {
      // v2.92 · (true, TRUE): hay que refrescar el SUBÁRBOL — con (true,
      // false) los matrixWorld de los hijos quedaban OBSOLETOS (el clon
      // copia matrices viejas y el giro π de carga no se reflejaba), y la
      // boca medida salía FUERA del modelo (láser desfasado en el visor).
      art.updateWorldMatrix(true, true);
      const inv = new THREE.Matrix4().copy(art.matrixWorld).invert();
      const vv = new THREE.Vector3();
      let minZ = Infinity, maxZ = -Infinity, minY = Infinity, zMinY = 0;
      const pts = [];
      art.traverse((o) => {
        if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
        const pa = o.geometry.attributes.position;
        if (!pa) return;
        for (let i = 0; i < pa.count; i++) {
          vv.fromBufferAttribute(pa, i).applyMatrix4(o.matrixWorld).applyMatrix4(inv);
          if (!isFinite(vv.z)) continue;
          pts.push(vv.x, vv.y, vv.z);
          if (vv.z < minZ) minZ = vv.z;
          if (vv.z > maxZ) maxZ = vv.z;
          if (vv.y < minY) { minY = vv.y; zMinY = vv.z; }   // base del puño
        }
      });
      if (!pts.length || !isFinite(minZ) || maxZ - minZ < 1e-4) return out;
      const lenZ = maxZ - minZ;
      // extremo de la BOCA: el Z opuesto al vértice más bajo (el puño)
      const tipZ = (Math.abs(zMinY - minZ) <= Math.abs(zMinY - maxZ)) ? maxZ : minZ;
      const sgn = tipZ === maxZ ? 1 : -1;
      // ventana de la BOCA: el 12 % más cercano a la punta
      const zTipIn = tipZ - sgn * lenZ * 0.12;
      // franja MEDIA del tubo (30 %-55 % hacia el centro)
      const zMid0 = tipZ - sgn * lenZ * 0.30;
      const zMid1 = tipZ - sgn * lenZ * 0.55;
      const loT = Math.min(tipZ, zTipIn), hiT = Math.max(tipZ, zTipIn);
      const loM = Math.min(zMid0, zMid1), hiM = Math.max(zMid0, zMid1);
      let sxT = 0, syT = 0, nT = 0, sxM = 0, syM = 0, szM = 0, nM = 0;
      for (let i = 0; i < pts.length; i += 3) {
        const x = pts[i], y = pts[i + 1], z = pts[i + 2];
        if (z >= loT && z <= hiT) { sxT += x; syT += y; nT++; }
        else if (z >= loM && z <= hiM) { sxM += x; syM += y; szM += z; nM++; }
      }
      if (nT <= 0) return out;
      out.muzzle = new THREE.Vector3(sxT / nT, syT / nT, tipZ);
      if (nM > 0) {
        const v = new THREE.Vector3(out.muzzle.x - sxM / nM,
          out.muzzle.y - syM / nM, tipZ - szM / nM);
        if (v.lengthSq() > 1e-9) out.dir = v.normalize();
        else out.dir = new THREE.Vector3(0, 0, sgn);
      } else {
        out.dir = new THREE.Vector3(0, 0, sgn);
      }
      // el eje SIEMPRE sale hacia FUERA por la boca medida
      if (out.dir.z * sgn < 0) out.dir.z = -out.dir.z;
      out.dir.normalize();
    } catch (e) { /* sin medición: _gunRay devuelve null y no hay rayo */ }
    return out;
  }
  /** v2.91 · RAYO del arma EN MANO (espacio RIG): origen = boca del cañón
   *  real y dirección = eje real, reconstruidos con la matriz del ARTE
   *  (art.localToWorld + cuaternión mundial del arte): el rayo sale de la
   *  punta del cañón que se VE, con cero desfase, pase lo que pase con la
   *  pose del mando o la escala. Lo usan la mira láser Y el disparo
   *  (WYSIWYG). Devuelve null si no hay revólver en mano ni medición. */
  _gunRay() {
    const g = this.game;
    if (!this._revInHand) return null;
    const art = this._revInHand.art;
    const muzzle = this._revHandMuzzle;
    const dirLocal = this._revHandDir;
    if (!art || !muzzle || !dirLocal) return null;
    try {
      art.updateWorldMatrix(true, false);
      // v2.120: rayo de MÓDULO (0 allocs por frame) — los llamadores lo
      // consumen síncronos (duelo/asedio/trigger verificados).
      const posW = art.localToWorld(_GR_V1.copy(muzzle));
      const qW = art.getWorldQuaternion(_GR_Q1);
      const dirW = _GR_V2.copy(dirLocal).applyQuaternion(qW).normalize();
      const qRig = g.rig.getWorldQuaternion(_GR_Q2).invert();
      return {
        pos: g.rig.worldToLocal(_GR_V3.copy(posW)),
        dir: _GR_V4.copy(dirW).applyQuaternion(qRig).normalize(),
      };
    } catch (e) { return null; }
  }

  /* ------------------------- CARTEL EN MONTAJE ------------------------- */
  paintCartel() {
    const cv = this.cv, c = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    // madera vieja
    const gr = c.createLinearGradient(0, 0, 0, H);
    gr.addColorStop(0, '#4a331c');
    gr.addColorStop(0.5, '#5c4224');
    gr.addColorStop(1, '#3a2712');
    c.fillStyle = gr;
    c.fillRect(0, 0, W, H);
    // vetas
    c.strokeStyle = 'rgba(30,20,8,0.35)';
    c.lineWidth = 2;
    for (let i = 0; i < 14; i++) {
      c.beginPath();
      const y = 20 + i * 50 + (i % 3) * 7;
      c.moveTo(8, y);
      c.bezierCurveTo(W * 0.3, y + 6, W * 0.7, y - 6, W - 8, y + 2);
      c.stroke();
    }
    // marco clavado
    c.strokeStyle = '#c89b4a';
    c.lineWidth = 10;
    c.strokeRect(14, 14, W - 28, H - 28);
    c.fillStyle = '#e8c87a';
    [[26, 26], [W - 26, 26], [26, H - 26], [W - 26, H - 26]].forEach(([x, y]) => {
      c.beginPath(); c.arc(x, y, 7, 0, Math.PI * 2); c.fill();
    });
    // estrella del sheriff (provisional)
    c.save();
    c.translate(W / 2, 96);
    c.fillStyle = '#e8c87a';
    c.strokeStyle = '#7a5a1e';
    c.lineWidth = 4;
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const r = (i % 2 === 0) ? 46 : 20;
      const a = -Math.PI / 2 + i * Math.PI / 5;
      const px = Math.cos(a) * r, py = Math.sin(a) * r;
      if (i === 0) c.moveTo(px, py); else c.lineTo(px, py);
    }
    c.closePath(); c.fill(); c.stroke();
    c.restore();
    // títulos
    c.textAlign = 'center';
    c.fillStyle = '#f6e3b0';
    c.font = 'bold 44px Georgia, serif';
    c.fillText(tx('cartel_t1'), W / 2, 196);
    c.fillText(tx('cartel_t2'), W / 2, 244);
    // cinta con la etapa VIGENTE (v2.94: «DUELO 1/2/FINAL · ¡GATILLO!» o el
    // nombre de la prueba que toca)
    c.fillStyle = '#8c2f1e';
    c.fillRect(66, 286, W - 132, 64);
    c.strokeStyle = '#e8c87a'; c.lineWidth = 4;
    c.strokeRect(66, 286, W - 132, 64);
    c.fillStyle = '#ffe9b8';
    c.font = 'bold 40px Georgia, serif';
    const stNow = clamp(this.stage || 1, 1, 5);
    const hv = this._hoverNodo | 0;   // v2.96: nodo apuntado con la pala
    if (hv >= 0 && (hv + 1) !== stNow) {
      c.fillText(tx(this._champion ? 'leyenda_ribbon' : 'replay_ribbon').replace('{n}', String(hv + 1)), W / 2, 330);   // v3.6.18 (ronda 24)
    } else {
      const ribbonKey = stNow === 2 ? 'e2' : (stNow === 4 ? 'e4'
        : (stNow === 5 ? 'duelo_ribbon3' : (stNow === 3 ? 'duelo_ribbon2' : 'duelo_ribbon')));
      c.fillText(tx(ribbonKey), W / 2, 330);
    }
    c.fillStyle = '#e0c890';
    c.font = 'italic 26px Georgia, serif';
    const winsTxt = (this.duelWins | 0) > 0
      ? (TL === 'en'
        ? 'Trigger: start the stage · Wins: ' + this.duelWins
        : 'Gatillo: empezar la etapa ' + stNow + ' · Ganados: ' + this.duelWins)
      : tx('duelo_sub');
    c.fillText(winsTxt, W / 2, 388);
    // plan de la ruta (v2.94: la etapa VIGENTE marcada con «►»)
    c.fillStyle = '#f6e3b0';
    c.font = 'bold 30px Georgia, serif';
    c.fillText(tx('plan'), W / 2, 452);
    c.font = '26px Georgia, serif';
    const lines = [tx('e1'), tx('e2'), tx('e3'), tx('e4'), tx('e5')];
    lines.forEach((ln, i) => {
      const cur = (i + 1) === stNow;
      c.fillStyle = cur ? '#ffdf8f' : '#e8d5a5';
      c.fillText((cur ? '► ' : '') + ln, W / 2, 496 + i * 36);
    });
    // v2.96: pista de REJUGUE (sólo si hay etapas superadas)
    if (this.stage > 1) {
      c.fillStyle = '#ffd257';
      c.font = 'italic 22px Georgia, serif';
      c.fillText(tx(this._champion ? 'leyenda_on' : 'replay_hint'), W / 2, 662);   // v3.6.18 (ronda 24)
    }
    // pie (v2.94: si ya es CAMPEÓN, la estrella brilla en el cartel)
    c.fillStyle = '#c9a86a';
    c.font = 'italic 22px Georgia, serif';
    // v3.6.18 (ronda 24): el pie del campeón cuenta sus SELLOS de leyenda
    c.fillText(this._champion
      ? (this._sellosLeyenda() >= 5 ? tx('leyenda_completa') : tx('leyenda_cstat', { n: this._sellosLeyenda() }))
      : tx('falta'), W / 2, 700);
    this.tex.needsUpdate = true;
  }

  /** Idioma en caliente (pp-lang): repinta el cartel. */
  refresh() {
    TL = (window.__PP_CORE && window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    if (this.inited) this.paintCartel();
  }

  /* ------------------------------ MÚSICA -------------------------------
   * Motor v2.78 del mago, intacto: BSO en bucle que sigue el AJUSTE GLOBAL
   * del núcleo («Música de los campeonatos», pp_arcade_vol) EN VIVO.
   * v3.6.3-SDK3: el motor vive en el SDK (createMusic v1.2.0) — fundido de
   * entrada 0,8 s, resurrección v2.124, UNA MELODÍA con arcPlaying, sync
   * en vivo con rampa 0,15 s y decode v2.125, UNA sola fuente. */
  musicOn() {
    // v2.111: durante el vagón manda vagon.mp3 (TrenAction) — la BSO del
    // saloon no debe solaparse si el núcleo re-invoca musicOn().
    if (this._stageMode === 'tren') return;
    this._musSDK.on();
  }
  /* Motor de la BSO: instancia perezosa del SDK (createMusic). Los knobs
   * son los del motor v2.78+v2.124 que sustituye y van POR DEFECTO en el
   * SDK: fadeIn 0,8 con ancla, syncMode 'ramp' (0,15 s), gateStart
   * arcPlaying, renace (resurrección v2.124) y parada instantánea. */
  get _musSDK() {
    if (!this.__musSDK) {
      this.__musSDK = createMusic(() => this.game, {
        url: () => this.manifest && this.manifest.musicUrl,
        vol: () => this._musicEffVol(),
        puede: () => this._stageMode !== 'tren',
      });
    }
    return this.__musSDK;
  }
  _musicEffVol() {
    try {
      const A = this.game && this.game.audio;
      if (!A) return OESTE.musicVol;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return OESTE.musicVol; }
  }
  _syncMusicGain() {
    // sincronía en vivo + resurrección v2.124: delegadas en el SDK
    this._musSDK.sync();
  }
  musicOff() {
    // parada instantánea, como siempre: delega en el SDK
    this._musSDK.off();
  }

  /* --------------------------- CICLO DE SALA --------------------------- */
  _findNetParts() {
    const g = this.game;
    try {
      return g.tableGroup.children.filter((m) =>
        Math.abs(m.position.z - (window.__PP_CORE.DIMS.tableCenterZ)) < 0.02 &&
        m.position.y > window.__PP_CORE.DIMS.tableTopY + 0.01);
    } catch (e) { return []; }
  }

  /* =================== MESA DE MADERA DEL SALOON (v2.87) ==================
   *  La mesa reglamentaria azul no pega con el saloon: aquí se viste con
   *  TABLONES de madera vieja (textura procedural, cero assets nuevos) y
   *  el marco/patas pasan a madera oscura. Patrón _tableMagicOn/Off del
   *  mago: se guarda el estado original, se aplica al ENTRAR al campeonato
   *  y se restaura al SALIR (dispose GPU incluido). Física intacta. */
  _woodTexture() {
    const cv = document.createElement('canvas');
    cv.width = 1024; cv.height = 1024;
    const c = cv.getContext('2d');
    if (!c) return null;
    const tones = ['#7c4a22', '#8a5a2b', '#6e421e', '#93682f', '#7a4c22'];
    const N = tones.length;                       // 5 tablones a lo largo de la mesa
    const pw = cv.width / N;
    const det = (i, k, a) => Math.sin(i * 12.9898 + k * 78.233) * 43758.5453 % a;  // pseudo-aleatorio determinista
    for (let i = 0; i < N; i++) {
      // base con leve degradado (desgaste del centro al canto)
      const gr = c.createLinearGradient(i * pw, 0, (i + 1) * pw, 0);
      gr.addColorStop(0, tones[i]);
      gr.addColorStop(0.5, '#8f6128');
      gr.addColorStop(1, tones[i]);
      c.fillStyle = gr;
      c.fillRect(i * pw, 0, pw, cv.height);
      // vetas oscuras onduladas (a lo largo del tablón)
      c.strokeStyle = 'rgba(46,28,12,0.35)';
      c.lineWidth = 2;
      for (let v = 0; v < 7; v++) {
        const x0 = i * pw + 14 + Math.abs(det(i, v, 100)) / 100 * (pw - 28);
        c.beginPath();
        c.moveTo(x0, -10);
        c.bezierCurveTo(
          x0 + (det(i, v + 1, 16) - 8), cv.height * 0.33,
          x0 + (det(i, v + 2, 16) - 8), cv.height * 0.66,
          x0 + (det(i, v + 3, 12) - 6), cv.height + 10,
        );
        c.stroke();
      }
      // vetas claras (brillo de barniz viejo)
      c.strokeStyle = 'rgba(232,200,140,0.14)';
      c.lineWidth = 3;
      for (let v = 0; v < 2; v++) {
        const x0 = i * pw + 20 + Math.abs(det(i, v + 9, 100)) / 100 * (pw - 40);
        c.beginPath();
        c.moveTo(x0, -10);
        c.bezierCurveTo(x0 + 10, cv.height * 0.4, x0 - 10, cv.height * 0.7, x0 + 6, cv.height + 10);
        c.stroke();
      }
      // nudo de madera en los tablones alternos
      if (i % 2 === 0) {
        const kx = i * pw + pw * 0.5 + (det(i, 21, 40) - 20);
        const ky = cv.height * (0.25 + Math.abs(det(i, 22, 50)) / 100);
        for (let r = 14; r >= 4; r -= 5) {
          c.beginPath();
          c.ellipse(kx, ky, r * 1.6, r, 0.3, 0, Math.PI * 2);
          c.strokeStyle = 'rgba(52,32,14,0.4)';
          c.lineWidth = 2;
          c.stroke();
        }
        c.beginPath();
        c.ellipse(kx, ky, 3, 2, 0.3, 0, Math.PI * 2);
        c.fillStyle = 'rgba(40,24,10,0.55)';
        c.fill();
      }
      // junta entre tablones
      c.fillStyle = 'rgba(24,14,5,0.8)';
      c.fillRect(i * pw - 3, 0, 6, cv.height);
    }
    const tex = new THREE.CanvasTexture(cv);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
    try { tex.anisotropy = this.game.renderer.capabilities.getMaxAnisotropy(); } catch { /* */ }
    return tex;
  }

  _tableWoodOn() {
    const g = this.game;
    if (!g.tableGroup || this._woodSaved) return;
    const top = g.tableGroup.getObjectByName('ppTableTop');
    if (!top || !top.material) return;
    this._woodSaved = {
      mat: top.material,
      map: top.material.map || null,
      col: top.material.color.getHex(),
      rough: top.material.roughness,
      metal: top.material.metalness,
    };
    const tex = this._woodTexture();
    this._woodTex = tex;
    if (tex) {
      top.material.map = tex;
      top.material.color.setHex(0xffffff);
      top.material.roughness = 0.85;
      top.material.metalness = 0.0;
      top.material.needsUpdate = true;
    }
    // marco y patas a madera oscura (v2.87: el núcleo les da nombre)
    for (const n of g.tableGroup.children) {
      if ((n.name === 'ppTableApron' || n.name === 'ppTableLeg') &&
          n.material && n.material.color && !this._woodFrameMat) {
        this._woodFrameMat = n.material;          // apuntalado: UN material compartido
        this._woodFrameCol = n.material.color.getHex();
        break;
      }
    }
    if (this._woodFrameMat) {
      this._woodFrameMat.color.setHex(0x5a4028);
      this._woodFrameMat.needsUpdate = true;
    }
  }

  _tableWoodOff() {
    const s = this._woodSaved;
    if (s && s.mat) {
      s.mat.map = s.map;
      s.mat.color.setHex(s.col);
      s.mat.roughness = s.rough;
      s.mat.metalness = s.metal;
      s.mat.needsUpdate = true;
    }
    if (this._woodFrameMat) {
      this._woodFrameMat.color.setHex(this._woodFrameCol);
      this._woodFrameMat.needsUpdate = true;
    }
    this._woodSaved = null;
    this._woodFrameMat = null;
    if (this._woodTex) { try { this._woodTex.dispose(); } catch { /* */ } this._woodTex = null; }
  }

  _parkMainBall() {
    const g = this.game;
    // bola principal aparcada bajo el suelo mientras no juega (patrón mago)
    if (g.ball.pos.y > -5) {
      g.ball.pos.set(0, -10, 0);
      g.ball.vel.set(0, 0, 0);
      g.ball.spin.set(0, 0, 0);
      g.ballMesh.visible = false;
    }
  }

  /** Lanzar la sala (botón del menú CAMPEONATOS → ChampLoader.launch). */
  startChamp() {
    const g = this.game;
    this.build();
    this.active = true;
    if (!this._netParts || !this._netParts.length) this._netParts = this._findNetParts();
    for (const m of this._netParts) m.visible = false;
    g.tableGroup.visible = true;
    this._tableWoodOn();                 // v2.87: mesa de madera del saloon (restaura al salir)
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    if (g.fanfareBanner && g.fanfareBanner.group) g.fanfareBanner.group.visible = false;
    g.confettiBurst = 0;
    g.rules.message = tx('msg_enter');
    g.rules.state = STATE_NAME;          // el ÁRBITRO queda en pausa
    g.rules.oppLabel = 'forajido';
    g.ball.ignoreNet = true;
    this._parkMainBall();
    // tinte de la bola principal (BLANCA v2.89, visible en la madera)
    const m = g.ballMesh;
    if (m && m.material && !this._ballSaved) {
      this._ballSaved = {
        col: m.material.color.getHex(),
        em: m.material.emissive ? m.material.emissive.getHex() : null,
        ei: m.material.emissiveIntensity,
      };
      m.material.color.setHex(OESTE.ballColors[0]);
      if (m.material.emissive) m.material.emissive.setHex(OESTE.ballEmissive);
    }
    // sala visible: forajido + mapa + cartel
    this.group.visible = true;
    this.sprite.visible = true;
    this.mapa.visible = true;
    this.cartel.visible = true;
    if (g.roomGroup) g.roomGroup.visible = true;          // v2.94: por si el TREN la cerró
    if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = true;
    if (this.arbustoGroup) this.arbustoGroup.visible = true;    // v2.83
    if (this.arbustoSombra) this.arbustoSombra.visible = true;
    this.setState('present', 3.5);       // saluda con su pose base y pasa a idle
    this.musicOn();
    // v2.94: el mapa SIEMPRE al día (tapas levantadas + anillo en la etapa
    // vigente) y la insignia del CAMPEÓN si ya se ganó el duelo final
    this._refreshMap();
    if (this._champion) this._insigniaShow();
    // v2.86: sala lista para el DUELO (gatillo) — re-ancla el forajido y el
    // arbusto en SU sitio de sala por si el último uso fue un duelo
    this._duelOn = false;
    this._armT = 1.2;
    if (this.sprite) this.sprite.position.set(OESTE.x, this.spriteBaseY, OESTE.z);
    if (this.sprite) { this.sprite.rotation.z = 0; this._hitShakeT = 0; this._fadeT = 0; }   // v2.91: fuera temblor/fundido
    if (this.arbustoGroup) this.arbustoGroup.position.set(ARBUSTO.x, 0, ARBUSTO.z);
    if (this.arbustoSombra) this.arbustoSombra.position.set(ARBUSTO.x, 0.004, ARBUSTO.z);
  }

  /* ======================================================================
   *  v2.86 · DUELO Nv. 1 + SUPERPODERES (métodos nuevos del forajido).
   *  La SALA DE ESPERA queda EXACTAMENTE igual; esto se añade encima.
   *  ====================================================================== */
  storageKey(k) { return 'pp_champ_oeste_' + k; }

  /* ================== v2.119 · PUNTOS DEL CAMPEONATO ======================
   *  Recolección coherente con el RANKING MUNDIAL durante TODAS las fases
   *  de habilidad del Salvaje Oeste:
   *    · ASEDIO  — forajido abatido +100 · estrella del sheriff +150 ·
   *                oleada superada +200 · asedio superado +300
   *    · DUELO   — punto a favor +25 · duelo ganado +250
   *    · TREN    — cajón reventado +20 · lingote asegurado +100 ·
   *                forajido de la ventana +150 · indio alcanzado +150 ·
   *                parada con botín completo +250 · trayecto completo +300
   *  Cada suma persiste (pp_champ_oeste_puntos) y suelta un «+N» dorado
   *  flotante donde ocurre. El ranking publica ESTA cifra (p: puntos). */
  _puntosAdd(n, pos) {
    this.puntos = (this.puntos | 0) + (n | 0);
    try {
      localStorage.setItem(this.storageKey('puntos'), String(this.puntos));
    } catch (e) { /* */ }
    if (!pos || !this.group) return;
    // «+N» dorado flotante (pool de 5 sprites, sube y se desvanece)
    let pop = null;
    for (const p of this._pops) { if (!p.viva) { pop = p; break; } }
    if (!pop) {
      if (this._pops.length >= 5) return;      // pool lleno: se pierde el pop
      const cv = document.createElement('canvas');
      cv.width = 256; cv.height = 128;
      const tex = new THREE.CanvasTexture(cv);
      tex.colorSpace = THREE.SRGBColorSpace;
      const spr = new THREE.Sprite(new THREE.SpriteMaterial({
        map: tex, transparent: true, depthWrite: false, depthTest: false,
      }));
      spr.renderOrder = 950;
      spr.scale.set(0.46, 0.23, 1);
      this.group.add(spr);
      pop = { spr, cv, tex, viva: false, t: 0, base: new THREE.Vector3() };
      this._pops.push(pop);
    }
    const c = pop.cv.getContext('2d');
    c.clearRect(0, 0, 256, 128);
    c.font = 'bold 84px Georgia, serif';
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.lineWidth = 14;
    c.strokeStyle = 'rgba(61,39,8,0.95)';
    c.strokeText('+' + n, 128, 68);
    c.fillStyle = '#ffd24a';
    c.fillText('+' + n, 128, 68);
    pop.tex.needsUpdate = true;
    pop.base.copy(pos);
    pop.base.y += 0.32;
    pop.spr.position.copy(pop.base);
    pop.spr.visible = true;
    pop.spr.material.opacity = 1;
    pop.viva = true;
    pop.t = 0;
  }
  _puntosStep(dt) {
    for (const p of this._pops) {
      if (!p.viva) continue;
      p.t += dt;
      const k = Math.min(1, p.t / 1.15);
      p.spr.position.y = p.base.y + k * 0.42;
      p.spr.material.opacity = 1 - k;
      if (k >= 1) { p.viva = false; p.spr.visible = false; }
    }
  }

  /* ======================================================================
   *  v2.94 · RUTA DE ETAPAS — el gatillo de la sala lanza la etapa ACTUAL:
   *   1 DUELO Nv.1 · 2 ASEDIO · 3 DUELO Nv.2 · 4 ASALTO AL TREN · 5 FINAL.
   *  En PRUEBA activa el gatillo va a la prueba (disparo del asedio; en el
   *  tren la bola va sola). 1,2 s de asentamiento anti-gesto accidental.
   *  ====================================================================== */
  serveTrigger(i) {
    if (!this.active) return;
    if (this._instrK) return;   // v2.106: cartel explicativo en pantalla
    // v2.94: PRUEBA activa → el gatillo es suyo (disparo del revólver en
    // el asedio — v2.98: POR MANO; en el tren no hay gatillo)
    if (this._stageMode === 'asedio') { if (this._asedio) this._asedio.trigger(i); return; }
    // v2.111: el gatillo del vagón DISPARA el revólver de la mano libre
    if (this._stageMode === 'tren') { if (this._tren) this._tren.trigger(i); return; }
    if (this._duelOn) return;
    if (this._armT > 0) return;
    const st = this.stage;
    if (st === 2) return this._startAsedio();
    if (st === 4) return this._startTren();
    // 1, 3 y 5: DUELOS (Nv. 1, 2 y FINAL)
    const nv = st >= 5 ? 3 : (st === 3 ? 2 : 1);
    this._startDuel(nv);
  }

  /* ========================================================================
   *  v2.106 · CARTEL EXPLICATIVO ANTES DE CADA PRUEBA (petición global:
   *  «en todas las pruebas de habilidad de todos los campeonatos debería
   *  aparecer un cartel con la explicación»). Aquí: ASEDIO y TREN. El
   *  cartel lo pinta el NÚCLEO (showInstrucciones) con maquetación
   *  cuidada (texto envuelto, sin cortes). El gatillo no hace nada
   *  mientras el cartel está en pantalla; la prueba arranca sola al irse. */
  _instrGo(k, body) {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('msg_guest'); return; }
    if (this._instrK === k) {
      this._instrK = null;
      try { body(); } catch (e) {
        console.warn('[oeste.' + k + '] error arrancando la prueba', e);
      }
      return;
    }
    if (!this.active) return;
    this._instrK = k;
    g.showInstrucciones(tx('instr_' + k + '_t'), tx('instr_' + k), 7.5,
      () => { try { this._instrGo(k, body); } catch (e) { this._instrK = null; } },
      'oeste',   // v2.107: pergamino del SALVAJE OESTE
      { empezar: true });   // v2.130: espera al botón EMPEZAR (común)
  }

  /** DUELO (Nv. 1, 2 o FINAL): partida REAL del núcleo (a 11) contra la IA,
   *  vestida de forajido — la misma arquitectura del WIZARD (v2.70) con su
   *  REGLA FIJA. v2.94: la dificultad crece por nivel (DUELO_NV: aiMul y
   *  superpoderes más vivos) y el cartel/mensajes acompañan. */
  _startDuel(nv) {
    const g = this.game;
    nv = nv || 1;
    this._duelNv = nv;
    this._duelStage = nv === 3 ? 5 : (nv === 2 ? 3 : 1);   // etapa que supera
    if (g.net.online) { g.rules.message = tx('msg_guest'); return; }
    this._duelOn = true;
    this._duelT = 0;
    this._rivalOn = true;
    g.mode = 'arcade';
    g.rules.oppLabel = 'forajido';
    g.rules.startMatch('match');
    g.applyAISkill();
    g.resetToss();
    g.aiToss = null;
    g.demoToss = null;
    g.ai.reset();
    g.setupAIServe();
    this.round = (this.rank ? this.rank.length : 0) + 1;
    this.streakP = 0;
    this.streakAi = 0;
    g.freezeT = 0;
    // escena: la RED y el MARCADOR vuelven (duelo real), el cartel de sala
    // se retira; el SALOON (room v2.85) y los troqueles siguen puestos
    if (!this._netParts || !this._netParts.length) this._netParts = this._findNetParts();
    for (const m of this._netParts) m.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    this.cartel.visible = false;
    this.mapa.visible = true;
    g.ball.ignoreNet = false;
    g.ballMesh.visible = true;
    // el forajido EN PERSONA (posición probada del mago) + arbusto delante
    this._duelPose = true;
    if (this.sprite) {
      this.sprite.visible = true;
      this.sprite.position.set(DUELO.x, this.spriteBaseY + DUELO.dy, DUELO.z);
    }
    if (this.arbustoGroup) {
      this.arbustoGroup.visible = true;
      this.arbustoGroup.position.set(DUELO.x, 0, DUELO.arbustoZ);
      this.arbustoGroup.rotation.y = Math.atan2(-DUELO.x, 0.55 - DUELO.arbustoZ);
    }
    if (this.arbustoSombra) this.arbustoSombra.position.set(DUELO.x, 0.004, DUELO.arbustoZ);
    this.setState('present', 2.2);
    // duelo limpio de poderes previos
    this._endPower();
    // v2.94: el PRIMER superpoder llega antes en los duelos difíciles
    this._powerCd = this._nvCfg().primer;
    this._pendingPower = null;
    this._rallyFired = false;
    // v2.90: SIN pistola en la mano libre — la pala está SIEMPRE en la
    // mano y el revólver SOLO aparece en el duelo del «Disparo certero».
    this._gunVisible(false);
    this.musicOn();
    const upKey = nv === 3 ? 'duelo_up3' : (nv === 2 ? 'duelo_up2' : 'duelo_up');
    g.rules.message = tx(upKey);
    g.audio.announce(tx(upKey), true);
    this._playLaugh(0.65);
  }

  /** v2.94: config de dificultad del duelo VIGENTE (DUELO_NV). */
  _nvCfg() {
    const base = DUELO_NV[(this._duelNv || 1) - 1] || DUELO_NV[0];
    // v3.6.18 (ronda 24): en rejugada LEYENDA el forajido afila la puntería
    // (sólo campeón; el camino normal queda EXACTAMENTE igual).
    if (!this._leyendaOn) return base;
    return {
      aiMul: base.aiMul * 1.15,
      chance: Math.min(0.60, base.chance + 0.06),
      cooldown: Math.max(6.0, base.cooldown - 1.5),
      primer: Math.max(3.0, base.primer - 1.0),
      warn: base.warn,
    };
  }

  /* ======================================================================
   *  v2.94 · ETAPA 2 — ASEDIO AL ESCONDITE (y ETAPA 4 — ASALTO AL TREN):
   *  arranque/cierre desde la sala. La física va por testStep/testActive
   *  (el núcleo la delega); el cierre restaura la SALA al detalle.
   *  ====================================================================== */
  _startAsedio() {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('msg_guest'); return; }
    // v2.106: cartel explicativo ANTES de entrar en la prueba
    this._instrGo('asedio', () => {
      if (!this.active) return;
      this._endPower();
      this._stageMode = 'asedio';
      this.loadWaveJingle();      // v2.99: el cartel suena desde el primero
      this._asedio = new AsedioAction(this);
      this._asedio.start();
    });
  }
  _startTren() {
    const g = this.game;
    if (g.net.online) { g.rules.message = tx('msg_guest'); return; }
    // v2.106: cartel explicativo ANTES de entrar en la prueba
    this._instrGo('tren', () => {
      if (!this.active) return;
      this._endPower();
      this._stageMode = 'tren';
      // v2.122 · UNA MELODÍA: el vagón tiene SU música (vagon.mp3 en el
      // TrenAction, ranura aparte de esta BSO). Si el saloon sigue sonando
      // aquí, las DOS se solapan todo el trayecto — se retira ANTES de
      // arrancar el tren y _endPrueba() la trae de vuelta a la sala.
      this.musicOff();
      this._tren = new TrenAction(this);
      this._tren.start();
    });
  }
  /** Fin del ASEDIO: etapa superada → destapa el mapa; luego SALA. */
  _endAsedio(won) {
    const a = this._asedio;
    // v3.6.15 (ronda 18 · EMBUDO COMPLETO): champ_rank del ASEDIO (etapa 2).
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'oeste', prueba: 'asedio', win: !!won,
        score: 0, stars: 0,
        kills: Math.max(0, Math.min(12, (a && a.kills) | 0)),
        wave: Math.max(1, Math.min(3, (a && a.wave) | 0)),
      });
    } catch (e) { /* el reporte nunca rompe */ }
    this._stageMode = null;
    this._asedio = null;
    if (a) a.dispose();
    this._endPrueba(won, 2);
  }
  /** Fin del TREN: etapa superada → destapa el mapa; luego SALA. */
  _endTren(won) {
    const t = this._tren;
    // v3.6.15 (ronda 18 · EMBUDO COMPLETO): champ_rank del TREN (etapa 4).
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'oeste', prueba: 'tren', win: !!won,
        score: 0, stars: 0,
        ingots: Math.max(0, Math.min(99, (t && t.ingots) | 0)),
        wave: Math.max(1, Math.min(3, (t && t.wave) | 0)),
      });
    } catch (e) { /* el reporte nunca rompe */ }
    this._stageMode = null;
    this._tren = null;
    if (t) t.dispose();
    this._endPrueba(won, 4);
  }
  /** RESTAURACIÓN de la sala tras una prueba (común asedio/tren). */
  _endPrueba(won, stage) {
    const g = this.game;
    this._freeGunApply(false);
    this._gunVisible(false);
    if (this.fx) this.fx.laserVisible(false);
    g.rules.state = STATE_NAME;          // el árbitro sigue dormido
    g.ball.ignoreNet = true;
    g.freezeT = 0;
    for (const m of (this._netParts || [])) m.visible = false;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    // sala de vuelta: room, troqueles, mapa, cartel, forajido y arbusto
    if (g.roomGroup) g.roomGroup.visible = true;
    g.champDecorHidden = false;          // v2.95: troqueles de vuelta
    if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = true;
    this.mapa.visible = true;
    this.cartel.visible = true;
    if (this.sprite) {
      this.sprite.visible = true;
      this.sprite.position.set(OESTE.x, this.spriteBaseY, OESTE.z);
      this.sprite.rotation.z = 0;
      this._hitShakeT = 0; this._fadeT = 0;
    }
    if (this.arbustoGroup) {
      this.arbustoGroup.visible = true;
      this.arbustoGroup.position.set(ARBUSTO.x, 0, ARBUSTO.z);
    }
    if (this.arbustoSombra) this.arbustoSombra.position.set(ARBUSTO.x, 0.004, ARBUSTO.z);
    this._parkMainBall();
    this.setState('idle', 0);
    this._armT = 1.2;                    // anti-gesto accidental de vuelta
    // v2.96: REJUGADA fallida — el progreso real vuelve antes de abrir sala
    if (!won && this._replayReal != null) {
      this.stage = this._replayReal;
      this._replayReal = null;
      this._leyendaOn = false;   // v3.6.18 (ronda 24): la LEYENDA se corta al caer
      this._refreshMap();
    }
    if (won) this._stageClear(stage);
    this.paintCartel();
    // v2.122 · UNA MELODÍA: de vuelta en la sala vuelve la BSO del saloon
    // (tras el TREN quedó apagada; en el asedio sigue viva y musicOn es
    // idempotente — sin dobles fuentes jamás).
    this.musicOn();
  }

  /** v2.94 · ETAPA SUPERADA: persiste el progreso, levanta la TAPA del mapa,
   *  mueve el ANILLO al nodo siguiente y anuncia. La etapa 5 → CAMPEÓN. */
  _stageClear(stage) {
    const g = this.game;
    // v3.6.18 (ronda 24): las REJUGADAS se resuelven ANTES del gate del
    // campeón — repetir la coronación no existe (el camino ya está sellado)
    // y la LEYENDA del duelo final necesita su sello, no otra corona.
    if (this._replayReal != null) {
      const nReplay = stage;
      this.stage = this._replayReal;
      this._replayReal = null;
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e9) { /* */ }
      this._refreshMap();
      // v3.6.18 (ronda 24): SELLO DE LEYENDA — la etapa rejugada en modo
      // leyenda queda sellada; 5/5 dispara la medalla LEYENDA DEL OESTE.
      if (this._leyendaOn) {
        this._leyendaOn = false;
        try { localStorage.setItem(this.storageKey('leyenda_' + nReplay), '1'); } catch (eL) { /* */ }
        const sellos = this._sellosLeyenda();
        g.rules.message = sellos >= 5 ? tx('leyenda_medalla_msg') : tx('leyenda_sello').replace('{n}', String(nReplay));
        g.audio.announce(g.rules.message, true);
        this._setStateSilent('surprised', 2.2);
        this.sfx('diana', 0);
        if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
        if (sellos >= 5) this._leyendaFlow();
        return;
      }
      g.rules.message = tx('replay_done');
      g.audio.announce(tx('replay_done'), true);
      this._setStateSilent('surprised', 2.2);
      this.sfx('diana', 0);
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
      return;
    }
    if (stage >= 5) {
      this._championFlow();
      return;
    }
    this.stage = Math.max(this.stage, Math.min(5, stage + 1));
    try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e) { /* */ }
    // v3.6.15 (ronda 18 · EMBUDO COMPLETO): avance de etapa (embudo por champ,
    // igual que La Locura desde la ronda 11).
    try { __PP_TELE.ev('stage', { n: this.stage, id: 'oeste' }); } catch (eT) { /* */ }
    this._refreshMap();
    g.rules.message = tx('etapa_hecho');
    g.audio.announce(tx('etapa_hecho'), true);
    this._setStateSilent('surprised', 2.2);
    this.sfx('diana', 0);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.8, 200);
  }

  /** v2.94 · ¡CAMPEÓN DEL SALVAJE OESTE! (duelo FINAL ganado): insignia en
   *  la sala, registro y risa amarga del forajido. */
  _championFlow() {
    const g = this.game;
    this._champion = true;
    try { localStorage.setItem(this.storageKey('champ'), '1'); } catch (e) { /* */ }
    this.stage = 5;
    try { localStorage.setItem(this.storageKey('stage'), '5'); } catch (e2) { /* */ }
    this._refreshMap();
    this._insigniaShow();
    g.rules.message = tx('champ_gana');
    g.audio.announce(tx('champ_gana'), true);
    // v3.6.18 (ronda 24 · CORONACIÓN): fecha del título + panel épico del
    // núcleo con título propio, mensaje del forajido y fila de ESTADÍSTICAS.
    try { localStorage.setItem(this.storageKey('fecha'), new Date().toISOString()); } catch (eF) { /* */ }
    try {
      const C = window.__PP_CORE;
      if (C && C.showChampConseguido) {
        const fecha = new Date();
        const fTxt = (C.lang && C.lang() === 'en')
          ? fecha.toLocaleDateString('en-US', { day: 'numeric', month: 'short', year: 'numeric' })
          : fecha.toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' });
        C.showChampConseguido('oeste', {
          campeon: true,
          title: tx('coronacion_titulo'),
          msg: tx('coronacion_msg'),
          dur: 14,
          stats: [
            [tx('coronacion_pts'), String(this.puntos | 0)],
            [tx('coronacion_duelos'), String(this.duelWins | 0)],
            [tx('coronacion_fecha'), fTxt],
          ],
        });
      }
    } catch (e) { /* */ }
    // v3.6.15 (ronda 18 · EMBUDO COMPLETO): ¡un campeón más en el Oeste!
    try { __PP_TELE.ev('champion', { id: 'oeste' }); } catch (eC) { /* */ }
    this._setStateSilent('defeated', 5);
    this.sfx('diana', 0);
    this._playLaugh(0.8);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 1.0, 260);
    // ranking mundial (convención v2.70)
    try {
      const W = (typeof window !== 'undefined' && window.__PP_WORLD);
      if (W && typeof W.submit === 'function') {
        let nm = '';
        try { nm = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e3) { /* */ }
        Promise.resolve(W.submit('oeste', { n: nm || 'Anónimo', p: this.puntos | 0, a: '★' }))
          .catch(() => { /* nunca rompe */ });
      }
    } catch (e4) { /* */ }
  }

  /** v3.6.18 (ronda 24): cuántos sellos de leyenda lleva el campeón. */
  _sellosLeyenda() {
    let n = 0;
    for (let i = 1; i <= 5; i++) {
      try { if (localStorage.getItem(this.storageKey('leyenda_' + i)) === '1') n++; } catch (e) { /* */ }
    }
    return n;
  }

  /** v3.6.18 (ronda 24 · ¡LEYENDA DEL OESTE!): las 5 etapas selladas en
   *  modo leyenda — medalla, registro, telemetría y una última risa. */
  _leyendaFlow() {
    const g = this.game;
    try { localStorage.setItem(this.storageKey('leyenda'), '1'); } catch (e) { /* */ }
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'oeste', prueba: 'leyenda', win: true,
        score: this.puntos | 0, stars: 3,
      });
    } catch (eT) { /* el reporte nunca rompe */ }
    try {
      const C = window.__PP_CORE;
      if (C && C.showChampConseguido) {
        C.showChampConseguido('oeste', {
          campeon: true,
          title: tx('leyenda_medalla_titulo'),
          msg: tx('leyenda_medalla_msg'),
          dur: 12,
        });
      }
    } catch (e) { /* */ }
    this._setStateSilent('defeated', 4);
    this.sfx('diana', 0);
    this._playLaugh(0.9);
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 1.0, 260);
  }

  /** v2.94 · INSIGNIA del sheriff (assets/insignia.png): panel dorado con
   *  anillo que brilla en la sala del campeonato — el premio final. */
  _insigniaShow() {
    try {
      const g = this.game;
      if (!this._insignia) {
        const grp = new THREE.Group();
        const ring = new THREE.Mesh(
          new THREE.RingGeometry(0.40, 0.46, 40),
          new THREE.MeshBasicMaterial({
            color: 0xf6d34c, transparent: true, opacity: 0.55,
            blending: THREE.AdditiveBlending, depthWrite: false,
            side: THREE.DoubleSide,
          }),
        );
        ring.renderOrder = 5;
        grp.add(ring);
        const plane = new THREE.Mesh(
          new THREE.PlaneGeometry(0.62, 0.62),
          new THREE.MeshBasicMaterial({ transparent: true, depthWrite: false }),
        );
        plane.renderOrder = 6;
        grp.add(plane);
        const img = new Image();
        img.onload = () => {
          const t = new THREE.Texture();
          t.colorSpace = THREE.SRGBColorSpace;
          t.image = img; t.needsUpdate = true;
          plane.material.map = t;
          plane.material.needsUpdate = true;
        };
        img.src = new URL('./assets/insignia.png', import.meta.url).href;
        grp.position.set(-1.72, 1.42, -3.4);
        // mira al CENTRO de la sala (donde está el jugador, como el decor)
        grp.rotation.y = Math.atan2(0 - grp.position.x, 0.55 - grp.position.z);
        this.group.add(grp);
        this._insignia = { grp, ring };
      }
      this._insignia.grp.visible = true;
    } catch (e) { /* sin insignia: la sala sigue */ }
  }

  /** Frame a frame EN DUELO (la sala usa su update de siempre). */
  _updateDuel(dt) {
    const g = this.game;
    this._duelT += dt;
    if (this._armT > 0) this._armT = 0;
    // v2.91 · FUNDIDO de la pose de impacto: 1 s — la imagen se oscurece
    // hasta negro (0-0,5) y de ahí va apareciendo la pose normal (0,5-1)
    if (this._fadeT > 0) {
      this._duelFadeStep(dt);
    } else if (this._transient > 0) {
      this._transient -= dt;
      if (this._transient <= 0) this._duelFadeStart();
    }
    // v2.91 · TEMBLOR del impacto (los 4 s de pose): el sprite vibra
    if (this.sprite && this._hitShakeT > 0) {
      this._hitShakeT -= dt;
      this.sprite.position.x = DUELO.x + (Math.random() * 2 - 1) * 0.012;
      this.sprite.rotation.z = (Math.random() * 2 - 1) * 0.02;
      if (this._hitShakeT <= 0) {
        this._hitShakeT = 0;                 // v2.91: sin residuo negativo
        this.sprite.position.x = DUELO.x;
        this.sprite.rotation.z = 0;
      }
    }
    if (this.sprite) {
      this.sprite.position.y = this.spriteBaseY + DUELO.dy + Math.sin(this._t * 1.1) * 0.012;
    }
    // ARBUSTO RODANTE delante del forajido (su «tapador» en la mesa)
    if (this.arbustoGroup && this.arbustoMesh) {
      const ab = ARBUSTO;
      const dx = ab.amplitud * Math.sin(this._t * ((Math.PI * 2) / ab.periodo));
      this.arbustoGroup.position.set(DUELO.x + dx, 0, DUELO.arbustoZ);
      this.arbustoMesh.rotation.z = -dx / (ab.h / 2);
      if (this.arbustoSombra) this.arbustoSombra.position.set(DUELO.x + dx, 0.004, DUELO.arbustoZ);
    }
    // PODERES: aviso pendiente → efecto → cooldown (motor del CLOWN/WIZARD)
    if (this._pendingPower) {
      this._pendT -= dt;
      if (this._pendT <= 0) this._launchPending();
    }
    if (this._powerT > 0) this._powerT -= dt;
    if (this._powerCd > 0) this._powerCd -= dt;
    if (this._duelo) { this._duelo.update(dt); if (this._duelo.done) { this._duelo.dispose(); this._duelo = null; } }
    if (this._dyn) { this._dyn.update(dt); if (this._dyn.done) { this._dyn.dispose(); this._dyn = null; } }
    // v2.120: actualización de los dos poderes nuevos
    if (this._tormenta) { this._tormenta.update(dt); if (this._tormenta.done) { this._tormenta.dispose(); this._tormenta = null; } }
    if (this._stamp) { this._stamp.update(dt); if (this._stamp.done) { this._stamp.dispose(); this._stamp = null; } }
    this.maybeTriggerPower();
    if (this.fx) this.fx.update(dt);
    if (this.powerSign) this.powerSign.update(dt);
    this._syncMusicGain();
    // revancha (gatillo en «over» del núcleo): la BSO vuelve al servir
    if (!this._musSDK.sonando() && g.rules.state === 'serve') this.musicOn();
  }

  /* ================= SUPERPODERES (motor de dos fases v2.71) ============== */

  /** ¿Toca lanzar superpoder? SOLO con la bola en juego y viniendo hacia el
   *  jugador — las mismas puertas del CLOWN y del WIZARD. v2.94: la
   *  probabilidad crece con el NIVEL del duelo (DUELO_NV). */
  maybeTriggerPower() {
    if (!this.active || !this._rivalOn || this._pendingPower) return;
    if (this._powerT > 0 || this._powerCd > 0) return;
    const g = this.game;
    const r = g.rules;
    const ball = g.ball;
    if (!ball || !ball.vel) return;
    if (r.state !== 'rally' || this._rallyFired) { this._toward = false; return; }
    if ((r.rallyHits || 0) < OESTE_POWER.minRallyHits) { this._toward = false; return; }
    const toward = ball.vel.z > 0.35;
    const edge = toward && !this._toward;
    this._toward = toward;
    if (!edge) return;
    if (Math.random() < this._nvCfg().chance) this.firePower();
  }

  /** Los CUATRO poderes del forajido (v2.120: + TORMENTA y ESTAMPIDA —
   *  el revólver necesita su GLB cargado; los otros dos salen ya).
   *  v2.121: TODOS llevan MINIATURA propia en el cartel — los clásicos
   *  disparo/dinamita estrenan powerdisparo.png y powertnt.png. */
  _powerList() {
    const list = [];
    if (this._revolverReady || this._revolverTried) {
      list.push({ kind: 'disparo', icon: 'powerdisparo.png' });
    }
    if (this._tntReady || this._tntTried) list.push({ kind: 'dinamita', icon: 'powertnt.png' });
    list.push({ kind: 'arena', icon: 'powerarena.png' });
    list.push({ kind: 'estampida', icon: 'powerestampida.png' });
    if (!list.length) list.push({ kind: 'dinamita', icon: 'powertnt.png' });   // respaldo
    return list;
  }

  /** FASE 1 — AVISO: cartel «¡SUPERPODER!» + risa + congelación breve. */
  firePower(forceKind) {
    const g = this.game;
    let list = this._powerList().filter((p) => p && p.kind);
    if (!list.length) return;
    if (forceKind) {
      const hit = list.filter((p) => p.kind === forceKind);
      if (hit.length) list = hit;
    } else if (list.length > 1) {
      const alt = list.filter((p) => p.kind !== this._lastPower);
      if (alt.length) list = alt;
    }
    const cfg = list[(Math.random() * list.length) | 0];
    this._pendingPower = cfg;
    this._pendT = OESTE_POWER.warn;
    this._rallyFired = true;
    this._setStateSilent('angry', Math.min(3.4, Math.max(2.2, OESTE_POWER.warn * 1.3)));
    // v2.120: el cartel muestra el ICONO del superpoder anunciado
    this.powerSign.show(cfg.icon ? this._A(cfg.icon) : null);
    // v3.6.2-SDK2: congela() del SDK (patrón locura v2.40, una sola fuente)
    congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1);
    this._playLaugh(0.9);
    g.rules.message = tx('pw_warn');
    if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.6, 200);
  }

  /** FASE 2 — EFECTO en pleno rallye (si el punto sigue vivo). */
  _launchPending() {
    const cfg = this._pendingPower;
    this._pendingPower = null;
    this._pendT = 0;
    if (!cfg) return;
    const g = this.game;
    if (g.rules.state !== 'rally') {
      this._powerCd = 3;
      this._rallyFired = false;
      return;
    }
    this._powerKind = cfg.kind;
    this._lastPower = cfg.kind;
    this._powerCd = this._nvCfg().cooldown;   // v2.94: cooldown por nivel
    if (cfg.kind === 'disparo') {
      // v2.89 · EL DUELO: bola congelada + diana + pala-revólver
      this._duelo = new DueloAction(this);
      this._duelo.start();
      this._powerT = DUELO_P.drawT + DUELO_P.window + 1.5;
      g.rules.message = tx('pw_disparo');
    } else if (cfg.kind === 'arena') {
      // v2.120 · TORMENTA DE ARENA: polvo sobre TU campo + rodantes
      this._tormenta = new TormentaAction(this);
      this._tormenta.start();
      this._powerT = TORMENTA.dur;
      g.rules.message = tx('pw_arena');
    } else if (cfg.kind === 'estampida') {
      // v2.120 · ESTAMPIDA: la manada cruza detrás de la mesa
      this._stamp = new EstampidaAction(this);
      this._stamp.start();
      this._powerT = ESTAMPIDA.dur;
      g.rules.message = tx('pw_estampida');
    } else {
      this._dyn = new DinamitaAction(this);
      this._dyn.start();
      // v2.90: la salva lanza 2-5 cartuchos (1 s entre lanzamientos)
      this._powerT = this._dyn.totalT;
      g.rules.message = tx('pw_dinamita');
    }
  }

  /** Fin de poderes (punto nuevo, salida o revancha). Los manchones NO se
   *  borran: se desvanecen solos (~6 s), como pide el artista. */
  _endPower() {
    if (this._duelo) { this._duelo.dispose(); this._duelo = null; }
    if (this._rev) { this._rev.dispose(); this._rev = null; }
    if (this._dyn) { this._dyn.dispose(); this._dyn = null; }
    // v2.120: los dos poderes nuevos también se apagan aquí (mismo cierre)
    if (this._tormenta) { this._tormenta.dispose(); this._tormenta = null; }
    if (this._stamp) { this._stamp.dispose(); this._stamp = null; }
    this._powerKind = null;
    this._powerT = 0;
    // v2.120: cierre íntegro del motor (aviso pendiente y flancos) — antes
    // quedaban colgados y lo parcheaba cada _startDuel.
    this._pendingPower = null;
    this._pendT = 0;
    this._rallyFired = false;
    this._toward = false;
    this._restoreBallTint();
  }

  /** La bola MANCHADA por el Disparo certero (oscura hasta fin del punto). */
  _ballDarkApply() {
    const g = this.game;
    const m = g.ballMesh;
    if (!m || !m.material || this._ballDark) return;
    this._ballDark = true;
    this._ballDarkSaved = {
      col: m.material.color.getHex(),
      em: m.material.emissive ? m.material.emissive.getHex() : null,
      ei: m.material.emissiveIntensity,
    };
    m.material.color.setHex(0x181310);          // v2.89: casi NEGRA
    if (m.material.emissive) m.material.emissive.setHex(0x0a0503);
  }
  _restoreBallTint() {
    if (!this._ballDark) return;
    const g = this.game;
    const m = g.ballMesh;
    this._ballDark = false;
    if (m && m.material) {
      // vuelve a la bola BLANCA del campeonato (v2.89, visible en la madera;
      // el original lo guarda _ballSaved)
      m.material.color.setHex(OESTE.ballColors[0]);
      if (m.material.emissive) m.material.emissive.setHex(OESTE.ballEmissive);
    }
    this._ballDarkSaved = null;
  }

  /** v2.90: LOS CONTADORES 3·2·1 HAN DESAPARECIDO (petición del artista):
   *  ni sobre la diana del duelo ni sobre los cartuchos de dinamita. Solo
   *  queda el tic-tac sonoro como aviso del tiempo que queda. */

  /* ====== v2.90 · SIN PISTOLA EN LA MANO LIBRE ==========================
   *  La pistola antigua (pistol.glb) está RETIRADA de este campeonato
   *  (indicación del artista): la pala está SIEMPRE en su mano y el
   *  revólver SOLO aparece en el duelo del «Disparo certero». Ya no hay
   *  _loadGunArt/_attachGunArt: nada se carga ni se apila en las monturas.
   *  ====================================================================== */
  /** Normaliza un GLB: eje más largo → Z (cañón/madera), tamaño objetivo. */
  /** v2.89 · Centro/base medidos sobre VÉRTICES REALES en espacio raíz.
   *  Box3.setFromObject usa las boundingBox cacheadas por nodo y con los
   *  GLB del artista (nodos con transforms enormes) desincroniza: el
   *  centrado salía desplazado y los modelos «no se veían». */
  _medirVertices(root) {
    const v = new THREE.Vector3();
    const out = { cx: 0, cy: 0, cz: 0, minY: 0, n: 0 };
    let sx = 0, sy = 0, sz = 0;
    let mny = Infinity;
    root.updateMatrixWorld(true);
    root.traverse((o) => {
      if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
      const pa = o.geometry.attributes.position;
      if (!pa) return;
      const mm = o.matrixWorld.elements;
      const step = Math.max(1, Math.floor(pa.count / 800));
      for (let i = 0; i < pa.count; i += step) {
        v.fromBufferAttribute(pa, i);
        const x = mm[0] * v.x + mm[4] * v.y + mm[8] * v.z + mm[12];
        const y = mm[1] * v.x + mm[5] * v.y + mm[9] * v.z + mm[13];
        const z = mm[2] * v.x + mm[6] * v.y + mm[10] * v.z + mm[14];
        if (!isFinite(x) || !isFinite(y) || !isFinite(z)) continue;
        sx += x; sy += y; sz += z; out.n++;
        if (y < mny) mny = y;
      }
    });
    if (out.n > 0) {
      out.cx = sx / out.n; out.cy = sy / out.n; out.cz = sz / out.n;
      out.minY = mny;
    }
    return out;
  }
  _normalizeGunArt(scene, targetLen, encara) {
    const box = new THREE.Box3().setFromObject(scene);
    if (box.isEmpty()) return null;
    const size = box.getSize(new THREE.Vector3());
    const root = new THREE.Group();
    root.add(scene);
    const ax = [['x', size.x], ['y', size.y], ['z', size.z]].sort((a, b) => b[1] - a[1]);
    if (ax[0][0] === 'x') scene.rotation.y = Math.PI / 2;
    else if (ax[0][0] === 'y') scene.rotation.x = -Math.PI / 2;
    const s2 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const ax2 = [['x', s2.x], ['y', s2.y]].sort((a, b) => b[1] - a[1])[0][0];
    if (ax2 === 'x') scene.rotateZ(Math.PI / 2);
    const s3 = new THREE.Box3().setFromObject(root).getSize(new THREE.Vector3());
    const len = Math.max(s3.x, s3.y, s3.z) || 1;
    root.scale.setScalar(targetLen / len);
    if (encara) {
      // boca del cañón hacia -Z (el punto más bajo del modelo no puede caer
      // en la mitad -Z; el revólver del artista usa la convención del mago)
      try {
        root.updateMatrixWorld(true);
        const lv = new THREE.Vector3(), tv = new THREE.Vector3();
        let found = false;
        root.traverse((o) => {
          if (!o.isMesh || !o.geometry || !o.geometry.attributes) return;
          const pa = o.geometry.attributes.position;
          if (!pa) return;
          for (let i = 0; i < pa.count; i++) {
            tv.fromBufferAttribute(pa, i).applyMatrix4(o.matrixWorld);
            if (!found || tv.y < lv.y) { lv.copy(tv); found = true; }
          }
        });
        if (found && lv.z < 0) root.rotation.y += Math.PI;
      } catch (e) { /* orientación original si el barrido falla */ }
      // v2.89 · FIX RAÍZ: el centrado va en el NODO INTERNO (root.position
      // lo pisa el consumidor al colocar el modelo) y se mide con VÉRTICES
      // (Box3 cacheado desincronizaba con estos GLB).
      const mb = this._medirVertices(root);
      // el centro medido está en espacio PADRE (escala del root incluida):
      // scene.position es LOCAL al root → dividir por la escala
      const inv = 1 / (root.scale.x || 1);
      scene.position.x -= mb.cx * inv;
      scene.position.y -= (mb.minY + 0.055) * inv;   // agarre bajo el origen
      scene.position.z -= mb.cz * inv;
      root.updateMatrixWorld(true);
    } else {
      // TNT/revólver: centrado con la BASE en el origen (se planta en la
      // mesa) — nodo interno + vértices reales (fix raíz v2.89).
      const mb = this._medirVertices(root);
      const inv = 1 / (root.scale.x || 1);   // centro medido en espacio padre
      scene.position.x -= mb.cx * inv;
      scene.position.y -= mb.minY * inv;
      scene.position.z -= mb.cz * inv;
    }
    return root;
  }
  _gunVisible(on) {
    const g = this.game;
    if (!g.gunMounts) return;
    for (let k = 0; k < 2; k++) {
      if (g.gunMounts[k]) g.gunMounts[k].visible = !!on && k === (1 - g.paddleHand);
    }
  }

  /** GATILLO del DUELO (el núcleo lo trae hasta aquí en rallye mientras
   *  paddleGunArmed esté activo). v2.90: el rayo sale de la boca REAL del
   *  cañón del revólver en mano (medida por vértices) y sigue su EJE —
   *  exactamente el mismo rayo que la mira láser (WYSIWYG). Se puede
   *  disparar UNA Y OTRA VEZ durante todo el duelo (0,16 s entre tiros). */
  fireGun(i) {
    // v2.90: SOLO existe el disparo del DUELO (revólver en la mano de la
    // pala). Sin pistola en la mano libre no hay más blancos: la dinamita
    // ya no se neutraliza a tiros (se batea con la pala o estalla).
    if (!this.active || !this._duelOn) return;
    if (!(this._duelo && this._duelo.phase === 'duel')) return;
    const g = this.game;
    const ray = this._gunRay();
    if (!ray) return;
    const now = performance.now() / 1000;
    if (now - (this._gunLast || 0) < 0.16) return;   // disparos libres 3 s
    this._gunLast = now;
    const rPos = ray.pos, rDir = ray.dir;
    // ¿acierta a la DIANA del duelo? (rayo vs esfera generosa, v2.89)
    let len = 5;
    if (this.diana && this.diana.visible) {
      const toD = this.diana.position.clone().sub(rPos);
      const t = clamp(toD.dot(rDir), 0, 8);
      const closest = rDir.clone().multiplyScalar(t).add(rPos);
      if (closest.distanceTo(this.diana.position) < DUELO_P.dianaRadio) {
        len = Math.max(0.3, t);
        this._duelo.acierto();
        if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.7, 130);
      }
    }
    if (this.fx) {
      this.fx.beam(rPos, rDir, len);
      // v2.91: fogonazo en la BOCA del revólver con cada tiro
      this.fx.flash(ray.pos, 1.1, 0xffd98a);
    }
    this.sfx('disparo', 0);   // v2.91: ¡BANG! del revólver del oeste en cada disparo
  }

  /* ================= GLB del revólver y la dinamita (caché) =============== */
  _loadProps() {
    if (this._propsLoading) return;
    this._propsLoading = true;
    const done = () => { if (!this._revolverReady && !this._tntReady) this._propsLoading = false; };
    try {
      new GLTFLoader().load(this.manifest.revolverUrl, (gltf) => {
        try {
          this._revolverModel = this._normalizeGunArt(gltf.scene, DISPARO.escala, false);
          if (this._revolverModel) {
            // v2.91: BOCA DEL CAÑÓN hacia -Z GARANTIZADA POR MEDICIÓN
            // (fuera la heurística frágil del «y medio» de las mitades Z,
            // que podía dar la vuelta al revólver): se mide la boca en
            // espacio LOCAL del modelo y se gira el NODO INTERNO 180° si
            // cayera en +Z. El giro va en el nodo interno (el dibujo del
            // desenfundado anima la rotación Y del root y la pisaría).
            try {
              let m = this._medirCañon(this._revolverModel);
              if (m.muzzle && m.muzzle.z > 0) {
                const inner = this._revolverModel.children[0] || this._revolverModel;
                inner.rotation.y += Math.PI;
                // v2.93: re-medir DESPUÉS del volteo para guardar la boca
                // en -Z LOCAL exacta (la usan el duelo y el encaramiento)
                m = this._medirCañon(this._revolverModel);
              }
              if (m.muzzle) {
                this._revMuzzleLocal = m.muzzle.clone();   // unidades locales del arte
                this._revBarrelLocal = m.dir ? m.dir.clone() : new THREE.Vector3(0, 0, -1);
              }
            } catch (e) { /* orientación original si la medición falla */ }
          }
          this._revolverReady = true;
          // v2.95: si la PRUEBA ya arrancó sin GLB, el revólver entra en
          // mano en cuanto el modelo cargue — v2.98: DOS revólveres si el
          // forajido está DESTAPADO (reveal); fuera el revólver libre
          if (this._stageMode === 'asedio' && this._asedio &&
              this._asedio.phase === 'reveal') {
            try {
              if (!this._twoGuns) this._twoGunApply(true);
              // v2.99: el REVÓLVER DEL FORAJIDO también entra con el GLB
              if (!this._asedio._outlawGun && this._asedio._zona) {
                this._asedio._outlawGunApply(this._asedio._zona.x,
                  ASEDIO.outZ);
              }
            } catch (e2) { /* */ }
          }
          // v2.111: igual en el VAGÓN — pala + revólver desde el arranque
          if (this._stageMode === 'tren' && this._tren) {
            try { this._freeGunApply(true); } catch (e2) { /* */ }
          }
        } catch (e) { /* reserva de cajas */ }
        done();
      }, undefined, () => { this._revolverTried = true; done(); });
      new GLTFLoader().load(this.manifest.tntUrl, (gltf) => {
        try {
          this._tntModel = this._normalizeGunArt(gltf.scene, DINAMITA.escala, false);
          this._tntReady = true;
        } catch (e) { /* reserva de cajas */ }
        done();
      }, undefined, () => { this._tntTried = true; done(); });
    } catch (e) { this._propsLoading = false; }
  }

  /* ================= SONIDOS del duelo (Web Audio del núcleo) ============= */
  sfx(name, pan) {
    const g = this.game;
    const A = g.audio;
    if (!A || !A.ctx || A.ctx.state !== 'running') return;
    const p = pan || 0;
    try {
      if (name === 'disparo') {
        // ¡BANG! de duelo: estampido + grave + metralla
        A.playNoise(0.20, 750, 0.7, 1.0, p, 'lowpass');
        A.playOsc(150, 45, 0.26, 'triangle', 0.95, p);
        A.playNoise(0.05, 3200, 1.2, 0.42, p);
      } else if (name === 'impacto') {
        A.playNoise(0.09, 2400, 1.4, 0.75, p);
        A.playOsc(1150, 260, 0.11, 'square', 0.5, p);
        A.playOsc(180, 90, 0.09, 'sine', 0.4, p);
      } else if (name === 'boom') {
        A.playNoise(0.55, 240, 0.8, 1.0, p, 'lowpass');
        A.playOsc(85, 32, 0.55, 'sine', 1.0, p);
        A.playNoise(0.12, 2800, 1.1, 0.42, p);
      } else if (name === 'mecha') {
        A.playNoise(0.07, 5400, 2.6, 0.05, p);
      } else if (name === 'tick') {
        A.playOsc(920, 640, 0.08, 'square', 0.34, 0);
      } else if (name === 'pew') {
        A.playOsc(880, 220, 0.12, 'sawtooth', 0.14, 0);
      } else if (name === 'diana') {
        // ¡TING! metálico de diana alcanzada (v2.89)
        A.playOsc(1560, 1180, 0.16, 'square', 0.4, 0);
        A.playNoise(0.05, 4200, 1.6, 0.28, 0);
      } else if (name === 'desenfundar') {
        A.playNoise(0.08, 1800, 1.2, 0.3, p);
        A.playOsc(520, 240, 0.10, 'triangle', 0.25, p);
      } else if (name === 'lanzar') {
        A.playNoise(0.12, 900, 0.9, 0.3, p);
        A.playOsc(300, 520, 0.14, 'sine', 0.2, p);
      } else if (name === 'aterrizar') {
        A.playNoise(0.07, 500, 1.0, 0.5, 0, 'lowpass');
        A.playOsc(190, 120, 0.08, 'triangle', 0.45, 0);
      } else if (name === 'pala') {
        A.playNoise(0.05, 1400, 1.2, 0.55, 0);
        A.playOsc(210, 140, 0.09, 'triangle', 0.5, 0);
      } else if (name === 'llanto') {
        // v2.91 · LLANTO del forajido al comerse el disparo: tres sollozos
        // descendentes («uh… uh… uuhh…») con voz + octava grave
        const wail = (delay, f0, f1, dur, g0) => setTimeout(() => {
          try {
            A.playOsc(f0, f1, dur, 'sawtooth', g0, p);
            A.playOsc(f0 * 0.5, f1 * 0.5, dur, 'triangle', g0 * 0.7, p);
          } catch (e) { /* sin voz */ }
        }, delay);
        wail(0, 540, 330, 0.42, 0.20);
        wail(720, 480, 280, 0.46, 0.20);
        wail(1520, 420, 215, 0.62, 0.22);
      } else if (name === 'madera') {
        // v2.94 · GOLPE de madera (cobertura del asedio): toca seco + astillas
        A.playNoise(0.09, 900, 0.9, 0.6, p, 'lowpass');
        A.playOsc(220, 90, 0.09, 'triangle', 0.5, p);
      } else if (name === 'crash') {
        // v2.94 · REVIENTO de la cobertura: derrumbe de barriles y tablones
        A.playNoise(0.5, 420, 0.8, 0.9, p, 'lowpass');
        A.playOsc(120, 40, 0.4, 'triangle', 0.7, p);
        A.playNoise(0.16, 2400, 1.3, 0.4, p);
      } else if (name === 'coin') {
        // v2.94 · CANDADO abierto: ¡ting! dorado + monedas (arpegio rápido)
        A.playOsc(1560, 1180, 0.14, 'square', 0.4, 0);
        const arp = (delay, f) => setTimeout(() => {
          try { A.playOsc(f, f * 0.99, 0.12, 'triangle', 0.3, 0); } catch (e2) { /* */ }
        }, delay);
        arp(90, 1760); arp(180, 2093); arp(280, 2637);
        A.playNoise(0.06, 5200, 1.6, 0.24, 0);
      } else if (name === 'whistle') {
        // v2.94 · SILBATO del tren (dos tonos desafinados + aliento)
        A.playOsc(622, 610, 0.85, 'triangle', 0.34, 0);
        A.playOsc(784, 770, 0.85, 'triangle', 0.30, 0);
        A.playNoise(0.7, 1800, 0.5, 0.10, 0);
      } else if (name === 'whistle_long') {
        // v2.94 · SILBATO LARGO de llegada a la estación
        A.playOsc(622, 600, 1.7, 'triangle', 0.4, 0);
        A.playOsc(784, 760, 1.7, 'triangle', 0.36, 0);
        A.playOsc(622 * 0.5, 600 * 0.5, 1.7, 'sine', 0.22, 0);
        A.playNoise(1.5, 1500, 0.5, 0.12, 0);
      } else if (name === 'brake') {
        // v2.94 · FRENADO de la locomotora: chirrido metálico que cae
        A.playNoise(1.6, 2600, 1.0, 0.34, 0, 'highpass');
        A.playOsc(320, 90, 1.6, 'sawtooth', 0.16, 0);
      } else if (name === 'grito') {
        // v2.106 · ¡GRITO! del jugador al recibir la bala del forajido:
        // chillido agudo que CAE con vibrato + respiración (voz + octava)
        const grit = (delay, f0, f1, dur, g0) => setTimeout(() => {
          try {
            A.playOsc(f0, f1, dur, 'sawtooth', g0, 0);
            A.playOsc(f0 * 0.5, f1 * 0.5, dur, 'triangle', g0 * 0.7, 0);
          } catch (e2) { /* sin voz */ }
        }, delay);
        grit(0, 1040, 760, 0.18, 0.30);
        grit(150, 980, 620, 0.22, 0.26);
        grit(340, 900, 480, 0.30, 0.22);
        A.playNoise(0.16, 2200, 0.9, 0.14, 0);
      } else if (name === 'alarma') {
        // v2.99 · ALARMA al quedar 20 s de la OLEADA: cuatro pitidos urgentes
        const pip = (delay, f0, f1, dur, g0) => setTimeout(() => {
          try {
            A.playOsc(f0, f1, dur, 'square', g0, 0);
            A.playOsc(f0 * 0.5, f1 * 0.5, dur, 'square', g0 * 0.6, 0);
          } catch (e2) { /* */ }
        }, delay);
        pip(0, 880, 660, 0.17, 0.34);
        pip(430, 880, 660, 0.17, 0.34);
        pip(860, 880, 660, 0.17, 0.34);
        pip(1290, 880, 660, 0.26, 0.42);
      }
    } catch (e) { /* sin sonido: nunca rompe */ }
  }

  /* ================= RISA real del forajido (motor v2.54) =================
   *  v3.6.2-SDK2 (FASE 4): buffer y reproducción viven en el SDK de
   *  campeonatos (cache + lección v2.125 + silencio del arcade). El
   *  anti-spam de 3,2 s y el paneo 0,4 (opts.pan del SDK) se conservan
   *  aquí — misma conducta exacta. */
  loadLaugh() {
    try { this.__sfxSDK().precarga('risas.mp3'); } catch (e) { /* */ }
  }
  _playLaugh(vol) {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      const now = performance.now() / 1000;
      if (now - (this._laughLast || 0) < 3.2) return;
      const eng = this.__sfxSDK();
      if (!eng.tiene('risas.mp3')) {
        eng.precarga('risas.mp3');            // aún decodificando: sin gasto
        return;
      }
      this._laughLast = now;
      eng.play('risas.mp3', vol || 0.8, { pan: 0.4 });
    } catch (e) { /* */ }
  }

  /* v3.6.2-SDK2 · motor SFX del SDK de campeonatos (una instancia por
   * controlador, cache propia; assets relativos a ESTE módulo). */
  __sfxSDK() {
    if (!this.__sdkSfx) this.__sdkSfx = createSfx(import.meta.url, () => this.game);
    return this.__sdkSfx;
  }

  /* ============ v2.106 · RISA del PUEBLO (derrota del asedio) ============
   *  v3.6.2-SDK2 (FASE 4): motor en el SDK (precarga perezosa + play). */
  loadRisaPueblo() {
    try { this.__sfxSDK().precarga('risas_pueblo.mp3'); } catch (e) { /* */ }
  }
  _playRisaPueblo(vol) {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      const eng = this.__sfxSDK();
      eng.precarga('risas_pueblo.mp3');   // perezosa: si aún no está, pedirla ya
      eng.play('risas_pueblo.mp3', vol || 0.85);
    } catch (e) { /* */ }
  }

  /* ============ v2.99 · MÚSICA del CARTEL de oleada (oleada.mp3) ==========
   *  v3.6.2-SDK2 (FASE 4): motor en el SDK (precarga perezosa + play). */
  loadWaveJingle() {
    try { this.__sfxSDK().precarga('decor/asedio/oleada.mp3'); } catch (e) { /* */ }
  }
  _playWaveJingle(vol) {
    try {
      const g = this.game;
      const actx = g.audio && g.audio.ctx;
      if (!actx || actx.state !== 'running') return;
      const eng = this.__sfxSDK();
      eng.precarga('decor/asedio/oleada.mp3');   // perezosa: pedirla si falta
      eng.play('decor/asedio/oleada.mp3', vol || 0.85);
    } catch (e) { /* */ }
  }

  /* ================= Gancho de PUNTO del árbitro (v2.70) ================== */
  onPoint(it) {
    if (!this.active || !this._duelOn) return;
    const w = it && it.winner;
    this._rallyFired = false;
    this._toward = false;
    this._restoreBallTint();   // la bola manchada se limpia con el punto
    if (w === 'ai') {
      this._setStateSilent(Math.random() < 0.5 ? 'laughing' : 'victory', 2.2);
      if (Math.random() < 0.5) this._playLaugh(0.55);
      this.streakAi++;
    } else if (w === 'player') {
      this._setStateSilent(Math.random() < 0.5 ? 'surprised' : 'picando', 2.0);
      this.streakP++;
      this._puntosAdd(25, null);   // v2.119: punto de duelo a favor (+25)
    }
  }

  /** Fin del DUELO: registros + ranking mundial (convención v2.70) + poses. */
  onMatchOver(winner) {
    if (!this.active || !this._duelOn) return;
    const g = this.game;
    const w = winner === 'player';
    if (w) this._puntosAdd(250, null);   // v2.119: duelo ganado (+250)
    // v3.6.15 (ronda 18 · EMBUDO COMPLETO): champ_rank del DUELO (etapas
    // 1/3/5 · Nv 1-3). Espejo de La Locura (ronda 17): el agregador del
    // worker sólo lee champ/win/score/stars; nv y duelScore viajan crudos.
    try {
      __PP_TELE.ev('champ_rank', {
        champ: 'oeste', prueba: 'duelo', win: !!w,
        score: this.puntos | 0, stars: w ? 1 : 0,
        nv: this._duelNv || 1,
        duelScore: g.rules.scorePlayer | 0,
      });
    } catch (e) { /* el reporte nunca rompe */ }
    this.rank.push({ w, score: g.rules.scorePlayer | 0, stars: w ? 1 : 0, duel: true, pts: this.puntos | 0 });
    if (this.rank.length > 10) this.rank = this.rank.slice(-10);
    if (w) {
      this.duelWins = (this.duelWins || 0) + 1;
      try { localStorage.setItem(this.storageKey('duelwins'), String(this.duelWins)); } catch (e) { /* */ }
    }
    try { localStorage.setItem(this.storageKey('rank'), JSON.stringify(this.rank)); } catch (e2) { /* */ }
    try {
      const W = (typeof window !== 'undefined' && window.__PP_WORLD);
      if (w && W && typeof W.submit === 'function') {
        let nm = '';
        try { nm = String(localStorage.getItem('pp_player_name') || '').trim().slice(0, 12); } catch (e4) { /* */ }
        Promise.resolve(W.submit('oeste', {
          n: nm || 'Anónimo',
          p: this.puntos | 0,   // v2.119: el ranking publica los PUNTOS
          a: '✔',
        })).catch(() => { /* nunca rompe */ });
      }
    } catch (e3) { /* */ }
    this._endPower();
    this.musicOff();
    // v2.94: mensajes por nivel de duelo
    const nv = this._duelNv || 1;
    const ganaKey = nv === 3 ? 'duelo_gana3' : (nv === 2 ? 'duelo_gana2' : 'duelo_gana');
    const pierdeKey = nv === 3 ? 'duelo_pierde3' : (nv === 2 ? 'duelo_pierde2' : 'duelo_pierde');
    if (w) {
      this.setState('defeated', 5);
    } else {
      this.setState('victory', 5);
      this._playLaugh(0.8);
    }
    g.rules.message = w ? tx(ganaKey) : tx(pierdeKey);
    // v2.94 · ETAPA SUPERADA: el duelo ganado destapa la SIGUIENTE etapa
    // (duelo 1 → etapa 2, duelo 2 → etapa 4, FINAL → ¡CAMPEÓN!) y VOLVEMOS
    // A LA SALA (el duelo se cierra; la revancha sólo tiene sentido al
    // perder). Al PERDER, _duelOn sigue vivo: el gatillo del núcleo en
    // «over» relanza la revancha como siempre.
    if (w) {
      this._duelOn = false;
      this._rivalOn = false;
      this._duelPose = false;
      if (this.powerSign) this.powerSign.hide();
      g.rules.state = STATE_NAME;      // el árbitro vuelve a dormir
      g.ball.ignoreNet = true;
      g.freezeT = 0;
      for (const m of (this._netParts || [])) m.visible = false;
      g.scoreboardGroup.visible = false;
      g.aiPaddleMesh.visible = false;
      this._parkMainBall();
      this.cartel.visible = true;
      this.mapa.visible = true;
      if (this.sprite) {
        this.sprite.position.set(OESTE.x, this.spriteBaseY, OESTE.z);
        this.sprite.rotation.z = 0;
        this._hitShakeT = 0; this._fadeT = 0;
      }
      if (this.arbustoGroup) {
        this.arbustoGroup.position.set(ARBUSTO.x, 0, ARBUSTO.z);
        this.arbustoGroup.rotation.y = Math.atan2(-ARBUSTO.x, 0.55 - ARBUSTO.z);
      }
      if (this.arbustoSombra) this.arbustoSombra.position.set(ARBUSTO.x, 0.004, ARBUSTO.z);
      this.setState('idle', 0);
      this._armT = 1.2;
      this._stageClear(this._duelStage || 1);
      this.musicOn();
    }
    this.paintCartel();   // el cartel de sala queda al día (ganados + etapa)
  }
  /** v2.93 · SANGRE EN LA CÁMARA: el forajido GANÓ el duelo (ninguna diana
   *  acertada) y su disparo salpica al jugador — gotas que escurren por el
   *  visor con su reguero (~10 s). Efecto puro del visor: no toca el juego. */
  _sangreTrigger() {
    try {
      if (!this._sangre) this._sangre = new SangreCara(this);
      this._sangre.trigger();
    } catch (e) { /* nunca tumba el frame */ }
  }
  /** v2.95 · MANCHONES FIJOS del asedio (persist=true: toda la etapa). */
  _manchasTrigger(n, persist) {
    try {
      if (!this._manchas) this._manchas = new SangreManchon(this);
      this._manchas.trigger(n, persist);
    } catch (e) { /* nunca tumba el frame */ }
  }

  /** Volver al núcleo (menú/otro modo): TODO queda como estaba. */
  leave() {
    const g = this.game;
    this.active = false;
    // v2.96: REJUGADA en curso — el progreso real vuelve (el storage manda)
    if (this._replayReal != null) {
      this.stage = this._replayReal;
      this._replayReal = null;
      this._leyendaOn = false;             // ronda 25 (auditoría): sin flag huérfano
      try { localStorage.setItem(this.storageKey('stage'), String(this.stage)); } catch (e0) { /* */ }
    }
    this.musicOff();
    // v2.93: la sangre del visor se retira AL INSTANTE al salir de la sala
    if (this._sangre) this._sangre.stop();
    if (this._manchas) this._manchas.stop();     // v2.94: manchones del asedio
    // v2.94: si había PRUEBA activa (asedio/tren), cerrarla y restaurar
    if (this._stageMode) {
      if (this._asedio) { this._asedio.dispose(); this._asedio = null; }
      if (this._tren) { this._tren.dispose(); this._tren = null; }
      this._stageMode = null;
      this._freeGunApply(false);
      if (g.roomGroup) g.roomGroup.visible = true;
      g.champDecorHidden = false;        // v2.95: troqueles de vuelta
      if (g.champDecor && g.champDecor.group) g.champDecor.group.visible = true;
    }
    // v2.86: si había DUELO, cerrarlo — el árbitro se reinicia SIEMPRE
    if (this._duelOn) {
      this._duelOn = false;
      this._rivalOn = false;
      this._duelPose = false;
      this._endPower();
      this._gunVisible(false);
      this._freeGunApply(false);
      g.freezeT = 0;
      if (this.powerSign) this.powerSign.hide();
      if (g.rules.state !== STATE_NAME) {
        g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
      }
    }
    if (!this.inited) return;
    this._tableWoodOff();    // v2.87: mesa reglamentaria azul de vuelta
    if (this.group) this.group.visible = false;
    if (this.sprite) this.sprite.visible = false;
    if (this.mapa) this.mapa.visible = false;
    if (this.cartel) this.cartel.visible = false;
    if (this._insignia) this._insignia.grp.visible = false;
    if (this.arbustoGroup) this.arbustoGroup.visible = false;   // v2.83
    if (this.arbustoSombra) this.arbustoSombra.visible = false;
    if (this._netParts) for (const mm of this._netParts) mm.visible = true;
    g.scoreboardGroup.visible = true;
    g.aiPaddleMesh.visible = true;
    g.ballMesh.visible = true;
    g.ball.ignoreNet = false;
    if (this._ballSaved && g.ballMesh && g.ballMesh.material) {
      g.ballMesh.material.color.setHex(this._ballSaved.col);
      if (g.ballMesh.material.emissive && this._ballSaved.em !== null) {
        g.ballMesh.material.emissive.setHex(this._ballSaved.em);
      }
      g.ballMesh.material.emissiveIntensity = this._ballSaved.ei;
      this._ballSaved = null;
    }
    if (g.rules.state === STATE_NAME) {
      g.rules.startMatch(g.mode === 'survival' ? 'survival' : 'match');
    }
    if (g.rules.oppLabel === 'forajido') g.rules.oppLabel = 'cpu';
  }

  /** Reentrada desde el menú de pausa (patrón reenter del mago). */
  reenter() {
    if (!this.active) return;
    const g = this.game;
    // v2.94: PRUEBA activa — nada que re-anclar (su step sigue por testStep)
    if (this._stageMode) { this.musicOn(); return; }
    // v2.86: el duelo vive en estados del núcleo — nada que re-anclar
    if (this._duelOn) { this.musicOn(); return; }
    g.rules.state = STATE_NAME;
    g.tableGroup.visible = true;
    g.scoreboardGroup.visible = false;
    g.aiPaddleMesh.visible = false;
    for (const m of this._netParts || []) m.visible = false;
    this._parkMainBall();
    if (this.group) {
      this.group.visible = true;
      this.sprite.visible = true;
      this.mapa.visible = true;
      this.cartel.visible = true;
      if (this._champion && this._insignia) this._insignia.grp.visible = true;
      if (this.arbustoGroup) this.arbustoGroup.visible = true;  // v2.83
      if (this.arbustoSombra) this.arbustoSombra.visible = true;
    }
    this.musicOn();
  }

  /** Frame a frame: balanceo de espera + bola aparcada (el núcleo RE-SIRVE
   *  la bola cada frame en 'champtest': magia la re-aparca en su step(),
   *  patrón idéntico) + sincronía de volumen. */
  update(dt) {
    if (!this.active || !this.inited) return;
    this._t += dt;
    // v2.93 · REGUERO DE SANGRE en la cámara (el forajido ganó el duelo):
    // corre SIEMPRE que la sala viva — durante el duelo y en el rallye
    // siguiente (la salpicadura dura ~10 s y entorpece la partida).
    if (this._sangre) this._sangre.update(dt);
    if (this._manchas) this._manchas.update(dt);   // v2.94: manchones fijos
    this._puntosStep(dt);   // v2.119: los «+N» flotan en TODAS las fases
    // v2.94 · PRUEBA activa (asedio/tren): su física corre por testStep —
    // aquí van SOLO los visuales por frame (FX, láser, HUD, música)
    if (this._stageMode === 'asedio' && this._asedio) {
      this._asedio.fxStep(dt);
      this._syncMusicGain();
      return;
    }
    if (this._stageMode === 'tren' && this._tren) {
      this._tren.fxStep(dt);
      this._syncMusicGain();
      return;
    }
    // v2.86: en DUELO la sala duerme — manda _updateDuel
    if (this._duelOn) { this._updateDuel(dt); return; }
    if (this._armT > 0) this._armT -= dt;   // asentamiento anti-gesto accidental
    this._parkMainBall();   // contra el re-servido del núcleo (patrón mago)
    // pose transitoria → idle (la sala respira)
    if (this._transient > 0) {
      this._transient -= dt;
      if (this._transient <= 0) this.setState('idle');
    }
    // balanceo suave de espera (patrón vaivén, amplitud discreta)
    if (this.sprite) {
      this.sprite.position.y = this.spriteBaseY + Math.sin(this._t * 1.1) * 0.012;
    }
    // v2.94: el anillo de la INSIGNIA del campeón late suave
    if (this._insignia && this._insignia.grp.visible) {
      this._insignia.ring.material.opacity = 0.45 + Math.sin(this._t * 2.4) * 0.18;
    }
    // ARBUSTO RODANTE (v2.83): péndulo del centro a un extremo (50 cm) y
    // vuelta al contrario (100 cm), rodando sin deslizar (rotación
    // proporcional al desplazamiento) y siempre rozando el suelo.
    if (this.arbustoGroup && this.arbustoMesh) {
      const ab = ARBUSTO;
      const dx = ab.amplitud * Math.sin(this._t * ((Math.PI * 2) / ab.periodo));
      this.arbustoGroup.position.x = ab.x + dx;
      this.arbustoMesh.rotation.z = -dx / (ab.h / 2);
      if (this.arbustoSombra) this.arbustoSombra.position.x = ab.x + dx;
    }
    this._syncMusicGain();   // v2.78: la BSO sigue el ajuste global en vivo
  }

  /* ================== v2.96 · REJUGAR ETAPAS SUPERADAS ====================
   *  El núcleo lanza el rayo de la PALA contra el mapa de la sala
   *  (replayMap) y avisa del nodo apuntado (replayHover): el ANILLO salta
   *  a ese nodo y el cartel muestra «REJUGAR ETAPA N». El gatillo sobre
   *  un nodo SUPERADO relanza esa etapa (replayLaunch) guardando el
   *  progreso real: al terminar la rejugada el camino sigue donde estaba.
   *  ====================================================================== */
  replayMap() {
    if (!this.active || !this.inited) return null;
    if (this._stageMode || this._duelOn) return null;   // en prueba/duelo no
    if (!this.mapa || !this.mapa.visible) return null;
    return {
      plane: this.mapa,
      nodesPx: NODOS,
      imgW: 1699, imgH: 926,
      // v2.108: MODO DEPURACIÓN — las 5 etapas seleccionables sin requisitos
      maxIdx: ppDbg() ? 4 : clamp(this.stage, 1, 5) - 1,
    };
  }
  replayHover(idx) {
    const i = idx | 0;
    if (i === (this._hoverNodo | 0)) return;
    this._hoverNodo = i;
    const g = this.game;
    if (i >= 0) {
      const n0 = NODOS[i];
      const PHm2 = MAPA.PW * 926 / 1699;
      if (this.mapaMarker && n0) {
        this.mapaMarker.position.set(
          (n0.x / 1699 - 0.5) * MAPA.PW, (0.5 - n0.y / 926) * PHm2, 0.006);
        this.mapaMarker.scale.setScalar((n0.r / 120) * 1.22);
      }
      if (g.renderer.xr.isPresenting) g.haptic(g.paddleHand, 0.25, 60);
    } else {
      this._refreshMap();      // el anillo vuelve a la etapa vigente
    }
    this.paintCartel();        // la cinta muestra REJUGAR ETAPA N
  }
  replayLaunch(idx) {
    const g = this.game;
    const n = (idx | 0) + 1;
    const st = clamp(this.stage, 1, 5);
    if (this._stageMode || this._duelOn) return;
    // v3.6.18 (ronda 24): siendo CAMPEÓN, hasta el nodo VIGENTE es una
    // rejugada LEYENDA (el camino normal ya no existe: estás coronado).
    if (n === st && !this._champion) return this.serveTrigger();  // nodo VIGENTE: camino normal
    if (this._armT > 0) return;                   // anti-gesto accidental
    this._replayReal = st;                        // el progreso real se conserva
    this._leyendaOn = !!this._champion;           // v3.6.18 (ronda 24): sólo campeón rejuga en LEYENDA
    this.stage = n;
    this._refreshMap();
    this.paintCartel();
    g.rules.message = tx(this._leyendaOn ? 'leyenda_up' : 'replay_up').replace('{n}', String(n));
    g.audio.announce(g.rules.message, true);
    if (n === 2) return this._startAsedio();
    if (n === 4) return this._startTren();
    return this._startDuel(n >= 5 ? 3 : (n === 3 ? 2 : 1));
  }
  /** v2.96 · BORRADO DE REGISTROS en VIVO: la sala (si estaba abierta)
   *  vuelve a la ETAPA 1 al momento — borrar registros ya no puede dejar
   *  el camino a medias (lección de la Quest: el storage se vaciaba pero
   *  la sala seguía en la etapa 3). leave() + estado a cero + startChamp(). */
  _resetLive() {
    const g = this.game;
    const estaba = !!this.active;
    try { this.leave(); } catch (e) { /* sigue */ }
    this.stage = 1; this._champion = false; this._heridas = 0;
    this._leyendaOn = false;               // ronda 25 (auditoría): el borrado corta también la LEYENDA
    this.duelWins = 0; this.rank = []; this.round = 1;
    this.streakP = 0; this.streakAi = 0;
    this._replayReal = null; this._hoverNodo = -1;
    try {                                     // segunda pasada: sin restos
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf('pp_champ_oeste_') === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e3) { /* */ }
    if (estaba) this.startChamp();            // la sala vuelve en la ETAPA 1
  }

  /* ================== v2.94 · MAPA DE ETAPAS AL DÍA =======================
   *  Levanta las TAPAS de los nodos ya superados y coloca el ANILLO dorado
   *  en el nodo de la etapa vigente (pulsación en el update de sala). */
  _refreshMap() {
    try {
      for (const t of this.tapas) {
        const nd = (t.userData && t.userData.nodo) | 0;
        // v2.108: en MODO DEPURACIÓN todas las tapas levantadas — las 5
        // etapas son visibles y apuntables con la pala desde el principio.
        t.visible = ppDbg() ? false : (nd >= this.stage);   // tapa sólo en nodos PENDIENTES
      }
      const n0 = NODOS[clamp(this.stage, 1, 5) - 1];
      if (n0 && this.mapaMarker) {
        const PHm2 = MAPA.PW * 926 / 1699;
        this.mapaMarker.position.set(
          (n0.x / 1699 - 0.5) * MAPA.PW, (0.5 - n0.y / 926) * PHm2, 0.006);
        this.mapaMarker.scale.setScalar(n0.r / 120);
      }
    } catch (e) { /* sin mapa: la sala sigue */ }
  }
}

/* ============================================================================
 *  MÓDULO (contrato ChampLoader — igual que locura y magia)
 *  ============================================================================ */
export default {
  id: 'oeste',
  /** v2.128: ¿campeonato superado? (cinta ★ SUPERADO del menú) */
  isChampion() { return !!(CTRL && CTRL._champion); },
  /** v2.130 · INTRO de campeonato: silencia la BSO privada mientras suena
   *  el vídeo de la historia del rival (hook opcional del núcleo). */
  champIntroPause(on) {
    if (!CTRL) return;
    try { on ? CTRL.musicOff() : CTRL.musicOn(); } catch (e) { /* */ }
  },
  /* v2.83 · TROQUELES de cartón del Oeste (PNG recortados a su alfa en
   * assets/decor/): el núcleo (createChampDecor, v2.80/81) los monta al
   * activarse este campeonato y los destruye al salir — igual que en
   * locura y magia, cada campeonato monta SOLO los suyos. Posiciones
   * escogidas para no tapar el cartel/RANKING (1,46/-1,7), el forajido
   * (1,62/-4,5), el corredor del arbusto (x 1,1-2,1 en z -3,7), el mapa
   * (pared izquierda) ni los huecos reservados del orbe (0/-4,2) y el
   * portal (0/-5,4). */
  decor: {
    pieces: [
      { file: 'assets/decor/saloon.png',   h: 1.15, x: -2.30, z: -2.75, sway: 0.5 },
      { file: 'assets/decor/cactus.png',   h: 1.35, x:  2.45, z: -2.35, sway: 0.7 },
      { file: 'assets/decor/carruaje.png', h: 0.90, x: -2.35, z: -1.15, sway: 0.6 },
      { file: 'assets/decor/sebusca.png',  h: 1.10, x:  2.00, z: -0.80, sway: 0.8 },
    ],
  },

  /* v2.85 · DECORADO DE SALA («room») — EL SALOON. El núcleo
   * (createChampRoom) viste los 6 PLANOS de la sala con el arte de
   * assets/room/ SOLO mientras este campeonato está activo: tablones de
   * madera, barra con espejo y botellas en la trasera, puerta y
   * ventanas al desierto en la frontal, lámparas de aceite en el techo
   * y alfombra roja en el suelo. Al salir, la sala vuelve a su tema
   * clásico (dispose GPU). Sin variants todavía: llegarán con los
   * duelos del forajido (misma mecánica que locura/magia: el _setStage
   * llamará game.champRoom.useVariant). Medidas reales: suelo/techo
   * 6,10 × 7,90 m · frontal/trasera 6,10 × 2,85 m · laterales 7,90 × 2,85 m. */
  room: {
    floor: 'assets/room/suelo.jpg',
    ceil:  'assets/room/techo.jpg',
    back:  'assets/room/fondo.jpg',      // trasera: la BARRA del saloon
    front: 'assets/room/frente.jpg',     // pared del forajido: la puerta
    left:  'assets/room/izquierda.jpg',  // estufa + guitarra
    right: 'assets/room/derecha.jpg',    // piano + sombreros
  },

  get controller() { return CTRL; },

  /** ctx = { game, id, stateName } — lo entrega ChampLoader. */
  init(ctx) {
    if (!window.__PP_CORE) {
      throw new Error('oeste: window.__PP_CORE no disponible (¿se cargó fuera del juego?)');
    }
    GAME = ctx.game;
    STATE_NAME = ctx.stateName || STATE_NAME;
    TL = (window.__PP_CORE.lang && window.__PP_CORE.lang() === 'en') ? 'en' : 'es';
    const A = (p) => new URL('./assets/' + p, import.meta.url).href;
    const stateUrls = {};
    for (const st of STATES) stateUrls[st] = A(st + '.webp');
    const manifest = {
      stateUrls,
      mapUrl: A('mapa.webp'),
      tapaUrl: A('tapa.webp'),
      musicUrl: A('bso.mp3'),
      laughUrl: A('risas.mp3'),
      risasPuebloUrl: A('risas_pueblo.mp3'),   // v2.106: risa de la DERROTA
      waveUrl: A('decor/asedio/oleada.mp3'),   // v2.99: música de los CARTELES
      // v2.90: pistol.glb RETIRADO (no se usa en este campeonato)
      revolverUrl: A('revolver.glb'),
      tntUrl: A('small_tnt.glb'),
      // v2.111 · EL BOTÍN DEL TREN
      lingoteUrl: A('lowpoly_gold_bar.glb'),
      vagonMusicUrl: A('vagon.mp3'),
      ligotesUrl: A('ligotes.png'),
      contadorUrl: A('contador.png'),   // v2.116: MARCADOR del asedio
      portalUrl: A('portals.webp'),
      // v2.140 · RESULTADO DE LA ESTACIÓN (megafonía + paneles + risas)
      recompensaUrl: A('recompensa.png'),
      roboUrl: A('forajido_robo.png'),
      risasForajidoUrl: A('risas_forajido.mp3'),
    };
    CTRL = new ForajidoStand(GAME, manifest);
    CTRL.stateName = STATE_NAME;
    CTRL.id = ctx.id;
    // v2.86: puente de PRUEBAS headless (el CTRL vive en clausura)
    try { window.__PP_OESTE = { ctrl: () => CTRL }; } catch (e) { /* */ }
    // idioma en caliente (v2.120: handler con nombre + reenganche seguro —
    // antes cada init() apilaba un listener anónimo nuevo)
    if (_ppLangFnO) {
      document.removeEventListener('pp-lang', _ppLangFnO);
    }
    _ppLangFnO = () => {
      try { if (CTRL) CTRL.refresh(); } catch (e) { /* */ }
    };
    document.addEventListener('pp-lang', _ppLangFnO);
    return Promise.resolve();   // sin data.json: lista al instante
  },

  start() { if (CTRL) CTRL.startChamp(); },
  leave() { if (CTRL) CTRL.leave(); },
  refresh() { if (CTRL) CTRL.refresh(); },
  update(dt) { if (CTRL) CTRL.update(dt); },
  reenter() { if (CTRL) CTRL.reenter(); },
  /* v2.86 · DUELO: ganchos del árbitro + pistola + gatillo (contrato v2.70) */
  onPoint(it) { if (CTRL) CTRL.onPoint(it); },
  onMatchOver(w) { if (CTRL) CTRL.onMatchOver(w); },
  aiMul() {
    const g = GAME;
    if (!CTRL || !CTRL.active || !CTRL._duelOn || !g ||
        g.rules.oppLabel !== 'forajido') return 1;
    // v2.94: IA por nivel de duelo (1,0 / 1,2 / 1,4 — DUELO_NV)
    return CTRL._nvCfg().aiMul;
  },
  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },   // v2.98: con mano
  get gunArmed() { return !!(CTRL && CTRL.active && CTRL._duelOn); },
  fireGun(i) { if (CTRL) CTRL.fireGun(i); },
  /* v2.89 · EL DUELO: el gatillo de la mano de la PALA dispara mientras el
   *  duelo del Disparo certero esté vivo (la pala ES un revólver). */
  get paddleGunArmed() { return !!(CTRL && CTRL._paddleGunFlag); },

  /* v2.94 · PRUEBAS (etapas 2 y 4): el núcleo delega la FÍSICA del frame
   *  mientras testActive() responda true (patrón orbe de Magia — el árbitro
   *  duerme en 'champtest' y la pala del mando activo sigue viva). */
  testStep(dt) {
    if (!CTRL) return;
    if (CTRL._stageMode === 'asedio' && CTRL._asedio) CTRL._asedio.step(dt);
    else if (CTRL._stageMode === 'tren' && CTRL._tren) CTRL._tren.step(dt);
  },

  /* v2.96 · REJUGAR etapas superadas (mapa + gatillo, vía núcleo) */
  replayMap() { return CTRL ? CTRL.replayMap() : null; },
  replayHover(idx) { if (CTRL) CTRL.replayHover(idx); },
  replayLaunch(idx) { if (CTRL) CTRL.replayLaunch(idx); },
  testActive() {
    return !!(CTRL && CTRL.active && (CTRL._asedio || CTRL._tren));
  },

  /* v2.115 · banco visual / depuración (foro3d): instancia viva del tren. */
  get trenDebug() { return (CTRL && CTRL._tren) || null; },

  /** v2.96 · BORRAR REGISTROS = EMPEZAR DE CERO SIEMPRE: se borra el
   *  storage Y el estado VIVO (la sala reabre en la etapa 1 al momento). */
  resetRecords() {
    try {
      const dead = [];
      for (let i = 0; i < localStorage.length; i++) {
        const k = localStorage.key(i);
        if (k && String(k).indexOf('pp_champ_oeste_') === 0) dead.push(k);
      }
      for (const k of dead) { try { localStorage.removeItem(k); } catch (e2) { /* */ } }
    } catch (e) { /* */ }
    if (CTRL) {
      try { CTRL._resetLive(); } catch (e3) { console.warn('[oeste.resetRecords]', e3); }
    }
  },
};

/* v2.111: export de pruebas headless (sin efecto en el juego).
 * v2.116: también ASEDIO (config) y las 2 acciones de etapa para el banco. */
export { TrenAction, TREN, ASEDIO, AsedioAction, ForajidoStand,
         TormentaAction, EstampidaAction, TORMENTA, ESTAMPIDA };
