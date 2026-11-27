// gen_menu_r114_cont1.js — contenido: resumen, flujo, Portada (A), Hall (B), Arcano (C)
const fs = require('fs');
const { P, h1, h2, h3, p, nota, vineta, tabla, figura, pesoCubemap, durSala } = require('./gen_menu_r114_lib.js');

const ACT = JSON.parse(fs.readFileSync('/home/z/my-project/scripts/_menu_activos.json', 'utf8'));

const C = [];

// ══ 1 · RESUMEN EJECUTIVO ══
C.push(h1('1 · Resumen ejecutivo'));
C.push(p('Este documento inventaria todas las piezas de arte y recursos que componen el menú de Crazy Ping Pong (CrazyPP), de la portada 2D hasta el espacio Arcano, con sus características técnicas medidas en disco y los requisitos que el código fuente impone a cada una. El objetivo es servir de documento de trabajo para el rediseño artístico: cada pieza tiene su ficha, y el catálogo maestro de la sección 10 ordena el trabajo pieza a pieza con la especificación recomendada de cada recurso. Todo el contenido procede del análisis del código fuente en src/game/ y de la medición directa de los ficheros en public/assets/, sin estimaciones.'));
C.push(p([{ t: 'El hallazgo estructural principal es que el arte del menú sigue un ' }, { t: 'patrón doble', b: true }, { t: '. Por un lado hay ficheros externos con un contrato estricto de nombres y proporciones (los cubemaps de seis caras del hall y sus músicas, el búho del Arcano, los modelos GLB de las palas, el vídeo de intro). Por otro lado, una gran parte del menú es arte procedural dibujado en canvas en tiempo de ejecución (las placas de museo, la pared de insignias, el panel del Arcano, la bóveda estelar), que no se rediseña sustituyendo ficheros sino reescribiendo funciones de dibujo. Entre ambos hay un tercer grupo: piezas incrustadas en base64 dentro del propio código (el hero de la portada, los botones de juego, el logo del menú, los iconos de los superpoderes).'}]));;
C.push(p('Las cifras verificadas del inventario: 54 activos externos en public/assets/ (36 JPG de cubemaps, 6 MP3 de música, 2 GLB, 1 MP4, 9 PNG), 57 piezas únicas incrustadas en base64 en el código y alrededor de quince familias de arte procedural. El análisis también corrige varias premisas habituales sobre el menú, importantes antes de encargar arte nuevo: el candado.png no es el candado de las salas bloqueadas (ese es un glifo vectorial del menú 2D) sino el candado de los superpoderes del Arcano; palas.png no se muestra nunca en pantalla, vive como contorno trazado en 34 polilíneas; arcano.mp3 no es la música del hall sino la del espacio Arcano; y el museo clásico es la única variante sin música propia.'));

// ══ 2 · FLUJO Y CÓMO LEER EL DOCUMENTO ══
C.push(h1('2 · Flujo del menú y cómo leer las fichas'));
C.push(p('El menú no es una pantalla única sino una cadena de superficies. El jugador arranca en la portada 2D (que es a la vez pantalla de carga, intro y título), y desde ahí entra en VR al hall 3D, una estancia de museo vestida con seis variantes temáticas desbloqueables. Dentro del hall, apuntar al búho abre el espacio Arcano (la galería de superpoderes), y el menú 2D de sala dibujado en canvas permite escoger variante, palas, bolas y mesas. La tabla siguiente resume esa cadena y los recursos que cada fase consume.'));
C.push(tabla(
  ['Fase', 'Superficie', 'Tecnología', 'Recursos principales'],
  [
    ['Arranque', 'Portada 2D (#overlay)', 'DOM + CSS', 'Hero JPEG, botones PNG, música OGG, intro.mp4'],
    ['Menú principal (VR)', 'Hall 3D (museo)', 'Escena three.js', 'Cubemap 6 caras, arcano.png, placas canvas'],
    ['Galería', 'Espacio Arcano', 'Escena three.js', 'arcano.png, candado.png, palas.png (trazo), arcano.mp3'],
    ['Configuración', 'Menú 2D de sala', 'Canvas 2D', 'Logo JPEG, iconos vectoriales'],
    ['Selección de sala', 'Grid Arte del hall', 'Canvas 2D', 'Sin arte propio (nombres y candados vectoriales)'],
    ['Partida', 'Cancha (contexto)', 'Escena three.js', 'assets/partido/ (5 JPG), sala procedural'],
  ],
  [14, 26, 18, 42]));
