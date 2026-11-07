#!/usr/bin/env python3
"""
CRAZY PING PONG · ronda 10 · OPTIMIZACIÓN DE FPS en XR (FUENTES)
================================================================
LECCIÓN DE ESTA RONDA: el parche va SIEMPRE a los fuentes de src/game/ —
public/game.html se REGENERA desde ellos en cada bump_version.py (el artefacto
no es editable: bump lo reconstruye byte-exacto y borra cualquier edit directo).

Diagnóstico (telemetría vr_end real: 38 fps de media en 83 min de VR):
  · setFramebufferScaleFactor(1.7) → ~2.9× píxeles por ojo vs nativo
  · setFoveation(0)                → periferia a resolución completa
  · PCFSoftShadowMap 2048×2048     → shadow pass pesado por frame
Cambios (SOLO presentación; cero física, cero gameplay):
  c12_pingponggame.js — renderer:
    1. framebufferScaleFactor 1.7 → 1.4 (nivel «Extra Sharpness» del Meta
       Browser: ~1.96× píxeles/ojo, -32% sombreado GPU)
    2. foveation 0 → 0.5 (el compositor comprime la periferia; imperceptible)
    3. sombras PCFSoft 2048 → PCF 1024 (la zona sombreada es la mesa, 6×6 m)
    4. vr_end lleva fpsMin/fpsMax de la SESIÓN VR (reset en onSessionStart)
  c00_pre_three.js — módulo __PP_TELE:
    5. noteFrame acumula fpsLo/fpsHi (récord de la sesión, no solo 12 muestras)
    6. resetFps() exportado
Cada aguja debe aparecer EXACTAMENTE una vez en su fichero; si no, aborta sin
escribir nada. Idempotente de facto: si ya está el texto nuevo, lo dice.
"""

import sys

F12 = "/home/z/my-project/src/game/core/c12_pingponggame.js"
F00 = "/home/z/my-project/src/game/core/c00_pre_three.js"
CAT = "/home/z/my-project/scripts/telemetria_catalogo.json"

EDITS = [
    (F12,
     "    // Nitidez máxima en el visor: sin foveación (borde nítido en toda la\n"
     "    // lente) y framebuffer sobredimensionado (Quest 3 tiene GPU de sobra\n"
     "    // para esta escena).\n"
     "    this.renderer.xr.setFoveation(0);\n"
     "    this.renderer.xr.setFramebufferScaleFactor(1.7);",
     "    // v3.6.6 (ronda 10 · AUDITORÍA DE FPS): la telemetría vr_end midió 38\n"
     "    // fps de media en sesión larga — GPU saturada por nitidez máxima\n"
     "    // (1.7× = ~2.9× píxeles/ojo + foveation 0 + sombras PCFSoft 2048²).\n"
     "    // Compromiso nitidez/rendimiento: 1.4× («Extra Sharpness» del Meta\n"
     "    // Browser, nitidez alta) + foveation 0.5 (periferia comprimida por el\n"
     "    // compositor, imperceptible en juego).\n"
     "    this.renderer.xr.setFoveation(0.5);\n"
     "    this.renderer.xr.setFramebufferScaleFactor(1.4);"),

    (F12,
     "this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;",
     "this.renderer.shadowMap.type = THREE.PCFShadowMap;"),

    (F12,
     "dir.shadow.mapSize.set(2048, 2048);",
     "dir.shadow.mapSize.set(1024, 1024);"),

    (F12,
     "    try { __PP_TELE.ev('vr_start', { mode: this.mode, multi: !!(this.net && this.net.online) }); } catch { /* */ }\n"
     "    this._vrT0 = Date.now();",
     "    try { __PP_TELE.ev('vr_start', { mode: this.mode, multi: !!(this.net && this.net.online) }); } catch { /* */ }\n"
     "    this._vrT0 = Date.now();\n"
     "    try { __PP_TELE.resetFps(); } catch { /* */ }"),

    (F12,
     "        dur: this._vrT0 ? Math.round((Date.now() - this._vrT0) / 1000) : 0,\n"
     "        fps: __PP_TELE.fpsAvg(),\n"
     "      });",
     "        dur: this._vrT0 ? Math.round((Date.now() - this._vrT0) / 1000) : 0,\n"
     "        fps: __PP_TELE.fpsAvg(),\n"
     "        fpsMin: __PP_TELE.fpsLo(),\n"
     "        fpsMax: __PP_TELE.fpsHi(),\n"
     "      });"),

    (F00,
     "    frames: 0, fpsAcc: 0, fpsSamples: [],",
     "    frames: 0, fpsAcc: 0, fpsSamples: [], fpsLo: null, fpsHi: null,"),

    (F00,
     "      const fps = st.frames / st.fpsAcc;\n"
     "      st.fpsSamples.push(Math.round(fps));\n"
     "      if (st.fpsSamples.length > 12) st.fpsSamples.shift();\n"
     "      st.frames = 0; st.fpsAcc = 0;",
     "      const fps = st.frames / st.fpsAcc;\n"
     "      const red = Math.round(fps);\n"
     "      st.fpsSamples.push(red);\n"
     "      if (st.fpsSamples.length > 12) st.fpsSamples.shift();\n"
     "      // ronda 10: récord de la sesión (no solo las últimas 12 muestras)\n"
     "      if (st.fpsLo === null || red < st.fpsLo) st.fpsLo = red;\n"
     "      if (st.fpsHi === null || red > st.fpsHi) st.fpsHi = red;\n"
     "      st.frames = 0; st.fpsAcc = 0;"),

    (F00,
     "  function fpsAvg() {\n"
     "    const s = st.fpsSamples.slice();\n"
     "    return s.length ? Math.round(s.reduce((a, b) => a + b, 0) / s.length) : null;\n"
     "  }",
     "  function fpsAvg() {\n"
     "    const s = st.fpsSamples.slice();\n"
     "    return s.length ? Math.round(s.reduce((a, b) => a + b, 0) / s.length) : null;\n"
     "  }\n"
     "\n"
     "  /** ronda 10: mínimo/máximo DE LA SESIÓN VR (reset al entrar en VR). */\n"
     "  function resetFps() { st.fpsLo = null; st.fpsHi = null; }\n"
     "  function fpsLo() { return st.fpsLo; }\n"
     "  function fpsHi() { return st.fpsHi; }"),

    (F00,
     "  return { ev, flush, noteFrame, fpsAvg,",
     "  return { ev, flush, noteFrame, fpsAvg, resetFps, fpsLo, fpsHi,"),
]


