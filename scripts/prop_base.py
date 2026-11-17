# -*- coding: utf-8 -*-
"""Sistema de materiales y helpers para la propuesta de arte (estética candy arcade del juego).
Paleta extraída de 'Menú de ping-pong futurista sin texto.png'."""

# Paleta original del juego (extracción dominante)
P = {
    "negro":   "#030715",  # fondo profundo
    "marino":  "#061848",  # azul marino chassis
    "marino2": "#043B92",  # azul royal
    "marino3": "#0A1B44",
    "teal":    "#0288B1",  # cian/teal dominante
    "teal_lt": "#8FE8F5",
    "teal_pl": "#97CED6",
    "ambar":   "#F59D1D",  # naranja/ámbar
    "ambar_lt": "#F1E5AB",
    "magenta": "#D70B66",
    "magenta_lt": "#FF7FC0",
    "rojo":    "#DF4E45",
    "verde":   "#06B469",
    "verde_lt": "#30E66D",
    "morado":  "#590F65",
    "acero":   "#4C5170",
    "acero_lt": "#83998C",
    "crema":   "#F9F9E7",
    "crema_ds": "#CDD4B4",
}

DEFS = """<defs>
<linearGradient id="gChassis" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A1B44"/><stop offset=".55" stop-color="#061848"/><stop offset="1" stop-color="#030715"/></linearGradient>
<linearGradient id="gChassisHi" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0E2B6E"/><stop offset="1" stop-color="#061848"/></linearGradient>
<linearGradient id="gGreen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B8FF9E"/><stop offset=".25" stop-color="#30E66D"/><stop offset=".7" stop-color="#06B469"/><stop offset="1" stop-color="#047A3C"/></linearGradient>
<linearGradient id="gMagenta" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7FC0"/><stop offset=".45" stop-color="#D70B66"/><stop offset="1" stop-color="#8A0740"/></linearGradient>
<linearGradient id="gBlue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7FD4FF"/><stop offset=".5" stop-color="#0288B1"/><stop offset="1" stop-color="#043B92"/></linearGradient>
<linearGradient id="gPurple" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C77FE8"/><stop offset=".55" stop-color="#590F65"/><stop offset="1" stop-color="#2E0838"/></linearGradient>
<linearGradient id="gOrange" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFC97A"/><stop offset=".45" stop-color="#F59D1D"/><stop offset="1" stop-color="#C25E0E"/></linearGradient>
<linearGradient id="gRed" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF9A8A"/><stop offset=".45" stop-color="#DF4E45"/><stop offset="1" stop-color="#8A1F16"/></linearGradient>
<linearGradient id="gTeal" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8FE8F5"/><stop offset=".5" stop-color="#0288B1"/><stop offset="1" stop-color="#01547F"/></linearGradient>
<linearGradient id="gSteel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9FB2A6"/><stop offset=".5" stop-color="#4C5170"/><stop offset="1" stop-color="#262B45"/></linearGradient>
<linearGradient id="gGold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF6D0"/><stop offset=".18" stop-color="#F1E5AB"/><stop offset=".5" stop-color="#F59D1D"/><stop offset=".82" stop-color="#B26A08"/><stop offset="1" stop-color="#F7D989"/></linearGradient>
<linearGradient id="gGoldSoft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7D989"/><stop offset=".6" stop-color="#F59D1D"/><stop offset="1" stop-color="#8A5A10"/></linearGradient>
<linearGradient id="gCream" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".5" stop-color="#F9F9E7"/><stop offset="1" stop-color="#CDD4B4"/></linearGradient>
<linearGradient id="gWood" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D9A968"/><stop offset=".5" stop-color="#B07C42"/><stop offset="1" stop-color="#7A5228"/></linearGradient>
<linearGradient id="gSheen" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<linearGradient id="gSheenDiag" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".5"/><stop offset=".38" stop-color="#FFFFFF" stop-opacity=".1"/><stop offset=".42" stop-color="#FFFFFF" stop-opacity="0"/><stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>
<linearGradient id="gShadeBot" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity=".38"/></linearGradient>
<radialGradient id="gRecess"><stop offset="0" stop-color="#01030A"/><stop offset=".72" stop-color="#050B1C"/><stop offset="1" stop-color="#12306E"/></radialGradient>
<radialGradient id="gSphere"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#F9F9E7"/><stop offset="1" stop-color="#A8B098"/></radialGradient>
<radialGradient id="gSky"><stop offset="0" stop-color="#0A1B44"/><stop offset="1" stop-color="#020510"/></radialGradient>
<radialGradient id="gGlowTeal"><stop offset="0" stop-color="#0288B1" stop-opacity=".55"/><stop offset="1" stop-color="#0288B1" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowPink"><stop offset="0" stop-color="#D70B66" stop-opacity=".5"/><stop offset="1" stop-color="#D70B66" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowGold"><stop offset="0" stop-color="#F59D1D" stop-opacity=".55"/><stop offset="1" stop-color="#F59D1D" stop-opacity="0"/></radialGradient>
<radialGradient id="gGlowGreen"><stop offset="0" stop-color="#30E66D" stop-opacity=".5"/><stop offset="1" stop-color="#30E66D" stop-opacity="0"/></radialGradient>
<radialGradient id="gVig"><stop offset=".55" stop-color="#000000" stop-opacity="0"/><stop offset="1" stop-color="#000000" stop-opacity=".5"/></radialGradient>
<pattern id="pDotsTeal" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#0288B1" opacity=".5"/></pattern>
<pattern id="pDotsPink" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#D70B66" opacity=".45"/></pattern>
<pattern id="pDotsGold" width="14" height="14" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.8" fill="#F59D1D" opacity=".45"/></pattern>
<filter id="fGlowTeal" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#35C4E0" flood-opacity=".85"/></filter>
<filter id="fGlowGold" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#F59D1D" flood-opacity=".8"/></filter>
<filter id="fGlowPink" x="-40%" y="-40%" width="180%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="#FF4FA0" flood-opacity=".8"/></filter>
<filter id="fShadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity=".55"/></filter>
</defs>"""

