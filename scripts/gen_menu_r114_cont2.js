// gen_menu_r114_cont2.js — contenido: Menú 2D (D), Palas (E), Audio (F), Cancha (G),
// catálogo maestro (10), reglas y flujo (11), anexo técnico (12)
const fs = require('fs');
const { P, h1, h2, p, nota, vineta, tabla, figura, pesoCubemap } = require('./gen_menu_r114_lib.js');

const ACT = JSON.parse(fs.readFileSync('/home/z/my-project/scripts/_menu_activos.json', 'utf8'));
const B64 = JSON.parse(fs.readFileSync('/home/z/my-project/scripts/_menu_base64.json', 'utf8'));
const kb = v => String(Math.round(v));

const C = [];

// ══ 6 · APARTADO D · MENÚ 2D ══
C.push(h1('6 · Apartado D · Menú 2D de sala (canvas del juego)'));
C.push(p('El menú de configuración se dibuja en un canvas 2D dentro de la escena, con estética de placa de museo coherente con el hall. Su única pieza de arte externa es el logo bitmap incrustado en c10 (línea 1): un JPEG de 840×388 y 82 KB usado en la cabecera del menú. Todo lo demás es vectorial: las filas de la pantalla ESCOGER HALL son placas de 150 px de alto con medallón, el candado de las salas bloqueadas es un glifo vectorial propio (PP_ICONS.candado, distinto del candado.png del Arcano), y los textos salen de la tabla de traducciones con español e inglés vivo.'));
C.push(tabla(
  ['Pantalla o elemento', 'Arte implicado', 'Detalle'],
  [
    ['Cabecera del menú', 'Logo JPEG 840×388 (c10:1)', 'Único consumidor: c12:2066; ratio 2,17:1'],
    ['ESCOGER HALL (6 filas)', 'Sin arte; placas vectoriales', 'Nombre en oro si está activa, hito de desbloqueo con recorte con elipsis, candado vectorial sobre las bloqueadas'],
    ['Visita online', 'Sin arte', 'Mensaje De visita online ves el salón del ANFITRIÓN y arte del anfitrión'],
    ['Grid Arte del hall', 'Sin arte propio', '6 celdas en 3 columnas con estado actual/conseguida y candado; pie con nota de recompensas'],
    ['Sonidos de menú', 'Osciladores (sin ficheros)', 'Variante bloqueada: barrido descendente 330→260 Hz; elección confirmada con clic'],
    ['Elección de variante', 'Código', 'applyHallVariant en vivo + persistencia pp_hallvar + evento hallv al rival'],
  ],
  [24, 26, 50], { size: 18 }));
C.push(p('Para el rediseño del menú 2D, el trabajo es de composición y paleta sobre las funciones de dibujo de c12 (drawMenuHallPick y el grid de Arte del hall); solo el logo es una pieza gráfica sustituible. Si se rediseña la identidad, conviene regenerar el logo con alfa (PNG) o mantener el JPEG con fondo integrado, cuidando el ratio 2,17:1 para no romper la cabecera.'));

