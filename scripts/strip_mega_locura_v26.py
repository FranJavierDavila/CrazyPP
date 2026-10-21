#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3.6.34 · Retira la MEGA PALA interna del módulo locura (v26).

La Mega Pala pasa a ser NORMATIVA del NÚCLEO (game.html): carga por rally
de 11+ golpes, icono sobre el mango + jingle, gatillo voluntaria, FX del
canto/onda y conmutador «Pala Mejorada». El módulo ya no guarda estado ni
pinta FX de pala (adiós núcleo dorado, halo, aro, chispas y recarga a tiempo).

Cada corte verifica su marcador ÚNICO antes de aplicar; si algo no cuadra,
aborta SIN escribir (idempotente: si el marker ya no existe, se salta).
"""
import sys
from pathlib import Path

F = Path('/home/z/my-project/public/championships/locura/index.js')
src = F.read_text(encoding='utf-8')
orig = src
n_ediciones = 0


def cortar_entre(ini: str, fin: str, mantener_fin: bool = True,
                 obligatorio: bool = True) -> None:
    """Borra desde la línea que contiene `ini` (incluida) hasta la que
    contiene `fin` (excluida si mantener_fin, incluida si no)."""
    global src, n_ediciones
    if ini not in src:
        if obligatorio:
            sys.exit(f'ABORTA: marker INI no encontrado: {ini[:70]!r}')
        return
    if src.count(ini) != 1:
        sys.exit(f'ABORTA: marker INI no es único ({src.count(ini)}): {ini[:70]!r}')
    i = src.index(ini)
    j = src.find(fin, i)
    if j < 0:
        sys.exit(f'ABORTA: marker FIN no encontrado tras INI: {fin[:70]!r}')
    src = src[:i] + src[j if mantener_fin else j + len(fin):]
    n_ediciones += 1


def sustituir(viejo: str, nuevo: str) -> None:
    global src, n_ediciones
    if viejo not in src:
        sys.exit(f'ABORTA: bloque no encontrado: {viejo[:70]!r}')
    if src.count(viejo) != 1:
        sys.exit(f'ABORTA: bloque no es único ({src.count(viejo)}): {viejo[:70]!r}')
    src = src.replace(viejo, nuevo)
    n_ediciones += 1


# 1) playerPower → referencia histórica de la norma
sustituir(
    "  playerPower: { kind: 'mega_pala', reachMul: 1.38, duration: 8.0, trigger: 'crazy_combo_rally6' },",
    "  // v3.6.34: el PODER DE PALA es NORMATIVA del núcleo (MEGA PALA en\n"
    "  // todos los campeonatos: rally de 11+ golpes la carga, gatillo la\n"
    "  // suelta). Línea histórica — el módulo ya no implementa nada.\n"
    "  playerPower: { kind: 'mega_pala', reachMul: 1.38, duration: 8.0, trigger: 'norma_rally11' },")

# 2) constantes del modelo viejo → nota de la norma
sustituir(
    """// v3.6.33 · MEGA PALA 2.0 «NÚCLEO DE ENERGÍA» — constantes del nuevo modelo.
//  · USO VOLUNTARIO: el gatillo LIBERA la carga (bola en juego); el saque
//    sigue siendo del saque. Recarga automática a los MEGA_RECARGA segundos
//    de terminar el efecto.
//  · CRAZY COMBO (rally 6 ganado) = RECARGA INSTANTÁNEA (premio de siempre).
//  · El NÚCLEO dorado vive en la garganta de la pala TODO el partido
//    (dormida = tenue · cargada = brillante) — el jugador SIEMPRE sabe que
//    tiene el poder y cuándo puede soltarlo.
const MEGA_RECARGA = 14;      // s de recarga tras agotar el efecto
const MEGA_ESCALA = 1.3;      // ×1,30 visual de la montura (física intacta)
const MEGA_SHOCK_T = 0.55;    // s de vida de la onda de choque al liberar
""",
    """// v3.6.34 · la MEGA PALA vive en el NÚCLEO (MEGA PALA NORMATIVA): carga
// por rally de 11+ golpes, ICONO sobre el mango + jingle propio, gatillo
// voluntaria y conmutador «Pala Mejorada» en AJUSTES. Aquí ya no quedan
// constantes ni FX de pala (adiós núcleo dorado, halo, aro y chispas).
""")

# 3) init del estado mega en el constructor
sustituir(
    """    // mega pala
    this._BASE_HIT = DIMS.hitAssistRadius;
    this._megaT = 0;
    // v3.6.33 · MEGA PALA 2.0 «NÚCLEO DE ENERGÍA»: modelo de 3 estados.
    //  DORMIDA (poder en propiedad, sin carga) · CARGADA (gatillo la libera)
    //  · ACTIVA (_megaT > 0, 8 s). La recarga corre sola (MEGA_RECARGA s) y
    //  el CRAZY COMBO la llena al instante. _megaMatch arma la carga al
    //  empezar CADA partido (el dueño la usa cuando quiere, no cuando toca).
    this._megaS = 0;         // escala visual actual de la montura de pala
    this._megaWarn = false;  // aviso «el poder se agota» ya disparado
    this._megaFx = null;     // [fx0, fx1] canto+núcleo+chispas por montura
    this._megaFxOn = false;  // la energía está VIVA (evita loops por frame)
    this._megaReady = false; // CARGADA: el gatillo puede liberarla YA
    this._megaCd = 0;        // segundos restantes de recarga
    this._megaMatch = false; // hay un partido vivo (arma la carga al empezar)
    this._megaFlash = 0;     // destello «lista de nuevo» (decae en el update)
    this._megaHaloTex = null;
    this._megaDotTex = null;
