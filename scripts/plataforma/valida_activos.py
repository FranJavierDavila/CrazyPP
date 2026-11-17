"""Fase B · Valida los ACTIVOS gráficos de un campeonato.

Criterios (afinados con el bug real del rodante.png v2.125):
  · ERROR: referencias del manifest a ficheros inexistentes.
  · SOSPECHA: PNG con ALGUNA ESQUINA opaca (alfa ≥ 200) — es el patrón del
    fondo mal recortado (rodante traía esquinas 6/255/54/109). Los toques en
    el CENTRO del borde son legítimos (bandas/parallax a sangre).
Uso: python3 scripts/plataforma/valida_activos.py championships/<id>
Exit 0 = sin errores (las sospechas son informativas).
"""
import json
import sys
from pathlib import Path

from PIL import Image

RAIZ = Path('/home/z/my-project/public')


def esquinas_opacas(p: Path):
    try:
        im = Image.open(p)
    except Exception:
        return False
    if im.mode != 'RGBA':
        return False
    w, h = im.size
    px = im.load()
    return any(px[x, y][3] >= 200
               for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)))


def main(carpeta_rel):
    carpeta = RAIZ / carpeta_rel
    if not carpeta.is_dir():
        print('✗ No existe', carpeta)
        sys.exit(1)
    print(f'— activos de {carpeta_rel}')
    rotas = 0

    # referencias del manifest (ERROR real)
    mf = carpeta / 'manifest.json'
    if mf.is_file():
        m = json.loads(mf.read_text(encoding='utf-8'))
        refs = []

        def recojer(o):
            if isinstance(o, str) and o.startswith('assets/'):
                refs.append(o)
            elif isinstance(o, dict):
                for v in o.values():
                    recojer(v)
            elif isinstance(o, list):
                for v in o:
                    recojer(v)

        recojer({k: m.get(k) for k in ('decor', 'room', 'audio', 'powers', 'stages')})
        for r in refs:
            if not (carpeta / r).is_file():
                rotas += 1
                print(f'  ERROR falta {carpeta_rel}/{r}')

    # alfa de esquinas (sospecha informativa)
    sospechas = []
    for p in sorted(carpeta.rglob('*.png')):
        if esquinas_opacas(p):
            sospechas.append(p.relative_to(RAIZ))
    for s in sospechas:
        print(f'  revisar alfa (esquina opaca): {s}')

    if rotas:
        print(f'✗ {rotas} referencias rotas')
        sys.exit(1)
    print(f'  ✓ sin errores · {len(sospechas)} PNG por revisar (informativo)')
    sys.exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1])
