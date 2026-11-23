#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C2 (auditoría r120 · ola 3) · externaliza los recursos base64 del artefacto.

Los GLB / OGG / MP3 / PNG / WebP / JPEG embebidos en las fuentes del juego
salen a public/assets/externos/ (y assets/audio/ para los bancos de voz).
El HTML pasa de 12,5 MB a ~3 MB; los ZIP siguen autocontenidos (build_zip.py
ya copia public/assets) y el SW cachea /assets/ con cacheFirst.

Por diseño: se ejecuta UNA vez (aborta si un asset ya existe) y cada
sustitución exige su ancla EXACTA una vez — si algo no cuadra, aborta sin
escribir nada a medias. Los pequeños SFX r62 (58 KB) y el vendor PeerJS
SE QUEDAN embebidos a propósito.
"""
import base64
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
SRC = RAIZ / 'src/game'
EXT = RAIZ / 'public/assets/externos'
AUD = RAIZ / 'public/assets/audio'

informe = []


def leer(rel):
    return (SRC / rel).read_text(encoding='utf-8')


def escribir(rel, txt):
    (SRC / rel).write_text(txt, encoding='utf-8', newline='\n')


def asset(nombre, datos, carpeta=EXT):
    carpeta.mkdir(parents=True, exist_ok=True)
    p = carpeta / nombre
    if p.exists():
        raise SystemExit(f'ABORTA: {p} ya existe (ejecución no idempotente por diseño)')
    p.write_bytes(datos)
    return p.stat().st_size


def b64bin(b64):
    return base64.b64decode(b64 + '=' * (-len(b64) % 4))


def uri_datos(uri):
    m = re.fullmatch(r'data:([\w/+.-]+);base64,([A-Za-z0-9+/=]+)', uri)
    if not m:
        raise SystemExit('ABORTA: data URI malformado')
    return m.group(1), b64bin(m.group(2))


def ext_de(mime):
    return {'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp',
            'audio/mpeg': 'mp3', 'audio/ogg': 'ogg', 'audio/wav': 'wav'}[mime]


def sustituir_una(txt, viejo, nuevo, etiqueta):
    n = txt.count(viejo)
    if n != 1:
        raise SystemExit(f'ABORTA [{etiqueta}]: ancla aparece {n} veces (esperaba 1)')
    informe.append(f'  · {etiqueta}')
    return txt.replace(viejo, nuevo, 1)


# ---------------------------------------------------------------- c01 (pala + pistola)
def c01():
    rel = 'core/c01_modelos_3d.js'
    txt = leer(rel)
    lineas = txt.split('\n')

    # PALA_GLB_B64: se elimina SIN escribir asset — public/assets/pala/pala.glb
    # ya existe (1.411.384 B) y es el mismo GLB (1.881.872 B b64 ≈ mismo binario).
    i_pala = [i for i, l in enumerate(lineas) if l.startswith("const PALA_GLB_B64 = '")]
    if len(i_pala) != 1:
        raise SystemExit(f'ABORTA c01: PALA_GLB_B64 encontrada {len(i_pala)} veces')
    b64_pala = lineas[i_pala[0]][len("const PALA_GLB_B64 = '"):-2]
    bin_pala = b64bin(b64_pala)
    pala_ext = RAIZ / 'public/assets/pala/pala.glb'
    if not pala_ext.exists():
        raise SystemExit('ABORTA c01: no existe public/assets/pala/pala.glb')
    if abs(pala_ext.stat().st_size - len(bin_pala)) > 64:
        raise SystemExit(f'ABORTA c01: pala externa {pala_ext.stat().st_size} B != embebida {len(bin_pala)} B')
    informe.append(f'  · c01 PALA_GLB_B64 eliminada ({len(bin_pala)} B — ya vive en assets/pala/pala.glb)')
    lineas[i_pala[0]] = ''

    # GUN_GLB_B64 → assets/externos/gun.glb
    i_gun = [i for i, l in enumerate(lineas) if l.startswith("const GUN_GLB_B64 = '")]
    if len(i_gun) != 1:
        raise SystemExit(f'ABORTA c01: GUN_GLB_B64 encontrada {len(i_gun)} veces')
    b64_gun = lineas[i_gun[0]][len("const GUN_GLB_B64 = '"):-2]
    t = asset('gun.glb', b64bin(b64_gun))
    informe.append(f'  · c01 GUN_GLB_B64 → assets/externos/gun.glb ({t} B)')
    lineas[i_gun[0]] = ''
    txt = '\n'.join(lineas)

    # docstring de loadPaddleModel
    txt = sustituir_una(txt, """/** v3.0.3 · Carga el GLB de la pala: PRIMERO el modelo EXTERNO
 *  assets/pala/pala.glb — la pala ya no vive SOLO dentro del código:
 *  sustituir ese archivo cambia la pala de todo el juego sin tocar nada
 *  (pedido del dueño para crecer por assets). Si falla (apertura local
 *  file://, archivo ausente, caché vieja) se usa el GLB incrustado de
 *  siempre. Devuelve el modelo o null (fallback procedural). */""",
"""/** v3.0.3 · Carga el GLB de la pala desde assets/pala/pala.glb — la pala
 *  no vive dentro del código: sustituir ese archivo cambia la pala de todo
 *  el juego sin tocar nada (pedido del dueño para crecer por assets).
 *  C2 (r129 · ola 3): ya NO hay copia base64 en el HTML — si el GLB falta,
 *  resuelve null y makePaddleVisual dibuja la pala procedural. */""", 'c01 docstring loadPaddleModel')

    # cuerpo de loadPaddleModel: fuera el fallback embebido
    txt = sustituir_una(txt, """export function loadPaddleModel() {
  return new Promise((resolve) => {
    const loader = new GLTFLoader();
    const fromEmbedded = () => {
      try {
        loader.parse(decodeB64(PALA_GLB_B64), '', (gltf) => {
          resolve(hardenPaddle(gltf.scene));
        }, (err) => {
          console.error('No se pudo cargar el GLB de la pala:', err);
          resolve(null);
        });
      } catch (e) {
        console.error('Error decodificando el GLB:', e);
        resolve(null);
      }
    };
    fetch('assets/pala/pala.glb')
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((buf) => new Promise((res, rej) => loader.parse(buf, '', (g) => res(g), rej)))
      .then((gltf) => {
        console.info('Pala: modelo EXTERNO assets/pala/pala.glb cargado');
        resolve(hardenPaddle(gltf.scene));
      })
      .catch(() => fromEmbedded());
  });
}""",
"""export function loadPaddleModel() {
  return new Promise((resolve) => {
    const loader = new GLTFLoader();
    fetch('assets/pala/pala.glb')
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((buf) => new Promise((res, rej) => loader.parse(buf, '', (g) => res(g), rej)))
      .then((gltf) => {
        console.info('Pala: modelo EXTERNO assets/pala/pala.glb cargado');
        resolve(hardenPaddle(gltf.scene));
      })
      .catch(() => {
        console.warn('Pala: GLB externo no disponible — pala procedural');
        resolve(null);
      });
  });
}""", 'c01 loadPaddleModel')

    # loadGunModel: fetch en vez de base64
    txt = sustituir_una(txt, """export function loadGunModel() {
  return new Promise((resolve) => {
    if (!GUN_GLB_B64 || GUN_GLB_B64.indexOf('__') === 0) return resolve(null);
    try {
      const loader = new GLTFLoader();
      loader.parse(decodeB64(GUN_GLB_B64), '', (gltf) => {""",
"""export function loadGunModel() {
  return new Promise((resolve) => {
    // C2 (r129): el GLB vive en assets/externos/gun.glb (antes base64).
    // Sin GLB o si falla: null → pistola procedural de makeGunVisual.
    const loader = new GLTFLoader();
    fetch('assets/externos/gun.glb')
      .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
      .then((buf) => {
        loader.parse(buf, '', (gltf) => {""", 'c01 loadGunModel cabecera')

    txt = sustituir_una(txt, """        resolve(model);
      }, () => resolve(null));
    } catch { resolve(null); }
  });
}""",
"""          resolve(model);
        }, () => resolve(null));
      })
      .catch(() => resolve(null));
  });
}""", 'c01 loadGunModel cola')

    # decodeB64 puede quedar sin uso — comprobar
    usos = len(re.findall(r'decodeB64\(', txt)) - 1  # -1 por la definición
    if usos == 0:
        txt = sustituir_una(txt, """function decodeB64(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer;
}

