#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · r29 (v3.6.125, FASE 127) — SWAP de assets EMBEBIDOS en
c12_pingponggame.js (una línea por constante, mismas anclas que r25/r26b):

  · ICONOS del dueño  : PNG_PODER_FENIX / PNG_PODER_CRONO (nuevos PNG) y
    PNG_PODER_HIELO → PNG_PODER_OSCURIDAD (el Hielo se ANULA).
  · VOCES PIPER de la casa (davefx/lessac — la voz animosa de siempre):
    VOZ_PODER_FENIX(+EN) · VOZ_PODER_CRONO(+EN) · VOZ_PODER_RED(+EN) ·
    VOZ_PODER_ELEC(+EN) · VOZ_PODER_HIELO(+EN) → VOZ_PODER_OSCURIDAD(+EN).

Idempotente por construcción (reemplaza el literal completo de la línea).
"""
import re
from base64 import b64encode
from pathlib import Path

C12 = Path('/home/z/my-project/upload/src/game/core/c12_pingponggame.js')
A = Path('/home/z/my-project/upload/scripts/_r29_assets')


def duri(p, mime):
    return f'data:{mime};base64,' + b64encode(p.read_bytes()).decode('ascii')


def main():
    src = C12.read_text(encoding='utf-8')

    # — 1) sustituciones directas (línea entera por nombre de constante) —
    directos = {
        'PNG_PODER_FENIX': duri(A / 'icon_fenix.png', 'image/png'),
        'PNG_PODER_CRONO': duri(A / 'icon_crono.png', 'image/png'),
        'VOZ_PODER_FENIX': duri(A / 'voz_fenix_es.mp3', 'audio/mpeg'),
        'VOZ_PODER_FENIX_EN': duri(A / 'voz_fenix_en.mp3', 'audio/mpeg'),
        'VOZ_PODER_CRONO': duri(A / 'voz_crono_es.mp3', 'audio/mpeg'),
        'VOZ_PODER_CRONO_EN': duri(A / 'voz_crono_en.mp3', 'audio/mpeg'),
        'VOZ_PODER_RED': duri(A / 'voz_red_es.mp3', 'audio/mpeg'),
        'VOZ_PODER_RED_EN': duri(A / 'voz_red_en.mp3', 'audio/mpeg'),
        'VOZ_PODER_ELEC': duri(A / 'voz_elec_es.mp3', 'audio/mpeg'),
        'VOZ_PODER_ELEC_EN': duri(A / 'voz_elec_en.mp3', 'audio/mpeg'),
    }
    n_sust = 0
    for nombre, uri in directos.items():
        patron = re.compile(rf"^const {nombre} = 'data:[^']+';$", re.M)
        if not patron.search(src):
            raise SystemExit(f'ANCLA NO ENCONTRADA: {nombre}')
        src = patron.sub(f"const {nombre} = '{uri}';", src, count=1)
        n_sust += 1

    # — 2) HIELO → OSCURIDAD: la línea del PNG se renombra con el icono del
    #      dueño; las dos líneas de voz (ES/EN) se renombran con las nuevas —
    viejos = {
        'PNG_PODER_HIELO': ('PNG_PODER_OSCURIDAD',
                            duri(A / 'icon_oscuridad.png', 'image/png')),
        'VOZ_PODER_HIELO': ('VOZ_PODER_OSCURIDAD',
                            duri(A / 'voz_oscuridad_es.mp3', 'audio/mpeg')),
        'VOZ_PODER_HIELO_EN': ('VOZ_PODER_OSCURIDAD_EN',
                               duri(A / 'voz_oscuridad_en.mp3', 'audio/mpeg')),
    }
    for viejo, (nuevo, uri) in viejos.items():
        patron = re.compile(rf"^const {viejo} = 'data:[^']+';$", re.M)
        if not patron.search(src):
            raise SystemExit(f'ANCLA NO ENCONTRADA: {viejo}')
        src = patron.sub(f"const {nuevo} = '{uri}';", src, count=1)
        n_sust += 1

    C12.write_text(src, encoding='utf-8')
    print(f'OK · {n_sust} constantes de assets sustituidas/renombradas')

    # — verificación rápida —
    for chk in ('PNG_PODER_OSCURIDAD', 'VOZ_PODER_OSCURIDAD',
                'VOZ_PODER_OSCURIDAD_EN'):
        assert f"const {chk} = 'data:" in src, f'falta {chk}'
    assert 'PNG_PODER_HIELO' not in src, 'quedó PNG_PODER_HIELO'
    assert 'VOZ_PODER_HIELO' not in src, 'quedó VOZ_PODER_HIELO'
    print('VERIFICADO: OSCURIDAD presente · HIELO ausente')


if __name__ == '__main__':
    main()
