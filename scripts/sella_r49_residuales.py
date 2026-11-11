#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r49_residuales.py — FASE 144 · SELLADO VIVO a 3.6.142-SDK6.

Los SEIS RESIDUALES post-demo (lista PENDIENTE VIVO de la FASE 143):
  1. resync que re-ancla BallAuth.shot también en RALLYE (hoy sólo en
     saque) — c09 (_sendResync lleva `sh` · _applyResync lo re-ancla).
  2. survgo online no notifica al invitado en v2 — c09 (receptor k:'m'
     entiende 'survival' en el invitado) + c12 (el ANFITRIÓN online
     arranca supervivencia y avisa por el cable).
  3. abandono impune en ELO — c12.onNetEnded: duelo P2P en curso se
     registra por el marcador DEL CORTE (decisión) en ambos extremos.
  4. escala 1,3 residual de GIGANTE tras desconexión — c12.onNetEnded:
     aiPaddleMesh a 1,0 + _dlReset().
  5. _hallBufs sin expulsión LRU — c03: LRU real con tope 3 (acceso
     refresca; el que suena nunca se expulsa).
  6. animate sin try global — c12: ESCUDO DEL BUCLE (dedupe por firma,
     telemetría anim_shield, el frame continúa).

Este sellador (patrón sella_r48_viva, con el golden VIEJO capturado
ANTES de sobrescribirlo para que el re-ancla de los tests sea real):
  · VERSION.json → 3.6.142-SDK6 · FASE 144 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/faseNombre/tamaño/golden en test_r*.mjs
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r49_residuales.py
"""
import glob
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/upload')
SRC = RAIZ / 'src' / 'game'
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'
VIEJA, NUEVA = '3.6.141-SDK6', '3.6.142-SDK6'
FASE_VIEJA, FASE_NUEVA = 143, 144
VIEJO_NOMBRE = ('La cabaña suena — cabana.mp3 en el Hall y batería '
                'multijugador lista para clientes reales')
NOMBRE = ('Los seis residuales — resync en rallye, survgo online, ELO del '
          'abandono, GIGANTE residual, LRU de salones y escudo del bucle')

# AGUJAS sobre el game.html ENSAMBLADO (aguja, esperado exacto; None = ≥1)
AGUJAS = [
    # 1 · resync con correlativo de golpes (ida + vuelta)
    (b'sh: this._ball ? (this._ball.shot | 0) : 0,', 1),
    (b"if (m.st !== 'serve' && typeof m.sh === 'number' && this._ball) {", 1),
    # 2 · survgo online: anfitrión arranca y receptor invitado en espejo
    (b"this.net.sendMode('survival');", 2),   # guest pide + host avisa
    (b"this.game.switchMode('survival');", None),  # c09 nuevo + c12 paths
    # 3 · ELO por el corte
    (b"rE.state !== 'over'", 1),
    (b"this.stats.recordMatch(gano, this.difficulty,", 1),
    # 4 · GIGANTE residual
    (b'this.aiPaddleMesh.scale.setScalar(1.0); } catch { /* */ }', 1),
    # 5 · LRU del salón
    (b'this._hallBufsLRU', 5),   # init + defensa(×2 en una línea) + hit + inserción
    # 6 · escudo del bucle
    (b"window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    (b"[animate] escudo del bucle:", 1),
    # conservación FASE 143 (la cabaña sigue sonando)
    (b"musica: 'assets/hall/cabana/cabana.mp3'", 1),
]


def sella_sellos(golden_viejo: str, tamano_viejo: int) -> None:
    """VERSION.json + c00 + badge + sw → 3.6.142 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
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
    # los sellos del juego deben vivir en las PIEZAS (el ensamblador es la
    # única vía) — c00/badge ya parcheados arriba; nada más que tocar.
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
    """Re-ancla versión/fase/nombre/tamaño/golden en los tests de rondas."""
    cambios = [
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.529.358 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
    n_fich = 0
    for f in sorted(glob.glob(str(RAIZ / 'scripts' / 'test_r*.mjs'))):
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
        n = gh.count(aguja)
        bien = (n >= 1) if esperado is None else (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] {aguja.decode()[:44]:46s} '
              f'×{n} (esperado {esperado if esperado is not None else "≥1"})')
        ok = ok and bien
    v_ok = f"const VERSION = '{NUEVA}'".encode() in gh
    print(f'  [{"✓" if v_ok else "✗"}] VERSION {NUEVA}')
    ok = ok and v_ok
    print(f'VERIFICACIÓN r49: {"TODO OK" if ok else "FALLO"}')
    return ok


def main() -> None:
    # golden/tamaño VIEJOS capturados ANTES de tocar nada (los llevan los
    # tests de rondas — reancla real, no el no-op del sella_r48)
    vdat0 = json.loads((SRC / 'VERSION.json').read_text(encoding='utf-8'))
    golden_viejo = vdat0.get('golden', '')
    tamano_viejo = int(vdat0.get('tamano', 0))
    if golden_viejo and golden_viejo != hashlib.sha256(
            GAME.read_bytes()).hexdigest():
        print('⚠ VERSION.json golden ≠ sha de public/game.html actual '
              f'({golden_viejo[:12]}…) — el re-ancla usa el de VERSION.json')

    sella_sellos(golden_viejo, tamano_viejo)
    datos = ensambla()
    sha = hashlib.sha256(datos).hexdigest()
    GAME.write_bytes(datos)
    GOLDEN.write_text(
        '# SHA-256 del game.html ensamblado '
        '(build_game.py — regenerado por sella_r49_residuales)\n'
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
