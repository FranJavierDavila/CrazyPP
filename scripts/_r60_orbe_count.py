#!/usr/bin/env python3
"""r60 · calculadora del orbe COMPLEJO (etapa 4 de magia).
Réplica exacta de _buildGrid(): celdas d<=rC (núcleo), d<=rM (medio),
d<=rO (exterior), radios en LADRILLOS. Objetivo: <= la mitad de los ~1419
actuales conservando el tamaño físico del orbe (rO*brick ≈ 0,616 m)."""

def count(rC, rM, rO):
    R = int(rO) if rO == int(rO) else int(rO) + 1  # ceil
    n = [0, 0, 0]
    eps = 1e-4
    for x in range(-R, R + 1):
        for y in range(-R, R + 1):
            for z in range(-R, R + 1):
                d = (x * x + y * y + z * z) ** 0.5
                if d <= rC + eps: n[0] += 1
                elif d <= rM + eps: n[1] += 1
                elif d <= rO + eps: n[2] += 1
    return n

# ACTUAL: complejo (1419 esperado) y normal (437 esperado)
for name, rC, rM, rO, br in [
    ("NORMAL actual", 1.5, 3.0, 4.6, 0.125),
    ("COMPLEJO actual", 2.0, 4.0, 7.0, 0.088),
]:
    n = count(rC, rM, rO)
    tot = sum(n)
    print(f"{name}: núcleo={n[0]} medio={n[1]} ext={n[2]} TOTAL={tot} "
          f"radio_físico={rO*br:.3f} m cima≈{(int(rO) if rO==int(rO) else int(rO)+1)*br+br/2 + rO*br:.3f} sobre topY")

print()
# CANDIDATOS: TOTAL <= ~710 (la mitad) manteniendo radio físico ~0,61 m
# (cima/baja idénticas: el centro deriva de reach*brick+brick/2 con la fórmula intacta)
for rC, rM, rO, br in [
    (2.0, 3.5, 5.5, 0.112),   # 0.616 m
    (2.0, 3.5, 6.0, 0.103),   # 0.618 m
    (1.5, 3.0, 5.0, 0.123),   # 0.615 m
    (2.0, 4.0, 5.5, 0.112),
    (1.5, 3.5, 5.5, 0.112),
    (2.0, 3.0, 5.5, 0.112),
    (1.5, 3.0, 5.5, 0.112),
    (2.0, 3.5, 5.0, 0.123),   # 0.615 m
]:
    n = count(rC, rM, rO)
    tot = sum(n)
    reach = int(rO) if rO == int(rO) else int(rO) + 1
    ok = "OK " if tot <= 710 else "ALTO"
    print(f"{ok} rC={rC} rM={rM} rO={rO} brick={br}: núcleo={n[0]} medio={n[1]} ext={n[2]} "
          f"TOTAL={tot} radio={rO*br:.3f} m apoya_base={'sí' if abs(reach*br + br/2 - (reach*br+br/2))<1e-9 else '?'} "
          f"reach*brick={reach*br:.3f}")
