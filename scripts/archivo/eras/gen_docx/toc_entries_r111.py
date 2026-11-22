#!/usr/bin/env python3
"""Extrae los títulos H1/H2 del informe y produce el JSON de entradas del índice
(para add_toc_placeholders.py --entries). Estimación de página: igual heurística que el modo auto."""
import json
import sys
from docx import Document

doc = Document('/home/z/my-project/download/Auditoria_calidad_CrazyPP_r111.docx')
entries = []
page = 1
for i, para in enumerate(doc.paragraphs):
    estilo = para.style.name if para.style else ''
    if not estilo.startswith('Heading'):
        continue
    nivel = int(estilo.split()[-1]) if estilo.split()[-1].isdigit() else 0
    if nivel > 2:
        continue
    texto = para.text.strip()
    if not texto:
        continue
    page = max(1, 1 + i // 8)
    entries.append({'level': nivel, 'text': texto, 'page': str(page)})

print(json.dumps(entries, ensure_ascii=False))
