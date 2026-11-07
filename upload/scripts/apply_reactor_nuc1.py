#!/usr/bin/env python3
"""v3.3.0-NUC1 · Aplica el REACTOR DE ENERGÍA INESTABLE (etapa 2) al módulo
estacion_orbital: inserta la clase ReactorInestable, enruta _empezarPrueba,
instancia en el constructor, ordena _testActivo y reenter, renombra la etapa
y actualiza manifest.json. Cada ancho se verifica ÚNICO antes de tocar."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
IDX = RAIZ / 'public/championships/estacion_orbital/index.js'
MAN = RAIZ / 'public/championships/estacion_orbital/manifest.json'
GLB_SRC = RAIZ / 'upload/nucleo_gravedad_lp.glb'
GLB_DST = RAIZ / 'public/championships/estacion_orbital/assets/nucleo_gravedad_lp.glb'
FRAG = RAIZ / 'scripts/reactor_nuc1_class.js'

src = IDX.read_text()
frag = FRAG.read_text().rstrip() + '\n'

def reemplazo(antes, despues, etiqueta):
    global src
    n = src.count(antes)
    if n != 1:
        sys.exit(f'ERROR ancla {etiqueta!r}: {n} apariciones (esperaba 1)')
    src = src.replace(antes, despues, 1)
    print(f'  OK {etiqueta}')

# 1) etapa 2 del camino: muro1 → reactor
reemplazo(
    "    { kind: 'prueba', id: 'muro1', name: 'Arkanoid orbital' },   // v3.2.0: MURO según el mapa del dueño",
    "    { kind: 'prueba', id: 'reactor', name: 'Reactor inestable' },   // v3.3.0: REACTOR DE ENERGÍA INESTABLE (mecánica del dueño)",
    'CFG.etapas[1] reactor')

# 2) clase ReactorInestable tras el cierre de EOArkanoid (fin de su _hud)
ancla_clase = """    if (this._msg) {
      g2.textAlign = 'center';
      g2.fillStyle = '#ffd257';
      g2.font = '800 40px system-ui, sans-serif';
      g2.fillText(this._msg, 512, 40);
    }
    this.hudTex.needsUpdate = true;
  }
}
"""
reemplazo(ancla_clase, ancla_clase + '\n' + frag, 'clase ReactorInestable')

# 3) instancia en el constructor del StockController
reemplazo(
    "    this.arkanoid = new EOArkanoid(this);",
    "    this.arkanoid = new EOArkanoid(this);\n"
    "    // v3.3.0: REACTOR DE ENERGÍA INESTABLE (etapa 2)\n"
    "    this.reactor = new ReactorInestable(this);",
    'constructor reactor')

# 4) enrutado de _empezarPrueba
reemplazo(
    "    // v3.2.0 · MUROS ORBITALES: las pruebas del camino son ahora ARKANOID\n"
    "    if (et.id === 'muro1' || et.id === 'muro2') { this._empezarMuro(et); return; }",
    "    // v3.3.0 · REACTOR DE ENERGÍA INESTABLE: la etapa 2 ya no es muro\n"
    "    if (et.id === 'reactor') { this._empezarReactor(et); return; }\n"
    "    // v3.2.0 · MUROS ORBITALES: la etapa 4 sigue siendo ARKANOID II\n"
    "    if (et.id === 'muro2') { this._empezarMuro(et); return; }",
    'enrutado _empezarPrueba')

# 5) _empezarReactor + _arrancarReactor antes de _arrancarPrueba
nuevos_metodos = """  /* — v3.3.0 · REACTOR DE ENERGÍA INESTABLE: cartel explicativo (piel del
   *  artista vía NORMAS_SKIN) + arranque del ReactorInestable ——————————— */
  _empezarReactor(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';       // árbitro dormido durante el cartel
    this.cartel.visible = false;
    this.rivalEstado('idle');
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        g.showInstrucciones(
          tx('PRUEBA · REACTOR DE ENERGÍA INESTABLE',
             'SKILL TEST · UNSTABLE POWER REACTOR'),
          [
            tx('El NÚCLEO DE GRAVEDAD lanza esferas de plasma: golpéalas con la pala y mételas en las COMPUERTAS de energía.',
               'The GRAVITY CORE hurls plasma spheres: bat them with your paddle into the energy GATES.'),
            tx('Cada acierto estabiliza el reactor; un fallo sacude la nave y altera la gravedad. Primero una compuerta GRANDE, luego pequeñas y móviles. 2 min 30 s y 5 fallos de margen.',
               'Every hit stabilizes the reactor; a miss shakes the ship and shifts gravity. First one BIG gate, then small moving ones. 2 min 30 s, 5 misses allowed.'),
          ],
          7.5,
          () => {
            this._instrK = null;          // próxima entrada re-explica (regla v2.106)
            try { this._arrancarReactor(et); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarReactor(et);
  }
  _arrancarReactor(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // estado genérico de PRUEBA (árbitro dormido)
    this.reactor.start();
    this.musicOn();
  }

"""
reemplazo('  _arrancarPrueba(compleja) {', nuevos_metodos + '  _arrancarPrueba(compleja) {',
          '_empezarReactor/_arrancarReactor')

# 6) _testActivo: el reactor primero
reemplazo(
    "  _testActivo() {\n    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    "  _testActivo() {\n    if (this.reactor && this.reactor.active) return this.reactor;\n"
    "    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    '_testActivo reactor')

# 7) export reenter: rama del reactor
reemplazo(
    "  reenter() {   // v3.2.0: en pleno muro, reanuda la prueba\n"
    "    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {",
    "  reenter() {   // v3.2.0: en plena prueba, reanuda\n"
    "    if (CTRL && CTRL.reactor && CTRL.reactor.active) {\n"
    "      try { CTRL.reactor.reenter(); } catch (e) { /* */ }\n"
    "      return;\n"
    "    }\n"
    "    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {",
    'export reenter reactor')

IDX.write_text(src)
print(f'index.js escrito: {len(src):,} B')

# 8) manifest.json: etapa 2 → reactor + versión v8
man = json.loads(MAN.read_text())
for st in man['stages']:
    if st['id'] == 'muro1':
        st['id'] = 'reactor'
        st['name'] = 'Reactor de energía inestable'
        st['kind'] = 'reactor'
        st['nota'] = ('v3.3.0: el núcleo de gravedad lanza esferas de plasma; '
                      'devuélvelas con la pala a las compuertas de energía')
for k in ('version', 'manifestVersion', 'v'):
    if k in man and isinstance(man[k], str):
        man[k] = man[k].replace('v7', 'v8')
if 'nota' in man and isinstance(man['nota'], str):
    man['nota'] += ' · v3.3.0-NUC1: etapa 2 = Reactor de energía inestable'
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n')
print(f"manifest.json: stages[1] = {man['stages'][1]['id']} / {man['stages'][1]['name']}")

# 9) asset GLB a los assets del campeonato
if not GLB_DST.exists():
    shutil.copy2(GLB_SRC, GLB_DST)
    print(f'GLB copiado → {GLB_DST.name} ({GLB_DST.stat().st_size:,} B)')
else:
    print('GLB ya alojado')

# 10) validación sintáctica
r = subprocess.run(['node', '--check', str(IDX)], capture_output=True, text=True)
if r.returncode != 0:
    sys.exit(f'ERROR de sintaxis:\n{r.stderr[:2000]}')
print('node --check OK')