C.push(p('Cada ficha de este documento contiene cinco campos: qué es la pieza y su función en el menú; dónde vive (fichero externo con su ruta exacta, o fichero y línea del código fuente si está incrustada); sus características medidas (formato, dimensiones, peso, duración); el requisito que el código impone (proporciones, transparencia, posiciones de referencia); y la especificación recomendada para el rediseño. Las miniaturas incluidas son vistas reducidas de las piezas actuales para identificarlas de un vistazo.'));

// ══ 3 · APARTADO A · PORTADA 2D ══
C.push(h1('3 · Apartado A · Portada 2D (overlay de arranque)'));
C.push(p('La portada es un overlay DOM (#overlay) con fondo degradado azul noche que cubre el canvas 3D mientras este carga; no hay pantallas separadas de carga ni de título. Detrás del arte, varias capas decorativas son CSS puro sin ficheros: dos haces de luz de pabellón, tres bolas de ping-pong flotantes y seis estrellas doradas que titilan, todas regenerables con código. La música de portada arranca al primer toque de pantalla y se pausa al entrar en VR o al ver la INTRO (con ducking y reanudación automática).'));
C.push(tabla(
  ['Elemento', 'Identificador', 'Recurso', 'Presentación'],
  [
    ['Arte hero (título)', 'img de .hero-wrap', 'JPEG base64 (misma pieza que el fondo)', 'Máx. 680 px de ancho, esquinas 26 px, borde dorado'],
    ['Fondo difuminado', '.bgblur', 'El mismo JPEG base64', 'Cover, blur 16 px, brillo 0,42, Ken Burns 30 s'],
    ['Botón JUGAR EN VR', '#playEs / #playEn', '2 PNG base64 (ES/EN)', 'Máx. 360 px; texto horneado en la imagen; pulso + vaivén'],
    ['Selector de idioma', '#padEs / #padEn', '2 PNG base64', '84×84 px (fuentes 160×160), etiqueta de texto fuera del arte'],
    ['Línea de estado', '#status', 'Texto (sin arte)', '13,5 px, gris #8d9aa8, mensajes de compatibilidad WebXR'],
    ['Pie de portada', '.footer (7 botones)', 'Texto + enlaces', 'Ranking mundial, passthrough, INTRO, instalar PWA, Ko-fi, TV'],
    ['Silenciador', '#mutebtn', 'Texto (emoji)', '46×46 px, abajo a la derecha; alterna música portada y menú VR'],
    ['Visor de INTRO', '#introov / video#introvid', 'assets/intro.mp4', 'Máx. 96vw×90vh con sonido; sin póster declarado'],
    ['Ranking mundial', '#wrlov', 'Panel DOM', 'Panel 560 px con borde dorado; insignia de logro 30×30 px'],
  ],
  [20, 18, 26, 36], { size: 18 }));

