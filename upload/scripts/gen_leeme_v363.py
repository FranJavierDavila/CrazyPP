#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenera download/LEEME-DESCARGA.txt para la V3.6.3-SDK3 (FASE 5 del plan
de modularización: createMusic unifica la música de los campeonatos)."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.6.3-SDK3
(FASE 5 de la modularización · música unificada en el SDK)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v363-sdk3-COMPLETO.zip     125.216.557 B (~119 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (con el SDK compartido championships/sdk/) +
    relay live-service + extras Next.js + guías. ES EL RECOMENDADO:
    con uno solo tienes la web y el relay.

  crazypp-v363-sdk3-CLOUDFLARE.zip   125.203.941 B (~119 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v363-sdk3-ligera.zip        11.454.675 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar;
    el SDK de campeonatos viaja dentro de ella). Ideal para Netlify
    Drop o pruebas rápidas; faltarán los campeonatos salvo que copies
    championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.6.3-SDK3
  · FASE 5 de la modularización P0: createMusic (champ_sdk.js v1.2.0)
    unifica la MÚSICA en bucle de los campeonatos. Los tres motores
    que seguían duplicados convergen en UNA sola máquina de estados
    del SDK, cada uno con su conducta exacta: el OESTE baja la BSO
    del saloon (motor v2.78+v2.124: fundido 0,8 s, sincronía en vivo
    con el ajuste global, UNA MELODÍA, resurrección de contexto) y la
    música del vagón (v2.111: sin fundido, sync directo), MAGIA su
    BSO del Wizard (v30) y VALLE NEÓN su música WAV (v3: volumen
    fijo, fundido de entrada 1,2 s, parada con fundido 0,4 s). La
    exclusividad BSO↔vagón se reproduce con opts.excluso.
  · El fix v2.125 (decodeAudioData en forma promesa) vive UNA vez en
    el SDK también para la música: NINGÚN módulo conserva ya
    decodeAudioData propio. Un bug del kernel se arregla UNA vez y
    sirven los 5 campeonatos.
  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta, los
    superpoderes redefinidos de SUP1, el reactor, el escudo y los
    duelos se comportan exactamente igual.
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
    NUEVO: también puedes jugar SIN descargar nada desde
    https://franjavierdavila.github.io/CrazyPP/ (GitHub Pages).
  · Comprueba la versión: la portada muestra el sello V3.6.3-SDK3 y en
    consola window.__PP_VERSION === '3.6.3-SDK3' (y window.__PP_SDK
    === '1.2.0' al cargar un campeonato).
  · Los 4 ZIPs se regeneran byte-exactos con el ensamblador del repo:
    python3 scripts/release-v363/build_zip.py (la cadena íntegra de
    release vive en git, a salvo de los reciclajes del sandbox).
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado para V3.6.3-SDK3')
