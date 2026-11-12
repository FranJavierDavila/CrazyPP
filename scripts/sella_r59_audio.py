#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r59_audio.py — FASE 153 · SELLADO VIVO a 3.6.150-SDK6.

CONFIG_AUDIO · LA MEZCLA DE AUDIO ES DATA-DRIVEN (petición del dueño:
«seguir extendiendo el patrón data-driven a otro subsistemas»):

  · CONFIG_AUDIO (c02, patrón ARCANO_CFG/CONFIG_MENU) — ÚNICA FUENTE DE
    VERDAD DE LA MEZCLA: buses (master → compresor → destino + murmullo),
    canales de fábrica (música/efectos/locutor), los tres canales de
    melodía con sus fundidos (musica/bso/salon — INVARIANTE UNA MELODÍA)
    y las cinco muestras SFX reales (pala/mesa/canto/red/suelo) con
    nivel/piso/tono + clamps + jitter. c03 LEE la tabla (44 lectores):
    cambiar la mezcla es editar AQUÍ, sin tocar lógica.
  · Los timeouts de parada se DERIVAN de su rampa (salidaS·1000 + 100)
    para que jamás queden cortos frente al fundido que acompañan.
  · El estado del usuario (pp_musicvol/pp_fxvol/pp_arcade_vol) sigue
    vivo aparte: la tabla da la FÁBRICA, no el estado (separación
    datos/runtime del patrón).
  · RE-ANCLA r32: el literal «0.30 * this.musicVol» pasó a dato
    (CONFIG_AUDIO.salon.base · misma cura que r43/r57).
  · FUERA DE ÁMBITO (fila futura): los TIMBRES sintéticos de respaldo
    (playOsc/playNoise, blips de UI y del Arcano) — otra tabla, otra ronda.

Este sellador (patrón sella_r58_menu_salir; golden VIEJO capturado ANTES
de sobrescribir):
  · VERSION.json → 3.6.150-SDK6 · FASE 153 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden Y hashes de contrato
    (c02/c03) en test_r*.mjs + qa_sup1_v366.py
  · NUEVO r59 (lección r58): qa_r46_humo_gobernador.py entra en la lista
    de re-ancla (su versión dura viaja con la fase)
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r59_audio.py
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
VIEJA, NUEVA = '3.6.149-SDK6', '3.6.150-SDK6'
FASE_VIEJA, FASE_NUEVA = 152, 153
VIEJO_NOMBRE = ('CONFIG_MENU r58: menú data-driven + botón SALIR A LA WEB en el HUB '
                '(confirmación desde datos · telemetría salir_web con flush síncrono · '
                'session.end() con guardia 2 s · AUTO_ORIGIN sin dominios hardcodeados)')
NOMBRE = ('CONFIG_AUDIO r59: la MEZCLA de audio es data-driven — buses+compresor+'
          'murmullo · canales de fábrica música/efectos/locutor · fundidos menú/BSO/'
          'salón con timeouts derivados · SFX pala/mesa/canto/red/suelo (nivel/piso/'
          'tono) · clamps + jitter como datos (44 lectores en c03)')