C.push(h2('A.1 · Arte hero y fondo de portada (una pieza, dos roles)'));
C.push(...figura('hero', 340, 'Figura 1 · Arte hero actual: JPEG 1280×720 incrustado en base64 (161 KB). La misma pieza difuminada y oscurecida sirve de fondo de portada.'));
C.push(p([{ t: 'El arte oficial del título es un ' }, { t: 'JPEG de 1280×720 y 161 KB incrustado en base64', b: true }, { t: ' que aparece dos veces en el código y cumple dos roles con una sola pieza: como imagen hero flotante (máximo 680 px de ancho, esquinas redondeadas de 26 px, borde dorado y animación de levitación) y como fondo a pantalla completa difuminado (blur de 16 px, brillo al 42 % y saturación 1,25, con movimiento Ken Burns de 30 segundos). El título del juego vive horneado dentro de esta imagen; no existe un logotipo en texto. Para el rediseño conviene producir una única pieza nueva de al menos 1600×900 en JPEG (sin canal alfa), cuidando que la zona central-superior aguante el recorte de esquinas redondeadas, y regenerar las dos copias base64 (00_head.html línea 29 y 03_body.html línea 17).'}]));;
C.push(h2('A.2 · Botón JUGAR EN VR y selector de idioma'));
C.push(p('El gran botón de juego son dos PNG de 512×128 (91,0 KB la versión española y 89,1 KB la inglesa) con el texto horneado en el arte, mostrados a un máximo de 360 px de ancho con animación de pulso, vaivén y escalado al pasar el puntero. Las palas-bandera del selector de idioma son dos PNG de 160×160 (12,2 y 18,9 KB) mostrados a 84×84 px; la etiqueta ESPAÑOL / ENGLISH es texto del DOM, no arte, así que puede cambiarse sin tocar imagen. Para el rediseño: PNG con transparencia, idealmente a doble resolución (1024×256 los botones, 320×320 las banderas), en las dos variantes de idioma, dejando margen perimetral para que la animación de pulso no roce el borde.'));
C.push(h2('A.3 · Música de portada'));
C.push(p([{ t: 'La pista de portada es un ' }, { t: 'OGG Vorbis instrumental de 89,7 segundos y 929 KB incrustado en base64', b: true }, { t: ' (asignado a window.__PP_MUSIC_URL en 07_tail.html, línea 19), con metadatos de origen «Cover» instrumental. Se reproduce en bucle a volumen 0,5 en la portada 2D, y dentro del juego a 0,26 × musicVol bajo el invariante UNA MELODÍA (la pista del salón la retira y no deja que renace mientras el salón esté abierto). Un rediseño sonoro debe entregar un instrumental de bucle limpio (entradas y salidas con fundido, sin golpe seco de cierre) y regenerar el literal base64 del fichero.' }]));
C.push(h2('A.4 · Vídeo de intro y visor'));
C.push(p('El vídeo de intro es un fichero externo, assets/intro.mp4, H.264 de 1920×1080, 10,0 segundos y 5,5 MB. El visor 2D (#introov) lo reproduce con sonido a un máximo del 96 % del ancho y 90 % de alto de la ventana, pausa la música de portada mientras dura y lo cierra con el botón, la tecla Escape, el fin del vídeo o al pulsar JUGAR. Ojo: este visor no declara atributo poster, así que si el fichero falta solo queda el aviso de error; añadir un póster de fallback sería una mejora trivial del HTML. El vídeo es opcional y manual, nunca bloquea el arranque.'));
C.push(h2('A.5 · Ranking mundial, toast PWA e insignias'));
C.push(p('El panel de Ranking Mundial es DOM puro con estilo propio (fondo degradado #10141d a #0a0d14, borde dorado, ancho mínimo de 560 px) y consume una insignia cuadrada por campeonato mostrada a 30×30 px. El toast PWA y los botones de instalación no requieren arte nuevo, pero la PWA sí declara tres iconos que son piezas de marca: logo-192.png, logo-512.png y logo-maskable-512.png, con la versión maskable needing zona de seguridad para la máscara del sistema. Estos iconos hoy no están en el alcance del rediseño del menú, pero conviene actualizarlos si cambia la identidad visual.'));

// ══ 4 · APARTADO B · HALL 3D ══
C.push(h1('4 · Apartado B · Hall 3D: la caja y sus seis variantes'));
C.push(p('El hall es una estancia de 6,10 × 7,90 × 2,85 metros construida con seis planos vestidos por el mismo cubemap, con texturas en espacio sRGB y anisotropía 4, y carga perezosa a prueba de fallos: si un JPG no llega, el plano conserva su color de respaldo. El arte de las caras pinta TODO el mobiliario del museo (zócalos, sofás, plantas, gloria, vitrinas), porque los pintores de pared 3D fueron retirados del código; el centro de la estancia debe quedar libre y el suelo trae el emblema elíptico de la casa y el techo el círculo luminoso. Las seis variantes del hall son la misma caja con distinta carpeta de assets y distinta música: cambiar de salón es vestir en vivo otra carpeta (applyHallVariant) y reconstruir su mobiliario 3D.'));
C.push(tabla(
  ['Cara', 'Fichero', 'Resolución actual', 'Plano físico', 'Contenido esperado'],
  [
    ['Frente (pared de insignias)', 'frente.jpg', '1849×864', '6,10×2,85 m', 'Gloria, vitrinas, zócalos'],
    ['Fondo (la puerta)', 'fondo.jpg', '1849×864', '6,10×2,85 m', 'Puerta al museo'],
    ['Izquierda (ventanal)', 'izquierda.jpg', '2395×864', '7,90×2,85 m', 'Ventanal del pabellón'],
    ['Derecha', 'derecha.jpg', '2395×864', '7,90×2,85 m', 'Simétrica a la izquierda'],
    ['Suelo', 'suelo.jpg', '1296×1678', '6,10×7,90 m', 'Emblema elíptico central'],
    ['Techo', 'techo.jpg', '1296×1678', '6,10×7,90 m', 'Círculo luminoso'],
  ],
  [22, 14, 16, 16, 32]));
