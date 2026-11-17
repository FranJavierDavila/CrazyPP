# -*- coding: utf-8 -*-
"""Cuerpos SVG de la propuesta: componentes, iconos y extras (estética candy arcade del juego).
Zonas de texto LIBRES según especificación v1 (guías magenta incluidas)."""

# guías de zonas (idénticas a la especificación v1)
G_PANEL = ('<circle cx="96" cy="76" r="48"/><text x="52" y="152">VOLVER 96</text>'
           '<rect x="176" y="28" width="834" height="84"/><text x="182" y="60">TITULO 48px izq</text>'
           '<circle cx="1184" cy="76" r="48"/><text x="1120" y="152">CERRAR 96</text>'
           '<rect x="48" y="144" width="1184" height="608"/><text x="56" y="172">CONTENIDO 1184x608</text>')
G_BTN = ('<rect x="36" y="24" width="72" height="72"/><text x="36" y="110">ICONO 72</text>'
         '<rect x="132" y="16" width="472" height="88"/><text x="140" y="44">TEXTO izq 42px 1 linea</text>')
G_FILA = ('<rect x="24" y="24" width="56" height="56"/><text x="24" y="96">ICONO 56</text>'
          '<rect x="104" y="16" width="276" height="72"/><text x="108" y="40">TEXTO 34px + sub 24px</text>'
          '<rect x="400" y="16" width="216" height="72"/><text x="404" y="40">VALOR dcha 32px</text>')
G_CIRC = '<circle cx="64" cy="64" r="28"/><text x="42" y="108">ICONO 56</text>'
G_TAB = ('<rect x="24" y="24" width="40" height="40"/><text x="24" y="80">ICO 40</text>'
         '<rect x="76" y="16" width="140" height="56"/><text x="80" y="40">TEXTO 32px</text>')
G_MODO = ('<rect x="252" y="48" width="136" height="136"/><text x="252" y="200">ICONO 136</text>'
          '<rect x="40" y="212" width="560" height="52"/><text x="180" y="240">TITULO centro 44px</text>'
          '<rect x="40" y="268" width="560" height="44"/><text x="180" y="296">SUBTITULO 27px</text>'
          '<rect x="496" y="24" width="120" height="120"/><text x="500" y="160">SPRITE estado</text>')
G_HALL = ('<text x="36" y="44">ARTE full-bleed (miniatura escenario)</text>'
          '<rect x="32" y="248" width="576" height="52"/><text x="36" y="276">TITULO izq 40px</text>'
          '<rect x="32" y="304" width="576" height="36"/><text x="36" y="330">HITO 26px</text>'
          '<rect x="496" y="24" width="120" height="120"/><text x="500" y="160">SPRITE</text>')
G_LIGA = ('<rect x="28" y="24" width="132" height="80"/><text x="32" y="52">N liga 64px izq</text>'
          '<rect x="340" y="40" width="144" height="56"/><text x="344" y="68">RECOMPENSA dcha 28px</text>'
          '<rect x="184" y="96" width="144" height="144"/><text x="188" y="256">SPRITE 144</text>'
          '<rect x="40" y="248" width="432" height="44"/><text x="170" y="276">NOMBRE centro 34px</text>')

from prop_base import (glow, sheen, shade_bot, dots, socket, bolt, brackets,
                       star4, top_light_arc, bot_dark_arc)

