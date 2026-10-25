#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · QA TOTAL (un comando, toda la cadena).
Encadena TODAS las capas de verificación del proyecto, de la más rápida a la
más lenta, y saca el marcador global. Descubre los QA de la versión actual
por nombre (qa_sup1_vNNN.py → el más alto), así que no hay que tocarlo en
cada release.

Capas:
  A. qa_version.py        — cadena de versión única (23 checks)
  B. test_fisica.mjs      — determinismo de la física (11 escenarios)
  C. qa_manifiestos.py    — schema + assets de los 5 campeonatos (29)
  D. qa_rendimiento.py    — presupuesto (tamaños/física/boot, 14)
  E. qa_sup1_vNNN.py      — el juego EN VIVO con el orbital cargado (~150)
  F. qa_imp2_vNNN.py      — reactor de impulso (~66)
  G. qa_escudo_vNNN.py    — escudo de pala (~54)
  H. qa_descargas_vNNN.py — hub + 4 ZIPs byte-exactos (~208)
  I. smoke_sdkN.py        — SDK + 5 módulos en cadena
  J. qa_telemetria.py     — telemetría anónima: catálogo, receptor, E2E (41)
  K. qa_hub_hints.py      — (POST-DEPLOY, --produccion) hints del hub en
                            producción contra el estado real del dueño (11)
  L. qa_champion_listo.py — (POST-DEPLOY, --produccion) estado champion de
                            los 5 campeonatos en producción (13)

Uso:
  python3 scripts/qa_todo.py                # TODO (A-J, pre-deploy)
  python3 scripts/qa_todo.py --rapido       # solo A-D (sin Playwright pesado)
  python3 scripts/qa_todo.py --produccion   # A-J + K/L contra PRODUCCIÓN
                                            # (tras el deploy: K/L exigen
                                            # que pages sirva la versión
                                            # de la FUENTE DE VERDAD)
