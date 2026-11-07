#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA estático · SONIDO REAL DEL TREN (v3.6.26 · ronda 33) — capa V.

Congela la regresión del vagón del Oeste (rondas 28-33):
  1 · Los 4 assets del artista existen en assets/tren/ (bytes > 0) y las
      dos pistas mudas en el dispositivo (Tunel + Tren_Llegada) están en
      el PERFEL PROBADO de caballos.mp3 (44100 Hz · 256 kbps CBR).
  2 · SDK v1.5.4 exporta createBucle (+ precarga) y oeste lo importa.
  3 · Cableado COMPLETO de las 4 pistas:
      · vias.mp3: ON en _depart, setVol DIRECTO por frame en marcha, OFF
        con fundido al frenar en _llegaEstacion.
      · Tren_Llegada.mp3: CONCATENADO CON LA VOZ (v3.6.26, petición del
        dueño «igual concatenando el sonido con la voz que sí suena») —
        entra justo al terminar la locución real (audio._voiceDur).
      · Tunel.mp3: ONE-SHOT CUANDO SE BAJA LA LUZ (v3.6.26, petición del
        dueño «ver de lanzarlo cuando se baja la luz») — paso 'pre'→'in'
        de _tunnelStep, ya NO al nacer la fase 'pre'.
      · one-shots POR EL MOTOR DEL GALOPE (v3.6.26): _pistaTren agenda y
        _pistaTrenStep dispara con createBucle.on() — el motor PROBADO en
        el hardware de la Quest (galopes + rodadura) —, corta con off()
        ANTES del wrap de src.loop (contador p.vivo) y desiste en paz a
        los 12 s. Cero play() de createSfx para los one-shots.
      · caballos.mp3: galopes por instancia (spawn on · herido off seco ·
        gone off) y cierre duro _galCorta() en dispose().
  4 · La regla SDK: NINGÚN decodeAudioData nuevo en el módulo.
  5 · FIX del apilado: rejilla 3×3 SIN solape (aritmética con valores reales).
  6 · v3.6.23: ignoraMute:true en los 3 motores; sin «¡YIHAAA!»; auto-
      reparación por frame.
  7 · HEREDADO v3.6.25 (el galope fantasma): auto-reparación SÓLO con
      jinete vivo; rodadura 0,30; contrato SDK booleano/sinPend/huérfana
      muerta/vigilante anti-decode-colgado.
  8 · NUEVO v3.6.26 (el one-shot sordo en el dispositivo): SDK v1.5.4
      createBucle.precarga() — pedir + decodificar SIN sonar; el módulo
      precarga los one-shots EN LOS DOS MOTORES (createSfx heredado y el
      motor del galope nuevo).
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
# v3.6.26: las dos pistas mudas en el dispositivo, en el PERFIL PROBADO de
# caballos.mp3 (44100 Hz · 256 kbps) — cero rarezas de encoder para el
# decoder de la Quest.
chk((OESTE / 'assets' / 'tren' / 'Tunel.mp3').stat().st_size > 350000,
    'Tunel.mp3 re-codificado a 256 kbps (perfil caballos)')
chk((OESTE / 'assets' / 'tren' / 'Tren_Llegada.mp3').stat().st_size > 120000,
    'Tren_Llegada.mp3 re-codificado a 256 kbps (perfil caballos)')

# ── 2 · SDK v1.5.4 + IMPORT ───────────────────────────────────────────────
chk("const SDK_VERSION = '1.6.0'" in sdk, 'SDK_VERSION = 1.6.0 (re-ancla honesto r98 — 1.6.0 desde la r97)')
chk('export function createBucle' in sdk, 'SDK exporta createBucle')
chk('createBucle, createRivalVoz, createPowerSign' in sdk, 'createBucle en el export default (con createRivalVoz r97)')
chk(re.search(r"import \{[^}]*createBucle[^}]*assetURL[^}]*\} from '\.\./sdk/champ_sdk\.js'", mod) is not None,
    'oeste importa createBucle + assetURL del SDK')

# ── 2b · HEREDADO v1.5.1 · IGNORAMUTE + PLAY PENDIENTE ────────────────────
chk('const silencio = !O.ignoraMute && A && (A.arcMute || A._arcDucked);' in sdk,
    'SDK createSfx: gate con ignoraMute (v1.5.1)')
chk('if (!o.ignoraMute && A && (A.arcMute || A._arcDucked)) return 0.0001;' in sdk,
    'SDK createBucle: gate con ignoraMute en objetivo()')
