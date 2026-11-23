// gen_espectador_r115_cont.js — contenido de la propuesta de modo espectador
const fs = require('fs');
const { P, h1, h2, h3, p, nota, vineta, tabla } = require('./gen_menu_r114_lib.js');

const FIG = JSON.parse(fs.readFileSync('/home/z/my-project/scripts/_fig_dims.json', 'utf8'));

function figura(anchoPx, pie) {
  const buf = fs.readFileSync('/home/z/my-project/download/_thumbs_r115/' + FIG.f);
  const alto = Math.round(anchoPx * FIG.h / FIG.w);
  return [
    new (require('docx').Paragraph)({
      alignment: require('docx').AlignmentType.CENTER,
      spacing: { before: 120, after: 40 },
      children: [new (require('docx').ImageRun)({
        data: buf, transformation: { width: anchoPx, height: alto }, type: 'png' })],
    }),
    new (require('docx').Paragraph)({
      alignment: require('docx').AlignmentType.CENTER, spacing: { after: 160, line: 276 },
      children: [new (require('docx').TextRun)({
        text: pie, size: 18, color: P.secondary, font: { ascii: 'Times New Roman' }, italics: true })],
    }),
  ];
}

const C = [];

// ══ 1 · RESUMEN EJECUTIVO ══
C.push(h1('1 · Resumen ejecutivo · las tres respuestas'));
C.push(p([{ t: '¿Es posible un modo espectador dentro del juego? ' , b: true }, { t: 'Sí, y encaja de forma natural con la arquitectura actual: un espectador es un tercer par de solo lectura atendido por el anfitrión. El código hoy rechaza expresamente un segundo par cuando hay una conexión viva (c09:269-275) y solo contempla dos roles, anfitrión e invitado (c09:9, 221, 239), pero las rutas de salida y de entrada que el espectador necesita ya existen y están localizadas: el fan-out se añade en los tres puntos por donde el anfitrión emite (c09:437, 1600, 2520) y la recepción reutiliza intactas las rutas del invitado (c09:1779, 1191). La alternativa de retransmitir por el servicio no encaja hoy: el worker solo expone HTTP (ICE, presencia e invitaciones) sin socket persistente.' }]));
C.push(p([{ t: '¿Introduciría latencia en el multijugador? ', b: true }, { t: 'No tiene por qué introducirla, porque el espectador consume y no produce: todo su tráfico es de descarga y no toca el camino de entrada del duelo. El riesgo real es doble y distinto: la saturación de la conexión de SUBIDA del anfitrión si cada espectador recibe el flujo completo, y la CPU del anfitrión (un visor Quest) al sostener varias conexiones extra. Con un flujo reducido para espectadores (pose a 15 Hz y bola a 10 Hz en lugar de 60/20-30) el coste cae a unos 2,5 KB/s por espectador, y con un límite de 4 a 6 espectadores el anfitrión añade en total menos de 15 KB/s, órdenes de magnitud por debajo de lo que ya consume la voz. Con eso, la latencia del duelo queda intacta.' }]));
C.push(p([{ t: '¿Pueden los espectadores participar o influir? ', b: true }, { t: 'Sí, por niveles. Existe un catálogo con cuatro niveles de implicación: cosmética local (cámaras, repeticiones, estadísticas), ambiente compartido (ovación colectiva que alimenta el megáfono y las luces del salón), ritmo sin resultado (votar el salón del próximo partido, tiempo muerto colectivo) y gameplay directo canalizado por voto mayoritario (el sistema de poderes de Duelos ya tiene el gancho: pow, c09:539). La regla de oro que protege la competitividad: en partidas clasificadas el nivel de gameplay se desactiva, los votos se agregan y filtra SOLO el anfitrión, y el árbitro de puntos (claim/ack y resync, c09:818-826, 2055-2086) nunca acepta decisiones del público.' }]));
C.push(p('Este documento justifica las tres respuestas con el código actual (secciones 2 a 5), propone el diseño del espectador pasivo con cambios concretos (sección 4 y 5), cataloga las mecánicas de influencia con su coste y riesgo (sección 6), y ordena la implementación en cinco fases mapeadas a ficheros (sección 7). Todas las cifras de tráfico y frecuencias proceden de las constantes y comentarios del código, citados por fichero y línea.'));

