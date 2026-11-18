#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r58_menu_salir.py — FASE 152 · SELLADO VIVO a 3.6.149-SDK6.

CONFIG_MENU · MENÚ DATA-DRIVEN + BOTÓN «SALIR A LA WEB» (petición del
dueño: «Colocar un botón desde el Menú principal para cerrar el juego y
salir a la web principal» · «seguir extendiendo el patrón data-driven a
otro subsistemas»):

  · CONFIG_MENU (c02, patrón ARCANO_CFG r55) — ÚNICA FUENTE DE VERDAD DE
    LA SALIDA: id/etiquetas (claves i18n)/gradiente/icono/confirmación/
    telemetría/destino/guardia XR como DATOS. Cambiar la tarjeta es
    editar la tabla, sin tocar lógica.
  · Tarjeta en el HUB (c12, pie, ancho completo 96 px, gris acero) bajo
    el reto diario y antes del cierre — dibujada DESDE los datos con el
    _modeCard existente + resolutor de iconos por nombre (_iconoDeMenu,
    icono «salir» dibujado: puerta con flecha).
  · Página de confirmación «¿SALIR A LA WEB?» (gemela del PROMPT B del
    hall, textos desde CONFIG_MENU.salir.confirmacion; B cancela).
  · salirALaWeb() — la ÚNICA puerta: telemetría 'salir_web' con flush
    síncrono (sendBeacon/keepalive) → session.end() con guardia de 2 s
    (dato tiempoMaxEsperaXRms) → location.assign(urlDestino), donde
    'AUTO_ORIGIN' resuelve la web principal SIN dominios hardcodeados:
    location.origin + la ruta sin game.html (vale en Pages, espejo
    local y cualquier dominio).
  · i18n es/en simétricos (hub_salirweb*, salirask_*, hint_salirweb) +
    tooltip 'salirweb' en el mapa EXACT de c12.

Este sellador (patrón sella_r57_auditoria_fisica; golden VIEJO capturado
ANTES de sobrescribir):
  · VERSION.json → 3.6.149-SDK6 · FASE 152 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden Y hashes de contrato
    (c00/c02/c12) en test_r*.mjs + qa_sup1_v366.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r58_menu_salir.py