// ══ 7 · APARTADO E · PALAS ══
C.push(h1('7 · Apartado E · Palas: catálogo y modelos 3D'));
C.push(p([{ t: 'La pala base es un modelo externo con respaldo: el juego intenta cargar ' }, { t: 'assets/pala/pala.glb (GLB de 1,38 MB)', b: true }, { t: ' y si falla parsea una copia incrustada en base64 dentro de c01. El contrato del modelo es estricto: ejes con la hoja hacia +Y, mango hacia −Y y cara normal ±Z; la escala la fija el código en 0,026 m/unidad, con lo que la hoja mide 16 cm y la pala completa 26 cm. Un proceso posterior endurece el modelo (corrige winding, fuerza doble cara, ajusta metalicidad y rugosidad). El repintado por piel lo hacen las texturas procedurales: el color edge pinta el canto (mesh trim del GLB) y el grip la cinta del mango.' }]));
C.push(p('La pala Pro Carbon es el caso especial: su campo modelUrl sustituye el modelo entero por assets/pala/pala_pro.glb (34 KB) con respaldo a su textura procedural. Además de las palas, existe un segundo modelo incrustado, la pistola de rayos del superpoder Arkanoide (GLB en base64, escala 0,05, unos 18,8 cm), que pertenece al gameplay pero conviene documentar porque comparte pipeline.'));
C.push(tabla(
  ['Id', 'Nombre', 'Desbloqueo', 'Textura (clave)', 'Canto (edge)', 'Cinta (grip)', 'Modelo'],
  [
    ['clasica', 'Clásica', 'Disponible', '— (madera base)', '—', '0x6b4a2f', 'pala.glb'],
    ['fuego', 'Fuego', '150 puntos', 'fuego', '0xff5a2a', '0xc22a12', 'pala.glb'],
    ['hielo', 'Hielo', '400 puntos', 'hielo', '0x35c4e8', '0x1479a3', 'pala.glb'],
    ['oro', 'Oro', '800 puntos', 'oro', '0xf2c14e', '0x3a2c10', 'pala.glb'],
    ['arcoiris', 'Arcoíris', '1500 puntos', 'holo (animada)', '0xb07aff', '0x8e44ad', 'pala.glb'],
    ['carbon', 'Pro Carbon', '2500 puntos', 'carbon', '0xff2d2d', '0x17181c', 'pala_pro.glb'],
    ['neon', 'Neón', 'Racha de 7 días', 'neon', '0x39ff88', '0x0f3d2e', 'pala.glb'],
    ['fantasma', 'Fantasma', 'Racha de 14 días', 'fantasma', '0xbfe9ff', '0x43545e', 'pala.glb'],
    ['campeon', 'Campeón', 'Racha de 30 días', 'oro (animada)', '0xffd700', '0x4a3808', 'pala.glb'],
  ],
  [11, 12, 15, 17, 12, 12, 21], { size: 18 }));
C.push(p('Los desbloqueos de palas son coste en puntos de entrenamiento o días de racha del Reto del Día; ningún candado depende de ficheros de arte. Las claves de textura (fuego, hielo, oro, holo, carbon, neon, fantasma) corresponden a constructores canvas de TEX_BUILDERS en c13: rediseñar el aspecto de una piel es escribir un nuevo constructor o ajustar colores, no sustituir ficheros. Si se produce un GLB nuevo de pala, debe respetar la jerarquía de meshes que el repintado espera (trim para el canto, cinta para el grip) y los anclajes PALA_GRIP_Y (−2,9) y PALA_BLADE_Y (2,1115).'));

// ══ 8 · APARTADO F · AUDIO ══
C.push(h1('8 · Apartado F · Audio del menú y los salones'));
C.push(p([{ t: 'El sistema sonoro del menú se rige por el ' }, { t: 'invariante UNA MELODÍA', b: true }, { t: ': solo suena una pista contextual cada vez. La portada tiene su OGG embebido (a 0,5 en 2D, 0,26 × musicVol dentro del juego); cada salón tiene su MP3 (0,30 × musicVol, fundidos de 1,2 s de entrada y 1,0 s de salida, caché LRU de 3 buffers); el museo clásico es deliberadamente silencioso; y el espacio Arcano cambia la pista del salón por arcano.mp3 mientras dura la visita, restaurándola al salir. Cualquier rediseño sonoro debe respetar esa cadena de prioridad y los fundidos, no solo las pistas.' }]));
C.push(tabla(
  ['Contexto', 'Pista', 'Formato y duración', 'Volumen y notas'],
  [
    ['Portada 2D', 'OGG base64 (07_tail:19)', 'Vorbis, 89,7 s, 929 KB', '0,5 en 2D; bucle; arranca al primer toque'],
    ['Museo', 'Sin música (por diseño)', '—', 'Única variante silenciosa'],
    ['Cabaña', 'cabana/cabana.mp3', 'MP3 192 kbps estéreo, 175,4 s', '0,30 × musicVol; icono de pared permite silenciar'],
    ['Neón', 'neon/arcade.mp3', 'MP3 192 kbps estéreo, 176,4 s', 'Ídem'],
    ['Observatorio', 'observatorio/observatorio.mp3', 'MP3 192 kbps estéreo, 158,7 s', 'Ídem'],
    ['Dojo', 'dojo/dojo.mp3', 'MP3 192 kbps estéreo, 175,6 s', 'Ídem'],
    ['Rascacielos', 'rascacielos/rascacielos.mp3', 'MP3 192 kbps estéreo, 177,3 s', 'Ídem'],
    ['Espacio Arcano', 'arcano.mp3', 'MP3 192 kbps estéreo, 161,9 s', 'Sustituye temporalmente la pista del salón'],
    ['Murmullo de pabellón', 'Ruido rosa procedural', 'Sintetizado', 'Base 0,05; entra 1,5 s, sale 0,8 s'],
  ],
  [16, 26, 26, 32], { size: 18 }));
