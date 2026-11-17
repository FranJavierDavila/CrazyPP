# -*- coding: utf-8 -*-
"""Genera el pack de plantillas de arte para los menus (SVG + PNG 2x + guias + LEEME + index).
Salida: /home/z/my-project/download/plantillas_menu_arte_v1/  (+ zip aparte por Bash)."""
import os, sys
import cairosvg
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/z/my-project/download/plantillas_menu_arte_v1"
D_SVG = os.path.join(BASE, "svg")
D_PNG = os.path.join(BASE, "png2x")
D_GUI = os.path.join(BASE, "guias")
for d in (D_SVG, D_PNG, D_GUI):
    os.makedirs(d, exist_ok=True)

STYLE = (
 ".b-panel{fill:#0E1726;fill-opacity:.92;stroke:#2A3B55;stroke-width:2}"
 ".b-panel88{fill:#0E1726;fill-opacity:.88;stroke:#2A3B55;stroke-width:1}"
 ".b-panel80{fill:#0E1726;fill-opacity:.8;stroke:#2A3B55;stroke-width:2}"
 ".b-panel70{fill:#0E1726;fill-opacity:.7;stroke:#2A3B55;stroke-width:1}"
 ".b-prim{fill:#35E0FF;fill-opacity:.14;stroke:#35E0FF;stroke-opacity:.8;stroke-width:2}"
 ".b-art{fill:#16243A;stroke:#2A3B55;stroke-width:2}"
 ".b-rail{fill:#1C2840}"
 ".b-railon{fill:#35E0FF;fill-opacity:.3;stroke:#35E0FF;stroke-width:2}"
 ".b-knob{fill:#9FB0C8}"
 ".b-knobon{fill:#35E0FF;stroke:#BFF4FF;stroke-width:3}"
 ".b-fill{fill:#35E0FF}"
 ".b-plate{fill:#070B12;fill-opacity:.55}"
 ".b-green{fill:none;stroke:#3DDC84;stroke-width:20;stroke-linecap:round}"
 ".b-lock{fill:none;stroke:#F2F6FF;stroke-opacity:.92;stroke-width:14;stroke-linecap:round}"
 ".b-amber{fill:none;stroke:#FF8A3D;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}"
 ".am10{fill:none;stroke:#FF8A3D;stroke-width:10;stroke-linecap:round;stroke-linejoin:round}"
 ".p1{fill:#35E0FF}"
 ".p1s{fill:none;stroke:#35E0FF;stroke-width:6;stroke-linecap:round}"
 ".p2{fill:none;stroke:#9FB0C8;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}"
 ".b-ico{fill:none;stroke:#F2F6FF;stroke-width:8;stroke-linecap:round;stroke-linejoin:round}"
 ".b-dot{fill:#F2F6FF}"
 ".g rect,.g circle,.g path{fill:none;stroke:#FF3BD4;stroke-width:2;stroke-dasharray:6 4}"
 ".g text{fill:#FF3BD4;stroke:none;font-family:monospace;font-size:12px}"
)

def wrap(w, h, body, guides=""):
    g = '<g class="g">%s</g>' % guides if guides else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">'
            '<style>%s</style>%s%s</svg>') % (w, h, w, h, STYLE, body, g)

