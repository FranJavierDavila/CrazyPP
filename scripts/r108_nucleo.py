#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r108 · NÚCLEO — los cinco encargos del dueño:

1 · CLONACIÓN: los clones dejan de ESPEJAR la pala — puestos fijos de
    guardia + intercepción con el predictor REAL (predictStrike RK4) y
    acierto SIEMPRE (CLON_EXITO 1.0): verdaderos campeones asistentes.
2 · BOLA LOCA: su tarjeta del Arcano recibe descripción y métricas
    (arc_desc_bolaloca / arc_met_bolaloca — faltaban).
3 · HALLS: el panel 3D «PICK A HALL» tenía los rects hallv:<id> SIN caso
    en el dispatcher (por eso «disponibles pero no se pueden
    seleccionar») — case 'hallv' con caída al caso hall_var.
4 · SUPER CRIPTONITA: poder 16.º del registro, 12 s — bola verde
    fosforito pulsante, estela verde (firma), cristales 1-5 (20-50 cm)
    al botar en la mesa rival, romper = freno 1/3 + dirección aleatoria.
    Icono DEL DUEÑO (SuperPala_Criptonita.png, cuantizado a 256).
5 · Cometa: la fábrica vive en c07 (r108_c07_cometa_cristales.py).
"""
import base64
import io
import os

from PIL import Image

R = '/home/z/my-project/src/game/core/'

# ── icono del dueño → PNG cuantizado a 256 colores → base64 ──────────
im = Image.open('/home/z/my-project/upload/SuperPala_Criptonita.png').convert('RGBA')
im_q = im.quantize(colors=256, method=Image.FASTOCTREE)
buf = io.BytesIO()
im_q.save(buf, 'PNG', optimize=True)
kb = buf.tell() / 1024
B64 = base64.b64encode(buf.getvalue()).decode('ascii')
print(f"icono cripto: {im.size} → {kb:.0f} KB cuantizado")

# ════════════════════ c02 · ventana cripto 12 s ═════════════════════
c02 = io.open(R + 'c02_cfg_escena.js', encoding='utf-8').read()

def edit(txt, old, new, tag, cnt=1):
    assert old in txt, f"{tag}: ancla NO encontrada"
    assert txt.count(old) == cnt, f"{tag}: ancla ambigua ({txt.count(old)})"
    return txt.replace(old, new)

c02 = edit(c02,
  "                    // SIEMPRE desbloqueada, primer puesto del Arcano)\n"
  "    dlGigante: 12,  // DUELOS LOCOS · GIGANTE (r84)",
  "                    // SIEMPRE desbloqueada, primer puesto del Arcano)\n"
  "    cripto: 12,     // r108 · SUPER CRIPTONITA (12 s — spec del dueño)\n"
  "    dlGigante: 12,  // DUELOS LOCOS · GIGANTE (r84)",
  "c02 ventana cripto")
io.open(R + 'c02_cfg_escena.js', 'w', encoding='utf-8').write(c02)
print("c02: ARCANO_CFG.ventanas.cripto = 12 ✓")

# ════════════════════ c12 · el corazón de la ronda ══════════════════
c12 = io.open(R + 'c12_pingponggame.js', encoding='utf-8').read()
n0 = len(c12)

# 1 · import de los cristales
c12 = edit(c12,
  "createNubePrismas, createOndaEsfera, createRoom",
  "createCristalesCripto, createNubePrismas, createOndaEsfera, createRoom",
  "1 import cristales")

# 2 · campos nuevos
c12 = edit(c12,
  "    this._clonFx = null;              // [clonIzq, clonDer] grupos fantasma\n"
  "    this._clonFxOn = false;",
  "    this._clonFx = null;              // [clonIzq, clonDer] grupos fantasma\n"
  "    this._clonFxOn = false;\n"
  "    // r108 · SUPER CRIPTONITA (12 s): bola verde fosforito pulsante +\n"
  "    // cristales de cuarzo veteados que brotan en la mesa del rival.\n"
  "    this._criptoT = 0;                // s restantes de ventana cripto\n"
  "    this._criptoWarn = false;\n"
  "    this._criptoTickN = 0;\n"
  "    this._criptoTint = null;          // tinta original de la bola (restaurar)\n"
  "    this.cristalesCripto = null;      // pool de cristales (c07)\n"
  "    // r108 · los ASISTENTES del clon: predicción compartida + pose propia\n"
  "    this._clonPredicT = 0;\n"
  "    this._clonPredicP = null;\n"
  "    this._clonPoseQ = null;",
  "2 campos")

# 3 · firma verde del cripto
c12 = edit(c12,
  "  ancla: [1.0, 0.78, 0.25],     // Ancla — oro de las cadenas\n};",
  "  ancla: [1.0, 0.78, 0.25],     // Ancla — oro de las cadenas\n"
  "  // r108 (v3.6.206) · SUPER CRIPTONITA — verde fosforito del dueño\n"
  "  cripto: [0.42, 1.0, 0.45],\n};",
  "3 firma cripto")

# 4 · el icono del dueño, cuantizado (const justo antes del registro)
c12 = edit(c12,
  "const PODERES_PALA = [",
  "// r108 · SUPER CRIPTONITA — icono DEL DUEÑO (SuperPala_Criptonita.png,\n"
  "// cuantizado a 256 colores, mismo cauce que el resto de insignias).\n"
  f"const PNG_PODER_CRIPTO = 'data:image/png;base64,{B64}';\n\n"
  "const PODERES_PALA = [",
  "4 icono const")

# 5 · entrada en el registro (el último — patrón de la casa)
c12 = edit(c12,
  "  { id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),\n"
  "    voz: VOZ_PODER_BOLALOCA, vozEn: VOZ_PODER_BOLALOCA_EN, png: PNG_PODER_BOLALOCA },\n"
  "];",
  "  { id: 'bolaloca', dur: ARCANO_CFG.ventanas.bolaloca, nombre: () => T('poder_bolaloca'),\n"
  "    voz: VOZ_PODER_BOLALOCA, vozEn: VOZ_PODER_BOLALOCA_EN, png: PNG_PODER_BOLALOCA },\n"
  "  // r108 (v3.6.206) · SUPER CRIPTONITA (16.º poder — ENTRA AL FINAL,\n"
  "  // patrón de la casa): 12 s de bola verde fosforito pulsante con\n"
  "  // estela verde (anula la estela por defecto) que se disipa a ~50 cm;\n"
  "  // cada bote en la mesa del RIVAL siembra 1-5 cristales de cuarzo\n"
  "  // veteados (20-50 cm) que la bola ROMPE al chocar: freno a 1/3 y\n"
  "  // dirección totalmente aleatoria. Icono DEL DUEÑO.\n"
  "  { id: 'cripto', dur: ARCANO_CFG.ventanas.cripto, nombre: () => T('poder_cripto'),\n"
  "    png: PNG_PODER_CRIPTO },\n"
  "];",
  "5 registro")

# 6 · tipo en la ficha del Arcano
c12 = edit(c12,
  "  bolaloca: ['arcono_tipo_distraccion', '#c39bff'],   // FASE 160: caos de bola",
  "  bolaloca: ['arcono_tipo_distraccion', '#c39bff'],   // FASE 160: caos de bola\n"
  "  cripto: ['arcono_tipo_ataque', '#6cff8a'],          // r108: cristales de kryptonita",
  "6 tipo ficha")

# 7 · despacho del gatillo
c12 = edit(c12,
  "    this._megaActivaMia = true;   // r107: esta ventana la arma YO\n"
  "    if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent); // FASE 160",
  "    this._megaActivaMia = true;   // r107: esta ventana la arma YO\n"
  "    if (ent.id === 'cripto') return this._criptoTrigger(ent);   // r108\n"
  "    if (ent.id === 'bolaloca') return this._bolalocaTrigger(ent); // FASE 160",
  "7 dispatcher")

# 8 · poderes vivos (la regla del dueño: SOLO 1 poder en marcha)
c12 = edit(c12,
  "      ['onda', '_ondaT'], ['salva', '_salvaT'], ['ancla', '_anclaT']];",
  "      ['onda', '_ondaT'], ['salva', '_salvaT'], ['ancla', '_anclaT'],\n"
  "      ['cripto', '_criptoT']];",
  "8 poder vivo")

# 9 · el icono cede a su efecto (misma lectura que el resto)
c12 = edit(c12,
  "    if (ent.id === 'bolaloca') return this._bolalocaT > 0;   // FASE 160",
  "    if (ent.id === 'bolaloca') return this._bolalocaT > 0;   // FASE 160\n"
  "    if (ent.id === 'cripto') return this._criptoT > 0;       // r108",
  "9 sel activa")

# 10 · tick de ventana (tras el bloque del clon, mismo patrón)
c12 = edit(c12,
  "      } else if (this._clonT < 1 && (this._clonTickN || 0) < 3) {\n"
  "        this._clonTickN = 3;\n"
  "        this._poderTickBlip(3);\n"
  "      }\n"
  "    }",
  "      } else if (this._clonT < 1 && (this._clonTickN || 0) < 3) {\n"
  "        this._clonTickN = 3;\n"
  "        this._poderTickBlip(3);\n"
  "      }\n"
  "    }\n"
  "    // r108 · SUPER CRIPTONITA: ventana PROPIA de 12 s (spec del dueño).\n"
  "    if (pwViva(this._criptoT)) {\n"
  "      this._criptoT -= dt;\n"
  "      if (this._criptoT <= 0) {\n"
  "        this._criptoFin();               // fin natural (12 s agotados)\n"
  "      } else if (this._criptoT < 2 && !this._criptoWarn) {\n"
  "        this._criptoWarn = true;\n"
  "        this._poderTickBlip(2);          // v3.6.43: cuenta sonora uniforme\n"
  "      } else if (this._criptoT < 3 && (this._criptoTickN || 0) < 1) {\n"
  "        this._criptoTickN = 1;\n"
  "        this._poderTickBlip(1);\n"
  "      } else if (this._criptoT < 1 && (this._criptoTickN || 0) < 3) {\n"
  "        this._criptoTickN = 3;\n"
  "        this._poderTickBlip(3);\n"
  "      }\n"
  "    }",
  "10 tick ventana")

# 11 · cortina de poderes en pruebas: la cripto también se recoge
c12 = edit(c12,
  "    if (this._ondaT > 0) {\n"
  "      this._ondaT = 0; this._ondaWarn = false; this._ondaTickN = 0;\n"
  "      this._ondaFlojoT = 0; this._ondaShakeT = 0;\n"
  "      try { this._ondaFin(); } catch (eO33) { /* */ }\n"
  "    }",
  "    if (this._ondaT > 0) {\n"
  "      this._ondaT = 0; this._ondaWarn = false; this._ondaTickN = 0;\n"
  "      this._ondaFlojoT = 0; this._ondaShakeT = 0;\n"
  "      try { this._ondaFin(); } catch (eO33) { /* */ }\n"
  "    }\n"
  "    if (this._criptoT > 0) {\n"
  "      this._criptoT = 0; this._criptoWarn = false; this._criptoTickN = 0;\n"
  "      try { this._criptoFin(); } catch (eCr33) { /* */ }\n"
  "    }",
  "11 cortina pruebas")

# 12 · frame de la cripto (junto al frame del clon)
c12 = edit(c12,
  "    if (this._clonT > 0) {\n"
  "      try { this._clonFrame(dt); } catch (eCF) { /* el clon nunca tumba el frame */ }\n"
  "    } else if (this._clonFxOn) {\n"
  "      this._clonVis(false);\n"
  "    }",
  "    if (this._clonT > 0) {\n"
  "      try { this._clonFrame(dt); } catch (eCF) { /* el clon nunca tumba el frame */ }\n"
  "    } else if (this._clonFxOn) {\n"
  "      this._clonVis(false);\n"
  "    }\n"
  "    // r108 · SUPER CRIPTONITA: pulso fosforito de la bola + cristales\n"
  "    // vivos (crecen, brillan y chocan con la bola — romperlos la frena\n"
  "    // a 1/3 y la despide en dirección aleatoria, spec del dueño).\n"
  "    if (this._criptoT > 0) {\n"
  "      try { this._criptoFrame(dt); }\n"
  "      catch (eCrFr) { /* la criptonita nunca tumba el frame */ }\n"
  "    }",
  "12 frame cripto")

# 13 · cosecha de cristales al botar en la mesa rival (tras el bote sorpresa)
c12 = edit(c12,
  "              break;             // un bote sorpresivo por frame basta\n"
  "            }\n"
  "          }",
  "              break;             // un bote sorpresivo por frame basta\n"
  "            }\n"
  "          }\n"
  "          // r108 · SUPER CRIPTONITA: la bola verde que BOTA en la mesa\n"
  "          // del rival hace crecer 1-5 cristales de cuarzo veteados\n"
  "          // (20-50 cm, aleatorio) en el punto del bote — obstáculos\n"
  "          // REALES que luego la bola puede romper (spec del dueño).\n"
  "          if (this._criptoT > 0 && this.cristalesCripto) {\n"
  "            for (const eC of this.events) {\n"
  "              if (eC.type !== 'table' || eC.side !== 'ai' || eC.edge) continue;\n"
  "              try { this.cristalesCripto.nace(eC.pos, DIMS.tableTopY); }\n"
  "              catch (eCrN) { /* */ }\n"
  "              try { this.audio.playOsc(620, 1240, 0.22, 'triangle', 0.12, 0); }\n"
  "              catch (eCrN2) { /* */ }\n"
  "              break;             // una cosecha de cristales por frame\n"
  "            }\n"
  "          }",
  "13 cosecha cristales")

# 14 · los métodos del cripto (tras _ondaEsferaMuere de la r107)
c12 = edit(c12,
  "  _ondaEsferaMuere() {\n"
  "    try { this.ondaEsfera.muere(); } catch (eOM1) { /* */ }\n"
  "    try { this.audio.playOsc(110, 40, 0.18, 'sawtooth', 0.16, 0); } catch (eOM2) { /* */ }\n"
  "    try { this.audio.playNoise(0.14, 210, 0.3, 0.12, 0, 'lowpass'); } catch (eOM3) { /* */ }\n"
  "  }\n",
  "  _ondaEsferaMuere() {\n"
  "    try { this.ondaEsfera.muere(); } catch (eOM1) { /* */ }\n"
  "    try { this.audio.playOsc(110, 40, 0.18, 'sawtooth', 0.16, 0); } catch (eOM2) { /* */ }\n"
  "    try { this.audio.playNoise(0.14, 210, 0.3, 0.12, 0, 'lowpass'); } catch (eOM3) { /* */ }\n"
  "  }\n"
  "\n"
  "  /* ==================================================================\n"
  "   *  r108 · SUPER CRIPTONITA (petición literal del dueño, 12 s): «La\n"
  "   *  bola se convierte en un verde fosforito pulsante de luz verde. Su\n"
  "   *  estela es verde (anula la estela por defecto) dejando un rastro\n"
  "   *  de luz verde en su recorrido que se desvanece a ~50 cm. Cuando la\n"
  "   *  bola golpea la mesa en la zona rival hace crecer de uno a hasta 5\n"
  "   *  cristales de cuarzo verdosos veteados (20-50 cm, aleatorio) sobre\n"
  "   *  la superficie de la mesa del rival. Si la bola golpea los\n"
  "   *  cristales los rompe en pedacitos pero se frena a 1/3 de su\n"
  "   *  velocidad y sale en una dirección completamente aleatoria».\n"
  "   *  La estela verde la da la FIRMA (TRAIL_PODER.cripto) — el cometa\n"
  "   *  r107/r108 y la estela-línea la leen solas.\n"
  "   *  ================================================================== */\n"
  "  _criptoTrigger(ent) {\n"
  "    if (this._criptoT > 0) {\n"
  "      // refresco honesto (patrón clon/onda): la ventana vuelve a 12 s\n"
  "      this._criptoT = CRIPTO_DUR;\n"
  "      this._criptoWarn = false;\n"
  "      this._criptoTickN = 0;\n"
  "      this._megaActivaId = 'cripto';\n"
  "      this._megaActivaDur = CRIPTO_DUR;\n"
  "      this._megaTexDirty = true;\n"
  "      this.rules.message = T('arc_cripto_go');\n"
  "      return true;\n"
  "    }\n"
  "    if (!this._megaMatriz.find((x) => x.id === 'cripto')) return false;\n"
  "    this._megaGasta(ent);\n"
  "    this._criptoT = CRIPTO_DUR;\n"
  "    this._criptoWarn = false;\n"
  "    this._criptoTickN = 0;\n"
  "    this._megaActivaId = 'cripto';\n"
  "    this._megaActivaDur = CRIPTO_DUR;\n"
  "    this._megaTexDirty = true;\n"
  "    if (!this.cristalesCripto) {\n"
  "      try {\n"
  "        this.cristalesCripto = createCristalesCripto();\n"
  "        this.rig.add(this.cristalesCripto.group);\n"
  "      } catch (eCC2) { this.cristalesCripto = null; }\n"
  "    }\n"
  "    try { this._criptoTintAplicar(); } catch (eCT2) { /* */ }\n"
  "    // firma: el cristal despierta (dos voces ascendentes)\n"
  "    try { this.audio.playOsc(220, 880, 0.25, 'triangle', 0.14, 0); } catch (e) { /* */ }\n"
  "    try { this.audio.playOsc(440, 1320, 0.3, 'sine', 0.1, 0.08); } catch (e2) { /* */ }\n"
  "    this.rules.message = T('arc_cripto_go');\n"
  "    if (this.renderer.xr && this.renderer.xr.isPresenting) {\n"
  "      try { this.haptic(this.paddleHand, 0.7, 120); } catch (e3) { /* */ }\n"
  "    }\n"
  "    return true;\n"
  "  }\n"
  "\n"
  "  /** r108 · LA BOLA KRYPTONITA: verde fosforito con emisivo verde que\n"
  "   *  PULSA (el frame lo modula). Guarda la tinta original y la restaura\n"
  "   *  al acabar — mismo patrón de la oscuridad (r29) y la brasa del\n"
  "   *  fénix; cede la bola si otro poder la viste. */\n"
  "  _criptoTintAplicar() {\n"
  "    const m = this.ballMesh;\n"
  "    if (!m || !m.material || this._criptoTint) return;\n"
  "    try { if (this._oscuridadTint) this._oscuridadTintRestaurar(); } catch (eC0) { /* */ }\n"
  "    try { if (this._prismaBolaTint) this._prismaBolaTintRestaurar(); } catch (eC1) { /* */ }\n"
  "    this._criptoTint = {\n"
  "      col: m.material.color.getHex(),\n"
  "      em: m.material.emissive ? m.material.emissive.getHex() : null,\n"
  "      ei: m.material.emissiveIntensity != null ? m.material.emissiveIntensity : null,\n"
  "    };\n"
  "    m.material.color.setHex(0x53ff6e);          // verde fosforito\n"
  "    if (m.material.emissive) m.material.emissive.setHex(0x1fd94e);\n"
  "    if (m.material.emissiveIntensity != null) m.material.emissiveIntensity = 1.1;\n"
  "  }\n"
  "\n"
  "  _criptoTintRestaurar() {\n"
  "    if (!this._criptoTint) return;\n"
  "    const f = this._criptoTint;\n"
  "    this._criptoTint = null;\n"
  "    const m = this.ballMesh;\n"
  "    if (!m || !m.material) return;\n"
  "    m.material.color.setHex(f.col);\n"
  "    if (m.material.emissive && f.em != null) m.material.emissive.setHex(f.em);\n"
  "    if (m.material.emissiveIntensity != null && f.ei != null) {\n"
  "      m.material.emissiveIntensity = f.ei;\n"
  "    }\n"
  "  }\n"
  "\n"
  "  /** r108 · FRAME de la criptonita: pulso de la bola + cristales vivos\n"
  "   *  (crecen, pulsan) + COLISIÓN: la bola que choca con un cristal lo\n"
  "   *  ROMPE en pedacitos, se frena a 1/3 y sale en dirección totalmente\n"
  "   *  aleatoria e impredecible (spec literal del dueño). */\n"
  "  _criptoFrame(dt) {\n"
  "    const m = this.ballMesh;\n"
  "    if (m && m.material && this._criptoTint &&\n"
  "        m.material.emissiveIntensity != null) {\n"
  "      const ph = performance.now() * 0.001;\n"
  "      m.material.emissiveIntensity =\n"
  "        0.75 + 0.55 * (0.5 + 0.5 * Math.sin(ph * 9.4));   // pulso vivo\n"
  "    }\n"
  "    if (!this.cristalesCripto) return;\n"
  "    try { this.cristalesCripto.update(dt); } catch (eCrU) { /* */ }\n"
  "    const b = this.ball;\n"
  "    if (!(b && b.pos && b.vel && this.rules &&\n"
  "          this.rules.state === 'rally' && b.pos.z < DIMS.tableCenterZ)) return;\n"
  "    let iCol = -1;\n"
  "    try { iCol = this.cristalesCripto.colisiona(b.pos, DIMS.ballRadius); }\n"
  "    catch (eCrC) { iCol = -1; }\n"
  "    if (iCol < 0) return;\n"
  "    const pR = b.pos.clone();\n"
  "    try { this.cristalesCripto.rompe(iCol); } catch (eCrR) { /* */ }\n"
  "    try { this.chispas.burst(pR, TRAIL_PODER.cripto); } catch (eCrB) { /* */ }\n"
  "    try { this.chispas.burst(pR, TRAIL_PODER.cripto); } catch (eCrB2) { /* */ }\n"
  "    // freno a 1/3 + dirección COMPLETAMENTE ALEATORIA (azimut y\n"
  "    // elevación al azar — ni la IA ni el dueño pueden preleerla)\n"
  "    const sp3 = Math.max(1.2, b.vel.length() / 3);\n"
  "    const az = Math.random() * Math.PI * 2;\n"
  "    const el = 0.18 + Math.random() * 0.55;\n"
  "    b.vel.set(Math.cos(az) * Math.cos(el) * sp3, Math.sin(el) * sp3,\n"
  "      Math.sin(az) * Math.cos(el) * sp3);\n"
  "    try { this.audio.playOsc(1400, 300, 0.2, 'square', 0.14, 0); } catch (eCrS) { /* */ }\n"
  "    try { this.audio.playNoise(0.18, 2400, 0.5, 0.12, 0, 'highpass'); } catch (eCrS2) { /* */ }\n"
  "    this.rules.message = T('cripto_rompe');\n"
  "    if (this.renderer.xr && this.renderer.xr.isPresenting) {\n"
  "      try { this.haptic(this.paddleHand, 0.5, 70); } catch (eCrH) { /* */ }\n"
  "    }\n"
  "  }\n"
  "\n"
  "  /** r108 · Fin de la ventana: la bola vuelve a su tinta y los\n"
  "   *  cristales vivos se deshacen (la mesa queda limpia). */\n"
  "  _criptoFin() {\n"
  "    this._criptoT = 0;\n"
  "    this._criptoTintRestaurar();\n"
  "    if (this.cristalesCripto) {\n"
  "      try { this.cristalesCripto.fin(); } catch (eCrF) { /* */ }\n"
  "    }\n"
  "    this.rules.message = T('arc_cripto_fin');\n"
  "    try { this.audio.playOsc(880, 220, 0.2, 'triangle', 0.12, 0); } catch (e) { /* */ }\n"
  "  }\n",
  "14 métodos cripto")

# 15 · HALLS: el caso que faltaba (los rects hallv:<id> caían al vacío)
c12 = edit(c12,
  "      case 'hall_var': {",
  "      case 'hallv':\n"
  "        // r108 · EL PANEL 3D «PICK A HALL» VUELVE A LA VIDA: sus rects\n"
  "        // hallv:<id> caían al vacío (sin caso en el dispatcher) — por\n"
  "        // eso los salones se VEÍAN disponibles pero NO se podían\n"
  "        // seleccionar (informe del dueño). El arg ya trae el id de la\n"
  "        // variante: cae al MISMO cauce del menú de ajustes (hall_var),\n"
  "        // que ya sabe negarse con candado y mensaje del hito.\n"
  "      case 'hall_var': {",
  "15 caso hallv")

# 16 · CLON: los campeones aciertan SIEMPRE
c12 = edit(c12,
  "const CLON_EXITO = 0.9;     // tasa de acierto de la devolución (90 %)",
  "const CLON_EXITO = 1.0;     // r108 · ASISTENTES CAMPEONES: aciertan SIEMPRE\n"
  "                            // (el dueño: «acertando siempre su golpe»)",
  "16 exito 1.0")
c12 = edit(c12,
  "  /** v3.6.50 · DEVOLUCIÓN del clon (el 90 % de acierto): solver de la",
  "  /** r108 · DEVOLUCIÓN del ASISTENTE (CAMPEÓN: acierta SIEMPRE, antes\n"
  "   *  era el 90 % de v3.6.50): solver de la",
  "16a doc devuelve")
c12 = edit(c12,
  "            this._clonFallada = true;      // UNA tirada por vuelo (el 10 % es real)",
  "            this._clonFallada = true;      // UNA tirada por vuelo (acierta SIEMPRE)",
  "16b doc tirada")
c12 = edit(c12,
  "   *  3) BARRE el confeti en patrulla, 4) CAZA la bola que se escapa por\n"
  "   *  SU lado si el jugador no puede llegar (90 % de éxito). */",
  "   *  3) BARRE el confeti en patrulla, 4) INTERCEPTA y devuelve SIEMPRE\n"
  "   *  la bola que se le escapa al jugador (asistentes campeones r108). */",
  "16c doc frame")

# 17 · CLON: predicción compartida antes del bucle de clones
c12 = edit(c12,
  "    const blancos = this._clonBlancos(_clonBlancosBuf);\n"
  "    const confetiVivo = !!(this.confetti && this.confetti.points.visible &&\n"
  "      this.confettiBurst > 0 && this.confetti.kill);",
  "    const blancos = this._clonBlancos(_clonBlancosBuf);\n"
  "    const confetiVivo = !!(this.confetti && this.confetti.points.visible &&\n"
  "      this.confettiBurst > 0 && this.confetti.kill);\n"
  "    // r108 · PREDICCIÓN compartida (una por frame, cada 0,12 s, sólo\n"
  "    // con bola entrante legal): el predictor REAL de la casa\n"
  "    // (predictStrike, RK4 c05) señala el punto de golpeo en NUESTRO\n"
  "    // campo y SU lado — el asistente campeón corre ANTES de que llegue\n"
  "    // la bola (los clones ya no esperan quietos su 0,32 m de suerte).\n"
  "    let _pred = null;\n"
  "    if (this._clonCd <= 0 && b0 && b0.pos && b0.vel && r &&\n"
  "        r.state === 'rally' && r.lastHitter === 'ai' && b0.vel.z > 0.25) {\n"
  "      this._clonPredicT -= dt;\n"
  "      if (this._clonPredicT <= 0) {\n"
  "        this._clonPredicT = 0.12;\n"
  "        try {\n"
  "          const pr = predictStrike(b0, 1, !!r.validBounce);\n"
  "          this._clonPredicP = pr && pr.point ? pr.point : null;\n"
  "        } catch (eCP) { this._clonPredicP = null; }\n"
  "      }\n"
  "      if (this._clonPredicP) {\n"
  "        const lx = this._clonPredicP.x;\n"
  "        _pred = {\n"
  "          x: lx,\n"
  "          y: this._clonPredicP.y,\n"
  "          z: this._clonPredicP.z,\n"
  "          lado: lx < -0.18 ? -1 : (lx > 0.18 ? 1 : 0),   // el centro es del dueño\n"
  "        };\n"
  "      }\n"
  "    }",
  "17 prediccion")

# 18 · CLON: puestos fijos + intercepción (adiós al espejo)
c12 = edit(c12,
  "      } else {\n"
  "        // GUARDIA: flanquea la pala del jugador a ±CLON_DIST (50 cm)\n"
  "        if (!ps || !ps.pos) continue;\n"
  "        tx = ps.pos.x + lado * CLON_DIST;\n"
  "        ty = ps.pos.y;\n"
  "        tz = ps.pos.z;\n"
  "      }\n"
  "      const kk = 1 - Math.exp(-dt * (blanco ? 3.4 : 10));   // el fantasma va con lag",
  "      } else if (_pred && _pred.lado === lado) {\n"
  "        // r108 · INTERCEPCIÓN: el asistente CORRE al punto de golpeo\n"
  "        // que el predictor real señala en SU lado — verdadero campeón:\n"
  "        // llega antes de que la bola lo haga y la devuelve siempre.\n"
  "        tx = THREE.MathUtils.clamp(_pred.x, -1.25, 1.25);\n"
  "        ty = THREE.MathUtils.clamp(_pred.y, 0.75, 1.5);\n"
  "        tz = THREE.MathUtils.clamp(_pred.z, CLON_Z - 0.25, CLON_Z + 0.3);\n"
  "      } else {\n"
  "        // r108 · PUESTO PROPIO (ya no ESPEJA la pala del dueño — el\n"
  "        // encargo: «no repiten nuestros movimientos, son dos\n"
  "        // asistentes»): cada uno custodia SU mitad con balanceo suave.\n"
  "        tx = lado * CLON_POSTE_X;\n"
  "        ty = CLON_ALTURA + Math.sin(now * 1.1 + (lado > 0 ? 0 : Math.PI)) * 0.06;\n"
  "        tz = CLON_Z;\n"
  "      }\n"
  "      const kk = 1 - Math.exp(-dt * (blanco ? 3.4\n"
  "        : (_pred && _pred.lado === lado ? 14 : 8)));   // el campeón SPRINTA",
  "18 puestos")

# 19 · CLON: orientación propia (capturada al armar, nunca en vivo)
c12 = edit(c12,
  "      // orientación: la base de la pala del jugador (misma pose de hoja)\n"
  "      if (ps && ps.right && ps.up && ps.normal) {\n"
  "        _clonM.makeBasis(ps.right, ps.up, ps.normal);\n"
  "        _clonQ.setFromRotationMatrix(_clonM);\n"
  "        grp.quaternion.copy(_clonQ);\n"
  "      }",
  "      // r108 · orientación PROPIA: pose de guardia capturada al armar\n"
  "      // el poder — los asistentes ya no copian la pose viva del dueño\n"
  "      if (this._clonPoseQ) grp.quaternion.copy(this._clonPoseQ);",
  "19 orientacion")

# 20 · CLON: captura de pose en el gatillo
c12 = edit(c12,
  "    try { this._buildClonFx(); } catch (e) { this._clonFx = null; }\n"
  "    this._clonVis(true);",
  "    try { this._buildClonFx(); } catch (e) { this._clonFx = null; }\n"
  "    // r108 · cada asistente nace con SU pose de guardia (la del dueño\n"
  "    // en el instante de armar, congelada — jamás la copia en vivo)\n"
  "    try {\n"
  "      const psQ = this.controllerPaddles\n"
  "        ? this.controllerPaddles[this.paddleHand | 0] : null;\n"
  "      if (psQ && psQ.right && psQ.up && psQ.normal) {\n"
  "        _clonM.makeBasis(psQ.right, psQ.up, psQ.normal);\n"
  "        this._clonPoseQ = _clonQ.setFromRotationMatrix(_clonM).clone();\n"
  "      }\n"
  "    } catch (eCQ) { this._clonPoseQ = null; }\n"
  "    this._clonPredicT = 0;\n"
  "    this._clonPredicP = null;\n"
  "    this._clonVis(true);",
  "20 pose gatillo")

# 21 · constantes de los puestos de los asistentes
c12 = edit(c12,
  "const CLON_CATCH = 0.32;    // radio de caza alrededor de cada clon (m)",
  "const CLON_CATCH = 0.32;    // radio de caza alrededor de cada clon (m)\n"
  "// r108 · LOS ASISTENTES CAMPEONES: puestos PROPIOS (no espejan la pala\n"
  "// del dueño) y z propio — dos jugadores más que custodian su mitad.\n"
  "const CLON_POSTE_X = 0.62;  // x del puesto de cada asistente (±62 cm)\n"
  "const CLON_ALTURA = 1.02;   // altura de guardia de los asistentes (m)\n"
  "const CLON_Z = DIMS.tableCenterZ + DIMS.tableHalfLength + 0.3;  // su plano",
  "21 puestos const")

# 22 · ventana CRIPTO_DUR junto a CLON_DUR
c12 = edit(c12,
  "const CLON_DUR = ARCANO_CFG.ventanas.clon;        // s de ventana por activación (regla del dueño)",
  "const CLON_DUR = ARCANO_CFG.ventanas.clon;        // s de ventana por activación (regla del dueño)\n"
  "const CRIPTO_DUR = ARCANO_CFG.ventanas.cripto;    // r108 · SUPER CRIPTONITA (12 s)",
  "22 CRIPTO_DUR")

# 23 · la cripto nace DESBLOQUEADA (mismo trato que la Bola Loca)
c12 = edit(c12,
  "      if (ok.indexOf('bolaloca') >= 0 && lista.indexOf('bolaloca') < 0) {\n"
  "        lista.unshift('bolaloca');\n"
  "        try {\n"
  "          localStorage.setItem('pp_poderes_v1', JSON.stringify(lista));\n"
  "        } catch { /* la sesión la lleva en memoria */ }\n"
  "      }\n"
  "      return lista;\n"
  "    } catch { return ['bolaloca']; }",
  "      if (ok.indexOf('bolaloca') >= 0 && lista.indexOf('bolaloca') < 0) {\n"
  "        lista.unshift('bolaloca');\n"
  "        try {\n"
  "          localStorage.setItem('pp_poderes_v1', JSON.stringify(lista));\n"
  "        } catch { /* la sesión la lleva en memoria */ }\n"
  "      }\n"
  "      // r108 · SUPER CRIPTONITA nace DESBLOQUEADO (el dueño lo pide y\n"
  "      // lo juega desde el primer día, mismo trato que la Bola Loca).\n"
  "      if (ok.indexOf('cripto') >= 0 && lista.indexOf('cripto') < 0) {\n"
  "        lista.unshift('cripto');\n"
  "        try {\n"
  "          localStorage.setItem('pp_poderes_v1', JSON.stringify(lista));\n"
  "        } catch { /* la sesión la lleva en memoria */ }\n"
  "      }\n"
  "      return lista;\n"
  "    } catch { return ['bolaloca', 'cripto']; }",
  "23 desbloqueo")

# 24 · la _pred necesita la bola ANTES del bucle: renombro la local
#     (el bloque 17 usa b0 — la declaro junto a blancos)
c12 = edit(c12,
  "    const blancos = this._clonBlancos(_clonBlancosBuf);",
  "    const b0 = this.ball;\n"
  "    const blancos = this._clonBlancos(_clonBlancosBuf);",
  "24 b0")

io.open(R + 'c12_pingponggame.js', 'w', encoding='utf-8').write(c12)
print(f"c12: {len(c12) - n0} bytes · 24 cables r108 aplicados")

# ════════════════════ c00 · textos ES/EN ════════════════════════════
c00 = io.open(R + 'c00_pre_three.js', encoding='utf-8').read()
m0 = len(c00)

ES_NEW = """    arc_met_ancla: 'Inmunidad a poderes rivales · sin bonus activo · 10 s',
    // FASE 160 · la ficha que FALTABA (informe r108 del dueño: «el super
    // poder de bola loca no tiene descripciones y le faltarían por poner
    // en su tarjeta»)
    arc_desc_bolaloca: 'La bola crece y vive su caos: ciclo arcoíris y deriva imprevisible que descoloca a cualquiera y revienta los planes del rival.',
    arc_met_bolaloca: 'Tamaño ×1,65 · ciclo arcoíris · deriva aleatoria · 10 s',
    // r108 · SUPER CRIPTONITA (el dueño: nuevo poder de pala, 12 s)
    arc_desc_cripto: 'La bola se vuelve kryptonita: verde fosforito pulsante con estela de luz verde que se disipa a medio metro; cada bote en la mesa del rival siembra cristales de cuarzo veteados de 20 a 50 cm y si la bola los rompe, sale despedida al 33 % en dirección imposible.',
    arc_met_cripto: 'Bola verde pulsante · estela verde 50 cm · 1-5 cristales (20-50 cm) · romper = ×1/3 + dirección aleatoria · 12 s',
    poder_cripto: 'SUPER CRIPTONITA',
    arc_cripto_go: '¡SUPER CRIPTONITA! La bola es kryptonita y siembra cristales en la mesa rival',
    arc_cripto_fin: 'La criptonita se apaga: bola y mesa vuelven a la normalidad',
    cripto_rompe: '¡Cristal roto! La bola sale despedida al 33 % en dirección imposible',"""

EN_NEW = """    arc_met_ancla: 'Immune to rival powers · no active bonus · 10 s',
    // FASE 160 · the missing card (r108 owner report: Bola Loca had no
    // description on its gallery card)
    arc_desc_bolaloca: 'The ball grows and lives its chaos: rainbow cycle and unpredictable drift that throws anyone off and wrecks the rival\\'s plans.',
    arc_met_bolaloca: 'Size ×1.65 · rainbow cycle · random drift · 10 s',
    // r108 · SUPER CRYPTONITE (owner: new paddle power, 12 s)
    arc_desc_cripto: 'The ball becomes kryptonite: pulsing phosphor green with a light-green trail that fades within half a meter; every bounce on the rival table grows veined quartz crystals 20-50 cm tall, and if the ball smashes one it crawls away at 33% on an impossible heading.',
    arc_met_cripto: 'Pulsing green ball · 50 cm green trail · 1-5 crystals (20-50 cm) · breaking = ×1/3 + random heading · 12 s',
    poder_cripto: 'SUPER CRYPTONITE',
    arc_cripto_go: 'SUPER CRYPTONITE! The ball is kryptonite and seeds crystals on the rival table',
    arc_cripto_fin: 'The kryptonite fades: ball and table are back to normal',
    cripto_rompe: 'Crystal shattered! The ball crawls away at 33% on an impossible heading',"""

c00 = edit(c00, ES_ANCLA := "    arc_met_ancla: 'Inmunidad a poderes rivales · sin bonus activo · 10 s',",
           ES_NEW, "c00 ES")
c00 = edit(c00, "    arc_met_ancla: 'Immune to rival powers · no active bonus · 10 s',",
           EN_NEW, "c00 EN")
io.open(R + 'c00_pre_three.js', 'w', encoding='utf-8').write(c00)
print(f"c00: {len(c00) - m0} bytes · fichas ES/EN (bolaloca + cripto) ✓")