// ══ 2 · CÓMO FUNCIONA EL MULTIJUGADOR HOY ══
C.push(h1('2 · Cómo funciona el multijugador de CrazyPP hoy'));
C.push(h2('2.1 · Topología y autoridad'));
C.push(p('La partida en línea es par-a-par simétrico con autoridad por mitad de mesa: quien tiene la bola en su mitad decide botes, fallos y puntos, y el anfitrión actúa como árbitro final cuando hay disputa (c09:840-844). Ambos extremos simulan la física de la bola con el mismo motor determinista: el dueño integra y emite instantáneas, y el rival simula un fantasma con la física real que se corrige con interpolación (c12:18794-18835; c09:2222-2242). El anfitrión es además el reloj de referencia del duelo (c09:984; c09b:364-365). No hay servidor de simulación ni relay de datos: la señalización usa la nube pública de PeerJS, y un worker HTTP propio entrega credenciales efímeras de TURN para el atravesado de NAT (c09:858-935) y gestiona presencia e invitaciones (c09c:169, 241, 263).'));
C.push(p('La consecuencia estructural para un modo espectador es doble. Primera: la malla es estrictamente 1:1 — los campos de conexión son singulares y un par entrante se rechaza si hay conexión viva (c09:5, 269-275) —, así que el espectador exige una lista de conexiones de solo lectura, algo que hoy no existe. Segunda: el invitado es inalcanzable (su ID de PeerJS es anónimo, c09:255), de modo que el único punto de enganche posible es el anfitrión, que ya recibe y decodifica la pose del invitado (c09:1806-1821) y puede retransmitirla marcada con su origen.'));

C.push(h2('2.2 · Canales y catálogo de mensajes'));
C.push(tabla(
  ['Canal', 'Tipo', 'Contenido', 'Frecuencia y coste'],
  [
    ['fast (RTC)', 'Binario, no fiable, sin orden', 'Pose del avatar (cabeza + 2 manos, 31 B) + SNAP de bola (33 B) + eventos HIT (46 B) y HANDOFF (45 B) fiables por retransmisión hasta ack', 'Pose 60 Hz (52 B/paquete ≈ 3,1 KB/s); SNAP 20-30 Hz (54 B ≈ 1,1-1,6 KB/s, solo del dueño de la bola); eventos por golpe'],
    ['rel (RTC)', 'JSON ordenado', 'hello2, reloj (tick2/tock2), mstart con cuenta atrás de 3 s, claim/ack por punto, resync del árbitro, pausa, hallv del salón, mend al terminar', 'Decenas de mensajes por partida; hello2 ronda los 150 B; resync ~15 campos'],
    ['Sala PeerJS', 'JSON fiable', 'Señalización SDP/ICE de la conexión v2, respaldo v1 a 30 Hz (~10 KB/s) y túnel de emergencia', 'Activo en arranque y degradación'],
    ['Voz (MediaConnection)', 'Audio P2P', 'Micrófono entre anfitrión e invitado', 'Opus, no cuantificado en el código (estimado 3-4 KB/s)'],
  ],
  [14, 18, 42, 26], { size: 16 }));
C.push(p('Dos detalles del transporte importan para el espectador. Los paquetes binarios están muy cuantizados (posiciones a medio milímetro en enteros de 16 bits, cuaterniones de tres componentes, c09b:168-174) y el sistema ya maneja contrapresión: si el buffer de envío supera los umbrales declarados se recorta la pose y los eventos antes de saturar (c09:1538-1541). Y el receptor ya sabe reconstruir la partida desde un flujo: el modo degradado v1 demuestra que con un simple stream JSON se ve el partido completo (applySync y applyBallStream, c09:643-833), que es exactamente lo que un espectador necesita.'));

C.push(h2('2.3 · Robustez actual (lo que el espectador hereda)'));
C.push(p('El watchdog de silencio unificado corta a los 12 segundos en v2 sana (60 s con pausa anunciada, 25 s durante reinicio de ICE) y solo el invitado renegocia ICE, con un máximo de dos intentos (c09:1394-1478). Si cae el anfitrión la partida muere para ambos y no hay migración de rol ni reenganche (la partida local contra CPU toma el relevo, c12:1525-1574). El espectador heredará este mismo patrón: corte por silencio, sin reconexión de partida en curso, y la posibilidad futura de promocionarlo a invitado si el jugador activo abandona (sección 6, mecánica de banquillo).'));

