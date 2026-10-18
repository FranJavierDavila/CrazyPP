#!/usr/bin/env python3
"""CRAZY PING PONG · v3.4.0-IMP1 — integra el REACTOR DE IMPULSO (nueva etapa
4 del campeonato Estación Orbital, mecánica del dueño) en el módulo orbital:
  · clase ReactorImpulso + IMP_CFG (scripts/reactor_impulso_class.js)
  · CFG.etapas[3] muro2 → impulso + routing (_empezarImpulso/_arrancarImpulso)
  · constructor: this.impulso · _testActivo · export reenter + gunArmed/fireGun
    (FIX: el export nunca exponía gunArmed/fireGun y el gatillo no llegaba)
  · fireGun: raycast contra las DIANAS cuánticas · _gunUpdate: pistola en IMP1
  · leave(): stop() de reactor (fix v3.3.0 que faltaba) e impulso
  · manifest.json → v9 (stages[3] impulso) · game.html → 3.4.0-IMP1
Anclas ÚNICAS (assert count==1) sobre el módulo de 5.195 líneas."""
import json
import re
import sys
from pathlib import Path

RAIZ = Path('/home/z/my-project')
MOD = RAIZ / 'public/championships/estacion_orbital/index.js'
CLS = RAIZ / 'scripts/reactor_impulso_class.js'
MAN = RAIZ / 'public/championships/estacion_orbital/manifest.json'
GAME = RAIZ / 'public/game.html'

src = MOD.read_text(encoding='utf-8')
cls = CLS.read_text(encoding='utf-8').rstrip() + '\n'
n_ediciones = 0

def rep(s, viejo, nuevo, etiqueta):
    global n_ediciones
    k = s.count(viejo)
    if k != 1:
        sys.exit(f'FALLO ({etiqueta}): ancla encontrada {k} veces (esperado 1):\n{viejo[:120]}…')
    n_ediciones += 1
    print(f'  · {etiqueta}')
    return s.replace(viejo, nuevo)

# ── 1. CFG.etapas[3]: muro2 → impulso ────────────────────────────────────────
src = rep(src,
    "    { kind: 'prueba', id: 'muro2', name: 'Arkanoid II' },   // v3.2.0: MURO rojo/azul + láser",
    "    { kind: 'prueba', id: 'impulso', name: 'Reactor de impulso' },   // v3.4.0: REACTOR DE IMPULSO (mecánica del dueño; sustituye al ARKANOID II)",
    'CFG.etapas[3] → impulso')

# ── 2. Clase ReactorImpulso + IMP_CFG antes de PwSignEO ──────────────────────
ancla_pw = ("/* ============================================================================\n"
            " *  PwSignEO (v3.2.1) — ANUNCIO ÉPICO de «SUPER POWER!!» · port 1:1 del")
src = rep(src, ancla_pw, cls + '\n' + ancla_pw, 'clase ReactorImpulso insertada')

# ── 3. Constructor: instancia tras reactor ───────────────────────────────────
src = rep(src,
    "    this.reactor = new ReactorInestable(this);",
    "    this.reactor = new ReactorInestable(this);\n"
    "    // v3.4.0: REACTOR DE IMPULSO (etapa 4) — cubos cuánticos + láser + dianas\n"
    "    this.impulso = new ReactorImpulso(this);",
    'constructor: this.impulso')

# ── 4. Routing en _empezarPrueba ─────────────────────────────────────────────
src = rep(src,
    "    // v3.2.0 · MUROS ORBITALES: la etapa 4 sigue siendo ARKANOID II\n"
    "    if (et.id === 'muro2') { this._empezarMuro(et); return; }",
    "    // v3.4.0 · REACTOR DE IMPULSO: nueva etapa 4 (mecánica del dueño)\n"
    "    if (et.id === 'impulso') { this._empezarImpulso(et); return; }\n"
    "    // v3.2.0 · MUROS ORBITALES (ARKANOID II): sustituido por el reactor de impulso\n"
    "    if (et.id === 'muro2') { this._empezarMuro(et); return; }",
    'routing _empezarPrueba')

# ── 5. Métodos _empezarImpulso / _arrancarImpulso tras _arrancarReactor ──────
ancla_arr = ("  _arrancarReactor(et) {\n"
             "    const g = this.game;\n"
             "    this._poderClear();\n"
             "    this.state = 'prueba';\n"
             "    g.rules.state = 'arkanoid';        // estado genérico de PRUEBA (árbitro dormido)\n"
             "    this.reactor.start();\n"
             "    this.musicOn();\n"
             "  }\n")