# Hashes de contrato: COMPLETOS antes → después (los tests comparan el sha256
# entero, no sólo el prefijo) + prefijos al final. Esta fase toca c02
# (CONFIG_AUDIO) y c03 (44 lectores). c00 SOLO cambia el sello de versión
# (const VERSION), c12 NO cambia (su hash r58 queda vivo en los tests).
HASHES_VIEJOS_NUEVOS = [
    # c02_cfg_escena.js (CONFIG_AUDIO)
    ('c5669e5b14cb56d2e7fc42dd1737e09bcbd720dd0853431e14445bbb3f97f704',
     'f40acc1a8a6a08c26c6fe4bff39f11dd6dae9ec763356784b8b3bb1169a096ba'),
    # c03_audio_voz.js (44 lectores de CONFIG_AUDIO)
    ('b35fe59a94935f77339f03d65c393a4616da28be738cf24a6b687e390874bfbe',
     'afa69daca5d2556625226c62f1ed032c2218a07f719882a22a2b878570069e42'),
]

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO r59 · CONFIG_AUDIO: la tabla (el ensamblador quita el prefijo export)
    ('const CONFIG_AUDIO = {', 1),
    ('murmullo: { base: 0.05, entradaS: 1.5, salidaS: 0.8 },', 1),
    ('compresor: { umbral: -16, rodilla: 22, ratio: 5, ataqueS: 0.002, liberacionS: 0.12 },', 1),
    ('canales: { musica: 1, efectos: 1, locutor: 0.18 },', 1),
    ('musica: { base: 0.26, entradaS: 0.9, salidaS: 0.7, reajusteS: 0.15 },', 1),
    ('bso: { entradaS: 0.8, salidaS: 0.6, reajusteMs: 150, duckMs: 250, restauraMs: 500 },', 1),
    ('salon: { base: 0.30, entradaS: 1.2, salidaS: 1.0 },', 1),
    ('pala:  { nivel: 0.72, piso: 0.15, tonoMin: 0.84, tonoMax: 1.34 },', 1),
    ('mesa:  { nivel: 0.5,  piso: 0.1,  tonoMin: 0.86, tonoMax: 1.30 },', 1),
    ('canto: { nivel: 0.42, piso: 0.2,  tonoMin: 0.90, tonoMax: 1.18 },', 1),
    ('red:   { nivel: 0.5,  piso: 0.25, tonoMin: 0.88, tonoMax: 1.22 },', 1),
    ('suelo: { nivel: 0.42, piso: 0.05, tonoMin: 0.86, tonoMax: 1.18 },', 1),
    # NUEVO r59 · los lectores en c03 (muestra de las filas clave)
    ('this.master.gain.value = CONFIG_AUDIO.buses.master;   // r59: dato', 1),
    ('this.arcVol = CONFIG_AUDIO.canales.locutor;   // r59: fábrica de la tabla (el usuario manda después)', 1),
    ('const P = CONFIG_AUDIO.sfx.pala;   // r59: la fila MANDA', 1),
    ('const P = CONFIG_AUDIO.sfx.mesa;   // r59: la fila MANDA', 1),
    ('const P = CONFIG_AUDIO.sfx.canto;   // r59: la fila MANDA', 1),
    ('const P = CONFIG_AUDIO.sfx.red;   // r59: la fila MANDA', 1),
    ('const P = CONFIG_AUDIO.sfx.suelo;   // r59: la fila MANDA', 1),
    ('CONFIG_AUDIO.salon.base * this.musicVol', 1),
    ('CONFIG_AUDIO.musica.base * this.musicVol', 1),
    ('t + CONFIG_AUDIO.bso.reajusteMs / 1000);   // r59: dato (150 ms)', 1),
    ('_applyArcGain(ms = CONFIG_AUDIO.bso.reajusteMs)', 1),
    ('CONFIG_AUDIO.sfx.jitterBase +', 1),
    ('CONFIG_AUDIO.buses.murmullo.salidaS * 1000 + 100', 1),
    # CONSERVACIÓN r58 · CONFIG_MENU (el menú data-driven intacto)
    ('const CONFIG_MENU = {', 1),
    ("id: 'salirweb',", 1),
    ("urlDestino: 'AUTO_ORIGIN',", 1),
    ('tiempoMaxEsperaXRms: 2000,', 1),
    ("eventoTelemetria: 'salir_web',", 1),
    ('async salirALaWeb() {', 1),
    ('drawMenuSalidaAsk(rects) {', 1),
    ("hub_salirweb: 'SALIR A LA WEB',", 1),
    ("hub_salirweb: 'EXIT TO WEB',", 1),
    # CONSERVACIÓN r57 · R1 PASO_TUNE (pala con la base temporal de la física)
    ('const PASO_TUNE = { uiMax: 1 / 30, fisMax: 1 / 12 };', 1),
    ('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);', 1),
    ('updatePaddleSim(ps, grip.position, tmpMountQ, now, dtFis);', 1),
    # CONSERVACIÓN r57 · R2 margen de bote ALINEADO (3 simuladores)
    ('DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 &&', 3),
    # CONSERVACIÓN r56 · BOTE_TUNE / BOLA_TUNE
    ('const BOTE_TUNE = {', 1),
    ('const BOLA_TUNE = { spinGanancia: 0.45 };', 1),
    # CONSERVACIÓN r55 · ARCANO_CFG (capa de datos del Arcano intacta)
    ('const ARCANO_CFG = {', 1),
    ('const pwViva = (t) => (on || dlV) && t > 0;', 1),
    ('dur: ARCANO_CFG.ventanas.', 14),
    ('arcMesh.position.set(ARCANO_CFG.ui.buho.x, ARCANO_CFG.ui.buho.y,', 1),
    # CONSERVACIÓN r54 + FASE 145/144/143
    ('this._megaGasta(ent);   // r54 · la ACTIVACIÓN gasta su carga', 1),
    ('gunConsuma = this.champs.fireGun(i) === true;', 1),
    ("window.__PP_TELE.ev('anim_shield', { msg: sig });", 1),
    ("musica: 'assets/hall/cabana/cabana.mp3'", 1),
]

# AGUJAS por REGEX (patrón, esperado) — 44 lectores de CONFIG_AUDIO en c03
AGUJAS_RE = [
    (r'CONFIG_AUDIO\.buses\.\w+', 12),    # master+ambiente+reajusteFxS+compresor×5+murmullo×4
    (r'CONFIG_AUDIO\.canales\.\w+', 3),   # música/efectos/locutor (fábrica)
    (r'CONFIG_AUDIO\.musica\.\w+', 7),    # base×3 + reajusteS + entradaS + salidaS×2
    (r'CONFIG_AUDIO\.bso\.\w+', 7),       # reajusteMs×2 + entradaS + salidaS×2 + duck + restaura
    (r'CONFIG_AUDIO\.salon\.\w+', 5),     # base×2 + entradaS + salidaS×2
    (r'CONFIG_AUDIO\.sfx\.\w+', 10),      # abs×5 + filas×5
    (r'if \(pwViva\(this\._\w+T\)\)', 13),
    (r'\(on \|\| dlV\)', 1),
    (r'CONFIG_MENU\.salir', 8),
    (r'BOTE_TUNE\.\w+', 7),
    (r'PASO_TUNE\.\w+', 3),
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.150 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r59'
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
    (c02/c03) en test_r*.mjs + qa_sup1_v366.py. NUEVO r59 (lección r58):
    qa_r46_humo_gobernador.py viaja en la lista (versión dura)."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE — lección r57)
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.559.455 (etiqueta)
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
          '+ hashes COMPLETOS c02/c03 · qa_r46 incluido)')
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
    print(f'VERIFICACIÓN r59: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r59_audio)\n'
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