""", '', 'c01 decodeB64 sin usos → fuera')
        informe.append('  · c01 decodeB64 eliminado (sin usos)')
    escribir(rel, txt)


# ---------------------------------------------------------------- c00 (bancos de voz)
def c00():
    rel = 'core/c00_pre_three.js'
    txt = leer(rel)
    lineas = txt.split('\n')
    i_es = [i for i, l in enumerate(lineas) if l.startswith('export const VOICE_B64 = {')]
    i_en = [i for i, l in enumerate(lineas) if l.startswith('export const VOICE_B64_EN = {')]
    if len(i_es) != 1 or len(i_en) != 1 or i_en[0] < i_es[0]:
        raise SystemExit(f'ABORTA c00: bloques VOICE mal localizados ({len(i_es)}/{len(i_en)})')
    # cierre del bloque EN: primera línea exacta '};' tras i_en
    j_en = next(j for j in range(i_en[0], len(lineas)) if lineas[j] == '};')
    j_es = next(j for j in range(i_es[0], i_en[0]) if lineas[j] == '};')

    def parsear(ini, fin):
        banco = {}
        for l in lineas[ini + 1:fin]:
            m = re.fullmatch(r'\s*([A-Za-z0-9_]+):\s*["\']([A-Za-z0-9+/=]{100,})["\'],?\s*', l)
            if m:
                banco[m.group(1)] = m.group(2)
        return banco

    banco_es = parsear(i_es[0], j_es)
    banco_en = parsear(i_en[0], j_en)
    if not banco_es or not banco_en:
        raise SystemExit('ABORTA c00: bancos de voz vacíos')
    ok_es = len(banco_es)
    t_es = asset('voz_es.json', __import__('json').dumps(banco_es, ensure_ascii=True).encode(), AUD)
    t_en = asset('voz_en.json', __import__('json').dumps(banco_en, ensure_ascii=True).encode(), AUD)
    informe.append(f'  · c00 VOICE_B64 ({ok_es} clips) → assets/audio/voz_es.json ({t_es} B)')
    informe.append(f'  · c00 VOICE_B64_EN ({len(banco_en)} clips) → assets/audio/voz_en.json ({t_en} B)')

    nuevo = """/* C2 (r129 · ola 3) · banco de voz EXTERNO: los clips OGG Opus ya no
 * viajan dentro del HTML (~2 MB de base64 fuera). Se descargan de
 * assets/audio/voz_*.json (el SW los cachea con cacheFirst y los ZIP los
 * llevan). Si la descarga falla (file://, red) el juego sigue — sin
 * megafonía. Al aterrizar el banco se emite 'pp-voz-lista' y GameAudio
 * recarga en caliente (reloadVoice). Regenerar: gen_voice.py + build_voice.py */