CSS_GUIDES = (".g rect,.g circle,.g path{fill:none;stroke:#FF3BD4;stroke-width:2;stroke-dasharray:6 4}"
              ".g text{fill:#FF3BD4;stroke:none;font-family:monospace;font-size:12px}")

# ---------- helpers ----------

def glow(cx, cy, rx, ry, gid, op=1.0):
    return '<ellipse cx="%g" cy="%g" rx="%g" ry="%g" fill="url(#%s)" opacity="%g"/>' % (cx, cy, rx, ry, gid, op)

def sheen(x, y, w, h, r, op=0.55):
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="url(#gSheen)" opacity="%g"/>' % (x, y, w, h, r, op)

def shade_bot(x, y, w, h, r, op=1.0):
    return '<rect x="%g" y="%g" width="%g" height="%g" rx="%g" fill="url(#gShadeBot)" opacity="%g"/>' % (x, y, w, h, r, op)

def dots(x, y, w, h, pid="pDotsTeal", op=0.5):
    return '<rect x="%g" y="%g" width="%g" height="%g" fill="url(#%s)" opacity="%g"/>' % (x, y, w, h, pid, op)

def socket(cx, cy, r):
    """Recesivo circular para icono, con bisel oscuro y luz inferior."""
    return ('<circle cx="%g" cy="%g" r="%g" fill="url(#gRecess)" stroke="#043B92" stroke-width="%g"/>'
            '<path d="M %g,%g A %g,%g 0 0 0 %g,%g" fill="none" stroke="#97CED6" stroke-opacity=".5" stroke-width="%g" stroke-linecap="round"/>'
            ) % (cx, cy, r, max(2.0, r * 0.06),
                 cx - r * 0.58, cy + r * 0.62, r * 0.92, r * 0.92, cx + r * 0.58, cy + r * 0.62, max(1.5, r * 0.045))

