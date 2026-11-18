#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r67_datos.py — FASE 161 · r67 · DATOS DEL VESTÍBULO.
Inyecta en la fuente (src/game/, NO en el ensamblado):
  · c02_cfg_escena.js → ICONOS_MENUS (registro de 17 iconos base64 del set
    «CRAZY ICONOS v1», intercambiables sin tocar código) + CONFIG_MENUS
    (layout del Vestíbulo: cabecera, 3 paneles, dock — ids de acción,
    iconos, gradientes; reordenar/recolorar/cambiar icono = editar datos).
  · c00_pre_three.js → claves i18n vest_*/dock_* en ES y EN.
Cada ancla se comprueba ÚNICA (count==1) o ABORTA sin escribir (estilo casa).
"""
import json
import re
import sys
from pathlib import Path

SRC = Path('/home/z/my-project/upload/src/game')
C02 = SRC / 'core/c02_cfg_escena.js'
C00 = SRC / 'core/c00_pre_three.js'
JSON_IC = Path('/home/z/my-project/upload/scripts/iconos_v67.json')

reg = json.loads(JSON_IC.read_text(encoding='utf-8'))

# ---------------------------------------------------------------- c02 · datos
# CONFIG_MENUS — layout del Vestíbulo (canvas 2560×1440). Los ids de acción
# son los del despachador de c12 (intactos). gradiente = [claro, oscuro].
config_menus = '''\
/* =====================================================================
 *  r67 · FASE 161 · ICONOS_MENUS — REGISTRO DE ICONOS DEL VESTÍBULO
 *  ---------------------------------------------------------------------
 *  Set «CRAZY ICONOS v1»: 17 iconos diseñados a mano (SVG → PNG 256 px
 *  cuantizado a 64 colores) bajo un sistema común — glifo blanco con
 *  sub-trazo oscuro, acento con degradado del color de su tarjeta y
 *  brillo especular. CÓMO PERSONALIZAR UN ICONO: sustituye el campo src
 *  por otra data-URI (o cambia escala) — el render lo lee AQUÍ, sin
 *  tocar una línea de lógica. Añadir icono nuevo = añadir fila.
 *  ===================================================================== */
export const ICONOS_MENUS = {
  version: 1,
  resolucion: 256,
  iconos: {
__ICONOS__
  },
};

/* =====================================================================
 *  r67 · FASE 161 · CONFIG_MENUS — ÚNICA FUENTE DE VERDAD DEL VESTÍBULO
 *  ---------------------------------------------------------------------
 *  La página principal del menú ('main') se pinta AQUÍ como DATOS (mismo
 *  contrato que CONFIG_MENU/ARCANO_CFG): lienzo, cabecera, los TRES
 *  paneles (compite · jugar · casa) con sus tarjetas y el dock de
 *  utilidades. Los ids son los del despachador de c12; los subtítulos
 *  vivos los resuelve c12 (_vestSubPorId) con las expresiones del HUB.
 *  · Reordenar tarjetas / paneles: mover filas aquí.
 *  · Recolorar: editar gradiente [claro, oscuro].
 *  · Cambiar icono: editar icono (nombre de ICONOS_MENUS).
 *  · heroe: tarjeta a toda fila en grande · par: media fila (2 por línea).
 *  ===================================================================== */
export const CONFIG_MENUS = {
  version: 1,
  lienzo: { ancho: 2560, alto: 1440 },
  cabecera: { x: 850, y: 56, w: 860, h: 150, idiomas: true },
  paneles: [
    { id: 'compite', tituloKey: 'vest_compite', x: 110, y: 246, w: 680, h: 950,
      tarjetas: [
        { id: 'tab:multi', icono: 'multijugador', etiquetaKey: 'hub_multi',
          gradiente: ['#ba58ff', '#7a1fd0'] },
        { id: 'page:champs', icono: 'campeonatos', etiquetaKey: 'sec_crazy',
          gradiente: ['#ffca1e', '#d88c00'] },
        { id: 'wrl:open', icono: 'ranking', etiquetaKey: 'sec_rank',
          gradiente: ['#1ed8cc', '#0a8892'] },
      ] },
    { id: 'jugar', tituloKey: 'vest_jugar', x: 850, y: 246, w: 860, h: 950,
      tarjetas: [
        { id: 'start', icono: 'partido', etiquetaKey: 'hub_play',
          gradiente: ['#4af05e', '#189e2c'], heroe: true },
        { id: 'carrera:abre', icono: 'carrera', etiquetaKey: 'carrera_lbl',
          gradiente: ['#ff4ad6', '#c60898'] },
        { id: 'traingo', icono: 'entrenar', etiquetaKey: 'sec_train',
          gradiente: ['#3aacff', '#0c60d6'], par: true },
        { id: 'survgo', icono: 'supervivencia', etiquetaKey: 'sec_surv',
          gradiente: ['#ff6026', '#d02c00'], par: true },
      ] },
    { id: 'casa', tituloKey: 'vest_casa', x: 1770, y: 246, w: 680, h: 950,
      tarjetas: [
        { id: 'homehall', icono: 'vestibulo', etiquetaKey: 'hall_home_btn',
          gradiente: ['#7c94c4', '#3c5280'] },
        { id: 'tut:go', icono: 'academia', etiquetaKey: 'tut_hub',
          gradiente: ['#ffba2a', '#e27c00'] },
        { id: 'page:opts', icono: 'ajustes', etiquetaKey: 'opts_title',
          gradiente: ['#96a8c2', '#586884'] },
      ] },
  ],
  dock: { x: 340, y: 1226, w: 1880, h: 170,
    items: [
      { id: 'docktv', icono: 'tv', etiquetaKey: 'dock_tv' },
      { id: 'dockintro', icono: 'intro', etiquetaKey: 'dock_intro' },
      { id: 'dockpwa', icono: 'instalar', etiquetaKey: 'dock_instalar' },
      { id: 'dockkofi', icono: 'apoyar', etiquetaKey: 'dock_apoyar' },
      { id: 'salirweb', icono: 'salir', etiquetaKey: 'dock_salir' },
    ] },
};
'''

icon_lines = []
for name, ent in reg['iconos'].items():
    icon_lines.append(f"    {name}: {{ src: '{ent['src']}', escala: {ent['escala']} }},")
block_c02 = config_menus.replace('__ICONOS__', '\n'.join(icon_lines))

t = C02.read_text(encoding='utf-8')
ANCHOR_C02 = ('};\n\n/* =====================================================================\n'
              ' *  r59 · FASE 153 · CONFIG_AUDIO')
if t.count(ANCHOR_C02) != 1:
    sys.exit(f'ABORTA: ancla c02 count={t.count(ANCHOR_C02)} (esperaba 1)')
t = t.replace(ANCHOR_C02, '};\n\n' + block_c02 + '\n/* =====================================================================\n'
              ' *  r59 · FASE 153 · CONFIG_AUDIO')
C02.write_text(t, encoding='utf-8')
print('c02 OK: ICONOS_MENUS + CONFIG_MENUS inyectados tras CONFIG_MENU')

# ---------------------------------------------------------------- c00 · i18n
ES_KEYS = """\
    // r67 · FASE 161 · EL VESTÍBULO (títulos de paneles + dock)
    vest_jugar: 'JUGAR',
    vest_compite: 'COMPITE',
    vest_casa: 'TU CASA',
    dock_tv: 'TV en vivo',
    dock_intro: 'Intro',
    dock_instalar: 'Instalar',
    dock_apoyar: 'Apoyar',
    dock_salir: 'Salir a la web',
