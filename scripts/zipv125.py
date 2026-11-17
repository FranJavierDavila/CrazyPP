"""Empaqueta la V2.125 oficial: crazypp-v2125.zip (index.html + assets + championships).

Réplica exacta de la estructura del zip oficial: index.html (game.html),
assets/intro.mp4 y championships/ (con championships.schema.json incluido,
el nuevo contrato). Excluye descargas/ (espejo web) y cachés.
"""
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

RAIZ = Path('/home/z/my-project')
PUB = RAIZ / 'public'
OUT = RAIZ / 'download' / 'crazypp-v2125.zip'


def sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def main():
    if OUT.exists():
        OUT.unlink()
    n = 0
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        z.write(PUB / 'game.html', 'index.html')
        n += 1
        intro = PUB / 'assets' / 'intro.mp4'
        if intro.is_file():
            z.write(intro, 'assets/intro.mp4')
            n += 1
        for p in sorted((PUB / 'championships').rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                z.write(p, str(p.relative_to(PUB)))
                n += 1
    # verificación
    r = subprocess.run(['unzip', '-t', str(OUT)], capture_output=True, text=True)
    ok = 'No errors detected' in r.stdout
    print(f'zip: {OUT.name} · {n} ficheros · {OUT.stat().st_size:,} B')
    print(f'sha256: {sha256(OUT)}')
    print(f'unzip -t: {"OK" if ok else "ERROR"}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
