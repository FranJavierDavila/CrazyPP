"""Fase A · Restauración de un snapshot verificado.

Verifica el SHA256 del zip y el SHA256SUMS interno, vuelca public/ sobre el
proyecto y deja src/scripts en <zip>.restaurado/ para revisión manual.

Uso: python3 scripts/plataforma/restaurar.py respaldos/crazypp-....zip [--si]
El flag --si evita la confirmación (para automatización).
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

RAIZ = Path('/home/z/my-project')


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 20), b''):
            h.update(bloque)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    zip_path = Path(sys.argv[1])
    auto = '--si' in sys.argv
    if not zip_path.is_file():
        print('No existe:', zip_path)
        sys.exit(1)

    meta_path = zip_path.with_suffix('.json')
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        real = sha256(zip_path)
        if real != meta.get('sha256'):
            print(f'✗ SHA256 del zip NO coincide ({real} ≠ {meta.get("sha256")})')
            sys.exit(1)
        print(f'✓ SHA256 del zip verificado ({real[:16]}…)')

    if not auto:
        r = input(f'¿Restaurar {zip_path.name} sobre public/? [escribir SI] ')
        if r.strip() != 'SI':
            print('Cancelado.')
            sys.exit(1)

    tmp = Path(tempfile.mkdtemp(prefix='restaurar-'))
    subprocess.run(['unzip', '-q', str(zip_path), '-d', str(tmp)], check=True)

    sums = tmp / 'SHA256SUMS.txt'
    if sums.is_file():
        malos = []
        for linea in sums.read_text(encoding='utf-8').splitlines():
            if not linea.strip():
                continue
            h, arc = linea.split('  ', 1)
            f = tmp / arc
            if not f.is_file() or sha256(f) != h:
                malos.append(arc)
        if malos:
            print('✗ Ficheros corruptos dentro del zip:', malos[:5])
            sys.exit(1)
        print(f'✓ {len(sums.read_text(encoding="utf-8").splitlines())} ficheros internos verificados')

    # public/ vuelve tal cual
    pub = tmp / 'public'
    if pub.is_dir():
        destino = RAIZ / 'public'
        respaldo_antes = RAIZ / 'respaldos' / ('public-antes-' + zip_path.stem)
        if destino.is_dir():
            respaldo_antes.parent.mkdir(exist_ok=True)
            shutil.move(str(destino), str(respaldo_antes))
            print('· public/ anterior guardado en', respaldo_antes.name)
        shutil.copytree(pub, destino)
        print('✓ public/ restaurado')

    # src y scripts/plataforma a carpeta de revisión
    para_revision = RAIZ / (zip_path.stem + '.restaurado')
    para_revision.mkdir(exist_ok=True)
    for rel in ('src', 'scripts/plataforma'):
        origen = tmp / rel
        if origen.exists():
            dst = para_revision / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(origen, dst, dirs_exist_ok=True)
    print('✓ src/scripts en', para_revision.name, '(revisión manual)')
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    main()
