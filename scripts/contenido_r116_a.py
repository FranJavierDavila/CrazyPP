# -*- coding: utf-8 -*-
"""contenido_r116_a.py — capítulos 1-3 del análisis de modo espectador."""

BLOQUES_A = [

# ══════════════ CAPÍTULO 1 ══════════════
('h1', '1 · Las tres preguntas, contestadas'),
('p', 'Este documento responde con detalle a la pregunta que motiva la propuesta: si el modo espectador que ya se analizó en la propuesta r115 incorpora dinámicas reales de participación, si introduce latencia o dificulta el juego, y si constituye un motivo diferenciador capaz de resultar novedoso. Todo el análisis se apoya en el código fuente real de la capa de red (c09_red_netlink, c09b_red_nucleo, c09c_red_social y c12_pingponggame), cuyas constantes y rutas se citan por fichero y línea. Donde aparece una estimación (por ejemplo, el bitrate de la voz) se marca como tal; donde el dato procede del código, se presenta el valor medido de sus constantes.'),
('callouts', [
    ('0 ms', 'latencia añadida al camino de entrada del duelo'),
    ('2,5 KB/s', 'coste de red por espectador con flujo reducido'),
    ('4-6', 'espectadores sostenibles por sala sin relay'),
    ('0,5-1 s', 'retraso natural de la vista del espectador (correcto)'),
]),

('h2', '1.1 · ¿Qué dinámicas incorporarían los espectadores?'),
('p', 'El catálogo de dinámicas se ordena en cuatro niveles de implicación creciente, pensados para que el espectador tenga un recorrido: ver la partida, reaccionar a ella, influir en su ambiente y ritmo, y en los modos casuales llegar a influir en el juego mismo. Los niveles 0 y 1 no tocan en absoluto la partida; el nivel 2 toca su ritmo sin tocar su resultado; el nivel 3 solo existe en modos casuales y pasa siempre por el filtro del anfitrión. La sección 2 desarrolla cada mecánica con su comportamiento jugable, su canal técnico, su coste y su riesgo; aquí queda el mapa completo.'),
('tabla', {
    'title': 'Los cuatro niveles de participación del público (resumen; detalle en la sección 2)',
    'head': ['Nivel', 'Dinámicas', '¿Toca el resultado?', 'Coste de red'],
    'ratios': [0.14, 0.42, 0.20, 0.24],
    'size': 9,
    'rows': [
        ['0 · Observar', 'Cámara libre y director automático, repetición a cámara lenta, estadísticas en vivo, predicciones locales', 'No (todo es local al espectador)', 'Solo descarga del estado (~2,5 KB/s)'],
        ['1 · Ambiente', 'Ovómetro colectivo con cánticos sintéticos, luces y props del salón reaccionando, confeti en los puntos', 'No (audio y visuales)', '1 mensaje rel agregado a 1-2 Hz'],
        ['2 · Ritmo', 'Votar el salón del próximo partido, tiempo muerto colectivo (uno por set), repetición comentada', 'No (pausa y vestuario, nunca puntos)', 'Votos rel agregados, rate-limit 1 cada 5 s'],
        ['3 · Influencia', 'Voto mayoritario del siguiente poder en Duelos Locos, micro-ajuste simétrico del saque, banquillo para sustituir al invitado que abandona', 'Solo en modos casuales, nunca en clasificadas', 'Mismo canal rel; el anfitrión aplica y el duelo recibe el resultado'],
    ],
}),

('h2', '1.2 · ¿Introduce latencia, o lo dificulta?'),
('p', 'No introduce latencia en el duelo, y la razón es arquitectónica, no de optimización: el espectador consume estado y no produce datos de juego. Su tráfico es de solo descarga y no toca el camino de entrada del duelo (el canal fast por el que el invitado recibe pose y bola). El único recurso compartido es la conexión de subida y la CPU del anfitrión, y ambas quedan acotadas por dos condiciones de diseño: el fan-out hacia el público se ejecuta después del envío del duelo (con control de buffer por conexión), y el público recibe un flujo reducido (pose a 15 Hz y bola a 10 Hz en lugar de 60 y 20-30) con un tope de 4 a 6 espectadores por sala. Con esas condiciones el anfitrión añade menos de 15 KB/s en total, un orden de magnitud por debajo del coste de la voz, y la latencia del duelo queda intacta.'),
('p', 'En cuanto a si lo dificulta, la pregunta admite tres lecturas y las tres tienen respuesta. Para la partida en sí, no: la física (c04) y la máquina de estados del duelo no reciben ni un cambio. Para los jugadores, solo en forma de ambiente opt-in: los efectos del público son sonido y luz entre puntos, desactivables por jugador. Para el desarrollo, la complejidad es media y muy localizada: los cambios viven en la capa de red (un tercer rol, la guardia de sala que admite espectadores, el fan-out en los tres puntos de salida existentes y un mensaje de enganche a partida en curso), mientras que el códec de paquetes se reutiliza tal cual. El capítulo 4 desglosa ese coste por componente.'),

('h2', '1.3 · ¿Es un diferenciador? ¿Puede resultar novedoso?'),
('p', 'Sí, por tres palancas combinadas que la sección 5 argumenta con el estado actual del género. Primera: la espectación nativa en el visor, renderizada desde el estado de la partida (kilobytes por segundo) y no desde un vídeo, algo que ni siquiera el referente del género ofrece hoy más allá de herramientas de streaming o de espectación en 2D desde PC; su propia comunidad pide desde 2021 poder sentarse en el sofá de otra sala para ver a jugadores hábiles. Segunda: la participación graduada con influencia real pero acotada, que convierte al espectador en un embudo de retención hacia el juego en vez de un espejo pasivo. Tercera: la integridad competitiva declarada, con el árbitro de puntos intocable y el ELO blindado, lo que permite hacer torneos con grada sin sospechas. La combinación de las tres es infrecuente en juegos de mesa virtual y, sobre todo, es barata de conseguir con esta arquitectura: el estado que el espectador necesita ya viaja entre los dos jugadores.'),

# ══════════════ CAPÍTULO 2 ══════════════
('h1', '2 · Dinámicas de espectador: el diseño jugable'),
('p', 'El principio de diseño que ordena todo el catálogo es que el espectador es un participante de datos bajos y emoción alta: consuma pocos kilobytes, pero participe. Cada dinámica se describe aquí en términos jugables (qué hace el espectador exactamente y qué perciben los jugadores), junto con su canal técnico y su riesgo. El recorrido de implicación es deliberado: primero observar sin compromiso, después reaccionar con un gesto, después votar, y solo en casuales llegar a tocar el juego. Este gradiente convierte la grada en un espacio con progresión propia, no en un anexo.'),

('h2', '2.1 · Dinámicas de observación (nivel 0, siempre disponibles)'),
('p', 'Son la base del modo y todo lo que necesitan los primeros espectadores. Ninguna envía un solo byte hacia la partida: son render y UI sobre el estado que ya llega. Cuatro dinámicas componen este nivel.'),
('v', '<b>Cámara libre y cámara director.</b> El espectador orbita la cancha, se coloca junto a la red o adopta la vista televisiva clásica lateral. La cámara director es automática: el encuadre se elige según el estado de la bola que ya viaja en el SNAP, sin coste añadido. El cliente ya renderiza la sala completa (el invitado lo hace hoy), de modo que la cámara libre es trabajo de UI, no de red.'),
('v', '<b>Repetición a cámara lenta.</b> El espectador guarda localmente los últimos segundos de estado y puede rebobinar a voluntad. Como consume su propio buffer, no afecta a nadie más; es la dinámica más valiosa para aprender de rivales buenos y la más barata de implementar.'),
('v', '<b>Panel de estadísticas en vivo.</b> La velocidad de la bola se deriva del campo vel del SNAP (que ya viaja a 20-30 Hz), y el marcador, el rally y los modos llegan por claim, ack y resync. Con eso, velocidad de último golpe, longitud del intercambio actual y puntos ganados tras saque son paneles de lectura directa.'),
('v', '<b>Predicción sin impacto.</b> Antes de cada punto, el espectador puede apostar quién lo gana, con una tabla personal de aciertos. Es puro UI local y sirve de ensayo de la interacción de voto que se usa en niveles superiores: se aprende el gesto sin riesgo alguno.'),

('h2', '2.2 · Dinámicas de ambiente compartido (nivel 1)'),
('p', 'Aquí el público deja de ser invisible: su energía se agrega en un ovómetro colectivo y se materializa en el salón. El espectador mantiene un aplauso (botón o gesto que no requiere soltar nada); cada gesto aporta al medidor de la grada, que se agrega en el anfitrión a 1-2 Hz y se difunde a todos como un mensaje crowd normal. Al superar umbrales, el cliente genera cánticos sintéticos del salón (la voz entre jugadores es 1:1 y privada y no se retransmite al público: el ambiente es audio generado por el propio cliente con el medidor como parámetro), las luces y props emisivos de la variante de salón actual suben de intensidad, y en cada punto la grada suelta confeti si el medidor estaba alto.'),
('p', 'La consecuencia jugable deseada es la del sofá del salón: los jugadores sienten grada cuando la hay, y los espectadores ven su gesto colectivo tener efecto visible en el mundo compartido. El coste es mínimo (un mensaje rel agregado) y el riesgo también, porque el efecto es simétrico: la ovación no favorece a nadie, solo eleva el ambiente. Los jugadores disponen de interruptores para silenciar cánticos o apagar confeti sin salir de la partida.'),

('h2', '2.3 · Dinámicas de ritmo (nivel 2)'),
('p', 'Estas dinámicas tocan el flujo de la partida, nunca su resultado. Tres mecanismos, todos apoyados en eventos que ya existen. El voto de salón permite a la grada elegir la variante del salón para el próximo partido: el evento hallv que hoy usa el anfitrión para cambiar de salón en vivo es exactamente el canal necesario. El tiempo muerto colectivo da a la grada un único tiempo muerto por set: si la mayoría lo activa, ambos jugadores ven la petición y el anfitrión decide aceptarla con el flujo pause/resume existente. La repetición comentada, opcional, sincroniza una cámara lenta entre puntos cuando la grada la pide por mayoría; es la más compleja de las tres y por eso se deja al final de la fase F4.'),

('h2', '2.4 · Dinámicas de influencia en juego (nivel 3, solo modos casuales)'),
('p', 'Es el nivel que convierte a la grada en protagonista, reservado a modos casuales porque sí toca el juego. El voto de poderes reutiliza el sistema de Duelos Locos: el poder que ya viaja por el canal rel (pow) pasa a ser elegido por la grada entre tres opciones, por mayoría simple con un voto por espectador cada cinco segundos; el anfitrión agrega, aplica y el duelo recibe el resultado como cualquier mensaje suyo. El empuje moral del ovómetro da a la ovación un efecto simétrico y sutil: si la grada ovaciona a un jugador al superar el umbral máximo, su siguiente saque sale con un 2 por ciento más de velocidad y un destello visual; ambos jugadores pueden recibirlo, así que la ventaja no es estructural. El banquillo resuelve de paso una carencia real: si el invitado abandona, el espectador con mejor marca de predicciones puede sentarse en su silla; el mensaje de enganche a partida en curso (spec-snap) es el mismo que usa la espectación, y la renegociación ICE del lado invitado ya existe. Por último, el MVP de la grada premia semanalmente, con cosmética, al espectador más activo de las salas públicas.'),

('h2', '2.5 · Tabla maestra de dinámicas'),
('p', 'La tabla siguiente condensa el catálogo completo con su canal, coste, efecto y riesgo. Todos los costes de red derivan de las constantes del código (POSE_HZ 60, SNAP_HZ 20-30, paquetes de 52-54 bytes) más los mensajes nuevos agregados; el detalle arquitectónico de cada canal está en el capítulo 3.'),
('tabla', {
    'title': 'Catálogo completo de dinámicas de espectador',
    'head': ['Dinámica', 'Qué hace el espectador', 'Canal y coste', 'Efecto en el duelo', 'Riesgo principal', 'Fase'],
    'ratios': [0.15, 0.25, 0.20, 0.17, 0.15, 0.08],
    'size': 8.2,
    'rows': [
        ['Cámara libre / director', 'Orbita la cancha o elige encuadre automático', 'Solo descarga del estado existente', 'Ninguno', 'Ninguno relevante', 'F1'],
        ['Repetición lenta local', 'Rebobina su propio buffer de estado', 'Local, 0 bytes extra', 'Ninguno', 'Ninguno', 'F1'],
        ['Estadísticas en vivo', 'Lee velocidad, rally y marcador', 'Deriva de SNAP y rel', 'Ninguno', 'Ninguno', 'F2'],
        ['Predicciones', 'Aposta el ganador del punto (UI)', 'Local, 0 bytes extra', 'Ninguno', 'Ninguno', 'F2'],
        ['Ovómetro', 'Mantiene aplauso; suma al medidor colectivo', '1 rel agregado a 1-2 Hz', 'Audio y luces del salón', 'Ruido; opt-out por jugador', 'F3'],
        ['Cánticos y confeti', 'Umbrales del ovómetro disparan ambiente', 'Mismo mensaje crowd', 'Estético, simétrico', 'Molestar; interruptores', 'F3'],
        ['Voto de salón', 'Elige la variante del próximo partido', 'Voto rel agregado', 'hallv al acabar el partido', 'Incluir en F4 tras F3', 'F4'],
        ['Tiempo muerto', 'Uno por set; mayoría lo pide', 'Voto rel agregado', 'pause/resume del anfitrión', 'Abuso; un solo uso por set', 'F4'],
        ['Voto de poderes', 'Elige entre 3 poderes (casuales)', 'Voto rel rate-limitado', 'pow existente (c09:539)', 'Fraude; agregación solo en anfitrión', 'F5'],
        ['Empuje moral', 'Ovación al máximo del ovómetro', 'Mismo mensaje crowd', '+2 % de velocidad en el saque siguiente (simétrico)', 'Desequilibrio; efecto sutil y revocable', 'F5'],
        ['Banquillo', 'Sustituye al invitado que abandona', 'spec-snap + promoción', 'Cambio de jugador', 'Renegociación ICE; prueba', 'F5'],
        ['MVP de la grada', 'Participa activamente en salas públicas', 'Métricas locales', 'Recompensa cosmética', 'Ninguno en el duelo', 'F5'],
    ],
}),

('h2', '2.6 · Las cinco reglas de diseño jugable'),
('p', 'Cinco reglas protegen la partida y hacen el catálogo coherente. No son accesorias: cada dinámica de la tabla las cumple o no entra.'),
('v', '<b>Efecto neutro o simétrico.</b> Ninguna dinámica decide un punto: el ambiente es simétrico, el ritmo no cambia el marcador y la influencia en juego solo existe en casuales. El árbitro de puntos (claim/ack y resync del anfitrión) no acepta decisiones de la grada bajo ningún modo.'),
('v', '<b>Nada durante el vuelo de la bola.</b> Los eventos de público se aplican entre puntos. En realidad virtual, un cambio visual o sonoro durante el rally altera la percepción del jugador; por eso el crowd se aplica con el balón muerto.'),
('v', '<b>Opt-out total por jugador.</b> Cada jugador puede silenciar cánticos, apagar confeti y desactivar el tiempo muerto colectivo sin salir de la partida; por defecto el ambiente llega activado a volumen bajo.'),
('v', '<b>Agregación solo en el anfitrión.</b> Los votos entran al anfitrión con rate-limit (un voto por espectador y cada 5 segundos); el invitado y la FSM del duelo jamás reciben nada directamente del público, con lo que no existe camino de fraude hacia el segundo jugador.'),
('v', '<b>Clasificadas en modo 0-2.</b> El nivel 3 se filtra por el modo que ya viaja en mstart.md (match, duelos o survival); en partidas clasificadas con ELO el filtro lo desactiva y el mend que liquida el ELO queda fuera del alcance de la grada.'),

# ══════════════ CAPÍTULO 3 ══════════════
('h1', '3 · Latencia y arquitectura: por qué el duelo no se entera'),
('h2', '3.1 · El camino del dato'),
('p', 'La figura siguiente resume el flujo completo con la notación del código. El anfitrión ya produce y codifica el estado del duelo (paquetes binarios de 52 y 54 bytes con pose del avatar, instantánea de bola y eventos); el fan-out propuesto se añade en los tres puntos de salida que ya existen (send, _fastSend y sendRel), y el espectador consume ese flujo con las mismas rutas de entrada que usa el invitado (_onFast y _onRel). La única corriente ascendente del público son votos agregados por el canal rel de control, a 1-2 Hz, que el anfitrión filtra y aplica.'),
('fig', {'path': '/home/z/my-project/download/_thumbs_r115/fig_pipeline_r116.png',
         'caption': 'Figura 1 · Pipeline del modo espectador sobre la arquitectura existente: descarga de estado para el público, retorno de votos por el canal de control, y el camino del duelo (izquierda a derecha, azul oscuro) sin cambios.',
         'maxw': 470, 'maxh': 240}),

('h2', '3.2 · Las dos condiciones que protegen al duelo'),
('p', 'Que el espectador no añada latencia al duelo no es una promesa sino el resultado de dos condiciones de diseño, ambas apoyadas en mecanismos que el código ya tiene. Primera: el orden de envío. El fan-out hacia los espectadores se ejecuta después del send hacia el invitado, y cada espectador dispone de su propio control de bufferedAmount con el patrón de contrapresión existente (que ya descarta pose y eventos cuando el buffer supera los umbrales declarados, c09:1538-1541): un espectador lento llena únicamente su propio buffer y jamás retrasa al invitado. Segunda: la separación de canales. Todo lo que el público produce (votos, reacciones) viaja por el canal rel de control JSON, ordenado y de baja frecuencia; el canal fast del duelo no recibe ni un paquete del público. Además, el invitado no ve a los espectadores: recibe del anfitrión, como siempre, mensajes normales suyos.'),
('p', 'Conviene ser preciso sobre el recurso que sí se comparte: la subida del anfitrión. Hoy el anfitrión emite hacia el invitado unos 4,7 KB/s de estado (pose a 60 Hz más instantáneas a 30 Hz más eventos esporádicos, más la voz estimada en 3-4 KB/s). El público de flujo reducido añade unos 2,5 KB/s por espectador; con el tope de 4 a 6 espectadores, el anfitrión queda por debajo de 15 KB/s añadidos, unos 120 kilobits por segundo: trivial incluso para una conexión móvil modesta. El peligro solo aparece si se desactiva el flujo reducido o se levanta el tope sin un relay; por eso el cap y la reducción son parte del diseño y no recortes opcionales.'),

('h2', '3.3 · Los números, medidos del código'),
('tabla', {
    'title': 'Coste de red por destino derivado de las constantes del código (la voz se marca como estimación)',
    'head': ['Flujo', 'Composición', 'Coste'],
    'ratios': [0.34, 0.46, 0.20],
    'size': 8.8,
    'rows': [
        ['Duelo (anfitrión → invitado)', 'Pose 52 B a 60 Hz + SNAP 54 B a 20-30 Hz + eventos HIT/HANDOFF esporádicos', '≈ 4,7 KB/s'],
        ['Espectador, flujo completo', 'Copia del flujo del anfitrión (pose + snap + eventos)', '≈ 5,0 KB/s'],
        ['Espectador completo + pose del invitado', 'El anfitrión retransmite además la pose del invitado que ya decodifica (byte de origen añadido)', '≈ 8-10 KB/s (estimación)'],
        ['Espectador, flujo reducido (propuesto)', 'Pose a 15 Hz + SNAP a 10 Hz + todos los eventos + rel', '≈ 2,5 KB/s'],
        ['Votos del público (retorno)', 'Mensajes rel agregados por el anfitrión', '1-2 Hz, < 0,2 KB/s'],
        ['Anfitrión total con 4 espectadores reducidos', 'Duelo + 4 × flujo reducido + votos', '< 15 KB/s añadidos'],
    ],
}),
('fig', {'path': '/home/z/my-project/download/_thumbs_r115/fig_ancho_banda_r116.png',
         'caption': 'Figura 2 · Coste de red por destino en KB/s. Los valores derivan de POSE_HZ, SNAP_HZ y los tamaños de paquete del código; la barra del espectador completo con pose del invitado es estimación (8-10 KB/s).',
         'maxw': 455, 'maxh': 205}),
('p', 'La lectura del gráfico es la clave del argumento completo: el espectador de flujo reducido cuesta menos de la mitad de lo que ya cuesta el propio duelo, y cuatro espectadores juntos cuestan menos que la voz que ya viaja hoy. La latencia del duelo, en consecuencia, no tiene de dónde salir: el canal del duelo no se comparte, el orden de envío protege al invitado y el ancho de banda sobra.'),

('h2', '3.4 · Lo que sí experimenta el espectador'),
('p', 'El espectador verá la partida con un retraso natural de entre medio segundo y un segundo: el retardo de red más el jitter buffer de interpolación del receptor (que el código dimensiona entre 40 y 220 ms según pérdida y jitter) más la holgura del flujo reducido a 15 Hz. Es el comportamiento correcto por dos razones. La primera es técnica: el buffer de interpolación es lo que permite renderizar suave con paquetes que llegan a saltos, y reducírselo al espectador solo le daría tirones. La segunda es jugable: ese retraso evita el espionaje táctico en tiempo real y reduce el efecto arena en partidas igualadas. El HUD del espectador debe mostrar ese retardo medido (el eco NTP que ya viaja en cada cabecera de paquete permite medirlo con precisión) en lugar de prometer directo absoluto.'),

('h2', '3.5 · Límites honestos'),
('p', 'Tres límites conviene declarar con la misma claridad que las ventajas. Primero, la escala: sin relay, la sala sostiene 4 a 6 espectadores cómodamente (cada uno es una RTCPeerConnection extra con su memoria y su procesado ICE en la Quest del anfitrión); gradas mayores exigen un componente nuevo (WebSocket persistente en el worker, que hoy solo expone HTTP para ICE, presencia e invitaciones), y es la pieza que justificaría el esfuerzo solo si la adopción lo pide. Segundo, la continuidad: no existe migración de anfitrión, la sala muere con su creador y los espectadores la verán caer como cae hoy el duelo; el banquillo de la fase F5 mitiga el caso del invitado que abandona, no el de la sala entera. Tercero, la dependencia heredada: la señalización pasa por la nube pública de PeerJS, igual que hoy para el duelo; el modo espectador no la empeora, pero tampoco la protege.'),
]
