#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Busca los stubs reales de Math.random y las agujas del manifest v26."""
from pathlib import Path

for q, pat in [('scripts/qa_portal_v3642.py', 'Math.random'),
               ('scripts/qa_superpoderes_v3643.py', 'Math.random'),
               ('scripts/qa_descargas_v365.py', 'v26'),
               ('scripts/qa_descargas_v365.py', '26')]:
    t = Path(q).read_text(encoding='utf-8')
    lines = t.split('\n')
    vistos = set()
    for i, l in enumerate(lines):
        if pat in l and l.strip() not in vistos:
            vistos.add(l.strip())
            print(f'{q}:{i+1}: {l.strip()[:105]}')
    print('---')
