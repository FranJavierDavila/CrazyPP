#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r66_bolaloca.py — FASE 160 · SELLADO VIVO a 3.6.157-SDK6.

BOLA LOCA + REGLA «SOLO 1 SUPERPODER EN MARCHA» · r66 — dos peticiones del
dueño:

  1) REGLA DEL DUEÑO: «el jugador solo pueda lanzar un superpoder de pala
     de cada vez… si un superpoder de pala está activo SOLO cuando este se
     termine podrá aplicar otro. Solo 1 superpoder puede estar ejecutándose
     al mismo tiempo» — helper _poderVivoAlguno() (la mesa de relojes que
     gobierna updateMega y recoge _dlVentanasApaga) y los DOS gatillos
     (megaTrigger y _dlTrigger) bloquean un poder DISTINTO mientras una
     ventana corre: aviso honesto «Ya hay un superpoder activo», cero
     consumo. Relanzar el MISMO poder (refresco/alargar MEGA) sigue vivo.

  2) BOLA LOCA (15.º poder, PRIMERO del registro y SIEMPRE desbloqueado):
     «Se trata del superpoder que usa Wizard en el campeonato de la Magia,
     la bola grande que cambia de colores y modifica su trayectoria
     ligeramente de forma aleatoria. Lo llamaremos "Bola Loca", durará 10
     segundos». Los parámetros EXACTOS del mago (LOCA_BALL de magia):
     ×1,65 con radio físico, ciclo HSL 0,30 vueltas/s (0.9/0.58 + emissive
     0.22), vaivén 4 m/s² a 8,5 rad/s y ráfagas 2,5 m/s² cada 0,22 s.
     Icono DEL DUEÑO (SuperPala_BolaLoca.png cuantizado a 64 colores) y
     voces Piper NATIVAS de la casa (es_ES-davefx «¡Bola loca!» /
     en_US-lessac «Crazy ball!») — mismo contrato data-URI que el registro.
     Anuncio con la MISMA voz del sistema en campeonatos (concesión +
     selector) y el nombre corto en duelos (dl_bolaloca).
     · Sala ARCANA: primer puesto (índice 0 de PODERES_PALA) SIN candado —
       poderesDesbloqueados() la SIEMBRA de serie y se auto-persiste; el
       sorteo aleatorio de la coronación la excluye sola (ya no está con
       candado). La voz de la sala Arcana presenta la ficha como siempre
       (la galería es data-driven del registro).
     · DUELOS LOCOS: disponible DE INICIO (siempre desbloqueada → entra en
       el surto) y la vieja 'loca' (spin ×2, anunciada «BOLA LOCA») SALE
       del surto para no duplicar el nombre — sigue VIVA en recepción para
       rivales con build anterior.
     · PUERTA CONSERVADORA (la del crono): deriva y radio físico SOLO en
       local; en online la bola crece y cicla color (visual) y la física
       NUNCA se toca (una deriva aleatoria no puede viajar en HIT/HANDOFF).

Este sellador (patrón sella_r65_saque; golden VIEJO capturado ANTES;
agujas de conservación r65 importadas de SU módulo — cero transcripción;
conteos medidos con scripts/_r66_mide_agujas.py):
  · VERSION.json → 3.6.157-SDK6 · FASE 160 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden en test_r*.mjs +
    qa_sup1_v366.py + qa_r46_humo_gobernador.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r66_bolaloca.py
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
VIEJA, NUEVA = '3.6.156-SDK6', '3.6.157-SDK6'
FASE_VIEJA, FASE_NUEVA = 159, 160
# nombre VIEJO importado del sellador r65 (cero transcripción)
_spec65 = importlib.util.spec_from_file_location(
    's65', RAIZ / 'scripts' / 'sella_r65_saque.py')
s65 = importlib.util.module_from_spec(_spec65)
_spec65.loader.exec_module(s65)
VIEJO_NOMBRE = s65.NOMBRE
NOMBRE = ('BOLA LOCA + SOLO 1 SUPERPODER EN MARCHA r66: la BOLA LOCA original del '
          'Wizard de magia entra como 15.º poder — PRIMERO del registro y SIEMPRE '
          'desbloqueado (sala Arcana sin candado · Duelos Locos de inicio · excluida '
          'del sorteo de coronación · la vieja loca de spin sale del surto) — bola '
          '×1,65 con radio físico, ciclo arcoíris 0,30 vueltas/s y deriva aleatoria '
          'del mago (vaivén 4 m/s² a 8,5 rad/s + ráfagas 2,5 m/s² cada 0,22 s) en '
          'ventana de 10 s, icono del dueño y voces Piper nativas — Y la regla del '
          'dueño: solo 1 superpoder de pala puede estar ejecutándose al mismo tiempo '
          '(_poderVivoAlguno gobierna los dos gatillos; relanzar el MISMO poder '
          'sigue permitido)')