// ══ 3 · LA IDEA ══
C.push(h1('3 · La propuesta en una frase'));
C.push(p([{ t: 'Espectador como tercer par de solo lectura atendido por el anfitrión, con fan-out añadido en los tres puntos de salida existentes, flujo reducido y un mensaje nuevo de enganche a partida en curso. ', b: true }, { t: 'El espectador renderiza la partida en el motor 3D local alimentándose del mismo estado que ya viaja entre los jugadores; no hay streaming de vídeo, y por eso el coste se mide en kilobytes por segundo y no en los decenas de megabits que costaría retransmitir imagen.' }]));
C.push(...figura(430, 'Figura 1 · Topología actual (1:1 estricta), espectador pasivo como descarga del anfitrión y espectador con influencia por votos de baja tasa filtrados por el anfitrión.'));

// ══ 4 · DISEÑO S1 ══
C.push(h1('4 · Diseño del espectador pasivo (S1)'));
C.push(p('Siete cambios concretos, todos localizados en la capa de red existente sin tocar la física ni la FSM del duelo. Se listan con su punto exacto de anclaje en el código.'));
C.push(vineta([{ t: 'Tercer rol. ', b: true }, { t: 'Ampliar role a host | guest | spec (hoy solo hay dos, c09:9, 221, 239) y añadirlo al saludo hello2. El espectador instancia NetClock como no-anfitrión (c09:984) y no participa en claim/ack ni emite resync.' }]));
C.push(vineta([{ t: 'Guardia de sala con lista de público. ', b: true }, { t: 'La guardia que hoy cierra la conexión entrante si hay otra viva (c09:269-275) pasa a distinguir: par de juego si no hay, espectador si el entrante anuncia rol spec; los espectadores viven en una lista specConns con tope configurable (4 por defecto, 6 máximo).' }]));
C.push(vineta([{ t: 'Fan-out en los tres puntos de salida. ', b: true }, { t: 'Tras el envío al invitado, _fastSend (c09:1600), sendRel (c09:2520) y send (c09:437) repiten hacia specConns. El orden importa: primero el duelo, después el público, y cada espectador con su propio control de bufferedAmount para que un espectador lento nunca retrase al invitado (el patrón de contrapresión ya existe, c09:1538-1541).' }]));
C.push(vineta([{ t: 'Flujo reducido para el público. ', b: true }, { t: 'Pose a 15 Hz y SNAP a 10 Hz (el receptor ya interpola con un jitter buffer de 40-220 ms, c09b:504-511), eventos HIT/HANDOFF todos y control rel completo salvo la ráfaga de reloj. Coste estimado: ~2,5 KB/s por espectador con la pose del invitado retransmitida.' }]));
C.push(vineta([{ t: 'Enganche a partida en curso. ', b: true }, { t: 'Mensaje rel nuevo spec-snap que reutiliza los ~15 campos del resync del árbitro (c09:2055-2086) más el estado de la bola (pos, vel, spin, shot); se envía al unirse y luego como ancla cada 5 segundos. Hoy no existe forma de entrar a mitad de partida (el invitado siempre empieza 0-0 tras mstart, c12:1443-1499), y este mensaje lo resuelve para el espectador sin tocar el flujo del duelo.' }]));
C.push(vineta([{ t: 'Espejo por emisor. ', b: true }, { t: 'La pose viaja ya espejada 180° por el emisor (c09:77-103, 1751-1760) y el receptor actual asume un único rival (c09:1779). El anfitrión retransmite la pose del invitado que ya decodifica (c09:1806-1821) añadiendo un byte de origen, y el espectador aplica el despeje de espejo por emisor.' }]));
C.push(vineta([{ t: 'Descubrimiento. ', b: true }, { t: 'El listado público de salas (c09c:312-315) y las invitaciones (c09c:257-290) son los puntos naturales para un botón VER; la presencia ya publica campos de sala (c09c:124-135) donde marcar que la sala admite público.' }]));
C.push(p('El HUD del espectador puede empezar siendo mínimo: cámara libre orbitando la cancha (el cliente ya sabe renderizar una sala completa — el invitado lo hace hoy), marcador y nombre de los dos jugadores, y un indicador EN DIRECTO con el retardo propio medido por el eco NTP que ya viaja en cada cabecera de paquete (c09b:350-368).'));