chk('pend[name] = { vol, opts };' in sdk and 'delete pend[name]; play(' in sdk,
    'SDK createSfx: play PENDIENTE se auto-dispara al decodificar')

# ── 2c · HEREDADO v1.5.2 · LOS 3 AGUJEROS DEL DISPOSITIVO ─────────────────
chk(re.search(r"function suena\(\) \{[^}]*inst\.src\.context === a", sdk, re.S) is not None,
    'SDK suena(): instancia de contexto MUERTO = false (reparación libre)')
sv = re.search(r"function setVol\(v\) \{.*?inst\.gain\.gain\.value = eff;", sdk, re.S)
chk(sv is not None and '!o.ignoraMute && A && (A.arcMute || A._arcDucked)' in sv.group(0),
    'SDK setVol(): respeta ignoraMute (escritura viva sin mute de música)')
chk(sdk.count("addEventListener('statechange'") >= 2,
    'SDK: statechange en createSfx Y createBucle (despertar del ctx dormido)')
pl = re.search(r"function play\(name, vol, opts\) \{.*?\n  \}", sdk, re.S).group(0)
chk("if (actx.state !== 'running') {" in pl,
    'SDK createSfx.play(): ctx dormido queda PENDIENTE, no descartado')
ob = re.search(r"function on\(desfase, panv\) \{.*?\n  \}", sdk, re.S).group(0)
chk("if (actx.state !== 'running') {" in ob and 'pendArranque' in ob,
    'SDK createBucle.on(): ctx dormido recuerda wanted + (desfase, pan)')
chk('sonando: suena(),' in sdk,
    'SDK estado(): usa la suena() consciente de contexto (QA honesta)')

# ── 2d · HEREDADO v1.5.3 · EL GALOPE FANTASMA ─────────────────────────────
chk('return true;' in pl and pl.rstrip().endswith('return false;\n  }') is False
    and 'return false;' in pl,
    'SDK play(): contrato BOOLEANO (true sólo con disparo real)')
chk('if (!(opts && opts.sinPend)) pend[name]' in pl,
    'SDK play(): opción sinPend — el que reintentA gobierna (cero dobles)')
chk('delete pend[name];     // v1.5.3: el disparo real CONSUME el pend' in sdk,
    'SDK play(): el disparo real CONSUME el pend del nombre')
chk('busyAt[name] = Date.now();' in sdk and 'Date.now() - (busyAt[name] || 0) < 20000' in sdk,
    'SDK createSfx: vigilante anti-decode-colgado (busyAt, 20 s)')
chk('busy = true; busyAt = Date.now();' in sdk and 'Date.now() - busyAt < 20000' in sdk,
    'SDK createBucle: vigilante anti-decode-colgado (busyAt, 20 s)')
okill = re.search(r"// contexto muerto \(re-bind de VR\): v1\.5\.3 — MATAR la huérfana.*?inst = null;", sdk, re.S)
chk(okill is not None and 'inst.src.stop()' in okill.group(0)
    and 'inst.gain.disconnect()' in okill.group(0),
    'SDK createBucle.on(): MATA la instancia huérfana (stop + disconnect)')
chk(sdk.count('pendArranque = null;') >= 3,
    'SDK createBucle: el arranque CONSUME pendArranque (3 rutas)')

# ── 2e · NUEVO v3.6.26 · SDK v1.5.4 (el one-shot sordo en el dispositivo) ─
pc = re.search(r"function precarga\(\) \{[^}]*\}", sdk, re.S)
chk(pc is not None and 'cargar(a)' in pc.group(0) and 'cargar' in pc.group(0)
    and 'on(' not in pc.group(0),
    'SDK createBucle.precarga(): decodifica SIN sonar (v1.5.4)')
chk('return { on, off, setVol, suena, estado, precarga };' in sdk,
    'SDK createBucle: precarga en el contrato público')

# ── 3 · CABLEADO DE LAS 4 PISTAS ─────────────────────────────────────────
chk('tren/vias.mp3' in mod, 'vias.mp3 referenciado (bucle de rodadura)')
chk('tren/caballos.mp3' in mod, 'caballos.mp3 referenciado (galope por instancia)')
chk(re.search(r"_depart\(\) \{[\s\S]{0,900}?_viasBuc\.on\(\)", mod) is not None,
    '_depart → rodadura ON (desde que salimos)')
# PRECARGA de los one-shots: en createSfx (heredado) Y en el motor del
# galope (v3.6.26) — el buffer que madura es el del motor que SUENA.
chk(mod.count("precarga('tren/Tren_Llegada.mp3')") == 1
    and mod.count("precarga('tren/Tunel.mp3')") == 1,
    'precarga createSfx de LOS DOS one-shots (heredada)')
