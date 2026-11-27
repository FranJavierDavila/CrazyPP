#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G3-G4 (auditoría r120 · ola 3 · r129) · PODA del andamio muerto.

Borra (el histórico git lo conserva):
  · andamio del template: src/app/page.tsx, src/components/ping-pong-canvas.tsx,
    src/lib/game/ (7 ficheros · 1.818 líneas de segunda física/reglas/IA) —
    inalcanzables: next.config.ts reescribe / a /game.html con beforeFiles.
  · 46 de 48 componentes shadcn ui (sólo viven toast.tsx y toaster.tsx,
    usados por layout.tsx → use-toast → lib/utils).
  · 4 copias .pre_r83 de src/game/core (G1-G2, fuera del ORDER del build).
  · package-lock.json (el toolchain es bun de principio a fin; queda bun.lock).
  · .env y db/custom.db dejan de estar trackeados (G1-G2; siguen en disco).

package.json: nombre «crazypp», 57 de 67 dependencias de producción fuera
(quedan next/react/react-dom/@radix-ui/react-toast/cva/clsx/lucide-react/
tailwind-merge + prisma/@prisma/client que exige el hook db:push de la
plataforma), three → devDependencies (los arneses QA lo importan),
acorn → devDependencies (mod_fase2_analizar.mjs lo usaba sin declarar).
"""
import json
import shutil
import subprocess
from pathlib import Path

RAIZ = Path('/home/z/my-project')

# 1 · borrados de ficheros
for f in [RAIZ / 'src/app/page.tsx',
          RAIZ / 'src/components/ping-pong-canvas.tsx',
          RAIZ / 'package-lock.json']:
    f.unlink(missing_ok=True)
    print('borrado:', f.relative_to(RAIZ))
shutil.rmtree(RAIZ / 'src/lib/game', ignore_errors=True)
print('borrado: src/lib/game/ (completo)')
ui = RAIZ / 'src/components/ui'
quedan = {'toast.tsx', 'toaster.tsx'}
for f in sorted(ui.iterdir()):
    if f.name not in quedan:
        f.unlink()
print(f'ui/: quedan {len(list(ui.iterdir()))} de 48 (toast + toaster)')
for f in (RAIZ / 'src/game/core').glob('*.pre_r83'):
    f.unlink()
    print('borrado:', f.relative_to(RAIZ))

# 2 · .env y db/custom.db fuera del índice (siguen en disco)
for rel in ('.env', 'db/custom.db'):
    subprocess.run(['git', 'rm', '--cached', '--quiet', rel], cwd=RAIZ, check=False)
gi = RAIZ / '.gitignore'
txt = gi.read_text(encoding='utf-8')
if 'db/custom.db' not in txt:
    gi.write_text(txt.rstrip('\n') + '\n\n# G1-G2 (r129): binario SQLite regenerable con db:push\ndb/custom.db\n',
                  encoding='utf-8')
    print('.gitignore: db/custom.db añadido')

# 3 · package.json
pj = RAIZ / 'package.json'
datos = json.loads(pj.read_text(encoding='utf-8'))
datos['name'] = 'crazypp'
KEEP = {'next', 'react', 'react-dom', '@radix-ui/react-toast', 'class-variance-authority',
        'clsx', 'lucide-react', 'tailwind-merge', 'prisma', '@prisma/client'}
borradas = sorted(set(datos['dependencies']) - KEEP)
three_v = datos['dependencies'].pop('three')
datos['dependencies'] = {k: v for k, v in datos['dependencies'].items() if k in KEEP}
datos['devDependencies']['three'] = three_v
datos['devDependencies']['acorn'] = '^8.14.1'
pj.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f"package.json: nombre={datos['name']} · deps {67 - 1 - len(borradas) + 1}→{len(datos['dependencies'])} "
      f"({len(borradas)} fuera: {', '.join(borradas[:8])}…) · three→dev · +acorn")
