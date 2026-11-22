#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sella_r65_saque.py — FASE 159 · SELLADO VIVO a 3.6.156-SDK6.

EL SAQUE VUELVE A LA MANO · r65 — BLINDAJE DEL SAQUE EN 4 CAPAS
(petición del dueño, MÁXIMA PRIORIDAD: «no se puede sacar, por alguna
razón la pelota aparece detrás del jugador y no en su mano y no responde
a los controles correctamente, por lo visto es solo en el saque»).

Diagnóstico r65: el pegado bola→mano exige MUCHAS guardias a la vez
(presenting · frozen · netFrozen · inHall · _netStart · estado/servidor ·
bh.active · pose fresca) y el lanzamiento vivía AL FINAL de la cadena del
gatillo (replayConsume v3.6.31 compite en 'serve'; hand.active podía negar
el saque natural con un connected[] desactualizado). Cualquier guardia que
fallara en el casco dejaba la bola donde murió el punto anterior — a
menudo detrás del jugador — y el punto bloqueado. Los caminos estáticos
están BIEN (QA verde r64): el fallo es de dispositivo, así que el fix es
DEFENSA EN PROFUNDIDAD (c12, cero cambios data-driven, cero i18n):

  · CAPA 1 · GATILLO SAQUE-PRIMERO: en 'serve' del jugador el gatillo
    lanza SIEMPRE y ANTES de gunArmed/replayConsume/arkanoid/over — la
    reordenación que el cartel del superpoder (v3.6.35) ya prometía
    («En 'serve' el gatillo sigue SIENDO DEL SAQUE — cero conflicto»).
    Misma condición que la rama del final: reordenación pura.
  · CAPA 2 · RESPALDO RELATIVO A LA CABEZA: el punto fijo viejo
    (0,3 · 1,05 · fondo+0,4) podía quedar DETRÁS del jugador (el museo
    mueve el rig con enterHall/exitHall y el casco no re-centra al
    arrancar partida). Ahora nace 0,35 m por delante de la mirada y a la
    altura del pecho: SIEMPRE delante del jugador.
  · CAPA 3 · POSE FRESCA + GRIP VIVO: la pose del mando libre se acepta
    sólo con seenT < 400 ms (el bucle de mandos sella ps.seenT cada frame;
    un 'connected' sobrevive a un mando dormido/reemparejado) y el saque
    natural por grip ya NO exige hand.active — el evento squeeze es prueba
    vivísima de que el mando responde. La velocidad sigue siendo la REAL
    de la mano (requisito A v3.1.0-SRV2 intacto).
  · CAPA 4 · WATCHDOG «LA BOLA SIEMPRE VUELVE A TU MANO»: corre FUERA de
    las guardias del pegado; si el jugador es el sacador, la bola está en
    saque y NO está en la mano libre durante ~1 s, la DEVUELVE a la mano
    (pose fresca) o delante de la mirada (capa 2) y anula su velocidad.
    En el camino feliz es un no-op (distancia < 0,45 m cada frame).

Además (telemetría, «receptor no responde»): el receptor de producción
está VIVO (latido 200 OK · CORS * · último registro 15 h antes del
informe) — el panel telemetria.html ahora DICE QUÉ receptor probó
(«receptor no responde · probó <origen><ruta>») para destapar al instante
una pp_tele_url vieja guardada en localStorage.

Este sellador (patrón sella_r64_medallas; golden VIEJO capturado ANTES de
sobrescribir; agujas de conservación r64 importadas de SU módulo — cero
transcripción):
  · VERSION.json → 3.6.156-SDK6 · FASE 159 (sdk 1.6.0, fecha hoy)
  · c00_pre_three.js VERSION + badge de 03_body.html + CACHE de sw.js
  · ensambla public/game.html y fija el golden real
  · re-ancla versión/fase/nombre/tamaño/golden en test_r*.mjs +
    qa_sup1_v366.py + qa_r46_humo_gobernador.py (c02 SIN cambio en r65:
    el hash de contrato 2d9496cb… queda intacto — la edición vive en c12)
  · verifica AGUJAS sobre el game.html final, incl. la NEGATIVA del punto
    fijo viejo (exit 1 si falla)

