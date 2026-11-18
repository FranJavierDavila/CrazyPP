#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audita qué tokens de identidad del build_zip v364 sobreviven en el código
FASE 7 migrado. No toca nada: solo informa."""
import json
from pathlib import Path

PUB = Path('/home/z/my-project/public')

ORBITAL_TKS = [
    'class ReactorImpulso', 'const IMP_CFG', "id: 'impulso'",
    '_empezarImpulso', '_arrancarImpulso', '_oleadaArranca',
    '_dianaHit', '_pertAplica', '_cadenaDestruye',
    'nucleo_gravedad_lp.glb', 'class ReactorInestable',
    'class EOArkanoid', 'class PwSignEO',
    "if (et.id === 'impulso') { this._empezarImpulso(et); return; }",
    "if (et.id === 'escudo') { this._empezarEscudo(et); return; }",
    "if (this.escudo) this.escudo.stop();",
    'RIV_H = 2.15', 'position.set(1.26, RIV_H / 2',
    '(D.tableCenterZ || -1.6) - 1.70',
    'cubeS: 0.16, cubeHitR: 0.14', 'ballT: 0.80, ballH: 0.34',
    'atrSep: 0.19', 'static HUECOS', '_atractorSepara',
    'dianaMat', 'ShaderMaterial', 'uDissolve',
    'alphaTest: ventanal ? 0.35 : 0', 'warpSpeed',
    "imp.phase === 'play' || imp.phase === 'intro'",
    'function _geoMeteorito', '_rocasGeo = [_geoMeteorito(0)',
    'vertexColors: true, flatShading: true', 'emissive: 0xff6a22',
    'dronTractor', '_tractorTrap', 'caída vertical pura',
    'const ATT = 7.5', "this._sfx('risa_astro.mp3')",
    "this._sfx('enfado_astro.mp3')", 'dianaVis: 2.0',
    'this._restT > 0.6', "congela(this.game, (def.warn || 2.0) + 0.15)",
    "from '../sdk/champ_sdk.js'", 'createSfx(import.meta.url',
    '__sdkSfx',
    'class EscudoCasco', 'const ESC_CFG', "id: 'escudo'",
    '_empezarEscudo', '_arrancarEscudo', 'escudo_pala/',
    'window.__PP_PADDLE_SWEEP', 'BARRERA DE CASCO', 'champDecorHidden',
    'x: 1197, y: 335, r: 115', 'TAPA_W = 240 / 1376',
    "get gunArmed() { return !!(CTRL && CTRL.gunArmed); }",
    # tokens FASE 5/6 que v364 verificaba del orbital
    'createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
    'onTex: (tex) => { try { this.ctrl._ownTex.add(tex); }',
]

SDK_TKS = [
    "const SDK_VERSION = '1.3.0'", 'export function createSfx',
    'export function congela', 'export function descongela',
    'export function getCore', 'export function assetURL',
    'forma promesa (v2.125)', 'function precarga',
    'opts && opts.pan', 'export function createMusic',
    'o.gateStart !== false && arcPlaying()', 'export function createPowerSign',
    'V240 = o.coreo', 'const breathe = 0.78 + Math.sin(t * 9.0) * 0.22',
    'window.__PP_SDK = SDK_VERSION',
    # nuevos de v1.4.0
    "const SDK_VERSION = '1.4.0'", 'export function createRival',
    'export function createCartel', "modo === 'perezoso'", "modo === 'precarga'",
]

MOD_TKS = {
    'oeste': [
        "import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
        '__sfxSDK', "precarga('risas_forajido.mp3')",
        "eng.play('risas.mp3', vol || 0.8, { pan: 0.4 })",
        'congela(g, DUELO_P.drawT + DUELO_P.window + 0.35)',
        'congela(g, 0.10)',
        'congela(g, Math.max(this.powerSign.T_OUT, OESTE_POWER.warn) + 0.1)',
        'const __CORE = getCore() || {}',
        'get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
        'vol: () => this._musicEffVol()',
        "puede: () => this._stageMode !== 'tren'",
        'get _musSDKv()', "syncMode: 'direct'",
        'excluso: () => this.ctrl._musSDK.sonando()',
        '_musicStart() { this._musSDKv.on(); }',
        '_musicStop() { this._musSDKv.off(); }',
        'createPowerSign(THREE', "coreo: 'clasica'", "arte: 'plano'",
        'pintar: (aplicar) => this._pintarRespaldo(aplicar)',
        'oesteCanvas(1024, 560)',
    ],
    'magia': [
        "import { createSfx, createMusic, createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
        '__sfxSDK', "precarga('risas.mp3')", "eng.play('risas.mp3', 1.0)",
        'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
        'const __CORE = getCore() || {}',
        'get _musSDK()', "url: () => this.manifest && this.manifest.musicUrl",
        'vol: () => this._musicEffVol()',
        '_syncMusicGain() {', 'this._musSDK.sync();',
        'createPowerSign(THREE', "coreo: 'clasica'", "arte: 'canvas1024'",
        'fallbackURL: () => paintPowerBanner()',
    ],
    'locura': [
        "import { createPowerSign, congela, getCore } from '../sdk/champ_sdk.js'",
        'congela(g, Math.max(this.powerSign.T_OUT, warn) + 0.1)',
        'const __CORE = getCore() || {}',
        'createPowerSign(THREE', "coreo: 'v240'", 'halo: true',
        "arte: 'fit1833'",
    ],
    'valle_neon': [
        "import { createMusic, getCore } from '../sdk/champ_sdk.js'",
        'const CORE = getCore();',
        'get _musSDK()', 'fadeIn: 1.2', 'ancla: false',
        "syncMode: 'none'", 'gateOn: true', 'stopFade: 0.4',
        # nuevos FASE 7
        "import { createCartel, createMusic, createRival, getCore } from '../sdk/champ_sdk.js'",
        "modo: 'precarga'", "base: 'rival_kraken.png'", "ext: 'png'",
        'createCartel(THREE', 'this._cartelSDK.pinta(',
        'this._rivalSDK.rivalEstado(st);',
    ],
}

ORBITAL_NUEVOS = [
    "import { createCartel, createMusic, createPowerSign, createRival, createSfx, congela } from '../sdk/champ_sdk.js'",
    "modo: 'perezoso'", "base: 'rival.webp'",
    'this._rivalSDK = createRival(THREE, () => this.game, {',
    'this._cartelSDK = createCartel(THREE, () => this.game, {',
    'this._cartelSDK.pinta((c, W, H) => {',
    'this._rivalSDK.rivalEstado(estado);',
    'get _musSDK()', 'gateOn: true,', 'vol: () => this._musicEffVol()',
    'musicOn() { this._musSDK.on(); }',
    '_syncMusicGain() { this._musSDK.sync(); }',
]

print('== ORBITAL (tokens v364 que sobreviven / muertos) ==')
eo = (PUB / 'championships/estacion_orbital/index.js').read_text(encoding='utf-8')
for tk in ORBITAL_TKS:
    if tk not in eo:
        print('  MUERTO :', repr(tk))
print('== ORBITAL (tokens nuevos FASE 7) ==')
for tk in ORBITAL_NUEVOS:
    print(('  OK     : ' if tk in eo else '  FALTA  : ') + repr(tk))
print('  decodeAudioData en orbital:', eo.count('decodeAudioData('))

print('== SDK ==')
sdk = (PUB / 'championships/sdk/champ_sdk.js').read_text(encoding='utf-8')
for tk in SDK_TKS:
    print(('  OK     : ' if tk in sdk else '  AUSENTE: ') + repr(tk))

print('== RESTO DE MÓDULOS ==')
for mod, tks in MOD_TKS.items():
    src = (PUB / f'championships/{mod}/index.js').read_text(encoding='utf-8')
    man = json.loads((PUB / f'championships/{mod}/manifest.json').read_text(encoding='utf-8'))
    print(f'-- {mod} (manifest v{man.get("version")}, decodeAudioData={src.count("decodeAudioData(")})')
    for tk in tks:
        if tk not in src:
            print('  MUERTO :', repr(tk))
