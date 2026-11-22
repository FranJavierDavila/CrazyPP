#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fusiona_informe.py — portada + cuerpo → PDF final en download/ con metadatos."""
from pypdf import PdfReader, PdfWriter

A4_W, A4_H = 595.28, 841.89
CUBIERTA = '/home/z/my-project/scripts/auditoria_cover.pdf'
CUERPO = '/home/z/my-project/scripts/auditoria_body.pdf'
FINAL = '/home/z/my-project/download/Auditoria_Fisicas_Guardianes_Ecosfera_r56.pdf'


def normaliza(page):
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    if abs(w - A4_W) > 0.1 or abs(h - A4_H) > 0.1:
        page.scale_to(A4_W, A4_H)
    return page


w = PdfWriter()
w.add_page(normaliza(PdfReader(CUBIERTA).pages[0]))
for p in PdfReader(CUERPO).pages:
    w.add_page(normaliza(p))
w.add_metadata({
    '/Title': 'Auditoría de físicas — Guardianes de la Ecosfera (CRAZY PING PONG · r56 · FASE 150)',
    '/Author': 'Z.ai',
    '/Creator': 'Z.ai',
    '/Subject': 'Auditoría de solo lectura del núcleo de simulación física en 8 ítems, con evidencia y recomendaciones',
})
with open(FINAL, 'wb') as f:
    w.write(f)
print('FINAL OK →', FINAL, '· páginas:', len(w.pages))