# (nombre, ancho, alto, cuerpo, guias, especificacion, escala_export)
COMPONENTS = [
 ("panel_base", 1280, 800,
  '<rect class="b-panel" width="1280" height="800" rx="40"/>',
  '<circle cx="96" cy="76" r="48"/><text x="52" y="152">VOLVER 96</text>'
  '<rect x="176" y="28" width="834" height="84"/><text x="182" y="60">TITULO 48px izq</text>'
  '<circle cx="1184" cy="76" r="48"/><text x="1120" y="152">CERRAR 96</text>'
  '<rect x="48" y="144" width="1184" height="608"/><text x="56" y="172">CONTENIDO 1184x608</text>',
  "Panel contenedor cristal oscuro 92% + borde 2px #2A3B55, radio 40. 9-slice bordes 48px. Zonas libres: volver (96,28..124,124), titulo (176..1010 x 28..112, 48px izq), cerrar (1136..1232 x 28..124), contenido (48..1232 x 144..752).", 2),
 ("btn_primario", 640, 120,
  '<rect class="b-prim" width="640" height="120" rx="24"/>',
  '<rect x="36" y="24" width="72" height="72"/><text x="36" y="110">ICONO 72</text>'
  '<rect x="132" y="16" width="472" height="88"/><text x="140" y="44">TEXTO izq 42px 1 linea</text>',
  "CTA. Fondo #35E0FF 14% + borde #35E0FF 80%. Icono 72px en (36,24); texto x=132..604, 42px, izq.", 2),
 ("btn_secundario", 640, 120,
  '<rect class="b-panel" width="640" height="120" rx="24"/>',
  '<rect x="36" y="24" width="72" height="72"/><text x="36" y="110">ICONO 72</text>'
  '<rect x="132" y="16" width="472" height="88"/><text x="140" y="44">TEXTO izq 42px 1 linea</text>',
  "Accion normal. Fondo #0E1726 92% + borde #2A3B55. Mismas zonas que btn_primario.", 2),
 ("btn_fila", 640, 104,
  '<rect class="b-panel88" width="640" height="104" rx="20"/>',
  '<rect x="24" y="24" width="56" height="56"/><text x="24" y="96">ICONO 56</text>'
  '<rect x="104" y="16" width="276" height="72"/><text x="108" y="40">TEXTO 34px + sub 24px</text>'
  '<rect x="400" y="16" width="216" height="72"/><text x="404" y="40">VALOR dcha 32px</text>',
  "Fila de lista (Ajustes/Entrenar/Rankings). Fondo 88% + borde 1px. Icono 56 (24,24); texto 34px + sub 24px (x=104..380); slot derecho x=400..616 (valor/toggle/slider) 32px.", 2),
 ("btn_circular", 128, 128,
  '<circle class="b-panel80" cx="64" cy="64" r="62"/>',
  '<circle cx="64" cy="64" r="28"/><text x="42" y="108">ICONO 56</text>',
  "Volver / cerrar / pin. Circular perfecto, fondo 80% + borde 2px. Icono 56px centrado.", 2),
 ("btn_tab", 240, 88,
  '<rect class="b-panel70" width="240" height="88" rx="20"/>',
  '<rect x="24" y="24" width="40" height="40"/><text x="24" y="80">ICO 40</text>'
  '<rect x="76" y="16" width="140" height="56"/><text x="80" y="40">TEXTO 32px</text>',
  "Pestana (Campeonatos: Historial/Musica). Fondo 70%. Icono 40 (24,24); texto 32px x=76..216.", 2),
 ("tarjeta_modo", 640, 420,
  '<rect class="b-panel" width="640" height="420" rx="32"/>',
  '<rect x="252" y="48" width="136" height="136"/><text x="252" y="200">ICONO 136</text>'
  '<rect x="40" y="212" width="560" height="52"/><text x="180" y="240">TITULO centro 44px</text>'
  '<rect x="40" y="268" width="560" height="44"/><text x="180" y="296">SUBTITULO 27px</text>'
  '<rect x="496" y="24" width="120" height="120"/><text x="500" y="160">SPRITE estado</text>',
  "Modos del menu principal + grid de Entrenar. Fondo 92% + borde 2px. Icono 136 centrado y=48..184; titulo 44px centro; subtitulo 27px; slot sprite 120px en (496,24) para aspa/candado.", 2),
 ("tarjeta_hall", 640, 360,
  '<defs><linearGradient id="scrimH" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0" stop-color="#070B12" stop-opacity="0"/>'
  '<stop offset=".55" stop-color="#070B12" stop-opacity="0"/>'
  '<stop offset="1" stop-color="#070B12" stop-opacity=".85"/></linearGradient></defs>'
  '<rect class="b-art" width="640" height="360" rx="24"/>'
  '<rect fill="url(#scrimH)" width="640" height="360" rx="24"/>',
  '<text x="36" y="44">ARTE full-bleed (miniatura escenario)</text>'
  '<rect x="32" y="248" width="576" height="52"/><text x="36" y="276">TITULO izq 40px</text>'
  '<rect x="32" y="304" width="576" height="36"/><text x="36" y="330">HITO 26px</text>'
  '<rect x="496" y="24" width="120" height="120"/><text x="500" y="160">SPRITE</text>',
  "Tarjeta de Hall: TU ARTE full-bleed como fondo (el rect azul es placeholder); el scrim inferior lo aplico yo por codigo. Titulo 40px izq y=248..300; hito 26px y=304..340; slot sprite 120px en (496,24).", 2),
 ("tarjeta_liga", 512, 320,
  '<rect class="b-panel" width="512" height="320" rx="28"/>',
  '<rect x="28" y="24" width="132" height="80"/><text x="32" y="52">N liga 64px izq</text>'
  '<rect x="340" y="40" width="144" height="56"/><text x="344" y="68">RECOMPENSA dcha 28px</text>'
  '<rect x="184" y="96" width="144" height="144"/><text x="188" y="256">SPRITE 144</text>'
  '<rect x="40" y="248" width="432" height="44"/><text x="170" y="276">NOMBRE centro 34px</text>',
  "Escalera de Carrera. Numero de liga 64px izq (28..160 x 24..104); recompensa 28px dcha; sprite 144px centrado (184,96); nombre 34px centro y=248..292.", 2),
 ("toggle_off", 112, 64,
  '<rect class="b-rail" width="112" height="64" rx="32"/><circle class="b-knob" cx="32" cy="32" r="28"/>',
  "", "Toggle OFF: rail #1C2840, knob #9FB0C8 56px.", 2),
 ("toggle_on", 112, 64,
  '<rect class="b-railon" width="112" height="64" rx="32"/><circle class="b-knobon" cx="80" cy="32" r="28"/>',
  "", "Toggle ON: rail #35E0FF 30% + borde, knob #35E0FF con aro claro.", 2),
 ("slider_track", 480, 8,
  '<rect class="b-rail" width="480" height="8" rx="4"/>',
  "", "Raail de slider #1C2840. El fill se recorta por porcentaje.", 2),
 ("slider_fill", 480, 8,
  '<rect class="b-fill" width="480" height="8" rx="4"/>',
  "", "Relleno de slider #35E0FF (entrega longitud completa).", 2),
 ("slider_knob", 48, 48,
  '<circle cx="24" cy="24" r="21" fill="none" stroke="#35E0FF" stroke-opacity=".3" stroke-width="4"/>'
  '<circle cx="24" cy="24" r="14" fill="#F2F6FF" stroke="#35E0FF" stroke-width="3"/>',
  "", "Knob 48px: circulo #F2F6FF con anillo #35E0FF.", 2),
 ("prog_track", 480, 12,
  '<rect class="b-rail" width="480" height="12" rx="6"/>',
  "", "Track de progreso #1C2840 (barras de hitos).", 2),
 ("prog_fill", 480, 12,
  '<defs><linearGradient id="gradP" x1="0" y1="0" x2="1" y2="0">'
  '<stop offset="0" stop-color="#35E0FF"/><stop offset="1" stop-color="#3DDC84"/></linearGradient></defs>'
  '<rect fill="url(#gradP)" width="480" height="12" rx="6"/>',
  "", "Relleno de progreso con degradado #35E0FF a #3DDC84.", 2),
 ("spr_aspa", 256, 256,
  '<circle class="b-plate" cx="128" cy="128" r="104"/>'
  '<line class="b-green" x1="88" y1="88" x2="168" y2="168"/>'
  '<line class="b-green" x1="168" y1="88" x2="88" y2="168"/>',
  "", "SUPERADO: placa #070B12 55% + aspa #3DDC84 trazo 20 caps redondas. Debe leerse a distancia.", 2),
 ("spr_candado", 256, 256,
  '<circle class="b-plate" cx="128" cy="128" r="104"/>'
  '<rect class="b-lock" x="88" y="120" width="80" height="64" rx="10"/>'
  '<path class="b-lock" d="M104,120 V100 A24,24 0 0 1 152,100 V120"/>',
  "", "BLOQUEADO: misma placa + candado #F2F6FF 92% (cuerpo 80x64 + arco).", 2),
 ("spr_actual", 192, 192,
  '<circle class="b-amber" cx="96" cy="96" r="70"/>'
  '<path class="b-amber" d="M16,42 V16 H42"/><path class="b-amber" d="M150,16 H176 V42"/>'
  '<path class="b-amber" d="M176,150 V176 H150"/><path class="b-amber" d="M42,176 H16 V150"/>'
  '<circle cx="96" cy="96" r="6" fill="#FF8A3D"/>',
  "", "ACTUAL: marcador #FF8A3D, anillo con 4 muescas en esquinas. El pulso lo animo yo por codigo.", 2),
 ("spr_chincheta_fijada", 128, 128,
  '<circle class="p1" cx="64" cy="40" r="16"/><polygon class="p1" points="48,56 80,56 64,88"/>'
  '<line class="p1s" x1="64" y1="88" x2="64" y2="106"/>',
  "", "Chincheta FIJADA #35E0FF.", 2),
 ("spr_chincheta_libre", 128, 128,
  '<circle class="p2" cx="64" cy="40" r="16"/><polygon class="p2" points="48,56 80,56 64,88"/>'
  '<line class="p2" x1="64" y1="88" x2="64" y2="106"/>',
  "", "Chincheta libre #9FB0C8.", 2),
 ("spr_trofeo", 192, 192,
  '<path class="am10" d="M60,56 V78 A36,34 0 0 0 132,78 V56"/>'
  '<path class="am10" d="M60,64 H46 A14,14 0 0 0 46,92 H60"/>'
  '<path class="am10" d="M132,64 H146 A14,14 0 0 1 146,92 H132"/>'
  '<line class="am10" x1="96" y1="112" x2="96" y2="138"/>'
  '<line class="am10" x1="70" y1="138" x2="122" y2="138"/>'
  '<line class="am10" x1="62" y1="150" x2="130" y2="150"/>',
  "", "Trofeo #FF8A3D (hitos y recompensas de liga).", 2),
]

