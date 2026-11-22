#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""release_backup_r83 — Release GitHub v3.6.75-SDK6 (4 ZIPs) + respaldo
main→proyecto, reutilizando las funciones de deploy_pages.py (la ronda r83
ya empujó pages FF a mano tras el rescate del linaje; el script original
abortó ANTES de la release y del backup).
El GIT_TOKEN llega por ENTORNO (nunca en ficheros commitables)."""
import os
import sys

sys.path.insert(0, '/home/z/my-project/scripts')
_PAT_FILE = '/home/z/my-project/scripts/worker-tele/.github-pat'
if os.path.exists(_PAT_FILE) and not os.environ.get('GIT_TOKEN'):
    os.environ.setdefault('GIT_TOKEN', open(_PAT_FILE).read().strip())
if not os.environ.get('GIT_TOKEN'):
    sys.exit('FALLO: exporta GIT_TOKEN en el entorno (el PAT nunca va en ficheros commitables)')

import deploy_pages as dp

dp.ensure_excluded()
# el HEAD ya es el commit r83 (main = 561d22e) y pages ya está empujado
dp.do_release(dp.detect_version())
print('— respaldo main → proyecto —')
dp.do_backup()
print('✓ Release + backup completados')
