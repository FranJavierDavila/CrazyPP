#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_duelo_r110 — CAPA GATE · V3.6.100-SDK6, r110 «DUELO REPARADO».

Informe del dueño tras una partida real con amigos: «es imposible golpear
la bola… las palas no aparecen donde deberían… veo su pelota cuando mueve
su pala». Causa raíz encontrada y reparada en r110:
  1 · BIT 4 DE POSE: el emisor lo ponía con la pala en CUALQUIER mano; los
      3 lectores lo interpretan como «pala en la mano IZQUIERDA (slot 0)».
      Un jugador diestro (el 95 %) viajaba mal leído: el rival pintaba su
      pala en la MANO LIBRE (donde está la bola del saque — «veo su
      pelota») y el validador §12 comparaba cada golpe contra la mano
      equivocada (rechazos masivos: «la bola cae irremediablemente»).
  2 · VALIDADOR: MAX_SPIN/TOL_FUTURE/HIT_NEAR_PAD rechazaban golpes
      legítimos con latencia/efecto real.
  3 · FANTASMA INJUGABLE: el fantasma se simulaba SIN palas aunque la bola
      ya estuviera EN MI MITAD (ventana muerta de RTT..300 ms por golpeo).
  4 · SAQUE ATASCADO: si el TOSS/HIT del saque rival se perdía, mi bola
      quedaba HELD para siempre → reparación por SNAPs del rival.

ESTA CAPA corre el BANCO DE DUELO en Node (scripts/diag_multijugador_r110.mjs):
código REAL de producción (c09 NetLink + c09b PPNET + física c04/c05 + c02)
con dos extremos completos sobre un cable simulado (40 ms ±12 ms, pérdida
1 % en fast), verificando:
  S1 · espejo de pose EXACTO diestro y zurdo (posición 0 cm ±2 · ángulo <3°)
  S2 · saque legal (solucionador real) → cruce → autoridad del invitado →
       CONTACTO del invitado → validación del anfitrión 0 rechazos.
Ejecución: node --no-warnings (sin visor, sin red real) · ~40 s.
"""
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
BANCO = RAIZ / 'scripts' / 'diag_multijugador_r110.mjs'
SB = RAIZ / 'scripts' / 'ppdiag'
CORE = RAIZ / 'src' / 'game' / 'core'
REALES = ['c02_cfg_escena.js', 'c04_fisica_ccd.js', 'c05_colisiones_ia_golpeo.js',
          'c09_red_netlink.js', 'c09b_red_nucleo.js']


def prepara_sandbox():
    """Copia los módulos REALES de src al sandbox Node (stubs c00/c01 incluidos).
    Se rehace SIEMPRE: el sandbox corre siempre el código vivo del árbol."""
    SB.mkdir(exist_ok=True)
    for f in REALES:
        shutil.copy2(CORE / f, SB / f)
    (SB / 'c00_pre_three.js').write_text('export const T = (k, p) => k;\n', encoding='utf-8')
    (SB / 'c01_modelos_3d.js').write_text(
        'export const PALA_SCALE = 0.026;\n'
        'export const PALA_GRIP_Y = -2.9;\n'
        'export const PALA_BLADE_Y = 2.1115;\n', encoding='utf-8')


def main():
    prepara_sandbox()
    if not BANCO.exists():
        print('✗ FALLO: no existe el banco de duelo', BANCO)
        return 1
    try:
        r = subprocess.run(
            ['node', '--no-warnings', str(BANCO)],
            capture_output=True, text=True, timeout=220, cwd=str(RAIZ),
        )
    except subprocess.TimeoutExpired:
        print('✗ FALLO: el banco de duelo excedió 220 s')
        return 1
    out = (r.stdout or '') + (r.stderr or '')
    print(out.strip()[-2600:])
    ok = r.returncode == 0 and out.count('✓') >= 9 and '✗ FALLO' not in out
    print()
    if ok:
        print('✓ CAPA r110 VERDE: enlace v2 + espejo de pose exacto + duelo con saque,')
        print('  autoridad, contacto del invitado y 0 rechazos del validador.')
        return 0
    print('✗ CAPA r110 EN FALLO: revisar el banco de duelo arriba.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
