#!/usr/bin/env python3
"""Regenera download/LEEME-DESCARGA.txt para la V3.6.1-SDK1 (SDK de campeonatos)."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.6.1-SDK1
(SDK de campeonatos · FASE 3 de la modularización)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v361-sdk1-COMPLETO.zip     125.211.557 B (~119 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (con el SDK compartido championships/sdk/) +
    relay live-service + extras Next.js + guías. ES EL RECOMENDADO:
    con uno solo tienes la web y el relay.

  crazypp-v361-sdk1-CLOUDFLARE.zip   125.199.213 B (~119 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v361-sdk1-ligera.zip        11.453.419 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar;
    el SDK de campeonatos viaja dentro de ella). Ideal para Netlify
    Drop o pruebas rápidas; faltarán los campeonatos salvo que copies
    championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.6.1-SDK1
  · SDK DE CAMPEONATOS (FASE 3 de la modularización P0): nace
    championships/sdk/champ_sdk.js v1.0.0 — el kernel que los 5
    campeonatos reimplementaban vive en UNA sola fuente: motor de SFX
    canónico (con la lección v2.125 «forma promesa» que llegó a estar
    copiada 7 veces en el Oeste), congela()/descongela() del aviso de
    superpoder (patrón de La Locura) y el puente al núcleo. Un bug del
    kernel se arregla UNA vez y sirven los 5.
  · LA ESTACIÓN ORBITAL estrena la adopción (manifest v14): su voz
    (_sfx) y el congelado del aviso vienen del SDK con conducta
    idéntica.
  · CERO cambios de gameplay: superpoderes redefinidos de SUP1,
    meteoritos 3D, rayo tractor con dron, gravedad cero, audios del
    ASTRO, diana 2 s y pelota que siempre vuelve — todo se comporta
    exactamente igual.
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
  · Comprueba la versión: la portada muestra el sello V3.6.1-SDK1 y en
    consola window.__PP_VERSION === '3.6.1-SDK1' (y window.__PP_SDK
    === '1.0.0' al cargar un campeonato).
  · Los 4 ZIPs se regeneran byte-exactos con el ensamblador del repo:
    python3 scripts/release-v361/build_zip.py (la cadena íntegra de
    release vive en git, a salvo de los reciclajes del sandbox).
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado para V3.6.1-SDK1')
