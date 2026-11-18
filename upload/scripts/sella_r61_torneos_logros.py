#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r61_torneos_logros.py — FASE 155 · SELLADO VIVO a 3.6.152-SDK6.

CONFIG_TORNEOS + CONFIG_LOGROS · TORNEOS Y LOGROS SON DATA-DRIVEN
(petición del dueño: «seguir extendiendo el patrón data-driven» — sexta
parada tras ARCANO_CFG/física/menú/audio/dificultad):

  · CONFIG_TORNEOS (c02, patrón ARCANO_CFG/CONFIG_MENU/CONFIG_AUDIO/
    CONFIG_DIFICULTAD) — ÚNICA FUENTE DE VERDAD DE LOS TORNEOS: partido
    (el FORMATO del árbitro c06: a 11, ventaja 2, iguala 10, saque cada 2/
    cada punto en iguala, pausas de punto, best-of de fábrica y del PARTIDO
    libre, factor de serie), caminos (etapas por campeonato — antes
    CHAMP_STAGE_TOTAL de c11), portada (respaldo 'locura'), candados
    (antes ChampLoader.LOCKED, r72) y circuito (niveles/combo/estrellas
    del PRO TRAINING c13).
  · CONFIG_LOGROS (c02) — ÚNICA FUENTE DE VERDAD DE LOS LOGROS: core (los
    6 medallones CRAZY — ACHIEVEMENTs se DERIVA en c06 — y sus condiciones,
    antes dispersas en GameStats) y train (los 10 honores del PRO TRAINING,
    antes el array ACHS con umbrales repartidos).
  · LECTORES enchufados: c06 (ACHIEVEMENTS derivado · COND_LOGRO ×5 ·
    formato del árbitro ×6), c11 (LOCKED · portadaId · _stageHint · alias
    CHAMP_STAGE_TOTAL), c12 (bestOfLibre ×7) y c13 (ACHS · LEVELS ·
    comboMulN · starsFor · grants · hitos con RALLY_BONUS deduplicado).
  · DEDUP r61: el bonus del metrónomo del okHit usaba literales 30/50/100 →
    15/25/50 duplicando RALLY_MILL/RALLY_BONUS (tablas que ya existían en
    c13): ahora lee las tablas. Cero cambios de comportamiento.
  · RE-ANCLES r61: test_r23 (regex del catálogo ACHIEVEMENTS → forma
    derivada + tabla c02).

Este sellador (patrón sella_r60_dificultad; golden VIEJO capturado ANTES de
sobrescribir):
  · VERSION.json → 3.6.152-SDK6 · FASE 155 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden Y hash de contrato (c02)
    en test_r*.mjs + qa_sup1_v366.py + qa_r46_humo_gobernador.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r61_torneos_logros.py
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
VIEJA, NUEVA = '3.6.151-SDK6', '3.6.152-SDK6'
FASE_VIEJA, FASE_NUEVA = 154, 155
VIEJO_NOMBRE = ('CONFIG_DIFICULTAD r60: la DIFICULTAD es data-driven — presets (curvas CPU '
                'easy/medium/hard) · asistencia de saque por nivel · topes/exponentes de '
                'scalePreset · ELO (anclas/K por modo/paso/bandas matchmaking) · adaptativo · '
                'supervivencia · fórmula de esfuerzo r113 (12 lectores c02/c06/c12 · alias '
                'AI_PRESETS/SERVE_ASSIST_TIERS/ELO_CPU)')
NOMBRE = ('CONFIG_TORNEOS+LOGROS r61: TORNEOS y LOGROS data-driven — formato del árbitro '
          '(a 11/ventaja/iguala/saque/pausas/best-of/serie) · caminos+portada+candados de '
          'campeonatos · circuito (niveles/combo/estrellas) · catálogo core 6 medallones '
          'derivado + condiciones GameStats · train 10 honores c13 (lectores c06/c11/c12/c13 '
          '· alias CHAMP_STAGE_TOTAL)')