"""
import glob
import hashlib
import importlib.util
import json
import re
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
VIEJA, NUEVA = '3.6.148-SDK6', '3.6.149-SDK6'
FASE_VIEJA, FASE_NUEVA = 151, 152
VIEJO_NOMBRE = ('Auditoría de físicas r57 aplicada: R1 pala mide con la base temporal '
                'de la física (PASO_TUNE c12) · R2 golden c05 (16 escenarios) + margen '
                'de bote alineado en los 3 simuladores · R3 Magnus ×1 predicho vs '
                '×2,2 documentado')
NOMBRE = ('CONFIG_MENU r58: menú data-driven + botón SALIR A LA WEB en el HUB '
          '(confirmación desde datos · telemetría salir_web con flush síncrono · '
          'session.end() con guardia 2 s · AUTO_ORIGIN sin dominios hardcodeados)')

# Hashes de contrato: COMPLETOS antes → después (los tests comparan el sha256
# entero, no sólo el prefijo) + prefijos al final. Esta fase toca c00 (i18n),
# c02 (CONFIG_MENU) y c12 (HUB/prompt/despachador/salida). c04/c05 intactos.
# Los VIEJOS: c02 y c12 son los NUEVOS del sellador r57 (vivos en los tests);
# c00 viene de git HEAD (sha256 verificado antes de sellar).
HASHES_VIEJOS_NUEVOS = [
    # c00_pre_three.js (i18n es/en)
    ('45aeb64c946a4ada3363f1960599c88b7ff5d9e06eb27b33ac7dd620c0d0682a',
     '33d33f57bdff238976fb6f63a7b1c801234fb605babba66d521a516abde1b81d'),
    # c02_cfg_escena.js (CONFIG_MENU)
    ('24a3c7786f9ad387fbd78c3e95fe51aef754f8620f7baf7438d884941519ba75',
     'c5669e5b14cb56d2e7fc42dd1737e09bcbd720dd0853431e14445bbb3f97f704'),
    # c12_pingponggame.js (HUB + salirask + despachador + salirALaWeb)
    ('515b5febafde44df99e627dcc16750b4cbcb678a799764c51a8a841e511eb4c2',
     '990974a6c8c2d990298b81c0d09fb683e4fe2284b59d1a245360b23bc2ee5656'),
]

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO r58 · CONFIG_MENU (el ensamblador quita el prefijo export)
    ('const CONFIG_MENU = {', 1),
    ("id: 'salirweb',", 1),
    ("urlDestino: 'AUTO_ORIGIN',", 1),
    ('tiempoMaxEsperaXRms: 2000,', 1),
    ("eventoTelemetria: 'salir_web',", 1),
    ('cerrarSesionXR: true,', 1),
    ('confirmacion: {', 1),
    # NUEVO r58 · tarjeta en el HUB + icono por nombre
    ('const SALIRCFG = CONFIG_MENU.salir;', 1),
    ('this._iconoDeMenu(SALIRCFG.icono), false);', 1),
    ('_iconoDeMenu(nombre) {', 1),
    ('_iconoSalir(c, cx, cy) {', 1),
    # NUEVO r58 · página de confirmación + despachador + la única puerta
    ('drawMenuSalidaAsk(rects) {', 1),
    ("btn('salirweb_si', 132, 470, 760, 170,", 1),
    ("btn('salirweb_no', 132, 700, 760, 170,", 1),
    ("case 'salirweb':", 1),
    ("case 'salirweb_si':", 1),
    ("case 'salirweb_no':", 1),
    ('async salirALaWeb() {', 1),
    ('this.renderer.xr.getSession()', 2),   # r58 salida + la preexistente (captura 5959)
    ("window.location.pathname.replace(/game\\.html$/, '')", 1),
    ("window.__PP_TELE.ev(S.eventoTelemetria, {});", 1),
    ('window.__PP_TELE.flush(true);', 1),
    ("'salirweb': 'hint_salirweb',", 1),
    # NUEVO r58 · i18n es/en
    ("hub_salirweb: 'SALIR A LA WEB',", 1),
    ("hub_salirweb: 'EXIT TO WEB',", 1),
    ("salirask_yes_btn: 'SÍ, SALIR',", 1),
    ("salirask_yes_btn: 'YES, EXIT',", 1),
    # CONSERVACIÓN r57 · R1 PASO_TUNE (pala con la base temporal de la física)
    ('const PASO_TUNE = { uiMax: 1 / 30, fisMax: 1 / 12 };', 1),
    ('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);', 1),
    ('const dtFis = Math.min(_rawDt, PASO_TUNE.fisMax);', 1),
    ('updatePaddleSim(ps, grip.position, tmpMountQ, now, dtFis);', 1),
    ('r57 · CONTRATO (auditoría R1)', 1),
    # CONSERVACIÓN r57 · R2 margen de bote ALINEADO en los 3 simuladores
    ('DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 &&', 3),
    ('r57 · AUDITORÍA R2: el margen de bote en X', 1),
    # CONSERVACIÓN r57 · R3 Magnus ×1 predicho vs ×2,2 real
    ('r57 · AUDITORÍA R3: el ×2,2 sólo vuela en la bola MARCADA', 1),
    ('DIMS.efectoMagnusMul || 1.5', 1),
    # CONSERVACIÓN r56 · BOTE_TUNE (c04) + BOLA_TUNE (c12)
    ('const BOTE_TUNE = {', 1),
    ('spinDecayBote: 0.72,', 1),
    ('gripImpactRef: 4.5,', 1),
    ('cascaronInercia: 0.4,', 1),
    ('cascaronAcoplo: 1.5,', 1),
    ('omegaLerp: 0.5,', 1),
    ('omegaDecay: 8,', 1),
    ('spin.multiplyScalar(BOTE_TUNE.spinDecayBote);', 1),
    ('impact / BOTE_TUNE.gripImpactRef', 1),
    ('BOTE_TUNE.cascaronInercia * g', 2),
    ('const kf = BOTE_TUNE.cascaronAcoplo / r;', 1),
    ('ps.omega.lerp(tmpV, BOTE_TUNE.omegaLerp);', 1),
    ('1 - dt * BOTE_TUNE.omegaDecay', 1),
    ('const BOLA_TUNE = { spinGanancia: 0.45 };', 1),
    ('const BOLA_SPIN_GANANCIA = BOLA_TUNE.spinGanancia;', 1),
    # CONSERVACIÓN r55 · ARCANO_CFG (capa de datos del Arcano intacta)
    ('const ARCANO_CFG = {', 1),
    ('ventanas: {', 1),
    ('golpesPorCarga: 20,', 1),
    ("campeonato: { origen: 'registro_completo', candados: false },", 1),
    ("duelos: { origen: 'surtido_base_mas_desbloqueados', candados: true },", 1),
    ('ui: { buho: { x: 2.70, y: 2.60, zOff: 0.016 } },', 1),
    ('const pwViva = (t) => (on || dlV) && t > 0;', 1),
    ('const MEGA_DUR = ARCANO_CFG.ventanas.mega;', 1),
    ('const MEGA_GOLPES = ARCANO_CFG.reglas.golpesPorCarga;', 1),
    ('dur: ARCANO_CFG.ventanas.', 14),
    ('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,', 1),
    # CONSERVACIÓN r54 (semántica de la ventana viva intacta)
    ('this._megaGasta(ent);   // r54 · la ACTIVACIÓN gasta su carga', 1),
    ('if (this._dlT > 0 || this._dlId) {', 1),
    ('_dlVentana(id) {', 1),
    ('this._dlVentanasApaga();', 1),
    ("const dlGig = this._dlOn('gigante') || this._dlOn('mega');", 1),
    # CONSERVACIÓN FASE 145/144/143
    ('gunConsuma = this.champs.fireGun(i) === true;', 1),
    ("window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    ("musica: 'assets/hall/cabana/cabana.mp3'", 1),
]

# AGUJAS por REGEX (patrón, esperado)
AGUJAS_RE = [
    (r'if \(pwViva\(this\._\w+T\)\)', 13),
    (r'\(on \|\| dlV\)', 1),          # sólo la definición: cero copias
    (r'else if \(this\._\w+T > 0\) \{', 9),
    (r'BOTE_TUNE\.\w+', 7),           # 6 lectores + 1 repeat de cascaronInercia
    (r'PASO_TUNE\.\w+', 3),           # uiMax + fisMax (×2: dt y dtFis)
    (r'CONFIG_MENU\.salir', 8),       # 4 código (ask+método+HUB+caso) + 4 comentarios
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.149 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r58'
    vj.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n',
                  encoding='utf-8')

    def parchea(ruta: Path, viejo: str, nuevo: str) -> None:
        if not ruta.exists():
            return
        t = ruta.read_text(encoding='utf-8')
        if viejo in t:
            ruta.write_text(t.replace(viejo, nuevo), encoding='utf-8')

    parchea(SRC / 'core' / 'c00_pre_three.js',
            f"const VERSION = '{VIEJA}'", f"const VERSION = '{NUEVA}'")
    parchea(SRC / '03_body.html', f'>V{VIEJA}</span>', f'>V{NUEVA}</span>')
    parchea(RAIZ / 'public' / 'sw.js',
            f"crazypp-v{VIEJA}", f"crazypp-v{NUEVA}")
    print(f'· sellos → {NUEVA} · FASE {FASE_NUEVA}')


def ensambla() -> bytes:
    """El ensamblado EXACTO de build_game.py, en este proceso."""
    spec = importlib.util.spec_from_file_location(
        'bg', RAIZ / 'scripts' / 'build_game.py')
    bg = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bg)
    return b''.join(
        bg.pieza_pura((SRC / n).read_bytes()) if n.startswith('core/')
        else (SRC / n).read_bytes()
        for n, _ in bg.ORDER
    )


def reancla_tests(sha: str, tamano: int, golden_viejo: str,
                  tamano_viejo: int) -> int:
    """Re-ancla versión/fase/nombre/tamaño/golden Y hashes de contrato
    (c00/c02/c12) en test_r*.mjs + qa_sup1_v366.py (lección r53: los QA
    Python con versión hardcodeada van en la lista)."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE: VIEJO_NOMBRE
        # podría contener «FASE 151» y el reemplazo de número lo corrompería
        # — lección r57)
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.551.209 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
    # 2.º los hashes de contrato COMPLETOS (los tests comparan el sha256
    # entero) — los prefijos van al FINAL para no frankenstenizar
    pares = list(HASHES_VIEJOS_NUEVOS)
    for viejo, nuevo in pares:
        cambios.append((viejo, nuevo))
        cambios.append((viejo[:16], nuevo[:16]))
        cambios.append((viejo[:8], nuevo[:8]))
    n_fich = 0
    dianas = sorted(glob.glob(str(RAIZ / 'scripts' / 'test_r*.mjs'))) + \
        [str(RAIZ / 'scripts' / 'qa_sup1_v366.py')]
    for f in dianas:
        p = Path(f)
        t = p.read_text(encoding='utf-8')
        orig = t
        for viejo, nuevo in cambios:
            t = t.replace(viejo, nuevo)
        if t != orig:
            p.write_text(t, encoding='utf-8')
            n_fich += 1
    print(f'· {n_fich} tests re-anclados (versión/fase/nombre/tamaño/golden '
          '+ hashes COMPLETOS c00/c02/c12)')
    return n_fich


