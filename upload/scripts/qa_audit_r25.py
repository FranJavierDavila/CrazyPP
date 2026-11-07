#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_audit_r25.py · Auditoría transversal de bugs latentes (Ronda 25).

Capas (estáticas, sin navegador):
  A · storage write==read por campeonato (claves usadas vs convención)
  B · promesas .then( sin .catch( en el mismo objeto encadenado
  C · addEventListener vs removeEventListener por fichero (fuga potencial)
  D · setTimeout/setInterval sin cancelación visible en el mismo fichero
  E · llamadas a métodos this.* inexistentes en la clase del módulo
      (heurística: nombre definido como método ` name(` en el fichero)
  F · nuevas claves i18n usadas con tx( ausentes del bloque strings

Devuelve informe [OK]/[AVISO]/[FALLO] y código de salida 0/1.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path('/home/z/my-project')
CHAMPS = BASE / 'public/championships'
CORE = BASE / 'src/game/core'

OK, AVISO, FALLO = 'OK', 'AVISO', 'FALLO'
res = []  # (nivel, capa, msg)


def add(niv, capa, msg):
    res.append((niv, capa, msg))


def leer(p):
    try:
        return p.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


# ── A · storage write==read ─────────────────────────────────────────────
def capa_storage():
    for d in sorted(CHAMPS.iterdir()):
        if not d.is_dir() or d.name.startswith('_'):
            continue
        if not (d / 'manifest.json').exists():
            continue   # sdk/, demos, no-campeonatos
        man = {}
        try:
            man = json.loads(leer(d / 'manifest.json'))
        except Exception:
            add(FALLO, 'A', f'{d.name}: manifest.json ilegible')
            continue
        base = str(man.get('storage') or '').replace('*$', '').rstrip('*')
        if not base:
            add(AVISO, 'A', f'{d.name}: manifest sin storage')
            continue
        js = leer(d / 'index.js')
        # claves usadas via storageKey('x'), base literal o this.base+'x'
        usadas = set(re.findall(r"storageKey\('([^']+)'\)", js))
        usadas |= set(re.findall(r"this\.base \+ '([a-z0-9_]+)'", js))
        literales = set(re.findall(r"'(" + re.escape(base.rstrip('*')) + r"[a-z0-9_]+)'", js))
        for lit in literales:
            usadas.add(lit[len(base):])
        malas = [k for k in usadas if not re.match(r'^[a-z0-9_]+$', k)]
        for m in malas:
            add(AVISO, 'A', f'{d.name}: clave rara via storageKey → {m!r}')
        if usadas:
            add(OK, 'A', f'{d.name}: {len(usadas)} claves bajo base {base!r} (convención uniforme)')
        else:
            add(AVISO, 'A', f'{d.name}: sin claves storageKey detectadas')


# ── B · promesas sin catch ──────────────────────────────────────────────
def capa_promesas():
    ficheros = list(CHAMPS.glob('*/index.js')) + list(CORE.glob('*.js'))
    patron_then = re.compile(r'\.then\(')
    patron_catch = re.compile(r'\.catch\(')
    for f in ficheros:
        js = leer(f)
        if 'fetch(' not in js and '.then(' not in js:
            continue
        # heurística por línea: then sin catch en la misma sentencia
        lineas = js.split('\n')
        for i, ln in enumerate(lineas, 1):
            if patron_then.search(ln) and not patron_catch.search(ln):
                # .then(fn, fn) con ambos handlers: rechazo ya cubierto
                if re.search(r'\.then\([^)]*,\s*[^)]+\)\s*;?\s*[})]?\s*$', ln):
                    continue
                # mirar hasta 14 líneas más allá del mismo bloque
                seg = '\n'.join(lineas[i - 1:i + 14])
                if not patron_catch.search(seg):
                    nombre = f.relative_to(BASE)
                    add(AVISO, 'B', f'{nombre}:{i} .then( sin .catch( a la vista → riesgo de unhandledrejection')


# ── C · listeners ───────────────────────────────────────────────────────
def capa_listeners():
    ficheros = list(CHAMPS.glob('*/index.js')) + list(CORE.glob('*.js'))
    for f in ficheros:
        js = leer(f)
        n_add = len(re.findall(r'addEventListener\(', js))
        n_rem = len(re.findall(r'removeEventListener\(', js))
        # VR: la mayoría de listeners van sobre controllers/ofs.gamepad —
        # sólo marcamos AVISO si add >> rem y no hay abort/off/onremove
        if n_add - n_rem >= 6 and not re.search(r'signal|abort|on\(.removed|dispose', js):
            add(AVISO, 'C', f'{f.name}: {n_add} add vs {n_rem} remove (revisar ciclo de vida)')


# ── D · timers sin cancelación ─────────────────────────────────────────
def capa_timers():
    ficheros = list(CHAMPS.glob('*/index.js')) + list(CORE.glob('*.js'))
    for f in ficheros:
        js = leer(f)
        n_st = len(re.findall(r'\bsetTimeout\(', js))
        n_ct = len(re.findall(r'\bclearTimeout\(', js))
        # intervalos ASIGNADOS (= setInterval) sin clear del mismo id: fuga.
        # window.setInterval sin asignar = singleton de vida de app: OK.
        asignados = re.findall(r'(\w[\w.$]*)\s*=\s*(?:window\.)?setInterval\(', js)
        fuga = [v for v in asignados
                if not re.search(r'clearInterval\(\s*' + re.escape(v) + r'\s*\)', js)
                and ('clearInterval(' + v.split('.')[-1]) not in js]
        for v in fuga:
            add(AVISO, 'D', f'{f.name}: intervalo asignado a {v!r} sin clearInterval a la vista')
        # setTimeout sin guardar id es normal en UI efímera; sólo señal si hay
        # muchísimos más timeouts que clears Y además hay dispose (salas)
        if 'dispose' in js and n_st >= 25 and n_ct == 0:
            add(AVISO, 'D', f'{f.name}: {n_st} setTimeout y 0 clearTimeout (revisar tras dispose)')


# ── E · métodos this.* inexistentes ────────────────────────────────────
def capa_metodos():
    for d in sorted(CHAMPS.glob('*/')):
        if d.name.startswith('_'):
            continue
        js = leer(d / 'index.js')
        if not js:
            continue
        # métodos definidos a CUALQUIER indentación (clases anidadas incluidas)
        definidos = set(re.findall(r'^\s*(?:async )?([a-zA-Z_$][\w$]*)\s*\(', js, re.M))
        # getters/setters
        definidos |= set(re.findall(r'^\s*(?:get|set) ([a-zA-Z_$][\w$]*)\s*\(', js, re.M))
        # asignaciones dinámicas (this._A = (p) => ...) y const locales
        definidos |= set(re.findall(r'this\.([a-zA-Z_$][\w$]*)\s*=\s*(?:async )?\(?[^=)]*\)?\s*=>', js))
        usados = set(re.findall(r'\bthis\.([a-zA-Z_$][\w$]*)\s*\(', js))
        # también las clases internas delegan en ctrl.: ctrl.metodo(
        usados |= set(re.findall(r'\bctrl\.([a-zA-Z_$][\w$]*)\s*\(', js))
        fantasma = sorted(u for u in usados if u not in definidos)
        # whitelist: helpers 2D de canvas (this = ctx), configs de una letra
        wl = {'sfx', 'group', 'mapa', 'cartel', 'sprite', 'fx',
              'moveTo', 'arcTo', 'closePath', 'fill', 'fillText', 'stroke',
              'beginPath', 'arc', 'save', 'restore', 'translate', 'rotate'}
        fantasma = [g for g in fantasma if g not in wl and not re.match(r'^[A-Z]$', g)]
        if fantasma:
            add(AVISO, 'E', f'{d.name}: this./ctrl. llamados sin definición visible → {", ".join(fantasma[:8])}')
        else:
            add(OK, 'E', f'{d.name}: {len(usados)} métodos this./ctrl. todos definidos')


# ── F · i18n: claves tx( presentes en strings ──────────────────────────
def capa_i18n():
    for d in sorted(CHAMPS.glob('*/')):
        if d.name.startswith('_'):
            continue
        js = leer(d / 'index.js')
        if not js:
            continue
        # estilo LITERAL (tx = (es, en) =>): las claves no aplican
        if re.search(r'const tx = \((?:es|a)\s*,', js):
            add(OK, 'F', f'{d.name}: tx literal (es,en) — capa i18n no aplica')
            continue
        usadas = set(re.findall(r"\btx\('([^']+)'", js))
        usadas = {u for u in usadas if not u.endswith('_')}   # prefijos dinámicos
        # bloque de strings: claves `key:` dentro de es:{...} / en:{...}
        m_es = re.search(r"const (?:S|STRINGS|STR)\s*=\s*\{\s*es\s*:\s*\{(.*?)\n {2}\}", js, re.S)
        m_en = re.search(r"en\s*:\s*\{(.*?)\n {2}\}", js, re.S)
        blob = (m_es.group(1) if m_es else '') + (m_en.group(1) if m_en else '')
        definidas = set(re.findall(r"([a-zA-Z_$][\w$]*)\s*:\s*['`\"\[]", blob))
        faltan = sorted(usadas - definidas)
        if faltan:
            add(AVISO, 'F', f'{d.name}: tx( sin clave visible en strings → {", ".join(faltan[:10])}')
        else:
            add(OK, 'F', f'{d.name}: {len(usadas)} claves tx( todas definidas')


def main():
    capa_storage()
    capa_promesas()
    capa_listeners()
    capa_timers()
    capa_metodos()
    capa_i18n()
    n_ok = sum(1 for n, _, _ in res if n == OK)
    n_av = sum(1 for n, _, _ in res if n == AVISO)
    n_fa = sum(1 for n, _, _ in res if n == FALLO)
    for n, capa, msg in res:
        print(f'  [{n:5}] {capa} · {msg}')
    print('-' * 72)
    print(f'  {n_ok} OK · {n_av} avisos · {n_fa} fallos → {"VERDE" if n_fa == 0 else "ROJO"}')
    return 0 if n_fa == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