Salida: marcador global. Exit 1 si CUALQUIER capa falla."""
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SCR = RAIZ / 'scripts'
TIMEOUT = {  # segundos por capa
    'qa_version.py': 120, 'test_fisica.mjs': 90, 'qa_manifiestos.py': 60,
    'qa_rendimiento.py': 300,
}

def ultimo(pat):
    cand = sorted(SCR.glob(pat))
    return cand[-1].name if cand else None

CAPAS = [
    ('A · versión única', 'qa_version.py'),
    ('B · física determinista', 'test_fisica.mjs'),
    ('C · manifiestos', 'qa_manifiestos.py'),
    ('D · presupuesto', 'qa_rendimiento.py'),
    ('E · juego en vivo (sup1)', ultimo('qa_sup1_v*.py')),
    ('F · reactor de impulso', 'qa_imp2_v351.py'),
    ('G · escudo de pala', 'qa_escudo_v350.py'),
    ('H · hub + ZIPs', ultimo('qa_descargas_v*.py')),
    ('I · smoke del SDK', ultimo('smoke_sdk*.py')),
    ('J · telemetría', 'qa_telemetria.py'),
    ('T · zonas entrenamiento', 'qa_train_zonas_v3619.py'),
    ('U · ayudas entrenamiento', 'qa_train_ayudas_v3621.py'),
    ('V · sonido del tren', 'qa_tren_audio_v3626.py'),
    ('W · salon del artista', 'qa_hall_salon_v3628.py'),
    ('X · sala del partido + mejor de 3', 'qa_partido_sala_v3629.py'),
    ('Y · hall sin pala ni bola', 'qa_hall_sin_pala_v3630.py'),
    ('Z · menú campeonatos + intro', 'qa_menu_intro_v3631.py'),
    # AC (qa_mega_norma_v3634) RETIRADA: verificaba la norma v3.6.34 (una
    # carga por rally, icono canvas, gatillo cualquiera). La sustituye AD
    # (v3635): SUPERPODER DE PALA con CARGAS ×3 — cada 11 golpes del rally
    # = +1 (tope ×3, distinto sustituye), icono DEL DUEÑO anclado al mango
    # con etiqueta ×N, voz TTS embebida y gatillo del mando LIBRE.
    # AD (qa_mega_cargas_v3635) y AE (qa_poderes_matriz_v3636) RETIRADAS:
    # la sustituye AF (v3637): SÚPER IMÁN (3.er poder, spec completa del
    # dueño: campo 8 s al punto dulce, topes 0,45/0,12/3/0,35/0,15, consumo
    # por impacto asistido, máx. 3) + flechas de la matriz como sprites
    # PROPIOS (disco+oro+pulso) + SÚPER EFECTO notorio (halo rojo en la
    # bola, anillo de bote, rival con error ×2 y piernas ×0,85) + toda la
    # norma de la matriz con 3 poderes y las 6 voces nativas.
    ('AF · superpoder imán (v3637)', 'qa_poderes_iman_v3637.py'),
    # AG (v3638): INMEDIATEZ del gatillo (redibujo diferido + textura
    # persistente + PRECALIENTE repartido) + halo HIJO de la bola (cero
    # desfase) + flechas EN EL PLANO del icono (anclaje mundo + lateral de
    # cámara, tangenciales) + LOD 50 % en juego / 100 % mirando el mango.
    ('AG · poderes inmediatez+LOD (v3638)', 'qa_poderes_v3638.py'),
    # AH (v3639): PARTIDA NUEVA = PALA LIMPIA (reporte del dueño: los
    # poderes sin gastar de una partida previa PERMANECÍAN) — hook único
    # rules.onMatchStart avisado por el árbitro en CADA startMatch (menú,
    # revancha por gatillo y de menú, cambio de modo, online, calibración
    # y reinicio automático del estado 'over') → _megaNormReset completo:
    # matriz, icono ×N, FX de los tres poderes, flechas, halo, marcas de
    # bola y escalas LOD. Idempotente y sin dispose doble.
    ('AH · partida nueva pala limpia (v3639)', 'qa_poderes_reset_v3639.py'),
    # AI (v3640): EL PODER ACTIVO SE VE EN LA PALA (petición del dueño:
    # «que el usuario sepa el tipo de poder que tiene activo, sin que
    # moleste») — el icono del mango NO desaparece al activar: pasa a modo
    # ACTIVO con ANILLO DE TIEMPO que se vacía (oro/cian/azul = firma del
    # canto), PARPADEA los últimos 2 s y al terminar vuelve al inventario.
    # Un solo icono (FASE 38), redibujo diferido+ahorrado (r46), el
    # indicador duerme en CADA _megaNormReset (FASE 41).
    ('AI · poder activo se ve en pala (v3640)', 'qa_poderes_activo_v3640.py'),
    # AJ (v3641): SÚPER PORTAL, 4.º PODER DE PALA (spec completa del dueño:
    # portal que traslada la bola tras cada golpe VÁLIDO — 8 s / 3 golpes,
    # desviación lateral 0,25–0,70 m, vertical 0–0,15 m, conserva 90–100 %
    # de la rapidez, antirrebote 0,25 s, salida legal con bote jugable por
    # el solver existente, swap ATÓMICO: la bola jamás cruza la red
    # físicamente, cero colisiones fantasma, árbitro y física intactos) +
    # penalización honesta a la IA rival (c06: predicción muerta al cruzar
    # el portal, error ×1,6, piernas ×0,75, +10 % de fallo; la marca se
    # limpia al devolver). Icono del dueño + voces ES/EN embebidos.
    # AJ (v3641) RETIRADA: verificaba el portal de r49 (swap inmediato +
    # muerte de predicción por frame — el dueño demostró en el Quest que la
    # IA dejaba de devolver). La sustituye AK (v3642).
    # AK (v3642): EL PORTAL SE ENTIENDE Y LA IA RESPONDE (informe del dueño
    # tras V3.6.41): tránsito EXPLÍCITO en 3 fases (portal de ENTRADA con
    # portals.png al 50 % en la zona de impacto + halo → la bola viaja
    # OCULTA 1 s con la física congelada → el MISMO portal se abre SOBRE la
    # mesa rival y la bola sale por su CENTRO con bote jugable del solver),
    # IA penalizada en % con FLANCO único (nunca anulada; la marca muere
    # con la ventana y con el punto), icono del dueño RECORTADO con alfa
    # (verificación PIL) y voz ES nativa Piper (la de r49 estaba corrupta),
    # ANTI-LAG (precaliente de 13 piezas al empezar la partida: cantos,
    # icono, imagen del portal y 4 voces) y PASSTHROUGH en AJUSTES (en VR,
    # por defecto OFF, cambio de modo en vivo con re-entrada automática).
    ('AK · portal se entiende + IA responde (v3642)', 'qa_portal_v3642.py'),
    # AL (v3643): SUPERPODERES QUE SE VEN Y SE OYEN (informe del dueño tras
    # V3.6.42): Súper EFECTO exagerado (brush ×3, Magnus ×2,2, bote ×2,4,
    # tope ×3, halo +35 %) · Súper IMÁN con radio 0,75 m, RESCATE real
    # (bolas escapadas atraídas al punto dulce) y 3 FLECHAS cian bola→pala
    # · Súper PORTAL con 3 GOLPES GARANTIZADOS por activación (el gasto
    # por golpe mataba la ventana con sorteo ×1 — «con uno solo me
    # desaparece»; vigilante de matriz retirado) · CUENTA SONORA 3·2·1
    # uniforme en los cuatro poderes (sin mirar el icono) · PASSTHROUGH EN
    # CALIENTE (sesión siempre immersive-ar; _pstAplicar canjea fondo/sala
    # al vuelo — el conmutador ya NO sale a la web).
    ('AL · superpoderes se ven y se oyen (v3643)', 'qa_superpoderes_v3643.py'),
    # r52 (v3644): el informe del dueño tras probar V3.6.43 en el Quest —
    # «el Super iman no hace nada… en el Super efecto tampoco noto nada,
    # además de que la marca del bote va desfasada. El sonido de alerta de
    # que se está agotando no suena o no se percibe» → IMÁN con campo
    # continuo en la pala + flechas ×1,8 ANCLADAS (la r51 las construyó
    # pero nadie las llamaba) + física 0,95/6,5/0,80 y rescate 7,5/1,05 ·
    # EFECTO con halo 0,21 + estela roja + anillo de bote mayor · MARCA DEL
    # BOTE clavada a la bola visual · BLIPS 988/1319 a gain 0,42 con
    # háptica 3·2·1 · y el LADRILLO BOMBA del ARKANOID 2 (etapa 4 de La
    # Locura): negro con bomba.webp, sustituye a un azul (≥1 vez/partida
    # garantizada), salta cada 4 s, espera sin azules, DETONA radio
    # 2 filas × 2 columnas (bola o láser) y no vuelve en la partida.
    ('AM · imán/efecto se notan + bomba (v3644)', 'qa_bomba_v3644.py'),
    # r53 (v3645): LA BOMBA POR INTERVALOS + EL LADRILLO ELÉCTRICO del
    # ARKANOID 2 (etapa 4 de La Locura) — «salga de manera aleatoria pero
    # con intervalos de 15 segundos si tiene ladrillos disponible donde
    # aparecer» (cadencia r53: 1.ª aparición 2-12 s, siguiente a +15 s) ·
    # y en los ÚLTIMOS 30 s un azul al azar se ELECTRIFICA (rayitos pool
    # de 14, chisporroteo, ZAP de sellado; SÓLO la bola lo activa — el
    # láser ni lo ve) → al darle con la bola ATRAE al resto y los reparte
    # por ANILLOS en las celdas contiguas (las más próximas primero),
    # todos eléctricos → CUALQUIER impacto desencadena la REACCIÓN EN
    # CADENA ramificada (ondas de 0,12 s) que arrasa la pared = misión
    # SUPERADA, con el reloj CONGELADO durante el destrozo. state0 restaura
    # el muro de fábrica con cada partida.
    ('AN · bomba por intervalos + ladrillo eléctrico (v3645)',
     'qa_electrico_v3645.py'),
    # AO (ronda 54 · v3.6.46): el SÚPER EFECTO es SPIN REAL — el movimiento
    # de la pala al golpear clasifica TOPSPIN/BACKSPIN/SIDESPIN y el BOTE
    # traduce cada uno (acelera hacia delante / casi PARA / patada lateral),
    # con penalización al rival ya viva (error ×2 · piernas ×0,85) y halo +
    # anillo de bote TINTADOS por tipo. El SÚPER IMÁN es un GANCHO: la bola
    # que viene en nuestra dirección de golpeo es arrastrada al CENTRO VIVO
    # de la pala; fuera flechas/campo/canto — PALA METÁLICA −80 % mientras
    # dure. Y la pala del rival JAMÁS atraviesa la mesa (clamp del mango
    # completo: hoja + palo hasta la punta, puerta con el agarre).
    ('AO · spin real + gancho + pala metálica + clamp mango (v3646)',
     'qa_spin_pala_v3646.py'),
    # AP (ronda 55 · v3.6.47): el SÚPER EFECTO SÓLO vive en el INTERCAMBIO
    # (petición del dueño): NUNCA sobre el saque (ni propio — serveFlight —
    # ni el del rival — su ventana no es rally) y SÓLO en las jugadas del
    # JUGADOR (el multiplicador viaja en sus palas); la firma del bote
    # (topspin/backspin/sidespin) y el acople ×2,4 SÓLO en la MITAD DEL
    # RIVAL (boteRival = pos.z < C) — mishits y botes propios son juego
    # normal. Fuera del rally la pala es HONESTA (sin brush ×2 ni marca).
    ('AP · efecto sólo en el intercambio y en la mesa del rival (v3647)',
     'qa_efecto_rally_v3647.py'),
    # AQ (ronda 56 · v3.6.48): LA NORMA DEL DUEÑO — «Todos los superpoderes
    # de la pala que se concedan superados los 20 toques no antes. El super
    # iman que ralentice la bola y la dirija hacia el centro de nuestra
    # pala… el efecto solo entra cuando tenemos que devolver un golpe del
    # rival… menos en los saques… evidentemente el efecto solo dura 10
    # segundos. Pasado ese tiempo… todo vuelve a la normalidad. El super
    # Efecto tambien solo está activo 10 segundos desde la activación y la
    # ventaja del efecto en los botes solo es para nosotros, el perjudicado
    # siempre es el rival.» → MEGA_GOLPES 11→20 (19 toques NADA · 20 → +1 ·
    # 40/60 acumula · 80 tope), EFECTO_DUR/IMAN_DUR 8→10 con ventana
    # PURAMENTE TEMPORAL (RETIRADOS los topes de golpes: EFECTO_GOLPES,
    # IMAN_ASIST y el cierre por golpes — el reloj es la única ley), el
    # r57: el GANCHO/FRENO se RETIRA — el imán es GUÍA DE TIRO (el solver
    # de la casa corrige cada golpe hacia la mesa del rival; 10 s sin gasto
    # por asistencia). Golden de física intacto (la guía vive en el golpe).
    ('AQ · poderes: 20 toques y 10 segundos (v3648)',
     'qa_poderes_10s20_v3648.py'),
    # r57: NORMA DE EMOCIONES DEL RIVAL (regla del dueño en TODOS los
    # campeonatos: idle/crazy/angry/laughing/focused/picando/surprised/
    # panic/pool>20/victory/defeated) + las 3 imágenes nuevas (pared
    # izquierda y suelo del Hall, suelo de pista para partido/entrenamiento).
    ('AR · norma de emociones del rival + imágenes r57 (v3649)',
     'qa_norma_rival_v3649.py'),
    ('AS · súper clonación + voz del selector (v3650)',
     'qa_clon_voz_v3650.py'),
    # r59 (v3651): LA ACADEMIA — TUTORIAL INTERACTIVO (petición del dueño:
    # «la gente entra, hay tanto menú y opciones que no saben ni cómo hacer
    # para sacar»). 9 pasos guiados con práctica real sobre la mesa de
    # verdad: TU MANDO (diagrama Quest + gatillo), LA PALA (vaivén), EL
    # SAQUE (bola en mano libre, cruce de red, rearme), EL INTERCAMBIO
    # (profesor con el solver de la casa, 2 devoluciones), LOS BOTONES
    # (A/X real), LOS MODOS + 5 poderes, ¡YA SABES JUGAR! Tres puertas
    # (banner del HUB, oferta de primera vez, AJUSTES) y B/Y de salida.
    # AT (v3651) CAPA HISTÓRICA desde r69: su aguja «botón de repetir el
    # tutorial en AJUSTES» contradice la orden del dueño (r69 retiró ese
    # botón; la academia vive en el banner del HUB y la oferta de primera
    # vez). La cadena BB (r67) → BD (r69) → BE (r70) → BF (r71) conserva y
    # amplía sus verificaciones vivas.
    # AU (ronda 60): aguja del tutorial actualizada a la verdad actual
    # (SIN tut:go en AJUSTES desde r69).
    # AV (ronda 61): agujas del adaptativo actualizadas a su casa nueva:
    # AJUSTES › JUEGO (ronda 71).
    # AU (ronda 60 · v3.6.52): LOS TRES ARREGLOS del informe del dueño tras
    # probar LA ACADEMIA en el Quest — (1) «el tutorial se queda bloqueado,
    # se superpone con otras ventanas del menú y no es pulsable»: el menú
    # NACÍA del clic y seguía abierto (delante del jugador, order 990 sobre
    # el 985 del panel, misma altura de ojos) y toggleMenu duerme con calib —
    # start() ahora lo cierra DIRECTO (3 puertas cubiertas) con salida B/Y
    # siempre viva; (2) «ME HAS QUITADO DE TODOS LOS ESCENARIOS LOS
    # TROQUELES»: no se borraron — el cerrojo champDecorHidden de las
    # pruebas especiales podía quedar PECHO tras una salida no prevista
    # (reproducido en vivo) → AUTOCURACIÓN en leaveAll (también en el return
    # temprano) y los 5 campeonatos verifican SU decorado en vivo; (3) «la
    # etapa 4 del orbe en Wizard… supera los 1000 y pico… como mucho la
    # mitad… penalizando los FPS»: ORBE_COMPLEJO 1.419 → 515 (−63,7%, tope
    # ≤710) con la MISMA envergadura (0,625 m), dianas +42%, cima 2,07 < HUD
    # 2,28 y base en mesa — recuento REAL en la página sobre las constantes
    # SERVIDAS. BONUS pinzado en la auditoría: el MAPA DEL TALLER de
    # valle_neon llevaba detached desde SDK5 (add antes de existir el group
    # perezoso) → build() antes de colgar; la batería vuelve a ir SIN
    # errores JS.
    ('AU · tres arreglos del dueño (v3652)', 'qa_r60_v3652.py'),
    # AV (ronda 61 · v3.6.53): LAS TRES CANDIDATAS APROBADAS por el dueño —
    # (1) ESTELA DE PODER: la estela viste la firma del poder ACTIVO (mega
    # ámbar · efecto rojo · imán cian · portal violeta · clon azul fantasma)
    # con lerp y respaldo por spin; (2) RIVAL ADAPTATIVO visible y decidible
    # (existía desde v2.x: conmutador persistente HUB+AJUSTES, mensaje y
    # lerp del factor — gana→aprieta, pierde→afloja, OFF honesto);
    # (3) REPETICIÓN DEL MEJOR INTERCAMBIO: grabadora por frames y fantasmas
    # al terminar el partido (mejor = más toques, ≥3; gatillo salta; sin
    # grabación en calib/academia/online; visibilidades restauradas exactas).
    ('AV · estela+adaptativo+repetición (v3653)', 'qa_r61_v3653.py'),
    # AW (v3654): SONIDO REAL por síntesis modal (5 muestras físicas
    # incrustadas con playbackRate por velocidad + jitter, canto metálico
    # propio con e.edge, fallback sintético intacto) + HÁPTICA ESCALADA por
    # impacto (rally+saque, ARKANOID conserva refuerzo v2.44) + CÁMARA LENTA
    # (repetición al 50% con pastilla ámbar + dilatación de la bola de
    # partido 0,34×→1 en ~1,15 s, sólo local).
    ('AW · sonido real+háptica+cine (v3654)', 'qa_r62_v3654.py'),
    # AX (v3655): LA ACADEMIA CIERRA BIEN — arreglo del panel huérfano del
    # tutorial (stop anulaba el juego antes de desmontar el panel: el panel
    # quedaba VISIBLE para siempre). QA sobre el GRAFO DE ESCENA (lo que el
    # jugador ve): nace en el rig, desaparece con gatillo y B, sin
    # duplicados ni residuos, sello sólo al jugar, partido jugable tras salir.
    ('AX · academia cierra bien (v3655)', 'qa_r63_v3655.py'),
    # AY (v3656): LA ACADEMIA, A PUNTO — las tres correcciones del dueño al
    # tutorial: (1) textos auto-ajustados (fitFont/pill/wrap2, canvas
    # 1280×800: nada se corta ya); (2) MANDO 3D PROCEDURAL Touch Plus (6
    # piezas giratorias con resalte por paso, la promesa del punto 2);
    # (3) práctica real (3 saques válidos con cerrojo + 6 devoluciones con
    # rally real) y el panel se APARTA a un lado en la práctica (pose
    # frente⇄lado con lerp). QA de fuente + grafo con rig real.
    # AZ (v3657): EL ONBOARDING GAMIFICADO — voz nativa Piper es/en (25
    # átomos por idioma, narra al entrar, STICK repite), mando GLB REAL
    # del dueño con halos por pieza (anclas por raycast) y 4 acciones
    # reales en el paso 1, 2 pasos NUEVOS de reglas visuales sobre la
    # mesa (holo marcador a 11 + holo rotación del saque con doble bote),
    # panel PIZARRA del dueño (textos tiza en la zona negra), el saque
    # demo del espectador DUERME en la academia (adiós al bote continuo)
    # y gating real en los 11 pasos.
    # BA (v3658): LA ACADEMIA SOBRE LA MESA — informe del dueño tras
    # V3.6.57: bola DORMIDA en los pasos quietos (adiós al bote continuo
    # de la bola apoyada), voces Piper MÁS PAUSADAS (length-scale 1.16 +
    # respiros), DOS mandos GLB reales centrados (izquierdo Y/X + derecho
    # B/A espejo), halos OPACOS con etiqueta, RAQUETA FANTASMA sobre los
    # mandos, pintor 9 sin solapes y las reglas REALES sobre la mesa:
    # paso 3 (demo de saque con los mandos + 3 saques tuyos), paso 4
    # (intercambio real: el rival devuelve hasta fallar — rota el sacador)
    # y paso 5 (marcador BAJO con saques reales: 11 por 2 y 10-10 cada
    # punto). Panel apartado en 3-6: la mesa nunca tapada.
    # BB (v3659): LA ACADEMIA EN TUS MANOS — informe del dueño tras
    # V3.6.58: (1) speakPlan CANCELA la voz viva (adiós al audio doble);
    # (2) mandos GLB ANCLADOS a los grips XR reales al 75% (nada flotando);
    # (3) UNA sola raqueta (aura sobre la pala REAL, sin clones fantasma);
    # (4) guion reorganizado a 9 pasos con demo del PROFESOR sobre la mesa
    # real + AROS GUÍA y la rejilla de modos 2×3 en UNA pizarra.
    # BC (v3660): LA RAQUETA DEL RIVAL — informe del dueño tras V3.6.59:
    # «la pelota en el saque y en el juego debe ser golpeada por la raqueta
    # del rival; permanece quieta y la golpea un fantasma». El profesor
    # tiene PALA visible (la misma del juego, hoja en el origen) que arma,
    # barre y golpea: saques demo/marcador retenidos hasta que la hoja
    # llega, devoluciones de pasos 3/5 desde la posición exacta de la bola
    # y el feed del paso 5 con bola VIVA (la renumeración r67 la dejó
    # congelada: sin tutBolaViva en ese paso, el rally no existía).
    # BD (v3661): UNA RAQUETA, CERO FANTASMAS — capa histórica, sustituida
    # por BE (qa_r70_v3662) que conserva sus verificaciones y añade las de
    # la r70 (anclaje al rig, saque de dos botes, voz cortada, passthrough).
    # BE (v3662): LA ACADEMIA PERFECTA — capa histórica, sustituida por
    # BF (qa_r71_v3663) que conserva sus verificaciones y añade las de la
    # r71 (palma del profesor elevada con solver verificado, botes SOBRE
    # la mesa con vallas x/z/y, cartel con autoajuste, menú por categorías).
    # AY (v3656) · AZ (v3657) · BA (v3658) · BB (v3659) CAPAS HISTÓRICAS desde
    # r70: sus guiones MECÁNICA teletransportan la bola con la semántica del
    # árbitro PRE-r70 (un solo contacto contaba por «cruzada») y quedaron
    # sin ejecutar en las rondas 68-70 (subconjunto de 12 capas). La cadena
    # BD (r69) → BE (r70) → BF (r71) re-verifica la academia COMPLETA con
    # las reglas VIGENTES (dos botes sobre la mesa, vallas x/z/y, palma
    # elevada, raqueta al RIG) — sus agujas vivas viven en BF.
    # BF (v3663): EL SERVICIO HONESTO — el informe del dueño tras V3.6.62:
    # el saque del profesor debía botar primero en SU campo (la palma vieja
    # hacía imposible el doble bote: fallback = un solo bote), el saque del
    # jugador contaba botes en el SUELO (largos y laterales «buenos»), el
    # cartel del 10-10 recortaba «GANAR», y la CPU + el rival adaptativo
    # debían vivir DENTRO de un AJUSTES reorganizado por subcategorías con
    # iconos explícitos.
    ('BF · servicio honesto (v3663)', 'qa_r71_v3663.py'),
    # BG (v3664): EL TELÓN Y EL CANDADO — el informe del dueño tras V3.6.63:
    # los títulos del cartel de la Academia pisaban la cabecera (pasos 3/4/7
    # solapados, paso 8 con el texto PODERES dentro de la tarjeta ENTRENAR
    # por el wrap2 sin x), las 5 tarjetas de Entrenamiento sin icono, Astro
    # invisible (el grupo del orbital colgado de scene y no del rig) y la
    # entrada a campeonatos viéndose montarse: telón negro + candados con
    # voz «Próximamente» y bypass FORO3D.
    ('BG · telón y candado (v3664)', 'qa_r72_v3664.py'),
]

# Capas POST-DEPLOY (--produccion): cargan game.html de PRODUCCIÓN y exigen
# que pages sirva la versión de la FUENTE DE VERDAD (src/game/VERSION.json).
CAPAS_PRODUCCION = [
    ('K · hints del hub (prod)', 'qa_hub_hints.py'),
    ('L · champion listo (prod)', 'qa_champion_listo.py'),
]

def main():
    rapido = '--rapido' in sys.argv
    produccion = '--produccion' in sys.argv
    # r60: --desde N --hasta M (1-indexados sobre CAPAS+PRODUCCION) para
    # poder trocear la suite en turnos cortos sin recortar cobertura.
    def _num(flag, defecto):
        return int(sys.argv[sys.argv.index(flag) + 1]) if flag in sys.argv else defecto
    desde, hasta = _num('--desde', 1), _num('--hasta', 10 ** 6)
    capas = [(i, n, s) for i, (n, s) in
             enumerate(CAPAS + (CAPAS_PRODUCCION if produccion else []), 1)
             if desde <= i <= hasta]
    filas = []
    fallos_total = 0
    t_global = time.monotonic()
    for _idx, nombre, script in capas:
        if not script or not (SCR / script).exists():
            filas.append((nombre, 'AUSENTE', '-', script or '(no encontrado)'))
            fallos_total += 1
            continue
        if rapido and script.startswith('qa_sup1'):
            break
        cmd = ['node', '--no-warnings', str(SCR / script)] if script.endswith('.mjs') \
            else [sys.executable, str(SCR / script)]
        t0 = time.monotonic()
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=TIMEOUT.get(script, 600))
            dur = time.monotonic() - t0
            salida = r.stdout + r.stderr
            if script.endswith('.mjs'):
                # test_fisica: 'RESULTADO: N escenarios · 0 desviaciones'
                linea = next((l for l in salida.splitlines() if l.startswith('RESULTADO')), '')
                desv = '0 desviaciones' in linea and r.returncode == 0
                estado = 'OK' if desv else 'FALLO'
                resumen = linea.replace('RESULTADO: ', '').strip()
            else:
                linea = next((l for l in salida.splitlines()
                              if 'RESULTADO' in l.upper()), '')
                limpio = linea.replace('RESULTADO:', '').replace('RESULTADO', '').strip()
                n_fallos = 0
                for trozo in limpio.replace('OK ·', '·').split('·'):
                    t = trozo.strip().lower()
                    for pref in ('fallos', 'fallo', 'desviaciones'):
                        if t.startswith(pref):
                            try:
                                n_fallos = int(t.split()[0])
                            except (ValueError, IndexError):
                                n_fallos = 9999
                estado = 'OK' if (r.returncode == 0 and n_fallos == 0) else 'FALLO'
                resumen = f'{limpio} ({dur:.0f} s)'
        except subprocess.TimeoutExpired:
            dur = time.monotonic() - t0
            estado, resumen = 'TIMEOUT', f'>{dur:.0f} s'
        if estado != 'OK':
            fallos_total += 1
        filas.append((nombre, estado, resumen, script))

    print('=' * 72)
    print('CRAZY PING PONG · QA TOTAL')
    print('=' * 72)
    for nombre, estado, resumen, script in filas:
        marca = '✓' if estado == 'OK' else ('·' if estado == 'OMITIDA' else '✗')
        print(f'  {marca} {nombre:28s} [{estado:7s}] {resumen}  ({script})')
    print('=' * 72)
    print(f'  TIEMPO TOTAL: {time.monotonic() - t_global:.0f} s · '
          f'CAPAS EN FALLO: {fallos_total}')
    sys.exit(1 if fallos_total else 0)

if __name__ == '__main__':
    main()