def verifica() -> bool:
    gh = GAME.read_bytes()
    ok = True
    for aguja, esperado in AGUJAS:
        n = gh.count(aguja.encode('utf-8'))
        bien = (n >= 1) if esperado is None else (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] {aguja[:52]:54s} '
              f'×{n} (esperado {esperado if esperado is not None else "≥1"})')
        ok = ok and bien
    txt = gh.decode('utf-8', 'replace')
    for pat, esperado in AGUJAS_RE:
        n = len(re.findall(pat, txt))
        bien = (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] RE {pat[:46]:50s} '
              f'×{n} (esperado {esperado})')
        ok = ok and bien
    v_ok = f"const VERSION = '{NUEVA}'".encode() in gh
    print(f'  [{"✓" if v_ok else "✗"}] VERSION {NUEVA}')
    ok = ok and v_ok
    print(f'VERIFICACIÓN r58: {"TODO OK" if ok else "FALLO"}')
    return ok


def main() -> None:
    # golden/tamaño VIEJOS capturados ANTES de tocar nada (los llevan los
    # tests de rondas — reancla real)
    vdat0 = json.loads((SRC / 'VERSION.json').read_text(encoding='utf-8'))
    golden_viejo = vdat0.get('golden', '')
    tamano_viejo = int(vdat0.get('tamano', 0))
    if golden_viejo and golden_viejo != hashlib.sha256(
            GAME.read_bytes()).hexdigest():
        print('⚠ VERSION.json golden ≠ sha de public/game.html actual '
              f'({golden_viejo[:12]}…) — el re-ancla usa el de VERSION.json')

    sella_sellos()
    datos = ensambla()
    sha = hashlib.sha256(datos).hexdigest()
    GAME.write_bytes(datos)
    GOLDEN.write_text(
        '# SHA-256 del game.html ensamblado '
        '(build_game.py — regenerado por sella_r58_menu_salir)\n'
        f'{sha}\n', encoding='utf-8')
    print(f'· game.html ESCRITO: {len(datos):,} B · sha {sha[:16]}…')
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['golden'] = sha
    vdat['tamano'] = len(datos)
    vj.write_text(json.dumps(vdat, ensure_ascii=False, indent=2) + '\n',
                  encoding='utf-8')
    reancla_tests(sha, len(datos), golden_viejo, tamano_viejo)
    if not verifica():
        sys.exit(1)


if __name__ == '__main__':
    main()
