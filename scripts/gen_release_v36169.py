#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_release_v36169.py — FASE 174 · r78 · generador del release.
Re-sella scripts/release-v36168/build_zip.py → scripts/release-v36169/:
  · tokens de versión (v36168→v36169 · 3.6.168→3.6.169) + veto explícito
    de la versión anterior en el hub.
  · notas del release: FASE 173 → FASE 174 (MENÚS EN PROFUNDIDAD).
Auxiliares (mock_host.mjs · package.json · server.mjs · voz-alerta/) se
copian del kit v36168 intactos.
"""
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(os.environ.get('CPP_RAIZ') or '/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'release-v36168'
DESTINO = RAIZ / 'scripts' / 'release-v36169'

if not (ORIGEN / 'build_zip.py').exists():
    sys.exit('ABORTA: release-v36168/build_zip.py no existe')

t = (ORIGEN / 'build_zip.py').read_text(encoding='utf-8')

# 1 · notas FASE 173 → FASE 174 (ANTES de los tokens de versión)
ini = t.find("'Rama    : main · SDK6 (FASE 173")
fin = t.find("'  3.6.168\\n'")
if ini < 0 or fin < 0:
    sys.exit('ABORTA: bloque de notas FASE 173 no hallado')
fin += len("'  3.6.168\\n'")

NOTAS = """'Rama    : main · SDK6 (FASE 174 — MENÚS EN PROFUNDIDAD: «todos los\\n'
    'subniveles con el mismo tipo de maquetación ocupando todo el espacio\\n'
    'que tenemos ahora en los paneles… repasa los menús hasta su nivel más\\n'
    'profundo… nada de desbordamientos ni solapamientos» + «sala pública\\n'
    'en espera» + «interruptor del sistema de alertas»). CUATRO piezas:\\n'
    '  · MOTOR _menuBandas: las FILAS A PANEL COMPLETO del nivel 3+ — el\\n'
    '    mismo lenguaje de las rejillas (placa de museo + medallón +\\n'
    '    etiqueta + sub) para los controles profundos; altura repartida\\n'
    '    POR CUENTA (no desborda por construcción), texto que se encoge al\\n'
    '    ancho real y ids EXACTOS del despacho legado (interactividad\\n'
    '    intacta). Tipos: titulo · lectura · fila · filaN · grid · barra ·\\n'
    '    teclado · codigo.\\n'
    '  · MIGRADOS: las 11 páginas de AJUSTES (juego · sala · salaroom ·\\n'
    '    salamesa · salabola · salahall · sonido · visual · perfil · rendi\\n'
    '    · pala) y los 3 teclados (join · name · gripname) — ADIÓS a la\\n'
    '    tarjeta legada 1024×1536 (placa suprimida en todas). El candado\\n'
    '    de ARCANOS pasa al motor: una pieza pinta los 4 grids.\\n'
    '  · SALA PÚBLICA EN ESPERA: «Dejar en espera · MI CASA» deja la sala\\n'
    '    VIVA en segundo plano (net:espera); ATRÁS desde MULTIJUGADOR no\\n'
    '    la cierra; el Vestíbulo declara «SALA {c} EN ESPERA · pública»;\\n'
    '    la alerta de duelo avisa al anfitrión esté donde esté; cancelar\\n'
    '    sigue siendo cancelar.\\n'
    '  · SISTEMA DE ALERTAS: abierto para todos POR DEFECTO; AJUSTES ›\\n'
    '    JUEGO lo silencia (pp_alertas_v1) — sin quad, sin pitidos, sin\\n'
    '    voz; el duelo PENDIENTE se acepta desde MULTIJUGADOR.\\n'
    '  · QA: test_red_nucleo 60/0 · qa_vestibulo_r78 95/0 — NUEVAS checks\\n'
    '    EN VIVO: ids de las 14 páginas migradas, TODO dentro de la panela\\n'
    '    C y CERO SOLAPES par a par, botón «Dejar en espera» + chip «SALA\\n'
    '    AB12C EN ESPERA», alertas abiertas por defecto + regresión r77\\n'
    '    (túnel adaptativo/QoS), r76 (piso 72) y r75/r74 íntegra.\\n'
    '  · Ensamblado 12.265.139 B.\\n'
    '  SE CONSERVA TODO: r55-r77 íntegro (garantía de red, cadencia 72,\\n'
    '    la red en serio, escoger hall, candado global, multijugador en 3\\n'
    '    zonas, alerta de duelo, placa de museo, BOLA LOCA, Hall FASE 29,\\n'
    '    ELO, taller UGC, PWA, PRO TRAINING).\\n'
    '  · sellada a\\n'
    '  3.6.169\\n'"""

t = t[:ini] + NOTAS + t[fin:]

# 2 · tokens de versión (orden: el más largo primero)
for a, b in [('v36168-sdk6', 'v36169-sdk6'),
             ('V3.6.168-SDK6', 'V3.6.169-SDK6'),
             ('3.6.168-SDK6', '3.6.169-SDK6'),
             ('v36168', 'v36169'),
             ('3.6.168', '3.6.169')]:
    t = t.replace(a, b)

# 3 · veto explícito de la versión anterior en el hub
t = t.replace("'v36169-sdk6' not in hub",
              "'v36169-sdk6' not in hub or 'v36168-sdk6' in hub")

DESTINO.mkdir(exist_ok=True)
(DESTINO / 'build_zip.py').write_text(t, encoding='utf-8')
# TODO el kit auxiliar del release anterior, excepto el build_zip re-sellado
for f in ORIGEN.iterdir():
    if f.name == 'build_zip.py':
        continue
    d = DESTINO / f.name
    if f.is_dir():
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(f, d)
    else:
        shutil.copy2(f, d)

# verificación mínima: sin tokens viejos salvo los vetos deliberados
res = t.count('36168')
print(f'gen_release_v36169 OK → {DESTINO} (notas FASE 174 · vetos v36168: {res})')