C.push(p('Estas proporciones son un contrato: el código mapea cada JPG 1:1 sobre su plano sin distorsión, y las seis variantes usan exactamente las mismas dimensiones. Un rediseño puede cambiar el estilo artístico, pero debe respetar resolución por cara, nombres de fichero y composición (centro libre, emblema abajo, círculo arriba).'));

C.push(h2('B.1 · Las seis variantes del hall'));
C.push(tabla(
  ['Variante', 'Nombre visible', 'Desbloqueo', 'Carpeta', 'Música', 'Peso cubemap'],
  [
    ['Museo', 'MUSEO', 'Libre', 'assets/hall/', 'Sin música', pesoCubemap('')],
    ['Cabaña', 'LA CABAÑA', '10 victorias', 'assets/hall/cabana/', durSala('/cabana'), pesoCubemap('/cabana')],
    ['Neón', 'SALÓN NEÓN ARCADE', 'Rally de 20 o más', 'assets/hall/neon/', durSala('/neon'), pesoCubemap('/neon')],
    ['Observatorio', 'OBSERVATORIO ESTELAR', 'ELO 1100 o más', 'assets/hall/observatorio/', durSala('/observatorio'), pesoCubemap('/observatorio')],
    ['Dojo', 'DOJO ZEN', '5 saques directos', 'assets/hall/dojo/', durSala('/dojo'), pesoCubemap('/dojo')],
    ['Rascacielos', 'RASCACIELOS', '25 victorias', 'assets/hall/rascacielos/', durSala('/rascacielos'), pesoCubemap('/rascacielos')],
  ],
  [12, 20, 15, 22, 15, 16], { size: 18 }));
C.push(p('Todas las pistas de salón son MP3 a 192 kbps, 44,1 kHz y estéreo, con duraciones entre 158,7 y 177,3 segundos. En línea, el invitado ve el salón del anfitrión (la variante viaja por red con el evento hallv); el candado solo gobierna elegirla, no verla. Cada carpeta de variante contiene exactamente siete ficheros: las seis caras JPG más su MP3.'));

C.push(h2('B.2 · El cubemap del museo al detalle'));
C.push(...figura('museo_frente', 320, 'Figura 2 · Cara frontal del museo (1849×864): pared de insignias con gloria y vitrinas pintadas en el arte.'));
C.push(...figura('museo_suelo', 170, 'Figura 3 · Cara del suelo (1296×1678): emblema elíptico central de la casa.'));
C.push(...figura('museo_techo', 170, 'Figura 4 · Cara del techo (1296×1678): círculo luminoso sobre el centro de la estancia.'));
C.push(p('Las dos caras cortas (frente y fondo) y las dos largas (laterales) son paneles horizontales; suelo y techo son retratos casi cuadrados. Al diseñar hay que pensar en perspectiva de estancia: la cara frontal es la que el jugador ve al entrar y concentra la identidad del salón; las laterales acompañan y pueden repetir motivos con variaciones; suelo y techo son piezas simétricas con un solo elemento central cada una. El peso total del cubemap del museo es de unos ' + pesoCubemap('') + ', cifra útil como presupuesto para las nuevas piezas.'));

C.push(h2('B.3 · Comparativa rápida de estilo entre salones'));
C.push(...figura('neon_frente', 240, 'Figura 5 · Cara frontal del Salón Neón Arcade (recreativas y marquesinas cian y rosa pintadas en el arte).'));
C.push(...figura('dojo_frente', 240, 'Figura 6 · Cara frontal del Dojo Zen (madera clara y farolillo de piedra pintados en el arte).'));
C.push(p('Las caras frontales de cada variante ya definen una identidad cromática distinta (azul museo, madera cálida de cabaña, cian y rosa neón, azul estelar, verde zen, gris urbano). El rediseño puede mantener esas identidades o unificarlas; en cualquier caso, cada una es una tanda independiente de seis caras.'));