ICONS = [
 ("ico_entrenar", "Diana con flecha clavada",
  '<circle class="b-ico" cx="64" cy="64" r="30"/><circle class="b-ico" cx="64" cy="64" r="12"/>'
  '<line class="b-ico" x1="104" y1="24" x2="76" y2="52"/><circle class="b-dot" cx="76" cy="52" r="5"/>'),
 ("ico_multijugador", "Dos palas cruzadas y bola",
  '<circle class="b-ico" cx="42" cy="42" r="18"/><circle class="b-ico" cx="86" cy="42" r="18"/>'
  '<line class="b-ico" x1="54" y1="54" x2="76" y2="76"/><line class="b-ico" x1="74" y1="54" x2="52" y2="76"/>'
  '<circle class="b-ico" cx="64" cy="94" r="7"/>'),
 ("ico_campeonatos", "Copa con asas",
  '<path class="b-ico" d="M40,32 V48 A24,24 0 0 0 88,48 V32 Z"/>'
  '<path class="b-ico" d="M40,40 H26 A12,12 0 0 0 26,64 H42"/>'
  '<path class="b-ico" d="M88,40 H102 A12,12 0 0 1 102,64 H86"/>'
  '<line class="b-ico" x1="64" y1="72" x2="64" y2="88"/><line class="b-ico" x1="48" y1="88" x2="80" y2="88"/>'
  '<line class="b-ico" x1="42" y1="96" x2="86" y2="96"/>'),
 ("ico_escalera", "Tres escalones ascendentes con flecha",
  '<polyline class="b-ico" points="24,96 48,96 48,76 72,76 72,56 96,56 96,32"/>'
  '<polyline class="b-ico" points="86,42 96,32 106,42"/>'),
 ("ico_hall", "Mesa de ping-pong en perspectiva con red",
  '<polygon class="b-ico" points="28,48 100,48 116,84 12,84"/>'
  '<line class="b-ico" x1="64" y1="36" x2="64" y2="84"/><line class="b-ico" x1="56" y1="36" x2="72" y2="36"/>'),
 ("ico_ajustes", "Engranaje",
  '<circle class="b-ico" cx="64" cy="64" r="20"/><circle class="b-ico" cx="64" cy="64" r="8"/>'
  '<line class="b-ico" x1="88" y1="64" x2="96" y2="64"/><line class="b-ico" x1="81" y1="81" x2="87" y2="87"/>'
  '<line class="b-ico" x1="64" y1="88" x2="64" y2="96"/><line class="b-ico" x1="47" y1="81" x2="41" y2="87"/>'
  '<line class="b-ico" x1="40" y1="64" x2="32" y2="64"/><line class="b-ico" x1="47" y1="47" x2="41" y2="41"/>'
  '<line class="b-ico" x1="64" y1="40" x2="64" y2="32"/><line class="b-ico" x1="81" y1="47" x2="87" y2="41"/>'),
 ("ico_sala_escena", "Mesa con fondo de escenario (Ajustes: Sala y Escena)",
  '<rect class="b-ico" x="24" y="36" width="80" height="56" rx="6"/>'
  '<polyline class="b-ico" points="32,88 48,60 60,76 72,56 96,88"/><circle class="b-ico" cx="84" cy="52" r="6"/>'),
 ("ico_sonido", "Altavoz con dos ondas",
  '<polygon class="b-ico" points="36,52 48,52 64,38 64,90 48,78 36,78"/>'
  '<path class="b-ico" d="M78,50 A16,16 0 0 1 78,78"/><path class="b-ico" d="M88,42 A26,26 0 0 1 88,86"/>'),
 ("ico_musica", "Nota musical",
  '<circle class="b-ico" cx="48" cy="88" r="10"/><circle class="b-ico" cx="88" cy="80" r="10"/>'
  '<line class="b-ico" x1="58" y1="88" x2="58" y2="44"/><line class="b-ico" x1="98" y1="80" x2="98" y2="36"/>'
  '<line class="b-ico" x1="58" y1="44" x2="98" y2="36"/>'),
 ("ico_vr_pala", "Pala de perfil con ondas de senal (modo VR)",
  '<ellipse class="b-ico" cx="44" cy="56" rx="26" ry="18" transform="rotate(-35 44 56)"/>'
  '<line class="b-ico" x1="60" y1="72" x2="92" y2="104"/>'
  '<path class="b-ico" d="M92,34 A14,14 0 0 1 106,48"/><path class="b-ico" d="M100,26 A22,22 0 0 1 114,40"/>'),
 ("ico_direccion", "Trayectoria recta hacia diana (Entrenar)",
  '<circle class="b-ico" cx="92" cy="64" r="14"/><circle class="b-dot" cx="92" cy="64" r="5"/>'
  '<line class="b-ico" x1="20" y1="64" x2="66" y2="64"/><polyline class="b-ico" points="66,52 78,64 66,76"/>'),
 ("ico_altura", "Arco parabolico sobre la red",
  '<line class="b-ico" x1="20" y1="92" x2="108" y2="92"/><path class="b-ico" d="M28,88 Q64,24 100,88"/>'
  '<line class="b-ico" x1="64" y1="92" x2="64" y2="74"/><line class="b-ico" x1="56" y1="74" x2="72" y2="74"/>'),
 ("ico_efecto", "Bola con estela curva (spin)",
  '<circle class="b-ico" cx="64" cy="64" r="16"/>'
  '<path class="b-ico" d="M78,46 A26,26 0 0 1 88,62"/><path class="b-ico" d="M50,82 A26,26 0 0 1 40,66"/>'
  '<path class="b-ico" d="M30,48 Q22,64 30,80"/>'),
 ("ico_saque", "Bola lanzada desde pala inclinada",
  '<ellipse class="b-ico" cx="40" cy="86" rx="17" ry="11" transform="rotate(-25 40 86)"/>'
  '<circle class="b-ico" cx="72" cy="40" r="9"/>'
  '<line class="b-ico" x1="50" y1="72" x2="64" y2="58" stroke-dasharray="4 10"/>'),
 ("ico_ritmo", "Metronomo",
  '<polygon class="b-ico" points="44,32 84,32 98,96 30,96"/>'
  '<line class="b-ico" x1="64" y1="44" x2="78" y2="82"/><circle class="b-dot" cx="78" cy="82" r="6"/>'),
 ("ico_reto_semana", "Calendario con estrella",
  '<rect class="b-ico" x="28" y="36" width="72" height="60" rx="8"/>'
  '<line class="b-ico" x1="44" y1="28" x2="44" y2="44"/><line class="b-ico" x1="84" y1="28" x2="84" y2="44"/>'
  '<line class="b-ico" x1="28" y1="52" x2="100" y2="52"/>'
  '<polygon class="b-dot" points="64,61 67.2,69.5 76.4,70 69.2,75.7 71.6,84.5 64,79.5 56.4,84.5 58.8,75.7 51.6,70 60.8,69.5"/>'),
 ("ico_perfiles", "Busto de usuario",
  '<circle class="b-ico" cx="64" cy="46" r="14"/><path class="b-ico" d="M36,94 A28,28 0 0 1 92,94"/>'),
 ("ico_historial", "Reloj con flecha circular",
  '<circle class="b-ico" cx="64" cy="64" r="28"/>'
  '<line class="b-ico" x1="64" y1="64" x2="64" y2="46"/><line class="b-ico" x1="64" y1="64" x2="78" y2="70"/>'),
 ("ico_ranking", "Podio con barras",
  '<rect class="b-ico" x="28" y="60" width="20" height="36"/>'
  '<rect class="b-ico" x="54" y="44" width="24" height="52"/>'
  '<rect class="b-ico" x="84" y="68" width="20" height="28"/>'
  '<polygon class="b-dot" points="64,20 66,25.2 71.6,25.5 65.2,29.1 68.7,34.5 64,31.4 59.3,34.5 62.8,29.1 56.4,25.5 62,25.2"/>'),
 ("ico_jugar", "Triangulo play en circulo",
  '<circle class="b-ico" cx="64" cy="64" r="30"/><polygon class="b-dot" points="56,48 56,80 84,64"/>'),
 ("ico_info", "I en circulo (estados vacios)",
  '<circle class="b-ico" cx="64" cy="64" r="30"/><circle class="b-dot" cx="64" cy="46" r="4"/>'
  '<line class="b-ico" x1="64" y1="58" x2="64" y2="84"/>'),
 ("ico_bloqueo_mini", "Candado pequeno para filas",
  '<rect class="b-ico" x="44" y="60" width="40" height="32" rx="8"/>'
  '<path class="b-ico" d="M52,60 V50 A12,12 0 0 1 76,50 V60"/><circle class="b-dot" cx="64" cy="74" r="4"/>'),
]

