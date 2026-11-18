#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r60_dificultad.py — FASE 154 · SELLADO VIVO a 3.6.151-SDK6.

CONFIG_DIFICULTAD · LA DIFICULTAD ES DATA-DRIVEN (petición del dueño:
«seguir extendiendo el patrón data-driven a otro subsistemas» — quinta
parada tras ARCANO_CFG/física/menú/audio):

  · CONFIG_DIFICULTAD (c02, patrón ARCANO_CFG/CONFIG_MENU/CONFIG_AUDIO) —
    ÚNICA FUENTE DE VERDAD DE LA DIFICULTAD: presets (las tres curvas de
    la CPU), saque (asistencia por dificultad), escala (topes y
    exponentes de scalePreset), elo (anclas CPU · K por modo · paso/piso/
    inicial · bandas del matchmaking), adaptativo (paso por punto y tope),
    supervivencia (rampa por rallye y techo) y esfuerzo (la fórmula r113
    del fallo de la CPU INTELIGENTE, c06).
  · ALIAS del contrato (patrón FASE 149): AI_PRESETS / SERVE_ASSIST_TIERS
    / ELO_CPU se vuelven alias de la tabla — c12/c13/tests/__PP_ELO
    siguen importando el nombre histórico.
  · 12 lectores enchufados: c02 (scalePreset · rivalPorElo), c06
    (constructor ELO · migración · recordMatch · fórmula esfuerzo) y c12
    (adaptativo · supervivencia · rango legal del k).
  · RE-ANCLES r60: test_r39 (import de c12 con CONFIG_DIFICULTAD) y
    qa_r113 (agujas CPU a la forma dato).

Este sellador (patrón sella_r59_audio; golden VIEJO capturado ANTES de
sobrescribir):
  · VERSION.json → 3.6.151-SDK6 · FASE 154 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden Y hash de contrato (c02)
    en test_r*.mjs + qa_sup1_v366.py + qa_r46_humo_gobernador.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r60_dificultad.py
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
VIEJA, NUEVA = '3.6.150-SDK6', '3.6.151-SDK6'
FASE_VIEJA, FASE_NUEVA = 153, 154
VIEJO_NOMBRE = ('CONFIG_AUDIO r59: la MEZCLA de audio es data-driven — buses+compresor+'
                'murmullo · canales de fábrica música/efectos/locutor · fundidos menú/BSO/'
                'salón con timeouts derivados · SFX pala/mesa/canto/red/suelo (nivel/piso/'
                'tono) · clamps + jitter como datos (44 lectores en c03)')
NOMBRE = ('CONFIG_DIFICULTAD r60: la DIFICULTAD es data-driven — presets (curvas CPU '
          'easy/medium/hard) · asistencia de saque por nivel · topes/exponentes de '
          'scalePreset · ELO (anclas/K por modo/paso/bandas matchmaking) · adaptativo · '
          'supervivencia · fórmula de esfuerzo r113 (12 lectores c02/c06/c12 · alias '
          'AI_PRESETS/SERVE_ASSIST_TIERS/ELO_CPU)')

