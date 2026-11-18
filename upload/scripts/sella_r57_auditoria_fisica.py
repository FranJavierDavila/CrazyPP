#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r57_auditoria_fisica.py — FASE 151 · SELLADO VIVO a 3.6.148-SDK6.

TOP-3 DE LA AUDITORÍA DE FÍSICAS APLICADO (informe r56, pendiente futuro):

  · R1 · BASE TEMPORAL DE LA PALA (c12 + contrato en c04): la pala mide su
    velocidad/giro con la MISMA base temporal que la bola — dtFis
    (PASO_TUNE.fisMax, cap 1/12) — y no el dt de UI (cap 1/30). Con frames
    caídos de 33-83 ms el swing ya no se infla y el golpe no depende del
    lag del casco. Frames < 33 ms (72-120 Hz): idéntico bit a bit.
    PASO_TUNE (c12, patrón BOLA_TUNE r56): los dos caps del paso viven en
    tabla — uiMax 1/30 · fisMax 1/12.
  · R2 · GOLDEN c05 (scripts/test_fisica_c05.mjs + fisica_golden_c05.json):
    16 escenarios deterministas de stepPhysics/predictStrike/
    testPaddleContact/simulateServePath/computeShotVelocity (PRNG sembrado
    para el jitter de canto). MARGEN DE BOTE ALINEADO: la mesa real bota
    con |x| ≤ halfWidth + r·0,5 — ahora los TRES simuladores (predictStrike,
    simulateBounceUntilTable, simulateServePath) predicen con el mismo
    margen (antes daban por perdida la bola que sobresale media bola del
    canto). Único delta del golden: predictStrike.borde (null → punto).
  · R3 · MAGNUS ×1 PREDICHO vs ×2,2 REAL documentado (c02 fila +
    docs/SUPERPODER-DE-PALA.md §6): los simuladores predicen SIEMPRE con
    Magnus ×1 — a propósito: el rival no puede pre-leer la curva del
    Súper Efecto.
  · DEUDA r55 sanada: mod_fase2_analizar/generar.mjs auto-ubicables
    (import.meta.url) — generador + build byte-exacto verificados.

Este sellador (patrón sella_r56_fisica_datos; golden VIEJO capturado ANTES
de sobrescribir):
  · VERSION.json → 3.6.148-SDK6 · FASE 151 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden Y hashes de contrato
    (c04/c05/c12/c02) en test_r*.mjs + qa_sup1_v366.py
  · verifica AGUJAS sobre el game.html final (exit 1 si falla)

Uso: python3 scripts/sella_r57_auditoria_fisica.py
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
VIEJA, NUEVA = '3.6.147-SDK6', '3.6.148-SDK6'
FASE_VIEJA, FASE_NUEVA = 150, 151
VIEJO_NOMBRE = ('Data-driven FASE 150: BOTE_TUNE (física fina de c04) + BOLA_TUNE '
                '(giro visible de c12) — valores idénticos, golden 0 desviaciones')
NOMBRE = ('Auditoría de físicas r57 aplicada: R1 pala mide con la base temporal '
          'de la física (PASO_TUNE c12) · R2 golden c05 (16 escenarios) + margen '
          'de bote alineado en los 3 simuladores · R3 Magnus ×1 predicho vs '
          '×2,2 documentado')

# Hashes de contrato: COMPLETOS antes → después (los tests comparan el sha256
# entero, no sólo el prefijo) + reparación de «frankensteins» (prefijo nuevo
# + cola vieja, si un re-ancla de prefijos corrió antes) + prefijos al final.
# Sólo test_r*.mjs; los generadores de release históricos NO se tocan.
NOMBRE_CORRUPTO = ('Data-driven FASE 151: BOTE_TUNE (física fina de c04) + BOLA_TUNE '
                   '(giro visible de c12) — valores idénticos, golden 0 desviaciones')