EXTRAS = [
 ("fondo_menu", 2048, 1024, 1,
  '<defs>'
  '<radialGradient id="radBg" cx=".5" cy=".45" r=".8">'
  '<stop offset="0" stop-color="#0D1522"/><stop offset="1" stop-color="#070B12"/></radialGradient>'
  '<radialGradient id="radVig" cx=".5" cy=".5" r=".75">'
  '<stop offset=".55" stop-color="#070B12" stop-opacity="0"/>'
  '<stop offset="1" stop-color="#070B12" stop-opacity=".55"/></radialGradient></defs>'
  '<rect fill="url(#radBg)" width="2048" height="1024"/><rect fill="url(#radVig)" width="2048" height="1024"/>'
  '<circle cx="200" cy="180" r="3" fill="#35E0FF" opacity=".08"/><circle cx="480" cy="120" r="2" fill="#35E0FF" opacity=".06"/>'
  '<circle cx="900" cy="300" r="2.5" fill="#35E0FF" opacity=".07"/><circle cx="1300" cy="200" r="3" fill="#35E0FF" opacity=".05"/>'
  '<circle cx="1700" cy="400" r="2" fill="#35E0FF" opacity=".08"/><circle cx="300" cy="700" r="2.5" fill="#35E0FF" opacity=".06"/>'
  '<circle cx="760" cy="820" r="3" fill="#35E0FF" opacity=".07"/><circle cx="1100" cy="750" r="2" fill="#35E0FF" opacity=".05"/>'
  '<circle cx="1500" cy="820" r="2.5" fill="#35E0FF" opacity=".08"/><circle cx="1850" cy="700" r="2" fill="#35E0FF" opacity=".06"/>'
  '<circle cx="1000" cy="500" r="2" fill="#35E0FF" opacity=".05"/><circle cx="600" cy="450" r="2.5" fill="#35E0FF" opacity=".06"/>',
  "Ambiente del menu: gradiente radial #0D1522 a #070B12 + vineta + particulas sutiles (menos del 6%)."),
 ("ilustracion_vacio", 512, 512, 2,
  '<ellipse cx="210" cy="310" rx="120" ry="80" transform="rotate(-18 210 310)" fill="none" stroke="#35E0FF" stroke-opacity=".4" stroke-width="10"/>'
  '<line x1="292" y1="372" x2="388" y2="448" stroke="#35E0FF" stroke-opacity=".4" stroke-width="10" stroke-linecap="round"/>'
  '<circle cx="150" cy="150" r="30" fill="none" stroke="#35E0FF" stroke-opacity=".4" stroke-width="10"/>'
  '<line x1="120" y1="470" x2="400" y2="470" stroke="#9FB0C8" stroke-opacity=".3" stroke-width="6" stroke-dasharray="4 14" stroke-linecap="round"/>',
  "Pieza de linea en cian 40% (pala apoyada + bola) para estados vacios."),
 ("avatar_placeholder", 160, 160, 2,
  '<circle cx="80" cy="80" r="76" fill="#0E1726" stroke="#2A3B55" stroke-width="2"/>'
  '<circle cx="80" cy="62" r="20" fill="none" stroke="#5A6B82" stroke-width="6"/>'
  '<path d="M46,118 A34,34 0 0 1 114,118" fill="none" stroke="#5A6B82" stroke-width="6" stroke-linecap="round"/>',
  "Silueta de usuario neutra circular (Multijugador/Rankings)."),
]