def bolt(cx, cy, r=5.5):
    return ('<circle cx="%g" cy="%g" r="%g" fill="url(#gGoldSoft)" stroke="#3A2404" stroke-width="1"/>'
            '<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="#3A2404" stroke-width="1.4" stroke-linecap="round"/>'
            '<circle cx="%g" cy="%g" r="%g" fill="#FFFFFF" opacity=".55"/>'
            ) % (cx, cy, r, cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5, cx - r * 0.35, cy - r * 0.35, r * 0.28)

def brackets(x, y, w, h, L=26, sw=5, op=0.95, gid="gGold"):
    s = 'fill="none" stroke="url(#%s)" stroke-width="%g" stroke-linecap="round" stroke-opacity="%g"' % (gid, sw, op)
    return ('<path d="M %g,%g H %g V %g" %s/><path d="M %g,%g H %g V %g" %s/>'
            '<path d="M %g,%g V %g H %g" %s/><path d="M %g,%g V %g H %g" %s/>'
            ) % (x + L, y, x, y + L, s,
                 x + w - L, y, x + w, y + L, s,
                 x, y + h - L, y + h, x + L, s,
                 x + w, y + h - L, y + h, x + w - L, s)

def star4(cx, cy, r, fill="#F9F9E7", op=1.0):
    """Estrella de 4 puntas (destello)."""
    k = r * 0.22
    return ('<path d="M %g,%g C %g,%g %g,%g %g,%g C %g,%g %g,%g %g,%g C %g,%g %g,%g %g,%g '
            'C %g,%g %g,%g %g,%g Z" fill="%s" opacity="%g"/>'
            ) % (cx, cy - r, cx + k, cy - k, cx + k, cy - k, cx + r, cy,
                 cx + k, cy + k, cx + k, cy + k, cx, cy + r,
             cx - k, cy + k, cx - k, cy + k, cx - r, cy,
             cx - k, cy - k, cx - k, cy - k, cx, cy - r, fill, op)

def top_light_arc(cx, cy, r, col="#CFF1FF", sw=2.5, op=0.8):
    """Luz de canto superior (arco)."""
    return ('<path d="M %g,%g A %g,%g 0 0 1 %g,%g" fill="none" stroke="%s" stroke-opacity="%g" '
            'stroke-width="%g" stroke-linecap="round"/>'
            ) % (cx - r * 0.62, cy - r * 0.62, r, r, cx + r * 0.62, cy - r * 0.62, col, op, sw)

def bot_dark_arc(cx, cy, r, col="#020409", sw=2.5, op=0.6):
    return ('<path d="M %g,%g A %g,%g 0 0 0 %g,%g" fill="none" stroke="%s" stroke-opacity="%g" '
            'stroke-width="%g" stroke-linecap="round"/>'
            ) % (cx - r * 0.62, cy + r * 0.62, r, r, cx + r * 0.62, cy + r * 0.62, col, op, sw)

def ico(outline, fills="", accent_glow="gGlowTeal", glow_op=0.22):
    """Icono con bisel: copia trasera oscura desplazada + frente en crema. outline sin stroke propio."""
    back = ('<g transform="translate(0,3)" opacity=".4" fill="none" stroke="#020409" stroke-width="8" '
            'stroke-linecap="round" stroke-linejoin="round">%s</g>') % outline
    front = ('<g fill="none" stroke="url(#gCream)" stroke-width="8" stroke-linecap="round" '
             'stroke-linejoin="round">%s</g>') % outline
    g = glow(64, 66, 54, 54, accent_glow, glow_op) if accent_glow else ""
    return g + back + front + fills

def wrap(w, h, body, guides=""):
    g = '<g class="g">%s</g>' % guides if guides else ""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">%s%s%s%s</svg>'
            ) % (w, h, w, h, DEFS, '<style>%s</style>' % CSS_GUIDES, body, g)
