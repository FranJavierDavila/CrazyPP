"""Fase E · ASISTENTE DE CREACIÓN DE CAMPEONATOS — CRAZY PING PONG v2.125

Transforma una idea en un PAQUETE DE CAMPEONATO completo, validado e integrado:
  1 Ficha      id, título, descripción, tema, dificultad
  2 Rival      nombre, estados (con provisionales dibujados)
  3 Poderes    del stock (confeti) o marcados «requieren módulo»
  4 Materiales inventario + provisionales reales (PNG con alfa, sala, BSO wav)
  5 Pruebas    duelo del núcleo con dificultad propia (stock)
  6 Sala       decorado de 6 planos + troqueles decor
  7 Montaje    manifest.json + index.js + índice regenerado + VALIDACIÓN

El resultado ES JUGABLE desde el primer minuto (plantilla stock: sala+rival+
BSO+duelo del núcleo con aiMul); el artista reemplaza provisionales después.

Uso:
  python3 scripts/plataforma/crear_campeonato.py                    # interactivo
  python3 scripts/plataforma/crear_campeonato.py --semilla s.json   # automático
  python3 scripts/plataforma/crear_campeonato.py --plantilla oeste ...  # valores base
"""
import json
import math
import struct
import subprocess
import sys
import time
import wave
from pathlib import Path

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

RAIZ = Path('/home/z/my-project')
PUB = RAIZ / 'public'
CHAMPS = PUB / 'championships'
PLAT = RAIZ / 'scripts' / 'plataforma'

TEMAS = {
    'oeste':   {'base': '#b98b4a', 'suelo': '#8a5a2b', 'techo': '#5c3a1a', 'pared': '#a97b3f',
                'acento': '#7c231a', 'rival': '#7a5c34'},
    'circo':   {'base': '#c23b3b', 'suelo': '#8f2f2f', 'techo': '#5c1616', 'pared': '#d94f4f',
                'acento': '#e8b45a', 'rival': '#c23b3b'},
    'magia':   {'base': '#4a3b8f', 'suelo': '#2c2650', 'techo': '#181440', 'pared': '#3b2f75',
                'acento': '#35f0ff', 'rival': '#6a5acd'},
    'espacio': {'base': '#24344d', 'suelo': '#16233a', 'techo': '#0c1524', 'pared': '#2c405e',
                'acento': '#4fd8ff', 'rival': '#8fa8c8'},
    'selva':   {'base': '#2f6b3a', 'suelo': '#1e4a28', 'techo': '#123018', 'pared': '#3a7d46',
                'acento': '#a2e85a', 'rival': '#4a8f56'},
    'ciudad':  {'base': '#4a4f5e', 'suelo': '#2e3240', 'techo': '#1c1f2a', 'pared': '#585e70',
                'acento': '#ffd740', 'rival': '#8a90a5'},
    'hielo':   {'base': '#7fb8d8', 'suelo': '#5a94b8', 'techo': '#3d6e8f', 'pared': '#a3d2ea',
                'acento': '#ffffff', 'rival': '#bcdff0'},
}
ESTADOS_RIVAL = ['idle', 'duelo', 'derrotado', 'triunfante']


def pregunta(txt, defecto, semilla=None, clave=None):
    if semilla is not None and clave and clave in semilla:
        return semilla[clave]
    try:
        r = input(f'{txt} [{defecto}]: ').strip()
        return r or defecto
    except EOFError:
        print('\n✗ entrada cerrada sin respuesta (usa --semilla para modo automático)')
        sys.exit(1)