# ---------- 1. SVGs ----------
count_svg = 0
for name, w, h, body, guides, spec, sc in COMPONENTS:
    with open(os.path.join(D_SVG, name + ".svg"), "w") as f:
        f.write(wrap(w, h, body, guides))
    count_svg += 1
for name, desc, body in ICONS:
    with open(os.path.join(D_SVG, name + ".svg"), "w") as f:
        f.write(wrap(128, 128, body))
    count_svg += 1
for name, w, h, sc, body, desc in EXTRAS:
    with open(os.path.join(D_SVG, name + ".svg"), "w") as f:
        f.write(wrap(w, h, body))
    count_svg += 1
print("SVGs escritos:", count_svg)

# ---------- 2. PNGs limpios 2x + guias 1x ----------
made_png = []
for name, w, h, body, guides, spec, sc in COMPONENTS:
    cairosvg.svg2png(bytestring=wrap(w, h, body).encode("utf-8"),
                     write_to=os.path.join(D_PNG, name + ".png"), scale=sc)
    made_png.append(name)
    if guides:
        cairosvg.svg2png(bytestring=wrap(w, h, body, guides).encode("utf-8"),
                         write_to=os.path.join(D_GUI, name + "_guias.png"), scale=1)
for name, desc, body in ICONS:
    cairosvg.svg2png(bytestring=wrap(128, 128, body).encode("utf-8"),
                     write_to=os.path.join(D_PNG, name + ".png"), scale=2)
    made_png.append(name)
