#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r62 · GENERADOR DE MUESTRAS SFX REALISTAS (síntesis modal física)
================================================================
El dueño: «conseguir esos sonidos realistas sería genial».

Modelo físico: una bola de ping pong (40 mm, 2,7 g, cáscara hueca) contra
cada superficie. La cáscara resuena en MODOS (parciales inarmónicos con
decaimiento exponencial propio), el contacto aporta un TRANSITORIO de ~1 ms
(ruido conformado) y la rigidez del contacto desliza el tono hacia abajo
los primeros milisegundos. Cada superficie añade su cuerpo:

  mesa  (pock)  : modos de la bola brillantes + golpe seco de la madera
  pala   (tock) : goma amortigua + resonancia de la hoja de madera
  canto  (ping) : parcial metálico LARGO e inarmónico (beating entre dos)
  red    (thud) : tela amortiguada + vaínillo de trama (ruido graves)
  suelo  (knock): golpe sordo y grave del suelo de la sala

SALIDA: WAV 44100 Hz · mono · 16-bit PCM (el formato más vainilla posible
para decodeAudioData del casco — la lección r36: 44,1 kHz es el perfil
probado) + base64.json para incrustar en c03_audio_voz.js.
SEMIILLA FIJA (62): build reproducible → golden estable.
"""
import base64
import json
import os
import wave

import numpy as np

SR = 44100
SEED = 62
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sfx_r62')
PEAK = 0.91          # cabeza para el compresor del master
TAIL_DB = -52.0      # corte de cola por debajo del pico

# ----------------------------------------------------------------------
# Especificación modal: [(f_Hz, tau_ms, amp, glide_pct), ...]
#   glide_pct: caída tonal instantánea al contacto (rigidez del impacto)
# Cada muestra = suma de modos + transitorio de ruido + golpe de cuerpo.
# ----------------------------------------------------------------------
MODOS = {
    # Bola sobre MESA: «pock» limpio — 1,25 kHz manda, brillo corto,
    # cuerpo de madera 190 Hz apenas asoma.
    'mesa': {
        'dur': 0.070,
        'modes': [
            (1247.0, 11.0, 1.00, 0.030),
            (2611.0, 5.5, 0.55, 0.028),
            (5230.0, 2.6, 0.30, 0.025),
            (190.0, 9.0, 0.22, 0.012),
        ],
        'transient': {'dur': 0.0011, 'lp': 9200.0, 'amp': 0.85},
    },
    # Bola sobre PALA (goma + hoja): «tock» con cuerpo — la goma come el
    # brillo (LP), la hoja de madera resuena 210 Hz, ataque un pelo más
    # blando que la mesa.
    'pala': {
        'dur': 0.060,
        'modes': [
            (812.0, 9.5, 1.00, 0.035),
            (1640.0, 5.0, 0.42, 0.030),
            (210.0, 24.0, 0.55, 0.010),
            (3330.0, 2.0, 0.16, 0.022),
        ],
        'transient': {'dur': 0.0016, 'lp': 6400.0, 'amp': 0.60},
    },
    # Bola en el CANTO: «ping» metálico — parciales altos INARMÓNICOS con
    # cola larga y beating (2100/2140 Hz a 40 Hz de batido). Es LA firma
    # que distingue el canto a oído.
    'canto': {
        'dur': 0.170,
        'modes': [
            (2100.0, 62.0, 1.00, 0.012),
            (2140.0, 62.0, 0.85, 0.012),   # beating con el anterior
            (3330.0, 38.0, 0.50, 0.010),
            (4920.0, 22.0, 0.34, 0.008),
            (6510.0, 12.0, 0.20, 0.006),
        ],
        'transient': {'dur': 0.0007, 'lp': 12000.0, 'amp': 0.70},
    },
    # Bola en la RED: tela amortiguada — thud grave + vaín de la trama
    # (ruido corto pasado por LP bajo) + zumbido corto de cuerda.
    'red': {
        'dur': 0.090,
        'modes': [
            (172.0, 26.0, 1.00, 0.008),
            (341.0, 12.0, 0.45, 0.006),
            (618.0, 7.0, 0.18, 0.005),
        ],
        'transient': {'dur': 0.0055, 'lp': 820.0, 'amp': 0.75},
    },
    # Bola al SUELO: knock sordo — grave, corto, sin brillo.
    'suelo': {
        'dur': 0.100,
        'modes': [
            (131.0, 30.0, 1.00, 0.006),
            (272.0, 14.0, 0.38, 0.005),
            (540.0, 6.0, 0.14, 0.004),
        ],
        'transient': {'dur': 0.0022, 'lp': 3100.0, 'amp': 0.55},
    },
}


def _lp_noise(rng, n, cutoff):
    """Ruido blanco → paso bajo de 1 polo (coeficiente alpha clásico)."""
    x = rng.standard_normal(n)
    dt = 1.0 / SR
    rc = 1.0 / (2.0 * np.pi * cutoff)
    alpha = dt / (rc + dt)
    y = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def _softclip(x):
    """tanh suave: punch sin digitales (el compresor del master agradece)."""
    return np.tanh(1.25 * x) / np.tanh(1.25)


def generar(nombre, spec, rng):
    n = int(round(spec['dur'] * SR))
    t = np.arange(n) / SR
    total = np.zeros(n)
    for (f, tau_ms, amp, glide) in spec['modes']:
        tau = tau_ms * 1e-3
        # deslizamiento de tono: f(t) = f·(1 - glide·e^(-t/2,2 ms)) — la
        # rigidez del contacto cae en el primer instante y el tono baja.
        ft = f * (1.0 - glide * np.exp(-t / 0.0022))
        fase = 2.0 * np.pi * np.cumsum(ft) / SR
        env = np.exp(-t / tau)
        # ataque del modo: 0,12 ms de subida (evita click de discontinuidad
        # en el tono, el TRANSITORIO es quien da el ataque real)
        atk = int(0.00012 * SR)
        if atk > 0:
            env = env.copy()
            env[:atk] *= np.linspace(0.0, 1.0, atk)
        total += amp * env * np.sin(fase)
    tr = spec['transient']
    nt = int(round(tr['dur'] * SR))
    ruido = _lp_noise(rng, nt, tr['lp'])
    # el transitorio muere exponencial (contacto de ~1 ms)
    env_t = np.exp(-np.arange(nt) / (nt * 0.38))
    total[:nt] += tr['amp'] * ruido * env_t
    # soft-clip + normalización de pico
    total = _softclip(total)
    pico = np.max(np.abs(total))
    if pico > 0:
        total = total / pico * PEAK
    # fade-out final de 1,5 ms (corte de cola limpio)
    fo = int(0.0015 * SR)
    total[-fo:] *= np.linspace(1.0, 0.0, fo)
    pcm = (total * 32767.0).astype('<i2')
    return pcm


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rng = np.random.default_rng(SEED)
    resumen = {}
    b64 = {}
    for nombre in ('mesa', 'pala', 'canto', 'red', 'suelo'):
        pcm = generar(nombre, MODOS[nombre], rng)
        n = len(pcm)
        dur = n / SR
        # corte de cola real: último índice por encima del suelo de ruido
        suelo_db = 20 * np.log10(PEAK) + TAIL_DB
        wpath = os.path.join(OUT_DIR, f'{nombre}.wav')
        with wave.open(wpath, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        # r62-CORRECCIÓN: el base64 lleva el WAV COMPLETO (contenedor RIFF
        # incluido) — la primera versión codificaba el PCM desnudo y
        # decodeAudioData lo rechazaba (sin cabecera no hay formato).
        with open(wpath, 'rb') as f:
            raw = f.read()
        b64[nombre] = base64.b64encode(raw).decode('ascii')
        # métricas de cordura
        fl = np.abs(np.fft.rfft(pcm.astype(np.float64) / 32767.0))
        fq = np.fft.rfftfreq(n, 1.0 / SR)
        centroide = float(np.sum(fq * fl) / max(np.sum(fl), 1e-9))
        resumen[nombre] = {
            'duracion_ms': round(dur * 1000, 1),
            'bytes_wav': len(raw),
            'bytes_b64': len(b64[nombre]),
            'pico': round(float(np.max(np.abs(pcm.astype(np.float64))) / 32767.0), 3),
            'centroide_hz': round(centroide, 1),
        }
    with open(os.path.join(OUT_DIR, 'base64.json'), 'w') as f:
        json.dump(b64, f)
    total_b64 = sum(len(v) for v in b64.values())
    print('=== SFX r62 · síntesis modal (semilla %d) ===' % SEED)
    for k, v in resumen.items():
        print(f"  {k:6s} {v['duracion_ms']:6.1f} ms · pico {v['pico']:.3f} · "
              f"centroide {v['centroide_hz']:7.1f} Hz · wav {v['bytes_wav']:6d} B · "
              f"b64 {v['bytes_b64']:6d} B")
    print(f"  TOTAL base64: {total_b64} bytes ({total_b64/1024:.1f} KB) — "
          f"incrustable en c03 sin peso real")
    # verificación de decodificación WAV válida (relectura)
    for nombre in resumen:
        with wave.open(os.path.join(OUT_DIR, f'{nombre}.wav'), 'rb') as w:
            assert w.getframerate() == SR and w.getnchannels() == 1 \
                and w.getsampwidth() == 2, f'{nombre}: WAV no vainilla'
    print('  WAV re-leídos: 44100 Hz · mono · 16-bit OK')


if __name__ == '__main__':
    main()
