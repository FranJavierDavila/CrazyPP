#!/usr/bin/env python3
"""V3.5.0-ESC1 · Integración quirúrgica de la etapa 4 NUEVA «ESCUDO DE PALA ·
DEFENSA DEL CASCO» en el módulo Estación Orbital + reorden del camino
(impulso → etapa 2, orden pedido por el dueño) + manifest v11."""
import json
import re
import sys

MOD = '/home/z/my-project/public/championships/estacion_orbital/index.js'
MAN = '/home/z/my-project/public/championships/estacion_orbital/manifest.json'
CLS = '/home/z/my-project/scripts/escudo_pala_class.js'

s = open(MOD, encoding='utf-8').read()
n0 = len(s)
orig = s

def rep(old, new, tag):
    global s
    if s.count(old) != 1:
        sys.exit(f'FALLO: ancla no única ({tag}): {old[:80]!r}')
    s = s.replace(old, new)
    print('·', tag)

# ── 1) CFG.etapas: impulso → etapa 2 · escudo → etapa 4 (reactor fuera) ──
rep(
    """    { kind: 'duelo', id: 'duelo1', name: 'Duelo 1', aiMul: 0.90 },
    { kind: 'prueba', id: 'reactor', name: 'Reactor inestable' },   // v3.3.0: REACTOR DE ENERGÍA INESTABLE (mecánica del dueño)
    { kind: 'duelo', id: 'duelo2', name: 'Duelo 2', aiMul: 1.12 },
    { kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' },   // v3.4.0: REACTOR DE IMPULSO (mecánica del dueño; sustituye al ARKANOID II)
    { kind: 'duelo', id: 'final', name: 'DUELO FINAL', aiMul: 1.42 },""",
    """    { kind: 'duelo', id: 'duelo1', name: 'Duelo 1', aiMul: 0.90 },
    // v3.5.0 (orden del dueño): «colocar la etapa 4 como etapa 2» — el REACTOR
    // DE IMPULSO sube al hueco de la etapa 2; el reactor NUC1 (v3.3.0) queda
    // fuera del camino (clase conservada en el módulo, re-insertable).
    { kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' },
    { kind: 'duelo', id: 'duelo2', name: 'Duelo 2', aiMul: 1.12 },
    // v3.5.0: ETAPA 4 NUEVA — «ESCUDO DE PALA · DEFENSA DEL CASCO» (mecánica
    // reactiva del dueño): devuelve los orbes de plasma con la pala-escudo.
    { kind: 'prueba', id: 'escudo', name: 'Escudo de pala' },
    { kind: 'duelo', id: 'final', name: 'DUELO FINAL', aiMul: 1.42 },""",
    'CFG.etapas reordenado')

# ── 2) clase EscudoCasco + ESC_CFG antes de PwSignEO ──
cls = open(CLS, encoding='utf-8').read()
anchor = 'class PwSignEO'
if s.count(anchor) < 1:
    sys.exit('FALLO: no encuentro class PwSignEO')
idx = s.index(anchor)
s = s[:idx] + cls + '\n' + s[idx:]
print('· clase EscudoCasco insertada (+%d líneas)' % cls.count('\n'))

# ── 3) constructor: instancia tras impulso (usa _ownTex del ctrl) ──
rep(
    "    // v3.4.0: REACTOR DE IMPULSO (etapa 4) — cubos cuánticos + láser + dianas\n    this.impulso = new ReactorImpulso(this);",
    "    // v3.4.0: REACTOR DE IMPULSO (etapa 4) — cubos cuánticos + láser + dianas\n    this.impulso = new ReactorImpulso(this);\n    // v3.5.0: ESCUDO DE PALA (etapa 4 nueva) — pala-escudo contra orbes piratas\n    this.escudo = new EscudoCasco(this);",
    'constructor: this.escudo')

# ── 4) routing _empezarPrueba ──
rep(
    "    // v3.4.0 · REACTOR DE IMPULSO: nueva etapa 4 (mecánica del dueño)\n    if (et.id === 'impulso') { this._empezarImpulso(et); return; }",
    "    // v3.4.0 · REACTOR DE IMPULSO: etapa 2 desde v3.5.0 (orden del dueño)\n    if (et.id === 'impulso') { this._empezarImpulso(et); return; }\n    // v3.5.0 · ESCUDO DE PALA: nueva etapa 4 (mecánica reactiva del dueño)\n    if (et.id === 'escudo') { this._empezarEscudo(et); return; }",
    'routing _empezarPrueba')

# ── 5) _testActivo: escudo tras impulso ──
rep(
    "    if (this.impulso && this.impulso.active) return this.impulso;\n    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    "    if (this.impulso && this.impulso.active) return this.impulso;\n    if (this.escudo && this.escudo.active) return this.escudo;\n    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    '_testActivo')

# ── 6) leave(): escudo.stop() ──
rep(
    "    if (this.impulso) this.impulso.stop();     // v3.4.0: fuera el reactor de impulso",
    "    if (this.impulso) this.impulso.stop();     // v3.4.0: fuera el reactor de impulso\n    if (this.escudo) this.escudo.stop();       // v3.5.0: fuera el escudo de pala",
    'leave()')

# ── 7) export reenter: rama del escudo ──
rep(
    """    if (CTRL && CTRL.impulso && CTRL.impulso.active) {
      try { CTRL.impulso.reenter(); } catch (e) { /* */ }
      return;
    }""",
    """    if (CTRL && CTRL.impulso && CTRL.impulso.active) {
      try { CTRL.impulso.reenter(); } catch (e) { /* */ }
      return;
    }
    if (CTRL && CTRL.escudo && CTRL.escudo.active) {
      try { CTRL.escudo.reenter(); } catch (e) { /* */ }
      return;
    }""",
    'export reenter')

