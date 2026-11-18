#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r62 · INSERTA el const PP_SFX_REALES_B64 en src/game/core/c03_audio_voz.js
===========================================================================
- La muestra vive DESPUÉS del bloque DEPS-FASE2-FIN (lección r61: el bloque
  generado se regenera — nada útil dentro).
- IDEMPOTENTE: entre marcadores /* PP_SFX_REALES-INICIO ... FIN *​/ se
  sustituye entero; si no existen, se inserta tras DEPS-FASE2-FIN.
- Verifica al final que el fichero sigue siendo JS importable (llaves,
  tamaño, marcadores).
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C03 = os.path.join(BASE, 'src', 'game', 'core', 'c03_audio_voz.js')
B64 = os.path.join(BASE, 'scripts', 'sfx_r62', 'base64.json')

INI = '/* PP_SFX_REALES-INICIO (generado por scripts/_r62_insertar_sfx.py — no editar a mano) */'
FIN = '/* PP_SFX_REALES-FIN */'
DEPS_FIN = '/* DEPS-FASE2-FIN */'


def bloque(b64):
    lineas = [INI, '// r62 · MUESTRAS SFX REALES (síntesis modal física, semilla 62) —',
              '// WAV 44100 Hz · mono · 16-bit PCM en base64. Bola de ping pong de 40 mm',
              '// contra cada superficie: modos de la cáscara + transitorio de contacto +',
              '// cuerpo de la superficie (gen_sfx_r62.py). Fallback: síntesis previa.',
              'const PP_SFX_REALES_B64 = {']
    for k in ('mesa', 'pala', 'canto', 'red', 'suelo'):
        lineas.append(f"  {k}: '{b64[k]}',")
    lineas += ['};', FIN, '']
    return '\n'.join(lineas)


def main():
    with open(B64) as f:
        b64 = json.load(f)
    for k in ('mesa', 'pala', 'canto', 'red', 'suelo'):
        assert k in b64 and len(b64[k]) > 1000, f'falta base64 de {k}'
    with open(C03, encoding='utf-8') as f:
        src = f.read()

    if INI in src:
        i = src.index(INI)
        j = src.index(FIN, i) + len(FIN)
        nuevo = src[:i] + bloque(b64) + src[j:]
        print('c03: bloque PP_SFX_REALES SUSTITUIDO (idempotente)')
    else:
        if DEPS_FIN not in src:
            sys.exit('FALTA el marcador DEPS-FASE2-FIN en c03')
        i = src.index(DEPS_FIN) + len(DEPS_FIN)
        nuevo = src[:i] + '\n' + bloque(b64) + src[i:]
        print('c03: bloque PP_SFX_REALES INSERTADO tras DEPS-FASE2-FIN')

    with open(C03, 'w', encoding='utf-8') as f:
        f.write(nuevo)

    # verificación
    with open(C03, encoding='utf-8') as f:
        chk = f.read()
    assert chk.count(INI) == 1 and chk.count(FIN) == 1, 'marcadores duplicados'
    assert chk.index(INI) > chk.index(DEPS_FIN), 'el bloque quedó DENTRO de DEPS-FASE2'
    assert 'const PP_SFX_REALES_B64 = {' in chk, 'const ausente'
    for k in ('mesa', 'pala', 'canto', 'red', 'suelo'):
        assert f"  {k}: '" in chk, f'clave {k} ausente'
    print(f"c03 verificado: {len(chk)} bytes · const tras DEPS-FASE2-FIN · "
          f"5 muestras presentes")


if __name__ == '__main__':
    main()