"""
EN_KEYS = """\
    // r67 · FASE 161 · THE LOBBY (panel titles + dock)
    vest_jugar: 'PLAY',
    vest_compite: 'COMPETE',
    vest_casa: 'YOUR HOME',
    dock_tv: 'Live TV',
    dock_intro: 'Intro',
    dock_instalar: 'Install',
    dock_apoyar: 'Support',
    dock_salir: 'Exit to web',
"""
t0 = C00.read_text(encoding='utf-8')
for ancla, keys, nombre in [
    ("    hub_play: '\u25b6 JUGAR',", ES_KEYS, 'ES'),
    ("    hub_play: '\u25b6 PLAY',", EN_KEYS, 'EN'),
]:
    if t0.count(ancla) != 1:
        sys.exit(f'ABORTA: ancla i18n {nombre} count={t0.count(ancla)} (esperaba 1)')
    t0 = t0.replace(ancla, ancla + '\n' + keys.rstrip('\n'))
C00.write_text(t0, encoding='utf-8')
print('c00 OK: claves vest_*/dock_* inyectadas en ES y EN')

# ---------------------------------------------------------------- verificación
t2 = C02.read_text(encoding='utf-8')
assert 'export const CONFIG_MENUS' in t2 and 'export const ICONOS_MENUS' in t2
assert t2.count('export const CONFIG_MENUS') == 1
assert len(re.findall(r"data:image/png;base64,", t2)) == len(reg['iconos'])
print(f'VERIFICADO: c02 con {len(reg["iconos"])} iconos embebidos · CONFIG_MENUS único')
