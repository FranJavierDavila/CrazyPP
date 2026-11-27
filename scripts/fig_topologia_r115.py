#!/usr/bin/env python3
"""fig_topologia_r115.py — figura de topología de red para la propuesta de
modo espectador: hoy (1:1), espectador pasivo (fan-out) y espectador con
influencia (votos de baja tasa). Salida: PNG + dims JSON."""
import json
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

AZUL = '#0F3049'
CYAN = '#1B6B7A'
ORO = '#B8860B'
GRIS = '#5A6B7A'


def caja(ax, x, y, w, h, texto, color, fs=10, bold=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02',
                 fc=color, ec='none', alpha=0.92))
    ax.text(x + w / 2, y + h / 2, texto, ha='center', va='center',
            fontsize=fs, color='white', fontweight='bold' if bold else 'normal')


def flecha(ax, x1, y1, x2, y2, texto, color, doble=False, ls='-'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='<-' if doble else '->',
                 mutation_scale=16, color=color, lw=2.2, linestyle=ls))
    ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.045, texto, ha='center', va='bottom',
            fontsize=8.2, color=color)


fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4), constrained_layout=True)
for ax in axes:
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

# ── Panel 1 · hoy ──
caja(axes[0], 0.06, 0.52, 0.36, 0.20, 'ANFITRIÓN\n(autoridad de su mitad,\nárbitro y reloj)', AZUL, 9.5)
caja(axes[0], 0.58, 0.52, 0.36, 0.20, 'INVITADO\n(autoridad de su mitad,\nsimula bola fantasma)', AZUL, 9.5)
flecha(axes[0], 0.43, 0.66, 0.57, 0.66, 'pose 60 Hz · SNAP 20-30 Hz', CYAN, doble=True)
flecha(axes[0], 0.43, 0.55, 0.57, 0.55, 'control JSON (rel)', GRIS, doble=True, ls='--')
caja(axes[0], 0.06, 0.10, 0.88, 0.26,
     'Malla ESTRICTAMENTE 1:1\nun segundo par entrante se rechaza (c09:269)\n'
     'sin relay de datos: el worker solo señala ICE y presencia', '#EDF3F5', 9, bold=False)
axes[0].text(0.5, 0.95, 'Hoy · duelo 1 contra 1', ha='center', fontsize=11.5,
             color=AZUL, fontweight='bold')

# ── Panel 2 · espectador pasivo ──
caja(axes[1], 0.36, 0.55, 0.28, 0.20, 'ANFITRIÓN\nfan-out en los 3\npuntos de salida', AZUL, 9)
caja(axes[1], 0.04, 0.72, 0.24, 0.16, 'INVITADO\n(duelo intacto)', AZUL, 9)
caja(axes[1], 0.72, 0.72, 0.24, 0.16, 'Invitado', AZUL, 9)
caja(axes[1], 0.04, 0.22, 0.26, 0.17, 'ESPECTADOR 1\nsolo descarga', CYAN, 8.5)
caja(axes[1], 0.37, 0.22, 0.26, 0.17, 'ESPECTADOR 2\nsolo descarga', CYAN, 8.5)
caja(axes[1], 0.70, 0.22, 0.26, 0.17, 'ESPECTADOR N\n(máx. 4-6)', CYAN, 8.5)
flecha(axes[1], 0.42, 0.70, 0.20, 0.88, '', CYAN, doble=True)
flecha(axes[1], 0.58, 0.70, 0.80, 0.88, '', CYAN, doble=True)
for x0 in (0.17, 0.50, 0.83):
    flecha(axes[1], 0.50, 0.55, x0, 0.39, 'stream reducido\n~2,5 KB/s', CYAN if x0 == 0.50 else CYAN)
axes[1].text(0.5, 0.95, 'S1 · espectador pasivo', ha='center', fontsize=11.5,
             color=AZUL, fontweight='bold')
axes[1].text(0.5, 0.03, 'solo-descarga: no toca el camino de entrada del duelo',
             ha='center', fontsize=8.5, color=GRIS, style='italic')

# ── Panel 3 · influencia ──
caja(axes[2], 0.36, 0.55, 0.28, 0.20, 'ANFITRIÓN\n(filtra y decide\nlos votos)', AZUL, 9)
caja(axes[2], 0.04, 0.74, 0.30, 0.17, 'PÚBLICO\novómetro · votos\neventos', CYAN, 8.5)
caja(axes[2], 0.66, 0.74, 0.30, 0.17, 'PARTIDA CASUAL\npoderes tipo Duelos\n(voto mayoritario)', CYAN, 8.5)
caja(axes[2], 0.04, 0.50, 0.28, 0.16, 'Duelo\n(afectación\nsutil, opcional)', AZUL, 8.5)
caja(axes[2], 0.04, 0.08, 0.92, 0.30,
     'Guardarraíl: en partidas clasificadas (ELO)\n'
     'los votos solo tocan cosmética; claim/ack y\n'
     'resync del árbitro quedan intactos', '#FDF6E9', 8.6, bold=False)
flecha(axes[2], 0.19, 0.74, 0.44, 0.66, 'votos rel\n1-2 Hz', GRIS)
flecha(axes[2], 0.62, 0.70, 0.50, 0.60, 'aplica', ORO)
flecha(axes[2], 0.42, 0.58, 0.22, 0.56, '', ORO)
axes[2].text(0.5, 0.95, 'S3 · público con influencia', ha='center', fontsize=11.5,
             color=AZUL, fontweight='bold')

salida = '/home/z/my-project/download/_thumbs_r115/fig_topologia.png'
import os
os.makedirs(os.path.dirname(salida), exist_ok=True)
fig.savefig(salida, dpi=170, facecolor='white')
plt.close(fig)

from PIL import Image
im = Image.open(salida)
json.dump({'f': 'fig_topologia.png', 'w': im.width, 'h': im.height},
          open('/home/z/my-project/scripts/_fig_dims.json', 'w'))
print('✓ figura', im.size, '→', salida)
