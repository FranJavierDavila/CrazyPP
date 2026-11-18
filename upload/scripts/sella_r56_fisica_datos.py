#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r56_fisica_datos.py — FASE 150 · SELLADO VIVO a 3.6.147-SDK6.

EXTENSIÓN DATA-DRIVEN A FÍSICA Y BOLA (directiva del dueño: «No queremos
NADA hardcodeado. TODO el juego debe ser Data-drive!» — patrón r55):

  · BOTE_TUNE (c04, junto a CCD_TUNE): los 6 números finos del bote y del
    giro de muñeca dejan de ser literales dentro de las funciones —
    spinDecayBote 0.72 · gripImpactRef 4.5 · cascaronInercia 0.4 ·
    cascaronAcoplo 1.5 · omegaLerp 0.5 · omegaDecay 8. Valores IDÉNTICOS:
    golden test_fisica 11 escenarios · 0 desviaciones.
  · BOLA_TUNE (c12): la ganancia del giro visible vive en tabla —
    BOLA_SPIN_GANANCIA pasa a ALIAS de BOLA_TUNE.spinGanancia (0.45, r24).
  · PANEL DE TELEMETRÍA r56 (public/telemetria.html, fuera del ensamblado):
    rankings por jugador (?rank=1, worker desplegado) + ficha individual
    (?eventos=500&sid=) · qa_dashboard_r56 13/13.

Este sellador (patrón sella_r55_capa_datos; golden VIEJO capturado ANTES
de sobrescribir):
  · VERSION.json → 3.6.147-SDK6 · FASE 150 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/faseNombre/tamaño/golden en test_r*.mjs Y
    qa_sup1_v366.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r56_fisica_datos.py
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
VIEJA, NUEVA = '3.6.146-SDK6', '3.6.147-SDK6'
FASE_VIEJA, FASE_NUEVA = 149, 150
VIEJO_NOMBRE = ('El Arcano es data-driven: ARCANO_CFG única fuente de verdad '
                '(ventanas, reglas por modalidad, búho) + puerta única pwViva')
NOMBRE = ('Data-driven FASE 150: BOTE_TUNE (física fina de c04) + BOLA_TUNE '
          '(giro visible de c12) — valores idénticos, golden 0 desviaciones')

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO FASE 150 · BOTE_TUNE (c04) — la tabla y sus lectores
    ('const BOTE_TUNE = {', 1),       # el ensamblador elimina `export`
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
    # NUEVO FASE 150 · BOLA_TUNE (c12) — el giro visible es dato
    ('const BOLA_TUNE = { spinGanancia: 0.45 };', 1),
    ('const BOLA_SPIN_GANANCIA = BOLA_TUNE.spinGanancia;', 1),
    # CONSERVACIÓN r55 · ARCANO_CFG (la capa de datos del Arcano intacta)
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
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.147 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r56'
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
    """Re-ancla versión/fase/nombre/tamaño/golden en test_r*.mjs + qa_sup1
    (lección r53: los QA Python con versión hardcodeada van en la lista)."""
    cambios = [
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.547.159 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
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
    print(f'· {n_fich} tests re-anclados (versión/fase/nombre/tamaño/golden)')
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
    print(f'VERIFICACIÓN r56: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r56_fisica_datos)\n'
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