C.push(p('Los efectos de golpe son 5 WAV base64 a 44,1 kHz mono (mesa, pala, canto, red y suelo) mezclados por impacto con rangos de tono definidos; la voz del megáfono es un banco Piper→Opus incrustado por idioma con frases de bienvenida (la frase de bienvenida al modo suena en el menú), salas, dificultad y números, con respaldo de speechSynthesis solo en 2D. Los clics de interfaz son osciladores breves. Para el rediseño: las voces exigirían regenerar el banco con la voz elegida; los SFX de UI son código y se ajustan en los mismos ficheros fuente.'));

// ══ 9 · APARTADO G · CANCHA DE PARTIDO ══
C.push(h1('9 · Apartado G · La cancha de partido (contexto del rediseño)'));
C.push(p('La cancha no es parte del menú, pero comparte pipeline y contrato con el hall, así que se documenta como contexto. La sala es 100 % procedural (suelo, grid, cuatro paredes, techo, paneles de luz, tiras ámbar y anillo) y sus planos se visten con una cadena de prioridad: decorado del campeonato activo, salón del anfitrión y, por defecto, assets/partido/. Esa carpeta contiene cinco JPG con las mismas proporciones canónicas que el hall; la cara derecha no existe como fichero porque la imagen de izquierda se asigna a las dos paredes laterales por decisión expresa del dueño.'));
C.push(tabla(
  ['Fichero', 'Resolución', 'Peso', 'Uso'],
  [
    ['assets/partido/frente.jpg', '1849×864', '334,7 KB', 'Pared frontal de la cancha'],
    ['assets/partido/fondo.jpg', '1849×864', '437,4 KB', 'Pared trasera'],
    ['assets/partido/izquierda.jpg', '2395×864', '386,4 KB', 'Ambas paredes laterales (misma imagen)'],
    ['assets/partido/suelo.jpg', '1296×1678', '234,1 KB', 'Suelo de la cancha'],
    ['assets/partido/techo.jpg', '1296×1678', '381,5 KB', 'Techo'],
    ['assets/pista/suelo_pista.jpg', '1296×1678', '234,1 KB', 'Fichero suelto de pista (mismo peso que el suelo del partido)'],
  ],
  [30, 16, 14, 40], { size: 18 }));
C.push(p('El teñido por variante solo aplica a decorados de campeonato, nunca al arte por defecto ni al salón. Las banderas de fin de partida sí son piezas de arte visibles tras el juego: cuatro WebP de 1024×1024 con alfa incrustados en base64 (dos por idioma, victoria y derrota, entre 69 y 113 KB) mostradas en un plano cuadrado de 1,18 m sobre la mesa con respaldo a canvas si la imagen no decodifica.'));
C.push(...figura('poster_win', 200, 'Figura 10 · Bandera de victoria actual: WebP 1024×1024 con alfa, incrustado por idioma en c08.'));

