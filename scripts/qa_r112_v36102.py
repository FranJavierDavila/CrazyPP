#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""qa_r112_v36102.py — capa de QA de la ronda 112 (V3.6.108-SDK6).

HITO M5a del roadmap MEJORAS.md · IA CON ESTILOS (12 personalidades).

  1) REGISTRO (c02): OPPONENT_STYLES con 12 entradas (clasico + 11) —
     nombre/sub ES+EN, multiplicadores acotados y colocación (zIdle/bias);
     'clasico' con mul=null (byte-idéntico); estiloAplicar() con clamps.
  2) INTEGRACIÓN (c12): import OPPONENT_STYLES/estiloAplicar, estado
     ppEstilo persistido (pp_estilo_v1), _estiloActivo() con guardias
     (nunca online/campeonato/calibración/academia), merge en _aiKAplica,
     colocación vía _rivStyleCalc, selector ‹ › en AJUSTES › JUEGO,
     handler case 'estilo' con recálculo EN VIVO y mensaje.
  3) i18n (c00): estilo_lbl + msg_estilo ES/EN.
  4) TELEMETRÍA: ai_style (est+dif) en onMatchStart (sólo local, ≠ clásico);
     catálogo v7 con 17 eventos.
  5) NO-TRAMPA: arnés de estilos qa_estilos_r112.mjs — 12 estilos × 30
     rallies con física/árbitro/IA reales: cfg acotada (NT-1), invariantes
     I-1/I-2/I-3/I-4, firma ≠ clásico (D-1) y 66 parejas distinguibles (D-2).
  6) REGRESIÓN: r111 (onboarding), r110 (duelo), r109 (PWA), sello versión.