chk("__pistaUna('tren/Tren_Llegada.mp3', 0.5).precarga()" in mod
    and "__pistaUna('tren/Tunel.mp3', 0.42).precarga()" in mod,
    'precarga EN EL MOTOR DEL GALOPE de los dos one-shots (v3.6.26)')
i_prec = mod.find("precarga('tren/Tren_Llegada.mp3')")
i_dep = mod.find('_depart() {')
chk(i_prec != -1 and i_dep != -1 and i_prec < i_dep,
    'la precarga vive en el start() de la etapa (ANTES de cualquier _depart)')
# setVol DIRECTO por frame mientras marcha (mecanismo del galope) a 0,30
i_pista = mod.find('this._pistaTrenStep(dt);')
i_setvol = mod.find('this._viasBuc.setVol(0.30);')
chk(i_pista != -1 and i_setvol != -1 and 0 < i_setvol - i_pista < 600,
    'fxStep → rodadura con setVol DIRECTO por frame en marcha (0,30)')
chk(re.search(r"if \(this\.phase === 'run'\) \{\s*try \{ this\._viasBuc\.setVol", mod) is not None,
    'el setVol vivo de la rodadura es SÓLO en marcha (run)')
bv = re.search(r"get _viasBuc\(\) \{.*?\n  \}", mod, re.S).group(0)
chk('vol: () => 0.30,' in bv,
    'rodadura con cuerpo: vol 0,30 (0,13 era «casi imperceptible»)')
chk(re.search(r"_llegaEstacion\(\) \{.*?_viasBuc\.off\(\)", mod, re.S) is not None,
    '_llegaEstacion → rodadura OFF (frenado)')
# Tren_Llegada: CONCATENADO CON LA VOZ (v3.6.26) — a la caída de la
# locución real (_voiceDur), NADA al frenar en el andén
chk(re.search(r"tren_mega_llega.*?_voiceDur", mod, re.S) is not None,
    'anuncio de segundos → mide la duración de la VOZ real (_voiceDur)')
chk('this._llPistaT = durV + 0.35;' in mod,
    'el silbato del artista entra al CAER la locución (+0,35 s de cola)')
chk(re.search(r"if \(durV < 1\.0 \|\| durV > 8\.0\) durV = 2\.8;", mod) is not None,
    'fallback honesto de duración (megáfono apagado / respaldo TTS)')
chk(re.search(r"if \(this\._llPistaT > 0\) \{.*?_pistaTren\('tren/Tren_Llegada\.mp3', 0\.5, 4\.5\);", mod, re.S) is not None,
    'disparo diferido de Tren_Llegada.mp3 (con dur para el corte)')
chk(mod.count("play('tren/Tren_Llegada") == 0 and mod.count("play('tren/Tunel") == 0,
    'cero play() de createSfx para one-shots (siempre vía _pistaTren)')
# Tunel: CUANDO SE BAJA LA LUZ (paso 'pre'→'in'), NADA al nacer 'pre'
tin = re.search(r"this\._tunnelPhase = 'in';\s*this\._tunnelT2 = 0;.*?_pistaTren\('tren/Tunel\.mp3', 0\.42, 13\.9\);", mod, re.S)
chk(tin is not None, "paso 'pre'→'in' (SE BAJA LA LUZ) → Tunel.mp3 (one-shot)")
pre = re.search(r"this\._tunnelPhase = 'pre';[\s\S]{0,700}?_pistaTren\('tren/Tunel", mod)
chk(pre is None, "el disparo del túnel YA NO va al nacer 'pre' (boca a lo lejos)")
chk('_pistaTren(\'tren/Tunel.mp3\', 0.42' in mod and
    mod.count("_pistaTren('tren/Tunel.mp3'") == 1,
    'una sola vía de disparo del Tunel (en la caída de la luz)')

# ── 3a · NUEVO v3.6.26 · LOS ONE-SHOTS VIAJAN EN EL MOTOR DEL GALOPE ──────
pu = re.search(r"__pistaUna\(name, vol\) \{.*?\n  \}", mod, re.S)
chk(pu is not None and 'createBucle(() => this.game' in pu.group(0)
    and 'assetURL(import.meta.url, name)' in pu.group(0),
    '__pistaUna: cada one-shot es un createBucle del SDK (motor probado)')
