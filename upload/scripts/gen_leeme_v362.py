#!/usr/bin/env python3
"""Regenera download/LEEME-DESCARGA.txt para la V3.6.2-SDK2 (FASE 4 del plan
de modularización: el SDK de campeonatos adoptado por los 5)."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.6.2-SDK2
(FASE 4 de la modularización · SDK en los 5 campeonatos)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v362-sdk2-COMPLETO.zip     125.213.949 B (~119 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (con el SDK compartido championships/sdk/) +
    relay live-service + extras Next.js + guías. ES EL RECOMENDADO:
    con uno solo tienes la web y el relay.

  crazypp-v362-sdk2-CLOUDFLARE.zip   125.201.525 B (~119 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v362-sdk2-ligera.zip        11.452.689 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar;
    el SDK de campeonatos viaja dentro de ella). Ideal para Netlify
    Drop o pruebas rápidas; faltarán los campeonatos salvo que copies
    championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.6.2-SDK2
  · FASE 4 de la modularización P0: el SDK DE CAMPEONATOS
    (champ_sdk.js v1.1.0) ya lo usan LOS 5 campeonatos. La Estación
    Orbital estrenó la adopción en SDK1; ahora se suman el OESTE
    (4 motores SFX one-shot + 3 congelados; manifest v49), MAGIA
    (risa del mago + congelado; v29), LA LOCURA (el congelado del
    aviso — el patrón v2.40 que NACIÓ en ese módulo — + puente; v21)
    y VALLE NEÓN (puente; v2).
  · SDK v1.1.0: precarga() (calentar la cache sin sonar, el patrón
    load* de la casa) y opts.pan (paneo estéreo opcional). Un bug
    del kernel se arregla UNA vez y sirven los 5 campeonatos.
  · CERO cambios de gameplay: física CCD/SRV2/FEEL1 intacta, los
    superpoderes redefinidos de SUP1, el reactor, el escudo y los
    duelos se comportan exactamente igual. La música en bucle (BSO
    del saloon, vagón del Oeste, valle) conserva su motor propio.
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
  · Comprueba la versión: la portada muestra el sello V3.6.2-SDK2 y en
    consola window.__PP_VERSION === '3.6.2-SDK2' (y window.__PP_SDK
    === '1.1.0' al cargar un campeonato).
  · Los 4 ZIPs se regeneran byte-exactos con el ensamblador del repo:
    python3 scripts/release-v362/build_zip.py (la cadena íntegra de
    release vive en git, a salvo de los reciclajes del sandbox).
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado para V3.6.2-SDK2')