// ══ 5 · LATENCIA ══
C.push(h1('5 · ¿Introduce latencia? Análisis por ruta'));
C.push(p('La pregunta correcta no es si el espectador añade milisegundos al duelo (no los añade si el diseño respeta dos condiciones), sino qué recursos del anfitrión compite por compartir. La tabla separa lo que se toca de lo que no.'));
C.push(tabla(
  ['Ruta', '¿La toca el espectador?', 'Detalle'],
  [
    ['Entrada del duelo (fast → _onFast → _applyFastEv)', 'NO', 'Solo-descarga: el espectador no envía nada por el canal fast; el receptor del duelo no cambia'],
    ['Salida del duelo (pose/SNAP hacia el invitado)', 'NO, si el orden es duelo primero', 'El fan-out se ejecuta DESPUÉS del send hacia el invitado; un espectador lento solo llena su propio buffer (control por conexiones separadas)'],
    ['Canal rel (control JSON)', 'Solo lectura de copias', 'El público recibe copia; sus votos entran por rel agregados (1-2 Hz), jamás por fast'],
    ['Subida del anfitrión', 'SÍ, es el recurso compartido', '~5 KB/s por espectador a flujo completo; ~2,5 KB/s con flujo reducido; cap de 4-6 espectadores → menos de 15 KB/s añadidos'],
    ['CPU del anfitrión (Quest)', 'SÍ, por conexiones extra', 'Cada espectador es una RTCPeerConnection propia (RAM y llamadas send() por frame); el fan-out debe medirse y el cap proteger'],
    ['Nube de señalización PeerJS', 'Igual que hoy', 'Una conexión de señalización por espectador; riesgo heredado, no nuevo'],
  ],
  [30, 20, 50], { size: 16 }));
C.push(p([{ t: 'Con números: el anfitrión emite hoy hacia el invitado unos 5-7 KB/s (pose 3,1 + SNAP ≤1,6 + eventos y control esporádicos, más la voz estimada). Con cuatro espectadores de flujo reducido el total queda por debajo de 20 KB/s, unos 160 kilobits por segundo, trivial incluso para una conexión móvil modesta. ' }, { t: 'La conclusión honesta: con flujo reducido y cap de público, el modo espectador no añade latencia perceptible al duelo; sin esas dos protecciones y con público masivo, la saturación de subida del anfitrión SÍ degradaría el duelo — por eso el cap no es una limitación cosmética sino parte del diseño.' }]));
C.push(p('La percepción del espectador, por su parte, tendrá un retardo natural de medio segundo a segundo: RTT más el jitter buffer de interpolación (40-220 ms, c09b:504-511) más el enganche de flujo reducido. Para un espectador es correcto e incluso conveniente (evita el espionaje táctico en tiempo real); el HUD debe mostrar ese retardo medido en lugar de prometer directo absoluto.'));