export let VOICE_B64 = null;
export let VOICE_B64_EN = null;
(() => {
  const aplicar = (lang, json) => {
    if (lang === 'es') VOICE_B64 = json; else VOICE_B64_EN = json;
    try { window.dispatchEvent(new Event('pp-voz-lista')); } catch (e) { /* */ }
  };
  const cargar = (url, lang) => fetch(url)
    .then((r) => (r.ok ? r.json() : Promise.reject(new Error('HTTP ' + r.status))))
    .then((j) => aplicar(lang, j))
    .catch(() => { /* sin banco: megafonía en silencio, el juego sigue */ });
  cargar('assets/audio/voz_es.json', 'es');
  cargar('assets/audio/voz_en.json', 'en');
})();"""
    lineas[i_es[0]:j_en + 1] = nuevo.split('\n')
    escribir(rel, '\n'.join(lineas))


# ---------------------------------------------------------------- c03 (recarga de voz)
def c03():
    rel = 'core/c03_audio_voz.js'
    txt = leer(rel)
    txt = sustituir_una(txt, """export class GameAudio {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;""",
"""export class GameAudio {
  constructor() {
    this.ctx = null;
    this.master = null;
    this.noiseBuffer = null;
    // C2 (r129): el banco de voz llega EXTERNO (assets/audio/voz_*.json);
    // cuando aterrice, recarga en caliente la megafonía.
    try { window.addEventListener('pp-voz-lista', () => this.reloadVoice()); } catch (e) { /* */ }""",
        'c03 listener pp-voz-lista')
    escribir(rel, txt)


# ---------------------------------------------------------------- c13 (tutorial: mandos + pizarra)
def c13():
    rel = 'core/c13_ui_arranque.js'
    txt = leer(rel)
    lineas = txt.split('\n')

    for nombre_const, url, archivo in (
            ('TUT_MANDO_GLB', 'assets/externos/mando_izq.glb', 'mando_izq.glb'),
            ('TUT_MANDO_DER_GLB', 'assets/externos/mando_der.glb', 'mando_der.glb'),
            ('TUT_PIZARRA', 'assets/externos/pizarra.webp', 'pizarra.webp')):
        prefijo = f'const {nombre_const} = '
        idx = [i for i, l in enumerate(lineas) if l.lstrip().startswith(prefijo)]
        if len(idx) != 1:
            raise SystemExit(f'ABORTA c13: {nombre_const} {len(idx)} veces')
        m = re.fullmatch(r"(\s*)const (\w+) = '([^']+)';\s*", lineas[idx[0]])
        if not m:
            raise SystemExit(f'ABORTA c13: línea de {nombre_const} no casa')
        sangria, valor = m.group(1), m.group(3)
        if nombre_const == 'TUT_PIZARRA':
            _, binario = uri_datos('data:image/webp;base64,' + valor)
        else:
            binario = b64bin(valor)
        t = asset(archivo, binario)
        informe.append(f'  · c13 {nombre_const} → {url} ({t} B)')
        lineas[idx[0]] = f"{sangria}const {nombre_const} = '{url}';   // C2 (r129): antes base64 embebido"
    txt = '\n'.join(lineas)

    txt = sustituir_una(txt, "  /* ---- ASSETS r65 · mando GLB del dueño + pizarra (base64, embebidos) */",
                        "  /* ---- ASSETS r65 · mando GLB del dueño + pizarra (ficheros externos, C2 r129) */",
                        'c13 comentario assets')

    txt = sustituir_una(txt, "      im.src = 'data:image/webp;base64,' + TUT_PIZARRA;",
                        "      im.src = TUT_PIZARRA;", 'c13 pizarra consumer')

    # decode del tutorial (c13:4770-4790)
    txt = sustituir_una(txt, """        const bin = Uint8Array.from(atob(def.bin), (ch) => ch.charCodeAt(0));
        new GLTFLoader().parse(bin.buffer, '', (gltf) => {
          if (!anclados || anclados.indexOf(reg) < 0) return;
          const m = _montaMando(gltf, def.anclas, texHalo);
          mont.add(m.glb);
          reg.glb = m.glb; reg.halos = m.halos; reg.esc = m.esc;
          if (h === (G ? G.paddleHand : 1)) {
            mando = m.glb;                    // compat QA: mando de la pala
            mandoSpin = m.glb;
          }
          _recolocaEtiqueta();
        }, () => { /* sin GLB: el panel funciona igual */ });""",
"""        fetch(def.bin)
          .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
          .then((buf) => {
            new GLTFLoader().parse(buf, '', (gltf) => {
              if (!anclados || anclados.indexOf(reg) < 0) return;
              const m = _montaMando(gltf, def.anclas, texHalo);
              mont.add(m.glb);
              reg.glb = m.glb; reg.halos = m.halos; reg.esc = m.esc;
              if (h === (G ? G.paddleHand : 1)) {
                mando = m.glb;                    // compat QA: mando de la pala
                mandoSpin = m.glb;
              }
              _recolocaEtiqueta();
            }, () => { /* sin GLB: el panel funciona igual */ });
          })
          .catch(() => { /* sin GLB: el panel funciona igual */ });""", 'c13 tutorial decode async')

    escribir(rel, txt)


# ---------------------------------------------------------------- c12 (réplica ajuste + poderes)
def c12():
    rel = 'core/c12_pingponggame.js'
    txt = leer(rel)

    txt = sustituir_una(txt, """        const bin = Uint8Array.from(atob(this.handOf[h] === 'left' ? GLBS.izq : GLBS.der), (ch) => ch.charCodeAt(0));
        new GLTFLoader().parse(bin.buffer, '', (gltf) => {
          try {
            const modelo = gltf.scene;
            const box = new THREE.Box3().setFromObject(modelo);
            const cen = box.getCenter(new THREE.Vector3());
            const tam = box.getSize(new THREE.Vector3());
            const esc = 0.154 / Math.max(tam.x, tam.y, tam.z, 0.01);   // r67: 75 %
            modelo.position.sub(cen);
            modelo.scale.setScalar(esc);
            const glb = new THREE.Group();
            glb.rotation.y = Math.PI;   // la cara del GLB mira a -Z (mando real)
            glb.add(modelo);
            mont.add(glb);
            mont.visible = !!this.calibPala;   // si ya salimos, no resucita
          } catch (eM) { /* decorativo */ }
        }, () => { /* sin GLB: sin réplica, el ajuste funciona igual */ });""",
"""        const urlGlb = this.handOf[h] === 'left' ? GLBS.izq : GLBS.der;
        fetch(urlGlb)
          .then((r) => (r.ok ? r.arrayBuffer() : Promise.reject(new Error('HTTP ' + r.status))))
          .then((buf) => {
            new GLTFLoader().parse(buf, '', (gltf) => {
              try {
                const modelo = gltf.scene;
                const box = new THREE.Box3().setFromObject(modelo);
                const cen = box.getCenter(new THREE.Vector3());
                const tam = box.getSize(new THREE.Vector3());
                const esc = 0.154 / Math.max(tam.x, tam.y, tam.z, 0.01);   // r67: 75 %
                modelo.position.sub(cen);
                modelo.scale.setScalar(esc);
                const glb = new THREE.Group();
                glb.rotation.y = Math.PI;   // la cara del GLB mira a -Z (mando real)
                glb.add(modelo);
                mont.add(glb);
                mont.visible = !!this.calibPala;   // si ya salimos, no resucita
              } catch (eM) { /* decorativo */ }
            }, () => { /* sin GLB: sin réplica, el ajuste funciona igual */ });
          })
          .catch(() => { /* sin GLB: sin réplica, el ajuste funciona igual */ });""", 'c12 réplica ajuste async')

    # TODAS las data-URIs grandes del fichero → assets/externos/poder_<n>.<ext>
    # (63 URIs: PNG_PODER_*, VOZ_PODER_*, AUDIO_TRUENO_A/B, VOZ_SEL_*, …)
    patron = re.compile(r"'(data:([\w/+.-]+);base64,([A-Za-z0-9+/=]{1000,}))'")
    contador = {'n': 0}

    def repl(m):
        contador['n'] += 1
        mime, datos = m.group(2), b64bin(m.group(3))
        nombre = f'poder_{contador["n"]:02d}.{ext_de(mime)}'
        t = asset(nombre, datos)
        informe.append(f'  · c12 URI #{contador["n"]} → assets/externos/{nombre} ({t} B)')
        return f"'assets/externos/{nombre}'"

    txt = patron.sub(repl, txt)
    if contador['n'] < 50:
        raise SystemExit(f'ABORTA c12: solo {contador["n"]} URIs (esperaba ~63)')
    escribir(rel, txt)


# ---------------------------------------------------------------- c02 (iconos de menús)
def c02():
    rel = 'core/c02_cfg_escena.js'
    txt = leer(rel)
    patron = re.compile(r"(\w+):\s*\{\s*src:\s*'(data:image/png;base64,([A-Za-z0-9+/=]{1000,}))'")

    hechos = {'n': 0}

    def repl(m):
        hechos['n'] += 1
        t = asset(f'icono_{m.group(1)}.png', b64bin(m.group(3)))
        informe.append(f'  · c02 icono {m.group(1)} → assets/externos/icono_{m.group(1)}.png ({t} B)')
        return f"{m.group(1)}: {{ src: 'assets/externos/icono_{m.group(1)}.png'"

    txt = patron.sub(repl, txt)
    if hechos['n'] != 24:
        raise SystemExit(f'ABORTA c02: {hechos["n"]} iconos (esperaba 24)')
    escribir(rel, txt)


# ---------------------------------------------------------------- c08 (carteles fanfarria)
def c08():
    rel = 'core/c08_hall_hud.js'
    txt = leer(rel)
    patron = re.compile(r"'(data:([\w/+.-]+);base64,([A-Za-z0-9+/=]{1000,}))'")
    orden = [('es', 'win'), ('es', 'lose'), ('en', 'win'), ('en', 'lose')]

    idx = {'n': 0}

    def repl(m):
        lang, clave = orden[idx['n']] if idx['n'] < len(orden) else ('x', str(idx['n']))
        idx['n'] += 1
        nombre = f'poster_{lang}_{clave}.webp'
        t = asset(nombre, b64bin(m.group(3)))
        informe.append(f'  · c08 → assets/externos/{nombre} ({t} B)')
        return f"'assets/externos/{nombre}'"

    txt = patron.sub(repl, txt)
    if idx['n'] != 4:
        raise SystemExit(f'ABORTA c08: {idx["n"]} URIs (esperaba 4)')
    escribir(rel, txt)


# ---------------------------------------------------------------- c10 (logo del menú)
def c10():
    rel = 'core/c10_menu_saque.js'
    txt = leer(rel)
    m = re.search(r"(export const MENU_LOGO_SRC = ')(data:image/jpeg;base64,([A-Za-z0-9+/=]{1000,}))(')", txt)
    if not m:
        raise SystemExit('ABORTA c10: MENU_LOGO_SRC no encontrado')
    t = asset('logo_menu.jpg', b64bin(m.group(3)))
    txt = txt[:m.start()] + m.group(1) + 'assets/externos/logo_menu.jpg' + m.group(4) + txt[m.end():]
    informe.append(f'  · c10 MENU_LOGO_SRC → assets/externos/logo_menu.jpg ({t} B)')
    escribir(rel, txt)


# ---------------------------------------------------------------- 07_tail (música)
def c07tail():
    rel = '07_tail.html'
    txt = leer(rel)
    m = re.search(r"(window\.__PP_MUSIC_URL = ')(data:audio/ogg;base64,([A-Za-z0-9+/=]{1000,}))(')", txt)
    if not m:
        raise SystemExit('ABORTA tail: __PP_MUSIC_URL no encontrado')
    t = asset('musica.ogg', b64bin(m.group(3)))
    txt = txt[:m.start()] + m.group(1) + 'assets/externos/musica.ogg' + m.group(4) + txt[m.end():]
    informe.append(f'  · 07_tail música → assets/externos/musica.ogg ({t} B)')
    escribir(rel, txt)


# ---------------------------------------------------------------- portada (head CSS + body imgs)
def portada():
    # head: fondo difuminado
    txt = leer('00_head.html')
    m = re.search(r'(background-image: url\(")(data:image/jpeg;base64,([A-Za-z0-9+/=]{1000,}))("\))', txt)
    if not m:
        raise SystemExit('ABORTA head: bgblur no encontrado')
    datos_head = b64bin(m.group(3))
    t = asset('portada.jpg', datos_head)
    txt = txt[:m.start()] + m.group(1) + 'assets/externos/portada.jpg' + m.group(4) + txt[m.end():]
    informe.append(f'  · 00_head bgblur → assets/externos/portada.jpg ({t} B)')
    escribir('00_head.html', txt)

    # body: hero + botones
    txt = leer('03_body.html')
    m = re.search(r'(<img src=")(data:image/jpeg;base64,([A-Za-z0-9+/=]{1000,}))(")', txt)
    if not m:
        raise SystemExit('ABORTA body: hero no encontrado')
    if b64bin(m.group(3)) == datos_head:
        informe.append('  · 03_body hero = MISMA portada (reutiliza el fichero)')
        url_hero = 'assets/externos/portada.jpg'
    else:
        t2 = asset('portada_hero.jpg', b64bin(m.group(3)))
        informe.append(f'  · 03_body hero → assets/externos/portada_hero.jpg ({t2} B)')
        url_hero = 'assets/externos/portada_hero.jpg'
    txt = txt[:m.start()] + m.group(1) + url_hero + m.group(4) + txt[m.end():]

    nombres = {'padEs': 'pad_es.png', 'padEn': 'pad_en.png',
               'playEs': 'jugar_es.png', 'playEn': 'jugar_en.png'}
    for ident, nombre in nombres.items():
        m = re.search(r'(id="' + ident + r'" src=")(data:image/png;base64,([A-Za-z0-9+/=]{1000,}))(")', txt)
        if not m:
            raise SystemExit(f'ABORTA body: {ident} no encontrado')
        t = asset(nombre, b64bin(m.group(3)))
        txt = txt[:m.start()] + m.group(1) + f'assets/externos/{nombre}' + m.group(4) + txt[m.end():]
        informe.append(f'  · 03_body {ident} → assets/externos/{nombre} ({t} B)')
    escribir('03_body.html', txt)


def main():
    total = 0
    for paso in (c01, c00, c03, c13, c12, c02, c08, c10, c07tail, portada):
        informe.append(f'[{paso.__name__}]')
        paso()
    # barrido final: nada grande debe quedar fuera de c03 (SFX) y el vendor
    print('== INFORME C2 ==')
    print('\n'.join(informe))
    print('== VERIFICACIÓN ==')
    for f in sorted(SRC.glob('core/*.js')) + sorted(SRC.glob('*.html')):
        txt = f.read_text(encoding='utf-8', errors='replace')
        grandes = [len(l) for l in txt.split('\n') if len(l) > 5000]
        uris = len(re.findall(r'data:[\w/+.-]+;base64,[A-Za-z0-9+/=]{1000,}', txt))
        if grandes or uris:
            print(f'  {f.name}: {len(grandes)} líneas >5k ({sum(grandes)} B) · {uris} data-URIs grandes')
    print('(esperado: c03 SFX 5 líneas · 07_tail peerjs ~1-2 líneas; nada más)')


if __name__ == '__main__':
    main()