# Hash de contrato: c02 SÍ cambia en r66 (ventana bolaloca). El par se
# re-ancla en los tests que lo llevan (patrón r64: pares viejo→nuevo).
import hashlib as _h
_c02_antes = None  # se calcula en main() ANTES del sellado (los sellos no
# tocan c02; el contenido de c02 ya es el definitivo — hash estable)
HASHES_VIEJOS_NUEVOS = []

# AGUJAS r66 — conteos MEDIDOS sobre ensamblado en memoria
# (scripts/_r66_mide_agujas.py — método r63/r64/r65).
AGUJAS = [
    # FASE 160 · registro y datos
    ('const PNG_PODER_BOLALOCA', 1),
    ('const VOZ_PODER_BOLALOCA =', 1),
    ('const VOZ_PODER_BOLALOCA_EN =', 1),
    ("{ id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),", 1),
    ('voz: VOZ_PODER_BOLALOCA, vozEn: VOZ_PODER_BOLALOCA_EN, png: PNG_PODER_BOLALOCA', 1),
    ("bolaloca: ['arcono_tipo_distraccion', '#c39bff']", 1),
    ('const BOLALOCA_DUR = ARCANO_CFG.ventanas.bolaloca;', 1),
    ('const BOLALOCA_SCALE = 1.65;', 1),
    ('const BOLALOCA_HUE_V = 0.30;', 1),
    ('const BOLALOCA_SWAY = 4.0;', 1),
    ('const BOLALOCA_FREQ = 8.5;', 1),
    ('const BOLALOCA_JIT = 2.5;', 1),
    ('const BOLALOCA_JT = 0.22;', 1),
    ('bolaloca: 10,', 1),
    ('bolaloca: ARCANO_CFG.ventanas.bolaloca,', 1),
    # FASE 160 · regla SOLO 1 PODER
    ('_poderVivoAlguno()', 3),   # definición + gate megaTrigger + gate _dlTrigger
    ('poder_uno_activo', 3),     # i18n ES + i18n EN + uso en el gate
    ('REGLA DEL DUEÑO: SOLO 1 superpoder de pala en marcha', 1),
    # FASE 160 · trigger/frame/fin
    ('_bolalocaTrigger(ent) {', 1),
    ('_bolalocaFrame(dt) {', 1),
    ('_bolalocaFin() {', 1),
    ('_bolalocaAplicaFx() {', 1),
    ('this._bolalocaT = BOLALOCA_DUR;', 2),
    ('_bolalocaAplicaFx();', 1),
    ('pwViva(this._bolalocaT)', 1),
    ("['_bolalocaT', '_bolalocaFin']", 1),
    # FASE 160 · icono activo (selActiva + rest)
    ("if (ent.id === 'bolaloca') return this._bolalocaT > 0;", 1),
    ("if (this._megaActivaId === 'bolaloca') return this._bolalocaT;", 1),
    # FASE 160 · desbloqueo de serie + surto
    ('BOLA LOCA SIEMPRE DESBLOQUEADA', 1),
    ("lista.unshift('bolaloca');", 1),
    ("return ['bolaloca'];", 1),
    ("filter((id) => id !== 'loca')", 1),
    # FASE 160 · i18n (ES + EN)
    ("dl_bolaloca: 'BOLA LOCA',", 1),
    ("dl_bolaloca: 'CRAZY BALL',", 1),
    ("arc_bolaloca_go: '¡BOLA LOCA!", 1),
    ("arc_bolaloca_fin: 'BOLA LOCA agotada',", 1),
    ("poder_bolaloca: '¡BOLA LOCA!',", 1),
    ("arc_bolaloca_go: 'CRAZY BALL!", 1),
    ("arc_bolaloca_fin: 'CRAZY BALL worn off',", 1),
    ("poder_bolaloca: 'CRAZY BALL!',", 1),
    # FASE 160 · wiring (dispatcher + _dlArma + selector + prewarm)
    ("if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent);", 1),
    ("bolaloca: '_bolalocaTrigger',", 1),
    ("else if (id === 'bolaloca') par = [VOZ_PODER_BOLALOCA, VOZ_PODER_BOLALOCA_EN];", 1),
    ("this._megaVozPrecalentar('bolaloca');", 1),
    # FASE 160 · parámetros EXACTOS del mago usados en el frame
    ('m.material.color.setHSL(hue, 0.9, 0.58);', 1),
    ('m.material.emissive.setHSL(hue, 0.9, 0.22);', 1),
    ('Math.sin(this._bolalocaPh * BOLALOCA_FREQ)', 1),
    ('(Math.random() - 0.5) * 2 * BOLALOCA_JIT', 1),
    ('DIMS.ballRadius = this._bolalocaFx.r * BOLALOCA_SCALE;', 1),
    ('m.scale.setScalar(BOLALOCA_SCALE);', 1),
    ('this._bolalocaReloj += dt;', 1),
    # FASE 160 · cortina (etapas 2/4 la callan) + estado del constructor
    ('la BOLA LOCA también calla en etapas 2/4', 1),
    ('this._bolalocaReloj = 0;', 2),   # constructor + _bolalocaAplicaFx
    # CONSERVACIÓN r65 · las 4 capas del saque siguen intactas
    ('LA BOLA SIEMPRE VUELVE A TU MANO', 1),
    ('_srvManoValida(bh) {', 1),
] + list(s65.AGUJAS)

