#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FASE 7 · CIERRE DEL SDK v1.x — cirugía re-operable sobre orbital y valle:

  · ORBITAL: música → createMusic (adiós al ÚLTIMO decodeAudioData propio,
    el «arsenal» bso.wav), standee del ASTRO → createRival (motor «perezoso»,
    guard v3.2.1 + eco QA _rivalEstado), cartel de bienvenida → createCartel.
    Manifest v15 → v16.
  · VALLE NEÓN: standee → createRival (motor «precarga» + FIX: el arte real
    era .png — los .webp pedidos nunca existieron, silueta gris desde v1),
    cartel de sala → createCartel. Manifest v3 → v4.

Re-operable: si un bloque ya está migrado, lo detecta y no lo toca.
Todo reemplazo va asertado: si el ancla no está EXACTAMENTE donde toca, ABORTA.
"""
import json
import sys
from pathlib import Path

CH = Path('/home/z/my-project/public/championships')
SDK = CH / 'sdk' / 'champ_sdk.js'
FALLOS = []


def aborta(msg):
    FALLOS.append(msg)
    print('FALLO:', msg)


def splice(s, inicio, fin_marker, nuevo, etiqueta, incluir_fin=True):
    """Sustituye s[inicio:fin] donde fin es la PRIMERA aparición de
    fin_marker a partir de inicio. Devuelve el texto nuevo."""
    i = s.find(inicio)
    if i < 0:
        aborta(f'{etiqueta}: no encuentro el inicio {inicio[:60]!r}')
        return s
    j = s.find(fin_marker, i + len(inicio))
    if j < 0:
        aborta(f'{etiqueta}: no encuentro el fin {fin_marker[:60]!r}')
        return s
    if incluir_fin:
        j += len(fin_marker)
    return s[:i] + nuevo + s[j:]


def ya_migrado(s, sello):
    return sello in s


# ————————————————————————————————————————— ORBITAL —————————————————————————
def orbital():
    p = CH / 'estacion_orbital' / 'index.js'
    s = p.read_text(encoding='utf-8')
    orig = s
    SELLO = 'v3.6.5-SDK5 · FASE 7'
    if SELLO not in s:
        # R1 · import
        viejo = "import { createPowerSign, createSfx, congela } from '../sdk/champ_sdk.js';"
        nuevo = ("import { createCartel, createMusic, createPowerSign, createRival, "
                 "createSfx, congela } from '../sdk/champ_sdk.js';")
        if s.count(viejo) != 1:
            aborta('orbital R1: el import del SDK no está exactly una vez')
        else:
            s = s.replace(viejo, nuevo)

        # R2 · slots de música en el constructor
        viejo = ("    this._mus = null; this._musBuf = null; this._musBusy = false;\n"
                 "    this._musWanted = false; this._musRamp = 0;\n")
        nuevo = ("    // v3.6.5-SDK5 · FASE 7: la ranura de música vive DENTRO del SDK\n"
                 "    // (createMusic); los slots _mus/_musBuf/_musBusy/_musWanted/\n"
                 "    // _musRamp desaparecen con el motor que los llevaba.\n")
        if s.count(viejo) != 1:
            aborta('orbital R2: los slots de música no están una vez')
        else:
            s = s.replace(viejo, nuevo)

        # R3 · standee del ASTRO → createRival (perezoso)
        inicio = '    // RIVAL: standee del ASTRO (assets/rival.webp, arte del dueño)'
        fin = "    this.rivalEstado('idle');\n"
        nuevo = '''    // RIVAL: standee del ASTRO (assets/rival.webp, arte del dueño)
    // v3.5.1 · 3.ª CORRECCIÓN DE COLOCACIÓN (informe del dueño: «el rival
    // astro está metido en la pared… que se coloque como en el resto de
    // rivales, totalmente visible a una distancia fija de la mesa»): el
    // spot v3.4.1 (z −3,82) caía justo sobre la TRANSICIÓN pintada del arte
    // de la pared frontal — la sala dibuja su propia perspectiva y a esa
    // profundidad los pies del ASTRO se leían dentro del arranque del muro
    // (diagnóstico visual: download/diag_imp2/e1_rival.png). AHORA: más
    // CERCA de la mesa, claramente DENTRO de la sala — z = borde lejano de
    // la mesa − 0,33 (distancia fija, la misma referencia que los recortes
    // del suelo que se leen bien) · x = borde derecho + 0,50 (regla fija de
    // duelos). Cuerpo entero de 2,15 m, pies en el suelo y de cara.
    // Historia: v3.2.1 (x 1,62 · z −4,5) · v3.4.1 (x 1,26 · z −3,82).
    // v3.6.5-SDK5 · FASE 7: el STANDEE vive en el SDK (createRival, motor
    // «perezoso» del orbital: UNA textura viva + guard anti-recarga v3.2.1).
    this._rivalSDK = createRival(THREE, () => this.game, {
      modo: 'perezoso',
      base: 'rival.webp',
      alto: 2.15,                          // convención OESTE.spriteHeight
      alphaTest: 0.25,
      depthWrite: false,
      renderOrder: 6,
      pos: [1.26, 2.15 / 2, (D.tableCenterZ || -1.6) - 1.70],
      resuelve: (f) => this._A(f),
      onTex: (t) => this._ownTex.add(t),
      onEstado: (st) => { this._rivalEstado = st; },   // el QA lee este eco
    });
    this.rivalMesh = this._rivalSDK.mesh;  // identidad intacta: el poder de
                                           // meteoritos teletransporta
                                           // rivalMesh a pelo (x 0, z −2,1)
    this.group.add(this.rivalMesh);
    this._rivalEstado = '';
    this._rivalSDK.rivalEstado('idle');
'''
        s = splice(s, inicio, fin, nuevo, 'orbital R3: standee')

        # R4 · cartel de bienvenida → createCartel
        inicio = '    // CARTEL de bienvenida (redibujable por etapa)'
        fin = '    this._pintaCartel();\n'
        nuevo = '''    // CARTEL de bienvenida (redibujable por etapa)
    // v2.130 · ANTES flotaba sobre la mesa (0 / 1,38 / −1,05) tapando la
    // vista del rival — petición del artista: la MESA SIEMPRE LIBRE. Va a
    // la pared FRONTAL, a la izquierda del marcador del núcleo (x −1,78),
    // como tablón de misión: visible, aimable y sin estorbar a nadie.
    // v3.6.5-SDK5 · FASE 7: la fontanería (canvas → textura → plano →
    // needsUpdate) vive en el SDK (createCartel); el ARTE sigue siendo
    // nuestro (_pintaCartel pinta en el lienzo del SDK).
    this._cartelSDK = createCartel(THREE, () => this.game, {
      cvW: 512, cvH: 256,
      w: 1.15, h: 0.575,
      pos: [-2.2, 1.5, -5.28],
      rot: [0, 0.1, 0],
      onTex: (t) => this._ownTex.add(t),
    });
    this.cartel = this._cartelSDK.mesh;
    this.group.add(this.cartel);
    this._pintaCartel();
'''
        s = splice(s, inicio, fin, nuevo, 'orbital R4: cartel')

        # R5 · _pintaCartel → pintor del lienzo del SDK
        inicio = '  _pintaCartel() {'
        fin = '    this.cartelTex.needsUpdate = true;\n  }\n'
        nuevo = '''  _pintaCartel() {
    // v3.6.5-SDK5 · FASE 7: el lienzo vive en el SDK (createCartel); el
    // ARTE de este tablón de misión sigue siendo del orbital, byte a byte.
    this._cartelSDK.pinta((c, W, H) => {
      const et = this._etapa();
      c.clearRect(0, 0, W, H);
      c.fillStyle = '#101a2c';
      c.fillRect(0, 0, W, H);
      c.strokeStyle = '#4fd8ff'; c.lineWidth = 10;
      c.strokeRect(8, 8, W - 16, H - 16);
      c.textAlign = 'center';
      c.fillStyle = '#f4ecdd';
      c.font = 'bold 40px Trebuchet MS, sans-serif';
      c.fillText(tx('ESTACIÓN ORBITAL', 'ORBITAL STATION'), W / 2, 64);
      c.fillStyle = '#7fe8ff';
      c.font = 'bold 34px Trebuchet MS, sans-serif';
      c.fillText(tx('ETAPA ' + (this.stage + 1) + '/5 · ' + et.name.toUpperCase(),
        'STAGE ' + (this.stage + 1) + '/5 · ' + et.name.toUpperCase()), W / 2, 124);
      c.fillStyle = '#eef4ff';
      c.font = '24px Trebuchet MS, sans-serif';
      c.fillText(tx('APUNTA Y PULSA EL GATILLO', 'AIM AND PULL THE TRIGGER'), W / 2, 178);
      c.fillText(tx('para empezar', 'to start'), W / 2, 214);
      if (this._champion) {
        c.fillStyle = '#ffd740';
        c.font = 'bold 26px Trebuchet MS, sans-serif';
        c.fillText(tx('★ SUPERADO · revancha libre', '★ CLEARED · free rematch'), W / 2, 248);
      }
    });
  }
'''
        s = splice(s, inicio, fin, nuevo, 'orbital R5: _pintaCartel')

        # R6 · rivalEstado → delegador
        inicio = '  rivalEstado(estado) {'
        fin = '  /* — v3.2.1 · EXPRESIONES DEL ASTRO'
        nuevo = '''  rivalEstado(estado) {
    // assets/<estado>.webp si existe; si no, mantiene el actual.
    // v3.2.1: si el estado no cambia NO recarga — el motor de expresiones
    // vigila cada frame y reasignar el mismo webp 60 veces/s no es gratis
    // (decode + subida a GPU en Quest).
    // v3.6.5-SDK5 · FASE 7: el guard y el cambio de cara viven en el SDK
    // (createRival «perezoso»); this._rivalEstado sigue llenándose vía el
    // eco onEstado (el QA lo lee).
    this._rivalSDK.rivalEstado(estado);
  }
  /* — v3.2.1 · EXPRESIONES DEL ASTRO'''
        s = splice(s, inicio, fin, nuevo, 'orbital R6: rivalEstado', incluir_fin=False)

        # R7 · bloque MÚSICA completo → createMusic
        inicio = '  /* ------------------------------ MÚSICA --------------------------------'
        fin = '''  musicOff() {
    this._musWanted = false;
    if (this._mus) {
      try { this._mus.src.stop(); } catch (e) { /* */ }
      try { this._mus.gain.disconnect(); } catch (e) { /* */ }
      this._mus = null;
    }
  }
'''
        nuevo = '''  /* ------------------------------ MÚSICA --------------------------------
   *  v3.6.5-SDK5 · FASE 7: el motor vive en el SDK (createMusic) con los
   *  knobs CANÓNICOS de la BSO (fundido de entrada 0,8 s con ancla, sync
   *  rampa 0,15 s con guard de fundido, gate UNA MELODÍA al arrancar y
   *  dentro de on(), resurrección de contexto v2.124, parada instantánea).
   *  El «arsenal» que quedaba — el decodeAudioData propio de esta bso.wav —
   *  ya no existe: el fix v2.125 (forma promesa) vive UNA sola vez en el
   *  SDK. El volumen efectivo se consulta EN VIVO vía _musicEffVol(). */
  get _musSDK() {
    if (!this.__musSDK) {
      this.__musSDK = createMusic(() => this.game, {
        url: () => {
          try {
            const m = this.manifest && this.manifest.audio && this.manifest.audio.music;
            return m ? new URL('./' + m, import.meta.url).href : this._A('bso.wav');
          } catch (e) { return this._A('bso.wav'); }
        },
        vol: () => this._musicEffVol(),
        gateOn: true,                        // UNA MELODÍA también en on()
      });
    }
    return this.__musSDK;
  }
  _musicEffVol() {
    try {
      const A = this.game && this.game.audio;
      if (!A) return 0.18;
      return (A.arcMute || A._arcDucked) ? 0.0001 : Math.max(0.0001, A.arcVol);
    } catch (e) { return 0.18; }
  }
  musicOn() { this._musSDK.on(); }
  musicOff() { this._musSDK.off(); }
  _syncMusicGain() { this._musSDK.sync(); }
'''
        s = splice(s, inicio, fin, nuevo, 'orbital R7: música')
    else:
        print('· orbital: ya migrado a FASE 7 (sello presente)')
    if s != orig and not FALLOS:
        p.write_text(s, encoding='utf-8')
        print(f'· orbital/index.js: cirugía FASE 7 aplicada ({len(orig)} → {len(s)} chars)')
    elif FALLOS:
        print('· orbital: SIN escribir (hay fallos)')
    return s


# ————————————————————————————————————————— VALLE ———————————————————————————
def valle():
    p = CH / 'valle_neon' / 'index.js'
    s = p.read_text(encoding='utf-8')
    orig = s
    SELLO = 'v3.6.5-SDK5 · FASE 7'
    if SELLO not in s:
        # V1 · import
        viejo = "import { createMusic, getCore } from '../sdk/champ_sdk.js';"
        nuevo = "import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js';"
        if s.count(viejo) != 1:
            aborta('valle V1: el import del SDK no está exactamente una vez')
        else:
            s = s.replace(viejo, nuevo)

        # V2 · standee → createRival (precarga + FIX de arte real)
        inicio = '    /* standee del rival (arte del campeonato o silueta de reserva) */'
        fin = "    (rival.states || []).forEach((st) => { if (this.stTex.hasOwnProperty(st)) cargaTex(st + '.webp', st); });\n"
        nuevo = '''    /* standee del rival (arte del campeonato o silueta de reserva)
     * v3.6.5-SDK5 · FASE 7: el standee vive en el SDK (createRival, motor
     * «precarga» de la casa valle: swap de mapas precargados + escala por
     * aspecto real). FIX de la migración: se pedían «rival.webp /
     * <estado>.webp», ficheros que NUNCA existieron en assets/ (los reales
     * son .png) — el cartón llevaba pintada la silueta gris de reserva
     * desde la v1. Ahora carga el arte ZETA-7 real: rival_kraken.png +
     * <estado>.png (idle/duelo/derrotado/triunfante). */
    const rival = this.man.rival || {};
    this._rivalSDK = createRival(THREE, () => this.game, {
      modo: 'precarga',
      base: 'rival_kraken.png',
      ext: 'png',
      estados: (rival.states || []).filter(
        (st) => ['idle', 'duelo', 'derrotado', 'triunfante'].indexOf(st) >= 0),
      alto: 1.85,
      anchoFijo: 0.9,                      // el plano nacía 0,9 × 1,85
      material: 'standard',
      alphaTest: 0.05,
      castShadow: true,
      aspecto: true,
      grupo: true,
      pos: [DUEL_X, 0, STAND_Z],
      rotY: Math.atan2(-DUEL_X, 0.55 - STAND_Z),
      resuelve: (f) => this._A('assets/' + f),
      onTex: (t) => this._ownTex.add(t),
    });
    this.standee = this._rivalSDK.node;
    this.standeeMesh = this._rivalSDK.mesh;
    this.standeeMat = this._rivalSDK.mat;
    this.group.add(this.standee);
'''
        s = splice(s, inicio, fin, nuevo, 'valle V2: standee')

        # V3 · cartel de sala → createCartel
        inicio = '    /* cartel de sala (canvas) */'
        fin = '    this.group.add(this.cartel);\n'
        nuevo = '''    /* cartel de sala (canvas)
     * v3.6.5-SDK5 · FASE 7: la fontanería del lienzo vive en el SDK
     * (createCartel); el ARTE sigue siendo nuestro (_pintaCartel). */
    this._cartelSDK = createCartel(THREE, () => this.game, {
      cvW: 1024, cvH: 512,
      w: 2.3, h: 1.15,
      pos: [-1.05, 1.62, -3.6],
      rot: [0, 0.42, 0],
      transparent: true,
      onTex: (t) => this._ownTex.add(t),
    });
    this.cartel = this._cartelSDK.mesh;
    this.group.add(this.cartel);
'''
        s = splice(s, inicio, fin, nuevo, 'valle V3: cartel')

        # V4 · _pintaCartel → pintor del lienzo del SDK
        inicio = '  _pintaCartel() {'
        fin = '    this.cartelTex.needsUpdate = true;\n  }\n'
        nuevo = '''  _pintaCartel() {
    // v3.6.5-SDK5 · FASE 7: el lienzo vive en el SDK (createCartel); el
    // ARTE de este cartel de sala sigue siendo del módulo, byte a byte.
    this._cartelSDK.pinta((c, W, H) => {
      c.clearRect(0, 0, W, H);
      c.fillStyle = 'rgba(8,13,28,.88)';
      c.beginPath(); c.roundRect(10, 10, W - 20, H - 20, 34); c.fill();
      c.lineWidth = 6; c.strokeStyle = '#f59e0b'; c.stroke();
      c.textAlign = 'center';
      c.fillStyle = '#fbbf24'; c.font = '800 74px "Baloo 2", sans-serif';
      c.fillText(this.nombre.toUpperCase().slice(0, 22), W / 2, 104);
      c.fillStyle = '#e2e8f0'; c.font = '600 40px "Nunito Sans", sans-serif';
      const et = this._etapa();
      const lbl = et.kind === 'duelo' ? tx('Etapa', 'Stage') : tx('Prueba', 'Test');
      c.fillText(lbl + ' ' + (this.stage + 1) + '/' + this.etapas.length + ' · ' + et.name, W / 2, 176);
      c.fillStyle = '#94a3b8'; c.font = '600 34px "Nunito Sans", sans-serif';
      c.fillText(tx('Rival: ' + this.rivalNombre, 'Rival: ' + this.rivalNombre), W / 2, 240);
      if (this._champion) {
        c.fillStyle = '#fde047'; c.font = '800 46px "Baloo 2", sans-serif';
        c.fillText('🏆 ' + tx('¡CAMPEÓN!', 'CHAMPION!'), W / 2, 316);
      }
      c.fillStyle = '#7dd3fc'; c.font = '700 36px "Nunito Sans", sans-serif';
      c.fillText(tx('Apunta al mapa con la pala', 'Aim at the map with the paddle'), W / 2, 392);
      c.fillText(tx('y aprieta el gatillo para jugar', 'and pull the trigger to play'), W / 2, 442);
    });
  }
'''
        s = splice(s, inicio, fin, nuevo, 'valle V4: _pintaCartel')

        # V5 · rivalEstado → delegador (hasta el comentario de música)
        inicio = '  rivalEstado(st) {'
        fin = '  /* ------------------------------ música --------------------------------'
        nuevo = '''  rivalEstado(st) {
    // v3.6.5-SDK5 · FASE 7: el swap de caras (con caída a la base) vive en
    // el SDK (createRival «precarga»); aquí queda el punto de entrada.
    this._rivalSDK.rivalEstado(st);
  }

  /* ------------------------------ música --------------------------------'''
        s = splice(s, inicio, fin, nuevo, 'valle V5: rivalEstado', incluir_fin=False)
    else:
        print('· valle_neon: ya migrado a FASE 7 (sello presente)')
    if s != orig and not FALLOS:
        p.write_text(s, encoding='utf-8')
        print(f'· valle_neon/index.js: cirugía FASE 7 aplicada ({len(orig)} → {len(s)} chars)')
    elif FALLOS:
        print('· valle: SIN escribir (hay fallos)')
    return s


# ————————————————————————————————————————— MANIFESTS ———————————————————————
NOTAS = {
    'estacion_orbital': (16,
        '2026-10-19 v3.6.5-SDK5 · FASE 7 de la modularización P0 · CIERRE DEL SDK v1.x (champ_sdk.js v1.4.0): '
        'el standee del ASTRO pasa a createRival (motor «perezoso»: una textura viva + guard anti-recarga '
        'v3.2.1 + eco del estado para el QA), el cartel de bienvenida pasa a createCartel (el ARTE sigue '
        'siendo del módulo) y la MÚSICA — el ÚLTIMO decodeAudioData propio que quedaba en los campeonatos '
        '(la bso.wav del «arsenal») — pasa a createMusic con los knobs canónicos de la BSO. Conducta idéntica.'),
    'valle_neon': (4,
        '2026-10-19 v3.6.5-SDK5 · FASE 7 de la modularización P0 · CIERRE DEL SDK v1.x (champ_sdk.js v1.4.0): '
        'el standee de ZETA-7 pasa a createRival (motor «precarga»: swap de mapas + escala por aspecto) y el '
        'cartel de sala pasa a createCartel. FIX de la migración: el standee pedía «rival.webp / <estado>.webp» '
        'que nunca existieron (los assets reales son .png) y llevaba pintada la silueta gris de reserva desde '
        'la v1 — ahora carga el arte real (rival_kraken.png + estados .png).'),
}


def manifests():
    for mod, (vnew, nota) in NOTAS.items():
        p = CH / mod / 'manifest.json'
        mjs = json.loads(p.read_text(encoding='utf-8'))
        cur = mjs.get('version')
        if cur == vnew:
            print(f'· {mod}: manifest ya está en v{vnew}')
            continue
        if cur != vnew - 1:
            aborta(f'manifest de {mod} está en v{cur}, esperaba v{vnew - 1}')
            continue
        mjs['version'] = vnew
        mjs.setdefault('notes', []).append(nota)
        p.write_text(json.dumps(mjs, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'· {mod}: manifest v{vnew} · nota FASE 7 añadida')


if __name__ == '__main__':
    orbital()
    valle()
    if not FALLOS:
        manifests()
    if FALLOS:
        print(f'\\nFASE 7: {len(FALLOS)} FALLOS — nada escrito parcialmente roto:')
        for f in FALLOS:
            print('  ·', f)
        sys.exit(1)
    print('FASE 7: rival/HUD/música-al-SDK unificados (orbital v16 · valle v4).')
