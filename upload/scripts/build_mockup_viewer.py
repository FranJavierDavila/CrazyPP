#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_mockup_viewer.py — Visor HTML autónomo de los mockups del Vestíbulo.
Embebe los 3 PNG en base64 dentro de un único HTML (sin dependencias) para
que el dueño pueda verlos aunque el chat no le muestre las imágenes."""
import base64
from pathlib import Path

D = Path('/home/z/my-project/download')
MOCKS = [
    ('mockup1_vestibulo_arco.png', '1 · El Vestíbulo — vista VR completa',
     'Cabecera con pala+bola y banderas ES/EN · panel central JUGAR (héroe '
     'PARTIDO, Carrera, Entrenar, Supervivencia) · izquierda COMPITE '
     '(Multijugador, Campeonatos, Ranking) · derecha TU CASA (Sala Arcana, '
     'Academia, Ajustes) · dock inferior con utilidades.'),
    ('mockup2_panel_jugar_closeup.png', '2 · Panel JUGAR en detalle',
     'El lenguaje caramelo de la referencia: gradiente glossy + sheen de '
     'cristal, medallón oscuro con icono blanco, aro oscuro y glow. Badge '
     'de progreso (estrella) y subtítulos con estado vivo.'),
    ('mockup3_pantalla_campeonatos.png', '3 · Pantalla de sección — Campeonatos',
     'Plantilla común para todas las secciones: ‹ Volver siempre arriba-'
     'izquierda, estado en la cabecera, pestañas (Mis torneos · Inscribir · '
     'Coronación), tarjetas con badge (EN CURSO / CORONADO / BLOQUEADO) y '
     'CTA verde.'),
]

cards = []
for fn, tit, desc in MOCKS:
    b64 = base64.b64encode((D / fn).read_bytes()).decode()
    cards.append(f'''
  <section class="card">
    <h2>{tit}</h2>
    <p>{desc}</p>
    <img src="data:image/png;base64,{b64}" alt="{tit}">
    <div class="file">fichero: download/{fn}</div>
  </section>''')

html = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mockups · El Vestíbulo — Crazy Ping Pong FASE 161</title>
<style>
  :root {{ color-scheme: dark; }}
  body {{ margin: 0; padding: 24px; background: #060d1f;
         font: 16px/1.5 system-ui, sans-serif; color: #dfe9f5; }}
  h1 {{ font-size: 26px; margin: 0 0 4px; color: #fff; }}
  .sub {{ color: #8fb0d8; margin: 0 0 24px; }}
  .card {{ background: rgba(13,27,61,.85); border: 1px solid #2a5ca8;
          border-radius: 16px; padding: 18px 20px; margin: 0 0 28px;
          max-width: 1100px; }}
  .card h2 {{ margin: 0 0 6px; font-size: 20px; color: #7fd0ff; }}
  .card p {{ margin: 0 0 14px; color: #c9d3dd; }}
  .card img {{ width: 100%; height: auto; border-radius: 10px;
              border: 1px solid #1c3a6e; display: block; }}
  .file {{ margin-top: 8px; font-size: 12px; color: #5f7183; }}
</style>
</head>
<body>
<h1>Mockups · «El Vestíbulo» — rediseño de los menús principales</h1>
<p class="sub">Crazy Ping Pong · FASE 161 (propuesta) · estilo calcado de la
referencia «Menú de ping-pong futurista sin texto» · aprobación pendiente</p>
{''.join(cards)}
</body>
</html>'''
(D / 'mockups_vestibulo.html').write_text(html, encoding='utf-8')
print('OK mockups_vestibulo.html',
      round((D / 'mockups_vestibulo.html').stat().st_size / 1024), 'KB')