AGUJAS_RE = [
    (r'_bolalocaT', 33),
    (r'_poderVivoAlguno', 3),
    (r'BOLALOCA_\w+', 21),
] + list(s65.AGUJAS_RE)

# CONSERVACIÓN heredada RE-ANCLADA en r66: el 15.º poder AÑADE una entrada
# al registro ('dur: ARCANO_CFG.ventanas.' 14→15) y UNA ventana pwViva más
# (13→14). Los selladores históricos (r63/r64) quedan intactos — el ajuste
# vive SOLO aquí (patrón r65: la cadena conserva y re-ancla hacia delante).
AGUJAS = [(a, 15 if a == 'dur: ARCANO_CFG.ventanas.' else e) for a, e in AGUJAS]
AGUJAS_RE = [(p, 14 if p == r'if \(pwViva\(this\._\w+T\)\)' else e)
             for p, e in AGUJAS_RE]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.157 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r66'
    # el sello del HUB: el release DE ESTA RONDA (v36157) — el hub
    # page.tsx se re-vende ANTES del build_zip (su candado exige el sello
    # nuevo y prohíbe los viejos); qa_version exige coherencia
    # página⇄VERSION.json (lección del re-ancla r66)
    vdat['hub'] = 'v36157-sdk6'
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
    """Re-ancla versión/fase/nombre/tamaño/golden en test_r*.mjs +
    qa_sup1_v366.py + qa_r46_humo_gobernador.py."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE — lección r57)
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.588.233 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
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
    print(f'· {n_fich} tests re-anclados (versión/fase/nombre/tamaño/golden)')
    return n_fich


def verifica() -> bool:
    gh = GAME.read_bytes()
    ok = True
    for aguja, esperado in AGUJAS:
        n = gh.count(aguja.encode('utf-8'))
        bien = (n >= 1) if esperado is None else (n == esperado)
        if not bien:
            print(f'  [✗] {aguja[:70]:74s} ×{n} (esperado '
                  f'{esperado if esperado is not None else "≥1"})')
        ok = ok and bien
    txt = gh.decode('utf-8', 'replace')
    for pat, esperado in AGUJAS_RE:
        n = len(re.findall(pat, txt))
        bien = (n == esperado)
        if not bien:
            print(f'  [✗] RE {pat[:54]:58s} ×{n} (esperado {esperado})')
        ok = ok and bien
    v_ok = f"const VERSION = '{NUEVA}'".encode() in gh
    if not v_ok:
        print(f'  [✗] VERSION {NUEVA}')
    ok = ok and v_ok
    n_agujas = len(AGUJAS) + len(AGUJAS_RE) + 1
    print(f'VERIFICACIÓN r66: {"TODO OK" if ok else "FALLO"} '
          f'({n_agujas} agujas)')
    return ok


def main() -> None:
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
        '(build_game.py — regenerado por sella_r66_bolaloca)\n'
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