// ══ 10 · CATÁLOGO MAESTRO ══
C.push(h1('10 · Catálogo maestro de piezas para el rediseño'));
C.push(p('Este catálogo es la lista de trabajo ordenada del proyecto: cada fila es una pieza (o tanda homogénea de piezas) con su ubicación, sus características actuales verificadas, el requisito que el código impone y la especificación recomendada. La columna de esfuerzo estima el trabajo por pieza considerando tamaño del arte, número de variantes y si exige tocar código o herramientas de trazado. La recomendación de orden de ejecución está en la sección 11.'));
C.push(h2('10.1 · Piezas externas (sustituir ficheros, sin tocar código)'));
C.push(tabla(
  ['Nº', 'Pieza', 'Ubicación', 'Características actuales y requisito del código', 'Spec de rediseño recomendada', 'Esfuerzo'],
  [
    ['1', 'Hero y fondo de portada', 'Base64 en 00_head:29 y 03_body:17', 'JPEG 1280×720, 161 KB, sin alfa; una pieza para dos roles (hero 680 px y fondo blur)', 'JPEG 1600×900 o superior; una sola pieza que aguante esquinas redondeadas y recorte de fondo; título legible al 42 % de brillo', 'Baja'],
    ['2', 'Botón JUGAR EN VR (ES/EN)', 'Base64 en 03_body:32-33', '2 PNG 512×128 (91 y 89 KB); texto horneado; máx. 360 px con pulso y vaivén', '2 PNG con alfa a 1024×256; margen perimetral para la animación; dos idiomas', 'Media'],
    ['3', 'Palas-bandera ES/EN', 'Base64 en 03_body:22 y 26', '2 PNG 160×160 (12 y 19 KB) mostrados a 84×84', '2 PNG con alfa a 320×320; la etiqueta de texto es DOM, no arte', 'Baja'],
    ['4', 'Vídeo de intro', 'assets/intro.mp4', 'H.264 1920×1080, 10,0 s, 5,5 MB; visor con sonido y ducking; sin póster declarado', 'Mantener 16:9 1920×1080; duración libre (hoy 10 s); valorar póster de fallback en el HTML', 'Media'],
    ['5', 'Logo del menú 2D', 'Base64 en c10:1', 'JPEG 840×388, 82 KB; cabecera del menú', 'PNG con alfa o JPEG; respetar ratio 2,17:1', 'Baja'],
    ['6', 'Cubemap del museo', 'assets/hall/ (6 JPG)', 'frente/fondo 1849×864; laterales 2395×864; suelo/techo 1296×1678; total ' + pesoCubemap(''), 'Respetar proporciones y nombres exactos; JPG RGB; centro libre; emblema en suelo y círculo en techo; arte pinta todo el mobiliario', 'Alta'],
    ['7', 'Cubemap cabaña (+ MP3)', 'assets/hall/cabana/', '6 JPG + cabana.mp3 (175,4 s); cubemap ' + pesoCubemap('/cabana'), 'Mismas proporciones; identidad madera de refugio; música de bucle instrumental', 'Alta'],
    ['8', 'Cubemap neón (+ MP3)', 'assets/hall/neon/', '6 JPG + arcade.mp3 (176,4 s); cubemap ' + pesoCubemap('/neon'), 'Mismas proporciones; identidad cian/rosa arcade', 'Alta'],
    ['9', 'Cubemap observatorio (+ MP3)', 'assets/hall/observatorio/', '6 JPG + observatorio.mp3 (158,7 s); cubemap ' + pesoCubemap('/observatorio'), 'Mismas proporciones; identidad azul estelar', 'Alta'],
    ['10', 'Cubemap dojo (+ MP3)', 'assets/hall/dojo/', '6 JPG + dojo.mp3 (175,6 s); cubemap ' + pesoCubemap('/dojo'), 'Mismas proporciones; identidad zen en madera clara', 'Alta'],
    ['11', 'Cubemap rascacielos (+ MP3)', 'assets/hall/rascacielos/', '6 JPG + rascacielos.mp3 (177,3 s); cubemap ' + pesoCubemap('/rascacielos'), 'Mismas proporciones; identidad urbana nocturna', 'Alta'],
    ['12', 'Búho del Arcano', 'assets/hall/arcano.png', 'PNG 1024×683 RGBA, 787 KB; dos usos (placa 0,585×0,39 m y búho 1,32×0,88 m)', 'PNG RGBA 1024×683 (o superior manteniendo 1,5:1); transparencia obligatoria; ojos en (0.452, 0.392) y (0.557, 0.376) del lienzo o re-medir c08:768', 'Media'],
    ['13', 'Candado de poderes', 'assets/hall/candado.png', 'PNG 512×512 RGBA, 14 KB; silueta negra sobre alfa; plano 0,16×0,16 m con halo rojo', 'Silueta negra pura sin relleno; el halo lo recorta en runtime', 'Baja'],
    ['14', 'Constelación de palas (logo)', 'assets/hall/palas.png + trazo en c08:1517', 'PNG 1024×768 RGBA, 58 KB; NO se muestra: vive como 34 polilíneas trazadas', 'Si cambia el logo: re-trazar con gen_trazo_palas_r47.py y regenerar ARCANO_PALAS_TRAZO', 'Alta'],
    ['15', 'Música de salones y Arcano', 'assets/hall/*/*.mp3 (6 pistas)', 'MP3 192 kbps 44,1 kHz estéreo, 158,7 a 177,3 s; bucle con fundidos', 'Instrumentales de bucle limpio (sin golpe de cierre); mantener duraciones aproximadas', 'Media'],
    ['16', 'Modelos de pala', 'assets/pala/pala.glb y pala_pro.glb', 'GLB 1,38 MB y 34 KB; escala de código 0,026; ejes hoja +Y, mango −Y, cara ±Z; repintado sobre trim y cinta', 'GLB con la misma jerarquía de meshes (trim, cinta) y anclajes PALA_GRIP_Y −2,9 y PALA_BLADE_Y 2,1115', 'Alta'],
  ],
  [5, 15, 17, 30, 27, 6], { size: 16 }));
