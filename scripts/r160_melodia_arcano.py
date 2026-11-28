#!/usr/bin/env python3
# r160 · LA MELODÍA DEL ARCANO VUELVE (informe del dueño: «no se escucha la
# melodía propia de esta sala»).
# CAUSA REPRODUCIDA (sonda r160): hallMute persistido (pp_hallmus=1, icono de
# la pared del salón — un rayo con gatillo puede tocarlo de paso) frena
# setHallWanted ANTES de cargar el buffer: bufs vacío, sin melodía, sin
# ningún aviso. Con la variante por defecto «anfitrion» (sin música) el
# ARCANO es el único sitio donde el mute se notaba.
# FIX: la sala ARCANO queda EXENTA del mute del salón — el icono de la pared
# sigue gobernando la música del salón (variantes), pero la MELODÍA PROPIA
# del Arcano suena siempre (r40 FASE 160: «MELODÍA PROPIA — dentro NO suena
# la pista del salón»). setHallWanted gana el 3.er parámetro ignoraMute.
# Además rearmHallAudio (primer gesto 2D) ya no puede pisar la sala.
import sys

F_C03 = '/home/z/my-project/src/game/core/c03_audio_voz.js'
F_C12 = '/home/z/my-project/src/game/core/c12_pingponggame.js'

with open(F_C03, 'r', encoding='utf-8') as f: c03 = f.read()
with open(F_C12, 'r', encoding='utf-8') as f: c12 = f.read()

P = []


def p(f, old, new, n=1):
    P.append((f, old, new, n))


# ── c03 · setHallWanted: 3.er parámetro ignoraMute ─────────────────────
p(F_C03, """  /** El juego marca la pista que debe sonar ahora (salón abierto). Con
   *  url=null (museo/CABAÑA o salida del salón) se apaga y nada nace. */
  setHallWanted(wanted, url) {
    const w = !!wanted && typeof url === 'string' && !!url;
    const cambioUrl = w && url !== this._hallUrl;
    this._hallUrl = w ? url : this._hallUrl;
    this.hallWanted = w;
    if (!w) { this._menuReq = false; this.stopHallMusic(); return; }   // r149 · F-A1: fuera del salón la recuerda expira
    if (this.hallMute) { this.stopHallMusic(); return; }   // icono: apagada
    if (this.hallPlaying && !cambioUrl) return;            // ya suena la suya
    if (this.hallPlaying && cambioUrl) this.stopHallMusic();  // salón nuevo
    this.startHallMusic();
  }""",
"""  /** El juego marca la pista que debe sonar ahora (salón abierto). Con
   *  url=null (museo/CABAÑA o salida del salón) se apaga y nada nace.
   *  r160 · ignoraMute: la sala ARCANO pide SU melodía propia exenta del
   *  mute del salón (informe del dueño: «no se escucha la melodía propia
   *  de esta sala» — el icono de la pared la silenciaba sin avisar y con
   *  la variante anfitrion era el único lugar donde se notaba). El icono
   *  sigue gobernando las PISTAS DEL SALÓN; la estancia propia manda. */
  setHallWanted(wanted, url, ignoraMute) {
    const w = !!wanted && typeof url === 'string' && !!url;
    const cambioUrl = w && url !== this._hallUrl;
    this._hallUrl = w ? url : this._hallUrl;
    this.hallWanted = w;
    this._hallSinMute = !!ignoraMute && w;
    if (!w) { this._menuReq = false; this._hallSinMute = false; this.stopHallMusic(); return; }   // r149 · F-A1: fuera del salón la recuerda expira
    if (this.hallMute && !this._hallSinMute) { this.stopHallMusic(); return; }   // icono: apagada (r160: la sala exenta pasa)
    if (this.hallPlaying && !cambioUrl) return;            // ya suena la suya
    if (this.hallPlaying && cambioUrl) this.stopHallMusic();  // salón nuevo
    this.startHallMusic();
  }""")

# ── c03 · startHallMusic: guard del mute respeta la exención ───────────
p(F_C03, """      this.kick();
      if (!this.ctx || !this.master || !this.hallWanted || this.hallMute) return;""",
"""      this.kick();
      if (!this.ctx || !this.master || !this.hallWanted ||
          (this.hallMute && !this._hallSinMute)) return;""")

# ── c03 · .then de la carga: mismo respeto ─────────────────────────────
p(F_C03, """      if (this.ctx && this.hallWanted && !this.hallMute &&
          this._hallUrl === url) this.startHallMusic();""",
"""      if (this.ctx && this.hallWanted &&
          !(this.hallMute && !this._hallSinMute) &&
          this._hallUrl === url) this.startHallMusic();""")

# ── c03 · estado inicial del flag (constructor, junto a hallMute) ──────
p(F_C03, """    this.hallMute = false;     // icono de la pared (persistente)
    try { this.hallMute = localStorage.getItem('pp_hallmus') === '1'; } catch { /* */ }""",
"""    this.hallMute = false;     // icono de la pared (persistente)
    try { this.hallMute = localStorage.getItem('pp_hallmus') === '1'; } catch { /* */ }
    this._hallSinMute = false; // r160: la sala ARCANO suena aunque el salón esté mudo""")

# ── c12 · _arconoEntrar: pide la melodía EXENTA ────────────────────────
p(F_C12, """      try { this.audio.setHallWanted(true, 'assets/hall/arcano.mp3'); } catch (eArcM1) { /* */ }""",
"""      // r160 · melodía PROPIA exenta del mute del salón (informe del
      // dueño: «no se escucha la melodía propia de esta sala»): el 3.er
      // parámetro la pasa aunque el icono de la pared tenga el salón mudo.
      try { this.audio.setHallWanted(true, 'assets/hall/arcano.mp3', true); } catch (eArcM1) { /* */ }""")

# ── c12 · rearmHallAudio: nunca pisa la sala (cinturón y tirantes) ─────
p(F_C12, """  rearmHallAudio() {
    try {
      this.audio.ensure();
      const hv = this._hallVarDef();""",
"""  rearmHallAudio() {
    try {
      if (this._arconoOn) return;   // r160: dentro del Arcano manda SU pista
      this.audio.ensure();
      const hv = this._hallVarDef();""")

# ── aplicar ────────────────────────────────────────────────────────────
B = {F_C03: c03, F_C12: c12}
mal = []
for i, (f, old, new, n) in enumerate(P):
    c = B[f].count(old)
    if c != n:
        mal.append((i, f.split('/')[-1], c, n))
if mal:
    for i, nom, c, n in mal:
        print(f"✗ parche {i} [{nom}]: {c} coincidencias (esperaba {n})")
    sys.exit(1)
for f, old, new, _ in P:
    B[f] = B[f].replace(old, new)
for f, s in B.items():
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(s)
    print(f"✓ {f.split('/')[-1]}: {len(s)} bytes")

ch3 = B[F_C03]
assert ch3.count('_hallSinMute') >= 4, 'faltan guards _hallSinMute'
assert "setHallWanted(true, 'assets/hall/arcano.mp3', true)" in B[F_C12]
print('✓ exención del mute: 4 puntos en c03 + llamada exenta en c12 + guard rearmHallAudio')