HASHES = [
    # c02_cfg_escena.js (contrato r56 → r57)
    ('17e2e94a77599faade33c1bb0fca6d8a846e2eda27e497c71c8e6385e57d03c2',
     '24a3c7786f9ad387fbd78c3e95fe51aef754f8620f7baf7438d884941519ba75'),
    ('24a3c77877599faade33c1bb0fca6d8a846e2eda27e497c71c8e6385e57d03c2',
     '24a3c7786f9ad387fbd78c3e95fe51aef754f8620f7baf7438d884941519ba75'),
    ('17e2e94a', '24a3c778'),
    # c04_fisica_ccd.js
    ('e4abb6ebb55bcfa7d412df50f72e09c3afc44dc4f0390a5c85661d4b77be6eb2',
     'd792b5e777629d63c9e1dbfed4c7ae1ff2f1a7b3bcddd4c6b5c76486e575666d'),
    ('d792b5e7b55bcfa7d412df50f72e09c3afc44dc4f0390a5c85661d4b77be6eb2',
     'd792b5e777629d63c9e1dbfed4c7ae1ff2f1a7b3bcddd4c6b5c76486e575666d'),
    ('e4abb6eb', 'd792b5e7'),
    # c05_colisiones_ia_golpeo.js
    ('8bb620820e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65',
     'b195a0db04e0cdc2d9812c66b8c33decb2fac237643d936f84e55095decc73b3'),
    ('b195a0db0e4974d4ccab8308060d4b8fd7328c812b103f9309bd98654cf81d65',
     'b195a0db04e0cdc2d9812c66b8c33decb2fac237643d936f84e55095decc73b3'),
    ('8bb62082', 'b195a0db'),
    # c12_pingponggame.js
    ('eec88aee60e3705bda3867ccd53766972f197a407862f7fa3a871c544517d1e6',
     '515b5febafde44df99e627dcc16750b4cbcb678a799764c51a8a841e511eb4c2'),
    ('515b5feb60e3705bda3867ccd53766972f197a407862f7fa3a871c544517d1e6',
     '515b5febafde44df99e627dcc16750b4cbcb678a799764c51a8a841e511eb4c2'),
    ('eec88aee', '515b5feb'),
]

# AGUJAS exactas sobre el game.html ENSAMBLADO (aguja UTF-8, esperado; None = ≥1)
AGUJAS = [
    # NUEVO r57 · R1 — PASO_TUNE (c12) + la pala con la base de la física
    ('const PASO_TUNE = { uiMax: 1 / 30, fisMax: 1 / 12 };', 1),
    ('const dt = Math.min(_rawDt, PASO_TUNE.uiMax);', 1),
    ('const dtFis = Math.min(_rawDt, PASO_TUNE.fisMax);', 1),
    ('updatePaddleSim(ps, grip.position, tmpMountQ, now, dtFis);', 1),
    ('r57 · CONTRATO (auditoría R1)', 1),
    # NUEVO r57 · R2 — margen de bote ALINEADO en los 3 simuladores
    ('DIMS.tableHalfWidth + DIMS.ballRadius * 0.5 &&', 3),
    ('r57 · AUDITORÍA R2: el margen de bote en X', 1),
    # NUEVO r57 · R3 — Magnus ×1 predicho vs ×2,2 real (documentado en datos)
    ('r57 · AUDITORÍA R3: el ×2,2 sólo vuela en la bola MARCADA', 1),
    ('DIMS.efectoMagnusMul || 1.5', 1),
    # CONSERVACIÓN r56 · BOTE_TUNE (c04) + BOLA_TUNE (c12)
    ('const BOTE_TUNE = {', 1),
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
    ('const BOLA_TUNE = { spinGanancia: 0.45 };', 1),
    ('const BOLA_SPIN_GANANCIA = BOLA_TUNE.spinGanancia;', 1),
    # CONSERVACIÓN r55 · ARCANO_CFG (capa de datos del Arcano intacta)
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
    (r'PASO_TUNE\.\w+', 3),           # uiMax + fisMax (×2: dt y dtFis)
]


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.148 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r57'
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
    (c04/c05/c12/c02) en test_r*.mjs + qa_sup1_v366.py (lección r53: los QA
    Python con versión hardcodeada van en la lista)."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE: VIEJO_NOMBRE
        # contiene «FASE 150» y el reemplazo de número lo corrompería —
        # lección r57) — incluye la variante ya corrupta por una 1.ª pasada
        (VIEJO_NOMBRE, NOMBRE),
        (NOMBRE_CORRUPTO, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (NOMBRE_CORRUPTO.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.548.808 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
    # 2.º los hashes de contrato COMPLETOS (los tests comparan el sha256
    # entero) — los prefijos van al FINAL para no frankenstenizar
    cambios.extend(HASHES)
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
    print(f'· {n_fich} tests re-anclados (versión/fase/nombre/tamaño/golden '
          '+ hashes COMPLETOS c02/c04/c05/c12)')
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
    print(f'VERIFICACIÓN r57: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r57_auditoria_fisica)\n'
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
