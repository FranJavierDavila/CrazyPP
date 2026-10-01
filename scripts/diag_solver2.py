#!/usr/bin/env python3
"""Solver v2: converge también en dejadas y respetando velocidad máx."""
import math

G = -9.81; AIR_DRAG_K = 0.142; MAGNUS = 0.0035; SPIN_DECAY = 0.3
TABLE_TOP = 0.76; BALL_R = 0.02; TOP_R = TABLE_TOP + BALL_R
NET_TOP = 0.9125; HALF_L = 1.37; HALF_W = 0.7625; C_Z = -1.6
REST = 0.88; FRIC = 0.94; BOUNCE_SPIN_KICK = 0.012; H = 1/240
NET_MARGIN = 0.055

def aero(vel, spin, h):
    sp = math.sqrt(sum(v*v for v in vel))
    if sp > 1e-6:
        f = max(0.0, 1 - AIR_DRAG_K*sp*h)
        vel[0] *= f; vel[1] *= f; vel[2] *= f
    sl = spin[0]**2 + spin[1]**2 + spin[2]**2
    if sl > 1e-4:
        m = [spin[1]*vel[2]-spin[2]*vel[1], spin[2]*vel[0]-spin[0]*vel[2], spin[0]*vel[1]-spin[1]*vel[0]]
        for i in range(3): vel[i] += m[i]*MAGNUS*h
        f = max(0.0, 1 - SPIN_DECAY*h)
        spin[0] *= f; spin[1] *= f; spin[2] *= f

def simulate(pos, vel, spin, max_t=1.7):
    p = list(pos); v = list(vel); s = list(spin); t = 0.0
    net_y = None; crossed = False
    while t < max_t:
        prev_y = p[1]; prev_z = p[2]
        v[1] += G*H; aero(v, s, H)
        for i in range(3): p[i] += v[i]*H
        t += H
        if not crossed and (prev_z - C_Z)*(p[2] - C_Z) <= 0 and prev_z != p[2]:
            f = (C_Z - prev_z)/(p[2] - prev_z)
            net_y = prev_y + (p[1]-prev_y)*f; crossed = True
        if v[1] < 0 and prev_y >= TOP_R and p[1] < TOP_R and abs(p[0]) <= HALF_W and abs(p[2]-C_Z) <= HALF_L:
            return (p[0], p[2]), t, net_y, None
        if p[1] < BALL_R:
            return None, t, net_y, (p[0], p[2])   # cayó al suelo aquí
    return None, t, net_y, None

def solve_shot(fpos, target, T, spin, max_speed=99.0, max_iter=14):
    fx, fy, fz = fpos; tx, tz = target
    vx = (tx-fx)/T; vz = (tz-fz)/T; vy = (TOP_R-fy)/T - 0.5*G*T
    v = [vx, vy, vz]
    d0 = math.hypot(tx-fx, tz-fz)
    ux = (tx-fx)/d0; uz = (tz-fz)/d0
    for it in range(max_iter):
        sp = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
        if sp > max_speed:
            k = max_speed/sp; v = [c*k for c in v]
        land, t_land, net_y, fell = simulate(fpos, v, spin)
        if net_y is not None and net_y < NET_TOP + NET_MARGIN:
            v[1] += (NET_TOP + NET_MARGIN + 0.01 - net_y)*1.8
            continue
        if land is None:
            if not crossed:
                v[1] += 0.30; v[0] *= 1.06; v[2] *= 1.06   # no cruzó: más de todo
            elif fell and (fell[1]-tz)*uz < 0:
                pass  # se quedó corta al caer al suelo: raro, siguiente iter decide
            else:
                v[0] *= 0.94; v[2] *= 0.94                 # se fue larga: frenar
            continue
        ex = land[0]-tx; ez = land[1]-tz
        e = ex*ux + ez*uz
        l = ex*(-uz) + ez*ux
        f = max(0.7, min(1.5, 1 - 0.9*e/d0))
        v[0] *= f; v[2] *= f
        v[0] += -l/T*(-uz); v[2] += -l/T*(ux)
    sp = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
    if sp > max_speed:
        k = max_speed/sp; v = [c*k for c in v]
    return v

CASES = [
    ("drive medio",   (0.0, 1.00, -1.95), 0.62, (13,-2), (0.30, -0.75), 6.2),
    ("drive 0.94",    (0.0, 1.00, -1.95), 0.55, (16, 3), (-0.35, -0.31), 6.2),
    ("drive cruzado", (0.4, 0.95, -1.90), 0.60, (11, 5), (-0.50, -0.45), 6.2),
    ("remate",        (0.1, 1.15, -1.85), 0.42, (20, 0), (0.25, -0.44), 7.1),
    ("push corto",    (0.0, 0.90, -2.10), 0.75, (-7, 0), (0.18, -0.78), 5.0),
    ("dejada corta",  (0.2, 0.95, -2.00), 0.95, (-8, 0), (-0.12, -1.30), 3.4),
    ("bloqueo",       (0.0, 1.05, -1.85), 0.48, (12, 0), (0.40, -0.60), 5.7),
    ("drive fondo y bajo", (0.0, 0.82, -2.20), 0.58, (14, 0), (-0.45, -0.30), 6.2),
    ("smash hard",    (0.2, 1.30, -1.80), 0.34, (24, 4), (-0.30, -0.50), 11.5),
]
print(f"{'caso':20s} {'bote':>17s} {'obj':>15s} {'err_cm':>7s} {'red_y':>7s}")
for name, fpos, T, spin, (tx, tz), maxV in CASES:
    spin_v = [float(spin[0]), float(spin[1]), 0.0]
    v = solve_shot(fpos, (tx, tz), T, spin_v, maxV)
    land, t_land, net_y, fell = simulate(fpos, v, list(spin_v))
    if land:
        err = math.hypot(land[0]-tx, land[1]-tz)*100
        ls = f"({land[0]:+.3f},{land[1]:+.3f})"
    else:
        err = 999; ls = f"FALLA fell={fell and (round(fell[0],2),round(fell[1],2))}"
    ok = "OK " if err <= 4.5 and (net_y or 0) > NET_TOP+0.03 else "!! "
    print(f"{ok}{name:18s} {ls:>17s} ({tx:+.2f},{tz:+.2f}) {err:6.1f} {net_y and round(net_y,3)!s:>7} v=({v[0]:+.2f},{v[1]:+.2f},{v[2]:+.2f}) t={t_land:.2f}")