Uso: python3 scripts/sella_r65_saque.py
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
VIEJA, NUEVA = '3.6.155-SDK6', '3.6.156-SDK6'
FASE_VIEJA, FASE_NUEVA = 158, 159
VIEJO_NOMBRE = ('CONFIG_MEDALLAS r64: MEDALLAS POR EJERCICIO DATA-DRIVEN — la escalera bronce/plata/oro '
                '(estrellas 1/2/3 · precisión 70/85) de medallaDe vive en c02 — novena parada tras ARCANO_CFG/'
                'física/menú/audio/dificultad/torneos+logros/pieles/rally (lector c13: MDE/MDP = '
                'CONFIG_MEDALLAS.estrellas/.precision — HUD, MEDALLERO y or5 intactos)')
NOMBRE = ('EL SAQUE VUELVE A LA MANO r65: blindaje del saque en 4 capas — gatillo SAQUE-PRIMERO '
          '(el lanzamiento ya no compite con replayConsume/arma del Oeste), respaldo del saque RELATIVO A '
          'LA CABEZA (el punto fijo 0,3·1,05·fondo+0,4 podía quedar detrás del jugador), pose del mando '
          'con FRESCURA de 400 ms, grip vivo (el evento squeeze es prueba de liveness) y WATCHDOG '
          'bola→mano (saque atascado = la bola vuelve a la mano libre en ~1 s — petición del dueño: '
          '«la pelota aparece detrás del jugador y no responde a los controles»)')

# Hash de contrato: c02 SIN CAMBIO en r65 (la edición vive en c12). El par
# 2d9496cb… sellado en r64 queda intacto y ningún test se re-ancla en él.
HASHES_VIEJOS_NUEVOS = []

# Agujas de conservación r64 importadas de SU sellador (misma fuente).
_spec64 = importlib.util.spec_from_file_location(
    's64', RAIZ / 'scripts' / 'sella_r64_medallas.py')
s64 = importlib.util.module_from_spec(_spec64)
_spec64.loader.exec_module(s64)

# AGUJAS r65 — conteos MEDIDOS sobre ensamblado en memoria
# (scripts/_r65_mide_agujas.py — método r63/r64).
AGUJAS = [
    # CAPA 1 · gatillo SAQUE-PRIMERO
    ('EL SAQUE ES EL DUEÑO DEL GATILLO', 1),
    ('this.tossFromHand(this.ballHand, true);', 2),
    # CAPA 2 · respaldo relativo a la cabeza (pegado del saque)
    ('r65 · la pose del mando libre debe ser VÁLIDA', 1),
    ('r65 · RESPALDO EN LA MANO VIRTUAL DEL JUGADOR', 1),
    ('const fSrv = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);', 1),
    ('this.ball.pos.copy(this.camera.position).addScaledVector(fSrv, 0.35);', 1),
    # CAPA 3 · grip vivo
    ('r65 · el EVENTO squeeze acaba de llegar de ESTE mando', 1),
    # CAPA 4 · watchdog bola→mano
    ('r65 · WATCHDOG DEL SAQUE', 1),
    ('LA BOLA SIEMPRE VUELVE A TU MANO', 1),
    ('const bhW = this.controllerPaddles[this.ballHand];', 1),
    ('const fWd = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);', 1),
    ('this.ball.pos.copy(this.camera.position).addScaledVector(fWd, 0.35);', 1),
    ('this._srvWdT = cerca ? 0 : (this._srvWdT || 0) + dt;', 1),
    ('this._srvWdT > 1.0', 1),
    # helper común de validez de pose (frescura 400 ms + plausibilidad 2,2 m)
    ('r65 · validez de la pose del mando libre para el SAQUE', 1),
    ('_srvManoValida(bh) {', 1),
    ('return bh.pos.distanceTo(this.camera.position) < 2.2;', 1),
    # frescura de pose en el bucle de mandos
    ('ps.seenT = performance.now();', 1),
    # compartidos (pegado + watchdog)
    ('this.ball.pos.y = Math.max(0.55, this.ball.pos.y - 0.55);', 3),
    # CAPA 2+3 · la misma armadura en el guardián ONLINE (_bolaGuard r25)
    ('r65 · misma armadura que el pegado local', 1),
    ('const fBg = tmpV.set(0, 0, -1).applyQuaternion(this.camera.quaternion);', 1),
    ('this.ball.pos.copy(this.camera.position).addScaledVector(fBg, 0.35);', 1),
    # CONSERVACIÓN r25 · en ESCRITORIO (sin visor) el punto reglamentario
    # se queda (r25: «escritorio: punto de saque reglamentario») — el
    # respaldo de cabeza es SOLO para VR (allí la cámara es la orbital)
    ('this.ball.pos.set(0.3, 1.05, D.tableCenterZ + D.tableHalfLength + 0.4);', 1),
    # NEGATIVA r65 · el punto fijo viejo HA DE HABER DESAPARECIDO del
    # pegado LOCAL (la variante D.* de escritorio en _bolaGuard es la de r25)
    ('this.ball.pos.set(0.3, 1.05, DIMS.tableCenterZ + DIMS.tableHalfLength + 0.4)', 0),
] + list(s64.AGUJAS)