// ══ 6 · INFLUENCIA ══
C.push(h1('6 · Participación e influencia del público'));
C.push(p('Influir no exige tocar la física: cuanto más cerca del resultado, más protections exige. El catálogo se ordena en cuatro niveles por riesgo competitivo; los niveles 0 y 1 son seguros en cualquier modo, y el nivel 3 queda reservado a modos casuales. Todos los votos del público entran como mensajes rel de baja frecuencia, se agregan en el anfitrión y llegan al duelo como un mensaje normal del anfitrión — el invitado nunca recibe nada directamente del público, así que no existe camino de fraude hacia el segundo jugador.'));
C.push(tabla(
  ['Nivel', 'Mecánica', 'Qué pasa', 'Gancho existente', 'Modos'],
  [
    ['0 · Cosmético local', 'Cámaras alternativas, repetición a cámara lenta propia, panel de estadísticas', 'Render y UI solo en el cliente del espectador, cero mensajes', 'El cliente ya renderiza la sala y la partida completa', 'Todos'],
    ['1 · Ambiente compartido', 'Ovómetro colectivo: aplausos que suben el cántico del megáfono y encienden las luces del salón en los puntos', 'Un mensaje crowd agregado 1-2 Hz filtrado por el anfitrión; efecto audiovisual para los tres', 'Sistema de voz megáfono y props emisivos por variante ya existen (c08)', 'Todos'],
    ['2 · Ritmo sin resultado', 'Votar el salón para el próximo partido; tiempo muerto colectivo (1 por set); repetición compartida', 'Voto mayoritario que el anfitrión aplica con los eventos existentes', 'hallv ya cambia el salón en vivo (c12:8033); pause/resume ya existe (c09:997)', 'Todos'],
    ['3 · Gameplay canalizado', 'El público vota el siguiente poder de Duelos Locos; ovómetro que da un micro-ajuste sutil al saque; banquillo: un espectador sustituye al invitado si abandona', 'Voto mayoritario con rate-limit (1 voto por espectador y 5 s); el anfitrión aplica y el duelo recibe el resultado', 'Sistema de poderes pow ya viaja por rel (c09:539); mend con abandono ya existe (c09:2512)', 'Solo casuales'],
  ],
  [16, 26, 28, 20, 10], { size: 16 }));
C.push(h2('6.1 · Guardarraíles de integridad (ELO)'));
C.push(p([{ t: 'El ELO del juego se registra localmente en cada extremo con paridad simétrica honesta (c09:749-758) y se liquida al terminar vía mend (c12:20668). Tres reglas protegen esa honestidad. Primera: el nivel 3 se activa solo en modos casuales — los modos ya viajan en mstart.md (c09:1366-1371), así que la regla es un filtro del anfitrión, no código nuevo de sincronización. Segunda: el árbitro de puntos es intocable — claim/ack y resync (c09:818-826, 2055-2086) no aceptan puntos del público bajo ningún modo. Tercera: toda influencia llega al duelo como mensaje del anfitrión tras agregación y rate-limit; ni el invitado ni la FSM conocen a los espectadores. ' }, { t: 'Con esas tres reglas, el público puede cambiar el ambiente, el ritmo y hasta los poderes de un casual, pero jamás puede fabricar un punto en una partida clasificada.', b: true }]));
C.push(p('La mecánica de banquillo merece mención aparte porque cierra una carencia real: hoy si el invitado abandona no hay reenganche ni migración de anfitrión (sección 2.3). Con el flujo spec-snap ya resuelto para el enganche, promocionar a un espectador a invitado es reutilizar ese mismo mensaje para transferirle el estado y cambiarle el rol — la única pieza nueva sería el apretón de manos de promoción y la renegociación de ICE que ya sabe hacer el lado invitado (c09:1455-1478).'));

// ══ 7 · PLAN ══
C.push(h1('7 · Plan de implementación por fases'));
C.push(tabla(
  ['Fase', 'Alcance', 'Ficheros y puntos de anclaje', 'Esfuerzo'],
  [
    ['F1 · Un espectador pasivo', 'Rol spec, guardia con lista, fan-out completo, spec-snap, HUD mínimo con cámara libre y EN DIRECTO', 'c09 (roles c09:9/221/239, guardia c09:269-275, fan-out c09:437/1600/2520, entrada c09:1779/1191), c12 (cámara y HUD)', 'Media'],
    ['F2 · Público múltiple y descubrimiento', 'Cap 4-6 espectadores, flujo reducido, byte de origen para el espejo, botón VER en salas públicas', 'c09 (contrapresión por conexión c09:1538), c09c (presencia c09c:124-135, listado c09c:312-315)', 'Media'],
    ['F3 · Reacciones (niveles 0-1)', 'Ovómetro, cánticos, luces de salón, confeti; panel de estadísticas del espectador', 'c08 (props emisivos y salas), c12 (HUD y audio megáfono), mensaje crowd nuevo en c09 rel', 'Media'],
    ['F4 · Ritmo (nivel 2)', 'Voto de salón para el próximo partido, tiempo muerto colectivo, repetición compartida', 'c12 (hallv c12:8033, pause c09:997), UI de votación', 'Baja-Media'],
    ['F5 · Influencia (nivel 3) y banquillo', 'Voto de poderes en casuales, micro-ajuste de ovómetro, promoción espectador a invitado', 'c09 (pow c09:539, mend c09:2512, promoción con ICE del invitado c09:1455), c12 (Duelos Locos)', 'Alta'],
  ],
  [18, 30, 42, 10], { size: 16 }));