nuevos_metodos = ancla_arr + """
  /* — v3.4.0 · REACTOR DE IMPULSO: cartel explicativo (piel del artista vía
   *  NORMAS_SKIN) + arranque del ReactorImpulso ——————————————— */
  _empezarImpulso(et) {
    const g = this.game;
    this.state = 'prueba';
    g.rules.state = 'champtest';       // árbitro dormido durante el cartel
    this.cartel.visible = false;
    this.rivalEstado('idle');
    if (this._instrK !== et.id) {
      this._instrK = et.id;
      try {
        g.showInstrucciones(
          tx('PRUEBA · REACTOR DE IMPULSO', 'SKILL TEST · IMPULSE REACTOR'),
          [
            tx('El REACTOR DE IMPULSO expulsa CUBOS CUÁNTICOS: destrúyelos golpeándolos con la bola desde la BASE FLOTANTE (aquí no hay mesa).',
               'The IMPULSE REACTOR spews QUANTUM CUBES: destroy them with the ball from the FLOATING BASE (no table here).'),
            tx('La PISTOLA LÁSER de tu mano libre acierta las DIANAS CUÁNTICAS y desata PERTURBACIONES: Gravedad 0, Atractor (¡un golpe los destruye todos!) y Supergravedad.',
               'The LASER PISTOL on your free hand shoots QUANTUM TARGETS and unleashes PERTURBATIONS: Zero-G, Attractor (one hit destroys them all!) and Supergravity.'),
            tx('3 OLEADAS de 3, 5 y 7 cubos · 2 minutos por oleada · cada diana acertada trae una perturbación nueva (y cada 30 s una automática).',
               '3 WAVES of 3, 5 and 7 cubes · 2 minutes each · every hit target brings a new perturbation (plus an automatic one every 30 s).'),
          ],
          7.5,
          () => {
            this._instrK = null;          // próxima entrada re-explica (regla v2.106)
            try { this._arrancarImpulso(et); } catch (e) { /* */ }
          },
          'estacion',
          { empezar: true });
        return;
      } catch (e) { this._instrK = null; }   // sin núcleo de carteles: arranca igual
    }
    this._instrK = null;
    this._arrancarImpulso(et);
  }
  _arrancarImpulso(et) {
    const g = this.game;
    this._poderClear();
    this.state = 'prueba';
    g.rules.state = 'arkanoid';        // estado genérico de PRUEBA (árbitro dormido)
    this.impulso.start();
    this.musicOn();
  }
"""
src = rep(src, ancla_arr, nuevos_metodos, '_empezarImpulso/_arrancarImpulso')

