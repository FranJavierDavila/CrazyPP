#!/usr/bin/env python3
"""Regenera download/LEEME-DESCARGA.txt para la V3.6.0-SUP1 (tras reciclaje del sandbox)."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.6.0-SUP1
(Superpoderes redefinidos + voz del ASTRO)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v360-sup1-COMPLETO.zip     125.206.366 B (~119 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (Estación Orbital con los superpoderes
    redefinidos, el Reactor de impulso y el Escudo de pala) + relay
    live-service + extras Next.js + guías. ES EL RECOMENDADO: con uno
    solo tienes la web y el relay.

  crazypp-v360-sup1-CLOUDFLARE.zip   125.194.235 B (~119 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v360-sup1-ligera.zip        11.451.838 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar).
    Ideal para Netlify Drop o pruebas rápidas; faltarán los
    campeonatos salvo que copies championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.6.0-SUP1
  · SUPERPODERES REDEFINIDOS: el aviso «Super Power!!» congela la
    partida de verdad (IA, física, saque y árbitro) hasta que
    desaparece — como en La Locura de siempre.
  · METEORITOS EN 3D: pequeñas rocas procedurales (basalto con vetas
    de óxido, calor de entrada y tumbling) que estallan al bloquear
    la bola. Fuera las imágenes recortadas.
  · RAYO TRACTOR con DRON: el rayo sale del emisor de un mini dron;
    la bola que lo cruza queda ATRAPADA flotando dentro del rayo y
    SOLO cae VERTICALMENTE cuando el rayo desaparece.
  · GRAVEDAD CERO real: las partículas blancas ATRAEN la bola y la
    hacen rebotar ENTRE ELLAS de manera aleatoria hasta que
    desaparecen y la dejan caer.
  · AUDIOS DEL ASTRO (mp3 del dueño): risa_astro.mp3 con la pose de
    risas y enfado_astro.mp3 cuando pierde un punto.
  · REACTOR DE IMPULSO (etapa 2): diana cuántica visible 2 s y la
    pelota SIEMPRE vuelve a botar sobre la base flotante.
  · Todo lo anterior intacto: ESCUDO DE PALA en la etapa 4, Reactor
    de energía inestable, PRECISIÓN CCD SDF, saque VR realista,
    gracia del saque, bote honesto, hall del anfitrión, física viva,
    palas con carácter, CRAZY TV y los 5 campeonatos.

DESPLIEGUE EN 3 PASOS (Cloudflare Pages, el habitual)
  1. Descomprime el ZIP (el COMPLETO o el CLOUDFLARE).
  2. Sube la CARPETA a Cloudflare Pages (arrastrar y soltar) o a
     Netlify Drop (con el ligero). index.html es el juego.
  3. Opcional (CRAZY TV): sube live-service/ a Railway/Render
     («npm install && npm start») y abre el juego con
     ?relay=https://TU-RELAY (los espectadores entran en tv.html).

NOTAS
  · En el casco, abre https://TU-DOMINIO (HTTPS obligatorio en Quest).
  · Comprueba la versión: la portada muestra el sello V3.6.0-SUP1 y en
    consola window.__PP_VERSION === '3.6.0-SUP1'.
  · Los 4 ZIPs se regeneran byte-exactos con el ensamblador del repo:
    python3 scripts/release-v360/build_zip.py (la cadena íntegra de
    release vive en git, a salvo de los reciclajes del sandbox).
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado para V3.6.0-SUP1')
