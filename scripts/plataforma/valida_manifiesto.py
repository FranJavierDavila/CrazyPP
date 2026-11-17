"""Fase B/E · Valida un manifest.json de campeonato contra el contrato v2.125.

Uso: python3 scripts/plataforma/valida_manifiesto.py championships/<id>/manifest.json
Salida: lista de ERRORES (bloquean publicar) y AVISOS (no bloquean).
Exit 0 = válido.
"""
import json
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project/public')
ERRORES = []
AVISOS = []


def err(m):
    ERRORES.append(m)


def aviso(m):
    AVISOS.append(m)


def main(ruta):
    ruta = Path(ruta)
    if not ruta.is_file():
        print('✗ No existe', ruta)
        sys.exit(1)
    carpeta = ruta.parent
    try:
        m = json.loads(ruta.read_text(encoding='utf-8'))
    except Exception as e:
        print('✗ JSON inválido:', e)
        sys.exit(1)

    # obligatorios
    for k in ('id', 'version', 'title', 'rival', 'storage', 'assets'):
        if k not in m:
            err(f'falta campo obligatorio «{k}»')
    if 'description' not in m:
        aviso('sin «description» — el catálogo y la IA la usan; añádela')
    if 'contract' not in m:
        aviso('sin «contract» — se asume 1 (contrato actual)')
    else:
        if m['contract'] != 1:
            err(f'contract={m["contract"]}: este núcleo solo soporta 1')

    # id == carpeta
    if m.get('id') and m['id'] != carpeta.name:
        err(f'id «{m["id"]}» ≠ carpeta «{carpeta.name}»')
    if m.get('id') and not re.fullmatch(r'[a-z0-9_-]{2,24}', m['id']):
        err(f'id «{m.get("id")}» no cumple ^[a-z0-9_-]{{2,24}}$')

    # título
    t = m.get('title') or {}
    if not t.get('es'):
        err('title.es vacío')

    # storage
    st = m.get('storage', '')
    if m.get('id') and not st.startswith('pp_champ_' + m['id']) \
            and not st.startswith('pp_arcade'):
        aviso(f'storage «{st}» fuera de la convención pp_champ_{m.get("id")}_*')

    # rival
    r = m.get('rival') or {}
    for k in ('id', 'name', 'kind'):
        if k not in r:
            err(f'rival sin «{k}»')
    estados = r.get('states') or []
    assets_dir = carpeta / 'assets'
    for stn in estados:
        if not (assets_dir / f'{stn}.webp').is_file():
            err(f'estado del rival «{stn}» sin assets/{stn}.webp')

    # referencias de decor/room/audio/powers → deben existir
    def ref(clave, val):
        if isinstance(val, str) and val.startswith('assets/'):
            if not (carpeta / val).is_file():
                err(f'{clave}: falta el fichero {val}')

    for pza in ((m.get('decor') or {}).get('pieces') or []):
        ref('decor.piece', pza.get('file'))
    for clave in ('floor', 'ceil', 'back', 'front', 'left', 'right'):
        ref('room.' + clave, (m.get('room') or {}).get(clave))
    au = m.get('audio') or {}
    ref('audio.music', au.get('music'))
    for nombre, v in (au.get('sounds') or {}).items():
        ref(f'audio.sounds.{nombre}', v)
    for p in (m.get('powers') or []):
        ref('power.icon', p.get('icon'))
        if p.get('kind') == 'custom' and not p.get('module'):
            err(f'power «{p.get("name")}» custom sin module')
    for e in (m.get('stages') or []):
        if e.get('kind') == 'custom' and not e.get('module'):
            err(f'etapa «{e.get("id")}» custom sin module')

    # powers duplicados
    kinds = [p.get('kind') for p in (m.get('powers') or [])]
    if len(kinds) != len(set(kinds)):
        aviso('powers con kind repetido')

    # estado del ciclo de vida
    if m.get('estado') and m['estado'] not in (
            'borrador', 'validacion', 'listo', 'publicado', 'desactivado'):
        err(f'estado «{m["estado"]}» no válido')

    # informe
    print(f'— {ruta} (v{m.get("version", "?")} · estado {m.get("estado", "publicado*")})')
    for e in ERRORES:
        print('  ERROR:', e)
    for a in AVISOS:
        print('  aviso:', a)
    if ERRORES:
        print(f'✗ {len(ERRORES)} errores')
        sys.exit(1)
    print('✓ manifiesto válido' + (f' ({len(AVISOS)} avisos)' if AVISOS else ''))
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
