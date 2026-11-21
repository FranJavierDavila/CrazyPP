#!/usr/bin/env python3
"""check_live_service_igualdad.py — N1 de la auditoría r111.

El relay de CRAZY TV existía en 4 copias idénticas (mini-services/ +
staging-v36207 + staging-v36209 + release-v36209). Decisión r112:
UNA fuente de verdad — mini-services/live-service/index.ts — y este
check en la batería:

  · FALLA (RC 1) si la fuente de verdad falta o no compila.
  · AVISA (informativo) cuando una copia CONGELADA de una release
    anterior diverge de la fuente de verdad — es lo esperado tras el
    fix r112 (las snapshots de release NO se retocan: documentan su era).
  · El riesgo real de deriva futuro lo cubre el empaquetado: si algún
    día se vuelve a desplegar el relay, debe COPIARSE desde
    mini-services/ (nunca editarse la copia).

Uso: python3 scripts/check_live_service_igualdad.py
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
CANON = RAIZ / 'mini-services/live-service/index.ts'
CONGELADAS = [
    RAIZ / 'scripts/staging-v36207/live-service/server.mjs',
    RAIZ / 'scripts/staging-v36209/live-service/server.mjs',
    RAIZ / 'scripts/release-v36209/server.mjs',
]


def main() -> int:
    if not CANON.exists():
        print(f'✗ FUENTE DE VERDAD AUSENTE: {CANON}')
        return 1
    # node --check no acepta .ts: compila a un .mjs temporal (TS es un
    # superconjunto sintáctico suficiente para el parser de Node en este
    # fichero: tipos solo en la firma de txt() — se despojan con sed simple)
    tmp = Path('/tmp/live_service_check.mjs')
    src = CANON.read_text(encoding='utf-8')
    # despojo mínimo del tipado inline (v: unknown, max: number, def: string)
    import re
    src = re.sub(r'\(v: unknown, max: number, def: string\)', '(v, max, def)', src)
    tmp.write_text(src, encoding='utf-8')
    r = subprocess.run(['node', '--check', str(tmp)], capture_output=True, text=True)
    if r.returncode != 0:
        print('✗ LA FUENTE DE VERDAD NO COMPILA:')
        print(r.stderr[:800])
        return 1
    print(f'✓ fuente de verdad OK: {CANON.relative_to(RAIZ)}')

    canon_bytes = CANON.read_bytes()
    # r112: las copias de despliegue son server.mjs — el canónico es index.ts:
    # se compara tras aplicar la MISMA conversión ts→mjs (despojo de tipos)
    # que usa el kit (actualiza_kit_relay_r112.py). Comparar bytes crudos del
    # .ts contra un .mjs siempre diría «diverge» aunque el código sea el mismo
    # y taparía las derivas reales.
    canon_mjs = re.sub(r'\(v: unknown, max: number, def: string\)',
                       '(v, max, def)', canon_bytes.decode('utf-8')).encode('utf-8')
    for copia in CONGELADAS:
        if not copia.exists():
            print(f'  · copia congelada ausente (ok): {copia.relative_to(RAIZ)}')
            continue
        if copia.read_bytes() == canon_mjs:
            print(f'  · idéntica a la fuente (tras ts→mjs): {copia.relative_to(RAIZ)}')
        else:
            print(f'  · DIVERGE (esperado: snapshot congelada de su release): '
                  f'{copia.relative_to(RAIZ)}')
    print('  → regla r112: si se re-despliega el relay, COPIAR desde mini-services/ (nunca editar la copia)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
