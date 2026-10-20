#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA estático · SONIDO REAL DEL TREN + ORO VISIBLE (v3.6.23 · ronda 29) — capa V.

Congela la regresión de la ronda 28 del vagón del Oeste Y el fix v3.6.23:
  1 · Los 4 assets del artista existen en assets/tren/ (bytes > 0).
  2 · El SDK v1.5.1 exporta createBucle y oeste lo importa (con assetURL).
  3 · Cableado COMPLETO de las 4 pistas: rodadura on/_depart y off+llegada,
      Tren_Llegada en la estación, Tunel en la entrada ('pre'→'in'), galopes
      por instancia (spawn on · herido off seco · gone off) y cierre duro
      _galCorta() en dispose().
  4 · La regla SDK: NINGÚN decodeAudioData nuevo en el módulo.
  5 · FIX del apilado: prototipo girado 90° (root.rotation.y) + cajones a
      las ventanas (x 2,55) + rejilla 3×3 SIN solape (verificación numérica
      con los valores REALES del código: sepX/sepZ/jitter/yaw + bbox mundo
      del GLB medido 0,078×0,038×0,170).
  6 · NUEVO v3.6.23 (informe del dueño «no se oyen los sonidos del tren»):
      ignoraMute:true en los 3 motores del vagón (rodadura, galopes y SFX
      de la etapa) — el gate arcMute/_arcDucked es de MÚSICA, no de SFX;
      sin «¡YIHAAA!» sintético en las entradas (0 llamadas); auto-reparación
      por frame de los 3 bucles (contexto renacido en re-bind de VR);
      SDK v1.5.1 con play pendiente (el 1er play de una pista nunca mudo).
