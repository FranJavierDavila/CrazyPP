#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RELEASE-V3.0.txt → cabecera V3.0.1 con tamaños/hash REALES + guía de verificación."""
import sys

PATHS = [
    '/home/z/my-project/download/RELEASE-V3.0.txt',
    '/home/z/my-project/public/descargas/RELEASE-V3.0.txt',
]

OLD_HEAD = """RELEASE CONGELADO — CRAZY PING PONG V3.0 «PRO TRAINING»
Fecha de sellado: 14/10/2026
Base: V2.141 (recuperada del enlace WeTransfer del dueño, SHA256 46948d37…, auditoría SUPERADA)

CONTENIDO DEL RELEASE
----------------------
1. crazypp-v3.zip                100.713.287 bytes → EL JUEGO COMPLETO V3.0
   - index.html 6.202.711 B: todo el juego en un solo archivo
     (V2.141 íntegra + módulo PRO TRAINING nuevo)
   - assets/intro.mp4 + 4 campeonatos autocontenidos:
     La Locura v20 (eager) · Magia v28 · Salvaje Oeste v48 · Estación Orbital v5
   - SHA256: c9c10c64fb8ee09c65ff39815f98c10deda494b11042d96d7a05c12dc6783d82
"""

NEW_HEAD = """RELEASE CONGELADO — CRAZY PING PONG V3.0.1 «PRO TRAINING»
Fecha de sellado: 14/10/2026 · V3.0.1 re-sellada el 14/10/2026 (fixes de la prueba en el casco)
Base: V2.141 (recuperada del enlace WeTransfer del dueño, SHA256 46948d37…, auditoría SUPERADA)

CONTENIDO DEL RELEASE
----------------------
1. crazypp-v3.zip                100.704.607 bytes → EL JUEGO COMPLETO V3.0.1
   (copia ESPEJO con nombre inequívoco para vencer cachés: crazypp-v3.0.1.zip,
   mismos bytes y mismo SHA256)
   - index.html 6.209.803 B: todo el juego en un solo archivo
     (V2.141 íntegra + módulo PRO TRAINING + fixes del casco V3.0.1)
   - assets/intro.mp4 + 4 campeonatos autocontenidos:
     La Locura v20 (eager) · Magia v28 · Salvaje Oeste v48 · Estación Orbital v5
   - SHA256: 208f9b2631dffd41c2cd72ad20798f723d76cbf00703358f4381a35b92bd20d1

   ✅ CÓMO COMPROBAR QUE TIENES LA BUILD NUEVA (sin mirar el zip):
   la portada 2D muestra «V3.0.1» en el pie (junto a Ko-fi) y TODAS las
   páginas del menú VR llevan el sello dorado «V3.0.1» bajo las palas de
   idioma. Si ves V3.0 (o nada), es la build antigua o una descarga cacheada.
"""

OLD_TAIL = """HISTORIAL DE TAMAÑOS
--------------------
  V2.124  5,31 MB · V2.141 100,67 MB (campeonatos con arte propio) ·
  V3.0    100,71 MB (+56 KB de módulo sobre V2.141)
"""

NEW_TAIL = """HISTORIAL DE TAMAÑOS
--------------------
  V2.124  5,31 MB · V2.141 100,67 MB (campeonatos con arte propio) ·
  V3.0    100,71 MB (+56 KB de módulo sobre V2.141) ·
  V3.0.1  100,70 MB (index 6.209.803 B — fixes del casco, ver ADDENDUM)
"""

def main():
    for p in PATHS:
        with open(p, encoding='utf-8') as f:
            txt = f.read()
        assert txt.count(OLD_HEAD) == 1, f'ancla cabecera no única en {p}'
        assert txt.count(OLD_TAIL) == 1, f'ancola historial no único en {p}'
        txt = txt.replace(OLD_HEAD, NEW_HEAD).replace(OLD_TAIL, NEW_TAIL)
        with open(p, 'w', encoding='utf-8') as f:
            f.write(txt)
        print('OK', p)

if __name__ == '__main__':
    main()
