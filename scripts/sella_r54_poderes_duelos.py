#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r54_poderes_duelos.py — FASE 148 · SELLADO VIVO a 3.6.145-SDK6.

LOS SUPERPODERES DE DUELOS LOCOS VIVEN SU VENTANA COMPLETA + BÚHO EN LA
ESQUINA (aclaración del dueño: en campeonatos los poderes NUNCA están
bloqueados — nacen al azar con la regla de los 20 toques; los candados del
Arcano sólo rigen en los duelos multijugador con poderes):

  · BUG «NACEN AGOTADOS» (DUELOS LOCOS): el slot ÚNICO _dlId/_dlT de duelos
    llevaba la ventana LOCAL y también la del RECEPTOR del rival (red/crono/
    oscuridad) — cualquier disparo propio o del rival SOBREESCRIBÍA el slot,
    la ventana recién armada quedaba fuera de su compuerta de tick y el
    «else if» de contexto muerto la ejecutaba AL INSTANTE con su mensaje
    «SÚPER X agotado»: efecto cero. FIX (c12 updateMega): puerta ÚNICA
    (on || dlV) con dlV = _dlEnabled() — las ventanas arman su reloj propio
    (*_T de siempre), conviven las mías Y las del rival, viven SUS segundos
    y al morir duelos las recoge _dlVentanasApaga (fin natural).
  · FX VIVOS EN DUELOS: fxOnEf/fxOnIm/fxOnPt sólo miraban `on` — el halo del
    SÚPER EFECTO moría UN FRAME tras el disparo (sonaba pero no se veía).
    Ahora (on || dlV). El canto dorado de la MEGA sigue siendo de campeonato
    (la GIGANTE de duelos tiene su propia escala).
  · IMÁN HONESTO: _imanTrigger no gastaba su carga (r57 retiró el gasto por
    ASISTENCIA, no el de activación) — re-disparo gratis para siempre y ent
    sintético de _dlArma huérfano en la matriz. Ahora gasta como TODOS.
  · BÚHO DEL ARCANO EN EL HALL (c08): (2,28 · 2,26) → (2,70 · 2,60) —
    alineado con la esquina superior derecha, ~6 cm de pared y techo
    (margen justo para el hover ×1,14).

Este sellador (patrón sella_r52_arcono_iconos, golden VIEJO capturado ANTES
de sobrescribir — reancla REAL; lección r53: los QA Python con versión
hardcodeada van en la lista):
  · VERSION.json → 3.6.145-SDK6 · FASE 148 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/faseNombre/tamaño/golden en test_r*.mjs Y
    qa_sup1_v366.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r54_poderes_duelos.py
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
VIEJA, NUEVA = '3.6.144-SDK6', '3.6.145-SDK6'
FASE_VIEJA, FASE_NUEVA = 146, 148
VIEJO_NOMBRE = ('Los iconos del Arcano nacen cargados — precalentamiento de '
                'la galería y repintado onload de la ficha')
NOMBRE = ('Los superpoderes de Duelos Locos viven su ventana completa '
          '(puerta única on||dlV, halo vivo en duelos, imán gasta su carga) '
          '+ búho del Arcano en la esquina superior derecha del Hall')

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # FIX 1 · puerta ÚNICA de duelos (dlV) en updateMega
    ('const dlV = this._dlEnabled();', 1),
    ("const emul = (on || dlV) && this._efectoT > 0 ? EFECTO_SPIN_MUL", 1),
    ('const imanAim = !!((on || dlV) && this._imanT > 0);', 1),
    # FIX 2 · FX vivos en duelos (el halo ya no muere al frame siguiente)
    ('const fxOnEf = (on || dlV) && this._efectoT > 0 && !!this._efectoFx;', 1),
    ('const fxOnIm = (on || dlV) && this._imanT > 0 && !!this._imanFx;', 1),
    ('const fxOnPt = (on || dlV) && this._portalT > 0 && !!this._portalFx;', 1),
    ('if (!((on || dlV) && this._efectoT > 0) && this.ball &&', 1),
    # FIX 3 · el IMÁN gasta su carga (consistencia de la casa)
    ('this._megaGasta(ent);   // r54 · la ACTIVACIÓN gasta su carga', 1),
    # FIX 3b · RAÍZ del «nacen agotados»: _dlVentanasApaga sólo en la
    # transición duelos→muerto (antes corría CADA FRAME fuera de duelos y
    # ejecutaba el fin de cualquier ventana recién armada)
    ('if (this._dlT > 0 || this._dlId) {', 1),
    # FIX 4 · búho del Arcano en la esquina superior derecha del Hall
    ('arcMesh.position.set(2.70, 2.60, z0 + 0.016);   // r54: esquina sup. dcha', 1),
    # la definición de _dlVentana sigue (reloj/warn del duelo)
    ('_dlVentana(id) {', 1),
    # conservación r84/r39 (mecánica GIGANTE/MEGA de duelos intacta)
    ("const dlGig = this._dlOn('gigante') || this._dlOn('mega');", 1),
    ('this._dlVentanasApaga();', 1),
    # conservación FASE 145 (contrato de consumo del gatillo del Oeste)
    ('gunConsuma = this.champs.fireGun(i) === true;', 1),
    # conservación FASE 144 (escudo del bucle) y FASE 143 (la cabaña suena)
    ("window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    ("musica: 'assets/hall/cabana/cabana.mp3'", 1),
]

# AGUJAS por REGEX (patrón, esperado)
AGUJAS_RE = [
    (r'if \(\(on \|\| dlV\) && this\._\w+T > 0\)', 13),
    (r'else if \(this\._\w+T > 0\) \{', 9),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.145 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r54'
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
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.540.068 (etiqueta)
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
    print(f'VERIFICACIÓN r54: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r54_poderes_duelos)\n'
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
