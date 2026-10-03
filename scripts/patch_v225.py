#!/usr/bin/env python3
"""Parchea verify_v225.py a la semántica v2.27: las causas viajan como CLAVES
(dblhit, dbl_opp, noret_you...) y se traducen al pintar. Los cambios:
  A5: applyPoint('doble golpe') -> applyPoint('dblhit'); captura 'c'=='dblhit'
  B2: pt.c 'doble golpe' -> 'dblhit'
  B6: pt.c 'doble bote: tu rival no llegó' -> 'dbl_opp'; remapCause con claves
"""
import io

P = "/home/z/my-project/scripts/verify_v225.py"
s = open(P, encoding="utf-8").read()

reps = [
    ("g.processIntents(g.rules.applyPoint('player', 'doble golpe'));",
     "g.processIntents(g.rules.applyPoint('player', 'dblhit'));"),
    ('a5["capt"]["c"] != "doble golpe"', 'a5["capt"]["c"] != "dblhit"'),
    ("pt: { w: 'player', c: 'doble golpe', rh: 2 } } });",
     "pt: { w: 'player', c: 'dblhit', rh: 2 } } });"),
    ("pt: { w: 'player', c: 'doble bote: tu rival no llegó', rh: 5 } } });",
     "pt: { w: 'player', c: 'dbl_opp', rh: 5 } } });"),
    ("swap1: N.remapCause('no la devolviste', true),",
     "swap1: N.remapCause('noret_you', true),"),
    ("swap2: N.remapCause('golpeaste tu propio campo', true),",
     "swap2: N.remapCause('own_you', true),"),
    ("neutral: N.remapCause('doble golpe', true) };",
     "neutral: N.remapCause('dblhit', true) };"),
    ('if b6["swap1"] != "tu rival no la devolvió" or b6["swap2"] != "tu rival golpeó su campo" or b6["neutral"] != "doble golpe":',
     'if b6["swap1"] != "noret_opp" or b6["swap2"] != "own_opp" or b6["neutral"] != "dblhit":'),
]
n = 0
for old, new in reps:
    if old in s:
        s = s.replace(old, new)
        n += 1
    else:
        print("NO ENCONTRADO:", old[:70])
open(P, "w", encoding="utf-8").write(s)
print(f"{n}/{len(reps)} sustituciones aplicadas")