AGUJAS_RE = [
    # r65 · identificadores nuevos (sin colisión histórica: _srvWdT y seenT
    # nacen aquí; tossFromHand(this.ballHand, true) 1→2 con el saque-primero;
    # el punto fijo viejo →0 en el pegado LOCAL — queda ×1 SOLO el punto
    # reglamentario de ESCRITORIO en _bolaGuard (r25, con alias D.*))
    (r'_srvWdT', 4),
    (r'_srvManoValida', 6),
    (r'seenT', 4),
    (r'distanceTo\(this\.camera\.position\)', 1),
    (r'addScaledVector\(f\w+, 0\.35\)', 3),
    (r'tossFromHand\(this\.ballHand, true\)', 2),
    (r'this\.ball\.pos\.set\(0\.3, 1\.05', 1),
] + list(s64.AGUJAS_RE)


def sella_sellos() -> None:
    """VERSION.json + c00 + badge + sw → 3.6.156 (idempotente)."""
    vj = SRC / 'VERSION.json'
    vdat = json.loads(vj.read_text(encoding='utf-8'))
    vdat['version'] = NUEVA
    vdat['fase'] = FASE_NUEVA
    vdat['faseNombre'] = NOMBRE
    vdat['sdk'] = '1.6.0'
    vdat['fecha'] = time.strftime('%Y-%m-%d')
    vdat['nota'] = 'r65'
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
    qa_sup1_v366.py + qa_r46_humo_gobernador.py (c02 intacto en r65)."""
    cambios = [
        # 1.º los NOMBRES (antes que los reemplazos de FASE — lección r57)
        (VIEJO_NOMBRE, NOMBRE),
        (VIEJO_NOMBRE.upper(), NOMBRE.upper()),
        (VIEJA, NUEVA),
        (f'fase === {FASE_VIEJA}', f'fase === {FASE_NUEVA}'),
        (f'FASE {FASE_VIEJA}', f'FASE {FASE_NUEVA}'),
        (str(tamano_viejo), str(tamano)),          # vjson.tamano (crudo)
        (f'{tamano_viejo:,}'.replace(',', '.'),     # 11.582.172 (etiqueta)
         f'{tamano:,}'.replace(',', '.')),
    ]
    if golden_viejo and golden_viejo != sha:
        cambios.append((golden_viejo, sha))
        cambios.append((golden_viejo[:16], sha[:16]))
        cambios.append((golden_viejo[:8], sha[:8]))
    # hashes de contrato: r65 NO toca c02 — sin pares (patrón r64, vacío)
    for viejo, nuevo in HASHES_VIEJOS_NUEVOS:
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
          f'· c02 intacto — sin pares de hash en r65)')
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
    print(f'VERIFICACIÓN r65: {"TODO OK" if ok else "FALLO"}')
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
        '(build_game.py — regenerado por sella_r65_saque)\n'
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