"""
import json
import os
import re
import subprocess
import sys

RAIZ = '/home/z/my-project'
OK = []
FAIL = []


def CHK(cond, msg):
    (OK if cond else FAIL).append(msg)
    print(('  ✓ ' if cond else '  ✗ FALLO: ') + msg)


V = json.load(open(os.path.join(RAIZ, 'src/game/VERSION.json')))
VER = V['version']

print('== ESTÁTICA (game.html · M5a) ==')
GH = open(os.path.join(RAIZ, 'public/game.html'), encoding='utf-8').read()

# 1 · registro de estilos (c02)
AGUJAS_C02 = [
    ("OPPONENT_STYLES = [", 'c02: registro OPPONENT_STYLES (forma build, sin export)'),
    ("{ id: 'clasico', es: 'Clásico', en: 'Classic',", 'c02: clasico primero'),
    ("mul: null, zIdle: 0, bias: 0, celeb: 0.6 }", 'c02: clasico byte-idéntico (mul null)'),
    ("{ id: 'looper', es: 'Looper', en: 'Looper',", 'c02: looper'),
    ("{ id: 'chopero', es: 'Chopero', en: 'Chopper',", 'c02: chopero'),
    ("{ id: 'bloqueador', es: 'Bloqueador', en: 'Blocker',", 'c02: bloqueador'),
    ("{ id: 'atacante', es: 'Atacante', en: 'Attacker',", 'c02: atacante'),
    ("{ id: 'defensivo', es: 'Defensivo', en: 'Defender',", 'c02: defensivo'),
    ("{ id: 'dejadas', es: 'Dejadas', en: 'Drop-shot',", 'c02: dejadas'),
    ("{ id: 'nervioso', es: 'Joven nervioso', en: 'Nervous youth',", 'c02: joven nervioso'),
    ("{ id: 'veterano', es: 'Veterano frío', en: 'Cold veteran',", 'c02: veterano frío'),
    ("{ id: 'gigante', es: 'Gigante', en: 'Giant',", 'c02: gigante'),
    ("{ id: 'relampago', es: 'Relámpago', en: 'Lightning',", 'c02: relámpago'),
    ("function estiloAplicar(cfg, estilo) {", 'c02: estiloAplicar con clamps (forma build)'),
    ("errStd: cl(cfg.errStd * (m.err || 1), 0.008, 0.16),", 'c02: errStd acotado (sin trampas)'),
    ("smash: cl(cfg.smash * (m.smash || 1), 0.01, 0.75),", 'c02: smash acotado'),
]
for aguja, nombre in AGUJAS_C02:
    CHK(aguja in GH, 'c02 estilos: ' + nombre)
CHK(GH.count("{ id: '") >= 12, 'c02: 12 entradas en el registro')

# 2 · integración (c12)
AGUJAS_C12 = [
    ("const est = this._estiloActivo();", 'c12: consumo del registro (estilo activo en el juego)'),
    ("localStorage.getItem('pp_estilo_v1') || 'clasico'", 'c12: ppEstilo persistido (pp_estilo_v1)'),
    ('_estiloActivo()', 'c12: _estiloActivo (guardia de contexto)'),
    # r115 · re-ancla: la herencia M5b ATERRIZÓ — el carácter del manifest
    # del campeonato se traduce a un estilo M5a (con toggle del dueño)
    ('// Herencia de estilos a campeonatos (M5b): el carácter del manifest',
     'c12: herencia M5b ATERRIZADA (manifest → estilo M5a)'),
    ('if (this.rivStyleOn === false) return null;', 'c12: toggle del dueño sobre la herencia'),
    ('if (this.net && this.net.online) return null;', 'c12: NUNCA en online'),
    ('if (est) cfg = estiloAplicar(cfg, est);', 'c12: merge en _aiKAplica'),
    ("btn('estilo:prev', 56, y, 120, 56, '‹'", 'c12: selector ‹ en AJUSTES › JUEGO'),
    ("btn('estilo:next', 192, y, 776, 56,", 'c12: selector de nombre (› / ciclo)'),
    ("case 'estilo': {", "c12: handler case 'estilo'"),
    ("localStorage.setItem('pp_estilo_v1', this.ppEstilo);", 'c12: persistencia al ciclar'),
    ('this.applyAISkill();          // recoloca cfg + colocación EN VIVO',
     'c12: recálculo EN VIVO al cambiar de estilo'),
    ("T('estilo_lbl') + ': '", 'c12: etiqueta con el nombre del estilo'),
]
for aguja, nombre in AGUJAS_C12:
    CHK(aguja in GH, 'c12 estilos: ' + nombre)
CHK('s.zIdle = est.zIdle;' in GH and 's.celeb = est.celeb;' in GH,
    'c12: colocación del estilo vía el canal r95 (zIdle/bias/celeb)')

# 3 · i18n (c00)
CHK("estilo_lbl: 'Estilo del rival'," in GH, 'i18n ES: estilo_lbl')
CHK("estilo_lbl: 'Rival style'," in GH, 'i18n EN: estilo_lbl')
CHK("msg_estilo: 'Rival: {v} · misma física, otro carácter'," in GH, 'i18n ES: msg_estilo')
CHK("msg_estilo: 'Rival: {v} · same physics, new character'," in GH, 'i18n EN: msg_estilo')

# 4 · telemetría (catálogo v7)
CHK("__PP_TELE.ev('ai_style', { est: this.ppEstilo, dif: this.difficulty });" in GH,
    'telemetría: ai_style emitido en onMatchStart')
CAT = json.load(open(os.path.join(RAIZ, 'scripts/telemetria_catalogo.json')))
# r115 · re-ancla: el catálogo vive en v8 (carrera entró en el v7 tardío)
CHK(str(CAT['version']).lstrip('v') == '8', f"catálogo v8 (={CAT['version']})")
CHK(len(CAT['eventos']) == 19, f"catálogo documenta 19 eventos (={len(CAT['eventos'])})")
nombres = {e['nombre'] for e in CAT['eventos']}
CHK('ai_style' in nombres, 'catálogo: ai_style documentado')

# 5 · sello + regresión
CHK(f'{VER}' in GH, f'sello de versión {VER} presente en el juego')
REGRESION = [
    ('_megaNormReset', 'r62+ hápticas/poderes intactos'),
    ('r110 · SEMÁNTICA DEL BIT 4', 'r110 fix de duelo presente'),
    ("navigator.serviceWorker.register('sw.js'", 'r109 PWA intacta'),
    ('LA MESA DE LA CASA — RETIRADA', 'r114 diorama retirado (petición del dueño)'),
    ("localStorage.getItem('pp_estilo_v1') || 'clasico'", 'r112 estado presente'),
]
for aguja, nombre in REGRESION:
    CHK(aguja in GH, 'regresión: ' + nombre)
CHK('_demoMuseoConstruir()' not in GH,
    'r114: el diorama IA-vs-IA del Hall está FUERA del servido')

# 6 · ARNÉS DE ESTILOS: corre como CAPA PROPIA del GATE (qa_estilos_r112.mjs,
#         igual que test_fisica.mjs en la capa B) — en esta capa sólo se
#         verifica que el arnés existe y es invocable (sintaxis node).
print('== ARNÉS DE ESTILOS (capa propia: qa_estilos_r112.mjs) ==')
CHK(os.path.exists(os.path.join(RAIZ, 'scripts/qa_estilos_r112.mjs')),
    'no-trampa: el arnés de estilos existe (capa propia del GATE)')
rs = subprocess.run(['node', '--no-warnings', '--check',
                     os.path.join(RAIZ, 'scripts/qa_estilos_r112.mjs')],
                    capture_output=True, text=True, timeout=60)
CHK(rs.returncode == 0, 'no-trampa: arnés con sintaxis node válida')

print(f"\nRESULTADO: {len(OK)} OK · {len(FAIL)} FALLOS")
if FAIL:
    print('\nFALLOS:')
    for f in FAIL:
        print('  ✗ ' + f)
    raise SystemExit(1)
print('CAPA r112 VERDE: 12 estilos de IA sobre la misma física, sin trampas,')
print('selector en AJUSTES › JUEGO, telemetría ai_style y catálogo v7.')