C.push(h2('B.4 · Mobiliario 3D por variante (procedural)'));
C.push(p('No es arte de imagen: cada salón añade geometría 3D propia pegada a la pared frontal, con materiales emisivos y sin luces nuevas para no encarecer la escena. El museo y la cabaña no tienen props propios; las cuatro variantes restantes comparten además 7 bolas doradas flotantes y 2 luces cálidas.'));
C.push(tabla(
  ['Variante', 'Prop 3D', 'Detalle de materiales y colores'],
  [
    ['Neón', 'Dos recreativas flanqueando la pared', 'Cuerpo 0,66×1,58×0,58 m; marquesina emisiva cian 0x66e2ff y rosa 0xff5cb0; pantalla CRT con parpadeo'],
    ['Observatorio', 'Globo terráqueo con anillo orbital', 'Textura canvas 256×128 (océano 0x1a5cb0, continentes 0x3f8a48); anillo emisivo azul 0x50c8ff; gira y flota'],
    ['Dojo', 'Farolillo de piedra tōrō y bambúes', 'Caja de luz cálida emisiva + trío de bambúes'],
    ['Rascacielos', 'Maqueta de dos torres', 'Textura canvas 64×128 de ventanas encendidas (0xffd98a sobre 0x1c2430); baliza roja 0xff2418 con parpadeo'],
  ],
  [14, 30, 56], { size: 18 }));

C.push(h2('B.5 · Placas HUD del hall (canvas procedural)'));
C.push(tabla(
  ['Placa', 'Canvas fuente', 'Plano en escena', 'Contenido y paleta'],
  [
    ['EL PULSO CRAZY (reto diario)', '1024×600', '0,86×0,50 m en x −2,55, y 1,70', 'Título 900 en degradado #ffe08a→#c9932f; subtítulo con el reto del día; repintada cada medianoche'],
    ['TU RACHA (asistencia)', '1024×600', '0,86×0,50 m en x +2,55, y 1,70', 'Días de racha y récord; misma paleta dorada'],
    ['PARED DE INSIGNIAS', '1024×640', '2,00×1,25 m centrada, y 1,60', 'Cifras del perfil (victorias, racha, estrellas, ELO), 6 medallones de logros 2×3, 16 chips de bola y 8 de mesa'],
    ['Icono de música del salón', '256×256', '0,36×0,36 m sobre la gloria (y 2,42)', 'Altavoz dorado #ffd257 con ondas o gris #8d8676 con barra roja #ff4444; solo en salones con música'],
  ],
  [22, 12, 24, 42], { size: 18 }));
C.push(p('Estas placas se pintan en canvas 2D con la paleta dorada de museo (#c9932f de filo, #ffe08a de título, #b9a77f de subtítulo sobre fondo #241c15→#120c08) y se cuelgan como planos transparentes a doce milímetros de la pared. Rediseñarlas significa reescribir drawHallSign y drawHallGloria (c08), no sustituir ficheros; los textos vienen de la tabla de traducciones T() en español e inglés vivo.'));

C.push(h2('B.6 · El búho del Arcano (icono del menú)'));
C.push(...figura('arcano', 300, 'Figura 7 · El búho del Arcano actual: PNG 1024×683 RGBA (787 KB). Los ojos deben caer en (0.452, 0.392) y (0.557, 0.376) del lienzo.'));
C.push(p([{ t: 'El icono que abre la galería de superpoderes es la única pieza de arte externo del HUD: ' }, { t: 'arcano.png, 1024×683 RGBA (proporción 1,5:1, transparencia obligatoria)', b: true }, { t: '. Se usa dos veces: como placa de 0,585×0,39 m en la esquina superior derecha de la pared frontal y como búho grande de 1,32×0,88 m dentro del espacio Arcano. El detalle crítico para el rediseño: los destellos de los ojos son sprites aditivos anclados a las fracciones medidas (0.452, 0.392) y (0.557, 0.376) del lienzo; un arte nuevo debe colocar los ojos exactamente ahí o habrá que re-medir y actualizar la constante en c08 (línea 768). Si el fichero falta, hay un búho vectorial de respaldo azul #5fd4ff.' }]));

