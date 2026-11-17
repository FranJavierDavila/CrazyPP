"""Fase C · Regenera championships/championships.json desde las carpetas.

Regla (AUDITORIA.md §4.5): el índice NO se edita a mano. Este script:
  · escanea public/championships/*/manifest.json
  · valida cada id contra ^[a-z0-9_-]{2,24}$ y valida_manifiesto
  · conserva el orden de los campeonatos conocidos y añade los nuevos al final
  · refleja eager (del índice previo) y estado (del manifest)
  · conserva el campo «note» histórico y estampa «generado»
Uso: python3 scripts/plataforma/genera_indice.py [--secar]  (--secar: solo mostrar)
"""
import json
import re
import sys
import time
from pathlib import Path

RAIZ = Path('/home/z/my-project/public/championships')
IDX = RAIZ / 'championships.json'


def main(secar=False):
    previo = {}
    if IDX.is_file():
        try:
            previo = json.loads(IDX.read_text(encoding='utf-8'))
        except Exception:
            previo = {}
    prev_ords = [e if isinstance(e, str) else (e.get('id') or '')
                 for e in (previo.get('championships') or [])]
    prev_eager = {e.get('id') for e in previo.get('championships', [])
                  if isinstance(e, dict) and e.get('eager')}

    carpetas = sorted(p for p in RAIZ.iterdir() if p.is_dir())
    encontrados = []
    for carp in carpetas:
        mf = carp / 'manifest.json'
        if not mf.is_file():
            continue
        try:
            m = json.loads(mf.read_text(encoding='utf-8'))
        except Exception as e:
            print(f'  ✗ {carp.name}: manifest ilegible ({e}) — NO se integra')
            continue
        cid = m.get('id') or carp.name
        if not re.fullmatch(r'[a-z0-9_-]{2,24}', cid):
            print(f'  ✗ {carp.name}: id «{cid}» inválido — NO se integra')
            continue
        encontrados.append({'id': cid, 'estado': m.get('estado') or 'publicado'})

    # orden: conocidos primero (orden previo), nuevos al final
    conocidos = [e for e in prev_ords if any(x['id'] == e for x in encontrados)]
    nuevos = [x['id'] for x in encontrados if x['id'] not in conocidos]
    orden = conocidos + nuevos
    por_id = {x['id']: x for x in encontrados}

    lista = []
    for cid in orden:
        x = por_id[cid]
        ent = {'id': cid}
        if cid in prev_eager:
            ent['eager'] = True
        if x['estado'] != 'publicado':
            ent['estado'] = x['estado']
        lista.append(ent if len(ent) > 1 else cid)

    doc = {
        'version': previo.get('version', 16) + 1,
        'generado': time.strftime('%Y-%m-%d %H:%M') + ' · genera_indice.py',
        'note': previo.get('note', ''),
        'championships': lista,
    }
    if secar:
        print(json.dumps(doc, ensure_ascii=False, indent=1)[:800])
        return
    IDX.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + '\n',
                   encoding='utf-8')
    print(f'✓ índice regenerado: {[e if isinstance(e, str) else e["id"] for e in lista]}')


if __name__ == '__main__':
    main(secar='--secar' in sys.argv)
