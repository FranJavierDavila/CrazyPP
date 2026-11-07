#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenera download/LEEME-DESCARGA.txt para la V3.6.4-SDK4 (FASE 5 del plan
de modularización: createPowerSign unifica el tablón de superpoder)."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.6.4-SDK4
(FASE 6 de la modularización · tablón y música en el SDK)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v364-sdk4-COMPLETO.zip     125.213.762 B (~119 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (con el SDK compartido championships/sdk/) +
    relay live-service + extras Next.js + guías. ES EL RECOMENDADO:
    con uno solo tienes la web y el relay.

  crazypp-v364-sdk4-CLOUDFLARE.zip   125.201.138 B (~119 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v364-sdk4-ligera.zip        11.453.534 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar;
    el SDK de campeonatos viaja dentro de ella). Ideal para Netlify
    Drop o pruebas rápidas; faltarán los campeonatos salvo que copies
    championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.6.4-SDK4
  · FASE 6 de la modularización P0: createPowerSign (champ_sdk.js
    v1.3.0) unifica el CARTEL DE SUPERPODER. Los 4 campeonatos con
    duelos delegan en UNA fábrica del SDK con dos coreografías
    exactas: la «clasica» v2.120 (Oeste v51 y Magia v31 — el Oeste
    conserva su respaldo pintado del tablón quemado y Magia su arte
    por canvas 1024) y la «v240» (La Locura v22 y la Estación
    Orbital v15 — con el HALO DE CONTORNO que respira; el orbital
    conserva _ownTex y el dispose de la regla Quest pasa a los cuatro).
  · El anclado a la red (v2.88) y el icono circular del poder
    anunciado (v2.120) son COMUNES: un bug del tablón se arregla UNA
    vez y sirven los 4.
  · La FASE 5 (createMusic) sigue intacta: ningún módulo conserva
    decodeAudioData propio y la música suena exactamente igual.
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
  · Comprueba la versión: la portada muestra el sello V3.6.4-SDK4 y en
    consola window.__PP_VERSION === '3.6.3-SDK3' (y window.__PP_SDK
    === '1.3.0' al cargar un campeonato).
  · Los 4 ZIPs se regeneran byte-exactos con el ensamblador del repo:
    python3 scripts/release-v364/build_zip.py (la cadena íntegra de
    release vive en git, a salvo de los reciclajes del sandbox).
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado para V3.6.4-SDK4')