// ══ 5 · APARTADO C · ESPACIO ARCANO ══
C.push(h1('5 · Apartado C · El espacio Arcano (galería de superpoderes)'));
C.push(p('Al apuntar al búho, la escena se planta sobre los pies del jugador y abre una estancia infinita: bóveda celeste, suelo de losetas vivo, motas azules, cometas y una constelación que dibuja el logo del juego con un bolígrafo de luz. Casi todo es procedural; consumen ficheros solo el búho grande (el mismo arcano.png), el candado de poderes y la constelación (a través de su contorno trazado). La galería presenta cada superpoder en un panel holográfico con navegación por flechas.'));
C.push(...figura('palas', 300, 'Figura 8 · palas.png (1024×768 RGBA, 58 KB): el logo macizo del juego. No se muestra: su contorno vive trazado en 34 polilíneas.'));
C.push(...figura('candado', 110, 'Figura 9 · candado.png (512×512 RGBA, 14 KB): silueta negra que recorta contra el halo rojo del bloqueo.'));
C.push(tabla(
  ['Pieza', 'Recurso o fuente', 'Características y presentación'],
  [
    ['Bóveda celeste', 'Canvas 1024×512 procedural', 'Esfera invertida r=58 m; degradado azul noche #03061a→#071129→#0a1a36'],
    ['Suelo de losetas', 'Lienzo vivo 512×512 por frame', '72×72 m en 48×48 losetas de 1,5 m; destellos que dibujan la trama y celdas azules rgb(16,40,78)→rgb(26,56,104)'],
    ['Motas y cometas', '240 puntos aditivos + 3 sprites', 'Color 0x49b6ff, tamaño 0,026; cometas con halo alargado blanco-azul'],
    ['Constelación de palas', 'palas.png → ARCANO_PALAS_TRAZO', '34 polilíneas (marching squares + Douglas-Peucker 1,6 px); plano 15×11,25 m a 45 m; tres pasadas de glow azul'],
    ['Búho grande', 'assets/hall/arcano.png', 'Plano 1,32×0,88 m a y 2,28; mismos destellos de ojos que la placa'],
    ['Letrero Salir / Exit', 'Canvas 256×96 procedural', '0,46×0,1725 m sobre el búho; texto 800 40 px system-ui con triple pasada azul'],
    ['Panel de la galería', 'Canvas 1024×700 + capa holo', '1,46×1,00 m a y 1,32; cristal rgba(10,24,48,.94), marco rgba(80,180,255,.9), título EL ARCANO #8fdcff; medallón circular del icono del poder (r 96 px)'],
    ['Flechas ‹ ›', 'Canvas 128×128 procedural', '0,20×0,20 m a x ±0,93; disco oscuro y chevron #8fdcff; sin flecha en los extremos del registro'],
    ['Candado de poderes', 'assets/hall/candado.png', '512×512 RGBA, silueta NEGRA sobre alfa; plano 0,16×0,16 m en (−0,612, 1,585) delante del panel; halo rojo pulsante rgba(255,45,30) que la silueta recorta'],
    ['Iconos de los poderes', '16 PNG base64 en c12', '256×256 cada uno (de 7 a 66 KB); recorte a sangre completa en el medallón del panel'],
    ['Música del Arcano', 'assets/hall/arcano.mp3', 'MP3 192 kbps 44,1 kHz estéreo, 161,9 s, 3,7 MB; arranca solo dentro del espacio Arcano'],
  ],
  [20, 26, 54], { size: 18 }));
C.push(p('Dos advertencias de rediseño para este apartado. Primera: palas.png no es una textura en uso sino el origen del trazo; cambiar el logo exige re-trazar con el script gen_trazo_palas_r47.py y regenerar la constante ARCANO_PALAS_TRAZO (c08, línea 1517), o la constelación seguirá dibujando el logo viejo. Segunda: el candado.png debe seguir siendo una silueta negra pura sobre transparencia, porque su lectura visual depende del halo rojo aditivo que hay detrás; un candado con relleno colorido rompería el efecto.'));
C.push(p('La voz del sistema presenta cada poder con anuncio solemne y los estados de bloqueo parpadean en azul #49b6ff ↔ rojo #ff3524 en los ojos del búho. El panel incluye índice (i de n), nombre, tipo con color por categoría, descripción envuelta y métricas; todos esos textos son traducibles y dinámicos, así que el rediseño del panel es totalmente de composición y paleta, no de contenido.'));

module.exports = C;
