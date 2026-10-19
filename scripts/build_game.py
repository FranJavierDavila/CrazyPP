#!/usr/bin/env python3
"""
CRAZY PING PONG · ENSAMBLADOR DEL JUEGO (fase 1 de modularización P0).
Reconstruye public/game.html a partir de src/game/ (wrappers + 14 subsistemas
en core/). Es el ÚNICO camino legítimo para cambiar el juego: se edita el
subsistema en src/game/core/, se ejecuta este script y game.html se regenera.

Uso:
  python3 scripts/build_game.py            # ensaya y compara con el SHA dorado
  python3 scripts/build_game.py --escribir # escribe public/game.html

Garantías:
  · Orden fijo de piezas (ORDER) — un fichero nuevo en core/ NO entra solo.
  · Token de identidad en la primera línea de cada pieza.
  · Si el resultado coincide con src/game/GOLDEN_SHA256.txt → «BYTE-EXACTO».
  · Sin --escribir no toca public/ (ensayo seguro).

FASE 2 (build de inserción): los subsistemas de core/ son MÓDULOS ES reales
(bloques de import generados marcados con DEPS-FASE2 + prefijos export).
Al ensamblar, este script aplica la transformación inversa sobre las piezas
core/: quita los bloques marcados y los prefijos `export ` de columna 0, de
modo que game.html sale BYTE-EXACTO con el mismo ámbito compartido de
siempre. Generación: node scripts/mod_fase2_generar.mjs · grafo:
scripts/mod_fase2_analizar.mjs (src/game/DEPS.json / DEPENDENCIAS.md).
Nota: `export ` en columna 0 dentro de core/ queda RESERVADO al generador.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src' / 'game'
GAME = RAIZ / 'public' / 'game.html'
GOLDEN = SRC / 'GOLDEN_SHA256.txt'

# ── fase 2: marcas del bloque de imports generado y prefijos export ──
MARK_INI = b'DEPS-FASE2-INICIO'
MARK_FIN = b'DEPS-FASE2-FIN'
RE_EXPORT = re.compile(rb'^export (?=(?:async function\b|function\b|class\b|const\b|let\b|var\b))')
RE_EXPORT_GUARDA = re.compile(rb'(?m)^export (?=(?:async function\b|function\b|class\b|const\b|let\b|var\b))')

def pieza_pura(datos: bytes) -> bytes:
    """Transformación inversa del generador: bloque DEPS fuera + export fuera."""
    lineas = datos.split(b'\n')
    fuera, saltando = [], False
    for l in lineas:
        if MARK_INI in l:
            saltando = True
            continue
        if MARK_FIN in l:
            saltando = False
            continue
        if not saltando:
            fuera.append(RE_EXPORT.sub(b'', l))
    return b'\n'.join(fuera)

# Orden EXACTO de piezas. (fichero, token requerido en su 1.ª línea)
ORDER = [
    ('00_head.html',        b'<!DOCTYPE html>'),
    ('01_vendor.html',      b'socket.io.min.js'),
    ('02_importmap.html',   b'importmap'),
    ('03_body.html',        None),                   # marcado de portada
    ('04_boot.html',        b'<script>'),
    ('05_module_open.html', b'type="module"'),
    # ── núcleo del juego (el <script type="module"> vive entre open/close) ──
    ('core/c00_pre_three.js',           b'/* ===='),
    ('core/c01_modelos_3d.js',          b"import * as THREE"),
    ('core/c02_cfg_escena.js',          b'const DIMS'),
    ('core/c03_audio_voz.js',           b'const VOICE_FULL'),
    ('core/c04_fisica_ccd.js',          b'const MAX_SUBSTEP_DT'),
    ('core/c05_colisiones_ia_golpeo.js', b'function collidePaddle('),
    ('core/c06_logros_stats_ia_rival.js', b'const ACHIEVEMENTS'),
    ('core/c07_escena_sala.js',         b'function createRoom'),
    ('core/c08_hall_hud.js',            b'const HALL = {'),
    ('core/c09_red_netlink.js',         b'class NetLink'),
    ('core/c10_menu_saque.js',          b'const MENU_LOGO_SRC'),
    ('core/c11_champloader.js',         b'class ChampLoader'),
    ('core/c12_pingponggame.js',        b'class PingPongGame'),
    ('core/c13_ui_arranque.js',         b'function renderPlayBtn'),
    ('06_module_close.html', b'</script>'),
    ('07_tail.html',        b'<script>'),
]

def main() -> None:
    escribir = '--escribir' in sys.argv

    # 1. existen TODAS las piezas y ninguna sobra en core/
    faltan = [n for n, _ in ORDER if not (SRC / n).exists()]
    if faltan:
        sys.exit('FALLO: piezas que faltan:\n  ' + '\n  '.join(faltan))
    en_orden = {n for n, _ in ORDER}
    sobran = [p.name for p in (SRC / 'core').glob('*.js') if f'core/{p.name}' not in en_orden]
    if sobran:
        sys.exit('FALLO: ficheros en core/ fuera del ORDER (añádelos a ORDER o bórralos):\n  '
                 + '\n  '.join(sobran))

    # 1b. guard de VERSIÓN ÚNICA: los sellos físicos casan con VERSION.json.
    #     La única fuente de verdad de la versión es src/game/VERSION.json y
    #     el único camino para cambiarla es scripts/bump_version.py.
    vjson = SRC / 'VERSION.json'
    if vjson.exists():
        try:
            vdat = json.loads(vjson.read_text(encoding='utf-8'))
            vver = vdat.get('version')
            if vver:
                c00txt = (SRC / 'core/c00_pre_three.js').read_text(encoding='utf-8')
                if c00txt.count(f"const VERSION = '{vver}'") != 1:
                    sys.exit(f'FALLO de versión única: c00_pre_three.js no lleva '
                             f"const VERSION = '{vver}' (VERSION.json). Camino legítimo: "
                             f'python3 scripts/bump_version.py <nueva-versión>')
                bodytxt = (SRC / '03_body.html').read_text(encoding='utf-8')
                if bodytxt.count(f'>V{vver}</span>') != 1:
                    sys.exit(f'FALLO de versión única: el badge #verBadge de 03_body.html '
                             f'no es V{vver}. Camino legítimo: python3 scripts/bump_version.py')
        except json.JSONDecodeError as e:
            sys.exit(f'FALLO: VERSION.json no es JSON válido: {e}')

    # 2. tokens de identidad
    fallos_tok = []
    for nombre, tok in ORDER:
        primera = (SRC / nombre).read_bytes().split(b'\n', 1)[0]
        if tok is not None and tok not in primera:
            fallos_tok.append(f'{nombre}: 1.ª línea sin {tok!r} → {primera[:70]!r}')
    if fallos_tok:
        sys.exit('FALLO de identidad de piezas:\n  ' + '\n  '.join(fallos_tok))

    # 3. ensamblar (fase 2: las piezas core/ pasan por la transformación inversa)
    datos = b''.join(
        pieza_pura((SRC / n).read_bytes()) if n.startswith('core/') else (SRC / n).read_bytes()
        for n, _ in ORDER
    )
    if MARK_INI in datos or MARK_FIN in datos:
        sys.exit('FALLO: restos de bloque DEPS-FASE2 en el ensamblado (marcas desequilibradas)')
    if RE_EXPORT_GUARDA.search(datos):
        sys.exit('FALLO: restos de prefijo export en columna 0 dentro del ensamblado')
    sha = hashlib.sha256(datos).hexdigest()
    print(f'· ensamblado: {len(datos):,} B · sha256 {sha[:16]}…')

    dorado = GOLDEN.read_text(encoding='utf-8').strip().splitlines()
    dorado_sha = next(l.strip() for l in dorado if l and not l.startswith('#'))
    if sha == dorado_sha:
        print('✓ BYTE-EXACTO contra el golden (GOLDEN_SHA256.txt)')
    else:
        print(f'! DIFIERE del golden {dorado_sha[:16]}… (cambio legítimo si editaste src/)')

    actual = GAME.read_bytes()
    if datos == actual:
        print('✓ public/game.html ya está sincronizado con src/')
        return
    if not escribir:
        print(f'! public/game.html DIFIERE de lo ensamblado ({len(actual):,} B en disco).')
        print('  Ensayo sin escribir. Para aplicar: python3 scripts/build_game.py --escribir')
        sys.exit(1)
    GAME.write_bytes(datos)
    print(f'✓ public/game.html REGENERADO ({len(datos):,} B)')

if __name__ == '__main__':
    main()
