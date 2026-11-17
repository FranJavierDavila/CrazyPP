#!/usr/bin/env python3
"""v2.108 · Verificación ESTÁTICA del modo depuración (núcleo + 3 módulos)."""
import io, sys

BASE = '/home/z/my-project/crazypp'
fails = 0

def chk(name, cond, where=''):
    global fails
    print(f'[{"OK" if cond else "FAIL"}] {name}' + (f'  ({where})' if where and not cond else ''))
    if not cond: fails += 1

def read(p):
    with io.open(f'{BASE}/{p}', encoding='utf-8') as f:
        return f.read()

core = read('index.html')
magia = read('championships/magia/index.js')
locura = read('championships/locura/index.js')
oeste = read('championships/oeste/index.js')

print('== NÚCLEO (index.html) ==')
chk('ppDebugMode() definida (foro3d, minúsculas)', "toLowerCase() === 'foro3d'" in core)
chk('window.__PP_DEBUG al arrancar', 'window.__PP_DEBUG = ppDebugMode()' in core)
chk('ppDebugRefresh() publica el refresco', 'window.ppDebugRefresh' in core)
chk('interceptor Storage.setItem', 'OP.__ppDebugGuard' in core)
chk('interceptor: pp_champ_*', "s.indexOf('pp_champ_') === 0" in core)
chk('interceptor: pp_arcade_*', "s.indexOf('pp_arcade_') === 0" in core)
chk('interceptor: pp_worldrank_cache', "s === 'pp_worldrank_cache'" in core)
chk('interceptor: ppxr_stats_v1 (stats núcleo)', "s === 'ppxr_stats_v1'" in core)
chk('WORLDRANK.submit guardado', 'window.__PP_DEBUG) return false' in core)
chk('__PP_TELE.ev guardado (telemetría)', core.count('window.__PP_DEBUG) return;') >= 1)
chk('teclado nombre: fila de dígitos', "btn('nkey:' + d, 56 + d * 90, 814" in core)
chk('guardar nombre → ppDebugRefresh', 'window.ppDebugRefresh) window.ppDebugRefresh(); } catch { /* */ }\n          this._nameBuf' in core.replace('\r\n', '\n'))
chk('reset registros → ppDebugRefresh', core.count('if (window.ppDebugRefresh) window.ppDebugRefresh();') >= 2)
chk('rótulo 3D: _updateDebugBadge()', '_updateDebugBadge()' in core)
chk('rótulo 3D: llamado cada frame', 'this._updateDebugBadge();   // v2.108' in core)
chk('rótulo 3D: texto MODO DEPURACIÓN', "cx.fillText('MODO DEPURACIÓN'" in core)
chk('rótulo 2D: #ppdbg en portada', 'id="ppdbg"' in core and 'MODO DEPURACIÓN</div>' in core)
chk('rótulo 2D: gancho __ppDbg2D', 'window.__ppDbg2D = paint' in core)
chk('versión 2.108.0', "const VERSION = '2.108.0';" in core)

print('== MAGIA ==')
chk('helper ppDbg()', 'function ppDbg()' in magia)
chk('maxIdx debug (replayMap)', 'maxIdx: ppDbg() ? 4 : Math.min(this.stage | 0, 4)' in magia)
chk('replayLaunch: vía replay en debug para nodos futuros', '(!ppDbg() || i === this.stage)' in magia)
chk('anuncio DEPURACIÓN · ETAPA N', "'DEPURACIÓN · ETAPA '" in magia)
chk('tapas levantadas en debug', '!champion && !ppDbg() && this.currentIdx < t.idx' in magia)

print('== LOCURA ==')
chk('helper ppDbg()', 'function ppDbg()' in locura)
chk('maxIdx debug (replayMap)', 'maxIdx: ppDbg() ? 4 : Math.min(this.stage | 0, 4)' in locura)
chk('replayLaunch: vía replay en debug para nodos futuros', '(!ppDbg() || i === this.stage)' in locura)
chk('anuncio DEPURACIÓN · ETAPA N', "'DEPURACIÓN · ETAPA '" in locura)
chk('tapas levantadas en debug', '!champion && !ppDbg() && this.currentIdx < t.idx' in locura)

print('== OESTE ==')
chk('helper ppDbg()', 'function ppDbg()' in oeste)
chk('maxIdx debug (replayMap)', 'maxIdx: ppDbg() ? 4 : clamp(this.stage, 1, 5) - 1' in oeste)
chk('tapas levantadas en debug (_refreshMap)', 't.visible = ppDbg() ? false : (nd >= this.stage)' in oeste)
chk('replayLaunch ya acepta cualquier nodo (v2.96, intacto)', 'this._replayReal = st;' in oeste)
chk('restauración post-intento (victoria)', '_replayReal != null' in oeste)

print('== MANIFESTS ==')
import json
for cid, ver in (('oeste', 27), ('locura', 12), ('magia', 22)):
    m = json.load(open(f'{BASE}/championships/{cid}/manifest.json', encoding='utf-8'))
    chk(f'{cid}: version={ver} + note_dbg', m.get('version') == ver and 'note_dbg' in m)

print('\nRESULTADO:', 'TODO OK' if fails == 0 else f'{fails} FALLOS')
sys.exit(1 if fails else 0)
