#!/usr/bin/env python3
"""release_v36209_close.py — cierre del release 3.6.209-SDK6.

El push de pages + backup ya están hechos (deploy_pages.py, sesión del
21-11-2026); esta pieza ejecuta SOLO la parte de release (do_release de
deploy_pages.py): tag v3.6.209-SDK6 + GitHub Release con los 4 ZIPs de
public/descargas. GIT_TOKEN por entorno (nunca en fichero).
"""
import sys

sys.path.insert(0, '/home/z/my-project/scripts')
import deploy_pages as dp

dp.do_release('3.6.209-SDK6')
