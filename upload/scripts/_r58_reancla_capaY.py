#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""r58 · re-ancla la capa Y (qa_hall_sin_pala_v3630) al hall SIN TROFEO:
el museo ya no tiene copa/peana/haz (espacio central libre, petición del
dueño) — quedan las 7 bolas doradas, 2 luces y el vaivén vivo."""
from pathlib import Path

p = Path('/home/z/my-project/scripts/qa_hall_sin_pala_v3630.py')
t = p.read_text(encoding='utf-8')

pares = [
    # evaluate: el bloque del museo → trofeo fuera + bolas + 2 luces
    ("""          // el museo sigue vivo: trofeo y bolas doradas
          const ud = G.hallGroup && G.hallGroup.userData.hall;
          out.museo = ud ? {
            cupLathe: !!(ud.trophyCup && ud.trophyCup.geometry &&
                         ud.trophyCup.geometry.type === 'LatheGeometry'),
            handles: (ud.trophyHandles || []).length,
            cupSilver: ud.trophyCup ? ud.trophyCup.material === ud.trophySilver : null,
            balls: ud.fx ? ud.fx.balls.length : 0,
            lights: (ud.lights || []).length,
          } : null;""",
     """          // el museo sigue vivo: bolas doradas (trofeo RETIRADO r58 —
          // espacio central libre, petición del dueño)
          const ud = G.hallGroup && G.hallGroup.userData.hall;
          out.museo = ud ? {
            trofeoFuera: (!ud.fx || (!ud.fx.trophy && !ud.fx.beam && !ud.fx.halo))
              && ud.trophyCup === undefined && ud.trophyHandles === undefined
              && ud.trophySilver === undefined,
            balls: ud.fx ? ud.fx.balls.length : 0,
            lights: (ud.lights || []).length,
          } : null;"""),
    # evaluate: el giro del trofeo → el vaivén de las bolas
    ("""          // el trofeo respira (updateHallFx)
          const r0 = ud && ud.fx && ud.fx.trophy ? ud.fx.trophy.rotation.y : 0;
          await new Promise(r => setTimeout(r, 400));
          const r1 = ud && ud.fx && ud.fx.trophy ? ud.fx.trophy.rotation.y : 0;
          out.trophySpin = +(r1 - r0).toFixed(4);""",
     """          // las bolas respiran (updateHallFx, r58: sin trofeo)
          const y0s = ud && ud.fx ? ud.fx.balls.map(b => b.position.y) : [];
          await new Promise(r => setTimeout(r, 400));
          out.ballMoved = ud && ud.fx ? ud.fx.balls.some((b, i) =>
            Math.abs(b.position.y - y0s[i]) > 0.002) : false;"""),
    # checks
    ("""        chk(m.get("cupLathe") and m.get("handles") == 2,
            "el museo intacto: trofeo Lathe + 2 asas")
        chk(m.get("cupSilver") is True,
            "sin campeón: trofeo PLATEADO (el arte no sufre)")
        chk(m.get("balls") == 7 and m.get("lights") == 3,
            "7 bolas doradas + 3 luces (el salón respira)")""",
     """        chk(m.get("trofeoFuera") is True,
            "museo r58: TROFEO FUERA (copa/haz/anillo fuera, espacio libre)")
        chk(m.get("balls") == 7 and m.get("lights") == 2,
            "7 bolas doradas + 2 luces (el salón respira)")"""),
    ("""        spin = checks.get("trophySpin")
        chk(isinstance(spin, (int, float)) and spin > 0,
            "el trofeo GIRA (updateHallFx vivo, delta " + str(spin) + ")")""",
     """        chk(checks.get("ballMoved") is True,
            "las bolas NAVEGAN (updateHallFx vivo, vaivén r58)")"""),
]

fallos = 0
for viejo, nuevo in pares:
    if viejo in t:
        t = t.replace(viejo, nuevo)
        print(f'  ✓ {viejo.strip().splitlines()[0][:52]!r} re-anclado')
    elif nuevo in t:
        print(f'  = ya re-anclado ({nuevo.strip().splitlines()[0][:40]!r})')
    else:
        print(f'  ✗ NO ENCONTRADO: {viejo.strip().splitlines()[0][:60]!r}')
        fallos += 1
p.write_text(t, encoding='utf-8')
exit(1 if fallos else 0)
