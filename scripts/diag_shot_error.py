#!/usr/bin/env python3
"""Réplica de la física de vuelo del juego para medir el error de
computeShotVelocity (sin arrastre/Magnus) frente a la física real."""
import math

# DIMS (game_part1.js)
G = -9.81
AIR_DRAG_K = 0.142
MAGNUS = 0.0035
SPIN_DECAY = 0.3
TABLE_TOP = 0.76
BALL_R = 0.02
TOP_R = TABLE_TOP + BALL_R
NET_TOP = 0.9125
HALF_L = 1.37
HALF_W = 0.7625
C_Z = -1.6
REST = 0.88
FRIC = 0.94
BOUNCE_SPIN_KICK = 0.012
H = 1 / 240


def aero(vel, spin, h):
    sp = math.sqrt(sum(v * v for v in vel))
    if sp > 1e-6:
        f = max(0.0, 1 - AIR_DRAG_K * sp * h)
        vel[0] *= f; vel[1] *= f; vel[2] *= f
    sl = spin[0] * spin[0] + spin[1] * spin[1] + spin[2] * spin[2]
    if sl > 1e-4:
        # tmpM = spin × vel
        m = [(spin[1] * vel[2] - spin[2] * vel[1]),
             (spin[2] * vel[0] - spin[0] * vel[2]),
             (spin[0] * vel[1] - spin[1] * vel[0])]
        for i in range(3):
            vel[i] += m[i] * MAGNUS * h
        f = max(0.0, 1 - SPIN_DECAY * h)
        spin[0] *= f; spin[1] *= f; spin[2] *= f


def no_drag_solution(fy, fz, tx, ty, tz, T):
    vy = (ty - fy) / T - 0.5 * G * T
    vx = (tx - fy * 0) / T  # placeholder, correct below
    vx = (tx - 0) / T  # x from 0
    vz = (tz - fz) / T
    return [vx, vy, vz]


def simulate(pos, vel, spin, max_t=1.6):
    """Devuelve (bote_en_mesa|None, tiempo_bote, y_al_cruzar_red|None)."""
    p = [0.0, pos[1], pos[2]]
    v = list(vel)
    s = list(spin)
    t = 0.0
    net_y = None
    net_checked = False
    while t < max_t:
        prev_y = p[1]
        prev_z = p[2]
        v[1] += G * H
        aero(v, s, H)
        for i in range(3):
            p[i] += v[i] * H
        t += H
        # cruce de red
        if not net_checked and (prev_z - C_Z) * (p[2] - C_Z) <= 0 and prev_z != p[2]:
            f = (C_Z - prev_z) / (p[2] - prev_z)
            net_y = prev_y + (p[1] - prev_y) * f
            net_checked = True
        # bote en mesa
        if v[1] < 0 and prev_y >= TOP_R and p[1] < TOP_R and \
           abs(p[0]) <= HALF_W and abs(p[2] - C_Z) <= HALF_L:
            p[1] = TOP_R
            v[1] *= -REST
            v[0] *= FRIC
            v[2] *= FRIC
            v[0] -= BOUNCE_SPIN_KICK * s[2]
            v[2] += BOUNCE_SPIN_KICK * s[0]
            return (p[0], p[2]), t, net_y
        if p[1] < BALL_R:
            return None, t, net_y
    return None, t, net_y


def report(name, fy, fz, spin_x, T, tx, tz):
    # semilla del juego (solo gravedad, desde x=0)
    v = no_drag_solution(fy, fz, tx, TOP_R, tz, T)
    v[0] = tx / T   # vx correcto
    spin = [spin_x, 0.0, 0.0]
    land, t_land, net_y = simulate([0, fy, fz], v, spin)
    land_str = f"({land[0]:+.2f}, {land[1]:+.2f})" if land else "FUERA/RED"
    print(f"{name:28s} T={T:.2f} spin={spin_x:+.0f} -> bote {land_str} "
          f"t={t_land:.2f}s objetivo=({tx:+.2f},{tz:+.2f}) red_y={net_y and round(net_y,3)}")

    # iterativo (lo que implementaré en JS)
    vv = list(v)
    ss = [spin_x, 0.0, 0.0]
    pos0 = [0, fy, fz]
    for it in range(7):
        land, t_land, net_y = simulate(pos0, vv, ss)
        if land is None:
            vv[1] += 0.5
            continue
        ex = tx - land[0]
        ez = tz - land[1]
        vv[0] += ex / T
        vv[2] += ez / T
        if net_y is not None and net_y < NET_TOP + 0.06:
            vv[1] += (NET_TOP + 0.07 - net_y) * 1.7
    land, t_land, net_y = simulate(pos0, vv, ss)
    land_str = f"({land[0]:+.2f}, {land[1]:+.2f})" if land else "FUERA/RED"
    print(f"{'  -> corregido iterativo':28s}          -> bote {land_str} "
          f"t={t_land:.2f}s red_y={net_y and round(net_y,3)}  v=({vv[0]:+.2f},{vv[1]:+.2f},{vv[2]:+.2f})")


print("=== CPU medium: drive con lift desde su fondo (z=-1.9, y=1.0) ===")
# sign = -1 (CPU en -Z). Golpe hacia +z (campo del jugador). spinX = -sign*(9..18) = +9..18
report("drive medio (sin arrastre)", 1.0, -1.95, +13, 0.62, 0.30, C_Z + 0.62 * HALF_L)
report("drive largo (sin arrastre)", 1.0, -1.95, +16, 0.55, -0.35, C_Z + 1.05 * HALF_L)
report("remate (sin arrastre)", 1.15, -1.85, +20, 0.42, 0.25, C_Z + 0.85 * HALF_L)
report("push corto (sin arrastre)", 0.9, -2.1, -7, 0.75, 0.18, C_Z + 0.6 * HALF_L)
