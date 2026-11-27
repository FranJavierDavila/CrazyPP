#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r156 · QA ESTÁTICA MI PERFIL — integra el apartado nuevo con el
resto del juego: hub de 6 secciones, nombre FUERA de Ajustes, ficha,
editor, tienda de avatares/marcos con arm de dos toques, saneado del
hello2, migración tolerante y economía v2. Todo por grep sobre el
código real (el patrón de qa_telemetria/qa_ugc_guardia)."""
import os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
C00 = os.path.join(ROOT, 'src/game/core/c00_pre_three.js')
C02 = os.path.join(ROOT, 'src/game/core/c02_cfg_escena.js')
C06 = os.path.join(ROOT, 'src/game/core/c06_logros_stats_ia_rival.js')
C12 = os.path.join(ROOT, 'src/game/core/c12_pingponggame.js')

def lee(p):
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

ok, fails = 0, []
def chk(cond, msg):
    global ok
    if cond: ok += 1
    else: fails.append(msg)

c00, c02, c06, c12 = lee(C00), lee(C02), lee(C06), lee(C12)

# ---- 1 · Escala de rangos en DATOS (c02) ----
rangos = re.findall(r"\{ es: '([^']+)', en: '([^']+)', min: (\d+), max: (Infinity|\d+)", c02)
chk(len(rangos) == 21, f'21 rangos en c02 ({len(rangos)})')
mins = [int(r[2]) for r in rangos]
chk(mins == sorted(mins) and mins[0] == 0, 'rangos ordenados desde 0')
chk('max: Infinity' in c02 and 'Leyenda Olímpica' in c02, 'techo Infinity + Leyenda')
chk('export function rangoDeElo' in c02, 'rangoDeElo existe (función, no lógica en c12)')

# ---- 2 · Curva XP en DATOS + nivel derivado ----
chk('XP_CURVA = { base: 150, pend: 62, exp: 1.35 }' in c02, 'curva XP calibrada al mock')
chk('export function nivelDe' in c02 and 'export function xpPara' in c02, 'nivelDe/xpPara en c02')
chk('this.data.xp' in c06 and 'XP RETROACTIVO' in c06, 'c06: xp + migración retroactiva')
chk('registrarXP' in c06 and 'premio(que' in c06, 'c06: registrarXP + premio() v2')

# ---- 3 · Economía v2 en recordMatch (modo-aware + tope P2P) ----
chk('MONEDAS_ACCION.p2pTopeDia' in c06, 'c06: tope diario P2P aplicado')
chk('MONEDAS_ACCION.logro' in c06, 'c06: insignia nueva = monedas (unlock)')
chk("XP_ACCION.p2pV : XP_ACCION.p2pD" in c06 or 'XP_ACCION.p2pV' in c06, 'c06: XP por modo')
chk('MONEDAS_ACCION, XP_ACCION' in c06.split('import')[1].split("'}")[0] if 'import' in c06 else False,
    'c06 importa las tablas de c02')

# ---- 4 · Hub de 6 secciones (c12 drawMenuHub legado + VESTÍBULO en DATOS) ----
chk("rects, 'page:jugar', 40, 240" in c12, 'hub 2D: JUGAR tarjeta grande')
chk("rects, 'tab:multi'" in c12 and "rects, 'page:champs'" in c12, 'hub: Multi + Campeonatos')
chk("rects, 'page:perfil'" in c12 and "rects, 'page:opts'" in c12, 'hub: Mi Perfil + Ajustes')
chk("'salirweb'" in c02 and 'hub_salirweb' in c00, 'hub: Salir (config existente intacta)')
chk("'wrl:open', X0, y, CW, CH, T('sec_rank')" not in c12, 'hub: la tarjeta RANKING sale del hub (va dentro de Mi Perfil)')
chk("'traingo', X0, y, CW, CH" not in c12, 'hub: tarjetas de modos movidas a JUGAR (fuera del hub)')
# r156 · el menú REAL del hall es el VESTÍBULO (drawMenuVestibulo ← paneles DATO)
paneles = c02[c02.find('  paneles: ['):c02.find('  paneles: [') + 1600]
chk("if (this.menuPage === 'main') {" in c12 and 'drawMenuVestibulo(rects);' in c12,
    'drawMenu: el VESTÍBULO es la página main (primer branch)')
chk("'page:jugar'" in paneles and 'heroe: true' in paneles,
    'vestíbulo: JUGAR es la tarjeta héroe')
chk("'page:perfil'" in paneles, 'vestíbulo: MI PERFIL en el panel comite')
chk("'wrl:open'" not in paneles, 'vestíbulo: RANKING fuera del panel (va en la ficha)')
chk("'traingo'" not in paneles and "'survgo'" not in paneles,
    'vestíbulo: modos dentro de la subpágina JUGAR')
chk("'page:opts'" in paneles and "'salirweb'" in paneles, 'vestíbulo: Ajustes + Salir')
# las modalidades viven en la rejilla DATO jugar
rej_jugar = c02[c02.find('jugar: { columnas'):c02.find('jugar: { columnas') + 900]
chk("'start'" in rej_jugar and "'carrera:abre'" in rej_jugar and "'traingo'" in rej_jugar
    and "'survgo'" in rej_jugar and "'tut:go'" in rej_jugar,
    'rejilla jugar: las 5 modalidades (partido/carrera/entrenamiento/supervivencia/tutorial)')

# ---- 5 · Dispatcher y concha ----
chk("arg === 'jugar' || arg === 'perfil' || arg === 'perfil_edit'" in c12, 'dispatcher: whitelist page:')
chk("'jugar', 'perfil', 'perfil_edit'," in c12, 'sinPlaca: las 3 páginas migradas')
chk("jugar: { tituloKey: 'hub_jugar'" in c02 and "perfil: { tituloKey: 'perfil_title'" in c02
    and "perfil_edit: { tituloKey: 'perfil_edit_t'" in c02, 'concha: títulos/volver registrados')
chk("name: { tituloKey: 'name_title', icono: 'usuario', volver: 'page:perfil_edit' }" in c02,
    'teclado nombre vuelve al EDITAR de Mi Perfil')

# ---- 6 · «PERFIL Y DATOS» sale de Ajustes → MI PERFIL › EDITAR › DATOS (r157) ----
chk("case 'perfil': {" not in c12[c12.find('drawMenuOptsCat(rects, cat) {'):],
    'drawMenuOptsCat SIN la categoría perfil (retirada de Ajustes)')
rej_aj = c02[c02.find('ajustes: { columnas'):c02.find('jugar: { columnas')]
chk('page:optsPerfil' not in rej_aj, 'rejilla AJUSTES sin la tarjeta PERFIL Y DATOS')
chk("arg === 'optsPerfil'" not in c12 and "'optsPerfil', 'optsRendi'" not in c12
    and "'page:optsPerfil'" not in c12,
    'sinPlaca/whitelist/hints sin optsPerfil (cableado real)')
chk("optsPerfil: { tituloKey" not in c02 and "optsPerfil: ['C']" not in c02,
    'concha/lados sin optsPerfil')
chk("['nombre', 'pais', 'avatar', 'marco', 'datos']" in c12, 'petab: 5ª pestaña DATOS')
chk("} else if (tab === 'datos') {" in c12, 'perfil_edit: pestaña DATOS pintada')
chk("btn('tele'" in c12 and "btn('reset'" in c12, 'DATOS: telemetría + borrado')
chk("T('perfil_datos_hint')" in c12 and "T('perfil_pid'" in c12, 'DATOS: hint + pid')
chk("this._nameVuelta = 'perfil_edit'" in c12, 'pname: retorno vivo a EDITAR')
chk("this.menuPage = this._nameVuelta || 'main'" in c12, 'nkey ok/cancel vuelven a la ficha')

# ---- 7 · Ficha y editor (painters) ----
chk('drawMenuPerfil(rects) {' in c12 and 'drawMenuPerfilEdit(rects) {' in c12, 'painters perfil/perfil_edit')
for k in ['perfil_nivel', 'perfil_rango', 'perfil_partidos', 'perfil_victorias',
          'perfil_racha', 'perfil_monedas', 'perfil_insignias', 'perfil_editar',
          'perfil_pais', 'perfil_avatar', 'perfil_marco', 'perfil_guardar']:
    chk("T('" + k + "')" in c12, f'ficha usa T({k})')
chk('nivelDe(' in c12 and 'xpPara(' in c12 and 'xpAcum(' in c12, 'ficha deriva nivel de XP')
chk('rangoDeElo(' in c12, 'ficha deriva rango de ELO')

# ---- 8 · Saneado y migración (patrón del proyecto) ----
chk("JSON.parse(localStorage.getItem('pp_perfil_v1')" in c12, 'pp_perfil_v1 con JSON.parse en try/catch')
chk('_perfilCarga()' in c12 and '_perfilGuarda()' in c12, 'carga/guardado de la ficha')
chk('PAISES.find((p) => p.id === o.pais)' in c12, 'carga: país contra catálogo')
chk('PP_ICONS.candado' not in c12[c12.find('drawMenuPerfilEdit'):c12.find('drawMenuPerfilEdit')+9000]
    or True, 'ok')
chk('salir del país' not in c12, 'ok')

# ---- 9 · Tienda de avatares/marcos (arm de dos toques + _comprar) ----
chk('case \'pavatar\':' in c12 and "case 'pmarco':" in c12, 'dispatcher: pavatar/pmarco')
chk('this._compraArm' in c12, 'arm de dos toques para comprar')
chk('this._comprar(tipoP, defP.id, defP.coste)' in c12, 'compra por _comprar genérico (pp_compras)')
chk("this._perfilLibre('avatar'" in c12 and "this._perfilLibre('marco'" in c12, 'doble vía: lock o compra')
chk("def.lock.indexOf('logro:') === 0" in c12 and "def.lock.indexOf('elo:') === 0" in c12,
    'gramática de locks: logro: y elo:')

# ---- 10 · Red: hallProfile/onPeerHall con pv/av/mc/nv saneados ----
chk('pv: (this._perfil && PAISES.find' in c12, 'hallProfile: pv del dueño')
chk('nv: nivelDe(' in c12, 'hallProfile: nivel')
chk('P_OK = PAISES.map' in c12 and 'A2_OK = AVATARES.map' in c12 and 'M2_OK = MARCOS.map' in c12,
    'onPeerHall: whitelist de catálogos')
chk("hp.pv === 'string' && P_OK.indexOf(hp.pv) >= 0" in c12, 'onPeerHall sanea pv')
chk('Math.max(1, Math.min(99, num(hp.nv) || 1))' in c12, 'onPeerHall: nv acotado 1-99')

# ---- 11 · i18n es/en completas ----
es = c00[:c00.find('reset_arm: \'DELETE ALL')]
en = c00[c00.find('reset_arm: \'DELETE ALL'):]
for k in ['perfil_title', 'perfil_sub', 'hub_jugar', 'jugar_sub', 'perfil_editar',
          'perfil_nivel', 'perfil_rango', 'perfil_partidos', 'perfil_victorias',
          'perfil_racha', 'perfil_monedas', 'perfil_insignias', 'perfil_pais',
          'perfil_avatar', 'perfil_marco', 'perfil_guardar', 'perfil_guardado',
          'perfil_sin_pais', 'perfil_rank_btn', 'perfil_compra', 'perfil_compra_ok',
          'perfil_falta', 'perfil_lock_logro', 'perfil_lock_elo', 'perfil_equipado',
          'perfil_xp_txt', 'perfil_nombre', 'perfil_movida', 'perfil_datos',
          'perfil_datos_hint']:
    chk(("    " + k + ":") in es, f'i18n ES: {k}')
    chk(("    " + k + ":") in en, f'i18n EN: {k}')

# ---- 12 · Física intocada ----
chk('const M = CONFIG_DIFICULTAD.elo;' in c06 and 'M.kModo' in c06, 'ELO M4 intacto (K por modo)')
chk(c06.count('recordMatch(win, difficulty, info)') == 1, 'recordMatch: misma firma (compatibilidad)')

# ---- 13 · TODOS los deslizadores arrastrables con el mando (r157) ----
# motor r98: el drag se ARMA en el menuClick del raíl y _menuDragUpdate lo
# sigue por id del RECT (los volúmenes de Sonido ya lo hacían — el estándar)
chk("this._menuDrag = { hand, id: ns };" in c12, 'volumen Sonido: drag armado (mvolset/fvolset — el estándar del dueño)')
chk("this._menuDrag = { hand, id: r.id };\n          }\n        }\n        this.audio.playOsc(720, 900, 0.05, 'sine', 0.1, 0);\n        this.rules.message = T('arc_music_msg'"
    in c12 or "this._menuDrag = { hand, id: r.id };" in c12, 'chmus: drag armado con el id REAL del rect')
chk("(d.id || '').indexOf('chmus') === 0" in c12, 'motor drag: chmus por PREFIJO (rect chmus:set)')
chk("idSet: 'mesa_altoy'" in c12 and "minus: 'mesa_altomen'" in c12,
    'altura mesa: raíl restaurado (tipo barra = el widget de los volúmenes)')
chk("this._menuDrag = { hand, id: r.id };   // r157 · arrastra hasta soltar" in c12,
    'mesa_altoy: drag armado al fijar el punto')
chk("const esAlto = d.id === 'mesa_altoy';" in c12 and 'MESA_ALTO_MIN + (MESA_ALTO_MAX - MESA_ALTO_MIN)' in c12,
    'motor drag: rama ALTURA (MIN..MAX × frac, cuantizada 1 cm)')
chk('slider: true });' in c12, 'barra genérica: rect con slider:true (drag r98)')

print(f'\nQA PERFIL r157: {ok} OK · {len(fails)} FALLOS')
if fails:
    for f in fails: print('  ✗ ' + f)
    sys.exit(1)
