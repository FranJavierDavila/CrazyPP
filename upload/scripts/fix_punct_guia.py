#!/usr/bin/env python3
"""Liga signos tipográficos a la palabra anterior para que ninguna línea empiece por — o ·"""
import re

P = '/home/z/my-project/download/guia-campeonatos-crazy-pingpong.html'
src = open(P, encoding='utf-8').read()

head, tail = src.split('</style>', 1)

# 1) La raya nunca abre línea: se liga a la palabra anterior
tail = tail.replace(' — ', '&nbsp;— ')

# 2) El punto medio nunca abre línea (etiquetas, pie, bandas, chuleta)
tail = tail.replace(' · ', '&nbsp;· ')

open(P, 'w', encoding='utf-8').write(head + '</style>' + tail)

n1 = tail.count('&nbsp;— ')
n2 = tail.count('&nbsp;· ')
print(f"rayas ligadas: {n1}, puntos medios ligados: {n2}")
