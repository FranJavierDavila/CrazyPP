#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CRAZY PING PONG · ronda 20 · INFORME DE DECISIÓN desde la telemetría D1
=======================================================================
Convierte los volcados del worker (_eventos_*.json / _resumen_*.json) en un
briefing humano y accionable: sesiones con duración real, curva de fps,
embudo champ_rank por campeonato y prueba, avance de etapas, errores y
adopción de versiones. Herramienta LOCAL de análisis — no toca el juego.

Uso:
  python3 scripts/informe.py [eventos.json] [resumen.json]
  (por defecto: los últimos _eventos_r*.json / _resumen_r*.json)

Salida: texto a stdout (y guarda scripts/informe_ultimo.txt).
"""
import glob
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

RAIZ = '/home/z/my-project'
SCR = os.path.join(RAIZ, 'scripts')

CAMPS = ('locura', 'magia', 'oeste', 'estacion_orbital', 'valle_neon')
# semántica del stage por campeonato (auditoría ronda 19): oeste 1..5, resto 0..4
STAGE_1INDEXED = {'oeste'}
TOTAL_ETAPAS = {'locura': 5, 'magia': 5, 'oeste': 5, 'estacion_orbital': 5, 'valle_neon': 5}


def _lista(ev_path, res_path):
    if len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    evs = sorted(glob.glob(os.path.join(SCR, '_eventos_r*.json')))
    res = sorted(glob.glob(os.path.join(SCR, '_resumen_r*.json')))
    return (evs[-1] if evs else None), (res[-1] if res else None)


def _fmt_dur(ms):
    if not ms or ms <= 0:
        return '—'
    s = int(ms // 1000)
    h, resto = divmod(s, 3600)
    m, sec = divmod(resto, 60)
    return f'{h}h{m:02d}m' if h else (f'{m}m{sec:02d}s' if m else f'{sec}s')


def _stage_humano(champ, n):
    """n tal como lo emite el módulo → etapa humana (1..5)."""
    if n is None:
        return None
    try:
        n = int(n)
    except (TypeError, ValueError):
        return None
    return n if champ in STAGE_1INDEXED else n + 1


def main():
    ev_path, res_path = _lista(None, None)
    if not ev_path:
        sys.exit('FALLO: no hay volcados _eventos_r*.json en scripts/')
    evs = json.load(open(ev_path, encoding='utf-8'))
    evs = evs.get('eventos', evs) if isinstance(evs, dict) else evs
    print('=' * 74)
    print('CRAZY PING PONG · INFORME DE DECISIÓN (telemetría D1)')
    print('=' * 74)
    print(f'fuente eventos : {os.path.basename(ev_path)} · {len(evs)} eventos')
    if res_path and os.path.exists(res_path):
        try:
            res = json.load(open(res_path, encoding='utf-8'))
            print(f'fuente resumen : {os.path.basename(res_path)} · total={res.get("total")} · sesionesUnicas={res.get("sesionesUnicas")} · arranques24h={res.get("arranques24h")}')
        except Exception as e:
            res = {}
            print(f'fuente resumen : ilegible ({e})')
    else:
        res = {}

    # ---- sesiones -----------------------------------------------------
    ses = defaultdict(list)
    for e in evs:
        ses[e.get('sid', '?')].append(e)

    # ---- curva fps global ---------------------------------------------
    pings = [(e.get('t'), e.get('fps'), e.get('sid')) for e in evs if e.get('e') == 'vr_ping' and e.get('fps')]
    vr_ends = [(e.get('t'), e.get('fps'), e.get('fpsMin'), e.get('fpsMax'), e.get('sid')) for e in evs if e.get('e') == 'vr_end']
    if pings:
        fpsv = [p[1] for p in pings]
        print(f'\n· FPS (vr_ping): {len(fpsv)} muestras · media {sum(fpsv)/len(fpsv):.1f} · mín {min(fpsv)} · máx {max(fpsv)} · ≥78: {sum(1 for f in fpsv if f >= 78)}/{len(fpsv)}')
    if vr_ends:
        fvs = [v[1] for v in vr_ends if v[1]]
        if fvs:
            print(f'· FPS (vr_end): media {sum(fvs)/len(fvs):.1f} · máx absoluto {max(fvs)}')

    # ---- sesiones recientes (últimas 8) --------------------------------
    print('\n— SESIONES (últimas 8 por último evento) —')
    orden = sorted(ses.values(), key=lambda evs_s: max((e.get('t') or 0) for e in evs_s))[-8:]
    for grupo in reversed(orden):
        grupo = sorted(grupo, key=lambda e: e.get('t') or 0)
        sid = grupo[0].get('sid', '?')[:8]
        ver = next((e.get('v') for e in grupo if e.get('v')), '?')
        plat = next((e.get('platform') for e in grupo if e.get('platform')), '?')
        t0, t1 = grupo[0].get('t'), max((e.get('t') or 0) for e in grupo)
        span = (t1 - t0) if (t0 and t1 and t1 > t0) else None
        inicio = datetime.fromtimestamp((t0 or 0) / 1000, tz=timezone.utc).strftime('%d-%b %H:%M') if t0 else '?'
        vr_start = next((e for e in grupo if e.get('e') == 'vr_start'), None)
        vr_end = next((e for e in grupo if e.get('e') == 'vr_end'), None)
        # duración VR REAL: vr_start → último evento de VR (ping o vr_end).
        # (el campo dur de vr_end es la animación de cierre, NO la sesión)
        vr_dur = None
        if vr_start and vr_start.get('t'):
            t_vr = [e.get('t') for e in grupo if e.get('e') in ('vr_start', 'vr_ping', 'vr_end') and e.get('t')]
            if t_vr:
                vr_dur = max(t_vr) - vr_start['t']
        pings_s = [e.get('fps') for e in grupo if e.get('e') == 'vr_ping' and e.get('fps')]
        fps_txt = '/'.join(str(f) for f in pings_s) or '—'
        en_vr = 'EN VR AHORA' if (vr_start and not vr_end) else ('VR cerrada' if vr_end else 'sin VR')
        print(f'  · {sid} v{ver} [{plat}] {inicio} UTC · ventana {_fmt_dur(span)} · {en_vr}')
        if vr_dur:
            print(f'      dur VR {_fmt_dur(vr_dur)} · pings fps: {fps_txt}'
                  + (f" · vr_end {vr_end.get('fps')} fps (mín {vr_end.get('fpsMin')}, máx {vr_end.get('fpsMax')})" if vr_end and vr_end.get('fps') else ' · sin vr_end'))

    # ---- embudo champ_rank --------------------------------------------
    cr = [e for e in evs if e.get('e') == 'champ_rank']
    stages = [e for e in evs if e.get('e') == 'stage']
    champs_ev = [e for e in evs if e.get('e') == 'champion']
    if cr or stages or champs_ev:
        print('\n— EMBUDO POR CAMPEONATO (champ_rank / stage / champion) —')
        por_camp = defaultdict(lambda: defaultdict(list))
        for e in cr:
            c = e.get('champ', '?')
            por_camp[c]['intentos'].append(e)
        for e in stages:
            c = e.get('id', '?')
            por_camp[c]['stages'].append(e)
        for e in champs_ev:
            c = e.get('champ', e.get('id', '?'))
            por_camp[c]['champion'].append(e)
        if not por_camp:
            print('  (sin eventos de embudo todavía)')
        for c in sorted(por_camp, key=lambda x: (x not in CAMPS, x)):
            d = por_camp[c]
            intentos = d.get('intentos', [])
            wins = [e for e in intentos if e.get('win')]
            pruebas = defaultdict(lambda: [0, 0])
            for e in intentos:
                p = e.get('prueba', e.get('kind', '?'))
                pruebas[p][0] += 1
                if e.get('win'):
                    pruebas[p][1] += 1
            st = d.get('stages', [])
            st_max = None
            if st:
                st_max = max((_stage_humano(c, e.get('n')) for e in st if e.get('n') is not None), default=None)
            total = TOTAL_ETAPAS.get(c, '?')
            linea = f'  · {c:16} pruebas: '
            linea += ' · '.join(f'{p} {w}/{n}' for p, (n, w) in sorted(pruebas.items())) if pruebas else '—'
            linea += f' | etapa máx: {st_max}/{total}' if st_max else ' | etapa máx: —'
            if d.get('champion'):
                linea += f" | ★ CHAMPION ×{len(d['champion'])}"
            print(linea)
            # métricas de las últimas pruebas
            for e in intentos[-4:]:
                extra = {k: v for k, v in e.items() if k in ('prueba', 'win', 'score', 'stars', 'nv', 'duelScore', 'kills', 'wave', 'bricks', 'lives', 'left', 'bajas', 'total', 'estab', 'cubes', 'hull', 'golpes', 'objetivo', 'perdidas', 'ingots')}
                print(f"      {json.dumps(extra, ensure_ascii=False)}")
    else:
        print('\n— EMBUDO: aún sin champ_rank/stage/champion —')

    # ---- errores ------------------------------------------------------
    errs = [e for e in evs if e.get('e') == 'error']
    print('\n— ERRORES —')
    if not errs:
        print('  · cero errores reportados')
    else:
        por_msg = defaultdict(int)
        for e in errs:
            por_msg[str(e.get('msg', e.get('m', '?')))[:90]] += 1
        for msg, n in sorted(por_msg.items(), key=lambda kv: -kv[1]):
            print(f'  · ×{n} {msg}')

    # ---- adopción de versiones ----------------------------------------
    print('\n— ADOPCIÓN DE VERSIONES (boots) —')
    boots = defaultdict(int)
    for e in evs:
        if e.get('e') == 'boot':
            boots[e.get('v', '?')] += 1
    for v, n in sorted(boots.items(), key=lambda kv: -kv[1]):
        print(f'  · v{v:16} ×{n}')

    out = '\n(informe guardado en scripts/informe_ultimo.txt)\n'
    print(out)


if __name__ == '__main__':
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            main()
        except SystemExit:
            raise
    texto = buf.getvalue()
    sys.stdout.write(texto)
    with open(os.path.join(SCR, 'informe_ultimo.txt'), 'w', encoding='utf-8') as f:
        f.write(texto)
