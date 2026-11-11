#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r55_capa_datos.py — FASE 149 · SELLADO VIVO a 3.6.146-SDK6.

EL ARCANO SE VUELVE DATA-DRIVEN (directiva del dueño: «No queremos NADA
hardcodeado. TODO el juego debe ser Data-drive!»):

  · ARCANO_CFG (c02, junto a DIMS): ÚNICA FUENTE DE VERDAD del Arcano —
    ventanas por poder (mega 15, oscuridad 20, portal 8, resto 10,
    prismaGuia 3.0, dlGigante/dlFuego/dlLoca), reglas por modalidad
    (golpesPorCarga 20 · campeonato: registro_completo sin candados ·
    duelos: surtido base+desbloqueados) y la posición del búho del Hall.
  · c12: las 15 consts *_DUR se vuelven ALIAS de la tabla; MEGA_GOLPES
    lee reglas.golpesPorCarga; DL_DUR se CONSTRUYE de la tabla (muere la
    duplicación de datos); PODERES_PALA gana `dur` por fila (catálogo
    auto-descripto); c08 importa ARCANO_CFG.
  · PUERTA ÚNICA pwViva(t) = (on || dlV) && t > 0: la REGLA de la ventana
    vive en UN sitio y las 19 compuertas r54 la LEEN — cero patrones
    copiados. Semántica idéntica (r54 intacto: imán gasta su carga,
    recogida sólo en transición, FX vivos).
  · BÚHO (c08): arcMesh.position.set(ARCANO_CFG.ui.buho.x, .y, z0+ .zOff)
    — moverlo = editar UN dato en c02.

Este sellador (patrón sella_r54_poderes_duelos; golden VIEJO capturado
ANTES de sobrescribir; lección r53: QA Python con versión en la lista):
  · VERSION.json → 3.6.146-SDK6 · FASE 149 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/faseNombre/tamaño/golden en test_r*.mjs Y
    qa_sup1_v366.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r55_capa_datos.py
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
VIEJA, NUEVA = '3.6.145-SDK6', '3.6.146-SDK6'
FASE_VIEJA, FASE_NUEVA = 148, 149
VIEJO_NOMBRE = ('Los superpoderes de Duelos Locos viven su ventana completa '
                '(puerta única on||dlV, halo vivo en duelos, imán gasta su '
                'carga) + búho del Arcano en la esquina superior derecha del '
                'Hall')
NOMBRE = ('El Arcano es data-driven: ARCANO_CFG única fuente de verdad '
          '(ventanas, reglas por modalidad, búho) + puerta única pwViva')

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # LA CAPA DE DATOS (c02; el ensamblador elimina `export`/`import` —
    # los imports se verifican sobre los FUENTES en test_r39)
    ('const ARCANO_CFG = {', 1),
    ('ventanas: {', 1),
    ('golpesPorCarga: 20,', 1),
    ("campeonato: { origen: 'registro_completo', candados: false },", 1),
    ("duelos: { origen: 'surtido_base_mas_desbloqueados', candados: true },", 1),
    ('ui: { buho: { x: 2.70, y: 2.60, zOff: 0.016 } },', 1),
    # LA PUERTA ÚNICA (c12) — la regla vive en UN sitio
    ('const pwViva = (t) => (on || dlV) && t > 0;', 1),
    # LOS ALIAS c12 leen la tabla (muestra + conteo aparte en AGUJAS_RE)
    ('const MEGA_DUR = ARCANO_CFG.ventanas.mega;', 1),
    ('const OSCURIDAD_DUR = ARCANO_CFG.ventanas.oscuridad;', 1),
    ('const PORTAL_DUR = ARCANO_CFG.ventanas.portal;', 1),
    ('const MEGA_GOLPES = ARCANO_CFG.reglas.golpesPorCarga;', 1),
    ('const DL_DUR = {   // r55: construida de ARCANO_CFG.ventanas (c02) — un solo dato', 1),
    ('dur: ARCANO_CFG.ventanas.', 14),          # el catálogo PODERES_PALA lleva su dur
    # LOS USOS de la capa de datos (lectores c12/c08; los imports de
    # fuente se verifican en test_r39 sobre src/)
    # EL BÚHO lee datos (c08)
    ('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,', 1),
    # CONSERVACIÓN r54 (semántica intacta)
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
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.146 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r55'
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
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.542.635 (etiqueta)
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
    print(f'VERIFICACIÓN r55: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r55_capa_datos)\n'
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