# Hash de contrato: c02 (tablas CONFIG_* + alias + scalePreset + rivalPorElo).
# c06/c11/c12/c13 cambian pero NINGÚN test lleva sus hashes (verificado r61).
HASHES_VIEJOS_NUEVOS = [
    # c02_cfg_escena.js (CONFIG_TORNEOS + CONFIG_LOGROS)
    ('22b0378157603614df075ba9f69b84ab45000cc02ab15a394191989fe238d63b',
     'ca26fac9407f02d0c8bea954f406e32d3cbc18576639733df0884b9317472b2a'),
]

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO r61 · CONFIG_TORNEOS: la tabla (el ensamblador quita el export)
    ('const CONFIG_TORNEOS = {', 1),
    ('puntosGanar: 11,', 1),
    ('ventajaMinima: 2,', 1),
    ('igualaEn: 10,', 1),
    ('saqueCada: 2,', 1),
    ('saqueIguala: 1,', 1),
    ('pausaPuntoS: 2.2,', 1),
    ('pausaSupervivenciaS: 1.7,', 1),
    ('bestOfLibre: 3,', 1),
    ('bestOfFabrica: 1,', 1),
    ('serieFactor: 2,', 1),
    ('caminos: { locura: 5, magia: 5, oeste: 5, estacion_orbital: 5, halloween: 5 },', 1),
    ("portada: 'locura',", 1),
    ("candados: ['estacion_orbital'],", 1),
    ('niveles: [', 1),
    # NUEVO r61 · CONFIG_LOGROS: la tabla
    ('const CONFIG_LOGROS = {', 1),
    ("cond: { tipo: 'aces', valor: 10 }", 1),
    ("cond: { tipo: 'medallasOro', cuenta: 5 }", 1),
    # NUEVO r61 · lectores torneos
    ('this.bestOf = CONFIG_TORNEOS.partido.bestOfFabrica;', 1),
    ('CONFIG_TORNEOS.partido.bestOfLibre;', 7),
    ('const CHAMP_STAGE_TOTAL = CONFIG_TORNEOS.caminos;', 1),
    ('static LOCKED = CONFIG_TORNEOS.candados;', 1),
    ('e ? e.id : CONFIG_TORNEOS.portada;', 1),
    # NUEVO r61 · lectores logros
    ('const ACHIEVEMENTS = CONFIG_LOGROS.core.map', 1),
    ('COND_LOGRO(', 5),
    ('RALLY_BONUS.t5a[hi]', 1),
    # CONSERVACIÓN r60 · CONFIG_DIFICULTAD (tabla + presets + saque + escala)
    ('const CONFIG_DIFICULTAD = {', 1),
    ('presets: {', 1),
    ('easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.15, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },', 1),
    ('medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.05,  missBase: 0.08, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },', 1),
    ('hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.024, missBase: 0.03, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },', 1),
    ('saque: {', 1),
    ('easy:   { reach: 0.060, vy: 3.5,  angleMul: 1.4,  assistMul: 1.35 },', 1),
    ('escala: {', 1),
    ('kMin: 0.7, kMax: 2.2,        // rango legal del factor k (invariante del arnés)', 1),
    ('const BOTE_TUNE = {', 1),
    ('const BOLA_TUNE = { spinGanancia: 0.45 };', 1),
    # CONSERVACIÓN r55 · ARCANO_CFG (capa de datos del Arcano intacta)
    ('const ARCANO_CFG = {', 1),
    ('const pwViva = (t) => (on || dlV) && t > 0;', 1),
    ('dur: ARCANO_CFG.ventanas.', 14),
    ('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,', 1),
    # CONSERVACIÓN r58 · CONFIG_MENU (salida a la web intacta)
    ('const CONFIG_MENU = {', 1),
    ('urlDestino: \'AUTO_ORIGIN\',', 1),
    # CONSERVACIÓN r59 · CONFIG_AUDIO (mezcla intacta)
    ('const CONFIG_AUDIO = {', 1),
    ('murmullo: { base: 0.05, entradaS: 1.5, salidaS: 0.8 },', 1),
    # CONSERVACIÓN r54 + FASE 145/144/143
    ('this._megaGasta(ent);   // r54 · la ACTIVACIÓN gasta su carga', 1),
    ('gunConsuma = this.champs.fireGun(i) === true;', 1),
    ("window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    ("musica: 'assets/hall/cabana/cabana.mp3'", 1),
]

