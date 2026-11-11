#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r52_arcono_iconos.py — FASE 146 · SELLADO VIVO a 3.6.144-SDK6.

LOS ICONOS DEL ARCANO NACEN CARGADOS (informe del dueño: «la primera vez
los iconos de los superpoderes no aparecen; hay que cargar la ventana con
la descripción para que aparezcan la segunda vez»):
  · RAÍZ: los PNG de PODERES_PALA son data URLs que decodifican ASÍNCRONO
    — la 1.ª _arconoRepinta de _arconoEntrar dibujaba el medallón VACÍO
    (drawImage de un Image no decodificado es no-op silencioso) y el icono
    no salía hasta la 2.ª visita (el Image ya en _arconoIconos, cargado).
  · FIX 1 (c12 constructor): _arconoPrecalentar() — UNA Image por poder
    del registro creada al arrancar; la galería nace decodificada.
  · FIX 2 (c12._arconoIconoImg): CONTRATO DE CARGA — img.onload repinta
    la ficha (sin voz) cuando el PNG está listo y ESE poder es el mostrado.
    Cubre el caso de dispositivo lento o icono gigante: nunca '?' visible.

Este sellador (patrón sella_r49_residuales, golden VIEJO capturado ANTES
de sobrescribir — reancla REAL):
  · VERSION.json → 3.6.144-SDK6 · FASE 146 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/faseNombre/tamaño/golden en test_r*.mjs
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r52_arcono_iconos.py
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
VIEJA, NUEVA = '3.6.143-SDK6', '3.6.144-SDK6'
FASE_VIEJA, FASE_NUEVA = 145, 146
VIEJO_NOMBRE = ('El gatillo del Oeste devuelve el superpoder (contrato de '
                'consumo fireGun) + carteles del Hall con idioma (chips '
                'BOLA/MESA y repintado pp-lang en caliente)')
NOMBRE = ('Los iconos del Arcano nacen cargados — precalentamiento de la '
          'galería y repintado onload de la ficha')

# AGUJAS sobre el game.html ENSAMBLADO (aguja, esperado exacto; None = ≥1)
AGUJAS = [
    # FIX 1 · precalentamiento en el constructor (llamada + bucle del método)
    (b'this._arconoPrecalentar();', 1),
    (b'for (const p of PODERES_PALA) this._arconoIconoImg(p.id);', 1),
    # FIX 2 · contrato de carga (onload → repinta la ficha viva)
    (b'img.onload = () => {', None),
    (b'const vivo = PODERES_PALA[this._arconoIdx];', 1),
    (b'if (vivo && vivo.id === id) this._arconoRepinta(false);', 1),
    # conservación FASE 145 (el gatillo del Oeste sigue con su contrato)
    (b'gunConsuma = this.champs.fireGun(i) === true;', 1),
    # conservación FASE 144 (escudo del bucle sigue vivo)
    (b"window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    # conservación FASE 143 (la cabaña sigue sonando)
    (b"musica: 'assets/hall/cabana/cabana.mp3'", 1),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.144 (idempotente)."""
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
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.538.499 (etiqueta)
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
    print(f'VERIFICACIÓN r52: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r52_arcono_iconos)\n'
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