# Hash de contrato: c02 (tabla + alias + scalePreset + rivalPorElo). c06/c12
# cambian pero NINGÚN test lleva sus hashes (verificado por grep r60).
HASHES_VIEJOS_NUEVOS = [
    # c02_cfg_escena.js (CONFIG_DIFICULTAD)
    ('f40acc1a8a6a08c26c6fe4bff39f11dd6dae9ec763356784b8b3bb1169a096ba',
     '22b0378157603614df075ba9f69b84ab45000cc02ab15a394191989fe238d63b'),
]

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO r60 · CONFIG_DIFICULTAD: la tabla (el ensamblador quita el export)
    ('const CONFIG_DIFICULTAD = {', 1),
    ('presets: {', 1),
    ('easy:   { maxSpeed: 2.0, accel: 6,  errStd: 0.09,  missBase: 0.15, minT: 0.62, maxT: 0.88, maxShotSpeed: 4.8, predictInterval: 0.16, smash: 0.04, short: 0.03 },', 1),
    ('medium: { maxSpeed: 2.7, accel: 9,  errStd: 0.05,  missBase: 0.08, minT: 0.52, maxT: 0.78, maxShotSpeed: 6.2, predictInterval: 0.10, smash: 0.15, short: 0.05 },', 1),
    ('hard:   { maxSpeed: 3.8, accel: 14, errStd: 0.024, missBase: 0.03, minT: 0.42, maxT: 0.62, maxShotSpeed: 10,  predictInterval: 0.06, smash: 0.30, short: 0.06 },', 1),
    ('saque: {', 1),
    ('easy:   { reach: 0.060, vy: 3.5,  angleMul: 1.4,  assistMul: 1.35 },', 1),
    ('escala: {', 1),
    ('kMin: 0.7, kMax: 2.2,        // rango legal del factor k (invariante del arnés)', 1),
    ('elo: {', None),   # la tabla + otros bloques ELO históricos
    ('cpu: { easy: 900, medium: 1050, hard: 1200 },', 1),
    ('kModo: { ia: 24, carrera: 20, p2p: 32 },', 1),
    ('adaptativo: { pasoSube: 0.055, pasoBaja: 0.05, topeDif: 6 },', 1),
    ('supervivencia: { porRallye: 0.08, techo: 2.1 },', 1),
    ('esfuerzo: {', 1),
    ('baseFrac: 0.25,', 1),
    ('tope: 0.85,                // techo honesto del fallo decidido', 1),
    ('cooldownS: 0.55,', 1),
    # NUEVO r60 · ALIAS del contrato (patrón FASE 149)
    ('const AI_PRESETS = CONFIG_DIFICULTAD.presets;', 1),
    ('const SERVE_ASSIST_TIERS = CONFIG_DIFICULTAD.saque;   // r60: dato', 1),
    ('const ELO_CPU = CONFIG_DIFICULTAD.elo.cpu;   // r60: dato', 1),
    # NUEVO r60 · lectores en c02 (scalePreset · rivalPorElo)
    ('const E = CONFIG_DIFICULTAD.escala;   // r60: topes y exponentes como datos', 1),
    ('const M = CONFIG_DIFICULTAD.elo;   // r60: bandas, jitter y paso como datos', 1),
    # NUEVO r60 · lectores en c06 (ELO + esfuerzo)
    ('elo: CONFIG_DIFICULTAD.elo.inicial,   // r60: dato (fábrica del número)', 1),
    ('this.data.elo = CONFIG_DIFICULTAD.elo.inicial;   // r60: dato', 1),
    ('const M = CONFIG_DIFICULTAD.elo;   // r60: el K por modo y los límites del número viven en datos', 1),
    ('this.data.elo = Math.max(M.piso, miElo + delta);   // r60: piso de la tabla', 1),
    ('const EF = CONFIG_DIFICULTAD.esfuerzo;   // r60: la fórmula del fallo vive en datos', 1),
    ('this.cfg.missBase * EF.baseFrac +', 1),
    ('Math.max(0, ballSpeed - EF.velUmbral) * EF.velPaso +', 1),
    ('Math.max(0, viaje - EF.viajeUmbral) * EF.viajePaso +', 1),
    ('this.hitCooldown = EF.cooldownS;   // r60: cadencia de la tabla', 1),
    # NUEVO r60 · lectores en c12 (adaptativo · supervivencia · rango k)
    ('const AD = CONFIG_DIFICULTAD.adaptativo;   // r60: el paso vive en datos', 1),
    ('const SV = CONFIG_DIFICULTAD.supervivencia;   // r60: la rampa vive en datos', 1),
    ('const ES = CONFIG_DIFICULTAD.escala;   // r60: rango legal de la tabla', 1),
    # (el import de c12 con CONFIG_DIFICULTAD lo vigila test_r39 sobre el
    #  FUENTE — el bloque DEPS-FASE2 no viaja en el ensamblado)
    # CONSERVACIÓN r59 · CONFIG_AUDIO (la mezcla data-driven intacta)
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

# AGUJAS por REGEX (patrón, esperado)
AGUJAS_RE = [
    # NUEVO r60 · los 12 lectores de CONFIG_DIFICULTAD
    (r'CONFIG_DIFICULTAD\.\w+', 12),
    (r'CONFIG_DIFICULTAD\.presets\b', 1),
    (r'CONFIG_DIFICULTAD\.saque\b', 1),
    (r'CONFIG_DIFICULTAD\.escala\b', 2),      # scalePreset (c02) + rango k (c12)
    (r'CONFIG_DIFICULTAD\.elo\b', 5),         # alias + rivalPorElo + recordMatch + inicial ×2
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
    """VERSION.json + c00 + badge + sw → 3.6.151 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r60'
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
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.563.859 (etiqueta)
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
    print(f'VERIFICACIÓN r60: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r60_dificultad)\n'
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