# ── 6. _testActivo: impulso antes de arkanoid ────────────────────────────────
src = rep(src,
    "  _testActivo() {\n"
    "    if (this.reactor && this.reactor.active) return this.reactor;\n"
    "    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    "  _testActivo() {\n"
    "    if (this.reactor && this.reactor.active) return this.reactor;\n"
    "    if (this.impulso && this.impulso.active) return this.impulso;\n"
    "    if (this.arkanoid && this.arkanoid.active) return this.arkanoid;",
    '_testActivo')

# ── 7. getter gunArmed: incluye impulso ──────────────────────────────────────
src = rep(src,
    "  get gunArmed() {\n"
    "    const g = this.game;\n"
    "    const ark = this.arkanoid;\n"
    "    return !!(this.state === 'prueba' && ark && ark.active && ark.variant === 2 &&\n"
    "      ark.phase === 'play' &&\n"
    "      g.gunMounts && g.gunMounts[1 - g.paddleHand] &&\n"
    "      g.gunMounts[1 - g.paddleHand].visible);\n"
    "  }",
    "  get gunArmed() {\n"
    "    const g = this.game;\n"
    "    const ark = this.arkanoid;\n"
    "    const imp = this.impulso;\n"
    "    // v3.4.0: la pistola también arma en el REACTOR DE IMPULSO (etapa 4)\n"
    "    const impOn = !!(imp && imp.active && imp.phase === 'play');\n"
    "    const arkOn = !!(ark && ark.active && ark.variant === 2 && ark.phase === 'play');\n"
    "    return !!(this.state === 'prueba' && (impOn || arkOn) &&\n"
    "      g.gunMounts && g.gunMounts[1 - g.paddleHand] &&\n"
    "      g.gunMounts[1 - g.paddleHand].visible);\n"
    "  }",
    'getter gunArmed')

# ── 8. fireGun: declaración hitDiana ─────────────────────────────────────────
src = rep(src,
    "    let hitTime = false;",
    "    let hitTime = false;\n"
    "    let hitDiana = false;   // v3.4.0: diana cuántica del reactor de impulso",
    'fireGun: hitDiana')

# ── 9. fireGun: raycast de dianas (rama impulso) ─────────────────────────────
src = rep(src,
    "    const ark = this.arkanoid;\n"
    "    if (ark && ark.active && ark.bricks && ark.bricks.length) {",
    "    const ark = this.arkanoid;\n"
    "    const imp = this.impulso;\n"
    "    if (imp && imp.active && imp.phase === 'play') {\n"
    "      // v3.4.0: RAYCAST contra la DIANA cuántica (sólo ella; nunca los cubos)\n"
    "      const ray = new THREE.Raycaster(pos, dir, 0, 8.0);\n"
    "      ray.camera = g.camera;             // los SPRITES exigen raycaster.camera (three r170)\n"
    "      const tgt = imp.laserTargets();\n"
    "      if (tgt.length) {\n"
    "        const hits = ray.intersectObjects(tgt, false);\n"
    "        if (hits.length) {\n"
    "          hitDist = hits[0].distance;\n"
    "          hitPoint.copy(hits[0].point);\n"
    "          hitDiana = true;\n"
    "        }\n"
    "      }\n"
    "    } else if (ark && ark.active && ark.bricks && ark.bricks.length) {",
    'fireGun: raycast dianas')

# ── 10. fireGun: aplicación del impacto en la diana ──────────────────────────
src = rep(src,
    "    } else if (hitTime) {\n"
    "      g.rig.updateWorldMatrix(true, false);\n"
    "      const lp = g.rig.worldToLocal(hitPoint.clone());\n"
    "      ark._flash(lp);\n"
    "      ark._breakTimeBrick();\n"
    "    }",
    "    } else if (hitTime) {\n"
    "      g.rig.updateWorldMatrix(true, false);\n"
    "      const lp = g.rig.worldToLocal(hitPoint.clone());\n"
    "      ark._flash(lp);\n"
    "      ark._breakTimeBrick();\n"
    "    } else if (hitDiana) {\n"
    "      g.rig.updateWorldMatrix(true, false);\n"
    "      const lp = g.rig.worldToLocal(hitPoint.clone());\n"
    "      imp._dianaHit(lp);\n"
    "    }",
    'fireGun: impacto diana')

# ── 11. _gunUpdate: pistola montada y armada también en impulso ──────────────
src = rep(src,
    "  _gunUpdate(dt) {\n"
    "    const g = this.game;\n"
    "    const ark = this.arkanoid;\n"
    "    const ark2On = !!(ark && ark.active && ark.variant === 2 &&\n"
    "      g.renderer && g.renderer.xr && g.renderer.xr.isPresenting);\n"
    "    const holdPhase = ark && (ark.phase === 'serve' || ark.phase === 'intro' ||\n"
    "      ark.phase === 'result');\n"
    "    const armed = ark2On && !holdPhase;\n"
    "    if (armed && !this._gunHintDone) {\n"
    "      this._gunHintDone = true;\n"
    "      try { g.rules.message = T('ark_gun_on'); } catch (e) { /* */ }\n"
    "    }\n"
    "    if (ark2On && !this._gunArtModel) this._loadGunArt();\n"
    "    if (ark2On && this._gunArtModel && (this._gunArt || []).length === 0) {\n"
    "      this._attachGunArt();\n"
    "    }",
    "  _gunUpdate(dt) {\n"
    "    const g = this.game;\n"
    "    const ark = this.arkanoid;\n"
    "    const ark2On = !!(ark && ark.active && ark.variant === 2 &&\n"
    "      g.renderer && g.renderer.xr && g.renderer.xr.isPresenting);\n"
    "    // v3.4.0: la PISTOLA también se monta y arma en el REACTOR DE IMPULSO\n"
    "    const imp = this.impulso;\n"
    "    const impOn = !!(imp && imp.active && imp.phase === 'play' &&\n"
    "      g.renderer && g.renderer.xr && g.renderer.xr.isPresenting);\n"
    "    const gunOn = ark2On || impOn;\n"
    "    const holdPhase = ark && (ark.phase === 'serve' || ark.phase === 'intro' ||\n"
    "      ark.phase === 'result');\n"
    "    const armed = impOn || (ark2On && !holdPhase);\n"
    "    if (armed && !this._gunHintDone) {\n"
    "      this._gunHintDone = true;\n"
    "      try { g.rules.message = T('ark_gun_on'); } catch (e) { /* */ }\n"
    "    }\n"
    "    if (gunOn && !this._gunArtModel) this._loadGunArt();\n"
    "    if (gunOn && this._gunArtModel && (this._gunArt || []).length === 0) {\n"
    "      this._attachGunArt();\n"
    "    }",
    '_gunUpdate: pistola en IMP1')

# ── 12. leave(): stops de reactor (FIX v3.3.0) e impulso ─────────────────────
src = rep(src,
    "    this.prueba.stop();\n"
    "    if (this.arkanoid) this.arkanoid.stop();   // v3.2.0: fuera el muro",
    "    this.prueba.stop();\n"
    "    if (this.arkanoid) this.arkanoid.stop();   // v3.2.0: fuera el muro\n"
    "    if (this.reactor) this.reactor.stop();     // v3.3.0 FIX: faltaba (quedaba vivo al salir)\n"
    "    if (this.impulso) this.impulso.stop();     // v3.4.0: fuera el reactor de impulso",
    'leave(): stops')

# ── 13. export: gunArmed + fireGun (contrato del núcleo) ─────────────────────
src = rep(src,
    "  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },",
    "  serveTrigger(i) { if (CTRL) CTRL.serveTrigger(i); },\n"
    "  // v3.4.0 FIX: el núcleo lee m.gunArmed / m.fireGun sobre el EXPORT del\n"
    "  // módulo (game.html L8585/L11645) — el export de EO nunca los exponía y\n"
    "  // el gatillo del láser no llegaba a StockController.fireGun.\n"
    "  get gunArmed() { return !!(CTRL && CTRL.gunArmed); },\n"
    "  fireGun(i) { if (CTRL) { try { CTRL.fireGun(i); } catch (e) { console.warn('[estacion.fireGun]', e); } } },",
    'export: gunArmed/fireGun')

# ── 14. export: reenter también reanuda el impulso ───────────────────────────
src = rep(src,
    "  reenter() {   // v3.2.0: en plena prueba, reanuda\n"
    "    if (CTRL && CTRL.reactor && CTRL.reactor.active) {\n"
    "      try { CTRL.reactor.reenter(); } catch (e) { /* */ }\n"
    "      return;\n"
    "    }\n"
    "    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {",
    "  reenter() {   // v3.2.0: en plena prueba, reanuda\n"
    "    if (CTRL && CTRL.reactor && CTRL.reactor.active) {\n"
    "      try { CTRL.reactor.reenter(); } catch (e) { /* */ }\n"
    "      return;\n"
    "    }\n"
    "    if (CTRL && CTRL.impulso && CTRL.impulso.active) {\n"
    "      try { CTRL.impulso.reenter(); } catch (e) { /* */ }\n"
    "      return;\n"
    "    }\n"
    "    if (CTRL && CTRL.arkanoid && CTRL.arkanoid.active) {",
    'export: reenter impulso')

MOD.write_text(src, encoding='utf-8')
print(f'· Módulo escrito: {len(src.splitlines())} líneas (+{n_ediciones} ediciones)\n')

# ── 15. manifest.json → v9 ───────────────────────────────────────────────────
man = json.loads(MAN.read_text(encoding='utf-8'))
man['version'] = 9
man['description']['es'] = ('El camino completo: 2 duelos, el REACTOR DE ENERGÍA INESTABLE, '
                            'el REACTOR DE IMPULSO (cubos cuánticos, pistola láser, dianas y '
                            'perturbaciones) y el DUELO FINAL contra el ASTRO a bordo de su estación espacial.')
man['description']['en'] = ('The full path: 2 duels, the UNSTABLE POWER REACTOR, the IMPULSE REACTOR '
                            '(quantum cubes, laser pistol, targets and perturbations) and the FINAL DUEL '
                            'against the ASTRO aboard his space station.')
st3 = man['stages'][3]
st3['id'] = 'impulso'
st3['kind'] = 'impulso'
st3['name'] = 'Reactor de impulso'
st3['nota'] = ('v3.4.0: destruye los cubos cuánticos con la pelota (3 oleadas de 3/5/7, 120 s cada una) '
               'desde la base flotante y desata perturbaciones (Gravedad 0, Atractor, Supergravedad) '
               'acertando las dianas con el láser. Sustituye al ARKANOID II (muro2).')
man['assets'] = man['assets'] + ', REACTOR DE IMPULSO: reactor_impulso/ con 6 imágenes de la sala del dueño (frente/fondo/techo/suelo JPG + izquierda/derecha PNG), diana_quantica.png, base.png y pantallainfo.png'
man['notes'].append('2026-10-18 v3.4.0-IMP1: la etapa 4 del camino es el REACTOR DE IMPULSO (mecánica del dueño): sala propia de 6 imágenes, núcleo azul/rojo, 3 oleadas de cubos cuánticos (3/5/7, 120 s independientes) destruidos con la pelota desde la base flotante (sin mesa), pistola láser contra dianas cuánticas (1 s visibles / 1 s de espera) que desatan perturbaciones (Gravedad 0, Atractor con destrucción en cadena, Supergravedad) con cambio automático cada 30 s, pantalla suspendida del techo con oleada/tiempo/cubos/estado/perturbación, ventanas con velocidad lumínica, y derrota con astro_laughing frente al jugador. El ARKANOID II queda fuera del camino.')
MAN.write_text(json.dumps(man, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print('· manifest.json → v9 (stages[3] = impulso)\n')

# ── 16. game.html → 3.4.0-IMP1 ───────────────────────────────────────────────
game = GAME.read_text(encoding='utf-8')
k = len(re.findall(r"^  const VERSION = '3\.3\.0-NUC1';.*$", game, flags=re.M))
if k != 1:
    sys.exit(f'FALLO (game.html VERSION): {k} líneas de versión')
nueva_ver = ("  const VERSION = '3.4.0-IMP1';   // v3.4.0-IMP1 · REACTOR DE IMPULSO (IMP1): NUEVA ETAPA 4 "
             "del campeonato Estación Orbital (mecánica del dueño) — sala propia de 6 imágenes del dueño SIN mesa "
             "(BASE FLOTANTE base.png como punto de reposición de la pelota) · núcleo del reactor ESTABLE azul / "
             "INESTABLE rojo con rotación caótica, alarma y expulsión de CUBOS CUÁNTICOS (3/5/7 · oleadas de 120 s "
             "independientes) · destrucción por golpeo REAL de la pelota (integración por subpasos + barrido del "
             "segmento prev→cur, bumper con la velocidad de la pala, patrón REACTOR) con fragmentación en cubitos "
             "visuales · PISTOLA LÁSER (pistol.glb, pegamento del muro reutilizado; FIX: el export del módulo nunca "
             "exponía gunArmed/fireGun y el gatillo no llegaba) contra DIANAS cuánticas (diana_quantica.png, ciclo "
             "1 s visible / 1 s de espera) que desatan PERTURBACIONES: Gravedad 0 / Atractor (un golpe destruye TODOS "
             "los cubos agrupados) / Supergravedad, con cambio automático cada 30 s INDEPENDIENTE del disparo · "
             "ventanas laterales con viaje a velocidad lumínica (estrellas con estelas del centro afuera, el mismo "
             "efecto en ambas) · PANTALLA suspendida del techo (pantallainfo.png + capa de texto): oleada, tiempo, "
             "cubos restantes, estado del reactor y perturbación activa · derrota = astro_laughing frente al jugador "
             "y regreso a la sala (etapa 1) · hereda íntegro v3.3.0-NUC1 (Reactor de energía inestable en la etapa 2) "
             "· (la CCD SDF de v3.1.2-CCD1 queda intacta) · física del núcleo sin cambios")
game = re.sub(r"^  const VERSION = '3\.3\.0-NUC1';.*$", nueva_ver.replace('\\', '\\\\'), game, count=1, flags=re.M)
game = game.replace('>V3.3.0-NUC1</span>', '>V3.4.0-IMP1</span>')
GAME.write_text(game, encoding='utf-8')
print('· game.html → 3.4.0-IMP1 (VERSION + badge)')
print(f'\nOK: {n_ediciones} ediciones en el módulo + manifest v9 + game.html IMP1')
