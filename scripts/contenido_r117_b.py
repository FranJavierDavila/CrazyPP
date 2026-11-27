# -*- coding: utf-8 -*-
"""contenido_r117_b.py — capítulos 4-7 del guion de experiencia del espectador."""

BLOQUES_B = [

# ══════════════ CAPÍTULO 4 ══════════════
('h1', '4 · El espejo: cómo te ven los jugadores'),
('p', 'La pregunta complementaria es qué percibe el jugador de la mesa. La respuesta de diseño es deliberada: los jugadores no ven avatares articulados de cada espectador. Retransmitir las poses del público significaría multiplicar el tráfico del anfitrión y exponer movimientos corporales privados de gente que no ha dado su consentimiento para eso; además cargaría el render de la Quest del anfitrión. En su lugar, el público se representa de forma agregada: las siluetas del graderío se llenan según el contador de espectadores conectados y se animan con el ovómetro (se incorporan, aplauden, agitan el ambiente). Es exactamente la diferencia entre un estadio con público y un estadio con personas filmadas una a una.'),
('p', 'La otra mitad del espejo son las señales discretas hacia la mesa: la grada siempre va un latido detrás del juego (el retardo de 0,5 a 1 s de la vista del espectador), y los efectos del público se aplican entre puntos, nunca durante el vuelo de la bola. El jugador siente reacción, no telepatía: la ovación llega justo cuando el punto ya está muerto, igual que en un pabellón real. La tabla siguiente mapea cada acción del espectador con lo que percibe el jugador y el canal técnico que lo transporta.'),
('tabla', {
    'title': 'Mapeo acción del espectador → percepción del jugador → canal',
    'head': ['Acción del espectador', 'Lo que percibe el jugador', 'Canal'],
    'ratios': [0.32, 0.44, 0.24],
    'size': 8.8,
    'rows': [
        ['Conectarse a la sala', 'La grada se llena de siluetas; banner EN DIRECTO · N (desactivable)', 'Mensaje crowd por rel'],
        ['Mantener el aplauso', 'Ovómetro sube; a umbral: cánticos sintéticos, luces y confeti entre puntos', 'Crowd agregado a 1-2 Hz'],
        ['Votar el tiempo muerto', 'Cartel La grada pide tiempo muerto; el anfitrión acepta o ignora', 'Voto rel agregado'],
        ['Votar el salón del próximo', 'Al terminar el partido, la variante cambia a la más votada (hallv)', 'Voto rel agregado'],
        ['Votar poderes (solo casual)', 'La siguiente mano de poderes llega elegida por la grada', 'Voto rel rate-limitado sobre pow'],
        ['Usar el banquillo', 'Nueva persona en la mesa: el flujo habitual de emparejamiento', 'Renegociación ICE del invitado'],
        ['Lo que nunca ocurre', 'La voz del duelo no sale de la mesa; la grada no tiene voz; nada se aplica durante el rally', 'Decisión de diseño (privacidad y juego)'],
    ],
}),

# ══════════════ CAPÍTULO 5 ══════════════
('h1', '5 · Lo que el espectador no puede hacer (y por qué)'),
('p', 'Las dinámicas nuevas solo se entienden con su frontera visible. Cada límite siguiente responde a una única razón (privacidad, integridad o coste) y está en el protocolo, no solo en la interfaz: el anfitrión y el duelo jamás reciben del espectador nada que no haya pasado por el filtro de agregación del canal de control.'),
('v', 'No puede hablar por voz: la voz es un canal 1:1 entre anfitrión e invitado y no se retransmite; el público expresa con el medidor, no con el micrófono.'),
('v', 'No puede emitir sonidos dirigidos a un jugador concreto: todo lo que produce es ambiente agregado; eso elimina de raíz el acoso y el tilt dirigido.'),
('v', 'No puede ver la mano de poderes pendiente de los jugadores ni ningún dato que no sea ya público del estado de la partida: privacidad de decisión.'),
('v', 'No puede pisar la superficie de juego ni colocarse en la línea de saque: su locomoción termina en el perímetro de la mesa.'),
('v', 'No puede tocar la bola, el marcador ni el árbitro de puntos: el claim y el ack son de los jugadores; la grada no fabrica puntos, jamás en clasificadas.'),
('v', 'No puede entrar a mirar salas privadas: solo salas públicas con insignia EN DIRECTO o salas a las que el anfitrión le invita.'),

# ══════════════ CAPÍTULO 6 ══════════════
('h1', '6 · Sensaciones clave: por qué se siente distinto'),
('p', 'Condensado en tres sensaciones. La primera es la sala habitada: el jugador que entrena solo tiene grada si la busca, el rally largo tiene ovación y el torneo tiene ambiente, y todo eso ocurre sin que la partida se enter en su mecánica. La segunda es la progresión del espectador: mirar sin compromiso, reaccionar con un gesto, votar entre puntos y, en casuales, sentarse por el banquillo; nadie exige el siguiente paso, pero existe. La tercera es la simetría protegida: el ambiente es opt-in por jugador, los efectos son entre puntos y nunca deciden un marcador clasificado.'),
('p', 'Lo que no cambia es tan importante como lo que cambia: el duelo, su física, su máquina de estados, la voz entre jugadores y el ritmo del rally quedan intactos; el ELO se liquida fuera del alcance de la grada; y la sala sigue muriendo con su anfitrión (el modo espectador no introduce migración). La experiencia nueva se construye encima del sistema existente, no al lado de él.'),

# ══════════════ CAPÍTULO 7 ══════════════
('h1', '7 · Elecciones de diseño recomendadas'),
('p', 'Las preguntas abiertas de esta capa de experiencia tienen una respuesta recomendada cada una; se dejan explicitadas porque son las decisiones que conviene revisar tras el primer test con usuarios reales.'),
('tabla', {
    'title': 'Preguntas abiertas de experiencia y opción recomendada',
    'head': ['Pregunta abierta', 'Opción recomendada', 'Por qué'],
    'ratios': [0.34, 0.30, 0.36],
    'size': 8.8,
    'rows': [
        ['¿Avatares individuales del público o grada agregada?', 'Grada agregada', 'Coste de retransmisión, privacidad de los movimientos y carga de render en la Quest'],
        ['¿Cámara del jugador inmersiva o ventana flotante?', 'Ventana por defecto, toma opcional', 'Confort en VR: la vista por ojos ajenos mareo a parte del público'],
        ['¿Voz del público en la sala?', 'Nunca por defecto; si algún día existe, solo megáfono moderado por el anfitrión', 'La voz es 1:1 y privada; el ambiente sintético ya cubre la expresión'],
        ['¿Puede el espectador elegir sala antes de entrar?', 'Sí: miniatura con marcador en directo en el listado', 'Deriva del estado que el descubrimiento ya publica; reduce entradas erróneas'],
        ['¿Aparece el espectador en el historial del partido?', 'Solo como cifra agregada (espectadores máximos)', 'Preserva la privacidad de quién mira y mantiene el historial comparable'],
    ],
}),
('nota', 'Base técnica compartida con el análisis anterior: descarga de estado por las rutas _onFast/_onRel existentes, enganche spec-snap para partidas en curso, contrapresión por conexión (c09:1538-1541), eco NTP para el retardo mostrado en el HUD, watchdog de 12 s aplicado a la lista de espectadores y voz MediaConnection 1:1 sin retransmitir. Las citas fichero:línea corresponden a V3.6.209-SDK6.'),
]
