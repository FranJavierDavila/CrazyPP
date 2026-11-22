#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r50_oeste_i18n.py — FASE 145 · SELLADO VIVO a 3.6.143-SDK6.

Dos frentes del dueño (informe post-demo):
  A · SUPERPODERES DE PALA NO SE APLICABAN EN EL SALVAJE OESTE — el arma
      estaba ARMADA todo el duelo (gunArmed = active && _duelOn) y la rama
      del revólver se comía el gatillo libre AUNQUE fuera de su ventana de
      fuego (fireGun no-op silencioso entre salvas). CONTRATO DE CONSUMO:
      fireGun devuelve true/false («el pulso es mío / no es mío») en núcleo
      (c11 wrapper + c12 enrutado) y en los módulos oeste, locura y
      estacion_orbital (halloween/plantilla ya devolvían bool). El pulso no
      consumido CAE al megaTrigger: el gatillo libre vuelve a soltar el
      poder seleccionado en TODOS los campeonatos.
  B · CARTELES DEL HALL SOLO EN CASTELLANO — (1) chips 'BOLA'/'MESA' de la
      pared de insignias hardcodeados → claves gloria_bola/gloria_mesa
      (ES/EN en c00); (2) cambiar idioma con el salón abierto no repintaba
      las placas 3D → listener 'pp-lang' en el constructor (drawHall +
      _arconoRepinta). Auditoría con scripts/auditoria_i18n_hall.mjs: las
      40 claves directas del hall ya tenían EN; el arte horneado de las
      panorámicas no lleva castellano (museo verificado a ojo).

Sellador (patrón sella_r49_residuales, golden VIEJO capturado ANTES):
  · VERSION.json → 3.6.143-SDK6 · FASE 145 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html (build_game.py) y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden en test_r*.mjs
  · verifica AGUJAS sobre el game.html final + los 3 módulos (exit 1 si falla)

Uso: python3 scripts/sella_r50_oeste_i18n.py
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
VIEJA, NUEVA = '3.6.142-SDK6', '3.6.143-SDK6'
FASE_VIEJA, FASE_NUEVA = 144, 145
VIEJO_NOMBRE = ('Los seis residuales — resync en rallye, survgo online, ELO del '
                'abandono, GIGANTE residual, LRU de salones y escudo del bucle')
NOMBRE = ('El gatillo del Oeste devuelve el superpoder (contrato de consumo '
          'fireGun) + carteles del Hall con idioma (chips BOLA/MESA y '
          'repintado pp-lang en caliente)')

# AGUJAS sobre el game.html ENSAMBLADO (aguja, esperado exacto; None = ≥1)
AGUJAS = [
    # A · contrato de consumo en el NÚCLEO
    (b'let gunConsuma = false;', 1),
    (b'try { gunConsuma = this.champs.fireGun(i) === true; } catch (e) { /* */ }', 1),
    (b'if (gunConsuma) return;', 1),
    (b"try { return m.fireGun(i) === true; } catch (e) { console.warn('[champs.fireGun]', e); }", 1),
    # B · i18n de los carteles del Hall
    (b"T('gloria_bola')", 1),
    (b"T('gloria_mesa')", 1),
    (b"gloria_bola: 'BOLA'", 1),
    (b"gloria_bola: 'BALL'", 1),
    (b"document.addEventListener('pp-lang', this._onLang);", 1),
    # conservación FASE 144 (los seis residuales siguen)
    (b"window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    (b"musica: 'assets/hall/cabana/cabana.mp3'", 1),
]

# AGUJAS de MÓDULOS (fichero relativo a public/, aguja, esperado exacto; None = ≥1)
AGUJAS_MOD = [
    ('championships/oeste/index.js',
     b"return CTRL ? (CTRL.fireGun(i) === true) : false;", 1),
    ('championships/oeste/index.js',
     b"if (!(this._duelo && this._duelo.phase === 'duel')) return false;", 1),
    ('championships/oeste/index.js',
     b'if (now - (this._gunLast || 0) < 0.16) return true;', 1),
    ('championships/locura/index.js',
     b'if (!mount) return false;', 1),
    ('championships/locura/index.js',
     b'if (now - this._gunLast < 0.16) return true;', 1),
    ('championships/locura/index.js',
     b'return CTRL ? (CTRL.fireGun(i) === true) : false;', 1),
    ('championships/estacion_orbital/index.js',
     b'if (!mount) return false;', 1),
    ('championships/estacion_orbital/index.js',
     b'if (now - this._gunLast < 0.16) return true;', 1),
    ('championships/estacion_orbital/index.js',
     b'if (CTRL) { try { return CTRL.fireGun(i) === true; } catch (e) { console.warn(\'[estacion.fireGun]\', e); } } return false;', 1),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.143 (idempotente)."""
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
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.536.191 (etiqueta)
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
    for rel, aguja, esperado in AGUJAS_MOD:
        p = RAIZ / 'public' / rel
        n = p.read_bytes().count(aguja) if p.exists() else 0
        bien = (n >= 1) if esperado is None else (n == esperado)
        print(f'  [{"✓" if bien else "✗"}] [{rel.split("/")[1]}] '
              f'{aguja.decode()[:38]:40s} ×{n}')
        ok = ok and bien
    v_ok = f"const VERSION = '{NUEVA}'".encode() in gh
    print(f'  [{"✓" if v_ok else "✗"}] VERSION {NUEVA}')
    ok = ok and v_ok
    print(f'VERIFICACIÓN r50: {"TODO OK" if ok else "FALLO"}')
    return ok


def main() -> None:
    # golden/tamaño VIEJOS capturados ANTES de tocar nada (los llevan los
    # tests de rondas — reancla real, no no-op)
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
        '(build_game.py — regenerado por sella_r50_oeste_i18n)\n'
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