COMPONENTS = [
 ("panel_base", 1280, 800, G_PANEL, 2,
  glow(640, 400, 660, 420, "gGlowTeal", 0.10)
  + '<rect x="4" y="4" width="1272" height="792" rx="40" fill="url(#gChassis)" stroke="#043B92" stroke-width="3" filter="url(#fShadow)"/>'
  + '<rect x="14" y="14" width="1252" height="772" rx="32" fill="none" stroke="#0288B1" stroke-opacity=".4" stroke-width="2"/>'
  + '<rect x="60" y="7" width="1160" height="3" rx="1.5" fill="#7FD4FF" opacity=".55"/>'
  + sheen(16, 8, 1248, 110, 34, 0.22)
  + dots(1076, 646, 180, 132, "pDotsTeal", 0.14) + dots(24, 640, 150, 136, "pDotsPink", 0.10)
  + bolt(36, 36) + bolt(1244, 36) + bolt(36, 764) + bolt(1244, 764)
  + '<line x1="48" y1="136" x2="1232" y2="136" stroke="url(#gGoldSoft)" stroke-width="3" opacity=".9"/>'
  + '<rect x="42" y="131" width="10" height="10" transform="rotate(45 47 136)" fill="url(#gGold)"/>'
  + '<rect x="1228" y="131" width="10" height="10" transform="rotate(45 1233 136)" fill="url(#gGold)"/>'
  + shade_bot(14, 560, 1252, 226, 30, 0.8)),
 ("btn_primario", 640, 120, G_BTN, 2,
  glow(320, 64, 340, 84, "gGlowTeal", 0.5)
  + '<rect x="3" y="3" width="634" height="114" rx="24" fill="url(#gBlue)" stroke="#043B92" stroke-width="3" filter="url(#fShadow)"/>'
  + sheen(9, 6, 622, 52, 20, 0.8) + shade_bot(9, 82, 622, 32, 18, 0.85)
  + '<rect x="44" y="6" width="552" height="3" rx="1.5" fill="#DFF6FF" opacity=".75"/>'
  + socket(72, 60, 34)
  + '<path d="M 598,46 L 612,60 L 598,74" fill="none" stroke="#F9F9E7" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity=".9"/>'
  + '<path d="M 614,46 L 628,60 L 614,74" fill="none" stroke="#F9F9E7" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" opacity=".55"/>'),
 ("btn_secundario", 640, 120, G_BTN, 2,
  '<rect x="3" y="3" width="634" height="114" rx="24" fill="url(#gChassisHi)" stroke="#4C5170" stroke-width="3" filter="url(#fShadow)"/>'
  + sheen(9, 6, 622, 48, 20, 0.5) + shade_bot(9, 84, 622, 30, 18, 0.85)
  + '<rect x="44" y="6" width="552" height="3" rx="1.5" fill="#83998C" opacity=".55"/>'
  + socket(72, 60, 34)),
 ("btn_fila", 640, 104, G_FILA, 2,
  '<rect x="3" y="3" width="634" height="98" rx="20" fill="url(#gChassisHi)" stroke="#12306E" stroke-width="2.5" filter="url(#fShadow)"/>'
  + sheen(8, 5, 624, 38, 16, 0.42) + shade_bot(8, 74, 624, 26, 16, 0.8)
  + '<rect x="40" y="6" width="560" height="2.5" rx="1.2" fill="#83998C" opacity=".45"/>'
  + socket(52, 52, 28)
  + '<rect x="400" y="16" width="216" height="72" rx="14" fill="#050B1C" stroke="#12306E" stroke-width="2"/>'
  + shade_bot(404, 52, 208, 32, 12, 0.7)
  + '<rect x="410" y="18" width="196" height="2.5" rx="1.2" fill="#83998C" opacity=".35"/>'),
 ("btn_circular", 128, 128, G_CIRC, 2,
  glow(64, 64, 68, 68, "gGlowTeal", 0.35)
  + '<circle cx="64" cy="64" r="60" fill="url(#gChassisHi)" stroke="url(#gGold)" stroke-width="4" filter="url(#fShadow)"/>'
  + '<circle cx="64" cy="64" r="46" fill="url(#gRecess)" stroke="#043B92" stroke-width="2"/>'
  + top_light_arc(64, 64, 58, "#FFF6D0", 2.5, 0.7) + bot_dark_arc(64, 64, 58, "#020409", 2.5, 0.5)),
 ("btn_tab", 240, 88, G_TAB, 2,
  '<rect x="3" y="3" width="234" height="82" rx="20" fill="url(#gChassisHi)" stroke="#4C5170" stroke-width="2.5" filter="url(#fShadow)"/>'
  + '<rect x="14" y="6" width="212" height="4" rx="2" fill="url(#gGold)" opacity=".9"/>'
  + sheen(8, 5, 224, 30, 16, 0.45) + shade_bot(8, 60, 224, 24, 14, 0.8)
  + socket(44, 44, 22)),
 ("tarjeta_modo", 640, 420, G_MODO, 2,
  glow(320, 130, 320, 130, "gGlowTeal", 0.22)
  + '<rect x="3" y="3" width="634" height="414" rx="32" fill="url(#gChassis)" stroke="#043B92" stroke-width="3" filter="url(#fShadow)"/>'
  + '<rect x="11" y="11" width="618" height="398" rx="26" fill="none" stroke="#0288B1" stroke-opacity=".4" stroke-width="2"/>'
  + brackets(16, 16, 608, 388, 30, 5)
  + sheen(9, 6, 622, 130, 28, 0.38)
  + '<circle cx="320" cy="116" r="74" fill="none" stroke="url(#gGoldSoft)" stroke-width="3" opacity=".9"/>'
  + socket(320, 116, 66)
  + '<circle cx="556" cy="84" r="56" fill="#050B1C" fill-opacity=".9" stroke="url(#gGoldSoft)" stroke-width="2.5" opacity=".95"/>'
  + shade_bot(11, 300, 618, 108, 24, 0.85)
  + dots(470, 326, 152, 78, "pDotsGold", 0.14)),
 ("tarjeta_hall", 640, 360, G_HALL, 2,
  '<rect x="3" y="3" width="634" height="354" rx="24" fill="url(#gWood)" stroke="#5A3A18" stroke-width="3" filter="url(#fShadow)"/>'
  + '<line x1="18" y1="15" x2="622" y2="15" stroke="#7A5228" stroke-width="1.5" opacity=".4"/>'
  + '<line x1="18" y1="345" x2="622" y2="345" stroke="#7A5228" stroke-width="1.5" opacity=".4"/>'
  + bolt(15, 15, 4.5) + bolt(625, 15, 4.5) + bolt(15, 345, 4.5) + bolt(625, 345, 4.5)
  + '<rect x="17" y="17" width="606" height="326" rx="16" fill="url(#gSky)" stroke="url(#gGoldSoft)" stroke-width="2.5"/>'
  + '<ellipse cx="320" cy="252" rx="280" ry="84" fill="url(#gGlowTeal)" opacity=".38"/>'
  + '<line x1="60" y1="298" x2="580" y2="298" stroke="#0288B1" stroke-opacity=".4" stroke-width="2"/>'
  + '<circle cx="500" cy="120" r="60" fill="#020510" fill-opacity=".55" stroke="url(#gGoldSoft)" stroke-width="2.5" opacity=".9"/>'
  + '<rect x="17" y="188" width="606" height="155" rx="16" fill="url(#gShadeBot)" opacity=".95"/>'
  + sheen(17, 17, 606, 60, 16, 0.3)),
 ("tarjeta_liga", 512, 320, G_LIGA, 2,
  glow(256, 150, 260, 150, "gGlowGold", 0.3)
  + '<rect x="3" y="3" width="506" height="314" rx="28" fill="url(#gChassis)" stroke="url(#gGoldSoft)" stroke-width="3" filter="url(#fShadow)"/>'
  + brackets(12, 12, 488, 296, 24, 4)
  + sheen(8, 6, 496, 110, 24, 0.4)
  + '<rect x="28" y="24" width="132" height="80" rx="12" fill="#050B1C" stroke="#12306E" stroke-width="2"/>'
  + shade_bot(30, 70, 128, 30, 10, 0.6)
  + glow(412, 68, 74, 46, "gGlowGold", 0.4)
  + '<circle cx="256" cy="168" r="78" fill="none" stroke="url(#gGold)" stroke-width="4"/>'
  + socket(256, 168, 64)
  + star4(256, 82, 8, "#FFF6D0", 0.95) + star4(178, 118, 5, "#F1E5AB", 0.8) + star4(334, 118, 5, "#F1E5AB", 0.8)
  + shade_bot(8, 252, 496, 58, 22, 0.8)
  + dots(384, 238, 108, 64, "pDotsGold", 0.12)),
 ("toggle_off", 112, 64, "", 2,
  '<rect x="2" y="2" width="108" height="60" rx="30" fill="url(#gSteel)" stroke="#020409" stroke-width="2.5" filter="url(#fShadow)"/>'
  + '<rect x="7" y="6" width="98" height="22" rx="18" fill="#000000" opacity=".22"/>'
  + '<circle cx="32" cy="32" r="24" fill="url(#gSphere)" stroke="#4C5170" stroke-width="2"/>'
  + '<circle cx="25" cy="24" r="7" fill="#FFFFFF" opacity=".8"/>'),
 ("toggle_on", 112, 64, "", 2,
  glow(56, 32, 66, 42, "gGlowGreen", 0.5)
  + '<rect x="2" y="2" width="108" height="60" rx="30" fill="url(#gGreen)" stroke="#047A3C" stroke-width="2.5" filter="url(#fShadow)"/>'
  + '<rect x="8" y="6" width="96" height="20" rx="16" fill="#FFFFFF" opacity=".5"/>'
  + '<circle cx="80" cy="32" r="24" fill="url(#gSphere)" stroke="#0A5A30" stroke-width="2"/>'
  + '<circle cx="73" cy="24" r="7" fill="#FFFFFF" opacity=".85"/>'),
 ("slider_track", 480, 8, "", 2,
  '<rect x="1" y="1" width="478" height="6" rx="3" fill="#050B1C" stroke="#12306E" stroke-width="1.5"/>'
  + '<rect x="3" y="2" width="474" height="2.5" rx="1.2" fill="#000000" opacity=".3"/>'),
 ("slider_fill", 480, 8, "", 2,
  glow(240, 4, 240, 10, "gGlowTeal", 0.55)
  + '<rect x="1" y="1" width="478" height="6" rx="3" fill="url(#gTeal)" stroke="#043B92" stroke-width="1"/>'
  + '<rect x="4" y="2" width="472" height="2.5" rx="1.2" fill="#FFFFFF" opacity=".45"/>'),
 ("slider_knob", 48, 48, "", 2,
  '<circle cx="24" cy="24" r="20" fill="url(#gSphere)" stroke="#0288B1" stroke-width="2.5" filter="url(#fShadow)"/>'
  + top_light_arc(24, 24, 19, "#FFFFFF", 2, 0.9)
  + '<circle cx="17" cy="17" r="5" fill="#FFFFFF" opacity=".85"/>'),
 ("prog_track", 480, 12, "", 2,
  '<rect x="1" y="1" width="478" height="10" rx="5" fill="#050B1C" stroke="#12306E" stroke-width="1.5"/>'
  + '<rect x="3" y="2.5" width="474" height="3" rx="1.5" fill="#000000" opacity=".3"/>'),
 ("prog_fill", 480, 12, "", 2,
  glow(240, 6, 240, 14, "gGlowGreen", 0.5)
  + '<rect x="1" y="1" width="478" height="10" rx="5" fill="url(#gGreen)" stroke="#047A3C" stroke-width="1"/>'
  + '<rect x="4" y="2.5" width="472" height="3.5" rx="1.7" fill="#FFFFFF" opacity=".5"/>'),
 ("spr_aspa", 256, 256, "", 2,
  glow(128, 128, 122, 122, "gGlowGreen", 0.45)
  + '<circle cx="128" cy="128" r="104" fill="url(#gRecess)" stroke="#043B92" stroke-width="3"/>'
  + '<circle cx="128" cy="128" r="112" fill="none" stroke="url(#gSteel)" stroke-width="4"/>'
  + '<g transform="translate(0,4)" opacity=".4"><line x1="88" y1="88" x2="168" y2="168" stroke="#020409" stroke-width="20" stroke-linecap="round"/>'
  + '<line x1="168" y1="88" x2="88" y2="168" stroke="#020409" stroke-width="20" stroke-linecap="round"/></g>'
  + '<line x1="88" y1="88" x2="168" y2="168" stroke="url(#gGreen)" stroke-width="20" stroke-linecap="round" filter="url(#fGlowTeal)"/>'
  + '<line x1="168" y1="88" x2="88" y2="168" stroke="url(#gGreen)" stroke-width="20" stroke-linecap="round" filter="url(#fGlowTeal)"/>'
  + '<line x1="95" y1="95" x2="161" y2="161" stroke="#EFFFF0" stroke-width="5" stroke-linecap="round" opacity=".55"/>'
  + '<line x1="161" y1="95" x2="95" y2="161" stroke="#EFFFF0" stroke-width="5" stroke-linecap="round" opacity=".55"/>'
  + top_light_arc(128, 128, 102, "#8FE8F5", 2.5, 0.5)),
 ("spr_candado", 256, 256, "", 2,
  glow(128, 128, 122, 122, "gGlowGold", 0.42)
  + '<circle cx="128" cy="128" r="104" fill="url(#gRecess)" stroke="#043B92" stroke-width="3"/>'
  + '<circle cx="128" cy="128" r="112" fill="none" stroke="url(#gSteel)" stroke-width="4"/>'
  + '<path d="M104,118 V96 A24,24 0 0 1 152,96 V118" transform="translate(0,4)" fill="none" stroke="#3A2404" stroke-width="13" stroke-linecap="round" opacity=".4"/>'
  + '<path d="M104,118 V96 A24,24 0 0 1 152,96 V118" fill="none" stroke="url(#gGold)" stroke-width="13" stroke-linecap="round"/>'
  + '<rect x="84" y="116" width="88" height="70" rx="12" fill="url(#gGold)" stroke="#8A5A10" stroke-width="2.5" filter="url(#fGlowGold)"/>'
  + sheen(87, 119, 82, 26, 10, 0.55) + shade_bot(87, 158, 82, 25, 10, 0.4)
  + '<circle cx="128" cy="146" r="10" fill="#3A2404"/><rect x="124" y="146" width="8" height="18" rx="4" fill="#3A2404"/>'),
 ("spr_actual", 192, 192, "", 2,
  glow(96, 96, 94, 94, "gGlowGold", 0.6)
  + '<circle cx="96" cy="96" r="70" fill="none" stroke="url(#gGold)" stroke-width="9" filter="url(#fGlowGold)"/>'
  + '<circle cx="96" cy="96" r="79" fill="none" stroke="#F59D1D" stroke-opacity=".3" stroke-width="2"/>'
  + '<path d="M18,44 V18 H44" fill="none" stroke="url(#gGoldSoft)" stroke-width="7" stroke-linecap="round"/>'
  + '<path d="M148,18 H174 V44" fill="none" stroke="url(#gGoldSoft)" stroke-width="7" stroke-linecap="round"/>'
  + '<path d="M174,148 V174 H148" fill="none" stroke="url(#gGoldSoft)" stroke-width="7" stroke-linecap="round"/>'
  + '<path d="M44,174 H18 V148" fill="none" stroke="url(#gGoldSoft)" stroke-width="7" stroke-linecap="round"/>'
  + '<circle cx="96" cy="96" r="7" fill="url(#gGold)" stroke="#8A5A10" stroke-width="1.5"/>'
  + star4(150, 42, 10, "#FFF6D0", 0.95)),
 ("spr_chincheta_fijada", 128, 128, "", 2,
  glow(64, 72, 54, 54, "gGlowPink", 0.5)
  + '<ellipse cx="64" cy="110" rx="26" ry="7" fill="#000000" opacity=".35"/>'
  + '<line x1="64" y1="88" x2="64" y2="108" stroke="url(#gSteel)" stroke-width="5" stroke-linecap="round"/>'
  + '<polygon points="48,58 80,58 64,88" fill="url(#gMagenta)" stroke="#8A0740" stroke-width="1.5"/>'
  + '<ellipse cx="64" cy="40" rx="18" ry="14" fill="url(#gMagenta)" stroke="#8A0740" stroke-width="1.5"/>'
  + '<ellipse cx="58" cy="35" rx="7" ry="4" fill="#FFFFFF" opacity=".6"/>'),
 ("spr_chincheta_libre", 128, 128, "", 2,
  '<ellipse cx="64" cy="110" rx="26" ry="7" fill="#000000" opacity=".3"/>'
  + '<line x1="64" y1="88" x2="64" y2="108" stroke="url(#gSteel)" stroke-width="5" stroke-linecap="round"/>'
  + '<polygon points="48,58 80,58 64,88" fill="url(#gSteel)" stroke="#262B45" stroke-width="1.5"/>'
  + '<ellipse cx="64" cy="40" rx="18" ry="14" fill="url(#gSteel)" stroke="#262B45" stroke-width="1.5"/>'
  + '<ellipse cx="58" cy="35" rx="7" ry="4" fill="#FFFFFF" opacity=".5"/>'),
 ("spr_trofeo", 192, 192, "", 2,
  glow(96, 100, 88, 88, "gGlowGold", 0.55)
  + '<path d="M60,64 H46 A14,14 0 0 0 46,92 H62" fill="none" stroke="#3A2404" stroke-width="9" stroke-linecap="round" opacity=".4" transform="translate(0,4)"/>'
  + '<path d="M132,64 H146 A14,14 0 0 1 146,92 H130" fill="none" stroke="#3A2404" stroke-width="9" stroke-linecap="round" opacity=".4" transform="translate(0,4)"/>'
  + '<path d="M60,64 H46 A14,14 0 0 0 46,92 H62" fill="none" stroke="url(#gGoldSoft)" stroke-width="9" stroke-linecap="round"/>'
  + '<path d="M132,64 H146 A14,14 0 0 1 146,92 H130" fill="none" stroke="url(#gGoldSoft)" stroke-width="9" stroke-linecap="round"/>'
  + '<path d="M60,50 V76 A36,34 0 0 0 132,76 V50 Z" fill="url(#gGold)" stroke="#8A5A10" stroke-width="2.5" filter="url(#fGlowGold)"/>'
  + '<line x1="57" y1="50" x2="135" y2="50" stroke="#FFF6D0" stroke-width="4" stroke-linecap="round" opacity=".9"/>'
  + '<ellipse cx="86" cy="62" rx="12" ry="9" fill="#FFFFFF" opacity=".5"/>'
  + '<line x1="96" y1="110" x2="96" y2="132" stroke="url(#gGoldSoft)" stroke-width="9"/>'
  + '<rect x="66" y="132" width="60" height="10" rx="4" fill="url(#gGold)" stroke="#8A5A10" stroke-width="1.5"/>'
  + '<rect x="56" y="144" width="80" height="16" rx="6" fill="url(#gWood)" stroke="#5A3A18" stroke-width="2"/>'
  + '<line x1="60" y1="148" x2="132" y2="148" stroke="url(#gGold)" stroke-width="3"/>'
  + star4(152, 38, 10, "#FFF6D0", 0.95) + star4(42, 86, 6, "#F1E5AB", 0.8)),
]
# (nombre, descripcion, outline(sin stroke), fills(con fill propio), glow, op_glow)
ICONS = [
 ("ico_entrenar", "Diana con flecha",
  '<circle cx="64" cy="64" r="30"/><circle cx="64" cy="64" r="12"/><line x1="104" y1="24" x2="76" y2="52"/>',
  '<circle cx="76" cy="52" r="5" fill="#30E66D"/>', "gGlowTeal", 0.22),
 ("ico_multijugador", "Dos palas cruzadas y bola",
  '<circle cx="42" cy="42" r="18"/><circle cx="86" cy="42" r="18"/><line x1="54" y1="54" x2="76" y2="76"/><line x1="74" y1="54" x2="52" y2="76"/>',
  '<circle cx="64" cy="94" r="7" fill="#F9F9E7"/>', "gGlowPink", 0.25),
 ("ico_campeonatos", "Copa con asas",
  '<path d="M40,32 V48 A24,24 0 0 0 88,48 V32 Z"/><path d="M40,40 H26 A12,12 0 0 0 26,64 H42"/>'
  '<path d="M88,40 H102 A12,12 0 0 1 102,64 H86"/><line x1="64" y1="72" x2="64" y2="88"/>'
  '<line x1="48" y1="88" x2="80" y2="88"/><line x1="42" y1="96" x2="86" y2="96"/>',
  '<path d="M64,38 C65.5,42 66.5,43 70,44 C66.5,45 65.5,46 64,50 C62.5,46 61.5,45 58,44 C61.5,43 62.5,42 64,38 Z" fill="#F59D1D"/>',
  "gGlowGold", 0.3),
 ("ico_escalera", "Escalones ascendentes con flecha",
  '<polyline points="24,96 48,96 48,76 72,76 72,56 96,56 96,32"/><polyline points="86,42 96,32 106,42"/>',
  '<circle cx="96" cy="32" r="4" fill="#F59D1D"/>', "gGlowTeal", 0.2),
 ("ico_hall", "Mesa en perspectiva con red",
  '<polygon points="28,48 100,48 116,84 12,84"/><line x1="64" y1="36" x2="64" y2="84"/><line x1="56" y1="36" x2="72" y2="36"/>',
  '<circle cx="64" cy="26" r="4.5" fill="#DF4E45"/>', "gGlowTeal", 0.22),
 ("ico_ajustes", "Engranaje",
  '<circle cx="64" cy="64" r="20"/><circle cx="64" cy="64" r="8"/>'
  '<line x1="88" y1="64" x2="96" y2="64"/><line x1="81" y1="81" x2="87" y2="87"/><line x1="64" y1="88" x2="64" y2="96"/>'
  '<line x1="47" y1="81" x2="41" y2="87"/><line x1="40" y1="64" x2="32" y2="64"/><line x1="47" y1="47" x2="41" y2="41"/>'
  '<line x1="64" y1="40" x2="64" y2="32"/><line x1="81" y1="47" x2="87" y2="41"/>',
  '', "gGlowTeal", 0.18),
 ("ico_sala_escena", "Sala y Escena",
  '<rect x="24" y="36" width="80" height="56" rx="6"/><polyline points="32,88 48,60 60,76 72,56 96,88"/>',
  '<circle cx="84" cy="52" r="6" fill="#F59D1D"/>', "gGlowTeal", 0.2),
 ("ico_sonido", "Altavoz con ondas",
  '<polygon points="36,52 48,52 64,38 64,90 48,78 36,78"/><path d="M78,50 A16,16 0 0 1 78,78"/><path d="M88,42 A26,26 0 0 1 88,86"/>',
  '', "gGlowTeal", 0.2),
 ("ico_musica", "Nota musical",
  '<line x1="58" y1="88" x2="58" y2="44"/><line x1="98" y1="80" x2="98" y2="36"/><line x1="58" y1="44" x2="98" y2="36"/>'
  '<circle cx="48" cy="88" r="10"/><circle cx="88" cy="80" r="10"/>',
  '<circle cx="48" cy="88" r="4.5" fill="#D70B66"/><circle cx="88" cy="80" r="4.5" fill="#D70B66"/>', "gGlowPink", 0.25),
 ("ico_vr_pala", "Pala VR con senal",
  '<ellipse cx="44" cy="56" rx="26" ry="18" transform="rotate(-35 44 56)"/><line x1="60" y1="72" x2="92" y2="104"/>'
  '<path d="M92,34 A14,14 0 0 1 106,48"/><path d="M100,26 A22,22 0 0 1 114,40"/>',
  '', "gGlowTeal", 0.22),
 ("ico_direccion", "Trayectoria a diana",
  '<circle cx="92" cy="64" r="14"/><line x1="20" y1="64" x2="66" y2="64"/><polyline points="66,52 78,64 66,76"/>',
  '<circle cx="92" cy="64" r="5" fill="#DF4E45"/>', "gGlowPink", 0.28),
 ("ico_altura", "Arco parabolico sobre la red",
  '<line x1="20" y1="92" x2="108" y2="92"/><path d="M28,88 Q64,24 100,88"/><line x1="64" y1="92" x2="64" y2="74"/><line x1="56" y1="74" x2="72" y2="74"/>',
  '', "gGlowTeal", 0.2),
 ("ico_efecto", "Bola con estela (spin)",
  '<circle cx="64" cy="64" r="16"/><path d="M78,46 A26,26 0 0 1 88,62"/><path d="M50,82 A26,26 0 0 1 40,66"/><path d="M30,48 Q22,64 30,80"/>',
  '<circle cx="64" cy="64" r="5" fill="#F9F9E7"/>', "gGlowPink", 0.3),
 ("ico_saque", "Bola lanzada desde pala",
  '<ellipse cx="40" cy="86" rx="17" ry="11" transform="rotate(-25 40 86)"/><circle cx="72" cy="40" r="9"/>'
  '<line x1="50" y1="72" x2="64" y2="58" stroke-dasharray="4 10"/>',
  '<circle cx="72" cy="40" r="4.5" fill="#F9F9E7"/>', "gGlowTeal", 0.2),
 ("ico_ritmo", "Metronomo",
  '<polygon points="44,32 84,32 98,96 30,96"/><line x1="64" y1="44" x2="78" y2="82"/>',
  '<circle cx="78" cy="82" r="6" fill="#D70B66"/>', "gGlowPink", 0.25),
 ("ico_reto_semana", "Calendario con estrella",
  '<rect x="28" y="36" width="72" height="60" rx="8"/><line x1="44" y1="28" x2="44" y2="44"/><line x1="84" y1="28" x2="84" y2="44"/><line x1="28" y1="52" x2="100" y2="52"/>',
  '<polygon points="64,61 67.2,69.5 76.4,70 69.2,75.7 71.6,84.5 64,79.5 56.4,84.5 58.8,75.7 51.6,70 60.8,69.5" fill="#F59D1D"/>',
  "gGlowGold", 0.3),
 ("ico_perfiles", "Busto de usuario",
  '<circle cx="64" cy="46" r="14"/><path d="M36,94 A28,28 0 0 1 92,94"/>',
  '', "gGlowTeal", 0.18),
 ("ico_historial", "Reloj",
  '<circle cx="64" cy="64" r="28"/><line x1="64" y1="64" x2="64" y2="46"/><line x1="64" y1="64" x2="78" y2="70"/>',
  '<circle cx="64" cy="64" r="3.5" fill="#97CED6"/>', "gGlowTeal", 0.18),
 ("ico_ranking", "Podio",
  '<rect x="28" y="60" width="20" height="36"/><rect x="54" y="44" width="24" height="52"/><rect x="84" y="68" width="20" height="28"/>',
  '<polygon points="64,20 66,25.2 71.6,25.5 65.2,29.1 68.7,34.5 64,31.4 59.3,34.5 62.8,29.1 56.4,25.5 62,25.2" fill="#F59D1D"/>',
  "gGlowGold", 0.28),
 ("ico_jugar", "Play",
  '<circle cx="64" cy="64" r="30"/>',
  '<polygon points="56,48 56,80 84,64" fill="url(#gGreen)" stroke="#047A3C" stroke-width="1.5"/>', "gGlowGreen", 0.35),
 ("ico_info", "Info",
  '<circle cx="64" cy="64" r="30"/><line x1="64" y1="58" x2="64" y2="84"/>',
  '<circle cx="64" cy="46" r="4" fill="#97CED6"/>', "gGlowTeal", 0.18),
 ("ico_bloqueo_mini", "Candado pequeno",
  '<rect x="44" y="60" width="40" height="32" rx="8"/><path d="M52,60 V50 A12,12 0 0 1 76,50 V60"/>',
  '<circle cx="64" cy="74" r="4" fill="#F1E5AB"/>', "gGlowGold", 0.25),
]