Idempotente y sin dependencias: sólo lectura de ficheros + aritmética.
"""
import json
import math
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
OESTE = RAIZ / 'public' / 'championships' / 'oeste'
SDK = RAIZ / 'public' / 'championships' / 'sdk' / 'champ_sdk.js'

ok = 0
fallos = 0


def chk(cond, msg):
    global ok, fallos
    if cond:
        ok += 1
        print(f'  ✓ {msg}')
    else:
        fallos += 1
        print(f'  ✗ FALLO: {msg}')


mod = (OESTE / 'index.js').read_text(encoding='utf-8')
sdk = SDK.read_text(encoding='utf-8')

# ── 1 · ASSETS DEL ARTISTA ────────────────────────────────────────────────
for f, mn in [('Tren_Llegada.mp3', 100000), ('vias.mp3', 100000),
              ('Tunel.mp3', 200000), ('caballos.mp3', 300000)]:
    p = OESTE / 'assets' / 'tren' / f
    chk(p.exists() and p.stat().st_size >= mn,
        f'asset assets/tren/{f} ({p.stat().st_size if p.exists() else 0} B)')

# ── 2 · SDK v1.5.0 + IMPORT ───────────────────────────────────────────────
chk("const SDK_VERSION = '1.5.1'" in sdk, 'SDK_VERSION = 1.5.1')
chk('export function createBucle' in sdk, 'SDK exporta createBucle')
chk('createBucle, createPowerSign' in sdk, 'createBucle en el export default')
chk(re.search(r"import \{[^}]*createBucle[^}]*assetURL[^}]*\} from '\.\./sdk/champ_sdk\.js'", mod) is not None,
    'oeste importa createBucle + assetURL del SDK')

# ── 2b · NUEVO v3.6.23 · IGNORAMUTE + PLAY PENDIENTE (SDK v1.5.1) ─────────
# El gate arcMute/_arcDucked es el silencio de la MÚSICA del arcade (BSO/
# vagón). Los SFX/ambiente del tren (rodadura, galopes, llegadas, túnel)
# suenan SIEMPRE — igual que los sintéticos de la casa, que nunca
# consultaron ese interruptor. Diagnóstico: el dueño tenía la música del
# arcade apagada y por eso NO oía las 4 pistas mp3 (gain 0,0001).
chk('const silencio = !O.ignoraMute && A && (A.arcMute || A._arcDucked);' in sdk,
    'SDK createSfx: gate con ignoraMute (v1.5.1)')
chk('if (!o.ignoraMute && A && (A.arcMute || A._arcDucked)) return 0.0001;' in sdk,
    'SDK createBucle: gate con ignoraMute (v1.5.1)')
chk('pend[name] = { vol, opts };' in sdk and 'delete pend[name]; play(' in sdk,
    'SDK createSfx: play PENDIENTE se auto-dispara al decodificar')

# ── 3 · CABLEADO DE LAS 4 PISTAS ──────────────────────────────────────────
chk('tren/vias.mp3' in mod, 'vias.mp3 referenciado (bucle de rodadura)')
chk('tren/caballos.mp3' in mod, 'caballos.mp3 referenciado (galope por instancia)')
chk(re.search(r"_depart\(\) \{[^}]*_viasBuc\.on\(\)", mod, re.S) is not None,
    '_depart → rodadura ON (mientras el vagón marcha)')
chk(re.search(r"_llegaEstacion\(\) \{.*?_viasBuc\.off\(\).*?Tren_Llegada\.mp3", mod, re.S) is not None,
    '_llegaEstacion → rodadura OFF + Tren_Llegada.mp3 (one-shot)')
chk(re.search(r"_tunnelPhase = 'in';.*?Tunel\.mp3", mod, re.S) is not None,
    "entrada de túnel ('pre'→'in') → Tunel.mp3 (one-shot)")
chk(re.search(r"_fjSpawn\(\) \{.*?_galBuc\(0\)\.on\(", mod, re.S) is not None,
    'forajido spawn → galope ON (desfasado + paneo)')
chk(re.search(r"_fjHerido\(\) \{.*?_galBuc\(0\)\.off\(true\)", mod, re.S) is not None,
    'forajido abatido → galope OFF seco')
chk(re.search(r"_indSpawn\(\) \{.*?_galBuc\(rec\.galK\)\.on\(", mod, re.S) is not None,
    'indios spawn → galope propio por jinete (desfasado)')
chk(re.search(r"_indHerido\(rec\) \{.*?_galBuc\(rec\.galK\)\.off\(true\)", mod, re.S) is not None,
    'indio abatido → SU galope OFF seco')
chk(re.search(r"dispose\(\) \{.*?_galCorta\(\);", mod, re.S) is not None,
    'dispose → _galCorta() (cierre duro de todos los bucles)')
chk('_galVol(' in mod and mod.count('_galVol(') >= 3,
    'volumen vivo por distancia (_galVol en forajido e indios)')

# ── 3b · NUEVO v3.6.23 · IGNORAMUTE EN EL VAGÓN + YIHHA FUERA + AUTOREPARACIÓN
b_vias = re.search(r"get _viasBuc\(\) \{.*?\n  \}", mod, re.S).group(0)
b_gal = re.search(r"_galBuc\(k\) \{.*?\n  \}", mod, re.S).group(0)
b_sfx = re.search(r"__sfxSDK\(\) \{[^}]*\}", mod, re.S).group(0)
chk('ignoraMute: true' in b_vias, 'rodadura _viasBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in b_gal, 'galopes _galBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in b_sfx, 'SFX de la etapa __sfxSDK: ignoraMute')
chk('this._sndYihha()' not in mod,
    'sin «¡YIHAAA!» sintético en las entradas (0 llamadas — método conservado)')
chk(mod.count('AUTOREPARACIÓN') >= 3 and '_viasBuc.suena()' in mod
    and '__galPool[0].suena()' in mod,
    'auto-reparación por frame (rodadura + galopes; re-bind de VR)')

# ── 4 · REGLA SDK: decode SOLO en el SDK ─────────────────────────────────
chk('decodeAudioData' not in mod, 'el módulo NO decodifica audio (regla SDK)')

# ── 5 · FIX DEL APILADO (lingotes sin interpenetración) ──────────────────
chk('root.rotation.y = Math.PI / 2;' in mod,
    'prototipo del lingote girado 90° (eje largo → X)')
chk(re.search(r"cajonOro: \{[^}]*x: 2\.55", mod, re.S) is not None,
    'cajones del oro pegados a las ventanas (x 2,55)')
cr = re.search(r"cajonOro: \{[^}]*\}", mod, re.S).group(0)
sepX = float(re.search(r'sepX: ([0-9.]+)', cr).group(1))
sepZ = float(re.search(r'sepZ: ([0-9.]+)', cr).group(1))
jX = float(re.search(r'jX: ([0-9.]+)', cr).group(1))
jZ = float(re.search(r'jZ: ([0-9.]+)', cr).group(1))
yaw = float(re.search(r'yaw: ([0-9.]+)', cr).group(1))
# bbox MUNDO del GLB (scripts/mide_lingote_mundo.py, con TRS de nodos)
L, W = 0.170, 0.0778                      # eje largo → X tras la rotación
ext_x = L * math.cos(yaw) + W * math.sin(yaw)
ext_z = W * math.cos(yaw) + L * math.sin(yaw)
hueco_x = sepX - ext_x - 2 * jX
hueco_z = sepZ - ext_z - 2 * jZ
chk(hueco_x > 0, f'rejilla sin solape en columnas (hueco +{hueco_x * 1000:.1f} mm)')
chk(hueco_z > 0, f'rejilla sin solape en filas (hueco +{hueco_z * 1000:.1f} mm)')
chk(2 * sepX + ext_x <= 0.72 and 2 * sepZ + ext_z <= 0.36,
    f'rejilla 3×3 cabe en el cajón ({2 * sepX + ext_x:.3f} × {2 * sepZ + ext_z:.3f} de 0,72 × 0,36)')

print(f'\nSONIDO DEL TREN · {ok} OK · {fallos} FALLOS')
sys.exit(1 if fallos else 0)
