# -*- coding: utf-8 -*-
"""contenido_r117_a.py — capítulos 1-3 del guion de experiencia del espectador."""

BLOQUES_A = [

# ══════════════ CAPÍTULO 1 ══════════════
('h1', '1 · La llegada: los primeros diez segundos'),
('p', 'La experiencia empieza antes de la sala. En el listado de salas públicas, las partidas activas muestran una insignia EN DIRECTO con el número de espectadores conectados y el marcador actual (el descubrimiento ya publica el estado de cada sala, así que la insignia es lectura directa). El espectador toca VER y entra; el anfitrión, además, puede invitar desde la sala a alguien de su historial con el gesto que ya usa para retar. No hay lobby intermedio ni pantalla de configuración obligatoria: la entrada debe durar menos que abrir la puerta de un bar.'),
('p', 'Al entrar, el mensaje de enganche a partida en curso (spec-snap) entrega todo el estado actual: marcador, modo, variante de salón, posición de la bola y poses de ambos jugadores. En uno o dos segundos el espectador está dentro, sentado en la grada del salón que se está jugando, viendo el siguiente punto. El salón que ve es el render completo que su cliente ya sabe hacer (el invitado renderiza hoy la sala del anfitrión con sus luces y sus props), de modo que entrar a ver no exige contenido nuevo: exige solo una silla.'),
('v', 'HUD mínimo en el visor: insignia EN DIRECTO, retardo medido de la vista (por ejemplo +0,8 s, medido con el eco NTP que ya viaja en las cabeceras), contador de espectadores y un aviso breve: modo espectador: puedes mirar, aplaudir y votar.'),
('v', 'Nada de sonido de voz al entrar: la voz del duelo es un canal 1:1 entre jugadores y no se retransmite al público por defecto; lo primero que se oye es el ambiente sintético del salón, a volumen bajo.'),

# ══════════════ CAPÍTULO 2 ══════════════
('h1', '2 · La sala desde dentro: primera persona, no una cámara estática'),
('p', 'La respuesta directa a la pregunta es: por defecto, primera persona en la grada. El espectador no es un ojo flotante ni una cámara fija de televisión: es un punto de vista humano colocado en un asiento del graderío del salón actual. Desde ahí puede girar la cabeza y mirar a cada jugador, seguir la bola moviendo el cuello como seguiría una pelota real, inclinarse hacia la mesa o echarse atrás. La locomoción está limitada al perímetro: puede levantarse y rodear la mesa hasta el límite punteado del mapa, pero nunca pisar la superficie de juego ni colocarse en la línea de saque del que sirve.'),
('p', 'La razón de esta elección es de presencia, no de estética. En realidad virtual, una cámara estática desorienta: el cuerpo espera poder moverse y la cabeza pide confirmar lo que el ojo intuye; una cámara flotante sin cuerpo rompe la sensación de estar en una sala. Un asiento en la grada entrega presencia sin tocar el juego, y su coste técnico es mínimo: el cliente del espectador ya renderiza la sala completa; solo se añaden límites de movimiento locales y el asiento por defecto. El mapa siguiente resume la sala, la grada, el límite de locomoción y los cuatro presets de cámara.'),
('fig', {'path': '/home/z/my-project/download/_thumbs_r115/fig_sala_r117.png',
         'caption': 'Figura 1 · Mapa superior de la sala: el espectador entra en primera persona a la grada (C1), con locomoción limitada al perímetro de la mesa; los presets C2 a C4 son tomas alternativas conmutables, todas derivadas del estado que ya viaja.',
         'maxw': 470, 'maxh': 260}),
('p', 'Sobre ese asiento por defecto se ofrecen cuatro tomas, conmutables con fundido corto y viñeta de confort para no marear. Las cuatro se calculan localmente con el estado que ya llega: ninguna añade bytes ni pide nada al anfitrión. El preset activo se recuerda por sala, de modo que volver a VER una sala restablece la toma preferida.'),
('tabla', {
    'title': 'Presets de cámara del espectador: qué es cada toma, para quién y su coste',
    'head': ['Preset', 'Qué es', 'Para quién', 'Coste técnico'],
    'ratios': [0.17, 0.36, 0.25, 0.22],
    'size': 8.8,
    'rows': [
        ['C1 · Grada (por defecto)', 'Primera persona en el asiento, con locomoción limitada al perímetro de la mesa', 'El espectador social que quiere sentirse en la sala', 'Límites locales y asiento; 0 bytes extra'],
        ['C2 · TV lateral', 'Trípode virtual tipo retransmisión, con encuadre automático que sigue la bola', 'Quien quiere ver el punto completo sin girar la cabeza', 'Lógica de encuadre local sobre el SNAP'],
        ['C3 · Bola-cam', 'Seguimiento cercano de la bola en vuelo', 'Aprender el giro, el efecto y la altura del golpe', 'Interpolación del SNAP existente'],
        ['C4 · Ojos del jugador', 'Vista desde la cabeza del avatar del anfitrión o del invitado', 'Estudiar la técnica y la preparación del golpe', 'La pose del avatar ya viaja; es matemática de cámara; se ofrece como ventana flotante'],
    ],
}),
('p', 'La toma del jugador (C4) merece una precisión de comodidad: mirar por los ojos de otro cuerpo en primera persona provoca mareo en parte del público cuando la cabeza gira rápido, así que se ofrece por defecto como ventana flotante (un monitor virtual sobre la mesa que muestra esa vista) y solo opcionalmente como toma controlada. Es la misma paleta que usan los modos espectador de otras disciplinas: la toma subjetiva es herramienta de estudio, no la vista por defecto.'),

# ══════════════ CAPÍTULO 3 ══════════════
('h1', '3 · El bucle de un minuto: qué puede hacer dentro del juego'),
('p', 'El diseño de interacción evita todo gesto que aparte la atención de la mesa: nada de menús flotantes sobre el punto, nada de apuntar con precisión. Todas las acciones se hacen con un pulgar, sin quitar los ojos del rally. La cronología siguiente describe una sesión típica de un minuto y medio con sus momentos y su efecto en la sala; cada fila es una acción verificable del catálogo del análisis anterior.'),
('tabla', {
    'title': 'Cronología de una sesión corta de espectador',
    'head': ['Momento', 'Qué haces', 'Qué pasa en la sala'],
    'ratios': [0.16, 0.42, 0.42],
    'size': 8.8,
    'rows': [
        ['t+0 s', 'Apareces en la grada; el HUD muestra EN DIRECTO y el retardo', 'La grada del salón tiene una silueta más; los jugadores ven el contador subir'],
        ['t+10 s', 'Eliges toma (grada, TV, bola-cam o ventana del jugador)', 'Nada cambia para nadie: es tu vista local'],
        ['t+30 s', 'Mantienes el aplauso tras un buen rally', 'El ovómetro colectivo sube; a umbral, cánticos sintéticos y luces del salón'],
        ['entre puntos', 'Predices quién gana el punto (pulgar izquierda o derecha)', 'Nada visible para los jugadores; alimenta tu marca personal'],
        ['minuto 1', 'Votas el salón del próximo partido entre tres variantes', 'Al acabar el partido, el salón cambia al más votado (el anfitrión confirma)'],
        ['minuto 2', 'La mayoría de la grada pide el tiempo muerto del set', 'Los jugadores ven el cartel; el anfitrión acepta o ignora (pause/resume)'],
        ['fin de set', 'El ovómetro estaba alto: confeti y ovación del salón', 'Efecto estético y simétrico; nadie gana nada por ello'],
        ['si un jugador abandona', 'Te sientas: el banquillo te promociona a invitado', 'Renegociación de conexión; flujo de emparejamiento habitual'],
    ],
}),
('p', 'Tres detalles hacen que el bucle se sienta vivo en vez de spam. Primero, el aplauso es un gesto mantenido que suma a un medidor colectivo: nunca suena tu aplauso individual (privacidad y anti-ruido), suena el salón cuando el medidor cruza un umbral. Segundo, la repetición personal permite rebobinar los últimos segundos a cámara lenta en cualquier momento, porque es tu buffer local: estudiar un saque no interrumpe nada ni avisa a nadie. Tercero, los votos tienen cadencia (un voto por espectador cada cinco segundos) y se agregan en el anfitrión, con lo que el ritmo de la sala nunca depende de un solo cliente.'),
]