C.push(h2('10.2 · Piezas incrustadas en base64 (regenerar el literal en el código)'));
C.push(tabla(
  ['Nº', 'Pieza', 'Ubicación', 'Características actuales', 'Spec de rediseño recomendada', 'Esfuerzo'],
  [
    ['17', 'Música de portada', 'Base64 en 07_tail:19', 'OGG Vorbis 89,7 s, 929 KB; bucle; vol 0,5 en 2D', 'Instrumental de bucle; regenerar el literal base64; valorar rebajar a 60-75 s para perder peso', 'Media'],
    ['18', 'Iconos de los superpoderes', '16 PNG base64 en c12 (21537-21680)', '256×256 cada uno, de 7 a 66 KB', 'PNG con alfa 256×256 (o 512 y recorte); composición pensada para medallón circular r 96 px', 'Media'],
    ['19', 'Banderas de fin de partida', '4 WebP base64 en c08:2657-2658', '1024×1024 con alfa, 69-113 KB; ES/EN × victoria/derrota', 'WebP cuadrado con alfa; margen para los chips de datos superpuestos', 'Media'],
    ['20', 'Insignias PWA', 'public/logo-192/512/maskable', 'PNG de marca del manifest', 'Regenerar si cambia la identidad; versión maskable con zona de seguridad', 'Baja'],
    ['21', 'Banco de voz del megáfono', 'VOICE_B64 ES/EN en c00', 'Piper→Opus; frases de bienvenida, salas, dificultad, números', 'Regenerar con la voz objetivo y recomprimir a Opus; respaldo speechSynthesis intacto', 'Media'],
    ['22', 'SFX de impacto (5 WAV)', 'PP_SFX_REALES_B64 en c03', '44,1 kHz mono; mesa, pala, canto, red, suelo', 'Regenerar con síntesis modal o muestras nuevas; mezcla en CONFIG_AUDIO', 'Media'],
  ],
  [5, 15, 20, 26, 28, 6], { size: 16 }));