EXTRAS = [
 ("fondo_menu", 2048, 1024, 1,
  '<rect width="2048" height="1024" fill="url(#gSky)"/>'
  + '<path d="M -120,260 C 320,60 760,110 1180,260" fill="none" stroke="url(#gBlue)" stroke-width="70" stroke-linecap="round" opacity=".12"/>'
  + '<path d="M -120,260 C 320,60 760,110 1180,260" fill="none" stroke="url(#gBlue)" stroke-width="26" stroke-linecap="round" opacity=".16"/>'
  + '<ellipse cx="1024" cy="580" rx="920" ry="270" fill="url(#gGlowTeal)" opacity=".30"/>'
  + '<ellipse cx="1024" cy="900" rx="430" ry="90" fill="#043B92" opacity=".45"/>'
  + '<line x1="0" y1="720" x2="2048" y2="720" stroke="#0288B1" stroke-opacity=".08" stroke-width="2"/>'
  + '<line x1="0" y1="800" x2="2048" y2="800" stroke="#0288B1" stroke-opacity=".06" stroke-width="2"/>'
  + '<line x1="0" y1="890" x2="2048" y2="890" stroke="#0288B1" stroke-opacity=".05" stroke-width="2"/>'
  + '<line x1="512" y1="620" x2="300" y2="1024" stroke="#0288B1" stroke-opacity=".05" stroke-width="2"/>'
  + '<line x1="1536" y1="620" x2="1748" y2="1024" stroke="#0288B1" stroke-opacity=".05" stroke-width="2"/>'
  + '<circle cx="200" cy="180" r="3" fill="#8FE8F5" opacity=".14"/><circle cx="480" cy="120" r="2" fill="#D70B66" opacity=".12"/>'
  + '<circle cx="900" cy="300" r="2.5" fill="#8FE8F5" opacity=".12"/><circle cx="1300" cy="200" r="3" fill="#F1E5AB" opacity=".12"/>'
  + '<circle cx="1700" cy="400" r="2" fill="#30E66D" opacity=".12"/><circle cx="300" cy="700" r="2.5" fill="#F59D1D" opacity=".10"/>'
  + '<circle cx="760" cy="820" r="3" fill="#8FE8F5" opacity=".10"/><circle cx="1100" cy="750" r="2" fill="#D70B66" opacity=".10"/>'
  + '<circle cx="1500" cy="820" r="2.5" fill="#F1E5AB" opacity=".12"/><circle cx="1850" cy="700" r="2" fill="#8FE8F5" opacity=".12"/>'
  + '<circle cx="1000" cy="500" r="2" fill="#30E66D" opacity=".10"/><circle cx="600" cy="450" r="2.5" fill="#8FE8F5" opacity=".10"/>'
  + dots(60, 60, 220, 160, "pDotsTeal", 0.12) + dots(1768, 812, 212, 150, "pDotsPink", 0.10)
  + '<rect width="2048" height="1024" fill="url(#gVig)"/>'),
 ("ilustracion_vacio", 512, 512, 2,
  glow(240, 300, 210, 170, "gGlowTeal", 0.35)
  + '<ellipse cx="210" cy="290" rx="120" ry="84" transform="rotate(-18 210 290)" fill="none" stroke="url(#gTeal)" stroke-width="10" opacity=".85"/>'
  + '<ellipse cx="210" cy="290" rx="68" ry="46" transform="rotate(-18 210 290)" fill="none" stroke="#8FE8F5" stroke-width="4" opacity=".3"/>'
  + '<line x1="292" y1="364" x2="392" y2="452" stroke="url(#gTeal)" stroke-width="10" stroke-linecap="round" opacity=".85"/>'
  + '<circle cx="150" cy="140" r="26" fill="url(#gSphere)" stroke="#0288B1" stroke-width="3"/>'
  + '<ellipse cx="250" cy="180" rx="150" ry="60" transform="rotate(-12 250 180)" fill="none" stroke="url(#gMagenta)" stroke-width="3" stroke-dasharray="10 14" opacity=".4"/>'
  + '<line x1="110" y1="470" x2="400" y2="470" stroke="#4C5170" stroke-width="5" stroke-dasharray="4 16" stroke-linecap="round" opacity=".5"/>'
  + star4(368, 108, 11, "#F1E5AB", 0.8)),
 ("avatar_placeholder", 160, 160, 2,
  '<circle cx="80" cy="80" r="74" fill="url(#gChassisHi)" stroke="url(#gGold)" stroke-width="4"/>'
  + '<circle cx="80" cy="80" r="62" fill="url(#gRecess)"/>'
  + '<circle cx="80" cy="62" r="20" fill="url(#gSteel)" opacity=".95"/>'
  + '<path d="M46,118 A34,34 0 0 1 114,118" fill="none" stroke="url(#gSteel)" stroke-width="11" stroke-linecap="round" opacity=".95"/>'
  + top_light_arc(80, 80, 72, "#FFF6D0", 2.5, 0.6)),
]