C.push(p('Cada fase es jugable por sí misma y ninguna reescribe la anterior: F1 es el 80 por ciento del valor percibido con el 40 por ciento del esfuerzo, y las siguientes son mecánicas añadidas sobre el mismo conducto. La métrica que decide pasar de fase es la salud del duelo con público activo: retardo del invitado y pérdida de paquetes fast medidos por el eco NTP que ya viaja en cada paquete (c09b:350-368), visibles en el netInfo existente (c09:2467-2485).'));

// ══ 8 · RIESGOS ══
C.push(h1('8 · Riesgos y mitigaciones'));
C.push(tabla(
  ['Riesgo', 'Escenario', 'Mitigación propuesta'],
  [
    ['Saturación de subida del anfitrión', 'Público masivo o espectadores en conexiones lentas que no drenan', 'Cap de 4-6 espectadores, flujo reducido, contrapresión por conexión independiente (patrón c09:1538-1541), expulsión del espectador lento'],
    ['CPU del anfitrión en Quest', 'Varias RTCPeerConnection + fan-out en el frame de render', 'Fan-out fuera del frame crítico, medición con netInfo (c09:2467), cap como protección, valorar DC dedicado de difusión interna'],
    ['Votos fraudulentos', 'Un cliente inunda de votos para influir en un casual', 'Rate-limit por espectador, agregación solo en el anfitrión, y en clasificadas el filtro nivel-3 desactivado por mstart.md'],
    ['Integridad del ELO', 'Presión social para que el público decida puntos', 'Árbitro intocable (claim/ack y resync solo entre jugadores); mend sin participación del público'],
    ['Privacidad', 'Espectadores escuchando la voz del duelo', 'La voz es MediaConnection 1:1 y no se retransmite al público por defecto; el anfitrión decidiría una retransmisión explícita'],
    ['Espectadores zombis', 'Conexiones medio muertas consumiendo fan-out', 'Mismo watchdog de silencio del duelo (12 s, c09:1394) aplicado a specConns con expulsión automática'],
    ['Dependencia de la nube PeerJS', 'Caída de la señalización pública impide nuevos espectadores', 'Riesgo heredado del diseño actual (ya es así para el duelo); las partidas en curso no se ven afectadas'],
  ],
  [22, 32, 46], { size: 16 }));

// ══ 9 · CONCLUSIÓN ══
C.push(h1('9 · Conclusión'));
C.push(p('El modo espectador es viable en el juego tal como está construido: la arquitectura par-a-par con autoridad compartida ya produce los streams que un espectador necesita, las rutas de render de partida completa existen (el invitado las usa hoy) y el coste por espectador se mide en kilobytes por segundo porque el espectador recibe estado, no vídeo. La latencia del duelo queda intacta bajo dos condiciones de diseño — descarga pura con fan-out posterior al envío del duelo, y cap de público con flujo reducido — que son parte de la propuesta, no extras opcionales. Y la participación del público es un gradiente controlable: desde reacciones que solo cambian el ambiente hasta votos que canalizan los poderes de los modos casuales, siempre con el anfitrión como único agregador y con el árbitro de puntos blindado, que es lo que mantiene honesto el ELO.'));
C.push(nota('Propuesta elaborada el 22 de noviembre de 2026 sobre el análisis del código fuente V3.6.209-SDK6 (c09_red_netlink.js, c09b_red_nucleo.js, c09c_red_social.js, c12_pingponggame.js). Las cifras de tráfico proceden de las constantes del código (POSE_HZ, SNAP_HZ, tamaños de paquete y umbrales de contrapresión); la voz se marca como estimación porque el código no cuantifica su bitrate. Las citas fichero:línea referencian la versión analizada.'));

module.exports = C;