C.push(h2('10.3 · Arte procedural (rediseño = reescribir funciones de dibujo)'));
C.push(tabla(
  ['Nº', 'Pieza', 'Fuente (fichero:línea)', 'Características actuales', 'Spec de rediseño recomendada', 'Esfuerzo'],
  [
    ['23', 'Placas EL PULSO CRAZY y TU RACHA', 'drawHallSign c08:37-80', 'Canvas 1024×600 → plano 0,86×0,50 m; paleta dorada de museo', 'Nueva composición y paleta; el título auto-encoge hasta caber; textos via T()', 'Media'],
    ['24', 'Pared de insignias', 'drawHallGloria c08:147-260', 'Canvas 1024×640 → plano 2,00×1,25 m; 6 medallones, 16 chips de bola, 8 de mesa', 'Rediseño de cuadrícula y aros (oro #e9b83c activo, gris #3a4048 inactivo); datos dinámicos del perfil', 'Media'],
    ['25', 'Icono de música del salón', 'drawHallMusica c08:89-134', 'Canvas 256×256 → plano 0,36×0,36 m; dos estados', 'Dos estados claros (sonando/silenciado); alfa obligatoria; hover ×1,16 en código', 'Baja'],
    ['26', 'Panel del Arcano', 'drawArcanoPanel c08:1383-1505', 'Canvas 1024×700 + capa holo de materialización → plano 1,46×1,00 m', 'Rediseño de cristal, marco y tipografía; mantener versión holo (bandas, scanlines) y textos i18n', 'Alta'],
    ['27', 'Flechas y letrero Salir', 'drawArcano* c08:1301-1381', 'Canvas 128×128 y 256×96; glow azul en tres pasadas', 'Ajuste de chevron y glow; hover con latido en código', 'Baja'],
    ['28', 'Bóveda, suelo de losetas, motas y cometas', 'c08:1078-1195 y 1600-1618', 'Esfera r=58 con canvas 1024×512; suelo 72×72 m con lienzo vivo por frame; 240 motas 0x49b6ff', 'Rediseño de paleta azul noche y trama de losetas; cuidar el coste por frame del lienzo vivo', 'Alta'],
    ['29', 'Props por variante', 'montarProps c08:816-919', 'Recreativas (neón), globo y anillo (observatorio), farol y bambú (dojo), torres (rascacielos)', 'Geometría emisiva sin luces nuevas; pegada a z0+0,62; paletas ya definidas por salón', 'Media'],
    ['30', 'Texturas de pieles de pala', 'TEX_BUILDERS c13:2949', '7 claves canvas (fuego, hielo, oro, holo, carbon, neon, fantasma) + colores edge/grip del catálogo', 'Nuevos constructores canvas por piel; el GLB aporta trim y cinta para el repintado', 'Media'],
    ['31', 'Candado del menú 2D y cabeceras', 'PP_ICONS y drawMenuHallPick c12', 'Glifo vectorial sobre las placas de sala bloqueada', 'Glifo nuevo coherente con la identidad; distinto de candado.png', 'Baja'],
  ],
  [5, 15, 20, 26, 28, 6], { size: 16 }));

// ══ 11 · REGLAS DE ORO Y FLUJO ══
C.push(h1('11 · Reglas de oro y flujo de trabajo recomendado'));
C.push(p('Las reglas siguientes resumen los contratos del código que ningún arte nuevo puede romper. Son la diferencia entre una sustitución limpia y un hall roto (plano gris por fichero ausente, destellos de ojos flotando fuera del búho, constelación dibujando un logo viejo).'));
C.push(vineta([{ t: 'Proporciones exactas de cubemap: ', b: true }, { t: 'frente/fondo 1849×864, laterales 2395×864, suelo/techo 1296×1678, en las seis variantes; JPG RGB opacos, mapeo 1:1 sin distorsión.' }]));
C.push(vineta([{ t: 'Nombres de fichero fijos: ', b: true }, { t: 'frente, fondo, izquierda, derecha, suelo, techo (.jpg) más el MP3 por carpeta; la carga es perezosa y el fallback es un plano de color.' }]));
C.push(vineta([{ t: 'Transparencia solo donde toca: ', b: true }, { t: 'arcano.png, candado.png, palas.png, botones e iconos son RGBA; las caras del cubemap y los fondos son JPEG sin alfa.' }]));
C.push(vineta([{ t: 'Ojos del búho: ', b: true }, { t: 'destellos anclados a (0.452, 0.392) y (0.557, 0.376) del lienzo; arte nuevo debe cumplirlo o re-medirse la constante.' }]));
C.push(vineta([{ t: 'Contorno antes que imagen: ', b: true }, { t: 'cambiar palas.png exige re-trazar y regenerar ARCANO_PALAS_TRAZO (34 polilíneas).'}]));
C.push(vineta([{ t: 'Silueta negra del candado: ', b: true }, { t: 'candado.png recorta contra el halo rojo aditivo; sin silueta pura el efecto desaparece.' }]));
C.push(vineta([{ t: 'Textos via T(): ', b: true }, { t: 'nada de texto horneado en arte procedural; solo los botones de portada llevan texto en imagen (duplicado por idioma).' }]));
C.push(vineta([{ t: 'Invariante UNA MELODÍA: ', b: true }, { t: 'una sola pista contextual; fundidos de entrada y salida respetados; el museo no lleva música.' }]));
C.push(vineta([{ t: 'Presupuesto de peso: ', b: true }, { t: 'el hall pesa hoy unos 30 MB con sus seis variantes; subir la resolución de las caras multiplica ese coste por seis.' }]));
C.push(tabla(
  ['Etapa', 'Piezas del catálogo', 'Criterio'],
  [
    ['1', 'Nº 1 a 3 (portada: hero, botones, banderas)', 'Máxima visibilidad, esfuerzo bajo; define la identidad nueva'],
    ['2', 'Nº 6 (museo) y Nº 12 (búho)', 'El salón por defecto y el icono del menú; valida el contrato de cubemap y de ojos'],
    ['3', 'Nº 23 a 27 (placas, insignias, icono, panel, flechas)', 'Coherencia del HUD con la nueva identidad; solo código canvas'],
    ['4', 'Nº 5 y 17 a 19 (logo menú, música portada, iconos, banderas)', 'Piezas embebidas; regenerar literales base64'],
    ['5', 'Nº 7 a 11 (cinco salas con su música)', 'El lote más grande; repetir la plantilla validada del museo'],
    ['6', 'Nº 14 a 16 (constelación, música restante, GLB)', 'Piezas con herramienta o contrato 3D estricto'],
  ],
  [10, 42, 48], { size: 18 }));