for name, w, h, sc, body, desc in EXTRAS:
    cairosvg.svg2png(bytestring=wrap(w, h, body).encode("utf-8"),
                     write_to=os.path.join(D_PNG, name + ".png"), scale=sc)
    made_png.append(name)
print("PNGs limpios:", len(made_png), "| guias:", len(os.listdir(D_GUI)))

# ---------- 3. QA: tamano + cobertura alpha ----------
print("\n-- QA alpha --")
bad = []
for n in sorted(made_png):
    p = os.path.join(D_PNG, n + ".png")
    im = Image.open(p).convert("RGBA")
    a = im.getchannel("A")
    cov = sum(1 for v in a.getdata() if v > 10) / (im.width * im.height)
    if cov < 0.005:
        bad.append(n)
    print("%-24s %dx%d cov=%.3f" % (n, im.width, im.height, cov))
print("SOSPECHOSOS:", bad if bad else "ninguno")

# ---------- 4. Hoja de contacto para control visual ----------
cols = 6
TH = 210
label_h = 18
pad = 10
rows = (len(made_png) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (TH + pad) + pad, rows * (TH + label_h + pad) + pad), (16, 16, 24))
dr = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except Exception:
    font = ImageFont.load_default()
for i, n in enumerate(sorted(made_png)):
    im = Image.open(os.path.join(D_PNG, n + ".png")).convert("RGBA")
    im.thumbnail((TH, TH))
    x = pad + (i % cols) * (TH + pad)
    y = pad + (i // cols) * (TH + label_h + pad)
    sheet.paste(im, (x + (TH - im.width) // 2, y + (TH - im.height) // 2), im)
    dr.text((x + 2, y + TH + 2), n[:30], fill=(220, 220, 230), font=font)
sheet.save("/tmp/render/contact_sheet.png")
print("Hoja de contacto: /tmp/render/contact_sheet.png", sheet.size)

# ---------- 5. index.html ----------
cards = []
for name, w, h, body, guides, spec, sc in COMPONENTS:
    gu = '<span class="ok">guia 1x incluida</span>' if guides else ""
    cards.append('<div class="card"><img src="svg/%s.svg" alt="%s"><h3>%s</h3>'
                 '<p class="meta">%dx%d · export %dx%d %s</p><p class="spec">%s</p></div>'
                 % (name, name, name, w, h, w * sc, h * sc, gu, spec))
for name, desc, body in ICONS:
    cards.append('<div class="card ico"><img src="svg/%s.svg" alt="%s"><h3>%s</h3><p class="spec">%s</p></div>'
                 % (name, name, name, desc))
for name, w, h, sc, body, desc in EXTRAS:
    cards.append('<div class="card"><img src="svg/%s.svg" alt="%s"><h3>%s</h3>'
                 '<p class="meta">%dx%d · export %dx%d</p><p class="spec">%s</p></div>'
                 % (name, name, name, w, h, w * sc, h * sc, desc))

html = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plantillas de arte — Menus Ping Pong VR v1</title>
<style>
body{background:#0A0F18;color:#F2F6FF;font:15px/1.5 system-ui,sans-serif;margin:0;padding:clamp(12px,3vw,32px)}
h1{font-size:clamp(18px,4vw,24px)} h2{font-size:clamp(15px,3vw,18px);border-bottom:1px solid #2A3B55;padding-bottom:6px;margin-top:34px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px}
.grid.ico{grid-template-columns:repeat(auto-fill,minmax(150px,1fr))}
.card{background:#0E1726;border:1px solid #2A3B55;border-radius:12px;padding:12px}
.card h3{margin:8px 0 2px;font-size:14px;word-break:break-all}
.card img{width:100%;height:auto;max-height:230px;object-fit:contain;display:block;
 background:repeating-conic-gradient(#151d2c 0% 25%,#0b111c 0% 50%) 0/16px 16px;border-radius:8px}
.card.ico img{max-height:110px}
.meta{color:#9FB0C8;font-size:12px;margin:2px 0}
.spec{color:#9FB0C8;font-size:12px;margin:6px 0 0}
.ok{color:#3DDC84;font-size:12px}
.pal{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}
.pal div{border-radius:8px;padding:8px 12px;font-size:12px;border:1px solid #2A3B55}
</style></head><body>
<h1>Plantillas de arte — Menus Ping Pong VR v1</h1>
<p>47 recursos: SVG editables (capa magenta = guias de zonas de texto, eliminable) + PNG limpio en <code>png2x/</code> + guias en <code>guias/</code>. Regla de oro: <b>no hornees texto</b>; deja libres las zonas marcadas (el texto lo compone el juego).</p>
<div class="pal">
<div style="background:#070B12">fondo #070B12</div><div style="background:#0E1726">panel #0E1726</div>
<div style="background:#2A3B55">borde #2A3B55</div><div style="background:#35E0FF;color:#070B12">primario #35E0FF</div>
<div style="background:#FF8A3D;color:#070B12">ambar #FF8A3D</div><div style="background:#3DDC84;color:#070B12">exito #3DDC84</div>
<div style="background:#5A6B82">bloqueado #5A6B82</div><div style="background:#F2F6FF;color:#070B12">texto #F2F6FF</div>
<div style="background:#9FB0C8;color:#070B12">texto2 #9FB0C8</div>
</div>
<h2>A · Contenedor y B · Botones y C · Tarjetas</h2><div class="grid">@@C1@@</div>
<h2>D · Controles y E · Sprites de estado</h2><div class="grid">@@C2@@</div>
<h2>F · Iconos (128, trazo 8, #F2F6FF)</h2><div class="grid ico">@@C3@@</div>
<h2>G · Extras</h2><div class="grid">@@C4@@</div>
</body></html>"""
html = (html.replace("@@C1@@", "".join(cards[:9]))
            .replace("@@C2@@", "".join(cards[9:22]))
            .replace("@@C3@@", "".join(cards[22:44]))
            .replace("@@C4@@", "".join(cards[44:])))
with open(os.path.join(BASE, "index.html"), "w") as f:
    f.write(html)
print("index.html escrito")

# ---------- 5b. index_autonomo.html: SVGs incrustados (funciona sin las carpetas) ----------
all_names = [c[0] for c in COMPONENTS] + [i[0] for i in ICONS] + [e[0] for e in EXTRAS]
auto = html
for n in all_names:
    with open(os.path.join(D_SVG, n + ".svg")) as f:
        sv = f.read()
    auto = auto.replace('<img src="svg/%s.svg" alt="%s">' % (n, n), sv)
auto = auto.replace(".card img{", ".card img,.card svg{").replace(".card.ico img{", ".card.ico img,.card.ico svg{")
auto = auto.replace("</p>\n<h2>", "</p><p><b>Version autonoma:</b> los SVG van incrustados; "
                    "este archivo funciona solo, sin las carpetas svg/ ni png2x/.</p>\n<h2>")
with open(os.path.join(BASE, "index_autonomo.html"), "w") as f:
    f.write(auto)
print("index_autonomo.html escrito (svgs inline:", auto.count("<svg"), ")")

# ---------- 6. LEEME.md ----------
leeme = """# Plantillas de arte — Menus Ping Pong VR v1

Pack para el rediseño visual de los menús (referencia: lenguaje de Racket Fury —
tarjetas con arte + titulo superpuesto, foco con borde ambar, pocas piezas por pantalla,
fondo oscuro). Validado frame a frame contra el video subido el 2026-11-17.

## Contenido
- `svg/` — 47 SVG editables (Figma/Illustrator/Inkscape). La capa magenta punteada son GUIAS de zonas (eliminable).
- `png2x/` — los mismos en PNG limpio con transparencia a escala 2x (fondo_menu a 1x). Pinta encima.
- `guias/` — 9 componentes con las zonas de texto/icono marcadas a 1x (referencia rapida).
- `index.html` — galeria visual con la ficha de cada recurso (NECESITA las carpetas al lado: descomprime el zip entero y abrela desde dentro).
- `index_autonomo.html` — la misma galeria con los SVG incrustados: funciona sola, sin carpetas.

## Reglas globales
1. SIN TEXTO HORNEADO: las zonas de texto se dejan LIBRES; el texto lo compone el juego (Rajdhani/Chakra Petch).
2. Dimensiones de diseno a 1x; exporta a 2x. En el mundo 3D la escala la fija el codigo: respeta proporciones.
3. Formato: botones/tarjetas/sprites PNG-32 con alpha; iconos SVG (se recolorean por codigo).
4. Grid base 8px; margenes internos 32px; gap icono-texto 24px.
5. Naming minusculas_snake_case.
6. Estados hover/pressed/disabled los genera el codigo (tinte + borde + glow): entrega 1 base por recurso.

## Tokens de color
| Uso | HEX |
|---|---|
| Fondo escena | #070B12 |
| Panel/superficie | #0E1726 al 92% |
| Borde normal / disabled | #2A3B55 / #1C2840 |
| Primario (foco, CTA) | #35E0FF |
| Competición (liga actual, trofeos) | #FF8A3D |
| Exito/superado | #3DDC84 |
| Bloqueado | #5A6B82 |
| Texto principal / secundario | #F2F6FF / #9FB0C8 |

## Estados (los horneara el codigo si no los haces tu)
| Estado | Receta |
|---|---|
| Hover/foco | Borde #35E0FF + glow exterior 24px al 35% |
| Pulsado | Fondo #35E0FF al 18%, escala 0.98 |
| Deshabilitado | Fondo 60%, borde #1C2840, sin glow |
| Superado | Borde #3DDC84 + fondo #3DDC84 al 10% + spr_aspa |
| Actual | Borde #FF8A3D + glow al 35% + spr_actual |
| Bloqueado | Desaturado + spr_candado; NO seleccionable (shake 300ms al intentarlo) |

## Catalogo
### A · Contenedor
- `panel_base` 1280x800 r40 — cabecera: volver 96px (48,28), titulo 48px izq (176..1010 x 28..112), cerrar 96px (1136,28); contenido 1184x608 desde y=144. 9-slice bordes 48px.

### B · Botones
- `btn_primario` 640x120 r24 — icono 72 (36,24) · texto 42px izq x=132..604. CTA cian.
- `btn_secundario` 640x120 r24 — igual, fondo panel.
- `btn_fila` 640x104 r20 — icono 56 (24,24) · texto 34px + sub 24px (x=104..380) · slot derecho x=400..616 (valor/toggle/slider).
- `btn_circular` 128x128 — icono 56 centrado. Volver/cerrar/pin.
- `btn_tab` 240x88 r20 — icono 40 (24,24) · texto 32px.

### C · Tarjetas
- `tarjeta_modo` 640x420 r32 — icono 136 centrado y=48..184 · titulo 44px centro · subtitulo 27px · slot sprite 120 (496,24).
- `tarjeta_hall` 640x360 r24 — TU ARTE full-bleed de fondo; titulo 40px izq y=248..300 · hito 26px · slot sprite 120 (496,24). El scrim lo pone el codigo.
- `tarjeta_liga` 512x320 r28 — N liga 64px izq · recompensa 28px dcha · sprite 144 centrado (184,96) · nombre 34px centro.

### D · Controles
- `toggle_off/on` 112x64 · `slider_track/fill` 480x8 · `slider_knob` 48x48 · `prog_track/fill` 480x12.

### E · Sprites de estado
- `spr_aspa` 256x256 (superado, verde) · `spr_candado` 256x256 (bloqueado) · `spr_actual` 192x192 (ambar, pulso por codigo) · `spr_chincheta_fijada/libre` 128x128 · `spr_trofeo` 192x192.

### F · Iconos (SVG 128x128, trazo 8, #F2F6FF, margen 16)
ico_entrenar · ico_multijugador · ico_campeonatos · ico_escalera · ico_hall · ico_ajustes · ico_sala_escena · ico_sonido · ico_musica · ico_vr_pala · ico_direccion · ico_altura · ico_efecto · ico_saque · ico_ritmo · ico_reto_semana · ico_perfiles · ico_historial · ico_ranking · ico_jugar · ico_info · ico_bloqueo_mini

### G · Extras
- `fondo_menu` 2048x1024 (ambiente) · `ilustracion_vacio` 512x512 (empty states) · `avatar_placeholder` 160x160.

## Orden de trabajo recomendado
1. panel_base → 2. btn_fila → 3. btn_primario/secundario → 4. btn_circular → 5. tarjeta_modo →
6. spr_aspa + spr_candado → 7. tarjeta_liga → 8. miniaturas Hall (tarjeta_hall) → 9. controles D →
10. btn_tab → 11. iconos (lotes de 5) → 12. extras.
Con los pasos 1-6 el juego ya puede maquetar el menu principal y Entrenar completos.

## Tipografia (la aplica el juego)
- Titulos: Chakra Petch Bold o Exo 2 Bold. Cuerpo: Rajdhani o Barlow Semi Condensed (numeros tabulares en rankings).
- Escala: titulo de vista 1.6x · seccion 1.2x · cuerpo 1x · caption 0.8x. Maximo 2 pesos por pantalla.
"""
with open(os.path.join(BASE, "LEEME.md"), "w") as f:
    f.write(leeme)
print("LEEME.md escrito")

# ---------- 7. Resumen ----------
n_svg = len(os.listdir(D_SVG)); n_png = len(os.listdir(D_PNG)); n_g = len(os.listdir(D_GUI))
print("\nRESUMEN: svg=%d png2x=%d guias=%d" % (n_svg, n_png, n_g))
print("OK" if (n_svg == 47 and n_png == 47 and not bad) else "REVISAR")
