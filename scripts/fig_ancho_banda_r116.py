#!/usr/bin/env python3
"""fig_ancho_banda_r116.py — coste de red por destino (KB/s) medido de las
constantes del código de CrazyPP (POSE_HZ, SNAP_HZ, tamaños de paquete).
Barras horizontales, valores etiquetados, sin rejilla (regla charts.md)."""
import json
import matplotlib.font_manager as fm
fm.fontManager.addfont('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf')
fm.fontManager.addfont('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# Valores derivados del código: pose 52 B a 60 Hz = 3,1 KB/s; SNAP 54 B a 30 Hz = 1,6 KB/s;
# espectador completo ≈ 5 KB/s (+ pose del invitado retransmitida ≈ 8-10); reducido 15/10 Hz ≈ 2,5.
datos = [
    ('Duelo: pose 60 Hz + SNAP 30 Hz + eventos', 4.7, '#1a4a7a'),
    ('Espectador, flujo completo (solo anfitrión)', 5.0, '#2d7ab3'),
    ('Espectador completo + pose del invitado retransmitida', 9.0, '#2d7ab3'),
    ('Espectador, flujo reducido 15 / 10 Hz', 2.5, '#4d8ab3'),
    ('Anfitrión total: 4 espectadores reducidos + duelo', 14.7, '#7a9bb8'),
]
etiquetas = [d[0] for d in datos]
valores = [d[1] for d in datos]
colores = [d[2] for d in datos]

fig, ax = plt.subplots(figsize=(9.2, 4.0), constrained_layout=True)
bars = ax.barh(range(len(datos)), valores, color=colores, height=0.58, edgecolor='none')
ax.set_yticks(range(len(datos)))
ax.set_yticklabels(etiquetas, fontsize=10.5, color='#142840')
ax.invert_yaxis()
ax.set_xlim(0, 16.8)
ax.set_xlabel('KB/s por destino (aprox.)', fontsize=10.5, color='#5a7a96')

# valores etiquetados -> rejilla fuera (regla charts.md)
for i, (et, v, _) in enumerate(datos):
    txt = '≈ 8-10' if i == 2 else f'{v:.1f}'.replace('.', ',')
    ax.text(v + 0.25, i, txt, va='center', fontsize=10.5, color='#142840', fontweight='bold')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color('#c0d0e2')
ax.tick_params(axis='x', colors='#5a7a96', labelsize=10)
ax.tick_params(axis='y', length=0)
ax.grid(False)

salida = '/home/z/my-project/download/_thumbs_r115/fig_ancho_banda_r116.png'
fig.savefig(salida, dpi=170, facecolor='#ffffff')
plt.close(fig)

from PIL import Image
im = Image.open(salida)
json.dump({'f': 'fig_ancho_banda_r116.png', 'w': im.width, 'h': im.height},
          open('/home/z/my-project/scripts/_fig_dims.json', 'w'))
# verificación de contenido no vacío
g = im.convert('L').histogram()
print('✓ figura', im.size, 'no-blanco:', round(1 - g[255] / sum(g), 3))