C.push(p('El flujo por pieza recomendado: elegir la fila del catálogo, producir el arte según la spec, sustituir el fichero externo o regenerar el literal base64, y validar en el juego entrando al hall correspondiente (las caras sin fichero caen a color de respaldo, que es el síntoma rápido de un nombre o proporción mal puestos). Para las piezas procedurales el paso de producción es código: reescribir la función de dibujo manteniendo las llamadas de datos dinámicos.'));

// ══ 12 · ANEXO ══
C.push(h1('12 · Anexo · Ficha técnica de activos medidos en disco'));
C.push(p('La tabla siguiente recoge los 54 activos externos de public/assets/ con sus valores medidos (formato, dimensiones o duración, peso). Es la referencia objetiva para comprobar que cualquier pieza nueva entra dentro de las características que el pipeline espera. Los pesos están en kilobytes y las duraciones en segundos.'));
const filas = [];
for (const [k, d] of Object.entries(ACT)) {
  const esGlb = k.endsWith('.glb');
  const tipo = (d.tipo === 'error' && esGlb) ? 'modelo3d' : d.tipo;
  let dim = '';
  if (d.tipo === 'video') {
    dim = d.ancho + '×' + d.alto + ' · ' + String(d.duracion_s).replace('.', ',') + ' s';
  } else if (esGlb || d.tipo === 'modelo3d') {
    dim = 'modelo 3D (GLB)';
  } else if (d.ancho) {
    dim = d.ancho + '×' + d.alto + (d.alfa ? ' RGBA' : ' RGB');
  } else if (d.duracion_s) {
    dim = d.duracion_s.toFixed(1).replace('.', ',') + ' s · ' +
      (d.canales === 2 ? 'estéreo' : 'mono') + ' · ' + d.bitrate_kbps + ' kbps';
  } else {
    dim = tipo;
  }
  filas.push([k, tipo, dim, kb(d.peso_kb)]);
}
C.push(tabla(['Fichero', 'Tipo', 'Dimensiones o duración', 'Peso (KB)'], filas, [42, 12, 34, 12], { size: 16 }));
C.push(p('Adicionalmente, el escaneo del código fuente encontró 57 piezas únicas incrustadas en base64: 27 imágenes (el hero-fondo compartido, 4 piezas de portada, el logo del menú, 4 banderas de fin de partida y 16 iconos de superpoderes) y 30 audios (la música de portada y el banco de voz y efectos de campeonatos). Su detalle de ubicación está recogido en las fichas y en el catálogo maestro de este documento.'));
nota('Documento generado el 22 de noviembre de 2026 a partir del código fuente V3.6.209-SDK6. Las miniaturas son vistas reducidas de las piezas actuales; las medidas proceden de la lectura directa de los ficheros en public/assets/ y del análisis del código en src/game/.');

module.exports = C;
