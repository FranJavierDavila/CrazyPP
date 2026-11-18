#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r68_datos.py — FASE 162 · r68 · DATOS DEL ARCO Y LAS SECCIONES.
En c02_cfg_escena.js:
  · ICONOS_MENUS v1 → v2 (24 iconos: + audio, ojo, usuario, gauge, consola,
    plus, entrar).
  · CONFIG_MENUS v1 → v2: lienzo VIRTUAL 3696×1400 troceado en TRES
    panelas físicas en ARCO (L 0,74 · C 0,98 · R 0,74 × 0,95 m; centro a
    1,15 m, lados a 1,25 m, yaw ±36°) — pantalla casi completa equidistante;
    DOCK ELIMINADO; SALIR A LA WEB reubicado en TU CASA; héroe JUGAR
    prominente y Carrera al nivel del resto.
  · CONFIG_SECCIONES (nuevo): concha de los subapartados (título+icono+
    atrás data-driven por página) y la rejilla de AJUSTES (8 tarjetas-icono
    en dos columnas sobre las panelas C y R).
Cada sustitución es asertada (el bloque v1 debe existir UNA vez)."""
import json
import re
import sys
from pathlib import Path

SRC = Path('/home/z/my-project/upload/src/game')
C02 = SRC / 'core/c02_cfg_escena.js'
REG = json.loads(Path('/home/z/my-project/upload/scripts/iconos_v68.json')
                 .read_text(encoding='utf-8'))

icon_lines = []
for name, ent in REG['iconos'].items():
    icon_lines.append(f"    {name}: {{ src: '{ent['src']}', escala: {ent['escala']} }},")

BLOQUE = f'''/* =====================================================================
 *  r68 · FASE 162 · ICONOS_MENUS v2 — REGISTRO DE ICONOS (24)
 *  ---------------------------------------------------------------------
 *  «CRAZY ICONOS v1» ampliado con los 7 iconos de las secciones (audio,
 *  ojo, usuario, gauge, consola, plus, entrar). MISMO CONTRATO: cambiar
 *  un icono = sustituir su data-URI aquí — cero lógica. (v1: 17 iconos
 *  del Vestíbulo, r67.)
 *  ===================================================================== */
export const ICONOS_MENUS = {{
  version: 2,
  resolucion: 256,
  iconos: {{
__ICONOS__
  }},
}};
'''.replace('__ICONOS__', '\n'.join(icon_lines))

CONFIG_MENUS_V2 = '''\
/* =====================================================================
 *  r68 · FASE 162 · CONFIG_MENUS v2 — EL ARCO (pantalla casi completa)
 *  ---------------------------------------------------------------------
 *  Petición del dueño: «el menú debe ocupar prácticamente toda la
 *  pantalla… los 3 bloques equidistantes como si de una pantalla curva
 *  se tratase… el dock desaparece completo (solo reubicar Salir a la
 *  WEB)… el bloque central más protagonismo para el botón verde de
 *  Jugar y la escalera al nivel del resto».
 *  · LIENZO VIRTUAL 3696×1400 troceado en TRES panelas físicas en arco:
 *    centro 0,98 m a 1,15 m · lados 0,74 m a 1,25 m · yaw ±36° — las
 *    tres centros equidistantes del jugador (pantalla curva real).
 *  · Las páginas legadas 1024×1536 se pintan centradas (escala 0,911).
 *  · dock: ELIMINADO (v1 r67) — «salir a la web» vive como tarjeta
 *    fina al pie de TU CASA.
 *  ===================================================================== */
export const CONFIG_MENUS = {
  version: 2,
  lienzo: { ancho: 3696, alto: 1400 },
  arco: {
    yawGrados: 36,
    yCentro: -0.05,
    panelas: [
      { id: 'L', x: 0, w: 1112, anchoM: 0.74, altoM: 0.95, yaw: 36, dist: 1.25 },
      { id: 'C', x: 1112, w: 1472, anchoM: 0.98, altoM: 0.95, yaw: 0, dist: 1.15 },
      { id: 'R', x: 2584, w: 1112, anchoM: 0.74, altoM: 0.95, yaw: -36, dist: 1.25 },
    ],
  },
  cabecera: { logo: true, idiomas: true, cierre: true, sello: true },
  paneles: [
    { id: 'compite', tituloKey: 'vest_compite', x: 40, y: 250, w: 1032, h: 1100,
      tarjetas: [
        { id: 'tab:multi', icono: 'multijugador', etiquetaKey: 'hub_multi',
          gradiente: ['#ba58ff', '#7a1fd0'] },
        { id: 'page:champs', icono: 'campeonatos', etiquetaKey: 'sec_crazy',
          gradiente: ['#ffca1e', '#d88c00'] },
        { id: 'wrl:open', icono: 'ranking', etiquetaKey: 'sec_rank',
          gradiente: ['#1ed8cc', '#0a8892'] },
      ] },
    { id: 'jugar', tituloKey: 'vest_jugar', x: 1152, y: 250, w: 1392, h: 1100,
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
    { id: 'casa', tituloKey: 'vest_casa', x: 2624, y: 250, w: 1032, h: 1100,
      tarjetas: [
        { id: 'homehall', icono: 'vestibulo', etiquetaKey: 'hall_home_btn',
          gradiente: ['#7c94c4', '#3c5280'] },
        { id: 'tut:go', icono: 'academia', etiquetaKey: 'tut_hub',
          gradiente: ['#ffba2a', '#e27c00'] },
        { id: 'page:opts', icono: 'ajustes', etiquetaKey: 'opts_title',
          gradiente: ['#96a8c2', '#586884'] },
        { id: 'salirweb', icono: 'salir', etiquetaKey: 'dock_salir',
          gradiente: ['#5f7183', '#3a4754'], fino: true },
      ] },
  ],
};

/* =====================================================================
 *  r68 · FASE 162 · CONFIG_SECCIONES — CONCHA DE LOS SUBAPARTADOS
 *  ---------------------------------------------------------------------
 *  «Rediseño de todos los apartados y submenús interiores… reorganizados
 *  de forma coherente y muy clara… evita exceso de texto, preferir
 *  iconos gráficos» (dueño). La concha pinta en las TRES panelas: fondo
 *  de cristal continuo + botón ATRÁS con icono (panela L) + título con
 *  medallón (panela C) + palas de idioma (panela R) + sello. Las rejillas
 *  convierten páginas en tarjetas-icono data-driven (AJUSTES: 8 tarjetas
 *  en dos columnas sobre las panelas C y R). Las páginas complejas
 *  (teclados, sliders, tablas) conservan su mecánica íntegra y visten la
 *  concha nueva.
 *  ===================================================================== */
export const CONFIG_SECCIONES = {
  version: 1,
  shell: {
    multi: { tituloKey: 'tab_multi', icono: 'multijugador', volver: 'page:main' },
    join: { tituloKey: 'join_title', icono: 'entrar', volver: 'tab:multi' },
    name: { tituloKey: 'name_title', icono: 'usuario', volver: 'page:optsPerfil' },
    gripname: { tituloKey: 'pala_gname_title', icono: 'partido', volver: 'page:optsPala' },
    rank: { tituloKey: 'sec_rank', icono: 'ranking', volver: 'page:main' },
    rankme: { tituloKey: 'rankme_t', icono: 'usuario', volver: 'page:main' },
    champs: { tituloKey: 'sec_crazy', icono: 'campeonatos', volver: 'page:main' },
    champhist: { tituloKey: 'sec_crazy', icono: 'campeonatos', volver: 'page:champs' },
    opts: { tituloKey: 'opts_title', icono: 'ajustes', volver: 'page:main',
      rejilla: 'ajustes' },
    optsJuego: { tituloKey: 'cat_juego', icono: 'consola', volver: 'page:opts' },
    optsSala: { tituloKey: 'cat_sala', icono: 'vestibulo', volver: 'page:opts' },
    optsSonido: { tituloKey: 'cat_sonido', icono: 'audio', volver: 'page:opts' },
    optsVisual: { tituloKey: 'cat_visual', icono: 'ojo', volver: 'page:opts' },
    optsPerfil: { tituloKey: 'cat_perfil', icono: 'usuario', volver: 'page:opts' },
    optsRendi: { tituloKey: 'cat_rendi', icono: 'gauge', volver: 'page:opts' },
    optsPala: { tituloKey: 'cat_pala', icono: 'partido', volver: 'page:opts' },
    salirask: { tituloKey: 'salirask_title', icono: 'salir', volver: 'page:main' },
    hallask: { tituloKey: 'hallask_title', icono: 'vestibulo', volver: 'page:main' },
    tutask: { tituloKey: 'tut_hub', icono: 'academia', volver: 'page:main' },
    train: { tituloKey: 'sec_train', icono: 'entrenar', volver: 'page:main' },
    carrera: { tituloKey: 'carrera_lbl', icono: 'carrera', volver: 'page:main' },
  },
  rejillas: {
    ajustes: { columnas: ['C', 'R'], y: 300, h: 220, gap: 24,
      tarjetas: [
        { id: 'page:optsJuego', icono: 'consola', etiquetaKey: 'cat_juego',
          gradiente: ['#4caf50', '#2e7d32'] },
        { id: 'page:optsSala', icono: 'vestibulo', etiquetaKey: 'cat_sala',
          gradiente: ['#42a5f5', '#1565c0'] },
        { id: 'page:optsSonido', icono: 'audio', etiquetaKey: 'cat_sonido',
          gradiente: ['#7e57c2', '#4527a0'] },
        { id: 'page:optsVisual', icono: 'ojo', etiquetaKey: 'cat_visual',
          gradiente: ['#26a69a', '#00695c'] },
        { id: 'page:optsPerfil', icono: 'usuario', etiquetaKey: 'cat_perfil',
          gradiente: ['#ff7043', '#bf360c'] },
        { id: 'page:optsRendi', icono: 'gauge', etiquetaKey: 'cat_rendi',
          gradiente: ['#ffa726', '#e65100'] },
        { id: 'page:optsPala', icono: 'partido', etiquetaKey: 'cat_pala',
          gradiente: ['#ec407a', '#ad1457'] },
        { id: 'kofi', icono: 'apoyar', etiquetaKey: 'btn_kofi',
          gradiente: ['#ffd25e', '#e8a80e'] },
      ] },
  },
};
'''

t = C02.read_text(encoding='utf-8')

# 1 · sustituir ICONOS_MENUS v1 → v2
m = re.search(r'/\* =+\n \*  r67 · FASE 161 · ICONOS_MENUS[^\0]*?\n\};\n', t)
if not m:
    sys.exit('ABORTA: bloque ICONOS_MENUS v1 no hallado')
t = t[:m.start()] + BLOQUE + t[m.end():]

# 2 · sustituir CONFIG_MENUS v1 → v2 (+ CONFIG_SECCIONES)
m = re.search(r'/\* =+\n \*  r67 · FASE 161 · CONFIG_MENUS[^\0]*?\n\};\n', t)
if not m:
    sys.exit('ABORTA: bloque CONFIG_MENUS v1 no hallado')
t = t[:m.start()] + CONFIG_MENUS_V2 + t[m.end():]

C02.write_text(t, encoding='utf-8')

# verificaciones
t2 = C02.read_text(encoding='utf-8')
assert t2.count('export const CONFIG_MENUS') == 1
assert t2.count('export const CONFIG_SECCIONES') == 1
assert t2.count('export const ICONOS_MENUS') == 1
n = len(re.findall(r'data:image/png;base64,', t2))
assert n == 24, f'iconos embebidos: {n}'
assert 'dock: {' not in t2.split('CONFIG_SECCIONES')[0].split('CONFIG_MENUS')[1]
print('c02 OK: ICONOS_MENUS v2 (24) + CONFIG_MENUS v2 (arco, sin dock) + CONFIG_SECCIONES')
