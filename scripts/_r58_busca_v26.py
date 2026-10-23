#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Busca menciones de 'locura' con número de versión en los QA de versión
y manifiestos (para re-anclar v26 → v27 de la r58)."""
from pathlib import Path

for q in ('scripts/qa_version.py', 'scripts/qa_manifiestos.py'):
    t = Path(q).read_text(encoding='utf-8')
    lines = t.split('\n')
    for i, l in enumerate(lines):
        if 'locura' in l and ('26' in l or '27' in l):
            print(f'{q}:{i+1}: {l.strip()[:110]}')
        if "'locura'" in l and ':' in l:
            print(f'{q}:{i+1}: {l.strip()[:110]}')
