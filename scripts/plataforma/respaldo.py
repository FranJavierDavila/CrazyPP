"""Fase A · Snapshot verificado del proyecto (protección del desarrollo).

Crea respaldos/crazypp-<fecha>-<etiqueta>.zip con:
  public/  (juego + campeonatos)  ·  src/  ·  scripts/plataforma  ·
  worklog.md  ·  next.config.ts · package.json
y dentro: SHA256SUMS.txt (hash de cada fichero) + RESPALDO.json (motivo, fecha,
versión del núcleo). Verificación: unzip -t + SHA256 al restaurar.

Uso:  python3 scripts/plataforma/respaldo.py "motivo" [--etiqueta v2125]
"""
import hashlib
import json
import subprocess
import sys
import time
import zipfile
from pathlib import Path

RAIZ = Path('/home/z/my-project')
DEST = RAIZ / 'respaldos'
INCLUIR = ['public', 'src', 'scripts/plataforma']
SUELTOS = ['worklog.md', 'next.config.ts', 'package.json']
EXCLUIR_DIR = {'node_modules', '.next', '__pycache__', '.git'}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 20), b''):
            h.update(bloque)
    return h.hexdigest()


def version_nucleo() -> str:
    try:
        s = (RAIZ / 'public/game.html').read_text(encoding='utf-8')
        for linea in s.splitlines():
            if "const VERSION =" in linea:
                return linea.split("'")[1]
    except Exception:
        pass
    return '?'


def main():
    motivo = ' '.join(sys.argv[1:2]) or 'sin motivo'
    etiqueta = 'snap'
    if '--etiqueta' in sys.argv:
        etiqueta = sys.argv[sys.argv.index('--etiqueta') + 1]
    DEST.mkdir(exist_ok=True)
    tstamp = time.strftime('%Y%m%d-%H%M')
    zip_path = DEST / f'crazypp-{tstamp}-{etiqueta}.zip'

    ficheros = []
    for rel in INCLUIR:
        base = RAIZ / rel
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if p.is_file() and not (set(p.parts) & EXCLUIR_DIR):
                ficheros.append(p)
    for rel in SUELTOS:
        p = RAIZ / rel
        if p.is_file():
            ficheros.append(p)

    manifest_interno = []
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(set(ficheros)):
            arc = str(p.relative_to(RAIZ))
            z.write(p, arc)
            manifest_interno.append((arc, sha256(p)))
        hashes = '\n'.join(f'{h}  {a}' for a, h in manifest_interno)
        z.writestr('SHA256SUMS.txt', hashes + '\n')
        meta = {
            'motivo': motivo,
            'fecha': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version_nucleo': version_nucleo(),
            'ficheros': len(manifest_interno),
            'sha256_zip_interno': None,
        }
        z.writestr('RESPALDO.json', json.dumps(meta, ensure_ascii=False, indent=1))

    hash_zip = sha256(zip_path)
    meta_ext = {
        'zip': zip_path.name,
        'sha256': hash_zip,
        'bytes': zip_path.stat().st_size,
        'motivo': motivo,
        'version_nucleo': version_nucleo(),
        'ficheros': len(manifest_interno),
    }
    (DEST / (zip_path.stem + '.json')).write_text(
        json.dumps(meta_ext, ensure_ascii=False, indent=1), encoding='utf-8')

    # verificación de integridad
    mal = subprocess.run(['unzip', '-t', str(zip_path)],
                         capture_output=True, text=True)
    ok = 'No errors detected' in mal.stdout
    print(f'respaldo: {zip_path.name}')
    print(f'  ficheros: {len(manifest_interno)} · {zip_path.stat().st_size:,} B')
    print(f'  sha256:   {hash_zip}')
    print(f'  unzip -t: {"OK" if ok else "ERROR"}')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