def dibuja_provisional(ruta, w, h, color, texto, alfa=True):
    """PNG/JPG provisional legible (el artista lo reemplaza luego)."""
    from PIL import Image, ImageDraw
    img = Image.new('RGBA' if alfa else 'RGB', (w, h), (*_hex(color), 0 if alfa else 255))
    d = ImageDraw.Draw(img)
    if alfa:
        d.rounded_rectangle((8, 8, w - 8, h - 8), radius=24,
                            fill=(*_hex(color), 210))
    else:
        d.rectangle((0, 0, w, h), fill=_hex(color))
    try:
        d.text((w // 2, h // 2 - 10), texto, fill=(255, 255, 255),
               anchor='mm')
        d.text((w // 2, h // 2 + 26), 'PROVISIONAL — reemplazar',
               fill=(255, 255, 255), anchor='mm')
    except Exception:
        pass
    ruta.parent.mkdir(parents=True, exist_ok=True)
    img.save(ruta)


def _hex(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def genera_bso(ruta, tema, segundos=8):
    """BSO provisional: pad suave en Lá menor con un brillo por tema (wav)."""
    sr = 22050
    n = sr * segundos
    acordes = [(110.0, 164.81, 220.0), (98.0, 146.83, 196.0),
               (87.31, 130.81, 174.61), (98.0, 146.83, 196.0)]
    brillo = {'espacio': 880.0, 'magia': 659.25, 'circo': 523.25,
              'oeste': 392.0, 'selva': 440.0, 'ciudad': 493.88, 'hielo': 783.99}
    tono = brillo.get(tema, 440.0)
    muestras = bytearray()
    for i in range(n):
        t = i / sr
        ac = acordes[int(t / 2) % len(acordes)]
        env = min(1, t / 0.5, max(0.0, (segundos - t) / 0.5))
        v = 0.0
        for j, f in enumerate(ac):
            v += math.sin(2 * math.pi * f * t) * (0.16 - j * 0.04)
        v += math.sin(2 * math.pi * tono * t) * 0.02 * (0.5 + 0.5 * math.sin(2 * math.pi * 0.5 * t))
        muestras += struct.pack('<h', int(max(-1, min(1, v * env)) * 20000))
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(ruta), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(bytes(muestras))


def fases(semilla, plantilla):
    print('════════ ASISTENTE DE CAMPEONATOS · CRAZY PING PONG ════════')
    base = {}
    if plantilla:
        pm = CHAMPS / plantilla / 'manifest.json'
        if pm.is_file():
            pv = json.loads(pm.read_text(encoding='utf-8'))
            base = {'titulo': pv.get('title'), 'tema': plantilla,
                    'dificultad': 0.9}
            print(f'· valores base de «{plantilla}» (su carpeta NO se toca)')

    def preg(t, d, k):
        if semilla and k in semilla:
            return semilla[k]
        if base and k in base and k not in ():
            return base[k]
        return pregunta(t, d, semilla, k)

    # ── FASE 1 · FICHA ────────────────────────────────────────────────
    print('\n— FASE 1 · FICHA DEL CAMPEONATO')
    while True:
        cid = preg('  id (minúsculas, sin espacios)', '', 'id')
        if not cid:
            cid = pregunta('  id (minúsculas, sin espacios)', 'nuevo_champ')
        cid = cid.strip().lower().replace(' ', '_')
        if not (2 <= len(cid) <= 24):
            print('  ✗ el id debe medir 2-24 caracteres'); continue
        if not all(ch.islower() or ch.isdigit() or ch in '_-' for ch in cid):
            print('  ✗ sólo minúsculas, dígitos, _ y -'); continue
        if (CHAMPS / cid).exists():
            print(f'  ✗ ya existe championships/{cid} — NO se sobrescribe'); continue
        break
    titulo_es = preg('  título (ES)', cid.replace('_', ' ').title(), 'titulo_es')
    titulo_en = (semilla or {}).get('titulo_en', titulo_es)
    if semilla and 'descripcion_es' in semilla:
        desc_es = semilla['descripcion_es']
    else:
        desc_es = pregunta('  descripción (ES)', f'Duelo temático del campeonato {titulo_es}.')
    desc_en = (semilla or {}).get('descripcion_en', desc_es)
    tema = preg('  tema ' + '/'.join(TEMAS), 'espacio', 'tema')
    tema = tema if tema in TEMAS else 'espacio'
    dific = float(preg('  dificultad de la IA (0,6 fácil … 1,3 brutal)',
                       '0.9', 'dificultad') or 0.9)

    # ── FASE 2 · RIVAL ────────────────────────────────────────────────
    print('\n— FASE 2 · RIVAL')
    rival = dict((semilla or {}).get('rival') or {})
    if 'nombre' in rival:
        rival_nombre = rival['nombre']
    else:
        rival_nombre = pregunta('  nombre del rival', 'El Retador')
    rival_estados = rival.get('estados') or ESTADOS_RIVAL
    print(f'  · estados provisionales: {", ".join(rival_estados)}')

    # ── FASE 3 · SUPERPODERES ─────────────────────────────────────────
    print('\n— FASE 3 · SUPERPODERES')
    poderes = (semilla or {}).get('poderes')
    if poderes is None:
        try:
            n = int(preg('  ¿cuántos poderes quieres definir?', '1') or 1)
        except ValueError:
            n = 1
        poderes = []
        for i in range(n):
            kind = pregunta(f'  poder {i + 1} — kind (confeti|custom)', 'confeti')
            nombre = pregunta(f'  poder {i + 1} — nombre', 'Lluvia de confeti')
            try:
                chance = float(preg(f'  poder {i + 1} — probabilidad (0-1)', '0.3') or 0.3)
            except ValueError:
                chance = 0.3
            poderes.append({'kind': kind, 'name': nombre, 'chance': chance,
                            'cooldown': 25, 'duration': 8})
    for p in poderes:
        if p.get('kind') not in ('confeti', 'custom'):
            print(f"  · aviso: «{p.get('kind')}» requiere módulo propio — se documenta "
                  'en el manifest pero el stock no lo ejecuta')
    poderes = [{'kind': p.get('kind', 'confeti'), 'name': p.get('name', 'Poder'),
                'chance': float(p.get('chance', 0.3)),
                'cooldown': float(p.get('cooldown', 25)),
                'duration': float(p.get('duration', 8))}
               for p in poderes] or [{'kind': 'confeti', 'name': 'Lluvia de confeti',
                                      'chance': 0.3, 'cooldown': 25, 'duration': 8}]

    # ── FASE 4 · MATERIALES (inventario + provisionales) ──────────────
    print('\n— FASE 4 · MATERIALES PROVISIONALES (el artista los reemplaza)')
    paleta = TEMAS[tema]
    carpeta = CHAMPS / cid
    assets = carpeta / 'assets'
    (assets / 'decor').mkdir(parents=True, exist_ok=True)

    # rival + estados
    dibuja_provisional(assets / 'rival.webp', 512, 1024, paleta['rival'],
                       rival_nombre.upper())
    for est in rival_estados:
        dibuja_provisional(assets / f'{est}.webp', 512, 1024, paleta['rival'],
                           f'{rival_nombre.upper()}\n{est.upper()}')
    # BSO provisional (wav procedural)
    genera_bso(assets / 'bso.wav', tema)
    # sala provisional (6 planos)
    sala = {}
    for pieza, etiqueta, col in (('floor', 'SUELO', paleta['suelo']),
                                 ('ceil', 'TECHO', paleta['techo']),
                                 ('back', 'PARED FONDO', paleta['pared']),
                                 ('front', 'PARED FRENTE', paleta['base']),
                                 ('left', 'PARED IZQ', paleta['pared']),
                                 ('right', 'PARED DER', paleta['pared'])):
        f = assets / f'sala_{pieza}.jpg'
        dibuja_provisional(f, 1024, 1024, col, f'{etiqueta} · {titulo_es.upper()}',
                           alfa=False)
        sala[pieza] = f'assets/sala_{pieza}.jpg'
    # troquel decor provisional
    decor_seed = (semilla or {}).get('decor') or [
        {'file': 'assets/decor/troquel1.png', 'h': 1.2, 'x': -2.30, 'z': -2.75, 'sway': 0.5}]
    for i, pza in enumerate(decor_seed):
        f = carpeta / pza['file']
        dibuja_provisional(f, 512, 640, paleta['acento'], f'TROQUEL {i + 1}')
    # iconos de poder
    for p in poderes:
        dibuja_provisional(assets / f'power{p["kind"]}.png', 256, 256,
                           paleta['acento'], p['name'].upper())
    print(f'  ✓ provisionales en {carpeta.relative_to(RAIZ)}')

    # ── FASE 5 · PRUEBAS ──────────────────────────────────────────────
    print('\n— FASE 5 · PRUEBAS')
    print('  · stock: DUELO del núcleo a 11 con dificultad propia (ronda +8%)')
    n_duelos = int((semilla or {}).get('duelos', 3) or 3)
    etapas = [{'id': f'duelo{i}', 'name': f'Duelo {i}', 'kind': 'duelo'}
              for i in range(1, max(1, n_duelos) + 1)]

    # ── FASE 6 · SALA ─────────────────────────────────────────────────
    print('\n— FASE 6 · SALA')
    print('  · decorado de 6 planos provisional + troqueles decor')

    # ── FASE 7 · MONTAJE ─────────────────────────────────────────────
    print('\n— FASE 7 · MONTAJE (manifest + módulo + índice + validación)')
    pref = f'pp_champ_{cid}_'
    manifest = {
        'id': cid,
        'version': 1,
        'contract': 1,
        'estado': 'borrador',
        'title': {'es': titulo_es, 'en': titulo_en},
        'description': {'es': desc_es, 'en': desc_en},
        'rival': {'id': f'{cid}_rival', 'name': rival_nombre, 'kind': 'stock',
                  'states': rival_estados, 'oppLabel': 'rival'},
        'storage': f'pp_champ_{cid}_*',
        'assets': f'manifiesto provisional: rival.webp, estados {rival_estados}, '
                  f'bso.wav, sala_*.jpg, decor/, power*.png (ver LEEME-ASSETS.txt)',
        'audio': {'music': 'assets/bso.wav', 'musicVolume': 0.18},
        'powers': poderes,
        'stages': etapas,
        'decor': {'pieces': decor_seed},
        'room': sala,
        'rewards': {'wins': pref + 'wins', 'champion': pref + 'champion'},
        'trophy': {'name': {'es': f'Copa {titulo_es}', 'en': f'{titulo_en} Cup'}},
        'duelo': {'aiMul': dific},
        'tema': tema,
        'notes': [f'{time.strftime("%Y-%m-%d")}: creado con crear_campeonato.py '
                  f'(plantilla stock, tema {tema})'],
    }
    (carpeta / 'manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

    # index.js desde la plantilla
    tpl = (PLAT / 'plantilla_index.js').read_text(encoding='utf-8')
    js = (tpl
          .replace('@ID@', cid)
          .replace('@TITULO_ES@', titulo_es)
          .replace('@TITULO_EN@', titulo_en)
          .replace('@RIVAL_NOMBRE@', rival_nombre.replace("'", "\\'"))
          .replace('@DIFICULTAD@', str(dific))
          .replace('@PUNTOS@', '11')
          .replace('@COLOR@', paleta['acento'])
          .replace('@STORAGE@', f'pp_champ_{cid}_')
          .replace('@PODERES_JSON@', json.dumps(poderes, ensure_ascii=False))
          .replace('@DECOR_JSON@', json.dumps({'pieces': decor_seed}, ensure_ascii=False))
          .replace('@ROOM_JSON@', json.dumps(sala, ensure_ascii=False)))
    (carpeta / 'index.js').write_text(js, encoding='utf-8')

    # LEEME de materiales
    leeme = f"""MATERIALES DE «{titulo_es}» ({cid}) — qué reemplazar y con qué
================================================================
Todo lo provisional es FUNCIONAL: puedes jugar hoy y cambiar el arte luego.

ASSETS/ (reemplaza y conserva el NOMBRE del fichero):
  rival.webp            rival de pie · 512×1024 PNG/WebP con ALFA real
  {'; '.join(f'{e}.webp' for e in rival_estados)}   estados del rival · 512×1024 con alfa
  bso.wav               BSO en bucle → sustituir por bso.mp3 (y actualiza
                        audio.music del manifest)
  sala_floor/ceil/back/front/left/right.jpg   sala 1024×1024 (6 planos)
  decor/troquel*.png    troqueles de cartón · PNG CON CANAL ALFA REAL
                        (esquinas transparentes; el recorte es el alfa)
  power*.png            iconos de superpoder · 256×256 con alfa

REGLAS DE ORO (scripts/plataforma/AUDITORIA.md):
  · las esquinas de los PNG recortados deben ser TRANSPARENTES (alfa<30)
  · verifica con: python3 scripts/plataforma/valida_activos.py championships/{cid}
  · el campo room/decor del manifest debe seguir apuntando a assets/...

PUBLICAR:
  1) cambia "estado": "borrador" → "publicado" en manifest.json
  2) python3 scripts/plataforma/genera_indice.py
  3) python3 scripts/plataforma/valida_manifiesto.py championships/{cid}/manifest.json
PREVISUALIZAR sin publicar: abre el juego con ?champ={cid}
"""
    (carpeta / 'LEEME-ASSETS.txt').write_text(leeme, encoding='utf-8')

    # índice + validación (con timeout: nunca colgar el asistente)
    def pasa(script, *args, cwd=None):
        try:
            r = subprocess.run([sys.executable, str(PLAT / script), *args],
                               cwd=cwd, timeout=60, capture_output=True, text=True)
            salida = (r.stdout or '').strip().splitlines()
            for l in salida[-3:]:
                print('    ·', l)
            if r.returncode != 0:
                for l in (r.stderr or '').strip().splitlines()[-3:]:
                    print('    !', l)
            return r.returncode == 0
        except subprocess.TimeoutExpired:
            print(f'    ✗ {script} no terminó en 60 s')
            return False

    print('\n· generando índice…')
    ok1 = pasa('genera_indice.py')
    print('· validando manifiesto…')
    ok2 = pasa('valida_manifiesto.py', str(carpeta / 'manifest.json'))
    print('· validando activos…')
    ok3 = pasa('valida_activos.py', f'championships/{cid}', cwd=str(PUB))
    ok = ok1 and ok2 and ok3
    print('\n════════ RESUMEN ════════')
    print(f'  campeonato: {carpeta.relative_to(RAIZ)}  (estado: borrador)')
    print(f'  jugable YA en borrador: abre el juego con  ?champ={cid}')
    print(f'  validación: {"✓ OK" if ok else "✗ revisar"}')
    return ok


def main():
    semilla = None
    plantilla = None
    argv = sys.argv[1:]
    if '--semilla' in argv:
        semilla = json.loads((RAIZ / argv[argv.index('--semilla') + 1])
                             .read_text(encoding='utf-8'))
    if '--plantilla' in argv:
        plantilla = argv[argv.index('--plantilla') + 1]
    ok = fases(semilla, plantilla)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