# ── 8) _empezarEscudo + _arrancarEscudo (tras _arrancarImpulso) ──
arr_imp_end = """  _arrancarImpulso(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // estado genérico de PRUEBA (árbitro dormido)
    this.impulso.start();
    this.musicOn();
  }"""
assert s.count(arr_imp_end) == 1, 'ancla _arrancarImpulso'
s = s.replace(arr_imp_end, arr_imp_end + """
  /* — v3.5.0 · ESCUDO DE PALA · DEFENSA DEL CASCO: cartel explicativo
   *  (piel 'estacion') + arranque del EscudoCasco ———————— */
  _empezarEscudo(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';       // árbitro dormido durante el cartel
    this.cartel.visible = false;
    this.rivalEstado('idle');
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        g.showInstrucciones(
          tx('PRUEBA · ESCUDO DE PALA', 'SKILL TEST · PADDLE SHIELD'),
          [
            tx('Drones piratas bombardean el casco: DEVUELVE sus orbes de plasma con la pala (la física es la de siempre, sin correcciones).',
               'Pirate drones shell the hull: RETURN their plasma orbs with the paddle (same old physics, no aids).'),
            tx('Golpe LIMPIO (centro de la hoja + rápido) = destello y +20 % de SOBRECARGA: al 100 % el próximo golpe firme lanza un ORBE PERFORANTE.',
               'CLEAN hit (blade sweet spot + fast) = flash and +20 % OVERCHARGE: at 100 % the next firm hit fires a PIERCING ORB.'),
            tx('3 FASES: 3 drones · 4 drones + el CENTINELA (5 rebotes y su núcleo queda expuesto) · la NAVE ABORDADORA (3 cañones). Si la INTEGRIDAD DEL CASCO llega a 0, derrota.',
               '3 PHASES: 3 drones · 4 drones + the SENTINEL (5 rebounds expose its core) · the BOARDING SHIP (3 cannons). If HULL INTEGRITY hits 0, you lose.'),
          ],
          7.5,
          () => {
            this._instrK = null;          // próxima entrada re-explica (regla v2.106)
            try { this._arrancarEscudo(et); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarEscudo(et);
  }
  _arrancarEscudo(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // estado genérico de PRUEBA (árbitro dormido)
    this.escudo.start();
    this.musicOn();
  }""")
print('· _empezarEscudo/_arrancarEscudo añadidos')

open(MOD, 'w', encoding='utf-8').write(s)
print('módulo: %d → %d caracteres (+%d)' % (n0, len(s), len(s) - n0))

# ── 9) manifest.json → v11: nuevo camino + descripción + cambios ──
m = json.load(open(MAN, encoding='utf-8'))
m['version'] = 11
m['stages'] = [
    {"id": "duelo1", "name": "Duelo 1", "kind": "duelo"},
    {"id": "impulso", "name": "Reactor de impulso", "kind": "impulso",
     "nota": "v3.5.0: ocupa la ETAPA 2 (orden del dueño): destruye los cubos cuánticos con la pelota (3 oleadas de 3/5/7, 120 s cada una) desde la base flotante y desata perturbaciones (Gravedad 0, Atractor, Supergravedad) acertando las dianas con el láser."},
    {"id": "duelo2", "name": "Duelo 2", "kind": "duelo"},
    {"id": "escudo", "name": "Escudo de pala", "kind": "escudo",
     "nota": "v3.5.0 · ETAPA 4 NUEVA «Escudo de Pala · Defensa del Casco»: devuelve los orbes de plasma (estándar, pesado, inestable y rotor) con la pala-escudo; golpe limpio y Sobrecarga con orbe perforante; 3 fases (drones, Centinela de rally y nave abordadora de 3 cañones); la INTEGRIDAD DEL CASCO manda y la barrera trasera recibe los impactos. Arte propio v3.5.0 (escudo_pala/)."},
    {"id": "final", "name": "DUELO FINAL", "kind": "duelo"},
]
m['description']['es'] = ('El camino completo: 2 duelos, el REACTOR DE IMPULSO (cubos cuánticos, pistola '
    'láser, dianas y perturbaciones) en la etapa 2, el ESCUDO DE PALA · DEFENSA DEL CASCO (orbes de '
    'plasma, drones piratas, Centinela y nave abordadora) en la etapa 4 y el DUELO FINAL contra el '
    'ASTRO a bordo de su estación espacial.')
m['description']['en'] = ('The full path: 2 duels, the IMPULSE REACTOR (quantum cubes, laser pistol, '
    'targets and perturbations) at stage 2, the PADDLE SHIELD · HULL DEFENSE (plasma orbs, pirate '
    'drones, Sentinel and boarding ship) at stage 4 and the FINAL DUEL against the ASTRO aboard his '
    'space station.')
m['cambios'] = [
    'v3.5.0-ESC1: el REACTOR DE IMPULSO pasa a la etapa 2 (orden del dueño) y la etapa 4 estrena el ESCUDO DE PALA · DEFENSA DEL CASCO con arte propio',
    'v3.4.1-RIV1: el ASTRO de la sala se recoloca en la convención de duelos (x 1,26 · z −3,82) — ya no se lee dentro de la pared frontal',
]
json.dump(m, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('manifest: version 11 + camino nuevo')
print('OK')