""",
    """    // v3.6.34: la MEGA PALA es NORMATIVA del NÚCLEO (carga por rally de
    // 11+ golpes, icono sobre el mango, gatillo voluntaria) — el módulo
    // ya no guarda estado ni pinta FX de pala (cero duplicados).
""")

# 4) startMatch: cero directo
sustituir(
    "    this.streakAi = 0;\n    this._megaT = 0;\n    this._picandoDone = false;",
    "    this.streakAi = 0;\n    this._picandoDone = false;")

# 5) leave(): dispose del FX viejo fuera
sustituir(
    """    // v3.6.32: MEGA PALA fuera — pala a tamaño 1, radio de siempre y
    // energía retirada con dispose (una sola llamada cubre los 3 estados)
    this._megaFxDispose();
    this._purgeBeams();""",
    "    this._purgeBeams();")

# 6) combo: el Clown reacciona igual; la carga la pone el núcleo en el rally
sustituir(
    """      if (hits >= th.comboRally) {
        // v3.6.33 · CRAZY COMBO = RECARGA INSTANTÁNEA: el uso de la MEGA PALA
        // es VOLUNTARIO (gatillo con la bola en juego), pero el combo mantiene
        // su premio de siempre — llena la carga al momento y, si el efecto ya
        // está activo, le repone los 8 s completos. El Clown se enfada igual.
        this.setState('hungry', 2.6);
        if (this.powers.includes('mega_pala')) {
          if (this._megaT > 0) {
            this._megaT = (this.data && this.data.playerPower &&
              this.data.playerPower.duration) || 8;
            this._megaWarn = false;
          } else {
            this._megaReady = true;
            this._megaCd = 0;
            this._megaFlash = 1;
          }
          this._megaShock();     // la onda celebra la carga (una por montura)
          this.game.rules.message = T('arc_combo');
          try { this.game.audio.playOsc(660, 1320, 0.14, 'square', 0.12, 0); } catch (e) { /* */ }
        } else {
          this.game.rules.message = T('arc_combo_locked');
        }
      } else if (hits >= th.surprisedRally || this.streakP >= 2) {""",
    """      if (hits >= th.comboRally) {
        // v3.6.34 · los rallyes largos SIGUEN poniendo al Clown hambriento,
        // pero la MEGA PALA ya no vive aquí: es NORMATIVA del núcleo y su
        // carga (rally de 11+ golpes) la pone el núcleo EN PLENO RALLYE.
        this.setState('hungry', 2.6);
      } else if (hits >= th.surprisedRally || this.streakP >= 2) {""")

# 7) la sección entera de métodos mega (_megaFxStart … _megaFxDispose)
cortar_entre('  /* ------------ v3.6.33 · MEGA PALA 2.0 — «NÚCLEO DE ENERGÍA» ------------',
             '  update(dt) {')

# 8) el bloque mega dentro de update() (radio, escala, estados y animación)
cortar_entre('    // MEGA PALA (Crazy Combo del jugador con poder desbloqueado)',
             '    // v2.36 · AVISO ANTES DEL PODER')

# 9) export wrapper: fuera megaTrigger
sustituir(
    """  /* ---- PISTOLA (v2.38), BOLA DOBLE (v2.44) y MEGA PALA (v3.6.33) —
   *     enrutados por el núcleo ---- */
  get gunArmed() { return !!(CTRL && CTRL.gunArmed); },
  fireGun(i) { if (CTRL) CTRL.fireGun(i); },
  /** v3.6.33 · GATILLO VOLUNTARIO de la MEGA PALA (bola en juego): el
   *  núcleo lo llama por el puente ChampLoader.megaTrigger; devuelve true
   *  si la pulsación era del poder (liberada / recargando / ya activa). */
  megaTrigger(i) { return !!(CTRL && CTRL.megaTrigger && CTRL.megaTrigger(i)); },""",
    """  /* ---- PISTOLA (v2.38) y BOLA DOBLE (v2.44) — enrutados por el núcleo.
   *     (La MEGA PALA es NORMATIVA del núcleo desde v3.6.34: el módulo ya
   *     no expone megaTrigger ni pinta FX de pala.) ---- */
  get gunArmed() { return !!(CTRL && CTRL.gunArmed); },
  fireGun(i) { if (CTRL) CTRL.fireGun(i); },""")

# 10) comentario del get impl() (citaba la capa QA retirada y el FX viejo)
sustituir(
    """  /** v3.6.32 (ronda 40): acceso de LECTURA al controller para QA —
   *  qa_mega_pala_v3632 sondea el estado del efecto MEGA PALA
   *  (_megaT/_megaFx/escala) sin tocar nada (la capa no escribe). */
  get impl() { return CTRL; },""",
    """  /** Acceso de LECTURA al controller para las capas QA (la capa no
   *  escribe). La MEGA PALA es del núcleo desde v3.6.34. */
  get impl() { return CTRL; },""")

# sanity: no queda ningún residuo mega del módulo EN CÓDIGO (los comentarios
# no cuentan: la historia de la casa se narra en ellos)
import re
codigo = re.sub(r'/\*.*?\*/', '', src, flags=re.S)
codigo = re.sub(r'^\s*//.*$', '', codigo, flags=re.M)
residuos = [m for m in ('_megaFx', '_megaReady', '_megaT', 'MEGA_RECARGA',
                        'MEGA_ESCALA', 'MEGA_SHOCK_T', 'megaTrigger',
                        '_megaShock', '_buildMegaFx', '_BASE_HIT') if m in codigo]
if residuos:
    sys.exit(f'ABORTA: residuos mega en el módulo: {residuos}')

F.write_text(src, encoding='utf-8')
print(f'OK · {n_ediciones} cortes aplicados · {len(orig)} → {len(src)} bytes '
      f'(-{len(orig) - len(src)})')
