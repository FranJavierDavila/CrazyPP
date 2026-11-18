#!/usr/bin/env python3
"""Regenera download/LEEME-DESCARGA.txt para la V3.4.1-RIV1."""
txt = """==========================================================
CRAZY PING PONG · CENTRO DE DESCARGAS · V3.4.1-RIV1
(ASTRO recolocado + Reactor de impulso en la etapa 4)
==========================================================

En esta carpeta están los 4 paquetes de la versión vigente, los mismos
que sirven los botones del hub /descargas de la preview:

  crazypp-v341-riv1-COMPLETO.zip     123.740.436 B (~118 MB)
    TODO: juego (index.html) + CRAZY TV (tv.html) + intro oficial +
    los 5 campeonatos (Estación Orbital con sus DOS reactores) + relay
    live-service + extras Next.js + guías. ES EL RECOMENDADO: con uno
    solo tienes la web y el relay.

  crazypp-v341-riv1-CLOUDFLARE.zip   123.728.360 B (~118 MB)
    El mismo juego pero ESTÁTICO PURO: sin TypeScript ni package.json,
    aceptado por la subida directa de Cloudflare Pages (arrastrar y
    soltar, sin wrangler). El relay NO va dentro: cógelo del COMPLETO
    o del SOLO.

  crazypp-v341-riv1-ligera.zip        11.447.371 B (~11 MB)
    El juego SIN la carpeta championships/ (va preparada para copiar).
    Ideal para Netlify Drop o pruebas rápidas; faltarán los
    campeonatos salvo que copies championships/ del COMPLETO.

  crazypp-live-service-SOLO.zip            6.089 B (~6 KB)
    Solo el relay de la CRAZY TV (live-service) para subir a
    GitHub → Railway/Render («npm install && npm start»).

QUÉ HAY DE NUEVO EN LA V3.4.1-RIV1
  · FIX DE COLOCACIÓN DEL ASTRO: el rival de la sala de la Estación
    Orbital ya NO se lee dentro de la pared frontal. Ahora está en la
    convención de duelos de la casa (x 1,26 · z −3,82): junto a la
    esquina lejana derecha de la mesa, en espacio abierto, a la misma
    profundidad que el CLOWN y el WIZARD, cuerpo entero y pies en el
    suelo. En el casco se ve entero y despejado desde el saque.
  · Todo lo de la V3.4.0-IMP1 sigue intacto: REACTOR DE IMPULSO en la
    etapa 4 (base flotante, cubos cuánticos 3/5/7, pistola láser,
    dianas 1 s/1 s, perturbaciones), REACTOR DE ENERGÍA INESTABLE en
    la etapa 2, PRECISIÓN CCD, saque VR realista, hall, CRAZY TV.

DESPLIEGUE EN 3 PASOS (Cloudflare Pages, el habitual)
  1. Descomprime el ZIP (el COMPLETO o el CLOUDFLARE).
  2. Sube la CARPETA a Cloudflare Pages (arrastrar y soltar) o a
     Netlify Drop (con el ligero). index.html es el juego.
  3. Opcional (CRAZY TV): sube live-service/ a Railway/Render
     («npm install && npm start») y abre el juego con
     ?relay=https://TU-RELAY (los espectadores entran en tv.html).

NOTAS
  · En el casco, abre https://TU-DOMINIO (HTTPS obligatorio en Quest).
  · Comprueba la versión: la portada muestra el sello V3.4.1-RIV1 y en
    consola window.__PP_VERSION === '3.4.1-RIV1'.
  · Versiones anteriores (v3.3.0-NUC1, v3.4.0-IMP1) se regeneran bajo
    petición: sus ensambladores viven en scripts/release-v330/ y
    scripts/release-v340/ del repositorio.
"""
open('/home/z/my-project/download/LEEME-DESCARGA.txt', 'w', encoding='utf-8').write(txt)
print('LEEME-DESCARGA.txt regenerado (V3.4.1-RIV1)')