# AGUJAS por REGEX (patrón, esperado)
AGUJAS_RE = [
    # NUEVO r61 · lectores de las dos tablas
    (r'CONFIG_TORNEOS\.\w+', 25),
    (r'CONFIG_TORNEOS\.partido\b', 13),
    (r'CONFIG_TORNEOS\.caminos\b', 4),
    (r'CONFIG_TORNEOS\.circuito\b', 4),
    (r'CONFIG_LOGROS\.\w+', 19),
    (r'CONFIG_LOGROS\.core\b', 5),
    (r'CONFIG_LOGROS\.train\b', 14),
    (r"COND_LOGRO\('\w+'\)", 5),
    # CONSERVACIÓN r60 · lectores de CONFIG_DIFICULTAD (12 en c02/c06/c12)
    (r'CONFIG_DIFICULTAD\.\w+', 12),
    (r'CONFIG_DIFICULTAD\.presets\b', 1),
    (r'CONFIG_DIFICULTAD\.saque\b', 1),
    (r'CONFIG_DIFICULTAD\.escala\b', 2),
    (r'CONFIG_DIFICULTAD\.elo\b', 5),
    (r'CONFIG_DIFICULTAD\.elo\.cpu\b', 1),
    (r'CONFIG_DIFICULTAD\.adaptativo\b', 1),
    (r'CONFIG_DIFICULTAD\.supervivencia\b', 1),
    (r'CONFIG_DIFICULTAD\.esfuerzo\b', 1),
    # CONSERVACIÓN r59 (44 lectores de CONFIG_AUDIO en c03)
    (r'CONFIG_AUDIO\.buses\.\w+', 12),
    (r'CONFIG_AUDIO\.canales\.\w+', 3),
    (r'CONFIG_AUDIO\.musica\.\w+', 7),
    (r'CONFIG_AUDIO\.bso\.\w+', 7),
    (r'CONFIG_AUDIO\.salon\.\w+', 5),
    (r'CONFIG_AUDIO\.sfx\.\w+', 10),
    (r'if \(pwViva\(this\._\w+T\)\)', 13),
    (r'\(on \|\| dlV\)', 1),
    (r'CONFIG_MENU\.salir', 8),
    (r'BOTE_TUNE\.\w+', 7),
    (r'PASO_TUNE\.\w+', 3),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.152 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r61'
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
    """Re-ancla versión/fase/nombre/tamaño/golden Y hash de contrato (c02)
    en test_r*.mjs + qa_sup1_v366.py + qa_r46_humo_gobernador.py."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE — lección r57)
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.568.289 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
    # 2.º los hashes de contrato COMPLETOS — los prefijos al FINAL
    pares = list(HASHES_VIEJOS_NUEVOS)
    for viejo, nuevo in pares:
        cambios.append((viejo, nuevo))
        cambios.append((viejo[:16], nuevo[:16]))
        cambios.append((viejo[:8], nuevo[:8]))
    n_fich = 0
    dianas = sorted(glob.glob(str(RAIZ / 'scripts' / 'test_r*.mjs'))) + \
        [str(RAIZ / 'scripts' / 'qa_sup1_v366.py'),
         str(RAIZ / 'scripts' / 'qa_r46_humo_gobernador.py')]
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
          '+ hash COMPLETO c02 · qa_r46 incluido)')
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
    print(f'VERIFICACIÓN r61: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r61_torneos_logros)\n'
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
