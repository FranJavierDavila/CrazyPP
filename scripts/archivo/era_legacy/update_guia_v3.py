#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Guía de campeonatos → V3.0: marcadores de versión + callout de novedad."""
import io

P = '/home/z/my-project/public/descargas/guia-campeonatos-crazy-pingpong.html'
s = io.open(P, encoding='utf-8').read()

# 1) marcadores de versión (4: title, cover-tag, footer-span, e-id)
n = s.count('V2.124')
assert n == 4, f"esperaba 4 marcadores, hay {n}"
s = s.replace('V2.124', 'V3.0')

# 2) callout de novedad V3.0 tras el párrafo de introducción
ancla = 'sin tocar los cimientos ni las habitaciones que ya están amuebladas.</p>'
assert s.count(ancla) == 1, "ancla del callout no única"
callout = ancla + '''

  <div class="callout">
    <div class="c-t">&#10024; Novedad en el juego &mdash; la V3.0 &laquo;PRO TRAINING&raquo;</div>
    <p>La versión actual del juego, la <strong>V3.0</strong>, estrena un <strong>centro de entrenamiento</strong> con cinco &aacute;reas profesionales (direcci&oacute;n, altura, efecto, saque y ritmo), feedback t&eacute;cnico en VR y pieles de pala desbloqueables. Vive en su propio m&oacute;dulo y <strong>no toca a los campeonatos</strong>: todo lo que cuenta esta gu&iacute;a &mdash;las tres zonas, el Taller, el Laboratorio y el Estadio&mdash; funciona exactamente igual que antes.</p>
  </div>'''
s = s.replace(ancla, callout)

io.open(P, 'w', encoding='utf-8').write(s)
print('guía HTML → V3.0 OK (4 marcadores + callout)')