def main():
    ficheros = {}
    for ruta, viejo, nuevo in EDITS:
        if ruta not in ficheros:
            ficheros[ruta] = open(ruta, encoding="utf-8").read()
        if viejo in ficheros[ruta] and nuevo in ficheros[ruta]:
            print(f"  = ya aplicado: {viejo[:60]!r}…")
            continue
        n_vec = ficheros[ruta].count(viejo)
        if n_vec != 1:
            print(f"FALLO · en {ruta.split('/')[-1]} la aguja aparece {n_vec} veces: {viejo[:80]!r}")
            sys.exit(1)
        ficheros[ruta] = ficheros[ruta].replace(viejo, nuevo)
        print(f"  ✓ {ruta.split('/')[-1]}: {len(viejo)} → {len(nuevo)} B")

    for ruta, contenido in ficheros.items():
        open(ruta, "w", encoding="utf-8").write(contenido)
        print(f"  · escrito {ruta.split('/')[-1]} ({len(contenido)} B)")

    # catálogo: fpsMin/fpsMax en vr_end (la auditoría PII de la capa J exige
    # que toda clave enviada exista en el catálogo)
    cat = open(CAT, encoding="utf-8").read()
    viejo_cat = ('{ "nombre": "fps", "tipo": "number|null", "desc": "FPS medio de la '
                 'sesión (muestreo cada 5 s; null si no hubo muestras)" }')
    nuevo_cat = (
        '{ "nombre": "fps", "tipo": "number|null", "desc": "FPS medio de la '
        'sesión (muestreo cada 5 s; null si no hubo muestras)" },\n'
        '        { "nombre": "fpsMin", "tipo": "number|null", "desc": "FPS mínimo '
        'de la sesión VR (ronda 10; peor intervalo de 5 s)" },\n'
        '        { "nombre": "fpsMax", "tipo": "number|null", "desc": "FPS máximo '
        'de la sesión VR (ronda 10; mejor intervalo de 5 s)" }'
    )
    if nuevo_cat not in cat:
        if cat.count(viejo_cat) != 1:
            print(f"FALLO · aguja del catálogo ×{cat.count(viejo_cat)}")
            sys.exit(1)
        open(CAT, "w", encoding="utf-8").write(cat.replace(viejo_cat, nuevo_cat))
        print("  ✓ catálogo vr_end: fpsMin/fpsMax añadidos")
    else:
        print("  = catálogo ya actualizado")


if __name__ == "__main__":
    main()
