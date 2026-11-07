#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA estático · SONIDO REAL DEL TREN (v3.6.24 · ronda 30) — capa V.

Congela la regresión del vagón del Oeste (rondas 28-30):
  1 · Los 4 assets del artista existen en assets/tren/ (bytes > 0).
  2 · SDK v1.5.2 exporta createBucle y oeste lo importa (con assetURL).
  3 · Cableado COMPLETO de las 4 pistas + MOMENTOS DEL DUEÑO (v3.6.24):
      · vias.mp3: ON en _depart, setVol DIRECTO por frame en marcha (el
        mecanismo que llegó al hardware de la Quest en los galopes), OFF
        con fundido al frenar en _llegaEstacion.
      · Tren_Llegada.mp3: «poco después de que se anuncien los segundos
        para llegar a la estación» — agenda _llPistaT=1,2 tras el anuncio
        de megafonía (tren_mega_llega) y NADA al frenar.
      · Tunel.mp3: «cuando en el parallax del plano exterior se cargan
        las imágenes tunelboca.png» — ONE-SHOT al nacer la fase 'pre'
        (la boca aparece a lo lejos), NADA al cruzar el ojo ('in').
      · one-shots CON REINTENTOS (_pistaTren/_pistaTrenStep en fxStep).
      · caballos.mp3: galopes por instancia (spawn on · herido off seco ·
        gone off) y cierre duro _galCorta() en dispose().
  4 · La regla SDK: NINGÚN decodeAudioData nuevo en el módulo.
  5 · FIX del apilado: prototipo girado 90° + cajones a las ventanas +
      rejilla 3×3 SIN solape (verificación numérica con valores reales).
  6 · v3.6.23: ignoraMute:true en los 3 motores; sin «¡YIHAAA!»; auto-
      reparación por frame de los 3 bucles.
  7 · NUEVO v3.6.24 (informe del dueño «solo caballos» — el dispositivo
      real sólo obedecía a la escritura de ganancia directa por frame):
      SDK v1.5.2 · (a) suena() cuenta MUERTA la instancia de un contexto
      renacido (antes true: bloqueaba la auto-reparación); (b) setVol
      respeta ignoraMute (la escritura viva ya no re-aplica el mute de
      MÚSICA); (c) on()/play() con el contexto dormido quedan PENDIENTES
      y el statechange del propio AudioContext los despierta (un one-shot
      ya no se pierde para nunca).
