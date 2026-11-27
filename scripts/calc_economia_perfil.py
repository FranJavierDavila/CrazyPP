#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cálculos del PLAN MI PERFIL: curva de XP, economía de monedas por
modalidad, presupuesto de sesión y tiempo-a-objeto. Todo impreso para
verificar cada número que entra en el informe."""
import math

# ---------- CURVA DE XP (calibrada al mock del dueño: L27≈5.000 XP) ----------
def xp_para(n):  # XP necesarios para pasar de nivel n a n+1
    return round(150 + 62 * (n - 1) ** 1.35)

def acum(n):     # XP acumulados desde nivel 1 hasta llegar a nivel n+1
    return sum(xp_para(i) for i in range(1, n + 1))

print("== CURVA XP ==")
print(f"L1→2: {xp_para(1)}  L5→6: {xp_para(5)}  L10→11: {xp_para(10)}  "
      f"L27→28: {xp_para(27)}  L40→41: {xp_para(40)}  L50→51: {xp_para(50)}")
for n in (10, 20, 27, 35, 50):
    print(f"XP acumulados para llegar a nivel {n}: {acum(n-1):,}")

XP = {  # XP por partida/acción según modalidad
    'partido_ia_v': 40, 'partido_ia_d': 12, 'bonus_hard': 10,
    'p2p_v': 60, 'p2p_d': 18,
    'carrera_etapa': 70, 'champ_etapa': 50, 'champ_titulo': 250,
    'surv_base': 20, 'surv_oleada': 3, 'tut': 100, 'train_meta': 15,
}
print("\n== XP TÍPICOS ==")
media = 0.75 * XP['partido_ia_v'] + 0.25 * XP['partido_ia_d']
print(f"partido IA medio (75% victorias): {media:.0f} XP")
nivel27 = acum(26)
print(f"partidos IA medios hasta nivel 27: {nivel27/media:.0f}")
media_p2p = 0.6 * XP['p2p_v'] + 0.4 * XP['p2p_d']
print(f"duelo P2P medio (60% victorias): {media_p2p:.0f} XP")

# ---------- MONEDAS POR MODALIDAD (propuesta) ----------
MON = {
    'ia_v': 25, 'ia_d': 8, 'ia_bonus_hard': 5,
    'p2p_v': 40, 'p2p_d': 12, 'p2p_tope_dia': 10,
    'carrera_nueva': 60, 'carrera_rep': 10,
    'champ_etapa': 40, 'champ_titulo': 300,
    'champ_oro': 80, 'champ_plata': 50, 'champ_bronce': 30,
    'surv_oleada': 2, 'surv_tope': 30, 'surv_record': 50,
    'train_meta': 20, 'tut': 50,
    'logro_min': 25, 'logro_max': 100,
}
print("\n== MONEDAS ==")
m_media = 0.75 * (MON['ia_v'] + MON['ia_bonus_hard']) + 0.25 * MON['ia_d']
print(f"partido IA medio (hard): {m_media} monedas")
sesion = 8 * m_media
print(f"sesión casual (8 partidos IA hard, ~1 h): {sesion} monedas")
print(f"sesión mixta (5 IA + 2 P2P + 1 surv 12 oleadas): "
      f"{5*m_media + 2*(MON['p2p_v']*0.6 + MON['p2p_d']*0.4) + MON['surv_oleada']*12}")

print("\n== TIEMPO-A-OBJETO (sesión casual = 8 partidos ≈ 1 h) ==")
for nombre, precio in [('bola neón', 200), ('mesa oro', 400), ('mesa carbón', 600),
                       ('avatar común', 250), ('avatar especial', 550),
                       ('avatar épico', 1000), ('avatar legendario', 2400),
                       ('marco básico', 150), ('marco legendario', 1800)]:
    print(f"  {nombre} ({precio}): {precio/sesion:.1f} sesiones")

print("\n== PRESUPUESTO TOTAL DEL CATÁLOGO NUEVO ==")
avatares = 8*250 + 6*550 + 4*1000 + 2*2400
marcos   = 4*150 + 3*400 + 2*900 + 1*1800
print(f"avatares (20): {avatares:,} · marcos (10): {marcos:,} · total: {avatares+marcos:,}")
print(f"vs catálogo actual de skins (mesa+bola): ~{sum([400,600,250,350,350,300,200,450,400,250,250,300,400,500]):,}")
print(f"horas de juego para TODO el catálogo nuevo: {(avatares+marcos)/sesion:.0f} h")

# ---------- RANGOS ELO (tabla del dueño) ----------
RANGOS = [('Novato III',0,799),('Novato II',800,899),('Novato I',900,999),
('Amateur III',1000,1099),('Amateur II',1100,1199),('Amateur I',1200,1299),
('Club III',1300,1399),('Club II',1400,1499),('Club I',1500,1599),
('Competidor III',1600,1699),('Competidor II',1700,1799),('Competidor I',1800,1899),
('Semiprofesional III',1900,1999),('Semiprofesional II',2000,2099),('Semiprofesional I',2100,2199),
('Profesional III',2200,2299),('Profesional II',2300,2399),('Profesional I',2400,2499),
('Maestro',2500,2699),('Gran Maestro',2700,2899),('Leyenda Olímpica',2900,10**9)]
print("\n== RANGOS ==")
print(f"rangos: {len(RANGOS)} · inicial del juego (1000) cae en: "
      f"{[r[0] for r in RANGOS if r[1] <= 1000 <= r[2]][0]}")
print(f"CPU easy(900)→{[r[0] for r in RANGOS if r[1] <= 900 <= r[2]][0]} · "
      f"medium(1050)→{[r[0] for r in RANGOS if r[1] <= 1050 <= r[2]][0]} · "
      f"hard(1200)→{[r[0] for r in RANGOS if r[1] <= 1200 <= r[2]][0]}")
# K=24 (ia), simular subida desde 1000 con 75% victorias vs medium (1050)
elo, K, n = 1000, 24, 0
for _ in range(500):
    exp = 1 / (1 + 10 ** ((1050 - elo) / 400))
    if (math.random() if hasattr(math, 'random') else 0.75) < exp or True:
        pass
    # determinista: 75% victorias
    win = (n % 4 != 3)  # 3 de cada 4 gana
    elo += round(K * ((1 - exp) if win else -exp))
    n += 1
    if elo >= 2500:
        break
print(f"simulación determinista (75% victorias vs 1050, K=24): "
      f"Maestro(2500) tras ~{n} partidos · ELO final {elo}")
elo, n = 1000, 0
for _ in range(2000):
    exp = 1 / (1 + 10 ** ((1200 - elo) / 400))
    win = (n % 4 != 3)
    elo += round(24 * ((1 - exp) if win else -exp))
    n += 1
    if elo >= 2500: break
print(f"75% victorias vs hard(1200), K=24: Maestro tras ~{n} partidos")
elo, n = 1000, 0
for _ in range(2000):
    exp = 1 / (1 + 10 ** ((1000 - elo) / 400))
    win = (n % 2 == 0)  # 50% vs igual nivel
    elo += round(32 * ((1 - exp) if win else -exp))
    n += 1
    if elo >= 2500: break
print(f"P2P 50% victorias vs igual ELO, K=32: Maestro tras ~{n} duelos (equilibrio estable: se estanca)")