chk('ignoraMute: true' in pu.group(0) and 'fadeIn: 0.06' in pu.group(0)
    and 'stopFade: 0.35' in pu.group(0),
    '__pistaUna: ignoraMute + fade corto de entrada y de corte')
chk('_pistaTren(name, vol, dur) {' in mod and '_pistaTrenStep(dt) {' in mod,
    '_pistaTren/_pistaTrenStep: agenda del motor del galope')
chk('this._pistaTrenStep(dt);' in mod,
    '_pistaTrenStep corre cada frame (fxStep)')
chk('t: 12' in mod, 'los reintentos viven 12 s de margen')
pt = re.search(r"_pistaTrenStep\(dt\) \{.*?\n  \}", mod, re.S).group(0)
chk('b.on(0, 0)' in pt,
    'el disparo es on() del MOTOR PROBADO (revival + espera de buffer incluidos)')
chk('b.suena()' in pt and 'p.vivo' in pt,
    'el reloj de play sólo corre con suena() honesto (instancia viva y en el ctx activo)')
chk('b.off()' in pt and 'this._trenPend.splice(i, 1);' in pt,
    'corte con off() ANTES del wrap de src.loop + retiro de la agenda')
chk(mod.count('b.on(0, 0)') == 1,
    'una sola vía de disparo de one-shots (sin llamadas sueltas)')

# ── 3b · GALOPES: ciclo de vida SANO (v3.6.25, el galope fantasma) ────────
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
# LA REPARACIÓN SÓLO CON JINETE VIVO (el fix del galope fantasma)
fjrep = re.search(r"if \(this\.__galPool && this\.__galPool\[0\] &&\s*"
                  r"\(this\._fjState === 'paso' \|\| this\._fjState === 'ida' \|\|\s*"
                  r"this\._fjState === 'ventana' \|\| this\._fjState === 'fuga'\)\) \{", mod)
chk(fjrep is not None,
    'forajido: auto-reparación SÓLO en paso/ida/ventana/fuga (sin resurrec'
    'ciones tras el balazo)')
indrep = re.search(r"if \(rec\.galK && rec\.state !== 'gone' && this\.__galPool &&\s*"
                   r"this\.__galPool\[rec\.galK\] &&\s*"
                   r"\(rec\.state === 'ida' \|\| rec\.state === 'ventana' \|\|\s*"
                   r"rec\.state === 'fuga'\)\) \{", mod)
chk(indrep is not None,
    'indios: TODO el bloque (setVol incluido) sólo con jinete vivo')

# ── 3c · HEREDADO v3.6.23 · IGNORAMUTE + YIHHA FUERA + AUTOREPARACIÓN ─────
bg = re.search(r"_galBuc\(k\) \{.*?\n  \}", mod, re.S).group(0)
bsfx = re.search(r"__sfxSDK\(\) \{[^}]*\}", mod, re.S).group(0)
chk('ignoraMute: true' in bv, 'rodadura _viasBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in bg, 'galopes _galBuc: ignoraMute (SFX, no música)')
chk('ignoraMute: true' in bsfx, 'SFX de la etapa __sfxSDK: ignoraMute')
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
cr = re.search(r"cajonOro: \{[^}]*\}", mod, re.S).group(0)
sepX = float(re.search(r'sepX: ([0-9.]+)', cr).group(1))
sepZ = float(re.search(r'sepZ: ([0-9.]+)', cr).group(1))
jX = float(re.search(r'jX: ([0-9.]+)', cr).group(1))
jZ = float(re.search(r'jZ: ([0-9.]+)', cr).group(1))
yaw = float(re.search(r'yaw: ([0-9.]+)', cr).group(1))
L, W = 0.170, 0.0778
ext_x = L * math.cos(yaw) + W * math.sin(yaw)
ext_z = W * math.cos(yaw) + L * math.sin(yaw)
hueco_x = sepX - ext_x - 2 * jX
hueco_z = sepZ - ext_z - 2 * jZ
chk(hueco_x > 0, f'rejilla sin solape en columnas (hueco +{hueco_x * 1000:.1f} mm)')
chk(hueco_z > 0, f'rejilla sin solape en filas (hueco +{hueco_z * 1000:.1f} mm)')
chk(2 * sepX + ext_x <= 0.72 and 2 * sepZ + ext_z <= 0.36,
    f'rejilla 3×3 cabe en el cajón ({2 * sepX + ext_x:.3f} × {2 * sepZ + ext_z:.3f} de 0,72 × 0,36)')

print(f'\nSONIDO DEL TREN v3626 · {ok} OK · {fallos} FALLOS')
sys.exit(1 if fallos else 0)