Idempotente y sin dependencias: sólo lectura de ficheros + aritmética.
"""
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

# ── 2 · SDK v1.5.2 + IMPORT ───────────────────────────────────────────────
chk("const SDK_VERSION = '1.5.2'" in sdk, 'SDK_VERSION = 1.5.2')
chk('export function createBucle' in sdk, 'SDK exporta createBucle')
chk('createBucle, createPowerSign' in sdk, 'createBucle en el export default')
chk(re.search(r"import \{[^}]*createBucle[^}]*assetURL[^}]*\} from '\.\./sdk/champ_sdk\.js'", mod) is not None,
    'oeste importa createBucle + assetURL del SDK')

# ── 2b · v3.6.23 · IGNORAMUTE + PLAY PENDIENTE (mantenido) ────────────────
chk('const silencio = !O.ignoraMute && A && (A.arcMute || A._arcDucked);' in sdk,
    'SDK createSfx: gate con ignoraMute (v1.5.1)')
chk('if (!o.ignoraMute && A && (A.arcMute || A._arcDucked)) return 0.0001;' in sdk,
    'SDK createBucle: gate con ignoraMute en objetivo()')
chk('pend[name] = { vol, opts };' in sdk and 'delete pend[name]; play(' in sdk,
    'SDK createSfx: play PENDIENTE se auto-dispara al decodificar')

# ── 2c · NUEVO v3.6.24 · SDK v1.5.2 (los 3 agujeros del dispositivo) ──────
chk(re.search(r"function suena\(\) \{[^}]*inst\.src\.context === a", sdk, re.S) is not None,
    'SDK suena(): instancia de contexto MUERTO = false (reparación libre)')
sv = re.search(r"function setVol\(v\) \{.*?inst\.gain\.gain\.value = eff;", sdk, re.S)
chk(sv is not None and '!o.ignoraMute && A && (A.arcMute || A._arcDucked)' in sv.group(0),
    'SDK setVol(): respeta ignoraMute (escritura viva sin mute de música)')
chk(sdk.count("addEventListener('statechange'") >= 2,
    'SDK: statechange en createSfx Y createBucle (despertar del ctx dormido)')
pl = re.search(r"function play\(name, vol, opts\) \{.*?\n  \}", sdk, re.S).group(0)
chk("if (actx.state !== 'running') {" in pl and 'pend[name] = { vol, opts };' in pl,
    'SDK createSfx.play(): ctx dormido queda PENDIENTE, no descartado')
ob = re.search(r"function on\(desfase, panv\) \{.*?\n  \}", sdk, re.S).group(0)
chk("if (actx.state !== 'running') {" in ob and 'pendArranque' in ob,
    'SDK createBucle.on(): ctx dormido recuerda wanted + (desfase, pan)')
chk('pendArranque = { desfase: desfase || 0, panv: panv || 0 };' in sdk,
    'SDK: el desfase/pano del arranque dormido se conserva')
chk('sonando: suena(),' in sdk,
    'SDK estado(): usa la suena() consciente de contexto (QA honesta)')

# ── 3 · CABLEADO DE LAS 4 PISTAS (momentos del dueño v3.6.24) ─────────────
chk('tren/vias.mp3' in mod, 'vias.mp3 referenciado (bucle de rodadura)')
chk('tren/caballos.mp3' in mod, 'caballos.mp3 referenciado (galope por instancia)')
chk(re.search(r"_depart\(\) \{[^}]*_viasBuc\.on\(\)", mod, re.S) is not None,
    '_depart → rodadura ON (desde que salimos)')
# setVol DIRECTO por frame mientras marcha (mecanismo del galope)
i_pista = mod.find('this._pistaTrenStep(dt);')
i_setvol = mod.find('this._viasBuc.setVol(0.13);')
chk(i_pista != -1 and i_setvol != -1 and 0 < i_setvol - i_pista < 600,
    'fxStep → rodadura con setVol DIRECTO por frame en marcha '
    '(junto a los reintentos de los one-shots)')
chk(re.search(r"if \(this\.phase === 'run'\) \{\s*try \{ this\._viasBuc\.setVol", mod) is not None,
    'el setVol vivo de la rodadura es SÓLO en marcha (run)')
chk(re.search(r"_llegaEstacion\(\) \{.*?_viasBuc\.off\(\)", mod, re.S) is not None,
    '_llegaEstacion → rodadura OFF (frenado)')
# Tren_Llegada: tras el anuncio de segundos (+1,2 s), NADA al frenar
chk(re.search(r"tren_mega_llega.*?this\._llPistaT = 1\.2;", mod, re.S) is not None,
    'anuncio de segundos → agenda el silbato del artista a +1,2 s')
chk(re.search(r"if \(this\._llPistaT > 0\) \{.*?_pistaTren\('tren/Tren_Llegada\.mp3', 0\.5\);", mod, re.S) is not None,
    'disparo diferido de Tren_Llegada.mp3 (con reintentos)')
chk(re.search(r"_llegaEstacion\(\) \{.*?_viasBuc\.off\(\).*?\n  \}", mod, re.S).group(0).find('Tren_Llegada') == -1,
    '_llegaEstacion ya NO dispara Tren_Llegada (sonó con el anuncio)')
chk(mod.count("play('tren/Tren_Llegada") == 0 and mod.count("play('tren/Tunel") == 0,
    'cero play() directo de one-shots (siempre vía _pistaTren con reintentos)')
# Tunel: al APARECER la boca (nace 'pre'), NADA al cruzar el ojo ('in')
pre = re.search(r"this\._tunnelPhase = 'pre';.*?_pistaTren\('tren/Tunel\.mp3', 0\.42\);", mod, re.S)
chk(pre is not None, "fase 'pre' (aparece tunelboca.png) → Tunel.mp3 (one-shot)")
chk(pre is not None and 'tunelGrp.visible = true;' in pre.group(0),
    'el disparo del túnel vive junto a la aparición de la boca (parallax)')
chk(re.search(r"this\._tunnelPhase = 'in';\s*this\._tunnelT2 = 0;\s*\}", mod) is not None,
    "la transición 'in' ya NO dispara sonido (sólo cambia de fase)")
# one-shots con reintentos
chk('_pistaTren(name, vol) {' in mod and '_pistaTrenStep(dt) {' in mod,
    '_pistaTren/_pistaTrenStep: agenda con reintentos para los one-shots')
chk('this._pistaTrenStep(dt);' in mod,
    '_pistaTrenStep corre cada frame (fxStep)')
chk('t: 6' in mod and 'eng.tiene(p.name)' in mod,
    'los reintentos viven 6 s y exigen buffer del motor')
# galopes por instancia (ronda 28, intacto)
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
chk('this._trenPend = [];' in (re.search(r"_galCorta\(\) \{.*?\n  \}", mod, re.S).group(0)),
    '_galCorta también vacía los one-shots agendados (dispose limpio)')

# ── 3b · v3.6.23 · IGNORAMUTE EN EL VAGÓN + YIHHA FUERA + AUTOREPARACIÓN ──
b_vias = re.search(r"get _viasBuc\(\) \{.*?\n  \}", mod, re.S).group(0)
b_gal = re.search(r"_galBuc\(k\) \{.*?\n  \}", mod, re.S).group(0)
b_sfx = re.search(r"__sfxSDK\(\) \{[^}]*\}", mod, re.S).group(0)
chk('ignoraMute: true' in b_vias, 'rodadura _viasBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in b_gal, 'galopes _galBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in b_sfx, 'SFX de la etapa __sfxSDK: ignoraMute')
chk('this._sndYihha()' not in mod,
    'sin «¡YIHAAA!» sintético en las entradas (0 llamadas — método conservado)')
chk(mod.count('AUTOREPARACIÓN') >= 2 and '_viasBuc.suena()' in mod
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

print(f'\nSONIDO DEL TREN v3624 · {ok} OK · {fallos} FALLOS')
sys.exit(1 if fallos else 0)
