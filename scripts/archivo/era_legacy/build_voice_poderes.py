#!/usr/bin/env python3
"""v3.6.28 · Inyecta los ÁTOMOS DE VOZ DE LOS SUPERPODERES DE PALA en el
banco de voz del juego (c00_pre_three.js · VOICE_B64 es-ES / VOICE_B64_EN
en-US). Clips generados con TTS (xiaochen es / jam en) y comprimidos a
Opus 28k mono — MISMO perfil que el banco del megáfono.

Uso:  python3 scripts/build_voice_poderes.py
Idempotente: los átomos existentes no se duplican.
"""
import base64
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
ORIGEN = RAIZ / 'scripts' / 'voice_poderes'
DESTINO = RAIZ / 'src' / 'game' / 'core' / 'c00_pre_three.js'

ATOMOS = {
    'VOICE_B64': [
        'poder_sin', 'poder_pala', 'poder_iman',
        'poder_efecto', 'poder_portal', 'poder_clon',
    ],
    'VOICE_B64_EN': [
        'poder_sin', 'poder_pala', 'poder_iman',
        'poder_efecto', 'poder_portal', 'poder_clon',
    ],
}
SUFIJO = {'VOICE_B64': '_es', 'VOICE_B64_EN': '_en'}


def b64_oggs(base: Path, claves, sufijo):
    out = []
    for k in claves:
        p = base / f'{k}{sufijo}.ogg'
        if not p.exists():
            sys.exit(f'FALLO: falta el clip {p}')
        datos = p.read_bytes()
        cod = base64.b64encode(datos).decode('ascii')
        assert '</' not in cod, 'base64 no puede contener </'
        out.append((k, cod, len(datos)))
    return out


def inyectar(texto: str, banco: str, pares):
    # localiza «export const <banco> = {» y su cierre «};» al inicio de línea
    m = re.search(r'^export const ' + banco + r' = \{\n', texto, re.M)
    if not m:
        sys.exit(f'FALLO: no se encuentra export const {banco} = {{')
    ins = m.end()
    fin = texto.find('\n};', ins)
    if fin < 0:
        sys.exit(f'FALLO: sin cierre para el banco {banco}')
    bloque = texto[ins:fin]
    ya = {k for k, _, _ in pares if re.search(r'^  ' + k + r': "', bloque, re.M)}
    lineas = []
    for k, cod, n in pares:
        if k in ya:
            print(f'  · {banco}.{k} ya estaba — se omite')
            continue
        lineas.append(f'  {k}: "{cod}",')
        print(f'  + {banco}.{k} ({n} B ogg → {len(cod)} B b64)')
    if not lineas:
        return texto, 0
    bloque = '\n'.join(lineas) + '\n'
    return texto[:ins] + bloque + texto[ins:], len(lineas)


def main():
    texto = DESTINO.read_text(encoding='utf-8')
    total = 0
    for banco, claves in ATOMOS.items():
        pares = b64_oggs(ORIGEN, claves, SUFIJO[banco])
        texto, n = inyectar(texto, banco, pares)
        total += n
    if total:
        DESTINO.write_text(texto, encoding='utf-8')
    print(f'OK · {total} átomos inyectados en {DESTINO.name}')


if __name__ == '__main__':
    main()
